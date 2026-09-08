"""The contract: what "done" means, agreed before a line is written.

A planner that specifies granular technical detail up front is specifying it
before anyone has looked at the problem, and an error there does not stay
local — it cascades through every later step and magnifies over a long horizon.
So the planner emits intent, and the generator and the evaluator negotiate the
*testable* form of it between themselves.

The generator proposes "I will build X, and you can verify it by testing Y".
The evaluator pushes back: the scope is too wide, that test is too weak, this
edge case is missing. They iterate until both agree. Only then does building
start, and the evaluator grades against the **contract** rather than against the
planner's original sentence.

Granularity is the whole game. Vague criteria produce vague critiques and the
generator shrugs; the run that motivated this pattern settled at 27 criteria for
one application, which is roughly the level at which a finding becomes something
you can act on rather than something you can nod at.

## Frozen criteria — the part that resists Goodhart

A loop can only see its own metric, so given the chance it optimises the metric
rather than the thing. The support bot tied to ticket-resolution rate learns to
*close* tickets; the agent given write access to its own evaluator makes the test
easier instead of making the work better.

The defence is that some criteria are **frozen**: they may be added to, never
weakened, never dropped, and no negotiation and no outer loop may touch them.
`Contract.negotiate()` raises when a proposal would relax one. That is the
mechanism, and it is enforced here rather than described in a prompt, because a
prompt is exactly the surface an optimiser learns to talk its way around.

## Fingerprints

The agreed contract is fingerprinted, and the fingerprint covers the criteria
themselves. A generator that alters the contract after agreement and proceeds
under the old approval is the same failure P15 prevents for human approvals: the
approval must bind to what was actually approved.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace

from ..core.errors import ValidationFailed

__all__ = ["Contract", "Criterion", "Proposal"]


@dataclass(frozen=True)
class Criterion:
    """One individually-checkable statement about what done means.

    `check` is the real signal — the command, assertion or measurement that can
    fail. A criterion whose check is "the agent says it is done" is not a
    criterion, it is a hope, so `check` is required.
    """

    key: str
    statement: str
    #: What actually decides it: a command to run, an assertion, a metric bound.
    check: str
    #: Frozen criteria may never be weakened or dropped, by anyone.
    frozen: bool = False

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValidationFailed("a criterion needs a key")
        if not self.check.strip():
            raise ValidationFailed(
                f"criterion {self.key!r} has no check — "
                "'the agent reports success' is not a verification"
            )

    def digest(self) -> str:
        return f"{self.key}|{self.statement}|{self.check}|{int(self.frozen)}"


@dataclass(frozen=True)
class Proposal:
    """A revision offered during negotiation, by either side."""

    criteria: tuple[Criterion, ...]
    note: str = ""


@dataclass(frozen=True)
class Contract:
    """The agreed definition of done, fingerprinted."""

    criteria: tuple[Criterion, ...] = ()
    agreed: bool = False
    history: tuple[str, ...] = field(default_factory=tuple)

    @property
    def fingerprint(self) -> str:
        """Covers every criterion. Changing one invalidates the agreement."""
        body = "\n".join(sorted(c.digest() for c in self.criteria))
        return hashlib.sha256(body.encode()).hexdigest()[:16]

    @property
    def frozen_keys(self) -> frozenset[str]:
        return frozenset(c.key for c in self.criteria if c.frozen)

    def by_key(self, key: str) -> Criterion | None:
        return next((c for c in self.criteria if c.key == key), None)

    def negotiate(self, proposal: Proposal) -> Contract:
        """Apply a revision, refusing anything that weakens a frozen criterion.

        Refusal is deliberate rather than a silent restore: an optimiser that
        keeps proposing weaker tests and keeps being quietly corrected learns
        nothing, while one that is refused with a reason has been told.
        """
        offered = {c.key: c for c in proposal.criteria}

        for key in self.frozen_keys:
            replacement = offered.get(key)
            existing = self.by_key(key)
            assert existing is not None
            if replacement is None:
                raise ValidationFailed(
                    f"proposal drops frozen criterion {key!r} — frozen criteria may be "
                    "added to, never removed",
                    dropped=key,
                )
            if not replacement.frozen:
                raise ValidationFailed(
                    f"proposal unfreezes {key!r}; a criterion an optimiser can thaw is "
                    "not an anchor",
                    unfrozen=key,
                )
            if replacement.check != existing.check:
                raise ValidationFailed(
                    f"proposal changes the check on frozen criterion {key!r} — this is "
                    "how a loop makes the test easier instead of making the work better",
                    criterion=key,
                )

        return replace(
            self,
            criteria=proposal.criteria,
            agreed=False,
            history=(*self.history, proposal.note or "revision"),
        )

    def agree(self, minimum_criteria: int = 1) -> Contract:
        """Close the negotiation.

        `minimum_criteria` exists because a contract of two vague items produces
        two vague critiques. It is a floor on granularity, not a target.
        """
        if len(self.criteria) < minimum_criteria:
            raise ValidationFailed(
                f"{len(self.criteria)} criteria is below the agreed floor of "
                f"{minimum_criteria}; vague criteria produce critiques a generator "
                "can shrug at",
                criteria=len(self.criteria),
            )
        return replace(self, agreed=True)

    def assert_unchanged(self, fingerprint: str) -> None:
        """Bind work to the contract that was actually agreed.

        Called by the evaluator before grading. A generator that renegotiated
        mid-flight and carried on under the old agreement fails here rather than
        being graded against a contract nobody accepted.
        """
        if self.fingerprint != fingerprint:
            raise ValidationFailed(
                "the contract changed after it was agreed; work must be graded against "
                "the contract it was approved under",
                expected=fingerprint,
                actual=self.fingerprint,
            )

    def report(self) -> str:
        lines = [
            f"contract {self.fingerprint} — {len(self.criteria)} criteria "
            f"({len(self.frozen_keys)} frozen), "
            f"{'agreed' if self.agreed else 'still negotiating'}"
        ]
        for criterion in self.criteria:
            mark = "*" if criterion.frozen else " "
            lines.append(f" {mark} {criterion.key}: {criterion.statement}  [{criterion.check}]")
        return "\n".join(lines)
