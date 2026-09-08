"""The factory: a spec that can be refused, and an order that cannot be skipped.

Every test here forbids a specific plausible-looking behaviour. A specification
is unusually easy to get wrong convincingly — it is prose with fields, it always
renders, and the failure appears months later as a margin nobody can explain or
an agent nobody approved in its current shape.
"""

from __future__ import annotations

import dataclasses

import pytest

from omnex.core.errors import ValidationFailed
from omnex.core.money import Money
from omnex.factory import AgentSpec, Capability, CostModel, Gate, Paradigm, Stage, Tool, start
from omnex.harness.contract import Criterion, Proposal

WORTH_IT = {
    "repeats_weekly": True,
    "verification_is_automated": True,
    "budget_absorbs_waste": True,
    "agent_has_tools": True,
    "has_goal_metric": True,
    "has_change_method": True,
    "has_standard_assessment": True,
}


def _spec(**overrides: object) -> AgentSpec:
    base: dict[str, object] = {
        "name": "mcp-broker",
        "role": "answers currency questions over MCP tools",
        "capabilities": (Capability("MCP", "omnex.mcp.McpClient"),),
        "tools": (Tool("convert", "mcp", Money.from_usd("0.0001")),),
        "memory_policy": "nothing beyond the turn",
        "context_policy": "tool output enters untrusted",
        "paradigm": Paradigm.REACT,
        "eval_suite": "fx_golden",
        "governance": "no spend above 1 USD without a human approval",
        "failure_modes": ("tool timeout", "unknown currency code"),
        "cost_model": CostModel(Money.from_usd("0.002"), Money.from_usd("0.0005")),
    }
    base.update(overrides)
    return AgentSpec(**base)  # type: ignore[arg-type]


# ── the spec refuses ──────────────────────────────────────────────────────
def test_a_complete_spec_has_nothing_to_report() -> None:
    assert _spec().audit() == []


def test_a_capability_naming_a_symbol_that_does_not_import_is_refused() -> None:
    """The point of the whole chain, enforced where it is cheapest.

    A spec that reads correctly and builds nothing is the expensive kind of
    document, and "Vector Search" was a gap in the node map for exactly this
    reason: a name is not a capability until something backs it.
    """
    spec = _spec(capabilities=(Capability("Telepathy", "omnex.mcp.Telepathy"),))
    problems = spec.audit()
    assert any("has no attribute" in p for p in problems)


def test_an_unpriced_tool_cannot_be_specified() -> None:
    with pytest.raises(ValidationFailed, match="no price"):
        Tool("free", "mcp", Money.zero())


def test_a_run_that_costs_nothing_has_not_been_costed() -> None:
    with pytest.raises(ValidationFailed, match="has not been costed"):
        CostModel(Money.zero(), Money.zero())


def test_an_agent_with_no_named_failure_modes_is_refused() -> None:
    """Unlisted failures mean the agent was imagined, not designed."""
    problems = _spec(failure_modes=()).audit()
    assert any("imagined rather than designed" in p for p in problems)


def test_every_problem_is_reported_at_once() -> None:
    """Being refused one thing at a time is how somebody concludes the check is the obstacle."""
    spec = _spec(
        role="thing",
        failure_modes=(),
        eval_suite="",
        governance="",
        capabilities=(Capability("Nope", "omnex.mcp.Nope"),),
    )
    problems = spec.audit()
    assert len(problems) >= 5
    with pytest.raises(ValidationFailed) as caught:
        spec.raise_if_incomplete()
    assert len(caught.value.context["problems"]) == len(problems)


def test_two_tools_sharing_a_name_hide_one_of_their_prices() -> None:
    spec = _spec(
        tools=(
            Tool("convert", "mcp", Money.from_usd("0.0001")),
            Tool("convert", "http", Money.from_usd("0.02")),
        )
    )
    assert any("share a name" in p for p in spec.audit())


