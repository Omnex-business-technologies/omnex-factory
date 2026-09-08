"""OMNEX engine — the production AI systems behind OMNEX Factory.

Each subpackage is one system, and each is usable on its own. They are in one
package because they share primitives and, more importantly, because the
interesting behaviour lives *between* them: the router (P2) spends a budget the
observability layer (P5) accounts for, the RAG pipeline (P1) retrieves through
the vector layer (P12) and is scored by the eval harness (P4), which is the gate
the deployment pipeline (P11) refuses to deploy past.

    core/    money, time, ids, errors, retry — no AI dependency at all
    obs/     P5  tracing, cost accounting, latency percentiles, alerting
    llm/     model protocol, pricing, deterministic test models
    router/  P2  complexity routing, spend tracking, cascade fallback
    guard/   P6  injection detection, PII redaction, output filters, sandbox
    vectors/ P12 hybrid search, metadata filters, embedding cache, backup
    rag/     P1  PDF ingest with page anchors, reranking, grounded citations
    memory/  P13 buffers, recall, compression, eviction
    evals/   P4  golden cases, metrics, regression gate, quality trend
    crew/    P3  supervisor, consensus, approval gates, audit trail
    hitl/    P15 uncertainty detection, pause/resume, approvals
    pipeline/P16 webhooks, idempotency, retries, dead letters
    tenancy/ P10 isolation, quotas, usage metering
    serving/ P14 batching, KV cache, load balancing
    finetune/P9  dataset prep, LoRA, DPO, forgetting checks
    mcp/     JSON-RPC tool protocol: untrusted results, priced per call
    factory/ node capabilities -> a fingerprinted AgentSpec, gates as a type,
             compilers to three targets that re-read their own output,
             per-run economics, a portfolio of live agents, and the loop back
"""

__version__ = "0.1.0"
