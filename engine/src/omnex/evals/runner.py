"""Running a suite, and the gate that decides whether a deploy proceeds.

**The gate blocks on newly-failing cases, not on the mean.** This is the whole
design and it is what most eval harnesses get wrong. An aggregate score is a
terrible regression signal: five cases breaking and five improving leaves the
mean flat, and the deploy ships with five things newly broken. Worse, the mean
recovers on the next commit while the five stay broken forever, because nobody
ever looked at them.

So a run is compared to its baseline CASE BY CASE. Any case that passed and now
fails blocks, regardless of what the average did. A drop in the mean is reported
too, with a tolerance, because a broad shallow decline across every case is a
real signal that no individual case would catch.

**The baseline is only comparable if the suite has not changed.** Editing an
expected answer and re-running produces a number that is not measuring the same
thing, and the classic version of this is a case quietly "fixed" to match what
the model now says. The suite fingerprint is stored with the baseline and
checked; a mismatch is refused rather than compared.

Runs are stored as JSON so quality has a history. "Is it better than last month"
is the question that actually gets asked, and it cannot be answered by a system
that only knows the last two runs.
"""

from __future__ import annotations

import json
import statistics
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..core.errors import ValidationFailed
from ..core.money import Money
from .cases import GoldenCase, Suite
from .metrics import MetricResult

__all__ = ["CaseResult", "EvalRunner", "Gate", "GateDecision", "RunReport", "Trend"]

#: A case passes when every metric it declares clears this. Per-metric rather
#: than an average of metrics: an answer that is perfectly relevant and entirely
#: unfaithful should not average its way to a pass.
DEFAULT_THRESHOLD = 0.5


@dataclass
class CaseResult:
    case_id: str
    tags: tuple[str, ...]
    metrics: dict[str, MetricResult] = field(default_factory=dict)
    answer: str = ""
    cost: Money = field(default_factory=Money.zero)
    error: str = ""

    def passed(self, thresholds: dict[str, float] | None = None) -> bool:
        if self.error:
            return False
        limits = thresholds or {}
        return all(
            m.score >= limits.get(name, DEFAULT_THRESHOLD) for name, m in self.metrics.items()
        )

    @property
    def score(self) -> float:
        """Mean of this case's metrics. For trend reporting only, never gating."""
        return statistics.fmean([m.score for m in self.metrics.values()]) if self.metrics else 0.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "tags": list(self.tags),
            "metrics": {n: m.score for n, m in self.metrics.items()},
            "detail": {n: m.detail for n, m in self.metrics.items()},
            "cost_picos": self.cost.picos,
            "error": self.error,
        }


