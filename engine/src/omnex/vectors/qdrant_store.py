"""Qdrant adapter — the scale path, with the filtering difference made explicit.

SQLite is the right choice until it is not. The crossover is roughly where a
brute-force scan stops fitting in the latency budget: a few million vectors at
768 dimensions, or sooner if queries are concurrent. Qdrant is the open-source
option that changes the least about the code above it, and the one thing it
changes matters enough to state here rather than bury.

**Filtering is pushed down, not applied afterwards.** Qdrant evaluates the
payload filter inside the HNSW traversal, so a filtered search returns `limit`
matching results rather than "however many of the top `limit` happened to
match". That is the same property `HybridStore` gives exactly, achieved a
different way — and it is why this adapter uses `query_filter` rather than
fetching and filtering in Python, which would reintroduce the post-filter bug
the store layer exists to avoid.

The lexical half stays in-process. Qdrant has sparse-vector support, but running
BM25 here keeps one scoring implementation across every backend, so a hybrid
result cannot differ between the local and the scaled deployment for reasons
nobody can reproduce locally.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from ..core.errors import ConfigurationError, TenantIsolationViolation
from .bm25 import Bm25Index
from .embed import Embedder
from .fusion import reciprocal_rank_fusion
from .types import Chunk, Filter, SearchHit

__all__ = ["QdrantStore"]


class QdrantStore:
    """A `VectorStore` backed by Qdrant, with BM25 kept in process."""

    def __init__(
        self,
        collection: str,
        embedder: Embedder,
        url: str = "http://localhost:6333",
        api_key: str = "",
        candidates: int = 50,
        require_tenant: bool = True,
        weights: dict[str, float] | None = None,
    ) -> None:
        self.collection = collection
        self.embedder = embedder
        self.candidates = candidates
        self.require_tenant = require_tenant
        self.weights = weights or {"lexical": 1.0, "dense": 1.0}
        self._lexical = Bm25Index()
        self._chunks: dict[str, Chunk] = {}
        self._client = self._connect(url, api_key)
        self._ensure_collection()

    @staticmethod
    def _connect(url: str, api_key: str) -> Any:
        try:
            from qdrant_client import QdrantClient
        except ImportError as exc:  # pragma: no cover - only without the extra
            raise ConfigurationError(
                "QdrantStore needs the 'vectors' extra: pip install 'omnex-engine[vectors]'"
            ) from exc
        return QdrantClient(url=url, api_key=api_key or None)

    def _ensure_collection(self) -> None:
        from qdrant_client.models import Distance, VectorParams

        existing = {c.name for c in self._client.get_collections().collections}
        if self.collection in existing:
            return
        self._client.create_collection(
            collection_name=self.collection,
            # Cosine, matching HybridStore, so switching backends does not
            # silently change what "similar" means.
            vectors_config=VectorParams(size=self.embedder.dimensions, distance=Distance.COSINE),
        )
        # A payload index on the tenant field. Without it, the pushed-down
        # filter degrades to a full payload scan and the latency win of moving
        # to Qdrant at all is spent on the filter.
        self._client.create_payload_index(
            collection_name=self.collection, field_name="tenant", field_schema="keyword"
        )

    # ── writes ────────────────────────────────────────────────────────────
    def upsert(self, chunks: Sequence[Chunk]) -> int:
        from qdrant_client.models import PointStruct

        if not chunks:
            return 0
        vectors = self.embedder.embed([c.text for c in chunks])
        points = [
            PointStruct(
                id=_point_id(chunk.id),
                vector=vector,
                payload={
                    "chunk_id": chunk.id,
                    "doc_id": chunk.doc_id,
                    "text": chunk.text,
                    "page": chunk.page,
                    "span": list(chunk.char_span),
                    "tenant": str(chunk.metadata.get("tenant", "")),
                    **chunk.metadata,
                },
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        self._client.upsert(collection_name=self.collection, points=points, wait=True)
        for chunk in chunks:
            self._chunks[chunk.id] = chunk
            self._lexical.add(chunk.id, chunk.text)
        return len(chunks)

    def delete(self, chunk_ids: Sequence[str]) -> int:
        from qdrant_client.models import PointIdsList

        self._client.delete(
            collection_name=self.collection,
            points_selector=PointIdsList(points=[_point_id(i) for i in chunk_ids]),
            wait=True,
        )
        removed = 0
        for chunk_id in chunk_ids:
            if self._chunks.pop(chunk_id, None) is not None:
                self._lexical.remove(chunk_id)
                removed += 1
        return removed

    # ── reads ─────────────────────────────────────────────────────────────
    def search(
        self,
        query: str,
        limit: int = 10,
        where: Filter | None = None,
        tenant: str | None = None,
        mode: str = "hybrid",
    ) -> list[SearchHit]:
        if self.require_tenant and tenant is None:
            raise TenantIsolationViolation("search requires an explicit tenant")

        rankings: dict[str, list[tuple[str, float]]] = {}
        if mode in ("hybrid", "dense"):
            rankings["dense"] = self._dense(query, where, tenant)
        if mode in ("hybrid", "lexical"):
            allowed = self._locally_filtered(where, tenant)
            rankings["lexical"] = [
                (doc_id, score)
                for doc_id, score in self._lexical.search(query, limit=self.candidates * 4)
                if doc_id in allowed
            ][: self.candidates]

        return reciprocal_rank_fusion(rankings, self._chunks, weights=self.weights, limit=limit)

    def _dense(
        self, query: str, where: Filter | None, tenant: str | None
    ) -> list[tuple[str, float]]:
        vector = self.embedder.embed([query])[0]
        results = self._client.query_points(
            collection_name=self.collection,
            query=vector,
            limit=self.candidates,
            # Pushed into the traversal. Filtering afterwards would return
            # fewer than `limit` matching results, tenant-dependently.
            query_filter=_to_qdrant_filter(where, tenant),
            with_payload=True,
        ).points
        out = []
        for point in results:
            payload = point.payload or {}
            chunk_id = str(payload.get("chunk_id", point.id))
            if chunk_id not in self._chunks:
                self._chunks[chunk_id] = _chunk_from_payload(chunk_id, payload)
            out.append((chunk_id, float(point.score)))
        return out

    def _locally_filtered(self, where: Filter | None, tenant: str | None) -> set[str]:
        from .types import matches_filter

        combined: Filter = dict(where or {})
        if tenant is not None:
            combined["tenant"] = tenant
        if not combined:
            return set(self._chunks)
        return {i for i, c in self._chunks.items() if matches_filter(c.metadata, combined)}

    def count(self, tenant: str | None = None) -> int:
        return int(
            self._client.count(
                collection_name=self.collection,
                count_filter=_to_qdrant_filter(None, tenant),
                exact=True,
            ).count
        )


def _point_id(chunk_id: str) -> int:
    """Qdrant wants an int or a UUID; our ids are ULIDs.

    Hashed to 63 bits deterministically, so the same chunk id always maps to the
    same point and an upsert replaces rather than duplicating.
    """
    import hashlib

    return int.from_bytes(hashlib.blake2b(chunk_id.encode(), digest_size=8).digest(), "big") >> 1


def _chunk_from_payload(chunk_id: str, payload: dict[str, Any]) -> Chunk:
    span = payload.get("span") or [0, 0]
    reserved = {"chunk_id", "doc_id", "text", "page", "span"}
    return Chunk(
        id=chunk_id,
        text=str(payload.get("text", "")),
        doc_id=str(payload.get("doc_id", "")),
        page=int(payload.get("page", 0)),
        char_span=(int(span[0]), int(span[1])),
        metadata={k: v for k, v in payload.items() if k not in reserved},
    )


def _to_qdrant_filter(where: Filter | None, tenant: str | None) -> Any:
    from qdrant_client.models import FieldCondition, MatchAny, MatchValue, Range
    from qdrant_client.models import Filter as QFilter

    conditions: list[Any] = []
    combined: Filter = dict(where or {})
    if tenant is not None:
        combined["tenant"] = tenant  # last, so it cannot be overridden
    for key, expected in combined.items():
        if isinstance(expected, dict):
            conditions.append(
                FieldCondition(
                    key=key, range=Range(gte=expected.get("gte"), lte=expected.get("lte"))
                )
            )
        elif isinstance(expected, (list, tuple, set)):
            conditions.append(FieldCondition(key=key, match=MatchAny(any=list(expected))))
        else:
            conditions.append(FieldCondition(key=key, match=MatchValue(value=expected)))
    return QFilter(must=conditions) if conditions else None
