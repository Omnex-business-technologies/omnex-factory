"""Metrics, computed in-process, with adapters for DeepEval and RAGAS.

The metrics here are deliberately the cheap deterministic ones. That is not a
claim that they are better than a judge model — they are not — but a claim about
where each belongs:

A **deterministic** metric runs on every commit, in CI, in under a second, and
gives the same answer twice. That is what a regression gate needs. A gate whose
own measurement is noisy either blocks good deploys or waves bad ones through,
and teams respond to a flaky gate by disabling it.

A **judge** metric is more faithful to human judgement and costs a model call
per case, with variance between runs. That belongs in a weekly quality review
over a large sample, not in the path of every pull request. The adapters exist
for exactly that, and `LlmJudge` takes a `LanguageModel` so its cost lands in
the same ledger as everything else.

The four RAG metrics below are the standard set, and each answers a different
question about a different half of the system:

    context recall     did retrieval FIND the evidence?      → fix retrieval
    context precision   is the retrieved set mostly noise?    → fix ranking
    faithfulness        does the answer follow the evidence?  → fix generation
    answer relevancy    does the answer address the question? → fix the prompt

Reporting one aggregate "quality" number collapses four independent failure
modes into a number that cannot tell you which knob to turn.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..rag.ground import Grounder
from ..vectors.embed import tokenize
from ..vectors.types import Chunk, SearchHit

__all__ = [
    "MetricResult",
    "answer_correctness",
    "answer_relevancy",
    "citation_accuracy",
    "context_precision",
    "context_recall",
    "faithfulness",
]

_STOP = frozenset(
    [
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "of",
        "in",
        "on",
        "at",
        "to",
        "for",
        "from",
        "by",
        "with",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "it",
        "its",
        "this",
        "that",
        "these",
        "those",
        "as",
        "not",
        "no",
        "do",
        "does",
        "did",
        "has",
        "have",
        "had",
        "will",
        "would",
        "can",
        "could",
        "should",
        "may",
        "might",
        "must",
        "what",
        "which",
        "who",
        "when",
        "where",
        "how",
        "why",
    ]
)


@dataclass(frozen=True)
class MetricResult:
    name: str
    score: float
    #: Why the score is what it is. A metric that reports only a number cannot
    #: be acted on — "0.62" says nothing about which case or which half.
    detail: str = ""

    @property
    def passed(self) -> bool:
        return self.score >= 0.5


def _content(text: str) -> set[str]:
    return {w for w in tokenize(text) if w not in _STOP and len(w) > 2}


# ── retrieval ─────────────────────────────────────────────────────────────


def context_recall(hits: Sequence[SearchHit], relevant_ids: Sequence[str]) -> MetricResult:
    """Did retrieval find the evidence at all?

    The FIRST metric to look at when answers are wrong. Nothing downstream can
    fix a missing chunk: no reranker reorders what it never received, and no
    prompt makes a model cite a page it was not shown.
    """
    if not relevant_ids:
        return MetricResult("context_recall", 1.0, "no relevant chunks declared")
    found = {h.chunk.id for h in hits}
    hit_count = sum(1 for i in relevant_ids if i in found)
    missing = [i for i in relevant_ids if i not in found]
    return MetricResult(
        "context_recall",
        hit_count / len(relevant_ids),
        f"{hit_count}/{len(relevant_ids)} found" + (f", missing {missing}" if missing else ""),
    )


def context_precision(hits: Sequence[SearchHit], relevant_ids: Sequence[str]) -> MetricResult:
    """How much of what was retrieved is actually relevant.

    Rank-weighted: a relevant chunk at position 1 counts for more than the same
    chunk at position 10, because the model attends to the top of its context
    and a relevant passage buried under nine irrelevant ones is nearly as bad as
    absent. This is what distinguishes a ranking problem from a recall problem.
    """
    if not hits:
        return MetricResult("context_precision", 0.0, "nothing retrieved")
    if not relevant_ids:
        return MetricResult("context_precision", 1.0, "no relevant chunks declared")

    relevant = set(relevant_ids)
    running = 0
    total = 0.0
    for position, hit in enumerate(hits, start=1):
        if hit.chunk.id in relevant:
            running += 1
            total += running / position
    score = total / min(len(relevant), len(hits))
    return MetricResult("context_precision", min(1.0, score), f"{running} relevant in {len(hits)}")


# ── generation ────────────────────────────────────────────────────────────


def faithfulness(
    answer: str, evidence: Sequence[Chunk], grounder: Grounder | None = None
) -> MetricResult:
    """Fraction of the answer's claims the evidence actually supports.

    Reuses P1's grounder rather than reimplementing it, so the number the eval
    reports and the check that runs in production are the same code. An eval
    that measures something subtly different from what ships is an eval that
    goes green while users see failures.
    """
    grounded = (grounder or Grounder()).check(answer, evidence)
    dropped = len(grounded.dropped)
    return MetricResult(
        "faithfulness",
        grounded.support_rate,
        f"{dropped} unsupported claim(s)" if dropped else "all claims supported",
    )


def answer_relevancy(question: str, answer: str) -> MetricResult:
    """Does the answer engage with what was asked?

    Catches the specific failure of an answer that is perfectly faithful to the
    evidence and about something else — common when retrieval returned a
    plausible neighbouring topic and the model dutifully summarised it.
    """
    asked = _content(question)
    if not asked:
        return MetricResult("answer_relevancy", 1.0, "no content words in question")
    given = _content(answer)
    covered = asked & given
    return MetricResult(
        "answer_relevancy",
        len(covered) / len(asked),
        f"{len(covered)}/{len(asked)} question terms addressed",
    )


def citation_accuracy(answer: str, must_cite: Sequence[int]) -> MetricResult:
    """Are the required pages cited, and no invented ones?

    Scored on both sides. Precision alone rewards citing nothing; recall alone
    rewards citing every page in the document.
    """
    from ..rag.ground import CITATION_PATTERN

    cited: set[int] = set()
    for match in CITATION_PATTERN.finditer(answer):
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        cited.update(range(start, end + 1))

    if not must_cite:
        return MetricResult("citation_accuracy", 1.0, "no citations required")
    required = set(must_cite)
    correct = cited & required
    spurious = cited - required
    recall = len(correct) / len(required)
    precision = len(correct) / len(cited) if cited else 0.0
    f1 = 0.0 if not (precision + recall) else 2 * precision * recall / (precision + recall)
    return MetricResult(
        "citation_accuracy",
        f1,
        f"cited {sorted(cited)}, required {sorted(required)}"
        + (f", spurious {sorted(spurious)}" if spurious else ""),
    )


def refusal_accuracy(
    answer: str, expect_refusal: bool, refusal_marker: str = "do not contain"
) -> MetricResult:
    """Did the system refuse exactly when it should have?

    Its own metric because scoring a refusal with a relevancy or correctness
    measure is nonsense in both directions: a correct refusal shares no content
    words with the question and scores zero, while a confidently wrong answer to
    an unanswerable question scores well. Both push a system toward answering
    everything, which is the failure the refusal cases exist to catch.
    """
    refused = refusal_marker.lower() in answer.lower() or not answer.strip()
    if expect_refusal:
        return MetricResult(
            "refusal_accuracy",
            1.0 if refused else 0.0,
            "correctly refused" if refused else "answered a question the corpus cannot answer",
        )
    return MetricResult(
        "refusal_accuracy",
        0.0 if refused else 1.0,
        "refused an answerable question" if refused else "answered as expected",
    )


def answer_correctness(answer: str, expected: str) -> MetricResult:
    """Overlap with the expected answer.

    Deliberately NOT exact match. Free-text exact match measures phrasing, so a
    correct answer worded differently scores zero and a suite built on it
    rewards a model for memorising the reference wording rather than being
    right. F1 over content words is crude and at least measures content.
    """
    expected_words = _content(expected)
    if not expected_words:
        return MetricResult("answer_correctness", 1.0, "no expected answer")
    given = _content(answer)
    if not given:
        return MetricResult("answer_correctness", 0.0, "empty answer")
    shared = expected_words & given
    precision = len(shared) / len(given)
    recall = len(shared) / len(expected_words)
    f1 = 0.0 if not (precision + recall) else 2 * precision * recall / (precision + recall)
    return MetricResult("answer_correctness", f1, f"{len(shared)}/{len(expected_words)} key terms")
