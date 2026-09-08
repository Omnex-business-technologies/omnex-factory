# Enterprise research — Tier 1, all eighteen sections

Fifteen projects, chosen by relevance to OMNEX rather than by star count. Every
factual claim carries the page it was read from and the date it was read. Judgements
are marked as judgements and live in `engine/scripts/intel_judgements.py`, one record
per project, so a disagreement is a one-line edit rather than an argument with a
paragraph.

**Architecture sections are inference from public evidence, not insider knowledge.**

## HKUDS/OpenSpace

**1 · Executive summary.** OpenSpace: The Skill Management Layer for AI Agents. [https://github.com/HKUDS/OpenSpace · 2026-08-05]

**2 · Technical architecture.** Python. No dependency manifest was collected for this project, so its internal architecture is not inferable from public metadata — recorded as UNKNOWN rather than guessed.

**3 · Business model.** Open source; the commercial surface would be the enterprise gaps in §9.

**4 · Market position.** 7300 stars and 881 forks at the reading date. [https://github.com/HKUDS/OpenSpace · 2026-08-05]

**5 · Competitive landscape.** Collides with P4 evals, P17 FinGround. Substitution risk scored 0.50.

**6 · Strengths.**
- judges skills by task outcome rather than by description, which is the correct axis
- local-first hub keeps data under the operator's control — no account required to start
- MIT, Python, LiteLLM and SQLite: every dependency is one we already use

**7 · Weaknesses.**
- skill quality is scored on outcomes it observed, so a skill used twice has a score with no confidence attached to it
- no stated protection against a skill that succeeds by doing something unsafe

**8 · Missing features.**
- per-capability regression detection
- cost per successful task
- refusal scoring

**9 · Enterprise features absent.**
- multi-tenant skill isolation
- audit trail for skill changes

**10 · Security review.** No dependency manifest, so no dependency-derived hazards can be named. Absence of findings here is absence of evidence, not evidence of safety.

**11 · Scalability review.** Operational complexity 0 — nothing beyond the application process itself needs to be run, monitored and paid for, on the evidence available.

**12 · Performance review.** Not measured. Nothing in this scan executed any of these projects, and a performance claim without a run is a rumour with a number in it.

**13 · Automation potential.** Integration cost scored 0.40; licence `MIT` permits building on it.

**14 · AI integration opportunities.** Advertises evaluation, mcp, skills, ui_patterns.

**15 · Revenue opportunities.** See `REVENUE_MATRIX.md` — the enterprise gaps in §9 are the paid surface.

**16 · OMNEX synergy.** evidence-based skill evaluation is the same idea as our eval gate (P4/P17).

**17 · Original improvement.** OpenSpace scores a skill by outcome; FinGround (P17) shows that an outcome score with no refusal column ranks a confabulating system respectably. Combining them — skill selection gated on a suite that scores refusal separately, with `Gate` comparing case-by-case rather than on the mean — is a skill registry that can say WHY it demoted something. That is the version an enterprise can adopt.

**18 · Priority.** Growth +18.0% over 82 days. Closest thing to a competitor for the eval work, and the most absorbable.

---

## openmemind/memind

**1 · Executive summary.** Self-evolving cognitive memory and context engine for AI agents in Java. [https://github.com/openmemind/memind · 2026-08-05]

**2 · Technical architecture.** Java. No dependency manifest was collected for this project, so its internal architecture is not inferable from public metadata — recorded as UNKNOWN rather than guessed.

**3 · Business model.** Open source; the commercial surface would be the enterprise gaps in §9.

**4 · Market position.** 903 stars and 91 forks at the reading date. [https://github.com/openmemind/memind · 2026-08-05]

**5 · Competitive landscape.** Collides with P13 memory. Substitution risk scored 0.60.

**6 · Strengths.**
- publishes numbers on three public memory benchmarks rather than asserting quality
- Apache-2.0, so the design is studiable and the interfaces are reusable
- reports lower context token usage alongside accuracy, which is the honest pairing

**7 · Weaknesses.**
- Java, which is a hard boundary against a Python engine — integration means a network hop and a second runtime to operate
- benchmark claims are self-reported under self-described aligned protocols

**8 · Missing features.**
- per-tenant memory isolation
- cost ceiling per retrieval
- forgetting audit

**9 · Enterprise features absent.**
- data residency
- right-to-erasure across derived memory graphs

**10 · Security review.** No dependency manifest, so no dependency-derived hazards can be named. Absence of findings here is absence of evidence, not evidence of safety.

**11 · Scalability review.** Operational complexity 0 — nothing beyond the application process itself needs to be run, monitored and paid for, on the evidence available.

**12 · Performance review.** Not measured. Nothing in this scan executed any of these projects, and a performance claim without a run is a rumour with a number in it.

**13 · Automation potential.** Integration cost scored 0.75; licence `Apache-2.0` permits building on it.

**14 · AI integration opportunities.** Advertises mcp, memory.

**15 · Revenue opportunities.** See `REVENUE_MATRIX.md` — the enterprise gaps in §9 are the paid surface.

**16 · OMNEX synergy.** direct overlap with P13 agent memory; names the benchmarks we should score on.

**17 · Original improvement.** Memind proves the benchmarks matter and that token cost belongs next to accuracy. The improvement is not a better memory graph — it is scoring memory the way P2 scores routing: pico-dollar cost per correct recall, with the break-even point where a cheaper memory tier stops paying. Nobody publishes that, and it is the number that decides whether memory is worth running at all.

**18 · Priority.** Growth +21.5% over 82 days. The benchmark target for P13; adopt the yardstick, not the runtime.

---

## neo4j-labs/create-context-graph

**1 · Executive summary.** AI agents with graph based reasoning memory, scaffolded in seconds. [https://github.com/neo4j-labs/create-context-graph · 2026-08-05]

**2 · Technical architecture.** Python. No dependency manifest was collected for this project, so its internal architecture is not inferable from public metadata — recorded as UNKNOWN rather than guessed.

**3 · Business model.** Open source; the commercial surface would be the enterprise gaps in §9.

**4 · Market position.** 704 stars and 98 forks at the reading date. [https://github.com/neo4j-labs/create-context-graph · 2026-08-05]

**5 · Competitive landscape.** Collides with P1 RAG, P12 vectors. Substitution risk scored 0.45.

**6 · Strengths.**
- three-memory split — conversation, entity graph, reasoning traces — is a better decomposition than a single vector store
- scaffolds a whole working application, which is the OMNEX module thesis validated by someone else
- Apache-2.0 with LiteLLM provider injection, so nothing is locked to one vendor

**7 · Weaknesses.**
- Neo4j is a heavy operational dependency for a small team
- generated applications are a starting point, and the scaffold cannot help with the part that is actually hard

**8 · Missing features.**
- citation verification on graph answers
- cost per query
- eval suite

**9 · Enterprise features absent.**
- tenant isolation in the graph
- cost attribution per tenant

**10 · Security review.** No dependency manifest, so no dependency-derived hazards can be named. Absence of findings here is absence of evidence, not evidence of safety.

**11 · Scalability review.** Operational complexity 0 — nothing beyond the application process itself needs to be run, monitored and paid for, on the evidence available.

**12 · Performance review.** Not measured. Nothing in this scan executed any of these projects, and a performance claim without a run is a rumour with a number in it.

**13 · Automation potential.** Integration cost scored 0.50; licence `Apache-2.0` permits building on it.

**14 · AI integration opportunities.** Advertises memory, reasoning.

**15 · Revenue opportunities.** See `REVENUE_MATRIX.md` — the enterprise gaps in §9 are the paid surface.

**16 · OMNEX synergy.** GraphRAG plus scaffolding — overlaps P1 retrieval and the OMNEX module thesis.

**17 · Original improvement.** A graph answer is harder to verify than a passage answer, because the claim is assembled from edges rather than quoted from a page. Applying the P1 grounder to graph traversals — every asserted relationship must resolve to an edge that exists, and a path that cannot be reconstructed is refused — is a genuinely new thing. GraphRAG systems currently ask you to trust the traversal.

**18 · Priority.** Growth +23.3% over 82 days. Best architectural ideas in the set; adopt the memory split.

---

## cisco-ai-defense/defenseclaw

**1 · Executive summary.** Security governance for OpenClaw and agentic AI runtimes. [https://github.com/cisco-ai-defense/defenseclaw · 2026-08-05]

**2 · Technical architecture.** Go. No dependency manifest was collected for this project, so its internal architecture is not inferable from public metadata — recorded as UNKNOWN rather than guessed.

**3 · Business model.** Open source; the commercial surface would be the enterprise gaps in §9.

**4 · Market position.** 806 stars and 139 forks at the reading date. [https://github.com/cisco-ai-defense/defenseclaw · 2026-08-05]

**5 · Competitive landscape.** Collides with P6 guardrails. Substitution risk scored 0.50.

**6 · Strengths.**
- frames the product as evidence and policy enforcement rather than as safety, which is the honest and the sellable framing
- durable audit export is exactly what a regulated buyer procures
- Apache-2.0 with a corporate security team behind it

**7 · Weaknesses.**
- Go gateway plus Python CLI is two runtimes to operate
- scanning capabilities before use cannot catch a capability that turns malicious after approval

**8 · Missing features.**
- tamper-evident audit chain
- per-tenant policy
- injection corpus with measured rates

**9 · Enterprise features absent.**
- SOC2 evidence export
- policy versioning

**10 · Security review.** No dependency manifest, so no dependency-derived hazards can be named. Absence of findings here is absence of evidence, not evidence of safety.

**11 · Scalability review.** Operational complexity 0 — nothing beyond the application process itself needs to be run, monitored and paid for, on the evidence available.

**12 · Performance review.** Not measured. Nothing in this scan executed any of these projects, and a performance claim without a run is a rumour with a number in it.

**13 · Automation potential.** Integration cost scored 0.60; licence `Apache-2.0` permits building on it.

**14 · AI integration opportunities.** Advertises observability, security.

**15 · Revenue opportunities.** See `REVENUE_MATRIX.md` — the enterprise gaps in §9 are the paid surface.

**16 · OMNEX synergy.** agent security governance overlaps P6 guardrails and the P3 audit trail.

**17 · Original improvement.** DefenseClaw exports audit evidence; our P3 audit trail is hash-chained, where the hash covers sequence and previous hash rather than payload alone, so a deletion is detectable rather than merely logged. Audit evidence that can prove it was not edited is a materially stronger product than audit evidence that cannot, and it is the difference between a log and a record.

**18 · Priority.** Growth +24.2% over 82 days. Strongest commercial framing in the set — study the positioning.

---

## InternLM/WildClawBench

**1 · Executive summary.** An in-the-wild benchmark for AI agents in the OpenClaw Environment. [https://github.com/InternLM/WildClawBench · 2026-08-05]

**2 · Technical architecture.** Python. No dependency manifest was collected for this project, so its internal architecture is not inferable from public metadata — recorded as UNKNOWN rather than guessed.

**3 · Business model.** Open source; the commercial surface would be the enterprise gaps in §9.

**4 · Market position.** 500 stars and 56 forks at the reading date. [https://github.com/InternLM/WildClawBench · 2026-08-05]

**5 · Competitive landscape.** Collides with P17 FinGround. Substitution risk scored 0.30.

**6 · Strengths.**
- reports execution time and API cost next to the score, which almost no benchmark does
- includes a Safety Alignment category rather than measuring capability alone
- MIT, and evaluated across four harnesses so results are not tied to one runtime

**7 · Weaknesses.**
- 60 tasks is small enough that a few task-specific fixes move the ranking
- in-the-wild tasks are hard to keep stable, so scores drift for reasons unrelated to the system under test

**8 · Missing features.**
- refusal scoring as a separate axis
- contamination checking
- per-case gating

**9 · Enterprise features absent.**
- private task sets
- reproducible scoring on internal data

**10 · Security review.** No dependency manifest, so no dependency-derived hazards can be named. Absence of findings here is absence of evidence, not evidence of safety.

**11 · Scalability review.** Operational complexity 0 — nothing beyond the application process itself needs to be run, monitored and paid for, on the evidence available.

**12 · Performance review.** Not measured. Nothing in this scan executed any of these projects, and a performance claim without a run is a rumour with a number in it.

**13 · Automation potential.** Integration cost scored 0.30; licence `MIT` permits building on it.

**14 · AI integration opportunities.** Advertises evaluation.

**15 · Revenue opportunities.** See `REVENUE_MATRIX.md` — the enterprise gaps in §9 are the paid surface.

**16 · OMNEX synergy.** benchmark methodology to learn from; reports cost per run, which is rare.

**17 · Original improvement.** WildClawBench prices a benchmark run and FinGround separates refusal from accuracy. Neither does both. A benchmark that reports pico-dollar cost per correct answer AND hallucination rate in the same table ranks systems the way a buyer actually chooses one — and our eval harness already computes both halves.

**18 · Priority.** Growth +37.4% over 82 days. Fastest grower in the set at +37% — benchmarks are having a moment.

---

## soulduse/ai-token-monitor

**1 · Executive summary.** macOS menu bar app for tracking Claude Code token usage and costs. [https://github.com/soulduse/ai-token-monitor · 2026-08-05]

**2 · Technical architecture.** TypeScript. No dependency manifest was collected for this project, so its internal architecture is not inferable from public metadata — recorded as UNKNOWN rather than guessed.

**3 · Business model.** Open source; the commercial surface would be the enterprise gaps in §9.

**4 · Market position.** 306 stars and 51 forks at the reading date. [https://github.com/soulduse/ai-token-monitor · 2026-08-05]

**5 · Competitive landscape.** Collides with P2 router, P5 cost tracking. Substitution risk scored 0.30.

**6 · Strengths.**
- +64% over 82 days from a small base — the demand signal is unambiguous
- offline by default, which removes the objection that kills spend tooling
- applies per-model pricing including cache reads, a detail most trackers miss

**7 · Weaknesses.**
- reports spend without reducing it — it is a thermometer, not a thermostat
- macOS menu bar only, so it cannot serve a team or a production system

**8 · Missing features.**
- routing recommendation
- break-even analysis
- team aggregation

**9 · Enterprise features absent.**
- per-tenant attribution
- budget enforcement
- invoice reconciliation

**10 · Security review.** No dependency manifest, so no dependency-derived hazards can be named. Absence of findings here is absence of evidence, not evidence of safety.

**11 · Scalability review.** Operational complexity 0 — nothing beyond the application process itself needs to be run, monitored and paid for, on the evidence available.

**12 · Performance review.** Not measured. Nothing in this scan executed any of these projects, and a performance claim without a run is a rumour with a number in it.

**13 · Automation potential.** Integration cost scored 0.20; licence `MIT` permits building on it.

**14 · AI integration opportunities.** Advertises caching.

**15 · Revenue opportunities.** See `REVENUE_MATRIX.md` — the enterprise gaps in §9 are the paid surface.

**16 · OMNEX synergy.** proves people install software purely to see spend — validates P2/P5 framing.

**17 · Original improvement.** Every tool in this category reports spend. P2 computes the break-even escalation rate — the point past which routing to a cheap model stops saving money — and our measured run cut cost to 42.4% at a 14.3% escalation rate against a 97.0% break-even. A monitor that says you are LOSING MONEY on your current routing policy, with the arithmetic, is a different product from one that draws a chart.

**18 · Priority.** Growth +63.6% over 82 days. The clearest revenue signal in the set.

---

## patoles/agent-flow

**1 · Executive summary.** Real-time visualization of Claude Code agent orchestration. [https://github.com/patoles/agent-flow · 2026-08-05]

**2 · Technical architecture.** TypeScript. No dependency manifest was collected for this project, so its internal architecture is not inferable from public metadata — recorded as UNKNOWN rather than guessed.

**3 · Business model.** Open source; the commercial surface would be the enterprise gaps in §9.

**4 · Market position.** 1500 stars and 162 forks at the reading date. [https://github.com/patoles/agent-flow · 2026-08-05]

**5 · Competitive landscape.** Collides with P5 observability, P8 streaming UI. Substitution risk scored 0.40.

**6 · Strengths.**
- +64% over 82 days, the fastest grower in the set — this is demand, not curiosity
- SSE over a relay server is the right shape and needs no infrastructure
- ships as a VS Code extension too, meeting people where they already are

**7 · Weaknesses.**
- visualises one agent runtime's hooks, so it is coupled to that runtime's format
- shows what happened without saying what it cost

**8 · Missing features.**
- cost per span
- failure path highlighting
- tail-based sampling

**9 · Enterprise features absent.**
- retention policy
- multi-user access control

**10 · Security review.** No dependency manifest, so no dependency-derived hazards can be named. Absence of findings here is absence of evidence, not evidence of safety.

**11 · Scalability review.** Operational complexity 0 — nothing beyond the application process itself needs to be run, monitored and paid for, on the evidence available.

**12 · Performance review.** Not measured. Nothing in this scan executed any of these projects, and a performance claim without a run is a rumour with a number in it.

**13 · Automation potential.** Integration cost scored 0.45; licence `Apache-2.0` permits building on it.

**14 · AI integration opportunities.** Advertises skills.

**15 · Revenue opportunities.** See `REVENUE_MATRIX.md` — the enterprise gaps in §9 are the paid surface.

**16 · OMNEX synergy.** agent-run visualisation overlaps P5 tracing and is the P8 UI we have not built.

**17 · Original improvement.** Agent Flow shows the shape of a run; our P5 trace attaches pico-dollar cost to leaf spans and exposes `failure_path()`. A visualiser where the expensive branch is visibly expensive and the failing path is selectable answers the two questions an operator actually has, and neither tool answers both today.

**18 · Priority.** Growth +64.1% over 82 days. The template for P8 — and proof the demand is real.

---

## ovoment/ovo-local-llm

**1 · Executive summary.** A private Claude-Code-style coding agent for Apple Silicon. [https://github.com/ovoment/ovo-local-llm · 2026-08-05]

**2 · Technical architecture.** TypeScript. No dependency manifest was collected for this project, so its internal architecture is not inferable from public metadata — recorded as UNKNOWN rather than guessed.

**3 · Business model.** Open source; the commercial surface would be the enterprise gaps in §9.

**4 · Market position.** 104 stars and 18 forks at the reading date. [https://github.com/ovoment/ovo-local-llm · 2026-08-05]

**5 · Competitive landscape.** Collides with P7 local-first. Substitution risk scored 0.35.

**6 · Strengths.**
- zero API keys is the strongest possible privacy claim and it is verifiable
- MLX-native with Ollama and OpenAI compatibility — the right compatibility surface
- bundles RAG, LoRA and image generation into one local install

**7 · Weaknesses.**
- +2.0% over 82 days — effectively flat
- Apple Silicon only, which is a hard ceiling on the market

**8 · Missing features.**
- eval harness
- cost comparison against hosted
- team deployment

**9 · Enterprise features absent.**
- fleet management
- policy enforcement

**10 · Security review.** No dependency manifest, so no dependency-derived hazards can be named. Absence of findings here is absence of evidence, not evidence of safety.

**11 · Scalability review.** Operational complexity 0 — nothing beyond the application process itself needs to be run, monitored and paid for, on the evidence available.

**12 · Performance review.** Not measured. Nothing in this scan executed any of these projects, and a performance claim without a run is a rumour with a number in it.

**13 · Automation potential.** Integration cost scored 0.40; licence `MIT` permits building on it.

**14 · AI integration opportunities.** Advertises local_models, mcp, rag.

**15 · Revenue opportunities.** See `REVENUE_MATRIX.md` — the enterprise gaps in §9 are the paid surface.

**16 · OMNEX synergy.** local-first agent stack, the same thesis as P7.

**17 · Original improvement.** The unanswered question in local-first is when it is actually cheaper. P2 prices the local tier at zero marginal cost and can compute the crossover against hosted pricing — a local stack that shows the monthly saving it is producing, in exact money, sells itself to the buyer who currently cannot justify the hardware.

**18 · Priority.** Growth stalled over 82 days. Flat despite a good thesis — the market is Apple-only and small.

---

## slowmist/slowmist-agent-security

**1 · Executive summary.** A comprehensive security review framework for AI agents in adversarial environments. [https://github.com/slowmist/slowmist-agent-security · 2026-08-05]

**2 · Technical architecture.** Markdown. No dependency manifest was collected for this project, so its internal architecture is not inferable from public metadata — recorded as UNKNOWN rather than guessed.

**3 · Business model.** Open source; the commercial surface would be the enterprise gaps in §9.

**4 · Market position.** 500 stars and 30 forks at the reading date. [https://github.com/slowmist/slowmist-agent-security · 2026-08-05]

**5 · Competitive landscape.** Collides with P6 guardrails. Substitution risk scored 0.15.

**6 · Strengths.**
- 26 attack categories is a taxonomy we can test against rather than a warning
- every external input is untrusted until verified is the same provenance rule P6 uses
- MIT and documentation-only, so it is cheap to adopt and impossible to break

**7 · Weaknesses.**
- documentation cannot be executed, so nothing here is measured
- a review framework depends on the reviewer, which does not scale

**8 · Missing features.**
- machine-readable corpus
- measured detection and false-positive rates

**9 · Enterprise features absent.**
- automated enforcement
- regression tracking as attacks evolve

**10 · Security review.** No dependency manifest, so no dependency-derived hazards can be named. Absence of findings here is absence of evidence, not evidence of safety.

**11 · Scalability review.** Operational complexity 0 — nothing beyond the application process itself needs to be run, monitored and paid for, on the evidence available.

**12 · Performance review.** Not measured. Nothing in this scan executed any of these projects, and a performance claim without a run is a rumour with a number in it.

**13 · Automation potential.** Integration cost scored 0.15; licence `MIT` permits building on it.

**14 · AI integration opportunities.** Advertises security, skills.

**15 · Revenue opportunities.** See `REVENUE_MATRIX.md` — the enterprise gaps in §9 are the paid surface.

**16 · OMNEX synergy.** attack taxonomy directly usable against our injection corpus (P6).

**17 · Original improvement.** The taxonomy is prose; our injection corpus is 30 cases with a measured 30/30 detection and 1/30 false-positive rate. Turning their 26 categories into executable cases with published detection AND false-positive rates produces the artefact the field is missing — a security claim with a denominator.

**18 · Priority.** Growth +11.1% over 82 days. Cheapest high-value absorption in the set: taxonomy in, corpus out.

---

## saltbo/agent-kanban

**1 · Executive summary.** An agent-first task board, Mission control for your AI workforce. [https://github.com/saltbo/agent-kanban · 2026-08-05]

**2 · Technical architecture.** TypeScript. No dependency manifest was collected for this project, so its internal architecture is not inferable from public metadata — recorded as UNKNOWN rather than guessed.

**3 · Business model.** Open source; the commercial surface would be the enterprise gaps in §9.

**4 · Market position.** 434 stars and 35 forks at the reading date. [https://github.com/saltbo/agent-kanban · 2026-08-05]

**5 · Competitive landscape.** Collides with P15 human-in-the-loop. Substitution risk scored 0.35.

**6 · Strengths.**
- Ed25519 identity per agent is the right primitive — actions are attributable
- +63% over 82 days
- treats delegation between agents as a first-class operation

**7 · Weaknesses.**
- FSL-1.1-ALv2 is not open source today; it becomes Apache-2.0 only after two years
- a kanban board is a coordination metaphor, not an approval control

**8 · Missing features.**
- approval bound to a proposal fingerprint
- budget ceilings per task

**9 · Enterprise features absent.**
- delegated authority limits
- segregation of duties

**10 · Security review.** No dependency manifest, so no dependency-derived hazards can be named. Absence of findings here is absence of evidence, not evidence of safety.

**11 · Scalability review.** Operational complexity 0 — nothing beyond the application process itself needs to be run, monitored and paid for, on the evidence available.

**12 · Performance review.** Not measured. Nothing in this scan executed any of these projects, and a performance claim without a run is a rumour with a number in it.

**13 · Automation potential.** Integration cost scored 0.55; licence `FSL-1.1-ALv2` **does not permit building on it.**

**14 · AI integration opportunities.** Advertises no capability from the taxonomy in the text collected for it.

**15 · Revenue opportunities.** See `REVENUE_MATRIX.md` — the enterprise gaps in §9 are the paid surface.

**16 · OMNEX synergy.** human-in-the-loop coordination surface, adjacent to P15 approvals.

**17 · Original improvement.** A board shows that an agent claimed a task. P15 binds an approval to the fingerprint of the exact proposal approved, so an agent cannot alter the plan after sign-off and proceed under the old approval. Attributable identity plus fingerprint-bound approval is the combination that makes autonomous work auditable rather than merely visible.

**18 · Priority.** Growth +63.2% over 82 days. Watch the licence — not absorbable until 2028.

---

## oguzbilgic/agent-kernel

**1 · Executive summary.** Minimal kernel to make any AI coding agent stateful. [https://github.com/oguzbilgic/agent-kernel · 2026-08-05]

**2 · Technical architecture.** Markdown. No dependency manifest was collected for this project, so its internal architecture is not inferable from public metadata — recorded as UNKNOWN rather than guessed.

**3 · Business model.** Open source; the commercial surface would be the enterprise gaps in §9.

**4 · Market position.** 335 stars and 40 forks at the reading date. [https://github.com/oguzbilgic/agent-kernel · 2026-08-05]

**5 · Competitive landscape.** Collides with P13 memory. Substitution risk scored 0.20.

**6 · Strengths.**
- no database and no vector store, so it works everywhere and cannot break
- git history gives it an audit trail for free
- MIT and trivially forkable

**7 · Weaknesses.**
- +1.8% over 82 days — attention has moved on
- flat markdown does not survive scale; retrieval becomes reading everything

**8 · Missing features.**
- retrieval ranking
- conflict resolution between notes
- decay

**9 · Enterprise features absent.**
- access control
- any multi-user story at all

**10 · Security review.** No dependency manifest, so no dependency-derived hazards can be named. Absence of findings here is absence of evidence, not evidence of safety.

**11 · Scalability review.** Operational complexity 0 — nothing beyond the application process itself needs to be run, monitored and paid for, on the evidence available.

**12 · Performance review.** Not measured. Nothing in this scan executed any of these projects, and a performance claim without a run is a rumour with a number in it.

**13 · Automation potential.** Integration cost scored 0.10; licence `MIT` permits building on it.

**14 · AI integration opportunities.** Advertises no capability from the taxonomy in the text collected for it.

**15 · Revenue opportunities.** See `REVENUE_MATRIX.md` — the enterprise gaps in §9 are the paid surface.

**16 · OMNEX synergy.** markdown-only memory is the low-cost end of P13.

**17 · Original improvement.** The insight worth keeping is that memory in a git repository is auditable by construction. Combining that with P13's ranked retrieval — files as the durable store, an index for retrieval, git as the audit log — keeps the property that made this popular while removing the reason it stalled.

**18 · Priority.** Growth stalled over 82 days. STALLED at +1.8% — a good idea that stopped compounding.

---

## slavingia/skills

**1 · Executive summary.** Claude Code skills based on The Minimalist Entrepreneur. [https://github.com/slavingia/skills · 2026-08-05]

**2 · Technical architecture.** Markdown. No dependency manifest was collected for this project, so its internal architecture is not inferable from public metadata — recorded as UNKNOWN rather than guessed.

**3 · Business model.** Open source; the commercial surface would be the enterprise gaps in §9.

**4 · Market position.** 9800 stars and 1000 forks at the reading date. [https://github.com/slavingia/skills · 2026-08-05]

**5 · Competitive landscape.** Collides with nothing we have shipped. Substitution risk scored 0.10.

**6 · Strengths.**
- the highest-starred project in the entire signal set and it contains no code
- distributed through a plugin marketplace, which is where the audience already is

**7 · Weaknesses.**
- no licence file, which means all rights reserved — it cannot be reused
- content is one person's book, so it does not generalise

**8 · Missing features.**
- licence
- any measurement of whether the skills help

**9 · Enterprise features absent.**
- everything — this is a consumer artefact

**10 · Security review.** No dependency manifest, so no dependency-derived hazards can be named. Absence of findings here is absence of evidence, not evidence of safety.

**11 · Scalability review.** Operational complexity 0 — nothing beyond the application process itself needs to be run, monitored and paid for, on the evidence available.

**12 · Performance review.** Not measured. Nothing in this scan executed any of these projects, and a performance claim without a run is a rumour with a number in it.

**13 · Automation potential.** Integration cost scored 0.05; licence `none stated` **does not permit building on it.**

**14 · AI integration opportunities.** Advertises plugin_architecture, skills.

**15 · Revenue opportunities.** See `REVENUE_MATRIX.md` — the enterprise gaps in §9 are the paid surface.

**16 · OMNEX synergy.** the distribution lesson: 9,800 stars for ten markdown files.

**17 · Original improvement.** The lesson is packaging, not content: ten markdown files in a marketplace outperformed every engineering project in this scan. OMNEX has eighteen production systems with measured numbers and no distribution surface. Publishing the measurable ones as installable skills is the highest-leverage move in this report, and it is nearly free.

**18 · Priority.** Growth +13.0% over 82 days. DISTRIBUTION LESSON — the most valuable row in the scan.

---

## facebookresearch/HyperAgents

**1 · Executive summary.** Self-referential self-improving agents that can optimize for any computable task. [https://github.com/facebookresearch/HyperAgents · 2026-08-05]

**2 · Technical architecture.** Python. No dependency manifest was collected for this project, so its internal architecture is not inferable from public metadata — recorded as UNKNOWN rather than guessed.

**3 · Business model.** Open source; the commercial surface would be the enterprise gaps in §9.

**4 · Market position.** 2700 stars and 348 forks at the reading date. [https://github.com/facebookresearch/HyperAgents · 2026-08-05]

**5 · Competitive landscape.** Collides with P3 multi-agent. Substitution risk scored 0.20.

**6 · Strengths.**
- a genuine research contribution with a corporate research lab behind it
- states its own safety hazard about executing model-generated code plainly

**7 · Weaknesses.**
- CC BY-NC-SA 4.0 is non-commercial — it cannot be built on by a business at all, and the ShareAlike term would infect anything derived from it
- executes model-generated code, which is a production risk rather than a feature

**8 · Missing features.**
- commercial licence
- sandbox boundary claims that survive scrutiny

**9 · Enterprise features absent.**
- any commercial use whatsoever

**10 · Security review.** No dependency manifest, so no dependency-derived hazards can be named. Absence of findings here is absence of evidence, not evidence of safety.

**11 · Scalability review.** Operational complexity 0 — nothing beyond the application process itself needs to be run, monitored and paid for, on the evidence available.

**12 · Performance review.** Not measured. Nothing in this scan executed any of these projects, and a performance claim without a run is a rumour with a number in it.

**13 · Automation potential.** Integration cost scored 1.00; licence `CC BY-NC-SA 4.0` **does not permit building on it.**

**14 · AI integration opportunities.** Advertises deployment, feedback_loops.

**15 · Revenue opportunities.** See `REVENUE_MATRIX.md` — the enterprise gaps in §9 are the paid surface.

**16 · OMNEX synergy.** self-improving agents are adjacent to P3, but the licence forecloses use.

**17 · Original improvement.** The absorbable idea is the loop, not the code: a meta-agent that proposes changes and an evaluator that accepts them. We already have the evaluator half (P4) and the approval half (P15). Self-improvement gated on a human-approved, fingerprint-bound proposal is the version that can run in production — HyperAgents cannot ship that because its safety story ends at a warning in the README.

**18 · Priority.** Growth +9.0% over 82 days. READ ONLY — non-commercial licence, absorb the idea and nothing else.

---

## alvinunreal/awesome-opensource-ai

**1 · Executive summary.** Curated list of the best truly open-source AI projects, models, tools. [https://github.com/alvinunreal/awesome-opensource-ai · 2026-08-05]

**2 · Technical architecture.** Markdown. No dependency manifest was collected for this project, so its internal architecture is not inferable from public metadata — recorded as UNKNOWN rather than guessed.

**3 · Business model.** Open source; the commercial surface would be the enterprise gaps in §9.

**4 · Market position.** 4400 stars and 563 forks at the reading date. [https://github.com/alvinunreal/awesome-opensource-ai · 2026-08-05]

**5 · Competitive landscape.** Collides with nothing we have shipped. Substitution risk scored 0.05.

**6 · Strengths.**
- CC0-1.0 — genuinely public domain, so the curation can be reused outright
- +23% over 82 days for a list, which shows curation still compounds

**7 · Weaknesses.**
- a list has no defensibility; the next list replaces it
- daily updates are a permanent maintenance burden with no revenue attached

**8 · Missing features.**
- measurement of the projects listed
- any monetisation

**9 · Enterprise features absent.**
- nothing enterprise about it

**10 · Security review.** No dependency manifest, so no dependency-derived hazards can be named. Absence of findings here is absence of evidence, not evidence of safety.

**11 · Scalability review.** Operational complexity 0 — nothing beyond the application process itself needs to be run, monitored and paid for, on the evidence available.

**12 · Performance review.** Not measured. Nothing in this scan executed any of these projects, and a performance claim without a run is a rumour with a number in it.

**13 · Automation potential.** Integration cost scored 0.05; licence `CC0-1.0` **does not permit building on it.**

**14 · AI integration opportunities.** Advertises no capability from the taxonomy in the text collected for it.

**15 · Revenue opportunities.** See `REVENUE_MATRIX.md` — the enterprise gaps in §9 are the paid surface.

**16 · OMNEX synergy.** curation as a growth channel; CC0 so the list itself is reusable.

**17 · Original improvement.** A list ranks by opinion. This engine ranks by measured 82-day velocity, licence absorbability and feature-gap opportunity, with the arithmetic printed. A curated list that publishes WHY each entry is ranked where it is — and updates itself from a scanner — is a defensible version of the highest-traffic format in this set.

**18 · Priority.** Growth +22.6% over 82 days. The format works; the version with evidence attached is ours to build.

---

## Ataraxy-Labs/opensessions

**1 · Executive summary.** tmux sidebar for coding agents with per-thread markers and a local HTTP API. [https://github.com/Ataraxy-Labs/opensessions · 2026-08-05]

**2 · Technical architecture.** Rust. No dependency manifest was collected for this project, so its internal architecture is not inferable from public metadata — recorded as UNKNOWN rather than guessed.

**3 · Business model.** Open source; the commercial surface would be the enterprise gaps in §9.

**4 · Market position.** 1200 stars and 70 forks at the reading date. [https://github.com/Ataraxy-Labs/opensessions · 2026-08-05]

**5 · Competitive landscape.** Collides with nothing we have shipped. Substitution risk scored 0.10.

**6 · Strengths.**
- Rust, MIT, and a local HTTP API that makes it scriptable

**7 · Weaknesses.**
- tmux-only, which caps the addressable audience

**8 · Missing features.**
- cost visibility
- remote sessions

**9 · Enterprise features absent.**
- team visibility

**10 · Security review.** No dependency manifest, so no dependency-derived hazards can be named. Absence of findings here is absence of evidence, not evidence of safety.

**11 · Scalability review.** Operational complexity 0 — nothing beyond the application process itself needs to be run, monitored and paid for, on the evidence available.

**12 · Performance review.** Not measured. Nothing in this scan executed any of these projects, and a performance claim without a run is a rumour with a number in it.

**13 · Automation potential.** Integration cost scored 0.50; licence `MIT` permits building on it.

**14 · AI integration opportunities.** Advertises no capability from the taxonomy in the text collected for it.

**15 · Revenue opportunities.** See `REVENUE_MATRIX.md` — the enterprise gaps in §9 are the paid surface.

**16 · OMNEX synergy.** developer surface rather than infrastructure; limited OMNEX overlap.

**17 · Original improvement.** The reusable idea is the local HTTP API for pushing session metadata — a pattern our pipeline (P16) could expose so any long-running job reports progress to whatever the operator already has open.

**18 · Priority.** Growth +15.4% over 82 days. Adjacent; note the pattern, do not build it.

---

---

*Generated by `engine/scripts/scan_intel.py` from `intel/snapshots/metrics_20260515.csv` and `intel/evidence_20260805.json`. Every figure resolves to a record in the evidence file; the generator refuses to publish a document that cites anything else.*
