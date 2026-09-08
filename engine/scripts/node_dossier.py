"""Every one of the 507 nodes, with the evidence a person needs to decide.

    python scripts/node_dossier.py

`nodes.json` records what each node *is claimed to be*: 461 gap, 46 proposed,
0 rejected, **0 implemented**. That last number is the one the whole node map
exists to move, and it has never moved — because moving it means opening a
branch, reading what it exports, working out whether a symbol is the capability,
and doing that 507 times. Nobody does an investigation 507 times.

`BUILD_ORDER.md` ranks the subset with no candidate that a figure reaches. This
covers **all 507**, including the 46 already proposed and the 345 no figure
touches, and it answers per node the question the ranking does not:

    What does this branch actually export, what is the best candidate, which
    direction does containment run, and what would make this decidable?

## What it is not

It is not a decision. `propose()` is reused rather than reimplemented — one
symbol resolver, the rule `one_symbol_resolver` already enforces — and it
proposes exactly what it proposed before. The recommendation column is a
**heuristic**, and says so in the document it writes. Nothing here sets
`verified`; only `apply_decisions.py` with a person's name may.

## The lifecycle, not a boolean

Each node carries a state from `CONSTITUTION.md`, and the states are never
collapsed:

    DISCOVERED       named by the ontology, no figure reaches it
    EVIDENCE-BACKED  at least one DIRECT figure names it, no candidate committed
    PROPOSED         a candidate that imports, unconfirmed
    REJECTED         a person said no
    IMPLEMENTED      a person agreed

`EXISTS ≠ RELEVANT ≠ APPROVED ≠ IMPLEMENTED`. A node with a proposal is not a
node with a decision.

## NO-EVIDENCE is not NO-VALUE

**373** nodes are reached by no direct figure at all. They are listed, unranked,
under a heading that says what that means: matching is lexical, so it is a
statement about shared vocabulary with one book, never about whether the
capability matters. They stay candidates for cheap investigation; they are not
scored as though the corpus backed them.

Note the two numbers that look contradictory and are not. **134** nodes have a
direct figure; only **116** of them are `EVIDENCE-BACKED`, because the other 18
already carry a proposal and so sit in `PROPOSED` — MCP has 62 direct figures and
an alias. Evidence and lifecycle are different axes, which is exactly why the
states are not collapsed into one.

## Only direct edges rank

Chapter-affinity edges outnumber lexical ones 736 to 550. Ranking on the total
ranks on chapter size — ReAct (6 direct, 63 chapter) would beat Vector Search
(22, 21) — so `BUILD_ORDER.md`'s rule holds here unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from build_order import DIRECT, branch_status
from ingest_atlas import CORPUS, EXPORT, parse
from link_nodes import Link, link
from node_map import Node, load, propose, public_symbols

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
BRANCHES = ROOT / "ontology" / "branches.json"
OUTPUT = CORPUS / "DECISIONS.md"

#: How many figure ids are printed per node. The rest are in `node_links.json`;
#: a document nobody can read is a document nobody checks.
FIGURES_SHOWN = 4


@dataclass(frozen=True)
class Dossier:
    """One node, everything measurable about it, and a proposed verdict."""

    branch: str
    branch_name: str
    branch_exports: int
    name: str
    claim: str
    alias: str | None
    verified: bool
    direct: int
    chapter: int
    figures: tuple[str, ...]
    candidate: str | None
    lifecycle: str
    recommendation: str
    confidence: str
    why: str

    @property
    def key(self) -> tuple[int, int, str, str]:
        """Deterministic: direct evidence, then chapter, then identity.

        Ties broken on names rather than dict order, so two runs over one corpus
        produce the same document and a diff means a real change.
        """
        return (-self.direct, -self.chapter, self.branch, self.name)


def _lifecycle(node: Node, direct: int) -> str:
    """The state, from `CONSTITUTION.md`, never collapsed into a boolean."""
    if node.claim == "implemented":
        # `verified` is what separates "a machine matched two names" from "a
        # person agreed they mean the same capability".
        return "IMPLEMENTED" if node.verified else "PROPOSED"
    if node.claim == "rejected":
        return "REJECTED"
    if node.claim == "proposed":
        return "PROPOSED"
    return "EVIDENCE-BACKED" if direct else "DISCOVERED"


def _verdict(node: Node, candidate: str | None, exports: int, direct: int) -> tuple[str, str, str]:
    """Recommendation, confidence and reason — a heuristic, labelled as one."""
    if node.claim == "implemented" and node.verified:
        return "settled", "n/a", "a person agreed; nothing here may change it"
    if node.claim == "rejected":
        return "settled", "n/a", "a person said no; the proposal must not return"
    if node.alias:
        return (
            "confirm-or-reject",
            "MEDIUM" if direct else "LOW",
            f"{node.alias} imports and nobody has ruled on it",
        )
    if candidate:
        return (
            "confirm-or-reject",
            "MEDIUM" if direct else "LOW",
            f"{candidate} matches by token containment, symbol more specific than node",
        )
    if exports:
        return (
            "read-the-branch",
            "LOW",
            f"the branch exports {exports} symbols and none matched by name; read them "
            "and either commit an alias or name what is absent in branches.json",
        )
    return (
        "build",
        "LOW",
        "the branch exports nothing, so no symbol here can be this capability",
    )


def dossiers(nodes: list[Node], links: list[Link], symbols: dict[str, str]) -> list[Dossier]:
    """One dossier per node, for every node, with no second resolver."""
    status = branch_status()
    direct: dict[tuple[str, str], int] = {}
    chapter: dict[tuple[str, str], int] = {}
    seen: dict[tuple[str, str], list[str]] = {}
    for edge in links:
        key = (edge.branch_id, edge.node)
        if edge.via in DIRECT:
            direct[key] = direct.get(key, 0) + 1
            seen.setdefault(key, []).append(edge.figure_id)
        else:
            chapter[key] = chapter.get(key, 0) + 1

    out: list[Dossier] = []
    for node in nodes:
        key = (node.branch, node.name)
        branch_name, _claim, exports = status.get(node.branch, ("?", "?", 0))
        hits = direct.get(key, 0)
        candidate = node.alias or propose(node.name, symbols)
        recommendation, confidence, why = _verdict(node, candidate, exports, hits)
        out.append(
            Dossier(
                branch=node.branch,
                branch_name=branch_name,
                branch_exports=exports,
                name=node.name,
                claim=node.claim,
                alias=node.alias,
                verified=node.verified,
                direct=hits,
                chapter=chapter.get(key, 0),
                figures=tuple(sorted(seen.get(key, []))[:FIGURES_SHOWN]),
                candidate=candidate,
                lifecycle=_lifecycle(node, hits),
                recommendation=recommendation,
                confidence=confidence,
                why=why,
            )
        )
    return out


def _row(entry: Dossier) -> str:
    """One queue line. The last three columns are the person's, and stay empty."""
    figures = " ".join(entry.figures) or "—"
    candidate = entry.candidate or "—"
    return (
        f"| {entry.branch} | {entry.name} | {entry.lifecycle} | {entry.direct} | "
        f"{entry.chapter} | {figures} | `{candidate}` | {entry.recommendation} | "
        f"{entry.confidence} | | | |"
    )


