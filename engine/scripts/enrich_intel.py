"""Build the committed evidence file the reports are generated from.

    python scripts/enrich_intel.py

## Why the GitHub records are a literal in this file

`omnex.intel.sources` documents the measured network reality: from inside this
environment PyPI, npm, crates.io and Docker Hub answer, while GitHub, Hugging
Face, arXiv and HN return 403 at the proxy. GitHub evidence therefore cannot be
fetched by this script, and pretending otherwise would produce a script that
silently emits an empty evidence file on every run.

So the GitHub readings below were fetched out of band — by an agent with a
browser tool, on the date recorded in `FETCHED_ON` — and are transcribed here as
data. Each carries the URL it came from and a short attributed excerpt, which is
exactly what `Evidence` is for. A future run with GitHub credentials replaces
this literal with a `GitHubSource` adapter and nothing downstream changes.

Recording them as a literal rather than as prose in a report is the point: the
figures become checkable data that `report.verify_document` compares rendered
claims against, so a number that drifts between the evidence and the narrative
is caught mechanically.

## What the registry half does

Package registries ARE reachable, so `enrich_registries()` fetches them live.
Their `requires_dist` / `dependencies` lists are the architecture declared by the
author in machine-readable form, which is what `reverse.infer` reads. Failures
are collected and reported rather than raised — a scan that dies on one renamed
package has thrown away the other ninety-nine fetches.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from omnex.intel import (
    Artifact,
    Confidence,
    Evidence,
    EvidenceFile,
    NpmSource,
    PypiSource,
    fetch_all,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
INTEL = REPO_ROOT / "intel"

#: The date every GitHub reading below was taken. One date, because a mixed-date
#: evidence file makes the growth arithmetic silently wrong.
FETCHED_ON = date(2026, 8, 5)


@dataclass(frozen=True)
class Reading:
    """One out-of-band GitHub observation, transcribed."""

    name: str
    stars: int
    forks: int
    language: str
    licence: str
    description: str
    #: Short attributed excerpt supporting the description and figures.
    excerpt: str

    def as_artifact(self) -> Artifact:
        url = f"https://github.com/{self.name}"
        return Artifact(
            id=f"github:{self.name}",
            name=self.name,
            source="github",
            url=url,
            description=self.description,
            language=self.language,
            licence=self.licence,
            popularity=self.stars,
            popularity_kind="stars",
            forks=self.forks,
            corpus=f"{self.description} {self.excerpt}",
            evidence=(
                Evidence(
                    url=url,
                    fetched_on=FETCHED_ON,
                    excerpt=self.excerpt,
                    # The project's own front page is authoritative about what it
                    # claims to be, and says nothing about whether it works.
                    confidence=Confidence.HIGH,
                ),
            ),
        )


#: Tier 1 — chosen by OMNEX relevance, not by star count.
READINGS: tuple[Reading, ...] = (
    Reading(
        "HKUDS/OpenSpace",
        7300,
        881,
        "Python",
        "MIT",
        "OpenSpace: The Skill Management Layer for AI Agents",
        "Skill retrieval, quality evaluation by real task outcomes, controlled evolution "
        "(FIX, DERIVED, CAPTURED), local-first hub. Python 3.12+, LiteLLM, SQLite, MCP, "
        "React + TypeScript dashboard. 7300 stars, 881 forks, MIT.",
    ),
    Reading(
        "openmemind/memind",
        903,
        91,
        "Java",
        "Apache-2.0",
        "Self-evolving cognitive memory and context engine for AI agents in Java",
        "Memory graphs, threads and Insight Trees; retrieval via REST, MCP, SDKs. Claims "
        "#1 among listed baselines on LoCoMo 86.88, LongMemEval 84.20, PersonaMem 67.91. "
        "903 stars, 91 forks, Apache-2.0.",
    ),
    Reading(
        "facebookresearch/HyperAgents",
        2700,
        348,
        "Python",
        "CC BY-NC-SA 4.0",
        "Self-referential self-improving agents that can optimize for any computable task",
        "Meta-agent generates and refines task-specific agents in a feedback loop; executes "
        "model-generated code in isolated domains. Python 3.12, Docker. Carries a safety "
        "warning about executing untrusted model-generated code. 2700 stars, 348 forks, "
        "licensed CC BY-NC-SA 4.0.",
    ),
    Reading(
        "neo4j-labs/create-context-graph",
        704,
        98,
        "Python",
        "Apache-2.0",
        "AI agents with graph based reasoning memory, scaffolded in seconds",
        "Scaffolds a full-stack agent app: FastAPI backend, neo4j-agent-memory, LiteLLM "
        "provider injection, Next.js frontend with SSE streaming and graph visualisation. "
        "Three-memory architecture: short-term, long-term entity graph, reasoning traces. "
        "704 stars, 98 forks, Apache-2.0.",
    ),
    Reading(
        "InternLM/WildClawBench",
        500,
        56,
        "Python",
        "MIT",
        "An in-the-wild benchmark for AI agents in the OpenClaw Environment",
        "60 tasks over six categories including Safety Alignment; graded 0.00-1.00 across "
        "four harnesses. Leaderboard reports execution time and API cost per model. "
        "500 stars, 56 forks, MIT.",
    ),
    Reading(
        "cisco-ai-defense/defenseclaw",
        806,
        139,
        "Go",
        "Apache-2.0",
        "Security governance for OpenClaw and agentic AI runtimes",
        "Scan capabilities before use, inspect runtime traffic, export durable audit "
        "evidence. Python CLI, Go gateway, policy engines, scanners, observability "
        "exporters. States it enforces policy and produces defensible records rather than "
        "proving an agent risk-free. 806 stars, 139 forks, Apache-2.0.",
    ),
    Reading(
        "slowmist/slowmist-agent-security",
        500,
        30,
        "Markdown",
        "MIT",
        "A comprehensive security review framework for AI agents in adversarial environments",
        "Review procedures for skills, repositories, URLs and blockchain addresses. "
        "Principle: every external input is untrusted until verified. Detection patterns "
        "across 26 attack categories with a risk-rating system. 500 stars, 30 forks, MIT.",
    ),
    Reading(
        "patoles/agent-flow",
        1500,
        162,
        "TypeScript",
        "Apache-2.0",
        "Real-time visualization of Claude Code agent orchestration",
        "Event relay server receiving agent hooks over HTTP and streaming via SSE, Next.js "
        "canvas for the node graph, VS Code extension. Concurrent multi-session monitoring "
        "and JSONL replay. 1500 stars, 162 forks, Apache-2.0.",
    ),
    Reading(
        "saltbo/agent-kanban",
        434,
        35,
        "TypeScript",
        "FSL-1.1-ALv2",
        "An agent-first task board, Mission control for your AI workforce",
        "Each agent gets an Ed25519 identity, claims tasks, opens pull requests and "
        "self-organises into teams. Task dependencies and cross-repository support. "
        "434 stars, 35 forks, FSL-1.1-ALv2 converting to Apache-2.0 after two years.",
    ),
    Reading(
        "soulduse/ai-token-monitor",
        306,
        51,
        "TypeScript",
        "MIT",
        "macOS menu bar app for tracking Claude Code token usage and costs",
        "Rust backend watches local JSONL session files, parses token counts, applies "
        "per-model pricing including cache read costs. Offline by default. Optional "
        "Supabase and webhook integrations. 306 stars, 51 forks, MIT.",
    ),
    Reading(
        "oguzbilgic/agent-kernel",
        335,
        40,
        "Markdown",
        "MIT",
        "Minimal kernel to make any AI coding agent stateful",
        "Three markdown files as the kernel — AGENTS.md, IDENTITY.md, KNOWLEDGE.md — plus "
        "knowledge/ and append-only notes/ directories in a git repository. No database "
        "and no vector store. 335 stars, 40 forks, MIT.",
    ),
    Reading(
        "Ataraxy-Labs/opensessions",
        1200,
        70,
        "Rust",
        "MIT",
        "tmux sidebar for coding agents with per-thread markers and a local HTTP API",
        "Sidebar showing live session state, status pills, logs and detected localhost "
        "ports inside tmux. Local HTTP API lets scripts and agents push metadata. "
        "1200 stars, 70 forks, MIT.",
    ),
    Reading(
        "ovoment/ovo-local-llm",
        104,
        18,
        "TypeScript",
        "MIT",
        "A private Claude-Code-style coding agent for Apple Silicon",
        "MLX-native, Ollama and OpenAI API compatible, zero API keys. Monaco editor, git "
        "panel, terminal, MCP servers, local diffusion image generation, document RAG and "
        "LoRA fine-tuning. 104 stars, 18 forks, MIT.",
    ),
    Reading(
        "slavingia/skills",
        9800,
        1000,
        "Markdown",
        "",
        "Claude Code skills based on The Minimalist Entrepreneur",
        "10 skills covering community, idea validation, MVP, first customers, pricing, "
        "marketing, growth, values and business review. Installed through the Claude Code "
        "plugin marketplace. 9800 stars, 1000 forks, no licence file.",
    ),
    Reading(
        "alvinunreal/awesome-opensource-ai",
        4400,
        563,
        "Markdown",
        "CC0-1.0",
        "Curated list of the best truly open-source AI projects, models, tools",
        "Daily updated curation of models, development tools and infrastructure, scoped to "
        "genuinely open-source projects. 4400 stars, 563 forks, CC0-1.0.",
    ),
)

#: Registry packages worth a live read — the substitutes and the components a
#: build would actually pull. Fetched, not transcribed.
PYPI_PACKAGES = ["litellm", "langgraph", "crewai", "mem0ai", "qdrant-client", "deepeval", "ragas"]
NPM_PACKAGES = ["ai", "@modelcontextprotocol/sdk", "langchain"]


def build() -> tuple[EvidenceFile, list[tuple[str, str]]]:
    evidence = EvidenceFile(fetched_on=FETCHED_ON)
    for reading in READINGS:
        evidence.add(reading.as_artifact())

    failures: list[tuple[str, str]] = []
    for source, names in ((PypiSource(), PYPI_PACKAGES), (NpmSource(), NPM_PACKAGES)):
        found, failed = fetch_all(source, names)
        for artifact in found:
            evidence.add(artifact)
        failures.extend(failed)

    return evidence, failures


def main() -> int:
    INTEL.mkdir(parents=True, exist_ok=True)
    evidence, failures = build()

    out = INTEL / f"evidence_{FETCHED_ON.isoformat().replace('-', '')}.json"
    out.write_text(json.dumps(evidence.as_dict(), indent=2, sort_keys=True) + "\n")

    by_source: dict[str, int] = {}
    for artifact in evidence.artifacts.values():
        by_source[artifact.source] = by_source.get(artifact.source, 0) + 1

    print(f"{len(evidence.artifacts)} artifacts written to {out.relative_to(REPO_ROOT)}")
    for source, count in sorted(by_source.items()):
        print(f"  {source:<12} {count:>3}")
    if failures:
        # Reported rather than swallowed: a source that quietly returned nothing
        # looks exactly like a source with nothing to report.
        print(f"\n{len(failures)} fetch failures:")
        for identifier, reason in failures:
            print(f"  {identifier:<28} {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
