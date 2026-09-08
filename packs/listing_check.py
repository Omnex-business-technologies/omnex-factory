"""A listing may not promise more than QC actually passed.

    python packs/listing_check.py

`GIG.md` writes the offer. `packs/*/manifest.json` records what came out of
`qc.py`. Between them there was nothing, and the gap is not small: the Complete
Vault sells "170+ images" for €49 while the four manifests total **80**.

Listing that is not a rounding error. It is a refund, a one-star review, and on
Etsy an account risk — and the person who finds out is the buyer, after paying.
So this refuses to let the promise and the goods drift, in the direction that
matters: a promise may shrink to fit the goods, the goods may never be assumed
to fit the promise.

## Why the manifest rather than the directory

`.gitignore` keeps `packs/*/` out of the repository and admits exactly one file
back: `!packs/*/manifest.json`. The images live on the machine that generated
them; the manifest is the committed record of what passed. So CI can check the
promise against the QC record everywhere, and only the machine holding the files
can check the files — which is `build_pack.py`'s job, not this one's.

That split is deliberate. A check that silently passes because it could not see
the data is worse than one that says which half it verified.

## A bundle is checked against its members' REAL counts

The Vault promises 170 and its four packs promise 50 + 40 + 40 + 40 = 170. It
would be easy, and wrong, to check promise against promise — the sum agrees with
itself while every pack is short. The bundle is compared against what the
members actually have.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

PACKS = Path(__file__).resolve().parent
LISTING = PACKS / "listing.json"


@dataclass(frozen=True)
class Shortfall:
    """One promise the goods do not cover."""

    listing: str
    promised: int
    have: int

    @property
    def missing(self) -> int:
        return self.promised - self.have

    def __str__(self) -> str:
        return (
            f"{self.listing}: promises {self.promised}, "
            f"{self.have} passed QC — {self.missing} short"
        )


def load_listing(path: Path | None = None) -> dict[str, object]:
    return json.loads((path or LISTING).read_text(encoding="utf-8"))


def qc_count(pack: str, root: Path | None = None) -> int | None:
    """How many images this pack's QC manifest records. `None` when absent.

    `None` is not zero. A pack with no manifest has never been through QC, and
    reporting that as "0 passed" invites somebody to read it as a pack that
    failed rather than one nobody has run.
    """
    manifest = (root or PACKS) / pack / "manifest.json"
    if not manifest.exists():
        return None
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    images = payload.get("images")
    if isinstance(images, list):
        # The list is the record; `count` is a summary of it and can drift.
        return len(images)
    count = payload.get("count")
    return int(count) if isinstance(count, int) else None


def audit(listing: dict[str, object], root: Path | None = None) -> tuple[list[Shortfall], list[str]]:
    """Shortfalls and other problems, collected rather than raised one at a time."""
    root = root or PACKS
    shortfalls: list[Shortfall] = []
    problems: list[str] = []

    packs: dict[str, dict[str, object]] = listing.get("packs") or {}  # type: ignore[assignment]
    have: dict[str, int] = {}

    for pack, offer in sorted(packs.items()):
        counted = qc_count(pack, root)
        if counted is None:
            problems.append(f"{pack}: no QC manifest — nothing has passed the gate")
            continue
        have[pack] = counted
        promised = int(offer["promised_images"])  # type: ignore[arg-type]
        if counted < promised:
            shortfalls.append(Shortfall(str(offer["listing_name"]), promised, counted))

    licence = str(listing.get("licence_file", ""))
    if licence and not (root / licence).exists():
        problems.append(
            f"the listing claims {listing.get('licence_claim')!r} and {licence} is not in packs/"
        )

    bundles: dict[str, dict[str, object]] = listing.get("bundles") or {}  # type: ignore[assignment]
    for name, bundle in sorted(bundles.items()):
        members: list[str] = list(bundle.get("includes") or [])  # type: ignore[arg-type]
        unknown = [m for m in members if m not in packs]
        if unknown:
            problems.append(f"bundle {name}: includes packs that are not listed: {unknown}")
        # Against what the members HAVE, never against what they promise — the
        # sum of promises agrees with the bundle's promise by construction.
        total = sum(have.get(member, 0) for member in members)
        promised = int(bundle["promised_images"])  # type: ignore[arg-type]
        if total < promised:
            shortfalls.append(Shortfall(str(bundle["listing_name"]), promised, total))

    return shortfalls, problems


def render(listing: dict[str, object], root: Path | None = None) -> str:
    root = root or PACKS
    packs: dict[str, dict[str, object]] = listing.get("packs") or {}  # type: ignore[assignment]
    lines = [f"{'pack':<12} {'promised':>9} {'passed QC':>10} {'short':>7}  listing"]
    for pack, offer in sorted(packs.items()):
        counted = qc_count(pack, root)
        promised = int(offer["promised_images"])  # type: ignore[arg-type]
        shown = "—" if counted is None else str(counted)
        short = "" if counted is None else str(max(promised - counted, 0) or "")
        lines.append(
            f"{pack:<12} {promised:>9} {shown:>10} {short:>7}  {offer['listing_name']}"
        )
    bundles: dict[str, dict[str, object]] = listing.get("bundles") or {}  # type: ignore[assignment]
    for name, bundle in sorted(bundles.items()):
        members: list[str] = list(bundle.get("includes") or [])  # type: ignore[arg-type]
        total = sum(qc_count(m, root) or 0 for m in members)
        promised = int(bundle["promised_images"])  # type: ignore[arg-type]
        lines.append(
            f"{name:<12} {promised:>9} {total:>10} {max(promised - total, 0) or '':>7}  "
            f"{bundle['listing_name']}"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PACKS, help="packs directory")
    args = parser.parse_args()

    listing = load_listing()
    print(render(listing, args.root))
    shortfalls, problems = audit(listing, args.root)

    if not shortfalls and not problems:
        print("\nevery listing is covered by goods that passed QC")
        return 0

    print()
    for problem in problems:
        print(f"FAIL {problem}")
    for shortfall in shortfalls:
        print(f"FAIL {shortfall}")
    print(
        f"\n{len(shortfalls)} listing(s) promise more than exists. Generate the "
        "missing images, or lower the promise in packs/listing.json AND in GIG.md — "
        "in that order, because the copy is what a buyer reads."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
