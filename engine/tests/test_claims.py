"""The claim registry, and the ways a registry lies to the person reading it.

Almost every test here is a refusal, for the same reason `test_apply_decisions`
is: the value of a status is entirely in what cannot produce it. A registry
where writing a row is the same act as proving it is a project tracker with
epistemic vocabulary painted on.

The twelve adversarial cases the hardening contract asks for are spread across
this file and `test_next_action.py`; each is named for the failure it forces
rather than the function it calls.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ENGINE = REPO / "engine"
sys.path.insert(0, str(ENGINE / "scripts"))

import claims as registry_module  # noqa: E402
from claims import Claim, Evidence, Registry, Stance, Status  # noqa: E402

TODAY = date(2026, 9, 8)


def _claim(**over: object) -> Claim:
    base: dict[str, object] = {
        "claim_id": "C-1",
        "claim": "a symbol imports",
        "type": "symbol",
        "source": "a test",
    }
    base.update(over)
    return Claim(**base)  # type: ignore[arg-type]


def _evidence(**over: object) -> Evidence:
    base: dict[str, object] = {
        "evidence_id": "E-1",
        "claim_id": "C-1",
        "stance": Stance.SUPPORTS,
        "method": "import",
        "observed_at": "2026-09-08",
        "detail": "imported it",
    }
    base.update(over)
    return Evidence(**base)  # type: ignore[arg-type]


def _status(claim: Claim, *evidence: Evidence, today: date = TODAY) -> Status:
    return Registry([claim], list(evidence)).status(claim, today=today)


# ── absence ───────────────────────────────────────────────────────────────
def test_a_claim_with_no_evidence_is_unknown_and_never_false() -> None:
    """The rule the whole repository rests on, at the point it would be broken.

    UNKNOWN blocks and FALSE lets you move on, which is exactly why an optimiser
    under pressure reaches for FALSE first.
    """
    assert _status(_claim()) is Status.UNKNOWN


def test_being_unable_to_check_is_not_evidence_against() -> None:
    """The error this file's own seed data contained on the first run.

    A 403 from an egress proxy contradicts *readability*. Filing it against the
    claim itself makes the registry assert something the evidence text denies.
    Readability is its own claim, and the thing it blocks stays UNKNOWN.
    """
    unreadable = _claim(claim_id="C-2", claim="the shape is readable", type="external")
    blocked = _evidence(
        evidence_id="E-2",
        claim_id="C-2",
        stance=Stance.CONTRADICTS,
        method="network_probe",
        source_version="proxy 2026-09-08",
        detail="403 to CONNECT",
    )
    accepts = _claim(claim="the API accepts it", type="external", dependencies=("C-2",))
    both = Registry([accepts, unreadable], [blocked])

    assert both.status(unreadable, today=TODAY) is Status.CONTRADICTED
    assert both.status(accepts, today=TODAY) is Status.UNKNOWN


# ── evidence must be able to settle the claim ─────────────────────────────
def test_a_claim_is_not_supported_merely_because_evidence_exists() -> None:
    """`person` cannot settle whether a symbol imports. Importing it can.

    Without this the registry degrades into a table where writing a row and
    proving a thing are the same act.
    """
    assert _status(_claim(), _evidence(method="person")) is Status.DISCOVERED
    assert _status(_claim(), _evidence(method="import")) is Status.SUPPORTED


def test_every_claim_type_names_a_way_it_could_be_settled() -> None:
    """A type with no verification method is a claim nothing could ever prove."""
    for claim_type, methods in registry_module.VERIFIES.items():
        assert methods, f"{claim_type} has no verification method"


# ── contradiction ─────────────────────────────────────────────────────────
def test_live_contradiction_outranks_support() -> None:
    """A claim with something arguing against it is not 'mostly true'."""
    against = _evidence(evidence_id="E-2", stance=Stance.CONTRADICTS, detail="it raised")
    assert _status(_claim(), _evidence(), against) is Status.CONTRADICTED


def test_contradictory_evidence_is_never_erased_only_superseded() -> None:
    """A registry that drops what disagreed with it cannot answer the only
    question worth asking of it: what would change my mind."""
    against = _evidence(evidence_id="E-2", stance=Stance.CONTRADICTS, detail="it raised")
    later = _evidence(evidence_id="E-3", supersedes="E-2", detail="fixed, then imported")

    store = Registry([_claim()], [against, later])
    assert store.status(_claim(), today=TODAY) is Status.SUPPORTED
    # Still on file, and still readable as history.
    assert any(e.evidence_id == "E-2" for e in store.for_claim("C-1"))
    assert store.superseded() == {"E-2"}


def test_superseding_the_only_evidence_is_not_the_same_as_never_having_any() -> None:
    against = _evidence(stance=Stance.CONTRADICTS)
    replacement = _evidence(evidence_id="E-9", claim_id="C-OTHER", supersedes="E-1")
    store = Registry([_claim()], [against, replacement])
    assert store.status(_claim(), today=TODAY) is Status.SUPERSEDED


# ── staleness ─────────────────────────────────────────────────────────────
def test_evidence_past_its_window_stops_counting() -> None:
    """ "LangGraph's API is X" was true against a version, on a date."""
    old = _evidence(
        method="package_read",
        observed_at="2026-01-01",
        source_version="langgraph 0.2.45",
        reverify_after=30,
    )
    external = _claim(type="external")
    assert _status(external, old) is Status.STALE
    assert _status(external, old, today=date(2026, 1, 15)) is Status.SUPPORTED


def test_evidence_about_this_repository_does_not_expire_on_a_clock() -> None:
    """It cannot change without a commit, and the commit re-runs the checker.
    Expiring it would turn every old-but-still-green check into a false alarm."""
    ancient = _evidence(observed_at="2020-01-01", reverify_after=1)
    assert _status(_claim(), ancient) is Status.SUPPORTED


def test_a_stale_contradiction_does_not_outrank_fresh_support() -> None:
    stale_against = _evidence(
        evidence_id="E-2",
        stance=Stance.CONTRADICTS,
        method="package_read",
        observed_at="2026-01-01",
        source_version="x 1.0",
        reverify_after=30,
    )
    fresh = _evidence(evidence_id="E-3", method="package_read", source_version="x 2.0")
    assert _status(_claim(type="external"), stale_against, fresh) is Status.SUPPORTED


# ── dependencies ──────────────────────────────────────────────────────────
def test_a_claim_is_never_firmer_than_what_it_rests_on() -> None:
    """C-011 ("citegate is installable from PyPI") depends on a workflow that has
    never run. It must not read SUPPORTED because its own row looks tidy."""
    base = _claim(claim_id="C-BASE", claim="the workflow runs", type="pipeline")
    built = _claim(claim_id="C-TOP", dependencies=("C-BASE",))
    store = Registry([base, built], [_evidence(claim_id="C-TOP")])
    assert store.status(built, today=TODAY) is Status.PARTIALLY_SUPPORTED


# ── a person's rejection ──────────────────────────────────────────────────
def test_a_rejected_claim_stays_rejected_whatever_the_evidence_says() -> None:
    """The one exit from the evidence machinery, and only a person may take it."""
    rejected = _claim(rejected_by="RaveZona", rejected_on="2026-09-08")
    assert _status(rejected, _evidence()) is Status.REJECTED


# ── the registry's own shape ──────────────────────────────────────────────
def test_a_malformed_registry_is_refused_with_every_reason_at_once() -> None:
    store = Registry(
        [
            _claim(),
            _claim(claim_id="C-BAD", type="vibes"),
            _claim(claim_id="C-DEP", dependencies=("C-NOPE",)),
        ],
        [
            _evidence(claim_id="C-GHOST"),
            _evidence(evidence_id="E-2", method="wishful"),
            _evidence(evidence_id="E-3", method="package_read"),
        ],
    )
    found = registry_module.problems(store)
    assert any("unknown claim C-GHOST" in p for p in found)
    assert any("not one anything verifies with" in p for p in found)
    assert any("no verification method" in p for p in found)
    assert any("depends on unknown claim" in p for p in found)
    assert any("no source_version" in p for p in found)


def test_an_observation_about_a_third_party_must_name_the_version() -> None:
    """Without it the observation is not repeatable and can never go stale."""
    store = Registry([_claim(type="external")], [_evidence(method="package_read")])
    assert any("source_version" in p for p in registry_module.problems(store))


# ── determinism ───────────────────────────────────────────────────────────
def test_reading_the_registry_twice_gives_the_same_answer() -> None:
    """Every state/graph script must be safely repeatable: no arbitrary ordering,
    no state that moves because it was read."""
    first = registry_module.load()
    second = registry_module.load()
    assert [c.claim_id for c in first.claims] == [c.claim_id for c in second.claims]
    assert registry_module.summarise(first, today=TODAY) == registry_module.summarise(
        second, today=TODAY
    )


def test_status_is_computed_and_not_a_field_anybody_can_type() -> None:
    """A stored status is a typed status, and a typed status is the one thing
    that must never be typeable."""
    assert not hasattr(Claim("x", "y", "symbol", "z"), "status")
    source = (ENGINE / "scripts" / "claims.py").read_text(encoding="utf-8")
    assert '"status"' not in source.split("def load(")[1].split("def problems(")[0], (
        "load() must not read a status field out of the file"
    )


# ── the committed registry ────────────────────────────────────────────────
def test_the_committed_registry_is_well_formed() -> None:
    assert registry_module.problems(registry_module.load()) == []


def test_the_committed_registry_records_what_is_not_known() -> None:
    """An all-green registry would mean nothing was asserted that could fail.

    release.yml has never run, the attestation action's major could not be read
    through the proxy, and nobody has imported an n8n binding. Those are UNKNOWN
    and must stay visible as UNKNOWN.
    """
    store = registry_module.load()
    counts = registry_module.summarise(store)
    assert counts[Status.UNKNOWN] > 0, "a registry with no unknowns is not being honest"
    assert counts[Status.CONTRADICTED] > 0, "negative evidence must survive in the file"


@pytest.mark.parametrize(
    ("claim_id", "expected"),
    [
        ("C-001", Status.REJECTED),
        ("C-005", Status.SUPPORTED),
        ("C-013", Status.UNKNOWN),
        ("C-011", Status.UNKNOWN),
    ],
)
def test_the_findings_this_session_made_are_on_file(claim_id: str, expected: str) -> None:
    """C-001: citegate did not import on 3.10, proven by running it.

    That evidence (E-001) is still on file and still CONTRADICTS — 3.10 was
    never going to import, on purpose. What changed is the promise it was
    checking: `oss/citegate/pyproject.toml` raised its floor to `>=3.11` in
    `0c0d426`, so the claim, as worded, can never become true again by any
    further code change. D-015 names that distinction and why more evidence
    would be noise; a person (not this test, not a script) rejected the claim
    with a name and a date, which is the only way `status()` lets a claim this
    permanently false stop reading as an open problem.

    C-005 read UNKNOWN here for as long as `release.yml` had never run. Run
    34237298583 — dispatched, not tagged — ran the gate, built the artifacts and
    **attested them**, which settles that the workflow builds and attests.

    It settles nothing else, and this parametrisation is where that is held.
    The run's `github_release` and `pypi` jobs were skipped by their event guard,
    so the publish half was split into **C-013** and stays UNKNOWN, and
    **C-011** (installable from PyPI by a stranger) stays UNKNOWN too: a
    workflow run is not a publish, and a GitHub Release is not PyPI.

    Narrowing a claim until the evidence fits is how a registry goes decorative.
    What makes the split legitimate is that the removed half is still here,
    still blocking, and still listed above.
    """
    store = registry_module.load()
    claim = next(c for c in store.claims if c.claim_id == claim_id)
    assert store.status(claim) is expected
