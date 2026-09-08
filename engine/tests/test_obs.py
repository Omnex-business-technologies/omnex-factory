"""Tests for P5. These are the assertions the other seventeen systems rely on."""

from __future__ import annotations

import asyncio
import statistics
from random import Random

import pytest

from omnex.core import FakeClock, IdFactory, Money, TransientError
from omnex.obs import (
    AlertManager,
    AlertRule,
    CostEvent,
    CostLedger,
    Histogram,
    MetricsRegistry,
    RobustBaseline,
    Severity,
    TailSampler,
    Tracer,
)
from omnex.obs.histogram import RELATIVE_ERROR
from omnex.obs.metrics import OVERFLOW

# ── Histogram ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "micros", [1, 63, 64, 100, 999, 1_000, 12_345, 1_000_000, 45_678_901, 90_000_000]
)
def test_reported_value_is_within_the_stated_error_bound(micros: int):
    """The 1.6% bound is the contract; every percentile in this repo depends on it."""
    hist = Histogram()
    hist.observe_micros(micros)
    reported = hist.percentile_micros(100)
    assert reported is not None
    assert reported >= micros  # never under-reports a latency
    assert (reported - micros) / micros <= RELATIVE_ERROR


def test_small_values_are_counted_exactly():
    hist = Histogram()
    for v in range(64):
        hist.observe_micros(v)
    assert hist.percentile_micros(100) == 63
    assert hist.percentile_micros(50) == 31


def test_percentiles_match_an_exact_sort_within_the_bound():
    rng = Random(42)
    samples = [int(rng.lognormvariate(9, 1.4)) + 1 for _ in range(20_000)]
    hist = Histogram()
    for s in samples:
        hist.observe_micros(s)
    ordered = sorted(samples)
    for q in (50, 90, 95, 99, 99.9):
        exact = ordered[min(len(ordered) - 1, int(q / 100 * len(ordered)))]
        reported = hist.percentile_micros(q)
        assert reported is not None
        assert abs(reported - exact) / exact <= RELATIVE_ERROR * 2


def test_memory_stays_bounded_regardless_of_observation_count():
    hist = Histogram()
    rng = Random(1)
    for _ in range(200_000):
        hist.observe_micros(rng.randint(1, 90_000_000))
    assert hist.count == 200_000
    assert len(hist.buckets) < 2_000  # ~1,600 possible, not 200,000


def test_mean_is_exact_even_though_buckets_are_approximate():
    hist = Histogram()
    for v in (100, 200, 300):
        hist.observe_micros(v)
    assert hist.mean_seconds == pytest.approx(200 / 1e6)


def test_merging_beats_averaging_percentiles_in_both_directions():
    """Percentiles do not average. This is why fleet stats merge histograms.

    Two instances, each with a correct p95, and the average of those two p95s is
    wrong — too low in one arrangement of the same data, 50x too high in another.
    No arithmetic on the two summary numbers recovers the truth; only the
    histograms hold enough information.
    """
    fast, slow = Histogram(), Histogram()
    for _ in range(1000):
        fast.observe_micros(10_000)  # 10ms
    for _ in range(1000):
        slow.observe_micros(1_000_000)  # 1000ms

    averaged = statistics.fmean([fast.percentile(95), slow.percentile(95)])
    merged = fast.merge(slow).percentile(95)
    assert averaged == pytest.approx(0.505, rel=0.02)
    assert merged == pytest.approx(1.0, rel=RELATIVE_ERROR)  # truth: the slow half owns the tail

    # Same two instances, different traffic split: averaging now over-reports 50x.
    mostly_fast = Histogram()
    for _ in range(1900):
        mostly_fast.observe_micros(10_000)
    few_slow = Histogram()
    for _ in range(100):
        few_slow.observe_micros(1_000_000)
    averaged2 = statistics.fmean([mostly_fast.percentile(95), few_slow.percentile(95)])
    merged2 = mostly_fast.merge(few_slow).percentile(95)
    assert averaged2 == pytest.approx(0.505, rel=0.02)
    assert merged2 == pytest.approx(0.010, rel=RELATIVE_ERROR)
    assert averaged2 / merged2 > 40


def test_negative_durations_are_refused_not_absorbed():
    """A negative duration means a wall clock jumped; absorbing it corrupts the tail."""
    with pytest.raises(ValueError, match="negative"):
        Histogram().observe_micros(-5)


