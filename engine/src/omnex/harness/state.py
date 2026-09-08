"""The log of what was tried, so the next run does not try it again.

State is what turns repetition into progress. Without it a loop repeats the same
mistake every cycle, and the second hour costs exactly what the first did.

Each recorded attempt carves a piece out of the search space. A project's own
log of failures and successes is what lets the next run skip roughly everything
already ruled out — which is why the cycle time falls run over run rather than
staying flat, and why the log is worth more than any single result in it.

## JSON, on disk, not in the context window

Two reasons, both observed rather than assumed.

Models overwrite markdown files and leave JSON alone. That is a strange fact and
it is a load-bearing one: progress written as prose gets rewritten by the next
agent that decides to tidy up, and the record of what failed disappears exactly
when it is most valuable.

And a compacted context is a lossy summary. Compaction is not coherence — the
details that drift out first are the specific ones, and "we tried X and it broke
Y" is nothing but specifics. The file survives a fresh context; a summary does
not survive itself.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from ..core.clock import Clock, SystemClock

__all__ = ["Attempt", "RunState"]


@dataclass(frozen=True)
class Attempt:
    """One thing that was tried, and what came of it."""

    criterion: str
    #: What was changed. Short — this is an index, not a diff store.
    change: str
    accepted: bool
    #: Why it failed, when it did. The part the next run needs most.
    reason: str = ""
    cost_picos: int = 0
    at: str = ""

    @property
    def signature(self) -> str:
        """Identifies the attempt, so a repeat is recognisable."""
        return f"{self.criterion}::{self.change.strip().lower()}"


@dataclass
class RunState:
    """Durable progress for one harness run."""

    goal: str
    contract_fingerprint: str = ""
    attempts: list[Attempt] = field(default_factory=list)
    clock: Clock = field(default_factory=SystemClock)

    # ── recording ─────────────────────────────────────────────────────────
    def record(
        self, criterion: str, change: str, accepted: bool, reason: str = "", cost_picos: int = 0
    ) -> Attempt:
        attempt = Attempt(
            criterion=criterion,
            change=change,
            accepted=accepted,
            reason=reason,
            cost_picos=cost_picos,
            at=self.clock.now().isoformat(),
        )
        self.attempts.append(attempt)
        return attempt

    # ── what the next pass should skip ────────────────────────────────────
    def already_tried(self, criterion: str, change: str) -> Attempt | None:
        """The prior attempt at this exact change, if there was one."""
        wanted = f"{criterion}::{change.strip().lower()}"
        return next((a for a in reversed(self.attempts) if a.signature == wanted), None)

    def ruled_out(self, criterion: str) -> tuple[str, ...]:
        """Changes already shown not to work for a criterion.

        Handed to the next pass so it spends its budget on the part of the space
        nobody has looked at.
        """
        return tuple(a.change for a in self.attempts if a.criterion == criterion and not a.accepted)

    def accepted_for(self, criterion: str) -> tuple[Attempt, ...]:
        return tuple(a for a in self.attempts if a.criterion == criterion and a.accepted)

    def stuck_on(self, criterion: str, threshold: int = 3) -> bool:
        """Consecutive failures on one criterion with nothing accepted since.

        The signal to throw the attempt away and start it differently rather
        than patch it again — the behaviour a solo loop lacks, because a solo
        loop can only ever try the next small fix.
        """
        streak = 0
        for attempt in reversed(self.attempts):
            if attempt.criterion != criterion:
                continue
            if attempt.accepted:
                return False
            streak += 1
            if streak >= threshold:
                return True
        return False

    # ── persistence ───────────────────────────────────────────────────────
    def as_dict(self) -> dict[str, object]:
        return {
            "goal": self.goal,
            "contract_fingerprint": self.contract_fingerprint,
            "attempts": [asdict(a) for a in self.attempts],
        }

    def save(self, path: Path | str) -> Path:
        """Write atomically — a half-written progress file is worse than none.

        A crash mid-write otherwise leaves JSON that will not parse, and the
        next run starts from zero having lost the whole log.
        """
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_text(json.dumps(self.as_dict(), indent=2, sort_keys=True) + "\n")
        temporary.replace(target)
        return target

    @classmethod
    def load(cls, path: Path | str, clock: Clock | None = None) -> RunState:
        payload = json.loads(Path(path).read_text())
        raw = payload.get("attempts", [])
        attempts = [
            Attempt(
                criterion=str(item["criterion"]),
                change=str(item["change"]),
                accepted=bool(item["accepted"]),
                reason=str(item.get("reason", "")),
                cost_picos=int(item.get("cost_picos", 0)),
                at=str(item.get("at", "")),
            )
            for item in raw
            if isinstance(item, dict)
        ]
        return cls(
            goal=str(payload.get("goal", "")),
            contract_fingerprint=str(payload.get("contract_fingerprint", "")),
            attempts=attempts,
            clock=clock or SystemClock(),
        )

    def report(self) -> str:
        accepted = sum(1 for a in self.attempts if a.accepted)
        return (
            f"{self.goal}: {len(self.attempts)} attempts, {accepted} accepted, "
            f"{len(self.attempts) - accepted} ruled out"
        )
