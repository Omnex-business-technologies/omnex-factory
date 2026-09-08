# OMNEX Execution Contract

How work is chosen, done, verified and recorded. `CONSTITUTION.md` says what may
not be traded away; this says the procedure.

Subordinate to the constitution and to repository truth. Where this document and
the repository disagree, **the repository is right and this changes.**

---

## 1 · Scarce resources

Time, context, tokens, compute, attention, complexity, dependencies, capital,
risk, external side effects.

Prefer actions that are high-value, evidence-backed, reversible, reusable,
low-risk and architecturally coherent.

**Verification depth is proportional to consequence.** Deeper when security
sensitivity, external side effects, financial consequence, production impact,
irreversibility or blast radius rise. The target is *maximum justified
verification*, not maximum verification — over-verifying a typo spends the budget
that a release needed.

## 2 · Autonomy levels

| level | what it covers |
|---|---|
| L0 | observe — inspect only |
| L1 | propose — analyse, prepare, apply nothing |
| L2 | implement — change the tree locally and validate |
| L3 | integrate — implement, test, refactor, update docs and durable state |
| L4 | operate — run authorised operational workflows |
| L5 | external effect — production, money, publication, credentials, irreversible state |

Default for ordinary repository engineering is **L3**. L5 requires explicit
authorisation unless a durable authorisation already covers that exact class.

### Side-effect classes

`READ · WRITE · LOCAL_EXECUTION · NETWORK · GIT · PACKAGE_INSTALL · DEPLOY ·
PUBLISH · CREDENTIAL · FINANCIAL · DESTRUCTIVE`

No action silently escalates its class. `PUBLISH`, `DEPLOY`, `FINANCIAL`,
`CREDENTIAL` and `DESTRUCTIVE` need explicit authorisation.

**Standing authorisations in this repository today:** commit and push to
`claude/production-ai-projects-bzz82l` in `RaveZona/omnex-factory` (`GIT`), and
nothing else. PyPI publication, storefront calls and GPU generation are held by
the person, and each refuses by name rather than proceeding.

## 3 · Information gain

Before expensive implementation: *what is the cheapest fact that could invalidate
the most expensive assumption?*

Investigate when cheap discovery prevents costly wrong work. Stop when more
information is unlikely to change the decision. `NO-EVIDENCE` is not `NO-VALUE` —
a node without evidence may still be worth a cheap investigation, it just may not
be represented as validated.

## 4 · Promise integrity

Every claim the repository makes about itself resolves to something:

```
CLAIM → RESOLVER → IMPLEMENTATION → TEST → EVIDENCE → GATE
```

Claims live in `pyproject.toml`, READMEs, docstrings, CLI help, exported symbols,
Docker services, skills, deployment manifests, benchmarks and listings. A missing
link fails the relevant gate.

