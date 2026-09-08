"""Deliver once, and only to a request that proved who sent it.

These two steps are the whole difference between a webhook endpoint and a public
URL that spends a GPU budget. They are tested here as the CLI an n8n
`executeCommand` node actually runs, not only as the classes underneath, because
the shape that fails in production is the process boundary: a command that exits
0 on a forged signature, or a store that starts empty every time the process
does.

The defect that produced this file is worth keeping written down. The binding
catalogue shipped naming `python -m omnex.pipeline.verify_webhook` and
`...seen_before` — neither of which existed. A catalogue entry is prose until
something resolves it, and an unresolvable command is worse than an unbound
reference: the workflow imports, the node is not marked a placeholder, and it
fails at the first real order.
"""

from __future__ import annotations

import hashlib
import hmac
import io
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from omnex.core.clock import FakeClock
from omnex.pipeline import Claims
from omnex.pipeline.__main__ import ALREADY_DELIVERED, PROCEED, REFUSED, SECRET_ENV, main

REPO = Path(__file__).resolve().parents[2]
SECRET = "a-signing-secret"


def _signed(body: bytes, at: int, secret: str = SECRET) -> tuple[str, str]:
    signature = hmac.new(secret.encode(), f"{at}.".encode() + body, hashlib.sha256).hexdigest()
    return str(at), signature


def _body(event_id: str = "evt_1", kind: str = "order_created") -> bytes:
    return json.dumps({"id": event_id, "type": kind, "total": 4900}).encode()


def _run(argv: list[str], stdin: bytes = b"", **env: str) -> tuple[int, str]:
    """Drive `main()` in-process, with stdin and the environment it would see."""
    import os

    class _Stdin:
        buffer = io.BytesIO(stdin)

    original_stdin, original_env = sys.stdin, dict(os.environ)
    sys.stdin = _Stdin()  # type: ignore[assignment]
    captured = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = captured
    try:
        os.environ.update(env)
        code = main(argv)
    finally:
        sys.stdin, sys.stdout = original_stdin, original_stdout
        os.environ.clear()
        os.environ.update(original_env)
    return code, captured.getvalue()


# ── the signature gate ────────────────────────────────────────────────────
def test_a_real_signature_proceeds_and_reports_only_the_identifying_fields() -> None:
    """The body is already in n8n; echoing it here copies a paid order into a second log."""
    body = _body()
    timestamp, signature = _signed(body, int(datetime.now(UTC).timestamp()))
    code, out = _run(
        ["verify", "--timestamp", timestamp, "--signature", signature],
        stdin=body,
        **{SECRET_ENV: SECRET},
    )
    assert code == PROCEED
    assert json.loads(out) == {"event_id": "evt_1", "kind": "order_created"}
    assert "4900" not in out


def test_a_forged_signature_is_refused() -> None:
    body = _body()
    timestamp, _ = _signed(body, int(datetime.now(UTC).timestamp()))
    code, out = _run(
        ["verify", "--timestamp", timestamp, "--signature", "0" * 64],
        stdin=body,
        **{SECRET_ENV: SECRET},
    )
    assert code == REFUSED
    assert out == "", "nothing may reach stdout for a request that did not verify"


def test_a_body_changed_after_signing_is_refused() -> None:
    """The failure a signature over the timestamp alone would miss."""
    timestamp, signature = _signed(_body(), int(datetime.now(UTC).timestamp()))
    code, _ = _run(
        ["verify", "--timestamp", timestamp, "--signature", signature],
        stdin=_body("evt_1", "refund_created"),
        **{SECRET_ENV: SECRET},
    )
    assert code == REFUSED


def test_a_captured_request_replayed_later_is_refused() -> None:
    old = int(datetime.now(UTC).timestamp()) - 3600
    body = _body()
    timestamp, signature = _signed(body, old)
    code, _ = _run(
        ["verify", "--timestamp", timestamp, "--signature", signature],
        stdin=body,
        **{SECRET_ENV: SECRET},
    )
    assert code == REFUSED


