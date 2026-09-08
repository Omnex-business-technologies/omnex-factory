"""Tests for P2. The headline one is `test_routing_benchmark_*` at the bottom."""

from __future__ import annotations

import inspect
import json
from datetime import date
from random import Random

import pytest

from omnex.core import (
    BudgetExceeded,
    ConfigurationError,
    FakeClock,
    IdFactory,
    Money,
    RateLimited,
    ValidationFailed,
)
from omnex.core.errors import PermanentError, TransientError
from omnex.llm import (
    CallOptions,
    CapabilityModel,
    FlakyModel,
    HeuristicCounter,
    Message,
    ModelCatalog,
    ScriptedModel,
    Task,
    Tier,
    spec_for,
)
from omnex.llm.types import Completion, FinishReason, Usage
from omnex.obs import CostLedger, Tracer
from omnex.router import (
    ComplexityClassifier,
    HeuristicVerifier,
    JsonVerifier,
    Router,
    RoutingPolicy,
    TokenShape,
    break_even_escalation_rate,
    fanout_plan,
    recommended_bias,
)
from omnex.router.economics import RouterEconomics
from omnex.router.verify import all_of

# Synthetic prices, chosen so the arithmetic is obvious: the strong tier is
# exactly 30x the cheap one on output. Deliberately NOT the shipped catalogue —
# a vendor repricing must never turn a logic test red.
CHEAP = spec_for("test/cheap", Tier.SMALL, "0.05", "0.10")
STRONG = spec_for("test/strong", Tier.LARGE, "1.50", "3.00")
CHEAP_ALT = spec_for("test/cheap-alt", Tier.SMALL, "0.05", "0.10")
TINY_WINDOW = spec_for("test/tiny", Tier.SMALL, "0.05", "0.10", context_window=200)


def _msg(text: str) -> list[Message]:
    return [Message("user", text)]


# ── Complexity classification ─────────────────────────────────────────────


def test_a_long_extraction_prompt_is_not_treated_as_hard():
    """The biggest source of false escalation: length read as difficulty."""
    classifier = ComplexityClassifier()
    document = "The quarterly report states revenue figures across regions. " * 60
    simple = classifier.classify(f"Extract all the revenue figures from this:\n{document}")
    assert simple.tier <= Tier.SMALL
    assert "extraction" in simple.matched
    # Same length, genuinely hard.
    hard = classifier.classify(
        f"Compare these two strategies and explain why one outperforms the other, "
        f"including trade-offs:\n{document}"
    )
    assert hard.tier >= Tier.LARGE
    assert hard.score > simple.score


@pytest.mark.parametrize(
    ("prompt", "at_most"),
    [
        ("Classify this ticket as billing, technical or other: my card was declined", Tier.SMALL),
        ("Translate to Croatian: the meeting starts at nine", Tier.SMALL),
        ("Convert to JSON: name Ada, born 1815", Tier.SMALL),
        ("What is the capital of France?", Tier.SMALL),
    ],
)
def test_mechanical_tasks_route_cheap(prompt: str, at_most: Tier):
    assert ComplexityClassifier().classify(prompt).tier <= at_most


@pytest.mark.parametrize(
    "prompt",
    [
        "Why does this deadlock, and walk me through the ordering step by step?",
        "Design a rate limiter for a multi-tenant API; what are the trade-offs versus a token bucket?",
        "Prove that the median minimises absolute deviation, and derive the result.",
    ],
)
def test_reasoning_tasks_route_strong(prompt: str):
    assert ComplexityClassifier().classify(prompt).tier >= Tier.LARGE


def test_several_questions_in_one_turn_raise_the_score():
    classifier = ComplexityClassifier()
    one = classifier.classify("How does the cache work?")
    many = classifier.classify("How does the cache work? What evicts entries? When is it warmed?")
    assert many.score > one.score
    assert "multiple_questions" in many.matched


def test_one_word_repeated_cannot_dominate_the_classification():
    """Otherwise a prompt containing 'why' forty times is the hardest query of the day."""
    classifier = ComplexityClassifier()
    spammed = classifier.classify("why " * 40)
    assert spammed.score < 1.0
    assert spammed.score < classifier.classify("why " * 400).score + 0.01


def test_classification_explains_itself():
    explanation = (
        ComplexityClassifier().classify("Why is this slow? Compare both designs.").explain()
    )
    assert "reasoning" in explanation and "score" in explanation


