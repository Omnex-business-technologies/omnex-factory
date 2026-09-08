"""Export paths, and a check that the deployed dashboards match the emitted metrics."""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path
from random import Random

import pytest

from omnex.core import ConfigurationError, FakeClock, IdFactory, Money
from omnex.obs import Tracer
from omnex.obs.export import (
    PROMETHEUS_CONTENT_TYPE,
    OtlpTraceExporter,
    serve_metrics,
    traces_to_jsonl,
)

DEPLOY = Path(__file__).resolve().parents[2] / "deploy" / "observability"


def _tracer() -> tuple[Tracer, FakeClock]:
    clock = FakeClock()
    return Tracer(clock=clock, ids=IdFactory(clock=clock, rng=Random(1))), clock


# ── JSONL export ──────────────────────────────────────────────────────────


def test_jsonl_export_round_trips_the_span_tree():
    tracer, clock = _tracer()
    with tracer.trace("answer") as trace:
        with tracer.span("retrieve", kind="retrieval"):
            clock.advance(0.05)
        with tracer.span("generate", kind="llm", model="sonnet") as span:
            clock.advance(0.3)
            span.record_usage(Money.from_usd("0.0021"), input_tokens=900, output_tokens=210)

    line = traces_to_jsonl([trace])
    assert "\n" not in line  # one trace, one line — greppable
    restored = json.loads(line)
    assert restored["trace_id"] == trace.trace_id
    assert len(restored["spans"]) == 3
    assert restored["total_cost_picos"] == Money.from_usd("0.0021").picos
    parents = {s["name"]: s["parent_id"] for s in restored["spans"]}
    root_id = next(s["span_id"] for s in restored["spans"] if s["parent_id"] is None)
    assert parents["retrieve"] == root_id and parents["generate"] == root_id


def test_exported_cost_is_an_integer_of_picos_not_a_float():
    """The one place money could lose precision is the copy people build dashboards from."""
    tracer, _ = _tracer()
    with tracer.trace("run") as trace, tracer.span("call", kind="llm") as span:
        span.record_usage(Money.from_usd("0.000000000001"))  # one pico

    payload = json.loads(traces_to_jsonl([trace]))
    costs = [s["cost_picos"] for s in payload["spans"]]
    assert all(isinstance(c, int) for c in costs)
    assert max(costs) == 1  # survives export; a float would round it away
    assert "1e-12" not in json.dumps(payload)


# ── OTLP adapter ──────────────────────────────────────────────────────────


def test_otlp_exporter_refuses_to_be_built_without_an_endpoint():
    with pytest.raises(ConfigurationError, match="endpoint"):
        OtlpTraceExporter(endpoint="")


def test_otlp_id_mapping_is_deterministic_and_never_zero():
    """A trace found in Grafana must be findable by its omnex id in the audit trail."""
    a = OtlpTraceExporter._otel_id("trace_01JQABCDEFGHJKMNPQRSTVWXYZ", 16)
    b = OtlpTraceExporter._otel_id("trace_01JQABCDEFGHJKMNPQRSTVWXYZ", 16)
    c = OtlpTraceExporter._otel_id("trace_01JQABCDEFGHJKMNPQRSTVWXY0", 16)
    assert a == b and a != c
    assert 0 < a < 2**128


def test_otlp_export_states_the_missing_extra_rather_than_failing_obscurely():
    try:
        import opentelemetry.sdk.trace  # noqa: F401
    except ImportError:
        with pytest.raises(ConfigurationError, match="otel"):
            OtlpTraceExporter(endpoint="http://localhost:4318")._ensure_provider()
    else:  # pragma: no cover - only when the extra is installed
        pytest.skip("opentelemetry installed; the missing-extra path cannot be exercised")


def test_span_attributes_flattened_for_otel_keep_cost_as_a_string():
    payload = {
        "span_id": "span_1",
        "trace_id": "trace_1",
        "kind": "llm",
        "cost_picos": 2_100_000_000,
        "input_tokens": 900,
        "output_tokens": 210,
        "cached_input_tokens": 0,
        "attributes": {"model": "sonnet", "sources": ["a", "b"]},
    }
    flat = OtlpTraceExporter._attributes(payload)
    assert flat["omnex.cost_picodollars"] == 2_100_000_000
    assert isinstance(flat["omnex.cost_usd"], str)
    assert flat["omnex.cost_usd"].startswith("0.0021")
    assert flat["omnex.attr.model"] == "sonnet"
    assert flat["omnex.attr.sources"] == '["a", "b"]'  # non-scalars survive as JSON


