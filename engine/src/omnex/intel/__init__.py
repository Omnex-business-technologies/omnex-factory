"""Opportunity intelligence — scanning the public ecosystem without inventing it.

An intelligence report written by a language model has one structural defect that
has nothing to do with how careful the model is: the output format has no slot
for provenance. "Project X uses SQLite" and "Project X probably uses SQLite"
render as the same sentence, so the reader cannot separate what was read from
what was pattern-matched. Both look like analysis.

This package gives provenance a slot and then enforces it.

    evidence.py   Claim = statement + Evidence. No evidence → renders UNKNOWN.
    snapshot.py   Ingest, and a filter that must account for every row it drops.
    growth.py     Velocity between snapshots. Confidence is COMPUTED from the
                  number of observations, so two points cannot be presented as
                  more than LOW no matter what the caller would prefer.
    sources.py    Registry adapters for the hosts this environment can reach.
    features.py   What projects CLAIM to do, capped at MEDIUM because a README
                  is evidence of a claim and not of an implementation.
    reverse.py    Architecture inferred from declared dependencies, each
                  inference carrying the manifest that produced it.
    gaps          features.CoverageMatrix.gaps() — the inverted feature matrix,
                  which is the half that says what to build.
    revenue.py    Opportunities priced in exact Money, ranked by payback.
    score.py      Two axes, opportunity and threat, never blended.
    report.py     Renders the documents, then verifies them against the evidence
                  and refuses sentences that are not supported.

The last line is the point of the whole package. The engine runs its own output
back through `omnex.rag.ground` — the same grounding verifier that decides
whether a RAG answer may be returned to a customer — so an intelligence document
is held to the standard we hold a product answer to.
"""

from .evidence import MAX_EXCERPT_CHARS, Artifact, Claim, Confidence, Evidence, EvidenceFile
from .features import TAXONOMY, CoverageMatrix, Feature, FeatureHit, Gap, mine
from .growth import HORIZONS, Projection, Velocity
from .report import Finding, Verification, render_claims, verify_document
from .revenue import BusinessModel, Complexity, Opportunity, Portfolio
from .reverse import SIGNATURES, ArchitectureReport, Layer, infer
from .score import Assessment, Score, ScoreInput, assess
from .snapshot import (
    DomainAssessment,
    DomainVerdict,
    FilterReport,
    NoiseFilter,
    Observation,
    Snapshot,
)
from .sources import (
    BLOCKED_HOSTS,
    CratesSource,
    DockerHubSource,
    NpmSource,
    PypiSource,
    Source,
    SourceUnavailable,
    fetch_all,
)

__all__ = [
    "BLOCKED_HOSTS",
    "HORIZONS",
    "MAX_EXCERPT_CHARS",
    "SIGNATURES",
    "TAXONOMY",
    "ArchitectureReport",
    "Artifact",
    "Assessment",
    "BusinessModel",
    "Claim",
    "Complexity",
    "Confidence",
    "CoverageMatrix",
    "CratesSource",
    "DockerHubSource",
    "DomainAssessment",
    "DomainVerdict",
    "Evidence",
    "EvidenceFile",
    "Feature",
    "FeatureHit",
    "FilterReport",
    "Finding",
    "Gap",
    "Layer",
    "NoiseFilter",
    "NpmSource",
    "Observation",
    "Opportunity",
    "Portfolio",
    "Projection",
    "PypiSource",
    "Score",
    "ScoreInput",
    "Snapshot",
    "Source",
    "SourceUnavailable",
    "Velocity",
    "Verification",
    "assess",
    "fetch_all",
    "infer",
    "mine",
    "render_claims",
    "verify_document",
]
