"""An agent, specified before it exists, and bound to that specification.

A spec is where an agent stops being a description and becomes something that
can be refused. Nine fields, and every one of them is required for a reason that
shows up later as a failure nobody could trace:

    role            what it is for, in one sentence somebody can disagree with
    capabilities    node names bound to symbols that IMPORT — not a wish list
    tools           what it may call, each priced
    memory_policy   what it remembers and for how long
    context_policy  what enters the prompt, and with what provenance
    paradigm        how it is orchestrated
    eval_suite      what grades it, by name, before it runs
    governance      who approves what, and what it may never do alone
    failure_modes   how it is expected to break
    cost_model      what one run costs, in exact pico-dollars

## Why capabilities must resolve

The whole chain that produced this module — 509 figures, 507 nodes, a ranking —
exists because a claim about capability is worthless unless something backs it.
`AgentSpec.audit()` resolves every capability symbol through
`core.symbols.resolve`, the same function `ontology_map.py` uses, so a spec
naming "Vector Search" without a symbol behind it is refused at specification
time rather than discovered at deploy time. A spec that reads correctly and
builds nothing is the expensive kind of document.

## Why failure modes are required rather than encouraged

An agent whose failure modes are unlisted has been imagined, not designed. The
field is required and must be non-empty, which is a low bar that nonetheless
stops the most common spec in the wild: a paragraph of what it will do, and
nothing about what happens when the tool times out.

## Why the spec is a contract

`AgentSpec.contract()` derives a `harness.Contract` from the spec — one
criterion per field, each with a real check — and the agreed contract is
fingerprinted. Editing a spec after agreement and carrying on under the old
approval is the failure P15 prevents for human approvals, and it is prevented
the same way here: the approval binds to what was approved.

Three criteria are **frozen**, chosen because each is a thing an optimiser under
pressure would relax first, and each has already been paid for somewhere in this
repository:

    untrusted_tool_results   `omnex.mcp` exists because a tool result reaching a
                             prompt as a bare string is the whole injection
                             surface.
    metered_runs             an unpriced run reports €0.00 while money moves.
    graded_before_shipped    "unchecked" is never "passed".
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import StrEnum

from ..core.errors import ValidationFailed
from ..core.money import Money
from ..core.symbols import resolve
from ..harness.contract import Contract, Criterion

__all__ = ["AgentSpec", "Capability", "CostModel", "Paradigm", "Tool"]


class Paradigm(StrEnum):
    """How the agent is orchestrated. Named, because the choice has consequences."""

    SINGLE = "single"
    REACT = "react"
    PLANNER_EXECUTOR = "planner_executor"
    SUPERVISOR_CREW = "supervisor_crew"
    GRAPH = "graph"


@dataclass(frozen=True)
class Capability:
    """One node this agent claims, bound to a symbol that must import."""

    node: str
    symbol: str

    def __post_init__(self) -> None:
        if not self.node.strip() or not self.symbol.strip():
            raise ValidationFailed("a capability needs both a node name and a symbol")


@dataclass(frozen=True)
class Tool:
    """One callable surface, priced. An unpriced tool cannot be specified.

    Same rule as `mcp.McpClient`, for the same reason: a tool costed at zero is
    not missing a number, it is reporting a wrong one, and every unit-economics
    gate downstream inherits the error without noticing.
    """

    name: str
    surface: str
    price_per_call: Money

    def __post_init__(self) -> None:
        if self.price_per_call.picos <= 0:
            raise ValidationFailed(
                f"tool {self.name!r} has no price; a run built from free tools "
                "reports a margin it does not have",
                tool=self.name,
            )


@dataclass(frozen=True)
class CostModel:
    """What one run costs, decomposed enough to act on.

    Kept separate from a single number because the two terms behave differently:
    a chatty agent is dominated by model spend and a tool-heavy one by call fees,
    and one figure hides whichever is actually the bill.
    """

    model_per_run: Money
    tools_per_run: Money
    infra_per_run: Money = field(default_factory=Money.zero)
    human_review_per_run: Money = field(default_factory=Money.zero)

    @property
    def total(self) -> Money:
        return (
            self.model_per_run + self.tools_per_run + self.infra_per_run + self.human_review_per_run
        )

    def __post_init__(self) -> None:
        if self.total.picos <= 0:
            raise ValidationFailed(
                "a run that costs nothing has not been costed; every downstream "
                "margin is then arithmetic on a placeholder"
            )


@dataclass(frozen=True)
class AgentSpec:
    """The whole specification, fingerprinted and refusable."""

    name: str
    role: str
    capabilities: tuple[Capability, ...]
    tools: tuple[Tool, ...]
    memory_policy: str
    context_policy: str
    paradigm: Paradigm
    eval_suite: str
    governance: str
    failure_modes: tuple[str, ...]
    cost_model: CostModel

    @property
    def fingerprint(self) -> str:
        """Covers every field. A spec edited after agreement is a different spec."""
        body = "\n".join(
            [
                self.name,
                self.role,
                *(f"{c.node}={c.symbol}" for c in sorted(self.capabilities, key=lambda c: c.node)),
                *(
                    f"{t.name}@{t.surface}:{t.price_per_call.picos}"
                    for t in sorted(self.tools, key=lambda t: t.name)
                ),
                self.memory_policy,
                self.context_policy,
                str(self.paradigm),
                self.eval_suite,
                self.governance,
                *sorted(self.failure_modes),
                str(self.cost_model.total.picos),
            ]
        )
        return hashlib.sha256(body.encode()).hexdigest()[:16]

    def audit(self) -> list[str]:
        """Every problem at once. Refusing one at a time teaches somebody to give up."""
        problems: list[str] = []
        if not self.name.strip():
            problems.append("the spec has no name")
        if len(self.role.split()) < 3:
            problems.append("the role is not a sentence anybody can disagree with")
        if not self.capabilities:
            problems.append("no capabilities: this is a description, not an agent")
        if not self.failure_modes:
            problems.append(
                "no failure modes named — an agent whose failures are unlisted has "
                "been imagined rather than designed"
            )
        if not self.eval_suite.strip():
            problems.append("no eval suite named, so 'it works' is unfalsifiable")
        if not self.governance.strip():
            problems.append("no governance: nobody has said what it may not do alone")

        for capability in self.capabilities:
            reason = resolve(capability.symbol)
            if reason is not None:
                problems.append(
                    f"capability {capability.node!r} claims {capability.symbol} — {reason}"
                )

        priced = {tool.name for tool in self.tools}
        if len(priced) != len(self.tools):
            problems.append("two tools share a name, so one of their prices is unreachable")
        return problems

    def raise_if_incomplete(self) -> None:
        problems = self.audit()
        if problems:
            raise ValidationFailed(
                "the spec is not complete:\n  " + "\n  ".join(problems),
                spec=self.name,
                problems=problems,
            )

    def contract(self) -> Contract:
        """Derive the definition of done from the spec itself.

        Derived rather than written alongside, because a contract maintained
        separately from the spec it describes drifts from it, and the drift is
        only discovered when something is graded against the wrong one.
        """
        criteria = [
            Criterion(
                key="capabilities_resolve",
                statement="every claimed capability names a symbol that imports",
                check="AgentSpec.audit() returns no unresolved capability",
            ),
            Criterion(
                key="untrusted_tool_results",
                statement="tool output enters a prompt as untrusted content",
                check="every tool result is a guard.Segment with Provenance.UNTRUSTED",
                frozen=True,
            ),
            Criterion(
                key="metered_runs",
                statement="every run records exact pico-dollar cost",
                check="obs.CostLedger has an event for the run, cost > 0",
                frozen=True,
            ),
            Criterion(
                key="graded_before_shipped",
                statement=f"the {self.eval_suite} suite gates the agent",
                check=f"evals regression gate passes on {self.eval_suite}",
                frozen=True,
            ),
            Criterion(
                key="failure_modes_handled",
                statement=f"{len(self.failure_modes)} named failure modes each have a path",
                check="one test per named failure mode",
            ),
            Criterion(
                key="governed",
                statement=self.governance,
                check="hitl approval is bound to a request fingerprint",
            ),
        ]
        return Contract(criteria=tuple(criteria))

    def agree(self) -> tuple[Contract, str]:
        """Complete the spec, agree its contract, and return both fingerprints.

        Returned together because they are checked together: the spec
        fingerprint says the specification did not move, and the contract
        fingerprint says the definition of done did not. Either one alone can be
        satisfied while the other has changed underneath it.
        """
        self.raise_if_incomplete()
        return self.contract().agree(minimum_criteria=6), self.fingerprint

    def assert_unchanged(self, fingerprint: str) -> None:
        if self.fingerprint != fingerprint:
            raise ValidationFailed(
                "the spec changed after it was agreed; work must be judged against "
                "the spec it was approved under",
                expected=fingerprint,
                actual=self.fingerprint,
            )
