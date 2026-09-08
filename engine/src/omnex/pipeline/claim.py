"""Deliver once, across processes that share nothing but a directory.

`IdempotencyStore` remembers completed work in a dict, which is correct for a
worker that stays up and useless for the shape an n8n workflow actually has: a
node runs a command, the process exits, and the next delivery starts a new one
with an empty dict. Both storefronts retry — Lemon Squeezy and Etsy will send the
same order again on a timeout or a non-2xx — so an in-memory store there
deduplicates nothing at all, and the failure is a second GPU-built pack and one
buyer wondering why they were charged twice.

## The primitive, and why this one

`os.open(path, O_CREAT | O_EXCL)` succeeds for exactly one caller and raises
`FileExistsError` for every other, in one syscall, with no lock file, no daemon
and no dependency. Read-then-write would leave the window that matters open: two
retries arriving together both read "not seen", both write, both deliver.

## What it does not cover, stated rather than implied

One filesystem. Two n8n hosts with separate disks each claim once and each
deliver once, and no amount of care inside this file changes that — it is a
property of where the directory is, so it belongs in the deployment decision and
not in a comment somebody hopes gets read. NFS is the same warning: `O_EXCL` is
exactly as atomic as the mount underneath it.

A claim is written **before** the work, so a crash mid-delivery leaves the event
claimed and undelivered. That is the deliberate direction. The other one delivers
twice on a crash, and of the two failures a customer notices the double charge.
`release()` exists for a caller that has decided its failure was transient and
wants the retry to land; nothing calls it automatically, because "the work
failed, so it is safe to run again" is a judgement about the work.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from ..core.clock import Clock, SystemClock
from ..core.errors import ValidationFailed

__all__ = ["Claimed", "Claims"]

#: Event ids come from a sender. A path separator in one would write outside the
#: store, so the id is hashed into the filename and kept verbatim inside the file.
_SAFE = re.compile(r"[^A-Za-z0-9._-]")


@dataclass(frozen=True)
class Claimed:
    """The outcome of one attempt to claim an event."""

    event_id: str
    #: True when THIS caller claimed it. False means somebody already had it.
    first: bool
    path: Path
    claimed_at: str = ""


@dataclass
class Claims:
    """A directory of claimed event ids, one file each."""

    directory: Path
    clock: Clock = field(default_factory=SystemClock)

    def _path(self, event_id: str) -> Path:
        safe = _SAFE.sub("-", event_id)[:64]
        digest = hashlib.sha256(event_id.encode()).hexdigest()[:16]
        return self.directory / f"{safe}.{digest}.json"

    def claim(self, event_id: str) -> Claimed:
        """Claim an event, or report that somebody else already did.

        Never raises on a duplicate: a redelivery is the normal case, not an
        error, and a caller that has to catch an exception to handle the common
        path writes a `try` around its whole workflow.
        """
        if not event_id:
            raise ValidationFailed(
                "an empty event id cannot be claimed — without the sender's own id "
                "there is no safe key, and a body hash would collapse two genuinely "
                "distinct events into one"
            )
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self._path(event_id)
        stamp = self.clock.now().isoformat()
        record = json.dumps({"event_id": event_id, "claimed_at": stamp}).encode()

        try:
            handle = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            return Claimed(event_id=event_id, first=False, path=path, claimed_at=_when(path))
        try:
            os.write(handle, record)
        finally:
            os.close(handle)
        return Claimed(event_id=event_id, first=True, path=path, claimed_at=stamp)

    def release(self, event_id: str) -> bool:
        """Un-claim, so a retry of genuinely failed work can land.

        Only a caller that knows its failure was transient may call this. A
        release after a delivery that partly succeeded is how one order ships
        twice.
        """
        path = self._path(event_id)
        if not path.exists():
            return False
        path.unlink()
        return True

    def seen(self, event_id: str) -> bool:
        return self._path(event_id).exists()


def _when(path: Path) -> str:
    try:
        return str(json.loads(path.read_text(encoding="utf-8")).get("claimed_at", ""))
    except (OSError, json.JSONDecodeError):
        # A claim whose record is unreadable is still a claim. The file's
        # existence is the fact; its contents are for whoever reads the directory.
        return ""
