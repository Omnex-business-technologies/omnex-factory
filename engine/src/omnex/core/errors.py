"""One error taxonomy, shared by every system in the engine.

The distinction that matters most is not what went wrong — it is **whether
trying again could possibly help**. Everything else in this engine keys off
that single bit: P16 decides whether to re-enqueue or dead-letter, P2 decides
whether to fall through to the next model or fail the request, P1 decides
whether to degrade to sources-only or return nothing.

Getting it wrong is expensive in both directions. Retrying a permanent failure
burns the budget and the deadline to arrive at the same answer — a malformed
prompt is still malformed on the fourth attempt. Dead-lettering a transient one
throws away work that would have succeeded a second later. So `retryable` is a
required property of the class, decided once where the error is defined, not a
guess made by a caller reading an error string.

`context` is a dict rather than a formatted message because these errors end up
in structured logs, in spans, and in an audit trail. A message that has already
had its variables baked into a sentence cannot be filtered, grouped or counted.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "BudgetExceeded",
    "ConfigurationError",
    "GuardrailBlocked",
    "NotGrounded",
    "OmnexError",
    "PermanentError",
    "ProviderError",
    "RateLimited",
    "TenantIsolationViolation",
    "TimeoutExceeded",
    "TransientError",
    "ValidationFailed",
]


class OmnexError(Exception):
    """Base for everything raised by the engine.

    `code` is a stable, machine-readable string. It is what a metric is
    labelled with and what an alert rule matches on, so it must not change when
    someone rewords the human message.
    """

    code: str = "omnex_error"
    retryable: bool = False

    def __init__(self, message: str, **context: Any) -> None:
        super().__init__(message)
        self.message = message
        self.context: dict[str, Any] = context

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
            **self.context,
        }

    def __str__(self) -> str:
        if not self.context:
            return self.message
        detail = " ".join(f"{k}={v!r}" for k, v in sorted(self.context.items()))
        return f"{self.message} ({detail})"


class TransientError(OmnexError):
    """A failure that a later, identical attempt could plausibly survive."""

    code = "transient"
    retryable = True


class PermanentError(OmnexError):
    """A failure that will recur identically. Retrying only spends the budget."""

    code = "permanent"
    retryable = False


class ProviderError(TransientError):
    """An upstream model or service failed.

    Defaults to retryable, but a 4xx from a provider is a permanent failure
    wearing a network error's clothes — so `from_status` classifies rather than
    letting every provider hiccup be retried four times.
    """

    code = "provider_error"

    @classmethod
    def from_status(cls, status: int, provider: str, message: str = "") -> OmnexError:
        msg = message or f"{provider} returned HTTP {status}"
        if status == 429:
            return RateLimited(msg, provider=provider, status=status)
        if status in (408, 425, 500, 502, 503, 504):
            return cls(msg, provider=provider, status=status)
        if 400 <= status < 500:
            # 401, 403, 404, 422: the same request will fail the same way.
            return PermanentError(msg, provider=provider, status=status)
        return cls(msg, provider=provider, status=status)


class RateLimited(TransientError):
    """Retryable, but only after `retry_after` — retrying sooner deepens the limit."""

    code = "rate_limited"

    def __init__(self, message: str, retry_after: float | None = None, **context: Any) -> None:
        super().__init__(message, **context)
        self.retry_after = retry_after


class TimeoutExceeded(TransientError):
    code = "timeout"


class BudgetExceeded(PermanentError):
    """A run hit a ceiling — passes, tokens, wall-clock or spend.

    Permanent by design. The budget is the stop condition; a retry that ignores
    it is a runaway loop with extra steps.
    """

    code = "budget_exceeded"


class GuardrailBlocked(PermanentError):
    """Content was refused by a guardrail. Carries the findings, not just a verdict."""

    code = "guardrail_blocked"

    def __init__(self, message: str, findings: list[Any] | None = None, **context: Any) -> None:
        super().__init__(message, **context)
        self.findings = findings or []

    def as_dict(self) -> dict[str, Any]:
        return {**super().as_dict(), "findings": [str(f) for f in self.findings]}

    def __str__(self) -> str:
        """Include the findings.

        An exception that says only "blocked by guardrails" sends whoever reads
        the log back to reproduce the request to learn which rule fired. The
        rule names are the entire useful content of this error.
        """
        base = super().__str__()
        if not self.findings:
            return base
        return f"{base} [{', '.join(str(f) for f in self.findings)}]"


class ValidationFailed(PermanentError):
    code = "validation_failed"


class NotGrounded(PermanentError):
    """A generated claim could not be traced to retrieved evidence.

    Its own class rather than a validation error because P1 treats it as a
    product outcome — the honest answer is "the documents do not say" — while a
    validation failure is a bug.
    """

    code = "not_grounded"


class TenantIsolationViolation(PermanentError):
    """A query or write would have crossed a tenant boundary.

    Never caught and continued anywhere in this engine. It means an isolation
    invariant is broken, and the only safe response is to fail the request
    loudly and page someone.
    """

    code = "tenant_isolation_violation"


class ConfigurationError(PermanentError):
    """Wrong at startup, not at runtime. Should be raised as early as possible."""

    code = "configuration_error"
