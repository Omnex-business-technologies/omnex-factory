"""Money attached to a run — and the four places this arithmetic lies convincingly.

A margin is a number, so it always renders. It renders when acquisition has been
charged to every run, when failures have been quietly excluded, when three runs
have been reported as a verdict, and when the mean has hidden the tail that
carries the cost. None of those look wrong on a dashboard.
"""

from __future__ import annotations

import pytest

from omnex.core.clock import FakeClock
from omnex.core.errors import ValidationFailed
from omnex.core.money import Money
from omnex.factory import (
    MINIMUM_RUNS,
    AgentEconomics,
    AgentSpec,
    Capability,
    CostModel,
    Paradigm,
    Run,
    RunCost,
    Tool,
)

CLOCK = FakeClock()
CHEAP = RunCost(model=Money.from_usd("0.002"), tools=Money.from_usd("0.0005"))


def _run(index: int, **overrides: object) -> Run:
    base: dict[str, object] = {
        "run_id": f"run-{index}",
        "agent": "broker",
        "customer": "acme",
        "at": CLOCK.now(),
        "revenue": Money.from_usd("0.01"),
        "cost": CHEAP,
        "accepted": True,
    }
    base.update(overrides)
    return Run(**base)  # type: ignore[arg-type]


def _filled(count: int = MINIMUM_RUNS, **overrides: object) -> AgentEconomics:
    economics = AgentEconomics()
    for index in range(count):
        economics.record(_run(index, **overrides))
    return economics


def _spec() -> AgentSpec:
    return AgentSpec(
        name="broker",
        role="answers currency questions over MCP tools",
        capabilities=(Capability("MCP", "omnex.mcp.McpClient"),),
        tools=(Tool("convert", "mcp", Money.from_usd("0.0001")),),
        memory_policy="nothing beyond the turn",
        context_policy="tool output enters untrusted",
        paradigm=Paradigm.REACT,
        eval_suite="fx_golden",
        governance="no spend above 1 USD without a human approval",
        failure_modes=("tool timeout",),
        cost_model=CostModel(Money.from_usd("0.002"), Money.from_usd("0.0005")),
    )


# ── acquisition is not a per-run cost ─────────────────────────────────────
def test_acquisition_does_not_touch_contribution_margin() -> None:
    """Charging it per run makes a customer look worse the more they use the product.

    That inverts the signal exactly: the heaviest user, who is repaying the
    acquisition fastest, shows the worst margin.
    """
    economics = _filled()
    before = economics.by_customer("acme").total
    economics.record_acquisition("acme", Money.from_usd("50.00"))
    assert economics.by_customer("acme").total == before


