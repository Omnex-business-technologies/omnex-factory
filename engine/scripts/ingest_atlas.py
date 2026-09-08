"""Parse the Universal AI OS export into a committed manifest, and reconcile it.

    python scripts/ingest_atlas.py

The export is one 760 KB markdown file describing 509 figures extracted from
*AI Engineering: System Design Patterns for LLMs, RAG and Agents*, mapped onto
28 branches and 507 nodes. It arrived by hand because the host serving it is
refused by this environment's egress policy; the file is committed beside this
script so the parse is reproducible by anyone, from the same bytes.

## What is taken as evidence and what is not

Taken: figure counts per branch, bounding boxes, sha, duplicate groups, page and
chapter, OCR text, and the node names. Those are records of something somebody
extracted, and they can be checked against the source.

**Not taken: the n/10 completeness scores.** The system that wrote each node also
scored it, which is the frozen-criteria problem with the anchor removed — the
same reason `ontology_map.py` has no completeness score of its own. The export is
candid about this in its own numbers: 350 of its 509 mappings sit in the review
queue rather than auto-accept, so most of them are the author's judgement
awaiting a check, not a measurement.

## Why the reconciliation is the point

Neither document alone says anything useful about priority. The export knows
where the *field's* attention is — 184 of 509 figures touch the protocol fabric
— and knows nothing about this repository. `ontology/branches.json`
knows what `engine/` actually implements and nothing about how much of the
literature each branch carries.

Joined, they answer a question neither can: **where does the corpus concentrate
while engine/ has nothing?** That is an argument from evidence rather than from
whoever wrote the roadmap, and it is the one number here worth acting on.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from dataclasses import field as dcfield
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
CORPUS = REPO / "corpus" / "universal-ai-os"
EXPORT = CORPUS / "export.md"
MANIFEST = CORPUS / "manifest.json"
RECONCILIATION = CORPUS / "RECONCILIATION.md"
BRANCHES = ROOT / "ontology" / "branches.json"

#: The export's own totals, asserted rather than trusted. A regex that silently
#: matches 400 of 509 records produces a smaller manifest and no error at all,
#: which is the failure mode this whole repository is built to refuse.
EXPECTED_FIGURES = 509
EXPECTED_NODES = 507
EXPECTED_BRANCHES = 28

_BRANCH_RE = re.compile(
    r"^### ([IVXL]+)\. (.+?)\n\n\*Layer:\* (\S+) · \*Nodes:\* (\d+) · "
    r"\*Mapped figures:\* (\d+) · \*ID:\* `([^`]+)`",
    re.M,
)
_FIGURE_RE = re.compile(r"^### (fig_\d+) — (.*?)$", re.M)
_XREF_RE = re.compile(r"^- \*\*([IVXL]+)\. .+?\*\* — \d+ figures: (.*?)$", re.M)
_FIG_ID_RE = re.compile(r"fig_\d+")
_FIELD_RES = {
    "page": re.compile(r"\*\*Page:\*\* (\d+) \(PDF page (\d+)\)"),
    "chapter": re.compile(r"\*\*Chapter:\*\* (.+?)$", re.M),
    "bbox": re.compile(r"\*\*BBox:\*\* \[([\d.,\s-]+)\]"),
    "composition": re.compile(r"\*\*Composition:\*\* (\S+)"),
    "role": re.compile(r"\*\*Role:\*\* (\S+)"),
    "quality": re.compile(r"\*\*Quality:\*\* ([\d.]+)"),
    "primary": re.compile(r"\*\*Primary branch:\*\* (\S+)"),
    "confidence": re.compile(r"\*\*Confidence:\*\* ([\d.]+)"),
    "sha": re.compile(r"sha `([0-9a-f]+)`"),
    "dup": re.compile(r"dup group `(\w+)`"),
    "caption": re.compile(r"\*\*Caption:\*\* (.+?)$", re.M),
    "mapping": re.compile(r"\*\*Mapping:\*\* (.+?)$", re.M),
    "ocr": re.compile(r"\*\*OCR:\*\* (.+?)$", re.M),
}


@dataclass
class Branch:
    """One branch as the export describes it."""

    id: str
    name: str
    layer: str
    slug: str
    nodes: int
    figures: int
    node_names: list[str] = field(default_factory=list)
    #: Every figure that maps to this branch at all, not only the ones for which
    #: it is the primary. A figure has one primary and touches several branches,
    #: so `figures` sums to 509 across the tree and `touched` does not — it is a
    #: count of edges, not of figures, and reading it as the latter double-counts.
    touched: list[str] = field(default_factory=list)

    @property
    def touch_count(self) -> int:
        return len(self.touched)


@dataclass
class Figure:
    """One extracted figure, with everything needed to find it in the source."""

    id: str
    title: str
    page: int
    pdf_page: int
    chapter: str
    bbox: list[float]
    composition: str
    role: str
    quality: float
    primary_branch: str
    confidence: float
    sha: str
    duplicate_group: str
    caption: str
    ocr: str
    #: Every branch the exporter scored for this figure, strongest first.
    #: The export publishes three; earlier versions of this parser read the
    #: primary and dropped the rest, which threw away the only per-figure
    #: signal in the document about where else it belongs.
    mappings: list[tuple[str, float]] = dcfield(default_factory=list)

    @property
    def band(self) -> str:
        """Recomputed here, never read from the export.

        The thresholds are `omnex.rag.figures.Band` — the export happens to use
        the same ones, and "happens to" is exactly why this is derived rather
        than copied across.
        """
        if self.confidence >= 0.85:
            return "auto"
        if self.confidence >= 0.5:
            return "review"
        return "weak"


def parse(text: str) -> tuple[list[Branch], list[Figure]]:
    """Read the export. Every count is asserted against the export's own totals."""
    branches = [
        Branch(id=m[0], name=m[1], layer=m[2], slug=m[5], nodes=int(m[3]), figures=int(m[4]))
        for m in _BRANCH_RE.findall(text)
    ]

    # Node names live in the per-branch tables; the first column of each row.
    #
    # The block must end at the next heading of EITHER level. Bounding it only by
    # the next `###` let the last branch run past the end of section 4 and into
    # the figure index, collecting 510 figure ids as though they were nodes —
    # 1017 parsed names against 507 declared. It went unnoticed because
    # EXPECTED_NODES is summed from the branch HEADERS while the linker consumes
    # the parsed NAMES: the assertion and the consumer read different sources, so
    # the count agreed with itself and with nothing else.
    for branch in branches:
        start = text.index(f"### {branch.id}. {branch.name}")
        rest = text[start:]
        stops = [pos for pos in (rest.find("\n### ", 1), rest.find("\n## ", 1)) if pos > 0]
        end = min(stops) if stops else -1
        block = rest[: end if end > 0 else len(rest)]
        branch.node_names = [
            row.split("|")[1].strip()
            for row in block.splitlines()
            if row.startswith("| ") and not row.startswith("| ---") and "| Node |" not in row
        ]

    # Section 7 lists, per branch, every figure that maps to it at all. The
    # branch headers in section 4 count only the figures whose PRIMARY branch it
    # is. Both are true and they answer different questions; using the narrower
    # one alone understated the protocol fabric by a factor of two and a half.
    by_id = {b.id: b for b in branches}
    for bid, listing in _XREF_RE.findall(text):
        if bid in by_id:
            by_id[bid].touched = _FIG_ID_RE.findall(listing)

    figures: list[Figure] = []
    marks = list(_FIGURE_RE.finditer(text))
    for index, mark in enumerate(marks):
        stop = marks[index + 1].start() if index + 1 < len(marks) else len(text)
        block = text[mark.start() : stop]
        figures.append(_figure_from(mark.group(1), mark.group(2), block))

    return branches, figures


