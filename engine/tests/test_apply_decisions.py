"""The one script allowed to set `verified`, and the five ways it refuses.

`0 implemented` is worth reading precisely because no machine can raise it. This
is the only thing in the repository that may, so almost every test here is a
refusal — the value of the number is entirely in what cannot produce it.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ENGINE = REPO / "engine"
sys.path.insert(0, str(ENGINE / "scripts"))

import apply_decisions  # noqa: E402
from node_map import Node  # noqa: E402

TODAY = date(2026, 9, 8)


def _nodes() -> list[Node]:
    return [
        Node(
            branch="XII", name="MCP", claim="proposed", alias="omnex.mcp.McpClient", verified=False
        ),
        Node(
            branch="I", name="Ghost", claim="proposed", alias="omnex.nope.Missing", verified=False
        ),
        Node(branch="I", name="Bare", claim="gap", alias=None, verified=False),
    ]


def _ruling(**over: object) -> apply_decisions.Ruling:
    base: dict[str, object] = {
        "branch": "XII",
        "node": "MCP",
        "decision": "implemented",
        "reviewer": "RaveZona",
        "when": "2026-09-08",
    }
    base.update(over)
    return apply_decisions.Ruling(**base)  # type: ignore[arg-type]


def _refused(
    ruling: apply_decisions.Ruling, nodes: list[Node] | None = None, **kw: object
) -> list[str]:
    return apply_decisions.refusals([ruling], nodes or _nodes(), today=TODAY, **kw)  # type: ignore[arg-type]


# ── the five refusals ─────────────────────────────────────────────────────
def test_a_decision_with_no_reviewer_is_refused() -> None:
    """An anonymous confirmation is indistinguishable from a generated one."""
    problems = _refused(_ruling(reviewer=""))
    assert any("no reviewer" in p for p in problems)


@pytest.mark.parametrize("name", ["claude", "Claude", "  BOT ", "agent", "system", "n/a", "TBD"])
def test_a_machine_shaped_reviewer_is_refused(name: str) -> None:
    """The rule this script exists to hold, at the line that would defeat it.

    A machine that can write a reviewer field can confirm its own proposal, and
    then `0 implemented` stops meaning anything.
    """
    problems = _refused(_ruling(reviewer=name))
    assert any("is not a person" in p for p in problems)
    assert any("fuller identifying one" in p for p in problems), (
        "the refusal must say how a person actually called that proceeds"
    )


def test_implemented_for_an_alias_that_does_not_import_is_refused() -> None:
    """ "This symbol IS this capability" cannot be said about a symbol that is absent."""
    problems = _refused(_ruling(branch="I", node="Ghost"))
    assert any("does not import" in p for p in problems)


def test_implemented_with_no_alias_at_all_is_refused() -> None:
    problems = _refused(_ruling(branch="I", node="Bare"))
    assert any("no symbol to agree about" in p for p in problems)


def test_overturning_a_confirmed_decision_needs_an_explicit_revision() -> None:
    """A decision that can be quietly reversed is not a decision."""
    nodes = _nodes()
    nodes[0].verified = True
    nodes[0].note = "rejected by Someone Else on 2026-09-01"

    problems = _refused(_ruling(), nodes)
    assert any("immutable" in p and "Someone Else" in p for p in problems)

    # With --revise, it still needs a reason for overturning them.
    assert any("needs a reason" in p for p in _refused(_ruling(), nodes, revising=True))
    assert _refused(_ruling(reason="the symbol was renamed"), nodes, revising=True) == []


@pytest.mark.parametrize(
    ("when", "fragment"),
    [("", "no date"), ("08-09-2026", "not YYYY-MM-DD"), ("2027-01-01", "in the future")],
)
def test_a_bad_date_is_refused(when: str, fragment: str) -> None:
    """Injected clock, so "in the future" is testable without waiting."""
    assert any(fragment in p for p in _refused(_ruling(when=when)))


def test_an_unknown_decision_word_is_refused() -> None:
    assert any("is not one of" in p for p in _refused(_ruling(decision="looks-fine")))


def test_a_ruling_for_a_node_that_does_not_exist_is_refused() -> None:
    assert any("no such node" in p for p in _refused(_ruling(branch="ZZ", node="Invented")))


def test_every_refusal_is_reported_at_once() -> None:
    """Being refused one row at a time is how somebody concludes the queue is the obstacle."""
    problems = apply_decisions.refusals(
        [
            _ruling(reviewer=""),
            _ruling(branch="I", node="Ghost", when="nope"),
            _ruling(branch="ZZ", node="Invented"),
        ],
        _nodes(),
        today=TODAY,
    )
    assert len(problems) >= 4, problems


# ── what it writes when nothing is refused ────────────────────────────────
def test_a_clean_ruling_confirms_the_node_with_its_provenance() -> None:
    nodes = _nodes()
    assert _refused(_ruling(), nodes) == []
    apply_decisions.apply([_ruling()], nodes)

    node = nodes[0]
    assert node.claim == "implemented"
    assert node.verified is True
    assert node.note == "implemented by RaveZona on 2026-09-08"


def test_deferring_records_the_look_and_confirms_nothing() -> None:
    """Deferring is the opposite of confirming; collapsing them inflates the count."""
    nodes = _nodes()
    ruling = _ruling(decision="deferred", reason="needs the branch read first")
    assert _refused(ruling, nodes) == []
    apply_decisions.apply([ruling], nodes)

    assert nodes[0].verified is False
    assert nodes[0].claim == "proposed", "a deferral must not change the claim"
    assert "deferred by RaveZona" in nodes[0].note


def test_a_revision_keeps_what_it_overturned() -> None:
    """A revision that erased its predecessor would hide that anybody disagreed."""
    nodes = _nodes()
    nodes[0].verified = True
    nodes[0].note = "rejected by Someone Else on 2026-09-01"
    apply_decisions.apply([_ruling(reason="the symbol was renamed")], nodes)

    assert "implemented by RaveZona" in nodes[0].note
    assert "was: rejected by Someone Else on 2026-09-01" in nodes[0].note


def test_provenance_round_trips() -> None:
    """The note is the record; if it cannot be read back it is not a record."""
    ruling = _ruling(reason="checked the transport by hand")
    read = apply_decisions.existing(ruling.note())
    assert read is not None
    assert (read.decision, read.reviewer, read.when, read.reason) == (
        "implemented",
        "RaveZona",
        "2026-09-08",
        "checked the transport by hand",
    )


def test_a_note_that_is_not_a_decision_reads_as_none() -> None:
    assert apply_decisions.existing("") is None
    assert apply_decisions.existing("some earlier remark about this node") is None


# ── the queue as it actually is ───────────────────────────────────────────
def test_the_committed_queue_carries_no_rulings() -> None:
    """507 rows waiting for a person, and nothing here may fill one in.

    If this ever fails, somebody ruled — which is the point. Update the premise
    then, deliberately.
    """
    queue = (REPO / "corpus" / "universal-ai-os" / "DECISIONS.md").read_text(encoding="utf-8")
    assert apply_decisions.read_queue(queue) == []


def test_a_filled_row_is_read_back_exactly() -> None:
    """Proof the parser can see a ruling; otherwise the test above is vacuous."""
    row = (
        "| XII | MCP | PROPOSED | 62 | 43 | fig_0047 | `omnex.mcp.McpClient` | "
        "confirm-or-reject | MEDIUM | implemented | RaveZona | 2026-09-08 |"
    )
    rulings = apply_decisions.read_queue(row)
    assert len(rulings) == 1
    assert (rulings[0].branch, rulings[0].node) == ("XII", "MCP")
    assert (rulings[0].decision, rulings[0].reviewer, rulings[0].when) == (
        "implemented",
        "RaveZona",
        "2026-09-08",
    )


def test_a_half_filled_row_is_still_read_and_then_refused() -> None:
    """A reviewer with no decision is a mistake, not an empty row to skip past."""
    row = (
        "| XII | MCP | PROPOSED | 62 | 43 | — | `x` | confirm-or-reject | MEDIUM |  | RaveZona |  |"
    )
    rulings = apply_decisions.read_queue(row)
    assert len(rulings) == 1
    problems = apply_decisions.refusals(rulings, _nodes(), today=TODAY)
    assert any("is not one of" in p for p in problems)
    assert any("no date" in p for p in problems)


def test_the_resolver_is_the_shared_one() -> None:
    """`one_symbol_resolver` — a second import check here would drift."""
    source = (ENGINE / "scripts" / "apply_decisions.py").read_text(encoding="utf-8")
    assert "from omnex.core.symbols import resolve" in source
    assert "importlib" not in source, "a private import check is a second resolver"
