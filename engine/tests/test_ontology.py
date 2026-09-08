"""The coverage map, held to the standard it claims to apply.

`ontology/branches.json` says which branches are already backed by code, and
where each branch came from. That claim decays silently: rename
`omnex.memory.LongTermMemory`
and the map still reads "Agent Memory -> implemented", now describing a
repository that no longer exists. Nobody re-reads a coverage document to check
it, which is exactly why it needs a test rather than a review.

So the load-bearing test here is `test_every_claimed_symbol_still_resolves`. It
is the reason the map cannot rot: a refactor that moves a symbol turns CI red in
the same run that moved it, while the claim is still fresh in somebody's head.

The last test in the file deliberately builds a lying branch and asserts the
audit catches it. A guard nobody has seen fail is a guard nobody knows is wired
up — and that check is cheaper to keep here than to remember to run by hand.
"""

from __future__ import annotations

import json

import pytest
from ontology_map import (
    CLAIMS,
    PRODUCERS,
    ROOT,
    SOURCE,
    WORTH_IT_KEYS,
    Branch,
    audit,
    load,
    render,
    resolve,
)

BRANCHES = load()
EXPECTED_BRANCH_COUNT = 38


def test_the_ontology_has_every_branch_exactly_once() -> None:
    ids = [branch.id for branch in BRANCHES]
    assert len(ids) == EXPECTED_BRANCH_COUNT
    assert len(set(ids)) == len(ids), "a duplicated branch id would hide one of the two"


@pytest.mark.parametrize("branch", BRANCHES, ids=lambda b: b.id)
def test_every_claimed_symbol_still_resolves(branch: Branch) -> None:
    """The one that stops the map becoming a document about the past."""
    unresolved = [(symbol, resolve(symbol)) for symbol in branch.symbols]
    broken = [f"{symbol}: {reason}" for symbol, reason in unresolved if reason is not None]
    assert not broken, f"{branch.id} cites symbols that no longer exist: {broken}"


@pytest.mark.parametrize("branch", BRANCHES, ids=lambda b: b.id)
def test_every_claimed_test_file_is_on_disk(branch: Branch) -> None:
    absent = [path for path in branch.tests if not (ROOT / path).exists()]
    assert not absent, f"{branch.id} cites test files that do not exist: {absent}"


@pytest.mark.parametrize("branch", BRANCHES, ids=lambda b: b.id)
def test_no_branch_survives_a_rule_it_breaks(branch: Branch) -> None:
    """Structural rules, not a score — see `_rule_violations`."""
    result = audit(branch)
    assert not result.violations, f"{branch.id}: {result.violations}"


def test_implemented_is_the_only_claim_that_costs_something() -> None:
    """`implemented` must be paid for in symbols and tests, or it means nothing."""
    for branch in BRANCHES:
        if branch.claim != "implemented":
            continue
        assert branch.symbols, f"{branch.id} claims implemented with nothing to import"
        assert branch.tests, f"{branch.id} claims implemented with nothing to run"
        assert not branch.missing, f"{branch.id} claims implemented and lists missing work"


def test_anything_left_to_build_answers_all_seven_conditions() -> None:
    """Mirrors `evaluate()`, which has no defaults on purpose.

    A default here would be a quiet assumption about somebody else's budget, and
    the condition that would default to True — "the budget absorbs the waste" —
    is the one worth thinking about.
    """
    for branch in BRANCHES:
        if not branch.missing:
            assert branch.worth_it is None, f"{branch.id} has a verdict but nothing left to do"
            continue
        assert branch.worth_it is not None, f"{branch.id} has missing work and no verdict"
        assert set(branch.worth_it) == set(WORTH_IT_KEYS), (
            f"{branch.id} must answer exactly the seven conditions"
        )
        for key, answer in branch.worth_it.items():
            assert isinstance(answer, bool), f"{branch.id}.{key} must be a bool, not {answer!r}"


def test_no_figure_is_ever_typed_into_the_ontology() -> None:
    """A branch cites the producer of its number, never the number.

    A literal here is correct until the next run on a different machine, and
    then wrong for as long as nobody re-reads it. `measured_by` points at the
    script or the committed leaderboard instead, which is the same rule
    `skill_numbers.py` exists to enforce for the skills.
    """
    for branch in BRANCHES:
        if branch.measured_by is None:
            continue
        assert branch.measured_by in PRODUCERS, f"{branch.id} cites an unknown producer"
        assert (ROOT / branch.measured_by).exists(), f"{branch.id} cites a producer that is gone"


