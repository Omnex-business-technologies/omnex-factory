"""P9 — fine-tuning: the parts around the training loop.

`trainer.train()` is four lines. What separates a fine-tune that helps from one
that quietly makes the product worse is decontamination, deduplication,
preference-pair validation and a measured catastrophic-forgetting check — all of
which are text and data problems, so all of which are tested on every commit
while the four lines that need a GPU are not.
"""

from .dataset import (
    CapabilityDelta,
    DatasetReport,
    Example,
    ForgettingCheck,
    LoraConfig,
    PreferenceIssue,
    PreferencePair,
    check_preferences,
    prepare,
)

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
