"""Three targets, one blueprint, and the round trip that decides whether they work.

A lossy compiler is invisible from its output. The workflow still imports, the
manifest still parses, the graph still runs — with a field quietly missing, and
the discovery happens at the first deployment that needed it. So the tests here
are mostly the same assertion applied three ways, plus the one that matters
most: proof that the assertion can fail.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from omnex.core.errors import ValidationFailed
from omnex.core.money import Money
from omnex.factory import AgentSpec, Capability, CostModel, Paradigm, Tool
from omnex.factory.compile import (
    Target,
    assert_round_trips,
    bindings,
    code,
    mcp_topology,
    n8n,
    plan,
    round_trip,
)
from omnex.factory.compile.blueprint import Blueprint, Step, StepKind
from omnex.graph.runtime import END, Graph


def _spec(paradigm: Paradigm = Paradigm.REACT, **overrides: object) -> AgentSpec:
    base: dict[str, object] = {
        "name": "mcp-broker",
        "role": "answers currency questions over MCP tools",
        "capabilities": (
            Capability("MCP", "omnex.mcp.McpClient"),
            Capability("Cost Ledger", "omnex.obs.CostLedger"),
        ),
        "tools": (
            Tool("convert", "mcp", Money.from_usd("0.0001")),
            Tool("rates", "mcp", Money.from_usd("0.0000005")),
        ),
        "memory_policy": "nothing beyond the turn",
        "context_policy": "tool output enters untrusted",
        "paradigm": paradigm,
        "eval_suite": "fx_golden",
        "governance": "no spend above 1 USD without a human approval",
        "failure_modes": ("tool timeout", "unknown currency code"),
        "cost_model": CostModel(Money.from_usd("0.002"), Money.from_usd("0.0005")),
    }
    base.update(overrides)
    return AgentSpec(**base)  # type: ignore[arg-type]


ALL_PARADIGMS = list(Paradigm)
REPO = Path(__file__).resolve().parents[2]


# ── the round trip, three targets by five paradigms ────────────────────────
@pytest.mark.parametrize("target", list(Target))
@pytest.mark.parametrize("paradigm", ALL_PARADIGMS)
def test_every_target_round_trips_every_paradigm(target: Target, paradigm: Paradigm) -> None:
    """`parse(emit(bp)) == bp`, for all fifteen combinations.

    A field added to `Blueprint` and forgotten in one emitter fails here rather
    than at the first deployment that needed it.
    """
    assert_round_trips(plan(_spec(paradigm)), target)


def test_the_round_trip_check_can_actually_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    """The test that makes the other fifteen worth running.

    A check that passes because it compares an artifact with itself proves
    nothing. This corrupts one field in the emitter and requires the difference
    to be named — not reported as a boolean, because "lossy" is not actionable and
    "step call_convert lost its ref" is.
    """
    blueprint = plan(_spec())
    original = mcp_topology.emit

    def lossy(bp: Blueprint) -> str:
        payload = json.loads(original(bp))
        for step in payload["steps"]:
            if step["kind"] == "tool":
                step["ref"] = "wrong.Reference"
        return json.dumps(payload)

    monkeypatch.setattr(mcp_topology, "emit", lossy)
    with pytest.raises(ValidationFailed, match="does not round-trip") as caught:
        assert_round_trips(blueprint, Target.MCP)
    assert any("call_convert" in d for d in caught.value.context["differences"])


def test_a_lost_edge_is_caught_too(monkeypatch: pytest.MonkeyPatch) -> None:
    """Losing an END edge is the failure a workflow hides best: it still opens."""
    blueprint = plan(_spec())
    original = n8n.emit

    def lossy(bp: Blueprint, *args: object, **kwargs: object) -> str:
        payload = json.loads(original(bp, *args, **kwargs))  # type: ignore[arg-type]
        payload["meta"]["omnexEnds"] = []
        return json.dumps(payload)

    monkeypatch.setattr(n8n, "emit", lossy)
    with pytest.raises(ValidationFailed, match="does not round-trip"):
        assert_round_trips(blueprint, Target.N8N)


# ── the blueprint refuses ──────────────────────────────────────────────────
def test_a_step_that_goes_nowhere_is_refused() -> None:
    with pytest.raises(ValidationFailed, match="goes nowhere"):
        Step("orphan", StepKind.CONTROL, "", ())


def test_a_control_step_carrying_a_reference_is_refused() -> None:
    with pytest.raises(ValidationFailed, match="carries a reference"):
        Step("think", StepKind.CONTROL, "omnex.mcp.McpClient", (END,))


def test_a_dangling_target_is_named() -> None:
    blueprint = Blueprint(
        agent="a",
        spec_fingerprint="f",
        paradigm="single",
        entry="one",
        steps=(Step("one", StepKind.CONTROL, "", ("two",)),),
        tool_picos=(),
    )
    assert any("does not exist" in p for p in blueprint.validate())


def test_an_unreachable_step_is_named() -> None:
    """A node nothing routes to is a node that will never run, silently."""
    blueprint = Blueprint(
        agent="a",
        spec_fingerprint="f",
        paradigm="single",
        entry="one",
        steps=(
            Step("one", StepKind.CONTROL, "", (END,)),
            Step("stranded", StepKind.CONTROL, "", (END,)),
        ),
        tool_picos=(),
    )
    assert any("unreachable" in p for p in blueprint.validate())


def test_an_incomplete_spec_never_compiles() -> None:
    """An artifact that looks deployable and refers to nothing is worse than none."""
    with pytest.raises(ValidationFailed, match="not complete"):
        plan(_spec(capabilities=(Capability("Ghost", "omnex.mcp.Ghost"),)))


def test_the_same_paradigm_gives_the_same_skeleton() -> None:
    """Shape comes from the spec, so a difference in output means a difference in spec."""
    first = plan(_spec(Paradigm.PLANNER_EXECUTOR))
    second = plan(_spec(Paradigm.PLANNER_EXECUTOR, name="other", role="does another job"))
    assert [s.name for s in first.steps] == [s.name for s in second.steps]
    assert first.digest != second.digest, "the digest ignores the agent it describes"


# ── the code target runs ───────────────────────────────────────────────────
def test_the_emitted_graph_is_the_graph_the_runtime_executes() -> None:
    """The reason the code target emits an object rather than a file.

    Round-tripping source proves text survived a text transformation. Reading
    the built graph back through `topology()` proves the thing that would
    actually run has the topology the blueprint described.
    """
    blueprint = plan(_spec(Paradigm.PLANNER_EXECUTOR))
    graph = code.emit(blueprint)
    run = graph.run({"path": []})
    assert run.finished
    assert run.state["path"][0] == blueprint.entry
    assert run.state["path"][-1] == "review"


def test_a_branch_takes_the_target_the_state_names() -> None:
    blueprint = plan(_spec(Paradigm.REACT))
    graph = code.emit(blueprint)
    run = graph.run({"path": [], "observe_next": END})
    assert run.finished
    assert run.state["path"].count("think") == 1, "the loop did not exit where told"


def test_parse_refuses_a_graph_that_is_not_the_blueprint() -> None:
    """Reconstructing the missing parts from the original must not extend to inventing steps."""
    blueprint = plan(_spec())
    other = Graph()
    other.add_node("unrelated", lambda state: None)
    other.add_edge("unrelated", END)
    other.set_entry("unrelated")
    with pytest.raises(ValidationFailed, match="does not contain the steps"):
        code.parse(other, blueprint)


# ── the runtime gained a check ─────────────────────────────────────────────
def test_a_router_target_typo_now_fails_before_anything_runs() -> None:
    """Previously caught by `_next` mid-run, after earlier nodes had spent money."""
    graph = Graph()
    graph.add_node("start", lambda state: None)
    graph.add_conditional_edge("start", lambda state: "typo", targets=("typo",))
    graph.set_entry("start")
    with pytest.raises(ValidationFailed, match="declares unknown target"):
        graph.validate()


def test_topology_reports_declared_branches_and_plain_edges_alike() -> None:
    graph = Graph()
    graph.add_node("a", lambda state: None)
    graph.add_node("b", lambda state: None)
    graph.add_edge("a", "b")
    graph.add_conditional_edge("b", lambda state: END, targets=("a", END))
    graph.set_entry("a")
    assert graph.topology() == {"a": ("b",), "b": ("a", END)}


# ── the mcp manifest ───────────────────────────────────────────────────────
def test_prices_cross_the_wire_as_integer_picos() -> None:
    """The one field where a float is silently wrong rather than loudly wrong."""
    payload = json.loads(mcp_topology.emit(plan(_spec())))
    picos = [tool["picos"] for tool in payload["tools"]]
    assert all(isinstance(p, int) for p in picos)
    assert 500_000 in picos, "a half-micro-dollar tool lost its price"


def test_a_price_that_is_not_an_integer_is_refused_on_read() -> None:
    payload = json.loads(mcp_topology.emit(plan(_spec())))
    payload["tools"][0]["picos"] = 0.0001
    with pytest.raises(ValidationFailed, match="integer count of picos"):
        mcp_topology.parse(json.dumps(payload))


def test_a_manifest_from_another_version_is_refused() -> None:
    """Reading it anyway applies this version's meanings to another version's fields."""
    payload = json.loads(mcp_topology.emit(plan(_spec())))
    payload["manifest"] = 99
    with pytest.raises(ValidationFailed, match="version mismatch"):
        mcp_topology.parse(json.dumps(payload))


# ── the n8n workflow ───────────────────────────────────────────────────────
def test_every_n8n_node_says_in_the_file_that_it_is_a_placeholder() -> None:
    """Whoever imports this must read it there, not in a commit message.

    The spec names a tool and its price. It does not name the endpoint, the
    credential or the payload, and a compiler that filled those in would ship
    invented configuration as though somebody had supplied it.
    """
    payload = json.loads(n8n.emit(plan(_spec())))
    assert payload["nodes"]
    for node in payload["nodes"]:
        assert "Placeholder" in node["notes"]
        assert node["type"] == "n8n-nodes-base.noOp"


def test_the_canvas_reads_left_to_right_from_the_entry() -> None:
    """A workflow with every node at the origin is a pile, not a diagram."""
    blueprint = plan(_spec(Paradigm.PLANNER_EXECUTOR))
    payload = json.loads(n8n.emit(blueprint))
    positions = {node["name"]: node["position"] for node in payload["nodes"]}
    assert positions[blueprint.entry][0] == 0
    assert positions["review"][0] > positions[blueprint.entry][0]
    assert len({tuple(p) for p in positions.values()}) == len(positions), "two nodes overlap"


def test_a_hand_moved_node_does_not_read_back_as_a_topology_change() -> None:
    """Positions are canvas, not meaning. Somebody will drag a node."""
    blueprint = plan(_spec())
    payload = json.loads(n8n.emit(blueprint))
    payload["nodes"][0]["position"] = [9999, 9999]
    assert n8n.parse(json.dumps(payload)) == blueprint


def test_a_workflow_this_did_not_emit_is_refused_rather_than_guessed() -> None:
    with pytest.raises(ValidationFailed, match="not emitted from a blueprint"):
        n8n.parse(json.dumps({"name": "someone else's", "nodes": [], "connections": {}}))


# ── choosing a target ──────────────────────────────────────────────────────
def test_the_caller_chooses_the_target_and_nothing_defaults() -> None:
    from omnex.factory.compile import compile_spec

    spec = _spec()
    assert isinstance(compile_spec(spec, Target.CODE), Graph)
    assert isinstance(compile_spec(spec, Target.MCP), str)
    assert isinstance(compile_spec(spec, Target.N8N), str)


def test_all_three_targets_agree_on_the_same_topology() -> None:
    """The question the neutral blueprint exists to make answerable.

    "Does the n8n workflow do the same thing as the code" has no meaning while
    the two artifacts share no vocabulary. Through the blueprint it is one
    equality.
    """
    blueprint = plan(_spec())
    results = [round_trip(blueprint, target) for target in Target]
    assert all(result.digest == blueprint.digest for result in results)
    assert len({result.digest for result in results}) == 1


# ── bindings: the configuration a compiler may not invent ──────────────────
def _catalogue(tmp_path: Path, payload: dict[str, object]) -> bindings.Catalogue:
    path = tmp_path / "n8n_bindings.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return bindings.load(path)


def _bound(tmp_path: Path, **overrides: object) -> bindings.Catalogue:
    """A catalogue covering the tools `_spec()` declares."""
    binding: dict[str, object] = {
        "node_type": "http",
        "credentials": {"httpHeaderAuth": "OMNEX_FX"},
        "parameters": {"method": "POST", "url": "https://fx.invalid/convert"},
    }
    binding.update(overrides)
    return _catalogue(
        tmp_path,
        {
            "node_types": {
                "http": {
                    "type": "n8n-nodes-base.httpRequest",
                    "type_version": 4.2,
                    "calls_out": True,
                }
            },
            "bindings": {"convert": dict(binding), "rates": dict(binding)},
        },
    )


@pytest.mark.parametrize("paradigm", ALL_PARADIGMS)
def test_a_bound_workflow_round_trips_exactly_like_an_unbound_one(
    paradigm: Paradigm, tmp_path: Path
) -> None:
    """Binding changes what a node IS, never what the topology SAYS.

    The property that makes these compilers is `parse(emit(bp)) == bp`. Real
    node types and real parameters are the largest change the emitter has taken,
    and if they cost the round trip they cost the only check that can see a lossy
    emission at all.
    """
    assert_round_trips(plan(_spec(paradigm)), Target.N8N, _bound(tmp_path))


def test_a_bound_step_stops_being_a_placeholder(tmp_path: Path) -> None:
    payload = json.loads(n8n.emit(plan(_spec()), _bound(tmp_path)))
    by_name = {node["name"]: node for node in payload["nodes"]}

    bound = by_name["call_convert"]
    assert bound["type"] == "n8n-nodes-base.httpRequest"
    assert bound["typeVersion"] == 4.2
    assert bound["parameters"]["url"] == "https://fx.invalid/convert"
    assert bound["credentials"] == {"httpHeaderAuth": {"name": "OMNEX_FX"}}
    assert "not confirmed by an import" in bound["notes"].lower()

    unbound = by_name["think"]
    assert unbound["type"] == "n8n-nodes-base.noOp"
    assert "Placeholder" in unbound["notes"]


def test_a_binding_cannot_shadow_the_reference_the_parser_reads_back(tmp_path: Path) -> None:
    """The subtle way a catalogue could break the round trip in silence.

    A parameter template is written by a person, and `omnexRef` is an ordinary
    key. Shadowing it would emit a workflow that imports, lays out and reads back
    as a DIFFERENT topology — the exact failure class the round trip exists for.
    """
    blueprint = plan(_spec())
    catalogue = _bound(
        tmp_path,
        parameters={"url": "https://fx.invalid/convert", "omnexRef": "something else"},
    )
    payload = json.loads(n8n.emit(blueprint, catalogue))
    node = next(n for n in payload["nodes"] if n["name"] == "call_convert")
    assert node["parameters"]["omnexRef"] == "convert"
    assert_round_trips(blueprint, Target.N8N, catalogue)


def test_an_unconfirmed_binding_is_refused_where_it_would_run_unattended(
    tmp_path: Path,
) -> None:
    """Fine to import and read; not fine to schedule against a customer's money."""
    blueprint = plan(_spec())
    catalogue = _bound(tmp_path)
    n8n.emit(blueprint, catalogue)  # building is allowed

    with pytest.raises(ValidationFailed, match="confirmed by an import") as caught:
        n8n.emit(blueprint, catalogue, require_confirmed=True)
    assert caught.value.context["unconfirmed"] == ["convert", "rates"], (
        "every unconfirmed reference must be named at once, not the first one"
    )


