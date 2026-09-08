"""JSON-RPC 2.0, the subset MCP speaks, with the framing mistakes made loud.

The wire format is small enough that everybody writes their own, and the bugs
are consequently the same everywhere. Three of them are structural here rather
than documented:

**A notification has no id and never gets a reply.** A client that sends one and
then waits for a response hangs forever, and the symptom — "the server stopped
responding" — points at the wrong process. `Notification` is a separate type
from `Request` so a caller cannot await one by accident: there is no id to
correlate on, and `expects_reply` says so.

**A response id that matches nothing is an error, not a message to drop.** The
tempting handling is to ignore it and keep reading. That turns a desynchronised
stream into a silent one, and the next response — belonging to some other
request — gets handed to a caller that will accept it happily because it has the
shape it expected. Answering the wrong question confidently is the failure mode
this whole package is built against.

**A batch is refused, not partially honoured.** JSON-RPC allows an array of
messages; MCP does not use it. A decoder that quietly takes `payload[0]` gives
back a plausible answer to one of several questions and drops the rest without
a trace, so this raises instead.

Codes are the JSON-RPC standard ones. `ErrorCode.TOOL_FAILED` is deliberately
NOT among them — see `server.py` for why a tool that raises is a *result*, not a
protocol error.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

from ..core.errors import ValidationFailed

__all__ = [
    "JSONRPC_VERSION",
    "ErrorCode",
    "Notification",
    "Request",
    "Response",
    "RpcError",
    "decode",
    "encode",
]

JSONRPC_VERSION = "2.0"


class ErrorCode(IntEnum):
    """The JSON-RPC standard codes, and nothing invented alongside them.

    A private code range exists (-32099..-32000) and is left empty on purpose:
    every failure this package produces is either a protocol failure, which is
    one of these, or a tool failure, which is not a protocol failure at all.
    """

    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


@dataclass(frozen=True)
class RpcError:
    """A protocol-level failure, as it travels on the wire."""

    code: ErrorCode
    message: str
    data: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"code": int(self.code), "message": self.message}
        if self.data:
            out["data"] = self.data
        return out


@dataclass(frozen=True)
class Request:
    """A call that expects exactly one reply, correlated by `id`."""

    id: str
    method: str
    params: dict[str, Any] = field(default_factory=dict)

    #: Kept as a property rather than a constant so the two message types answer
    #: the same question and a caller can branch on the answer, not on the type.
    @property
    def expects_reply(self) -> bool:
        return True

    def as_dict(self) -> dict[str, Any]:
        return {
            "jsonrpc": JSONRPC_VERSION,
            "id": self.id,
            "method": self.method,
            "params": self.params,
        }


@dataclass(frozen=True)
class Notification:
    """A one-way message. Waiting for a reply to one of these is a hang."""

    method: str
    params: dict[str, Any] = field(default_factory=dict)

    @property
    def expects_reply(self) -> bool:
        return False

    def as_dict(self) -> dict[str, Any]:
        return {"jsonrpc": JSONRPC_VERSION, "method": self.method, "params": self.params}


@dataclass(frozen=True)
class Response:
    """The reply to one `Request`, carrying a result or an error, never both.

    An empty `id` serialises as JSON-RPC's null id, which is what a peer must
    answer with when the request was so malformed that no id could be read from
    it. It is terminal by construction: nothing can correlate it, so `decode`
    refuses to parse one back rather than handing a caller a reply to a question
    it cannot identify.
    """

    id: str
    result: dict[str, Any] | None = None
    error: RpcError | None = None

    def __post_init__(self) -> None:
        if (self.result is None) == (self.error is None):
            raise ValidationFailed(
                "a response carries exactly one of result or error",
                id=self.id,
                has_result=self.result is not None,
                has_error=self.error is not None,
            )

    @property
    def ok(self) -> bool:
        return self.error is None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"jsonrpc": JSONRPC_VERSION, "id": self.id or None}
        if self.error is not None:
            out["error"] = self.error.as_dict()
        else:
            out["result"] = self.result
        return out


Message = Request | Notification | Response


def encode(message: Message) -> str:
    """One message, one line of JSON.

    `ensure_ascii=False` because tool arguments carry human text and escaping it
    to `\\uXXXX` triples the byte count of anything not in English — which is
    paid for on every call, in both directions, forever.
    """
    return json.dumps(message.as_dict(), ensure_ascii=False, separators=(",", ":"))


def decode(raw: str) -> Message:
    """Parse one message, refusing everything ambiguous.

    Every refusal here is a case where the permissive reading produces a message
    that looks usable. That is the whole reason the function is strict: a
    malformed message that raises costs one traceback, and a malformed message
    that parses costs a wrong answer nobody can trace.
    """
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValidationFailed(f"not JSON: {exc}", excerpt=raw[:120]) from exc

    if isinstance(payload, list):
        raise ValidationFailed(
            "JSON-RPC batches are not supported by MCP, and taking the first "
            "element would answer one question and silently drop the rest",
            count=len(payload),
        )
    if not isinstance(payload, dict):
        raise ValidationFailed(f"a message is an object, got {type(payload).__name__}")
    if payload.get("jsonrpc") != JSONRPC_VERSION:
        raise ValidationFailed(f"jsonrpc must be {JSONRPC_VERSION!r}", got=payload.get("jsonrpc"))

    has_id = "id" in payload and payload["id"] is not None
    if "method" in payload:
        method = payload["method"]
        if not isinstance(method, str) or not method:
            raise ValidationFailed("method must be a non-empty string", got=method)
        params = payload.get("params") or {}
        if not isinstance(params, dict):
            raise ValidationFailed("params must be an object", got=type(params).__name__)
        if has_id:
            return Request(id=str(payload["id"]), method=method, params=params)
        return Notification(method=method, params=params)

    if not has_id:
        raise ValidationFailed("a response must carry the id of the request it answers")

    if "error" in payload:
        error = payload["error"]
        if not isinstance(error, dict) or "code" not in error:
            raise ValidationFailed("an error must be an object with a code", got=error)
        try:
            code = ErrorCode(int(error["code"]))
        except ValueError:
            # An unknown code is still a failure; mapping it to INTERNAL_ERROR
            # keeps the original in `data` rather than discarding what the peer
            # actually said.
            code = ErrorCode.INTERNAL_ERROR
        raw_data = error.get("data")
        data: dict[str, Any] = raw_data if isinstance(raw_data, dict) else {}
        return Response(
            id=str(payload["id"]),
            error=RpcError(
                code=code,
                message=str(error.get("message", "")),
                data={**data, "wire_code": error["code"]},
            ),
        )

    if "result" not in payload:
        raise ValidationFailed("a response carries a result or an error", id=payload["id"])
    result = payload["result"]
    if not isinstance(result, dict):
        raise ValidationFailed("result must be an object", got=type(result).__name__)
    return Response(id=str(payload["id"]), result=result)
