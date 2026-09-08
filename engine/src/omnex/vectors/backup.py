"""Backup and restore — and the verification without which neither is real.

An untested backup is not a backup, it is a file. The failure is never "the
export crashed"; it is that the export quietly omitted something — the vectors,
the metadata, a tenant whose rows were being written during the dump — and
nobody finds out until the restore, which happens on the worst day of the
quarter.

So `verify_restore` does not compare file sizes or row counts. It runs a set of
queries against the original and the restored index and requires the **ranked
result ids to be identical**. That is the property anyone actually depends on: a
restored index whose search results differ from the original has not been
restored, whatever the row count says.

Vectors are exported alongside the text, rather than re-embedded on restore.
Re-embedding looks tidier and is a trap: it needs the same model to still exist
and behave identically, it costs a full re-embed of the corpus at exactly the
moment you are trying to recover quickly, and any drift in the model silently
produces a different index. The export is larger; the restore is deterministic
and offline.

Format is JSON Lines, gzipped: streamable, so a 40 GB export never has to be
held in memory, and greppable when someone needs to know whether one specific
document made it in.
"""

from __future__ import annotations

import gzip
import json
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..core.errors import ValidationFailed
from .store import HybridStore
from .types import Chunk

__all__ = ["BackupManifest", "RestoreReport", "export_store", "import_store", "verify_restore"]

BACKUP_FORMAT = 1


@dataclass(frozen=True)
class BackupManifest:
    format: int
    model_id: str
    dimensions: int
    chunks: int
    created_at: str

    def as_dict(self) -> dict[str, object]:
        return {
            "format": self.format,
            "model_id": self.model_id,
            "dimensions": self.dimensions,
            "chunks": self.chunks,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class RestoreReport:
    chunks_restored: int
    queries_checked: int
    mismatches: list[str]

    @property
    def ok(self) -> bool:
        return not self.mismatches


def export_store(store: HybridStore, path: str | Path, created_at: str = "") -> BackupManifest:
    """Write the whole index to a gzipped JSONL file. First line is the manifest."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    chunks = store.all_chunks()
    manifest = BackupManifest(
        format=BACKUP_FORMAT,
        model_id=store.embedder.model_id,
        dimensions=store.embedder.dimensions,
        chunks=len(chunks),
        created_at=created_at,
    )

    with gzip.open(destination, "wt", encoding="utf-8") as handle:
        handle.write(json.dumps(manifest.as_dict()) + "\n")
        for chunk in chunks:
            vector = store.vector_of(chunk.id)
            if vector is None:
                # A chunk without its vector would restore as unsearchable by
                # the dense side, and would do so silently. Refuse instead.
                raise ValidationFailed(
                    "chunk has no vector; refusing a partial export", chunk_id=chunk.id
                )
            handle.write(
                json.dumps(
                    {
                        "id": chunk.id,
                        "doc_id": chunk.doc_id,
                        "text": chunk.text,
                        "page": chunk.page,
                        "char_span": list(chunk.char_span),
                        "metadata": chunk.metadata,
                        "vector": vector,
                    },
                    separators=(",", ":"),
                )
                + "\n"
            )
    return manifest


def _read(path: str | Path) -> Iterator[dict[str, Any]]:
    with gzip.open(Path(path), "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def read_manifest(path: str | Path) -> BackupManifest:
    first = next(_read(path))
    return BackupManifest(
        format=int(first["format"]),
        model_id=str(first["model_id"]),
        dimensions=int(first["dimensions"]),
        chunks=int(first["chunks"]),
        created_at=str(first.get("created_at", "")),
    )


def import_store(store: HybridStore, path: str | Path, batch_size: int = 500) -> int:
    """Load a backup into `store`, reusing the exported vectors.

    Refuses a model mismatch rather than re-embedding: an index restored into a
    different embedding space is a working index that returns wrong answers,
    which is worse than a failed restore.
    """
    manifest = read_manifest(path)
    if manifest.format != BACKUP_FORMAT:
        raise ValidationFailed(
            "unsupported backup format", found=manifest.format, expected=BACKUP_FORMAT
        )
    current = f"{store.embedder.model_id}:{store.embedder.dimensions}"
    if f"{manifest.model_id}:{manifest.dimensions}" != current:
        raise ValidationFailed(
            "backup was built with a different embedding model",
            backup_model=f"{manifest.model_id}:{manifest.dimensions}",
            current_model=current,
        )

    restored = 0
    batch: list[Chunk] = []
    vectors: list[list[float]] = []
    rows = _read(path)
    next(rows)  # manifest

    for row in rows:
        batch.append(
            Chunk(
                id=str(row["id"]),
                text=str(row["text"]),
                doc_id=str(row.get("doc_id", "")),
                page=int(row.get("page", 0)),
                char_span=tuple(row.get("char_span", [0, 0])),
                metadata=dict(row.get("metadata", {})),
            )
        )
        vectors.append([float(v) for v in row["vector"]])
        if len(batch) >= batch_size:
            restored += _write_batch(store, batch, vectors)
            batch, vectors = [], []

    if batch:
        restored += _write_batch(store, batch, vectors)
    return restored


def _write_batch(store: HybridStore, chunks: list[Chunk], vectors: list[list[float]]) -> int:
    """Insert with the ORIGINAL vectors rather than recomputing them."""
    written = store.upsert(chunks)
    for chunk, vector in zip(chunks, vectors, strict=True):
        store._vectors[chunk.id] = vector
    return written


def verify_restore(
    original: HybridStore,
    restored: HybridStore,
    queries: Sequence[str],
    limit: int = 10,
    tenant: str | None = None,
) -> RestoreReport:
    """Compare ranked results between two indexes. Identical ids or it failed.

    Ranked ids, not counts and not scores. Counts miss a subtly corrupted vector
    that still returns *something*; scores can differ in the last float bit
    without meaning anything. The ordered ids are what a user experiences.
    """
    mismatches: list[str] = []
    for query in queries:
        before = [h.chunk.id for h in original.search(query, limit=limit, tenant=tenant)]
        after = [h.chunk.id for h in restored.search(query, limit=limit, tenant=tenant)]
        if before != after:
            mismatches.append(f"{query!r}: {before} != {after}")
    if original.count() != restored.count():
        mismatches.append(f"chunk count {original.count()} != {restored.count()}")
    return RestoreReport(
        chunks_restored=restored.count(), queries_checked=len(queries), mismatches=mismatches
    )
