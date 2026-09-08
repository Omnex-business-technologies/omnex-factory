"""Time, as an injected dependency.

Every system in this engine has a deadline, a retry schedule, a latency
histogram or a cache TTL. If those read the wall clock directly, three things
follow: the tests sleep, the tests are flaky, and the interesting cases — a
backoff that runs past its deadline, a cache entry that expires mid-request, a
budget that runs out on the fourth attempt — become untestable, because
reproducing them means waiting for real seconds to pass.

So nothing here calls `time.monotonic()` or `datetime.now()`. They call a
`Clock`. In production that is `SystemClock`. In tests it is `FakeClock`, whose
`advance()` moves time by exactly as much as the assertion needs and whose
`sleep()` is instantaneous — which is why the whole suite runs in under a
second while still asserting on hour-long TTLs.

`monotonic()` and `now()` are separate on purpose. `now()` is a wall-clock
timestamp for records a human will read (audit trails, trace start times); it
can jump backwards when NTP corrects the host. `monotonic()` cannot go
backwards and is the only thing durations are measured with. Measuring a
latency percentile with `now()` is how you get a negative p99.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Protocol, runtime_checkable

__all__ = ["Clock", "Deadline", "FakeClock", "SystemClock"]


@runtime_checkable
class Clock(Protocol):
    """The only source of time any omnex module is allowed to read."""

    def now(self) -> datetime:
        """Wall-clock time, always timezone-aware UTC. For records, not durations."""
        ...

    def monotonic(self) -> float:
        """Seconds from an arbitrary origin, never decreasing. For durations."""
        ...

    def sleep(self, seconds: float) -> None:
        """Block for `seconds`. Negative or zero returns immediately."""
        ...


class SystemClock:
    """The real clock. The only implementation that touches the host."""

    __slots__ = ()

    def now(self) -> datetime:
        return datetime.now(UTC)

    def monotonic(self) -> float:
        return _time.monotonic()

    def sleep(self, seconds: float) -> None:
        if seconds > 0:
            _time.sleep(seconds)


@dataclass
class FakeClock:
    """A clock that only moves when a test moves it.

    `sleep()` advances instead of blocking, so code under test that backs off
    for 32 seconds costs the suite nothing while still being observed to have
    waited 32 seconds. `slept` keeps every requested duration, because "did it
    back off with the right schedule" is a different assertion from "did it
    finish in time", and both matter for P16's retry logic.
    """

    start: datetime = datetime(2026, 1, 1, tzinfo=UTC)
    _elapsed: float = 0.0
    slept: list[float] = field(default_factory=list)

    def now(self) -> datetime:
        return self.start + timedelta(seconds=self._elapsed)

    def monotonic(self) -> float:
        return self._elapsed

    def sleep(self, seconds: float) -> None:
        if seconds > 0:
            self.slept.append(seconds)
            self._elapsed += seconds

    def advance(self, seconds: float) -> None:
        """Move time forward without recording it as a sleep the code performed."""
        if seconds < 0:
            raise ValueError("time does not run backwards")
        self._elapsed += seconds

    @property
    def total_slept(self) -> float:
        return sum(self.slept)


@dataclass(frozen=True)
class Deadline:
    """A wall-clock budget, expressed against a monotonic origin.

    Held by value and passed down a call stack so a nested provider call knows
    how much of the caller's budget is left rather than starting its own timeout
    from zero. That distinction is the difference between a 30s request timeout
    and three sequential 30s retries inside it.
    """

    expires_at: float
    clock: Clock

    @classmethod
    def after(cls, seconds: float, clock: Clock) -> Deadline:
        return cls(expires_at=clock.monotonic() + seconds, clock=clock)

    @classmethod
    def never(cls, clock: Clock) -> Deadline:
        return cls(expires_at=float("inf"), clock=clock)

    def remaining(self) -> float:
        """Seconds left; never negative, so callers can pass it straight to a timeout."""
        return max(0.0, self.expires_at - self.clock.monotonic())

    def expired(self) -> bool:
        return self.clock.monotonic() >= self.expires_at

    def shrink_to(self, seconds: float) -> Deadline:
        """A tighter deadline for a sub-call. Can only ever move the expiry earlier."""
        candidate = self.clock.monotonic() + seconds
        return Deadline(expires_at=min(self.expires_at, candidate), clock=self.clock)
