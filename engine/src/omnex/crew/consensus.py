"""Consensus between agents, and why a majority vote is the wrong rule here.

The obvious design is: three agents vote, majority wins. It is wrong for this
problem in two specific ways.

**Averaging hides disagreement, and the disagreement is the signal.** Two agents
confident yes and one confident no is not "yes with 67% confidence" — it is a
question a human should look at, and collapsing it to a number is how that
question stops being asked. `Consensus` therefore reports the dissent alongside
the outcome, and `contested` is what P15's uncertainty detector reads.

**Roles are not interchangeable voters.** A fact-checker that finds a claim
unsupported is not casting one vote among three; it has found something the
others merely did not look for. So the fact-checker holds a VETO, and — this is
the part that matters — a supervisor cannot silently overrule it. It can only
`override()`, which records who did it and why in the audit trail. Making the
override possible but expensive is the right shape: sometimes the fact-checker
is wrong, and a system with no escape hatch gets bypassed entirely.

Confidence is self-reported and treated as such. A model's stated confidence is
weakly calibrated at best, so it breaks ties and nothing more — it never
outvotes a veto and never turns a 1–2 minority into a majority.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum

__all__ = ["Consensus", "Opinion", "Position", "Role", "decide"]


class Role(StrEnum):
    SUPERVISOR = "supervisor"
    RESEARCHER = "researcher"
    WRITER = "writer"
    #: Holds a veto. Not a third voter.
    FACT_CHECKER = "fact_checker"


class Position(StrEnum):
    ACCEPT = "accept"
    REJECT = "reject"
    #: "I cannot tell from what I was given." Deliberately distinct from
    #: rejecting: it means fetch more evidence, not abandon the claim.
    ABSTAIN = "abstain"


@dataclass(frozen=True)
class Opinion:
    role: Role
    position: Position
    #: Self-reported, weakly calibrated, used only to break ties.
    confidence: float = 0.5
    reason: str = ""
    #: Chunk ids or page numbers. An opinion with no evidence is an assertion,
    #: and the report says which is which.
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class Consensus:
    accepted: bool
    #: True when the agents genuinely disagreed. Read by P15 to decide whether
    #: to involve a human — the number alone would have hidden this.
    contested: bool
    reason: str
    opinions: tuple[Opinion, ...] = ()
    vetoed_by: Role | None = None
    overridden_by: str = ""

    @property
    def dissent(self) -> tuple[Opinion, ...]:
        target = Position.ACCEPT if self.accepted else Position.REJECT
        return tuple(o for o in self.opinions if o.position is not target)

    def report(self) -> str:
        verdict = "ACCEPTED" if self.accepted else "REJECTED"
        lines = [f"{verdict} — {self.reason}" + ("  [CONTESTED]" if self.contested else "")]
        if self.vetoed_by:
            lines.append(f"  vetoed by {self.vetoed_by}")
        if self.overridden_by:
            lines.append(f"  veto overridden by {self.overridden_by}")
        for opinion in self.opinions:
            evidence = (
                f" ({len(opinion.evidence)} sources)" if opinion.evidence else " (no evidence)"
            )
            lines.append(
                f"  {opinion.role:<14} {opinion.position:<8} "
                f"{opinion.confidence:.2f}{evidence}  {opinion.reason[:60]}"
            )
        return "\n".join(lines)


def decide(opinions: Sequence[Opinion]) -> Consensus:
    """Combine opinions into an outcome, preserving the disagreement."""
    if not opinions:
        return Consensus(accepted=False, contested=False, reason="no opinions were offered")

    veto = next(
        (o for o in opinions if o.role is Role.FACT_CHECKER and o.position is Position.REJECT),
        None,
    )
    if veto is not None:
        # A veto is not outvoted. A fact-checker that found a claim unsupported
        # has found something the others did not look for, and counting it as
        # one of three is how an unsupported claim ships with two agreeing votes.
        return Consensus(
            accepted=False,
            contested=any(o.position is Position.ACCEPT for o in opinions),
            reason=f"fact-checker veto: {veto.reason or 'claim not supported'}",
            opinions=tuple(opinions),
            vetoed_by=Role.FACT_CHECKER,
        )

    voting = [o for o in opinions if o.position is not Position.ABSTAIN]
    if not voting:
        return Consensus(
            accepted=False,
            contested=False,
            reason="every agent abstained — gather more evidence rather than deciding",
            opinions=tuple(opinions),
        )

    accepts = [o for o in voting if o.position is Position.ACCEPT]
    rejects = [o for o in voting if o.position is Position.REJECT]
    contested = bool(accepts and rejects)

    if len(accepts) == len(rejects):
        # Tie. Self-reported confidence breaks it and does nothing else — it
        # cannot turn a minority into a majority anywhere else in this function.
        accept_weight = sum(o.confidence for o in accepts)
        reject_weight = sum(o.confidence for o in rejects)
        accepted = accept_weight > reject_weight
        return Consensus(
            accepted=accepted,
            contested=True,
            reason=f"tie broken on confidence ({accept_weight:.2f} vs {reject_weight:.2f})",
            opinions=tuple(opinions),
        )

    accepted = len(accepts) > len(rejects)
    return Consensus(
        accepted=accepted,
        contested=contested,
        reason=f"{len(accepts)} accept, {len(rejects)} reject"
        + (f", {len(opinions) - len(voting)} abstain" if len(voting) != len(opinions) else ""),
        opinions=tuple(opinions),
    )


def override(consensus: Consensus, by: str, reason: str) -> Consensus:
    """Overrule a veto. Possible, recorded, and never silent.

    An escape hatch that exists on purpose: sometimes the fact-checker is wrong,
    and a system with no way past it gets routed around entirely, which is worse
    than one where the bypass is logged. The cost of using it is that it names
    you in the audit trail.
    """
    if consensus.vetoed_by is None:
        return consensus
    if not reason.strip():
        raise ValueError("overriding a veto requires a stated reason")
    return Consensus(
        accepted=True,
        contested=True,
        reason=f"veto overridden: {reason}",
        opinions=consensus.opinions,
        vetoed_by=consensus.vetoed_by,
        overridden_by=by,
    )


@dataclass
class Crew:
    """Supervisor coordinating researcher, writer and fact-checker.

    The orchestration is a graph (see graph/runtime.py) so the budget ceilings,
    checkpointing and approval interrupts are the same ones every other system
    here uses. CrewAI is an adapter for teams already committed to it; the
    in-repo path is the default so this is testable without a framework.
    """

    audit: object  # AuditTrail; loose to avoid an import cycle
    opinions: list[Opinion] = field(default_factory=list)

    def contribute(self, opinion: Opinion) -> None:
        self.opinions.append(opinion)
        self.audit.record(  # type: ignore[attr-defined]
            actor=str(opinion.role),
            action="opinion",
            position=str(opinion.position),
            confidence=opinion.confidence,
            reason=opinion.reason,
            evidence=list(opinion.evidence),
        )

    def conclude(self) -> Consensus:
        result = decide(self.opinions)
        self.audit.record(  # type: ignore[attr-defined]
            actor=str(Role.SUPERVISOR),
            action="consensus",
            accepted=result.accepted,
            contested=result.contested,
            reason=result.reason,
            vetoed_by=str(result.vetoed_by) if result.vetoed_by else "",
        )
        return result

    def override_veto(self, consensus: Consensus, by: str, reason: str) -> Consensus:
        result = override(consensus, by=by, reason=reason)
        self.audit.record(  # type: ignore[attr-defined]
            actor=by, action="veto_override", reason=reason
        )
        return result
