"""Snapshot ingestion, and the noise report nobody asks for but everybody needs.

A scraped corpus arrives looking like data. The snapshot that prompted this
module was 2,037 rows, of which 1,808 (90.3%) had zero stars, three accounts
contributed 16% of the file by themselves, and three of the five topic domains
came back with a maximum of 0, 8 and 1 stars respectively — meaning those three
queries returned nothing at all and any analysis of them is analysis of an empty
set.

None of that is visible from the row count, which is the entire problem. A
pipeline that silently filters to the interesting rows produces a report that
looks identical whether the scrape worked or failed. So:

**Nothing is dropped silently.** `FilterReport` itemises every removal by reason
and `reconciles()` asserts the arithmetic — kept plus removed equals input. A
filter that cannot account for what it discarded is a filter that will one day
discard the signal.

**A dead domain is reported as dead.** `DomainVerdict.UNUSABLE` is a first-class
outcome, not a small number. The next scrape will have this failure somewhere
else, and it needs to surface as a headline rather than as a thin table.

**Owner concentration is judged, not counted.** An account with 122 repositories
is either a spammer or the Apache Software Foundation. The rule that separates
them is whether any of those repositories has traction: high volume with a zero
median is generated noise, high volume with real stars is an organisation doing
real work. Counting alone would delete Meta and keep the bot farm.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from pathlib import Path

__all__ = [
    "DomainAssessment",
    "DomainVerdict",
    "FilterReport",
    "NoiseFilter",
    "Observation",
    "Snapshot",
]


@dataclass(frozen=True)
class Observation:
    """One project observed at one moment. The unit of every snapshot."""

    name: str
    stars: int
    observed_on: date
    domain: str = ""

    @property
    def owner(self) -> str:
        return self.name.split("/")[0] if "/" in self.name else self.name


class DomainVerdict(StrEnum):
    """Whether a domain's slice of a scrape can carry any conclusion at all."""

    USABLE = "usable"
    #: Real repositories, too few to generalise from. Reportable with a caveat.
    THIN = "thin"
    #: The query failed. No conclusion of any kind is available.
    UNUSABLE = "unusable"


@dataclass(frozen=True)
class DomainAssessment:
    domain: str
    total: int
    head: int
    max_stars: int
    verdict: DomainVerdict

    def report(self) -> str:
        return (
            f"{self.domain:<20} {self.total:>5} rows  {self.head:>3} above the floor  "
            f"max {self.max_stars:>6}★  {self.verdict.upper()}"
        )


@dataclass
class FilterReport:
    """Every row that went in, accounted for.

    `reconciles()` exists because the alternative is a pipeline that loses rows
    to an off-by-one in a comprehension and reports a clean-looking result.
    """

    received: int = 0
    kept: int = 0
    duplicates: int = 0
    below_floor: int = 0
    spam_owners: int = 0
    #: owner -> rows contributed, for the accounts that tripped the rule.
    flagged_owners: dict[str, int] = field(default_factory=dict)

    @property
    def removed(self) -> int:
        return self.duplicates + self.below_floor + self.spam_owners

    def reconciles(self) -> bool:
        return self.received == self.kept + self.removed

    def report(self) -> str:
        share = self.removed / self.received if self.received else 0.0
        lines = [
            f"{self.received} rows in, {self.kept} kept, {self.removed} removed ({share:.1%})",
            f"  {self.duplicates:>5} duplicate rows",
            f"  {self.below_floor:>5} below the traction floor",
            f"  {self.spam_owners:>5} from bulk-generated accounts",
        ]
        for owner, count in sorted(self.flagged_owners.items(), key=lambda kv: -kv[1]):
            lines.append(f"        {owner:<24} {count:>4} rows, no traction on any of them")
        return "\n".join(lines)


