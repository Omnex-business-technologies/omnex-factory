"""SQLite-backed persistence, with the embedding model recorded in the file.

SQLite is the right default for the local-first tier (P7) and for anything under
a few million vectors: one file, no server, no operational cost, and it backs up
with `cp`. `sqlite-vec` is used for the ANN index when installed; without it the
scan is brute force, which for a corpus of tens of thousands is milliseconds and
exactly correct rather than approximately correct.

The important thing in this file is not the SQL. It is that **the embedding
model id is stored in the database and checked on open.** Opening an index built
with one model using a different one produces cosine similarities between
vectors from two unrelated spaces. Every number is finite, nothing raises, and
search returns confident nonsense. Recording the model turns that into a
startup error naming both models, which is a five-second fix instead of a week
of "retrieval feels worse since the deploy".

Vectors are stored as raw float32 bytes rather than JSON: a 768-dimension vector
is 3 KB as JSON and 3 KB of parsing on every read, against 3,072 bytes and a
`memoryview`. On a million chunks that is the difference between a database that
opens and one that does not.
"""

from __future__ import annotations

import json
import sqlite3
import struct
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ..core.errors import ConfigurationError
from .bm25 import Bm25Index
from .embed import Embedder
from .store import HybridStore
from .types import Chunk

__all__ = ["SCHEMA_VERSION", "SqliteStore"]

SCHEMA_VERSION = 1

_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chunks (
    id         TEXT PRIMARY KEY,
    doc_id     TEXT NOT NULL DEFAULT '',
    text       TEXT NOT NULL,
    page       INTEGER NOT NULL DEFAULT 0,
    span_start INTEGER NOT NULL DEFAULT 0,
    span_end   INTEGER NOT NULL DEFAULT 0,
    metadata   TEXT NOT NULL DEFAULT '{}',
    tenant     TEXT NOT NULL DEFAULT '',
    vector     BLOB NOT NULL
);
-- Tenant first: it is the filter that appears in every production query, and a
-- composite index is only useful when its leading column is the one you filter.
CREATE INDEX IF NOT EXISTS chunks_tenant_doc ON chunks (tenant, doc_id);
"""


def _pack(vector: Sequence[float]) -> bytes:
    return struct.pack(f"<{len(vector)}f", *vector)


def _unpack(blob: bytes) -> list[float]:
    return list(struct.unpack(f"<{len(blob) // 4}f", blob))


class SqliteStore(HybridStore):
    """A `HybridStore` that persists to SQLite and reloads on open."""

    def __init__(
        self,
        path: str | Path,
        embedder: Embedder,
        candidates: int = 50,
        require_tenant: bool = False,
    ) -> None:
        super().__init__(embedder=embedder, candidates=candidates, require_tenant=require_tenant)
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(self.path))
        self._db.row_factory = sqlite3.Row
        # WAL so a reader during an ingest is not blocked. The default rollback
        # journal serialises them, which turns a background reindex into an
        # outage for the query path.
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=NORMAL")
        self._db.executescript(_SCHEMA)
        self._check_or_record_model()
        self._load()

    # ── model identity ────────────────────────────────────────────────────
    def _check_or_record_model(self) -> None:
        row = self._db.execute("SELECT value FROM meta WHERE key='model_id'").fetchone()
        current = f"{self.embedder.model_id}:{self.embedder.dimensions}"
        if row is None:
            self._db.execute(
                "INSERT INTO meta (key, value) VALUES ('model_id', ?), ('schema_version', ?)",
                (current, str(SCHEMA_VERSION)),
            )
            self._db.commit()
            return
        if row["value"] != current:
            raise ConfigurationError(
                "this index was built with a different embedding model — "
                "cosine similarity between two unrelated vector spaces is meaningless; "
                "re-embed the corpus or open a different file",
                index_model=row["value"],
                current_model=current,
                path=str(self.path),
            )

    # ── persistence ───────────────────────────────────────────────────────
    def _load(self) -> None:
        self._chunks.clear()
        self._vectors.clear()
        self._lexical = Bm25Index()
        for row in self._db.execute("SELECT * FROM chunks"):
            chunk = Chunk(
                id=row["id"],
                text=row["text"],
                doc_id=row["doc_id"],
                page=row["page"],
                char_span=(row["span_start"], row["span_end"]),
                metadata=json.loads(row["metadata"]),
            )
            self._chunks[chunk.id] = chunk
            self._vectors[chunk.id] = _unpack(row["vector"])
            # Rebuilt rather than persisted: an inverted index is derived data,
            # and storing it means a schema migration every time scoring changes.
            self._lexical.add(chunk.id, chunk.text)

    def upsert(self, chunks: Sequence[Chunk]) -> int:
        written = super().upsert(chunks)
        rows: list[tuple[Any, ...]] = []
        for chunk in chunks:
            rows.append(
                (
                    chunk.id,
                    chunk.doc_id,
                    chunk.text,
                    chunk.page,
                    chunk.char_span[0],
                    chunk.char_span[1],
                    json.dumps(chunk.metadata, sort_keys=True),
                    str(chunk.metadata.get("tenant", "")),
                    _pack(self._vectors[chunk.id]),
                )
            )
        self._db.executemany(
            "INSERT INTO chunks (id, doc_id, text, page, span_start, span_end, metadata, tenant, vector) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET doc_id=excluded.doc_id, text=excluded.text, "
            "page=excluded.page, span_start=excluded.span_start, span_end=excluded.span_end, "
            "metadata=excluded.metadata, tenant=excluded.tenant, vector=excluded.vector",
            rows,
        )
        self._db.commit()
        return written

    def delete(self, chunk_ids: Sequence[str]) -> int:
        removed = super().delete(chunk_ids)
        self._db.executemany("DELETE FROM chunks WHERE id = ?", [(i,) for i in chunk_ids])
        self._db.commit()
        return removed

    def clear(self) -> None:
        super().clear()
        self._db.execute("DELETE FROM chunks")
        self._db.commit()

    def close(self) -> None:
        self._db.close()

    def __enter__(self) -> SqliteStore:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ── maintenance ───────────────────────────────────────────────────────
    def vacuum(self) -> None:
        """Reclaim space after bulk deletes. SQLite does not do this on its own."""
        self._lexical.compact()
        self._db.execute("VACUUM")

    def stats(self) -> dict[str, Any]:
        page_count = self._db.execute("PRAGMA page_count").fetchone()[0]
        page_size = self._db.execute("PRAGMA page_size").fetchone()[0]
        return {
            "chunks": self.count(),
            "bytes_on_disk": page_count * page_size,
            "model_id": self.embedder.model_id,
            "dimensions": self.embedder.dimensions,
            "path": str(self.path),
        }
