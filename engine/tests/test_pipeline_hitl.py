"""Tests for P16 and P15. The approval-binding test is the important one."""

from __future__ import annotations

from random import Random

import pytest

from omnex.core import FakeClock, IdFactory, Money, PermanentError, TransientError, ValidationFailed
from omnex.hitl import ApprovalStore, Proposal, UncertaintyDetector, Verdict
from omnex.pipeline import InMemoryBroker, JobState, WebhookVerifier, Worker, verify_signature

# ── P16: idempotency, retries, dead letters ───────────────────────────────


def _worker() -> tuple[InMemoryBroker, Worker]:
    clock = FakeClock()
    broker = InMemoryBroker(ids=IdFactory(clock=clock, rng=Random(1)))
    return broker, Worker(broker=broker, clock=clock, rng=Random(2))


def test_a_repeated_job_with_the_same_payload_is_not_run_twice():
    broker, worker = _worker()
    runs = {"n": 0}

    def handler(job):
        runs["n"] += 1
        return {"charged": job.payload["amount"]}

    worker.register("charge", handler)
    worker.run_once(broker.enqueue("charge", {"amount": 10}, idempotency_key="evt_1"))
    second = worker.run_once(broker.enqueue("charge", {"amount": 10}, idempotency_key="evt_1"))

    assert runs["n"] == 1
    assert second.result == {"charged": 10}


def test_the_same_key_with_a_different_payload_is_a_conflict_not_a_cache_hit():
    """The dangerous case: returning a result computed from other data."""
    broker, worker = _worker()
    worker.register("charge", lambda job: {"charged": job.payload["amount"]})
    worker.run_once(broker.enqueue("charge", {"amount": 10}, idempotency_key="evt_1"))

    with pytest.raises(ValidationFailed, match="different payload"):
        worker.run_once(broker.enqueue("charge", {"amount": 999}, idempotency_key="evt_1"))


def test_key_order_does_not_change_the_payload_fingerprint():
    broker, worker = _worker()
    worker.register("x", lambda job: "ok")
    worker.run_once(broker.enqueue("x", {"a": 1, "b": 2}, idempotency_key="k"))
    job = worker.run_once(broker.enqueue("x", {"b": 2, "a": 1}, idempotency_key="k"))
    assert job.state is JobState.DONE  # same payload, just written differently


def test_a_transient_failure_retries_then_dead_letters_with_everything_to_replay():
    broker, worker = _worker()
    attempts = {"n": 0}

    def flaky(job):
        attempts["n"] += 1
        raise TransientError("upstream down")

    worker.register("sync", flaky)
    job = worker.run_once(broker.enqueue("sync", {"id": 7}, idempotency_key="k7"))

    assert job.state is JobState.DEAD
    assert attempts["n"] == 3
    letter = worker.dead_letters[0]
    assert letter.job.payload == {"id": 7}  # replayable
    assert letter.job.idempotency_key == "k7"
    assert len(letter.job.errors) == 3
    assert "retries exhausted" in letter.reason


def test_a_permanent_failure_dead_letters_on_the_first_attempt():
    """Retrying a malformed payload produces four identical failures and delays the alert."""
    broker, worker = _worker()
    attempts = {"n": 0}

    def bad(job):
        attempts["n"] += 1
        raise PermanentError("payload is malformed")

    worker.register("sync", bad)
    worker.run_once(broker.enqueue("sync", {}))
    assert attempts["n"] == 1
    assert "permanent" in worker.dead_letters[0].reason


def test_an_unclassified_crash_dead_letters_rather_than_retrying_a_bug():
    broker, worker = _worker()
    worker.register("boom", lambda job: (_ for _ in ()).throw(KeyError("choices")))
    job = worker.run_once(broker.enqueue("boom", {}))
    assert job.state is JobState.DEAD and job.attempts == 1
    assert "handler raised" in worker.dead_letters[0].reason


def test_an_unregistered_kind_is_kept_for_replay_not_dropped():
    broker, worker = _worker()
    worker.run_once(broker.enqueue("not-deployed-yet", {"a": 1}))
    assert worker.dead_letters[0].job.payload == {"a": 1}


