"""The ranking that decides what gets built — and the ways it could lie.

A ranking is the most dangerous artifact in the chain. A wrong parse fails loudly
downstream; a wrong ORDER produces a perfectly formatted table that sends work at
the wrong thing for a month, and nobody can tell by looking at it.

So each test here names a specific way the order could be wrong while still
rendering: sorted by the wrong signal, reading `gap` as absence, or covering a
fifth of the ontology without saying where the rest went.
"""

from __future__ import annotations

import pytest
from build_order import DIRECT, THIN, Candidate, branch_status, evidence, rank, reconcile
from ingest_atlas import EXPORT, parse
from link_nodes import link
from node_map import load

pytestmark = pytest.mark.skipif(
    not EXPORT.exists(), reason="the Universal AI OS export is not in this checkout"
)


def _ranked():
    nodes = load()
    branches, figures = parse(EXPORT.read_text(encoding="utf-8"))
    return nodes, figures, rank(nodes, link(branches, figures))


def test_only_nodes_without_a_code_candidate_are_ranked() -> None:
    """A build order containing things already built is a to-do list, not an order."""
    nodes, _, ranked = _ranked()
    claim = {(n.branch, n.name): n.claim for n in nodes}
    for candidate in ranked:
        assert claim[(candidate.branch, candidate.name)] == "gap", candidate.name


def test_chapter_edges_never_change_the_order() -> None:
    """The trap this file exists for.

    Chapter affinity outnumbers direct evidence in this corpus, so ranking on the
    total silently ranks on chapter size. Measured: ReAct has 6 direct edges and
    63 chapter ones, Vector Search 22 and 21. On totals ReAct wins by a distance;
    on evidence it is not close. The order must reflect the second.
    """
    _, _, ranked = _ranked()
    by_name = {c.name: c for c in ranked}
    react, vectors = by_name["ReAct"], by_name["Vector Search"]
    assert react.chapter + react.direct > vectors.chapter + vectors.direct
    assert vectors.direct > react.direct
    assert ranked.index(vectors) < ranked.index(react), "the order followed chapter affinity"


def test_the_ranking_is_sorted_by_direct_evidence() -> None:
    _, _, ranked = _ranked()
    assert [c.direct for c in ranked] == sorted((c.direct for c in ranked), reverse=True)


def test_chapter_edges_are_counted_but_are_not_evidence() -> None:
    _, _, ranked = _ranked()
    assert "chapter" not in DIRECT
    assert any(c.chapter > 0 for c in ranked), "chapter counts were dropped, not separated"


def test_a_gap_on_a_branch_with_code_asks_before_it_builds() -> None:
    """`gap` means no alias was proposed. It never means the capability is absent.

    `node_map.propose()` matches token sets, so "Vector Search" is a gap while
    `omnex.vectors.HybridStore` sits in the package. A queue that reads gap as
    missing sends somebody to rebuild the vector store, and the rebuild passes
    review because the document said to.
    """
    _, _, ranked = _ranked()
    vectors = next(c for c in ranked if c.name == "Vector Search")
    assert vectors.action == "alias?"
    status = branch_status()
    for candidate in ranked:
        _, _, symbols = status[candidate.branch]
        expected = "alias?" if symbols else "build"
        assert candidate.action == expected, candidate.name


def test_build_is_only_claimed_where_the_branch_exports_nothing() -> None:
    _, _, ranked = _ranked()
    status = branch_status()
    for candidate in (c for c in ranked if c.action == "build"):
        assert status[candidate.branch][2] == 0, f"{candidate.branch} exports symbols"


