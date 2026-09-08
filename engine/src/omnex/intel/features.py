"""Feature mining: what a project claims to do, and what nobody claims at all.

## What this measures, precisely

Matching vocabulary in a README detects a **claim**, not an implementation. A
project whose front page says "rate limiting" has told us it believes rate
limiting matters to its audience; it has not told us the limiter works, is
distributed, or survives a restart. That distinction is the difference between
market research and an audit, and this module only does the first — so a mined
feature is capped at `Confidence.MEDIUM` and the cap is applied in code rather
than mentioned in prose.

This is not a weakness of the method. For competitive positioning, what a
project *advertises* is the more useful signal: it is what its users came for
and what a competitor must answer. The audit comes later, on the shortlist.

## Why the gap analysis is the valuable half

Everyone builds a feature matrix. A feature matrix tells you what exists, which
is the thing you can already see. Inverting it — features that appear in the
taxonomy, are demonstrably enterprise-relevant, and appear in *none* of the
projects in a cluster — tells you what to build. `CoverageMatrix.gaps()` returns
that, and `rarity` ranks it: a capability claimed by one project out of forty is
nearly as interesting as one claimed by none, because it is unlikely to be the
reason anybody chose the other thirty-nine.

The engine's own repository is the reference implementation of the answer. When
`gaps()` reports that a cluster of forty agent frameworks has no evaluation
story, that is not an abstract observation — `omnex.evals` exists, and the gap
is a distribution opportunity rather than a research project.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from .evidence import Artifact, Confidence

__all__ = [
    "TAXONOMY",
    "CoverageMatrix",
    "Feature",
    "FeatureHit",
    "Gap",
    "mine",
]


@dataclass(frozen=True)
class Feature:
    """One capability worth tracking across the ecosystem."""

    key: str
    category: str
    #: Alternative spellings the ecosystem actually uses. Matched
    #: case-insensitively on word boundaries — substring matching turns "auth"
    #: into a hit on "author", which is most of a README.
    patterns: tuple[str, ...]
    #: Would an enterprise buyer pay for this specifically? Drives gap ranking:
    #: a missing capability nobody would pay for is not an opportunity.
    enterprise_value: int = 1

    def matches(self, text: str) -> str:
        """The first matching phrase, or empty. Returned so a hit can be cited."""
        for pattern in self.patterns:
            found = re.search(rf"\b{re.escape(pattern)}\b", text, re.IGNORECASE)
            if found:
                return found.group(0)
        return ""


def _f(key: str, category: str, *patterns: str, value: int = 1) -> Feature:
    return Feature(key=key, category=category, patterns=patterns, enterprise_value=value)


#: The taxonomy from the brief, plus the spellings each concept actually appears
#: under. `enterprise_value` is 3 where a buyer procures the capability by name
#: (billing, security, observability, evaluation), 1 where it is table stakes.
TAXONOMY: tuple[Feature, ...] = (
    # ── retrieval ────────────────────────────────────────────────────────
    _f("rag", "retrieval", "rag", "retrieval augmented", "retrieval-augmented"),
    _f("graphrag", "retrieval", "graphrag", "graph rag", "knowledge graph", value=2),
    _f("vector_search", "retrieval", "vector search", "vector database", "embeddings"),
    _f("hybrid_search", "retrieval", "hybrid search", "bm25", "reciprocal rank", value=2),
    _f("reranking", "retrieval", "rerank", "reranker", "cross-encoder", value=2),
    _f("citations", "retrieval", "citation", "grounding", "provenance", value=3),
    _f("chunking", "retrieval", "chunking", "text splitter", "splitter"),
    # ── agents ───────────────────────────────────────────────────────────
    _f("multi_agent", "agents", "multi-agent", "multi agent", "swarm", "crew"),
    _f("tool_orchestration", "agents", "tool calling", "tool use", "function calling"),
    _f("mcp", "agents", "mcp", "model context protocol", value=2),
    _f("planning", "agents", "planner", "planning", "task decomposition"),
    _f("reasoning", "agents", "chain of thought", "reasoning", "reflection"),
    _f("memory", "agents", "memory", "long-term memory", "episodic", value=2),
    _f("workflow_engine", "agents", "workflow", "state machine", "dag", "graph execution"),
    _f(
        "human_in_the_loop", "agents", "human-in-the-loop", "human in the loop", "approval", value=3
    ),
    _f("skills", "agents", "skill", "skills", "plugin", "extension"),
    # ── platform ─────────────────────────────────────────────────────────
    _f("auth", "platform", "authentication", "oauth", "sso", "api key", value=2),
    _f("multi_tenancy", "platform", "multi-tenant", "multi tenant", "tenant", value=3),
    _f("billing", "platform", "billing", "stripe", "credits", "usage-based", value=3),
    _f("rate_limiting", "platform", "rate limit", "rate limiting", "throttle", value=2),
    _f("caching", "platform", "cache", "caching", "semantic cache", value=2),
    _f("plugin_architecture", "platform", "plugin", "adapter", "provider interface"),
    _f("deployment", "platform", "docker", "kubernetes", "helm", "terraform"),
    _f("ui_patterns", "platform", "dashboard", "web ui", "streaming ui", "playground"),
    # ── operations ───────────────────────────────────────────────────────
    _f("observability", "operations", "observability", "opentelemetry", "tracing", value=3),
    _f("logging", "operations", "logging", "structured logs", "audit log", value=2),
    _f("analytics", "operations", "analytics", "metrics", "prometheus"),
    _f("evaluation", "operations", "eval", "evals", "evaluation", "benchmark", value=3),
    _f("ab_testing", "operations", "a/b test", "ab testing", "experiment", value=2),
    _f("feedback_loops", "operations", "feedback loop", "human feedback", "rlhf", value=2),
    _f("ci_cd", "operations", "ci/cd", "github actions", "continuous integration"),
    _f("security", "operations", "guardrail", "prompt injection", "pii", "security", value=3),
    # ── economics ────────────────────────────────────────────────────────
    _f("model_routing", "economics", "model routing", "router", "fallback", value=3),
    _f(
        "cost_optimization",
        "economics",
        "cost optimization",
        "cost tracking",
        "token cost",
        value=3,
    ),
    _f("prompt_management", "economics", "prompt management", "prompt template", "versioning"),
    _f("local_models", "economics", "ollama", "llama.cpp", "local model", "on-premise", value=2),
    _f("quantization", "economics", "quantization", "quantized", "gguf", "awq"),
    _f("batching", "economics", "batching", "continuous batching", "vllm", value=2),
)


@dataclass(frozen=True)
class FeatureHit:
    feature: Feature
    matched_phrase: str

    @property
    def confidence(self) -> Confidence:
        """Capped at MEDIUM by construction.

        A README is evidence of a claim. Nothing mined from prose can be HIGH,
        because HIGH would mean we ran it.
        """
        return Confidence.MEDIUM


def mine(artifact: Artifact, taxonomy: tuple[Feature, ...] = TAXONOMY) -> list[FeatureHit]:
    """Which capabilities this project advertises.

    Searches the description and whatever corpus text was fetched — never the
    repository name alone, because a project called `agent-memory` matching
    `memory` on its own name is a tautology rather than a finding.
    """
    text = f"{artifact.description}\n{artifact.corpus}"
    hits: list[FeatureHit] = []
    for feature in taxonomy:
        phrase = feature.matches(text)
        if phrase:
            hits.append(FeatureHit(feature=feature, matched_phrase=phrase))
    return hits


@dataclass(frozen=True)
class Gap:
    """A capability the market wants and this cluster does not offer."""

    feature: Feature
    #: How many projects in the cluster claim it.
    claimed_by: int
    cluster_size: int

    @property
    def rarity(self) -> float:
        """0.0 = everybody has it, 1.0 = nobody does."""
        if not self.cluster_size:
            return 0.0
        return 1.0 - (self.claimed_by / self.cluster_size)

    @property
    def opportunity(self) -> float:
        """Rarity weighted by whether anyone would pay for it.

        A capability nobody has and nobody wants is not an opportunity, it is a
        reason. Multiplying by `enterprise_value` keeps the ranking honest about
        the difference.
        """
        return self.rarity * self.feature.enterprise_value

    def report(self) -> str:
        return (
            f"{self.feature.key:<22} {self.feature.category:<12} "
            f"claimed by {self.claimed_by:>3}/{self.cluster_size:<3} "
            f"rarity {self.rarity:.0%}  opportunity {self.opportunity:.2f}"
        )


@dataclass
class CoverageMatrix:
    """Feature claims across a set of projects, and what is missing from all of them.

    ## Why an artifact can be mined but not counted

    An artifact whose only text is a fifty-character registry summary tells us
    almost nothing about what it does. Counting it as "does not claim model
    routing" is wrong in a specific and dangerous way: `litellm`'s PyPI summary
    is "Library to easily interface with LLM API providers", which mentions
    neither routing nor cost — and litellm is one of the best known model
    routers in the ecosystem.

    Left uncorrected that produces the most confident possible version of the
    wrong answer: a gap analysis reporting that NOBODY does model routing,
    ranked top by rarity, published as an opportunity. The artifact was never
    evidence either way.

    So `min_corpus_chars` splits "did not claim it" from "we have no text to
    judge by". Thin artifacts are recorded in `uninformative` and excluded from
    the denominator — the same distinction the grounder draws when it calls a
    sentence NO_CLAIM rather than unsupported.
    """

    taxonomy: tuple[Feature, ...] = TAXONOMY
    #: Below this much text, absence of a feature is absence of evidence.
    #: A registry one-liner is ~50 chars; a README paragraph is several hundred.
    min_corpus_chars: int = 200
    #: artifact id -> feature keys claimed, for artifacts with enough text.
    claims: dict[str, set[str]] = field(default_factory=dict)
    #: artifact id -> characters available, for those that had too little.
    uninformative: dict[str, int] = field(default_factory=dict)

    def add(self, artifact: Artifact) -> list[FeatureHit]:
        hits = mine(artifact, self.taxonomy)
        text = f"{artifact.description}\n{artifact.corpus}".strip()
        if len(text) < self.min_corpus_chars:
            self.uninformative[artifact.id] = len(text)
            return hits
        self.claims[artifact.id] = {hit.feature.key for hit in hits}
        return hits

    @property
    def size(self) -> int:
        return len(self.claims)

    def counts(self) -> Counter[str]:
        counter: Counter[str] = Counter()
        for keys in self.claims.values():
            counter.update(keys)
        return counter

    def gaps(self, max_claimed_share: float = 0.15) -> list[Gap]:
        """Capabilities almost nobody in this cluster offers, ranked by opportunity.

        The threshold is a share rather than a count so the analysis behaves the
        same on a cluster of 20 and a cluster of 200. `0.15` catches both the
        genuinely absent and the nearly absent, because a capability one project
        in forty offers is not why anyone chose the other thirty-nine.
        """
        counts = self.counts()
        out: list[Gap] = []
        for feature in self.taxonomy:
            claimed = counts.get(feature.key, 0)
            if self.size and claimed / self.size <= max_claimed_share:
                out.append(Gap(feature=feature, claimed_by=claimed, cluster_size=self.size))
        return sorted(out, key=lambda gap: -gap.opportunity)

    def saturated(self, min_claimed_share: float = 0.6) -> list[Gap]:
        """The opposite end: what everybody already has.

        Useful in the other direction — building one of these is table stakes,
        not differentiation, and shipping it will not move a purchase decision.
        """
        counts = self.counts()
        out: list[Gap] = []
        for feature in self.taxonomy:
            claimed = counts.get(feature.key, 0)
            if self.size and claimed / self.size >= min_claimed_share:
                out.append(Gap(feature=feature, claimed_by=claimed, cluster_size=self.size))
        return sorted(out, key=lambda gap: -gap.claimed_by)
