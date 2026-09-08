---
name: grounded-answers
description: Verify every sentence of a generated answer against the retrieved evidence and drop the ones the evidence does not support. Use when building RAG that must cite page numbers, when a model invents figures or citations, or when an answer needs to refuse rather than guess.
---

# Grounded answers

Retrieval gives the model evidence. Nothing makes it *use* the evidence. This
checks each sentence of the finished answer against the chunk it cites, and
removes what the chunk does not support.

Measured: **25,000–30,000 sentences/sec** on one core, and — the part that
actually matters — **flat with document size**: 30,229/s at 1,000 sentences,
29,881/s at 4,000, 29,546/s at 20,000. The absolute figure is your hardware and
will move between runs; the flatness is the property. Reproduce with
`cd engine && .venv/bin/python scripts/skill_numbers.py`.

It was not always flat. Citation restoration was O(sentences × citations) —
correct on every input, invisible on a three-sentence answer, and 880/s on a
four-thousand-sentence filing, which is where ingestion actually runs. No
correctness test could see it; the measurement did.

Throughput matters because the usual objection to verifying every sentence is
that it costs a second model call. It does not. This check is lexical and runs
on the machine that already has the answer.

## The three verdicts

```python
from omnex.rag import Grounder

checked = Grounder().check(answer, evidence_chunks)
checked.text          # the answer with unsupported sentences removed
checked.pages_cited   # pages actually used
checked.refused       # nothing survived
for c in checked.checks:
    c.verdict         # SUPPORTED | UNSUPPORTED | FABRICATED_CITATION | UNCITED | NO_CLAIM
```

**FABRICATED_CITATION** — the sentence cites a page that is not in the evidence.
This is a hard drop with no threshold to tune. A citation to a page the system
never retrieved is not a weak claim, it is a fake receipt, and it is the failure
that destroys trust in a RAG system fastest because the reader *checks* it.

**UNSUPPORTED** — cited a real page, but the claim is not in it. Two independent
rules, and the numeric one is not negotiable by threshold:

- content-word overlap below 0.5 (a correct paraphrase shares about half its
  content words; an invented entity introduces words the source never contains)
- **every number in the claim must appear in the cited chunk.** 4.2% and 8.4%
  differ by one token and are different facts. No amount of semantic similarity
  makes a wrong figure acceptable in a document a person will act on.

**NO_CLAIM** — "In summary," and headings assert nothing and are kept.

## The refusal is the feature

When nothing survives, `refused` is true and the answer is the refusal string.
A RAG system that always produces prose is a system that will produce prose when
the corpus does not contain the answer. That prose is fluent, cited, and wrong,
and it is worse than silence.

## What it misses, stated plainly

**Inverted polarity.** The evidence says "latency increases when the pool is
exhausted". The answer says "latency *decreases* when the pool is exhausted".
Same content words, same numbers, overlap near 1.0 — and it passes. This is
kept as a test in `engine/tests/test_rag.py` so it cannot quietly stop being
true.

Closing it needs an entailment model or a judge call: more accurate, one model
call per sentence on every request, and a second model that can also be wrong.
That is a deployment decision with a cost, so it is documented here rather than
made for you.

**Correct paraphrase with unusual vocabulary** can fall below the overlap
threshold and be dropped. The failure direction is deliberate: a dropped true
sentence is a support ticket, an accepted false figure is a decision made on
bad information.

## Companion

`oss/citegate` is the standalone version of the citation check, dependency-free,
for use outside this engine.
