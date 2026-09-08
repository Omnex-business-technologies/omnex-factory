"""Sortable, prefixed identifiers.

A UUID4 is random, which means a table of traces ordered by primary key is in
no useful order, and an index on it fragments as it grows. Every id this engine
mints is instead a ULID: 48 bits of millisecond timestamp followed by 80 bits of
randomness, Crockford base32, 26 characters. Lexicographic order is
chronological order, so "the last 50 runs" is a range scan and a directory of
trace files sorts correctly with no metadata at all.

Ids are also PREFIXED — `run_01JQ…`, `span_01JQ…`, `tnt_01JQ…`. This is not
decoration. In a multi-tenant system (P10) with an audit trail (P3) and a
resume-by-id workflow (P15), the single most expensive mistake available is
passing an id of the wrong kind to a function that accepts a string. The prefix
turns that from a silent wrong-row lookup into an immediate, readable failure.

Both the clock and the randomness are injected, so a test can mint a known id
and assert on it. Determinism in id generation is what makes an audit-trail
hash chain (P3) reproducible.
"""

from __future__ import annotations

import os
import threading
from random import Random
from typing import Final

from .clock import Clock, SystemClock

__all__ = ["CROCKFORD", "IdFactory", "new_id", "parse_prefix"]

# Crockford base32: no I, L, O or U — the characters a human transcribing an id
# from a screenshot into a support ticket gets wrong.
CROCKFORD: Final = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

_TIME_CHARS = 10  # 48 bits
_RAND_CHARS = 16  # 80 bits


def _encode(value: int, length: int) -> str:
    out = [""] * length
    for i in range(length - 1, -1, -1):
        out[i] = CROCKFORD[value & 0x1F]
        value >>= 5
    return "".join(out)


class IdFactory:
    """Mints ULIDs. Thread-safe, and monotonic within a millisecond.

    Two ids minted in the same millisecond would otherwise sort arbitrarily
    against each other. Under load that is common — a trace and its first span
    are microseconds apart — and it makes a span list render out of order for
    reasons nobody can reproduce. So within a millisecond the random component
    is INCREMENTED rather than redrawn, which keeps ordering strict while
    staying unguessable.
    """

    def __init__(self, clock: Clock | None = None, rng: Random | None = None) -> None:
        self._clock = clock or SystemClock()
        self._rng = rng or Random(int.from_bytes(os.urandom(8), "big"))
        self._lock = threading.Lock()
        self._last_ms = -1
        self._last_rand = 0

    def new(self, prefix: str) -> str:
        if not prefix or not prefix.isascii() or not prefix.replace("_", "").isalnum():
            raise ValueError(f"id prefix must be short and alphanumeric, got {prefix!r}")
        ms = int(self._clock.now().timestamp() * 1000)
        with self._lock:
            if ms == self._last_ms:
                self._last_rand += 1
                # 80 bits exhausted inside one millisecond is not reachable in
                # practice, but wrapping silently would break ordering, so roll
                # the timestamp forward instead and stay correct.
                if self._last_rand >= 1 << 80:
                    ms += 1
                    self._last_ms = ms
                    self._last_rand = self._rng.getrandbits(80)
            else:
                self._last_ms = ms
                self._last_rand = self._rng.getrandbits(80)
            rand = self._last_rand
        return f"{prefix}_{_encode(ms, _TIME_CHARS)}{_encode(rand, _RAND_CHARS)}"

    def timestamp_ms_of(self, ident: str) -> int:
        """Recover the mint time from an id, for ordering checks and retention sweeps."""
        body = ident.split("_")[-1]
        if len(body) != _TIME_CHARS + _RAND_CHARS:
            raise ValueError(f"not an omnex id: {ident!r}")
        value = 0
        for ch in body[:_TIME_CHARS]:
            idx = CROCKFORD.find(ch.upper())
            if idx < 0:
                raise ValueError(f"not an omnex id: {ident!r}")
            value = (value << 5) | idx
        return value


_default = IdFactory()


def new_id(prefix: str) -> str:
    """Mint an id from the process-wide factory. Tests should use their own."""
    return _default.new(prefix)


def parse_prefix(ident: str) -> str:
    """The kind of thing an id refers to, for the wrong-kind-of-id guard."""
    head, _, tail = ident.rpartition("_")
    if not head or len(tail) != _TIME_CHARS + _RAND_CHARS:
        raise ValueError(f"not an omnex id: {ident!r}")
    return head
