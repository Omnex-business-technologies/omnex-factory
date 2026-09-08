"""Money attached to a run, not to a spreadsheet.

Every primitive this needs already existed — `core.Money` counts picos,
`obs.CostLedger` accumulates events, `router.economics` answers *is this routing
strategy still worth it*, `intel.revenue` prices offers. None of them was
attached to an agent run. That is what this is: wiring, mostly, with four
modelling decisions that are not.

## Acquisition is not a per-run cost, and subtracting it as one is wrong

The tempting formula is `revenue - model - tools - infra - storage - review -
acquisition`, per run. It produces a number and the number is nonsense.
Acquisition is paid once per customer; charging all of it against every run
makes a customer look worse the more they use the product, which inverts the
signal exactly. Contribution margin here is the VARIABLE cost only, and
acquisition is answered separately by `payback_runs()`: how many runs of this
customer's observed margin repay what it cost to win them.

## A failed run still costs

Revenue may be zero when a run fails. Cost is not. Excluding failures makes the
cheapest possible agent one that fails everything, which is the wrong incentive
to encode in a ledger — the same settlement rule the copilot bills on and
`mcp.McpClient` bills on, for the same reason.

## Margin is a distribution

`obs/cost.py` argues this for spend and it is more true for margin: a handful of
long agent runs carry most of the cost, so the mean margin sits above almost
every expensive run and the tail is invisible. `worst()` and `p10()` are the
numbers that say "cap the loop", and the mean is the number that says everything
is fine.

## A verdict needs enough runs to be one

`router.economics.break_even()` returns `None` before it has seen both tiers,
rather than guessing. `is_losing_money()` here does the same below
`MINIMUM_RUNS`: a margin computed from three runs is noise, and reporting it as
a verdict is how somebody kills a working agent or keeps a losing one.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime

from ..core.errors import ValidationFailed
from ..core.money import Money
from .spec import AgentSpec

__all__ = [
    "MINIMUM_RUNS",
    "AgentEconomics",
    "Margin",
    "Run",
    "RunCost",
]

#: Below this many runs, `is_losing_money()` answers None rather than guessing.
#: Ten is not a statistical claim; it is the point below which a single expensive
#: run moves the answer, which is what makes a verdict meaningless.
MINIMUM_RUNS = 10


@dataclass(frozen=True)
class RunCost:
    """What one run spent, by category, because the categories act differently.

    A single total says the agent is expensive. The split says which lever
    works: a chatty agent is model-dominated and wants a router, a tool-heavy
    one wants caching, and one dominated by human review does not have a cost
    problem at all — it has an accuracy problem wearing one.
    """

    model: Money = field(default_factory=Money.zero)
    tools: Money = field(default_factory=Money.zero)
    infra: Money = field(default_factory=Money.zero)
    storage: Money = field(default_factory=Money.zero)
    human_review: Money = field(default_factory=Money.zero)

    def __post_init__(self) -> None:
        for name in ("model", "tools", "infra", "storage", "human_review"):
            if getattr(self, name).picos < 0:
                raise ValidationFailed(f"{name} cost is negative, which is a refund path")

    @property
    def total(self) -> Money:
        return self.model + self.tools + self.infra + self.storage + self.human_review

    @property
    def largest(self) -> str:
        """Which category dominates. The lever, named."""
        by_name = {
            "model": self.model,
            "tools": self.tools,
            "infra": self.infra,
            "storage": self.storage,
            "human_review": self.human_review,
        }
        return max(by_name, key=lambda k: by_name[k].picos)


@dataclass(frozen=True)
class Run:
    """One execution of one agent for one customer, priced."""

    run_id: str
    agent: str
    customer: str
    at: datetime
    revenue: Money
    cost: RunCost
    #: Whether the run produced a result the customer could use. A failed run is
    #: still recorded, still costed, and usually earns nothing.
    accepted: bool = True

    @property
    def margin(self) -> Money:
        """Contribution margin: revenue less variable cost. Acquisition is elsewhere."""
        return self.revenue - self.cost.total


@dataclass(frozen=True)
class Margin:
    """A margin summary that refuses to be read as a single number."""

    runs: int
    revenue: Money
    cost: Money
    total: Money
    mean: Money
    median: Money
    p10: Money
    worst: Money
    accepted: int

    @property
    def acceptance_rate(self) -> float:
        return 0.0 if not self.runs else self.accepted / self.runs

    def as_dict(self) -> dict[str, object]:
        return {
            "runs": self.runs,
            "revenue": str(self.revenue),
            "cost": str(self.cost),
            "margin_total": str(self.total),
            "margin_mean": str(self.mean),
            "margin_median": str(self.median),
            "margin_p10": str(self.p10),
            "margin_worst": str(self.worst),
            "acceptance_rate": round(self.acceptance_rate, 4),
        }


def _percentile(sorted_picos: list[int], fraction: float) -> Money:
    if not sorted_picos:
        return Money.zero()
    index = min(int(fraction * len(sorted_picos)), len(sorted_picos) - 1)
    return Money.from_picos(sorted_picos[index])


def _summarise(runs: list[Run]) -> Margin:
    picos = sorted(run.margin.picos for run in runs)
    revenue = Money.zero()
    cost = Money.zero()
    for run in runs:
        revenue = revenue + run.revenue
        cost = cost + run.cost.total
    total = revenue - cost
    # Integer division on the TOTAL rather than averaging per-run means, so the
    # mean never drifts from the sum it is supposed to describe.
    mean = Money.from_picos(total.picos // len(runs)) if runs else Money.zero()
    return Margin(
        runs=len(runs),
        revenue=revenue,
        cost=cost,
        total=total,
        mean=mean,
        median=_percentile(picos, 0.5),
        p10=_percentile(picos, 0.10),
        worst=Money.from_picos(picos[0]) if picos else Money.zero(),
        accepted=sum(1 for run in runs if run.accepted),
    )


class AgentEconomics:
    """Every run of every agent, and the questions worth asking of them.

    In-process and deliberately not a database, for the reason `obs.CostLedger`
    gives: this is the aggregate that feeds a decision, and the durable record is
    the per-tenant usage table written on the request path.

    **Writes are thread-safe; reads are a snapshot.** `record()` and
    `record_acquisition()` hold a lock. The query methods do not, so a summary
    taken while runs are landing describes a consistent set of completed runs
    and may not include one recorded a microsecond ago. That is the right
    trade for a margin report and the wrong one for a billing invoice — which is
    what the durable table above is for.
    """

    def __init__(self) -> None:
        # Locked for the same reason `obs.CostLedger` is: this is a money
        # aggregate mutated from wherever runs finish, and the duplicate check
        # below is a check-then-act pair. Two threads recording the same
        # `run_id` both find it absent, both append, and the refusal that exists
        # precisely to stop double counting is the thing the race defeats.
        self._lock = threading.Lock()
        self._runs: list[Run] = []
        self._acquisition: dict[str, Money] = {}

    # ── recording ─────────────────────────────────────────────────────────
    def record(self, run: Run) -> None:
        """Check and append under one lock, or the duplicate refusal is decorative."""
        with self._lock:
            if any(existing.run_id == run.run_id for existing in self._runs):
                raise ValidationFailed(
                    f"run {run.run_id!r} is already recorded; counting one run twice "
                    "moves the margin in whichever direction that run happened to go",
                    run_id=run.run_id,
                )
            self._runs.append(run)

    def record_acquisition(self, customer: str, cost: Money) -> None:
        """What it cost to win this customer. Charged once, never per run."""
        with self._lock:
            self._acquisition[customer] = self._acquisition.get(customer, Money.zero()) + cost

    @property
    def runs(self) -> tuple[Run, ...]:
        return tuple(self._runs)

    # ── the questions ─────────────────────────────────────────────────────
    def overall(self) -> Margin:
        return _summarise(self._runs)

    def by_agent(self, agent: str) -> Margin:
        return _summarise([run for run in self._runs if run.agent == agent])

    def by_customer(self, customer: str) -> Margin:
        return _summarise([run for run in self._runs if run.customer == customer])

    def agents(self) -> tuple[str, ...]:
        return tuple(sorted({run.agent for run in self._runs}))

    def customers(self) -> tuple[str, ...]:
        return tuple(sorted({run.customer for run in self._runs}))

    def is_losing_money(self, agent: str | None = None) -> bool | None:
        """A live check, and `None` while there is not enough to answer with.

        Deliberately three-valued. A boolean forces a caller to treat "not
        enough runs yet" as one of the two verdicts, and whichever one it picks
        is wrong roughly half the time.
        """
        summary = self.by_agent(agent) if agent is not None else self.overall()
        if summary.runs < MINIMUM_RUNS:
            return None
        return summary.total.picos <= 0

    def payback_runs(self, customer: str) -> int | None:
        """Runs of observed margin needed to repay what winning this customer cost.

        `None` when nothing was spent acquiring them, and `None` again when the
        margin is not positive — an infinite payback reported as a large integer
        is a number somebody will put in a slide.
        """
        acquisition = self._acquisition.get(customer)
        if acquisition is None or acquisition.picos <= 0:
            return None
        summary = self.by_customer(customer)
        if summary.runs == 0 or summary.mean.picos <= 0:
            return None
        return -(-acquisition.picos // summary.mean.picos)

    def cost_drift(self, agent: str, spec: AgentSpec) -> float | None:
        """Observed cost per run over what the spec projected. `None` too early.

        The gate at `Stage.UNIT_ECONOMICS` clears an agent on its `CostModel`,
        which is an estimate. This is the measurement, and the two are not the
        same claim — `lib/core/agents/metering.ts` returns `estimated: boolean`
        for exactly this reason, and an estimate displayed as a measurement is
        the failure both of them prevent.

        A ratio above one means the agent costs more than it was approved on.
        Nothing here decides what to do about that: `Stage.SCALE_OR_KILL` is a
        stage a person reaches, and a factory that killed its own agents on a
        ratio would be grading its own homework with a budget.
        """
        runs = [run for run in self._runs if run.agent == agent]
        if len(runs) < MINIMUM_RUNS:
            return None
        projected = spec.cost_model.total
        if projected.picos <= 0:  # pragma: no cover - CostModel refuses this
            return None
        observed = sum(run.cost.total.picos for run in runs) // len(runs)
        return observed / projected.picos

    def worst_category(self, agent: str) -> str | None:
        """Which cost category dominates this agent's spend — the lever to pull."""
        runs = [run for run in self._runs if run.agent == agent]
        if not runs:
            return None
        totals = {
            name: sum(getattr(run.cost, name).picos for run in runs)
            for name in ("model", "tools", "infra", "storage", "human_review")
        }
        return max(totals, key=lambda name: totals[name])

    def report(self) -> str:
        lines: list[str] = []
        for agent in self.agents():
            summary = self.by_agent(agent)
            verdict = self.is_losing_money(agent)
            state = (
                f"not enough runs to say ({summary.runs} of {MINIMUM_RUNS})"
                if verdict is None
                else ("LOSING MONEY" if verdict else "ok")
            )
            lines.append(
                f"{agent}: {summary.runs} runs, margin {summary.total.format_adaptive()} "
                f"(mean {summary.mean.format_adaptive()}, worst "
                f"{summary.worst.format_adaptive()}), "
                f"{summary.acceptance_rate:.0%} accepted — {state}"
            )
            lever = self.worst_category(agent)
            if lever:
                lines.append(f"  largest cost: {lever}")
        return "\n".join(lines) or "no runs recorded"
