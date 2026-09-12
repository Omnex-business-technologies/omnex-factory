# OMNEX Factory

Two codebases in one repository. `engine/` is a zero-dependency Python AI
platform (18 production systems). The Next.js app at the root is the commercial
surface that sells access to them.

## The commands that gate a change

```bash
# TypeScript — root
npm audit --audit-level=moderate && npx tsc --noEmit && npx vitest run && npx next build

# Python — from engine/
.venv/bin/ruff check src tests scripts \
  && .venv/bin/ruff format --check src tests scripts \
  && .venv/bin/mypy \
  && .venv/bin/python scripts/invariant_map.py \
  && .venv/bin/python scripts/env_check.py \
  && .venv/bin/python scripts/extras_check.py \
  && .venv/bin/python scripts/release_check.py --target citegate \
  && .venv/bin/python scripts/release_check.py --target engine \
  && .venv/bin/python scripts/claims.py --check \
  && .venv/bin/python scripts/runs.py --check \
  && .venv/bin/python scripts/spine_check.py \
  && .venv/bin/python scripts/actions_pin_check.py \
  && .venv/bin/python scripts/n8n_bindings_check.py \
  && .venv/bin/python scripts/readme_check.py --check \
  && .venv/bin/python scripts/node_dossier.py \
  && git diff --exit-code ../corpus/universal-ai-os/DECISIONS.md \
  && .venv/bin/python scripts/apply_decisions.py --dry-run \
  && .venv/bin/python -m pytest tests/ -q \
  && .venv/bin/python scripts/mutate.py \
  && git diff --exit-code ontology/mutation_probe.json \
  && .venv/bin/python scripts/capability_map.py --check \
  && .venv/bin/python scripts/business_map.py --check \
  && .venv/bin/python scripts/state_map.py --check \
  && .venv/bin/python scripts/eval_gate.py --baseline suites/baseline.json --out .omnex/runs

# citegate — from oss/citegate/
../../engine/.venv/bin/python -m pytest tests/ -q
```

**Both release targets, never one.** `release_check.py` passed on citegate and
reported thirteen refusals against engine of which thirteen were false. A gate
that is right for the wrong reason looks exactly like a working one until a
second target exists.

**`ruff format --check` is not optional.** Omitting it locally is what turned CI
red at `01c73c8`; `ruff check` passes on code `ruff format` would rewrite. CI
(`.github/workflows/engine.yml`) runs it on Python 3.11, 3.12 and 3.13.

**This block is not documentation, it is an assertion.**
`engine/tests/test_ci_contract.py` reads it and requires CI to be a superset of
it. That test also catches the reverse failure, which had already happened: CI
ran `vitest run` against two hand-named files, one of which did not exist, so it
covered one suite of seven. Note its boundary honestly — it compares this block
with CI and cannot see a rule that is weak on *both* sides. `ruff format --check`
omitted `scripts` here and in CI, they agreed, and only reading them together
with fresh eyes found it.

Current state: **1,327 engine tests · 108 TypeScript · 16 citegate**, all green,
plus **29 of 29 mutations killed**, and the spine's **14 of 14 transitions
EXECUTABLE**.
All 100 TypeScript tests now run in CI; until recently, seven of them did.
**All 16 citegate tests now run in CI too** — until this commit, none of them
did: every `pytest` in every workflow inherited `working-directory: engine`.

## engine/src/omnex/ — what each module is for

| module | what it does | the number it carries |
|---|---|---|
| `core` | Money (pico-dollars), Clock, errors, ids | — |
| `router` | cheap→verify→escalate routing | routed spend **42.4%** of always-strong at equal accuracy |
| `rag` | retrieval + page- and figure-anchored citations + grounding | **25–30k** sentences/sec, flat with document size |
| `vectors` | hybrid dense/lexical store, RRF | — |
| `guard` | injection fence, PII, rate limits, sandbox | **30/30** attacks, **1/30** false positives |
| `evals` | golden cases, metrics, regression gate | gates on newly-failing cases, not the mean |
| `crew` | multi-agent consensus, hash-chained audit | — |
| `hitl` | human approval bound to a fingerprint | — |
| `harness` | long-running loop: worth-it gate, contract, evaluator, edges, isolation, state, outer loop | outer loop watches **cost per accepted change** |
| `mcp` | JSON-RPC 2.0 tool protocol over a `Transport` Protocol | built because **62 of 509 figures** named it — the top of `BUILD_ORDER.md` |
| `factory` | spec · gates · compilers · per-run economics · portfolio · the loop back | `worth_it` at the head of ten stages; `parse(emit(bp)) == bp` across **3 targets × 5 paradigms**; margin per run in exact picos |
| `intel` | opportunity scanning over public sources | — |
| `memory` `obs` `graph` `llm` `serving` `finetune` `deploy` `tenancy` `pipeline` | agent memory · OTel+Prometheus · graph runtime · provider adapters · inference · LoRA/DPO · packaging · multi-tenancy · queues+webhooks | — |

### Non-obvious invariants — breaking these is silent

**These are now checked, not asserted.** Each id below is an entry in
`engine/ontology/invariants.json` with a predicate behind it;
`scripts/invariant_map.py` runs them all and exits non-zero on any breach. Two
of the five defects found in the audit that produced this section were direct
violations of rules written right here, greppable in minutes, sitting untouched
because nothing grepped. A rule that is not in a gate decays at that rate.

- **Money is `int` pico-dollars (1e-12 USD).** Micro-dollars round cheap-model
  tokens to zero, so a router that saves money reports saving nothing. Never
  introduce a float currency path. → `money_is_int_picos`
- **Time comes from an injected `Clock`.** Nothing calls `datetime.now()` or
  `time.monotonic()` directly. `FakeClock` is why the suite asserts on hour-long
  TTLs and still runs in 7 seconds. → `time_is_injected` (two allowlisted files,
  each naming the parameter that already provides injection)
- **Zero required dependencies.** Heavy libraries (torch, transformers, pdf) sit
  behind Protocol adapters and are optional extras. A test must not need them.
  → `zero_required_dependencies`
- **`StrEnum` inherits `str` comparisons**, so `@total_ordering` fills in
  nothing. Any ordered `StrEnum` (e.g. `Tier`) must define all four comparisons
  explicitly. → `ordered_strenum_writes_all_four`
- **Symbol resolution has one implementation**, in `omnex.core.symbols`,
  imported by everything that asks whether a name exists.
  → `one_symbol_resolver`
- **The two sentence splitters must agree.** They are separate copies on purpose
  and have diverged twice. → `twin_splitters_agree`
- **A stated limitation is kept as a passing test.** `test_a_paraphrase_outside_
  the_corpus_is_missed` and the inverted-polarity grounding test are *supposed*
  to be green. Do not "fix" them; they are the honesty anchors.
  → `limitations_are_passing_tests`, declared **unenforceable**: a checker keying
  on test names would be satisfied by renaming one.
- **Refusals name every failing condition at once**, not the first.
  → `refusals_name_every_condition`, declared **unenforceable**.
- **Docstrings explain why and name the failure prevented.**
  → `docstrings_name_the_failure`, declared **unenforceable**: any mechanical
  proxy turns a convention into a quota.
- **A live listing may not promise more than QC passed.** The €49 Complete
  Vault sells "170+ images" against 80 in the manifests. Scoped to `live`
  offers — mirroring `registry.ts`'s `enabled` — because "you must have 170
  images" would be red until the day they exist, and a permanently red build is
  one people ignore. → `live_listings_are_covered`
- **An n8n binding names a credential and never carries one**, and may not claim
  confirmation without a person's name and a date. The emitted workflow JSON is
  committed and shared; a key in it is an incident, not a configuration.
  → `bindings_carry_no_credentials`
