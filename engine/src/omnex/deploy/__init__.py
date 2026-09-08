"""P11 — deployment: feature flags, canary rollout, automatic rollback.

The eval gate (P4, driven by `scripts/eval_gate.py` and the quality-gate
workflow) blocks a regression before it merges. This module covers what happens
after: a change reaches a slice of traffic, is measured against the slice that
did not get it, and is rolled back by a RULE rather than by whoever happens to
be watching the dashboard.

Rollout is sticky per subject, hashed rather than sampled, so a user at 10% does
not see the new behaviour on one message in ten of the same conversation.
"""

from .flags import CanaryMetrics, CanaryPolicy, Flag, FlagSet, RollbackDecision, Variant

__all__ = [
    "CanaryMetrics",
    "CanaryPolicy",
    "Flag",
    "FlagSet",
    "RollbackDecision",
    "Variant",
]
