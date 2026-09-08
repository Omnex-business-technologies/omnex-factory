"""The registry, and proof each predicate in it can fail.

`invariant_map.py` reporting six green checkers is worth exactly as much as the
demonstration that a checker goes red when the rule is broken. Every other
"can this actually fail" pattern in this repository exists because the answer
was once no — the compiler round trip compared an artifact with itself, and the
first concurrency test passed against an unguarded ledger.

So each checker here is pointed at a synthetic tree containing the violation it
is meant to catch. If it stays silent, it was never doing anything.

## The registry's own rules

An entry with no checker and no stated reason fails the script. That is the
mechanism that keeps `invariants.json` from becoming a second copy of CLAUDE.md
— a list of intentions that renders and enforces nothing, which is the state
this whole exercise was built to leave. `test_a_rule_with_neither_a_checker_nor_
a_reason_is_refused` is that mechanism under test.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import invariants
import pytest
from invariant_map import audit_registry, render, run
from invariants import load_registry


@pytest.fixture
def tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A throwaway source tree the checkers scan instead of the real one."""
    src = tmp_path / "engine" / "src" / "omnex"
    src.mkdir(parents=True)
    monkeypatch.setattr(invariants, "REPO", tmp_path)
    monkeypatch.setattr(invariants, "SRC", src)
    monkeypatch.setattr(invariants, "TESTS", tmp_path / "engine" / "tests")
    monkeypatch.setattr(invariants, "SCRIPTS", tmp_path / "engine" / "scripts")
    return src


# ── the real tree is clean ────────────────────────────────────────────────
def test_every_checker_passes_on_this_repository() -> None:
    """Through `run()`, so each checker sees the allowlist the registry gives it.

    Calling the checkers bare would test a stricter rule than the one that is
    actually in force, and a test that disagrees with the gate is a test people
    delete.
    """
    for ident, found in run(load_registry()).items():
        assert found == [], f"{ident}: " + "; ".join(str(v) for v in found)


def test_the_registry_survives_its_own_rules() -> None:
    assert audit_registry(load_registry()) == []


# ── each checker can fail ─────────────────────────────────────────────────
def test_a_float_over_money_is_caught(tree: Path) -> None:
    """The exact shape that had come back: `float(span.cost.picos)`."""
    (tree / "billing.py").write_text(
        "def record(span, counter):\n    counter.inc(float(span.cost.picos))\n",
        encoding="utf-8",
    )
    found = invariants.money_never_float()
    assert len(found) == 1
    assert "picos" in found[0].detail


def test_an_infinity_or_a_ratio_is_not_mistaken_for_money(tree: Path) -> None:
    """Why this is an AST pass and not a grep.

    `float("inf")` for an unreachable payback and `float(hits)/total` in a
    scorer are correct code, and a checker that flags them is one somebody
    switches off.
    """
    (tree / "fine.py").write_text(
        'def f(hits, total):\n    return float("inf") if not total else float(hits) / total\n',
        encoding="utf-8",
    )
    assert invariants.money_never_float() == []


def test_a_direct_clock_read_is_caught(tree: Path) -> None:
    (tree / "late.py").write_text(
        "import time\n\n\ndef go():\n    return time.monotonic()\n", encoding="utf-8"
    )
    found = invariants.clock_is_injected()
    assert len(found) == 1 and "late.py" in found[0].where


def test_a_clock_read_with_an_argument_is_caught(tree: Path) -> None:
    """`datetime.now(UTC)` is the form a hand-written grep for `now()` misses.

    It did: the audit that produced this file used a regex with empty
    parentheses and under-reported by two files. The checker found them the
    first time it ran, which is the whole argument for having one.
    """
    (tree / "stamp.py").write_text(
        "from datetime import UTC, datetime\n\n\ndef at():\n    return datetime.now(UTC)\n",
        encoding="utf-8",
    )
    assert len(invariants.clock_is_injected()) == 1


def test_prose_about_the_clock_is_not_a_clock_read(tree: Path) -> None:
    """A checker that fires on its own fix notice is one people learn to ignore."""
    (tree / "documented.py").write_text(
        '"""It used to call time.monotonic() directly, and no longer does."""\n\n\n'
        "def go() -> int:\n    return 1\n",
        encoding="utf-8",
    )
    assert invariants.clock_is_injected() == []


