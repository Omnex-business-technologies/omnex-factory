"""Every `uses:` in this repository's workflows is pinned to a commit SHA.

The check itself is exercised against synthetic text (so a test failure here
always points at the checker, never at whichever workflow happens to be
unpinned that day) and then against the real committed workflows once, to
hold the actual repository state in place.
"""

from __future__ import annotations

import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
sys.path.insert(0, str(ENGINE / "scripts"))

import actions_pin_check  # noqa: E402
import release_check  # noqa: E402


def test_a_tag_pinned_action_is_flagged() -> None:
    workflows = {"fake.yml": "steps:\n  - uses: actions/checkout@v7\n"}
    problems = actions_pin_check.unpinned(workflows)
    assert problems == ["fake.yml: actions/checkout@v7 is not pinned to a commit SHA"]


def test_a_sha_pinned_action_is_not_flagged() -> None:
    sha = "3d3c42e5aac5ba805825da76410c181273ba90b1"
    workflows = {"fake.yml": f"steps:\n  - uses: actions/checkout@{sha} # v7.0.1\n"}
    assert actions_pin_check.unpinned(workflows) == []


def test_a_short_sha_is_still_flagged() -> None:
    """GitHub accepts a short SHA, but it can become ambiguous as a repository
    grows -- only the full 40-character form is unambiguous forever."""
    workflows = {"fake.yml": "steps:\n  - uses: actions/checkout@3d3c42e\n"}
    assert len(actions_pin_check.unpinned(workflows)) == 1


def test_a_branch_name_that_looks_like_a_word_is_flagged() -> None:
    workflows = {"fake.yml": "steps:\n  - uses: actions/checkout@main\n"}
    assert len(actions_pin_check.unpinned(workflows)) == 1


def test_a_commented_out_uses_line_is_not_scanned() -> None:
    """`_uncommented` is reused, not re-implemented -- the same reason a
    prose mention of `branches:` once flipped a different check's verdict."""
    workflows = {"fake.yml": "steps:\n  # - uses: actions/checkout@v7\n"}
    assert actions_pin_check.unpinned(workflows) == []


def test_summarise_counts_match_the_unpinned_list() -> None:
    workflows = {
        "fake.yml": (
            "steps:\n"
            "  - uses: actions/checkout@v7\n"
            "  - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1\n"
        )
    }
    summary = actions_pin_check.summarise(workflows)
    assert summary == {"total_uses": 2, "pinned_to_sha": 1, "unpinned": 1}


def test_the_committed_workflows_have_every_action_pinned() -> None:
    """The actual repository state, held in place."""
    workflows = release_check._workflow_text()
    problems = actions_pin_check.unpinned(workflows)
    assert problems == [], "; ".join(problems)


def test_main_exits_nonzero_when_something_is_unpinned(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        release_check,
        "_workflow_text",
        lambda: {"fake.yml": "steps:\n  - uses: actions/checkout@v7\n"},
    )
    assert actions_pin_check.main() == 1
    assert "FAIL" in capsys.readouterr().out


def test_main_exits_zero_when_everything_is_pinned(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    sha = "3d3c42e5aac5ba805825da76410c181273ba90b1"
    monkeypatch.setattr(
        release_check,
        "_workflow_text",
        lambda: {"fake.yml": f"steps:\n  - uses: actions/checkout@{sha}\n"},
    )
    assert actions_pin_check.main() == 0
