# OMNEX Engine

**Eighteen production AI systems, built as one platform.**

The Python side of OMNEX Factory. Each subpackage is one system and each is
usable alone, but they live together because the interesting behaviour is
*between* them: the router spends a budget the observability layer accounts for,
the RAG pipeline retrieves through the vector layer and is scored by the eval
harness, which is the gate the deploy pipeline refuses to ship past.

---

## The rule this is built under

> *What does this system do when it is wrong, and how would you know?*

Same question the TypeScript side of this repo is built around, and it decides
most of what follows.

---

## No required dependencies

```toml
dependencies = []
```

Core, tracing, cost accounting, hybrid search, guardrails and the eval metrics
are written against the standard library. Every heavy library — LangGraph,
CrewAI, vLLM, PEFT, Qdrant, DeepEval, Redis — is an **adapter behind a
Protocol**, with an in-repo implementation the tests use instead.

This is not minimalism. It means the whole suite runs on a bare interpreter,
offline, with no API key, in about a second. A test suite that needs credentials
is a test suite that quietly stops being run, and CI enforces the property by
re-running everything with the provider environment variables blanked.

---

## Two decisions that propagate everywhere

### Money is an integer count of pico-dollars

The familiar argument is that `0.1 + 0.2 != 0.3`, so a spend counter drifts away
from the invoice. The half specific to LLM cost matters more: prices are quoted
per *million* tokens, and one token of a cheap model costs about `$0.00000005`.
Micro-dollars — the usual choice for payments — round that to zero, so a system
tracking micro-dollars reports that 20,000 cheap tokens were free.

Pico-dollars (1e-12) are also *exact* for every published price, because `$X` per
million tokens is exactly `X · 1e6` picos per token. A test adds one request cost
a million times and lands on `$41.000000` with no drift. Rounding happens once,
explicitly, at the boundary where Stripe or a human sees a number.

### Time is injected, never read from the host

Deadline-aware retry, cache TTLs and latency percentiles are untestable
otherwise — reproducing *"gave up on the fourth attempt because the deadline ran
out"* would mean waiting real seconds. `FakeClock` records a 32-second backoff
without costing the suite 32 seconds.

`now()` and `monotonic()` are separate: wall-clock time can jump backwards when
NTP corrects the host, and measuring a duration with it is how you get a negative
p99.

---

## Layout

```
src/omnex/
  core/      money · clock · ids · errors · retry     no AI dependency at all
  obs/       P5  tracing · cost · percentiles · alerting
  llm/       model protocol · pricing · deterministic test models
  router/    P2  complexity routing · spend tracking · cascade fallback
```

Landing next: `guard/` (P6) · `vectors/` (P12) · `rag/` (P1) · `memory/` (P13) ·
`evals/` (P4) · `crew/` (P3) · `hitl/` (P15) · `pipeline/` (P16) · `tenancy/`
(P10) · `serving/` (P14) · `finetune/` (P9).

---

## Running it

```bash
uv venv .venv
uv pip install --python .venv/bin/python -e '.[dev]'

.venv/bin/python -m pytest tests/      # the whole suite, ~1s, no network
.venv/bin/mypy                         # strict
.venv/bin/ruff check src tests
```

The observability stack, if you want to look at the dashboards rather than trust
them:

```bash
docker compose -f ../deploy/observability/compose.yaml up -d
# Grafana on :3001 — port 3001, not 3000, because 3000 is the Next.js app
```

---

## What is asserted, and where

Claims worth checking rather than believing:

| Claim | Test |
|---|---|
| Money does not drift over a million additions | `test_money_does_not_drift_over_a_million_additions` |
| Cheap-model tokens are not rounded to zero | `test_cheap_model_token_cost_is_not_rounded_to_zero` |
| Retry never sleeps past its own deadline | `test_deadline_stops_the_loop_before_sleeping_through_it` |
| Percentiles cannot be averaged — 2× low one way, 50× high the other | `test_merging_beats_averaging_percentiles_in_both_directions` |
| Latency error bound holds at every magnitude | `test_reported_value_is_within_the_stated_error_bound` |
| Tail sampling keeps every error | `test_tail_sampling_keeps_every_error_...` |
| Parent spans never double-count cost | `test_cost_is_not_double_counted_by_parents` |
| Concurrent tasks do not reparent each other's spans | `test_concurrent_tasks_do_not_reparent_each_others_spans` |
| A cost spike invisible to mean/stddev is caught by median/MAD | `test_median_baseline_catches_a_spike_that_mean_and_stddev_miss` |
| Alerts cannot flap into a pager storm | `test_hysteresis_stops_a_borderline_metric_from_flapping` |
| Shipped dashboards only query metrics the code emits | `test_deployed_queries_only_reference_metrics_the_code_emits` |

Two findings that are worth knowing independently of this codebase, both kept as
tests rather than as comments:

- **p99 over exactly 100 requests cannot see a 1-in-100 event.** The 99th ordered
  value is still a cheap request; the outlier is the 100th. A p99 panel on a
  low-traffic window is blind to precisely the rare expensive request it exists
  to catch.
- **A cardinality cap should fold, not drop.** Folding overflow into a single
  series keeps totals correct while refusing to mint new ones — and the overflow
  count is published, because a metric that silently stopped being a breakdown is
  one people keep reading as if it still were.

---

*Nothing described here is aspirational. Where a number appears, a test produces
it.*
