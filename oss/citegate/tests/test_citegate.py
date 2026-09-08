"""Correctness suite for citegate. Each test names a failure it prevents."""

from __future__ import annotations

import time

from citegate import Grounder, Source, Verdict, split_sentences

POOL = [Source(page=12, text="The connection pool defaults to twenty connections.")]
RATE = [Source(page=5, text="The threshold is 4.2% of capacity.")]


def test_a_supported_claim_survives():
    result = Grounder().check("The connection pool defaults to twenty connections. [p. 12]", POOL)
    assert not result.refused
    assert result.checks[0].verdict is Verdict.SUPPORTED


def test_a_citation_to_a_page_never_retrieved_is_dropped():
    """The citation makes the invented claim MORE convincing, not less."""
    result = Grounder().check("The pool defaults to fifty connections. [p. 41]", POOL)
    assert result.refused
    assert result.checks[0].verdict is Verdict.FABRICATED_CITATION


def test_a_claim_the_cited_page_does_not_make_is_dropped():
    result = Grounder().check("The pool scales automatically across regions. [p. 12]", POOL)
    assert result.refused


def test_a_wrong_number_is_caught_even_though_the_wording_matches():
    good = Grounder().check("The threshold is 4.2% of capacity. [p. 5]", RATE)
    bad = Grounder().check("The threshold is 8.4% of capacity. [p. 5]", RATE)
    assert not good.refused
    assert bad.refused and bad.checks[0].missing_numbers == ("8.4",)


def test_a_wrong_quantity_written_as_a_word_is_caught():
    """One swapped content word out of five keeps overlap above threshold."""
    assert Grounder().check("The pool defaults to fifty connections. [p. 12]", POOL).refused


def test_a_silent_unit_conversion_is_not_accepted():
    assert Grounder().check("The threshold is 0.042 of capacity. [p. 5]", RATE).refused


def test_a_cited_sentence_is_always_checked_however_short():
    """Otherwise a two-word invented capability rides through on its citation."""
    result = Grounder().check("It also autoscales. [p. 12]", POOL)
    assert result.refused
    assert result.checks[0].verdict is Verdict.UNSUPPORTED


def test_a_connective_without_a_citation_asserts_nothing():
    result = Grounder().check(
        "In summary: The connection pool defaults to twenty connections. [p. 12]", POOL
    )
    assert not result.refused


def test_an_uncited_factual_sentence_is_dropped():
    result = Grounder().check("The connection pool defaults to twenty connections.", POOL)
    assert result.checks[0].verdict is Verdict.UNCITED


def test_a_partly_grounded_answer_keeps_what_is_supported():
    result = Grounder().check(
        "The pool defaults to twenty connections. [p. 12] "
        "It replicates across three regions. [p. 12]",
        POOL,
    )
    assert "twenty connections" in result.text
    assert "three regions" not in result.text
    assert result.support_rate == 0.5


def test_a_page_range_citation_is_understood():
    spanning = [Source(page=12, page_end=13, text="The pool is exhausted at twenty.")]
    assert not Grounder().check("The pool is exhausted at twenty. [pp. 12-13]", spanning).refused


def test_citations_stay_attached_to_their_sentence():
    """A period, a space and a bracket is exactly the sentence-split pattern."""
    parts = split_sentences("The pool holds twenty. [p. 12] It restarts nightly. [p. 13]")
    assert len(parts) == 2
    assert parts[0].endswith("[p. 12]")


def test_abbreviations_do_not_fragment_a_sentence():
    assert split_sentences("Use a pool, e.g. Postgres. The limit is 20.") == [
        "Use a pool, e.g. Postgres.",
        "The limit is 20.",
    ]


def test_the_documented_limitation_is_real():
    """A swapped polarity word passes. Stated in the README, asserted here."""
    source = [Source(page=1, text="Latency increases when the pool is exhausted.")]
    assert (
        not Grounder().check("Latency decreases when the pool is exhausted. [p. 1]", source).refused
    )
    # An invented entity, by contrast, is caught.
    assert Grounder().check("Latency is governed by the shard router. [p. 1]", source).refused


def test_nothing_supported_means_a_refusal_rather_than_a_plausible_paragraph():
    result = Grounder().check("The pool autoscales to four hundred. [p. 12]", POOL)
    assert result.refused and result.text == ""


def test_splitting_a_long_document_stays_linear_in_its_citations():
    """The regression guard for a quadratic no correctness test could see.

    Citations are masked before splitting and restored afterwards. The original
    restore walked the document's whole citation list once per sentence —
    O(sentences x citations). Correct on every input, which is why 15 passing
    tests never saw it, and invisible on a four-sentence answer, which is the
    only shape bench.py measured. On a 4,000-sentence filing it was 1,439
    sentences/sec where the fixed code does over 300,000.

    Asserted as a growth ratio rather than a wall-clock bound, because an
    absolute threshold on a shared CI runner measures the runner. Eight times
    the input costs eight times the work when linear and sixty-four when
    quadratic; the bound below sits clear of the first and nowhere near the
    second.
    """
    sentence = "The connection pool defaults to twenty connections. [p. 12]"

    def elapsed(count: int) -> float:
        text = " ".join([sentence] * count)
        best = float("inf")
        for _ in range(3):  # best of three: a scheduler blip must not fail a build
            started = time.perf_counter()
            parts = split_sentences(text)
            best = min(best, time.perf_counter() - started)
            assert len(parts) == count
        return best

    small = elapsed(500)
    large = elapsed(4_000)
    assert large / max(small, 1e-6) < 24, "citation restoration has gone superlinear again"

    # And restoration is still correct at size, which is why the slow version
    # existed at all.
    assert split_sentences(" ".join([sentence] * 3)) == [sentence] * 3
