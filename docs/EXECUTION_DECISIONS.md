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