# ── the spec is bound to itself ───────────────────────────────────────────
@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("role", "does something else entirely"),
        ("memory_policy", "remembers everything forever"),
        ("context_policy", "trusts tool output"),
        ("paradigm", Paradigm.SUPERVISOR_CREW),
        ("eval_suite", "an_easier_suite"),
        ("governance", "no approval needed"),
        ("failure_modes", ("only one",)),
        ("cost_model", CostModel(Money.from_usd("0.001"), Money.from_usd("0.0001"))),
        ("tools", (Tool("convert", "mcp", Money.from_usd("0.5")),)),
        ("capabilities", (Capability("MCP", "omnex.mcp.McpServer"),)),
    ],
)
def test_changing_any_field_changes_the_fingerprint(field_name: str, value: object) -> None:
    """A fingerprint that misses a field is worse than none: it certifies the gap."""
    original = _spec()
    edited = dataclasses.replace(original, **{field_name: value})
    assert edited.fingerprint != original.fingerprint, field_name


def test_a_spec_edited_after_agreement_fails_its_own_fingerprint() -> None:
    spec = _spec()
    _, fingerprint = spec.agree()
    rescoped = dataclasses.replace(spec, governance="no approval needed")
    with pytest.raises(ValidationFailed, match="changed after it was agreed"):
        rescoped.assert_unchanged(fingerprint)


def test_the_contract_freezes_what_an_optimiser_would_relax_first() -> None:
    contract, _ = _spec().agree()
    assert contract.agreed
    assert contract.frozen_keys >= {
        "untrusted_tool_results",
        "metered_runs",
        "graded_before_shipped",
    }


def test_the_frozen_criteria_refuse_to_be_weakened() -> None:
    """The anchor. A criterion a loop can thaw is not an anchor."""
    contract, _ = _spec().agree()
    weakened = tuple(
        (
            Criterion(c.key, c.statement, "the agent reports success", frozen=True)
            if c.key == "metered_runs"
            else c
        )
        for c in contract.criteria
    )
    with pytest.raises(ValidationFailed, match="makes the test easier"):
        contract.negotiate(Proposal(criteria=weakened))


def test_a_dropped_frozen_criterion_is_refused_too() -> None:
    contract, _ = _spec().agree()
    without = tuple(c for c in contract.criteria if c.key != "untrusted_tool_results")
    with pytest.raises(ValidationFailed, match="drops frozen criterion"):
        contract.negotiate(Proposal(criteria=without))


# ── the order is a type ───────────────────────────────────────────────────
def test_stages_compare_by_position_and_not_alphabetically() -> None:
    """The StrEnum trap, and it answers wrongly rather than raising.

    `StrEnum` inherits `str`'s comparisons, so "deploy" < "idea" is True and a
    pipeline ordered by it permits every backwards move whose name happens to
    sort earlier. The check still reads as though it works.
    """
    assert Stage.IDEA < Stage.DEPLOY
    assert not Stage.DEPLOY < Stage.IDEA
    assert str(Stage.DEPLOY) < str(Stage.IDEA), "the string order is no longer the trap"


def test_all_four_comparisons_are_defined_on_the_stage_itself() -> None:
    """`@total_ordering` would fill in nothing here — it only supplies missing ones.

    Stage inherits all four from `str`, so a decorator sees nothing to add and
    the inherited, wrong versions survive. They have to be written out.
    """
    for dunder in ("__lt__", "__le__", "__gt__", "__ge__"):
        assert dunder in Stage.__dict__, f"{dunder} is inherited from str"


def test_comparing_a_stage_to_something_else_defers_rather_than_guesses() -> None:
    assert Stage.IDEA.__lt__("deploy") is NotImplemented


def test_the_order_is_the_declaration_order() -> None:
    stages = list(Stage)
    assert [s.position for s in stages] == list(range(len(stages)))
    assert stages[0] is Stage.IDEA
    assert stages[-1] is Stage.SCALE_OR_KILL


# ── the pipeline ──────────────────────────────────────────────────────────
def test_worth_it_runs_at_the_head_of_the_order() -> None:
    pipeline = start(_spec()).idea(**WORTH_IT)
    assert pipeline.reached is Stage.IDEA


def test_a_loop_that_cannot_repay_itself_is_refused_before_anything_is_drawn() -> None:
    conditions = {**WORTH_IT, "repeats_weekly": False, "has_goal_metric": False}
    with pytest.raises(ValidationFailed) as caught:
        start(_spec()).idea(**conditions)
    assert len(caught.value.context["reasons"]) == 2, "only the first failure was named"


