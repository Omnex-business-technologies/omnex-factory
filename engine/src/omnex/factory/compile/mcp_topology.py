"""The MCP target: a blueprint becomes a server manifest somebody can stand up.

What crosses here is the tool surface: names, the capability each step refers to,
prices in exact pico-dollars, and the order control moves through them. It is
JSON because that is what an MCP server's `tools/list` answers with and what a
host reads before it trusts anything.

**Prices travel as integer picos.** They are the one field on this wire where a
float would be silently wrong rather than loudly wrong: `0.0000005` survives a
JSON round trip looking fine and stops being exact the moment anything sums a
thousand of them. `omnex.mcp.ToolPrice` counts picos for the same reason, so the
manifest and the client agree by construction rather than by care.
"""

from __future__ import annotations

import json
from typing import Any

from ...core.errors import ValidationFailed
from .blueprint import Blueprint, Step, StepKind

__all__ = ["emit", "parse"]

MANIFEST_VERSION = 1


def emit(blueprint: Blueprint) -> str:
    blueprint.raise_if_invalid()
    payload = {
        "manifest": MANIFEST_VERSION,
        "agent": blueprint.agent,
        "spec": blueprint.spec_fingerprint,
        "paradigm": blueprint.paradigm,
        "entry": blueprint.entry,
        "tools": [{"name": name, "picos": picos} for name, picos in blueprint.tool_picos],
        "steps": [
            {"name": s.name, "kind": str(s.kind), "ref": s.ref, "next": list(s.goes_to)}
            for s in blueprint.steps
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False)


def parse(payload: str) -> Blueprint:
    raw: dict[str, Any] = json.loads(payload)
    if raw.get("manifest") != MANIFEST_VERSION:
        raise ValidationFailed(
            "manifest version mismatch; reading it anyway would apply this "
            "version's meanings to another version's fields",
            wanted=MANIFEST_VERSION,
            got=raw.get("manifest"),
        )
    tools: list[tuple[str, int]] = []
    for entry in raw.get("tools") or []:
        picos = entry.get("picos")
        if not isinstance(picos, int) or isinstance(picos, bool):
            raise ValidationFailed(
                "a price arrived as something other than an integer count of picos",
                tool=entry.get("name"),
                got=repr(picos),
            )
        tools.append((str(entry["name"]), picos))

    return Blueprint(
        agent=str(raw["agent"]),
        spec_fingerprint=str(raw["spec"]),
        paradigm=str(raw["paradigm"]),
        entry=str(raw["entry"]),
        steps=tuple(
            Step(
                name=str(s["name"]),
                kind=StepKind(s["kind"]),
                ref=str(s.get("ref", "")),
                goes_to=tuple(str(t) for t in s["next"]),
            )
            for s in raw["steps"]
        ),
        tool_picos=tuple(tools),
    )
