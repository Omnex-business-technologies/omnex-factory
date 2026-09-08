"""What a tool is, what it costs, and what its result is allowed to be.

Two things go wrong in almost every MCP client, and both are cheap to fix here
and expensive to fix later.

## A tool result is untrusted text entering a prompt

An MCP server is a third party. Its results are fetched pages, database rows,
another vendor's API — exactly the category `guard.Provenance.UNTRUSTED` exists
for. The usual client hands back a `str`, it goes through two helper functions,
and it reaches the prompt builder indistinguishable from something the developer
wrote. At that point an injected instruction in a tool result has the same
authority as the system prompt.

So `ToolResult` carries a `guard.Segment`, and there is **no parameter that
makes it trusted**. `__post_init__` refuses any other provenance, so even
constructing one directly cannot produce a trusted tool result. That is
structural rather than conventional on purpose: a convention holds until
somebody is in a hurry.

## A tool result costs money

A tool call spends — the server's compute, the API behind it, and the tokens the
result occupies in the next prompt. The keystone bug in the root app was a
missing `usage` block, which made every cost panel read €0.00 while real money
moved; the same shape appears here as a tool with no price.

An unpriced tool is therefore **refused, not billed at zero**. Zero is the
dangerous default because it is indistinguishable from free, and a client whose
ledger says zero is not missing a number — it is reporting a wrong one.

Prices are exact `Money` in pico-dollars for the reason in `core/money.py`: a
tool returning two kilobytes at a plausible rate rounds to zero in micro-dollars,
so the fee schedule that saves money reports saving nothing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..core.errors import ValidationFailed
from ..core.money import Money
from ..guard.injection import Provenance, Segment

__all__ = ["ToolPrice", "ToolResult", "ToolSpec"]

#: Result size is billed per kibibyte, rounded UP. A fractional charge is not
#: representable in whole picos at plausible rates, and rounding down bills a
#: 900-byte result at nothing.
BYTES_PER_UNIT = 1024


@dataclass(frozen=True)
class ToolSpec:
    """What a server says it can do. The schema is the server's claim, not ours."""

    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValidationFailed("a tool needs a name")

    @classmethod
    def from_wire(cls, payload: dict[str, Any]) -> ToolSpec:
        return cls(
            name=str(payload.get("name", "")),
            description=str(payload.get("description", "")),
            input_schema=payload.get("inputSchema") or {},
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


@dataclass(frozen=True)
class ToolPrice:
    """What one call to one tool costs, in exact pico-dollars.

    Split into a per-call and a per-kibibyte term because the two behave
    differently under load: a chatty tool called constantly is dominated by the
    first, and one tool returning a whole document is dominated by the second.
    Collapsing them into one number hides whichever is actually the bill.
    """

    per_call: Money = field(default_factory=Money.zero)
    per_kib: Money = field(default_factory=Money.zero)

    def __post_init__(self) -> None:
        if self.per_call.picos < 0 or self.per_kib.picos < 0:
            raise ValidationFailed(
                "a negative price is a credit, and this is not a refund path",
                per_call=str(self.per_call),
                per_kib=str(self.per_kib),
            )

    def of(self, result_bytes: int) -> Money:
        units = -(-max(result_bytes, 0) // BYTES_PER_UNIT)
        return self.per_call + self.per_kib * units


@dataclass(frozen=True)
class ToolResult:
    """What a tool returned, as untrusted content with a price on it.

    `is_error` is a tool-level failure — the tool ran and said no. It is not a
    protocol error, and the distinction is load-bearing: see `server.py`.
    """

    tool: str
    segment: Segment
    cost: Money
    is_error: bool = False
    #: The raw result object, kept for callers that need the structured form.
    #: Reading text out of here bypasses the provenance the segment carries, so
    #: it is named to make that visible at the call site.
    raw_untrusted: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.segment.provenance is not Provenance.UNTRUSTED:
            raise ValidationFailed(
                "a tool result is third-party content and may never be trusted; "
                "there is no path that marks one otherwise",
                tool=self.tool,
                provenance=str(self.segment.provenance),
            )

    @property
    def text(self) -> str:
        """The result text. Still untrusted — the segment is what a prompt takes."""
        return self.segment.text

    @classmethod
    def from_wire(
        cls, tool: str, payload: dict[str, Any], cost: Money, *, source: str = ""
    ) -> ToolResult:
        """Flatten MCP's content blocks into one untrusted segment.

        Non-text blocks (images, embedded resources) are named rather than
        dropped: a result that silently loses half its content is a result the
        model answers from anyway, and the answer looks fine.
        """
        parts: list[str] = []
        for block in payload.get("content") or []:
            if not isinstance(block, dict):
                continue
            kind = block.get("type", "")
            if kind == "text":
                parts.append(str(block.get("text", "")))
            else:
                parts.append(f"[{kind or 'unknown'} content not rendered as text]")
        return cls(
            tool=tool,
            segment=Segment(
                text="\n".join(parts),
                provenance=Provenance.UNTRUSTED,
                source=source or f"mcp:{tool}",
            ),
            cost=cost,
            is_error=bool(payload.get("isError")),
            raw_untrusted=payload,
        )
