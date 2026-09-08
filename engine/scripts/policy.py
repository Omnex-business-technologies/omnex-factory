"""What an action is allowed to touch, and what it may never decide for itself.

Autonomy is not "the agent can execute". The question that matters is *what
exactly* may it execute, under which conditions, and with what blast radius. So
every action declares the classes of effect it has, and `authorise()` answers
with every unmet requirement at once rather than the first.

## The escalation this prevents

An action that quietly widens its own class is the failure mode. "Run the test
suite" is LOCAL_EXECUTION; if it grows a `pip install` it became
PACKAGE_INSTALL, and if it grows a `twine upload` it became PUBLISH — three very
different blast radii wearing one name. `Action.effects` is declared, and
`authorise` compares it against the level actually granted. Nothing here can
raise its own level: `grant` comes from outside and is never computed from the
action asking.

## Five classes always need a person

`PUBLISH`, `DEPLOY`, `FINANCIAL`, `CREDENTIAL` and `DESTRUCTIVE` are irreversible
or outward-facing, and no autonomy level alone clears them — they need a durable
authorization naming that class. This is already how the repository behaves:
`packs/publish.py` refuses `--send` without an operator's endpoint,
`release.yml` refuses PyPI without a token and a reviewer, and
`apply_decisions.py` refuses a confirmation without a person's name.

## Money changes priority, never reality

`economic_weight` exists on an action and is used for **ordering only**. It is
deliberately not an input to authorisation and not an input to any claim's
status. The feedback loop this forbids is the dangerous one:

    high expected revenue → high priority → the agent wants the result
    → evidence read optimistically → claim "validated" → economics reinforced

`test_an_economic_score_cannot_change_a_claim_status` is the executable form of
that rule, because writing it in prose is what every system that failed this way
also did.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, StrEnum


class SideEffect(StrEnum):
    """What an action reaches. Declared, never inferred after the fact."""

    READ = "READ"
    WRITE = "WRITE"
    LOCAL_EXECUTION = "LOCAL_EXECUTION"
    NETWORK = "NETWORK"
    GIT = "GIT"
    PACKAGE_INSTALL = "PACKAGE_INSTALL"
    DEPLOY = "DEPLOY"
    PUBLISH = "PUBLISH"
    CREDENTIAL = "CREDENTIAL"
    FINANCIAL = "FINANCIAL"
    DESTRUCTIVE = "DESTRUCTIVE"


class Autonomy(IntEnum):
    """L0 proposes and does nothing; L5 acts without asking.

    An IntEnum on purpose — these are genuinely ordered and comparing them is
    the whole operation. `Stage` in `omnex.factory` is the cautionary tale: a
    StrEnum inherits string comparison, so `DEPLOY < IDEA` is true and
    `@total_ordering` fills in nothing.
    """

    L0_OBSERVE = 0
    L1_PROPOSE = 1
    L2_LOCAL = 2
    L3_REPOSITORY = 3
    L4_EXTERNAL = 4
    L5_UNSUPERVISED = 5


#: Effect → the lowest autonomy level that could ever cover it.
NEEDS: dict[SideEffect, Autonomy] = {
    SideEffect.READ: Autonomy.L0_OBSERVE,
    SideEffect.WRITE: Autonomy.L2_LOCAL,
    SideEffect.LOCAL_EXECUTION: Autonomy.L2_LOCAL,
    SideEffect.NETWORK: Autonomy.L2_LOCAL,
    SideEffect.PACKAGE_INSTALL: Autonomy.L2_LOCAL,
    SideEffect.GIT: Autonomy.L3_REPOSITORY,
    SideEffect.DEPLOY: Autonomy.L4_EXTERNAL,
    SideEffect.PUBLISH: Autonomy.L4_EXTERNAL,
    SideEffect.CREDENTIAL: Autonomy.L4_EXTERNAL,
    SideEffect.FINANCIAL: Autonomy.L4_EXTERNAL,
    SideEffect.DESTRUCTIVE: Autonomy.L5_UNSUPERVISED,
}

#: Effects no level alone clears. Each needs a durable authorization naming it,
#: because these are the ones that cannot be undone by a revert.
ALWAYS_ASKS = frozenset(
    {
        SideEffect.PUBLISH,
        SideEffect.DEPLOY,
        SideEffect.CREDENTIAL,
        SideEffect.FINANCIAL,
        SideEffect.DESTRUCTIVE,
    }
)


@dataclass(frozen=True)
class Action:
    """Something an agent proposes to do, with its blast radius declared."""

    action_id: str
    what: str
    effects: frozenset[SideEffect]
    #: Ordering only. Never an input to authorisation or to any claim's status.
    economic_weight: float = 0.0
    reversible: bool = True

    @property
    def required_level(self) -> Autonomy:
        return max((NEEDS[e] for e in self.effects), default=Autonomy.L0_OBSERVE)


@dataclass(frozen=True)
class Grant:
    """Authority handed to an agent from outside. Never computed from an action."""

    level: Autonomy = Autonomy.L0_OBSERVE
    #: Classes a person has durably authorised, e.g. {PUBLISH} after adding a
    #: token to an environment. Narrow on purpose.
    authorised: frozenset[SideEffect] = frozenset()
    granted_by: str = ""


@dataclass
class Decision:
    """Whether an action may proceed, and every reason it may not."""

    allowed: bool
    reasons: list[str] = field(default_factory=list)


def authorise(action: Action, grant: Grant) -> Decision:
    """Every reason this action may not run, collected rather than raised."""
    reasons: list[str] = []

    if grant.level < action.required_level:
        blocking = sorted(e.value for e in action.effects if NEEDS[e] > grant.level)
        reasons.append(
            f"{action.action_id} needs {action.required_level.name} for "
            f"{', '.join(blocking)}; the grant is {grant.level.name}"
        )

    for effect in sorted(action.effects & ALWAYS_ASKS, key=lambda e: e.value):
        if effect not in grant.authorised:
            reasons.append(
                f"{effect.value} is irreversible or outward-facing and is not "
                "covered by an autonomy level alone; it needs a durable "
                "authorization naming it"
            )

    if not action.reversible and not grant.granted_by:
        reasons.append(
            f"{action.action_id} is irreversible and the grant names nobody. "
            "An anonymous authorization is indistinguishable from none"
        )
    return Decision(allowed=not reasons, reasons=reasons)


def order(actions: list[Action]) -> list[Action]:
    """Rank by economic weight, then by id so the order is total and stable.

    This is the ONLY place economics is allowed to act. It changes which action
    is looked at first and nothing else — not a claim's status, not a
    verification result, not an authorisation. Money changes priority; money
    does not change reality.
    """
    return sorted(actions, key=lambda a: (-a.economic_weight, a.action_id))