def test_a_missing_secret_refuses_rather_than_verifying_against_an_empty_one() -> None:
    """An unset variable must not degrade into a check that passes."""
    body = _body()
    timestamp, signature = _signed(body, int(datetime.now(UTC).timestamp()), secret="")
    code, _ = _run(["verify", "--timestamp", timestamp, "--signature", signature], stdin=body)
    assert code == REFUSED


def test_the_secret_can_only_come_from_the_environment() -> None:
    """argv is visible in `ps`, and n8n writes the command it ran into its own log."""
    from omnex.pipeline.__main__ import build_parser

    with pytest.raises(SystemExit):
        build_parser().parse_args(["verify", "--secret", SECRET, "--timestamp", "1", "-s", "x"])


def test_a_payload_with_no_sender_id_is_refused() -> None:
    """Without the sender's id there is no safe key, and a body hash merges two real events."""
    body = json.dumps({"type": "order_created"}).encode()
    timestamp, signature = _signed(body, int(datetime.now(UTC).timestamp()))
    code, _ = _run(
        ["verify", "--timestamp", timestamp, "--signature", signature],
        stdin=body,
        **{SECRET_ENV: SECRET},
    )
    assert code == REFUSED


# ── deliver once ──────────────────────────────────────────────────────────
def test_the_second_delivery_of_one_event_does_not_proceed(tmp_path: Path) -> None:
    store = str(tmp_path / "claims")
    first, _ = _run(["claim", "--store", store, "--event-id", "evt_1"])
    second, out = _run(["claim", "--store", store, "--event-id", "evt_1"])
    assert first == PROCEED
    assert second == ALREADY_DELIVERED
    assert json.loads(out)["first"] is False


def test_a_redelivery_is_not_reported_as_an_error(tmp_path: Path) -> None:
    """Collapsing a retry into the failure code teaches whoever watches to ignore failures."""
    store = str(tmp_path / "claims")
    _run(["claim", "--store", store, "--event-id", "evt_1"])
    code, _ = _run(["claim", "--store", store, "--event-id", "evt_1"])
    assert code != REFUSED
    assert code == ALREADY_DELIVERED


def test_the_claim_survives_the_process_that_made_it(tmp_path: Path) -> None:
    """The whole reason `Claims` exists beside `IdempotencyStore`.

    An n8n node runs a command and the process exits. A dict-backed store starts
    empty on every redelivery and deduplicates nothing, which is exactly the case
    both storefronts produce with their retries.
    """
    store = tmp_path / "claims"
    module = "omnex.pipeline"
    env = {"PYTHONPATH": str(REPO / "engine" / "src")}
    argv = [sys.executable, "-m", module, "claim", "--store", str(store), "--event-id", "evt_1"]
    first = subprocess.run(argv, capture_output=True, env=env, check=False)
    second = subprocess.run(argv, capture_output=True, env=env, check=False)
    assert first.returncode == PROCEED, first.stderr.decode()
    assert second.returncode == ALREADY_DELIVERED


def test_two_claims_of_one_event_cannot_both_win(tmp_path: Path) -> None:
    """Read-then-write would leave the window two simultaneous retries arrive in."""
    claims = Claims(directory=tmp_path / "claims")
    outcomes = [claims.claim("evt_1") for _ in range(8)]
    assert sum(1 for outcome in outcomes if outcome.first) == 1


def test_an_event_id_containing_a_path_cannot_write_outside_the_store(tmp_path: Path) -> None:
    """Event ids come from a sender, and a sender is not trusted with a filename."""
    store = tmp_path / "claims"
    claims = Claims(directory=store)
    claimed = claims.claim("../../escaped")
    assert claimed.first is True
    assert claimed.path.parent == store
    assert not (tmp_path.parent / "escaped").exists()


def test_two_different_ids_that_sanitise_alike_stay_distinct(tmp_path: Path) -> None:
    """Sanitising alone would merge `a/b` and `a-b` into one claim, dropping an order."""
    claims = Claims(directory=tmp_path / "claims")
    assert claims.claim("a/b").first is True
    assert claims.claim("a-b").first is True


