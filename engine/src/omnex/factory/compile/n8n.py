"""The n8n target: a workflow JSON somebody else can host. Branch XI's named gap.

`omnex.pipeline` already runs jobs — queues, workers, webhooks with signature
verification, idempotency, retries, dead letters. What did not exist was emitting
that shape as something a person can import into an n8n instance they own. This
is that, and it is the only one of the three targets that leaves the process.

## What is honestly in the output, and what is not

A blueprint is a topology; an `AgentSpec` names a tool and its price and says
nothing about which HTTP endpoint it is, what credential it uses, or what body it
posts. A compiler that invented those would be writing configuration nobody
supplied and shipping it as though somebody had — and the failure lands on
whoever imports the workflow and watches it call the wrong host with the wrong
key.

So the configuration is not inferred, it is **supplied**, as a catalogue in
`bindings.py` that a person writes and a person confirms. A step whose `ref` has
a binding emits as that node type with those parameters. A step with no binding
emits as `n8n-nodes-base.noOp` carrying the reference it stands for, exactly as
before — a wiring diagram that imports, lays out correctly, and does nothing
until somebody fills it in.

`notes` on every node says which of the two it is, inside the file, where whoever
opens it will actually read it. A binding nobody has confirmed by importing says
that too, because "written down" and "seen to work" are different claims and the
gap between them is where an unattended workflow fails.

## No secret leaves here

The emitted JSON is committed and shared. Credentials are referenced by their
name in the operator's own n8n instance, and the whole document is scanned before
it is returned — not only the catalogue on load, because a secret can arrive
through a parameter path the catalogue never saw.

## Positions

n8n lays nodes out on a canvas and a workflow with every node at the origin is
unreadable. Positions are derived from distance-from-entry so the diagram opens
looking like the graph rather than like a pile, and they are recomputed on parse
rather than trusted, so a hand-moved node does not read back as a topology
change.
"""

from __future__ import annotations

import json
from typing import Any

from ...core.errors import ValidationFailed
from ...graph.runtime import END
from .bindings import EMPTY, Catalogue, looks_like_a_secret
from .blueprint import Blueprint, Step, StepKind

__all__ = ["emit", "parse"]

NOOP = "n8n-nodes-base.noOp"
COLUMN = 260
ROW = 140

PLACEHOLDER_NOTE = (
    "Placeholder. This node's behaviour was not specified — the agent spec names "
    "the capability and its price, not the endpoint, credential or payload. Fill "
    "it in before running."
)

UNCONFIRMED_NOTE = (
    "Bound from the catalogue but NOT confirmed by an import. The node type and "
    "parameters were written down, not observed working. Import once, then record "
    "confirmed_by and confirmed_at against this binding."
)

CONFIRMED_NOTE = "Bound from the catalogue and confirmed by an import."


def _depths(blueprint: Blueprint) -> dict[str, int]:
    """Distance from the entry, breadth-first, so the canvas reads left to right."""
    depth = {blueprint.entry: 0}
    frontier = [blueprint.entry]
    while frontier:
        name = frontier.pop(0)
        step = blueprint.by_name(name)
        if step is None:
            continue
        for target in step.goes_to:
            if target != END and target not in depth:
                depth[target] = depth[name] + 1
                frontier.append(target)
    for step in blueprint.steps:
        depth.setdefault(step.name, 0)
    return depth


def _positions(blueprint: Blueprint) -> dict[str, list[int]]:
    depth = _depths(blueprint)
    rows: dict[int, int] = {}
    out: dict[str, list[int]] = {}
    for step in blueprint.steps:
        column = depth[step.name]
        row = rows.get(column, 0)
        rows[column] = row + 1
        out[step.name] = [column * COLUMN, row * ROW]
    return out