def test_a_binding_is_only_as_confirmed_as_the_node_type_under_it(tmp_path: Path) -> None:
    """Confirming the entry while the type beneath it is unseen confirms nothing."""
    catalogue = _catalogue(
        tmp_path,
        {
            "node_types": {
                "http": {"type": "n8n-nodes-base.httpRequest", "type_version": 4.2},
            },
            "bindings": {
                "convert": {
                    "node_type": "http",
                    "parameters": {"url": "https://fx.invalid/convert"},
                    "confirmed": True,
                    "confirmed_by": "a person",
                    "confirmed_at": "2026-09-04",
                }
            },
        },
    )
    assert catalogue.bindings["convert"].confirmed is True
    assert catalogue.is_confirmed("convert") is False


def test_a_confirmation_with_nobody_behind_it_is_refused(tmp_path: Path) -> None:
    """Machine proposes, person verifies — `nodes.json`'s rule, one level out."""
    with pytest.raises(ValidationFailed, match="confirmed_by"):
        _catalogue(
            tmp_path,
            {
                "node_types": {"http": {"type": "n8n-nodes-base.httpRequest", "type_version": 4.2}},
                "bindings": {
                    "convert": {
                        "node_type": "http",
                        "parameters": {"url": "https://fx.invalid/x"},
                        "confirmed": True,
                    }
                },
            },
        )


