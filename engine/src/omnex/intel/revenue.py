"""Revenue modelling in exact money, with the assumptions on the outside.

Every "market opportunity" slide in existence is a number with no derivation. The
number is usually right about direction and wrong by an order of magnitude about
size, and because the inputs are not written down nobody can find out which.

`Opportunity` takes the opposite approach: the inputs are the object, the
estimate is a computed property, and `explain()` prints both. If a reader thinks
the price is optimistic they change one field and see the payback move. That is
the only form of financial projection worth committing to a repository.

## Why `Money` rather than floats

`omnex.core.money.Money` is pico-dollar integers. Here the amounts are large
enough that float error would not change a decision — but mixing two money
representations in one codebase is how the small amounts, where it does change
decisions, eventually get computed in the wrong one. One representation.

## Payback, not revenue

`monthly_revenue` alone ranks a large slow-building product above a small
immediate one, which is backwards for a business that needs the next module to
fund the one after it. `payback_months` is the ranking field: build cost divided
by monthly margin, which answers "when does this stop costing us money" — the
question the sequencing decision actually turns on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from ..core.money import Money

__all__ = [
    "BusinessModel",
    "Complexity",
    "Opportunity",
    "Portfolio",
]


class Complexity(StrEnum):
    """Build size, expressed in the only unit that survives contact with reality."""

    TRIVIAL = "trivial"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

    @property
    def developer_days(self) -> int:
        return {"trivial": 2, "small": 8, "medium": 25, "large": 70}[self.value]


class BusinessModel(StrEnum):
    CREDITS = "credits"
    SUBSCRIPTION = "subscription"
    USAGE = "usage"
    SELF_HOST_LICENCE = "self_host_licence"
    SUPPORT = "support"
    MARKETPLACE = "marketplace"
    OPEN_CORE = "open_core"


@dataclass(frozen=True)
class Opportunity:
    """One thing we could build or sell, with every assumption named.

    `demand`, `competitive_intensity`, `defensibility` and `maintenance_burden`
    are 0.0–1.0 judgements. They are judgements — the module does not pretend
    otherwise, and `explain()` prints them so a disagreement lands on the input
    rather than on the conclusion.
    """

    name: str
    model: BusinessModel
    complexity: Complexity
    #: Realistic monthly recurring revenue once it is live and marketed.
    monthly_revenue: Money
    #: Share of revenue eaten by inference, storage and payment fees.
    variable_cost_share: float = 0.3
    demand: float = 0.5
    competitive_intensity: float = 0.5
    defensibility: float = 0.5
    scalability: float = 0.5
    maintenance_burden: float = 0.3
    #: What one developer-day costs. Explicit so the payback figure means
    #: something specific rather than being an index.
    day_rate: Money = field(default_factory=lambda: Money.from_usd("400.00"))
    notes: str = ""

    @property
    def build_cost(self) -> Money:
        return self.day_rate * self.complexity.developer_days

    @property
    def time_to_mvp_days(self) -> int:
        """Calendar days, not developer days — nobody works seven-day weeks.

        The 1.6 multiplier is the ratio this repository has actually run at,
        stated so it can be corrected rather than hidden in a constant.
        """
        return max(1, round(self.complexity.developer_days * 1.6))

    @property
    def monthly_margin(self) -> Money:
        keep = 1.0 - self.variable_cost_share
        return Money.from_picos(int(self.monthly_revenue.picos * keep))

    @property
    def payback_months(self) -> float:
        """When it stops costing money. `inf` if it never does."""
        if not self.monthly_margin.picos:
            return float("inf")
        return self.build_cost.picos / self.monthly_margin.picos

    @property
    def annual_margin(self) -> Money:
        return self.monthly_margin * 12

    @property
    def priority(self) -> float:
        """0–100. Rewards demand and defensibility, punishes crowding and payback.

        Maintenance is subtracted rather than ignored because the burden is paid
        every month forever while the build cost is paid once — a module that is
        cheap to ship and expensive to keep alive is how a small team stops
        shipping anything new.
        """
        payback_score = 1.0 / (1.0 + self.payback_months / 6.0)
        raw = (
            self.demand * 3.0
            + self.defensibility * 2.0
            + self.scalability * 1.5
            + payback_score * 2.5
            + (1.0 - self.competitive_intensity) * 1.5
            - self.maintenance_burden * 1.5
        )
        return max(0.0, min(100.0, 100.0 * raw / 10.5))

    def explain(self) -> str:
        return "\n".join(
            [
                f"{self.name} — {self.model}, {self.complexity} build",
                f"  build cost        {self.build_cost.format_adaptive():>12} "
                f"({self.complexity.developer_days} dev-days, ~{self.time_to_mvp_days} calendar)",
                f"  monthly revenue   {self.monthly_revenue.format_adaptive():>12} "
                f"(margin {self.monthly_margin.format_adaptive()} "
                f"at {1 - self.variable_cost_share:.0%})",
                f"  payback           {self.payback_months:>12.1f} months",
                f"  annual margin     {self.annual_margin.format_adaptive():>12}",
                f"  demand {self.demand:.2f} · defensibility {self.defensibility:.2f} · "
                f"competition {self.competitive_intensity:.2f} · "
                f"maintenance {self.maintenance_burden:.2f}",
                f"  priority          {self.priority:>12.1f}/100",
            ]
            + ([f"  {self.notes}"] if self.notes else [])
        )


@dataclass
class Portfolio:
    """A set of opportunities, sequenced by when each stops costing money."""

    opportunities: list[Opportunity]

    def by_priority(self) -> list[Opportunity]:
        return sorted(self.opportunities, key=lambda o: -o.priority)

    def build_order(self) -> list[Opportunity]:
        """Fastest payback first.

        Not the same as priority order, and the difference is the point: a
        self-funding sequence pays for the ambitious item with the margin from
        the boring one. Building highest-priority-first is how a team spends its
        runway on the thing it was most excited about.
        """
        return sorted(self.opportunities, key=lambda o: (o.payback_months, -o.priority))

    def total_annual_margin(self) -> Money:
        total = Money.zero()
        for item in self.opportunities:
            total = total + item.annual_margin
        return total

    def total_build_cost(self) -> Money:
        total = Money.zero()
        for item in self.opportunities:
            total = total + item.build_cost
        return total

    def report(self) -> str:
        lines = [
            f"{len(self.opportunities)} opportunities · "
            f"{self.total_build_cost().format_adaptive()} to build · "
            f"{self.total_annual_margin().format_adaptive()} annual margin at full run-rate",
            "",
            f"{'#':<3} {'opportunity':<34} {'model':<18} {'payback':>9} {'annual':>12} {'pri':>6}",
        ]
        for index, item in enumerate(self.build_order(), 1):
            payback = (
                "never" if item.payback_months == float("inf") else f"{item.payback_months:.1f}mo"
            )
            lines.append(
                f"{index:<3} {item.name[:34]:<34} {item.model:<18} {payback:>9} "
                f"{item.annual_margin.format_adaptive():>12} {item.priority:>6.1f}"
            )
        return "\n".join(lines)