# ── Token estimation ──────────────────────────────────────────────────────


def test_upper_bound_is_always_at_or_above_the_estimate():
    counter = HeuristicCounter()
    for text in ["", "a", "hello world", "def f(x): return x * 2", "日本語のテキスト"]:
        assert counter.upper_bound(text) >= counter.estimate(text)


def test_cjk_is_not_undercounted_by_the_four_chars_rule():
    """Roughly one token per character; the naive rule is 3-4x low, enough to overflow a window."""
    counter = HeuristicCounter()
    cjk = "日本語のテキストをここに入れます"
    assert counter.estimate(cjk) >= len(cjk)
    naive = len(cjk) / 4
    assert counter.estimate(cjk) > naive * 3


def test_heuristic_error_stays_inside_the_stated_margin():
    """The 25% margin is the contract that makes upper_bound meaningful.

    Reference counts here are hand-tallied word-piece estimates for short
    English strings; the assertion is on the estimator's direction and rough
    scale, which is all the budget check relies on.
    """
    counter = HeuristicCounter()
    samples = [
        ("The quick brown fox jumps over the lazy dog.", 10),
        ("Routing decisions must be cheap to make.", 8),
        ("Costs are tracked in pico-dollars for exactness.", 11),
    ]
    for text, approx in samples:
        estimate = counter.estimate(text)
        assert 0.5 * approx <= estimate <= 2.0 * approx
        assert counter.upper_bound(text) >= estimate


def test_message_overhead_is_counted():
    """Forty messages of framing is the difference between fitting a window and not."""
    counter = HeuristicCounter()
    one = counter.estimate_messages([Message("user", "hi")])
    forty = counter.estimate_messages([Message("user", "hi")] * 40)
    assert forty > one * 39


# ── Catalogue ─────────────────────────────────────────────────────────────


def test_shipped_catalogue_parses_and_declares_when_it_was_verified():
    catalog = ModelCatalog.load()
    assert catalog.verified_on <= date.today()
    assert catalog.specs
    for spec in catalog.specs.values():
        assert spec.context_window > 0
        assert spec.max_output_tokens > 0


def test_stale_prices_fail_the_deploy_path_rather_than_reaching_a_bill():
    catalog = ModelCatalog.load()
    far_future = date(catalog.verified_on.year + 2, catalog.verified_on.month, 1)
    assert catalog.is_stale(far_future)
    with pytest.raises(ConfigurationError, match="stale"):
        catalog.assert_fresh(far_future)
    catalog.assert_fresh(catalog.verified_on)  # fresh on the day it was checked


def test_catalogue_json_documents_that_it_goes_out_of_date():
    payload = json.loads(
        (
            ModelCatalog.load().source and __import__("pathlib").Path(ModelCatalog.load().source)
        ).read_text()
    )
    assert "verified_on" in payload
    assert any("out of date" in line.lower() for line in payload["_comment"])


def test_tiers_are_ordered_by_capability_so_escalation_knows_what_stronger_means():
    assert Tier.NANO < Tier.SMALL < Tier.LARGE < Tier.REASONING
    assert Tier.LARGE >= Tier.SMALL


def test_price_ratio_weights_output_because_output_dominates_cost():
    catalog = ModelCatalog.load()
    ratio = catalog.price_ratio("hosted/small-fast", "hosted/frontier")
    input_only = (
        catalog.get("hosted/frontier").price.input_picos
        / catalog.get("hosted/small-fast").price.input_picos
    )
    assert ratio > input_only  # ignoring output understates the gap between tiers


def test_unknown_model_names_what_is_available():
    with pytest.raises(ConfigurationError, match="unknown model"):
        ModelCatalog.load().get("nope/does-not-exist")


# ── Economics ─────────────────────────────────────────────────────────────


def test_break_even_escalation_rate_is_one_minus_the_price_ratio():
    cheap, expensive = Money.from_usd("0.001"), Money.from_usd("0.030")
    assert break_even_escalation_rate(cheap, expensive) == pytest.approx(1 - 1 / 30)


