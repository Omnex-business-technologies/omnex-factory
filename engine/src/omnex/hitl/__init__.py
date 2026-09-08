"""P15 — human-in-the-loop.

The load-bearing idea: **an approval is bound to the exact proposal that was
shown.** A decision keyed only on a request id lets an agent re-plan between
asking and answering, so the human's "yes" authorises something they never saw.
Every decision records the fingerprint of what the approver actually read, and
`authorises()` refuses when the proposal has changed since.

Uncertainty detection is tuned to ask rarely — an approver seeing forty requests
an hour approves the forty-first without reading it — with irreversibility as an
overriding rule rather than another weighted signal.
"""

from .approval import (
    ApprovalRequest,
    ApprovalStore,
    Decision,
    Proposal,
    UncertaintyDetector,
    UncertaintySignal,
    Verdict,
)

__all__ = [
    "ApprovalRequest",
    "ApprovalStore",
    "Decision",
    "Proposal",
    "UncertaintyDetector",
    "UncertaintySignal",
    "Verdict",
]
