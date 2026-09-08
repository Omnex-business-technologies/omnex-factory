"""Tests for P4. The gate-vs-mean test is the one that justifies the design."""

from __future__ import annotations

import json
from pathlib import Path
from random import Random

import pytest

from omnex.core import FakeClock, IdFactory, Money, ValidationFailed
from omnex.evals import (
    EvalRunner,
    Gate,
    GoldenCase,
    MetricResult,
    RunReport,
    Suite,
    Trend,
    answer_correctness,
    answer_relevancy,
    citation_accuracy,
    contamination_report,
    context_precision,
    context_recall,
    faithfulness,
    require_clean,
)
from omnex.evals.runner import CaseResult
from omnex.llm import ScriptedModel, Tier, spec_for
from omnex.rag import Document, RagPipeline, chunk_document
from omnex.vectors import Chunk, HashingEmbedder, HybridStore, SearchHit

SUITES = Path(__file__).resolve().parents[1] / "suites"


def _case(case_id: str, **kw) -> GoldenCase:
    return GoldenCase(
        id=case_id,
        question=kw.pop("question", "q?"),
        expected=kw.pop("expected", "a"),
        tags=kw.pop("tags", ("t",)),
        **kw,
    )


def _report(scores: dict[str, float], fingerprint: str = "fp") -> RunReport:
    report = RunReport(suite="s", suite_fingerprint=fingerprint)
    for case_id, score in scores.items():
        report.results.append(
            CaseResult(case_id, ("t",), {"correctness": MetricResult("correctness", score)})
        )
    return report


# ── The gate ──────────────────────────────────────────────────────────────


def test_the_gate_blocks_a_regression_the_mean_completely_hides():
    """Five break, five improve, the average does not move, five things ship broken."""
    baseline = _report({f"c{i}": 0.9 for i in range(5)} | {f"d{i}": 0.1 for i in range(5)})
    current = _report({f"c{i}": 0.1 for i in range(5)} | {f"d{i}": 0.9 for i in range(5)})

    means_are_identical = abs(
        sum(r.score for r in current.results) - sum(r.score for r in baseline.results)
    )
    assert means_are_identical < 1e-9, "the mean is unchanged — that is the point"

    decision = Gate().decide(current, baseline)
    assert not decision.allowed
    assert len(decision.newly_failing) == 5
    assert len(decision.newly_passing) == 5
    assert "now fail" in decision.reason
    assert "regressed" in decision.report()


def test_a_broad_shallow_decline_no_single_case_catches_still_blocks():
    """The failure the per-case rule alone would miss."""
    baseline = _report({f"c{i}": 0.90 for i in range(20)})
    current = _report({f"c{i}": 0.60 for i in range(20)})  # every case still passes
    decision = Gate(max_mean_drop=0.02).decide(current, baseline)
    assert not decision.allowed
    assert "mean quality fell" in decision.reason


def test_an_improvement_is_allowed_and_named():
    baseline = _report({"a": 0.4, "b": 0.9})
    current = _report({"a": 0.95, "b": 0.9})
    decision = Gate().decide(current, baseline)
    assert decision.allowed
    assert decision.newly_passing == ("a",)
    assert decision.mean_delta > 0


def test_a_first_run_with_no_baseline_is_allowed_and_says_so():
    decision = Gate().decide(_report({"a": 0.9}), None)
    assert decision.allowed and "no baseline" in decision.reason


def test_comparing_against_a_baseline_from_a_different_suite_is_refused():
    """How an edited expected answer becomes an apparent improvement."""
    baseline = _report({"a": 0.9}, fingerprint="old")
    current = _report({"a": 0.95}, fingerprint="new")
    with pytest.raises(ValidationFailed, match="not comparable"):
        Gate().decide(current, baseline)


def test_the_regression_allowance_exists_but_defaults_to_zero():
    """Enough cases that one regression does not also trip the mean guard.

    With a small suite the two rules overlap and this would be testing the
    wrong one — which is itself worth knowing: on a 20-case suite a single
    hard failure moves the mean by more than the default tolerance, so the
    allowance cannot be used to wave one through anyway.
    """
    baseline = _report({f"c{i}": 0.9 for i in range(40)})
    current = _report({"c0": 0.1} | {f"c{i}": 0.9 for i in range(1, 40)})

    assert not Gate().decide(current, baseline).allowed
    assert Gate(allowed_regressions=1).decide(current, baseline).allowed


# ── Running ───────────────────────────────────────────────────────────────


