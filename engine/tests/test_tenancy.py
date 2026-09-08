"""Tests for P10."""

from __future__ import annotations

import pytest

from omnex.core import BudgetExceeded, FakeClock, Money, TenantIsolationViolation
from omnex.tenancy import Plan, Tenant, TenantContext, UsageLedger

ACME = Tenant(id="tnt_acme", name="Acme", plan=Plan.STARTER)
FREE = Tenant(id="tnt_free", name="Trial", plan=Plan.FREE)


def _ledger() -> UsageLedger:
    return UsageLedger(clock=FakeClock())


# ── Isolation ─────────────────────────────────────────────────────────────


def test_a_resource_from_another_tenant_raises_rather_than_returning():
    context = TenantContext(ACME)
    context.require("tnt_acme", "document")  # fine
    with pytest.raises(TenantIsolationViolation) as exc:
        context.require("tnt_globex", "document")
    assert "tnt_acme" in str(exc.value) and "tnt_globex" in str(exc.value)


def test_a_caller_filter_cannot_widen_the_tenant_scope():
    """The one filter that must never be negotiable."""
    context = TenantContext(ACME)
    assert context.filter({"tenant": "tnt_globex"})["tenant"] == "tnt_acme"
    assert context.filter({"doc_id": "x"}) == {"doc_id": "x", "tenant": "tnt_acme"}


def test_the_tenant_is_passed_explicitly_and_not_stored_globally():
    """An implicit current-tenant returns another customer's data under concurrency."""
    import inspect

    from omnex.tenancy import tenant as module

    source = inspect.getsource(module)
    assert "contextvar" not in source.lower()
    assert "threading.local" not in source.lower()


# ── Quotas ────────────────────────────────────────────────────────────────


def test_one_pathological_request_is_named_as_such_not_as_out_of_budget():
    """A monthly cap alone lets a single request eat the whole month."""
    check = _ledger().check(FREE, estimated_cost=Money.from_usd("0.50"))
    assert not check.allowed
    assert "per-request limit" in check.reason


def test_the_monthly_ceiling_stops_the_next_request_and_says_what_is_left():
    ledger = _ledger()
    # Exactly the free plan's $1.00 cap, in requests that each clear the
    # per-request limit — so the monthly rule is the one being tested.
    for _ in range(100):
        ledger.record(FREE, Money.from_usd("0.01"))
    assert ledger.spend_for(FREE.id) == Money.from_usd("1.00")

    check = ledger.check(FREE, estimated_cost=Money.from_usd("0.01"))
    assert not check.allowed
    assert "monthly spend" in check.reason
    assert check.remaining_spend == Money.zero()


def test_the_rate_limit_is_per_tenant():
    ledger = _ledger()
    tiny = Money.from_usd("0.001")
    allowed = sum(ledger.check(FREE, tiny).allowed for _ in range(20))
    assert allowed == 3  # the free plan's burst
    assert ledger.check(ACME, tiny).allowed  # a different tenant is unaffected


def test_checking_without_consuming_does_not_spend_a_tenants_rate_quota():
    ledger = _ledger()
    tiny = Money.from_usd("0.001")
    for _ in range(50):
        assert ledger.check(FREE, tiny, consume_rate=False).allowed
    assert sum(ledger.check(FREE, tiny).allowed for _ in range(10)) == 3


def test_a_denied_check_can_be_raised_with_its_reason():
    check = _ledger().check(FREE, estimated_cost=Money.from_usd("5.00"))
    with pytest.raises(BudgetExceeded, match="per-request"):
        check.raise_if_denied()


def test_plans_differ_in_every_dimension():
    assert (
        Tenant("a", "a", Plan.FREE).quota.monthly_spend
        < Tenant("b", "b", Plan.GROWTH).quota.monthly_spend
    )
    assert (
        Tenant("a", "a", Plan.FREE).quota.rate.rate
        < Tenant("b", "b", Plan.ENTERPRISE).quota.rate.rate
    )
    assert (
        Tenant("a", "a", Plan.STARTER).quota.max_documents
        < Tenant("b", "b", Plan.GROWTH).quota.max_documents
    )


# ── Usage and billing ─────────────────────────────────────────────────────


def test_rounding_happens_once_at_the_invoice_not_per_record():
    """Rounding each record and summing is how a bill ends up dollars out."""
    ledger = _ledger()
    for _ in range(1000):
        ledger.record(ACME, Money.from_usd("0.004"))
    assert ledger.spend_for(ACME.id) == Money.from_usd("4.00")
    assert ledger.invoice_cents(ACME.id) == 400  # not 0, which per-record rounding gives


def test_the_statement_shows_what_the_router_and_cache_saved():
    """The difference between a bill and a bill a customer is happy to pay."""
    ledger = _ledger()
    for _ in range(50):
        ledger.record(
            ACME, Money.from_usd("0.002"), kind="answer", undiscounted=Money.from_usd("0.030")
        )
    assert ledger.saved_for(ACME.id) == Money.from_usd("1.40")
    assert "saved" in ledger.statement(ACME)


def test_reconciliation_detects_drift_between_metering_and_billing():
    """A refunded charge or a double-metered retry, undetected for months."""
    ledger = _ledger()
    for _ in range(10):
        ledger.record(ACME, Money.from_usd("0.10"))

    exact = ledger.reconcile(ACME.id, billed=Money.from_usd("1.00"))
    assert exact.matches and "matches" in exact.report()

    drifted = ledger.reconcile(ACME.id, billed=Money.from_usd("0.80"))
    assert not drifted.matches
    assert drifted.difference == Money.from_usd("0.20")
    assert "DIFFERS" in drifted.report()


def test_usage_is_attributed_by_kind_so_a_bill_can_be_explained():
    ledger = _ledger()
    ledger.record(ACME, Money.from_usd("0.30"), kind="answer")
    ledger.record(ACME, Money.from_usd("0.05"), kind="embedding")
    ledger.record(ACME, Money.from_usd("0.20"), kind="answer")
    assert list(ledger.usage_by_kind(ACME.id)) == ["answer", "embedding"]
    assert ledger.usage_by_kind(ACME.id)["answer"] == Money.from_usd("0.50")


def test_one_tenants_usage_never_appears_in_anothers_total():
    ledger = _ledger()
    ledger.record(ACME, Money.from_usd("5.00"))
    ledger.record(FREE, Money.from_usd("0.10"))
    assert ledger.spend_for(FREE.id) == Money.from_usd("0.10")
    assert ledger.spend_for("tnt_nobody") == Money.zero()