- **An extra delivers what it declares, or says it does not.** `pip install
  omnex-engine[agents]` installed langgraph and crewai and gave you nothing —
  six of twelve extras had **zero** of their dependencies imported anywhere.
  Deliberately not "every extra needs an adapter": a declaration is evidence of
  an intended interface, not proof one should exist, so `unsupported` with a
  reason passes and silence does not. Checked per **dependency**, because
  `vectors` imports qdrant-client and not sqlite-vec or numpy.
  → `every_extra_declares_what_it_delivers`
- **Suite fingerprints refuse cross-suite comparison.** Editing an expected
  answer and re-running is otherwise indistinguishable from an improvement.

## Root app — the money path

- `lib/core/llm/provider.ts` — `LlmResult` carries an optional `usage` block.
  **This is the keystone**: without it nothing downstream can compute cost, and
  the copilot's cost panel reads €0.00 on every real run (the bug fixed in
  `3766976`).
- `lib/core/agents/metering.ts` — `priceCall()` returns `estimated: boolean`.
  An estimate is never displayed as a measurement.
- `lib/core/agents/budget.ts` — `estimateCostEur()` checks `cache:` **before**
  the unknown-provider fallback, or the one free path bills at the most
  expensive rate. **Free is priced per (provider, model), never per provider
  name alone.** `groq`, `google` and `huggingface` all priced at zero
  regardless of model until this was found: `providers()` lets `GROQ_MODEL` /
  `GOOGLE_MODEL` / `HF_LLM_MODEL` override the model independently of which
  provider is selected, so pointing one at a paid model billed the provider
  real money while every customer run kept showing €0.00 — `3766976`
  recurring one layer down, in the rate table rather than in `usage` wiring.
  `FREE_DEFAULT_MODEL` now names the exact model each free default configures;
  anything else on that provider falls through to the paid fallback, and
  OpenRouter is checked by its own `:free` suffix rather than a guess.
- `lib/modules/registry.ts` — module manifests. **Rule: module N+1 does not
  open until module N has taken a real payment.** Only `studio` is live;
  everything else is `enabled: false` on purpose, and `lib/__tests__/metering.
  test.ts` asserts `liveModules()` is exactly `['studio']`.
- Billing on the copilot: charged **on completion, proportional to measured
  cost, floor 1 credit**. Settlement runs in `onSettled` and fires on success,
  error **and** abort — a run that spent money and failed is the one an operator
  most needs to see.

## Where things live

- `engine/suites/` — benchmark suites + `LEADERBOARD.md` (fingerprint `884533eb08028871`)
- `engine/scripts/skill_numbers.py` — **the only source** of every number the
  skills publish. Re-measures rather than restates.
- `engine/ontology/` — the branch map onto `engine/`. `branches.json` holds
  claims and contains **no figures**; `scripts/ontology_map.py` resolves every
  symbol to decide status and renders `COVERAGE.md`. A claim for code that does
  not import fails CI. **`source` is load-bearing**: `proposal` branches were
  written down before anyone looked, `corpus:` branches were read out of a
  document. A map of an assumed list can confirm every entry on it and still be
  missing the field — v1 said 10 gaps against 28 assumed branches, and reading
  one corpus added 10 more.
- `engine/ontology/invariants.json` — **this repository's own rules, as
  predicates.** What `ontology_map.py` does for branches, one level in:
  `scripts/invariant_map.py` runs every checker, renders `INVARIANTS.md`, and
  exits non-zero on a breach. **A rule with no checker AND no written reason one
  is impossible fails the script** — the mechanism that stops the registry
  becoming a second copy of this file. Currently **9 of 12 enforced**, 3 declared
  unenforceable with reasons, 2 allowlisted exceptions that each name a working
  injection point. Each bullet in "Non-obvious invariants" above cites its id,
  and a test requires that link in both directions.
- `engine/ontology/capabilities.json` + `CAPABILITIES.md` +
  `engine/scripts/capability_map.py` — **the canonical capability registry**
  (Sovereign Execution Standard, Phase 1). A person states name, symbol,
  contract, dependencies, security requirements, limitations, known risks;
  everything the standard calls evidence is derived — E1 (declared, does not
  resolve) through E4 (integrated: another production module references it,
  excluding its own defining file). E5-E7 need a running deployment this
  repository does not have and are reported `E5_UNKNOWN_NOT_OBSERVABLE`
  rather than guessed. Currently **8 capabilities**, a deliberately small
  first cut. `state_map.py`'s gate 3 derives from `summarise()`, imported,
  never a second count.
- `engine/src/omnex/mcp/tools.py` + `server.py` — **§11 MCP/TOOL SECURITY's
  remaining three requirements**, added to a module that already had
  permission scoping (D-020): timeout controls, rate controls, and
  dangerous-operation classification. `ToolSpec` gained `timeout_seconds`
  and `dangerous`; `dangerous` is wire-safe (`as_dict()`/`from_wire()`)
  because it grants nothing and only warns a caller, while
  `required_permission` stays server-local because a forged claim there
  would grant access. Rate limiting reuses `guard.ratelimit.RateLimiter` —
  no second implementation — one instance per rate-limited tool, keyed by
  tool name. The timeout is a `threading.Thread` + `.join()` bound on the
  **caller's wait**, not a preemptive kill: the same honest limitation
  `mcp.transport.StreamTransport.receive()` and `guard/sandbox.py`'s module
  docstring already document for an in-process deadline, cited by name in
  `server.py`'s comment rather than restated differently. Both a timeout and
  a rate-limit rejection return a normal errored `ToolResult`
  (`isError: true`), never an `RpcError` — the module's own stated rule that
  a tool failing is a result, not a protocol error, applied to a rejection
  the server itself issues.
