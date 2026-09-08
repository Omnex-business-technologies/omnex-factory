"""Where each worker works, how results merge, what happens when two disagree.

This is the lesson a large real port paid for: agents fanned across one shared
workspace ran the same version-control commands and overwrote each other. The
run did not fail because the model was weak; it failed operationally, and the
fix was structural rather than a better prompt — forbid the unsafe commands,
give each group its own isolated tree.

Two agents writing the same file race. That is not a tuning problem and no
amount of instruction fixes it, so `Fleet.assign()` refuses to hand the same
writable path to two workers instead of trusting them to take turns.

Three questions have to be answered before any fan-out, and each is a field here
rather than an assumption:

    where does each worker work   → `Workspace.path`, unique per worker
    how do results merge          → `MergePolicy`
    what happens when two disagree → `DisagreementPolicy`

A plan without answers does not scale. It just fails faster.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import PurePosixPath

from ..core.errors import ValidationFailed

__all__ = ["DisagreementPolicy", "Fleet", "MergePolicy", "Workspace"]


class MergePolicy(StrEnum):
    """How independent results are combined."""

    #: Each worker owns disjoint files; the union is the result.
    DISJOINT_UNION = "disjoint_union"
    #: Results are proposals; a reviewer picks. Slower, safest for edits.
    REVIEWED = "reviewed"
    #: Last writer wins. Fast, and loses work — allowed only when stated.
    LAST_WRITE = "last_write"


class DisagreementPolicy(StrEnum):
    """What happens when two workers produce conflicting answers."""

    #: Stop and surface both. The honest default.
    ESCALATE = "escalate"
    #: Majority across workers, when there are enough of them to have one.
    MAJORITY = "majority"
    #: Re-run the conflicting slice with a fresh worker and compare again.
    RERUN = "rerun"


@dataclass(frozen=True)
class Workspace:
    """One worker's writable area."""

    worker: str
    path: PurePosixPath
    #: Paths the worker may read but must not write.
    readonly: frozenset[str] = frozenset()

    def conflicts_with(self, other: Workspace) -> bool:
        """True when either path contains the other — nesting is sharing."""
        a, b = self.path, other.path
        return a == b or a.is_relative_to(b) or b.is_relative_to(a)


@dataclass
class Fleet:
    """Workers, their workspaces, and the policies that govern the merge."""

    merge: MergePolicy = MergePolicy.REVIEWED
    on_disagreement: DisagreementPolicy = DisagreementPolicy.ESCALATE
    workspaces: dict[str, Workspace] = field(default_factory=dict)
    #: Commands no worker may run — the structural half of the fix.
    forbidden: frozenset[str] = frozenset({"git push", "git checkout", "git reset", "git clean"})

    def assign(self, worker: str, path: str, readonly: frozenset[str] = frozenset()) -> Workspace:
        """Give a worker its own tree, refusing any overlap with another's.

        Overlap includes nesting: a worker rooted at `/w/a` and another at
        `/w/a/b` are sharing, and the second will discover it by having its work
        deleted.
        """
        if worker in self.workspaces:
            raise ValidationFailed(f"worker {worker!r} already has a workspace")

        candidate = Workspace(worker=worker, path=PurePosixPath(path), readonly=readonly)
        for existing in self.workspaces.values():
            if candidate.conflicts_with(existing):
                raise ValidationFailed(
                    f"workspace {path!r} for {worker!r} overlaps {str(existing.path)!r} held "
                    f"by {existing.worker!r}; two workers writing one tree overwrite each "
                    "other, which no prompt prevents",
                    worker=worker,
                    conflicts_with=existing.worker,
                )
        self.workspaces[worker] = candidate
        return candidate

    def check_command(self, worker: str, command: str) -> None:
        """Refuse a command that reaches outside the worker's own tree."""
        if worker not in self.workspaces:
            raise ValidationFailed(f"{worker!r} has no workspace; assign one before it runs")
        lowered = command.strip().lower()
        for banned in self.forbidden:
            if lowered.startswith(banned):
                raise ValidationFailed(
                    f"{worker!r} may not run {banned!r} — shared version-control commands "
                    "are how parallel workers destroy each other's work",
                    worker=worker,
                    command=banned,
                )

    def ready(self) -> bool:
        """Have the three questions been answered for every worker?"""
        return bool(self.workspaces)

    def report(self) -> str:
        lines = [
            f"{len(self.workspaces)} worker(s) · merge {self.merge} · "
            f"disagreement {self.on_disagreement}"
        ]
        for workspace in sorted(self.workspaces.values(), key=lambda w: w.worker):
            lines.append(f"  {workspace.worker:<16} {workspace.path}")
        return "\n".join(lines)
