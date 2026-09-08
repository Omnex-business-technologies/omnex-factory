"""The recommendation engine, and the ways a score turns into an authority.

The dangerous transition in the whole chain is the third one:

    REPOSITORY FACT → GRAPH STATE → HEURISTIC RANKING
        → RECOMMENDATION → POLICY CHECK → AUTHORIZATION → EXECUTION

A number that quietly becomes a decision is how an autonomous system ends up
doing something nobody authorised while every individual step looked reasonable.
Most of this file is about that arrow.

The rest carries the adversarial cases the hardening contract names that belong
here rather than in `test_claims.py`: an economic score overriding technical
truth, an action exceeding its policy, a manually modified graph, and duplicate
execution producing duplicate state.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ENGINE = REPO / "engine"
sys.path.insert(0, str(ENGINE / "scripts"))

import next_action  # noqa: E402
import policy  # noqa: E402
from claims import Claim, Evidence, Registry, Stance, Status  # noqa: E402
from policy import Action, Autonomy, Grant, SideEffect, authorise  # noqa: E402


def _registry() -> Registry:
    return Registry(
        claims=[
            Claim("C-A", "a symbol imports", "symbol", "test"),
            Claim("C-B", "the API accepts it", "external", "test", dependencies=("C-A",)),
        ],
        evidence=[
            Evidence("E-A", "C-A", Stance.SUPPORTS, "import", "2026-09-08", "imported"),
        ],
    )


# ── a score is never an authority ─────────────────────────────────────────
def test_the_output_says_it_is_a_recommendation_and_not_a_decision() -> None:
    """Prose, but load-bearing prose: it is the thing a reader sees first."""
    text = next_action.render(next_action.queue(_registry()), Grant())
    assert "RECOMMENDATION" in text
    assert "not a decision" in text
    assert "heuristic" in text


def test_the_top_ranked_action_can_still_be_refused_by_policy() -> None:
    """Ranking runs BEFORE authorisation and cannot substitute for it.

    If the highest score could not be refused, the score would be the decision.
    """
    top = next_action.queue(_registry())[0]
    verdict = authorise(top.action(), Grant(level=Autonomy.L0_OBSERVE))
    assert not verdict.allowed
    assert verdict.reasons


def test_every_recommendation_exposes_what_is_needed_to_overrule_it() -> None:
    """A recommendation you cannot argue with is an instruction."""
    item = next_action.queue(_registry())[0]
    for field_name in (
        "evidence",
        "assumptions",
        "blockers",
        "dependencies",
        "unlocks",
        "effort",
        "risk",
        "reversible",
        "autonomy",
        "effects",
        "authorization",
    ):
        assert hasattr(item, field_name), f"a recommendation must expose {field_name}"
    assert item.assumptions, "an unstated assumption cannot be challenged"


def test_nothing_here_executes_anything() -> None:
    """The module ranks and prints. Execution is somebody else's step."""
    source = (ENGINE / "scripts" / "next_action.py").read_text(encoding="utf-8")
    for forbidden in ("subprocess", "os.system", "shutil.rmtree", "open("):
        assert forbidden not in source, f"the recommender must not {forbidden}"


# ── economics may reorder; it may not rewrite ─────────────────────────────
def test_an_economic_score_cannot_change_a_claim_status() -> None:
    """The feedback loop this forbids:

        high expected revenue → high priority → the agent wants the result
        → evidence read optimistically → claim "validated" → economics reinforced

    Money changes PRIORITY. Money does not change REALITY.
    """
    registry = _registry()
    before = {c.claim_id: registry.status(c) for c in registry.claims}

    rich = [
        Action("C-B", "lucrative", frozenset({SideEffect.READ}), economic_weight=10_000.0),
        Action("C-A", "dull", frozenset({SideEffect.READ}), economic_weight=0.0),
    ]
    assert [a.action_id for a in policy.order(rich)] == ["C-B", "C-A"], "money reorders"

    after = {c.claim_id: registry.status(c) for c in registry.claims}
    assert before == after, "and money changed nothing about what is true"


def test_economic_weight_is_not_an_input_to_authorisation() -> None:
    """Otherwise a valuable enough action would authorise itself."""
    poor = Action("a", "x", frozenset({SideEffect.PUBLISH}), economic_weight=0.0)
    rich = Action("a", "x", frozenset({SideEffect.PUBLISH}), economic_weight=1e9)
    grant = Grant(level=Autonomy.L5_UNSUPERVISED)
    assert authorise(poor, grant).reasons == authorise(rich, grant).reasons