def _figure_from(fid: str, title: str, block: str) -> Figure:
    def one(key: str, default: str = "") -> str:
        found = _FIELD_RES[key].search(block)
        return found.group(1).strip() if found else default

    page = _FIELD_RES["page"].search(block)
    bbox_raw = one("bbox")
    return Figure(
        id=fid,
        title=title.strip(),
        page=int(page.group(1)) if page else -1,
        pdf_page=int(page.group(2)) if page else -1,
        chapter=one("chapter"),
        bbox=[float(v) for v in bbox_raw.split(",")] if bbox_raw else [],
        composition=one("composition"),
        role=one("role"),
        quality=float(one("quality", "0") or 0),
        primary_branch=one("primary"),
        confidence=float(one("confidence", "0") or 0),
        sha=one("sha"),
        duplicate_group=one("dup"),
        caption=one("caption"),
        ocr=one("ocr"),
        mappings=_mappings(one("mapping")),
    )


def _mappings(raw: str) -> list[tuple[str, float]]:
    """Parse `Name (0.74) · Other (0.48)` into scored branch names."""
    out: list[tuple[str, float]] = []
    for part in raw.split("·"):
        found = re.match(r"\s*(.+?)\s*\(([\d.]+)\)\s*$", part)
        if found:
            out.append((found.group(1).strip(), float(found.group(2))))
    return out


