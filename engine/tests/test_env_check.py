"""The variables a deploy cannot run without, and the two ways that list rots.

Almost every one of these fails CLOSED — `cron-auth` returns false when unset,
`isOwner` refuses below sixteen characters, the Stripe routes answer 503. That is
the right direction, and it is why the failure is invisible: the site is up, the
pages render, and the feature is simply never reachable.

So the manifest is checked against the code in both directions, which is the same
argument `test_ci_contract.py` makes about the gate block, with the same stated
boundary: comparing two sides cannot see a variable missing from both.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import env_check  # noqa: E402


def _manifest() -> dict[str, object]:
    return env_check.load_manifest()


# ── the manifest and the code agree ───────────────────────────────────────
def test_no_variable_the_code_reads_is_undocumented() -> None:
    """An undocumented requirement is one an operator finds out about from an outage."""
    report = env_check.check(_manifest(), env_check.used_in_code())
    assert report.used_but_undocumented == []


def test_no_documented_variable_has_stopped_being_read() -> None:
    """A stale entry is an instruction somebody will follow for nothing."""
    report = env_check.check(_manifest(), env_check.used_in_code())
    assert report.documented_but_unused == []


def test_the_drift_check_can_fail_in_both_directions() -> None:
    """A check that only ever passes has not been shown to check anything."""
    manifest: dict[str, object] = {"vars": {"KEPT": {"required": False}, "STALE": {}}}
    report = env_check.check(manifest, {"KEPT", "NEW"})
    assert report.used_but_undocumented == ["NEW"]
    assert report.documented_but_unused == ["STALE"]
    assert report.manifest_drifted is True


def test_the_code_scan_finds_something_at_all() -> None:
    """Guards the vacuous pass: a scanner that reads no files agrees with everything."""
    used = env_check.used_in_code()
    assert len(used) > 20, "the scan found almost nothing; the drift check is vacuous"
    assert "STRIPE_SECRET_KEY" in used


# ── the runtime half ──────────────────────────────────────────────────────
def test_a_required_variable_that_is_unset_fails() -> None:
    manifest = _manifest()
    required = [n for n, e in manifest["vars"].items() if e.get("required")]  # type: ignore[union-attr,attr-defined]
    assert required, "nothing is marked required; the runtime check would pass empty"
    report = env_check.check(manifest, env_check.used_in_code(), environment={})
    assert report.missing_required == sorted(required)
    assert report.host_incomplete is True


def test_a_variable_set_to_whitespace_counts_as_unset() -> None:
    """A blank in a dashboard field looks configured and behaves exactly like absent."""
    manifest: dict[str, object] = {"vars": {"CRON_SECRET": {"required": True}}}
    assert env_check.check(
        manifest, {"CRON_SECRET"}, environment={"CRON_SECRET": "   "}
    ).missing_required == ["CRON_SECRET"]
    assert (
        env_check.check(
            manifest, {"CRON_SECRET"}, environment={"CRON_SECRET": "x"}
        ).missing_required
        == []
    )


def test_a_group_needs_only_one_of_its_members() -> None:
    """Studio with no image backend is live, billable and unable to produce anything.

    No single provider key can be marked required — the whole point of the
    adapters is that any one of them will do — so the constraint that matters is
    a group, and a per-variable flag cannot express it.
    """
    manifest: dict[str, object] = {
        "vars": {},
        "groups": {"an image model": {"any_of": ["FAL_KEY", "REPLICATE_API_TOKEN"]}},
    }
    assert env_check.check(manifest, set(), environment={}).unsatisfied_groups
    assert not env_check.check(manifest, set(), environment={"FAL_KEY": "k"}).unsatisfied_groups


def test_the_shipped_manifest_declares_the_image_group() -> None:
    groups: dict[str, object] = _manifest()["groups"]  # type: ignore[assignment]
    assert groups, "the group rule exists and nothing uses it"
    options = {name for group in groups.values() for name in group["any_of"]}  # type: ignore[index]
    assert options <= env_check.used_in_code(), "a group names a variable nothing reads"


# ── nothing prints a value ────────────────────────────────────────────────
def test_a_secret_never_reaches_the_report(capsys, monkeypatch) -> None:
    """A preflight that prints a key to a build log has copied the secret, not checked it.

    Runs the real `--runtime` path with real-looking values in the environment
    and requires that none of them appear anywhere in the output — not whole,
    not as a prefix, not as a length.
    """
    planted = {
        "STRIPE_SECRET_KEY": "sk_live_51ABCdefGHIjklMNO",
        "CRON_SECRET": "a-cron-secret-nobody-should-see",
        "SUPABASE_SERVICE_ROLE_KEY": "service-role-token-value",
    }
    for name, value in planted.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setattr(sys, "argv", ["env_check.py", "--runtime"])

    env_check.main()
    printed = capsys.readouterr().out
    for name, value in planted.items():
        assert name in printed, f"{name} is not even reported"
        assert value not in printed
        assert value[:8] not in printed


def test_the_manifest_marks_the_credentials_as_secret() -> None:
    """`secret` is what tells an operator which of these may not go in a NEXT_PUBLIC_ name."""
    variables: dict[str, dict[str, object]] = _manifest()["vars"]  # type: ignore[assignment]
    for name in ("STRIPE_SECRET_KEY", "SUPABASE_SERVICE_ROLE_KEY", "CRON_SECRET"):
        assert variables[name]["secret"] is True, name
    for name, entry in variables.items():
        if name.startswith("NEXT_PUBLIC_"):
            assert entry["secret"] is False, (
                f"{name} is marked secret and is compiled into the browser bundle"
            )


def test_every_documented_variable_says_why() -> None:
    """Without a reason, "required" is a rule nobody can weigh against an outage."""
    variables: dict[str, dict[str, object]] = _manifest()["vars"]  # type: ignore[assignment]
    thin = sorted(n for n, e in variables.items() if len(str(e.get("why", ""))) < 30)
    assert thin == [], thin


# ── the n8n side is derived, not copied ───────────────────────────────────
def test_the_n8n_variables_come_from_the_binding_catalogue() -> None:
    """A second copy of a list that is already data drifts the moment a binding changes."""
    derived = env_check.n8n_environment()
    assert "OMNEX_WEBHOOK_SECRET" in derived
    documented: dict[str, object] = _manifest()["vars"]  # type: ignore[assignment]
    assert not (set(derived) & set(documented)), (
        "an n8n variable was also typed into deploy/env.json; that is the copy "
        "this split exists to prevent"
    )


def test_the_manifest_is_valid_json_with_a_stated_reason() -> None:
    raw = json.loads((REPO / "deploy" / "env.json").read_text(encoding="utf-8"))
    assert raw["version"] == 1
    assert any("fail" in line.lower() for line in raw["why"])