# ── Metrics and cardinality ───────────────────────────────────────────────


def test_undeclared_label_is_a_registration_error_not_a_new_series():
    reg = MetricsRegistry()
    counter = reg.counter("omnex_calls_total", labels=("model",))
    with pytest.raises(ValueError, match="undeclared"):
        counter.inc(modle="typo")


def test_cardinality_cap_folds_into_overflow_and_keeps_the_total_correct():
    """The classic way to kill a metrics backend is an unbounded label value."""
    reg = MetricsRegistry()
    counter = reg.counter("omnex_requests_total", labels=("tenant",), max_series=10)
    for i in range(5000):
        counter.inc(tenant=f"tenant-{i}")

    assert len(counter.values) == 11  # 10 real series plus one overflow
    assert counter.total == 5000  # nothing was dropped
    assert counter.values[(("tenant", OVERFLOW),)] == 4990
    assert counter.overflowed == 4990


def test_overflow_is_published_because_a_silently_flattened_metric_misleads():
    reg = MetricsRegistry()
    counter = reg.counter("omnex_requests_total", labels=("tenant",), max_series=2)
    for i in range(10):
        counter.inc(tenant=f"t{i}")
    assert "omnex_metric_overflow_total" in reg.render()


def test_two_call_sites_disagreeing_about_labels_fail_at_registration():
    reg = MetricsRegistry()
    reg.counter("omnex_calls_total", labels=("model",))
    with pytest.raises(ValueError, match="already registered"):
        reg.counter("omnex_calls_total", labels=("model", "tenant"))


def test_timer_records_latency_even_when_the_body_raises():
    """A p99 built only from successes hides exactly the requests that hurt."""
    reg = MetricsRegistry()
    clock = FakeClock()
    timer = reg.timer("omnex_op_seconds", labels=("op",))

    with pytest.raises(TransientError), timer.time(clock, op="retrieve"):
        clock.advance(2.5)
        raise TransientError("upstream down")

    assert timer.histogram(op="retrieve").count == 1
    assert timer.histogram(op="retrieve").percentile(100) == pytest.approx(2.5, rel=RELATIVE_ERROR)


def test_prometheus_exposition_shape():
    reg = MetricsRegistry()
    reg.counter("omnex_calls_total", "Calls", labels=("model",)).inc(3, model="haiku")
    reg.gauge("omnex_queue_depth", "Queued", labels=()).set(7)
    clock = FakeClock()
    timer = reg.timer("omnex_op_seconds", "Op latency", labels=("op",))
    with timer.time(clock, op="rerank"):
        clock.advance(0.03)

    text = reg.render()
    assert "# TYPE omnex_calls_total counter" in text
    assert 'omnex_calls_total{model="haiku"} 3' in text
    assert "omnex_queue_depth 7" in text
    assert 'omnex_op_seconds_bucket{op="rerank",le="0.05"} 1' in text
    assert 'omnex_op_seconds_bucket{op="rerank",le="0.025"} 0' in text
    assert 'omnex_op_seconds_count{op="rerank"} 1' in text


def test_label_values_are_escaped():
    reg = MetricsRegistry()
    reg.counter("omnex_errors_total", labels=("message",)).inc(message='he said "no"\n')
    assert '\\"no\\"' in reg.render()


# ── Tracing ───────────────────────────────────────────────────────────────


def _tracer() -> tuple[Tracer, FakeClock]:
    clock = FakeClock()
    return Tracer(
        clock=clock,
        ids=IdFactory(clock=clock, rng=Random(1)),
        sampler=TailSampler(baseline_rate=1.0),
    ), clock


def test_spans_form_a_tree_with_correct_parents():
    tracer, clock = _tracer()
    with tracer.trace("answer") as trace:
        with tracer.span("retrieve", kind="retrieval"):
            clock.advance(0.05)
            with tracer.span("rerank", kind="rerank"):
                clock.advance(0.02)
        with tracer.span("generate", kind="llm"):
            clock.advance(0.4)

    root = trace.root
    assert root is not None and root.name == "answer"
    assert [s.name for s in trace.children_of(root.span_id)] == ["retrieve", "generate"]
    rerank = next(s for s in trace.spans if s.name == "rerank")
    retrieve = next(s for s in trace.spans if s.name == "retrieve")
    assert rerank.parent_id == retrieve.span_id
    assert trace.duration_seconds == pytest.approx(0.47)


