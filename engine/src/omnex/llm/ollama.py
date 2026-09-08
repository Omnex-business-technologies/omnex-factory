"""Ollama adapter — the zero-marginal-cost tier.

Priced at zero in the catalogue, and that is honest rather than a rounding: the
electricity is real but it is not per-token, and modelling it as a token price
would be a lie in the other direction. What it means concretely is that the
router (P2) prefers this tier whenever the task allows, that the eval gate (P4)
runs on every pull request without a credential, and that a developer can work
offline on a laptop against the same code paths production uses.

Usage still comes from the response, never from the estimator, even though the
cost is zero. Token counts drive the context-window checks and the trace, and a
tier where those numbers are invented is a tier whose behaviour cannot be
compared to the hosted ones — which is the whole point of having both behind one
interface.

Ollama's `/api/chat` returns `prompt_eval_count` and `eval_count` rather than
OpenAI's names. Translated here rather than anywhere else, so nothing above this
file has to know which backend served a request.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Sequence
from typing import Any

from ..core.clock import Clock, SystemClock
from ..core.errors import ProviderError
from ..core.money import Money
from .base import CallOptions
from .catalog import ModelSpec, Tier
from .types import Completion, FinishReason, Message, Usage

__all__ = ["OllamaModel", "local_spec"]


def local_spec(name: str, context_window: int = 32_768, tier: Tier = Tier.NANO) -> ModelSpec:
    """A spec for a locally-served model. Zero price, and that is the point."""
    from ..core.money import TokenPrice

    return ModelSpec(
        name=name,
        provider="ollama",
        tier=tier,
        price=TokenPrice("0", "0"),
        context_window=context_window,
        max_output_tokens=4096,
        notes="Local. Zero marginal cost, so the router prefers it wherever the task allows.",
    )


class OllamaModel:
    """A `LanguageModel` served by a local Ollama daemon.

    Uses `urllib` rather than `httpx` so the local tier — the one that is
    supposed to work with nothing installed — genuinely needs nothing installed.
    """

    def __init__(
        self,
        spec: ModelSpec,
        host: str = "http://127.0.0.1:11434",
        ollama_model: str = "",
        clock: Clock | None = None,
    ) -> None:
        self._spec = spec
        self.host = host.rstrip("/")
        #: The tag Ollama knows ("qwen2.5:7b-instruct"). Separate from our own
        #: name so the catalogue can use role-shaped names.
        self.ollama_model = ollama_model or spec.name.split("/")[-1]
        self.clock = clock or SystemClock()

    @property
    def spec(self) -> ModelSpec:
        return self._spec

    def complete(self, messages: Sequence[Message], options: CallOptions) -> Completion:
        payload = {
            "model": self.ollama_model,
            "messages": [m.as_dict() for m in messages],
            "stream": False,
            "options": {
                "temperature": options.temperature,
                "num_predict": options.max_tokens,
                **({"stop": list(options.stop)} if options.stop else {}),
            },
        }
        timeout = options.deadline.remaining() if options.deadline else 120.0

        started = self.clock.monotonic()
        request = urllib.request.Request(
            f"{self.host}/api/chat",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=max(1.0, timeout)) as response:
                body: dict[str, Any] = json.loads(response.read())
        except urllib.error.HTTPError as exc:
            raise ProviderError.from_status(exc.code, provider="ollama", message=str(exc)) from exc
        except OSError as exc:
            # Connection refused is the common one, and the useful message names
            # the fix rather than the errno.
            raise ProviderError(
                f"cannot reach Ollama at {self.host} — is it running? "
                f"(`ollama serve`, then `ollama pull {self.ollama_model}`)",
                provider="ollama",
            ) from exc
        latency = self.clock.monotonic() - started

        text = str(body.get("message", {}).get("content", ""))
        input_tokens = int(body.get("prompt_eval_count", 0) or 0)
        output_tokens = int(body.get("eval_count", 0) or 0)
        # Ollama reports `done_reason: "length"` when it hit num_predict. Same
        # silent-truncation trap as every hosted provider, so it is surfaced the
        # same way.
        finish = (
            FinishReason.LENGTH
            if str(body.get("done_reason", "")) == "length"
            else FinishReason.STOP
        )

        return Completion(
            text=text,
            model=self._spec.name,
            usage=Usage(input_tokens, output_tokens),
            cost=Money.zero(),
            undiscounted=Money.zero(),
            finish_reason=finish,
            latency_seconds=latency,
            provider="ollama",
            metadata={"ollama_model": self.ollama_model},
        )

    def available(self) -> bool:
        """Is the daemon up and does it have this model?

        Called at startup so a missing model is a clear message rather than a
        connection error on the first user request.
        """
        try:
            with urllib.request.urlopen(f"{self.host}/api/tags", timeout=2.0) as response:
                tags = json.loads(response.read())
        except OSError:
            return False
        names = {str(m.get("name", "")).split(":")[0] for m in tags.get("models", [])}
        return self.ollama_model.split(":")[0] in names
