---
name: finground
description: A 148-case finance grounding benchmark that scores hallucination rate next to pass rate, on a synthetic redistributable corpus. Use when evaluating whether a RAG or extraction system can be trusted on filings, or when a single aggregate score is hiding that a system never refuses.
---

# FinGround

148 cases over a committed synthetic filing corpus. **60 of them are
unanswerable** — the figure is genuinely not in the document.

| System | Overall | Exact figure | Period | Unit | Refusal | Hallucination |
|---|--:|--:|--:|--:|--:|--:|
| extractive-baseline | **79.1%** | 100.0% | 100.0% | 93.8% | 50.0% | **50.0%** |
| always-answers | 55.4% | 93.8% | 100.0% | 87.5% | 0.0% | **100.0%** |

Suite fingerprint `884533eb08028871`. A row scored against a different
fingerprint is not comparable and the harness refuses to compare it.

```bash
cd engine
.venv/bin/python scripts/build_finance_suite.py
.venv/bin/python scripts/leaderboard.py
```

## Why hallucination rate sits next to the score

Overall pass rate alone rewards answering everything. With 60 of 148 cases
unanswerable, a system that never refuses scores well on the answerable majority
and zero on the rest, which averages to something respectable.

The `always-answers` row is in the table for exactly that reason. It is not a
strawman — it is what a system optimised against a single aggregate looks like,
and it is what you will build if the aggregate is the only thing you watch.

In finance a confident wrong figure is not a lower score than a refusal. It is a
materially worse outcome, and a leaderboard that cannot express the difference
will rank a confabulating system above a careful one.

## Why the corpus is synthetic

Real filings are copyrighted. A benchmark built on scraped ones cannot be
redistributed, which is fatal for something meant to be reproducible by anyone
who wants to check the numbers.

These filings are generated deterministically with ground truth known by
construction. That also makes contamination *checkable* rather than hoped
about — you can prove a model has not memorised a document that did not exist
before you generated it.

The cost is realism: synthetic filings are cleaner than the real thing, so a
score here is an upper bound on a score against real documents. Stated because
it is the first thing a serious evaluator will ask.

## Four dimensions, not one

A finance answer is wrong in distinguishable ways, and collapsing them loses the
information you need to fix anything:

- **exact figure** — the number itself
- **period** — right number, wrong quarter. Common, and invisible in a pass rate.
- **unit** — thousands versus millions. The expensive one.
- **refusal** — did it decline when the document does not contain the answer

The baseline above scores 100% on figures and 93.8% on units. Those are
different problems with different fixes, and one aggregate would have told you
neither.

## Adding a system

Score it, append the row, and keep the fingerprint. The harness refuses a
comparison across fingerprints rather than silently producing one, because an
edited expected answer is otherwise indistinguishable from an improvement.
