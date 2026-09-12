"""Separating a reasoning model's thinking from its answer.

`Tier.REASONING` is the router's top escalation tier (`catalog._TIER_ORDER`),
so this is not a hypothetical concern raised for a model nothing routes to —
real production traffic already lands on reasoning models at the router's
most expensive step. A reasoning model that inlines its chain of thought in
the same text field as its answer (DeepSeek R1's `<think>...</think>`, and any
provider serving through an OpenAI-compatible endpoint that has not adopted a
separate field) silently contaminates every consumer of `Completion.text`:
`rag.ground` checks citations against reasoning chatter it was never meant to
see, `evals.metrics` scores faithfulness and relevancy against polluted text,
and a caller expecting structured output gets a block of prose glued onto its
JSON. Nothing raises anywhere in that chain — the exact silent-failure shape
this repository has already paid for once (the missing `usage` block that made
cost panels read €0.00 on real runs; `FinishReason.LENGTH`, which also looks
fine until something downstream parses it).

`split_reasoning` is the one place this gets parsed. An adapter that receives
its reasoning content already separated by the provider (Ollama's `thinking`
field, LiteLLM's normalised `reasoning_content` on some providers) should use
that directly rather than running it through here — this function exists for
the providers that do not separate it, not as the only path to a populated
`Completion.reasoning`.
"""

from __future__ import annotations

import re

__all__ = ["split_reasoning"]

#: DeepSeek R1's shape, also used by Qwen QwQ and other reasoning models served
#: through an OpenAI-compatible endpoint. DOTALL because a reasoning block
#: spans many lines; non-greedy so a model that reasons more than once keeps
#: each block distinct rather than swallowing everything between the first
#: open and the last close tag into one.
_THINK_BLOCK = re.compile(r"<think>(.*?)</think>", re.DOTALL | re.IGNORECASE)


def split_reasoning(text: str) -> tuple[str, str]:
    """Return `(answer, reasoning)`. `reasoning` is `""` when there is none to split.

    Every `<think>` block is kept, joined in order — a model that reasons,
    "calls a tool" in its own narration, and reasons again still has all of it
    preserved rather than silently truncated to the first block, which is the
    one a naive `str.split("<think>", 1)` would keep.
    """
    blocks = _THINK_BLOCK.findall(text)
    if not blocks:
        return text, ""
    answer = _THINK_BLOCK.sub("", text).strip()
    reasoning = "\n\n".join(block.strip() for block in blocks)
    return answer, reasoning
