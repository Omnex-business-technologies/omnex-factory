"""The store: hybrid search, and why the metadata filter runs first.

The single most common correctness bug in a filtered vector search is
**post-filtering**: retrieve the top 10 by similarity, then drop the ones whose
metadata does not match. It returns fewer than 10 results — sometimes zero — and
nothing errors. Worse, it is *silently tenant-dependent*: a large tenant's
documents crowd the top 10, so a small tenant's query returns nothing at all
while an identical query for the large tenant works. The bug reproduces only for
customers you have few documents for, which is to say new ones.

So `search()` applies the filter to the candidate set BEFORE ranking. In this
in-process store that is exact. Against a real ANN index it becomes either a
pushed-down filter (Qdrant supports this natively) or over-fetching by a factor
and filtering — and the adapter says which, because the two have different
recall characteristics and the difference is not a detail.

`tenant` is a first-class argument rather than one metadata key among many.
Making it optional is how a cross-tenant leak gets written: one query builder
that forgot to add the filter is enough, and it will not be found by tests that
only ever use one tenant. Here, omitting it searches nothing rather than
everything — the failure direction that produces an empty result and a bug
report, not a data breach.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from ..core.errors import TenantIsolationViolation, ValidationFailed
from .bm25 import Bm25Index
from .embed import Embedder, cosine
from .fusion import reciprocal_rank_fusion
from .types import Chunk, Filter, SearchHit, matches_filter

__all__ = ["HybridStore", "SearchMode", "VectorStore"]

SearchMode = str  # "hybrid" | "dense" | "lexical"


@runtime_checkable
class VectorStore(Protocol):
    def upsert(self, chunks: Sequence[Chunk]) -> int: ...
    def delete(self, chunk_ids: Sequence[str]) -> int: ...
    def search(
        self,
        query: str,
        limit: int = 10,
        where: Filter | None = None,
        tenant: str | None = None,
        mode: SearchMode = "hybrid",
    ) -> list[SearchHit]: ...
    def count(self, tenant: str | None = None) -> int: ...


@dataclass
class HybridStore:
    """BM25 + dense vectors + RRF, in process.

    The reference implementation: every other backend is checked against this
    one's behaviour, and it is what the tests for P1 retrieve through.

    **Single-writer. Not thread-safe, on purpose.** Indexing mutates the posting
    lists and the vector table together, and guarding that would put a lock on
    the read path of a retriever whose whole point is speed. Index from one
    thread, or index into a fresh store and swap the reference — an atomic
    rebind, which is cheaper than a lock and is how a search index is usually
    updated anyway.

    Stated here rather than discovered in production. `obs.CostLedger` and
    `factory.AgentEconomics` ARE locked, because losing an event there loses
    money; losing a concurrent write here loses a document, which a re-index
    restores.
    """

    embedder: Embedder
    #: Candidates each retriever contributes before fusion. Larger than the
    #: final limit on purpose — fusion can only reorder what it is given, so
    #: a document ranked 15th by BM25 and 2nd by the dense side is invisible
    #: to the fused result if each side only offered its top 10.
    candidates: int = 50
    #: Relative influence in fusion. Equal by default: an unmeasured weighting
    #: is a preference dressed up as a tuning parameter.
    weights: dict[str, float] = field(default_factory=lambda: {"lexical": 1.0, "dense": 1.0})
    #: Refuse un-scoped searches. Turning this off is a deliberate act.
    require_tenant: bool = False

    _chunks: dict[str, Chunk] = field(default_factory=dict)
    _vectors: dict[str, list[float]] = field(default_factory=dict)
    _lexical: Bm25Index = field(default_factory=Bm25Index)

    # ── writes ────────────────────────────────────────────────────────────
    def upsert(self, chunks: Sequence[Chunk]) -> int:
        if not chunks:
            return 0
        vectors = self.embedder.embed([c.text for c in chunks])
        for chunk, vector in zip(chunks, vectors, strict=True):
            if len(vector) != self.embedder.dimensions:
                raise ValidationFailed(
                    "embedder returned the wrong dimensionality",
                    expected=self.embedder.dimensions,
                    got=len(vector),
                )
            self._chunks[chunk.id] = chunk
            self._vectors[chunk.id] = vector
            self._lexical.add(chunk.id, chunk.text)
        return len(chunks)

    def delete(self, chunk_ids: Sequence[str]) -> int:
        removed = 0
        for chunk_id in chunk_ids:
            if self._chunks.pop(chunk_id, None) is not None:
                self._vectors.pop(chunk_id, None)
                self._lexical.remove(chunk_id)
                removed += 1
        return removed

    def clear(self) -> None:
        self._chunks.clear()
        self._vectors.clear()
        self._lexical = Bm25Index()

    # ── reads ─────────────────────────────────────────────────────────────
    def count(self, tenant: str | None = None) -> int:
        if tenant is None:
            return len(self._chunks)
        return sum(1 for c in self._chunks.values() if c.metadata.get("tenant") == tenant)

    def search(
        self,
        query: str,
        limit: int = 10,
        where: Filter | None = None,
        tenant: str | None = None,
        mode: SearchMode = "hybrid",
    ) -> list[SearchHit]:
        if self.require_tenant and tenant is None:
            raise TenantIsolationViolation(
                "search requires an explicit tenant; refusing to search across all tenants"
            )

        # PRE-filter. Ranking then filtering returns fewer than `limit` results
        # and does so in a tenant-dependent way — see the module docstring.
        allowed = self._candidate_ids(where, tenant)
        if not allowed:
            return []

        rankings: dict[str, list[tuple[str, float]]] = {}
        if mode in ("hybrid", "lexical"):
            rankings["lexical"] = [
                (doc_id, score)
                for doc_id, score in self._lexical.search(query, limit=self.candidates * 4)
                if doc_id in allowed
            ][: self.candidates]
        if mode in ("hybrid", "dense"):
            rankings["dense"] = self._dense_search(query, allowed)

        if mode == "lexical":
            return self._as_hits(rankings["lexical"], "lexical", limit)
        if mode == "dense":
            return self._as_hits(rankings["dense"], "dense", limit)

        return reciprocal_rank_fusion(rankings, self._chunks, weights=self.weights, limit=limit)

    def _candidate_ids(self, where: Filter | None, tenant: str | None) -> set[str]:
        combined: Filter = dict(where or {})
        if tenant is not None:
            # Set last so a caller-supplied `where` cannot override the tenant
            # scope — the one filter that must never be negotiable.
            combined["tenant"] = tenant
        if not combined:
            return set(self._chunks)
        return {
            chunk_id
            for chunk_id, chunk in self._chunks.items()
            if matches_filter(chunk.metadata, combined)
        }

    def _dense_search(self, query: str, allowed: set[str]) -> list[tuple[str, float]]:
        query_vector = self.embedder.embed([query])[0]
        scored = [
            (chunk_id, cosine(query_vector, self._vectors[chunk_id]))
            for chunk_id in allowed
            if chunk_id in self._vectors
        ]
        scored.sort(key=lambda kv: (-kv[1], kv[0]))
        return scored[: self.candidates]

    def _as_hits(
        self, ranking: Sequence[tuple[str, float]], name: str, limit: int
    ) -> list[SearchHit]:
        return [
            SearchHit(
                chunk=self._chunks[chunk_id],
                score=score,
                components={name: score},
                ranks={name: position},
            )
            for position, (chunk_id, score) in enumerate(ranking[:limit], start=1)
            if chunk_id in self._chunks
        ]

    # ── introspection, for backup and for tests ───────────────────────────
    def all_chunks(self) -> list[Chunk]:
        return list(self._chunks.values())

    def vector_of(self, chunk_id: str) -> list[float] | None:
        return self._vectors.get(chunk_id)
