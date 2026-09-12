"""An LLM-as-judge quality metric — costed, and never gating by default.

`metrics.py`'s own module docstring already names the reason this file did not
exist: a judge call is more faithful to human judgement than a string-overlap
metric, but it costs a model call and carries variance between runs, so it
cannot sit in the deterministic regression gate that runs on every commit.
That was never an argument that it should not exist — only that it belongs
somewhere else: a periodic quality review over a sample, not the path of every
pull request.

The four RAG metrics in `metrics.py` all need something to compare against — a
set of relevant chunk ids, an expected answer, a set of required citations.
OMNEX's actual product surface (ad copy, email subject lines, landing-page
headlines — see `lib/modules/registry.ts`) has none of that: there is no
"reference ad" a new one can be F1-scored against, and "is this on-brand and
compelling" is not a word-overlap question. A judge model is the only metric
shape that can answer it at all.

So: a fifth metric, not a replacement, priced through the same
`omnex.llm.LanguageModel` every other call in this engine goes through — its
cost is returned alongside the score so it lands in the same ledger as
everything else, exactly the shape `metrics.py` said this would take. Nothing
here makes it gate a run: `runner.EvalRunner`/`Gate` already read a per-metric
threshold override (`thresholds={"llm_judge": 0.0}`), and that existing
mechanism is how a caller keeps this metric recorded without ever blocking on
it — no change to `runner.py` was needed or made.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from ..core.money import Money
from ..llm.base import CallOptions, LanguageModel
from ..llm.types import Message
from .metrics import MetricResult

__all__ = ["JudgeResult", "judge_quality"]

_RUBRIC = """You are grading one response for quality. Score it from 0 to 10 on \
how well it answers the question, based only on: relevance, correctness (if \
evidence is given), clarity, and — if a brand voice is implied by the \
question — fit with that voice.

Question: {question}
{evidence_block}Answer: {answer}

Respond with exactly one line, no other text:
SCORE: <integer 0-10> REASON: <one sentence>"""

#: DOTALL so a reason spanning a model's stray newline still parses; a judge
#: model is not this engine's code and does not owe it a single physical line.
_SCORE_PATTERN = re.compile(r"SCORE:\s*(\d+)\s*REASON:\s*(.+)", re.IGNORECASE | re.DOTALL)


@dataclass(frozen=True)
class JudgeResult:
    """A judge score and what it cost. Both, never one without the other.

    Handing back only the `MetricResult` would let a caller record the score
    and forget the spend — the exact shape of the keystone bug this repo
    already paid for once (`lib/core/llm/provider.ts`'s missing `usage`
    block, cost panels reading €0.00 on real runs).
    """

    metric: MetricResult
    cost: Money


def judge_quality(
    question: str,
    answer: str,
    model: LanguageModel,
    evidence: Sequence[str] = (),
    options: CallOptions | None = None,
) -> JudgeResult:
    """Score one answer with one model call. Costs money — never call this per-commit.

    Parsing is strict on purpose. A judge reply that does not match the one
    required line scores 0.0 with the raw reply in `detail`, rather than a
    best-effort guess at what the model meant: a metric that silently defaults
    on a malformed reply reports a number nobody can trust exactly when the
    judge itself is the thing misbehaving, which is the one time the score
    most needs to be visibly wrong rather than plausibly wrong.
    """
    evidence_block = f"Evidence:\n{chr(10).join(evidence)}\n" if evidence else ""
    prompt = _RUBRIC.format(question=question, evidence_block=evidence_block, answer=answer)
    completion = model.complete([Message(role="user", content=prompt)], options or CallOptions())

    match = _SCORE_PATTERN.search(completion.text)
    if not match:
        return JudgeResult(
            MetricResult("llm_judge", 0.0, f"judge reply did not parse: {completion.text[:200]!r}"),
            completion.cost,
        )
    raw_score = int(match.group(1))
    if not 0 <= raw_score <= 10:
        return JudgeResult(
            MetricResult("llm_judge", 0.0, f"judge returned an out-of-range score {raw_score}"),
            completion.cost,
        )
    return JudgeResult(
        MetricResult("llm_judge", raw_score / 10.0, match.group(2).strip()),
        completion.cost,
    )
