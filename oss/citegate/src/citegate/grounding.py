"""Grounding: checking that each sentence is actually supported by its citation.

This is the file that makes the difference between a RAG demo and something you
would put in front of a customer. Retrieval quality gets all the attention, but
the failure that reaches users is not "we retrieved the wrong page" — it is the
model producing a fluent, plausible sentence that no retrieved page says, with a
citation attached to it. The citation makes it *more* convincing, not less.

So every sentence of a generated answer is verified against the chunk it cites,
and three distinct failures are separated because they need different responses:

**Fabricated citation** — cites a page that is not in the retrieved evidence at
all. Always dropped; there is nothing to check against.

**Unsupported claim** — cites a real chunk, but the chunk does not contain the
claim. This is the dangerous one and the common one.

**Uncited claim** — a sentence with no citation. Sometimes legitimate (a
connective like "In summary,"), so it is judged on whether it asserts anything.

Verification is lexical, not an LLM judge, and the trade is stated rather than
hidden. An entailment model or a judge call is more accurate and costs a model
call per sentence — on every request, which is a latency and cost profile most
products cannot carry, and which introduces a second model that can also
hallucinate. Content-word overlap against the cited chunk catches the failure
mode that actually occurs: an invented number, an invented name, an invented
relationship between two real things. It is conservative in the safe direction —
it can reject a correctly-paraphrased sentence, which costs a slightly terser
answer, and it does not accept an invented one.

`NumberCheck` exists separately because numbers are where this matters most and
where overlap is weakest. "The threshold is 4.2%" and "The threshold is 8.4%"
differ by one token and are entirely different claims, so every number in a
sentence must appear in the cited chunk.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum

_WORD = re.compile(r"[a-z0-9']+")

#: Sentence terminator, whitespace, then a capital or digit. The lookbehind also
#: accepts \x00, which is the citation mask below — without that, a sentence
#: ending in a citation never splits and one unsupported clause condemns every
#: supported claim beside it.
_SENTENCE = re.compile(r"(?<=[.!?\x00])\s+(?=[A-Z0-9\"'(\[])")
#: Personal titles are here because leaving them out was a real defect, not a
#: theoretical one: "Mr. Lee and Ms. Park disagreed." split into four fragments,
#: and a fragment is precisely what the grounding check cannot judge — "Mr."
#: carries no claim and no citation, so it scores as an unsupported sentence and
#: drags down the paragraph it was cut out of.
#:
#: This set must stay identical to the one in `omnex.rag.ingest`. The two
#: splitters are independent copies on purpose — citegate ships with no
#: dependencies — and they drifted HERE, in the data rather than in the code,
#: which is why comparing the two functions found nothing.
#: `engine/tests/test_citegate_parity.py` now runs both over one corpus and
#: fails on any difference.
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
#: Citations are masked before splitting: "…twenty. [p. 12]" otherwise splits
#: twice, once detaching the citation and once INSIDE it ("[p." / "12]"), and
#: either makes a correctly-cited claim read as uncited.
_CITATION_SPAN = re.compile(r"\[[^\]\n]{0,40}\]")
_MASK = "\x00{}\x00"
#: Matches a placeholder, so restoration touches only the citations a sentence
#: actually contains. Walking the document's whole citation list per sentence
#: instead is O(sentences x citations) — correct on every input, invisible on a
#: short answer, and 1,439 sentences/sec on a 4,000-sentence filing where the
#: same code does 30,000.
_MASK_REF = re.compile(r"\x00(\d+)\x00")


def tokenize(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def split_sentences(text: str) -> list[str]:
    """Sentence split that survives abbreviations and keeps citations attached."""
    citations: list[str] = []

    def mask(match: re.Match[str]) -> str:
        citations.append(match.group(0))
        return _MASK.format(len(citations) - 1)

    parts = _SENTENCE.split(_CITATION_SPAN.sub(mask, text.strip()))

    merged: list[str] = []
    for part in parts:
        words = merged[-1].split() if merged else []
        if merged and words and words[-1].lower() in _ABBREVIATIONS:
            merged[-1] = f"{merged[-1]} {part}"
        else:
            merged.append(part)

    def unmask(match: re.Match[str]) -> str:
        index = int(match.group(1))
        return citations[index] if index < len(citations) else match.group(0)

    out = []
    for sentence in merged:
        restored = _MASK_REF.sub(unmask, sentence) if "\x00" in sentence else sentence
        if restored.strip():
            out.append(restored.strip())
    return out


@dataclass(frozen=True)
class Source:
    """One retrieved passage and the page it came from.

    Deliberately minimal, so adapting a LangChain Document or a LlamaIndex Node
    is one line rather than an integration.
    """

    page: int
    text: str
    #: Last page, when the passage spans a break. A claim on a page boundary
    #: must be citable to both.
    page_end: int = 0

    @property
    def pages(self) -> tuple[int, ...]:
        last = max(self.page, self.page_end)
        return tuple(range(self.page, last + 1))


__all__ = [
    "CITATION_PATTERN",
    "GroundedAnswer",
    "Grounder",
    "SentenceCheck",
    "Source",
    "Verdict",
    "split_sentences",
]

CITATION_PATTERN = re.compile(r"\[(?:pp?\.?|pages?)\s*(\d+)(?:\s*[–-]\s*(\d+))?\]", re.IGNORECASE)
_NUMBER = re.compile(r"\d+(?:[.,]\d+)?%?")

#: Quantities written as words. Without these, "defaults to fifty connections"
#: passes a source saying "twenty connections" — one swapped content word out of
#: five keeps the overlap above threshold, and the swapped word is the entire
#: claim. Numerals get checked exactly; spelled-out quantities have to as well.
_NUMBER_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
    "thirty": "30",
    "forty": "40",
    "fifty": "50",
    "sixty": "60",
    "seventy": "70",
    "eighty": "80",
    "ninety": "90",
    "hundred": "100",
    "thousand": "1000",
    "million": "1000000",
}

#: Words carrying no claim. Excluded from overlap so a sentence is judged on
#: what it asserts rather than on how much grammar it shares with the source.
_STOPWORDS = frozenset(
    [
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "if",
        "then",
        "than",
        "that",
        "this",
        "these",
        "those",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "of",
        "in",
        "on",
        "at",
        "to",
        "for",
        "from",
        "by",
        "with",
        "as",
        "it",
        "its",
        "their",
        "his",
        "her",
        "our",
        "your",
        "my",
        "we",
        "you",
        "they",
        "he",
        "she",
        "not",
        "no",
        "nor",
        "do",
        "does",
        "did",
        "has",
        "have",
        "had",
        "can",
        "could",
        "will",
        "would",
        "shall",
        "should",
        "may",
        "might",
        "must",
        "there",
        "here",
        "when",
        "where",
        "which",
        "who",
        "whom",
        "what",
        "how",
        "why",
        "also",
        "very",
        "more",
        "most",
        "such",
        "into",
        "over",
        "under",
        "about",
        "between",
        "during",
        "within",
        "while",
        "because",
        "so",
        "however",
        "therefore",
        "thus",
        "hence",
    ]
)


class Verdict(StrEnum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    FABRICATED_CITATION = "fabricated_citation"
    UNCITED = "uncited"
    #: A sentence that asserts nothing — "In summary," or a heading.
    NO_CLAIM = "no_claim"


@dataclass(frozen=True)
class SentenceCheck:
    sentence: str
    verdict: Verdict
    cited_pages: tuple[int, ...] = ()
    #: Fraction of the sentence's content words found in the cited chunk.
    overlap: float = 0.0
    #: Numbers in the sentence that the cited chunk does not contain.
    missing_numbers: tuple[str, ...] = ()

    @property
    def keep(self) -> bool:
        return self.verdict in (Verdict.SUPPORTED, Verdict.NO_CLAIM)


@dataclass
class GroundedAnswer:
    """An answer after verification, with everything that was removed recorded."""

    text: str
    checks: list[SentenceCheck] = field(default_factory=list)
    pages_cited: tuple[int, ...] = ()

    @property
    def refused(self) -> bool:
        """True when nothing survived — the honest 'the documents do not say'."""
        return not self.text.strip()

    @property
    def dropped(self) -> list[SentenceCheck]:
        return [c for c in self.checks if not c.keep]

    @property
    def support_rate(self) -> float:
        claims = [c for c in self.checks if c.verdict is not Verdict.NO_CLAIM]
        if not claims:
            return 1.0
        return sum(1 for c in claims if c.keep) / len(claims)

    def report(self) -> str:
        lines = [f"{self.support_rate:.0%} of claims supported; pages {list(self.pages_cited)}"]
        for check in self.dropped:
            lines.append(f"  dropped [{check.verdict}] {check.sentence[:70]!r}")
        return "\n".join(lines)


@dataclass
class Grounder:
    """Verifies a generated answer against the evidence it was given."""

    #: Content-word overlap required to call a sentence supported. 0.5 is
    #: deliberately not high: a correct paraphrase shares roughly half its
    #: content words with the source, while an invented claim introduces
    #: entities the source never mentions and falls well below.
    min_overlap: float = 0.5
    #: Every number in a claim must appear in the cited chunk. Not negotiable
    #: by threshold: 4.2% and 8.4% differ by one token and are different facts.
    require_numbers: bool = True
    #: Sentences with fewer content words than this assert nothing.
    min_content_words: int = 3

    def check(self, answer: str, evidence: Sequence[Source]) -> GroundedAnswer:
        by_page: dict[int, list[Source]] = {}
        for chunk in evidence:
            for page in chunk.pages or (0,):
                by_page.setdefault(page, []).append(chunk)

        checks: list[SentenceCheck] = []
        kept: list[str] = []
        pages_used: set[int] = set()

        for sentence in _sentences(answer):
            check = self._check_sentence(sentence, by_page)
            checks.append(check)
            if check.keep:
                kept.append(sentence)
                pages_used.update(check.cited_pages)

        return GroundedAnswer(
            text=" ".join(kept).strip(),
            checks=checks,
            pages_cited=tuple(sorted(pages_used)),
        )

    def _check_sentence(self, sentence: str, by_page: dict[int, list[Source]]) -> SentenceCheck:
        cited = _cited_pages(sentence)
        # The claim is the sentence WITHOUT its citation. Leaving the citation
        # in means the page number is checked as if it were an asserted figure —
        # "[p. 12]" then reads as the claim "12", which the source never states,
        # and every correctly-cited sentence fails.
        claim = _without_citations(sentence)
        content = _content_words(claim)

        # Two rules decide whether a sentence asserts anything.
        #
        # A CITED sentence is always a claim. Attaching a citation is the author
        # declaring "the source says this", so it gets verified however short it
        # is. Without this rule, "It also scales automatically. [p. 12]" has two
        # content words, is classed as a connective, and sails through as an
        # invented capability with a citation attached to it.
        #
        # A sentence carrying a quantity is always a claim too: "The threshold
        # is 4.2%." has two content words and is entirely an assertion.
        looks_like_prose = len(content) < self.min_content_words
        if looks_like_prose and not cited and not _quantities(claim):
            return SentenceCheck(sentence, Verdict.NO_CLAIM, cited)

        if not cited:
            return SentenceCheck(sentence, Verdict.UNCITED)

        supporting = [c for page in cited for c in by_page.get(page, [])]
        if not supporting:
            # The model named a page that was never retrieved. There is nothing
            # to verify against, and the citation is doing active harm by
            # making the claim look checked.
            return SentenceCheck(sentence, Verdict.FABRICATED_CITATION, cited)

        best_overlap = 0.0
        best_missing: tuple[str, ...] = ()
        for chunk in supporting:
            chunk_words = set(_content_words(chunk.text))
            overlap = len(content & chunk_words) / len(content)
            missing = _missing_numbers(claim, chunk.text) if self.require_numbers else ()
            if overlap > best_overlap or (overlap == best_overlap and not missing):
                best_overlap, best_missing = overlap, missing

        if best_missing:
            return SentenceCheck(sentence, Verdict.UNSUPPORTED, cited, best_overlap, best_missing)
        if best_overlap < self.min_overlap:
            return SentenceCheck(sentence, Verdict.UNSUPPORTED, cited, best_overlap)
        return SentenceCheck(sentence, Verdict.SUPPORTED, cited, best_overlap)


def _sentences(text: str) -> list[str]:
    return split_sentences(text)


def _without_citations(sentence: str) -> str:
    """The asserted claim, with its citations removed."""
    return CITATION_PATTERN.sub(" ", sentence).strip()


def _content_words(text: str) -> set[str]:
    return {w for w in tokenize(text) if w not in _STOPWORDS and len(w) > 2}


def _cited_pages(sentence: str) -> tuple[int, ...]:
    pages: set[int] = set()
    for match in CITATION_PATTERN.finditer(sentence):
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        pages.update(range(start, end + 1))
    return tuple(sorted(pages))


def _missing_numbers(sentence: str, source: str) -> tuple[str, ...]:
    """Numbers asserted but absent from the source.

    Normalised so 1,200 and 1200 match, and so a percentage in the claim is
    found in a source that writes it the same way. Deliberately does NOT try to
    match 0.042 against 4.2% — a unit conversion the model performed silently is
    exactly the kind of step that should be checked by a human rather than
    accepted by a regex.
    """
    claimed = _quantities(sentence)
    if not claimed:
        return ()
    return tuple(sorted(claimed - _quantities(source)))


def _quantities(text: str) -> set[str]:
    """Every number in the text, whether written as a numeral or as a word."""
    found = {_normalise_number(n) for n in _NUMBER.findall(text)}
    found.update(_NUMBER_WORDS[w] for w in tokenize(text) if w in _NUMBER_WORDS)
    return found


def _normalise_number(raw: str) -> str:
    return raw.replace(",", "").rstrip("%").rstrip("0").rstrip(".") or "0"
