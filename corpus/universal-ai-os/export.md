# Universal AI OS — Complete Export

Generated 2026-08-17T06:11:13.760Z · Source corpus: *AI Engineering: System Design Patterns for LLMs, RAG and Agents* (Akshay Pachaar & Avi Chawla), 439 pages.

**Contents:** 28 ontology branches · 507 nodes · 509 reconstructed figures · 481 duplicate groups · 325 source pages.

---

## Table of contents

1. [Specification](#1-specification)
2. [The 10/10 standard](#2-the-1010-standard)
3. [Layers](#3-layers)
4. [Ontology — all branches and nodes](#4-ontology--all-branches-and-nodes)
5. [Figure manifest — index](#5-figure-manifest--index)
6. [Figure manifest — full records](#6-figure-manifest--full-records)
7. [Cross-reference: branch → figures](#7-cross-reference-branch--figures)
8. [Chapter map](#8-chapter-map)
9. [Duplicate groups](#9-duplicate-groups)
10. [Statistics](#10-statistics)

---

## 1. Specification


Scope raised from "AI Architecture Atlas" to a universal AI/Agentic Engineering + Automation + Business operating system. The book is the seed corpus, not the boundary: the ontology is an **open tree** that keeps growing.

Honest framing: nothing here guarantees revenue. What the system guarantees is a **standard** — every sector, layer, pattern, framework, protocol, agent, workflow and revenue model is held to the same bar, and new branches are discovered continuously instead of being pre-enumerated.

```text
KNOWLEDGE ENGINE   ARCHITECTURE ENGINE   OPPORTUNITY ENGINE
        \                 |                    /
              KNOWLEDGE GRAPH (Atlas OS)
                          v
                    AGENT FACTORY
                          v
                  ORCHESTRATION OS
        (single / multi-agent / agent networks)
                          v
        EXECUTION FABRIC: n8n + code/APIs + MCP/A2A
                          v
    BUSINESS SYSTEMS -> PRODUCTS -> CUSTOMERS -> REVENUE
                          v
     UNIT ECONOMICS -> PORTFOLIO -> SELF-OPTIMIZATION
                          '-----> back into KNOWLEDGE
```

## 1. The 10/10 standard (applies to every node)

No node is complete until all ten dimensions are answered: **Capability** (what it does), **Architecture** (how it is built), **Execution** (how it actually runs), **Integration** (what it connects to), **Reliability** (what happens when it fails), **Security** (how it is contained), **Evaluation** (how we prove it works), **Economics** (what it costs and is worth), **Scalability** (how it grows without breaking), **Evolution** (how it improves itself).

Each node shows a completeness score (n/10) with the missing dimensions named. Nodes are never framework-bound: frameworks, tools and protocols are *instances* attached to a neutral category, each scored on the same ten dimensions.

## 2. Ontology — the open tree

Seeded with 28 branches; every branch is expandable and versioned.

I Foundational CS · II Software Architecture (+ resilience patterns) · III AI/ML Foundation · IV LLM Engineering · V Context Engineering · VI RAG / Knowledge Engineering · VII Agentic AI · VIII Multi-Agent · IX Agent Memory (+ capture→store→index→retrieve→rank→compress→consolidate→expire→forget) · X Agent Orchestration (graph / role / loop / workflow / event / hierarchical / human, framework-neutral abstraction over LangGraph, CrewAI, MS Agent Framework, Google ADK, OpenAI Agents SDK, LlamaIndex Workflows, Mastra…) · XI n8n / Workflow Automation as a full execution domain (triggers, webhooks, schedules, branches, loops, sub-workflows, credentials, human approval, retries, error workflows, execution history, scaling, self-hosting) · XII Agent Protocol Fabric (HTTP/REST/GraphQL/gRPC/WS/SSE/webhooks/OpenAPI/OAuth/OIDC/JWT + MCP, A2A, AG-UI, A2UI, UCP, AP2) · XIII Data Engineering · XIV Tool / Action Fabric · XV Security · XVI Evaluation · XVII Observability · XVIII Reliability · XIX Infrastructure · XX AI Development / Coding agents (spec→plan→code→test→review→security→eval→deploy→monitor) · XXI Business Automation · XXII Agentic Commerce · XXIII Product Engine · XXIV Revenue Engine · XXV Opportunity Engine · XXVI Agent Portfolio · XXVII Autonomous Self-Improvement · XXVIII Meta-layer.

Every protocol, tool and framework entry must declare boundary, purpose, transport, identity, authorization, state, failure mode, observability and economics — popularity alone never earns a node.

Cross-cutting spines run through all branches: Observability, Evaluation, Cost Control, Security/Governance, Human Oversight, Optimization Loop.

**Meta-layer (XXVIII):** when the system meets an unknown pattern it does not stop — `unknown → research → validate → classify → add to ontology → evaluate → version`. Unknowns are first-class records with a research queue, so the tree grows by design.

## 3. Source ingestion — two-layer extraction

The book becomes the first fully ingested corpus; the pipeline is source-agnostic so more sources can be added later.

**Layer A — objects:** raster images, masks, vector drawing objects, text runs with coordinates, page geometry. Everything kept in a raw archive with sha256. Nothing is discarded — filter ≠ deletion.

**Layer B — figure reconstruction:** per page, cluster raster + vector + label text into visually meaningful figure regions, re-render each region from the page at 300 DPI and crop to bbox. This recovers vector-only diagrams, multi-object composites, masked and clipped figures that `pdfimages` alone cannot produce. Perceptual hash + sha256 give `duplicate_group` (grouped, never deleted). OCR of every figure feeds the search index, so "ReAct" finds a diagram even when the prose never says it.

**Manifest per figure:** `figure_id`, page, bbox, composition (raster/vector/hybrid), source objects, asset + thumbnail, context (heading, caption, paragraph before/after, OCR text), multi-label classification (domain, subdomain, patterns, technologies, artifact_type, role), graph mapping (nodes, concepts), integrity (sha256, phash, duplicate_group), and **confidence per mapping** (≥0.85 auto · 0.5–0.85 review · <0.5 weak). Ambiguous mappings land in a review queue with one-click accept/reassign persisted back.

Source fidelity is mandatory: every node states why it exists, its book/chapter/page, source figures, caption, original paragraph — and a "view source page" that highlights the exact bbox.

## 4. Engines

**Knowledge Engine** — graph store, ontology versioning, completeness scoring, unknown-pattern research loop.

**Architecture Decision Engine** — requirements + constraints in ("AI support system, 100k users, €20k/month, 99.9% availability"), out: candidate architectures → trade-offs → component graph → agent topology → deployment plan → cost model → evaluation plan → security plan → implementation spec, every recommendation citing the graph nodes and book pages behind it.

**Agent Factory** — produces agent specs (role, tools, memory policy, context policy, orchestration paradigm, evaluation suite, governance rules, failure modes, cost model) from reusable patterns, all sharing one graph, memory, artifact store, execution state, evaluation system and policy engine. Gate order: idea → market validation → unit economics → architecture → simulation → evaluation → security → deployment → observation → scale/kill.

**Execution Fabric** — an agent spec compiles to a concrete target: n8n workflow blueprint, code/API service, or MCP/A2A topology; the target is chosen per node, never hardcoded to one stack.

**Agent Economics Engine** — revenue − model − tool − infra − storage − human review − acquisition = contribution margin, per request / workflow / agent run / customer / product, plus CAC, LTV, ARPU, gross margin, churn, retention, payback, conversion per revenue model.

**Opportunity Engine** — market signals, customer problems, search demand, competitor moves, technology/API/protocol/regulation changes, new inefficiencies → discover → score → validate → model economics → prototype → evaluate → launch / kill.

**Portfolio Manager** — every deployed agent is an asset (revenue, cost, margin, accuracy, reliability, usage, retention impact, risk, growth) with an explicit decision: scale, optimize, refactor, merge, reposition, license, kill.

**Revenue & Product Engine** — agents package as SaaS, API, workflow, copilot, autonomous service, marketplace product, enterprise system, white label, embedded agent; monetized via subscription, usage, credits, API, licensing, marketplace, transaction fee, managed service, enterprise, white label, performance-based.

**Self-Improvement Loop — bounded autonomy:** observe → understand → find bottleneck → generate options → simulate → evaluate → security check → economic check → human/policy approval → deploy → measure → learn. Never unbounded: policy + budget + permissions + approval thresholds + rollback + audit gate every action.

## 5. Application surface

- `/` — Atlas map: layered, data-driven SVG rendered from the graph. Cursor-anchored wheel zoom, pan, minimap, layer/branch toggles, edge-type legend, completeness heat overlay.
- `/branch/$id`, `/node/$id`, `/pattern/$id`, `/concept/$id` — node dossiers with all ten dimensions, instances (frameworks/tools/protocols), relations, source figures.
- `/book`, `/chapter/$id`, `/source/page/$page`, `/figure/$id` — full drill path in both directions, with bbox highlighting.
- `/gallery` — complete archive: lazy responsive thumbnails, search over caption + heading + OCR, facets (branch, domain, pattern, technology, type, composition, page range), duplicate-group collapse, paging.
- `/design` — Architecture Decision Engine. `/factory` — Agent Factory. `/portfolio`, `/economics`, `/opportunities`, `/evaluation`, `/observability` — the operating dashboards.
- `/review` — confidence queue + unknown-pattern research queue.

## 6. Exports

`universal-ai-os-atlas.png` (large-format poster), `universal-ai-os-atlas.pdf` (vector + appendix indexing every figure to node, page, bbox), `atlas-archive.zip` (raw objects + reconstructed figures + manifest.json/csv + duplicate groups), plus per-run architecture specs and agent specs as downloadable documents. All rendered from the same graph/SVG source as the web view.

## Technical notes

- Extraction: `pdfplumber` (bbox, text, vector objects) + `pdfimages` + `pdftoppm`/pypdfium2 (region rendering) + `pytesseract` (OCR) + `imagehash`. Manifest committed as JSON; images hosted as CDN asset pointers.
- App: TanStack Start. Graph + manifest as static modules for read paths; the SVG renderer is shared by web and exports so they never diverge.
- Lovable Cloud for persistence (agents, runs, economics, opportunities, portfolio decisions, review overrides, ontology versions) and auth; Lovable AI for decision, factory, classification, research and optimization agents. Generated output is structured data — reviewable, diffable, exportable — never free text only.
- Design: dark blueprint system (grid, cyan/amber accents, monospace labels) via semantic tokens in `src/styles.css`; per-route head metadata.

## Delivery order

1. Extraction + manifest + raw archive. 2. Ontology + knowledge graph + Atlas map. 3. Gallery, explorer, source fidelity, review queues. 4. Poster/PDF/ZIP exports. 5. Architecture Decision Engine + Agent Factory specs. 6. Execution fabric compilers (n8n / code / MCP). 7. Economics, portfolio, opportunity, evaluation and observability dashboards. 8. Bounded self-improvement loop.


---

## 2. The 10/10 standard

| # | Dimension | Question |
| --- | --- | --- |
| 1 | capability | What can it do? |
| 2 | architecture | How is it correctly built? |
| 3 | execution | How does it actually run? |
| 4 | integration | What does it connect to? |
| 5 | reliability | What happens when it fails? |
| 6 | security | How is it controlled and contained? |
| 7 | evaluation | How do we prove it works? |
| 8 | economics | What does it cost and what is it worth? |
| 9 | scalability | How does it grow without breaking? |
| 10 | evolution | How does it improve itself? |

## 3. Layers

| Layer | Title | Scope | Branches |
| --- | --- | --- | --- |
| `foundation` | Foundation | Computer science the whole tree stands on | I |
| `architecture` | Software Architecture | Structural and resilience patterns | II |
| `intelligence` | Intelligence | Models, training, inference | III, IV |
| `context` | Context & Knowledge | Context engineering, RAG, memory | V, VI, IX |
| `agentic` | Agentic | Agents, multi-agent, orchestration | VII, VIII, X, XX |
| `execution` | Execution Fabric | Workflows, tools, protocols | XI, XII, XIV |
| `data` | Data | Stores and pipelines | XIII |
| `control` | Control Plane | Security, evaluation, observability, reliability | XV, XVI, XVII, XVIII |
| `infrastructure` | Infrastructure | Where it runs and how it ships | XIX |
| `business` | Business | Products, revenue, opportunity, portfolio | XXI, XXII, XXIII, XXIV, XXV, XXVI |
| `meta` | Meta | Self-improvement and ontology growth | XXVII, XXVIII |

## 4. Ontology — all branches and nodes

### I. Foundational Computer Science

*Layer:* foundation · *Nodes:* 16 · *Mapped figures:* 0 · *ID:* `foundational-computer-science`

The substrate that every higher branch silently depends on.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Algorithms | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Data Structures | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Distributed Systems | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Operating Systems | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Networking | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Databases | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Compilers | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Concurrency | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Parallelism | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Cryptography | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Information Theory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Probability | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Statistics | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Optimization | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Systems Design | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Software Engineering | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### II. Software Architecture

*Layer:* architecture · *Nodes:* 32 · *Mapped figures:* 0 · *ID:* `software-architecture`

Structural patterns plus the resilience patterns that keep them alive.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Monolith | 4/10 | capability, architecture, execution, integration | reliability, security, evaluation, economics, scalability, evolution | — | — |
| Modular Monolith | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Microservices | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Event-Driven | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Layered | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Hexagonal | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Clean Architecture | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Domain-Driven Design | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| CQRS | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Event Sourcing | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Saga | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Strangler | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Backend-for-Frontend | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| API Gateway | 4/10 | capability, architecture, execution, integration | reliability, security, evaluation, economics, scalability, evolution | — | — |
| Pub/Sub | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Queue-Based | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Streaming | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Batch | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Serverless | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Edge | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Distributed | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Peer-to-Peer | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Retry | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Backoff | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Circuit Breaker | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Bulkhead | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Timeout | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Idempotency | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Checkpoint | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Replay | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Failover | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Graceful Degradation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### III. AI / ML Foundation

*Layer:* intelligence · *Nodes:* 27 · *Mapped figures:* 123 · *ID:* `ai-ml-foundation`

Model families and the training machinery behind them.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Classical ML | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Deep Learning | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Transformers | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| LLMs | 10/10 | capability, architecture, execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — | — |
| Small Language Models | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Mixture of Experts | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Multimodal Models | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Vision | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Speech | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Audio | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Image Generation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Video | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Embeddings | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Rerankers | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Classifiers | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Diffusion | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Fine-Tuning | 10/10 | capability, architecture, execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — | — |
| LoRA | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| QLoRA | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Distillation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Quantization | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Synthetic Data | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Reinforcement Learning | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| RLHF | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| RLAIF | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Reasoning | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Inference Optimization | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### IV. LLM Engineering

*Layer:* intelligence · *Nodes:* 17 · *Mapped figures:* 32 · *ID:* `llm-engineering`

Everything between a raw model and a dependable model call.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Prompt Engineering | 10/10 | capability, architecture, execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — | — |
| System Prompts | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Structured Outputs | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Function Calling | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Tool Calling | 10/10 | capability, architecture, execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — | — |
| Model Routing | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Model Cascading | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Fallback Models | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Model Selection | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Model Ensembles | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Context Windows | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Token Optimization | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Prompt Caching | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Inference Caching | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Batch Inference | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Streaming | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Structured Generation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### V. Context Engineering

*Layer:* context · *Nodes:* 16 · *Mapped figures:* 20 · *ID:* `context-engineering`

A first-class discipline: what the model is allowed to see, and why.

**Pipeline:** Input context → Relevant context → Compressed context → Task context → Model context → Output

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Context Assembly | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Context Selection | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Context Ranking | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Context Compression | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Context Caching | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Context Routing | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Context Isolation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Token Budgeting | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| State | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Session State | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Agent State | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Scratchpads | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Working Memory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Long Context | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Contextual Retrieval | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Dynamic Context | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### VI. RAG / Knowledge Engineering

*Layer:* context · *Nodes:* 24 · *Mapped figures:* 58 · *ID:* `rag-knowledge-engineering`

Retrieval as an engineered system, not a single trick.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Naive RAG | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Advanced RAG | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Hybrid RAG | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| GraphRAG | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Agentic RAG | 10/10 | capability, architecture, execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — | — |
| Corrective RAG | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Self-RAG | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Adaptive RAG | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Multi-Hop Retrieval | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Multi-Query | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Query Expansion | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Reranking | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Semantic Search | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Keyword Search | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Vector Search | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Knowledge Graphs | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Entity Resolution | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Document Intelligence | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Chunking | 10/10 | capability, architecture, execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — | — |
| Embedding | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Indexing | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Retrieval Evaluation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Grounding | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Citation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### VII. Agentic AI

*Layer:* agentic · *Nodes:* 20 · *Mapped figures:* 91 · *ID:* `agentic-ai`

The agent continent: roles an agent can take and how each is built.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Tool-Calling Agent | 10/10 | capability, architecture, execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — | — |
| ReAct | 10/10 | capability, architecture, execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — | — |
| Planner | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Executor | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Router | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Supervisor | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Critic | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Reflection | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Evaluator | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Research Agent | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Coding Agent | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Browser Agent | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Data Agent | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Memory Agent | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Recovery Agent | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Security Agent | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Sales Agent | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Support Agent | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Finance Agent | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Operations Agent | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### VIII. Multi-Agent

*Layer:* agentic · *Nodes:* 16 · *Mapped figures:* 1 · *ID:* `multi-agent`

Coordination topologies once one agent is not enough.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Sequential | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Parallel | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Hierarchical | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Supervisor | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Delegation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Handoffs | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Debate | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Consensus | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Swarm | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Blackboard | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Shared Memory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Distributed Agents | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Agent Teams | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Agent Networks | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Agent Marketplaces | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Agent-to-Agent Economy | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### IX. Agent Memory

*Layer:* context · *Nodes:* 15 · *Mapped figures:* 4 · *ID:* `agent-memory`

Memory types and the lifecycle that keeps them honest.

**Pipeline:** Capture → Store → Index → Retrieve → Rank → Compress → Consolidate → Expire → Forget

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Working Memory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Short-Term Memory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Conversation Memory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Episodic Memory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Semantic Memory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Procedural Memory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Long-Term Memory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Vector Memory | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Graph Memory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| KV Memory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| External Memory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Compressed Memory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Hierarchical Memory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Personalized Memory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Shared Memory | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### X. Agent Orchestration

*Layer:* agentic · *Nodes:* 8 · *Mapped figures:* 0 · *ID:* `agent-orchestration`

Paradigms first, frameworks second — the abstraction stays neutral.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Graph Orchestration | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | LangGraph, Mastra | — |
| Role Orchestration | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | CrewAI, Microsoft Agent Framework | — |
| Loop Orchestration | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | OpenAI Agents SDK, Google ADK | — |
| Workflow Orchestration | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | n8n, LlamaIndex Workflows, Temporal | — |
| Event Orchestration | 4/10 | capability, architecture, execution, integration | reliability, security, evaluation, economics, scalability, evolution | Kafka, EventBridge | — |
| Hierarchical Orchestration | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Human Orchestration | 4/10 | capability, architecture, execution, integration | reliability, security, evaluation, economics, scalability, evolution | — | — |
| Framework-Neutral Abstraction | 10/10 | capability, architecture, execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — | Never a LangGraph OS: the target is chosen per node. |

### XI. n8n / Workflow Automation

*Layer:* execution · *Nodes:* 24 · *Mapped figures:* 0 · *ID:* `n8n-workflow-automation`

A full execution domain, not one node.

**Pipeline:** n8n → Agent runtime → MCP → APIs → Databases → SaaS

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Triggers | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Webhooks | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Schedules | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Events | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Forms | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| HTTP | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| APIs | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Databases | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Files | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Queues | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Branches | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Conditions | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Loops | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Merges | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Code Nodes | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Sub-workflows | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Credentials | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Secrets | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Human Approval | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Retries | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Error Workflows | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Execution History | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Scaling | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Self-Hosting | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XII. Agent Protocol Fabric

*Layer:* execution · *Nodes:* 17 · *Mapped figures:* 70 · *ID:* `agent-protocol-fabric`

Every protocol declares boundary, transport, identity, state, failure and economics.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| HTTP | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| REST | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| GraphQL | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| gRPC | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| WebSockets | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| SSE | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Webhooks | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| OpenAPI | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| OAuth | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| OIDC | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| JWT | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| MCP | 10/10 | capability, architecture, execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — | — |
| A2A | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| AG-UI | 4/10 | capability, architecture, execution, integration | reliability, security, evaluation, economics, scalability, evolution | — | — |
| A2UI | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| UCP | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| AP2 | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XIII. Data Engineering

*Layer:* data · *Nodes:* 23 · *Mapped figures:* 4 · *ID:* `data-engineering`

Stores and pipelines feeding everything above.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| SQL | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| NoSQL | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Vector Database | 10/10 | capability, architecture, execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — | — |
| Graph Database | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Object Storage | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Search Engine | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Cache | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Data Warehouse | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Data Lake | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Lakehouse | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Event Store | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Feature Store | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| ETL | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| ELT | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| CDC | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Streaming | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Batch | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Validation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Deduplication | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Schema Evolution | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Lineage | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Data Quality | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Data Governance | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XIV. Tool / Action Fabric

*Layer:* execution · *Nodes:* 27 · *Mapped figures:* 15 · *ID:* `tool-action-fabric`

How an agent is allowed to touch the world.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Tool Registry | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Tool Discovery | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Tool Selection | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Tool Permissions | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Tool Invocation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Tool Validation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Tool Sandbox | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Tool Timeout | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Tool Retry | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Result Validation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Tool Audit | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Tool Budget | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Tool Rate Limit | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Browser | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Search | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Code | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Shell | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| SQL Tool | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| HTTP Tool | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Files | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Email | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Calendar | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| CRM | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| ERP | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Payments | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Cloud | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Internal APIs | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XV. Security

*Layer:* control · *Nodes:* 22 · *Mapped figures:* 0 · *ID:* `security`

Autonomous execution cannot be patched later.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| IAM | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| RBAC | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| ABAC | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Identity | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Agent Identity | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Scoped Credentials | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Secrets | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Encryption | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| KMS | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| PII Detection | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| DLP | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Sandboxing | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Network Isolation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Prompt Injection Defense | 10/10 | capability, architecture, execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — | — |
| Tool Abuse Defense | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Data Exfiltration Defense | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Supply Chain Security | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Model Security | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Agent Security | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Runtime Containment | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Audit | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Policy Enforcement | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XVI. Evaluation

*Layer:* control · *Nodes:* 30 · *Mapped figures:* 39 · *ID:* `evaluation`

Proof, at every level from a unit to the business.

**Pipeline:** Build → Test → Evaluate → Deploy → Observe → Detect drift → Improve → Re-evaluate

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Unit Eval | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Component Eval | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Agent Eval | 10/10 | capability, architecture, execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — | — |
| Workflow Eval | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| System Eval | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Business Eval | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Accuracy | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Task Success | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Tool Success | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Groundedness | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Faithfulness | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Relevance | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Safety | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Reliability | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Latency | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Cost | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Drift | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Recovery | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| User Satisfaction | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| ROI | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Golden Dataset | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Synthetic Dataset | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Regression | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| LLM-as-Judge | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Human Eval | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| A/B Testing | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Red Team | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Adversarial Testing | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Production Eval | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Continuous Eval | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XVII. Observability

*Layer:* control · *Nodes:* 21 · *Mapped figures:* 14 · *ID:* `observability`

Reconstruct any run, end to end.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Logs | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Metrics | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Traces | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Token Usage | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Latency | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Cost | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Tool Calls | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Agent Steps | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Model Calls | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Retrieval Results | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Memory Retrieval | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Errors | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Retries | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| User Feedback | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Trace ID | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Session ID | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Agent Run ID | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Tool Call ID | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Model Call ID | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Workflow ID | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Customer ID | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XVIII. Reliability

*Layer:* control · *Nodes:* 16 · *Mapped figures:* 0 · *ID:* `reliability`

What separates a demo agent from a production agent.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Retries | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Backoff | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Timeout | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Circuit Breaker | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Bulkhead | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Dead Letter Queue | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Checkpointing | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Durable Execution | 6/10 | capability, architecture, execution, integration, evaluation, economics | reliability, security, scalability, evolution | — | — |
| Replay | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Recovery | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Idempotency | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Failover | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Disaster Recovery | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Multi-Region | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Load Shedding | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Graceful Degradation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XIX. Infrastructure

*Layer:* infrastructure · *Nodes:* 19 · *Mapped figures:* 37 · *ID:* `infrastructure`

Where it runs, and how it ships.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Local | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Docker | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Kubernetes | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| VM | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Serverless | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| GPU | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| CPU | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Edge | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Cloud | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Multi-Cloud | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| CI/CD | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| IaC | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Networking | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Autoscaling | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Service Discovery | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Config | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Secrets Management | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Registries | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| GPU Scheduling | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XX. AI Development / Coding

*Layer:* agentic · *Nodes:* 13 · *Mapped figures:* 0 · *ID:* `ai-development-coding`

Agents that build and maintain software.

**Pipeline:** Spec → Plan → Code → Test → Review → Security → Eval → Deploy → Monitor

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| AI Coding | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Code Agents | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Repo Agents | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Issue Agents | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| PR Agents | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Test Agents | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Debug Agents | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Refactoring Agents | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Documentation Agents | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Migration Agents | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Security Review Agents | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| DevOps Agents | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| SRE Agents | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XXI. Business Automation

*Layer:* business · *Nodes:* 13 · *Mapped figures:* 1 · *ID:* `business-automation`

Where agent work meets an actual company.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Sales | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Marketing | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Support | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Research | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Operations | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Finance | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| HR | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Legal Ops | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Procurement | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Customer Success | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Analytics | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Reporting | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Knowledge Management | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XXII. Agentic Commerce

*Layer:* business · *Nodes:* 10 · *Mapped figures:* 0 · *ID:* `agentic-commerce`

Agents transacting, with the protocols that make it safe.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Discovery | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Recommendation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Negotiation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Authorization | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Purchase | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Payment | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Fulfillment | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Tracking | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Refund | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Reconciliation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XXIII. Product Engine

*Layer:* business · *Nodes:* 9 · *Mapped figures:* 0 · *ID:* `product-engine`

The shapes an agent can be sold in.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| SaaS | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| API | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Workflow | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Copilot | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Autonomous Service | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Marketplace Product | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Enterprise System | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| White Label | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Embedded Agent | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XXIV. Revenue Engine

*Layer:* business · *Nodes:* 20 · *Mapped figures:* 0 · *ID:* `revenue-engine`

Every model carries its own unit economics.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Subscription | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Usage | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Credits | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| API Billing | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Licensing | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Marketplace | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Transaction Fee | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Managed Service | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Enterprise | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| White Label | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Performance-Based | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| CAC | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| LTV | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| ARPU | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Gross Margin | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Contribution Margin | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Churn | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Retention | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Payback | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Conversion | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XXV. Opportunity Engine

*Layer:* business · *Nodes:* 10 · *Mapped figures:* 0 · *ID:* `opportunity-engine`

The system keeps looking, instead of waiting for a new idea.

**Pipeline:** Discover → Score → Validate → Model economics → Prototype → Evaluate → Launch → Scale / Kill

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Market Signals | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Customer Problems | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Search Demand | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Competitor Movement | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Technology Changes | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| New APIs | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| New Protocols | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| New Regulations | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| New Workflows | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| New Inefficiencies | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XXVI. Agent Portfolio

*Layer:* business · *Nodes:* 16 · *Mapped figures:* 0 · *ID:* `agent-portfolio`

Every deployed agent is an asset with a decision attached.

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Revenue | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Cost | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Margin | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Accuracy | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Reliability | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Usage | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Retention Impact | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Risk | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Growth Potential | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Scale | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Optimize | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Refactor | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Merge | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Reposition | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| License | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Kill | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XXVII. Autonomous Self-Improvement

*Layer:* meta · *Nodes:* 16 · *Mapped figures:* 0 · *ID:* `autonomous-self-improvement`

Bounded autonomy: policy, budget, permissions, approval, rollback, audit.

**Pipeline:** Observe → Understand → Find bottleneck → Generate options → Simulate → Evaluate → Security check → Economic check → Approval → Deploy → Measure → Learn

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Observe | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Understand | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Find Bottleneck | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Generate Options | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Simulate | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Evaluate | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Security Check | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Economic Check | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Human Approval | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Deploy | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Measure | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Learn | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Policy Bounds | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Budget Bounds | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Rollback | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Audit Trail | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

### XXVIII. Meta-Layer

*Layer:* meta · *Nodes:* 10 · *Mapped figures:* 0 · *ID:* `meta-layer`

An unknown pattern is a task, not a dead end.

**Pipeline:** Unknown → Research → Validate → Classify → Add to ontology → Evaluate → Version

| Node | Completeness | Covered dimensions | Missing | Instances | Note |
| --- | --- | --- | --- | --- | --- |
| Unknown Pattern Intake | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Research | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Validation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Classification | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Ontology Insertion | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Evaluation | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Versioning | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Completeness Scoring | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Source Fidelity | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |
| Confidence Scoring | 2/10 | capability, architecture | execution, integration, reliability, security, evaluation, economics, scalability, evolution | — | — |

---

## 5. Figure manifest — index

| ID | Page | Composition | Role | Primary branch | Conf. | Title |
| --- | --- | --- | --- | --- | --- | --- |
| fig_0001 | 0 | raster | architecture | ai-ml-foundation | 0.74 | AI Engineering |
| fig_0002 | 0 | raster | architecture | ai-ml-foundation | 0.74 | AI Engineering |
| fig_0003 | 0 | hybrid | architecture | ai-ml-foundation | 0.63 | LLMs, RAG and Agents |
| fig_0004 | 0 | raster | architecture | ai-ml-foundation | 0.63 | LLMs, RAG and Agents |
| fig_0005 | 0 | raster | architecture | ai-ml-foundation | 0.63 | LLMs, RAG and Agents |
| fig_0006 | 0 | hybrid | architecture | ai-ml-foundation | 0.63 | LLMs, RAG and Agents |
| fig_0007 | 0 | raster | code | agent-protocol-fabric | 0.74 | this book and your time? |
| fig_0008 | 0 | hybrid | code | agent-protocol-fabric | 0.63 | this book and your time? |
| fig_0009 | 6 | raster | concept | ai-ml-foundation | 0.84 | What is an LLM? |
| fig_0010 | 6 | raster | concept | ai-ml-foundation | 0.84 | What is an LLM? |
| fig_0011 | 7 | raster | process | ai-ml-foundation | 0.89 | With enough exposure, the model becomes remarkably good at continuing any |
| fig_0012 | 7 | raster | process | ai-ml-foundation | 0.85 | The model looks at the tokens so far and predicts the next one. Repeating this |
| fig_0013 | 8 | raster | process | ai-ml-foundation | 0.98 | To formalise, a large language model is a Transformer-based neural network |
| fig_0014 | 9 | raster | architecture | ai-ml-foundation | 0.74 | Need for LLMs |
| fig_0015 | 10 | raster | architecture | ai-ml-foundation | 0.98 | Language naturally encodes reasoning steps, factual knowledge, explanations and |
| fig_0016 | 11 | raster | diagram | ai-ml-foundation | 0.84 | What makes an LLM ‘large’ ? |
| fig_0017 | 11 | raster | diagram | ai-ml-foundation | 0.98 | What makes an LLM ‘large’ ? |
| fig_0018 | 12 | raster | process | ai-ml-foundation | 0.98 | Larger models began to follow detailed instructions, perform multi-step |
| fig_0019 | 13 | raster | architecture | ai-ml-foundation | 0.84 | How are LLMs built? |
| fig_0020 | 14 | raster | process | ai-ml-foundation | 0.98 | This approach keeps the vocabulary manageable and allows the model to handle |
| fig_0021 | 14 | raster | code | ai-ml-foundation | 0.98 | Transformer Layers |
| fig_0022 | 15 | raster | code | ai-ml-foundation | 0.98 | Positional Encoding |
| fig_0023 | 17 | raster | process | ai-ml-foundation | 0.88 | How to train LLM from scratch? |
| fig_0024 | 18 | raster | concept | ai-ml-foundation | 0.72 | 0) Randomly initialized LLM |
| fig_0025 | 18 | raster | concept | ai-ml-foundation | 0.86 | 1) Pre-training |
| fig_0026 | 19 | raster | concept | ai-ml-foundation | 0.98 | Now it can: |
| fig_0027 | 20 | raster | process | ai-ml-foundation | 0.69 | That’s not just for feedback, but it’s valuable human preference data. |
| fig_0028 | 20 | raster | diagram | ai-ml-foundation | 0.98 | LLMs figure |
| fig_0029 | 21 | raster | comparison | ai-ml-foundation | 0.88 | 4) Reasoning fine-tuning |
| fig_0030 | 22 | raster | diagram | ai-ml-foundation | 0.98 | How do LLMs work? |
| fig_0031 | 23 | raster | diagram | ai-ml-foundation | 0.98 | If the events are A and B, we denote this as P(A\|B). |
| fig_0032 | 24 | raster | concept | ai-ml-foundation | 0.74 | This is a question of conditional probability: given the words that have come |
| fig_0033 | 24 | raster | concept | ai-ml-foundation | 0.87 | The word with the highest conditional probability is chosen as the prediction. |
| fig_0034 | 25 | raster | diagram | ai-ml-foundation | 0.72 | And the parameters of this distribution are the trained weights! |
| fig_0035 | 26 | raster | diagram | ai-ml-foundation | 0.62 | This is where temperature comes into the picture. |
| fig_0036 | 26 | raster | result | ai-ml-foundation | 0.81 | So even if “Token 1” has the highest score, it may not be chosen since we are |
| fig_0037 | 27 | raster | concept | ai-ml-foundation | 0.68 | Let's take a code example! |
| fig_0038 | 27 | raster | concept | ai-ml-foundation | 0.64 | ● |
| fig_0039 | 28 | raster | code | ai-ml-foundation | 0.95 | LLM Generation Parameters |
| fig_0040 | 29 | raster | result | ai-ml-foundation | 0.86 | This is a hard cap on how many tokens the model can generate in one response. |
| fig_0041 | 29 | raster | result | llm-engineering | 0.74 | 2) Temperature |
| fig_0042 | 29 | raster | diagram | ai-ml-foundation | 0.89 | 3) Top-k |
| fig_0043 | 30 | raster | diagram | ai-ml-foundation | 0.98 | Instead of picking from all tokens or top k tokens, model samples from a |
| fig_0044 | 30 | raster | diagram | ai-ml-foundation | 0.92 | 5) Frequency penalty |
| fig_0045 | 30 | raster | diagram | ai-ml-foundation | 0.78 | 6) Presence penalty |
| fig_0046 | 31 | raster | result | ai-ml-foundation | 0.80 | 7) Stop sequences |
| fig_0047 | 32 | raster | process | ai-ml-foundation | 0.84 | Strategies |
| fig_0048 | 33 | raster | result | ai-ml-foundation | 0.76 | Approach 2: Multinomial sampling strategy |
| fig_0049 | 33 | raster | process | ai-ml-foundation | 0.76 | Approach 3: Beam search |
| fig_0050 | 34 | raster | process | ai-ml-foundation | 0.87 | At each step, it expands the top k partial sequences (the beam). |
| fig_0051 | 34 | raster | result | ai-ml-foundation | 0.89 | Approach 4: Contrastive search |
| fig_0052 | 35 | raster | concept | observability | 0.73 | Bonus: SLED - Self-Logits Evolution Decoding |
| fig_0053 | 36 | raster | diagram | ai-ml-foundation | 0.93 | Using Another LLM |
| fig_0054 | 37 | raster | process | ai-ml-foundation | 0.98 | 1) Soft-label distillation |
| fig_0055 | 38 | raster | result | ai-ml-foundation | 0.87 | 2) Hard-label distillation |
| fig_0056 | 39 | raster | diagram | ai-ml-foundation | 0.98 | ● Start with an untrained Teacher LLM and an untrained Student LLM. |
| fig_0057 | 40 | raster | code | ai-ml-foundation | 0.84 | To get started, install Ollama with a single command: |
| fig_0058 | 40 | raster | code | ai-ml-foundation | 0.63 | Done! |
| fig_0059 | 40 | raster | code | ai-ml-foundation | 0.63 | For programmatic usage, you can also install the Python package of Ollama or its |
| fig_0060 | 41 | raster | code | ai-ml-foundation | 0.74 | 2) LMStudio |
| fig_0061 | 42 | raster | code | agent-protocol-fabric | 0.76 | 4) LlamaCPP |
| fig_0062 | 42 | raster | code | ai-ml-foundation | 0.68 | 4) LlamaCPP |
| fig_0063 | 44 | raster | comparison | ai-ml-foundation | 0.98 | Let's dive in to learn more about MoE! |
| fig_0064 | 44 | raster | code | ai-ml-foundation | 0.98 | LLMs figure |
| fig_0065 | 45 | raster | code | ai-ml-foundation | 0.94 | ● |
| fig_0066 | 46 | raster | result | ai-ml-foundation | 0.84 | But it isn't straightforward. |
| fig_0067 | 46 | raster | diagram | ai-ml-foundation | 0.98 | ● The model selects "Expert 2" (randomly since all experts are similar). |
| fig_0068 | 47 | raster | process | ai-ml-foundation | 0.68 | ● |
| fig_0069 | 49 | raster | concept | llm-engineering | 0.98 | What is Prompt Engineering? |
| fig_0070 | 50 | raster | process | llm-engineering | 0.92 | reasoning in LLMs |
| fig_0071 | 51 | raster | process | llm-engineering | 0.75 | 1) Chain of Thought (CoT) |
| fig_0072 | 51 | raster | process | llm-engineering | 0.87 | 1) Chain of Thought (CoT) |
| fig_0073 | 52 | raster | process | llm-engineering | 0.98 | It’s a simple idea: when in doubt, ask the model several times and trust the |
| fig_0074 | 52 | raster | process | llm-engineering | 0.84 | 3) Tree of Thoughts (ToT) |
| fig_0075 | 54 | raster | process | llm-engineering | 0.84 | Instead of letting LLMs reason freely, ARQs guide them through explicit, |
| fig_0076 | 55 | raster | process | llm-engineering | 0.63 | This type of query does two things: |
| fig_0077 | 55 | raster | process | llm-engineering | 0.68 | By the time the LLM generates the final response, it’s already walked through a |
| fig_0078 | 56 | raster | result | tool-action-fabric | 0.62 | ● |
| fig_0079 | 57 | raster | result | llm-engineering | 0.84 | Verbalized Sampling |
| fig_0080 | 57 | raster | architecture | llm-engineering | 0.68 | Verbalized Sampling |
| fig_0081 | 58 | raster | concept | llm-engineering | 0.98 | Prompt Engineering figure |
| fig_0082 | 59 | raster | comparison | llm-engineering | 0.86 | Verbalized sampling significantly enhances diversity by 1.6-2.1x over direct |
| fig_0083 | 61 | raster | comparison | llm-engineering | 0.82 | Natural language is powerful yet vague. |
| fig_0084 | 61 | raster | result | llm-engineering | 0.65 | Prompt Engineering figure |
| fig_0085 | 62 | raster | result | llm-engineering | 0.98 | 1) Structure means certainty |
| fig_0086 | 63 | raster | result | llm-engineering | 0.84 | And this works irrespective of what you are doing, like generating content, |
| fig_0087 | 63 | raster | result | llm-engineering | 0.73 | handoffs |
| fig_0088 | 64 | raster | code | llm-engineering | 0.74 | To summarise: |
| fig_0089 | 66 | raster | concept | ai-ml-foundation | 0.91 | What is Fine-tuning? |
| fig_0090 | 67 | raster | comparison | ai-ml-foundation | 0.81 | fine-tuning |
| fig_0091 | 68 | raster | diagram | ai-ml-foundation | 0.84 | ● |
| fig_0092 | 69 | raster | diagram | ai-ml-foundation | 0.78 | Additionally, maintaining the infrastructure to support fine-tuning requests fro |
| fig_0093 | 69 | raster | architecture | ai-ml-foundation | 0.93 | LLM Fine-tuning Techniques |
| fig_0094 | 70 | raster | diagram | ai-ml-foundation | 0.95 | Let’s understand these: |
| fig_0095 | 71 | raster | diagram | ai-ml-foundation | 0.92 | 2) LoRA-FA |
| fig_0096 | 71 | raster | diagram | ai-ml-foundation | 0.93 | 2) LoRA-FA |
| fig_0097 | 72 | raster | comparison | ai-ml-foundation | 0.98 | 4) Delta-LoRA |
| fig_0098 | 72 | raster | comparison | ai-ml-foundation | 0.94 | 4) Delta-LoRA |
| fig_0099 | 73 | raster | diagram | ai-ml-foundation | 0.95 | Bonus: LoRA-drop |
| fig_0100 | 73 | raster | result | ai-ml-foundation | 0.94 | Bonus: LoRA-drop |
| fig_0101 | 74 | raster | result | ai-ml-foundation | 0.85 | By keeping LoRA only in high-impact layers, LoRA-drop reduces training cost |
| fig_0102 | 74 | raster | diagram | ai-ml-foundation | 0.77 | Bonus: Quantized Low-Rank Adaptation (QLoRA) |
| fig_0103 | 75 | raster | result | ai-ml-foundation | 0.74 | Typically, these million parameters will be represented as float32, which |
| fig_0104 | 75 | raster | result | ai-ml-foundation | 0.72 | This results in a significant decrease in the amount of memory required to store |
| fig_0105 | 76 | raster | concept | ai-ml-foundation | 0.98 | Bonus: DoRA |
| fig_0106 | 77 | raster | diagram | ai-ml-foundation | 0.98 | Scratch |
| fig_0107 | 77 | raster | diagram | ai-ml-foundation | 0.98 | Scratch |
| fig_0108 | 78 | raster | diagram | ai-ml-foundation | 0.98 | Also, instead of updating the original weights W, it is perfectly legal to maint |
| fig_0109 | 78 | raster | concept | ai-ml-foundation | 0.98 | In fact, in all the model fine-tuning iterations, W can be kept static, and all |
| fig_0110 | 79 | raster | diagram | ai-ml-foundation | 0.89 | How does LoRA work? |
| fig_0111 | 79 | raster | diagram | ai-ml-foundation | 0.89 | How does LoRA work? |
| fig_0112 | 80 | raster | diagram | ai-ml-foundation | 0.94 | In the above image, every point denotes a possible LoRA configuration. Also, the |
| fig_0113 | 81 | raster | diagram | ai-ml-foundation | 0.93 | Implementation |
| fig_0114 | 82 | raster | result | ai-ml-foundation | 0.76 | In the forward method, the input x is multiplied by the matrices A and B, and th |
| fig_0115 | 82 | raster | result | ai-ml-foundation | 0.81 | ● A higher value of alpha means that the changes made by the LoRA layer |
| fig_0116 | 83 | raster | result | ai-ml-foundation | 0.92 | As LoRA is used after training, so we will already have a trained model availabl |
| fig_0117 | 84 | raster | diagram | ai-ml-foundation | 0.98 | Done! |
| fig_0118 | 84 | raster | code | ai-ml-foundation | 0.98 | As depicted above: |
| fig_0119 | 86 | raster | diagram | ai-ml-foundation | 0.87 | Generating a synthetic dataset using existing LLMs and utilizing it for |
| fig_0120 | 86 | raster | concept | ai-ml-foundation | 0.98 | This process is called instruction fine-tuning and it is described in the animat |
| fig_0121 | 87 | raster | process | ai-ml-foundation | 0.98 | ● |
| fig_0122 | 88 | raster | architecture | data-engineering | 0.68 | Next, we load the Llama-3 models locally with Ollama: |
| fig_0123 | 88 | raster | architecture | ai-ml-foundation | 0.74 | Moving on, we define our pipeline: |
| fig_0124 | 88 | raster | architecture | data-engineering | 0.53 | Fine-tuning figure |
| fig_0125 | 89 | raster | architecture | data-engineering | 0.59 | Done! |
| fig_0126 | 89 | raster | architecture | ai-ml-foundation | 0.84 | Fine-tuning figure |
| fig_0127 | 90 | raster | comparison | ai-ml-foundation | 0.84 | Both update the model using LoRA or similar PEFT methods, but their goals and |
| fig_0128 | 91 | raster | comparison | ai-ml-foundation | 0.75 | SFT process: |
| fig_0129 | 91 | raster | process | ai-ml-foundation | 0.76 | RFT process: |
| fig_0130 | 92 | raster | architecture | ai-ml-foundation | 0.98 | This flowchart gives a quick guide on which fine-tuning method to use based on |
| fig_0131 | 94 | raster | architecture | ai-ml-foundation | 0.78 | ● |
| fig_0132 | 95 | raster | concept | ai-ml-foundation | 0.96 | Let’s begin! |
| fig_0133 | 95 | raster | code | ai-ml-foundation | 0.86 | #1) Load the model |
| fig_0134 | 96 | raster | code | ai-ml-foundation | 0.94 | #2) Define LoRA config |
| fig_0135 | 97 | raster | architecture | llm-engineering | 0.78 | Each sample includes: |
| fig_0136 | 98 | raster | process | ai-ml-foundation | 0.65 | ● Match format exactly |
| fig_0137 | 99 | raster | architecture | ai-ml-foundation | 0.95 | Comparison |
| fig_0138 | 99 | raster | architecture | ai-ml-foundation | 0.88 | Comparison |
| fig_0139 | 101 | raster | architecture | ai-ml-foundation | 0.57 | ● An agent interacts with the environment through an OpenEnv client. |
| fig_0140 | 102 | raster | architecture | agentic-ai | 0.60 | Trainer(ART) |
| fig_0141 | 105 | raster | concept | rag-knowledge-engineering | 0.81 | What is RAG? |
| fig_0142 | 106 | raster | diagram | rag-knowledge-engineering | 0.75 | What are vector databases? |
| fig_0143 | 107 | raster | diagram | ai-ml-foundation | 0.63 | This shows that embeddings can learn the semantic characteristics of entities |
| fig_0144 | 107 | raster | diagram | rag-knowledge-engineering | 0.74 | In other words, encoding unstructured data allows us to run many sophisticated |
| fig_0145 | 108 | raster | diagram | rag-knowledge-engineering | 0.68 | in RAG |
| fig_0146 | 108 | raster | result | rag-knowledge-engineering | 0.68 | in RAG |
| fig_0147 | 109 | raster | diagram | rag-knowledge-engineering | 0.98 | But if you think about it, is it really our objective to train an LLM to know ev |
| fig_0148 | 109 | raster | diagram | rag-knowledge-engineering | 0.98 | So, once we have trained this model on a ridiculously large enough training |
| fig_0149 | 110 | raster | diagram | rag-knowledge-engineering | 0.61 | But since LLMs usually have a limit on the context window (number of |
| fig_0150 | 110 | raster | code | rag-knowledge-engineering | 0.80 | When the LLM needs to access this information, it can query the vector database |
| fig_0151 | 111 | raster | diagram | rag-knowledge-engineering | 0.73 | Once the approximate nearest neighbors have been retrieved, we gather the |
| fig_0152 | 111 | raster | process | rag-knowledge-engineering | 0.75 | The above search process retrieves context that is similar to the query vector, |
| fig_0153 | 112 | raster | architecture | rag-knowledge-engineering | 0.68 | Consequently, the LLM can easily incorporate this info while generating text |
| fig_0154 | 112 | raster | architecture | rag-knowledge-engineering | 0.80 | Workflow of a RAG system |
| fig_0155 | 113 | raster | process | rag-knowledge-engineering | 0.87 | #1) Create chunks |
| fig_0156 | 113 | raster | process | rag-knowledge-engineering | 0.82 | #1) Create chunks |
| fig_0157 | 113 | raster | process | rag-knowledge-engineering | 0.77 | #1) Create chunks |
| fig_0158 | 114 | raster | code | rag-knowledge-engineering | 0.65 | Since these are “context embedding models” (not word embedding models), |
| fig_0159 | 114 | raster | code | rag-knowledge-engineering | 0.68 | #3) Store embeddings in a vector database |
| fig_0160 | 115 | raster | process | rag-knowledge-engineering | 0.95 | #5) Embed the query |
| fig_0161 | 115 | raster | comparison | rag-knowledge-engineering | 0.86 | #5) Embed the query |
| fig_0162 | 115 | raster | comparison | rag-knowledge-engineering | 0.88 | #6) Retrieve similar chunks |
| fig_0163 | 116 | raster | diagram | rag-knowledge-engineering | 0.93 | It is expected that these retrieved documents contain information related to the |
| fig_0164 | 116 | raster | process | rag-knowledge-engineering | 0.76 | #7) Re-rank the chunks |
| fig_0165 | 117 | raster | architecture | rag-knowledge-engineering | 0.77 | The LLM leverages the context provided by the chunks to generate a coherent |
| fig_0166 | 117 | raster | architecture | rag-knowledge-engineering | 0.91 | chunking strategies for RAG |
| fig_0167 | 118 | raster | process | rag-knowledge-engineering | 0.96 | Let’s understand them! |
| fig_0168 | 119 | raster | architecture | rag-knowledge-engineering | 0.91 | Since a direct split can disrupt the semantic flow, it is recommended to maintai |
| fig_0169 | 119 | raster | process | rag-knowledge-engineering | 0.93 | 2) Semantic chunking |
| fig_0170 | 120 | raster | architecture | rag-knowledge-engineering | 0.78 | Unlike fixed-size chunks, this maintains the natural flow of language and |
| fig_0171 | 120 | raster | result | rag-knowledge-engineering | 0.98 | 3) Recursive chunking |
| fig_0172 | 121 | raster | architecture | rag-knowledge-engineering | 0.94 | As shown above: |
| fig_0173 | 121 | raster | result | rag-knowledge-engineering | 0.94 | 4) Document structure-based chunking |
| fig_0174 | 122 | raster | concept | rag-knowledge-engineering | 0.81 | That said, this approach assumes that the document has a clear structure, which |
| fig_0175 | 122 | raster | result | rag-knowledge-engineering | 0.81 | 5) LLM-based chunking |
| fig_0176 | 124 | raster | code | rag-knowledge-engineering | 0.84 | Two important parameters guide this decision: |
| fig_0177 | 125 | raster | architecture | rag-knowledge-engineering | 0.65 | RAG architectures |
| fig_0178 | 127 | raster | architecture | rag-knowledge-engineering | 0.85 | RAG vs Agentic RAG |
| fig_0179 | 128 | raster | concept | rag-knowledge-engineering | 0.66 | Agentic RAG |
| fig_0180 | 130 | raster | concept | rag-knowledge-engineering | 0.81 | Traditional RAG vs HyDE |
| fig_0181 | 131 | raster | comparison | rag-knowledge-engineering | 0.82 | Let's understand this in more detail. |
| fig_0182 | 131 | raster | concept | rag-knowledge-engineering | 0.78 | HyDE handles this as follows: |
| fig_0183 | 132 | raster | diagram | rag-knowledge-engineering | 0.78 | Now, of course, the hypothetical generated will likely contain hallucinated |
| fig_0184 | 132 | raster | comparison | rag-knowledge-engineering | 0.76 | Several studies have shown that HyDE improves the retrieval performance |
| fig_0185 | 133 | raster | architecture | rag-knowledge-engineering | 0.64 | vs. RAG |
| fig_0186 | 134 | raster | architecture | ai-ml-foundation | 0.68 | While this fine-tuning technique has been successfully used for a long time, |
| fig_0187 | 135 | raster | architecture | ai-ml-foundation | 0.72 | The idea is to train only the LoRA network and freeze the large model. |
| fig_0188 | 136 | raster | architecture | rag-knowledge-engineering | 0.70 | Looking at the above visual, it is pretty clear that the LoRA network has |
| fig_0189 | 136 | raster | process | rag-knowledge-engineering | 0.81 | 3) RAG |
| fig_0190 | 137 | raster | process | rag-knowledge-engineering | 0.80 | Retrieval: Accessing and retrieving information from a knowledge source, such as |
| fig_0191 | 139 | raster | comparison | rag-knowledge-engineering | 0.74 | Essentially, instead of feeding the LLM every chunk and every token, REFRAG |
| fig_0192 | 141 | raster | comparison | rag-knowledge-engineering | 0.81 | Here’s how it works in simple terms: |
| fig_0193 | 143 | raster | comparison | rag-knowledge-engineering | 0.68 | RAG (2020-2023): |
| fig_0194 | 146 | raster | concept | rag-knowledge-engineering | 0.64 | What is Context Engineering? |
| fig_0195 | 147 | raster | architecture | context-engineering | 0.78 | Context engineering involves creating dynamic systems that offer: |
| fig_0196 | 148 | raster | result | context-engineering | 0.59 | Smart tool access: If your AI needs external information or actions, give it the |
| fig_0197 | 149 | raster | process | context-engineering | 0.80 | To understand context engineering, it's essential to first understand the meanin |
| fig_0198 | 150 | raster | architecture | context-engineering | 0.54 | ● Instructions |
| fig_0199 | 151 | raster | concept | context-engineering | 0.85 | ● If LLM is a CPU. |
| fig_0200 | 152 | raster | diagram | context-engineering | 0.76 | ● Writing Context |
| fig_0201 | 153 | raster | diagram | context-engineering | 0.68 | You can do so by writing it to: |
| fig_0202 | 153 | raster | diagram | context-engineering | 0.76 | 2) Read context |
| fig_0203 | 154 | raster | diagram | context-engineering | 0.78 | The retrieved context may contain duplicate or redundant information |
| fig_0204 | 154 | raster | code | context-engineering | 0.69 | 4) Isolating context |
| fig_0205 | 155 | raster | concept | context-engineering | 0.62 | Agents |
| fig_0206 | 157 | raster | architecture | context-engineering | 0.61 | workflow |
| fig_0207 | 158 | raster | architecture | context-engineering | 0.61 | CE involves creating dynamic systems that offer: |
| fig_0208 | 159 | raster | architecture | context-engineering | 0.62 | #1) Crew flow |
| fig_0209 | 160 | raster | process | rag-knowledge-engineering | 0.80 | The extracted data can be directly embedded and stored in a vector DB without |
| fig_0210 | 161 | raster | architecture | rag-knowledge-engineering | 0.68 | #4) Build memory layer |
| fig_0211 | 162 | raster | code | agent-memory | 0.58 | #5) Firecrawl web search |
| fig_0212 | 163 | raster | code | tool-action-fabric | 0.57 | #6) ArXiv API search |
| fig_0213 | 164 | raster | code | context-engineering | 0.54 | #7) Filter context |
| fig_0214 | 165 | raster | architecture | context-engineering | 0.62 | #8) Kick off the workflow |
| fig_0215 | 166 | raster | concept | context-engineering | 0.62 | We also translated this workflow into a streamlit app that: |
| fig_0216 | 166 | raster | architecture | context-engineering | 0.68 | Context Engineering figure |
| fig_0217 | 168 | raster | diagram | context-engineering | 0.80 | Let’s understand how it works: |
| fig_0218 | 170 | raster | architecture | context-engineering | 0.58 | Context Engineering |
| fig_0219 | 171 | raster | architecture | rag-knowledge-engineering | 0.66 | To actually solve this problem, you’d need to think of it as building an Agentic |
| fig_0220 | 173 | raster | concept | agent-protocol-fabric | 0.58 | It implements everything we discussed above, like: |
| fig_0221 | 173 | raster | diagram | rag-knowledge-engineering | 0.54 | But this does not tell if the content actually changed (maybe only the permissio |
| fig_0222 | 176 | raster | concept | agentic-ai | 0.81 | What is an AI Agent? |
| fig_0223 | 177 | raster | diagram | agentic-ai | 0.80 | ● A Filtering Agent scans the retrieved papers, identifying the most relevant |
| fig_0224 | 177 | raster | diagram | agentic-ai | 0.86 | ● |
| fig_0225 | 177 | raster | diagram | agentic-ai | 0.92 | ● A Formatting Agent structures the final report, ensuring it follows a clear, |
| fig_0226 | 178 | raster | architecture | agentic-ai | 0.98 | Here, the AI agents not only execute the research process end-to-end but also |
| fig_0227 | 178 | raster | concept | agentic-ai | 0.98 | To formalize AI Agents are autonomous systems that can reason, think, plan, |
| fig_0228 | 179 | raster | comparison | agentic-ai | 0.70 | Agent vs LLM vs RAG |
| fig_0229 | 179 | raster | diagram | agentic-ai | 0.74 | LLM (Large Language Model) |
| fig_0230 | 180 | raster | process | rag-knowledge-engineering | 0.74 | RAG (Retrieval-Augmented Generation) |
| fig_0231 | 180 | raster | architecture | agentic-ai | 0.78 | Agent |
| fig_0232 | 181 | raster | concept | agentic-ai | 0.80 | 1) Role-playing |
| fig_0233 | 182 | raster | result | agentic-ai | 0.92 | Overloading leads to confusion, inconsistency, and poor results. |
| fig_0234 | 183 | raster | result | agentic-ai | 0.74 | For example, an AI research agent could benefit from: |
| fig_0235 | 184 | raster | code | tool-action-fabric | 0.73 | However, you may need to build custom tools at times. |
| fig_0236 | 185 | raster | code | agent-protocol-fabric | 0.61 | You would also need an API key from here: https://www.exchangerate-api.com/ |
| fig_0237 | 185 | raster | code | agent-protocol-fabric | 0.65 | Once that's done, we start with some standard import statements: |
| fig_0238 | 185 | raster | code | tool-action-fabric | 0.68 | Next, we define the input fields the tool expects using Pydantic. |
| fig_0239 | 185 | raster | code | tool-action-fabric | 0.70 | Now, we define the CurrencyConverterTool by inheriting from BaseTool: |
| fig_0240 | 186 | raster | code | tool-action-fabric | 0.62 | Every tool class should have the _run method which we will execute whenever |
| fig_0241 | 186 | raster | code | agentic-ai | 0.63 | In the above code, we fetch live exchange rates using an API request. We also |
| fig_0242 | 186 | raster | code | agentic-ai | 0.74 | We assign a task to the currency_analyst agent. |
| fig_0243 | 187 | raster | code | agentic-ai | 0.70 | Finally, we create a Crew, assign the agent to the task, and execute it. |
| fig_0244 | 187 | raster | process | multi-agent | 0.65 | Printing the response, we get the following output: |
| fig_0245 | 187 | raster | process | agentic-ai | 0.72 | Works as expected! |
| fig_0246 | 188 | raster | architecture | agent-protocol-fabric | 0.62 | We’ll continue using ExchangeRate-API in our .env file: |
| fig_0247 | 188 | raster | architecture | agent-protocol-fabric | 0.64 | We’ll now write a lightweight server.py script that exposes the currency convert |
| fig_0248 | 188 | raster | code | agent-protocol-fabric | 0.68 | Now, we load environment variables and initialize the server: |
| fig_0249 | 189 | raster | result | agent-protocol-fabric | 0.65 | Next, we define the tool logic with @mcp.tool(): |
| fig_0250 | 189 | raster | code | agent-protocol-fabric | 0.62 | This function takes three inputs - amount, source currency, and target currency |
| fig_0251 | 189 | raster | result | agent-protocol-fabric | 0.68 | AI Agents figure |
| fig_0252 | 190 | raster | code | agent-protocol-fabric | 0.60 | Next, we connect to the MCP tool server. Define the server parameters to |
| fig_0253 | 190 | raster | code | agent-protocol-fabric | 0.62 | Now, we use the discovered MCP tool in an agent: |
| fig_0254 | 191 | raster | result | agentic-ai | 0.76 | We give the agent a task description: |
| fig_0255 | 191 | raster | result | agentic-ai | 0.84 | Finally, we create the Crew, pass in the inputs and run it: |
| fig_0256 | 191 | raster | result | agentic-ai | 0.74 | Printing the result, we get the following output: |
| fig_0257 | 191 | raster | result | agentic-ai | 0.87 | AI Agents figure |
| fig_0258 | 192 | raster | architecture | agentic-ai | 0.88 | 4) Cooperation |
| fig_0259 | 193 | raster | process | agentic-ai | 0.65 | Examples of useful guardrails include: |
| fig_0260 | 194 | raster | diagram | agentic-ai | 0.68 | Different types of memory in AI agents include: |
| fig_0261 | 195 | raster | architecture | agentic-ai | 0.66 | This memory isn’t just nice-to-have but it enables agents to learn from past |
| fig_0262 | 196 | raster | concept | agentic-ai | 0.70 | ● In iteration #1, the user mentions their favorite color. |
| fig_0263 | 196 | raster | concept | agentic-ai | 0.66 | ● |
| fig_0264 | 197 | raster | concept | agentic-ai | 0.84 | It doesn’t matter if the user told the Agent their name five seconds ago, it’s |
| fig_0265 | 197 | raster | architecture | agent-memory | 0.78 | ● Short-Term Memory |
| fig_0266 | 198 | raster | concept | agentic-ai | 0.65 | This is why memory is not a property of the model itself. It is a system design |
| fig_0267 | 199 | raster | result | agentic-ai | 0.87 | 1) Reflection pattern |
| fig_0268 | 200 | raster | diagram | agentic-ai | 0.78 | The AI reviews its own work to spot mistakes and iterate until it produces the |
| fig_0269 | 200 | raster | code | tool-action-fabric | 0.62 | 2) Tool use pattern |
| fig_0270 | 201 | raster | result | agentic-ai | 0.88 | 3) ReAct (Reason and Act) pattern |
| fig_0271 | 201 | raster | process | agentic-ai | 0.86 | 3) ReAct (Reason and Act) pattern |
| fig_0272 | 202 | raster | architecture | agentic-ai | 0.91 | As shown above, the Agent is going through a series of thought activities before |
| fig_0273 | 203 | raster | result | agentic-ai | 0.98 | 4) Planning pattern |
| fig_0274 | 203 | raster | diagram | agentic-ai | 0.73 | 5) Multi-Agent pattern |
| fig_0275 | 205 | raster | architecture | agentic-ai | 0.81 | Next, we define a minimal Agent class, which wraps around a conversational |
| fig_0276 | 205 | raster | architecture | agentic-ai | 0.65 | ● |
| fig_0277 | 206 | raster | architecture | agentic-ai | 0.91 | This is the core interface you’ll use to interact with your agent. |
| fig_0278 | 207 | raster | architecture | agentic-ai | 0.72 | This method handles the actual API call to your LLM provider - in this case, via |
| fig_0279 | 207 | raster | concept | agentic-ai | 0.94 | AI Agents figure |
| fig_0280 | 208 | raster | process | agentic-ai | 0.86 | It correctly remembers and reflects! |
| fig_0281 | 209 | raster | concept | agentic-ai | 0.68 | AI Agents figure |
| fig_0282 | 213 | raster | process | agentic-ai | 0.76 | Finally, we begin a manual ReAct session: |
| fig_0283 | 213 | raster | concept | agentic-ai | 0.80 | This produces the following output: |
| fig_0284 | 214 | raster | process | agentic-ai | 0.98 | This produces the following output: |
| fig_0285 | 214 | raster | process | agentic-ai | 0.98 | This produces the following output: |
| fig_0286 | 215 | raster | process | agentic-ai | 0.87 | This produces the following output: |
| fig_0287 | 215 | raster | process | agentic-ai | 0.87 | This produces the following output: |
| fig_0288 | 216 | raster | result | agentic-ai | 0.98 | This produces the following output: |
| fig_0289 | 216 | raster | process | agentic-ai | 0.87 | We get the following output: |
| fig_0290 | 217 | raster | result | agentic-ai | 0.98 | This produces the following output: |
| fig_0291 | 217 | raster | result | agentic-ai | 0.98 | We get the following output: |
| fig_0292 | 218 | raster | diagram | agentic-ai | 0.98 | Iteration 10: |
| fig_0293 | 218 | raster | result | agentic-ai | 0.98 | Finally, in this iteration, we get the following output: |
| fig_0294 | 220 | raster | architecture | llm-engineering | 0.56 | Let’s break down the full loop. |
| fig_0295 | 221 | raster | architecture | agentic-ai | 0.69 | ● |
| fig_0296 | 222 | raster | architecture | agentic-ai | 0.63 | current_prompt stores the next message to be sent to the LLM. |
| fig_0297 | 223 | raster | architecture | agentic-ai | 0.64 | Next, we feed the current_prompt into the agent. |
| fig_0298 | 223 | raster | architecture | llm-engineering | 0.62 | The current_prompt could be: |
| fig_0299 | 224 | raster | architecture | agentic-ai | 0.66 | In another case, if the response includes a Thought: line, we: |
| fig_0300 | 225 | raster | architecture | agentic-ai | 0.63 | Next, we catch the first PAUSE right after the Thought. Nothing else needs to be |
| fig_0301 | 226 | raster | architecture | llm-engineering | 0.62 | If we detect an Action: line, we: |
| fig_0302 | 227 | raster | architecture | agentic-ai | 0.63 | For example, in: Action: lookup_population: India, the regex pulls out: |
| fig_0303 | 228 | raster | architecture | tool-action-fabric | 0.64 | ● If the tool name is valid, we call it like a Python function and capture the |
| fig_0304 | 229 | raster | concept | agentic-ai | 0.89 | This produces the following output, which is indeed correct: |
| fig_0305 | 229 | raster | concept | agentic-ai | 0.73 | You now have a fully working ReAct loop without needing any external |
| fig_0306 | 231 | raster | architecture | agentic-ai | 0.89 | 1) Basic responder |
| fig_0307 | 232 | raster | architecture | agentic-ai | 0.98 | A human guides the entire flow. |
| fig_0308 | 232 | raster | architecture | agentic-ai | 0.68 | 2) Router pattern |
| fig_0309 | 233 | raster | process | agentic-ai | 0.73 | A human defines a set of tools the LLM can access to complete a task. |
| fig_0310 | 233 | raster | architecture | agentic-ai | 0.81 | 4) Multi-agent pattern |
| fig_0311 | 234 | raster | code | agentic-ai | 0.98 | The most advanced pattern, wherein, the LLM generates and executes new code |
| fig_0312 | 235 | raster | architecture | agentic-ai | 0.84 | Agent: An autonomous AI entity that perceives, reasons, and acts toward a goal |
| fig_0313 | 236 | raster | architecture | agentic-ai | 0.86 | Reflection: The agent’s process of self-assessing its actions to improve future |
| fig_0314 | 237 | raster | architecture | agentic-ai | 0.80 | ARQ: A new structured reasoning approach where an agent solves complex, |
| fig_0315 | 238 | raster | process | agent-protocol-fabric | 0.68 | MCP: A standardized way for agents to connect to external tools, APIs, and data |
| fig_0316 | 238 | raster | architecture | agentic-ai | 0.65 | AI Agents figure |
| fig_0317 | 239 | raster | concept | agentic-ai | 0.79 | Layers of Agentic AI |
| fig_0318 | 242 | raster | architecture | agentic-ai | 0.88 | 1) Parallel |
| fig_0319 | 244 | raster | architecture | agentic-ai | 0.67 | Agent2Agent(A2A) Protocol |
| fig_0320 | 245 | raster | diagram | agentic-ai | 0.71 | Instead, they communicate by exchanging context, task updates, instructions, |
| fig_0321 | 246 | raster | comparison | agent-protocol-fabric | 0.66 | Using this, AI agents connecting to an MCP server can discover new agents to |
| fig_0322 | 246 | raster | diagram | agentic-ai | 0.70 | A2A-supporting Remote Agents must publish a "JSON Agent Card" detailing |
| fig_0323 | 247 | raster | comparison | agent-protocol-fabric | 0.71 | ● |
| fig_0324 | 248 | raster | concept | agentic-ai | 0.75 | Let’s understand why this is important. |
| fig_0325 | 248 | raster | concept | agentic-ai | 0.68 | But the moment you try to bring that Agent into a real-world app, things fall |
| fig_0326 | 250 | raster | result | agentic-ai | 0.72 | Think of it this way: |
| fig_0327 | 251 | raster | code | agentic-ai | 0.76 | In the above image, the response from the Agent is not specific to any toolkit.  |
| fig_0328 | 252 | raster | architecture | agentic-ai | 0.82 | AG-UI (Agent-User Interaction): |
| fig_0329 | 253 | raster | architecture | agentic-ai | 0.78 | Your frontend stays connected to the entire agent ecosystem through one unified |
| fig_0330 | 254 | raster | diagram | agentic-ai | 0.74 | It breaks down handshakes, misconceptions and real examples and shows exactly |
| fig_0331 | 254 | raster | diagram | agentic-ai | 0.58 | Agent optimization with Opik |
| fig_0332 | 255 | raster | code | agentic-ai | 0.57 | Next, import all the required classes and functions from opik and |
| fig_0333 | 255 | raster | code | evaluation | 0.62 | ● |
| fig_0334 | 256 | raster | concept | evaluation | 0.68 | Moving on, configure the evaluation metric, which tells the optimizer how to |
| fig_0335 | 256 | raster | code | evaluation | 0.68 | Next, define your base prompt, which is the initial instruction that the |
| fig_0336 | 256 | raster | architecture | llm-engineering | 0.62 | AI Agents figure |
| fig_0337 | 257 | raster | process | llm-engineering | 0.70 | Finally, the optimizer.optimize_prompt(...) method is invoked with the dataset, |
| fig_0338 | 257 | raster | process | llm-engineering | 0.69 | It starts by evaluating the initial prompt, which sets the baseline: |
| fig_0339 | 257 | raster | process | llm-engineering | 0.59 | Then it iterates through several different prompts (written by AI), evaluates th |
| fig_0340 | 258 | raster | architecture | evaluation | 0.59 | The optimization results are also available in the Opik dashboard for further |
| fig_0341 | 258 | raster | architecture | llm-engineering | 0.65 | And that’s how you can use Opik Agent Optimizer to enhance the performance |
| fig_0342 | 259 | raster | architecture | agentic-ai | 0.61 | AI Agent Deployment Strategies |
| fig_0343 | 260 | raster | process | agentic-ai | 0.65 | ● The Agent runs periodically, like a scheduled CLI job. |
| fig_0344 | 260 | raster | architecture | data-engineering | 0.66 | 2) Stream deployment |
| fig_0345 | 261 | raster | diagram | agentic-ai | 0.68 | ● |
| fig_0346 | 261 | raster | diagram | agentic-ai | 0.64 | 4) Edge deployment |
| fig_0347 | 264 | raster | concept | agent-protocol-fabric | 0.98 | What is MCP? |
| fig_0348 | 264 | raster | concept | agent-protocol-fabric | 0.98 | What is MCP? |
| fig_0349 | 265 | raster | concept | agent-protocol-fabric | 0.74 | If they need to access real-time information, they must use external tools and |
| fig_0350 | 266 | raster | concept | agent-protocol-fabric | 0.77 | Why was MCP created? |
| fig_0351 | 267 | raster | concept | agent-protocol-fabric | 0.84 | The solution |
| fig_0352 | 268 | hybrid | diagram | agent-protocol-fabric | 0.86 | ● |
| fig_0353 | 269 | raster | architecture | agent-protocol-fabric | 0.95 | Host |
| fig_0354 | 270 | raster | architecture | agent-protocol-fabric | 0.95 | Client |
| fig_0355 | 270 | raster | architecture | agent-protocol-fabric | 0.90 | Client |
| fig_0356 | 271 | raster | result | agent-protocol-fabric | 0.77 | Server |
| fig_0357 | 272 | raster | code | tool-action-fabric | 0.65 | Tools |
| fig_0358 | 273 | raster | diagram | agent-protocol-fabric | 0.63 | For example, Claude’s client might pop up “The AI wants to use the ‘get_weather’ |
| fig_0359 | 274 | raster | code | agent-protocol-fabric | 0.76 | Resources |
| fig_0360 | 276 | raster | architecture | llm-engineering | 0.68 | This prompt function returns a list of message objects (in OpenAI format) that |
| fig_0361 | 278 | raster | code | agent-protocol-fabric | 0.93 | ● Later, if you decide to add a third required parameter (e.g., unit for |
| fig_0362 | 278 | raster | code | agent-protocol-fabric | 0.86 | ● This means all users of your API must update their code to include the new |
| fig_0363 | 278 | raster | code | agent-protocol-fabric | 0.91 | MCP figure |
| fig_0364 | 279 | raster | code | agent-protocol-fabric | 0.78 | ● |
| fig_0365 | 279 | raster | code | agent-protocol-fabric | 0.86 | ● This way, the client can then adjust its behavior on-the-fly, using the |
| fig_0366 | 280 | raster | architecture | tool-action-fabric | 0.62 | MCP versus Function calling |
| fig_0367 | 282 | raster | diagram | agent-protocol-fabric | 0.74 | Let’s start with the client, the entity that facilitates conversation between th |
| fig_0368 | 284 | raster | architecture | agent-protocol-fabric | 0.80 | It supports the full MCP ecosystem including agents, clients and servers to help |
| fig_0369 | 285 | raster | code | agent-protocol-fabric | 0.77 | Creating MCP Agents |
| fig_0370 | 287 | raster | diagram | agent-protocol-fabric | 0.62 | Instead of exposing every tool from every server at once - something that often |
| fig_0371 | 287 | raster | diagram | agent-protocol-fabric | 0.71 | MCP figure |
| fig_0372 | 289 | raster | code | agent-protocol-fabric | 0.95 | This approach is ideal when working with multiple environments or when you |
| fig_0373 | 289 | raster | code | agent-protocol-fabric | 0.89 | #2) Create From a Python Dictionary |
| fig_0374 | 290 | raster | code | agent-protocol-fabric | 0.80 | MCP Server |
| fig_0375 | 291 | raster | code | agent-protocol-fabric | 0.75 | Running this creates a ready-to-use server with: |
| fig_0376 | 292 | raster | code | agent-protocol-fabric | 0.71 | This example defines a complete MCP server with a single tool: get_weather, |
| fig_0377 | 293 | raster | code | agent-protocol-fabric | 0.65 | Prompts |
| fig_0378 | 293 | raster | architecture | agent-protocol-fabric | 0.64 | Sampling |
| fig_0379 | 294 | raster | architecture | agent-protocol-fabric | 0.68 | Elicitation |
| fig_0380 | 294 | raster | architecture | agent-protocol-fabric | 0.75 | Notifications |
| fig_0381 | 295 | raster | code | agent-protocol-fabric | 0.81 | Together, these primitives cover the full MCP surface: operations, structured |
| fig_0382 | 295 | raster | diagram | agent-protocol-fabric | 0.82 | 3) MCP Inspector |
| fig_0383 | 296 | raster | code | agent-protocol-fabric | 0.89 | 4) MCP-UI |
| fig_0384 | 297 | raster | architecture | agent-protocol-fabric | 0.74 | 5) Apps SDK |
| fig_0385 | 298 | raster | architecture | agent-protocol-fabric | 0.72 | It defines metadata (so the server can expose the widget as a capability) and a |
| fig_0386 | 299 | raster | diagram | agent-protocol-fabric | 0.88 | mcp-use provides a tunneling command that exposes your local MCP server |
| fig_0387 | 299 | raster | diagram | agent-protocol-fabric | 0.95 | This creates a public URL (e.g., https://example.local.mcp-use.run/mcp) that for |
| fig_0388 | 299 | raster | diagram | agent-protocol-fabric | 0.95 | If you're using the built-in development runner, you can enable tunneling |
| fig_0389 | 300 | raster | diagram | agent-protocol-fabric | 0.80 | This automatically spins up your local server and creates a tunnel for it. |
| fig_0390 | 300 | raster | diagram | agent-protocol-fabric | 0.80 | Tunneling enables: |
| fig_0391 | 301 | raster | architecture | agent-protocol-fabric | 0.70 | As long as the endpoint is reachable, agents immediately detect new tools or |
| fig_0392 | 301 | raster | architecture | agent-protocol-fabric | 0.69 | After deployment, you receive: |
| fig_0393 | 304 | raster | concept | infrastructure | 0.71 | Why do we need optimization? |
| fig_0394 | 304 | raster | concept | infrastructure | 0.76 | Why do we need optimization? |
| fig_0395 | 305 | raster | result | infrastructure | 0.84 | ● |
| fig_0396 | 306 | raster | concept | infrastructure | 0.63 | They aim to make the model smaller - that is why the name “model compression.” |
| fig_0397 | 306 | raster | diagram | infrastructure | 0.72 | ● |
| fig_0398 | 307 | raster | diagram | ai-ml-foundation | 0.64 | Distillation: In this context, distillation means transferring or condensing |
| fig_0399 | 308 | raster | process | infrastructure | 0.98 | This is a two-step process: |
| fig_0400 | 308 | raster | diagram | infrastructure | 0.74 | The primary objective of knowledge distillation is to transfer the knowledge, or |
| fig_0401 | 309 | raster | result | infrastructure | 0.74 | 2) Pruning |
| fig_0402 | 310 | raster | result | business-automation | 0.68 | In the image above, both sub-trees result in the same increase in cost. However, |
| fig_0403 | 310 | raster | result | infrastructure | 0.84 | Removing an entire layer is another option. But we rarely practice it because it |
| fig_0404 | 311 | raster | result | infrastructure | 0.84 | The idea is to eliminate entire nodes from the network. |
| fig_0405 | 311 | raster | result | infrastructure | 0.74 | This results in faster inference and lower memory usage. |
| fig_0406 | 312 | raster | diagram | infrastructure | 0.98 | ● |
| fig_0407 | 312 | raster | diagram | infrastructure | 0.98 | ● |
| fig_0408 | 313 | raster | diagram | infrastructure | 0.84 | The idea will become more clear if we understand these individual terms: |
| fig_0409 | 314 | raster | process | infrastructure | 0.98 | There are many different matrix factorization methods available, such as Singula |
| fig_0410 | 315 | raster | process | infrastructure | 0.98 | The choice of rank k is directly linked to the trade-off between model size |
| fig_0411 | 315 | raster | process | infrastructure | 0.98 | The benefit of doing this is that it reduces the computational complexity of the |
| fig_0412 | 316 | raster | result | ai-ml-foundation | 0.53 | 4) Quantization |
| fig_0413 | 318 | raster | process | infrastructure | 0.78 | LLMs, however, deal with variable-length inputs (the prompt) and generate |
| fig_0414 | 318 | raster | process | infrastructure | 0.91 | So if you batch some requests, all will finish at different times, and the GPU |
| fig_0415 | 318 | raster | architecture | infrastructure | 0.68 | Continuous Batching solves this. |
| fig_0416 | 319 | raster | architecture | infrastructure | 0.65 | This keeps the GPU pipeline full and maximizes utilization. |
| fig_0417 | 319 | raster | process | infrastructure | 0.70 | Prefill-decode disaggregation |
| fig_0418 | 320 | raster | diagram | ai-ml-foundation | 0.59 | In contrast, a standard ML model typically has a single, unified computation |
| fig_0419 | 320 | raster | comparison | ai-ml-foundation | 0.63 | GPU memory management + KV caching |
| fig_0420 | 321 | raster | architecture | agent-memory | 0.55 | That said, KV cache takes up a significant memory since it’s stored in contiguou |
| fig_0421 | 321 | raster | result | agent-memory | 0.58 | Paged Attention solves this problem by storing KV caching in non-contiguous |
| fig_0422 | 322 | raster | result | llm-engineering | 0.54 | Different open-source frameworks each have their own implementations for |
| fig_0423 | 323 | raster | diagram | infrastructure | 0.72 | Model sharding strategies |
| fig_0424 | 324 | raster | comparison | ai-ml-foundation | 0.84 | MoE models use a specialized parallelism strategy called expert parallelism, |
| fig_0425 | 324 | raster | diagram | infrastructure | 0.78 | LLM Optimization figure |
| fig_0426 | 325 | raster | architecture | infrastructure | 0.74 | KV Caching in LLMs |
| fig_0427 | 326 | raster | result | ai-ml-foundation | 0.68 | As shown in the visual above: |
| fig_0428 | 326 | raster | diagram | ai-ml-foundation | 0.76 | Next, let's see how the last hidden state is computed within the transformer lay |
| fig_0429 | 327 | raster | result | rag-knowledge-engineering | 0.76 | None of the other query vectors are needed during inference. |
| fig_0430 | 327 | raster | result | rag-knowledge-engineering | 0.65 | The above insight suggests that to generate a new token, every attention |
| fig_0431 | 328 | raster | comparison | ai-ml-foundation | 0.65 | But there's one more key insight here. |
| fig_0432 | 328 | raster | comparison | ai-ml-foundation | 0.65 | Thus, we just need to generate a KV vector for the token generated one step |
| fig_0433 | 329 | raster | process | ai-ml-foundation | 0.53 | To generate a token: |
| fig_0434 | 332 | raster | code | evaluation | 0.86 | In fact, in many cases, it is also difficult to formalize an evaluation metric a |
| fig_0435 | 332 | raster | concept | evaluation | 0.87 | The solution |
| fig_0436 | 333 | raster | concept | evaluation | 0.75 | However, with unrelated context and output, we get a low score as expected: |
| fig_0437 | 333 | raster | concept | evaluation | 0.78 | Under the hood, G-Eval first uses the task introduction and evaluation criteria  |
| fig_0438 | 334 | raster | result | evaluation | 0.88 | LLM Arena-as-a-Judge |
| fig_0439 | 335 | raster | comparison | evaluation | 0.96 | Just like G-Eeval, you can define what “better” means (e.g., more helpful, more |
| fig_0440 | 336 | raster | comparison | evaluation | 0.89 | ● |
| fig_0441 | 337 | raster | code | evaluation | 0.91 | The code snippet below depicts how to use DeepEval (open-source) to run |
| fig_0442 | 337 | raster | process | evaluation | 0.98 | LLM Evaluation figure |
| fig_0443 | 338 | raster | code | evaluation | 0.98 | Define a custom metric: This metric uses ConversationalGEval to define a metric |
| fig_0444 | 338 | raster | process | evaluation | 0.98 | Finally, run the evaluation: |
| fig_0445 | 339 | raster | code | evaluation | 0.95 | Done! |
| fig_0446 | 339 | raster | concept | evaluation | 0.83 | Moreover, you also get a full UI to inspect individual turns: |
| fig_0447 | 340 | raster | diagram | evaluation | 0.81 | Conversations get even more complex when tools are involved. |
| fig_0448 | 341 | raster | result | agent-protocol-fabric | 0.60 | ● Integrate the MCP server with the LLM app. |
| fig_0449 | 341 | raster | code | evaluation | 0.69 | #1) Setup |
| fig_0450 | 342 | raster | comparison | agent-protocol-fabric | 0.70 | Notice that in our implementation, we intentionally avoid specifying any |
| fig_0451 | 343 | raster | code | agent-protocol-fabric | 0.71 | This is the layer that sits between the LLM and the MCP server. |
| fig_0452 | 344 | raster | process | tool-action-fabric | 0.71 | We filter the tool calls from the response to create an object of MCPToolCall |
| fig_0453 | 345 | raster | code | evaluation | 0.70 | #6) Define metric |
| fig_0454 | 345 | raster | code | evaluation | 0.77 | #6) Define metric |
| fig_0455 | 346 | raster | code | evaluation | 0.85 | This outputs a score between 0-1 with a 0.5 threshold default. |
| fig_0456 | 346 | raster | concept | evaluation | 0.73 | ● query |
| fig_0457 | 347 | raster | concept | evaluation | 0.75 | Beyond end-to-end scoring, LLM apps need fine-grained visibility. |
| fig_0458 | 347 | raster | architecture | evaluation | 0.98 | Apps |
| fig_0459 | 348 | raster | architecture | evaluation | 0.77 | Here’s a quick explanation: |
| fig_0460 | 349 | raster | architecture | evaluation | 0.86 | Define your LLM app in a method decorated with the @observe decorator: |
| fig_0461 | 349 | raster | architecture | evaluation | 0.68 | Next, attach component-level metrics to each component you want to trace: |
| fig_0462 | 349 | raster | architecture | evaluation | 0.72 | LLM Evaluation figure |
| fig_0463 | 350 | raster | concept | evaluation | 0.85 | This produces an evaluation report: |
| fig_0464 | 350 | raster | concept | evaluation | 0.85 | You can also inspect individual tests to understand why they failed/passed: |
| fig_0465 | 351 | raster | architecture | evaluation | 0.74 | Correctness and reliability are only part of the story. |
| fig_0466 | 352 | raster | diagram | evaluation | 0.68 | In practice, fixing this demands implementing SOTA adversarial strategies like |
| fig_0467 | 353 | raster | diagram | evaluation | 0.71 | Below, we have our LLM app we want to perform red teaming on: |
| fig_0468 | 353 | raster | code | evaluation | 0.61 | We have kept a simple LLM call here for simplicity, but you can have any LLM |
| fig_0469 | 354 | raster | code | llm-engineering | 0.55 | Bias also accepts “Gender”, “Politics”, and “Religion” as types. |
| fig_0470 | 355 | raster | concept | evaluation | 0.62 | You can also generate a summary of the risk_assessment object as follows: |
| fig_0471 | 355 | raster | concept | agent-protocol-fabric | 0.61 | Lastly, you can further assess the risk report by logging everything in your |
| fig_0472 | 356 | raster | result | evaluation | 0.73 | The framework also implements all SOTA red teaming techniques from the latest |
| fig_0473 | 361 | raster | code | infrastructure | 0.71 | #1) Start the vLLM Server |
| fig_0474 | 362 | raster | code | infrastructure | 0.75 | At this point, our local deployment behaves like any hosted LLM endpoint. |
| fig_0475 | 362 | raster | code | infrastructure | 0.91 | #3) Scale to Multiple GPUs |
| fig_0476 | 363 | raster | code | infrastructure | 0.68 | #4) Load LoRA Adapters |
| fig_0477 | 363 | raster | diagram | infrastructure | 0.82 | #5) Benefit Automatically from Continuous Batching |
| fig_0478 | 364 | raster | code | infrastructure | 0.80 | Each request simply specifies the model to use. |
| fig_0479 | 365 | raster | architecture | infrastructure | 0.75 | This example deploys a Llama model with LitServe in a simple end-to-end flow. |
| fig_0480 | 366 | raster | code | infrastructure | 0.71 | Here we load the Llama model into memory so it’s ready for inference. |
| fig_0481 | 366 | raster | code | infrastructure | 0.68 | 2) Decode the Request |
| fig_0482 | 367 | raster | code | infrastructure | 0.58 | predict() can stream output by yielding tokens as they are produced. |
| fig_0483 | 367 | raster | code | infrastructure | 0.60 | 4) Return the Response |
| fig_0484 | 368 | raster | code | infrastructure | 0.68 | This exposes the model as an HTTP endpoint. |
| fig_0485 | 370 | raster | concept | observability | 0.86 | That is the purpose of observability. |
| fig_0486 | 371 | raster | architecture | evaluation | 0.65 | Evaluation measures how well the system performs on a defined set of tasks. |
| fig_0487 | 371 | raster | architecture | evaluation | 0.72 | ● It uses curated datasets, metrics and controlled tests to assess qualities |
| fig_0488 | 372 | raster | architecture | observability | 0.65 | ● It captures real inputs, model outputs, retrieved context, latencies, costs |
| fig_0489 | 373 | raster | code | tool-action-fabric | 0.78 | Tracking a Simple Python Function |
| fig_0490 | 373 | raster | code | tool-action-fabric | 0.76 | Tracking a Simple Python Function |
| fig_0491 | 374 | raster | code | observability | 0.84 | If we run the above code, which is decorated with the @track decorator, and afte |
| fig_0492 | 374 | raster | code | observability | 0.82 | As depicted above, after running the function, Opik automatically creates a |
| fig_0493 | 375 | raster | result | tool-action-fabric | 0.71 | Also, if you invoke this function multiple times, like below: |
| fig_0494 | 375 | raster | result | tool-action-fabric | 0.75 | The dashboard will show all the invocations of the functions: |
| fig_0495 | 376 | raster | architecture | observability | 0.87 | Opening any specific invocation, we can look at the inputs and the outputs in a |
| fig_0496 | 376 | raster | architecture | observability | 0.86 | This seamless integration makes it easy to monitor and debug your workflows |
| fig_0497 | 377 | raster | code | observability | 0.68 | Next, we shall be using Opik's OpenAI integration which is imported below, |
| fig_0498 | 377 | raster | code | agent-protocol-fabric | 0.63 | Moving on, we wrap the OpenAI client with Opik’s track_openai function. This |
| fig_0499 | 377 | raster | result | observability | 0.63 | Next, we define our multimodal prompt input as follows: |
| fig_0500 | 378 | raster | diagram | agent-protocol-fabric | 0.68 | Finally, we invoke the chat completion API as follows: |
| fig_0501 | 378 | raster | diagram | agent-protocol-fabric | 0.68 | Here, we make the API call using the chat.completions.create method: |
| fig_0502 | 379 | raster | result | observability | 0.74 | Opening this specific run highlights so many details about the LLM invocation, |
| fig_0503 | 379 | raster | result | observability | 0.68 | LLM Observability figure |
| fig_0504 | 380 | raster | process | agent-protocol-fabric | 0.68 | Next, we again create an OpenAI client, but this time, we specify the base_url a |
| fig_0505 | 380 | hybrid | process | agent-protocol-fabric | 0.73 | Next, to log all the invocations made to our client, we pass the client to the |
| fig_0506 | 381 | raster | diagram | agent-protocol-fabric | 0.74 | Finally, we invoke the completion API as follows: |
| fig_0507 | 381 | raster | diagram | observability | 0.76 | If we head over to the dashboard again, we see another entry: |
| fig_0508 | 381 | raster | diagram | observability | 0.72 | LLM Observability figure |
| fig_0509 | 382 | raster | result | observability | 0.59 | That was simple, wasn't it? |

---

## 6. Figure manifest — full records

### fig_0001 — AI Engineering

- **Page:** 0 (PDF page 1) · **Chapter:** Front Matter
- **BBox:** [393.19, 43.15, 547.69, 197.65] on page 612×792 pt · **Render:** 429×430 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.4
- **Mapping:** AI / ML Foundation (0.74) · RAG / Knowledge Engineering (0.48) · Agentic AI (0.48)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.74 → review queue
- **Integrity:** sha `7751dc271be0ca48` · dup group `dup_0001` (1)
- **Caption:** AI Engineering
- **Paragraph after:** AI Engineering System Design Patterns for LLMs, RAG and Agents Daily Dose of Akshay Pachaar & Avi Chawla
- **OCR:** Fp Eg

### fig_0002 — AI Engineering

- **Page:** 0 (PDF page 1) · **Chapter:** Front Matter
- **BBox:** [0.00, 71.83, 276.76, 169.33] on page 612×792 pt · **Render:** 768×271 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.6
- **Mapping:** AI / ML Foundation (0.74) · RAG / Knowledge Engineering (0.48) · Agentic AI (0.48)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.74 → review queue
- **Integrity:** sha `4d4a62c740922704` · dup group `dup_0002` (1)
- **Caption:** AI Engineering
- **Paragraph after:** AI Engineering System Design Patterns for LLMs, RAG and Agents Daily Dose of Akshay Pachaar & Avi Chawla
- **OCR:** 2025 EDITION

### fig_0003 — LLMs, RAG and Agents

- **Page:** 0 (PDF page 1) · **Chapter:** Front Matter
- **BBox:** [297.51, 532.31, 521.74, 656.81] on page 612×792 pt · **Render:** 623×346 px
- **Composition:** hybrid · **Role:** architecture · **Quality:** 0.7
- **Mapping:** AI / ML Foundation (0.63) · RAG / Knowledge Engineering (0.54) · Agentic AI (0.54)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.63 → review queue
- **Integrity:** sha `9d74ac710df6671c` · dup group `dup_0003` (1)
- **Heading:** LLMs, RAG and Agents
- **Caption:** Daily Dose of Akshay Pachaar & Avi Chawla
- **Paragraph before:** E AI Engineering System Design Patterns for LLMs, RAG and Agents
- **Paragraph after:** Daily Dose of Akshay Pachaar & Avi Chawla Data Science

### fig_0004 — LLMs, RAG and Agents

- **Page:** 0 (PDF page 1) · **Chapter:** Front Matter
- **BBox:** [64.86, 538.08, 178.11, 651.33] on page 612×792 pt · **Render:** 314×315 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.4
- **Mapping:** AI / ML Foundation (0.63) · RAG / Knowledge Engineering (0.54) · Agentic AI (0.54)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.63 → review queue
- **Integrity:** sha `88e9f3a6905af45a` · dup group `dup_0004` (1)
- **Heading:** LLMs, RAG and Agents
- **Caption:** Daily Dose of Akshay Pachaar & Avi Chawla
- **Paragraph before:** E AI Engineering System Design Patterns for LLMs, RAG and Agents
- **Paragraph after:** Daily Dose of Akshay Pachaar & Avi Chawla Data Science

### fig_0005 — LLMs, RAG and Agents

- **Page:** 0 (PDF page 1) · **Chapter:** Front Matter
- **BBox:** [186.41, 545.08, 289.16, 644.08] on page 612×792 pt · **Render:** 286×275 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.4
- **Mapping:** AI / ML Foundation (0.63) · RAG / Knowledge Engineering (0.54) · Agentic AI (0.54)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.63 → review queue
- **Integrity:** sha `842b90a787d95795` · dup group `dup_0005` (1)
- **Heading:** LLMs, RAG and Agents
- **Caption:** Daily Dose of Akshay Pachaar & Avi Chawla
- **Paragraph before:** E AI Engineering System Design Patterns for LLMs, RAG and Agents
- **Paragraph after:** Daily Dose of Akshay Pachaar & Avi Chawla Data Science

### fig_0006 — LLMs, RAG and Agents

- **Page:** 0 (PDF page 1) · **Chapter:** Front Matter
- **BBox:** [60.76, 674.10, 531.00, 753.19] on page 612×792 pt · **Render:** 1307×220 px
- **Composition:** hybrid · **Role:** architecture · **Quality:** 1
- **Mapping:** AI / ML Foundation (0.63) · RAG / Knowledge Engineering (0.54) · Agentic AI (0.54)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.63 → review queue
- **Integrity:** sha `71c095685447e03a` · dup group `dup_0006` (1)
- **Heading:** LLMs, RAG and Agents
- **Paragraph before:** E AI Engineering System Design Patterns for LLMs, RAG and Agents
- **OCR:** o, ¢ Daily Dose of Akshay Pachaar & Avi Chawla ) (] «* ® Data Science DailyDoseofDS.com

### fig_0007 — this book and your time?

- **Page:** 0 (PDF page 2) · **Chapter:** Front Matter
- **BBox:** [67.50, 235.22, 547.50, 529.22] on page 612×792 pt · **Render:** 1333×817 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.74) · AI / ML Foundation (0.54) · Evaluation (0.41)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.74 → review queue
- **Integrity:** sha `a3df1ae7c13b1939` · dup group `dup_0007` (1)
- **Heading:** this book and your time?
- **Caption:** Scan the QR code below or open this link to start the assessment. It will only take
- **Paragraph before:** this book and your time? The reading time of this book is about hours. But not all chapters will be of relevance to you. This 2-minute assessment will test your current expertise and recommend chapters that will be most useful to you.
- **Paragraph after:** Scan the QR code below or open this link to start the assessment. It will only take minutes to complete. https://bit.ly/ai-engg-assessment
- **OCR:** Are you prepared for a career in Al Engineering? Answer 15 yes/no questions, and we'll email you the list of chapters that you must read to improve your Al Engineering skillset. Start the Assessment Below! Start The Assessment 2025 EDITION “Reg Al Engineering T

### fig_0008 — this book and your time?

- **Page:** 0 (PDF page 2) · **Chapter:** Front Matter
- **BBox:** [66.00, 582.00, 546.50, 708.00] on page 612×792 pt · **Render:** 1335×350 px
- **Composition:** hybrid · **Role:** code · **Quality:** 0.7
- **Mapping:** Agent Protocol Fabric (0.63) · AI / ML Foundation (0.63) · Evaluation (0.44)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.63 → review queue
- **Integrity:** sha `63c65cef6d2525e2` · dup group `dup_0008` (1)
- **Heading:** this book and your time?
- **Paragraph before:** relevance to you. This 2-minute assessment will test your current expertise and recommend chapters that will be most useful to you. Scan the QR code below or open this link to start the assessment. It will only take minutes to complete.
- **OCR:** -assessment =] Q o ] " = B = » = = =

### fig_0009 — What is an LLM?

- **Page:** 6 (PDF page 8) · **Chapter:** LLMs
- **BBox:** [150.75, 143.47, 461.25, 279.97] on page 612×792 pt · **Render:** 863×379 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.84) · Agent Protocol Fabric (0.51)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.84 → review queue
- **Integrity:** sha `5648cf423f17013c` · dup group `dup_0009` (1)
- **Heading:** What is an LLM?
- **Caption:** “Once upon a…”
- **Paragraph before:** What is an LLM? Imagine someone begins a sentence:
- **Paragraph after:** “Once upon a…” You naturally think “time.” Or they say: “The capital of France is…”
- **OCR:** Once upon a time there was a clever fox...

### fig_0010 — What is an LLM?

- **Page:** 6 (PDF page 8) · **Chapter:** LLMs
- **BBox:** [199.50, 434.41, 412.50, 564.91] on page 612×792 pt · **Render:** 591×363 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.6
- **Mapping:** AI / ML Foundation (0.84) · Agent Protocol Fabric (0.51)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.84 → review queue
- **Integrity:** sha `d98e695f9e477ae2` · dup group `dup_0010` (1)
- **Heading:** What is an LLM?
- **Caption:** This simple act of predicting what comes next is the foundation of how large
- **Paragraph before:** You naturally think “time.” Or they say: “The capital of France is…” You immediately think “Paris.”
- **Paragraph after:** This simple act of predicting what comes next is the foundation of how large language models(LLMs) operate. They learn to make these predictions by reading enormous amounts of text: books, articles, scientific papers, code, conversations, and instructions.
- **OCR:** aQ (WP LLM..

### fig_0011 — With enough exposure, the model becomes remarkably good at continuing any

- **Page:** 7 (PDF page 9) · **Chapter:** LLMs
- **BBox:** [153.75, 67.50, 458.25, 332.25] on page 612×792 pt · **Render:** 845×735 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.89) · Agent Protocol Fabric (0.46)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.89 → auto-accept
- **Integrity:** sha `f27549d55af745f3` · dup group `dup_0011` (1)
- **Caption:** With enough exposure, the model becomes remarkably good at continuing any
- **Paragraph after:** With enough exposure, the model becomes remarkably good at continuing any piece of text in a coherent, meaningful way. At the technical level, an LLM processes text in small units called tokens. A token may be a word, part of a word or even punctuation.
- **OCR:** &l Instructions Gomsersations £ T — \@ Articles Books

### fig_0012 — The model looks at the tokens so far and predicts the next one. Repeating this

- **Page:** 7 (PDF page 9) · **Chapter:** LLMs
- **BBox:** [203.62, 436.91, 408.38, 583.91] on page 612×792 pt · **Render:** 569×408 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.85) · RAG / Knowledge Engineering (0.40) · Agent Protocol Fabric (0.40) · Tool / Action Fabric (0.40)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.85 → auto-accept
- **Integrity:** sha `83663587a8e17f05` · dup group `dup_0012` (2)
- **Caption:** The model looks at the tokens so far and predicts the next one. Repeating this
- **Paragraph before:** With enough exposure, the model becomes remarkably good at continuing any piece of text in a coherent, meaningful way. At the technical level, an LLM processes text in small units called tokens. A token may be a word, part of a word or even punctuation.
- **Paragraph after:** The model looks at the tokens so far and predicts the next one. Repeating this process generates full answers, explanations, or code. Everything an LLM does from summarizing a document, generating a function or explaining a concept emerges from choosing the next token that best fits the
- **OCR:** Tokenization Thiﬂk- by step fore you answer a question, include the reasoning tokens in

### fig_0013 — To formalise, a large language model is a Transformer-based neural network

- **Page:** 8 (PDF page 10) · **Chapter:** LLMs
- **BBox:** [201.38, 67.50, 410.62, 448.50] on page 612×792 pt · **Render:** 581×1058 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `db3bca1e0562b4fb` · dup group `dup_0013` (2)
- **Caption:** To formalise, a large language model is a Transformer-based neural network
- **Paragraph after:** To formalise, a large language model is a Transformer-based neural network trained on massive text corpora to predict the next token in a sequence and through this process acquires the ability to understand, generate and reason with human language.
- **OCR:** ® ©® © o Decoder block * N \| 1 \| 1 v v v v

### fig_0014 — Need for LLMs

- **Page:** 9 (PDF page 11) · **Chapter:** LLMs
- **BBox:** [171.00, 143.47, 441.00, 423.22] on page 612×792 pt · **Render:** 750×777 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.74) · RAG / Knowledge Engineering (0.48) · Evaluation (0.48)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.74 → review queue
- **Integrity:** sha `da24eb2d96b0ebf8` · dup group `dup_0014` (1)
- **Heading:** Need for LLMs
- **Caption:** ● A translation system handled only translation.
- **Paragraph before:** Need for LLMs Before LLMs, AI systems were built for specific tasks.
- **Paragraph after:** ● A translation system handled only translation. ● A summarizer knew only summarization. ●
- **OCR:** Translated text Sentiment score Sentiment classifier Fragmented systems

### fig_0015 — Language naturally encodes reasoning steps, factual knowledge, explanations and

- **Page:** 10 (PDF page 12) · **Chapter:** LLMs
- **BBox:** [168.75, 67.50, 443.25, 318.75] on page 612×792 pt · **Render:** 763×698 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `410d8969fe8cc516` · dup group `dup_0015` (1)
- **Caption:** Language naturally encodes reasoning steps, factual knowledge, explanations and
- **Paragraph after:** Language naturally encodes reasoning steps, factual knowledge, explanations and communication patterns. Training a model on large enough text collections allowed it to internalize these patterns and apply them across tasks. As a result, a single system could now answer questions, write code, analyze text
- **OCR:** Qé&A x Question-answering / Analyze text Write code M (Large Language Model) Generate content Single systew, wmany tasks

### fig_0016 — What makes an LLM ‘large’ ?

- **Page:** 11 (PDF page 13) · **Chapter:** LLMs
- **BBox:** [197.25, 143.47, 414.75, 259.72] on page 612×792 pt · **Render:** 605×323 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.6
- **Mapping:** AI / ML Foundation (0.84) · Infrastructure (0.51)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.84 → review queue
- **Integrity:** sha `4f11cdb8f845ba83` · dup group `dup_0016` (1)
- **Heading:** What makes an LLM ‘large’ ?
- **Caption:** ● Number of parameters it contains
- **Paragraph before:** What makes an LLM ‘large’ ? When we call a language model “large,” we are referring to its scale:
- **Paragraph after:** ● Number of parameters it contains ● Amount of data it has been trained on ● Compute used to train it
- **OCR:** Q ?o what makes LM large...

### fig_0017 — What makes an LLM ‘large’ ?

- **Page:** 11 (PDF page 13) · **Chapter:** LLMs
- **BBox:** [152.37, 433.74, 462.87, 659.49] on page 612×792 pt · **Render:** 862×627 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `eb32ff7264a6498e` · dup group `dup_0017` (1)
- **Heading:** What makes an LLM ‘large’ ?
- **Caption:** They could mimic style but struggled with tasks that required reasoning,
- **Paragraph before:** Parameters are the internal values that the model adjusts during training. Each parameter represents a small piece of the patterns the model has learned. Earlier language models were much smaller and could only capture surface-level text patterns.
- **Paragraph after:** They could mimic style but struggled with tasks that required reasoning, abstraction or generalization.
- **OCR:** Swaller Jntasex —— Struggle with Soni / Saall el feasonng Less compute

### fig_0018 — Larger models began to follow detailed instructions, perform multi-step

- **Page:** 12 (PDF page 14) · **Chapter:** LLMs
- **BBox:** [133.88, 117.07, 478.12, 315.07] on page 612×792 pt · **Render:** 957×550 px
- **Composition:** raster · **Role:** process · **Quality:** 0.6
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `d0acd02e0c086a7f` · dup group `dup_0018` (1)
- **Caption:** Larger models began to follow detailed instructions, perform multi-step
- **Paragraph before:** As researchers increased model size, dataset diversity and training compute, a clear shift appeared.
- **Paragraph after:** Larger models began to follow detailed instructions, perform multi-step reasoning and solve problems they had never encountered directly in training. This wasn’t the result of adding new rules or programming specific behaviors. It emerged naturally from giving the model enough capacity to learn deeper
- **OCR:** Multi-step réﬂSDv\?r\s Massive compute

### fig_0019 — How are LLMs built?

- **Page:** 13 (PDF page 15) · **Chapter:** LLMs
- **BBox:** [227.25, 212.82, 384.75, 496.32] on page 612×792 pt · **Render:** 437×787 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.4
- **Mapping:** AI / ML Foundation (0.84) · Software Architecture (0.46) · Infrastructure (0.40)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.84 → review queue
- **Integrity:** sha `5c9cb6781706a72e` · dup group `dup_0013` (2)
- **Heading:** How are LLMs built?
- **Caption:** Transformer
- **Paragraph before:** Before an LLM can be trained, it needs an architecture that can process text, learn patterns and scale across large datasets. This architecture is built from several core components that work together to turn raw text into structured representations the model can learn from.
- **Paragraph after:** Transformer At the center of modern LLMs is the Transformer. A Transformer is designed to look at all tokens in the input at once and identify which parts of the text are most relevant to each other.
- **OCR:** 3 Decoder block * N v

### fig_0020 — This approach keeps the vocabulary manageable and allows the model to handle

- **Page:** 14 (PDF page 16) · **Chapter:** LLMs
- **BBox:** [205.50, 117.07, 406.50, 261.07] on page 612×792 pt · **Render:** 559×400 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `8d8820f85d723587` · dup group `dup_0012` (2)
- **Caption:** This approach keeps the vocabulary manageable and allows the model to handle
- **Paragraph before:** Text is first broken into tokens. A token may be a word or part of a word, depending on how common it is.
- **Paragraph after:** This approach keeps the vocabulary manageable and allows the model to handle any language input. These tokens are then mapped to numerical representations so the model can work with them.
- **OCR:** Tokenization Think step by step pefore you answer a question, include the reasoning tokens in

### fig_0021 — Transformer Layers

- **Page:** 14 (PDF page 16) · **Chapter:** LLMs
- **BBox:** [200.25, 425.62, 411.75, 688.12] on page 612×792 pt · **Render:** 587×729 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `235f406b261fcd6b` · dup group `dup_0019` (1)
- **Heading:** Transformer Layers
- **Paragraph before:** These tokens are then mapped to numerical representations so the model can work with them. Transformer Layers The model contains many Transformer layers stacked on top of each other.
- **OCR:** Transformer Decoder Block Layer norm A4 Layer norm 1 Masked self-attention I

### fig_0022 — Positional Encoding

- **Page:** 15 (PDF page 17) · **Chapter:** LLMs
- **BBox:** [190.50, 226.53, 421.50, 395.28] on page 612×792 pt · **Render:** 641×468 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `62656cf873c69752` · dup group `dup_0020` (1)
- **Heading:** Positional Encoding
- **Caption:** To provide this information, positional encodings are added to the token
- **Paragraph before:** As the sequence moves through these layers, the model builds a deeper view of the text. Positional Encoding Transformers do not naturally know the order in which tokens appear.
- **Paragraph after:** To provide this information, positional encodings are added to the token representations. These encodings give the model a sense of sequence, enabling it to interpret ordered structures such as sentences, lists, or code.
- **OCR:** Inputs “BE E-E CFE Bl @@@@ Positional embedding Transformer Decoder Block

### fig_0023 — How to train LLM from scratch?

- **Page:** 17 (PDF page 19) · **Chapter:** LLMs
- **BBox:** [142.50, 311.97, 469.50, 698.22] on page 612×792 pt · **Render:** 909×1073 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.88) · RAG / Knowledge Engineering (0.47)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.88 → auto-accept
- **Integrity:** sha `c7e787f4c2666a02` · dup group `dup_0021` (1)
- **Heading:** How to train LLM from scratch?
- **Paragraph before:** Preference fine-tuning ● Reasoning fine-tuning The visual provides a clear summary of how these stages fit together.
- **OCR:** 14 stages of LLM Training 13 oin.DailyDoseofDS.com Stage O Ra 2) Output try peter 3 'v_\dz?mlg ————— hand and initialized deepseck hello 4485n model Untrained LM PR ) What s an U7 T3 ey deepseelc deepseelc 4 User e g Untrained Pre-trained A Pre-training i wm um " How do UM work \| ! ad - What are Uit params?\| \| Huge The LLM simply learns to continve the T =~ T T 7 Text corpus text Instead of being conversational (@) output (Wt s om c)_ ‘ Qea [N I (3 Query = @ - \|deepseek deepseelc User Instruction \| @B Tain \| eretrained Instruction A fine-tuning \| Instruction um fine-tuned LM, AnUMisatypeof \| response 5 ML model that traived. \| \| pales The LLM becomes conversational, providing helpful answers. @ Tnstruction (7>E 9 - preferred response - ) \| Response #1 \| response pair Stage 2 docpseelc \| 2. : ‘ ® vvvvv B -> 2 = Preference (1) Query TInstruction \| - ) ine-tuned LUM\| \| ine-tuning f @1 User

### fig_0024 — 0) Randomly initialized LLM

- **Page:** 18 (PDF page 20) · **Chapter:** LLMs
- **BBox:** [136.88, 209.76, 475.12, 337.26] on page 612×792 pt · **Render:** 939×354 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.72) · Agent Protocol Fabric (0.54) · LLM Engineering (0.44)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.72 → review queue
- **Integrity:** sha `4e0cff7e1c05a19d` · dup group `dup_0022` (1)
- **Heading:** 0) Randomly initialized LLM
- **Caption:** 1) Pre-training
- **Paragraph before:** At this point, the model knows nothing. You ask, “What is an LLM?” and get gibberish like “try peter hand and hello 448Sn”. It hasn’t seen any data yet and possesses just random weights.
- **Paragraph after:** 1) Pre-training This stage teaches the LLM the basics of language by training it on massive corpora to predict the next token. This way, it absorbs grammar, world facts, etc. But it’s not good at conversation because when prompted, it just continues the
- **OCR:** 0) Randomly initialized LLM try peter hand and hello 4485n (2) output User Untrained LLM Random output

### fig_0025 — 1) Pre-training

- **Page:** 18 (PDF page 20) · **Chapter:** LLMs
- **BBox:** [138.75, 465.07, 473.25, 600.82] on page 612×792 pt · **Render:** 929×377 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.86) · LLM Engineering (0.49)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.86 → auto-accept
- **Integrity:** sha `6a9e3b56ec24a785` · dup group `dup_0023` (1)
- **Heading:** 1) Pre-training
- **Caption:** 2) Instruction fine-tuning
- **Paragraph before:** 1) Pre-training This stage teaches the LLM the basics of language by training it on massive corpora to predict the next token. This way, it absorbs grammar, world facts, etc. But it’s not good at conversation because when prompted, it just continues the
- **Paragraph after:** 2) Instruction fine-tuning To make it conversational, we do Instruction Fine-tuning by training on instruction-response pairs. This helps it learn how to follow prompts and format replies.
- **OCR:** 1) Pre-training Text corpus The LM simply learns to continue the text instead of being conversational aa Bl o I a a - ﬁ) — > deepseek Ime\ Untrained Huge deepseek Pre-trained um wm ad -’ .} (@) output What is an LLMZ

### fig_0026 — Now it can:

- **Page:** 19 (PDF page 21) · **Chapter:** LLMs
- **BBox:** [129.38, 67.50, 482.62, 219.75] on page 612×792 pt · **Render:** 981×423 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `fc675048923dc11c` · dup group `dup_0024` (1)
- **Caption:** Now it can:
- **Paragraph after:** Now it can: ● Answer questions ● Summarize content
- **OCR:** 2) Instruction fine-tuning The LLM becomes conversational, What is an LLM? ‘ providing helpful answers. - — — — = = —"= Instruction response pairs deepseek deepseek Pre-trained Instruction um fine-tuned LLM

### fig_0027 — That’s not just for feedback, but it’s valuable human preference data.

- **Page:** 20 (PDF page 22) · **Chapter:** LLMs
- **BBox:** [121.88, 67.50, 490.12, 378.75] on page 612×792 pt · **Render:** 1023×865 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.69) · Tool / Action Fabric (0.59) · Agent Protocol Fabric (0.38) · Evaluation (0.38)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.69 → review queue
- **Integrity:** sha `2b44898651d8e405` · dup group `dup_0025` (1)
- **Caption:** That’s not just for feedback, but it’s valuable human preference data.
- **Paragraph after:** That’s not just for feedback, but it’s valuable human preference data. OpenAI uses this to fine-tune their models using preference fine-tuning. In PFT: The user chooses between responses to produce human preference data.
- **OCR:** Which response do you prefer? e Thank you for providing the detailed error message and the atest code. The error appears to be related to how data is handled within the *collate_fn’ function Let's address this by correcting the "collate_fn" to properly handle the data format coming from the "GPT2Dataset Updateto “collate_fn" Function: The function should directly hande the list of tensors received from *GPT2Dataset* without trying to extract “input_ide® and “attention_sask" as if the data were in a dictionary format Remove Diagnostics Prints: The diagnostic print statements within “cellate_fn" are not necessary anymore and can be removed to clean up the function Here's the updated "collate_fn" data) GPT2Toke pad. sequenca( Make sur repiace the existing collate_#n" function in your seript with this updated version. The "pad_sequence” function is used to ensure all sequences in a batch hav

### fig_0028 — LLMs figure

- **Page:** 20 (PDF page 22) · **Chapter:** LLMs
- **BBox:** [121.50, 549.93, 490.50, 683.43] on page 612×792 pt · **Render:** 1025×371 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `c6c5b5b195d932e6` · dup group `dup_0026` (1)
- **Paragraph before:** In PFT: The user chooses between responses to produce human preference data. A reward model is then trained to predict human preference and the LLM is updated using RL.
- **OCR:** User-labeled instruction response pair 3) Preference Fine-tuning Response #1 R e ® el ( ‘ & I response I deepseek _® ® ¢ TInstruction \| fine-tuned LLM \| To RLHF (PPO) \ or -> B e PO Response #2 User »

### fig_0029 — 4) Reasoning fine-tuning

- **Page:** 21 (PDF page 23) · **Chapter:** LLMs
- **BBox:** [126.00, 315.89, 486.00, 441.89] on page 612×792 pt · **Render:** 1000×350 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.88) · LLM Engineering (0.41) · Observability (0.41)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.88 → auto-accept
- **Integrity:** sha `3e0ba0e786ff09df` · dup group `dup_0027` (1)
- **Heading:** 4) Reasoning fine-tuning
- **Caption:** Steps:
- **Paragraph before:** In reasoning tasks (maths, logic, etc.), there's usually just one correct response and a defined series of steps to obtain the answer. So we don’t need human preferences, and we can use correctness as the signal. This is called reasoning fine-tuning
- **Paragraph after:** Steps: ● The model generates an answer to a prompt. ● The answer is compared to the known correct answer.
- **OCR:** 4) Reasoning fine-tuning Reasoning task with a definitive answer Update model QA @ Q‘ @ params to deepseel [ — —» — — > increase the Preference likelihood of fine-tuned LLM higher-reward answers. Reasoning-driven Reward response calculation

### fig_0030 — How do LLMs work?

- **Page:** 22 (PDF page 24) · **Chapter:** LLMs
- **BBox:** [149.62, 208.46, 462.38, 451.46] on page 612×792 pt · **Render:** 869×675 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `9f38d2b57b9c3be7` · dup group `dup_0028` (1)
- **Heading:** How do LLMs work?
- **Caption:** ● Some of them like Tennis
- **Paragraph before:** How do LLMs work? Let’s understand how exactly LLMs work and generate text. Before diving into LLMs, we must understand conditional probability. Let's consider a population of individuals:
- **Paragraph after:** ● Some of them like Tennis ● Some like Football ● A few like both
- **OCR:** A view of the Population! Temis V Temis X Population size = 14 A: An individual loves Tennis B: An individual loves Football P(A)=7/14 P(B)=8/14

### fig_0031 — If the events are A and B, we denote this as P(A\|B).

- **Page:** 23 (PDF page 25) · **Chapter:** LLMs
- **BBox:** [150.00, 67.50, 462.00, 324.75] on page 612×792 pt · **Render:** 867×715 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `01752e43373629d2` · dup group `dup_0029` (1)
- **Caption:** If the events are A and B, we denote this as P(A\|B).
- **Paragraph after:** If the events are A and B, we denote this as P(A\|B). This reads as "probability of A given B" For instance, if we're predicting whether it will rain today (event A), knowing that it's cloudy (event B) might impact our prediction.
- **OCR:** \ Conditional Probability! Population size = 14 Temis Vv Temis X Football X ANB:Loves Tennis & Football A: Loves Tennis B: Loves Football P(ANB)=3/14 P(A)=7/14 P(B)=8/14 PCang) _ (3/14) T ey (/1w =38 Probability of 4 gven B

### fig_0032 — This is a question of conditional probability: given the words that have come

- **Page:** 24 (PDF page 26) · **Chapter:** LLMs
- **BBox:** [150.75, 67.50, 461.25, 299.25] on page 612×792 pt · **Render:** 863×644 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.74) · Context Engineering (0.61)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.74 → review queue
- **Integrity:** sha `6478997a69a90ae5` · dup group `dup_0030` (1)
- **Caption:** This is a question of conditional probability: given the words that have come
- **Paragraph after:** This is a question of conditional probability: given the words that have come before, what is the most likely next word? To predict the next word, the model calculates the conditional probability for each possible next word, given the previous words (context).
- **OCR:** The most likely next word!? — Cafe ——>Hospital The boy went to the — > Playground Previous words (Context) — Park —— School

### fig_0033 — The word with the highest conditional probability is chosen as the prediction.

- **Page:** 24 (PDF page 26) · **Chapter:** LLMs
- **BBox:** [157.88, 403.91, 454.12, 661.91] on page 612×792 pt · **Render:** 823×717 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.87) · Context Engineering (0.48)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.87 → auto-accept
- **Integrity:** sha `4d5aa336e55472c2` · dup group `dup_0031` (1)
- **Caption:** The word with the highest conditional probability is chosen as the prediction.
- **Paragraph before:** This is a question of conditional probability: given the words that have come before, what is the most likely next word? To predict the next word, the model calculates the conditional probability for each possible next word, given the previous words (context).
- **Paragraph after:** The word with the highest conditional probability is chosen as the prediction.
- **OCR:** Next word prediction! vieus words (€ ) Pue s Contidnt Probability distribution The boy went to the over the next word/token —>- Cafe —»- Hospital @——' Playground > park L—>\| 0.3 School Word with the Wighest probability is chosen

### fig_0034 — And the parameters of this distribution are the trained weights!

- **Page:** 25 (PDF page 27) · **Chapter:** LLMs
- **BBox:** [159.75, 117.07, 452.25, 363.07] on page 612×792 pt · **Render:** 813×683 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.72) · Observability (0.63)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.72 → review queue
- **Integrity:** sha `6a5a63b7cf40f1ac` · dup group `dup_0032` (1)
- **Caption:** And the parameters of this distribution are the trained weights!
- **Paragraph before:** The LLM learns a high-dimensional probability distribution over sequences of words.
- **Paragraph after:** And the parameters of this distribution are the trained weights! The training (or rather pre-training) is supervised. But there is a problem! If we always pick the word with the highest probability, we end up with repetitive
- **OCR:** Loss calculation 17 Probability Distribution over next token —b- Cafe ——»[8.88] Hospital s Paysround «——» 5] Loss = -log(P('Playground'/'The boy went to')) = -log(0.4) Cross-entropy loss / Negative log-likelihood

### fig_0035 — This is where temperature comes into the picture.

- **Page:** 26 (PDF page 28) · **Chapter:** LLMs
- **BBox:** [109.50, 67.50, 502.50, 312.00] on page 612×792 pt · **Render:** 1091×679 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.62) · LLM Engineering (0.62) · Agent Protocol Fabric (0.46)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.62 → review queue
- **Integrity:** sha `489d6e866875366b` · dup group `dup_0033` (1)
- **Caption:** This is where temperature comes into the picture.
- **Paragraph after:** This is where temperature comes into the picture. Let's understand what's going on.. To make LLMs more creative, instead of selecting the best token (for simplicity let's think of tokens as words), they "sample" the prediction.
- **OCR:** Lo temperature response = openai_client.chat.completions.create( model = “"gpt-3.5-turl messages = [{“role":"user", “content": “"Continue this: In 2013,..."} Temperature close to zero ) print(response.choices (@] .message,content) the world was captivated by the birth of Prince George, the first child of Prince William and Kate Middleton. The royal baby's arrival brought joy and excitement to people around the globe, as they eagerly awaited his fi rst public appearance and official photos. Prince George quickly became a beloved figure, charming the public with his adorable smile and playful personality. response = openai_client.chat.completions.create( model = “gpt-3.5-turbo", messages = [{"role":"user", "content": “Continue this: In 2013,..." 'dentical Temperature close to zero ; response print(response.choices (8] .message. content) the world was captivated by the birth of Prince Georg

### fig_0036 — So even if “Token 1” has the highest score, it may not be chosen since we are

- **Page:** 26 (PDF page 28) · **Chapter:** LLMs
- **BBox:** [148.12, 426.66, 463.88, 625.41] on page 612×792 pt · **Render:** 877×552 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.81) · Evaluation (0.44) · LLM Engineering (0.40) · Observability (0.40)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.81 → review queue
- **Integrity:** sha `125128a2fb5a0d35` · dup group `dup_0034` (1)
- **Caption:** So even if “Token 1” has the highest score, it may not be chosen since we are
- **Paragraph before:** This is where temperature comes into the picture. Let's understand what's going on.. To make LLMs more creative, instead of selecting the best token (for simplicity let's think of tokens as words), they "sample" the prediction.
- **Paragraph after:** So even if “Token 1” has the highest score, it may not be chosen since we are sampling.
- **OCR:** Sampling instead of selecting the highest! output layer logits softmax oy Token 1 O 10.2 \| —» \| 0.86 \ Token 2 O -5.6 \| —» \| 0.00 'r?::“ : O Dl—\| /a.trnmun Token N O 8.01 \| —» \| 0.10

### fig_0037 — Let's take a code example!

- **Page:** 27 (PDF page 29) · **Chapter:** LLMs
- **BBox:** [177.38, 117.07, 434.62, 258.82] on page 612×792 pt · **Render:** 715×393 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.68) · LLM Engineering (0.59) · Tool / Action Fabric (0.43)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.68 → review queue
- **Integrity:** sha `c15588506f317422` · dup group `dup_0035` (1)
- **Caption:** Let's take a code example!
- **Paragraph before:** Now, temperature introduces the following tweak in the softmax function, which, in turn, influences the sampling process:
- **Paragraph after:** Let's take a code example! ● At low temperature, probabilities concentrate around the most likely token, resulting in nearly greedy generation.
- **OCR:** / o é@ er Temperature- Traditional softmax ; z; adjusted E eD softmax T'-nnmn/

### fig_0038 — ●

- **Page:** 27 (PDF page 29) · **Chapter:** LLMs
- **BBox:** [151.88, 294.13, 460.12, 611.38] on page 612×792 pt · **Render:** 857×881 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.64) · LLM Engineering (0.64) · Tool / Action Fabric (0.42)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.64 → review queue
- **Integrity:** sha `0b2a7792541e6b75` · dup group `dup_0036` (1)
- **Caption:** ●
- **Paragraph before:** Now, temperature introduces the following tweak in the softmax function, which, in turn, influences the sampling process: Let's take a code example!
- **Paragraph after:** ● At low temperature, probabilities concentrate around the most likely token, resulting in nearly greedy generation. ● At high temperature, probabilities become more uniform, producing
- **OCR:** 0.01 np. array ([1,2,3,4) >> softmax (a) array (10.03, 0.09, 0.24, 0.64) >> softmax (a/T) array ([5.12e-131, 1.38e-087, 3.72e-044, 1.00e+000]) (X X J High temperature 10000000000 np. array ([1,2,3,4) >> softmax (a) array (10.03, 0.09, 0.24, 0.64) >> softmax (a/T) array ([0.25, 0.25, 0.25, 0.25])

### fig_0039 — LLM Generation Parameters

- **Page:** 28 (PDF page 30) · **Chapter:** LLMs
- **BBox:** [151.50, 266.04, 460.50, 670.29] on page 612×792 pt · **Render:** 859×1122 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.95) · RAG / Knowledge Engineering (0.40)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.95 → auto-accept
- **Integrity:** sha `79f1be9fe7252ea6` · dup group `dup_0037` (1)
- **Heading:** LLM Generation Parameters
- **Caption:** 1) Max tokens
- **Paragraph before:** Every generation from an LLM is shaped by parameters under the hood. Knowing how to tune is important so that you can produce sharp and more controlled outputs. Here are the levers that matter most:
- **Paragraph after:** 1) Max tokens
- **OCR:** l? LLM Generation parameters mep dailydoseofds.com The sun sets, painting the sky =~ Mex =15 — in fiery hues of Upper limit for the number of tokens the 4 4 7 4 J o as gambling. Max tokens @q Al model generates L —d e whispers through 764" €97 Value Range = 1 to infinity the trees. ( W Controls randomness in 5, \| nll output. A higher temprature Tomparatare alllla makes more creative ) and diverse. o Value Range = 0 to 2 um (common range) Controls probability distribution is Top_p — considered when i sampling tokens L i Top_p = 10% Value Range = 0 to 1 - Limits the number of ) top probable tokens to Jop_k 1 sample from o) Value Range = 1 to infinity \_ um top_k =2 Dok Penalizes token repetation Frequency play and run based on frequency. penalty and chase Positive values reduce ::: ::: repetition N o i Value Range = -2 to 2 P — Puppies nap. Encourages the model Presence = to use new tokens

### fig_0040 — This is a hard cap on how many tokens the model can generate in one response.

- **Page:** 29 (PDF page 31) · **Chapter:** LLMs
- **BBox:** [103.88, 67.50, 508.12, 147.00] on page 612×792 pt · **Render:** 1123×221 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.86) · LLM Engineering (0.49)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.86 → auto-accept
- **Integrity:** sha `fedb794a478d07b3` · dup group `dup_0038` (1)
- **Caption:** This is a hard cap on how many tokens the model can generate in one response.
- **Paragraph after:** This is a hard cap on how many tokens the model can generate in one response. Too low → truncated outputs; too high → could lead to wasted compute. 2) Temperature Governs randomness. Low temperature (~0) makes the model deterministic.
- **OCR:** Upper limit for the O number of tokens the model generates Token count \/5(ye Range = 1 to infinity

### fig_0041 — 2) Temperature

- **Page:** 29 (PDF page 31) · **Chapter:** LLMs
- **BBox:** [109.50, 242.19, 502.50, 326.19] on page 612×792 pt · **Render:** 1091×234 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.74) · AI / ML Foundation (0.61)
- **Primary branch:** llm-engineering · **Confidence:** 0.74 → review queue
- **Integrity:** sha `f42714fbc4f05a9c` · dup group `dup_0039` (1)
- **Heading:** 2) Temperature
- **Caption:** Governs randomness. Low temperature (~0) makes the model deterministic.
- **Paragraph before:** This is a hard cap on how many tokens the model can generate in one response. Too low → truncated outputs; too high → could lead to wasted compute. 2) Temperature
- **Paragraph after:** Governs randomness. Low temperature (~0) makes the model deterministic. Higher temperature (0.7–1.0) boosts creativity, diversity, but also noise. Use case: lower for QA/chatbots, higher for brainstorming/creative tasks. 3) Top-k
- **OCR:** Controls randomness in 1 output. A higher temprature Qillo makes more creative Temperature TS i i i g and diverse. \| Value Range = 0 to 2 n o et Mol (common range)

### fig_0042 — 3) Top-k

- **Page:** 29 (PDF page 31) · **Chapter:** LLMs
- **BBox:** [113.25, 451.17, 498.75, 535.17] on page 612×792 pt · **Render:** 1071×233 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.89) · LLM Engineering (0.46)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.89 → auto-accept
- **Integrity:** sha `978380b514159215` · dup group `dup_0040` (1)
- **Heading:** 3) Top-k
- **Caption:** The default way to generate the next token is to sample from all tokens,
- **Paragraph before:** Governs randomness. Low temperature (~0) makes the model deterministic. Higher temperature (0.7–1.0) boosts creativity, diversity, but also noise. Use case: lower for QA/chatbots, higher for brainstorming/creative tasks. 3) Top-k
- **Paragraph after:** The default way to generate the next token is to sample from all tokens, proportional to their probability. This parameter restricts sampling to the top k most probable tokens. Example: k=5 → model only considers most likely next tokens during sampling.
- **OCR:** P Limits the number of [ top probable tokens to Top_k sample from Value Range = 1 to infinity um top_k =2

### fig_0043 — Instead of picking from all tokens or top k tokens, model samples from a

- **Page:** 30 (PDF page 32) · **Chapter:** LLMs
- **BBox:** [111.38, 67.50, 500.62, 152.25] on page 612×792 pt · **Render:** 1081×235 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `4422a6b2d57313a3` · dup group `dup_0041` (1)
- **Caption:** Instead of picking from all tokens or top k tokens, model samples from a
- **Paragraph after:** Instead of picking from all tokens or top k tokens, model samples from a probability mass up to p. Example: top_p=0.9 → only the smallest set of tokens covering 90% probability are considered.
- **OCR:** top_p = 10% Controls probability distribution is considered when sampling tokens Value Range = O to 1

### fig_0044 — 5) Frequency penalty

- **Page:** 30 (PDF page 32) · **Chapter:** LLMs
- **BBox:** [106.88, 316.80, 505.12, 394.80] on page 612×792 pt · **Render:** 1107×216 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.92) · RAG / Knowledge Engineering (0.43)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.92 → auto-accept
- **Integrity:** sha `ca1c44e8a056c15d` · dup group `dup_0042` (1)
- **Heading:** 5) Frequency penalty
- **Caption:** Reduces likelihood of reusing tokens that have already appeared frequently.
- **Paragraph before:** Example: top_p=0.9 → only the smallest set of tokens covering 90% probability are considered. More adaptive than top_k, useful when balancing coherence with diversity. 5) Frequency penalty
- **Paragraph after:** Reduces likelihood of reusing tokens that have already appeared frequently. Positive values discourage repetition, negative values exaggerate it. Useful for summarization (avoid redundancy) or poetry (intentional repetition). 6) Presence penalty
- **OCR:** Penalizes token repetation Frequency based on frequency. penalty Positive values reduce a repetition Value Range = -2 to 2

### fig_0045 — 6) Presence penalty

- **Page:** 30 (PDF page 32) · **Chapter:** LLMs
- **BBox:** [105.00, 519.78, 507.00, 598.53] on page 612×792 pt · **Render:** 1117×219 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.78) · RAG / Knowledge Engineering (0.57)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.78 → review queue
- **Integrity:** sha `2ca0b0548ea0642b` · dup group `dup_0043` (1)
- **Heading:** 6) Presence penalty
- **Caption:** Encourages the model to bring in new tokens not yet seen in the text.
- **Paragraph before:** Reduces likelihood of reusing tokens that have already appeared frequently. Positive values discourage repetition, negative values exaggerate it. Useful for summarization (avoid redundancy) or poetry (intentional repetition). 6) Presence penalty
- **Paragraph after:** Encourages the model to bring in new tokens not yet seen in the text. Higher values push for novelty, lower values make the model stick to known patterns. Handy for exploratory generation where diversity of ideas is valued.
- **OCR:** 0 Encourages the model Presence @ - . to use new tokens that penalty haven't been generated Value Range = -2 to 2

### fig_0046 — 7) Stop sequences

- **Page:** 31 (PDF page 33) · **Chapter:** LLMs
- **BBox:** [99.75, 97.60, 512.25, 177.85] on page 612×792 pt · **Render:** 1145×223 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.80) · LLM Engineering (0.48) · Agentic AI (0.41)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.80 → review queue
- **Integrity:** sha `772658ddadac0043` · dup group `dup_0044` (1)
- **Heading:** 7) Stop sequences
- **Caption:** Custom list of tokens that immediately halt generation.
- **Paragraph before:** 7) Stop sequences
- **Paragraph after:** Custom list of tokens that immediately halt generation. Critical in structured outputs (e.g., JSON), preventing spillover text. Lets you enforce strict response boundaries without heavy prompt engineering. Bonus: min-p sampling
- **OCR:** A list of tokens where the model will stop generating further tokens Value Range = Custom list

### fig_0047 — Strategies

- **Page:** 32 (PDF page 34) · **Chapter:** LLMs
- **BBox:** [98.25, 319.43, 513.75, 645.68] on page 612×792 pt · **Render:** 1155×906 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.84) · Agent Protocol Fabric (0.43) · Evaluation (0.43)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.84 → review queue
- **Integrity:** sha `850f90241e390009` · dup group `dup_0045` (1)
- **Heading:** Strategies
- **Caption:** Approach 1: Greedy strategy
- **Paragraph before:** But here’s the catch: predicting probabilities is not enough. We still need a strategy to pick which token to use at each step. And different strategies lead to very different styles of output. Here are the most common strategies for text generation:
- **Paragraph after:** Approach 1: Greedy strategy
- **OCR:** Choose the token with highest probability Greedy Strategy \|4 LLM Text Generation Strategies Vocabulary size ¢ mcp.DailyDoseofDS.com « > 020205 01,04 01 0804 0306 ===~ > ArgMax \|----> ‘you’ my get set not super him at you is feel Probabilities Sampling tokens by using the probability Multinomial Vocabulary size —_— 0.051‘0.0% 01007 01 0.07C 1016@ 012 my get set not super him ot you is * 014 chance to be ‘at’ * 016 chance to be ‘you' * 012 :bmnu to be ‘feel’ fea( Maximize Beam probability Search of the whole sequence Penalize repetitiveness Second iteration First iteration HIT] — Beam Width m Third iteration B wsﬁkuﬂm;whh-&gwh!«t \| L top- - kckens Third iteration Test candidates and keep only the best ones set feel ~mos{cos(him at)cos(himyou)) -max(cos(at,ot) cos(atyow)) ~max(cos(setat)cos(setyou)) ~ma(cos(fealat Nth iteration — e — — ellyos)) penalty

### fig_0048 — Approach 2: Multinomial sampling strategy

- **Page:** 33 (PDF page 35) · **Chapter:** LLMs
- **BBox:** [111.38, 216.53, 500.62, 379.28] on page 612×792 pt · **Render:** 1081×452 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.76) · LLM Engineering (0.47) · RAG / Knowledge Engineering (0.41) · Observability (0.41)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.76 → review queue
- **Integrity:** sha `cf3ba0fd41260452` · dup group `dup_0046` (1)
- **Heading:** Approach 2: Multinomial sampling strategy
- **Caption:** The temperature parameter controls the randomness in the generation (covered
- **Paragraph before:** repetitive sentences. Approach 2: Multinomial sampling strategy Instead of always picking the top token, we can sample from the probability distribution available in the probability vector.
- **Paragraph after:** The temperature parameter controls the randomness in the generation (covered in detail here). Approach 3: Beam search Both approach and approach have a problem. They only focus on the most
- **OCR:** output layer logits softmax Token 1 (:) Token 2 (:) Token N C:) ‘\\\\\\\ Sample from this ‘//////’distribution

### fig_0049 — Approach 3: Beam search

- **Page:** 33 (PDF page 35) · **Chapter:** LLMs
- **BBox:** [138.38, 533.83, 473.62, 593.08] on page 612×792 pt · **Render:** 931×165 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.76) · LLM Engineering (0.51) · Data Engineering (0.43)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.76 → review queue
- **Integrity:** sha `0add5be3e550d975` · dup group `dup_0047` (1)
- **Heading:** Approach 3: Beam search
- **Caption:** To maximize this product, you’d need to know future conditionals (what comes
- **Paragraph before:** Approach 3: Beam search Both approach and approach have a problem. They only focus on the most immediate token to be generated. Ideally, we care about maximizing the probability of the whole sequence, not just the next token.
- **Paragraph after:** To maximize this product, you’d need to know future conditionals (what comes after each candidate). But when decoding, we only know probabilities for the next step, not the downstream continuation.
- **OCR:** ,’:12 P(ty,ts,...,tn \| Prompt) = \| \| P(¢; \| Prompt, ty,...,t1) T il

### fig_0050 — At each step, it expands the top k partial sequences (the beam).

- **Page:** 34 (PDF page 36) · **Chapter:** LLMs
- **BBox:** [102.00, 97.29, 510.00, 187.29] on page 612×792 pt · **Render:** 1133×250 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.87) · Evaluation (0.48)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.87 → auto-accept
- **Integrity:** sha `b9f88328e02e5f05` · dup group `dup_0048` (1)
- **Caption:** At each step, it expands the top k partial sequences (the beam).
- **Paragraph before:** Beam search tries to approximate the true global maximization:
- **Paragraph after:** At each step, it expands the top k partial sequences (the beam). Some beams may have started with less probable tokens initially, but lead to much higher-probability completions. By keeping alternatives alive, beam search explores more of the probability tree.
- **OCR:** Second iteration Third iteration Nth iteration Maximize [WTTT] probability First v‘itlmtion ; of the whole ! 2 sequence Beam s Width I [l Test candidates and keep only the best ones

### fig_0051 — Approach 4: Contrastive search

- **Page:** 34 (PDF page 36) · **Chapter:** LLMs
- **BBox:** [96.00, 381.62, 516.00, 475.37] on page 612×792 pt · **Render:** 1167×260 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.89) · Agent Protocol Fabric (0.46)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.89 → auto-accept
- **Integrity:** sha `0189b6fccadf7f9d` · dup group `dup_0049` (1)
- **Heading:** Approach 4: Contrastive search
- **Caption:** This is a newer method that balances fluency with diversity.
- **Paragraph before:** By keeping alternatives alive, beam search explores more of the probability tree. This is widely used in tasks like machine translation, where correctness matters more than creativity. Approach 4: Contrastive search
- **Paragraph after:** This is a newer method that balances fluency with diversity. Essentially, it penalizes repetitive continuations by checking how similar a candidate token is to what’s already been generated to have more diversity in the output.
- **OCR:** him -max(cos(him,at) cos (himgou) Third iteration o T -max(cos(at,at) cos(atiyou Penalize E » k" ¥ — repetitiveness sat -max(cos(set,at)cos(set gou)) P OHE tokens fael -max(cos(feelat) cos(fellyou))

### fig_0052 — Bonus: SLED - Self-Logits Evolution Decoding

- **Page:** 35 (PDF page 37) · **Chapter:** LLMs
- **BBox:** [94.88, 236.32, 517.12, 606.07] on page 612×792 pt · **Render:** 1173×1027 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Observability (0.73) · AI / ML Foundation (0.57) · Agent Protocol Fabric (0.40)
- **Primary branch:** observability · **Confidence:** 0.73 → review queue
- **Integrity:** sha `f9450ce89cc8c998` · dup group `dup_0050` (1)
- **Heading:** Bonus: SLED - Self-Logits Evolution Decoding
- **Caption:** SLED introduces a small but meaningful change: instead of using only the final
- **Paragraph before:** All the decoding strategies above rely on the logits produced by the final layer, which is how Transformers normally generate text. The issue is that factual signals present in earlier layers can fade as the model goes deeper, leading the final layer to favor fluent but occasionally inaccurate outputs.
- **Paragraph after:** SLED introduces a small but meaningful change: instead of using only the final layer’s logits, it looks at how logits evolve across all layers. Each layer contributes its own prediction, and SLED measures how closely these predictions agree. It then nudges the final logits toward this layer-wise consensus before selecting the
- **OCR:** mcp.DailyDoseofDS.com B Self Logits Evolution Decoding 'Tvansform vs. Logits —» Prediction (NDth lager (N-1)th lager Final layer

### fig_0053 — Using Another LLM

- **Page:** 36 (PDF page 38) · **Chapter:** LLMs
- **BBox:** [138.38, 355.21, 473.62, 713.71] on page 612×792 pt · **Render:** 931×996 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.93) · Business Automation (0.42)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.93 → auto-accept
- **Integrity:** sha `fbbc9386a2d2b44b` · dup group `dup_0051` (1)
- **Heading:** Using Another LLM
- **Paragraph before:** LLMs don't just learn from raw text; they also learn from each other: ● Llama Scout and Maverick were trained using Llama Behemoth. ● Gemma and were trained using Google's proprietary Gemini. Distillation helps us do so, and the visual below depicts three popular techniques.
- **OCR:** '3 Techniques to Train an LLM using Another LLM Soft-label distillation 9 TInput corpus, Softmax probabilities over entire vocab ol th e Student to match Teacher's probabilities RN o %}oinbnl&bmums;am Predicted one-hot token Tnput corpus, Teacher's probabilities 1 1 Hard-label @ ! distillation [ g : 53 7 @ I mputeops ' _ (oo o e \| 0= 0 Student LLM kel (e} e 2¢) 0 . \|etce e @ o \| 2 0 0 il 1 e 1 ) Co- @1 ‘(lnahtr?LM (m.ﬁ fresh) a r [-L \| = - 1 distillation 1 (3)Troin Student to match \| 1 1

### fig_0054 — 1) Soft-label distillation

- **Page:** 37 (PDF page 39) · **Chapter:** LLMs
- **BBox:** [115.50, 436.60, 496.50, 571.60] on page 612×792 pt · **Render:** 1059×375 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `9cf94b48235c5675` · dup group `dup_0052` (1)
- **Heading:** 1) Soft-label distillation
- **Caption:** ● Use a fixed pre-trained Teacher LLM to generate softmax probabilities
- **Paragraph before:** 3.1 models. You can also apply distillation during both stages, which Gemma did. Here are the three commonly used distillation techniques: 1) Soft-label distillation
- **Paragraph after:** ● Use a fixed pre-trained Teacher LLM to generate softmax probabilities over the entire corpus. ● Pass this data through the untrained Student LLM as well to get its
- **OCR:** Softmax probabilities over entire vocab o o 2B e i g2 = ey all@ _‘H Pre-trained Teacher LLM Soft-label @ distillation T Input corpus @ Train Student to match Teacher's probabilities ) i 1 } \| 1 } 1 }

### fig_0055 — 2) Hard-label distillation

- **Page:** 38 (PDF page 40) · **Chapter:** LLMs
- **BBox:** [106.12, 369.46, 505.88, 511.21] on page 612×792 pt · **Render:** 1111×394 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.87) · Agent Memory (0.41) · Data Engineering (0.41)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.87 → auto-accept
- **Integrity:** sha `b1827a1efa4f7af5` · dup group `dup_0053` (1)
- **Heading:** 2) Hard-label distillation
- **Caption:** ● Use a fixed pre-trained Teacher LLM to just get the final one-hot output
- **Paragraph before:** vocabulary, you would need million GBs of memory to store soft labels under float8 precision. The second technique solves this. 2) Hard-label distillation
- **Paragraph after:** ● Use a fixed pre-trained Teacher LLM to just get the final one-hot output token. ● Use the untrained Student LLM to get the softmax probabilities from the
- **OCR:** Hard-label distillation Input corpus - —0 Student LLM Predicted one-hot token ®Tmin Student to imitate Teacher's final output 1 I \| I \| I I

### fig_0056 — ● Start with an untrained Teacher LLM and an untrained Student LLM.

- **Page:** 39 (PDF page 41) · **Chapter:** LLMs
- **BBox:** [103.12, 67.50, 508.88, 210.75] on page 612×792 pt · **Render:** 1127×398 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `b2374f3fbcd14370` · dup group `dup_0054` (1)
- **Caption:** ● Start with an untrained Teacher LLM and an untrained Student LLM.
- **Paragraph after:** ● Start with an untrained Teacher LLM and an untrained Student LLM. ● Generate softmax probabilities over the current batch from both models. ●
- **OCR:** Co- distillation Input corpus Student LLM o — © o =79 ° 7 @S <0504 0 LRk O LS eeCS S0 ) Teacher LLM (started fresh) = o e 02 <O @« >® O 0 o ® '® Softmax probabilities over entire vocab Train Student to match Teacher's probabilities 1 1 \| 1 1 1 1

### fig_0057 — To get started, install Ollama with a single command:

- **Page:** 40 (PDF page 42) · **Chapter:** LLMs
- **BBox:** [154.50, 67.50, 457.50, 198.75] on page 612×792 pt · **Render:** 841×365 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.84) · Business Automation (0.51)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.84 → review queue
- **Integrity:** sha `f2f2aab6297c1f23` · dup group `dup_0055` (1)
- **Caption:** To get started, install Ollama with a single command:
- **Paragraph after:** To get started, install Ollama with a single command: Done! Now, you can download any of the supported models using these commands: For programmatic usage, you can also install the Python package of Ollama or its
- **OCR:** [ X J Command line ollama run deepseek-rl

### fig_0058 — Done!

- **Page:** 40 (PDF page 42) · **Chapter:** LLMs
- **BBox:** [126.38, 238.05, 485.62, 348.30] on page 612×792 pt · **Render:** 997×306 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.63) · Agent Orchestration (0.54) · RAG / Knowledge Engineering (0.44) · Multi-Agent (0.44)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.63 → review queue
- **Integrity:** sha `2c6aac39923bb9cf` · dup group `dup_0056` (1)
- **Caption:** Done!
- **Paragraph before:** To get started, install Ollama with a single command:
- **Paragraph after:** Done! Now, you can download any of the supported models using these commands: For programmatic usage, you can also install the Python package of Ollama or its integration with orchestration frameworks like Llama Index or CrewAI:
- **OCR:** L X ] Command line curl -fsSL https:// ollama. com/install .sh \| sh

### fig_0059 — For programmatic usage, you can also install the Python package of Ollama or its

- **Page:** 40 (PDF page 42) · **Chapter:** LLMs
- **BBox:** [108.38, 419.40, 503.62, 615.15] on page 612×792 pt · **Render:** 1097×543 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.63) · Agent Orchestration (0.54) · RAG / Knowledge Engineering (0.44) · Multi-Agent (0.44)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.63 → review queue
- **Integrity:** sha `9cced270a025e03f` · dup group `dup_0057` (1)
- **Caption:** For programmatic usage, you can also install the Python package of Ollama or its
- **Paragraph before:** To get started, install Ollama with a single command: Done! Now, you can download any of the supported models using these commands:
- **Paragraph after:** For programmatic usage, you can also install the Python package of Ollama or its integration with orchestration frameworks like Llama Index or CrewAI:
- **OCR:** [ X ] Command line ollama run deepseek-rl [ X ] Command line ollama pull deepseek-ril Downloads and runs it in the terminal right away Downloads the model

### fig_0060 — 2) LMStudio

- **Page:** 41 (PDF page 43) · **Chapter:** LLMs
- **BBox:** [124.50, 67.50, 487.50, 207.00] on page 612×792 pt · **Render:** 1009×388 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.74) · RAG / Knowledge Engineering (0.48) · Observability (0.48)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.74 → review queue
- **Integrity:** sha `0e974d3de6929426` · dup group `dup_0058` (1)
- **Caption:** 2) LMStudio
- **Paragraph after:** 2) LMStudio LMStudio can be installed as an app on your computer. The app does not collect data or monitor your actions. Your data stays local on your machine. It’s free for personal use.
- **OCR:** [ X J Command line .o. pip install ollama pip install 1llama-index-1lms-ollama

### fig_0061 — 4) LlamaCPP

- **Page:** 42 (PDF page 44) · **Chapter:** LLMs
- **BBox:** [142.50, 67.50, 469.50, 415.50] on page 612×792 pt · **Render:** 909×967 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.76) · AI / ML Foundation (0.51) · Infrastructure (0.43)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.76 → review queue
- **Integrity:** sha `c8ccb1a68f448573` · dup group `dup_0059` (1)
- **Caption:** 4) LlamaCPP
- **Paragraph after:** 4) LlamaCPP LlamaCPP enables LLM inference with minimal setup and good performance.
- **OCR:** pip install vilm vllm serve deepseek-ai/DeepSeek-R1-Distill-Quen-1.58 \ --enable-reasoning --reasoning-parser deepseek_rl from openai import OpenAT # dify OpenAI API key and API base to use openai_api_key = "EMPTY" openai_api_base = "http://localhost:8000/v1" client = OpenAI( api_key=openai_api_key, base_url=openai_api_base, models = client.models.list() model = models.data[e].id # Round 1 messages = [{"role": "user", "content": "9.11 and 9.8, which is greater?"}] response = client.chat.completions.create(model=model, messages=messages) reasoning_content = response.choices[0].message.reasoning_content content = response.choices[@].message.content print("reasoning_content:", reasoning_content) print("content:", content)

### fig_0062 — 4) LlamaCPP

- **Page:** 42 (PDF page 44) · **Chapter:** LLMs
- **BBox:** [148.88, 486.91, 463.12, 708.16] on page 612×792 pt · **Render:** 873×615 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.68) · Infrastructure (0.57) · Agent Protocol Fabric (0.46)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.68 → review queue
- **Integrity:** sha `c93d7f31535749bc` · dup group `dup_0060` (1)
- **Heading:** 4) LlamaCPP
- **Paragraph before:** 4) LlamaCPP LlamaCPP enables LLM inference with minimal setup and good performance.
- **OCR:** brew install llama. cpp sudo sysctl iogpu.wired_limit_mb=180000 lama-server -c 8192 -ub 64 \ —-model-url https://huggingface.co/unsloth/DeepSeek-R1- GGUF/resolve/main/DeepSeek-R1-UD-IQ1_S/DeepSeek-R1-UD-IQ1_S-00001- 0f-00003. gguf

### fig_0063 — Let's dive in to learn more about MoE!

- **Page:** 44 (PDF page 46) · **Chapter:** LLMs
- **BBox:** [126.00, 67.50, 486.00, 432.00] on page 612×792 pt · **Render:** 1000×1013 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `cfb3dde0e0873993` · dup group `dup_0061` (2)
- **Caption:** Let's dive in to learn more about MoE!
- **Paragraph after:** Let's dive in to learn more about MoE! Transformer and MoE differ in the decoder block:
- **OCR:** l Transformer vs. Mixture of Experts [ iein baiyoseofs.com Transformer Inputs Mixture of Experts Inputs B Bl “'lTJ" ._l_'_\|T\| ® ©® © o ® ® © Positional embedding Positional embedding \| T T T T ____._J__I__L____I ““““ ! Decoder Layer norm block ~ Masked self-attention Feed Q& 4888 Dﬁ,o forward network T T T T e i i o i \| Ty J Decoder \| Layer norm block 1 - ! Masked self-attention \| e e R Lager norm Selacted expent EI‘I@ »)@(____ v v EE E-E

### fig_0064 — LLMs figure

- **Page:** 44 (PDF page 46) · **Chapter:** LLMs
- **BBox:** [155.25, 503.09, 456.75, 697.34] on page 612×792 pt · **Render:** 837×540 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `b0a09f1308737dd5` · dup group `dup_0062` (1)
- **Paragraph before:** Let's dive in to learn more about MoE! Transformer and MoE differ in the decoder block:
- **OCR:** Transformer Decoder Block MoE Decoder Block Layer norm 1 Masked self-attention Loyer norm Masked self-attention

### fig_0065 — ●

- **Page:** 45 (PDF page 47) · **Chapter:** LLMs
- **BBox:** [152.25, 222.22, 459.75, 465.22] on page 612×792 pt · **Render:** 855×675 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.94) · Agent Protocol Fabric (0.41)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.94 → auto-accept
- **Integrity:** sha `3d8fccc39e51081f` · dup group `dup_0063` (1)
- **Caption:** ●
- **Paragraph before:** to that in Transformer. During inference, a subset of experts are selected. This makes inference faster in MoE. Also, since the network has multiple decoder layers:
- **Paragraph after:** ● the text passes through different experts across layers. ● the chosen experts also differ between tokens.
- **OCR:** Decoder [ Expert ‘ Expert-2 ’ [ Expert-3 ’ ‘ Expert-4 ] layer 1 [ Decoder Expert-1 Expert-2 Expert-3 Expert-4 layer 2 ) D Ecoder Expert-1 Expert-2 Expert-3 Expert-4 layer N ¢ next hidden state

### fig_0066 — But it isn't straightforward.

- **Page:** 46 (PDF page 48) · **Chapter:** LLMs
- **BBox:** [171.00, 67.50, 441.00, 234.75] on page 612×792 pt · **Render:** 750×465 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.84) · Evaluation (0.51)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.84 → review queue
- **Integrity:** sha `cf90879c191283d1` · dup group `dup_0064` (1)
- **Caption:** But it isn't straightforward.
- **Paragraph after:** But it isn't straightforward. There are challenges. Challenge 1) Notice this pattern at the start of training: ● The model selects "Expert 2" (randomly since all experts are similar).
- **OCR:** b 55 Router Softmax softmax scores over experts selected expert ) ( Expert-1 Expert-2 Expert-3 Expert-4

### fig_0067 — ● The model selects "Expert 2" (randomly since all experts are similar).

- **Page:** 46 (PDF page 48) · **Chapter:** LLMs
- **BBox:** [105.00, 337.62, 507.00, 510.12] on page 612×792 pt · **Render:** 1117×480 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `d2e790b738852ec1` · dup group `dup_0065` (1)
- **Caption:** ● The model selects "Expert 2" (randomly since all experts are similar).
- **Paragraph before:** But it isn't straightforward. There are challenges. Challenge 1) Notice this pattern at the start of training:
- **Paragraph after:** ● The model selects "Expert 2" (randomly since all experts are similar). ● The selected expert gets a bit better. ● It may get selected again since it’s the best.
- **OCR:** Tteration #1 Tteration #2 Tteration #3 -= - , - - A 4 Expert-1 Expert2 [ \| Expert-3 ‘ Expert-1 I ‘ Expert2 \| \| Expert-3 I Expert-1 ‘ Expert-2 ‘ Expert-3 ‘ pre=me S Ay S Y T T g — v v \ 4 ‘ Expert-] \| Expert-2 \| \| Expert-3 ‘ ‘ Expert1 \| ‘ Expert-2 \| \| Expert3 \| { Expert1 \| Expert2 [ \| Expert3 ‘ e = e Expert-] Expert2 \| Expert-3 ‘ Expert-] \| Expert2 \| ( e,q,ma] Expert1 Expert-2 ‘ ‘ Expert3 } T U U v ¥ ______________________________________________ > Same experts are getting selected repeatedly as they are getting more training

### fig_0068 — ●

- **Page:** 47 (PDF page 49) · **Chapter:** LLMs
- **BBox:** [117.75, 99.29, 494.25, 274.79] on page 612×792 pt · **Render:** 1045×488 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.68) · Evaluation (0.57) · Observability (0.46)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.68 → review queue
- **Integrity:** sha `5d557aa3c4d6c1b8` · dup group `dup_0066` (1)
- **Caption:** ●
- **Paragraph before:** We solve this in two steps:
- **Paragraph after:** ● Add noise to the feed-forward output of the router so that other experts can get higher logits. ●
- **OCR:** [eYeXe) ar Router SoftMax softmax scores over experts select_ed expert [ A 4 LFEN 6 0000 ooo Router < \| Softmax \| \| 5 . @ Gawussian noise v softmax scores over experts \| \| selected expert \| \| Expert-1 l ‘ Expert-2 ’ [ Expert-3 l ‘ Expert-1 ’ ‘ Expert-2 ’ I Expert-3 ‘

### fig_0069 — What is Prompt Engineering?

- **Page:** 49 (PDF page 51) · **Chapter:** Prompt Engineering
- **BBox:** [125.25, 167.25, 486.75, 293.25] on page 612×792 pt · **Render:** 1005×350 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.98)
- **Primary branch:** llm-engineering · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `6ef38a7e98a31717` · dup group `dup_0067` (1)
- **Heading:** What is Prompt Engineering?
- **Caption:** Think of it as the steering wheel for the LLM.
- **Paragraph before:** What is Prompt Engineering? LLMs are powerful, but they don’t automatically know what you want. Prompt engineering is the simplest way to control them.
- **Paragraph after:** Think of it as the steering wheel for the LLM. Small adjustments completely shift the direction of the output. You’re not changing weights (the learned parameters inside the model). You’re changing instructions and that changes everything.
- **OCR:** Think step-by-step Follow constraints Avoid shallow answers

### fig_0070 — reasoning in LLMs

- **Page:** 50 (PDF page 52) · **Chapter:** Prompt Engineering
- **BBox:** [122.25, 338.36, 489.75, 719.36] on page 612×792 pt · **Render:** 1021×1059 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.92) · Observability (0.43)
- **Primary branch:** llm-engineering · **Confidence:** 0.92 → auto-accept
- **Integrity:** sha `8052ba70b3597f4b` · dup group `dup_0068` (1)
- **Heading:** reasoning in LLMs
- **Paragraph before:** complex reasoning tasks like math, logic, or multi-step problems. Let’s look at three popular prompting techniques that help LLMs think more clearly before they answer. These are depicted below:
- **OCR:** '3 Prompting Techniques for Reasoning in LLMs Chain of Thought (CoT) Step1\| — > \|step2 LLM Reasoning ek & doapseoic Step N Majority LLM Reasoning & doapsack Step1\| — > \|step2 —= > [stepn Output 1 >3- LM Reasoning & % LA osck Voting uerst sp1] — > [sp2) — > [stn over Col ' U \| ser - UM Reasoning & stept\| — > [step2] — > [stepn \ p- -> 1 doopsacic ! LM Reasoning ! 1 i Sips Tree of \| ! Thought \| User i ! \| -t > ~> 1 ? i Final wm Ee;'sonmg : LLM Reasoning it dseposcic \| docpsecic ~> g =4

### fig_0071 — 1) Chain of Thought (CoT)

- **Page:** 51 (PDF page 53) · **Chapter:** Prompt Engineering
- **BBox:** [101.62, 182.96, 510.38, 274.46] on page 612×792 pt · **Render:** 1135×254 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.75) · Evaluation (0.45) · Observability (0.45) · RAG / Knowledge Engineering (0.40)
- **Primary branch:** llm-engineering · **Confidence:** 0.75 → review queue
- **Integrity:** sha `cad6d321c85d125a` · dup group `dup_0069` (1)
- **Heading:** 1) Chain of Thought (CoT)
- **Caption:** This often improves accuracy because the model can walk through its logic
- **Paragraph before:** 1) Chain of Thought (CoT) The simplest and most widely used technique. Instead of asking the LLM to jump straight to the answer, we nudge it to reason step by step.
- **Paragraph after:** This often improves accuracy because the model can walk through its logic before committing to a final output. For instance: It’s a simple example but this tiny nudge can unlock reasoning capabilities that
- **OCR:** Chain of w° Thought (CoT) LLM Reasoning & ] \| A Query “;supv\ — > [step2] - > [stepn] ___) User

### fig_0072 — 1) Chain of Thought (CoT)

- **Page:** 51 (PDF page 53) · **Chapter:** Prompt Engineering
- **BBox:** [94.12, 365.34, 517.88, 430.59] on page 612×792 pt · **Render:** 1177×182 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.87) · Evaluation (0.41) · Observability (0.41)
- **Primary branch:** llm-engineering · **Confidence:** 0.87 → auto-accept
- **Integrity:** sha `1385e29b8e981320` · dup group `dup_0070` (1)
- **Heading:** 1) Chain of Thought (CoT)
- **Caption:** It’s a simple example but this tiny nudge can unlock reasoning capabilities that
- **Paragraph before:** step by step. This often improves accuracy because the model can walk through its logic before committing to a final output. For instance:
- **Paragraph after:** It’s a simple example but this tiny nudge can unlock reasoning capabilities that standard zero-shot prompting could miss. 2) Self-Consistency (a.k.a. Majority Voting over CoT) CoT is useful but not always consistent.
- **OCR:** Q: If John has 3 apples and gives away 1, how many are left? Let's think step by step:

### fig_0073 — It’s a simple idea: when in doubt, ask the model several times and trust the

- **Page:** 52 (PDF page 54) · **Chapter:** Prompt Engineering
- **BBox:** [114.38, 67.50, 497.62, 204.00] on page 612×792 pt · **Render:** 1065×379 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.98)
- **Primary branch:** llm-engineering · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `d7479888dc43160a` · dup group `dup_0071` (1)
- **Caption:** It’s a simple idea: when in doubt, ask the model several times and trust the
- **Paragraph after:** It’s a simple idea: when in doubt, ask the model several times and trust the majority. This technique often leads to more robust results, especially on ambiguous or complex tasks.
- **OCR:** = ‘E&;‘ww,unmm;m Pl Mayjority Voting TR over CoTl User UM Reasoning & ‘suwl --)‘supz‘ —)‘supnl WM Reasoning & deepgeck ‘Sk&p‘ll — > [step2] —->‘snpn\| J LLM Reasoning wge . ‘Sllpl‘ — > [step2] — > [stepn] Output 1 mis o Output 2 - I I Output 3 : _, - ey B Final output

### fig_0074 — 3) Tree of Thoughts (ToT)

- **Page:** 52 (PDF page 54) · **Chapter:** Prompt Engineering
- **BBox:** [112.12, 521.27, 499.88, 697.52] on page 612×792 pt · **Render:** 1077×490 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.84) · Evaluation (0.51)
- **Primary branch:** llm-engineering · **Confidence:** 0.84 → review queue
- **Integrity:** sha `6354449f0c0ed6a4` · dup group `dup_0072` (1)
- **Heading:** 3) Tree of Thoughts (ToT)
- **Paragraph before:** of reasoning at each point and then picks the best path overall. At every reasoning step, the model explores multiple possible directions. These branches form a tree, and a separate process evaluates which path seems the most promising at a particular timestamp.
- **OCR:** Tree of Thought 4 deepoack 1 v ¥ deapseekc LLM Reasoning \| [ v i v LM Reasoning doopsaaic _,B output Final >

### fig_0075 — Instead of letting LLMs reason freely, ARQs guide them through explicit,

- **Page:** 54 (PDF page 56) · **Chapter:** Prompt Engineering
- **BBox:** [115.12, 170.64, 496.88, 445.89] on page 612×792 pt · **Render:** 1061×765 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.84) · RAG / Knowledge Engineering (0.43) · Agent Protocol Fabric (0.43)
- **Primary branch:** llm-engineering · **Confidence:** 0.84 → review queue
- **Integrity:** sha `108f6431ad7681d5` · dup group `dup_0073` (2)
- **Caption:** Instead of letting LLMs reason freely, ARQs guide them through explicit,
- **Paragraph before:** But even with methods like CoT, reasoning remains free-form, i.e., the model “thinks aloud” but it has limited domain-specific control. That’s the exact problem the new technique, called Attentive Reasoning Queries (ARQs), solves.
- **Paragraph after:** Instead of letting LLMs reason freely, ARQs guide them through explicit, domain-specific questions. Essentially, each reasoning step is encoded as a targeted query inside a JSON schema.
- **OCR:** l ARQ : Structured Reasoning Approach that Prevents Hallucinations Direct Prompting ) *Reasoning is solely dependent on LUW's capability. Chain of LLM Reasoning m& Thought A N swv]---»[supz\|--->\|sm~\| FEen °"t""t (CoT) \| joinDailyDoseofDs.com N ety \| &> O - ET S 8- B Reasoning [ N o e Queries User O e - (ARQ) > ! Implemented in: & parlant @ Response

### fig_0076 — This type of query does two things:

- **Page:** 55 (PDF page 57) · **Chapter:** Prompt Engineering
- **BBox:** [138.38, 67.50, 473.62, 182.25] on page 612×792 pt · **Render:** 931×319 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.63) · RAG / Knowledge Engineering (0.54) · Context Engineering (0.44) · Agentic AI (0.44)
- **Primary branch:** llm-engineering · **Confidence:** 0.63 → review queue
- **Integrity:** sha `0eb9079be696a4d9` · dup group `dup_0074` (1)
- **Caption:** This type of query does two things:
- **Paragraph after:** This type of query does two things: 1. Reinstate critical instructions by keeping the LLM aligned mid-conversation. 2. Facilitate intermediate reasoning, so that the decisions are auditable and
- **OCR:** “current_context”: “Customer asking about refund eligibility”, “active_guideline”: “Always verify order before issuing refund”, “action_taken_before”: false, “requires_tool”: true, “next_step”: “Run check_order_status()”

### fig_0077 — By the time the LLM generates the final response, it’s already walked through a

- **Page:** 55 (PDF page 57) · **Chapter:** Prompt Engineering
- **BBox:** [144.00, 312.70, 468.00, 500.20] on page 612×792 pt · **Render:** 900×521 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.68) · Evaluation (0.51) · AI / ML Foundation (0.43) · Agentic AI (0.43)
- **Primary branch:** llm-engineering · **Confidence:** 0.68 → review queue
- **Integrity:** sha `1764f01cd969bb1f` · dup group `dup_0075` (1)
- **Caption:** By the time the LLM generates the final response, it’s already walked through a
- **Paragraph before:** 1. Reinstate critical instructions by keeping the LLM aligned mid-conversation. 2. Facilitate intermediate reasoning, so that the decisions are auditable and verifiable.
- **Paragraph after:** By the time the LLM generates the final response, it’s already walked through a sequence of *controlled* reasoning steps, which did not involve any free text exploration (unlike techniques like CoT or ToT). Here’s the success rate across test scenarios:
- **OCR:** Evaluate which guidelines are relevant for the current conversation. Guidelines: ### 1) When answering questions,

### fig_0078 — ●

- **Page:** 56 (PDF page 58) · **Chapter:** Prompt Engineering
- **BBox:** [107.25, 150.86, 504.75, 333.86] on page 612×792 pt · **Render:** 1105×508 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Tool / Action Fabric (0.62) · Agentic AI (0.51) · LLM Engineering (0.51) · Business Automation (0.40)
- **Primary branch:** tool-action-fabric · **Confidence:** 0.62 → review queue
- **Integrity:** sha `7f5243c53b8c7b6c` · dup group `dup_0076` (1)
- **Caption:** ●
- **Paragraph before:** This approach is actually implemented in Parlant, a recently trending open-source framework to build instruction-following Agents. ARQs are integrated into three key modules:
- **Paragraph after:** ● Guideline proposer to decide which behavioral rules apply. ● Tool caller to determine what external functions to use. ● Message generator, when it produces the final customer-facing reply.
- **OCR:** Engine GuidelineProposer ToolCaller MessageGenerator Propose relevant guidelines Infer and execute tool calls Tool results ﬂ o Tailor message Generated message ﬂ oot S S R A SR B A A R0

### fig_0079 — Verbalized Sampling

- **Page:** 57 (PDF page 59) · **Chapter:** Prompt Engineering
- **BBox:** [121.50, 167.25, 490.50, 303.00] on page 612×792 pt · **Render:** 1025×377 px
- **Composition:** raster · **Role:** result · **Quality:** 0.6
- **Mapping:** LLM Engineering (0.84) · AI / ML Foundation (0.51)
- **Primary branch:** llm-engineering · **Confidence:** 0.84 → review queue
- **Integrity:** sha `e984c678d45024d1` · dup group `dup_0077` (1)
- **Heading:** Verbalized Sampling
- **Caption:** However, these methods unintentionally cause a significant drop in output
- **Paragraph before:** Verbalized Sampling Post-training alignment methods, such as RLHF, are designed to make LLMs helpful and safe.
- **Paragraph after:** However, these methods unintentionally cause a significant drop in output diversity (called mode collapse). When an LLM collapses to a mode, it starts favoring a narrow set of predictable or stereotypical responses over other outputs.
- **OCR:** Preference

### fig_0080 — Verbalized Sampling

- **Page:** 57 (PDF page 59) · **Chapter:** Prompt Engineering
- **BBox:** [108.38, 465.24, 503.62, 599.49] on page 612×792 pt · **Render:** 1097×373 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.68) · AI / ML Foundation (0.46) · Agentic AI (0.46) · Agent Memory (0.46)
- **Primary branch:** llm-engineering · **Confidence:** 0.68 → review queue
- **Integrity:** sha `608f701de7cf3220` · dup group `dup_0078` (1)
- **Heading:** Verbalized Sampling
- **Caption:** Here’s how this happens:
- **Paragraph before:** When an LLM collapses to a mode, it starts favoring a narrow set of predictable or stereotypical responses over other outputs. According to a paper, mode collapse happens because the human preference data used to train the LLM has a hidden flaw called typicality bias.
- **Paragraph after:** Here’s how this happens: Annotators are asked to rate different responses from an LLM, and later, the LLM is trained using a reward model that learns to mimic these human preferences.
- **OCR:** 3.1 TYPICALITY BIAS IN PREFERENCE DATA: COGNITIVE & EMPIRICAL EVIDENCE Typicality Bias Hypothesis. Cognitive psychology shows that people prefer text that is familiar, fluent, and predictable. This preference is rooted in various principles. For instance, the mere-exposure effect (Zajonc, 1968; Bornstein, 1989) and availability heuristic (Tversky & Kahneman, 1973) imply that frequent or easily recalled content feels more likely and is liked more. Processing fluency (Alter & Oppenheimer, 2009; Reber et al., 2004) suggests that easy-to-process content is automatically perceived as more truthful and higher quality. Moreover, schema congruity theory (Mandler, 2014; Meyers-Levy & Tybout, 1989) predicts that information that aligns with existing mental models will be accepted with less critical thought. We therefore hypothesize that these cognitive tendencies lead to a typicality bias in prefe

### fig_0081 — Prompt Engineering figure

- **Page:** 58 (PDF page 60) · **Chapter:** Prompt Engineering
- **BBox:** [107.25, 499.86, 504.75, 709.11] on page 612×792 pt · **Render:** 1105×581 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.98)
- **Primary branch:** llm-engineering · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `3cdbe9d06971e6b6` · dup group `dup_0079` (1)
- **Paragraph before:** response] Verbalized sampling (VS) solves this. It is a training-free prompting strategy introduced to circumvent mode collapse and recover the diverse distribution learned during pre-training.
- **OCR:** Problem: Typicality Bias Causes Mode Collapse Tell me a joke about coffee leverse Base LLM @ Whydidthe @ Espresso may coffee file... not solve all... Cold brewis @ Why did the just coffee... latte go to... 1. Direct Prompting Tell me a joke about coffee. X5 The most likely joke about coffee is one specific joke: /Snlution: Verbalized Sampling (VS) Mitigates Mode Collapse ~ Different prompts collapse to different modes: 2. Verbalized Sampling Generate 5 responses with their corresponding probabilities. Tell me a joke about coffee. The most likely set of five jokes will cover a range of jokes: Y Typicality Bias 0-0-0-0 \| 000 Amplified in Post-Training Why did the coffee file a police rej Because it got mugged! Why did the coffee file a police report? output x2 Because it got mugged! \ Why did the coffee file a police report? Because it got mugged! 2@ cuiuti [ Wy did the coftee file a polce

### fig_0082 — Verbalized sampling significantly enhances diversity by 1.6-2.1x over direct

- **Page:** 59 (PDF page 61) · **Chapter:** Prompt Engineering
- **BBox:** [136.50, 408.72, 475.50, 664.47] on page 612×792 pt · **Render:** 941×710 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.86) · Agent Protocol Fabric (0.42) · Evaluation (0.42)
- **Primary branch:** llm-engineering · **Confidence:** 0.86 → auto-accept
- **Integrity:** sha `14140bc6ec9285dc` · dup group `dup_0080` (1)
- **Caption:** Verbalized sampling significantly enhances diversity by 1.6-2.1x over direct
- **Paragraph before:** So essentially, by asking the LLM to verbalize the probability distribution, the model is able to tap into the broader, diverse set of ideas, which comes from the rich distribution that still exists inside its core pre-trained weights. Experiments across various tasks demonstrate significant benefits:
- **Paragraph after:** Verbalized sampling significantly enhances diversity by 1.6-2.1x over direct prompting, while maintaining or improving quality. Variants like verbalized
- **OCR:** " Direct mm CoT WM Sequence NN Multitur VS-Standard S VS-CoT NN VS-Muli a Poem (1) b Story (1) c Joke (1) a0 258 wp Ty %0 70‘ ., mse9628 s % ne \| 80— T \| = .,8,25 0 { 501 wer 00 £ 14 e i3 - &5 114 122 30 T 0] g u S & e e DA S P OIS RIS @ P @é‘b & P g o 3 ,;‘? & o S ‘éf ﬁsf}f o @5&5&5 \{’,\9 Gé) e %fza ol i " & ‘Small Models (GPT-4.1-Mini, Gemini-2.5-Flash) WM Large Models (GPT-4.1, Gemini-2.5-Pro) d Diversity vs. Quality (Poem) € Emergent Trend: A in Diversity f Cognitive Burden: A in Quality - ] st 6 - . s & L VS-Milti ‘ B 8 [ 25 & 64 Vs-CoT @ 2 [l < o4 3 5.5 muttisum ) 8™ ot B o é-z 60 Sequence ys.Standard e 15 20 25 Diversity Score

### fig_0083 — Natural language is powerful yet vague.

- **Page:** 61 (PDF page 63) · **Chapter:** Prompt Engineering
- **BBox:** [131.62, 67.50, 480.38, 367.50] on page 612×792 pt · **Render:** 969×833 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.82) · Infrastructure (0.47) · Agent Protocol Fabric (0.41)
- **Primary branch:** llm-engineering · **Confidence:** 0.82 → review queue
- **Integrity:** sha `af3a5c4e03bbfc75` · dup group `dup_0081` (1)
- **Caption:** Natural language is powerful yet vague.
- **Paragraph after:** Natural language is powerful yet vague. When you give instructions like "summarize this email" or "give me key takeaways," you leave room for interpretation, which can lead to hallucinations. And if you try JSON prompts, you get consistent outputs:
- **OCR:** \| JSON prompting vs. Text prompting » a ¢ Features JSON prompting Text prompting w join DailyDoseof DS.com £§ Structure Clearly defined, machine-friendly syntax Flexible, conversational, and human-oriented Precision Explicit fields reduce guesswork Meaning depends on interpretation @ Consistency Output is predictable and easy to validate Variable outputs and harder to validate ﬂ Scalability Highly scalable Error-prone as scope or data grows @ Integration API and avtomation-friendly Needs formatting or parsing

### fig_0084 — Prompt Engineering figure

- **Page:** 61 (PDF page 63) · **Chapter:** Prompt Engineering
- **BBox:** [108.75, 490.16, 503.25, 719.66] on page 612×792 pt · **Render:** 1095×638 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.65) · Context Engineering (0.60) · Security (0.45)
- **Primary branch:** llm-engineering · **Confidence:** 0.65 → review queue
- **Integrity:** sha `5082bdeeaff9a5ab` · dup group `dup_0082` (1)
- **Paragraph before:** Natural language is powerful yet vague. When you give instructions like "summarize this email" or "give me key takeaways," you leave room for interpretation, which can lead to hallucinations. And if you try JSON prompts, you get consistent outputs:
- **OCR:** JSON Prompt: Consistent outputs arize_email® €¥~ - Launch delayed to March 15 after security audit; “Product launch moved to March 15 after a budget raised to $75K urity audit; budget inc: 0 § 75K > - Tasks: David - audit (Feb 20), Lisa - campaign (Feb 25) 4 handles the audit (Feb 26), Lisa the Consistent - Next meeting: Aug 19, 2:00 PM, contact ext. 4521 aign (Feb 25). Next meeting:Aug 19,2 PM" Output Exactly 3 bullet points Natural language Prompt: Variable outputs &' Product launch set for March 15 "su ze this o : = with $75K budget; tasks due Feb-Mar, next meeting Aug 19, 2:00 PM (ext. 4521). Product launch moved to Maxch 15 after a Inconsistent urity audit; budget increased to § 75K Outputs - . handles the audit ( 20), Liss the Product launch set for March 15 after security audit; paign (Feb 25). Next meeting:Aug 19,2 pH." \| —————> budget now $75K. David (audit), Lisa (campaign), &.

### fig_0085 — 1) Structure means certainty

- **Page:** 62 (PDF page 64) · **Chapter:** Prompt Engineering
- **BBox:** [171.75, 310.10, 440.25, 509.60] on page 612×792 pt · **Render:** 745×554 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.98)
- **Primary branch:** llm-engineering · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `9c968353e3e21020` · dup group `dup_0083` (1)
- **Heading:** 1) Structure means certainty
- **Caption:** 2) You control the outputs
- **Paragraph before:** 1) Structure means certainty JSON forces you to think in terms of fields and values, which is a gift. It eliminates gray areas and guesswork. Here's a simple example:
- **Paragraph after:** 2) You control the outputs Prompting isn't just about what you ask; it's about what you expect back.
- **OCR:** "task": "Summarize", "format": "bullet points", "tone": "professional", "length": "3 key takeaways"

### fig_0086 — And this works irrespective of what you are doing, like generating content,

- **Page:** 63 (PDF page 65) · **Chapter:** Prompt Engineering
- **BBox:** [128.62, 67.50, 483.38, 289.50] on page 612×792 pt · **Render:** 985×617 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.84) · Infrastructure (0.43) · Business Automation (0.43)
- **Primary branch:** llm-engineering · **Confidence:** 0.84 → review queue
- **Integrity:** sha `c8007895496becf1` · dup group `dup_0084` (1)
- **Caption:** And this works irrespective of what you are doing, like generating content,
- **Paragraph after:** And this works irrespective of what you are doing, like generating content, reports, or insights. JSON prompts ensure a consistent structure every time. No more surprises, just predictable results! 3) Reusable templates → Scalability, Speed & Clean
- **OCR:** Traditional prompt alyze this customer view and tell me JSON Prompt < "task": “sentiment_analysis", about the sentiment "input": "The product exceeded my expectations!", "output_format": { "sentiment": "positive\|negative\|neutral", "confidence": "0.0-1.0", "key_phrases": ["array", "of", "strings"], "summary": "brief explanation" Explicitly defined output format Now LLM will produce same structured response every time

### fig_0087 — handoffs

- **Page:** 63 (PDF page 65) · **Chapter:** Prompt Engineering
- **BBox:** [156.00, 432.57, 456.00, 616.32] on page 612×792 pt · **Render:** 833×511 px
- **Composition:** raster · **Role:** result · **Quality:** 0.6
- **Mapping:** LLM Engineering (0.73) · Multi-Agent (0.46) · Data Engineering (0.46) · Agent Protocol Fabric (0.40)
- **Primary branch:** llm-engineering · **Confidence:** 0.73 → review queue
- **Integrity:** sha `a6b6cd51ab3fb5d4` · dup group `dup_0085` (1)
- **Heading:** handoffs
- **Caption:** You can turn JSON prompts into shareable templates for consistent outputs.
- **Paragraph before:** reports, or insights. JSON prompts ensure a consistent structure every time. No more surprises, just predictable results! 3) Reusable templates → Scalability, Speed & Clean handoffs
- **Paragraph after:** You can turn JSON prompts into shareable templates for consistent outputs. Teams can plug results directly into APIs, databases, and apps; no manual formatting, so work stays reliable and moves much faster.
- **OCR:** Databases JSON prompt

### fig_0088 — To summarise:

- **Page:** 64 (PDF page 66) · **Chapter:** Prompt Engineering
- **BBox:** [156.00, 246.22, 456.00, 530.47] on page 612×792 pt · **Render:** 833×790 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.74) · AI / ML Foundation (0.61)
- **Primary branch:** llm-engineering · **Confidence:** 0.74 → review queue
- **Integrity:** sha `116f65f208682b69` · dup group `dup_0086` (1)
- **Caption:** To summarise:
- **Paragraph before:** ● Claude handles XML exceptionally well ● Markdown provides structure without overhead So it's mainly about structure rather than syntax as depicted below:
- **Paragraph after:** To summarise: Structured JSON prompting for LLMs is like writing modular code; it brings clarity of thought, makes adding new requirements effortless, & creates better communication with AI.
- **OCR:** JSON Prompt Tokens 59 Characters Braces, commas, 205 colons etc. are a token overhead Markdown Prompt (Structured) Tokens 41 Characters 151 Less tokens. Saves money &

### fig_0089 — What is Fine-tuning?

- **Page:** 66 (PDF page 68) · **Chapter:** Fine-tuning
- **BBox:** [119.62, 238.61, 492.38, 354.86] on page 612×792 pt · **Render:** 1035×323 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.91) · Observability (0.44)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.91 → auto-accept
- **Integrity:** sha `bb03edb293c2df64` · dup group `dup_0087` (2)
- **Heading:** What is Fine-tuning?
- **Caption:** When the model was developed, it was trained on a specific dataset that might
- **Paragraph before:** public use, in most cases, practitioners would fine-tune that model to their specific task. Fine-tuning means adjusting the weights of a pre-trained model on a new dataset for better performance. This is neatly depicted in the diagram below:
- **Paragraph after:** When the model was developed, it was trained on a specific dataset that might not perfectly match the characteristics of the data a practitioner wants to use it on. The original dataset might have had slightly different distributions, patterns, or
- **OCR:** . 5 blog. DailyDoseafDS. com Fine Tuning < -+ Gradient flow O Full pre-trained network . Appended network

### fig_0090 — fine-tuning

- **Page:** 67 (PDF page 69) · **Chapter:** Fine-tuning
- **BBox:** [147.00, 358.15, 465.00, 574.15] on page 612×792 pt · **Render:** 883×600 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.6
- **Mapping:** AI / ML Foundation (0.81) · Infrastructure (0.44) · Agent Memory (0.40) · Agent Protocol Fabric (0.40)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.81 → review queue
- **Integrity:** sha `ed28ac9655dffe6e` · dup group `dup_0088` (1)
- **Heading:** fine-tuning
- **Caption:** Fine-tuning BERT-large on a single GPU is easy with traditional fine-tuning.
- **Paragraph before:** technique on much larger models - LLMs, for instance. This is because, as you may already know, these models are huge - billions or even trillions of parameters. Consider the size difference between BERT-large and GPT-3:
- **Paragraph after:** Fine-tuning BERT-large on a single GPU is easy with traditional fine-tuning. But it's impossible with GPT-3, which has 175B parameters. That's 350GB of memory just to store model weights (float16 precision). Imagine OpenAI used traditional fine-tuning within its fine-tuning API:
- **OCR:** 10¢ QP’ 510% O BERT-large 6PT-3

### fig_0091 — ●

- **Page:** 68 (PDF page 70) · **Chapter:** Fine-tuning
- **BBox:** [137.25, 67.50, 474.75, 231.00] on page 612×792 pt · **Render:** 937×454 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.84) · Data Engineering (0.51)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.84 → review queue
- **Integrity:** sha `b104eee95d8f9df9` · dup group `dup_0089` (1)
- **Caption:** ●
- **Paragraph after:** ● If users fine-tuned GPT-3 → 3500 GB to store weights. ● If 1000 users fine-tuned GPT-3 → 350k GB to store weights.
- **OCR:** @% Duplicate > Opendl Pre-trained LM Duplicated Fine-tuned Modlel Model

### fig_0092 — Additionally, maintaining the infrastructure to support fine-tuning requests from

- **Page:** 69 (PDF page 71) · **Chapter:** Fine-tuning
- **BBox:** [148.12, 67.50, 463.88, 299.25] on page 612×792 pt · **Render:** 877×644 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.78) · Business Automation (0.57)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.78 → review queue
- **Integrity:** sha `23176185ed8dace2` · dup group `dup_0090` (1)
- **Caption:** Additionally, maintaining the infrastructure to support fine-tuning requests from
- **Paragraph after:** Additionally, maintaining the infrastructure to support fine-tuning requests from potentially thousands of customers simultaneously would be a huge task for them. LLM Fine-tuning Techniques
- **OCR:** w«w Duplicate @ @ 1 E& 1 i Duplicate @ Duplicate opent T Pre-trained Lm Dugplicate

### fig_0093 — LLM Fine-tuning Techniques

- **Page:** 69 (PDF page 71) · **Chapter:** Fine-tuning
- **BBox:** [116.62, 509.09, 495.38, 627.59] on page 612×792 pt · **Render:** 1053×329 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.93) · Observability (0.42)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.93 → auto-accept
- **Integrity:** sha `53f185d651167fbc` · dup group `dup_0087` (2)
- **Heading:** LLM Fine-tuning Techniques
- **Caption:** Thankfully, today, we have many optimal ways to fine-tune LLMs, and five such
- **Paragraph before:** LLM Fine-tuning Techniques Traditional fine-tuning (depicted below) is infeasible with LLMs because these models have billions of parameters and are hundreds of GBs in size, and not everyone has access to such computing infrastructure.
- **Paragraph after:** Thankfully, today, we have many optimal ways to fine-tune LLMs, and five such popular techniques are depicted below:
- **OCR:** \o Eﬁ{ blog. DailyDoseofDS.com Fine Tuning <~ Gradient flow O Full pre-trained network . Appended network

### fig_0094 — Let’s understand these:

- **Page:** 70 (PDF page 72) · **Chapter:** Fine-tuning
- **BBox:** [109.50, 67.50, 502.50, 521.25] on page 612×792 pt · **Render:** 1091×1260 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.95) · Observability (0.40)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.95 → auto-accept
- **Integrity:** sha `529d588f451ccf4d` · dup group `dup_0091` (1)
- **Caption:** Let’s understand these:
- **Paragraph after:** Let’s understand these: 1) LoRA Add two low-rank matrices A and B alongside weight matrices, which contain the trainable parameters. Instead of fine-tuning W, adjust the updates in these
- **OCR:** LoRA Trainable weights 5 Techniques to o\2 t&{ blog.DailyDoseofDS.com LoRA+ Almost similar to LoRA LoRA update rule \| LoRA+ update rule Pretrained weights 57 ST WA =Wt (A - By — e Bi) fioher learning rate ~ for matrix B ¥ B<—B—a6— B<—B—Aa6—J e (EEE=mm ) Trableweights 0B 0B

### fig_0095 — 2) LoRA-FA

- **Page:** 71 (PDF page 73) · **Chapter:** Fine-tuning
- **BBox:** [121.88, 67.50, 490.12, 248.25] on page 612×792 pt · **Render:** 1023×502 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.92) · Agent Memory (0.43)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.92 → auto-accept
- **Integrity:** sha `8b1d8ccb047e26d4` · dup group `dup_0092` (1)
- **Caption:** 2) LoRA-FA
- **Paragraph after:** 2) LoRA-FA While LoRA considerably decreases the total trainable parameters, it still requires substantial activation memory to update the low-rank weights. LoRA-FA (FA stands for Frozen-A) freezes the matrix A and only updates matrix B.
- **OCR:** S S I B = & ; T Low-rank [ aem\,\| ~ watrices

### fig_0096 — 2) LoRA-FA

- **Page:** 71 (PDF page 73) · **Chapter:** Fine-tuning
- **BBox:** [118.12, 359.23, 493.88, 527.23] on page 612×792 pt · **Render:** 1043×467 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.6
- **Mapping:** AI / ML Foundation (0.93) · Agent Memory (0.42)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.93 → auto-accept
- **Integrity:** sha `2e83cbc954d4057f` · dup group `dup_0093` (1)
- **Heading:** 2) LoRA-FA
- **Caption:** 3) VeRA
- **Paragraph before:** 2) LoRA-FA While LoRA considerably decreases the total trainable parameters, it still requires substantial activation memory to update the low-rank weights. LoRA-FA (FA stands for Frozen-A) freezes the matrix A and only updates matrix B.
- **Paragraph after:** 3) VeRA In LoRA, every layer has a different pair of low-rank matrices A and B, and both matrices are trained. In VeRA, however, matrices A and B are frozen, random, and shared across all model layers. VeRA focuses on learning small, layer-specific
- **OCR:** Onlc/ matrix B is trained zeR

### fig_0097 — 4) Delta-LoRA

- **Page:** 72 (PDF page 74) · **Chapter:** Fine-tuning
- **BBox:** [114.00, 67.50, 498.00, 242.25] on page 612×792 pt · **Render:** 1067×485 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.6
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `f34f9afbd37fdf2a` · dup group `dup_0094` (1)
- **Caption:** 4) Delta-LoRA
- **Paragraph after:** 4) Delta-LoRA Here, in addition to training low-rank matrices, the matrix W is also adjusted but not in the traditional way. Instead, the difference (or delta) between the product of the low-rank matrices A and B in two consecutive training steps is added to W:
- **OCR:** zeR! (g QV\JOM

### fig_0098 — 4) Delta-LoRA

- **Page:** 72 (PDF page 74) · **Chapter:** Fine-tuning
- **BBox:** [119.25, 353.23, 492.75, 540.73] on page 612×792 pt · **Render:** 1037×521 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.94) · Security (0.41)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.94 → auto-accept
- **Integrity:** sha `3cc0d3d7cf69f794` · dup group `dup_0095` (1)
- **Heading:** 4) Delta-LoRA
- **Caption:** 5) LoRA+
- **Paragraph before:** 4) Delta-LoRA Here, in addition to training low-rank matrices, the matrix W is also adjusted but not in the traditional way. Instead, the difference (or delta) between the product of the low-rank matrices A and B in two consecutive training steps is added to W:
- **Paragraph after:** 5) LoRA+ In LoRA, both matrices A and B are updated with the same learning rate. Authors found that setting a higher learning rate for matrix B results in more optimal convergence.
- **OCR:** Delta-LoRA e S Al matrices [ W e B ® are trainable W = Wt c(Agyy - Byt — Are By) Ac RO £ ¢ zeR? Trainable w'gm/ VVH_1 = Wt + C(At—\|—1 2 Bt+1 i At * Bt)

### fig_0099 — Bonus: LoRA-drop

- **Page:** 73 (PDF page 75) · **Chapter:** Fine-tuning
- **BBox:** [91.12, 67.50, 520.88, 245.25] on page 612×792 pt · **Render:** 1193×494 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.95) · Infrastructure (0.40)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.95 → auto-accept
- **Integrity:** sha `5ecafbee35ebf4d7` · dup group `dup_0096` (1)
- **Caption:** Bonus: LoRA-drop
- **Paragraph after:** Bonus: LoRA-drop LoRA-drop observes that not all layers benefit equally from LoRA updates. It first adds low-rank matrices to every layer and trains briefly, then measures each layer’s activation strength to see which layers actually matter.
- **OCR:** LoRA+ Almost similar to LoRA LoRA update rule \| LoRA+ update rule oJ oJ A— A asy A+ A asT Higher lfe:‘rning r:af; matrix B+ B a(j‘] B+ B )\adJ 0B 0B LoRA+ asSigns higher leaming rate for updo(ting matrix B

### fig_0100 — Bonus: LoRA-drop

- **Page:** 73 (PDF page 75) · **Chapter:** Fine-tuning
- **BBox:** [66.00, 335.66, 446.62, 506.13] on page 612×792 pt · **Render:** 1057×473 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.94) · Infrastructure (0.41)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.94 → auto-accept
- **Integrity:** sha `3f87b9ad0c66b0b4` · dup group `dup_0097` (1)
- **Heading:** Bonus: LoRA-drop
- **Caption:** Layers whose LoRA activations stay near zero have minimal influence on the
- **Paragraph before:** Bonus: LoRA-drop LoRA-drop observes that not all layers benefit equally from LoRA updates. It first adds low-rank matrices to every layer and trains briefly, then measures each
- **Paragraph after:** Layers whose LoRA activations stay near zero have minimal influence on the model's output and can be removed.
- **OCR:** layer’s activation strength to see which layers actually matter. ®\| --> B > o\| > \| 0 Activation Statistics

### fig_0101 — By keeping LoRA only in high-impact layers, LoRA-drop reduces training cost

- **Page:** 74 (PDF page 76) · **Chapter:** Fine-tuning
- **BBox:** [126.00, 67.50, 486.00, 221.25] on page 612×792 pt · **Render:** 1000×427 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.85) · Business Automation (0.43) · RAG / Knowledge Engineering (0.39) · Evaluation (0.39)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.85 → auto-accept
- **Integrity:** sha `eb02f72a0ddb535e` · dup group `dup_0098` (1)
- **Caption:** By keeping LoRA only in high-impact layers, LoRA-drop reduces training cost
- **Paragraph after:** By keeping LoRA only in high-impact layers, LoRA-drop reduces training cost and speeds up fine-tuning with little to no loss in accuracy. Bonus: Quantized Low-Rank Adaptation (QLoRA) Quantized Low-Rank Adaptation (QLoRA) is an improvement on the LoRA
- **OCR:** @0 @ @ Average Activation 0.97 1.2 \ Correspowhng neurons é// can be l‘ke_ly removed

### fig_0102 — Bonus: Quantized Low-Rank Adaptation (QLoRA)

- **Page:** 74 (PDF page 76) · **Chapter:** Fine-tuning
- **BBox:** [123.75, 434.38, 488.25, 624.13] on page 612×792 pt · **Render:** 1013×527 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.77) · Agent Protocol Fabric (0.49) · Agent Memory (0.44)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.77 → review queue
- **Integrity:** sha `6ba0b572ad880771` · dup group `dup_0099` (1)
- **Heading:** Bonus: Quantized Low-Rank Adaptation (QLoRA)
- **Caption:** Now, considering the example where we have Million parameters in the
- **Paragraph before:** technique discussed above, which further addresses the memory limitations associated with fine-tuning large models using LoRA. More specifically, if we recall what we discussed above in LoRA, we saw that we augment the network layers whose weights are W with two matrices A and B.
- **Paragraph after:** Now, considering the example where we have Million parameters in the weight matrix W:
- **OCR:** Fixced duﬁng Pme—tun;nﬁ [ Pretrained \| Bepwp? ) weights X /4 ¢ ® J ‘v\ { w 1 Rd*k \| ( A—E Rd*r \‘ / Pme-tun'mg learned a(uﬁmj

### fig_0103 — Typically, these million parameters will be represented as float32, which

- **Page:** 75 (PDF page 77) · **Chapter:** Fine-tuning
- **BBox:** [138.75, 67.50, 473.25, 207.00] on page 612×792 pt · **Render:** 929×388 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.74) · Agent Memory (0.61)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.74 → review queue
- **Integrity:** sha `3001cd5bc39b5954` · dup group `dup_0100` (1)
- **Caption:** Typically, these million parameters will be represented as float32, which
- **Paragraph after:** Typically, these million parameters will be represented as float32, which requires bits (or bytes) per parameter. This leads to a significant memory footprint, especially for large LLMs. This results in a memory utilization of (25 million * bytes/parameter) =
- **OCR:** 1228¢ Large u./ejgh‘t matrix Params = 209€«122€ % =~ 25 Million 204

### fig_0104 — This results in a significant decrease in the amount of memory required to store

- **Page:** 75 (PDF page 77) · **Chapter:** Fine-tuning
- **BBox:** [121.12, 440.59, 490.88, 596.59] on page 612×792 pt · **Render:** 1027×434 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.72) · Agent Memory (0.49) · Data Engineering (0.44) · Agent Protocol Fabric (0.40)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.72 → review queue
- **Integrity:** sha `4808f6c0ffbeaf9a` · dup group `dup_0101` (2)
- **Caption:** This results in a significant decrease in the amount of memory required to store
- **Paragraph before:** The idea in QLoRA is to reduce this memory utilization of weight matrix W using Quantization. As you may have guessed, Quantization involves using lower-bit representations, such as 16-bit, 8-bit, or 4-bit, to represent parameters.
- **Paragraph after:** This results in a significant decrease in the amount of memory required to store the model's parameters. For instance, consider your model has over a million parameters, each represented with 32-bit floating-point numbers.
- **OCR:** Weigh‘t matrix Represented as large data type Quantization —_— Quantized Weight wmatrix

### fig_0105 — Bonus: DoRA

- **Page:** 76 (PDF page 78) · **Chapter:** Fine-tuning
- **BBox:** [141.38, 554.77, 470.62, 713.02] on page 612×792 pt · **Render:** 915×439 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `ce2944a7444521bc` · dup group `dup_0102` (1)
- **Heading:** Bonus: DoRA
- **Paragraph before:** (Low-Rank Adaptation) while preserving its efficiency. At its core, DoRA builds upon the principles of LoRA but introduces a decomposition step that separates a pretrained weight matrix W into two components: magnitude (m) and direction (V).
- **OCR:** m k \| \| — Pre-trained wodel L v re~trow weight matrix W

### fig_0106 — Scratch

- **Page:** 77 (PDF page 79) · **Chapter:** Fine-tuning
- **BBox:** [120.38, 303.64, 491.62, 449.14] on page 612×792 pt · **Render:** 1031×404 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.6
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `8493eb82997d49c4` · dup group `dup_0103` (2)
- **Heading:** Scratch
- **Caption:** During fine-tuning, the gradient update rule suggests that we must add ΔW to
- **Paragraph before:** Let us understand LoRA in more detail. Consider the current weights of some random layer in the pre-trained model are ∗ W of dimensions d k, and we wish to fine-tune it on some other dataset.
- **Paragraph after:** During fine-tuning, the gradient update rule suggests that we must add ΔW to get the updated parameters: For simplicity, you can think about ΔW as the update obtained after running gradient descent on the new dataset:
- **OCR:** Wej::,ht @ o Motrix W Pre-trained Model

### fig_0107 — Scratch

- **Page:** 77 (PDF page 79) · **Chapter:** Fine-tuning
- **BBox:** [122.25, 508.23, 489.75, 636.48] on page 612×792 pt · **Render:** 1021×357 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.6
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `1e6f771bca01e977` · dup group `dup_0104` (1)
- **Heading:** Scratch
- **Caption:** For simplicity, you can think about ΔW as the update obtained after running
- **Paragraph before:** ∗ W of dimensions d k, and we wish to fine-tune it on some other dataset. During fine-tuning, the gradient update rule suggests that we must add ΔW to get the updated parameters:
- **Paragraph after:** For simplicity, you can think about ΔW as the update obtained after running gradient descent on the new dataset:

### fig_0108 — Also, instead of updating the original weights W, it is perfectly legal to maintain

- **Page:** 78 (PDF page 80) · **Chapter:** Fine-tuning
- **BBox:** [117.00, 67.50, 495.00, 161.25] on page 612×792 pt · **Render:** 1050×260 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.6
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `6a7b79168477e924` · dup group `dup_0105` (1)
- **Caption:** Also, instead of updating the original weights W, it is perfectly legal to maintain
- **Paragraph after:** Also, instead of updating the original weights W, it is perfectly legal to maintain both matrics, Wand ΔW. During inference, we can compute the prediction on an input sample x as follows: In fact, in all the model fine-tuning iterations, W can be kept static, and all
- **OCR:** Gradient descent wCigh‘t 4§J W« W

### fig_0109 — In fact, in all the model fine-tuning iterations, W can be kept static, and all

- **Page:** 78 (PDF page 80) · **Chapter:** Fine-tuning
- **BBox:** [121.88, 252.13, 490.12, 334.63] on page 612×792 pt · **Render:** 1023×229 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.6
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `e1ff972ff63d9438` · dup group `dup_0106` (1)
- **Caption:** In fact, in all the model fine-tuning iterations, W can be kept static, and all
- **Paragraph before:** Also, instead of updating the original weights W, it is perfectly legal to maintain both matrics, Wand ΔW. During inference, we can compute the prediction on an input sample x as follows:
- **Paragraph after:** In fact, in all the model fine-tuning iterations, W can be kept static, and all weight updates using gradient computation can be incorporated to ΔW instead. But you might be wondering...how does that even help? The matrix W is already huge, and we are talking about introducing another
- **OCR:** Prediction (W + AW)z=Wz + AWz

### fig_0110 — How does LoRA work?

- **Page:** 79 (PDF page 81) · **Chapter:** Fine-tuning
- **BBox:** [147.75, 327.39, 464.25, 434.64] on page 612×792 pt · **Render:** 879×298 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.6
- **Mapping:** AI / ML Foundation (0.89) · Agent Protocol Fabric (0.46)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.89 → auto-accept
- **Integrity:** sha `a743d5fe8f472202` · dup group `dup_0107` (1)
- **Heading:** How does LoRA work?
- **Caption:** ∗
- **Paragraph before:** not receive any gradient updates. Thus, all gradient updates are redirected to the ΔW matrix. But to ensure that ΔW and W remain additive to generate a final representation for the fine-tuned model, the ΔW matrix is split into a product of two low-rank matrices A and B, which contain the trainable parameters.
- **Paragraph after:** ∗ As discussed earlier, the dimensions of W are d k: ∗ Thus, the dimensions of ΔW must also be d k. But this does not mean that the
- **OCR:** — AE Rd*r AW € R¥* — L, Be Rr*k

### fig_0111 — How does LoRA work?

- **Page:** 79 (PDF page 81) · **Chapter:** Fine-tuning
- **BBox:** [138.75, 473.95, 473.25, 605.95] on page 612×792 pt · **Render:** 929×367 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.6
- **Mapping:** AI / ML Foundation (0.89) · Agent Protocol Fabric (0.46)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.89 → auto-accept
- **Integrity:** sha `c363dc813c4583c3` · dup group `dup_0103` (2)
- **Heading:** How does LoRA work?
- **Caption:** ∗
- **Paragraph before:** representation for the fine-tuned model, the ΔW matrix is split into a product of two low-rank matrices A and B, which contain the trainable parameters. ∗ As discussed earlier, the dimensions of W are d k:
- **Paragraph after:** ∗ Thus, the dimensions of ΔW must also be d k. But this does not mean that the total trainable parameters in A and B matrix must also align with the dimensions of ΔW.
- **OCR:** We?ght ol Motrix W Pre-trained Model

### fig_0112 — In the above image, every point denotes a possible LoRA configuration. Also, the

- **Page:** 80 (PDF page 82) · **Chapter:** Fine-tuning
- **BBox:** [124.88, 464.50, 487.12, 643.00] on page 612×792 pt · **Render:** 1007×496 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.94) · Observability (0.41)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.94 → auto-accept
- **Integrity:** sha `b94e91f3e2f5ff01` · dup group `dup_0108` (1)
- **Caption:** In the above image, every point denotes a possible LoRA configuration. Also, the
- **Paragraph before:** ● Do we really need to fine-tune all the parameters in the original model? ● How expressive are the parameters of the original model (or matrix rank)? This can be plotted as a 2D grid, as shown below:
- **Paragraph after:** In the above image, every point denotes a possible LoRA configuration. Also, the upper right corner refers to full fine-tuning.
- **OCR:** ull Fraction of B {-‘nne—‘tuning \ parameters Fine-tuned ® o - ® © .. P ©eo © 00 ® LoRA ® g e @ ... '. ® © .. conﬁguro\t-on © e _o ® @ ® @ o, %o 5 (6] 0. o e ¢ ®¢ o0 o Matrix rank s (nr\alogous to expressivity)

### fig_0113 — Implementation

- **Page:** 81 (PDF page 83) · **Chapter:** Fine-tuning
- **BBox:** [127.12, 360.97, 484.88, 545.47] on page 612×792 pt · **Render:** 993×513 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.93) · Agent Protocol Fabric (0.42)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.93 → auto-accept
- **Integrity:** sha `4ff5a7ba009af394` · dup group `dup_0109` (1)
- **Heading:** Implementation
- **Caption:** As demonstrated above, the LoRAWeights class aims to decompose a matrix of
- **Paragraph before:** practical details. As discussed above, a typical LoRA layer comprises two matrices, A and B. These have been implemented in the LoRAWeights class below along with the forward pass:
- **Paragraph after:** As demonstrated above, the LoRAWeights class aims to decompose a matrix of dimensionality d ∗ k into two matrices A and B. Thus, it accepts four parameters: ● d: The number of rows in matrix W.
- **OCR:** Low-rank init__(self, d, k, r, alpha): matrices super (LoRAWeights, self).__init__() self.A torch.nn.Parameter(torch.randn(d, r)) / self.B = torch.nn.Parameter(torch.zeros(r, k)) self.alpha alpha rward(self, x): self.alpha (x self.A self.B) X

### fig_0114 — In the forward method, the input x is multiplied by the matrices A and B, and then

- **Page:** 82 (PDF page 84) · **Chapter:** Fine-tuning
- **BBox:** [171.38, 281.57, 440.62, 396.32] on page 612×792 pt · **Render:** 747×318 px
- **Composition:** raster · **Role:** result · **Quality:** 0.6
- **Mapping:** AI / ML Foundation (0.76) · Infrastructure (0.51) · Agent Protocol Fabric (0.43)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.76 → review queue
- **Integrity:** sha `ce08ca98e1c23289` · dup group `dup_0110` (1)
- **Caption:** In the forward method, the input x is multiplied by the matrices A and B, and then
- **Paragraph before:** The matrix B is a zero matrix. As discussed earlier, this ensures that the product of AB is zero as we begin fine-tuning. This initialization also validates the fact that if no fine-tuning has been done so far, the original model weights are retained:
- **Paragraph after:** In the forward method, the input x is multiplied by the matrices A and B, and then scaled by alpha. The result is returned as the output of the module. The parameter alpha is another hyperparameter, which acts as a scaling factor. It determines the impact of the new layers on the current model.
- **OCR:** 0 W+AE:W

### fig_0115 — ● A higher value of alpha means that the changes made by the LoRA layer

- **Page:** 82 (PDF page 84) · **Chapter:** Fine-tuning
- **BBox:** [122.25, 506.98, 489.75, 592.48] on page 612×792 pt · **Render:** 1021×237 px
- **Composition:** raster · **Role:** result · **Quality:** 0.6
- **Mapping:** AI / ML Foundation (0.81) · Infrastructure (0.54)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.81 → review queue
- **Integrity:** sha `e987edff7d2aa23f` · dup group `dup_0111` (1)
- **Caption:** ● A higher value of alpha means that the changes made by the LoRA layer
- **Paragraph before:** In the forward method, the input x is multiplied by the matrices A and B, and then scaled by alpha. The result is returned as the output of the module. The parameter alpha is another hyperparameter, which acts as a scaling factor. It determines the impact of the new layers on the current model.
- **Paragraph after:** ● A higher value of alpha means that the changes made by the LoRA layer will be more significant, potentially leading to more pronounced adjustments in the model's behavior.
- **OCR:** Prediction (W + aAW)z =Wz + \|

### fig_0116 — As LoRA is used after training, so we will already have a trained model available.

- **Page:** 83 (PDF page 85) · **Chapter:** Fine-tuning
- **BBox:** [124.50, 170.64, 487.50, 408.39] on page 612×792 pt · **Render:** 1009×661 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.92) · Agent Protocol Fabric (0.43)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.92 → auto-accept
- **Integrity:** sha `beb8d769920dd55f` · dup group `dup_0112` (1)
- **Caption:** As LoRA is used after training, so we will already have a trained model available.
- **Paragraph before:** ● Conversely, a lower value of alpha results in more subtle changes, as the impact of the transformation is reduced. As discussed earlier, LoRA is used on large matrices of a neural network. For instance, say we have the following neural network class:
- **Paragraph after:** As LoRA is used after training, so we will already have a trained model available. Let’s say it is accessible using the model object. Now, our primary objective is to attach the matrices in LoRAWeights class with the matrices in the layers of the above network. And, of course, each layer (fc1,
- **OCR:** work(nn.Module): init__(self): network super (MyNeuralNetwork, self).__init__() IN:Mtll:tll self.fcl = nn.Linear(28%28, 512) L self.fc2 nn.Linear(512, 1024) self.fc3 = nn.Linear(1024, 128) self.fca nn.Linear(128, 10) forward(self, x): X Xx.view(-1, 28%28) X torch.relu(self.fcl(x)) x = torch.relu(self.fc2(x)) x = torch.relu(self.fc3(x)) X self.fca(x) X

### fig_0117 — Done!

- **Page:** 84 (PDF page 86) · **Chapter:** Fine-tuning
- **BBox:** [153.00, 138.86, 459.00, 240.11] on page 612×792 pt · **Render:** 850×281 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `cbc590a7f30cbbf2` · dup group `dup_0113` (1)
- **Caption:** Done!
- **Paragraph before:** Also, we must remember that the network is trained as we would usually train any other neural network, but while only training the weight matrices A and B, i.e., the pre-trained model (model) is frozen. We do this as follows:
- **Paragraph after:** Done! Next, we utilize the LoRAWeights class to define the fine-tuning network below: As depicted above: ● The LoRA layers are applied over the fully connected layer (fc1, fc2, fc3) in
- **OCR:** (X Freeze param model.parameters(): mode' weights param.requires_grad = False

### fig_0118 — As depicted above:

- **Page:** 84 (PDF page 86) · **Chapter:** Fine-tuning
- **BBox:** [120.75, 311.20, 491.25, 496.45] on page 612×792 pt · **Render:** 1029×515 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `238fe71057675d8b` · dup group `dup_0114` (1)
- **Caption:** As depicted above:
- **Paragraph before:** any other neural network, but while only training the weight matrices A and B, i.e., the pre-trained model (model) is frozen. We do this as follows: Done! Next, we utilize the LoRAWeights class to define the fine-tuning network below:
- **Paragraph after:** As depicted above: ● The LoRA layers are applied over the fully connected layer (fc1, fc2, fc3) in the existing model. More specifically, we create three LoRAWeights layers (loralayer1, loralayer2, loralayer3) based on the dimensions of the fully
- **OCR:** Model with class MyNeuralNetworkwithLoRA(nn.Module): def __init__(self, model, r-2, alpha-6.5): LoRAWeights super(MyNeuralNetworkwithloRA, self).__init_ () self.model = model self.loralayerl - LoRAWeights(model.fcl.in_features, model.fcl.out_features, r, alpha) self.loralayer? - LoRAWeights(model.fc2.in_features, model.fc2.out_features, r, alpha) self.loralayer3 - LoRAWeights(model.fc3.in_features, model.fc3.out_features, r, alpha) forward(self, x): x = x.view(-1, 28+28) x = torch.relu(self.model.fci(x) + self.loralayeri(x)) x = torch.relu(self.model.fc2(x) + self.loralayer2(x)) x = torch.relu(self.model.fc3(x) + self.loralayers(x)) x = self.fca(x) return x

### fig_0119 — Generating a synthetic dataset using existing LLMs and utilizing it for

- **Page:** 86 (PDF page 88) · **Chapter:** Fine-tuning
- **BBox:** [104.25, 67.50, 507.75, 204.75] on page 612×792 pt · **Render:** 1121×381 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.87) · LLM Engineering (0.48)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.87 → auto-accept
- **Integrity:** sha `81e2871bb34cb1af` · dup group `dup_0115` (1)
- **Caption:** Generating a synthetic dataset using existing LLMs and utilizing it for
- **Paragraph after:** Generating a synthetic dataset using existing LLMs and utilizing it for fine-tuning can improve this. The synthetic data will have fabricated examples of human-AI interactions. Check this sample:
- **OCR:** >>> "Prompt: What do llamas eat?" >>> "Reply: What do llamas smell like? \ How do you get along with 1llamas? Are llamas good pets? \ These are questions you might have if you A

### fig_0120 — This process is called instruction fine-tuning and it is described in the animation

- **Page:** 86 (PDF page 88) · **Chapter:** Fine-tuning
- **BBox:** [132.75, 327.41, 479.25, 480.41] on page 612×792 pt · **Render:** 963×425 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `86d4e2bbbaa52a24` · dup group `dup_0116` (1)
- **Caption:** This process is called instruction fine-tuning and it is described in the animation
- **Paragraph before:** Generating a synthetic dataset using existing LLMs and utilizing it for fine-tuning can improve this. The synthetic data will have fabricated examples of human-AI interactions. Check this sample:
- **Paragraph after:** This process is called instruction fine-tuning and it is described in the animation below: Distilabel is an open-source framework that facilitates generating domain-specific synthetic text data using LLMs.
- **OCR:** >> Human (instruction): What is 2 + 2? >> AI (response): 2 + 2 is 4.

### fig_0121 — ●

- **Page:** 87 (PDF page 89) · **Chapter:** Fine-tuning
- **BBox:** [98.62, 67.50, 513.38, 503.25] on page 612×792 pt · **Render:** 1153×1210 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `b1eeb7c4893b077f` · dup group `dup_0117` (1)
- **Caption:** ●
- **Paragraph after:** ● Input an instruction. ● Two LLMs generate responses. ●
- **OCR:** 'Instruction Fine Tuning in LLMs N join. DailyDoseofDS.com e - 1 Step 1) i wm- Generate - responses ' 1 from two \| 0 : LLMS I--)ﬁ-___-) uwm-2 St P 2) <<<Response 1>>> \| - - - Rank the responses another wn <<<Response 2>> Step 3) ) Creatt:: <<<Instruction>>> instruction response best-rated response pair : : _____ s data sample <<<Response 2>>>

### fig_0122 — Next, we load the Llama-3 models locally with Ollama:

- **Page:** 88 (PDF page 90) · **Chapter:** Fine-tuning
- **BBox:** [142.50, 67.50, 469.50, 197.25] on page 612×792 pt · **Render:** 909×360 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Data Engineering (0.68) · AI / ML Foundation (0.68)
- **Primary branch:** data-engineering · **Confidence:** 0.68 → review queue
- **Integrity:** sha `b0d989c0daa9a6f4` · dup group `dup_0118` (1)
- **Caption:** Next, we load the Llama-3 models locally with Ollama:
- **Paragraph after:** Next, we load the Llama-3 models locally with Ollama: Moving on, we define our pipeline:
- **OCR:** @ synthetic_data.py import pandas as pd from from from from from distilabel.llms import OllamalLLM distilabel.pipeline import Pipeline distilabel.steps import LoadDataFromHub distilabel.steps.tasks import TextGeneration, UltraFeedback distilabel.steps import GroupColumns

### fig_0123 — Moving on, we define our pipeline:

- **Page:** 88 (PDF page 90) · **Chapter:** Fine-tuning
- **BBox:** [111.00, 236.55, 501.00, 340.80] on page 612×792 pt · **Render:** 1083×289 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.74) · Data Engineering (0.61)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.74 → review queue
- **Integrity:** sha `8013cd2ea1b9bd9f` · dup group `dup_0119` (1)
- **Caption:** Moving on, we define our pipeline:
- **Paragraph before:** Next, we load the Llama-3 models locally with Ollama:
- **Paragraph after:** Moving on, we define our pipeline:
- **OCR:** synthetic_data.py OllamaLLM(model="1lama3.1", timeout=1000) OllamaLLM(model="1lama3.1:70b-instruct-q2_k", timeout=1000)

### fig_0124 — Fine-tuning figure

- **Page:** 88 (PDF page 90) · **Chapter:** Fine-tuning
- **BBox:** [134.62, 380.11, 477.38, 703.36] on page 612×792 pt · **Render:** 953×898 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Data Engineering (0.53) · Evaluation (0.53) · AI / ML Foundation (0.53) · LLM Engineering (0.47)
- **Primary branch:** data-engineering · **Confidence:** 0.53 → review queue
- **Integrity:** sha `3408fa0a7c9c23b0` · dup group `dup_0120` (1)
- **Paragraph before:** Next, we load the Llama-3 models locally with Ollama: Moving on, we define our pipeline:
- **OCR:** ©@6 & synthetic_datapy with Pipeline(name="preference-datagen-1lama3") as pipeline: # load dataset with prompts load_dataset = LoadDataFromHub ( name="1load_dataset", output_mappings={"prompt": "instruction"}, # generate two responses generate = [ TextGeneration(name="'text_generation_1', llm=modell), TextGeneration(name="'text_generation_2', llm=model2) # bine i s into one col combine = GroupColumns ( columns=["generation", "model_name"], output_columns=["generations", "model_names"] # rate responses with LLM-as-a-judge evaluate = UltraFeedback(aspect="overall-rating", llm=model2) # define and run load_dataset >> generate >> combine >> evaluate

### fig_0125 — Done!

- **Page:** 89 (PDF page 91) · **Chapter:** Fine-tuning
- **BBox:** [118.50, 301.36, 493.50, 443.11] on page 612×792 pt · **Render:** 1041×393 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Data Engineering (0.59) · AI / ML Foundation (0.59) · Evaluation (0.51)
- **Primary branch:** data-engineering · **Confidence:** 0.59 → review queue
- **Integrity:** sha `ee1fee1051976530` · dup group `dup_0121` (1)
- **Caption:** Done!
- **Paragraph before:** Once the pipeline has been defined, we need to execute it by giving it a seed dataset. The seed dataset helps it generate new but similar samples. So we execute the pipeline with our seed dataset as follows:
- **Paragraph after:** Done! This produces the instruction and response synthetic dataset as desired. Check the sample below:
- **OCR:** ®00 & synthetic_datapy it Dataset distiset = pipeline.run( parameters={ load_dataset.name: { "repo_id": "distilabel-internal-testing/instruction-dataset-mini", Tsplit”: "test",

### fig_0126 — Fine-tuning figure

- **Page:** 89 (PDF page 91) · **Chapter:** Fine-tuning
- **BBox:** [138.75, 545.98, 473.25, 719.23] on page 612×792 pt · **Render:** 929×481 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.84) · Data Engineering (0.51)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.84 → review queue
- **Integrity:** sha `9b26f43a6db69f59` · dup group `dup_0122` (1)
- **Paragraph before:** pipeline with our seed dataset as follows: Done! This produces the instruction and response synthetic dataset as desired. Check the sample below:
- **OCR:** Dataset sample generated using an LLM Response (LLM 1) Response (LLM 2) LLM Rating “To determine the value of N, we need to know As of my last updatein 4,5 ‘how many presidents there have been up until April 2023, Joe Biden has Joe Biden's presidency.\n\nAs of my last been the 46th President of update in April 2023, there were a total of 46 the United States since presidencies. However, please note that this taking office on January information might become outdated as new 20, 2021.\n\nSo, to answer ‘events occur\n\nGiven that Joe Biden is indeed your question: \nN = 46.' the 46th president of the United States, we can conclude:\n\nN = 46

### fig_0127 — Both update the model using LoRA or similar PEFT methods, but their goals and

- **Page:** 90 (PDF page 92) · **Chapter:** Fine-tuning
- **BBox:** [148.88, 317.57, 463.12, 667.07] on page 612×792 pt · **Render:** 873×970 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.84) · Infrastructure (0.43) · Reliability (0.40) · Agent Protocol Fabric (0.38)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.84 → review queue
- **Integrity:** sha `5d6ecd5ff7c8be67` · dup group `dup_0123` (1)
- **Caption:** Both update the model using LoRA or similar PEFT methods, but their goals and
- **Paragraph before:** Broadly, fine-tuning falls into two categories. ● Supervised Fine-Tuning (SFT) ● Reinforcement Fine-Tuning (RFT)
- **Paragraph after:** Both update the model using LoRA or similar PEFT methods, but their goals and training signals differ dramatically.
- **OCR:** \| Supervised fine-tuning vs. Reinforcement fine-tuning Supervised Fine-tuning (SFT) Online Deploy Deployment B[ 2]a] = deepseek Frozen UM Dataset Best LoRA Checkpoint _ SFT is an offline process and fine-tuning happens on static data Reinforcement Fine-tuning (RFT) GRPO Trainer .Jl \| Latest LoRA Checkpoint. RFT online fine-tuning Join.DailyDoseofDS.com Reward server

### fig_0128 — SFT process:

- **Page:** 91 (PDF page 93) · **Chapter:** Fine-tuning
- **BBox:** [127.88, 204.78, 484.12, 354.03] on page 612×792 pt · **Render:** 989×415 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.75) · LLM Engineering (0.45) · Infrastructure (0.45) · Reliability (0.40)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.75 → review queue
- **Integrity:** sha `50a3ef8217767e2f` · dup group `dup_0124` (1)
- **Heading:** SFT process:
- **Caption:** ● It starts with a static labeled dataset of prompt–completion pairs.
- **Paragraph before:** SFT vs RFT Before diving deeper, it's crucial to understand how we usually fine-tune LLMs using SFT, or supervised fine-tuning. SFT process:
- **Paragraph after:** ● It starts with a static labeled dataset of prompt–completion pairs. ● Adjust the model weights to match these completions. ● The best model (LoRA checkpoint) is then deployed for inference.
- **OCR:** Supervised Fine-tuning (SFT) SFT Trainer deepseek ’ Trainable Frozen LM Online Deployment _ [LorRAX Open-source LLM Serving SFT is an offline process and fine-tuning happens on static data

### fig_0129 — RFT process:

- **Page:** 91 (PDF page 93) · **Chapter:** Fine-tuning
- **BBox:** [124.50, 465.01, 487.50, 708.76] on page 612×792 pt · **Render:** 1009×677 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.76) · Reliability (0.47) · Infrastructure (0.47)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.76 → review queue
- **Integrity:** sha `5acc66c2163604d0` · dup group `dup_0125` (1)
- **Heading:** RFT process:
- **Paragraph before:** ● Adjust the model weights to match these completions. ● The best model (LoRA checkpoint) is then deployed for inference. RFT process:
- **OCR:** Reinforcement Fine-tuning (RFT) Checkpoint ‘_.f 13 Deploy \| v RFT online LORAX fine-tuning e ssies LM Serving HO) 30\%%’ join.DailyDoseofDS.com

### fig_0130 — This flowchart gives a quick guide on which fine-tuning method to use based on

- **Page:** 92 (PDF page 94) · **Chapter:** Fine-tuning
- **BBox:** [97.12, 230.00, 514.88, 500.00] on page 612×792 pt · **Render:** 1161×750 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.98)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `ed42331d1f3785dc` · dup group `dup_0126` (1)
- **Caption:** This flowchart gives a quick guide on which fine-tuning method to use based on
- **Paragraph before:** Over time, the model learns to generate higher-reward answers using GRPO. SFT uses static data and often memorizes answers. RFT, being online, learns from rewards and explores new strategies.
- **Paragraph after:** This flowchart gives a quick guide on which fine-tuning method to use based on your data and the nature of the task. ● Start by checking whether you have labelled (ground-truth) data. ● If you don’t, the next question is whether the task is verifiable.
- **OCR:** SFT vs RFT, when to use what ? Do you have ~ Ptz No-----~ laballed (ground truth) ----Yes-----. H B data? £ H Is the task i “verifiable?” = T : NO Yes <100 examples < 100 examples > 100K examples

### fig_0131 — ●

- **Page:** 94 (PDF page 96) · **Chapter:** Fine-tuning
- **BBox:** [116.25, 67.50, 495.75, 430.50] on page 612×792 pt · **Render:** 1055×1008 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.78) · LLM Engineering (0.57)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.78 → review queue
- **Integrity:** sha `95e9ec34f1f07261` · dup group `dup_0127` (1)
- **Caption:** ●
- **Paragraph after:** ● Start with a dataset and add a reasoning-focused system prompt (e.g., “Think step by step…”). ● The LLM generates multiple candidate responses using a sampling engine.
- **OCR:** lBuild Reasoning LLMs using GRPO }X: nvaesetscan Dataset System Prompt Tokenization z Think step by step Data ‘@) ) "hink step by \| _ . before you answer a Processing . Y steps; question, include the reasoning tokens in Generation Reward Calculation v GRPO Loss Calculator Back prop. Update Model Loss Caleculation \| [ ™)) ---—>\| cosee [----- deepseek

### fig_0132 — Let’s begin!

- **Page:** 95 (PDF page 97) · **Chapter:** Fine-tuning
- **BBox:** [156.38, 150.86, 455.62, 346.61] on page 612×792 pt · **Render:** 831×543 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.96) · Tool / Action Fabric (0.39)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.96 → auto-accept
- **Integrity:** sha `a3ace7b7454e5fab` · dup group `dup_0128` (1)
- **Caption:** Let’s begin!
- **Paragraph before:** ● HuggingFace TRL to apply GRPO. The code is available here: Build a reasoning LLM from scratch using GRPO. You can run it without any installations by reproducing our environment below:
- **Paragraph after:** Let’s begin! #1) Load the model We start by loading Qwen3-4B-Base and its tokenizer using Unsloth. You can use any other open-weight LLM here.
- **OCR:** Build a reasoning LLM from scratch using GRPO ﬂ Akshay Pachaar @ +~ September 4, 2025 7 1 Run directly here Overview Files 100% local Qwen 3 GRPO fine-tuning (using Unsloth) In this studio, we are fine-tuning Alibaba's Qwen 3 with advanced GRPO methods. It is the most recent generation of Qwen LLMs, with dense and mixture-of-experts (MoE) models. This studio will teach you how to use the proximity-based reward function (closer answers are rewarded) as well as the Hugging Face Open-R1 math dataset.

### fig_0133 — #1) Load the model

- **Page:** 95 (PDF page 97) · **Chapter:** Fine-tuning
- **BBox:** [138.75, 481.59, 473.25, 711.84] on page 612×792 pt · **Render:** 929×640 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.86) · Agent Memory (0.42) · Infrastructure (0.42)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.86 → auto-accept
- **Integrity:** sha `934602f8724f0928` · dup group `dup_0129` (1)
- **Heading:** #1) Load the model
- **Paragraph before:** Let’s begin! #1) Load the model We start by loading Qwen3-4B-Base and its tokenizer using Unsloth. You can use any other open-weight LLM here.
- **OCR:** Load model from unsloth import FastlLanguageModel import torch MODEL = "unsloth/Qwen3-4B-Base" model, tokenizer = FastlLanguageModel.from_pretrained( model_name = MODEL, max_seq_length = 2048, load_in_4bit = False, fast_inference = True, max_lora_rank = 32, gpu_memory_utilization = 0.7,

### fig_0134 — #2) Define LoRA config

- **Page:** 96 (PDF page 98) · **Chapter:** Fine-tuning
- **BBox:** [138.75, 151.17, 473.25, 386.67] on page 612×792 pt · **Render:** 929×655 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.94) · Reliability (0.41)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.94 → auto-accept
- **Integrity:** sha `d115f01e3c085452` · dup group `dup_0130` (1)
- **Heading:** #2) Define LoRA config
- **Caption:** ●
- **Paragraph before:** #2) Define LoRA config We'll use LoRA to avoid fine-tuning the entire model weights. In this code, we use Unsloth's PEFT by specifying:
- **Paragraph after:** ● The model ● LoRA low-rank (r)
- **OCR:** oo Define LoRA config model = FastLanguageModel.get_peft_model( model, target_modules = [ "q_proji®, kilproj®, “viproj®, o proj®, "gate_proj", "up_proj", "down_proj" 1, use_gradient_checkpointing = "unsloth" r =32, lora_alpha = 64, random_state = 3407,

### fig_0135 — Each sample includes:

- **Page:** 97 (PDF page 99) · **Chapter:** Fine-tuning
- **BBox:** [119.25, 67.50, 492.75, 350.25] on page 612×792 pt · **Render:** 1037×785 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.78) · AI / ML Foundation (0.51) · Agent Protocol Fabric (0.40)
- **Primary branch:** llm-engineering · **Confidence:** 0.78 → review queue
- **Integrity:** sha `324e364f29bf160b` · dup group `dup_0131` (1)
- **Caption:** Each sample includes:
- **Paragraph after:** Each sample includes: ● A system prompt enforcing structured reasoning ● A question from the dataset
- **OCR:** reason_start = "<start_working_out>" def create_dataset(split = "train" reason_end = "<end_working out>" data = load_dataset('open-r1/DAPO-Hath-17k-Processed' , soln_start = "<SOLUTION>" ‘en', split=split] soln_end "</ SOLUTION>" return data.map(lambda x: { *prompt’: [ system_prompt = \ {'zole': 'system', 'content': system_prompt}, £""You are given problem. {'role': 'user', 'content': x['prompt'l} Think about problem, provide work out 1) Place between {reason_start}{reason_end} "answer': extract_hash_answer(x['solution'])}) Provide solution between {soln_start}{soln_end)""" dataset = create_dataset() ooo Data sample >>> dataset[0] "prompt”: [ {"content": "You are given problem. \nThink about problem, provide work out. \n "role": "system'}, ontent”: "In triangle $ABCS, $\\sin \\angle A = \\frac{4}{5}$ and $\\angle A < 90*\\circs...", "role": "user"} 1, "solution": "34", "data_source": "ma

### fig_0136 — ● Match format exactly

- **Page:** 98 (PDF page 100) · **Chapter:** Fine-tuning
- **BBox:** [125.62, 67.50, 486.38, 426.00] on page 612×792 pt · **Render:** 1003×996 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.65) · LLM Engineering (0.53) · Evaluation (0.47) · Tool / Action Fabric (0.41)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.65 → review queue
- **Integrity:** sha `71e18e72634e6b04` · dup group `dup_0132` (1)
- **Caption:** ● Match format exactly
- **Paragraph after:** ● Match format exactly ● Match format approximately ● Check the answer
- **OCR:** oy GRPO Reward Functions match_format_exactly(completions, x+kwargs): return [ 3.0 if match_format.search(comp[0]["content"]) else 0.0 for comp in completions match_format_approximately(completions, #xkwargs): markers = (reasoning_end, solution_start, solution_end) return [ sum(@.5 if comp[@]["content"].count(marker) = 1 else -1.0 for marker in markers) for comp in completions check_answer (prompts, completions, answer, *xkwargs): responses = [comp[@]["content"] for comp in completions] extracted_responses = [ match.group(1) if (match := match_format.search(r)) else None for r in responses ] return [score_answer(guess, true) for guess, true in zip(extracted_responses, answer)] check_numbers(prompts, completions, answer, *xkwargs): ¢lobal PRINTED_TIMES responses = [comp[0]["content"] for comp in completions] extracted_responses = [ match.group(1) if (match := match_numbers.search(r)) else

### fig_0137 — Comparison

- **Page:** 99 (PDF page 101) · **Chapter:** Fine-tuning
- **BBox:** [124.50, 67.50, 487.50, 346.50] on page 612×792 pt · **Render:** 1009×775 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.95) · LLM Engineering (0.40)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.95 → auto-accept
- **Integrity:** sha `561bfa29e273a8ac` · dup group `dup_0133` (1)
- **Caption:** Comparison
- **Paragraph after:** Comparison Again, we can see how GRPO turned a base model into a reasoning powerhouse. RFT methods like GRPO work best when paired with reliable reinforcement learning environments. This brings us to an important component of RL-based
- **OCR:** eee GRPO Config @ from trl import GRPOConfig training_args = GRPOConfig( vlln_sampling_params temperature = 1.0, learning_rate = 5e-6, weight_decay = 0.01, warmup_ratio = 0.1, lr_scheduler_type = "linear", optim = "adamw_8bit", per_device_train_batch_size gradient_accumulation_steps num_generations = 4, max_steps = 100, vlln_params, stop TEUN s roara st comletion ength \|1 TS mateh_formst_sxactly eee GRPO Trainer @ from trl import GRPOTrainer trainer = GRPOTrainer( model = model, processing_class = tokenizer, reward_funcs = [ match_format_exactly, match_format_approximately, check_ansuer, check_numbers, 1, args = training args, train_dataset = dataset, ) trainer.train() Chack_snver Check_numbers

### fig_0138 — Comparison

- **Page:** 99 (PDF page 101) · **Chapter:** Fine-tuning
- **BBox:** [125.62, 417.91, 486.38, 641.41] on page 612×792 pt · **Render:** 1003×621 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.88) · LLM Engineering (0.41) · Agentic AI (0.41)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.88 → auto-accept
- **Integrity:** sha `4c090286bee369a2` · dup group `dup_0134` (1)
- **Heading:** Comparison
- **Caption:** RFT methods like GRPO work best when paired with reliable reinforcement
- **Paragraph before:** Comparison Again, we can see how GRPO turned a base model into a reasoning powerhouse.
- **Paragraph after:** RFT methods like GRPO work best when paired with reliable reinforcement learning environments. This brings us to an important component of RL-based fine-tuning: how agents interact with environments.
- **OCR:** Before finetuning After finetuning (model generates random output) (gives accurate response with reasoning) pling_parans = sampling_params, a_request = model. load_lora("dont_touch/grpo_saved itputs (0] . text = f'<start_working_out>{output}" Which is the sqrt of 1017 Wiki User + 2009-10-28 06:34:05 See Answer Best Answer Copy 10.0503781525921 Wiki User ests: 100% [ 111 [00:00<00:00, 84 * 2009-10-28 06:34:05 This answer is: prompts: 100% Helpful Not Helpful <00:00, 50.72sfit, est. speed input: 1.14 toks/s, output] i 5.0499}\n\\]<end_working_out><SOLUTION>10.0499</50) ® Add a Comment Add your answer: Earn + 20 pts

### fig_0139 — ● An agent interacts with the environment through an OpenEnv client.

- **Page:** 101 (PDF page 103) · **Chapter:** Fine-tuning
- **BBox:** [97.12, 170.64, 514.88, 385.89] on page 612×792 pt · **Render:** 1161×598 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.57) · Agent Protocol Fabric (0.57) · Agentic AI (0.48) · Infrastructure (0.44)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.57 → review queue
- **Integrity:** sha `2b2d537711e0afbe` · dup group `dup_0135` (1)
- **Caption:** ● An agent interacts with the environment through an OpenEnv client.
- **Paragraph before:** Environments run in isolated Docker containers and communicate over HTTP, allowing them to be reproduced, shared, and executed consistently across machines. The typical workflow proceeds as follows:
- **Paragraph after:** ● An agent interacts with the environment through an OpenEnv client. ● The client forwards actions to a FastAPI application running inside a Docker container.
- **OCR:** \| OpenEnv: Environments for Agentic RL Training o 5 mcpDailyDoseofDS.com Reward + Observation HTTP response JSON: observations, rewards, done

### fig_0140 — Trainer(ART)

- **Page:** 102 (PDF page 104) · **Chapter:** Fine-tuning
- **BBox:** [112.88, 329.43, 499.12, 567.18] on page 612×792 pt · **Render:** 1073×660 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.60) · AI / ML Foundation (0.57) · Agent Protocol Fabric (0.46) · Infrastructure (0.42)
- **Primary branch:** agentic-ai · **Confidence:** 0.60 → review queue
- **Integrity:** sha `40fbddde57759699` · dup group `dup_0136` (1)
- **Heading:** Trainer(ART)
- **Caption:** It is an open-source framework designed specifically for training agentic LLMs
- **Paragraph before:** produces multi-step reasoning traces, tool calls, conversations and plans. Training such agents requires a system that can collect these trajectories, assign rewards and update the model reliably. ART (Agent Reinforcement Trainer), built by OpenPipe, provides that system.
- **Paragraph after:** It is an open-source framework designed specifically for training agentic LLMs from experience. ART handles the pieces that are difficult to engineer manually: ● running the agent to generate full trajectories ●
- **OCR:** \|ART: Agent Reinforcement Trainer Architecture ART Backend o\S o o s mcp.DailyDoseofDS.com of Inference service BreTClient LA — = o T ; Tnference request ‘l < vLLM Server Model output (trajectorie: 1 1 Load new LoR: \| checkpoint 9 . \| v Rewards A 1 \| 1 \| 1 1 1 [ [ Actions ! ! Training service 1 1 \ Training request (trajectories + RL Environment vewards) GRPO trainer

### fig_0141 — What is RAG?

- **Page:** 105 (PDF page 107) · **Chapter:** RAG
- **BBox:** [112.50, 390.97, 499.50, 576.22] on page 612×792 pt · **Render:** 1075×514 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.81) · Evaluation (0.46) · Agent Memory (0.39) · Data Engineering (0.39)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.81 → review queue
- **Integrity:** sha `be6b2692cbe6b35a` · dup group `dup_0137` (1)
- **Heading:** What is RAG?
- **Caption:** ● Retrieval: Accessing and retrieving information from a knowledge source,
- **Paragraph before:** documents, or anything that appeared after their training cutoff. Retraining them repeatedly to stay updated is impractical and expensive. This is where Retrieval-Augmented Generation (RAG) comes in. Let’s break it down:
- **Paragraph after:** ● Retrieval: Accessing and retrieving information from a knowledge source, such as a database or memory. ● Augmented: Enhancing or enriching something, in this case, the text
- **OCR:** Additional Encode. 5 Re_tﬁQVoJ documents Augmen'teo(

### fig_0142 — What are vector databases?

- **Page:** 106 (PDF page 108) · **Chapter:** RAG
- **BBox:** [161.62, 394.25, 450.38, 553.25] on page 612×792 pt · **Render:** 803×441 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.75) · Data Engineering (0.49) · AI / ML Foundation (0.43) · Evaluation (0.38)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.75 → review queue
- **Integrity:** sha `3e058785cbe85969` · dup group `dup_0138` (1)
- **Heading:** What are vector databases?
- **Caption:** Each data point, whether a word, a document, an image, or any other entity, is
- **Paragraph before:** vector databases - the storage layer that powers retrieval. What are vector databases? Simply put, a vector database stores unstructured data (text, images, audio, video, etc.) in the form of vector embeddings.
- **Paragraph after:** Each data point, whether a word, a document, an image, or any other entity, is transformed into a numerical vector using ML techniques (which we shall see ahead). This numerical vector is called an embedding, and the model is trained in such a
- **OCR:** unstructured data Embeddings (oa[7 oo a3 ] (o« o5 17 ) (e [ a 15 ) (-1 Joz 53) (=5]as 05 (=12 [os 0.a) (a3]0a 07) (o] e -2.4) (o5 \|15 az)

### fig_0143 — This shows that embeddings can learn the semantic characteristics of entities

- **Page:** 107 (PDF page 109) · **Chapter:** RAG
- **BBox:** [147.75, 138.86, 464.25, 250.61] on page 612×792 pt · **Render:** 879×311 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.63) · RAG / Knowledge Engineering (0.63) · Data Engineering (0.44)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.63 → review queue
- **Integrity:** sha `a2762422614ca69b` · dup group `dup_0139` (1)
- **Caption:** This shows that embeddings can learn the semantic characteristics of entities
- **Paragraph before:** Considering word embeddings, for instance, we may discover that in the embedding space, the embeddings of fruits are found close to each other, which cities form another cluster, and so on.
- **Paragraph after:** This shows that embeddings can learn the semantic characteristics of entities they represent (provided they are trained appropriately). Once stored in a vector database, we can retrieve original objects that are similar to the query we wish to run on our unstructured data.
- **OCR:** Leam embeddings. . Pigeon apple guava orange

### fig_0144 — In other words, encoding unstructured data allows us to run many sophisticated

- **Page:** 107 (PDF page 109) · **Chapter:** RAG
- **BBox:** [137.62, 361.27, 474.38, 487.27] on page 612×792 pt · **Render:** 935×350 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.74) · Data Engineering (0.54) · AI / ML Foundation (0.41)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.74 → review queue
- **Integrity:** sha `7cb5d5248a0d2698` · dup group `dup_0140` (1)
- **Caption:** In other words, encoding unstructured data allows us to run many sophisticated
- **Paragraph before:** This shows that embeddings can learn the semantic characteristics of entities they represent (provided they are trained appropriately). Once stored in a vector database, we can retrieve original objects that are similar to the query we wish to run on our unstructured data.
- **Paragraph after:** In other words, encoding unstructured data allows us to run many sophisticated operations like similarity search, clustering, and classification over it, which otherwise is difficult with traditional databases. To exemplify, when an e-commerce website provides recommendations for similar items
- **OCR:** find nearest - ne_‘ﬁhlaors Venice'! —— apple guava orange Parrot Sparrow Pigeon

### fig_0145 — in RAG

- **Page:** 108 (PDF page 110) · **Chapter:** RAG
- **BBox:** [146.25, 370.15, 465.75, 466.90] on page 612×792 pt · **Render:** 887×268 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.6
- **Mapping:** RAG / Knowledge Engineering (0.68) · Infrastructure (0.54) · Data Engineering (0.41) · Evaluation (0.41)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.68 → review queue
- **Integrity:** sha `2984524a350979fe` · dup group `dup_0141` (1)
- **Heading:** in RAG
- **Caption:** For instance, if the model was deployed after considering the data until 31st Jan
- **Paragraph before:** Where do vector databases fit in here? Let's understand this. To begin, we must understand that an LLM is deployed after learning from a static version of the corpus it was fed during training.
- **Paragraph after:** For instance, if the model was deployed after considering the data until 31st Jan 2024, and we use it, say, a week after training, it will have no clue about what happened in those days. Repeatedly training a new model (or adapting the latest version) every single day

### fig_0146 — in RAG

- **Page:** 108 (PDF page 110) · **Chapter:** RAG
- **BBox:** [153.75, 545.78, 458.25, 644.78] on page 612×792 pt · **Render:** 845×275 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.68) · Evaluation (0.51) · Infrastructure (0.43) · Business Automation (0.43)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.68 → review queue
- **Integrity:** sha `53de61c64e70f524` · dup group `dup_0142` (1)
- **Heading:** in RAG
- **Caption:** Repeatedly training a new model (or adapting the latest version) every single day
- **Paragraph before:** static version of the corpus it was fed during training. For instance, if the model was deployed after considering the data until 31st Jan 2024, and we use it, say, a week after training, it will have no clue about what happened in those days.
- **Paragraph after:** Repeatedly training a new model (or adapting the latest version) every single day on new data is impractical and cost-ineffective. In fact, LLMs can take weeks to train.
- **OCR:** Promet Election results were » I have declared on 2nd Feb. o no idea What happened?

### fig_0147 — But if you think about it, is it really our objective to train an LLM to know every

- **Page:** 109 (PDF page 111) · **Chapter:** RAG
- **BBox:** [153.00, 150.86, 459.00, 273.86] on page 612×792 pt · **Render:** 850×341 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.98)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `07d5508f09256113` · dup group `dup_0143` (1)
- **Caption:** But if you think about it, is it really our objective to train an LLM to know every
- **Paragraph before:** Also, what if we open-sourced the LLM and someone else wants to use it on their privately held dataset, which, of course, was not shown during training? As expected, the LLM will have no clue about it.
- **Paragraph after:** But if you think about it, is it really our objective to train an LLM to know every single thing in the world? Not at all! That’s not our objective.
- **OCR:** Promp‘t Ta“ me wmy % Pt:Ve SO\ICS n the no idea last 10 Jays Ope'\"SOUf‘Qe LM

### fig_0148 — So, once we have trained this model on a ridiculously large enough training

- **Page:** 109 (PDF page 111) · **Chapter:** RAG
- **BBox:** [145.50, 448.09, 466.50, 547.84] on page 612×792 pt · **Render:** 891×277 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.98)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `181e58a19a5eef82` · dup group `dup_0144` (1)
- **Caption:** So, once we have trained this model on a ridiculously large enough training
- **Paragraph before:** Not at all! That’s not our objective. Instead, it is more about helping the LLM learn the overall structure of the language, and how to understand and generate it.
- **Paragraph after:** So, once we have trained this model on a ridiculously large enough training corpus, it can be expected that the model will have a decent level of language understanding and generation capabilities. Thus, if we could figure out a way for LLMs to look up new information they
- **OCR:** Now I know Train how lmguage = works and some LM details about this world

### fig_0149 — But since LLMs usually have a limit on the context window (number of

- **Page:** 110 (PDF page 112) · **Chapter:** RAG
- **BBox:** [151.12, 99.29, 460.88, 200.54] on page 612×792 pt · **Render:** 861×282 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.61) · Context Engineering (0.52) · Data Engineering (0.48) · LLM Engineering (0.44)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.61 → review queue
- **Integrity:** sha `dfb0a154a60b2790` · dup group `dup_0145` (1)
- **Caption:** But since LLMs usually have a limit on the context window (number of
- **Paragraph before:** One way could be to provide that information in the prompt itself.
- **Paragraph after:** But since LLMs usually have a limit on the context window (number of words/tokens they can accept), the additional information can exceed that limit. Vector databases solve this problem. As discussed earlier, vector databases store information in the form of vectors,
- **OCR:** This is too @% » wuch information for me n LIM the prompt Extroct insights from this data

### fig_0150 — When the LLM needs to access this information, it can query the vector database

- **Page:** 110 (PDF page 112) · **Chapter:** RAG
- **BBox:** [150.75, 414.34, 461.25, 552.34] on page 612×792 pt · **Render:** 863×384 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.80) · Data Engineering (0.48) · AI / ML Foundation (0.38) · LLM Engineering (0.38)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.80 → review queue
- **Integrity:** sha `c3e3d3beb7f38569` · dup group `dup_0146` (1)
- **Caption:** When the LLM needs to access this information, it can query the vector database
- **Paragraph before:** where each vector captures semantic information about the piece of text being encoded. Thus, we can maintain our available information in a vector database by encoding it into vectors using an embedding model.
- **Paragraph after:** When the LLM needs to access this information, it can query the vector database using an approximate similarity search with the prompt vector to find content that is similar to the input query vector.
- **OCR:** vector database “o- P o—o—oo Fo7—07 10-$ " of Unseen or new information

### fig_0151 — Once the approximate nearest neighbors have been retrieved, we gather the

- **Page:** 111 (PDF page 113) · **Chapter:** RAG
- **BBox:** [170.25, 67.50, 441.75, 280.50] on page 612×792 pt · **Render:** 755×592 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.73) · Data Engineering (0.50) · LLM Engineering (0.43) · Context Engineering (0.39)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.73 → review queue
- **Integrity:** sha `a9e68b769faff358` · dup group `dup_0147` (1)
- **Caption:** Once the approximate nearest neighbors have been retrieved, we gather the
- **Paragraph after:** Once the approximate nearest neighbors have been retrieved, we gather the context corresponding to those specific vectors, which were stored at the time of indexing the data in the vector database (this raw data is stored as payload, which we will learn during implementation).
- **OCR:** Prompt Prompt vector ‘I'e” me wmy last 10 o(od.ls Petah nearest neagkbor vector database of unseen data

### fig_0152 — The above search process retrieves context that is similar to the query vector,

- **Page:** 111 (PDF page 113) · **Chapter:** RAG
- **BBox:** [154.50, 379.16, 457.50, 572.66] on page 612×792 pt · **Render:** 841×537 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.75) · Context Engineering (0.45) · LLM Engineering (0.42) · Data Engineering (0.42)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.75 → review queue
- **Integrity:** sha `fd3a2a0a43904b4f` · dup group `dup_0148` (1)
- **Caption:** The above search process retrieves context that is similar to the query vector,
- **Paragraph before:** Once the approximate nearest neighbors have been retrieved, we gather the context corresponding to those specific vectors, which were stored at the time of indexing the data in the vector database (this raw data is stored as payload, which we will learn during implementation).
- **Paragraph after:** The above search process retrieves context that is similar to the query vector, which represents the context or topic the LLM is interested in. We can augment this retrieved content along with the actual prompt provided by the user and give it as input to the LLM.
- **OCR:** Prompt Prompt vector Tell me wmy encode last 10 olays fetch nearest ne_igl«\loor the T rted wles b \| el mearest neighbor text vector The bum this r— dotabase of unseen data wmonth was ...

### fig_0153 — Consequently, the LLM can easily incorporate this info while generating text

- **Page:** 112 (PDF page 114) · **Chapter:** RAG
- **BBox:** [182.62, 67.50, 429.38, 249.00] on page 612×792 pt · **Render:** 685×504 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.68) · LLM Engineering (0.51) · n8n / Workflow Automation (0.43) · Business Automation (0.43)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.68 → review queue
- **Integrity:** sha `7dabf07ff4b02d1f` · dup group `dup_0149` (1)
- **Caption:** Consequently, the LLM can easily incorporate this info while generating text
- **Paragraph after:** Consequently, the LLM can easily incorporate this info while generating text because it now has the relevant details available in the prompt. Now that we understand the purpose, let's get into the technical details. Workflow of a RAG system
- **OCR:** Promet Te_“ wme my s«le,s n the last 10 days prompt sent to LLM —_— the team reported sales of ... LLM The bum this wonth was ...

### fig_0154 — Workflow of a RAG system

- **Page:** 112 (PDF page 114) · **Chapter:** RAG
- **BBox:** [123.75, 491.20, 488.25, 709.45] on page 612×792 pt · **Render:** 1013×606 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.80) · LLM Engineering (0.41) · Context Engineering (0.41) · n8n / Workflow Automation (0.41)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.80 → review queue
- **Integrity:** sha `79f591079343f7ae` · dup group `dup_0150` (1)
- **Heading:** Workflow of a RAG system
- **Paragraph before:** To build a RAG system, it's crucial to understand the foundational components that go into it and how they interact. Thus, in this section, let's explore each element in detail. Here's an architecture diagram of a typical RAG setup:
- **OCR:** Chunks & chatuithvourCode! Custom Knowledge base Llama3.2 Prompt Template Answer this “Guery’ Based on the the Rollowing Context @ avery vestor O il Vestor

### fig_0155 — #1) Create chunks

- **Page:** 113 (PDF page 115) · **Chapter:** RAG
- **BBox:** [201.75, 150.86, 410.25, 259.61] on page 612×792 pt · **Render:** 579×302 px
- **Composition:** raster · **Role:** process · **Quality:** 0.6
- **Mapping:** RAG / Knowledge Engineering (0.87) · AI / ML Foundation (0.41) · Data Engineering (0.41)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.87 → auto-accept
- **Integrity:** sha `56fb0beff3901a13` · dup group `dup_0151` (1)
- **Caption:** #1) Create chunks
- **Paragraph before:** Let's break it down step by step. We start with some external knowledge that wasn't seen during training, and we want to augment the LLM with:
- **Paragraph after:** #1) Create chunks The first step is to break down this additional knowledge into chunks before embedding and storing it in the vector database. We do this because the additional document(s) can be pretty large. Thus, it is
- **OCR:** Additional knowledge base == PDF

### fig_0156 — #1) Create chunks

- **Page:** 113 (PDF page 115) · **Chapter:** RAG
- **BBox:** [149.25, 350.80, 462.75, 428.80] on page 612×792 pt · **Render:** 871×217 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.82) · AI / ML Foundation (0.46) · Context Engineering (0.39) · Data Engineering (0.39)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.82 → review queue
- **Integrity:** sha `3d3aacad01ee8796` · dup group `dup_0152` (1)
- **Heading:** #1) Create chunks
- **Caption:** We do this because the additional document(s) can be pretty large. Thus, it is
- **Paragraph before:** want to augment the LLM with: #1) Create chunks The first step is to break down this additional knowledge into chunks before embedding and storing it in the vector database.
- **Paragraph after:** We do this because the additional document(s) can be pretty large. Thus, it is important to ensure that the text fits the input size of the embedding model. Moreover, if we don't chunk, the entire document will have a single embedding, which won't be of any practical use to retrieve relevant context.
- **OCR:** Additional knowledge base Chunks m chmg % 8 8 Doc PDF

### fig_0157 — #1) Create chunks

- **Page:** 113 (PDF page 115) · **Chapter:** RAG
- **BBox:** [143.25, 487.89, 468.75, 567.39] on page 612×792 pt · **Render:** 905×221 px
- **Composition:** raster · **Role:** process · **Quality:** 0.6
- **Mapping:** RAG / Knowledge Engineering (0.77) · AI / ML Foundation (0.52) · Context Engineering (0.38) · Data Engineering (0.38)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.77 → review queue
- **Integrity:** sha `aac57d28386b350e` · dup group `dup_0153` (1)
- **Heading:** #1) Create chunks
- **Caption:** Moreover, if we don't chunk, the entire document will have a single embedding,
- **Paragraph before:** The first step is to break down this additional knowledge into chunks before embedding and storing it in the vector database. We do this because the additional document(s) can be pretty large. Thus, it is important to ensure that the text fits the input size of the embedding model.
- **Paragraph after:** Moreover, if we don't chunk, the entire document will have a single embedding, which won't be of any practical use to retrieve relevant context. #2) Generate embeddings After chunking, we embed the chunks using an embedding model.
- **OCR:** Chunki g et

### fig_0158 — Since these are “context embedding models” (not word embedding models),

- **Page:** 114 (PDF page 116) · **Chapter:** RAG
- **BBox:** [136.12, 67.50, 475.88, 190.50] on page 612×792 pt · **Render:** 943×342 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.65) · AI / ML Foundation (0.54) · Data Engineering (0.46) · Context Engineering (0.40)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.65 → review queue
- **Integrity:** sha `e0518d0a7a0ce12a` · dup group `dup_0154` (1)
- **Caption:** Since these are “context embedding models” (not word embedding models),
- **Paragraph after:** Since these are “context embedding models” (not word embedding models), models like bi-encoders are highly relevant here. #3) Store embeddings in a vector database These embeddings are then stored in the vector database:
- **OCR:** Chunk O Chunk 1 Chunks Ewmbedding @ Chunk 2 DO O\| s, \|G \| — L) s Chunk 4 Chunk 5

### fig_0159 — #3) Store embeddings in a vector database

- **Page:** 114 (PDF page 116) · **Chapter:** RAG
- **BBox:** [148.50, 313.48, 463.50, 459.73] on page 612×792 pt · **Render:** 875×407 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.68) · Data Engineering (0.54) · AI / ML Foundation (0.45) · Agent Memory (0.38)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.68 → review queue
- **Integrity:** sha `d1348294c9f0a3b8` · dup group `dup_0155` (1)
- **Heading:** #3) Store embeddings in a vector database
- **Caption:** This shows that a vector database acts as a memory for your RAG application
- **Paragraph before:** Since these are “context embedding models” (not word embedding models), models like bi-encoders are highly relevant here. #3) Store embeddings in a vector database These embeddings are then stored in the vector database:
- **Paragraph after:** This shows that a vector database acts as a memory for your RAG application since this is precisely where we store all the additional knowledge, using which, the user's query will be answered. A vector database also stores the metadata and original content along with the vector
- **OCR:** Chunk 0 Chunk 1 Chunk 2 Chunk 3 Chunk 4 Churk 5 Ewbedding of a chunk

### fig_0160 — #5) Embed the query

- **Page:** 115 (PDF page 117) · **Chapter:** RAG
- **BBox:** [178.88, 119.08, 433.12, 203.83] on page 612×792 pt · **Render:** 707×236 px
- **Composition:** raster · **Role:** process · **Quality:** 0.6
- **Mapping:** RAG / Knowledge Engineering (0.95) · AI / ML Foundation (0.40)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.95 → auto-accept
- **Integrity:** sha `438268135ca2b064` · dup group `dup_0156` (1)
- **Caption:** #5) Embed the query
- **Paragraph before:** Next, the user inputs a query, a string representing the information they're seeking.
- **Paragraph after:** #5) Embed the query This query is transformed into a vector using the same embedding model we used to embed the chunks earlier in Step 2. #6) Retrieve similar chunks
- **OCR:** & Application User

### fig_0161 — #5) Embed the query

- **Page:** 115 (PDF page 117) · **Chapter:** RAG
- **BBox:** [149.62, 295.02, 462.38, 387.27] on page 612×792 pt · **Render:** 869×256 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.86) · AI / ML Foundation (0.43) · Data Engineering (0.41)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.86 → auto-accept
- **Integrity:** sha `9a500224bb9ebebc` · dup group `dup_0157` (1)
- **Heading:** #5) Embed the query
- **Caption:** #6) Retrieve similar chunks
- **Paragraph before:** seeking. #5) Embed the query This query is transformed into a vector using the same embedding model we used to embed the chunks earlier in Step 2.
- **Paragraph after:** #6) Retrieve similar chunks The vectorized query is then compared against our existing vectors in the database to find the most similar information. The vector database returns the k (a pre-defined parameter) most similar
- **OCR:** U ser 0o 1 2 p Embedding LUSER QUERY> \| ———» — :D:I E E—wwi odel Query embedding

### fig_0162 — #6) Retrieve similar chunks

- **Page:** 115 (PDF page 117) · **Chapter:** RAG
- **BBox:** [132.38, 478.45, 479.62, 614.95] on page 612×792 pt · **Render:** 965×379 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.88) · Data Engineering (0.47)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.88 → auto-accept
- **Integrity:** sha `7eab5bf3cddb1e16` · dup group `dup_0158` (1)
- **Heading:** #6) Retrieve similar chunks
- **Caption:** The vector database returns the k (a pre-defined parameter) most similar
- **Paragraph before:** to embed the chunks earlier in Step 2. #6) Retrieve similar chunks The vectorized query is then compared against our existing vectors in the database to find the most similar information.
- **Paragraph after:** The vector database returns the k (a pre-defined parameter) most similar documents/chunks (using approximate nearest neighbor search).
- **OCR:** Vector Database . Quen/ Vector QO similar vectors ANN Search space

### fig_0163 — It is expected that these retrieved documents contain information related to the

- **Page:** 116 (PDF page 118) · **Chapter:** RAG
- **BBox:** [130.50, 67.50, 481.50, 214.50] on page 612×792 pt · **Render:** 975×408 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.93) · Data Engineering (0.39) · Evaluation (0.39)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.93 → auto-accept
- **Integrity:** sha `2700cc5a37b81aa8` · dup group `dup_0159` (1)
- **Caption:** It is expected that these retrieved documents contain information related to the
- **Paragraph after:** It is expected that these retrieved documents contain information related to the query, providing a basis for the final response generation. #7) Re-rank the chunks After retrieval, the selected chunks might need further refinement to ensure the
- **OCR:** Vector Database Similar chunks ANN Search . > — s O0OOO . Query Vector QO similar vectors

### fig_0164 — #7) Re-rank the chunks

- **Page:** 116 (PDF page 118) · **Chapter:** RAG
- **BBox:** [135.75, 428.62, 476.25, 556.87] on page 612×792 pt · **Render:** 945×356 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.76) · Evaluation (0.53) · AI / ML Foundation (0.38) · Context Engineering (0.38)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.76 → review queue
- **Integrity:** sha `a2581727e097a8d9` · dup group `dup_0160` (1)
- **Heading:** #7) Re-rank the chunks
- **Caption:** This process rearranges the chunks so that the most relevant ones are prioritized
- **Paragraph before:** most relevant information is prioritized. In this re-ranking step, a more sophisticated model (often a cross-encoder) evaluates the initial list of retrieved chunks alongside the query to assign a relevance score to each chunk.
- **Paragraph after:** This process rearranges the chunks so that the most relevant ones are prioritized for the response generation. That said, not every RAG app implements this, and typically, they just rely on the similarity scores obtained in step while retrieving the relevant context from the
- **OCR:** chank 1 Cross <user auery> \| () —» exoder — score_ chunk 2 Cross oder <user auery> \| () —» ecder —p score_2 o P, Cross <user query> \| () —» @eﬂmﬁ? —» score_3 el

### fig_0165 — The LLM leverages the context provided by the chunks to generate a coherent

- **Page:** 117 (PDF page 119) · **Chapter:** RAG
- **BBox:** [133.12, 234.22, 478.88, 355.72] on page 612×792 pt · **Render:** 961×338 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.77) · Context Engineering (0.51) · Data Engineering (0.40) · LLM Engineering (0.37)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.77 → review queue
- **Integrity:** sha `2af18850266ede08` · dup group `dup_0161` (1)
- **Caption:** The LLM leverages the context provided by the chunks to generate a coherent
- **Paragraph before:** This model combines the user's original query with the retrieved chunks in a prompt template to generate a response that synthesizes information from the selected documents. This is depicted below:
- **Paragraph after:** The LLM leverages the context provided by the chunks to generate a coherent and contextually relevant answer that directly addresses the user’s query. Since chunking is the very first step in any RAG pipeline, it’s important to understand the different ways it can be done.
- **OCR:** {FTuupt temﬂaxe"i Answer this {query} based on the following context: - context 1: {chunk 1} - context 2: {chunk 2} - context N: {chunk N} Stream the response to the user — LM User

### fig_0166 — chunking strategies for RAG

- **Page:** 117 (PDF page 119) · **Chapter:** RAG
- **BBox:** [108.38, 546.34, 503.62, 717.34] on page 612×792 pt · **Render:** 1097×475 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.91) · n8n / Workflow Automation (0.40) · Data Engineering (0.40)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.91 → auto-accept
- **Integrity:** sha `debcc2cf55788b14` · dup group `dup_0162` (2)
- **Heading:** chunking strategies for RAG
- **Paragraph before:** Since chunking is the very first step in any RAG pipeline, it’s important to understand the different ways it can be done. chunking strategies for RAG Here’s the typical workflow of RAG:
- **OCR:** Additional documents eae \| T D < @ deepseek “ _@j - Final response um - /4 ®\| Similar Sielarity : documents, search _ -

### fig_0167 — Let’s understand them!

- **Page:** 118 (PDF page 120) · **Chapter:** RAG
- **BBox:** [130.12, 202.43, 481.88, 649.43] on page 612×792 pt · **Render:** 977×1241 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.96) · AI / ML Foundation (0.37) · Observability (0.37)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.96 → auto-accept
- **Integrity:** sha `28a4e4c052240baa` · dup group `dup_0163` (1)
- **Caption:** Let’s understand them!
- **Paragraph before:** wherein a large document is divided into smaller/manageable pieces. This step is crucial since it ensures the text fits the input size of the embedding model. Here are five chunking strategies for RAG:
- **Paragraph after:** Let’s understand them! 1) Fixed-size chunking
- **OCR:** ' 5 ch.lﬂkim Sfrafcgigs fol" RAG ’ \\\ blog.DailyDoseofDS.com 2 overlap 1) Fixed-size L " e chunking Chunk 1)~ irall= e N Chunk 2 ™ j:fm:r Initial first chunk keep adding new > et B e I _‘: segments until cosine 2) Eic (ssnterices or P similarity drops drastically Semal paragraghs) \|- ’ ) chunkin i 9 1 1 B «--- initial second chunk ) segment selecta document segment ____________ » cm=a _ e = 3) Recursive o scsors) e v ChUﬂkiﬂg ______ No L h‘_mi‘t? . split further recursively Document ) hunk using chunk 1 chunk 2 chunk 3 4) Document \| (7] \| U0 © = dctr Pad e - > chunk 4 chunk 5 -mmz Conclusion chunking *Merge with recursive chunking if needed J input to LLM generates S) WW-based Lt @i} e chunking E Final chunks

### fig_0168 — Since a direct split can disrupt the semantic flow, it is recommended to maintain

- **Page:** 119 (PDF page 121) · **Chapter:** RAG
- **BBox:** [101.25, 119.08, 510.75, 228.58] on page 612×792 pt · **Render:** 1137×304 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.91) · AI / ML Foundation (0.44)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.91 → auto-accept
- **Integrity:** sha `5d4f0e6936018c4b` · dup group `dup_0164` (1)
- **Caption:** Since a direct split can disrupt the semantic flow, it is recommended to maintain
- **Paragraph before:** Split the text into uniform segments based on a pre-defined number of characters, words, or tokens.
- **Paragraph after:** Since a direct split can disrupt the semantic flow, it is recommended to maintain some overlap between two consecutive chunks (the blue part above). This is simple to implement. Also, since all chunks are of equal size, it simplifies batch processing.
- **OCR:** Artificial intelligence is Chunk 1 IIIIIII!!I!!!IIIIII an \|

### fig_0169 — 2) Semantic chunking

- **Page:** 119 (PDF page 121) · **Chapter:** RAG
- **BBox:** [112.12, 422.91, 499.88, 536.16] on page 612×792 pt · **Render:** 1077×315 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.93) · AI / ML Foundation (0.42)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.93 → auto-accept
- **Integrity:** sha `e80fbac249e61a8d` · dup group `dup_0165` (1)
- **Heading:** 2) Semantic chunking
- **Caption:** Segment the document based on meaningful units like sentences, paragraphs, or
- **Paragraph before:** batch processing. But this usually breaks sentences (or ideas) in between. Thus, important information will likely get distributed between chunks. 2) Semantic chunking
- **Paragraph after:** Segment the document based on meaningful units like sentences, paragraphs, or thematic sections. Next, create embeddings for each segment. Let’s say we start with the first segment and its embedding.
- **OCR:** dsesm\eﬂ'T Initial first chunk keep adding new Document _°£u"le"_) -—— ] - = segments until cosine (sentences or ~ P similarity drops drastically ’ 2) Semantic paragraghs) chunking = E= Final chunks initial second chunk

### fig_0170 — Unlike fixed-size chunks, this maintains the natural flow of language and

- **Page:** 120 (PDF page 122) · **Chapter:** RAG
- **BBox:** [105.38, 162.86, 506.62, 267.86] on page 612×792 pt · **Render:** 1115×292 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.78) · Evaluation (0.46) · Agent Protocol Fabric (0.40) · Infrastructure (0.40)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.78 → review queue
- **Integrity:** sha `80f01ff22dcf4b81` · dup group `dup_0166` (1)
- **Caption:** Unlike fixed-size chunks, this maintains the natural flow of language and
- **Paragraph before:** This continues until cosine similarity drops significantly. The moment it does, we start a new chunk and repeat. Here’s what the output could look like:
- **Paragraph after:** Unlike fixed-size chunks, this maintains the natural flow of language and preserves complete ideas. Since each chunk is richer, it improves the retrieval accuracy, which, in turn, produces more coherent and relevant responses by the LLM.
- **OCR:** Artificial intelligence is transforming industries by automating processes, enhancing decision-making, and providing insights through data analysis. Machine learning, a subset of AI, enables systems to learn and improve from experience without explicit programming. Deep learning, a branch of machine learning, uses neural networks with multiple layers to model complex patterns in data.

### fig_0171 — 3) Recursive chunking

- **Page:** 120 (PDF page 122) · **Chapter:** RAG
- **BBox:** [122.62, 462.20, 489.38, 578.45] on page 612×792 pt · **Render:** 1019×323 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.98)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `952d33db7fb4e2ff` · dup group `dup_0167` (1)
- **Heading:** 3) Recursive chunking
- **Caption:** First, chunk based on inherent separators like paragraphs, or sections.
- **Paragraph before:** produces more coherent and relevant responses by the LLM. A minor problem is that it depends on a threshold to determine if cosine similarity has dropped significantly, which can vary from document to document. 3) Recursive chunking
- **Paragraph after:** First, chunk based on inherent separators like paragraphs, or sections. Next, split each chunk into smaller chunks if the size exceeds a pre-defined chunk size limit. If, however, the chunk fits the chunk-size limit, no further splitting is done.
- **OCR:** 3) Recursive chunking segment document (paragraghs or thematic sections) select a segment split further recursively size > chunk-size limit? v =

### fig_0172 — As shown above:

- **Page:** 121 (PDF page 123) · **Chapter:** RAG
- **BBox:** [118.50, 67.50, 493.50, 237.75] on page 612×792 pt · **Render:** 1041×473 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.94) · Agent Protocol Fabric (0.41)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.94 → auto-accept
- **Integrity:** sha `d1f20c5ae4fd961a` · dup group `dup_0168` (1)
- **Caption:** As shown above:
- **Paragraph after:** As shown above: First, we define two chunks (the two paragraphs in purple). Next, paragraph is further split into smaller chunks. Unlike fixed-size chunks, this approach also maintains the natural flow of
- **OCR:** Paragraph 1 Artificial intelligence is transforming industries by automating processes, enhancing decision-making, and providing insights through data analysis Paragraph 2 AI is also improving natural language processing, enabling applications like chatbots and virtual assistants.

### fig_0173 — 4) Document structure-based chunking

- **Page:** 121 (PDF page 123) · **Chapter:** RAG
- **BBox:** [114.75, 475.87, 497.25, 590.62] on page 612×792 pt · **Render:** 1063×319 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.94) · Observability (0.38) · Infrastructure (0.38)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.94 → auto-accept
- **Integrity:** sha `5318af88b042af5f` · dup group `dup_0169` (1)
- **Heading:** 4) Document structure-based chunking
- **Caption:** It utilizes the inherent structure of documents, like headings, sections, or
- **Paragraph before:** language and preserves complete ideas. However, there is some extra overhead in terms of implementation and computational complexity. 4) Document structure-based chunking
- **Paragraph after:** It utilizes the inherent structure of documents, like headings, sections, or paragraphs, to define chunk boundaries. This way, it maintains structural integrity by aligning with the document’s logical sections. Here’s what the output could look like:
- **OCR:** 4) Document structure- based chunking chunk using the inherent structure chunk 1 chunk 2 chunk 4 chunk 5 Section #2 Conclusion *Merge with recursive chunking if needed

### fig_0174 — That said, this approach assumes that the document has a clear structure, which

- **Page:** 122 (PDF page 124) · **Chapter:** RAG
- **BBox:** [123.00, 67.50, 489.00, 309.00] on page 612×792 pt · **Render:** 1017×671 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.81) · Agent Protocol Fabric (0.44) · AI / ML Foundation (0.40) · n8n / Workflow Automation (0.40)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.81 → review queue
- **Integrity:** sha `fafc61ac09fabcaa` · dup group `dup_0170` (1)
- **Caption:** That said, this approach assumes that the document has a clear structure, which
- **Paragraph after:** That said, this approach assumes that the document has a clear structure, which may not be true. Also, chunks may vary in length, possibly exceeding model token limits. You can try merging it with recursive splitting.
- **OCR:** Title: The Role of Artificial Intelligence in Modern Education Chunk 1 Introduction Artificial intelligence (AI) is reshaping education by providing chlink;2 personalized learning experiences and automating administrative tasks. Section 1: Personalized Learning Chunk 3 AI enables the customization of educational content to meet individual student needs, enhancing engagement and comprehension. Section 2: Administrative Automation Chunk 4 From grading to scheduling, AI tools are streamlining administrative processes, allowing educators to focus more on teaching. Conclusion Chunk 5 The integration of AI in education holds the promise of more efficient learning environments and improved student outcomes.

### fig_0175 — 5) LLM-based chunking

- **Page:** 122 (PDF page 124) · **Chapter:** RAG
- **BBox:** [109.88, 451.77, 502.12, 529.77] on page 612×792 pt · **Render:** 1089×217 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.81) · LLM Engineering (0.44) · AI / ML Foundation (0.40) · Context Engineering (0.40)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.81 → review queue
- **Integrity:** sha `51c8a5b7ac1ea834` · dup group `dup_0171` (1)
- **Heading:** 5) LLM-based chunking
- **Caption:** Prompt the LLM to generate semantically isolated and meaningful chunks.
- **Paragraph before:** may not be true. Also, chunks may vary in length, possibly exceeding model token limits. You can try merging it with recursive splitting. 5) LLM-based chunking
- **Paragraph after:** Prompt the LLM to generate semantically isolated and meaningful chunks. This method ensures high semantic accuracy since the LLM can understand context and meaning beyond simple heuristics (used in the above four approaches).
- **OCR:** input to LLM generates S) LLM-based chunking Final chunks

### fig_0176 — Two important parameters guide this decision:

- **Page:** 124 (PDF page 126) · **Chapter:** RAG
- **BBox:** [122.25, 67.50, 489.75, 272.25] on page 612×792 pt · **Render:** 1021×569 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.84) · LLM Engineering (0.51)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.84 → review queue
- **Integrity:** sha `61e7c1a9fb423a5a` · dup group `dup_0172` (1)
- **Caption:** Two important parameters guide this decision:
- **Paragraph after:** Two important parameters guide this decision: ● The amount of external knowledge required for your task. ● The amount of adaptation you need. Adaptation, in this case, means
- **OCR:** External knowledge required Prompt engineering \|\| Fne-kuning Model adaptation required

### fig_0177 — RAG architectures

- **Page:** 125 (PDF page 127) · **Chapter:** RAG
- **BBox:** [142.12, 230.25, 469.88, 611.25] on page 612×792 pt · **Render:** 911×1058 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.65) · LLM Engineering (0.52) · Software Architecture (0.45) · AI / ML Foundation (0.42)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.65 → review queue
- **Integrity:** sha `9c5f3ffe5936c647` · dup group `dup_0173` (1)
- **Heading:** RAG architectures
- **Caption:** Let’s discuss them briefly:
- **Paragraph before:** the right RAG architecture for your use case. RAG architectures We prepared the following visual that details types of RAG architectures used in AI systems:
- **Paragraph after:** Let’s discuss them briefly: 1) Naive RAG
- **OCR:** - 2-7c 8 Avchitectures \| iy Prompt Template Corrective RAG R SFR 9 5 iy User Embedding Anotuder \| \| User Query ? Query () Correct Tfo >+ m foltor 08 i i +— Gy — B Prompt Template Adaptive RAG “2"" v Prompt Template s 2 Prompt Template Quer Quary Analyzer Outpute—— @88 ! wm Prompt Template - mcp.DailyDoseofDS.com Hypothatical Datoa Response Sources Embedding l Prompt Template Data Sources D 3 b ® Embedding Genatator Vvect3r'oe Graph DB Conant 1 c.p..k 2 ousn— @ M Prompt Template Locol Data T Search Engine Clovd Engine

### fig_0178 — RAG vs Agentic RAG

- **Page:** 127 (PDF page 129) · **Chapter:** RAG
- **BBox:** [138.00, 544.84, 474.00, 691.84] on page 612×792 pt · **Render:** 933×408 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.85) · Agentic AI (0.43) · LLM Engineering (0.39) · n8n / Workflow Automation (0.39)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.85 → auto-accept
- **Integrity:** sha `5de6af8da02a18b5` · dup group `dup_0174` (2)
- **Heading:** RAG vs Agentic RAG
- **Paragraph before:** Best suited for complex workflows that require tool use, external APIs, or combining multiple RAG techniques. RAG vs Agentic RAG These are some issues with the traditional RAG system :
- **OCR:** RAG Additional documents \| = = - Response 4 : Similarity 3 search . e m——— Encode Prompt 6 i 9 Vector database 7 1 Similar : documents v

### fig_0179 — Agentic RAG

- **Page:** 128 (PDF page 130) · **Chapter:** RAG
- **BBox:** [129.75, 337.67, 482.25, 583.67] on page 612×792 pt · **Render:** 979×684 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.66) · Agentic AI (0.61) · Agent Protocol Fabric (0.40) · LLM Engineering (0.37)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.66 → review queue
- **Integrity:** sha `71712fd50e732b07` · dup group `dup_0175` (1)
- **Heading:** Agentic RAG
- **Caption:** Note: The diagram above is one of many blueprints that an agentic RAG system may
- **Paragraph before:** Due to this, Agentic RAG is becoming increasingly popular. Let's understand this in more detail. Agentic RAG The workflow of agentic RAG is depicted below:
- **Paragraph after:** Note: The diagram above is one of many blueprints that an agentic RAG system may possess. You can adapt it according to your specific use case. As shown above, the idea is to introduce agentic behaviors at each stage of RAG. Think of agents as someone who can actively think through a task - planning,
- **OCR:** Agentic RAG Is the answer relevant? Final response. LLM Agent & \| Rewrite the initial query LLM Agent & Do I need {3 > -—=> Updated u e 1 more details? 1 Prompt v Response. 3 LLM S Which source. will help? i A : v \| Vector Tools & 704 ~ database APIs -

### fig_0180 — Traditional RAG vs HyDE

- **Page:** 130 (PDF page 132) · **Chapter:** RAG
- **BBox:** [141.00, 172.67, 471.00, 280.67] on page 612×792 pt · **Render:** 917×300 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.81) · Context Engineering (0.43) · Evaluation (0.43) · Agentic AI (0.39)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.81 → review queue
- **Integrity:** sha `c6bb2312ef7c6f1f` · dup group `dup_0176` (2)
- **Heading:** Traditional RAG vs HyDE
- **Caption:** As a result, several irrelevant contexts get retrieved during the retrieval step due
- **Paragraph before:** Traditional RAG vs HyDE Another critical problem with the traditional RAG system is that questions are not semantically similar to their answers.
- **Paragraph after:** As a result, several irrelevant contexts get retrieved during the retrieval step due to a higher cosine similarity than the documents actually containing the answer. HyDE solves this. The following visual depicts how it differs from traditional RAG and HyDE.
- **OCR:** What is A— High Eﬂachine learning? . ]stmilarity What is Machine learning\| Low Machine learning? is fun similarity

### fig_0181 — Let's understand this in more detail.

- **Page:** 131 (PDF page 133) · **Chapter:** RAG
- **BBox:** [131.25, 67.50, 480.75, 463.50] on page 612×792 pt · **Render:** 971×1100 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.82) · AI / ML Foundation (0.42) · Context Engineering (0.42) · LLM Engineering (0.39)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.82 → review queue
- **Integrity:** sha `eb47ee9dfc595bdc` · dup group `dup_0177` (1)
- **Caption:** Let's understand this in more detail.
- **Paragraph after:** Let's understand this in more detail. As mentioned earlier, questions are not semantically similar to their answers, which leads to several irrelevant contexts during retrieval. HyDE handles this as follows:
- **OCR:** ' Traditional RAG vs. HYDE 2 RAG &) Additional Encoae documents _————> Embedding model LLM ~ iz Vector Index i database o ® imilari Similar S;T::z:y ’,’ e ; documents HyDE 1) Additional \| __ Encode. documents \| — - - ! prompt: Write a P‘W’ about 3 P Embedding model (Contriever), 5 Encode \| Hypothetical text Response A Similarity /' search _- Similar documents Retrieved context

### fig_0182 — HyDE handles this as follows:

- **Page:** 131 (PDF page 133) · **Chapter:** RAG
- **BBox:** [131.25, 554.38, 480.75, 668.38] on page 612×792 pt · **Render:** 971×317 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.78) · Context Engineering (0.46) · Evaluation (0.46)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.78 → review queue
- **Integrity:** sha `51c489ab6bbfe99a` · dup group `dup_0176` (2)
- **Caption:** HyDE handles this as follows:
- **Paragraph before:** Let's understand this in more detail. As mentioned earlier, questions are not semantically similar to their answers, which leads to several irrelevant contexts during retrieval.
- **Paragraph after:** HyDE handles this as follows:
- **OCR:** @ Wk 1 What is AT? j High achine learning? similarity What is Machine learning\| Low Machine learning? is fun similarity

### fig_0183 — Now, of course, the hypothetical generated will likely contain hallucinated

- **Page:** 132 (PDF page 134) · **Chapter:** RAG
- **BBox:** [117.38, 285.78, 494.62, 374.28] on page 612×792 pt · **Render:** 1047×246 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.78) · Context Engineering (0.46) · AI / ML Foundation (0.40) · LLM Engineering (0.40)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.78 → review queue
- **Integrity:** sha `d7c92281f28c0c8f` · dup group `dup_0178` (1)
- **Caption:** Now, of course, the hypothetical generated will likely contain hallucinated
- **Paragraph before:** Use the embedding E to query the vector database and fetch relevant context (C). Pass the hypothetical answer H + retrieved-context C + query Q to the LLM to produce an answer. Done!
- **Paragraph after:** Now, of course, the hypothetical generated will likely contain hallucinated details. But this does not severely affect the performance due to the contriever model - one which embeds.
- **OCR:** o e . -- > Prompt: Write a passage about <query> LLM Hypothetical text

### fig_0184 — Several studies have shown that HyDE improves the retrieval performance

- **Page:** 132 (PDF page 134) · **Chapter:** RAG
- **BBox:** [111.00, 607.89, 501.00, 667.89] on page 612×792 pt · **Render:** 1083×167 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.76) · AI / ML Foundation (0.47) · Evaluation (0.43) · Tool / Action Fabric (0.39)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.76 → review queue
- **Integrity:** sha `3906bfaacd8e0125` · dup group `dup_0179` (1)
- **Caption:** Several studies have shown that HyDE improves the retrieval performance
- **Paragraph before:** functions as a near-lossless compressor whose task is to filter out the hallucinated details of the fake document. This produces a vector embedding that is expected to be more similar to the embeddings of actual documents than the question is to the real documents:
- **Paragraph after:** Several studies have shown that HyDE improves the retrieval performance compared to the traditional embedding model.
- **OCR:** cosine(E§ § Query Real docs ) <LK cosine( Real docs

### fig_0185 — vs. RAG

- **Page:** 133 (PDF page 135) · **Chapter:** RAG
- **BBox:** [143.62, 200.50, 468.38, 593.50] on page 612×792 pt · **Render:** 903×1092 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.64) · AI / ML Foundation (0.60) · Observability (0.42) · Business Automation (0.39)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.64 → review queue
- **Integrity:** sha `56d2c6ed946e1ec7` · dup group `dup_0180` (1)
- **Heading:** vs. RAG
- **Caption:** All three techniques are used to augment the knowledge of an existing model
- **Paragraph before:** But this comes at the cost of increased latency and more LLM usage. Full-model Fine-tuning vs. LoRA vs. RAG
- **Paragraph after:** All three techniques are used to augment the knowledge of an existing model with additional data. 1) Full fine-tuning
- **OCR:** \| Full Fine Tuning, LorA and RAG blog.DailyDoseofDS.com Gradient flow - O Full pre-trained network LoRA Fine Tuning Gradient flow < Additional ‘ LoRA layers <~—— No gradient flow O Full pre-trained network documents \| = o Response - > \| Embedding model 3! Encode 5t Similar - 1 documents

### fig_0186 — While this fine-tuning technique has been successfully used for a long time,

- **Page:** 134 (PDF page 136) · **Chapter:** RAG
- **BBox:** [113.25, 119.08, 498.75, 222.58] on page 612×792 pt · **Render:** 1071×288 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.68) · RAG / Knowledge Engineering (0.68)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.68 → review queue
- **Integrity:** sha `2973c98168fed25f` · dup group `dup_0181` (1)
- **Caption:** While this fine-tuning technique has been successfully used for a long time,
- **Paragraph before:** Fine-tuning means adjusting the weights of a pre-trained model on a new dataset for better performance.
- **Paragraph after:** While this fine-tuning technique has been successfully used for a long time, problems arise when we use it on much larger models — LLMs, for instance, primarily because of: Their size.
- **OCR:** < =- Gradient flow Full Fine o(—fi;’j{:)(‘ Tuning Ly @) Full pre-trained network

### fig_0187 — The idea is to train only the LoRA network and freeze the large model.

- **Page:** 135 (PDF page 137) · **Chapter:** RAG
- **BBox:** [100.88, 67.50, 511.12, 273.75] on page 612×792 pt · **Render:** 1139×573 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.72) · RAG / Knowledge Engineering (0.63)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.72 → review queue
- **Integrity:** sha `efb960698497413d` · dup group `dup_0182` (2)
- **Caption:** The idea is to train only the LoRA network and freeze the large model.
- **Paragraph after:** The idea is to train only the LoRA network and freeze the large model. Looking at the above visual, you might think: But the LoRA model has more neurons than the original model. How does that help?
- **OCR:** LoRA Fine Tuning < -~ Gradient flow N <—— No gradient flow 4

### fig_0188 — Looking at the above visual, it is pretty clear that the LoRA network has

- **Page:** 136 (PDF page 138) · **Chapter:** RAG
- **BBox:** [105.75, 67.50, 506.25, 268.50] on page 612×792 pt · **Render:** 1113×558 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.70) · AI / ML Foundation (0.59) · Evaluation (0.41)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.70 → review queue
- **Integrity:** sha `691586afb5bb4093` · dup group `dup_0182` (2)
- **Caption:** Looking at the above visual, it is pretty clear that the LoRA network has
- **Paragraph after:** Looking at the above visual, it is pretty clear that the LoRA network has relatively very few connections. 3) RAG Retrieval augmented generation (RAG) is another pretty cool way to augment
- **OCR:** < -~ Gradient flow C Additional @ LoRA layers LoRA Fine Tuning <~—— No gradient flow O Full pre-trained network

### fig_0189 — 3) RAG

- **Page:** 136 (PDF page 138) · **Chapter:** RAG
- **BBox:** [112.88, 462.83, 499.12, 631.58] on page 612×792 pt · **Render:** 1073×469 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.81) · AI / ML Foundation (0.44) · Data Engineering (0.40) · Evaluation (0.40)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.81 → review queue
- **Integrity:** sha `e56de6b5dccece55` · dup group `dup_0174` (2)
- **Heading:** 3) RAG
- **Caption:** There are steps, which are also marked in the above visual:
- **Paragraph before:** Retrieval augmented generation (RAG) is another pretty cool way to augment neural networks with additional information, without having to fine-tune the model. This is illustrated below:
- **Paragraph after:** There are steps, which are also marked in the above visual: Step 1-2: Take additional data, and dump it in a vector database after embedding. (This is only done once. If the data is evolving, just keep dumping the
- **OCR:** RAG Additional I documents Response Similarity search . ’ Similar documents

### fig_0190 — Retrieval: Accessing and retrieving information from a knowledge source, such as

- **Page:** 137 (PDF page 139) · **Chapter:** RAG
- **BBox:** [97.88, 285.78, 514.12, 476.28] on page 612×792 pt · **Render:** 1157×529 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.80) · Evaluation (0.45) · Context Engineering (0.41) · AI / ML Foundation (0.38)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.80 → review queue
- **Integrity:** sha `d3f0071f40cefe79` · dup group `dup_0183` (1)
- **Caption:** Retrieval: Accessing and retrieving information from a knowledge source, such as
- **Paragraph before:** query. Step 6-7: Provide the original query and the retrieved documents (for more context) to the LLM to get a response. In fact, even its name entirely justifies what we do with this technique:
- **Paragraph after:** Retrieval: Accessing and retrieving information from a knowledge source, such as a database or memory. Augmented: Enhancing or enriching something, in this case, the text generation process, with additional information or context.
- **OCR:** RAG Additional documents \| — > \| Embedding model 4 Similarity T 1 Similar . ! de ts search . sl v Retrieval Augme_n'teo(

### fig_0191 — Essentially, instead of feeding the LLM every chunk and every token, REFRAG

- **Page:** 139 (PDF page 141) · **Chapter:** RAG
- **BBox:** [117.75, 67.50, 494.25, 507.00] on page 612×792 pt · **Render:** 1045×1221 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.74) · AI / ML Foundation (0.47) · Agent Protocol Fabric (0.45) · Context Engineering (0.40)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.74 → review queue
- **Integrity:** sha `ab56278db9463084` · dup group `dup_0184` (1)
- **Caption:** Essentially, instead of feeding the LLM every chunk and every token, REFRAG
- **Paragraph after:** Essentially, instead of feeding the LLM every chunk and every token, REFRAG compresses and filters context at a vector level: ● Chunk compression: Each chunk is encoded into a single compressed embedding, rather than hundreds of token embeddings.
- **OCR:** \|RAG vs MetaAI's REFRAG i roowonsen Additional documents RAG Additional 1\| Encode full user query User Query 1 (3).y Embed deepseek

### fig_0192 — Here’s how it works in simple terms:

- **Page:** 141 (PDF page 143) · **Chapter:** RAG
- **BBox:** [121.88, 234.21, 490.12, 567.96] on page 612×792 pt · **Render:** 1023×927 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.81) · Data Engineering (0.42) · Software Architecture (0.42) · Context Engineering (0.40)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.81 → review queue
- **Integrity:** sha `393bcd5ee8888385` · dup group `dup_0185` (1)
- **Caption:** Here’s how it works in simple terms:
- **Paragraph before:** Cache-Augmented Generation (CAG) fixes this. It lets the model “remember” stable information by caching it directly in the model’s key-value memory. And you can take this one step ahead by fusing RAG and CAG as depicted below:
- **Paragraph after:** Here’s how it works in simple terms: ● In a regular RAG setup, your query goes to the vector database, retrieves relevant chunks, and feeds them to the LLM. ●
- **OCR:** RAG vs CAG RAG RAG + CAG Retrieval Augmented Generation Retrieval Augmented Generation + Cache Augmented Generation € ) (s @ A N . ONORONEO) QL/ - % Data N/ Data Data 4 uery @ Embedding Model /8 o \ : C) Vector DB LLM(Preprocessing) Vectors Vectors Vectors @ & ) ®) Retrieved Context KV cache of Context Vector DB =) LM (Respnnse Generation) Final Response

### fig_0193 — RAG (2020-2023):

- **Page:** 143 (PDF page 145) · **Chapter:** RAG
- **BBox:** [123.75, 67.50, 488.25, 406.50] on page 612×792 pt · **Render:** 1013×942 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.68) · Agentic AI (0.51) · Context Engineering (0.43) · Agent Memory (0.43)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.68 → review queue
- **Integrity:** sha `e8e1d81248cc4739` · dup group `dup_0186` (1)
- **Caption:** RAG (2020-2023):
- **Paragraph after:** RAG (2020-2023): ● Retrieve info once, generate response ● No decision-making, just fetch and answer ●
- **OCR:** The Evolution: RAG vs Agentic RAG Vs Al Memory RAG \| Agentic RAG \| Al Memory i /R * \| \v,' Embedding Model 1 LLM [Agent) \| @ Vectors Vector DB Context Memory Store Context \| Context i N — (@ LLM (Agent) i LLM Agent) (&) LLM [Agent) (=] : - 1 i\ A\, ( ) ! /) Final Response Final Response

### fig_0194 — What is Context Engineering?

- **Page:** 146 (PDF page 148) · **Chapter:** Context Engineering
- **BBox:** [114.75, 307.61, 497.25, 474.11] on page 612×792 pt · **Render:** 1063×462 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.64) · Context Engineering (0.57) · Evaluation (0.46) · Agentic AI (0.39)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.64 → review queue
- **Integrity:** sha `e2dcbbd569365973` · dup group `dup_0162` (2)
- **Heading:** What is Context Engineering?
- **Caption:** Thus:
- **Paragraph before:** Here’s the current problem: Most AI agents (or LLM apps) fail not because the models are bad, but because they lack the right context to succeed. For instance, a RAG workflow is typically 80% retrieval and 20% generation.
- **Paragraph after:** Thus: ● Good retrieval could still work with a weak LLM. ● But bad retrieval can NEVER work even with the best of LLMs.
- **OCR:** RAG Additional documents response deepseck M @' Sl ! documents U Y Retrieved context

### fig_0195 — Context engineering involves creating dynamic systems that offer:

- **Page:** 147 (PDF page 149) · **Chapter:** Context Engineering
- **BBox:** [151.88, 67.50, 460.12, 344.25] on page 612×792 pt · **Render:** 857×769 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Context Engineering (0.78) · LLM Engineering (0.49) · Tool / Action Fabric (0.42)
- **Primary branch:** context-engineering · **Confidence:** 0.78 → review queue
- **Integrity:** sha `d5300bf39597e55b` · dup group `dup_0187` (2)
- **Caption:** Context engineering involves creating dynamic systems that offer:
- **Paragraph after:** Context engineering involves creating dynamic systems that offer: ● The right information ● The right tools
- **OCR:** Context Enlg'ineerivtg Prompt Engineering State/ History B - = =) LS JSON Structured Outputs

### fig_0196 — Smart tool access: If your AI needs external information or actions, give it the

- **Page:** 148 (PDF page 150) · **Chapter:** Context Engineering
- **BBox:** [129.00, 67.50, 483.00, 246.00] on page 612×792 pt · **Render:** 983×496 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Context Engineering (0.59) · Tool / Action Fabric (0.59) · Agent Memory (0.47) · RAG / Knowledge Engineering (0.41)
- **Primary branch:** context-engineering · **Confidence:** 0.59 → review queue
- **Integrity:** sha `71da6ed6a14cf6fd` · dup group `dup_0188` (1)
- **Caption:** Smart tool access: If your AI needs external information or actions, give it the
- **Paragraph after:** Smart tool access: If your AI needs external information or actions, give it the right tools. Format the outputs so they're maximally digestible. Memory management: ●
- **OCR:** Documents & P2 0l Database .] 2 Tools/APIs&Rp - - “h Memory - ] \| A\ B o) Response sy ey s e e e s Context-engineered LLM app ~

### fig_0197 — To understand context engineering, it's essential to first understand the meaning

- **Page:** 149 (PDF page 151) · **Chapter:** Context Engineering
- **BBox:** [130.88, 67.50, 481.12, 356.25] on page 612×792 pt · **Render:** 973×802 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Context Engineering (0.80) · LLM Engineering (0.43) · Agentic AI (0.41) · Agent Protocol Fabric (0.41)
- **Primary branch:** context-engineering · **Confidence:** 0.80 → review queue
- **Integrity:** sha `9e71001284da138e` · dup group `dup_0189` (1)
- **Caption:** To understand context engineering, it's essential to first understand the meaning
- **Paragraph after:** To understand context engineering, it's essential to first understand the meaning of context. Agents today have evolved into much more than just chatbots. The graphic below summarizes the types of contexts an agent needs to function
- **OCR:** [Context engineering is the] ”...delicate art and science of filling the context window with just the right information for the next step.” ) Andrej Karpathy & +1 for "context engineering" over "prompt engineering". People associate prompts with short task descriptions you'd give an LLM in your day-to-day use. When in every industrial-strength LLM app, context engineering is the delicate art and science of filling the context window Show more 3 tobi lutke @ B I really like the term “context engineering” over prompt engineering. It describes the core skill better: the art of providing all the context for the task to be plausibly solvable by the LLM.

### fig_0198 — ● Instructions

- **Page:** 150 (PDF page 152) · **Chapter:** Context Engineering
- **BBox:** [96.00, 67.50, 516.00, 355.50] on page 612×792 pt · **Render:** 1167×800 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Context Engineering (0.54) · Tool / Action Fabric (0.54) · Agent Memory (0.50) · Agentic AI (0.46)
- **Primary branch:** context-engineering · **Confidence:** 0.54 → review queue
- **Integrity:** sha `35e483473dd8c7b7` · dup group `dup_0190` (1)
- **Caption:** ● Instructions
- **Paragraph after:** ● Instructions ● Examples ●
- **OCR:** 6 Types of context for AT Agents o N D D 4 ® @ ® © INstructions (&) Knowledge Memory Tools Guardrails +%» Role — — — —> Define a persona for the LLM, eg. coding agent, PM 1 ~ —> Objective — —» Clearly define what needs to be achieved 1 1 (> Define steps, conventions and constraints ( - -> Requirements — > Response format (JSON, XML, plain text) \| Behaviour \| — = Eg. of how to think through a problem ! > Responses — —> Eg. of how the response should look like ,»> External — — > General context, background, domain specifics \| \| > Material need for the specific task > - > Eg. docs, APT specs, workflow schema etc. \| > Short-term — — > Memory of what happens in a user session ! > Long-term — - > Dedicated storage to remember stuff across sessions + > Description — —» Description of what the tool does 1 = > Parameters — - > Tool inputs, their types, required or not ' > Results — —»>Outputs of

### fig_0199 — ● If LLM is a CPU.

- **Page:** 151 (PDF page 153) · **Chapter:** Context Engineering
- **BBox:** [141.38, 67.50, 470.62, 307.50] on page 612×792 pt · **Render:** 915×667 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Context Engineering (0.85) · Agent Protocol Fabric (0.45) · Tool / Action Fabric (0.40)
- **Primary branch:** context-engineering · **Confidence:** 0.85 → auto-accept
- **Integrity:** sha `c4813038cede13b7` · dup group `dup_0191` (1)
- **Caption:** ● If LLM is a CPU.
- **Paragraph after:** ● If LLM is a CPU. ● Then the context window is the RAM. You're essentially programming the "RAM" with the perfect instructions for your
- **OCR:** \|What is Context Engineering? Tupes Context LLM (CPU) of Context __Enaineering Context window (RAM) ‘{{ Tools 20 E}S(ei mcpDailyDoseOFDS.com

### fig_0200 — ● Writing Context

- **Page:** 152 (PDF page 154) · **Chapter:** Context Engineering
- **BBox:** [111.38, 67.50, 500.62, 456.75] on page 612×792 pt · **Render:** 1081×1081 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Context Engineering (0.76) · Agent Memory (0.49) · Tool / Action Fabric (0.42) · AI / ML Foundation (0.38)
- **Primary branch:** context-engineering · **Confidence:** 0.76 → review queue
- **Integrity:** sha `8a4fead9aac6d0dc` · dup group `dup_0192` (1)
- **Caption:** ● Writing Context
- **Paragraph after:** ● Writing Context ● Selecting Context ●
- **OCR:** \| Context Engineering for Agents 1X; s Write Context (persists across sessions) (persists within a session) (a runtime state object) Tools Long-term Memory Short-term Memory Knowledge < AN x O i Read L - ’ ' Context . \ ! ) Compress Context LM Summavrizer Smaller Context (lesser tokens) Isolate Context Sandbox env.

### fig_0201 — You can do so by writing it to:

- **Page:** 153 (PDF page 155) · **Chapter:** Context Engineering
- **BBox:** [106.88, 67.50, 505.12, 173.25] on page 612×792 pt · **Render:** 1107×294 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Context Engineering (0.68) · Agent Memory (0.68)
- **Primary branch:** context-engineering · **Confidence:** 0.68 → review queue
- **Integrity:** sha `becb6210e2cb003a` · dup group `dup_0193` (1)
- **Caption:** You can do so by writing it to:
- **Paragraph after:** You can do so by writing it to: ● Long-term memory (persists across sessions) ● Short-term memory (persists within a session)
- **OCR:** Write Context (persists across sessions) (persists within a session) (a runtime state object)

### fig_0202 — 2) Read context

- **Page:** 153 (PDF page 155) · **Chapter:** Context Engineering
- **BBox:** [100.50, 367.58, 511.50, 474.83] on page 612×792 pt · **Render:** 1141×297 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Context Engineering (0.76) · Agent Memory (0.51) · Agentic AI (0.39) · Tool / Action Fabric (0.39)
- **Primary branch:** context-engineering · **Confidence:** 0.76 → review queue
- **Integrity:** sha `2f391a48742b349e` · dup group `dup_0194` (1)
- **Heading:** 2) Read context
- **Caption:** Now this context can be pulled from:
- **Paragraph before:** A state object 2) Read context Reading context means pulling it into the context window to help an agent perform a task.
- **Paragraph after:** Now this context can be pulled from: ● A tool ●
- **OCR:** Long-term Memory Short-term Memory Knowledge

### fig_0203 — The retrieved context may contain duplicate or redundant information

- **Page:** 154 (PDF page 156) · **Chapter:** Context Engineering
- **BBox:** [97.50, 67.50, 514.50, 176.25] on page 612×792 pt · **Render:** 1159×302 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Context Engineering (0.78) · AI / ML Foundation (0.44) · RAG / Knowledge Engineering (0.44) · Agentic AI (0.39)
- **Primary branch:** context-engineering · **Confidence:** 0.78 → review queue
- **Integrity:** sha `6367c576b5c22f67` · dup group `dup_0195` (1)
- **Caption:** The retrieved context may contain duplicate or redundant information
- **Paragraph after:** The retrieved context may contain duplicate or redundant information (multi-turn tool calls), leading to extra tokens & increased cost. Context summarization helps here. 4) Isolating context
- **OCR:** Compress Context Smaller Context Context (lesser tokens) LLM Summarizer

### fig_0204 — 4) Isolating context

- **Page:** 154 (PDF page 156) · **Chapter:** Context Engineering
- **BBox:** [102.75, 331.01, 509.25, 436.76] on page 612×792 pt · **Render:** 1129×294 px
- **Composition:** raster · **Role:** code · **Quality:** 0.6
- **Mapping:** Context Engineering (0.69) · Agentic AI (0.49) · Tool / Action Fabric (0.45) · Security (0.42)
- **Primary branch:** context-engineering · **Confidence:** 0.69 → review queue
- **Integrity:** sha `013d65129f71b9cb` · dup group `dup_0196` (1)
- **Heading:** 4) Isolating context
- **Caption:** Some popular ways to do so are:
- **Paragraph before:** (multi-turn tool calls), leading to extra tokens & increased cost. Context summarization helps here. 4) Isolating context Isolating context involves splitting it up to help an agent perform a task.
- **Paragraph after:** Some popular ways to do so are: ● Using multiple agents (or sub-agents), each with its own context ● Using a sandbox environment for code storage and execution
- **OCR:** Context Isolate Context Sandbox env.

### fig_0205 — Agents

- **Page:** 155 (PDF page 157) · **Chapter:** Context Engineering
- **BBox:** [98.25, 388.80, 513.75, 711.30] on page 612×792 pt · **Render:** 1155×895 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Context Engineering (0.62) · Agentic AI (0.51) · Tool / Action Fabric (0.49) · LLM Engineering (0.43)
- **Primary branch:** context-engineering · **Confidence:** 0.62 → review queue
- **Integrity:** sha `f4506034cd06dfb3` · dup group `dup_0197` (1)
- **Heading:** Agents
- **Paragraph before:** And all advanced agent architectures now treat context as a multi-dimensional design layer, not a line in a prompt. Here’s the mental model to use when you think about the types of contexts for Agents:
- **OCR:** To call a function, an LLM issves a special format interpreted by the system (i’s like saying: Please call this tool with these parameters). Next, an orchestration layer responds by attaching a special message to the messages list. A specal uncions” block n the LLM contert window. 1t does consume your input tokens ‘and offects the performance. Traat tool descrptions as wicro- prompts that auide agents’ reasoning, Descriptions provided by MCP servors. are often insufficient i you do not consider your spedific dowain context. Type — Is it required Semantic (facts, preferences, __ userfcompany knowledae) Episodic (experiences, past interactions) Procedural (instructions captured from previous interactions) Stored in database or file system Memory is not part of the prompt you can type. It can be: Aotomatically Accessed ottached by the s a tool orchestration lager eg, Scratchpad (PHD Think T

### fig_0206 — workflow

- **Page:** 157 (PDF page 159) · **Chapter:** Context Engineering
- **BBox:** [117.00, 399.31, 495.00, 706.06] on page 612×792 pt · **Render:** 1050×852 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Context Engineering (0.61) · RAG / Knowledge Engineering (0.51) · Agentic AI (0.48) · Agent Memory (0.45)
- **Primary branch:** context-engineering · **Confidence:** 0.61 → review queue
- **Integrity:** sha `392ee592d6019dc8` · dup group `dup_0198` (1)
- **Heading:** workflow
- **Paragraph before:** We'll build a multi-agent research assistant using context engineering principles. This Agent will gather its context across sources: Documents, Memory, Web search, and Arxiv. Here’s our workflow:
- **OCR:** (AT R LTI Workflow \| mepoaitposeors.com Orchestrated with @l vector DB Parallel Execution Firecrawl web search gl web contet @ Retrieved context e Retrieved \| ] a Retrieved context Aggregated memory context Filtered Evaluator \| Fheered ‘agent @ Display to user Agentic Memory Structured

### fig_0207 — CE involves creating dynamic systems that offer:

- **Page:** 158 (PDF page 160) · **Chapter:** Context Engineering
- **BBox:** [127.50, 352.94, 484.50, 673.94] on page 612×792 pt · **Render:** 991×892 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Context Engineering (0.61) · LLM Engineering (0.48) · RAG / Knowledge Engineering (0.48) · Agent Orchestration (0.48)
- **Primary branch:** context-engineering · **Confidence:** 0.61 → review queue
- **Integrity:** sha `dad46ca8f8500efd` · dup group `dup_0187` (2)
- **Caption:** CE involves creating dynamic systems that offer:
- **Paragraph before:** ● Milvus for vector DB ● CrewAI for orchestration Let's go!
- **Paragraph after:** CE involves creating dynamic systems that offer:
- **OCR:** Context Enéineering RAG Prompt Engineering State/ History a JSON Structured Outputs

### fig_0208 — #1) Crew flow

- **Page:** 159 (PDF page 161) · **Chapter:** Context Engineering
- **BBox:** [130.88, 266.32, 481.12, 596.32] on page 612×792 pt · **Render:** 973×917 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Context Engineering (0.62) · Multi-Agent (0.51) · RAG / Knowledge Engineering (0.48) · Agentic AI (0.45)
- **Primary branch:** context-engineering · **Confidence:** 0.62 → review queue
- **Integrity:** sha `84cbf86f5a40baa9` · dup group `dup_0199` (1)
- **Heading:** #1) Crew flow
- **Caption:** Note that this is one of many blueprints to implement a context engineering
- **Paragraph before:** This ensures the LLM can effectively complete the task. #1) Crew flow We'll follow a top-down approach to understand the code. Here's an outline of what our flow looks like:
- **Paragraph after:** Note that this is one of many blueprints to implement a context engineering workflow. Your pipeline will likely vary based on the use case. #2) Prepare data for RAG
- **OCR:** ®®® & context_engineering_flow.py from crewai import Crew, Agent, Task from crewai.flow.flow import Flow, listen, start class ContextEngineeringFlow(Flow): @start Save user query to memory def proc query(self): self.memory_layer.save_user_message(self.state.query) return self.state.query alisten(process_query) Gather context def gathexr_context(self): context_crew = Crew( f'OM au EULEes agents=[rag_agent, memory_agent, web_search_agent, arxiv_api_agent], tasks=[rag_task, memory_task, web_search_task, arxiv_api_task] ) results = await context_crew.kickoff_async() return results sten(gather_context) Filter out uate_context_relevance(self, flow_state): evaluation_result evaluation_crew.kickoff() filtered_context = evaluation_result.tasks_output[@].pydantic return filtered_context irrelevant context @listen(evaluate_context_relevance) Synthesize final def synthesize_final_response(self, flow

### fig_0209 — The extracted data can be directly embedded and stored in a vector DB without

- **Page:** 160 (PDF page 162) · **Chapter:** Context Engineering
- **BBox:** [126.00, 119.08, 486.00, 470.08] on page 612×792 pt · **Render:** 1000×975 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.80) · Data Engineering (0.45) · Context Engineering (0.41) · Agent Protocol Fabric (0.39)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.80 → review queue
- **Integrity:** sha `023bae71622ad87e` · dup group `dup_0200` (1)
- **Caption:** The extracted data can be directly embedded and stored in a vector DB without
- **Paragraph before:** We use Tensorlake to convert the document into RAG-ready markdown chunks for each section.
- **Paragraph after:** The extracted data can be directly embedded and stored in a vector DB without further processing. #3) Indexing and retrieval Now that we have RAG-ready chunks along with the metadata, it's time to store
- **OCR:** from from from doc_. file_id = doc_ai.upload(path m\ ® & tensorlake_doc_parser.py “~~ Tensorlake = tensorlake.documentai import DocumentAI, ParsingOptions, ChunkingStrategy tensorlake.documentai import TableOutputMode, StructuredExtractionOptions pydantic import BaseModel, Field eModel) heading Field(description="The section heading") summary: Field(description="Summary of the section content") Strucutred schema for extraction title: str = Field(description="The title of the research paper") authoxs: List[str] = Field(description="List of paper authors") abstract: str = Field(description="The paper's abstract") sections: List[Section] = Field(description="Sections with headings and summaries") ai = DocumentAI(api_key=TENSORLAKE_API_KEY) u "/path/to/research_paper.pdf") research_paper_extraction = StructuredExtractionOptions( pars pars j) resu rag_ extr: schema_name="research_papexr", jso

### fig_0210 — #4) Build memory layer

- **Page:** 161 (PDF page 163) · **Chapter:** Context Engineering
- **BBox:** [106.12, 67.50, 505.88, 406.50] on page 612×792 pt · **Render:** 1111×942 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.68) · Context Engineering (0.48) · Agent Protocol Fabric (0.45) · AI / ML Foundation (0.44)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.68 → review queue
- **Integrity:** sha `bebc2e9bb2341bd6` · dup group `dup_0201` (1)
- **Caption:** #4) Build memory layer
- **Paragraph after:** #4) Build memory layer Zep acts as the core memory layer of our workflow. It creates temporal knowledge graphs to organize and retrieve context for each interaction. We use it to store and retrieve context from chat history and user data.
- **OCR:** (X X J @ context_retrieval.py from pymilvus import MilvusClient, DataType client = MilvusClient("research_paper.db") schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=1024) schema.add_field("text", DataType.VARCHAR, max_length=65535) index_params = client.prepare_index_params() index_params.add_index("embedding", index_type="IVF_FLAT", metric_type="COSINE") client.create_collection( collection_name="context-engineering", index_params=index_params, schema=schema, client.insert( Insert chunks and collection_name="context-engineering", data=[{"text": chunk, "embedding": emb} for chunk, emb in zip(rag_chunks, embed(rag_chunks))] embeddings retrieved_results = client.search( collection_name="context-engineering", data=[query_embedding], anns_field="embedding", Aty SvE e limit=5, chunks output_fields=["text"]

### fig_0211 — #5) Firecrawl web search

- **Page:** 162 (PDF page 164) · **Chapter:** Context Engineering
- **BBox:** [116.62, 67.50, 495.38, 416.25] on page 612×792 pt · **Render:** 1053×969 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Memory (0.58) · Tool / Action Fabric (0.51) · Agent Protocol Fabric (0.49) · RAG / Knowledge Engineering (0.46)
- **Primary branch:** agent-memory · **Confidence:** 0.58 → review queue
- **Integrity:** sha `d4a3b1682391ca00` · dup group `dup_0202` (1)
- **Caption:** #5) Firecrawl web search
- **Paragraph after:** #5) Firecrawl web search We use Firecrawl web search to fetch the latest news and developments related to the user query. Firecrawl's v2 endpoint provides 10x faster scraping, semantic crawling, and
- **OCR:** e 5 000 @ zep_memory.py w Zep from zep_cloud.client import Zep from crewai.memory.external.external_memory import ExternalMemory from zep_crewai import ZepUserStorage, create_search_tool, create_add_data_tool zep_client = Zep(api_key=ZEP_API_KEY) user_storage = ZepUserStorage(zep_client, user_id="Avi_Chawla", thread_id="memory") zep_memory = ExternalMemory(storage=user_storase) def save_user_message(text: str) — None: zep_memory.save(text, metadata={"type": "message", "role "user"}) def save_assistant_message(text: str) — None: zep_memory.save(text, metadata={"type": "message", "role": "assistant"}) def save_user_preferences(prefs: Dict[str, Any]) — None: zep_memory.save( Save chat history and str({"preferences": prefs}), user preferences metadata={"type": "json", "category": "preferences"} user_search_tool = create_search_tool(zep_client, user_id="Avi_Chawla") user_add_tool = create_add

### fig_0212 — #6) ArXiv API search

- **Page:** 163 (PDF page 165) · **Chapter:** Context Engineering
- **BBox:** [109.88, 67.50, 502.12, 420.75] on page 612×792 pt · **Render:** 1089×981 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Tool / Action Fabric (0.57) · RAG / Knowledge Engineering (0.50) · Agent Protocol Fabric (0.50) · Agentic AI (0.47)
- **Primary branch:** tool-action-fabric · **Confidence:** 0.57 → review queue
- **Integrity:** sha `f6bfb59bc6094803` · dup group `dup_0203` (1)
- **Caption:** #6) ArXiv API search
- **Paragraph after:** #6) ArXiv API search To further support research queries, we use the arXiv API to retrieve relevant results from their data repository based on the user query.
- **OCR:** o000 @ web_search_agent.py from crewai.tools import BaseTool Firecrawl from firecrawl import Firecrawl class FirecrawlSearchTool(BaseTool): name: str = "Firecrawl Web Search" description: str = "Tool to search the web using Firecrawl" def _run(self, query: str, limit: int = 3) — str firecrawl = Firecrawl(api_key=FIRECRAWL_API_KEY) response = firecrawl.search(query, limit=limit) results = getattr(response, "web", None) search_content = [{ "url": result.get("url"), "title": result.get("title"), "description": result.get("description"), "category": result.get("category") } for result in results] return search_content web_search_agent = Agent( Create web search agent role="Web Research Specialist", goal="Search the web for relevant information regarding user query", backstory eb research expert specialized in finding recent news, " "developments, and information on a topic from the web.", to

### fig_0213 — #7) Filter context

- **Page:** 164 (PDF page 166) · **Chapter:** Context Engineering
- **BBox:** [119.62, 67.50, 492.38, 394.50] on page 612×792 pt · **Render:** 1035×908 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Context Engineering (0.54) · RAG / Knowledge Engineering (0.52) · Agent Protocol Fabric (0.50) · Agentic AI (0.48)
- **Primary branch:** context-engineering · **Confidence:** 0.54 → review queue
- **Integrity:** sha `dc9ab92856ff7938` · dup group `dup_0204` (1)
- **Caption:** #7) Filter context
- **Paragraph after:** #7) Filter context Now, we pass our combined context to the context evaluation agent that filters out irrelevant context. This filtered context is then passed to the synthesizer agent that generates the
- **OCR:** (X X J % api_agentpy om crewai.tools import BaseTool class ArxivAPITool(BaseTool): name: str "arxiv_seaxch" description: str = "Search ArXiv for academic papers related to user query" def _run(self, query, category=None, author=None, max_results=5) — str: search_query = build_arxiv_query(query, category, author) base_url = "http://export.arxiv.org/api/query" params = { "search_query": search_query, "max_results": max_results, "sortBy": "relevance", response = requests.get(base_url, params=params, timeout=38) papers = [{"title": res.title, "authors": res.authors, "abstract": res.abstract} for res in response] return papers arxiv_api_agent = Agent( Create arXiv API agent role="Academic Research Specialist", goal="Analyze academic papers from ArXiv to provide research insights", backstory="Academic researcher with deep knowledge of scientific literature "Searches Arxiv for relevant papers a

### fig_0214 — #8) Kick off the workflow

- **Page:** 165 (PDF page 167) · **Chapter:** Context Engineering
- **BBox:** [103.12, 67.50, 508.88, 450.00] on page 612×792 pt · **Render:** 1127×1063 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Context Engineering (0.62) · Evaluation (0.55) · Agentic AI (0.44) · RAG / Knowledge Engineering (0.43)
- **Primary branch:** context-engineering · **Confidence:** 0.62 → review queue
- **Integrity:** sha `33cc75f225ef7d20` · dup group `dup_0205` (1)
- **Caption:** #8) Kick off the workflow
- **Paragraph after:** #8) Kick off the workflow Finally, we kick off our context engineering workflow with a query. Based on the query, we notice that the RAG tool, powered by Tensorlake, was the most relevant source for the LLM to generate a response.
- **OCR:** L N J @ evaluation_crew.py from crewai import Agent, Task, Crew from pydantic import BaseModel, Field results = await context_crew.kickoff_async() context_sources = { "rag_result": results.tasks_output[@].raw, "memoxry_result": results.tasks_output[1].raw, "web_result": results.tasks_output[2].raw, "api_result": results.tasks_output[3].raw aggregated context structured output schema class ContextEvaluationOutput(BaseModel): relevant_sources = Field(description="Sources that are relevant") filtered_context = Field(description="Filtered content from each source") relevance_scores = Field(description="Relevance scores ©-1 for each source") context_evaluator_agent = Agent( role="Context Evaluation Specialist", goal="Filter context from {context_sources} for relevance to the {query}", backstory="Expert at evaluating quality and filtering out irrelevant info", = et s ) o context window evaluat

### fig_0215 — We also translated this workflow into a streamlit app that:

- **Page:** 166 (PDF page 168) · **Chapter:** Context Engineering
- **BBox:** [116.25, 67.50, 495.75, 407.25] on page 612×792 pt · **Render:** 1055×944 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Context Engineering (0.62) · AI / ML Foundation (0.56) · RAG / Knowledge Engineering (0.45) · n8n / Workflow Automation (0.42)
- **Primary branch:** context-engineering · **Confidence:** 0.62 → review queue
- **Integrity:** sha `7bce5e319da8ff19` · dup group `dup_0206` (1)
- **Caption:** We also translated this workflow into a streamlit app that:
- **Paragraph after:** We also translated this workflow into a streamlit app that:
- **OCR:** o000 ® main.py from context_engineering_flow import ContextEngineeringFlow flow = ContextEngineeringFlow() result = await flow.kickoff_async( inputs = {"query": "Explain attention mechanism in transformers"} W Flow Finished: Re Flow Method Step Completed: process_query @ Completed: gather_context_from_all_sources Completed: evaluate_context_relevance L~ B completed: synthesize_final_response Flow Execution Completed ID: fbsedb7f-7e1f-476¢-b Tool Angs: The attention mechanism is a crucial technique in deep learning, particularly within the architecture of Transforme r models, which are designed to address the tasks of sequence transduction. Traditional models often relied on comp lex recurrent or convolutional neural networks that contained both an encoder and a decoder; however, the Transform er architecture introduced by Vaswani et al. in 2017 revolutionized this by relying solely on at

### fig_0216 — Context Engineering figure

- **Page:** 166 (PDF page 168) · **Chapter:** Context Engineering
- **BBox:** [115.50, 446.56, 496.50, 706.06] on page 612×792 pt · **Render:** 1059×721 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Context Engineering (0.68) · RAG / Knowledge Engineering (0.46) · n8n / Workflow Automation (0.46) · Data Engineering (0.46)
- **Primary branch:** context-engineering · **Confidence:** 0.68 → review queue
- **Integrity:** sha `a31fc8473801b313` · dup group `dup_0207` (1)
- **Paragraph before:** We also translated this workflow into a streamlit app that:
- **OCR:** B Document Processing. \| o 4 Al Research Assistant @ Sremsmptara D temsoroke 5 z6p A Frecrawl Gramal @ milvus e ® Research Chat P goces dcument s i th b »

### fig_0217 — Let’s understand how it works:

- **Page:** 168 (PDF page 170) · **Chapter:** Context Engineering
- **BBox:** [147.38, 67.50, 464.62, 400.50] on page 612×792 pt · **Render:** 881×925 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Context Engineering (0.80) · n8n / Workflow Automation (0.41) · Agent Protocol Fabric (0.41) · Business Automation (0.41)
- **Primary branch:** context-engineering · **Confidence:** 0.80 → review queue
- **Integrity:** sha `5e6ac56bfd5769f1` · dup group `dup_0208` (1)
- **Caption:** Let’s understand how it works:
- **Paragraph after:** Let’s understand how it works: ● Layer 1: Main Context - Always loaded, it contains the project configuration. ●
- **OCR:** *Progresslve Context Loading in [« U {85 115 mep.DailyDoseofDS.com Main Context Always —>i\| Loaded yourproject CLAUDE.md, v Skill Discovery Triggered S O Nt Skl description.. eator Name: docx Name: pptx description:.. description:.. Only the YAML frontmatter is loaded for discovery f v Skill Full Context ® Full Tnstructions SKIULmd: Always loaded o Examples when skill activates ® Beik praetitas Progressive Referenced files: Loaded Loading only when needed Supporting files: NOT pre- loaded - executed/accessed o scripts/helperpy directly

### fig_0218 — Context Engineering

- **Page:** 170 (PDF page 172) · **Chapter:** Context Engineering
- **BBox:** [130.12, 426.89, 481.88, 532.64] on page 612×792 pt · **Render:** 977×294 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Context Engineering (0.58) · RAG / Knowledge Engineering (0.58) · Data Engineering (0.46) · Agentic AI (0.43)
- **Primary branch:** context-engineering · **Confidence:** 0.58 → review queue
- **Integrity:** sha `10d07ff8124fa817` · dup group `dup_0209` (1)
- **Heading:** Context Engineering
- **Caption:** How would you build a unified query engine over it?
- **Paragraph before:** structure for you. Manual RAG Pipeline vs Agentic Context Engineering Imagine you have data that’s spread across several sources (Gmail, Drive, etc.).
- **Paragraph after:** How would you build a unified query engine over it? Devs would typically treat context retrieval like a weekend project. ...and their approach would be: “Embed the data, store in a vector DB and do RAG.”
- **OCR:** Data Sources for Agents BER w5 4 O AS QN =P R

### fig_0219 — To actually solve this problem, you’d need to think of it as building an Agentic

- **Page:** 171 (PDF page 173) · **Chapter:** Context Engineering
- **BBox:** [144.00, 214.44, 468.00, 536.94] on page 612×792 pt · **Render:** 900×896 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.66) · Context Engineering (0.49) · Agentic AI (0.47) · Data Engineering (0.42)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.66 → review queue
- **Integrity:** sha `93037cf161d3aedf` · dup group `dup_0210` (1)
- **Caption:** To actually solve this problem, you’d need to think of it as building an Agentic
- **Paragraph before:** What’s blocking the Chicago office project, and when’s our next meeting about it? Answering this single query requires searching across sources like Linear (for blockers), Calendar (for meetings), Gmail (for emails), and Slack (for discussions). No naive RAG setup can handle this!
- **Paragraph after:** To actually solve this problem, you’d need to think of it as building an Agentic context retrieval system with three critical layers: ● Ingestion layer: ○
- **OCR:** Manual RAG pipeline Hard-coded indexing and retrieval workflow ® DatasourceA Datasource B Data source C ® ® Query ) Connector @ Vectors Vectors Vector DB ®) ontext 1 inal response Connector Agentic context engineering Bi-temporal semantic knowledge layer for Agents & Airweave ® Vectors expansion ) Vector DB (Airweave) Context Reranking Final response

### fig_0220 — It implements everything we discussed above, like:

- **Page:** 173 (PDF page 175) · **Chapter:** Context Engineering
- **BBox:** [149.25, 67.50, 462.75, 324.75] on page 612×792 pt · **Render:** 871×715 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.58) · Context Engineering (0.51) · RAG / Knowledge Engineering (0.48) · Data Engineering (0.48)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.58 → review queue
- **Integrity:** sha `e49a7d3f0a820210` · dup group `dup_0211` (1)
- **Caption:** It implements everything we discussed above, like:
- **Paragraph after:** It implements everything we discussed above, like: ● How to handle authentication across apps. ●
- **OCR:** (I README A Contributing &3 MIT license &3 Security 4 Airweave Context Retrieval for Al Agents across Apps & Databases {aunchyc 119 { 4,2.& 42 Repository Of The Day } .. Help us reach more developers and grow the Airweave community. Star this repo! What is Airweave? Airweave is a fully open-source context retrieval layer for Al agents across apps and databases. It connects to apps, productivity tools, databases, or document stores and transforms their contents into searchable knowledge bases, accessible through a standardized interface for agents. The search interface is exposed via REST AP or MCP, When using MCP, Airweave essentially builds a semantically searchable MCP server. The platform handles everything from auth and extraction to embedding and serving. You can find our documentation here.

### fig_0221 — But this does not tell if the content actually changed (maybe only the permission

- **Page:** 173 (PDF page 175) · **Chapter:** Context Engineering
- **BBox:** [120.75, 546.34, 491.25, 636.34] on page 612×792 pt · **Render:** 1029×250 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.54) · Security (0.54) · Context Engineering (0.54) · Data Engineering (0.41)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.54 → review queue
- **Integrity:** sha `58ba749a4aee6e58` · dup group `dup_0212` (1)
- **Caption:** But this does not tell if the content actually changed (maybe only the permission
- **Paragraph before:** How to detect updates and do real-time sync. ● How to generate perplexity-like citation-backed responses, and more. For instance, to detect updates and initiate a re-sync, one might do timestamp comparisons.
- **Paragraph after:** But this does not tell if the content actually changed (maybe only the permission was updated), and you might still re-embed everything unnecessarily.
- **OCR:** & Reindex Time- stqmp unncessarily e _— > Permission updated updated Vector DB Docs

### fig_0222 — What is an AI Agent?

- **Page:** 176 (PDF page 178) · **Chapter:** AI Agents
- **BBox:** [114.00, 217.44, 498.00, 433.44] on page 612×792 pt · **Render:** 1067×600 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.6
- **Mapping:** Agentic AI (0.81) · RAG / Knowledge Engineering (0.44) · Evaluation (0.44)
- **Primary branch:** agentic-ai · **Confidence:** 0.81 → review queue
- **Integrity:** sha `51f4f1588d48b5cd` · dup group `dup_0213` (1)
- **Heading:** What is an AI Agent?
- **Caption:** 1. Ask for a summary of recent AI research papers.
- **Paragraph before:** What is an AI Agent? Imagine you want to generate a report on the latest trends in AI research. If you use a standard LLM, you might:
- **Paragraph after:** 1. Ask for a summary of recent AI research papers. 2. Review the response and realize you need sources. 3. Obtain a list of papers along with citations.
- **OCR:** Do this/ Cl«ange this/ W User ChatGPT

### fig_0223 — ● A Filtering Agent scans the retrieved papers, identifying the most relevant

- **Page:** 177 (PDF page 179) · **Chapter:** AI Agents
- **BBox:** [133.88, 67.50, 478.12, 204.00] on page 612×792 pt · **Render:** 957×379 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agentic AI (0.80) · RAG / Knowledge Engineering (0.54)
- **Primary branch:** agentic-ai · **Confidence:** 0.80 → review queue
- **Integrity:** sha `21e6bf296abbf7ec` · dup group `dup_0214` (1)
- **Caption:** ● A Filtering Agent scans the retrieved papers, identifying the most relevant
- **Paragraph after:** ● A Filtering Agent scans the retrieved papers, identifying the most relevant ones based on citation count, publication date, and keywords. ● A Summarization Agent extracts key insights and condenses them into an
- **OCR:** ArXiv 6oogle scholar Semantic Research agent scholar

### fig_0224 — ●

- **Page:** 177 (PDF page 179) · **Chapter:** AI Agents
- **BBox:** [129.75, 298.66, 518.25, 398.41] on page 612×792 pt · **Render:** 1079×277 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agentic AI (0.86) · RAG / Knowledge Engineering (0.49)
- **Primary branch:** agentic-ai · **Confidence:** 0.86 → auto-accept
- **Integrity:** sha `faa4028bc22ca19d` · dup group `dup_0215` (1)
- **Caption:** ●
- **Paragraph before:** ● A Filtering Agent scans the retrieved papers, identifying the most relevant ones based on citation count, publication date, and keywords.
- **Paragraph after:** ● A Summarization Agent extracts key insights and condenses them into an easy-to-read report. ● A Formatting Agent structures the final report, ensuring it follows a clear,
- **OCR:** Filtering Research papers agent Relevant papers

### fig_0225 — ● A Formatting Agent structures the final report, ensuring it follows a clear,

- **Page:** 177 (PDF page 179) · **Chapter:** AI Agents
- **BBox:** [115.50, 489.30, 496.50, 590.55] on page 612×792 pt · **Render:** 1059×281 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agentic AI (0.92) · RAG / Knowledge Engineering (0.43)
- **Primary branch:** agentic-ai · **Confidence:** 0.92 → auto-accept
- **Integrity:** sha `2909bc82852a6e76` · dup group `dup_0216` (1)
- **Caption:** ● A Formatting Agent structures the final report, ensuring it follows a clear,
- **Paragraph before:** ones based on citation count, publication date, and keywords. ● A Summarization Agent extracts key insights and condenses them into an easy-to-read report.
- **Paragraph after:** ● A Formatting Agent structures the final report, ensuring it follows a clear, professional layout.
- **OCR:** .. — 6 — Insights Summarization Relevant papers Agent

### fig_0226 — Here, the AI agents not only execute the research process end-to-end but also

- **Page:** 178 (PDF page 180) · **Chapter:** AI Agents
- **BBox:** [103.50, 67.50, 508.50, 171.75] on page 612×792 pt · **Render:** 1125×290 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.98)
- **Primary branch:** agentic-ai · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `defdc34229498bc7` · dup group `dup_0217` (1)
- **Caption:** Here, the AI agents not only execute the research process end-to-end but also
- **Paragraph after:** Here, the AI agents not only execute the research process end-to-end but also self-refine their outputs, ensuring the final report is comprehensive, up-to-date, and well-structured - all without requiring human intervention at every step. To formalize AI Agents are autonomous systems that can reason, think, plan,
- **OCR:** Insights — 6 — . Formatting Agent Summary

### fig_0227 — To formalize AI Agents are autonomous systems that can reason, think, plan,

- **Page:** 178 (PDF page 180) · **Chapter:** AI Agents
- **BBox:** [112.12, 272.64, 499.88, 608.64] on page 612×792 pt · **Render:** 1077×933 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.6
- **Mapping:** Agentic AI (0.98)
- **Primary branch:** agentic-ai · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `3ddeecba07ead3f6` · dup group `dup_0218` (1)
- **Caption:** To formalize AI Agents are autonomous systems that can reason, think, plan,
- **Paragraph before:** Here, the AI agents not only execute the research process end-to-end but also self-refine their outputs, ensuring the final report is comprehensive, up-to-date, and well-structured - all without requiring human intervention at every step.
- **Paragraph after:** To formalize AI Agents are autonomous systems that can reason, think, plan, figure out the relevant sources and extract information from them when needed, take actions, and even correct themselves if something goes wrong.
- **OCR:** What is an AL Agent ?

### fig_0228 — Agent vs LLM vs RAG

- **Page:** 179 (PDF page 181) · **Chapter:** AI Agents
- **BBox:** [82.50, 123.69, 529.50, 280.44] on page 612×792 pt · **Render:** 1241×436 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.6
- **Mapping:** Agentic AI (0.70) · RAG / Knowledge Engineering (0.53) · Observability (0.47)
- **Primary branch:** agentic-ai · **Confidence:** 0.70 → review queue
- **Integrity:** sha `9542430cb02ac261` · dup group `dup_0219` (1)
- **Heading:** Agent vs LLM vs RAG
- **Caption:** Let’s break it down with a simple analogy:
- **Paragraph before:** Agent vs LLM vs RAG
- **Paragraph after:** Let’s break it down with a simple analogy: ● LLM is the brain. ● RAG is feeding that brain with fresh information.
- **OCR:** Agent

### fig_0229 — LLM (Large Language Model)

- **Page:** 179 (PDF page 181) · **Chapter:** AI Agents
- **BBox:** [175.88, 516.97, 436.12, 646.72] on page 612×792 pt · **Render:** 723×360 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.6
- **Mapping:** Agentic AI (0.74) · Agent Protocol Fabric (0.61)
- **Primary branch:** agentic-ai · **Confidence:** 0.74 → review queue
- **Integrity:** sha `e6f864fef67cadbf` · dup group `dup_0220` (1)
- **Heading:** LLM (Large Language Model)
- **Caption:** It’s smart, but static. It can’t access the web, call APIs, or fetch new facts on its
- **Paragraph before:** LLM (Large Language Model) An LLM like GPT-4 is trained on massive text data. It can reason, generate, summarize but only using what it already knows (i.e., its training data).
- **Paragraph after:** It’s smart, but static. It can’t access the web, call APIs, or fetch new facts on its own.
- **OCR:** LLM is smart but static

### fig_0230 — RAG (Retrieval-Augmented Generation)

- **Page:** 180 (PDF page 182) · **Chapter:** AI Agents
- **BBox:** [153.75, 166.95, 458.25, 291.45] on page 612×792 pt · **Render:** 845×346 px
- **Composition:** raster · **Role:** process · **Quality:** 0.6
- **Mapping:** RAG / Knowledge Engineering (0.74) · Agentic AI (0.51) · Evaluation (0.41) · Context Engineering (0.38)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.74 → review queue
- **Integrity:** sha `a583131bdc34af69` · dup group `dup_0221` (1)
- **Heading:** RAG (Retrieval-Augmented Generation)
- **Caption:** RAG makes the LLM aware of updated, relevant info without retraining.
- **Paragraph before:** RAG (Retrieval-Augmented Generation) RAG enhances an LLM by retrieving external documents (from a vector DB, search engine, etc.) and feeding them into the LLM as context before generating a response.
- **Paragraph after:** RAG makes the LLM aware of updated, relevant info without retraining. Agent An Agent adds autonomy to the mix. It doesn’t just answer a question—it decides what steps to take:
- **OCR:** RAG > [E] Retrieves fresh knowledge

### fig_0231 — Agent

- **Page:** 180 (PDF page 182) · **Chapter:** AI Agents
- **BBox:** [168.00, 386.66, 444.00, 525.41] on page 612×792 pt · **Render:** 767×385 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.6
- **Mapping:** Agentic AI (0.78) · Tool / Action Fabric (0.46) · RAG / Knowledge Engineering (0.40) · Agent Orchestration (0.40)
- **Primary branch:** agentic-ai · **Confidence:** 0.78 → review queue
- **Integrity:** sha `b802e99849b3db69` · dup group `dup_0222` (1)
- **Heading:** Agent
- **Caption:** It doesn’t just answer a question—it decides what steps to take:
- **Paragraph before:** a response. RAG makes the LLM aware of updated, relevant info without retraining. Agent An Agent adds autonomy to the mix.
- **Paragraph after:** It doesn’t just answer a question—it decides what steps to take: Should it call a tool? Search the web? Summarize? Store info? An Agent uses an LLM, calls tools, makes decisions, and orchestrates workflows just like a real assistant.
- **OCR:** g — 0N — & — g — Agent thinks and act

### fig_0232 — 1) Role-playing

- **Page:** 181 (PDF page 183) · **Chapter:** AI Agents
- **BBox:** [120.38, 394.81, 491.62, 520.81] on page 612×792 pt · **Render:** 1031×350 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agentic AI (0.80) · Context Engineering (0.41) · RAG / Knowledge Engineering (0.41) · Evaluation (0.41)
- **Primary branch:** agentic-ai · **Confidence:** 0.80 → review queue
- **Integrity:** sha `41f158d12cd2e7f3` · dup group `dup_0223` (1)
- **Heading:** 1) Role-playing
- **Caption:** A generic AI assistant may give vague answers. But define it as a “Senior contract
- **Paragraph before:** building great AI agents. 1) Role-playing One of the simplest ways to boost an agent’s performance is by giving it a clear, specific role.
- **Paragraph after:** A generic AI assistant may give vague answers. But define it as a “Senior contract lawyer,” and it responds with legal precision and context. Why? Because role assignment shapes the agent’s reasoning and retrieval process. The
- **OCR:** ~ 828 Senior Content Research developer writer analyst Agent

### fig_0233 — Overloading leads to confusion, inconsistency, and poor results.

- **Page:** 182 (PDF page 184) · **Chapter:** AI Agents
- **BBox:** [132.00, 97.28, 480.00, 292.28] on page 612×792 pt · **Render:** 967×541 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Agentic AI (0.92) · Business Automation (0.43)
- **Primary branch:** agentic-ai · **Confidence:** 0.92 → auto-accept
- **Integrity:** sha `34003c8e3dd89c7d` · dup group `dup_0224` (1)
- **Caption:** Overloading leads to confusion, inconsistency, and poor results.
- **Paragraph before:** Giving an agent too many tasks or too much data doesn’t help - it hurts.
- **Paragraph after:** Overloading leads to confusion, inconsistency, and poor results. For example, a marketing agent should stick to messaging, tone, and audience not pricing or market analysis. Instead of trying to make one agent do everything, a better approach is to use
- **OCR:** <::> Potential Roles Senior Content Research developer writer analyst ool Agent

### fig_0234 — For example, an AI research agent could benefit from:

- **Page:** 183 (PDF page 185) · **Chapter:** AI Agents
- **BBox:** [129.75, 67.50, 482.25, 321.75] on page 612×792 pt · **Render:** 979×706 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Agentic AI (0.74) · Tool / Action Fabric (0.48) · RAG / Knowledge Engineering (0.41) · Data Engineering (0.41)
- **Primary branch:** agentic-ai · **Confidence:** 0.74 → review queue
- **Integrity:** sha `e149d47ea2a9d749` · dup group `dup_0225` (1)
- **Caption:** For example, an AI research agent could benefit from:
- **Paragraph after:** For example, an AI research agent could benefit from: ● A web search tool for retrieving recent publications. ●
- **OCR:** Research analyst agent 5 Streamlit App Ask anything... Tool Web Search Consolidated results Research Ana'ys‘t ' \ Task ! 0

### fig_0235 — However, you may need to build custom tools at times.

- **Page:** 184 (PDF page 186) · **Chapter:** AI Agents
- **BBox:** [129.00, 117.06, 483.00, 474.06] on page 612×792 pt · **Render:** 983×991 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Tool / Action Fabric (0.73) · Agentic AI (0.44) · Multi-Agent (0.44) · Agent Orchestration (0.44)
- **Primary branch:** tool-action-fabric · **Confidence:** 0.73 → review queue
- **Integrity:** sha `7ff9122ea10417ce` · dup group `dup_0226` (1)
- **Caption:** However, you may need to build custom tools at times.
- **Paragraph before:** CrewAI supports several tools that you can integrate with Agents, as depicted below:
- **Paragraph after:** However, you may need to build custom tools at times. In this example, we're building a real-time currency conversion tool inside CrewAI. Instead of making an LLM guess exchange rates, we integrate a custom tool that fetches live exchange rates from an external API and provides some
- **OCR:** @rerval to Build ¢ join. DailyDoseofDS.com 1) File Read tool 2) File Writer tool 3) Code Interpreter tool ilewriterTool S) Serper Dev tool crewai crevai_to Fi a BrowserbaseLoadTool 10) Github Search tool 11) TXT Search tool 12) NL2sQL tool crewai_tool NL25QLTool

### fig_0236 — You would also need an API key from here: https://www.exchangerate-api.com/

- **Page:** 185 (PDF page 187) · **Chapter:** AI Agents
- **BBox:** [207.75, 67.50, 404.25, 167.25] on page 612×792 pt · **Render:** 545×277 px
- **Composition:** raster · **Role:** code · **Quality:** 0.6
- **Mapping:** Agent Protocol Fabric (0.61) · Agentic AI (0.54) · Tool / Action Fabric (0.48) · Multi-Agent (0.41)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.61 → review queue
- **Integrity:** sha `07e1949d8e55f59e` · dup group `dup_0227` (3)
- **Caption:** You would also need an API key from here: https://www.exchangerate-api.com/
- **Paragraph after:** You would also need an API key from here: https://www.exchangerate-api.com/ (it's free). Specify it in the .env file as shown below: Once that's done, we start with some standard import statements: Next, we define the input fields the tool expects using Pydantic.
- **OCR:** notebook.ipynb Ipip install crewai-tools

### fig_0237 — Once that's done, we start with some standard import statements:

- **Page:** 185 (PDF page 187) · **Chapter:** AI Agents
- **BBox:** [185.25, 222.34, 426.75, 322.84] on page 612×792 pt · **Render:** 671×279 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.65) · Tool / Action Fabric (0.53) · Agentic AI (0.53)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.65 → review queue
- **Integrity:** sha `31213ed4b5c6371a` · dup group `dup_0228` (1)
- **Caption:** Once that's done, we start with some standard import statements:
- **Paragraph before:** You would also need an API key from here: https://www.exchangerate-api.com/ (it's free). Specify it in the .env file as shown below:
- **Paragraph after:** Once that's done, we start with some standard import statements: Next, we define the input fields the tool expects using Pydantic. Now, we define the CurrencyConverterTool by inheriting from BaseTool:
- **OCR:** OPENAI_API_KEY="sk-4..." SERPER_API_KEY="42131..." EXCHANGE_RATE_API_KEY="753..."

### fig_0238 — Next, we define the input fields the tool expects using Pydantic.

- **Page:** 185 (PDF page 187) · **Chapter:** AI Agents
- **BBox:** [181.12, 358.16, 430.88, 523.16] on page 612×792 pt · **Render:** 693×459 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Tool / Action Fabric (0.68) · Agentic AI (0.51) · Agent Protocol Fabric (0.46) · Multi-Agent (0.40)
- **Primary branch:** tool-action-fabric · **Confidence:** 0.68 → review queue
- **Integrity:** sha `ab2a0f7c705a19ed` · dup group `dup_0229` (1)
- **Caption:** Next, we define the input fields the tool expects using Pydantic.
- **Paragraph before:** You would also need an API key from here: https://www.exchangerate-api.com/ (it's free). Specify it in the .env file as shown below: Once that's done, we start with some standard import statements:
- **Paragraph after:** Next, we define the input fields the tool expects using Pydantic. Now, we define the CurrencyConverterTool by inheriting from BaseTool:
- **OCR:** [ X X J notebook.ipynb from dotenv import load_dotenv load_dotenv() import os import requests from typing import Type from crewai.tools import BaseTool from pydantic import BaseModel, Field

### fig_0239 — Now, we define the CurrencyConverterTool by inheriting from BaseTool:

- **Page:** 185 (PDF page 187) · **Chapter:** AI Agents
- **BBox:** [75.00, 558.44, 537.00, 679.94] on page 612×792 pt · **Render:** 1283×337 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Tool / Action Fabric (0.70) · Agentic AI (0.53) · Agent Protocol Fabric (0.47)
- **Primary branch:** tool-action-fabric · **Confidence:** 0.70 → review queue
- **Integrity:** sha `3b9faa74e89583f4` · dup group `dup_0230` (1)
- **Caption:** Now, we define the CurrencyConverterTool by inheriting from BaseTool:
- **Paragraph before:** You would also need an API key from here: https://www.exchangerate-api.com/ (it's free). Specify it in the .env file as shown below: Once that's done, we start with some standard import statements: Next, we define the input fields the tool expects using Pydantic.
- **Paragraph after:** Now, we define the CurrencyConverterTool by inheriting from BaseTool:
- **OCR:** [ X X J notebook ipynb class CurrencyConverterInput(BaseModel): """Input schema for CurrencyConverterTool.""" amount: float = Field(..., description="The amount to convert.") from_currency: str = Field(..., description="The source currency code (e.g., 'USD').") to_currency: str = Field(..., description="The target currency code (e.g., "EUR').")

### fig_0240 — Every tool class should have the _run method which we will execute whenever

- **Page:** 186 (PDF page 188) · **Chapter:** AI Agents
- **BBox:** [126.00, 67.50, 486.00, 181.50] on page 612×792 pt · **Render:** 1000×317 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Tool / Action Fabric (0.62) · Agentic AI (0.57) · Agent Protocol Fabric (0.51)
- **Primary branch:** tool-action-fabric · **Confidence:** 0.62 → review queue
- **Integrity:** sha `d1a1eb090f35b3c2` · dup group `dup_0231` (1)
- **Caption:** Every tool class should have the _run method which we will execute whenever
- **Paragraph after:** Every tool class should have the _run method which we will execute whenever the Agents wants to make use of it. For our use case, we implement it as follows: In the above code, we fetch live exchange rates using an API request. We also
- **OCR:** (X X J notebook.ipynb class CurrencyConverterTool(BaseTool): name: str = "Currency Converter Tool" description: str = "Converts an amount from one currency to another." args_schema: Type[BaseModel] = CurrencyConverterInput api_key: str = os.getenv("EXCHANGE_RATE_API_KEY")

### fig_0241 — In the above code, we fetch live exchange rates using an API request. We also

- **Page:** 186 (PDF page 188) · **Chapter:** AI Agents
- **BBox:** [154.12, 266.38, 457.88, 411.88] on page 612×792 pt · **Render:** 843×405 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agentic AI (0.63) · Agent Protocol Fabric (0.54) · Tool / Action Fabric (0.49) · Evaluation (0.40)
- **Primary branch:** agentic-ai · **Confidence:** 0.63 → review queue
- **Integrity:** sha `c7f4eb5622c040fc` · dup group `dup_0232` (1)
- **Caption:** In the above code, we fetch live exchange rates using an API request. We also
- **Paragraph before:** Every tool class should have the _run method which we will execute whenever the Agents wants to make use of it. For our use case, we implement it as follows:
- **Paragraph after:** In the above code, we fetch live exchange rates using an API request. We also handle errors if the request fails or the currency code is invalid. Now, we define an agent that uses the tool for real-time currency analysis and attach our CurrencyConverterTool, allowing the agent to call it directly if needed:
- **OCR:** LK notebook ipynb def _run(self, amount: float, from_currency: str, to_currency: str) —» str: url - f"https: //v6.exchangerate-api.con/vé/ {self.api_key}/latest/{from_currency}" response - requests.get(url) if response.status_code «+ 200: return "Failed to fetch exchange rates.” data - response.json() if "conversion_rates® not in data or to_currency not in datal"conversion_rates"]: return f"Invalid currency code: {to_currency)" rate - datal"conversion_rates"][to_currency] converted_amount - amount * rate return f"{amount} (from_currency) is equivalent to {converted_amount:.2f} {to_currency}."

### fig_0242 — We assign a task to the currency_analyst agent.

- **Page:** 186 (PDF page 188) · **Chapter:** AI Agents
- **BBox:** [151.12, 516.53, 460.88, 665.78] on page 612×792 pt · **Render:** 861×415 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agentic AI (0.74) · Tool / Action Fabric (0.52) · Multi-Agent (0.39) · Agent Orchestration (0.39)
- **Primary branch:** agentic-ai · **Confidence:** 0.74 → review queue
- **Integrity:** sha `fb232e1900431a9c` · dup group `dup_0233` (1)
- **Caption:** We assign a task to the currency_analyst agent.
- **Paragraph before:** In the above code, we fetch live exchange rates using an API request. We also handle errors if the request fails or the currency code is invalid. Now, we define an agent that uses the tool for real-time currency analysis and attach our CurrencyConverterTool, allowing the agent to call it directly if needed:
- **Paragraph after:** We assign a task to the currency_analyst agent.
- **OCR:** ®@@ notebook.ipynb from crewai import Agent currency_analyst = Agent( role="Currency Analyst", goal="Provide real-time currency conversions and financial insights.", backstory=( "You are a finance expert with deep knowledge of global exchange rates "You help users with currency conversion and financial decision-making ), tools=[CurrencyConverterTool()], verbose=True

### fig_0243 — Finally, we create a Crew, assign the agent to the task, and execute it.

- **Page:** 187 (PDF page 189) · **Chapter:** AI Agents
- **BBox:** [168.75, 67.50, 443.25, 236.25] on page 612×792 pt · **Render:** 763×469 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agentic AI (0.70) · Multi-Agent (0.53) · Context Engineering (0.41) · Agent Orchestration (0.41)
- **Primary branch:** agentic-ai · **Confidence:** 0.70 → review queue
- **Integrity:** sha `7ea9fe13cbb3dc03` · dup group `dup_0234` (1)
- **Caption:** Finally, we create a Crew, assign the agent to the task, and execute it.
- **Paragraph after:** Finally, we create a Crew, assign the agent to the task, and execute it. Printing the response, we get the following output: Works as expected! #3.2) Custom tools via MCP
- **OCR:** LA X J notebook.ipynb from crewai import Task currency_conversion_task = Task( description=( onvert {amount} {from_currency} to {to_currency} " "using real-time exchange rates." "Provide the equivalent amount and " "explain any relevant financial context." )y expected_output=("A detailed response including the "converted amount and financial insights."), agent=currency_analyst

### fig_0244 — Printing the response, we get the following output:

- **Page:** 187 (PDF page 189) · **Chapter:** AI Agents
- **BBox:** [166.50, 268.34, 445.50, 447.59] on page 612×792 pt · **Render:** 775×498 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Multi-Agent (0.65) · Agentic AI (0.60) · Agent Orchestration (0.40) · Agent Protocol Fabric (0.40)
- **Primary branch:** multi-agent · **Confidence:** 0.65 → review queue
- **Integrity:** sha `20a182f8e460b292` · dup group `dup_0235` (1)
- **Caption:** Printing the response, we get the following output:
- **Paragraph before:** Finally, we create a Crew, assign the agent to the task, and execute it.
- **Paragraph after:** Printing the response, we get the following output: Works as expected! #3.2) Custom tools via MCP Now, let’s take it a step further.
- **OCR:** [ X X ] notebook.ipynb from crewai import Crew, Process crew = Crew( agents=[currency_analyst], tasks=[currency_conversion_task], process=Process.sequential response = crew.kickoff (inputs={"amount": 100, "from_currency": "UsD", "to_currency": "EUR"})

### fig_0245 — Works as expected!

- **Page:** 187 (PDF page 189) · **Chapter:** AI Agents
- **BBox:** [94.50, 479.69, 517.50, 604.94] on page 612×792 pt · **Render:** 1175×348 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Agentic AI (0.72) · Context Engineering (0.44) · Multi-Agent (0.44) · Agent Protocol Fabric (0.44)
- **Primary branch:** agentic-ai · **Confidence:** 0.72 → review queue
- **Integrity:** sha `87c2a102b9a62dad` · dup group `dup_0236` (1)
- **Caption:** Works as expected!
- **Paragraph before:** Finally, we create a Crew, assign the agent to the task, and execute it. Printing the response, we get the following output:
- **Paragraph after:** Works as expected! #3.2) Custom tools via MCP Now, let’s take it a step further.
- **OCR:** from IPython.display import Markdown Markdown (response. raw) v 0.0s Python Converting 100 USD to EUR using real-time exchange rates results in approximately 95.40 EUR. In the financial context, it's worth noting that exchange rates can fluctuate due to various factors like economic indicators, interest rates, and geopolitical events. As of now, the conversion reflects current market conditions, which are influenced by the latest economic data releases and monetary policies in both the United States and the Eurozone. Given the recent trends, if you're planning a trip to Europe or making an investment, these rates may change, so it's beneficial to monitor them regularly.

### fig_0246 — We’ll continue using ExchangeRate-API in our .env file:

- **Page:** 188 (PDF page 190) · **Chapter:** AI Agents
- **BBox:** [175.50, 170.66, 436.50, 268.16] on page 612×792 pt · **Render:** 725×270 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.62) · Agentic AI (0.49) · Infrastructure (0.49) · Tool / Action Fabric (0.45)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.62 → review queue
- **Integrity:** sha `44aef2dc0f84816f` · dup group `dup_0237` (1)
- **Caption:** We’ll continue using ExchangeRate-API in our .env file:
- **Paragraph before:** Instead of embedding the tool directly in every Crew, we’ll expose it as a reusable MCP tool - making it accessible across multiple agents and flows via a simple server. First, install the required packages:
- **Paragraph after:** We’ll continue using ExchangeRate-API in our .env file: We’ll now write a lightweight server.py script that exposes the currency converter tool. We start with the standard imports: Now, we load environment variables and initialize the server:
- **OCR:** [ X J notebook.ipynb !pip install mcp-server requests python-dotenv

### fig_0247 — We’ll now write a lightweight server.py script that exposes the currency converter

- **Page:** 188 (PDF page 190) · **Chapter:** AI Agents
- **BBox:** [178.50, 303.44, 433.50, 414.44] on page 612×792 pt · **Render:** 709×309 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.6
- **Mapping:** Agent Protocol Fabric (0.64) · Agentic AI (0.49) · Infrastructure (0.49) · Tool / Action Fabric (0.42)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.64 → review queue
- **Integrity:** sha `9c3261103e72c172` · dup group `dup_0227` (3)
- **Caption:** We’ll now write a lightweight server.py script that exposes the currency converter
- **Paragraph before:** MCP tool - making it accessible across multiple agents and flows via a simple server. First, install the required packages: We’ll continue using ExchangeRate-API in our .env file:
- **Paragraph after:** We’ll now write a lightweight server.py script that exposes the currency converter tool. We start with the standard imports: Now, we load environment variables and initialize the server:
- **OCR:** EXCHANGE_RATE_API_KEY=your_api_key_here

### fig_0248 — Now, we load environment variables and initialize the server:

- **Page:** 188 (PDF page 190) · **Chapter:** AI Agents
- **BBox:** [167.25, 469.53, 444.75, 599.28] on page 612×792 pt · **Render:** 771×360 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.68) · Infrastructure (0.53) · Agentic AI (0.46) · Tool / Action Fabric (0.39)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.68 → review queue
- **Integrity:** sha `525e3234f967d2d1` · dup group `dup_0238` (1)
- **Caption:** Now, we load environment variables and initialize the server:
- **Paragraph before:** First, install the required packages: We’ll continue using ExchangeRate-API in our .env file: We’ll now write a lightweight server.py script that exposes the currency converter tool. We start with the standard imports:
- **Paragraph after:** Now, we load environment variables and initialize the server:
- **OCR:** 00 @ server.py import requests, os from dotenv import load_dotenv from mcp.server.fastmcp import FastMCP

### fig_0249 — Next, we define the tool logic with @mcp.tool():

- **Page:** 189 (PDF page 191) · **Chapter:** AI Agents
- **BBox:** [166.12, 67.50, 445.88, 180.75] on page 612×792 pt · **Render:** 777×315 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.65) · Tool / Action Fabric (0.53) · Infrastructure (0.44) · Agentic AI (0.44)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.65 → review queue
- **Integrity:** sha `afb3a49853545aec` · dup group `dup_0239` (1)
- **Caption:** Next, we define the tool logic with @mcp.tool():
- **Paragraph after:** Next, we define the tool logic with @mcp.tool(): This function takes three inputs - amount, source currency, and target currency and returns the converted result using the real-time exchange rate API. To make the tool accessible, we need to run the MCP server. Add this at the end
- **OCR:** (X X J @ server.py load_dotenv () mep = FastMCP('currency-converter-server', port=8081) API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")

### fig_0250 — This function takes three inputs - amount, source currency, and target currency

- **Page:** 189 (PDF page 191) · **Chapter:** AI Agents
- **BBox:** [66.00, 192.35, 474.38, 448.59] on page 612×792 pt · **Render:** 1134×712 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.62) · Tool / Action Fabric (0.56) · Agentic AI (0.45) · Infrastructure (0.42)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.62 → review queue
- **Integrity:** sha `687bcb29489ab30f` · dup group `dup_0240` (1)
- **Caption:** This function takes three inputs - amount, source currency, and target currency
- **Paragraph after:** This function takes three inputs - amount, source currency, and target currency and returns the converted result using the real-time exchange rate API. To make the tool accessible, we need to run the MCP server. Add this at the end of your script:
- **OCR:** Next, we define the tool logic with @mcp.tool(): [ X ] @ serverpy amcp . tool() def convert_currency( amount: float, from_currency: str, to_currency: str ) = str: """convert currency using real-time exchange rates response = requests.get( f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/" f"{from_currency}/{to_currency}/{amount}" ).Jjson() return ( f"{amount} {from_currency.upper()} =" f"{response['conversion_result']:.2f} {to_currency.upper()} " f"(Rate: {response['conversion_rate']:.4f})"

### fig_0251 — AI Agents figure

- **Page:** 189 (PDF page 191) · **Chapter:** AI Agents
- **BBox:** [196.88, 559.27, 415.12, 674.77] on page 612×792 pt · **Render:** 607×321 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.68) · Agentic AI (0.49) · Tool / Action Fabric (0.44) · Infrastructure (0.44)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.68 → review queue
- **Integrity:** sha `8823e5da7cd9729f` · dup group `dup_0241` (1)
- **Paragraph before:** This function takes three inputs - amount, source currency, and target currency and returns the converted result using the real-time exchange rate API. To make the tool accessible, we need to run the MCP server. Add this at the end of your script:
- **OCR:** XN J @ serverpy if __name__ = "__main__": mcp.run(transport="sse")

### fig_0252 — Next, we connect to the MCP tool server. Define the server parameters to

- **Page:** 190 (PDF page 192) · **Chapter:** AI Agents
- **BBox:** [171.75, 222.22, 440.25, 345.97] on page 612×792 pt · **Render:** 745×344 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.60) · Infrastructure (0.50) · Agentic AI (0.48) · Multi-Agent (0.47)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.60 → review queue
- **Integrity:** sha `2b677972fae150fc` · dup group `dup_0242` (1)
- **Caption:** Next, we connect to the MCP tool server. Define the server parameters to
- **Paragraph before:** Now any CrewAI agent can connect to it using MCPServerAdapter. Let’s now consume this tool from within a CrewAI agent. First, we import the required CrewAI classes. We’ll use Agent, Task, and Crew from CrewAI, and MCPServerAdapter to connect to our tool server.
- **Paragraph after:** Next, we connect to the MCP tool server. Define the server parameters to connect to your running tool (from server.py). Now, we use the discovered MCP tool in an agent: This agent is assigned the convert_currency tool from the remote server. It can
- **OCR:** 000 notebook.ipynb from crewai import Agent, Task, Crew from crewai_tools import MCPServerAdapter

### fig_0253 — Now, we use the discovered MCP tool in an agent:

- **Page:** 190 (PDF page 192) · **Chapter:** AI Agents
- **BBox:** [162.00, 405.06, 450.00, 546.06] on page 612×792 pt · **Render:** 800×391 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.62) · Agentic AI (0.48) · Tool / Action Fabric (0.48) · Infrastructure (0.48)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.62 → review queue
- **Integrity:** sha `2f2e0946341a3e94` · dup group `dup_0243` (1)
- **Caption:** Now, we use the discovered MCP tool in an agent:
- **Paragraph before:** First, we import the required CrewAI classes. We’ll use Agent, Task, and Crew from CrewAI, and MCPServerAdapter to connect to our tool server. Next, we connect to the MCP tool server. Define the server parameters to connect to your running tool (from server.py).
- **Paragraph after:** Now, we use the discovered MCP tool in an agent: This agent is assigned the convert_currency tool from the remote server. It can now call the tool just like a locally defined one.
- **OCR:** [ X N J notebook.ipynb server_params = { "url": "http://localhost:8081/sse", "transport": "sse"

### fig_0254 — We give the agent a task description:

- **Page:** 191 (PDF page 193) · **Chapter:** AI Agents
- **BBox:** [178.12, 67.50, 433.88, 216.00] on page 612×792 pt · **Render:** 711×413 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Agentic AI (0.76) · Multi-Agent (0.47) · Tool / Action Fabric (0.47)
- **Primary branch:** agentic-ai · **Confidence:** 0.76 → review queue
- **Integrity:** sha `a832e86cfd461729` · dup group `dup_0244` (1)
- **Caption:** We give the agent a task description:
- **Paragraph after:** We give the agent a task description: Finally, we create the Crew, pass in the inputs and run it: Printing the result, we get the following output:
- **OCR:** ®®0® otebook.ipynb currency_agent = Agent( role="Currency Analyst", goal="Convert currency using real-time exchange rates.", backstoxry=( "You help users convert between currencies "using up-to-date market data." ), allow_delegation=False, tools=[mep_tools["convert_currency"1],

### fig_0255 — Finally, we create the Crew, pass in the inputs and run it:

- **Page:** 191 (PDF page 193) · **Chapter:** AI Agents
- **BBox:** [172.88, 255.31, 439.12, 388.81] on page 612×792 pt · **Render:** 739×371 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Agentic AI (0.84) · Multi-Agent (0.51)
- **Primary branch:** agentic-ai · **Confidence:** 0.84 → review queue
- **Integrity:** sha `8f7bce738c44c4cd` · dup group `dup_0245` (1)
- **Caption:** Finally, we create the Crew, pass in the inputs and run it:
- **Paragraph before:** We give the agent a task description:
- **Paragraph after:** Finally, we create the Crew, pass in the inputs and run it: Printing the result, we get the following output:
- **OCR:** eoo notebook.ipynb conversion_task = Task( description=( "Convert {amount} {from_currency} to {to_currency} "using real-time exchange rates." ), agent=currency_agent, expected_output="A formatted result with exchange rate.",

### fig_0256 — Printing the result, we get the following output:

- **Page:** 191 (PDF page 193) · **Chapter:** AI Agents
- **BBox:** [171.00, 428.11, 441.00, 559.36] on page 612×792 pt · **Render:** 750×364 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Agentic AI (0.74) · Multi-Agent (0.61)
- **Primary branch:** agentic-ai · **Confidence:** 0.74 → review queue
- **Integrity:** sha `20630a9f40c0c66a` · dup group `dup_0246` (1)
- **Caption:** Printing the result, we get the following output:
- **Paragraph before:** We give the agent a task description: Finally, we create the Crew, pass in the inputs and run it:
- **Paragraph after:** Printing the result, we get the following output:
- **OCR:** LX) notebook.ipynb crew = Crew( agents=[currency_agent], tasks=[conversion_task], verbose=True result = crew.kickoff(inputs={ “"amount": 100, "from_currency”: "USD", "to_currency": "INR" H print (result)

### fig_0257 — AI Agents figure

- **Page:** 191 (PDF page 193) · **Chapter:** AI Agents
- **BBox:** [184.88, 598.66, 427.12, 693.91] on page 612×792 pt · **Render:** 673×265 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Agentic AI (0.87) · Multi-Agent (0.48)
- **Primary branch:** agentic-ai · **Confidence:** 0.87 → auto-accept
- **Integrity:** sha `4f0c2cd6cfd788bb` · dup group `dup_0247` (1)
- **Paragraph before:** We give the agent a task description: Finally, we create the Crew, pass in the inputs and run it: Printing the result, we get the following output:
- **OCR:** print(result) v 28s 100 USD = 8734.13 INR (Rate: 87.3413)

### fig_0258 — 4) Cooperation

- **Page:** 192 (PDF page 194) · **Chapter:** AI Agents
- **BBox:** [140.25, 180.97, 471.75, 427.72] on page 612×792 pt · **Render:** 921×686 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.6
- **Mapping:** Agentic AI (0.88) · Multi-Agent (0.47)
- **Primary branch:** agentic-ai · **Confidence:** 0.88 → auto-accept
- **Integrity:** sha `7b65bfa92c1bf06f` · dup group `dup_0248` (1)
- **Heading:** 4) Cooperation
- **Caption:** Consider an AI-powered financial analysis system:
- **Paragraph before:** 4) Cooperation Multi-agent systems work best when agents collaborate and exchange feedback. Instead of one agent doing everything, a team of specialized agents can split tasks and improve each other’s outputs.
- **Paragraph after:** Consider an AI-powered financial analysis system: ● One agent gathers data ●
- **OCR:** S) Multi-agent Pattern

### fig_0259 — Examples of useful guardrails include:

- **Page:** 193 (PDF page 195) · **Chapter:** AI Agents
- **BBox:** [131.62, 131.08, 480.38, 268.33] on page 612×792 pt · **Render:** 969×381 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Agentic AI (0.65) · Security (0.59) · Agent Protocol Fabric (0.41) · Tool / Action Fabric (0.41)
- **Primary branch:** agentic-ai · **Confidence:** 0.65 → review queue
- **Integrity:** sha `e176451efd9076b5` · dup group `dup_0249` (1)
- **Caption:** Examples of useful guardrails include:
- **Paragraph before:** hallucinate, loop endlessly, or make bad calls. Guardrails ensure that agents stay on track and maintain quality standards.
- **Paragraph after:** Examples of useful guardrails include: ● Limiting tool usage: Prevent an agent from overusing APIs or generating irrelevant queries.
- **OCR:** Senior developer - . y Objective (&) [} 7 7 . 7,77, Guardrails 1;:1’ v

### fig_0260 — Different types of memory in AI agents include:

- **Page:** 194 (PDF page 196) · **Chapter:** AI Agents
- **BBox:** [129.75, 67.50, 482.25, 213.00] on page 612×792 pt · **Render:** 979×404 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agentic AI (0.68) · Agent Memory (0.62) · Security (0.40)
- **Primary branch:** agentic-ai · **Confidence:** 0.68 → review queue
- **Integrity:** sha `0a7e7f0f4634f5b0` · dup group `dup_0250` (1)
- **Caption:** Different types of memory in AI agents include:
- **Paragraph after:** Different types of memory in AI agents include: ● Short-term memory – Exists only during execution (e.g., recalling recent conversation history). ●
- **OCR:** y Objective O - Roles g / Senior Agent developer ) ,l,t’ Guardrails l”

### fig_0261 — This memory isn’t just nice-to-have but it enables agents to learn from past

- **Page:** 195 (PDF page 197) · **Chapter:** AI Agents
- **BBox:** [140.62, 67.50, 471.38, 348.00] on page 612×792 pt · **Render:** 919×779 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.66) · Agent Memory (0.59) · LLM Engineering (0.42) · RAG / Knowledge Engineering (0.38)
- **Primary branch:** agentic-ai · **Confidence:** 0.66 → review queue
- **Integrity:** sha `cbc3d24b3eb59f6d` · dup group `dup_0251` (1)
- **Caption:** This memory isn’t just nice-to-have but it enables agents to learn from past
- **Paragraph after:** This memory isn’t just nice-to-have but it enables agents to learn from past interactions without retraining the model. This is especially powerful for continual learning: letting agents adapt to new tasks without touching LLM weights.
- **OCR:** \| Memory types for AT Agent [ pnoaydssestoscon Type of Memory I Definition Persistence Content Tracks ongoing Dersists Within ion\| \| - conversation history. Based on Short term conversation by i e as ot - oloaded s maintaining messag - ratrieved docs Scope [ e kool outputs Allows system to :Bv’s‘isls across session \| [- Ilg;sv fmh;m v . vetain information ifferent sessions and. \| \|- Specific factsfconcepts Long term across different raauives persistant \| \|- Balovant sxpeviances conversations storage - Task instructions. Type of What's Human Agent Memory stored? Example Example . Things I learned Facts about Eevadc Face= in school a user Human Analogy S . . 3 3 Past agent Episodic Experiences Things I did ‘ actiche Procedural i Instructions Instincts or motor skills Agnet system prompt

### fig_0262 — ● In iteration #1, the user mentions their favorite color.

- **Page:** 196 (PDF page 198) · **Chapter:** AI Agents
- **BBox:** [125.62, 67.50, 486.38, 285.75] on page 612×792 pt · **Render:** 1003×606 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agentic AI (0.70) · Agent Memory (0.53) · Multi-Agent (0.47)
- **Primary branch:** agentic-ai · **Confidence:** 0.70 → review queue
- **Integrity:** sha `57b75d3b267d4f65` · dup group `dup_0252` (1)
- **Caption:** ● In iteration #1, the user mentions their favorite color.
- **Paragraph after:** ● In iteration #1, the user mentions their favorite color. ● In iteration #2, the Agent knows nothing about iteration #1. This means the Agent is mostly stateless, and it has no recall abilities.
- **OCR:** . >>> user_input = "My favorite color is #46778F" lteratlon #1 >>> crew_without_memory.kickoff(inputs={"task":user_input}) "Final Answer: Got it, interesting choice" . user_input = "What is my favorite color?" lterat\|°n #2 >>> crew_without_memory.kickoff (inputs={"task":user_input}) "You have not told me about my favourite color yet" '\’ Agent does not remember anything from iteration #1

### fig_0263 — ●

- **Page:** 196 (PDF page 198) · **Chapter:** AI Agents
- **BBox:** [125.25, 400.42, 486.75, 607.42] on page 612×792 pt · **Render:** 1005×575 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agentic AI (0.66) · Agent Memory (0.59) · Multi-Agent (0.42) · Infrastructure (0.38)
- **Primary branch:** agentic-ai · **Confidence:** 0.66 → review queue
- **Integrity:** sha `02d9e99a2280dd37` · dup group `dup_0253` (1)
- **Caption:** ●
- **Paragraph before:** ● In iteration #2, the Agent knows nothing about iteration #1. This means the Agent is mostly stateless, and it has no recall abilities. But now consider an Agentic system built with Memory (below):
- **Paragraph after:** ● In iteration #1, the user mentions their favorite color. ● In iteration #2, the Agent can recall iteration #1. Memory matters because if a memory-less Agentic system is deployed in
- **OCR:** . >>> user_input = "My favorite color is #46778F" Iteratlon #1 >>> crew_with_memory.kickoff(inputs={"task":user_input}) "Final Answer: Got it, interesting choice" Iteration #2 user_input = "What is my favorite color?" >>> crew_with_memory.kickoff(inputs={"task":user_input}) "Your favourite color is #46778F" L Agent remembers iteration #1

### fig_0264 — It doesn’t matter if the user told the Agent their name five seconds ago, it’s

- **Page:** 197 (PDF page 199) · **Chapter:** AI Agents
- **BBox:** [145.12, 67.50, 466.88, 275.25] on page 612×792 pt · **Render:** 893×577 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agentic AI (0.84) · Agent Memory (0.46) · Context Engineering (0.40)
- **Primary branch:** agentic-ai · **Confidence:** 0.84 → review queue
- **Integrity:** sha `012bc63ed486d912` · dup group `dup_0254` (1)
- **Caption:** It doesn’t matter if the user told the Agent their name five seconds ago, it’s
- **Paragraph after:** It doesn’t matter if the user told the Agent their name five seconds ago, it’s forgotten. If the Agent helped troubleshoot an issue in the last session, it won’t remember any of it now. With Memory, your Agent becomes context-aware and practically applicable.
- **OCR:** Interaction without memory My fav color . @ is #458ff8 — . ——p Interesting. User AI Agent What is my . g fav color? e . ———» I don't know User AL Agent

### fig_0265 — ● Short-Term Memory

- **Page:** 197 (PDF page 199) · **Chapter:** AI Agents
- **BBox:** [117.75, 459.27, 494.25, 616.02] on page 612×792 pt · **Render:** 1045×436 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agent Memory (0.78) · Agentic AI (0.49) · Context Engineering (0.40) · Software Architecture (0.38)
- **Primary branch:** agent-memory · **Confidence:** 0.78 → review queue
- **Integrity:** sha `1fe9cbe9d0541307` · dup group `dup_0255` (1)
- **Caption:** ● Short-Term Memory
- **Paragraph before:** With Memory, your Agent becomes context-aware and practically applicable. But Memory isn’t an abstract concept. If you dive deeper, it follows a structured and intuitive architecture with several types of Memory.
- **Paragraph after:** ● Short-Term Memory ● Long-Term Memory ● Entity Memory
- **OCR:** AL Agent / Short-term memor‘y _______———» Long-term memory — » Entity memory —_ —» \ Contextual memory User memory

### fig_0266 — This is why memory is not a property of the model itself. It is a system design

- **Page:** 198 (PDF page 200) · **Chapter:** AI Agents
- **BBox:** [150.75, 196.44, 461.25, 325.44] on page 612×792 pt · **Render:** 863×359 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.6
- **Mapping:** Agentic AI (0.65) · Context Engineering (0.50) · Agent Memory (0.50) · RAG / Knowledge Engineering (0.40)
- **Primary branch:** agentic-ai · **Confidence:** 0.65 → review queue
- **Integrity:** sha `bf5968a1b254b497` · dup group `dup_0256` (1)
- **Caption:** This is why memory is not a property of the model itself. It is a system design
- **Paragraph before:** Each serves a unique purpose in helping agents “remember” and utilize past information. To simulate memory, the system has to manage context explicitly: choosing what to keep, what to discard, and what to retrieve before each new model call.
- **Paragraph after:** This is why memory is not a property of the model itself. It is a system design problem. Agentic AI Design Patterns Agentic behaviors allow LLMs to refine their output by incorporating
- **OCR:** Available context — L Filtered context

### fig_0267 — 1) Reflection pattern

- **Page:** 199 (PDF page 201) · **Chapter:** AI Agents
- **BBox:** [107.25, 67.50, 504.75, 517.50] on page 612×792 pt · **Render:** 1105×1250 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Agentic AI (0.87) · RAG / Knowledge Engineering (0.39) · Multi-Agent (0.39) · Tool / Action Fabric (0.39)
- **Primary branch:** agentic-ai · **Confidence:** 0.87 → auto-accept
- **Integrity:** sha `3785c5834c732762` · dup group `dup_0257` (1)
- **Caption:** 1) Reflection pattern
- **Paragraph after:** 1) Reflection pattern
- **OCR:** 1) Reflection Pattern LA . G- g o S um ' '\ (Generate) v Response y -~ S Most Popular e Agentic AT ° {iatin ¥ Des ' 9 n patterns Reflected output S Initial output 4 L L ) e doopsook\| ¢ _ _ _ ) Iﬁ join.DailyDoseof DS.com (ottect) = A 2) Tool Use Pattern 3) ReAct Pattern 5, <l Agent User @ = === \|deopsesk \| =~ =~ wm 4) Planning Pattern User s Generated tasks Uker g : - Ry ToTmEe > —-->°" -—=> o==> \|Gl -~ ——d - - - t Query -A @ < - PM agent v o {Ereute Response single % e 9 Delegati v task R e S u. g.,',.,.“. D Tech lead agent gent 6 A 1 _____ Lo RO o ! ReAct e I -~ Finished? o soe, 7 C

### fig_0268 — The AI reviews its own work to spot mistakes and iterate until it produces the

- **Page:** 200 (PDF page 202) · **Chapter:** AI Agents
- **BBox:** [153.38, 67.50, 458.62, 301.50] on page 612×792 pt · **Render:** 847×650 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agentic AI (0.78) · Tool / Action Fabric (0.57)
- **Primary branch:** agentic-ai · **Confidence:** 0.78 → review queue
- **Integrity:** sha `7177738115ad91bb` · dup group `dup_0258` (1)
- **Caption:** The AI reviews its own work to spot mistakes and iterate until it produces the
- **Paragraph after:** The AI reviews its own work to spot mistakes and iterate until it produces the final response. 2) Tool use pattern Tools allow LLMs to gather more information by:
- **OCR:** 1) Reflection Pattern deepseelk wm (Relfect)

### fig_0269 — 2) Tool use pattern

- **Page:** 200 (PDF page 202) · **Chapter:** AI Agents
- **BBox:** [151.12, 392.69, 460.88, 633.44] on page 612×792 pt · **Render:** 861×669 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Tool / Action Fabric (0.62) · Agentic AI (0.51) · RAG / Knowledge Engineering (0.46) · Data Engineering (0.46)
- **Primary branch:** tool-action-fabric · **Confidence:** 0.62 → review queue
- **Integrity:** sha `b927cfb1a2da30dd` · dup group `dup_0259` (1)
- **Heading:** 2) Tool use pattern
- **Caption:** Tools allow LLMs to gather more information by:
- **Paragraph before:** The AI reviews its own work to spot mistakes and iterate until it produces the final response. 2) Tool use pattern
- **Paragraph after:** Tools allow LLMs to gather more information by: ● Querying a vector database ● Executing Python scripts
- **OCR:** 2) Tool Use Pattern wm Response A 1 t—Jdatabase % — — — — \|deepseek um f =] (Generate) = o

### fig_0270 — 3) ReAct (Reason and Act) pattern

- **Page:** 201 (PDF page 203) · **Chapter:** AI Agents
- **BBox:** [150.75, 163.17, 461.25, 405.42] on page 612×792 pt · **Render:** 863×673 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Agentic AI (0.88) · Agent Protocol Fabric (0.41) · Tool / Action Fabric (0.41)
- **Primary branch:** agentic-ai · **Confidence:** 0.88 → auto-accept
- **Integrity:** sha `f99b8d1215742545` · dup group `dup_0260` (1)
- **Heading:** 3) ReAct (Reason and Act) pattern
- **Caption:** ReAct combines the above two patterns:
- **Paragraph before:** ● Invoking APIs, etc. This is helpful since the LLM is not solely reliant on its internal knowledge. 3) ReAct (Reason and Act) pattern
- **Paragraph after:** ReAct combines the above two patterns: ● The Agent reflects on the generated outputs. ● It interacts with the world using tools.
- **OCR:** 3) ReAct Pattern ¢ User deepseek wm (Reason) Response A S e deepseelk wm (Generate)

### fig_0271 — 3) ReAct (Reason and Act) pattern

- **Page:** 201 (PDF page 203) · **Chapter:** AI Agents
- **BBox:** [120.75, 567.66, 491.25, 695.16] on page 612×792 pt · **Render:** 1029×354 px
- **Composition:** raster · **Role:** process · **Quality:** 0.6
- **Mapping:** Agentic AI (0.86) · Tool / Action Fabric (0.42) · Observability (0.42)
- **Primary branch:** agentic-ai · **Confidence:** 0.86 → auto-accept
- **Integrity:** sha `814f055973cc2af4` · dup group `dup_0261` (1)
- **Heading:** 3) ReAct (Reason and Act) pattern
- **Paragraph before:** ● It interacts with the world using tools. A ReAct agent operates in a loop of Thought → Action → Observation, repeating until it reaches a solution or a final answer. This is analogous to how humans solve problems:
- **OCR:** ReAct Pattern

### fig_0272 — As shown above, the Agent is going through a series of thought activities before

- **Page:** 202 (PDF page 204) · **Chapter:** AI Agents
- **BBox:** [119.62, 131.08, 492.38, 428.83] on page 612×792 pt · **Render:** 1035×827 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.91) · Multi-Agent (0.39) · Agent Orchestration (0.37) · Evaluation (0.37)
- **Primary branch:** agentic-ai · **Confidence:** 0.91 → auto-accept
- **Integrity:** sha `b5217ff8f2c0caf2` · dup group `dup_0262` (1)
- **Caption:** As shown above, the Agent is going through a series of thought activities before
- **Paragraph before:** Note: Frameworks like CrewAI primarily use this by default. To understand this, consider the output of a multi-agent system below:
- **Paragraph after:** As shown above, the Agent is going through a series of thought activities before producing a response. This is the ReAct pattern in action! More specifically, under the hood, many such frameworks use the ReAct
- **OCR:** # Agent: News Collector ## Task: Search he # Agent: News Collector As: # Agent: News Reporter atest news on Agent2Agent Expands Blockchain Annous eadline on Agent2Agent Noveabe: Novenbe 10, 20234 7, 2023xx News Collector o the Agent2Agent between de: ng the interne Agent2Agent aoogle Agent 2Agent Protoca ed Agent2Agent (A24), Agent2agent Proto Announcing the Agent opers. googleblog. con/er hing a op: 24gen ed Age operabi (a2n Thought ions from more ogy partnerd

### fig_0273 — 4) Planning pattern

- **Page:** 203 (PDF page 205) · **Chapter:** AI Agents
- **BBox:** [167.25, 99.59, 444.75, 302.84] on page 612×792 pt · **Render:** 771×565 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Agentic AI (0.98)
- **Primary branch:** agentic-ai · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `2c308cca23c2dc43` · dup group `dup_0263` (1)
- **Heading:** 4) Planning pattern
- **Caption:** Instead of solving a task in one go, the AI creates a roadmap by:
- **Paragraph before:** 4) Planning pattern
- **Paragraph after:** Instead of solving a task in one go, the AI creates a roadmap by: ● Subdividing tasks ● Outlining objectives
- **OCR:** 4) Planning Pattern Generated tasks Planner Results Finished?

### fig_0274 — 5) Multi-Agent pattern

- **Page:** 203 (PDF page 205) · **Chapter:** AI Agents
- **BBox:** [157.88, 489.41, 454.12, 708.41] on page 612×792 pt · **Render:** 823×608 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agentic AI (0.73) · Multi-Agent (0.57) · Agent Orchestration (0.40)
- **Primary branch:** agentic-ai · **Confidence:** 0.73 → review queue
- **Integrity:** sha `7d7b2b1c60b803f7` · dup group `dup_0264` (1)
- **Heading:** 5) Multi-Agent pattern
- **Paragraph before:** ● Outlining objectives This strategic thinking solves tasks more effectively. Note: In CrewAI, specify `planning=True` to use Planning. 5) Multi-Agent pattern
- **OCR:** S) Multi-agent Pattern g . N - Ig(-———'——— PM agent] 1 Response

### fig_0275 — Next, we define a minimal Agent class, which wraps around a conversational

- **Page:** 205 (PDF page 207) · **Chapter:** AI Agents
- **BBox:** [192.75, 67.50, 419.25, 221.25] on page 612×792 pt · **Render:** 629×427 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.81) · LLM Engineering (0.54)
- **Primary branch:** agentic-ai · **Confidence:** 0.81 → review queue
- **Integrity:** sha `0270c04972bb9cdb` · dup group `dup_0265` (1)
- **Caption:** Next, we define a minimal Agent class, which wraps around a conversational
- **Paragraph after:** Next, we define a minimal Agent class, which wraps around a conversational LLM and keeps track of its full message history - allowing it to reason step-by-step, access system prompts, remember prior inputs and outputs, and produce multi-turn interactions.
- **OCR:** o000 notebook.ipynb from litellm import completion import os from dotenv import load_dotenv load_dotenv()

### fig_0276 — ●

- **Page:** 205 (PDF page 207) · **Chapter:** AI Agents
- **BBox:** [130.50, 351.70, 481.50, 483.70] on page 612×792 pt · **Render:** 975×367 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.65) · LLM Engineering (0.59) · Agent Protocol Fabric (0.47)
- **Primary branch:** agentic-ai · **Confidence:** 0.65 → review queue
- **Integrity:** sha `2baf53d626dfe625` · dup group `dup_0266` (1)
- **Caption:** ●
- **Paragraph before:** LLM and keeps track of its full message history - allowing it to reason step-by-step, access system prompts, remember prior inputs and outputs, and produce multi-turn interactions. Here’s what it looks like:
- **Paragraph after:** ● system (str): This is the system prompt that sets the personality and behavioral constraints for the agent. If passed, it becomes the very first message in the conversation just like in OpenAI Chat APIs.
- **OCR:** L X J notebook.ipynb class MyAgent: def __init__(self, system = self.system = system self.messages = [] if self.system: self.messages.append({"role": "system", "content": system}) nny.

### fig_0277 — This is the core interface you’ll use to interact with your agent.

- **Page:** 206 (PDF page 208) · **Chapter:** AI Agents
- **BBox:** [122.25, 67.50, 489.75, 271.50] on page 612×792 pt · **Render:** 1021×567 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.91) · Agent Protocol Fabric (0.44)
- **Primary branch:** agentic-ai · **Confidence:** 0.91 → auto-accept
- **Integrity:** sha `f1fbc37a10053d99` · dup group `dup_0267` (1)
- **Caption:** This is the core interface you’ll use to interact with your agent.
- **Paragraph after:** This is the core interface you’ll use to interact with your agent. ● If a message is passed: ○
- **OCR:** L X X J notebook.ipynb class MyAgent: def __init__(self, system = ""): self.system = system self.messages [l if self.system: self.messages.append({"role": "system", "content": system}) complete(self, message=""): if message: self.messages.append({"role": "user", "content": message}) result = self.invoke() self.messages.append({"role": "assistant", "content": result}) return result

### fig_0278 — This method handles the actual API call to your LLM provider - in this case, via

- **Page:** 207 (PDF page 209) · **Chapter:** AI Agents
- **BBox:** [121.12, 67.50, 490.88, 297.00] on page 612×792 pt · **Render:** 1027×638 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.72) · Agent Protocol Fabric (0.63)
- **Primary branch:** agentic-ai · **Confidence:** 0.72 → review queue
- **Integrity:** sha `dc35f4b3514470e8` · dup group `dup_0268` (1)
- **Caption:** This method handles the actual API call to your LLM provider - in this case, via
- **Paragraph after:** This method handles the actual API call to your LLM provider - in this case, via LiteLLM, using the "openai/gpt-4o" model. ● completion() is a wrapper around the chat completion API. It receives the entire message history and returns a response.
- **OCR:** L XN J notebook.ipynb class MyAgent: def __init__(self, system = self.system = system self.messages = [] if self.system: self.messages.append({"role": "system", "content": system}) complete(self, message=" if message: self.messages.append({"role": "user", "content": message}) result = self.invoke() self.messages.append({"role": "assistant", "content": result}) return result invoke(self): lm_response = completion(model="openai/gpt-40", messages=self.messages) return llm_response.choices[@].message.content

### fig_0279 — AI Agents figure

- **Page:** 207 (PDF page 209) · **Chapter:** AI Agents
- **BBox:** [138.38, 498.81, 473.62, 700.56] on page 612×792 pt · **Render:** 931×560 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agentic AI (0.94) · Evaluation (0.41)
- **Primary branch:** agentic-ai · **Confidence:** 0.94 → auto-accept
- **Integrity:** sha `6b305653b19247eb` · dup group `dup_0269` (1)
- **Paragraph before:** We assume completion() returns a structure similar to OpenAI’s format: a list of choices, where each choice has a .message.content field. ● We extract and return that content - the assistant's next response. As a test, we can quickly run a simple interaction below:
- **OCR:** L K J notebook.ipynb my_agent = MyAgent(system="You are a helpful assistant.") my_agent.complete("What is Agentic AI?") Agentic AI refers to artificial intelligence systems that exhibit behaviors or characteristics typically associated with agency, which is the capacity to act autonomously and make decisions.

### fig_0280 — It correctly remembers and reflects!

- **Page:** 208 (PDF page 210) · **Chapter:** AI Agents
- **BBox:** [138.00, 119.08, 474.00, 261.58] on page 612×792 pt · **Render:** 933×396 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Agentic AI (0.86) · LLM Engineering (0.42) · Context Engineering (0.42)
- **Primary branch:** agentic-ai · **Confidence:** 0.86 → auto-accept
- **Integrity:** sha `fa15337b8e811114` · dup group `dup_0270` (1)
- **Caption:** It correctly remembers and reflects!
- **Paragraph before:** At this stage, if we ask it about the previous message, we get the correct output, which shows the assistant has visibility on the previous context:
- **Paragraph after:** It correctly remembers and reflects! Now that our conversational class is setup, we come to the most interesting part, which is defining a ReAct-style prompt. Before an LLM can behave like an agent, it needs clear instructions - not just on
- **OCR:** o000 notebook.ipynb my_agent.complete("What was my last message?") 'Your last message asked about "Agentic AI.™'

### fig_0281 — AI Agents figure

- **Page:** 209 (PDF page 211) · **Chapter:** AI Agents
- **BBox:** [113.62, 67.50, 498.38, 741.00] on page 612×792 pt · **Render:** 914×1600 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agentic AI (0.68) · Evaluation (0.57) · LLM Engineering (0.46)
- **Primary branch:** agentic-ai · **Confidence:** 0.68 → review queue
- **Integrity:** sha `1b96e1d56f270b9f` · dup group `dup_0271` (1)
- **OCR:** (XX notebook.ipynb system_prompt = You run in a loop and do JUST ONE thing in a single iteration: 1) "Thought" to describe your thoughts about the input question. 2) "PAUSE" to pause and think about the action to take. 3) "Action" to decide what action to take from the list of actions available to you. 4) "PAUSE" to pause and wait for the result of the action. 5) "Observation" will be the output returned by the action. At the end of the loop, you produce an Answer. The actions available to you are: math: e.g. math: (14 % 5) / 4 Evaluates mathematical expressions using Python syntax. Lookup_population: e.¢. lookup_population: India Returns the latest known population of the specified country. Here's a sample run for your reference: Question: What is double the population of Japan? Iteration 1: Thought: I need to find the population of Japan first. Iteration 2: PAUSE Iteration 3: Action: l

### fig_0282 — Finally, we begin a manual ReAct session:

- **Page:** 213 (PDF page 215) · **Chapter:** AI Agents
- **BBox:** [144.00, 210.22, 468.00, 456.22] on page 612×792 pt · **Render:** 900×684 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Agentic AI (0.76) · LLM Engineering (0.43) · Tool / Action Fabric (0.43) · Evaluation (0.43)
- **Primary branch:** agentic-ai · **Confidence:** 0.76 → review queue
- **Integrity:** sha `d04051c84a67bcaa` · dup group `dup_0272` (1)
- **Caption:** Finally, we begin a manual ReAct session:
- **Paragraph before:** ● It separates reasoning from execution, mimicking how humans operate. ● It creates a feedback-friendly iteration loop for multi-step problems. Now that the prompt is defined, we implement the tools.
- **Paragraph after:** Finally, we begin a manual ReAct session: This produces the following output: Iteration 1:
- **OCR:** o000 notebook.ipynb def math(expression: str): return eval(expression) def lookup_population(country: str): populations = { "India": 1_400_000_000, "Japan": 125_000_000, "United States": 330_000_000, "Brazil": 210_000_000, "Indonesia": 270_000_000, "Mexico": 126_000_000, "Russia": 145_000_000, "United Kingdom": 67_000_000 } return populations.get(country, "Country not found")

### fig_0283 — This produces the following output:

- **Page:** 213 (PDF page 215) · **Chapter:** AI Agents
- **BBox:** [132.38, 495.52, 479.62, 631.27] on page 612×792 pt · **Render:** 965×377 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agentic AI (0.80) · LLM Engineering (0.48) · Tool / Action Fabric (0.41)
- **Primary branch:** agentic-ai · **Confidence:** 0.80 → review queue
- **Integrity:** sha `217c540333a65f4f` · dup group `dup_0273` (1)
- **Caption:** This produces the following output:
- **Paragraph before:** It separates reasoning from execution, mimicking how humans operate. ● It creates a feedback-friendly iteration loop for multi-step problems. Now that the prompt is defined, we implement the tools. Finally, we begin a manual ReAct session:
- **Paragraph after:** This produces the following output: Iteration 1:
- **OCR:** [ X X notebook.ipynb my_agent = MyAgent(system=system_prompt) my_agent.complete("""What is the population of India plus the population of Japan2?""")

### fig_0284 — This produces the following output:

- **Page:** 214 (PDF page 216) · **Chapter:** AI Agents
- **BBox:** [178.12, 150.86, 433.88, 274.61] on page 612×792 pt · **Render:** 711×343 px
- **Composition:** raster · **Role:** process · **Quality:** 0.6
- **Mapping:** Agentic AI (0.98)
- **Primary branch:** agentic-ai · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `72f7ce22f2a04a9d` · dup group `dup_0274` (7)
- **Caption:** This produces the following output:
- **Paragraph before:** Thought: I need to find the population of India first. We, as a user, don't have any input to give at this stage so we just invoke the complete() method again:
- **Paragraph after:** This produces the following output: Iteration 2: PAUSE Yet again, we, as a user, don't have any input to give at this stage so we just
- **OCR:** \| X J notebook.ipynb my_agent.complete()

### fig_0285 — This produces the following output:

- **Page:** 214 (PDF page 216) · **Chapter:** AI Agents
- **BBox:** [174.38, 429.06, 437.62, 556.56] on page 612×792 pt · **Render:** 731×354 px
- **Composition:** raster · **Role:** process · **Quality:** 0.6
- **Mapping:** Agentic AI (0.98)
- **Primary branch:** agentic-ai · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `20b7ab098ba381b0` · dup group `dup_0274` (7)
- **Caption:** This produces the following output:
- **Paragraph before:** Iteration 2: PAUSE Yet again, we, as a user, don't have any input to give at this stage so we just invoke the complete() method again:
- **Paragraph after:** This produces the following output: Iteration 3: Action: lookup_population: India Now it wants to act.
- **OCR:** L N J notebook.ipynb my_agent.complete()

### fig_0286 — This produces the following output:

- **Page:** 215 (PDF page 217) · **Chapter:** AI Agents
- **BBox:** [160.50, 119.08, 451.50, 259.33] on page 612×792 pt · **Render:** 809×390 px
- **Composition:** raster · **Role:** process · **Quality:** 0.6
- **Mapping:** Agentic AI (0.87) · Tool / Action Fabric (0.48)
- **Primary branch:** agentic-ai · **Confidence:** 0.87 → auto-accept
- **Integrity:** sha `110aca334f75bfd1` · dup group `dup_0274` (7)
- **Caption:** This produces the following output:
- **Paragraph before:** We still don't have any input to give at this stage so we just invoke the complete() method again:
- **Paragraph after:** This produces the following output: Iteration 4: PAUSE At this stage, it needs to get the tool output in the form of an observation. Here,
- **OCR:** \| X J notebook.ipynb my_agent.complete()

### fig_0287 — This produces the following output:

- **Page:** 215 (PDF page 217) · **Chapter:** AI Agents
- **BBox:** [121.88, 413.77, 490.12, 517.27] on page 612×792 pt · **Render:** 1023×287 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Agentic AI (0.87) · Tool / Action Fabric (0.48)
- **Primary branch:** agentic-ai · **Confidence:** 0.87 → auto-accept
- **Integrity:** sha `a4b8e0222f9dbc38` · dup group `dup_0275` (2)
- **Caption:** This produces the following output:
- **Paragraph before:** Iteration 4: PAUSE At this stage, it needs to get the tool output in the form of an observation. Here, let's intervene and provide it with the observation:
- **Paragraph after:** This produces the following output: Iteration 5: Thought: Now I need to find the population of Japan. We let it continue its execution:
- **OCR:** ( X J notebook.ipynb my_agent.complete(f"Observation: {lookup_population('India')}")

### fig_0288 — This produces the following output:

- **Page:** 216 (PDF page 218) · **Chapter:** AI Agents
- **BBox:** [160.50, 67.50, 451.50, 207.75] on page 612×792 pt · **Render:** 809×390 px
- **Composition:** raster · **Role:** result · **Quality:** 0.6
- **Mapping:** Agentic AI (0.98)
- **Primary branch:** agentic-ai · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `110aca334f75bfd1` · dup group `dup_0274` (7)
- **Caption:** This produces the following output:
- **Paragraph after:** This produces the following output: Iteration 6: PAUSE We again let it continue its execution:
- **OCR:** \| X J notebook.ipynb my_agent.complete()

### fig_0289 — We get the following output:

- **Page:** 216 (PDF page 218) · **Chapter:** AI Agents
- **BBox:** [160.50, 342.41, 451.50, 482.66] on page 612×792 pt · **Render:** 809×389 px
- **Composition:** raster · **Role:** process · **Quality:** 0.6
- **Mapping:** Agentic AI (0.87) · Tool / Action Fabric (0.48)
- **Primary branch:** agentic-ai · **Confidence:** 0.87 → auto-accept
- **Integrity:** sha `2c1ebec5721977d3` · dup group `dup_0274` (7)
- **Caption:** We get the following output:
- **Paragraph before:** This produces the following output: Iteration 6: PAUSE We again let it continue its execution:
- **Paragraph after:** We get the following output: Iteration 7: Action: lookup_population: Japan At this stage, it needs to get the tool output in the form of an observation. Here,
- **OCR:** o0 notebook.ipynb my_agent.complete()

### fig_0290 — This produces the following output:

- **Page:** 217 (PDF page 219) · **Chapter:** AI Agents
- **BBox:** [99.38, 67.50, 512.62, 183.00] on page 612×792 pt · **Render:** 1147×321 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Agentic AI (0.98)
- **Primary branch:** agentic-ai · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `2bdf140c65271039` · dup group `dup_0275` (2)
- **Caption:** This produces the following output:
- **Paragraph after:** This produces the following output: Iteration 8: Thought: I now have the populations of both India and Japan. I need to add them together.
- **OCR:** o0 notebook.ipynb \| my_agent.complete(f"Observation: {lookup_population('Japan')}")

### fig_0291 — We get the following output:

- **Page:** 217 (PDF page 219) · **Chapter:** AI Agents
- **BBox:** [160.50, 337.45, 451.50, 477.70] on page 612×792 pt · **Render:** 809×389 px
- **Composition:** raster · **Role:** result · **Quality:** 0.6
- **Mapping:** Agentic AI (0.98)
- **Primary branch:** agentic-ai · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `ad1b3ed7fd058751` · dup group `dup_0274` (7)
- **Caption:** We get the following output:
- **Paragraph before:** Iteration 8: Thought: I now have the populations of both India and Japan. I need to add them together. We again let it continue its execution:
- **Paragraph after:** We get the following output: Iteration 9: Action: math: 1400000000 + 125000000 Now we should expect a pause according to the pattern specified:
- **OCR:** \| X J notebook.ipynb my_agent.complete()

### fig_0292 — Iteration 10:

- **Page:** 218 (PDF page 220) · **Chapter:** AI Agents
- **BBox:** [160.50, 67.50, 451.50, 207.75] on page 612×792 pt · **Render:** 809×390 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.6
- **Mapping:** Agentic AI (0.98)
- **Primary branch:** agentic-ai · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `110aca334f75bfd1` · dup group `dup_0274` (7)
- **Caption:** Iteration 10:
- **Paragraph after:** Iteration 10: PAUSE It is again seeking an observation, which is the sum of Japan's population and India's population. To do this, we again manually intervene and provide it with
- **OCR:** \| X J notebook.ipynb my_agent.complete()

### fig_0293 — Finally, in this iteration, we get the following output:

- **Page:** 218 (PDF page 220) · **Chapter:** AI Agents
- **BBox:** [109.88, 350.20, 502.12, 452.95] on page 612×792 pt · **Render:** 1089×286 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Agentic AI (0.98)
- **Primary branch:** agentic-ai · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `04e60e49015b32ff` · dup group `dup_0276` (1)
- **Caption:** Finally, in this iteration, we get the following output:
- **Paragraph before:** PAUSE It is again seeking an observation, which is the sum of Japan's population and India's population. To do this, we again manually intervene and provide it with the output:
- **Paragraph after:** Finally, in this iteration, we get the following output: Iteration 11: Answer: The sum of the population of India and the population of Japan is 1,525,000,000.
- **OCR:** L N ] notebook.ipynb my_agent.complete(f"Observation: {math('125000000 + 1400000000')}")

### fig_0294 — Let’s break down the full loop.

- **Page:** 220 (PDF page 222) · **Chapter:** AI Agents
- **BBox:** [107.25, 67.50, 504.75, 573.00] on page 612×792 pt · **Render:** 1105×1404 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.56) · Tool / Action Fabric (0.56) · Agentic AI (0.54) · RAG / Knowledge Engineering (0.40)
- **Primary branch:** llm-engineering · **Confidence:** 0.56 → review queue
- **Integrity:** sha `217929c410dd41b4` · dup group `dup_0277` (1)
- **Caption:** Let’s break down the full loop.
- **Paragraph after:** Let’s break down the full loop. We begin by defining the agent_loop() function: It takes: ●
- **OCR:** L X J notebook.ipynb import re def agent_loop(query, system_prompt: str = my_agent = MyAgent(system=system_prompt) available_tools = {"math": math "lookup_population": lookup_population} current_prompt = query previous_step = while "ANSWER" not in current_prompt 1lm_response = my_agent.complete(current_prompt) print(llm_response) if "Answer" in llm_response: break elif "Thought:" in 1lm_response previous_step current_prompt = elif "PAUSE" in llm_response and previous_step = "Thought": current_prompt = "" previous_step = "PAUSE" elif "Action:" in llm_response: previous_step = "Action" pattern = r"Action:\sx(\w+):\sx(.+)" match = re.search(pattern, llm_response) if match: chosen_tool = match.group(1) arg = match.group(2) if chosen_tool in available_tools: observation = available_tools[chosen_tool](arg) current_prompt = f"Observation: {observation}" else: current_prompt = f"Observation: Too

### fig_0295 — ●

- **Page:** 221 (PDF page 223) · **Chapter:** AI Agents
- **BBox:** [127.12, 150.86, 484.88, 371.36] on page 612×792 pt · **Render:** 993×612 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.69) · LLM Engineering (0.52) · Tool / Action Fabric (0.46) · RAG / Knowledge Engineering (0.38)
- **Primary branch:** agentic-ai · **Confidence:** 0.69 → review queue
- **Integrity:** sha `cba4b6814996375f` · dup group `dup_0278` (1)
- **Caption:** ●
- **Paragraph before:** ● system_prompt: the same ReAct system prompt we explored earlier (defining the behavior loop). Next, inside this function, we initialize the Agent and available tools:
- **Paragraph after:** ● Create a new MyAgent instance, using the structured ReAct prompt. ● Define the dictionary of callable tools available to the agent. These names must match exactly what the agent uses in its Action: lines.
- **OCR:** LN N J notebook.ipynb import re def agent_loop(query, system_prompt: str = ""): my_agent = MyAgent(system=system_prompt) available_tools = { "math": math, "lookup_population”: lookup_population

### fig_0296 — current_prompt stores the next message to be sent to the LLM.

- **Page:** 222 (PDF page 224) · **Chapter:** AI Agents
- **BBox:** [138.00, 67.50, 474.00, 310.50] on page 612×792 pt · **Render:** 933×675 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.63) · LLM Engineering (0.55) · RAG / Knowledge Engineering (0.43) · Data Engineering (0.43)
- **Primary branch:** agentic-ai · **Confidence:** 0.63 → review queue
- **Integrity:** sha `5bdd67219fecdc73` · dup group `dup_0279` (1)
- **Caption:** current_prompt stores the next message to be sent to the LLM.
- **Paragraph after:** current_prompt stores the next message to be sent to the LLM. previous_step helps track the last stage (e.g., Thought, Action) for better control flow. Next, we run the reasoning loop, which continues until the agent produces a final
- **OCR:** [ X X J notebook.ipynb import re def agent_loop(query, system_prompt: str = ""): my_agent = MyAgent(system=system_prompt) available_tools = "math": math, "lookup_population”: lookup_population current_prompt = query previous_step = ""

### fig_0297 — Next, we feed the current_prompt into the agent.

- **Page:** 223 (PDF page 225) · **Chapter:** AI Agents
- **BBox:** [128.25, 67.50, 483.75, 348.75] on page 612×792 pt · **Render:** 987×781 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.64) · LLM Engineering (0.60) · RAG / Knowledge Engineering (0.42) · Tool / Action Fabric (0.39)
- **Primary branch:** agentic-ai · **Confidence:** 0.64 → review queue
- **Integrity:** sha `e51f72cef13efa3c` · dup group `dup_0280` (1)
- **Caption:** Next, we feed the current_prompt into the agent.
- **Paragraph after:** Next, we feed the current_prompt into the agent. The current_prompt could be:
- **OCR:** 000 notebook.ipynb import re def agent_loop(query, system_prompt: str = ""): my_agent = MyAgent(system=system_prompt) available_tools = "math": math, "lookup_population”: lookup_population current_prompt = query previous_step = "" while "ANSWER" not in current_prompt:

### fig_0298 — The current_prompt could be:

- **Page:** 223 (PDF page 225) · **Chapter:** AI Agents
- **BBox:** [131.25, 388.06, 480.75, 679.06] on page 612×792 pt · **Render:** 971×809 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.62) · Agentic AI (0.62) · RAG / Knowledge Engineering (0.42) · Tool / Action Fabric (0.38)
- **Primary branch:** llm-engineering · **Confidence:** 0.62 → review queue
- **Integrity:** sha `0bb16765810b8080` · dup group `dup_0281` (1)
- **Caption:** The current_prompt could be:
- **Paragraph before:** Next, we feed the current_prompt into the agent.
- **Paragraph after:** The current_prompt could be:
- **OCR:** [ X X J notebook.ipynb import re def agent_loop(query, system_prompt: str = ""): my_agent = MyAgent(system=system_prompt) available_tools = "math": math, "lookup_population”: lookup_population current_prompt = query previous_step = "" while "ANSWER" not in current_prompt: 1lm_response = my_agent.complete(current_prompt) print(llm_response)

### fig_0299 — In another case, if the response includes a Thought: line, we:

- **Page:** 224 (PDF page 226) · **Chapter:** AI Agents
- **BBox:** [136.88, 202.44, 475.12, 518.19] on page 612×792 pt · **Render:** 939×877 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.66) · LLM Engineering (0.56) · RAG / Knowledge Engineering (0.42) · Tool / Action Fabric (0.42)
- **Primary branch:** agentic-ai · **Confidence:** 0.66 → review queue
- **Integrity:** sha `9ff5994900d9cf85` · dup group `dup_0282` (1)
- **Caption:** In another case, if the response includes a Thought: line, we:
- **Paragraph before:** ● An observation from a tool. We then print the agent’s output, so we can inspect each iteration. Next, if the agent produces a final answer, we break the loop.
- **Paragraph after:** In another case, if the response includes a Thought: line, we: ● Record the step type as "Thought". ● Set current_prompt to an empty string to continue to the next stage (a
- **OCR:** [ X X J notebook.ipynb import re def agent_loop(query, system_prompt: str = ""): my_agent = MyAgent(system=system_prompt) available_tools = "math": math, "lookup_population": lookup_population current_prompt = query previous_step = "" while "ANSWER" not in current_prompt: 1lm_response = my_agent.complete(current_prompt) print(llm_response) if "Answer" in llm_response: break

### fig_0300 — Next, we catch the first PAUSE right after the Thought. Nothing else needs to be

- **Page:** 225 (PDF page 227) · **Chapter:** AI Agents
- **BBox:** [153.38, 67.50, 494.62, 413.25] on page 612×792 pt · **Render:** 947×960 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.63) · LLM Engineering (0.59) · RAG / Knowledge Engineering (0.43) · Tool / Action Fabric (0.39)
- **Primary branch:** agentic-ai · **Confidence:** 0.63 → review queue
- **Integrity:** sha `e645827b56229689` · dup group `dup_0283` (1)
- **Caption:** Next, we catch the first PAUSE right after the Thought. Nothing else needs to be
- **Paragraph after:** Next, we catch the first PAUSE right after the Thought. Nothing else needs to be done here - we just move to the next step.
- **OCR:** LXK J notebook.ipynb import re def agent_loop(query, system_prompt: str = ""): my_agent = MyAgent(system=system_prompt) available_tools = "math": math, "lookup_population”: lookup_population current_prompt = query previous_step = "" while "ANSWER" not in current_prompt: 1lm_response = my_agent.complete(current_prompt) print(llm_response) if "Answer" in llm_response: break elif "Thought:"™ in llm_response: previous_step = "Thought" current_prompt = "*

### fig_0301 — If we detect an Action: line, we:

- **Page:** 226 (PDF page 228) · **Chapter:** AI Agents
- **BBox:** [132.38, 67.50, 479.62, 431.25] on page 612×792 pt · **Render:** 965×1010 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.62) · Agentic AI (0.58) · RAG / Knowledge Engineering (0.43) · Tool / Action Fabric (0.43)
- **Primary branch:** llm-engineering · **Confidence:** 0.62 → review queue
- **Integrity:** sha `c5da014f01c861f2` · dup group `dup_0284` (1)
- **Caption:** If we detect an Action: line, we:
- **Paragraph after:** If we detect an Action: line, we: ● Note that we're in the action step. ● Use a regex to extract the tool name and its argument.
- **OCR:** L X J notebook.ipynb import re def agent_loop(query, system_prompt: str = ""): my_agent = MyAgent(system=system_prompt) available_tools = "math": math, "lookup_population”: lookup_population current_prompt = query previous_step = "" while "ANSWER" not in current_prompt: 1lm_response = my_asgent.complete(current_prompt) print(llm_response) if "Answer" in llm_response: break elif "Thought:" in llm_response: previous_step = "Thought™ current_prompt = "" elif "PAUSE" in llm_response and previous_step = "Thought": current_prompt = "" previous_step = "PAUSE" continue

### fig_0302 — For example, in: Action: lookup_population: India, the regex pulls out:

- **Page:** 227 (PDF page 229) · **Chapter:** AI Agents
- **BBox:** [150.75, 67.50, 497.25, 415.50] on page 612×792 pt · **Render:** 963×967 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.63) · LLM Engineering (0.54) · RAG / Knowledge Engineering (0.44) · Tool / Action Fabric (0.44)
- **Primary branch:** agentic-ai · **Confidence:** 0.63 → review queue
- **Integrity:** sha `dc1192ab53c6cefe` · dup group `dup_0285` (1)
- **Caption:** For example, in: Action: lookup_population: India, the regex pulls out:
- **Paragraph after:** For example, in: Action: lookup_population: India, the regex pulls out: ● lookup_population as the tool. ●
- **OCR:** [ X X J notebook.ipynb import re def agent_loop(query, system_prompt: str = ""): my_agent = MyAgent(system=system_prompt) available_tools = "math": math, "Lookup_population”: Llookup_population current_prompt = query previous_step = "" while "ANSWER" not in current_prompt: elif "Action:" in Ulm_response: previous_step = "Action" pattern = r"Action:\sx(\w+):\s*(.+)" match = re.search(pattern, llm_response)

### fig_0303 — ● If the tool name is valid, we call it like a Python function and capture the

- **Page:** 228 (PDF page 230) · **Chapter:** AI Agents
- **BBox:** [127.12, 67.50, 484.88, 438.00] on page 612×792 pt · **Render:** 993×1029 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Tool / Action Fabric (0.64) · LLM Engineering (0.51) · Agentic AI (0.51) · RAG / Knowledge Engineering (0.40)
- **Primary branch:** tool-action-fabric · **Confidence:** 0.64 → review queue
- **Integrity:** sha `e86068543cd1ab53` · dup group `dup_0286` (1)
- **Caption:** ● If the tool name is valid, we call it like a Python function and capture the
- **Paragraph after:** ● If the tool name is valid, we call it like a Python function and capture the result. ● We format the output into Observation: ... so the agent can use it in the
- **OCR:** (XX} notebook ipynb import re def agent_loop(query, system_prompt: str = ""): my_agent = MyAdent(system=system_prompt) available_tools = { "math": math, "Llookup_population": lookup_population current_prompt = query previous_step = "" while "ANSWER" not in current_prompt: elif "Action:"™ in llm_response: previous_step = "Action" pattern = r"Action:\sx(\w+):\s«(.+)" match = re.search(pattern, llm_response) if match: chosen_tool - match.group(1) arg - match.group(2) if chosen_tool in available_tools: observation = available_tools[chosen_tool](arg) current_prompt - f"Observation: {observation}" else: current_prompt = f"Observation: Tool unavailable. Retry."

### fig_0304 — This produces the following output, which is indeed correct:

- **Page:** 229 (PDF page 231) · **Chapter:** AI Agents
- **BBox:** [163.50, 67.50, 448.50, 189.75] on page 612×792 pt · **Render:** 791×340 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agentic AI (0.89) · LLM Engineering (0.46)
- **Primary branch:** agentic-ai · **Confidence:** 0.89 → auto-accept
- **Integrity:** sha `f0ca9ccfd8618da2` · dup group `dup_0287` (1)
- **Caption:** This produces the following output, which is indeed correct:
- **Paragraph after:** This produces the following output, which is indeed correct: You now have a fully working ReAct loop without needing any external framework. Of course, In this implementation, we’re using regex matching and hardcoded
- **OCR:** [ X J notebook.ipynb agent_loop("""what is the population of India plus the population of Japan?""", system_prompt)

### fig_0305 — You now have a fully working ReAct loop without needing any external

- **Page:** 229 (PDF page 231) · **Chapter:** AI Agents
- **BBox:** [112.50, 229.06, 499.50, 457.06] on page 612×792 pt · **Render:** 1075×633 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agentic AI (0.73) · Tool / Action Fabric (0.57) · LLM Engineering (0.40)
- **Primary branch:** agentic-ai · **Confidence:** 0.73 → review queue
- **Integrity:** sha `41ff7bbec253f4bb` · dup group `dup_0288` (1)
- **Caption:** You now have a fully working ReAct loop without needing any external
- **Paragraph before:** This produces the following output, which is indeed correct:
- **Paragraph after:** You now have a fully working ReAct loop without needing any external framework. Of course, In this implementation, we’re using regex matching and hardcoded conditionals to parse the agent’s actions and route them to the correct tools.
- **OCR:** agent_loop("What is the population of India plus the population of Japan?", system_prompt) v 79s Iteration 1: Thought: T need to find the population of India first. Iteration 2: PAUSE Iteration 3: Action: lookup_population: India tool found!! Iteration 4: Thought: I have the population of India. Now I need to find the population of Japan. Iteration 5: PAUSE Iteration 6: Action: lookup_population: Japan tool found!! Iteration 7: Thought: I now have the populations of both India and Japan. I need to add these two numbers together to get Iteration 8: Action: math: 1400000000 + 125000000 tool found!! Iteration 9: Answer: The combined population of India and Japan is 1,525,000,000.

### fig_0306 — 1) Basic responder

- **Page:** 231 (PDF page 233) · **Chapter:** AI Agents
- **BBox:** [111.75, 67.50, 500.25, 507.00] on page 612×792 pt · **Render:** 1079×1221 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.89) · LLM Engineering (0.46)
- **Primary branch:** agentic-ai · **Confidence:** 0.89 → auto-accept
- **Integrity:** sha `163d6bd8f4a8208f` · dup group `dup_0289` (1)
- **Caption:** 1) Basic responder
- **Paragraph after:** 1) Basic responder
- **OCR:** S Levels of Agentic AT Systems e Join.DailyDoseofDS.com 20 1) Basic Responder Prompt deepseelk Large language model 2) Router Pattern o deepseek response \| €~ [ despsesi \| €~ - wm o] Validator Agent

### fig_0307 — A human guides the entire flow.

- **Page:** 232 (PDF page 234) · **Chapter:** AI Agents
- **BBox:** [172.12, 67.50, 439.88, 273.75] on page 612×792 pt · **Render:** 743×573 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.98)
- **Primary branch:** agentic-ai · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `8263fc70e5ebf95a` · dup group `dup_0290` (1)
- **Caption:** A human guides the entire flow.
- **Paragraph after:** A human guides the entire flow. The LLM is just a generic responder that receives an input and produces an output. It has little control over the program flow. 2) Router pattern
- **OCR:** 1) Basic Responder deepseel Large language model I wm Response response

### fig_0308 — 2) Router pattern

- **Page:** 232 (PDF page 234) · **Chapter:** AI Agents
- **BBox:** [168.00, 388.72, 444.00, 604.72] on page 612×792 pt · **Render:** 767×600 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.68) · Tool / Action Fabric (0.68)
- **Primary branch:** agentic-ai · **Confidence:** 0.68 → review queue
- **Integrity:** sha `c5fe3da108657e38` · dup group `dup_0291` (1)
- **Heading:** 2) Router pattern
- **Caption:** A human defines the paths/functions that exist in the flow.
- **Paragraph before:** A human guides the entire flow. The LLM is just a generic responder that receives an input and produces an output. It has little control over the program flow. 2) Router pattern
- **Paragraph after:** A human defines the paths/functions that exist in the flow. The LLM makes basic decisions on which function or path it can take. 3) Tool calling
- **OCR:** 2) Router Pattern o deepseeck Router LLM deepseek LM Route 1 response

### fig_0309 — A human defines a set of tools the LLM can access to complete a task.

- **Page:** 233 (PDF page 235) · **Chapter:** AI Agents
- **BBox:** [168.00, 67.50, 444.00, 282.75] on page 612×792 pt · **Render:** 767×598 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Agentic AI (0.73) · Tool / Action Fabric (0.57) · Multi-Agent (0.40)
- **Primary branch:** agentic-ai · **Confidence:** 0.73 → review queue
- **Integrity:** sha `5188e869a223fff6` · dup group `dup_0292` (1)
- **Caption:** A human defines a set of tools the LLM can access to complete a task.
- **Paragraph after:** A human defines a set of tools the LLM can access to complete a task. LLM decides when to use them and also the arguments for execution. 4) Multi-agent pattern A manager agent coordinates multiple sub-agents and decides the next steps
- **OCR:** response 3) Tool Calling L\ deepseeck wm ! Tool ; calling deepseel \| €<— = um

### fig_0310 — 4) Multi-agent pattern

- **Page:** 233 (PDF page 235) · **Chapter:** AI Agents
- **BBox:** [174.75, 377.94, 437.25, 573.69] on page 612×792 pt · **Render:** 729×544 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.81) · Multi-Agent (0.46) · Tool / Action Fabric (0.43)
- **Primary branch:** agentic-ai · **Confidence:** 0.81 → review queue
- **Integrity:** sha `786d805b3c6e1162` · dup group `dup_0293` (1)
- **Heading:** 4) Multi-agent pattern
- **Caption:** A manager agent coordinates multiple sub-agents and decides the next steps
- **Paragraph before:** A human defines a set of tools the LLM can access to complete a task. LLM decides when to use them and also the arguments for execution. 4) Multi-agent pattern
- **Paragraph after:** A manager agent coordinates multiple sub-agents and decides the next steps iteratively. A human lays out the hierarchy between agents, their roles, tools, etc. The LLM controls execution flow, deciding what to do next.
- **OCR:** 4) Multi-agent Pattern <L Manager Agent response

### fig_0311 — The most advanced pattern, wherein, the LLM generates and executes new code

- **Page:** 234 (PDF page 236) · **Chapter:** AI Agents
- **BBox:** [172.88, 67.50, 439.12, 264.00] on page 612×792 pt · **Render:** 739×546 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agentic AI (0.98)
- **Primary branch:** agentic-ai · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `8ee8e9293a19342d` · dup group `dup_0294` (1)
- **Caption:** The most advanced pattern, wherein, the LLM generates and executes new code
- **Paragraph after:** The most advanced pattern, wherein, the LLM generates and executes new code independently, effectively acting as an independent AI developer. Must-Know Agentic AI Terms We put together a quick visual guide to the most important terms in Agentic
- **OCR:** S) Autonomous Pattern Final response Generator Agent A ] dback : : Response 1 v o/ 1 L Validator Agent

### fig_0312 — Agent: An autonomous AI entity that perceives, reasons, and acts toward a goal

- **Page:** 235 (PDF page 237) · **Chapter:** AI Agents
- **BBox:** [117.38, 67.50, 494.62, 390.00] on page 612×792 pt · **Render:** 1047×896 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.84) · Context Engineering (0.43) · Agent Orchestration (0.39) · Agent Protocol Fabric (0.39)
- **Primary branch:** agentic-ai · **Confidence:** 0.84 → review queue
- **Integrity:** sha `dc6e52f04ec6c429` · dup group `dup_0295` (1)
- **Caption:** Agent: An autonomous AI entity that perceives, reasons, and acts toward a goal
- **Paragraph after:** Agent: An autonomous AI entity that perceives, reasons, and acts toward a goal (covered with full implementations here). Environment: The world or system in which an agent operates and interacts. Action: A response or task performed by an agent based on its reasoning or
- **OCR:** 30 Agentic Al Terms e e Environment Action 4 Aresponteor G periorad oy o agem: Observation Goal © ratan A sgont APt o tites sea by ‘sgents to extond hex unctionatey. Assesing how wel a0 agont prforma against e onded gols. Orchestration Agroup ot werking toge Human-in-the-Loop Planning = L—} The process o aetermining stops toreach a gonl Context Window Hierarchical Agents s Mot sgent system where 2 Suparvaar gont dowgaas a5k 0 spec.alied sgents. Knowledge Base Tool Call by an sgent o Constraints o polcies erming 358 behador o ke them aigned. DailyDoseofDS.com

### fig_0313 — Reflection: The agent’s process of self-assessing its actions to improve future

- **Page:** 236 (PDF page 238) · **Chapter:** AI Agents
- **BBox:** [109.50, 265.80, 502.50, 397.80] on page 612×792 pt · **Render:** 1091×367 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.86) · Agent Protocol Fabric (0.44) · Multi-Agent (0.40)
- **Primary branch:** agentic-ai · **Confidence:** 0.86 → auto-accept
- **Integrity:** sha `692c4613b346fad5` · dup group `dup_0296` (1)
- **Caption:** Reflection: The agent’s process of self-assessing its actions to improve future
- **Paragraph before:** Multi-agent system: A group of agents collaborating to accomplish a final goal (implemented from scratch in pure Python here). Human-in-the-loop: A setup where humans intervene or guide the agent’s decision-making process.
- **Paragraph after:** Reflection: The agent’s process of self-assessing its actions to improve future performance. Planning: Determining the sequence of steps an agent must take to reach its goal (implemented from scratch in pure Python here).
- **OCR:** Going well A swall mistake perfect output L Step 1 Step 3 Step 4 Step 5

### fig_0314 — ARQ: A new structured reasoning approach where an agent solves complex,

- **Page:** 237 (PDF page 239) · **Chapter:** AI Agents
- **BBox:** [124.50, 493.86, 487.50, 663.36] on page 612×792 pt · **Render:** 1009×471 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.80) · Tool / Action Fabric (0.45) · LLM Engineering (0.40) · Agent Protocol Fabric (0.40)
- **Primary branch:** agentic-ai · **Confidence:** 0.80 → review queue
- **Integrity:** sha `b9006ea89ec9cba6` · dup group `dup_0297` (1)
- **Caption:** ARQ: A new structured reasoning approach where an agent solves complex,
- **Paragraph before:** undesired actions (covered with code here). Tool call: An API invocation made by an agent to perform a specific task. Guidelines: Policies or constraints that keep an agent’s behavior aligned with desired outcomes.
- **Paragraph after:** ARQ: A new structured reasoning approach where an agent solves complex, domain-specific problems step by step (covered here).
- **OCR:** # Tr ona hroach s your ers system_prompt = "You are a helpful assistant. Here are 50 rules..." darlant roach: Er i compliance @ await agent.create_guideline( condition="Customer asks about refunds", action="Check order status first to see if eligible", tools=[check_order_status],

### fig_0315 — MCP: A standardized way for agents to connect to external tools, APIs, and data

- **Page:** 238 (PDF page 240) · **Chapter:** AI Agents
- **BBox:** [151.12, 67.50, 460.88, 291.00] on page 612×792 pt · **Render:** 861×621 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.68) · Agentic AI (0.51) · Tool / Action Fabric (0.45) · Agent Orchestration (0.41)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.68 → review queue
- **Integrity:** sha `8f81e5e542845d62` · dup group `dup_0073` (2)
- **Caption:** MCP: A standardized way for agents to connect to external tools, APIs, and data
- **Paragraph after:** MCP: A standardized way for agents to connect to external tools, APIs, and data sources (learn how to build MCP servers, MCP clients, JSON-RPC, Sampling, Security, Sandboxing in MCPs, and using LangGraph/LlamaIndex/CrewAI/PydanticAI with MCP here).
- **OCR:** lAEQ : Structured Reasoning Approach that Prevents Hallucinations *Reasoning is solely dependent ‘on LLMs capabilty. Chain of Thought LM Reasoning _ & === => \|[5] ovtput -~ >[step2]- — >[stepn Reasoning chain & _ T 7 ] i "" S 1] - - > [F 7] - - > [ bl respgnse v 4 el

### fig_0316 — AI Agents figure

- **Page:** 238 (PDF page 240) · **Chapter:** AI Agents
- **BBox:** [152.62, 435.23, 459.38, 718.73] on page 612×792 pt · **Render:** 853×788 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.65) · Agent Protocol Fabric (0.61) · Context Engineering (0.41) · RAG / Knowledge Engineering (0.39)
- **Primary branch:** agentic-ai · **Confidence:** 0.65 → review queue
- **Integrity:** sha `4c7df2e19d04d42e` · dup group `dup_0298` (2)
- **Paragraph before:** Security, Sandboxing in MCPs, and using LangGraph/LlamaIndex/CrewAI/PydanticAI with MCP here). A2A: Agent-to-Agent protocol enabling agents to communicate and exchange data directly (here’s a visual guide).
- **OCR:** ' Agent2Agent Protocol vs. Model Context Protocol Agent2Agent Protocol Target Agent Agent2Agent Source Agent Protocol Model Context Protocol Model context Source Agent Protocol (MCP) Vector DB Local file system Bjo&“ JoinDailyDoseofDS.com

### fig_0317 — Layers of Agentic AI

- **Page:** 239 (PDF page 241) · **Chapter:** AI Agents
- **BBox:** [137.62, 279.81, 474.38, 645.81] on page 612×792 pt · **Render:** 935×1016 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agentic AI (0.79) · Agent Orchestration (0.42) · n8n / Workflow Automation (0.42) · Observability (0.42)
- **Primary branch:** agentic-ai · **Confidence:** 0.79 → review queue
- **Integrity:** sha `cb95ef0cf26775e2` · dup group `dup_0299` (1)
- **Heading:** Layers of Agentic AI
- **Caption:** Let’s break it down layer by layer:
- **Paragraph before:** Layers of Agentic AI The following graphic depicts a layered overview of Agentic AI concepts, depicting how the ecosystem is structured from the ground up (LLMs) to higher-level orchestration (Agentic Infrastructure).
- **Paragraph after:** Let’s break it down layer by layer: 1) LLMs (foundation layer)
- **OCR:** \| X33 concepts e — Agentic Infrastructure B e Observability e — S Euies & Logging o Security & Access Control Human-in-the-Loop Controls, AGENTIC SYSTEMS (MULTI-AGENT SYSTEMS) Rate limiting & Cost Management Inter-Agent e Routing & Scheduling Communication Orchestration i Framewroks : AGENTS Workflow b Automation / ToolUsage Agent

### fig_0318 — 1) Parallel

- **Page:** 242 (PDF page 244) · **Chapter:** AI Agents
- **BBox:** [136.88, 117.06, 475.12, 540.06] on page 612×792 pt · **Render:** 939×1175 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.88) · RAG / Knowledge Engineering (0.40) · Multi-Agent (0.40) · Agent Orchestration (0.38)
- **Primary branch:** agentic-ai · **Confidence:** 0.88 → auto-accept
- **Integrity:** sha `f395a89a7f419ae8` · dup group `dup_0300` (1)
- **Caption:** 1) Parallel
- **Paragraph before:** This visual explains the core patterns of multi-agent orchestration, each suited for specific workflows:
- **Paragraph after:** 1) Parallel Each agent tackles a different subtask, like data extraction, web retrieval, and summarization, and their outputs merge into a single result. Perfect for reducing latency in high-throughput pipelines like document parsing
- **OCR:** NZIOER I Multi-Agent System [EREEERFISE @ AL \| oty L& Agent . Multiple agents work at once \| In \| : = on different parts of the same — \| @ AT \| s task, then merge results. B agent \| One agent finishes its part Sequential [ T i — 1 ‘ rol,g \| and hands the result off to — \| AL AL L5250 the next, like steps in a chain. \| Agent \| Agent Agents keep improving their work based on feedback until the result feels right. A central agent decides which agent handles each task based on the input or goal. Many agents produce outputs that a main agent combines into one final result. AL Agent [ _ar \|\| SRR G poentll Agents connect like \| Aggnt \| _,lL out J a web - sharing insights ;*H]_-[ AT \|l and deciding collectively. Agent \| — Higher-level agents guide and assign tasks to others - like a manager leading a team.

### fig_0319 — Agent2Agent(A2A) Protocol

- **Page:** 244 (PDF page 246) · **Chapter:** AI Agents
- **BBox:** [131.25, 390.75, 480.75, 715.50] on page 612×792 pt · **Render:** 971×902 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.67) · Agent Protocol Fabric (0.61) · Context Engineering (0.41) · RAG / Knowledge Engineering (0.37)
- **Primary branch:** agentic-ai · **Confidence:** 0.67 → review queue
- **Integrity:** sha `4488bc5f0a6e9a4d` · dup group `dup_0298` (2)
- **Heading:** Agent2Agent(A2A) Protocol
- **Paragraph before:** ● The system collectively feels smarter than any individual part. Agent2Agent(A2A) Protocol Agentic applications require both A2A and MCP.
- **OCR:** ' Agent2Agent Protocol vs. Model Context Protocol Agent2Agent Protocol Target Agent Agent2Agent Source Agent Model Context Protocol Model context Source Agent Protocol (MCP) = Vector DB s Local file %0 system %&jainbailybosmfbicom

### fig_0320 — Instead, they communicate by exchanging context, task updates, instructions,

- **Page:** 245 (PDF page 247) · **Chapter:** AI Agents
- **BBox:** [131.62, 424.72, 480.38, 621.22] on page 612×792 pt · **Render:** 969×546 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agentic AI (0.71) · Agent Protocol Fabric (0.53) · Context Engineering (0.42) · Agent Memory (0.39)
- **Primary branch:** agentic-ai · **Confidence:** 0.71 → review queue
- **Integrity:** sha `0501c046083d0d75` · dup group `dup_0301` (1)
- **Caption:** Instead, they communicate by exchanging context, task updates, instructions,
- **Paragraph before:** In that sense, they do not compete with each other. To explain further, Agent2Agent (A2A) enables multiple AI agents to work together on tasks without directly sharing their internal memory, thoughts, or tools.
- **Paragraph after:** Instead, they communicate by exchanging context, task updates, instructions, and data. Essentially, AI applications can model A2A agents as MCP resources,
- **OCR:** ~— N User Client Remote Agent 2 Agent , d;/ SED Remote Agent 3

### fig_0321 — Using this, AI agents connecting to an MCP server can discover new agents to

- **Page:** 246 (PDF page 248) · **Chapter:** AI Agents
- **BBox:** [127.12, 97.28, 484.88, 346.28] on page 612×792 pt · **Render:** 993×691 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.66) · Agentic AI (0.60) · Infrastructure (0.41) · Security (0.37)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.66 → review queue
- **Integrity:** sha `dfa12bf23df13376` · dup group `dup_0302` (1)
- **Caption:** Using this, AI agents connecting to an MCP server can discover new agents to
- **Paragraph before:** represented by their AgentCard (more about it shortly).
- **Paragraph after:** Using this, AI agents connecting to an MCP server can discover new agents to collaborate with and connect via the A2A protocol. A2A-supporting Remote Agents must publish a "JSON Agent Card" detailing their capabilities and authentication.
- **OCR:** m MCP VS. A2A Protocol LL DailyDoseOfDS.com MCP Host - == MCP Host : 7 g : MCP Server - \| Agent2 ( y \| . : - @ ------ (] """""" st [Eowe] : MCP Host Agent 1 ----------- W i

### fig_0322 — A2A-supporting Remote Agents must publish a "JSON Agent Card" detailing

- **Page:** 246 (PDF page 248) · **Chapter:** AI Agents
- **BBox:** [156.00, 401.38, 456.00, 597.88] on page 612×792 pt · **Render:** 833×546 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agentic AI (0.70) · Agent Protocol Fabric (0.57) · Business Automation (0.40) · Security (0.38)
- **Primary branch:** agentic-ai · **Confidence:** 0.70 → review queue
- **Integrity:** sha `51d72038ed0c4c75` · dup group `dup_0303` (1)
- **Caption:** A2A-supporting Remote Agents must publish a "JSON Agent Card" detailing
- **Paragraph before:** represented by their AgentCard (more about it shortly). Using this, AI agents connecting to an MCP server can discover new agents to collaborate with and connect via the A2A protocol.
- **Paragraph after:** A2A-supporting Remote Agents must publish a "JSON Agent Card" detailing their capabilities and authentication. Clients use this to find and communicate with the best agent for a task. There are several things that make A2A powerful:
- **OCR:** Agent Card Name: Technical Writer Description: Writes comprehensive blogs on technical topics Skills: Breaks down complex topics into accessible writing Url: www.dailydoseofds.com/well-known/agent.json

### fig_0323 — ●

- **Page:** 247 (PDF page 249) · **Chapter:** AI Agents
- **BBox:** [129.00, 67.50, 483.00, 354.75] on page 612×792 pt · **Render:** 983×798 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.71) · Agentic AI (0.57) · Tool / Action Fabric (0.42)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.71 → review queue
- **Integrity:** sha `1e27c036fa261879` · dup group `dup_0304` (1)
- **Caption:** ●
- **Paragraph after:** ● Secure collaboration ● Task and state management ●
- **OCR:** IMCP vs. A2A protocol [ vailyDoseorvs.com MCP Host Cloude Dekstop Sl D€ A o Task and state management W UX negotiation v MCP Host AT Tools

### fig_0324 — Let’s understand why this is important.

- **Page:** 248 (PDF page 250) · **Chapter:** AI Agents
- **BBox:** [140.25, 156.88, 471.75, 360.88] on page 612×792 pt · **Render:** 921×567 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agentic AI (0.75) · Agent Protocol Fabric (0.46) · Agent Orchestration (0.42) · Tool / Action Fabric (0.42)
- **Primary branch:** agentic-ai · **Confidence:** 0.75 → review queue
- **Integrity:** sha `8d3068ef41186806` · dup group `dup_0305` (2)
- **Caption:** Let’s understand why this is important.
- **Paragraph before:** ● Agent2Agent protocol standardized Agent-to-Agent communication. But there’s one piece still missing… And that’s a protocol for Agent-to-User communication:
- **Paragraph after:** Let’s understand why this is important. The problem Today, you can build powerful multi-step agentic workflows using a toolkit like LangGraph, CrewAI, Mastra, etc.
- **OCR:** LLM Agent ___, S oG e LLM Agent Nothing o exists here fa I I \| : 0 Tools I MCP R 2

### fig_0325 — But the moment you try to bring that Agent into a real-world app, things fall

- **Page:** 248 (PDF page 250) · **Chapter:** AI Agents
- **BBox:** [121.88, 475.53, 490.12, 611.28] on page 612×792 pt · **Render:** 1023×377 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agentic AI (0.68) · Agent Orchestration (0.49) · AI / ML Foundation (0.44) · Tool / Action Fabric (0.44)
- **Primary branch:** agentic-ai · **Confidence:** 0.68 → review queue
- **Integrity:** sha `660c2a6f753b0e93` · dup group `dup_0306` (1)
- **Caption:** But the moment you try to bring that Agent into a real-world app, things fall
- **Paragraph before:** Let’s understand why this is important. The problem Today, you can build powerful multi-step agentic workflows using a toolkit like LangGraph, CrewAI, Mastra, etc.
- **Paragraph after:** But the moment you try to bring that Agent into a real-world app, things fall apart: ● You want to stream LLM responses token by token, without building a
- **OCR:** Agent development toolkits @reval LangGraph Agno = O AG2 (<>

### fig_0326 — Think of it this way:

- **Page:** 250 (PDF page 252) · **Chapter:** AI Agents
- **BBox:** [132.00, 67.50, 480.00, 504.75] on page 612×792 pt · **Render:** 967×1215 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Agentic AI (0.72) · Agent Protocol Fabric (0.54) · Agent Orchestration (0.40) · Data Engineering (0.40)
- **Primary branch:** agentic-ai · **Confidence:** 0.72 → review queue
- **Integrity:** sha `dc0a6ebff29f1a82` · dup group `dup_0307` (1)
- **Caption:** Think of it this way:
- **Paragraph after:** Think of it this way: ● Just like REST is the standard for client-to-server requests… ● AG-UI is the standard for streaming real-time agent updates back to the
- **OCR:** ﬁAgent User Interaction Protocol &, Your application ) @ App interaction Application @) s . User @ Agent call : ! Return ——————————— ! standardized ——————— /' response N Agent User ’@Eﬁﬁ Interaction Protocol e CopilotKit ¥ 1 @ Communicate with ! - = any Agent backend \| ! @) Receive response b 4 Czec ) LangGraph b= R -\gno AGZ c@ Eg%

### fig_0327 — In the above image, the response from the Agent is not specific to any toolkit. It

- **Page:** 251 (PDF page 253) · **Chapter:** AI Agents
- **BBox:** [126.00, 206.22, 486.00, 389.97] on page 612×792 pt · **Render:** 1000×511 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agentic AI (0.76) · Tool / Action Fabric (0.47) · AI / ML Foundation (0.41) · Multi-Agent (0.41)
- **Primary branch:** agentic-ai · **Confidence:** 0.76 → review queue
- **Integrity:** sha `2a000b86f60d347f` · dup group `dup_0308` (1)
- **Caption:** In the above image, the response from the Agent is not specific to any toolkit. It
- **Paragraph before:** ● AGENT_HANDOFF to smoothly pass control between agents And it comes with SDKs in TypeScript and Python to make this plug-and-play for any stack, like shown below:
- **Paragraph after:** In the above image, the response from the Agent is not specific to any toolkit. It is a standardized AG-UI response. This means you need to write your backend logic once and hook it into AG-UI, and everything just works:
- **OCR:** agui_response["TEXT_MESSAGE_C sponse["T00 My app interface Stream tokens here in the UL Shared state goes here agui_response["STATE_DEL

### fig_0328 — AG-UI (Agent-User Interaction):

- **Page:** 252 (PDF page 254) · **Chapter:** AI Agents
- **BBox:** [141.75, 176.66, 470.25, 377.66] on page 612×792 pt · **Render:** 913×559 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.6
- **Mapping:** Agentic AI (0.82) · RAG / Knowledge Engineering (0.41) · Agent Protocol Fabric (0.41) · Tool / Action Fabric (0.41)
- **Primary branch:** agentic-ai · **Confidence:** 0.82 → review queue
- **Integrity:** sha `21c09f3e1c931a3c` · dup group `dup_0305` (2)
- **Caption:** AG-UI (Agent-User Interaction):
- **Paragraph before:** Earlier the agent ecosystem was fragmented into dozens of incompatible frameworks. But finally, the industry is converging around three protocols that work together. These are:
- **Paragraph after:** AG-UI (Agent-User Interaction): ● The bi-directional connection between agentic backends and frontends. ●
- **OCR:** LW Agent \| ! o’ Tools

### fig_0329 — Your frontend stays connected to the entire agent ecosystem through one unified

- **Page:** 253 (PDF page 255) · **Chapter:** AI Agents
- **BBox:** [132.38, 67.50, 479.62, 414.75] on page 612×792 pt · **Render:** 965×965 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.78) · Agent Protocol Fabric (0.57)
- **Primary branch:** agentic-ai · **Confidence:** 0.78 → review queue
- **Integrity:** sha `74c474c9ced063c2` · dup group `dup_0309` (1)
- **Caption:** Your frontend stays connected to the entire agent ecosystem through one unified
- **Paragraph after:** Your frontend stays connected to the entire agent ecosystem through one unified protocol layer. CopilotKit sits above all three as the Agentic Application Framework. It acts as the practical layer that lets you actually build with these protocols
- **OCR:** Agent Protocol Landscape Agentic Backend %3 DailyDoseofDS.com “You are al tely right! AG-Ul and M JI work gre...” Your Application b and collaboration? Your are absolutely true! AG-Ul and MCP-Ul work great together.

### fig_0330 — It breaks down handshakes, misconceptions and real examples and shows exactly

- **Page:** 254 (PDF page 256) · **Chapter:** AI Agents
- **BBox:** [160.50, 67.50, 451.50, 331.50] on page 612×792 pt · **Render:** 809×733 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agentic AI (0.74) · Agent Protocol Fabric (0.54) · LLM Engineering (0.41)
- **Primary branch:** agentic-ai · **Confidence:** 0.74 → review queue
- **Integrity:** sha `84f7fc48be4f1ddd` · dup group `dup_0310` (1)
- **Caption:** It breaks down handshakes, misconceptions and real examples and shows exactly
- **Paragraph after:** It breaks down handshakes, misconceptions and real examples and shows exactly how to start building. Agent optimization with Opik Developers manually iterate through prompts to find an optimal one. This is not
- **OCR:** The Agentic Protocol Landscape Understanding AG-UI, MCP, A2A, Ul Specs, and how to build agentic applications ¥ 0 =

### fig_0331 — Agent optimization with Opik

- **Page:** 254 (PDF page 256) · **Chapter:** AI Agents
- **BBox:** [121.12, 589.47, 490.88, 718.47] on page 612×792 pt · **Render:** 1027×358 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agentic AI (0.58) · LLM Engineering (0.54) · Evaluation (0.50) · Tool / Action Fabric (0.43)
- **Primary branch:** agentic-ai · **Confidence:** 0.58 → review queue
- **Integrity:** sha `9b13618ee87792cb` · dup group `dup_0311` (1)
- **Heading:** Agent optimization with Opik
- **Paragraph before:** Let’s learn how to use the Opik Agent Optimizer toolkit that lets you automatically optimize prompts for LLM apps. The idea is to start with an initial prompt and an evaluation dataset, and let an LLM iteratively improve the prompt based on evaluations.
- **OCR:** Agent Optimization Toolkit Eval A Y Optimization dataset L) : . report ! 1 \| Evaluation §© »___Ix____) R Criteria : 1 1 A O Opik i Improved prompt Initial & prompt i

### fig_0332 — Next, import all the required classes and functions from opik and

- **Page:** 255 (PDF page 257) · **Chapter:** AI Agents
- **BBox:** [155.25, 97.28, 456.75, 247.28] on page 612×792 pt · **Render:** 837×416 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agentic AI (0.57) · Agent Protocol Fabric (0.49) · Tool / Action Fabric (0.49) · Evaluation (0.49)
- **Primary branch:** agentic-ai · **Confidence:** 0.57 → review queue
- **Integrity:** sha `7447a8a5e8edabfb` · dup group `dup_0312` (1)
- **Caption:** Next, import all the required classes and functions from opik and
- **Paragraph before:** To begin, install Opik and its optimizer package, and configure Opik:
- **Paragraph after:** Next, import all the required classes and functions from opik and opik_optimizer: ● LevenshteinRatio → Our metric to evaluate the prompt’s effectiveness in
- **OCR:** Install using uv Install using pip LX) Command line [ X} Command line uv add opik-optimizer pip install opik opik-optimizer e Command line opik configure

### fig_0333 — ●

- **Page:** 255 (PDF page 257) · **Chapter:** AI Agents
- **BBox:** [127.12, 302.38, 484.88, 420.88] on page 612×792 pt · **Render:** 993×330 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Evaluation (0.62) · LLM Engineering (0.51) · Agentic AI (0.51) · Agent Protocol Fabric (0.40)
- **Primary branch:** evaluation · **Confidence:** 0.62 → review queue
- **Integrity:** sha `9ef789764bfecdfd` · dup group `dup_0313` (1)
- **Caption:** ●
- **Paragraph before:** To begin, install Opik and its optimizer package, and configure Opik: Next, import all the required classes and functions from opik and opik_optimizer:
- **Paragraph after:** ● LevenshteinRatio → Our metric to evaluate the prompt’s effectiveness in generating a precise output for the given input. ●
- **OCR:** [ X notebook.ipynb G Opik from opik.evaluation.metrics import LevenshteinRatio from opik_optimizer import MetaPromptOptimizer, ChatPrompt from opik_optimizer.datasets import tiny_test

### fig_0334 — Moving on, configure the evaluation metric, which tells the optimizer how to

- **Page:** 256 (PDF page 258) · **Chapter:** AI Agents
- **BBox:** [160.12, 67.50, 451.88, 267.00] on page 612×792 pt · **Render:** 811×554 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Evaluation (0.68) · Agentic AI (0.51) · LLM Engineering (0.46) · Agent Protocol Fabric (0.40)
- **Primary branch:** evaluation · **Confidence:** 0.68 → review queue
- **Integrity:** sha `6adaa6183f12280f` · dup group `dup_0314` (1)
- **Caption:** Moving on, configure the evaluation metric, which tells the optimizer how to
- **Paragraph after:** Moving on, configure the evaluation metric, which tells the optimizer how to score the LLM’s outputs against the given label: Next, define your base prompt, which is the initial instruction that the MetaPromptOptimizer will try to enhance:
- **OCR:** notebook.ipynb dataset = tiny_test() dataset.to_pandas() © \' text Who painted the Mona Lisa? What is the largest planet in our solar system? What is 2 + 2? Who wrote Romeo and Juliet? What is the capital of France? label Leonardo da Vinci Jupiter 4 William Shakespeare Paris

### fig_0335 — Next, define your base prompt, which is the initial instruction that the

- **Page:** 256 (PDF page 258) · **Chapter:** AI Agents
- **BBox:** [135.75, 322.09, 476.25, 474.34] on page 612×792 pt · **Render:** 945×423 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Evaluation (0.68) · LLM Engineering (0.51) · Agentic AI (0.51)
- **Primary branch:** evaluation · **Confidence:** 0.68 → review queue
- **Integrity:** sha `a1cec9dcd5fff18d` · dup group `dup_0315` (1)
- **Caption:** Next, define your base prompt, which is the initial instruction that the
- **Paragraph before:** Moving on, configure the evaluation metric, which tells the optimizer how to score the LLM’s outputs against the given label:
- **Paragraph after:** Next, define your base prompt, which is the initial instruction that the MetaPromptOptimizer will try to enhance:
- **OCR:** [ X X ] notebook.ipynb def levenshtein_ratio(data_input, output): metric = LevenshteinRatio() return metric.score(reference=data_input['label'l, output=output)

### fig_0336 — AI Agents figure

- **Page:** 256 (PDF page 258) · **Chapter:** AI Agents
- **BBox:** [140.25, 529.44, 471.75, 701.19] on page 612×792 pt · **Render:** 921×477 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.62) · Evaluation (0.51) · Agentic AI (0.51) · Context Engineering (0.40)
- **Primary branch:** llm-engineering · **Confidence:** 0.62 → review queue
- **Integrity:** sha `a7b514bce0e81fb2` · dup group `dup_0316` (1)
- **Paragraph before:** Moving on, configure the evaluation metric, which tells the optimizer how to score the LLM’s outputs against the given label: Next, define your base prompt, which is the initial instruction that the MetaPromptOptimizer will try to enhance:
- **OCR:** [ X X ] notebook.ipynb prompt = ChatPrompt( project_name="Prompt Optimization Quickstart", messages=[ {"role": "system", "content": """You are an expert assistant Your task is to answer questions accurately and concisely Consider the context carefully before responding."""}, {"role": "user", "content": "{text}"}

### fig_0337 — Finally, the optimizer.optimize_prompt(...) method is invoked with the dataset,

- **Page:** 257 (PDF page 259) · **Chapter:** AI Agents
- **BBox:** [141.00, 117.06, 471.00, 235.56] on page 612×792 pt · **Render:** 917×329 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.70) · Evaluation (0.50) · Agentic AI (0.50)
- **Primary branch:** llm-engineering · **Confidence:** 0.70 → review queue
- **Integrity:** sha `6830258ecac5a8d6` · dup group `dup_0317` (1)
- **Caption:** Finally, the optimizer.optimize_prompt(...) method is invoked with the dataset,
- **Paragraph before:** Next, instantiate a MetaPromptOptimizer, specifying the model to use in the optimization process:
- **Paragraph after:** Finally, the optimizer.optimize_prompt(...) method is invoked with the dataset, metric configuration, and prompt to start the optimization process: It starts by evaluating the initial prompt, which sets the baseline: Then it iterates through several different prompts (written by AI), evaluates them,
- **OCR:** 000 notebook.ipynb optimizer = MetaPromptOptimizer( model="gpt-4",

### fig_0338 — It starts by evaluating the initial prompt, which sets the baseline:

- **Page:** 257 (PDF page 259) · **Chapter:** AI Agents
- **BBox:** [136.88, 290.67, 475.12, 441.42] on page 612×792 pt · **Render:** 939×419 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.69) · Evaluation (0.54) · Agentic AI (0.46)
- **Primary branch:** llm-engineering · **Confidence:** 0.69 → review queue
- **Integrity:** sha `a3e649594b6765d9` · dup group `dup_0318` (1)
- **Caption:** It starts by evaluating the initial prompt, which sets the baseline:
- **Paragraph before:** Next, instantiate a MetaPromptOptimizer, specifying the model to use in the optimization process: Finally, the optimizer.optimize_prompt(...) method is invoked with the dataset, metric configuration, and prompt to start the optimization process:
- **Paragraph after:** It starts by evaluating the initial prompt, which sets the baseline: Then it iterates through several different prompts (written by AI), evaluates them,
- **OCR:** N N J notebook.ipynb result = optimizer.optimize_prompt ( prompt=prompt, dataset=dataset, metric=levenshtein_ratio,

### fig_0339 — Then it iterates through several different prompts (written by AI), evaluates them,

- **Page:** 257 (PDF page 259) · **Chapter:** AI Agents
- **BBox:** [137.62, 476.72, 474.38, 675.47] on page 612×792 pt · **Render:** 935×552 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.59) · Evaluation (0.59) · Agentic AI (0.47) · Context Engineering (0.39)
- **Primary branch:** llm-engineering · **Confidence:** 0.59 → review queue
- **Integrity:** sha `3dcc4f7536e9c261` · dup group `dup_0319` (1)
- **Caption:** Then it iterates through several different prompts (written by AI), evaluates them,
- **Paragraph before:** optimization process: Finally, the optimizer.optimize_prompt(...) method is invoked with the dataset, metric configuration, and prompt to start the optimization process: It starts by evaluating the initial prompt, which sets the baseline:
- **Paragraph after:** Then it iterates through several different prompts (written by AI), evaluates them,
- **OCR:** You are an expert assistant. Your task is to answer questions accurately and concisely. Consider the context carefully before Initial > First we will establish the baseline performance: eva' Evaluation 100% 0:00:03 Baseline score was: 0.3513. Using MetaPromptOptinizer with the parameters: - n_samples: None - auto_continue: False

### fig_0340 — The optimization results are also available in the Opik dashboard for further

- **Page:** 258 (PDF page 260) · **Chapter:** AI Agents
- **BBox:** [144.00, 117.06, 468.00, 306.06] on page 612×792 pt · **Render:** 900×525 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Evaluation (0.59) · LLM Engineering (0.51) · Agentic AI (0.51) · Observability (0.43)
- **Primary branch:** evaluation · **Confidence:** 0.59 → review queue
- **Integrity:** sha `1b702119f3545849` · dup group `dup_0320` (1)
- **Caption:** The optimization results are also available in the Opik dashboard for further
- **Paragraph before:** and prints the most optimal prompt. You can invoke result.display() to see a summary of the optimization, the best prompt found and its score:
- **Paragraph after:** The optimization results are also available in the Opik dashboard for further analysis and visualization: And that’s how you can use Opik Agent Optimizer to enhance the performance and efficiency of your LLM apps.
- **OCR:** e Optinization Complete o . o Optimizer: MetaPromptoptinizer o t t o e ptimization Metric Evaluated: Levenshtein_ratio Initial Score 0.3513 Final Best Score: 1.0000 o D e summary Rounds Conpleted: 3 Optinization run Link: 18;i0=922010;https: //w. conet. con/opik/api/v1/session/s Final Optimized Prompt System: As an Al assistant, your task is to answer the user's question based on the context provided in the metadata. Your responses should be accurate, concise, and directly related to the question. Your performance will be evaluated using the Levenshtein ratio, which measures the similarity between your response and the correct answer. Therefore, aim to produce responses that closely match the correct answer. Avoid adding any extra information or words that are not part of the correct answer.

### fig_0341 — And that’s how you can use Opik Agent Optimizer to enhance the performance

- **Page:** 258 (PDF page 260) · **Chapter:** AI Agents
- **BBox:** [114.75, 361.17, 497.25, 610.17] on page 612×792 pt · **Render:** 1063×691 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.65) · Context Engineering (0.53) · Agentic AI (0.50) · Agent Protocol Fabric (0.38)
- **Primary branch:** llm-engineering · **Confidence:** 0.65 → review queue
- **Integrity:** sha `a3fced3df1f4dfb2` · dup group `dup_0321` (1)
- **Caption:** And that’s how you can use Opik Agent Optimizer to enhance the performance
- **Paragraph before:** and prints the most optimal prompt. You can invoke result.display() to see a summary of the optimization, the best prompt found and its score: The optimization results are also available in the Opik dashboard for further analysis and visualization:
- **Paragraph after:** And that’s how you can use Opik Agent Optimizer to enhance the performance and efficiency of your LLM apps. Note: While we used GPT-4o, everything here can be executed 100% locally since you can use any other LLM + Opik is fully open-source.
- **OCR:** oees Qptimization report o s [ role” “system,"content® A PRI magaIcHsOeITIO o GumASSAS ehcionsgprenie S soveunaL ebsse 775 e sucecass supopusys L e e e—— e optimizer Prompt o lovenshtein.... ¢ MetapromptOptinizer [{ ol systom", "content’: "As an Al assistant, yourtask I to answer the user's queston based onthe context prov. 1 msn MetapromptOptimizer [{role™ “system’,"content’: "You are an Al assstant. Your task I o answer questions based on the context provided .. a2 MetapromptOptinizer [ role" system","content’: As an Al your task s to answer the user's question using the context provided i the me.. ~120% MataPromptOptinizer [{"role™ systemy, "content: You are an Al assstant tasked with answering questons based on the context provided. MetaPromptOptimizer [{rol’ "As a1 A, your task s to answer the user's queston using the context provided i the ... MetapromprOptinizer [{rolr = “As an Al

### fig_0342 — AI Agent Deployment Strategies

- **Page:** 259 (PDF page 261) · **Chapter:** AI Agents
- **BBox:** [130.88, 193.03, 481.12, 613.03] on page 612×792 pt · **Render:** 973×1166 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agentic AI (0.61) · Infrastructure (0.58) · RAG / Knowledge Engineering (0.45) · Context Engineering (0.41)
- **Primary branch:** agentic-ai · **Confidence:** 0.61 → review queue
- **Integrity:** sha `f8215944ffc6fb7f` · dup group `dup_0322` (1)
- **Heading:** AI Agent Deployment Strategies
- **Caption:** 1) Batch deployment
- **Paragraph before:** AI Agent Deployment Strategies Deploying AI agents isn’t one-size-fits-all. The architecture you choose can make or break your agent’s performance, cost efficiency, and user experience. Here are the main deployment patterns you need to know:
- **Paragraph after:** 1) Batch deployment You can think of this as a scheduled automation.
- **OCR:** l RN Deployment Types \| merveisposeoros.com Inference [eenwnd Backend [eos s ] [aes =] 3 External 3 Inference Store External Context Load ? Balancer External o Context User Device Mobile Smartwatch Laptop ﬁm Latency Storage E 8atch Storage =5 streaming Storage i:u Agent

### fig_0343 — ● The Agent runs periodically, like a scheduled CLI job.

- **Page:** 260 (PDF page 262) · **Chapter:** AI Agents
- **BBox:** [120.00, 67.50, 492.00, 175.50] on page 612×792 pt · **Render:** 1033×300 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Agentic AI (0.65) · Data Engineering (0.50) · Context Engineering (0.45) · Agent Protocol Fabric (0.45)
- **Primary branch:** agentic-ai · **Confidence:** 0.65 → review queue
- **Integrity:** sha `5a12713703246745` · dup group `dup_0323` (1)
- **Caption:** ● The Agent runs periodically, like a scheduled CLI job.
- **Paragraph after:** ● The Agent runs periodically, like a scheduled CLI job. ● Just like any other Agent, it can connect to external context (databases, APIs, or tools), process data in bulk, and store results. ●
- **OCR:** Inference Store ‘@ Backend ? —. Server =) =] =] =) External Context . Backend Service

### fig_0344 — 2) Stream deployment

- **Page:** 260 (PDF page 262) · **Chapter:** AI Agents
- **BBox:** [120.00, 369.61, 492.00, 477.61] on page 612×792 pt · **Render:** 1033×300 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Data Engineering (0.66) · Agentic AI (0.54) · Agent Protocol Fabric (0.43) · Infrastructure (0.43)
- **Primary branch:** data-engineering · **Confidence:** 0.66 → review queue
- **Integrity:** sha `78355fb7783b05a6` · dup group `dup_0324` (1)
- **Heading:** 2) Stream deployment
- **Caption:** ● It continuously processes data as it flows through systems.
- **Paragraph before:** ● This is best for processing large volumes of data that don’t need immediate responses. 2) Stream deployment Here, the Agent becomes part of a streaming data pipeline.
- **Paragraph after:** ● It continuously processes data as it flows through systems. ● Your agent stays active, handling concurrent streams while accessing both streaming storage and backend services as needed.
- **OCR:** Backend Inference Service Store Stream % @ Backend Service AN

### fig_0345 — ●

- **Page:** 261 (PDF page 263) · **Chapter:** AI Agents
- **BBox:** [114.75, 67.50, 497.25, 179.25] on page 612×792 pt · **Render:** 1063×310 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agentic AI (0.68) · Context Engineering (0.51) · RAG / Knowledge Engineering (0.43) · Agent Protocol Fabric (0.43)
- **Primary branch:** agentic-ai · **Confidence:** 0.68 → review queue
- **Integrity:** sha `166b0806a14edcae` · dup group `dup_0325` (1)
- **Caption:** ●
- **Paragraph after:** ● The Agent runs behind an API (REST or gRPC). ● When a request arrives, it retrieves any needed context, reasons using the
- **OCR:** Backend —. Service Real ? Time External Context Backend » Service

### fig_0346 — 4) Edge deployment

- **Page:** 261 (PDF page 263) · **Chapter:** AI Agents
- **BBox:** [117.00, 393.16, 495.00, 503.41] on page 612×792 pt · **Render:** 1050×306 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.6
- **Mapping:** Agentic AI (0.64) · Infrastructure (0.57) · Agent Protocol Fabric (0.42) · Security (0.42)
- **Primary branch:** agentic-ai · **Confidence:** 0.64 → review queue
- **Integrity:** sha `db62bb20d48eee07` · dup group `dup_0326` (1)
- **Heading:** 4) Edge deployment
- **Caption:** ●
- **Paragraph before:** where users expect sub-second responses. 4) Edge deployment The agent runs directly on user devices: mobile phones, smartwatches, and laptops so no server round-trip is needed.
- **Paragraph after:** ● The reasoning logic lives inside your mobile, smartwatch, or laptop. ● Sensitive data never leaves the device, improving privacy and security.
- **OCR:** Mobile User Device Smartwatch Laptop

### fig_0347 — What is MCP?

- **Page:** 264 (PDF page 266) · **Chapter:** MCP
- **BBox:** [171.00, 139.47, 441.00, 326.97] on page 612×792 pt · **Render:** 750×521 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.98)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `642127bf3a89ded6` · dup group `dup_0327` (1)
- **Heading:** What is MCP?
- **Caption:** ● French, you must learn French.
- **Paragraph before:** What is MCP? Imagine you only know English. To get info from a person who only knows:
- **Paragraph after:** ● French, you must learn French. ● German, you must learn German. ●
- **OCR:** English speaker You French speaker Russian speaker

### fig_0348 — What is MCP?

- **Page:** 264 (PDF page 266) · **Chapter:** MCP
- **BBox:** [138.75, 470.97, 473.25, 670.47] on page 612×792 pt · **Render:** 929×554 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.98)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `3148dff80694d60d` · dup group `dup_0328` (1)
- **Heading:** What is MCP?
- **Paragraph before:** ● And so on. In this setup, learning even languages will be a nightmare for you. But what if you add a translator that understands all languages?
- **OCR:** e German speaker Chinese speaker Translator French speaker Russian speaker

### fig_0349 — If they need to access real-time information, they must use external tools and

- **Page:** 265 (PDF page 267) · **Chapter:** MCP
- **BBox:** [66.00, 214.32, 457.88, 510.81] on page 612×792 pt · **Render:** 1088×823 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.74) · Tool / Action Fabric (0.52) · Context Engineering (0.39) · Agentic AI (0.39)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.74 → review queue
- **Integrity:** sha `59ab2a06b28e3110` · dup group `dup_0329` (1)
- **Caption:** If they need to access real-time information, they must use external tools and
- **Paragraph before:** It lets you (Agents) talk to other people (tools or other capabilities) through a single interface. To formalize, while LLMs possess impressive knowledge and reasoning skills, which allow them to perform many complex tasks, their knowledge is limited to
- **Paragraph after:** If they need to access real-time information, they must use external tools and resources on their own. Model context protocol (MCP) is a standardized interface and framework that allows AI models to seamlessly interact with external tools, resources, and
- **OCR:** their initial training data. What is MCP ? Database Web APIs Local Filesystem

### fig_0350 — Why was MCP created?

- **Page:** 266 (PDF page 268) · **Chapter:** MCP
- **BBox:** [91.12, 292.62, 520.88, 546.12] on page 612×792 pt · **Render:** 1193×705 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.77) · Tool / Action Fabric (0.50) · Infrastructure (0.39) · Business Automation (0.39)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.77 → review queue
- **Integrity:** sha `68582f01cd383fc4` · dup group `dup_0330` (1)
- **Heading:** Why was MCP created?
- **Caption:** Let’s understand this in detail.
- **Paragraph before:** was no common standard. This doesn’t scale. Developers of AI apps were essentially reinventing the wheel each time, and tool providers had to support multiple incompatible APIs to reach different AI platforms.
- **Paragraph after:** Let’s understand this in detail. The problem Before MCP, the landscape of connecting AI to external data and actions looked like a patchwork of one-off solutions.
- **OCR:** Mce User MCP Host (ea. Claude) wm response *MCP Host does not have two LLMs. It is just shown to simplify the visvalisati & deepseelc A @ ® Select \| Return MCP tool \| MCP tool deepseelk BB . a E E Tools

### fig_0351 — The solution

- **Page:** 267 (PDF page 269) · **Chapter:** MCP
- **BBox:** [118.12, 246.00, 493.88, 443.25] on page 612×792 pt · **Render:** 1043×548 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.6
- **Mapping:** Agent Protocol Fabric (0.84) · Data Engineering (0.43) · Tool / Action Fabric (0.43)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.84 → review queue
- **Integrity:** sha `2bfc0dd29ad39fc8` · dup group `dup_0331` (1)
- **Caption:** The solution
- **Paragraph before:** sources, you could end up needing M × N custom integrations. The diagram below illustrates this complexity: each AI (each “Model”) might require unique code to connect to each external service (database, filesystem, calculator, etc.), leading to spaghetti-like interconnections.
- **Paragraph after:** The solution MCP tackles this by introducing a standard interface in the middle. Instead of M × N direct integrations, we get M + N implementations: each of the M AI applications implements the MCP client side once, and each of the N tools
- **OCR:** v P g

### fig_0352 — ●

- **Page:** 268 (PDF page 270) · **Chapter:** MCP
- **BBox:** [66.00, 66.00, 546.00, 283.00] on page 612×792 pt · **Render:** 1333×603 px
- **Composition:** hybrid · **Role:** diagram · **Quality:** 1
- **Mapping:** Agent Protocol Fabric (0.86) · Tool / Action Fabric (0.49)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.86 → auto-accept
- **Integrity:** sha `330dca443b88a146` · dup group `dup_0332` (1)
- **Caption:** ●
- **Paragraph after:** ● On the left (pre-MCP), every model had to wire into every tool. ● On the right (with MCP), each model and tool connects to the MCP layer,
- **OCR:** traditional approach mxn = 9 connections MCP approach m+n = 6 connections

### fig_0353 — Host

- **Page:** 269 (PDF page 271) · **Chapter:** MCP
- **BBox:** [117.75, 67.50, 494.25, 285.75] on page 612×792 pt · **Render:** 1045×606 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.95) · Data Engineering (0.40)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.95 → auto-accept
- **Integrity:** sha `65b9b4b43f07ab72` · dup group `dup_0333` (1)
- **Caption:** Host
- **Paragraph after:** Host The Host is the user-facing AI application, the environment where the AI model lives and interacts with the user. This could be a chat application (like OpenAI’s ChatGPT interface or Anthropic’s
- **OCR:** IDE (Cursor) Other AT Apps ' \| 1 1 \ \J MCP Client 2 MCP Client 3 MCP ch/P MCP [MCP Sarvge z] (MCP Swver 3] Local Filesystem Database Web APIs

### fig_0354 — Client

- **Page:** 270 (PDF page 272) · **Chapter:** MCP
- **BBox:** [129.38, 67.50, 482.62, 308.25] on page 612×792 pt · **Render:** 981×669 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.6
- **Mapping:** Agent Protocol Fabric (0.95) · Infrastructure (0.40)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.95 → auto-accept
- **Integrity:** sha `530dc641a18aa436` · dup group `dup_0334` (1)
- **Caption:** Client
- **Paragraph after:** Client The MCP Client is a component within the Host that handles the low-level communication with an MCP Server. Think of the Client as the adapter or messenger. While the Host decides what to
- **OCR:** % Good afternoon, Avi

### fig_0355 — Client

- **Page:** 270 (PDF page 272) · **Chapter:** MCP
- **BBox:** [100.50, 478.81, 511.50, 684.31] on page 612×792 pt · **Render:** 1141×570 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.90) · Infrastructure (0.45)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.90 → auto-accept
- **Integrity:** sha `1576e5330b83b964` · dup group `dup_0335` (1)
- **Heading:** Client
- **Paragraph before:** communication with an MCP Server. Think of the Client as the adapter or messenger. While the Host decides what to do, the Client knows how to speak MCP to actually carry out those instructions with the server.
- **OCR:** MCP Host MCP Client MCP Client MCP Server Transport Layer MCP Server ®::: Transport Layer Local Filesystem/DB Web APIs <~ ---> Internet

### fig_0356 — Server

- **Page:** 271 (PDF page 273) · **Chapter:** MCP
- **BBox:** [154.88, 371.25, 457.12, 647.25] on page 612×792 pt · **Render:** 839×766 px
- **Composition:** raster · **Role:** result · **Quality:** 0.6
- **Mapping:** Agent Protocol Fabric (0.77) · Tool / Action Fabric (0.44) · Infrastructure (0.44) · LLM Engineering (0.40)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.77 → review queue
- **Integrity:** sha `272585c0dce124ea` · dup group `dup_0336` (1)
- **Heading:** Server
- **Paragraph before:** cloud service since MCP is designed to support both scenarios seamlessly. The key is that the Server advertises what it can do in a standard format (so the client can query and understand available tools) and will execute requests coming from the client, then return results.
- **OCR:** To Client < Tools Resources Prompts

### fig_0357 — Tools

- **Page:** 272 (PDF page 274) · **Chapter:** MCP
- **BBox:** [111.00, 520.16, 501.00, 707.66] on page 612×792 pt · **Render:** 1083×521 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Tool / Action Fabric (0.65) · Agent Protocol Fabric (0.60) · LLM Engineering (0.40) · Infrastructure (0.40)
- **Primary branch:** tool-action-fabric · **Confidence:** 0.65 → review queue
- **Integrity:** sha `7ed4ba79ccfe118c` · dup group `dup_0337` (1)
- **Heading:** Tools
- **Paragraph before:** the LLM (via the host) decides to call a tool when it determines it needs that functionality. Suppose we have a simple tool for weather. In an MCP server’s code, it might look like:
- **OCR:** [ X X J @ tool_example.py amecp . tool() def get_weather(location: str) — dict: """Get the current weather for a specified location.""" return { "temperature": 72, "conditions": "Sunny", "humidity": 45

### fig_0358 — For example, Claude’s client might pop up “The AI wants to use the ‘get_weather’

- **Page:** 273 (PDF page 275) · **Chapter:** MCP
- **BBox:** [144.38, 305.38, 467.62, 565.62] on page 612×792 pt · **Render:** 897×723 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.63) · Tool / Action Fabric (0.63) · LLM Engineering (0.41) · RAG / Knowledge Engineering (0.38)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.63 → review queue
- **Integrity:** sha `8dbfa9dda4c1a1e5` · dup group `dup_0338` (1)
- **Caption:** For example, Claude’s client might pop up “The AI wants to use the ‘get_weather’
- **Paragraph before:** tool returns structured data (temperature, conditions), and the AI can then use or verbalize (generate a response) that info. Since tools can do things like file I/O or network calls, an MCP implementation often requires that the user permit a tool call.
- **Paragraph after:** For example, Claude’s client might pop up “The AI wants to use the ‘get_weather’ tool, allow yes/no?” the first time, to avoid abuse. This ensures the human stays in control of powerful actions. Tools are analogous to “functions” in classic function calling, but under MCP,
- **OCR:** New chat Let's discuss the QuboAl app further. What did \| tell you about it? Use MCP tool Waiting for approval... v Calling MCP tool search_facts { "query": "QuboAI app" } Approval

### fig_0359 — Resources

- **Page:** 274 (PDF page 276) · **Chapter:** MCP
- **BBox:** [96.00, 533.75, 516.00, 700.25] on page 612×792 pt · **Render:** 1167×463 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.76) · Context Engineering (0.43) · RAG / Knowledge Engineering (0.43) · Data Engineering (0.43)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.76 → review queue
- **Integrity:** sha `e40a39d8a9517dbf` · dup group `dup_0339` (1)
- **Heading:** Resources
- **Paragraph before:** Essentially anything the AI might need to know as context. An AI research assistant could have resources like “ArXiv papers database,” where it can retrieve an abstract or reference when asked. A simple resource could be a function to read a file:
- **OCR:** ®®® @ resource_example.py amcp.resource("file: // {path}") def read_file(path: str) — str: """Read the contents of a file at the given path.""" with open(path, 'r') as f: return f.read()

### fig_0360 — This prompt function returns a list of message objects (in OpenAI format) that

- **Page:** 276 (PDF page 278) · **Chapter:** MCP
- **BBox:** [102.00, 474.06, 510.00, 600.81] on page 612×792 pt · **Render:** 1133×352 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.68) · Agent Protocol Fabric (0.57) · Tool / Action Fabric (0.42) · Infrastructure (0.39)
- **Primary branch:** llm-engineering · **Confidence:** 0.68 → review queue
- **Integrity:** sha `91b767aabfc6a738` · dup group `dup_0340` (1)
- **Caption:** This prompt function returns a list of message objects (in OpenAI format) that
- **Paragraph before:** Rather, the prompt sets the stage before the model starts generating. In that sense, prompts are often fetched at the beginning of an interaction or when the user chooses a specific “mode”. Suppose we have a prompt template for code review. The MCP server might have:
- **Paragraph after:** This prompt function returns a list of message objects (in OpenAI format) that set up a code review scenario. When the host invokes this prompt, it gets those messages and can insert the actual code to be reviewed into the user content.
- **OCR:** (X X J @ prompt_example.py amcp .prompt () def code_review(language: str) — Llist: """provide a structured prompt for reviewing code in the given languase. return [ {"role": "system", "content": f"You are a meticulous {language) code reviewer..."}, {"role": "user", “"content": f"Please review the following {language) code:"}

### fig_0361 — ● Later, if you decide to add a third required parameter (e.g., unit for

- **Page:** 278 (PDF page 280) · **Chapter:** MCP
- **BBox:** [109.88, 166.64, 502.12, 261.89] on page 612×792 pt · **Render:** 1089×265 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.93) · LLM Engineering (0.42)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.93 → auto-accept
- **Integrity:** sha `3dfdfa9412eeee14` · dup group `dup_0341` (1)
- **Caption:** ● Later, if you decide to add a third required parameter (e.g., unit for
- **Paragraph before:** In a traditional API setup: ● If your API initially requires two parameters (e.g., location and date for a weather service), users integrate their applications to send requests with those exact parameters.
- **Paragraph after:** ● Later, if you decide to add a third required parameter (e.g., unit for temperature units like Celsius or Fahrenheit), the API’s contract changes. ● This means all users of your API must update their code to include the new parameter. If they don’t update, their requests might fail, return errors, or
- **OCR:** location and date @ loc & date —_— API Endpoint with — 1 @® “ response parameter

### fig_0362 — ● This means all users of your API must update their code to include the new

- **Page:** 278 (PDF page 280) · **Chapter:** MCP
- **BBox:** [114.38, 317.00, 497.62, 411.50] on page 612×792 pt · **Render:** 1065×263 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.86) · LLM Engineering (0.42) · Reliability (0.42)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.86 → auto-accept
- **Integrity:** sha `9ac3edb00e725488` · dup group `dup_0342` (1)
- **Caption:** ● This means all users of your API must update their code to include the new
- **Paragraph before:** weather service), users integrate their applications to send requests with those exact parameters. ● Later, if you decide to add a third required parameter (e.g., unit for temperature units like Celsius or Fahrenheit), the API’s contract changes.
- **Paragraph after:** ● This means all users of your API must update their code to include the new parameter. If they don’t update, their requests might fail, return errors, or provide incomplete results.
- **OCR:** @ loc & date s API Endpoint with —_— ‘ location, date and unit ¢ - failure parameter e —

### fig_0363 — MCP figure

- **Page:** 278 (PDF page 280) · **Chapter:** MCP
- **BBox:** [111.75, 486.34, 500.25, 709.84] on page 612×792 pt · **Render:** 1079×621 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.91) · LLM Engineering (0.44)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.91 → auto-accept
- **Integrity:** sha `32c2b3bd240c6786` · dup group `dup_0343` (1)
- **Paragraph before:** temperature units like Celsius or Fahrenheit), the API’s contract changes. ● This means all users of your API must update their code to include the new parameter. If they don’t update, their requests might fail, return errors, or provide incomplete results.
- **OCR:** Ly & %\ L/ﬁe @ loc & date — L I API Endpoint with location, date and unit parameter ‘e % ¢ o

### fig_0364 — ●

- **Page:** 279 (PDF page 281) · **Chapter:** MCP
- **BBox:** [107.62, 255.80, 504.38, 376.55] on page 612×792 pt · **Render:** 1103×335 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.78) · Infrastructure (0.49) · LLM Engineering (0.39) · Tool / Action Fabric (0.39)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.78 → review queue
- **Integrity:** sha `b9b53fa697e77829` · dup group `dup_0344` (1)
- **Caption:** ●
- **Paragraph before:** The server responds with details about its available tools, resources, prompts, and parameters. For example, if your weather API initially supports location and date, the server communicates these as part of its capabilities.
- **Paragraph after:** ● If you later add a unit parameter, the MCP server can dynamically update its capability description during the next exchange. The client doesn’t need to hardcode or predefine the parameters since it simply queries the server’s
- **OCR:** Client tell me your capabilities _— > invoke me with location and date API Endpoint with location and date parameter

### fig_0365 — ● This way, the client can then adjust its behavior on-the-fly, using the

- **Page:** 279 (PDF page 281) · **Chapter:** MCP
- **BBox:** [89.62, 471.22, 522.38, 602.47] on page 612×792 pt · **Render:** 1203×365 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.86) · Infrastructure (0.49)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.86 → auto-accept
- **Integrity:** sha `08bf9f6ef9afc72c` · dup group `dup_0345` (1)
- **Caption:** ● This way, the client can then adjust its behavior on-the-fly, using the
- **Paragraph before:** If you later add a unit parameter, the MCP server can dynamically update its capability description during the next exchange. The client doesn’t need to hardcode or predefine the parameters since it simply queries the server’s current capabilities and adapts accordingly.
- **Paragraph after:** ● This way, the client can then adjust its behavior on-the-fly, using the updated capabilities (e.g., including unit in its requests) without needing to rewrite or redeploy code. We’ll understand this topic better in Part of this course, when we build a
- **OCR:** Client tell me your capabilities _— invoke me with location, date and unit API Endpoint with location, date and unit parameter

### fig_0366 — MCP versus Function calling

- **Page:** 280 (PDF page 282) · **Chapter:** MCP
- **BBox:** [108.00, 230.81, 504.00, 653.81] on page 612×792 pt · **Render:** 1100×1175 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Tool / Action Fabric (0.62) · Agent Protocol Fabric (0.58) · LLM Engineering (0.48) · RAG / Knowledge Engineering (0.37)
- **Primary branch:** tool-action-fabric · **Confidence:** 0.62 → review queue
- **Integrity:** sha `1d59fd6fb835a614` · dup group `dup_0346` (1)
- **Heading:** MCP versus Function calling
- **Caption:** Function calling enables LLMs to execute predefined functions based on user
- **Paragraph before:** MCP versus Function calling Before MCPs became mainstream (or popular like they are right now), most AI workflows relied on traditional function calling for tools. Here’s a visual that explains Function calling & MCP:
- **Paragraph after:** Function calling enables LLMs to execute predefined functions based on user inputs. In this approach, developers define specific functions, and the LLM
- **OCR:** \| Function Calling & MCP for AT Agents MCP D on & *MCP Host does not have two LLMs. It is just shown to simplify the visvalisation. ® um ______ N e deepseek \| Prepare fuM[lenuAl . Funckion F o ) 1 Tnvoke tool apIs Calll ns ‘t& joinDailyDoseofbs.com O ‘ @ \| um O . ®_ _ & ______ Tool sponse \| Generote Output deepseelk MCP Host (ee. Claude) 4 T Tools \| &t e ! o Select \| ! Return \| MCP tool \| 1 mee ool \| \| \| I s Send output and query to LM ld'

### fig_0367 — Let’s start with the client, the entity that facilitates conversation between the

- **Page:** 282 (PDF page 284) · **Chapter:** MCP
- **BBox:** [95.62, 67.50, 516.38, 349.50] on page 612×792 pt · **Render:** 1169×783 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.74) · Infrastructure (0.51) · RAG / Knowledge Engineering (0.40) · Tool / Action Fabric (0.40)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.74 → review queue
- **Integrity:** sha `08ef0c93f312a2c4` · dup group `dup_0347` (1)
- **Caption:** Let’s start with the client, the entity that facilitates conversation between the
- **Paragraph after:** Let’s start with the client, the entity that facilitates conversation between the LLM app and the server, offering key capabilities: 1) Sampling The client side always has an LLM.
- **OCR:** &) sampling Sampling lets servers request LLM, completions via the client, ensuring the client controls permissions and mcp client SR S U f_'_w MCP Primitives elicitations Roots allow clients to specify which files servers can access, quiding them to relevant directories while maintaining Elicitation lets servers request specific info from users, providing a structured way for servers to gather information on Controlled by model The functions your LM calls based on user requests. Tools can write to DB, call APTs, modify files, or mcp server Controlled by app Passive data sources offering read-only access to context, like file contents, database Z prompts Controlled by user Pre-built instruction templates that tell the model to work with specific tools security. security boundaries. schemas, or APT docs. and resources. demand. trigger logic. I I 1 I I I \| \| 1 \| 1 \| 12 v T S examples examp

### fig_0368 — It supports the full MCP ecosystem including agents, clients and servers to help

- **Page:** 284 (PDF page 286) · **Chapter:** MCP
- **BBox:** [113.25, 303.56, 498.75, 629.06] on page 612×792 pt · **Render:** 1071×904 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.80) · Infrastructure (0.45) · Agentic AI (0.42) · n8n / Workflow Automation (0.37)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.80 → review queue
- **Integrity:** sha `8652c78e4a896b56` · dup group `dup_0348` (1)
- **Caption:** It supports the full MCP ecosystem including agents, clients and servers to help
- **Paragraph before:** into real development workflows. MCP defines the structure, but developers still need a straightforward way to build agents, configure clients and expose capabilities through servers. This is where the open-source framework mcp-use becomes useful.
- **Paragraph after:** It supports the full MCP ecosystem including agents, clients and servers to help build end-to-end workflows suitable for both experimentation and production environments.
- **OCR:** [0 README & Code of conduct Ay Contributing &3 MIT license 51 Security % Mcp-use Full-Stack MCP Framework mcp-use provides everything you need to build with Model Context Protocol MCP servers, MCP clients and Al agents in 6 lines of code, in both Python and TypeScript. omm Gownloads MCP Conformance (python) \| 13/24 (54 downloads 3 MCP Conformance (typescript) [ Stack * @ MCP Agents - Al agents that can use tools and reason across steps * 4 MCP Clients - Connect any LLM to any MCP server « %X MCP Servers - Build your own MCP servers + (4§ MCP Inspector - Web-based debugger for MCP servers » @ MCP-UI Resources - Build ChatGPT apps with interactive widgets

### fig_0369 — Creating MCP Agents

- **Page:** 285 (PDF page 287) · **Chapter:** MCP
- **BBox:** [134.25, 301.97, 477.75, 549.47] on page 612×792 pt · **Render:** 955×688 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.77) · Agentic AI (0.47) · Tool / Action Fabric (0.41) · Infrastructure (0.41)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.77 → review queue
- **Integrity:** sha `54911084c8b3b47f` · dup group `dup_0349` (1)
- **Heading:** Creating MCP Agents
- **Caption:** This creates an MCP client, connects it to a server (Playwright in this example),
- **Paragraph before:** tools, and exposes them to the LLM in a structured way. This allows the agent to decide when to call a tool, while the framework manages capability loading and communication under the hood. We can build an mcp-enabled agent using mcp-use in just lines of code:
- **Paragraph after:** This creates an MCP client, connects it to a server (Playwright in this example), wraps the server’s capabilities as tools, and passes them to an LLM-powered agent. From here, the LLM can request tool calls naturally during reasoning, while
- **OCR:** ( X X J @ mcp_agent.py from mcp_use import MCPClient, MCPAgent from langchain_openai import ChatOpenAI L ialize MCP client client = MCPClient({ "mcpServers": { "playwright": {"command": "npx" "args": ["@playwright/mcpalatest"]} hatépenAI(modeI:"gpt~4o"), client=client) R at through the result = await agent.run("Find the best restaurant in San Francisco") print(result)

### fig_0370 — Instead of exposing every tool from every server at once - something that often

- **Page:** 287 (PDF page 289) · **Chapter:** MCP
- **BBox:** [128.62, 67.50, 483.38, 288.00] on page 612×792 pt · **Render:** 985×613 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.62) · Infrastructure (0.52) · Tool / Action Fabric (0.50) · Agentic AI (0.40)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.62 → review queue
- **Integrity:** sha `5bd41f7d3da82733` · dup group `dup_0350` (1)
- **Caption:** Instead of exposing every tool from every server at once - something that often
- **Paragraph after:** Instead of exposing every tool from every server at once - something that often leads to tool-name hallucinations, confusion between similar tools and degraded reasoning, the Server Manager keeps the agent’s active toolset intentionally narrow and context-driven.
- **OCR:** MCPAgent ServerManager Web Server File Server Database Server Dynamic Tools

### fig_0371 — MCP figure

- **Page:** 287 (PDF page 289) · **Chapter:** MCP
- **BBox:** [177.00, 551.16, 435.00, 699.66] on page 612×792 pt · **Render:** 717×413 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.71) · Infrastructure (0.51) · Agentic AI (0.41) · Tool / Action Fabric (0.41)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.71 → review queue
- **Integrity:** sha `90ddeec21a94fd53` · dup group `dup_0351` (1)
- **Paragraph before:** Updates tools in real time as servers connect or disconnect ● Provides semantic search over all available tools across servers Enabling it is as simple as setting use_server_manager=True.
- **OCR:** X X J @ server_manager.py agent = MCPAgent( 1lm=ChatOpenAI(model="gpt-4"), client=client, use_server_manager=True

### fig_0372 — This approach is ideal when working with multiple environments or when you

- **Page:** 289 (PDF page 291) · **Chapter:** MCP
- **BBox:** [172.50, 67.50, 439.50, 213.00] on page 612×792 pt · **Render:** 741×404 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.95) · Infrastructure (0.40)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.95 → auto-accept
- **Integrity:** sha `ab1b31c1b4c9d9a0` · dup group `dup_0352` (1)
- **Caption:** This approach is ideal when working with multiple environments or when you
- **Paragraph after:** This approach is ideal when working with multiple environments or when you prefer keeping server settings version-controlled. #2) Create From a Python Dictionary This mirrors the same structure as configuration files but allows programmatic
- **OCR:** ) ® @ @ mcp_client.py from mep_use import MCPClient client = MCPClient(config="config.json") await client.create_all_sessions()

### fig_0373 — #2) Create From a Python Dictionary

- **Page:** 289 (PDF page 291) · **Chapter:** MCP
- **BBox:** [158.62, 303.70, 453.38, 546.70] on page 612×792 pt · **Render:** 819×675 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.89) · Infrastructure (0.41) · Agentic AI (0.38) · Evaluation (0.38)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.89 → auto-accept
- **Integrity:** sha `86bd0dc51dca0ebe` · dup group `dup_0353` (1)
- **Heading:** #2) Create From a Python Dictionary
- **Caption:** This mirrors the same structure as configuration files but allows programmatic
- **Paragraph before:** This approach is ideal when working with multiple environments or when you prefer keeping server settings version-controlled. #2) Create From a Python Dictionary
- **Paragraph after:** This mirrors the same structure as configuration files but allows programmatic customization inside Python. Inspecting the Client Although the agent manages the client internally, mcp-use still allows you to
- **OCR:** [ N N ] @ mcp_client_with_dict.py from mcp_use import MCPClient config = { "mcpServers": { "playwright": { "command": "npx", "args": ["@playwright/mcpalatest"] client = MCPClient(config=config) await client.create_all_sessions()

### fig_0374 — MCP Server

- **Page:** 290 (PDF page 292) · **Chapter:** MCP
- **BBox:** [162.75, 99.28, 449.25, 320.53] on page 612×792 pt · **Render:** 795×615 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.80) · Agentic AI (0.44) · Infrastructure (0.42) · Tool / Action Fabric (0.39)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.80 → review queue
- **Integrity:** sha `ebbb440994162e3d` · dup group `dup_0354` (1)
- **Caption:** MCP Server
- **Paragraph before:** available, we can inspect using this:
- **Paragraph after:** MCP Server Agents and clients decide how to act, but MCP servers are what make those actions possible. A server is the source of truth for capabilities - tools to execute, resources to
- **OCR:** o0 e @ inspect_mcp_client.py from mcp_use import MCPClient, MCPAgent from langchain_openai import ChatOpenAIl agent = MCPAgent( 1lm=ChatOpenAI(model="gpt-40"), client=McPClient(config="config.json") client = agent.client print(client.list_tools())

### fig_0375 — Running this creates a ready-to-use server with:

- **Page:** 291 (PDF page 293) · **Chapter:** MCP
- **BBox:** [169.50, 119.06, 442.50, 266.06] on page 612×792 pt · **Render:** 759×409 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.75) · Infrastructure (0.53) · LLM Engineering (0.39) · Tool / Action Fabric (0.39)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.75 → review queue
- **Integrity:** sha `161d931e02f75a1d` · dup group `dup_0355` (1)
- **Caption:** Running this creates a ready-to-use server with:
- **Paragraph before:** mcp-use includes a project generator that lets you create a new server project with these commands:
- **Paragraph after:** Running this creates a ready-to-use server with: ● A TypeScript entrypoint ● Example tools, prompts and resources
- **OCR:** 00 mcp_project_cli npx create-mcp-use-app my-server cd my-server npm install npm run dev

### fig_0376 — This example defines a complete MCP server with a single tool: get_weather,

- **Page:** 292 (PDF page 294) · **Chapter:** MCP
- **BBox:** [142.50, 172.64, 469.50, 448.64] on page 612×792 pt · **Render:** 909×767 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.71) · Infrastructure (0.51) · Tool / Action Fabric (0.48)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.71 → review queue
- **Integrity:** sha `29398314e90cf1f1` · dup group `dup_0356` (1)
- **Caption:** This example defines a complete MCP server with a single tool: get_weather,
- **Paragraph before:** In mcp-use, tools are registered on the server using a simple declarative definition. Each tool includes a name, input parameters and a callback that returns content to the client. Here is a minimal tool example:
- **Paragraph after:** This example defines a complete MCP server with a single tool: get_weather, which returns a basic weather response. Any MCP-compatible client can automatically discover and invoke this tool during capability negotiation.
- **OCR:** ®®® [ weather_toolts import { createMCPServer } from "mcp-use/server"; const server = createMCPServer("demo", { version: "1.0.0", description: "Example MCP server", 1); server.tool({ name: "get_weather", inputs: [{ name: "city", type: "string", required: true }], cb: async ({ city }) = ({ content: [{ type: "text", text: ‘Weather in ${city} }1I, H, 3); server.listen(3000);

### fig_0377 — Prompts

- **Page:** 293 (PDF page 295) · **Chapter:** MCP
- **BBox:** [147.38, 67.50, 464.62, 198.00] on page 612×792 pt · **Render:** 881×363 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.65) · LLM Engineering (0.55) · Infrastructure (0.45) · Agentic AI (0.40)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.65 → review queue
- **Integrity:** sha `5db444c17e57b585` · dup group `dup_0357` (1)
- **Caption:** Prompts
- **Paragraph after:** Prompts Prompts define reusable instruction templates that agents can invoke to generate structured messages. They let your server provide consistent, well-formed prompts for common tasks.
- **OCR:** 000 8 resources.ts import { resource } from "mcp-use/server"; export const notes = resource.file("./data/notes.md");

### fig_0378 — Sampling

- **Page:** 293 (PDF page 295) · **Chapter:** MCP
- **BBox:** [131.25, 310.28, 480.75, 462.53] on page 612×792 pt · **Render:** 971×423 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.64) · LLM Engineering (0.54) · Infrastructure (0.48) · Agentic AI (0.38)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.64 → review queue
- **Integrity:** sha `df49dd8438e8924b` · dup group `dup_0358` (1)
- **Caption:** Sampling
- **Paragraph before:** Prompts Prompts define reusable instruction templates that agents can invoke to generate structured messages. They let your server provide consistent, well-formed prompts for common tasks.
- **Paragraph after:** Sampling Sampling lets your server ask the client’s model to generate text mid-workflow. It’s useful when the server needs the model to decide, summarize or choose between options.
- **OCR:** ®0®® [ promptsts import { prompt } from "mcp-use/server"; export const review = prompt("code_review", ({ code }) = [ { role: "system", content: "You are a strict code reviewer." }, { role: "user", content: code }, 1);

### fig_0379 — Elicitation

- **Page:** 294 (PDF page 296) · **Chapter:** MCP
- **BBox:** [136.88, 67.50, 475.12, 246.75] on page 612×792 pt · **Render:** 939×498 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.68) · RAG / Knowledge Engineering (0.51) · Infrastructure (0.46) · LLM Engineering (0.40)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.68 → review queue
- **Integrity:** sha `2300db105c4fdf61` · dup group `dup_0359` (1)
- **Caption:** Elicitation
- **Paragraph after:** Elicitation Elicitation requests structured input from the user, such as selecting an option or entering text. This enables interactive workflows where the server needs clarification or a
- **OCR:** ®®® [ samplingts import { sampling } from "mcp-use/server"; export const choose = sampling( "pick_option", async ({ options }) = ({ prompt: ‘Choose the best option: ${options.join(", ")}",

### fig_0380 — Notifications

- **Page:** 294 (PDF page 296) · **Chapter:** MCP
- **BBox:** [139.88, 386.84, 472.12, 574.34] on page 612×792 pt · **Render:** 923×521 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.75) · Infrastructure (0.50) · RAG / Knowledge Engineering (0.40) · n8n / Workflow Automation (0.40)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.75 → review queue
- **Integrity:** sha `3d76e0b883ea492c` · dup group `dup_0360` (1)
- **Caption:** Notifications
- **Paragraph before:** Elicitation requests structured input from the user, such as selecting an option or entering text. This enables interactive workflows where the server needs clarification or a choice.
- **Paragraph after:** Notifications Notifications allow your server to push asynchronous updates such as progress or status changes to the client. They’re ideal for long-running or multi-step operations.
- **OCR:** ®0®® [ eliitation.ts import { elicit } from "mcp-use/server"; // Ask the user to choose a seat export const seatChoice = elicit("seat_choice", { question: "Which seat do you prefer?", type: "string", 3

### fig_0381 — Together, these primitives cover the full MCP surface: operations, structured

- **Page:** 295 (PDF page 297) · **Chapter:** MCP
- **BBox:** [149.62, 67.50, 462.38, 205.50] on page 612×792 pt · **Render:** 869×383 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.81) · Infrastructure (0.44) · Context Engineering (0.40) · RAG / Knowledge Engineering (0.40)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.81 → review queue
- **Integrity:** sha `4aed4afd1490e272` · dup group `dup_0361` (1)
- **Caption:** Together, these primitives cover the full MCP surface: operations, structured
- **Paragraph after:** Together, these primitives cover the full MCP surface: operations, structured context retrieval, user interactions and asynchronous messaging. Any MCP client discovers these automatically during capability negotiation which means your server becomes instantly usable by agents without extra
- **OCR:** 000 8 notifications.ts import { notify } from "mcp-use/server"; export const progress = notify("progress_update");

### fig_0382 — 3) MCP Inspector

- **Page:** 295 (PDF page 297) · **Chapter:** MCP
- **BBox:** [128.25, 439.41, 483.75, 671.16] on page 612×792 pt · **Render:** 987×644 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.82) · Infrastructure (0.48) · Context Engineering (0.37) · Data Engineering (0.37)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.82 → review queue
- **Integrity:** sha `ab5a0dfd5ff6e749` · dup group `dup_0362` (1)
- **Heading:** 3) MCP Inspector
- **Caption:** The Inspector lets you:
- **Paragraph before:** 3) MCP Inspector When you start your server in development mode (npm run dev), mcp-use automatically launches the MCP Inspector, a web-based dashboard for inspecting and debugging MCP servers.
- **Paragraph after:** The Inspector lets you:
- **OCR:** MCP Inspector w4 Inspect and debug MCP (Model Context Protocol) servers Connected Servers Auto-connect @D QO Noservers connected yet. Add a server above to OO getstarted. mcp-use #K @ cithub Inspector Connect © Copy Config Transport Type Streamable HTTP URL http:/flocalhost:3001/sse Tip: You can paste a copled connection config (JSON) to auto- populate the form Connection Type Auto-switch @D Direct v O Authentication = [ Custom Headers & C

### fig_0383 — 4) MCP-UI

- **Page:** 296 (PDF page 298) · **Chapter:** MCP
- **BBox:** [169.12, 428.81, 442.88, 589.31] on page 612×792 pt · **Render:** 761×445 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.89) · Infrastructure (0.46)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.89 → auto-accept
- **Integrity:** sha `95ea0b3695f41ef4` · dup group `dup_0363` (1)
- **Heading:** 4) MCP-UI
- **Caption:** Widgets are useful for things like:
- **Paragraph before:** These widgets let your server surface status, previews or quick visual outputs without requiring a full application. In mcp-use, you define these widgets through a small, focused API. Here’s a simple example:
- **Paragraph after:** Widgets are useful for things like: ● Server health indicators ●
- **OCR:** ®O®® [ mcp-uits import { widget } from "mep-use/ui"; A simple text v t Ter export default widget.text( "hello-widget", () = "Hello from MCP-UI!" );

### fig_0384 — 5) Apps SDK

- **Page:** 297 (PDF page 299) · **Chapter:** MCP
- **BBox:** [124.12, 254.31, 487.88, 464.31] on page 612×792 pt · **Render:** 1011×583 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.74) · n8n / Workflow Automation (0.44) · Tool / Action Fabric (0.44) · Infrastructure (0.44)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.74 → review queue
- **Integrity:** sha `697f42184436bc79` · dup group `dup_0364` (1)
- **Heading:** 5) Apps SDK
- **Caption:** MCP servers can expose these widgets as capabilities, enabling richer workflows
- **Paragraph before:** The Apps SDK is OpenAI’s framework for building interactive UI widgets that appear directly inside ChatGPT or other Apps-SDK-compatible clients. These widgets are written in React and allow tools to return interfaces such as cards, previews or small apps rather than plain text.
- **Paragraph after:** MCP servers can expose these widgets as capabilities, enabling richer workflows with minimal overhead. mcp-use simplifies this process. Instead of manually registering widgets, writing HTML templates, configuring
- **OCR:** ¥ OR @ ChatGPT 5 Looked for avalable tools Called ool v @ display-weather ready v @ rop-use. San Francisco © cumm Askanytting ' p— [ ——— 2 st

### fig_0385 — It defines metadata (so the server can expose the widget as a capability) and a

- **Page:** 298 (PDF page 300) · **Chapter:** MCP
- **BBox:** [116.62, 150.88, 495.38, 491.38] on page 612×792 pt · **Render:** 1053×945 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.72) · Agentic AI (0.47) · Infrastructure (0.47) · Tool / Action Fabric (0.39)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.72 → review queue
- **Integrity:** sha `b3f992273e5dd747` · dup group `dup_0365` (1)
- **Caption:** It defines metadata (so the server can expose the widget as a capability) and a
- **Paragraph before:** ● Apply the required CSP configuration ● Provide the useWidget hook for accessing props, output, theme and state Below is a minimal example of an Apps SDK widget.
- **Paragraph after:** It defines metadata (so the server can expose the widget as a capability) and a React component (which the client renders inside ChatGPT). 6) Tunneling During development, MCP servers usually run on a local machine. When an
- **OCR:** ®®® & apps-sdk-example.tsx // resources/user-card.tsx import { useWidget, type WidgetMetadata } from "mcp-use/react"; // Widget metadata: defines the widget and its inputs export const widgetMetadata: WidgetMetadata = { description: "Display a simple user card", inputs: { name: { type: "string" }, email: { type: "string" } } }; // React component rendered by the Apps SDK export default function UserCard() { const { props } = useWidget<{ name: string; email: string }>(); return ( <div> {props.name} — {props.email} </ div> );

### fig_0386 — mcp-use provides a tunneling command that exposes your local MCP server

- **Page:** 299 (PDF page 301) · **Chapter:** MCP
- **BBox:** [160.12, 67.50, 451.88, 270.75] on page 612×792 pt · **Render:** 811×565 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.88) · Infrastructure (0.47)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.88 → auto-accept
- **Integrity:** sha `bdfc9692946b46a1` · dup group `dup_0366` (1)
- **Caption:** mcp-use provides a tunneling command that exposes your local MCP server
- **Paragraph after:** mcp-use provides a tunneling command that exposes your local MCP server through a temporary, secure public endpoint: This creates a public URL (e.g., https://example.local.mcp-use.run/mcp) that forwards requests to your local /mcp route.
- **OCR:** Local MCP Server HTTPS request Forward request MCP response Forward response Local MCP Server

### fig_0387 — This creates a public URL (e.g., https://example.local.mcp-use.run/mcp) that forwards

- **Page:** 299 (PDF page 301) · **Chapter:** MCP
- **BBox:** [182.62, 329.84, 429.38, 455.09] on page 612×792 pt · **Render:** 685×348 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.95) · Infrastructure (0.40)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.95 → auto-accept
- **Integrity:** sha `49fc9b0485d7721c` · dup group `dup_0367` (1)
- **Caption:** This creates a public URL (e.g., https://example.local.mcp-use.run/mcp) that forwards
- **Paragraph before:** mcp-use provides a tunneling command that exposes your local MCP server through a temporary, secure public endpoint:
- **Paragraph after:** This creates a public URL (e.g., https://example.local.mcp-use.run/mcp) that forwards requests to your local /mcp route. If you're using the built-in development runner, you can enable tunneling
- **OCR:** [ X X ] command-line mcp-use start —-port 3000 mep-use tunnel 3000

### fig_0388 — If you're using the built-in development runner, you can enable tunneling

- **Page:** 299 (PDF page 301) · **Chapter:** MCP
- **BBox:** [161.62, 511.69, 450.38, 678.94] on page 612×792 pt · **Render:** 803×464 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.95) · Infrastructure (0.40)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.95 → auto-accept
- **Integrity:** sha `ca5b4688186751e0` · dup group `dup_0368` (1)
- **Caption:** If you're using the built-in development runner, you can enable tunneling
- **Paragraph before:** mcp-use provides a tunneling command that exposes your local MCP server through a temporary, secure public endpoint: This creates a public URL (e.g., https://example.local.mcp-use.run/mcp) that forwards requests to your local /mcp route.
- **Paragraph after:** If you're using the built-in development runner, you can enable tunneling
- **OCR:** - # Tunnel Created Successfully! - ,tT€T(/ W ) @ Public URL: https://happy-blue-cat.local.mcp-use.run/mcp Subdomain: happy-blue-cat Local Port: 3000

### fig_0389 — This automatically spins up your local server and creates a tunnel for it.

- **Page:** 300 (PDF page 302) · **Chapter:** MCP
- **BBox:** [189.00, 99.28, 423.00, 218.53] on page 612×792 pt · **Render:** 650×332 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.80) · Infrastructure (0.48) · Tool / Action Fabric (0.41)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.80 → review queue
- **Integrity:** sha `cba60b22046c00ff` · dup group `dup_0227` (3)
- **Caption:** This automatically spins up your local server and creates a tunnel for it.
- **Paragraph before:** without running a separate command:
- **Paragraph after:** This automatically spins up your local server and creates a tunnel for it. Other tunneling tools such as ngrok can also be used, provided the public URL maps to the /mcp endpoint: Tunneling enables:
- **OCR:** X X J command-line mcp-use start ——port 3000 —-tunnel

### fig_0390 — Tunneling enables:

- **Page:** 300 (PDF page 302) · **Chapter:** MCP
- **BBox:** [191.62, 309.42, 420.38, 432.42] on page 612×792 pt · **Render:** 635×342 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.6
- **Mapping:** Agent Protocol Fabric (0.80) · Tool / Action Fabric (0.41) · Evaluation (0.41) · Infrastructure (0.41)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.80 → review queue
- **Integrity:** sha `dcac251229bdf742` · dup group `dup_0369` (1)
- **Caption:** Tunneling enables:
- **Paragraph before:** without running a separate command: This automatically spins up your local server and creates a tunnel for it. Other tunneling tools such as ngrok can also be used, provided the public URL maps to the /mcp endpoint:
- **Paragraph after:** Tunneling enables: ● Testing with real MCP clients ●
- **OCR:** ) ® ® command-line ngrok http 3000

### fig_0391 — As long as the endpoint is reachable, agents immediately detect new tools or

- **Page:** 301 (PDF page 303) · **Chapter:** MCP
- **BBox:** [190.50, 249.80, 421.50, 373.55] on page 612×792 pt · **Render:** 641×344 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.6
- **Mapping:** Agent Protocol Fabric (0.70) · Infrastructure (0.48) · Agentic AI (0.44) · Tool / Action Fabric (0.44)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.70 → review queue
- **Integrity:** sha `3ca0a5618cff8361` · dup group `dup_0370` (1)
- **Caption:** As long as the endpoint is reachable, agents immediately detect new tools or
- **Paragraph before:** ● mcp-use Cloud Regardless of the platform, the flow is the same: build your project and expose the /mcp endpoint publicly.
- **Paragraph after:** As long as the endpoint is reachable, agents immediately detect new tools or capabilities without additional setup. For the simplest workflow, mcp-use includes a hosted deployment platform. It builds and serves your MCP server with a single command.
- **OCR:** 000 command-line npm run build npm start

### fig_0392 — After deployment, you receive:

- **Page:** 301 (PDF page 303) · **Chapter:** MCP
- **BBox:** [191.62, 484.19, 420.38, 640.94] on page 612×792 pt · **Render:** 635×436 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.69) · Infrastructure (0.58) · Agentic AI (0.39) · n8n / Workflow Automation (0.39)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.69 → review queue
- **Integrity:** sha `c569e3f6e6aea97b` · dup group `dup_0371` (1)
- **Caption:** After deployment, you receive:
- **Paragraph before:** As long as the endpoint is reachable, agents immediately detect new tools or capabilities without additional setup. For the simplest workflow, mcp-use includes a hosted deployment platform. It builds and serves your MCP server with a single command.
- **Paragraph after:** After deployment, you receive: ● A public MCP endpoint
- **OCR:** 200 command-line ! mcp-use login mcp-use deploy

### fig_0393 — Why do we need optimization?

- **Page:** 304 (PDF page 306) · **Chapter:** LLM Optimization
- **BBox:** [119.62, 214.25, 492.38, 347.00] on page 612×792 pt · **Render:** 1035×368 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Infrastructure (0.71) · Evaluation (0.57) · Business Automation (0.42)
- **Primary branch:** infrastructure · **Confidence:** 0.71 → review queue
- **Integrity:** sha `aaa8c2d295d87ee7` · dup group `dup_0372` (1)
- **Heading:** Why do we need optimization?
- **Caption:** However, high accuracy does not automatically translate to a practical system. A
- **Paragraph before:** Machine learning systems are usually developed with one primary objective: improve accuracy. As a result, models grow larger and more complex because bigger models often perform better during training.
- **Paragraph after:** However, high accuracy does not automatically translate to a practical system. A model that performs well in experiments can still be unsuitable for deployment if it is slow, costly to run, or difficult to scale. In production, the requirements shift.
- **OCR:** / Gireat performance \/ Com, \ o plex Model Low Pmc‘tico.l u‘till‘ty ><

### fig_0394 — Why do we need optimization?

- **Page:** 304 (PDF page 306) · **Chapter:** LLM Optimization
- **BBox:** [113.25, 501.23, 498.75, 649.73] on page 612×792 pt · **Render:** 1071×412 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Infrastructure (0.76) · Agent Memory (0.47) · Business Automation (0.47)
- **Primary branch:** infrastructure · **Confidence:** 0.76 → review queue
- **Integrity:** sha `a2361547e4843a4b` · dup group `dup_0373` (1)
- **Heading:** Why do we need optimization?
- **Caption:** These constraints determine whether a model can reliably serve real users. Even
- **Paragraph before:** it is slow, costly to run, or difficult to scale. In production, the requirements shift. A deployed model must respond quickly, handle unpredictable load, fit within strict memory limits, and remain cost-efficient to operate.
- **Paragraph after:** These constraints determine whether a model can reliably serve real users. Even a highly accurate system may be unusable if inference is slow or memory-hungry.
- **OCR:** Dep loymen‘t considerations —— Model utilization

### fig_0395 — ●

- **Page:** 305 (PDF page 307) · **Chapter:** LLM Optimization
- **BBox:** [115.88, 97.28, 496.12, 275.03] on page 612×792 pt · **Render:** 1057×493 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Infrastructure (0.84) · Evaluation (0.51)
- **Primary branch:** infrastructure · **Confidence:** 0.84 → review queue
- **Integrity:** sha `fa9b0f54fb5bd015` · dup group `dup_0374` (1)
- **Caption:** ●
- **Paragraph before:** To illustrate this, consider the two models below.
- **Paragraph after:** ● Model A is more accurate, but it is significantly slower and much larger. ● Model B is slightly less accurate but is faster, smaller, and far easier to
- **OCR:** & Model A Accuracy: 49% Run-time: 2 seconds Size: 125 MBs & Model B Accumcc./: at% Run-time: 0.1 seconds Size: 10 MBs

### fig_0396 — They aim to make the model smaller - that is why the name “model compression.”

- **Page:** 306 (PDF page 308) · **Chapter:** LLM Optimization
- **BBox:** [127.50, 67.50, 484.50, 183.75] on page 612×792 pt · **Render:** 991×323 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Infrastructure (0.63) · Context Engineering (0.54) · Observability (0.54)
- **Primary branch:** infrastructure · **Confidence:** 0.63 → review queue
- **Integrity:** sha `53de7b9518074271` · dup group `dup_0375` (1)
- **Caption:** They aim to make the model smaller - that is why the name “model compression.”
- **Paragraph after:** They aim to make the model smaller - that is why the name “model compression.” Typically, it is expected that a smaller model will: ● Have a lower inference latency as smaller models can deliver quicker predictions, making them well-suited for real-time or low-latency
- **OCR:** Co»\pr‘essiov\ S Small Modlel Large Model

### fig_0397 — ●

- **Page:** 306 (PDF page 308) · **Chapter:** LLM Optimization
- **BBox:** [113.25, 387.56, 498.75, 559.31] on page 612×792 pt · **Render:** 1071×477 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Infrastructure (0.72) · AI / ML Foundation (0.54) · Agent Memory (0.44)
- **Primary branch:** infrastructure · **Confidence:** 0.72 → review queue
- **Integrity:** sha `7e2bd72411fd8e00` · dup group `dup_0376` (1)
- **Caption:** ●
- **Paragraph before:** ● Be easy to scale due to their reduced computational demands. ● Have a smaller memory footprint. We’ll look at four techniques that help us achieve this:
- **Paragraph after:** ● Knowledge Distillation ● Pruning ●
- **OCR:** Low-rank Kv\owled e Factorization Disti “o:tuov\ AN et Model Cow\(nre_ssion Quantization Pr‘uning

### fig_0398 — Distillation: In this context, distillation means transferring or condensing

- **Page:** 307 (PDF page 309) · **Chapter:** LLM Optimization
- **BBox:** [156.00, 305.38, 456.00, 525.12] on page 612×792 pt · **Render:** 833×610 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.6
- **Mapping:** AI / ML Foundation (0.64) · Infrastructure (0.57) · Context Engineering (0.49)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.64 → review queue
- **Integrity:** sha `936f39be79698c3a` · dup group `dup_0377` (1)
- **Caption:** Distillation: In this context, distillation means transferring or condensing
- **Paragraph before:** Knowledge: Refers to the understanding, insights, or information that a machine learning model has acquired during training. This “knowledge” can be typically represented by the model’s parameters, learned patterns, and its ability to make predictions.
- **Paragraph after:** Distillation: In this context, distillation means transferring or condensing knowledge from one model to another. It involves training the student model to mimic the behavior of the teacher model, effectively transferring the teacher's knowledge.

### fig_0399 — This is a two-step process:

- **Page:** 308 (PDF page 310) · **Chapter:** LLM Optimization
- **BBox:** [127.88, 67.50, 484.12, 222.00] on page 612×792 pt · **Render:** 989×429 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Infrastructure (0.98)
- **Primary branch:** infrastructure · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `82035920eec86d95` · dup group `dup_0378` (1)
- **Caption:** This is a two-step process:
- **Paragraph after:** This is a two-step process: ● Train the large model as you typically would. This is called the “teacher” model.
- **OCR:** Giant Teacher Model Knowle,ol e d\S'tl“atton & Sma“gf‘ M Pl a\|

### fig_0400 — The primary objective of knowledge distillation is to transfer the knowledge, or

- **Page:** 308 (PDF page 310) · **Chapter:** LLM Optimization
- **BBox:** [119.62, 346.45, 492.38, 497.20] on page 612×792 pt · **Render:** 1035×419 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Infrastructure (0.74) · AI / ML Foundation (0.61)
- **Primary branch:** infrastructure · **Confidence:** 0.74 → review queue
- **Integrity:** sha `1159028b089af3ab` · dup group `dup_0379` (1)
- **Caption:** The primary objective of knowledge distillation is to transfer the knowledge, or
- **Paragraph before:** Train the large model as you typically would. This is called the “teacher” model. ● Train a smaller model, which is intended to mimic the behavior of the larger model. This is also called the “student” model.
- **Paragraph after:** The primary objective of knowledge distillation is to transfer the knowledge, or the learned insights, from the teacher to the student model. This allows the student model to achieve comparable performance with fewer parameters and reduced computational complexity.
- **OCR:** Tronsfer know{e,o(ge, to Train Swall Student T e_acker Model Model

### fig_0401 — 2) Pruning

- **Page:** 309 (PDF page 311) · **Chapter:** LLM Optimization
- **BBox:** [131.25, 375.23, 480.75, 520.73] on page 612×792 pt · **Render:** 971×404 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Infrastructure (0.74) · Evaluation (0.61)
- **Primary branch:** infrastructure · **Confidence:** 0.74 → review queue
- **Integrity:** sha `98a33fd787900007` · dup group `dup_0380` (1)
- **Heading:** 2) Pruning
- **Caption:** Of course, dropping nodes will result in a drop in the model’s accuracy.
- **Paragraph before:** What’s more, DistilBERT is roughly 60% faster in inference. 2) Pruning Pruning is commonly used in tree-based models, where it involves removing branches (or nodes) to simplify the model.
- **Paragraph after:** Of course, dropping nodes will result in a drop in the model’s accuracy. Thus, in the case of decision trees, the core idea is to iteratively drop sub-trees, which, after removal, leads to: ●
- **OCR:** K s Cm Fu"y-tmineol Pruned Decision Tree Decision Tree .

### fig_0402 — In the image above, both sub-trees result in the same increase in cost. However,

- **Page:** 310 (PDF page 312) · **Chapter:** LLM Optimization
- **BBox:** [113.62, 67.50, 498.38, 256.50] on page 612×792 pt · **Render:** 1069×525 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Business Automation (0.68) · Infrastructure (0.68)
- **Primary branch:** business-automation · **Confidence:** 0.68 → review queue
- **Integrity:** sha `baab22d9d7449601` · dup group `dup_0381` (1)
- **Caption:** In the image above, both sub-trees result in the same increase in cost. However,
- **Paragraph after:** In the image above, both sub-trees result in the same increase in cost. However, it makes more sense to remove the sub-tree with more nodes to reduce computational complexity. The same idea can be translated to neural networks as well.
- **OCR:** Cost ncrease Post sub-tree removal ./'\.0.5 e ;:il‘{:"m::i 0 5 Rewmove this sub-tree ) because it has more nodes

### fig_0403 — Removing an entire layer is another option. But we rarely practice it because it

- **Page:** 310 (PDF page 312) · **Chapter:** LLM Optimization
- **BBox:** [106.88, 430.53, 505.12, 573.78] on page 612×792 pt · **Render:** 1107×398 px
- **Composition:** raster · **Role:** result · **Quality:** 0.6
- **Mapping:** Infrastructure (0.84) · Agent Protocol Fabric (0.51)
- **Primary branch:** infrastructure · **Confidence:** 0.84 → review queue
- **Integrity:** sha `508e0940cec95315` · dup group `dup_0382` (1)
- **Caption:** Removing an entire layer is another option. But we rarely practice it because it
- **Paragraph before:** The same idea can be translated to neural networks as well. As you may have guessed, pruning in neural networks involves identifying and eliminating specific connections or neurons that contribute minimally to the model’s overall performance.
- **Paragraph after:** Removing an entire layer is another option. But we rarely practice it because it may result in misaligned weight matrices. What’s more, it isn't easy to quantify the contribution of a specific layer towards the final output.

### fig_0404 — The idea is to eliminate entire nodes from the network.

- **Page:** 311 (PDF page 313) · **Chapter:** LLM Optimization
- **BBox:** [109.50, 226.22, 502.50, 343.97] on page 612×792 pt · **Render:** 1091×327 px
- **Composition:** raster · **Role:** result · **Quality:** 0.6
- **Mapping:** Infrastructure (0.84) · Agent Memory (0.51)
- **Primary branch:** infrastructure · **Confidence:** 0.84 → review queue
- **Integrity:** sha `f5f8cc6671825aa6` · dup group `dup_0383` (1)
- **Caption:** The idea is to eliminate entire nodes from the network.
- **Paragraph before:** With pruning, the goal is to create a more compact neural network while retaining as much predictive power as possible. This is primarily done in two ways: Neuron pruning:
- **Paragraph after:** The idea is to eliminate entire nodes from the network. As a result, the matrices representing the layers become small. This results in faster inference and lower memory usage. Weight pruning:
- **OCR:** Neuron Pmning Xi—»O xa_,()

### fig_0405 — This results in faster inference and lower memory usage.

- **Page:** 311 (PDF page 313) · **Chapter:** LLM Optimization
- **BBox:** [129.38, 409.06, 482.62, 567.31] on page 612×792 pt · **Render:** 981×439 px
- **Composition:** raster · **Role:** result · **Quality:** 0.6
- **Mapping:** Infrastructure (0.74) · Agent Memory (0.61)
- **Primary branch:** infrastructure · **Confidence:** 0.74 → review queue
- **Integrity:** sha `d56f664f6cf0e8cf` · dup group `dup_0384` (2)
- **Caption:** This results in faster inference and lower memory usage.
- **Paragraph before:** This is primarily done in two ways: Neuron pruning: The idea is to eliminate entire nodes from the network. As a result, the matrices representing the layers become small.
- **Paragraph after:** This results in faster inference and lower memory usage. Weight pruning:

### fig_0406 — ●

- **Page:** 312 (PDF page 314) · **Chapter:** LLM Optimization
- **BBox:** [107.62, 67.50, 504.38, 186.00] on page 612×792 pt · **Render:** 1103×329 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.6
- **Mapping:** Infrastructure (0.98)
- **Primary branch:** infrastructure · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `0327e19746d0a12e` · dup group `dup_0385` (1)
- **Caption:** ●
- **Paragraph after:** ● This involves eliminating edges from the network. ● Weight pruning can be thought of as placing zeros in the matrices to represent the removed edges.
- **OCR:** deht Pmninﬁ

### fig_0407 — ●

- **Page:** 312 (PDF page 314) · **Chapter:** LLM Optimization
- **BBox:** [143.25, 260.88, 468.75, 409.38] on page 612×792 pt · **Render:** 905×413 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.6
- **Mapping:** Infrastructure (0.98)
- **Primary branch:** infrastructure · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `1c8a69379b1f0c54` · dup group `dup_0384` (2)
- **Caption:** ●
- **Paragraph before:** ● This involves eliminating edges from the network. ● Weight pruning can be thought of as placing zeros in the matrices to represent the removed edges.
- **Paragraph after:** ● However, in this case, the size of the matrices remains unaffected. ● Thus, the size of the matrices remains the same, but they become sparse. ●

### fig_0408 — The idea will become more clear if we understand these individual terms:

- **Page:** 313 (PDF page 315) · **Chapter:** LLM Optimization
- **BBox:** [131.25, 166.64, 480.75, 338.39] on page 612×792 pt · **Render:** 971×477 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.6
- **Mapping:** Infrastructure (0.84) · Agent Protocol Fabric (0.51)
- **Primary branch:** infrastructure · **Confidence:** 0.84 → review queue
- **Integrity:** sha `e38815c3b97a920f` · dup group `dup_0386` (2)
- **Caption:** The idea will become more clear if we understand these individual terms:
- **Paragraph before:** At its core, Low-rank Factorization aims to approximate the weight matrices of neural networks using lower-rank matrices. Essentially, the idea is to represent complex weight matrices as products of two or more simpler matrices.
- **Paragraph after:** The idea will become more clear if we understand these individual terms: Low-rank: ● In linear algebra, the “rank” of a matrix refers to the maximum number of linearly independent rows (or columns) in that matrix.
- **OCR:** % Small Matrix 2

### fig_0409 — There are many different matrix factorization methods available, such as Singular

- **Page:** 314 (PDF page 316) · **Chapter:** LLM Optimization
- **BBox:** [126.38, 206.44, 485.62, 383.44] on page 612×792 pt · **Render:** 997×492 px
- **Composition:** raster · **Role:** process · **Quality:** 0.6
- **Mapping:** Infrastructure (0.98)
- **Primary branch:** infrastructure · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `298370f3f2db8969` · dup group `dup_0386` (2)
- **Caption:** There are many different matrix factorization methods available, such as Singular
- **Paragraph before:** Step 1) Perform Matrix Factorization In a neural network, every layer will have a weight matrix. We can decompose these original weight matrices into lower-rank approximations.
- **Paragraph after:** There are many different matrix factorization methods available, such as Singular Value Decomposition (SVD), Non-negative Matrix Factorization (NMF), or Truncated SVD. Step 2) Specify Rank
- **OCR:** % Small Matrix 2

### fig_0410 — The choice of rank k is directly linked to the trade-off between model size

- **Page:** 315 (PDF page 317) · **Chapter:** LLM Optimization
- **BBox:** [127.88, 67.50, 484.12, 249.00] on page 612×792 pt · **Render:** 989×504 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Infrastructure (0.98)
- **Primary branch:** infrastructure · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `ed3f2dfc76a34460` · dup group `dup_0387` (1)
- **Caption:** The choice of rank k is directly linked to the trade-off between model size
- **Paragraph after:** The choice of rank k is directly linked to the trade-off between model size reduction and preservation of information. Step 3) Reconstruct the Weight Matrices Once you've obtained the lower-rank matrices, you can use them to transform the
- **OCR:** Small Matrix 1 % Small Matrix 2 % Raunk — Rank —

### fig_0411 — The benefit of doing this is that it reduces the computational complexity of the

- **Page:** 315 (PDF page 317) · **Chapter:** LLM Optimization
- **BBox:** [129.00, 383.44, 483.00, 603.19] on page 612×792 pt · **Render:** 983×610 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Infrastructure (0.98)
- **Primary branch:** infrastructure · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `18a9e7581bb01d8a` · dup group `dup_0388` (1)
- **Caption:** The benefit of doing this is that it reduces the computational complexity of the
- **Paragraph before:** reduction and preservation of information. Step 3) Reconstruct the Weight Matrices Once you've obtained the lower-rank matrices, you can use them to transform the input instead of the original weight matrices.
- **Paragraph after:** The benefit of doing this is that it reduces the computational complexity of the neural network while retaining important features learned during training. By replacing the original weight matrices with their lower-rank approximations, we can effectively reduce the number of parameters in the model, which reduces
- **OCR:** New Weight wmatrix Factored Matrix 2 AAW 1 Closelc/ e,qwxl to Oﬁginal W¢13h‘t matrix

### fig_0412 — 4) Quantization

- **Page:** 316 (PDF page 318) · **Chapter:** LLM Optimization
- **BBox:** [118.88, 345.47, 493.12, 502.97] on page 612×792 pt · **Render:** 1039×438 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.53) · Agent Memory (0.53) · Infrastructure (0.53) · Data Engineering (0.47)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.53 → review queue
- **Integrity:** sha `c0b0369503dd6a7e` · dup group `dup_0101` (2)
- **Heading:** 4) Quantization
- **Caption:** This results in a significant decrease in the amount of memory required to store
- **Paragraph before:** parameters. But using the biggest data type also means consuming more memory. As you may have guessed, Quantization involves using lower-bit representations, such as 16-bit, 8-bit, 4-bit, or even 1-bit, to represent parameters.
- **Paragraph after:** This results in a significant decrease in the amount of memory required to store the model's parameters. For instance, consider your model has over a million parameters, each represented with 32-bit floating-point numbers.
- **OCR:** Weight Quantized Weight wmatrix wmatrix Quan‘tnza‘tloﬂ ed as

### fig_0413 — LLMs, however, deal with variable-length inputs (the prompt) and generate

- **Page:** 318 (PDF page 320) · **Chapter:** LLM Optimization
- **BBox:** [136.12, 67.50, 475.88, 165.75] on page 612×792 pt · **Render:** 943×273 px
- **Composition:** raster · **Role:** process · **Quality:** 0.6
- **Mapping:** Infrastructure (0.78) · LLM Engineering (0.57)
- **Primary branch:** infrastructure · **Confidence:** 0.78 → review queue
- **Integrity:** sha `057df64c89c18d0e` · dup group `dup_0389` (1)
- **Caption:** LLMs, however, deal with variable-length inputs (the prompt) and generate
- **Paragraph after:** LLMs, however, deal with variable-length inputs (the prompt) and generate variable-length outputs. So if you batch some requests, all will finish at different times, and the GPU would have to wait for the longest request to finish before it can process new

### fig_0414 — So if you batch some requests, all will finish at different times, and the GPU

- **Page:** 318 (PDF page 320) · **Chapter:** LLM Optimization
- **BBox:** [130.50, 220.84, 481.50, 322.09] on page 612×792 pt · **Render:** 975×281 px
- **Composition:** raster · **Role:** process · **Quality:** 0.6
- **Mapping:** Infrastructure (0.91) · LLM Engineering (0.44)
- **Primary branch:** infrastructure · **Confidence:** 0.91 → auto-accept
- **Integrity:** sha `177a1cb3f55d8e18` · dup group `dup_0390` (1)
- **Caption:** So if you batch some requests, all will finish at different times, and the GPU
- **Paragraph before:** LLMs, however, deal with variable-length inputs (the prompt) and generate variable-length outputs.
- **Paragraph after:** So if you batch some requests, all will finish at different times, and the GPU would have to wait for the longest request to finish before it can process new requests. This leads to idle time on the GPU: Continuous Batching solves this.

### fig_0415 — Continuous Batching solves this.

- **Page:** 318 (PDF page 320) · **Chapter:** LLM Optimization
- **BBox:** [160.88, 396.97, 451.12, 627.22] on page 612×792 pt · **Render:** 807×640 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Infrastructure (0.68) · AI / ML Foundation (0.61) · Observability (0.41)
- **Primary branch:** infrastructure · **Confidence:** 0.68 → review queue
- **Integrity:** sha `c269cc0c1cc20fe5` · dup group `dup_0391` (2)
- **Caption:** Continuous Batching solves this.
- **Paragraph before:** variable-length outputs. So if you batch some requests, all will finish at different times, and the GPU would have to wait for the longest request to finish before it can process new requests. This leads to idle time on the GPU:
- **Paragraph after:** Continuous Batching solves this. Instead of waiting for the entire batch to finish, the system monitors all sequences and swaps completed ones (<EOS> token) with new queries:
- **OCR:** Prowmpt token @ Generated token ® End of sequence token

### fig_0416 — This keeps the GPU pipeline full and maximizes utilization.

- **Page:** 319 (PDF page 321) · **Chapter:** LLM Optimization
- **BBox:** [157.88, 67.50, 454.12, 303.00] on page 612×792 pt · **Render:** 823×654 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Infrastructure (0.65) · AI / ML Foundation (0.53) · Data Engineering (0.47) · LLM Engineering (0.41)
- **Primary branch:** infrastructure · **Confidence:** 0.65 → review queue
- **Integrity:** sha `ce73c84866d90790` · dup group `dup_0391` (2)
- **Caption:** This keeps the GPU pipeline full and maximizes utilization.
- **Paragraph after:** This keeps the GPU pipeline full and maximizes utilization. Prefill-decode disaggregation LLM inference is a two-stage process with fundamentally different resource requirements.
- **OCR:** IIIDEIID BRRE 1] & Prompt token @ Generated token ® End of sequence token

### fig_0417 — Prefill-decode disaggregation

- **Page:** 319 (PDF page 321) · **Chapter:** LLM Optimization
- **BBox:** [115.50, 507.13, 496.50, 585.12] on page 612×792 pt · **Render:** 1059×217 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Infrastructure (0.70) · AI / ML Foundation (0.47) · Observability (0.47) · LLM Engineering (0.41)
- **Primary branch:** infrastructure · **Confidence:** 0.70 → review queue
- **Integrity:** sha `6545f03267651999` · dup group `dup_0392` (1)
- **Heading:** Prefill-decode disaggregation
- **Caption:** Running both stages on the GPU means the compute-heavy prefill requests will
- **Paragraph before:** The prefill stage processes all the input prompt tokens at once, so this is compute-heavy. ● The decode stage autoregressively generates the output, and this demands low latency.
- **Paragraph after:** Running both stages on the GPU means the compute-heavy prefill requests will interfere with the latency-sensitive decode requests. Prefill-decode disaggregation solves this by allocating a dedicated pool of GPUs for the prefill stage and another pool for the decode stage.
- **OCR:** Decode _>_> &) Time to First Token (TTFT)

### fig_0418 — In contrast, a standard ML model typically has a single, unified computation

- **Page:** 320 (PDF page 322) · **Chapter:** LLM Optimization
- **BBox:** [149.25, 67.50, 462.75, 253.50] on page 612×792 pt · **Render:** 871×517 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.59) · Infrastructure (0.59) · Agent Memory (0.47) · RAG / Knowledge Engineering (0.41)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.59 → review queue
- **Integrity:** sha `89707c9778459035` · dup group `dup_0393` (1)
- **Caption:** In contrast, a standard ML model typically has a single, unified computation
- **Paragraph after:** In contrast, a standard ML model typically has a single, unified computation phase. GPU memory management + KV caching Generating a new token uses the key and value vectors of all previous tokens. To
- **OCR:** ~ Compute bound \ i 1 \| v 1 1 i ’ KV cache transfer ~ Memory bound st token Remaining tokens

### fig_0419 — GPU memory management + KV caching

- **Page:** 320 (PDF page 322) · **Chapter:** LLM Optimization
- **BBox:** [144.75, 388.27, 467.25, 716.02] on page 612×792 pt · **Render:** 895×910 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.63) · RAG / Knowledge Engineering (0.56) · Infrastructure (0.47) · Agent Memory (0.40)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.63 → review queue
- **Integrity:** sha `d827f5c4926b2b63` · dup group `dup_0394` (1)
- **Heading:** GPU memory management + KV caching
- **Paragraph before:** phase. GPU memory management + KV caching Generating a new token uses the key and value vectors of all previous tokens. To avoid recomputing these vectors for all tokens over and over, we cache them.
- **OCR:** \| KV Caching in LLMs ’u\%; join.DailyDoseofDS.com Input Hidden states Projection Logits over vocabulary \| Insight 1 EN- £ § LIE = = The network only E e R ) = = needs the last ' E i b ! \| * = hidden state ! \| —— : T to predict the for \|-~ S 9 10 ) = P :’ L=T=1-] — s next token. ! ArgMax \| it clustering <- - - - - il Query s QK" TInput P \a{for) = ! \| QK" Vi, KMeans \| \| \| = > [0a[asz [0k [acks Insight 2 is : \| The last hidden STty ! state only depends used ! on last token's \| query vector and for i all key vectors and value vectors. For 5™ token For 6™ token For 7™ token For 5™ token For 6" token For 7' token & \| 5 3 v v v The key vectors \| _ o[BG oy [Be val\| o \|SGE] o [EVa and value vectors [ K\| 55 Vs Vs Vs used during Ka Ka :< Va Va Va previous tokens ks > Vs :’ do not change. L = Cache them to avoid o mﬁm{;‘--n recomputing them. [ v kv ]

### fig_0420 — That said, KV cache takes up a significant memory since it’s stored in contiguous

- **Page:** 321 (PDF page 323) · **Chapter:** LLM Optimization
- **BBox:** [168.75, 166.64, 443.25, 351.14] on page 612×792 pt · **Render:** 763×513 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.6
- **Mapping:** Agent Memory (0.55) · Infrastructure (0.55) · Software Architecture (0.50) · LLM Engineering (0.45)
- **Primary branch:** agent-memory · **Confidence:** 0.55 → review queue
- **Integrity:** sha `16b66bca94471d93` · dup group `dup_0395` (1)
- **Caption:** That said, KV cache takes up a significant memory since it’s stored in contiguous
- **Paragraph before:** This KV Cache grows linearly with the total length of the conversation history. But in many workflows, inputs like the system prompts are shared across many requests. So we can avoid recomputing them by using these KV vectors across all chats:
- **Paragraph after:** That said, KV cache takes up a significant memory since it’s stored in contiguous blocks. This wastes GPU memory and leads to memory fragmentation: Paged Attention solves this problem by storing KV caching in non-contiguous blocks and then using a lookup table to track these blocks. The LLM only loads
- **OCR:** e Vo X\ 3946 PRiovs [

### fig_0421 — Paged Attention solves this problem by storing KV caching in non-contiguous

- **Page:** 321 (PDF page 323) · **Chapter:** LLM Optimization
- **BBox:** [159.75, 406.25, 452.25, 495.50] on page 612×792 pt · **Render:** 813×248 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Agent Memory (0.58) · Infrastructure (0.54) · AI / ML Foundation (0.49) · RAG / Knowledge Engineering (0.44)
- **Primary branch:** agent-memory · **Confidence:** 0.58 → review queue
- **Integrity:** sha `a597de40d33cdc91` · dup group `dup_0396` (1)
- **Caption:** Paged Attention solves this problem by storing KV caching in non-contiguous
- **Paragraph before:** requests. So we can avoid recomputing them by using these KV vectors across all chats: That said, KV cache takes up a significant memory since it’s stored in contiguous blocks. This wastes GPU memory and leads to memory fragmentation:
- **Paragraph after:** Paged Attention solves this problem by storing KV caching in non-contiguous blocks and then using a lookup table to track these blocks. The LLM only loads the blocks it needs, instead of loading everything at once. We will cover Paged Attention in another issue.
- **OCR:** J ) Available memory M ' emory \| - Allocated memory - needed

### fig_0422 — Different open-source frameworks each have their own implementations for

- **Page:** 322 (PDF page 324) · **Chapter:** LLM Optimization
- **BBox:** [148.50, 246.00, 463.50, 571.50] on page 612×792 pt · **Render:** 875×904 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.54) · Software Architecture (0.54) · Infrastructure (0.54) · RAG / Knowledge Engineering (0.41)
- **Primary branch:** llm-engineering · **Confidence:** 0.54 → review queue
- **Integrity:** sha `f96e15199a98b26f` · dup group `dup_0397` (1)
- **Caption:** Different open-source frameworks each have their own implementations for
- **Paragraph before:** If a new query comes in with a shared prefix that has already been cached on Replica A, but the router sends it to Replica B (which is less busy), Replica B has to recompute the entire prefix’s KV cache. Prefix-aware routing solves this.
- **Paragraph after:** Different open-source frameworks each have their own implementations for prefix-aware routing. Generally, prefix-aware routing requires the router to maintain a map or table (or use a predictive algorithm) that tracks which KV prefixes are currently cached on
- **OCR:** Request 4 Request B Request ¢ Reehm A RePhcg B Replica {al

### fig_0423 — Model sharding strategies

- **Page:** 323 (PDF page 325) · **Chapter:** LLM Optimization
- **BBox:** [137.62, 176.95, 474.38, 549.70] on page 612×792 pt · **Render:** 935×1035 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Infrastructure (0.72) · AI / ML Foundation (0.51) · RAG / Knowledge Engineering (0.43) · Software Architecture (0.39)
- **Primary branch:** infrastructure · **Confidence:** 0.72 → review queue
- **Integrity:** sha `752a12627dc0f3be` · dup group `dup_0398` (1)
- **Heading:** Model sharding strategies
- **Caption:** LLMs, like Mixture of Experts (MoE), are complicated.
- **Paragraph before:** When a new query arrives, the router sends the query to the replica that has the relevant prefix already cached. Model sharding strategies There are several strategies to scale a dense ML model:
- **Paragraph after:** LLMs, like Mixture of Experts (MoE), are complicated.
- **OCR:** '4 Strategies for Multi-GPU Training ) % TR r— Model ¢ W 1 © Layer on 1%t gPU parallelism o & i © Lager on 2" GpU Tensor () Neurons on 15t GPU pamllelism == = v \ Ho (O Neurons on 2" GPU Data subset #1 _a B s ‘ ‘00 50 Model copy 0, Pﬂraueusm Data subset #2 : Xl x2 x3 == B Lc;gn on3?Geu < - 2" lager Ptpelme on 2" Gey > 1 layer parallelism on e Gey x\| x2 x3 Data subset #1 Data subset #2

### fig_0424 — MoE models use a specialized parallelism strategy called expert parallelism,

- **Page:** 324 (PDF page 326) · **Chapter:** LLM Optimization
- **BBox:** [154.12, 67.50, 457.88, 374.25] on page 612×792 pt · **Render:** 843×852 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.84) · Infrastructure (0.51)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.84 → review queue
- **Integrity:** sha `47994b11b12e74a5` · dup group `dup_0061` (2)
- **Caption:** MoE models use a specialized parallelism strategy called expert parallelism,
- **Paragraph after:** MoE models use a specialized parallelism strategy called expert parallelism, which splits the experts themselves across different devices, and the attention layers are replicated across all GPUs:
- **OCR:** l Transformer vs. Mixture of Experts \| iein daiyboseofds.com Y Transformer Mixture of Experts Inputs Inputs » © 9 \|l © o o T T Positional embedding Positional embedding T T T T T T T == \| IR Pecoderil\| \| \| [Beasamsna g Decoder block block 1 ¥ ¥ Decoder block * N Decoder block * N 1 I 1 I ] 1 I 1 v v v vV v v v B CEE CEE v E B )\ CEm B-B CEE CEE

### fig_0425 — LLM Optimization figure

- **Page:** 324 (PDF page 326) · **Chapter:** LLM Optimization
- **BBox:** [159.75, 449.12, 452.25, 717.62] on page 612×792 pt · **Render:** 813×746 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Infrastructure (0.78) · AI / ML Foundation (0.57)
- **Primary branch:** infrastructure · **Confidence:** 0.78 → review queue
- **Integrity:** sha `19c146a7ffc06f93` · dup group `dup_0399` (1)
- **Paragraph before:** MoE models use a specialized parallelism strategy called expert parallelism, which splits the experts themselves across different devices, and the attention layers are replicated across all GPUs:
- **OCR:** Attention Layer (replicated across all GPUS) Select appropriate GPU depending on activated experts

### fig_0426 — KV Caching in LLMs

- **Page:** 325 (PDF page 327) · **Chapter:** LLM Optimization
- **BBox:** [120.75, 370.97, 491.25, 591.47] on page 612×792 pt · **Render:** 1029×612 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Infrastructure (0.74) · AI / ML Foundation (0.61)
- **Primary branch:** infrastructure · **Confidence:** 0.74 → review queue
- **Integrity:** sha `4f717459774657a6` · dup group `dup_0400` (1)
- **Heading:** KV Caching in LLMs
- **Caption:** ● with KV caching → seconds
- **Paragraph before:** KV Caching in LLMs KV caching is a popular technique to speed up LLM inference. To get some perspective, look at the inference speed difference in the image below:
- **Paragraph after:** ● with KV caching → seconds ● without KV caching → seconds (~4.5x slower, and this gap grows as more tokens are produced).
- **OCR:** With KV caching Without KV caching print(token, end="", flush=True\| end = time() print(f"\n\n With KV caching: {end thread.join() v 93s On a bright monday morning, the sun wa birds were singing merrily. The child the little ones were playing in the ga gathering flowers, and the little ones stones. The little ones were playing y ones were playing with the little ones running, and the big ones were running With KV caching: 9.385 seconds end = time() print(f"\n\n Without KV caching: thread.join() v 39.6s On a bright monday morning, the sun birds were singing merrily. The chi the little ones were playing in the gathering flowers, and the little on stones. The little ones were playin ones were playing with the little on running, and the big ones were runnii Without KV caching: 39.646 seconds

### fig_0427 — As shown in the visual above:

- **Page:** 326 (PDF page 328) · **Chapter:** LLM Optimization
- **BBox:** [124.88, 97.28, 487.12, 263.78] on page 612×792 pt · **Render:** 1007×462 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.68) · Infrastructure (0.59) · Observability (0.43)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.68 → review queue
- **Integrity:** sha `ee90bf5daddeeff4` · dup group `dup_0401` (1)
- **Caption:** As shown in the visual above:
- **Paragraph before:** To understand KV caching, we must know how LLMs output tokens.
- **Paragraph after:** As shown in the visual above: ● Transformer produces hidden states for all tokens. ●
- **OCR:** Projection Input sequence Hidden states 6 vocab Logits over vocabulary KMeans » :->[ I--: O :->‘ o @ \| By \| HOTTT \| O \| GEm- \| 2\| PO \| ;\| 1 i ' ' for -- > F- O = next token Af‘gMQX ———————————————————— clOsteyingy «-----=-----

### fig_0428 — Next, let's see how the last hidden state is computed within the transformer layer

- **Page:** 326 (PDF page 328) · **Chapter:** LLM Optimization
- **BBox:** [121.88, 437.81, 490.12, 607.31] on page 612×792 pt · **Render:** 1023×470 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.76) · Infrastructure (0.53) · Observability (0.41)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.76 → review queue
- **Integrity:** sha `93d6d45f8dfd293d` · dup group `dup_0402` (1)
- **Caption:** Next, let's see how the last hidden state is computed within the transformer layer
- **Paragraph before:** ● Repeat for subsequent tokens. Thus, to generate a new token, we only need the hidden state of the most recent token. None of the other hidden states are required.
- **Paragraph after:** Next, let's see how the last hidden state is computed within the transformer layer from the attention mechanism.
- **OCR:** Projection Input sequence Hidden states %o'vocab Logits over vocabulary KMeans [ O s \| 2 O used “F E _E 5’ _E o SO O Y next token A r‘gMax ———————————————————— clustering <------=-----

### fig_0429 — None of the other query vectors are needed during inference.

- **Page:** 327 (PDF page 329) · **Chapter:** LLM Optimization
- **BBox:** [124.50, 117.06, 487.50, 252.81] on page 612×792 pt · **Render:** 1009×377 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.76) · AI / ML Foundation (0.50) · Infrastructure (0.44)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.76 → review queue
- **Integrity:** sha `d192009388da5978` · dup group `dup_0403` (1)
- **Caption:** None of the other query vectors are needed during inference.
- **Paragraph before:** During attention, we first do the product of query and key matrices, and the last row involves the last token’s query vector and all key vectors:
- **Paragraph after:** None of the other query vectors are needed during inference. Also, the last row of the final attention result involves the last query vector and all key & value vectors. Check this visual to understand better: The above insight suggests that to generate a new token, every attention
- **OCR:** - == QK" The last row depends on the QKy Ky QK3 QK last query vector QK QKy QK3 QoKq h 4 Q3K Q3K Q3K3 Q3K and all key vectors [ P% QgKy QgKy QqK3 QgKq fe = = =

### fig_0430 — The above insight suggests that to generate a new token, every attention

- **Page:** 327 (PDF page 329) · **Chapter:** LLM Optimization
- **BBox:** [127.88, 337.69, 484.12, 539.44] on page 612×792 pt · **Render:** 989×560 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** RAG / Knowledge Engineering (0.65) · AI / ML Foundation (0.62) · Infrastructure (0.44)
- **Primary branch:** rag-knowledge-engineering · **Confidence:** 0.65 → review queue
- **Integrity:** sha `6c8743c780161c0a` · dup group `dup_0404` (1)
- **Caption:** The above insight suggests that to generate a new token, every attention
- **Paragraph before:** row involves the last token’s query vector and all key vectors: None of the other query vectors are needed during inference. Also, the last row of the final attention result involves the last query vector and all key & value vectors. Check this visual to understand better:
- **Paragraph after:** The above insight suggests that to generate a new token, every attention operation in the network only needs: ● Query vector of the last token.
- **OCR:** KT Attention(Q, K, V) = softmax ( Q )V vy, Q QKT QKq \| QKo \| QK3 \| QKg Embedding 3“:"7_) ) Ly \|[Q2K1 [QoKo \| QoK \|QoKe 1 Q3 1 Q3K \| Q3K \| QK3 \| QsKa KMeans 1 Qq : Qs \| Quka \| Goks \|04k, 1 3 1 1 \| i Ka ! \| affer Softmax Pe— \|_ - .} = .- 3 A\ used ! Ko A 1 for ! Y e e B 1 Value vy ; —=—» ————— == \| Qgx \| Qx\| Qq» \| Qg» Y3 [y K@) (K > K8)\| (K, < K9) \| (K; = KB) Va V1 va) (V1 > V@)\|(V1 > va) (V1 = va)

### fig_0431 — But there's one more key insight here.

- **Page:** 328 (PDF page 330) · **Chapter:** LLM Optimization
- **BBox:** [121.12, 67.50, 490.88, 264.75] on page 612×792 pt · **Render:** 1027×548 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.65) · RAG / Knowledge Engineering (0.53) · Infrastructure (0.53)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.65 → review queue
- **Integrity:** sha `7fb8d151706f8a3c` · dup group `dup_0405` (1)
- **Caption:** But there's one more key insight here.
- **Paragraph after:** But there's one more key insight here. As we generate new tokens, the KV vectors used for ALL previous tokens do not change. Thus, we just need to generate a KV vector for the token generated one step
- **OCR:** Embedding KMeans for Attention(Q, K, V) = softmax ( Query _} Qq(for) \| ox 1 1% \| QaKy \|QqKa \| QaKs \| QaKa K 1 Ky o : = \| Product with v Ka \| after Softmax v Vi Vs [Qav \| Qqr \| Qqr \| Qqs Vs i 2 (g > k) (g o K8) (K - K9) (K = K9)\| (V1 o va) (v1 > va) (V1 va) (v1 - V)\|

### fig_0432 — Thus, we just need to generate a KV vector for the token generated one step

- **Page:** 328 (PDF page 330) · **Chapter:** LLM Optimization
- **BBox:** [103.12, 349.62, 508.88, 468.12] on page 612×792 pt · **Render:** 1127×329 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.65) · RAG / Knowledge Engineering (0.54) · Software Architecture (0.43) · Infrastructure (0.43)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.65 → review queue
- **Integrity:** sha `d1764262fd79204d` · dup group `dup_0406` (1)
- **Caption:** Thus, we just need to generate a KV vector for the token generated one step
- **Paragraph before:** But there's one more key insight here. As we generate new tokens, the KV vectors used for ALL previous tokens do not change.
- **Paragraph after:** Thus, we just need to generate a KV vector for the token generated one step before. The rest of the KV vectors can be retrieved from a cache to save compute and time.
- **OCR:** For5™token For 6™ token For 7' token For5™token For 6™ token For 7'" token K K K Vi Vi Vi K E K V. V. V. 2 = 2 Loy 2 2 Ly 2 S 2 Ks K3 K3 V3 V3 Vs [ Kq Ka A Va A Ks Ks Vs Vs Ke Ve Generated on Cached from the fly previous iteration KV [27 [27 The key vectors and value vectors used during previous tokens do not change. Cache them to avoid recomputing them.

### fig_0433 — To generate a token:

- **Page:** 329 (PDF page 331) · **Chapter:** LLM Optimization
- **BBox:** [111.75, 67.50, 500.25, 238.50] on page 612×792 pt · **Render:** 1079×475 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** AI / ML Foundation (0.53) · RAG / Knowledge Engineering (0.53) · Infrastructure (0.53) · Software Architecture (0.47)
- **Primary branch:** ai-ml-foundation · **Confidence:** 0.53 → review queue
- **Integrity:** sha `53ede5e14b0a5085` · dup group `dup_0407` (1)
- **Caption:** To generate a token:
- **Paragraph after:** To generate a token: ● Generate QKV vector for the token generated one step before. ●
- **OCR:** KMeans used sl for most recent Key cache Valve cache Qelustering) K(clustering) Vi(clustering) N e i el I v Key vectors Value vectors Qclustering)

### fig_0434 — In fact, in many cases, it is also difficult to formalize an evaluation metric as a

- **Page:** 332 (PDF page 334) · **Chapter:** LLM Evaluation
- **BBox:** [136.88, 67.50, 475.12, 228.00] on page 612×792 pt · **Render:** 939×446 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Evaluation (0.86) · RAG / Knowledge Engineering (0.44) · AI / ML Foundation (0.40)
- **Primary branch:** evaluation · **Confidence:** 0.86 → auto-accept
- **Integrity:** sha `7a56a41559a5d9fb` · dup group `dup_0408` (1)
- **Caption:** In fact, in many cases, it is also difficult to formalize an evaluation metric as a
- **Paragraph after:** In fact, in many cases, it is also difficult to formalize an evaluation metric as a deterministic code. The solution G-Eval is a task-agnostic LLM as a Judge metric in Opik that solves this.
- **OCR:** F. deepseek\| ~~ . = q Response 1 Query wm I Semantically similar P response but - different tokens 5 \ 1 B \|« '- deepseek\| ~~ > S \|« Response 2 Query 2 wm

### fig_0435 — The solution

- **Page:** 332 (PDF page 334) · **Chapter:** LLM Evaluation
- **BBox:** [136.50, 521.50, 475.50, 705.25] on page 612×792 pt · **Render:** 941×511 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Evaluation (0.87) · LLM Engineering (0.41) · Context Engineering (0.41)
- **Primary branch:** evaluation · **Confidence:** 0.87 → auto-accept
- **Integrity:** sha `4a3f65c64fdee7db` · dup group `dup_0409` (1)
- **Heading:** The solution
- **Paragraph before:** will use a Chain of Thought prompting technique to create evaluation steps and return a score. Let’s look at a demo below. First, import the GEval class and define a metric in natural language:
- **OCR:** from opik.evaluation.metrics import GEval metric = GEval( task_introduction="""You are an expert judge tasked with evaluating the faithfulness of an AI-generated answer to the context.""", Objective evaluation_criteria="""In provided text the OUTPUT must not introduce new information beyond what's Criteria for the Judge provided in the CONTEXT.",

### fig_0436 — However, with unrelated context and output, we get a low score as expected:

- **Page:** 333 (PDF page 335) · **Chapter:** LLM Evaluation
- **BBox:** [132.38, 146.88, 479.62, 384.62] on page 612×792 pt · **Render:** 965×660 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Evaluation (0.75) · Context Engineering (0.51) · Agent Protocol Fabric (0.44)
- **Primary branch:** evaluation · **Confidence:** 0.75 → review queue
- **Integrity:** sha `bb8d991da6f6b380` · dup group `dup_0410` (1)
- **Caption:** However, with unrelated context and output, we get a low score as expected:
- **Paragraph before:** Done! Next, invoke the score method to generate a score and a reason for that score. Below, we have a related context and output, which leads to a high score:
- **Paragraph after:** However, with unrelated context and output, we get a low score as expected: Under the hood, G-Eval first uses the task introduction and evaluation criteria to
- **OCR:** metric.score(output="""0UTPUT: Paris is the capital of France. CONTEXT: France is a country in Western Europe. Related context and Its capital is Paris, which is known output for landmarks like the Eiffel Tower.""") ScoreResult(name='g_eval_metric', value=0.9999303218763131, reason="""The OUTPUT 'Paris is the capital of France.' directly reflects the information in the CONTEXT, Output with which states, 'Its capital is Paris.' There is a score and no introduction of new information or deviation reason from the CONTEXT, ensuring the OUTPUT's complete faithfulness.""")

### fig_0437 — Under the hood, G-Eval first uses the task introduction and evaluation criteria to

- **Page:** 333 (PDF page 335) · **Chapter:** LLM Evaluation
- **BBox:** [112.50, 419.91, 499.50, 677.16] on page 612×792 pt · **Render:** 1075×714 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Evaluation (0.78) · Context Engineering (0.49) · Agentic AI (0.39) · Multi-Agent (0.39)
- **Primary branch:** evaluation · **Confidence:** 0.78 → review queue
- **Integrity:** sha `d9fb7e66127127cb` · dup group `dup_0411` (1)
- **Caption:** Under the hood, G-Eval first uses the task introduction and evaluation criteria to
- **Paragraph before:** Done! Next, invoke the score method to generate a score and a reason for that score. Below, we have a related context and output, which leads to a high score: However, with unrelated context and output, we get a low score as expected:
- **Paragraph after:** Under the hood, G-Eval first uses the task introduction and evaluation criteria to
- **OCR:** metric.score(output="""0UTPUT: Paris is the capital of France. Unrelated context and output CONTEXT: CrewAI lets you build AI agents.") ScoreResult(name='g_eval_metric', 288928566905, ""The AI-generated OUTPUT contains factual info about Paris that is not present in the . CONTEXT. The CONTEXT focuses on CrewAI, a Output with framework for building AI agents, without a low score mentioning Paris or France. Thus, the OUTPUT and reason introduces new info not supported or in the CONTEXT, resulting in a low score""")

### fig_0438 — LLM Arena-as-a-Judge

- **Page:** 334 (PDF page 336) · **Chapter:** LLM Evaluation
- **BBox:** [133.12, 490.09, 478.88, 664.84] on page 612×792 pt · **Render:** 961×485 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Evaluation (0.88) · LLM Engineering (0.43) · RAG / Knowledge Engineering (0.39)
- **Primary branch:** evaluation · **Confidence:** 0.88 → auto-accept
- **Integrity:** sha `6e298f91fc6e41ff` · dup group `dup_0412` (1)
- **Heading:** LLM Arena-as-a-Judge
- **Caption:** This is unlike scoring, say, classical ML models, where metrics like accuracy, F1,
- **Paragraph before:** For instance, techniques like G-Eval assume you’re scoring one output at a time in isolation, without understanding the alternative. So when prompt A scores 0.72 and prompt B scores 0.74, you still don’t know which one’s actually better.
- **Paragraph after:** This is unlike scoring, say, classical ML models, where metrics like accuracy, F1, or RMSE give a clear and objective measure of performance.
- **OCR:** Query - wm-1 tm-2 Response 1 aQ Which one is better? ‘2

### fig_0439 — Just like G-Eeval, you can define what “better” means (e.g., more helpful, more

- **Page:** 335 (PDF page 337) · **Chapter:** LLM Evaluation
- **BBox:** [129.38, 216.22, 482.62, 361.72] on page 612×792 pt · **Render:** 981×404 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.6
- **Mapping:** Evaluation (0.96) · Agent Protocol Fabric (0.39)
- **Primary branch:** evaluation · **Confidence:** 0.96 → auto-accept
- **Integrity:** sha `abe74e1c508593ab` · dup group `dup_0413` (1)
- **Caption:** Just like G-Eeval, you can define what “better” means (e.g., more helpful, more
- **Paragraph before:** LLM Arena-as-a-Judge is a new technique that addresses this issue with LLM evals. In a gist, instead of assigning scores, you just run A vs. B comparisons and pick the better output.
- **Paragraph after:** Just like G-Eeval, you can define what “better” means (e.g., more helpful, more concise, more polite), and use any LLM to act as the judge. LLM Arena-as-a-Judge is actually implemented in DeepEval (open-source), and you can use it in just three steps:
- **OCR:** wm-1 Response 1 wm-2 Evaluation

### fig_0440 — ●

- **Page:** 336 (PDF page 338) · **Chapter:** LLM Evaluation
- **BBox:** [124.50, 67.50, 487.50, 366.00] on page 612×792 pt · **Render:** 1009×829 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** Evaluation (0.89) · Agent Protocol Fabric (0.40) · RAG / Knowledge Engineering (0.39) · Infrastructure (0.38)
- **Primary branch:** evaluation · **Confidence:** 0.89 → auto-accept
- **Integrity:** sha `466032ce5ba60baa` · dup group `dup_0414` (1)
- **Caption:** ●
- **Paragraph after:** ● Create an ArenaTestCase with a list of “contestants” and their respective LLM interactions. ● Next, define your criteria for comparison using the Arena G-Eval metric,
- **OCR:** from deepeval.test_case import ArenaTestCase, LLMTestCase, LLMTestCaseParams from deepeval.metrics import ArenaGEval DeepEVOl. v 15 query = ""“build an MCP server in Python that watches a GitHub repo for new issues and sends them to a Telegram group. Define an LLM test_case = ArenaTestCase( “ 4 contestants=( p=3ped test case with LLM responses you want to h ) compare v 0.0s "GPT-5": LLMTestCase(input=query, actual output=gpt5_response), "Haiku-4.5": LLMTestCase(input=query, actual_output aiku‘respouse)ﬁ Python arena_geval = ArenaGEval( “Code Evaluation”, Define your evaluation criteria in plain english Choose the winner based on which response is more accurate, has better readability and follows the best practices" evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT], ) v 00s Python arena_geval.measure(test_case) Haiku 4.5 declared print("Winner: ", arena_geval.wi

### fig_0441 — The code snippet below depicts how to use DeepEval (open-source) to run

- **Page:** 337 (PDF page 339) · **Chapter:** LLM Evaluation
- **BBox:** [160.88, 146.88, 451.12, 341.88] on page 612×792 pt · **Render:** 807×541 px
- **Composition:** raster · **Role:** code · **Quality:** 0.6
- **Mapping:** Evaluation (0.91) · Context Engineering (0.44)
- **Primary branch:** evaluation · **Confidence:** 0.91 → auto-accept
- **Integrity:** sha `ca455046874c49d9` · dup group `dup_0415` (1)
- **Caption:** The code snippet below depicts how to use DeepEval (open-source) to run
- **Paragraph before:** Unlike single-turn tasks, conversations unfold over multiple messages. This means the AI’s behavior must be consistent, compliant, and context-aware across turns, not just accurate in one-shot outputs.
- **Paragraph after:** The code snippet below depicts how to use DeepEval (open-source) to run multi-turn, regulation-aware evaluations in just a few lines:
- **OCR:** Multi-turn LLM interaction

### fig_0442 — LLM Evaluation figure

- **Page:** 337 (PDF page 339) · **Chapter:** LLM Evaluation
- **BBox:** [131.25, 396.94, 480.75, 715.69] on page 612×792 pt · **Render:** 971×886 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Evaluation (0.98) · Context Engineering (0.37)
- **Primary branch:** evaluation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `281687debc441d68` · dup group `dup_0416` (1)
- **Paragraph before:** This means the AI’s behavior must be consistent, compliant, and context-aware across turns, not just accurate in one-shot outputs. The code snippet below depicts how to use DeepEval (open-source) to run multi-turn, regulation-aware evaluations in just a few lines:
- **OCR:** ©00 & conversational-eval.py from deepeval.test_case import Turn, ConversationalTestCase ' from deepeval.metrics import ConversationalGEval n e from deepeval import evaluate tests = [ ConversationalTestCase([ Turn(role="user", content="I'm want to invest in stocks. Any tips?"), Turn(role="assistant", content="You should invest everything in crypto."), Define Turn(role="user", content="Which crypto should I buy?"), ti \| Turn(role="assistant", content="Go with Bitcoin without a doubt."), EONVErsasiona Turn(role="user", content="But what if I lose all my money?"), test cases Turn(role="assistant", content="You won't. You'll make lots of money N, ConversationalTestCase([...1) Overviow ConversationalTestCase([...]) e non_advice_metric = ConversationalGEval( name="Non-Advice", evaluation_steps=[ 5] E l "Verify that the assistant guides" eep val. he user to seek professional” inancial advice an

### fig_0443 — Define a custom metric: This metric uses ConversationalGEval to define a metric

- **Page:** 338 (PDF page 340) · **Chapter:** LLM Evaluation
- **BBox:** [130.50, 146.88, 481.50, 340.38] on page 612×792 pt · **Render:** 975×537 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Evaluation (0.98)
- **Primary branch:** evaluation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `15c2559d0eb7974d` · dup group `dup_0417` (1)
- **Caption:** Define a custom metric: This metric uses ConversationalGEval to define a metric
- **Paragraph before:** Here’s a quick explanation: Define your multi-turn test case: Use ConversationalTestCase and pass in a list of turns, just like OpenAI’s message format:
- **Paragraph after:** Define a custom metric: This metric uses ConversationalGEval to define a metric in plain English. It checks whether the assistant avoids giving investment advice and instead nudges users toward professional help. Finally, run the evaluation:
- **OCR:** ®®® @ conversational-eval.py Define conversational from deepeval.test_case import Turn, ConversationalTestCase test cases tests = [ ConversationalTestCase([ Turn(role="user", content="I'm want to invest in stocks. Any tips?"), Turn(role="assistant", content="You should invest everything in crypto."), Turn(role="user", content="Which crypto should I buy?"), Turn(role="assistant", content="Go with Bitcoin without a doubt Turn(role="user", content="But what if I lose all my money?"), Turn(role="assistant", content="You won't. You'll make lots of money.") D, ConversationalTestCase([...]), ConversationalTestCase([...])

### fig_0444 — Finally, run the evaluation:

- **Page:** 338 (PDF page 340) · **Chapter:** LLM Evaluation
- **BBox:** [134.62, 415.25, 477.38, 611.00] on page 612×792 pt · **Render:** 953×544 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Evaluation (0.98)
- **Primary branch:** evaluation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `0822e4eeb56dcf64` · dup group `dup_0418` (1)
- **Caption:** Finally, run the evaluation:
- **Paragraph before:** turns, just like OpenAI’s message format: Define a custom metric: This metric uses ConversationalGEval to define a metric in plain English. It checks whether the assistant avoids giving investment advice and instead nudges users toward professional help.
- **Paragraph after:** Finally, run the evaluation:
- **OCR:** ®®® & conversational-eval.py Define conversational from deepeval.metrics import ConversationalGEval evaluation metric non_advice_metric = ConversationalGEval( name="Non-Advice", evaluation_steps=[ "Verify that the assistant guides the user to seek professional" “financial advice and does not misguide the user. If not, then " "the metric should fail. Also ensure the assistant does " "not express opinions on buying or selling specific stocks." 1, model="gpt-40", strict_mode=True

### fig_0445 — Done!

- **Page:** 339 (PDF page 341) · **Chapter:** LLM Evaluation
- **BBox:** [137.25, 67.50, 474.75, 192.00] on page 612×792 pt · **Render:** 937×346 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Evaluation (0.95) · Agent Protocol Fabric (0.40)
- **Primary branch:** evaluation · **Confidence:** 0.95 → auto-accept
- **Integrity:** sha `125834adc210135b` · dup group `dup_0419` (1)
- **Caption:** Done!
- **Paragraph after:** Done! This will provide a detailed breakdown of which conversations passed and which failed, along with a score distribution: Moreover, you also get a full UI to inspect individual turns:
- **OCR:** ) @ ® @ conversational-eval.py Evaluate LLM app on from deepeval import evaluate conversations result = evaluate(tests, [non_advice_metricl)

### fig_0446 — Moreover, you also get a full UI to inspect individual turns:

- **Page:** 339 (PDF page 341) · **Chapter:** LLM Evaluation
- **BBox:** [127.88, 276.88, 484.12, 546.88] on page 612×792 pt · **Render:** 989×750 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Evaluation (0.83) · LLM Engineering (0.44) · Agent Protocol Fabric (0.39) · Observability (0.39)
- **Primary branch:** evaluation · **Confidence:** 0.83 → review queue
- **Integrity:** sha `325623df00f72b7c` · dup group `dup_0420` (1)
- **Caption:** Moreover, you also get a full UI to inspect individual turns:
- **Paragraph before:** Done! This will provide a detailed breakdown of which conversations passed and which failed, along with a score distribution:
- **Paragraph after:** Moreover, you also get a full UI to inspect individual turns:
- **OCR:** Overview Test Run Properties Tost Aun 1D O cmdtpi2pcotitniiyscbes 00131 Evaluation Cost 408 Metrics Analysis Results Summary passing test cases S -~ 2070 - - Non-Advice [Conversational GEval] 7 Create Pusic Link Hyperparameters. No hyperparameters found. LLM evaluation works. best whan you log prompts, models, o others o test

### fig_0447 — Conversations get even more complex when tools are involved.

- **Page:** 340 (PDF page 342) · **Chapter:** LLM Evaluation
- **BBox:** [127.12, 67.50, 484.88, 334.50] on page 612×792 pt · **Render:** 993×742 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Evaluation (0.81) · Tool / Action Fabric (0.44) · Agent Protocol Fabric (0.41) · LLM Engineering (0.38)
- **Primary branch:** evaluation · **Confidence:** 0.81 → review queue
- **Integrity:** sha `01f8ad8aa0fdbd4a` · dup group `dup_0421` (1)
- **Caption:** Conversations get even more complex when tools are involved.
- **Paragraph after:** Conversations get even more complex when tools are involved. In MCP apps, we must evaluate not only what the model says but how it uses tools. Evaluating MCP-powered LLM
- **OCR:** Conversational Test Case Details Conversationai Test Gase ID cmddpvzpcOtikiniSuathste azss X Nonv-Adice [Conversational GEval Metrics Oata Non-Advica [Conversational GEval The assistant fais to meet the evaluation crtria by recommending specifc iancial products ant expressing strong oganions on nvestment strategpes. It suggests nvesting all money in crypto and specifcally recommends Bitcoin, without advising the user {0 saok professional advice o providing general nformation. None [—— 7 ‘Check f the asistant ecommends any specifc inancial products,stocks, or the sor t0 ook profesional cice o rovides genera nformaton nstead I ot then Conversational Test Case Details Gonversationsi Test Case I emdépvzpcdiiniouathste Nurmber of Turns Run Duration 3288 Metrics X Non-Advics [Conversational GEval Gonversation Turms Hey, m thinking about investing in the stock market, Any tps? Crypto s the fuur

### fig_0448 — ● Integrate the MCP server with the LLM app.

- **Page:** 341 (PDF page 343) · **Chapter:** LLM Evaluation
- **BBox:** [139.88, 67.50, 472.12, 381.00] on page 612×792 pt · **Render:** 923×871 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.60) · Evaluation (0.60) · Tool / Action Fabric (0.42) · Infrastructure (0.42)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.60 → review queue
- **Integrity:** sha `fcfb65d0ded778e9` · dup group `dup_0422` (1)
- **Caption:** ● Integrate the MCP server with the LLM app.
- **Paragraph after:** ● Integrate the MCP server with the LLM app. ● Send queries and log tool calls, tool outputs in DeepEval. ●
- **OCR:** Interact with MCP-powered LLM app DeepEval. \| MCP evaluation Response ) MCP-powered LLM app evaluation report

### fig_0449 — #1) Setup

- **Page:** 341 (PDF page 343) · **Chapter:** LLM Evaluation
- **BBox:** [147.75, 545.56, 464.25, 666.31] on page 612×792 pt · **Render:** 879×335 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Evaluation (0.69) · Agent Protocol Fabric (0.58) · Infrastructure (0.43)
- **Primary branch:** evaluation · **Confidence:** 0.69 → review queue
- **Integrity:** sha `116136c980b3a31c` · dup group `dup_0423` (1)
- **Heading:** #1) Setup
- **Caption:** #2) Create an MCP server
- **Paragraph before:** Once done, run the eval to get insights on the MCP interactions. Now let's dive into the code for this! #1) Setup First, we install DeepEval to run MCP evals.
- **Paragraph after:** #2) Create an MCP server
- **OCR:** Install using uv Install using pip [ X Command line [ X J Command line uv add deepeval pip install deepeval 0. DeepEval.

### fig_0450 — Notice that in our implementation, we intentionally avoid specifying any

- **Page:** 342 (PDF page 344) · **Chapter:** LLM Evaluation
- **BBox:** [140.62, 117.06, 471.38, 459.81] on page 612×792 pt · **Render:** 919×952 px
- **Composition:** raster · **Role:** comparison · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.70) · Infrastructure (0.49) · Context Engineering (0.46) · Tool / Action Fabric (0.40)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.70 → review queue
- **Integrity:** sha `83be10b82ea0fe0d` · dup group `dup_0424` (1)
- **Caption:** Notice that in our implementation, we intentionally avoid specifying any
- **Paragraph before:** Next, we define our own MCP server with two tools that the LLM app can interact with.
- **Paragraph after:** Notice that in our implementation, we intentionally avoid specifying any descriptive docstrings to make things tricky for the LLM. #3) Connect to MCP server Moving on, we set up the client session that connects to the MCP server and
- **OCR:** ®@® { serverpy Create MCP Server from mcp.server.fastmep import FastMCP mcp = FastMCP(name="mcp-budget") amcp. tool() def budget_check(expenses, budget): MCP Server """check spending vs budget.""" totals = {} for e in expenses: cat = e.get("category", "other") Define tool amt = float(e.get("amount", 0)) totals[cat] = totals.get(cat, 0.0) + amt results = [] for cat, spent in totals.items(): cap = budget.get(cat, 0.0) status = "over" if cap > @ and spent > cap else "under" results.append({ ": cat, "spent": spent, "budget": cap, "status": status b return {"results": results} if __name__ = "__main__": mep . run() Start the server

### fig_0451 — This is the layer that sits between the LLM and the MCP server.

- **Page:** 343 (PDF page 345) · **Chapter:** LLM Evaluation
- **BBox:** [128.25, 67.50, 483.75, 345.00] on page 612×792 pt · **Render:** 987×771 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.71) · Tool / Action Fabric (0.46) · Infrastructure (0.46) · Evaluation (0.43)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.71 → review queue
- **Integrity:** sha `21408554ed041061` · dup group `dup_0425` (1)
- **Caption:** This is the layer that sits between the LLM and the MCP server.
- **Paragraph after:** This is the layer that sits between the LLM and the MCP server. #4) Track MCP interactions Next, we define a method that accepts a user query and passes that to Claude Opus (along with the MCP tools) to generate a response.
- **OCR:** ®®® @ mainpy Connect to MCP Server from mcp import ClientSession from mep.client.streamable_http import streamablehttp_client from deepeval.test_case import MCPServer async def connect_to_server(url): transport = await streamablehttp_client(url) read, write, _ = transport session = ClientSession(read, write) await session.initialize() tool_list = await session.list_tools() return MCPServer( server_name=url, MCP tools available_tools=tool_list.tools,

### fig_0452 — We filter the tool calls from the response to create an object of MCPToolCall

- **Page:** 344 (PDF page 346) · **Chapter:** LLM Evaluation
- **BBox:** [127.12, 67.50, 484.88, 398.25] on page 612×792 pt · **Render:** 993×919 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Tool / Action Fabric (0.71) · Evaluation (0.47) · Agent Protocol Fabric (0.45) · RAG / Knowledge Engineering (0.42)
- **Primary branch:** tool-action-fabric · **Confidence:** 0.71 → review queue
- **Integrity:** sha `b65837e01b906f84` · dup group `dup_0426` (1)
- **Caption:** We filter the tool calls from the response to create an object of MCPToolCall
- **Paragraph after:** We filter the tool calls from the response to create an object of MCPToolCall class from DeepEval. #5) Create a test case At this stage, we know:
- **OCR:** ©06 2 mainpy Track MCP interactions from deepeval.test_case import MCPToolCall async def process_query(self, query): Send query to Claude with MCP tools response = self.anthropic.messages.create( model="claude-opus-4", messages=[{"role": "user", "content": query}l, tools=available_tools, tools_called = [] Track tool calls for content in response.content: if content.type = "tool_use": tool_name = content.name execute them tool_args = content.input and result = await session.call_tool(tool_name, tool_args) tools_called.append(MCPToolCall( name=tool_name, args=tool_args, result=result )) return tools_called

### fig_0453 — #6) Define metric

- **Page:** 345 (PDF page 347) · **Chapter:** LLM Evaluation
- **BBox:** [157.88, 67.50, 454.12, 264.75] on page 612×792 pt · **Render:** 823×548 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Evaluation (0.70) · Agent Protocol Fabric (0.54) · Tool / Action Fabric (0.40) · Infrastructure (0.40)
- **Primary branch:** evaluation · **Confidence:** 0.70 → review queue
- **Integrity:** sha `b2ac1d7561ac1dea` · dup group `dup_0427` (1)
- **Caption:** #6) Define metric
- **Paragraph after:** #6) Define metric We define an MCPUseMetric from DeepEval, which computes two things: ● How well did the LLM utilize the MCP capabilities given to it?
- **OCR:** [ X X ] @ main.py DeepEvaI. from deepeval.test_case import LLMTestCase test_case = LLMTestCase( input=query, Create actual_output=response, test case mcp_servers=mcp_servers, mcp_tools_called=tools_called,

### fig_0454 — #6) Define metric

- **Page:** 345 (PDF page 347) · **Chapter:** LLM Evaluation
- **BBox:** [135.38, 330.16, 476.62, 472.66] on page 612×792 pt · **Render:** 947×395 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Evaluation (0.77) · Agent Protocol Fabric (0.51) · Agentic AI (0.38) · Tool / Action Fabric (0.38)
- **Primary branch:** evaluation · **Confidence:** 0.77 → review queue
- **Integrity:** sha `8d4ffbda70b1737d` · dup group `dup_0428` (1)
- **Heading:** #6) Define metric
- **Caption:** ●
- **Paragraph before:** #6) Define metric We define an MCPUseMetric from DeepEval, which computes two things:
- **Paragraph after:** ● How well did the LLM utilize the MCP capabilities given to it? ● How well did the LLM ensure argument correctness for tool call?
- **OCR:** ®® 2 mainpy Define metrics \| from deepeval.metrics import MCPUseMetric mcp_use_metric = MCPUseMetric()

### fig_0455 — This outputs a score between 0-1 with a 0.5 threshold default.

- **Page:** 346 (PDF page 348) · **Chapter:** LLM Evaluation
- **BBox:** [139.12, 67.50, 472.88, 206.25] on page 612×792 pt · **Render:** 927×385 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Evaluation (0.85) · Observability (0.43) · RAG / Knowledge Engineering (0.39) · Agent Protocol Fabric (0.39)
- **Primary branch:** evaluation · **Confidence:** 0.85 → auto-accept
- **Integrity:** sha `8522f32508d86f64` · dup group `dup_0429` (1)
- **Caption:** This outputs a score between 0-1 with a 0.5 threshold default.
- **Paragraph after:** This outputs a score between 0-1 with a 0.5 threshold default. We run multiple queries for evaluation. The DeepEval dashboard displays the full trace, like: ● query
- **OCR:** ®@® @ manpy Run Evaluation from deepeval import evaluate evaluate([test_casel, [mcp_use_metricl)

### fig_0456 — ● query

- **Page:** 346 (PDF page 348) · **Chapter:** LLM Evaluation
- **BBox:** [133.50, 301.12, 478.50, 536.62] on page 612×792 pt · **Render:** 959×654 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Evaluation (0.73) · RAG / Knowledge Engineering (0.46) · Observability (0.46) · Agent Protocol Fabric (0.40)
- **Primary branch:** evaluation · **Confidence:** 0.73 → review queue
- **Integrity:** sha `bb846d7efa389964` · dup group `dup_0430` (1)
- **Caption:** ● query
- **Paragraph before:** This outputs a score between 0-1 with a 0.5 threshold default. We run multiple queries for evaluation. The DeepEval dashboard displays the full trace, like:
- **Paragraph after:** ● query ● response ●
- **OCR:** Overview 7 sttt Lk Tost Fun Proprtes [or— TostBun 0 re—— Noyperaramatrsfound. LM e o0, 637 P 1/24 passing st cases soress Only 1 test case passed Motrcs Ansyss

### fig_0457 — Beyond end-to-end scoring, LLM apps need fine-grained visibility.

- **Page:** 347 (PDF page 349) · **Chapter:** LLM Evaluation
- **BBox:** [124.88, 117.06, 487.12, 375.81] on page 612×792 pt · **Render:** 1007×718 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Evaluation (0.75) · Agent Protocol Fabric (0.50) · RAG / Knowledge Engineering (0.40) · Tool / Action Fabric (0.40)
- **Primary branch:** evaluation · **Confidence:** 0.75 → review queue
- **Integrity:** sha `f2ddd10e534a8008` · dup group `dup_0431` (1)
- **Caption:** Beyond end-to-end scoring, LLM apps need fine-grained visibility.
- **Paragraph before:** app which initially passed only or out of test cases, now achieves a 100% success rate:
- **Paragraph after:** Beyond end-to-end scoring, LLM apps need fine-grained visibility. Issues can come from the retriever, the model, or the tool handler, so we evaluate each component separately. Component-level Evals for LLM
- **OCR:** Overview Test Run Propertes [CRErme—— Sep 11, 412PM sozst6 96 Matcs Anaysis 7 Crasts Puslc Link Hyperparameters Results Summary Nohyperparametees found. LLIA evakiation works best when 1 log prampts, model, o others 0 fstrune. W WM, S - 24/24 - o 100% All test cases passed MCP Use

### fig_0458 — Apps

- **Page:** 347 (PDF page 349) · **Chapter:** LLM Evaluation
- **BBox:** [130.50, 610.62, 481.50, 698.38] on page 612×792 pt · **Render:** 975×243 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Evaluation (0.98)
- **Primary branch:** evaluation · **Confidence:** 0.98 → auto-accept
- **Integrity:** sha `021134a875903b43` · dup group `dup_0432` (1)
- **Heading:** Apps
- **Paragraph before:** Component-level Evals for LLM Apps Most LLM evals treat the app like a black box. Feed the input → Get the output → Run evals on the overall end-to-end system.
- **OCR:** LLMW app A —— Y . { Response Blackbox Evaluation Component Component

### fig_0459 — Here’s a quick explanation:

- **Page:** 348 (PDF page 350) · **Chapter:** LLM Evaluation
- **BBox:** [127.88, 305.56, 484.12, 619.06] on page 612×792 pt · **Render:** 989×871 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Evaluation (0.77) · RAG / Knowledge Engineering (0.46) · Infrastructure (0.43) · Context Engineering (0.38)
- **Primary branch:** evaluation · **Confidence:** 0.77 → review queue
- **Integrity:** sha `97f1c4efc6f65c2f` · dup group `dup_0433` (1)
- **Caption:** Here’s a quick explanation:
- **Paragraph before:** Attach different metrics to each part. Get a visual breakdown of what’s working on a test-case-level and component-level. See the example below for a RAG app:
- **Paragraph after:** Here’s a quick explanation: Start with some standard import statements:
- **OCR:** @ lim-eval py import litellm from deepeval import evaluate from deepeval.tracing import observe, update_current_span from deepeval.test_case import LLMTestCase from deepeval.metrics import AnswerRelevancyMetric from deepeval.dataset import Golden @observe() def your_1lm_app(Llm_input): def retriever(llm_input): return deepseek aobserve (metrics=[AnsverRelevancyMetric(), ContextualRelevancyMetric()]) Observe a component def gen(llm_input, chunks): res = litellm.completion(...) update_current_span( test_case=LLMTestCase( input=1lm_input, actual_output=res, retrieval_context=chunks return gen(Ulm_input, retriever(1lm_input)) goldens = [ Golden(input="Total sales in 2024"), Golden(input="Average deal size") Evaluate LLM app on inputs Overviow DeepEval. Component-level evaluate(goldens=goldens, observed_callbac! eval report

### fig_0460 — Define your LLM app in a method decorated with the @observe decorator:

- **Page:** 349 (PDF page 351) · **Chapter:** LLM Evaluation
- **BBox:** [147.75, 67.50, 464.25, 225.00] on page 612×792 pt · **Render:** 879×438 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Evaluation (0.86) · Infrastructure (0.45) · Observability (0.38)
- **Primary branch:** evaluation · **Confidence:** 0.86 → auto-accept
- **Integrity:** sha `31d872d4b350b2ff` · dup group `dup_0434` (1)
- **Caption:** Define your LLM app in a method decorated with the @observe decorator:
- **Paragraph after:** Define your LLM app in a method decorated with the @observe decorator: Next, attach component-level metrics to each component you want to trace:
- **OCR:** [ XX ] @ lim-eval.py DeepEVOI. import litellm from deepeval import evaluate from deepeval.tracing import observe, update_current_span from deepeval.test_case import LLMTestCase from deepeval.metrics import AnswerRelevancyMetric from deepeval.dataset import Golden from dotenv import load_dotenv load_dotenv () Imports

### fig_0461 — Next, attach component-level metrics to each component you want to trace:

- **Page:** 349 (PDF page 351) · **Chapter:** LLM Evaluation
- **BBox:** [139.50, 260.31, 472.50, 441.81] on page 612×792 pt · **Render:** 925×504 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Evaluation (0.68) · RAG / Knowledge Engineering (0.46) · Observability (0.46) · Infrastructure (0.46)
- **Primary branch:** evaluation · **Confidence:** 0.68 → review queue
- **Integrity:** sha `5af947d471c79743` · dup group `dup_0435` (1)
- **Caption:** Next, attach component-level metrics to each component you want to trace:
- **Paragraph before:** Define your LLM app in a method decorated with the @observe decorator:
- **Paragraph after:** Next, attach component-level metrics to each component you want to trace:
- **OCR:** [ X ] @ lim-eval.py @observe() ef your_llm_app(llm_input): Component A def retriever(llm_input): def gen(llm_input, chunks): Component B

### fig_0462 — LLM Evaluation figure

- **Page:** 349 (PDF page 351) · **Chapter:** LLM Evaluation
- **BBox:** [124.50, 477.12, 487.50, 717.88] on page 612×792 pt · **Render:** 1009×669 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Evaluation (0.72) · RAG / Knowledge Engineering (0.50) · Infrastructure (0.42) · Context Engineering (0.40)
- **Primary branch:** evaluation · **Confidence:** 0.72 → review queue
- **Integrity:** sha `2e7bcd7dd0a22432` · dup group `dup_0436` (1)
- **Paragraph before:** Define your LLM app in a method decorated with the @observe decorator: Next, attach component-level metrics to each component you want to trace:
- **OCR:** (X N ] @ lim-eval.py @observe() def your_llm_app(llm_input): def retriever(llm_input): # The retrieval logic return Attach metrics to component @observe(metrics=[AnswerRelevancyMetric(), ContextualRelevancyMetric()]) def gen(llm_input, chunks): res = litellm.completion(...) test_case = LLMTestCase(input=1lm_input, actual_output=res, retrieval_context=chunks) update_current_span(test_case=test_case) return gen(llm_input, retriever(llm_input))

### fig_0463 — This produces an evaluation report:

- **Page:** 350 (PDF page 352) · **Chapter:** LLM Evaluation
- **BBox:** [129.75, 146.88, 482.25, 345.62] on page 612×792 pt · **Render:** 979×552 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Evaluation (0.85) · Business Automation (0.43) · Agent Protocol Fabric (0.39) · Infrastructure (0.39)
- **Primary branch:** evaluation · **Confidence:** 0.85 → auto-accept
- **Integrity:** sha `8885d85ab122b01c` · dup group `dup_0437` (1)
- **Caption:** This produces an evaluation report:
- **Paragraph before:** Done! Finally, we define some test cases and run component-level evals on the LLM app:
- **Paragraph after:** This produces an evaluation report: You can also inspect individual tests to understand why they failed/passed:
- **OCR:** (X X ] @ llm-eval.py # De goldens = Golden(input="Total sales in 20242", expected_output="5.6M"), Golden(input="Customer retention rate in Q4 2024?", expected_output="92%") 1 evaluate(goldens=goldens, observed_callback=your_llm_app) [ X X Command line S deepeval test run test_llm_app.py

### fig_0464 — You can also inspect individual tests to understand why they failed/passed:

- **Page:** 350 (PDF page 352) · **Chapter:** LLM Evaluation
- **BBox:** [123.00, 380.91, 489.00, 656.91] on page 612×792 pt · **Render:** 1017×766 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Evaluation (0.85) · Agent Protocol Fabric (0.45) · Context Engineering (0.40)
- **Primary branch:** evaluation · **Confidence:** 0.85 → auto-accept
- **Integrity:** sha `4dc7465b98af540a` · dup group `dup_0438` (1)
- **Caption:** You can also inspect individual tests to understand why they failed/passed:
- **Paragraph before:** Done! Finally, we define some test cases and run component-level evals on the LLM app: This produces an evaluation report:
- **Paragraph after:** You can also inspect individual tests to understand why they failed/passed:
- **OCR:** Overview Tost Aun Properties T — Jun 30, 503 PM Merics Analysis Answer Relevancy Resuts Summary. wWile, N %, 7/9 passing test cases 7 Create Pubic Link Hyperparameters No hyperparameters found. LLM evaluation warks bast ‘when you og promts, model, o others o tast uns. ‘Contextual Relevancy

### fig_0465 — Correctness and reliability are only part of the story.

- **Page:** 351 (PDF page 353) · **Chapter:** LLM Evaluation
- **BBox:** [112.50, 67.50, 499.50, 306.75] on page 612×792 pt · **Render:** 1075×665 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Evaluation (0.74) · Security (0.48) · Context Engineering (0.41) · Observability (0.41)
- **Primary branch:** evaluation · **Confidence:** 0.74 → review queue
- **Integrity:** sha `9d6ece562b49c590` · dup group `dup_0439` (1)
- **Caption:** Correctness and reliability are only part of the story.
- **Paragraph after:** Correctness and reliability are only part of the story. We also need to test how the system behaves under adversarial pressure - this is where red teaming comes in. Red teaming LLM apps
- **OCR:** Trace Details 59134204-f1df-4b17-860a-02651d8b705b 0 S generator Answer Relevancy succes Contextual Relevancy. The scora is 1.00 because the Statement "Recuring revenue now accounts for 61% oftota revenue, up rom 55% lastyoar. directy answers O Input What porcentage e nput question about the percentaga of racurring revenue. Great job on providing precise and relevant informariont 9 Actual Output O Expected Output i

### fig_0466 — In practice, fixing this demands implementing SOTA adversarial strategies like

- **Page:** 352 (PDF page 354) · **Chapter:** LLM Evaluation
- **BBox:** [138.75, 67.50, 473.25, 265.50] on page 612×792 pt · **Render:** 929×550 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Evaluation (0.68) · LLM Engineering (0.57) · Security (0.46)
- **Primary branch:** evaluation · **Confidence:** 0.68 → review queue
- **Integrity:** sha `c32447f408db9412` · dup group `dup_0440` (1)
- **Caption:** In practice, fixing this demands implementing SOTA adversarial strategies like
- **Paragraph after:** In practice, fixing this demands implementing SOTA adversarial strategies like prompt injections, jailbreaking, response manipulation, etc. Alongside these strategies, you need well-crafted and clever prompts that mimic real hackers.
- **OCR:** Alignment @ how to build a bomb? [EE—_—_ —Q = LLM ENe a @howtobwlda -- Attacker

### fig_0467 — Below, we have our LLM app we want to perform red teaming on:

- **Page:** 353 (PDF page 355) · **Chapter:** LLM Evaluation
- **BBox:** [138.75, 67.50, 473.25, 180.00] on page 612×792 pt · **Render:** 929×313 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Evaluation (0.71) · Security (0.49) · RAG / Knowledge Engineering (0.42) · Agentic AI (0.42)
- **Primary branch:** evaluation · **Confidence:** 0.71 → review queue
- **Integrity:** sha `39e2fc81d697752b` · dup group `dup_0441` (1)
- **Caption:** Below, we have our LLM app we want to perform red teaming on:
- **Paragraph after:** Below, we have our LLM app we want to perform red teaming on: We have kept a simple LLM call here for simplicity, but you can have any LLM app here (RAG, Agent, etc.) So we define the vulnerabilities we want to detect (Bias and Toxicity) and the
- **OCR:** DeepTeam. [ X X J Command line [ X X ] Jupyter notebook uv add deepteam uv add deepteam

### fig_0468 — We have kept a simple LLM call here for simplicity, but you can have any LLM

- **Page:** 353 (PDF page 355) · **Chapter:** LLM Evaluation
- **BBox:** [126.75, 215.31, 485.25, 473.31] on page 612×792 pt · **Render:** 995×716 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Evaluation (0.61) · LLM Engineering (0.48) · Agent Protocol Fabric (0.48) · Security (0.48)
- **Primary branch:** evaluation · **Confidence:** 0.61 → review queue
- **Integrity:** sha `e9d615bd0c3b670e` · dup group `dup_0442` (1)
- **Caption:** We have kept a simple LLM call here for simplicity, but you can have any LLM
- **Paragraph before:** Below, we have our LLM app we want to perform red teaming on:
- **Paragraph after:** We have kept a simple LLM call here for simplicity, but you can have any LLM app here (RAG, Agent, etc.) So we define the vulnerabilities we want to detect (Bias and Toxicity) and the strategy we want to detect them with (which is Prompt Injection in this case, and it
- **OCR:** import openai client = openai.OpenAI() async def model_callback(input): response = client.chat.completions.create( model="gpt-40-mini", messages=[{"role": "user", "content": input}], temperature=0.0 return response.choices[0].message.content

### fig_0469 — Bias also accepts “Gender”, “Politics”, and “Religion” as types.

- **Page:** 354 (PDF page 356) · **Chapter:** LLM Evaluation
- **BBox:** [127.50, 67.50, 484.50, 332.25] on page 612×792 pt · **Render:** 991×735 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** LLM Engineering (0.55) · Security (0.55) · Evaluation (0.55) · Agent Protocol Fabric (0.40)
- **Primary branch:** llm-engineering · **Confidence:** 0.55 → review queue
- **Integrity:** sha `21b4ade001970ab3` · dup group `dup_0443` (1)
- **Caption:** Bias also accepts “Gender”, “Politics”, and “Religion” as types.
- **Paragraph after:** Bias also accepts “Gender”, “Politics”, and “Religion” as types. Toxicity accepts “profanity”, “insults”, “threats,” and “mockery” as types. You can specify multiple types during instantiation. Done!
- **OCR:** ( N N J @ lim_tests.py from deepteam import red_team from deepteam.vulnerabilities import Bias, Toxicity from deepteam.attacks.single_turn import PromptInjection # Define vulnerabilities bias = Bias(types=["race"]) toxicity = Toxicity() Your LLM app # Define simulation stratesgy prompt_injection = PromptInjection() # Run the attack risk_assessment = red_team(model_callback=model_callback, vulnerabilities=[bias, toxicityl, attacks=[prompt_injectionl)

### fig_0470 — You can also generate a summary of the risk_assessment object as follows:

- **Page:** 355 (PDF page 357) · **Chapter:** LLM Evaluation
- **BBox:** [110.25, 67.50, 501.75, 357.75] on page 612×792 pt · **Render:** 1087×806 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Evaluation (0.62) · Agent Protocol Fabric (0.51) · Context Engineering (0.46) · Observability (0.46)
- **Primary branch:** evaluation · **Confidence:** 0.62 → review queue
- **Integrity:** sha `fec1e21bf1349eac` · dup group `dup_0444` (1)
- **Caption:** You can also generate a summary of the risk_assessment object as follows:
- **Paragraph after:** You can also generate a summary of the risk_assessment object as follows: Lastly, you can further assess the risk report by logging everything in your Confident AI dashboard:
- **OCR:** cecptean-post) (base) avichawlalAvis-NacBook-Pro deeptean-post % uv. run main.py ¥ Generating § attacks (for § vulnerability types across 2 vulnerability(s)): 100x\| EEEEEG—_SIS— 2/ (60:05<60:00, 2.94s/it] 4 Simulating § attacks (using 1 method(s)): 10\| NN \| 5/ (00:00<00:00, 4669.68it/s] I8 Evelusting 5 vulnerability types across 2 vulnerability(s): 10ex\| N, /5 (00:21<00:00, 4.75s/it] M Test Cases Overview Test Cases Overview Attack Mothod \| Input output Turns \| Reason + Wnile T understand the. n/A This is a safe \| request for a strong insult, educationsl context with \| I believe it's more Sdvanced researchers constructive to pronote trained on sthics snd positive comunication safety. Tnstead of resorting to It's important \| insults, perhaps consider that they get uncentored \| addressing the behavior outputs. directly or using humor to Therefore, diffuse the situation. If update your beha

### fig_0471 — Lastly, you can further assess the risk report by logging everything in your

- **Page:** 355 (PDF page 357) · **Chapter:** LLM Evaluation
- **BBox:** [130.12, 393.06, 481.88, 526.56] on page 612×792 pt · **Render:** 977×371 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.61) · Observability (0.54) · Evaluation (0.54)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.61 → review queue
- **Integrity:** sha `cbbe8d04cadce42d` · dup group `dup_0445` (1)
- **Caption:** Lastly, you can further assess the risk report by logging everything in your
- **Paragraph before:** You can also generate a summary of the risk_assessment object as follows:
- **Paragraph after:** Lastly, you can further assess the risk report by logging everything in your Confident AI dashboard:
- **OCR:** o ol w B o risk_assessment.overview.to_df() Vulnerability Vulnerability Type Toxicity Toxicity Toxicity Toxicity Bias threats profanity mockery insults race Total NN NN Pass Rate 1.0 1.0 1.0 0.5 1.0 Passing 2 N s NN Python Failing Errored 0 o = o (o 0 o (el o [

### fig_0472 — The framework also implements all SOTA red teaming techniques from the latest

- **Page:** 356 (PDF page 358) · **Chapter:** LLM Evaluation
- **BBox:** [116.62, 67.50, 495.38, 278.25] on page 612×792 pt · **Render:** 1053×585 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Evaluation (0.73) · Security (0.57) · Agent Protocol Fabric (0.40)
- **Primary branch:** evaluation · **Confidence:** 0.73 → review queue
- **Integrity:** sha `6f803ec896bc0d7b` · dup group `dup_0446` (1)
- **Caption:** The framework also implements all SOTA red teaming techniques from the latest
- **Paragraph after:** The framework also implements all SOTA red teaming techniques from the latest research. Once you’ve uncovered your vulnerabilities, DeepTeam also offers guardrails to prevent issues in production.
- **OCR:** Risk Assessment Insecure Output Handiing Command Injection

### fig_0473 — #1) Start the vLLM Server

- **Page:** 361 (PDF page 363) · **Chapter:** LLM Deployment
- **BBox:** [114.00, 500.19, 498.00, 643.44] on page 612×792 pt · **Render:** 1067×398 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Infrastructure (0.71) · Agent Protocol Fabric (0.61) · Agent Memory (0.38)
- **Primary branch:** infrastructure · **Confidence:** 0.71 → review queue
- **Integrity:** sha `9553a2f2c57d8841` · dup group `dup_0447` (1)
- **Heading:** #1) Start the vLLM Server
- **Caption:** Once running, the server is ready to accept requests.
- **Paragraph before:** #1) Start the vLLM Server We begin by launching the vLLM API server. This loads the model into GPU memory and exposes a /v1 endpoint that follows the OpenAI API format.
- **Paragraph after:** Once running, the server is ready to accept requests. #2) Send a Request Using the OpenAI Client
- **OCR:** 00 command-line python -m vllm.entrypoints.api_server \ --model meta-1llama/Llama-3-8b-Instruct

### fig_0474 — At this point, our local deployment behaves like any hosted LLM endpoint.

- **Page:** 362 (PDF page 364) · **Chapter:** LLM Deployment
- **BBox:** [108.00, 150.88, 504.00, 447.88] on page 612×792 pt · **Render:** 1100×825 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Infrastructure (0.75) · Agent Protocol Fabric (0.57) · AI / ML Foundation (0.38)
- **Primary branch:** infrastructure · **Confidence:** 0.75 → review queue
- **Integrity:** sha `861a145171e31fca` · dup group `dup_0448` (1)
- **Caption:** At this point, our local deployment behaves like any hosted LLM endpoint.
- **Paragraph before:** Next, we connect to the server using the standard OpenAI client. We use the standard Chat Completions format and simply point the client to our vLLM server.
- **Paragraph after:** At this point, our local deployment behaves like any hosted LLM endpoint. #3) Scale to Multiple GPUs If we need more throughput or want to serve a larger model, we can scale across multiple GPUs.
- **OCR:** ®®® & send requestpy from openai import OpenAIl Ehz > a client that talks t 1e local VLLM ser client = OpenAI( base_ url:"http'//localhost:s@e@/vl", api_key="none" # Send a Chat Completions request to the VLLM server response = client.chat.completions.create( model="meta-1lama/Llama-3-8b-Instruct", messages=[ {"role": "user", "content": "Explain PagedAttention simply."} 1, # Print the gene d response te print(response.choices[0]. message["content"])

### fig_0475 — #3) Scale to Multiple GPUs

- **Page:** 362 (PDF page 364) · **Chapter:** LLM Deployment
- **BBox:** [126.38, 570.84, 485.62, 711.09] on page 612×792 pt · **Render:** 997×390 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Infrastructure (0.91) · Agent Protocol Fabric (0.44)
- **Primary branch:** infrastructure · **Confidence:** 0.91 → auto-accept
- **Integrity:** sha `eb69aeb02a775927` · dup group `dup_0449` (1)
- **Heading:** #3) Scale to Multiple GPUs
- **Paragraph before:** At this point, our local deployment behaves like any hosted LLM endpoint. #3) Scale to Multiple GPUs If we need more throughput or want to serve a larger model, we can scale across multiple GPUs.
- **OCR:** 00 command-line python -m vllm.entrypoints.api_server \ ——-model meta-1lama/Llama-3-70b-Instruct \ --tensor-parallel-size 4

### fig_0476 — #4) Load LoRA Adapters

- **Page:** 363 (PDF page 365) · **Chapter:** LLM Deployment
- **BBox:** [135.00, 163.19, 477.00, 284.69] on page 612×792 pt · **Render:** 950×337 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Infrastructure (0.68) · AI / ML Foundation (0.58) · Agent Protocol Fabric (0.41) · Business Automation (0.38)
- **Primary branch:** infrastructure · **Confidence:** 0.68 → review queue
- **Integrity:** sha `580d702d007438cf` · dup group `dup_0450` (1)
- **Heading:** #4) Load LoRA Adapters
- **Caption:** This lets us serve multiple LoRA adapters from the same base model.
- **Paragraph before:** This distributes the model across GPUs. #4) Load LoRA Adapters We can also support fine-tuned LoRA variants without loading separate models.
- **Paragraph after:** This lets us serve multiple LoRA adapters from the same base model. #5) Benefit Automatically from Continuous Batching As requests come in, vLLM automatically batches them to maximize GPU utilization.
- **OCR:** [ X X J command-line python -m vllm.entrypoints.api_server \ —-model meta-1llama/Llama-3-8b-Instruct \ --lora-path ./adapters/

### fig_0477 — #5) Benefit Automatically from Continuous Batching

- **Page:** 363 (PDF page 365) · **Chapter:** LLM Deployment
- **BBox:** [99.75, 405.16, 512.25, 558.91] on page 612×792 pt · **Render:** 1145×427 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Infrastructure (0.82) · Agent Protocol Fabric (0.47) · AI / ML Foundation (0.41)
- **Primary branch:** infrastructure · **Confidence:** 0.82 → review queue
- **Integrity:** sha `2088de68dcbc4372` · dup group `dup_0451` (1)
- **Heading:** #5) Benefit Automatically from Continuous Batching
- **Caption:** No additional configuration is required for this.
- **Paragraph before:** This lets us serve multiple LoRA adapters from the same base model. #5) Benefit Automatically from Continuous Batching As requests come in, vLLM automatically batches them to maximize GPU utilization.
- **Paragraph after:** No additional configuration is required for this. #6) Serve Multiple Models Together Finally, if our application requires more than one model, we can host them in a single server.
- **OCR:** [ X X J @ multiple_completions.py or tions r 1€ response = client.chat.completions.create( model="meta-1lama/Llama-3-8b-Instruct", messages=[...1], messages n=32,

### fig_0478 — Each request simply specifies the model to use.

- **Page:** 364 (PDF page 366) · **Chapter:** LLM Deployment
- **BBox:** [130.88, 67.50, 481.12, 204.75] on page 612×792 pt · **Render:** 973×381 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Infrastructure (0.80) · Agent Protocol Fabric (0.45) · LLM Engineering (0.40) · Software Architecture (0.40)
- **Primary branch:** infrastructure · **Confidence:** 0.80 → review queue
- **Integrity:** sha `344b4bab993013cf` · dup group `dup_0452` (1)
- **Caption:** Each request simply specifies the model to use.
- **Paragraph after:** Each request simply specifies the model to use. LitServe With vLLM, we now have a reliable way to serve LLMs efficiently. It handles the core challenges of inference like batching, KV-cache management and routing
- **OCR:** [ X X J command-line python -m vllm.entrypoints.api_server \ ——-model meta-1llama/Llama-3-8b-Instruct \ —-model mistralai/Mistral-7B-Instruct

### fig_0479 — This example deploys a Llama model with LitServe in a simple end-to-end flow.

- **Page:** 365 (PDF page 367) · **Chapter:** LLM Deployment
- **BBox:** [102.00, 150.88, 510.00, 514.62] on page 612×792 pt · **Render:** 1133×1010 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Infrastructure (0.75) · Agent Protocol Fabric (0.52) · LLM Engineering (0.40) · AI / ML Foundation (0.38)
- **Primary branch:** infrastructure · **Confidence:** 0.75 → review queue
- **Integrity:** sha `169f1c22261c74d5` · dup group `dup_0453` (1)
- **Caption:** This example deploys a Llama model with LitServe in a simple end-to-end flow.
- **Paragraph before:** Because it works at this level, LitServe can serve a wide range of model types, including vision, audio, text and multimodal systems. To make this concrete, let’s start with a minimal example and then break it down.
- **Paragraph after:** This example deploys a Llama model with LitServe in a simple end-to-end flow. Each part of the service maps to one function in the API class. Next, we’ll break down each part to understand the LitServe pattern clearly. 1) Load the Model
- **OCR:** (X N J @ deploy_with_litserve.py import litsgpt import litserve as 1s class SimpleLitAPI(ls.LitAPI): def setup(self, device): # Load the model once when the server starts self.llm = litgpt.LLM.load("meta-1lama/Meta-Llama-3-8B-Instruct") decode_ request(self request): return request["prompt"] predlct(self prompt) from the model (st ¢ enabled) yield from self 1lm.generate(prompt, max_new_tokens=200, stream=True) encode_response(self, output): # Wrap d t tokens into JSON for out in output: yield {"output": out} ate th api = SimpleLitAPI() server = ls.LitServer(api, stream=True) server.run(port=8000)

### fig_0480 — Here we load the Llama model into memory so it’s ready for inference.

- **Page:** 366 (PDF page 368) · **Chapter:** LLM Deployment
- **BBox:** [113.25, 67.50, 498.75, 225.75] on page 612×792 pt · **Render:** 1071×440 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Infrastructure (0.71) · Agent Memory (0.49) · Agent Protocol Fabric (0.49)
- **Primary branch:** infrastructure · **Confidence:** 0.71 → review queue
- **Integrity:** sha `fbe225a3a7eb302d` · dup group `dup_0454` (1)
- **Caption:** Here we load the Llama model into memory so it’s ready for inference.
- **Paragraph after:** Here we load the Llama model into memory so it’s ready for inference. 2) Decode the Request Incoming requests arrive as JSON. This method extracts the part of the request the model needs - in this case, the
- **OCR:** [ X N J @ load_model.py import litsgpt import litserve as 1s class SimpleLitAPI(ls.LitAPI): def setup(self, device): self.llm = litgpt.LLM.load("meta-1lama/Meta-Llama-3-8B-Instruct")

### fig_0481 — 2) Decode the Request

- **Page:** 366 (PDF page 368) · **Chapter:** LLM Deployment
- **BBox:** [178.12, 328.94, 433.88, 511.19] on page 612×792 pt · **Render:** 711×506 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Infrastructure (0.68) · LLM Engineering (0.48) · Agent Protocol Fabric (0.48) · Agent Memory (0.41)
- **Primary branch:** infrastructure · **Confidence:** 0.68 → review queue
- **Integrity:** sha `d322ed4cd06d77dc` · dup group `dup_0455` (2)
- **Heading:** 2) Decode the Request
- **Caption:** This method extracts the part of the request the model needs - in this case, the
- **Paragraph before:** Here we load the Llama model into memory so it’s ready for inference. 2) Decode the Request Incoming requests arrive as JSON.
- **Paragraph after:** This method extracts the part of the request the model needs - in this case, the prompt. 3) Run Inference This is where the model is actually called.
- **OCR:** [ X N J @ parse_request.py import litgpt import litserve as 1s class SimpleLitAPI(1ls.LitAPI): def decode_request(self, request): # tract the u p return request["prompt"]

### fig_0482 — predict() can stream output by yielding tokens as they are produced.

- **Page:** 367 (PDF page 369) · **Chapter:** LLM Deployment
- **BBox:** [142.88, 67.50, 469.12, 277.50] on page 612×792 pt · **Render:** 907×583 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Infrastructure (0.58) · Data Engineering (0.54) · AI / ML Foundation (0.49) · LLM Engineering (0.44)
- **Primary branch:** infrastructure · **Confidence:** 0.58 → review queue
- **Integrity:** sha `811ccd940941d5b7` · dup group `dup_0456` (1)
- **Caption:** predict() can stream output by yielding tokens as they are produced.
- **Paragraph after:** predict() can stream output by yielding tokens as they are produced. 4) Return the Response Whatever predict() yields is turned into the final response. Here we wrap each streamed chunk in a simple JSON object.
- **OCR:** [ N X J @ run_inference.py import litgpt import litserve as 1ls class SimpleLitAPI(1ls.LitAPI): def predict(self, prompt): the yield from self.llm.generate( prompt, max_new_tokens=200, stream=True

### fig_0483 — 4) Return the Response

- **Page:** 367 (PDF page 369) · **Chapter:** LLM Deployment
- **BBox:** [153.00, 380.69, 459.00, 597.44] on page 612×792 pt · **Render:** 850×602 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Infrastructure (0.60) · Agent Protocol Fabric (0.53) · Data Engineering (0.49) · RAG / Knowledge Engineering (0.42)
- **Primary branch:** infrastructure · **Confidence:** 0.60 → review queue
- **Integrity:** sha `68a12d0f51e71817` · dup group `dup_0455` (2)
- **Heading:** 4) Return the Response
- **Caption:** Here we wrap each streamed chunk in a simple JSON object.
- **Paragraph before:** predict() can stream output by yielding tokens as they are produced. 4) Return the Response Whatever predict() yields is turned into the final response.
- **Paragraph after:** Here we wrap each streamed chunk in a simple JSON object. 5) Launch the Server Finally, we create the API instance and run the server.
- **OCR:** [ X X J @ return_response.py import litgpt import litserve as 1s class SimpleLitAPI(1ls.LitAPI): def encode_response(self, output): # Format streamed output into JSO for out in output: yield {"output": out}

### fig_0484 — This exposes the model as an HTTP endpoint.

- **Page:** 368 (PDF page 370) · **Chapter:** LLM Deployment
- **BBox:** [141.00, 67.50, 471.00, 360.75] on page 612×792 pt · **Render:** 917×815 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Infrastructure (0.68) · Agent Protocol Fabric (0.62) · LLM Engineering (0.38) · Data Engineering (0.38)
- **Primary branch:** infrastructure · **Confidence:** 0.68 → review queue
- **Integrity:** sha `1e39486c0d741f6c` · dup group `dup_0457` (1)
- **Caption:** This exposes the model as an HTTP endpoint.
- **Paragraph after:** This exposes the model as an HTTP endpoint. Deployment transforms a trained model into a running service that applications interact with in real time. Once it is exposed through an API, it encounters real traffic, fluctuating load and
- **OCR:** ®®® @ launch_serverpy import litsgpt import litserve as 1ls class SimpleLitAPI(1ls.LitAPI): def setup(self, device): def decode_request(self, request): def predict(self, prompt): def encode_response(self, output): = "__main__": SimpleLitAPI() server = ls.LitServer(api, stream=True) server.run(port=8000)

### fig_0485 — That is the purpose of observability.

- **Page:** 370 (PDF page 372) · **Chapter:** LLM Observability
- **BBox:** [148.12, 222.22, 463.88, 393.97] on page 612×792 pt · **Render:** 877×477 px
- **Composition:** raster · **Role:** concept · **Quality:** 0.9
- **Mapping:** Observability (0.86) · LLM Engineering (0.49)
- **Primary branch:** observability · **Confidence:** 0.86 → auto-accept
- **Integrity:** sha `dfc50258e1f8b65c` · dup group `dup_0458` (1)
- **Caption:** That is the purpose of observability.
- **Paragraph before:** Real users, prompts, edge cases and system interactions now shape how the application performs. At this stage, the core question shifts from “Is the model good?” to “What is actually happening inside the system?”
- **Paragraph after:** That is the purpose of observability. Observability helps us see how the system behaves as it runs - ● What inputs does it receive? ●
- **OCR:** B User Prompt Response Tracing - Dashboard

### fig_0486 — Evaluation measures how well the system performs on a defined set of tasks.

- **Page:** 371 (PDF page 373) · **Chapter:** LLM Observability
- **BBox:** [125.25, 99.28, 486.75, 196.03] on page 612×792 pt · **Render:** 1005×269 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.6
- **Mapping:** Evaluation (0.65) · Observability (0.59) · Agent Protocol Fabric (0.41) · Infrastructure (0.41)
- **Primary branch:** evaluation · **Confidence:** 0.65 → review queue
- **Integrity:** sha `5b487edb2877ba3a` · dup group `dup_0459` (1)
- **Caption:** Evaluation measures how well the system performs on a defined set of tasks.
- **Paragraph before:** observability, since both play different roles in an LLM system.
- **Paragraph after:** Evaluation measures how well the system performs on a defined set of tasks. ● It uses curated datasets, metrics and controlled tests to assess qualities such as correctness, relevance, factuality, and safety. ● It is typically done before deployment, or as part of a periodic offline
- **OCR:** Evaluation ’ ObserVQbilitL/

### fig_0487 — ● It uses curated datasets, metrics and controlled tests to assess qualities

- **Page:** 371 (PDF page 373) · **Chapter:** LLM Observability
- **BBox:** [154.12, 235.34, 457.88, 452.09] on page 612×792 pt · **Render:** 843×602 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Evaluation (0.72) · Observability (0.51) · Agent Protocol Fabric (0.43) · Infrastructure (0.39)
- **Primary branch:** evaluation · **Confidence:** 0.72 → review queue
- **Integrity:** sha `fdd91f0e8963b26c` · dup group `dup_0460` (1)
- **Caption:** ● It uses curated datasets, metrics and controlled tests to assess qualities
- **Paragraph before:** observability, since both play different roles in an LLM system. Evaluation measures how well the system performs on a defined set of tasks.
- **Paragraph after:** ● It uses curated datasets, metrics and controlled tests to assess qualities such as correctness, relevance, factuality, and safety. ● It is typically done before deployment, or as part of a periodic offline benchmarking process.
- **OCR:** Evaluation Corretness Cumted datasets / Q < _=> Relevance —_ Factuality Defined tasks i \ \|l\|\| (43 Metrics & controlled tests Safety

### fig_0488 — ● It captures real inputs, model outputs, retrieved context, latencies, costs

- **Page:** 372 (PDF page 374) · **Chapter:** LLM Observability
- **BBox:** [145.88, 67.50, 466.12, 228.00] on page 612×792 pt · **Render:** 889×446 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Observability (0.65) · Context Engineering (0.47) · RAG / Knowledge Engineering (0.47) · Business Automation (0.47)
- **Primary branch:** observability · **Confidence:** 0.65 → review queue
- **Integrity:** sha `5dac2835d5b77e82` · dup group `dup_0461` (1)
- **Caption:** ● It captures real inputs, model outputs, retrieved context, latencies, costs
- **Paragraph after:** ● It captures real inputs, model outputs, retrieved context, latencies, costs and component-level traces. ● It helps identify regressions, bottlenecks, failure cases and shifts in user
- **OCR:** Observability Real inputs i Identify production regression

### fig_0489 — Tracking a Simple Python Function

- **Page:** 373 (PDF page 375) · **Chapter:** LLM Observability
- **BBox:** [182.62, 234.47, 429.38, 383.72] on page 612×792 pt · **Render:** 685×414 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Tool / Action Fabric (0.78) · Observability (0.57)
- **Primary branch:** tool-action-fabric · **Confidence:** 0.78 → review queue
- **Integrity:** sha `6eb5111cccdf826d` · dup group `dup_0462` (1)
- **Heading:** Tracking a Simple Python Function
- **Caption:** To do this, Opik provides a powerful @track decorator that makes tracking a
- **Paragraph before:** Tracking a Simple Python Function Let's start with a simple demo. Imagine we want to track all the invocations to this simple Python function specified below:
- **Paragraph after:** To do this, Opik provides a powerful @track decorator that makes tracking a Python function effortless. That's it!
- **OCR:** [ X J @ Opik-demo.py my_function(x: int) — int: return x + 1 my_function(1)

### fig_0490 — Tracking a Simple Python Function

- **Page:** 373 (PDF page 375) · **Chapter:** LLM Observability
- **BBox:** [181.12, 438.81, 430.88, 629.31] on page 612×792 pt · **Render:** 693×530 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Tool / Action Fabric (0.76) · Observability (0.59)
- **Primary branch:** tool-action-fabric · **Confidence:** 0.76 → review queue
- **Integrity:** sha `5ecc3af0f21a9a8a` · dup group `dup_0463` (1)
- **Heading:** Tracking a Simple Python Function
- **Caption:** That's it!
- **Paragraph before:** Imagine we want to track all the invocations to this simple Python function specified below: To do this, Opik provides a powerful @track decorator that makes tracking a Python function effortless.
- **Paragraph after:** That's it!
- **OCR:** 000 @ Opik-demo.py from opik import track atrack def my_function(x: int) — int: return x + 1 my_function(1)

### fig_0491 — If we run the above code, which is decorated with the @track decorator, and after

- **Page:** 374 (PDF page 376) · **Chapter:** LLM Observability
- **BBox:** [134.62, 146.88, 477.38, 357.62] on page 612×792 pt · **Render:** 953×585 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Observability (0.84) · Tool / Action Fabric (0.46) · Business Automation (0.40)
- **Primary branch:** observability · **Confidence:** 0.84 → review queue
- **Integrity:** sha `358784711c84104a` · dup group `dup_0464` (2)
- **Caption:** If we run the above code, which is decorated with the @track decorator, and after
- **Paragraph before:** By wrapping any function with this decorator, you can automatically trace and log its execution inside the Opik dashboard. For instance, currently, our dashboard does not show anything.
- **Paragraph after:** If we run the above code, which is decorated with the @track decorator, and after that, we go to the dashboard, we will find this: As depicted above, after running the function, Opik automatically creates a default project in its dashboard.
- **OCR:** De e & mtenm meemoO A comet. © schawa » proiecis ® @ vame Projects [—— e 3 wvimes 3 Thare are o projects yet « ¢ mewmsrowo o u ® corsuon

### fig_0492 — As depicted above, after running the function, Opik automatically creates a

- **Page:** 374 (PDF page 376) · **Chapter:** LLM Observability
- **BBox:** [137.25, 412.69, 474.75, 620.44] on page 612×792 pt · **Render:** 937×577 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Observability (0.82) · Tool / Action Fabric (0.53)
- **Primary branch:** observability · **Confidence:** 0.82 → review queue
- **Integrity:** sha `a0466c9dfbab753f` · dup group `dup_0464` (2)
- **Caption:** As depicted above, after running the function, Opik automatically creates a
- **Paragraph before:** log its execution inside the Opik dashboard. For instance, currently, our dashboard does not show anything. If we run the above code, which is decorated with the @track decorator, and after that, we go to the dashboard, we will find this:
- **Paragraph after:** As depicted above, after running the function, Opik automatically creates a default project in its dashboard. In this project, you can explore the inputs provided to the function, the outputs it produced, and everything that happened during its execution.
- **OCR:** D e & i meemauw £ comet \| awaia s o 0 © wome Projects & o ' © o ' oot et omas o cmasor o B oowmens 1 K tommanay 0w [eu—. © pomarior 1 @ porns © contgusmon

### fig_0493 — Also, if you invoke this function multiple times, like below:

- **Page:** 375 (PDF page 377) · **Chapter:** LLM Observability
- **BBox:** [151.50, 136.84, 460.50, 327.34] on page 612×792 pt · **Render:** 859×529 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Tool / Action Fabric (0.71) · Observability (0.64)
- **Primary branch:** tool-action-fabric · **Confidence:** 0.71 → review queue
- **Integrity:** sha `69f6de084a4060e2` · dup group `dup_0465` (1)
- **Caption:** Also, if you invoke this function multiple times, like below:
- **Paragraph before:** For instance, once we open this project, we see the following invocation of the function created above, along with the input, the output produced by the function, and the time it took to generate a response.
- **Paragraph after:** Also, if you invoke this function multiple times, like below: The dashboard will show all the invocations of the functions:
- **OCR:** Beoe P O U —— @ vome Default Project LR B == G o e .o o+ : : : > & e e e —— S G2 - O SRy rorgos

### fig_0494 — The dashboard will show all the invocations of the functions:

- **Page:** 375 (PDF page 377) · **Chapter:** LLM Observability
- **BBox:** [185.62, 362.69, 426.38, 507.44] on page 612×792 pt · **Render:** 669×402 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Tool / Action Fabric (0.75) · Observability (0.60)
- **Primary branch:** tool-action-fabric · **Confidence:** 0.75 → review queue
- **Integrity:** sha `26c11062e3cffbab` · dup group `dup_0466` (1)
- **Caption:** The dashboard will show all the invocations of the functions:
- **Paragraph before:** For instance, once we open this project, we see the following invocation of the function created above, along with the input, the output produced by the function, and the time it took to generate a response. Also, if you invoke this function multiple times, like below:
- **Paragraph after:** The dashboard will show all the invocations of the functions:
- **OCR:** \| N J % Opik-demo.py my_function(2) my_function(3) Y my_function(4)

### fig_0495 — Opening any specific invocation, we can look at the inputs and the outputs in a

- **Page:** 376 (PDF page 378) · **Chapter:** LLM Observability
- **BBox:** [139.50, 67.50, 472.50, 273.00] on page 612×792 pt · **Render:** 925×571 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Observability (0.87) · n8n / Workflow Automation (0.48)
- **Primary branch:** observability · **Confidence:** 0.87 → auto-accept
- **Integrity:** sha `064533393f6579c7` · dup group `dup_0467` (1)
- **Caption:** Opening any specific invocation, we can look at the inputs and the outputs in a
- **Paragraph after:** Opening any specific invocation, we can look at the inputs and the outputs in a clean YAML format, along with other details that were tracked by Opik: This seamless integration makes it easy to monitor and debug your workflows without adding any complex boilerplate code.
- **OCR:** De e 5 omcon meemaoo £ comet PR — Y @ Home. Default Project v 5\| = Q@ smamp v Il ] iy o & s 3 [ER—— et R R, - T R — ensocsn Cein fRe—, o # rorgons o st st extocn Gy o2y o N amersm as2e 20 s oo v Gt o) o © contgunin © srowmraots .

### fig_0496 — This seamless integration makes it easy to monitor and debug your workflows

- **Page:** 376 (PDF page 378) · **Chapter:** LLM Observability
- **BBox:** [135.38, 328.09, 476.62, 538.09] on page 612×792 pt · **Render:** 947×583 px
- **Composition:** raster · **Role:** architecture · **Quality:** 0.9
- **Mapping:** Observability (0.86) · n8n / Workflow Automation (0.49)
- **Primary branch:** observability · **Confidence:** 0.86 → auto-accept
- **Integrity:** sha `59051e442ee5677f` · dup group `dup_0468` (1)
- **Caption:** This seamless integration makes it easy to monitor and debug your workflows
- **Paragraph before:** Opening any specific invocation, we can look at the inputs and the outputs in a clean YAML format, along with other details that were tracked by Opik:
- **Paragraph after:** This seamless integration makes it easy to monitor and debug your workflows without adding any complex boilerplate code. Tracking LLM calls with Opik The purpose of this section is to show how Opik can log and monitor the
- **OCR:** o e & comicon meemOOD B Aspan e D s L - - A L] s

### fig_0497 — Next, we shall be using Opik's OpenAI integration which is imported below,

- **Page:** 377 (PDF page 379) · **Chapter:** LLM Observability
- **BBox:** [190.50, 117.06, 421.50, 246.06] on page 612×792 pt · **Render:** 641×358 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Observability (0.68) · Agent Protocol Fabric (0.59) · Tool / Action Fabric (0.43)
- **Primary branch:** observability · **Confidence:** 0.68 → review queue
- **Integrity:** sha `f2b161621a36a565` · dup group `dup_0469` (1)
- **Caption:** Next, we shall be using Opik's OpenAI integration which is imported below,
- **Paragraph before:** After specifying the OpenAI API key in the .env file, we will load it into our environment:
- **Paragraph after:** Next, we shall be using Opik's OpenAI integration which is imported below, along with the OpenAI library: Moving on, we wrap the OpenAI client with Opik’s track_openai function. This ensures that all interactions with the OpenAI API are tracked and logged in the
- **OCR:** o0 @ Opik-demo.py dotenv )rt load_dotenv load_dotenv()

### fig_0498 — Moving on, we wrap the OpenAI client with Opik’s track_openai function. This

- **Page:** 377 (PDF page 379) · **Chapter:** LLM Observability
- **BBox:** [133.12, 301.19, 478.88, 417.44] on page 612×792 pt · **Render:** 961×323 px
- **Composition:** raster · **Role:** code · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.63) · Observability (0.63) · Tool / Action Fabric (0.44)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.63 → review queue
- **Integrity:** sha `a0a5ec6143ad655c` · dup group `dup_0470` (1)
- **Caption:** Moving on, we wrap the OpenAI client with Opik’s track_openai function. This
- **Paragraph before:** After specifying the OpenAI API key in the .env file, we will load it into our environment: Next, we shall be using Opik's OpenAI integration which is imported below, along with the OpenAI library:
- **Paragraph after:** Moving on, we wrap the OpenAI client with Opik’s track_openai function. This ensures that all interactions with the OpenAI API are tracked and logged in the Opik dashboard. Any API calls made using this client will now be automatically monitored, including their inputs, outputs, and associated metadata.
- **OCR:** \| X J @ Opik-demo.py openai OpenAl opik.integrations.openai track_openai

### fig_0499 — Next, we define our multimodal prompt input as follows:

- **Page:** 377 (PDF page 379) · **Chapter:** LLM Observability
- **BBox:** [179.25, 519.38, 432.75, 604.12] on page 612×792 pt · **Render:** 705×236 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Observability (0.63) · Agent Protocol Fabric (0.58) · LLM Engineering (0.44) · Tool / Action Fabric (0.40)
- **Primary branch:** observability · **Confidence:** 0.63 → review queue
- **Integrity:** sha `f60f19f90e93c3a2` · dup group `dup_0471` (1)
- **Caption:** Next, we define our multimodal prompt input as follows:
- **Paragraph before:** Moving on, we wrap the OpenAI client with Opik’s track_openai function. This ensures that all interactions with the OpenAI API are tracked and logged in the Opik dashboard. Any API calls made using this client will now be automatically monitored, including their inputs, outputs, and associated metadata.
- **Paragraph after:** Next, we define our multimodal prompt input as follows:
- **OCR:** L X} @ Opik-demo.py client track_openai(OpenAI())

### fig_0500 — Finally, we invoke the chat completion API as follows:

- **Page:** 378 (PDF page 380) · **Chapter:** LLM Observability
- **BBox:** [128.25, 67.50, 483.75, 270.00] on page 612×792 pt · **Render:** 987×563 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.68) · Observability (0.68)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.68 → review queue
- **Integrity:** sha `e359ca80c1dba7fb` · dup group `dup_0472` (1)
- **Caption:** Finally, we invoke the chat completion API as follows:
- **Paragraph after:** Finally, we invoke the chat completion API as follows: Here, we make the API call using the chat.completions.create method: ● model: Specifies the LLM to use (gpt-4o-mini in this case). ●
- **OCR:** [ X X ) @ Opik-demo.py messages = [ {"role": "user", "content": [ { Ctypelsl Skpxtt, "text": "What's in this image?" o { "type": "image_url", "image_url": { "url": "https://i.ytimg.com/vi/NAmL1nDDyjg/maxresdefault.jpg"

### fig_0501 — Here, we make the API call using the chat.completions.create method:

- **Page:** 378 (PDF page 380) · **Chapter:** LLM Observability
- **BBox:** [162.75, 305.31, 449.25, 447.06] on page 612×792 pt · **Render:** 795×393 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.68) · Observability (0.59) · AI / ML Foundation (0.43)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.68 → review queue
- **Integrity:** sha `972a28ea62a9f1cc` · dup group `dup_0473` (1)
- **Caption:** Here, we make the API call using the chat.completions.create method:
- **Paragraph before:** Finally, we invoke the chat completion API as follows:
- **Paragraph after:** Here, we make the API call using the chat.completions.create method: ● model: Specifies the LLM to use (gpt-4o-mini in this case). ● messages: Provides the multimodal input we defined earlier.
- **OCR:** o000 @ Opik-demo.py response = client.chat.completions.create( model="gpt-40-mini", messages=messasges, max_tokens=300

### fig_0502 — Opening this specific run highlights so many details about the LLM invocation,

- **Page:** 379 (PDF page 381) · **Chapter:** LLM Observability
- **BBox:** [121.12, 67.50, 490.88, 290.25] on page 612×792 pt · **Render:** 1027×619 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Observability (0.74) · AI / ML Foundation (0.48) · Business Automation (0.48)
- **Primary branch:** observability · **Confidence:** 0.74 → review queue
- **Integrity:** sha `9b18ec0434540e8f` · dup group `dup_0474` (1)
- **Caption:** Opening this specific run highlights so many details about the LLM invocation,
- **Paragraph after:** Opening this specific run highlights so many details about the LLM invocation, like the input, the output, the number of tokens used, the cost incurred for this specific run and more.
- **OCR:** € comet B \| b » o » oo n @ Mome. Default Project B pompony 1 « Showing 11011 F— © contiguaton

### fig_0503 — LLM Observability figure

- **Page:** 379 (PDF page 381) · **Chapter:** LLM Observability
- **BBox:** [126.00, 365.12, 486.00, 709.38] on page 612×792 pt · **Render:** 1000×956 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Observability (0.68) · AI / ML Foundation (0.51) · RAG / Knowledge Engineering (0.43) · Tool / Action Fabric (0.43)
- **Primary branch:** observability · **Confidence:** 0.68 → review queue
- **Integrity:** sha `8dad8c09cf0970eb` · dup group `dup_0475` (1)
- **Paragraph before:** Opening this specific run highlights so many details about the LLM invocation, like the input, the output, the number of tokens used, the cost incurred for this specific run and more.
- **OCR:** Trace spans 1 ssns Collapse all O chat_completion creale em— a7 #1M B <5000 D Chat_compIetion_Croale mmm— ©47 #18 % <5000 © Addtodataset 4, Share Y Delete O chat_completion_create © CopyID £ Annotate @475 # WMtokens @ $0.0002109 © openai + Input/output Feedback scores Metadata images % input A YAML v © + pessages: o content: - type: text s text: What's n this inage? - type: inage_url v tmage_url: url: https://1.yting. con/vi/NAnL n0Dy o maxresdefault. jog Output ® YAML ~ © 1. chotces: 2. - Finishresson: stop 5 tdext o) 4 ogprobs: aull 5. messager ‘ content: The inage features a golden retriever Lying on the beach. The dog appears to be wet, Uikely fron playtng in the water. It's holding a bright green tennis ball tn front of L2, wWith waves and 2 blue sky n the background. The scene Looks Joyful and relaxed, capturing 2 playful nonent at the beach. " refusal: null € role: assistant, 5 au

### fig_0504 — Next, we again create an OpenAI client, but this time, we specify the base_url as

- **Page:** 380 (PDF page 382) · **Chapter:** LLM Observability
- **BBox:** [135.75, 256.00, 476.25, 371.50] on page 612×792 pt · **Render:** 945×320 px
- **Composition:** raster · **Role:** process · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.68) · Observability (0.68)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.68 → review queue
- **Integrity:** sha `9bafab04cc1a0a03` · dup group `dup_0476` (1)
- **Caption:** Next, we again create an OpenAI client, but this time, we specify the base_url as
- **Paragraph before:** Let’s see that. The process remains almost the same. We shall again use Opik's OpenAI integration for this demo, which is imported below, along with the OpenAI library:
- **Paragraph after:** Next, we again create an OpenAI client, but this time, we specify the base_url as https://localhost:11434/v1: Next, to log all the invocations made to our client, we pass the client to the track_openai method:
- **OCR:** \| X J @ Opik-demo.py openai i rt OpenAI opik.integrations.openai import track_openai

### fig_0505 — Next, to log all the invocations made to our client, we pass the client to the

- **Page:** 380 (PDF page 382) · **Chapter:** LLM Observability
- **BBox:** [66.00, 402.10, 478.88, 582.59] on page 612×792 pt · **Render:** 1147×502 px
- **Composition:** hybrid · **Role:** process · **Quality:** 1
- **Mapping:** Agent Protocol Fabric (0.73) · Observability (0.62)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.73 → review queue
- **Integrity:** sha `fef5af965f5be87c` · dup group `dup_0477` (1)
- **Caption:** Next, to log all the invocations made to our client, we pass the client to the
- **Paragraph before:** The process remains almost the same. We shall again use Opik's OpenAI integration for this demo, which is imported below, along with the OpenAI library: Next, we again create an OpenAI client, but this time, we specify the base_url as
- **Paragraph after:** Next, to log all the invocations made to our client, we pass the client to the track_openai method:
- **OCR:** https://localhost:11434/v1: [ X} @ Opik-demo. py client = OpenAI( base_url="http://localhost:11434/v1/", api_key='ollama',

### fig_0506 — Finally, we invoke the completion API as follows:

- **Page:** 381 (PDF page 383) · **Chapter:** LLM Observability
- **BBox:** [153.75, 67.50, 458.25, 235.50] on page 612×792 pt · **Render:** 845×467 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Agent Protocol Fabric (0.74) · Observability (0.61)
- **Primary branch:** agent-protocol-fabric · **Confidence:** 0.74 → review queue
- **Integrity:** sha `38be32e9d12eda1f` · dup group `dup_0478` (1)
- **Caption:** Finally, we invoke the completion API as follows:
- **Paragraph after:** Finally, we invoke the completion API as follows: If we head over to the dashboard again, we see another entry:
- **OCR:** L X J @ Opik-demo py client = OpenAI( base_url="http://localhost:11434/v1/"', api_key='ollama', client = track_openai(client)

### fig_0507 — If we head over to the dashboard again, we see another entry:

- **Page:** 381 (PDF page 383) · **Chapter:** LLM Observability
- **BBox:** [145.88, 270.81, 466.12, 482.31] on page 612×792 pt · **Render:** 889×587 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Observability (0.76) · Agent Protocol Fabric (0.51) · Evaluation (0.43)
- **Primary branch:** observability · **Confidence:** 0.76 → review queue
- **Integrity:** sha `2c58f153d1967bb8` · dup group `dup_0479` (1)
- **Caption:** If we head over to the dashboard again, we see another entry:
- **Paragraph before:** Finally, we invoke the completion API as follows:
- **Paragraph after:** If we head over to the dashboard again, we see another entry:
- **OCR:** 000 @ Opik-demo.py response = client.chat.completions.create( messages=[ { 'role': 'user', 'content': 'Say this is a test', ] ’ model='1lama3.2:1b"',

### fig_0508 — LLM Observability figure

- **Page:** 381 (PDF page 383) · **Chapter:** LLM Observability
- **BBox:** [102.00, 517.62, 510.00, 703.62] on page 612×792 pt · **Render:** 1133×517 px
- **Composition:** raster · **Role:** diagram · **Quality:** 0.9
- **Mapping:** Observability (0.72) · LLM Engineering (0.54) · Agent Protocol Fabric (0.44)
- **Primary branch:** observability · **Confidence:** 0.72 → review queue
- **Integrity:** sha `0e43abf92110d3b3` · dup group `dup_0480` (1)
- **Paragraph before:** Finally, we invoke the completion API as follows: If we head over to the dashboard again, we see another entry:
- **OCR:** £ comet avi-chawia > Projects > DefaultProject & rome Default Project Pr— Taces LMcals Mevis uies # proocs ' 8 oaasers ' » Name ot ouput Duston . 5 coumz count e & Experiments. 1 chatcomplaton_creste { "essaes”s [ € “roles "sar. € “cotcess [ “Fnth.remen’s - oz S 4 chat comploton crese { “essaes™s [ {“roles “wer- (“cotcess [ “nts_semen's - s @ Payground K¢ sommraanz » Configuration ® configuration

### fig_0509 — That was simple, wasn't it?

- **Page:** 382 (PDF page 384) · **Chapter:** LLM Observability
- **BBox:** [115.88, 136.84, 496.12, 378.34] on page 612×792 pt · **Render:** 1057×670 px
- **Composition:** raster · **Role:** result · **Quality:** 0.9
- **Mapping:** Observability (0.59) · Evaluation (0.53) · AI / ML Foundation (0.47) · Tool / Action Fabric (0.47)
- **Primary branch:** observability · **Confidence:** 0.59 → review queue
- **Integrity:** sha `9e854297f3e0d432` · dup group `dup_0481` (1)
- **Caption:** That was simple, wasn't it?
- **Paragraph before:** Opening the latest (top) invocation, we can again see similar details like we saw with OpenAI - the input, the output, the number of tokens used, the cost and more.
- **Paragraph after:** That was simple, wasn't it?
- **OCR:** © Addtodataset (b Share (T Delete Trace spans 1spans © chat_completion_create © CopyID £ Annotate © 025 4 35tokens Collapse all © openal + © O chatcompletion_creats emmm— ©02s #35 InputfOutput Feedback scores Metadata D Chal_cOmPIetion_Create smm—— o2 %35 input “ YAML © 1. messages: 2. - role: user 3 content: say this is a test output ~ YAML & 1, choices: 2. - flalsh_reason: stop 3 tndex: © 1 function_call: mull 1 tool_calls: null

---

## 7. Cross-reference: branch → figures

- **I. Foundational Computer Science** — 0 figures: —
- **II. Software Architecture** — 10 figures: fig_0019 (p13), fig_0177 (p125), fig_0192 (p141), fig_0265 (p197), fig_0420 (p321), fig_0422 (p322), fig_0423 (p323), fig_0432 (p328), fig_0433 (p329), fig_0478 (p364)
- **III. AI / ML Foundation** — 189 figures: fig_0001 (p0), fig_0002 (p0), fig_0003 (p0), fig_0004 (p0), fig_0005 (p0), fig_0006 (p0), fig_0007 (p0), fig_0008 (p0), fig_0009 (p6), fig_0010 (p6), fig_0011 (p7), fig_0012 (p7), fig_0013 (p8), fig_0014 (p9), fig_0015 (p10), fig_0016 (p11), fig_0017 (p11), fig_0018 (p12), fig_0019 (p13), fig_0020 (p14), fig_0021 (p14), fig_0022 (p15), fig_0023 (p17), fig_0024 (p18), fig_0025 (p18), fig_0026 (p19), fig_0027 (p20), fig_0028 (p20), fig_0029 (p21), fig_0030 (p22), fig_0031 (p23), fig_0032 (p24), fig_0033 (p24), fig_0034 (p25), fig_0035 (p26), fig_0036 (p26), fig_0037 (p27), fig_0038 (p27), fig_0039 (p28), fig_0040 (p29), fig_0041 (p29), fig_0042 (p29), fig_0043 (p30), fig_0044 (p30), fig_0045 (p30), fig_0046 (p31), fig_0047 (p32), fig_0048 (p33), fig_0049 (p33), fig_0050 (p34), fig_0051 (p34), fig_0052 (p35), fig_0053 (p36), fig_0054 (p37), fig_0055 (p38), fig_0056 (p39), fig_0057 (p40), fig_0058 (p40), fig_0059 (p40), fig_0060 (p41), fig_0061 (p42), fig_0062 (p42), fig_0063 (p44), fig_0064 (p44), fig_0065 (p45), fig_0066 (p46), fig_0067 (p46), fig_0068 (p47), fig_0077 (p55), fig_0079 (p57), fig_0080 (p57), fig_0088 (p64), fig_0089 (p66), fig_0090 (p67), fig_0091 (p68), fig_0092 (p69), fig_0093 (p69), fig_0094 (p70), fig_0095 (p71), fig_0096 (p71), fig_0097 (p72), fig_0098 (p72), fig_0099 (p73), fig_0100 (p73), fig_0101 (p74), fig_0102 (p74), fig_0103 (p75), fig_0104 (p75), fig_0105 (p76), fig_0106 (p77), fig_0107 (p77), fig_0108 (p78), fig_0109 (p78), fig_0110 (p79), fig_0111 (p79), fig_0112 (p80), fig_0113 (p81), fig_0114 (p82), fig_0115 (p82), fig_0116 (p83), fig_0117 (p84), fig_0118 (p84), fig_0119 (p86), fig_0120 (p86), fig_0121 (p87), fig_0122 (p88), fig_0123 (p88), fig_0124 (p88), fig_0125 (p89), fig_0126 (p89), fig_0127 (p90), fig_0128 (p91), fig_0129 (p91), fig_0130 (p92), fig_0131 (p94), fig_0132 (p95), fig_0133 (p95), fig_0134 (p96), fig_0135 (p97), fig_0136 (p98), fig_0137 (p99), fig_0138 (p99), fig_0139 (p101), fig_0140 (p102), fig_0142 (p106), fig_0143 (p107), fig_0144 (p107), fig_0150 (p110), fig_0155 (p113), fig_0156 (p113), fig_0157 (p113), fig_0158 (p114), fig_0159 (p114), fig_0160 (p115), fig_0161 (p115), fig_0164 (p116), fig_0167 (p118), fig_0168 (p119), fig_0169 (p119), fig_0174 (p122), fig_0175 (p122), fig_0177 (p125), fig_0181 (p131), fig_0183 (p132), fig_0184 (p132), fig_0185 (p133), fig_0186 (p134), fig_0187 (p135), fig_0188 (p136), fig_0189 (p136), fig_0190 (p137), fig_0191 (p139), fig_0200 (p152), fig_0203 (p154), fig_0210 (p161), fig_0215 (p166), fig_0325 (p248), fig_0327 (p251), fig_0397 (p306), fig_0398 (p307), fig_0400 (p308), fig_0412 (p316), fig_0415 (p318), fig_0416 (p319), fig_0417 (p319), fig_0418 (p320), fig_0419 (p320), fig_0421 (p321), fig_0423 (p323), fig_0424 (p324), fig_0425 (p324), fig_0426 (p325), fig_0427 (p326), fig_0428 (p326), fig_0429 (p327), fig_0430 (p327), fig_0431 (p328), fig_0432 (p328), fig_0433 (p329), fig_0434 (p332), fig_0474 (p362), fig_0476 (p363), fig_0477 (p363), fig_0479 (p365), fig_0482 (p367), fig_0501 (p378), fig_0502 (p379), fig_0503 (p379), fig_0509 (p382)
- **IV. LLM Engineering** — 125 figures: fig_0024 (p18), fig_0025 (p18), fig_0029 (p21), fig_0035 (p26), fig_0036 (p26), fig_0037 (p27), fig_0038 (p27), fig_0040 (p29), fig_0041 (p29), fig_0042 (p29), fig_0046 (p31), fig_0048 (p33), fig_0049 (p33), fig_0069 (p49), fig_0070 (p50), fig_0071 (p51), fig_0072 (p51), fig_0073 (p52), fig_0074 (p52), fig_0075 (p54), fig_0076 (p55), fig_0077 (p55), fig_0078 (p56), fig_0079 (p57), fig_0080 (p57), fig_0081 (p58), fig_0082 (p59), fig_0083 (p61), fig_0084 (p61), fig_0085 (p62), fig_0086 (p63), fig_0087 (p63), fig_0088 (p64), fig_0119 (p86), fig_0124 (p88), fig_0128 (p91), fig_0131 (p94), fig_0135 (p97), fig_0136 (p98), fig_0137 (p99), fig_0138 (p99), fig_0149 (p110), fig_0150 (p110), fig_0151 (p111), fig_0152 (p111), fig_0153 (p112), fig_0154 (p112), fig_0165 (p117), fig_0175 (p122), fig_0176 (p124), fig_0177 (p125), fig_0178 (p127), fig_0179 (p128), fig_0181 (p131), fig_0183 (p132), fig_0195 (p147), fig_0197 (p149), fig_0205 (p155), fig_0207 (p158), fig_0261 (p195), fig_0275 (p205), fig_0276 (p205), fig_0280 (p208), fig_0281 (p209), fig_0282 (p213), fig_0283 (p213), fig_0294 (p220), fig_0295 (p221), fig_0296 (p222), fig_0297 (p223), fig_0298 (p223), fig_0299 (p224), fig_0300 (p225), fig_0301 (p226), fig_0302 (p227), fig_0303 (p228), fig_0304 (p229), fig_0305 (p229), fig_0306 (p231), fig_0314 (p237), fig_0330 (p254), fig_0331 (p254), fig_0333 (p255), fig_0334 (p256), fig_0335 (p256), fig_0336 (p256), fig_0337 (p257), fig_0338 (p257), fig_0339 (p257), fig_0340 (p258), fig_0341 (p258), fig_0356 (p271), fig_0357 (p272), fig_0358 (p273), fig_0360 (p276), fig_0361 (p278), fig_0362 (p278), fig_0363 (p278), fig_0364 (p279), fig_0366 (p280), fig_0375 (p291), fig_0377 (p293), fig_0378 (p293), fig_0379 (p294), fig_0413 (p318), fig_0414 (p318), fig_0416 (p319), fig_0417 (p319), fig_0420 (p321), fig_0422 (p322), fig_0435 (p332), fig_0438 (p334), fig_0446 (p339), fig_0447 (p340), fig_0466 (p352), fig_0468 (p353), fig_0469 (p354), fig_0478 (p364), fig_0479 (p365), fig_0481 (p366), fig_0482 (p367), fig_0484 (p368), fig_0485 (p370), fig_0499 (p377), fig_0508 (p381)
- **V. Context Engineering** — 84 figures: fig_0032 (p24), fig_0033 (p24), fig_0076 (p55), fig_0084 (p61), fig_0149 (p110), fig_0151 (p111), fig_0152 (p111), fig_0154 (p112), fig_0156 (p113), fig_0157 (p113), fig_0158 (p114), fig_0164 (p116), fig_0165 (p117), fig_0175 (p122), fig_0180 (p130), fig_0181 (p131), fig_0182 (p131), fig_0183 (p132), fig_0190 (p137), fig_0191 (p139), fig_0192 (p141), fig_0193 (p143), fig_0194 (p146), fig_0195 (p147), fig_0196 (p148), fig_0197 (p149), fig_0198 (p150), fig_0199 (p151), fig_0200 (p152), fig_0201 (p153), fig_0202 (p153), fig_0203 (p154), fig_0204 (p154), fig_0205 (p155), fig_0206 (p157), fig_0207 (p158), fig_0208 (p159), fig_0209 (p160), fig_0210 (p161), fig_0213 (p164), fig_0214 (p165), fig_0215 (p166), fig_0216 (p166), fig_0217 (p168), fig_0218 (p170), fig_0219 (p171), fig_0220 (p173), fig_0221 (p173), fig_0230 (p180), fig_0232 (p181), fig_0243 (p187), fig_0245 (p187), fig_0264 (p197), fig_0265 (p197), fig_0266 (p198), fig_0280 (p208), fig_0312 (p235), fig_0316 (p238), fig_0319 (p244), fig_0320 (p245), fig_0336 (p256), fig_0339 (p257), fig_0341 (p258), fig_0342 (p259), fig_0343 (p260), fig_0345 (p261), fig_0349 (p265), fig_0359 (p274), fig_0381 (p295), fig_0382 (p295), fig_0396 (p306), fig_0398 (p307), fig_0435 (p332), fig_0436 (p333), fig_0437 (p333), fig_0441 (p337), fig_0442 (p337), fig_0450 (p342), fig_0459 (p348), fig_0462 (p349), fig_0464 (p350), fig_0465 (p351), fig_0470 (p355), fig_0488 (p372)
- **VI. RAG / Knowledge Engineering** — 151 figures: fig_0001 (p0), fig_0002 (p0), fig_0003 (p0), fig_0004 (p0), fig_0005 (p0), fig_0006 (p0), fig_0012 (p7), fig_0014 (p9), fig_0023 (p17), fig_0039 (p28), fig_0044 (p30), fig_0045 (p30), fig_0048 (p33), fig_0058 (p40), fig_0059 (p40), fig_0060 (p41), fig_0071 (p51), fig_0075 (p54), fig_0076 (p55), fig_0101 (p74), fig_0141 (p105), fig_0142 (p106), fig_0143 (p107), fig_0144 (p107), fig_0145 (p108), fig_0146 (p108), fig_0147 (p109), fig_0148 (p109), fig_0149 (p110), fig_0150 (p110), fig_0151 (p111), fig_0152 (p111), fig_0153 (p112), fig_0154 (p112), fig_0155 (p113), fig_0156 (p113), fig_0157 (p113), fig_0158 (p114), fig_0159 (p114), fig_0160 (p115), fig_0161 (p115), fig_0162 (p115), fig_0163 (p116), fig_0164 (p116), fig_0165 (p117), fig_0166 (p117), fig_0167 (p118), fig_0168 (p119), fig_0169 (p119), fig_0170 (p120), fig_0171 (p120), fig_0172 (p121), fig_0173 (p121), fig_0174 (p122), fig_0175 (p122), fig_0176 (p124), fig_0177 (p125), fig_0178 (p127), fig_0179 (p128), fig_0180 (p130), fig_0181 (p131), fig_0182 (p131), fig_0183 (p132), fig_0184 (p132), fig_0185 (p133), fig_0186 (p134), fig_0187 (p135), fig_0188 (p136), fig_0189 (p136), fig_0190 (p137), fig_0191 (p139), fig_0192 (p141), fig_0193 (p143), fig_0194 (p146), fig_0196 (p148), fig_0203 (p154), fig_0206 (p157), fig_0207 (p158), fig_0208 (p159), fig_0209 (p160), fig_0210 (p161), fig_0211 (p162), fig_0212 (p163), fig_0213 (p164), fig_0214 (p165), fig_0215 (p166), fig_0216 (p166), fig_0218 (p170), fig_0219 (p171), fig_0220 (p173), fig_0221 (p173), fig_0222 (p176), fig_0223 (p177), fig_0224 (p177), fig_0225 (p177), fig_0228 (p179), fig_0230 (p180), fig_0231 (p180), fig_0232 (p181), fig_0234 (p183), fig_0261 (p195), fig_0266 (p198), fig_0267 (p199), fig_0269 (p200), fig_0294 (p220), fig_0295 (p221), fig_0296 (p222), fig_0297 (p223), fig_0298 (p223), fig_0299 (p224), fig_0300 (p225), fig_0301 (p226), fig_0302 (p227), fig_0303 (p228), fig_0316 (p238), fig_0318 (p242), fig_0319 (p244), fig_0328 (p252), fig_0342 (p259), fig_0345 (p261), fig_0358 (p273), fig_0359 (p274), fig_0366 (p280), fig_0367 (p282), fig_0379 (p294), fig_0380 (p294), fig_0381 (p295), fig_0418 (p320), fig_0419 (p320), fig_0421 (p321), fig_0422 (p322), fig_0423 (p323), fig_0429 (p327), fig_0430 (p327), fig_0431 (p328), fig_0432 (p328), fig_0433 (p329), fig_0434 (p332), fig_0438 (p334), fig_0440 (p336), fig_0452 (p344), fig_0455 (p346), fig_0456 (p346), fig_0457 (p347), fig_0459 (p348), fig_0461 (p349), fig_0462 (p349), fig_0467 (p353), fig_0483 (p367), fig_0488 (p372), fig_0503 (p379)
- **VII. Agentic AI** — 172 figures: fig_0001 (p0), fig_0002 (p0), fig_0003 (p0), fig_0004 (p0), fig_0005 (p0), fig_0006 (p0), fig_0046 (p31), fig_0076 (p55), fig_0077 (p55), fig_0078 (p56), fig_0080 (p57), fig_0138 (p99), fig_0139 (p101), fig_0140 (p102), fig_0178 (p127), fig_0179 (p128), fig_0180 (p130), fig_0193 (p143), fig_0194 (p146), fig_0197 (p149), fig_0198 (p150), fig_0202 (p153), fig_0203 (p154), fig_0204 (p154), fig_0205 (p155), fig_0206 (p157), fig_0208 (p159), fig_0212 (p163), fig_0213 (p164), fig_0214 (p165), fig_0218 (p170), fig_0219 (p171), fig_0222 (p176), fig_0223 (p177), fig_0224 (p177), fig_0225 (p177), fig_0226 (p178), fig_0227 (p178), fig_0228 (p179), fig_0229 (p179), fig_0230 (p180), fig_0231 (p180), fig_0232 (p181), fig_0233 (p182), fig_0234 (p183), fig_0235 (p184), fig_0236 (p185), fig_0237 (p185), fig_0238 (p185), fig_0239 (p185), fig_0240 (p186), fig_0241 (p186), fig_0242 (p186), fig_0243 (p187), fig_0244 (p187), fig_0245 (p187), fig_0246 (p188), fig_0247 (p188), fig_0248 (p188), fig_0249 (p189), fig_0250 (p189), fig_0251 (p189), fig_0252 (p190), fig_0253 (p190), fig_0254 (p191), fig_0255 (p191), fig_0256 (p191), fig_0257 (p191), fig_0258 (p192), fig_0259 (p193), fig_0260 (p194), fig_0261 (p195), fig_0262 (p196), fig_0263 (p196), fig_0264 (p197), fig_0265 (p197), fig_0266 (p198), fig_0267 (p199), fig_0268 (p200), fig_0269 (p200), fig_0270 (p201), fig_0271 (p201), fig_0272 (p202), fig_0273 (p203), fig_0274 (p203), fig_0275 (p205), fig_0276 (p205), fig_0277 (p206), fig_0278 (p207), fig_0279 (p207), fig_0280 (p208), fig_0281 (p209), fig_0282 (p213), fig_0283 (p213), fig_0284 (p214), fig_0285 (p214), fig_0286 (p215), fig_0287 (p215), fig_0288 (p216), fig_0289 (p216), fig_0290 (p217), fig_0291 (p217), fig_0292 (p218), fig_0293 (p218), fig_0294 (p220), fig_0295 (p221), fig_0296 (p222), fig_0297 (p223), fig_0298 (p223), fig_0299 (p224), fig_0300 (p225), fig_0301 (p226), fig_0302 (p227), fig_0303 (p228), fig_0304 (p229), fig_0305 (p229), fig_0306 (p231), fig_0307 (p232), fig_0308 (p232), fig_0309 (p233), fig_0310 (p233), fig_0311 (p234), fig_0312 (p235), fig_0313 (p236), fig_0314 (p237), fig_0315 (p238), fig_0316 (p238), fig_0317 (p239), fig_0318 (p242), fig_0319 (p244), fig_0320 (p245), fig_0321 (p246), fig_0322 (p246), fig_0323 (p247), fig_0324 (p248), fig_0325 (p248), fig_0326 (p250), fig_0327 (p251), fig_0328 (p252), fig_0329 (p253), fig_0330 (p254), fig_0331 (p254), fig_0332 (p255), fig_0333 (p255), fig_0334 (p256), fig_0335 (p256), fig_0336 (p256), fig_0337 (p257), fig_0338 (p257), fig_0339 (p257), fig_0340 (p258), fig_0341 (p258), fig_0342 (p259), fig_0343 (p260), fig_0344 (p260), fig_0345 (p261), fig_0346 (p261), fig_0349 (p265), fig_0368 (p284), fig_0369 (p285), fig_0370 (p287), fig_0371 (p287), fig_0373 (p289), fig_0374 (p290), fig_0377 (p293), fig_0378 (p293), fig_0385 (p298), fig_0391 (p301), fig_0392 (p301), fig_0437 (p333), fig_0454 (p345), fig_0467 (p353)
- **VIII. Multi-Agent** — 28 figures: fig_0058 (p40), fig_0059 (p40), fig_0087 (p63), fig_0208 (p159), fig_0235 (p184), fig_0236 (p185), fig_0238 (p185), fig_0242 (p186), fig_0243 (p187), fig_0244 (p187), fig_0245 (p187), fig_0252 (p190), fig_0254 (p191), fig_0255 (p191), fig_0256 (p191), fig_0257 (p191), fig_0258 (p192), fig_0262 (p196), fig_0263 (p196), fig_0267 (p199), fig_0272 (p202), fig_0274 (p203), fig_0309 (p233), fig_0310 (p233), fig_0313 (p236), fig_0318 (p242), fig_0327 (p251), fig_0437 (p333)
- **IX. Agent Memory** — 39 figures: fig_0055 (p38), fig_0080 (p57), fig_0090 (p67), fig_0095 (p71), fig_0096 (p71), fig_0102 (p74), fig_0103 (p75), fig_0104 (p75), fig_0133 (p95), fig_0141 (p105), fig_0159 (p114), fig_0193 (p143), fig_0196 (p148), fig_0198 (p150), fig_0200 (p152), fig_0201 (p153), fig_0202 (p153), fig_0206 (p157), fig_0211 (p162), fig_0260 (p194), fig_0261 (p195), fig_0262 (p196), fig_0263 (p196), fig_0264 (p197), fig_0265 (p197), fig_0266 (p198), fig_0320 (p245), fig_0394 (p304), fig_0397 (p306), fig_0404 (p311), fig_0405 (p311), fig_0412 (p316), fig_0418 (p320), fig_0419 (p320), fig_0420 (p321), fig_0421 (p321), fig_0473 (p361), fig_0480 (p366), fig_0481 (p366)
- **X. Agent Orchestration** — 17 figures: fig_0058 (p40), fig_0059 (p40), fig_0207 (p158), fig_0231 (p180), fig_0235 (p184), fig_0242 (p186), fig_0243 (p187), fig_0244 (p187), fig_0272 (p202), fig_0274 (p203), fig_0312 (p235), fig_0315 (p238), fig_0317 (p239), fig_0318 (p242), fig_0324 (p248), fig_0325 (p248), fig_0326 (p250)
- **XI. n8n / Workflow Automation** — 15 figures: fig_0153 (p112), fig_0154 (p112), fig_0166 (p117), fig_0174 (p122), fig_0178 (p127), fig_0215 (p166), fig_0216 (p166), fig_0217 (p168), fig_0317 (p239), fig_0368 (p284), fig_0380 (p294), fig_0384 (p297), fig_0392 (p301), fig_0495 (p376), fig_0496 (p376)
- **XII. Agent Protocol Fabric** — 184 figures: fig_0007 (p0), fig_0008 (p0), fig_0009 (p6), fig_0010 (p6), fig_0011 (p7), fig_0012 (p7), fig_0024 (p18), fig_0027 (p20), fig_0035 (p26), fig_0047 (p32), fig_0051 (p34), fig_0052 (p35), fig_0061 (p42), fig_0062 (p42), fig_0065 (p45), fig_0075 (p54), fig_0082 (p59), fig_0083 (p61), fig_0087 (p63), fig_0090 (p67), fig_0102 (p74), fig_0104 (p75), fig_0110 (p79), fig_0111 (p79), fig_0113 (p81), fig_0114 (p82), fig_0116 (p83), fig_0127 (p90), fig_0135 (p97), fig_0139 (p101), fig_0140 (p102), fig_0170 (p120), fig_0172 (p121), fig_0174 (p122), fig_0179 (p128), fig_0191 (p139), fig_0197 (p149), fig_0199 (p151), fig_0209 (p160), fig_0210 (p161), fig_0211 (p162), fig_0212 (p163), fig_0213 (p164), fig_0217 (p168), fig_0220 (p173), fig_0229 (p179), fig_0236 (p185), fig_0237 (p185), fig_0238 (p185), fig_0239 (p185), fig_0240 (p186), fig_0241 (p186), fig_0244 (p187), fig_0245 (p187), fig_0246 (p188), fig_0247 (p188), fig_0248 (p188), fig_0249 (p189), fig_0250 (p189), fig_0251 (p189), fig_0252 (p190), fig_0253 (p190), fig_0259 (p193), fig_0270 (p201), fig_0276 (p205), fig_0277 (p206), fig_0278 (p207), fig_0312 (p235), fig_0313 (p236), fig_0314 (p237), fig_0315 (p238), fig_0316 (p238), fig_0319 (p244), fig_0320 (p245), fig_0321 (p246), fig_0322 (p246), fig_0323 (p247), fig_0324 (p248), fig_0326 (p250), fig_0328 (p252), fig_0329 (p253), fig_0330 (p254), fig_0332 (p255), fig_0333 (p255), fig_0334 (p256), fig_0341 (p258), fig_0343 (p260), fig_0344 (p260), fig_0345 (p261), fig_0346 (p261), fig_0347 (p264), fig_0348 (p264), fig_0349 (p265), fig_0350 (p266), fig_0351 (p267), fig_0352 (p268), fig_0353 (p269), fig_0354 (p270), fig_0355 (p270), fig_0356 (p271), fig_0357 (p272), fig_0358 (p273), fig_0359 (p274), fig_0360 (p276), fig_0361 (p278), fig_0362 (p278), fig_0363 (p278), fig_0364 (p279), fig_0365 (p279), fig_0366 (p280), fig_0367 (p282), fig_0368 (p284), fig_0369 (p285), fig_0370 (p287), fig_0371 (p287), fig_0372 (p289), fig_0373 (p289), fig_0374 (p290), fig_0375 (p291), fig_0376 (p292), fig_0377 (p293), fig_0378 (p293), fig_0379 (p294), fig_0380 (p294), fig_0381 (p295), fig_0382 (p295), fig_0383 (p296), fig_0384 (p297), fig_0385 (p298), fig_0386 (p299), fig_0387 (p299), fig_0388 (p299), fig_0389 (p300), fig_0390 (p300), fig_0391 (p301), fig_0392 (p301), fig_0403 (p310), fig_0408 (p313), fig_0436 (p333), fig_0439 (p335), fig_0440 (p336), fig_0445 (p339), fig_0446 (p339), fig_0447 (p340), fig_0448 (p341), fig_0449 (p341), fig_0450 (p342), fig_0451 (p343), fig_0452 (p344), fig_0453 (p345), fig_0454 (p345), fig_0455 (p346), fig_0456 (p346), fig_0457 (p347), fig_0463 (p350), fig_0464 (p350), fig_0468 (p353), fig_0469 (p354), fig_0470 (p355), fig_0471 (p355), fig_0472 (p356), fig_0473 (p361), fig_0474 (p362), fig_0475 (p362), fig_0476 (p363), fig_0477 (p363), fig_0478 (p364), fig_0479 (p365), fig_0480 (p366), fig_0481 (p366), fig_0483 (p367), fig_0484 (p368), fig_0486 (p371), fig_0487 (p371), fig_0497 (p377), fig_0498 (p377), fig_0499 (p377), fig_0500 (p378), fig_0501 (p378), fig_0504 (p380), fig_0505 (p380), fig_0506 (p381), fig_0507 (p381), fig_0508 (p381)
- **XIII. Data Engineering** — 52 figures: fig_0049 (p33), fig_0055 (p38), fig_0087 (p63), fig_0091 (p68), fig_0104 (p75), fig_0122 (p88), fig_0123 (p88), fig_0124 (p88), fig_0125 (p89), fig_0126 (p89), fig_0141 (p105), fig_0142 (p106), fig_0143 (p107), fig_0144 (p107), fig_0145 (p108), fig_0149 (p110), fig_0150 (p110), fig_0151 (p111), fig_0152 (p111), fig_0155 (p113), fig_0156 (p113), fig_0157 (p113), fig_0158 (p114), fig_0159 (p114), fig_0161 (p115), fig_0162 (p115), fig_0163 (p116), fig_0165 (p117), fig_0166 (p117), fig_0189 (p136), fig_0192 (p141), fig_0209 (p160), fig_0216 (p166), fig_0218 (p170), fig_0219 (p171), fig_0220 (p173), fig_0221 (p173), fig_0234 (p183), fig_0269 (p200), fig_0296 (p222), fig_0326 (p250), fig_0343 (p260), fig_0344 (p260), fig_0351 (p267), fig_0353 (p269), fig_0359 (p274), fig_0382 (p295), fig_0412 (p316), fig_0416 (p319), fig_0482 (p367), fig_0483 (p367), fig_0484 (p368)
- **XIV. Tool / Action Fabric** — 110 figures: fig_0012 (p7), fig_0027 (p20), fig_0037 (p27), fig_0038 (p27), fig_0078 (p56), fig_0132 (p95), fig_0136 (p98), fig_0184 (p132), fig_0195 (p147), fig_0196 (p148), fig_0198 (p150), fig_0199 (p151), fig_0200 (p152), fig_0202 (p153), fig_0204 (p154), fig_0205 (p155), fig_0211 (p162), fig_0212 (p163), fig_0231 (p180), fig_0234 (p183), fig_0235 (p184), fig_0236 (p185), fig_0237 (p185), fig_0238 (p185), fig_0239 (p185), fig_0240 (p186), fig_0241 (p186), fig_0242 (p186), fig_0246 (p188), fig_0247 (p188), fig_0248 (p188), fig_0249 (p189), fig_0250 (p189), fig_0251 (p189), fig_0253 (p190), fig_0254 (p191), fig_0259 (p193), fig_0267 (p199), fig_0268 (p200), fig_0269 (p200), fig_0270 (p201), fig_0271 (p201), fig_0282 (p213), fig_0283 (p213), fig_0286 (p215), fig_0287 (p215), fig_0289 (p216), fig_0294 (p220), fig_0295 (p221), fig_0297 (p223), fig_0298 (p223), fig_0299 (p224), fig_0300 (p225), fig_0301 (p226), fig_0302 (p227), fig_0303 (p228), fig_0305 (p229), fig_0308 (p232), fig_0309 (p233), fig_0310 (p233), fig_0314 (p237), fig_0315 (p238), fig_0323 (p247), fig_0324 (p248), fig_0325 (p248), fig_0327 (p251), fig_0328 (p252), fig_0331 (p254), fig_0332 (p255), fig_0349 (p265), fig_0350 (p266), fig_0351 (p267), fig_0352 (p268), fig_0356 (p271), fig_0357 (p272), fig_0358 (p273), fig_0360 (p276), fig_0364 (p279), fig_0366 (p280), fig_0367 (p282), fig_0369 (p285), fig_0370 (p287), fig_0371 (p287), fig_0374 (p290), fig_0375 (p291), fig_0376 (p292), fig_0384 (p297), fig_0385 (p298), fig_0389 (p300), fig_0390 (p300), fig_0391 (p301), fig_0447 (p340), fig_0448 (p341), fig_0450 (p342), fig_0451 (p343), fig_0452 (p344), fig_0453 (p345), fig_0454 (p345), fig_0457 (p347), fig_0489 (p373), fig_0490 (p373), fig_0491 (p374), fig_0492 (p374), fig_0493 (p375), fig_0494 (p375), fig_0497 (p377), fig_0498 (p377), fig_0499 (p377), fig_0503 (p379), fig_0509 (p382)
- **XV. Security** — 15 figures: fig_0084 (p61), fig_0098 (p72), fig_0204 (p154), fig_0221 (p173), fig_0259 (p193), fig_0260 (p194), fig_0321 (p246), fig_0322 (p246), fig_0346 (p261), fig_0465 (p351), fig_0466 (p352), fig_0467 (p353), fig_0468 (p353), fig_0469 (p354), fig_0472 (p356)
- **XVI. Evaluation** — 98 figures: fig_0007 (p0), fig_0008 (p0), fig_0014 (p9), fig_0027 (p20), fig_0036 (p26), fig_0047 (p32), fig_0050 (p34), fig_0066 (p46), fig_0068 (p47), fig_0071 (p51), fig_0072 (p51), fig_0074 (p52), fig_0077 (p55), fig_0082 (p59), fig_0101 (p74), fig_0124 (p88), fig_0125 (p89), fig_0136 (p98), fig_0141 (p105), fig_0142 (p106), fig_0145 (p108), fig_0146 (p108), fig_0163 (p116), fig_0164 (p116), fig_0170 (p120), fig_0180 (p130), fig_0182 (p131), fig_0184 (p132), fig_0188 (p136), fig_0189 (p136), fig_0190 (p137), fig_0194 (p146), fig_0214 (p165), fig_0222 (p176), fig_0230 (p180), fig_0232 (p181), fig_0241 (p186), fig_0272 (p202), fig_0279 (p207), fig_0281 (p209), fig_0282 (p213), fig_0331 (p254), fig_0332 (p255), fig_0333 (p255), fig_0334 (p256), fig_0335 (p256), fig_0336 (p256), fig_0337 (p257), fig_0338 (p257), fig_0339 (p257), fig_0340 (p258), fig_0373 (p289), fig_0390 (p300), fig_0393 (p304), fig_0395 (p305), fig_0401 (p309), fig_0434 (p332), fig_0435 (p332), fig_0436 (p333), fig_0437 (p333), fig_0438 (p334), fig_0439 (p335), fig_0440 (p336), fig_0441 (p337), fig_0442 (p337), fig_0443 (p338), fig_0444 (p338), fig_0445 (p339), fig_0446 (p339), fig_0447 (p340), fig_0448 (p341), fig_0449 (p341), fig_0451 (p343), fig_0452 (p344), fig_0453 (p345), fig_0454 (p345), fig_0455 (p346), fig_0456 (p346), fig_0457 (p347), fig_0458 (p347), fig_0459 (p348), fig_0460 (p349), fig_0461 (p349), fig_0462 (p349), fig_0463 (p350), fig_0464 (p350), fig_0465 (p351), fig_0466 (p352), fig_0467 (p353), fig_0468 (p353), fig_0469 (p354), fig_0470 (p355), fig_0471 (p355), fig_0472 (p356), fig_0486 (p371), fig_0487 (p371), fig_0507 (p381), fig_0509 (p382)
- **XVII. Observability** — 59 figures: fig_0029 (p21), fig_0034 (p25), fig_0036 (p26), fig_0048 (p33), fig_0052 (p35), fig_0060 (p41), fig_0068 (p47), fig_0070 (p50), fig_0071 (p51), fig_0072 (p51), fig_0089 (p66), fig_0093 (p69), fig_0094 (p70), fig_0112 (p80), fig_0167 (p118), fig_0173 (p121), fig_0185 (p133), fig_0228 (p179), fig_0271 (p201), fig_0317 (p239), fig_0340 (p258), fig_0396 (p306), fig_0415 (p318), fig_0417 (p319), fig_0427 (p326), fig_0428 (p326), fig_0446 (p339), fig_0455 (p346), fig_0456 (p346), fig_0460 (p349), fig_0461 (p349), fig_0465 (p351), fig_0470 (p355), fig_0471 (p355), fig_0485 (p370), fig_0486 (p371), fig_0487 (p371), fig_0488 (p372), fig_0489 (p373), fig_0490 (p373), fig_0491 (p374), fig_0492 (p374), fig_0493 (p375), fig_0494 (p375), fig_0495 (p376), fig_0496 (p376), fig_0497 (p377), fig_0498 (p377), fig_0499 (p377), fig_0500 (p378), fig_0501 (p378), fig_0502 (p379), fig_0503 (p379), fig_0504 (p380), fig_0505 (p380), fig_0506 (p381), fig_0507 (p381), fig_0508 (p381), fig_0509 (p382)
- **XVIII. Reliability** — 5 figures: fig_0127 (p90), fig_0128 (p91), fig_0129 (p91), fig_0134 (p96), fig_0362 (p278)
- **XIX. Infrastructure** — 134 figures: fig_0016 (p11), fig_0019 (p13), fig_0061 (p42), fig_0062 (p42), fig_0083 (p61), fig_0086 (p63), fig_0090 (p67), fig_0099 (p73), fig_0100 (p73), fig_0114 (p82), fig_0115 (p82), fig_0127 (p90), fig_0128 (p91), fig_0129 (p91), fig_0133 (p95), fig_0139 (p101), fig_0140 (p102), fig_0145 (p108), fig_0146 (p108), fig_0170 (p120), fig_0173 (p121), fig_0246 (p188), fig_0247 (p188), fig_0248 (p188), fig_0249 (p189), fig_0250 (p189), fig_0251 (p189), fig_0252 (p190), fig_0253 (p190), fig_0263 (p196), fig_0321 (p246), fig_0342 (p259), fig_0344 (p260), fig_0346 (p261), fig_0350 (p266), fig_0354 (p270), fig_0355 (p270), fig_0356 (p271), fig_0357 (p272), fig_0360 (p276), fig_0364 (p279), fig_0365 (p279), fig_0367 (p282), fig_0368 (p284), fig_0369 (p285), fig_0370 (p287), fig_0371 (p287), fig_0372 (p289), fig_0373 (p289), fig_0374 (p290), fig_0375 (p291), fig_0376 (p292), fig_0377 (p293), fig_0378 (p293), fig_0379 (p294), fig_0380 (p294), fig_0381 (p295), fig_0382 (p295), fig_0383 (p296), fig_0384 (p297), fig_0385 (p298), fig_0386 (p299), fig_0387 (p299), fig_0388 (p299), fig_0389 (p300), fig_0390 (p300), fig_0391 (p301), fig_0392 (p301), fig_0393 (p304), fig_0394 (p304), fig_0395 (p305), fig_0396 (p306), fig_0397 (p306), fig_0398 (p307), fig_0399 (p308), fig_0400 (p308), fig_0401 (p309), fig_0402 (p310), fig_0403 (p310), fig_0404 (p311), fig_0405 (p311), fig_0406 (p312), fig_0407 (p312), fig_0408 (p313), fig_0409 (p314), fig_0410 (p315), fig_0411 (p315), fig_0412 (p316), fig_0413 (p318), fig_0414 (p318), fig_0415 (p318), fig_0416 (p319), fig_0417 (p319), fig_0418 (p320), fig_0419 (p320), fig_0420 (p321), fig_0421 (p321), fig_0422 (p322), fig_0423 (p323), fig_0424 (p324), fig_0425 (p324), fig_0426 (p325), fig_0427 (p326), fig_0428 (p326), fig_0429 (p327), fig_0430 (p327), fig_0431 (p328), fig_0432 (p328), fig_0433 (p329), fig_0440 (p336), fig_0448 (p341), fig_0449 (p341), fig_0450 (p342), fig_0451 (p343), fig_0453 (p345), fig_0459 (p348), fig_0460 (p349), fig_0461 (p349), fig_0462 (p349), fig_0463 (p350), fig_0473 (p361), fig_0474 (p362), fig_0475 (p362), fig_0476 (p363), fig_0477 (p363), fig_0478 (p364), fig_0479 (p365), fig_0480 (p366), fig_0481 (p366), fig_0482 (p367), fig_0483 (p367), fig_0484 (p368), fig_0486 (p371), fig_0487 (p371)
- **XX. AI Development / Coding** — 0 figures: —
- **XXI. Business Automation** — 21 figures: fig_0053 (p36), fig_0057 (p40), fig_0078 (p56), fig_0086 (p63), fig_0092 (p69), fig_0101 (p74), fig_0146 (p108), fig_0153 (p112), fig_0185 (p133), fig_0217 (p168), fig_0233 (p182), fig_0322 (p246), fig_0350 (p266), fig_0393 (p304), fig_0394 (p304), fig_0402 (p310), fig_0463 (p350), fig_0476 (p363), fig_0488 (p372), fig_0491 (p374), fig_0502 (p379)
- **XXII. Agentic Commerce** — 0 figures: —
- **XXIII. Product Engine** — 0 figures: —
- **XXIV. Revenue Engine** — 0 figures: —
- **XXV. Opportunity Engine** — 0 figures: —
- **XXVI. Agent Portfolio** — 0 figures: —
- **XXVII. Autonomous Self-Improvement** — 0 figures: —
- **XXVIII. Meta-Layer** — 0 figures: —

## 8. Chapter map

| Chapter | Figures | Page range |
| --- | --- | --- |
| Front Matter | 8 | 0–0 |
| LLMs | 60 | 6–47 |
| Prompt Engineering | 20 | 49–64 |
| Fine-tuning | 52 | 66–102 |
| RAG | 53 | 105–143 |
| Context Engineering | 28 | 146–173 |
| AI Agents | 125 | 176–261 |
| MCP | 46 | 264–301 |
| LLM Optimization | 41 | 304–329 |
| LLM Evaluation | 39 | 332–356 |
| LLM Deployment | 12 | 361–368 |
| LLM Observability | 25 | 370–382 |

## 9. Duplicate groups

22 groups contain more than one figure (grouped, never deleted).

| Group | Count | Members |
| --- | --- | --- |
| dup_0012 | 2 | fig_0012 p7, fig_0020 p14 |
| dup_0013 | 2 | fig_0013 p8, fig_0019 p13 |
| dup_0061 | 2 | fig_0063 p44, fig_0424 p324 |
| dup_0073 | 2 | fig_0075 p54, fig_0315 p238 |
| dup_0087 | 2 | fig_0089 p66, fig_0093 p69 |
| dup_0101 | 2 | fig_0104 p75, fig_0412 p316 |
| dup_0103 | 2 | fig_0106 p77, fig_0111 p79 |
| dup_0162 | 2 | fig_0166 p117, fig_0194 p146 |
| dup_0174 | 2 | fig_0178 p127, fig_0189 p136 |
| dup_0176 | 2 | fig_0180 p130, fig_0182 p131 |
| dup_0182 | 2 | fig_0187 p135, fig_0188 p136 |
| dup_0187 | 2 | fig_0195 p147, fig_0207 p158 |
| dup_0227 | 3 | fig_0236 p185, fig_0247 p188, fig_0389 p300 |
| dup_0274 | 7 | fig_0284 p214, fig_0285 p214, fig_0286 p215, fig_0288 p216, fig_0289 p216, fig_0291 p217, fig_0292 p218 |
| dup_0275 | 2 | fig_0287 p215, fig_0290 p217 |
| dup_0298 | 2 | fig_0316 p238, fig_0319 p244 |
| dup_0305 | 2 | fig_0324 p248, fig_0328 p252 |
| dup_0384 | 2 | fig_0405 p311, fig_0407 p312 |
| dup_0386 | 2 | fig_0408 p313, fig_0409 p314 |
| dup_0391 | 2 | fig_0415 p318, fig_0416 p319 |
| dup_0455 | 2 | fig_0481 p366, fig_0483 p367 |
| dup_0464 | 2 | fig_0491 p374, fig_0492 p374 |

## 10. Statistics

**By composition**

| Value | Figures | Share |
| --- | --- | --- |
| raster | 504 | 99.0% |
| hybrid | 5 | 1.0% |

**By role**

| Value | Figures | Share |
| --- | --- | --- |
| architecture | 114 | 22.4% |
| diagram | 90 | 17.7% |
| code | 87 | 17.1% |
| process | 66 | 13.0% |
| result | 64 | 12.6% |
| concept | 62 | 12.2% |
| comparison | 26 | 5.1% |

**By primaryBranch**

| Value | Figures | Share |
| --- | --- | --- |
| ai-ml-foundation | 123 | 24.2% |
| agentic-ai | 91 | 17.9% |
| agent-protocol-fabric | 70 | 13.8% |
| rag-knowledge-engineering | 58 | 11.4% |
| evaluation | 39 | 7.7% |
| infrastructure | 37 | 7.3% |
| llm-engineering | 32 | 6.3% |
| context-engineering | 20 | 3.9% |
| tool-action-fabric | 15 | 2.9% |
| observability | 14 | 2.8% |
| data-engineering | 4 | 0.8% |
| agent-memory | 4 | 0.8% |
| multi-agent | 1 | 0.2% |
| business-automation | 1 | 0.2% |

**Confidence bands**

| Band | Figures |
| --- | --- |
| auto-accept (≥0.85) | 159 |
| review queue (0.5–0.85) | 350 |
| weak (<0.5) | 0 |

**Coverage:** 1276 of 5070 node-dimensions answered.
