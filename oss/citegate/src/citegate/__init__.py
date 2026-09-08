"""citegate — verify that a RAG answer is supported by the sources it cites.

Zero dependencies, microseconds per sentence, designed to run in the request
path rather than in an offline eval. See README.md for what it catches, what it
does not, and why the trade is made that way.
"""

from .grounding import (
    GroundedAnswer,
    Grounder,
    SentenceCheck,
    Source,
    Verdict,
    split_sentences,
)

__all__ = [
    "GroundedAnswer",
    "Grounder",
    "SentenceCheck",
    "Source",
    "Verdict",
    "split_sentences",
]
__version__ = "0.1.0"