def test_a_crashing_case_counts_as_failing_not_missing():
    """Skipping it raises the pass rate by shrinking the denominator."""
    suite = Suite(
        "s", [_case("ok"), _case("boom"), _case("refuse", expected="", expect_refusal=True)]
    )

    def answerer(case: GoldenCase):
        if case.id == "boom":
            raise RuntimeError("provider exploded")
        return "a", {"correctness": MetricResult("correctness", 1.0)}, Money.zero()

    report = EvalRunner(suite).run(answerer, now="2026-01-01T00:00:00Z")
    assert len(report.results) == 3
    assert len(report.failed) == 1
    assert "provider exploded" in report.failed[0].error
    assert report.pass_rate == pytest.approx(2 / 3)


def test_a_case_passes_only_if_every_metric_clears_its_bar():
    """An unfaithful but relevant answer must not average its way to a pass."""
    result = CaseResult(
        "c",
        ("t",),
        {
            "faithfulness": MetricResult("faithfulness", 0.1),
            "answer_relevancy": MetricResult("answer_relevancy", 1.0),
        },
    )
    assert not result.passed()
    assert result.score > 0.5  # the average would have passed it


def test_results_break_down_by_tag_so_a_regression_can_be_attributed():
    report = RunReport(suite="s", suite_fingerprint="fp")
    report.results = [
        CaseResult("a", ("multi_hop",), {"m": MetricResult("m", 0.1)}),
        CaseResult("b", ("multi_hop",), {"m": MetricResult("m", 0.2)}),
        CaseResult("c", ("lookup",), {"m": MetricResult("m", 0.9)}),
    ]
    assert report.by_tag() == {"lookup": 1.0, "multi_hop": 0.0}
    assert "multi_hop" in report.summary()


def test_a_report_round_trips_through_json(tmp_path):
    report = _report({"a": 0.9, "b": 0.2})
    report.save(tmp_path / "r.json")
    restored = RunReport.load(tmp_path / "r.json")
    assert restored.pass_rate == report.pass_rate
    assert restored.suite_fingerprint == report.suite_fingerprint


# ── Suite hygiene ─────────────────────────────────────────────────────────


def test_a_suite_with_no_refusal_cases_is_rejected():
    """It scores a system that always answers exactly like one that knows when to stop."""
    suite = Suite("s", [_case("a"), _case("b")])
    with pytest.raises(ValidationFailed, match="refusal"):
        suite.validate()


def test_an_untagged_case_is_rejected_because_its_regression_cannot_be_explained():
    with pytest.raises(ValidationFailed, match="tag"):
        GoldenCase(id="a", question="q", expected="a", tags=())


def test_duplicate_case_ids_are_caught_before_a_run():
    suite = Suite("s", [_case("dup"), _case("dup"), _case("r", expected="", expect_refusal=True)])
    with pytest.raises(ValidationFailed, match="duplicate"):
        suite.validate()


def test_editing_a_case_changes_the_suite_fingerprint():
    before = Suite("s", [_case("a", expected="twenty")]).fingerprint
    after = Suite("s", [_case("a", expected="fifty")]).fingerprint
    assert before != after


def test_contamination_is_detected_before_a_number_gets_published():
    """A model evaluated on cases it trained on scores excellently and means nothing."""
    suite = Suite(
        "s",
        [
            _case("leaked", question="What is the request timeout for the billing service?"),
            _case("clean", question="Which region hosts the archive service?"),
            _case("r", expected="", expect_refusal=True),
        ],
    )
    training = [
        "Documentation says: what is the request timeout for the billing service? It is 5 seconds.",
        "Unrelated notes about deployment schedules and rotation.",
    ]
    report = contamination_report(suite, training, threshold=0.6)
    assert not report.clean
    assert [case for case, _ in report.contaminated] == ["leaked"]

    with pytest.raises(ValidationFailed, match="contaminated"):
        require_clean(suite, training, threshold=0.6)


# ── Metrics ───────────────────────────────────────────────────────────────


def _hit(chunk_id: str, text: str = "text") -> SearchHit:
    return SearchHit(chunk=Chunk(id=chunk_id, text=text, page=1, page_end=1), score=1.0)


def test_context_recall_names_what_retrieval_missed():
    result = context_recall([_hit("a"), _hit("b")], ["a", "z"])
    assert result.score == 0.5
    assert "z" in result.detail


def test_context_precision_is_rank_weighted():
    """A relevant chunk buried under nine irrelevant ones is nearly as bad as absent."""
    top = context_precision([_hit("a"), _hit("x"), _hit("y")], ["a"])
    buried = context_precision([_hit("x"), _hit("y"), _hit("a")], ["a"])
    assert top.score > buried.score


def test_faithfulness_reuses_the_same_grounder_that_runs_in_production():
    evidence = [Chunk(id="e", text="The pool holds twenty connections.", page=3, page_end=3)]
    good = faithfulness("The pool holds twenty connections. [p. 3]", evidence)
    bad = faithfulness("The pool holds four hundred connections. [p. 3]", evidence)
    assert good.score == 1.0
    assert bad.score == 0.0
    assert "unsupported" in bad.detail


