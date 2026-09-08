"""Cost per request — attributed, distributed, and honest about caching.

"What did that cost?" is three different questions and most instrumentation only
answers the first.

*Total spend* is easy and nearly useless on its own: it tells you the bill, not
what to do about it.

*Cost per request* is the one that drives decisions, and it must be reported as
a DISTRIBUTION rather than a mean. Spend is long-tailed in the same way latency
is — a small number of requests with huge contexts or long agent loops carry
most of the bill — so the mean sits below almost every expensive request and
makes the tail invisible. A p99 cost of forty times the median is the normal
shape here, and it is exactly the signal that says "cap the context" or "put a
budget on the loop".

*Counterfactual spend* is the question nobody instruments and finance always
asks: what would this have cost without the cache, without the router, on the
expensive model throughout? Without a baseline recorded at the time, the saving
is unprovable after the fact — which is how cost work ends up sounding like a
claim instead of a number. So every event carries `undiscounted` alongside
`cost`, and the difference is reported rather than asserted.

All arithmetic is exact `Money`. See core/money.py for why that is not fussiness.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from ..core.money import Money
from .histogram import Histogram
from .trace import Trace

__all__ = ["CostBreakdown", "CostEvent", "CostLedger"]


@dataclass(frozen=True)
class CostEvent:
    """One billable unit of work, attributed to whoever should pay for it."""

    at: datetime
    trace_id: str
    model: str
    cost: Money
    #: What the same work would have cost at full price with no cache and no
    #: routing. Equal to `cost` when there was nothing to save.
    undiscounted: Money
    tenant_id: str = ""
    route: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cached_input_tokens: int = 0

    @property
    def saved(self) -> Money:
        return self.undiscounted - self.cost


@dataclass
class CostBreakdown:
    total: Money
    undiscounted: Money
    events: int

    @property
    def saved(self) -> Money:
        return self.undiscounted - self.total

    @property
    def saved_percent(self) -> float:
        if not self.undiscounted:
            return 0.0
        return 100.0 * self.saved.picos / self.undiscounted.picos

    def as_dict(self) -> dict[str, object]:
        return {
            "total": str(self.total),
            "undiscounted": str(self.undiscounted),
            "saved": str(self.saved),
            "saved_percent": round(self.saved_percent, 2),
            "events": self.events,
        }


class CostLedger:
    """Accumulates cost events and answers the three questions above.

    Deliberately not a database. It is the in-process aggregate that feeds
    metrics and dashboards; the durable record is the per-tenant usage table
    (P10) written on the request path, because an in-memory ledger loses the
    month's billing when a pod restarts.
    """

    def __init__(self) -> None:
        # One lock over every mutation, matching `obs/metrics.py`, which already
        # had one while this file — the ledger money actually lands in — did not.
        #
        # `self._total = self._total + event.cost` is read-modify-write on three
        # separate attributes plus five dictionaries. Two threads recording
        # concurrently lose an event silently: no exception, no gap in a
        # sequence, just a total that is lower than the sum of what happened.
        # Cost figures that are quietly low are worse than missing ones, because
        # they get believed.
        #
        # Coarse rather than per-field on purpose. A finer lock would let a
        # reader see `_events` incremented before `_total` moved, which is a
        # ledger that briefly disagrees with itself.
        self._lock = threading.Lock()
        self._total = Money.zero()
        self._undiscounted = Money.zero()
        self._events = 0
        self._by_model: dict[str, list[Money]] = defaultdict(list)
        self._by_tenant: dict[str, Money] = defaultdict(Money.zero)
        self._by_route: dict[str, Money] = defaultdict(Money.zero)
        self._undiscounted_by_model: dict[str, Money] = defaultdict(Money.zero)
        self._per_request = Histogram(name="cost_picodollars")
        self._per_request_by_trace: dict[str, Money] = defaultdict(Money.zero)
        self._tokens: dict[str, int] = defaultdict(int)

    def record(self, event: CostEvent) -> None:
        """One event, recorded atomically across every aggregate it touches."""
        with self._lock:
            self._total = self._total + event.cost
            self._undiscounted = self._undiscounted + event.undiscounted
            self._events += 1
            self._by_model[event.model].append(event.cost)
            self._undiscounted_by_model[event.model] = (
                self._undiscounted_by_model[event.model] + event.undiscounted
            )
            if event.tenant_id:
                self._by_tenant[event.tenant_id] = self._by_tenant[event.tenant_id] + event.cost
            if event.route:
                self._by_route[event.route] = self._by_route[event.route] + event.cost
            self._per_request_by_trace[event.trace_id] = (
                self._per_request_by_trace[event.trace_id] + event.cost
            )
            self._tokens["input"] += event.input_tokens
            self._tokens["output"] += event.output_tokens
            self._tokens["cached_input"] += event.cached_input_tokens

    def seal_request(self, trace_id: str) -> Money:
        """Close out one request and fold its total into the per-request distribution.

        Separate from `record` because a request is many events: folding each
        LLM call in individually would produce a "cost per request" distribution
        that is really a cost-per-call distribution, and an agent run that makes
        twelve cheap calls would look twelve times cheaper than a single
        expensive one it actually outspent.
        """
        with self._lock:
            total = self._per_request_by_trace.pop(trace_id, Money.zero())
            self._per_request.observe_units(total.picos)
        return total

    def record_trace(self, trace: Trace, tenant_id: str = "", route: str = "") -> Money:
        """Ingest a finished trace: one event per cost-bearing span, then seal."""
        for span in trace.spans:
            if not span.cost:
                continue
            undiscounted = Money.from_picos(
                int(span.attributes.get("undiscounted_picos", span.cost.picos))
            )
            self.record(
                CostEvent(
                    at=span.started_at,
                    trace_id=trace.trace_id,
                    model=str(span.attributes.get("model", "unknown")),
                    cost=span.cost,
                    undiscounted=undiscounted,
                    tenant_id=tenant_id,
                    route=route or trace.name,
                    input_tokens=span.input_tokens,
                    output_tokens=span.output_tokens,
                    cached_input_tokens=span.cached_input_tokens,
                )
            )
        return self.seal_request(trace.trace_id)

    # ── answers ───────────────────────────────────────────────────────────
    @property
    def overall(self) -> CostBreakdown:
        return CostBreakdown(self._total, self._undiscounted, self._events)

    def by_model(self) -> dict[str, CostBreakdown]:
        out: dict[str, CostBreakdown] = {}
        for model, costs in self._by_model.items():
            total = Money.zero()
            for c in costs:
                total = total + c
            out[model] = CostBreakdown(total, self._undiscounted_by_model[model], len(costs))
        return dict(sorted(out.items(), key=lambda kv: -kv[1].total.picos))

    def by_tenant(self) -> dict[str, Money]:
        return dict(sorted(self._by_tenant.items(), key=lambda kv: -kv[1].picos))

    def by_route(self) -> dict[str, Money]:
        return dict(sorted(self._by_route.items(), key=lambda kv: -kv[1].picos))

    def top_spenders(self, n: int = 5) -> list[tuple[str, Money]]:
        return list(self.by_tenant().items())[:n]

    def per_request(self) -> dict[str, Money | int | None]:
        """The distribution, not the mean. p99/p50 is the number worth watching."""
        pct = self._per_request

        def at(q: float) -> Money | None:
            units = pct.percentile_units(q)
            return None if units is None else Money.from_picos(units)

        return {
            "requests": pct.count,
            "mean": Money.from_picos(int(pct.total / pct.count)) if pct.count else None,
            "p50": at(50),
            "p95": at(95),
            "p99": at(99),
            "max": Money.from_picos(pct.max_value) if pct.max_value is not None else None,
        }

    def tail_ratio(self) -> float | None:
        """p99 divided by p50. Above ~10 means a few requests carry the bill."""
        p50 = self._per_request.percentile_units(50)
        p99 = self._per_request.percentile_units(99)
        if not p50 or p99 is None:
            return None
        return p99 / p50

    def tokens(self) -> dict[str, int]:
        return dict(self._tokens)

    def report(self) -> str:
        """A plain-text summary suitable for a CI comment or a terminal."""
        overall = self.overall
        lines = [
            f"spend {overall.total.format_adaptive()} over {overall.events} calls",
            f"  would have cost {overall.undiscounted.format_adaptive()} undiscounted "
            f"→ saved {overall.saved.format_adaptive()} ({overall.saved_percent:.1f}%)",
        ]
        dist = self.per_request()
        if dist["requests"]:
            ratio = self.tail_ratio()
            lines.append(
                f"  per request: p50 {dist['p50']} · p95 {dist['p95']} · p99 {dist['p99']}"
                + (f"  (p99/p50 = {ratio:.1f}×)" if ratio else "")
            )
        for model, breakdown in self.by_model().items():
            lines.append(
                f"  {model:<28} {breakdown.total.format_adaptive():>12}  ({breakdown.events} calls)"
            )
        return "\n".join(lines)
