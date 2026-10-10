from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager
from random import Random

import pytest

from omnex.core import IdFactory, RetryPolicy, TransientError, ValidationFailed
from omnex.pipeline import InMemoryBroker, JobState, Worker
from omnex.pipeline.queue import IdempotencyStore


class TrackingStore(IdempotencyStore):
    def __init__(self):
        super().__init__()
        self._entered_guard = threading.Lock()
        self._entries = 0
        self.second_entry = threading.Event()

    @contextmanager
    def serialise(self, key: str) -> Iterator[None]:
        with self._entered_guard:
            self._entries += 1
            if self._entries == 2:
                self.second_entry.set()
        with super().serialise(key):
            yield


def _worker(store: IdempotencyStore | None = None):
    broker = InMemoryBroker(ids=IdFactory(rng=Random(1)))
    worker = Worker(
        broker=broker, idempotency=store or IdempotencyStore(), policy=RetryPolicy(max_attempts=1)
    )
    return broker, worker


def test_concurrent_same_key_across_workers_executes_and_records_once():
    store = TrackingStore()
    broker, first = _worker(store)
    _, second = _worker(store)
    entered = threading.Event()
    release = threading.Event()
    calls = 0
    call_guard = threading.Lock()

    def handler(job):
        nonlocal calls
        with call_guard:
            calls += 1
        entered.set()
        assert release.wait(timeout=3)
        return {"amount": job.payload["amount"]}

    first.register("charge", handler)
    second.register("charge", handler)
    job_a = broker.enqueue("charge", {"amount": 5}, "evt-1")
    job_b = broker.enqueue("charge", {"amount": 5}, "evt-1")
    failures: list[BaseException] = []

    def run(worker, job):
        try:
            worker.run_once(job)
        except BaseException as exc:
            failures.append(exc)

    thread_a = threading.Thread(target=run, args=(first, job_a))
    thread_b = threading.Thread(target=run, args=(second, job_b))
    thread_a.start()
    assert entered.wait(timeout=3)
    thread_b.start()
    assert store.second_entry.wait(timeout=3)
    release.set()
    thread_a.join(timeout=3)
    thread_b.join(timeout=3)

    assert not thread_a.is_alive() and not thread_b.is_alive()
    assert failures == []
    assert calls == 1
    assert job_a.state is JobState.DONE and job_b.state is JobState.DONE
    assert job_a.result == job_b.result == {"amount": 5}
    assert store._key_locks == {}


def test_different_keys_execute_concurrently():
    _, worker = _worker()
    both_inside = threading.Barrier(2)
    worker.register("run", lambda job: (both_inside.wait(timeout=3), job.id)[1])
    jobs = [worker.broker.enqueue("run", {}, key) for key in ("key-a", "key-b")]
    errors: list[BaseException] = []

    def run(job):
        try:
            worker.run_once(job)
        except BaseException as exc:
            errors.append(exc)

    threads = [threading.Thread(target=run, args=(job,)) for job in jobs]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=4)

    assert not any(thread.is_alive() for thread in threads)
    assert errors == []
    assert all(job.state is JobState.DONE for job in jobs)
    assert worker.idempotency._key_locks == {}


def test_failed_handler_releases_key_and_later_delivery_can_retry():
    _, worker = _worker()
    calls = 0

    def handler(job):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise TransientError("upstream unavailable")
        return "charged"

    worker.register("charge", handler)
    first = worker.broker.enqueue("charge", {"amount": 5}, "evt-2")
    assert worker.run_once(first).state is JobState.DEAD
    assert worker.idempotency.check("evt-2", first.fingerprint) == (False, None)
    assert worker.idempotency._key_locks == {}

    retry = worker.broker.enqueue("charge", {"amount": 5}, "evt-2")
    assert worker.run_once(retry).state is JobState.DONE
    assert retry.result == "charged"
    assert calls == 2
    assert worker.idempotency._key_locks == {}


def test_same_key_with_different_payload_remains_a_conflict():
    _, worker = _worker()
    worker.register("charge", lambda job: job.payload["amount"])
    first = worker.broker.enqueue("charge", {"amount": 5}, "evt-3")
    worker.run_once(first)
    mismatch = worker.broker.enqueue("charge", {"amount": 500}, "evt-3")

    with pytest.raises(ValidationFailed, match="different payload"):
        worker.run_once(mismatch)
    assert worker.idempotency._key_locks == {}


def test_completed_keys_do_not_leave_lock_entries_behind():
    _, worker = _worker()
    worker.register("noop", lambda job: "ok")
    for number in range(200):
        worker.run_once(worker.broker.enqueue("noop", {"n": number}, f"key-{number}"))
    assert worker.idempotency._key_locks == {}
