"""Generate FinGround — a finance-domain grounding benchmark.

Most public RAG benchmarks measure whether the right passage was retrieved. That
is the easy half. In finance the expensive failure is different and specific:
the system retrieves the right filing, produces a fluent sentence, and gets the
NUMBER wrong — or attributes a figure to the wrong period, or restates a
guidance range as a commitment. Nobody notices, because the answer reads exactly
like the correct one.

So FinGround scores four things a general benchmark does not:

    exact_figure   the number must match the source, digit for digit
    period         Q3 vs Q4, FY2025 vs FY2024 — the same figure, different claim
    unit           thousands vs millions, reported vs constant currency
    unanswerable   the filing genuinely does not say, and saying so is correct

Two fifths of the suite is unanswerable. In this domain a confident wrong answer
is not a lower score than a refusal — it is a materially worse outcome, and a
benchmark that treats them as equally wrong will rank a confabulating system
above a careful one.

The corpus is SYNTHETIC and says so. Real filings are copyrighted, and a
benchmark built on scraped ones cannot be redistributed, which is fatal for
something meant to be reproducible by anyone. Synthetic filings are generated
here, deterministically, with the ground truth known by construction — which
also makes contamination checkable rather than hoped about.

    python scripts/build_finance_suite.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITES = ROOT / "suites"

COMPANIES = [
    ("Northwind Logistics", "NWL"),
    ("Cobalt Systems", "CBS"),
    ("Harbour Analytics", "HBA"),
    ("Meridian Foods", "MRF"),
    ("Vantage Robotics", "VGR"),
    ("Ashford Energy", "AFE"),
    ("Lyric Health", "LYH"),
    ("Ironvale Mining", "IVM"),
]

QUARTERS = ["Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"]


def build_corpus() -> tuple[list[str], list[dict[str, object]]]:
    """One page per company-quarter, with the figures known by construction."""
    pages: list[str] = []
    facts: list[dict[str, object]] = []

    page = 0
    for company, ticker in COMPANIES:
        base_revenue = 120 + len(company) * 7
        for index, quarter in enumerate(QUARTERS):
            page += 1
            revenue = base_revenue + index * 13
            margin = round(18.4 + index * 1.3, 1)
            headcount = 1_200 + index * 45
            # Guidance is a RANGE and is phrased as one. A system that reports
            # the midpoint as a commitment has changed the claim.
            guidance_low = revenue + 8
            guidance_high = revenue + 21

            pages.append(
                f"{company} ({ticker}) — {quarter} results. "
                f"Revenue for {quarter} was {revenue}.0 million euros, reported in millions. "
                f"Gross margin for {quarter} was {margin} percent. "
                f"Headcount at the end of {quarter} was {headcount} employees. "
                f"Management guides {ticker} revenue for the following quarter to a range of "
                f"{guidance_low}.0 to {guidance_high}.0 million euros. "
                f"No dividend was declared for {quarter}."
            )
            facts.append(
                {
                    "company": company,
                    "ticker": ticker,
                    "quarter": quarter,
                    "page": page,
                    "revenue": revenue,
                    "margin": margin,
                    "headcount": headcount,
                    "guidance_low": guidance_low,
                    "guidance_high": guidance_high,
                }
            )

    return pages, facts


def build_suite(facts: list[dict[str, object]]) -> dict[str, object]:
    cases: list[dict[str, object]] = []

    for fact in facts:
        ticker, quarter, page = fact["ticker"], fact["quarter"], fact["page"]

        cases.append(
            {
                "id": f"figure-revenue-{ticker}-{str(quarter).replace(' ', '')}",
                "question": f"What was {ticker} revenue in {quarter}?",
                "expected": f"{ticker} revenue in {quarter} was {fact['revenue']}.0 million euros.",
                "must_cite": [page],
                "tags": ["exact_figure", "revenue"],
            }
        )
        cases.append(
            {
                "id": f"figure-margin-{ticker}-{str(quarter).replace(' ', '')}",
                "question": f"What was the gross margin for {ticker} in {quarter}?",
                "expected": f"Gross margin for {quarter} was {fact['margin']} percent.",
                "must_cite": [page],
                "tags": ["exact_figure", "margin"],
            }
        )

    # Period discrimination: the same figure, a different quarter. A system that
    # retrieves the company and reports whichever number it found scores well on
    # a general benchmark and is wrong here.
    for fact in facts:
        if fact["quarter"] != "Q3 2025":
            continue
        cases.append(
            {
                "id": f"period-{fact['ticker']}-q3-not-q4",
                "question": f"What was {fact['ticker']} revenue in Q3 2025, not Q4?",
                "expected": f"Revenue for Q3 2025 was {fact['revenue']}.0 million euros.",
                "must_cite": [fact["page"]],
                "tags": ["period", "revenue"],
            }
        )

    # Guidance is a range. Reporting the midpoint as a commitment is a different
    # and materially worse claim than the one the filing makes.
    for fact in facts[:16]:
        cases.append(
            {
                "id": f"unit-guidance-{fact['ticker']}-{str(fact['quarter']).replace(' ', '')}",
                "question": f"What is the revenue guidance for {fact['ticker']} after {fact['quarter']}?",
                "expected": (
                    f"Guidance is a range of {fact['guidance_low']}.0 to "
                    f"{fact['guidance_high']}.0 million euros."
                ),
                "must_cite": [fact["page"]],
                "tags": ["unit", "guidance"],
            }
        )

    # Unanswerable: plausible, specific, and genuinely absent. Two fifths of the
    # suite, because in this domain a confident wrong answer is materially worse
    # than a refusal rather than merely a lower score.
    absent = [
        ("net_income", "What was {t} net income in {q}?"),
        ("ceo", "Who is the chief executive of {t}?"),
        ("capex", "What was capital expenditure for {t} in {q}?"),
        ("debt", "What is {t} total debt at the end of {q}?"),
        ("tax_rate", "What effective tax rate did {t} report for {q}?"),
        ("segment", "How much of {t} revenue in {q} came from Europe?"),
    ]
    for kind, template in absent:
        for fact in facts[:10]:
            cases.append(
                {
                    "id": f"unanswerable-{kind}-{fact['ticker']}-{str(fact['quarter']).replace(' ', '')}",
                    "question": template.format(t=fact["ticker"], q=fact["quarter"]),
                    "expected": "",
                    "expect_refusal": True,
                    "tags": ["unanswerable", kind],
                }
            )

    return {"name": "finground", "version": "1", "cases": cases}


def main() -> None:
    SUITES.mkdir(parents=True, exist_ok=True)
    pages, facts = build_corpus()
    (SUITES / "finground_corpus.json").write_text(
        json.dumps({"doc_id": "filings", "pages": pages, "synthetic": True}, indent=2)
    )
    suite = build_suite(facts)
    (SUITES / "finground.json").write_text(json.dumps(suite, indent=2))

    tags: dict[str, int] = {}
    for case in suite["cases"]:  # type: ignore[index]
        for tag in case["tags"]:  # type: ignore[index]
            tags[tag] = tags.get(tag, 0) + 1
    total = len(suite["cases"])  # type: ignore[arg-type]
    print(f"FinGround: {total} cases over {len(pages)} synthetic filing pages")
    for tag, count in sorted(tags.items()):
        print(f"  {tag:<14} {count:>4}  ({count / total:.0%})")


if __name__ == "__main__":
    main()
