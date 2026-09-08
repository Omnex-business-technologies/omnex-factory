"""Opportunity intelligence — the properties that stop a report being fiction.

An intelligence document is read once, acted on, and rarely re-derived. That
makes it the worst possible place for a quiet error: nobody downstream will
notice, and the decision it changed is already made. So these tests target the
failures that would be invisible in the finished document.

The scan runs against the committed snapshot at `intel/snapshots/`, not a
synthetic fixture, because the interesting behaviour here — 90% noise, three dead
domains, six bulk-generated accounts — is a property of real scrapes that a
hand-written fixture would flatter.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from omnex.core.money import Money
from omnex.intel import (
    Artifact,
    Claim,
    Confidence,
    CoverageMatrix,
    DomainVerdict,
    Evidence,
    EvidenceFile,
    NoiseFilter,
    Observation,
    Snapshot,
    Velocity,
    assess,
    infer,
    mine,
    verify_document,
)
from omnex.intel.evidence import MAX_EXCERPT_CHARS
from omnex.intel.revenue import BusinessModel, Complexity, Opportunity, Portfolio

SNAPSHOT = Path(__file__).resolve().parents[2] / "intel" / "snapshots" / "metrics_20260515.csv"


@pytest.fixture(scope="module")
def snapshot() -> Snapshot:
    return Snapshot.load_csv(SNAPSHOT)


# ── the filter must account for everything ────────────────────────────────


def test_the_filter_accounts_for_every_row_it_removed(snapshot: Snapshot) -> None:
    """A filter that cannot say what it dropped will one day drop the signal.

    `apply()` raises rather than returning if the arithmetic fails, so this
    asserts the accounting is actually exercised on real data rather than
    trusting the guard to have been reached.
    """
    signal, report = snapshot.apply()

    assert report.received == len(snapshot)
    assert report.kept == len(signal)
    assert report.reconciles()
    assert report.kept + report.removed == report.received


def test_the_real_scrape_is_overwhelmingly_noise(snapshot: Snapshot) -> None:
    """The headline finding, pinned so a future filter change cannot hide it."""
    signal, report = snapshot.apply()

    assert report.received == 2037
    assert len(signal) == 70
    # The 3.5% that survives holds essentially all of the attention.
    assert signal.stars_total() / snapshot.stars_total() > 0.99


def test_bulk_generated_accounts_are_removed_but_real_organisations_are_not() -> None:
    """Volume alone would delete Meta and keep the bot farm.

    The rule is volume AND no traction anywhere in that volume. This builds both
    shapes explicitly, because getting it backwards is silent — the report simply
    stops mentioning the most credible publishers in the ecosystem.
    """
    when = date(2026, 5, 15)
    farm = [Observation(f"botfarm/repo-{i}", 0, when, "AI Agent") for i in range(50)]
    org = [Observation(f"bigorg/project-{i}", 500, when, "AI Agent") for i in range(50)]

    flagged = NoiseFilter().spam_owners(farm + org)

    assert "botfarm" in flagged
    assert "bigorg" not in flagged


def test_the_six_flagged_owners_are_reported_by_name(snapshot: Snapshot) -> None:
    """Naming them is the point — an unnamed count cannot be argued with."""
    _, report = snapshot.apply()

    assert set(report.flagged_owners) >= {"vmoebriiha", "openclaw-mcp-vps", "snighsbwang"}
    assert sum(report.flagged_owners.values()) == report.spam_owners


# ── a dead domain is reported as dead ─────────────────────────────────────


def test_the_three_failed_domain_queries_are_reported_unusable(snapshot: Snapshot) -> None:
    """Long Context, Multi-modal and Speculative Model returned nothing usable.

    Their maxima are 0, 8 and 1 stars. Presenting those as thin sections rather
    than as failed queries is how a report describes an empty set with a
    straight face — and the next scrape will fail somewhere else.
    """
    verdicts = {a.domain: a for a in snapshot.assess_domains()}

    assert verdicts["Long Context"].verdict is DomainVerdict.UNUSABLE
    assert verdicts["Long Context"].max_stars == 0
    assert verdicts["Multi-modal"].verdict is DomainVerdict.UNUSABLE
    assert verdicts["Speculative Model"].verdict is DomainVerdict.UNUSABLE

    assert verdicts["AI Agent"].verdict is DomainVerdict.USABLE
    # Two repos above the floor is real but not generalisable, and says so.
    assert verdicts["RAG"].verdict is DomainVerdict.THIN


# ── growth confidence cannot be overstated ────────────────────────────────


def test_a_two_point_velocity_cannot_be_presented_above_low_confidence() -> None:
    """The constraint is enforced by the type, not by a reviewer noticing.

    `confidence` is a computed property with no setter, so there is no way to
    construct a two-point velocity and label it HIGH. This is the same
    discipline as `Deadline.shrink_to()`, which can only tighten.
    """
    velocity = Velocity.between(
        Observation("HKUDS/OpenSpace", 6185, date(2026, 5, 15)),
        Observation("HKUDS/OpenSpace", 7300, date(2026, 8, 5)),
    )

    assert velocity.points == 2
    assert velocity.confidence is Confidence.LOW
    assert all(p.confidence is Confidence.LOW for p in velocity.projections())

    with pytest.raises(AttributeError):
        velocity.confidence = Confidence.HIGH  # type: ignore[misc]


def test_confidence_rises_on_its_own_as_snapshots_accumulate() -> None:
    """The mechanism that makes the engine improve while running unattended."""
    base = dict(
        identifier="x",
        earlier_value=100,
        later_value=120,
        earlier_on=date(2026, 5, 15),
        later_on=date(2026, 8, 5),
    )
    assert Velocity(**base, points=2).confidence is Confidence.LOW  # type: ignore[arg-type]
    assert Velocity(**base, points=4).confidence is Confidence.MEDIUM  # type: ignore[arg-type]
    assert Velocity(**base, points=9).confidence is Confidence.HIGH  # type: ignore[arg-type]


def test_the_projection_band_is_linear_to_compound_and_widens_with_horizon() -> None:
    """Two points have no variance, so the band is the two honest extrapolations.

    Linear is the conservative reading, compound the optimistic one, and beyond
    the measurement window they diverge — which is a real property of the
    uncertainty rather than a tuned constant.
    """
    velocity = Velocity.between(
        Observation("m", 743, date(2026, 5, 15)),
        Observation("m", 903, date(2026, 8, 5)),
    )

    near, far = velocity.project(30), velocity.project(180)
    assert near.low <= near.high
    assert (far.high - far.low) > (near.high - near.low)
    # Compounding growth outruns linear past the measurement window.
    assert far.compound > far.linear


def test_a_reversed_pair_is_refused_rather_than_reporting_decline() -> None:
    """Silently reporting growth as decline would raise nothing at all."""
    with pytest.raises(ValueError, match="not after"):
        Velocity.between(
            Observation("x", 100, date(2026, 8, 5)),
            Observation("x", 120, date(2026, 5, 15)),
        )


def test_velocity_across_two_different_projects_is_refused() -> None:
    with pytest.raises(ValueError, match="different projects"):
        Velocity.between(
            Observation("a/one", 100, date(2026, 5, 15)),
            Observation("b/two", 120, date(2026, 8, 5)),
        )


def test_a_stalled_project_never_outranks_a_compounding_one(snapshot: Snapshot) -> None:
    """The whole reason two points were worth collecting.

    agent-kernel (+1.8%) and memind (+21.5%) are indistinguishable on stars
    alone at the moment of the snapshot. With equal relevance and equal
    licensing, growth has to break the tie in the right direction.
    """
    names = snapshot.by_name()
    stalled = Velocity.between(
        names["oguzbilgic/agent-kernel"],
        Observation("oguzbilgic/agent-kernel", 335, date(2026, 8, 5)),
    )
    compounding = Velocity.between(
        names["openmemind/memind"], Observation("openmemind/memind", 903, date(2026, 8, 5))
    )
    assert stalled.stalled
    assert not compounding.stalled

    artifact = Artifact(
        id="x", name="x", source="github", url="https://example.test/x", licence="MIT"
    )
    slow = assess(artifact, stalled, relevance=0.8, relevance_note="n", integration_cost=0.3)
    fast = assess(artifact, compounding, relevance=0.8, relevance_note="n", integration_cost=0.3)

    assert fast.opportunity.total > slow.opportunity.total


# ── claims without evidence stay visible ──────────────────────────────────


def test_a_claim_with_no_evidence_renders_as_unknown_rather_than_disappearing() -> None:
    """A gap in the evidence is a finding. Dropping it inflates the report."""
    claim = Claim("uses a distributed queue")

    assert claim.confidence is Confidence.NONE
    assert not claim.supported
    assert claim.render().startswith("UNKNOWN")


def test_a_claim_is_never_more_confident_than_its_best_evidence() -> None:
    weak = Evidence("https://a.test", date(2026, 8, 5), "x", Confidence.LOW)
    strong = Evidence("https://b.test", date(2026, 8, 5), "y", Confidence.HIGH)

    assert Claim("s", (weak,)).confidence is Confidence.LOW
    assert Claim("s", (weak, strong)).confidence is Confidence.HIGH


def test_confidence_orders_by_strength_not_alphabetically() -> None:
    """`StrEnum` inherits str's comparisons; a partial ordering compares words.

    Alphabetically HIGH < LOW, so a caller filtering for "at least MEDIUM" would
    keep its worst-supported claims and discard its best.
    """
    assert Confidence.HIGH > Confidence.MEDIUM > Confidence.LOW > Confidence.NONE
    assert max([Confidence.LOW, Confidence.HIGH]) is Confidence.HIGH


def test_an_oversized_excerpt_is_refused_at_construction() -> None:
    """The excerpt cap is a licence boundary, not a formatting preference."""
    with pytest.raises(ValueError, match="over the"):
        Evidence("https://a.test", date(2026, 8, 5), "x" * (MAX_EXCERPT_CHARS + 1))


def test_an_unknown_licence_is_treated_as_not_absorbable() -> None:
    """No LICENSE file means all rights reserved, not public domain."""
    assert Artifact(id="a", name="a", source="s", url="u", licence="MIT").absorbable
    assert Artifact(id="b", name="b", source="s", url="u", licence="Apache-2.0").absorbable
    assert not Artifact(id="c", name="c", source="s", url="u", licence="").absorbable
    assert not Artifact(id="d", name="d", source="s", url="u", licence="AGPL-3.0").absorbable


# ── report verification ───────────────────────────────────────────────────


def _evidence_file() -> EvidenceFile:
    file = EvidenceFile(fetched_on=date(2026, 8, 5))
    file.add(
        Artifact(
            id="github:HKUDS/OpenSpace",
            name="HKUDS/OpenSpace",
            source="github",
            url="https://github.com/HKUDS/OpenSpace",
            description="OpenSpace: The Skill Management Layer for AI Agents",
            popularity=7300,
            evidence=(
                Evidence(
                    "https://github.com/HKUDS/OpenSpace",
                    date(2026, 8, 5),
                    "OpenSpace: The Skill Management Layer for AI Agents. 7300 stars, 881 forks.",
                    Confidence.HIGH,
                ),
            ),
        )
    )
    return file


def test_a_citation_to_evidence_that_was_never_fetched_is_refused() -> None:
    """The failure mode generated intelligence actually exhibits.

    A plausible URL for a page nobody opened reads exactly like a real citation.
    This check is exact and has no false positives, which is why it is allowed
    to block publication.
    """
    document = (
        "OpenSpace is a skill layer. [https://github.com/HKUDS/OpenSpace · 2026-08-05]\n"
        "It has an enterprise tier. [https://openspace.example/pricing · 2026-08-05]\n"
    )
    result = verify_document(document, _evidence_file())

    assert not result.publishable
    fabricated = [f for f in result.fatal if f.kind == "fabricated_citation"]
    assert len(fabricated) == 1
    assert "openspace.example" in fabricated[0].detail


def test_a_figure_that_appears_in_no_evidence_record_is_refused() -> None:
    """Comparing against structured data catches what prose comparison cannot."""
    document = "OpenSpace has 40000 enterprise customers. [https://github.com/HKUDS/OpenSpace · 2026-08-05]"
    result = verify_document(document, _evidence_file())

    assert not result.publishable
    assert any(f.kind == "number_mismatch" for f in result.fatal)


def test_a_correctly_cited_and_correctly_numbered_document_passes() -> None:
    document = (
        "OpenSpace reached 7300 stars and 881 forks. "
        "[https://github.com/HKUDS/OpenSpace · 2026-08-05]"
    )
    result = verify_document(document, _evidence_file())

    assert result.publishable
    assert result.citations_checked == 1


def test_uncited_prose_is_not_checked_and_does_not_block_publication() -> None:
    """Narrative framing is ours, not a claim about anyone else's system.

    Requiring a citation on every sentence would make the connective tissue of a
    document unpublishable, which is how a verification pass gets switched off.
    """
    result = verify_document(
        "This section explains why the ranking is split in two.", _evidence_file()
    )

    assert result.publishable
    assert result.checked_sentences == 0


# ── feature mining and gaps ───────────────────────────────────────────────


def test_mining_reads_the_corpus_not_the_repository_name() -> None:
    """A project called `agent-memory` matching `memory` on its name proves nothing."""
    named_only = Artifact(id="a", name="someone/agent-memory", source="github", url="u")
    described = Artifact(
        id="b",
        name="someone/x",
        source="github",
        url="u",
        description="Long-term memory and vector search for agents",
    )

    assert not mine(named_only)
    assert {hit.feature.key for hit in mine(described)} >= {"memory", "vector_search"}


def test_a_mined_feature_is_capped_at_medium_confidence() -> None:
    """A README is evidence of a claim. HIGH would mean we ran it."""
    artifact = Artifact(id="a", name="a", source="s", url="u", description="Includes rate limiting")
    hits = mine(artifact)

    assert hits
    assert all(hit.confidence is Confidence.MEDIUM for hit in hits)


def test_word_boundaries_stop_auth_matching_author() -> None:
    """Substring matching would make `auth` hit most of every README."""
    artifact = Artifact(id="a", name="a", source="s", url="u", description="Written by the author")
    assert "auth" not in {hit.feature.key for hit in mine(artifact)}


def test_the_gap_analysis_finds_what_a_cluster_does_not_offer() -> None:
    """The half that says what to build, rather than what already exists."""
    matrix = CoverageMatrix()
    for index in range(10):
        matrix.add(
            Artifact(
                id=f"a{index}",
                name=f"n{index}",
                source="s",
                url="u",
                description="An agent framework with tool calling and a planner",
                # Long enough to be informative — a one-liner would be excluded
                # from the denominator rather than counted as lacking anything.
                corpus="It orchestrates tools, decomposes tasks through a planner, and "
                "runs them against a model provider of your choosing. " * 3,
            )
        )

    gaps = {gap.feature.key for gap in matrix.gaps()}
    assert "billing" in gaps
    assert "multi_tenancy" in gaps
    # Claimed by all ten, so not a gap.
    assert "tool_orchestration" not in gaps


def test_a_gap_nobody_would_pay_for_ranks_below_one_they_would() -> None:
    """Rarity alone would rank an unwanted capability as the top opportunity."""
    matrix = CoverageMatrix()
    matrix.add(
        Artifact(
            id="a",
            name="n",
            source="s",
            url="u",
            description="a plain library",
            corpus="It does one thing and does not concern itself with anything else at all. " * 4,
        )
    )

    ranked = matrix.gaps()
    top = ranked[0]
    assert top.feature.enterprise_value == 3
    assert ranked == sorted(ranked, key=lambda gap: -gap.opportunity)


# ── architecture inference ────────────────────────────────────────────────


def test_architecture_without_a_manifest_is_reported_as_not_inferable() -> None:
    """Visibly different from a report about a genuinely simple system."""
    report = infer(Artifact(id="a", name="n", source="github", url="u"))

    assert report.layers == []
    assert report.claims[0].confidence is Confidence.NONE
    assert "not inferable" in report.claims[0].statement


def test_a_shared_redis_between_broker_and_cache_is_named_as_a_failure_point() -> None:
    """The class of finding a project's own documentation will not contain."""
    artifact = Artifact(
        id="pypi:x",
        name="x",
        source="pypi",
        url="https://pypi.org/project/x/",
        tags=("fastapi", "celery", "redis", "sqlalchemy"),
        evidence=(Evidence("https://pypi.org/project/x/", date(2026, 8, 5), "x"),),
    )
    report = infer(artifact)

    assert {"http", "worker", "cache", "relational"} <= report.layer_keys
    hazards = " ".join(c.statement for c in report.failure_points)
    assert "broker and the application cache" in hazards
    # Four separately-operated components: worker, cache, relational, and the
    # count is what decides whether a small team can adopt it.
    assert report.operational_complexity == 3


