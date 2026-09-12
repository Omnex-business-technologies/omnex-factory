"""Every GitHub Action this repository runs, pinned to a commit — never a tag.

    python scripts/actions_pin_check.py

## The attack this closes

`uses: actions/checkout@v7` is a promise the workflow file cannot keep: `v7` is
a ref the ACTION'S maintainer controls, not this repository. If that
maintainer's account is compromised — or the maintainer is coerced, which has
happened to real widely-used actions — `v7` can be moved to point at different
code with no change here at all. Every workflow in this repository would run
the new code on its next trigger, and nothing in this repository's own history
would show it happened. Pinning to a 40-character commit SHA closes exactly
this: a SHA is immutable by construction, so "controlled GitHub Actions" (the
operator's Sovereign Execution Standard, Phase 2) means this and nothing
weaker — a version tag is a claim about intent, a SHA is the thing itself.

## Why a comment survives the pin

Every pinned line here also carries `# vX.Y.Z` — not for this checker, which
never reads it, but for the next person deciding whether to take a new release:
`git log --oneline <old-sha>..<new-sha>` in the action's own repository is the
only way to review what changed, and a bare 40-character hex string gives
nobody a version to start from.

## What this does not check

Whether the currently-pinned commit is itself trustworthy. Pinning stops a
FUTURE substitution; it says nothing about the commit chosen today, which is
still a judgement call made by whoever wrote the pin. That judgement is
recorded in `docs/EXECUTION_DECISIONS.md`, not verified here.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import release_check  # noqa: E402

_USES = re.compile(r"uses:\s*([\w.\-/]+)@(\S+)")
#: A full, lower-case git commit SHA. GitHub accepts a short SHA in `uses:`,
#: but a short SHA can become ambiguous as a repository grows — the full form
#: is the only one that stays unambiguous forever.
_FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def find_uses(text: str) -> list[tuple[str, str]]:
    """Every `(action, ref)` pair in a workflow, comments stripped first.

    Reuses `release_check._uncommented` rather than a second comment-stripping
    reader — the exact drift `twin_splitters_agree` is named after, and the
    reason a workflow's own `#` comment once flipped a different check's
    verdict (see release_check.py's module docstring).
    """
    return [
        (action, ref)
        for line in text.splitlines()
        for match in [_USES.search(release_check._uncommented(line))]
        if match
        for action, ref in [(match.group(1), match.group(2))]
    ]


def unpinned(workflows: dict[str, str]) -> list[str]:
    """`file: action@ref` for every ref that is not a full commit SHA."""
    problems: list[str] = []
    for name, text in sorted(workflows.items()):
        for action, ref in find_uses(text):
            if not _FULL_SHA.match(ref):
                problems.append(f"{name}: {action}@{ref} is not pinned to a commit SHA")
    return problems


def summarise(workflows: dict[str, str]) -> dict[str, int]:
    total = sum(len(find_uses(text)) for text in workflows.values())
    bad = len(unpinned(workflows))
    return {"total_uses": total, "pinned_to_sha": total - bad, "unpinned": bad}


def main() -> int:
    workflows = release_check._workflow_text()
    problems = unpinned(workflows)
    summary = summarise(workflows)
    print(f"{summary['pinned_to_sha']} of {summary['total_uses']} actions pinned to a commit SHA")
    for problem in problems:
        print(f"  FAIL {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
