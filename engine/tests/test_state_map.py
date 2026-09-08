"""Machine state that can lie is worse than none.

`execution_state.json` is the most dangerous artifact in this repository, because
it is the one thing an agent reads *instead of looking*. If its numbers live
apart from the code they describe it becomes a second copy of the truth — and
unlike prose, it drifts authoritatively.

So the tests here are mostly about the two ways it could stop being derived: a
field the file carries and the repository does not produce, and a field the
repository produces and the file has not caught up with. Plus the one that makes
the whole thing possible: running the generator twice must produce the same
bytes, which is why there is no timestamp in it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ENGINE = REPO / "engine"
sys.path.insert(0, str(ENGINE / "scripts"))

import state_map  # noqa: E402


def _committed() -> dict[str, object]:
    return json.loads((REPO / "execution_state.json").read_text(encoding="utf-8"))


# ── the file is derived, and provably so ──────────────────────────────────
def test_the_committed_state_agrees_with_the_repository() -> None:
    """The whole point. If this fails, regenerate — never edit the file."""
    drop = {"source_commit", "branch", "tree_clean"}
    committed = {k: v for k, v in _committed().items() if k not in drop}
    measured = {k: v for k, v in state_map.derive().items() if k not in drop}
    assert state_map.differences(committed, measured) == []


def test_drift_is_caught_in_both_directions() -> None:
    """A stale file and a file ahead of the code are different failures."""
    behind = state_map.differences({"a": 1}, {"a": 1, "b": 2})
    assert behind == ["state.b is measured and not in the file"]

    ahead = state_map.differences({"a": 1, "ghost": 3}, {"a": 1})
    assert ahead == ["state.ghost is in the file and not measured"]

    changed = state_map.differences({"a": 1}, {"a": 2})
    assert changed == ["state.a: file says 1, repository says 2"]


def test_drift_is_found_at_any_depth() -> None:
    """A count nested three levels down is exactly where a lie would hide."""
    problems = state_map.differences(
        {"nodes": {"by_claim": {"gap": 461}}},
        {"nodes": {"by_claim": {"gap": 460}}},
    )
    assert problems == ["state.nodes.by_claim.gap: file says 461, repository says 460"]


def test_generating_twice_produces_the_same_state() -> None:
    """No timestamp, on purpose.

    A generation time would change on every run, so the file would differ from
    itself and `--check` would have to learn to ignore a field. Once a validator
    ignores one field it can be taught to ignore another.
    """
    first = state_map.derive()
    second = state_map.derive()
    assert first == second
    assert "generated_at" not in first
    assert first["source_commit"], "state must be keyed on something that identifies the tree"


# ── UNKNOWN is not FALSE ──────────────────────────────────────────────────
def test_an_unmeasured_gate_is_unknown_and_never_false() -> None:
    """`false` is a claim that the gate fails; UNKNOWN is the honest state.

    Most gates need evidence this process cannot produce — a deployment, a user,
    a payment. Rendering those as failures would be as wrong as rendering them
    as passes.
    """
    for name, gate in state_map.derive()["gates"].items():
        assert gate["status"] in {state_map.PASS, state_map.FAIL, state_map.UNKNOWN}, name
        assert gate["status"] is not False, name


def test_every_unknown_gate_says_which_evidence_it_waits_for() -> None:
    """UNKNOWN with no reason is indistinguishable from nobody having looked."""
    thin = [
        name
        for name, gate in state_map.derive()["gates"].items()
        if gate["status"] == state_map.UNKNOWN and len(str(gate["why"])) < 40
    ]
    assert thin == [], thin


def test_integrity_is_the_only_gate_a_repository_scan_can_decide() -> None:
    """Gate 0 is measurable here; claiming any other would be overreach."""
    gates = state_map.derive()["gates"]
    assert gates["0_integrity"]["status"] == state_map.PASS
    decided = [n for n, g in gates.items() if g["status"] != state_map.UNKNOWN]
    assert decided == ["0_integrity"], decided


def test_integrity_fails_when_a_declared_licence_is_missing() -> None:
    """Proof gate 0 can fail — it was failing until this session.

    Both pyproject files declared MIT and no LICENSE file existed anywhere.
    """
    facts = state_map.derive()
    facts["promise_integrity"]["licences"]["LICENSE"] = False
    assert state_map.gates(facts)["0_integrity"]["status"] == state_map.FAIL
    assert any("LICENSE is missing" in e for e in state_map.gates(facts)["0_integrity"]["evidence"])


def test_integrity_fails_on_a_promise_with_nothing_behind_it() -> None:
    facts = state_map.derive()
    facts["extras"]["problems"] = 2
    assert state_map.gates(facts)["0_integrity"]["status"] == state_map.FAIL


# ── the number a machine may not raise ────────────────────────────────────
def test_the_human_decision_count_is_read_and_never_computed() -> None:
    """It comes from `verified` in nodes.json, which only a person's decision sets.

    Zero is the correct value today, and it is the number the whole node map
    exists to move. A machine that could raise it would make it meaningless.
    """
    assert state_map.derive()["nodes"]["verified_by_a_person"] == 0

    source = (ENGINE / "scripts" / "state_map.py").read_text(encoding="utf-8")
    assert "verified" in source
    for forbidden in ("verified = True", '"verified": True', "node['verified'] ="):
        assert forbidden not in source, "state_map must read the flag, never set it"


# ── what is blocked stays visible ─────────────────────────────────────────
def test_every_blocker_names_a_resolution() -> None:
    """A blocker with no way out is a complaint, not a state."""
    blocked = state_map.derive()["blocked"]
    assert len(blocked) >= 4
    for item in blocked:
        assert item["what"] and item["reason"] and item["resolution"], item
        assert len(item["resolution"]) > 15, item


def test_the_corpus_numbers_are_the_ones_the_ontology_carries() -> None:
    state = state_map.derive()
    assert state["corpus"] == {"figures": 509, "nodes": 507}
    assert state["nodes"]["total"] == 507
    assert sum(state["nodes"]["by_claim"].values()) == 507


def test_the_state_names_its_own_generator_and_forbids_editing() -> None:
    note = str(_committed()["$comment"])
    assert "state_map.py" in note
    assert "Do not edit" in note
