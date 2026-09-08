"""The chain, walked — and every link that is only written down, said so.

    python scripts/spine_check.py           # the fourteen transitions
    python scripts/spine_check.py --strict   # exit non-zero on anything DOCUMENTED

The hardening contract's final gate: before broad adapter or deployment work,
demonstrate

    TRUTH → STATE → CLAIM → EVIDENCE → CAPABILITY → DEPENDENCY
      → EXECUTION GRAPH → NEXT ACTION → POLICY → EXECUTION → VERIFICATION
      → RUN LEDGER → CHECKPOINT → RECOVERY

and for each transition name its SOURCE, CONTRACT, VALIDATION, FAILURE MODE and
PROOF. **If a transition is merely documented rather than executable, classify it
accordingly.** Do not claim completion.

## What makes this different from a diagram

Each link names a callable and a test. `EXECUTABLE` means the callable resolves
here, right now, through `omnex.core.symbols.resolve` — the one resolver — and
the test file exists. Anything else is `DOCUMENTED` or `ABSENT`, and the
difference between "we designed this" and "this runs" stops being a matter of
tone.

That is the whole point. A gate that can only print a passing chain is the
decorative architecture it was built to prevent, so this one is expected to
report failures of its own design. On the commit that introduced it, it did:
**EXECUTION → RUN LEDGER was `DOCUMENTED`** — `runs.py` was checked by CI and
nothing wrote to it, so `state/runs.jsonl` did not exist.

## Why `--strict` is not the default

An all-green chain is the goal, not the current state, and a permanently red
build is one people learn to ignore — the same reasoning that scopes
`live_listings_are_covered` to live offers. The default reports honestly and
exits 0; `--strict` is for the day the chain is meant to be complete, and for a
test that asserts a specific link has not silently regressed.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
sys.path.insert(0, str(ENGINE / "scripts"))
sys.path.insert(0, str(ENGINE / "src"))

from omnex.core.symbols import resolve  # noqa: E402


class Grade(StrEnum):
    """Three states, never two. `DOCUMENTED` is the one that matters."""

    EXECUTABLE = "EXECUTABLE"
    #: The design exists and is written down; nothing runs it.
    DOCUMENTED = "DOCUMENTED"
    ABSENT = "ABSENT"


@dataclass(frozen=True)
class Link:
    """One transition, with everything the contract requires named."""

    step: str
    source: str
    contract: str
    #: The callable that performs it. Resolved, never assumed.
    performed_by: str
    #: The test that holds it, relative to `engine/`.
    proof: str
    failure_mode: str
    #: A file whose existence proves the link has actually been exercised.
    #: Empty when resolving the callable is itself the proof.
    artifact: str = ""

    def grade(self) -> tuple[Grade, str]:
        """EXECUTABLE only when the code resolves, the test exists, and — where
        the link produces something — that artifact is on disk."""
        if (reason := resolve(self.performed_by)) is not None:
            return Grade.ABSENT, f"{self.performed_by} does not resolve ({reason})"
        if not (ENGINE / self.proof).exists():
            return Grade.ABSENT, f"{self.proof} is not in this checkout"
        if self.artifact and not (REPO / self.artifact).exists():
            return Grade.DOCUMENTED, f"{self.artifact} does not exist — nothing has produced one"
        return Grade.EXECUTABLE, ""


#: The fourteen transitions, in the contract's order. Each names real code.
CHAIN: tuple[Link, ...] = (
    Link(
        step="TRUTH → STATE",
        source="the repository working tree and git",
        contract="state is derived from the repository, never typed",
        performed_by="state_map.derive",
        proof="tests/test_state_map.py",
        failure_mode="machine state drifts and is read instead of looking",
        artifact="execution_state.json",
    ),
    Link(
        step="STATE → CLAIM",
        source="state/claims.jsonl",
        contract="a claim is a written assertion with a type that can be settled",
        performed_by="claims.load",
        proof="tests/test_claims.py",
        failure_mode="an assertion nothing could ever verify",
        artifact="state/claims.jsonl",
    ),
    Link(
        step="CLAIM → EVIDENCE",
        source="state/evidence.jsonl",
        contract="evidence carries a method, a stance, a version and an expiry",
        performed_by="claims.Registry",
        proof="tests/test_claims.py",
        failure_mode="support and contradiction collapse into one field",
        artifact="state/evidence.jsonl",
    ),
    Link(
        step="EVIDENCE → CAPABILITY",
        source="claims.VERIFIES",
        contract="only a method appropriate to the claim type can settle it",
        performed_by="claims.VERIFIES",
        proof="tests/test_claims.py",
        failure_mode="writing a row and proving a thing become the same act",
    ),
    Link(
        step="CAPABILITY → DEPENDENCY",
        source="a claim's `dependencies`",
        contract="a claim is never firmer than what it rests on",
        performed_by="claims.Claim",
        proof="tests/test_claims.py",
        failure_mode="a conclusion outruns its own foundation",
    ),
    Link(
        step="DEPENDENCY → EXECUTION GRAPH",
        source="the registry, joined on dependency edges",
        contract="the graph is derived; there is no second, maintained copy",
        performed_by="next_action.recommend",
        proof="tests/test_next_action.py",
        failure_mode="a hand-kept task list drifts from the repository",
    ),
    Link(
        step="EXECUTION GRAPH → NEXT ACTION",
        source="claim status and dependent count",
        contract="ranking is a heuristic and says so in its own output",
        performed_by="next_action.queue",
        proof="tests/test_next_action.py",
        failure_mode="a score quietly becomes a decision",
    ),
    Link(
        step="NEXT ACTION → POLICY",
        source="the action's declared side-effect classes",
        contract="an action may not silently escalate its own autonomy level",
        performed_by="policy.authorise",
        proof="tests/test_next_action.py",
        failure_mode="'run the tests' grows a publish step and keeps its name",
    ),
    Link(
        step="POLICY → EXECUTION",
        source="a Grant handed in from outside",
        contract="PUBLISH/DEPLOY/CREDENTIAL/FINANCIAL/DESTRUCTIVE need a person",
        performed_by="policy.Grant",
        proof="tests/test_next_action.py",
        failure_mode="an autonomy level alone clears an irreversible action",
    ),
    Link(
        step="EXECUTION → VERIFICATION",
        source="the gate block in CLAUDE.md",
        contract="CI is a superset of the documented gate",
        performed_by="release_check.covers_changes",
        proof="tests/test_ci_contract.py",
        failure_mode="the document is stricter than CI and becomes advice",
    ),
    Link(
        step="VERIFICATION → RUN LEDGER",
        source="an agent recording what it did",
        contract="append-only, hash-chained, no secrets, expectation before result",
        performed_by="runs.append",
        proof="tests/test_runs.py",
        failure_mode="work happens and leaves no reconstructible trace",
        artifact="state/runs.jsonl",
    ),
    Link(
        step="RUN LEDGER → CHECKPOINT",
        source="the registry plus the ledger",
        contract="derived from the commit, and carries no timestamp",
        performed_by="runs.checkpoint",
        proof="tests/test_runs.py",
        failure_mode="a checkpoint differs from itself and its validator learns to ignore a field",
    ),
    Link(
        step="CHECKPOINT → RECOVERY",
        source="the newest checkpoint",
        contract="seven questions answered without conversational memory",
        performed_by="runs.recovery_briefing",
        proof="tests/test_runs.py",
        failure_mode="a fresh session needs a person to say where the last one stopped",
    ),
    Link(
        step="RECOVERY → TRUTH",
        source="the briefing's own next action",
        contract="it is labelled a recommendation, and re-derives rather than trusts",
        performed_by="claims.load",
        proof="tests/test_runs.py",
        failure_mode="the loop closes on its own summary instead of the repository",
    ),
)


def walk(chain: tuple[Link, ...] | None = None) -> list[tuple[Link, Grade, str]]:
    """Grade every link. `chain` defaults to `CHAIN` read at call time, not at
    definition time — a default argument would bind the tuple once and make the
    module's own gate impossible to test against a broken chain."""
    return [(link, *link.grade()) for link in (CHAIN if chain is None else chain)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Walk the spine and grade every link.")
    parser.add_argument(
        "--strict", action="store_true", help="exit non-zero unless every link is EXECUTABLE"
    )
    parser.add_argument("--verbose", action="store_true", help="print each link's full contract")
    args = parser.parse_args()

    results = walk()
    width = max(len(link.step) for link in CHAIN)
    for link, grade, detail in results:
        print(f"  {link.step:<{width}}  {grade.value:<11} {detail}")
        if args.verbose:
            print(f"      source     {link.source}")
            print(f"      contract   {link.contract}")
            print(f"      performed  {link.performed_by}")
            print(f"      proof      {link.proof}")
            print(f"      fails as   {link.failure_mode}")

    counts = {g: sum(1 for _, grade, _ in results if grade is g) for g in Grade}
    print()
    print(" · ".join(f"{n} {g.value}" for g, n in counts.items() if n))

    unproven = [link for link, grade, _ in results if grade is not Grade.EXECUTABLE]
    if unproven:
        print()
        print("Not a complete chain. The links above that are not EXECUTABLE are")
        print("designs, not mechanisms, and this gate exists to say so rather than")
        print("to average them away:")
        for link in unproven:
            print(f"  - {link.step}: {link.failure_mode}")
        if args.strict:
            return 1
        print()
        print("Exit 0 without --strict: an all-green chain is the goal, not the")
        print("current state, and a permanently red build is one people ignore.")
    else:
        print("\nEvery transition resolves to code that runs and a test that holds it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
