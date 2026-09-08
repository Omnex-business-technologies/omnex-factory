"""Evidence: the record that a claim was actually observed somewhere.

Competitive intelligence produced by a language model has one structural defect,
and it is not that the model is careless. It is that the output format has no
slot for provenance. "OpenSpace uses SQLite for persistence" and "OpenSpace
probably uses SQLite for persistence" render identically in a report, so a reader
cannot tell which sentences were read off a page and which were pattern-matched
from a thousand similar projects. Both look like analysis. Only one is.

So in this engine a claim is not a string. It is a `Claim`, which carries the
`Evidence` it came from, and a claim with no evidence is `Confidence.NONE` and
gets rendered as UNKNOWN rather than dropped or softened. The report generator
in `report.py` runs the finished document back through `omnex.rag.ground`, and a
sentence citing evidence that is not in the committed evidence file is refused —
the same treatment a fabricated page citation gets in P1.

## The excerpt limit is a licence boundary, not a formatting preference

`Evidence.excerpt` is capped and the cap is enforced in `__post_init__`. The
engine records metadata and short attributed quotations for analysis; it does not
vendor other people's source code into this repository under whatever licence
they chose. `Artifact.licence` is a recorded field for the same reason — "can we
absorb this?" is a question with a factual answer, and it should be answered from
data rather than from optimism.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum

__all__ = [
    "MAX_EXCERPT_CHARS",
    "Artifact",
    "Claim",
    "Confidence",
    "Evidence",
]

#: Long enough to carry a repository description and a sentence of context;
#: short enough that no accumulation of excerpts reconstitutes a source file.
MAX_EXCERPT_CHARS = 600


class Confidence(StrEnum):
    """How much weight a claim can bear.

    All four comparisons are defined explicitly for the reason documented on
    `omnex.llm.catalog.Tier`: `StrEnum` inherits `str`'s comparisons, so
    `total_ordering` fills in nothing and a partially-defined ordering silently
    falls back to comparing the words alphabetically. Here that would put
    `HIGH` below `LOW` — and a caller filtering for "at least MEDIUM" would
    quietly drop its best-supported claims and keep its worst.
    """

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @property
    def rank(self) -> int:
        return _CONFIDENCE_ORDER.index(self)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Confidence):
            return NotImplemented
        return self.rank < other.rank

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Confidence):
            return NotImplemented
        return self.rank <= other.rank

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Confidence):
            return NotImplemented
        return self.rank > other.rank

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Confidence):
            return NotImplemented
        return self.rank >= other.rank


_CONFIDENCE_ORDER = [Confidence.NONE, Confidence.LOW, Confidence.MEDIUM, Confidence.HIGH]


@dataclass(frozen=True)
class Evidence:
    """One observation, with where and when it was made.

    `fetched_on` is not decoration. Every figure in this engine is a reading of
    a page that keeps changing, so a star count without a date is not a fact,
    it is a rumour with a number in it.
    """

    url: str
    fetched_on: date
    excerpt: str
    #: What kind of statement this excerpt can support. A repository's own
    #: description is HIGH for "what it claims to do" and no evidence at all for
    #: "whether it works".
    confidence: Confidence = Confidence.MEDIUM

    def __post_init__(self) -> None:
        if not self.url:
            raise ValueError("evidence needs a url — an unattributable excerpt is not evidence")
        if len(self.excerpt) > MAX_EXCERPT_CHARS:
            raise ValueError(
                f"excerpt is {len(self.excerpt)} chars, over the {MAX_EXCERPT_CHARS} limit; "
                "this engine records short attributed quotations, not other people's source"
            )

    def cite(self) -> str:
        return f"[{self.url} · {self.fetched_on.isoformat()}]"

    def as_dict(self) -> dict[str, str]:
        return {
            "url": self.url,
            "fetched_on": self.fetched_on.isoformat(),
            "excerpt": self.excerpt,
            "confidence": str(self.confidence),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, str]) -> Evidence:
        return cls(
            url=payload["url"],
            fetched_on=date.fromisoformat(payload["fetched_on"]),
            excerpt=payload.get("excerpt", ""),
            confidence=Confidence(payload.get("confidence", "medium")),
        )


@dataclass(frozen=True)
class Claim:
    """A statement plus what backs it.

    An unsupported claim is not an error and is not discarded — a gap in the
    evidence is itself worth reporting, and pretending we know is how an
    intelligence product becomes a liability. It renders as UNKNOWN.
    """

    statement: str
    evidence: tuple[Evidence, ...] = ()

    @property
    def confidence(self) -> Confidence:
        """The best evidence available, never better than the evidence allows."""
        if not self.evidence:
            return Confidence.NONE
        return max(item.confidence for item in self.evidence)

    @property
    def supported(self) -> bool:
        return self.confidence > Confidence.NONE

    def render(self) -> str:
        if not self.supported:
            return f"UNKNOWN — {self.statement} (no public evidence found)"
        citations = " ".join(item.cite() for item in self.evidence)
        return f"{self.statement} {citations}"


@dataclass(frozen=True)
class Artifact:
    """One public project, normalised across whichever source produced it.

    GitHub reports stars, PyPI reports downloads, Hugging Face reports likes.
    They are not the same quantity and averaging them would be meaningless, so
    `popularity` carries the number and `popularity_kind` carries what it is —
    comparisons happen within a kind, never across.
    """

    id: str
    name: str
    source: str
    url: str
    description: str = ""
    language: str = ""
    licence: str = ""
    popularity: int = 0
    popularity_kind: str = "stars"
    forks: int = 0
    evidence: tuple[Evidence, ...] = ()
    tags: tuple[str, ...] = ()
    #: Free-form text mined for features — README, description, docs excerpt.
    corpus: str = ""

    @property
    def owner(self) -> str:
        return self.name.split("/")[0] if "/" in self.name else self.source

    @property
    def absorbable(self) -> bool:
        """Is the licence one we could build on without infecting our own?

        Deliberately conservative and deliberately explicit. An unknown licence
        is treated as "no", because "no LICENSE file" means all rights reserved
        rather than public domain — a distinction that has ended companies.
        """
        return self.licence.lower().split()[0] in _PERMISSIVE if self.licence else False

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "source": self.source,
            "url": self.url,
            "description": self.description,
            "language": self.language,
            "licence": self.licence,
            "popularity": self.popularity,
            "popularity_kind": self.popularity_kind,
            "forks": self.forks,
            "tags": list(self.tags),
            "corpus": self.corpus,
            "evidence": [item.as_dict() for item in self.evidence],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> Artifact:
        raw_evidence = payload.get("evidence", [])
        evidence: list[Evidence] = []
        if isinstance(raw_evidence, list):
            for item in raw_evidence:
                if isinstance(item, dict):
                    evidence.append(Evidence.from_dict({str(k): str(v) for k, v in item.items()}))
        tags = payload.get("tags", [])
        return cls(
            id=str(payload["id"]),
            name=str(payload["name"]),
            source=str(payload.get("source", "")),
            url=str(payload.get("url", "")),
            description=str(payload.get("description", "")),
            language=str(payload.get("language", "")),
            licence=str(payload.get("licence", "")),
            popularity=_as_int(payload.get("popularity")),
            popularity_kind=str(payload.get("popularity_kind", "stars")),
            forks=_as_int(payload.get("forks")),
            evidence=tuple(evidence),
            tags=tuple(str(t) for t in tags) if isinstance(tags, list) else (),
            corpus=str(payload.get("corpus", "")),
        )


_PERMISSIVE = frozenset({"mit", "apache", "apache-2.0", "bsd", "bsd-3-clause", "isc", "unlicense"})


def _as_int(value: object) -> int:
    """Coerce a JSON field to int without trusting it. Absent or junk reads zero."""
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, (str, float)):
        try:
            return int(float(value))
        except ValueError:
            return 0
    return 0


@dataclass
class EvidenceFile:
    """The committed, dated record every report is generated from.

    Committed rather than fetched at render time, for the same reason
    `suites/finground_corpus.json` is committed: a report whose numbers come
    from a live network call cannot be reproduced by a reader, and a
    conclusion nobody can re-derive is an opinion.
    """

    fetched_on: date
    artifacts: dict[str, Artifact] = field(default_factory=dict)

    def add(self, artifact: Artifact) -> None:
        self.artifacts[artifact.id] = artifact

    def get(self, artifact_id: str) -> Artifact | None:
        return self.artifacts.get(artifact_id)

    def as_dict(self) -> dict[str, object]:
        return {
            "fetched_on": self.fetched_on.isoformat(),
            "artifacts": [a.as_dict() for a in self.artifacts.values()],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> EvidenceFile:
        raw = payload.get("artifacts", [])
        file = cls(fetched_on=date.fromisoformat(str(payload["fetched_on"])))
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    file.add(Artifact.from_dict(item))
        return file