def test_replaying_after_a_fix_works_and_replaying_a_success_is_a_no_op():
    """The failure mode of every 'just re-run the DLQ' script."""
    broker, worker = _worker()
    state = {"broken": True, "charges": 0}

    def handler(job):
        if state["broken"]:
            raise TransientError("dependency down")
        state["charges"] += 1
        return "charged"

    worker.register("charge", handler)
    worker.run_once(broker.enqueue("charge", {"amount": 5}, idempotency_key="c1"))
    assert len(worker.dead_letters) == 1

    state["broken"] = False
    replayed = worker.replay(worker.dead_letters[0])
    assert replayed.state is JobState.DONE and state["charges"] == 1
    assert worker.dead_letters == []

    # A second replay of the same work does not charge again.
    worker.run_once(broker.enqueue("charge", {"amount": 5}, idempotency_key="c1"))
    assert state["charges"] == 1


# ── P16: webhook verification ─────────────────────────────────────────────


def _signed(secret: str, clock: FakeClock, body: bytes) -> tuple[str, str]:
    timestamp = str(int(clock.now().timestamp()))
    import hashlib
    import hmac

    signature = hmac.new(
        secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256
    ).hexdigest()
    return timestamp, signature


def test_a_valid_recent_signature_is_accepted():
    clock = FakeClock()
    verifier = WebhookVerifier(secret="shh", clock=clock)
    body = b'{"id":"evt_1","type":"charge.created"}'
    timestamp, signature = _signed("shh", clock, body)
    verifier.verify(timestamp, body, signature)  # does not raise


def test_a_replayed_request_is_rejected_once_it_is_stale():
    """A valid signature is valid forever without a timestamp window."""
    clock = FakeClock()
    verifier = WebhookVerifier(secret="shh", clock=clock, tolerance_seconds=300)
    body = b'{"id":"evt_1"}'
    timestamp, signature = _signed("shh", clock, body)

    clock.advance(301)
    with pytest.raises(PermanentError, match="replay"):
        verifier.verify(timestamp, body, signature)


def test_a_tampered_body_fails_even_with_a_valid_timestamp():
    clock = FakeClock()
    verifier = WebhookVerifier(secret="shh", clock=clock)
    timestamp, signature = _signed("shh", clock, b'{"amount":10}')
    with pytest.raises(PermanentError, match="signature"):
        verifier.verify(timestamp, b'{"amount":9999}', signature)


def test_signature_comparison_is_constant_time():
    """`==` leaks the correct prefix through timing, for free."""
    import inspect

    from omnex.pipeline import webhook

    assert "compare_digest" in inspect.getsource(webhook.verify_signature)
    assert not verify_signature("shh", "1", b"body", "wrong")


def test_the_idempotency_key_is_the_senders_event_id_not_a_body_hash():
    """Two identical charges a second apart are two charges."""
    clock = FakeClock()
    verifier = WebhookVerifier(secret="shh", clock=clock)
    first = verifier.parse(b'{"id":"evt_1","type":"charge","amount":10}')
    second = verifier.parse(b'{"id":"evt_2","type":"charge","amount":10}')
    assert first.idempotency_key != second.idempotency_key

    with pytest.raises(PermanentError, match="deduplicate"):
        verifier.parse(b'{"type":"charge","amount":10}')


# ── P15: approval binding ─────────────────────────────────────────────────


def _store() -> ApprovalStore:
    return ApprovalStore(ids=IdFactory(clock=FakeClock(), rng=Random(3)), clock=FakeClock())


def _refund(amount: str = "10.00", to: str = "customer@example.com") -> Proposal:
    return Proposal(
        action="issue_refund",
        summary=f"Refund {amount} to {to}",
        arguments={"amount": amount, "to": to},
        reversible=False,
    )


def test_an_approval_does_not_authorise_a_changed_proposal():
    """The whole point of P15. Between asking and answering, an agent re-plans."""
    store = _store()
    shown = _refund(amount="10.00")
    request = store.ask(shown)
    decision = store.decide(request.id, Verdict.APPROVED, decided_by="ana")

    assert decision.authorises(shown)

    # The agent re-planned. The human never saw this.
    changed = _refund(amount="10000.00")
    assert not decision.authorises(changed)


