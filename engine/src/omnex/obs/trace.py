"""Distributed tracing: a span tree that keeps the shape of a run.

A flat list of log lines tells you what happened. It does not tell you that the
rerank step ran three times because the retrieval above it returned nothing, or
that 80% of a request's cost went to one fact-check retry buried four levels
down. Those are structural questions, and they need the parent links.

Three things here go beyond the usual span implementation, each for a reason
that shows up in production rather than in a demo.

**Cost is a first-class span field, and only leaves carry it.** Every span
records the money *it* spent, never the sum of its children. `Trace.total_cost`
then sums all spans and cannot double count, while `subtree_cost()` gives the
roll-up for display. The alternative — parents aggregating as they go — produces
a total that is correct only if every intermediate node remembered to not add,
which is a rule nobody keeps.

**Sampling is tail-based.** Head sampling decides at the first span, when the
only thing known is that a request started, so it keeps a uniform 1% — which is
1% of the errors, and the one trace you need during an incident is almost
certainly in the 99% that was thrown away. `TailSampler` buffers a trace in
memory and decides when it ends, so every error, every unusually slow run and
every unusually expensive one is kept, plus a random floor of ordinary traffic
for baselines.

**`failure_path()` returns the branch, not the tree.** During an incident the
question is "where did this actually break", and a 200-span dump does not answer
it. The failing path from root to deepest error usually does, in six lines.

Parenting uses `contextvars`, so it is correct under `asyncio` — a plain
module-level "current span" is shared between concurrently running coroutines
and reparents spans into whichever task happened to run last.
"""

from __future__ import annotations

import contextvars
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from random import Random
from typing import Any, Literal

from ..core.clock import Clock, SystemClock
from ..core.errors import OmnexError
from ..core.ids import IdFactory
from ..core.money import Money
from .metrics import MetricsRegistry

__all__ = ["Span", "SpanKind", "TailSampler", "Trace", "Tracer", "current_span_id"]

SpanKind = Literal["run", "llm", "retrieval", "rerank", "tool", "agent", "guard", "internal"]
Status = Literal["running", "ok", "error"]

_current_span: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "omnex_current_span", default=None
)
_current_trace: contextvars.ContextVar[Trace | None] = contextvars.ContextVar(
    "omnex_current_trace", default=None
)


def current_span_id() -> str | None:
    return _current_span.get()


@dataclass
class Span:
    span_id: str
    trace_id: str
    parent_id: str | None
    name: str
    kind: SpanKind
    started_at: datetime
    start_mono: float
    end_mono: float | None = None
    status: Status = "running"
    error: dict[str, Any] | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    #: Money spent *directly* by this span. Parents must leave this at zero.
    cost: Money = field(default_factory=Money.zero)
    input_tokens: int = 0
    output_tokens: int = 0
    cached_input_tokens: int = 0

    @property
    def duration_seconds(self) -> float | None:
        return None if self.end_mono is None else self.end_mono - self.start_mono

    def set(self, **attributes: Any) -> None:
        self.attributes.update(attributes)

    def record_usage(
        self,
        cost: Money,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cached_input_tokens: int = 0,
    ) -> None:
        self.cost = self.cost + cost
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.cached_input_tokens += cached_input_tokens

    def to_dict(self) -> dict[str, Any]:
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "kind": self.kind,
            "started_at": self.started_at.isoformat(),
            "duration_s": self.duration_seconds,
            "status": self.status,
            "error": self.error,
            "attributes": self.attributes,
            "cost_picos": self.cost.picos,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cached_input_tokens": self.cached_input_tokens,
        }


