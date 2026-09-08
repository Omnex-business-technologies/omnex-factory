"""The loop closing — and the refusal that stops it closing against itself.

Everything upstream produces outcomes. This turns them into one stream the outer
loop can read, and writes an accepted improvement back as a node claim. The
danger is entirely in that last step: a machine that could write `implemented`
into the ontology would generate the evidence, grade the evidence, and report
coverage climbing.
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
    Asset,
    Capability,
    CostModel,
    Decision,
    NodeClaim,
    Observation,
    Paradigm,
    Portfolio,
    Run,
    RunCost,
    Source,
    Tool,
    claim,
    observe,
    to_run_state,
)
from omnex.factory.compile import Target, assert_round_trips, code, plan
from omnex.harness.contract import Contract, Criterion
from omnex.harness.meta import Health, diagnose

CLOCK = FakeClock()


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
        failure_modes=("tool timeout", "unknown currency code"),
        cost_model=CostModel(Money.from_usd("0.002"), Money.from_usd("0.0005")),
    )


def _economics(runs: int = MINIMUM_RUNS, accepted_every: int = 1) -> AgentEconomics:
    economics = AgentEconomics()
    for index in range(runs):
        economics.record(
            Run(
                run_id=f"r{index}",
                agent="broker",
                customer="acme",
                at=CLOCK.now(),
                revenue=Money.from_usd("0.01"),
                cost=RunCost(model=Money.from_usd("0.002")),
                accepted=index % accepted_every == 0,
            )
        )
    return economics


# ── the closure ───────────────────────────────────────────────────────────
def test_a_loop_may_propose_a_capability() -> None:
    proposed = claim(
        "MCP",
        "omnex.mcp.McpClient",
        "XII",
        (Observation(Source.RUN, "broker", "run r0", True, 1000),),
    )
    assert proposed.claim == "proposed"
    assert "1 of 1 observations accepted" in proposed.evidence


def test_a_loop_may_never_mark_one_implemented() -> None:
    """The whole closure. The thing producing the evidence does not grade it.

    Written as a refusal rather than an absent parameter because somebody will
    construct one directly, and `implemented` is the value they will reach for.
    """
    for attempted in ("implemented", "verified", "done"):
        with pytest.raises(ValidationFailed, match="never mark one"):
            NodeClaim("MCP", "omnex.mcp.McpClient", "XII", "evidence", claim=attempted)


def test_a_claim_naming_a_symbol_that_does_not_import_is_refused() -> None:
    """`node_map.py` would refuse it later. Refusing here says which run produced it."""
    with pytest.raises(ValidationFailed, match="has no attribute"):
        NodeClaim("Telepathy", "omnex.mcp.Telepathy", "XII", "evidence")


def test_having_run_is_not_evidence() -> None:
    """A capability claimed from a stream of failures is claimed from the fact of running."""
    failures = tuple(
        Observation(Source.RUN, "broker", f"run r{i}", False, 1000, reason="nothing usable")
        for i in range(5)
    )
    with pytest.raises(ValidationFailed, match="having run is not evidence"):
        claim("MCP", "omnex.mcp.McpClient", "XII", failures)


# ── observations refuse ───────────────────────────────────────────────────
def test_a_free_observation_is_refused() -> None:
    """The one number the outer loop cannot afford to have gamed.

    Cost per accepted change falls toward zero the more zero-cost observations
    a loop emits, which reports it as cheaper the more noise it produces.
    """
    with pytest.raises(ValidationFailed, match="dilutes cost per accepted change"):
        Observation(Source.RUN, "broker", "run r0", True, 0)


def test_a_rejection_with_no_reason_is_refused() -> None:
    """The part the next run needs most, and the part always dropped first."""
    with pytest.raises(ValidationFailed, match="rejection with no reason"):
        Observation(Source.COMPILE, "n8n", "emit and re-read", False, 1000)


def test_a_persons_attention_costs_something_rather_than_nothing() -> None:
    """It does not appear on an invoice. That is not the same as being free."""
    portfolio = Portfolio(_economics())
    portfolio.add(Asset("broker", accuracy=0.9, growth=0.3))
    portfolio.enact("broker", Decision.SCALE, by="ravezona")
    decisions = [o for o in observe(portfolio=portfolio) if o.source is Source.DECISION]
    assert decisions and all(o.cost_picos > 0 for o in decisions)


def test_deferring_a_decision_does_not_count_as_accepting_one() -> None:
    """Otherwise a portfolio improves its accepted rate by declining to decide."""
    portfolio = Portfolio(_economics())
    portfolio.add(Asset("broker", accuracy=0.9, growth=0.3))
    portfolio.enact("broker", Decision.WATCH, by="ravezona")
    decisions = [o for o in observe(portfolio=portfolio) if o.source is Source.DECISION]
    assert decisions and not decisions[0].accepted
    assert "not the asset earning its place" in decisions[0].reason


# ── the stream the outer loop reads ───────────────────────────────────────
def test_the_three_sources_stay_distinguishable() -> None:
    """ "Runs cost more per result" and "the compilers keep breaking" are not one signal.

    A blended ratio reports them identically, and the intervention for each is
    the opposite of the intervention for the other.
    """
    portfolio = Portfolio(_economics())
    portfolio.add(Asset("broker", accuracy=0.9, growth=0.3))
    portfolio.enact("broker", Decision.SCALE, by="ravezona")
    observations = observe(
        economics=_economics(),
        portfolio=portfolio,
        compiles=(("n8n", True, 1000, ""),),
    )
    state = to_run_state("close the loop", observations)
    criteria = {attempt.criterion for attempt in state.attempts}
    assert criteria == {str(Source.RUN), str(Source.COMPILE), str(Source.DECISION)}
    assert state.ruled_out(str(Source.COMPILE)) == ()


def test_the_outer_loop_reads_the_stream_and_answers() -> None:
    contract = Contract(
        criteria=(Criterion("metered", "runs are metered", "ledger event > 0", frozen=True),)
    )
    state = to_run_state("close the loop", observe(economics=_economics()))
    verdict = diagnose(state, contract)
    assert verdict.health is not Health.UNKNOWN
    assert verdict.cost_per_accepted.picos > 0


def test_a_loop_accepting_nothing_is_visible_rather_than_silent() -> None:
    contract = Contract(criteria=(Criterion("metered", "m", "c", frozen=True),))
    state = to_run_state("close the loop", observe(economics=_economics(accepted_every=99)))
    verdict = diagnose(state, contract)
    assert verdict.accepted <= 1
    assert verdict.spent.picos > 0


def test_an_empty_stream_produces_an_empty_state_rather_than_a_fake_one() -> None:
    assert observe() == ()
    assert to_run_state("nothing happened", ()).attempts == []


# ── the whole chain, end to end ───────────────────────────────────────────
def test_the_chain_runs_from_spec_to_an_observation_the_outer_loop_accepts() -> None:
    """The capstone. Every part of the plan, in one pass, on one agent.

    A spec built from a node the corpus evidenced, compiled to all three targets,
    run on the in-repo runtime, costed in exact pico-dollars, decided in the
    portfolio, and fed back as a proposal that has to resolve against a real
    symbol. If any link is decorative this fails.
    """
    spec = _spec()

    # 1. it compiles, and every target re-reads its own output
    blueprint = plan(spec)
    for target in Target:
        assert_round_trips(blueprint, target)

    # 2. the code target actually runs
    graph = code.emit(blueprint)
    run_result = graph.run({"path": [], "observe_next": "__end__"})
    assert run_result.finished
    assert run_result.state["path"][0] == blueprint.entry

    # 3. every execution costs exact picos and is recorded
    economics = AgentEconomics()
    for index in range(MINIMUM_RUNS):
        economics.record(
            Run(
                run_id=f"chain-{index}",
                agent=spec.name,
                customer="acme",
                at=CLOCK.now(),
                revenue=Money.from_usd("0.01"),
                cost=RunCost(model=Money.from_usd("0.002"), tools=Money.from_usd("0.0005")),
                accepted=True,
            )
        )
    summary = economics.by_agent(spec.name)
    assert summary.total.picos > 0
    assert economics.is_losing_money(spec.name) is False
    assert economics.cost_drift(spec.name, spec) == pytest.approx(1.0)

    # 4. it appears in the portfolio and somebody decides about it
    portfolio = Portfolio(economics)
    portfolio.add(Asset(spec.name, frozenset({"MCP"}), accuracy=0.92, retention=0.8, growth=0.3))
    assert portfolio.recommend(spec.name).decision is Decision.SCALE
    settled = portfolio.enact(spec.name, Decision.SCALE, by="ravezona")
    assert settled.is_decided

    # 5. the outcomes become one stream the outer loop accepts
    observations = observe(
        economics=economics,
        portfolio=portfolio,
        compiles=tuple((str(t), True, 1000, "") for t in Target),
    )
    contract = Contract(
        criteria=(Criterion("metered", "runs are metered", "ledger event > 0", frozen=True),)
    )
    verdict = diagnose(to_run_state("the chain", observations), contract)
    assert verdict.accepted == len(observations)
    assert verdict.cost_per_accepted.picos > 0

    # 6. and it writes back a claim a machine cannot grade
    written = claim("MCP", "omnex.mcp.McpClient", "XII", observations)
    assert written.claim == "proposed"
    with pytest.raises(ValidationFailed):
        NodeClaim(written.node, written.symbol, written.branch, written.evidence, "implemented")
