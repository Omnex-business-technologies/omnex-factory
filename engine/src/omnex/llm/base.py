"""The one interface every model in this engine is used through.

Everything downstream — the router, the RAG pipeline, the crew, the eval
harness — depends on `LanguageModel` and nothing else. That is what makes a
LiteLLM call, a local Ollama call and a scripted test double interchangeable at
every call site, and it is why the test suite needs no network.

`CallOptions` is a value object rather than a long keyword signature because the
router passes options DOWN a chain — cheap attempt, escalation, fallback — and
each hop needs to adjust one field while preserving the rest. With keyword
arguments that becomes a dict splat that silently drops whatever the caller
forgot to re-forward; the classic version of this bug is a deadline that
survives the first hop and vanishes on the retry.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
from typing import Protocol, runtime_checkable

from ..core.clock import Deadline
from ..core.money import Money
from .catalog import ModelSpec
from .types import Completion, Message

__all__ = ["CallOptions", "LanguageModel", "compute_cost"]


@dataclass(frozen=True)
class CallOptions:
    max_tokens: int = 1024
    temperature: float = 0.0
    stop: tuple[str, ...] = ()
    #: Remaining budget for the whole call chain, not this hop. See core/clock.py.
    deadline: Deadline | None = None
    #: Hard ceiling on what this call may spend. The router enforces it before
    #: dispatch using an upper-bound token estimate.
    spend_ceiling: Money | None = None
    #: Ask the provider to cache this prefix where supported.
    cache_prefix: bool = False
    #: Free-form passthrough for provider-specific parameters. Kept separate so
    #: a provider-specific option can never shadow a first-class one.
    extra: tuple[tuple[str, object], ...] = ()

    def with_(self, **changes: object) -> CallOptions:
        """A copy with fields changed, preserving everything else.

        Used at every hop of the router's chain. The point is that forgetting a
        field is impossible: you state what changes, not what survives.
        """
        return replace(self, **changes)  # type: ignore[arg-type]


@runtime_checkable
class LanguageModel(Protocol):
    """A thing that turns messages into a completion, and knows what it costs."""

    @property
    def spec(self) -> ModelSpec: ...

    def complete(self, messages: Sequence[Message], options: CallOptions) -> Completion: ...


def compute_cost(
    spec: ModelSpec,
    input_tokens: int,
    output_tokens: int,
    cached_input_tokens: int = 0,
    reference: ModelSpec | None = None,
) -> tuple[Money, Money]:
    """Actual cost, and what the same tokens would have cost on `reference`.

    The second number is the whole basis of every savings claim in this engine.
    It has to be computed here, at the moment of the call, against the model that
    would otherwise have served — reconstructing it later means guessing which
    model a router would have picked, which is exactly the thing under test.

    With no reference, the undiscounted figure is this model at full price with
    no cache, which still makes prompt-cache savings measurable on their own.
    """
    actual = spec.price.cost(input_tokens, output_tokens, cached_input_tokens)
    baseline_spec = reference or spec
    baseline = baseline_spec.price.cost(input_tokens, output_tokens, cached_input_tokens=0)
    return actual, baseline