def test_the_allowlist_silences_only_what_it_names(tree: Path) -> None:
    (tree / "excused.py").write_text(
        "import time\n\n\ndef go():\n    return time.time()\n", encoding="utf-8"
    )
    (tree / "not_excused.py").write_text(
        "import time\n\n\ndef go():\n    return time.time()\n", encoding="utf-8"
    )
    allowed = "engine/src/omnex/excused.py"
    found = invariants.clock_is_injected((allowed,))
    assert len(found) == 1
    assert "not_excused.py" in found[0].where


def test_an_ordered_strenum_missing_its_operators_is_caught(tree: Path) -> None:
    (tree / "stage.py").write_text(
        "from enum import StrEnum\n\n\n"
        "class Phase(StrEnum):\n    ONE = 'one'\n    TWO = 'two'\n\n\n"
        "def before(a, b):\n    return Phase.ONE < Phase.TWO\n",
        encoding="utf-8",
    )
    found = invariants.ordered_strenum_defines_all_comparisons()
    assert len(found) == 1 and found[0].where == "Phase"


def test_a_strenum_nobody_orders_is_left_alone(tree: Path) -> None:
    """Most StrEnums here are labels. Requiring operators on all of them is noise."""
    (tree / "kind.py").write_text(
        "from enum import StrEnum\n\n\nclass Kind(StrEnum):\n    A = 'a'\n    B = 'b'\n",
        encoding="utf-8",
    )
    assert invariants.ordered_strenum_defines_all_comparisons() == []


def test_a_second_resolver_is_caught(tree: Path) -> None:
    (tree / "copy.py").write_text(
        "def resolve(symbol: str) -> str | None:\n    return None\n", encoding="utf-8"
    )
    found = invariants.one_symbol_resolver()
    assert len(found) == 1 and "copy.py" in found[0].where


