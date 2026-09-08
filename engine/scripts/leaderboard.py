"""Score a system on FinGround and render the public leaderboard.

    python scripts/leaderboard.py --system extractive-baseline

A leaderboard is only worth publishing if a reader can reproduce a row, so the
generated table carries the suite fingerprint and the corpus is synthetic and
committed. "Trust our number" is not a benchmark.

The columns are chosen so a confabulating system cannot top the table. Overall
pass rate alone rewards answering everything: a system that never refuses scores
100% on the answerable third and 0% on the unanswerable third, which averages to
a respectable-looking number. So `refusal` is its own column and `hallucination
rate` — answered when it should have refused — is reported next to the score.
In finance that is the number that matters, because a confident wrong figure is
not a lower score, it is a materially worse outcome.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from omnex.core import FakeClock, IdFactory, Money
from omnex.evals import (
    EvalRunner,
    GoldenCase,
    MetricResult,
    Suite,
    citation_accuracy,
    context_recall,
    faithfulness,
    refusal_accuracy,
)
from omnex.rag import REFUSAL, Document, RagConfig, RagPipeline, chunk_document
from omnex.vectors import HashingEmbedder, HybridStore

ROOT = Path(__file__).resolve().parents[1]


def run(system: str) -> dict[str, object]:
    from eval_gate import extractive_answer  # the reference system

    from omnex.llm import ScriptedModel, Tier, spec_for

    payload = json.loads((ROOT / "suites" / "finground_corpus.json").read_text())
    document = Document.from_pages(payload["doc_id"], payload["pages"])
    store = HybridStore(embedder=HashingEmbedder(), candidates=20)
    store.upsert(chunk_document(document, target_chars=420, ids=IdFactory(clock=FakeClock())))
    spec = spec_for("local/bench", Tier.SMALL, "0", "0")

    suite = Suite.load(ROOT / "suites" / "finground.json")
    suite.validate()

    def answerer(case: GoldenCase) -> tuple[str, dict[str, MetricResult], Money]:
        hits = store.search(case.question, limit=4)
        if system == "always-answers":
            # The system a naive leaderboard would rank highly: never refuses.
            reply = (
                f"{hits[0].chunk.text.split('.')[0]}. {hits[0].chunk.cite}"
                if hits
                else "Unable to determine."
            )
        else:
            reply = extractive_answer(case.question, hits) or REFUSAL

        model = ScriptedModel(model_spec=spec, responses=[reply], output_tokens=60)
        answer = RagPipeline(
            store=store, model=model, config=RagConfig(max_regenerations=0), clock=FakeClock()
        ).answer(case.question)

        if case.expect_refusal:
            return (
                answer.text,
                {"refusal_accuracy": refusal_accuracy(answer.text, expect_refusal=True)},
                answer.cost,
            )

        metrics = {
            "context_recall": context_recall(answer.hits, case.relevant_chunks),
            "faithfulness": faithfulness(answer.text, [h.chunk for h in answer.hits]),
            "refusal_accuracy": refusal_accuracy(answer.text, expect_refusal=False),
        }
        if case.must_cite:
            metrics["citation_accuracy"] = citation_accuracy(answer.text, case.must_cite)
        return answer.text, metrics, answer.cost

    report = EvalRunner(suite).run(answerer, label=system, now="2026-08-05T00:00:00Z")
    by_tag = report.by_tag()
    unanswerable = [r for r in report.results if "unanswerable" in r.tags]
    hallucinated = sum(1 for r in unanswerable if not r.passed(report.thresholds))

    return {
        "system": system,
        "overall": report.pass_rate,
        "exact_figure": by_tag.get("exact_figure", 0.0),
        "period": by_tag.get("period", 0.0),
        "unit": by_tag.get("unit", 0.0),
        "refusal": by_tag.get("unanswerable", 0.0),
        "hallucination_rate": hallucinated / len(unanswerable) if unanswerable else 0.0,
        "cases": len(report.results),
        "unanswerable": len(unanswerable),
        "fingerprint": report.suite_fingerprint,
    }


def render(rows: list[dict[str, object]]) -> str:
    header = (
        "| System | Overall | Exact figure | Period | Unit | Refusal | Hallucination rate |\n"
        "|---|--:|--:|--:|--:|--:|--:|"
    )
    lines = [header]
    for row in sorted(rows, key=lambda r: (-float(r["overall"]), float(r["hallucination_rate"]))):
        lines.append(
            f"| {row['system']} | {float(row['overall']):.1%} | "
            f"{float(row['exact_figure']):.1%} | {float(row['period']):.1%} | "
            f"{float(row['unit']):.1%} | {float(row['refusal']):.1%} | "
            f"{float(row['hallucination_rate']):.1%} |"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--systems", nargs="*", default=["extractive-baseline", "always-answers"])
    parser.add_argument("--out", default="suites/LEADERBOARD.md")
    args = parser.parse_args()

    rows = [run(system) for system in args.systems]
    table = render(rows)
    fingerprint = rows[0]["fingerprint"]

    body = f"""# FinGround leaderboard

Finance-domain grounding benchmark. {rows[0]["cases"]} cases over a synthetic,
committed corpus, so any row here is reproducible:

```bash
python scripts/build_finance_suite.py
python scripts/leaderboard.py
```

Suite fingerprint `{fingerprint}` — a row scored against a different fingerprint
is not comparable and the harness refuses to compare it.

{table}

## Why "hallucination rate" is next to the score

Overall pass rate alone rewards answering everything. {rows[0]["unanswerable"]} of
the {rows[0]["cases"]} cases here are unanswerable, so a system that never refuses
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
"""
    (ROOT / args.out).write_text(body)
    print(table)
    print(f"\nwritten to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