@dataclass
class Trace:
    trace_id: str
    name: str
    spans: list[Span] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)

    # ── structure ─────────────────────────────────────────────────────────
    @property
    def root(self) -> Span | None:
        return next((s for s in self.spans if s.parent_id is None), None)

    def by_id(self, span_id: str) -> Span | None:
        return next((s for s in self.spans if s.span_id == span_id), None)

    def children_of(self, span_id: str | None) -> list[Span]:
        return [s for s in self.spans if s.parent_id == span_id]

    # ── totals, computed from the spans rather than tallied as we go ──────
    @property
    def total_cost(self) -> Money:
        total = Money.zero()
        for span in self.spans:
            total = total + span.cost
        return total

    def subtree_cost(self, span_id: str) -> Money:
        span = self.by_id(span_id)
        if span is None:
            return Money.zero()
        total = span.cost
        for child in self.children_of(span_id):
            total = total + self.subtree_cost(child.span_id)
        return total

    @property
    def total_tokens(self) -> dict[str, int]:
        return {
            "input": sum(s.input_tokens for s in self.spans),
            "output": sum(s.output_tokens for s in self.spans),
            "cached_input": sum(s.cached_input_tokens for s in self.spans),
        }

    @property
    def duration_seconds(self) -> float | None:
        root = self.root
        return None if root is None else root.duration_seconds

    @property
    def failed(self) -> bool:
        return any(s.status == "error" for s in self.spans)

    def failure_path(self) -> list[Span]:
        """Root → deepest failing span. The branch that broke, not the whole tree."""
        failing = [s for s in self.spans if s.status == "error"]
        if not failing:
            return []
        deepest = max(failing, key=lambda s: self._depth(s))
        path: list[Span] = []
        cursor: Span | None = deepest
        while cursor is not None:
            path.append(cursor)
            cursor = self.by_id(cursor.parent_id) if cursor.parent_id else None
        return list(reversed(path))

    def _depth(self, span: Span) -> int:
        depth = 0
        cursor = span
        while cursor.parent_id:
            parent = self.by_id(cursor.parent_id)
            if parent is None:
                break
            cursor = parent
            depth += 1
        return depth

    # ── rendering ─────────────────────────────────────────────────────────
    def render(self, cost_threshold: Money | None = None) -> str:
        """An ASCII tree for a terminal. The fastest way to read a run.

        Spans above `cost_threshold` are marked, because "which step spent the
        money" is the question that gets asked about every expensive request.
        """
        lines: list[str] = [f"trace {self.trace_id}  {self.name}"]
        root = self.root
        if root is not None:
            self._render_into(lines, root, prefix="", last=True, threshold=cost_threshold)
        tokens = self.total_tokens
        lines.append(
            f"  total {self.total_cost.format_adaptive()}  "
            f"{tokens['input']}in/{tokens['output']}out tokens  "
            f"{len(self.spans)} spans"
        )
        return "\n".join(lines)

    def _render_into(
        self, lines: list[str], span: Span, prefix: str, last: bool, threshold: Money | None
    ) -> None:
        elbow = "└─ " if last else "├─ "
        dur = "" if span.duration_seconds is None else f" {span.duration_seconds * 1000:.0f}ms"
        mark = {"ok": "", "error": " ✗", "running": " …"}[span.status]
        money = ""
        if span.cost:
            money = f" {span.cost.format_adaptive()}"
            if threshold is not None and span.cost > threshold:
                money += " ←"
        lines.append(f"  {prefix}{elbow}{span.name} [{span.kind}]{dur}{money}{mark}")
        children = self.children_of(span.span_id)
        child_prefix = prefix + ("   " if last else "│  ")
        for i, child in enumerate(children):
            self._render_into(lines, child, child_prefix, i == len(children) - 1, threshold)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "name": self.name,
            "duration_s": self.duration_seconds,
            "failed": self.failed,
            "total_cost_picos": self.total_cost.picos,
            "total_tokens": self.total_tokens,
            "attributes": self.attributes,
            "spans": [s.to_dict() for s in self.spans],
        }


@dataclass
class TailSampler:
    """Decides at the END of a trace whether it is worth keeping.

    Head sampling keeps a uniform slice chosen before anything is known, which
    keeps 1% of errors. These rules keep everything that is interesting and a
    floor of what is not — the floor matters, because a store containing only
    failures makes every latency comparison meaningless.
    """

    error_always: bool = True
    slow_threshold_seconds: float = 5.0
    expensive_threshold: Money = field(default_factory=lambda: Money.from_usd("0.01"))
    #: Fraction of ordinary traces kept for baselines.
    baseline_rate: float = 0.05
    rng: Random = field(default_factory=Random)

    def keep(self, trace: Trace) -> tuple[bool, str]:
        if self.error_always and trace.failed:
            return True, "error"
        duration = trace.duration_seconds
        if duration is not None and duration >= self.slow_threshold_seconds:
            return True, "slow"
        if trace.total_cost >= self.expensive_threshold:
            return True, "expensive"
        if self.rng.random() < self.baseline_rate:
            return True, "baseline"
        return False, "sampled_out"


