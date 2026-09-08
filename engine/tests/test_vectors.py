"""Tests for P12. The hybrid-beats-either test is the one that justifies the layer."""

from __future__ import annotations

import gzip
import json

import pytest

from omnex.core import ConfigurationError, TenantIsolationViolation, ValidationFailed
from omnex.vectors import (
    Bm25Index,
    Chunk,
    EmbeddingCache,
    HashingEmbedder,
    HybridStore,
    SqliteStore,
    SynonymEmbedder,
    cosine,
    export_store,
    import_store,
    read_manifest,
    reciprocal_rank_fusion,
    verify_restore,
)

# ── BM25 ──────────────────────────────────────────────────────────────────


def test_term_frequency_saturates_so_keyword_stuffing_does_not_win():
    """The reason BM25 rather than raw TF-IDF."""
    index = Bm25Index()
    index.add("honest", "The cache invalidation protocol handles network partitions correctly.")
    index.add("stuffed", "cache " * 200 + "unrelated filler text about gardening")

    ranked = dict(index.search("cache invalidation protocol"))
    assert ranked["honest"] > ranked["stuffed"]


def test_a_term_in_most_documents_does_not_demote_the_documents_containing_it():
    """Unfloored IDF goes negative for common terms and inverts the ranking."""
    index = Bm25Index()
    for i in range(10):
        index.add(f"doc{i}", "the system processes requests")
    index.add("special", "the system processes requests using a bloom filter")

    results = index.search("the system bloom")
    assert results[0][0] == "special"
    assert all(score >= 0 for _, score in results)


def test_length_normalisation_stops_long_documents_winning_by_size():
    index = Bm25Index()
    index.add("short", "bloom filter")
    index.add("long", "bloom filter " + "unrelated words " * 200)
    ranked = dict(index.search("bloom filter"))
    assert ranked["short"] > ranked["long"]


def test_re_adding_a_document_replaces_rather_than_accumulates():
    index = Bm25Index()
    index.add("a", "cache cache cache")
    first = dict(index.search("cache"))["a"]
    index.add("a", "cache")
    assert dict(index.search("cache"))["a"] != first
    assert index.live_documents == 1


def test_a_tombstoned_document_stops_affecting_statistics_immediately():
    index = Bm25Index()
    for i in range(5):
        index.add(f"doc{i}", "bloom filter implementation")
    index.add("target", "bloom filter implementation")
    index.remove("target")

    assert index.live_documents == 5
    assert all(doc_id != "target" for doc_id, _ in index.search("bloom"))
    assert index.compact() == 1
    assert index.live_documents == 5


# ── Embeddings and the cache ──────────────────────────────────────────────


def test_hashing_embedder_is_deterministic_and_normalised():
    embedder = HashingEmbedder()
    a, b = embedder.embed(["cache invalidation", "cache invalidation"])
    assert a == b
    assert cosine(a, b) == pytest.approx(1.0)


def test_similar_text_is_closer_than_unrelated_text():
    embedder = HashingEmbedder()
    query, near, far = embedder.embed(
        ["cache invalidation protocol", "the cache invalidation design", "gardening in autumn"]
    )
    assert cosine(query, near) > cosine(query, far)


def test_the_cache_key_includes_the_model_so_a_model_bump_is_a_miss():
    """Content-hash-only keying serves vectors from the OLD model. Silently."""
    old = EmbeddingCache(HashingEmbedder(dims=64, version="v1"))
    old.embed(["cache invalidation"])
    assert old.misses == 1 and old.hits == 0

    old.embed(["cache invalidation"])
    assert old.hits == 1  # same model, same text: a hit

    new = EmbeddingCache(HashingEmbedder(dims=64, version="v2"))
    new._store = old._store  # same underlying storage, as a shared cache would be
    new.embed(["cache invalidation"])
    assert new.misses == 1, "a model change must not be served from cache"


