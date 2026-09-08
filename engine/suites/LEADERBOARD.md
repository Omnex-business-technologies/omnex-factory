# FinGround leaderboard

Finance-domain grounding benchmark. 148 cases over a synthetic,
committed corpus, so any row here is reproducible:

```bash
python scripts/build_finance_suite.py
python scripts/leaderboard.py
```

Suite fingerprint `884533eb08028871` — a row scored against a different fingerprint
is not comparable and the harness refuses to compare it.

| System | Overall | Exact figure | Period | Unit | Refusal | Hallucination rate |
|---|--:|--:|--:|--:|--:|--:|
| extractive-baseline | 79.1% | 100.0% | 100.0% | 93.8% | 50.0% | 50.0% |
| always-answers | 55.4% | 93.8% | 100.0% | 87.5% | 0.0% | 100.0% |

## Why "hallucination rate" is next to the score

Overall pass rate alone rewards answering everything. 60 of
the 148 cases here are unanswerable, so a system that never refuses
scores well on the answerable majority and zero on the rest, which averages to
something respectable. The `always-answers` row is in the table precisely to show
that — it is not a strawman, it is what a system optimised for a single aggregate
looks like.

In finance a confident wrong figure is not a lower score than a refusal. It is a
materially worse outcome, and a leaderboard that cannot express the difference
will rank a confabulating system above a careful one.

## Why the corpus is synthetic

Real filings are copyrighted, and a benchmark built on scraped ones cannot be
redistributed — which is fatal for something meant to be reproducible by anyone.
These filings are generated deterministically with the ground truth known by
construction, which also makes contamination checkable rather than hoped about.
