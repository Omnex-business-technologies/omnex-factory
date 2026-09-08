"""Async work: idempotency, retries, and a dead-letter queue you can replay.

Four decisions, each closing a hole that shows up in production rather than in
a design review.

**An idempotency key covers the PAYLOAD, not just the key.** The usual
implementation stores seen keys and returns the cached result on a repeat. That
is right for a genuine retry and catastrophically wrong for a caller that reused
a key with a different body — an off-by-one in their loop, a stale variable —
because it silently returns the wrong answer for a request that was never
processed. So the payload hash is stored with the key and a mismatch is a
CONFLICT, loudly, rather than a cache hit.

**Delivery is at-least-once, so handlers must be idempotent, and this says so.**
Exactly-once delivery does not exist across a network. Pretending otherwise
pushes the duplicate handling into whichever handler forgets it.

**Dead letters keep everything needed to replay.** A DLQ holding only an error
message is a list of things you know broke and cannot retry. Each entry keeps
the original payload, every attempt's error, and the idempotency key — so a
replay after a fix is one call, and a replay of something already fixed is a
no-op rather than a double charge.

**Retry classification comes from the error, not the handler.** A `PermanentError`
dead-letters on the first attempt: retrying a malformed payload four times
produces four identical failures and delays the alert by the backoff schedule.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from random import Random
from typing import Any

from ..core.clock import Clock, SystemClock
from ..core.errors import OmnexError, PermanentError, ValidationFailed
from ..core.ids import IdFactory
from ..core.retry import RetryPolicy

__all__ = [
    "DeadLetter",
    "IdempotencyStore",
    "InMemoryBroker",
    "Job",
    "JobState",
    "Worker",
    "payload_hash",
]


def payload_hash(payload: Any) -> str:
    """Stable hash of a payload. Key order must not change the hash."""
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[
        :32
    ]


class JobState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    RETRYING = "retrying"
    DEAD = "dead"


@dataclass
class Job:
    id: str
    kind: str
    payload: dict[str, Any]
    #: Supplied by the caller. Two jobs with the same key are the same job.
    idempotency_key: str = ""
    attempts: int = 0
    state: JobState = JobState.QUEUED
    errors: list[str] = field(default_factory=list)
    result: Any = None

    @property
    def fingerprint(self) -> str:
        return payload_hash(self.payload)


@dataclass
class DeadLetter:
    """Everything needed to replay the job after the bug is fixed."""

    job: Job
    reason: str
    attempts: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job.id,
            "kind": self.job.kind,
            "payload": self.job.payload,
            "idempotency_key": self.job.idempotency_key,
            "reason": self.reason,
            "attempts": self.attempts,
            "errors": self.job.errors,
        }


@dataclass
class IdempotencyStore:
    """Remembers completed work, keyed by (key, payload hash)."""

    #: key -> (payload fingerprint, result)
    seen: dict[str, tuple[str, Any]] = field(default_factory=dict)

    def check(self, key: str, fingerprint: str) -> tuple[bool, Any]:
        """Returns (already_done, cached_result). Raises on a key/payload mismatch."""
        if not key:
            return False, None
        record = self.seen.get(key)
        if record is None:
            return False, None
        stored_fingerprint, result = record
        if stored_fingerprint != fingerprint:
            # The dangerous case. Returning the cached result here answers a
            # request that was never processed, with data from a different one.
            raise ValidationFailed(
                "idempotency key reused with a different payload — refusing to return "
                "a result computed from other data",
                key=key,
                stored=stored_fingerprint,
                received=fingerprint,
            )
        return True, result

    def record(self, key: str, fingerprint: str, result: Any) -> None:
        if key:
            self.seen[key] = (fingerprint, result)


Handler = Callable[[Job], Any]


@dataclass
class InMemoryBroker:
    """A broker that needs no Redis. The default, and the ONLY one that exists.

    It exists so the whole retry / DLQ / idempotency behaviour is testable
    without a service, which is the only way those paths get exercised on every
    commit. An earlier version of this docstring called Celery the production
    path and named a celery adapter module — that file has never existed, the
    `worker` extra is declared `unsupported`, and `pipeline.Claims` is what
    actually covers the durable case the n8n workflow needs.
    """

    jobs: list[Job] = field(default_factory=list)
    ids: IdFactory = field(default_factory=IdFactory)

    def enqueue(self, kind: str, payload: dict[str, Any], idempotency_key: str = "") -> Job:
        job = Job(
            id=self.ids.new("job"), kind=kind, payload=payload, idempotency_key=idempotency_key
        )
        self.jobs.append(job)
        return job

    def pending(self) -> list[Job]:
        return [j for j in self.jobs if j.state in (JobState.QUEUED, JobState.RETRYING)]


@dataclass
class Worker:
    """Runs jobs with retry, idempotency and dead-lettering."""

    broker: InMemoryBroker
    handlers: dict[str, Handler] = field(default_factory=dict)
    policy: RetryPolicy = field(default_factory=lambda: RetryPolicy(max_attempts=3, base_delay=0.5))
    idempotency: IdempotencyStore = field(default_factory=IdempotencyStore)
    clock: Clock = field(default_factory=SystemClock)
    rng: Random = field(default_factory=Random)
    dead_letters: list[DeadLetter] = field(default_factory=list)

    def register(self, kind: str, handler: Handler) -> None:
        self.handlers[kind] = handler

    def run_once(self, job: Job) -> Job:
        handler = self.handlers.get(job.kind)
        if handler is None:
            # An unregistered kind is a deploy problem, not a transient one.
            # Dead-lettering keeps the payload so it can be replayed once the
            # handler ships, instead of being dropped or retried forever.
            job.state = JobState.DEAD
            self.dead_letters.append(DeadLetter(job, f"no handler for {job.kind!r}", job.attempts))
            return job

        done, cached = self.idempotency.check(job.idempotency_key, job.fingerprint)
        if done:
            job.state = JobState.DONE
            job.result = cached
            return job

        while True:
            job.attempts += 1
            job.state = JobState.RUNNING
            try:
                job.result = handler(job)
            except OmnexError as exc:
                job.errors.append(f"{exc.code}: {exc.message}")
                if not exc.retryable or job.attempts >= self.policy.max_attempts:
                    job.state = JobState.DEAD
                    self.dead_letters.append(
                        DeadLetter(
                            job,
                            "permanent failure" if not exc.retryable else "retries exhausted",
                            job.attempts,
                        )
                    )
                    return job
                job.state = JobState.RETRYING
                self.clock.sleep(self.policy.delay_for(job.attempts, self.rng, exc))
            except Exception as exc:
                # An unclassified exception is a bug in the handler. Dead-letter
                # immediately rather than retrying a crash three more times.
                job.errors.append(f"{type(exc).__name__}: {exc}")
                job.state = JobState.DEAD
                self.dead_letters.append(DeadLetter(job, "handler raised", job.attempts))
                return job
            else:
                job.state = JobState.DONE
                self.idempotency.record(job.idempotency_key, job.fingerprint, job.result)
                return job

    def drain(self) -> list[Job]:
        return [self.run_once(job) for job in self.broker.pending()]

    def replay(self, dead_letter: DeadLetter) -> Job:
        """Re-run a dead letter after a fix.

        The idempotency key rides along, so replaying something that was
        actually completed on a later attempt is a no-op rather than a second
        charge — which is the failure mode of every "just re-run the DLQ" script.
        """
        self.dead_letters = [d for d in self.dead_letters if d.job.id != dead_letter.job.id]
        job = Job(
            id=dead_letter.job.id,
            kind=dead_letter.job.kind,
            payload=dead_letter.job.payload,
            idempotency_key=dead_letter.job.idempotency_key,
        )
        self.broker.jobs.append(job)
        return self.run_once(job)


def require_permanent(condition: bool, message: str, **context: Any) -> None:
    """Raise a non-retryable error. For handlers validating their input."""
    if not condition:
        raise PermanentError(message, **context)
