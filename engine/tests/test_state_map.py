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


def test_no_gate_claims_a_file_is_absent_while_it_sits_in_the_repository() -> None:
    """The defect this file existed to prevent, found in this file's subject.

    Gates 1 and 2 carried hard-coded evidence — "node_dossier.py does not
    exist", "state/claims.jsonl does not exist" — written when both were true.
    Both scripts were then written, entered CI, and ran for weeks while
    `execution_state.json` went on reporting them absent, and `--check` passed
    the whole time because it compared the committed file against those same
    literals. A constant validated against itself.

    So this asserts the property rather than the two known cases: any path a
    gate names as missing must actually be missing. Keyed on paths, because a
    list of the two that already bit would stop covering whatever is added next.

    The first version of this keyed on one phrasing — `<file> does not exist` —
    and three more gates drifted past it in phrasings it could not see:
    `10_distribution` said "release_check.py and release.yml **do** not exist"
    (plural, and with the first filename two words further back than the regex
    reached) while both were in CI, and `6_security` and `9_autonomy` asserted
    absence with no filename at all. So the scan is now per clause: any clause
    that denies existence is checked against every filename in that clause.
    """
    offenders: list[str] = []
    for name, gate in state_map.derive()["gates"].items():
        for text in [str(gate["why"]), *(str(e) for e in gate["evidence"])]:
            offenders += [
                f"{name}: says {named!r} does not exist, and it does"
                for named in state_map.denied_existing_files(text)
            ]

    assert offenders == [], "; ".join(offenders)


def test_the_absence_checker_catches_the_phrasings_that_already_slipped_past_it() -> None:
    """A checker nobody has seen fail is a checker nobody has tested.

    These three strings are verbatim what gates 10, 6 and 9 actually carried
    while every file they named was in the repository and in CI. The first
    version of the scan above found nothing in any of them.
    """
    drifted = "release_check.py and release.yml do not exist; no artifact has been built"
    assert set(state_map.denied_existing_files(drifted)) == {
        "release_check.py",
        "release.yml",
    }, "the plural phrasing and the 'A and B' construction must both be seen"

    # Both original bites, including the one the first scan could never have
    # caught: `json` ordered before `jsonl` truncated this to a path that
    # resolves to nothing, so gate 2 read as clean no matter what it said.
    assert state_map.denied_existing_files("node_dossier.py does not exist") == ["node_dossier.py"]
    assert state_map.denied_existing_files("state/claims.jsonl does not exist") == [
        "state/claims.jsonl"
    ]

    # A denial naming no file cannot be path-checked; it is recognised as a
    # denial all the same, which is why gates 6 and 9 now derive instead.
    assert state_map._DENIED_INSIDE.search("no run ledger exists, so nothing follows")
    assert state_map._DENIED_INSIDE.search("no secret scanning or SBOM exists yet")

    # A file named positively is not an offence.
    assert state_map.denied_existing_files("release.yml exists and runs in CI") == []

    # And the denial must be ABOUT the file: this one denies a revenue log, and
    # the BUSINESS.md in the same sentence is not what is being called absent.
    assert (
        state_map.denied_existing_files(
            "no revenue log exists — 0 recorded is not 0 earned, and BUSINESS.md "
            "refuses to render it as a measurement"
        )
        == []
    )


def test_the_repaired_gates_derive_their_evidence_rather_than_stating_it() -> None:
    """The fix, held in place. Each gate must move when the repository moves,
    so its evidence has to contain a measured quantity — not a sentence that
    happened to be true on the day somebody typed it."""
    gates = state_map.derive()["gates"]

    architecture = " ".join(str(e) for e in gates["1_architecture"]["evidence"])
    assert "node_dossier.py exists: True" in architecture
    assert "ruled on by a person: 0" in architecture, "only apply_decisions.py may raise this"

    evidence = " ".join(str(e) for e in gates["2_evidence"]["evidence"])
    assert "claims registry present: True" in evidence
    assert "SUPPORTED" in evidence, "the derived status counts, recomputed not stored"

    security = " ".join(str(e) for e in gates["6_security"]["evidence"])
    assert "dependency_audit_in_ci: True" in security, "npm audit runs in ci.yml"
    assert "sbom_generated: True" in security, "release.yml now generates and reads back an SBOM"
    assert "dependency_review_in_ci: True" in security, "dependency-review-action runs on PRs"

    supply = state_map.derive()["supply_chain"]
    assert supply["actions_pinned_to_sha"] == supply["actions_total"] > 0, (
        "every GitHub Action this repository runs must be pinned to a commit SHA"
    )

    autonomy = " ".join(str(e) for e in gates["9_autonomy"]["evidence"])
    assert "chain intact: True" in autonomy
    assert "runs recorded: 0" not in autonomy, "the ledger is not empty"

    distribution = " ".join(str(e) for e in gates["10_distribution"]["evidence"])
    assert "release_check.py present: True" in distribution
    assert "release.yml present: True" in distribution

    implementation = " ".join(str(e) for e in gates["3_implementation"]["evidence"])
    assert "capability registry" in implementation
    assert "E4_INTEGRATED" in implementation or "E3_TESTED" in implementation


def test_gate_3_never_claims_more_capabilities_than_the_registry_holds() -> None:
    """Gate 3 used to say 'no capability registry' as a literal. Once one
    exists, the gate must move WITH it, not past it -- claiming coverage the
    registry itself does not carry would be the same defect one level up."""
    import capability_map

    state = state_map.derive()
    gate_evidence = " ".join(str(e) for e in state["gates"]["3_implementation"]["evidence"])
    real_total = capability_map.summarise(capability_map.derive_all())["total"]
    assert str(real_total) in gate_evidence
