"""P16 — agentic automation: webhooks, async execution, idempotency, dead letters.

An idempotency key covers the PAYLOAD as well as the key: the usual
implementation returns a cached result for a repeated key, which is right for a
retry and catastrophic for a caller that reused a key with a different body.
Dead letters keep everything needed to replay — a DLQ holding only error
messages is a list of things you know broke and cannot retry.

`IdempotencyStore` and `Claims` solve the same problem at different lifetimes.
The store is a dict, correct for a worker that stays up. `Claims` is a directory,
because the shape an n8n workflow has is a command that runs and exits, where an
in-memory store starts empty on every redelivery and deduplicates nothing.
`python -m omnex.pipeline` is the CLI those workflow nodes call.
"""

from .claim import Claimed, Claims
from .queue import (
    DeadLetter,
    IdempotencyStore,
    InMemoryBroker,
    Job,
    JobState,
    Worker,
    payload_hash,
)
from .webhook import WebhookEvent, WebhookVerifier, verify_signature

__all__ = [
    "Claimed",
    "Claims",
    "DeadLetter",
    "IdempotencyStore",
    "InMemoryBroker",
    "Job",
    "JobState",
    "WebhookEvent",
    "WebhookVerifier",
    "Worker",
    "payload_hash",
    "verify_signature",
]
