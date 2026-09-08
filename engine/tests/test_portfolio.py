"""The portfolio: a decision per asset, and the three refusals that keep it honest.

A portfolio table always renders. It renders with a three-run agent graded, with
an agent retired on a number nobody measured, and with one row that reads exactly
like a portfolio. Each of those has a test here forbidding it.
"""

from __future__ import annotations

import pytest

from omnex.core.clock import FakeClock
from omnex.core.errors import ValidationFailed
from omnex.core.money import Money
from omnex.factory import (
    MINIMUM_RUNS,
    AgentEconomics,
    Asset,
    Decision,
    Portfolio,
    Run,
    RunCost,
)

CLOCK = FakeClock()


def _economics(
    agent: str = "broker", runs: int = MINIMUM_RUNS, revenue: str = "0.01", cost: str = "0.002"
) -> AgentEconomics:
    economics = AgentEconomics()
    _fill(economics, agent, runs, revenue, cost)
    return economics


def _fill(
    economics: AgentEconomics, agent: str, runs: int, revenue: str = "0.01", cost: str = "0.002"
) -> AgentEconomics:
    for index in range(runs):
        economics.record(
            Run(
                run_id=f"{agent}-{index}",
                agent=agent,
                customer="acme",
                at=CLOCK.now(),
                revenue=Money.from_usd(revenue),
                cost=RunCost(model=Money.from_usd(cost)),
            )
        )
    return economics


def _portfolio(economics: AgentEconomics | None = None, **asset: object) -> Portfolio:
    portfolio = Portfolio(economics or _economics())
    fields: dict[str, object] = {"agent": "broker", "accuracy": 0.9, "retention": 0.8}
    fields.update(asset)
    portfolio.add(Asset(**fields))  # type: ignore[arg-type]
    return portfolio


# ── recommend is not decide ───────────────────────────────────────────────
def test_a_recommendation_is_unsigned_until_a_person_signs_it() -> None:
    """The node map's rule, at the level where it costs the most.

    `KILL` is irreversible and it is the decision an optimiser under cost
    pressure reaches for first.
    """
    proposed = _portfolio(growth=0.4).recommend("broker")
    assert proposed.by == ""
    assert not proposed.is_decided
    assert "awaiting a person" in proposed.report()


def test_enacting_records_who_and_what_they_overrode() -> None:
    portfolio = _portfolio(growth=0.4)
    settled = portfolio.enact("broker", Decision.LICENSE, by="ravezona", note="partner asked")
    assert settled.is_decided
    assert settled.decision is Decision.LICENSE
    assert any("proposed scale" in r for r in settled.reasons)
    assert any("outranks the proposal" in r for r in settled.reasons)
    assert "partner asked" in settled.reasons


def test_an_unsigned_decision_is_refused() -> None:
    """Nobody can be asked about a decision with no name against it."""
    with pytest.raises(ValidationFailed, match="somebody's name"):
        _portfolio(growth=0.4).enact("broker", Decision.KILL, by="  ")


def test_the_undecided_are_named_because_that_is_the_normal_failure() -> None:
    portfolio = _portfolio(growth=0.4)
    assert portfolio.undecided() == ("broker",)
    portfolio.enact("broker", Decision.SCALE, by="ravezona")
    assert portfolio.undecided() == ()
    assert [r.agent for r in portfolio.decided()] == ["broker"]


# ── the three refusals ────────────────────────────────────────────────────
def test_too_few_runs_is_watch_and_says_so() -> None:
    portfolio = _portfolio(_economics(runs=3), growth=0.4)
    proposed = portfolio.recommend("broker")
    assert proposed.decision is Decision.WATCH
    assert any("below the 10" in r for r in proposed.reasons)


def test_nothing_is_killed_on_a_dimension_nobody_measured() -> None:
    """Retiring an agent for a number nobody has is worse than keeping a losing one."""
    losing = _economics(revenue="0.0001")
    proposed = _portfolio(losing, accuracy=None, growth=0.0).recommend("broker")
    assert proposed.decision is Decision.WATCH
    assert any("never measured" in r for r in proposed.reasons)


def test_merge_needs_two_and_comes_from_overlap_not_from_one_asset() -> None:
    economics = _economics()
    _fill(economics, "reporter", MINIMUM_RUNS)
    portfolio = Portfolio(economics)
    portfolio.add(Asset("broker", frozenset({"MCP", "Cost Ledger"}), accuracy=0.9, growth=0.2))
    portfolio.add(Asset("reporter", frozenset({"Cost Ledger"}), accuracy=0.9, growth=0.2))
    assert portfolio.overlaps() == (("broker", "reporter", frozenset({"Cost Ledger"})),)
    assert Decision.MERGE not in {portfolio.recommend(a.agent).decision for a in portfolio.assets}
    assert "maintained twice" in portfolio.report()


