"""When routing saves money, and the exact point at which it stops.

Most routers ship without this file, and it is the difference between a cost
optimisation and a cost *story*.

## The break-even escalation rate

Send every query to the cheap model first; escalate to the expensive one when
the cheap answer is inadequate. With `c` the cost of a cheap call, `e` the cost
of an expensive one, and `r` the fraction that escalate:

    routed cost per query  =  c + r · e
    always-expensive cost  =  e

Routing wins only while `c + r·e < e`, that is:

    r  <  1 − c/e

So the break-even escalation rate is **one minus the price ratio**, and it says
something sharp that intuition gets wrong in both directions:

- Cheap tier 30× cheaper: break-even `r` = 96.7%. Escalation is nearly free;
  route aggressively, because even a mostly-failing cheap tier still wins.
- Cheap tier only 2× cheaper: break-even `r` = 50%. Escalate more than half the
  time and the router is *actively losing money* against having no router at
  all — while looking busy, adding a network hop, and doubling p99 latency.

The second case is common and almost never measured, because "we route to save
cost" is assumed rather than checked. `is_losing_money()` checks it against
observed traffic, and `headroom()` says how much slack is left before it flips.

Latency has the same shape and is not free either: an escalated request pays
both calls sequentially, so the p99 of a routed system is roughly the sum, not
the max. A router at 40% escalation with a 96% break-even is winning on money
and may still be losing on latency.

## Where the classifier's bias comes from

Route cheap when the *expected* cost is lower:

    c + (1−P)·e  <  e     ⟺     P > c/e

where `P` is the probability the cheap tier suffices. So the tolerance for
complexity on the cheap tier is set entirely by the price ratio, not by taste,
and `recommended_bias()` converts a ratio into the score shift that encodes it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.money import Money

__all__ = [
    "REFERENCE_PRICE_RATIO",
    "RouterEconomics",
    "break_even_escalation_rate",
    "recommended_bias",
]

#: The price ratio the default complexity thresholds were tuned against. A
#: deployment whose ratio differs gets a bias correction rather than new
#: thresholds, so there is one number to reason about instead of four.
REFERENCE_PRICE_RATIO = 10.0


def break_even_escalation_rate(cheap: Money, expensive: Money) -> float:
    """The escalation rate above which routing costs more than not routing.

    Returns 0.0 when the cheap tier is not actually cheaper — in which case any
    escalation at all loses, and the honest answer is to stop routing.
    """
    if expensive.picos <= 0:
        return 0.0
    ratio = cheap.picos / expensive.picos
    return max(0.0, 1.0 - ratio)


def recommended_bias(price_ratio: float, reference: float = REFERENCE_PRICE_RATIO) -> float:
    """Score shift for a given expensive/cheap price ratio.

    Derived from `P > c/e`: a bigger ratio lowers the probability the cheap tier
    must clear, so more complexity can be tolerated there (negative bias). A
    small ratio raises it sharply, and the router should become conservative
    fast (positive bias) — at a ratio near 1 there is nothing to win and
    everything to lose from a wasted first call.

    Clamped, because the formula's tails are steeper than any real threshold
    set should be moved by a single scalar.
    """
    if price_ratio <= 0:
        return 0.35
    raw = 0.5 * (1.0 / price_ratio - 1.0 / reference)
    return max(-0.15, min(0.35, raw))


@dataclass
class RouterEconomics:
    """Observed routing outcomes, and whether they are still worth it.

    Counts *decisions*, not calls: a request routed cheap and then escalated is
    one routed request with one escalation, not two requests. Getting that wrong
    halves the apparent escalation rate, which is exactly the direction that
    makes a losing router look fine.
    """

    routed_cheap: int = 0
    routed_expensive_directly: int = 0
    escalations: int = 0
    #: What was actually spent.
    spend: Money = field(default_factory=Money.zero)
    #: What the same traffic would have cost always using the reference model.
    baseline_spend: Money = field(default_factory=Money.zero)
    #: Per-call averages used for the break-even calculation, updated as
    #: observations arrive rather than assumed from the price sheet — the real
    #: ratio depends on prompt and answer lengths, which differ per tier.
    cheap_spend: Money = field(default_factory=Money.zero)
    expensive_spend: Money = field(default_factory=Money.zero)
    cheap_calls: int = 0
    expensive_calls: int = 0

    # ── recording ─────────────────────────────────────────────────────────
    def record_call(self, cost: Money, baseline: Money, tier_is_cheap: bool) -> None:
        self.spend = self.spend + cost
        self.baseline_spend = self.baseline_spend + baseline
        if tier_is_cheap:
            self.cheap_spend = self.cheap_spend + cost
            self.cheap_calls += 1
        else:
            self.expensive_spend = self.expensive_spend + cost
            self.expensive_calls += 1

    def record_decision(self, started_cheap: bool, escalated: bool) -> None:
        if started_cheap:
            self.routed_cheap += 1
        else:
            self.routed_expensive_directly += 1
        if escalated:
            self.escalations += 1

    # ── the question that matters ────────────────────────────────────────
    @property
    def escalation_rate(self) -> float:
        """Escalations over requests that *could* have escalated.

        Denominator is requests routed cheap, not all requests. Including
        requests sent straight to the expensive tier dilutes the rate and hides
        the failure it is meant to expose.
        """
        return 0.0 if not self.routed_cheap else self.escalations / self.routed_cheap

    @property
    def mean_cheap_cost(self) -> Money:
        return (
            Money.zero()
            if not self.cheap_calls
            else Money.from_picos(self.cheap_spend.picos // self.cheap_calls)
        )

    @property
    def mean_expensive_cost(self) -> Money:
        return (
            Money.zero()
            if not self.expensive_calls
            else Money.from_picos(self.expensive_spend.picos // self.expensive_calls)
        )

    def break_even(self) -> float | None:
        """Observed break-even rate, or None before both tiers have been seen."""
        if not self.cheap_calls or not self.expensive_calls:
            return None
        return break_even_escalation_rate(self.mean_cheap_cost, self.mean_expensive_cost)

    def is_losing_money(self) -> bool:
        """True when observed escalation has passed the break-even point."""
        threshold = self.break_even()
        return threshold is not None and self.escalation_rate > threshold

    def headroom(self) -> float | None:
        """Escalation-rate slack remaining. Negative means already losing."""
        threshold = self.break_even()
        return None if threshold is None else threshold - self.escalation_rate

    @property
    def saved(self) -> Money:
        return self.baseline_spend - self.spend

    @property
    def saved_percent(self) -> float:
        if not self.baseline_spend:
            return 0.0
        return 100.0 * self.saved.picos / self.baseline_spend.picos

    def report(self) -> str:
        lines = [
            f"routed {self.routed_cheap} cheap, {self.routed_expensive_directly} straight to strong",
            f"escalated {self.escalations} ({self.escalation_rate:.1%} of cheap-routed)",
            f"spend {self.spend.format_adaptive()} vs "
            f"{self.baseline_spend.format_adaptive()} always-strong "
            f"→ saved {self.saved.format_adaptive()} ({self.saved_percent:.1f}%)",
        ]
        threshold = self.break_even()
        if threshold is not None:
            verdict = "LOSING MONEY" if self.is_losing_money() else "ok"
            lines.append(
                f"break-even escalation rate {threshold:.1%}, "
                f"headroom {(self.headroom() or 0):+.1%} — {verdict}"
            )
        return "\n".join(lines)
