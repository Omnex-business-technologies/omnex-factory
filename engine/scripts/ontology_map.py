"""Verify the ontology against the code that is supposed to back it.

    python scripts/ontology_map.py

A coverage map is worth exactly as much as its weakest claim. Typed by hand, the
row "Agent Memory -> omnex.memory" stays green through the refactor that renamed
every symbol in it, and the map becomes a document about a repository that no
longer exists. So nothing here is typed: `ontology/branches.json` supplies the
CLAIM, this script imports every module and resolves every symbol to decide the
STATUS, and a branch that names something absent fails the run.

That is also why there is no completeness score. The proposal this map answers
scored each node n/10 on ten dimensions — but the system that writes a node
would also be the system that scores it, which is `harness/contract.py`'s frozen
criteria problem with the anchor removed. Two binary facts replace it, and
neither is ours to grade: the symbol imports, or it does not; the test file is
on disk, or it is not.

## The verdict answers a narrower question than it looks like

For every branch with something still to build, `omnex.harness.worth_it`
supplies a verdict. That gate is about LOOPS — its conditions are Karpathy's
(does the task recur, can a machine fail the work, will the budget absorb the
waste, can the agent see what breaks) and autoresearch's (goal, method,
assessment). So the question it answers is:

    should an autonomous loop OWN this branch?

"NOT worth it" here means *do not point a loop at it*. It has never meant *do
not build it*, and a reader who takes it that way has been misled by this script
rather than by the gate.

Failures are collected and reported together rather than raised at the first
one, for the reason CLAUDE.md gives: being refused repeatedly, one condition at
a time, is how somebody concludes the check is the obstacle.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from omnex.core.symbols import resolve
from omnex.harness.worth_it import Verdict, evaluate

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ontology" / "branches.json"
OUTPUT = ROOT / "ontology" / "COVERAGE.md"

#: A branch may cite a figure only by naming what produces it. Nothing in the
#: JSON is a number, because a literal typed there is right until the next run
#: on a different machine and then silently wrong forever.
PRODUCERS = ("scripts/skill_numbers.py", "suites/LEADERBOARD.md")

CLAIMS = ("implemented", "partial", "gap", "knowledge")

#: Where a branch came from. `proposal` means somebody wrote it down before
#: looking; `corpus:<name>` means it was read out of a source document. The
#: distinction is the whole reason version 2 exists: a map of an assumed list
#: can confirm every entry on it and still be missing the field, and "23 of 28
#: covered" says nothing at all when the 28 were never evidence.
SOURCE_PREFIXES = ("proposal", "corpus:")

WORTH_IT_KEYS = (
    "repeats_weekly",
    "verification_is_automated",
    "budget_absorbs_waste",
    "agent_has_tools",
    "has_goal_metric",
    "has_change_method",
    "has_standard_assessment",
)


@dataclass
class Branch:
    """One ontology branch and everything the JSON claims about it."""

    id: str
    name: str
    claim: str
    modules: list[str]
    symbols: list[str]
    tests: list[str]
    measured_by: str | None
    missing: list[str]
    note: str
    worth_it: dict[str, bool] | None
    source: str

    @property
    def has_work_left(self) -> bool:
        return bool(self.missing)

    @property
    def derived(self) -> bool:
        """Read out of a source document rather than assumed from a proposal."""
        return self.source.startswith("corpus:")


@dataclass
class Audit:
    """What the filesystem says, as opposed to what the JSON claims."""

    branch: Branch
    unresolved: list[str] = field(default_factory=list)
    absent_tests: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    verdict: Verdict | None = None

    @property
    def ok(self) -> bool:
        return not (self.unresolved or self.absent_tests or self.violations)


def version(path: Path = SOURCE) -> str:
    """The ontology's own version, read rather than restated.

    Printed by `main()`. A hardcoded literal here goes stale the first time the
    file is revised, and a run that reports the wrong version is worse than one
    that reports none.
    """
    raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return str(raw["ontology_version"])


def load(path: Path = SOURCE) -> list[Branch]:
    """Read the claims. Reading them is not believing them."""
    raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return [
        Branch(
            id=entry["id"],
            name=entry["name"],
            claim=entry["claim"],
            modules=entry["modules"],
            symbols=entry["symbols"],
            tests=entry["tests"],
            measured_by=entry["measured_by"],
            missing=entry["missing"],
            note=entry["note"],
            worth_it=entry["worth_it"],
            source=entry["source"],
        )
        for entry in raw["branches"]
    ]


def audit(branch: Branch, root: Path = ROOT) -> Audit:
    """Check a branch against the repository, collecting every failure."""
    result = Audit(branch=branch)

    for symbol in branch.symbols:
        reason = resolve(symbol)
        if reason is not None:
            result.unresolved.append(f"{symbol}: {reason}")

    result.absent_tests = [path for path in branch.tests if not (root / path).exists()]

    result.violations = list(_rule_violations(branch, root))

    if branch.has_work_left and branch.worth_it is not None:
        supplied = {key: branch.worth_it[key] for key in WORTH_IT_KEYS if key in branch.worth_it}
        if len(supplied) == len(WORTH_IT_KEYS):
            result.verdict = evaluate(**supplied)

    return result


def _rule_violations(branch: Branch, root: Path) -> list[str]:
    """The structural rules. Each is a refusal, not a score.

    `implemented` is the only claim that buys anything, so it is the only one
    with a price: at least one symbol that imports and at least one test file
    that exists. A branch cannot talk its way past either.
    """
    problems: list[str] = []

    if branch.claim not in CLAIMS:
        problems.append(f"claim {branch.claim!r} is not one of {CLAIMS}")

    if branch.claim in ("implemented", "partial"):
        if not branch.symbols:
            problems.append(f"claims {branch.claim!r} with no symbols to back it")
        if not branch.tests:
            problems.append(f"claims {branch.claim!r} with no tests to back it")

    if branch.claim == "implemented" and branch.missing:
        problems.append("claims 'implemented' while listing missing work")

    if branch.claim == "partial" and not branch.missing:
        problems.append("claims 'partial' without naming what is missing")

    if branch.claim in ("gap", "knowledge"):
        if branch.symbols:
            problems.append(f"claims {branch.claim!r} but cites symbols")
        if branch.tests:
            problems.append(f"claims {branch.claim!r} but cites tests")

    if branch.claim == "gap" and not branch.missing:
        problems.append("claims 'gap' without naming what is missing")

    if branch.claim == "knowledge" and branch.missing:
        problems.append("claims 'knowledge' but lists missing work — it is a gap, then")

    # Anything still to build must carry all seven answers, explicitly. This
    # mirrors `evaluate()` itself, which has no defaults because the condition
    # that would default to True is the one worth thinking about.
    if branch.has_work_left:
        if branch.worth_it is None:
            problems.append("has missing work but no worth_it verdict")
        else:
            absent = [key for key in WORTH_IT_KEYS if key not in branch.worth_it]
            if absent:
                problems.append(f"worth_it is missing answers: {', '.join(absent)}")
            extra = [key for key in branch.worth_it if key not in WORTH_IT_KEYS]
            if extra:
                problems.append(f"worth_it has unknown keys: {', '.join(extra)}")
    elif branch.worth_it is not None:
        problems.append("carries a worth_it verdict with no missing work to justify it")

    if branch.measured_by is not None:
        if branch.measured_by not in PRODUCERS:
            problems.append(f"measured_by {branch.measured_by!r} is not one of {PRODUCERS}")
        elif not (root / branch.measured_by).exists():
            problems.append(f"measured_by {branch.measured_by!r} does not exist")

    if not branch.note.strip():
        problems.append("has no note explaining its claim")

    if not branch.source.startswith(SOURCE_PREFIXES):
        problems.append(f"source {branch.source!r} does not say where the branch came from")

    return problems


def render(audits: list[Audit]) -> str:
    """Write COVERAGE.md from the audit, never from the claims alone."""
    counts = {claim: sum(a.branch.claim == claim for a in audits) for claim in CLAIMS}
    total = len(audits)
    backed = sum(1 for a in audits if a.branch.claim in ("implemented", "partial"))
    derived = [a for a in audits if a.branch.derived]

    lines = [
        "# Ontology coverage",
        "",
        "Generated by `scripts/ontology_map.py`. Do not edit — every row here is",
        "re-derived by importing the module and resolving the symbol, so editing this",
        "file changes nothing and editing `ontology/branches.json` to claim more makes",
        "the script fail.",
        "",
        f"**{backed} of {total} branches are backed by code that imports.** "
        f"{counts['implemented']} implemented · {counts['partial']} partial · "
        f"{counts['gap']} gap · {counts['knowledge']} reference-only.",
        "",
        f"**{len(derived)} of them were discovered rather than assumed.** The rest came "
        "from a proposal written before anyone looked at a source, and a map of an "
        "assumed list can confirm every entry on it while missing the field entirely — "
        "which is why `source` is a column and not a footnote.",
        "",
        "| # | Branch | Claim | Backed by | Measured by | Source |",
        "|---|---|---|---|---|---|",
    ]

    for entry in audits:
        branch = entry.branch
        modules = ", ".join(f"`{m}`" for m in branch.modules) or "—"
        measured = f"`{branch.measured_by}`" if branch.measured_by else "—"
        origin = "derived" if branch.derived else "proposal"
        lines.append(
            f"| {branch.id} | {branch.name} | {branch.claim} | {modules} | {measured} | {origin} |"
        )

    lines += [
        "",
        "## What is left, and whether a loop should own it",
        "",
        "Each verdict below comes from `omnex.harness.worth_it`, which gates **loops**.",
        "A refusal means *do not point an autonomous loop at this branch*. It does not",
        "mean the work is not worth doing by hand — that is a separate decision, taken",
        "per branch, and this file does not take it.",
        "",
    ]

    outstanding = [a for a in audits if a.branch.has_work_left]
    for entry in outstanding:
        branch = entry.branch
        lines.append(f"### {branch.id} · {branch.name} ({branch.claim})")
        lines.append("")
        lines.append(branch.note)
        lines.append("")
        for item in branch.missing:
            lines.append(f"- missing: {item}")
        lines.append("")
        if entry.verdict is not None:
            lines.append("```")
            lines.append(entry.verdict.report())
            lines.append("```")
            lines.append("")

    approved = [a for a in outstanding if a.verdict is not None and a.verdict.worth_it]
    lines += [
        "## Reading of the whole map",
        "",
        f"{len(outstanding)} branches have work left. "
        f"{len(approved)} of them {'passes' if len(approved) == 1 else 'pass'} "
        "all seven conditions for a loop to own.",
        "",
        "The condition that refuses most of them is `repeats`: a branch is built once,",
        "and a loop pointed at a one-off spends whether or not it ships. That is the",
        "finding, and it is about the machinery rather than about the branches — the",
        "same gate is what `harness` runs before any long-running loop starts.",
        "",
        f"The second finding is the count itself. Version 1 reported ten branches with "
        f"work left, against a list of twenty-eight nobody had checked against a source. "
        f"Reading one corpus added {len(derived)} more. That number is a property of how "
        "hard anyone has looked, not a property of the field, and it should be expected "
        "to rise with the next source rather than converge.",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    audits = [audit(branch) for branch in load()]

    failures = [entry for entry in audits if not entry.ok]
    for entry in failures:
        print(f"FAIL {entry.branch.id} · {entry.branch.name}")
        for problem in entry.violations:
            print(f"  rule: {problem}")
        for symbol in entry.unresolved:
            print(f"  unresolved: {symbol}")
        for path in entry.absent_tests:
            print(f"  absent test: {path}")

    if failures:
        print(f"\n{len(failures)} of {len(audits)} branches do not survive their own claim.")
        return 1

    OUTPUT.write_text(render(audits), encoding="utf-8")

    resolved = sum(len(entry.branch.symbols) for entry in audits)
    backed = sum(1 for entry in audits if entry.branch.claim in ("implemented", "partial"))
    outstanding = [entry for entry in audits if entry.branch.has_work_left]
    approved = [e for e in outstanding if e.verdict is not None and e.verdict.worth_it]

    print(f"ontology v{version()} — {len(audits)} branches, {resolved} symbols resolved")
    print(f"  backed by code       {backed}")
    print(f"  work left            {len(outstanding)}")
    print(f"  a loop should own    {len(approved)}")
    print(f"\nwrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