# ── the rules, each naming its evidence ───────────────────────────────────
def test_low_accuracy_is_a_quality_problem_and_repricing_will_not_help() -> None:
    proposed = _portfolio(accuracy=0.4, growth=0.5).recommend("broker")
    assert proposed.decision is Decision.REFACTOR
    assert any("wearing a cost problem" in r for r in proposed.reasons)


def test_losing_but_growing_is_optimise_and_names_the_largest_cost() -> None:
    proposed = _portfolio(_economics(revenue="0.0001"), growth=0.5).recommend("broker")
    assert proposed.decision is Decision.OPTIMISE
    assert any("model" in r for r in proposed.reasons)


def test_losing_with_no_growth_is_kill_proposed_never_enacted() -> None:
    proposed = _portfolio(_economics(revenue="0.0001"), growth=0.0).recommend("broker")
    assert proposed.decision is Decision.KILL
    assert not proposed.is_decided, "a machine retired an agent"


def test_profitable_and_growing_is_scale() -> None:
    assert _portfolio(growth=0.5).recommend("broker").decision is Decision.SCALE


def test_profitable_flat_and_leaking_customers_is_reposition() -> None:
    proposed = _portfolio(growth=0.0, retention=0.2).recommend("broker")
    assert proposed.decision is Decision.REPOSITION
    assert any("wrong buyer" in r for r in proposed.reasons)


def test_profitable_flat_and_sticky_is_license() -> None:
    assert _portfolio(growth=0.0, retention=0.9).recommend("broker").decision is Decision.LICENSE


def test_growth_that_was_never_measured_is_not_read_as_no_growth() -> None:
    """`None` means unmeasured. Reading it as zero retires software for a missing metric."""
    losing = _portfolio(_economics(revenue="0.0001"), growth=None, accuracy=0.9)
    assert losing.recommend("broker").decision is Decision.KILL
    growing = _portfolio(_economics(revenue="0.0001"), growth=0.5, accuracy=0.9)
    assert growing.recommend("broker").decision is Decision.OPTIMISE


# ── the asset refuses ─────────────────────────────────────────────────────
@pytest.mark.parametrize("field_name", ["accuracy", "retention"])
def test_a_rate_outside_zero_to_one_is_refused(field_name: str) -> None:
    with pytest.raises(ValidationFailed, match=r"outside 0\.0-1\.0"):
        Asset("broker", **{field_name: 1.5})  # type: ignore[arg-type]


def test_an_asset_cannot_be_added_twice() -> None:
    portfolio = _portfolio()
    with pytest.raises(ValidationFailed, match="already in the portfolio"):
        portfolio.add(Asset("broker"))


def test_an_agent_outside_the_portfolio_is_refused_with_the_list() -> None:
    with pytest.raises(ValidationFailed) as caught:
        _portfolio().recommend("ghost")
    assert caught.value.context["known"] == ["broker"]


# ── the honest limit ──────────────────────────────────────────────────────
def test_one_asset_says_it_is_not_a_portfolio() -> None:
    """A one-row table reads exactly like a portfolio, which is the problem."""
    report = _portfolio(growth=0.3).report()
    assert report.startswith("n=1. This is not a portfolio yet")
    assert "not evidence that there are any" in report


def test_two_assets_stop_saying_it() -> None:
    economics = _economics()
    _fill(economics, "reporter", MINIMUM_RUNS)
    portfolio = Portfolio(economics)
    portfolio.add(Asset("broker", accuracy=0.9, growth=0.2))
    portfolio.add(Asset("reporter", accuracy=0.9, growth=0.2))
    assert "not a portfolio yet" not in portfolio.report()


def test_total_margin_sums_the_assets_and_nothing_else() -> None:
    economics = _economics()
    _fill(economics, "reporter", MINIMUM_RUNS)
    _fill(economics, "unlisted", MINIMUM_RUNS)
    portfolio = Portfolio(economics)
    portfolio.add(Asset("broker", accuracy=0.9))
    portfolio.add(Asset("reporter", accuracy=0.9))
    expected = economics.by_agent("broker").total + economics.by_agent("reporter").total
    assert portfolio.total_margin() == expected
    assert portfolio.total_margin() != economics.overall().total
