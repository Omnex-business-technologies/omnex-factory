"""Reranking: the step that fixes what fusion cannot.

Retrieval and reranking answer different questions and the split is the point.
Retrieval is *recall* under a latency budget: get the right chunk somewhere in
the top 50, cheaply, over a corpus of millions. Reranking is *precision* over
those 50: given the query and one chunk together, how relevant is this actually?

A cross-encoder can do the second because it sees query and document jointly —
it can notice that the document mentions the query's terms in an unrelated
clause. A bi-encoder cannot: it compressed the document into a vector before it
had ever seen the query. That is a real capability difference, not a tuning one,
and it is why the expensive step is worth its cost on 50 documents and
impossible on 5,000,000.

Two consequences worth stating:

**Reranking cannot rescue bad retrieval.** It can only reorder what it is given.
If the right chunk is at rank 200 and the reranker sees the top 50, no amount of
reranking quality helps. Recall@candidates is therefore the number to watch when
answer quality is poor — `recall_at` is here so it can be measured rather than
assumed.

**Rerank AFTER fusion, not instead of it.** Fusion (RRF) deliberately discards
score magnitude, which is right when combining incomparable scales. A
cross-encoder's score is calibrated and comparable, so it is the one place where
magnitude should be kept — and it is kept last, on the fused candidate set.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from ..core.errors import ConfigurationError
from ..vectors.embed import tokenize
from ..vectors.types import Chunk, SearchHit

__all__ = ["CrossEncoderReranker", "LexicalReranker", "Reranker", "recall_at"]

_STOP = frozenset(
    [
        "a",
        "an",
        "the",
        "of",
        "in",
        "on",
        "at",
        "to",
        "for",
        "from",
        "by",
        "with",
        "is",
        "are",
        "was",
        "were",
        "and",
        "or",
    ]
)


@runtime_checkable
class Reranker(Protocol):
    def rerank(self, query: str, hits: Sequence[SearchHit], limit: int) -> list[SearchHit]: ...


@dataclass
class LexicalReranker:
    """Query-aware scoring that needs no model. The default, and the test double.

    Scores three things a bi-encoder cannot see once it has compressed the
    document: how many distinct query terms appear, how *tightly* they appear
    together, and whether they appear early. Term proximity is the useful signal
    here — a document containing "connection" in one paragraph and "pool" in
    another is a worse answer to "connection pool" than one containing the
    phrase, and no vector distance distinguishes them.

    Not as good as a cross-encoder. Deterministic, free, and dependency-free,
    which makes it the right default for the local tier and the only sane choice
    for a test suite that must produce identical rankings on every run.
    """

    #: Weight on the fraction of query terms present at all.
    coverage_weight: float = 0.6
    #: Weight on how tightly the matched terms cluster.
    proximity_weight: float = 0.3
    #: Weight on how early the first match appears.
    position_weight: float = 0.1
    #: Keep the retrieval score as a tie-breaker, scaled small so it never
    #: overrides the query-aware signal it is there to refine.
    retrieval_weight: float = 0.05

    def rerank(self, query: str, hits: Sequence[SearchHit], limit: int) -> list[SearchHit]:
        terms = [t for t in tokenize(query) if t not in _STOP]
        if not terms:
            return list(hits[:limit])

        scored: list[tuple[float, SearchHit]] = []
        for hit in hits:
            score = self._score(terms, hit.chunk) + self.retrieval_weight * hit.score
            scored.append((score, hit))

        scored.sort(key=lambda pair: (-pair[0], pair[1].chunk.id))
        return [
            SearchHit(
                chunk=hit.chunk,
                score=score,
                components={**hit.components, "rerank": score},
                ranks={**hit.ranks, "rerank": position},
            )
            for position, (score, hit) in enumerate(scored[:limit], start=1)
        ]

    def _score(self, terms: Sequence[str], chunk: Chunk) -> float:
        tokens = tokenize(chunk.text)
        if not tokens:
            return 0.0
        positions: dict[str, list[int]] = {}
        for index, token in enumerate(tokens):
            if token in terms:
                positions.setdefault(token, []).append(index)

        if not positions:
            return 0.0

        coverage = len(positions) / len(set(terms))

        # Tightest window containing one occurrence of each matched term.
        firsts = [min(p) for p in positions.values()]
        lasts = [max(p) for p in positions.values()]
        span = max(lasts) - min(firsts) + 1
        proximity = len(positions) / span if span else 1.0

        position = 1.0 - (min(firsts) / len(tokens))

        return (
            self.coverage_weight * coverage
            + self.proximity_weight * min(1.0, proximity)
            + self.position_weight * position
        )


@dataclass
class CrossEncoderReranker:
    """A sentence-transformers cross-encoder. The accurate, expensive path.

    Batched in one call rather than per-hit: a cross-encoder's cost is dominated
    by model invocation overhead at these batch sizes, and 50 separate forward
    passes takes roughly an order of magnitude longer than one batch of 50.

    The default model is a small open-weights MS MARCO cross-encoder — it runs
    on CPU in tens of milliseconds for 50 pairs, which keeps the whole pipeline
    viable with no GPU and no hosted reranking API.
    """

    model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    max_length: int = 512
    _model: Any = field(default=None, repr=False)

    def _ensure(self) -> Any:
        if self._model is not None:
            return self._model
        try:
            from sentence_transformers import CrossEncoder
        except ImportError as exc:  # pragma: no cover - only without the extra
            raise ConfigurationError(
                "CrossEncoderReranker needs the 'rag' extra: "
                "pip install 'omnex-engine[rag]' — or use LexicalReranker, which needs nothing"
            ) from exc
        self._model = CrossEncoder(self.model_name, max_length=self.max_length)
        return self._model

    def rerank(self, query: str, hits: Sequence[SearchHit], limit: int) -> list[SearchHit]:
        if not hits:
            return []
        model = self._ensure()
        scores = model.predict([(query, hit.chunk.text) for hit in hits])
        ranked = sorted(zip(scores, hits, strict=True), key=lambda pair: -float(pair[0]))
        return [
            SearchHit(
                chunk=hit.chunk,
                score=float(score),
                components={**hit.components, "rerank": float(score)},
                ranks={**hit.ranks, "rerank": position},
            )
            for position, (score, hit) in enumerate(ranked[:limit], start=1)
        ]


def recall_at(hits: Sequence[SearchHit], relevant_ids: Sequence[str], k: int) -> float:
    """Fraction of known-relevant chunks present in the top k.

    The number to check first when answers are poor. Reranking can only reorder
    what retrieval handed it: if this is low, the reranker is not the problem
    and improving it will not help.
    """
    if not relevant_ids:
        return 1.0
    top = {hit.chunk.id for hit in hits[:k]}
    return sum(1 for i in relevant_ids if i in top) / len(relevant_ids)
