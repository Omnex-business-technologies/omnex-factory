"""LiteLLM adapter — the real multi-provider call path.

LiteLLM is used for exactly one thing: normalising a hundred providers onto one
request shape. Everything it also offers — retries, fallbacks, budgets, caching,
callbacks — is deliberately NOT used, because each of those already exists in
this engine with behaviour the tests pin down, and two layers of retry compose
into `outer_attempts × inner_attempts` calls against a provider that is already
rate-limiting you. That failure is invisible in the code and obvious in the bill.

So: `num_retries=0`, no fallback list, no router. This class translates a request
out and a response back, and classifies errors into the taxonomy the rest of the
engine understands.

**Usage comes from the provider, never from the estimator.** The token counts
that produce a cost are the ones the API reported. When a provider omits usage —
some streaming paths do — that is recorded as an explicit condition rather than
quietly back-filled with an estimate, because a cost silently derived from a
guess is indistinguishable in a ledger from one that was measured.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from ..core.clock import Clock, SystemClock
from ..core.errors import ConfigurationError, PermanentError, ProviderError, RateLimited
from .base import CallOptions, compute_cost
from .catalog import ModelSpec
from .types import Completion, FinishReason, Message, Usage

__all__ = ["LiteLlmModel"]

_FINISH_REASONS = {
    "stop": FinishReason.STOP,
    "length": FinishReason.LENGTH,
    "max_tokens": FinishReason.LENGTH,
    "tool_calls": FinishReason.TOOL_CALL,
    "function_call": FinishReason.TOOL_CALL,
    "content_filter": FinishReason.CONTENT_FILTER,
}


class LiteLlmModel:
    """A `LanguageModel` backed by `litellm.completion`."""

    def __init__(
        self,
        spec: ModelSpec,
        litellm_model: str = "",
        reference: ModelSpec | None = None,
        clock: Clock | None = None,
        api_base: str = "",
    ) -> None:
        self._spec = spec
        #: The provider-qualified id LiteLLM expects ("groq/llama-3.3-70b").
        #: Separate from our own name so the catalogue can use role-shaped names
        #: and swapping the underlying model is a data change.
        self.litellm_model = litellm_model or spec.name
        self.reference = reference
        self.clock = clock or SystemClock()
        self.api_base = api_base

    @property
    def spec(self) -> ModelSpec:
        return self._spec

    def complete(self, messages: Sequence[Message], options: CallOptions) -> Completion:
        try:
            import litellm
        except ImportError as exc:  # pragma: no cover - only without the extra
            raise ConfigurationError(
                "LiteLlmModel needs the 'llm' extra: pip install 'omnex-engine[llm]'"
            ) from exc

        kwargs: dict[str, Any] = {
            "model": self.litellm_model,
            "messages": [m.as_dict() for m in messages],
            "max_tokens": options.max_tokens,
            "temperature": options.temperature,
            # Our retry loop owns this. Leaving LiteLLM's default on multiplies
            # attempts against a provider that is already rate-limiting us.
            "num_retries": 0,
        }
        if options.stop:
            kwargs["stop"] = list(options.stop)
        if self.api_base:
            kwargs["api_base"] = self.api_base
        # Pass the caller's remaining budget down, so a nested call cannot start
        # a fresh timeout inside an already-expiring request.
        if options.deadline is not None:
            kwargs["timeout"] = max(0.1, options.deadline.remaining())
        kwargs.update(dict(options.extra))

        started = self.clock.monotonic()
        try:
            response = litellm.completion(**kwargs)
        except Exception as exc:
            raise self._classify(exc) from exc
        latency = self.clock.monotonic() - started

        return self._to_completion(response, latency)

    # ── translation ───────────────────────────────────────────────────────
    def _to_completion(self, response: Any, latency: float) -> Completion:
        choice = response.choices[0]
        text = getattr(choice.message, "content", "") or ""
        finish = _FINISH_REASONS.get(
            str(getattr(choice, "finish_reason", "stop")), FinishReason.STOP
        )

        raw = getattr(response, "usage", None)
        if raw is None:
            # Better to fail than to invent a number that lands in a ledger
            # indistinguishable from a measured one.
            raise ProviderError(
                "provider returned no usage; cost cannot be computed from a response alone",
                provider=self._spec.provider,
                model=self._spec.name,
            )

        input_tokens = int(getattr(raw, "prompt_tokens", 0) or 0)
        output_tokens = int(getattr(raw, "completion_tokens", 0) or 0)
        cached = _cached_tokens(raw)

        cost, undiscounted = compute_cost(
            self._spec, input_tokens, output_tokens, cached, self.reference
        )
        return Completion(
            text=text,
            model=self._spec.name,
            usage=Usage(input_tokens, output_tokens, cached),
            cost=cost,
            undiscounted=undiscounted,
            finish_reason=finish,
            latency_seconds=latency,
            provider=self._spec.provider,
            metadata={"litellm_model": self.litellm_model},
        )

    def _classify(self, exc: Exception) -> Exception:
        """Map a LiteLLM exception onto the engine's retryable/permanent split.

        Status code first, exception class name second. The class names are
        stable enough to key on but the status is the thing that actually
        determines whether a retry can help.
        """
        status = getattr(exc, "status_code", None)
        if isinstance(status, int):
            return ProviderError.from_status(status, provider=self._spec.provider, message=str(exc))

        name = type(exc).__name__
        if "RateLimit" in name:
            return RateLimited(str(exc), provider=self._spec.provider)
        if any(
            k in name for k in ("Timeout", "ServiceUnavailable", "InternalServer", "APIConnection")
        ):
            return ProviderError(str(exc), provider=self._spec.provider)
        if any(
            k in name
            for k in (
                "Authentication",
                "PermissionDenied",
                "NotFound",
                "BadRequest",
                "InvalidRequest",
            )
        ):
            return PermanentError(str(exc), provider=self._spec.provider)
        return ProviderError(str(exc), provider=self._spec.provider)


def _cached_tokens(usage: Any) -> int:
    """Cached prompt tokens, however this provider chose to report them.

    Three shapes in the wild, and the value is a SUBSET of prompt_tokens in all
    of them. Returning zero when unknown under-reports the saving, which is the
    safe direction — over-reporting would make a cache look like it is working
    when it is not.
    """
    details = getattr(usage, "prompt_tokens_details", None)
    if details is not None:
        cached = getattr(details, "cached_tokens", None)
        if cached is not None:
            return int(cached)
    for attr in ("cache_read_input_tokens", "cached_tokens"):
        value = getattr(usage, attr, None)
        if value is not None:
            return int(value)
    return 0
