"""The router: classify, dispatch, verify, escalate — inside a budget.

Three mechanisms live here that are frequently collapsed into one, and keeping
them distinct is most of what makes the thing work:

**Routing** picks a tier from predicted complexity, before any call.
**Escalation** moves UP a tier because the answer was inadequate.
**Fallback** moves SIDEWAYS to another provider at the same tier because a call
failed.

Conflating the last two is the expensive mistake: answering a 429 by escalating
spends ten times more on a bigger model to solve a problem that was never about
capability. So a `TransientError` produces a fallback and a rejected `Verdict`
produces an escalation, and they are counted separately — the escalation rate is
the number the economics depend on, and polluting it with provider outages makes
a healthy router look like a losing one.

Budget is enforced BEFORE dispatch, using an upper-bound token estimate, because
a ceiling checked afterwards is an audit rather than a control. When the budget
cannot cover an escalation, the router returns the cheap answer along with the
reason it stopped, rather than either exceeding the ceiling or failing outright.
A degraded answer with a stated cause is almost always worth more to a caller
than an exception.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from random import Random

from ..core.clock import Clock, Deadline, SystemClock
from ..core.errors import BudgetExceeded, OmnexError, PermanentError, TransientError
from ..core.money import Money
from ..core.retry import RetryPolicy, retry_call
from ..llm.base import CallOptions, LanguageModel
from ..llm.catalog import ModelSpec, Tier
from ..llm.tokens import HeuristicCounter
from ..llm.types import Completion, Message
from ..obs.cost import CostLedger
from ..obs.trace import Tracer
from .complexity import Complexity, ComplexityClassifier
from .economics import RouterEconomics, recommended_bias
from .verify import HeuristicVerifier, Verifier

__all__ = ["RouteStep", "RoutedCompletion", "Router", "RoutingPolicy"]


@dataclass
class RoutingPolicy:
    """How aggressive to be, and where the hard stops are."""

    #: Highest tier the router may reach, whatever the classifier says. The
    #: ceiling that stops one pathological prompt from buying a reasoning-model
    #: call on a free-tier product.
    max_tier: Tier = Tier.LARGE
    #: Lowest tier to consider. Raise it for a product where a nano answer is
    #: never acceptable, so the router does not spend a call proving it.
    min_tier: Tier = Tier.NANO
    #: Escalations permitted per request. One is almost always right: a second
    #: means three calls, and if two tiers both failed the third rarely helps
    #: enough to justify tripling the cost.
    max_escalations: int = 1
    #: Per-request spend ceiling. Checked before every dispatch.
    spend_ceiling: Money = field(default_factory=lambda: Money.from_usd("0.05"))
    #: Retries for a failing provider before falling back sideways.
    retry: RetryPolicy = field(default_factory=lambda: RetryPolicy(max_attempts=2, base_delay=0.2))
    #: Model used as the "what would this have cost anyway" baseline. Savings
    #: are measured against it; without one, savings are unfalsifiable.
    reference_model: str = ""


@dataclass
class RouteStep:
    """One attempt, kept whether it succeeded or not.

    The rejected attempts are the interesting part of a routed request: they are
    what the escalation rate is computed from and what a human reads when asking
    why something cost four times what it should have.
    """

    tier: Tier
    model: str
    outcome: str  # accepted | rejected | failed | skipped_budget | skipped_window
    cost: Money = field(default_factory=Money.zero)
    reason: str = ""


@dataclass
class RoutedCompletion:
    completion: Completion | None
    complexity: Complexity
    steps: list[RouteStep]
    escalated: bool
    #: Set when an escalation was warranted but the budget could not cover it.
    #: The answer is returned anyway, degraded and labelled.
    degraded_reason: str = ""

    @property
    def total_cost(self) -> Money:
        total = Money.zero()
        for step in self.steps:
            total = total + step.cost
        return total

    @property
    def accepted(self) -> bool:
        return any(s.outcome == "accepted" for s in self.steps)


class Router:
    """Routes a request across tiers under a budget, and accounts for it."""

    def __init__(
        self,
        models: Sequence[LanguageModel],
        policy: RoutingPolicy | None = None,
        classifier: ComplexityClassifier | None = None,
        verifier: Verifier | None = None,
        counter: HeuristicCounter | None = None,
        clock: Clock | None = None,
        tracer: Tracer | None = None,
        ledger: CostLedger | None = None,
        rng: Random | None = None,
    ) -> None:
        if not models:
            raise PermanentError("a router needs at least one model")
        self.policy = policy or RoutingPolicy()
        self.classifier = classifier or ComplexityClassifier()
        self.verifier = verifier or HeuristicVerifier()
        self.counter = counter or HeuristicCounter()
        self.clock = clock or SystemClock()
        self.tracer = tracer
        self.ledger = ledger
        self.rng = rng or Random()
        self.economics = RouterEconomics()

        self._by_tier: dict[Tier, list[LanguageModel]] = {}
        for model in models:
            self._by_tier.setdefault(model.spec.tier, []).append(model)
        self._tiers = sorted(self._by_tier)

        self._reference: ModelSpec | None = None
        if self.policy.reference_model:
            for model in models:
                if model.spec.name == self.policy.reference_model:
                    self._reference = model.spec
                    break

    # ── tier selection ────────────────────────────────────────────────────
    def calibrate(self) -> float:
        """Set the classifier's bias from the actual price ratio in this fleet.

        Called explicitly rather than in the constructor so it is visible in a
        trace and in a test. The right amount of caution is a function of the
        price gap between tiers, not of taste — see economics.py.
        """
        cheapest = self._cheapest_spec()
        dearest = self._dearest_spec()
        if cheapest is None or dearest is None or cheapest.price.output_picos == 0:
            # A free local tier makes the ratio infinite: route cheap
            # aggressively, since a wasted attempt costs only latency.
            self.classifier.bias = -0.15
            return float("inf")
        ratio = dearest.price.output_picos / cheapest.price.output_picos
        self.classifier.bias = recommended_bias(ratio)
        return ratio

    def _allowed_tiers(self) -> list[Tier]:
        return [t for t in self._tiers if self.policy.min_tier <= t <= self.policy.max_tier]

    def _cheapest_spec(self) -> ModelSpec | None:
        allowed = self._allowed_tiers()
        return self._by_tier[allowed[0]][0].spec if allowed else None

    def _dearest_spec(self) -> ModelSpec | None:
        allowed = self._allowed_tiers()
        return self._by_tier[allowed[-1]][0].spec if allowed else None

    def _resolve_tier(self, wanted: Tier) -> Tier | None:
        """Nearest available tier at or above `wanted`, then below if none."""
        allowed = self._allowed_tiers()
        if not allowed:
            return None
        for tier in allowed:
            if tier >= wanted:
                return tier
        return allowed[-1]

    def _next_tier_above(self, tier: Tier) -> Tier | None:
        return next((t for t in self._allowed_tiers() if t > tier), None)

    # ── budget ────────────────────────────────────────────────────────────
    def _worst_case_cost(
        self, spec: ModelSpec, messages: Sequence[Message], options: CallOptions
    ) -> Money:
        """Upper bound on what this call could cost, for a pre-dispatch check.

        Upper bound, not estimate: under-estimating dispatches a call the
        ceiling existed to prevent, and the ceiling is then decorative.
        """
        input_upper = self.counter.upper_bound_messages(messages)
        return spec.price.cost(input_upper, options.max_tokens)

    # ── the main path ─────────────────────────────────────────────────────
    def route(
        self, messages: Sequence[Message], options: CallOptions | None = None
    ) -> RoutedCompletion:
        options = options or CallOptions()
        ceiling = options.spend_ceiling or self.policy.spend_ceiling
        question = messages[-1].content if messages else ""
        complexity = self.classifier.classify(question)

        steps: list[RouteStep] = []
        spent = Money.zero()
        #: Times the loop DECIDED to move up a tier. Governs max_escalations.
        escalation_attempts = 0
        #: Calls that actually produced an answer. An escalation only counts
        #: once a second answer exists — counting the intent instead inflates
        #: the escalation rate, which is the single number the break-even
        #: calculation depends on, and makes a healthy router look like it is
        #: losing money. A budget-blocked escalation is not an escalation.
        served_calls = 0
        started_cheap = False
        result: Completion | None = None
        degraded = ""

        tier = self._resolve_tier(complexity.tier)
        if tier is None:
            raise PermanentError("no model available within the policy's tier bounds")

        cheapest_allowed = self._allowed_tiers()[0]
        started_cheap = tier == cheapest_allowed

        while True:
            model = self._pick_model(tier, messages, options, steps)
            if model is None:
                stronger = self._next_tier_above(tier)
                if stronger is None:
                    break
                tier = stronger
                continue

            worst_case = self._worst_case_cost(model.spec, messages, options)
            if spent + worst_case > ceiling:
                steps.append(
                    RouteStep(
                        tier=tier,
                        model=model.spec.name,
                        outcome="skipped_budget",
                        reason=f"worst case {worst_case.format_adaptive()} would exceed "
                        f"the {ceiling.format_adaptive()} ceiling",
                    )
                )
                if result is not None:
                    # An answer already exists; keep it rather than failing.
                    degraded = "escalation skipped: would exceed the spend ceiling"
                    break
                cheaper = self._cheaper_tier_than(tier)
                if cheaper is None:
                    raise BudgetExceeded(
                        "no model can serve this request within the spend ceiling",
                        ceiling=str(ceiling),
                        cheapest_worst_case=str(worst_case),
                    )
                tier = cheaper
                continue

            served, completion, error = self._call_with_fallback(
                model, tier, messages, options, steps
            )
            if completion is None or served is None:
                stronger = self._next_tier_above(tier)
                if stronger is None:
                    raise error or TransientError("every model failed")
                tier = stronger
                continue

            spent = spent + completion.cost
            served_calls += 1
            verdict = self.verifier.check(messages, completion)
            # Attributed to the model that ACTUALLY served, which after a
            # sideways fallback is not the one originally picked. Recording the
            # intended model here is how a routing report ends up describing a
            # call that never happened.
            steps.append(
                RouteStep(
                    tier=tier,
                    model=served.spec.name,
                    outcome="accepted" if verdict.accept else "rejected",
                    cost=completion.cost,
                    reason=verdict.reason,
                )
            )
            self.economics.record_call(
                completion.cost, completion.undiscounted, tier_is_cheap=tier == cheapest_allowed
            )

            if verdict.accept:
                result = completion
                break

            result = completion  # keep the best-so-far in case escalation is blocked
            stronger = self._next_tier_above(tier)
            if stronger is None or escalation_attempts >= self.policy.max_escalations:
                degraded = (
                    f"no stronger tier available ({verdict.reason})"
                    if stronger is None
                    else f"escalation limit reached ({verdict.reason})"
                )
                break
            escalation_attempts += 1
            tier = stronger

        escalated = served_calls > 1
        self.economics.record_decision(started_cheap=started_cheap, escalated=escalated)
        return RoutedCompletion(
            completion=result,
            complexity=complexity,
            steps=steps,
            escalated=escalated,
            degraded_reason=degraded,
        )

    def _cheaper_tier_than(self, tier: Tier) -> Tier | None:
        below = [t for t in self._allowed_tiers() if t < tier]
        return below[-1] if below else None

    def _pick_model(
        self,
        tier: Tier,
        messages: Sequence[Message],
        options: CallOptions,
        steps: list[RouteStep],
    ) -> LanguageModel | None:
        """First model in the tier whose context window can hold the request.

        Checked before dispatch: a window overflow discovered by the provider is
        a failed request that still cost latency, and on some providers still
        billed for the input it rejected.
        """
        needed = self.counter.upper_bound_messages(messages)
        for model in self._by_tier.get(tier, []):
            if model.spec.fits(needed, options.max_tokens):
                return model
            steps.append(
                RouteStep(
                    tier=tier,
                    model=model.spec.name,
                    outcome="skipped_window",
                    reason=f"needs ~{needed} + {options.max_tokens} tokens, "
                    f"window is {model.spec.context_window}",
                )
            )
        return None

    def _call_with_fallback(
        self,
        model: LanguageModel,
        tier: Tier,
        messages: Sequence[Message],
        options: CallOptions,
        steps: list[RouteStep],
    ) -> tuple[LanguageModel | None, Completion | None, OmnexError | None]:
        """Call, retrying then falling back sideways within the tier.

        Sideways, not upwards: a provider failure says nothing about whether the
        task needed a stronger model. Returns the model that actually served, so
        the caller attributes the cost to the right one.
        """
        candidates = [model, *[m for m in self._by_tier.get(tier, []) if m is not model]]
        last: OmnexError | None = None

        for candidate in candidates:
            deadline = options.deadline or Deadline.never(self.clock)
            if deadline.expired():
                last = TransientError("deadline exhausted before dispatch")
                break
            try:
                completion = self._dispatch(candidate, messages, options, deadline)
            except OmnexError as exc:
                last = exc
                steps.append(
                    RouteStep(
                        tier=tier,
                        model=candidate.spec.name,
                        outcome="failed",
                        reason=f"{exc.code}: {exc.message}",
                    )
                )
                if not exc.retryable:
                    # A 400 will fail identically on the next provider too.
                    break
                continue
            return candidate, completion, None

        return None, None, last

    def _dispatch(
        self,
        model: LanguageModel,
        messages: Sequence[Message],
        options: CallOptions,
        deadline: Deadline,
    ) -> Completion:
        def call() -> Completion:
            return model.complete(messages, options.with_(deadline=deadline))

        if self.tracer is None:
            return retry_call(
                call, self.policy.retry, clock=self.clock, rng=self.rng, deadline=deadline
            )

        with self.tracer.span("model-call", kind="llm", model=model.spec.name) as span:
            completion = retry_call(
                call, self.policy.retry, clock=self.clock, rng=self.rng, deadline=deadline
            )
            span.set(
                tier=str(model.spec.tier),
                provider=model.spec.provider,
                undiscounted_picos=completion.undiscounted.picos,
                finish_reason=str(completion.finish_reason),
            )
            span.record_usage(
                completion.cost,
                input_tokens=completion.usage.input_tokens,
                output_tokens=completion.usage.output_tokens,
                cached_input_tokens=completion.usage.cached_input_tokens,
            )
            return completion

    # ── reporting ─────────────────────────────────────────────────────────
    def report(self) -> str:
        return self.economics.report()
