"""Predicting how hard a query is, without spending money to find out.

The constraint that shapes this whole file: **the classifier must be
essentially free**. Using a small model to decide which model to use costs about
what the small model would have cost answering directly, so an LLM-based
classifier eliminates most of the saving it exists to produce, and adds a
network round trip to every request. So this is lexical and structural — regex
and counting — and runs in microseconds.

That buys cheapness at the price of accuracy, and the errors are **not
symmetric**, which is the part usually missed:

- *Under*-estimating sends hard work to a weak model. The answer comes back
  wrong or hedged, the router escalates, and the request is paid for twice —
  plus double latency.
- *Over*-estimating sends easy work to an expensive model. Paid once, at the
  price that would have been paid anyway without any router.

Under-estimating is therefore the more expensive mistake, and `bias` exists to
push the score up when the cost ratio between tiers is small. Where exactly to
set it is derived in economics.py rather than guessed, because it depends on the
price ratio, not on taste.

Some markers *reduce* the score. Extraction, classification, translation and
formatting are long-prompt, short-answer, mechanically simple tasks — and a
naive length heuristic reads them as hard, which is the single biggest source of
false escalation in a system like this.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..llm.catalog import Tier

__all__ = ["SIGNALS", "Complexity", "ComplexityClassifier"]


@dataclass(frozen=True)
class Signal:
    name: str
    pattern: re.Pattern[str]
    #: Positive raises the score, negative lowers it.
    weight: float
    #: Cap on the contribution regardless of match count, so one word repeated
    #: forty times cannot dominate the classification.
    cap: float = 1.0


def _p(expr: str) -> re.Pattern[str]:
    return re.compile(expr, re.IGNORECASE)


SIGNALS: list[Signal] = [
    # ── raises complexity ────────────────────────────────────────────────
    Signal(
        "multi_step",
        _p(r"\b(step[- ]by[- ]step|first.{0,40}\bthen\b|walk me through|break (this|it) down)"),
        0.22,
    ),
    Signal("reasoning", _p(r"\b(why|justify|reason about|implications?)\b"), 0.18, cap=0.36),
    # Separate from, and heavier than, general reasoning. A request to prove or
    # derive demands formal correctness rather than a plausible explanation, and
    # it is the one category where a weak model's answer is confidently wrong
    # rather than visibly hedged — so the verifier is least likely to catch it
    # and the classifier has to.
    Signal(
        "formal_reasoning",
        _p(r"\b(prove|derive|theorem|lemma|by induction|formally show)\b"),
        0.30,
        cap=0.60,
    ),
    Signal(
        "comparison", _p(r"\b(compare|contrast|trade[- ]?offs?|versus|vs\.?|pros and cons)\b"), 0.16
    ),
    # Open-ended synthesis with no single correct answer. Weighted above general
    # reasoning because there is nothing to check the output against.
    Signal("design", _p(r"\b(design|architect|strategy|plan|approach for|how should we)\b"), 0.24),
    Signal(
        "math",
        _p(
            r"(\d+\s*[+\-*/^=]\s*\d+|\b(calculate|compute|solve for|integral|derivative|probability)\b)"
        ),
        0.18,
        cap=0.36,
    ),
    Signal("code_block", _p(r"```|\bdef \w+\(|\bclass \w+\b|\bSELECT\b.+\bFROM\b"), 0.15),
    Signal(
        "debugging",
        _p(r"\b(debug|why does.{0,30}(fail|crash|error)|stack ?trace|traceback)\b"),
        0.20,
    ),
    Signal(
        "constraints",
        _p(r"\b(must not|without using|ensure that|subject to|constraint)\b"),
        0.12,
        cap=0.24,
    ),
    Signal("open_ended", _p(r"\b(what would happen|speculate|forecast|what if)\b"), 0.16),
    Signal("ambiguity", _p(r"\b(it depends|unclear|ambiguous|not sure (what|which))\b"), 0.10),
    # ── lowers complexity ────────────────────────────────────────────────
    # Long prompt, short mechanical answer. Without these, a length heuristic
    # reads a 4,000-word document to classify as the hardest query of the day.
    Signal("extraction", _p(r"\b(extract|list all|find all|pull out|parse)\b"), -0.22),
    Signal(
        "classification",
        _p(r"\b(classify|categori[sz]e|label|is this (a|an)|which category)\b"),
        -0.24,
    ),
    Signal(
        "translation",
        _p(r"\b(translate|render in (english|spanish|german|french|croatian))\b"),
        -0.20,
    ),
    Signal(
        "formatting",
        _p(r"\b(reformat|convert to (json|csv|yaml|markdown)|fix the formatting)\b"),
        -0.24,
    ),
    Signal("lookup", _p(r"^\s*(what|who|when|where) (is|are|was|were)\b"), -0.16),
    Signal("summarise", _p(r"\b(summari[sz]e|tl;?dr|in one sentence)\b"), -0.12),
]


@dataclass(frozen=True)
class Complexity:
    """A score in [0, 1], the tier it maps to, and why."""

    score: float
    tier: Tier
    matched: tuple[str, ...] = ()
    length_component: float = 0.0

    def explain(self) -> str:
        signals = ", ".join(self.matched) if self.matched else "no lexical signals"
        return (
            f"score {self.score:.2f} → {self.tier} ({signals}; length {self.length_component:.2f})"
        )


@dataclass
class ComplexityClassifier:
    """Lexical complexity scoring. Microseconds, no network, no tokens.

    `thresholds` map score bands to tiers. They are ordered ascending and read
    as "score at or above this goes to this tier".
    """

    thresholds: tuple[tuple[float, Tier], ...] = (
        (0.00, Tier.NANO),
        (0.28, Tier.SMALL),
        (0.55, Tier.LARGE),
        (0.80, Tier.REASONING),
    )
    #: Added to every score. Raise it when the cheap/expensive price ratio is
    #: small enough that a wasted escalation costs more than always going big.
    #: economics.py derives the right value from the price ratio.
    bias: float = 0.0
    #: Length contribution saturates here — a long document is not linearly
    #: harder to reason about, and past a point it is a retrieval problem
    #: rather than a reasoning one.
    length_saturation_chars: int = 4000
    max_length_weight: float = 0.18
    signals: list[Signal] = field(default_factory=lambda: list(SIGNALS))

    def classify(self, text: str) -> Complexity:
        matched: list[str] = []
        score = 0.0

        for signal in self.signals:
            hits = len(signal.pattern.findall(text))
            if not hits:
                continue
            matched.append(signal.name)
            contribution = signal.weight * hits
            # Cap magnitude, preserving sign.
            if abs(contribution) > signal.cap:
                contribution = signal.cap if contribution > 0 else -signal.cap
            score += contribution

        length_component = self.max_length_weight * min(
            1.0, len(text) / self.length_saturation_chars
        )
        score += length_component

        # A question mark per clause suggests several distinct asks in one turn,
        # which is a genuinely harder request than the same words as a statement.
        questions = text.count("?")
        if questions > 1:
            score += min(0.12, 0.04 * (questions - 1))
            matched.append("multiple_questions")

        score = max(0.0, min(1.0, score + self.bias))
        return Complexity(
            score=score,
            tier=self.tier_for(score),
            matched=tuple(matched),
            length_component=length_component,
        )

    def tier_for(self, score: float) -> Tier:
        chosen = self.thresholds[0][1]
        for threshold, tier in self.thresholds:
            if score >= threshold:
                chosen = tier
        return chosen
