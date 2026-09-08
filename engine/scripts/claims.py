"""What this repository asserts, what backs it, and what argues against it.

    python scripts/claims.py            # every claim with its derived status
    python scripts/claims.py --check    # refuse a registry that lies

`state_map.py` answers "where is execution". This answers the harder question
underneath it: **which of the things we say are actually true, how do we know,
and when did we last look.**

## Status is derived, never written

The hardening contract lists `status` among a claim's fields. It is not stored
here, and that is deliberate. A stored status is a typed status, and a typed
status is the one thing that must never be typeable — it would let anybody
promote a claim to SUPPORTED without producing the evidence that word means.

    evidence.jsonl → status() → the claim's state

Same argument `execution_state.json` already makes one level out. `--check`
recomputes every status and prints it; there is no field to disagree with.

## A claim is not SUPPORTED because evidence exists

Evidence has a **method**, and each kind of claim accepts only some methods.
"`omnex.mcp.McpClient` imports" is settled by importing it; it is not settled by
somebody writing that it does. `VERIFIES` is that mapping, and evidence whose
method is not in it counts toward nothing. Without this rule the registry
degrades into a table where writing a row is the same act as proving it.

## Contradiction is kept, never overwritten

Negative evidence is first-class and is never deleted. A later positive result
does not erase it — it must name it in `supersedes`, which leaves both in the
file and the reason visible. A registry that silently drops what disagreed with
it cannot answer the only question worth asking of it: what would change my mind.

So a claim carrying live contradiction is CONTRADICTED even when supporting
evidence also exists, and PARTIALLY_SUPPORTED only when the contradiction was
explicitly superseded and something is still missing.

## Absence is UNKNOWN, never FALSE

A claim with no evidence is UNKNOWN. `false` is a claim in its own right and
needs its own evidence. This is the rule the whole repository is built on, and
it is the one an optimiser under pressure reaches to break first, because
UNKNOWN blocks and FALSE lets you move on.

## Evidence goes stale

"LangGraph's API is X" was true against a version, on a date. `reverify_after`
(in days) and `source_version` make that explicit, and evidence past its window
stops counting — the claim falls back to STALE rather than staying green on a
measurement nobody has repeated. Evidence with no expiry is evidence about this
repository, which cannot change without a commit that would re-run the checker.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from enum import StrEnum
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
STATE = REPO / "state"
CLAIMS = STATE / "claims.jsonl"
EVIDENCE = STATE / "evidence.jsonl"


class Status(StrEnum):
    """The eight states a claim can be in. Never collapsed into a boolean.

    `CONTRADICTED` and `STALE` are the two most systems lack, and they are the
    two that matter: without them a registry can only say yes or nothing, and
    every disagreement or expiry has to be rounded to one of those.
    """

    DISCOVERED = "DISCOVERED"
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    UNKNOWN = "UNKNOWN"
    STALE = "STALE"
    SUPERSEDED = "SUPERSEDED"
    REJECTED = "REJECTED"


class Stance(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"


#: Claim type → the evidence methods that can settle it. A method outside this
#: set counts toward nothing, which is what stops "somebody wrote it down" from
#: being indistinguishable from "somebody checked".
#:
#: Deliberately small and literal. Every entry is a method this repository can
#: actually perform today; adding a type means adding the way it gets verified,
#: in the same commit, or the type is prose.
VERIFIES: dict[str, frozenset[str]] = {
    # A symbol exists and imports — settled by `omnex.core.symbols.resolve`.
    "symbol": frozenset({"import"}),
    # A behaviour holds — settled by a named test that must be green.
    "behaviour": frozenset({"test", "mutation"}),
    # A number — settled by the script that re-measures it, never by quoting.
    "measurement": frozenset({"script"}),
    # A property of a third-party package — needs the version it was read at.
    "external": frozenset({"package_read", "network_probe"}),
    # Something only a person can settle: a decision, a confirmation, an import
    # into n8n that actually worked.
    "human": frozenset({"person"}),
    # A property of the CI configuration — settled by reading the workflows.
    "pipeline": frozenset({"workflow_read", "ci_run"}),
}

#: Evidence about this repository does not expire on a clock: it cannot change
#: without a commit, and the commit re-runs the checker that produced it.
_SELF_EVIDENT = frozenset({"import", "test", "mutation", "script", "workflow_read"})


@dataclass(frozen=True)
class Evidence:
    """One observation, for or against a claim.

    `stance` is the field that makes negative evidence first-class rather than
    an absence. A registry that can only record support cannot distinguish
    "nobody looked" from "somebody looked and it was false".
    """

    evidence_id: str
    claim_id: str
    stance: Stance
    method: str
    observed_at: str
    detail: str
    source_version: str = ""
    environment: str = ""
    #: Days after `observed_at` this stops counting. 0 means it does not expire.
    reverify_after: int = 0
    #: The evidence id this one explicitly overrides. Never a deletion.
    supersedes: str = ""

    @property
    def observed(self) -> date:
        return date.fromisoformat(self.observed_at)

    def stale_on(self, today: date) -> bool:
        """Past its re-verification window. Self-evident methods never are."""
        if self.reverify_after <= 0 or self.method in _SELF_EVIDENT:
            return False
        return today > self.observed + timedelta(days=self.reverify_after)


@dataclass(frozen=True)
class Claim:
    """Something this repository asserts. Its status is computed, not stored."""

    claim_id: str
    claim: str
    type: str
    source: str
    #: Claim ids this one rests on. A dependency that is not SUPPORTED caps this
    #: one, because a conclusion cannot be firmer than what it stands on.
    dependencies: tuple[str, ...] = ()
    #: Set by a person, and the only way a claim leaves the evidence machinery.
    rejected_by: str = ""
    rejected_on: str = ""


@dataclass
class Registry:
    """Claims and evidence, joined. The only thing that computes a status."""

    claims: list[Claim] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)

    def for_claim(self, claim_id: str) -> list[Evidence]:
        return [e for e in self.evidence if e.claim_id == claim_id]

    def superseded(self) -> set[str]:
        """Evidence ids explicitly overridden by a later observation."""
        return {e.supersedes for e in self.evidence if e.supersedes}

    def status(self, claim: Claim, *, today: date | None = None) -> Status:
        """The claim's state, derived from its evidence every time it is asked.

        Order matters and is the argument itself: a human rejection outranks
        everything; live contradiction outranks support; absence is UNKNOWN and
        never FALSE; and a dependency that is not itself SUPPORTED caps this
        claim at PARTIALLY_SUPPORTED, because a conclusion cannot be firmer than
        what it rests on.
        """
        now = today or datetime.now(UTC).date()
        if claim.rejected_by:
            return Status.REJECTED

        gone = self.superseded()
        live = [e for e in self.for_claim(claim.claim_id) if e.evidence_id not in gone]
        if not live:
            # Distinguishing these two is the point. Evidence that existed and
            # was overridden is not the same as evidence that never existed.
            return Status.SUPERSEDED if self.for_claim(claim.claim_id) else Status.UNKNOWN

        usable = [e for e in live if e.method in VERIFIES.get(claim.type, frozenset())]
        if not usable:
            # Somebody wrote something down by a method that cannot settle this
            # kind of claim. That is a lead, not a verification.
            return Status.DISCOVERED

        against = [e for e in usable if e.stance is Stance.CONTRADICTS]
        if any(not e.stale_on(now) for e in against):
            return Status.CONTRADICTED

        supporting = [e for e in usable if e.stance is Stance.SUPPORTS]
        fresh = [e for e in supporting if not e.stale_on(now)]
        if not fresh:
            return Status.STALE if supporting else Status.UNKNOWN

        if any(self.status(d, today=now) is not Status.SUPPORTED for d in self._depends(claim)):
            return Status.PARTIALLY_SUPPORTED
        return Status.SUPPORTED

    def _depends(self, claim: Claim) -> list[Claim]:
        by_id = {c.claim_id: c for c in self.claims}
        return [by_id[d] for d in claim.dependencies if d in by_id]


def _read(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def load(claims: Path | None = None, evidence: Path | None = None) -> Registry:
    return Registry(
        claims=[
            Claim(
                claim_id=str(row["claim_id"]),
                claim=str(row["claim"]),
                type=str(row["type"]),
                source=str(row["source"]),
                dependencies=tuple(str(d) for d in row.get("dependencies", ()) or ()),  # type: ignore[union-attr]
                rejected_by=str(row.get("rejected_by", "")),
                rejected_on=str(row.get("rejected_on", "")),
            )
            for row in _read(claims or CLAIMS)
        ],
        evidence=[
            Evidence(
                evidence_id=str(row["evidence_id"]),
                claim_id=str(row["claim_id"]),
                stance=Stance(str(row["stance"])),
                method=str(row["method"]),
                observed_at=str(row["observed_at"]),
                detail=str(row["detail"]),
                source_version=str(row.get("source_version", "")),
                environment=str(row.get("environment", "")),
                reverify_after=int(row.get("reverify_after", 0)),  # type: ignore[arg-type]
                supersedes=str(row.get("supersedes", "")),
            )
            for row in _read(evidence or EVIDENCE)
        ],
    )


def problems(registry: Registry) -> list[str]:
    """Every way the registry is malformed, collected rather than raised."""
    found: list[str] = []
    ids = {c.claim_id for c in registry.claims}

    if len(ids) != len(registry.claims):
        found.append("duplicate claim_id — a claim addressed twice has two states")
    seen: set[str] = set()
    for e in registry.evidence:
        if e.evidence_id in seen:
            found.append(f"{e.evidence_id}: duplicate evidence_id")
        seen.add(e.evidence_id)
        if e.claim_id not in ids:
            found.append(f"{e.evidence_id}: evidence for unknown claim {e.claim_id}")
        if e.method not in {m for methods in VERIFIES.values() for m in methods}:
            found.append(f"{e.evidence_id}: method {e.method!r} is not one anything verifies with")
        if e.method in {"external", "package_read", "network_probe"} and not e.source_version:
            found.append(
                f"{e.evidence_id}: an observation about a third party with no "
                "source_version is not repeatable and cannot go stale"
            )
        if e.supersedes and e.supersedes not in seen | {x.evidence_id for x in registry.evidence}:
            found.append(f"{e.evidence_id}: supersedes {e.supersedes}, which is not on file")

    for claim in registry.claims:
        if claim.type not in VERIFIES:
            found.append(
                f"{claim.claim_id}: type {claim.type!r} has no verification method, "
                "so nothing could ever settle it"
            )
        for dependency in claim.dependencies:
            if dependency not in ids:
                found.append(f"{claim.claim_id}: depends on unknown claim {dependency}")
        if claim.rejected_by and not claim.rejected_on:
            found.append(f"{claim.claim_id}: rejected with no date")
    return found


def summarise(registry: Registry, *, today: date | None = None) -> dict[Status, int]:
    counts = dict.fromkeys(Status, 0)
    for claim in registry.claims:
        counts[registry.status(claim, today=today)] += 1
    return counts


def _render(registry: Registry, order: Iterable[Claim]) -> str:
    lines = []
    width = max((len(c.claim_id) for c in registry.claims), default=8)
    for claim in order:
        status = registry.status(claim)
        live = [
            e
            for e in registry.for_claim(claim.claim_id)
            if e.evidence_id not in registry.superseded()
        ]
        against = sum(1 for e in live if e.stance is Stance.CONTRADICTS)
        lines.append(
            f"  {claim.claim_id:<{width}}  {status.value:<20} "
            f"{len(live)} live evidence" + (f", {against} against" if against else "")
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="What this repository asserts, and what backs it.")
    parser.add_argument(
        "--check", action="store_true", help="exit non-zero on a malformed registry"
    )
    args = parser.parse_args()

    registry = load()
    if not registry.claims:
        print("No claims on file. That is an empty registry, not a clean one:")
        print("nothing here has been asserted, so nothing here has been checked.")
        return 0

    counts = summarise(registry)
    print(" · ".join(f"{n} {s.value}" for s, n in counts.items() if n))
    print()
    print(_render(registry, sorted(registry.claims, key=lambda c: c.claim_id)))

    broken = problems(registry)
    if broken:
        print()
        for problem in broken:
            print(f"FAIL {problem}")
        print(f"\n{len(broken)} problem(s) in the registry itself.")
        return 1
    if args.check:
        print("\nThe registry is well formed. Every status above was recomputed, not read.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
