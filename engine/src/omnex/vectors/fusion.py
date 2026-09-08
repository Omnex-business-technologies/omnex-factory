"""Combining rankings: why Reciprocal Rank Fusion, and not score normalisation.

The obvious way to merge a BM25 ranking with a cosine ranking is to normalise
both to [0, 1] and take a weighted sum. It is the wrong tool, for a reason that
is easy to miss and hard to debug.

**The two scores are not on comparable scales, and their scales move.** A cosine
similarity lives in [-1, 1] and clusters tightly — the gap between the best and
tenth-best result is often 0.04. BM25 is unbounded above and depends on corpus
statistics: the same query against the same documents produces different
absolute scores after an ingest, because the IDFs moved. Min-max normalising
each result set fixes the range but destroys the information that mattered: a
set where everything is equally bad normalises its worst member to 0 and its
best to 1, exactly like a set where everything is excellent. The fused ranking
then depends on how *spread out* each retriever's scores happened to be, which
is not a property anyone intended to rank by.

Reciprocal Rank Fusion uses only the ranks:

    RRF(d) = Σ over retrievers  w_r / (k + rank_r(d))

Ranks are comparable across retrievers by construction. It needs no calibration,
no per-corpus tuning, and no assumption that either score is meaningful in
absolute terms. `k` (60 by convention, from the original TREC work) damps the
influence of the very top ranks so that one retriever's confident first place
cannot single-handedly decide the fused order — which is what makes fusion
robust when one side is having a bad query.

The cost is real and worth stating: RRF discards *magnitude*. A document that
BM25 scored 40.0 and one it scored 4.1 are just rank 1 and rank 2. Where a
retriever's absolute score is genuinely calibrated — a cross-encoder's relevance
probability, for instance — that information is worth keeping, which is why P1
reranks with a cross-encoder AFTER fusing rather than fusing its scores in.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from .types import Chunk, SearchHit

__all__ = ["RRF_K", "reciprocal_rank_fusion"]

#: Conventional damping constant. Larger flattens the advantage of top ranks.
RRF_K = 60.0


def reciprocal_rank_fusion(
    rankings: Mapping[str, Sequence[tuple[str, float]]],
    chunks: Mapping[str, Chunk],
    weights: Mapping[str, float] | None = None,
    k: float = RRF_K,
    limit: int = 10,
) -> list[SearchHit]:
    """Fuse named rankings of `(chunk_id, score)` into one ordered list.

    `chunks` supplies the payloads. A ranking may reference a chunk that another
    retriever has never seen — that is the normal case and the entire point.
    """
    weights = weights or {}
    fused: dict[str, float] = {}
    components: dict[str, dict[str, float]] = {}
    ranks: dict[str, dict[str, int]] = {}

    for name, ranking in rankings.items():
        weight = weights.get(name, 1.0)
        for position, (chunk_id, score) in enumerate(ranking, start=1):
            fused[chunk_id] = fused.get(chunk_id, 0.0) + weight / (k + position)
            components.setdefault(chunk_id, {})[name] = score
            ranks.setdefault(chunk_id, {})[name] = position

    ordered = sorted(fused.items(), key=lambda kv: (-kv[1], kv[0]))
    hits: list[SearchHit] = []
    for chunk_id, score in ordered[:limit]:
        chunk = chunks.get(chunk_id)
        if chunk is None:
            # A retriever returned an id the store no longer has. Skipping is
            # right: the alternative is a hit whose text cannot be shown, which
            # fails later and further from the cause.
            continue
        hits.append(
            SearchHit(
                chunk=chunk,
                score=score,
                components=components.get(chunk_id, {}),
                ranks=ranks.get(chunk_id, {}),
            )
        )
    return hits
