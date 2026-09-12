"""split_reasoning: the one place a reasoning model's <think> block gets parsed out."""

from __future__ import annotations

from omnex.llm.reasoning import split_reasoning


def test_text_with_no_think_block_passes_through_unchanged() -> None:
    answer, reasoning = split_reasoning("Paris is the capital of France.")
    assert answer == "Paris is the capital of France."
    assert reasoning == ""


def test_a_single_think_block_is_removed_from_the_answer() -> None:
    text = "<think>The user wants the capital.</think>Paris is the capital of France."
    answer, reasoning = split_reasoning(text)
    assert answer == "Paris is the capital of France."
    assert reasoning == "The user wants the capital."


def test_a_think_block_spanning_multiple_lines_is_captured_whole() -> None:
    text = "<think>\nStep one.\nStep two.\n</think>\nFinal answer."
    answer, reasoning = split_reasoning(text)
    assert answer == "Final answer."
    assert "Step one." in reasoning
    assert "Step two." in reasoning


def test_multiple_think_blocks_are_all_kept_not_only_the_first() -> None:
    """A naive split(<think>, 1) would drop everything after the first close tag."""
    text = "<think>first pass</think>partial.<think>second pass</think>final answer."
    answer, reasoning = split_reasoning(text)
    assert answer == "partial.final answer."
    assert "first pass" in reasoning
    assert "second pass" in reasoning


def test_matching_is_case_insensitive() -> None:
    text = "<THINK>loud thinking</THINK>quiet answer."
    answer, reasoning = split_reasoning(text)
    assert answer == "quiet answer."
    assert reasoning == "loud thinking"
