# Execution decisions

Long-term memory for decisions that changed what gets built, and for every
material deviation from a plan. A decision recorded nowhere has to be reached
again from scratch by the next reader, which is how a repository loses the
reasoning and keeps only the result.

Each entry states what was decided, what evidence forced it, what else was
considered, and whether it can be undone. **Evidence is not the plan.** A plan is
an intention; evidence is a measurement somebody can repeat.

> This file will become a generated projection of `state/decisions.jsonl` once
> that store exists. It is hand-written today because the store does not, and
> claiming otherwise would be the exact failure D-001 records.

---

## D-001 · The execution report was not evidence

**date:** 2026-09-08 · **status:** ACCEPTED · **reversible:** n/a (a finding)

**context.** A long planning exchange produced a detailed architecture: a
constitution, an execution contract, derived machine state, a node dossier
engine, a decision queue, a release engine. An adversarial review then graded it
— "Truth discipline 10/10", "`execution_state.json` is not manual state",
"Governance 10/10".

**evidence.** Measured against the filesystem, at HEAD `83f4393` with a clean
working tree:

```
REPORTED → PRESENT → VERIFIED → INTEGRATED → PRODUCTION
   15         0          0           0            0
```

All fifteen named artifacts were ABSENT — `CONSTITUTION.md`,
`EXECUTION_CONTRACT.md`, `execution_state.json`, `docs/EXECUTION_DECISIONS.md`,
`state/decisions.jsonl`, `node_dossier.py`, `state_map.py`, `state_check.py`,
`extras_check.py`, `apply_decisions.py`, `release_check.py`, `next_action.py`,
`release.yml`, `DECISIONS.md`, `LICENSE`. The whole exchange had run in plan
mode, which blocks every write.

**alternatives.** Accept the grading and continue to the next phase; or measure
first and report the gap.

**chosen.** Measure, report the gap, and start from zero.

**reason.** The grading was of a document. Nothing had crossed `REPORTED`, and
treating a plan as an implementation is precisely the failure the review's own
Truth adversary exists to catch: documentation became evidence because it
existed.

**tradeoffs.** Slower, and it contradicts a favourable review.

**risk.** None from recording it. The risk was in the other direction.

---

## D-002 · Six unsupported extras are reclassified, not adapted

**date:** 2026-09-08 · **status:** ACCEPTED · **reversible:** yes

**context.** `engine/pyproject.toml` declares twelve extras. The plan initially
treated four of them as work items — write the missing adapters so the
declarations become true.

**evidence.** Every import in `src/omnex` was grepped, indented ones included:

| extra | dependencies imported | verdict |
|---|--:|---|
| `llm` | 1/1 — `omnex.llm.litellm_adapter` | supported |
| `rag` | 2/2 — `omnex.rag.ingest`, `omnex.rag.rerank` | supported |
| `otel` | 3/4 — `omnex.obs.export` | partial |
| `vectors` | 1/3 — `omnex.vectors.qdrant_store` | partial |
| `figures` | 1/4 — `omnex.rag.figures` | partial |
| `api` | 0/4 | unsupported |
| `memory` | 0/1 | unsupported |
| `worker` | 0/2 | unsupported |
| `agents` | 0/2 | unsupported |
| `evals` | 0/3 | unsupported |
| `finetune` | 0/5 | unsupported |

**Six, not four.** `api` and `finetune` were missed by the first pass, which
grepped only the four already noticed — the reason the check is a script and not
a memory. `fastapi` appears in `intel/sources.py` as a *string* in a list of
frameworks to scan for, never as an import.

**alternatives.** (a) Write six adapters. (b) Delete the six extras. (c) Declare
a status per extra and check the declaration against the code.

**chosen.** (c), with each of the six marked `unsupported` and a stated reason.

**reason.** A declaration is evidence of an intended interface, not proof the
interface should exist. Six adapters written so twelve declarations look complete
is decorative architecture and inflates adapter count, not capability. The
objective is promise integrity. Deleting them loses the intent, which is real —
`finetune` deliberately holds the parts *around* the training loop and its extra
describes a GPU path somebody may still want.

**tradeoffs.** `pip install omnex-engine[agents]` still installs two libraries
that do nothing. That is now documented in the metadata rather than discovered
after installing.

**risk.** A future reader may take `unsupported` as permission to ignore the
extra. Mitigated by requiring the reason to say what it would take.

---

## D-003 · A backticked adapter filename is a claim

**date:** 2026-09-08 · **status:** ACCEPTED · **reversible:** yes

**context.** `graph/runtime.py` said there was "an adapter for it in
`langgraph_adapter.py`". `pipeline/queue.py` said "Celery is the production path
(`celery_adapter.py`)". Neither file has ever existed.

**evidence.** `extras_check.prose_adapters()` found both. Rewriting the
docstrings to *explain* that the files do not exist made the checker fail again —
it cannot tell a claim from a denial when both are backticked.

**alternatives.** Teach the checker to parse negation; or make the notation the
rule.

**chosen.** A backticked `*_adapter.py` is a claim that the file exists. Prose
about an adapter that does not exist uses plain words.

**reason.** Parsing "has never existed" out of a sentence fails in the direction
of passing, which is the worst direction for a check whose whole job is catching
prose that resolves to nothing. This is the same class as
`n8n_bindings.json` naming `omnex.pipeline.verify_webhook`.