def test_a_single_provider_dependency_is_named_as_a_concentration_risk() -> None:
    artifact = Artifact(
        id="pypi:y",
        name="y",
        source="pypi",
        url="https://pypi.org/project/y/",
        tags=("openai", "fastapi"),
        evidence=(Evidence("https://pypi.org/project/y/", date(2026, 8, 5), "y"),),
    )
    hazards = " ".join(c.statement for c in infer(artifact).failure_points)

    assert "single model provider" in hazards
    assert "no telemetry dependency" in hazards


def test_every_architecture_claim_carries_the_manifest_that_produced_it() -> None:
    artifact = Artifact(
        id="pypi:z",
        name="z",
        source="pypi",
        url="https://pypi.org/project/z/",
        tags=("qdrant-client",),
        evidence=(Evidence("https://pypi.org/project/z/", date(2026, 8, 5), "z"),),
    )
    report = infer(artifact)

    assert all(claim.supported for claim in report.claims)
    assert all(claim.evidence[0].url == "https://pypi.org/project/z/" for claim in report.claims)


# ── scoring and revenue ───────────────────────────────────────────────────


def test_a_score_prints_the_arithmetic_that_produced_it() -> None:
    """An unfalsifiable number is either accepted whole or discarded whole."""
    artifact = Artifact(id="a", name="thing", source="s", url="u", licence="MIT")
    result = assess(
        artifact, None, relevance=0.9, relevance_note="overlaps P13", integration_cost=0.2
    )

    explanation = result.opportunity.explain()
    assert "omnex_relevance" in explanation
    assert "overlaps P13" in explanation
    assert "0.90" in explanation


