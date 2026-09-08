"""What an n8n node actually is, as data a person confirms — branch XI's gap.

`n8n.py` emits a workflow whose every node is `n8n-nodes-base.noOp`. That is the
honest artifact for a compiler with nothing to go on: an `AgentSpec` names a tool
and its price and says nothing about which endpoint it is, what credential it
uses or what body it posts, so a compiler that filled those in would be shipping
configuration nobody supplied. Branch XI records the consequence in its own
`missing` field — the workflow imports as a wiring diagram rather than running.

This is the thing that was missing, and it is deliberately **data, not code**.
The shapes n8n and a storefront expect cannot be verified from the environment
this repository is developed in; the open web is refused at the proxy. So no
shape is inferred here. Each one is written down, validated structurally, and
carries the one fact that matters about it:

## A binding is proposed until a person imports it

`confirmed` starts false and cannot be set by anything mechanical. Flipping it
requires `confirmed_by` (a name) and `confirmed_at` (a date), because the only
evidence that a node type and its parameters are right is that a real n8n
instance accepted them — and this process cannot perform that import. It is the
same rule `ontology/nodes.json` already runs on symbol resolution, one level out:
a machine may propose, only a person may verify.

## Credentials are named, never carried

A binding names a credential; it never holds one. The emitted workflow JSON goes
into a repository, and a key in it is an incident rather than a configuration.
`looks_like_a_secret` is run over every value on load AND over the whole emitted
document, because the two failures are different — a secret typed into the
catalogue and a secret that arrives through some other parameter path.

## One definition of a node type, not one per binding

`node_types` is separate from `bindings` for the same reason symbol resolution
has a single implementation: two bindings that each spell out `typeVersion` will
eventually disagree, and the disagreement is invisible in a diff of either one.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ...core.errors import ValidationFailed

__all__ = [
    "Binding",
    "Catalogue",
    "NodeType",
    "load",
    "looks_like_a_secret",
    "unbound_refs",
]

#: Values that must never appear in a committed catalogue or an emitted workflow.
#: Deliberately shape-based rather than a list of provider prefixes: a rule that
#: only knows `sk-` is satisfied by every key that is not OpenAI's.
_SECRET_SHAPES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "an API key prefix",
        re.compile(r"\b(?:sk|pk|rk|shpat|xox[baprs]|ghp|gho|github_pat)[-_][A-Za-z0-9_-]{8,}"),
    ),
    ("an inline bearer token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{12,}")),
    ("a JSON Web Token", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.")),
    ("a private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("a URL with credentials in it", re.compile(r"https?://[^/\s:@]+:[^/\s@]+@")),
)


def looks_like_a_secret(value: str) -> str | None:
    """Name the shape that matched, or `None`.

    Returns the description rather than a boolean because "this file contains a
    secret" is not actionable and "line contains an inline bearer token" is.
    """
    for description, pattern in _SECRET_SHAPES:
        if pattern.search(value):
            return description
    return None


@dataclass(frozen=True)
class NodeType:
    """One n8n node type, defined once and referenced by name.

    `confirmed` means a person imported a workflow containing this type into a
    real n8n instance and it was accepted. Nothing in this process can establish
    that, so nothing in this process may set it.
    """

    name: str
    type: str
    type_version: float
    #: Whether this node reaches the network. Drives the error-output rule and,
    #: later, retry and rate-limit parameters.
    calls_out: bool = False
    confirmed: bool = False
    confirmed_by: str = ""
    confirmed_at: str = ""
    note: str = ""


@dataclass(frozen=True)
class Binding:
    """One blueprint `ref` mapped onto a node type, with its parameters."""

    ref: str
    node_type: str
    #: The credential's NAME in the operator's n8n instance, keyed by credential
    #: kind. Never a value — see the module docstring.
    credentials: dict[str, str] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    #: Environment variables the command reads INSIDE itself rather than through
    #: its arguments. A signing secret belongs here and must never appear in a
    #: command string: argv is visible in `ps` and n8n records what it ran.
    #: Without this field an operator reading the derived environment list would
    #: set every variable the commands interpolate and none of the ones that
    #: matter most.
    env: tuple[str, ...] = ()
    confirmed: bool = False
    confirmed_by: str = ""
    confirmed_at: str = ""
    #: Where the shape came from. `proposal` means somebody wrote it down from
    #: documentation nobody here could open, which is not the same claim as
    #: having seen it work.
    source: str = "proposal"
    note: str = ""


@dataclass(frozen=True)
class Catalogue:
    """Node types and bindings, already validated."""

    node_types: dict[str, NodeType]
    bindings: dict[str, Binding]
    path: Path | None = None

    def get(self, ref: str) -> Binding | None:
        return self.bindings.get(ref)

    def node_type_of(self, binding: Binding) -> NodeType:
        return self.node_types[binding.node_type]

    def is_confirmed(self, ref: str) -> bool:
        """A binding is only as confirmed as the node type it stands on."""
        binding = self.bindings.get(ref)
        if binding is None:
            return False
        return binding.confirmed and self.node_types[binding.node_type].confirmed

    def summary(self) -> str:
        confirmed = sum(1 for ref in self.bindings if self.is_confirmed(ref))
        types_ok = sum(1 for t in self.node_types.values() if t.confirmed)
        return (
            f"{len(self.bindings)} binding(s), {confirmed} confirmed by an import · "
            f"{len(self.node_types)} node type(s), {types_ok} confirmed"
        )


EMPTY = Catalogue(node_types={}, bindings={})


def unbound_refs(refs: list[str], catalogue: Catalogue) -> list[str]:
    """Refs with no binding, sorted and de-duplicated.

    These are the nodes that still emit as placeholders. Reported rather than
    raised: a partially bound workflow is the normal state while a catalogue is
    being filled in, and refusing it outright would mean nobody could import
    anything until everything was done.
    """
    return sorted({ref for ref in refs if ref and ref not in catalogue.bindings})


def _confirmation_problems(what: str, name: str, payload: dict[str, Any]) -> list[str]:
    """A claim of confirmation needs a person's name and a date behind it."""
    if not payload.get("confirmed"):
        return []
    problems = []
    if not str(payload.get("confirmed_by") or "").strip():
        problems.append(
            f"{what} {name!r} claims confirmed with no confirmed_by — an import "
            "was performed by somebody, and nothing mechanical may claim it"
        )
    if not str(payload.get("confirmed_at") or "").strip():
        problems.append(f"{what} {name!r} claims confirmed with no confirmed_at date")
    return problems


