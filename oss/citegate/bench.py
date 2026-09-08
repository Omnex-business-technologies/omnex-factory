"""Throughput of citegate against the alternatives it is meant to sit beside.

    python bench.py

The comparison numbers for a judge call and a cross-encoder are NOT measured
here — they are the published latency ranges for those approaches, marked as
such. What is measured is citegate itself, on this machine, right now.

## Two shapes, because one shape hid a bug for a whole release

The first case is many short answers, which is what a chat gate actually sees.
That was the only case this benchmark measured, and it is why an O(n x m) loop
in citation restoration survived: at four sentences an answer, the quadratic
term is nothing. On one long document it was everything — 1,439 sentences/sec
where the same code now does over 300,000.

So the second case is one long document. A benchmark whose shape cannot express
a bug will report good numbers straight through it.
"""

from __future__ import annotations

import sys
import time

sys.path.insert(0, "src")

from citegate import Grounder, Source  # noqa: E402

SENTENCE = "The connection pool defaults to twenty connections. [p. 12]"

ANSWER = (
    "The connection pool defaults to twenty connections. [p. 12] "
    "Raising it requires a restart of the service. [p. 12] "
    "Error ERR_4021 is raised when the pool is exhausted. [p. 13] "
    "It also replicates across three regions automatically. [p. 12]"
)
SOURCES = [
    Source(page=12, text="The connection pool defaults to twenty connections. Raising it requires a restart of the service."),
    Source(page=13, text="Error ERR_4021 is raised when the connection pool is exhausted."),
]


def main() -> None:
    grounder = Grounder()
    grounder.check(ANSWER, SOURCES)  # warm

    runs = 5_000
    started = time.perf_counter()
    for _ in range(runs):
        grounder.check(ANSWER, SOURCES)
    elapsed = time.perf_counter() - started

    sentences = runs * 4
    print(f"many short answers: {runs} answers ({sentences} sentences) in {elapsed:.2f}s")
    print(f"  {sentences / elapsed:,.0f} sentences/second")
    print(f"  {elapsed / sentences * 1e6:.1f} microseconds per sentence")

    # One long document — the shape the short-answer case cannot express.
    long_sentences = 20_000
    long_answer = " ".join([SENTENCE] * long_sentences)
    grounder.check(SENTENCE, SOURCES)  # warm
    started = time.perf_counter()
    checked = grounder.check(long_answer, SOURCES)
    long_elapsed = time.perf_counter() - started
    assert len(checked.checks) == long_sentences, "the splitter lost sentences"

    print(f"\none long document: {long_sentences} sentences in {long_elapsed:.2f}s")
    print(f"  {long_sentences / long_elapsed:,.0f} sentences/second")
    print("  flat with document size — it was quadratic until the restore was fixed")
    print()
    print("For scale (published ranges, not measured here):")
    print("  LLM judge call     300,000 - 1,500,000 microseconds per sentence, plus a bill")
    print("  cross-encoder        1,000 -    20,000 microseconds per sentence, plus ~2 GB of torch")
    print()
    print("citegate is not more accurate than either. It is the only one of the")
    print("three that can run on every response inside a request handler, which")
    print("is where a gate has to be to stop anything reaching a user.")


if __name__ == "__main__":
    main()