def test_opportunity_and_threat_are_never_blended() -> None:
    """A fast-growing thing we cannot absorb is the most important row.

    Blended into one ranking it lands mid-table, which is where nobody reads.
    """
    rival = Artifact(id="r", name="rival", source="s", url="u", licence="AGPL-3.0", popularity=9000)
    velocity = Velocity.between(
        Observation("rival", 4000, date(2026, 5, 15)),
        Observation("rival", 9000, date(2026, 8, 5)),
    )
    result = assess(
        rival,
        velocity,
        relevance=0.2,
        relevance_note="cannot build on it",
        integration_cost=0.9,
        substitutes_our_product=0.9,
    )

    assert result.threat.total > result.opportunity.total
    assert result.headline.startswith("COMPETITOR")


def test_a_score_outside_zero_to_one_is_a_bug_not_a_strong_opinion() -> None:
    artifact = Artifact(id="a", name="a", source="s", url="u")
    with pytest.raises(ValueError, match="outside"):
        assess(artifact, None, relevance=1.4, relevance_note="n", integration_cost=0.2)


def test_build_order_is_by_payback_not_by_priority() -> None:
    """A self-funding sequence pays for the ambitious item with the boring one."""
    quick = Opportunity(
        name="quick",
        model=BusinessModel.CREDITS,
        complexity=Complexity.SMALL,
        monthly_revenue=Money.from_usd("2000.00"),
        demand=0.5,
    )
    ambitious = Opportunity(
        name="ambitious",
        model=BusinessModel.SUBSCRIPTION,
        complexity=Complexity.LARGE,
        monthly_revenue=Money.from_usd("3000.00"),
        demand=0.95,
        defensibility=0.95,
    )
    portfolio = Portfolio([ambitious, quick])

    assert portfolio.build_order()[0].name == "quick"
    assert portfolio.by_priority()[0].name == "ambitious"
    assert quick.payback_months < ambitious.payback_months


