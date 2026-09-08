"""Agent memory: a bounded buffer, durable recall, and eviction that keeps what matters.

Three failures shape this file, and all three are things that happen rather than
things that might.

**Recency-only eviction throws away the important thing first.** "I am allergic
to peanuts", said in turn 2, matters more than the last five turns of
scheduling chatter — and a sliding window drops it precisely because it is old.
So eviction scores on salience as well as recency, and anything PINNED is never
evictable at all. Pinning is the mechanism a product uses for constraints it
must not forget: allergies, account ids, "never email my manager".

**Compression that loses facts is worse than forgetting.** Summarising ten turns
into a paragraph is the standard fix for a full context window, and the standard
result is a summary that reads well and has silently dropped the one number the
next question needs. So compression here EXTRACTS facts rather than paraphrasing
prose, and `preserves()` checks the compressed form still contains them —
verified in the tests against questions the original could answer.

**Cross-session sync with last-write-wins loses data.** Two devices, both
offline, both editing: the later clock wins and the other edit vanishes with no
error anywhere. Entries carry a monotonically increasing version per key, and a
conflict is *reported* rather than resolved silently, because which edit should
win is a product decision and not a storage one.

Everything is token-budgeted rather than turn-budgeted. A window is a token
window; ten short turns and ten long ones are not the same amount of context,
and counting turns is how a system that worked in testing overflows in
production the first time a user pastes a stack trace.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from enum import StrEnum

from ..core.clock import Clock, SystemClock
from ..core.errors import ValidationFailed
from ..core.ids import IdFactory
from ..llm.tokens import HeuristicCounter
from ..llm.types import Message

__all__ = [
    "CompressionResult",
    "EvictionPolicy",
    "LongTermMemory",
    "MemoryEntry",
    "MemoryKind",
    "ShortTermBuffer",
    "compress",
]


class MemoryKind(StrEnum):
    TURN = "turn"
    #: A durable statement about the user or task. Survives compression.
    FACT = "fact"
    #: A compressed stand-in for turns that were evicted.
    SUMMARY = "summary"


@dataclass
class MemoryEntry:
    id: str
    text: str
    kind: MemoryKind = MemoryKind.TURN
    role: str = "user"
    #: Sequence number, not a timestamp. Two entries written in the same
    #: millisecond need a total order, and wall clocks go backwards.
    seq: int = 0
    #: Never evicted. For constraints a product must not forget.
    pinned: bool = False
    #: Times this entry has been retrieved. Frequency is a genuine salience
    #: signal — something referred back to repeatedly is load-bearing.
    hits: int = 0
    tokens: int = 0
    #: Per-key version for cross-session sync. See `LongTermMemory.merge`.
    version: int = 1
    key: str = ""

    @property
    def salience(self) -> float:
        """How much this entry is worth keeping, independent of its age.

        Facts outrank turns because a fact is a distilled claim while a turn is
        mostly conversational filler; repeated retrieval outranks both, because
        the agent itself keeps deciding it needs this.
        """
        base = {MemoryKind.FACT: 2.0, MemoryKind.SUMMARY: 1.5, MemoryKind.TURN: 1.0}[self.kind]
        return base + min(3.0, 0.5 * self.hits)


class EvictionPolicy(StrEnum):
    #: Oldest first. Simple, and drops the allergy.
    RECENCY = "recency"
    #: Least-retrieved first.
    FREQUENCY = "frequency"
    #: Salience weighted by age. The default, and the only one that survives
    #: contact with a real conversation.
    SALIENCE = "salience"


@dataclass
class ShortTermBuffer:
    """A token-bounded working set for one session."""

    max_tokens: int = 4000
    policy: EvictionPolicy = EvictionPolicy.SALIENCE
    counter: HeuristicCounter = field(default_factory=HeuristicCounter)
    ids: IdFactory = field(default_factory=IdFactory)
    entries: list[MemoryEntry] = field(default_factory=list)
    _seq: int = 0
    #: Entries evicted since the last compression, kept so they can be
    #: summarised rather than simply lost.
    evicted: list[MemoryEntry] = field(default_factory=list)

    def add(
        self,
        text: str,
        kind: MemoryKind = MemoryKind.TURN,
        role: str = "user",
        pinned: bool = False,
        key: str = "",
    ) -> MemoryEntry:
        self._seq += 1
        entry = MemoryEntry(
            id=self.ids.new("mem"),
            text=text,
            kind=kind,
            role=role,
            seq=self._seq,
            pinned=pinned,
            tokens=self.counter.estimate(text),
            key=key,
        )
        self.entries.append(entry)
        self._evict()
        return entry

    @property
    def token_count(self) -> int:
        return sum(e.tokens for e in self.entries)

    def _evict(self) -> None:
        while self.token_count > self.max_tokens:
            candidates = [e for e in self.entries if not e.pinned]
            if not candidates:
                # Everything left is pinned. Refusing is right: silently
                # dropping a pinned constraint is the failure pinning exists to
                # prevent, and quietly exceeding the window is the failure the
                # budget exists to prevent.
                raise ValidationFailed(
                    "pinned entries alone exceed the token budget — raise max_tokens "
                    "or unpin something; neither dropping a pin nor overflowing is safe",
                    pinned_tokens=self.token_count,
                    max_tokens=self.max_tokens,
                )
            victim = min(candidates, key=self._eviction_rank)
            self.entries.remove(victim)
            self.evicted.append(victim)

    def _eviction_rank(self, entry: MemoryEntry) -> float:
        """Lower is evicted first."""
        if self.policy is EvictionPolicy.RECENCY:
            return float(entry.seq)
        if self.policy is EvictionPolicy.FREQUENCY:
            return float(entry.hits)
        # Salience, discounted by age. A high-salience entry survives many
        # turns; a plain turn survives a few. The discount is gentle on purpose
        # — steeper and it degenerates into recency, which is the policy this
        # exists to avoid.
        age = self._seq - entry.seq
        return entry.salience - 0.02 * age

    def touch(self, entry_id: str) -> None:
        """Record that an entry was used. Feeds the frequency signal."""
        for entry in self.entries:
            if entry.id == entry_id:
                entry.hits += 1
                return

    def messages(self) -> list[Message]:
        ordered = sorted(self.entries, key=lambda e: e.seq)
        return [Message(role=e.role, content=e.text) for e in ordered]  # type: ignore[arg-type]

    def pinned(self) -> list[MemoryEntry]:
        return [e for e in self.entries if e.pinned]


@dataclass(frozen=True)
class CompressionResult:
    summary: str
    facts: tuple[str, ...]
    original_tokens: int
    compressed_tokens: int

    @property
    def ratio(self) -> float:
        return 0.0 if not self.original_tokens else self.compressed_tokens / self.original_tokens

    def preserves(self, required: Sequence[str]) -> tuple[bool, tuple[str, ...]]:
        """Does the compressed form still contain these facts?

        The check that makes compression safe to run. A summary that reads well
        and dropped the one number the next question needs is the normal outcome
        of paraphrasing, and it is undetectable without asking this directly.
        """
        haystack = (self.summary + " " + " ".join(self.facts)).lower()
        missing = tuple(r for r in required if r.lower() not in haystack)
        return (not missing, missing)


#: Sentences shaped like durable statements rather than conversation.
_FACT_MARKERS = (
    "i am",
    "i'm",
    "my ",
    "we are",
    "we're",
    "our ",
    "always",
    "never",
    "must ",
    "prefer",
    "allergic",
    "budget",
    "deadline",
    "account",
    "id is",
)


def compress(
    entries: Iterable[MemoryEntry], counter: HeuristicCounter | None = None
) -> CompressionResult:
    """Compress turns by EXTRACTING durable statements, not paraphrasing prose.

    Extraction rather than summarisation because extraction cannot invent and
    cannot silently omit a specific: it either keeps a sentence verbatim or it
    does not, and `preserves()` can check which. A generated summary is fluent,
    lossy in ways nobody can enumerate, and costs a model call.

    Deliberately mechanical. A model-written summary reads better; this one is
    auditable, free, and the thing it is protecting — a stated constraint — is
    exactly what a paraphrase blurs.
    """
    counter = counter or HeuristicCounter()
    items = list(entries)
    original = sum(e.tokens for e in items)

    facts: list[str] = []
    for entry in items:
        if entry.kind is MemoryKind.FACT:
            facts.append(entry.text)
            continue
        for sentence in _sentences(entry.text):
            lowered = sentence.lower()
            if any(marker in lowered for marker in _FACT_MARKERS):
                facts.append(sentence.strip())

    # Deduplicate while preserving order — a repeated constraint is one
    # constraint, but the FIRST statement of it is the one to keep, because a
    # later restatement is often a paraphrase that has already lost detail.
    seen: set[str] = set()
    unique: list[str] = []
    for fact in facts:
        lowered = fact.lower()
        if lowered not in seen:
            seen.add(lowered)
            unique.append(fact)

    topics = _topics(items)
    summary = (
        f"Earlier in this conversation ({len(items)} turns): " + ", ".join(topics) + "."
        if topics
        else f"Earlier in this conversation: {len(items)} turns with no durable facts."
    )
    compressed = counter.estimate(summary) + sum(counter.estimate(f) for f in unique)
    return CompressionResult(
        summary=summary,
        facts=tuple(unique),
        original_tokens=original,
        compressed_tokens=compressed,
    )


def _sentences(text: str) -> list[str]:
    from ..rag.ingest import split_sentences

    return split_sentences(text)


def _topics(entries: Sequence[MemoryEntry], limit: int = 6) -> list[str]:
    from ..vectors.embed import tokenize

    counts: dict[str, int] = {}
    for entry in entries:
        for token in tokenize(entry.text):
            if len(token) > 4:
                counts[token] = counts.get(token, 0) + 1
    return [word for word, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]]


@dataclass
class LongTermMemory:
    """Durable, searchable memory that outlives one session.

    Backed by the P12 vector store, so recall is the same hybrid search the RAG
    pipeline uses — one retrieval implementation rather than a second, subtly
    different one that fails in ways the first one's tests do not cover.
    """

    store: object  # VectorStore; typed loosely to avoid a hard import cycle
    tenant: str = ""
    ids: IdFactory = field(default_factory=IdFactory)
    clock: Clock = field(default_factory=SystemClock)
    #: Per-key version numbers, for the sync conflict check.
    versions: dict[str, int] = field(default_factory=dict)

    def remember(self, text: str, key: str = "", pinned: bool = False, **metadata: object) -> str:
        from ..vectors.types import Chunk

        chunk_id = self.ids.new("mem")
        version = self.versions.get(key, 0) + 1 if key else 1
        if key:
            self.versions[key] = version
        self.store.upsert(  # type: ignore[attr-defined]
            [
                Chunk(
                    id=chunk_id,
                    text=text,
                    doc_id=key or chunk_id,
                    metadata={
                        "tenant": self.tenant,
                        "key": key,
                        "pinned": pinned,
                        "version": version,
                        "at": self.clock.now().isoformat(),
                        **metadata,
                    },
                )
            ]
        )
        return chunk_id

    def recall(self, query: str, limit: int = 5) -> list[str]:
        hits = self.store.search(  # type: ignore[attr-defined]
            query, limit=limit, tenant=self.tenant or None
        )
        return [h.chunk.text for h in hits]

    def merge(self, incoming: Sequence[MemoryEntry]) -> list[str]:
        """Merge another session's entries. Returns keys that CONFLICT.

        Conflicts are reported rather than resolved. Last-write-wins loses an
        edit with no error anywhere — two devices, both offline, both editing,
        and one of them silently never happened. Which edit should win is a
        product decision; storage is the wrong layer to make it.
        """
        conflicts: list[str] = []
        for entry in incoming:
            if not entry.key:
                self.remember(entry.text)
                continue
            known = self.versions.get(entry.key, 0)
            if entry.version <= known and known > 0:
                conflicts.append(entry.key)
                continue
            self.versions[entry.key] = entry.version
            self.remember(entry.text, key=entry.key, pinned=entry.pinned)
        return conflicts
