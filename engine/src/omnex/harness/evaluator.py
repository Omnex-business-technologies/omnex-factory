"""The critic. Its own context, by construction rather than by discipline.

Three independent sources say the same thing, which is why it is enforced in the
type system rather than written on a sign:

    "self-evaluation is a trap"
    "a graph of agents sharing one context is a single loop in a costume —
     it is agreeing with itself in a different font"
    the agent may not touch the file that scores it, "because if it could, it
     would just make the test easier instead of making the model better"

The subtle version is the dangerous one. Splitting the roles is not enough: hand
the critic the maker's transcript and it inherits the maker's reasoning, its
justifications and its blind spots, and the separation becomes cosmetic. It
still says yes, later, more expensively, with more green ticks on the way down.

So `Evaluator.grade()` accepts the contract and the artifact under test and
**nothing else**. There is no parameter through which a transcript, a message
history or a generator handle can be passed. That is the whole mechanism, and it
is why the constructor is deliberately narrow.

## Grading a real signal

A criterion carries a `check` — something that ran and either passed or failed.
`grade()` takes the observed results of those checks; it does not ask an agent
whether it thinks the work is done. "Did the test actually pass" is the
question, and a `CheckResult` with `passed=None` is recorded as UNVERIFIED
rather than being charitably read as success.

## Why harshness is tunable and generosity is not

A standalone critic can be tuned strict — it is far easier to teach something to
criticise than to teach it to doubt itself while it builds. `Rubric.weights` and
`min_score` exist for that. What is not tunable from inside a run is what counts
as passing a frozen criterion.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from ..core.errors import ValidationFailed
from .contract import Contract, Criterion

__all__ = ["CheckResult", "Evaluator", "Grade", "Rubric", "Verdict"]


class Verdict(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    #: The check did not run, or reported nothing. Never read as a pass.
    UNVERIFIED = "unverified"


@dataclass(frozen=True)
class CheckResult:
    """What actually happened when a criterion's check was run."""

    key: str
    #: None means the check did not produce a verdict — not that it passed.
    passed: bool | None
    detail: str = ""

    @property
    def verdict(self) -> Verdict:
        if self.passed is None:
            return Verdict.UNVERIFIED
        return Verdict.PASSED if self.passed else Verdict.FAILED


@dataclass(frozen=True)
class Rubric:
    """Written-down opinion, so subjective quality is still gradable.

    The claim worth taking seriously is that taste is gradable if you hold an
    opinion firmly enough to write it down. Weights make the opinion explicit
    and arguable; leaving them implicit does not make the grading neutral, it
    makes it unexaminable.
    """

    weights: dict[str, float] = field(default_factory=dict)
    #: Fraction of weighted criteria that must pass.
    min_score: float = 1.0

    def weight_of(self, criterion: Criterion) -> float:
        return self.weights.get(criterion.key, 1.0)


@dataclass(frozen=True)
class Grade:
    contract_fingerprint: str
    results: tuple[CheckResult, ...]
    score: float
    accepted: bool
    #: Criteria that failed, worst first — what the generator must fix.
    failures: tuple[str, ...]
    unverified: tuple[str, ...]

    def report(self) -> str:
        lines = [
            f"{'ACCEPTED' if self.accepted else 'REJECTED'} — score {self.score:.0%} "
            f"against contract {self.contract_fingerprint}"
        ]
        for key in self.failures:
            lines.append(f"  FAIL      {key}")
        for key in self.unverified:
            lines.append(f"  UNVERIFIED {key} — the check produced no verdict")
        return "\n".join(lines)


@dataclass(frozen=True)
class Evaluator:
    """Grades work against a contract. Cannot be handed the generator's context.

    Note what this constructor does NOT take: no transcript, no message list, no
    reference to whatever produced the artifact. Adding one would be a one-line
    change and would silently undo the only thing this class is for, so the
    absence is the design and the test suite asserts it.
    """

    rubric: Rubric = field(default_factory=Rubric)

    def grade(
        self,
        contract: Contract,
        agreed_fingerprint: str,
        results: tuple[CheckResult, ...],
    ) -> Grade:
        """Score observed check results against the agreed contract.

        `agreed_fingerprint` is required so work is graded against the contract
        it was approved under, not one renegotiated in the meantime.
        """
        if not contract.agreed:
            raise ValidationFailed(
                "grading against a contract that was never agreed — the negotiation "
                "is what makes the criteria testable"
            )
        contract.assert_unchanged(agreed_fingerprint)

        observed = {r.key: r for r in results}
        unknown = sorted(set(observed) - {c.key for c in contract.criteria})
        if unknown:
            raise ValidationFailed(
                f"results reference criteria not in the contract: {', '.join(unknown)}",
                unknown=unknown,
            )

        total = 0.0
        earned = 0.0
        failures: list[str] = []
        unverified: list[str] = []

        for criterion in contract.criteria:
            weight = self.rubric.weight_of(criterion)
            total += weight
            result = observed.get(criterion.key)
            verdict = result.verdict if result else Verdict.UNVERIFIED

            if verdict is Verdict.PASSED:
                earned += weight
            elif verdict is Verdict.FAILED:
                failures.append(criterion.key)
            else:
                # A criterion nobody checked is not a criterion that passed.
                unverified.append(criterion.key)

        score = earned / total if total else 0.0

        # A frozen criterion that did not demonstrably pass rejects the work
        # outright, whatever the weighted score says. That is what frozen means:
        # a high average cannot buy its way past the anchor.
        frozen_unmet = [
            criterion.key
            for criterion in contract.criteria
            if criterion.frozen
            and (
                criterion.key not in observed
                or observed[criterion.key].verdict is not Verdict.PASSED
            )
        ]
        # Deduplicated: a frozen criterion that failed its check appears in both
        # lists, and reporting it twice makes the critique look longer than it is.
        reported = list(dict.fromkeys([*failures, *frozen_unmet]))

        return Grade(
            contract_fingerprint=contract.fingerprint,
            results=results,
            score=score,
            accepted=not frozen_unmet and not unverified and score >= self.rubric.min_score,
            failures=tuple(reported),
            unverified=tuple(unverified),
        )