def test_changing_dimensions_also_invalidates():
    cache = EmbeddingCache(HashingEmbedder(dims=64))
    cache.embed(["text"])
    other = EmbeddingCache(HashingEmbedder(dims=128))
    other._store = cache._store
    other.embed(["text"])
    assert other.misses == 1


def test_the_cache_actually_saves_work_on_repeated_ingest():
    cache = EmbeddingCache(HashingEmbedder())
    texts = [f"chunk number {i}" for i in range(100)]
    cache.embed(texts)
    cache.embed(texts)
    assert cache.hit_ratio == 0.5
    assert cache.misses == 100


def test_the_cache_is_bounded():
    cache = EmbeddingCache(HashingEmbedder(), max_entries=50)
    cache.embed([f"text {i}" for i in range(500)])
    assert len(cache._store) <= 50


# ── Fusion ────────────────────────────────────────────────────────────────


def _chunks(*ids: str) -> dict[str, Chunk]:
    return {i: Chunk(id=i, text=i) for i in ids}


def test_fusion_uses_ranks_so_incomparable_score_scales_do_not_matter():
    """BM25 is unbounded and corpus-dependent; cosine sits in a tight band."""
    rankings = {
        "lexical": [("a", 41.7), ("b", 12.2), ("c", 0.9)],  # unbounded
        "dense": [("b", 0.84), ("c", 0.83), ("a", 0.81)],  # tightly clustered
    }
    hits = reciprocal_rank_fusion(rankings, _chunks("a", "b", "c"))
    # `a` wins outright on the lexical side by a huge margin and comes LAST on
    # the dense side. `b` is near the top of both. Fusion prefers the consistent
    # document, which is the behaviour that makes it robust — and note that a
    # weighted sum of 41.7 against 0.84 is dominated entirely by whichever scale
    # happens to be larger.
    assert hits[0].chunk.id == "b"
    assert hits[0].ranks == {"lexical": 2, "dense": 1}


def test_a_document_found_by_only_one_retriever_still_surfaces():
    rankings = {"lexical": [("only-lexical", 9.0)], "dense": [("only-dense", 0.9)]}
    hits = reciprocal_rank_fusion(rankings, _chunks("only-lexical", "only-dense"))
    assert {h.chunk.id for h in hits} == {"only-lexical", "only-dense"}


def test_one_retriever_cannot_single_handedly_dominate():
    """The k constant damps top ranks; that is what makes fusion robust."""
    rankings = {
        "lexical": [("wrong", 999.0), *[(f"x{i}", 1.0) for i in range(9)]],
        "dense": [("right", 0.9), ("wrong", 0.1)],
    }
    hits = reciprocal_rank_fusion(rankings, _chunks("wrong", "right", *[f"x{i}" for i in range(9)]))
    ids = [h.chunk.id for h in hits[:2]]
    assert "right" in ids and "wrong" in ids  # neither is buried


def test_a_hit_can_explain_where_it_came_from():
    rankings = {"lexical": [("a", 9.0)], "dense": [("a", 0.9)]}
    hit = reciprocal_rank_fusion(rankings, _chunks("a"))[0]
    assert "lexical#1" in hit.explain() and "dense#1" in hit.explain()


def test_a_ranking_referencing_a_deleted_chunk_is_skipped_not_returned_empty():
    rankings = {"lexical": [("gone", 9.0), ("here", 1.0)]}
    hits = reciprocal_rank_fusion(rankings, _chunks("here"))
    assert [h.chunk.id for h in hits] == ["here"]


# ── Hybrid search: the justification for the whole layer ──────────────────


