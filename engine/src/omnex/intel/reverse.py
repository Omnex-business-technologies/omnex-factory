"""Architecture inference from declared dependencies.

Reverse engineering at architectural level does not require reading anybody's
source, and reading the source is usually the slower route anyway. A dependency
manifest is the architecture stated by the author in machine-readable form: a
package that declares `fastapi`, `celery` and `redis` has an HTTP tier, an async
worker tier and a broker, and it has said so more reliably than its README will.

Three rules keep this from becoming astrology.

**Every inference carries the dependency that produced it.** `Claim.evidence`
holds the manifest URL; a claim with nothing behind it renders as UNKNOWN rather
than as a confident sentence about a system nobody looked at.

**Absence is reported as absence, never as a negative finding.** A project with
no observability dependency may export telemetry through an interface, or in a
sibling package, or not at all. The claim is "declares no telemetry dependency",
which is a fact, rather than "has no observability", which is a guess wearing a
fact's clothes.

**Failure points come from combinations, not from checklists.** `redis` alone is
unremarkable. `redis` serving as both Celery broker and application cache is a
specific, nameable operational hazard — a cache flush destroys queued work — and
that is the class of finding worth writing down, because it is the one the
project's own documentation will not contain.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .evidence import Artifact, Claim, Confidence, Evidence

__all__ = [
    "SIGNATURES",
    "ArchitectureReport",
    "Layer",
    "infer",
]


@dataclass(frozen=True)
class Layer:
    """One architectural role, and the packages that indicate it."""

    key: str
    description: str
    packages: frozenset[str]
    #: Does depending on this imply a separate process to run and pay for?
    adds_infrastructure: bool = False


def _layer(key: str, description: str, *packages: str, infra: bool = False) -> Layer:
    return Layer(key, description, frozenset(packages), infra)


SIGNATURES: tuple[Layer, ...] = (
    _layer(
        "http",
        "synchronous HTTP tier",
        "fastapi",
        "flask",
        "django",
        "express",
        "starlette",
        "next",
        "hono",
        "koa",
        "aiohttp",
    ),
    _layer(
        "worker",
        "asynchronous worker tier",
        "celery",
        "rq",
        "dramatiq",
        "bullmq",
        "arq",
        "temporalio",
        infra=True,
    ),
    _layer(
        "broker",
        "message broker",
        "kombu",
        "pika",
        "kafka-python",
        "confluent-kafka",
        "amqplib",
        "nats-py",
        infra=True,
    ),
    _layer(
        "cache", "cache or ephemeral store", "redis", "aiocache", "ioredis", "memcached", infra=True
    ),
    _layer(
        "relational",
        "relational database",
        "sqlalchemy",
        "psycopg",
        "psycopg2",
        "asyncpg",
        "prisma",
        "drizzle-orm",
        "pg",
        "mysqlclient",
        infra=True,
    ),
    _layer("embedded_db", "embedded datastore", "sqlite3", "aiosqlite", "duckdb", "better-sqlite3"),
    _layer(
        "vector",
        "vector index",
        "qdrant-client",
        "chromadb",
        "pinecone-client",
        "weaviate-client",
        "lancedb",
        "faiss-cpu",
        "faiss-gpu",
        "pgvector",
        "milvus",
        infra=True,
    ),
    _layer(
        "llm_api",
        "hosted model provider",
        "openai",
        "anthropic",
        "litellm",
        "cohere",
        "google-generativeai",
        "mistralai",
    ),
    _layer(
        "llm_local",
        "local inference",
        "vllm",
        "llama-cpp-python",
        "ollama",
        "transformers",
        "ctranslate2",
        infra=True,
    ),
    _layer(
        "orchestration",
        "agent orchestration framework",
        "langchain",
        "langgraph",
        "llama-index",
        "crewai",
        "autogen",
        "haystack-ai",
        "dspy-ai",
    ),
    _layer(
        "telemetry",
        "telemetry export",
        "opentelemetry-api",
        "opentelemetry-sdk",
        "prometheus-client",
        "sentry-sdk",
        "datadog",
        "langsmith",
    ),
    _layer(
        "queueing_cloud",
        "managed cloud services",
        "boto3",
        "google-cloud-storage",
        "azure-storage-blob",
        infra=True,
    ),
    _layer(
        "ui", "shipped user interface", "react", "vue", "svelte", "streamlit", "gradio", "textual"
    ),
    _layer("auth", "authentication", "authlib", "python-jose", "passlib", "next-auth", "supabase"),
    _layer("payments", "payments", "stripe", "paddle-sdk", "lemonsqueezy"),
)


@dataclass
class ArchitectureReport:
    """What can be said about a system's shape, and what cannot."""

    artifact_id: str
    layers: list[Layer] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    failure_points: list[Claim] = field(default_factory=list)

    @property
    def layer_keys(self) -> set[str]:
        return {layer.key for layer in self.layers}

    @property
    def operational_complexity(self) -> int:
        """How many separate things somebody has to run, monitor and pay for.

        The number that decides whether a small team can actually adopt this,
        and the one no project's landing page ever states.
        """
        return sum(1 for layer in self.layers if layer.adds_infrastructure)

    @property
    def confidence(self) -> Confidence:
        if not self.claims:
            return Confidence.NONE
        return max(claim.confidence for claim in self.claims)

    def report(self) -> str:
        lines = [
            f"{self.artifact_id} — {len(self.layers)} layers, "
            f"operational complexity {self.operational_complexity} "
            f"({self.confidence} confidence)"
        ]
        for claim in self.claims:
            lines.append(f"  · {claim.render()}")
        if self.failure_points:
            lines.append("  failure points:")
            for claim in self.failure_points:
                lines.append(f"    ! {claim.render()}")
        return "\n".join(lines)


