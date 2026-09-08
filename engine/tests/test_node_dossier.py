"""507 dossiers, and the decision none of them makes.

`nodes.json` has recorded `0 implemented` and `0 rejected` since it was written.
That is not neglect: moving either number means opening a branch, reading what it
exports, deciding whether a symbol is the capability, and doing it 507 times.
Nobody does an investigation 507 times, so the number never moved.

This turns each of those investigations into a row somebody can read. The tests
here are mostly about the boundary that makes the row worth reading — the machine
gathers and ranks, and decides nothing.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ENGINE = REPO / "engine"
sys.path.insert(0, str(ENGINE / "scripts"))

import node_dossier  # noqa: E402
from ingest_atlas import EXPORT, parse  # noqa: E402
from link_nodes import link  # noqa: E402
from node_map import Node, load, public_symbols  # noqa: E402

QUEUE = REPO / "corpus" / "universal-ai-os" / "DECISIONS.md"


def _entries() -> list[node_dossier.Dossier]:
    branches, figures = parse(EXPORT.read_text(encoding="utf-8"))
    return node_dossier.dossiers(load(), link(branches, figures), public_symbols())


# ── every node, not the interesting subset ────────────────────────────────
def test_all_507_nodes_get_a_dossier() -> None:
    """`BUILD_ORDER.md` ranks the 116 with no candidate that a figure reaches.

    The other 391 are exactly the ones nobody looks at, which is why the count
    has never moved.
    """
    entries = _entries()
    assert len(entries) == 507
    assert len({(e.branch, e.name) for e in entries}) == 507


def test_every_node_carries_an_explicit_lifecycle_state() -> None:
    allowed = {"DISCOVERED", "EVIDENCE-BACKED", "PROPOSED", "REJECTED", "IMPLEMENTED"}
    assert {e.lifecycle for e in _entries()} <= allowed


def test_evidence_and_lifecycle_are_different_axes() -> None:
    """The two numbers that look contradictory and are not.

    134 nodes have a direct figure; only 116 read EVIDENCE-BACKED, because 18
    already carry a proposal. MCP has 62 direct figures *and* an alias. Collapsing
    the states would lose one of the two facts.
    """
    entries = _entries()
    with_figures = [e for e in entries if e.direct]
    assert len(with_figures) > sum(1 for e in with_figures if e.lifecycle == "EVIDENCE-BACKED")

    mcp = next(e for e in entries if e.name == "MCP")
    assert mcp.direct > 0 and mcp.lifecycle == "PROPOSED"


# ── the machine does not decide ───────────────────────────────────────────
def test_nothing_here_confirms_anything() -> None:
    """The rule the whole node map stands on, at the place it would break.

    A dossier engine that could set `verified` would make the count of confirmed
    decisions meaningless — it is only worth reading because a machine cannot
    raise it.
    """
    assert all(e.verified is False for e in _entries())

    source = (ENGINE / "scripts" / "node_dossier.py").read_text(encoding="utf-8")
    for forbidden in ("verified=True", "verified = True", '"verified": True'):
        assert forbidden not in source


def test_the_queue_leaves_the_decision_columns_empty() -> None:
    """Three empty cells per row. A pre-filled decision is a fabricated one."""
    # Counted by column width rather than by prefix: the document also holds a
    # two-column summary table, and a filter that swept it in would have made
    # this assertion about the wrong rows.
    rows = [
        line
        for line in QUEUE.read_text(encoding="utf-8").splitlines()
        if line.count("|") == 13 and not line.startswith("| branch |") and "---" not in line
    ]
    assert len(rows) == 507
    data = rows
    for row in data:
        assert row.endswith("| | | |"), row


def test_the_document_says_its_ranking_is_a_heuristic() -> None:
    """A score presented as a finding becomes an authority nobody voted for."""
    text = QUEUE.read_text(encoding="utf-8")
    assert "**heuristic**, not a finding" in text
    assert "they do not know whether a symbol is the" in text


def test_a_settled_node_is_not_reopened() -> None:
    """A person's `implemented` or `rejected` may not be re-proposed by a machine."""
    settled = Node(branch="I", name="Whatever", claim="rejected", alias=None, verified=True)
    _, _, why = node_dossier._verdict(settled, "omnex.core.Money", 10, 5)
    assert "must not return" in why

    agreed = Node(
        branch="I", name="Whatever", claim="implemented", alias="omnex.core.Money", verified=True
    )
    action, _, _ = node_dossier._verdict(agreed, "omnex.core.Money", 10, 5)
    assert action == "settled"


