"""Embeddings: the protocol, a cache that cannot serve stale vectors, and two
deterministic instruments for tests.

The cache is the part with a real bug in it if you build it the obvious way.
Keying on the content hash alone means that changing the embedding model — a
version bump, a swap from one open-weights model to another — serves vectors
produced by the OLD model for text you re-embedded with the new one. Nothing
errors. The index quietly becomes a mixture of two incompatible spaces, recall
degrades by an amount nobody can attribute, and the only symptom is that search
"feels worse". So the key is `sha256(model_id | dimensions | text)`, and a model
change is a cache miss by construction.

The two test embedders are measuring instruments, labelled as such:

`HashingEmbedder` is feature hashing — real, dependency-free, and genuinely
lexical. It gives stable vectors with true similarity structure, which is enough
for testing storage, filtering, persistence and backup.

`SynonymEmbedder` exists because a lexical embedder cannot demonstrate the one
thing hybrid search is for. If the dense side and the lexical side both key on
surface words, fusing them shows no benefit and any "hybrid beats BM25" test is
measuring nothing. So this one places configured synonym groups on shared
dimensions, simulating the single property a real embedding model has that BM25
lacks: paraphrases land near each other. It models that and nothing else, and
the tests that use it say which property they are relying on.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

__all__ = ["Embedder", "EmbeddingCache", "HashingEmbedder", "SynonymEmbedder", "cosine", "tokenize"]

_WORD = re.compile(r"[a-z0-9']+")


def tokenize(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine similarity. Assumes nothing about normalisation."""
    if len(a) != len(b):
        raise ValueError(f"dimension mismatch: {len(a)} vs {len(b)}")
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


@runtime_checkable
class Embedder(Protocol):
    @property
    def model_id(self) -> str:
        """Stable identity of the model AND its version. Part of the cache key."""
        ...

    @property
    def dimensions(self) -> int: ...

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        """Batch on purpose: per-text calls to a hosted embedder are the slow path."""
        ...


@dataclass
class HashingEmbedder:
    """Feature hashing into a fixed space. Deterministic, no dependencies.

    Signed hashing (each token contributes +1 or -1 depending on a second hash
    bit) so that collisions cancel in expectation rather than accumulating into
    a systematic bias toward whichever bucket is crowded.
    """

    dims: int = 256
    version: str = "v1"

    @property
    def model_id(self) -> str:
        return f"hashing-{self.dims}-{self.version}"

    @property
    def dimensions(self) -> int:
        return self.dims

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._one(t) for t in texts]

    def _one(self, text: str) -> list[float]:
        vector = [0.0] * self.dims
        for token in tokenize(text):
            digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
            value = int.from_bytes(digest, "big")
            index = value % self.dims
            sign = 1.0 if (value >> 63) & 1 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(v * v for v in vector))
        return [v / norm for v in vector] if norm else vector


@dataclass
class SynonymEmbedder:
    """A test instrument modelling exactly TWO properties of a real embedder.

    Not a language model and not pretending to be. It simulates the two
    behaviours that make dense and lexical retrieval complementary — and nothing
    else. Tests that use it say which of the two they are relying on.

    **Paraphrases land close.** Tokens in a configured group share a dimension,
    so "car" and "automobile" produce nearly identical vectors while BM25 sees
    no overlap at all. This is the gap hybrid search exists to close, and
    without simulating it a hybrid-versus-lexical comparison measures nothing.

    **Rare identifiers lose their specificity.** `blur_identifiers` maps every
    token containing a digit onto one shared dimension. That is a crude stand-in
    for a real effect: subword tokenizers split `ERR_4021` into fragments shared
    with thousands of unrelated strings, so the vector carries "this is an error
    code" and not "this is error code 4021". It is why a dense-only system
    answers a question about `ERR_4021` with documents about other error codes,
    and why the lexical half of a hybrid index is not optional.
    """

    groups: list[set[str]] = field(default_factory=list)
    dims: int = 128
    version: str = "v1"
    blur_identifiers: bool = True

    @property
    def model_id(self) -> str:
        return f"synonym-{self.dims}-{self.version}"

    @property
    def dimensions(self) -> int:
        return self.dims

    def _canonical(self, token: str) -> str:
        for index, group in enumerate(self.groups):
            if token in group:
                return f"__group{index}__"
        if self.blur_identifiers and any(ch.isdigit() for ch in token):
            return "__identifier__"
        return token

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        out = []
        for text in texts:
            vector = [0.0] * self.dims
            for token in tokenize(text):
                canonical = self._canonical(token)
                digest = hashlib.blake2b(canonical.encode(), digest_size=8).digest()
                vector[int.from_bytes(digest, "big") % self.dims] += 1.0
            norm = math.sqrt(sum(v * v for v in vector))
            out.append([v / norm for v in vector] if norm else vector)
        return out


@dataclass
class EmbeddingCache:
    """Content-addressed cache in front of an embedder.

    The key includes the model id and the dimension count, so a model swap is a
    miss rather than a silent mixture of two vector spaces. `stale_key_guard`
    verifies that property directly.
    """

    embedder: Embedder
    max_entries: int = 50_000
    _store: dict[str, list[float]] = field(default_factory=dict)
    hits: int = 0
    misses: int = 0

    def _key(self, text: str) -> str:
        payload = f"{self.embedder.model_id}|{self.embedder.dimensions}|{text}"
        return hashlib.sha256(payload.encode()).hexdigest()

    @property
    def model_id(self) -> str:
        return self.embedder.model_id

    @property
    def dimensions(self) -> int:
        return self.embedder.dimensions

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        keys = [self._key(t) for t in texts]
        missing = [
            (i, t) for i, (t, k) in enumerate(zip(texts, keys, strict=True)) if k not in self._store
        ]

        # Results are assembled here rather than read back out of the store,
        # because a batch larger than `max_entries` evicts its own earlier
        # entries while it is still being filled. Reading back then raises
        # KeyError on a cache that is behaving exactly as configured.
        resolved: dict[str, list[float]] = {k: self._store[k] for k in keys if k in self._store}

        if missing:
            self.misses += len(missing)
            fresh = self.embedder.embed([t for _, t in missing])
            for (i, _), vector in zip(missing, fresh, strict=True):
                self._evict_if_needed()
                self._store[keys[i]] = vector
                resolved[keys[i]] = vector
        self.hits += len(texts) - len(missing)

        return [resolved[k] for k in keys]

    def _evict_if_needed(self) -> None:
        # Insertion-ordered dicts make the oldest entry the first one. Crude,
        # and correct for the access pattern here: an ingest run embeds each
        # chunk once, so recency beats frequency.
        if len(self._store) >= self.max_entries:
            self._store.pop(next(iter(self._store)))

    @property
    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        return 0.0 if not total else self.hits / total

    def clear(self) -> None:
        self._store.clear()
