"""An append-only, tamper-evident audit trail.

An audit log that can be edited is a log that proves nothing. The usual version
is a table of rows with timestamps, and anyone with write access — or any bug
with write access — can change a row, delete one, or reorder them, and nothing
about the log reveals it. For a system that takes actions on a customer's behalf
and needs to answer "who decided this, on what evidence", that is the whole
value gone.

So each entry carries the hash of the previous one. Changing any entry changes
its hash, which breaks every link after it, and `verify()` names the first
broken index. It does not *prevent* tampering — nothing in-process can — but it
makes tampering detectable, which is what "auditable" actually means.

Two properties that are easy to get wrong:

**The hash covers the sequence number and the previous hash, not just the
payload.** Hashing content alone lets two entries be swapped without breaking
anything, because each still hashes to what it did before.

**Entries are canonicalised before hashing.** `json.dumps` with sorted keys, so
a dict that round-trips through storage with a different key order still
verifies. Without this the chain breaks on the first restart and everyone learns
to ignore the warning.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from ..core.clock import Clock, SystemClock

__all__ = ["GENESIS", "AuditEntry", "AuditTrail"]

#: The hash the first entry links to. Fixed and public — its only job is to be
#: the same value every time so entry 0 can be verified like every other.
GENESIS = "0" * 64


def _canonical(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class AuditEntry:
    seq: int
    actor: str
    action: str
    payload: dict[str, Any]
    at: str
    previous_hash: str
    hash: str = ""

    def compute_hash(self) -> str:
        body = _canonical(
            {
                "seq": self.seq,
                "actor": self.actor,
                "action": self.action,
                "payload": self.payload,
                "at": self.at,
                "previous_hash": self.previous_hash,
            }
        )
        return hashlib.sha256(body.encode()).hexdigest()

    def as_dict(self) -> dict[str, Any]:
        return {
            "seq": self.seq,
            "actor": self.actor,
            "action": self.action,
            "payload": self.payload,
            "at": self.at,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }


@dataclass
class AuditTrail:
    """Append-only. There is deliberately no update or delete."""

    clock: Clock = field(default_factory=SystemClock)
    entries: list[AuditEntry] = field(default_factory=list)

    def record(self, actor: str, action: str, **payload: Any) -> AuditEntry:
        previous = self.entries[-1].hash if self.entries else GENESIS
        draft = AuditEntry(
            seq=len(self.entries),
            actor=actor,
            action=action,
            payload=dict(payload),
            at=self.clock.now().isoformat(),
            previous_hash=previous,
        )
        entry = AuditEntry(**{**draft.as_dict(), "hash": draft.compute_hash()})
        self.entries.append(entry)
        return entry

    def verify(self) -> tuple[bool, int | None, str]:
        """Check the chain. Returns (ok, first_broken_index, reason)."""
        previous = GENESIS
        for index, entry in enumerate(self.entries):
            if entry.seq != index:
                return False, index, f"sequence number {entry.seq} at position {index}"
            if entry.previous_hash != previous:
                return False, index, "previous hash does not match the entry before it"
            if entry.hash != entry.compute_hash():
                return False, index, "entry content does not match its own hash"
            previous = entry.hash
        return True, None, "chain intact"

    @property
    def head(self) -> str:
        """The current tip. Publishing this pins the whole history."""
        return self.entries[-1].hash if self.entries else GENESIS

    def by_actor(self, actor: str) -> list[AuditEntry]:
        return [e for e in self.entries if e.actor == actor]

    def render(self) -> str:
        ok, broken, reason = self.verify()
        lines = [f"audit trail: {len(self.entries)} entries, {reason}"]
        if not ok:
            lines.append(f"  FIRST BROKEN AT {broken}")
        for entry in self.entries:
            detail = ", ".join(f"{k}={v}" for k, v in sorted(entry.payload.items()))
            lines.append(f"  {entry.seq:>3} {entry.actor:<14} {entry.action:<20} {detail[:70]}")
        return "\n".join(lines)

    def to_jsonl(self) -> str:
        return "\n".join(_canonical(e.as_dict()) for e in self.entries)

    @classmethod
    def from_jsonl(cls, text: str, clock: Clock | None = None) -> AuditTrail:
        trail = cls(clock=clock or SystemClock())
        for line in text.splitlines():
            if line.strip():
                trail.entries.append(AuditEntry(**json.loads(line)))
        return trail