def reconcile(branches: list[Branch], figures: list[Figure]) -> str:
    """Join corpus weight against what `engine/` claims, and rank by the gap."""
    claims: dict[str, dict[str, Any]] = {
        b["id"]: b for b in json.loads(BRANCHES.read_text(encoding="utf-8"))["branches"]
    }
    by_band: dict[str, int] = {}
    for figure in figures:
        by_band[figure.band] = by_band.get(figure.band, 0) + 1

    lines = [
        "# Corpus weight against engine coverage",
        "",
        "Generated by `engine/scripts/ingest_atlas.py`. Do not edit.",
        "",
        f"{len(figures)} figures over {len(branches)} branches and "
        f"{sum(b.nodes for b in branches)} nodes, from *AI Engineering: System Design "
        "Patterns for LLMs, RAG and Agents*.",
        "",
        "Bands recomputed from each figure's confidence rather than read from the "
        f"export: {by_band.get('auto', 0)} auto-accept, {by_band.get('review', 0)} "
        f"review, {by_band.get('weak', 0)} weak. Most mappings are the export "
        "author's judgement awaiting a check — which is why the figure COUNTS are "
        "used below and the mappings are not.",
        "",
        "The n/10 completeness scores in the export are deliberately ignored. The "
        "system that wrote each node also scored it.",
        "",
        "Two counts per branch, because the export carries two and they answer "
        "different questions. **Primary** is the figures for which this branch is "
        "the main subject; it sums to 509. **Touches** is every figure that maps "
        "to the branch at all — a figure has one primary and several mappings, so "
        "this counts edges and sums to far more. Ranking on primary alone "
        "understated the protocol fabric by a factor of two and a half.",
        "",
        "| # | Branch | Primary | Touches | Nodes | engine/ claim | Symbols |",
        "|---|---|--:|--:|--:|---|--:|",
    ]

    ordered = sorted(branches, key=lambda b: -b.touch_count)
    for branch in ordered:
        claim = claims.get(branch.id)
        verdict = claim["claim"] if claim else "—"
        symbols = len(claim["symbols"]) if claim else 0
        lines.append(
            f"| {branch.id} | {branch.name} | {branch.figures} | {branch.touch_count} | "
            f"{branch.nodes} | {verdict} | {symbols} |"
        )

    heavy_and_absent = [
        b for b in ordered if b.touch_count >= 30 and claims.get(b.id, {}).get("claim") == "gap"
    ]
    lines += [
        "",
        "## What the join says that neither side could",
        "",
    ]
    if heavy_and_absent:
        for branch in heavy_and_absent:
            lines.append(
                f"- **{branch.id} {branch.name}** is touched by {branch.touch_count} "
                f"of {len(figures)} figures — {branch.touch_count / len(figures):.0%} "
                f"of the corpus, and primary for {branch.figures} of them — while "
                "`engine/` has no code for it at all. This is the largest hole by "
                "evidence rather than by opinion."
            )
    else:
        lines.append("- No branch is both corpus-heavy and entirely absent from `engine/`.")

    lines += [
        "",
        "Branches with **zero** figures are not thereby unimportant. The corpus is "
        "one book with one author's emphasis: it says nothing about business "
        "automation, revenue or self-improvement, and a reader who treated zero as "
        "a verdict would delete the half of this platform that earns money.",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    text = EXPORT.read_text(encoding="utf-8")
    branches, figures = parse(text)

    problems = []
    if len(figures) != EXPECTED_FIGURES:
        problems.append(f"parsed {len(figures)} figures, export declares {EXPECTED_FIGURES}")
    if len(branches) != EXPECTED_BRANCHES:
        problems.append(f"parsed {len(branches)} branches, export declares {EXPECTED_BRANCHES}")
    total_nodes = sum(b.nodes for b in branches)
    if total_nodes != EXPECTED_NODES:
        problems.append(
            f"branch headers total {total_nodes} nodes, export declares {EXPECTED_NODES}"
        )
    for branch in branches:
        if len(branch.node_names) != branch.nodes:
            problems.append(
                f"branch {branch.id} declares {branch.nodes} nodes, "
                f"{len(branch.node_names)} names parsed"
            )

    declared = sum(b.figures for b in branches)
    if declared != EXPECTED_FIGURES:
        problems.append(
            f"branch headers total {declared} figures, export declares {EXPECTED_FIGURES}"
        )

    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        return 1

    MANIFEST.write_text(
        json.dumps(
            {
                "source": "AI Engineering: System Design Patterns for LLMs, RAG and Agents",
                "export": "corpus/universal-ai-os/export.md",
                "branches": [asdict(b) | {"touch_count": b.touch_count} for b in branches],
                "figures": [asdict(f) | {"band": f.band} for f in figures],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    RECONCILIATION.write_text(reconcile(branches, figures), encoding="utf-8")

    print(f"{len(figures)} figures · {len(branches)} branches · {total_nodes} nodes")
    print(f"wrote {MANIFEST.relative_to(REPO)}")
    print(f"wrote {RECONCILIATION.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