def test_a_stage_cannot_be_skipped() -> None:
    """Prose says architecture is fourth. A type makes the shortcut deliberate."""
    pipeline = start(_spec()).idea(**WORTH_IT)
    with pytest.raises(ValidationFailed, match="out of order"):
        pipeline.architecture()


def test_a_stage_cannot_be_repeated_or_walked_backwards() -> None:
    pipeline = start(_spec()).idea(**WORTH_IT)
    with pytest.raises(ValidationFailed, match="out of order"):
        pipeline.idea(**WORTH_IT)


def test_a_refused_gate_stops_the_pipeline_rather_than_being_recorded() -> None:
    """ "Recorded as failed and continued" is the shape of having no order at all."""
    pipeline = start(_spec()).idea(**WORTH_IT)
    with pytest.raises(ValidationFailed, match="refused"):
        pipeline.advance(Gate(Stage.MARKET, passed=False, reasons=("no buyer named",)))
    assert pipeline.reached is Stage.IDEA


def test_a_negative_contribution_margin_is_refused_at_specification_time() -> None:
    """`router.is_losing_money()` asks this per call. This asks it before building."""
    pipeline = start(_spec()).idea(**WORTH_IT)
    pipeline.advance(Gate(Stage.MARKET, passed=True, note="one named buyer"))
    with pytest.raises(ValidationFailed, match="contribution margin"):
        pipeline.unit_economics(Money.from_usd("0.001"))


def test_a_spec_rescoped_mid_pipeline_fails_the_next_gate() -> None:
    """Approved on numbers that no longer describe it, and nothing else would notice."""
    pipeline = start(_spec()).idea(**WORTH_IT)
    pipeline.spec = dataclasses.replace(
        pipeline.spec, cost_model=CostModel(Money.from_usd("9"), Money.from_usd("1"))
    )
    with pytest.raises(ValidationFailed, match="changed after it was agreed"):
        pipeline.advance(Gate(Stage.MARKET, passed=True))


def test_the_full_order_runs_end_to_end() -> None:
    spec = _spec()
    pipeline = start(spec).idea(**WORTH_IT)
    pipeline.advance(Gate(Stage.MARKET, passed=True, note="one named buyer"))
    pipeline.unit_economics(Money.from_usd("0.01"))
    pipeline.architecture()
    for stage in (
        Stage.SIMULATION,
        Stage.EVALUATION,
        Stage.SECURITY,
        Stage.DEPLOY,
        Stage.OBSERVE,
        Stage.SCALE_OR_KILL,
    ):
        pipeline.advance(Gate(stage, passed=True, note="evidence supplied by a person"))
    assert pipeline.reached is Stage.SCALE_OR_KILL
    assert len(pipeline.passed) == len(list(Stage))


def test_the_report_names_what_has_not_been_reached() -> None:
    """A pipeline that only lists its successes reads as finished."""
    report = start(_spec()).idea(**WORTH_IT).report()
    assert "not yet:" in report
    assert "scale_or_kill" in report


def test_start_binds_both_fingerprints() -> None:
    """Either one alone can hold while the other has moved underneath it."""
    pipeline = start(_spec())
    assert pipeline.spec_fingerprint == pipeline.spec.fingerprint
    assert pipeline.contract_fingerprint == pipeline.spec.contract().fingerprint
    assert pipeline.spec_fingerprint != pipeline.contract_fingerprint


# ── one resolver, not two ─────────────────────────────────────────────────
def test_the_factory_and_the_ontology_scripts_share_one_resolver() -> None:
    """The splitter lesson, applied before it costs anything.

    `rag/ingest.py` and citegate hold two copies of one sentence splitter, and a
    quadratic fixed in the first survived in the second for a further commit.
    Symbol resolution is now imported by everything that needs it rather than
    copied into each.
    """
    import ontology_map

    from omnex.core.symbols import resolve
    from omnex.factory import spec as factory_spec

    assert ontology_map.resolve is resolve
    assert factory_spec.resolve is resolve
