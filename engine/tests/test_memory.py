"""Tests for P13. The allergy test is the one that justifies salience eviction."""

from __future__ import annotations

from random import Random

import pytest

from omnex.core import FakeClock, IdFactory, ValidationFailed
from omnex.memory import (
    EvictionPolicy,
    LongTermMemory,
    MemoryEntry,
    MemoryKind,
    ShortTermBuffer,
    compress,
)
from omnex.vectors import HashingEmbedder, HybridStore

ALLERGY = "I am allergic to peanuts and must never be served them."


def _buffer(**kw) -> ShortTermBuffer:
    return ShortTermBuffer(ids=IdFactory(clock=FakeClock(), rng=Random(1)), **kw)


def test_recency_eviction_drops_the_allergy_and_salience_keeps_it():
    """The whole argument for scoring on salience rather than age."""
    recency = _buffer(max_tokens=120, policy=EvictionPolicy.RECENCY)
    salience = _buffer(max_tokens=120, policy=EvictionPolicy.SALIENCE)

    for buffer in (recency, salience):
        buffer.add(ALLERGY, kind=MemoryKind.FACT)
        for i in range(30):
            buffer.add(f"Can we move the meeting to Tuesday afternoon slot {i}?")

    assert ALLERGY not in [e.text for e in recency.entries], "recency loses it, as expected"
    assert ALLERGY in [e.text for e in salience.entries], "salience keeps it"


def test_a_pinned_entry_is_never_evicted():
    buffer = _buffer(max_tokens=100)
    buffer.add("Account id is ACC-9931.", kind=MemoryKind.FACT, pinned=True)
    for i in range(50):
        buffer.add(f"Some ordinary conversational turn number {i} with filler words.")
    assert any(e.pinned for e in buffer.entries)
    assert "ACC-9931" in " ".join(e.text for e in buffer.entries)


def test_pins_that_alone_exceed_the_budget_fail_loudly_rather_than_silently():
    """Neither dropping a pin nor overflowing the window is safe."""
    buffer = _buffer(max_tokens=20)
    buffer.add("A pinned constraint that is quite long and wordy indeed.", pinned=True)
    with pytest.raises(ValidationFailed, match="pinned entries alone"):
        buffer.add("Another pinned constraint, also long and wordy.", pinned=True)


def test_the_budget_is_tokens_not_turns():
    """Ten short turns and ten long ones are not the same amount of context."""
    buffer = _buffer(max_tokens=200)
    for _ in range(5):
        buffer.add("short")
    assert len(buffer.entries) == 5
    buffer.add("word " * 400)
    assert buffer.token_count <= 200


def test_retrieval_frequency_raises_salience():
    buffer = _buffer(max_tokens=10_000)
    entry = buffer.add("The deployment window is Thursday evening.")
    before = entry.salience
    for _ in range(4):
        buffer.touch(entry.id)
    assert entry.salience > before


def test_compression_preserves_the_facts_a_later_question_needs():
    """A summary that reads well and dropped the number is the normal outcome."""
    buffer = _buffer(max_tokens=10_000)
    buffer.add(ALLERGY)
    buffer.add("My account id is ACC-9931.")
    buffer.add("We must ship before the deadline on 14 March.")
    for i in range(20):
        buffer.add(f"Chatting about the weather and the office plants, turn {i}.")

    result = compress(buffer.entries)
    ok, missing = result.preserves(["allergic to peanuts", "ACC-9931", "14 March"])
    assert ok, f"compression lost: {missing}"
    assert result.ratio < 0.6, "and it actually compressed"


def test_compression_reports_what_it_lost_rather_than_hiding_it():
    buffer = _buffer(max_tokens=10_000)
    for i in range(10):
        buffer.add(f"Purely conversational turn {i} about nothing in particular.")
    result = compress(buffer.entries)
    ok, missing = result.preserves(["a fact that was never stated"])
    assert not ok and missing == ("a fact that was never stated",)


def test_compression_extracts_verbatim_so_it_cannot_invent():
    buffer = _buffer(max_tokens=10_000)
    buffer.add("I prefer morning meetings before ten.")
    result = compress(buffer.entries)
    assert any("prefer morning meetings" in f for f in result.facts)


def test_long_term_recall_uses_the_same_retrieval_as_the_rag_pipeline():
    store = HybridStore(embedder=HashingEmbedder(), candidates=10)
    memory = LongTermMemory(store=store, tenant="acme", ids=IdFactory(clock=FakeClock()))
    memory.remember(ALLERGY, key="dietary")
    memory.remember("The deployment window is Thursday evening.", key="deploy")

    assert any("peanuts" in r for r in memory.recall("food allergies", limit=3))


def test_a_sync_conflict_is_reported_not_silently_resolved():
    """Two devices, both offline, both editing. Last-write-wins loses one."""
    store = HybridStore(embedder=HashingEmbedder())
    memory = LongTermMemory(store=store, tenant="acme", ids=IdFactory(clock=FakeClock()))
    memory.remember("Deadline is 14 March.", key="deadline")  # version 1

    stale = MemoryEntry(id="x", text="Deadline is 20 March.", key="deadline", version=1)
    fresh = MemoryEntry(id="y", text="Deadline is 28 March.", key="deadline", version=2)

    assert memory.merge([stale]) == ["deadline"]  # reported, not applied
    assert memory.merge([fresh]) == []  # newer version wins cleanly


def test_memory_from_another_tenant_is_never_recalled():
    store = HybridStore(embedder=HashingEmbedder(), candidates=10)
    acme = LongTermMemory(store=store, tenant="acme", ids=IdFactory(clock=FakeClock()))
    globex = LongTermMemory(store=store, tenant="globex", ids=IdFactory(clock=FakeClock()))
    acme.remember("Acme's secret deployment key rotation schedule.")
    assert globex.recall("deployment key rotation") == []
