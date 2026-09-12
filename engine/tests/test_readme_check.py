"""README.md's quoted engine test count, checked against the repository.

CLAUDE.md's own "Lab notes" already record this exact drift class happening
to itself four times over. It had never been checked in README.md, which
quoted 1,231 through this session's Phases 1-5 while the real count moved to
1,286 -- found and fixed as part of this file's own existence.
"""

from __future__ import annotations

import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
sys.path.insert(0, str(ENGINE / "scripts"))

import readme_check  # noqa: E402


def test_the_pattern_matches_the_real_sentence() -> None:
    text = "It has its own README, 1,231 tests, zero required dependencies, and is why"
    match = readme_check._QUOTED.search(text)
    assert match is not None
    assert match.group() == "1,231 tests, zero required dependencies"


def test_the_committed_readme_agrees_with_the_repository() -> None:
    """The whole point. If this fails, run readme_check.py -- never hand-edit."""
    real = readme_check.count_engine_tests()
    text = readme_check.README.read_text(encoding="utf-8")
    match = readme_check._QUOTED.search(text)
    assert match is not None, "README.md no longer has a sentence this script recognises"
    quoted = int(match.group().split()[0].replace(",", ""))
    assert quoted == real, f"README.md says {quoted}, the repository has {real}"


def test_count_engine_tests_agrees_with_a_direct_pytest_collection() -> None:
    """Not a second implementation of counting -- both paths run the same
    `pytest --collect-only` command, so this mostly guards against the
    parsing regex silently matching nothing and returning a false zero."""
    assert readme_check.count_engine_tests() > 1000


def test_main_rewrites_a_stale_number(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    fake_readme = tmp_path / "README.md"
    fake_readme.write_text("Some prose. 1 tests, zero required dependencies. More prose.")
    monkeypatch.setattr(readme_check, "README", fake_readme)
    monkeypatch.setattr(readme_check, "count_engine_tests", lambda: 42)

    sys_argv = sys.argv
    try:
        sys.argv = ["readme_check.py"]
        code = readme_check.main()
    finally:
        sys.argv = sys_argv

    assert code == 0
    assert "42 tests, zero required dependencies" in fake_readme.read_text()


def test_main_check_mode_refuses_a_stale_number_without_writing(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    fake_readme = tmp_path / "README.md"
    original = "Some prose. 1 tests, zero required dependencies. More prose."
    fake_readme.write_text(original)
    monkeypatch.setattr(readme_check, "README", fake_readme)
    monkeypatch.setattr(readme_check, "count_engine_tests", lambda: 42)

    sys_argv = sys.argv
    try:
        sys.argv = ["readme_check.py", "--check"]
        code = readme_check.main()
    finally:
        sys.argv = sys_argv

    assert code == 1
    assert fake_readme.read_text() == original, "--check must never write"


def test_main_refuses_when_the_sentence_is_missing(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    fake_readme = tmp_path / "README.md"
    fake_readme.write_text("Nothing about tests here.")
    monkeypatch.setattr(readme_check, "README", fake_readme)
    monkeypatch.setattr(readme_check, "count_engine_tests", lambda: 42)

    code = readme_check.main()
    assert code == 1