def test_cost_is_not_double_counted_by_parents():
    """Parents never record cost; totals sum every span and still cannot overcount."""
    tracer, _ = _tracer()
    with tracer.trace("agent-run") as trace, tracer.span("supervisor", kind="agent"):
        for _ in range(3):
            with tracer.span("call", kind="llm", model="haiku") as span:
                span.record_usage(Money.from_usd("0.0004"), input_tokens=800, output_tokens=120)

    assert trace.total_cost == Money.from_usd("0.0012")
    supervisor = next(s for s in trace.spans if s.name == "supervisor")
    assert trace.subtree_cost(supervisor.span_id) == Money.from_usd("0.0012")
    assert supervisor.cost == Money.zero()
    assert trace.total_tokens == {"input": 2400, "output": 360, "cached_input": 0}


def test_failure_path_returns_the_branch_not_the_tree():
    tracer, _ = _tracer()
    with pytest.raises(TransientError), tracer.trace("answer") as trace:
        with tracer.span("retrieve", kind="retrieval"):
            pass
        for _ in range(20):
            with tracer.span("noise", kind="internal"):
                pass
        with tracer.span("verify", kind="agent"), tracer.span("fact-check", kind="llm"):
            raise TransientError("provider down")

    assert len(trace.spans) > 20
    assert [s.name for s in trace.failure_path()] == ["answer", "verify", "fact-check"]
    assert trace.failure_path()[-1].error["code"] == "transient"


def test_error_status_and_metrics_are_recorded_from_the_span():
    tracer, _ = _tracer()
    with pytest.raises(TransientError), tracer.trace("run"), tracer.span("call", kind="llm"):
        raise TransientError("boom")

    assert (
        tracer.registry.counter("omnex_errors_total", labels=("kind", "code")).value(
            kind="llm", code="transient"
        )
        == 1
    )


def test_rendered_tree_marks_the_expensive_step():
    tracer, clock = _tracer()
    with tracer.trace("answer") as trace:
        with tracer.span("retrieve", kind="retrieval"):
            clock.advance(0.02)
        with tracer.span("generate", kind="llm", model="opus") as span:
            clock.advance(1.2)
            span.record_usage(Money.from_usd("0.031"), input_tokens=9000, output_tokens=700)

    rendered = trace.render(cost_threshold=Money.from_usd("0.01"))
    assert "└─" in rendered or "├─" in rendered
    assert "generate [llm]" in rendered
    assert "←" in rendered  # the expensive step is flagged
    assert "$0.0310" in rendered


async def test_concurrent_tasks_do_not_reparent_each_others_spans():
    """A module-level 'current span' silently corrupts every trace under asyncio."""
    tracer, _ = _tracer()
    results: dict[str, object] = {}

    async def run(name: str) -> None:
        with tracer.trace(name) as trace, tracer.span(f"{name}-outer"):
            await asyncio.sleep(0)
            with tracer.span(f"{name}-inner"):
                await asyncio.sleep(0)
        results[name] = trace

    await asyncio.gather(run("alpha"), run("beta"))

    for name in ("alpha", "beta"):
        trace = results[name]
        assert {s.name for s in trace.spans} == {name, f"{name}-outer", f"{name}-inner"}
        inner = next(s for s in trace.spans if s.name == f"{name}-inner")
        outer = next(s for s in trace.spans if s.name == f"{name}-outer")
        assert inner.parent_id == outer.span_id


def test_span_outside_a_trace_is_a_loud_error():
    tracer, _ = _tracer()
    with pytest.raises(RuntimeError, match="outside a trace"), tracer.span("orphan"):
        pass


# ── Tail sampling ─────────────────────────────────────────────────────────


def test_tail_sampling_keeps_every_error_where_head_sampling_would_keep_one_percent():
    clock = FakeClock()
    tracer = Tracer(
        clock=clock,
        ids=IdFactory(clock=clock, rng=Random(2)),
        sampler=TailSampler(baseline_rate=0.0, rng=Random(3)),
    )
    for i in range(200):
        if i % 20 == 0:
            with pytest.raises(TransientError), tracer.trace("run"), tracer.span("call"):
                raise TransientError("boom")
        else:
            with tracer.trace("run"), tracer.span("call"):
                pass

    assert len(tracer.kept) == 10  # every failure, nothing else
    assert all(t.attributes["sampling"] == "error" for t in tracer.kept)