def test_an_opportunity_with_no_margin_never_pays_back() -> None:
    """`inf` rather than a large number, so it sorts last and reads as never."""
    dead = Opportunity(
        name="dead",
        model=BusinessModel.SUPPORT,
        complexity=Complexity.MEDIUM,
        monthly_revenue=Money.zero(),
    )
    assert dead.payback_months == float("inf")
    assert "never" in Portfolio([dead]).report()


def test_revenue_arithmetic_is_exact_money_not_floats() -> None:
    opportunity = Opportunity(
        name="x",
        model=BusinessModel.CREDITS,
        complexity=Complexity.SMALL,
        monthly_revenue=Money.from_usd("1000.00"),
        variable_cost_share=0.3,
    )
    assert opportunity.monthly_margin == Money.from_usd("700.00")
    assert opportunity.annual_margin == Money.from_usd("8400.00")
    assert opportunity.build_cost == Money.from_usd("3200.00")


def test_an_artifact_with_only_a_registry_one_liner_is_excluded_not_counted_as_absent() -> None:
    """The correction that stopped a wrong headline reaching a report.

    litellm's PyPI summary is "Library to easily interface with LLM API
    providers" — it mentions neither routing nor cost, and litellm is one of the
    best known model routers there is. Counted naively it becomes evidence that
    nobody does model routing, ranked top of the gap table by rarity, published
    as an opportunity. Absence of evidence has to be recorded as absence of
    evidence, not as a negative finding.
    """
    matrix = CoverageMatrix()
    thin = Artifact(
        id="pypi:litellm",
        name="litellm",
        source="pypi",
        url="u",
        description="Library to easily interface with LLM API providers",
    )
    thick = Artifact(
        id="github:real",
        name="real",
        source="github",
        url="u",
        description="An agent framework",
        corpus="It provides model routing with fallback, cost tracking per request, "
        "observability through opentelemetry, and multi-tenant billing. " * 3,
    )
    matrix.add(thin)
    matrix.add(thick)

    assert "pypi:litellm" in matrix.uninformative
    assert matrix.size == 1

    # The one informative artifact claims routing, so routing is not a gap.
    assert "model_routing" not in {gap.feature.key for gap in matrix.gaps()}
