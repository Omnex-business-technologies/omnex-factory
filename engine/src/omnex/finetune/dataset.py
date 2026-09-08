"""Fine-tuning: the parts around the training loop, which is where it goes wrong.

`trainer.train()` is four lines and every tutorial has them. What separates a
fine-tune that helps from one that quietly makes the product worse is entirely
in this file, and none of it needs a GPU to get right.

**Decontamination before anything else.** A model trained on the eval set scores
excellently and means nothing, and the failure is invisible in every metric you
would look at — including the one you are about to put in a release note. P4's
`contamination_report` does the checking; `prepare()` refuses to build a dataset
that has not been through it.

**Deduplication, because duplicates are effectively a higher learning rate on
whatever is duplicated.** Scraped and generated corpora are full of near
duplicates, and the model over-fits precisely the passages that happened to be
copied around most.

**Catastrophic forgetting is measured, not hoped away.** A model fine-tuned on
your support tickets gets better at support tickets and worse at everything
else, and the "everything else" is where the regression is discovered by a
customer. `ForgettingCheck` runs a RETAINED capability suite before and after and
reports per-capability deltas — a single aggregate would let a gain on the target
task hide a collapse on general instruction-following.

**DPO pairs are checked for actual preference.** A pair whose chosen and rejected
responses are near-identical teaches nothing and adds noise; a pair where the
rejected response is better than the chosen one teaches the opposite of what was
intended. Both occur in real preference data, both are detectable, and neither
is detectable after training.

The training adapter needs PEFT and torch and is never installed in CI. Every
decision above is a text and data problem, deliberately, so it is tested on every
commit while the four lines that need a GPU are not.
"""

from __future__ import annotations

import hashlib
import statistics
from collections.abc import Sequence
from dataclasses import dataclass, field

from ..core.errors import ValidationFailed
from ..vectors.embed import tokenize

__all__ = [
    "CapabilityDelta",
    "DatasetReport",
    "Example",
    "ForgettingCheck",
    "LoraConfig",
    "PreferenceIssue",
    "PreferencePair",
    "check_preferences",
    "prepare",
]


@dataclass(frozen=True)
class Example:
    """One instruction-tuning example."""

    instruction: str
    response: str
    source: str = ""

    @property
    def fingerprint(self) -> str:
        """Normalised, so trivial whitespace and case differences still collide."""
        normalised = " ".join(tokenize(f"{self.instruction} {self.response}"))
        return hashlib.sha256(normalised.encode()).hexdigest()[:16]

    def shingles(self, size: int = 5) -> set[str]:
        words = tokenize(f"{self.instruction} {self.response}")
        if len(words) < size:
            return {" ".join(words)} if words else set()
        return {" ".join(words[i : i + size]) for i in range(len(words) - size + 1)}


@dataclass(frozen=True)
class PreferencePair:
    """A DPO training pair: one preferred response, one rejected."""

    prompt: str
    chosen: str
    rejected: str
    #: Optional independent scores. When present, they are checked against the
    #: labels — a pair whose "rejected" scores higher is mislabelled.
    chosen_score: float | None = None
    rejected_score: float | None = None


@dataclass
class DatasetReport:
    kept: list[Example] = field(default_factory=list)
    exact_duplicates: int = 0
    near_duplicates: int = 0
    too_short: int = 0
    contaminated: int = 0

    @property
    def removed(self) -> int:
        return self.exact_duplicates + self.near_duplicates + self.too_short + self.contaminated

    def report(self) -> str:
        return (
            f"{len(self.kept)} kept, {self.removed} removed "
            f"({self.exact_duplicates} exact dupes, {self.near_duplicates} near dupes, "
            f"{self.too_short} too short, {self.contaminated} contaminated)"
        )


def prepare(
    examples: Sequence[Example],
    eval_questions: Sequence[str],
    min_response_words: int = 5,
    near_duplicate_threshold: float = 0.8,
) -> DatasetReport:
    """Clean a dataset. Refuses to run without an eval set to decontaminate against.

    `eval_questions` is required rather than optional on purpose. Made optional,
    it is omitted, and the resulting model is evaluated on data it memorised.
    """
    if not eval_questions:
        raise ValidationFailed(
            "prepare() needs the eval questions to decontaminate against — "
            "a model trained on its own eval set scores excellently and means nothing"
        )

    report = DatasetReport()
    seen: set[str] = set()
    kept_shingles: list[set[str]] = []
    eval_shingles = [_shingles(q) for q in eval_questions]

    for example in examples:
        if len(tokenize(example.response)) < min_response_words:
            report.too_short += 1
            continue

        fingerprint = example.fingerprint
        if fingerprint in seen:
            report.exact_duplicates += 1
            continue

        shingles = example.shingles()
        # Near duplicates are effectively a higher learning rate on whatever
        # was copied around most, which is rarely what you want emphasised.
        if any(_overlap(shingles, other) >= near_duplicate_threshold for other in kept_shingles):
            report.near_duplicates += 1
            continue

        instruction_shingles = _shingles(example.instruction)
        if any(_overlap(instruction_shingles, e) >= 0.7 for e in eval_shingles):
            report.contaminated += 1
            continue

        seen.add(fingerprint)
        kept_shingles.append(shingles)
        report.kept.append(example)

    return report


def _shingles(text: str, size: int = 5) -> set[str]:
    words = tokenize(text)
    if len(words) < size:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i : i + size]) for i in range(len(words) - size + 1)}