def test_tail_sampling_keeps_slow_and_expensive_traces():
    clock = FakeClock()
    tracer = Tracer(
        clock=clock,
        ids=IdFactory(clock=clock, rng=Random(4)),
        sampler=TailSampler(baseline_rate=0.0, slow_threshold_seconds=5.0, rng=Random(5)),
    )
    with tracer.trace("slow"), tracer.span("call"):
        clock.advance(6.0)
    with tracer.trace("pricey"), tracer.span("call", kind="llm") as span:
        span.record_usage(Money.from_usd("0.05"))
    with tracer.trace("ordinary"), tracer.span("call"):
        clock.advance(0.01)

    assert [t.attributes["sampling"] for t in tracer.kept] == ["slow", "expensive"]


# ── Anomaly detection ─────────────────────────────────────────────────────


def test_median_baseline_catches_a_spike_that_mean_and_stddev_miss():
    """The spike inflates the standard deviation it is measured against."""
    rng = Random(9)
    normal = [0.10 + rng.gauss(0, 0.01) for _ in range(100)]
    spike = 0.9

    baseline = RobustBaseline(window=100)
    for v in normal:
        baseline.observe(v)
    robust_score = baseline.score(spike)

    # Contaminate a mean/stddev baseline the way a real window would be, with a
    # handful of earlier spikes still inside it.
    contaminated = [*normal[:90], 0.85, 0.88, 0.91, 0.87, 0.86, 0.89, 0.90, 0.84, 0.92, 0.83]
    mu = statistics.fmean(contaminated)
    sigma = statistics.pstdev(contaminated)
    classic_z = (spike - mu) / sigma

    assert robust_score is not None and robust_score > 20  # unmistakable
    assert classic_z < 3.5  # the same spike is invisible to mean/stddev
    assert baseline.is_anomalous(spike)


def test_baseline_refuses_to_judge_before_it_has_seen_enough():
    baseline = RobustBaseline(min_samples=20)
    for _ in range(5):
        baseline.observe(0.1)
    assert baseline.score(99.0) is None
    assert not baseline.is_anomalous(99.0)


def test_identical_window_does_not_report_infinite_severity():
    """MAD is zero for a healthy rare-event counter; an epsilon would make it explode."""
    baseline = RobustBaseline(min_samples=5)
    for _ in range(30):
        baseline.observe(0.0)
    assert baseline.score(0.0) is None
    assert baseline.score(1.0) == float("inf")  # stated, not a silent 1e12


def test_normal_variation_is_not_flagged():
    rng = Random(11)
    baseline = RobustBaseline()
    for _ in range(100):
        baseline.observe(0.1 + rng.gauss(0, 0.01))
    assert not baseline.is_anomalous(0.115)


# ── Alerting ──────────────────────────────────────────────────────────────


def _rules() -> list[AlertRule]:
    return [
        AlertRule(
            name="ErrorRateHigh",
            metric="error_rate",
            threshold=0.05,
            severity=Severity.PAGE,
            for_evaluations=3,
            clear_evaluations=5,
            summary="More than 5% of requests failing",
        )
    ]


def test_alert_needs_a_sustained_breach_before_firing():
    manager = AlertManager(_rules())
    for _ in range(2):
        fired, _ = manager.evaluate({"error_rate": 0.2})
        assert fired == []
    fired, _ = manager.evaluate({"error_rate": 0.2})
    assert [a.rule.name for a in fired] == ["ErrorRateHigh"]
    assert fired[0].as_dict()["severity"] == "page"


def test_alert_does_not_re_notify_while_it_stays_firing():
    manager = AlertManager(_rules())
    for _ in range(10):
        manager.evaluate({"error_rate": 0.2})
    fired, resolved = manager.evaluate({"error_rate": 0.2})
    assert fired == [] and resolved == []
    assert manager.firing == ["ErrorRateHigh"]


