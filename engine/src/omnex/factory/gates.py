"""The gate order, as a type rather than a comment in a README.

    idea → market → unit economics → architecture → simulation → evaluation
         → security → deploy → observe → scale or kill

Written down, this is a diagram everyone agrees with and nobody follows: the
interesting stage is architecture, so that is where work starts, and the
economics gate becomes a thing that happens after launch when somebody asks why
the margin is negative. Making it a type is what changes that —
`Pipeline.advance()` refuses a stage that skips one, so the shortcut has to be
taken deliberately and in writing.

`worth_it` runs at the head. That ordering is not a preference either: the seven
conditions cost nothing to answer and everything downstream is expensive, so a
loop that could never repay itself should be refused before anybody draws an
architecture for it.

## The StrEnum ordering trap, and why the comparisons are written out

`StrEnum` inherits `str`'s comparisons, so `Stage.DEPLOY < Stage.IDEA` is
already answerable — alphabetically, and wrongly. Worse, `@total_ordering` fills
in *nothing*, because it only supplies operators a class does not already have,
and this one inherits all four. A pipeline ordered by that silently permits
every backwards move whose stage name happens to sort earlier, and the check
still reads as though it works.

So the order is an explicit position table and all four comparisons are defined
against it. This is the invariant `CLAUDE.md` names, written out where it would
otherwise be silent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from ..core.errors import ValidationFailed
from ..harness import worth_it
from .spec import AgentSpec

__all__ = ["Gate", "Pipeline", "Stage"]


class Stage(StrEnum):
    """The order, and the only thing that decides it.

    Comparisons come from `_ORDER` below, never from the string value. See the
    module docstring: inherited string comparison answers confidently and wrongly.
    """

    IDEA = "idea"
    MARKET = "market"
    UNIT_ECONOMICS = "unit_economics"
    ARCHITECTURE = "architecture"
    SIMULATION = "simulation"
    EVALUATION = "evaluation"
    SECURITY = "security"
    DEPLOY = "deploy"
    OBSERVE = "observe"
    SCALE_OR_KILL = "scale_or_kill"

    @property
    def position(self) -> int:
        return _ORDER[self]

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Stage):
            return NotImplemented
        return self.position < other.position

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Stage):
            return NotImplemented
        return self.position <= other.position

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Stage):
            return NotImplemented
        return self.position > other.position

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Stage):
            return NotImplemented
        return self.position >= other.position


_ORDER: dict[Stage, int] = {stage: index for index, stage in enumerate(Stage)}


@dataclass(frozen=True)
class Gate:
    """One stage's verdict, with the reasons it failed rather than a boolean."""

    stage: Stage
    passed: bool
    reasons: tuple[str, ...] = ()
    note: str = ""

    def report(self) -> str:
        if self.passed:
            return f"{self.stage}: passed{f' — {self.note}' if self.note else ''}"
        return f"{self.stage}: REFUSED\n  " + "\n  ".join(self.reasons)


@dataclass
class Pipeline:
    """A spec walking the gate order, unable to skip and unable to go back.

    Holds the agreed fingerprints so every gate after agreement re-checks them.
    An agent whose spec was edited between the economics gate and the deploy gate
    was approved on numbers that no longer describe it, and nothing later in the
    order would notice.
    """

    spec: AgentSpec
    spec_fingerprint: str = ""
    contract_fingerprint: str = ""
    passed: list[Gate] = field(default_factory=list)

    @property
    def reached(self) -> Stage | None:
        return self.passed[-1].stage if self.passed else None

    def _next_expected(self) -> Stage:
        reached = self.reached
        if reached is None:
            return Stage.IDEA
        return list(Stage)[reached.position + 1] if reached is not Stage.SCALE_OR_KILL else reached

    def advance(self, gate: Gate) -> Pipeline:
        """Record a gate, refusing anything out of order or already failed.

        A refused gate stops the pipeline where it stands rather than being
        recorded and stepped over. The whole value of an order is that a later
        stage cannot start without an earlier one, and "recorded as failed and
        continued" is exactly the shape of not having an order at all.
        """
        expected = self._next_expected()
        if gate.stage is not expected:
            raise ValidationFailed(
                f"gate {gate.stage} out of order: {expected} has not been passed. "
                "Skipping is what turns this order into a diagram nobody follows",
                expected=str(expected),
                got=str(gate.stage),
                reached=str(self.reached) if self.reached else None,
            )
        if not gate.passed:
            raise ValidationFailed(
                f"gate {gate.stage} refused:\n  " + "\n  ".join(gate.reasons),
                stage=str(gate.stage),
                reasons=list(gate.reasons),
            )
        if self.spec_fingerprint:
            self.spec.assert_unchanged(self.spec_fingerprint)
        self.passed.append(gate)
        return self

    # ── the gates that can be decided from the spec alone ─────────────────
    # There are three. The rest — market, simulation, evaluation, security,
    # deploy, observe, scale-or-kill — take a `Gate` a person constructs with
    # evidence, and that asymmetry is deliberate: a spec cannot grade its own
    # market, and a factory that offered a `market()` helper would be inviting
    # exactly the self-assessment the frozen criteria exist to prevent.
    def idea(self, **conditions: bool) -> Pipeline:
        """`worth_it` at the head, with all seven answers required by keyword.

        No defaults, for the reason `worth_it.evaluate` gives: a default here is
        a quiet assumption about somebody else's budget, and the one that would
        default to True is exactly the one worth thinking about.
        """
        verdict = worth_it.evaluate(**conditions)
        return self.advance(
            Gate(
                stage=Stage.IDEA,
                passed=verdict.worth_it,
                reasons=tuple(f"{c}: {c.why}" for c in verdict.failed),
                note="all seven conditions hold",
            )
        )

    def unit_economics(self, revenue_per_run: Any) -> Pipeline:
        """Refuses a negative contribution margin at specification time.

        `router.is_losing_money()` answers this at runtime for a model call. The
        same question at agent level belongs here, before anything is built,
        because an agent whose spec cannot clear its own cost model will not
        start clearing it in production.
        """
        cost = self.spec.cost_model.total
        margin = revenue_per_run - cost
        losing = margin.picos <= 0
        return self.advance(
            Gate(
                stage=Stage.UNIT_ECONOMICS,
                passed=not losing,
                reasons=(
                    (
                        f"a run costs {cost} and earns {revenue_per_run}: "
                        f"contribution margin {margin}",
                    )
                    if losing
                    else ()
                ),
                note=f"margin {margin} per run",
            )
        )

    def architecture(self) -> Pipeline:
        """Every capability resolves, or the architecture is a diagram."""
        problems = self.spec.audit()
        return self.advance(
            Gate(
                stage=Stage.ARCHITECTURE,
                passed=not problems,
                reasons=tuple(problems),
                note=f"{len(self.spec.capabilities)} capabilities resolve",
            )
        )

    def report(self) -> str:
        lines = [f"{self.spec.name} — reached {self.reached or 'nothing'}"]
        lines.extend(f"  {gate.report()}" for gate in self.passed)
        remaining = [s for s in Stage if self.reached is None or s > self.reached]
        if remaining:
            lines.append(f"  not yet: {', '.join(str(s) for s in remaining)}")
        return "\n".join(lines)


def start(spec: AgentSpec) -> Pipeline:
    """Agree the spec and its contract, then hand back a pipeline bound to both."""
    contract, spec_fingerprint = spec.agree()
    return Pipeline(
        spec=spec,
        spec_fingerprint=spec_fingerprint,
        contract_fingerprint=contract.fingerprint,
    )