def _overlap(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


@dataclass(frozen=True)
class PreferenceIssue:
    index: int
    kind: str
    detail: str


def check_preferences(
    pairs: Sequence[PreferencePair], min_difference: float = 0.15
) -> list[PreferenceIssue]:
    """Find pairs that teach nothing, or teach the opposite of what was meant.

    Both failures are common in real preference data — a labelling interface
    that defaults to the first option, a scoring model applied inconsistently —
    and neither is detectable after training. The model simply comes out
    slightly wrong in a way nobody can attribute.
    """
    issues: list[PreferenceIssue] = []
    for index, pair in enumerate(pairs):
        if pair.chosen.strip() == pair.rejected.strip():
            issues.append(PreferenceIssue(index, "identical", "chosen and rejected are the same"))
            continue

        similarity = _overlap(_shingles(pair.chosen, 4), _shingles(pair.rejected, 4))
        if similarity >= 0.95:
            issues.append(
                PreferenceIssue(
                    index, "near_identical", f"{similarity:.0%} overlap — teaches nothing"
                )
            )

        if pair.chosen_score is not None and pair.rejected_score is not None:
            if pair.rejected_score > pair.chosen_score:
                # Teaches the opposite of what was intended.
                issues.append(
                    PreferenceIssue(
                        index,
                        "inverted",
                        f"rejected scores {pair.rejected_score:.2f} above chosen "
                        f"{pair.chosen_score:.2f}",
                    )
                )
            elif pair.chosen_score - pair.rejected_score < min_difference:
                issues.append(
                    PreferenceIssue(
                        index,
                        "weak_preference",
                        f"only {pair.chosen_score - pair.rejected_score:.2f} apart",
                    )
                )
    return issues


@dataclass(frozen=True)
class CapabilityDelta:
    capability: str
    before: float
    after: float

    @property
    def delta(self) -> float:
        return self.after - self.before

    @property
    def regressed(self) -> bool:
        return self.delta < 0


@dataclass
class ForgettingCheck:
    """Before-and-after scores on a RETAINED capability suite.

    Per capability, never aggregated, because a fine-tune that gains 20 points
    on the target task and loses 30 on general instruction-following shows up as
    a small net loss in any average — and gets shipped, because the target task
    is the one being watched.
    """

    #: How much a retained capability may fall before the fine-tune is rejected.
    max_regression: float = 0.05

    def compare(self, before: dict[str, float], after: dict[str, float]) -> list[CapabilityDelta]:
        shared = sorted(set(before) & set(after))
        return [CapabilityDelta(name, before[name], after[name]) for name in shared]

    def verdict(self, deltas: Sequence[CapabilityDelta], target: str) -> tuple[bool, str]:
        """Accept the fine-tune? Returns (accept, reason)."""
        retained = [d for d in deltas if d.capability != target]
        target_delta = next((d for d in deltas if d.capability == target), None)

        worst = min(retained, key=lambda d: d.delta, default=None)
        if worst is not None and -worst.delta > self.max_regression:
            return False, (
                f"forgot {worst.capability}: {worst.before:.2f} → {worst.after:.2f} "
                f"({worst.delta:+.2f}), beyond the {self.max_regression:.2f} tolerance"
            )

        if target_delta is None:
            return False, f"the target capability {target!r} was not measured"
        if target_delta.delta <= 0:
            return False, (
                f"no gain on the target: {target_delta.before:.2f} → {target_delta.after:.2f}"
            )

        mean_retained = statistics.fmean([d.delta for d in retained]) if retained else 0.0
        return True, (
            f"{target} {target_delta.delta:+.2f}, retained capabilities {mean_retained:+.3f} mean"
        )

    def report(self, deltas: Sequence[CapabilityDelta], target: str) -> str:
        accept, reason = self.verdict(deltas, target)
        lines = [f"{'ACCEPT' if accept else 'REJECT'}: {reason}"]
        for delta in sorted(deltas, key=lambda d: d.delta):
            marker = " ←" if delta.regressed and delta.capability != target else ""
            lines.append(
                f"  {delta.capability:<28} {delta.before:.2f} → {delta.after:.2f} "
                f"({delta.delta:+.2f}){marker}"
            )
        return "\n".join(lines)


@dataclass(frozen=True)
class LoraConfig:
    """LoRA hyperparameters, with the two relationships that actually matter.

    `alpha / r` is the effective scaling, and it is the number to reason about
    rather than either alone — doubling `r` while holding `alpha` halves the
    update magnitude, which is the opposite of what most people expect when they
    "increase capacity".

    Targeting attention projections only is the common default and is usually
    wrong for style adaptation: the MLP layers carry more of what a fine-tune on
    tone is trying to change, and omitting them is why a run "does nothing".
    """

    r: int = 16
    alpha: int = 32
    dropout: float = 0.05
    target_modules: tuple[str, ...] = (
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    )
    learning_rate: float = 1e-4
    epochs: int = 2

    def __post_init__(self) -> None:
        if self.r < 1:
            raise ValidationFailed("LoRA rank must be at least 1")
        if self.epochs > 5:
            # Not a hard limit, but worth stating: past a few epochs on a small
            # adapter dataset the model memorises rather than generalises, and
            # the forgetting check is where that shows up.
            raise ValidationFailed(
                "more than 5 epochs on a LoRA adapter memorises rather than generalises; "
                "set it deliberately if that is what you want",
                epochs=self.epochs,
            )

    @property
    def scaling(self) -> float:
        """alpha / r — the effective update magnitude."""
        return self.alpha / self.r

    def as_peft_kwargs(self) -> dict[str, object]:
        return {
            "r": self.r,
            "lora_alpha": self.alpha,
            "lora_dropout": self.dropout,
            "target_modules": list(self.target_modules),
            "task_type": "CAUSAL_LM",
        }