def emit(
    blueprint: Blueprint,
    catalogue: Catalogue | None = None,
    *,
    require_confirmed: bool = False,
) -> str:
    """Emit a workflow, binding whatever the catalogue can bind.

    `require_confirmed` is for a deploy path rather than a build: an unconfirmed
    binding is fine to import by hand and read, and is not fine to schedule
    against a customer's money. Refuses naming every unconfirmed ref at once,
    because fixing them one import at a time is the slow version of the same
    work.
    """
    blueprint.raise_if_invalid()
    catalogue = catalogue or EMPTY
    prices = dict(blueprint.tool_picos)
    positions = _positions(blueprint)

    if require_confirmed:
        unconfirmed = sorted(
            {s.ref for s in blueprint.steps if s.ref and not catalogue.is_confirmed(s.ref)}
        )
        if unconfirmed:
            raise ValidationFailed(
                "these references have no binding confirmed by an import, and a "
                "workflow that runs unattended may not be built on a shape nobody "
                "has seen work:\n  " + "\n  ".join(unconfirmed),
                agent=blueprint.agent,
                unconfirmed=unconfirmed,
            )

    nodes: list[dict[str, Any]] = []
    for step in blueprint.steps:
        parameters: dict[str, Any] = {"omnexKind": str(step.kind), "omnexRef": step.ref}
        if step.kind is StepKind.TOOL:
            parameters["omnexPricePicos"] = prices.get(step.ref, 0)

        binding = catalogue.get(step.ref) if step.ref else None
        node: dict[str, Any] = {
            "name": step.name,
            "type": NOOP,
            "typeVersion": 1,
            "position": positions[step.name],
            "parameters": parameters,
            "notes": PLACEHOLDER_NOTE,
        }
        if binding is not None:
            node_type = catalogue.node_type_of(binding)
            node["type"] = node_type.type
            node["typeVersion"] = node_type.type_version
            # The omnex keys are written LAST so a binding cannot overwrite the
            # reference the parser reads back. A catalogue entry that shadowed
            # `omnexRef` would round-trip as a different topology while the
            # workflow still imported, which is the failure this package's whole
            # round-trip property exists to make impossible.
            node["parameters"] = {**binding.parameters, **parameters}
            if binding.credentials:
                node["credentials"] = {
                    kind: {"name": name} for kind, name in sorted(binding.credentials.items())
                }
            node["notes"] = CONFIRMED_NOTE if catalogue.is_confirmed(step.ref) else UNCONFIRMED_NOTE
        nodes.append(node)

    connections: dict[str, Any] = {}
    for step in blueprint.steps:
        outgoing = [
            {"node": target, "type": "main", "index": 0} for target in step.goes_to if target != END
        ]
        # A step whose only target is END still needs its entry in the map, or
        # reading the workflow back loses the edge and the round trip passes by
        # having forgotten the same thing twice.
        connections[step.name] = {"main": [outgoing]}

    payload = {
        "name": blueprint.agent,
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1"},
        "meta": {
            "omnexSpec": blueprint.spec_fingerprint,
            "omnexParadigm": blueprint.paradigm,
            "omnexEntry": blueprint.entry,
            "omnexEnds": sorted(s.name for s in blueprint.steps if END in s.goes_to),
            "omnexOrder": [s.name for s in blueprint.steps],
            # Prices belong to the AGENT, not to whichever node happens to
            # reference a tool. Reading them back off the tool nodes lost every
            # price in four of the five paradigms, where tools are resources the
            # steps use rather than steps of their own — and the workflow still
            # imported, so nothing said so.
            "omnexToolPicos": [[name, picos] for name, picos in blueprint.tool_picos],
            "omnexBound": sorted(
                {s.ref for s in blueprint.steps if s.ref and catalogue.get(s.ref) is not None}
            ),
        },
    }
    document = json.dumps(payload, ensure_ascii=False, indent=2)

    # Scanned here rather than only on catalogue load. The two are different
    # failures: a key typed into the catalogue, and a key that reached a node
    # through some parameter path the catalogue never held. This file is
    # committed and shared, so the second one is an incident either way.
    shape = looks_like_a_secret(document)
    if shape is not None:
        raise ValidationFailed(
            f"the emitted workflow contains what looks like {shape}. Credentials "
            "are referenced by their name in the operator's n8n instance; a "
            "workflow JSON with a key in it is an incident, not a configuration",
            agent=blueprint.agent,
            shape=shape,
        )
    return document


def parse(payload: str) -> Blueprint:
    raw: dict[str, Any] = json.loads(payload)
    meta = raw.get("meta") or {}
    if "omnexEntry" not in meta:
        raise ValidationFailed(
            "this workflow was not emitted from a blueprint; without the entry "
            "node and step order there is nothing to compare against"
        )

    connections = raw.get("connections") or {}
    ends = set(meta.get("omnexEnds") or [])
    by_name = {node["name"]: node for node in raw.get("nodes") or []}

    steps: list[Step] = []
    for name in meta.get("omnexOrder") or list(by_name):
        node = by_name[name]
        parameters = node.get("parameters") or {}
        outgoing = tuple(
            entry["node"]
            for group in (connections.get(name, {}).get("main") or [])
            for entry in group
        )
        if name in ends:
            outgoing = (*outgoing, END)
        steps.append(
            Step(
                name=name,
                kind=StepKind(parameters.get("omnexKind", StepKind.CONTROL)),
                ref=str(parameters.get("omnexRef", "")),
                goes_to=outgoing,
            )
        )

    tools: list[tuple[str, int]] = []
    for entry in meta.get("omnexToolPicos") or []:
        name, picos = entry
        if not isinstance(picos, int) or isinstance(picos, bool):
            raise ValidationFailed(
                "a price arrived as something other than an integer count of picos",
                tool=name,
                got=repr(picos),
            )
        tools.append((str(name), picos))
    return Blueprint(
        agent=str(raw["name"]),
        spec_fingerprint=str(meta["omnexSpec"]),
        paradigm=str(meta["omnexParadigm"]),
        entry=str(meta["omnexEntry"]),
        steps=tuple(steps),
        tool_picos=tuple(sorted(tools)),
    )
