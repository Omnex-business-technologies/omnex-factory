"""Tests for P11."""

from __future__ import annotations

from omnex.core import Money
from omnex.deploy import CanaryMetrics, CanaryPolicy, Flag, FlagSet, Variant


def test_a_subject_always_lands_in_the_same_arm():
    """A per-request die roll makes the product look erratic and the comparison meaningless."""
    flag = Flag("new-router", rollout_percent=10)
    for subject in (f"user-{i}" for i in range(50)):
        assignments = {flag.variant_for(subject) for _ in range(20)}
        assert len(assignments) == 1


def test_the_rollout_percentage_is_roughly_honoured():
    flag = Flag("new-router", rollout_percent=25)
    canary = sum(flag.variant_for(f"user-{i}") is Variant.CANARY for i in range(4000))
    assert 0.22 < canary / 4000 < 0.28


def test_allow_and_deny_lists_override_the_percentage():
    flag = Flag(
        "new-router",
        rollout_percent=0,
        allow_list=frozenset({"staff-1"}),
        deny_list=frozenset({"burned-customer"}),
    )
    assert flag.variant_for("staff-1") is Variant.CANARY
    assert flag.variant_for("anyone-else") is Variant.CONTROL

    fully_rolled = Flag("f", rollout_percent=100, deny_list=frozenset({"burned-customer"}))
    assert fully_rolled.variant_for("burned-customer") is Variant.CONTROL


def test_an_unknown_flag_is_control_never_canary():
    """A typo in a flag name must not silently enrol everyone in an experiment."""
    flags = FlagSet().add(Flag("new-router", rollout_percent=100))
    assert flags.variant("new-rooter", "user-1") is Variant.CONTROL
    assert flags.is_canary("new-router", "user-1")


def test_a_disabled_flag_sends_everyone_to_control():
    flag = Flag("f", rollout_percent=100, enabled=False)
    assert flag.variant_for("anyone") is Variant.CONTROL


# ── Rollback ──────────────────────────────────────────────────────────────

CONTROL = CanaryMetrics(
    requests=5000,
    errors=25,
    pass_rate=0.90,
    p95_latency_seconds=1.2,
    cost_per_request=Money.from_usd("0.004"),
)


def test_a_canary_with_too_little_traffic_gets_no_verdict():
    """With 20 requests one error is a 5% error rate. Rolling back on that is noise."""
    decision = CanaryPolicy().should_roll_back(
        CanaryMetrics(requests=20, errors=1, pass_rate=0.5), CONTROL
    )
    assert not decision.roll_back and decision.undecided
    assert "before a verdict means anything" in decision.reason


def test_a_healthy_canary_stays():
    decision = CanaryPolicy().should_roll_back(
        CanaryMetrics(
            requests=1000,
            errors=5,
            pass_rate=0.91,
            p95_latency_seconds=1.25,
            cost_per_request=Money.from_usd("0.004"),
        ),
        CONTROL,
    )
    assert not decision.roll_back and not decision.undecided


def test_a_quality_drop_rolls_back_even_with_no_errors():
    """The failure a health check cannot see: everything responds, worse."""
    decision = CanaryPolicy().should_roll_back(
        CanaryMetrics(
            requests=1000,
            errors=0,
            pass_rate=0.80,
            p95_latency_seconds=1.2,
            cost_per_request=Money.from_usd("0.004"),
        ),
        CONTROL,
    )
    assert decision.roll_back and "quality" in decision.reason


def test_a_more_expensive_canary_rolls_back_too():
    """Correct and twice the price is a rollback — usually found on the invoice."""
    decision = CanaryPolicy().should_roll_back(
        CanaryMetrics(
            requests=1000,
            errors=5,
            pass_rate=0.91,
            p95_latency_seconds=1.2,
            cost_per_request=Money.from_usd("0.012"),
        ),
        CONTROL,
    )
    assert decision.roll_back and "cost" in decision.reason


def test_errors_and_latency_each_trigger_a_rollback():
    errors = CanaryPolicy().should_roll_back(
        CanaryMetrics(requests=1000, errors=100, pass_rate=0.90, p95_latency_seconds=1.2), CONTROL
    )
    assert errors.roll_back and "error rate" in errors.reason

    slow = CanaryPolicy().should_roll_back(
        CanaryMetrics(requests=1000, errors=5, pass_rate=0.90, p95_latency_seconds=4.0), CONTROL
    )
    assert slow.roll_back and "p95" in slow.reason
