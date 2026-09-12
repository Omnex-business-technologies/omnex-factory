# OMNEX Factory

**One platform, many AI business modules — sharing one login, one credit balance
and one AI infrastructure.**

A module is a route group plus a manifest entry. The dashboard, pricing and
navigation are generated from that manifest, so shipping a new product is
configuration rather than a new application. Credits are the single currency
across every module, which is what makes each new module raise the value of a
purchase already made.

Module #1 is **AI Ad Studio**: upload a product photo, pick a scene, get
campaign-grade visuals across every publishing format.

---

## Why this exists

Most agent demos work once, on a good day, on the happy path. This is built
around the opposite question: **what does an agent system do when it is wrong,
and how would you know?**

That question shaped nearly every design decision below.

---

## More than one codebase

Everything above is the commercial surface — a Next.js app. It sells access to
something bigger that also lives in this repository:

**`engine/`** is a separate, zero-dependency Python AI platform: eighteen
production systems — LLM routing, RAG with page- and figure-anchored citations,
a hybrid vector store, injection/PII guardrails, multi-agent consensus with a
hash-chained audit trail, human-in-the-loop approval, OpenTelemetry
observability, and a compiler that turns one agent spec into a runnable graph,
an MCP server, or an n8n workflow. It has [its own README](engine/README.md),
1,292 tests, zero required dependencies, and is why GitHub lists this repo's
primary language as Python — not because the commercial app is secondary, but
because the engine is larger.

The rest of the top level supports one side or the other, or the process that
builds them:

| Path | What it is |
|---|---|
| `oss/citegate/` | A standalone, dependency-free citation checker extracted from the engine's RAG grounder — its own package, its own [README](oss/citegate/README.md), its own tests. |
| `skills/` | Five packaged Claude Skills (`cost-router`, `eval-gate`, `finground`, `grounded-answers`, `injection-corpus`), each shipping a measured number rather than a claim. [README](skills/README.md) |
| `packs/` | Image-generation job packs for a separate digital-goods line (Etsy / Lemon Squeezy) — QC gates, listing checks, deterministic pack assembly. |
| `intel/` | Committed market-research snapshots: competitive intel, a revenue matrix, a roadmap — the evidence behind product decisions, not the decisions themselves. |
| `corpus/` | A 509-figure reference corpus (~1.7 MB, from *AI Engineering* by Pachaar & Chawla) that ranks what the engine should build next by how many figures name a capability it doesn't have yet. |
| `state/` | An append-only, hash-chained ledger of claims, evidence, and execution runs — the mechanism that keeps this file, and every other doc in the repo, a measurement rather than a hope. |
| `docs/` | Why things were built the way they were, in the order they happened, with the evidence that forced each call. |
| `deploy/` | A local-first Docker stack — the same router, guardrails, and eval gate as production, priced at zero. |

`CLAUDE.md`, `CONSTITUTION.md` and `EXECUTION_CONTRACT.md` are the operating
rules for whoever works on this repository next, human or agent — not
application code, worth reading before changing anything load-bearing.

---

## Architecture

```mermaid
flowchart TB
    UI["Studio UI<br/>upload · scene · format"] --> API["/api/studio/generate"]

    API --> G1{{"1 · auth + rate limit"}}
    G1 --> G2{{"2 · validate against catalogue"}}
    G2 --> G3{{"3 · CHARGE credits<br/>SELECT … FOR UPDATE"}}
    G3 --> GEN["4 · image provider chain"]

    GEN --> P1["fal"]
    GEN --> P2["replicate"]
    GEN --> P3["local ComfyUI"]
    GEN --> P4["pollinations · free"]

    GEN -->|success| ST["5 · persist to storage<br/>+ usage_events"]
    GEN -->|failure| RF["6 · REFUND credits"]

    ST --> RESP["response<br/>+ capabilities of the provider<br/>that actually served"]

    subgraph core["lib/core — shared by every module"]
        LLM["llm/ · provider chain<br/>semantic cache · embeddings"]
        AG["agents/ · guardrails<br/>traces · budget"]
        BILL["billing/ · credits · packs"]
        SUP["supabase/ · RLS · BOM-safe env"]
    end
```

### The order in step 3–6 is the point

Credits are charged **before** the provider call, because the balance row is
locked and decremented inside a single SQL function — that is what stops two
simultaneous requests spending the same credits. And because charging first
would otherwise bill for nothing, a provider failure **refunds**.

---

## Design decisions worth reading

**The provider chain reports who actually served.**
A response used to advertise the capabilities of the *intended* provider while a
fallback had really produced the render — so a control that the serving provider
ignores looked available. `capabilitiesOf(result.provider)` reports on what ran.

**A control that does nothing is not shipped.**
One provider silently ignores its `strength` parameter — proven by identical
SHA-256 output at two different settings. Since a generative model returns
different images anyway, determinism had to be established first before a
difference could mean anything. Providers now declare `honoursStrength`, and the
UI hides the fidelity control when it would be fake.

**Guardrails run on output, not just input.**
Prompt-injection detection on fetched content, and outbound checks for leaked
credentials, unfilled template placeholders, and messages addressed to one named
recipient being published to everyone. That last rule exists because it happened.

**Budgets stop runs with a reason.**
Three independent ceilings — passes, tokens, wall-clock — because they fail
differently: a pass cap catches a loop that thrashes without spending, a token
cap catches one runaway generation, a wall-clock cap catches a hung provider.
The default sits below the platform timeout so a run stops with a stated cause
instead of being killed without one.

**Traces preserve the shape of a run.**
A span tree with parent links, a `failurePath()` that returns only the failing
branch, and totals computed from spans rather than tallied as the run proceeds.

**Tests run against a real database.**
`consume_credits` is PL/pgSQL whose correctness *is* the row lock, so a mock
would prove nothing. CI starts a real Postgres in a container and asserts under
concurrency: ten simultaneous spends of 20 against a balance of 100 leave exactly
five successes and a balance of zero.

---

## Stack

| Layer | Choice |
|---|---|
| App | Next.js 16 (App Router), React 19, TypeScript strict + `exactOptionalPropertyTypes` |
| Data | Supabase / Postgres, RLS, PL/pgSQL, pgvector |
| Payments | Stripe — one-time credit packs, webhook idempotency by primary-key conflict |
| Images | Provider chain: fal · replicate · local ComfyUI · pollinations (free fallback) |
| LLM | Free-first chain: Ollama · Groq · Google · OpenRouter · HF · Anthropic |
| CI | GitHub Actions — types, unit tests, real Postgres via Testcontainers, prod build |

---

## Layout

```
app/(app)/studio/          module #1 — AI Ad Studio
app/api/studio/            generate · upload
app/api/stripe/            checkout · webhook · portal
lib/core/                  shared by every module
  ├─ llm/                  provider chain · semantic cache · embeddings
  ├─ images/               image provider chain · ComfyUI client
  ├─ agents/               guardrails · traces · budget
  ├─ billing/              credits · packs
  └─ supabase/             env (BOM-safe) · admin · server · client
lib/modules/
  ├─ registry.ts           module manifests — the factory spine
  └─ studio/               11 campaign categories · personas · prompt builder
supabase/migrations/       credit ledger · usage events · webhook idempotency
```

## Running it

```bash
npm install
cp .env.local.example .env.local   # Supabase URL + keys required
npm run dev
```

Tests, including the containerised database suite (needs Docker):

```bash
npm test
```

---

*Built and operated solo. Every behaviour described above is asserted by a test
or was verified against the live system — none of it is aspirational.*
