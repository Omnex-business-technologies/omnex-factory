"""The corpus parse, held to the export's own totals.

A regex that matches 400 of 509 records writes a smaller manifest and raises
nothing. Every downstream number is then quietly wrong, and the failure is
invisible because the output still looks like a manifest. So the counts are
asserted against what the export itself declares, three ways — figure records
parsed, branch headers parsed, and the totals those headers add up to.

The bands are the second thing worth pinning. The export states its own
thresholds and `omnex.rag.figures.Band` states the same ones independently;
`test_bands_agree_with_the_engine_implementation` exists so that if either side
moves, the disagreement surfaces here rather than in a review queue somebody
trusts.
"""

from __future__ import annotations

import json

import pytest
from ingest_atlas import (
    CORPUS,
    EXPECTED_BRANCHES,
    EXPECTED_FIGURES,
    EXPECTED_NODES,
    EXPORT,
    MANIFEST,
    parse,
)

from omnex.rag.figures import Band

pytestmark = pytest.mark.skipif(
    not EXPORT.exists(), reason="the Universal AI OS export is not in this checkout"
)


def _parsed() -> tuple[list, list]:
    return parse(EXPORT.read_text(encoding="utf-8"))


def test_every_record_the_export_declares_is_parsed() -> None:
    branches, figures = _parsed()
    assert len(figures) == EXPECTED_FIGURES
    assert len(branches) == EXPECTED_BRANCHES
    assert sum(b.nodes for b in branches) == EXPECTED_NODES


def test_the_branch_headers_account_for_every_figure() -> None:
    """Two independent counts of the same thing, required to agree.

    Per-branch totals come from the export's branch headers; the record count
    comes from the manifest body. They are written by different parts of the
    exporter, so agreement is evidence and disagreement is a real defect.
    """
    branches, figures = _parsed()
    assert sum(b.figures for b in branches) == len(figures)


def test_primary_and_touch_counts_are_kept_apart() -> None:
    """Two counts, and conflating them is a real mistake already made once.

    A figure has ONE primary branch and maps to SEVERAL. Primary counts sum to
    509 because every figure has exactly one; touch counts sum to far more
    because they count edges. Ranked on primary alone, the protocol fabric shows
    70 figures; ranked on touches it shows 184 — the same branch, a factor of
    two and a half apart, and the second is the one that says how much of the
    corpus depends on it.
    """
    branches, figures = _parsed()
    assert sum(b.figures for b in branches) == len(figures)
    assert sum(b.touch_count for b in branches) > len(figures)

    fabric = next(b for b in branches if b.id == "XII")
    assert fabric.touch_count > fabric.figures, "section 7 was not parsed"


def test_every_touched_figure_id_exists() -> None:
    """A cross-reference to a record that is not in the manifest is a dangling edge."""
    branches, figures = _parsed()
    known = {f.id for f in figures}
    for branch in branches:
        unknown = [fid for fid in branch.touched if fid not in known]
        assert not unknown, f"{branch.id} references figures that do not exist: {unknown[:3]}"


def test_bands_agree_with_the_engine_implementation() -> None:
    _, figures = _parsed()
    for figure in figures:
        assert figure.band == str(Band.of(figure.confidence)), figure.id


def test_no_figure_loses_the_page_it_came_from() -> None:
    """A citation nobody can follow is not a citation."""
    _, figures = _parsed()
    assert all(f.pdf_page >= 1 for f in figures)
    assert all(f.sha for f in figures), "a record with no hash cannot be tied to an image"


def test_duplicates_are_grouped_and_every_record_survives() -> None:
    _, figures = _parsed()
    groups = {f.duplicate_group for f in figures if f.duplicate_group}
    assert groups, "the export records duplicate groups"
    assert len(figures) == EXPECTED_FIGURES, "grouping must never drop a record"


def test_the_committed_manifest_matches_the_committed_export() -> None:
    """The generated file and its generator, required not to drift."""
    if not MANIFEST.exists():
        pytest.skip("manifest not generated in this checkout")
    stored = json.loads(MANIFEST.read_text(encoding="utf-8"))
    _, figures = _parsed()
    assert len(stored["figures"]) == len(figures)
    assert stored["figures"][0]["id"] == figures[0].id


def test_the_reconciliation_refuses_to_read_zero_as_a_verdict() -> None:
    """The corpus is one book with one author's emphasis.

    Fourteen branches carry no figures at all, including every branch that earns
    money. A reader who took zero for a judgement would delete half the platform,
    so the rendered document has to say so where it cannot be missed.
    """
    page = (CORPUS / "RECONCILIATION.md").read_text(encoding="utf-8")
    assert "zero as a verdict" in page
    assert "one book with one author's emphasis" in page
