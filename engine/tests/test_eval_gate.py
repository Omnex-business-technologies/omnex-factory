"""`eval_gate.py`'s own CLI — argument parsing and exit code, not `omnex.evals`.

`test_evals.py` already covers `Suite`, `Gate.decide()`, `EvalRunner` and
`Trend` in isolation. Nothing there exercises this script's `main()`: whether
it actually returns 0 when nothing regressed, 1 when something did, and
whether `--record` actually writes a baseline a later run reads back. This
script has run in CI (`quality-gate.yml`) and, since this round, in CLAUDE.md's
own gate block, with none of that covered until now — the same shape of gap
`test_n8n_bindings_check.py` closed for `n8n_bindings_check.py`.

Runs against the real, committed `suites/rag_core.json` and its corpus rather
than a synthetic suite: the point is proving THIS script's plumbing (argument
parsing, `--record`, the exit code), and the real suite is small and
deterministic (`ScriptedModel`, no network), so nothing is gained by
inventing a second one.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE / "scripts"))
sys.path.insert(0, str(ENGINE / "src"))

import eval_gate  # noqa: E402


def _run(monkeypatch, argv: list[str]) -> int:
    monkeypatch.chdir(ENGINE)
    monkeypatch.setattr(sys, "argv", ["eval_gate.py", *argv])
    return eval_gate.main()


def test_a_first_run_with_no_baseline_passes(tmp_path, monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    baseline = tmp_path / "baseline.json"
    code = _run(
        monkeypatch,
        ["--baseline", str(baseline), "--out", str(tmp_path / "runs"), "--label", "test"],
    )
    assert code == 0
    assert "no baseline; recording" in capsys.readouterr().out
    assert not baseline.exists(), "a plain run must not write the baseline; only --record may"


def test_record_writes_a_baseline_a_later_run_reads_back(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    baseline = tmp_path / "baseline.json"
    out = tmp_path / "runs"

    recorded = _run(monkeypatch, ["--baseline", str(baseline), "--out", str(out), "--record"])
    assert recorded == 0
    assert baseline.exists()

    # The real answerer is deterministic (ScriptedModel, no network, no
    # regeneration) -- comparing a fresh run against the baseline it just
    # wrote must show zero drift and pass again.
    unchanged = _run(monkeypatch, ["--baseline", str(baseline), "--out", str(out)])
    assert unchanged == 0


def test_a_regression_against_the_baseline_fails_the_gate(tmp_path, monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    """Sabotage-verified: record a real baseline, then edit ONE result so the
    baseline claims a case passed that the real (deterministic) run still
    fails -- the exact shape `Gate.decide()` calls a regression."""
    baseline = tmp_path / "baseline.json"
    out = tmp_path / "runs"
    assert _run(monkeypatch, ["--baseline", str(baseline), "--out", str(out), "--record"]) == 0

    payload = json.loads(baseline.read_text())
    failing = next(
        r for r in payload["results"] if r["metrics"].get("answer_relevancy", 1.0) == 0.0
    )
    for name in failing["metrics"]:
        failing["metrics"][name] = 1.0
    baseline.write_text(json.dumps(payload))

    code = _run(monkeypatch, ["--baseline", str(baseline), "--out", str(out)])
    assert code == 1
    output = capsys.readouterr().out
    assert failing["case_id"] in output


def test_out_of_the_box_defaults_run_against_the_real_suite(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """No flags but --baseline/--out redirected: the real suite and corpus
    this repository ships load and run under the script's own defaults."""
    code = _run(monkeypatch, ["--baseline", str(tmp_path / "b.json"), "--out", str(tmp_path / "r")])
    assert code == 0
