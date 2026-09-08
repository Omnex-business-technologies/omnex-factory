"""Rate limiting that does not let twice the limit through at the window edge.

The obvious implementation is a fixed window: count requests per minute, reset
on the minute. It is wrong in a specific, exploitable way. A client that sends
its full quota at 10:00:59 and again at 10:01:00 has sent **twice the limit in
one second** while never exceeding the counter, and the burst lands on the
backend exactly as if there were no limiter. Every fixed-window limiter has this
hole and most only discover it under attack.

So this is GCRA — the leaky-bucket-as-a-meter formulation. Instead of counting,
it tracks a single timestamp, the *theoretical arrival time* of the next
conforming request. Constant time, one float of state per key, exactly smooth,
and burst is an explicit parameter rather than an accident of where the window
boundary fell.

Two things it gets right that a token bucket usually does not:

**`retry_after` is exact.** GCRA already knows when the next request would
conform, so a rejected caller is told precisely how long to wait rather than
being sent away to guess and retry-storm. That number flows into `RateLimited`,
which retry.py already honours.

**Checking is not the same as consuming.** `peek()` answers "would this be
allowed" without spending quota. A guardrail pipeline that checks a limit, then
fails validation, then returns — while having already consumed the caller's
quota — bills a tenant for requests that never ran.

Keys are arbitrary strings, so the same limiter serves per-tenant, per-user,
per-IP and per-tenant-per-route by composing the key. Eviction is on read, since
an unbounded key map is a memory leak with a slow fuse, and per-IP keys in
particular are attacker-controlled.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.clock import Clock, SystemClock
from ..core.errors import RateLimited

__all__ = ["Decision", "RateLimit", "RateLimiter"]


@dataclass(frozen=True)
class RateLimit:
    """`rate` requests per `period` seconds, tolerating a burst of `burst`."""

    rate: int
    period_seconds: float = 60.0
    #: Requests allowed to arrive back to back before smoothing applies. 1 means
    #: perfectly smooth — usually too strict for real clients, which batch.
    burst: int = 1

    def __post_init__(self) -> None:
        if self.rate <= 0:
            raise ValueError("rate must be positive")
        if self.period_seconds <= 0:
            raise ValueError("period must be positive")
        if self.burst < 1:
            raise ValueError("burst must be at least 1")

    @property
    def emission_interval(self) -> float:
        """Seconds between conforming requests at the sustained rate."""
        return self.period_seconds / self.rate

    @property
    def delay_tolerance(self) -> float:
        """How far ahead of schedule a burst may run."""
        return self.emission_interval * self.burst


@dataclass(frozen=True)
class Decision:
    allowed: bool
    #: Seconds until a conforming request. Zero when allowed.
    retry_after: float = 0.0
    #: Requests still available in the burst allowance, for response headers.
    remaining: int = 0

    def raise_if_limited(self, key: str = "") -> None:
        if not self.allowed:
            raise RateLimited(
                "rate limit exceeded",
                retry_after=self.retry_after,
                key=key,
            )


@dataclass
class RateLimiter:
    """GCRA limiter over arbitrary string keys."""

    limit: RateLimit
    clock: Clock = field(default_factory=SystemClock)
    #: Keys untouched for this long are dropped on the next sweep. Per-IP keys
    #: are attacker-controlled, so an unbounded map is a memory leak someone
    #: else decides when to trigger.
    idle_eviction_seconds: float = 3600.0
    max_keys: int = 100_000
    _tat: dict[str, float] = field(default_factory=dict)
    _last_sweep: float = 0.0

    def check(self, key: str, cost: int = 1) -> Decision:
        """Consume `cost` units if conforming. Returns the decision either way."""
        return self._evaluate(key, cost, consume=True)

    def peek(self, key: str, cost: int = 1) -> Decision:
        """Would this be allowed? Consumes nothing.

        For a pipeline that may reject a request for other reasons after the
        limit check — consuming there bills a tenant for work never done.
        """
        return self._evaluate(key, cost, consume=False)

    def _evaluate(self, key: str, cost: int, consume: bool) -> Decision:
        if cost < 1:
            raise ValueError("cost must be at least 1")
        now = self.clock.monotonic()
        self._maybe_sweep(now)

        interval = self.limit.emission_interval
        tolerance = self.limit.delay_tolerance
        increment = interval * cost

        tat = max(self._tat.get(key, now), now)
        # Conforming when the new theoretical arrival time stays inside the
        # tolerance window ahead of now.
        new_tat = tat + increment
        allowed = new_tat - now <= tolerance

        if not allowed:
            return Decision(
                allowed=False,
                retry_after=max(0.0, new_tat - now - tolerance),
                remaining=self._remaining(tat, now, interval, tolerance),
            )

        if consume:
            self._tat[key] = new_tat
        return Decision(
            allowed=True,
            retry_after=0.0,
            remaining=self._remaining(new_tat if consume else tat, now, interval, tolerance),
        )

    @staticmethod
    def _remaining(tat: float, now: float, interval: float, tolerance: float) -> int:
        return max(0, int((tolerance - max(0.0, tat - now)) / interval))

    def reset(self, key: str) -> None:
        self._tat.pop(key, None)

    def _maybe_sweep(self, now: float) -> None:
        if now - self._last_sweep < self.idle_eviction_seconds and len(self._tat) < self.max_keys:
            return
        self._last_sweep = now
        cutoff = now - self.idle_eviction_seconds
        stale = [k for k, tat in self._tat.items() if tat < cutoff]
        for key in stale:
            del self._tat[key]
        if len(self._tat) >= self.max_keys:
            # Still over after evicting idle keys: drop the oldest. Shedding
            # limiter state is a worse outcome than an OOM only in theory —
            # in practice the OOM takes the whole process with it.
            ordered = sorted(self._tat.items(), key=lambda kv: kv[1])
            for key, _ in ordered[: len(self._tat) - self.max_keys + 1]:
                del self._tat[key]

    @property
    def tracked_keys(self) -> int:
        return len(self._tat)
