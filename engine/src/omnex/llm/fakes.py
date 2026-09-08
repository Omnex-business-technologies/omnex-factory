"""Deterministic stand-in models — and the one that makes router savings measurable.

These are not mocks in the usual sense. A mock asserts that a call happened;
these produce a *world with known properties* so a claim about system behaviour
can be checked arithmetically.

`CapabilityModel` is the important one. A router that sends easy work to a cheap
model saves money only if the cheap model actually answers the easy work
correctly — otherwise it saves nothing and costs an escalation. Measuring that
against real providers means paying for a benchmark, waiting minutes per run, and
getting a slightly different answer every time, which is why most routing
"savings" figures are estimates presented as results.

So: a task carries the tier genuinely required to solve it, and a
`CapabilityModel` answers correctly exactly when its own tier is at least that.
Three strategies — always-cheap, always-expensive, routed — can then be run over
the same task set, and accuracy *and* cost compared exactly, instantly, with no
network. The router's savings claim becomes arithmetic rather than anecdote.

This models one thing faithfully (capability is monotone in tier) and ignores
much else (a big model can still be wrong; a small one can get lucky). It is a
measuring instrument for the routing logic, not a simulation of a language
model, and the tests say which of the two they are relying on.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from ..core.clock import Clock, FakeClock
from ..core.errors import OmnexError, TransientError
from .base import CallOptions, compute_cost
from .catalog import ModelSpec, Tier
from .tokens import HeuristicCounter
from .types import Completion, FinishReason, Message, Usage

__all__ = ["CapabilityModel", "FlakyModel", "ScriptedModel", "SlowModel", "Task", "spec_for"]


def spec_for(
    name: str,
    tier: Tier,
    input_usd_per_mtok: str,
    output_usd_per_mtok: str,
    *,
    context_window: int = 128_000,
    cached_input_usd_per_mtok: str | None = None,
) -> ModelSpec:
    """A synthetic spec with prices chosen by the test, not by a vendor.

    Tests that assert on routing arithmetic use these rather than the shipped
    catalogue, so a vendor repricing can never turn a logic test red.
    """
    from ..core.money import TokenPrice

    return ModelSpec(
        name=name,
        provider="test",
        tier=tier,
        price=TokenPrice(input_usd_per_mtok, output_usd_per_mtok, cached_input_usd_per_mtok),
        context_window=context_window,
        max_output_tokens=4096,
        supports_prompt_cache=cached_input_usd_per_mtok is not None,
    )


@dataclass
class ScriptedModel:
    """Returns pre-written responses in order, and records what it was asked."""

    model_spec: ModelSpec
    responses: list[str] = field(default_factory=list)
    #: Output tokens to report per response. Real output length drives most of
    #: the cost, so a test that cares about money sets this deliberately.
    output_tokens: int = 100
    calls: list[list[Message]] = field(default_factory=list)
    counter: HeuristicCounter = field(default_factory=HeuristicCounter)
    reference: ModelSpec | None = None
    _index: int = 0

    @property
    def spec(self) -> ModelSpec:
        return self.model_spec

    def complete(self, messages: Sequence[Message], options: CallOptions) -> Completion:
        self.calls.append(list(messages))
        if self._index >= len(self.responses):
            raise AssertionError(
                f"{self.model_spec.name} was called {self._index + 1} times but only "
                f"{len(self.responses)} responses were scripted"
            )
        text = self.responses[self._index]
        self._index += 1
        return _build_completion(
            spec=self.model_spec,
            text=text,
            messages=messages,
            options=options,
            output_tokens=self.output_tokens,
            counter=self.counter,
            reference=self.reference,
        )


@dataclass(frozen=True)
class Task:
    """A benchmark item whose true difficulty is known."""

    prompt: str
    #: The weakest tier that can actually solve this.
    required_tier: Tier
    answer: str
    wrong_answer: str = "I am not sure."


@dataclass
class CapabilityModel:
    """Answers correctly exactly when its tier meets the task's requirement."""

    model_spec: ModelSpec
    tasks: dict[str, Task]
    output_tokens: int = 120
    #: Output tokens when the model fails. Wrong answers are usually shorter,
    #: and pretending otherwise overstates the cost of a failed cheap attempt —
    #: which would flatter the routing result.
    failed_output_tokens: int = 40
    calls: list[str] = field(default_factory=list)
    counter: HeuristicCounter = field(default_factory=HeuristicCounter)
    reference: ModelSpec | None = None

    @property
    def spec(self) -> ModelSpec:
        return self.model_spec

    def complete(self, messages: Sequence[Message], options: CallOptions) -> Completion:
        prompt = messages[-1].content
        self.calls.append(prompt)
        task = self.tasks.get(prompt)
        if task is None:
            raise AssertionError(f"CapabilityModel has no task registered for {prompt!r}")
        solved = self.model_spec.tier >= task.required_tier
        return _build_completion(
            spec=self.model_spec,
            text=task.answer if solved else task.wrong_answer,
            messages=messages,
            options=options,
            output_tokens=self.output_tokens if solved else self.failed_output_tokens,
            counter=self.counter,
            reference=self.reference,
            metadata={"solved": solved, "required_tier": str(task.required_tier)},
        )


