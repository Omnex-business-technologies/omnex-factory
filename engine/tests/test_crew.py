"""Tests for P3. The veto and the tamper-detection tests are the load-bearing ones."""

from __future__ import annotations

import pytest

from omnex.core import FakeClock
from omnex.crew import AuditEntry, AuditTrail, Crew, Opinion, Position, Role, decide, override


def _opinion(role: Role, position: Position, confidence: float = 0.8, **kw) -> Opinion:
    return Opinion(role=role, position=position, confidence=confidence, **kw)


# ── Consensus ─────────────────────────────────────────────────────────────


def test_a_fact_checker_veto_is_not_outvoted_by_two_agreeing_agents():
    """How an unsupported claim ships: counted as one vote among three."""
    result = decide(
        [
            _opinion(Role.RESEARCHER, Position.ACCEPT, 0.9),
            _opinion(Role.WRITER, Position.ACCEPT, 0.9),
            _opinion(Role.FACT_CHECKER, Position.REJECT, 0.6, reason="page 12 does not say this"),
        ]
    )
    assert not result.accepted
    assert result.vetoed_by is Role.FACT_CHECKER
    assert result.contested
    assert "page 12" in result.reason


def test_disagreement_is_reported_rather_than_averaged_into_a_number():
    """Two yes and one no is a question for a human, not 67% confidence."""
    result = decide(
        [
            _opinion(Role.RESEARCHER, Position.ACCEPT),
            _opinion(Role.WRITER, Position.ACCEPT),
            _opinion(Role.SUPERVISOR, Position.REJECT, reason="sources are thin"),
        ]
    )
    assert result.accepted and result.contested
    assert [o.role for o in result.dissent] == [Role.SUPERVISOR]
    assert "CONTESTED" in result.report()


def test_unanimous_agreement_is_not_contested():
    result = decide(
        [_opinion(Role.RESEARCHER, Position.ACCEPT), _opinion(Role.WRITER, Position.ACCEPT)]
    )
    assert result.accepted and not result.contested


def test_abstaining_means_gather_more_evidence_not_reject():
    all_abstain = decide(
        [
            _opinion(Role.RESEARCHER, Position.ABSTAIN),
            _opinion(Role.WRITER, Position.ABSTAIN),
        ]
    )
    assert not all_abstain.accepted
    assert "gather more evidence" in all_abstain.reason
    assert not all_abstain.contested  # nobody disagreed; nobody could tell


def test_an_abstention_does_not_count_against_the_majority():
    result = decide(
        [
            _opinion(Role.RESEARCHER, Position.ACCEPT),
            _opinion(Role.WRITER, Position.ABSTAIN),
        ]
    )
    assert result.accepted
    assert "1 abstain" in result.reason


def test_confidence_breaks_a_tie_and_does_nothing_else():
    tie = decide(
        [
            _opinion(Role.RESEARCHER, Position.ACCEPT, 0.9),
            _opinion(Role.WRITER, Position.REJECT, 0.4),
        ]
    )
    assert tie.accepted and tie.contested and "tie broken" in tie.reason

    # A confident minority still loses where there is a real majority.
    minority = decide(
        [
            _opinion(Role.RESEARCHER, Position.REJECT, 0.99),
            _opinion(Role.WRITER, Position.ACCEPT, 0.1),
            _opinion(Role.SUPERVISOR, Position.ACCEPT, 0.1),
        ]
    )
    assert minority.accepted


def test_a_veto_can_be_overridden_but_never_silently():
    vetoed = decide(
        [
            _opinion(Role.RESEARCHER, Position.ACCEPT),
            _opinion(Role.FACT_CHECKER, Position.REJECT, reason="unverified"),
        ]
    )
    overridden = override(vetoed, by="ana@omnex", reason="source confirmed by phone")
    assert overridden.accepted
    assert overridden.overridden_by == "ana@omnex"
    assert overridden.vetoed_by is Role.FACT_CHECKER  # the veto is still on the record
    assert "overridden" in overridden.report()


