"""Ingest that keeps the page anchor, because the citation depends on it.

The reason page-number citations are hard is not the citation. It is that by the
time text reaches a chunker it has usually been concatenated into one string,
and the page it came from is gone. Reconstructing it afterwards — by counting
characters, by re-searching the source — is guesswork that is wrong precisely at
page boundaries, which is where a claim spanning a page break lives. The reader
then follows a citation to page 12 and finds half a sentence.

So pages are carried as structure through the whole pipeline: a `Document` is a
list of `Page`, chunking maps each chunk's span back onto the pages it covers,
and a chunk that straddles a break records both.

**Chunks split on sentence boundaries, not character counts.** A chunk that ends
mid-sentence produces two failures at once: retrieval matches half a statement,
and the grounding check (ground.py) cannot verify a claim against a fragment
that does not contain it. Splitting at the nearest sentence boundary costs a
little size variance and buys a corpus where every chunk is a complete thought.

**Overlap is measured in sentences, not characters.** Character overlap
routinely cuts mid-word and produces a chunk starting "…ation protocol handles",
which is noise in the lexical index and a bad embedding on the dense side.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..core.errors import ConfigurationError, ValidationFailed
from ..core.ids import IdFactory
from ..vectors.types import Chunk

__all__ = ["Document", "Page", "chunk_document", "load_pdf", "split_sentences"]

#: Sentence terminator followed by whitespace and a capital or a digit. Avoids
#: splitting on "e.g." and "No. 4" — abbreviations are the usual source of
#: fragment chunks in naive splitters.
#: A masked citation (see below) ends with \x00, and a sentence very often ends
#: with one. Without \x00 in the lookbehind, masking fixes the split-inside-a-
#: citation bug and introduces a worse one: no sentence ending in a citation
#: ever splits, so a whole grounded answer becomes a single "sentence" and one
#: unsupported claim condemns every supported claim beside it.
_SENTENCE = re.compile(r"(?<=[.!?\x00])\s+(?=[A-Z0-9\"'(\[])")
_ABBREVIATIONS = {
    "e.g.",
    "i.e.",
    "etc.",
    "vs.",
    "cf.",
    "no.",
    "fig.",
    "approx.",
    "dr.",
    "mr.",
    "ms.",
}


#: Bracketed citations, masked before splitting and restored afterwards.
#:
#: Two separate ways the splitter mangles "…twenty connections. [p. 12]": the
#: period-space-bracket detaches the citation from its sentence, and the period
#: inside "[p. 12]" splits the citation itself into "[p." and "12]". Both make a
#: correctly-cited claim read as uncited, which fails every grounded answer in
#: the system. Masking removes the split triggers entirely rather than trying to
#: out-clever them with lookarounds.
#:
#: Length-bounded so a long bracketed block in a source document is not swallowed.
_CITATION_SPAN = re.compile(r"\[[^\]\n]{0,40}\]")
_MASK = "\x00{}\x00"
#: Matches a placeholder so restoration touches only the citations a sentence
#: actually contains. Scanning the full citation list per sentence instead is
#: quadratic in the document, which is invisible on a three-sentence answer and
#: is the difference between 0.9s and 4.5s on a four-thousand-sentence filing.
_MASK_REF = re.compile(r"\x00(\d+)\x00")


def _ends_with_abbreviation(sentence: str) -> bool:
    words = sentence.split()
    return bool(words) and words[-1].lower() in _ABBREVIATIONS


def split_sentences(text: str) -> list[str]:
    """Sentence split that does not fall over on common abbreviations.

    The regex alone splits "…see e.g. Table 4" into two, because a period
    followed by a capital is exactly what it looks for. Abbreviations are the
    single biggest source of fragment chunks in naive splitters, and a fragment
    chunk breaks the grounding check downstream — a claim cannot be verified
    against half of the sentence that supports it.
    """
    citations: list[str] = []

    def mask(match: re.Match[str]) -> str:
        citations.append(match.group(0))
        return _MASK.format(len(citations) - 1)

    masked = _CITATION_SPAN.sub(mask, text.strip())
    parts = _SENTENCE.split(masked)

    merged: list[str] = []
    for part in parts:
        if merged and _ends_with_abbreviation(merged[-1]):
            merged[-1] = f"{merged[-1]} {part}"
        else:
            merged.append(part)

    def unmask(match: re.Match[str]) -> str:
        index = int(match.group(1))
        return citations[index] if index < len(citations) else match.group(0)

    restored = []
    for sentence in merged:
        text_out = (
            _MASK_REF.sub(unmask, sentence).strip() if "\x00" in sentence else sentence.strip()
        )
        if text_out:
            restored.append(text_out)
    return restored


@dataclass(frozen=True)
class Page:
    """One page, with its 1-based number preserved from the source."""

    number: int
    text: str


@dataclass
class Document:
    """A source document as a sequence of pages.

    `offsets` maps each page to its span in the concatenated text, which is what
    lets a chunk's character span be translated back into page numbers without
    guessing.
    """

    doc_id: str
    pages: list[Page] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_text(cls, doc_id: str, text: str, **metadata: Any) -> Document:
        """A single-page document. Page 1 rather than page 0 — a citation to
        page 0 is a citation nobody can follow."""
        return cls(doc_id=doc_id, pages=[Page(1, text)], metadata=dict(metadata))

    @classmethod
    def from_pages(cls, doc_id: str, texts: Sequence[str], **metadata: Any) -> Document:
        return cls(
            doc_id=doc_id,
            pages=[Page(i, t) for i, t in enumerate(texts, start=1)],
            metadata=dict(metadata),
        )

    @property
    def page_count(self) -> int:
        return len(self.pages)

    def full_text(self) -> tuple[str, list[tuple[int, int, int]]]:
        """Concatenated text plus `(page_number, start, end)` spans.

        Pages are joined with a newline, and the separator is accounted for in
        the offsets — an off-by-one here shifts every citation in a long
        document by one page somewhere in the middle.
        """
        parts: list[str] = []
        offsets: list[tuple[int, int, int]] = []
        cursor = 0
        for index, page in enumerate(self.pages):
            text = page.text
            parts.append(text)
            offsets.append((page.number, cursor, cursor + len(text)))
            cursor += len(text)
            if index < len(self.pages) - 1:
                parts.append("\n")
                cursor += 1
        return "".join(parts), offsets

    def pages_for_span(self, start: int, end: int) -> tuple[int, int]:
        """Which pages a character span touches. Inclusive on both ends."""
        _, offsets = self.full_text()
        touched = [n for n, s, e in offsets if start < e and end > s]
        if not touched:
            return (0, 0)
        return (min(touched), max(touched))


def chunk_document(
    document: Document,
    target_chars: int = 900,
    overlap_sentences: int = 1,
    min_chars: int = 120,
    ids: IdFactory | None = None,
    **metadata: Any,
) -> list[Chunk]:
    """Split into retrievable chunks with page anchors intact.

    `target_chars` rather than tokens because the boundary is a sentence
    anyway — token-exact chunking is precision applied to the wrong decision,
    and it requires a tokenizer at ingest time for no retrieval benefit.
    """
    if target_chars < min_chars:
        raise ValidationFailed("target_chars must be at least min_chars", target=target_chars)

    factory = ids or IdFactory()
    text, _ = document.full_text()
    sentences = split_sentences(text)
    if not sentences:
        return []

    # Locate every sentence in the concatenated text, so spans are exact rather
    # than reconstructed by re-joining with assumed whitespace.
    spans: list[tuple[int, int]] = []
    cursor = 0
    for sentence in sentences:
        found = text.find(sentence, cursor)
        if found < 0:  # pragma: no cover - split_sentences preserves content
            found = cursor
        spans.append((found, found + len(sentence)))
        cursor = found + len(sentence)

    chunks: list[Chunk] = []
    index = 0
    while index < len(sentences):
        end = index
        size = 0
        while end < len(sentences) and size < target_chars:
            size += len(sentences[end]) + 1
            end += 1

        start_char = spans[index][0]
        end_char = spans[end - 1][1]
        body = text[start_char:end_char].strip()

        if len(body) >= min_chars or not chunks:
            first_page, last_page = document.pages_for_span(start_char, end_char)
            chunks.append(
                Chunk(
                    id=factory.new("chk"),
                    text=body,
                    doc_id=document.doc_id,
                    page=first_page,
                    page_end=last_page,
                    char_span=(start_char, end_char),
                    metadata={**document.metadata, **metadata},
                )
            )
        elif chunks:
            # A short tail is merged into the previous chunk rather than kept as
            # its own. A 40-character chunk retrieves noisily — it matches on one
            # term with nothing around it to disambiguate — and it is the usual
            # source of a citation pointing at a heading.
            previous = chunks[-1]
            merged_span = (previous.char_span[0], end_char)
            first_page, last_page = document.pages_for_span(*merged_span)
            chunks[-1] = Chunk(
                id=previous.id,
                text=text[merged_span[0] : merged_span[1]].strip(),
                doc_id=previous.doc_id,
                page=first_page,
                page_end=last_page,
                char_span=merged_span,
                metadata=previous.metadata,
            )

        if end >= len(sentences):
            break
        index = max(index + 1, end - overlap_sentences)

    return chunks


def load_pdf(path: str | Path, doc_id: str = "", **metadata: Any) -> Document:
    """Read a PDF into pages, preserving the publisher's page numbering.

    Uses pypdf, which is the open-source, pure-Python option and needs no
    system libraries — important for the local-first tier, where the whole point
    is that ingest runs on a laptop with no services installed.
    """
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - only without the extra
        raise ConfigurationError(
            "PDF ingest needs the 'rag' extra: pip install 'omnex-engine[rag]'"
        ) from exc

    source = Path(path)
    reader = PdfReader(str(source))
    pages = [Page(number=i, text=(p.extract_text() or "")) for i, p in enumerate(reader.pages, 1)]

    empty = sum(1 for p in pages if not p.text.strip())
    if empty == len(pages):
        # A scanned PDF extracts as pages of nothing. Silently indexing an empty
        # document produces a corpus that answers every question with "the
        # documents do not say", and the cause is three layers away.
        raise ValidationFailed(
            "no extractable text — this looks like a scanned PDF and needs OCR first",
            path=str(source),
            pages=len(pages),
        )

    return Document(
        doc_id=doc_id or source.stem,
        pages=pages,
        metadata={"source": str(source), "empty_pages": empty, **metadata},
    )
