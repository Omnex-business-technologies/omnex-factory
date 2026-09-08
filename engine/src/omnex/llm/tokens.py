"""Counting tokens before the provider does, and being honest that it is a guess.

A budget check has to happen BEFORE the call — afterwards is an audit, not a
control. But the exact token count is a property of a tokenizer this process
may not have, for a model it may not have downloaded, so the pre-call number is
always an estimate.

The mistake is to let that estimate pretend to be a count. Two rules keep it
honest:

**Budget and context checks use an UPPER bound, not the point estimate.** The
two errors are not symmetric. Over-estimating routes a request to a bigger
context window or refuses it slightly early — annoying, recoverable, visible.
Under-estimating means the request is dispatched, the provider rejects it for
overflowing the window (having sometimes already billed for the input), or it
sails past a spend ceiling that existed precisely to stop it. So `upper_bound()`
inflates by a margin derived from the estimator's own measured error.

**Billing never uses an estimate.** Cost is computed from the usage the provider
reported, always. The estimate exists to decide whether to make the call, and it
is discarded the moment a real count arrives — the router asserts the two are in
the same ballpark and records the drift, because a heuristic that has quietly
drifted 40% low is a budget that no longer holds.

The heuristic itself is deliberately simple and its error is measured in the
tests rather than asserted here. Roughly four characters per token holds for
English prose; code and CJK do not, and both are handled separately because the
difference is large enough to matter — CJK is close to one token per character,
which the naive rule under-counts by 3–4×.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from .types import Message

__all__ = ["HeuristicCounter", "TiktokenCounter", "TokenCounter"]

#: Per-message overhead: role markers and delimiters the provider adds around
#: content. Small, but a 40-message conversation is ~160 tokens of pure framing,
#: which is the difference between fitting a context window and not.
_MESSAGE_OVERHEAD = 4


@runtime_checkable
class TokenCounter(Protocol):
    def estimate(self, text: str) -> int:
        """Best guess at the token count."""
        ...

    def upper_bound(self, text: str) -> int:
        """A count this text is very unlikely to exceed. For budget and window checks."""
        ...


class HeuristicCounter:
    """Character-class based estimation. No dependency, no model download.

    `margin` is the inflation applied by `upper_bound`. The default of 25% is
    not a guess: it is above the worst over-run measured in
    `test_heuristic_error_stays_inside_the_stated_margin`, which is the only
    thing that makes the upper bound meaningful.
    """

    __slots__ = ("margin",)

    def __init__(self, margin: float = 0.25) -> None:
        if margin < 0:
            raise ValueError("margin must not be negative")
        self.margin = margin

    def estimate(self, text: str) -> int:
        if not text:
            return 0

        cjk = 0
        other: list[str] = []
        for ch in text:
            # CJK, Hiragana, Katakana and Hangul are roughly one token per
            # character. The 4-chars-per-token rule under-counts them 3–4×,
            # which is enough to turn a fitting request into an overflow.
            if _is_dense_script(ch):
                cjk += 1
            else:
                other.append(ch)

        rest = "".join(other)
        # Whitespace runs collapse into their neighbours rather than costing a
        # token each, so they are not counted at full weight.
        collapsed = re.sub(r"\s+", " ", rest)
        # Punctuation and digits tokenize more finely than letters do.
        punctuation = sum(1 for ch in collapsed if not ch.isalnum() and not ch.isspace())
        digits = sum(1 for ch in collapsed if ch.isdigit())
        letters = len(collapsed) - punctuation - digits

        return max(1, cjk + round(letters / 4 + digits / 2 + punctuation * 0.75))

    def upper_bound(self, text: str) -> int:
        return int(self.estimate(text) * (1 + self.margin)) + 1

    def estimate_messages(self, messages: Sequence[Message]) -> int:
        return sum(self.estimate(m.content) + _MESSAGE_OVERHEAD for m in messages)

    def upper_bound_messages(self, messages: Sequence[Message]) -> int:
        return int(self.estimate_messages(messages) * (1 + self.margin)) + 1


def _is_dense_script(ch: str) -> bool:
    try:
        name = unicodedata.name(ch)
    except ValueError:
        return False
    return name.startswith(("CJK", "HIRAGANA", "KATAKANA", "HANGUL"))


class TiktokenCounter:
    """Exact counts when `tiktoken` is installed, with the same interface.

    Still exposes `upper_bound`, with a small margin rather than none: the
    encoding used by a hosted model is not always the one available locally, and
    a bound that claims to be exact is worse than one that admits a margin.
    """

    def __init__(self, encoding: str = "cl100k_base", margin: float = 0.05) -> None:
        try:
            import tiktoken
        except ImportError as exc:  # pragma: no cover - only without the dep
            raise ImportError(
                "TiktokenCounter needs tiktoken; HeuristicCounter needs nothing"
            ) from exc
        self._enc = tiktoken.get_encoding(encoding)
        self.margin = margin

    def estimate(self, text: str) -> int:
        return len(self._enc.encode(text, disallowed_special=()))

    def upper_bound(self, text: str) -> int:
        return int(self.estimate(text) * (1 + self.margin)) + 1