@dataclass
class FlakyModel:
    """Wraps a model and fails the first `fail_times` calls.

    Exists to separate two things the router must treat differently: a provider
    FAILING (retry, or fall back to another provider at the same tier) and a
    model ANSWERING BADLY (escalate to a stronger tier). Conflating them means
    a rate limit gets answered by spending ten times more on a bigger model,
    which is both expensive and useless.
    """

    inner: ScriptedModel | CapabilityModel
    fail_times: int = 1
    error: OmnexError = field(default_factory=lambda: TransientError("provider unavailable"))
    attempts: int = 0

    @property
    def spec(self) -> ModelSpec:
        return self.inner.spec

    def complete(self, messages: Sequence[Message], options: CallOptions) -> Completion:
        self.attempts += 1
        if self.attempts <= self.fail_times:
            raise self.error
        return self.inner.complete(messages, options)


@dataclass
class SlowModel:
    """Wraps a model and advances a FakeClock, so deadlines are testable.

    Advancing an injected clock rather than sleeping is what lets a test assert
    "the deadline was exceeded on the third hop" without the suite taking three
    real seconds.
    """

    inner: ScriptedModel | CapabilityModel
    latency_seconds: float
    clock: Clock = field(default_factory=FakeClock)

    @property
    def spec(self) -> ModelSpec:
        return self.inner.spec

    def complete(self, messages: Sequence[Message], options: CallOptions) -> Completion:
        completion = self.inner.complete(messages, options)
        if isinstance(self.clock, FakeClock):
            self.clock.advance(self.latency_seconds)
        from dataclasses import replace

        return replace(completion, latency_seconds=self.latency_seconds)


def _build_completion(
    spec: ModelSpec,
    text: str,
    messages: Sequence[Message],
    options: CallOptions,
    output_tokens: int,
    counter: HeuristicCounter,
    reference: ModelSpec | None,
    metadata: dict[str, object] | None = None,
) -> Completion:
    input_tokens = counter.estimate_messages(messages)
    # Truncation is reported, not silently ignored, because `length` is the
    # easiest failure to ship: the answer looks fine and is simply cut off.
    capped = min(output_tokens, options.max_tokens)
    finish = FinishReason.LENGTH if capped < output_tokens else FinishReason.STOP
    cached = input_tokens // 2 if (options.cache_prefix and spec.supports_prompt_cache) else 0
    cost, undiscounted = compute_cost(spec, input_tokens, capped, cached, reference)
    return Completion(
        text=text,
        model=spec.name,
        usage=Usage(input_tokens, capped, cached),
        cost=cost,
        undiscounted=undiscounted,
        finish_reason=finish,
        provider=spec.provider,
        metadata=dict(metadata or {}),
    )


def tasks_from(pairs: Sequence[tuple[str, Tier, str]]) -> dict[str, Task]:
    """Build a task set from (prompt, required_tier, answer) triples."""
    return {p: Task(prompt=p, required_tier=t, answer=a) for p, t, a in pairs}


CapabilityFactory = Callable[[ModelSpec], CapabilityModel]
