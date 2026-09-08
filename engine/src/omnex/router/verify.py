"""Deciding whether a cheap answer is good enough to keep.

This is the hinge of the whole router. Routing by predicted complexity alone is
a guess; what makes it safe is catching the guess when it was wrong and
escalating. So the verifier's job is narrow and specific: **detect that the
model did not actually answer**, not judge whether the answer is correct.

Correctness needs a judge, and a judge is another model call — which costs about
what escalating would have cost, on *every* request rather than the failing
fraction, so it deletes the saving it was meant to protect. `LlmVerifier` exists
for the cases where that trade is worth making (P4's offline eval loop, where
there is no latency budget and accuracy is the product), and it is not the
default.

What is detectable for free is surprisingly load-bearing, because a weak model
failing an over-its-head task does not usually produce a confident wrong
answer — it hedges, refuses, restates the question, or runs out of tokens
mid-sentence. All four are visible in the text.

Truncation deserves its own mention. `finish_reason == length` is not an error,
raises nothing, and returns text that looks fine until you notice it stops in
the middle of a sentence. It is the easiest failure to ship in an LLM system,
and it is the cheapest one to catch — one enum comparison.
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..llm.types import Completion, FinishReason, Message

__all__ = ["HeuristicVerifier", "JsonVerifier", "Verdict", "Verifier", "all_of"]


@dataclass(frozen=True)
class Verdict:
    accept: bool
    reason: str = ""
    #: Rough confidence in the verdict itself, for tracing and for P15's
    #: uncertainty gate. Not the model's confidence in its answer — nothing
    #: here can observe that.
    confidence: float = 1.0

    @classmethod
    def ok(cls) -> Verdict:
        return cls(accept=True)

    @classmethod
    def reject(cls, reason: str, confidence: float = 1.0) -> Verdict:
        return cls(accept=False, reason=reason, confidence=confidence)


@runtime_checkable
class Verifier(Protocol):
    def check(self, messages: Sequence[Message], completion: Completion) -> Verdict: ...


#: Phrases a model reaches for when it cannot do the task. Deliberately narrow:
#: a broad list rejects legitimate hedging in answers that are genuinely
#: uncertain, and every false rejection is a full-price escalation.
_REFUSAL = re.compile(
    r"("
    r"\bi (?:do not|don't|cannot|can't) (?:know|determine|answer|help with)\b"
    # Both contractions and the expanded form: models write "I am not sure" at
    # least as often as "I'm not sure", and matching only the contraction lets
    # half of all hedges through unnoticed.
    r"|\bi(?:'m| am)? not (?:sure|certain|able to)\b"
    r"|\bunable to (?:determine|answer|assist)\b"
    r"|\binsufficient information\b"
    r"|\bas an ai\b"
    r"|\bi (?:would need|need) more (?:information|context)\b"
    r")",
    re.IGNORECASE,
)

#: Restating the question instead of answering it.
_ECHO_THRESHOLD = 0.75

#: Below this many significant words, an answer cannot meaningfully be a
#: restatement — it is a label, a number or a name, and those legitimately reuse
#: the prompt's vocabulary.
_MIN_WORDS_FOR_ECHO_CHECK = 6

#: A restatement is roughly as long as the question. An answer far shorter than
#: the prompt is a distillation, which is what extraction and summarisation are
#: *supposed* to produce — and both reuse the prompt's vocabulary almost
#: entirely.
_MIN_LENGTH_RATIO_FOR_ECHO_CHECK = 0.5


@dataclass
class HeuristicVerifier:
    """Free checks for "the model did not answer". No tokens, no latency."""

    #: Below this many characters an answer is treated as non-responsive,
    #: unless the request looks like it wants a one-word answer.
    min_chars: int = 12
    reject_truncated: bool = True
    reject_refusals: bool = True

    def check(self, messages: Sequence[Message], completion: Completion) -> Verdict:
        text = completion.text.strip()

        if not text:
            return Verdict.reject("empty response")

        if self.reject_truncated and completion.finish_reason is FinishReason.LENGTH:
            # Escalation is not always the right answer here — sometimes the fix
            # is a bigger max_tokens on the same model — but returning a
            # sentence that stops halfway never is.
            return Verdict.reject("truncated at max_tokens", confidence=1.0)

        if self.reject_refusals and _REFUSAL.search(text):
            return Verdict.reject("model declined or hedged", confidence=0.9)

        prompt = messages[-1].content.strip() if messages else ""
        if len(text) < self.min_chars and not _wants_short_answer(prompt):
            return Verdict.reject(f"answer of {len(text)} chars is not responsive", confidence=0.7)

        # The echo check only applies to answers long enough to BE a
        # restatement. This is not a nicety: for a classification or extraction
        # task the correct answer is necessarily a word lifted from the prompt
        # ("billing", "technical"), so an unguarded echo check rejects every
        # correct cheap answer on exactly the tasks the cheap tier exists to
        # serve. Each false rejection then costs a full-price escalation, and
        # the router silently spends more than having no router at all —
        # measured, not hypothetical: it turned a 60% saving into a 2% loss
        # across the 200-task benchmark before this guard existed.
        if (
            prompt
            and _could_be_a_restatement(prompt, text)
            and _echo_ratio(prompt, text) > _ECHO_THRESHOLD
        ):
            return Verdict.reject("restated the question without answering", confidence=0.8)

        return Verdict.ok()


def _wants_short_answer(prompt: str) -> bool:
    """Whether a very short answer is legitimate rather than non-responsive.

    The second pattern matters more than it looks. A factual lookup — "What is
    the capital of…", "Who wrote…" — is correctly answered by a single noun, and
    a blanket minimum length rejects the right answer, escalates, and pays full
    price to be told "Prague" a second time.
    """
    return bool(
        re.search(
            r"\b(yes or no|true or false|one word|how many|what year|classify|label)\b",
            prompt,
            re.IGNORECASE,
        )
        or re.match(r"\s*(what|who|which|where|when)\s+(is|was|are|were)\b", prompt, re.IGNORECASE)
    )


def _significant_words(text: str) -> list[str]:
    return [w for w in re.findall(r"\w+", text.lower()) if len(w) > 3]


def _could_be_a_restatement(prompt: str, answer: str) -> bool:
    """Whether the echo check can say anything useful about this pair.

    Two guards, both learned from the benchmark rather than assumed. A short
    answer is a label ("billing"), and a label legitimately comes from the
    prompt's own vocabulary. A short answer to a long prompt is a distillation —
    an extraction or a summary — which reuses that vocabulary by definition.
    Without these, the check rejects correct answers on precisely the mechanical
    tasks the cheap tier exists to serve, and every false rejection buys a
    full-price escalation.
    """
    answer_words = _significant_words(answer)
    if len(answer_words) < _MIN_WORDS_FOR_ECHO_CHECK:
        return False
    prompt_words = _significant_words(prompt)
    if not prompt_words:
        return False
    return len(answer_words) >= _MIN_LENGTH_RATIO_FOR_ECHO_CHECK * len(prompt_words)


def _echo_ratio(prompt: str, answer: str) -> float:
    """Fraction of the answer's words that came straight from the prompt.

    Cheap proxy for "restated the question". Word-level rather than character
    level, because a substring measure fires on any answer that quotes a term
    from the question, which is most correct answers.
    """
    answer_words = _significant_words(answer)
    if not answer_words:
        return 0.0
    prompt_words = set(_significant_words(prompt))
    shared = sum(1 for w in answer_words if w in prompt_words)
    return shared / len(answer_words)


@dataclass
class JsonVerifier:
    """Rejects output that is not parseable JSON, optionally with required keys.

    Worth having as its own verifier because a truncated JSON response is the
    single most common structured-output failure, and it fails *downstream* —
    in a parser, with a message about an unexpected end of input, far from the
    model call that caused it.
    """

    required_keys: tuple[str, ...] = ()

    def check(self, messages: Sequence[Message], completion: Completion) -> Verdict:
        text = completion.text.strip()
        # Models fence JSON in markdown more often than not.
        fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.S)
        if fenced:
            text = fenced.group(1)
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            return Verdict.reject(f"not valid JSON: {exc.msg}")
        if self.required_keys:
            if not isinstance(payload, dict):
                return Verdict.reject("JSON is not an object")
            missing = [k for k in self.required_keys if k not in payload]
            if missing:
                return Verdict.reject(f"missing keys: {', '.join(missing)}")
        return Verdict.ok()


def all_of(*verifiers: Verifier) -> Verifier:
    """Combine verifiers; the first rejection wins and carries its reason."""

    @dataclass
    class _All:
        parts: tuple[Verifier, ...]

        def check(self, messages: Sequence[Message], completion: Completion) -> Verdict:
            for verifier in self.parts:
                verdict = verifier.check(messages, completion)
                if not verdict.accept:
                    return verdict
            return Verdict.ok()

    return _All(verifiers)