def test_every_catalogue_problem_is_named_at_once(tmp_path: Path) -> None:
    """Being refused one line at a time is how somebody concludes the check is the obstacle."""
    with pytest.raises(ValidationFailed) as caught:
        _catalogue(
            tmp_path,
            {
                "node_types": {"http": {"type": "no-dots-here", "type_version": 4.2}},
                "bindings": {
                    "convert": {"node_type": "ghost", "parameters": {}},
                    "rates": {"node_type": "http", "parameters": {}, "confirmed": True},
                },
            },
        )
    problems = caught.value.context["problems"]
    assert len(problems) >= 4, problems
    assert any("no-dots-here" in p for p in problems)
    assert any("ghost" in p for p in problems)
    assert any("confirmed_by" in p for p in problems)
    assert any("confirmed_at" in p for p in problems)


def test_a_credential_written_into_the_catalogue_is_refused(tmp_path: Path) -> None:
    """A binding names a credential; it never holds one."""
    with pytest.raises(ValidationFailed, match="API key prefix"):
        _catalogue(
            tmp_path,
            {
                "node_types": {"http": {"type": "n8n-nodes-base.httpRequest", "type_version": 4.2}},
                "bindings": {
                    "convert": {
                        "node_type": "http",
                        "parameters": {
                            "url": "https://fx.invalid/x",
                            "headerValue": "sk-live-9f2a4c8e1b7d",
                        },
                    }
                },
            },
        )


