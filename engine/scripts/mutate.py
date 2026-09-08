"""Break the load-bearing rules on purpose. Every one must turn a test red.

    python scripts/mutate.py

"How many bugs are in it" has no honest integer, and inventing one is worse than
declining. What CAN be measured is the thing the question is really after: how
much of this codebase is actually held by its tests. Nine hundred green
assertions are evidence of nothing until breaking the code breaks them.

This is `test_the_round_trip_check_can_actually_fail` generalised. That test
breaks one emitter so the other fifteen are not comparing an artifact with
itself. The concurrency suite does the same by removing a lock and requiring the
loss. Both exist because the answer to "could this fail?" was once no, silently.
So the catalogue below asks it of every rule this repository considers
load-bearing, and a mutation that SURVIVES is a named hole with a file and a
line rather than a vague worry.

## Not a mutation-testing library

No `mutmut`, no dependency, and no attempt at coverage of every operator. A
random mutation of an arbitrary line mostly produces code that does not compile
or behaviour nobody promised, and the report is then dominated by noise a person
has to triage. Each entry here is hand-written against a rule the repository has
already paid for, and names the test that is supposed to catch it. Small and
argued beats large and unread.

## The working tree is never touched

Mutations are applied to a copy under a temporary directory. An in-place mutate
with a `finally` restore is one interrupt away from leaving a sabotaged file in
somebody's checkout, and the sabotage is designed to look plausible.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent


@dataclass(frozen=True)
class Mutation:
    """One rule, broken the way somebody would plausibly break it."""

    ident: str
    #: Path relative to the repository root.
    path: str
    #: Must appear exactly once, so the mutation is unambiguous.
    find: str
    replace: str
    #: Tests that must fail. Node ids, run from `engine/`.
    caught_by: tuple[str, ...]
    rule: str


CATALOGUE: tuple[Mutation, ...] = (
    Mutation(
        ident="stage_order_falls_back_to_string",
        path="engine/src/omnex/factory/gates.py",
        find="        return self.position < other.position",
        replace="        return str(self) < str(other)",
        caught_by=(
            "tests/test_factory.py::test_stages_compare_by_position_and_not_alphabetically",
        ),
        rule="an ordered StrEnum must not fall back to inherited string comparison",
    ),
    Mutation(
        ident="tool_result_may_be_trusted",
        path="engine/src/omnex/mcp/tools.py",
        find="        if self.segment.provenance is not Provenance.UNTRUSTED:",
        replace="        if False:",
        caught_by=("tests/test_mcp.py::test_a_tool_result_can_never_be_marked_trusted",),
        rule="a tool result is third-party content and may never be marked trusted",
    ),
    Mutation(
        ident="money_accepts_a_float",
        path="engine/src/omnex/core/money.py",
        find="        if isinstance(amount, float):",
        replace="        if False:",
        caught_by=("tests/test_core.py",),
        rule="Money refuses a float rather than accepting-and-rounding it",
    ),
    Mutation(
        ident="frozen_criteria_can_be_weakened",
        path="engine/src/omnex/harness/contract.py",
        find="            if replacement.check != existing.check:",
        replace="            if False:",
        caught_by=("tests/test_factory.py::test_the_frozen_criteria_refuse_to_be_weakened",),
        rule="a frozen criterion's check may never change — the anti-Goodhart anchor",
    ),
    Mutation(
        ident="n8n_loses_tool_prices",
        path="engine/src/omnex/factory/compile/n8n.py",
        find='            "omnexToolPicos": [[name, picos] for name, picos in blueprint.tool_picos],',
        replace='            "omnexToolPicos": [],',
        caught_by=("tests/test_compile.py::test_every_target_round_trips_every_paradigm",),
        rule="a compiler must re-read its own output without loss",
    ),
    Mutation(
        ident="cost_counter_becomes_a_float",
        path="engine/src/omnex/obs/metrics.py",
        find="            self.values[key] = self.values.get(key, 0) + amount",
        replace="            self.values[key] = self.values.get(key, 0.0) + amount",
        caught_by=(
            "tests/test_obs.py::test_a_pico_dollar_counter_stays_exact_past_the_float_boundary",
        ),
        rule="money never travels through a float accumulator",
    ),
    Mutation(
        ident="a_loop_may_grade_itself",
        path="engine/src/omnex/factory/feedback.py",
        find='        if self.claim != "proposed":',
        replace="        if False:",
        caught_by=("tests/test_feedback.py::test_a_loop_may_never_mark_one_implemented",),
        rule="the thing producing the evidence does not get to grade it",
    ),
    Mutation(
        ident="the_ledger_loses_its_lock",
        path="engine/src/omnex/obs/cost.py",
        find='        """One event, recorded atomically across every aggregate it touches."""\n        with self._lock:',
        replace='        """One event, recorded atomically across every aggregate it touches."""\n        if True:',
        caught_by=("tests/test_concurrency.py::test_the_cost_ledger_loses_no_event_under_threads",),
        rule="concurrent recording must not lose money",
    ),
    Mutation(
        ident="acquisition_charged_per_run",
        path="engine/src/omnex/factory/economics.py",
        find="        return self.revenue - self.cost.total",
        replace="        return self.revenue - self.cost.total - Money.from_usd('0.01')",
        caught_by=(
            "tests/test_economics.py::"
            "test_the_distribution_and_the_total_come_from_one_definition_of_margin",
        ),
        # This one SURVIVED on the first run and is the reason the probe exists.
        # `Run.margin` and `_summarise`'s total were two independent paths that
        # happened to agree, so changing one moved the median, p10 and worst
        # while the total and the verdict stayed put. Every number individually
        # plausible, the summary internally inconsistent, and nothing red.
        rule="the distribution and the total share one definition of margin",
    ),
    Mutation(
        ident="a_twin_splitter_drifts",
        path="engine/src/omnex/rag/ingest.py",
        find='    "dr.",\n',
        replace="",
        caught_by=("tests/test_citegate_parity.py::test_the_abbreviation_sets_are_the_same_set",),
        rule="the two splitter copies must agree",
    ),
    Mutation(
        ident="the_duplicate_run_refusal_is_dropped",
        path="engine/src/omnex/factory/economics.py",
        find="            if any(existing.run_id == run.run_id for existing in self._runs):",
        replace="            if False:",
        caught_by=("tests/test_economics.py::test_the_same_run_cannot_be_recorded_twice",),
        rule="one run counted twice moves the margin in whichever direction it went",
    ),
    Mutation(
        ident="an_unpriced_tool_bills_at_zero",
        path="engine/src/omnex/mcp/client.py",
        find="        if price is None:",
        replace="        if False:",
        caught_by=(
            "tests/test_mcp.py::test_a_tool_with_no_price_is_refused_rather_than_billed_at_zero",
        ),
        rule="zero is not a missing number, it is a wrong one",
    ),
    Mutation(
        ident="a_binding_may_shadow_the_reference",
        path="engine/src/omnex/factory/compile/n8n.py",
        find='            node["parameters"] = {**binding.parameters, **parameters}',
        replace='            node["parameters"] = {**parameters, **binding.parameters}',
        caught_by=(
            "tests/test_compile.py"
            "::test_a_binding_cannot_shadow_the_reference_the_parser_reads_back",
        ),
        rule="a hand-written parameter template may not rewrite the topology the parser reads back",
    ),
    Mutation(
        ident="a_key_rides_out_in_the_workflow",
        path="engine/src/omnex/factory/compile/n8n.py",
        find="    shape = looks_like_a_secret(document)",
        replace="    shape = None",
        caught_by=("tests/test_compile.py::test_a_secret_reaching_the_emitted_workflow_stops_it",),
        rule="an emitted workflow is committed and shared; a credential in it is an incident",
    ),
    Mutation(
        ident="a_claim_stops_being_exclusive",
        path="engine/src/omnex/pipeline/claim.py",
        find="            handle = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)",
        replace="            handle = os.open(path, os.O_CREAT | os.O_WRONLY, 0o600)",
        caught_by=(
            "tests/test_pipeline_cli.py::test_the_second_delivery_of_one_event_does_not_proceed",
        ),
        rule="both storefronts retry; one order delivered twice is two GPU-built packs",
    ),
    Mutation(
        ident="an_extra_may_claim_what_nothing_backs",
        path="engine/scripts/extras_check.py",
        find='    if status == "supported" and unbacked:',
        replace="    if False:",
        caught_by=("tests/test_extras_check.py::test_supported_with_nothing_importing_it_fails",),
        rule="an install that delivers a dependency and no capability is a promise with nothing behind it",
    ),
    Mutation(
        ident="derived_state_stops_being_checked",
        path="engine/scripts/state_map.py",
        find='    walk(committed, measured, "state")\n    return problems',
        replace='    walk(committed, measured, "state")\n    return []',
        caught_by=("tests/test_state_map.py::test_drift_is_caught_in_both_directions",),
        rule="machine state that can drift from the repository is worse than none",
    ),
    Mutation(
        ident="a_settled_decision_can_be_reopened",
        path="engine/scripts/node_dossier.py",
        find='    if node.claim == "rejected":\n        return "settled", "n/a", "a person said no; the proposal must not return"',
        replace='    if False:\n        return "settled", "n/a", "a person said no; the proposal must not return"',
        caught_by=("tests/test_node_dossier.py::test_a_settled_node_is_not_reopened",),
        rule="a person's rejection must not come back as a proposal on the next run",
    ),
)


@dataclass(frozen=True)
class Result:
    mutation: Mutation
    killed: bool
    detail: str


def _stage(workspace: Path) -> Path:
    """Copy what the targeted tests need. Never the working tree itself."""
    shutil.copytree(ENGINE / "src", workspace / "engine" / "src")
    shutil.copytree(ENGINE / "tests", workspace / "engine" / "tests")
    shutil.copytree(ENGINE / "scripts", workspace / "engine" / "scripts")
    shutil.copytree(REPO / "oss", workspace / "oss")
    shutil.copy2(ENGINE / "pyproject.toml", workspace / "engine" / "pyproject.toml")
    return workspace / "engine"


def verify_catalogue() -> list[str]:
    """Every mutation must be applicable and point at a test that exists.

    A `find` string that no longer appears, or appears twice, is a mutation that
    silently stops testing anything — the same failure mode as a CI step naming
    a file that does not exist.
    """
    problems: list[str] = []
    for mutation in CATALOGUE:
        target = REPO / mutation.path
        if not target.exists():
            problems.append(f"{mutation.ident}: {mutation.path} is gone")
            continue
        occurrences = target.read_text(encoding="utf-8").count(mutation.find)
        if occurrences != 1:
            problems.append(
                f"{mutation.ident}: its anchor appears {occurrences} times in "
                f"{mutation.path}, so the mutation is ambiguous or stale"
            )
        for node in mutation.caught_by:
            path = ENGINE / node.split("::")[0]
            if not path.exists():
                problems.append(f"{mutation.ident}: names missing test file {node}")
    return problems


def apply_and_run(mutation: Mutation, workspace: Path) -> Result:
    engine = _stage(workspace)
    target = workspace / mutation.path
    source = target.read_text(encoding="utf-8")
    target.write_text(source.replace(mutation.find, mutation.replace, 1), encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, "-m", "pytest", *mutation.caught_by, "-x", "-q", "--no-header"],
        cwd=engine,
        capture_output=True,
        text=True,
        check=False,
    )
    killed = completed.returncode != 0
    tail = (completed.stdout or completed.stderr).strip().splitlines()
    return Result(
        mutation=mutation,
        killed=killed,
        detail=tail[-1] if tail else "no output",
    )


def main() -> int:
    problems = verify_catalogue()
    if problems:
        print("the catalogue does not apply to this tree:")
        for problem in problems:
            print(f"  FAIL {problem}")
        return 1

    results: list[Result] = []
    for mutation in CATALOGUE:
        with tempfile.TemporaryDirectory(prefix="omnex-mutate-") as raw:
            results.append(apply_and_run(mutation, Path(raw)))
        state = "killed " if results[-1].killed else "SURVIVED"
        print(f"  {state}  {mutation.ident:38} {mutation.rule}")

    survivors = [r for r in results if not r.killed]
    print(f"\n{len(results) - len(survivors)} of {len(results)} mutations killed")
    for result in survivors:
        print(
            f"  HOLE {result.mutation.ident}: nothing failed when "
            f"{result.mutation.path} broke '{result.mutation.rule}' — {result.detail}"
        )
    return 1 if survivors else 0


if __name__ == "__main__":
    raise SystemExit(main())
