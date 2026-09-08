---
name: eval-gate
description: A CI deploy gate for AI systems that blocks on cases which used to pass and now fail, rather than on an average. Use when adding quality checks to a pipeline, when a mean score is hiding regressions, or when a team keeps shipping changes that break specific known-good cases.
---

# Eval gate

```bash
cd engine && .venv/bin/python scripts/eval_gate.py \
    --suite suites/rag_core.json \
    --baseline .omnex/baseline.json \
    --out .omnex/runs
```

Exits non-zero when quality regressed. That is the whole contract.

## It gates on newly-failing cases, not on the mean

A mean can absorb a real regression. Ten cases improve slightly, three cases
that used to work now fail completely, the average goes *up*, and the gate lets
it through. Those three cases are somebody's actual workflow.

So the primary rule is: **any case that passed against the baseline and fails
now blocks the deploy**, and the gate prints their ids.

```
BLOCKED — 3 case(s) that passed now fail
  regressed: rag-014, rag-031, fin-002
```

A mean-drop tolerance exists as a *secondary* rule (`max_mean_drop = 0.02`),
because a broad shallow decline across every case is also real and no individual
case crosses its threshold. It is not the primary rule and it is not zero — a
gate that blocks on any movement at all blocks on noise, and a gate that fires
on noise gets switched off, which is strictly worse than not having one.

`allowed_regressions` defaults to 0 and should stay there. It exists so a team
can knowingly ship a trade-off, not so the gate can be widened one increment at
a time until it never fires.

## Three properties that sound obvious and are usually missing

**It exits non-zero.** A quality check that prints a warning and exits 0 never
blocks anything. This fails the build the way a type error does.

**Its output is readable in a CI log.** Case ids in the terminal, where the
person who broke it is already looking — not a JSON blob, not a link to a
dashboard behind a login.

**It records the run whether or not it passed.** A failed run is the most useful
one to keep: it is the evidence for what changed. Deleting runs because the
build went red is how a team loses the ability to answer "when did this start".

## The baseline is never updated automatically

Only on an explicit `--record`.

Auto-updating on success ratifies a slow decline one commit at a time, each one
only slightly worse than the last and each one passing its own gate. After two
months the baseline *is* the degraded system, and every number since has been
measuring it against itself.

## The suite fingerprint

The gate refuses to compare runs across different suite fingerprints, raising
rather than producing a number.

Editing an expected answer and re-running is otherwise indistinguishable from
fixing the system — the score goes up either way. Refusing the comparison makes
changing the suite a deliberate act with its own commit, which is where it
belongs.

## What it cannot tell you

Whether your suite measures the right thing. A gate is a regression detector,
not a quality oracle: it holds the line where the baseline was drawn and has no
opinion about whether that line was in a useful place. Cases that nobody wrote
cannot regress.
