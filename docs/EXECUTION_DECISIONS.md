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