def test_a_two_times_cheaper_tier_starts_losing_money_at_fifty_percent_escalation():
    """The case nobody measures: the router looks busy while costing more than none."""
    cheap, expensive = Money.from_usd("0.010"), Money.from_usd("0.020")
    assert break_even_escalation_rate(cheap, expensive) == pytest.approx(0.5)

    econ = RouterEconomics()
    for i in range(100):
        econ.record_call(cheap, expensive, tier_is_cheap=True)
        escalated = i < 60  # 60% escalation, above the 50% break-even
        if escalated:
            econ.record_call(expensive, expensive, tier_is_cheap=False)
        econ.record_decision(started_cheap=True, escalated=escalated)

    assert econ.escalation_rate == pytest.approx(0.6)
    assert econ.break_even() == pytest.approx(0.5)
    assert econ.is_losing_money()
    assert econ.headroom() < 0
    assert "LOSING MONEY" in econ.report()
    # And the arithmetic agrees: routed spend exceeds always-expensive spend.
    assert econ.spend > expensive * 100


def test_a_thirty_times_cheaper_tier_tolerates_almost_any_escalation_rate():
    cheap, expensive = Money.from_usd("0.001"), Money.from_usd("0.030")
    econ = RouterEconomics()
    for i in range(100):
        econ.record_call(cheap, expensive, tier_is_cheap=True)
        escalated = i < 80  # 80% escalation and still ahead
        if escalated:
            econ.record_call(expensive, expensive, tier_is_cheap=False)
        econ.record_decision(started_cheap=True, escalated=escalated)

    assert econ.escalation_rate == pytest.approx(0.8)
    assert not econ.is_losing_money()
    assert econ.saved > Money.zero()


def test_escalation_rate_denominator_excludes_requests_never_routed_cheap():
    """Including them dilutes the rate and hides the failure it exists to expose."""
    econ = RouterEconomics()
    econ.record_decision(started_cheap=True, escalated=True)
    econ.record_decision(started_cheap=True, escalated=False)
    for _ in range(98):
        econ.record_decision(started_cheap=False, escalated=False)
    assert econ.escalation_rate == pytest.approx(0.5)  # not 0.01


def test_recommended_bias_gets_cautious_as_the_price_gap_narrows():
    wide = recommended_bias(30.0)
    reference = recommended_bias(10.0)
    narrow = recommended_bias(1.5)
    assert wide < reference < narrow
    assert reference == pytest.approx(0.0)
    assert wide >= -0.15 and narrow <= 0.35


# ── Routing behaviour ─────────────────────────────────────────────────────


def _router(models, **policy_kwargs) -> Router:
    clock = FakeClock()
    return Router(
        models,
        policy=RoutingPolicy(**policy_kwargs),
        clock=clock,
        rng=Random(1),
    )


def _capability(spec, tasks: dict[str, Task], reference=STRONG) -> CapabilityModel:
    return CapabilityModel(model_spec=spec, tasks=tasks, reference=reference)


EASY = "Classify this ticket as billing or technical: my card was declined"
HARD = "Why does this deadlock, and compare the trade-offs of each fix step by step?"


def _tasks() -> dict[str, Task]:
    return {
        EASY: Task(EASY, Tier.SMALL, "billing"),
        HARD: Task(HARD, Tier.LARGE, "Lock ordering; prefer a single lock."),
    }


def test_easy_work_goes_cheap_and_stays_there():
    tasks = _tasks()
    cheap, strong = _capability(CHEAP, tasks), _capability(STRONG, tasks)
    routed = _router([cheap, strong]).route(_msg(EASY))

    assert routed.accepted and not routed.escalated
    assert [s.model for s in routed.steps] == ["test/cheap"]
    assert strong.calls == []


def test_hard_work_goes_straight_to_the_strong_tier_without_a_wasted_attempt():
    tasks = _tasks()
    cheap, strong = _capability(CHEAP, tasks), _capability(STRONG, tasks)
    routed = _router([cheap, strong]).route(_msg(HARD))

    assert routed.accepted and not routed.escalated
    assert cheap.calls == []  # no cheap call to waste
    assert [s.model for s in routed.steps] == ["test/strong"]


def test_a_misclassified_hard_task_is_caught_and_escalated():
    """The safety net that makes cheap-first routing acceptable at all."""
    sneaky = "What is the capital of the country whose bank set rates at four in 1997?"
    tasks = {sneaky: Task(sneaky, Tier.LARGE, "Prague")}
    cheap, strong = _capability(CHEAP, tasks), _capability(STRONG, tasks)
    router = _router([cheap, strong])

    routed = router.route(_msg(sneaky))

    assert routed.escalated
    assert routed.completion is not None and routed.completion.text == "Prague"
    assert [s.outcome for s in routed.steps] == ["rejected", "accepted"]
    assert "declined or hedged" in routed.steps[0].reason
    assert router.economics.escalation_rate == 1.0