@dataclass
class RunReport:
    suite: str
    suite_fingerprint: str
    results: list[CaseResult] = field(default_factory=list)
    at: str = ""
    label: str = ""
    thresholds: dict[str, float] = field(default_factory=dict)

    @property
    def passed(self) -> list[CaseResult]:
        return [r for r in self.results if r.passed(self.thresholds)]

    @property
    def failed(self) -> list[CaseResult]:
        return [r for r in self.results if not r.passed(self.thresholds)]

    @property
    def pass_rate(self) -> float:
        return 0.0 if not self.results else len(self.passed) / len(self.results)

    @property
    def total_cost(self) -> Money:
        total = Money.zero()
        for result in self.results:
            total = total + result.cost
        return total

    def metric_mean(self, name: str) -> float:
        scores = [r.metrics[name].score for r in self.results if name in r.metrics]
        return statistics.fmean(scores) if scores else 0.0

    def by_tag(self) -> dict[str, float]:
        """Pass rate per tag — how a regression gets attributed to a cause."""
        tags: dict[str, list[bool]] = {}
        for result in self.results:
            for tag in result.tags:
                tags.setdefault(tag, []).append(result.passed(self.thresholds))
        return {tag: sum(v) / len(v) for tag, v in sorted(tags.items())}

    def as_dict(self) -> dict[str, Any]:
        return {
            "suite": self.suite,
            "suite_fingerprint": self.suite_fingerprint,
            "at": self.at,
            "label": self.label,
            "thresholds": self.thresholds,
            "pass_rate": self.pass_rate,
            "total_cost_picos": self.total_cost.picos,
            "results": [r.as_dict() for r in self.results],
        }

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.as_dict(), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> RunReport:
        payload = json.loads(Path(path).read_text())
        report = cls(
            suite=payload["suite"],
            suite_fingerprint=payload["suite_fingerprint"],
            at=payload.get("at", ""),
            label=payload.get("label", ""),
            thresholds=payload.get("thresholds", {}),
        )
        for row in payload["results"]:
            result = CaseResult(
                case_id=row["case_id"],
                tags=tuple(row.get("tags", [])),
                cost=Money.from_picos(int(row.get("cost_picos", 0))),
                error=row.get("error", ""),
            )
            detail = row.get("detail", {})
            result.metrics = {
                name: MetricResult(name, float(score), detail.get(name, ""))
                for name, score in row["metrics"].items()
            }
            report.results.append(result)
        return report

    def summary(self) -> str:
        lines = [
            f"{self.suite}: {len(self.passed)}/{len(self.results)} passed "
            f"({self.pass_rate:.0%}), cost {self.total_cost.format_adaptive()}"
        ]
        for tag, rate in self.by_tag().items():
            lines.append(f"  {tag:<24} {rate:.0%}")
        for result in self.failed[:10]:
            worst = min(result.metrics.values(), key=lambda m: m.score, default=None)
            reason = result.error or (
                f"{worst.name}={worst.score:.2f} ({worst.detail})" if worst else ""
            )
            lines.append(f"  FAIL {result.case_id}: {reason}")
        return "\n".join(lines)


#: A function that answers one case. Returns the answer text, the metrics it
#: produced, and what it cost.
Answerer = Callable[[GoldenCase], tuple[str, dict[str, MetricResult], Money]]


@dataclass
class EvalRunner:
    suite: Suite
    thresholds: dict[str, float] = field(default_factory=dict)

    def run(self, answerer: Answerer, label: str = "", now: str = "") -> RunReport:
        self.suite.validate()
        report = RunReport(
            suite=self.suite.name,
            suite_fingerprint=self.suite.fingerprint,
            at=now or datetime.now(UTC).isoformat(),
            label=label,
            thresholds=dict(self.thresholds),
        )
        for case in self.suite.cases:
            try:
                answer, metrics, cost = answerer(case)
                report.results.append(
                    CaseResult(case.id, case.tags, metrics, answer=answer, cost=cost)
                )
            except Exception as exc:
                # A crashing case is a FAILING case, not a missing one. Skipping
                # it silently raises the pass rate by shrinking the denominator,
                # which is the most flattering possible way to break.
                report.results.append(
                    CaseResult(case.id, case.tags, {}, error=f"{type(exc).__name__}: {exc}")
                )
        return report


@dataclass(frozen=True)
class GateDecision:
    allowed: bool
    reason: str
    newly_failing: tuple[str, ...] = ()
    newly_passing: tuple[str, ...] = ()
    mean_delta: float = 0.0

    def report(self) -> str:
        verdict = "PASS" if self.allowed else "BLOCK"
        lines = [f"{verdict}: {self.reason}"]
        if self.newly_failing:
            lines.append(f"  regressed: {', '.join(self.newly_failing)}")
        if self.newly_passing:
            lines.append(f"  improved:  {', '.join(self.newly_passing)}")
        lines.append(f"  mean delta: {self.mean_delta:+.3f}")
        return "\n".join(lines)


