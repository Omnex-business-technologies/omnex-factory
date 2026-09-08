"""Feature flags and canary rollout, with the rollback rule stated as code.

Two things here that a generic flag library does not give you, because they are
specific to shipping model changes rather than code changes.

**A rollout percentage must be sticky per subject.** Hashing the subject id, not
rolling a die per request, so the same user gets the same variant every time.
Without it a user at 10% rollout sees the new behaviour on one in ten messages
of the same conversation, which reads as the system being erratic rather than as
an experiment — and it makes any comparison between the arms meaningless because
no user is wholly in either.

**Rollback is a rule, not a judgement call.** `CanaryPolicy.should_roll_back`
takes the canary's measurements and the baseline's and answers yes or no. A
canary watched by a human is a canary that survives until the human goes to
sleep; encoding the rule means it can be evaluated every minute by something
that does not.

The minimum-sample rule matters more than the thresholds. With 20 requests, one
error is a 5% error rate, and rolling back on that is rolling back on noise —
which teaches everyone to raise the threshold until it never fires. So the
policy refuses to judge below `min_requests`, and says so.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import StrEnum

from ..core.money import Money

__all__ = ["CanaryMetrics", "CanaryPolicy", "Flag", "FlagSet", "RollbackDecision", "Variant"]


class Variant(StrEnum):
    CONTROL = "control"
    CANARY = "canary"


@dataclass(frozen=True)
class Flag:
    name: str
    #: 0-100. The share of subjects that get the canary.
    rollout_percent: float = 0.0
    #: Always canary, whatever the percentage. For staff and for the accounts
    #: that asked to be early.
    allow_list: frozenset[str] = frozenset()
    #: Never canary. For the customer who has been burned once already.
    deny_list: frozenset[str] = frozenset()
    enabled: bool = True

    def variant_for(self, subject: str) -> Variant:
        """Sticky per subject: the same id always lands in the same arm.

        Hashed rather than random, so it survives a restart, a redeploy, and
        being asked from a different process. A per-request die roll gives a
        user at 10% the new behaviour on one message in ten of the same
        conversation — which reads as an unstable product and makes the
        comparison between arms meaningless.
        """
        if not self.enabled or subject in self.deny_list:
            return Variant.CONTROL
        if subject in self.allow_list:
            return Variant.CANARY
        if self.rollout_percent <= 0:
            return Variant.CONTROL
        if self.rollout_percent >= 100:
            return Variant.CANARY
        digest = hashlib.blake2b(f"{self.name}:{subject}".encode(), digest_size=8).digest()
        bucket = int.from_bytes(digest, "big") % 10_000
        return Variant.CANARY if bucket < self.rollout_percent * 100 else Variant.CONTROL


@dataclass
class FlagSet:
    flags: dict[str, Flag] = field(default_factory=dict)

    def add(self, flag: Flag) -> FlagSet:
        self.flags[flag.name] = flag
        return self

    def variant(self, name: str, subject: str) -> Variant:
        flag = self.flags.get(name)
        # An unknown flag is CONTROL, never canary. A typo in a flag name must
        # not silently enrol everyone in an experiment.
        return flag.variant_for(subject) if flag else Variant.CONTROL

    def is_canary(self, name: str, subject: str) -> bool:
        return self.variant(name, subject) is Variant.CANARY


@dataclass(frozen=True)
class CanaryMetrics:
    requests: int = 0
    errors: int = 0
    #: Quality from the eval harness, where a canary is scored on live traffic.
    pass_rate: float = 1.0
    p95_latency_seconds: float = 0.0
    cost_per_request: Money = field(default_factory=Money.zero)

    @property
    def error_rate(self) -> float:
        return 0.0 if not self.requests else self.errors / self.requests


@dataclass(frozen=True)
class RollbackDecision:
    roll_back: bool
    reason: str
    #: True when there was not enough traffic to judge either way.
    undecided: bool = False


@dataclass
class CanaryPolicy:
    """When to roll a canary back, expressed so a machine can evaluate it."""

    #: Below this, the canary has not earned a verdict. With 20 requests one
    #: error is a 5% error rate, and rolling back on that is rolling back on
    #: noise — which teaches everyone to raise the threshold until it never
    #: fires at all.
    min_requests: int = 200
    #: Extra error rate the canary may carry over the control, absolute.
    max_error_rate_increase: float = 0.01
    #: Quality drop that triggers a rollback, absolute.
    max_pass_rate_drop: float = 0.03
    #: Latency multiple, relative. Latency is far noisier than error rate, so
    #: the tolerance is a ratio rather than an absolute.
    max_latency_ratio: float = 1.5
    #: Cost multiple. A canary that is correct and twice the price is a
    #: rollback too — a fact routinely discovered a month later on the invoice.
    max_cost_ratio: float = 1.5

    def should_roll_back(self, canary: CanaryMetrics, control: CanaryMetrics) -> RollbackDecision:
        if canary.requests < self.min_requests:
            return RollbackDecision(
                roll_back=False,
                reason=f"only {canary.requests} canary requests; "
                f"{self.min_requests} needed before a verdict means anything",
                undecided=True,
            )

        if canary.error_rate - control.error_rate > self.max_error_rate_increase:
            return RollbackDecision(
                True,
                f"error rate {canary.error_rate:.2%} vs control {control.error_rate:.2%}",
            )

        if control.pass_rate - canary.pass_rate > self.max_pass_rate_drop:
            return RollbackDecision(
                True,
                f"quality {canary.pass_rate:.1%} vs control {control.pass_rate:.1%}",
            )

        if (
            control.p95_latency_seconds > 0
            and canary.p95_latency_seconds / control.p95_latency_seconds > self.max_latency_ratio
        ):
            return RollbackDecision(
                True,
                f"p95 {canary.p95_latency_seconds:.2f}s vs control "
                f"{control.p95_latency_seconds:.2f}s",
            )

        if control.cost_per_request and canary.cost_per_request.picos > int(
            control.cost_per_request.picos * self.max_cost_ratio
        ):
            return RollbackDecision(
                True,
                f"cost {canary.cost_per_request.format_adaptive()} vs control "
                f"{control.cost_per_request.format_adaptive()}",
            )

        return RollbackDecision(False, "canary is within every tolerance")
