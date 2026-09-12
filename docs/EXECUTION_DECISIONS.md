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

---

## D-007 · `state_check.py` was folded into `state_map.py --check`, and never recorded

**date:** 2026-09-08 · **status:** ACCEPTED · **reversible:** yes

**context.** The plan named `state_map.py` and `state_check.py` as two artifacts.
Only one exists.

**evidence.** A reconciliation of every artifact the plan names found 15 PRESENT
and 7 ABSENT. `state_check.py` was among the absent — not because it was skipped
but because its behaviour lives in `state_map.py --check`.

**chosen.** Keep the fold. Record the deviation, which is the part that was
missing: an absent artifact that is absent *on purpose* is indistinguishable
from one that was forgotten unless somebody writes down which it is.

**reason.** The generator and the validator share one derivation. Splitting them
gives two files that must agree about the shape of the state — the drift this
repository keeps paying for, and the reason `one_symbol_resolver` exists.
`env_check.py` and `release_check.py` use the same `--mode` shape.

**tradeoffs.** The plan's artifact list no longer matches the filesystem
one-for-one, which is why this entry exists.

**risk.** Low. The same argument applies to `runs.py`, which absorbs the planned
`checkpoint.py` and `recover.py` for the same reason and is recorded in D-008.

---

## D-008 · The execution spine, and what was deliberately not built

**date:** 2026-09-08 · **status:** ACCEPTED · **reversible:** yes

**context.** The hardening contract requires the spine to exist before broad
adapter, deployment or commercialization work. It did not exist: `claims.jsonl`,
`evidence.jsonl`, `runs.jsonl`, `next_action.py`, `checkpoint.py` and
`recover.py` were all ABSENT while PHASE 3 was reported complete.

**evidence.** A file-by-file reconciliation, run before writing anything:
15 PRESENT, 7 ABSENT, and the seven absent were the whole spine.

**chosen.** `claims.py` (registry + derived status), `policy.py` (side-effect
classes, autonomy, authorisation), `next_action.py` (derived graph +
recommendation), `runs.py` (ledger + checkpoint + recovery). 51 tests, 5
mutations, both `--check` modes in CI and in the documented gate.

**reason, decision by decision:**

- **Status is derived, not stored.** The contract lists `status` as a claim
  field. Storing it makes it typeable, and a typeable status lets anybody write
  SUPPORTED without producing what the word means. `evidence.jsonl → status()`.
- **A claim is not SUPPORTED because evidence exists.** `VERIFIES` maps claim
  type to the methods that can settle it. Without it, writing a row and proving
  a thing are the same act.
- **Contradiction is superseded, never deleted.** `E-004` (citegate's tests
  never ran in CI) is still on file under `E-005`, because a registry that drops
  what disagreed with it cannot say what would change its mind.
- **Money orders; money does not decide.** `economic_weight` reaches `order()`
  and nothing else. `test_an_economic_score_cannot_change_a_claim_status` and
  `test_economic_weight_is_not_an_input_to_authorisation` are the executable
  form — the prose version is what every system that failed this way also had.
- **`runs.py` absorbs `checkpoint.py` and `recover.py`.** Three files, one data
  model, three places to drift. Same argument as D-007.

**what was deliberately NOT built, and why:**

- **Full invalidation propagation** (dependency change → staleness → claim
  invalidation → graph recomputation). The metadata it needs is in place —
  `source_version`, `reverify_after`, `dependencies` — but nothing in the
  repository yet has a dependency whose change would trigger it. Building the
  propagation now would be a mechanism with no input. The contract explicitly
  permits this: implement the minimum metadata that makes future propagation
  safe. That metadata cannot be backfilled; the mechanism can.
- **The OUTCOME → LEARNING → GRAPH UPDATE loop.** `expected_outcome` and
  `observed_outcome` are on every run from the first one, because an expectation
  recorded after the result is a description rather than a prediction and cannot
  be added later. The loop itself needs runs to learn from and there are zero.
- **A proof manifest.** No invariant requires it and no capability depends on it.

**tradeoffs.** The registry has 12 claims. That is small, and deliberately so:
every one is a claim this session actually made and can point at evidence for.
A registry seeded with plausible-looking rows would have exactly the property
the whole design refuses.

**risk.** The registry becoming a second copy of `nodes.json` or `invariants.json`.
Mitigated by scope: those answer "does this symbol exist" and "is this rule
held". This answers "how do we know, when did we last look, and what argues
against it" — and `C-012` (the Etsy shape is unreadable here) is a claim neither
of the others could hold.

**a correction made during the work.** The first seed filed the egress-proxy 403
as evidence *contradicting* "the Etsy API accepts this request", which made the
registry report CONTRADICTED — asserting as false something the evidence text
itself called unverifiable. Being unable to check is not evidence against.
Split into `C-012` (readability, CONTRADICTED, measured) and `C-009`
(acceptance, UNKNOWN, no evidence), and `test_being_unable_to_check_is_not_
evidence_against` now holds that line.

---

## D-009 · The final gate, and the link it was built to find

**date:** 2026-09-08 · **status:** ACCEPTED · **reversible:** yes

**context.** The hardening contract requires, before broad adapter or deployment
work, that the chain from TRUTH to RECOVERY be demonstrated and that any
transition which is *merely documented* be classified as such.

**evidence.** `spine_check.py` on the commit that introduced it:
**13 EXECUTABLE · 1 DOCUMENTED**. The documented one was
`VERIFICATION → RUN LEDGER`: `runs.py` resolved, `test_runs.py` existed, CI
checked it — and `state/runs.jsonl` did not exist, because nothing wrote to it.
Predicted before the checker was written, then reported by it.

**chosen.** Three grades, not two. `ABSENT` means the code is not there.
`DOCUMENTED` means the code and its test are there and **nothing has ever run
it**. Collapsing those two into "not passing" would have been tidier and would
have lost the only distinction that matters here.

**reason.** `DOCUMENTED` is the state that reads as finished in every summary
that lacks a word for it. `release.yml` is still in it. So was the run ledger,
and so was this whole architecture on the day `D-001` recorded that fifteen
reported artifacts existed zero times.

**the writer, and what was refused.** `runs.py --record` opens a run before the
work with a required `--expect`; `runs.py --observe` closes it. **The
observation is appended, never written back** — the ledger is hash-chained, so
editing a row breaks every link after it, and in any case what happened is a
different fact from what was predicted, at a different time. `expected_outcome`
travels from parent to observation unchanged and `revised_predictions()` refuses
a mismatch: the one way that field could be defeated is quietly improving what
you said you expected while recording what occurred.

**R-0001 is the first row and was not backfilled.** Sixty-one commits of prior
work have no ledger entry and will not get one. An expectation written after the
result is a description, and manufacturing sixty-one of them to make an artifact
exist is precisely the substitution `D-001` caught.

**tradeoffs.** `--strict` is not the default. An all-green chain is the goal, not
the current state, and a permanently red build is one people learn to ignore —
the same reasoning that scopes `live_listings_are_covered` to live offers.

**risk.** The chain reading 14/14 and meaning less than it looks. Mitigated by
two mutations: one collapses `DOCUMENTED` into `EXECUTABLE`, the other lets a
prediction be revised after the fact. Both are killed.

**two defects found in the checker by running it.** Five links named symbols the
shared resolver cannot reach — it resolves `module.attribute`, not
`module.Class.method` — and `state_map.build` did not exist (`derive` does). And
`walk(chain=CHAIN)` bound its default at definition time, which made the gate's
own failure path untestable. All fixed; the last one is why
`test_strict_exits_non_zero_when_a_link_is_not_executable` runs a subprocess.

---

## D-010 · Why the PHASE 4 adapters were not built

**date:** 2026-09-08 · **status:** ACCEPTED · **reversible:** yes

**context.** The plan's PHASE 4 names adapters for the extras that declare
dependencies nothing imports — `api`, `memory`, `worker`, `agents`, `evals`,
`finetune`. Six of twelve extras, and the obvious next block of work.

**evidence, measured before choosing.** `extras_check.py` reports
**2 supported · 3 partial · 6 unsupported · 1 tooling**, and every one of the six
`unsupported` entries already carries a specific reason naming what exists
in-process instead. That is the rule the checker actually enforces — *an extra
delivers what it declares, or says it does not* — so promise integrity is
already satisfied. Nothing in the repository depends on the six, and no observed
failure calls for them. `next_action.py` does not rank one.

**chosen.** Do not build them. Cut the citegate release instead: `release.yml`
had never executed, `C-005` carried zero evidence, and that was the largest
single `UNKNOWN → measured` conversion available.

**reason.** Building six adapters because a diagram names them is the decorative
architecture `D-004` already refused. A declaration is evidence of an intended
interface, not proof one should exist.

**the hazard, recorded so it is not rediscovered.** `worker` is the one that
looks most obviously buildable and is the most dangerous. `Worker.broker` is
typed to the **concrete** `InMemoryBroker`, and `Worker` runs jobs *in-process*
with its own retry and dead-lettering; celery hands work to a *remote* worker.
Extract a shared `Broker` Protocol and `Worker(broker=CeleryBroker(...))`
type-checks — then submits to celery **and** runs the job locally. A
double-execution path, in the module whose sibling `claim.py` exists because
"the other direction charges the customer twice."

So the first step of that phase is **extracting the Protocol and deciding what
`Worker` may accept**, not writing the adapter. Writing `CeleryBroker` first
produces two concrete classes that happen to share method names, which is the
twin-splitter failure with extra steps.

**what was kept.** The celery API was read from PyPI rather than memory
(`celery 5.6.3`, `requires-python >=3.9`, `send_task(..., task_id=...)` — which
matters, because it lets an idempotency key *be* the task id). That research is
in the session scratchpad, not committed: a claim about a third-party API is
true against a version on a date, and committing it without a
`reverify_after` would create exactly the stale-figure drift this repository
keeps paying for.

**tradeoffs.** The six extras stay `unsupported`. Someone reading
`pyproject.toml` still sees twelve extras and six that deliver nothing — which
is why the *reason* string on each is load-bearing and why `extras_check.py`
refuses silence.

**when this reverses.** When an adapter has a real consumer. Not when a diagram
names one.

---

## D-011 · Narrowing C-005, and why that is not how a claim gets to pass

**date:** 2026-09-08 · **status:** ACCEPTED · **reversible:** yes

**context.** `release.yml` ran for the first time — run `34237298583`,
`run_number` 1, dispatched rather than tagged. Gate green, build green,
**attestation green**. `github_release` and `pypi` were skipped by their
`event_name` guard, and zero releases and zero tags existed afterwards.

**the problem.** `C-005` read "release.yml builds, attests **and publishes**
citegate". Filing the run as `supports` would have derived `SUPPORTED` for a
sentence containing a verb the run deliberately never exercised. Filing nothing
would have thrown away the first real measurement of the release path.

**chosen.** Split, on the precedent already in the registry: `C-005` narrows to
"builds and attests" — exactly what run `34237298583` demonstrates — and the
removed half becomes **`C-013`**, "publishes a GitHub Release carrying the
attested artifacts", `UNKNOWN`, with `dependencies: ["C-005"]`. This is the same
shape as `C-012` (readability, measured) and `C-009` (acceptance, unknown, and
depending on it).

**reason, stated plainly because this is the abusable move.** Narrowing a claim
until the evidence fits is how a registry becomes decorative. What makes this
legitimate is that **nothing was dropped**: the removed half is a claim in its
own right, still `UNKNOWN`, still blocking, and `C-011` ("installable from PyPI
by a stranger") is untouched and stays `UNKNOWN` too — a workflow run is not a
publish, and a GitHub Release is not PyPI. Three verbs, three states, none
collapsed. Had the publish half simply been deleted, the count would have
improved and the repository would know less.

**what the run also settled, for free.** `actions/attest-build-provenance@v2` is
current. That was the one line in `release.yml` that could not be checked
against GitHub's documentation from this environment (`docs.github.com` answers
`403 to CONNECT`), and rehearsing it before the tag is the whole reason
`workflow_dispatch` was added.

**one prediction that was wrong**, recorded because the ledger's value is in the
gaps: the dispatch was expected to be refused until `release.yml` reached the
default branch. The API queued it from the feature branch instead. `R-0004`'s
own `expected_outcome` held; this was a planning assumption alongside it, and it
was assumption, not measurement, that made it wrong.

---

## D-012 · deploy/local's Dockerfile has never worked, and why the fix is not obvious

**date:** 2026-09-08 · **status:** RESOLVED — chosen fix built and verified · **reversible:** yes

**context.** `C-014` claimed `deploy/local/Dockerfile` builds the engine image
and its build-time test suite passes. `docker.yml` (added and rehearsed in
`D-010`'s successor work) dispatched for real for the first time — run
`34275113635`, on `master`, its first execution ever.

**evidence.** The build failed at the baked `RUN python -m pytest tests/ -q`.
Not the failure DOCKER.md's own lessons predicted (a slim base missing a
system library, the `insightface`/`libxcb` shape) — ~90 tests fail with
`FileNotFoundError`-shaped errors: `test_business_map`, `test_env_check`,
`test_release_check`, `test_state_map`, `test_node_dossier`,
`test_spine_check`, `test_runs`, `test_claims`, `test_obs_export`,
`test_pipeline_cli`, `test_mutation`, `test_next_action`, `test_invariants`,
`test_extras_check`, plus `test_intel` errors. `E-013` files this against
`C-014` as `CONTRADICTED`.

**root cause.** `compose.yaml`'s `engine` service builds with
`context: ../../engine` — only the `engine/` subtree ever enters the image.
Many of the engine's own tests are not self-contained to `engine/`: they read
`lib/`, `oss/`, `corpus/`, `state/`, `.github/workflows/`, `CLAUDE.md`,
`execution_state.json`. This is not a new discovery about the tests — CLAUDE.md
has documented it since `engine.yml`'s own `paths:` filter was widened: *"The
engine's tests read outside engine/... `test_listing` reads `packs/`,
`test_business_map` reads `lib/modules/registry.ts`, `test_env_check` reads
every `process.env` in `lib`, `app` and `components`, `test_ci_contract` reads
`CLAUDE.md` and these workflows, and the citegate parity test reads `oss/`."*
`deploy/local/Dockerfile`'s docstring assumed the opposite: *"only needs to be
able to run the engine and its tests."* That assumption was never checked
against what the tests actually are, because nothing had ever built the image.
Inside the container, `Path(__file__).resolve().parents[2]` — the idiom nearly
every cross-cutting test uses to find the repository root — resolves to the
filesystem root instead, and every file lookup off it fails.

**why this is not patched in the same commit.** Two real fixes exist and they
are not equivalent:

1. **Widen the build context to the repository root.** Makes the container's
   tree match what the tests expect, the same way `engine.yml`'s CI job
   checks out the whole repo and only sets `working-directory: engine`. Correct
   in the sense that nothing is skipped — but it directly contradicts
   `DOCKER.md`'s own claim for this image, "~120 MB instead of ~8 GB," which
   is a comparison against the *GPU* images and was never measured against a
   full-repo context. `oss/`, `corpus/` (509 figures), `lib/`, `app/`, `.git/`
   are all real weight, and `COPY . .` would need a `.dockerignore` written
   and verified, not assumed.
2. **Scope the baked test command to a principled subset.** Faster, keeps the
   image's actual size story true — but "principled" is doing the work: there
   is no existing marker distinguishing "tests of the `omnex` package" from
   "monorepo-wide gate tests that happen to live in `engine/tests/`." Inventing
   one under deadline, to make a red build green, is exactly the class of
   change `CLAUDE.md`'s own lab notes already warn about — a test suite that
   quietly stops being run is worse than a red build, and a hand-picked
   `--ignore` list is the same failure with extra steps.

**chosen: neither, yet.** Recorded as a finding rather than patched blind. This
session has no working Docker daemon to iterate against locally (`ulimit:
error setting limit (Operation not permitted)` — a real sandbox restriction,
not a policy refusal), so every attempt costs a full CI round trip on a design
question that deserves more than a guess-and-check loop. `R-0008-observed`
holds the measured failure; this entry holds the reasoning. Whichever fix is
chosen, it gets its own run recorded before the work, the same as every other
change this session.

**risk of doing nothing.** `docker.yml` stays on `workflow_dispatch` only and
is not wired into `pull_request` or `push` — exactly the caution that kept
this from being a red check on every PR before anyone had verified it could
pass at all.

**one more prediction wrong, recorded rather than smoothed over.** `R-0008`
expected a system-library gap. The actual failure was architectural. Both
`R-0007` and `R-0008` on this same claim were wrong about the mechanism while
right that something would fail — worth noting as its own small pattern:
guessing the failure shape from a document written about a *different* image
class (GPU, `omnex/flux:1`) was less reliable than it read at the time.

**resolution.** Option 1 (widen the build context to the repository root) was
chosen, not picked blind: checking first found 19 test files across `engine/`,
`packs/`, `oss/` and `state/` using the `parents[2]` repo-root idiom — too
broad and cross-cutting for option 2's "principled subset" to carve out
without the exact risk `CLAUDE.md`'s own lab notes warn about, a test suite
that quietly stops being run. `compose.yaml`'s `engine` service now builds
with `context: ../..`; the whole repo copies in, `.dockerignore` keeps out
`node_modules/` and `.next/` (519 MB and 17 MB, the two real weight
offenders); runtime paths moved from `/app` to `/repo/engine` to match.
`R-0009`'s dispatch (run `34277217838`) cut the failure from ~90 tests to
~24, all one new, narrower cause: `python:3.12-slim` has no `git` binary, and
`business_map.py`, `release_check.py`, `runs.py` and `state_map.py` all shell
out to it. The first version of the new root `.dockerignore` had also
excluded `.git/` itself on the reasoning that history is "never a build
input" — wrong here, disproven by this exact failure, and corrected along
with a `fetch-depth: 0` fix to `docker.yml`'s checkout (shallow history would
have starved `business_map.py`'s day-count even with `git` installed and
`.git/` present — `release.yml`'s own gate job already carries this fix for
the same reason). `R-0010`'s dispatch (run `34277853648`) built clean: `git`
installed, the full 1,230-test suite passed baked into the image in 15.4s,
tagged `omnex-local-engine:latest` at 349,489,234 bytes (~333 MB — bigger
than the Dockerfile's un-measured "~120 MB" comment, since the context is now
the whole repository, not `engine/` alone, and that comment has been
corrected rather than left stale). `C-014` is `SUPPORTED` (`E-014`). Three
real, escalating-but-narrowing failures (90 → 24 → 0), each fixed on
evidence from an actual dispatch rather than guessed in advance — the same
discipline `R-0007`/`R-0008`'s wrong mechanism guesses argue for.

---

## D-013 · MIT → Apache-2.0, and the transfer that prompted asking

**date:** 2026-09-09 · **status:** DECIDED — operator's explicit choice · **reversible:** partially

