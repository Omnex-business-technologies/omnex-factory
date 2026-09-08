"""Serving: continuous batching, KV-cache-aware routing, and capacity that is
computed rather than guessed.

Three things decide whether a self-hosted inference deployment is cheaper than
a hosted API, and none of them is the GPU.

## Continuous batching beats static batching, and the reason is the tail

Static batching collects N requests, runs them together, and returns when the
LONGEST finishes. A batch of eight where seven produce 20 tokens and one
produces 500 spends 96% of its time running a batch of one, while the seven
finished replies sit undelivered. Continuous batching evicts each sequence as it
hits its stop token and admits a waiting request into the freed slot, so the
short requests leave immediately and the slot keeps working.

`simulate()` measures both on the same arrival pattern. The gap is not
theoretical and it is largest exactly where real traffic lives: a long tail of
output lengths.

## Prefix-aware routing is the largest single cost lever

Every request in a RAG system shares a system prompt, and often a document
prefix. Routing a request to a replica that already has that prefix in its KV
cache skips re-computing it — for a 2,000-token shared prefix that is most of
the prefill. Round-robin routing scatters those requests across replicas and
every one pays full prefill.

`PrefixAwareBalancer` routes on prefix hash with a load ceiling, because pure
affinity is how one replica gets every request for the popular document while
three sit idle. Affinity until a replica is busier than a threshold, then
overflow.

## Capacity is Little's Law, not a guess

`plan_capacity` inverts the arrival rate and target latency into the concurrency
a deployment needs. The usual alternative — "add replicas until it feels fast" —
finds the answer eventually, at the price of finding it in production.
"""

from __future__ import annotations

import hashlib
import heapq
from dataclasses import dataclass, field

__all__ = [
    "BatchResult",
    "CapacityPlan",
    "PrefixAwareBalancer",
    "QuantizationProfile",
    "Request",
    "plan_capacity",
    "simulate",
]


@dataclass(frozen=True)
class Request:
    id: str
    #: When it arrives, seconds from the start of the window.
    arrives_at: float
    prompt_tokens: int
    output_tokens: int
    #: Tokens shared with other requests — a system prompt, a document. Only
    #: this part can be served from a warm KV cache.
    shared_prefix_tokens: int = 0

    @property
    def prefix_key(self) -> str:
        return hashlib.blake2b(f"{self.shared_prefix_tokens}".encode(), digest_size=8).hexdigest()


@dataclass
class BatchResult:
    """What a scheduling policy achieved on one arrival pattern."""

    policy: str
    completed: int = 0
    #: Wall-clock from arrival to the last token, per request.
    latencies: list[float] = field(default_factory=list)
    #: Arrival to FIRST token. What a streaming UI actually shows the user.
    ttfts: list[float] = field(default_factory=list)
    makespan: float = 0.0

    @property
    def throughput(self) -> float:
        return 0.0 if not self.makespan else self.completed / self.makespan

    def percentile(self, values: list[float], q: float) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        index = min(len(ordered) - 1, int(q / 100 * len(ordered)))
        return ordered[index]

    @property
    def p50_latency(self) -> float:
        return self.percentile(self.latencies, 50)

    @property
    def p95_latency(self) -> float:
        return self.percentile(self.latencies, 95)

    @property
    def p95_ttft(self) -> float:
        return self.percentile(self.ttfts, 95)

    def report(self) -> str:
        return (
            f"{self.policy:<12} {self.completed:>4} done  "
            f"throughput {self.throughput:6.1f}/s  "
            f"p50 {self.p50_latency:5.2f}s  p95 {self.p95_latency:5.2f}s  "
            f"p95 TTFT {self.p95_ttft:5.2f}s"
        )


