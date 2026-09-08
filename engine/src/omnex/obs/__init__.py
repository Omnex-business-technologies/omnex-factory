"""P5 — observability. Tracing, cost, latency, error rates and alerting.

Built before anything else in the engine, because instrumentation added
afterwards instruments what you remember rather than what happens, and because
every claim the other seventeen systems make about cost or latency is measured
through this module rather than asserted.

The whole layer runs in-process with no dependencies. OpenTelemetry and
Prometheus are export adapters (`otel.py`), not the source of truth — so a test
can assert on the exact spans and money a code path produced without a
collector, a scrape endpoint, or a container.
"""

from .anomaly import Alert, AlertManager, AlertRule, RobustBaseline, Severity
from .cost import CostBreakdown, CostEvent, CostLedger
from .histogram import Histogram
from .metrics import DEFAULT_LATENCY_BUCKETS, Counter, Gauge, MetricsRegistry, Timer
from .trace import Span, TailSampler, Trace, Tracer, current_span_id

__all__ = [
    "DEFAULT_LATENCY_BUCKETS",
    "Alert",
    "AlertManager",
    "AlertRule",
    "CostBreakdown",
    "CostEvent",
    "CostLedger",
    "Counter",
    "Gauge",
    "Histogram",
    "MetricsRegistry",
    "RobustBaseline",
    "Severity",
    "Span",
    "TailSampler",
    "Timer",
    "Trace",
    "Tracer",
    "current_span_id",
]