**context.** The operator transferred `omnex-factory` from the personal
account `RaveZona` to `Omnex-business-technologies` — steps 1, 2 and 3 of
`docs/TRANSFER.md`, all `CREDENTIAL`/`DESTRUCTIVE`-class and irreducibly
theirs. Verified rather than assumed: `search_repositories` on the new path
returns the repo with `created_at: 2026-07-29` (the *original* creation date,
not a fresh import's), and both `get_file_contents` and `git ls-remote`
against the old `RaveZona/omnex-factory` path still resolve — GitHub's
redirect, live, not just documented. In the same exchange the operator asked
for a "more prestigious" license than MIT.

**evidence and alternatives.** Four options were put to the operator, each
with its real tradeoff stated plainly rather than a bare list of names:
Apache-2.0 (adds an explicit patent grant and a NOTICE convention over MIT,
fully OSI-permissive, no new restriction — the license of Kubernetes and
TensorFlow); Business Source License 1.1 (source-available, blocks a
commercial competitor for a fixed window before converting to Apache-2.0 —
has real teeth here since OMNEX already sells access, but stops being "open
source" by the OSI definition); AGPL-3.0 (copyleft strong enough to require a
SaaS wrapper to publish its modifications — the most defensive option, at the
cost of most integration-friendliness); or leaving MIT and writing down why.
The operator chose **Apache-2.0**.

**what changed.** `LICENSE` at `/`, `engine/` and `oss/citegate/` (identical
text, matching the pre-existing convention of one copy per package) rewritten
to the full Apache License 2.0 text, boilerplate notice reading "Copyright
2026 Omnex Technologies" — the org name, not the prior personal-account
holder, since the license file is being rewritten anyway at the same moment
the repository changed hands; flagged here rather than assumed silently
correct. Both `pyproject.toml` files: `license = { text = "MIT" }` →
`{ text = "Apache-2.0" }`; citegate's classifier list and `[project.urls]`
(the latter is what `release_check.py` actually compares against the git
remote — TRANSFER.md's own step 5) updated to match, plus its README's
licence line. `packs/LICENSE.txt` is untouched on purpose: a commercial EULA
for sold image packs, not a code license, and never was MIT.

**what this session could not do itself.** `add_repo` refused
`Omnex-business-technologies/omnex-factory` outright — "cross-tier adds are
not supported in v1... session already has repos from owner(s) [ravezona]".
This session started scoped to `ravezona/*` and cannot widen to a different
owner mid-conversation; a fresh session sourced from the new path is what
regains full tool access (PR creation, CI-check reads) under the new org.
`git remote set-url origin <new path>` was tried, and inconsistently held —
present at the end of one tool call, reverted to `RaveZona/omnex-factory` by
the next, then observed holding again later, with no local action between
the checks that would explain either transition. Rather than assume either
state, this is left to the environment: the actual push in this same batch
of work is the real test, recorded as `R-0011`'s observation, not asserted
here in advance.

**reversible how.** The license swap is reversible only forwards, not back:
Apache-2.0 code already distributed under that grant cannot be un-licensed
for whoever received it, though nothing here has shipped to PyPI yet
(`C-011` is still `UNKNOWN`), so the practical exposure today is zero. The
org transfer keeps a redirect from `RaveZona/omnex-factory`, which is a
courtesy GitHub can remove, not a guarantee — `git remote set-url origin
<path>` is the documented recovery in `docs/TRANSFER.md` if it ever is.

**what is still open.** `docs/TRANSFER.md` step 6 — a ruleset requiring
status checks on `master` — is unchanged by any of this and remains the one
step that pays immediately: nothing today stops a red-CI merge to the new
canonical repository any more than it stopped one on the old.

---

## D-014 · 8 npm advisories to 0, and a gate that keeps it there

**date:** 2026-09-12 · **status:** RESOLVED — fixed and gated · **reversible:** yes

**context.** GitHub's Dependabot reported 13 open advisories (2 critical, 5
high, 6 moderate) on `master` the same day the repository moved
organizations. Neither `ci.yml` nor any other workflow ran a dependency audit
of any kind, so this had been true for an unmeasured length of time before
anyone looked.

**why the count does not match.** `npm audit` reports 8 (3 moderate, 4 high,
1 critical), not Dependabot's 13. Both are real measurements from different
tools against possibly different advisory databases and dedup rules; neither
number is asserted as canonical here, and the discrepancy is recorded rather
than smoothed into agreement. `npm audit`'s 8 is what this session could
verify directly, reproduce, and act on.

**the critical one, specifically.** `next` 16.2.12 (satisfying the
`^16.2.6` in `package.json` at the time) carried an unauthenticated RCE on
Windows-hosted servers and a second RCE in the Image Optimization API via
AVIF files — both patched only in `16.3.3+`. `16.2.12` was not an old,
neglected pin; it was the version `npm install` would hand a fresh clone
today, on a range that looked current.

**what actually needed fixing, and why `npm audit fix` could not do it.**
`npm audit fix` failed both before and after the `next` bump with
`Cannot read properties of null (reading 'edgesOut')` — an internal npm
error, not investigated further since a manual path was available and
narrower. Bumping `next` alone (16.2.12 → 16.3.5) resolved the critical RCEs
*and* a nested, independently-versioned copy of `postcss` that only existed
inside `next`'s own dependency tree (`node_modules/next/node_modules/postcss`
at 8.4.31, vulnerable, while the top-level `postcss` was already 8.5.24 and
fine) — the same shape of bug this repository's own twin-splitter lesson
already names: two copies of the same thing can diverge silently. `vitest`
and `@vitest/mocker` went 4.1.10 → 4.1.11, a patched release inside the
existing `^4.1.8` range. The remaining three — `qs` (via `stripe`), `nanoid`
(via `postcss`), `brace-expansion` (via `@testcontainers/postgresql` →
`archiver` → `glob` → `minimatch`) — are transitive with no direct entry in
`package.json`, so a version bump has nothing to bump; `overrides` in
`package.json` pins each to its patched release
(`qs@^6.16.0`, `nanoid@^3.3.18`, `brace-expansion@^2.1.4`) regardless of what
their parent originally asked for.

**verified, not assumed.** `npm audit` reads 0 vulnerabilities after the
change. `npx tsc --noEmit`, `npx vitest run` (68/68) and `npx next build`
(11/11 routes) all run clean against the new dependency tree — a security
fix that breaks the build is not a fix, it is a trade.

**the structural half.** A one-time cleanup regresses the moment a new
dependency lands with a fresh advisory. `ci.yml` now runs
`npm audit --audit-level=moderate` before the type-check, so this fails the
build the next time it happens rather than sitting unnoticed until someone
checks the Security tab — the same reasoning `extras_check.py` and
`release_check.py` are already built on. Added to `CLAUDE.md`'s own
documented TypeScript gate too, so the command a developer runs locally
matches what CI now runs, rather than the document being stricter or looser
than CI in either direction.

**reversible how.** Every change here is a version bump or a version pin;
`git revert` undoes it cleanly. The `overrides` entries stop applying the
moment `stripe`, `postcss` or `@testcontainers/postgresql` themselves bump
past the vulnerable range and carry a fixed transitive version on their own
— worth revisiting then, not before.

---

## D-015 · Two claims that are fixed and will never say so

**date:** 2026-09-12 · **status:** ACCEPTED, action needed from a person ·
**reversible:** n/a (a finding, plus two comment-only edits)

**context.** With PR #12 merged, `next_action.py` was run to find the next
real item rather than assume one. It ranked `C-001` and `C-008` at the top —
both `CONTRADICTED`, both flagged "no machine may close it." Re-measuring
found both **already fixed**, by commits that predate this session's summary,
with nobody having gone back to tell the ledger.

**C-001** ("citegate imports on Python 3.10"). `oss/citegate/pyproject.toml`
declared `>=3.10` when `E-001` measured the contradiction (`grounding.py`
imports `enum.StrEnum`, 3.11+ only). Commit `0c0d426` — the same commit that
built `release_check.py` and found this as one of its four bugs — already
raised the floor to `>=3.11`. Re-measured just now, on the actual
interpreters: `/usr/bin/python3.10 -c "import citegate"` still raises
`ImportError: cannot import name 'StrEnum'` (expected — 3.10 was never going
to be supported), and `/usr/bin/python3.11` imports clean. The floor is
honest now. But the claim as worded — "imports on Python 3.10" — did not get
fixed into truth; it got fixed into **irrelevance**, because the promise it
was checking no longer exists in the file. No amount of further code change
makes `C-001` `SUPPORTED`; the fix was raising the floor, not lowering the
requirement.