def test_an_empty_event_id_is_refused_rather_than_claimed(tmp_path: Path) -> None:
    code, _ = _run(["claim", "--store", str(tmp_path), "--event-id", ""])
    assert code == REFUSED


def test_a_release_lets_a_genuinely_failed_delivery_retry(tmp_path: Path) -> None:
    """Never automatic: "the work failed" is a judgement about the work."""
    claims = Claims(
        directory=tmp_path / "claims", clock=FakeClock(datetime(2026, 9, 4, tzinfo=UTC))
    )
    assert claims.claim("evt_1").first is True
    assert claims.release("evt_1") is True
    assert claims.claim("evt_1").first is True
    assert claims.release("never-claimed") is False


def test_the_claim_records_when_it_was_taken(tmp_path: Path) -> None:
    clock = FakeClock(datetime(2026, 9, 4, 12, 0, tzinfo=UTC))
    claims = Claims(directory=tmp_path / "claims", clock=clock)
    claims.claim("evt_1")
    again = claims.claim("evt_1")
    assert again.claimed_at.startswith("2026-09-04T12:00")


# ── the catalogue names commands that exist ───────────────────────────────
def test_every_command_this_repository_claims_to_own_resolves() -> None:
    """The gate for the defect that produced this file.

    A binding whose `source` is this repository can be resolved from here, so it
    is. One whose source is a storefront cannot, and says so in its own note
    rather than being silently exempt.
    """
    sys.path.insert(0, str(REPO / "engine" / "scripts"))
    import n8n_bindings_check

    from omnex.factory.compile import bindings

    catalogue = bindings.load(REPO / "engine" / "ontology" / "n8n_bindings.json")
    assert n8n_bindings_check.unresolved_commands(catalogue) == []

    ours = [r for r, b in catalogue.bindings.items() if b.source == n8n_bindings_check.OURS]
    assert len(ours) >= 4, "the check passes vacuously if nothing claims to be ours"


def test_a_command_naming_a_module_that_does_not_exist_is_caught(tmp_path: Path) -> None:
    """Proof the check above can fail — it is the exact shape that shipped once."""
    sys.path.insert(0, str(REPO / "engine" / "scripts"))
    import n8n_bindings_check

    from omnex.factory.compile import bindings

    path = tmp_path / "n8n_bindings.json"
    path.write_text(
        json.dumps(
            {
                "node_types": {
                    "command": {"type": "n8n-nodes-base.executeCommand", "type_version": 1}
                },
                "bindings": {
                    "order.verify": {
                        "node_type": "command",
                        "source": n8n_bindings_check.OURS,
                        "parameters": {"command": "python -m omnex.pipeline.verify_webhook"},
                    },
                    "order.dedupe": {
                        "node_type": "command",
                        "source": n8n_bindings_check.OURS,
                        "parameters": {"command": "python -m omnex.pipeline seen_before"},
                    },
                    "pack.ghost": {
                        "node_type": "command",
                        "source": n8n_bindings_check.OURS,
                        "parameters": {"command": "python packs/not_a_file.py"},
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    problems = n8n_bindings_check.unresolved_commands(bindings.load(path))
    assert len(problems) == 3, problems
    assert any("has no __main__" in p for p in problems)
    assert any("is not a subcommand" in p for p in problems)
    assert any("does not exist" in p for p in problems)


def test_the_environment_list_includes_what_a_command_never_spells_out() -> None:
    """Derived from the commands alone it would name everything except the secret."""
    sys.path.insert(0, str(REPO / "engine" / "scripts"))
    import n8n_bindings_check

    from omnex.factory.compile import bindings

    catalogue = bindings.load(REPO / "engine" / "ontology" / "n8n_bindings.json")
    environment = n8n_bindings_check.required_env(catalogue)
    assert SECRET_ENV in environment, "the one variable whose absence stops everything"
    assert environment[SECRET_ENV] == ["order.verify_signature"]
    assert SECRET_ENV not in str(catalogue.bindings["order.verify_signature"].parameters)
