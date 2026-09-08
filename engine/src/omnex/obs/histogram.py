"""A bounded-error latency histogram, and the reason percentiles cannot be averaged.

The naive way to get a p95 is to keep every observation and sort. It is exact,
and it is unbounded: a service handling 2,000 requests per second accumulates
7.2 million floats an hour, per instance, per metric. The usual second attempt —
keep a running mean and standard deviation — cannot produce a percentile at all
unless the distribution is normal, and latency distributions never are. They are
long-tailed, which is precisely why anyone asks for p99.

So this is a log-linear bucketed histogram, the HdrHistogram idea: values below
64 are counted exactly, and above that each power of two is divided into 64
linear sub-buckets. That gives a hard relative-error bound of 1/64 — under 1.6%
— at any magnitude, from a 3-microsecond cache hit to a 90-second timeout, in
about 1,600 counters total regardless of how many observations arrive.

`percentile()` returns the bucket's UPPER edge, never its midpoint. For latency
the asymmetry is deliberate: reporting a p99 slightly high is a conservative
error, reporting it low tells you an SLO is met when it is not.

**The merge property is the point of the whole file.** Percentiles do not
average. Two instances each reporting p95 = 100ms do not imply the fleet's p95
is 100ms, and no arithmetic on those two numbers recovers the real one — the
information needed is gone. Histograms merge by adding bucket counts, which is
exact. Any fleet-wide percentile in this engine is computed by merging
histograms, and `test_merging_beats_averaging_percentiles` shows how far wrong
the averaging shortcut goes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

__all__ = ["PRECISION_BITS", "SUB_BUCKETS", "Histogram"]

PRECISION_BITS = 6
SUB_BUCKETS = 1 << PRECISION_BITS  # 64
#: Worst-case relative error of any reported value.
RELATIVE_ERROR = 1.0 / SUB_BUCKETS


def _index_of(value: int) -> int:
    """Bucket index for a non-negative integer observation."""
    if value < SUB_BUCKETS:
        return value  # exact, no bucketing at all down here
    exponent = value.bit_length() - 1
    shift = exponent - PRECISION_BITS
    sub = (value >> shift) - SUB_BUCKETS
    return (shift + 1) * SUB_BUCKETS + sub


def _upper_edge(index: int) -> int:
    """Largest value that lands in `index`. Reported as the bucket's value."""
    if index < SUB_BUCKETS:
        return index
    shift = index // SUB_BUCKETS - 1
    sub = index % SUB_BUCKETS
    low = (SUB_BUCKETS + sub) << shift
    return low + (1 << shift) - 1


@dataclass
class Histogram:
    """Counts observations in microseconds. Sparse — only occupied buckets exist.

    Microseconds, not seconds, because the unit must be an integer: a float
    bucket key reintroduces the rounding this structure exists to bound. One
    microsecond of resolution is finer than anything worth measuring here and
    still leaves room for a 24-hour observation inside a machine word.
    """

    name: str = "latency"
    buckets: dict[int, int] = field(default_factory=dict)
    count: int = 0
    total: int = 0
    min_value: int | None = None
    max_value: int | None = None

    def observe_units(self, value: int) -> None:
        """Count one observation of a non-negative integer quantity.

        Generic on purpose: the same structure answers "p95 latency" and "p95
        cost per request" (in pico-dollars), and a cost distribution is just as
        long-tailed as a latency one — a handful of requests carry most of the
        spend, and the mean hides them.
        """
        if value < 0:
            # A negative duration means someone measured with a wall clock that
            # jumped. Refuse it rather than let it distort the tail.
            raise ValueError(f"negative observation: {value} — measure with a monotonic clock")
        idx = _index_of(value)
        self.buckets[idx] = self.buckets.get(idx, 0) + 1
        self.count += 1
        self.total += value
        self.min_value = value if self.min_value is None else min(self.min_value, value)
        self.max_value = value if self.max_value is None else max(self.max_value, value)

    def observe_micros(self, micros: int) -> None:
        self.observe_units(micros)

    def observe_seconds(self, seconds: float) -> None:
        self.observe_units(round(seconds * 1_000_000))

    def percentile_units(self, q: float) -> int | None:
        """The q-th percentile in whatever unit was observed."""
        return self.percentile_micros(q)

    def percentile(self, q: float) -> float | None:
        """The q-th percentile in SECONDS, or None when nothing was observed.

        Returns seconds because that is what an SLO is written in, while the
        internals stay in integer microseconds.
        """
        micros = self.percentile_micros(q)
        return None if micros is None else micros / 1_000_000

    def percentile_micros(self, q: float) -> int | None:
        if not 0 < q <= 100:
            raise ValueError("percentile must be in (0, 100]")
        if self.count == 0:
            return None
        target = math.ceil(q / 100 * self.count)
        seen = 0
        for idx in sorted(self.buckets):
            seen += self.buckets[idx]
            if seen >= target:
                return _upper_edge(idx)
        return self.max_value

    @property
    def mean_seconds(self) -> float | None:
        """Exact, because the running total is kept alongside the buckets."""
        return None if self.count == 0 else (self.total / self.count) / 1_000_000

    def merge(self, other: Histogram) -> Histogram:
        """Combine two histograms exactly. This is how a fleet percentile is computed."""
        out = Histogram(name=self.name, buckets=dict(self.buckets))
        for idx, n in other.buckets.items():
            out.buckets[idx] = out.buckets.get(idx, 0) + n
        out.count = self.count + other.count
        out.total = self.total + other.total
        mins = [v for v in (self.min_value, other.min_value) if v is not None]
        maxs = [v for v in (self.max_value, other.max_value) if v is not None]
        out.min_value = min(mins) if mins else None
        out.max_value = max(maxs) if maxs else None
        return out

    def snapshot(self) -> dict[str, float | int | None]:
        return {
            "count": self.count,
            "mean_s": self.mean_seconds,
            "min_s": None if self.min_value is None else self.min_value / 1e6,
            "p50_s": self.percentile(50),
            "p95_s": self.percentile(95),
            "p99_s": self.percentile(99),
            "max_s": None if self.max_value is None else self.max_value / 1e6,
        }

    def cumulative_counts(self, boundaries_seconds: list[float]) -> list[tuple[float, int]]:
        """Cumulative counts at fixed boundaries, for Prometheus export.

        The internal resolution is ~1,600 buckets, which is far too many to
        publish as a Prometheus histogram — cardinality is charged per series.
        Export therefore re-buckets to a handful of conventional boundaries; the
        high-resolution copy stays in-process for the percentiles that matter.
        """
        out: list[tuple[float, int]] = []
        for edge in boundaries_seconds:
            edge_micros = int(edge * 1_000_000)
            running = sum(n for idx, n in self.buckets.items() if _upper_edge(idx) <= edge_micros)
            out.append((edge, running))
        return out
