"""Rank what to build next by evidence, not by opinion.

    python scripts/build_order.py

Part 1 placed 509 figures onto nodes. Part 2 classified 507 nodes against code
that imports. This is the join, and it is the only file in the chain that says
what to do next — so it is also the one with the most room to be quietly wrong.

## Three rules, each guarding a way this ranking could lie

**Only direct evidence ranks.** An edge from chapter affinity says "figures in
this chapter usually land here". That is a prior about a neighbourhood, not
evidence about the node, and there are 736 of them against 550 lexical ones. Rank
on the total and the order stops measuring evidence and starts measuring chapter
size: ReAct (6 direct, 63 chapter) climbs above Vector Search (22 direct, 21),
and the queue now recommends whatever the book drew the most pictures near.
Chapter counts are shown, in their own column, and never sort anything.

**`gap` means no alias, not proven absence.** `node_map.propose()` matches token
sets, so "Vector Search" is a gap while `omnex.vectors.HybridStore` sits in the
package. A queue that reads gap as "missing" sends somebody to rebuild the vector
store. So every row carries the action derived from its branch: a branch that
exports resolving symbols gets `alias?` — go look before writing anything — and
only a branch exporting nothing at all gets `build`.

**Everything is accounted for.** Ranked plus unevidenced plus proposed plus
confirmed equals 507 or the run fails. A build order listing 111 nodes out of 507
without saying where the other 396 went is a reading list, not a measurement.

## What this does not decide

Evidence is how much of one book depends on a capability. It is not market
demand, not revenue, and not whether the thing is worth building at all — that
question belongs to `harness.worth_it`, which runs per node before any code, and
can reject the top of this list. The ranking says what the corpus insists on.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ingest_atlas import CORPUS, EXPECTED_NODES, EXPORT, Figure, parse
from link_nodes import Link, link
from node_map import CLAIMS, Node, load

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
BRANCHES = ROOT / "ontology" / "branches.json"
ORDER = CORPUS / "BUILD_ORDER.md"

#: The signals that count as evidence about a node. `chapter` is deliberately
#: absent: it is evidence about a chapter, and it outnumbers these two.
DIRECT = ("lexical", "reinforced")

#: Below this, the evidence is one or two captions. Such a node stays in the
#: table — dropping it would hide it — but it sits under a heading that says
#: what that much evidence is worth.
THIN = 3

#: How many rows get their figures listed. The rest are traceable through
#: `node_links.json`; printing 111 evidence blocks makes the document unreadable
#: and unreadable is how a ranking stops being checked.
DETAILED = 12


@dataclass(frozen=True)
class Candidate:
    """One node with no code, and what the corpus says about it."""

    branch: str
    name: str
    direct: int
    chapter: int
    #: Figure ids that reached this node lexically, strongest edge first.
    figures: tuple[str, ...]
    #: `build` where the branch exports nothing, `alias?` where it exports
    #: something that has to be ruled out first.
    action: str
    branch_name: str
    branch_claim: str

    @property
    def key(self) -> tuple[int, int, str, str]:
        """Deterministic order: direct evidence, then chapter, then identity.

        Ties broken on names rather than on dict order, so two runs of this
        script on the same corpus produce the same document and a diff means a
        real change.
        """
        return (-self.direct, -self.chapter, self.branch, self.name)


def branch_status() -> dict[str, tuple[str, str, int]]:
    """Each branch's name, claim and how many symbols it exports.

    Read from `branches.json` rather than re-derived: `ontology_map.py` already
    resolves every symbol on every run, so a claim that survives in that file has
    already been checked against imports.
    """
    raw = json.loads(BRANCHES.read_text(encoding="utf-8"))
    return {b["id"]: (b["name"], b["claim"], len(b["symbols"])) for b in raw["branches"]}


def evidence(links: list[Link]) -> tuple[dict[tuple[str, str], int], dict[tuple[str, str], int]]:
    """Direct and chapter edge counts per node, kept apart on purpose."""
    direct: dict[tuple[str, str], int] = {}
    chapter: dict[tuple[str, str], int] = {}
    for edge in links:
        key = (edge.branch_id, edge.node)
        bucket = direct if edge.via in DIRECT else chapter
        bucket[key] = bucket.get(key, 0) + 1
    return direct, chapter


def rank(nodes: list[Node], links: list[Link]) -> list[Candidate]:
    """Every node with no code candidate that at least one figure reaches."""
    status = branch_status()
    direct, chapter = evidence(links)
    figures: dict[tuple[str, str], list[str]] = {}
    for edge in sorted(links, key=lambda e: (-e.score, e.figure_id)):
        if edge.via in DIRECT:
            figures.setdefault((edge.branch_id, edge.node), []).append(edge.figure_id)

    out: list[Candidate] = []
    for node in nodes:
        key = (node.branch, node.name)
        if node.claim != "gap" or (key not in direct and key not in chapter):
            continue
        name, claim, symbols = status.get(node.branch, (node.branch, "unknown", 0))
        out.append(
            Candidate(
                branch=node.branch,
                name=node.name,
                direct=direct.get(key, 0),
                chapter=chapter.get(key, 0),
                figures=tuple(figures.get(key, ())),
                action="alias?" if symbols else "build",
                branch_name=name,
                branch_claim=claim,
            )
        )
    return sorted(out, key=lambda c: c.key)


def reconcile(nodes: list[Node], ranked: list[Candidate]) -> list[str]:
    """Ranked + unevidenced + proposed + confirmed == every node, or say so.

    The same rule `unplaced()` applies to figures. A queue that silently covers
    a fifth of the ontology cannot be argued with, which is the property that
    makes it dangerous rather than merely incomplete.
    """
    problems: list[str] = []
    if len(nodes) != EXPECTED_NODES:
        problems.append(f"{len(nodes)} nodes loaded, the export declares {EXPECTED_NODES}")

    counts = {claim: sum(1 for n in nodes if n.claim == claim) for claim in CLAIMS}
    unevidenced = counts["gap"] - len(ranked)
    total = len(ranked) + unevidenced + counts["proposed"] + counts["implemented"]
    if total != len(nodes):
        problems.append(f"{total} nodes accounted for, {len(nodes)} exist")
    if unevidenced < 0:
        problems.append(f"{len(ranked)} ranked exceeds {counts['gap']} nodes with no code")

    ranked_keys = {(c.branch, c.name) for c in ranked}
    if len(ranked_keys) != len(ranked):
        problems.append("a node appears twice in the ranking")
    return problems


def render(nodes: list[Node], figures: list[Figure], ranked: list[Candidate]) -> str:
    counts = {claim: sum(1 for n in nodes if n.claim == claim) for claim in CLAIMS}
    unevidenced = counts["gap"] - len(ranked)
    by_id = {f.id: f for f in figures}
    strong = [c for c in ranked if c.direct >= THIN]
    thin = [c for c in ranked if c.direct < THIN]

    lines = [
        "# Build order — what the corpus insists on, ranked",
        "",
        "Generated by `engine/scripts/build_order.py`. Do not edit.",
        "",
        f"{len(ranked)} of {counts['gap']} nodes with no code candidate are reached by at "
        f"least one figure. The other {unevidenced} are named by the ontology and "
        "evidenced by nothing in this corpus — matching is lexical, so that is a "
        "statement about shared vocabulary, never about whether the capability "
        "matters.",
        "",
        "## Read the two columns separately",
        "",
        "**`direct`** counts figures whose text names the node. **`chapter`** counts "
        "figures placed by chapter affinity — a prior about a neighbourhood, not "
        "evidence about the node, and there are more of them in the corpus than "
        "there are direct edges. Only `direct` sorts this table. Ranked on the "
        "total, ReAct (6 direct, 63 chapter) would outrank Vector Search (22 "
        "direct, 21), and the order would be measuring how many pictures the book "
        "drew nearby.",
        "",
        "**`action`** is derived, not chosen. `gap` here means `node_map.propose()` "
        "found no symbol whose token set matches the node name — it does not mean "
        "the capability is absent. `Vector Search` is a gap while "
        "`omnex.vectors.HybridStore` is in the package. So a node on a branch that "
        "already exports resolving symbols gets **`alias?`**: go read that code and "
        "either commit an alias or record why it is not the same thing. Only a "
        "branch exporting nothing at all gets **`build`**.",
        "",
        "Evidence is not a decision. It says how much of one book depends on a "
        "capability, and nothing about demand, revenue or difficulty. "
        "`harness.worth_it` answers that, per node, before any code — and it is "
        "allowed to reject the top of this list.",
        "",
        "`alias?` is an instruction to look, and looking has two outcomes, both "
        "recordable. If the code is the capability, commit the alias in "
        "`nodes.json` and the node leaves this queue. If it is not, name what is "
        "actually absent in that branch's `missing` list in `branches.json` — the "
        "way branch XII names A2A. A conclusion that goes in neither place is one "
        "the next reader has to reach again from scratch.",
        "",
        "This queue moves as code lands. MCP led it at 62 direct figures until "
        "`omnex.mcp` was built; branch XII then began exporting symbols, "
        "`node_map.refresh()` proposed an alias, and the node left the ranking — "
        "taking every other XII node from `build` to `alias?` with it.",
        "",
        f"## The queue — {len(strong)} nodes with {THIN} or more direct figures",
        "",
        "| # | node | branch | direct | chapter | action |",
        "|--:|---|---|--:|--:|---|",
    ]
    for position, c in enumerate(strong, 1):
        lines.append(
            f"| {position} | **{c.name}** | {c.branch} · {c.branch_name} | "
            f"{c.direct} | {c.chapter} | `{c.action}` |"
        )

    lines += [
        "",
        f"## Evidence for the top {min(DETAILED, len(strong))}",
        "",
        "Figure ids resolve in `manifest.json`; every one carries the PDF page it "
        "was cut from, so a claim here can be checked against the book.",
        "",
    ]
    for c in strong[:DETAILED]:
        lines.append(f"### {c.name} — {c.branch} · {c.branch_name} (`{c.action}`)")
        lines.append("")
        lines.append(
            f"{c.direct} figures name it directly; the branch is `{c.branch_claim}` "
            f"in `branches.json`."
        )
        lines.append("")
        for fid in c.figures[:8]:
            figure = by_id.get(fid)
            if figure is None:  # pragma: no cover - ids come from the same parse
                continue
            title = figure.title or figure.caption[:60] or "(untitled)"
            lines.append(f"- `{fid}` p.{figure.pdf_page} — {title}")
        if len(c.figures) > 8:
            lines.append(f"- … and {len(c.figures) - 8} more")
        lines.append("")

    lines += [
        f"## Thin evidence — {len(thin)} nodes under {THIN} direct figures",
        "",
        "One or two captions. Listed rather than dropped, because a node removed "
        "from the document is a node nobody argues with again.",
        "",
        "| node | branch | direct | chapter | action |",
        "|---|---|--:|--:|---|",
    ]
    for c in thin:
        lines.append(
            f"| {c.name} | {c.branch} · {c.branch_name} | {c.direct} | {c.chapter} | `{c.action}` |"
        )

    lines += [
        "",
        "## Reconciliation",
        "",
        "| bucket | nodes |",
        "|---|--:|",
        f"| ranked here (no code, evidenced) | {len(ranked)} |",
        f"| no code, no figure reaches them | {unevidenced} |",
        f"| alias proposed, awaiting a human | {counts['proposed']} |",
        f"| confirmed implemented | {counts['implemented']} |",
        f"| **total** | **{len(nodes)}** |",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    nodes = load()
    branches, figures = parse(EXPORT.read_text(encoding="utf-8"))
    links = link(branches, figures)
    ranked = rank(nodes, links)

    problems = reconcile(nodes, ranked)
    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        return 1

    ORDER.write_text(render(nodes, figures, ranked), encoding="utf-8")
    print(f"{len(ranked)} nodes with no code are evidenced by at least one figure")
    for position, c in enumerate(ranked[:10], 1):
        print(f"  {position:2}. {c.direct:3} direct {c.chapter:3} chapter  {c.action:6} {c.name}")
    print(f"\nwrote {ORDER.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