HEADER = (
    "| branch | node | state | direct | chapter | figures | candidate | "
    "recommendation | confidence | **decision** | **reviewer** | **date** |\n"
    "|---|---|---|--:|--:|---|---|---|---|---|---|---|"
)


def render(entries: list[Dossier]) -> str:
    """The decision queue: all 507, evidence-backed ones ranked, the rest not."""
    backed = sorted([e for e in entries if e.direct], key=lambda e: e.key)
    unbacked = sorted([e for e in entries if not e.direct], key=lambda e: (e.branch, e.name))
    states: dict[str, int] = {}
    for entry in entries:
        states[entry.lifecycle] = states.get(entry.lifecycle, 0) + 1
    settled = sum(1 for e in entries if e.recommendation == "settled")

    lines = [
        "# Decisions — every node, and what a person has to rule on",
        "",
        "Generated by `engine/scripts/node_dossier.py`. Do not edit the first nine",
        "columns; they are derived. **The last three are yours.**",
        "",
        f"{len(entries)} nodes. {len(backed)} are reached by at least one direct figure and",
        f"are ranked below. {len(unbacked)} are reached by none and are listed after, unranked.",
        "",
        "## How to use this",
        "",
        "Fill `decision`, `reviewer` and `date` on any row you rule on, then run",
        "`python scripts/apply_decisions.py`. Accepted decisions: `implemented`",
        "(this symbol IS this capability), `rejected` (it is not, and the proposal",
        "must not return), `deferred` (not now, and why).",
        "",
        "**A decision with no reviewer is refused.** So is a machine-written one. The",
        "count of confirmed decisions is only worth reading if a machine cannot raise",
        f"it — today it is **{sum(1 for e in entries if e.verified)}**.",
        "",
        "## What the columns mean, and what they do not",
        "",
        "`recommendation` and `confidence` are a **heuristic**, not a finding. They",
        "rank what to look at first; they do not know whether a symbol is the",
        "capability. Only reading the code answers that, which is the whole reason",
        "this document exists rather than a script that decides.",
        "",
        "`direct` counts figures whose text names the node. `chapter` counts figures",
        "placed by chapter affinity — a prior about a neighbourhood, not evidence",
        "about the node. Only `direct` sorts. Chapter edges outnumber lexical ones",
        "736 to 550, so ranking on the total would rank on chapter size: ReAct",
        "(6 direct, 63 chapter) would outrank Vector Search (22, 21).",
        "",
        "`state` is the lifecycle, and the states are never collapsed:",
        "",
        "```",
        "DISCOVERED       named by the ontology, no figure reaches it",
        "EVIDENCE-BACKED  a direct figure names it, no candidate committed",
        "PROPOSED         a candidate that imports, unconfirmed",
        "REJECTED         a person said no",
        "IMPLEMENTED      a person agreed",
        "```",
        "",
        "`EXISTS ≠ RELEVANT ≠ APPROVED ≠ IMPLEMENTED`.",
        "",
        "## Where it stands",
        "",
        "| state | nodes |",
        "|---|--:|",
        *(f"| {state} | {count} |" for state, count in sorted(states.items())),
        "",
        f"{settled} node(s) are settled and may not be changed here.",
        "",
        f"**Evidence and lifecycle are different axes.** {len(backed)} nodes have a direct",
        f"figure, and only {sum(1 for e in backed if e.lifecycle == 'EVIDENCE-BACKED')} of them",
        "read `EVIDENCE-BACKED` — the rest already carry a proposal, so they sit in",
        "`PROPOSED`. MCP has 62 direct figures *and* an alias. Two numbers that look",
        "contradictory are measuring different things, which is the reason the states",
        "are not collapsed into one.",
        "",
        f"## Evidence-backed — {len(backed)} nodes, ranked by direct figures",
        "",
        HEADER,
        *(_row(entry) for entry in backed),
        "",
        f"## NO-EVIDENCE — {len(unbacked)} nodes, unranked",
        "",
        "No figure in this corpus reaches these. **That is not NO-VALUE.** Matching is",
        "lexical, so it is a statement about shared vocabulary with one book, never",
        "about whether the capability matters. `Idempotency` is here with zero figures",
        "while `omnex.pipeline.IdempotencyStore` has been in the package for months,",
        "and `Retry`, `Timeout` and `Consensus` are the same — the corpus simply did",
        "not draw pictures of them.",
        "",
        "They are unranked on purpose. Scoring them would represent an absence of",
        "evidence as a quantity of evidence. They remain candidates for cheap",
        "investigation, and a `recommendation` here still says where to look.",
        "",
        HEADER,
        *(_row(entry) for entry in unbacked),
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    nodes = load()
    branches, figures = parse(EXPORT.read_text(encoding="utf-8"))
    entries = dossiers(nodes, link(branches, figures), public_symbols())

    OUTPUT.write_text(render(entries), encoding="utf-8")

    states: dict[str, int] = {}
    actions: dict[str, int] = {}
    for entry in entries:
        states[entry.lifecycle] = states.get(entry.lifecycle, 0) + 1
        actions[entry.recommendation] = actions.get(entry.recommendation, 0) + 1
    print(f"{len(entries)} dossiers · {len(figures)} figures")
    print(f"  states       {dict(sorted(states.items()))}")
    print(f"  recommended  {dict(sorted(actions.items()))}")
    print(f"  confirmed by a person: {sum(1 for e in entries if e.verified)}")
    print(
        "\nThe recommendation column is a heuristic. Nothing here decides, and "
        "nothing here sets `verified` — only apply_decisions.py with a name may."
    )
    print(f"\nwrote {OUTPUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
