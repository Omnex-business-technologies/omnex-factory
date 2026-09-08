"""The target-neutral shape a spec compiles into, before any target sees it.

Three compilers emit from this and read back into it. Putting a neutral form in
the middle is not architecture for its own sake: without it, "does the n8n
workflow do the same thing as the code" is a question nobody can answer, because
the two artifacts have no common vocabulary to be compared in. With it, the
question is `parse(emit(bp)) == bp`, which a test can decide.

## What a blueprint is, and what it deliberately is not

It is a **topology**: named steps, what each one refers to, and where control can
go next. It is not an implementation. An `AgentSpec` names capabilities and
priced tools; it does not contain the body of a function, and a compiler that
invented one would be generating configuration nobody supplied and stating it as
though somebody had.

So the code target emits a runnable `graph.Graph` whose nodes are bound stubs,
the MCP target emits a server manifest, and the n8n target emits a workflow whose
nodes are placeholders someone hosts and fills in. Each is a skeleton that is
honest about being one.

## The paradigm decides the shape, and it is derived

`REACT` is think → act → observe → back to think or out. `PLANNER_EXECUTOR` is
plan → execute → review. The shape comes from the spec's `paradigm` field rather
than from an argument, so two agents declared with the same paradigm compile to
the same skeleton and a difference in the output means a difference in the spec.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum

from ...core.errors import ValidationFailed
from ...graph.runtime import END
from ..spec import AgentSpec, Paradigm

__all__ = ["Blueprint", "Step", "StepKind", "plan"]


class StepKind(StrEnum):
    """What a step stands for. Control steps carry no reference by design."""

    CONTROL = "control"
    CAPABILITY = "capability"
    TOOL = "tool"


@dataclass(frozen=True)
class Step:
    """One node in the topology and every place control may go from it."""

    name: str
    kind: StepKind
    #: A dotted symbol for a capability, a tool name for a tool, empty for control.
    ref: str
    #: Targets. More than one means a branch; `END` is a legal target.
    goes_to: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name:
            raise ValidationFailed("a step needs a name")
        if not self.goes_to:
            raise ValidationFailed(
                f"step {self.name!r} goes nowhere — a node with no outgoing edge is a "
                "graph that stops without saying so"
            )
        if self.kind is StepKind.CONTROL and self.ref:
            raise ValidationFailed(f"control step {self.name!r} carries a reference")
        if self.kind is not StepKind.CONTROL and not self.ref:
            raise ValidationFailed(f"{self.kind} step {self.name!r} refers to nothing")

    def digest(self) -> str:
        return f"{self.name}|{self.kind}|{self.ref}|{','.join(self.goes_to)}"


@dataclass(frozen=True)
class Blueprint:
    """A whole agent as topology, comparable across targets."""

    agent: str
    spec_fingerprint: str
    paradigm: str
    entry: str
    steps: tuple[Step, ...]
    #: Tool name to price in pico-dollars. Integers, not `Money`, because this
    #: crosses a wire in two of the three targets and a float there is the
    #: currency bug this package refuses everywhere else.
    tool_picos: tuple[tuple[str, int], ...]

    @property
    def digest(self) -> str:
        body = "\n".join(
            [
                self.agent,
                self.spec_fingerprint,
                self.paradigm,
                self.entry,
                *(s.digest() for s in self.steps),
                *(f"{name}={picos}" for name, picos in self.tool_picos),
            ]
        )
        return hashlib.sha256(body.encode()).hexdigest()[:16]

    def by_name(self, name: str) -> Step | None:
        return next((s for s in self.steps if s.name == name), None)

    def validate(self) -> list[str]:
        """Every problem at once: dangling targets, no entry, unreachable steps."""
        problems: list[str] = []
        names = {s.name for s in self.steps}
        if len(names) != len(self.steps):
            problems.append("two steps share a name")
        if self.entry not in names:
            problems.append(f"entry {self.entry!r} is not a step")
        for step in self.steps:
            for target in step.goes_to:
                if target != END and target not in names:
                    problems.append(f"{step.name} goes to {target!r}, which does not exist")

        reachable = {self.entry} if self.entry in names else set()
        frontier = list(reachable)
        while frontier:
            current = self.by_name(frontier.pop())
            if current is None:
                continue
            for target in current.goes_to:
                if target != END and target not in reachable:
                    reachable.add(target)
                    frontier.append(target)
        for orphan in sorted(names - reachable):
            problems.append(f"{orphan} is unreachable from {self.entry!r}")
        return problems

    def raise_if_invalid(self) -> None:
        problems = self.validate()
        if problems:
            raise ValidationFailed(
                "the blueprint will not run:\n  " + "\n  ".join(problems),
                agent=self.agent,
                problems=problems,
            )


def _react(tools: tuple[str, ...]) -> tuple[tuple[Step, ...], str]:
    act_targets = tuple(f"call_{t}" for t in tools) or ("observe",)
    steps = [
        Step("think", StepKind.CONTROL, "", ("act",)),
        Step("act", StepKind.CONTROL, "", act_targets),
        *(Step(f"call_{t}", StepKind.TOOL, t, ("observe",)) for t in tools),
        Step("observe", StepKind.CONTROL, "", ("think", END)),
    ]
    return tuple(steps), "think"


def _planner_executor(capabilities: tuple[str, ...]) -> tuple[tuple[Step, ...], str]:
    steps = [
        Step("plan", StepKind.CONTROL, "", (f"use_{_slug(capabilities[0])}",)),
        *(
            Step(
                f"use_{_slug(symbol)}",
                StepKind.CAPABILITY,
                symbol,
                (
                    (f"use_{_slug(capabilities[index + 1])}",)
                    if index + 1 < len(capabilities)
                    else ("review",)
                ),
            )
            for index, symbol in enumerate(capabilities)
        ),
        Step("review", StepKind.CONTROL, "", (END,)),
    ]
    return tuple(steps), "plan"


def _supervisor_crew(capabilities: tuple[str, ...]) -> tuple[tuple[Step, ...], str]:
    workers = tuple(f"worker_{_slug(s)}" for s in capabilities)
    steps = [
        Step("supervise", StepKind.CONTROL, "", workers),
        *(
            Step(f"worker_{_slug(symbol)}", StepKind.CAPABILITY, symbol, ("merge",))
            for symbol in capabilities
        ),
        Step("merge", StepKind.CONTROL, "", (END,)),
    ]
    return tuple(steps), "supervise"


def _chain(capabilities: tuple[str, ...]) -> tuple[tuple[Step, ...], str]:
    steps = tuple(
        Step(
            f"use_{_slug(symbol)}",
            StepKind.CAPABILITY,
            symbol,
            (
                (f"use_{_slug(capabilities[index + 1])}",)
                if index + 1 < len(capabilities)
                else (END,)
            ),
        )
        for index, symbol in enumerate(capabilities)
    )
    return steps, steps[0].name


def _slug(symbol: str) -> str:
    return symbol.rpartition(".")[2].lower() or symbol.lower()


def plan(spec: AgentSpec) -> Blueprint:
    """Derive the topology from the spec. Same paradigm, same skeleton.

    Refuses an incomplete spec first: compiling one produces an artifact that
    looks deployable and refers to capabilities nothing backs, which is a worse
    outcome than not compiling.
    """
    spec.raise_if_incomplete()
    capabilities = tuple(c.symbol for c in spec.capabilities)
    tools = tuple(t.name for t in spec.tools)

    if spec.paradigm is Paradigm.REACT:
        steps, entry = _react(tools)
    elif spec.paradigm is Paradigm.PLANNER_EXECUTOR:
        steps, entry = _planner_executor(capabilities)
    elif spec.paradigm is Paradigm.SUPERVISOR_CREW:
        steps, entry = _supervisor_crew(capabilities)
    else:  # SINGLE and GRAPH are both a chain; SINGLE simply has one link.
        steps, entry = _chain(capabilities)

    blueprint = Blueprint(
        agent=spec.name,
        spec_fingerprint=spec.fingerprint,
        paradigm=str(spec.paradigm),
        entry=entry,
        steps=steps,
        tool_picos=tuple(sorted((t.name, t.price_per_call.picos) for t in spec.tools)),
    )
    blueprint.raise_if_invalid()
    return blueprint
