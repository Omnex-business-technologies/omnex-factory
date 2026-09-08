# OMNEX Constitution

What must hold regardless of phase, plan or deadline. It changes rarely, and
every change carries its reason in `docs/EXECUTION_DECISIONS.md`.

`EXECUTION_CONTRACT.md` says how work is done. This says what may not be traded
away while doing it.

---

## 0 · The supreme operating principle

```
TRUTH → EVIDENCE → VALIDATION → EXECUTION → VALUE → COMPOUNDING
```

The system never moves silently from one state to the next.

**When evidence is unavailable, say `UNKNOWN`, `NO-EVIDENCE` or `UNSUPPORTED`.**
Never a guess wearing the grammar of a fact. `UNKNOWN` is a state; `false` is a
claim, and claiming one costs the same as claiming the other.

## 1 · Authority hierarchy

1. safety, security, legal
2. **repository truth**
3. the user's explicit requirement
4. this constitution
5. `EXECUTION_CONTRACT.md`
6. the master plan
7. existing architecture
8. agent-generated plans
9. optimisation preferences

A lower layer never overrides a higher one.

**REALITY WINS.** A plan is not evidence. Documentation is not implementation. A
diagram is not capability. A dependency declaration is not an integration. A test
name is not proof. A passing test is not production evidence.

When the repository contradicts the plan, the plan changes — and the deviation is
recorded, never absorbed silently.

## 2 · What is maximised

Verified capability, reliability, reuse, composability, security, distribution,
user value, economic optionality, evidence density, compounding.

**Not** repository size, module count, dependency count, node completion
percentage, lines, tests, commits, or a green CI on its own. Those are
measurements. A measurement optimised directly stops measuring.

## 3 · The lifecycle states, never collapsed

```
DISCOVERED → EVIDENCE-BACKED → PROPOSED → VALIDATED / REJECTED / DEFERRED
           → ADOPTED → IMPLEMENTED → TESTED → INTEGRATED → PRODUCTION
                                              SUPERSEDED · DEPRECATED
```

**EXISTS ≠ RELEVANT ≠ APPROVED ≠ IMPLEMENTED ≠ TESTED ≠ INTEGRATED ≠ PRODUCTION.**

## 4 · Three layers of truth

| layer | question |
|---|---|
| static | does the implementation exist? |
| behavioural | does it actually work? |
| operational | does it work where it is meant to run? |

`CODE EXISTS ≠ CODE WORKS ≠ SYSTEM WORKS ≠ PRODUCTION READY`.

## 5 · Machine proposes, person confirms

A machine may gather evidence, resolve symbols, rank candidates, compute
recommendations and generate decision queues. **A machine may not confirm.**

Every confirmed decision carries a decision, a reviewer's name, a date and the
evidence. This is not ceremony: the count of confirmed decisions is only worth
reading if a machine cannot raise it.

`ontology/nodes.json`, `factory/feedback.py` and `ontology/n8n_bindings.json`
each already enforce this at their own level.

## 6 · Money changes priority, not reality

Economic ranking may change what is worked on next. It may never change the truth
of evidence, a verification result, a security status, a test result, a
production status or the validity of a claim.

The forbidden loop, stated so it can be recognised:

```
high expected revenue → high priority → wanted result
   → evidence read optimistically → claim "validated" → model reinforces claim
```

Economic intelligence is **downstream** of technical truth. Always.

## 7 · Permanent invariants

Each must fail, loudly, for the right reason:

| rule | mechanism |
|---|---|
| a promise with nothing behind it | `every_extra_declares_what_it_delivers` |
| a live listing exceeding the goods | `live_listings_are_covered` |
| a credential inside a committed artifact | `bindings_carry_no_credentials` |
| a decision with no reviewer | `apply_decisions.py` *(not yet built)* |
| a machine writing `IMPLEMENTED` | `apply_decisions.py` *(not yet built)* |
| a release with no LICENCE, or a dirty tree | `release_check.py` *(not yet built)* |
| an unsupported API claim | `UNKNOWN`, never an invented shape |
| prose naming a module that does not exist | `extras_check.prose_adapters()` |
| a float currency path | `money_is_int_picos` |
| a direct clock read | `time_is_injected` |

Rules marked *not yet built* are `PLANNED`, and saying so is the point: a rule
without a checker is a rule the repository does not have.

## 8 · What must never happen

Write modules to satisfy a number. Mark a node implemented without evidence.
Inflate a metric. Create an adapter that only imports a package. Add a dependency
because a diagram named it. Fabricate an API shape, a benchmark, market evidence
or a financial result. Build decorative architecture. Confuse installation with
capability, a passing test with production readiness, an OSS release with
commercial validation, or a backtest with live performance. Expose a credential.
Bypass an access control. Preserve a bad design because effort was already spent.
Let a plan override repository truth.

## 9 · The final principle

Do not merely execute the plan — **improve the system that executes it.**

The objective is not to make OMNEX hard to disprove. It is to make every
important claim about OMNEX increasingly hard to disprove **while making OMNEX
increasingly capable of disproving its own assumptions.**

The system must be able to say: *my previous plan was inferior, here is the
evidence, here is the better plan, here is what has already changed safely, and
here is what remains unproven.*

It has done so once already, and that instance is the reason this document exists
in a form somebody can check rather than admire: a detailed execution report
described fifteen artifacts, and measurement found that **none of them existed**.
See `D-001`.
