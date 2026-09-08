"""The loop closing: what happened becomes what is known, and only through a check.

Everything upstream of this produces outcomes. A run costs money and is accepted
or not. A compiler round-trips or loses a field. A person decides to scale an
agent or retire it. Left there, those are three separate logs nobody reads
together, and the harness that watches whether any of this is worth running has
nothing to watch.

This turns them into one stream `harness.meta.diagnose()` can read — the outer
loop already watches **pico-dollar cost per accepted change**, which is the ratio
that separates genuine progress from paying more each round to stand still, and
it needs observations shaped like attempts to do it.

## The closure, and the one thing it may not do

An accepted improvement writes back a **node claim**: this run suggests that
capability X is now backed by symbol Y. That claim then has to survive
`node_map.py`, which resolves the symbol by importing it.

So the loop can propose a capability. It cannot mark one implemented. `claim()`
emits `proposed` and there is no parameter that makes it `implemented` — the same
refusal `node_map` makes for the same reason, arriving one level up where the
pressure to relax it is strongest, because here the thing proposing is the thing
being measured on how much it produces.

A machine that could write `implemented` into `nodes.json` would close the loop
against itself: it would generate the evidence, grade the evidence, and report
coverage climbing. Requiring a symbol that imports and a person who agrees is
what makes the climb mean something.

## Refused observations

An observation with no cost is refused. Everything in this chain spends — a run
spends tokens, a compile spends an interpreter, a decision spends somebody's
attention — and a zero-cost observation dilutes cost per accepted change toward
zero, which reports the loop as cheaper the more of these it emits. That is the
one number the outer loop cannot afford to have gamed, and emitting free
observations is exactly how a loop would game it.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..core.errors import ValidationFailed
from ..core.money import Money
from ..core.symbols import resolve
from ..harness.state import RunState
from .economics import AgentEconomics, Run
from .portfolio import Decision, Portfolio, Recommendation

__all__ = ["NodeClaim", "Observation", "Source", "claim", "observe", "to_run_state"]


class Source(StrEnum):
    """Where an observation came from. Kept, because they fail differently."""

    RUN = "run"
    COMPILE = "compile"
    DECISION = "decision"


@dataclass(frozen=True)
class Observation:
    """One thing that happened, priced, and judged accepted or not."""

    source: Source
    subject: str
    #: What was tried or produced. Short — this indexes, it does not store.
    change: str
    accepted: bool
    cost_picos: int
    reason: str = ""

    def __post_init__(self) -> None:
        if self.cost_picos <= 0:
            raise ValidationFailed(
                "an observation with no cost dilutes cost per accepted change toward "
                "zero, which reports the loop as cheaper the more of these it emits",
                source=str(self.source),
                subject=self.subject,
            )
        if not self.subject.strip() or not self.change.strip():
            raise ValidationFailed("an observation needs a subject and a change")
        if not self.accepted and not self.reason.strip():
            raise ValidationFailed(
                f"{self.subject}: a rejection with no reason is the part the next run "
                "needs most, and the part that is always dropped first",
                subject=self.subject,
            )


@dataclass(frozen=True)
class NodeClaim:
    """A capability this loop believes is now backed, and by what.

    `claim` is always `proposed`. There is no field that makes it `implemented`,
    and that is the closure: the loop generating the evidence may not also grade
    it. `node_map.py` resolves `symbol` by importing it, and a person decides
    whether the two names mean the same capability.
    """

    node: str
    symbol: str
    branch: str
    evidence: str
    claim: str = "proposed"

    def __post_init__(self) -> None:
        if self.claim != "proposed":
            raise ValidationFailed(
                f"a loop may propose a capability, never mark one {self.claim!r} — the "
                "thing producing the evidence does not get to grade it",
                node=self.node,
                attempted=self.claim,
            )
        reason = resolve(self.symbol)
        if reason is not None:
            raise ValidationFailed(
                f"claim for {self.node!r} names {self.symbol} — {reason}",
                node=self.node,
                symbol=self.symbol,
            )


def observe(
    *,
    economics: AgentEconomics | None = None,
    portfolio: Portfolio | None = None,
    compiles: tuple[tuple[str, bool, int, str], ...] = (),
) -> tuple[Observation, ...]:
    """Collect one stream out of the three places outcomes land.

    Runs, compiler results and portfolio decisions in one list, ordered runs
    first, because that is the order the outer loop's ratio is built from and a
    stream sorted by wall clock interleaves three different kinds of cost into a
    trend nobody can read.
    """
    out: list[Observation] = []

    for run in economics.runs if economics else ():
        out.append(_from_run(run))

    for subject, ok, picos, reason in compiles:
        out.append(
            Observation(
                source=Source.COMPILE,
                subject=subject,
                change="emit and re-read",
                accepted=ok,
                cost_picos=picos,
                reason=reason or ("" if ok else "the compiler did not round-trip"),
            )
        )

    for settled in portfolio.decided() if portfolio else ():
        out.append(_from_decision(settled))

    return tuple(out)


def _from_run(run: Run) -> Observation:
    """A run is an attempt: it spent, and it either produced something usable or not."""
    return Observation(
        source=Source.RUN,
        subject=run.agent,
        change=f"run {run.run_id}",
        accepted=run.accepted,
        cost_picos=max(run.cost.total.picos, 1),
        reason="" if run.accepted else "the run produced nothing the customer could use",
    )


#: Decisions that mean the asset earned its place. `WATCH` is deliberately not
#: here: deferring is not an acceptance, and counting it as one would let a
#: portfolio improve its accepted rate by declining to decide.
_ACCEPTING = frozenset({Decision.SCALE, Decision.LICENSE, Decision.OPTIMISE})


def _from_decision(settled: Recommendation) -> Observation:
    accepted = settled.decision in _ACCEPTING
    return Observation(
        source=Source.DECISION,
        subject=settled.agent,
        change=f"decided {settled.decision}",
        # Somebody's attention is the cost, and it is not free just because it
        # does not appear on an invoice. One pico stands for it rather than zero,
        # which the constructor refuses.
        cost_picos=1,
        accepted=accepted,
        reason="" if accepted else f"{settled.decision} is not the asset earning its place",
    )


def to_run_state(
    goal: str, observations: tuple[Observation, ...], contract_fingerprint: str = ""
) -> RunState:
    """Shape the stream so `harness.meta.diagnose()` can read it.

    The criterion each attempt is filed under is its source, so the diagnosis can
    tell "runs are getting more expensive per accepted result" from "the
    compilers keep breaking" — two situations one blended ratio reports
    identically.
    """
    state = RunState(goal=goal, contract_fingerprint=contract_fingerprint)
    for observation in observations:
        state.record(
            criterion=str(observation.source),
            change=f"{observation.subject}: {observation.change}",
            accepted=observation.accepted,
            reason=observation.reason,
            cost_picos=observation.cost_picos,
        )
    return state


def claim(node: str, symbol: str, branch: str, observations: tuple[Observation, ...]) -> NodeClaim:
    """Write an accepted improvement back as a proposal, or refuse to.

    Refuses when nothing was accepted. A loop that claims a capability from a
    stream of failures is claiming it from the fact that it ran, and running is
    not evidence.
    """
    accepted = [o for o in observations if o.accepted]
    if not accepted:
        raise ValidationFailed(
            f"nothing was accepted, so there is no improvement to claim for {node!r}; "
            "having run is not evidence",
            node=node,
            observations=len(observations),
        )
    spent = Money.from_picos(sum(o.cost_picos for o in observations))
    return NodeClaim(
        node=node,
        symbol=symbol,
        branch=branch,
        evidence=(
            f"{len(accepted)} of {len(observations)} observations accepted, "
            f"{spent.format_adaptive()} spent"
        ),
    )
