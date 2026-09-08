"""FinGround (P17) — the properties that make the benchmark worth publishing.

A benchmark is a claim about other people's systems, so the bar is higher than
for ordinary code: if the ground truth is wrong, every score computed against it
is wrong in a way nobody downstream can detect. These tests check the three
things that would invalidate it — ground truth that is not actually in the
corpus, "unanswerable" cases the corpus quietly answers, and prose in the
published leaderboard that has drifted from the data it describes.

The last test is the one the whole benchmark exists for.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from build_finance_suite import QUARTERS, build_corpus, build_suite
from leaderboard import run

ROOT = Path(__file__).resolve().parents[1]
SUITES = ROOT / "suites"


def test_the_corpus_is_deterministic() -> None:
    """Regenerating must not move the ground truth under a published score.

    A benchmark whose corpus changes between runs makes every previously
    reported number incomparable, and nothing in the score itself reveals it.
    """
    first_pages, first_facts = build_corpus()
    second_pages, second_facts = build_corpus()
    assert first_pages == second_pages
    assert first_facts == second_facts


def test_the_committed_corpus_matches_the_generator() -> None:
    committed = json.loads((SUITES / "finground_corpus.json").read_text())
    pages, _ = build_corpus()
    assert committed["pages"] == pages
    # The synthetic flag is what makes the corpus redistributable. If it ever
    # goes false, the licence story goes with it.
    assert committed["synthetic"] is True


def test_every_answerable_expectation_appears_in_the_page_it_cites() -> None:
    """The ground truth is known by construction — this checks it actually is.

    `expected` is written by the generator from the same fact dict that wrote
    the page, so a divergence here means the two drifted apart and the suite is
    scoring answers against figures no filing contains.
    """
    pages, facts = build_corpus()
    suite = build_suite(facts)

    checked = 0
    for case in suite["cases"]:  # type: ignore[index]
        if case.get("expect_refusal"):
            continue
        page_text = pages[int(case["must_cite"][0]) - 1]
        for number in re.findall(r"\d+\.?\d*", str(case["expected"])):
            assert number in page_text, f"{case['id']}: {number} is not on its cited page"
            checked += 1
    assert checked > 200


def test_unanswerable_cases_are_genuinely_absent_from_the_corpus() -> None:
    """A refusal case the corpus secretly answers punishes the correct answer.

    This is the failure that makes a benchmark actively harmful: a careful
    system reads the page, finds the figure, reports it, and is marked wrong.
    """
    pages, facts = build_corpus()
    corpus = " ".join(pages).lower()
    suite = build_suite(facts)

    subjects = ["net income", "chief executive", "capital expenditure", "total debt", "tax rate"]
    refusals = [c for c in suite["cases"] if c.get("expect_refusal")]  # type: ignore[union-attr]
    assert len(refusals) == 60

    for subject in subjects:
        assert subject not in corpus, f"the corpus answers {subject!r} — it cannot be unanswerable"


def test_a_period_case_names_a_quarter_the_corpus_distinguishes() -> None:
    """Period discrimination only tests anything if the quarters really differ."""
    _, facts = build_corpus()
    revenues_by_company: dict[str, set[int]] = {}
    for fact in facts:
        revenues_by_company.setdefault(str(fact["ticker"]), set()).add(int(fact["revenue"]))
    for ticker, revenues in revenues_by_company.items():
        assert len(revenues) == len(QUARTERS), f"{ticker} repeats a revenue figure across quarters"


def test_the_leaderboard_prose_matches_the_data_it_describes() -> None:
    """Published prose drifts from published numbers. Here it cannot.

    The document states how many cases are unanswerable as an argument for its
    own scoring design. If the suite grows and the sentence does not, the
    argument silently becomes false while still reading as authoritative.
    """
    text = (SUITES / "LEADERBOARD.md").read_text()
    suite = json.loads((SUITES / "finground.json").read_text())
    total = len(suite["cases"])
    unanswerable = sum(1 for c in suite["cases"] if c.get("expect_refusal"))

    assert f"{total} cases" in text
    assert f"{unanswerable} of" in text


def test_overall_score_alone_would_rank_a_confabulator_respectably() -> None:
    """The claim the whole benchmark is built to support.

    `always-answers` never refuses. On a single aggregate it lands in the
    fifties — unremarkable rather than disqualifying, and comfortably inside the
    range where a vendor would publish it. The hallucination column is what
    separates the two systems: it answers 100% of the questions whose filings do
    not contain the answer.

    If this test ever fails because the gap narrowed, the benchmark has stopped
    doing its job and the leaderboard design needs revisiting — not the number.
    """
    careful = run("extractive-baseline")
    confabulator = run("always-answers")

    # On the aggregate alone the gap is real but not damning.
    assert float(confabulator["overall"]) > 0.5
    assert float(careful["overall"]) - float(confabulator["overall"]) < 0.30

    # On the column that matters in this domain, it is total.
    assert float(confabulator["hallucination_rate"]) == 1.0
    assert float(careful["hallucination_rate"]) < float(confabulator["hallucination_rate"])


def test_the_extractive_baseline_still_hallucinates_half_the_time() -> None:
    """A stated limitation, kept as a passing test rather than a footnote.

    The reference system is not good — it refuses only half the cases it should.
    Recording that here means an improvement has to move this number to change
    the test, and nobody can mistake the baseline for a solved problem.
    """
    careful = run("extractive-baseline")
    assert float(careful["refusal"]) == 0.5
    assert float(careful["hallucination_rate"]) == 0.5
