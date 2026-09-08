"""Link the 509 figures to the 507 nodes, at the resolution the export lacks.

    python scripts/link_nodes.py

The export maps every figure to BRANCHES and stops there. That is 28 buckets for
509 figures, and it is why "the protocol fabric carries 184 figures" is true and
useless for building anything: the branch has seventeen nodes, and nobody knows
which figure belongs to MCP rather than to OAuth. This closes that gap and, more
importantly, measures how much of the tree the corpus actually reaches.

## The matching is lexical, and that is stated rather than hidden

A node name is matched against a figure's title, caption and OCR text by token
overlap. That catches the distinctive names — HNSW, ReAct, MCP, LoRA — and misses
every case where the book says "the retrieval step" and the node is called
"Hybrid Search". So recall is bounded by vocabulary, not by the corpus.

Two structural rules keep the result honest rather than merely large:

**A figure may only match nodes on branches it already touches.** The export's
own branch mapping is the fence. Without it, "Router" in a figure caption matches
a node called "Router" in a branch the figure has nothing to do with, and the
graph fills with edges that render convincingly and mean nothing.

**A single shared common word is not a match.** Node names like "Agent Memory"
and "Tool Calling" share tokens with almost everything, so a match needs either a
rare token or more than one token in common. The stop list is in the code and can
be argued with.

## What the number is for

`nodes_reached` is the honest headline: how many of 507 nodes any figure lands
on at all. A low number is not a failure of this script — it is the measurement
that says how much of the ontology this one book can evidence, and therefore how
much of it is still assumption. That is the question the whole ontology v2 change
was about, asked one level finer.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass

from ingest_atlas import CORPUS, EXPORT, Branch, Figure, parse

from omnex.rag.figures import Band

LINKS = CORPUS / "node_links.json"
COVERAGE = CORPUS / "NODE_COVERAGE.md"
UNPLACED = CORPUS / "unplaced.json"

#: Tokens too common in this domain to carry a match on their own. A node named
#: "Agent Memory" must not match every figure that says "agent".
STOPWORDS = frozenset(
    [
        "a",
        "an",
        "and",
        "as",
        "at",
        "by",
        "for",
        "from",
        "in",
        "into",
        "of",
        "on",
        "or",
        "the",
        "to",
        "with",
        "agent",
        "agents",
        "ai",
        "api",
        "based",
        "data",
        "design",
        "engine",
        "flow",
        "layer",
        "llm",
        "llms",
        "model",
        "models",
        "node",
        "pattern",
        "patterns",
        "process",
        "system",
        "systems",
        "tool",
        "tools",
        "type",
        "types",
        "use",
        "used",
        "using",
        "via",
        "work",
    ]
)

#: Below this, a match is noise. Bands come from `Band.of`, so this is the floor
#: under the review queue rather than a second, competing threshold.
FLOOR = 0.5

#: A token this rare carries a match on its own. log(509/(1+c)) crosses 2.5
#: at roughly forty figures, so "MCP" qualifies and "memory" does not.
RARE = 2.5

#: Weight for a node token that appears in no figure at all — treated as
#: maximally rare, so its ABSENCE from a match counts heavily against it.
MAX_IDF = math.log(509.0)

#: A chapter-derived edge can never be auto-accepted. Chapter affinity says
#: "figures like this one usually land here", which is a prior about a
#: neighbourhood, not evidence about this figure. Capping it below Band.AUTO is
#: structural: no tuning of the affinity can promote it into the trusted band.
CHAPTER_CEILING = 0.84

#: Below this share of a chapter's linked figures, an affinity is noise.
CHAPTER_FLOOR = 0.06

#: Pages either side that may REINFORCE an existing candidate. Never create one:
#: a figure that invents an edge from its neighbours propagates one mislink down
#: a whole chapter, and the result looks more confident the more wrong it is.
NEIGHBOUR_PAGES = 2
NEIGHBOUR_BONUS = 0.05


def tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 1}


@dataclass(frozen=True)
class Link:
    """One figure attached to one node, with the score that put it there."""

    figure_id: str
    branch_id: str
    node: str
    score: float
    #: Which signal produced this edge. An edge that cannot say why it exists is
    #: indistinguishable from one somebody typed, and the three signals here are
    #: not equally strong — so the reason travels with the edge rather than
    #: living in a commit message.
    via: str = "lexical"

    @property
    def band(self) -> str:
        return str(Band.of(self.score))


def inverse_frequency(figures: list[Figure]) -> dict[str, float]:
    """How rare each token is across the corpus, for weighting a match.

    The first version of this file scored a match as the share of the node's
    tokens that appeared, which put 452 of 453 edges in the top band — a
    confidence score with no dynamic range, and therefore a review queue that
    was empty by construction rather than by quality. Matching "MCP" and
    matching "memory" are not the same evidence, and a score that cannot tell
    them apart is decoration.
    """
    counts: dict[str, int] = {}
    for figure in figures:
        for token in tokens(f"{figure.title} {figure.caption} {figure.ocr}"):
            counts[token] = counts.get(token, 0) + 1
    total = max(len(figures), 1)
    return {token: math.log(total / (1 + count)) for token, count in counts.items()}


def score_match(node_tokens: set[str], figure_tokens: set[str], weight: dict[str, float]) -> float:
    """How strongly a node name is present in a figure's text, weighted by rarity.

    Scored on the NODE's tokens rather than on the union: a two-word node fully
    present in a long OCR block is a strong match, and Jaccard would punish it
    for the length of text it was found in. Each token then counts for how rare
    it is, so a node reached through its distinctive word outranks one reached
    through a word half the corpus uses.
    """
    meaningful = node_tokens - STOPWORDS
    if not meaningful:
        return 0.0
    hits = meaningful & figure_tokens
    if not hits:
        return 0.0
    # One common token alone is not evidence; a rare one, or two of them, is.
    if len(hits) == 1 and len(meaningful) > 1 and weight.get(next(iter(hits)), 0.0) < RARE:
        return 0.0
    have = sum(weight.get(t, MAX_IDF) for t in hits)
    want = sum(weight.get(t, MAX_IDF) for t in meaningful)
    return min(have / want, 1.0) if want else 0.0


def _branch_weight(figure: Figure, name_to_id: dict[str, str]) -> dict[str, float]:
    """How strongly the exporter scored each branch for this figure.

    Used to modulate a lexical match, never to create one. Normalised into
    [0.6, 1.0] so a branch the exporter was unsure about still contributes —
    the scores are the exporter's judgement, and treating them as a hard filter
    would import its review queue as though it were settled.
    """
    if not figure.mappings:
        return {}
    top = max(score for _, score in figure.mappings) or 1.0
    return {
        name_to_id[name]: 0.6 + 0.4 * (score / top)
        for name, score in figure.mappings
        if name in name_to_id
    }


def chapter_affinity(
    branches: list[Branch], figures: list[Figure], links: list[Link]
) -> dict[str, list[tuple[str, str, float]]]:
    """Which nodes the linked figures of each chapter actually landed on.

    Derived from the lexical pass rather than hand-assigned. A hand-written
    chapter->node table is a second ontology to maintain and drifts from the
    first; this one cannot disagree with the edges, because it is made of them.
    """
    by_chapter: dict[str, dict[tuple[str, str], int]] = {}
    totals: dict[str, int] = {}
    placed = {edge.figure_id: edge for edge in links}

    for figure in figures:
        if figure.id not in placed or not figure.chapter:
            continue
        totals[figure.chapter] = totals.get(figure.chapter, 0) + 1
        for edge in [e for e in links if e.figure_id == figure.id]:
            key = (edge.branch_id, edge.node)
            by_chapter.setdefault(figure.chapter, {})
            by_chapter[figure.chapter][key] = by_chapter[figure.chapter].get(key, 0) + 1

    affinity: dict[str, list[tuple[str, str, float]]] = {}
    for chapter, counts in by_chapter.items():
        total = max(totals.get(chapter, 0), 1)
        rows = [
            (bid, node, hits / total)
            for (bid, node), hits in counts.items()
            if hits / total >= CHAPTER_FLOOR
        ]
        affinity[chapter] = sorted(rows, key=lambda r: -r[2])[:6]
    return affinity


def link(branches: list[Branch], figures: list[Figure]) -> list[Link]:
    """Attach figures to nodes with three signals, strongest first.

    1. Lexical, fenced by the branches the export already mapped the figure to,
       weighted by rarity and by the exporter's own branch score.
    2. Chapter affinity, for figures the first pass could not place at all.
       Capped below the auto band by construction.
    3. Page neighbourhood, which may only reinforce an existing candidate.

    The order matters and is not a preference: a weaker signal never overwrites
    a stronger one, and never manufactures an edge where the stronger signal
    found nothing to reinforce.
    """
    by_figure: dict[str, list[str]] = {}
    for branch in branches:
        for fid in branch.touched:
            by_figure.setdefault(fid, []).append(branch.id)

    name_to_id = {b.name: b.id for b in branches}
    nodes_of = {b.id: [(n, tokens(n)) for n in b.node_names] for b in branches}
    weight = inverse_frequency(figures)
    links: list[Link] = []

    # --- signal 1: lexical ---------------------------------------------------
    for figure in figures:
        text = tokens(f"{figure.title} {figure.caption} {figure.ocr}")
        if not text:
            continue
        branch_weight = _branch_weight(figure, name_to_id)
        for branch_id in by_figure.get(figure.id, []):
            modifier = branch_weight.get(branch_id, 1.0)
            for node, node_tokens in nodes_of.get(branch_id, []):
                raw = score_match(node_tokens, text, weight)
                if raw < FLOOR:
                    continue
                # The exporter's branch score RANKS a match; it never gates one.
                # Multiplying before the floor test dropped 37 lexically exact
                # edges and nine nodes with them — trading node coverage for
                # figure coverage, which is not a repair.
                score = max(min(raw * modifier, 1.0), FLOOR)
                links.append(Link(figure.id, branch_id, node, score, "lexical"))

    # --- signal 2: chapter affinity, only for figures still unplaced ----------
    affinity = chapter_affinity(branches, figures, links)
    placed = {edge.figure_id for edge in links}
    for figure in figures:
        if figure.id in placed or not figure.chapter:
            continue
        allowed = set(by_figure.get(figure.id, []))
        for branch_id, node, share in affinity.get(figure.chapter, []):
            if branch_id not in allowed:
                continue
            score = min(FLOOR + share, CHAPTER_CEILING)
            if score >= FLOOR:
                links.append(Link(figure.id, branch_id, node, score, "chapter"))

    # --- signal 3: neighbourhood reinforcement -------------------------------
    pages: dict[int, set[tuple[str, str]]] = {}
    for edge in links:
        page = next((f.pdf_page for f in figures if f.id == edge.figure_id), -1)
        pages.setdefault(page, set()).add((edge.branch_id, edge.node))

    reinforced: list[Link] = []
    for edge in links:
        figure = next(f for f in figures if f.id == edge.figure_id)
        near = any(
            (edge.branch_id, edge.node) in pages.get(figure.pdf_page + delta, set())
            for delta in range(-NEIGHBOUR_PAGES, NEIGHBOUR_PAGES + 1)
            if delta != 0
        )
        if near and edge.via == "lexical":
            reinforced.append(
                Link(
                    edge.figure_id,
                    edge.branch_id,
                    edge.node,
                    min(edge.score + NEIGHBOUR_BONUS, 1.0),
                    "reinforced",
                )
            )
        else:
            reinforced.append(edge)

    reinforced.sort(key=lambda edge: (-edge.score, edge.figure_id))
    return reinforced


def unplaced(figures: list[Figure], links: list[Link]) -> list[dict[str, str]]:
    """Every figure with no edge, and the reason — filtering is not deletion.

    `intel.FilterReport.reconciles()` exists because a pipeline that loses rows
    to an off-by-one reports a clean-looking result. The same applies here with
    more force: a coverage document that quietly counts 296 of 509 and calls it
    coverage is worse than one that reports 213 misses, because the first cannot
    be argued with.
    """
    linked = {edge.figure_id for edge in links}
    out: list[dict[str, str]] = []
    for figure in figures:
        if figure.id in linked:
            continue
        text = f"{figure.title} {figure.caption} {figure.ocr}".strip()
        if not text:
            reason = "no title, caption or OCR text to match on"
        elif not figure.chapter:
            reason = "no chapter, so no affinity fallback"
        else:
            reason = (
                "no node name overlaps its text, and its chapter has no affinity above the floor"
            )
        out.append(
            {
                "figure_id": figure.id,
                "chapter": figure.chapter,
                "role": figure.role,
                "primary_branch": figure.primary_branch,
                "reason": reason,
            }
        )
    return out


def render(
    branches: list[Branch],
    figures: list[Figure],
    links: list[Link],
    missing: list[dict[str, str]],
) -> str:
    total_nodes = sum(b.nodes for b in branches)
    reached = {(edge.branch_id, edge.node) for edge in links}
    placed = {edge.figure_id for edge in links}
    by_via: dict[str, int] = {}
    for edge in links:
        by_via[edge.via] = by_via.get(edge.via, 0) + 1

    lines = [
        "# Figure-to-node coverage",
        "",
        "Generated by `engine/scripts/link_nodes.py`. Do not edit.",
        "",
        "## Two coverages, and only one of them is nearly done",
        "",
        f"**Figures placed: {len(placed)} of {len(figures)}.** The remaining "
        f"{len(missing)} are listed individually in `unplaced.json` with a reason "
        "each. Placed plus unplaced must equal the manifest, or the run fails — "
        "filtering is not deletion.",
        "",
        f"**Nodes reached: {len(reached)} of {total_nodes}.** This did not improve "
        "when figure placement did, and it structurally cannot: chapter affinity "
        "is derived from where lexical matches already landed, so it spreads "
        "coverage across figures without discovering a single new node. "
        f"The {total_nodes - len(reached)} unreached nodes need work on the NODE "
        "side — names and aliases — not on the figure side. Reporting the first "
        "number alone would hide that entirely.",
        "",
        f"{len(links)} edges: "
        + " · ".join(f"{count} {via}" for via, count in sorted(by_via.items())),
        "",
        "## What each signal is allowed to do",
        "",
        "- **lexical** — node name tokens against title, caption and OCR, weighted "
        "by how rare each token is, fenced by the branches the export already "
        "mapped the figure to. The exporter's own branch score ranks a match and "
        "never gates one; multiplying before the floor test dropped 37 exact "
        "matches and nine nodes with them.",
        "- **chapter** — for figures the lexical pass could not place at all. "
        f"Capped at {CHAPTER_CEILING} by construction, which is below the auto "
        "band, so no tuning of the affinity can promote a chapter guess into the "
        "trusted band. Affinity is derived from the lexical edges rather than "
        "hand-written, so it cannot disagree with them.",
        "- **reinforced** — a lexical edge whose node also appears within "
        f"{NEIGHBOUR_PAGES} pages. It may only strengthen an existing candidate. "
        "A figure that could invent an edge from its neighbours would propagate "
        "one mislink down a whole chapter and look more confident for it.",
        "",
        "Matching is lexical and structural, never semantic: a figure captioned "
        '"the retrieval step" does not reach a node named "Hybrid Search". **The '
        "unreached count is an upper bound on what this corpus evidences, not a "
        "verdict on the nodes.**",
        "",
        "| # | Branch | Nodes | Reached | Edges |",
        "|---|---|--:|--:|--:|",
    ]

    for branch in sorted(branches, key=lambda b: -b.nodes):
        hit = {edge.node for edge in links if edge.branch_id == branch.id}
        edges = sum(1 for edge in links if edge.branch_id == branch.id)
        lines.append(f"| {branch.id} | {branch.name} | {branch.nodes} | {len(hit)} | {edges} |")

    lines += [
        "",
        "## The number this was built to produce",
        "",
        f"{total_nodes - len(reached)} of {total_nodes} nodes have no figure at "
        "all. Every one is a claim standing on somebody having written it down, "
        "with nothing from this corpus behind it. That is the ontology v2 finding "
        "one level finer and considerably less comfortable.",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    branches, figures = parse(EXPORT.read_text(encoding="utf-8"))
    links = link(branches, figures)
    missing = unplaced(figures, links)

    placed = {edge.figure_id for edge in links}
    if len(placed) + len(missing) != len(figures):
        print(f"FAIL {len(placed)} placed + {len(missing)} unplaced != {len(figures)} figures")
        return 1

    LINKS.write_text(
        json.dumps(
            {
                "floor": FLOOR,
                "edges": [
                    {
                        "figure_id": edge.figure_id,
                        "branch_id": edge.branch_id,
                        "node": edge.node,
                        "score": round(edge.score, 4),
                        "band": edge.band,
                        "via": edge.via,
                    }
                    for edge in links
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    COVERAGE.write_text(render(branches, figures, links, missing), encoding="utf-8")
    UNPLACED.write_text(json.dumps(missing, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    reached = {(edge.branch_id, edge.node) for edge in links}
    total_nodes = sum(b.nodes for b in branches)
    print(f"{len(links)} edges · {len(reached)}/{total_nodes} nodes reached")
    print(f"  figures placed:   {len(placed)}/{len(figures)}  (+{len(missing)} accounted for)")
    print(f"  auto-accept edges: {sum(1 for e in links if e.band == 'auto')}")
    print(f"\nwrote {LINKS.name}, {COVERAGE.name}, {UNPLACED.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