class Tracer:
    """Creates traces and spans, and wires them into metrics.

    Every finished span records its latency and outcome into the registry, so
    the dashboard's error rate and latency percentiles are a by-product of
    tracing rather than a second, separately-maintained instrumentation pass
    that drifts out of sync with the first.
    """

    def __init__(
        self,
        clock: Clock | None = None,
        ids: IdFactory | None = None,
        registry: MetricsRegistry | None = None,
        sampler: TailSampler | None = None,
        service: str = "omnex-engine",
    ) -> None:
        self.clock = clock or SystemClock()
        self.ids = ids or IdFactory(clock=self.clock)
        self.registry = registry or MetricsRegistry()
        self.sampler = sampler or TailSampler()
        self.service = service
        #: Traces the sampler decided to keep. Bounded by the caller in production.
        self.kept: list[Trace] = []

        self._latency = self.registry.timer(
            "omnex_span_duration_seconds",
            "Span wall-clock duration",
            labels=("kind", "name", "status"),
        )
        self._spans = self.registry.counter(
            "omnex_spans_total", "Spans completed", labels=("kind", "status")
        )
        self._errors = self.registry.counter(
            "omnex_errors_total", "Span failures by error code", labels=("kind", "code")
        )
        self._cost = self.registry.counter(
            "omnex_cost_picodollars_total",
            "Spend in pico-dollars (1e-12 USD), summed exactly",
            labels=("kind", "model"),
        )
        self._tokens = self.registry.counter(
            "omnex_tokens_total", "Tokens by direction", labels=("model", "direction")
        )

    @contextmanager
    def trace(self, name: str, **attributes: Any) -> Iterator[Trace]:
        """Open a trace. The root span shares its lifetime."""
        trace = Trace(trace_id=self.ids.new("trace"), name=name, attributes=dict(attributes))
        token = _current_trace.set(trace)
        try:
            with self.span(name, kind="run", **attributes):
                yield trace
        finally:
            _current_trace.reset(token)
            keep, reason = self.sampler.keep(trace)
            trace.attributes["sampling"] = reason
            if keep:
                self.kept.append(trace)

    @contextmanager
    def span(self, name: str, kind: SpanKind = "internal", **attributes: Any) -> Iterator[Span]:
        trace = _current_trace.get()
        if trace is None:
            raise RuntimeError("span() outside a trace() — open a trace first")
        span = Span(
            span_id=self.ids.new("span"),
            trace_id=trace.trace_id,
            parent_id=_current_span.get(),
            name=name,
            kind=kind,
            started_at=self.clock.now(),
            start_mono=self.clock.monotonic(),
            attributes=dict(attributes),
        )
        trace.spans.append(span)
        token = _current_span.set(span.span_id)
        try:
            yield span
        except BaseException as exc:
            span.status = "error"
            span.error = (
                exc.as_dict()
                if isinstance(exc, OmnexError)
                else {"code": type(exc).__name__, "message": str(exc), "retryable": False}
            )
            raise
        else:
            if span.status == "running":
                span.status = "ok"
        finally:
            _current_span.reset(token)
            span.end_mono = self.clock.monotonic()
            self._record(span)

    def _record(self, span: Span) -> None:
        duration = span.duration_seconds or 0.0
        self._latency.observe(duration, kind=span.kind, name=span.name, status=span.status)
        self._spans.inc(kind=span.kind, status=span.status)
        if span.status == "error":
            code = (span.error or {}).get("code", "unknown")
            self._errors.inc(kind=span.kind, code=str(code))
        model = str(span.attributes.get("model", ""))
        if span.cost:
            # Picos as an integer, never `float(...)`. The cast that used to be
            # here turned an exact amount into a float64 accumulator, and the
            # cost counter is cumulative: past 2**53 picos — $9,007.20 — it
            # stops being the number it reports.
            self._cost.inc(span.cost.picos, kind=span.kind, model=model)
        if span.input_tokens:
            self._tokens.inc(span.input_tokens, model=model, direction="input")
        if span.output_tokens:
            self._tokens.inc(span.output_tokens, model=model, direction="output")
        if span.cached_input_tokens:
            self._tokens.inc(span.cached_input_tokens, model=model, direction="cached_input")