def test_a_provider_failure_falls_back_sideways_not_upwards():
    """Answering a 429 by buying a bigger model is expensive and beside the point."""
    tasks = _tasks()
    flaky = FlakyModel(
        inner=_capability(CHEAP, tasks), fail_times=99, error=RateLimited("slow down")
    )
    alt = _capability(CHEAP_ALT, tasks)
    strong = _capability(STRONG, tasks)
    router = _router([flaky, alt, strong])

    routed = router.route(_msg(EASY))

    assert routed.accepted and not routed.escalated
    assert strong.calls == []  # never escalated
    assert alt.calls == [EASY]  # served by the sibling at the same tier
    assert [s.outcome for s in routed.steps] == ["failed", "accepted"]
    assert router.economics.escalation_rate == 0.0  # an outage is not an escalation


def test_a_permanent_provider_error_does_not_try_the_sibling():
    """A 400 fails identically everywhere; retrying it just burns the deadline."""
    tasks = _tasks()
    broken = FlakyModel(
        inner=_capability(CHEAP, tasks), fail_times=99, error=PermanentError("malformed request")
    )
    alt = _capability(CHEAP_ALT, tasks)
    strong = _capability(STRONG, tasks)

    routed = _router([broken, alt, strong]).route(_msg(EASY))

    assert alt.calls == []
    assert routed.steps[0].outcome == "failed"


def test_cost_is_attributed_to_the_model_that_actually_served():
    """Otherwise a routing report describes a call that never happened."""
    tasks = _tasks()
    flaky = FlakyModel(inner=_capability(CHEAP, tasks), fail_times=99, error=TransientError("down"))
    alt = _capability(CHEAP_ALT, tasks)
    routed = _router([flaky, alt, _capability(STRONG, tasks)]).route(_msg(EASY))

    accepted = [s for s in routed.steps if s.outcome == "accepted"]
    assert [s.model for s in accepted] == ["test/cheap-alt"]
    assert accepted[0].cost > Money.zero()


def test_a_model_whose_context_window_cannot_hold_the_request_is_skipped_before_dispatch():
    """A window overflow found by the provider is a failed call that still cost latency."""
    long_prompt = "Classify this: " + ("word " * 2000)
    tasks = {long_prompt: Task(long_prompt, Tier.SMALL, "billing")}
    tiny = _capability(TINY_WINDOW, tasks)
    big = _capability(CHEAP, tasks)

    routed = _router([tiny, big]).route(_msg(long_prompt))

    assert tiny.calls == []
    assert routed.steps[0].outcome == "skipped_window"
    assert "window is 200" in routed.steps[0].reason
    assert routed.accepted


# ── Budget ────────────────────────────────────────────────────────────────


def test_an_escalation_that_would_break_the_ceiling_returns_a_degraded_answer_with_a_reason():
    """A labelled degraded answer beats both an exception and a blown budget."""
    sneaky = "What is the capital of the country whose bank set rates at four in 1997?"
    tasks = {sneaky: Task(sneaky, Tier.LARGE, "Prague")}
    # Wide enough for the cheap attempt (worst case ~$0.000104), far too tight
    # for the strong one (~$0.0031).
    router = _router(
        [_capability(CHEAP, tasks), _capability(STRONG, tasks)],
        spend_ceiling=Money.from_usd("0.001"),
    )

    routed = router.route(_msg(sneaky))

    assert not routed.escalated
    assert routed.completion is not None  # the cheap answer is still returned
    assert "spend ceiling" in routed.degraded_reason
    assert any(s.outcome == "skipped_budget" for s in routed.steps)
    assert routed.total_cost < Money.from_usd("0.001")


def test_a_ceiling_no_model_can_meet_fails_loudly_rather_than_spending_anyway():
    tasks = _tasks()
    router = _router(
        [_capability(CHEAP, tasks), _capability(STRONG, tasks)],
        spend_ceiling=Money.from_picos(1),
    )
    with pytest.raises(BudgetExceeded, match="spend ceiling"):
        router.route(_msg(EASY))


