"""Where money is counted under threads, and where the limit is declared instead.

A lost concurrent write does not raise, does not leave a gap in a sequence, and
does not appear anywhere. It produces a total lower than the sum of what
happened — and a cost figure that is quietly low is worse than one that is
missing, because it gets believed and acted on.

Only `obs/metrics.py` had a lock. `obs.CostLedger`, where the money actually
lands, did not. Neither did `factory.AgentEconomics`, whose duplicate refusal is
a check-then-act pair and so was defeated by the exact race it exists to prevent.

## The switch interval, and why the first version of this file was worthless

Written the obvious way — eight threads, a barrier, assert the total — every
test here passed WITHOUT the lock. CPython's default 5ms switch interval means
threads rarely interleave inside a short critical section, so the suite would
have shipped a guard nobody had shown was doing anything. That is the same
"check that cannot fail" this repository breaks emitters on purpose to avoid,
and it was reintroduced here by accident.

`sys.setswitchinterval(1e-9)` forces the interpreter to switch aggressively.
With it, the unlocked ledger loses more than half the money — measured at $0.29
recorded out of $0.64 spent — while the EVENT COUNT stays correct. A ledger
reporting the right number of events and half the amount is the worst shape this
could take, and it is what `test_the_lock_is_load_bearing` demonstrates rather
than asserts.

The GIL is not a defence to rely on either way: it narrows this window, it does
not close it, and free-threaded CPython removes it.

## Two of these prove a guarantee; two prove the absence of one

The declared-limit tests are honesty anchors in the sense
`test_a_paraphrase_outside_the_corpus_is_missed` is: they are SUPPOSED to be
green, and they assert the boundary is written where somebody reads it before
relying on it. A limitation that is a passing test is a limitation nobody
discovers in production.
"""

from __future__ import annotations

import contextlib
import sys
import threading
from collections.abc import Callable, Iterator
from datetime import UTC, datetime

import pytest

from omnex.core.errors import ValidationFailed
from omnex.core.money import Money
from omnex.factory import AgentEconomics, Portfolio, Run, RunCost
from omnex.obs.cost import CostEvent, CostLedger
from omnex.vectors.store import HybridStore

#: Enough contention to surface a lost update once switching is aggressive.
#: Below roughly this, the race is real and simply does not show up often enough
#: for a test to depend on.
THREADS = 16
PER_THREAD = 400
PENNY = Money.from_usd("0.0001")
AT = datetime(2026, 1, 1, tzinfo=UTC)


@pytest.fixture(autouse=True)
def _aggressive_thread_switching() -> Iterator[None]:
    """Global and restored. Without it every assertion here passes unguarded."""
    original = sys.getswitchinterval()
    sys.setswitchinterval(1e-9)
    try:
        yield
    finally:
        sys.setswitchinterval(original)