def infer(artifact: Artifact) -> ArchitectureReport:
    """Read the declared dependencies and say what they imply.

    `artifact.tags` carries the dependency list the registry adapters collected.
    An artifact with no dependency data yields a report whose every claim is
    UNKNOWN — which is the correct output, and visibly different from a report
    about a simple system.
    """
    report = ArchitectureReport(artifact_id=artifact.id)
    declared = {tag.lower() for tag in artifact.tags}

    if not declared:
        report.claims.append(
            Claim(
                "no dependency manifest was collected, so architecture is not inferable "
                "from public metadata"
            )
        )
        return report

    manifest = Evidence(
        url=artifact.url,
        fetched_on=_first_fetch_date(artifact),
        excerpt=", ".join(sorted(declared)[:20]),
        # A dependency list is authoritative about what is depended on, and
        # says nothing about how well any of it is used.
        confidence=Confidence.MEDIUM,
    )

    for layer in SIGNATURES:
        hit = declared & layer.packages
        if not hit:
            continue
        report.layers.append(layer)
        report.claims.append(
            Claim(f"has a {layer.description} (declares {', '.join(sorted(hit))})", (manifest,))
        )

    keys = report.layer_keys
    report.claims.append(
        Claim(
            f"requires {report.operational_complexity} separately-operated component(s) "
            f"beyond the application process",
            (manifest,),
        )
    )
    report.failure_points.extend(_failure_points(keys, declared, manifest))
    return report


def _failure_points(keys: set[str], declared: set[str], manifest: Evidence) -> list[Claim]:
    """Hazards that come from combinations, which is where the real ones live."""
    found: list[Claim] = []

    if "worker" in keys and "cache" in keys and "redis" in declared:
        found.append(
            Claim(
                "Redis appears to serve as both the task broker and the application cache; "
                "a routine cache flush destroys queued work, and the two have opposite "
                "durability requirements",
                (manifest,),
            )
        )

    if "vector" in keys and "cache" not in keys:
        found.append(
            Claim(
                "a vector index with no cache layer declared — every repeated query pays "
                "the embedding call again, which is the single largest avoidable cost in "
                "a retrieval system",
                (manifest,),
            )
        )

    if "llm_api" in keys and "telemetry" not in keys:
        found.append(
            Claim(
                "calls a paid model provider but declares no telemetry dependency; spend "
                "and latency regressions surface on the invoice rather than on a dashboard",
                (manifest,),
            )
        )

    if "llm_api" in keys and len(declared & _PROVIDERS) == 1:
        found.append(
            Claim(
                f"depends on a single model provider ({', '.join(sorted(declared & _PROVIDERS))}); "
                "a provider outage or price change has no fallback path",
                (manifest,),
            )
        )

    if "http" in keys and "worker" not in keys and "llm_api" in keys:
        found.append(
            Claim(
                "long-running model calls inside a synchronous HTTP tier with no worker "
                "declared — request timeouts and connection limits become the throughput "
                "ceiling well before the model does",
                (manifest,),
            )
        )

    if "relational" in keys and "auth" in keys and "payments" not in keys:
        found.append(
            Claim(
                "stores user accounts but declares no payment integration; monetisation "
                "is either absent or lives outside this component",
                (manifest,),
            )
        )

    return found


_PROVIDERS = frozenset({"openai", "anthropic", "cohere", "google-generativeai", "mistralai"})


def _first_fetch_date(artifact: Artifact):  # type: ignore[no-untyped-def]
    if artifact.evidence:
        return artifact.evidence[0].fetched_on
    from datetime import date

    return date.today()