def test_every_claim_is_one_of_the_four() -> None:
    for branch in BRANCHES:
        assert branch.claim in CLAIMS
        assert branch.note.strip(), f"{branch.id} has no note explaining its claim"


def test_the_rendered_map_says_a_refusal_is_not_a_prohibition() -> None:
    """The verdict gates loops, and the document must not let that be misread.

    `worth_it` refuses long-running loops. Rendered without that qualification,
    "NOT worth it" reads as "this should not be built", which is a different and
    much larger claim than the gate makes.
    """
    page = render([audit(branch) for branch in BRANCHES])
    assert "gates **loops**" in page
    assert "does not" in page and "worth doing by hand" in page


def test_the_committed_map_matches_what_the_script_renders_now() -> None:
    """A generated file that drifts from its generator is worse than no file."""
    committed = (ROOT / "ontology" / "COVERAGE.md").read_text(encoding="utf-8")
    assert committed == render([audit(branch) for branch in BRANCHES]), (
        "COVERAGE.md is stale — re-run `python scripts/ontology_map.py`"
    )


def test_the_source_file_is_valid_json_with_a_version() -> None:
    raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert raw["ontology_version"] == "2"
    assert len(raw["branches"]) == EXPECTED_BRANCH_COUNT


def test_a_branch_that_lies_about_its_code_is_caught() -> None:
    """The guard, observed failing.

    Without this, `test_every_claimed_symbol_still_resolves` passing tells you
    the claims are true OR that the resolver quietly returns None for everything.
    """
    liar = Branch(
        id="FAKE-1",
        name="Fabricated",
        claim="implemented",
        modules=["omnex.memory"],
        symbols=["omnex.memory.NoSuchThing"],
        tests=["tests/test_memory.py"],
        measured_by=None,
        missing=[],
        note="claims a symbol that was never written",
        worth_it=None,
        source="proposal",
    )
    result = audit(liar)
    assert not result.ok
    assert any("NoSuchThing" in entry for entry in result.unresolved)


def test_a_branch_that_hides_work_behind_implemented_is_caught() -> None:
    hider = Branch(
        id="FAKE-2",
        name="Fabricated",
        claim="implemented",
        modules=["omnex.memory"],
        symbols=["omnex.memory.LongTermMemory"],
        tests=["tests/test_memory.py"],
        measured_by=None,
        missing=["the half that was never built"],
        note="claims completeness while naming what is absent",
        worth_it=None,
        source="proposal",
    )
    result = audit(hider)
    assert not result.ok
    assert any("implemented" in entry for entry in result.violations)


def test_a_branch_that_will_not_say_where_it_came_from_is_caught() -> None:
    """`source` is load-bearing, so an unset one has to fail rather than default.

    A branch with no provenance defaults, in a reader's head, to "somebody
    checked" — which is the assumption version 2 exists to remove.
    """
    anonymous = Branch(
        id="FAKE-3",
        name="Fabricated",
        claim="knowledge",
        modules=[],
        symbols=[],
        tests=[],
        measured_by=None,
        missing=[],
        note="does not say where it came from",
        worth_it=None,
        source="somebody said so",
    )
    result = audit(anonymous)
    assert not result.ok
    assert any("came from" in entry for entry in result.violations)


def test_every_branch_says_where_it_came_from() -> None:
    for branch in BRANCHES:
        assert branch.source.startswith(("proposal", "corpus:")), branch.id


def test_the_ontology_contains_branches_nobody_proposed() -> None:
    """The point of version 2.

    A map built only from a proposal can confirm or refute every entry on it and
    cannot discover the entry nobody wrote down. If this ever drops to zero, the
    ontology has stopped being read out of sources and gone back to being a list.
    """
    derived = [b for b in BRANCHES if b.derived]
    assert derived, "no branch was discovered from a corpus"
    assert all(b.source.startswith("corpus:") for b in derived)
    # Discovered branches are gaps or partials by nature — code cannot already
    # implement something nobody had named.
    assert all(b.claim in ("gap", "partial") for b in derived)