@dataclass
class Gate:
    """Compares a run to its baseline and decides whether to deploy."""

    #: How far the mean may fall before it blocks on its own. Small, because a
    #: broad shallow decline is real — but non-zero, because a gate that blocks
    #: on any movement at all blocks on noise and gets switched off.
    max_mean_drop: float = 0.02
    #: Cases allowed to regress. Zero by default and it should stay zero: this
    #: exists so a team can knowingly ship a trade-off, not so the gate can be
    #: quietly widened until it never fires.
    allowed_regressions: int = 0

    def decide(self, current: RunReport, baseline: RunReport | None) -> GateDecision:
        if baseline is None:
            return GateDecision(
                allowed=True,
                reason=f"no baseline; recording {current.pass_rate:.0%} as the first one",
            )

        if baseline.suite_fingerprint != current.suite_fingerprint:
            # Refusing is the point. Comparing against a baseline from a
            # different suite is how an edited expected answer turns into an
            # apparent improvement.
            raise ValidationFailed(
                "the suite changed since the baseline was recorded — these numbers are "
                "not comparable; re-record the baseline deliberately",
                baseline=baseline.suite_fingerprint,
                current=current.suite_fingerprint,
            )

        before = {r.case_id: r.passed(baseline.thresholds) for r in baseline.results}
        after = {r.case_id: r.passed(current.thresholds) for r in current.results}

        regressed = tuple(sorted(c for c, ok in after.items() if before.get(c, False) and not ok))
        improved = tuple(sorted(c for c, ok in after.items() if ok and not before.get(c, True)))

        current_mean = (
            statistics.fmean([r.score for r in current.results]) if current.results else 0.0
        )
        baseline_mean = (
            statistics.fmean([r.score for r in baseline.results]) if baseline.results else 0.0
        )
        delta = current_mean - baseline_mean

        if len(regressed) > self.allowed_regressions:
            return GateDecision(
                allowed=False,
                reason=f"{len(regressed)} case(s) that passed now fail",
                newly_failing=regressed,
                newly_passing=improved,
                mean_delta=delta,
            )

        if delta < -self.max_mean_drop:
            return GateDecision(
                allowed=False,
                reason=f"mean quality fell {abs(delta):.3f}, beyond the {self.max_mean_drop} tolerance",
                newly_failing=regressed,
                newly_passing=improved,
                mean_delta=delta,
            )

        return GateDecision(
            allowed=True,
            reason=f"no regressions; {len(improved)} improved",
            newly_passing=improved,
            mean_delta=delta,
        )


@dataclass
class Trend:
    """Quality over time. Answers 'is this better than last month'."""

    history: list[RunReport] = field(default_factory=list)

    @classmethod
    def load(cls, directory: str | Path) -> Trend:
        folder = Path(directory)
        if not folder.exists():
            return cls()
        reports = [RunReport.load(p) for p in sorted(folder.glob("*.json"))]
        return cls(sorted(reports, key=lambda r: r.at))

    def record(self, report: RunReport, directory: str | Path) -> None:
        stamp = (report.at or "run").replace(":", "-")
        report.save(Path(directory) / f"{stamp}-{report.label or 'run'}.json")
        self.history.append(report)

    def pass_rates(self) -> list[tuple[str, float]]:
        return [(r.at, r.pass_rate) for r in self.history]

    def chronically_failing(self, window: int = 5) -> list[str]:
        """Cases that have failed every recent run.

        The ones an aggregate hides. A case broken for a month contributes the
        same small constant to every mean and therefore never shows up as a
        regression again — it is only visible by asking this question.
        """
        recent = self.history[-window:]
        if not recent:
            return []
        always_failed: set[str] | None = None
        for report in recent:
            failing = {r.case_id for r in report.failed}
            always_failed = failing if always_failed is None else always_failed & failing
        return sorted(always_failed or set())

    def sparkline(self, name: str = "pass rate") -> str:
        blocks = "▁▂▃▄▅▆▇█"
        rates = [r.pass_rate for r in self.history]
        if not rates:
            return f"{name}: no history"
        marks = "".join(blocks[min(7, int(r * 8))] for r in rates)
        return f"{name}: {marks} ({rates[0]:.0%} → {rates[-1]:.0%} over {len(rates)} runs)"


def load_baseline(path: str | Path) -> RunReport | None:
    target = Path(path)
    return RunReport.load(target) if target.exists() else None


def check_suite(cases: Sequence[GoldenCase]) -> None:
    Suite(name="ad-hoc", cases=list(cases)).validate()
