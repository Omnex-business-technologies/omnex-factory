"""Environment reading that survives real deployment environments.

`clean_env` exists because of a specific, repeated failure on the TypeScript
side of this repo (see `lib/core/supabase/env.ts`): a key pasted into a
dashboard field arrives with a UTF-8 BOM, a trailing newline, or wrapping
quotes. The value looks correct in every log line — the BOM is invisible — and
every request fails with 401. The fix is not "be careful when pasting"; it is
to strip those characters on read, once, in one function, so no caller can
forget.

`Settings` is a plain dataclass built from the environment in one place. The
alternative — reading `os.environ` where the value is needed — means a missing
key is discovered on the first request that happens to take that branch, in
production, hours after deploy. Here it is discovered at construction, and
`require()` names what is missing.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from .errors import ConfigurationError

__all__ = ["Settings", "clean_env", "env_bool", "env_float", "env_int", "env_str"]

# BOM, zero-width space, zero-width no-break space, and the usual whitespace.
_JUNK = "﻿​⁠\r\n\t "
_QUOTES = "\"'`"


def clean_env(raw: str | None) -> str:
    """Strip the characters that make a correct-looking secret fail."""
    if raw is None:
        return ""
    return raw.strip(_JUNK).strip(_QUOTES).strip(_JUNK)


def env_str(name: str, default: str = "") -> str:
    value = clean_env(os.environ.get(name))
    return value if value else default


def env_int(name: str, default: int) -> int:
    value = env_str(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer", value=value) from exc


def env_float(name: str, default: float) -> float:
    value = env_str(name)
    if not value:
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be a number", value=value) from exc


def env_bool(name: str, default: bool = False) -> bool:
    value = env_str(name).lower()
    if not value:
        return default
    if value in ("1", "true", "yes", "on"):
        return True
    if value in ("0", "false", "no", "off"):
        return False
    raise ConfigurationError(f"{name} must be a boolean", value=value)


@dataclass(frozen=True)
class Settings:
    """Everything the engine reads from the environment, resolved once."""

    environment: str = field(default_factory=lambda: env_str("OMNEX_ENV", "development"))
    service_name: str = field(default_factory=lambda: env_str("OMNEX_SERVICE", "omnex-engine"))
    #: Where traces and metrics go. Empty means the in-memory collector only —
    #: the default, so nothing in development silently ships telemetry anywhere.
    otlp_endpoint: str = field(default_factory=lambda: env_str("OTEL_EXPORTER_OTLP_ENDPOINT"))
    #: Local-first (P7). When set, the router prefers the local model tier.
    ollama_host: str = field(default_factory=lambda: env_str("OLLAMA_HOST"))
    #: Hard ceiling on what one request may spend, in USD. P2 enforces it.
    request_budget_usd: str = field(
        default_factory=lambda: env_str("OMNEX_REQUEST_BUDGET_USD", "0.05")
    )
    #: Wall-clock ceiling per run, seconds. Kept below the platform timeout so a
    #: run stops with a stated cause instead of being killed without one.
    run_timeout_seconds: float = field(default_factory=lambda: env_float("OMNEX_RUN_TIMEOUT", 55.0))
    data_dir: str = field(default_factory=lambda: env_str("OMNEX_DATA_DIR", ".omnex"))

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ("production", "prod")

    def require(self, *names: str) -> dict[str, str]:
        """Fetch required environment values, naming every missing one at once.

        Reporting them one per deploy is how a five-minute config fix becomes a
        five-deploy afternoon.
        """
        found: dict[str, str] = {}
        missing: list[str] = []
        for name in names:
            value = env_str(name)
            if value:
                found[name] = value
            else:
                missing.append(name)
        if missing:
            raise ConfigurationError(
                "missing required environment variables", missing=", ".join(missing)
            )
        return found

    def as_dict(self) -> dict[str, Any]:
        """Safe to log: this dataclass holds no secrets, only their locations."""
        return {
            "environment": self.environment,
            "service_name": self.service_name,
            "otlp_endpoint": self.otlp_endpoint or "(in-memory only)",
            "ollama_host": self.ollama_host or "(unset)",
            "request_budget_usd": self.request_budget_usd,
            "run_timeout_seconds": self.run_timeout_seconds,
            "data_dir": self.data_dir,
        }