def test_hysteresis_stops_a_borderline_metric_from_flapping():
    """Firing fast and resolving slow is what turns a pager storm into one page."""
    manager = AlertManager(_rules())
    for _ in range(3):
        manager.evaluate({"error_rate": 0.06})
    assert manager.firing == ["ErrorRateHigh"]

    # Oscillating either side of the threshold must not produce a resolve/fire pair.
    for value in (0.04, 0.06, 0.04, 0.06, 0.04, 0.06):
        fired, resolved = manager.evaluate({"error_rate": value})
        assert fired == [] and resolved == []
    assert manager.firing == ["ErrorRateHigh"]

    # Genuinely healthy for the full clear window: resolves exactly once.
    transitions = [manager.evaluate({"error_rate": 0.001}) for _ in range(6)]
    assert [r for _, resolved in transitions for r in resolved] == ["ErrorRateHigh"]
    assert manager.firing == []


def test_missing_metric_is_not_treated_as_zero():
    """A scrape gap must not resolve an alert, nor fire a 'below threshold' one."""
    manager = AlertManager(
        [
            AlertRule(
                name="ThroughputLow",
                metric="rps",
                threshold=1.0,
                comparison="lt",
                for_evaluations=2,
            )
        ]
    )
    for _ in range(5):
        fired, resolved = manager.evaluate({})
        assert fired == [] and resolved == []


# ── Cost ledger ───────────────────────────────────────────────────────────


def _event(
    trace_id: str, model: str, usd: str, undiscounted: str | None = None, tenant: str = "t1"
) -> CostEvent:
    return CostEvent(
        at=FakeClock().now(),
        trace_id=trace_id,
        model=model,
        cost=Money.from_usd(usd),
        undiscounted=Money.from_usd(undiscounted or usd),
        tenant_id=tenant,
    )


def test_cost_per_request_is_a_distribution_not_a_mean():
    """An agent making twelve cheap calls must not look cheaper than one expensive call."""
    ledger = CostLedger()
    for r in range(980):
        for _ in range(12):  # a chatty agent run: many small calls
            ledger.record(_event(f"trace-{r}", "haiku", "0.00002"))
        ledger.seal_request(f"trace-{r}")
    for r in range(20):  # a long-context run: one large call
        ledger.record(_event(f"big-{r}", "opus", "0.42"))
        ledger.seal_request(f"big-{r}")

    dist = ledger.per_request()
    assert dist["requests"] == 1000
    # Bucketed, so within the histogram's stated bound rather than exact — and
    # never below the true value, which is the direction that matters for spend.
    true_p50 = Money.from_usd("0.00024")
    assert true_p50 <= dist["p50"] <= Money.from_picos(int(true_p50.picos * (1 + RELATIVE_ERROR)))
    assert dist["p99"] > Money.from_usd("0.4")
    assert ledger.tail_ratio() > 1000  # 2% of requests carry 97% of the bill

    # The mean is kept exactly — and still sits above 98% of requests while
    # being dominated by the 2% that are not. That gap is the whole argument
    # for reporting a distribution rather than an average.
    assert dist["mean"] > dist["p50"]
    assert dist["mean"] < dist["p99"]


def test_p99_of_one_hundred_samples_cannot_see_a_one_in_a_hundred_event():
    """A percentile needs enough samples to contain the event you are asking about.

    With exactly 100 requests and one expensive outlier, the 99th ordered value
    is still a cheap request — the outlier is the 100th. A dashboard showing p99
    over a low-traffic window is therefore blind to precisely the rare, costly
    request it was put there to catch, and the fix is a wider window or a max,
    not a bigger number.
    """
    ledger = CostLedger()
    for r in range(99):
        ledger.record(_event(f"t{r}", "haiku", "0.0001"))
        ledger.seal_request(f"t{r}")
    ledger.record(_event("outlier", "opus", "0.42"))
    ledger.seal_request("outlier")

    dist = ledger.per_request()
    assert dist["p99"] < Money.from_usd("0.001")  # the outlier is invisible at p99
    assert dist["max"] > Money.from_usd("0.4")  # but max still reports it


def test_sealing_is_what_separates_per_request_from_per_call():
    ledger = CostLedger()
    for _ in range(4):
        ledger.record(_event("t", "haiku", "0.001"))
    assert ledger.per_request()["requests"] == 0  # nothing sealed yet
    assert ledger.seal_request("t") == Money.from_usd("0.004")
    assert ledger.per_request()["requests"] == 1


def test_savings_are_measured_against_a_recorded_baseline_not_asserted():
    ledger = CostLedger()
    for i in range(10):
        ledger.record(_event(f"t{i}", "haiku", "0.0002", undiscounted="0.0030"))
        ledger.seal_request(f"t{i}")
    overall = ledger.overall
    assert overall.total == Money.from_usd("0.002")
    assert overall.undiscounted == Money.from_usd("0.03")
    assert overall.saved == Money.from_usd("0.028")
    assert overall.saved_percent == pytest.approx(93.33, abs=0.01)


