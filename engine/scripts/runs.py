"""What an agent did, why it was allowed to, and how a fresh one continues.

    python scripts/runs.py                    # the ledger
    python scripts/runs.py --checkpoint       # write one from the current state
    python scripts/runs.py --recover          # what a fresh agent needs to know
    python scripts/runs.py --check            # refuse a tampered or leaky ledger

This session hit a context limit twice. Both times the next session had to
reconstruct what had happened from a git log and a summary — which works only
because a person was there to say "you stopped at PHASE 3". That is exactly the
dependency this file removes.

## One module, not three

The plan named `checkpoint.py` and `recover.py` separately. They are one data
model — a checkpoint is a projection of the ledger plus the registry, and a
recovery is a rendering of the newest checkpoint — and three files sharing one
model is three places for the model to drift. Same argument as
`one_symbol_resolver`. The deviation is recorded rather than silent.

## Append-only, and chained so that is checkable

Every entry carries the hash of the one before it. Editing an old entry breaks
every hash after it, so "append-only" is a property the file can be tested for
rather than a convention people are asked to respect. `omnex.crew` already does
this for consensus audit; this is the same device one level out.

The chain proves *internal* consistency only. Somebody who rewrites the whole
file, recomputing as they go, produces a valid chain — it is tamper-**evident**,
not tamper-proof, and calling it the latter would be the kind of claim this
repository exists to refuse. Git history is what makes the rewrite visible.

## No secrets, checked rather than promised

Runs record what was done, and what was done sometimes involves a credential.
The ledger records the credential's **name**, never its value —
`bindings.looks_like_a_secret` is reused to enforce it, the same detector the
n8n catalogue uses. A ledger that has copied a token has become the incident it
was meant to record.

## expected_outcome is written before the result, or it is not a prediction

Every run carries `expected_outcome` and `observed_outcome`, and the second
starts UNKNOWN. The field is nearly free now and impossible to add
retroactively: an expectation recorded *after* the result is not a prediction,
it is a description. The full OUTCOME → LEARNING → GRAPH UPDATE loop is not
built — there are not enough runs for it to learn from, and building it now
would be decorative — but the data it will need cannot be backfilled, so it
starts here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
STATE = REPO / "state"
LEDGER = STATE / "runs.jsonl"
CHECKPOINTS = STATE / "checkpoints.jsonl"
sys.path.insert(0, str(ENGINE / "scripts"))
sys.path.insert(0, str(ENGINE / "src"))

from claims import Status  # noqa: E402
from claims import load as load_claims  # noqa: E402
from next_action import queue  # noqa: E402

from omnex.factory.compile.bindings import looks_like_a_secret  # noqa: E402

#: Written into `observed_outcome` until something measures it. Never `False`:
#: an unmeasured result is unmeasured, not a failure.
UNKNOWN = "UNKNOWN"


@dataclass
class Run:
    """One unit of agent work, reconstructible from this record alone."""

    run_id: str
    session_id: str
    agent_id: str
    timestamp: str
    objective: str
    selected_action: str
    authorization: str
    autonomy_level: str
    git_commit_before: str
    #: Written before the work, so it is a prediction rather than a description.
    expected_outcome: str
    parent_run_id: str = ""
    policy: str = ""
    budget: str = ""
    inputs_hash: str = ""
    outputs_hash: str = ""
    git_commit_after: str = ""
    evidence_refs: tuple[str, ...] = ()
    checkpoint_id: str = ""
    result: str = UNKNOWN
    observed_outcome: str = UNKNOWN
    rollback_ref: str = ""
    prev_hash: str = ""

    def digest(self) -> str:
        """A hash over every field except the chain link itself."""
        body = {k: v for k, v in asdict(self).items() if k != "prev_hash"}
        body["prev_hash"] = self.prev_hash
        return hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


def _read(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def load(path: Path | None = None) -> list[Run]:
    rows = _read(path or LEDGER)
    return [
        Run(
            **{
                **row,  # type: ignore[arg-type]
                "evidence_refs": tuple(row.get("evidence_refs", ()) or ()),  # type: ignore[union-attr]
            }
        )
        for row in rows
    ]


def append(run: Run, path: Path | None = None) -> Run:
    """Add one entry, chained to the last. The only way the ledger grows.

    Idempotent on `run_id`: appending the same run twice is a no-op rather than
    a second entry. A retried step must not read as two units of work.
    """
    target = path or LEDGER
    existing = load(target)
    if any(r.run_id == run.run_id for r in existing):
        return next(r for r in existing if r.run_id == run.run_id)

    run.prev_hash = existing[-1].digest() if existing else ""
    leak = _leaks(run)
    if leak:
        raise ValueError(f"refusing to write a run that carries {leak}")

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(run), sort_keys=True) + "\n")
    return run


def _leaks(run: Run) -> str | None:
    for value in asdict(run).values():
        if isinstance(value, str) and (found := looks_like_a_secret(value)):
            return found
    return None


def broken_links(runs: list[Run]) -> list[str]:
    """Every place the chain does not hold, which is every place it was edited."""
    problems: list[str] = []
    expected = ""
    for run in runs:
        if run.prev_hash != expected:
            problems.append(
                f"{run.run_id}: prev_hash {run.prev_hash[:8] or '(empty)'} but the "
                f"entry before it hashes to {expected[:8] or '(empty)'} — the ledger "
                "was edited, not appended to"
            )
        expected = run.digest()
    problems.extend(
        f"{run.run_id}: carries {leak}" for run in runs if (leak := _leaks(run)) is not None
    )
    return problems


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args], capture_output=True, text=True, timeout=60
    ).stdout.strip()


@dataclass
class Checkpoint:
    """Enough for a fresh session to continue without conversational memory."""

    checkpoint_id: str
    git_commit: str
    tree_clean: bool
    claims: dict[str, int] = field(default_factory=dict)
    blockers: list[str] = field(default_factory=list)
    next_action: str = ""
    contradicted: list[str] = field(default_factory=list)
    unknown: list[str] = field(default_factory=list)
    runs_recorded: int = 0
    verification: str = ""


def checkpoint() -> Checkpoint:
    """Derived from the repository every time. Never typed, never accumulated."""
    registry = load_claims()
    statuses = {c.claim_id: registry.status(c) for c in registry.claims}
    ranked = queue(registry)
    commit = _git("rev-parse", "HEAD")

    return Checkpoint(
        # Keyed on the commit, not a timestamp: a checkpoint that changed every
        # run would differ from itself and force its validator to ignore a field.
        checkpoint_id=f"cp-{commit[:12]}",
        git_commit=commit,
        tree_clean=not _git("status", "--porcelain"),
        claims={
            s.value: sum(1 for v in statuses.values() if v is s)
            for s in Status
            if any(v is s for v in statuses.values())
        },
        blockers=[f"{r.claim_id}: {'; '.join(r.blockers)}" for r in ranked if r.blockers],
        next_action=ranked[0].what if ranked else "",
        contradicted=[k for k, v in sorted(statuses.items()) if v is Status.CONTRADICTED],
        unknown=[k for k, v in sorted(statuses.items()) if v is Status.UNKNOWN],
        runs_recorded=len(load()),
        verification="run the gate block in CLAUDE.md; this file does not run it",
    )


def recovery_briefing(point: Checkpoint) -> str:
    """The seven questions a fresh agent has, answered from the repository."""
    runs = load()
    failed = [r for r in runs if r.result not in (UNKNOWN, "ok", "success")]
    return "\n".join(
        [
            f"WHERE WE ARE     {point.git_commit[:12]} on "
            f"{_git('rev-parse', '--abbrev-ref', 'HEAD')}, "
            f"tree {'clean' if point.tree_clean else 'DIRTY'}",
            f"WHAT IS TRUE     {point.claims.get('SUPPORTED', 0)} claim(s) SUPPORTED",
            f"WHAT IS UNKNOWN  {len(point.unknown)}: {', '.join(point.unknown) or 'none'}",
            f"WHAT WAS DONE    {point.runs_recorded} run(s) in the ledger",
            f"WHAT FAILED      {len(failed)}: "
            + (", ".join(f"{r.run_id} ({r.result})" for r in failed) or "nothing recorded"),
            f"WHAT IS BLOCKED  {len(point.contradicted)} contradicted: "
            + (", ".join(point.contradicted) or "none"),
            "                 " + ("; ".join(point.blockers) or "no dependency blockers"),
            f"WHAT NEXT        {point.next_action or 'nothing outstanding in the registry'}",
            "",
            "That is a RECOMMENDATION derived from the claim registry, not an",
            "instruction and not an authorization. Verify before acting:",
            f"                 {point.verification}",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="The run ledger, checkpoint and recovery.")
    parser.add_argument("--checkpoint", action="store_true", help="write one for this commit")
    parser.add_argument("--recover", action="store_true", help="what a fresh agent needs")
    parser.add_argument("--check", action="store_true", help="refuse a tampered or leaky ledger")
    args = parser.parse_args()

    runs = load()
    if args.check:
        problems = broken_links(runs)
        for problem in problems:
            print(f"FAIL {problem}")
        if problems:
            print(f"\n{len(problems)} problem(s). The chain is evidence of editing, not of intent.")
            return 1
        print(f"{len(runs)} run(s), chain intact, no secret-shaped value on file.")
        return 0

    if args.recover:
        print(recovery_briefing(checkpoint()))
        return 0

    point = checkpoint()
    if args.checkpoint:
        CHECKPOINTS.parent.mkdir(parents=True, exist_ok=True)
        rows = [r for r in _read(CHECKPOINTS) if r.get("checkpoint_id") != point.checkpoint_id]
        rows.append(asdict(point))
        CHECKPOINTS.write_text(
            "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8"
        )
        print(f"wrote {point.checkpoint_id} to state/checkpoints.jsonl")
        return 0

    if not runs:
        print("No runs recorded. The ledger is empty, which is not the same as")
        print("no work having happened — it means nothing has been writing to it.")
    for run in runs:
        print(f"  {run.run_id}  {run.result:<10} {run.objective}")
    print()
    print(recovery_briefing(point))
    return 0


if __name__ == "__main__":
    sys.exit(main())