def _corpus() -> list[Chunk]:
    return [
        Chunk(
            id="c1",
            text="Error ERR_4021 occurs when the connection pool is exhausted.",
            doc_id="runbook",
            page=12,
            metadata={"tenant": "acme"},
        ),
        Chunk(
            id="c2",
            text="Our automobile fleet insurance renews each January.",
            doc_id="policy",
            page=3,
            metadata={"tenant": "acme"},
        ),
        Chunk(
            id="c3",
            text="General guidance on handling database errors and retries.",
            doc_id="runbook",
            page=7,
            metadata={"tenant": "acme"},
        ),
        Chunk(
            id="c4",
            text="Vehicle maintenance schedules for the company car pool.",
            doc_id="ops",
            page=21,
            metadata={"tenant": "acme"},
        ),
        Chunk(
            id="c5",
            text="Confidential pricing for a different customer entirely.",
            doc_id="secret",
            page=1,
            metadata={"tenant": "globex"},
        ),
        Chunk(
            id="c6",
            text="Error ERR_9988 indicates a TLS handshake failure at startup.",
            doc_id="runbook",
            page=44,
            metadata={"tenant": "acme"},
        ),
    ]


def _synonym_store() -> HybridStore:
    """Dense side models ONE property: paraphrases are close. See embed.py."""
    store = HybridStore(
        embedder=SynonymEmbedder(groups=[{"car", "automobile", "vehicle"}]), candidates=20
    )
    store.upsert(_corpus())
    return store


def test_lexical_separates_two_identifiers_that_dense_search_cannot():
    """Ask a dense-only system for ERR_4021 and you get documents about OTHER error codes.

    Relies on the `blur_identifiers` property of the test embedder (see
    embed.py): a subword tokenizer splits a rare identifier into fragments
    shared with thousands of unrelated strings, so the vector says "error code"
    and not "error code 4021". The corpus holds two such codes.
    """
    store = _synonym_store()

    # Both documents share the token "err", so both are lexical candidates —
    # but only c1 contains "4021", and BM25 scores that decisively.
    lexical = {
        h.chunk.id: h.score
        for h in store.search("ERR_4021", limit=5, tenant="acme", mode="lexical")
    }
    assert max(lexical, key=lambda k: lexical[k]) == "c1"
    assert lexical["c1"] > 2 * lexical["c6"], "the right code wins by a wide margin"

    # The dense side has no such handle: both identifiers collapsed onto the
    # same blurred dimension, so the wrong error code looks just as relevant.
    dense = {
        h.chunk.id: h.score for h in store.search("ERR_4021", limit=5, tenant="acme", mode="dense")
    }
    assert "c6" in dense, "the wrong error code is retrieved as if relevant"
    assert dense["c6"] == pytest.approx(dense["c1"], rel=0.20), "and is barely distinguishable"


def test_dense_finds_the_paraphrase_that_lexical_search_cannot():
    store = _synonym_store()
    dense = store.search("car fleet", limit=3, tenant="acme", mode="dense")
    assert dense[0].chunk.id in {"c2", "c4"}  # automobile / vehicle

    lexical = store.search("automobile", limit=3, tenant="acme", mode="lexical")
    assert [h.chunk.id for h in lexical] == ["c2"]  # exact term only, misses c4


def test_hybrid_recovers_both_where_either_alone_misses_one():
    """The measured justification for fusing rather than picking a side."""
    store = _synonym_store()

    identifier = store.search("ERR_4021", limit=3, tenant="acme")
    paraphrase = store.search("vehicle fleet", limit=3, tenant="acme")

    assert identifier[0].chunk.id == "c1"  # lexical strength preserved
    assert {h.chunk.id for h in paraphrase} & {"c2", "c4"}  # dense strength preserved


# ── Filtering and isolation ───────────────────────────────────────────────


def test_the_filter_runs_before_ranking_not_after():
    """Post-filtering returns fewer than `limit`, and breaks for small tenants first."""
    store = HybridStore(embedder=HashingEmbedder(), candidates=20)
    # One tenant with many documents that would crowd any global top-k.
    store.upsert(
        [
            Chunk(
                id=f"big{i}",
                text="connection pool exhausted error handling",
                metadata={"tenant": "big"},
            )
            for i in range(200)
        ]
    )
    store.upsert(
        [
            Chunk(
                id=f"small{i}",
                text="connection pool exhausted error handling",
                metadata={"tenant": "small"},
            )
            for i in range(3)
        ]
    )

    hits = store.search("connection pool exhausted", limit=3, tenant="small")
    assert len(hits) == 3, "post-filtering would have returned zero here"
    assert all(h.chunk.metadata["tenant"] == "small" for h in hits)


