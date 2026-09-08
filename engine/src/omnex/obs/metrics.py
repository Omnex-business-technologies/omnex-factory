"""Counters, gauges and timers, with a cardinality limit that actually bites.

The in-process registry is the default and needs no dependency, no scrape
target and no running Prometheus. That matters more than it sounds: it means
every test in this repo can assert on the metrics a code path emitted, so
"does this record a cost" and "does this count a retry as an error" are
regression-tested rather than eyeballed on a dashboard once.

**The cardinality cap is the most important thing in this file.** The classic
way to take down a metrics backend is a label whose value set is unbounded —
`tenant_id`, `trace_id`, `user_email`, or a raw error message. Each distinct
combination is a new time series stored forever; a few thousand tenants times a
few models times a few status values is millions of series, and the failure mode
is not a warning, it is the monitoring system dying at the moment you need it.

So a metric declares its label names up front, values are capped per metric, and
observations beyond the cap are folded into a single `__overflow__` series
rather than being dropped silently or admitted. Folding keeps the totals correct
— the sum over all series still equals reality — while refusing to mint new
series. `overflowed` is itself exposed, because a metric that quietly stopped
being broken down by model is a metric someone will misread.
"""

from __future__ import annotations

import threading
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal

from ..core.clock import Clock, SystemClock
from .histogram import Histogram

__all__ = [
    "DEFAULT_LATENCY_BUCKETS",
    "OVERFLOW",
    "Counter",
    "Gauge",
    "MetricsRegistry",
    "Timer",
]

OVERFLOW = "__overflow__"

#: Conventional latency boundaries in seconds, spanning a cache hit to a timeout.
DEFAULT_LATENCY_BUCKETS = [
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
    30.0,
    60.0,
]

Labels = tuple[tuple[str, str], ...]


def _normalise(label_names: tuple[str, ...], labels: dict[str, str] | None) -> Labels:
    labels = labels or {}
    unknown = set(labels) - set(label_names)
    if unknown:
        # Declared up front so a typo cannot silently create a parallel series
        # that looks like the real metric but holds a fraction of the traffic.
        raise ValueError(f"undeclared labels {sorted(unknown)}; declared: {list(label_names)}")
    return tuple((name, str(labels.get(name, ""))) for name in label_names)


class _Series:
    """Shared cardinality bookkeeping for one metric."""

    def __init__(self, name: str, label_names: tuple[str, ...], max_series: int) -> None:
        self.name = name
        self.label_names = label_names
        self.max_series = max_series
        self.overflowed = 0
        self._lock = threading.Lock()

    def key(self, labels: dict[str, str] | None, known: Mapping[Labels, object]) -> Labels:
        k = _normalise(self.label_names, labels)
        if k in known or len(known) < self.max_series:
            return k
        with self._lock:
            self.overflowed += 1
        return tuple((name, OVERFLOW) for name in self.label_names)


