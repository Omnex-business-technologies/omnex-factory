"""How messages move, kept behind a Protocol so the client never learns.

MCP runs over stdio, over HTTP with server-sent events, and over whatever a host
invents next. The client below knows none of that: it sends a string and reads a
string, and every transport concern — framing, buffering, process lifetime —
lives here.

That boundary is not tidiness. It is what makes the client testable without a
subprocess: `MemoryTransport.pair()` is a real transport with real framing, so
the tests exercise the same code path a stdio server does, minus the operating
system. A test suite that can only reach the client through a spawned process
tests the process spawner.

**Framing is newline-delimited JSON**, one message per line. The invariant that
makes it safe is that `protocol.encode` produces JSON with no raw newline —
`json.dumps` escapes them inside strings — so a message can never split itself
across two frames. `test_an_encoded_message_never_contains_a_raw_newline` guards
that, because the day it stops being true this transport silently truncates
every message containing a newline and delivers the remainder as garbage.
"""

from __future__ import annotations

import contextlib
from collections import deque
from typing import IO, Protocol

from ..core.clock import Clock, SystemClock
from ..core.errors import PermanentError

__all__ = ["MemoryTransport", "StreamTransport", "Transport"]


class Transport(Protocol):
    """A bidirectional line channel. Everything above this speaks strings."""

    def send(self, message: str) -> None:
        """Write one message. Raises `PermanentError` if the peer is gone."""
        ...

    def receive(self, timeout: float) -> str | None:
        """Read one message, or None if `timeout` seconds pass with nothing."""
        ...

    def close(self) -> None: ...


class MemoryTransport:
    """Two ends of a channel in one process, with real framing.

    Used by tests and by an in-process server. `pair()` returns both ends
    already crossed over, because wiring them by hand is a mistake that produces
    a transport talking to itself — which passes a surprising number of tests.
    """

    def __init__(self, *, clock: Clock | None = None) -> None:
        self._clock: Clock = clock or SystemClock()
        self._inbox: deque[str] = deque()
        self._peer: MemoryTransport | None = None
        self._closed = False

    @classmethod
    def pair(cls, *, clock: Clock | None = None) -> tuple[MemoryTransport, MemoryTransport]:
        left, right = cls(clock=clock), cls(clock=clock)
        left._peer, right._peer = right, left
        return left, right

    def send(self, message: str) -> None:
        if self._closed or self._peer is None or self._peer._closed:
            raise PermanentError("the transport is closed", transport="memory")
        if "\n" in message:
            raise PermanentError("a framed message may not contain a newline", transport="memory")
        self._peer._inbox.append(message)

    def receive(self, timeout: float) -> str | None:
        """Poll until something arrives or the deadline passes.

        Polling rather than blocking because both ends live on one thread: a
        blocking read here would deadlock against a peer that has not been given
        a turn to send yet.
        """
        deadline = self._clock.monotonic() + max(timeout, 0.0)
        while True:
            if self._inbox:
                return self._inbox.popleft()
            if self._clock.monotonic() >= deadline:
                return None
            self._clock.sleep(0.001)

    def close(self) -> None:
        self._closed = True

    @property
    def pending(self) -> int:
        return len(self._inbox)


class StreamTransport:
    """Newline-delimited JSON over any pair of text streams, stdio included.

    `timeout` is accepted and not enforced inside the read: a blocking
    `readline()` is the operating system's to interrupt, not this object's, and
    a Clock cannot be injected into it. Pretending otherwise — sleeping in a
    loop around a blocking call — produces a timeout that fires only after the
    read it was meant to bound has already returned. So the parameter is
    documented as advisory here and the deadline is enforced by whoever owns the
    process, which is the only layer that can actually kill it.
    """

    def __init__(self, reader: IO[str], writer: IO[str]) -> None:
        self._reader = reader
        self._writer = writer

    def send(self, message: str) -> None:
        if "\n" in message:
            raise PermanentError("a framed message may not contain a newline", transport="stream")
        try:
            self._writer.write(message + "\n")
            self._writer.flush()
        except (BrokenPipeError, ValueError) as exc:
            # A dead peer process does not come back on a retry, so this is
            # permanent rather than a transient network hiccup.
            raise PermanentError(f"the peer is gone: {exc}", transport="stream") from exc

    def receive(self, timeout: float) -> str | None:
        line = self._reader.readline()
        if not line:
            return None
        return line.rstrip("\n")

    def close(self) -> None:
        for stream in (self._reader, self._writer):
            # Already-closed streams are the normal case on a second close.
            with contextlib.suppress(OSError, ValueError):
                stream.close()
