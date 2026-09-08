"""P3 — multi-agent research with consensus and a tamper-evident audit trail.

Two positions differ from the usual supervisor-plus-workers design:

- **A fact-checker holds a veto, not a vote.** An agent that found a claim
  unsupported has found something the others did not look for; counting it as
  one of three is how an unsupported claim ships with two agreeing votes. A
  supervisor can override, but only via `override()`, which names them in the
  audit trail — an escape hatch that exists because a system with no way past
  the fact-checker gets routed around entirely.
- **Disagreement is preserved, not averaged.** Two yes and one no is a question
  for a human, not "67% confident". `contested` is what P15 reads.

The audit trail is hash-chained. It cannot prevent tampering — nothing
in-process can — but `verify()` names the first broken entry, and detectable is
what "auditable" actually means.
"""

from .audit import GENESIS, AuditEntry, AuditTrail
from .consensus import Consensus, Crew, Opinion, Position, Role, decide, override

__all__ = [
    "GENESIS",
    "AuditEntry",
    "AuditTrail",
    "Consensus",
    "Crew",
    "Opinion",
    "Position",
    "Role",
    "decide",
    "override",
]
