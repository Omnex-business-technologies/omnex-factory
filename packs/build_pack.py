"""Turn QC-passed images into a file a buyer downloads.

    python packs/build_pack.py cosmetics --out dist/

`qc.py` decides which images are good enough. `listing_check.py` decides whether
there are enough of them. Between "enough good images in a directory" and
"something Etsy can deliver" there was nothing, and that gap is the difference
between a folder and a product.

## What this refuses

**A pack that does not cover its own listing.** The €49 Vault sells "170+
images" against 80 that passed QC; building a zip from that would put the
shortfall in a buyer's hands. The same check `listing_check.py` runs in CI runs
here, and here it can also see the files.

**A manifest entry with no file behind it.** The manifest is the committed QC
record and the images are gitignored, so CI can only compare the promise against
the record. This is the one place both halves are visible, and a record naming
an image nobody has is the failure CI structurally cannot catch.

**A pack without its licence.** The listing claims "full commercial licence,
unlimited projects". A claim with no file in the zip is exposure, not a claim.

## Formats: crop, never pad

Four ratios — 1:1, 4:5, 9:16, 16:9 — cropped from the centre. Padding would keep
every pixel and add bars, and a background scene with bars is not publishable:
the buyer drops a product onto it and the bars are still there. Cropping loses
edge pixels, which is the correct loss for this product. Stated because it is a
judgement, not a default.

## The zip is deterministic

Fixed timestamps and sorted entries, so building twice from the same inputs
produces identical bytes. That makes "is the file I uploaded the file I built"
answerable with a hash instead of trust.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

PACKS = Path(__file__).resolve().parent

#: Aspect ratios the listing promises, as (width, height) in lowest terms.
FORMATS: dict[str, tuple[int, int]] = {
    "1x1": (1, 1),
    "4x5": (4, 5),
    "9x16": (9, 16),
    "16x9": (16, 9),
}

#: Every entry gets this timestamp so two builds of one input are byte-identical.
#: 1980-01-01 is the earliest a zip can express.
_FIXED_TIME = (1980, 1, 1, 0, 0, 0)

#: A source image and one target ratio produce one rendered file. Injected so the
#: assembly logic is testable without Pillow, which `packs/` never requires at
#: import time — the same discipline `qc.py` and `train_lora.py` already follow.
Renderer = Callable[[Path, tuple[int, int]], bytes]


@dataclass(frozen=True)
class Built:
    """What one build produced, and what it can be checked against."""

    pack: str
    archive: Path
    images: int
    entries: int
    sha256: str

    def report(self) -> str:
        return (
            f"{self.pack}: {self.entries} files from {self.images} images "
            f"→ {self.archive.name} ({self.sha256[:12]})"
        )


def centre_crop(source: Path, ratio: tuple[int, int]) -> bytes:
    """Crop to the ratio from the centre and encode as PNG.

    Pillow is imported here rather than at module scope: `packs/` runs on
    machines that have a GPU stack and on machines that have nothing, and an
    import-time dependency makes the second kind unable to even read the help
    text.
    """
    from io import BytesIO

    from PIL import Image  # noqa: PLC0415 — deliberate lazy import, see above

    with Image.open(source) as image:
        width, height = image.size
        target = ratio[0] / ratio[1]
        if width / height > target:
            new_width = int(round(height * target))
            box = ((width - new_width) // 2, 0, (width - new_width) // 2 + new_width, height)
        else:
            new_height = int(round(width / target))
            box = (0, (height - new_height) // 2, width, (height - new_height) // 2 + new_height)
        buffer = BytesIO()
        image.crop(box).save(buffer, format="PNG")
        return buffer.getvalue()


def manifest_of(pack: str, root: Path | None = None) -> dict[str, object]:
    path = (root or PACKS) / pack / "manifest.json"
    if not path.exists():
        raise FileNotFoundError(f"{pack} has no QC manifest — run qc.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def missing_files(pack: str, root: Path | None = None) -> list[str]:
    """Manifest entries with no image behind them.

    The check CI cannot make. `.gitignore` keeps `packs/*/` out of the
    repository and admits only `manifest.json` back, so a record naming a file
    nobody has looks identical to a healthy one from anywhere except the machine
    holding the files.
    """
    root = root or PACKS
    manifest = manifest_of(pack, root)
    images: list[dict[str, object]] = manifest.get("images") or []  # type: ignore[assignment]
    return [
        str(entry["file"])
        for entry in images
        if not (root / pack / "images" / str(entry["file"])).exists()
        and not (root / pack / str(entry["file"])).exists()
    ]


def _source(pack: str, name: str, root: Path) -> Path:
    nested = root / pack / "images" / name
    return nested if nested.exists() else root / pack / name


def build(
    pack: str,
    out: Path,
    root: Path | None = None,
    renderer: Renderer = centre_crop,
    formats: dict[str, tuple[int, int]] | None = None,
) -> Built:
    """Assemble one deliverable archive, refusing everything incomplete."""
    root = root or PACKS
    formats = formats or FORMATS

    absent = missing_files(pack, root)
    if absent:
        raise FileNotFoundError(
            f"{pack}: {len(absent)} manifest entries have no image on disk "
            f"(first: {absent[0]}) — the QC record and the files disagree"
        )

    licence = root / "LICENSE.txt"
    if not licence.exists():
        raise FileNotFoundError(
            "LICENSE.txt is absent, and the listing claims a full commercial "
            "licence — a claim with no file in the zip is exposure"
        )

    manifest = manifest_of(pack, root)
    images: list[dict[str, object]] = manifest.get("images") or []  # type: ignore[assignment]
    out.mkdir(parents=True, exist_ok=True)
    archive = out / f"omnex-{pack}.zip"

    rendered: list[dict[str, object]] = []
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for entry in sorted(images, key=lambda e: str(e["file"])):
            name = str(entry["file"])
            source = _source(pack, name, root)
            stem = Path(name).stem
            for label, ratio in sorted(formats.items()):
                payload = renderer(source, ratio)
                target = f"{label}/{stem}.png"
                info = zipfile.ZipInfo(target, date_time=_FIXED_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                bundle.writestr(info, payload)
                rendered.append({"file": target, "bytes": len(payload)})

        for extra, body in (
            ("LICENCE.txt", licence.read_bytes()),
            ("README.txt", _readme(pack, manifest, len(images), sorted(formats)).encode()),
            (
                "manifest.json",
                json.dumps(
                    {
                        "pack": pack,
                        "name": manifest.get("name"),
                        "source_images": len(images),
                        "formats": sorted(formats),
                        "files": rendered,
                    },
                    indent=2,
                ).encode(),
            ),
        ):
            info = zipfile.ZipInfo(extra, date_time=_FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(info, body)

    return Built(
        pack=pack,
        archive=archive,
        images=len(images),
        entries=len(rendered) + 3,
        sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
    )


def _readme(pack: str, manifest: dict[str, object], images: int, formats: list[str]) -> str:
    return "\n".join(
        [
            f"{manifest.get('name', pack)}",
            "=" * len(str(manifest.get("name", pack))),
            "",
            f"{images} scenes, each delivered in {len(formats)} formats: "
            + ", ".join(f.replace("x", ":") for f in formats),
            "",
            "Every image is a finished commercial scene — lighting, surface, depth of",
            "field and colour already handled. Drop your product in and publish.",
            "",
            "Formats are centre-cropped from one source, so the same scene is framed",
            "for feed, paid ads, stories and web hero without bars.",
            "",
            "LICENCE.txt covers commercial use. AI-generated: no model releases and",
            "no location permits are needed.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deliverable pack archive.")
    parser.add_argument("pack", help="pack directory name, e.g. cosmetics")
    parser.add_argument("--out", type=Path, default=PACKS / "dist", help="output directory")
    parser.add_argument("--root", type=Path, default=PACKS, help="packs directory")
    parser.add_argument(
        "--allow-short",
        action="store_true",
        help="build even when the pack does not cover its listing (for a draft)",
    )
    args = parser.parse_args()

    if not args.allow_short:
        sys.path.insert(0, str(PACKS))
        from listing_check import audit, load_listing  # noqa: PLC0415 — CLI-time import

        shortfalls, _ = audit(load_listing(), args.root)
        for shortfall in shortfalls:
            if shortfall.listing == _listing_name(args.pack, args.root):
                print(f"FAIL {shortfall}")
                print(
                    "Refusing to build. Generate the missing images, lower the "
                    "promise, or pass --allow-short for a draft nobody sells."
                )
                return 1

    try:
        built = build(args.pack, args.out, args.root)
    except FileNotFoundError as exc:
        print(f"FAIL {exc}")
        return 1
    print(built.report())
    return 0


def _listing_name(pack: str, root: Path) -> str:
    sys.path.insert(0, str(PACKS))
    from listing_check import load_listing  # noqa: PLC0415 — CLI-time import

    listing = load_listing()
    offer = (listing.get("packs") or {}).get(pack) or {}  # type: ignore[union-attr]
    return str(offer.get("listing_name", pack))


if __name__ == "__main__":
    sys.exit(main())
