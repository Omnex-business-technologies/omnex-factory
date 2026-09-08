"""A listing may not promise more than QC passed — and the promise is data.

`GIG.md` sells "170+ images" in the €49 Complete Vault. The four QC manifests
total **80**. Nothing connected the two, so the only thing standing between that
copy and a live Etsy listing was somebody remembering.

The failure this prevents is not a rounding error. A buyer pays €49, receives
less than half of what the page said, and the discovery happens after the money
moves — which is a refund, a one-star review, and on Etsy an account risk.

## Direction matters

A promise may shrink to fit the goods. The goods may never be assumed to fit the
promise. `listing.json` is transcribed FROM `GIG.md`, and when the two disagree
the copy is right, because the copy is what a buyer reads.

## What is checked where

`.gitignore` admits exactly one file back out of `packs/*/`:
`!packs/*/manifest.json`. So the images live on the machine that made them and
the manifest is the committed QC record. This suite checks promise against that
record everywhere; only the machine holding the files can check the files.
Saying which half was verified is the point — a check that passes because it
could not see the data is worse than one that reports what it saw.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parents[2]
PACKS = REPO / "packs"
CHECKER = PACKS / "listing_check.py"

pytestmark = pytest.mark.skipif(not CHECKER.exists(), reason="packs/ is not in this checkout")


def _module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("packs_listing_check", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["packs_listing_check"] = module
    spec.loader.exec_module(module)
    return module


def _pack(root: Path, name: str, images: int) -> None:
    (root / name).mkdir(parents=True, exist_ok=True)
    (root / name / "manifest.json").write_text(
        json.dumps(
            {
                "pack": name,
                "name": name.title(),
                "count": images,
                "images": [{"file": f"scene-{i:03}.png", "kb": 30} for i in range(images)],
            }
        ),
        encoding="utf-8",
    )


def _listing(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "formats": ["1:1", "4:5", "9:16", "16:9"],
        "licence_file": "LICENSE.txt",
        "licence_claim": "Full commercial licence",
        "packs": {
            "alpha": {"listing_name": "Alpha Pack", "price_eur": 19, "promised_images": 10},
            "beta": {"listing_name": "Beta Pack", "price_eur": 19, "promised_images": 10},
        },
        "bundles": {
            "both": {
                "listing_name": "Both Packs",
                "price_eur": 29,
                "includes": ["alpha", "beta"],
                "promised_images": 20,
            }
        },
    }
    base.update(overrides)
    return base


# ── the real repository ───────────────────────────────────────────────────
def test_the_gate_reports_the_real_shortfall_exactly() -> None:
    """Deliberately not "the repo passes" — today it does not, and that is the point.

    Asserting the current failure would break the moment the images are
    generated, which is the outcome this exists to encourage. So the assertion
    is on the arithmetic: whatever the counts are, the shortfall reported is
    promised minus what passed QC.
    """
    module = _module()
    listing = module.load_listing()
    shortfalls, _ = module.audit(listing, PACKS)
    for shortfall in shortfalls:
        assert shortfall.missing == shortfall.promised - shortfall.have
        assert shortfall.missing > 0, "a covered listing was reported as short"


def test_the_promise_matches_the_copy_a_buyer_reads() -> None:
    """`listing.json` is transcribed from GIG.md; drift between them is silent.

    The copy sells the pack. If somebody edits GIG.md to promise sixty images
    and this file still says fifty, the gate passes on a promise nobody is
    making — and the buyer's expectation comes from the page, not from JSON.
    """
    gig = (REPO / "GIG.md").read_text(encoding="utf-8")
    listing = _module().load_listing()

    for offer in listing["packs"].values():  # type: ignore[union-attr]
        name = str(offer["listing_name"])
        assert name in gig, f"{name!r} is promised in listing.json and absent from GIG.md"

    for bundle in listing["bundles"].values():  # type: ignore[union-attr]
        assert str(bundle["listing_name"]) in gig

    # The Vault's headline number, read out of the copy rather than assumed.
    match = re.search(r"(\d+)\+?\s+images", gig)
    assert match is not None, "GIG.md no longer states an image count for the bundle"
    assert int(match.group(1)) == int(listing["bundles"]["vault"]["promised_images"])  # type: ignore[index]


def test_every_promised_format_is_named_in_the_copy() -> None:
    gig = (REPO / "GIG.md").read_text(encoding="utf-8")
    for ratio in _module().load_listing()["formats"]:  # type: ignore[union-attr]
        assert str(ratio) in gig


# ── the gate can fail, and passes when it should ──────────────────────────
def test_a_covered_listing_passes(tmp_path: Path) -> None:
    module = _module()
    _pack(tmp_path, "alpha", 10)
    _pack(tmp_path, "beta", 10)
    (tmp_path / "LICENSE.txt").write_text("licence", encoding="utf-8")
    shortfalls, problems = module.audit(_listing(), tmp_path)
    assert shortfalls == []
    assert problems == []


def test_one_image_short_is_caught(tmp_path: Path) -> None:
    """The check must fail on a shortfall of one, not only on an obvious one."""
    module = _module()
    _pack(tmp_path, "alpha", 9)
    _pack(tmp_path, "beta", 10)
    (tmp_path / "LICENSE.txt").write_text("licence", encoding="utf-8")
    shortfalls, _ = module.audit(_listing(), tmp_path)
    names = {s.listing: s.missing for s in shortfalls}
    assert names["Alpha Pack"] == 1
    assert names["Both Packs"] == 1, "the bundle did not inherit its member's shortfall"


def test_a_bundle_is_measured_against_what_its_members_have(tmp_path: Path) -> None:
    """The trap: promise-versus-promise agrees with itself while everything is short.

    The Vault promises 170 and its four packs promise 50+40+40+40 = 170. Checking
    those two numbers against each other passes forever, no matter how few images
    exist.
    """
    module = _module()
    _pack(tmp_path, "alpha", 1)
    _pack(tmp_path, "beta", 1)
    (tmp_path / "LICENSE.txt").write_text("licence", encoding="utf-8")
    shortfalls, _ = module.audit(_listing(), tmp_path)
    bundle = next(s for s in shortfalls if s.listing == "Both Packs")
    assert bundle.have == 2, "the bundle counted promises instead of goods"
    assert bundle.missing == 18


def test_a_pack_that_never_ran_qc_is_not_reported_as_zero(tmp_path: Path) -> None:
    """`None` is not zero. Never-run and failed-everything need different responses."""
    module = _module()
    _pack(tmp_path, "alpha", 10)
    (tmp_path / "LICENSE.txt").write_text("licence", encoding="utf-8")
    assert module.qc_count("beta", tmp_path) is None

    _, problems = module.audit(_listing(), tmp_path)
    assert any("never" in p or "nothing has passed" in p for p in problems)


def test_the_image_list_outranks_the_count_field(tmp_path: Path) -> None:
    """A summary field drifts from the list it summarises; the list is the record."""
    module = _module()
    (tmp_path / "alpha").mkdir()
    (tmp_path / "alpha" / "manifest.json").write_text(
        json.dumps({"count": 99, "images": [{"file": "a.png"}]}), encoding="utf-8"
    )
    assert module.qc_count("alpha", tmp_path) == 1


def test_a_missing_licence_file_is_a_problem(tmp_path: Path) -> None:
    """The listing claims a commercial licence. A claim with no file is exposure."""
    module = _module()
    _pack(tmp_path, "alpha", 10)
    _pack(tmp_path, "beta", 10)
    _, problems = module.audit(_listing(), tmp_path)
    assert any("LICENSE.txt" in p for p in problems)


def test_a_bundle_naming_an_unknown_pack_is_caught(tmp_path: Path) -> None:
    module = _module()
    _pack(tmp_path, "alpha", 10)
    _pack(tmp_path, "beta", 10)
    (tmp_path / "LICENSE.txt").write_text("licence", encoding="utf-8")
    listing = _listing()
    listing["bundles"]["both"]["includes"] = ["alpha", "ghost"]  # type: ignore[index]
    _, problems = module.audit(listing, tmp_path)
    assert any("ghost" in p for p in problems)


def test_the_licence_file_the_real_listing_names_exists() -> None:
    listing = _module().load_listing()
    assert (PACKS / str(listing["licence_file"])).exists()
