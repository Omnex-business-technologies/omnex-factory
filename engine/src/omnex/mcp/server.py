"""The server side, and the one distinction that decides whether an agent recovers.

## A tool that fails is a RESULT, not a protocol error

This is the mistake worth building the module around. When a tool raises, the
obvious move is to return a JSON-RPC error — the call did fail, after all. Every
client then treats it the way it treats a malformed message: it raises, the
exception unwinds past the agent loop, and **the model never sees what went
wrong**. So the agent retries the identical call, gets the identical failure, and
burns the budget in a loop that cannot learn anything, because the one piece of
information that would let it adapt was consumed by an exception handler.

A JSON-RPC error means *this message was wrong*: unknown method, bad params,
broken frame. A tool that ran and refused means *the world said no*, and that is
content the model must read — "the currency code EURO is not valid, use EUR" is
a sentence an agent recovers from immediately.

So: protocol failures become `RpcError`. Tool failures become a normal result
with `isError` set and the exception text as content. `handle()` never lets a
tool exception escape, because a server that dies on a bad argument takes the
session with it.

## Ordering is enforced

`tools/call` before `initialize` is refused. Capability negotiation is the point
of the handshake; a client that skips it is running against assumptions about a
server it has not spoken to, and the failure surfaces later as a missing tool.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ..core.errors import ConfigurationError, ValidationFailed
from ..guard.ratelimit import RateLimit, RateLimiter
from .protocol import (
    ErrorCode,
    Notification,
    Request,
    Response,
    RpcError,
    decode,
    encode,
)
from .tools import ToolSpec
from .transport import Transport

__all__ = ["PROTOCOL_VERSION", "McpServer", "ServerInfo"]

#: The revision this implementation speaks. It is negotiated rather than
#: assumed: `initialize` returns it, and the client refuses a server that
#: answers with something else instead of continuing hopefully.
PROTOCOL_VERSION = "2025-06-18"

#: A handler takes the decoded arguments and returns text or a content payload.
Handler = Callable[[dict[str, Any]], Any]


@dataclass(frozen=True)
class ServerInfo:
    """Who answered the handshake, and what they admit to supporting."""

    name: str
    version: str
    protocol_version: str
    capabilities: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_wire(cls, payload: dict[str, Any]) -> ServerInfo:
        info = payload.get("serverInfo") or {}
        return cls(
            name=str(info.get("name", "")),
            version=str(info.get("version", "")),
            protocol_version=str(payload.get("protocolVersion", "")),
            capabilities=payload.get("capabilities") or {},
        )


class McpServer:
    """Registers tools and answers messages. Owns no transport of its own."""

    def __init__(
        self, name: str, version: str = "0.1.0", *, protocol_version: str = PROTOCOL_VERSION
    ) -> None:
        self.name = name
        self.version = version
        self.protocol_version = protocol_version
        self._specs: dict[str, ToolSpec] = {}
        self._handlers: dict[str, Handler] = {}
        self._limiters: dict[str, RateLimiter] = {}
        self._initialized = False

    # ── registration ──────────────────────────────────────────────────────
    def tool(
        self,
        name: str,
        description: str = "",
        input_schema: dict[str, Any] | None = None,
        *,
        required_permission: str | None = None,
        timeout_seconds: float | None = None,
        dangerous: bool = False,
        rate_limit: RateLimit | None = None,
    ) -> Callable[[Handler], Handler]:
        """Register one tool. Re-registering a name is refused, not overwritten.

        Silent replacement is how two versions of a tool end up in one process
        and the one that answers depends on import order.

        `rate_limit`, when given, gets its own `RateLimiter` keyed by tool
        name — reusing `guard.ratelimit`'s GCRA implementation rather than a
        second one, per this repository's own `one_symbol_resolver` /
        `twin_splitters_agree` rule against duplicate implementations of the
        same thing. `timeout_seconds` and `dangerous` are stored on the
        `ToolSpec`; see its docstring for what each means and, for
        `timeout_seconds`, what kind of bound `_call` actually enforces.
        """

        def register(handler: Handler) -> Handler:
            if name in self._handlers:
                raise ConfigurationError(f"tool {name!r} is already registered", tool=name)
            self._specs[name] = ToolSpec(
                name,
                description,
                input_schema or {},
                required_permission,
                timeout_seconds,
                dangerous,
            )
            self._handlers[name] = handler
            if rate_limit is not None:
                self._limiters[name] = RateLimiter(rate_limit)
            return handler

        return register

    @property
    def tools(self) -> tuple[ToolSpec, ...]:
        return tuple(self._specs[name] for name in sorted(self._specs))

    def available_to(self, granted: frozenset[str] | None) -> tuple[ToolSpec, ...]:
        """The tools one caller may see. `None` grant means unrestricted.

        Unrestricted-by-default is what keeps every existing caller of this
        server — every test, every server that never opted into scoping —
        seeing exactly the tool list it always saw. A caller only loses tools
        once it is handed an actual (possibly empty) granted set.
        """
        if granted is None:
            return self.tools
        return tuple(
            t
            for t in self.tools
            if t.required_permission is None or t.required_permission in granted
        )

    @property
    def initialized(self) -> bool:
        return self._initialized

    # ── dispatch ──────────────────────────────────────────────────────────
    def handle(self, raw: str, *, granted: frozenset[str] | None = None) -> str | None:
        """Answer one message. None means there is nothing to send back.

        `granted` names the permissions the caller on the other end of this
        message actually holds. It is `None` by default — unrestricted,
        matching every server's behaviour before scoping existed — because a
        transport that never passes a caller identity has not opted into
        scoping and must not be silently narrowed by it.
        """
        try:
            message = decode(raw)
        except ValidationFailed as exc:
            return encode(
                Response(id="", error=RpcError(ErrorCode.PARSE_ERROR, exc.message, exc.context))
            )

        if isinstance(message, Notification):
            self._on_notification(message)
            return None
        if isinstance(message, Response):
            # A server does not receive responses to requests it never sent.
            return encode(
                Response(
                    id=message.id,
                    error=RpcError(ErrorCode.INVALID_REQUEST, "this peer sends no requests"),
                )
            )
        return encode(self._on_request(message, granted))

    def _on_notification(self, message: Notification) -> None:
        if message.method == "notifications/initialized":
            self._initialized = True

    def _on_request(self, request: Request, granted: frozenset[str] | None) -> Response:
        if request.method == "initialize":
            self._initialized = True
            return Response(id=request.id, result=self._handshake())
        if request.method == "tools/list":
            return self._require_handshake(request) or Response(
                id=request.id,
                result={"tools": [spec.as_dict() for spec in self.available_to(granted)]},
            )
        if request.method == "tools/call":
            return self._require_handshake(request) or self._call(request, granted)
        if request.method == "ping":
            return Response(id=request.id, result={})
        return Response(
            id=request.id,
            error=RpcError(ErrorCode.METHOD_NOT_FOUND, f"unknown method {request.method!r}"),
        )

    def _handshake(self) -> dict[str, Any]:
        return {
            "protocolVersion": self.protocol_version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": self.name, "version": self.version},
        }

    def _require_handshake(self, request: Request) -> Response | None:
        if self._initialized:
            return None
        return Response(
            id=request.id,
            error=RpcError(
                ErrorCode.INVALID_REQUEST,
                "initialize has not been called; capability negotiation is the "
                "point of the handshake and skipping it runs the session against "
                "assumptions about a server nobody has spoken to",
            ),
        )

    def _call(self, request: Request, granted: frozenset[str] | None = None) -> Response:
        name = request.params.get("name")
        allowed = {spec.name for spec in self.available_to(granted)}
        if not isinstance(name, str) or name not in self._handlers or name not in allowed:
            # A tool this caller lacks the permission for is refused with the
            # exact same error as a tool that does not exist — never
            # "permission denied". Naming a scoped tool's existence to a
            # caller who cannot use it discloses a capability for free; the
            # `available` list already reflects only what this caller may see.
            return Response(
                id=request.id,
                error=RpcError(
                    ErrorCode.INVALID_PARAMS,
                    f"no tool named {name!r}",
                    {"available": sorted(allowed)},
                ),
            )
        arguments = request.params.get("arguments") or {}
        if not isinstance(arguments, dict):
            return Response(
                id=request.id,
                error=RpcError(ErrorCode.INVALID_PARAMS, "arguments must be an object"),
            )

        limiter = self._limiters.get(name)
        if limiter is not None:
            decision = limiter.check(name)
            if not decision.allowed:
                # A rate limit is the world saying "not yet", not a broken
                # message — the same "tool that fails is a RESULT" rule this
                # module is built around (see the module docstring), applied
                # to a rejection this server issued rather than one the
                # handler raised.
                return Response(
                    id=request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    f"rate limit exceeded for {name!r}; "
                                    f"retry after {decision.retry_after:.3f}s"
                                ),
                            }
                        ],
                        "isError": True,
                    },
                )

        timeout = self._specs[name].timeout_seconds
        try:
            if timeout is None:
                produced = self._handlers[name](arguments)
            else:
                produced = self._call_bounded(name, arguments, timeout)
        except _HandlerTimedOut:
            # A bound on how long THIS caller waits, not a preemptive kill of
            # the handler thread — the same honest limitation
            # `mcp.transport.StreamTransport.receive()` and `guard.sandbox`'s
            # module docstring already document for an in-process deadline: a
            # `Clock` cannot be injected into a running thread, so nothing at
            # this layer can actually stop a genuinely hung handler, only stop
            # waiting for it. `guard.sandbox`'s `subprocess.run(timeout=...)`
            # is the stronger, OS-level guarantee, and is a different
            # mechanism for a different case (an external process, not an
            # in-process callable).
            return Response(
                id=request.id,
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"tool {name!r} did not return within {timeout}s; "
                                "the call is abandoned but the handler may still "
                                "be running"
                            ),
                        }
                    ],
                    "isError": True,
                },
            )
        except Exception as exc:  # every exception — see the module docstring
            # Every exception, including ones this package did not define. A
            # third-party tool raising something unexpected must reach the model
            # as text, not kill the session it was serving.
            return Response(
                id=request.id,
                result={
                    "content": [{"type": "text", "text": f"{type(exc).__name__}: {exc}"}],
                    "isError": True,
                },
            )
        return Response(id=request.id, result=_as_content(produced))

    def _call_bounded(self, name: str, arguments: dict[str, Any], timeout: float) -> Any:
        """Run a handler on a worker thread and wait at most `timeout` seconds.

        Bounds the caller's wait; does not bound the handler. See the
        `_HandlerTimedOut` branch in `_call` for why that distinction is
        honestly documented rather than papered over.
        """
        outcome: dict[str, Any] = {}

        def run() -> None:
            try:
                outcome["result"] = self._handlers[name](arguments)
            except BaseException as exc:  # re-raised on the caller's thread
                outcome["error"] = exc

        worker = threading.Thread(target=run, daemon=True)
        worker.start()
        worker.join(timeout)
        if worker.is_alive():
            raise _HandlerTimedOut(name)
        if "error" in outcome:
            raise outcome["error"]
        return outcome.get("result")

    # ── serving ───────────────────────────────────────────────────────────
    def loopback(self) -> Transport:
        """A transport that runs this server in-process, synchronously.

        Not a test double. It is the real dispatch path with the operating
        system removed, which is what makes it worth using in tests: a stub that
        returns canned replies verifies the stub. It is also a genuine
        deployment shape — a server you wrote and a client you wrote, in one
        process, with no reason to serialise through a pipe.
        """
        return _Loopback(self)

    def serve(
        self,
        transport: Transport,
        *,
        timeout: float = 30.0,
        limit: int = 0,
        granted: frozenset[str] | None = None,
    ) -> int:
        """Read, answer, repeat, until the peer goes quiet.

        `limit` bounds the number of messages handled and exists so a test can
        run the real loop rather than a reimplementation of it. Zero means no
        bound. `granted` is fixed for the whole session, matching one
        transport connection belonging to one caller — a caller who needs a
        different grant reconnects rather than re-authenticating mid-stream.
        """
        handled = 0
        while not limit or handled < limit:
            raw = transport.receive(timeout)
            if raw is None:
                break
            reply = self.handle(raw, granted=granted)
            handled += 1
            if reply is not None:
                transport.send(reply)
        return handled


class _HandlerTimedOut(Exception):
    """Internal signal: `_call_bounded`'s wait expired. Never reaches a caller."""


class _Loopback:
    """One end of a channel whose other end is a server that answers immediately."""

    def __init__(self, server: McpServer) -> None:
        self._server = server
        self._inbox: list[str] = []

    def send(self, message: str) -> None:
        reply = self._server.handle(message)
        if reply is not None:
            self._inbox.append(reply)

    def receive(self, timeout: float) -> str | None:
        """`timeout` is accepted and unused: the reply is already here."""
        return self._inbox.pop(0) if self._inbox else None

    def close(self) -> None:
        self._inbox.clear()


def _as_content(produced: Any) -> dict[str, Any]:
    """Accept a string, a content payload, or anything else, without guessing wrongly."""
    if isinstance(produced, dict) and "content" in produced:
        return produced
    return {"content": [{"type": "text", "text": str(produced)}], "isError": False}
