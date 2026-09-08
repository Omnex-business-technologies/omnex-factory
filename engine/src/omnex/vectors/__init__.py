"""P12 — hybrid retrieval at scale.

BM25 and dense vectors fused by Reciprocal Rank Fusion, metadata filtering that
runs BEFORE ranking, an embedding cache that cannot serve vectors from a
superseded model, SQLite persistence for the local tier and a Qdrant adapter for
the scaled one, and a backup whose restore is verified by comparing ranked
results rather than row counts.

Three positions worth knowing before reading the code:

- **Fusion by rank, not by normalised score.** Cosine and BM25 are not on
  comparable scales and BM25's scale moves with the corpus; min-max normalising
  each result set destroys the information that mattered. See `fusion.py`.
- **Pre-filter, never post-filter.** Ranking then filtering silently returns
  fewer than `limit` results, and does so tenant-dependently — it breaks for
  small tenants first. See `store.py`.
- **The embedding model id belongs in the index and in the cache key.** Both
  failures are silent: an index opened with the wrong model returns confident
  nonsense, and a content-hash cache serves stale vectors after a model bump.
"""

from .backup import (
    BackupManifest,
    RestoreReport,
    export_store,
    import_store,
    read_manifest,
    verify_restore,
)
from .bm25 import Bm25Index
from .embed import Embedder, EmbeddingCache, HashingEmbedder, SynonymEmbedder, cosine, tokenize
from .fusion import RRF_K, reciprocal_rank_fusion
from .sqlite_store import SqliteStore
from .store import HybridStore, VectorStore
from .types import Chunk, Filter, SearchHit, matches_filter

__all__ = [
    "RRF_K",
    "BackupManifest",
    "Bm25Index",
    "Chunk",
    "Embedder",
    "EmbeddingCache",
    "Filter",
    "HashingEmbedder",
    "HybridStore",
    "RestoreReport",
    "SearchHit",
    "SqliteStore",
    "SynonymEmbedder",
    "VectorStore",
    "cosine",
    "export_store",
    "import_store",
    "matches_filter",
    "read_manifest",
    "reciprocal_rank_fusion",
    "tokenize",
    "verify_restore",
]