def test_the_budget_check_uses_an_upper_bound_not_a_point_estimate():
    """Under-estimating dispatches the call the ceiling existed to prevent."""
    counter = HeuristicCounter(margin=0.25)
    messages = _msg(EASY)
    point = counter.estimate_messages(messages)
    bound = counter.upper_bound_messages(messages)
    assert bound > point


# ── Verification ──────────────────────────────────────────────────────────


def _completion(text: str, finish: FinishReason = FinishReason.STOP) -> Completion:
    return Completion(
        text=text,
        model="test/cheap",
        usage=Usage(10, 10),
        cost=Money.zero(),
        undiscounted=Money.zero(),
        finish_reason=finish,
    )


@pytest.mark.parametrize(
    "text",
    [
        "I'm not sure.",
        "I am not sure what you mean.",
        "I cannot determine that.",
        "As an AI, I lack access.",
        "I would need more context.",
    ],
)
def test_hedges_are_caught_in_both_contracted_and_expanded_form(text: str):
    assert not HeuristicVerifier().check(_msg(EASY), _completion(text)).accept


def test_truncation_is_rejected_even_though_it_raises_nothing():
    """The easiest failure to ship: the answer looks fine and simply stops."""
    verdict = HeuristicVerifier().check(
        _msg(EASY), _completion("The three causes are lock ordering, and", FinishReason.LENGTH)
    )
    assert not verdict.accept and "truncated" in verdict.reason


def test_a_short_answer_is_accepted_when_the_question_wanted_one():
    assert HeuristicVerifier().check(_msg("Yes or no: is it cached?"), _completion("Yes")).accept
    assert (
        not HeuristicVerifier().check(_msg("Explain the cache design"), _completion("Yes")).accept
    )


def test_restating_the_question_is_not_an_answer():
    prompt = "Explain how the distributed cache invalidation protocol handles partitions"
    echo = "The distributed cache invalidation protocol handles partitions somehow"
    assert not HeuristicVerifier().check(_msg(prompt), _completion(echo)).accept


def test_a_normal_answer_passes():
    assert (
        HeuristicVerifier()
        .check(
            _msg(EASY),
            _completion("This is a billing issue — the card was declined by the issuer."),
        )
        .accept
    )


def test_json_verifier_catches_the_truncated_object_before_a_parser_does():
    assert not JsonVerifier().check(_msg("x"), _completion('{"a": 1, "b":')).accept
    assert JsonVerifier().check(_msg("x"), _completion('{"a": 1}')).accept
    assert JsonVerifier().check(_msg("x"), _completion('```json\n{"a": 1}\n```')).accept
    assert (
        not JsonVerifier(required_keys=("a", "b")).check(_msg("x"), _completion('{"a": 1}')).accept
    )


def test_combined_verifiers_report_the_first_failure():
    combined = all_of(HeuristicVerifier(), JsonVerifier())
    verdict = combined.check(_msg("x"), _completion("I'm not sure."))
    assert not verdict.accept and "hedged" in verdict.reason


# ── Tracing and accounting integration ────────────────────────────────────


def test_a_routed_request_produces_a_trace_and_a_ledger_entry():
    tasks = _tasks()
    clock = FakeClock()
    tracer = Tracer(clock=clock, ids=IdFactory(clock=clock, rng=Random(2)))
    ledger = CostLedger()
    router = Router(
        [_capability(CHEAP, tasks), _capability(STRONG, tasks)],
        clock=clock,
        tracer=tracer,
        ledger=ledger,
        rng=Random(1),
    )

    with tracer.trace("answer") as trace:
        routed = router.route(_msg(EASY))

    assert routed.accepted
    llm_spans = [s for s in trace.spans if s.kind == "llm"]
    assert len(llm_spans) == 1
    assert llm_spans[0].attributes["model"] == "test/cheap"
    assert llm_spans[0].attributes["tier"] == "small"
    assert llm_spans[0].cost > Money.zero()

    total = ledger.record_trace(trace, tenant_id="acme", route="/answer")
    assert total == trace.total_cost
    # The undiscounted baseline rode through on the span, so the saving is
    # measured rather than asserted.
    assert ledger.overall.saved > Money.zero()


def test_calibration_derives_caution_from_the_actual_price_gap():
    tasks = _tasks()
    router = _router([_capability(CHEAP, tasks), _capability(STRONG, tasks)])
    ratio = router.calibrate()
    assert ratio == pytest.approx(30.0)
    assert router.classifier.bias < 0  # a wide gap permits aggressive cheap routing


