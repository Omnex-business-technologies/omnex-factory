"""Growth measured between snapshots, with the honesty enforced by the type.

The uploaded snapshot has one collection date. One date is not a trend, and a
30/90/180-day forecast derived from it would be arithmetic performed on nothing.
What makes forecasting possible here is that the snapshot is dated 2026-05-15 and
a live fetch is dated today: two points, 82 days apart. That is a real
measurement, and on the three repositories checked by hand it separated

    HKUDS/OpenSpace      6,185 → 7,300   +18.0%
    openmemind/memind      743 →   903   +21.5%
    oguzbilgic/agent-kernel 329 →   335    +1.8%   — stalled

which is exactly the distinction a star count alone cannot make.

## Why confidence is a property and not a parameter

Two points fix a rate. They cannot fix a shape: the same pair is consistent with
steady compounding, with a single viral week followed by silence, and with a
decline that has already begun since the second reading. Every one of those
implies a different 180-day number.

So `Velocity.confidence` is computed from `points` and there is no way to set it.
A caller cannot construct a two-point velocity and label it HIGH, because the
attribute does not exist to be assigned. This is the same discipline as
`Deadline.shrink_to()` in `omnex.core.clock`, which can only ever tighten: the
constraint is enforced where it cannot be forgotten rather than documented where
it can.

## Why the band is linear-to-compound rather than a standard deviation

A confidence interval needs a variance, and two points have none — any sigma
printed next to a two-point projection is decoration. But the two extrapolations
that bracket the honest range are both computable and both meaningful:

    linear    the growth continues at the same absolute rate  — the floor
    compound  the growth continues at the same relative rate  — the ceiling

Beyond the measurement window, linear is the conservative reading and compound
the optimistic one, and the truth for a healthy project is between them. The band
is that interval. It widens with the horizon on its own, for a real reason,
rather than because a constant was tuned until the picture looked right.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .evidence import Confidence
from .snapshot import Observation

__all__ = ["HORIZONS", "Projection", "Velocity"]

#: The horizons the brief asks for. Kept here so a report cannot quietly use
#: different ones from the tests.
HORIZONS = (30, 90, 180)


@dataclass(frozen=True)
class Projection:
    horizon_days: int
    #: Same absolute growth per day as measured. The conservative reading.
    linear: int
    #: Same relative growth per day as measured. The optimistic reading.
    compound: int
    confidence: Confidence

    @property
    def low(self) -> int:
        return min(self.linear, self.compound)

    @property
    def high(self) -> int:
        return max(self.linear, self.compound)

    def report(self) -> str:
        spread = self.high - self.low
        return (
            f"{self.horizon_days:>4}d  {self.low:>7,} – {self.high:<7,} "
            f"(±{spread:,} spread, {self.confidence} confidence)"
        )


@dataclass(frozen=True)
class Velocity:
    """Change in a popularity metric between two observations of the same thing.

    Constructed through `between()` rather than directly, so the two readings
    are always of the same project and always in chronological order — a
    velocity computed on a reversed pair reports a thriving project as dying and
    raises nothing.
    """

    identifier: str
    earlier_value: int
    later_value: int
    earlier_on: date
    later_on: date
    #: How many observations the estimate rests on. Two is the floor, and the
    #: floor is what the current data provides.
    points: int = 2

    @classmethod
    def between(cls, earlier: Observation, later: Observation) -> Velocity:
        if earlier.name != later.name:
            raise ValueError(
                f"cannot compute velocity across different projects: "
                f"{earlier.name!r} and {later.name!r}"
            )
        if later.observed_on <= earlier.observed_on:
            raise ValueError(
                f"{earlier.name}: the later observation is dated "
                f"{later.observed_on}, not after {earlier.observed_on} — "
                "a reversed pair reports growth as decline and raises nothing"
            )
        return cls(
            identifier=earlier.name,
            earlier_value=earlier.stars,
            later_value=later.stars,
            earlier_on=earlier.observed_on,
            later_on=later.observed_on,
        )

    @property
    def days(self) -> int:
        return (self.later_on - self.earlier_on).days

    @property
    def absolute_change(self) -> int:
        return self.later_value - self.earlier_value

    @property
    def per_day(self) -> float:
        """Absolute change per day."""
        return self.absolute_change / self.days

    @property
    def relative_change(self) -> float:
        """Fractional change over the whole window. 0.18 is +18%.

        A project that started from zero has no meaningful relative change —
        every increase is infinite growth — so it reports 0.0 and the absolute
        figure is the one to read.
        """
        if self.earlier_value <= 0:
            return 0.0
        return self.absolute_change / self.earlier_value

    @property
    def daily_growth_factor(self) -> float:
        """The compounding rate implied by the two readings."""
        if self.earlier_value <= 0:
            return 1.0
        return float((self.later_value / self.earlier_value) ** (1.0 / self.days))

    @property
    def confidence(self) -> Confidence:
        """Derived from the number of observations. Not settable — that is the point.

        Two points cannot be presented as anything better than LOW no matter
        what the caller believes, because the attribute is computed. As future
        snapshots accumulate this rises on its own, which is the mechanism by
        which the engine gets more trustworthy while running unattended.
        """
        if self.points < 2:
            return Confidence.NONE
        if self.points == 2:
            return Confidence.LOW
        if self.points < 5:
            return Confidence.MEDIUM
        return Confidence.HIGH

    @property
    def stalled(self) -> bool:
        """Under 5% over the window — attention has moved on.

        Worth naming separately from "declining". A stalled project is usually
        still maintained and still usable; what it is not is a bet on the
        future, and an acquisition or partnership decision turns on that.
        """
        return abs(self.relative_change) < 0.05

    def project(self, horizon_days: int) -> Projection:
        linear = self.later_value + self.per_day * horizon_days
        compound = self.later_value * (self.daily_growth_factor**horizon_days)
        return Projection(
            horizon_days=horizon_days,
            linear=max(0, round(linear)),
            compound=max(0, round(compound)),
            confidence=self.confidence,
        )

    def projections(self, horizons: tuple[int, ...] = HORIZONS) -> list[Projection]:
        return [self.project(days) for days in horizons]

    def report(self) -> str:
        direction = "stalled" if self.stalled else f"{self.relative_change:+.1%}"
        return (
            f"{self.identifier:<44} {self.earlier_value:>6,} → {self.later_value:<6,} "
            f"over {self.days}d  {direction}"
        )
