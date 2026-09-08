"""The gate that runs before anything else: is a loop worth building at all?

This is the single largest margin protector in the package, and it is the part
every enthusiastic write-up leaves out. A long-running harness burns tokens
whether or not it ships anything — it re-reads context, retries, explores. Run
against the wrong task it costs more than it returns, forever, quietly.

Two independent sources supply the conditions and they do not overlap, so both
are checked.

**The Karpathy conditions — is a loop economic?**

    repeats          the task recurs, at least weekly. A one-off is better
                     served by one good prompt; the setup never pays back.
    verified         a test, type check, linter or build can fail the work
                     without a human in the room. No automated check means
                     somebody reads every diff — the job the loop was meant to
                     remove.
    budget           the token budget can absorb the waste. This is why loops
                     read as obvious to people with free tokens and reckless to
                     people paying per call.
    tools            the agent can run the code and see what breaks. Without
                     that it iterates blind.

**The autoresearch conditions — is the task even shaped like a loop?**

    goal             a defined metric that moves
    method           a defined way to make a change
    assessment       a standardised way to score the result

A task can be economic and the wrong shape, or the right shape and uneconomic.
Both refuse.

## Why this refuses rather than warns

A warning in a log is read once, by the person who already decided. `evaluate()`
returns a `Verdict` whose `raise_if_not_worth_it()` stops the run and names
every condition that failed, so the failure is legible before the money is
spent rather than in the invoice afterwards.

Nothing here is clever. It is a checklist, and the reason it earns its place is
that the expensive mistake in this category is not a bad loop — it is a
perfectly good loop pointed at a task that could never repay it.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..core.errors import ValidationFailed

__all__ = ["Condition", "Verdict", "evaluate"]


class Condition(StrEnum):
    """One reason a loop may not be worth building. Named, never a bare bool."""

    REPEATS = "repeats"
    VERIFIED = "verified"
    BUDGET = "budget"
    TOOLS = "tools"
    GOAL = "goal"
    METHOD = "method"
    ASSESSMENT = "assessment"

    @property
    def why(self) -> str:
        return _WHY[self]


_WHY: dict[Condition, str] = {
    Condition.REPEATS: (
        "the task does not recur often enough for the setup to pay back — one good "
        "prompt is cheaper than a loop that runs once"
    ),
    Condition.VERIFIED: (
        "nothing can fail the work automatically, so a human reads every result — "
        "which is the job the loop was supposed to remove"
    ),
    Condition.BUDGET: (
        "the budget cannot absorb the waste; loops re-read, retry and explore, and "
        "spend whether or not a run ships anything"
    ),
    Condition.TOOLS: (
        "the agent cannot run the work and observe what breaks, so it iterates blind"
    ),
    Condition.GOAL: "there is no metric that moves, so 'better' is unfalsifiable",
    Condition.METHOD: "there is no defined way to make a change, so there is nothing to iterate",
    Condition.ASSESSMENT: (
        "there is no standardised way to score a result, so two runs cannot be compared"
    ),
}


@dataclass(frozen=True)
class Verdict:
    """Whether to build the loop, and precisely why not."""

    failed: tuple[Condition, ...]

    @property
    def worth_it(self) -> bool:
        return not self.failed

    def report(self) -> str:
        if self.worth_it:
            return "worth it: all seven conditions hold"
        lines = [f"NOT worth it — {len(self.failed)} condition(s) fail:"]
        lines.extend(f"  {c}: {c.why}" for c in self.failed)
        return "\n".join(lines)

    def raise_if_not_worth_it(self) -> None:
        """Stop before the spend, naming every failure at once.

        All of them, not the first: fixing one condition and being refused
        again on the next is how somebody concludes the check is the problem.
        """
        if not self.worth_it:
            raise ValidationFailed(self.report(), failed=[str(c) for c in self.failed])


def evaluate(
    *,
    repeats_weekly: bool,
    verification_is_automated: bool,
    budget_absorbs_waste: bool,
    agent_has_tools: bool,
    has_goal_metric: bool,
    has_change_method: bool,
    has_standard_assessment: bool,
) -> Verdict:
    """Check all seven conditions.

    Every argument is keyword-only and required. There are no defaults, because
    a default here is a quiet assumption about somebody else's budget — and the
    one that would default to True is exactly the one worth thinking about.
    """
    checks = (
        (Condition.REPEATS, repeats_weekly),
        (Condition.VERIFIED, verification_is_automated),
        (Condition.BUDGET, budget_absorbs_waste),
        (Condition.TOOLS, agent_has_tools),
        (Condition.GOAL, has_goal_metric),
        (Condition.METHOD, has_change_method),
        (Condition.ASSESSMENT, has_standard_assessment),
    )
    return Verdict(failed=tuple(condition for condition, holds in checks if not holds))
