"""Figure-level anchoring: a citation that points at a diagram, not at a page.

`ingest.py` carries page anchors all the way to the chunk, which is enough for
prose. It is not enough for a document whose argument is in its figures — a
reader told "page 214" still has to find which of the four diagrams on it was
meant, and an answer that cites a page containing a contradicting diagram is
indistinguishable from one that cites the right one.

## Why extraction is not `pdfimages`

Pulling embedded rasters recovers photographs and screenshots. It recovers none
of this:

- a diagram drawn entirely in vector strokes, which has no embedded image at all
- a composite of a background raster, six vector arrows and twelve text labels,
  which comes out as nineteen unrelated objects
- a figure clipped by a mask, which comes out as the unclipped original

So this module works in two layers. **Layer A** takes every object the page
declares — raster, vector, text run — with its coordinates, and keeps all of
them. **Layer B** clusters those objects into regions that are figures, and the
region is then re-rendered from the page and cropped. What comes out is what a
reader sees, which is not the same as what the file stores.

## The rules that are structural rather than tuned

**Text alone is never a figure.** A caption joins a region that already has a
raster or vector member; a run of text touching only other text is prose. Without
that rule every paragraph in the document becomes a figure with a high score,
and the manifest that results is worse than no manifest.

**A filter accounts for every object it drops.** `RegionReport.reconciles()` is
the same guarantee `intel.FilterReport` makes, for the same reason: a pipeline
that loses objects to an off-by-one reports a clean-looking result.

**Duplicates are grouped, never deleted.** The same figure reprinted in a later
chapter is evidence about the document's structure. `duplicate_group` records the
relationship and both records survive.

**A band is computed from a score, never assigned.** `Band.of()` is the only way
to get one, so a caller cannot mark a weak mapping as automatic — which is the
failure that turns a review queue into a rubber stamp.

## What this does not do

Clustering is geometric. Two figures stacked with no gap, sharing one caption
band, merge into a single region — `test_two_figures_sharing_a_caption_band_
merge` asserts that they do. It is a stated limitation kept as a passing test,
not a bug to be quietly tuned away: the fix is a layout model, and a proximity
threshold nudged until the one known case passes will fail differently on the
next document.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol

from ..core.clock import Clock, SystemClock
from ..core.errors import ConfigurationError, ValidationFailed

__all__ = [
    "BBox",
    "Band",
    "Composition",
    "FigureRecord",
    "FigureRegion",
    "Manifest",
    "ObjectKind",
    "PageObject",
    "PageSource",
    "PerceptualHasher",
    "RegionRenderer",
    "RegionReport",
    "TextRecognizer",
    "cluster_page",
    "duplicate_groups",
    "extract_figures",
    "hamming",
]

#: Objects whose padded boxes touch are treated as one figure. In points, at 72
#: per inch, so this is a shade under 3mm — wide enough to catch a label sitting
#: just off a diagram, narrow enough not to swallow the next paragraph.
DEFAULT_PAD = 8.0

#: Below this, a region is a bullet glyph or a rule, not a figure.
MIN_AREA = 2_500.0

#: Perceptual hashes within this many bits are the same picture. 64-bit phash;
#: 5 is the conventional near-duplicate threshold and is stated here rather than
#: buried at a call site so it can be argued with.
PHASH_DISTANCE = 5


class ObjectKind(StrEnum):
    """What a page declares an object to be, before we decide what it means."""

    RASTER = "raster"
    VECTOR = "vector"
    TEXT = "text"


class Composition(StrEnum):
    """What a finished region turned out to be made of.

    Recorded because it explains a later failure: a `VECTOR` region that OCRs to
    nothing is normal, while a `RASTER` one that does is a rendering problem.
    """

    RASTER = "raster"
    VECTOR = "vector"
    HYBRID = "hybrid"


class Band(StrEnum):
    """How much a mapping can be trusted, computed from its score.

    All four comparisons are defined explicitly for the reason documented on
    `omnex.llm.catalog.Tier` and `omnex.intel.Confidence`: `StrEnum` inherits
    `str`'s comparisons, so `total_ordering` fills in nothing and the ordering
    silently falls back to alphabetical — which here would sort `AUTO` below
    `REVIEW` below `WEAK` and invert every "at least" filter in the codebase.
    """

    WEAK = "weak"
    REVIEW = "review"
    AUTO = "auto"

    @classmethod
    def of(cls, score: float) -> Band:
        """The only constructor. A band is never handed in by a caller.

        A mapping the extractor is unsure about must arrive in the review queue
        no matter who is calling, because the caller that would rather not be
        interrupted is exactly the one whose mappings need looking at.
        """
        if not 0.0 <= score <= 1.0:
            raise ValidationFailed(f"score {score} is outside 0.0-1.0", score=score)
        if score >= 0.85:
            return cls.AUTO
        if score >= 0.5:
            return cls.REVIEW
        return cls.WEAK

    @property
    def rank(self) -> int:
        return _BAND_ORDER.index(self)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Band):
            return NotImplemented
        return self.rank < other.rank

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Band):
            return NotImplemented
        return self.rank <= other.rank

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Band):
            return NotImplemented
        return self.rank > other.rank

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Band):
            return NotImplemented
        return self.rank >= other.rank


_BAND_ORDER = (Band.WEAK, Band.REVIEW, Band.AUTO)


@dataclass(frozen=True)
class BBox:
    """A rectangle in PDF user space, origin bottom-left, units of 1/72 inch."""

    x0: float
    y0: float
    x1: float
    y1: float

    def __post_init__(self) -> None:
        if self.x1 < self.x0 or self.y1 < self.y0:
            raise ValidationFailed(
                f"bbox is inside out: ({self.x0}, {self.y0}) to ({self.x1}, {self.y1})"
            )

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def area(self) -> float:
        return self.width * self.height

    def padded(self, pad: float) -> BBox:
        return BBox(self.x0 - pad, self.y0 - pad, self.x1 + pad, self.y1 + pad)

    def touches(self, other: BBox, pad: float = 0.0) -> bool:
        a, b = self.padded(pad), other
        return not (a.x1 < b.x0 or b.x1 < a.x0 or a.y1 < b.y0 or b.y1 < a.y0)

    def merged_with(self, other: BBox) -> BBox:
        return BBox(
            min(self.x0, other.x0),
            min(self.y0, other.y0),
            max(self.x1, other.x1),
            max(self.y1, other.y1),
        )

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.x0, self.y0, self.x1, self.y1)


@dataclass(frozen=True)
class PageObject:
    """One thing the page declares, before any judgement about what it is for."""

    kind: ObjectKind
    bbox: BBox
    text: str = ""

    @property
    def is_graphic(self) -> bool:
        return self.kind in (ObjectKind.RASTER, ObjectKind.VECTOR)


@dataclass(frozen=True)
class FigureRegion:
    """A cluster of page objects that together are one figure."""

    page: int
    bbox: BBox
    members: tuple[PageObject, ...]

    @property
    def composition(self) -> Composition:
        kinds = {m.kind for m in self.members if m.is_graphic}
        if kinds == {ObjectKind.RASTER}:
            return Composition.RASTER
        if kinds == {ObjectKind.VECTOR}:
            return Composition.VECTOR
        return Composition.HYBRID

    @property
    def label_text(self) -> str:
        """Text runs caught inside the region — captions, axis labels, legends."""
        return " ".join(m.text for m in self.members if m.kind is ObjectKind.TEXT and m.text)


@dataclass
class RegionReport:
    """Every object that went in, accounted for.

    Filtering is not deletion: an object that did not become part of a figure is
    counted under the reason it was set aside, and the totals must reconcile.
    """

    received: int = 0
    clustered: int = 0
    text_only: int = 0
    below_min_area: int = 0

    @property
    def set_aside(self) -> int:
        return self.text_only + self.below_min_area

    def reconciles(self) -> bool:
        return self.received == self.clustered + self.set_aside

    def report(self) -> str:
        share = self.set_aside / self.received if self.received else 0.0
        return (
            f"{self.received} objects in, {self.clustered} in figures, "
            f"{self.set_aside} set aside ({share:.1%}): "
            f"{self.text_only} prose, {self.below_min_area} below minimum area"
        )


def cluster_page(
    objects: Sequence[PageObject],
    page: int,
    *,
    pad: float = DEFAULT_PAD,
    min_area: float = MIN_AREA,
    report: RegionReport | None = None,
) -> list[FigureRegion]:
    """Group a page's objects into figure regions.

    Repeatedly merges clusters whose padded boxes touch, until nothing more
    merges — so a chain of a diagram, its arrow and its label ends as one region
    even though the diagram and the label never touch each other directly.

    A cluster containing no raster or vector member is prose and is set aside,
    which is the rule that keeps the manifest from filling with paragraphs.
    """
    tally = report if report is not None else RegionReport()
    tally.received += len(objects)

    clusters: list[tuple[BBox, list[PageObject]]] = [(obj.bbox, [obj]) for obj in objects]

    merged = True
    while merged:
        merged = False
        for i in range(len(clusters)):
            if not clusters[i][1]:
                continue
            for j in range(i + 1, len(clusters)):
                if not clusters[j][1]:
                    continue
                if clusters[i][0].touches(clusters[j][0], pad):
                    clusters[i] = (
                        clusters[i][0].merged_with(clusters[j][0]),
                        clusters[i][1] + clusters[j][1],
                    )
                    clusters[j] = (clusters[j][0], [])
                    merged = True

    regions: list[FigureRegion] = []
    for bbox, members in clusters:
        if not members:
            continue
        if not any(m.is_graphic for m in members):
            tally.text_only += len(members)
            continue
        if bbox.area < min_area:
            tally.below_min_area += len(members)
            continue
        tally.clustered += len(members)
        regions.append(FigureRegion(page=page, bbox=bbox, members=tuple(members)))

    regions.sort(key=lambda r: (-r.bbox.y1, r.bbox.x0))
    return regions


def hamming(left: str, right: str) -> int:
    """Bit distance between two hex perceptual hashes of equal width."""
    if len(left) != len(right):
        raise ValidationFailed(
            f"perceptual hashes of different widths: {len(left)} vs {len(right)}"
        )
    return (int(left, 16) ^ int(right, 16)).bit_count()


def duplicate_groups(
    records: Sequence[FigureRecord], *, distance: int = PHASH_DISTANCE
) -> dict[str, str]:
    """Map every figure id to the id of its group's first member.

    Grouping, never deletion. The same diagram reprinted three chapters later is
    a fact about the document worth keeping — and the caller who wants one of
    each can collapse on this key, while the caller auditing the source still
    sees all three.

    Identical bytes group by sha256 first, which is exact. Near-identical
    renders — the same figure at a different scale — group by perceptual hash.
    """
    leaders: list[FigureRecord] = []
    assignment: dict[str, str] = {}

    for record in records:
        for leader in leaders:
            same_bytes = record.sha256 == leader.sha256
            close = bool(record.phash) and bool(leader.phash)
            if same_bytes or (close and hamming(record.phash, leader.phash) <= distance):
                assignment[record.figure_id] = leader.figure_id
                break
        else:
            leaders.append(record)
            assignment[record.figure_id] = record.figure_id

    return assignment


@dataclass
class FigureRecord:
    """One figure, with everything needed to find it in the source again."""

    figure_id: str
    doc_id: str
    page: int
    bbox: BBox
    composition: Composition
    score: float
    sha256: str = ""
    phash: str = ""
    ocr_text: str = ""
    caption: str = ""
    heading: str = ""
    duplicate_group: str = ""

    @property
    def band(self) -> Band:
        """Derived, so it cannot disagree with the score that produced it."""
        return Band.of(self.score)

    @property
    def needs_review(self) -> bool:
        return self.band < Band.AUTO

    def as_dict(self) -> dict[str, Any]:
        return {
            "figure_id": self.figure_id,
            "doc_id": self.doc_id,
            "page": self.page,
            "bbox": list(self.bbox.as_tuple()),
            "composition": str(self.composition),
            "score": self.score,
            "band": str(self.band),
            "sha256": self.sha256,
            "phash": self.phash,
            "ocr_text": self.ocr_text,
            "caption": self.caption,
            "heading": self.heading,
            "duplicate_group": self.duplicate_group,
        }


@dataclass
class Manifest:
    """The committed record of an extraction run.

    Images live outside the repository — a few thousand 300-DPI crops are
    permanent weight in git history — so this is the artifact that is versioned,
    and `sha256` is what ties a record back to the file it describes.
    """

    doc_id: str
    created_at: str
    records: list[FigureRecord] = field(default_factory=list)
    report: RegionReport = field(default_factory=RegionReport)

    @property
    def review_queue(self) -> list[FigureRecord]:
        """Everything below AUTO, in the order a human should work through it."""
        pending = [r for r in self.records if r.needs_review]
        pending.sort(key=lambda r: (r.score, r.page))
        return pending

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(
            {
                "doc_id": self.doc_id,
                "created_at": self.created_at,
                "figures": [r.as_dict() for r in self.records],
                "objects": {
                    "received": self.report.received,
                    "clustered": self.report.clustered,
                    "text_only": self.report.text_only,
                    "below_min_area": self.report.below_min_area,
                    "reconciles": self.report.reconciles(),
                },
            },
            indent=indent,
            sort_keys=True,
        )


class PageSource(Protocol):
    """Layer A. Everything the page declares, with coordinates, nothing dropped."""

    def page_count(self) -> int: ...

    def objects(self, page: int) -> Sequence[PageObject]: ...


class RegionRenderer(Protocol):
    """Layer B. Re-render a region from the page rather than lifting an object."""

    def render(self, page: int, bbox: BBox, dpi: int) -> bytes: ...


class TextRecognizer(Protocol):
    """OCR, so a diagram is findable by the words drawn inside it."""

    def text_of(self, image: bytes) -> str: ...


class PerceptualHasher(Protocol):
    """A hash that survives rescaling, for near-duplicate grouping."""

    def phash(self, image: bytes) -> str: ...


def score_region(region: FigureRegion) -> float:
    """How confident we are this region is one figure.

    Deliberately legible rather than clever. A region of several graphic objects
    carrying its own label text is almost certainly a figure; a single small
    vector stroke with nothing around it is probably a rule under a heading.
    Anything in between lands in the review queue, which is where an uncertain
    mapping belongs.
    """
    graphics = sum(1 for m in region.members if m.is_graphic)
    score = 0.45
    if graphics >= 2:
        score += 0.25
    if region.label_text.strip():
        score += 0.2
    if region.bbox.area >= MIN_AREA * 8:
        score += 0.15
    return min(score, 1.0)


def extract_figures(
    source: PageSource,
    *,
    doc_id: str,
    renderer: RegionRenderer | None = None,
    recognizer: TextRecognizer | None = None,
    hasher: PerceptualHasher | None = None,
    clock: Clock | None = None,
    dpi: int = 300,
    pages: Iterable[int] | None = None,
) -> Manifest:
    """Run both layers over a document and return the manifest.

    Every collaborator past `source` is optional and degrades to absent rather
    than to a wrong value: without a renderer there are no bytes, so no sha256
    and no perceptual hash, so no duplicate grouping — and the manifest says so
    by leaving those fields empty rather than filling them with a default that
    reads like a measurement.
    """
    now = (clock or SystemClock()).now()
    manifest = Manifest(doc_id=doc_id, created_at=now.isoformat())
    numbers = list(pages) if pages is not None else list(range(1, source.page_count() + 1))

    for page in numbers:
        regions = cluster_page(source.objects(page), page, report=manifest.report)
        for index, region in enumerate(regions, start=1):
            record = FigureRecord(
                figure_id=f"{doc_id}-p{page:04d}-f{index:02d}",
                doc_id=doc_id,
                page=page,
                bbox=region.bbox,
                composition=region.composition,
                score=score_region(region),
                caption=region.label_text,
            )
            if renderer is not None:
                image = renderer.render(page, region.bbox, dpi)
                record.sha256 = hashlib.sha256(image).hexdigest()
                if recognizer is not None:
                    record.ocr_text = recognizer.text_of(image)
                if hasher is not None:
                    record.phash = hasher.phash(image)
            manifest.records.append(record)

    if any(r.sha256 for r in manifest.records):
        groups = duplicate_groups(manifest.records)
        for record in manifest.records:
            record.duplicate_group = groups[record.figure_id]

    return manifest


def pdfplumber_source(path: str) -> PageSource:
    """The real Layer A, behind the `figures` extra.

    Kept at the edge and returning the Protocol, so every test above this line
    runs on a bare interpreter. A suite that needs a system tesseract binary is
    a suite that stops being run.
    """
    try:
        import pdfplumber  # noqa: F401
    except ImportError as exc:  # pragma: no cover - only without the extra
        raise ConfigurationError(
            "figure extraction needs the 'figures' extra: pip install 'omnex-engine[figures]'"
        ) from exc

    raise ConfigurationError(  # pragma: no cover - adapter lands with the corpus
        "the pdfplumber adapter is not wired yet — pass a PageSource explicitly"
    )
