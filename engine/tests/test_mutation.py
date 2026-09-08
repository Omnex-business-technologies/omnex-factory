"""The mutation catalogue, kept applicable and shown to work.

The full probe lives in `scripts/mutate.py` and runs as its own CI step, because
twelve mutations each spawning a pytest is seconds this suite should not spend
on every run. What belongs here is cheap and load-bearing: that every mutation
still applies to the tree it claims to mutate, and that the harness genuinely
turns a test red rather than reporting success from a run that never happened.

A stale `find` string is the failure this file exists for. It costs nothing, it
raises nothing, and the mutation silently stops testing anything — exactly the
shape of the CI step that named a test file which did not exist. Verified here
so a refactor that moves the line is caught by the suite rather than by somebody
eventually reading the probe's output.

## What the probe answers

"How many bugs are there" has no honest integer. "How much of this is actually
held by its tests" does, and on its first run the answer was 11 of 12: the
twelfth found that `Run.margin` and `_summarise`'s total were independent code
paths that happened to agree, so changing one moved the median, p10 and worst
while the total and the verdict stayed put. Every number individually plausible,
the summary internally inconsistent, and nothing red.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from mutate import CATALOGUE, apply_and_run, verify_catalogue


def test_every_mutation_still_applies_to_the_tree() -> None:
    """A stale anchor is a mutation that silently stops testing anything."""
    assert verify_catalogue() == []


def test_the_catalogue_covers_the_rules_this_repository_calls_load_bearing() -> None:
    """Not a coverage percentage — a named list, argued one at a time.

    A random mutation of an arbitrary line mostly produces code that does not
    compile, and a report dominated by noise is one nobody triages. Each entry
    is hand-written against a rule already paid for, so the count means
    something.
    """
    subjects = {mutation.path for mutation in CATALOGUE}
    for expected in (
        "engine/src/omnex/core/money.py",
        "engine/src/omnex/obs/cost.py",
        "engine/src/omnex/obs/metrics.py",
        "engine/src/omnex/mcp/tools.py",
        "engine/src/omnex/harness/contract.py",
        "engine/src/omnex/factory/gates.py",
        "engine/src/omnex/factory/feedback.py",
        "engine/src/omnex/factory/economics.py",
        "engine/src/omnex/factory/compile/n8n.py",
        "engine/src/omnex/rag/ingest.py",
    ):
        assert expected in subjects, f"no mutation exercises {expected}"


def test_every_mutation_names_a_distinct_rule() -> None:
    idents = [mutation.ident for mutation in CATALOGUE]
    assert len(set(idents)) == len(idents)
    assert all(mutation.rule.strip() for mutation in CATALOGUE)
    assert all(mutation.caught_by for mutation in CATALOGUE)


def test_the_probe_actually_turns_a_test_red() -> None:
    """One mutation end to end, so the harness is not reporting on a run it skipped.

    A subprocess that fails to start, a copy that lands in the wrong place, a
    pytest invocation matching no tests — each returns a value this could read as
    "killed" or "survived" without anything having been exercised. Running one
    for real is the only way to know the other eleven mean what they say.
    """
    mutation = next(m for m in CATALOGUE if m.ident == "stage_order_falls_back_to_string")
    with tempfile.TemporaryDirectory(prefix="omnex-mutate-test-") as raw:
        result = apply_and_run(mutation, Path(raw))
    assert result.killed, (
        "breaking Stage's ordering did not fail its test, so the probe is not "
        f"running what it thinks it is: {result.detail}"
    )


def test_the_probe_never_touches_the_working_tree() -> None:
    """An in-place mutate is one interrupt from leaving sabotage in a checkout.

    And the sabotage is written to look plausible, which is what makes it worth
    forbidding structurally rather than remembering to clean up.
    """
    source = Path(__file__).resolve().parents[1] / "src" / "omnex" / "factory" / "gates.py"
    before = source.read_text(encoding="utf-8")
    mutation = next(m for m in CATALOGUE if m.path.endswith("factory/gates.py"))
    with tempfile.TemporaryDirectory(prefix="omnex-mutate-safety-") as raw:
        apply_and_run(mutation, Path(raw))
    assert source.read_text(encoding="utf-8") == before