def test_rewording_the_explanation_does_not_invalidate_an_approval():
    """The fingerprint covers what will HAPPEN, not how it was described."""
    store = _store()
    shown = _refund()
    decision = store.decide(store.ask(shown).id, Verdict.APPROVED, decided_by="ana")

    reworded = Proposal(
        action=shown.action,
        summary="Send the customer their money back",
        arguments=shown.arguments,
        reversible=False,
    )
    assert decision.authorises(reworded)


def test_a_rejection_authorises_nothing():
    store = _store()
    proposal = _refund()
    decision = store.decide(store.ask(proposal).id, Verdict.REJECTED, decided_by="ana")
    assert not decision.authorises(proposal)
    assert store.effective_proposal(decision.request_id) is None


def test_an_amendment_authorises_the_amended_action_and_only_that():
    """'Yes, but send it to finance instead' is common and must be expressible."""
    store = _store()
    request = store.ask(_refund(to="customer@example.com"))
    decision = store.decide(
        request.id,
        Verdict.AMENDED,
        decided_by="ana",
        amended_arguments={"to": "finance@example.com"},
    )

    effective = store.effective_proposal(request.id)
    assert effective is not None
    assert effective.arguments["to"] == "finance@example.com"
    assert decision.authorises(effective)
    # The original, unamended action is NOT authorised.
    assert not decision.authorises(request.proposal)


def test_the_approver_sees_the_concrete_arguments():
    rendered = _refund(amount="10.00").render()
    assert "amount = '10.00'" in rendered
    assert "reversible: NO" in rendered


def test_a_decision_for_an_unknown_request_is_refused():
    with pytest.raises(PermanentError, match="no such approval"):
        _store().decide("apr_nope", Verdict.APPROVED, decided_by="ana")


# ── P15: when to ask ──────────────────────────────────────────────────────


def test_an_irreversible_action_always_asks_however_confident_everything_else_is():
    """Deleting a customer's data with high confidence is still deleting it."""
    detector = UncertaintyDetector()
    ask, signals = detector.assess(
        Proposal(action="delete_account", summary="Delete", reversible=False),
        support_rate=1.0,
        escalations_exhausted=False,
        guardrail_findings=(),
    )
    assert ask
    assert signals[0].name == "irreversible"


def test_a_confident_reversible_action_does_not_ask():
    """Asking about everything is the same as asking about nothing."""
    ask, signals = UncertaintyDetector().assess(
        Proposal(action="draft_reply", summary="Draft", reversible=True), support_rate=1.0
    )
    assert not ask and signals == ()


def test_weak_signals_accumulate_into_a_question():
    detector = UncertaintyDetector()
    weak_only, _ = detector.assess(
        Proposal(action="send_email", summary="Send", reversible=True), support_rate=0.5
    )
    assert not weak_only  # 0.4 alone is below the 0.6 threshold

    combined, signals = detector.assess(
        Proposal(action="send_email", summary="Send", reversible=True),
        support_rate=0.5,
        guardrail_findings=("unfilled_placeholder",),
    )
    assert combined
    assert {s.name for s in signals} == {"weak_grounding", "guardrail"}


def test_cost_alone_does_not_ask_at_the_default_threshold():
    """A deliberate calibration, stated rather than accidental.

    Cost contributes 0.4 against a 0.6 threshold, so an expensive but otherwise
    clean action proceeds. A product that wants every large spend reviewed sets
    a lower threshold — the point is that this is a dial with a documented
    default, not an emergent property of the weights.
    """
    expensive = Proposal(
        action="bulk_generate",
        summary="Generate 10,000 images",
        reversible=True,
        cost=Money.from_usd("240.00"),
    )
    ask, signals = UncertaintyDetector().assess(expensive, support_rate=1.0)
    assert not ask
    assert [s.name for s in signals] == ["expensive"]  # seen, just not decisive

    stricter, _ = UncertaintyDetector(threshold=0.4).assess(expensive)
    assert stricter