# ── Scrape endpoint ───────────────────────────────────────────────────────


def test_metrics_endpoint_serves_prometheus_text():
    tracer, clock = _tracer()
    with tracer.trace("run"), tracer.span("call", kind="llm", model="haiku") as span:
        clock.advance(0.2)
        span.record_usage(Money.from_usd("0.0004"), input_tokens=500, output_tokens=100)

    server = serve_metrics(tracer.registry, port=0)
    try:
        port = server.server_address[1]
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/metrics", timeout=5) as resp:
            assert resp.status == 200
            assert resp.headers["Content-Type"] == PROMETHEUS_CONTENT_TYPE
            body = resp.read().decode()
        assert "omnex_spans_total" in body
        assert "omnex_cost_picodollars_total" in body
        assert "omnex_span_duration_seconds_bucket" in body

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=5) as resp:
            assert resp.read() == b"ok"
    finally:
        server.shutdown()
        server.server_close()


# ── The dashboards must match the code ────────────────────────────────────


def _emitted_metric_names() -> set[str]:
    tracer, _ = _tracer()
    reg = tracer.registry
    names = set()
    for counter in reg._counters.values():
        names.add(counter.name)
    for gauge in reg._gauges.values():
        names.add(gauge.name)
    for timer in reg._timers.values():
        names.update(
            {timer.name, f"{timer.name}_bucket", f"{timer.name}_sum", f"{timer.name}_count"}
        )
    # Synthesised inside render() rather than registered, because it is a
    # property of the registry itself rather than of any one metric.
    names.add("omnex_metric_overflow_total")
    return names


def _referenced_metric_names(text: str) -> set[str]:
    return set(re.findall(r"\bomnex_[a-z0-9_]+", text))


@pytest.mark.parametrize("filename", ["prometheus-rules.yml", "grafana-dashboard.json"])
def test_deployed_queries_only_reference_metrics_the_code_emits(filename: str):
    """The classic silent rot: a renamed metric leaves a dashboard reading 'No data'.

    Nothing fails, nothing alerts, and the panel is trusted until an incident
    proves it has been blank for months. This test turns that into a build error.
    """
    path = DEPLOY / filename
    assert path.exists(), f"missing deploy artefact: {path}"
    referenced = _referenced_metric_names(path.read_text())
    assert referenced, "expected the artefact to query omnex metrics"
    unknown = referenced - _emitted_metric_names()
    assert not unknown, f"{filename} queries metrics the engine does not emit: {sorted(unknown)}"


def test_every_alert_rule_has_a_sustain_window():
    """A rule that fires on one scrape fires on one slow request, and gets muted."""
    text = (DEPLOY / "prometheus-rules.yml").read_text()
    alerts = re.findall(r"- alert: (\w+)(.*?)(?=\n      - alert:|\Z)", text, re.S)
    assert len(alerts) >= 5
    for name, body in alerts:
        assert re.search(r"^\s+for:\s", body, re.M), f"{name} fires without a sustain window"
        assert re.search(r"severity:\s*(page|ticket|info)", body), f"{name} has no severity"


def test_dashboard_is_valid_json_and_pins_its_uid():
    dashboard = json.loads((DEPLOY / "grafana-dashboard.json").read_text())
    assert dashboard["uid"] == "omnex-engine"  # stable, so links do not rot
    titles = [p["title"] for p in dashboard["panels"]]
    assert "Cost per request" in titles
    assert "Run latency percentiles" in titles
    # Percentiles must come from bucket rates, never from a pre-averaged series.
    for panel in dashboard["panels"]:
        for target in panel.get("targets", []):
            if "p95" in target.get("legendFormat", "") or "p99" in target.get("legendFormat", ""):
                assert "histogram_quantile" in target["expr"]