def test_a_secret_reaching_the_emitted_workflow_stops_it(tmp_path: Path) -> None:
    """The second failure, which the load-time scan structurally cannot see.

    The catalogue is one path into a node's parameters. A workflow JSON is
    committed and shared, so the document itself is scanned before it is
    returned — not the catalogue it was built from.
    """
    catalogue = _bound(tmp_path)
    catalogue.bindings["convert"].parameters["headerValue"] = "Bearer aGVsbG90aGVyZTEyMzQ1"
    with pytest.raises(ValidationFailed, match="bearer token"):
        n8n.emit(plan(_spec()), catalogue)


def test_a_network_node_with_no_address_must_say_why(tmp_path: Path) -> None:
    """A half-binding is legitimate; an unexplained one gets an invented url."""
    with pytest.raises(ValidationFailed, match="invents one"):
        _catalogue(
            tmp_path,
            {
                "node_types": {
                    "http": {
                        "type": "n8n-nodes-base.httpRequest",
                        "type_version": 4.2,
                        "calls_out": True,
                    }
                },
                "bindings": {"convert": {"node_type": "http", "parameters": {"method": "POST"}}},
            },
        )
    # The same entry with a note explaining the absence loads.
    catalogue = _catalogue(
        tmp_path,
        {
            "node_types": {
                "http": {
                    "type": "n8n-nodes-base.httpRequest",
                    "type_version": 4.2,
                    "calls_out": True,
                }
            },
            "bindings": {
                "convert": {
                    "node_type": "http",
                    "parameters": {"method": "POST"},
                    "note": "endpoint not readable from this environment",
                }
            },
        },
    )
    assert catalogue.bindings["convert"].parameters == {"method": "POST"}


