"""The deploy gate. Exits non-zero when quality regressed.

    python scripts/eval_gate.py --suite suites/rag_core.json \
        --baseline .omnex/baseline.json --out .omnex/runs

Designed to be the thing CI actually calls, which means three properties that
sound obvious and are usually missing:

**It exits non-zero.** A quality check that prints a warning and exits 0 is a
quality check that never blocks anything. This one fails the build the same way
a type error does.

**Its output is readable in a CI log.** Not a JSON blob and not a link to a
dashboard behind a login — the regressed case ids, in the terminal, where the
person who broke it is already looking.

**It records the run whether or not it passed.** A failed run is the most useful
one to keep: it is the evidence for what changed, and deleting it because the
build went red is how a team loses the ability to answer "when did this start".

The baseline is only updated on an explicit `--record`, never automatically on
success. Auto-updating means a slow decline is silently ratified one commit at
a time, each one only slightly worse than the last, and after two months the
baseline is the degraded system.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from omnex.core import FakeClock, IdFactory, Money
from omnex.evals import (
    EvalRunner,
    Gate,
    GoldenCase,
    MetricResult,
    Suite,
    Trend,
    answer_relevancy,
    citation_accuracy,
    context_recall,
    faithfulness,
    load_baseline,
    refusal_accuracy,
)
from omnex.rag import REFUSAL, Document, RagConfig, RagPipeline, chunk_document
from omnex.vectors import HashingEmbedder, HybridStore

#: Below this question-term coverage, the best sentence in the corpus is not an
#: answer and the extractive baseline says so. Without a refusal path a baseline
#: scores zero on every refusal case while looking confident, which is the exact
#: behaviour the suite exists to detect.
_ANSWER_FLOOR = 0.34


def extractive_answer(question: str, hits) -> str:
    """Pick the sentence that best answers the question, and cite its page.

    A genuine extractive-QA baseline rather than a stub: it is what a system
    with retrieval and no generator can do, which makes it the right floor to
    measure a generator against. It also exercises the whole grounded path —
    every sentence it returns is verbatim from a retrieved chunk, so anything
    the grounder rejects is a bug in the grounder rather than a bad answer.
    """
    from omnex.rag import split_sentences
    from omnex.vectors.embed import tokenize

    stop = {"what", "which", "who", "how", "many", "the", "is", "are", "for", "does", "and", "in"}
    asked = {t for t in tokenize(question) if t not in stop and len(t) > 2}
    if not asked or not hits:
        return ""

    best_score, best_sentence, best_chunk = 0.0, "", None
    for hit in hits:
        for sentence in split_sentences(hit.chunk.text):
            words = set(tokenize(sentence))
            score = len(asked & words) / len(asked)
            if score > best_score:
                best_score, best_sentence, best_chunk = score, sentence.strip(), hit.chunk

    if best_score < _ANSWER_FLOOR or best_chunk is None:
        return ""
    return f"{best_sentence} {best_chunk.cite}"


def build_answerer(corpus_path: Path):
    """Wire the suite to the real pipeline.

    Uses the local, zero-cost path by default (P7) so the gate runs on every
    pull request without a credential or a bill. A deployment that wants the
    gate to exercise its production model swaps the model here; everything else
    — the metrics, the comparison, the exit code — is unchanged.
    """
    import json

    from omnex.llm import ScriptedModel, Tier, spec_for

    payload = json.loads(corpus_path.read_text())
    document = Document.from_pages(payload["doc_id"], payload["pages"])
    store = HybridStore(embedder=HashingEmbedder(), candidates=20)
    store.upsert(chunk_document(document, target_chars=400, ids=IdFactory(clock=FakeClock())))
    spec = spec_for("local/gate", Tier.SMALL, "0", "0")

    def answerer(case: GoldenCase) -> tuple[str, dict[str, MetricResult], Money]:
        hits = store.search(case.question, limit=4)
        # When nothing in the corpus clears the floor, the baseline says so in
        # the same words the pipeline uses. Substituting a placeholder here
        # would make a correct refusal look like a bad answer.
        reply = extractive_answer(case.question, hits) or REFUSAL
        model = ScriptedModel(model_spec=spec, responses=[reply], output_tokens=40)
        # Regeneration off: the extractive baseline is deterministic, so a
        # second attempt returns the identical answer and only costs a call.
        # A generator-backed run leaves it on.
        answer = RagPipeline(
            store=store, model=model, config=RagConfig(max_regenerations=0), clock=FakeClock()
        ).answer(case.question)

        # A refusal case is scored ONLY on whether it refused. Adding relevancy
        # to it would penalise the correct behaviour: a proper refusal shares no
        # content words with the question and scores zero.
        if case.expect_refusal:
            return (
                answer.text,
                {"refusal_accuracy": refusal_accuracy(answer.text, expect_refusal=True)},
                answer.cost,
            )

        metrics = {
            "context_recall": context_recall(answer.hits, case.relevant_chunks),
            "answer_relevancy": answer_relevancy(case.question, answer.text),
            "faithfulness": faithfulness(answer.text, [h.chunk for h in answer.hits]),
            "refusal_accuracy": refusal_accuracy(answer.text, expect_refusal=False),
        }
        if case.must_cite:
            metrics["citation_accuracy"] = citation_accuracy(answer.text, case.must_cite)
        return answer.text, metrics, answer.cost

    return answerer


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the eval suite and gate a deploy on it.")
    parser.add_argument("--suite", default="suites/rag_core.json")
    parser.add_argument("--corpus", default="suites/rag_core_corpus.json")
    parser.add_argument("--baseline", default=".omnex/baseline.json")
    parser.add_argument("--out", default=".omnex/runs")
    parser.add_argument("--label", default="ci")
    parser.add_argument(
        "--record",
        action="store_true",
        help="overwrite the baseline with this run — deliberate, never automatic",
    )
    parser.add_argument("--max-mean-drop", type=float, default=0.02)
    args = parser.parse_args()

    suite = Suite.load(args.suite)
    suite.validate()
    print(f"suite {suite.name}: {len(suite.cases)} cases, fingerprint {suite.fingerprint}")

    report = EvalRunner(suite).run(build_answerer(Path(args.corpus)), label=args.label)
    print(report.summary())

    # Recorded before the verdict. A failed run is the most useful one to keep.
    Trend().record(report, args.out)

    decision = Gate(max_mean_drop=args.max_mean_drop).decide(report, load_baseline(args.baseline))
    print()
    print(decision.report())

    trend = Trend.load(args.out)
    print()
    print(trend.sparkline())
    chronic = trend.chronically_failing()
    if chronic:
        # Invisible to any aggregate: broken long enough that they contribute
        # the same constant to every mean and never regress again.
        print(f"chronically failing ({len(chronic)}): {', '.join(chronic[:10])}")

    if args.record:
        report.save(args.baseline)
        print(f"\nbaseline recorded at {args.baseline}")

    return 0 if decision.allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