def test_the_queue_moved_when_the_node_at_its_head_was_built() -> None:
    """This test failed on purpose, and that failure is the point of it.

    The first version asserted `ranked[0].name == "MCP"` — 62 figures, branch XII
    exporting nothing — and said that if either half changed it was supposed to
    break, because the queue had moved and anything quoting it was stale. Then
    `omnex.mcp` landed, branch XII started exporting symbols, `node_map.refresh()`
    proposed an alias, and MCP left the ranking entirely. The test broke exactly
    where it said it would.

    So it now records the movement rather than the position: MCP is gone from the
    queue, and every remaining node on that branch has stopped saying `build`,
    because there is now code on XII to read before writing more.
    """
    nodes, _, ranked = _ranked()
    names = {c.name for c in ranked}
    assert "MCP" not in names, "MCP is back in the build queue"

    mcp = next(n for n in nodes if n.branch == "XII" and n.name == "MCP")
    assert mcp.claim == "proposed", "the alias for MCP was lost"
    assert mcp.alias is not None and mcp.alias.startswith("omnex.mcp.")
    assert not mcp.verified, "a machine marked a node implemented"

    fabric = [c for c in ranked if c.branch == "XII"]
    assert fabric, "branch XII lost every node it had evidence for"
    assert all(c.action == "alias?" for c in fabric)


def test_the_head_of_the_queue_is_derived_and_not_asserted() -> None:
    """Whatever leads, leads because the corpus put it there.

    Deliberately not naming the node: pinning the name is what made the previous
    test brittle in a useful way once, and twice is a chore. What must hold is
    that the head is the most-evidenced node with no code, and that it is ahead
    on direct figures rather than on chapter affinity.
    """
    _, _, ranked = _ranked()
    head = ranked[0]
    assert head.direct == max(c.direct for c in ranked)
    assert head.direct > head.chapter or head.direct >= 20, (
        "the head is carried by chapter affinity, which is not evidence"
    )


def test_every_node_is_accounted_for() -> None:
    """Ranked + unevidenced + proposed + confirmed == 507, or the run fails.

    `unplaced()` applies this to figures for the same reason: a document that
    quietly covers 111 of 507 cannot be argued with, and that is what makes it
    worse than one reporting the shortfall.
    """
    nodes, _, ranked = _ranked()
    assert reconcile(nodes, ranked) == []


def test_reconciliation_catches_a_node_ranked_twice() -> None:
    nodes, _, ranked = _ranked()
    problems = reconcile(nodes, [*ranked, ranked[0]])
    assert any("twice" in p for p in problems)


def test_evidence_counts_split_on_the_signal_that_produced_the_edge() -> None:
    branches, figures = parse(EXPORT.read_text(encoding="utf-8"))
    links = link(branches, figures)
    direct, chapter = evidence(links)
    assert sum(direct.values()) + sum(chapter.values()) == len(links)
    assert set(direct) & set(chapter), "no node has both, so the split is not being exercised"


def test_thin_evidence_is_kept_visible_rather_than_trimmed() -> None:
    """One caption is weak evidence. It is not an argument for deletion."""
    _, _, ranked = _ranked()
    thin = [c for c in ranked if c.direct < THIN]
    assert thin, "nothing is thin, so the threshold is not doing anything"
    from build_order import ORDER

    if ORDER.exists():
        page = ORDER.read_text(encoding="utf-8")
        for candidate in thin[:5]:
            assert candidate.name in page


def test_the_document_refuses_to_read_evidence_as_a_decision() -> None:
    from build_order import ORDER

    if not ORDER.exists():
        pytest.skip("BUILD_ORDER.md not generated in this checkout")
    page = ORDER.read_text(encoding="utf-8")
    assert "Evidence is not a decision" in page
    assert "worth_it" in page
    assert "never about whether the capability matters" in page


def test_the_order_is_stable_across_runs() -> None:
    """Two runs on one corpus must produce one document, or a diff means nothing."""
    _, _, first = _ranked()
    _, _, second = _ranked()
    assert [(c.branch, c.name) for c in first] == [(c.branch, c.name) for c in second]


def test_a_candidate_sorts_on_evidence_before_identity() -> None:
    strong = Candidate("XII", "A", 9, 0, (), "build", "Fabric", "gap")
    weak = Candidate("I", "B", 2, 99, (), "build", "CS", "gap")
    assert sorted([weak, strong], key=lambda c: c.key)[0] is strong