def test_an_unbound_reference_is_reported_rather_than_raised(tmp_path: Path) -> None:
    """A part-filled catalogue is the normal state and must stay importable."""
    blueprint = plan(_spec())
    catalogue = _catalogue(
        tmp_path,
        {
            "node_types": {"noop": {"type": "n8n-nodes-base.noOp", "type_version": 1}},
            "bindings": {"convert": {"node_type": "noop", "parameters": {}}},
        },
    )
    refs = [s.ref for s in blueprint.steps]
    assert bindings.unbound_refs(refs, catalogue) == ["rates"]
    assert json.loads(n8n.emit(blueprint, catalogue))["meta"]["omnexBound"] == ["convert"]


# ── the catalogue this repository ships ────────────────────────────────────
def test_the_committed_catalogue_loads_and_claims_nothing_it_cannot_show() -> None:
    """`n8n_bindings.json` is data with a gate on it, like every other claim here."""
    catalogue = bindings.load(REPO / "engine" / "ontology" / "n8n_bindings.json")
    assert catalogue.bindings, "an empty catalogue is a checker with nothing to check"
    for ref in catalogue.bindings:
        assert not catalogue.is_confirmed(ref), (
            f"{ref} claims an import nobody in this repository performed; if that "
            "changed, this premise is stale and the count in the docstring is too"
        )
