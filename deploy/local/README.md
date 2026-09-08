# Local-first stack (P7)

**Zero API cost, offline, and the same code paths as production.**

```bash
docker compose -f deploy/local/compose.yaml up -d
docker compose -f deploy/local/compose.yaml exec ollama ollama pull qwen2.5:7b-instruct
docker compose -f deploy/local/compose.yaml exec engine python scripts/eval_gate.py
```

## Why this exists

Not "a dev environment". The point is that it runs the **same** router,
guardrails, grounder, vector store and eval gate as production, with the model
tier swapped for one that costs nothing. A development environment that differs
from production is one where the bugs you find are not the bugs you have.

Three consequences worth stating:

- **The eval gate runs on every pull request** because it costs nothing. A gate
  that runs nightly tells you which of yesterday's twelve merges broke it, which
  is not the same as telling you.
- **Someone can evaluate the system before paying for anything.** No account, no
  key, no card.
- **The router prefers this tier wherever the task allows.** Local models are
  priced at zero in the catalogue, which is honest — the electricity is real but
  it is not per-token — and `Router.calibrate()` reads that as an infinite price
  ratio and routes aggressively cheap.

## What is open source here

Everything. Ollama for inference, SQLite for vectors, the engine's own BM25 for
lexical retrieval, its own histogram and tracing for observability. There is no
hosted dependency in this stack at all — the paid providers in the catalogue are
an *option* the router can reach for, not a requirement to run.

## The one thing that is enforced rather than documented

The compose file sets `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` and `GROQ_API_KEY`
to empty strings, and the Dockerfile runs the test suite during the build. If
the local stack ever starts depending on a hosted provider, the image fails to
build rather than quietly billing someone.
