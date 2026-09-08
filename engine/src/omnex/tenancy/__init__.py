"""P10 — multi-tenant isolation, quotas and usage metering.

The TypeScript side of this repo already holds the hard part of billing: a
PL/pgSQL `consume_credits` whose correctness IS a row lock, asserted under
concurrency against a real Postgres. This is the engine-side counterpart —
what a tenant is allowed to do, and what they actually did, in a form that
reconciles against that ledger.

Isolation is checked on the path rather than described in a comment; every
cross-tenant leak in history was in a system whose documentation said tenants
were isolated. `TenantContext` is passed explicitly and never inferred from a
thread-local, because an implicit current-tenant works until one background job
or one `asyncio.gather` runs with whichever tenant was set last — and that bug
does not raise, it returns another customer's data.
"""

from .tenant import (
    Plan,
    Quota,
    QuotaCheck,
    Reconciliation,
    Tenant,
    TenantContext,
    UsageLedger,
    UsageRecord,
)

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
