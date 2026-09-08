"""Move a decision from the queue into the record — and refuse the five ways it lies.

    python scripts/apply_decisions.py --dry-run    # what would change
    python scripts/apply_decisions.py              # write it

`node_dossier.py` writes `DECISIONS.md`: 507 rows, each with the evidence and a
heuristic recommendation, and three empty columns at the end. This reads the rows
somebody filled in and writes them into `nodes.json`.

It is the only thing in this repository allowed to set `verified`. That is the
whole design: `0 implemented` is worth reading precisely because no machine can
raise it, and a script that could would turn the number into decoration.

## What it refuses, and why each one matters

**A decision with no reviewer.** An anonymous confirmation is indistinguishable
from a generated one. The name is the evidence that a person looked.

**A machine-shaped reviewer.** `claude`, `agent`, `bot`, `assistant`, `ai` and
friends are refused by name. A person genuinely called Claude gives a fuller
identifying name — the cost is one inconvenience, and the alternative is that the
one number a machine may not raise becomes one it can.

**`implemented` for an alias that does not import.** "This symbol IS this
capability" is not a claim anybody can make about a symbol that is not there.
Checked through `omnex.core.symbols.resolve` — the one resolver, not a second
copy.

**Changing somebody else's confirmed decision.** A confirmation is immutable
unless a revision is explicit: `--revise` plus a reason, and the previous
reviewer and date are kept in the note rather than overwritten. A decision that
can be quietly reversed is not a decision.

**A date in the future, or not a date.** Injected `Clock`, like everything else
here, so the check is testable without waiting.

Every problem is reported at once. Being refused one row at a time is how
somebody concludes the queue is the obstacle rather than the work.

## Where provenance lives

In the node's existing `note`, as `<decision> by <reviewer> on <date>`, optionally
followed by a reason. No schema change: `nodes.json` is read and written by
`node_map.load`/`save`, and adding a field here would mean two writers with
different ideas of the shape.

## `deferred` does not confirm anything

It records that somebody looked and chose not to rule, with a reason. `claim` and
`verified` are untouched, because deferring is the opposite of confirming and
collapsing the two would inflate the only count that matters.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
QUEUE = REPO / "corpus" / "universal-ai-os" / "DECISIONS.md"
sys.path.insert(0, str(ROOT / "src"))

from node_map import Node, load, save  # noqa: E402

from omnex.core.symbols import resolve  # noqa: E402

DECISIONS = ("implemented", "rejected", "deferred")

#: Reviewer names that are not a person. Refused by name because the rule this
#: script exists to hold is "a machine may not confirm", and a machine that can
#: write a reviewer field can defeat it in one line.
NOT_A_PERSON = {
    "agent",
    "ai",
    "assistant",
    "auto",
    "automation",
    "bot",
    "chatgpt",
    "claude",
    "codex",
    "copilot",
    "gpt",
    "llm",
    "machine",
    "model",
    "n/a",
    "none",
    "opus",
    "script",
    "system",
    "tbd",
    "unknown",
}

#: `<decision> by <reviewer> on <date>`, optionally ` — <reason>`. Kept in the
#: node's existing `note` so `nodes.json` keeps one writer and one shape.
_PROVENANCE = re.compile(
    r"^(?P<decision>implemented|rejected|deferred) by (?P<reviewer>.+?) "
    r"on (?P<date>\d{4}-\d{2}-\d{2})(?: — (?P<reason>.*))?$"
)


@dataclass(frozen=True)
class Ruling:
    """One row somebody filled in."""

    branch: str
    node: str
    decision: str
    reviewer: str
    when: str
    reason: str = ""

    def note(self) -> str:
        base = f"{self.decision} by {self.reviewer} on {self.when}"
        return f"{base} — {self.reason}" if self.reason else base


def existing(note: str) -> Ruling | None:
    """The confirmed decision already on a node, if its note carries one."""
    found = _PROVENANCE.match(note.strip())
    if found is None:
        return None
    return Ruling(
        branch="",
        node="",
        decision=found["decision"],
        reviewer=found["reviewer"],
        when=found["date"],
        reason=found["reason"] or "",
    )


def read_queue(text: str) -> list[Ruling]:
    """Every row with something in the decision column. Empty rows are not rulings."""
    rulings: list[Ruling] = []
    for line in text.splitlines():
        if line.count("|") != 13 or line.startswith("| branch |") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        branch, node = cells[0], cells[1]
        decision, reviewer, when = cells[9], cells[10], cells[11]
        if not (decision or reviewer or when):
            continue
        rulings.append(
            Ruling(
                branch=branch,
                node=node,
                decision=decision.lower(),
                reviewer=reviewer,
                when=when,
            )
        )
    return rulings


def refusals(
    rulings: list[Ruling],
    nodes: list[Node],
    *,
    today: date | None = None,
    revising: bool = False,
) -> list[str]:
    """Every reason a ruling may not be applied, collected rather than raised."""
    now = today or datetime.now(UTC).date()
    by_key = {(n.branch, n.name): n for n in nodes}
    problems: list[str] = []

    for ruling in rulings:
        where = f"{ruling.branch}/{ruling.node}"
        node = by_key.get((ruling.branch, ruling.node))
        if node is None:
            problems.append(f"{where}: no such node in nodes.json")
            continue

        if ruling.decision not in DECISIONS:
            problems.append(
                f"{where}: decision {ruling.decision!r} is not one of {', '.join(DECISIONS)}"
            )
        if not ruling.reviewer:
            problems.append(
                f"{where}: no reviewer — an anonymous confirmation is "
                "indistinguishable from a generated one"
            )
        elif ruling.reviewer.strip().lower() in NOT_A_PERSON:
            problems.append(
                f"{where}: reviewer {ruling.reviewer!r} is not a person. A machine may "
                "not confirm; if that is your name, give a fuller identifying one"
            )

        problems.extend(_date_problems(where, ruling.when, now))

        if ruling.decision == "implemented":
            if not node.alias:
                problems.append(
                    f"{where}: implemented with no alias — there is no symbol to agree about"
                )
            elif (reason := resolve(node.alias)) is not None:
                problems.append(
                    f"{where}: implemented, but {node.alias} does not import ({reason})"
                )

        prior = existing(node.note)
        if prior and node.verified and not revising:
            problems.append(
                f"{where}: already {prior.decision} by {prior.reviewer} on {prior.when}. "
                "A confirmation is immutable; pass --revise with a reason to change it"
            )
        if revising and prior and not ruling.reason:
            problems.append(f"{where}: --revise needs a reason for overturning {prior.reviewer}")

    return problems


def _date_problems(where: str, when: str, now: date) -> list[str]:
    if not when:
        return [f"{where}: no date"]
    try:
        given = date.fromisoformat(when)
    except ValueError:
        return [f"{where}: date {when!r} is not YYYY-MM-DD"]
    if given > now:
        return [f"{where}: dated {when}, which is in the future"]
    return []


def apply(rulings: list[Ruling], nodes: list[Node]) -> list[str]:
    """Write the rulings onto the nodes. Only reached once nothing was refused."""
    by_key = {(n.branch, n.name): n for n in nodes}
    changed: list[str] = []
    for ruling in rulings:
        node = by_key[(ruling.branch, ruling.node)]
        prior = existing(node.note)
        note = ruling.note()
        if prior:
            # The overturned decision stays visible. A revision that erased what
            # it replaced would leave no way to see that anybody disagreed.
            note = f"{note} (was: {prior.decision} by {prior.reviewer} on {prior.when})"

        if ruling.decision == "deferred":
            # Deferring is the opposite of confirming. `claim` and `verified` are
            # untouched, or the one count that matters would include people who
            # explicitly declined to rule.
            node.note = note
            changed.append(f"{ruling.branch}/{ruling.node}: deferred (claim unchanged)")
            continue

        node.claim = ruling.decision
        node.verified = True
        node.note = note
        changed.append(f"{ruling.branch}/{ruling.node}: {ruling.decision} by {ruling.reviewer}")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply filled rows from DECISIONS.md.")
    parser.add_argument("--dry-run", action="store_true", help="report, write nothing")
    parser.add_argument(
        "--revise",
        action="store_true",
        help="allow overturning a confirmed decision; each needs a reason",
    )
    args = parser.parse_args()

    nodes = load()
    rulings = read_queue(QUEUE.read_text(encoding="utf-8"))
    confirmed = sum(1 for n in nodes if n.verified)

    if not rulings:
        print(f"No rows in DECISIONS.md carry a decision. {confirmed} node(s) confirmed.")
        print(
            "\nThat is the honest state, not a failure: 507 rows are waiting for a "
            "person, and nothing here may fill one in."
        )
        return 0

    problems = refusals(rulings, nodes, revising=args.revise)
    if problems:
        print(f"FAIL {len(problems)} ruling(s) refused:")
        for problem in problems:
            print(f"  {problem}")
        return 1

    changed = apply(rulings, nodes)
    print(f"{len(changed)} ruling(s) {'would be' if args.dry_run else ''} applied:")
    for line in changed:
        print(f"  {line}")

    if args.dry_run:
        print("\nNothing written. Re-run without --dry-run to record these.")
        return 0

    save(nodes)
    print(f"\nwrote ontology/nodes.json — {sum(1 for n in nodes if n.verified)} node(s) confirmed")
    print("Re-run node_dossier.py and state_map.py so the derived views follow.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
