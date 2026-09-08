"""MCP — the protocol layer, and the node the corpus insists on hardest.

`corpus/universal-ai-os/BUILD_ORDER.md` ranks 111 capabilities with no code by
how many of 509 figures name them. MCP leads with 62 direct figures, more than
twice the next node, on branch XII — the one branch in the top of that queue
that exports nothing at all. This module is that result acted on, not a
preference.

What it is: JSON-RPC 2.0 over a `Transport` Protocol, standard library only,
with two positions the usual client does not take.

**A tool result is untrusted text entering a prompt.** It comes back as a
`guard.Segment` with `Provenance.UNTRUSTED`, and there is no parameter that
makes it anything else — `ToolResult` refuses to construct otherwise. A third
party's output that reaches a prompt builder as a bare `str` has the same
authority as the system prompt, and that is the whole injection surface.

**A tool result costs money.** Priced in exact pico-dollar `Money`, recorded in
`obs.CostLedger`, billed on completion whether the call succeeded or failed. An
unpriced tool is refused rather than billed at zero: zero is indistinguishable
from free, and a ledger reading €0.00 while money moves is the bug this
repository has already paid for once.

The third position lives in `server.py`: a tool that raises returns a *result*
with `isError`, never a JSON-RPC error, so the model reads what went wrong
instead of an exception handler eating it and the agent retrying forever.
"""

from .client import CLIENT_NAME, McpClient
from .protocol import (
    JSONRPC_VERSION,
    ErrorCode,
    Notification,
    Request,
    Response,
    RpcError,
    decode,
    encode,
)
from .server import PROTOCOL_VERSION, McpServer, ServerInfo
from .tools import ToolPrice, ToolResult, ToolSpec
from .transport import MemoryTransport, StreamTransport, Transport

__all__ = [
    "CLIENT_NAME",
    "JSONRPC_VERSION",
    "PROTOCOL_VERSION",
    "ErrorCode",
    "McpClient",
    "McpServer",
    "MemoryTransport",
    "Notification",
    "Request",
    "Response",
    "RpcError",
    "ServerInfo",
    "StreamTransport",
    "ToolPrice",
    "ToolResult",
    "ToolSpec",
    "Transport",
    "decode",
    "encode",
]
