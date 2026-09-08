"""What models exist, what they cost, and what they can do.

The catalogue is DATA (`models.json`), not code, for a reason that has bitten
every team that hardcoded it: a price copied from a pricing page into a source
file is a price that is eventually wrong, and nothing about the program's
behaviour reveals it. Every routing decision, every budget check and every
savings figure downstream is then confidently, invisibly wrong.

So the file carries `verified_on`, and `ModelCatalog.load()` reports staleness
rather than silently trusting a number nobody has looked at in a year.
`assert_fresh()` exists for the deploy path, where shipping year-old prices into
a billing system is worth failing a build over.

**The tests for the router do not use this catalogue.** They build synthetic
models with prices chosen to make an arithmetic property obvious — a 30×
cheap-to-expensive ratio, say. That keeps routing behaviour provable and stops
the test suite from turning into an assertion about a vendor's current price
list, which would go red for reasons that have nothing to do with the code.

Tiers are ordered, because escalation needs to know what "stronger" means. The
order is by capability, not by price: they usually agree, but when a provider
prices a new small model above an older large one, escalating to the cheaper-
but-weaker model would be the wrong move and the ordering is what prevents it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from ..core.errors import ConfigurationError
from ..core.money import TokenPrice

__all__ = ["CATALOG_PATH", "ModelCatalog", "ModelSpec", "Tier"]

CATALOG_PATH = Path(__file__).with_name("models.json")

#: Beyond this, a price is old enough that it should be re-checked rather than
#: trusted. Vendors reprice more often than that, almost always downwards —
#: which means a stale catalogue makes the expensive tier look worse than it is
#: and routes traffic away from a model that has become good value.
STALE_AFTER_DAYS = 90


class Tier(StrEnum):
    """Capability tiers, ordered by capability. Escalation moves up this ladder.

    All four comparisons are defined explicitly, and that is not boilerplate.
    `StrEnum` inherits from `str`, which already provides `__lt__`, `__le__`,
    `__gt__` and `__ge__` — so `functools.total_ordering` fills in nothing, and
    defining only `__lt__` leaves the other three doing LEXICOGRAPHIC string
    comparison. The result is silent and wrong in exactly the direction that
    hurts: `Tier.LARGE >= Tier.SMALL` evaluates `"large" >= "small"`, which is
    False, so a router asked to escalate finds no stronger tier and quietly
    stops escalating. It raises nothing and looks like a routing policy choice.
    """

    NANO = "nano"
    SMALL = "small"
    LARGE = "large"
    REASONING = "reasoning"

    @property
    def rank(self) -> int:
        return _TIER_ORDER.index(self)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Tier):
            return NotImplemented
        return self.rank < other.rank

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Tier):
            return NotImplemented
        return self.rank <= other.rank

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Tier):
            return NotImplemented
        return self.rank > other.rank

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Tier):
            return NotImplemented
        return self.rank >= other.rank


_TIER_ORDER = [Tier.NANO, Tier.SMALL, Tier.LARGE, Tier.REASONING]


@dataclass(frozen=True)
class ModelSpec:
    name: str
    provider: str
    tier: Tier
    price: TokenPrice
    context_window: int
    max_output_tokens: int
    supports_tools: bool = True
    supports_vision: bool = False
    #: Whether the provider bills cached input tokens at a reduced rate. A router
    #: that cannot represent this routes as if caching did not exist, and prompt
    #: caching moves the economics of a long system prompt more than model
    #: choice does.
    supports_prompt_cache: bool = False
    notes: str = ""

    def fits(self, estimated_input_tokens: int, max_output_tokens: int) -> bool:
        """Whether a call plausibly fits, leaving room for the output.

        Checked BEFORE dispatch. A context-window overflow discovered by the
        provider is a failed request that still consumed latency and, on some
        providers, still billed for the input.
        """
        return estimated_input_tokens + max_output_tokens <= self.context_window

    @classmethod
    def from_dict(cls, name: str, payload: dict[str, Any]) -> ModelSpec:
        return cls(
            name=name,
            provider=payload["provider"],
            tier=Tier(payload["tier"]),
            price=TokenPrice(
                payload["input_usd_per_mtok"],
                payload["output_usd_per_mtok"],
                payload.get("cached_input_usd_per_mtok"),
            ),
            context_window=int(payload["context_window"]),
            max_output_tokens=int(payload["max_output_tokens"]),
            supports_tools=bool(payload.get("supports_tools", True)),
            supports_vision=bool(payload.get("supports_vision", False)),
            supports_prompt_cache="cached_input_usd_per_mtok" in payload,
            notes=payload.get("notes", ""),
        )


class ModelCatalog:
    """Loaded model specs, with staleness reported rather than assumed away."""

    def __init__(self, specs: dict[str, ModelSpec], verified_on: date, source: str = "") -> None:
        self.specs = specs
        self.verified_on = verified_on
        self.source = source

    @classmethod
    def load(cls, path: Path | None = None) -> ModelCatalog:
        path = path or CATALOG_PATH
        payload = json.loads(path.read_text())
        verified = date.fromisoformat(payload["verified_on"])
        specs = {name: ModelSpec.from_dict(name, spec) for name, spec in payload["models"].items()}
        return cls(specs, verified, source=str(path))

    # ── freshness ─────────────────────────────────────────────────────────
    def age_days(self, today: date | None = None) -> int:
        return ((today or datetime.now(UTC).date()) - self.verified_on).days

    def is_stale(self, today: date | None = None) -> bool:
        return self.age_days(today) > STALE_AFTER_DAYS

    def assert_fresh(self, today: date | None = None) -> None:
        """Fail loudly. For the deploy path, where stale prices reach a bill."""
        if self.is_stale(today):
            raise ConfigurationError(
                "model price catalogue is stale — re-verify against the provider pricing pages",
                verified_on=self.verified_on.isoformat(),
                age_days=self.age_days(today),
                limit_days=STALE_AFTER_DAYS,
                source=self.source,
            )

    # ── lookup ────────────────────────────────────────────────────────────
    def get(self, name: str) -> ModelSpec:
        try:
            return self.specs[name]
        except KeyError as exc:
            raise ConfigurationError(
                "unknown model", model=name, known=", ".join(sorted(self.specs))
            ) from exc

    def by_tier(self, tier: Tier) -> list[ModelSpec]:
        return sorted(
            (s for s in self.specs.values() if s.tier is tier),
            key=lambda s: s.price.output_picos,
        )

    def cheapest_in(self, tier: Tier) -> ModelSpec:
        candidates = self.by_tier(tier)
        if not candidates:
            raise ConfigurationError("no model in tier", tier=str(tier))
        return candidates[0]

    def price_ratio(self, cheap: str, expensive: str, output_share: float = 0.2) -> float:
        """How many times more expensive one model is than another, per token.

        Weighted by a realistic output share rather than comparing input prices
        alone: output is typically 3–5× the input price, so a comparison that
        ignores it understates the gap between tiers and makes routing look less
        worthwhile than it is.
        """

        def blend(price: TokenPrice) -> float:
            return (1 - output_share) * price.input_picos + output_share * price.output_picos

        cheap_blend = blend(self.get(cheap).price)
        if cheap_blend == 0:
            return float("inf")
        return blend(self.get(expensive).price) / cheap_blend