- `engine/scripts/actions_pin_check.py` — **every `uses:` in every workflow
  pinned to a full commit SHA, never a version tag** (Phase 2: "pinned or
  controlled GitHub Actions"). A tag is the action's maintainer's to move; a
  SHA is not. Resolving each tag found `actions/attest-build-provenance`
  (at `@v2`, before it was bumped) used an *annotated* tag, where the bare
  tag's own SHA is the tag object, not the commit it points to — pinning to
  that would have shipped a `uses:` line that parses and does not resolve.
  **20 of 20** currently pinned, each with a `# vX.Y.Z` comment for the next
  version bump. **A pin does not verify its own currency** — `actions_pin_
  check.py` only proves a `uses:` line resolves to a real commit, never that
  the commit is recent. `astral-sh/setup-uv` sat at `v7.6.0` (2026-03-16)
  three major versions behind `v10.1.0`, found the same way `C-008` found
  `attest-build-provenance@v2` two majors stale: cloning the action's own
  public repository through this session's git proxy read lane and reading
  its tags, not trusting the pin's age to be visible from inside this
  repository. Recorded as **C-016** (`CONTRADICTED` via `E-016`) before
  bumping — the same order C-008 was handled in, evidence first, fix
  second. `v10.1.0`'s tag is lightweight (`git rev-parse` already gives the
  commit; `v7.6.0`'s was annotated and needed `^{commit}`), so which
  dereference a given tag needs is not something to assume from the last
  action checked.
- **CodeQL default setup is confirmed enabled** (`state/claims.jsonl` C-015,
  `SUPPORTED`) — not by reading the repository, which cannot see a GitHub
  *setting*, but by GitHub's own service refusing an advanced-setup workflow
  this session pushed and reverted: "CodeQL analyses from advanced
  configurations cannot be processed when the default setup is enabled." That
  refusal is the evidence — a live, one-time `network_probe` observation of a
  GitHub-side setting, the same shape as C-005's and C-008's `ci_run` findings,
  never a fact `state_map.py` can rederive from a checkout. The workflow itself
  was not kept: GitHub refuses to run both, so an advanced-setup file here
  could only ever be permanently red for zero analysis gained over what
  default setup already runs. Secret scanning has no such exception and stays
  the one genuinely unobservable control in gate 6.
- `oss/citegate/`'s release path + `engine/scripts/sbom_check.py` — **an SBOM
  generated in a CLEAN venv containing only the package, never the venv
  running the SBOM tool itself** (which would report the tool's own ~30
  transitive dependencies as the package's). `sbom_check.py` reads the
  generated file back and confirms it actually names the released package at
  the released version — generating a file nothing reads is the "signed
  artifact is not automatic production security" trap named directly in
  Phase 2.
- `corpus/universal-ai-os/DECISIONS.md` + `engine/scripts/node_dossier.py` —
  **all 507 nodes, each with the evidence a person needs to rule on it.**
  `nodes.json` has read `0 implemented, 0 rejected` since it was written — not
  neglect, but the cost of doing an investigation 507 times. Each row carries
  branch, lifecycle state, direct and chapter figure counts, figure ids, the
  candidate from `propose()` (**the same resolver**, never a second one), a
  recommendation and a confidence; the last three columns are the person's and a
  machine may never fill them. **134 nodes have a direct figure and only 116 read
  `EVIDENCE-BACKED`** — the other 18 already carry a proposal, so evidence and
  lifecycle are separate axes and the states are not collapsed. The 373 with no
  figure are listed **unranked**: scoring an absence of evidence would represent
  it as a quantity of evidence. `Idempotency` sits there with zero figures while
  `omnex.pipeline.IdempotencyStore` has been in the package for months.
- `engine/scripts/apply_decisions.py` — **the only thing allowed to set
  `verified`.** `0 implemented` is worth reading precisely because no machine can
  raise it, so this refuses five ways of pretending: a decision with no reviewer;
  a **machine-shaped reviewer** (`claude`, `bot`, `agent`, `system`… refused by
  name, and the message says how a person actually called that proceeds);
  `implemented` for an alias that does not import (through `core.symbols.resolve`,
  the one resolver); overturning somebody else's confirmation without `--revise`
  and a reason; a date that is malformed or in the future. Provenance goes in the
  node's existing `note` — **no schema change**, because two writers with
  different ideas of the shape is the drift this repository keeps paying for. A
  revision **keeps what it overturned** (`was: rejected by … on …`), or nothing
  would show that anybody disagreed. `deferred` records the look and confirms
  nothing: `claim` and `verified` are untouched, since collapsing "declined to
  rule" into "confirmed" inflates the only count that matters.
- `CONSTITUTION.md` — what holds regardless of phase: the authority hierarchy
  (**repository truth outranks every plan**), the lifecycle states that are never
  collapsed, the three layers of truth, *machine proposes / person confirms*, and
  **money changes priority, never reality**. Changes rarely; each change carries
  its reason in `docs/EXECUTION_DECISIONS.md`.
- `EXECUTION_CONTRACT.md` — how work is chosen and verified: autonomy levels and
  side-effect classes, promise integrity, evidence rules, the four adversaries,
  definition of done, the twelve maturity gates, and **what is currently blocked
  with a named resolution for each**.
- `execution_state.json` + `engine/scripts/state_map.py` — **where execution
  actually is, derived not typed.** `state_map.py --check` fails when the file
  and the repository disagree **in either direction**. Machine state is the most
  dangerous artifact here because it is the thing an agent reads *instead of
  looking*, and unlike prose it drifts authoritatively. **No timestamp**, on
  purpose: a generation time changes every run, so the file would differ from
  itself and the validator would have to learn to ignore a field — it is keyed on
  `source_commit` instead. Today: **1 gate PASS, 12 UNKNOWN, 0 FAIL**, and every
  UNKNOWN names the evidence it waits for, because `UNKNOWN` is a state and
  `false` is a claim. **Gates 0, 1, 2, 3, 5, 6, 9, 10, 11 and 12 derive their
  evidence from a real source; only 4, 7 and 8 state why they cannot — no
  integration, observability or evaluation evidence exists yet to read.**
  Gates 11 and 12 joined that list latest, and deliberately incompletely: a
  live listing or a revenue log now moves their evidence and prose, but never
  their `PASS`/`FAIL` verdict, which stays a person's call under §21 of the
  Sovereign Execution Standard. The undifferentiated version of that
  distinction was itself a defect for weeks: gates 1 and 2 carried the
  hard-coded strings "node_dossier.py does not exist" and
  "state/claims.jsonl does not exist", both scripts were then written and entered
  CI, and `--check` passed the whole time because it compared the committed file
  against those same literals — a constant validated against itself, in the file
  whose docstring warns about exactly this. `test_no_gate_claims_a_file_is_absent_
  while_it_sits_in_the_repository` is the structural fix, keyed on paths rather
  than on the two cases that already bit.
- `LICENSE` (`/`, `engine/`, `oss/citegate/`) — **Apache-2.0**, moved from MIT
  once the repository transferred to `Omnex-business-technologies`. Both
  `pyproject.toml` files originally declared `license = { text = "MIT" }` with
  **no licence file anywhere in the repository**, which is the same shape
  `build_pack.py` already refuses in a pack: a claim with no file behind it. No
  release was possible until that was fixed. `packs/LICENSE.txt` is unrelated —
  a commercial EULA for the image packs, never touched by this.
- `engine/scripts/extras_check.py` + `[tool.omnex.extras]` — **what
  `pip install omnex-engine[x]` actually delivers, measured per dependency.**
  Six of twelve extras had **zero** of their dependencies imported anywhere
  (`api`, `memory`, `worker`, `agents`, `evals`, `finetune`), and two docstrings
  named adapter modules that have never existed. Statuses:
  **2 supported · 3 partial · 6 unsupported · 1 tooling**. Per dependency, not
  per extra — `vectors` imports qdrant-client and not sqlite-vec or numpy, so
  "backed" hides two unused pins and "unbacked" erases a real adapter.
  Decisions live in `docs/EXECUTION_DECISIONS.md`.
- `engine/scripts/release_check.py` + `.github/workflows/release.yml` — **what
  refuses a package before a stranger installs it.** Three modes: the default is
  drift (declarations against the code and against CI), `--release` is the
  operator before tagging, and `--tag` is the workflow the tag triggered — there
  the tag necessarily exists, so "is this name free" inverts into "does it name
  this version". It found citegate declaring `requires-python = ">=3.10"` while
  importing `enum.StrEnum` (3.11: pip resolves, installs, first import raises),
  and citegate's **sixteen tests never running in CI**. Then running it on the
  *second* target found four bugs in itself — the worst being that the check for
  suites CI does not run could not see the suite CI does run, and was right about
  citegate by coincidence of that same bug. **Both targets are in the gate now,
  never one.** Its import scanner is its own, via `ast`: `extras_check` asks
  *declared → imported* where a prose false positive is never looked up, this
  asks *imported → declared* and reads the answer as truth. That asymmetry is
  what found `tiktoken` imported by `omnex.llm.tokens` and declared by nothing.
  The release workflow attests provenance with `actions/attest-build-provenance`
  — verifiable by `gh attestation verify`, not a file we write about ourselves —
  and PyPI publish sits behind a `pypi` environment needing both the operator's
  token and their approval. **It has now run** — `workflow_dispatch` was added so
  the first execution would not have to be the real one, and run `34237298583`
  took the gate, the build, `twine check` and the attestation green while
  `github_release` and `pypi` were skipped by their `event_name` guard. Zero
  releases and zero tags existed afterwards, which is the property that made the
  rehearsal worth running: `actions/attest-build-provenance@v2` was the one line
  in that file that could not be read against `docs.github.com` from here — but
  the action's own repository is public, and this session's git proxy serves
  anonymous reads of public GitHub repos directly, the same lane `add_repo` uses.
  That read found `@v2` two majors stale (last released 2025-06-11; `v4.2.2` is
  current), still functional but never "current" — `C-008` is `CONTRADICTED`,
  not `SUPPORTED`, and the pin is now `@v4`. **A blocked doc host is not a
  blocked repository**: the two lanes answer differently, and reading the second
  is what turned "could not be checked" into "checked, and wrong." The
  **publish** half is untouched by any of this and is `C-013`, still UNKNOWN.
- `state/` + `engine/scripts/claims.py` · `policy.py` · `next_action.py` ·
  `runs.py` — **the execution spine: what is asserted, what backs it, what may
  act on it, and how a fresh session continues.** `claims.jsonl` and
  `evidence.jsonl` are separate on purpose — evidence is a first-class entity
  with a method, a version, an environment and an expiry, and **negative
  evidence is first-class too**. A claim's **status is derived, never stored**:
  a stored status is a typeable one, and that is the single thing that must not
  be typeable. Eight states, never collapsed — `CONTRADICTED` and `STALE` are
  the two most systems lack and the two that matter. **A claim is not SUPPORTED
  because evidence exists**: `VERIFIES` maps each claim type to the methods that
  can settle it, so `person` cannot settle whether a symbol imports. Contradiction
  is **superseded, never deleted** — `E-004`, "citegate's tests never ran in CI",
  is still on file under `E-005`. Absence is `UNKNOWN`, and **being unable to
  check is not evidence against**: the Etsy shape is `C-012` CONTRADICTED
  (measured: 403 at the proxy) while whether the API would accept the request is
  `C-009` UNKNOWN. `policy.py` maps eleven side-effect classes to autonomy
  levels; `PUBLISH`, `DEPLOY`, `CREDENTIAL`, `FINANCIAL` and `DESTRUCTIVE` are
  cleared by **no level alone**, even L5. **Money changes priority, never
  reality** — `economic_weight` reaches `order()` and nothing else, and two tests
  hold that line. `next_action.py` derives the queue from the registry rather
  than a maintained list, so a claim that becomes SUPPORTED leaves it without
  anybody crossing it off; its score is printed **as a heuristic** and the policy
  check runs after it and can refuse the top-ranked item. `runs.py` is the
  hash-chained, append-only ledger plus checkpoint and recovery: `--recover`
  answers WHERE WE ARE · WHAT IS TRUE · WHAT IS UNKNOWN · WHAT WAS DONE · WHAT
  FAILED · WHAT IS BLOCKED · WHAT NEXT from the repository, with no
  conversational memory. The chain is tamper-**evident**, not tamper-proof, and
  says so. Every run carries `expected_outcome` from the start because an
  expectation recorded after the result is a description, not a prediction.
- `docs/TRANSFER.md` — **the runbook for moving this repo into an organization.**
  Written, then performed: `omnex-factory` now lives at
  `Omnex-business-technologies/omnex-factory`, moved from the personal account
  `RaveZona`, with the old path redirecting (confirmed on both the API and the
  git protocol, not assumed). Steps 1–4 were the operator's alone, by design —
  every one is `CREDENTIAL`- or `DESTRUCTIVE`-class under `policy.py`, cleared
  by no autonomy level. Step 5 (repointing `oss/citegate/pyproject.toml`'s
  `[project.urls]` at the new path) and this file's own references are done.
  **What this session cannot do itself is widen to the new owner mid-session**:
  `add_repo` refused a cross-owner add outright ("cross-tier adds are not
  supported"), so a session that started on `ravezona/*` stays scoped there —
  only a fresh session sourced from the new path gets full tool access
  (PR creation, CI checks) under the new org; git-level push through the old
  remote URL keeps working via the redirect in the meantime. Step 6 (a ruleset
  requiring status checks on `master`) is still open — the one that pays
  immediately, since nothing today stops a red-CI merge.
- `docs/EXECUTION_DECISIONS.md` — why something was built, what evidence forced
  it, what else was considered, whether it can be undone. `D-001` records the
  finding that a detailed execution report described fifteen artifacts of which
  **none existed** — the whole exchange had run in plan mode.
- `packs/publish.py` — **the last step before money: the request that creates a
  listing.** It builds the request and, by default, does not send it. No
  endpoint is written into this repository — the storefront API shapes were not
  readable from the environment this was developed in, so `--send` requires
  `OMNEX_LEMONSQUEEZY_URL` / `OMNEX_ETSY_URL` from the operator and refuses by
  name without one. Five refusals, all reported **at once**: a pack that does not
  cover its listing, no built archive, no price, an unconfigured credential, and
  `--send` with no endpoint. A sixth guard is the `live` flag: publishing an
  offer whose flag is still false needs `--force-draft`, because going live is a
  person's decision and it is the one that starts `registry.ts`'s clock. Header
  **names** travel in the request, never values, so `--dry-run` output cannot
  leak a key. Price crosses as integer cents via `Decimal` — `float("19.99")*100`
  is `1998.9999999999998`, and rounding rescues it rather than the type doing so.
- `deploy/env.json` + `engine/scripts/env_check.py` — **which of the 28
  environment variables a deploy cannot run without, and why.** Almost all of
  them **fail closed**: `cron-auth` returns false when `CRON_SECRET` is unset,
  `isOwner` refuses below 16 characters, every Stripe route answers 503. Correct
  direction, invisible failure — the site is up, the pages render, the feature is
  never reachable. **7 required, 11 secret**, plus one `any_of` group ("an image
  model"), because no single provider key can be required and Studio with none of
  them is live, billable and unable to produce anything. Two modes: the default
  compares the manifest with every `process.env` in the code **in both
  directions** and never reads the environment (CI's mode, or it would be
  permanently red); `--runtime` is the operator's, on the host about to serve.
  **No value is ever printed** — a preflight that prints a key to a build log has
  copied the secret, not checked it. The n8n side is *derived* from
  `n8n_bindings.json` and deliberately not listed here.
- `app/api/healthz/` + `app/api/readyz/` + `lib/core/health/manifest.ts` —
  **`env_check.py --runtime`'s question, asked over HTTP** (Sovereign
  Execution Standard, Phase 4: health and readiness checks). `/api/healthz`
  is liveness only — 200 the instant the process can answer at all, no
  dependency checked — kept separate from `/api/readyz` so a missing Stripe
  key produces a visible 503 rather than a restart-policy crash loop.
  `/api/readyz` reads the same `deploy/env.json` manifest and reports which
  required variables are unset and which `any_of` group has no member set —
  **names only, never values**, the same rule `env_check.py` already
  enforces at CI time, now enforced at request time too.
- `lib/__tests__/copilot-stream.integration.test.ts` — **the copilot route,
  wired end to end** (Sovereign Execution Standard, Phase 5: AUTH → REQUEST
  → VALIDATION → BILLING/CREDIT → PROVIDER → PERSISTENCE → EVENT →
  RESPONSE, as one exercised path). Six other suites each proved one piece
  of `/api/copilot/stream` correct alone — guardrails, metering, budget,
  the SSE stream, the trace, the real-Postgres credit ledger — and none of
  them had ever been proven to agree about what the route does when wired
  together. Only the genuinely external systems are faked (Supabase, the
  LLM provider); rate limiting, guardrails, budget, metering and SSE
  assembly all run as real production code. Proven not vacuous by sabotage:
  commenting out the route's `spendCredits` call was confirmed to fail the
  test before the fix was confirmed to pass it.
- `lib/core/agents/guardrails.ts` — **`guardInbound`'s injection rules exist
  for text an agent FETCHED, not for a user talking to their own copilot.**
  The copilot route ran the user's own chat message through them anyway.
  Checked against seven realistic questions, six were hard-blocked with a
  400 — "act as a career coach", "from now on reply in French", "show your
  instructions for X" are ordinary ways to prompt an assistant, not attacks,
  and there is no trust boundary crossed when the user instructs their own
  copilot (they are the principal, not a confused deputy). New `redactSecrets()`
  is the one half of `guardInbound` that still belongs on a user's own words —
  a real credential pasted into a question should not reach a third-party LLM
  provider — and the route now uses it, never blocking, always redacting.
  Proven by sabotage: `copilot-stream.integration.test.ts`'s new test
  confirmed to fail with the old `guardInbound`-based block, then pass with
  the fix.
- `app/api/studio/upload/route.ts` — **`file.type` is a label the client
  wrote on its own multipart request, not a fact about the bytes that
  follow it.** Trivial to set to `image/jpeg` on arbitrary content with a
  raw `fetch`/`curl`, no browser file picker involved — and it was the sole
  gate on both extension selection and image-type validation before writing
  to the `products` bucket, which this route's own docstring already calls
  public, and handing back a public URL on this product's own domain.
  OWASP's own name for this class is Unrestricted File Upload. New exported
  `matchesSignature(mimeType, bytes)` checks the real JPEG/PNG/WebP magic
  bytes against what was actually uploaded and refuses with 415 before
  anything reaches storage; `file.type` still selects which signature to
  check and the stored extension, but no longer stands in for the content
  it claims to describe. This route had zero test coverage before
  `lib/__tests__/upload.test.ts`. Proven by sabotage: removing the
  `matchesSignature` call was confirmed to let an HTML payload labelled
  `image/jpeg` through with a 200 and a real `upload()` call, before the
  check was restored and reconfirmed to refuse it with 415.
- `app/api/stripe/webhook/route.ts` + `supabase/migrations/003_webhook_retry.
  sql` — **idempotency that survives a failed first attempt.** Migration 001's
  gate inserted the event id and treated any primary-key conflict as "already
  handled" — correct for a genuine duplicate delivery, wrong for Stripe's own
  retry of an event whose first attempt claimed the row and then failed (a
  transient DB error, a timeout): the retry hit the same conflict and was
  silently swallowed, so a customer who paid could never receive credits and
  Stripe stopped retrying because the handler answered 200. `claim_webhook_
  event()` returns three outcomes instead of one boolean — `new`, `retry` (a
  prior attempt at this exact event failed) or `duplicate` — with the
  three-way decision made inside one PL/pgSQL function so the atomicity is a
  database property, the same reasoning `consume_credits`' row lock already
  uses. Verified against a real local PostgreSQL 16 (this sandbox has no
  Docker daemon, so the committed `credits.db.test.ts` suite — which spins up
  its own container — could not run here): reproduced the original bug
  directly (a failed-and-retried event id reads as an existing row regardless
  of outcome), confirmed the fix resolves it, and fired 5 truly concurrent
  `psql` processes at one failed event to confirm exactly 1 wins the retry
  and 4 read `duplicate` — the property a mock cannot prove.
- `lib/core/security/ratelimit.ts` — **keyed by the verified user, never by a
  header alone, whenever one is available.** Every route this repository
  wires to `checkRateLimit` (`studio_generate`, `studio_upload`,
  `copilot_stream`, `stripe_checkout`) already authenticates the caller with
  Supabase before checking the limit, but the check itself keyed purely on
  `x-forwarded-for` / `x-real-ip` — headers the calling client sets on its
  own request. An authenticated attacker who cannot forge a session can
  trivially forge a header, so every one of those four limits was bypassable
  by rotating a fresh spoofed IP on each call. `checkRateLimit` now takes an
  optional `identity` that outranks the header entirely when passed; all four
  call sites pass `user.id`. No test file existed for this module at all
  before this round. Proven by sabotage: `lib/__tests__/ratelimit.test.ts`'s
  bypass test — same user, a brand-new IP on every call — was confirmed to
  fail against the header-only code before the fix was confirmed to pass it.
  Deliberately does not claim `x-forwarded-for` is trustworthy on any
  particular deployment platform (Vercel's edge or otherwise) for the two
  configured limits (`email_send`, `auth`) nothing in this repository calls
  yet — that claim is unverifiable from here and stays the header's fallback
  behaviour, not something this fix asserts. **A second bypass sat right next
  to the first**: any request carrying a valid `CRON_SECRET` bearer token
  exempted itself from every limit at once, inherited from the same donor
  codebase `RATE_LIMITS`' own comment already names — but this repository has
  no `app/api/cron/*` route and no `vercel.json` `crons` entry, so nothing
  legitimate ever sends that header to a customer-facing route. Its only live
  effect was downside: a leaked `CRON_SECRET` would have handed an attacker
  unlimited calls to every one of these routes, undoing the identity-keying
  fix in the same breath. Removed outright rather than kept "just in case" —
  a bypass with no legitimate caller and a real leak scenario is pure
  liability. `stripe_portal` also gained the rate limit `stripe_checkout`
  already had; nothing had documented why the sibling route lacked one.
- `engine/ontology/n8n_bindings.json` + `engine/scripts/n8n_bindings_check.py` —
  **what an n8n node actually is, as data a person confirms.** Branch XI's
  `missing` field named the gap in words: without endpoint, method and credential
  per tool, an emitted workflow imports as a wiring diagram. The emitter now
  binds from this catalogue and leaves `noOp` only where nothing is bound.
  Nothing in it is inferred — the open web is refused at this environment's
  proxy, so the Etsy and Lemon Squeezy shapes could not be read, and those two
  bindings carry the knowable parts (node type, method, credential name) with the
  url deliberately absent and a note saying why. `confirmed` means **a person
  imported it and n8n accepted it**; setting it needs `confirmed_by` and
  `confirmed_at`, exactly as `nodes.json` requires for symbol resolution.
  Currently **7 bindings, 0 confirmed · 4 node types, 0 confirmed** — the one
  figure here a script cannot flatter. `emit(..., require_confirmed=True)` is
  what a deploy path uses; building and reading by hand does not need it.
  A binding whose `source` is `this repository` names a command the checker
  **resolves** — module, `__main__`, subcommand, or a real `.py` path — because
  the first version of this catalogue named two modules that did not exist.
  **The checker itself had no test and did not run in CI** until this round —
  the resolution logic that caught that original defect was, for the whole
  time since, invisible to `test_ci_runs_every_gate_script_the_document_names`
  because it was never named in this gate block either. `test_n8n_bindings_
  check.py` now exercises `unresolved_commands()` and `required_env()` against
  synthetic catalogues, plus one test holding the real committed catalogue to
  the same standard.
- `engine/scripts/eval_gate.py` — the same shape of gap found one script over:
  added to this gate block and CI in the *previous* round (D-032) with
  `omnex.evals`'s own logic (`Gate.decide`, `EvalRunner`, `Trend`) already
  covered by `test_evals.py`, but the CLI script's own `main()` — argument
  parsing, the exit code, `--record` — had never been exercised directly.
  `test_eval_gate.py` runs the real committed suite through `main()`: a first
  run with no baseline passes and writes nothing, `--record` writes one a
  later deterministic run reads back clean, and a **sabotage-verified**
  regression test edits one recorded result to claim a case passed that the
  real run still fails, confirming `main()` returns `1` and names the
  regressed case — not just that `Gate.decide()` can compute one in isolation.
- `engine/src/omnex/pipeline/__main__.py` — the CLI an n8n `executeCommand` node
  runs: `verify` (signature, replay window, sender id; body on stdin) and `claim`
  (deliver once). **Exit codes are the interface**: `0` proceed, `1` refused,
  `3` already delivered. `3` is separate because a redelivery is the normal case,
  and collapsing it into the failure code teaches whoever watches the workflow to
  ignore failures. The secret is read from `OMNEX_WEBHOOK_SECRET` and there is no
  `--secret` flag — argv is visible in `ps` and n8n writes the command it ran
  into its own execution log.
- `engine/src/omnex/pipeline/claim.py` — `Claims`, a directory with one file per
  event id, taken with `os.open(O_CREAT|O_EXCL)`. `IdempotencyStore` is a dict
  and is correct for a worker that stays up; an n8n node runs a command and the
  process exits, so a dict there starts empty on every redelivery and
  deduplicates nothing. Boundary stated in the module: one filesystem, and a
  claim is written **before** the work, so a crash leaves an event claimed and
  undelivered — the other direction charges the customer twice.
- `packs/listing.json` + `packs/listing_check.py` — **what a listing promises,
  as data, against what QC passed.** `GIG.md` sells the €49 Complete Vault as
  "170+ images"; the four QC manifests total **80**. Nothing connected the copy
  to the goods, so the only thing between that page and a live Etsy listing was
  somebody remembering. The check reads manifests rather than directories
  because `.gitignore` admits exactly one file back out of `packs/*/`
  (`!packs/*/manifest.json`) — the images live on the machine that made them.
  A bundle is measured against its members' **real** counts: the Vault promises
  170 and its packs promise 50+40+40+40 = 170, so promise-versus-promise agrees
  with itself while every pack is short.
- `BUSINESS.md` + `engine/scripts/business_map.py` — **the same mechanism as
  `INVARIANTS.md`, one level out.** Every figure derived: days since the first
  commit in THIS repository (a repo cannot see the work before it, and a number
  that quietly counts something else is worse than none), goods against the
  promise, what is live, and the ask log. **A missing revenue log renders as "0
  recorded, which is not 0 earned" — never €0.00.** It reads the repository and
  cannot see Stripe, Supabase, Etsy or Lemon Squeezy, and says so in its own
  last section; printing an unobservable as zero is the mistake `3766976`
  already paid for. Today: **day 45, 208 commits, 80 of 170 images through QC,
  0 listings live, 1 module enabled, no revenue log.** `--check` (D-036, this
  round) closes the one gap the other four derived-and-committed documents
  never had: nothing regenerated or diffed it, and it had drifted 11 commits
  stale with nothing reporting so. A raw `git diff --exit-code` would be
  permanently red the day after every regeneration — `_elapsed()`'s headline
  depends on `datetime.now(UTC)`, not just the checked-out commit — so
  `--check` masks that one line before comparing (the same "drop the
  volatile field" move `state_map.py`'s `differences()` already makes for
  `source_commit`) and still fails on a real disagreement in the goods,
  live, or revenue figures.
- `packs/build_pack.py` — QC-passed images → a file Etsy can deliver. Four
  ratios **cropped from the centre, never padded**: a background scene with bars
  is not publishable, so losing edge pixels is the correct loss here. The zip is
  **deterministic** (fixed timestamps, sorted entries) so "is the file I uploaded
  the file I built" is a hash rather than trust. Two refusal layers, and the
  split is the point: CI can only compare the promise against the manifest,
  while this — on the machine holding the files — also catches a manifest entry
  with no image behind it. Pillow is imported inside the function, so the
  assembly logic where every refusal lives is testable without it.
- `engine/scripts/mutate.py` — **the honest answer to "how many bugs".** There
  is no integer for that. There is a measurable one for *how much of this is
  actually held by its tests*: twenty-nine hand-written mutations against rules the
  repo has already paid for, each naming the test that must go red. Currently
  **29 of 29 killed**. On its first run it was 11 — the survivor showed that
  `Run.margin` and `_summarise`'s total were independent paths that happened to
  agree, so changing one moved the median, p10 and worst while the total and the
  verdict stayed put. No dependency, no coverage threshold: a coverage gate
  invites padding, which is the Goodhart the whole `harness` is built against.
  **`main()` now writes `ontology/mutation_probe.json`** — committed, survivors
  included — because `state_map.py`'s gate 3 used to say "the mutation probe
  kills every mutation" as a literal string in its own source, true the day it
  was typed and never re-checked again, the exact shape gates 1 and 2 already
  carried once ("node_dossier.py does not exist," hard-coded, for weeks after
  the script existed). `git diff --exit-code ontology/mutation_probe.json`
  guards its freshness the same way `node_dossier.py`'s output is guarded, and
  `state_map.py` compares the file's `total` against the live `CATALOGUE`
  length so a mutation added with nobody re-running the probe shows up as
  stale rather than silently undercounted.
- `engine/ontology/nodes.json` — all **507 nodes** against exported symbols.
  Three claims: `gap` (no candidate), `proposed` (an alias that imports,
  unconfirmed), `implemented` (**a person agreed**). A machine proposes and
  verifies resolution; it may never decide two names mean the same
  capability. Four claims, not three: `rejected` (a human said no) exists
  because the first `refresh()` after `omnex.mcp` landed proposed `Code →
  omnex.mcp.ErrorCode`, which is wrong — and with nowhere to record that, the
  same wrong proposal returns on every run and the queue can only grow.
  `refresh()` may propose for a gap; `prune()` withdraws proposals the current
  rule would no longer make; neither may touch anything a human verified.
  **Containment runs one way**: a symbol more specific than the node can be its
  implementation (`MCP` → `McpClient`), one broader cannot — `omnex.factory.Tool`
  was proposed for fourteen different "Tool X" nodes at once before that rule
  landed. Pruning that noise raised the gap count from 447 to 464, which is the
  honest direction. Currently **461 gap · 46 proposed · 0 rejected · 0
  implemented**.
- `corpus/universal-ai-os/BUILD_ORDER.md` — the join, from
  `scripts/build_order.py`: every node with no code, ranked by how many figures
  name it. **Only direct lexical edges sort it.** Chapter-affinity edges
  outnumber them 736 to 550, so ranking on the total ranks on chapter size —
  ReAct (6 direct, 63 chapter) would beat Vector Search (22, 21). And `gap`
  means *no alias was proposed*, never *the capability is absent*: `Vector
  Search` is a gap while `omnex.vectors.HybridStore` is in the package, so a
  node whose branch already exports symbols gets `alias?` (go read that code
  first), and only a branch exporting nothing gets `build`. **The queue moves as
  code lands**: MCP led it at 62 figures until `omnex.mcp` was built, at which
  point branch XII began exporting, the node became `proposed`, and every other
  XII node went from `build` to `alias?`. `test_the_queue_moved_when_the_node_at_
  its_head_was_built` is the record of that; the head is no longer pinned by
  name, because pinning it is what made the first version brittle.
- `corpus/universal-ai-os/` — 509 figures from *AI Engineering* (Pachaar &
  Chawla), the committed source export beside them, and `RECONCILIATION.md`
  joining corpus weight against `engine/` coverage. `scripts/ingest_atlas.py`
  parses it and **asserts the export's own totals** — a regex matching 400 of
  509 writes a smaller manifest and raises nothing. The n/10 scores in that
  export are deliberately not imported: its author scored its own nodes.
- `engine/src/omnex/factory/` — a set of capabilities compiled into an
  `AgentSpec`: role, capabilities bound to symbols that must import, priced
  tools, memory and context policy, paradigm, eval suite, governance, failure
  modes, cost model. The spec is fingerprinted and derives a `harness.Contract`,
  so one rescoped after approval fails the next gate. `Stage` makes the gate
  order a type — `idea → market → unit economics → architecture → simulation →
  evaluation → security → deploy → observe → scale/kill` — and
  `Pipeline.advance()` refuses anything out of order. Only three gates can be
  decided from the spec (idea, unit economics, architecture); the rest take
  evidence a person supplies, because a spec must not grade its own market.
  **`Stage` is the `StrEnum` trap in the flesh**: inherited string comparison
  makes `Stage.DEPLOY < Stage.IDEA` true, and `@total_ordering` fills in nothing
  because all four operators are already inherited. They are written out.
- `engine/src/omnex/factory/compile/` — one neutral `Blueprint` (topology, never
  implementation) and three emitters: a runnable `graph.Graph`, an MCP server
  manifest, an n8n workflow JSON. **The property that makes them compilers is
  `parse(emit(bp)) == bp`**, checked across every target × paradigm, and
  `test_the_round_trip_check_can_actually_fail` breaks an emitter on purpose so
  the other fifteen are not comparing an artifact with itself. That matrix found
  a real bug: n8n read tool prices off tool *nodes*, so four of five paradigms
  lost every price and the workflow still imported. Prices now travel in `meta`.
  An n8n node is `noOp` and says **in its own `notes` field** that it is a
  placeholder whenever nothing in `n8n_bindings.json` binds its ref — a spec
  names a tool and its price, never the endpoint, credential or payload, and
  inventing those ships configuration nobody supplied. A bound node carries the
  real type and parameters and says in the same field whether anybody has
  imported it. **The omnex keys are merged last on purpose**: a hand-written
  parameter template that shadowed `omnexRef` would round-trip as a different
  topology while the workflow still imported, which is the one way the round-trip
  property could be defeated from the data side (`a_binding_may_shadow_the_
  reference` in `mutate.py`).
- `engine/src/omnex/factory/economics.py` — margin per run, per agent, per
  customer, in exact picos. **Acquisition is not a per-run cost**: charging it
  that way makes a customer look worse the more they use the product, so it is
  answered by `payback_runs()` instead. A failed run is costed and counted, or
  the cheapest agent is one that fails everything. Margin is reported as a
  distribution — `worst()` is the number that says "cap the loop", the mean is
  the number that says everything is fine. `is_losing_money()` is **three-valued**
  and answers `None` below `MINIMUM_RUNS`, like `router.break_even()`.
  `cost_drift()` compares what the gate approved (an estimate) against what
  happened (a measurement) — the `metering.ts` `estimated: boolean` rule again.
- `engine/src/omnex/factory/portfolio.py` — live agents as assets with one
  explicit decision each. **`recommend()` proposes, `enact()` records a person's
  name** — the node map's rule at the level where it costs most, because `KILL`
  is irreversible and is what an optimiser under cost pressure reaches for
  first. Three refusals: too few runs is `WATCH`; nothing is killed on a
  dimension nobody measured (`None` means unmeasured, never zero); `MERGE` comes
  from overlap across the portfolio. `report()` opens with **`n=1. This is not a
  portfolio yet`** whenever there are fewer than two assets.
- `engine/src/omnex/factory/feedback.py` — runs, compiler results and portfolio
  decisions become one stream `harness.meta.diagnose()` reads, and an accepted
  improvement writes back a node claim. **That claim is always `proposed` and
  there is no parameter that makes it `implemented`** — the thing producing the
  evidence does not grade it. A zero-cost observation is refused: cost per
  accepted change falls toward zero the more of them a loop emits, and that is
  the one number the outer loop cannot afford to have gamed.
  `test_the_chain_runs_from_spec_to_an_observation_the_outer_loop_accepts` walks
  the whole thing in one pass, so a decorative link fails.
- `skills/` — five packaged skills, each carrying its measured number
- `intel/` — committed scan snapshots and reports
- `oss/citegate/` — standalone, dependency-free citation checker
- `packs/` — image-generation job packs (separate concern from `engine/`)

## Conventions that are already decided

- Docstrings explain **why**, and name the failure the code prevents. Match the
  surrounding density rather than adding a house style.
- Refusals name every failing condition at once, not the first — being refused
  repeatedly is how somebody concludes the check is the obstacle.
- Prefer a structural fix to a tuned threshold. `Fleet.assign()` refuses
  overlapping workspaces rather than trusting workers to take turns.
- New measured claims go in `skill_numbers.py` first, then get quoted.

## Lab notes — mistakes already paid for, do not repeat

- `ruff check` passing does not mean `ruff format --check` passes. Run both.
- **`ruff check --select RULE --fix` narrows the enabled rule set to RULE, so
  every `# noqa` for a rule *not* in the selection reads as unused and is
  stripped.** Run to delete three stale `S603`/`PLC0415` directives, it removed
  **21** — including every legitimate `E402` and `F401` in the suite — and the
  damage looks like a tidy-up in the diff. `git checkout` on the files that had
  no other changes was the recovery. Fix a specific rule by hand, or run
  `--fix` with the project's own configuration and no `--select`.
- **This file hand-quotes figures that scripts derive, and they drift.** Four
  were stale when PR #1 was prepared for landing: `day 37, 80 commits` (measured:
  day 41, 94), `19 of 19 killed` (27), `464 gap · 43 proposed` (461 · 46). Each
  is produced by a script — `business_map.py`, `mutate.py`, `node_map` — and
  copied here by hand, which is the drift this repository builds gates against,
  in the document that describes those gates. **Re-measure before quoting**, and
  treat a figure in this file as a claim with a date rather than a fact. A
  checker comparing quoted figures against their scripts is the obvious fix and
  is not built: it needs the figures tagged first, and an untagged regex over
  prose fails in the direction of passing.
- **A package with no lint config is not "passing lint", it is unlinted.**
  `oss/citegate` had no `[tool.ruff]` and there is no config at the repository
  root either, so ruff fell back to its defaults (line-length 88, a narrower
  rule set) while the code was written under the engine's 100. Nothing noticed
  because nothing had ever linted it — the same `working-directory: engine`
  inheritance that hid the tests. The first CI run of the new job found an
  unused `import pytest` and two files needing reformatting. citegate now
  carries its own config, deliberately identical to the engine's so the twin
  splitters stay readable side by side.
- **A tag-only workflow is not continuous integration.** `release.yml` runs the
  whole suite, and only when somebody pushes a tag; counting it would let "CI
  runs this package's tests" pass while no push and no pull request ran
  anything. `covers_changes()` requires a `pull_request:` or a `push:` with
  `branches:` before a job counts.
- **A workflow reader that does not strip comments reads prose as configuration,
  and fails toward passing.** `covers_changes()` and `jobs()` are substring scans
  over raw YAML. Adding `workflow_dispatch` to `release.yml` meant writing a
  comment saying it deliberately has *no* `branches:` — and that comment contains
  the string `branches:`, which flipped a tag-only release gate into counting as
  continuous integration. Nothing downstream would have said so: it makes
  `test_every_pytest_suite_in_the_repository_runs_in_ci` pass more easily, not
  less. The same blindness is live one level over — `engine.yml`'s citegate job
  explains itself with a comment containing the word `pytest`, so a job that only
  *discussed* running a suite would have satisfied every caller grepping its
  block for one. Both readers now go through `_uncommented()`, which respects
  quotes so `- "citegate-v*"` survives. Found by writing a comment, not by
  reading the code.
- **A workflow's `paths:` filter is part of its gate.** `engine.yml` triggered on
  `engine/**` only, while the engine suite reads `packs/`, `lib/`, `app/`,
  `components/`, `oss/`, `corpus/`, `CLAUDE.md` and the workflows themselves. A
  change to any of those could not turn the job red, so the gate was green by not
  running. Widened, and the filter now names each reason. Found again later, the
  same shape: a commit that only touched `state/evidence.jsonl` and
  `state/runs.jsonl` (recording `D-012`'s findings) would not have triggered
  `engine.yml` either, and `test_the_committed_registry_is_well_formed`,
  `test_the_committed_ledger_is_intact` and three siblings read exactly those
  files with no path argument. `state/**` and `execution_state.json` are in the
  filter now. The lesson generalises past this one list: a `paths:` filter is a
  claim about what a test suite reads, and it drifts the same way any other
  unchecked claim does — one committed-file test added, one filter entry not.
- **`test_ci_contract` compared ruff's directories and nothing else.** A whole
  script added to CLAUDE.md's gate block and not to CI passed it untouched —
  which is the same drift it was built for, one level up.
  `test_ci_runs_every_gate_script_the_document_names` closes that half.
- **A catalogue entry is prose until something resolves it.** The first version
  of `n8n_bindings.json` shipped naming `python -m omnex.pipeline.verify_webhook`
  and `...seen_before`. Neither was a module. It passed every check written for
  it — the schema was valid, no secret was in it, the node type existed — because
  every one of those checks was about the entry's *shape*. An unresolvable
  command is worse than an unbound ref: the workflow imports, the node is not
  marked a placeholder, and nothing says otherwise until the first real order.
  `unresolved_commands()` now resolves every command claiming to be ours, and
  `test_a_command_naming_a_module_that_does_not_exist_is_caught` reproduces the
  exact three shapes that shipped.
- **A concurrency test written the obvious way passes without the lock.** At
  CPython's default 5ms switch interval, eight threads rarely interleave inside
  a short critical section, so the first version of `test_concurrency.py` was
  green against an unguarded `CostLedger` and proved nothing.
  `sys.setswitchinterval(1e-9)` plus 16×400 makes it unmistakable: the unlocked
  ledger reports **the right event count and half the money** ($0.29 of $0.64).
  The GIL narrows this window; it does not close it, and free-threaded CPython
  removes it.
- **Twins can diverge in their DATA while their code stays identical.** The two
  splitters were line-for-line equivalent and the engine's `_ABBREVIATIONS` had
  quietly grown by `dr.`/`mr.`/`ms.`, so citegate split "Mr. Lee and Ms. Park
  disagreed." into four fragments. Comparing the functions found nothing; only
  `test_citegate_parity.py`, running both over one corpus, did.
- **Symbol resolution lives in `omnex.core.symbols`, imported by everything.**
  `ontology_map.py`, `node_map.py` and `omnex.factory` all ask "does this name
  exist"; the splitter lesson below is what a second copy costs.
- A citation like `[url · 2026-08-05]` parses as the asserted figure "2026"
  unless citations are stripped *before* number extraction.
- Masking citations before sentence-splitting is required, **and** the restore
  must substitute only the placeholders a sentence contains — walking the whole
  citation list per sentence is O(n²) and cost 4.5s on a 4,000-sentence filing
  (fixed in `d8d3ca5`, guarded by a growth-ratio test).
- **That splitter exists twice.** `engine/src/omnex/rag/ingest.py` and
  `oss/citegate/src/citegate/grounding.py` are independent copies, on purpose —
  citegate ships dependency-free. The quadratic was fixed in the engine and
  survived in citegate for a further commit. Fix a splitter bug in both, or
  check the other before claiming it is fixed.
- **A benchmark whose shape cannot express a bug reports good numbers straight
  through it.** `bench.py` measured 5,000 answers of four sentences each, where
  the quadratic term is nothing, and published 46,279 sentences/sec while the
  same code did 1,439/sec on one long document. It now measures both shapes.
- A thin artifact (a 50-char PyPI summary) is not evidence of absence. The gap
  matrix excludes corpora under 200 chars and names them, because "nobody does
  model_routing" was nearly published about litellm, which *is* a router.
- The shell's cwd persists between calls and is often already `engine/`.
  `cd engine` then fails. Use absolute paths or check first.
- **The open web is not reachable — only an allowlist is.** Measured: PyPI, npm,
  crates.io, GitLab and Docker Hub answer, and GitHub arrives through the git
  lane (`add_repo`, then clone). Everything else — `example.com`,
  `wikipedia.org`, `vercel.com`, `lovable.app`, `drive.google.com` — gets
  `gateway answered 403 to CONNECT` and never opens a socket. The previous
  version of this note named four blocked hosts and what answers, which reads as
  "the rest is fine"; that omission cost a session, with three clients
  (WebFetch, curl, Chromium through the proxy) each refused identically before
  anyone thought to test `wikipedia.org` as a control. **Read
  `curl -sS "$HTTPS_PROXY/__agentproxy/status"` → `recentRelayFailures` before
  trying any host not on the list** — the proxy logs its own refusals, so one
  read replaces a round of guessing. A 403 there is an org policy decision:
  report it, never route around it. Content from a blocked host arrives by `@`
  upload or through a GitHub repo, and the network policy itself is the user's
  to widen at environment level.
- **`docs.github.com` being 403 does not mean a GitHub Action's version is
  unreadable.** `release.yml` shipped a comment saying `actions/attest-build-
  provenance@v2`'s currency "could not be checked against GitHub's own
  documentation from the environment it was written in" — true, and also not
  the only way to check. The action's own repository is public, and this
  session's git proxy serves anonymous clones of public GitHub repos directly —
  the same lane `add_repo` uses for read access. Cloning it and reading tags
  found `@v2` two majors stale (last released 2025-06-11; `v4.2.2` is current).
  The doc host and the git lane are different paths through the same proxy and
  answer differently; a 403 on one is not evidence about the other. Bumped to
  `@v4` once the read confirmed `subject-path` still worked unchanged.
- **A brand-new workflow file cannot be `workflow_dispatch`'d before it reaches
  the default branch — a new trigger on an already-registered workflow can.**
  `release.yml` already existed on master when `workflow_dispatch` was added to
  it on a feature branch, and dispatching from that branch worked (run
  `34237298583`) — GitHub already had a registry entry for the workflow by
  path, and a new trigger type on a commit that isn't on master was still
  honoured. `docker.yml` was a file with no history on any branch GitHub had
  indexed, and dispatching it the same way returned `404 Not Found` — it did
  not even appear in the workflow list. The two cases look identical from the
  commit (both are "a `workflow_dispatch` block on a feature branch") and
  behave oppositely. Rehearsing a genuinely new workflow needs it on the
  default branch first; only a new trigger on an existing one can be rehearsed
  from a feature branch the way `release.yml`'s attestation bump was.
- **A polling loop on a quiet resource fails this repo's own `worth_it` gate.**
  An hourly PR check-in ran ~30 times against a green, unchanged PR: `repeats`
  holds, `budget` does not — it spent every hour and shipped nothing, and
  `goal` does not, because no metric moved. Webhook subscription already wakes
  the session on real PR events, so the poll was redundant with a mechanism that
  costs nothing when nothing happens. Prefer the event; if a fallback is needed
  at all, make it daily.
- **A merge can land before the next push does, twice in a row, on this
  operator's cadence.** PR #8 was merged at its first green commit; a
  follow-up fix pushed seconds later landed on the feature branch but never
  reached `master`. Recovered by cherry-picking it back after restarting the
  branch — and PR #9, opened for exactly that recovery, was merged at ITS
  first green commit too, orphaning a second follow-up push the same way. The
  fix each time was the same: after any merge notification, diff the file you
  expect against what `origin/master` actually has before trusting the
  restart — do not assume the last thing pushed is the thing that landed. If a
  PR is likely to be merged fast, push everything intended for it in one shot
  rather than iterating with pushes in between.
- **A session's own git remote reverted once, unexplained, after `git remote
  set-url`.** After `omnex-factory` transferred to `Omnex-business-technologies`,
  setting `origin` to the new path was observed present at the end of one
  Bash call and reverted to `RaveZona/omnex-factory` by the next, with no
  local action between the two checks that would explain it — then, later in
  the same session with still nothing done to it directly, observed holding
  the new URL again, and `release_check.py --target citegate`'s
  `[project.urls]` check (which compares the declared URLs against
  `git remote get-url origin`) passed. One reversion is not a pattern; it is
  named here because it happened at all, in an environment that also refuses
  `add_repo` across owners for a session sourced elsewhere (`D-013`). Treat a
  git remote as unverified until checked in the same breath as the command
  that depends on it, not assumed stable from an earlier check in the
  conversation.

<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