def test_a_free_local_tier_makes_the_router_maximally_aggressive():
    free = spec_for("local/free", Tier.NANO, "0", "0")
    tasks = _tasks()
    router = _router([_capability(free, tasks), _capability(STRONG, tasks)])
    assert router.calibrate() == float("inf")
    assert router.classifier.bias == -0.15


def test_a_router_with_no_models_is_a_configuration_error_not_a_runtime_one():
    with pytest.raises(PermanentError, match="at least one model"):
        Router([])


# ── The benchmark ─────────────────────────────────────────────────────────


def _benchmark_tasks() -> dict[str, Task]:
    """200 tasks whose true difficulty is known.

    Honest about what this measures. The prompts are phrased so the lexical
    classifier can read them, which means this is NOT a measurement of the
    classifier's real-world accuracy — that needs a labelled production
    dataset, and P17 builds one. What it measures is the ROUTING MACHINERY:
    given a classifier that is right most of the time and wrong sometimes, does
    the verify-and-escalate loop recover the lost accuracy, and what does it
    cost? The 20 adversarial tasks exist precisely to be misclassified.
    """
    tasks: dict[str, Task] = {}
    for i in range(120):  # mechanical, genuinely easy
        p = f"Classify ticket {i} as billing or technical: the card was declined at checkout."
        tasks[p] = Task(p, Tier.SMALL, "billing")
    for i in range(60):  # genuinely hard, and phrased like it
        p = (
            f"Why does service {i} deadlock under load, and compare the trade-offs "
            f"of each fix step by step?"
        )
        tasks[p] = Task(p, Tier.LARGE, "Lock ordering.")
    for i in range(20):  # hard, phrased like a lookup — the classifier will miss these
        p = f"What is the capital of the country whose central bank set rate {i} in 1997?"
        tasks[p] = Task(p, Tier.LARGE, "Prague")
    return tasks


def test_routing_benchmark_matches_strong_accuracy_at_a_fraction_of_the_cost():
    tasks = _benchmark_tasks()
    prompts = list(tasks)

    # Baseline 1: always cheap. Cheapest possible, and wrong on every hard task.
    cheap_only = _capability(CHEAP, tasks)
    cheap_cost, cheap_correct = Money.zero(), 0
    for p in prompts:
        c = cheap_only.complete(_msg(p), CallOptions())
        cheap_cost = cheap_cost + c.cost
        cheap_correct += c.text == tasks[p].answer

    # Baseline 2: always strong. Correct on everything, and the cost ceiling.
    strong_only = _capability(STRONG, tasks)
    strong_cost, strong_correct = Money.zero(), 0
    for p in prompts:
        c = strong_only.complete(_msg(p), CallOptions())
        strong_cost = strong_cost + c.cost
        strong_correct += c.text == tasks[p].answer

    # The router.
    router = _router([_capability(CHEAP, tasks), _capability(STRONG, tasks)])
    router.calibrate()
    routed_cost, routed_correct, escalated = Money.zero(), 0, 0
    for p in prompts:
        result = router.route(_msg(p))
        routed_cost = routed_cost + result.total_cost
        routed_correct += (
            result.completion is not None and result.completion.text == tasks[p].answer
        )
        escalated += result.escalated

    assert cheap_correct == 120  # fails all 80 hard tasks
    assert strong_correct == 200  # the accuracy ceiling

    # The claim: the router recovers full accuracy...
    assert routed_correct == 200
    # ...for well under half of what always-strong costs...
    assert routed_cost < strong_cost * 1  # strictly cheaper
    assert routed_cost.picos / strong_cost.picos < 0.5
    # ...and only the 20 adversarial tasks were paid for twice.
    assert escalated == 20
    assert router.economics.escalation_rate == pytest.approx(20 / 140)

    # And it is comfortably the right side of break-even.
    assert not router.economics.is_losing_money()
    assert router.economics.headroom() > 0.5
    assert router.economics.saved > Money.zero()


def test_the_benchmark_report_states_the_numbers_rather_than_claiming_them():
    tasks = _benchmark_tasks()
    router = _router([_capability(CHEAP, tasks), _capability(STRONG, tasks)])
    router.calibrate()
    for p in tasks:
        router.route(_msg(p))
    report = router.report()
    assert "break-even" in report and "saved" in report
    assert "LOSING MONEY" not in report


