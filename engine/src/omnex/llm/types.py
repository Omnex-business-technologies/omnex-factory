"""The value types every model call passes through.

Small file, but two decisions in it propagate everywhere.

`Usage` reports `cached_input_tokens` as a SUBSET of `input_tokens`, matching how
providers actually report it. Treating it as an addition inflates the recorded
cost of exactly the requests a cache was supposed to make cheap, which then
makes prompt caching look useless in the very dashboard you would use to justify
it.

`Completion` carries the `finish_reason` as a typed value rather than the
provider's raw string. `length` — the model hitting `max_tokens` mid-sentence —
is not an error and does not raise, so it is the single easiest failure to ship:
the answer looks fine, is silently truncated, and any downstream parser sees
malformed JSON with no explanation. Making it a distinct enum member means
callers must think about it, and the eval harness (P4) can count it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Literal

from ..core.money import Money

__all__ = ["Completion", "FinishReason", "Message", "Role", "Usage"]

Role = Literal["system", "user", "assistant", "tool"]


class FinishReason(StrEnum):
    STOP = "stop"
    #: Hit max_tokens. Not an error, and that is precisely the danger.
    LENGTH = "length"
    TOOL_CALL = "tool_call"
    CONTENT_FILTER = "content_filter"
    ERROR = "error"


@dataclass(frozen=True)
class Message:
    role: Role
    content: str
    name: str = ""

    def as_dict(self) -> dict[str, str]:
        out = {"role": self.role, "content": self.content}
        if self.name:
            out["name"] = self.name
        return out


@dataclass(frozen=True)
class Usage:
    """Token counts as the provider reported them, never as we estimated them."""

    input_tokens: int = 0
    output_tokens: int = 0
    #: A subset of `input_tokens`, not an addition.
    cached_input_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cache_hit_ratio(self) -> float:
        return 0.0 if not self.input_tokens else self.cached_input_tokens / self.input_tokens

    def __add__(self, other: Usage) -> Usage:
        return Usage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cached_input_tokens=self.cached_input_tokens + other.cached_input_tokens,
        )


@dataclass(frozen=True)
class Completion:
    """One model response, with everything needed to bill and judge it."""

    text: str
    model: str
    usage: Usage
    cost: Money
    #: What this call would have cost on the reference model with no cache. The
    #: router's savings claim is the difference, recorded at the time — after the
    #: fact it is unprovable, which is how cost work turns into an assertion.
    undiscounted: Money
    finish_reason: FinishReason = FinishReason.STOP
    latency_seconds: float = 0.0
    provider: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def truncated(self) -> bool:
        return self.finish_reason is FinishReason.LENGTH

    @property
    def saved(self) -> Money:
        return self.undiscounted - self.cost
