"""Human-in-the-loop: when to ask, and making the answer mean something.

Two halves, and the second is the one that is usually missing.

## When to ask

Asking about everything is the same as asking about nothing — an approver who
sees forty requests an hour approves the forty-first without reading it. So
`UncertaintyDetector` scores a proposed action on signals that are actually
available, and only crosses the threshold when something is genuinely off:
weak grounding, a router that exhausted its escalations, a guardrail warning, an
unusually expensive action, or — regardless of any of those — an action that
cannot be undone.

Irreversibility is a separate, overriding rule rather than another weighted
signal. Deleting a customer's data with high confidence is still deleting a
customer's data, and no amount of confidence in the other signals should be able
to outvote that.

## Making the answer mean something

**An approval is bound to the exact thing that was approved.** This is the part
that turns HITL from theatre into a control. The naive implementation stores
`approved: true` against a request id and then executes whatever the agent has
in hand when the reply arrives. Between the two, the agent may have re-planned,
retried, or had its state mutated by another branch — and the human's "yes" now
authorises something they never saw.

So an `ApprovalRequest` carries the SHA-256 of the exact proposal, the decision
records that same hash, and `authorises()` compares them. A changed proposal
means the approval no longer applies, and the correct behaviour is to ask again.
`test_an_approval_does_not_authorise_a_changed_proposal` is the whole file.

Everything is serialisable, because the approver replies minutes or hours later
and the process that asked is long gone.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from ..core.clock import Clock, SystemClock
from ..core.errors import PermanentError
from ..core.ids import IdFactory
from ..core.money import Money

__all__ = [
    "ApprovalRequest",
    "ApprovalStore",
    "Decision",
    "Proposal",
    "UncertaintyDetector",
    "UncertaintySignal",
    "Verdict",
]


def _hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


class Verdict(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"
    #: The approver changed the proposal before approving it. Common and
    #: important: "yes, but send it to finance instead".
    AMENDED = "amended"


@dataclass(frozen=True)
class Proposal:
    """Exactly what the agent intends to do, in a form a human can read."""

    action: str
    summary: str
    #: The concrete arguments. Hashed, so a change invalidates the approval.
    arguments: dict[str, Any] = field(default_factory=dict)
    #: What the approver needs in order to judge it — retrieved evidence,
    #: the cost, who is affected. Validated context, not a raw prompt dump.
    context: dict[str, Any] = field(default_factory=dict)
    reversible: bool = True
    cost: Money = field(default_factory=Money.zero)

    @property
    def fingerprint(self) -> str:
        """Covers what will HAPPEN, not how it was explained.

        `summary` and `context` are excluded deliberately: rewording an
        explanation should not invalidate an approval, while changing a single
        argument must.
        """
        return _hash({"action": self.action, "arguments": self.arguments})

    def render(self) -> str:
        lines = [
            f"Action: {self.action}",
            f"  {self.summary}",
            f"  reversible: {'yes' if self.reversible else 'NO'}",
        ]
        if self.cost:
            lines.append(f"  cost: {self.cost.format_adaptive()}")
        for key, value in sorted(self.arguments.items()):
            lines.append(f"  {key} = {value!r}")
        return "\n".join(lines)


@dataclass(frozen=True)
class ApprovalRequest:
    id: str
    proposal: Proposal
    #: The graph checkpoint to resume from. Carried so the run can continue in
    #: a different process — see graph/runtime.py.
    checkpoint: dict[str, Any] = field(default_factory=dict)
    reasons: tuple[str, ...] = ()
    requested_at: str = ""

    @property
    def fingerprint(self) -> str:
        return self.proposal.fingerprint


@dataclass(frozen=True)
class Decision:
    request_id: str
    verdict: Verdict
    #: The fingerprint of what the approver actually saw. The whole point.
    approved_fingerprint: str
    decided_by: str = ""
    decided_at: str = ""
    note: str = ""
    #: Set for AMENDED — the arguments the approver substituted.
    amended_arguments: dict[str, Any] = field(default_factory=dict)

    def authorises(self, proposal: Proposal) -> bool:
        """Does this decision authorise THIS proposal?

        False when the proposal changed after the human saw it. Between asking
        and answering, an agent can re-plan, retry, or have its state mutated by
        another branch — and a decision keyed only on a request id would let the
        human's "yes" authorise something they never read.
        """
        if self.verdict is Verdict.REJECTED:
            return False
        # One comparison covers APPROVED and AMENDED alike, because `decide()`
        # already folded any amendments in when it computed this fingerprint.
        # An amendment is not a special case at execution time; it is simply a
        # different thing having been approved.
        return self.approved_fingerprint == proposal.fingerprint


@dataclass
class ApprovalStore:
    """Pending requests and their decisions. Durable in production; in-memory here."""

    ids: IdFactory = field(default_factory=IdFactory)
    clock: Clock = field(default_factory=SystemClock)
    requests: dict[str, ApprovalRequest] = field(default_factory=dict)
    decisions: dict[str, Decision] = field(default_factory=dict)

    def ask(
        self,
        proposal: Proposal,
        checkpoint: dict[str, Any] | None = None,
        reasons: tuple[str, ...] = (),
    ) -> ApprovalRequest:
        request = ApprovalRequest(
            id=self.ids.new("apr"),
            proposal=proposal,
            checkpoint=dict(checkpoint or {}),
            reasons=reasons,
            requested_at=self.clock.now().isoformat(),
        )
        self.requests[request.id] = request
        return request

    def decide(
        self,
        request_id: str,
        verdict: Verdict,
        decided_by: str,
        note: str = "",
        amended_arguments: dict[str, Any] | None = None,
    ) -> Decision:
        request = self.requests.get(request_id)
        if request is None:
            raise PermanentError("no such approval request", request_id=request_id)
        decision = Decision(
            request_id=request_id,
            verdict=verdict,
            # For an amendment the authorised thing is the proposal WITH the
            # approver's changes applied — derived here from the stored request,
            # so it is provably built from what they were shown rather than from
            # something the caller passed in.
            approved_fingerprint=_apply_amendments(request.proposal, amended_arguments).fingerprint,
            decided_by=decided_by,
            decided_at=self.clock.now().isoformat(),
            note=note,
            amended_arguments=dict(amended_arguments or {}),
        )
        self.decisions[request_id] = decision
        return decision

    def decision_for(self, request_id: str) -> Decision | None:
        return self.decisions.get(request_id)

    def effective_proposal(self, request_id: str) -> Proposal | None:
        """What was actually authorised — the proposal plus any amendments.

        The caller executes THIS, not whatever proposal it happens to hold.
        """
        request = self.requests.get(request_id)
        decision = self.decisions.get(request_id)
        if request is None or decision is None or decision.verdict is Verdict.REJECTED:
            return None
        return _apply_amendments(request.proposal, decision.amended_arguments)

    def pending(self) -> list[ApprovalRequest]:
        return [r for r in self.requests.values() if r.id not in self.decisions]


def _apply_amendments(proposal: Proposal, amendments: dict[str, Any] | None) -> Proposal:
    if not amendments:
        return proposal
    return Proposal(
        action=proposal.action,
        summary=proposal.summary,
        arguments={**proposal.arguments, **amendments},
        context=proposal.context,
        reversible=proposal.reversible,
        cost=proposal.cost,
    )


@dataclass(frozen=True)
class UncertaintySignal:
    name: str
    weight: float
    detail: str = ""


@dataclass
class UncertaintyDetector:
    """Decides when a human should be asked.

    Tuned to ask rarely. An approver who sees forty requests an hour approves
    the forty-first without reading it, at which point the gate has become a
    delay rather than a control.
    """

    threshold: float = 0.6
    #: Actions above this cost are escalated regardless of confidence.
    expensive_above: Money = field(default_factory=lambda: Money.from_usd("1.00"))
    #: Grounding support below this is a real signal that the answer is thin.
    weak_support_below: float = 0.7

    def assess(
        self,
        proposal: Proposal,
        support_rate: float = 1.0,
        escalations_exhausted: bool = False,
        guardrail_findings: tuple[str, ...] = (),
        model_declined: bool = False,
    ) -> tuple[bool, tuple[UncertaintySignal, ...]]:
        signals: list[UncertaintySignal] = []

        if not proposal.reversible:
            # Overriding, not weighted. Deleting a customer's data with high
            # confidence is still deleting a customer's data.
            return True, (
                UncertaintySignal("irreversible", 1.0, f"{proposal.action} cannot be undone"),
            )

        if support_rate < self.weak_support_below:
            signals.append(
                UncertaintySignal("weak_grounding", 0.4, f"support rate {support_rate:.0%}")
            )
        if escalations_exhausted:
            signals.append(
                UncertaintySignal("escalations_exhausted", 0.3, "the strongest tier was not enough")
            )
        if guardrail_findings:
            signals.append(UncertaintySignal("guardrail", 0.35, ", ".join(guardrail_findings[:3])))
        if model_declined:
            signals.append(UncertaintySignal("model_declined", 0.3, "the model hedged or refused"))
        if proposal.cost > self.expensive_above:
            signals.append(UncertaintySignal("expensive", 0.4, proposal.cost.format_adaptive()))

        total = sum(s.weight for s in signals)
        return total >= self.threshold, tuple(signals)

    def explain(self, signals: tuple[UncertaintySignal, ...]) -> str:
        if not signals:
            return "no uncertainty signals"
        return "; ".join(f"{s.name} ({s.detail})" for s in signals)
