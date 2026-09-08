"""What to do next, why, and everything needed to disagree with it.

    python scripts/next_action.py           # the ranked queue
    python scripts/next_action.py --top 1   # just the head

The node dossier answers "what do we know about this node". `state_map.py`
answers "where is execution". Neither answers the question an agent actually has
at the start of a session: **what should happen next, and what makes that the
right thing rather than the tidiest-looking thing.**

## A score is a heuristic. It is never an authority.

    REPOSITORY FACT → GRAPH STATE → HEURISTIC RANKING
        → RECOMMENDATION → POLICY CHECK → AUTHORIZATION → EXECUTION

Each arrow is a different kind of step and the dangerous one is the third, where
a number quietly becomes a decision. So the score is printed as a score, the
word RECOMMENDATION is in the output, and `authorise()` from `policy.py` runs
*after* ranking and can refuse the top-ranked item outright. Nothing here
executes anything.

Every recommendation carries what somebody needs to overrule it: the evidence
behind it, the assumptions in it, its blockers, its dependencies, what it would
unlock, effort, risk, reversibility, the autonomy level it needs, the external
effects it has and the authorization those require.

## The graph is derived, and there is no second copy

Candidates come from `claims.jsonl` and `evidence.jsonl` alone — one action per
claim that is not settled, with its blockers read from the dependency edges the
registry already has. Nothing here is hand-maintained, so nothing here can drift
from the registry. Two runs over an unchanged repository produce the same queue:
ties break on claim id, never on dict order.

## Why unresolved claims and not tasks

A task list is written by somebody, and then it is wrong the moment the
repository moves. A claim that is UNKNOWN or CONTRADICTED is a fact about the
repository right now, and "make this claim settled" is an action derived from
it. When the claim becomes SUPPORTED the action disappears without anybody
crossing it off — which is the property a hand-written queue can never have.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE / "scripts"))

from claims import VERIFIES, Claim, Registry, Status, load  # noqa: E402
from policy import NEEDS, Action, Autonomy, Grant, SideEffect, authorise, order  # noqa: E402

#: Verification method → what performing it actually touches. This is how an
#: action's blast radius is derived rather than guessed: settling an `external`
#: claim means going to the network, settling a `human` one means asking a
#: person and cannot be done by an agent at any autonomy level.
TOUCHES: dict[str, frozenset[SideEffect]] = {
    "import": frozenset({SideEffect.LOCAL_EXECUTION}),
    "test": frozenset({SideEffect.LOCAL_EXECUTION}),
    "mutation": frozenset({SideEffect.LOCAL_EXECUTION}),
    "script": frozenset({SideEffect.LOCAL_EXECUTION}),
    "workflow_read": frozenset({SideEffect.READ}),
    "ci_run": frozenset({SideEffect.GIT}),
    "package_read": frozenset({SideEffect.NETWORK}),
    "network_probe": frozenset({SideEffect.NETWORK}),
    "person": frozenset(),  # nothing an agent does; it is somebody's judgement
}

#: How much a status argues for acting. A contradiction is the most valuable
#: thing in the registry — something we believed is wrong and we know it — while
#: DISCOVERED means somebody wrote a lead down by a method that settles nothing.
URGENCY: dict[Status, int] = {
    Status.CONTRADICTED: 5,
    Status.STALE: 4,
    Status.UNKNOWN: 3,
    Status.PARTIALLY_SUPPORTED: 3,
    Status.DISCOVERED: 2,
    Status.SUPERSEDED: 2,
    Status.SUPPORTED: 0,
    Status.REJECTED: 0,
}


@dataclass(frozen=True)
class Recommendation:
    """One proposal, with everything needed to argue against it."""

    claim_id: str
    what: str
    why: str
    status: Status
    score: int
    evidence: tuple[str, ...]
    assumptions: tuple[str, ...]
    blockers: tuple[str, ...]
    dependencies: tuple[str, ...]
    unlocks: tuple[str, ...]
    effort: str
    risk: str
    reversible: bool
    autonomy: Autonomy
    effects: frozenset[SideEffect]
    authorization: tuple[str, ...]

    def action(self) -> Action:
        return Action(
            action_id=self.claim_id,
            what=self.what,
            effects=self.effects,
            economic_weight=float(self.score),
            reversible=self.reversible,
        )


def _method_for(claim: Claim) -> str:
    """The cheapest method that could settle this claim type. Stable, not random."""
    return sorted(VERIFIES.get(claim.type, frozenset()))[0] if VERIFIES.get(claim.type) else ""


def _what(claim: Claim, status: Status, method: str) -> str:
    """How this claim gets settled — which is not always "go and measure it".

    A CONTRADICTED claim has already been measured; that is why it is
    contradicted. C-001 ("citegate imports on 3.10") was disproved by running it
    and the response was to raise the floor, not to re-run the import. What it
    waits on now is a person saying "yes, this is false, and we have answered
    it" — which `apply_decisions.py`'s rule covers too: a machine may not close
    it, so it stays in the queue until somebody does.
    """
    if status is Status.CONTRADICTED:
        return (
            f"resolve {claim.claim_id}: evidence contradicts it. Either change the "
            f"repository so it becomes true, or reject the claim with a person's "
            f"name and a date. No machine may close it. — {claim.claim}"
        )
    return f"settle {claim.claim_id} by {method or 'no known method'}: {claim.claim}"


def recommend(registry: Registry) -> list[Recommendation]:
    """One recommendation per unsettled claim, derived and never authored."""
    statuses = {c.claim_id: registry.status(c) for c in registry.claims}
    dependents: dict[str, list[str]] = {c.claim_id: [] for c in registry.claims}
    for claim in registry.claims:
        for dependency in claim.dependencies:
            if dependency in dependents:
                dependents[dependency].append(claim.claim_id)

    out: list[Recommendation] = []
    for claim in sorted(registry.claims, key=lambda c: c.claim_id):
        status = statuses[claim.claim_id]
        if status in (Status.SUPPORTED, Status.REJECTED):
            continue

        method = _method_for(claim)
        effects = TOUCHES.get(method, frozenset())
        blockers = tuple(
            f"{d} is {statuses[d].value}"
            for d in claim.dependencies
            if statuses.get(d) is not Status.SUPPORTED
        )
        live = tuple(
            e.evidence_id
            for e in registry.for_claim(claim.claim_id)
            if e.evidence_id not in registry.superseded()
        )
        needs_person = method == "person" or not effects
        out.append(
            Recommendation(
                claim_id=claim.claim_id,
                what=_what(claim, status, method),
                why=f"{status.value} with {len(live)} live evidence; {len(dependents[claim.claim_id])} claim(s) rest on it",
                status=status,
                score=URGENCY[status] * 10 + len(dependents[claim.claim_id]) - len(blockers) * 2,
                evidence=live,
                assumptions=(
                    f"that {method or 'some method'} is the right way to settle a "
                    f"{claim.type} claim",
                    "that the claim as written is the claim worth settling",
                ),
                blockers=blockers,
                dependencies=claim.dependencies,
                unlocks=tuple(dependents[claim.claim_id]),
                effort="unmeasured",
                risk="low"
                if effects <= {SideEffect.READ, SideEffect.LOCAL_EXECUTION}
                else "raised",
                reversible=not (effects & {SideEffect.PUBLISH, SideEffect.DEPLOY}),
                autonomy=max((NEEDS[e] for e in effects), default=Autonomy.L0_OBSERVE),
                effects=effects,
                authorization=("a person: no agent action can settle this",)
                if needs_person
                else (),
            )
        )
    return out


def queue(registry: Registry) -> list[Recommendation]:
    """Ranked, with ties broken on claim id so two runs agree."""
    by_action = {r.claim_id: r for r in recommend(registry)}
    return [by_action[a.action_id] for a in order([r.action() for r in by_action.values()])]


def render(items: list[Recommendation], grant: Grant) -> str:
    lines = [
        "RECOMMENDATION — not a decision, and not an authorization.",
        "The score below is a heuristic over claim status and dependents. It ranks",
        "what to look at first; it does not establish that anything is true, and it",
        "cannot authorise anything. The policy check runs after it and may refuse.",
        "",
    ]
    for item in items:
        verdict = authorise(item.action(), grant)
        lines += [
            f"── {item.claim_id}  score {item.score}  [{item.status.value}]",
            f"   WHAT           {item.what}",
            f"   WHY            {item.why}",
            f"   EVIDENCE       {', '.join(item.evidence) or 'none on file'}",
            f"   BLOCKERS       {'; '.join(item.blockers) or 'none'}",
            f"   DEPENDENCIES   {', '.join(item.dependencies) or 'none'}",
            f"   UNLOCKS        {', '.join(item.unlocks) or 'nothing else on file'}",
            f"   EFFORT         {item.effort}",
            f"   RISK           {item.risk}",
            f"   REVERSIBLE     {item.reversible}",
            f"   AUTONOMY       {item.autonomy.name}",
            f"   EFFECTS        {', '.join(sorted(e.value for e in item.effects)) or 'none'}",
            f"   AUTHORIZATION  {'; '.join(item.authorization) or 'none beyond the grant'}",
            f"   POLICY         {'allowed' if verdict.allowed else 'REFUSED'}",
        ]
        lines += [f"                  - {reason}" for reason in verdict.reasons]
        lines.append("")
    for assumption in dict.fromkeys(a for item in items for a in item.assumptions):
        lines.append(f"   assumes: {assumption}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="What to do next, and why. A recommendation.")
    parser.add_argument("--top", type=int, default=0, help="show only the N highest ranked")
    parser.add_argument(
        "--level",
        default="L1_PROPOSE",
        choices=[a.name for a in Autonomy],
        help="the autonomy level to evaluate the policy check against",
    )
    args = parser.parse_args()

    registry = load()
    if not registry.claims:
        print("No claims on file, so there is nothing to derive a next action from.")
        print("An empty registry is not a finished one.")
        return 0

    items = queue(registry)
    if not items:
        print("Every claim on file is SUPPORTED or REJECTED. Nothing is outstanding")
        print("that this registry can see — which is a statement about the registry,")
        print("not about the repository.")
        return 0

    print(render(items[: args.top] if args.top else items, Grant(level=Autonomy[args.level])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
