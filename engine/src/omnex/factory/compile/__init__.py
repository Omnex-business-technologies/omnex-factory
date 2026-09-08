"""One spec, three targets, and a round trip that decides whether each works.

    code   an `omnex.graph.Graph` this process runs
    mcp    a server manifest a host stands up
    n8n    a workflow JSON somebody imports into their own instance

The target is chosen per agent and passed in. Nothing here picks one, because a
compiler that hardcodes its target is a code generator with extra steps, and the
whole point of the neutral `Blueprint` is that the same specification can land in
whichever of the three a customer already runs.

## The property that makes these compilers rather than emitters

    parse(emit(blueprint)) == blueprint

A compiler that cannot re-read its own output has no way to tell a lossy
emission from a correct one, and the loss is invisible — the artifact still
opens, still lays out, still looks like the agent. `round_trip()` runs the check
and `assert_round_trips()` raises with what differed, so a field added to
`Blueprint` and forgotten in one emitter fails immediately rather than at the
first deployment that needed it.

The three are checked the same way against the same blueprint, which is also how
"does the n8n workflow do the same thing as the code" becomes a question with an
answer.
"""

from __future__ import annotations

from enum import StrEnum

from ...core.errors import ValidationFailed
from ..spec import AgentSpec
from . import bindings, code, mcp_topology, n8n
from .bindings import Binding, Catalogue, NodeType
from .blueprint import Blueprint, Step, StepKind, plan

__all__ = [
    "Binding",
    "Blueprint",
    "Catalogue",
    "NodeType",
    "Step",
    "StepKind",
    "Target",
    "assert_round_trips",
    "bindings",
    "code",
    "compile_spec",
    "mcp_topology",
    "n8n",
    "plan",
    "round_trip",
]


class Target(StrEnum):
    CODE = "code"
    MCP = "mcp"
    N8N = "n8n"


def compile_spec(spec: AgentSpec, target: Target, catalogue: Catalogue | None = None) -> object:
    """Compile to one named target. The caller chooses; nothing here defaults.

    `catalogue` binds n8n nodes to real node types and is ignored by the other
    two targets, which have no such gap: the code target runs in this process and
    the MCP manifest describes tools the host already owns.
    """
    blueprint = plan(spec)
    if target is Target.CODE:
        return code.emit(blueprint)
    if target is Target.MCP:
        return mcp_topology.emit(blueprint)
    return n8n.emit(blueprint, catalogue)


def round_trip(
    blueprint: Blueprint, target: Target, catalogue: Catalogue | None = None
) -> Blueprint:
    """Emit and read straight back, through the real emitter and the real parser."""
    if target is Target.CODE:
        return code.parse(code.emit(blueprint), blueprint)
    if target is Target.MCP:
        return mcp_topology.parse(mcp_topology.emit(blueprint))
    return n8n.parse(n8n.emit(blueprint, catalogue))


def assert_round_trips(
    blueprint: Blueprint, target: Target, catalogue: Catalogue | None = None
) -> None:
    """Raise naming what differed, rather than returning False.

    A boolean tells you a compiler is lossy. The difference tells you which
    field, which is the part somebody has to fix.
    """
    returned = round_trip(blueprint, target, catalogue)
    if returned == blueprint:
        return
    differences = [
        f"{field}: {getattr(blueprint, field)!r} -> {getattr(returned, field)!r}"
        for field in ("agent", "spec_fingerprint", "paradigm", "entry", "tool_picos")
        if getattr(blueprint, field) != getattr(returned, field)
    ]
    before = {s.name: s.digest() for s in blueprint.steps}
    after = {s.name: s.digest() for s in returned.steps}
    differences.extend(
        f"step {name}: {before.get(name)!r} -> {after.get(name)!r}"
        for name in sorted(set(before) | set(after))
        if before.get(name) != after.get(name)
    )
    raise ValidationFailed(
        f"the {target} compiler does not round-trip:\n  " + "\n  ".join(differences),
        target=str(target),
        differences=differences,
    )