def test_answer_relevancy_catches_a_faithful_answer_about_something_else():
    off_topic = answer_relevancy(
        "What is the billing timeout?", "The archive service is owned by team-c."
    )
    on_topic = answer_relevancy(
        "What is the billing timeout?", "The billing timeout is five seconds."
    )
    assert on_topic.score > off_topic.score


def test_citation_accuracy_penalises_both_missing_and_invented_pages():
    perfect = citation_accuracy("Fact. [p. 3]", [3])
    missing = citation_accuracy("Fact.", [3])
    spurious = citation_accuracy("Fact. [p. 3] More. [p. 9]", [3])
    assert perfect.score == 1.0
    assert missing.score == 0.0
    assert 0.0 < spurious.score < 1.0
    assert "spurious" in spurious.detail


def test_correctness_is_not_exact_match_so_rewording_is_not_punished():
    reworded = answer_correctness(
        "The connection pool holds twenty connections.",
        "Twenty connections are held in the connection pool.",
    )
    wrong = answer_correctness(
        "The archive runs in Frankfurt.", "Twenty connections are held in the connection pool."
    )
    # 0.8, not 1.0: "holds" and "held" are different tokens without a stemmer.
    # Stated rather than tuned away — the metric is crude on purpose, and the
    # gate compares a run to a baseline scored the same crude way, so a constant
    # bias cancels while a real change still shows.
    assert reworded.score > 0.75
    assert wrong.score < 0.2


# ── Trend ─────────────────────────────────────────────────────────────────


def test_a_chronically_failing_case_is_visible_even_though_the_mean_forgot_it():
    """Broken for a month, contributing the same constant to every mean."""
    trend = Trend(
        [
            _report({"broken": 0.1, "fine": 0.9}),
            _report({"broken": 0.1, "fine": 0.9}),
            _report({"broken": 0.1, "fine": 0.95}),
        ]
    )
    assert trend.chronically_failing(window=3) == ["broken"]


def test_the_trend_can_be_stored_and_reloaded(tmp_path):
    trend = Trend()
    for index in range(3):
        report = _report({"a": 0.9})
        report.at = f"2026-01-0{index + 1}T00:00:00Z"
        trend.record(report, tmp_path)
    reloaded = Trend.load(tmp_path)
    assert len(reloaded.history) == 3
    assert "→" in reloaded.sparkline()


# ── The shipped suite, end to end ─────────────────────────────────────────


def test_the_shipped_suite_is_large_valid_and_balanced():
    """The '100+ golden cases' claim, checked rather than asserted."""
    suite = Suite.load(SUITES / "rag_core.json")
    suite.validate()

    assert len(suite.cases) >= 100
    refusals = [c for c in suite.cases if c.expect_refusal]
    assert len(refusals) >= 20, "too few refusal cases to detect a confidently-wrong system"
    assert {"lookup", "numeric", "multi_page", "refusal"} <= set(suite.tags)
    # Every non-refusal case names the page its answer lives on.
    assert all(c.must_cite for c in suite.cases if not c.expect_refusal)


def test_the_suite_runs_against_the_real_pipeline_and_scores_it():
    """An integration check: the harness, the pipeline and the metrics together."""
    corpus = json.loads((SUITES / "rag_core_corpus.json").read_text())
    document = Document.from_pages(corpus["doc_id"], corpus["pages"])
    store = HybridStore(embedder=HashingEmbedder(), candidates=20)
    store.upsert(
        chunk_document(document, target_chars=400, ids=IdFactory(clock=FakeClock(), rng=Random(7)))
    )

    suite = Suite.load(SUITES / "rag_core.json")
    sample = Suite("sample", suite.cases[:3] + [c for c in suite.cases if c.expect_refusal][:2])
    spec = spec_for("test/answerer", Tier.SMALL, "0.05", "0.10")

    def answerer(case: GoldenCase):
        # A model that answers by echoing the retrieved excerpt. Grounded by
        # construction, so what is being tested is the harness wiring, not a
        # model's ability — that is what P17's benchmark is for.
        hits = store.search(case.question, limit=3)
        reply = f"{hits[0].chunk.text.split('.')[0]}. {hits[0].chunk.cite}" if hits else ""
        model = ScriptedModel(model_spec=spec, responses=[reply or "nothing"], output_tokens=40)
        pipeline = RagPipeline(store=store, model=model, clock=FakeClock())
        answer = pipeline.answer(case.question)
        metrics = {
            "context_recall": context_recall(answer.hits, case.relevant_chunks),
            "answer_relevancy": answer_relevancy(case.question, answer.text),
        }
        return answer.text, metrics, answer.cost

    report = EvalRunner(sample).run(answerer, label="integration", now="2026-01-01T00:00:00Z")
    assert len(report.results) == 5
    assert all(not r.error for r in report.results), [r.error for r in report.results if r.error]
    assert "passed" in report.summary()