# ── policy ────────────────────────────────────────────────────────────────
def test_an_action_may_not_silently_escalate_its_own_level() -> None:
    """ "Run the tests" that grows a `twine upload` is a different blast radius
    wearing the same name. The required level comes from declared effects."""
    local = Action("a", "run tests", frozenset({SideEffect.LOCAL_EXECUTION}))
    grown = Action("a", "run tests", frozenset({SideEffect.LOCAL_EXECUTION, SideEffect.PUBLISH}))
    assert local.required_level < grown.required_level

    grant = Grant(level=Autonomy.L2_LOCAL)
    assert authorise(local, grant).allowed
    assert not authorise(grown, grant).allowed


@pytest.mark.parametrize(
    "effect",
    [
        SideEffect.PUBLISH,
        SideEffect.DEPLOY,
        SideEffect.CREDENTIAL,
        SideEffect.FINANCIAL,
        SideEffect.DESTRUCTIVE,
    ],
)
def test_the_five_irreversible_classes_are_never_cleared_by_a_level_alone(
    effect: SideEffect,
) -> None:
    """Even at L5. These need a durable authorization naming the class."""
    action = Action("a", "x", frozenset({effect}))
    verdict = authorise(action, Grant(level=Autonomy.L5_UNSUPERVISED, granted_by="RaveZona"))
    assert not verdict.allowed
    assert any("durable authorization" in r for r in verdict.reasons)

    named = Grant(
        level=Autonomy.L5_UNSUPERVISED, authorised=frozenset({effect}), granted_by="RaveZona"
    )
    assert authorise(action, named).allowed


def test_an_irreversible_action_needs_a_grant_that_names_somebody() -> None:
    action = Action("a", "x", frozenset({SideEffect.WRITE}), reversible=False)
    anonymous = Grant(level=Autonomy.L3_REPOSITORY)
    assert any("names nobody" in r for r in authorise(action, anonymous).reasons)


def test_every_refusal_is_reported_at_once() -> None:
    action = Action(
        "a", "x", frozenset({SideEffect.PUBLISH, SideEffect.FINANCIAL}), reversible=False
    )
    verdict = authorise(action, Grant(level=Autonomy.L0_OBSERVE))
    assert len(verdict.reasons) >= 3, verdict.reasons


def test_autonomy_levels_compare_as_numbers_not_as_strings() -> None:
    """`Stage` is the cautionary tale: a StrEnum inherits string comparison, so
    `DEPLOY < IDEA` is true and `@total_ordering` fills in nothing."""
    assert Autonomy.L0_OBSERVE < Autonomy.L5_UNSUPERVISED
    assert max(Autonomy) is Autonomy.L5_UNSUPERVISED


# ── the graph is derived ──────────────────────────────────────────────────
def test_the_queue_is_derived_from_the_registry_and_not_maintained() -> None:
    """A claim that becomes SUPPORTED leaves the queue without anybody editing
    a list — the property a hand-written task file can never have."""
    registry = _registry()
    assert any(r.claim_id == "C-B" for r in next_action.queue(registry))

    registry.evidence.append(
        Evidence("E-B", "C-B", Stance.SUPPORTS, "package_read", "2026-09-08", "read it", "x 1.0")
    )
    assert not any(r.claim_id == "C-B" for r in next_action.queue(registry))


def test_a_blocked_claim_names_what_blocks_it() -> None:
    registry = Registry(
        claims=[
            Claim("C-A", "base", "pipeline", "test"),
            Claim("C-B", "built on it", "external", "test", dependencies=("C-A",)),
        ],
        evidence=[],
    )
    built = next(r for r in next_action.queue(registry) if r.claim_id == "C-B")
    assert built.blockers == ("C-A is UNKNOWN",)
    assert built.dependencies == ("C-A",)


def test_running_it_twice_produces_the_same_queue() -> None:
    """Determinism: ties break on claim id, never on dict order."""
    registry = _registry()
    assert [r.claim_id for r in next_action.queue(registry)] == [
        r.claim_id for r in next_action.queue(registry)
    ]


def test_a_contradicted_claim_asks_for_a_person_not_another_measurement() -> None:
    """C-001 was disproved by running it, and the answer was to raise the floor.
    Re-running the import would not close it; only a person can."""
    registry = Registry(
        claims=[Claim("C-A", "it imports on 3.10", "symbol", "test")],
        evidence=[
            Evidence("E-A", "C-A", Stance.CONTRADICTS, "import", "2026-09-08", "ImportError")
        ],
    )
    item = next_action.queue(registry)[0]
    assert item.status is Status.CONTRADICTED
    assert "reject the claim with a person's name" in item.what
    assert "No machine may close it" in item.what


# ── against the real registry ─────────────────────────────────────────────
def test_the_real_queue_puts_nothing_settled_in_it() -> None:
    from claims import load

    registry = load()
    settled = {c.claim_id for c in registry.claims if registry.status(c) is Status.SUPPORTED}
    assert settled, "the registry has nothing supported, so this is vacuous"
    assert not settled & {r.claim_id for r in next_action.queue(registry)}