@dataclass(frozen=True)
class NoiseFilter:
    """What counts as signal. Every threshold is stated rather than implied."""

    #: Below this, a repository tells us nothing about the ecosystem. It may
    #: still be excellent — this measures attention, and says so.
    traction_floor: int = 100
    #: An account contributing more rows than this is examined, not condemned.
    owner_volume_threshold: int = 20
    #: ...and is only removed if none of its repositories cleared this. A real
    #: organisation with many repositories will clear it easily; a generated
    #: farm never does.
    owner_traction_threshold: int = 10

    def spam_owners(self, observations: list[Observation]) -> dict[str, int]:
        """Accounts with high volume and no traction anywhere in that volume."""
        by_owner: dict[str, list[Observation]] = defaultdict(list)
        for item in observations:
            by_owner[item.owner].append(item)

        flagged: dict[str, int] = {}
        for owner, rows in by_owner.items():
            if len(rows) <= self.owner_volume_threshold:
                continue
            if max(row.stars for row in rows) >= self.owner_traction_threshold:
                # Volume plus traction is an organisation, not a farm.
                continue
            flagged[owner] = len(rows)
        return flagged


@dataclass
class Snapshot:
    """One collection run. The engine compares snapshots; it never averages them."""

    observed_on: date
    observations: list[Observation] = field(default_factory=list)

    @classmethod
    def load_csv(cls, path: Path | str) -> Snapshot:
        """Read a scrape of the form `name,stars,collected_at,domain`."""
        rows: list[Observation] = []
        with Path(path).open(newline="", encoding="utf-8-sig") as handle:
            for record in csv.DictReader(handle):
                rows.append(
                    Observation(
                        name=record["name"].strip(),
                        stars=int(record["stars"]),
                        observed_on=date.fromisoformat(record["collected_at"].strip()),
                        domain=record.get("domain", "").strip(),
                    )
                )
        if not rows:
            raise ValueError(f"{path} contained no rows")

        dates = {row.observed_on for row in rows}
        if len(dates) > 1:
            raise ValueError(
                f"{path} mixes {len(dates)} collection dates; a snapshot is one moment — "
                "split it and compare the snapshots instead"
            )
        return cls(observed_on=next(iter(dates)), observations=rows)

    def __len__(self) -> int:
        return len(self.observations)

    def by_name(self) -> dict[str, Observation]:
        return {item.name: item for item in self.observations}

    def apply(self, noise: NoiseFilter | None = None) -> tuple[Snapshot, FilterReport]:
        """Filter to signal, and account for everything removed."""
        rule = noise or NoiseFilter()
        report = FilterReport(received=len(self.observations))

        seen: set[str] = set()
        deduped: list[Observation] = []
        for item in self.observations:
            if item.name in seen:
                report.duplicates += 1
                continue
            seen.add(item.name)
            deduped.append(item)

        flagged = rule.spam_owners(deduped)
        report.flagged_owners = flagged

        kept: list[Observation] = []
        for item in deduped:
            if item.owner in flagged:
                report.spam_owners += 1
                continue
            if item.stars < rule.traction_floor:
                report.below_floor += 1
                continue
            kept.append(item)

        report.kept = len(kept)
        if not report.reconciles():
            # Unreachable by construction; raised rather than asserted because
            # a filter that has lost count must never return a plausible result.
            raise RuntimeError(
                f"filter lost rows: {report.received} in, "
                f"{report.kept} kept + {report.removed} removed"
            )
        return Snapshot(observed_on=self.observed_on, observations=kept), report

    def assess_domains(self, noise: NoiseFilter | None = None) -> list[DomainAssessment]:
        """Which domains in this scrape can carry a conclusion, and which cannot."""
        rule = noise or NoiseFilter()
        by_domain: dict[str, list[Observation]] = defaultdict(list)
        for item in self.observations:
            by_domain[item.domain].append(item)

        out: list[DomainAssessment] = []
        for domain, rows in by_domain.items():
            head = sum(1 for row in rows if row.stars >= rule.traction_floor)
            top = max(row.stars for row in rows)
            if head == 0:
                # Not "a small result". The query returned nothing usable, and a
                # report that treats this as a thin section is misleading.
                verdict = DomainVerdict.UNUSABLE
            elif head < 5:
                verdict = DomainVerdict.THIN
            else:
                verdict = DomainVerdict.USABLE
            out.append(DomainAssessment(domain, len(rows), head, top, verdict))
        return sorted(out, key=lambda a: -a.total)

    def owner_concentration(self, top: int = 10) -> list[tuple[str, int]]:
        return Counter(item.owner for item in self.observations).most_common(top)

    def stars_total(self) -> int:
        return sum(item.stars for item in self.observations)
