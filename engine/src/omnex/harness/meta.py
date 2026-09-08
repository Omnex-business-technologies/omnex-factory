"""The outer loop: watching whether the inner loop is still worth running.

A loop can only see its own metric. That is Goodhart, and it is why the support
bot tied to ticket-resolution rate learns to close tickets rather than solve
them — the number climbs for months while the thing it stood for gets worse.

The published answer is a second loop that watches the first, reads where its
search is stuck, and changes how it searches. Reported result: five times better
on the same model, because the improvement came from the architecture rather
than from raw intelligence. The inner loop gets stuck because a model returns to
its own priors even after they stop working, and the outer loop's job is to
break that.

## What ours watches that theirs does not

Theirs watches the score. A score that creeps upward is indistinguishable from
progress — right up until you divide by what it cost.

Ours watches **cost per accepted change**, in pico-dollars, which the engine
already measures everywhere else. That single ratio separates three situations a
score alone conflates:

    score up,   cost per accepted change flat or falling   → genuinely improving
    score up,   cost per accepted change rising            → STUCK, and paying
                                                             more each round to
                                                             stay there
    score flat, cost per accepted change rising            → stop

The middle row is the one nobody catches. It looks like progress in every
dashboard and it is the most expensive state a loop can be in, because the
metric keeps rewarding the spend.

## What the outer loop may not do

It may change how the inner loop searches: the order, the breadth, whether to
abandon an approach and restart. It may **never** touch a frozen criterion.
An outer loop permitted to relax what counts as success would optimise the
easiest thing available to it — the definition — which is the failure the whole
contract exists to prevent, arriving one level up.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from enum import StrEnum

from ..core.money import Money
from .contract import Contract
from .state import RunState

__all__ = ["Diagnosis", "Health", "Intervention", "diagnose"]


class Health(StrEnum):
    IMPROVING = "improving"
    #: Still accepting changes, but each one costs more than the last.
    STUCK = "stuck"
    #: Accepting nothing, and spending to do it.
    STALLED = "stalled"
    #: Not enough rounds to say anything honest.
    UNKNOWN = "unknown"


class Intervention(StrEnum):
    """What the outer loop may change. Never the definition of success."""

    CONTINUE = "continue"
    #: Abandon the current approach and start the criterion differently.
    RESTART_APPROACH = "restart_approach"
    #: Force exploration away from what has already been tried.
    DIVERSIFY = "diversify"
    #: Cost per accepted change has stopped justifying the run.
    STOP = "stop"


@dataclass(frozen=True)
class Diagnosis:
    health: Health
    intervention: Intervention
    accepted: int
    spent: Money
    cost_per_accepted: Money
    #: Earlier-half versus later-half cost per accepted change.
    trend: float
    detail: str

    def report(self) -> str:
        return (
            f"{self.health.upper()} → {self.intervention}: {self.accepted} accepted, "
            f"{self.spent.format_adaptive()} spent, "
            f"{self.cost_per_accepted.format_adaptive()} per accepted change. {self.detail}"
        )


def _cost_per_accepted(attempts: list[tuple[bool, int]]) -> float:
    """Picos spent per accepted change. `inf` when nothing was accepted."""
    spent = sum(cost for _, cost in attempts)
    accepted = sum(1 for ok, _ in attempts if ok)
    if accepted == 0:
        return float("inf") if spent else 0.0
    return spent / accepted


def diagnose(
    state: RunState,
    contract: Contract,
    *,
    min_rounds: int = 4,
    worsening_ratio: float = 1.5,
) -> Diagnosis:
    """Is this loop still earning its budget?

    `contract` is taken so the caller cannot route a diagnosis around it, and is
    used only to confirm there is something frozen to protect. Nothing here
    mutates it — this function has no path to.
    """
    rounds = [(a.accepted, a.cost_picos) for a in state.attempts]
    accepted = sum(1 for ok, _ in rounds if ok)
    spent = Money.from_picos(sum(cost for _, cost in rounds))

    if len(rounds) < min_rounds:
        return Diagnosis(
            health=Health.UNKNOWN,
            intervention=Intervention.CONTINUE,
            accepted=accepted,
            spent=spent,
            cost_per_accepted=Money.zero(),
            trend=1.0,
            detail=f"{len(rounds)} rounds is too few to judge; {min_rounds} needed.",
        )

    overall = _cost_per_accepted(rounds)
    half = len(rounds) // 2
    early = _cost_per_accepted(rounds[:half])
    late = _cost_per_accepted(rounds[half:])

    per_accepted = (
        Money.zero() if overall in (0.0, float("inf")) else Money.from_picos(int(overall))
    )

    if accepted == 0:
        return Diagnosis(
            health=Health.STALLED,
            intervention=Intervention.RESTART_APPROACH,
            accepted=0,
            spent=spent,
            cost_per_accepted=Money.zero(),
            trend=float("inf"),
            detail=(
                "nothing has been accepted across the whole run — patching the same "
                "approach again will not change that; throw it out and start differently."
            ),
        )

    # A later half that accepts nothing is the clearest possible worsening.
    if late == float("inf"):
        return Diagnosis(
            health=Health.STUCK,
            intervention=Intervention.DIVERSIFY,
            accepted=accepted,
            spent=spent,
            cost_per_accepted=per_accepted,
            trend=float("inf"),
            detail=(
                "the recent half accepted nothing while continuing to spend — the search "
                "has returned to priors that stopped working."
            ),
        )

    trend = late / early if early > 0 else 1.0

    if trend >= worsening_ratio:
        # The expensive middle case: still accepting, paying more each round.
        stopping = trend >= worsening_ratio * 2
        return Diagnosis(
            health=Health.STUCK,
            intervention=Intervention.STOP if stopping else Intervention.DIVERSIFY,
            accepted=accepted,
            spent=spent,
            cost_per_accepted=per_accepted,
            trend=trend,
            detail=(
                f"cost per accepted change is {trend:.1f}x its earlier level. The score "
                "may still be rising; this is what paying more to stand still looks like."
            ),
        )

    return Diagnosis(
        health=Health.IMPROVING,
        intervention=Intervention.CONTINUE,
        accepted=accepted,
        spent=spent,
        cost_per_accepted=per_accepted,
        trend=trend,
        detail=f"cost per accepted change is {trend:.2f}x its earlier level, {len(contract.frozen_keys)} anchors held.",
    )


def mean_cost_per_accepted(states: list[RunState]) -> Money:
    """Across several runs — the number that says whether the harness is paying.

    Averaged over runs rather than over attempts, because a single enormous run
    would otherwise decide the figure for every small one.
    """
    ratios = [_cost_per_accepted([(a.accepted, a.cost_picos) for a in s.attempts]) for s in states]
    usable = [r for r in ratios if r not in (0.0, float("inf"))]
    if not usable:
        return Money.zero()
    return Money.from_picos(int(statistics.fmean(usable)))
