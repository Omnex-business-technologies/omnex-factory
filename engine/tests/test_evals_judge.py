"""Tests for the LLM-as-judge metric: costed, strictly parsed, never silent."""

from __future__ import annotations

from omnex.core import Money
from omnex.evals import JudgeResult, judge_quality
from omnex.llm import ScriptedModel, Tier, spec_for


def _judge(*responses: str) -> ScriptedModel:
    spec = spec_for("judge-model", Tier.LARGE, "3.00", "15.00")
    return ScriptedModel(model_spec=spec, responses=list(responses))


def test_a_well_formed_reply_scores_and_costs() -> None:
    model = _judge("SCORE: 8 REASON: on-brand, answers the question directly")
    result = judge_quality(
        "Write a headline for a coffee shop", "Wake up to better mornings.", model
    )

    assert isinstance(result, JudgeResult)
    assert result.metric.name == "llm_judge"
    assert result.metric.score == 0.8
    assert "on-brand" in result.metric.detail
    assert result.cost > Money.zero()


def test_a_malformed_reply_scores_zero_and_names_itself_unparsed() -> None:
    model = _judge("Sure! I would rate this a solid effort.")
    result = judge_quality("q?", "a.", model)

    assert result.metric.score == 0.0
    assert "did not parse" in result.metric.detail
    # The cost is still real -- the call happened and must still be billed.
    assert result.cost > Money.zero()


def test_an_out_of_range_score_is_refused_not_clamped() -> None:
    """Clamping a 15 to 10 would hide a judge model that cannot follow the rubric."""
    model = _judge("SCORE: 15 REASON: extremely good")
    result = judge_quality("q?", "a.", model)

    assert result.metric.score == 0.0
    assert "out-of-range" in result.metric.detail


def test_evidence_is_included_in_the_prompt_when_given() -> None:
    model = _judge("SCORE: 5 REASON: adequate")
    judge_quality("q?", "a.", model, evidence=["Fact one.", "Fact two."])

    sent = model.calls[0][0].content
    assert "Fact one." in sent
    assert "Fact two." in sent


def test_no_evidence_omits_the_evidence_block() -> None:
    model = _judge("SCORE: 5 REASON: adequate")
    judge_quality("q?", "a.", model)

    sent = model.calls[0][0].content
    assert "Evidence:" not in sent
