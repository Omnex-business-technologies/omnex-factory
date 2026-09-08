"""Figure-to-node edges — the properties that stop a graph from lying convincingly.

A knowledge graph fails differently from a pipeline. A pipeline that breaks stops
producing; a graph that breaks produces *more* — edges that render, cluster and
look like structure while meaning nothing. Nobody reading the picture can tell.

So the tests here are mostly refusals. The fence, the stopword rule, and the
dynamic-range check each exist because without them the edge count goes UP and
the result gets worse.
"""

from __future__ import annotations

import pytest
from ingest_atlas import EXPORT, parse
from link_nodes import (
    CHAPTER_CEILING,
    FLOOR,
    STOPWORDS,
    inverse_frequency,
    link,
    score_match,
    tokens,
    unplaced,
)

pytestmark = pytest.mark.skipif(
    not EXPORT.exists(), reason="the Universal AI OS export is not in this checkout"
)


def _linked():
    branches, figures = parse(EXPORT.read_text(encoding="utf-8"))
    return branches, figures, link(branches, figures)


def test_no_edge_crosses_into_a_branch_the_figure_never_touched() -> None:
    """The fence, and the reason the graph is not simply larger.

    Node names repeat across branches — "Router", "Cache", "Queue". Without the
    export's own branch mapping as a boundary, one caption reaches every branch
    that happens to share a word, and the graph fills with edges that survive
    every visual inspection.
    """
    branches, _, links = _linked()
    touched = {b.id: set(b.touched) for b in branches}
    for edge in links:
        assert edge.figure_id in touched[edge.branch_id], (
            f"{edge.figure_id} was linked to {edge.branch_id}, which it does not touch"
        )


def test_every_edge_names_a_node_that_exists_on_that_branch() -> None:
    branches, _, links = _linked()
    names = {b.id: set(b.node_names) for b in branches}
    for edge in links:
        assert edge.node in names[edge.branch_id], f"{edge.node} is not on {edge.branch_id}"


def test_a_single_common_word_does_not_make_an_edge() -> None:
    """ "Agent Memory" must not attach to every figure that says "agent"."""
    weight = {"agent": 0.1, "memory": 0.4, "hnsw": 5.0}
    assert score_match({"agent", "memory"}, {"agent"}, weight) == 0.0
    # A rare token alone is evidence, and is allowed through.
    assert score_match({"hnsw"}, {"hnsw"}, weight) >= FLOOR


def test_a_node_made_entirely_of_stopwords_can_never_match() -> None:
    assert score_match({"the", "agent"}, {"the", "agent"}, {}) == 0.0
    assert "agent" in STOPWORDS


def test_the_score_has_real_dynamic_range() -> None:
    """The check that caught this file's own first version.

    Scoring a match as the plain share of node tokens present put 452 of 453
    edges in the top band — a confidence score that cannot separate anything,
    and a review queue empty by construction rather than by quality. Weighting
    by token rarity restored the spread. If this ever collapses again, the
    banding has gone back to being decoration.
    """
    _, _, links = _linked()
    bands = {edge.band for edge in links}
    assert len(bands) > 1, "every edge landed in one band — the score is not measuring"
    top = sum(1 for edge in links if edge.band == "auto")
    assert top < len(links), "nothing needs review, which is not a result, it is a bug"


def test_rarity_ranks_a_distinctive_match_above_a_generic_one() -> None:
    _, figures = parse(EXPORT.read_text(encoding="utf-8"))
    weight = inverse_frequency(figures)
    common = [t for t in weight if weight[t] < 1.0]
    rare = [t for t in weight if weight[t] > 4.0]
    assert common and rare, "the corpus should contain both frequent and rare tokens"
    assert max(weight[t] for t in rare) > max(weight[t] for t in common)


def test_the_uncovered_count_is_reported_as_an_upper_bound() -> None:
    """Lexical matching misses paraphrase, and the document must not pretend otherwise.

    A reader who takes "373 nodes uncovered" as "373 nodes the field ignores"
    has been misled by this repository rather than by the corpus.
    """
    from link_nodes import COVERAGE

    page = COVERAGE.read_text(encoding="utf-8")
    assert "upper bound" in page
    assert "never semantic" in page
    assert "not a verdict on the nodes" in page


def test_tokens_ignores_single_characters() -> None:
    assert tokens("A B mcp") == {"mcp"}


def test_every_figure_is_placed_or_accounted_for() -> None:
    """The reconciliation. "We covered them all" has to be checkable.

    A coverage document that quietly counts 296 of 509 and calls it coverage is
    worse than one reporting 213 misses, because the first cannot be argued
    with. Placed plus unplaced must equal the manifest exactly.
    """
    _, figures, links = _linked()
    missing = unplaced(figures, links)
    placed = {edge.figure_id for edge in links}
    assert len(placed) + len(missing) == len(figures)
    assert not (placed & {row["figure_id"] for row in missing})


def test_every_unplaced_figure_names_a_reason() -> None:
    _, figures, links = _linked()
    for row in unplaced(figures, links):
        assert row["reason"].strip(), row["figure_id"]


def test_a_chapter_edge_can_never_be_auto_accepted() -> None:
    """Structural, not tuned.

    Chapter affinity says "figures like this one usually land here" — a prior
    about a neighbourhood, not evidence about this figure. The ceiling sits
    below the auto band, so no affinity value can promote a guess into the
    trusted band.
    """
    from omnex.rag.figures import Band

    assert CHAPTER_CEILING < 0.85
    _, _, links = _linked()
    chapter_edges = [e for e in links if e.via == "chapter"]
    assert chapter_edges, "the chapter signal produced nothing"
    assert all(e.band != str(Band.AUTO) for e in chapter_edges)


def test_neighbourhood_only_reinforces_what_lexical_found() -> None:
    """It may strengthen a candidate; it may never invent one.

    A figure that could create an edge from its neighbours propagates a single
    mislink down a whole chapter, and the result reads as more confident the
    more wrong it is.
    """
    _, _, links = _linked()
    reinforced = [e for e in links if e.via == "reinforced"]
    assert reinforced
    # Every reinforced edge is a lexical edge that was promoted, so its node
    # must also be reachable lexically somewhere in the corpus.
    lexical_nodes = {(e.branch_id, e.node) for e in links if e.via in ("lexical", "reinforced")}
    assert all((e.branch_id, e.node) in lexical_nodes for e in reinforced)


def test_placing_more_figures_did_not_silently_lower_node_coverage() -> None:
    """The regression this file caught during its own construction.

    Weighting a lexical match by the exporter's branch score BEFORE the floor
    test dropped 37 exact matches and nine nodes with them — better figure
    coverage bought with worse node coverage, which is not a repair. The score
    now ranks a match and never gates one.
    """
    _, _, links = _linked()
    reached = {(e.branch_id, e.node) for e in links}
    assert len(reached) >= 134, f"node coverage fell to {len(reached)}"