def _secret_problems(what: str, name: str, payload: object, trail: str = "") -> list[str]:
    """Walk a value of any shape, because a secret hides at any depth."""
    problems: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            problems.extend(_secret_problems(what, name, value, f"{trail}.{key}"))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            problems.extend(_secret_problems(what, name, value, f"{trail}[{index}]"))
    elif isinstance(payload, str):
        shape = looks_like_a_secret(payload)
        if shape is not None:
            problems.append(
                f"{what} {name!r} carries what looks like {shape} at {trail or 'itself'} "
                "— a binding names a credential, it never holds one"
            )
    return problems


def load(path: Path) -> Catalogue:
    """Read and validate a catalogue, naming every problem at once.

    Stopping at the first one means whoever is filling this in learns about the
    next mistake only after fixing this one, which is how somebody concludes the
    check is the obstacle.
    """
    raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    problems: list[str] = []

    node_types: dict[str, NodeType] = {}
    for name, payload in sorted((raw.get("node_types") or {}).items()):
        missing = [key for key in ("type", "type_version") if key not in payload]
        if missing:
            problems.append(f"node type {name!r} is missing {', '.join(missing)}")
            continue
        if not str(payload["type"]).count("."):
            problems.append(
                f"node type {name!r} has type {payload['type']!r}, which is not a "
                "package-qualified n8n node type such as n8n-nodes-base.httpRequest"
            )
        if not isinstance(payload["type_version"], int | float) or isinstance(
            payload["type_version"], bool
        ):
            problems.append(f"node type {name!r} has a non-numeric type_version")
            continue
        problems.extend(_confirmation_problems("node type", name, payload))
        node_types[name] = NodeType(
            name=name,
            type=str(payload["type"]),
            type_version=float(payload["type_version"]),
            calls_out=bool(payload.get("calls_out", False)),
            confirmed=bool(payload.get("confirmed", False)),
            confirmed_by=str(payload.get("confirmed_by", "")),
            confirmed_at=str(payload.get("confirmed_at", "")),
            note=str(payload.get("note", "")),
        )

    bindings: dict[str, Binding] = {}
    for ref, payload in sorted((raw.get("bindings") or {}).items()):
        node_type = str(payload.get("node_type", ""))
        if node_type not in node_types:
            problems.append(
                f"binding {ref!r} names node type {node_type!r}, which this "
                "catalogue does not define"
            )
        credentials = payload.get("credentials") or {}
        if not isinstance(credentials, dict):
            problems.append(f"binding {ref!r} has credentials that are not a mapping")
            credentials = {}
        problems.extend(_confirmation_problems("binding", ref, payload))
        problems.extend(_secret_problems("binding", ref, payload.get("parameters") or {}))
        problems.extend(_secret_problems("binding", ref, credentials, ".credentials"))

        # A node that reaches the network and has no address is a half-binding.
        # That is a legitimate state — the endpoint may be genuinely unknown to
        # whoever wrote the entry — but it has to say so, or the next person
        # reads a missing URL as an oversight and invents one.
        parameters = payload.get("parameters") or {}
        calls_out = node_type in node_types and node_types[node_type].calls_out
        if calls_out and not parameters.get("url") and not str(payload.get("note", "")).strip():
            problems.append(
                f"binding {ref!r} uses a node type that reaches the network but "
                "names no url and gives no note — say why the endpoint is absent, "
                "or the next reader takes it for an oversight and invents one"
            )
        bindings[ref] = Binding(
            ref=ref,
            node_type=node_type,
            credentials={str(k): str(v) for k, v in credentials.items()},
            parameters=dict(payload.get("parameters") or {}),
            env=tuple(str(name) for name in payload.get("env") or ()),
            confirmed=bool(payload.get("confirmed", False)),
            confirmed_by=str(payload.get("confirmed_by", "")),
            confirmed_at=str(payload.get("confirmed_at", "")),
            source=str(payload.get("source", "proposal")),
            note=str(payload.get("note", "")),
        )

    if problems:
        raise ValidationFailed(
            f"{path.name} will not load:\n  " + "\n  ".join(problems),
            path=str(path),
            problems=problems,
        )
    return Catalogue(node_types=node_types, bindings=bindings, path=path)