def test_overriding_without_a_reason_is_refused():
    vetoed = decide([_opinion(Role.FACT_CHECKER, Position.REJECT)])
    with pytest.raises(ValueError, match="stated reason"):
        override(vetoed, by="ana", reason="   ")


def test_an_opinion_without_evidence_is_labelled_as_such():
    result = decide([_opinion(Role.RESEARCHER, Position.ACCEPT, evidence=())])
    assert "no evidence" in result.report()


# ── Audit trail ───────────────────────────────────────────────────────────


def _trail() -> AuditTrail:
    return AuditTrail(clock=FakeClock())


def test_an_intact_chain_verifies():
    trail = _trail()
    trail.record("researcher", "searched", query="pool size")
    trail.record("writer", "drafted", words=120)
    ok, broken, reason = trail.verify()
    assert ok and broken is None and "intact" in reason


def test_editing_an_entry_breaks_the_chain_and_names_where():
    """An audit log that can be edited is a log that proves nothing."""
    trail = _trail()
    trail.record("researcher", "searched", query="pool size")
    trail.record("writer", "drafted", words=120)
    trail.record("fact_checker", "verified", supported=True)

    tampered = trail.entries[1]
    trail.entries[1] = AuditEntry(**{**tampered.as_dict(), "payload": {"words": 999}})

    ok, broken, reason = trail.verify()
    assert not ok and broken == 1
    assert "does not match its own hash" in reason
    assert "FIRST BROKEN AT 1" in trail.render()


def test_deleting_an_entry_is_detected():
    trail = _trail()
    for i in range(4):
        trail.record("agent", "step", n=i)
    del trail.entries[2]
    ok, broken, _ = trail.verify()
    assert not ok and broken == 2


def test_swapping_two_entries_is_detected():
    """Hashing content alone would let this through — each still hashes the same."""
    trail = _trail()
    for i in range(4):
        trail.record("agent", "step", n=i)
    trail.entries[1], trail.entries[2] = trail.entries[2], trail.entries[1]
    ok, broken, _ = trail.verify()
    assert not ok and broken == 1


def test_the_chain_survives_a_round_trip_through_storage():
    """Key order must not change a hash, or the chain breaks on first restart."""
    trail = _trail()
    trail.record("researcher", "searched", zebra=1, alpha=2, middle=3)
    trail.record("writer", "drafted", words=120)

    restored = AuditTrail.from_jsonl(trail.to_jsonl(), clock=FakeClock())
    ok, _, _ = restored.verify()
    assert ok
    assert restored.head == trail.head


def test_the_head_pins_the_whole_history():
    trail = _trail()
    trail.record("a", "x")
    head_before = trail.head
    trail.record("b", "y")
    assert trail.head != head_before  # appending moves the tip


# ── The crew, end to end ──────────────────────────────────────────────────


def test_a_run_leaves_a_verifiable_record_of_who_decided_what():
    trail = _trail()
    crew = Crew(audit=trail)

    crew.contribute(_opinion(Role.RESEARCHER, Position.ACCEPT, 0.8, evidence=("p12",)))
    crew.contribute(_opinion(Role.WRITER, Position.ACCEPT, 0.7, evidence=("p12",)))
    crew.contribute(
        _opinion(Role.FACT_CHECKER, Position.REJECT, 0.9, reason="p12 states twenty, not fifty")
    )

    result = crew.conclude()
    assert not result.accepted and result.vetoed_by is Role.FACT_CHECKER

    final = crew.override_veto(result, by="ana@omnex", reason="corrected upstream")
    assert final.accepted

    ok, _, _ = trail.verify()
    assert ok
    assert [e.action for e in trail.entries] == [
        "opinion",
        "opinion",
        "opinion",
        "consensus",
        "veto_override",
    ]
    assert trail.by_actor("ana@omnex")[0].action == "veto_override"
