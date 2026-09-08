"""Webhook ingest: verify, then enqueue, then return.

The shape matters as much as the checks. A webhook endpoint that does the work
before responding will be redelivered by the sender's own retry logic while the
first copy is still running — so the endpoint verifies, enqueues, and returns
202 in milliseconds. Everything slow happens in a worker where it can be retried
and dead-lettered.

Three verification rules, in order, each with a reason:

1. **Constant-time signature comparison.** `==` on a signature leaks its
   correct prefix through timing. The leak is small and entirely avoidable, and
   `hmac.compare_digest` costs nothing.
2. **Timestamp window.** A valid signature is valid forever without one, so a
   captured request can be replayed next year. Five minutes is the usual window.
3. **Signature over timestamp AND body.** Signing the body alone lets an
   attacker move a valid signature onto a different timestamp; signing the
   timestamp alone is worse.

The idempotency key comes from the SENDER's event id where one exists, not from
a hash of the body. Two genuinely distinct events can have identical bodies —
two identical £10 charges a second apart are two charges — and deduplicating on
body hash silently drops the second one.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, field
from typing import Any

from ..core.clock import Clock, SystemClock
from ..core.errors import PermanentError, ValidationFailed

__all__ = ["WebhookEvent", "WebhookVerifier", "verify_signature"]

#: How old a signed request may be. Long enough for a slow network and a clock
#: a little out of sync; short enough that a captured request is not a
#: long-lived credential.
DEFAULT_TOLERANCE_SECONDS = 300


def verify_signature(secret: str, timestamp: str, body: bytes, provided: str) -> bool:
    """HMAC-SHA256 over `timestamp.body`, compared in constant time."""
    signed = f"{timestamp}.".encode() + body
    expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, provided)


@dataclass(frozen=True)
class WebhookEvent:
    event_id: str
    kind: str
    payload: dict[str, Any]
    #: The sender's own id. The right idempotency key — two identical bodies
    #: can be two real events.
    idempotency_key: str = ""


@dataclass
class WebhookVerifier:
    secret: str
    clock: Clock = field(default_factory=SystemClock)
    tolerance_seconds: int = DEFAULT_TOLERANCE_SECONDS

    def verify(self, timestamp: str, body: bytes, signature: str) -> None:
        """Raise unless this request is authentic and recent."""
        if not self.secret:
            raise ValidationFailed("webhook secret is not configured")

        try:
            sent_at = int(timestamp)
        except ValueError as exc:
            raise PermanentError("webhook timestamp is not an integer", value=timestamp) from exc

        age = abs(int(self.clock.now().timestamp()) - sent_at)
        if age > self.tolerance_seconds:
            # Checked BEFORE the signature so a replayed request is rejected on
            # the cheap comparison, and so a valid old signature cannot be used
            # as an oracle for the expensive one.
            raise PermanentError(
                "webhook timestamp outside the tolerance window — possible replay",
                age_seconds=age,
                tolerance=self.tolerance_seconds,
            )

        if not verify_signature(self.secret, timestamp, body, signature):
            raise PermanentError("webhook signature does not match")

    def parse(self, body: bytes, kind_field: str = "type", id_field: str = "id") -> WebhookEvent:
        import json

        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise PermanentError("webhook body is not JSON", detail=exc.msg) from exc
        if not isinstance(payload, dict):
            raise PermanentError("webhook body is not an object")

        event_id = str(payload.get(id_field, ""))
        if not event_id:
            # Without the sender's id there is no safe idempotency key, and a
            # body hash would deduplicate two genuinely distinct events.
            raise PermanentError(f"webhook payload has no {id_field!r} to deduplicate on")

        return WebhookEvent(
            event_id=event_id,
            kind=str(payload.get(kind_field, "unknown")),
            payload=payload,
            idempotency_key=event_id,
        )
