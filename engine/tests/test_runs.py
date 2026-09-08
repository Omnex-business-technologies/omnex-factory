"""The run ledger, and the four ways a ledger stops being evidence.

It can be edited, it can be duplicated, it can copy a secret, and it can record
an expectation after the fact. Each of those turns an audit trail into a
narrative, and each has a test here.

`test_a_fresh_agent_can_recover_without_conversational_memory` is the one that
motivated the file. This session hit a context limit twice, and both times the
next session needed a person to say where it had stopped.
"""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ENGINE = REPO / "engine"
sys.path.insert(0, str(ENGINE / "scripts"))

import runs as ledger  # noqa: E402
from runs import Run  # noqa: E402


def _run(**over: object) -> Run:
    base: dict[str, object] = {
        "run_id": "R-1",
        "session_id": "S-1",
        "agent_id": "claude",
        "timestamp": "2026-09-08T07:00:00Z",
        "objective": "settle C-002",
        "selected_action": "import citegate on 3.11",
        "authorization": "grant L2_LOCAL",
        "autonomy_level": "L2_LOCAL",
        "git_commit_before": "7dc6a35",
        "expected_outcome": "the import succeeds and C-002 becomes SUPPORTED",
    }
    base.update(over)
    return Run(**base)  # type: ignore[arg-type]


# ── duplicate execution ───────────────────────────────────────────────────
def test_appending_the_same_run_twice_does_not_duplicate_it(tmp_path: Path) -> None:
    """A retried step must not read as two units of work — otherwise every
    "cost per accepted change" figure computed from this file is inflated."""
    path = tmp_path / "runs.jsonl"
    ledger.append(_run(), path)
    ledger.append(_run(), path)
    assert len(ledger.load(path)) == 1


# ── tamper evidence ───────────────────────────────────────────────────────
def test_editing_an_earlier_entry_breaks_every_link_after_it(tmp_path: Path) -> None:
    """ "Append-only" becomes a property the file can be tested for rather than
    a convention people are asked to respect."""
    path = tmp_path / "runs.jsonl"
    ledger.append(_run(), path)
    ledger.append(_run(run_id="R-2", objective="settle C-003"), path)
    assert ledger.broken_links(ledger.load(path)) == []

    rows = [json.loads(line) for line in path.read_text().splitlines()]
    rows[0]["objective"] = "something more flattering"
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))

    problems = ledger.broken_links(ledger.load(path))
    assert any("edited, not appended to" in p for p in problems)


def test_the_chain_is_evidence_of_editing_not_proof_against_it() -> None:
    """Stated in the module, because calling it tamper-proof would be the kind
    of claim this repository exists to refuse: a full rewrite recomputing as it
    goes produces a valid chain. Git history is what catches that."""
    doc = ledger.__doc__ or ""
    assert "tamper-**evident**" in doc
    assert "not tamper-proof" in doc


# ── secrets ───────────────────────────────────────────────────────────────
def test_a_run_carrying_a_secret_shaped_value_is_refused(tmp_path: Path) -> None:
    """A ledger that has copied a token has become the incident it records."""
    with pytest.raises(ValueError, match="refusing to write"):
        ledger.append(_run(authorization="Bearer sk-live-9f2a4c8e1b7d"), tmp_path / "r.jsonl")


def test_the_secret_detector_is_the_shared_one() -> None:
    """A second copy would drift from the one the n8n catalogue uses."""
    source = (ENGINE / "scripts" / "runs.py").read_text(encoding="utf-8")
    assert "from omnex.factory.compile.bindings import looks_like_a_secret" in source


# ── outcome ───────────────────────────────────────────────────────────────
def test_expected_outcome_is_required_and_observed_starts_unknown() -> None:
    """An expectation recorded after the result is a description, not a
    prediction — and it cannot be backfilled, which is why the field exists now
    rather than when the learning loop is built."""
    run = _run()
    assert run.expected_outcome
    assert run.observed_outcome == "UNKNOWN"
    assert run.result == "UNKNOWN", "an unmeasured result is unmeasured, never a failure"

    with pytest.raises(TypeError):
        Run(  # type: ignore[call-arg]
            run_id="R",
            session_id="S",
            agent_id="a",
            timestamp="t",
            objective="o",
            selected_action="s",
            authorization="x",
            autonomy_level="L0_OBSERVE",
            git_commit_before="abc",
        )


# ── checkpoint and recovery ───────────────────────────────────────────────
def test_a_checkpoint_names_the_commit_it_describes() -> None:
    """A checkpoint without one describes a state nobody can return to."""
    point = ledger.checkpoint()
    assert point.git_commit
    assert point.checkpoint_id.startswith("cp-")
    assert point.git_commit[:12] in point.checkpoint_id


