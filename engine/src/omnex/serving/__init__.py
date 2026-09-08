"""P14 — inference serving: batching, KV-cache routing, capacity.

Three levers decide whether self-hosting beats a hosted API, and none is the GPU:
continuous batching (static batching returns when the LONGEST sequence in the
batch finishes), prefix-aware routing (every RAG request shares a system prompt,
and routing to a replica that already has it in cache skips most of the
prefill), and planning capacity with Little's Law at 70% utilisation rather than
adding replicas until it feels fast.
"""

from .batching import (
    BatchResult,
    CapacityPlan,
    PrefixAwareBalancer,
    QuantizationProfile,
    Request,
    plan_capacity,
    simulate,
)

__all__ = [
    "BatchResult",
    "CapacityPlan",
    "PrefixAwareBalancer",
    "QuantizationProfile",
    "Request",
    "plan_capacity",
    "simulate",
]
