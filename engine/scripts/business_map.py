"""What the business actually is, derived from files rather than remembered.

    python scripts/business_map.py

`INVARIANTS.md` made the code's rules checkable. This does the same one level
out: every number in `BUSINESS.md` is read from git, from `packs/listing.json`,
from the QC manifests and from `lib/modules/registry.ts`. Nothing is typed in,
so nothing can be optimistic by accident.

## Why this exists at all

Asked "when will there be a financial result", the honest answer was that the
repository could not say — and that was the finding, not an evasion. Every
economics primitive is built: margin per run, per agent, per customer, in exact
pico-dollars. None had seen a customer. A machine that can compute a portfolio
and has one asset reports `n=1. This is not a portfolio yet`, which is correct
and useless as a plan.

So the mechanism that made the code honest gets pointed at the business: a
generated document with a headline number that can get worse.

## The one thing it must never do

This reads the repository. It cannot see Stripe, Supabase, Etsy or Lemon
Squeezy. So "0 recorded" means zero recorded HERE, and printing that as "0
earned" would be the same class of lie as a cost panel reading €0.00 while money
moves. Every unobservable is named in its own section rather than defaulted to
zero.

## Elapsed time is measured from the first commit in THIS repository

Not from when the work started. A repository cannot see what came before it, and
a number that quietly counts something else is worse than no number.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
OUTPUT = REPO / "BUSINESS.md"
REVENUE_LOG = REPO / "REVENUE_LOG.json"


@dataclass(frozen=True)
class Age:
    """How long this repository has existed, and how busy it has been.

    `days` is `None` on a shallow clone. `actions/checkout@v4` fetches depth 1 by
    default, so `git log --reverse` returns the single fetched commit and the
    first commit LOOKS like today — which renders as "Day 0, 1 commit" and reads
    entirely plausible. A derived number that is quietly wrong is the exact
    failure this document exists to prevent, so it refuses to report rather than
    reporting a figure it cannot support.
    """

    first_commit: str
    days: int | None
    commits: int
    recent_commits: int
    shallow: bool = False


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True, check=False
    ).stdout.strip()


def age(today: datetime | None = None) -> Age:
    shallow = _git("rev-parse", "--is-shallow-repository") == "true"
    first = _git("log", "--reverse", "--format=%ad", "--date=short").splitlines()
    commits = int(_git("rev-list", "--count", "HEAD") or 0)
    recent = int(_git("rev-list", "--count", "--since=30 days ago", "HEAD") or 0)

    if shallow or not first:
        return Age(
            first_commit="unknown" if not first else first[0],
            days=None,
            commits=commits,
            recent_commits=recent,
            shallow=shallow,
        )

    started = datetime.strptime(first[0], "%Y-%m-%d").replace(tzinfo=UTC)
    now = today or datetime.now(UTC)
    return Age(
        first_commit=first[0],
        days=(now - started).days,
        commits=commits,
        recent_commits=recent,
    )


def live_modules() -> list[str]:
    """Modules `registry.ts` marks enabled.

    Parsed rather than imported: this is a Python script and the manifest is
    TypeScript. The block form is what the file actually uses, and a regex over
    one line would silently find nothing — which is how a check reports "no live
    modules" on a repository that has one.
    """
    source = (REPO / "lib" / "modules" / "registry.ts").read_text(encoding="utf-8")
    return [
        block.group(1)
        for block in re.finditer(r"id:\s*'([a-z-]+)'[^}]*?enabled:\s*true", source, re.DOTALL)
    ]


def goods() -> tuple[list[dict[str, object]], int, int]:
    """Per-pack readiness, plus totals, straight from the QC manifests."""
    import sys

    sys.path.insert(0, str(REPO / "packs"))
    from listing_check import load_listing, qc_count

    listing = load_listing()
    rows: list[dict[str, object]] = []
    promised = passed = 0
    for pack, offer in sorted((listing.get("packs") or {}).items()):
        have = qc_count(pack, REPO / "packs")
        want = int(offer["promised_images"])
        promised += want
        passed += have or 0
        rows.append(
            {
                "pack": pack,
                "listing": offer["listing_name"],
                "price_eur": offer.get("price_eur"),
                "promised": want,
                "passed": have,
                "live": bool(offer.get("live")),
            }
        )
    return rows, promised, passed


def revenue() -> dict[str, object]:
    """What has been asked for and what has been paid, if anybody wrote it down.

    Absent is not zero. A missing log means nobody recorded, which is a
    different problem from nobody paying — and the two need opposite responses.
    """
    if not REVENUE_LOG.exists():
        return {"recorded": False}
    payload = json.loads(REVENUE_LOG.read_text(encoding="utf-8"))
    entries: list[dict[str, object]] = payload.get("entries") or []
    paid = [e for e in entries if e.get("outcome") == "paid"]
    return {
        "recorded": True,
        "asks": len(entries),
        "paid": len(paid),
        "eur": sum(float(e.get("amount_eur", 0)) for e in paid),
    }


def _elapsed(when: Age) -> str:
    """The headline, or a refusal to produce one from a checkout that cannot support it."""
    if when.days is None:
        reason = (
            "the clone is shallow, so the first commit cannot be read"
            if when.shallow
            else "there is no commit history here"
        )
        return (
            f"**Elapsed time is not measurable from this checkout** — {reason}. "
            f"{when.commits} commit(s) visible. Reporting a day count anyway would "
            "print a plausible number nobody measured."
        )
    return (
        f"**Day {when.days}** since the first commit in this repository "
        f"({when.first_commit}), {when.commits} commits, {when.recent_commits} in the "
        "last 30 days."
    )


def render(today: datetime | None = None) -> str:
    when = age(today)
    rows, promised, passed = goods()
    modules = live_modules()
    money = revenue()
    live_listings = [r for r in rows if r["live"]]

    if money["recorded"]:
        headline_money = f"€{money['eur']:.2f} recorded across {money['paid']} paid order(s)"
    else:
        headline_money = "no revenue log exists — **0 recorded, which is not 0 earned**"

    lines = [
        "# Business — the numbers, derived",
        "",
        "Generated by `engine/scripts/business_map.py`. Do not edit.",
        "",
        _elapsed(when),
        "",
        f"**Money:** {headline_money}.",
        "",
        f"**Goods:** {passed} of {promised} promised images have passed QC "
        f"({promised - passed} short). {len(live_listings)} listing(s) live, "
        f"{len(modules)} module(s) enabled.",
        "",
        "Elapsed time is measured from the first commit HERE. A repository cannot "
        "see the work that came before it, and a number that quietly counts "
        "something else is worse than no number.",
        "",
        "## Goods against the promise",
        "",
        "| pack | listing | € | promised | passed QC | short | live |",
        "|---|---|--:|--:|--:|--:|:-:|",
    ]
    for row in rows:
        have = row["passed"]
        shown = "—" if have is None else str(have)
        short = "" if have is None else str(max(int(row["promised"]) - int(have), 0) or "")
        lines.append(
            f"| {row['pack']} | {row['listing']} | {row['price_eur']} | {row['promised']} | "
            f"{shown} | {short} | {'yes' if row['live'] else 'no'} |"
        )

    lines += [
        "",
        "## What is selling",
        "",
        f"- Listings live: {', '.join(r['pack'] for r in live_listings) or '**none**'}",
        f"- Modules enabled: {', '.join(modules) or '**none**'}",
        "",
        "`lib/modules/registry.ts` holds the rule that module N+1 does not open "
        "until module N has taken a real payment, and `packs/listing.json` carries "
        "the same shape for listings. Both are green while nothing sells, which is "
        "the honest state rather than a passing grade.",
        "",
        "## The ask log",
        "",
    ]
    if money["recorded"]:
        lines.append(f"{money['asks']} recorded ask(s), {money['paid']} paid, €{money['eur']:.2f}.")
    else:
        lines += [
            "`REVENUE_LOG.json` does not exist, so there is no record of anybody "
            "being asked to buy anything.",
            "",
            'That is the number worth having, because **"0 asked" and "20 asked, 0 '
            'replied" are different problems with opposite remedies** — and without '
            "a log they are indistinguishable. Zero recorded is not zero earned, and "
            "it is not zero asked either. It is nobody having written it down.",
        ]

    lines += [
        "",
        "## What this document cannot see",
        "",
        "It reads the repository. Stripe, Supabase, Etsy and Lemon Squeezy are "
        "outside it, so every figure above is *recorded here*, never *what "
        "happened*. Printing an unobservable as zero is the same class of mistake "
        "as a cost panel reading €0.00 while money moves — which this codebase has "
        "already made once, in `3766976`.",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    OUTPUT.write_text(render(), encoding="utf-8")
    when = age()
    rows, promised, passed = goods()
    print(
        f"day {when.days} · {when.commits} commits"
        if when.days is not None
        else f"elapsed unmeasurable (shallow clone) · {when.commits} commit(s) visible"
    )
    print(f"goods    {passed}/{promised} images through QC ({promised - passed} short)")
    print(
        f"live     {len([r for r in rows if r['live']])} listing(s), {len(live_modules())} module(s)"
    )
    print(f"revenue  {'logged' if revenue()['recorded'] else 'no log exists'}")
    print(f"\nwrote {OUTPUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
