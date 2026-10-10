from __future__ import annotations

import importlib.util
import json
import sys
import zipfile
from pathlib import Path
from types import ModuleType

import pytest

BUILDER = Path(__file__).resolve().parents[2] / "packs" / "build_pack.py"


def _module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("pack_candidate", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _pack(root: Path, names: list[str]) -> None:
    images = root / "alpha" / "images"
    for name in names:
        source = images / name
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(name.encode())
    (root / "alpha").mkdir(parents=True, exist_ok=True)
    (root / "alpha" / "manifest.json").write_text(
        json.dumps({"pack": "alpha", "name": "Alpha", "images": [{"file": n} for n in names]}),
        encoding="utf-8",
    )
    (root / "LICENSE.txt").write_text("commercial licence", encoding="utf-8")


@pytest.mark.parametrize("existing", [False, True])
def test_render_failure_preserves_previous_archive_and_removes_temporary_file(
    tmp_path: Path, existing: bool
):
    module = _module()
    _pack(tmp_path, ["scene.png"])
    out = tmp_path / "dist"
    out.mkdir()
    archive = out / "omnex-alpha.zip"
    previous = b"previous valid deliverable"
    if existing:
        archive.write_bytes(previous)
    attempts = 0

    def renderer(source: Path, ratio: tuple[int, int]) -> bytes:
        nonlocal attempts
        attempts += 1
        if attempts == 2:
            raise RuntimeError("renderer failed")
        return b"partial image"

    with pytest.raises(RuntimeError, match="renderer failed"):
        module.build("alpha", out, tmp_path, renderer=renderer, formats={"a": (1, 1), "b": (2, 1)})

    if existing:
        assert archive.read_bytes() == previous
    else:
        assert not archive.exists()
    assert list(out.glob(".omnex-alpha.zip.*.tmp")) == []


def test_success_replaces_archive_with_a_complete_zip_and_cleans_temporary_file(tmp_path: Path):
    module = _module()
    _pack(tmp_path, ["scene.png"])
    out = tmp_path / "dist"
    out.mkdir()
    archive = out / "omnex-alpha.zip"
    archive.write_bytes(b"old artifact")

    built = module.build(
        "alpha",
        out,
        tmp_path,
        renderer=lambda source, ratio: b"new complete image",
        formats={"sq": (1, 1)},
    )

    assert built.archive == archive
    with zipfile.ZipFile(archive) as result:
        assert "sq/scene.png" in result.namelist()
        assert result.read("sq/scene.png") == b"new complete image"
        assert "manifest.json" in result.namelist()
    assert list(out.glob(".omnex-alpha.zip.*.tmp")) == []


def test_colliding_source_stems_are_refused_before_rendering(tmp_path: Path):
    module = _module()
    _pack(tmp_path, ["first/scene.png", "second/scene.jpg"])
    out = tmp_path / "dist"
    rendered: list[str] = []

    def renderer(source: Path, ratio: tuple[int, int]) -> bytes:
        rendered.append(str(source))
        return b"image"

    with pytest.raises(ValueError, match="source basenames must be unique"):
        module.build("alpha", out, tmp_path, renderer=renderer, formats={"sq": (1, 1)})

    assert rendered == []
    assert not (out / "omnex-alpha.zip").exists()
    if out.exists():
        assert list(out.glob(".omnex-alpha.zip.*.tmp")) == []