Already enforced: `extras_check.py` (extras and prose-named adapters),
`env_check.py` (environment variables), `listing_check.py` (a listing against QC),
`n8n_bindings_check.py` (a binding's commands), `invariant_map.py` (the rules).

## 5 · Human decision governance

The machine generates dossiers, resolves symbols, collects evidence, ranks
candidates and produces decision queues. The person approves, rejects, defers or
revises. Every confirmed decision carries decision, reviewer, date, evidence.

A recommendation is never an authority:

```
REPOSITORY FACT → GRAPH STATE → HEURISTIC RANKING → RECOMMENDATION
   → POLICY CHECK → AUTHORISATION → EXECUTION
```

A score never silently becomes a decision. Any ranking states that it is a
heuristic, in its own output.

## 6 · Evidence

Evidence is separate from the claim it supports, and negative evidence is
first-class. Every external observation carries `observed_at`, source, version
and verification method, because *"the API is X"* is not true a year later.

Prefer, in order: repository evidence · actual installed package behaviour ·
official documentation · authoritative package metadata · reproducible
experiment · secondary sources.

**Contradictory evidence is never deleted.** A newer positive result *supersedes*
it explicitly, so the registry can still answer what contradicted the claim and
when.

### What is reachable from here

PyPI and `files.pythonhosted.org` answer, so a third-party API shape is read from
the actual package rather than from memory. The open web is refused at the proxy,
so Etsy and Lemon Squeezy shapes are `UNKNOWN` and stay that way until somebody
with access supplies them. That is a stated boundary, not an excuse: the
storefront bindings carry the knowable parts and a note saying what is absent.

## 7 · Adversarial verification

Before a milestone is called done, try to break it. Four adversaries:

- **completeness** — what is missing?
- **truth** — which claim might not be true?
- **failure** — how does this break in production?
- **value** — is there real user value, or only technical impression?

`mutate.py` is this mechanism for code: sixteen rules broken on purpose, each
naming the test that must go red. A rule that survives its mutation is a rule the
tests do not hold.

## 8 · Definition of done

Not done because code exists, an import succeeds, a unit test passes,
documentation exists or CI is green.

**Done** means the capability reached the evidence level appropriate to its
claimed status, and its limitations are explicit. Production claims need
production evidence; distribution claims need release evidence; economic claims
need empirical evidence.

If any material criterion fails, say `PARTIALLY COMPLETED`, `BLOCKED`,
`EXPERIMENTAL`, `UNKNOWN`, `UNSUPPORTED`, `DEFERRED` or `REJECTED`.

## 9 · Release maturity gates

```
0  integrity      the repository tells the truth
1  architecture   509 figures / 507 nodes mapped
2  evidence       important claims have evidence
3  implementation implemented capabilities have tests
4  integration    components work together
5  production     deployment is verified
6  security       supply chain and permissions controlled
7  observability  logs, metrics, traces
8  evaluation     AI outputs measurable
9  autonomy       agent actions policy-bounded
10 distribution   artifacts legitimately releasable
11 commercial     external users get measurable value
12 economic       economic outcomes measurable
```

No gate is skipped silently. An unmeasured gate is `UNKNOWN`, not `false`.

## 10 · Derived state, never a second truth

```
SOURCE OF TRUTH → TRANSFORMATION → DERIVED ARTIFACT → VALIDATOR
```

| source | transformation | artifact | validator |
|---|---|---|---|
| repository, git, ontology, pyproject | `state_map.py` | `execution_state.json` | `state_check.py` |
| `invariants.json` + checkers | `invariant_map.py` | `INVARIANTS.md` | its own exit code |
| `branches.json` + symbols | `ontology_map.py` | `COVERAGE.md` | its own exit code |
| listing + QC manifests | `business_map.py` | `BUSINESS.md` | `test_business_map.py` |

An artifact that cannot name its source of truth is either given one or removed.

**No timestamp in a derived artifact.** A generation time changes on every run,
which would make the file differ from itself and force the validator to learn to
ignore fields. Derived state is keyed on the commit it was derived from.
Timestamps belong to observations and events, where they mean something.

## 11 · Idempotency

Every state, graph, projection and verification script is safely repeatable.
Running it twice must not duplicate entries, mutate a human decision, alter
recorded evidence, produce arbitrary ordering, or change output without an input
change.

## 12 · Stop the line

A high-severity invariant failure blocks downstream work. Do not route around a
failure to advance a phase number.

When blocked, the report is:

```
BLOCKED → exact reason → evidence → affected scope
        → minimum required resolution → safe alternative if one exists
```

**Currently blocked, with evidence:**

| what | reason | minimum resolution |
|---|---|---|
| Etsy / Lemon Squeezy API shapes | proxy refuses the open web (`403 to CONNECT`) | a person supplies the endpoint via `OMNEX_*_URL` |
| a live listing | 80 of 170 images through QC | 90 more images generated on a GPU |
| PyPI publication | no `PYPI_API_TOKEN`, held by the person | the credential holder runs the final step |
| n8n binding confirmation | 0 of 7 confirmed | one import into a real n8n instance |

A stopped phase is not a failed phase.

## 13 · Next best action

After every material state change: update state → reassess evidence,
dependencies, risk and value → select the next action.

The master plan sets direction. The current evidence sets the next move.
Repository truth overrides both.
