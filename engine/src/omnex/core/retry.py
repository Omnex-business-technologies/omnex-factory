"""Retry with backoff, deadline-aware and jittered.

Three decisions here are load-bearing.

**Full jitter, not fixed backoff.** `base * 2**attempt` alone synchronises
clients: everything that failed during one upstream blip retries at the same
instant, which is the blip's second wave. Full jitter — sleeping a uniform
random amount between zero and the computed ceiling — spreads that wave out. It
is measurably better than "exponential plus a bit of noise" under contention,
and it is the reason the RNG is injected: a jittered schedule that cannot be
made deterministic cannot be asserted on.

**The deadline outranks the schedule.** A policy that allows five attempts
inside a 10-second deadline must not sleep 32 seconds before attempt four. When
the next delay would not fit, the loop stops *now* and raises the failure it
already has, rather than sleeping through the deadline and raising a timeout
that hides the real cause.

**Only `retryable` errors are retried.** Not "any exception". A `KeyError` in a
response parser is a bug, and retrying it four times turns one stack trace into
four and delays the fix. Errors classify themselves (see errors.py); this module
just obeys.
"""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from random import Random
from typing import Any, TypeVar

from .clock import Clock, Deadline, SystemClock
from .errors import OmnexError, RateLimited

__all__ = ["Attempt", "RetryPolicy", "retry_call", "retry_call_async"]

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    """How many times, how long between, and how long in total."""

    max_attempts: int = 4
    base_delay: float = 0.5
    max_delay: float = 30.0
    #: Multiply the ceiling by this each attempt. 2.0 is the usual doubling.
    multiplier: float = 2.0
    #: When an upstream states `Retry-After`, obey it instead of the computed
    #: delay — it is information we do not otherwise have. Capped by max_delay
    #: so a provider cannot pin a worker for an hour with one header.
    honour_retry_after: bool = True

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.base_delay < 0 or self.max_delay < 0:
            raise ValueError("delays must not be negative")

    def ceiling_for(self, attempt: int) -> float:
        """Upper bound of the jitter window before attempt `attempt` (1-based)."""
        raw = self.base_delay * (self.multiplier ** max(0, attempt - 1))
        return min(self.max_delay, raw)

    def delay_for(self, attempt: int, rng: Random, error: BaseException | None = None) -> float:
        if self.honour_retry_after and isinstance(error, RateLimited) and error.retry_after:
            return min(self.max_delay, error.retry_after)
        return rng.uniform(0.0, self.ceiling_for(attempt))


@dataclass(frozen=True)
class Attempt:
    """One observed attempt. Handed to `on_attempt` so callers can emit a span or metric."""

    number: int
    error: BaseException | None
    delay: float
    will_retry: bool


def _should_retry(exc: BaseException) -> bool:
    if isinstance(exc, OmnexError):
        return exc.retryable
    # Non-omnex exceptions are treated as bugs unless a caller wraps them. A
    # library raising a bare ConnectionError is the caller's job to classify —
    # doing it here by exception name has been tried and misclassifies.
    return False


def retry_call(
    fn: Callable[[], T],
    policy: RetryPolicy | None = None,
    *,
    clock: Clock | None = None,
    rng: Random | None = None,
    deadline: Deadline | None = None,
    on_attempt: Callable[[Attempt], None] | None = None,
) -> T:
    """Call `fn`, retrying retryable failures under `policy` and `deadline`."""
    policy = policy or RetryPolicy()
    clock = clock or SystemClock()
    rng = rng or Random()
    deadline = deadline or Deadline.never(clock)

    last: BaseException | None = None
    for attempt in range(1, policy.max_attempts + 1):
        if deadline.expired():
            break
        try:
            result = fn()
        except BaseException as exc:
            last = exc
            if not _should_retry(exc) or attempt == policy.max_attempts:
                if on_attempt:
                    on_attempt(Attempt(attempt, exc, 0.0, will_retry=False))
                raise
            delay = policy.delay_for(attempt, rng, exc)
            # Do not sleep into the deadline just to fail on the far side of it.
            if delay > deadline.remaining():
                if on_attempt:
                    on_attempt(Attempt(attempt, exc, 0.0, will_retry=False))
                raise
            if on_attempt:
                on_attempt(Attempt(attempt, exc, delay, will_retry=True))
            clock.sleep(delay)
        else:
            if on_attempt:
                on_attempt(Attempt(attempt, None, 0.0, will_retry=False))
            return result

    assert last is not None  # loop only exits early after a failure
    raise last


async def retry_call_async(
    fn: Callable[[], Awaitable[T]],
    policy: RetryPolicy | None = None,
    *,
    clock: Clock | None = None,
    rng: Random | None = None,
    deadline: Deadline | None = None,
    on_attempt: Callable[[Attempt], None] | None = None,
    sleep: Callable[[float], Awaitable[Any]] | None = None,
) -> T:
    """Async twin of `retry_call`.

    `sleep` is injectable separately from `clock` because an async test wants
    the wait recorded (FakeClock) without a real `asyncio.sleep`; passing the
    fake clock's `sleep` through a trivial coroutine gives both.
    """
    policy = policy or RetryPolicy()
    clock = clock or SystemClock()
    rng = rng or Random()
    deadline = deadline or Deadline.never(clock)

    async def _default_sleep(seconds: float) -> None:
        if seconds > 0:
            await asyncio.sleep(seconds)

    do_sleep = sleep or _default_sleep

    last: BaseException | None = None
    for attempt in range(1, policy.max_attempts + 1):
        if deadline.expired():
            break
        try:
            outcome = fn()
            result = await outcome if inspect.isawaitable(outcome) else outcome
        except BaseException as exc:
            last = exc
            if not _should_retry(exc) or attempt == policy.max_attempts:
                if on_attempt:
                    on_attempt(Attempt(attempt, exc, 0.0, will_retry=False))
                raise
            delay = policy.delay_for(attempt, rng, exc)
            if delay > deadline.remaining():
                if on_attempt:
                    on_attempt(Attempt(attempt, exc, 0.0, will_retry=False))
                raise
            if on_attempt:
                on_attempt(Attempt(attempt, exc, delay, will_retry=True))
            await do_sleep(delay)
        else:
            if on_attempt:
                on_attempt(Attempt(attempt, None, 0.0, will_retry=False))
            return result

    assert last is not None
    raise last