def test_a_required_dependency_is_caught(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = tmp_path / "engine"
    engine.mkdir()
    (engine / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = ["requests>=2"]\n', encoding="utf-8"
    )
    monkeypatch.setattr(invariants, "ENGINE", engine)
    monkeypatch.setattr(invariants, "REPO", tmp_path)
    found = invariants.no_required_dependencies()
    assert len(found) == 1 and "requests" in found[0].detail


def test_a_diverged_twin_is_caught(monkeypatch: pytest.MonkeyPatch) -> None:
    """The abbreviation drift, reproduced through the checker rather than described."""
    from omnex.rag import ingest

    monkeypatch.setattr(ingest, "_ABBREVIATIONS", ingest._ABBREVIATIONS - {"dr."})
    found = invariants.twin_splitters_agree()
    assert len(found) == 1
    assert "abbreviation sets differ" in found[0].detail


# ── the registry polices itself ───────────────────────────────────────────
def _entry(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": "sample",
        "rule": "a rule",
        "paid_for": "a real failure",
        "checker": "money_never_float",
        "allowlist": [],
    }
    base.update(overrides)
    return base


def test_a_rule_with_neither_a_checker_nor_a_reason_is_refused() -> None:
    """The mechanism. Without it this file is CLAUDE.md with syntax highlighting."""
    problems = audit_registry([_entry(checker=None)])
    assert any("no checker and no stated reason" in p for p in problems)


def test_a_rule_declared_unenforceable_with_a_reason_is_accepted() -> None:
    assert audit_registry([_entry(checker=None, unenforceable="prose cannot be measured")]) == []


def test_a_rule_cannot_be_unenforceable_and_enforced_at_once() -> None:
    problems = audit_registry([_entry(unenforceable="but also this")])
    assert any("claims to be unenforceable" in p for p in problems)


def test_a_checker_that_does_not_exist_is_refused() -> None:
    problems = audit_registry([_entry(checker="wishful_thinking")])
    assert any("does not exist" in p for p in problems)


def test_a_rule_nobody_can_point_at_a_failure_for_is_refused() -> None:
    """A rule with no `paid_for` is a preference, and preferences are not gates."""
    problems = audit_registry([_entry(paid_for="  ")])
    assert any("paid_for" in p for p in problems)


def test_an_exception_without_a_reason_is_refused() -> None:
    problems = audit_registry([_entry(allowlist=[{"path": "engine/pyproject.toml", "reason": ""}])])
    assert any("no reason" in p for p in problems)


def test_an_exception_for_a_file_that_is_gone_is_refused() -> None:
    problems = audit_registry(
        [_entry(allowlist=[{"path": "engine/src/omnex/deleted.py", "reason": "stale"}])]
    )
    assert any("which is gone" in p for p in problems)


def test_two_entries_cannot_share_an_id() -> None:
    assert any("listed twice" in p for p in audit_registry([_entry(), _entry()]))


# ── the document points at its own enforcement ────────────────────────────
def test_claude_md_names_the_invariant_that_backs_each_rule() -> None:
    """The link between the prose and the predicate, in both directions.

    Every id in the registry must appear in CLAUDE.md, and every id CLAUDE.md
    cites must exist in the registry. Without this the two drift the way the
    documented gate and CI drifted, and a reader cannot tell which rules are
    checked and which are hopes.
    """
    text = (invariants.REPO / "CLAUDE.md").read_text(encoding="utf-8")
    ids = {str(entry["id"]) for entry in load_registry()}
    missing = sorted(ident for ident in ids if f"`{ident}`" not in text)
    assert not missing, f"CLAUDE.md does not cite: {missing}"


def test_the_rendered_map_reports_the_unenforceable_rather_than_hiding_them() -> None:
    """Dropping them would make the enforced count look better than the repo is."""
    entries = load_registry()
    page = render(entries, run(entries))
    assert "## Declared unenforceable" in page
    for entry in entries:
        if not entry.get("checker"):
            assert str(entry["id"]) in page


# ── the business rule ─────────────────────────────────────────────────────
def test_nothing_is_live_so_nothing_is_violated_today() -> None:
    """Honest state, not a passing grade.

    Every offer in `packs/listing.json` is `live: false`, so the gate is green
    while the Complete Vault still promises 170 images against 80 that passed
    QC. `packs/listing_check.py` reports that shortfall regardless — the report
    tells you what is missing, the gate stops you selling a lie.
    """
    assert invariants.live_listings_are_covered() == []

    checker = invariants.REPO / "packs" / "listing_check.py"
    if not checker.exists():
        pytest.skip("packs/ is not in this checkout")
    module = invariants._load(checker, "packs_listing_check_test")
    shortfalls, _ = module.audit(module.load_listing(), invariants.REPO / "packs")
    assert shortfalls, "the shortfall vanished — regenerate this test's premise"


def test_a_live_listing_that_is_short_is_refused(tmp_path: Path) -> None:
    """The gate bites the moment somebody publishes, and not before.

    Scoped to live offers on purpose: "you must have 170 images" would be red
    until the day they exist, and a permanently red build is one people learn to
    ignore — the exact failure this registry was built against. Proving it fires
    therefore needs a directory where something IS live and short, rather than
    publishing something to find out.
    """
    if not (invariants.REPO / "packs" / "listing_check.py").exists():
        pytest.skip("packs/ is not in this checkout")

    (tmp_path / "alpha").mkdir()
    (tmp_path / "alpha" / "manifest.json").write_text(
        json.dumps({"images": [{"file": "a.png"}]}), encoding="utf-8"
    )
    (tmp_path / "LICENSE.txt").write_text("licence", encoding="utf-8")
    (tmp_path / "listing.json").write_text(
        json.dumps(
            {
                "licence_file": "LICENSE.txt",
                "packs": {
                    "alpha": {
                        "listing_name": "Alpha Pack",
                        "promised_images": 40,
                        "live": True,
                    },
                    "beta": {
                        "listing_name": "Beta Pack",
                        "promised_images": 40,
                        "live": False,
                    },
                },
                "bundles": {},
            }
        ),
        encoding="utf-8",
    )

    found = invariants.live_listings_are_covered(tmp_path)
    assert len(found) == 1, "the offer that is not live was counted, or the live one was not"
    assert "Alpha Pack" in found[0].detail
    assert "39 short" in found[0].detail
