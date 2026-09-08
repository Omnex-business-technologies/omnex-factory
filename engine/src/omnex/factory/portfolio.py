"""Every deployed agent as an asset, and one explicit decision each.

A set of agents nobody decides about is not a portfolio, it is a list. The
decision is the artifact here — scale, optimise, refactor, merge, reposition,
license, kill — and the point of writing it down per asset is that *no decision*
stops being available. An agent that is quietly losing money while nobody has
said "keep it" is the normal failure, and it does not show up anywhere.

## Recommend is not decide

The same rule the node map runs on. `recommend()` reads measurements and
proposes; `enact()` records what a person chose and who they are. A machine that
retired its own agents on a ratio would be grading its own homework with a
budget, and `KILL` is the decision where that matters most — it is irreversible
and it is the one an optimiser under cost pressure reaches for first.

So a recommendation carries `by=""`. Only `enact()` fills that in, and
`Portfolio.decided()` reports what a person actually settled, separately from
what the numbers suggested.

## Three refusals, each guarding a way this becomes theatre

**Too few runs is `WATCH`, never a verdict.** Below `MINIMUM_RUNS` the
economics cannot answer, so neither can this. A portfolio that grades a
three-run agent is inventing a signal.

**Nothing is killed on an unmeasured dimension.** If accuracy was never
measured, `KILL` is not available — you would be retiring an agent for a number
nobody has. It becomes `WATCH` with the missing measurement named, which is
actionable in a way "kill it" is not.

**`MERGE` needs two.** It is the one decision that cannot be made about an asset
in isolation, so it is derived from overlap across the portfolio rather than
offered per agent.

## The honest limit, stated where it cannot be missed

This repository has one live module. A portfolio of one is n=1: the machinery
here is ready for more, and is not evidence that there are more. `report()` says
so on its first line whenever there are fewer than two assets, because a
one-row portfolio table otherwise reads exactly like a portfolio.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..core.errors import ValidationFailed
from ..core.money import Money
from .economics import MINIMUM_RUNS, AgentEconomics, Margin

__all__ = ["Asset", "Decision", "Portfolio", "Recommendation"]

#: Below this accuracy an agent is failing at the job rather than costing too
#: much for it, and the answer is the work, not the price.
ACCURACY_FLOOR = 0.7

#: Period-over-period run growth that counts as growing rather than flat.
GROWTH_FLOOR = 0.1


class Decision(StrEnum):
    """What happens to an asset. `WATCH` is a real answer, not a placeholder."""

    WATCH = "watch"
    SCALE = "scale"
    OPTIMISE = "optimise"
    REFACTOR = "refactor"
    MERGE = "merge"
    REPOSITION = "reposition"
    LICENSE = "license"
    KILL = "kill"


@dataclass(frozen=True)
class Asset:
    """One deployed agent, with every dimension either measured or absent.

    `None` means *not measured* and never *zero*. The distinction is the whole
    reason the fields are optional: an accuracy of 0.0 is a broken agent and an
    accuracy of `None` is a broken measurement, and treating the second as the
    first retires working software.
    """

    agent: str
    #: Capabilities it holds, for the overlap that produces MERGE.
    capabilities: frozenset[str] = frozenset()
    accuracy: float | None = None
    retention: float | None = None
    #: Runs this period over runs last period, minus one. `None` before there
    #: are two periods to compare.
    growth: float | None = None
    #: Named risks a person recorded. Unlisted is not the same as none.
    risks: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.agent.strip():
            raise ValidationFailed("an asset needs an agent name")
        for name in ("accuracy", "retention"):
            value = getattr(self, name)
            if value is not None and not 0.0 <= value <= 1.0:
                raise ValidationFailed(f"{name} {value} is outside 0.0-1.0", **{name: value})


@dataclass(frozen=True)
class Recommendation:
    """A proposal with its evidence, or a decision a person made and signed."""

    agent: str
    decision: Decision
    reasons: tuple[str, ...]
    #: Empty while a machine proposed it. `enact()` is the only thing that fills
    #: this in, and only a filled one is a decision.
    by: str = ""

    @property
    def is_decided(self) -> bool:
        return bool(self.by)

    def report(self) -> str:
        who = f" — decided by {self.by}" if self.by else " (proposed, awaiting a person)"
        return f"{self.agent}: {self.decision}{who}\n  " + "\n  ".join(self.reasons)


class Portfolio:
    """Live agents, their measurements, and the decision standing against each.

    **Single-writer. Not thread-safe, on purpose.** `add()` and `enact()` are
    things a person does, one at a time, from a review — not a request path. A
    lock here would be ceremony around an operation that has never had a second
    caller, and the honest limit costs less than the machinery.

    The distinction against `AgentEconomics`, which this reads and which IS
    locked: runs land from wherever work finishes, concurrently and often.
    Decisions land from a meeting.
    """

    def __init__(self, economics: AgentEconomics) -> None:
        self._economics = economics
        self._assets: dict[str, Asset] = {}
        self._decided: dict[str, Recommendation] = {}

    def add(self, asset: Asset) -> None:
        if asset.agent in self._assets:
            raise ValidationFailed(f"{asset.agent!r} is already in the portfolio")
        self._assets[asset.agent] = asset

    @property
    def assets(self) -> tuple[Asset, ...]:
        return tuple(self._assets[name] for name in sorted(self._assets))

    # ── proposing ─────────────────────────────────────────────────────────
    def recommend(self, agent: str) -> Recommendation:
        """Read the measurements and propose. Never decides; see the module docstring."""
        asset = self._assets.get(agent)
        if asset is None:
            raise ValidationFailed(f"{agent!r} is not in the portfolio", known=sorted(self._assets))

        summary = self._economics.by_agent(agent)
        reasons: list[str] = []

        if summary.runs < MINIMUM_RUNS:
            reasons.append(
                f"{summary.runs} runs is below the {MINIMUM_RUNS} the economics needs "
                "to answer, so nothing here is a verdict"
            )
            return Recommendation(agent, Decision.WATCH, tuple(reasons))

        losing = summary.total.picos <= 0
        growing = asset.growth is not None and asset.growth >= GROWTH_FLOOR
        reasons.append(
            f"{summary.runs} runs, margin {summary.total.format_adaptive()} "
            f"(worst run {summary.worst.format_adaptive()})"
        )

        if asset.accuracy is not None and asset.accuracy < ACCURACY_FLOOR:
            reasons.append(
                f"accuracy {asset.accuracy:.0%} is below {ACCURACY_FLOOR:.0%} — this is a "
                "quality problem wearing a cost problem's clothes, and repricing it "
                "will not help"
            )
            return Recommendation(agent, Decision.REFACTOR, tuple(reasons))

        if losing:
            if asset.accuracy is None:
                reasons.append(
                    "accuracy was never measured, so retiring this would be retiring it "
                    "for a number nobody has — measure it first"
                )
                return Recommendation(agent, Decision.WATCH, tuple(reasons))
            if growing:
                reasons.append(
                    f"losing money but usage is growing {asset.growth:+.0%} — the "
                    f"largest cost is {self._economics.worst_category(agent)}"
                )
                return Recommendation(agent, Decision.OPTIMISE, tuple(reasons))
            reasons.append("losing money with no growth to pay for the loss")
            return Recommendation(agent, Decision.KILL, tuple(reasons))

        if growing:
            reasons.append(f"profitable and growing {asset.growth:+.0%}")
            return Recommendation(agent, Decision.SCALE, tuple(reasons))

        if asset.retention is not None and asset.retention < 0.5:
            reasons.append(
                f"profitable but only {asset.retention:.0%} of customers return — "
                "the offer reaches the wrong buyer rather than the product being wrong"
            )
            return Recommendation(agent, Decision.REPOSITION, tuple(reasons))

        reasons.append(
            "profitable and flat: the margin is real and the demand is not moving, "
            "which is the shape that earns more licensed than operated"
        )
        return Recommendation(agent, Decision.LICENSE, tuple(reasons))

    def overlaps(self) -> tuple[tuple[str, str, frozenset[str]], ...]:
        """Pairs of agents sharing capabilities — the only source of `MERGE`.

        Per-asset rules cannot see this: two agents are each individually fine
        and together are one agent maintained twice.
        """
        names = sorted(self._assets)
        return tuple(
            (left, right, shared)
            for index, left in enumerate(names)
            for right in names[index + 1 :]
            if (shared := self._assets[left].capabilities & self._assets[right].capabilities)
        )

    # ── deciding ──────────────────────────────────────────────────────────
    def enact(self, agent: str, decision: Decision, by: str, note: str = "") -> Recommendation:
        """Record what a person chose. The only path to a decided recommendation."""
        if agent not in self._assets:
            raise ValidationFailed(f"{agent!r} is not in the portfolio")
        if not by.strip():
            raise ValidationFailed(
                "a decision needs somebody's name against it; an unsigned decision is "
                "one nobody can be asked about later",
                agent=agent,
            )
        proposed = self.recommend(agent)
        reasons = [f"proposed {proposed.decision}"]
        if note:
            reasons.append(note)
        if decision is not proposed.decision:
            reasons.append(f"a person chose {decision} instead, which outranks the proposal")
        settled = Recommendation(agent, decision, tuple(reasons), by=by)
        self._decided[agent] = settled
        return settled

    def decided(self) -> tuple[Recommendation, ...]:
        return tuple(self._decided[name] for name in sorted(self._decided))

    def undecided(self) -> tuple[str, ...]:
        """Assets nobody has said anything about — the normal failure, made visible."""
        return tuple(name for name in sorted(self._assets) if name not in self._decided)

    # ── reporting ─────────────────────────────────────────────────────────
    def summary(self) -> dict[str, Margin]:
        return {name: self._economics.by_agent(name) for name in sorted(self._assets)}

    def total_margin(self) -> Money:
        total = Money.zero()
        for margin in self.summary().values():
            total = total + margin.total
        return total

    def report(self) -> str:
        lines: list[str] = []
        if len(self._assets) < 2:
            lines.append(
                f"n={len(self._assets)}. This is not a portfolio yet — the machinery is "
                "ready for more assets and is not evidence that there are any."
            )
            lines.append("")
        lines.append(f"{len(self._assets)} assets · margin {self.total_margin().format_adaptive()}")
        for asset in self.assets:
            settled = self._decided.get(asset.agent)
            lines.append((settled or self.recommend(asset.agent)).report())
        for left, right, shared in self.overlaps():
            lines.append(
                f"{left} and {right} share {', '.join(sorted(shared))} — one capability "
                f"maintained twice is the case for {Decision.MERGE}"
            )
        if self.undecided():
            lines.append(
                "no decision recorded for: " + ", ".join(self.undecided()) + " — an asset "
                "nobody has decided about is the one that quietly loses money"
            )
        return "\n".join(lines)
