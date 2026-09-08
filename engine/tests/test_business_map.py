"""The business, derived — and the one figure it must never print as zero.

`INVARIANTS.md` made the code's rules checkable. `BUSINESS.md` does it one level
out, because asked "when will there be a financial result" the repository could
not say, and that was the finding rather than an evasion: every economics
primitive was built and none had seen a customer.

The failure this file guards is specific. This script reads the repository; it
cannot see Stripe, Supabase, Etsy or Lemon Squeezy. Printing an unobservable as
`€0.00` is the same class of mistake as a cost panel reading €0.00 while money
moves — which this codebase has already made once, in `3766976`. So "0 recorded"
must never render as "0 earned", and a missing log must never render as a
measurement.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import business_map
import pytest

REPO = Path(__file__).resolve().parents[2]


# ── elapsed time comes from git ───────────────────────────────────────────
def test_the_day_count_is_derived_from_the_first_commit() -> None:
    """Typed elapsed time is wrong the day after it is typed.

    Asserted on the arithmetic rather than on a fixed date, because CI checks
    out shallow and a hardcoded first commit made this test a statement about
    clone depth. That is what turned CI red and found the real defect below.
    """
    when = business_map.age(datetime(2026, 9, 4, tzinfo=UTC))
    assert when.commits > 0
    assert when.recent_commits <= when.commits
    if when.days is None:
        pytest.skip("shallow clone — elapsed time is refused, see the test below")
    expected = (
        datetime(2026, 9, 4, tzinfo=UTC)
        - datetime.strptime(when.first_commit, "%Y-%m-%d").replace(tzinfo=UTC)
    ).days
    assert when.days == expected


def test_the_day_count_moves_with_the_clock() -> None:
    early = business_map.age(datetime(2026, 8, 1, tzinfo=UTC))
    later = business_map.age(datetime(2026, 9, 4, tzinfo=UTC))
    if early.days is None or later.days is None:
        pytest.skip("shallow clone — elapsed time is refused")
    assert later.days - early.days == 34


def test_a_shallow_clone_refuses_to_report_a_day_count(monkeypatch: pytest.MonkeyPatch) -> None:
    """The defect CI found, and the reason this file exists at all.

    `actions/checkout@v4` fetches depth 1, so `git log --reverse` returns the one
    commit it has and the first commit LOOKS like today. The original script
    would have written "Day 0, 1 commit" — a plausible number nobody measured,
    which is exactly the failure BUSINESS.md is built to prevent. It now refuses
    instead, and says which checkout it could not measure from.
    """
    real = business_map._git

    def shallow(*args: str) -> str:
        if args[:2] == ("rev-parse", "--is-shallow-repository"):
            return "true"
        return real(*args)

    monkeypatch.setattr(business_map, "_git", shallow)
    when = business_map.age(datetime(2026, 9, 4, tzinfo=UTC))
    assert when.days is None
    assert when.shallow is True
    assert when.commits > 0, "commit count is still readable and should still be reported"

    page = business_map.render(datetime(2026, 9, 4, tzinfo=UTC))
    assert "not measurable from this checkout" in page
    assert "Day 0" not in page
    assert "plausible number nobody measured" in page


def test_elapsed_time_is_labelled_as_this_repository_only() -> None:
    """A repository cannot see the work that came before it.

    A figure that quietly counts something else is worse than no figure, and
    "day 37" read as "37 days of work" would be exactly that.
    """
    page = business_map.render(datetime(2026, 9, 4, tzinfo=UTC))
    assert "cannot see the work that came before it" in page
    if business_map.age().days is not None:
        assert "first commit in this repository" in page


# ── the registry is parsed in the form it is written in ───────────────────
def test_only_the_enabled_module_is_reported_live() -> None:
    assert business_map.live_modules() == ["studio"]


def test_a_single_line_regex_would_have_found_nothing() -> None:
    """The trap this parser exists for, kept as a test rather than a memory.

    `registry.ts` writes each manifest as a block, so `id` and `enabled` are on
    different lines. A pattern without DOTALL matches nothing and reports "no
    live modules" on a repository that has one — a silent zero, which is the
    shape of error this whole document is built against.
    """
    import re

    source = (REPO / "lib" / "modules" / "registry.ts").read_text(encoding="utf-8")
    naive = re.findall(r"id: '([a-z-]+)'.*enabled: true", source)
    assert naive == [], "the single-line form now matches; this test's premise is stale"
    assert business_map.live_modules() == ["studio"]


# ── goods agree with the listing gate ─────────────────────────────────────
def test_the_goods_table_agrees_with_the_listing_check() -> None:
    """Two readers of one truth. Disagreement means one of them is wrong."""
    import sys

    sys.path.insert(0, str(REPO / "packs"))
    from listing_check import load_listing, qc_count

    rows, promised, passed = business_map.goods()
    listing = load_listing()
    assert promised == sum(
        int(o["promised_images"])
        for o in listing["packs"].values()  # type: ignore[union-attr]
    )
    assert passed == sum(qc_count(r["pack"], REPO / "packs") or 0 for r in rows)


def test_every_pack_carries_its_live_flag() -> None:
    rows, _, _ = business_map.goods()
    assert rows and all("live" in row for row in rows)
    assert all(row["live"] is False for row in rows), "something went live; update the premise"


# ── money: absent is not zero ─────────────────────────────────────────────
def test_a_missing_log_is_not_reported_as_zero_earned(monkeypatch: pytest.MonkeyPatch) -> None:
    """The load-bearing refusal.

    "0 asked" and "20 asked, 0 replied" are different problems with opposite
    remedies, and without a log they are indistinguishable. Rendering either as
    €0.00 collapses them into a measurement nobody took.
    """
    monkeypatch.setattr(business_map, "REVENUE_LOG", REPO / "does-not-exist.json")
    assert business_map.revenue() == {"recorded": False}

    page = business_map.render(datetime(2026, 9, 4, tzinfo=UTC))
    assert "0 recorded, which is not 0 earned" in page
    assert "€0.00 recorded" not in page
    assert "different problems with opposite remedies" in page


def test_a_present_log_is_summarised(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    log = tmp_path / "REVENUE_LOG.json"
    log.write_text(
        json.dumps(
            {
                "entries": [
                    {"who": "acme", "outcome": "paid", "amount_eur": 49},
                    {"who": "beta", "outcome": "paid", "amount_eur": 19},
                    {"who": "gamma", "outcome": "no reply"},
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(business_map, "REVENUE_LOG", log)
    money = business_map.revenue()
    assert money == {"recorded": True, "asks": 3, "paid": 2, "eur": 68.0}

    page = business_map.render(datetime(2026, 9, 4, tzinfo=UTC))
    assert "€68.00" in page
    assert "3 recorded ask(s), 2 paid" in page


def test_an_ask_that_was_refused_is_not_counted_as_revenue(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """An ask is not a sale, and a log that blurs them is a log that flatters."""
    log = tmp_path / "REVENUE_LOG.json"
    log.write_text(
        json.dumps({"entries": [{"who": "acme", "outcome": "declined", "amount_eur": 490}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(business_map, "REVENUE_LOG", log)
    assert business_map.revenue()["paid"] == 0
    assert business_map.revenue()["eur"] == 0


# ── the document states its own blind spot ────────────────────────────────
def test_the_document_names_what_it_cannot_see() -> None:
    page = business_map.render(datetime(2026, 9, 4, tzinfo=UTC))
    for outside in ("Stripe", "Supabase", "Etsy", "Lemon Squeezy"):
        assert outside in page
    assert "recorded here" in page
    assert "3766976" in page, "the precedent for this exact mistake is unnamed"
