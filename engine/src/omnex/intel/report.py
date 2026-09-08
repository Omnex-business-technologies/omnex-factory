"""Rendering, and the verification pass the documents have to survive.

## What was planned, what was measured, and what this actually does

The intention was to gate every rendered sentence through `omnex.rag.ground` —
the same verifier that decides whether a RAG answer may be shown to a customer —
and refuse anything it called unsupported. Measured against real report prose,
that gate does not work, and it fails in the expensive direction:

    supported            "OpenSpace is a skill management layer for AI agents."
    unsupported          "OpenSpace uses SQLite for persistence and LiteLLM
                          for model access."                       ← TRUE
    unsupported          "OpenSpace has 40,000 enterprise customers."
    fabricated_citation  "OpenSpace is written in Python. [p. 9]"

The second line is a true statement, drawn from the same excerpt, marked
unsupported. The reason is structural rather than a threshold that wants
nudging: `Grounder` requires content-word overlap because it was built for
EXTRACTIVE answers, where the reply is a restatement of the source. Report prose
is SYNTHESIS — it aggregates, compares and infers across artifacts, so overlap
with any single excerpt is naturally low. Lowering `min_overlap` until the true
sentence passes would also pass the fabricated one, since "40,000 enterprise
customers" shares just as few words with the source as the truth does.

So the verdicts are used for what each one can actually carry:

**`fabricated_citation` is a hard refusal.** A citation pointing at evidence
that is not in the committed file is wrong with no interpretation available, and
it is the failure mode generated intelligence actually exhibits — the plausible
URL for a page nobody fetched. This gate is exact and has no false positives.

**Numeric claims are checked against the evidence file directly.** Every figure
attributed to an artifact must equal the recorded value. A star count drifting
between the evidence and the prose is the other real failure, and comparing
against structured data catches it where comparing against prose cannot.

**`unsupported` becomes a review flag, not a deletion.** It is reported with the
sentence so a human can look, and it is explicitly not treated as a verdict of
falsehood. Reporting a check as stronger than it measured is the failure this
whole package exists to prevent; it would be an odd place to start committing it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..rag.ground import Grounder, GroundingVerdict
from ..vectors.types import Chunk
from .evidence import Artifact, Claim, Confidence, EvidenceFile

__all__ = [
    "Finding",
    "Verification",
    "render_claims",
    "verify_document",
]

#: `[https://example.com/x · 2026-08-05]` as emitted by `Evidence.cite()`.
_CITATION = re.compile(r"\[(?P<url>https?://[^\s\]]+)\s*·\s*(?P<date>\d{4}-\d{2}-\d{2})\]")
#: Numbers with optional thousands separators, as they appear in report prose.
_NUMBER = re.compile(r"\b\d[\d,]*\b")


@dataclass(frozen=True)
class Finding:
    """One problem with a rendered document."""

    kind: str
    sentence: str
    detail: str

    @property
    def fatal(self) -> bool:
        """Does this block publication?

        Only citation fabrication and numeric contradiction do. A review flag
        that blocked publication would be indistinguishable from a false claim,
        which is how a verification pass gets turned off.
        """
        return self.kind in {"fabricated_citation", "number_mismatch"}

    def report(self) -> str:
        marker = "REFUSED" if self.fatal else "review"
        return f"  [{marker}] {self.kind}: {self.detail}\n            {self.sentence[:110]}"


@dataclass
class Verification:
    checked_sentences: int = 0
    citations_checked: int = 0
    findings: list[Finding] = field(default_factory=list)

    @property
    def fatal(self) -> list[Finding]:
        return [f for f in self.findings if f.fatal]

    @property
    def flags(self) -> list[Finding]:
        return [f for f in self.findings if not f.fatal]

    @property
    def publishable(self) -> bool:
        return not self.fatal

    def report(self) -> str:
        lines = [
            f"{self.checked_sentences} sentences, {self.citations_checked} citations checked — "
            f"{len(self.fatal)} refused, {len(self.flags)} flagged for review",
        ]
        for finding in self.fatal + self.flags:
            lines.append(finding.report())
        return "\n".join(lines)


def verify_document(text: str, evidence: EvidenceFile) -> Verification:
    """Check a rendered report against the evidence it was generated from.

    Two exact checks and one advisory one. The exact checks are the ones a
    reader cannot perform for themselves without re-fetching everything, which
    is precisely why they belong in the pipeline rather than in a review
    checklist nobody runs.
    """
    result = Verification()
    known_urls = {
        item.url for artifact in evidence.artifacts.values() for item in artifact.evidence
    } | {artifact.url for artifact in evidence.artifacts.values()}
    recorded_numbers = _recorded_numbers(evidence)

    for sentence in _sentences(text):
        citations = _CITATION.findall(sentence)
        if not citations:
            continue
        result.checked_sentences += 1

        for url, _cited_date in citations:
            result.citations_checked += 1
            if url not in known_urls:
                result.findings.append(
                    Finding(
                        "fabricated_citation",
                        sentence,
                        f"{url} is not in the committed evidence file",
                    )
                )

        # The claim is the sentence WITHOUT its citation. Leaving the citation
        # in means its date is checked as if it were an asserted figure — the
        # 2026 in `· 2026-08-05` reads as the claim "2026", which no evidence
        # record contains, and every correctly-cited sentence is refused. This
        # is the same trap `omnex.rag.ground._without_citations` exists for; it
        # bites once per citation format.
        for raw in _NUMBER.findall(_CITATION.sub(" ", sentence)):
            value = int(raw.replace(",", ""))
            # Small numbers are counts of things in the report itself — "3
            # layers", "2 of 5 domains" — and are computed rather than cited.
            # Only figures large enough to be a fetched metric are checked.
            if value < 100:
                continue
            if value not in recorded_numbers:
                result.findings.append(
                    Finding(
                        "number_mismatch",
                        sentence,
                        f"{value:,} appears in no evidence record",
                    )
                )

    return result


def _recorded_numbers(evidence: EvidenceFile) -> set[int]:
    """Every figure the evidence file actually asserts, plus those in excerpts."""
    numbers: set[int] = set()
    for artifact in evidence.artifacts.values():
        numbers.add(artifact.popularity)
        numbers.add(artifact.forks)
        for item in artifact.evidence:
            for raw in _NUMBER.findall(item.excerpt):
                numbers.add(int(raw.replace(",", "")))
        for raw in _NUMBER.findall(artifact.description):
            numbers.add(int(raw.replace(",", "")))
    return numbers


#: Stand-in for a citation while sentences are being split. A citation contains
#: dots (in the URL and the date) and is preceded by one, so splitting naively
#: both cuts INSIDE it and detaches it from the claim it belongs to — leaving an
#: orphan "[url · date]" that is checked as if it were a sentence, and a claim
#: that now appears uncited. Masked, split, restored.
_MASK = "\x00"


def _sentences(text: str) -> list[str]:
    """Split prose, keeping citations attached and markdown table rows whole.

    A table row is one record, not five sentences, and splitting it on periods
    turns every version number into a sentence boundary.
    """
    out: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("|"):
            out.append(stripped)
            continue

        citations: list[str] = []

        def _hide(match: re.Match[str], sink: list[str] = citations) -> str:
            sink.append(match.group(0))
            return f"{_MASK}{len(sink) - 1}{_MASK}"

        masked = _CITATION.sub(_hide, stripped)
        # Never split INTO a citation. A citation trails the sentence it
        # supports — "claim. [url · date]" — so a plain sentence break leaves the
        # claim looking uncited (and therefore unchecked) and the citation
        # standing alone as a sentence asserting nothing. The negative lookahead
        # keeps the pair together while still breaking after it.
        for part in re.split(rf"(?<=[.!?])\s+(?!{_MASK})", masked):
            piece = part.strip()
            if not piece:
                continue
            for index, citation in enumerate(citations):
                piece = piece.replace(f"{_MASK}{index}{_MASK}", citation)
            out.append(piece)
    return out


def render_claims(claims: list[Claim], minimum: Confidence = Confidence.LOW) -> str:
    """Render claims, keeping unsupported ones visible as UNKNOWN.

    Dropping them would be the tidier output and the worse product: a gap in the
    evidence is a finding, and a report that silently omits what it could not
    establish reads as more complete than it is.
    """
    lines: list[str] = []
    for claim in claims:
        if claim.confidence >= minimum or not claim.supported:
            lines.append(f"- {claim.render()}")
    return "\n".join(lines)


def ground_prose(text: str, artifact: Artifact) -> list[tuple[str, GroundingVerdict]]:
    """Advisory pass with the RAG grounder, for the record.

    Kept because the `fabricated_citation` verdict is genuinely exact and worth
    having a second implementation of, and because a future extractive section —
    one that quotes rather than synthesises — would be gated by this properly.
    Its `unsupported` verdicts are advisory here, for the reason in the module
    docstring, and callers are expected to treat them that way.
    """
    chunks = [
        Chunk(id=f"{artifact.id}#{index}", text=item.excerpt, doc_id=artifact.id, page=index + 1)
        for index, item in enumerate(artifact.evidence)
    ]
    if not chunks:
        return []
    checked = Grounder().check(text, chunks)
    return [(check.sentence, check.verdict) for check in checked.checks]
