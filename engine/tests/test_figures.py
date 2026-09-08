"""Figure extraction — the properties that decide whether a manifest is usable.

Every test here runs on a bare interpreter. No pdfplumber, no pypdfium2, no
tesseract binary, no network. That is not a convenience: the extraction pipeline
is the part of this repo most likely to be run on a laptop against somebody
else's document, and a suite that only passes where four system dependencies
happen to be installed is a suite that stops being run.

The doubles below stand in for the four Protocols. They are deliberately dumb —
a renderer that returns the bbox as bytes is enough to prove that hashing,
duplicate grouping and graceful degradation are wired correctly, and it makes
every assertion about behaviour rather than about somebody else's library.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence

import pytest

from omnex.core import FakeClock, ValidationFailed
from omnex.rag.figures import (
    Band,
    BBox,
    Composition,
    FigureRecord,
    Manifest,
    ObjectKind,
    PageObject,
    RegionReport,
    cluster_page,
    duplicate_groups,
    extract_figures,
    hamming,
)


class FakeSource:
    """Layer A without a PDF: pages of objects handed in directly."""

    def __init__(self, pages: dict[int, list[PageObject]]) -> None:
        self._pages = pages

    def page_count(self) -> int:
        return max(self._pages) if self._pages else 0

    def objects(self, page: int) -> Sequence[PageObject]:
        return self._pages.get(page, [])


class FakeRenderer:
    """Deterministic bytes per region, so sha256 is stable across runs."""

    def __init__(self, payload: dict[tuple[int, tuple[float, ...]], bytes] | None = None) -> None:
        self._payload = payload or {}
        self.calls: list[tuple[int, BBox, int]] = []

    def render(self, page: int, bbox: BBox, dpi: int) -> bytes:
        self.calls.append((page, bbox, dpi))
        override = self._payload.get((page, bbox.as_tuple()))
        return override if override is not None else f"{page}:{bbox.as_tuple()}".encode()


class FakeRecognizer:
    def text_of(self, image: bytes) -> str:
        return "ReAct loop"


class FakeHasher:
    """A hash of the content, so identical renders collide and others do not.

    Keyed on the bytes rather than on their length. Hashing the length looks
    equivalent and is not: two different regions of the same document routinely
    render to byte strings of equal size, which would group them as duplicates
    and make `test_the_same_figure_reprinted_later_groups_across_pages` pass
    without the reprint ever being detected.
    """

    def __init__(self, table: dict[bytes, str] | None = None) -> None:
        self._table = table or {}

    def phash(self, image: bytes) -> str:
        if image in self._table:
            return self._table[image]
        return hashlib.sha256(image).hexdigest()[:16]


def graphic(x0: float, y0: float, x1: float, y1: float, kind: ObjectKind) -> PageObject:
    return PageObject(kind=kind, bbox=BBox(x0, y0, x1, y1))


def label(x0: float, y0: float, x1: float, y1: float, text: str) -> PageObject:
    return PageObject(kind=ObjectKind.TEXT, bbox=BBox(x0, y0, x1, y1), text=text)


# --------------------------------------------------------------------------
# Band: computed, ordered, and refusing to be talked into confidence
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (1.0, Band.AUTO),
        (0.85, Band.AUTO),
        (0.8499, Band.REVIEW),
        (0.5, Band.REVIEW),
        (0.4999, Band.WEAK),
        (0.0, Band.WEAK),
    ],
)
def test_the_band_is_computed_from_the_score(score: float, expected: Band) -> None:
    assert Band.of(score) is expected


def test_a_score_outside_the_range_is_refused_rather_than_clamped() -> None:
    """Clamping would turn a bug in a scorer into a confident mapping."""
    with pytest.raises(ValidationFailed):
        Band.of(1.5)
    with pytest.raises(ValidationFailed):
        Band.of(-0.1)


def test_band_ordering_is_by_rank_and_not_by_the_word() -> None:
    """The StrEnum trap, demonstrated rather than asserted.

    `Band` inherits `str`, so without the four explicit comparisons the ordering
    silently falls back to comparing the words — and alphabetically "auto" sorts
    *below* "weak", which inverts every "at least this confident" filter.
    """
    assert Band.WEAK < Band.REVIEW < Band.AUTO
    assert Band.AUTO > Band.WEAK
    assert sorted([Band.AUTO, Band.WEAK, Band.REVIEW]) == [Band.WEAK, Band.REVIEW, Band.AUTO]
    # The comparison the enum would have inherited, shown to disagree.
    assert not ("auto" > "weak")


def test_a_record_cannot_disagree_with_its_own_score() -> None:
    record = FigureRecord(
        figure_id="f1",
        doc_id="d",
        page=1,
        bbox=BBox(0, 0, 100, 100),
        composition=Composition.RASTER,
        score=0.6,
    )
    assert record.band is Band.REVIEW
    assert record.needs_review
    record.score = 0.95
    assert record.band is Band.AUTO
    assert not record.needs_review


# --------------------------------------------------------------------------
# Clustering
# --------------------------------------------------------------------------


def test_text_alone_is_never_a_figure() -> None:
    """Without this rule every paragraph becomes a figure with a good score."""
    objects = [
        label(50, 700, 500, 715, "A paragraph of ordinary prose."),
        label(50, 680, 500, 695, "And the sentence that follows it."),
    ]
    report = RegionReport()
    regions = cluster_page(objects, page=3, report=report)

    assert regions == []
    assert report.text_only == 2
    assert report.clustered == 0
    assert report.reconciles()


def test_a_label_joins_the_diagram_it_belongs_to_through_a_chain() -> None:
    """The label touches the arrow, the arrow touches the diagram, so all three
    are one figure — even though the label never touches the diagram itself."""
    objects = [
        graphic(100, 500, 300, 700, ObjectKind.RASTER),
        graphic(302, 550, 340, 570, ObjectKind.VECTOR),
        label(344, 550, 420, 566, "Figure 4.2 — the router"),
    ]
    regions = cluster_page(objects, page=7)

    assert len(regions) == 1
    assert len(regions[0].members) == 3
    assert "Figure 4.2" in regions[0].label_text
    assert regions[0].bbox.x1 >= 420


def test_a_vector_only_diagram_is_recovered_and_named_as_such() -> None:
    """The case `pdfimages` cannot produce at all: no embedded raster exists."""
    objects = [
        graphic(100, 400, 260, 560, ObjectKind.VECTOR),
        graphic(262, 450, 300, 470, ObjectKind.VECTOR),
    ]
    regions = cluster_page(objects, page=11)

    assert len(regions) == 1
    assert regions[0].composition is Composition.VECTOR


def test_a_composite_of_raster_and_vector_is_one_hybrid_figure() -> None:
    objects = [
        graphic(100, 400, 300, 600, ObjectKind.RASTER),
        graphic(150, 450, 250, 550, ObjectKind.VECTOR),
    ]
    regions = cluster_page(objects, page=11)

    assert len(regions) == 1
    assert regions[0].composition is Composition.HYBRID


def test_a_rule_under_a_heading_is_below_the_minimum_area() -> None:
    objects = [graphic(50, 700, 500, 702, ObjectKind.VECTOR)]
    report = RegionReport()

    assert cluster_page(objects, page=1, report=report) == []
    assert report.below_min_area == 1
    assert report.reconciles()


def test_every_object_is_accounted_for() -> None:
    """Filtering is not deletion — the totals must reconcile or the report lies."""
    objects = [
        graphic(100, 400, 300, 600, ObjectKind.RASTER),
        label(100, 380, 300, 396, "Figure 1"),
        label(50, 100, 500, 116, "Unrelated prose far below."),
        graphic(50, 90, 500, 92, ObjectKind.VECTOR),
    ]
    report = RegionReport()
    cluster_page(objects, page=2, report=report)

    assert report.received == 4
    assert report.reconciles()
    assert "4 objects in" in report.report()


def test_two_figures_sharing_a_caption_band_merge() -> None:
    """A stated limitation, kept as a passing test.

    Clustering is geometric. Two diagrams stacked with no gap under one shared
    caption are one region to this code, and they should be two. The fix is a
    layout model; a proximity threshold nudged until this case passes will fail
    differently on the next document, so the behaviour is pinned here instead of
    being tuned away.
    """
    objects = [
        graphic(100, 500, 300, 700, ObjectKind.RASTER),
        graphic(100, 300, 300, 495, ObjectKind.RASTER),
        label(100, 280, 300, 296, "Figures 5.1 and 5.2"),
    ]
    regions = cluster_page(objects, page=9)

    assert len(regions) == 1, "known limitation: geometric clustering cannot split these"


# --------------------------------------------------------------------------
# Duplicates: grouped, never deleted
# --------------------------------------------------------------------------


def _record(figure_id: str, sha: str = "", ph: str = "") -> FigureRecord:
    return FigureRecord(
        figure_id=figure_id,
        doc_id="d",
        page=1,
        bbox=BBox(0, 0, 100, 100),
        composition=Composition.RASTER,
        score=0.9,
        sha256=sha,
        phash=ph,
    )


def test_identical_figures_are_grouped_and_both_survive() -> None:
    records = [_record("a", sha="ff"), _record("b", sha="ff"), _record("c", sha="ee")]
    groups = duplicate_groups(records)

    assert groups["a"] == groups["b"] == "a"
    assert groups["c"] == "c"
    assert len(records) == 3, "grouping must never remove a record"


def test_a_rescaled_reprint_groups_by_perceptual_hash() -> None:
    near = format(0x0F0F0F0F0F0F0F0F, "016x")
    same_but_one_bit = format(0x0F0F0F0F0F0F0F0E, "016x")
    far = format(0xFFFFFFFFFFFFFFFF, "016x")

    groups = duplicate_groups(
        [
            _record("a", sha="1", ph=near),
            _record("b", sha="2", ph=same_but_one_bit),
            _record("c", sha="3", ph=far),
        ]
    )

    assert groups["b"] == "a"
    assert groups["c"] == "c"


def test_hamming_refuses_hashes_of_different_widths() -> None:
    """Comparing a 64-bit hash to a 128-bit one silently returns a small number."""
    with pytest.raises(ValidationFailed):
        hamming("ff", "ffff")


# --------------------------------------------------------------------------
# Extraction end to end
# --------------------------------------------------------------------------


def _two_page_source() -> FakeSource:
    return FakeSource(
        {
            1: [
                graphic(100, 400, 300, 600, ObjectKind.RASTER),
                label(100, 380, 300, 396, "Figure 1.1"),
            ],
            2: [graphic(100, 400, 300, 600, ObjectKind.VECTOR)],
        }
    )


def test_extraction_reads_time_from_the_injected_clock() -> None:
    clock = FakeClock()
    manifest = extract_figures(_two_page_source(), doc_id="book", clock=clock)

    assert manifest.created_at == clock.now().isoformat()


def test_without_a_renderer_the_hash_fields_stay_empty_rather_than_wrong() -> None:
    """Degrading to absent is the point: an empty sha256 reads as "not measured",
    while a placeholder reads as a measurement and groups unrelated figures."""
    manifest = extract_figures(_two_page_source(), doc_id="book", clock=FakeClock())

    assert manifest.records
    assert all(r.sha256 == "" for r in manifest.records)
    assert all(r.phash == "" for r in manifest.records)
    assert all(r.duplicate_group == "" for r in manifest.records)


def test_with_a_renderer_every_figure_is_hashed_and_grouped() -> None:
    manifest = extract_figures(
        _two_page_source(),
        doc_id="book",
        renderer=FakeRenderer(),
        recognizer=FakeRecognizer(),
        hasher=FakeHasher(),
        clock=FakeClock(),
    )

    assert len(manifest.records) == 2
    assert all(r.sha256 for r in manifest.records)
    assert all(r.ocr_text == "ReAct loop" for r in manifest.records)
    assert all(r.duplicate_group for r in manifest.records)


def test_ocr_makes_a_diagram_findable_by_a_word_the_prose_never_uses() -> None:
    """The reason OCR is in the index rather than only in the record."""
    manifest = extract_figures(
        _two_page_source(),
        doc_id="book",
        renderer=FakeRenderer(),
        recognizer=FakeRecognizer(),
        clock=FakeClock(),
    )

    hits = [r for r in manifest.records if "ReAct" in r.ocr_text]
    assert hits, "a figure must be searchable by text drawn inside it"


def test_the_same_figure_reprinted_later_groups_across_pages() -> None:
    shared = b"identical-render"
    renderer = FakeRenderer(
        {
            (1, (100.0, 380.0, 300.0, 600.0)): shared,
            (2, (100.0, 400.0, 300.0, 600.0)): shared,
        }
    )
    manifest = extract_figures(
        _two_page_source(),
        doc_id="book",
        renderer=renderer,
        hasher=FakeHasher(),
        clock=FakeClock(),
    )

    groups = {r.duplicate_group for r in manifest.records}
    assert len(groups) == 1, "the same render on two pages is one duplicate group"
    assert len(manifest.records) == 2, "and both records survive"


def test_the_review_queue_is_ordered_worst_first() -> None:
    manifest = Manifest(doc_id="d", created_at="2026-01-01T00:00:00+00:00")
    manifest.records = [
        _record("high"),
        FigureRecord("mid", "d", 2, BBox(0, 0, 10, 10), Composition.RASTER, 0.7),
        FigureRecord("low", "d", 1, BBox(0, 0, 10, 10), Composition.RASTER, 0.3),
    ]

    queue = [r.figure_id for r in manifest.review_queue]
    assert queue == ["low", "mid"], "AUTO stays out of the queue; worst comes first"


def test_the_manifest_records_whether_its_own_object_count_reconciles() -> None:
    manifest = extract_figures(
        _two_page_source(), doc_id="book", renderer=FakeRenderer(), clock=FakeClock()
    )
    payload = json.loads(manifest.to_json())

    assert payload["objects"]["reconciles"] is True
    assert payload["doc_id"] == "book"
    assert len(payload["figures"]) == 2
    assert payload["figures"][0]["band"] in {"auto", "review", "weak"}


def test_a_figure_id_carries_its_page_so_a_citation_can_be_followed() -> None:
    manifest = extract_figures(_two_page_source(), doc_id="book", clock=FakeClock())

    assert manifest.records[0].figure_id == "book-p0001-f01"
    assert manifest.records[1].figure_id == "book-p0002-f01"


def test_an_inside_out_bbox_is_refused_at_construction() -> None:
    with pytest.raises(ValidationFailed):
        BBox(300, 100, 100, 300)
