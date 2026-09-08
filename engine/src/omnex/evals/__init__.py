"""P4 — the eval harness and the gate that blocks a regression.

The design decision that matters: **the gate blocks on newly-failing cases, not
on the mean.** Five cases breaking and five improving leaves an aggregate flat,
and the deploy ships with five things newly broken — which then stay broken,
because the mean recovered and nobody looked again.

Metrics are deterministic and in-process by default. Not because a judge model
is worse — it is more faithful to human judgement — but because a gate whose own
measurement is noisy either blocks good deploys or waves bad ones through, and a
team's response to a flaky gate is to switch it off. Judge-based scoring belongs
in a weekly review over a large sample; the adapters are there for that.

Four RAG metrics, kept separate because they name four different repairs:
context recall (fix retrieval), context precision (fix ranking), faithfulness
(fix generation), answer relevancy (fix the prompt).
"""

from .cases import ContaminationReport, GoldenCase, Suite, contamination_report, require_clean
from .metrics import (
    MetricResult,
    answer_correctness,
    answer_relevancy,
    citation_accuracy,
    context_precision,
    context_recall,
    faithfulness,
    refusal_accuracy,
)
from .runner import CaseResult, EvalRunner, Gate, GateDecision, RunReport, Trend, load_baseline

__all__ = [
    "CaseResult",
    "ContaminationReport",
    "EvalRunner",
    "Gate",
    "GateDecision",
    "GoldenCase",
    "MetricResult",
    "RunReport",
    "Suite",
    "Trend",
    "answer_correctness",
    "answer_relevancy",
    "citation_accuracy",
    "contamination_report",
    "context_precision",
    "context_recall",
    "faithfulness",
    "load_baseline",
    "refusal_accuracy",
    "require_clean",
]