def test_a_caller_filter_cannot_override_the_tenant_scope():
    store = _synonym_store()
    hits = store.search("pricing", limit=10, tenant="acme", where={"tenant": "globex"})
    assert all(h.chunk.metadata["tenant"] == "acme" for h in hits)
    assert not any(h.chunk.id == "c5" for h in hits)


def test_an_unscoped_search_can_be_refused_outright():
    store = _synonym_store()
    store.require_tenant = True
    with pytest.raises(TenantIsolationViolation):
        store.search("anything", limit=5)


def test_range_and_membership_filters():
    store = _synonym_store()
    early = store.search("runbook errors", limit=10, tenant="acme", where={"page": {"lte": 10}})
    assert all(h.chunk.page <= 10 for h in early)
    docs = store.search("errors", limit=10, tenant="acme", where={"doc_id": ["runbook", "ops"]})
    assert all(h.chunk.doc_id in {"runbook", "ops"} for h in docs)


def test_deleting_removes_from_both_the_vector_and_lexical_sides():
    store = _synonym_store()
    assert store.delete(["c1"]) == 1
    assert store.search("4021", limit=5, tenant="acme", mode="lexical") == []
    assert all(h.chunk.id != "c1" for h in store.search("error", limit=5, tenant="acme"))


def test_a_wrong_sized_vector_is_refused_rather_than_stored():
    class Broken:
        model_id = "broken"
        dimensions = 64

        def embed(self, texts):
            return [[0.0] * 32 for _ in texts]

    store = HybridStore(embedder=Broken())
    with pytest.raises(ValidationFailed, match="dimensionality"):
        store.upsert([Chunk(id="x", text="text")])


# ── SQLite persistence ────────────────────────────────────────────────────


def test_an_index_survives_a_restart_with_identical_results(tmp_path):
    path = tmp_path / "index.db"
    embedder = SynonymEmbedder(groups=[{"car", "automobile", "vehicle"}])

    with SqliteStore(path, embedder) as store:
        store.upsert(_corpus())
        before = [h.chunk.id for h in store.search("vehicle fleet", limit=5, tenant="acme")]

    with SqliteStore(path, embedder) as reopened:
        assert reopened.count() == 6
        after = [h.chunk.id for h in reopened.search("vehicle fleet", limit=5, tenant="acme")]

    assert before == after


def test_opening_an_index_with_a_different_model_fails_loudly(tmp_path):
    """Two unrelated vector spaces produce finite, confident, meaningless scores."""
    path = tmp_path / "index.db"
    with SqliteStore(path, HashingEmbedder(dims=64, version="v1")) as store:
        store.upsert([Chunk(id="a", text="hello")])

    with pytest.raises(ConfigurationError, match="different embedding model") as exc:
        SqliteStore(path, HashingEmbedder(dims=64, version="v2"))
    assert "v1" in str(exc.value) and "v2" in str(exc.value)  # names both


def test_upsert_replaces_rather_than_duplicating(tmp_path):
    path = tmp_path / "index.db"
    with SqliteStore(path, HashingEmbedder()) as store:
        store.upsert([Chunk(id="a", text="first version")])
        store.upsert([Chunk(id="a", text="second version")])
        assert store.count() == 1
        assert store.search("second", limit=1, mode="lexical")[0].chunk.text == "second version"


def test_page_anchors_survive_persistence(tmp_path):
    """P1 cites page numbers; losing the anchor at the storage layer breaks that."""
    path = tmp_path / "index.db"
    embedder = HashingEmbedder()
    with SqliteStore(path, embedder) as store:
        store.upsert(
            [Chunk(id="a", text="pool exhausted", page=41, char_span=(120, 200), doc_id="rb")]
        )
    with SqliteStore(path, embedder) as reopened:
        hit = reopened.search("pool exhausted", limit=1, mode="lexical")[0]
        assert hit.chunk.page == 41
        assert hit.chunk.char_span == (120, 200)
        assert hit.chunk.cite == "[p. 41]"


