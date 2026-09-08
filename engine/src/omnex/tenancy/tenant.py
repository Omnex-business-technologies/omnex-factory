"""Multi-tenancy: isolation, quotas, and usage that reconciles with the invoice.

The existing TypeScript side of this repo already does the hard part of billing
correctly — `consume_credits` is PL/pgSQL whose correctness *is* a row lock, and
CI asserts under concurrency that ten simultaneous spends of 20 against a
balance of 100 leave exactly five successes and a balance of zero. This module
is the engine-side counterpart: it decides what a tenant is allowed to do, and
records what they actually did, in a form that can be reconciled against that
ledger.

Three rules.

**Isolation is checked, not documented.** `TenantContext.require` fails loudly
when a query would cross a boundary, and the check is on the path rather than in
a comment. Every cross-tenant leak in history was in a system whose
documentation said tenants were isolated.

**A quota is checked before the work and recorded after it.** Checking
afterwards is an audit; recording before it is billing for work that failed.
Both halves are needed, and they are different calls on purpose.

**Usage is metered in exact `Money` and reconciled.** `UsageLedger.reconcile`
compares metered usage to what was actually billed and reports the difference,
because the two drift — a failed charge that was refunded, a retry that metered
twice — and a system that cannot detect the drift bills a customer wrongly for
months. Silence is not agreement.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum

from ..core.clock import Clock, SystemClock
from ..core.errors import BudgetExceeded, TenantIsolationViolation
from ..core.money import Money
from ..guard.ratelimit import Decision, RateLimit, RateLimiter

__all__ = [
    "Plan",
    "Quota",
    "QuotaCheck",
    "Reconciliation",
    "Tenant",
    "TenantContext",
    "UsageLedger",
    "UsageRecord",
]


class Plan(StrEnum):
    FREE = "free"
    STARTER = "starter"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"


@dataclass(frozen=True)
class Quota:
    """What a plan allows. Separate limits because they fail differently."""

    #: Requests per minute. Protects latency for everyone else.
    rate: RateLimit = field(default_factory=lambda: RateLimit(rate=60, period_seconds=60, burst=10))
    #: Spend ceiling for the billing period. Protects the operator's margin.
    monthly_spend: Money = field(default_factory=lambda: Money.from_usd("10.00"))
    #: Ceiling on one request. Protects against a single pathological prompt —
    #: a monthly cap alone lets one request eat the whole month.
    per_request_spend: Money = field(default_factory=lambda: Money.from_usd("0.05"))
    max_documents: int = 1_000

    @classmethod
    def for_plan(cls, plan: Plan) -> Quota:
        if plan is Plan.FREE:
            return cls(
                rate=RateLimit(rate=10, period_seconds=60, burst=3),
                monthly_spend=Money.from_usd("1.00"),
                per_request_spend=Money.from_usd("0.01"),
                max_documents=50,
            )
        if plan is Plan.STARTER:
            return cls(
                rate=RateLimit(rate=60, period_seconds=60, burst=10),
                monthly_spend=Money.from_usd("25.00"),
                per_request_spend=Money.from_usd("0.05"),
                max_documents=1_000,
            )
        if plan is Plan.GROWTH:
            return cls(
                rate=RateLimit(rate=300, period_seconds=60, burst=50),
                monthly_spend=Money.from_usd("250.00"),
                per_request_spend=Money.from_usd("0.25"),
                max_documents=25_000,
            )
        return cls(
            rate=RateLimit(rate=1200, period_seconds=60, burst=200),
            monthly_spend=Money.from_usd("5000.00"),
            per_request_spend=Money.from_usd("2.00"),
            max_documents=1_000_000,
        )


@dataclass(frozen=True)
class Tenant:
    id: str
    name: str
    plan: Plan = Plan.FREE

    @property
    def quota(self) -> Quota:
        return Quota.for_plan(self.plan)


@dataclass(frozen=True)
class TenantContext:
    """The tenant a request belongs to. Passed explicitly, never inferred.

    Not a thread-local or a global. An implicit current-tenant is convenient
    until one background job, one batch, or one `asyncio.gather` runs with
    whichever tenant was last set — and that bug does not raise, it just returns
    another customer's data.
    """

    tenant: Tenant

    @property
    def id(self) -> str:
        return self.tenant.id

    def require(self, resource_tenant_id: str, resource: str = "record") -> None:
        """Assert a resource belongs to this tenant. Never caught and continued."""
        if resource_tenant_id != self.tenant.id:
            raise TenantIsolationViolation(
                f"{resource} belongs to another tenant",
                requested_by=self.tenant.id,
                owned_by=resource_tenant_id,
            )

    def filter(self, where: dict[str, object] | None = None) -> dict[str, object]:
        """A metadata filter scoped to this tenant.

        The tenant key is set LAST so a caller-supplied filter cannot override
        it — the one filter that must never be negotiable.
        """
        return {**dict(where or {}), "tenant": self.tenant.id}


@dataclass(frozen=True)
class QuotaCheck:
    allowed: bool
    reason: str = ""
    rate: Decision | None = None
    remaining_spend: Money = field(default_factory=Money.zero)

    def raise_if_denied(self) -> None:
        if not self.allowed:
            raise BudgetExceeded(self.reason)


@dataclass(frozen=True)
class UsageRecord:
    tenant_id: str
    at: str
    kind: str
    cost: Money
    #: What this would have cost without the router and the cache. Carried so a
    #: tenant's invoice can show what the optimisation saved them, which is the
    #: difference between a bill and a bill they are happy to pay.
    undiscounted: Money = field(default_factory=Money.zero)
    units: int = 1
    request_id: str = ""


@dataclass(frozen=True)
class Reconciliation:
    metered: Money
    billed: Money

    @property
    def difference(self) -> Money:
        return self.metered - self.billed

    @property
    def matches(self) -> bool:
        return self.difference == Money.zero()

    def report(self) -> str:
        verdict = "matches" if self.matches else "DIFFERS"
        return (
            f"metered {self.metered.format_adaptive()} vs "
            f"billed {self.billed.format_adaptive()} — {verdict} "
            f"({self.difference.format_adaptive()})"
        )


@dataclass
class UsageLedger:
    """Records what each tenant used, and enforces the ceilings before they do."""

    clock: Clock = field(default_factory=SystemClock)
    records: list[UsageRecord] = field(default_factory=list)
    _limiters: dict[str, RateLimiter] = field(default_factory=dict)

    def _limiter(self, tenant: Tenant) -> RateLimiter:
        limiter = self._limiters.get(tenant.id)
        if limiter is None or limiter.limit != tenant.quota.rate:
            limiter = RateLimiter(tenant.quota.rate, clock=self.clock)
            self._limiters[tenant.id] = limiter
        return limiter

    def check(self, tenant: Tenant, estimated_cost: Money, consume_rate: bool = True) -> QuotaCheck:
        """Check every ceiling BEFORE doing the work.

        Rate is checked with `peek` when `consume_rate` is False, so a caller
        that may reject the request for another reason does not spend the
        tenant's quota on work that never ran.
        """
        quota = tenant.quota

        if estimated_cost > quota.per_request_spend:
            # Checked before the monthly cap: a single pathological request
            # should be named as such rather than reported as "out of budget",
            # which sends the customer to the wrong page of the docs.
            return QuotaCheck(
                False,
                f"request would cost {estimated_cost.format_adaptive()}, above the "
                f"{quota.per_request_spend.format_adaptive()} per-request limit on {tenant.plan}",
            )

        spent = self.spend_for(tenant.id)
        remaining = quota.monthly_spend - spent
        if spent + estimated_cost > quota.monthly_spend:
            return QuotaCheck(
                False,
                f"monthly spend {spent.format_adaptive()} of "
                f"{quota.monthly_spend.format_adaptive()} — {remaining.format_adaptive()} left",
                remaining_spend=remaining,
            )

        limiter = self._limiter(tenant)
        decision = limiter.check(tenant.id) if consume_rate else limiter.peek(tenant.id)
        if not decision.allowed:
            return QuotaCheck(
                False,
                f"rate limit: retry in {decision.retry_after:.1f}s",
                rate=decision,
                remaining_spend=remaining,
            )

        return QuotaCheck(True, rate=decision, remaining_spend=remaining)

    def record(
        self,
        tenant: Tenant,
        cost: Money,
        kind: str = "request",
        undiscounted: Money | None = None,
        units: int = 1,
        request_id: str = "",
    ) -> UsageRecord:
        """Record what was ACTUALLY used, after the work succeeded."""
        entry = UsageRecord(
            tenant_id=tenant.id,
            at=self.clock.now().isoformat(),
            kind=kind,
            cost=cost,
            undiscounted=undiscounted or cost,
            units=units,
            request_id=request_id,
        )
        self.records.append(entry)
        return entry

    # ── reporting ─────────────────────────────────────────────────────────
    def for_tenant(self, tenant_id: str) -> list[UsageRecord]:
        return [r for r in self.records if r.tenant_id == tenant_id]

    def spend_for(self, tenant_id: str) -> Money:
        total = Money.zero()
        for record in self.for_tenant(tenant_id):
            total = total + record.cost
        return total

    def saved_for(self, tenant_id: str) -> Money:
        total = Money.zero()
        for record in self.for_tenant(tenant_id):
            total = total + (record.undiscounted - record.cost)
        return total

    def invoice_cents(self, tenant_id: str) -> int:
        """The billable amount, rounded to cents exactly once, at the boundary.

        Rounding each record and summing the results is how a thousand
        sub-cent requests become a bill that is off by several dollars.
        """
        return self.spend_for(tenant_id).to_cents()

    def reconcile(self, tenant_id: str, billed: Money) -> Reconciliation:
        """Compare metered usage to what the payment processor actually took.

        These drift — a failed charge that was refunded, a retry that metered
        twice, a webhook processed out of order — and a system that cannot
        detect the drift bills a customer wrongly for months. Silence is not
        agreement.
        """
        return Reconciliation(metered=self.spend_for(tenant_id), billed=billed)

    def usage_by_kind(self, tenant_id: str) -> dict[str, Money]:
        out: dict[str, Money] = {}
        for record in self.for_tenant(tenant_id):
            out[record.kind] = out.get(record.kind, Money.zero()) + record.cost
        return dict(sorted(out.items(), key=lambda kv: -kv[1].picos))

    def statement(self, tenant: Tenant) -> str:
        spent = self.spend_for(tenant.id)
        saved = self.saved_for(tenant.id)
        lines = [
            f"{tenant.name} ({tenant.plan}): {spent.format_adaptive()} of "
            f"{tenant.quota.monthly_spend.format_adaptive()}, "
            f"{len(self.for_tenant(tenant.id))} requests",
        ]
        if saved:
            lines.append(f"  routing and caching saved {saved.format_adaptive()}")
        for kind, amount in self.usage_by_kind(tenant.id).items():
            lines.append(f"  {kind:<20} {amount.format_adaptive():>12}")
        return "\n".join(lines)


def assert_all_owned(context: TenantContext, tenant_ids: Sequence[str], resource: str) -> None:
    """Bulk isolation check, for a result set rather than one row."""
    for owner in tenant_ids:
        context.require(owner, resource)
