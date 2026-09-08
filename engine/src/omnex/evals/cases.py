"""Golden cases: what "correct" means, written down and versioned.

A suite is data on disk, not code, so it can be reviewed in a pull request by
someone who does not read Python — which is usually the person who knows whether
the expected answer is right.

Two fields do more work than they look like they should.

`must_cite` turns a citation into part of the expected answer rather than
decoration. A RAG system that produces the right sentence with the wrong page
has failed, and a metric that only compares answer text scores it perfect.

`tags` are how a regression gets attributed. An aggregate score that drops two
points tells you nothing actionable; the same drop broken down by tag — "every
multi-hop case regressed, single-hop is unchanged" — names the cause. Tags are
therefore required to be non-empty.

**Contamination is checked, not assumed.** `contamination_report` compares the
suite against a training corpus, because a fine-tuned model (P9) evaluated on
cases it was trained on produces a number that means nothing and looks excellent.
That check has to exist before it is needed, not after a leaderboard is published.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..core.errors import ValidationFailed
from ..vectors.embed import tokenize

__all__ = ["ContaminationReport", "GoldenCase", "Suite", "contamination_report"]


@dataclass(frozen=True)
class GoldenCase:
    """One question with a known-correct answer and the evidence behind it."""

    id: str
    question: str
    #: The expected answer. Compared semantically, not by string equality —
    #: exact-match scoring on free text measures phrasing, not correctness.
    expected: str
    #: Pages the answer must cite. Empty means citations are not being tested.
    must_cite: tuple[int, ...] = ()
    #: Chunk ids that should be retrieved. Lets retrieval be scored separately
    #: from generation, which is the only way to know which half regressed.
    relevant_chunks: tuple[str, ...] = ()
    #: Required for attribution. An unlabelled case is one whose regression
    #: cannot be explained.
    tags: tuple[str, ...] = ()
    #: Set when the correct behaviour is to refuse. A suite without these
    #: rewards a model that answers everything confidently.
    expect_refusal: bool = False
    context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.tags:
            raise ValidationFailed("every case needs at least one tag", case=self.id)
        if not self.expect_refusal and not self.expected.strip():
            raise ValidationFailed("a non-refusal case needs an expected answer", case=self.id)

    @property
    def fingerprint(self) -> str:
        """Stable hash of the case content. Changes when the case changes.

        A baseline is only comparable to a run of the SAME cases. Without a
        fingerprint, editing an expected answer silently makes the new run look
        like an improvement against a baseline that no longer applies.
        """
        payload = f"{self.question}|{self.expected}|{sorted(self.must_cite)}|{self.expect_refusal}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


@dataclass
class Suite:
    name: str
    cases: list[GoldenCase] = field(default_factory=list)
    version: str = "1"

    @classmethod
    def load(cls, path: str | Path) -> Suite:
        payload = json.loads(Path(path).read_text())
        return cls(
            name=payload["name"],
            version=str(payload.get("version", "1")),
            cases=[
                GoldenCase(
                    id=c["id"],
                    question=c["question"],
                    expected=c.get("expected", ""),
                    must_cite=tuple(c.get("must_cite", [])),
                    relevant_chunks=tuple(c.get("relevant_chunks", [])),
                    tags=tuple(c.get("tags", [])),
                    expect_refusal=bool(c.get("expect_refusal", False)),
                    context=c.get("context", {}),
                )
                for c in payload["cases"]
            ],
        )

    def save(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps(
                {
                    "name": self.name,
                    "version": self.version,
                    "cases": [
                        {
                            "id": c.id,
                            "question": c.question,
                            "expected": c.expected,
                            "must_cite": list(c.must_cite),
                            "relevant_chunks": list(c.relevant_chunks),
                            "tags": list(c.tags),
                            "expect_refusal": c.expect_refusal,
                            "context": c.context,
                        }
                        for c in self.cases
                    ],
                },
                indent=2,
            )
        )

    def validate(self) -> None:
        """Catch suite problems before a run, not in the middle of one."""
        seen: set[str] = set()
        for case in self.cases:
            if case.id in seen:
                raise ValidationFailed("duplicate case id", case=case.id)
            seen.add(case.id)
        if not self.cases:
            raise ValidationFailed("empty suite", suite=self.name)
        refusals = sum(1 for c in self.cases if c.expect_refusal)
        if refusals == 0:
            # Not fatal, but worth knowing: a suite where every question has an
            # answer cannot distinguish a careful system from a confident one.
            raise ValidationFailed(
                "suite has no refusal cases — it cannot detect a system that answers "
                "everything confidently, which is the failure mode RAG has",
                suite=self.name,
            )

    @property
    def fingerprint(self) -> str:
        joined = "|".join(sorted(c.fingerprint for c in self.cases))
        return hashlib.sha256(joined.encode()).hexdigest()[:16]

    def by_tag(self, tag: str) -> list[GoldenCase]:
        return [c for c in self.cases if tag in c.tags]

    @property
    def tags(self) -> tuple[str, ...]:
        return tuple(sorted({t for c in self.cases for t in c.tags}))


@dataclass(frozen=True)
class ContaminationReport:
    checked: int
    contaminated: list[tuple[str, float]]

    @property
    def clean(self) -> bool:
        return not self.contaminated

    @property
    def rate(self) -> float:
        return 0.0 if not self.checked else len(self.contaminated) / self.checked


def contamination_report(
    suite: Suite, training_texts: Iterable[str], threshold: float = 0.8
) -> ContaminationReport:
    """Find cases whose question appears in the training data.

    Shingled overlap rather than exact match: training data is rarely a verbatim
    copy, and a paraphrase leaks the answer just as effectively. The check is
    deliberately conservative — a flagged case is one to look at, not
    automatically one to delete.

    Run this BEFORE publishing any number from a fine-tuned model. A model
    evaluated on cases it was trained on scores excellently and means nothing,
    and the failure is invisible in every metric you would otherwise look at.
    """
    corpus = [_shingles(t) for t in training_texts]
    flagged: list[tuple[str, float]] = []

    for case in suite.cases:
        question = _shingles(case.question)
        if not question:
            continue
        best = max((len(question & doc) / len(question) for doc in corpus), default=0.0)
        if best >= threshold:
            flagged.append((case.id, best))

    return ContaminationReport(checked=len(suite.cases), contaminated=flagged)


def _shingles(text: str, size: int = 4) -> set[str]:
    words = tokenize(text)
    if len(words) < size:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i : i + size]) for i in range(len(words) - size + 1)}


def require_clean(suite: Suite, training_texts: Sequence[str], threshold: float = 0.8) -> None:
    report = contamination_report(suite, training_texts, threshold)
    if not report.clean:
        raise ValidationFailed(
            "evaluation suite is contaminated by the training data",
            cases=", ".join(case for case, _ in report.contaminated[:10]),
            rate=round(report.rate, 3),
        )
