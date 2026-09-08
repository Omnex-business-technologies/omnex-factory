"""What an install promises, and the six extras that promised nothing.

`pip install omnex-engine[agents]` installs langgraph and crewai. No module here
imports either. The install succeeds, the extra looks delivered, and the user has
two large dependencies and no capability — the same shape as a listing that sells
170 images against 80, which this repository already gates from the other side.

The measurement that produced this file: **six of twelve extras had zero of their
declared dependencies imported anywhere** — `api`, `memory`, `worker`, `agents`,
`evals`, `finetune`. Two docstrings made it worse by naming adapter modules that
have never existed.

The fix is not six adapters. An extra nobody backs is evidence of an intended
interface, not proof the interface should exist, so `unsupported` with a stated
reason is an accepted state and silence is not.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ENGINE = REPO / "engine"
sys.path.insert(0, str(ENGINE / "scripts"))

import extras_check  # noqa: E402


def _manifest() -> dict[str, object]:
    return tomllib.loads((ENGINE / "pyproject.toml").read_text(encoding="utf-8"))


# ── the shipped manifest agrees with the code ─────────────────────────────
def test_every_declared_extra_says_what_it_delivers() -> None:
    report = extras_check.check(_manifest(), extras_check.importers())
    assert report.problems == []


def test_no_adapter_named_in_prose_is_missing() -> None:
    """`graph/runtime.py` pointed at a langgraph adapter; the file never existed."""
    assert extras_check.prose_adapters() == []


def test_the_import_scan_finds_the_adapters_that_do_exist() -> None:
    """Guards the vacuous pass: a scanner reading nothing agrees with everything."""
    found = extras_check.importers()
    assert found.get("litellm") == "omnex.llm.litellm_adapter"
    assert found.get("qdrant_client") == "omnex.vectors.qdrant_store"
    assert found.get("opentelemetry") == "omnex.obs.export"


def test_an_indented_import_still_counts() -> None:
    """Every optional dependency here is imported inside a function, by design.

    A scan that only saw module-scope imports would call the entire adapter layer
    missing — `pdfplumber` is imported inside `rag/figures.py`'s reader, not at
    the top of it.
    """
    assert extras_check.importers().get("pdfplumber") == "omnex.rag.figures"


# ── the measurement this file was written for ─────────────────────────────
def test_six_extras_deliver_no_capability_and_say_so() -> None:
    """The finding, kept as a test so it cannot quietly change.

    If one of these becomes backed, this premise is stale and the count in the
    docstrings is too — which is the point of asserting the number rather than
    the property.
    """
    described: dict[str, dict[str, object]] = _manifest()["tool"]["omnex"]["extras"]  # type: ignore[index,assignment]
    unsupported = sorted(k for k, v in described.items() if v.get("status") == "unsupported")
    assert unsupported == ["agents", "api", "evals", "finetune", "memory", "worker"]

    report = extras_check.check(_manifest(), extras_check.importers())
    for extra in unsupported:
        assert not any(report.backing[extra].values()), f"{extra} is backed after all"


def test_every_non_supported_extra_carries_a_reason() -> None:
    """Without one, a deliberate placeholder is indistinguishable from an oversight."""
    described: dict[str, dict[str, object]] = _manifest()["tool"]["omnex"]["extras"]  # type: ignore[index,assignment]
    for extra, entry in sorted(described.items()):
        if entry.get("status") in {"supported", "tooling"}:
            continue
        assert len(str(entry.get("why", ""))) >= 40, extra


# ── proof the check can fail, one shape per rule ──────────────────────────
def _fake(status: str, deps: list[str], **entry: object) -> dict[str, object]:
    return {
        "project": {"optional-dependencies": {"thing": deps}},
        "tool": {"omnex": {"extras": {"thing": {"status": status, **entry}}}},
    }


def test_supported_with_nothing_importing_it_fails() -> None:
    """The exact state `agents` was in: declared, installed, and inert."""
    report = extras_check.check(_fake("supported", ["langgraph>=0.2"]), {})
    assert not report
    assert any("delivers a dependency and no capability" in p for p in report.problems)


def test_unsupported_while_something_imports_it_fails() -> None:
    """A status that understates what exists is still a status that misleads."""
    report = extras_check.check(
        _fake("unsupported", ["litellm>=1.5"], why="x" * 50),
        {"litellm": "omnex.llm.litellm_adapter"},
    )
    assert any("understates what exists" in p for p in report.problems)


def test_a_partial_whose_unused_list_drifted_fails() -> None:
    """The list and the code must agree, or the list is a second copy of the truth."""
    report = extras_check.check(
        _fake("partial", ["litellm>=1.5", "redis>=5"], unused=["numpy"], why="x" * 50),
        {"litellm": "omnex.llm.litellm_adapter"},
    )
    assert any("drifted from the code" in p for p in report.problems)


def test_a_partial_that_is_really_supported_or_unsupported_fails() -> None:
    """`partial` must mean partial; either end of the range is a different claim."""
    whole = extras_check.check(
        _fake("partial", ["litellm>=1.5"], why="x" * 50),
        {"litellm": "omnex.llm.litellm_adapter"},
    )
    assert any("it is supported" in p for p in whole.problems)

    none = extras_check.check(_fake("partial", ["redis>=5"], why="x" * 50), {})
    assert any("it is unsupported" in p for p in none.problems)


def test_a_reason_that_says_nothing_fails() -> None:
    report = extras_check.check(_fake("unsupported", ["redis>=5"], why="TODO"), {})
    assert any("no usable reason" in p for p in report.problems)


def test_drift_is_caught_in_both_directions() -> None:
    """An undescribed extra and a stale description are different failures."""
    undescribed: dict[str, object] = {
        "project": {"optional-dependencies": {"ghost": ["redis>=5"]}},
        "tool": {"omnex": {"extras": {}}},
    }
    assert any("nobody has described" in p for p in extras_check.check(undescribed, {}).problems)

    stale: dict[str, object] = {
        "project": {"optional-dependencies": {}},
        "tool": {"omnex": {"extras": {"ghost": {"status": "supported"}}}},
    }
    assert any("stale entry" in p for p in extras_check.check(stale, {}).problems)


def test_an_unknown_status_is_refused(tmp_path: Path) -> None:
    report = extras_check.check(_fake("probably-fine", ["redis>=5"]), {})
    assert any("expected one of" in p for p in report.problems)


def test_a_backticked_adapter_with_no_file_is_caught(tmp_path: Path) -> None:
    """Proof the prose check works, on a tree built for it.

    A backticked `*_adapter.py` is a claim that the file exists. Prose about an
    adapter that does not exist uses plain words — which is why parsing negation
    was not attempted: a check that has to read "never existed" out of a sentence
    fails in the direction of passing.
    """
    (tmp_path / "omnex").mkdir()
    (tmp_path / "omnex" / "runtime.py").write_text(
        '"""See `ghost_adapter.py` for the production path."""\n', encoding="utf-8"
    )
    assert len(extras_check.prose_adapters(tmp_path / "omnex")) == 1

    (tmp_path / "omnex" / "ghost_adapter.py").write_text("", encoding="utf-8")
    assert extras_check.prose_adapters(tmp_path / "omnex") == []


# ── running it twice changes nothing ──────────────────────────────────────
def test_the_check_is_idempotent() -> None:
    """A verification script that mutates state is not a verification script."""
    first = extras_check.check(_manifest(), extras_check.importers())
    second = extras_check.check(_manifest(), extras_check.importers())
    assert first.problems == second.problems
    assert first.backing == second.backing


@pytest.mark.parametrize(
    ("spec", "expected"),
    [
        ("opentelemetry-sdk>=1.27", "opentelemetry-sdk"),
        ("uvicorn[standard]>=0.32", "uvicorn"),
        ("torch>=2.5", "torch"),
        ("redis", "redis"),
    ],
)
def test_a_requirement_string_reduces_to_its_name(spec: str, expected: str) -> None:
    assert extras_check._requirement_name(spec) == expected