**tradeoffs.** A small notation rule contributors must know. It is stated in
`extras_check.py` beside the pattern that enforces it.

**risk.** Low. The failure mode is a false positive, which is loud.

---

## D-004 · Phases 6–14 are deferred, with the reason recorded

**date:** 2026-09-08 · **status:** ACCEPTED · **reversible:** yes

**context.** The master plan names Evaluation, Security, Autonomy L0→L5, Skill
Registry, Distribution, Commercialization, Opportunity Intelligence, Capital
Allocation and Continuous Self-Improvement. The proof manifest and Economic
Shadow Mode were also proposed.

**evidence.** No invariant requires them, no existing capability depends on
them, and no observed failure calls for them. Nothing has been distributed;
revenue is zero; zero of seven n8n bindings are confirmed.

**alternatives.** Specify them now for completeness; or defer with a recorded
reason and a stated trigger.

**chosen.** Defer. Each gets files when its prerequisite passes its own gate.

**reason.** Specifying Capital Allocation before a single artifact leaves the
repository is writing a plan for a capability whose prerequisites do not exist —
decorative architecture by the plan's own definition.

**tradeoffs.** The execution plan is narrower than the master plan. That is the
intended relationship, not a shortfall.

**risk.** Deferral becoming abandonment. Mitigated by this entry naming the
trigger rather than a date.

---

## D-005 · A gate was right about one target for the wrong reason

**date:** 2026-09-08 · **status:** ACCEPTED · **reversible:** n/a (a defect fixed)

**context.** `release_check.py` was written to refuse a package that is not ready
to ship, and its first run found two real defects in `oss/citegate`: a
`requires-python = ">=3.10"` the code could never satisfy (`enum.StrEnum` is
3.11, reproduced with `/usr/bin/python3.10 -c "import citegate"`), and sixteen
tests that had never run in CI.

**evidence.** Run against the *second* target it reported thirteen refusals
against `engine`, and every one was false:

1. it read `dependencies` and ignored `[project.optional-dependencies]`, so it
   called `zero_required_dependencies` — the engine's entire design — a defect;
2. it borrowed `extras_check.importers()`, whose regex matches inside docstrings,
   and reported imports of `a`, `free`, `the` and `zero`;
3. it assumed a target's directory name was its import name (engine's is `omnex`);
4. it looked for `working-directory` only inside job blocks while `engine.yml`
   sets it in top-level `defaults:` — **so the check written to find suites CI
   does not run could not see the suite CI does run.**

**alternatives.** Ship it as-is, since it was correct about the target it was
written for; scope it permanently to citegate; or fix it and require both.

**chosen.** Fix all four, and put **both** targets in CI and in `CLAUDE.md`'s gate
block. `read_imports` now reads the syntax tree with `ast` rather than a regex.

**reason.** Bug 4 is the one worth recording. It produced the *right answer* for
citegate — by coincidence of the same bug that made it wrong about engine. A gate
that is right for the wrong reason is indistinguishable from a working one until
a second target exists, which is why one target is now never enough. The same
argument `test_the_round_trip_check_can_actually_fail` already makes for the
compilers.

**tradeoffs.** A second import scanner beside `extras_check.importers()`. Justified
by a difference in contract and stated in the docstring: that one asks whether a
*declared* name appears anywhere, where a false positive is never looked up; this
asks what a package imports and reads the answer as truth. `IMPORT_NAME` and
`_requirement_name` are reused rather than copied.

**risk.** A third target exposing a fifth assumption. Mitigated only in that
`test_the_committed_target_passes_the_drift_checks` is parametrised, so adding a
target adds a test rather than a hope.

---

## D-006 · `tiktoken` was imported and nothing declared it

**date:** 2026-09-08 · **status:** ACCEPTED · **reversible:** yes

**context.** Fixing D-005's bug 1 cleared twelve of the thirteen refusals. One
survived, and it was true.

**evidence.** `src/omnex/llm/tokens.py:130` imports `tiktoken` inside
`TiktokenCounter`. Measured: `dependencies = []` and none of the twelve groups in
`[project.optional-dependencies]` names it. **There was no
`pip install omnex-engine[…]` that made that class work.** It fails honestly at
runtime (`"TiktokenCounter needs tiktoken; HeuristicCounter needs nothing"`), so
nothing was silently broken — but a real capability had no declared install path.

**alternatives.** Declare it in a group; mark the counter unsupported; or delete
the class.

**chosen.** Declare `tiktoken>=0.8` in the `llm` extra, beside `litellm`, and add
`omnex.llm.tokens` to that extra's `backed_by`. `extras_check.py` confirms it at
2/2 `supported`.

**reason.** `TiktokenCounter` is real, working, tested code with a stated purpose,
so §4's correction does not apply — the intention plainly still holds and the
declaration was simply missing. `llm` is the module it serves.

**tradeoffs.** None found. Both dependencies in the group are imported, so the
extra's status does not change.

**risk.** Low, and the interesting part is what this says about `extras_check.py`:
it asks *declared → imported* and **cannot see this direction by construction**.
`release_check.py` asks *imported → declared*. Neither subsumes the other, and
that asymmetry is why the second checker earns its place rather than duplicating
the first.
