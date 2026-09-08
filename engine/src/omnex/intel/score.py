"""Scoring that can be argued with.

A priority score is a number that reorders someone's quarter. Presented bare it
is unfalsifiable — a reader who disagrees has nothing to disagree *with*, so they
either accept it or discard the whole analysis. Both outcomes are bad, and the
second is the common one.

So a `Score` carries its inputs. Every axis keeps the value, the weight and a
one-line rationale, and `explain()` prints the arithmetic. A reader who thinks
integration cost was underrated can see it was 0.3 at weight 2 and say so. That
turns the score into the start of a conversation instead of the end of one.

## Two axes, not one ranking

`opportunity` and `threat` are computed separately and never combined, because
they answer different questions and a single ranking conflates them. A
fast-growing project we cannot absorb (wrong licence, wrong language, direct
substitute for what we sell) scores near zero on opportunity and near the top on
threat — and it is the most important row in the report. A blended score would
place it mid-table, which is precisely where nobody reads.
"""

from __future__ import annotations

from dataclasses import dataclass

from .evidence import Artifact, Confidence
from .growth import Velocity

__all__ = ["Assessment", "Score", "ScoreInput", "assess"]


@dataclass(frozen=True)
class ScoreInput:
    """One axis: what it measured, how much it counted, and why."""

    name: str
    #: Normalised 0.0–1.0. Anything outside is a bug in the caller, not a strong opinion.
    value: float
    weight: float
    rationale: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"{self.name} scored {self.value}, outside 0.0–1.0")
        if self.weight <= 0:
            raise ValueError(f"{self.name} has weight {self.weight}; a zero-weight axis is noise")

    @property
    def contribution(self) -> float:
        return self.value * self.weight


@dataclass(frozen=True)
class Score:
    subject: str
    inputs: tuple[ScoreInput, ...]
    #: The weakest evidence behind any input. A score built on rumour is a
    #: rumour with a decimal point, and this is where that shows.
    confidence: Confidence = Confidence.LOW

    @property
    def total(self) -> float:
        """Weighted mean, on 0–100."""
        weight = sum(item.weight for item in self.inputs)
        if not weight:
            return 0.0
        return 100.0 * sum(item.contribution for item in self.inputs) / weight

    def explain(self) -> str:
        lines = [f"{self.subject}: {self.total:.1f}/100 ({self.confidence} confidence)"]
        for item in sorted(self.inputs, key=lambda i: -i.contribution):
            lines.append(
                f"  {item.name:<22} {item.value:.2f} x{item.weight:g}  "
                f"→ {item.contribution:5.2f}   {item.rationale}"
            )
        return "\n".join(lines)


@dataclass(frozen=True)
class Assessment:
    """Both verdicts on one project, kept apart on purpose."""

    artifact: Artifact
    opportunity: Score
    threat: Score
    velocity: Velocity | None = None

    @property
    def headline(self) -> str:
        if self.threat.total > self.opportunity.total + 15:
            return "COMPETITOR — track, do not absorb"
        if self.opportunity.total >= 60:
            return "ABSORB — high value, integrable"
        if self.opportunity.total >= 40:
            return "WATCH — worth a second pass"
        return "PASS"

    def report(self) -> str:
        return (
            f"{self.artifact.name:<44} opportunity {self.opportunity.total:5.1f}  "
            f"threat {self.threat.total:5.1f}  {self.headline}"
        )


def _velocity_value(velocity: Velocity | None) -> tuple[float, str]:
    """Growth normalised to 0–1, with the rationale that produced it.

    Capped at +50% over the window: past that the difference between a very fast
    project and an extremely fast one stops changing what we would do about it,
    and letting one viral repository dominate an entire ranking is how a scoring
    system becomes a popularity contest with extra steps.
    """
    if velocity is None:
        return 0.0, "no second observation — growth unmeasured"
    if velocity.stalled:
        return 0.1, f"stalled at {velocity.relative_change:+.1%} over {velocity.days}d"
    normalised = max(0.0, min(1.0, velocity.relative_change / 0.5))
    return normalised, f"{velocity.relative_change:+.1%} over {velocity.days}d"


def assess(
    artifact: Artifact,
    velocity: Velocity | None,
    relevance: float,
    relevance_note: str,
    integration_cost: float,
    substitutes_our_product: float = 0.0,
) -> Assessment:
    """Score one project on both axes.

    `relevance` and `integration_cost` are judgements, supplied by the caller
    with a note, not computed here — pretending to derive them from a star count
    would be the exact failure this module exists to prevent. What the module
    guarantees is that they are recorded, weighted visibly, and printable.
    """
    growth_value, growth_note = _velocity_value(velocity)
    licence_value = 1.0 if artifact.absorbable else 0.0
    licence_note = (
        f"{artifact.licence} — permissive"
        if artifact.absorbable
        else f"{artifact.licence or 'no licence stated'} — cannot build on it"
    )

    opportunity = Score(
        subject=f"{artifact.name} · opportunity",
        inputs=(
            ScoreInput("omnex_relevance", relevance, 3.0, relevance_note),
            ScoreInput("licence_absorbable", licence_value, 2.5, licence_note),
            ScoreInput("integration_ease", 1.0 - integration_cost, 2.0, "inverse of build effort"),
            ScoreInput("growth", growth_value, 1.5, growth_note),
        ),
        confidence=min(
            (item.confidence for item in artifact.evidence),
            default=Confidence.NONE,
        ),
    )

    threat = Score(
        subject=f"{artifact.name} · threat",
        inputs=(
            ScoreInput("substitutes_us", substitutes_our_product, 3.0, "overlap with what we sell"),
            ScoreInput("growth", growth_value, 2.5, growth_note),
            ScoreInput(
                "distribution",
                min(1.0, artifact.popularity / 5000),
                1.5,
                f"{artifact.popularity:,} {artifact.popularity_kind}",
            ),
        ),
        confidence=min(
            (item.confidence for item in artifact.evidence),
            default=Confidence.NONE,
        ),
    )

    return Assessment(artifact=artifact, opportunity=opportunity, threat=threat, velocity=velocity)