def test_an_unverified_implemented_claim_reads_as_proposed() -> None:
    """`implemented` without a person behind it is a proposal wearing a better word."""
    node = Node(branch="I", name="X", claim="implemented", alias="omnex.core.Money", verified=False)
    assert node_dossier._lifecycle(node, 3) == "PROPOSED"


# ── one resolver, reused ──────────────────────────────────────────────────
def test_the_candidate_comes_from_the_canonical_proposer() -> None:
    """`one_symbol_resolver` — a second matcher here would drift from node_map."""
    source = (ENGINE / "scripts" / "node_dossier.py").read_text(encoding="utf-8")
    assert "from node_map import" in source and "propose" in source
    # No private re-implementation of the token split that propose() owns.
    assert "_split_node" not in source
    assert "_split_symbol" not in source


def test_containment_still_runs_one_way() -> None:
    """The rule that stopped `omnex.factory.Tool` being proposed for 14 nodes."""
    entries = _entries()
    tool_nodes = [e for e in entries if e.name.startswith("Tool ") and e.candidate]
    assert len(tool_nodes) <= 1, [e.name for e in tool_nodes]


# ── evidence rules ────────────────────────────────────────────────────────
def test_only_direct_figures_rank_the_queue() -> None:
    """Chapter edges outnumber lexical ones 736 to 550.

    Ranking on the total ranks on chapter size: ReAct (6 direct, 63 chapter)
    would outrank Vector Search (22, 21).
    """
    backed = sorted([e for e in _entries() if e.direct], key=lambda e: e.key)
    assert [e.direct for e in backed] == sorted((e.direct for e in backed), reverse=True)

    react = next(e for e in _entries() if e.name == "ReAct")
    vector = next(e for e in _entries() if e.name == "Vector Search")
    assert react.chapter > vector.chapter
    assert vector.direct > react.direct
    assert vector.key < react.key, "chapter affinity leaked into the ranking"


def test_nodes_with_no_evidence_are_listed_and_not_scored() -> None:
    """NO-EVIDENCE is not NO-VALUE, and scoring an absence would say it was one."""
    text = QUEUE.read_text(encoding="utf-8")
    assert "NO-EVIDENCE — 373 nodes, unranked" in text
    assert "That is not NO-VALUE" in text

    entries = _entries()
    unbacked = [e for e in entries if not e.direct]
    assert len(unbacked) == 373
    assert all(e.direct == 0 for e in unbacked)


def test_a_node_with_no_figures_can_still_have_a_real_capability() -> None:
    """The example the NO-EVIDENCE heading names, kept as a test.

    `Idempotency` is reached by zero figures and `omnex.pipeline.IdempotencyStore`
    has been in the package for months. Lexical matching measures shared
    vocabulary with one book, never whether the capability matters.
    """
    idempotency = next(e for e in _entries() if e.name == "Idempotency")
    assert idempotency.direct == 0
    assert idempotency.candidate == "omnex.pipeline.IdempotencyStore"


# ── the document is reproducible ──────────────────────────────────────────
def test_generating_twice_produces_the_same_document() -> None:
    """A queue that reorders itself makes every diff unreadable."""
    entries = _entries()
    assert node_dossier.render(entries) == node_dossier.render(entries)
    assert node_dossier.render(entries) == QUEUE.read_text(encoding="utf-8")


def test_the_committed_queue_matches_the_repository() -> None:
    """Same rule as execution_state.json: derived, so it must be regenerable."""
    assert node_dossier.render(_entries()) == QUEUE.read_text(encoding="utf-8")