**C-008** ("`actions/attest-build-provenance@v2` is a current major
version"). `E-011` measured `@v2` two majors stale on 2026-09-08. The pin
was already moved to `@v4` as part of that same investigation
(`.github/workflows/release.yml:146`). Same shape as C-001: the file no
longer makes the claim being checked, so the claim can never mechanically
become true again — it can only be superseded.

**why no evidence was added, and why no claim was closed.** Adding another
`contradicts` entry for either would be noise — the file already agrees with
itself that both are false, twice now. What is missing is not evidence, it
is a person's judgement that the *problem* the claim was tracking is closed,
which is a `reject`, not a `support`. `next_action.py`'s own text is
explicit: *"Either change the repository so it becomes true, or reject the
claim with a person's name and a date. No machine may close it."* Both floors
already changed; neither claim can ever become true as worded; therefore both
need the second option, and `apply_decisions.py`'s refusal of
machine-shaped reviewers for `nodes.json` applies here by the same logic
even though `claims.jsonl` has no script enforcing it yet — this repository
does not get to selectively apply its own rule to the file that has a
checker and skip it for the file that does not.

**what a person needs to do, precisely.** Add `rejected_by` (a real name) and
`rejected_on` (today's date) to the `C-001` and `C-008` rows in
`state/claims.jsonl`, with a `note` along the lines of "fixed by raising the
requires-python floor / bumping the action pin, not by making the original
claim true — see D-015." That is a two-field edit per row; I am not making it
myself.

**docker.yml, fixed directly (comment-only, not a claim question).**
`docker.yml`'s header still read "This has never run" and its size-check step
still asked "against the Dockerfile's own claim of '~120 MB'" — both false:
`C-014` is `SUPPORTED` (`E-014`, run `34277853648`, merged as part of
`588514c`), and the Dockerfile stopped repeating a size number during that
same fix, on purpose, because the honest comparison was never measured
against a full-repo build context. This one needed no reject and no person —
it was a comment describing a past that already changed, the same class of
drift `release.yml`'s pre-rehearsal comments were before the dispatch, fixed
the same way: rewritten to say what happened, cited by run id and evidence
id rather than re-asserted from memory.

**what else was considered.** Silently updating `claims.jsonl` myself and
letting `claims.py --check` wave it through — rejected outright; that is
exactly the "machine decides two things mean the same thing" move
`CONSTITUTION.md` and `node_map.py`'s own docstring refuse for ontology
nodes, and there is no principled reason a claim without a dedicated checker
gets less discipline than one with one.

**reversible how.** The `docker.yml` comment edit is a comment; `git revert`
undoes it with no behavioral change either direction. The `claims.jsonl`
edit this entry asks for is additive (two fields on an existing row) and
`claims.py`'s own rule — a rejection keeps what it overturned — means even a
mistaken reject is legible and correctable later, never a silent overwrite.

**closed, 2026-09-12.** Ronaldo Čudina reviewed both findings and accepted
the resolution above. `rejected_by: "Ronaldo Čudina"` and
`rejected_on: "2026-09-12"` are now on the `C-001` and `C-008` rows in
`state/claims.jsonl` — a real name, not a machine-shaped one, exactly what
`apply_decisions.py`'s rule for `nodes.json` would have required if
`claims.jsonl` had the same script enforcing it. `claims.py --check`
recomputes both as `REJECTED`, which outranks the live contradicting
evidence per `status()`'s own documented order; `E-001` and `E-011` stay on
file untouched, because a rejection is not a deletion. `R-0014` records the
edit and its verification. One knock-on: `tests/test_claims.py`'s
`test_the_findings_this_session_made_are_on_file` hard-coded `C-001` to
`Status.CONTRADICTED` and had to be updated to `Status.REJECTED` — found by
running the suite, not by inspection, which is the same lesson `D-013` and
`D-014` already paid for about this file's own quoted figures: a status
this file asserts is a claim with a date, and the check that catches it
drifting is the test suite, not a second read.

---

## D-016 · What replaces C-001 and C-008's bug class, not just the instance

**date:** 2026-09-12 · **status:** ACCEPTED · **reversible:** yes, a config file

**context.** Closing `C-001` and `C-008` settles two instances. The operator
asked the sharper question: what stops the same class of bug from coming
back, and is there something more durable than a rejected row in a ledger.

**C-001's class was already closed, before this session touched it.**
`release_check.py::_check_floor` (built in `0c0d426`, the same commit that
found the original bug) does three things on every push, for both targets:
checks the declared `requires-python` floor against what the code's imports
actually need (`required_floor`, an `ast` scan for version-gated stdlib —
`enum.StrEnum` among them), imports on that floor's real interpreter when
one is present on the runner, and — the part that matters here —
`_floor_in_matrix` refuses if the CI job actually running the suite does
not name that exact floor version in its matrix. Proven live rather than
read and trusted: reverting `citegate`'s `requires-python` to the old
`>=3.10` in memory and re-running `_check_floor` against the real,
committed `engine.yml` job produces the exact refusal the original bug
should have produced — *"requires-python is >=3.10 and the code needs 3.11
(enum.StrEnum) — pip resolves, installs, and the first import raises."* The
C-001 class cannot recur silently; it was never insufficiently guarded, it
was guarded by something this investigation hadn't gone and read yet.

**C-008's class had no guard, and now does.** Dependabot's *security*
alerts are automatic for supported ecosystems with zero configuration —
that is how the 13 npm advisories behind `D-014` surfaced with no
`dependabot.yml` on file. A stale-but-not-vulnerable pin is invisible to
that channel: `actions/attest-build-provenance@v2` carried no CVE, so
nothing flagged it, and the only reason it was found at all was a manual
`git clone` of the action's own public repository during the release
rehearsal, reading tags by hand because `docs.github.com` is blocked at
this environment's proxy. That is not a repeatable process, it is a thing
that happened once because someone went looking.

Added `.github/dependabot.yml`, `version: 2`, four `updates` entries
matching every package manifest actually in the repository —
`github-actions` (directory `/`, which GitHub resolves against every
workflow regardless of where they live), `npm` (root), and `pip` for
`engine/` and `oss/citegate/` separately, mirroring how `release_check.py
--target` already treats them as two packages rather than one. Each groups
minor/patch bumps into one weekly PR per ecosystem so this does not trade
"nobody is watching" for "thirty PRs nobody reads"; a major bump still
opens its own PR, since that is where a breaking change is most likely to
hide. This does not re-detect the `@v2` staleness this session already
fixed by hand — it means the next one, on any action in any workflow, or
any dependency in any of the four manifests, surfaces as a PR instead of
requiring someone to go looking again.

**what else was considered.** Writing a bespoke checker (mirroring
`_check_floor`'s shape) that clones each pinned action's repository and
compares tags, run inside `release_check.py` or CI. Rejected: it would
duplicate a mechanism GitHub already runs for exactly this ecosystem, cost
a network call per pinned action on every push rather than a scheduled
weekly check, and be one more piece of this repository's own code to keep
correct — the same reasoning `extras_check.py` uses to prefer an honest
`unsupported` over a decorative adapter nobody needed.

**what was verified.** `.github/dependabot.yml` parses as the schema
Dependabot expects (`yaml.safe_load`, checked structurally). It sits
outside `.github/workflows/`, so `release_check.py`'s workflow scanner
(`_workflow_text`, globbing `.github/workflows/*.yml` only) does not see it
and none of its drift checks change. No test in the suite reads this file
or `EXECUTION_DECISIONS.md`'s own content directly, so — unlike the
`state/**` gap `D-012` found — there is no CI-coverage claim this addition
could be silently outside of.

**reversible how.** Deleting `.github/dependabot.yml` returns to today's
state exactly; Dependabot's security-alert channel is unaffected either
way, since that one needs no config file to begin with.

---

## D-017 · The citegate tag push was refused, and nothing public exists

**date:** 2026-09-12 · **status:** ACCEPTED, blocked on the operator ·
**reversible:** n/a (a finding; no tag exists anywhere but this sandbox)

**context.** The operator gave explicit, specific authorization — after
being shown exactly what it creates (a real, public, irreversible-once-
pushed GitHub Release) — to cut `citegate-v0.1.0`. `release_check.py
--target citegate --release` was run first and found only the documented
session-local `[project.urls]` artifact; the dirty-tree, tag-not-taken,
HEAD-on-remote-branch, license, version, floor and dependency checks all
passed clean. `git tag citegate-v0.1.0` created the tag locally at `1a109e1`.

**what happened.** `git push origin citegate-v0.1.0` was refused with a
clean `HTTP 403 Forbidden` at the git-receive-pack layer itself — confirmed
with `GIT_CURL_VERBOSE`: TLS handshake to `github.com` succeeded normally,
the `POST /RaveZona/omnex-factory/git-receive-pack` request went through,
and GitHub's own response was the 403, not this sandbox's proxy
(`recentRelayFailures` was empty at the time). Retried once per the
network-error protocol; same result.

**ruled out, in order:**
1. **A proxy problem.** `curl -sS "$HTTPS_PROXY/__agentproxy/status"`
   showed zero recent relay failures, and the TLS/HTTP exchange completed
   normally up to GitHub's own 403 response.
2. **A general access regression.** An ordinary branch push to
   `claude/production-ai-projects-bzz82l` on the same remote, in the same
   minute, succeeded normally — ruling out "this session cannot reach
   `RaveZona/omnex-factory` right now" as the explanation.
3. **The already-known cross-owner limitation.** Pushing the same tag
   directly to `Omnex-business-technologies/omnex-factory` was blocked
   too, but with a *different*, already-documented failure: this session's
   own proxy refuses it outright ("is not in this session's authorized
   repository set"), the same `add_repo` cross-tier restriction `D-013`
   already named. That is a different failure mode from the clean 403 on
   the old path, which rules out "the new owner is simply unreachable"
   as the explanation for the tag-specific refusal there.

**what is left, honestly.** The refusal is specific to *creating this tag
ref* — not the repository, not this branch, not this session's network
path in general. The most consistent unconfirmed explanation is a tag
protection rule or ruleset on the repository or organization restricting
who may create a tag matching this pattern, distinct from the branch-
protection ruleset `docs/TRANSFER.md`'s own step 6 already tracks as open.
This session has no tool that reads GitHub rulesets or tag-protection
settings (checked: the GitHub MCP toolset here has `get_tag`, `list_tags`,
`get_release_by_tag` and the Actions tools, nothing that reads a
repository's rule configuration) — so this cannot be confirmed from here,
only reported.

**not routed around.** No force, no alternate credential, no third push
path attempted beyond the two legitimate diagnostic pushes above. The
local tag object exists only in this sandbox's git store and was never
accepted by GitHub — confirmed with `get_tag`, which returns `404`.
Nothing public was created; `C-013` stays `UNKNOWN`, not `CONTRADICTED` —
being unable to push is not evidence the workflow itself would fail, the
same `UNKNOWN`-is-not-`FALSE` distinction `execution_state.json` already
holds elsewhere.

**what the operator can check, since this session cannot.** GitHub
Settings → Rules → Rulesets (and the older Settings → Tags → "Tag
protection rules") on `Omnex-business-technologies/omnex-factory`, for
any rule matching `citegate-v*` or `*`. If one exists and is intended to
block automated pushes, the tag needs pushing from a person's own
machine, or the rule needs a bypass naming this integration. If no such
rule exists, this is worth a second attempt from here — the failure was
clean enough to retry once resolved, but not something to keep retrying
blind.

**reversible how.** Nothing to reverse — no tag, no release, no artifact
exists anywhere outside this sandbox's local git store. `R-0016` records
the attempt and this finding.

**update, same day: repo-level Rulesets ruled out.** The operator checked
`Omnex-business-technologies/omnex-factory`'s Settings → Rules → Rulesets
directly — empty, "You haven't created any rulesets." A second push
attempt (`GIT_CURL_VERBOSE`, same method as the first) produced the
identical clean `HTTP 403` at the git-receive-pack layer, confirming the
refusal does not come from a repository-level ruleset. What is left,
untested from here: an **organization-level** ruleset (a separate setting
from the per-repository page just checked — `Omnex-business-
technologies`'s org settings, not the repo's), the older, separate
**Settings → Tags → "Tag protection rules"** page (distinct UI from
Rulesets, never checked), and the possibility that whatever GitHub App
this session's git access runs through simply was never granted a
permission scope covering tag-ref creation specifically — plausible
because some integrations gate "create tag" as a higher-risk action
separately from ordinary branch pushes, checkable only from
`https://github.com/settings/installations` (or the org's installed
GitHub Apps page) → the app → Permissions, which is the operator's page,
not this session's.

**resolved, same day: root cause found, and it is none of the above.**
The operator checked all three remaining candidates (org-level Rulesets,
the legacy Tag protection rules page, and the App's own Permissions page)
and none applied. `GIT_TRACE_CURL=1 git push origin citegate-v0.1.0`
finally surfaced the response body git's own error handling had been
swallowing (`unpack error` / `unexpected disconnect while reading
sideband packet` was the *symptom*, not the cause — git cannot parse a
plain-text error into a sideband packet and gives up before printing it):

```
ERR push contains a ref outside refs/heads/*; only branch updates are permitted.
```

This is GitHub's own git-receive-pack response, and it names the actual
mechanism: **the credential this session's git access uses is scoped to
`refs/heads/*` only**. Not a repository setting, not an org setting, not
a ruleset of any kind — a property of the token itself, enforced by
GitHub before any repository-level policy is even consulted. Every
candidate in the update above (repo Rulesets, org Rulesets, Tag
protection rules, App permissions as *read via the GitHub UI*) was a
reasonable place to look and every one came back clean because none of
them is where this restriction lives.

**what this means, plainly.** No setting on `github.com` that either the
operator or this session can reach will change this — the token
Claude Code Remote's git integration uses for this session is, by
design or by the platform's own default, branch-only. This reads as the
same shape `policy.py`'s own `ALWAYS_ASKS` set encodes one layer up in
this repository (`PUBLISH`, `DEPLOY`, `CREDENTIAL`, `FINANCIAL`,
`DESTRUCTIVE` — "cleared by no level alone") — except enforced here by
GitHub itself, on the actual credential, rather than by a document this
repository writes about itself. A tag is exactly the kind of ref a
platform would reasonably keep out of an agent's write scope: it is
what turns a rehearsal into a release.

**resolution.** `citegate-v0.1.0` needs pushing from the operator's own
machine, with their own git credentials — not from this session, and not
by any further diagnosis or retry here. `git tag citegate-v0.1.0
<commit>` at `1a109e1` (or wherever `master` is by the time this is
done) then `git push origin citegate-v0.1.0` from a real developer
checkout completes what this session correctly could not.

---

## D-018 · vitest 5 and TypeScript 7, verified rather than merged blind

**date:** 2026-09-12 · **status:** ACCEPTED · **reversible:** yes, a version bump

**context.** Dependabot's own `.github/dependabot.yml` (`D-016`) opened
`#26` (`vitest` 4.1.11 → 5.0.0), `#24` (`@vitest/mocker` 4.1.11 → 5.0.0)
and `#27` (`typescript` 5.9.3 → 7.0.2) within minutes of being merged.
`#26` failed CI outright: `npm ci` refused with `ERESOLVE` because
`vitest@5.0.0` peer-requires `@types/node@"^22.0.0 || >=24.0.0"` while
`package.json` still pinned `^20`. `#24` and `#27` both showed green CI in
isolation, which is not the same claim — `#24` alone would pair
`@vitest/mocker@5.0.0` with `vitest@4.1.11`, a combination nobody tests
together, and `#27` moves to `typescript-go`, a from-scratch Go
reimplementation of the compiler, not a version bump of the same code.

**what was actually checked, not assumed.** vitest 5's own release notes
list real breaking changes — mocks cleared by default before each test,
removed entry points, `sequential` replaced by `concurrent`, changed
`test.for/each` title formatting. Each was checked against this
repository specifically before touching a version number:

- Only one test file (`lib/__tests__/metering.test.ts`) uses any `vi.*`
  mocking, and it is a single `vi.fn()` created fresh inside one test with
  no `vi.mock()`, no shared module-level mock, no `beforeEach`/`afterEach`
  reset logic — the new default-clear-mocks behavior has nothing to act on
  here.
- No file uses `sequential`, `test.each`, or `test.for`.
- Every import is `from 'vitest'` or `from 'vitest/config'`, both kept
  entry points — none of the ones vitest 5 removed.
- `@vitest/mocker` is never imported directly; it is purely a transitive
  dependency `vitest` itself resolves.

**measured, not read from a changelog.** `@types/node` raised `^20` →
`^22` (the floor vitest 5 actually requires), `@vitest/mocker` and
`vitest` both to `^5.0.0`, `typescript` to `^7.0.2` — one `npm install`,
one dependency tree, tested together rather than three separate merges
each assumed harmless alone. Full gate, twice (once with `typescript@^5`
still pinned to isolate the vitest-only change, once with both bumped
together): `npm audit` 0 vulnerabilities, `tsc --noEmit` clean, `vitest
run` 68/68, `next build` 11/11 routes — no source file touched, the
version bumps alone are sufficient. `engine/tests/test_ci_contract.py`
re-run and unaffected, as expected for a root-level dependency change.

**what surprised, honestly.** Nothing broke. `tsc`'s own reported time
inside `next build` dropped from ~5.2s to ~0.8–1.2s under TypeScript 7 —
the Go rewrite's own performance claim, measured here rather than quoted.
That speed is not evidence of correctness, only of the compiler doing
less work per file or doing it faster; the type-check still reports zero
errors on the same source tree either way, which is the claim that
actually matters.

**what was not done, on purpose.** TypeScript 7 is a full reimplementation
of the compiler, not the same code with a version bump — a clean `tsc
--noEmit` and a clean `next build` prove this codebase's specific surface
compiles the same, not that every edge case of the type system behaves
identically. That residual uncertainty is stated rather than absorbed
into "verified": if a type-checking discrepancy surfaces later that this
local gate could not have caught, `typescript@^7` is the first place to
look, and reverting it alone (independent of the vitest/`@types/node`
pair) is a one-line change.

**why one PR, not three.** `#24`, `#26` and `#27` each looked
independently safe or independently broken; only running all three
together, then the whole gate, shows whether the combination is what
Dependabot's own grouping already argued for (major bumps get their own
PR because that is where a breaking change hides) but could not itself
verify, since it never runs three separate PRs' dependency trees merged
together. `#24` and `#26` are superseded by this branch directly; `#27`'s
version is the same target, verified alongside the pair it actually ships
next to rather than merged in isolation on the strength of its own green
CI.

**reversible how.** `git revert` on the four-line `package.json` diff
returns to `vitest@4.1.11`, `@vitest/mocker@4.1.11`, `@types/node@^20`,
`typescript@^5` exactly; `package-lock.json` regenerates identically from
a clean `npm install` either direction.

---

## D-019 · Eight CodeQL alerts, read before either accepted or dismissed

**date:** 2026-09-12 · **status:** ACCEPTED · **reversible:** yes, workflow config

**context.** The operator pasted GitHub's own Security tab: three `High`
"Clear-text logging of sensitive information" alerts and five `Medium`
"Workflow does not contain permissions" alerts, all opened the same day.
Copilot Autofix had already proposed a fix for the first one. Neither
accepted nor dismissed anything without reading the flagged code first —
a bot's severity label is not evidence, the same standard this repository
already holds itself to for every other claim.

**the three "clear-text logging" alerts are false positives, and the
finding is the same shape three times.** `engine/scripts/runs.py:420`,
`engine/scripts/env_check.py:160`, and
`engine/src/omnex/pipeline/__main__.py:53`:

- `runs.py`'s `--check` loop prints `f"{run.run_id}: carries {leak}"` where
  `leak` comes from `looks_like_a_secret()`
  (`omnex/factory/compile/bindings.py:74`). That function's own docstring
  states the reason it returns a description rather than a boolean: `"this
  file contains a secret" is not actionable and "line contains an inline
  bearer token" is`. Read the five entries in `_SECRET_SHAPES` directly —
  each pairs a fixed string ("an API key prefix", "an inline bearer
  token", …) with a compiled pattern, and the function returns the fixed
  string on a match. No `.group()` call anywhere. The worst that print
  statement can ever emit is `carries an inline bearer token` — never the
  token.
- `env_check.py:160` prints `secrets = sum(1 for e in documented.values()
  if e.get("secret"))` — a count of how many manifest entries are *marked*
  secret, never a name or a value.
- `pipeline/__main__.py:53` prints `SECRET_ENV` (the literal string
  `"OMNEX_WEBHOOK_SECRET"`) inside the branch that only runs `if not
  secret:` — the actual value is empty in every code path that reaches
  this print, and the local variable holding it (`secret`) is never
  referenced in the message at all.

CodeQL's taint tracker most plausibly flags all three because a
value *associated* with a secret — by name, by being a description of
one, or by co-existing in the same function as a variable called `secret`
— reaches a `print()`, without modeling that `looks_like_a_secret`'s
return value is a closed set of five safe strings. **Not applying
Copilot's proposed fix**: redacting `runs.py`'s output would actively
undo the documented reason the function returns a description at all.
Recommended to the operator: dismiss all three as false positive, with
the `_SECRET_SHAPES` read above as the reason on file. This session has
no tool that dismisses a GitHub code-scanning alert, so the dismissal
itself is the operator's action.

**the five "workflow does not contain permissions" alerts are real, and
fixed.** `ci.yml`, `engine.yml`, `docker.yml` and `quality-gate.yml` had
no top-level `permissions:` block at all — `release.yml` already does
(`contents: read`, widened per-job only where a job actually reaches
outside the repository), which is why `release.yml` was never flagged and
is the pattern this fix mirrors exactly. Checked what every flagged job
actually does before choosing a scope, rather than defaulting to a
guess: `ci.yml`'s one job checks out, audits, type-checks, tests and
builds; `engine.yml`'s two jobs (`check`, `citegate`) lint, type-check and
test; `docker.yml`'s one job builds and inspects an image, never pushes
it anywhere; `quality-gate.yml`'s one job runs the eval gate and uploads
an artifact — `actions/upload-artifact` authenticates with its own
runtime token, not the `permissions:` block, so this needs no write
scope either. None of the four writes to the repository, comments on a
PR, or reaches outside it. `contents: read` — the least a workflow can
declare — is correct for all four, not a guess narrowed down from
something broader.

**what was verified.** All four edited files still parse as valid YAML
with the new key read back correctly. `test_ci_contract.py` and
`test_release_check.py` — the two suites that read these exact workflow
files (`covers_changes()`, `jobs()`, `_uncommented()`, `ci_job_running()`)
— stay green, confirming a new top-level `permissions:` key does not
confuse either reader. Full engine gate re-verified: ruff check/format,
invariant_map, state_map --check, full pytest all green — no Python
source changed, so this was expected rather than newly discovered.

**what else was considered.** Widening any job's permissions beyond
`contents: read` "to be safe" — rejected; a permission nothing uses is
exactly the shape this alert exists to catch, one level up.

**reversible how.** Four one-line `permissions:` blocks; `git revert`
removes them and returns each workflow to implicit default permissions,
which is the state that was flagged in the first place.

---

## D-020: MCP tool permission scoping — one real gap found in a handbook review

**context.** The operator asked for a thorough review of
`github.com/umang-algo/agentic-ai-handbook` — a 21-chapter coding
handbook — for anything worth building into `engine/mcp`, after sharing
architecture diagrams and a lesson on a "4-layer secure agent"
(Security → Tools → Memory → LLM). The review was read in full, not
skimmed for confirmation: most of the handbook's concepts are already
implemented in `engine/`, several more rigorously than the lesson's own
example code (`memory.ShortTermBuffer` is token-budgeted; the lesson's
own in-memory buffer is turn-budgeted only), and several more are
outside this product's current scope (healthcare/legal/finance vertical
agent chapters). Reporting every chapter as a "win" to match the
operator's framing would have been the same failure this file already
warns against elsewhere — manufacturing prestige instead of measuring
it. Exactly one concrete, actionable gap was found: `McpServer` had no
notion of per-tool access control. Every registered tool was visible
and callable by every caller of `tools/list` and `tools/call` — correct
for a single-tenant server, wrong the moment one server exposes both a
read-only tool and something destructive (the lesson's own example is
`delete_all`) to callers who should not all see the same list. The
operator confirmed building exactly this one gap ("Da, gradi to"), not
a broader mandate to build everything the handbook mentions.

**what was built.** `ToolSpec.required_permission: str | None = None` —
deliberately never read from or written to `from_wire()`/`as_dict()`,
because a remote server claiming its own permission scope over the wire
would let a compromised or malicious server grant itself access it
should not have; scoping is a local, server-side policy decision only.
`McpServer.available_to(granted: frozenset[str] | None)` filters
`self.tools`, with `granted=None` returning everything unfiltered — the
same default `handle()`, `_on_request()`, `_call()` and `serve()` all
carry, so every caller and every one of the 47 pre-existing tests keeps
seeing exactly what it always saw. Scoping is opt-in per tool and
opt-in per caller; nothing already deployed loses a tool by this
landing.

**the one real design decision: what an unauthorized call looks like.**
The handbook's own example (`ToolOrchestrator.get_available_tools()`)
filters the list a caller sees but says nothing about what happens if
that caller tries to call a filtered-out tool by name anyway. Here,
`_call()` refuses a scoped-and-unauthorized tool with the *exact* same
error, code and `available` payload as a tool that does not exist at
all — never a distinct "permission denied". A distinguishable refusal
confirms a scoped tool's existence to a caller who is not supposed to
know it is there, which is itself a capability disclosure. This is my
own security-engineering judgment, not copied from the reference
material, and it is the one place this feature goes further than the
lesson it was prompted by.

**what was verified.** Four new tests
(`test_an_unscoped_caller_sees_and_calls_everything`,
`test_a_scoped_tool_is_invisible_to_a_caller_without_the_permission`,
`test_calling_a_scoped_tool_without_permission_reads_exactly_like_no_such_tool`,
`test_a_caller_with_the_right_permission_gets_the_scoped_tool_back`) plus
all 47 pre-existing `test_mcp.py` tests, green. Full engine gate run
clean: ruff check/format, mypy, invariant_map (9/9), env_check,
extras_check, `release_check.py` both targets (citegate's known
session-local `[project.urls]` artifact is the only non-passing check,
unchanged from every prior run this session), claims/runs/spine checks,
`state_map.py` regenerated and agreeing in both directions,
`apply_decisions.py --dry-run`, full `pytest tests/ -q`, and
`mutate.py` at 29/29 killed. Recorded as R-0019.

**what else was considered.** A boolean `is_allowed(tool, granted)`
check exposed as a separate public method — rejected, because a second
entry point for the same decision `available_to()` already makes is
exactly the "two copies that can diverge" shape `twin_splitters_agree`
exists to warn about; `_call()` derives `allowed` from `available_to()`
directly instead. Encoding permissions as a hierarchy or a policy
object (roles, wildcards) — rejected as unearned complexity: nothing in
this codebase yet has more than one caller identity, and a flat
`frozenset[str]` is the smallest structure that the one real requirement
(a caller either holds a named permission or does not) needs.

**reversible how.** Three files changed
(`mcp/tools.py`, `mcp/server.py`, `tests/test_mcp.py`), all additive —
every new parameter defaults to `None`/unrestricted. `git revert` removes
the feature cleanly; no caller of the prior API needs to change.

---

## D-021: three more handbook gaps — found because the first pass was challenged

**context.** D-020 called the review of `agentic-ai-handbook` complete after
finding one gap (MCP permission scoping). The operator pushed back — "is that
really all we can extract from all 21 chapters?" — and the honest answer, on
inspection, was that the first pass had only read chapter READMEs for most
chapters, not the substantive `.py` lesson code, which is not the thorough
review the operator originally asked for. A second pass, done properly this
time (every chapter's actual code read and compared against a specific
`engine/` module, not a README skim), found three more genuine, small,
concrete gaps. Two things are worth naming about the process itself: first,
that a "prestige" audit is only worth the name if it can come back with zero,
one, or many findings depending on what is actually there — the second pass
was instructed explicitly not to pad the list to look more thorough, and it
still surfaces exactly three, not a round or flattering number. Second, the
operator's own separately-supplied full-repository audit (D-021's sibling
work, see the state-sync commit) independently named "no vanity numbers,
no assumed evidence" as its own operating rule — the same discipline applied
from a different direction landed on the same three gaps, which is some
evidence the discipline is doing real work rather than being a slogan.

**gap 1 — LLM-as-judge eval metric.** `evals/metrics.py`'s own module
docstring already said this adapter was never built and named the shape it
would take: "a model call scored against `omnex.llm.LanguageModel` so its
cost lands in the same ledger as everything else." `evals/judge.py` builds
exactly that: `judge_quality()` sends one rubric prompt through a
`LanguageModel`, parses a strict `SCORE: <0-10> REASON: <...>` reply (a
malformed or out-of-range reply scores 0.0 with the raw text on file, never a
best-effort guess — a judge model itself misbehaving is the one time a
score most needs to look visibly wrong), and returns `JudgeResult{metric,
cost}` so the spend is never dropped on the floor. It does not gate any run:
no change was made to `runner.py`'s `Gate`/`EvalRunner` at all, because the
per-metric threshold override those already read (`thresholds={"llm_judge":
0.0}`) is the existing mechanism for exactly this, and adding a second one
would be the kind of duplicate machinery `twin_splitters_agree` warns about
at a different layer. Why it matters concretely: OMNEX's actual product
(`lib/modules/registry.ts` — ad copy, email subject lines, landing-page
headlines) generates content none of the four existing deterministic metrics
can score, because all four need something to compare against (a relevant
chunk id, an expected answer, a required citation) and there is no
"reference ad" a new one can be F1-scored against.

**gap 2 — concurrent MCP tool dispatch.** `McpClient.call_tool()` sends one
request and blocks on that request's own reply before another can be
issued. When one LLM turn returns several independent tool calls — the
standard `parallel_tool_calls` shape — every call beyond the first today
adds a full synchronous round trip directly to wall-clock time, which is
exactly what `graph.runtime.Budget.max_seconds` exists to protect against.
`call_tools()` sends every request in a batch before blocking on any reply,
then demuxes incoming messages by id — reusing `_exchange()`'s own
desynchronisation guard ("an id this client did not send is refused loudly,
never accepted as the next thing off the wire"), extended from one
outstanding id to a set. Results return in call order regardless of reply
order. A protocol-level error aborts the whole batch, matching how a single
call's own protocol error aborts; a tool-level failure (`isError`) stays a
normal, billed result and does not abort its siblings, matching how
`call_tool` already treats a tool-level failure. `MemoryTransport` still
delivers everything in send order, so the test suite is honest about
exercising the correlation logic rather than asserting a wall-clock
speedup this transport cannot demonstrate — the saving is real only against
a transport where the server can act on requests concurrently (a
subprocess, a socket), which is the transport this method exists for.

**gap 3 — reasoning-model output was never separated from the answer.**
`Completion.text` is the one field every consumer in this engine treats as
"the answer" — `rag.ground`, `evals.metrics`, `guard.output`, the router.
Neither adapter (`llm/ollama.py`, `llm/litellm_adapter.py`) stripped or
separated an inlined reasoning block, and this was not hypothetical:
`llm/catalog.py`'s `Tier.REASONING` is already the router's top escalation
tier, meaning real production traffic already lands on reasoning models at
the router's most expensive step. A leaked `<think>...</think>` block would
silently contaminate RAG grounding (checking citations against reasoning
chatter), eval metrics (scoring faithfulness against polluted text) and any
structured-output parser downstream — with nothing raising anywhere, the
same silent-failure shape as the missing `usage` block that made cost
panels read €0.00 on real runs. `llm/reasoning.py`'s `split_reasoning()`
extracts every `<think>` block (not only the first — a model that reasons,
narrates a tool call, and reasons again keeps all of it) into a new
`Completion.reasoning` field. Both adapters prefer a provider's own
separated field when one exists (Ollama's `thinking` key on newer daemon
versions, LiteLLM's normalised `reasoning_content` on providers that report
one) and fall back to tag-splitting only when the provider does not
separate it — the same "trust the provider's own claim before parsing
around it" instinct as `Usage.cached_input_tokens` being read from the
provider rather than estimated.

**what was verified.** 5 new tests for `judge_quality` (well-formed reply,
malformed reply, out-of-range score, evidence included/omitted in the
prompt), 6 for `call_tools` (empty batch, order-preserving results,
tool-level failure billed without aborting, unpriced-tool refusal before
any request is sent, over-budget refusal before any request is sent, a
reply outside the batch refused), 5 for `split_reasoning` in isolation, and
5 for the two adapters via `monkeypatch` at the actual network/library
boundary (`urllib.request.urlopen` for Ollama, `sys.modules["litellm"]` for
LiteLLM, since `litellm` is imported lazily inside `complete()` and is not
installed in this environment — zero required dependencies, so faking it at
`sys.modules` rather than as a module attribute was the only way to
exercise that path without the extra). Full engine gate green: ruff
check/format, mypy, all 9 enforced invariants, `env_check`, `extras_check`
(the `evals` extra's `unsupported, 0/3 imported` status is unaffected —
`judge.py` uses zero new dependencies, built entirely on the engine's own
`LanguageModel`), `release_check.py` both targets (only the documented
session-local citegate-URL artifact), `claims.py --check`, `runs.py
--check`, `spine_check.py`, full `pytest tests/ -q`, and `mutate.py` at
29/29. One expected side effect required its own two-script regeneration:
`node_map.py`'s `refresh()` proposed `omnex.llm.split_reasoning` for a gap
node the moment the symbol existed, which changed `nodes.json`'s
gap/proposed counts (461/46 → 460/47) and required `node_dossier.py` and
`state_map.py` to be re-run in that order (dossier reads `nodes.json`;
state reads both) before their own committed-file tests passed again — the
same "a symbol appearing anywhere in `engine/` moves the queue" behaviour
CLAUDE.md already documents for the MCP module landing. Run recorded and
closed as R-0021. Re-measured CLAUDE.md's test count again after landing
all three: 1,256 (was 1,235 after D-020 alone).

**what else was considered.** For gap 1, gating the judge metric by default
and requiring an explicit opt-OUT — rejected, because the module docstring
this whole feature is answering already states why a noisy metric must
never be a default gate; opt-in-to-gate is the only direction that does not
risk a variance-driven regression gate teaching a team to disable it. For
gap 2, true `asyncio`-based concurrency — rejected as disproportionate: this
engine has zero async code anywhere and introducing it for one method would
mean either a sync/async split of `McpClient` or an event loop bridge, for a
benefit (real OS-level concurrency) that `MemoryTransport`-backed tests
cannot demonstrate anyway; the send-everything-then-drain pattern captures
the actual saving (avoiding N sequential round trips) without the async
surface. For gap 3, clamping an out-of-range provider score or silently
discarding an unparseable block — rejected for the same reason judge.py
refuses to guess: a provider or model behaving unexpectedly is exactly the
moment a wrong-looking answer is more useful than a plausible-looking one.

**reversible how.** Three independent, additive changes, each revertible on
its own: `evals/judge.py` is a new file nothing else calls yet;
`McpClient.call_tools()` is a new method beside the unmodified
`call_tool()`; `Completion.reasoning` defaults to `""` and both adapters
fall back to it being empty when `split_reasoning` finds nothing, so no
existing caller's behaviour changes unless the model it talks to actually
emits a `<think>` block.

---

## D-022: Phase 0 truth lock — three gates were lying, and the guard could not see any of them

**context.** The operator supplied a "Sovereign Execution & Proof
Architecture" standard. Its §3 and §8 Phase 0 both require a Repository
Truth Pass *before* any new implementation, so that was done first rather
than building anything the standard asks for. The pass found that three of
the thirteen maturity gates in `execution_state.json` asserted the absence
of things that had since arrived — the exact defect class this repository
already paid for once with gates 1 and 2, and built a structural fix
against.

**what was false.** `10_distribution` said "release_check.py and release.yml
do not exist; no artifact has been built, signed or published" while
`engine/scripts/release_check.py` is in the CLAUDE.md gate block and in CI,
and `.github/workflows/release.yml` exists and has actually executed once
(the `workflow_dispatch` rehearsal). `9_autonomy` said "no run ledger
exists" while `state/runs.jsonl` held 39 hash-chained runs that
`runs.py --check` verifies on every CI run. `6_security` said "no secret
scanning, dependency audit, SBOM or signed release exists yet" while
`npm audit --audit-level=moderate` runs at `ci.yml:53`,
`.github/dependabot.yml` sits beside it, and `attest-build-provenance@v4`
is wired into the release workflow.

**why the guard missed all three — four independent reasons.** This is the
part worth recording, because the guard
(`test_no_gate_claims_a_file_is_absent_while_it_sits_in_the_repository`)
was written precisely to stop this and was itself green throughout.
(1) Its regex required `<file> does not exist`, singular; gate 10 said
"**do** not exist", plural, and the construction "A.py and B.yml do not
exist" also put the first filename further back than the pattern reached.
(2) Gates 6 and 9 denied existence with no filename at all, so a
path-keyed scan had nothing to resolve. (3) Its path bases were
repo/engine/engine-scripts, which do not include `.github/workflows`, so
even once the phrasing was understood `release.yml` resolved to nothing and
read as clean. (4) Its extension alternation was `py|json|jsonl|md|yml|yaml`
— `json` before `jsonl` — so `state/claims.jsonl does not exist` truncated
to `state/claims.json`, a path that does not exist, meaning **gate 2, one
of the two cases the guard was written for, could never have been caught by
it**. A guard nobody has seen fail is a guard nobody has tested; this one
had four holes and a docstring describing the bug it was not catching.

**what was done.** The three gates now derive, like gates 0/1/2 already
did, from three new fact helpers: `_run_ledger()` (run count, chain
integrity via the ledger's own `broken_links`, runs by autonomy level),
`_release_tooling()` (both files present) and `_supply_chain()` (dependency
audit in CI, Dependabot config, provenance attestation, SBOM — each read
from the workflows through `release_check._uncommented`, the repository's
one comment-stripping reader, rather than a second copy). The scan itself
moved out of the test and into `state_map.denied_existing_files()`, which
the test now calls — one implementation, for the same reason
`one_symbol_resolver` and `twin_splitters_agree` exist — and a new test
feeds it the three verbatim drifted strings plus both original bites and
requires it to catch every one.

**two boundaries stated rather than papered over.** CodeQL default setup
and secret scanning are GitHub *settings*, not files; a repository scan
cannot see either, so `6_security` reports neither present nor absent and
says so. A control this process cannot observe is unobserved, which is not
the same as missing — the distinction the whole file exists to keep, and
exactly the standard's §7 discipline. Separately, `10_distribution`
deliberately does not derive whether anything was published: reading
`git tag` would disagree between a full clone and CI's shallow checkout,
producing a validator that fails on where it ran, and C-005/C-011/C-013 in
`state/claims.jsonl` already track publication as claims about other
systems.

**a finding deliberately NOT acted on.** Deriving `9_autonomy` immediately
contradicted a sentence in my own first draft of it ("nothing above L3 has
ever been taken"): the ledger shows one `L4_EXTERNAL` run, R-0005, the
citegate tag-push attempt — and its `result` is still `UNKNOWN`, never
closed with `--observe`. The gate now derives "N runs above L3, of which M
recorded a successful outcome" instead of asserting anything. R-0005 was
left open rather than closed: D-017 established that *a* tag push was
refused by a platform ref restriction, but closing R-0005 on the strength
of a later run's finding would be inferring an outcome rather than
observing one, which is the standard's §7 and this repository's own rule.
It is the operator's to close.

**what else was considered.** Widening the guard's regex to also match the
two new phrasings and leaving the three gates as prose — rejected: that
keeps three literals that must be re-read by a human to stay true, and the
whole lesson of gates 1 and 2 is that nobody re-reads them. Deriving the
gates and leaving the guard alone — rejected for the mirror reason: the
next gate added will be prose again, and a guard with four holes would not
catch it either.

**reversible how.** `git revert` restores the three prose gates and the
narrower guard. Nothing outside `state_map.py`, `test_state_map.py` and the
regenerated `execution_state.json` changed.

---

## D-023: a capability registry, capped where a repository scan actually ends

**context.** The operator's Sovereign Execution Standard, §8 Phase 1, calls
for a "canonical capability registry" carrying an evidence ladder (E0
UNKNOWN through E7 OUTCOME PROVEN) and the invariant "every material claim
must resolve to an evidence object." D-022's truth lock had already found
gate `3_implementation` saying "measuring coverage per capability needs a
capability registry that does not exist" as a literal — this is what closes
that literal, the same way `_run_ledger`/`_release_tooling`/`_supply_chain`
closed the other three.

**scope, stated rather than implied.** `ontology/capabilities.json` seeds
**8** capabilities: money as pico-dollar integers, the injected clock, cost-
aware routing, RAG citation grounding, the injection fence, MCP per-tool
permission scoping, hybrid retrieval, and the eval regression gate. Chosen
because each one's evidence is unambiguous, not as an attempt at the
platform's full surface — the source file's own `$comment` says this in
words, and `state_map.py`'s gate 3 now says it too ("8 is a first,
deliberately small cut"). A registry padded to look complete on day one is
exactly the shape §26's "Score Anti-Gaming Rule" exists to refuse.

**what is derived, and what a person still states.** A person writes name,
symbol, description, contract, dependencies, security requirements,
limitations, known risks, economic relevance — the standard's own minimum
field set, checked non-empty by `test_every_capability_states_dependencies_
and_risks`. Everything the standard calls evidence is computed by
`capability_map.py` from the current tree: `omnex.core.symbols.resolve`
decides E1 (declared, does not import) versus code-present; a grep over
`engine/tests/` for the bare symbol name decides E3 (tested); a grep over
`engine/src` — excluding the symbol's own defining file, so a class is never
evidence of its own integration — decides E4. This is the same discipline
`nodes.json`'s `verified` field already enforces one level over: the
interesting number is never typed by whoever wrote the entry.

**the ladder stops at E4, on purpose and said so on every entry.** E5
(operationally verified), E6 (production verified) and E7 (outcome proven)
each require evidence from something this repository does not have — a
running deployment, an operator, a payment. Gate `5_production` already
carries this exact reason as UNKNOWN. Rather than omit the three rungs
silently or guess at them, every capability's rendered entry states
`E5_UNKNOWN_NOT_OBSERVABLE` against a single shared reason string —
`NOT_OBSERVABLE_REASON` — so the sentence cannot drift into eight
almost-identical copies the way the split gate literals did in D-022.
`test_e5_through_e7_are_never_claimed` holds the ceiling in place.

**what was verified.** All 8 declared symbols resolve (`test_every_declared_
capability_actually_resolves`); `derive_all()` is idempotent, run twice in
the same test; every `E4_INTEGRATED` capability's `integrated_by` list is
under `src/omnex` and excludes its own defining file
(`test_a_capability_is_not_integrated_by_its_own_defining_file` — written
because excluding the defining file was the one detail in `_referencing_
files` most likely to be forgotten by a future edit, not because an earlier
version of this session's own code shipped without it; no such bug was
observed here). The committed `CAPABILITIES.md` matches a fresh render, checked
the same way `INVARIANTS.md` is. `state_map.py`'s gate 3 was wired to
`capability_map.summarise()` — imported, not re-derived, the same reason
`_registry()` imports `claims` rather than re-reading `claims.jsonl` — and
`test_gate_3_never_claims_more_capabilities_than_the_registry_holds` checks
the gate's own count against the registry's rather than a hard-coded
number, so the two cannot quietly diverge the way D-022's gates did. Full
engine gate green: ruff/mypy, all invariants, both release targets, claims/
runs/spine, `state_map.py --check`, full `pytest` (1,267 tests, up from
1,256), `mutate.py` 29/29. `capability_map.py --check` added to both
CLAUDE.md's gate block and `engine.yml`, in that order, so
`test_ci_contract.py`'s superset requirement holds without needing its own
change. Run recorded and closed as R-0023.

**what else was considered.** A capability's evidence stored as a boolean
per E-level (`tested: true`, `integrated: true`) rather than one ladder
value — rejected, because the standard's own ladder is explicitly ordinal
("stronger evidence has a higher level") and a set of independent booleans
can produce an incoherent state (integrated but not tested) that the
ordinal design refuses by construction. A separate machine-readable JSON
artifact alongside the rendered `CAPABILITIES.md` — deferred, not rejected:
nothing yet consumes capability data as JSON outside `state_map.py`, which
already imports `capability_map` directly, so a second serialisation format
would be surface with no reader, the same objection `docstrings_name_the_
failure` raises about padding for its own sake.

**reversible how.** Four new/changed files
(`ontology/capabilities.json`, `scripts/capability_map.py`,
`tests/test_capability_map.py`, `ontology/CAPABILITIES.md`) plus additive
changes to `state_map.py`, `test_state_map.py`, `CLAUDE.md` and
`engine.yml`. `git revert` returns gate 3 to its D-022 wording; nothing
outside these files and the regenerated `execution_state.json` changed.

---

## D-024: every GitHub Action pinned to a commit — and a wrong pin caught before it shipped

**context.** Sovereign Execution Standard, Phase 2, names "pinned or
controlled GitHub Actions" as a required supply-chain control. A repository
scan for D-022's `_supply_chain()` had already measured what security
tooling exists here; it had not asked whether the workflows trust a moving
target. They did: every one of the 19 `uses:` lines across all five
workflow files pinned to a bare major-version tag (`@v7`, `@v8`, `@v4`),
never a commit.

**why a tag is not a pin.** `actions/checkout@v7` is a promise the workflow
file cannot keep, because `v7` is a ref the action's own maintainer
controls, not this repository. If that maintainer's GitHub account were
compromised — this has happened to real, widely-used actions — `v7` could
be moved to different code with no change here at all, and every workflow
would run it on its next trigger with nothing in this repository's history
showing why. A 40-character commit SHA is immutable by construction; a
version tag is a claim about intent.

**the mistake this caught before it shipped.** Resolving each tag meant
cloning the action's own public repository (the git proxy's anonymous
public-GitHub lane, the same one `add_repo` uses) and reading the commit
`v7`/`v8`/`v4` currently points to. Doing this for all six distinct actions
(`checkout`, `setup-node`, `upload-artifact`, `download-artifact`,
`attest-build-provenance`, `setup-uv`) surfaced a real inconsistency:
`git rev-parse v4` on `attest-build-provenance` and `git rev-parse v7` on
`setup-uv` returned a **tag object** SHA, not the commit SHA the tag points
to — those two repositories use *annotated* tags, where the other four use
lightweight ones. `git cat-file -t <ref>` on all six showed `tag` for those
two and `commit` for the rest; dereferencing with `<ref>^{commit}` gave the
right answer in every case. Pinning to the tag-object SHA would have
produced a workflow that parses as valid YAML, passes review at a glance,
and fails the moment it runs — `uses:` requires a commit, and a tag object
is not one. Checking uniformly across all six rather than assuming the
first four generalised is what caught it; the standard's own §22
("adversarial verification... how can this be proven to NOT work") is the
posture that made checking the assumption worth doing at all.

**what was done.** All 19 existing pins plus one new one (20 total) now
name a full 40-character commit SHA with a `# vX.Y.Z` comment — not read by
any checker, but the only way a future reviewer can run
`git log <old>..<new>` in the action's own repository to see what a version
bump actually changes. `scripts/actions_pin_check.py` derives this rather
than trusting it stays true: it reuses `release_check._uncommented` and
`._workflow_text` (no second comment-stripping reader — the
`twin_splitters_agree` lesson), extracts every `uses: action@ref`, and
fails on any `ref` that is not `^[0-9a-f]{40}$`. Added
`actions/dependency-review-action` to `ci.yml`, gated to `pull_request`
only (it has no base ref to diff against on a plain push) — reviews a
PR's dependency *diff* against known vulnerabilities and licence
incompatibilities, which is a different question from `npm audit`'s
"is anything currently installed insecure."

**wired in, not bolted on.** `state_map.py`'s `_supply_chain()` now also
reports `actions_pinned_to_sha`/`actions_total` (via
`actions_pin_check.summarise()`, imported) and
`dependency_review_in_ci`; gate `6_security`'s evidence carries both.
`test_gate_...` in `test_state_map.py` asserts `actions_pinned_to_sha ==
actions_total > 0` directly against the live repository, so a future
unpinned addition fails this test rather than only `actions_pin_check.py`
itself — two readers of the same fact, deliberately, since one is the gate
CI runs standalone and the other is the state the gate feeds.

**what was verified.** `actions_pin_check.py` reports 20/20; every edited
workflow file still parses as YAML; `test_ci_contract.py` still passes,
so CI remains a superset of CLAUDE.md's gate block with no separate edit
needed there; full engine gate green (ruff/mypy, all invariants, both
release targets, claims/runs/spine, `state_map.py --check`,
`capability_map.py --check`, full `pytest` — 1,276 tests, up from 1,267 —
and `mutate.py` 29/29).

**what else was considered.** Pinning to each action's `v7.0.0`-style
first point release instead of whatever `v7` currently resolves to —
rejected: that would silently roll every action *backward* to its first
release under the major version, changing what the workflows actually run
today rather than freezing it. Writing the pin-checker to also verify the
SHA belongs to the named action's actual repository (fetch and confirm) —
deferred: `actions_pin_check.py`'s own docstring says explicitly what it
does not check ("whether the currently-pinned commit is itself
trustworthy") rather than silently implying more coverage than it has.

**reversible how.** Five workflow files with only `uses:` lines changed
(no trigger, job, or step logic touched), plus
`scripts/actions_pin_check.py`, its test, and the additive `state_map.py`/
`CLAUDE.md`/`engine.yml` changes. `git revert` returns every action to its
tag-pinned form.

---

## D-025: an SBOM, generated in a clean room and read back before it is trusted

**context.** Sovereign Execution Standard, Phase 3 (BUILD → PROVENANCE →
RELEASE CHAIN), names SBOM generation as part of the chain from source to a
released artifact. D-022 and D-024's truth passes had both already measured
`sbom_generated: False` — the one supply-chain control confirmed genuinely
absent, not merely unobservable like CodeQL or secret scanning. `citegate`
is the only thing `release.yml` actually builds, so it is the only target.

**the mistake this caught before it shipped, again.** The first working
version scanned the wrong venv: `pip install cyclonedx-bom .` into one
environment, then pointing `cyclonedx-py environment` at that SAME
environment's interpreter, reported 64 components for citegate — every
package on the system Python, then 35 even in a fresh venv, because
`cyclonedx-bom` and its own ~30 transitive dependencies (`lxml`,
`jsonschema`, `packageurl-python`, `lark`...) were sitting in the venv being
described. Citegate would have been reported as depending on a JSON schema
validator it has never imported. The fix — install ONLY the target package
into a clean venv, then run `cyclonedx-py` from an isolated location
(`uvx --from cyclonedx-bom`) pointed AT that venv's interpreter rather than
its own — was verified locally before it went anywhere near CI: this
environment's network allowlist includes PyPI, so the entire recipe (`uv
venv` → `uv pip install .` → `uvx --from cyclonedx-bom cyclonedx-py
environment` → read-back) was run for real, twice, producing a real
CycloneDX 1.6 SBOM confirming what CLAUDE.md already claimed in prose:
citegate has **zero** dependency components. That real output is committed
as `engine/tests/fixtures/citegate-sbom.json` so the test suite holds the
actual shape in place without needing network or a build step itself.

**the read-back, not just the generation.** `scripts/sbom_check.py` is the
second half, and the more important one: a `cyclonedx-py` exit code of 0
proves the tool ran, not that what it wrote describes the right thing. It
loads the generated SBOM and `pyproject.toml` and checks `bomFormat`,
`specVersion`, and that `metadata.component`'s name and version match the
package actually being released — catching, for instance, an SBOM
generated against a stale checkout that still says the previous version.
This is the standard's own §2 stated as code: "a signed artifact is not
automatic production security." Wired into `release.yml`'s `build` job
immediately after generation, using the same clean venv's Python (deleted
right after, since it has served its purpose) — no new dependency on the
job beyond what `uv` already manages.

**a second thing caught while wiring it in.**
`test_every_file_a_workflow_names_exists` — the structural guard that
already exists to catch a workflow naming a file that is not in the
repository — flagged `dist/citegate.cdx.json` as a phantom, because that
file does not exist in the repository; it is generated by the very `run:`
block that also reads it back. The honest fix is not an allowlist entry for
one filename, it is recognising the shape: a token following `-o` or
`--output-file` earlier in the same workflow file is a declared OUTPUT, not
an expected input, and should never have been checked for pre-existence in
the first place. `_DECLARED_OUTPUT` in `test_ci_contract.py` implements
that structurally, scoped per workflow FILE rather than per physical line —
`_run_commands` already splits a multi-line `run: |` block into one entry
per line, so the `-o file \` line and the line reading that file back are
two separate list entries, and the exclusion has to see across all of them
or it sees neither. A new test
(`test_a_declared_output_does_not_hide_a_genuine_phantom`) proves the
exclusion recognises the real SBOM path as declared AND still flags the
original `lib/__tests__/agent-memory.test.ts` phantom from this test's own
docstring — the fix closes exactly the new gap, not the old one it exists
to guard.

**what was verified.** `sbom_check.py`'s tests run against both synthetic
payloads (every field it checks, exercised in isolation) and the real
fixture generated this session; `release.yml` still parses as YAML after
the new step; `test_ci_contract.py` passes with the new exclusion and the
regression test proving it is not a blind spot; `state_map.py`'s
`sbom_generated` fact now reads `True` and gate 6's prose was corrected
from "what is absent is an SBOM" to name what actually changed, without
overclaiming — the gate still says "none of this has run for real," since
`release.yml` has been rehearsed exactly once via `workflow_dispatch` and
this step has never executed there. Full engine gate green (ruff/mypy, all
invariants, both release targets, claims/runs/spine, `state_map.py --check`,
`capability_map.py --check`, `actions_pin_check.py`, full `pytest` — 1,286
tests, up from 1,276 — `mutate.py` 29/29).

**what else was considered.** Generating the SBOM from `pyproject.toml`
alone (a requirements-style SBOM, no venv needed) — rejected: citegate
declares zero required dependencies, so a manifest-only SBOM would be
correct today and silently stale the day a real dependency is added,
whereas the environment-based approach describes what is actually
installed regardless of what was declared, the same "measure the code, not
the promise" instinct `extras_check.py` already applies one level over.
Committing a full second SBOM fixture representing a hypothetical
dependency-bearing package (to test the code path where components are
non-empty) — deferred: the synthetic `_sbom()` helper in the test file
already exercises that path without needing a second real build.

**reversible how.** One new script (`sbom_check.py`), its test and fixture,
one new step block in `release.yml` (no existing step's logic changed, only
inserted between two of them), and the structural fix plus its own test in
`test_ci_contract.py`. `git revert` removes the SBOM step and the fixture
together; the exclusion fix in `test_ci_contract.py` can be reverted
independently since nothing else depends on it yet.

---

## D-026: liveness and readiness, scoped to what this sandbox can actually verify

**context.** Sovereign Execution Standard, Phase 4 (PRODUCTION-PARITY
STAGING), names a staging environment, database migrations, health checks,
readiness checks, rollback, smoke and integration tests. Before building
anything, `docker info` was tried in this session: Docker is **not
available** in this sandbox, unlike the GitHub-hosted runner `docker.yml`'s
own comment says has one. That rules out directly building or running
`deploy/local/compose.yaml` or the root `compose.yaml` here — anything
built against them could only be verified by careful reading, the way
`release.yml` itself can only be rehearsed in real CI. Scoped this round to
the one Phase 4 piece that is fully buildable AND fully verifiable inside
this sandbox with no Docker: health and readiness checks for the root
Next.js app, which `npm`/`vitest`/a local dev server can all exercise for
real.

**the gap, measured.** `grep` across `app/` and `lib/` for `healthz`,
`/health`, `readyz` found nothing — no endpoint existed for a platform, an
uptime monitor, or a human to ask "is this process alive" or "does it have
what it needs." `deploy/env.json` + `engine/scripts/env_check.py` already
answer the second question thoroughly, but only at CI time, against the
code — `env_check.py`'s own docstring names a `--runtime` mode as "the
operator's, on the host about to serve," which means a person must SSH in
and run a CLI command. Nothing exposed the same answer over HTTP, which is
what a deployment platform's own health check, or an uptime monitor, or a
human with only a browser, can actually reach.

**what was built, and the one design decision in it.** `/api/healthz` is
liveness ONLY — always 200, checks nothing — kept structurally separate
from `/api/readyz`, which reads the exact same `deploy/env.json` manifest
`env_check.py` already reads and checks it against live `process.env`. The
separation is deliberate, not incidental: a platform's restart policy acts
on liveness, and conflating "the process can run" with "Stripe is
configured" would turn a missing environment variable into a crash-loop
instead of the visible, fixable 503 it already is with the checks apart.
`lib/core/health/manifest.ts`'s `checkReadiness()` is a pure function
(manifest, env) → result, tested directly with a synthetic manifest so the
suite does not depend on which real secrets happen to be set when it runs;
a second pair of tests then exercises the real route handlers against the
actual `deploy/env.json`. **Names only, never values**, in the 503 body —
the identical rule `env_check.py` already enforces at CI time, now
enforced at request time by the same logic, not a second copy of it
(`checkReadiness` is the one function both the manifest-shape tests and the
real-route tests call).

**verified against a running process, not just a function call.** Vitest
calling `GET()` directly proves the handler's logic; it does not prove
Next.js actually serves it at the named path. `next dev` was started for
real in this sandbox and both routes hit with `curl`: `/api/healthz`
returned `200 {"ok":true}` immediately; `/api/readyz`, with only the two
placeholder Supabase variables CLAUDE.md's own build command sets, answered
`503` naming exactly the five still-missing required variables
(`SUPABASE_SERVICE_ROLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`,
`CRON_SECRET`, `OMNEX_OWNER_KEY`) and the unsatisfied `"an image model"`
group — with the two variables actually set correctly absent from the
missing list, proving the check reads real `process.env`, not a stub.

**wired in, not bolted on.** A new `_health_endpoints()` fact in
`state_map.py` feeds gate `5_production`'s evidence, worded carefully to
not overclaim: "the app now has the pieces a deployment platform would
check... which narrows what a first deploy still needs, **not whether one
exists**." Gate 5 stays `UNKNOWN` — nothing is deployed, and two new routes
existing does not change that — but the evidence is richer than it was.

**what was NOT built, and why that is the honest boundary here rather than
an omission.** A staging environment, database migration rehearsal,
rollback path, and smoke/integration tests against a real running stack all
need something this sandbox does not have: a container runtime. Building
YAML for any of them without the ability to run it here would repeat
exactly the mistake D-024 and D-025 both caught mid-task — a config that
parses and does not work — with no way to catch it before it reached CI.
Phase 4's remaining pieces are left for a session (or a CI rehearsal, the
`workflow_dispatch` pattern `release.yml` already established) that
actually has Docker.

**what else was considered.** A single `/api/health?mode=ready` endpoint
switching behaviour on a query parameter — rejected: two separate routes
make the liveness/readiness distinction structural (a caller cannot
accidentally point a liveness probe at logic that can 503 on a
misconfigured secret) rather than a convention a query string can be
typo'd past. Reading `deploy/env.json` through a shared Node module that
also re-implements `env_check.py`'s CI-time drift check in TypeScript —
rejected as scope creep: the drift check already exists, runs in CI, and
duplicating it in a second language is the exact "twin splitters" risk this
repository already named and paid for once.

**reversible how.** Three new files under `app/api/` and `lib/core/health/`,
one new test file, and additive changes to `state_map.py` (a new gate-5
fact) and `CLAUDE.md`. `git revert` removes the two routes cleanly; nothing
in the existing app calls either one, so nothing else changes behaviour.

---

## D-027: seven suites that each pass alone, proven to agree when wired together

**context.** Sovereign Execution Standard, Phase 5 (INTEGRATION / E2E
PROOF), names exactly one flow to prove: AUTH → REQUEST → VALIDATION →
BILLING/CREDIT → PROVIDER → PERSISTENCE → EVENT → RESPONSE. `/api/copilot/
stream` is that flow, named component for component in its own docstring
("auth → rate limit → guard the input → run under a budget → guard the
output → meter and bill what was actually spent").

**the gap, measured before anything was built.** `grep` across
`lib/__tests__/` for anything importing `app/api/copilot/stream/route`
found nothing. Six suites already exist and each proves one piece of that
route correct in isolation — `guardrails.test.ts`, `metering.test.ts`,
`budget.test.ts`, `stream.test.ts`, `trace.test.ts`, and
`credits.db.test.ts` against a real Postgres — but nothing had ever called
the route handler itself and checked that the seven pieces actually agree
about what happens when a real request arrives. This is the exact bug
shape this repository has already paid for once, one level down: `mutate.
py`'s own history records that `Run.margin` and `_summarise`'s total were
independent paths that happened to agree until a mutation moved one and
not the other. Six suites each independently correct is the same risk at
the level of a whole HTTP route.

**a real control checked before writing anything new.**
`credits.db.test.ts`'s own docstring says it is "skipped automatically when
Docker is unavailable." `docker info` was already confirmed to fail in
this sandbox in D-026's investigation. Read fully before building on top of
it: the suite is not naively skipped — its own first test independently
re-checks `docker info` and explicitly warns and returns rather than
silently reporting a false pass, and every other test in the file
early-returns on the same `available` flag with a comment naming exactly
the "vacuous pass" failure this is guarding against. Confirmed by running
it here: 4 tests "pass," three of them true no-ops, and the suite's own
design already treats that as correct rather than something to paper over.
This was a genuine risk worth checking, not a gap — it turned out to
already be handled with more care than the question deserved.

**what was built.** `lib/__tests__/copilot-stream.integration.test.ts`
calls the real `POST()` handler with a real `NextRequest`, faking only the
systems that are genuinely external to this codebase: Supabase (`auth.
getUser`, the `consume_credits` RPC, the `usage_events` insert) and the LLM
provider (`complete`, `hasProvider`). Rate limiting, guardrails, the run
budget, metering's cost math, and the SSE stream assembly all run as real
production code, unmocked — mocking those would only prove the mocks agree
with each other, not that the route does what its own docstring claims.
Five paths: the full paid success path (asserting the SAME credit figure
appears in both the `consume_credits` call and the `usage_events` row,
never two numbers that happen to match); unauthenticated (401, before any
provider call); a guard-blocked question (400, using the real injection
detector, not a stub that always agrees); a failed provider call (still
recorded, `ok: false` — "a run that spent money and then failed is
precisely the one an operator needs to see," the route's own docstring);
and no provider configured (the degraded zero-cost path, still recorded at
`credits: 0`).

**proven not vacuous, by sabotage — not just asserted.** The whole point
of this suite is at risk of the exact failure it exists to catch if the
mocks are wired wrong and every assertion passes for a reason unrelated to
the real code path. So the route's own `spendCredits` call was commented
out, the suite re-run, and the credit-flow test failed with exactly the
expected assertion (`consume_credits` never called) — then the file was
restored and the suite re-confirmed green. This is the same discipline
`test_the_round_trip_check_can_actually_fail` already holds at the
compiler-target level and `mutate.py` holds across the whole engine gate;
extended here to a hand-written integration test, which needed the same
proof and had never received it.

**what was verified.** 5 new tests, all passing, with the sabotage
regression confirmed as described above; full TypeScript gate green
(`npm audit`, `tsc --noEmit`, `vitest run` — 82 tests, up from 77 —
`next build`, all routes still registering correctly); full engine gate
green (ruff/mypy, all invariants, `actions_pin_check.py` 20/20,
`capability_map.py --check`, `state_map.py --check`, both release targets,
claims/runs/spine, full `pytest` — 1,286 tests — `mutate.py` 29/29).

**what else was considered.** Mocking `lib/core/agents/guardrails.ts` or
`lib/core/agents/metering.ts` too, to make the test purely about wiring —
rejected: that would remove exactly the layer most likely to disagree with
its own unit tests under real conditions (a guard rule tuned against a
narrow test corpus behaving differently against this test's exact prompt
text is itself useful information, and did not happen here — but mocking
it away would have made that unknowable). Testing against a real Postgres
here too, extending `credits.db.test.ts`'s pattern into this file — passed
over for this round since Docker is unavailable in this sandbox (confirmed
in D-026); the mocked-Supabase boundary is the correct one for what is
verifiable now, and a future session with Docker can extend this test to
route through `credits.db.test.ts`'s real container instead.

**reversible how.** One new test file, purely additive; nothing in
`app/api/copilot/stream/route.ts` or any module it imports was changed.
`git revert` removes the test with no effect on any other suite.

---

## D-028: a claim purge that found the repo's marketing clean and its own README stale

**context.** Sovereign Execution Standard §14 (CLAIM PURGE) names a
systematic search for unsupported claims — "production-ready," "fully
autonomous," "enterprise-grade," "revenue generating," "battle-tested," and
similar — across README, docs, code comments, and UI, with a rule to
downgrade or remove anything found without an evidence level behind it.

**what the search actually found: very little, and it says something.**
`grep` for the standard's own named phrases plus a dozen more common
superlatives ("best-in-class," "world-class," "cutting-edge," "industry-
leading," "state-of-the-art"...) across every `.md`/`.ts`/`.tsx`/`.py` file
found exactly one set of hits, all inside `corpus/universal-ai-os/
export.md` — a committed export of the *source book*'s own captions
("The most advanced pattern..."), already documented in CLAUDE.md as
quoted third-party material whose own n/10 scores are "deliberately not
imported" because "its author scored its own nodes." Purging a book's own
words would be a category error, not a claim purge. `GIG.md`'s Etsy/Fiverr
listing copy — the one place in this repository actually writing sales
copy — was read in full rather than grepped past: it already carries its
own "Honest note" disclaiming the AI-generation limitation before a
customer orders, which is the standard's own §14 discipline already
self-applied without anyone naming it that. Zero chapters needed purging —
this is the same shape D-021's handbook audit reported (some rounds find
nothing to fix, and that is a real result, not a failed search) rather
than a manufactured finding to justify the round.

**what the search DID find: README.md's own numbers had drifted.** It
quotes engine's test count in one sentence — "1,231 tests, zero required
dependencies" — and that number had not moved since before this session's
Phase 1 work, while the real count reached 1,286 across five phases of
this same session. CLAUDE.md's own "Lab notes" section already records
this exact drift class happening to *itself* four times; it had never
been checked in README.md, a different file with no structural protection
at all — this session's own practice of re-verifying CLAUDE.md's figure
after every phase does not extend to README.md, and nothing else did
either.

**what was built.** `scripts/readme_check.py` derives the real count via
`pytest --collect-only -q` — the same command a person runs, not a second
counting implementation that could disagree with it — and either rewrites
README.md's one narrowly-matched sentence or, under `--check`, refuses if
it disagrees. The regex is deliberately narrow (`[\d,]+ tests, zero
required dependencies`) so it can only ever touch the one sentence it was
written for, never a different number elsewhere in the file. Wired into
CLAUDE.md's gate block and `engine.yml`, immediately after
`actions_pin_check.py`.

**a self-referential correction, held in place rather than described
once.** Adding `readme_check.py` and its own tests moved the real count
again — first to 1,286, checked, then to 1,292 once `test_readme_check.py`
itself existed — and the number was re-synced each time rather than
quoted once and left to become the next stale figure this same mechanism
would need to catch.

**what was verified.** `readme_check.py --check` caught the real,
pre-existing 1,231-vs-1,286 drift (confirmed failing before any fix);
running it without `--check` corrected it; 6 new tests, including one
asserting the currently-committed README agrees with the repository right
now (the same shape as `state_map.py`'s and `capability_map.py`'s own
"committed artifact agrees with reality" tests); full engine gate green
(ruff/mypy, all invariants, `actions_pin_check.py` 20/20, `capability_map.
py --check`, `state_map.py --check`, both release targets, claims/runs/
spine, full `pytest` — 1,292 tests — `mutate.py` 29/29).

**what else was considered.** Extending the same mechanism to check
CLAUDE.md's own quoted figures too, replacing the manual re-verification
this session has been doing by hand every phase — deferred, not rejected:
CLAUDE.md quotes several independent numbers in one sentence (engine
tests, TypeScript tests, citegate tests, mutations, spine transitions),
and a single script maintaining all five correctly is a larger, separate
piece of work than the one-sentence fix this round scoped to. A GitHub
Action or pre-commit hook enforcing this on every PR rather than only in
the gate script — rejected as redundant: `engine.yml` already runs
`readme_check.py --check` on every push and pull request, which is the
same enforcement point every other check in this repository uses.

**reversible how.** One new script, one new test file, and two-line
additions to `CLAUDE.md` and `engine.yml`. `git revert` removes the check
and leaves README.md at whatever count it last held — the file itself is
untouched by the revert since the fix already landed as ordinary prose.

## D-029: MCP tool security — timeout, rate, and danger classification, none of which existed

**context.** §11 MCP/TOOL SECURITY names timeout controls, rate controls, and
dangerous-operation classification alongside permission scoping. D-020 already
covers permission scoping (`required_permission`, `available_to()`). The other
three did not exist anywhere in `omnex.mcp`: `McpServer._call()` invoked a
handler with no bound on how long it could run, no rate limiter existed in the
package, and `ToolSpec` had no concept of "this operation is hard to undo."

**what was found.** Confirmed by reading `server.py` and `tools.py` in full and
grepping the package for `RateLimit`/`timeout` — nothing. `McpClient` already
bounds how long it waits for a *reply* (`self.timeout`), which is a different
thing from the server bounding how long it waits for its *own handler*.

**what was built.**

- `ToolSpec` gained `timeout_seconds: float | None = None` and
  `dangerous: bool = False`. `dangerous` is wire-safe — `as_dict()` and
  `from_wire()` both carry it — while `required_permission` deliberately stays
  server-local, exactly as it already did. The two look like the same kind of
  field and are not: a forged `required_permission` claim would grant access a
  client should not have, while a forged `dangerous` claim grants nothing —
  it is a caveat for whoever is about to call the tool, not a capability. A
  non-positive `timeout_seconds` is refused at construction: zero is not a
  bound, it guarantees the timeout branch fires on every call.
- `McpServer.tool()` gained `timeout_seconds`, `dangerous`, and `rate_limit`
  parameters. `rate_limit`, when given, allocates one
  `omnex.guard.ratelimit.RateLimiter` keyed by tool name — the existing GCRA
  implementation, not a second one, per this repository's own
  `one_symbol_resolver` / `twin_splitters_agree` rule against duplicate
  mechanisms for the same problem.
- `_call()` now checks the tool's rate limiter (if any) before invoking the
  handler, and — if a timeout is configured — runs the handler on a
  `threading.Thread` and `.join(timeout)`s it rather than calling it directly.
  Both a rate-limit rejection and a timeout return a normal `Response` with
  `isError: true` and explanatory text, never an `RpcError` — consistent with
  `server.py`'s own stated central rule ("a tool that fails is a RESULT, not a
  protocol error") applied to two rejections the server itself issues rather
  than ones a handler raises.

**the honesty constraint, stated rather than glossed over.** A
`threading.Thread.join(timeout)` bounds how long the *caller* waits. It does
not kill the handler thread — Python has no safe mechanism to do that, and
claiming otherwise would be the same overclaim `guard/sandbox.py`'s module
docstring already warns against. `mcp.transport.StreamTransport.receive()`
already documents exactly this limitation for its own `timeout` parameter
("the parameter is documented as advisory here and the deadline is enforced by
whoever owns the process, which is the only layer that can actually kill it"),
and `guard/sandbox.py`'s docstring cross-references that same precedent when
explaining why *its* timeout (`subprocess.run(timeout=...)`, genuinely
preemptive because it kills an OS process) is a different, stronger
guarantee. The new MCP timeout is the `StreamTransport` case, not the
`sandbox` case, and `server.py`'s inline comment says so by name rather than
inventing new language that would read as a stronger promise than the
mechanism keeps. A test (`test_a_hung_handler_is_bounded_by_its_configured_
timeout`) proves the caller-side bound actually holds — a handler blocked on
an `Event` that is never set still returns within the configured timeout —
while the still-blocked background thread is released at the end of the same
test so it does not leak into the next one.

**what was verified.** `test_a_handler_that_returns_in_time_is_unaffected_by_
its_timeout` and `test_a_hung_handler_is_bounded_by_its_configured_timeout`
prove the timeout only fires when it should. `test_a_rate_limited_tool_
refuses_the_call_it_cannot_afford` and `test_a_rate_limit_rejection_is_a_
result_not_a_protocol_error` prove the limiter is wired and its rejection
shape matches the module's own stated rule.
`test_a_dangerous_tool_is_declared_on_the_wire_but_a_permission_is_not` proves
the wire-safety split holds in both directions at once — one spec, one
serialization, opposite behaviour for the two new-adjacent fields.
`test_a_non_positive_timeout_is_refused_at_registration` covers the
construction-time refusal. 6 new tests, all green;
`engine/ontology/CAPABILITIES.md` regenerated (`Clock`'s integration count
moved 26→27 because `server.py` now reaches it transitively through
`RateLimiter`, confirmed by re-running `capability_map.py`, not hand-edited);
`README.md`'s test count re-synced twice by `readme_check.py` — 1,292→1,298
for the six MCP tests, then 1,298→1,299 for the `runs.py` test added below —
the same mechanism D-028 built. Full engine gate green: ruff/format/mypy, all
invariants, `actions_pin_check.py` 20/20, `readme_check.py --check`,
`capability_map.py --check`, `state_map.py --check`, both release targets,
claims/runs/spine, full `pytest` (1,299 tests), `mutate.py` 29/29 — including
every pre-existing `omnex.mcp` test, unchanged.

**a second, self-caught defect: `runs.py --level` accepted a string
`state_map.py` does not recognise.** Recording R-0029 with `--level L3`
instead of the canonical `L3_REPOSITORY` (`policy.Autonomy`'s actual member
names are `L2_LOCAL`, `L3_REPOSITORY`, `L4_EXTERNAL`, `L5_UNSUPERVISED`)
landed silently, because `runs.py` never validated `--level` against
anything. `state_map.py`'s gate 9 counts autonomy "above L3" with
`r.autonomy_level not in ("", "L3_REPOSITORY")` — a string that merely fails
to equal the canonical spelling reads as an *escalation past* it, not as a
typo. R-0029's record and observation are now permanently in the ledger
mis-labelled `L3` (append-only; there is no path that edits a past row), so
`execution_state.json`'s gate 9 now honestly reports 3 runs above L3 and 1
successful, where the true figure is 1 and 0. That is the correct behaviour
of a derived file reading an actual, if mistaken, ledger entry — the fix
belongs in `runs.py`, not in disguising what is on file. Added
`VALID_LEVELS = frozenset(a.name for a in Autonomy)` and a refusal at
`--record` time when `--level` is not a member, plus
`test_recording_a_run_refuses_a_level_state_map_would_not_recognise` in
`test_runs.py` naming this exact incident so it cannot recur silently.
Consistent with the structural-fix-over-allowlist convention this repository
already follows elsewhere (`denied_existing_files()`, `checkReadiness()`):
the fix is a membership check against the one real source of level names
(`policy.Autonomy`), not a special case for the string `"L3"`.

**a pre-existing, unrelated flake observed and left alone.** `release_check.py
--target citegate` failed locally on `[project.urls]` pointing at
`omnex-business-technologies/omnex-factory` while `git remote get-url origin`
answered `RaveZona/omnex-factory` at the moment of the check — the exact,
previously-documented git-remote reversion in CLAUDE.md's lab notes ("A
session's own git remote reverted once, unexplained"). Re-checked
independently of this change (same failure on a `git stash` of this work);
not a regression this PR introduces, and not something this PR fixes, since
the actual fix is whatever is causing the remote to revert, which is outside
this session's control. Noted here rather than silently worked around.

**what else was considered.** A protocol-level error code for rate limiting
and timeouts, mirroring how some MCP implementations signal these — rejected
for the reason above: this module's whole design is built against exactly
that shape, because a protocol error kills the calling agent's ability to
read what happened and adapt. A configurable *default* timeout applied to
every tool with no explicit setting — rejected as a silent behaviour change:
every tool registered before this field existed had no bound, and a global
default would time some of them out for the first time with no code change
visible at their call sites. Killing the handler thread via
`ctypes.pythonapi.PyThreadState_SetAsyncExc` or similar — rejected outright:
it is unsafe (can corrupt interpreter state mid-operation) and exactly the
overclaim `guard/sandbox.py` was written to avoid making.

**reversible how.** Two files change shape (`tools.py`, `server.py`), both by
addition — every new field defaults to the fully-open behaviour that already
existed (`None` timeout, `dangerous=False`, no rate limiter unless
requested). `git revert` removes the capability with no change to any
existing tool's registration.

## D-030: CodeQL as a file, so gate 6 can see the one static-analysis control that was invisible on purpose

**context.** `execution_state.json`'s gate 6 has said, since it was written,
that "CodeQL default setup and secret scanning are GitHub settings rather than
files, so a repository scan cannot see them and this claims neither way." That
sentence is honest about a genuine boundary — GitHub's "default setup" for
CodeQL is a toggle in repository Settings with no corresponding file, so a
process that only reads the checked-out tree cannot observe it either way.
Re-reading it during this round's truth pass raised the obvious question: is
that the *only* way to run CodeQL, or is it the way that happens to be
invisible to this exact checker?

**what was found.** It is not the only way. CodeQL also ships as an "advanced
setup" — an ordinary GitHub Actions workflow using `github/codeql-action`'s
`init` and `analyze` actions — which is a committed file, observable the same
way `dependabot.yml`, the SBOM step, and every pinned action already are. No
such workflow existed in `.github/workflows/`. Gate 6 was not reporting a
control that cannot be seen; it was reporting a control that, for this half of
the pair, could have been seen and simply was not there.

**what was built.** `.github/workflows/codeql.yml`: a matrix over
`javascript-typescript` (the root Next.js app) and `python` (`engine/` and
`oss/citegate/`), triggered on push and pull request to `master`/`main`, a
weekly cron (Monday 03:17 UTC, off the hour so it does not compete with every
other repository's `0 0 * * *`), and `workflow_dispatch`. Both
`github/codeql-action` steps (`init`, `analyze`) are pinned to a full commit
SHA, resolved the same way Phase 2 already resolved every other action: cloned
`github/codeql-action` through the git proxy's public-repository read lane,
confirmed `v4.38.0` is an annotated tag (`git cat-file -t` said `tag`, not
`commit` — the exact shape that already bit `attest-build-provenance` and
`setup-uv` in Phase 2), and dereferenced with `^{commit}` rather than trusting
`git rev-parse` on the bare tag.

`state_map.py`'s `_supply_chain()` gained `codeql_workflow_present`, checking
only whether a workflow file names `codeql-action` — not whether a scan has
ever run, found anything, or had a finding triaged, the same boundary
`sbom_generated` already keeps between a control existing in the repository and
a control doing something in production. Gate 6's prose now separates the two
controls it used to bundle: CodeQL moves from "cannot see it" to "here, or
not"; secret scanning, which genuinely has no advanced-setup file, keeps the
original unobservable claim, now stated about one control instead of two.

**what was verified.** `actions_pin_check.py` — 23 of 23 actions pinned
(20 pre-existing + 3 new: `checkout`, `codeql-action/init`,
`codeql-action/analyze`). `test_the_repaired_gates_derive_their_evidence_
rather_than_stating_it` extended with `codeql_workflow_present: True`.
`execution_state.json` regenerated and re-checked in both directions. Full
engine gate green: ruff/format/mypy, all invariants, `env_check.py`,
`extras_check.py`, `release_check.py --target engine`, claims/runs/spine,
`readme_check.py --check` (no test-count change — this round adds workflow and
script lines, not tests), `capability_map.py --check`, `state_map.py --check`,
`apply_decisions.py --dry-run`, full `pytest tests/` (1,299 tests, unchanged),
`mutate.py` (29/29). `npx tsc --noEmit` clean (no TypeScript touched).
`release_check.py --target citegate` failed on the same pre-existing,
previously-documented git-remote reversion as D-029 — reproduced independent
of this change, unrelated to it, and not something this session can fix from
inside the sandbox.

**what else was considered.** Enabling CodeQL's "default setup" via a
repository-settings API call instead of a workflow file — rejected: it would
have solved the actual security question (does static analysis run) while
leaving gate 6 exactly as blind as before, since a setting has no artifact for
`state_map.py` to read. The whole point of this round was closing the gap
between "a control exists" and "a control is visible to the mechanism whose
job is to say so," and a settings-only fix would have closed neither. Running
CodeQL only on `python` (matching the SBOM and release path's engine-only
focus) — rejected: the root Next.js app is the commercial surface handling
real payment flow (`lib/core/agents/budget.ts`, the Stripe routes), and
`javascript-typescript` static analysis is exactly the tooling `ci.yml`'s
`npm audit` does not cover (a dependency's known CVE versus a vulnerability in
this repository's own code are different questions). A `security-events:
write` permission narrower than the whole job — not available: `codeql-
action/analyze` needs it to upload SARIF results to the Security tab, and
GitHub does not offer a finer-grained scope for that specific write.

**reversible how.** One new workflow file and one additive fact in
`state_map.py`. `git revert` removes the workflow and the fact; gate 6's prose
would need a matching revert to stop citing a fact that no longer exists,
otherwise `state_map.py --check` would immediately say so.

**addendum, same PR, before merge: the workflow could not run, and the
finding got stronger because of it.** CI on PR #43 failed both `codeql.yml`
jobs with GitHub's own error: "CodeQL analyses from advanced configurations
cannot be processed when the default setup is enabled." That is GitHub
refusing to accept an advanced-setup SARIF upload while the repository's
CodeQL *default setup* — the very setting gate 6's prose named as
unobservable — is already turned on. The two configurations are mutually
exclusive on GitHub's side; there is no combination of workflow permissions
or `category` naming that reconciles them, only disabling default setup
(a repository Settings change, `CREDENTIAL`/`DESTRUCTIVE`-adjacent under
`policy.py` and not something this session takes on its own initiative) or
not running the advanced workflow at all.

Reverted `.github/workflows/codeql.yml` and `codeql_workflow_present` rather
than leave a check that can only ever be red for zero analysis gained — this
repository already runs CodeQL, via the setting the workflow would have
duplicated. The refusal message itself is then the more valuable artifact:
a live, one-time confirmation that default setup is genuinely active,
recorded as **C-015** (`SUPPORTED` via `E-015`, method `network_probe`) in
`state/claims.jsonl` rather than as a fact in `state_map.py`, because it is
not rederivable from a checkout the way every other Phase 2 fact here is —
the same reason C-005's and C-008's confirmations live in the claim registry
and not in `execution_state.json`. Gate 6's prose now cites C-015 by id
instead of claiming "neither way" for CodeQL specifically; secret scanning,
which has no advanced-setup file to attempt this trick with, keeps the
original unobservable claim as the one remaining control in that sentence.

This is the structural pattern this repository already runs on, held to
its own PR: a checker's own CI run produced evidence the checker's source
tree could never contain, and that evidence went into the ledger built for
exactly this (`state/claims.jsonl` + `state/evidence.jsonl`), not into a
"pass" bent to fit it. `actions_pin_check.py` accordingly reports 20/20
again, not 23/23; `README.md`'s test count is unchanged at 1,299 (no test
was added or removed by the revert, since the CI failure was caught before
merge, not after).

**what was verified, second pass.** `state_map.py --check` after both the
revert and the regeneration; `claims.py --check` shows C-015 `SUPPORTED` (1
live evidence) and the registry still well-formed at 15 claims; full engine
gate re-run green end to end (ruff/format/mypy, all invariants, `env_check.py`,
`extras_check.py`, `release_check.py --target engine`, claims/runs/spine,
`readme_check.py --check`, `capability_map.py --check`, `state_map.py
--check`, `apply_decisions.py --dry-run`, full `pytest tests/`, `mutate.py`
29/29); `release_check.py --target citegate` still failing on the same
pre-existing, unrelated git-remote reversion.

## D-031: the n8n binding checker had no test and did not run in CI

**context.** This round's truth pass, after PR #43's CodeQL correction, looked
for the same class of gap the last several rounds have each found once: a real
checker that exists, catches a real defect class, and is invisible to
`test_ci_runs_every_gate_script_the_document_names` because nobody named it in
CLAUDE.md's gate block. `readme_check.py` was that gap two rounds ago;
`actions_pin_check.py`, `capability_map.py` and `sbom_check.py` before it.

**what was found.** `engine/scripts/n8n_bindings_check.py` exists, has a
docstring naming a real defect it was built to catch (`unresolved_commands()`
was added after the catalogue once named `python -m omnex.pipeline.
verify_webhook` and `...seen_before`, neither of which was a real module, and
every schema-level check passed both), and exits non-zero on exactly that
class of problem. It had **zero tests** and did not appear in CLAUDE.md's gate
block or `engine.yml` — the resolution logic that caught the original defect
had, for the entire time since, no test holding it in place and no CI run
exercising it on every push or pull request. It is not `n8n_bindings.json`
that was undertested (`bindings.load()` has its own coverage through
`test_factory_compile.py`); it is this checker's own two functions,
`unresolved_commands()` and `required_env()`, that had none.

**what was built.** `engine/tests/test_n8n_bindings_check.py`: nine tests
against synthetic catalogues built via `bindings.load()` on a `tmp_path` file
(no second parser — the same `Catalogue`/`load()` the checker itself uses) —
a module with no `__main__`, a real module with a real subcommand, a real
module with a bad subcommand, a binding naming no command at all, a
`proposal`-sourced binding that must never be resolved (only `source: this
repository` entries claim to be checkable), the environment-variable
derivation reading both interpolated and declared names, `main()` failing on
a catalogue that will not load and on an unresolved command, and — the test
that is the actual point — the real, committed `n8n_bindings.json` still
resolving cleanly today. Added `scripts/n8n_bindings_check.py` to CLAUDE.md's
gate block (between `actions_pin_check.py` and `readme_check.py`, preserving
the order the document already runs things in) and a matching step in
`engine.yml`, in the same position.

**what was verified.** `test_ci_contract.py`'s
`test_ci_runs_every_gate_script_the_document_names` passes with the new
script named in both places. `n8n_bindings_check.py` itself still exits 0
against the real catalogue (7 bindings, 0 confirmed — unchanged; this round
adds coverage, not new bindings). Full engine gate green: ruff/format/mypy,
all invariants, `env_check.py`, `extras_check.py`, `release_check.py --target
engine`, claims/runs/spine, `actions_pin_check.py` (20/20), the new
`n8n_bindings_check.py` step, `readme_check.py --check` (1,308, up from 1,299
— nine new tests), `capability_map.py --check`, `state_map.py --check`,
`apply_decisions.py --dry-run`, full `pytest tests/`, `mutate.py` (29/29).
`release_check.py --target citegate` still failing on the same pre-existing,
previously-documented git-remote reversion, unrelated to this change.

**what else was considered.** Making `n8n_bindings_check.py` exit non-zero on
an unconfirmed binding, to force the CI gate to reflect that 0 of 7 bindings
are confirmed — rejected, and the module's own docstring already gives the
reason: "a permanently red build is one people learn to ignore," and
unconfirmed is every entry's honest starting state, not a defect. Writing a
second, independent command-resolution implementation for the test file
rather than reusing `bindings.load()` — rejected as exactly the
`one_symbol_resolver`/`twin_splitters_agree` mistake this repository already
paid for once; the test file uses the same `Catalogue` the checker consumes,
so a change to the schema shows up as a test failure here too rather than two
readers silently disagreeing.

**reversible how.** One new test file and two-line additions to CLAUDE.md and
`engine.yml`. `git revert` removes CI coverage and the test file; the checker
itself is untouched either way, since this round added test and CI wiring,
not new logic.

## D-032: two CI checks a developer running the documented gate could never reproduce

**context.** D-031 closed a gap by generalising a pattern: a real checker with
no test and no CI wiring. This round generalised one more level up and asked
the opposite question — not "does every documented script run in CI"
(`test_ci_runs_every_gate_script_the_document_names` already holds that), but
"does CI run anything the document never mentions." Nobody had asked that
question in either direction until now; the existing test only checks
`documented <= in_ci`.

**what was found.** Computing both sets directly (`_gate_scripts` over
CLAUDE.md's fenced block versus over every workflow's commands) found
`{'node_dossier.py', 'eval_gate.py'} = in_ci - documented`, non-empty. Both are
real, blocking CI checks:

- `node_dossier.py` (`engine.yml`'s "Decision queue" step) regenerates
  `corpus/universal-ai-os/DECISIONS.md` from all 507 node dossiers and the step
  fails the build if `git diff --exit-code` finds drift — the same "derived,
  never authored" rule `execution_state.json` and `CAPABILITIES.md` already
  enforce, just never added to the document that lists how to check it
  locally.
- `eval_gate.py` (`quality-gate.yml`'s separate job) runs the golden RAG suite
  against `suites/baseline.json` and blocks a pull request on a regression in
  any previously-passing case.

A developer who ran only the documented commands, saw everything green, and
pushed could still watch CI turn red for a reason CLAUDE.md never named —
exactly the failure mode the document's own preface warns about ("the
document becomes advice again") and the exact class of gap D-028
(`readme_check.py`) and D-031 (`n8n_bindings_check.py`) each closed once, for
one script at a time, without ever closing the general case.

**what was built.** Both commands added to CLAUDE.md's gate block:
`node_dossier.py` followed by `git diff --exit-code
../corpus/universal-ai-os/DECISIONS.md` (the exact two lines `engine.yml` already
runs), placed immediately before `apply_decisions.py --dry-run` since a
decision review depends on the dossier being current; `eval_gate.py --baseline
suites/baseline.json --out .omnex/runs` appended at the end, matching
`quality-gate.yml`'s own invocation exactly. New test
`test_the_documented_gate_names_every_script_ci_runs` in `test_ci_contract.py`
asserts `in_ci <= documented` — the mirror of the existing test — so the two
sets are now held equal from both directions, closing the general case this
time rather than the two specific scripts.

**what was verified.** Both commands run for real, locally, exactly as
written: `node_dossier.py` regenerated `DECISIONS.md` with zero diff against
what was already committed (it was current); `eval_gate.py` ran the real
golden suite and exited 0 (`PASS: no regressions; 0 improved`, 83% pass rate,
matching the suite's known, accepted limitation on `multi_page`/`comparison`
categories — not a new failure introduced by this change). Both new tests
pass; the full existing `test_ci_contract.py` suite still passes with the
stricter, bidirectional check in place. Full engine gate green end to end,
including the two newly-documented steps: ruff/format/mypy, all invariants,
`env_check.py`, `extras_check.py`, `release_check.py --target engine`,
claims/runs/spine, `actions_pin_check.py` (20/20), `n8n_bindings_check.py`,
`readme_check.py --check` (1,309, up from 1,308 — one new test), `capability_
map.py --check`, `state_map.py --check`, `node_dossier.py` + diff,
`apply_decisions.py --dry-run`, full `pytest tests/`, `mutate.py` (29/29
killed), `eval_gate.py`. `BUSINESS.md` also regenerated during this round's
truth pass (day 45, 195 commits — both re-measured, not restated) with no
narrative change. `release_check.py --target citegate` still fails on the
same pre-existing, previously-documented git-remote reversion, unrelated to
this change.

**what else was considered.** Loosening the new test to a documented
allowlist of "known CI-only steps" (e.g. an explicit exemption list) rather
than requiring equality — rejected: an allowlist is exactly the mechanism
that let `node_dossier.py` and `eval_gate.py` go unnoticed for as long as
they did, since nothing forced anyone to update it. Requiring equality means
the only way to add a CI-only script gate in the future is to also document
it, which is the property this round exists to establish. Inlining the
`quality-gate.yml` suite-fingerprint pre-check (a raw Python one-liner in the
workflow) into CLAUDE.md's block as well — not needed: `Gate.decide()`
(`omnex/evals/runner.py`) already refuses on a `suite_fingerprint` mismatch
internally, so the workflow's inline check is a friendlier early message
about a failure `eval_gate.py` alone already catches, not a second gate.

**reversible how.** Two lines added to CLAUDE.md's fenced block and one new
test function. `git revert` removes both; the stricter test would then need
its own revert too, or it would immediately fail on the next CI-only script
someone adds and forgets to document — which is the property working as
intended, not a bug in the revert.

## D-033: eval_gate.py's own CLI had no test, one script after the last one

**context.** D-032 added `eval_gate.py` to CLAUDE.md's gate block and CI in
the same round it wrote the bidirectional `documented == in_ci` test. Adding
a script to the gate closes the CI-visibility gap; it says nothing about
whether the script's own logic has a test, which is a different, adjacent
gap — the exact one D-031 closed for `n8n_bindings_check.py` one round
earlier. Checking immediately after landing D-032 found the same shape here.

**what was found.** `omnex.evals`'s library code (`Suite`, `Gate.decide()`,
`EvalRunner`, `Trend`) is well covered by `test_evals.py`. `scripts/eval_
gate.py`'s own `main()` — argument parsing, the exit code, `--record`,
whether a fresh run with no baseline behaves correctly, whether a genuine
regression against a real baseline actually returns 1 — had never been
exercised directly by anything. `grep -rl "import eval_gate" tests/*.py`
returned nothing.

**what was built.** `engine/tests/test_eval_gate.py`, four tests run against
the real, committed `suites/rag_core.json` and its corpus (not a synthetic
suite — the point is this script's own plumbing, and the real suite is
small, deterministic and already zero-cost):

- a first run with no baseline passes and writes nothing (only `--record`
  may write the baseline file);
- `--record` writes a baseline a later, independently-run instance of the
  same deterministic pipeline reads back as unchanged;
- **sabotage-verified**: record a real baseline, then edit ONE result in the
  saved JSON to claim a case passed that the real run still fails at
  (score 0.0, one of the suite's known chronic failures) — `main()` must
  return `1` and print that case's id, proving the CLI's exit code and
  output actually reflect `Gate.decide()`'s verdict rather than merely that
  `Gate.decide()` can compute one in isolation;
- the script's own defaults load and run the real suite and corpus this
  repository ships, with only `--baseline`/`--out` redirected to `tmp_path`.

**what was verified.** All four tests pass, including the sabotage case
(confirmed failing before the fix was written — the JSON edit trick, not a
mocked `Gate`). `engine/ontology/CAPABILITIES.md` regenerated: `Gate`'s
capability entry gained a fourth referencing test file, confirmed by
`capability_map.py --check` rather than hand-edited. `README.md`'s test
count re-synced 1,309→1,313 by `readme_check.py`. Full engine gate green:
ruff/format/mypy, all invariants, `env_check.py`, `extras_check.py`,
`release_check.py --target engine`, claims/runs/spine, `actions_pin_check.py`
(20/20), `n8n_bindings_check.py`, `readme_check.py --check`, `capability_
map.py --check`, `state_map.py --check`, `node_dossier.py` + diff,
`apply_decisions.py --dry-run`, full `pytest tests/` (1,313 tests),
`mutate.py` (29/29 killed), `eval_gate.py` itself. `release_check.py
--target citegate` still fails on the same pre-existing, previously-
documented git-remote reversion, unrelated to this change.

**what else was considered.** Writing a small synthetic suite (two or three
`GoldenCase`s) instead of running the real committed one — rejected: the
real suite is already deterministic and cheap (`ScriptedModel`, no network,
regeneration off), so a synthetic one would only add a second fixture to
keep in sync with `omnex.evals`'s schema for no isolation benefit, the same
reasoning `test_n8n_bindings_check.py` used to reuse `bindings.load()`
rather than inventing a parallel catalogue format. Mocking `Gate.decide()`
to force a `False` verdict rather than genuinely engineering a regression —
rejected: it would prove the CLI prints whatever the mock returns, not that
a real regression in a real recorded baseline actually reaches the exit
code, which is the one property worth holding in place given this script's
whole reason for existing ("a quality check that exits 0 never blocks
anything").

**reversible how.** One new test file, no production code changed.
`git revert` removes it with no effect on `eval_gate.py` or `omnex.evals`.

## D-034: a pin does not verify its own currency — astral-sh/setup-uv, three majors stale

**context.** `actions_pin_check.py` proves every `uses:` line resolves to a
full commit SHA. It has never claimed, and cannot claim, that the commit is
*recent* — a SHA that never moves is exactly as valid a pin the day it is
written as three years later, and nothing about the string itself says which.
`C-008` already found this exact class of drift once (`attest-build-
provenance@v2`, two majors stale) via the same technique: read the action's
own public repository rather than trust anything visible from inside this
one. Re-running that same technique against the other pinned action this
repository actually depends on for its own build step (`astral-sh/setup-uv`,
used in every workflow that runs Python) was the obvious next check nobody
had repeated since.

**what was found.** Cloning `astral-sh/setup-uv` through this session's git
proxy public-repository read lane and reading its tags: the pin (`v7.6.0`,
released 2026-03-16) is three major versions behind the current tag
(`v10.1.0`). Read the intervening `action.yml` history rather than assuming
compatibility: `enable-cache` and `cache-dependency-glob` — the two inputs
every workflow here actually sets — are unchanged in both name and meaning
at `v10.1.0`. The one behavioural change found (commit `f451684`, "disable
automatic caching for sensitive events") only narrows what the `auto` default
does on `pull_request_target`/`workflow_run`/`release`/tag-push events; every
workflow here sets `enable-cache: true` explicitly, which that same commit's
own description states is preserved as an override. `v10.1.0`'s tag is
**lightweight** (`git cat-file -t` says `commit`, not `tag`) — the opposite
shape from `v7.6.0`'s annotated tag, so `git rev-parse v10.1.0` already gives
the pinnable commit with no `^{commit}` dereference needed. Assuming every
tag needs the same handling as the last one checked would have been the
mistake here; checking each one's actual type, again, is what Phase 2 already
established as the discipline.

**what was built.** Bumped all six `astral-sh/setup-uv` uses (two in
`engine.yml`, three in `release.yml`, one in `quality-gate.yml`) to
`@bec219d24cd3e171d82865faccec33120bb574f4 # v10.1.0`. Recorded **C-016**
("astral-sh/setup-uv@v7.6.0 is a current major version") with **E-016**
(`network_probe`, `contradicts`, `reverify_after: 90`) *before* making the
change — the same order C-008 was handled in: evidence lands in the ledger
first, the fix follows it, so the record shows what was found and why rather
than a fix with no trace of the finding that motivated it.

**what was verified.** `actions_pin_check.py` still reports 20 of 20 pinned
(the count does not change; only which commits six of them point to).
`claims.py --check` shows C-016 `CONTRADICTED` (1 live evidence, 1 against),
recomputed rather than typed. Full engine gate green: ruff/format/mypy, all
invariants, `env_check.py`, `extras_check.py`, `release_check.py --target
engine`, claims/runs/spine, `actions_pin_check.py`, `n8n_bindings_check.py`,
`readme_check.py --check` (1,313, unchanged — no test added or removed),
`capability_map.py --check`, `state_map.py --check`, `node_dossier.py` +
diff, `apply_decisions.py --dry-run`, full `pytest tests/`, `mutate.py`
(29/29 killed), `eval_gate.py`. The actual CI behaviour of `setup-uv@v10.1.0`
on this repository's runners can only be confirmed once these workflows run
for real on GitHub — read-and-reason verification of the action's own
history, not a local execution, same boundary D-030's CodeQL rehearsal was
explicit about. `release_check.py --target citegate` still fails on the
same pre-existing, previously-documented git-remote reversion, unrelated.

**what else was considered.** Checking every action pinned anywhere in the
repository for staleness in one pass, building a standing script for it —
deferred, not rejected: a script that re-derives "is this the latest tag"
needs the same public-repo git-clone lane this round used by hand, and
turning that into a repeatable, non-network-dependent CI check is a larger
piece of work than this round's scope (the network read only works in this
kind of sandboxed session with the proxy allowlist, not from a locked-down
CI runner with no such lane). Bumping only `setup-uv` and leaving the other
five actions unchecked this round rather than re-verifying all seven —
accepted deliberately: the other six were already read in D-030 and D-033's
adjacent rounds within the last few hours of repository time and nothing has
tagged since; re-cloning six repositories to re-confirm a fact unlikely to
have changed in that window is not a good use of the one external read this
round needed.

**reversible how.** Six one-line `uses:` changes plus one claim/evidence
pair, additive only. `git revert` restores the old pin; the claim and
evidence rows stay on file either way, since evidence is never deleted, only
superseded.

## D-035: gate 3's own hard-coded claim — the third occurrence of a defect this repository has already named twice

**context.** The operator shared the full text of the Sovereign Execution
Standard verbatim for the first time this session (earlier rounds worked from
a from-memory summary). Re-reading §0 ("NO EVIDENCE = NO CLAIM"), §7 (the
UNKNOWN/NO-EVIDENCE discipline) and §23 (STATE CONSISTENCY — "if a mismatch
exists, the capability must not be automatically marked verified") against
`state_map.py`'s own source, rather than against its rendered output, is what
this round's truth pass changed: previous rounds read `execution_state.json`
and asked whether it agreed with the repository; this one read the *script
that writes it* and asked whether every sentence in it was still earning its
truth on every run.

**what was found.** `state_map.py`'s own module docstring warns, twice, about
exactly one failure shape: a gate whose evidence is a literal cannot notice
when it comes true or stops being true. Gates 1 and 2 already carried this
defect once each — "node_dossier.py does not exist" and "state/claims.jsonl
does not exist," both hard-coded, both surviving for weeks after the named
scripts existed, both caught only by `test_no_gate_claims_a_file_is_absent_
while_it_sits_in_the_repository`. Gate 3 carried a third, unnoticed instance
of the identical shape: `"the suite is green and the mutation probe kills
every mutation"`, typed directly into this file's source rather than derived
from anything. That sentence was true the day it was written and would have
stayed exactly as true in the rendered `execution_state.json` if a mutation
had started surviving the next day, if `mutate.py` had been deleted, or if it
had never been run at all in a given session — none of those states could
change the string, because nothing read anything to produce it.

**what was built.** `mutate.py`'s `main()` now calls `write_result()`
(extracted as its own function so a test can exercise the persistence against
synthetic `Result`s rather than paying for a full 29-mutation run twice),
writing `ontology/mutation_probe.json` — committed, not `.omnex/`-ignored,
because `state_map.py`'s `derive()` must produce the same
`execution_state.json` from a fresh checkout that it does locally, and a
gitignored sidecar would make CI and a local run disagree about whether the
fact exists at all. Written on every run, survivors included: a probe result
with a hole in it is the one worth keeping on file, the same argument
`eval_gate.py`'s `Trend` already makes for a failed suite run.

`state_map.py` gained `_mutation_probe()` (reads the file, or reports
`{"present": False}` — the state a hard-coded string could never represent)
and `_mutation_clause()` (gate 3's sentence, built from what was actually
read). A second check rides along: `catalogue_size_matches` compares the
file's `total` against the live `len(mutate.CATALOGUE)`, so a mutation added
to the catalogue with nobody re-running the probe reads as **stale**, not as
a silently undercounted total. `git diff --exit-code ontology/mutation_
probe.json` guards freshness the same way `node_dossier.py`'s output already
is — added as its own step, gated to the same `matrix.python == '3.12'`
condition as `mutate.py` itself, immediately after it in `engine.yml`, since
the file is only ever regenerated on that interpreter.

CLAUDE.md's gate block reordered so `mutate.py` and its diff check now run
*before* `capability_map.py --check` and `state_map.py --check`: not because
CI's own step order matters (analysed and confirmed it does not — every check
in a CI job reads the same static checked-out commit regardless of which
script runs first, since none of them overwrite a file another one reads
mid-job on the interpreters where mutation doesn't run), but because a
contributor pasting the whole documented one-liner and running it fresh needs
`ontology/mutation_probe.json` to exist and be current *before* `state_map.py
--check` can meaningfully compare against it, and the written order should
say so rather than rely on it happening to work by accident of file
persistence.

**what was verified.** The full, reordered CLAUDE.md one-liner run start to
finish, for real, in the new order — not assumed from the individual scripts
passing in isolation. Two new tests in `test_mutation.py`
(`test_write_result_records_survivors_rather_than_hiding_them`, against
synthetic `Result`s, and `test_the_committed_result_matches_the_live_
catalogue_size`, against the real committed file) and three in
`test_state_map.py` (`_mutation_probe()`'s presence now appears in gate 3's
evidence; a monkeypatched absent file produces the honest `{"present": False}`
this shape could never produce before; a synthetic stale-catalogue case
reaches the "re-run mutate.py" clause). `test_ci_contract.py`'s full suite
still passes with the reordered document and workflow. Full engine gate
green end to end in the new documented order: ruff/format/mypy, all
invariants, `env_check.py`, `extras_check.py`, `release_check.py --target
engine`, claims/runs/spine, `actions_pin_check.py` (20/20), `n8n_bindings_
check.py`, `readme_check.py --check` (1,317, up from 1,313 — 4 new tests),
`node_dossier.py` + diff, `apply_decisions.py --dry-run`, full `pytest
tests/`, `mutate.py` (29/29 killed) + its new diff check, `capability_map.py
--check`, `state_map.py --check`, `eval_gate.py`. `release_check.py --target
citegate` still fails on the same pre-existing, previously-documented
git-remote reversion, unrelated. While in this file, corrected `mutate.py`'s
own stale figure in CLAUDE.md's "Where things live" section (quoted "27 of
27," measured 29 of 29) — the exact drift class its own Lab Notes section
already warns about, found by re-measuring rather than restating while this
bullet was already open for the persistence note.

**what else was considered.** Writing the probe result into `.omnex/`
alongside `eval_gate.py`'s `Trend` runs, matching that convention exactly —
rejected once the gitignore was checked: `.omnex/` is *entirely* ignored,
which is fine for `eval_gate.py`'s own trend history (a local/CI-ephemeral
run log `quality-gate.yml` uploads as a build artifact rather than commits)
but wrong for a fact `execution_state.json` must reproduce identically from
a fresh checkout. Requiring `mutation_probe.json`'s `source_commit` to equal
the exact current `HEAD` in `state_map.py --check`'s strict comparison —
rejected: every derived file already committed here (`execution_state.json`
itself, via its own `source_commit` field) is structurally one commit behind
itself at the moment it is committed, and `test_the_committed_state_agrees_
with_the_repository` already excludes `source_commit` from its equality check
for exactly this reason; holding a *different* derived file to a stricter
standard than the one it feeds would be arbitrary. Reordering `engine.yml`'s
steps to match CLAUDE.md's new order exactly — not done, since the two files
have never matched step-for-step (`env_check.py` runs fifth in CLAUDE.md's
block and near the end in `engine.yml`, unchanged by any prior round) and
`test_ci_contract.py` only requires the *set* of gate scripts to match, never
their sequence; reordering `engine.yml` for cosmetic symmetry would be a
larger, riskier diff for a property nothing checks or needs.

**reversible how.** Two new fields on the derived-state graph
(`mutation_probe`, feeding gate 3's evidence and prose), one new committed
file, one new CI step, and a block reorder in CLAUDE.md with no scripts added
or removed from the set `test_ci_runs_every_gate_script_the_document_names`
and its mirror already check. `git revert` restores the literal sentence gate
3 carried before — a regression in kind, not a break, since nothing downstream
depends on `mutation_probe.json` existing.

**addendum, same PR, before merge: the freshness check itself failed on
every pull request, structurally.** PR #49's CI went red on exactly the new
"Mutation probe result committed" step, on its very first real run. The log
showed `git diff --exit-code` failing on one line:
`"source_commit"` changing from the commit this session generated the file
against to `218569dc...` — a SHA that appears nowhere in this repository's
history. GitHub Actions checks out a synthetic merge-preview commit for a
`pull_request` event (`refs/pull/N/merge`), fabricated fresh on every run and
never a real commit anything else could match. `write_result()`'s
`source_commit` field, bound via `git rev-parse HEAD` at generation time,
could therefore never equal what a fresh CI run would compute — the check
was not flaky, it was guaranteed to fail on every single pull request from
the moment it started running for real.

The same commit-binding pattern exists in `execution_state.json` and does
not have this problem, for a reason this round initially missed: `state_map.
py`'s own `differences()` explicitly drops `source_commit` (along with
`branch` and `tree_clean`) before comparing committed against measured.
Copying the field without copying the exclusion reproduced the shape of a
working pattern without the part that makes it work. `DECISIONS.md` and
`CAPABILITIES.md`, the two other files this repository already diff-checks
after regeneration, avoid the problem entirely by carrying no commit hash at
all — the simpler and, in hindsight, obviously correct precedent to follow
for a file whose freshness is checked with a raw `git diff`, not a
field-excluding comparator.

Removed `source_commit` from `mutation_probe.json` rather than adding an
exclusion mechanism: nothing downstream needed the exact commit, only the
counts, and a file with no volatile field is simpler than a diff check smart
enough to ignore one. Verified the fix actually holds, not just that it
compiles: ran `mutate.py` twice in a row and confirmed the two output files
are byte-for-byte identical — the property `git diff --exit-code` needs to
be meaningful across independent runs, checked directly rather than inferred
from removing the field that broke it. Every affected test updated to assert
`"source_commit" not in payload` rather than checking a value; `execution_
state.json` and `CLAUDE.md`'s quoted figures regenerated. Full engine gate
re-run green end to end after the fix, including a fresh `git diff --exit-
code ontology/mutation_probe.json` against the newly-committed schema.

The lesson generalises past this one field: a value bound to `git rev-parse
HEAD` inside content a `pull_request`-triggered `git diff --exit-code` step
compares is never safe to commit, because the checked-out commit on that
event type is never the one that will exist in history. `execution_state.
json` gets away with it only because its own comparator was written to
know that; a new committed-and-diffed artifact should default to carrying no
commit hash unless it also carries that exclusion.

## D-036: gates 11 and 12 carried the same hard-coded claim as gates 1, 2 and 3 — found a fourth time

**context.** Continuing the truth pass under the full Sovereign Execution
Standard text after PR #49 merged. D-035 named the failure shape precisely:
"a gate whose evidence is a literal cannot notice that it came true," found
in gates 1, 2 and 3 of `state_map.py`'s `gates()` function, each fixed in a
separate prior round. The obvious next question a genuine truth pass has to
ask is whether the same file still carries a fourth instance nobody has
looked for yet — re-reading `gates()` end to end, rather than re-running it
and trusting a green `--check`, since `--check` only proves the committed
file agrees with itself, never that either one is honest.

**what was found.** It does. `11_commercial` and `12_economic` — the two
gates furthest from anything this repository can decide on its own — still
read exactly as they were first written: `"no external user has obtained the
software; 0 listings live"` and `"no revenue log exists — 0 recorded is not
0 earned, and BUSINESS.md refuses to render it as a measurement"`, both typed
directly into `state_map.py`'s source with no function call behind either
number. `business_map.py` already computes every one of these facts for
`BUSINESS.md` — `goods()`, `live_modules()`, `revenue()` — and `gates()`
imported none of them. A listing going live, or `REVENUE_LOG.json` appearing,
would have left both sentences reading precisely as they always had, the
same silent-survival shape `mutate.py`'s hard-coded gate-3 claim already
demonstrated concretely: true the day it was typed, and nothing afterward
could make it false again.

A second, smaller finding surfaced while checking for it: `BUSINESS.md` is
committed and re-rendered by `business_map.py`, but unlike `DECISIONS.md`,
`CAPABILITIES.md`, `INVARIANTS.md`, `execution_state.json` and `mutation_
probe.json` — every other derived-and-committed document in this
repository — nothing regenerates or diffs it in CI or in CLAUDE.md's gate
block. Measured directly: it had drifted eleven commits stale (`195` vs the
live `206`) with nothing anywhere reporting so. Not fixed in this round —
see "what was considered" below for why a `git diff --exit-code BUSINESS.md`
step would be structurally wrong here, in the same way D-035's addendum
found `mutation_probe.json`'s `source_commit` structurally wrong for a
`pull_request` CI run. `BUSINESS.md` was regenerated by hand as part of this
round's own gate run, which is the correct remedy for a drift this shaped
until a real fix exists — recorded here rather than silently folded into an
unrelated commit.

**what was built.** `state_map.py` gained `_business()`, importing
`business_map` and calling its three existing functions rather than
re-deriving any of them — the same "no second resolver" reasoning
`_capabilities()` already documents for `capability_map`. `derive()` now
carries a `"business"` fact block (`listings_live`, `modules_live`,
`goods_passed`, `goods_promised`, `revenue_recorded`). `gates()` reads it:
when both facts are still at their original "nothing yet" values, the
prose is byte-identical to what it always was, so no committed history
changes meaning. When either fact moves, the gate does **not** silently
flip to `PASS` — that would substitute a machine's arithmetic for a
person's judgment on exactly the two gates furthest from anything code can
decide — it instead names the new count and says outright that a person
must re-argue the gate against what the fact actually proves, staying
`UNKNOWN` either way. This is deliberately narrower than gates 1-3's fix:
those gates' underlying claims (a mutation probe's kill count, a capability
registry's size) are themselves the evidence a machine may assemble: gates
11 and 12 are `PASS`/`FAIL` calls this repository's own Constitution
reserves for a person, so the fix here stops the gate from lying about the
inputs to that judgment without pretending a machine may render the verdict.

**what was verified.** `test_business_facts_agree_with_business_map_itself`
(no second resolver, checked directly against the same three functions).
Two sabotage tests, the same shape D-035 used to prove gate 3's fix was not
decorative: `test_gate_11_moves_when_a_listing_goes_live` monkeypatches
`business_map.goods()` to return one live listing and asserts the gate's
`why` text no longer contains `"0 listings live"`, now names the real count,
says a person must re-argue it, and stays `UNKNOWN` throughout;
`test_gate_12_moves_when_a_revenue_log_appears` does the equivalent for
`business_map.revenue()`. Both existing tests
(`test_the_repaired_gates_derive_their_evidence_rather_than_stating_it` and
the absence-checker regression test guarding the exact "no revenue log
exists ... BUSINESS.md refuses" sentence) still pass unmodified. Full
documented gate sequence run start to finish: ruff/format/mypy, every
invariant, `env_check.py`, `extras_check.py`, `release_check.py --target
engine`, claims/runs/spine, `actions_pin_check.py` (20/20, and each of the
seven distinct pinned actions independently checked against its own public
repository's tags through this session's git-proxy read lane — all seven
already at their current major version, so no further bump was due this
round), `n8n_bindings_check.py`, `readme_check.py` (1,320, up from 1,317 —
3 new tests; regenerated after `--check` correctly caught the drift my own
new tests introduced), `node_dossier.py` + diff, `apply_decisions.py
--dry-run`, full `pytest tests/`, `mutate.py` (29/29 killed, unchanged) + its
diff check, `capability_map.py --check`, `state_map.py --check`,
`eval_gate.py`. `release_check.py --target citegate` still fails on the
same pre-existing, previously-documented git-remote reversion (`origin`
reading `RaveZona/omnex-factory` rather than the org's transferred path),
reproduced independently of this change and unrelated to it.

**what else was considered.** Making gates 11/12 derive a `PASS` once
`listings_live > 0` or `revenue_recorded` is true — rejected: §21 of the
Sovereign Execution Standard is explicit that a confirmed human decision may
never be synthesized, and a live listing or an existing revenue log is a
fact about *inputs*, not a verdict on commercial or economic maturity a
machine is positioned to render; collapsing "the count moved" into "the gate
passed" would be exactly the overreach `apply_decisions.py` already refuses
by name for node confirmations. Adding a `git diff --exit-code BUSINESS.md`
CI step to close the staleness finding in the same round — rejected after
checking why it was never added: `business_map.py`'s `Age.days` and
`recent_commits` are computed from `datetime.now(UTC)` and a rolling
"30 days ago" window, not from the checked-out commit alone, so the
rendered file differs from itself between two runs on two different days
even with zero new commits — a `git diff --exit-code` gate on it would be
permanently red the day after any regeneration, the exact "a permanently red
build is one people ignore" failure CLAUDE.md already names for
`live_listings_are_covered`. The correct fix is narrower than the pattern
used for `DECISIONS.md`/`mutation_probe.json` (a masked or partial-field
comparison, `--check`ing only the goods/live/revenue substance and ignoring
the elapsed-time line, mirroring how `state_map.py`'s own `differences()`
drops `source_commit`/`branch`/`tree_clean`) and is left for a following
round rather than rushed alongside an unrelated fix in this one.

**reversible how.** One new fact block on the derived-state graph
(`business`, feeding gates 11 and 12's evidence and prose only), no new
committed file, no CI step added or removed, no script added to or removed
from the set `test_ci_runs_every_gate_script_the_document_names` and its
mirror check. `git revert` restores the two literal sentences exactly as
they were — a regression in kind, not a break, since nothing downstream
depends on the new `business` fact block existing.

## D-037: BUSINESS.md's freshness gap, closed the way D-036 said it should be

**context.** D-036 diagnosed a real gap and deliberately did not fix it in
the same round: `BUSINESS.md` is the one derived-and-committed document in
this repository that nothing regenerates or diffs anywhere — unlike
`DECISIONS.md`, `CAPABILITIES.md`, `INVARIANTS.md`, `execution_state.json`
and `mutation_probe.json`, all five of which fail CI when they disagree
with a fresh run. Measured directly at the time: 11 commits stale (`195`
committed vs `206` live), moving to `208` by the time this round started —
proof the gap was still open, not a one-time measurement that had since
self-corrected.

**why it was not a same-round fix.** A naive `git diff --exit-code
BUSINESS.md` step, copying the pattern already used for `DECISIONS.md` and
`mutation_probe.json`, would have been *worse* than the gap it closed.
Every other diff-checked document here is a pure function of the
checked-out commit — run the generator twice against the same tree and it
produces the same bytes. `BUSINESS.md` is not: `business_map.age()`'s
`days` field is `(now - started).days` and `recent_commits` counts commits
in a rolling "30 days ago" window, both keyed to `datetime.now(UTC)` at the
moment the script runs, not to the commit alone. A raw diff would go red
the calendar day after every regeneration even with zero repository
changes — the same "permanently red build is one people ignore" failure
CLAUDE.md already names for `live_listings_are_covered`, and structurally
the same trap `mutation_probe.json`'s `source_commit` field fell into on a
`pull_request` CI run (D-035's addendum) before that field was removed
outright. `BUSINESS.md` cannot drop the volatile content the way
`mutation_probe.json` did, though — the elapsed-time line is the document's
whole first paragraph, not an optional field — so the fix had to be a
comparison that ignores it rather than a schema that omits it.

**what was built.** `business_map.py` gained `--check` (mirroring
`readme_check.py`'s and `state_map.py`'s existing `--check` convention) and
two module-level pieces: `_VOLATILE`, a regex matching `_elapsed()`'s
sentence in either of its two shapes (the normal day-count line and the
shallow-clone refusal, which also embeds a bare commit count and needed the
same treatment), and `_stable()`, which substitutes both shapes with a
fixed placeholder before comparing. `--check` renders the current facts,
reads the committed file, and fails only when the *masked* versions
disagree — the same "drop the volatile field before comparing" move
`state_map.py`'s own `differences()` already makes for `source_commit`,
`branch` and `tree_clean`, applied to a markdown sentence via regex
substitution instead of a JSON key exclusion, because there is no
structured field here to drop. Wired into `engine.yml` (a new "Business
figures are current" step, placed beside "Capability registry" in the
cluster of derived-document checks) and into CLAUDE.md's gate block
(`business_map.py --check`, between `capability_map.py --check` and
`state_map.py --check`) — required to be in both by
`test_ci_runs_every_gate_script_the_document_names` and its mirror, the
same bidirectional test that has caught this exact class of drift for
`node_dossier.py` and `eval_gate.py` in earlier rounds.

**what was verified.** The masking property directly, not assumed from
reading the regex: `render(2026-08-01)` and `render(2026-09-12)` produce
different text (`early != later`, ruling out a vacuous test) but identical
text once both pass through `_stable()`. The shallow-clone shape
separately, since it carries its own bare commit count with no day count
alongside it — masked exactly like the normal sentence, proven by
asserting the phrase survives in the raw render and disappears after
`_stable()`. A structural sabotage test (renaming a section heading, never
a current figure, so the test does not go stale as real numbers move)
confirms `--check` still exits `1` on a genuine disagreement — the check
that proves the mask has not swallowed more than it was built to. A
missing-file case, and the real committed `BUSINESS.md` held to its own
new standard (`test_the_committed_business_md_passes_check`). One test
bug caught while writing this: the shallow-clone test's first version
asserted the refused phrase *survived* masking, backwards from what the
fix requires, and a second version used a rendering date before the
repository's first commit, producing a negative day count `\d+` could not
match — the regex was tightened to `-?\d+` for robustness even though a
real invocation cannot run before the repository it measures existed.
Full documented gate sequence run start to finish: ruff/format/mypy, every
invariant, `env_check.py`, `extras_check.py`, `release_check.py --target
engine`, claims/runs/spine, `actions_pin_check.py` (20/20),
`n8n_bindings_check.py`, `readme_check.py --check` (1,327, up from 1,320 —
7 new tests), `node_dossier.py` + diff, `apply_decisions.py --dry-run`,
full `pytest tests/`, `mutate.py` (29/29 killed, unchanged) + its diff
check, `capability_map.py --check`, `business_map.py --check`,
`state_map.py --check`, `eval_gate.py`. `release_check.py --target
citegate` still fails on the same pre-existing, previously-documented
git-remote reversion, and `tests/test_mcp.py::test_a_rate_limited_tool_
refuses_the_call_it_cannot_afford` reproduced its own already-documented
flake (see PR #50's own comment thread) — reran clean in isolation both
times, unrelated to anything this round touched.

**what else was considered.** A tuned staleness threshold ("fail if more
than N commits old") instead of a masked comparison — rejected: this
repository's own conventions prefer a structural fix to a tuned threshold
(`Fleet.assign()`'s refusal is the named precedent), and a threshold would
still be red or green somewhat arbitrarily rather than tracking whether the
*content that matters* actually disagrees. Parsing the rendered numbers
back out of the markdown table with a second reader, the way
`readme_check.py` extracts one quoted figure — rejected as more surface
than needed: `readme_check.py` owns exactly one sentence in a file it does
not otherwise generate, while `business_map.py` already owns the entire
render path, so masking the one volatile paragraph and diffing the rest
verbatim is simpler than re-deriving a parser for content the same module
already produces.

**reversible how.** One new CLI flag on an existing script, one new CI
step, two new module-level helpers (`_VOLATILE`, `_stable`), no new
committed file, no schema change to `BUSINESS.md` itself. `git revert`
returns `business_map.py` to write-only, and removing the matching
`engine.yml` step and CLAUDE.md line keeps
`test_ci_runs_every_gate_script_the_document_names` and its mirror
satisfied on the reverted set.

## D-038: the €0.00 cost-panel bug (3766976) recurring one layer down, in the rate table itself

**context.** Every round this session had truth-passed `engine/` — the
Python platform. The root TypeScript app, the actual commercial money path
CLAUDE.md calls "the keystone," had not been exercised at all: `npm audit`,
`tsc --noEmit`, `vitest run` and `next build` are the documented root gate
and none had run this session before now. Running them found the suite
green, which is exactly why reading the code they cover mattered more than
trusting a green run — a passing test proves what it asserts, not what
nobody thought to assert.

**what was found.** `lib/core/agents/budget.ts`'s `estimateCostEur()` — the
function `priceCall()` calls for every real customer-facing copilot run —
priced `groq`, `google` and `huggingface` at zero unconditionally, keyed
only by provider name. `lib/core/llm/provider.ts`'s `providers()` lets an
operator override `GROQ_MODEL`, `GOOGLE_MODEL` or `HF_LLM_MODEL`
independently of provider selection — verifiable from this repository's
own source with no external pricing knowledge needed. Point one of those
env vars at a different model on the same hosted API and the provider
still bills whatever it actually bills, while `priceCall()` keeps returning
`costEur: 0` for every such run because it only ever looked at
`result.provider`, never `result.model` — despite `LlmResult` already
carrying `model` on every result, unused by this one call site. Any
customer run through that path would settle at the 1-credit floor no
matter how much the provider actually charged: the exact "cost panel reads
€0.00 while money moves" shape `3766976` already fixed once for missing
`usage` wiring, recurring here in the rate table itself rather than in
`usage` plumbing. `CLAUDE.md`'s own `budget.ts` bullet already documented
the `cache:`-before-fallback rule this same function gets right one line
later — the adjacent rule, model-scoping, had no bullet and no test.

Deliberately not claimed: that Groq, Google AI Studio or Hugging Face's
router are *not* free today for their current default models. This
environment cannot reach their pricing pages to check (the open web is
blocked here; only PyPI/npm/crates.io/GitLab/DockerHub and GitHub's git
lane answer), and asserting a specific external billing fact without being
able to verify it would be the same "NO EVIDENCE = NO CLAIM" violation in
the opposite direction. What is fixed is narrower and needs no external
verification: the codebase's *own* stated free defaults —
`llama-3.3-70b-versatile` on Groq, `gemini-2.0-flash` on Google,
`meta-llama/Llama-3.3-70B-Instruct` on Hugging Face, the exact strings
`providers()` itself hardcodes — are what stays priced at zero. Any other
model an operator points the same provider at now falls through to the
existing "unknown, treated as paid" fallback, the identical principle this
function already applied to an unrecognised provider name, now applied at
model granularity too. OpenRouter needed no such table: its own `:free`
model-id suffix is a structural, checkable fact, not a claim this codebase
has to maintain.

**what was built.** `estimateCostEur(provider, model, promptTokens,
completionTokens)` — `model` is now a required parameter, not bolted on
optionally, so no call site can silently keep pricing by provider name
alone. `FREE_DEFAULT_MODEL` names the three (provider, model) pairs that
are actually free by this codebase's own configuration; `isFreeCall()`
special-cases OpenRouter's suffix convention and falls back to that table
for everything else. `RATE_PER_MTOK` now holds only genuinely
unconditional entries: `ollama` (self-hosted, never leaves this process's
own host, free regardless of model) and the two image providers
`pollinations`/`local` (no configurable model override, no paid tier this
codebase talks to — left untouched, out of scope for this finding).
`priceCall()` in `metering.ts` now threads `result.model` through both of
its call sites (the reported-usage path and the length-estimate fallback).

**what was verified.** `npx tsc --noEmit` did *not* catch the signature
change at any test call site — `tsconfig.json` excludes `lib/__tests__/**`
from the type-checked set, so the three existing call sites with the old
3-argument shape passed a token count where `model` now belongs, sliding
every subsequent argument one position and turning `NaN` into a silently
wrong answer rather than a caught type error. Found this by running
`npx vitest run` on the affected files directly (not assumed from `tsc`
being clean): four tests failed with `NaN` and `false` where `0` and
`true` were expected, the concrete cost of trusting a type check that does
not cover test files. All four updated to pass a real model string. Two
new tests added, at two levels: `estimateCostEur('groq', <default>, …)` is
zero while `estimateCostEur('groq', <anything else>, …)` is paid (same
for `google`), and a `priceCall()`-level test constructs two `LlmResult`s
differing only in `model` and asserts one is free and the other is not —
the level a real request actually goes through, not just the pricing
function in isolation. Full root gate re-run end to end after the fix:
`npm audit --audit-level=moderate` (0 vulnerabilities), `tsc --noEmit`
(clean), `vitest run` (85 tests, up from 82 — all passing), `next build`
(compiles, all 17 routes render/collect cleanly). `engine/tests/
test_ci_contract.py` re-run since `CLAUDE.md` changed (unaffected;
untouched by this PR's actual gate scripts).

**what else was considered.** Hard-coding a specific non-zero rate for
Groq/Google/Hugging Face's paid tiers instead of falling through to the
generic unknown-provider estimate (`{in: 1.0, out: 3.0}`) — rejected: this
environment cannot verify current published rates for any of the three, so
a specific number would be exactly the unsupported claim this fix exists
to remove, just moved from "free" to "a specific wrong price." The generic
paid fallback is honest about what it is — a conservative placeholder, not
a measurement — the same status quo already accepted for any other unknown
provider. Extending the same model-scoping to the two image providers
(`pollinations`, `local`) — not done: neither has a configurable model
override env var, and both are genuinely free regardless of model (a
public free API and self-hosted compute respectively), so there is no
override loophole for them to close.

**reversible how.** One required parameter added to an exported function
(`estimateCostEur`), all three of its call sites in this repository updated
in the same change, no new file, no schema or API surface change outside
`lib/core/agents/budget.ts` and `lib/core/agents/metering.ts`. `git revert`
returns to provider-only pricing — a regression in kind (the exact defect
this closes), not a break, since nothing downstream depends on the new
parameter's presence beyond the two files that already call the function.

## D-039: the Stripe webhook could not tell a duplicate delivery from a retry of a failure — a paid customer could lose their credits silently

**context.** Continuing the truth pass into the money path after D-038,
this round read `app/api/stripe/webhook/route.ts` — "the only place credits
are granted for money," per its own docstring — against §9 (Credit /
Billing Integrity) and §22 (Adversarial Verification) of the Sovereign
Execution Standard: not "does it work" but "how would this fail under a
retry, a partial failure, a race." No test file existed for this route at
all before this round — an E1/E2 capability (code-present, declared) with
no E3 (tested) evidence, on the one route that moves real money.

**what was found.** The idempotency gate inserted `event.id` into
`webhook_events` and treated any primary-key conflict as "already handled."
That is correct for a genuine duplicate delivery. It is wrong for the other
case migration 001's own comment names but does not handle: a webhook that
claims its row and then fails mid-processing (a transient Supabase outage,
a timeout, anything after the insert) leaves that row behind with no
distinguishing mark. Stripe retries on any non-2xx response — the handler's
own catch block returns 500 specifically to trigger that retry — but the
retry's insert hits the identical conflict and is silently answered
`{received: true, duplicate: true}`. The customer paid, `grantCredits` never
ran, and Stripe stops retrying because the handler just told it the delivery
succeeded. Reproduced directly against a real Postgres before writing any
fix: inserted a row, marked it `:failed` (exactly what the catch block
does), then confirmed the old check (`exists(select 1 from webhook_events
where id = ...)`) reads `true` regardless of whether the prior attempt
succeeded or failed — the two states this repository's own `webhook_events`
schema records are indistinguishable to the code that reads it.

**what was built.** Migration 003 adds `claim_webhook_event(id, type)`,
returning `'new'` (never seen), `'retry'` (a prior attempt at this exact
event failed) or `'duplicate'` (already succeeded, or another request
currently owns it) — three outcomes where the route previously had one
boolean. The insert-then-conditional-update happens inside a single
PL/pgSQL function (`insert` in the main body, `unique_violation` caught,
then an `update ... where id = p_id and type = p_type || ':failed'`), so
the atomicity is a database property rather than an application-level
check-then-act — the identical reasoning `consume_credits`' `FOR UPDATE`
row lock already uses one function up in the same migration file, applied
here to a conditional `UPDATE`'s implicit row lock instead. A companion
`mark_webhook_event_failed(id, type)` replaces the route's raw `update`.
`route.ts` now branches on the RPC's three outcomes: `'duplicate'` returns
early exactly as before; `'new'` and `'retry'` both proceed into the
existing `switch` unchanged.

**what was verified.** This sandbox has no Docker daemon, so the committed
`credits.db.test.ts` suite — which starts its own disposable Postgres
container via testcontainers, the established pattern for anything whose
correctness IS a database constraint or lock — could not run here; its own
docstring states plainly why a mock cannot substitute (`consume_credits`'
row lock, and now `claim_webhook_event`'s, are database properties, not
application logic a fake client could reproduce). Four new tests were added
to that suite in the same style (new / duplicate / retry / concurrent
retry), which CI's real Postgres container will run — but "will run in CI"
is not "was verified now." Rather than stop at that limitation, a real
local PostgreSQL 16 turned out to be installed in this environment (`psql`,
`pg_ctlcluster` present via `postgresql-16`, independent of Docker): started
it, applied the same sanitized migration 001 the test harness applies plus
the new migration 003, and ran the exact scenarios directly. Confirmed, in
order: a never-seen event returns `'new'`; a second claim of a
never-marked-failed event returns `'duplicate'`; a claim marked `:failed`
and reclaimed returns `'retry'` and resets the row so a THIRD claim
correctly reads `'duplicate'` again; and — the property no sequential test
can establish — five genuinely concurrent OS processes (`psql &` five times,
`wait`) claiming the same failed event returned exactly one `'retry'` and
four `'duplicate'`, proving the row-lock atomicity holds under real
concurrency, not simulated sequencing. The original bug was reproduced on
the same database before any fix existed, confirming the finding was real
and not a misreading of the code. Root gate green after the fix: `npm audit`
(0 vulnerabilities), `tsc --noEmit`, `vitest run` (89 tests, +4 — all
passing, the four new ones a graceful no-op here exactly like the existing
suite's own Docker-unavailable path, per its established convention), `next
build` (17 routes, clean).

**what else was considered.** Flipping to "insert after successful
processing" instead of "insert before, retry on failure" — rejected: that
reopens the exact race `webhook_events`' insert-first design was built to
close (migration 001's own comment: "so two concurrent requests can never
double-spend the same credits"). Two truly concurrent deliveries of a
not-yet-failed event would both pass a check-then-insert gate and could
both grant credits. Handling this at the application level (read the row,
branch on its `type` in TypeScript, then conditionally update) — rejected
for the same reason a TypeScript-level fix was rejected for
`consume_credits` originally: the three-way decision needs to be atomic
across concurrent requests, and that atomicity is a single-statement
database property, not something two round-trips from Node can guarantee
without introducing a second lock of its own. Writing a NEW test file with
its own container instead of extending `credits.db.test.ts`'s — rejected:
both exercise tables from the same migration, and a second 240-second image
pull in CI for schema this size is cost with no isolation benefit gained.

**reversible how.** One new migration file (`003_webhook_retry.sql`,
additive — matches the existing `001`/`002` numbering convention, neither
edited in place), one route file changed to call two new RPCs instead of a
raw insert/update, four new tests in an existing suite. `git revert` returns
`route.ts` to the raw insert/update pattern; the two new SQL functions stay
harmless and unreferenced if left in place, or a follow-up migration can
drop them. Nothing downstream depends on the new outcomes beyond the one
route that already calls them.

## D-040: every wired rate limit was bypassable by an authenticated attacker rotating one header

**context.** Continuing the truth pass into the money/security path after
D-039, this round read `lib/core/security/ratelimit.ts` against §11 (MCP /
Tool Security — "rate controls") and §22 (Adversarial Verification — the
question is not "does it work" but "how would this fail under attack"). No
test file existed for this module at all before this round, on the
mechanism that is supposed to stop a single caller from hammering paid
provider calls, storage uploads, streaming connections and Stripe checkout
creation.

**what was found.** `checkRateLimit()` derived its key entirely from
`getClientId()`, which reads `x-forwarded-for` or `x-real-ip` — headers the
calling client sets on the request it sends. Every route that actually
calls `checkRateLimit` — `studio_generate`, `studio_upload`,
`copilot_stream`, `stripe_checkout` — already authenticates the caller with
Supabase (`supabase.auth.getUser()`) *before* the rate-limit check, so a
verified, non-spoofable `user.id` was sitting one line above every single
call and never used. An authenticated attacker who cannot forge a session
can trivially forge a header: sending a fresh `x-forwarded-for` value on
every request landed each call in its own IP-keyed sliding window, so the
limit never engaged no matter how many requests the same authenticated
account sent. This is exploitable regardless of any question about which
deployment platform's edge does or does not sanitize that header for
anonymous traffic — the identity that matters here (the authenticated user)
was never consulted at all.

**what was built.** `checkRateLimit(request, route, identity?)` gained a
third, optional parameter. When passed, it is the key, full stop, and the
header is never read — `const clientId = identity || getClientId(request)`.
All four call sites now pass `user.id`. The module docstring states plainly
what this fix does and does not claim: it does not assert that
`x-forwarded-for` is trustworthy on any particular host for the two
configured limits (`email_send`, `auth`) nothing in this repository calls
yet — an unverifiable claim about a deployment platform's edge behaviour
from an environment with no way to check it — only that every limit
actually wired to a route now keys on an identity nothing but a valid
session can produce.

**what was verified.** `lib/__tests__/ratelimit.test.ts` — the first test
file for this module — proves the exact bypass is closed: the same
identity, a brand-new spoofed IP on every one of `MAX` calls, still hits
the limit on call `MAX + 1`. Proven not decorative by sabotage, the
established discipline this repository already applies elsewhere
(`mutate.py`, `eval_gate.py`'s regression test, the copilot integration
test's `spendCredits` sabotage): reverted `ratelimit.ts` to the
header-only pre-fix version and confirmed 4 of 5 new tests fail, the bypass
test among them, with the exact assertion this fix exists to make true —
then restored the fix and confirmed all 5 pass again. Root gate green:
`npm audit` (0 vulnerabilities), `tsc --noEmit`, `vitest run` (94 tests,
+5), `next build` (17 routes, clean).

**what else was considered.** Fixing `getClientId()` itself — e.g.
preferring the last comma-separated entry over the first, on the RFC 7239
convention that intermediate proxies append their own observed peer address
to the end of the chain — considered and rejected for this round: whether
that convention holds depends on how many hops sit between a real client
and this process, which is a property of the deployment topology (Vercel's
edge vs. the self-hosted `DOCKER.md`/`compose.yaml` path this repository
also documents), not something a general rewrite of the parsing order can
get right for every topology at once, and asserting one platform's behavior
as fact would be exactly the claim this decision explicitly declines to
make elsewhere. Left as a named, honest gap rather than a rewrite that
swaps one unverified trust assumption for another. Making `identity`
required rather than optional — rejected: two configured limits have no
route wired to them yet, and forcing every future caller to supply an
identity forecloses ever adding a genuinely anonymous rate-limited route
without a signature change.

**reversible how.** One optional parameter added to an exported function,
four call sites updated to pass it, one new test file, no schema or API
surface change elsewhere. `git revert` returns to header-only keying — a
regression in kind (the exact defect this closes), not a break, since
nothing downstream depends on the parameter's presence.