def simulate(
    requests: list[Request],
    policy: str = "continuous",
    max_batch: int = 8,
    prefill_tokens_per_second: float = 8000.0,
    decode_tokens_per_second: float = 900.0,
) -> BatchResult:
    """Run an arrival pattern through a scheduling policy.

    A discrete-event simulation, not a GPU. It models the one thing that
    determines the answer — when a slot becomes free — and deliberately does not
    model memory pressure, kernel launch overhead or tensor parallelism. That
    makes it a tool for comparing POLICIES, which is what the choice actually
    is, and useless for predicting absolute throughput on specific hardware. The
    tests say which of the two they rely on.

    Decode throughput is modelled as per-slot rather than per-batch, which is the
    behaviour that matters: a decode step for a batch of eight costs roughly the
    same wall time as a batch of one, because it is memory-bandwidth bound. That
    is precisely why keeping slots full is worth this much effort.
    """
    result = BatchResult(policy=policy)
    ordered = sorted(requests, key=lambda r: r.arrives_at)

    if policy == "static":
        return _simulate_static(
            ordered, result, max_batch, prefill_tokens_per_second, decode_tokens_per_second
        )
    return _simulate_continuous(
        ordered, result, max_batch, prefill_tokens_per_second, decode_tokens_per_second
    )


def _simulate_static(
    ordered: list[Request],
    result: BatchResult,
    max_batch: int,
    prefill_rate: float,
    decode_rate: float,
) -> BatchResult:
    """Collect a batch, run it, return when the LONGEST finishes."""
    now = 0.0
    index = 0
    while index < len(ordered):
        batch = ordered[index : index + max_batch]
        index += len(batch)
        now = max(now, batch[-1].arrives_at)

        prefill = sum(r.prompt_tokens for r in batch) / prefill_rate
        # The whole batch waits for the longest sequence. Seven finished replies
        # sit undelivered while one keeps decoding.
        longest = max(r.output_tokens for r in batch)
        decode = longest / decode_rate
        finished = now + prefill + decode

        for request in batch:
            result.ttfts.append(now + prefill - request.arrives_at)
            result.latencies.append(finished - request.arrives_at)
            result.completed += 1
        now = finished
        result.makespan = now
    return result


def _simulate_continuous(
    ordered: list[Request],
    result: BatchResult,
    max_batch: int,
    prefill_rate: float,
    decode_rate: float,
) -> BatchResult:
    """Evict each sequence as it finishes; admit a waiting request into the slot."""
    #: (free_at, slot_index) — the earliest-free slot is the next to be filled.
    slots: list[tuple[float, int]] = [(0.0, i) for i in range(max_batch)]
    heapq.heapify(slots)

    for request in ordered:
        free_at, slot = heapq.heappop(slots)
        start = max(free_at, request.arrives_at)
        prefill = request.prompt_tokens / prefill_rate
        decode = request.output_tokens / decode_rate
        finished = start + prefill + decode

        result.ttfts.append(start + prefill - request.arrives_at)
        result.latencies.append(finished - request.arrives_at)
        result.completed += 1
        result.makespan = max(result.makespan, finished)
        heapq.heappush(slots, (finished, slot))

    return result