def test_scripted_model_refuses_to_be_called_more_times_than_it_was_scripted():
    """A silent extra call is how a test 'passes' while asserting nothing."""
    model = ScriptedModel(model_spec=CHEAP, responses=["one"])
    model.complete(_msg("a"), CallOptions())
    with pytest.raises(AssertionError, match="only 1 responses"):
        model.complete(_msg("b"), CallOptions())


# ── Fan-out economics ─────────────────────────────────────────────────────


CHEAP_IN, CHEAP_OUT = Money.from_usd("0.25"), Money.from_usd("1.25")
DEAR_IN, DEAR_OUT = Money.from_usd("5"), Money.from_usd("25")
PRICES = {
    "cheap_in": CHEAP_IN,
    "cheap_out": CHEAP_OUT,
    "expensive_in": DEAR_IN,
    "expensive_out": DEAR_OUT,
}
NARROW = {**PRICES, "cheap_in": Money.from_usd("3"), "cheap_out": Money.from_usd("15")}


def _shape(divergent: bool, context: int = 20_000) -> TokenShape:
    return TokenShape(
        context=context,
        research_output=800,
        synthesis_output=1_500,
        divergent=divergent,
    )


def test_research_fanout_is_cheaper_because_the_cheap_tier_does_the_reading():
    """Legs reading DIFFERENT sources: the single call would have read them all."""
    plan = fanout_plan(legs=6, shape=_shape(divergent=True), **PRICES)
    assert plan.cheaper
    assert plan.ratio < 0.25
    assert "cheaper AND parallel" in plan.verdict


def test_consensus_over_one_prompt_cannot_save_money_at_a_narrow_price_gap():
    """The correction that matters.

    The published argument for fan-out quotes the per-token price gap between
    tiers. That gap is not the comparison: with every leg re-reading one shared
    prompt, and the synthesiser billed at the expensive INPUT rate for every
    leg's output, a 1.7x tier gap makes fan-out multiples dearer rather than
    60% cheaper. It buys answer diversity, and it should be argued for on that.
    """
    plan = fanout_plan(legs=6, shape=_shape(divergent=False), **NARROW)

    assert not plan.cheaper
    assert plan.ratio > 3.0
    assert "buys latency, not money" in plan.verdict

    # Same legs, same prices, different material: now it is cheaper. The flag
    # decides this, not the price gap.
    assert fanout_plan(legs=6, shape=_shape(divergent=True), **NARROW).cheaper


def test_duplicated_context_is_named_because_it_is_the_hidden_term():
    """At long contexts the re-read prompt dominates, and nothing else says so."""
    plan = fanout_plan(legs=10, shape=_shape(divergent=False, context=50_000), **PRICES)
    assert plan.duplicated_context_share > 0.5
    assert f"{plan.duplicated_context_share:.0%}" in plan.verdict


def test_break_even_leg_count_is_the_number_that_decides_the_configuration():
    """Below it fan-out is cheaper; above it you are paying for latency."""
    shape = _shape(divergent=False)
    limit = fanout_plan(legs=3, shape=shape, **PRICES).break_even_legs
    assert limit >= 1
    # At the line the two cost the same, so the parallelism is free.
    assert fanout_plan(legs=limit, shape=shape, **PRICES).ratio <= 1.0
    # One leg past it, every extra leg is bought with money.
    assert not fanout_plan(legs=limit + 1, shape=shape, **PRICES).cheaper


def test_a_wider_tier_gap_moves_break_even_up_rather_than_making_it_free():
    shape = _shape(divergent=False)
    assert (
        fanout_plan(legs=3, shape=shape, **PRICES).break_even_legs
        > fanout_plan(legs=3, shape=shape, **NARROW).break_even_legs
    )


def test_fanout_refuses_a_configuration_it_cannot_price():
    with pytest.raises(ValidationFailed, match="at least one leg"):
        fanout_plan(legs=0, shape=_shape(divergent=True), **PRICES)
    with pytest.raises(ValidationFailed, match="cannot be negative"):
        TokenShape(context=-1, research_output=1, synthesis_output=1)


def test_every_price_is_keyword_only_so_input_and_output_cannot_be_swapped():
    """Six numbers of the same type: a positional call site is a latent bug."""
    signature = inspect.signature(fanout_plan)
    assert all(p.kind is p.KEYWORD_ONLY for p in signature.parameters.values())
