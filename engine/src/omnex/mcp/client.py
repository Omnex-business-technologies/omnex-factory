"""The client side: correlation, provenance and money, in that order of danger.

A tool call leaves the process and comes back. Three things can go wrong on the
way, and only the first is usually handled.

**The reply may not be the reply.** Responses are correlated by id, and the
failure everybody ships is to read the next message off the stream and hand it
back. On a stream that has desynchronised — a duplicate, a late reply, a server
that answered twice — the caller then receives a confident answer to a different
question. `_exchange` refuses any id it did not send, and refuses it loudly:
dropping the message keeps the stream desynchronised and the next answer is
wrong in the same way, with nothing left in the logs.

**The reply is untrusted text about to enter a prompt.** Handled in `tools.py`;
the client never produces anything but an `UNTRUSTED` segment.

**The reply cost money.** An unpriced tool is refused rather than billed at
zero — `€0.00` is not a missing number, it is a wrong one, and it is the exact
shape of the keystone bug this repository already paid for once. Failed calls are
billed too: the work happened, and a run that spent money and failed is the one
an operator most needs to see.

Server-initiated requests are answered with `METHOD_NOT_FOUND` rather than
ignored. A server that asked something and is waiting is a server that hangs,
and the symptom lands on the wrong side of the connection.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from ..core.clock import Clock, SystemClock
from ..core.errors import (
    BudgetExceeded,
    ConfigurationError,
    PermanentError,
    ProviderError,
    TimeoutExceeded,
    ValidationFailed,
)
from ..core.money import Money
from ..obs.cost import CostEvent, CostLedger
from .protocol import (
    ErrorCode,
    Notification,
    Request,
    Response,
    RpcError,
    decode,
    encode,
)
from .server import PROTOCOL_VERSION, ServerInfo
from .tools import ToolPrice, ToolResult, ToolSpec
from .transport import Transport

__all__ = ["CLIENT_NAME", "McpClient"]

CLIENT_NAME = "omnex-mcp"


@dataclass
class McpClient:
    """One session with one server, priced and provenance-tagged throughout."""

    transport: Transport
    #: Per-tool prices. A tool absent from here cannot be called: see the module
    #: docstring for why zero is the one default this refuses to take.
    prices: dict[str, ToolPrice] = field(default_factory=dict)
    clock: Clock = field(default_factory=SystemClock)
    ledger: CostLedger | None = None
    trace_id: str = "mcp"
    tenant_id: str = ""
    timeout: float = 30.0
    #: A hard cap on what this session may spend. `None` means uncapped, which
    #: is a decision the caller makes explicitly rather than inherits.
    budget: Money | None = None
    protocol_version: str = PROTOCOL_VERSION

    _counter: int = field(default=0, init=False)
    _spent: Money = field(default_factory=Money.zero, init=False)
    _server: ServerInfo | None = field(default=None, init=False)
    _notifications: list[Notification] = field(default_factory=list, init=False)

    # ── handshake ─────────────────────────────────────────────────────────
    def initialize(self) -> ServerInfo:
        """Negotiate, and refuse a version mismatch instead of continuing hopefully.

        Two peers that disagree about the revision still exchange messages that
        parse. The disagreement surfaces later as a missing field or an absent
        capability, at which point it looks like a bug in whichever side noticed.
        """
        result = self._exchange(
            "initialize",
            {
                "protocolVersion": self.protocol_version,
                "capabilities": {},
                "clientInfo": {"name": CLIENT_NAME, "version": "1.0.0"},
            },
        )
        info = ServerInfo.from_wire(result)
        if info.protocol_version != self.protocol_version:
            raise ValidationFailed(
                "the server speaks a different MCP revision",
                wanted=self.protocol_version,
                got=info.protocol_version,
            )
        self._server = info
        self.transport.send(encode(Notification("notifications/initialized")))
        return info

    @property
    def server(self) -> ServerInfo | None:
        return self._server

    @property
    def spent(self) -> Money:
        return self._spent

    @property
    def notifications(self) -> tuple[Notification, ...]:
        """Everything the server volunteered, kept rather than discarded."""
        return tuple(self._notifications)

    # ── tools ─────────────────────────────────────────────────────────────
    def list_tools(self) -> tuple[ToolSpec, ...]:
        result = self._exchange("tools/list", {})
        return tuple(
            ToolSpec.from_wire(entry)
            for entry in result.get("tools") or []
            if isinstance(entry, dict)
        )

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> ToolResult:
        """Call one tool, price it, record it, and hand back untrusted content."""
        price = self.prices.get(name)
        if price is None:
            raise ConfigurationError(
                f"tool {name!r} has no price; billing it at zero would report a "
                "wrong number rather than a missing one",
                tool=name,
                priced=sorted(self.prices),
            )
        if self.budget is not None and self._spent + price.per_call > self.budget:
            raise BudgetExceeded(
                "the session budget cannot cover another call",
                tool=name,
                spent=str(self._spent),
                budget=str(self.budget),
            )

        result = self._exchange("tools/call", {"name": name, "arguments": arguments or {}})
        # Billed on the bytes the result actually occupies, which is also what
        # it will cost to carry in the next prompt.
        cost = price.of(len(json.dumps(result, ensure_ascii=False).encode("utf-8")))
        outcome = ToolResult.from_wire(name, result, cost)
        self._settle(name, outcome)
        return outcome

    def _settle(self, name: str, outcome: ToolResult) -> None:
        """Bill on completion — success, failure, both.

        A failed tool call spent the same compute and returns text the next
        prompt still pays to carry. Billing only successes makes the cheapest
        possible session one that fails every call, which is the wrong incentive
        to encode in a ledger.
        """
        self._spent = self._spent + outcome.cost
        if self.ledger is not None:
            self.ledger.record(
                CostEvent(
                    at=self.clock.now(),
                    trace_id=self.trace_id,
                    model=f"mcp:{name}",
                    cost=outcome.cost,
                    undiscounted=outcome.cost,
                    tenant_id=self.tenant_id,
                    route="mcp",
                )
            )

    # ── the wire ──────────────────────────────────────────────────────────
    def _next_id(self) -> str:
        self._counter += 1
        return f"{self.trace_id}-{self._counter}"

    def _exchange(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        request = Request(id=self._next_id(), method=method, params=params)
        self.transport.send(encode(request))
        deadline = self.clock.monotonic() + self.timeout

        while True:
            remaining = deadline - self.clock.monotonic()
            if remaining <= 0:
                raise TimeoutExceeded(
                    f"no reply to {method!r} within {self.timeout}s",
                    method=method,
                    request_id=request.id,
                )
            raw = self.transport.receive(remaining)
            if raw is None:
                raise TimeoutExceeded(
                    f"the transport closed while waiting for {method!r}",
                    method=method,
                    request_id=request.id,
                )

            message = decode(raw)
            if isinstance(message, Notification):
                self._notifications.append(message)
                continue
            if isinstance(message, Request):
                # Answering keeps the peer moving. Ignoring it hangs the server
                # and reports the symptom on this side of the connection.
                self.transport.send(
                    encode(
                        Response(
                            id=message.id,
                            error=RpcError(
                                ErrorCode.METHOD_NOT_FOUND,
                                f"{CLIENT_NAME} serves no requests",
                            ),
                        )
                    )
                )
                continue
            if message.id != request.id:
                raise ValidationFailed(
                    "the stream is desynchronised: a reply arrived for a request "
                    "this client did not send, and accepting the next one would "
                    "answer the wrong question confidently",
                    wanted=request.id,
                    got=message.id,
                )
            if message.error is not None:
                raise _as_error(method, message.error)
            return message.result or {}


def _as_error(method: str, error: RpcError) -> Exception:
    """Map a protocol error onto the taxonomy the rest of the engine retries on.

    `INTERNAL_ERROR` is the only one worth another attempt: the others describe
    a message that will be exactly as wrong the second time, and retrying them
    spends the budget to learn nothing.
    """
    context = {"method": method, "code": int(error.code), **error.data}
    if error.code is ErrorCode.INTERNAL_ERROR:
        return ProviderError(error.message, provider="mcp", **context)
    if error.code is ErrorCode.PARSE_ERROR:
        return ValidationFailed(error.message, **context)
    return PermanentError(error.message, **context)