def _in_parallel(work: Callable[[int], None], count: int = THREADS) -> list[BaseException]:
    """Run `work(index)` on `count` threads released together, collecting failures.

    A barrier rather than plain starts: without one the first thread often
    finishes before the last begins, and the test passes by never overlapping.
    """
    barrier = threading.Barrier(count)
    failures: list[BaseException] = []
    lock = threading.Lock()

    def runner(index: int) -> None:
        barrier.wait()
        try:
            work(index)
        # Every exception, so a thread that dies is reported by the assertion
        # rather than by a traceback on stderr that pytest counts as a pass.
        except BaseException as exc:
            with lock:
                failures.append(exc)

    threads = [threading.Thread(target=runner, args=(i,)) for i in range(count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return failures


def _hammer(ledger: CostLedger) -> None:
    def work(index: int) -> None:
        for _ in range(PER_THREAD):
            ledger.record(
                CostEvent(
                    at=AT,
                    trace_id=f"trace-{index}",
                    model=f"model-{index % 2}",
                    cost=PENNY,
                    undiscounted=PENNY,
                    tenant_id=f"tenant-{index % 4}",
                    route="chat",
                    input_tokens=1,
                )
            )

    assert not _in_parallel(work)


# ── locked: the money aggregates ──────────────────────────────────────────
def test_the_cost_ledger_loses_no_event_under_threads() -> None:
    ledger = CostLedger()
    _hammer(ledger)
    expected = THREADS * PER_THREAD
    assert ledger.overall.events == expected
    assert ledger.overall.total == PENNY * expected
    assert ledger.tokens()["input"] == expected


def test_every_aggregate_in_the_ledger_agrees_after_a_race() -> None:
    """A partial write is the dangerous shape: a total no breakdown sums to."""
    ledger = CostLedger()
    _hammer(ledger)
    total = ledger.overall.total
    assert sum((b.total for b in ledger.by_model().values()), Money.zero()) == total
    assert sum(ledger.by_tenant().values(), Money.zero()) == total
    assert sum(ledger.by_route().values(), Money.zero()) == total


def test_the_lock_is_load_bearing() -> None:
    """Proof the guard does work, by removing it and measuring the damage.

    The pattern `test_the_round_trip_check_can_actually_fail` uses: a check that
    passes for the wrong reason is indistinguishable from one that works, and
    this file's first version was exactly that.

    Note which number stays right. The event count is correct and the money is
    not, so nothing about the output looks partial — it looks like a smaller
    bill.
    """
    unlocked = CostLedger()
    unlocked._lock = contextlib.nullcontext()  # type: ignore[assignment]
    _hammer(unlocked)

    expected = PENNY * (THREADS * PER_THREAD)
    assert unlocked.overall.events == THREADS * PER_THREAD, (
        "even the event count survived, so contention is too low for this to prove anything"
    )
    assert unlocked.overall.total < expected, (
        "the unlocked ledger did not lose an update; raise THREADS/PER_THREAD or "
        "check that setswitchinterval is in effect, because as written this file "
        "proves nothing about the lock"
    )


def test_agent_economics_records_every_run_under_threads() -> None:
    economics = AgentEconomics()

    def work(index: int) -> None:
        for step in range(PER_THREAD):
            economics.record(
                Run(
                    run_id=f"{index}-{step}",
                    agent="broker",
                    customer="acme",
                    at=AT,
                    revenue=Money.from_usd("0.01"),
                    cost=RunCost(model=PENNY),
                )
            )

    assert not _in_parallel(work)
    assert economics.overall().runs == THREADS * PER_THREAD


def test_the_duplicate_refusal_survives_contention() -> None:
    """Check-then-act, the shape a race defeats most quietly.

    Unlocked, two threads submitting one `run_id` both find it absent and both
    append — and the refusal written specifically to stop double counting is the
    thing that fails. Exactly one thread must win.
    """
    economics = AgentEconomics()
    run = Run(
        run_id="contested",
        agent="broker",
        customer="acme",
        at=AT,
        revenue=Money.from_usd("0.01"),
        cost=RunCost(model=PENNY),
    )

    failures = _in_parallel(lambda _: economics.record(run))
    assert all(isinstance(f, ValidationFailed) for f in failures)
    assert len(failures) == THREADS - 1, "more than one thread recorded the same run"
    assert economics.overall().runs == 1


def test_acquisition_totals_survive_threads() -> None:
    economics = AgentEconomics()

    def work(_: int) -> None:
        for _step in range(PER_THREAD):
            economics.record_acquisition("acme", PENNY)

    assert not _in_parallel(work)
    economics.record(
        Run(
            run_id="one",
            agent="broker",
            customer="acme",
            at=AT,
            revenue=PENNY * (THREADS * PER_THREAD) + PENNY,
            cost=RunCost(model=PENNY),
        )
    )
    # Acquisition totalled exactly, so one run of this margin repays it.
    assert economics.payback_runs("acme") == 1


# ── declared: the limits that are written down instead ────────────────────
@pytest.mark.parametrize("subject", [HybridStore, Portfolio])
def test_a_single_writer_component_says_so_where_somebody_will_read_it(subject: type) -> None:
    """An honesty anchor, and it is supposed to be green.

    Neither is locked, and that is a decision rather than an oversight: a store
    is rebuilt and rebound, and a portfolio decision comes out of a meeting. The
    failure mode of leaving it unwritten is somebody putting either behind a
    request handler assuming everything here is safe.
    """
    doc = subject.__doc__ or ""
    assert "Single-writer" in doc, f"{subject.__name__} does not declare its concurrency limit"
    assert "not thread-safe" in doc.lower()


def test_the_locked_and_the_declared_are_not_the_same_set() -> None:
    """Proof the distinction is real rather than a phrase applied everywhere."""
    assert "Single-writer" not in (CostLedger.__doc__ or "")
    assert "thread-safe" in (AgentEconomics.__doc__ or "")
    assert "Single-writer" in (Portfolio.__doc__ or "")