@dataclass
class Counter:
    """Monotonically increasing count. Never decremented — that is what a gauge is for."""

    name: str
    help: str = ""
    label_names: tuple[str, ...] = ()
    max_series: int = 200
    values: dict[Labels, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._series = _Series(self.name, self.label_names, self.max_series)
        self._lock = threading.Lock()

    def inc(self, amount: float = 1.0, **labels: str) -> None:
        """Add to a series, staying EXACT while every increment is an integer.

        The accumulator starts at integer zero rather than `0.0`, which is the
        whole fix and is easy to miss. Python integers are arbitrary precision,
        so a counter fed only integers is exact forever; one that ever sees a
        float becomes a float and stays one, losing exactness above 2**53.

        That mattered here in the worst place. `trace.py` used to record cost as
        `float(span.cost.picos)`, and 2**53 picos is $9,007.20 — a cumulative
        counter, so it was not a question of whether it would arrive. A cost
        number that silently stops being exact is the failure `core/money.py`
        exists to prevent, and it had reappeared in the metrics export where
        nobody looks.

        The honest limit: what Prometheus's own storage does with the value
        afterwards is float64 and outside this process. This stops us
        MANUFACTURING the loss; it cannot stop theirs.
        """
        if amount < 0:
            raise ValueError("a counter cannot decrease")
        key = self._series.key(labels, self.values)
        with self._lock:
            self.values[key] = self.values.get(key, 0) + amount

    def value(self, **labels: str) -> float:
        return self.values.get(_normalise(self.label_names, labels), 0)

    @property
    def total(self) -> float:
        """Correct even after overflow, which is the reason overflow folds rather than drops."""
        return sum(self.values.values())

    @property
    def overflowed(self) -> int:
        return self._series.overflowed


@dataclass
class Gauge:
    """A value that goes up and down — queue depth, active runs, budget remaining."""

    name: str
    help: str = ""
    label_names: tuple[str, ...] = ()
    max_series: int = 200
    values: dict[Labels, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._series = _Series(self.name, self.label_names, self.max_series)
        self._lock = threading.Lock()

    def set(self, value: float, **labels: str) -> None:
        key = self._series.key(labels, self.values)
        with self._lock:
            self.values[key] = value

    def inc(self, amount: float = 1.0, **labels: str) -> None:
        key = self._series.key(labels, self.values)
        with self._lock:
            self.values[key] = self.values.get(key, 0.0) + amount

    def dec(self, amount: float = 1.0, **labels: str) -> None:
        self.inc(-amount, **labels)

    def value(self, **labels: str) -> float:
        return self.values.get(_normalise(self.label_names, labels), 0.0)

    @property
    def overflowed(self) -> int:
        return self._series.overflowed


@dataclass
class Timer:
    """A named family of latency histograms.

    Used as a context manager. It records on the way out even when the body
    raised, because the latency of a failure is the number you most want during
    an incident — a p99 computed only from successes hides exactly the requests
    that are hurting, and it is what makes a dashboard look calm while users
    are timing out.
    """

    name: str
    help: str = ""
    label_names: tuple[str, ...] = ()
    max_series: int = 200
    histograms: dict[Labels, Histogram] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._series = _Series(self.name, self.label_names, self.max_series)
        self._lock = threading.Lock()

    def observe(self, seconds: float, **labels: str) -> None:
        key = self._series.key(labels, self.histograms)
        with self._lock:
            hist = self.histograms.get(key)
            if hist is None:
                hist = Histogram(name=self.name)
                self.histograms[key] = hist
        hist.observe_seconds(seconds)

    def histogram(self, **labels: str) -> Histogram:
        return self.histograms.get(_normalise(self.label_names, labels), Histogram(name=self.name))

    def merged(self) -> Histogram:
        """Fleet view across every label combination — by merging, never by averaging."""
        out = Histogram(name=self.name)
        for hist in self.histograms.values():
            out = out.merge(hist)
        return out

    def time(self, clock: Clock | None = None, **labels: str) -> _TimerContext:
        return _TimerContext(self, clock or SystemClock(), labels)

    @property
    def overflowed(self) -> int:
        return self._series.overflowed


class _TimerContext:
    __slots__ = ("_clock", "_labels", "_start", "_timer", "seconds")

    def __init__(self, timer: Timer, clock: Clock, labels: dict[str, str]) -> None:
        self._timer = timer
        self._clock = clock
        self._labels = labels
        self._start = 0.0
        self.seconds = 0.0

    def __enter__(self) -> _TimerContext:
        self._start = self._clock.monotonic()
        return self

    def __exit__(self, *exc: object) -> Literal[False]:
        self.seconds = self._clock.monotonic() - self._start
        self._timer.observe(self.seconds, **self._labels)
        return False  # never swallow the exception


class MetricsRegistry:
    """Holds every metric and renders them in Prometheus text exposition format."""

    def __init__(self) -> None:
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, Gauge] = {}
        self._timers: dict[str, Timer] = {}
        self._lock = threading.Lock()

    def counter(
        self, name: str, help: str = "", labels: tuple[str, ...] = (), max_series: int = 200
    ) -> Counter:
        with self._lock:
            existing = self._counters.get(name)
            if existing is None:
                existing = Counter(name, help, labels, max_series)
                self._counters[name] = existing
            elif existing.label_names != labels:
                # Two call sites disagreeing about a metric's labels produces
                # series that cannot be summed. Fail at registration.
                raise ValueError(
                    f"metric {name!r} already registered with labels {existing.label_names}"
                )
            return existing

    def gauge(
        self, name: str, help: str = "", labels: tuple[str, ...] = (), max_series: int = 200
    ) -> Gauge:
        with self._lock:
            existing = self._gauges.get(name)
            if existing is None:
                existing = Gauge(name, help, labels, max_series)
                self._gauges[name] = existing
            elif existing.label_names != labels:
                raise ValueError(f"metric {name!r} already registered with different labels")
            return existing

    def timer(
        self, name: str, help: str = "", labels: tuple[str, ...] = (), max_series: int = 200
    ) -> Timer:
        with self._lock:
            existing = self._timers.get(name)
            if existing is None:
                existing = Timer(name, help, labels, max_series)
                self._timers[name] = existing
            elif existing.label_names != labels:
                raise ValueError(f"metric {name!r} already registered with different labels")
            return existing

    # ── exposition ────────────────────────────────────────────────────────
    @staticmethod
    def _render_labels(labels: Labels) -> str:
        if not labels:
            return ""
        inner = ",".join(f'{k}="{_escape(v)}"' for k, v in labels)
        return "{" + inner + "}"

    def render(self, latency_buckets: list[float] | None = None) -> str:
        """Prometheus text exposition (version 0.0.4)."""
        buckets = latency_buckets or DEFAULT_LATENCY_BUCKETS
        lines: list[str] = []

        for counter in sorted(self._counters.values(), key=lambda c: c.name):
            if counter.help:
                lines.append(f"# HELP {counter.name} {counter.help}")
            lines.append(f"# TYPE {counter.name} counter")
            for key, value in sorted(counter.values.items()):
                lines.append(f"{counter.name}{self._render_labels(key)} {_num(value)}")

        for gauge in sorted(self._gauges.values(), key=lambda g: g.name):
            if gauge.help:
                lines.append(f"# HELP {gauge.name} {gauge.help}")
            lines.append(f"# TYPE {gauge.name} gauge")
            for key, value in sorted(gauge.values.items()):
                lines.append(f"{gauge.name}{self._render_labels(key)} {_num(value)}")

        for timer in sorted(self._timers.values(), key=lambda t: t.name):
            if timer.help:
                lines.append(f"# HELP {timer.name} {timer.help}")
            lines.append(f"# TYPE {timer.name} histogram")
            for key, hist in sorted(timer.histograms.items()):
                base = self._render_labels(key)
                for edge, cumulative in hist.cumulative_counts(buckets):
                    le = self._render_labels((*key, ("le", _num(edge))))
                    lines.append(f"{timer.name}_bucket{le} {cumulative}")
                inf = self._render_labels((*key, ("le", "+Inf")))
                lines.append(f"{timer.name}_bucket{inf} {hist.count}")
                lines.append(f"{timer.name}_sum{base} {_num(hist.total / 1_000_000)}")
                lines.append(f"{timer.name}_count{base} {hist.count}")

        # A metric that silently stopped being broken down is worse than one
        # that never was, so overflow is published rather than logged.
        overflow_lines = []
        every_metric: list[Counter | Gauge | Timer] = [
            *self._counters.values(),
            *self._gauges.values(),
            *self._timers.values(),
        ]
        for metric in every_metric:
            n = metric.overflowed
            if n:
                overflow_lines.append(f'omnex_metric_overflow_total{{metric="{metric.name}"}} {n}')
        if overflow_lines:
            lines.append(
                "# HELP omnex_metric_overflow_total Observations folded into __overflow__ by the cardinality cap"
            )
            lines.append("# TYPE omnex_metric_overflow_total counter")
            lines.extend(sorted(overflow_lines))

        return "\n".join(lines) + "\n"


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _num(value: float) -> str:
    """Render a metric value without inventing or losing digits.

    The `< 1e15` guard is about FLOATS, where `int(value)` past that point is
    already a rounded number and printing it as an integer would assert a
    precision nobody has. A genuine `int` falls through to `repr`, which prints
    every digit exactly — which is what a pico-dollar counter needs, and why
    `Counter.inc` keeps integer series integral.
    """
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    return repr(value)
