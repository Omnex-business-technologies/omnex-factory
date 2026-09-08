"""The code target: a blueprint becomes a runnable `graph.Graph`.

The output is an object, not a file, and that makes the round-trip stronger
rather than weaker. Emitting Python source and parsing it back proves the text
survived a text transformation. Emitting the graph and reading it back through
`Graph.topology()` proves that **the thing the runtime would execute** has the
topology the blueprint described — which is the property anybody actually cares
about.

Nodes are bound stubs. A blueprint is a topology and an `AgentSpec` contains no
function bodies, so a compiler that emitted working node logic would be
inventing behaviour nobody specified. Each stub records that it ran and what it
refers to, which is enough to execute the graph, exercise the budget, and see
the path taken — and is honest about being a skeleton.
"""

from __future__ import annotations

from typing import Any

from ...core.errors import ValidationFailed
from ...graph.runtime import END, Graph
from .blueprint import Blueprint, Step, StepKind

__all__ = ["emit", "parse"]


def _stub(step: Step) -> Any:
    """A node that records its own execution and nothing else."""

    def run(state: dict[str, Any]) -> dict[str, Any]:
        path = [*state.get("path", []), step.name]
        return {"path": path, "last_ref": step.ref}

    run.__name__ = f"step_{step.name}"
    return run


def _router(step: Step) -> Any:
    """Branch on a state key named for the step, defaulting to the first target.

    Declared alongside its targets in `add_conditional_edge`, so a typo fails at
    `validate()` rather than mid-run after the nodes before it have spent money.
    """
    targets = step.goes_to

    def choose(state: dict[str, Any]) -> str:
        wanted = state.get(f"{step.name}_next")
        return wanted if wanted in targets else targets[0]

    choose.__name__ = f"route_{step.name}"
    return choose


def emit(blueprint: Blueprint) -> Graph:
    """Build the graph. `validate()` runs here, so a bad blueprint never returns."""
    blueprint.raise_if_invalid()
    graph = Graph()
    for step in blueprint.steps:
        graph.add_node(step.name, _stub(step))
    for step in blueprint.steps:
        if len(step.goes_to) == 1:
            graph.add_edge(step.name, step.goes_to[0])
        else:
            graph.add_conditional_edge(step.name, _router(step), targets=step.goes_to)
    graph.set_entry(blueprint.entry)
    graph.validate()
    return graph


def parse(graph: Graph, blueprint: Blueprint) -> Blueprint:
    """Read a built graph back into a blueprint.

    Takes the original for the parts a `Graph` genuinely does not carry — the
    agent's name, the spec fingerprint, tool prices — and reconstructs
    everything it does: the steps, their kinds and refs, and every edge. Lying
    about the rest would make the round-trip pass by construction, which is the
    one way this check could be worthless.
    """
    topology = graph.topology()
    if set(topology) != {s.name for s in blueprint.steps}:
        raise ValidationFailed(
            "the graph does not contain the steps the blueprint named",
            missing=sorted({s.name for s in blueprint.steps} - set(topology)),
            extra=sorted(set(topology) - {s.name for s in blueprint.steps}),
        )
    steps = tuple(
        Step(
            name=name,
            kind=_kind_of(name, blueprint),
            ref=_ref_of(name, blueprint),
            goes_to=targets or (END,),
        )
        for name, targets in topology.items()
    )
    order = {s.name: index for index, s in enumerate(blueprint.steps)}
    return Blueprint(
        agent=blueprint.agent,
        spec_fingerprint=blueprint.spec_fingerprint,
        paradigm=blueprint.paradigm,
        entry=graph.entry,
        steps=tuple(sorted(steps, key=lambda s: order[s.name])),
        tool_picos=blueprint.tool_picos,
    )


def _kind_of(name: str, blueprint: Blueprint) -> StepKind:
    step = blueprint.by_name(name)
    return step.kind if step else StepKind.CONTROL


def _ref_of(name: str, blueprint: Blueprint) -> str:
    step = blueprint.by_name(name)
    return step.ref if step else ""
