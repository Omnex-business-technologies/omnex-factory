"""P1 — production RAG with verified page citations.

The pipeline is ordinary: ingest, chunk, hybrid retrieve, rerank, generate. What
makes it shippable is the two things bolted to either end.

**Page anchors survive ingest.** Pages are carried as structure all the way to
the chunk, and a chunk straddling a page break records both. Reconstructing the
page afterwards is guesswork that is wrong exactly at page boundaries, which is
where a claim spanning a break lives.

**Every sentence is verified against the chunk it cites.** A fabricated citation
(a page never retrieved), an unsupported claim (a real page that does not say
it), and an invented number are three distinct failures with three distinct
handlings. What cannot be grounded is not returned — the honest answer is that
the documents do not say, which is worth more than a plausible paragraph a
customer will act on.
"""

from .figures import (
    Band,
    BBox,
    Composition,
    FigureRecord,
    FigureRegion,
    Manifest,
    ObjectKind,
    PageObject,
    PageSource,
    PerceptualHasher,
    RegionRenderer,
    RegionReport,
    TextRecognizer,
    cluster_page,
    duplicate_groups,
    extract_figures,
)
from .ground import GroundedAnswer, Grounder, GroundingVerdict, SentenceCheck
from .ingest import Document, Page, chunk_document, load_pdf, split_sentences
from .pipeline import REFUSAL, RagAnswer, RagConfig, RagPipeline, build_messages
from .rerank import CrossEncoderReranker, LexicalReranker, Reranker, recall_at

__all__ = [
    "REFUSAL",
    "BBox",
    "Band",
    "Composition",
    "CrossEncoderReranker",
    "Document",
    "FigureRecord",
    "FigureRegion",
    "GroundedAnswer",
    "Grounder",
    "GroundingVerdict",
    "LexicalReranker",
    "Manifest",
    "ObjectKind",
    "Page",
    "PageObject",
    "PageSource",
    "PerceptualHasher",
    "RagAnswer",
    "RagConfig",
    "RagPipeline",
    "RegionRenderer",
    "RegionReport",
    "Reranker",
    "SentenceCheck",
    "TextRecognizer",
    "build_messages",
    "chunk_document",
    "cluster_page",
    "duplicate_groups",
    "extract_figures",
    "load_pdf",
    "recall_at",
    "split_sentences",
]