def test_spend_is_attributed_by_tenant_and_model():
    ledger = CostLedger()
    ledger.record(_event("a", "opus", "0.30", tenant="acme"))
    ledger.record(_event("b", "haiku", "0.01", tenant="acme"))
    ledger.record(_event("c", "haiku", "0.05", tenant="globex"))
    assert list(ledger.by_tenant()) == ["acme", "globex"]
    assert ledger.by_tenant()["acme"] == Money.from_usd("0.31")
    assert list(ledger.by_model()) == ["opus", "haiku"]


def test_ledger_ingests_a_trace_and_attributes_every_cost_bearing_span():
    clock = FakeClock()
    tracer = Tracer(clock=clock, ids=IdFactory(clock=clock, rng=Random(6)))
    with tracer.trace("answer") as trace:
        with tracer.span("retrieve", kind="retrieval"):
            pass
        with tracer.span(
            "generate", kind="llm", model="sonnet", undiscounted_picos=30_000_000_000
        ) as span:
            span.record_usage(Money.from_usd("0.002"), input_tokens=1200, output_tokens=300)

    ledger = CostLedger()
    total = ledger.record_trace(trace, tenant_id="acme", route="/answer")
    assert total == Money.from_usd("0.002")
    assert ledger.overall.saved == Money.from_usd("0.028")
    assert ledger.by_route()["/answer"] == Money.from_usd("0.002")
    assert ledger.tokens() == {"input": 1200, "output": 300, "cached_input": 0}


def test_report_is_readable_and_states_the_savings():
    ledger = CostLedger()
    for i in range(50):
        ledger.record(_event(f"t{i}", "haiku", "0.0002", undiscounted="0.0030"))
        ledger.seal_request(f"t{i}")
    report = ledger.report()
    assert "saved" in report and "%" in report
    assert "p50" in report and "p99" in report


def test_a_pico_dollar_counter_stays_exact_past_the_float_boundary():
    """The float currency path that had reappeared in the metrics export.

    `trace.py` recorded cost as `float(span.cost.picos)`. IEEE754 doubles hold
    integers exactly only below 2**53, which is 9,007,199,254,740,992 picos —
    $9,007.20. The cost counter is cumulative, so this was not a question of
    whether it would arrive.

    The failure is silent and one-directional: the counter keeps incrementing
    and quietly stops being the number it reports. `core/money.py` exists to
    prevent exactly this, and the rule had been re-broken somewhere nobody reads.
    """
    from omnex.obs.metrics import MetricsRegistry

    registry = MetricsRegistry()
    counter = registry.counter("omnex_cost_picodollars_total", "cost", ("model",))

    boundary = 2**53
    counter.inc(boundary, model="strong")
    counter.inc(1, model="strong")
    assert counter.value(model="strong") == boundary + 1

    # The same two increments as floats cannot tell those apart, which is the
    # whole point rather than a curiosity about this test.
    assert float(boundary) + 1.0 == float(boundary)

    rendered = registry.render()
    assert str(boundary + 1) in rendered, "the exposition rounded an exact amount"


def test_the_cost_counter_is_fed_integers_not_floats():
    """Guarding the call site, not just the container.

    An exact accumulator is undone by one `float()` at the point of use, and
    that cast is the easiest thing in the world to reintroduce while "fixing a
    type error".
    """
    from omnex.core.money import Money
    from omnex.obs.metrics import MetricsRegistry

    registry = MetricsRegistry()
    clock = FakeClock()
    tracer = Tracer(
        clock=clock,
        ids=IdFactory(clock=clock, rng=Random(7)),
        registry=registry,
        sampler=TailSampler(baseline_rate=1.0),
    )
    with tracer.trace("run"), tracer.span("call", kind="llm") as span:
        span.cost = Money.from_picos(2**53 + 7)

    counter = registry.counter("omnex_cost_picodollars_total", labels=("kind", "model"))
    recorded = list(counter.values.values())
    assert recorded, "the tracer recorded no cost"
    assert all(isinstance(value, int) for value in recorded), (
        f"cost reached the counter as a float: {recorded}"
    )
    assert counter.total == 2**53 + 7
