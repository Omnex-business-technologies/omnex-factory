"""BM25 lexical retrieval, in-process.

Dense retrieval is worse than a keyword index at the things keyword indexes are
good at, and those things are not rare: exact identifiers, error codes, product
SKUs, surnames, version numbers. Ask a dense-only system for `ERR_4021` and it
returns documents about errors; BM25 returns the one document containing
`ERR_4021`. That is the half of hybrid search people skip because embeddings
feel more modern.

BM25 over the classic TF-IDF for one reason worth stating: **term-frequency
saturation.** A document that repeats a query term forty times is not forty
times more relevant, and `k1` bounds that contribution — which is what makes the
score robust against keyword-stuffed and boilerplate-heavy documents. `b`
controls length normalisation, so a long document does not win simply by
containing more words.

Deletion marks a tombstone rather than rebuilding, because ingest is
incremental and a full reindex per deleted chunk turns an O(1) operation into
O(n). Statistics are recomputed lazily from live documents only, so a tombstoned
document cannot influence the IDF of terms it contained.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field

from .embed import tokenize

__all__ = ["BM25_B", "BM25_K1", "Bm25Index"]

#: Saturation. Higher means term frequency keeps mattering for longer.
BM25_K1 = 1.5
#: Length normalisation. 0 disables it, 1 applies it fully.
BM25_B = 0.75


@dataclass
class Bm25Index:
    """An inverted index with BM25 scoring."""

    k1: float = BM25_K1
    b: float = BM25_B
    _postings: dict[str, dict[str, int]] = field(default_factory=dict)
    _lengths: dict[str, int] = field(default_factory=dict)
    _deleted: set[str] = field(default_factory=set)

    def add(self, doc_id: str, text: str) -> None:
        if doc_id in self._lengths:
            self.remove(doc_id)  # re-adding must replace, not accumulate
        tokens = tokenize(text)
        self._lengths[doc_id] = len(tokens)
        self._deleted.discard(doc_id)
        for term, count in Counter(tokens).items():
            self._postings.setdefault(term, {})[doc_id] = count

    def remove(self, doc_id: str) -> None:
        """Tombstone. Cheap, and excluded from statistics immediately."""
        if doc_id in self._lengths:
            self._deleted.add(doc_id)

    def compact(self) -> int:
        """Physically drop tombstoned documents. Returns how many were removed."""
        removed = len(self._deleted)
        for doc_id in self._deleted:
            self._lengths.pop(doc_id, None)
        for term in list(self._postings):
            postings = self._postings[term]
            for doc_id in self._deleted:
                postings.pop(doc_id, None)
            if not postings:
                del self._postings[term]
        self._deleted.clear()
        return removed

    @property
    def live_documents(self) -> int:
        return len(self._lengths) - len(self._deleted)

    @property
    def _average_length(self) -> float:
        live = [n for doc, n in self._lengths.items() if doc not in self._deleted]
        return sum(live) / len(live) if live else 0.0

    def _idf(self, term: str, total: int) -> float:
        postings = self._postings.get(term, {})
        containing = sum(1 for doc in postings if doc not in self._deleted)
        if containing == 0:
            return 0.0
        # Robertson-Spärck Jones with the +0.5 smoothing, floored at zero: a
        # term in more than half the corpus otherwise scores NEGATIVE and
        # actively demotes documents that contain the query's own words.
        raw = math.log(1 + (total - containing + 0.5) / (containing + 0.5))
        return max(0.0, raw)

    def search(self, query: str, limit: int = 10) -> list[tuple[str, float]]:
        total = self.live_documents
        if total == 0:
            return []
        avg = self._average_length or 1.0
        scores: dict[str, float] = {}

        for term in tokenize(query):
            idf = self._idf(term, total)
            if idf == 0.0:
                continue
            for doc_id, freq in self._postings.get(term, {}).items():
                if doc_id in self._deleted:
                    continue
                length = self._lengths[doc_id]
                # The saturation term: doubling `freq` does not double the score.
                denominator = freq + self.k1 * (1 - self.b + self.b * length / avg)
                scores[doc_id] = (
                    scores.get(doc_id, 0.0) + idf * (freq * (self.k1 + 1)) / denominator
                )

        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        return ranked[:limit]

    def documents(self) -> Sequence[str]:
        return [d for d in self._lengths if d not in self._deleted]
