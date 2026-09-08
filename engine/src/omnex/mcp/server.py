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

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ..core.errors import ConfigurationError, ValidationFailed
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
        self._initialized = False

    # ── registration ──────────────────────────────────────────────────────
    def tool(
        self, name: str, description: str = "", input_schema: dict[str, Any] | None = None
    ) -> Callable[[Handler], Handler]:
        """Register one tool. Re-registering a name is refused, not overwritten.

        Silent replacement is how two versions of a tool end up in one process
        and the one that answers depends on import order.
        """

        def register(handler: Handler) -> Handler:
            if name in self._handlers:
                raise ConfigurationError(f"tool {name!r} is already registered", tool=name)
            self._specs[name] = ToolSpec(name, description, input_schema or {})
            self._handlers[name] = handler
            return handler

        return register

    @property
    def tools(self) -> tuple[ToolSpec, ...]:
        return tuple(self._specs[name] for name in sorted(self._specs))

    @property
    def initialized(self) -> bool:
        return self._initialized

    # ── dispatch ──────────────────────────────────────────────────────────
    def handle(self, raw: str) -> str | None:
        """Answer one message. None means there is nothing to send back."""
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
        return encode(self._on_request(message))

    def _on_notification(self, message: Notification) -> None:
        if message.method == "notifications/initialized":
            self._initialized = True

    def _on_request(self, request: Request) -> Response:
        if request.method == "initialize":
            self._initialized = True
            return Response(id=request.id, result=self._handshake())
        if request.method == "tools/list":
            return self._require_handshake(request) or Response(
                id=request.id, result={"tools": [spec.as_dict() for spec in self.tools]}
            )
        if request.method == "tools/call":
            return self._require_handshake(request) or self._call(request)
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

    def _call(self, request: Request) -> Response:
        name = request.params.get("name")
        if not isinstance(name, str) or name not in self._handlers:
            return Response(
                id=request.id,
                error=RpcError(
                    ErrorCode.INVALID_PARAMS,
                    f"no tool named {name!r}",
                    {"available": sorted(self._handlers)},
                ),
            )
        arguments = request.params.get("arguments") or {}
        if not isinstance(arguments, dict):
            return Response(
                id=request.id,
                error=RpcError(ErrorCode.INVALID_PARAMS, "arguments must be an object"),
            )
        try:
            produced = self._handlers[name](arguments)
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

    def serve(self, transport: Transport, *, timeout: float = 30.0, limit: int = 0) -> int:
        """Read, answer, repeat, until the peer goes quiet.

        `limit` bounds the number of messages handled and exists so a test can
        run the real loop rather than a reimplementation of it. Zero means no
        bound.
        """
        handled = 0
        while not limit or handled < limit:
            raw = transport.receive(timeout)
            if raw is None:
                break
            reply = self.handle(raw)
            handled += 1
            if reply is not None:
                transport.send(reply)
        return handled


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