def test_stats_report_something_useful(tmp_path):
    with SqliteStore(tmp_path / "i.db", HashingEmbedder()) as store:
        store.upsert(_corpus())
        stats = store.stats()
        assert stats["chunks"] == 6 and stats["bytes_on_disk"] > 0


# ── Backup and restore ────────────────────────────────────────────────────


def test_a_restored_index_returns_identical_ranked_results(tmp_path):
    """Row counts do not prove a restore. Ranked ids do."""
    embedder = SynonymEmbedder(groups=[{"car", "automobile", "vehicle"}])
    original = HybridStore(embedder=embedder)
    original.upsert(_corpus())

    backup = tmp_path / "backup.jsonl.gz"
    manifest = export_store(original, backup, created_at="2026-08-05T00:00:00Z")
    assert manifest.chunks == 6

    restored = HybridStore(embedder=embedder)
    assert import_store(restored, backup) == 6

    report = verify_restore(
        original, restored, ["ERR_4021", "vehicle fleet", "database errors"], tenant="acme"
    )
    assert report.ok, report.mismatches
    assert report.queries_checked == 3


def test_verification_catches_a_corrupted_restore(tmp_path):
    """The whole point: a restore that looks fine by row count but is not."""
    embedder = SynonymEmbedder(groups=[{"car", "automobile", "vehicle"}])
    original = HybridStore(embedder=embedder)
    original.upsert(_corpus())

    damaged = HybridStore(embedder=embedder)
    damaged.upsert([c for c in _corpus() if c.id != "c1"])  # one document short

    report = verify_restore(original, damaged, ["ERR_4021"], tenant="acme")
    assert not report.ok
    assert any("chunk count" in m for m in report.mismatches)


def test_restoring_into_a_different_model_is_refused(tmp_path):
    backup = tmp_path / "b.jsonl.gz"
    source = HybridStore(embedder=HashingEmbedder(dims=64, version="v1"))
    source.upsert([Chunk(id="a", text="hello")])
    export_store(source, backup)

    target = HybridStore(embedder=HashingEmbedder(dims=64, version="v2"))
    with pytest.raises(ValidationFailed, match="different embedding model"):
        import_store(target, backup)


def test_the_backup_carries_vectors_rather_than_re_embedding_on_restore(tmp_path):
    """Re-embedding needs the model to still exist and behave identically."""
    backup = tmp_path / "b.jsonl.gz"
    store = HybridStore(embedder=HashingEmbedder())
    store.upsert([Chunk(id="a", text="hello world")])
    export_store(store, backup)

    with gzip.open(backup, "rt") as handle:
        handle.readline()  # manifest
        row = json.loads(handle.readline())
    assert len(row["vector"]) == 256
    assert row["page"] == 0 and "metadata" in row


def test_the_manifest_is_readable_without_loading_the_whole_backup(tmp_path):
    backup = tmp_path / "b.jsonl.gz"
    store = HybridStore(embedder=HashingEmbedder())
    store.upsert([Chunk(id=f"c{i}", text=f"text {i}") for i in range(100)])
    export_store(store, backup, created_at="2026-08-05T00:00:00Z")

    manifest = read_manifest(backup)
    assert manifest.chunks == 100
    assert manifest.model_id == "hashing-256-v1"
    assert manifest.created_at == "2026-08-05T00:00:00Z"


def test_a_chunk_without_a_vector_fails_the_export_rather_than_shipping_partial(tmp_path):
    store = HybridStore(embedder=HashingEmbedder())
    store.upsert([Chunk(id="a", text="hello")])
    del store._vectors["a"]
    with pytest.raises(ValidationFailed, match="partial export"):
        export_store(store, tmp_path / "b.jsonl.gz")