def test_a_checkpoint_carries_no_timestamp_so_it_does_not_differ_from_itself() -> None:
    """The lesson `execution_state.json` already paid for: a generation time
    changes every run, and then the validator has to learn to ignore a field."""
    first, second = ledger.checkpoint(), ledger.checkpoint()
    assert first == second
    assert not any("time" in f for f in vars(first))


def test_a_fresh_agent_can_recover_without_conversational_memory() -> None:
    """The seven questions, answered from the repository rather than a summary."""
    briefing = ledger.recovery_briefing(ledger.checkpoint())
    for question in (
        "WHERE WE ARE",
        "WHAT IS TRUE",
        "WHAT IS UNKNOWN",
        "WHAT WAS DONE",
        "WHAT FAILED",
        "WHAT IS BLOCKED",
        "WHAT NEXT",
    ):
        assert question in briefing, f"a fresh agent cannot answer {question}"


def test_the_briefing_says_its_next_action_is_a_recommendation() -> None:
    """It is the first thing a fresh agent reads, so it is the likeliest place
    for a suggestion to be mistaken for an instruction."""
    briefing = ledger.recovery_briefing(ledger.checkpoint())
    assert "RECOMMENDATION" in briefing
    assert "not an authorization" in briefing


def test_the_committed_ledger_is_intact() -> None:
    assert ledger.broken_links(ledger.load()) == []


# ── closing a run without editing it ──────────────────────────────────────
def test_an_observation_is_appended_and_never_edits_the_run(tmp_path: Path) -> None:
    """The ledger is hash-chained, so "record the result" cannot be an update.
    What happened is a different fact from what was predicted, at a different
    time, and it gets its own row."""
    path = tmp_path / "runs.jsonl"
    opened = ledger.append(_run(), path)
    closed = ledger.append(
        ledger.observe(opened, result="ok", outcome="it imported", commit_after="deadbee"), path
    )

    rows = ledger.load(path)
    assert len(rows) == 2
    assert rows[0].observed_outcome == "UNKNOWN", "the original row is untouched"
    assert closed.parent_run_id == opened.run_id
    assert ledger.broken_links(rows) == []


def test_a_prediction_may_not_be_revised_while_its_result_is_recorded(tmp_path: Path) -> None:
    """The single way `expected_outcome` could be defeated: quietly improving
    what you said you expected as you write down what occurred."""
    path = tmp_path / "runs.jsonl"
    opened = ledger.append(_run(), path)
    closed = ledger.observe(opened, result="ok", outcome="fine")
    honest = ledger.append(closed, path)
    assert ledger.revised_predictions(ledger.load(path)) == []

    rewritten = replace(honest, expected_outcome="something I never actually predicted")
    problems = ledger.revised_predictions([opened, rewritten])
    assert any("may not be revised" in p for p in problems)


def test_recording_a_run_refuses_without_a_prediction(tmp_path: Path, monkeypatch) -> None:
    """`--expect` is required because now is the only moment it can honestly be
    written. Afterwards it is a description."""
    monkeypatch.setattr(sys, "argv", ["runs", "--record", "--objective", "x", "--action", "y"])
    monkeypatch.setattr(ledger, "LEDGER", tmp_path / "runs.jsonl")
    assert ledger.main() == 1


def test_the_committed_ledger_records_a_prediction_made_before_its_outcome() -> None:
    """R-0001 was written before the work it describes was finished. That is the
    only kind of row this file can honestly contain, and the reason none of the
    61 commits before it were backfilled."""
    rows = ledger.load()
    assert rows, "the ledger has no writer again"
    assert all(r.expected_outcome for r in rows)
    assert ledger.revised_predictions(rows) == []


def test_the_next_run_id_is_the_next_free_one_not_a_row_count() -> None:
    """`len(runs) + 1` was wrong twice: observation rows are entries too, so the
    second run came out R-0003 — a gap that reads like a deletion in an
    append-only file — and once a gap exists the count can land on an id already
    taken. `append` is idempotent on run_id, so that collision would not raise:
    it would return the earlier row and silently drop the new one."""
    rows = [_run(run_id="R-0001"), _run(run_id="R-0001-observed"), _run(run_id="R-0003")]
    assert ledger.next_run_id(rows) == "R-0004"
    assert ledger.next_run_id([]) == "R-0001"


def test_a_colliding_run_id_would_be_silently_dropped(tmp_path: Path) -> None:
    """The reason the generator must never produce a used id. This documents the
    behaviour rather than changing it — idempotency on retry is deliberate."""
    path = tmp_path / "runs.jsonl"
    ledger.append(_run(run_id="R-0001", objective="the real one"), path)
    ledger.append(_run(run_id="R-0001", objective="a different unit of work"), path)

    rows = ledger.load(path)
    assert len(rows) == 1
    assert rows[0].objective == "the real one", "the second was dropped, not merged"
