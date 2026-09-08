"""Assembling a deliverable, and the four things it refuses to ship.

`qc.py` decides which images pass. `listing_check.py` decides whether there are
enough. This is the step that turns "enough good images in a directory" into a
file Etsy can hand a buyer — and every refusal here is a way that file could
otherwise reach somebody who paid for it.

The renderer is injected. `packs/` runs on machines with a GPU stack and on
machines with nothing, so Pillow is imported inside the function that needs it
and the assembly logic — which is where the refusals live — is testable without
it. That is the same discipline `qc.py` and `train_lora.py` already follow.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import zipfile
from pathlib import Path
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parents[2]
PACKS = REPO / "packs"
BUILDER = PACKS / "build_pack.py"

pytestmark = pytest.mark.skipif(not BUILDER.exists(), reason="packs/ is not in this checkout")


def _module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("packs_build_pack", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["packs_build_pack"] = module
    spec.loader.exec_module(module)
    return module


def _fake_renderer(source: Path, ratio: tuple[int, int]) -> bytes:
    """Deterministic bytes that depend on the source and the ratio.

    Not a stub returning a constant: a constant would let a bug that renders one
    ratio four times pass every assertion here.
    """
    return f"{source.name}|{ratio[0]}x{ratio[1]}".encode()


def _pack(root: Path, name: str, images: int, *, on_disk: int | None = None) -> None:
    directory = root / name / "images"
    directory.mkdir(parents=True, exist_ok=True)
    entries = [f"scene-{i:03}.png" for i in range(images)]
    for entry in entries[: images if on_disk is None else on_disk]:
        (directory / entry).write_bytes(b"not really a png")
    (root / name / "manifest.json").write_text(
        json.dumps({"pack": name, "name": name.title(), "images": [{"file": e} for e in entries]}),
        encoding="utf-8",
    )
    (root / "LICENSE.txt").write_text("COMMERCIAL LICENCE\n", encoding="utf-8")


# ── what it produces ──────────────────────────────────────────────────────
def test_every_source_image_appears_in_every_format(tmp_path: Path) -> None:
    module = _module()
    _pack(tmp_path, "alpha", 3)
    built = module.build("alpha", tmp_path / "dist", tmp_path, renderer=_fake_renderer)

    with zipfile.ZipFile(built.archive) as bundle:
        names = set(bundle.namelist())
    for index in range(3):
        for label in ("1x1", "4x5", "9x16", "16x9"):
            assert f"{label}/scene-{index:03}.png" in names
    assert built.images == 3
    assert built.entries == 3 * 4 + 3


def test_each_format_is_actually_rendered_differently(tmp_path: Path) -> None:
    """A builder that renders one ratio four times ships four identical files."""
    module = _module()
    _pack(tmp_path, "alpha", 1)
    built = module.build("alpha", tmp_path / "dist", tmp_path, renderer=_fake_renderer)

    with zipfile.ZipFile(built.archive) as bundle:
        payloads = {
            name: bundle.read(name) for name in bundle.namelist() if name.endswith("scene-000.png")
        }
    assert len(payloads) == 4
    assert len(set(payloads.values())) == 4, "the same bytes were written for every ratio"


def test_the_licence_and_a_readme_travel_with_the_images(tmp_path: Path) -> None:
    """The listing claims a commercial licence; a claim with no file is exposure."""
    module = _module()
    _pack(tmp_path, "alpha", 1)
    built = module.build("alpha", tmp_path / "dist", tmp_path, renderer=_fake_renderer)

    with zipfile.ZipFile(built.archive) as bundle:
        names = bundle.namelist()
        assert "LICENCE.txt" in names
        assert "README.txt" in names
        assert "manifest.json" in names
        readme = bundle.read("README.txt").decode()
        assert "1:1" in readme and "16:9" in readme
        assert json.loads(bundle.read("manifest.json"))["source_images"] == 1


def test_two_builds_of_one_input_are_byte_identical(tmp_path: Path) -> None:
    """So "is the file I uploaded the file I built" is a hash, not trust."""
    module = _module()
    _pack(tmp_path, "alpha", 2)
    first = module.build("alpha", tmp_path / "a", tmp_path, renderer=_fake_renderer)
    second = module.build("alpha", tmp_path / "b", tmp_path, renderer=_fake_renderer)
    assert first.sha256 == second.sha256
    assert first.sha256 == hashlib.sha256(second.archive.read_bytes()).hexdigest()


# ── what it refuses ───────────────────────────────────────────────────────
def test_a_manifest_entry_with_no_image_stops_the_build(tmp_path: Path) -> None:
    """The check CI structurally cannot make.

    `.gitignore` admits only `manifest.json` back out of `packs/*/`, so from
    anywhere except the machine holding the files a record naming an image
    nobody has looks identical to a healthy one.
    """
    module = _module()
    _pack(tmp_path, "alpha", 5, on_disk=3)
    assert len(module.missing_files("alpha", tmp_path)) == 2
    with pytest.raises(FileNotFoundError, match="disagree"):
        module.build("alpha", tmp_path / "dist", tmp_path, renderer=_fake_renderer)


def test_a_missing_licence_stops_the_build(tmp_path: Path) -> None:
    module = _module()
    _pack(tmp_path, "alpha", 1)
    (tmp_path / "LICENSE.txt").unlink()
    with pytest.raises(FileNotFoundError, match="commercial"):
        module.build("alpha", tmp_path / "dist", tmp_path, renderer=_fake_renderer)


def test_a_pack_that_never_ran_qc_stops_the_build(tmp_path: Path) -> None:
    module = _module()
    (tmp_path / "ghost").mkdir()
    (tmp_path / "LICENSE.txt").write_text("licence", encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="no QC manifest"):
        module.build("ghost", tmp_path / "dist", tmp_path, renderer=_fake_renderer)


def test_images_beside_the_manifest_are_found_too(tmp_path: Path) -> None:
    """`qc.py` writes into the pack directory; older packs keep images alongside."""
    module = _module()
    (tmp_path / "alpha").mkdir()
    (tmp_path / "alpha" / "scene-000.png").write_bytes(b"png")
    (tmp_path / "alpha" / "manifest.json").write_text(
        json.dumps({"images": [{"file": "scene-000.png"}]}), encoding="utf-8"
    )
    (tmp_path / "LICENSE.txt").write_text("licence", encoding="utf-8")
    assert module.missing_files("alpha", tmp_path) == []


# ── the ratios ────────────────────────────────────────────────────────────
def test_the_four_promised_ratios_are_the_ones_built() -> None:
    """The listing names four; building three and calling it done is silent."""
    module = _module()
    sys.path.insert(0, str(PACKS))
    from listing_check import load_listing

    promised = {str(f).replace(":", "x") for f in load_listing()["formats"]}  # type: ignore[union-attr]
    assert set(module.FORMATS) == promised


def test_the_crop_keeps_the_ratio_it_was_asked_for() -> None:
    """Exercises the real Pillow path when it is installed, and says so when not."""
    pillow = pytest.importorskip("PIL", reason="Pillow is an optional extra for packs/")
    from io import BytesIO

    module = _module()
    source = Path(__file__).parent / "_crop_source.png"
    pillow.Image.new("RGB", (1000, 400), "white").save(source)
    try:
        for ratio in ((1, 1), (4, 5), (9, 16), (16, 9)):
            with pillow.Image.open(BytesIO(module.centre_crop(source, ratio))) as out:
                width, height = out.size
            assert abs(width / height - ratio[0] / ratio[1]) < 0.01, ratio
            assert width <= 1000 and height <= 400, "cropping grew the image"
    finally:
        source.unlink(missing_ok=True)
