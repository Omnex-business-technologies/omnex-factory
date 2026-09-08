"""Anomaly detection and alerting that a human will not learn to ignore.

Two failure modes kill an alerting system, and neither is "the maths was not
clever enough".

**Detection on mean and standard deviation is broken by the thing it is
detecting.** A cost spike raises the mean and inflates the standard deviation,
so the z-score of the spike is suppressed by the spike's own contribution — the
bigger the anomaly, the harder it is to see. Worse, one extreme sample poisons
the baseline for as long as it stays in the window. So the baseline here is the
MEDIAN and the median absolute deviation. Both have a breakdown point of 50%:
up to half the window can be garbage before the estimate moves. The score is the
standard modified z-score, `0.6745 * (x - median) / MAD`, where the constant
makes MAD a consistent estimator of σ for normal data, so the familiar
thresholds still mean roughly what people expect.

**Alerts that fire on a single sample get muted by the people they page.** One
slow request is not an incident. So a rule must hold for a sustained period
before it fires, and — separately — must be clear for a period before it
resolves. The two thresholds are asymmetric on purpose: a metric hovering at the
boundary otherwise flaps between firing and resolved, which produces a pager
storm from a system that is merely borderline.

MAD of zero is handled explicitly rather than by adding an epsilon. It means
every sample in the window is identical, which is common for a healthy counter
of a rare event, and dividing by an epsilon there reports the first non-zero
value as an infinitely severe anomaly.
"""

from __future__ import annotations

import statistics
from collections import deque
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal

__all__ = ["Alert", "AlertManager", "AlertRule", "Comparison", "RobustBaseline", "Severity"]

#: Makes MAD a consistent estimator of the standard deviation for normal data.
_MAD_TO_SIGMA = 0.6745


class Severity(StrEnum):
    PAGE = "page"
    TICKET = "ticket"
    INFO = "info"


Comparison = Literal["gt", "lt"]


@dataclass
class RobustBaseline:
    """A rolling window scored by median and median absolute deviation."""

    window: int = 100
    #: Modified z-score beyond which a sample is anomalous. 3.5 is the
    #: conventional cut; it corresponds to roughly one in 2,000 for normal data.
    threshold: float = 3.5
    #: Below this many samples the baseline refuses to judge. A detector that
    #: fires on its third-ever observation trains its audience to ignore it.
    min_samples: int = 20
    values: deque[float] = field(default_factory=deque)

    def __post_init__(self) -> None:
        self.values = deque(self.values, maxlen=self.window)

    def observe(self, value: float) -> None:
        self.values.append(value)

    @property
    def median(self) -> float | None:
        return statistics.median(self.values) if self.values else None

    @property
    def mad(self) -> float | None:
        if not self.values:
            return None
        med = statistics.median(self.values)
        return statistics.median([abs(v - med) for v in self.values])

    def score(self, value: float) -> float | None:
        """Modified z-score of `value`, or None when the window cannot support a judgement."""
        if len(self.values) < self.min_samples:
            return None
        med = statistics.median(self.values)
        mad = statistics.median([abs(v - med) for v in self.values])
        if mad == 0:
            # Every sample identical. Any deviation is *something*, but MAD
            # cannot scale it, so fall back to the mean absolute deviation and
            # give up rather than divide by an epsilon and report infinity.
            mean_abs = statistics.fmean([abs(v - med) for v in self.values])
            if mean_abs == 0:
                return None if value == med else float("inf")
            return (value - med) / mean_abs
        return _MAD_TO_SIGMA * (value - med) / mad

    def is_anomalous(self, value: float) -> bool:
        score = self.score(value)
        return score is not None and abs(score) >= self.threshold


@dataclass(frozen=True)
class AlertRule:
    """A named condition, with the sustain and clear periods that stop flapping."""

    name: str
    metric: str
    threshold: float
    comparison: Comparison = "gt"
    severity: Severity = Severity.TICKET
    #: Consecutive breaching evaluations required before firing.
    for_evaluations: int = 3
    #: Consecutive healthy evaluations required before resolving. Deliberately
    #: larger than `for_evaluations` — resolving faster than firing is what
    #: makes a borderline metric flap.
    clear_evaluations: int = 5
    summary: str = ""

    def breached(self, value: float) -> bool:
        return value > self.threshold if self.comparison == "gt" else value < self.threshold


@dataclass
class Alert:
    rule: AlertRule
    value: float
    fired_at_evaluation: int
    labels: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        return {
            "alert": self.rule.name,
            "severity": self.rule.severity.value,
            "metric": self.rule.metric,
            "value": self.value,
            "threshold": self.rule.threshold,
            "summary": self.rule.summary
            or f"{self.rule.metric} {self.rule.comparison} {self.rule.threshold}",
            **self.labels,
        }


@dataclass
class _RuleState:
    breaching_streak: int = 0
    healthy_streak: int = 0
    firing: bool = False


class AlertManager:
    """Evaluates rules against metric values and emits state transitions only.

    Returns *transitions* rather than the current state, because a system that
    re-notifies on every evaluation while a condition persists is a system whose
    notifications get filtered into a folder nobody opens.
    """

    def __init__(self, rules: list[AlertRule]) -> None:
        self.rules = rules
        self._state: dict[str, _RuleState] = {r.name: _RuleState() for r in rules}
        self._evaluations = 0

    @property
    def firing(self) -> list[str]:
        return sorted(name for name, st in self._state.items() if st.firing)

    def evaluate(self, values: dict[str, float]) -> tuple[list[Alert], list[str]]:
        """One evaluation cycle. Returns (newly firing, newly resolved rule names)."""
        self._evaluations += 1
        fired: list[Alert] = []
        resolved: list[str] = []

        for rule in self.rules:
            if rule.metric not in values:
                continue
            value = values[rule.metric]
            state = self._state[rule.name]

            if rule.breached(value):
                state.breaching_streak += 1
                state.healthy_streak = 0
                if not state.firing and state.breaching_streak >= rule.for_evaluations:
                    state.firing = True
                    fired.append(
                        Alert(rule=rule, value=value, fired_at_evaluation=self._evaluations)
                    )
            else:
                state.healthy_streak += 1
                state.breaching_streak = 0
                if state.firing and state.healthy_streak >= rule.clear_evaluations:
                    state.firing = False
                    resolved.append(rule.name)

        return fired, resolved