def test_payback_is_answered_separately_and_in_runs() -> None:
    economics = _filled()
    economics.record_acquisition("acme", Money.from_usd("1.00"))
    mean = economics.by_customer("acme").mean
    assert economics.payback_runs("acme") == -(-Money.from_usd("1.00").picos // mean.picos)


def test_payback_on_a_losing_customer_is_none_rather_than_a_big_number() -> None:
    """An infinite payback reported as an integer is a number somebody puts in a slide."""
    economics = _filled(revenue=Money.zero())
    economics.record_acquisition("acme", Money.from_usd("1.00"))
    assert economics.payback_runs("acme") is None


def test_payback_is_none_when_nothing_was_spent_winning_them() -> None:
    assert _filled().payback_runs("acme") is None


# ── a failed run still costs ──────────────────────────────────────────────
def test_a_failed_run_is_costed_and_counted() -> None:
    """Excluding failures makes the cheapest agent one that fails everything."""
    economics = AgentEconomics()
    for index in range(MINIMUM_RUNS):
        economics.record(_run(index, accepted=False, revenue=Money.zero()))
    summary = economics.overall()
    assert summary.runs == MINIMUM_RUNS
    assert summary.acceptance_rate == 0.0
    assert summary.cost.picos > 0
    assert summary.total.picos < 0, "a run that earned nothing and spent money broke even"


def test_acceptance_rate_and_margin_are_separate_questions() -> None:
    economics = AgentEconomics()
    for index in range(MINIMUM_RUNS):
        economics.record(_run(index, accepted=index % 2 == 0))
    assert economics.overall().acceptance_rate == 0.5
    assert economics.overall().total.picos > 0


# ── a verdict needs enough runs ───────────────────────────────────────────
def test_no_verdict_below_the_minimum() -> None:
    """Three-valued on purpose. A boolean forces a caller to guess, wrongly, half the time."""
    economics = _filled(count=MINIMUM_RUNS - 1)
    assert economics.is_losing_money() is None
    assert economics.is_losing_money("broker") is None


def test_a_verdict_arrives_at_the_minimum_and_is_correct() -> None:
    assert _filled().is_losing_money("broker") is False
    losing = _filled(revenue=Money.from_usd("0.001"))
    assert losing.is_losing_money("broker") is True


def test_an_unknown_agent_has_no_verdict_rather_than_a_clean_one() -> None:
    assert _filled().is_losing_money("nobody") is None


# ── the mean hides the tail ───────────────────────────────────────────────
def test_the_distribution_is_reported_and_not_just_the_mean() -> None:
    """A handful of long runs carry the cost; the mean sits above almost all of them."""
    economics = AgentEconomics()
    for index in range(MINIMUM_RUNS - 1):
        economics.record(_run(index))
    economics.record(_run(99, cost=RunCost(model=Money.from_usd("5.00"))))
    summary = economics.overall()
    assert summary.worst.picos < 0, "the expensive run did not show as a loss"
    assert summary.worst < summary.median
    assert summary.p10 <= summary.median


def test_the_mean_never_drifts_from_the_total_it_describes() -> None:
    """Averaging per-run means rounds each one; dividing the total rounds once."""
    economics = AgentEconomics()
    for index in range(7):
        economics.record(_run(index, revenue=Money.from_picos(1_000_000_003)))
    summary = economics.overall()
    assert summary.mean.picos == summary.total.picos // summary.runs
    assert summary.total == summary.revenue - summary.cost


# ── recording refuses ─────────────────────────────────────────────────────
def test_the_same_run_cannot_be_recorded_twice() -> None:
    """Double-counting moves the margin in whichever direction that run went."""
    economics = _filled()
    with pytest.raises(ValidationFailed, match="already recorded"):
        economics.record(_run(0))


def test_a_negative_cost_is_refused() -> None:
    with pytest.raises(ValidationFailed, match="refund path"):
        RunCost(model=Money.from_picos(-1))


# ── which lever to pull ───────────────────────────────────────────────────
def test_the_dominant_cost_category_is_named() -> None:
    """A total says the agent is expensive. The split says what would help."""
    economics = AgentEconomics()
    for index in range(MINIMUM_RUNS):
        economics.record(
            _run(
                index,
                cost=RunCost(model=Money.from_usd("0.001"), human_review=Money.from_usd("0.40")),
            )
        )
    assert economics.worst_category("broker") == "human_review"
    assert economics.by_agent("broker").runs == MINIMUM_RUNS


def test_a_run_cost_names_its_own_largest_category() -> None:
    assert RunCost(model=Money.from_usd("1"), tools=Money.from_usd("2")).largest == "tools"


def test_worst_category_is_none_for_an_agent_with_no_runs() -> None:
    assert AgentEconomics().worst_category("broker") is None


# ── estimate versus measurement ───────────────────────────────────────────
def test_cost_drift_compares_what_was_approved_against_what_happened() -> None:
    """The unit-economics gate clears an agent on an ESTIMATE. This is the measurement.

    `metering.ts` returns `estimated: boolean` for the same reason: an estimate
    displayed as a measurement is the failure both of them prevent.
    """
    spec = _spec()
    assert _filled().cost_drift("broker", spec) == pytest.approx(1.0)

    expensive = AgentEconomics()
    for index in range(MINIMUM_RUNS):
        expensive.record(_run(index, cost=RunCost(model=Money.from_usd("0.0075"))))
    drift = expensive.cost_drift("broker", spec)
    assert drift is not None and drift == pytest.approx(3.0)


def test_cost_drift_says_nothing_before_it_has_enough_runs() -> None:
    assert _filled(count=MINIMUM_RUNS - 1).cost_drift("broker", _spec()) is None


def test_nothing_here_decides_to_kill_an_agent() -> None:
    """`scale_or_kill` is a stage a person reaches.

    A factory that killed its own agents on a ratio would be grading its own
    homework with a budget, which is the judgement every claim-level rule in this
    repository refuses to let a machine make.
    """
    economics = AgentEconomics()
    assert not [name for name in dir(economics) if "kill" in name or "retire" in name]


# ── the report ────────────────────────────────────────────────────────────
def test_the_report_says_when_it_cannot_say() -> None:
    report = _filled(count=3).report()
    assert "not enough runs to say (3 of 10)" in report


def test_the_report_names_the_lever() -> None:
    assert "largest cost: model" in _filled().report()


def test_an_empty_ledger_reports_nothing_rather_than_zero_margin() -> None:
    """Zero margin on no runs reads as a break-even agent, and there is no agent."""
    assert AgentEconomics().report() == "no runs recorded"


def test_the_distribution_and_the_total_come_from_one_definition_of_margin() -> None:
    """Found by `scripts/mutate.py`, which is the only reason it exists.

    `Run.margin` is revenue less variable cost. `_summarise` computes the total
    by summing revenue and cost SEPARATELY and subtracting once — a different
    code path that happens to agree. Nothing asserted that it must.

    A mutation changing `Run.margin` therefore survived the whole suite: the
    total and the verdict were unaffected, and only the median, p10 and worst
    quietly moved. A summary whose distribution disagrees with its own total is
    exactly the kind of wrong that reads as fine, since each number is
    individually plausible.
    """
    economics = AgentEconomics()
    revenues = ["0.010", "0.030", "0.007", "0.250", "0.001"]
    for index, revenue in enumerate(revenues):
        economics.record(
            _run(
                index,
                revenue=Money.from_usd(revenue),
                cost=RunCost(model=Money.from_usd("0.002"), tools=Money.from_usd("0.0005")),
            )
        )

    summary = economics.overall()
    from_runs = Money.zero()
    for run in economics.runs:
        from_runs = from_runs + run.margin

    assert summary.total == from_runs, "the total and the per-run margins disagree"
    assert summary.worst == min((run.margin for run in economics.runs), key=lambda m: m.picos)
    assert summary.mean.picos == from_runs.picos // len(revenues)