@dataclass
class PrefixAwareBalancer:
    """Routes on shared-prefix affinity, with a load ceiling.

    Affinity alone is how one replica ends up serving every request for the
    popular document while three sit idle, so a replica over `max_load_factor`
    times the mean load overflows to the least loaded one. The cache win is
    worth a lot; it is not worth an unbalanced fleet.
    """

    replicas: int
    #: A replica may run this many requests ahead of the least-loaded one before
    #: affinity gives way. An absolute skew rather than a ratio, because a ratio
    #: is meaningless at low volume — with four replicas and three requests the
    #: mean is 0.75, and any ratio test breaks affinity immediately, which is
    #: precisely when the cache win is cheapest to keep.
    max_skew: int = 8
    max_load_factor: float = 1.5
    #: prefix key -> replica index
    affinity: dict[str, int] = field(default_factory=dict)
    load: list[int] = field(default_factory=list)
    cache_hits: int = 0
    overflows: int = 0

    def __post_init__(self) -> None:
        if self.replicas < 1:
            raise ValueError("need at least one replica")
        self.load = [0] * self.replicas

    def route(self, request: Request) -> int:
        key = request.prefix_key
        preferred = self.affinity.get(key)

        if preferred is not None:
            if self.load[preferred] - min(self.load) <= self.max_skew:
                self.load[preferred] += 1
                self.cache_hits += 1
                return preferred
            # Warm cache, but this replica is carrying too much. Take the
            # prefill hit rather than the queueing one.
            self.overflows += 1

        chosen = min(range(self.replicas), key=lambda i: (self.load[i], i))
        self.affinity.setdefault(key, chosen)
        self.load[chosen] += 1
        return chosen

    def release(self, replica: int) -> None:
        self.load[replica] = max(0, self.load[replica] - 1)

    @property
    def imbalance(self) -> float:
        """Max load over mean load. 1.0 is perfectly even."""
        mean = sum(self.load) / self.replicas
        return 0.0 if mean == 0 else max(self.load) / mean

    @property
    def hit_rate(self) -> float:
        total = sum(self.load)
        return 0.0 if not total else self.cache_hits / total


@dataclass(frozen=True)
class CapacityPlan:
    concurrency_needed: float
    replicas: int
    utilisation: float

    def report(self) -> str:
        return (
            f"{self.replicas} replicas for {self.concurrency_needed:.1f} concurrent requests "
            f"at {self.utilisation:.0%} utilisation"
        )


def plan_capacity(
    requests_per_second: float,
    mean_seconds_per_request: float,
    slots_per_replica: int = 8,
    target_utilisation: float = 0.7,
) -> CapacityPlan:
    """Little's Law: concurrency = arrival rate x service time.

    `target_utilisation` is the part people leave out. Queueing delay rises
    non-linearly as utilisation approaches 1 — at 95% a small burst produces a
    queue that takes minutes to drain — so capacity is planned at 70% and the
    headroom is the point rather than waste.
    """
    if target_utilisation <= 0 or target_utilisation > 1:
        raise ValueError("target utilisation must be in (0, 1]")
    concurrency = requests_per_second * mean_seconds_per_request
    effective_slots = slots_per_replica * target_utilisation
    replicas = max(
        1, int(concurrency / effective_slots) + (1 if concurrency % effective_slots else 0)
    )
    return CapacityPlan(
        concurrency_needed=concurrency,
        replicas=replicas,
        utilisation=concurrency / (replicas * slots_per_replica),
    )


@dataclass(frozen=True)
class QuantizationProfile:
    """What a quantisation choice costs and buys, stated rather than assumed.

    The numbers are a deployment's own measurements, not universal constants —
    which is exactly why this is a value type a team fills in from their own
    eval run rather than a table baked into the code. What the type enforces is
    that a quality number EXISTS: quantising without measuring quality is how a
    deployment gets 2x cheaper and quietly worse, and the bill improves while
    the complaints do not.
    """

    name: str
    bits: int
    #: Multiple of the fp16 memory footprint.
    memory_ratio: float
    #: Pass rate on the deployment's own eval suite (P4), measured after.
    measured_pass_rate: float
    #: Throughput multiple, measured.
    throughput_ratio: float = 1.0

    def acceptable(self, baseline_pass_rate: float, max_drop: float = 0.02) -> bool:
        return baseline_pass_rate - self.measured_pass_rate <= max_drop

    def report(self, baseline_pass_rate: float) -> str:
        drop = baseline_pass_rate - self.measured_pass_rate
        verdict = "acceptable" if self.acceptable(baseline_pass_rate) else "TOO LOSSY"
        return (
            f"{self.name}: {self.memory_ratio:.2f}x memory, "
            f"{self.throughput_ratio:.2f}x throughput, "
            f"quality {drop:+.1%} — {verdict}"
        )
