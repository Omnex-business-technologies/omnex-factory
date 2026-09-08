"""Validate the n8n binding catalogue, and say how much of it anybody has seen work.

    python scripts/n8n_bindings_check.py

`ontology_map.py` checks claims about branches. `invariant_map.py` checks this
repository's rules. This checks the one piece of configuration the engine cannot
derive and cannot verify: what an n8n node actually is.

## The number it exists to report

Not "how many bindings are written down" — writing one down costs nothing and
proves nothing. The number is **how many have been confirmed by an import**, and
today it is zero of seven. That figure can only go up when a person imports a
workflow into a real n8n instance and records their name against the binding, so
it is the one thing here a script cannot flatter.

The structural checks — a binding naming a node type that does not exist, a
confirmation with nobody behind it, a value shaped like a credential, a
network-calling node with no address and no explanation — all run on load and
raise together rather than one at a time.

Exits non-zero on a catalogue that will not load. It does **not** exit non-zero
on unconfirmed bindings: unconfirmed is the honest starting state of every entry,
and a permanently red build is one people learn to ignore.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import re
import shlex
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
sys.path.insert(0, str(ENGINE / "src"))

from omnex.core.errors import ValidationFailed  # noqa: E402
from omnex.factory.compile import bindings  # noqa: E402

CATALOGUE = ENGINE / "ontology" / "n8n_bindings.json"

#: `source` value claiming the command is this repository's own, and therefore
#: checkable from here. Anything else names a remote shape nothing local can
#: resolve, and is reported as proposed instead.
OURS = "this repository"

_ENV = re.compile(r"\$\{?([A-Z][A-Z0-9_]*)\}?")


def unresolved_commands(catalogue: bindings.Catalogue) -> list[str]:
    """Bindings that claim to run this repository's own code and do not.

    The failure this exists for happened: two bindings named
    `python -m omnex.pipeline.verify_webhook` and `...seen_before`, neither of
    which was a module. A catalogue entry is prose until something resolves it,
    and an unresolvable command is worse than an unbound ref — the workflow
    imports, the node is not a placeholder, and it fails at the first real order.

    Only entries whose `source` is this repository are checked. A storefront
    endpoint cannot be resolved from here and says so in its own note.
    """
    problems: list[str] = []
    for ref, binding in sorted(catalogue.bindings.items()):
        if binding.source != OURS:
            continue
        command = str(binding.parameters.get("command", ""))
        if not command:
            problems.append(f"{ref} claims to run this repository's code and names no command")
            continue
        problems.extend(f"{ref}: {problem}" for problem in _resolve(command))
    return problems


def _resolve(command: str) -> list[str]:
    tokens = shlex.split(command)
    if "-m" in tokens:
        module = tokens[tokens.index("-m") + 1]
        rest = tokens[tokens.index("-m") + 2 :]
        subcommand = next((t for t in rest if not t.startswith("-")), "")
        return _resolve_module(module, subcommand)

    script = next((t for t in tokens if t.endswith(".py")), "")
    if not script:
        return [f"{command!r} runs neither a module nor a .py file in this repository"]
    if not (REPO / script).exists():
        return [f"{script} does not exist"]
    return []


def _resolve_module(module: str, subcommand: str) -> list[str]:
    entry = f"{module}.__main__"
    try:
        # find_spec RAISES rather than returning None when a parent package is
        # missing, which is the common case here: the defect this catches named
        # `omnex.pipeline.verify_webhook`, a package that never existed.
        found = importlib.util.find_spec(entry)
    except ModuleNotFoundError:
        found = None
    if found is None:
        return [f"{module} has no __main__, so `python -m {module}` cannot run"]
    if not subcommand:
        return []

    parser = importlib.import_module(entry).build_parser()
    # `choices` on the sub-parsers action is the only place argparse records the
    # accepted subcommands. Reading it is better than calling parse_args, which
    # would raise on the required flags this command legitimately has.
    known = [
        name
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
        for name in action.choices
    ]
    if known and subcommand not in known:
        return [f"`{module} {subcommand}` is not a subcommand; it accepts {', '.join(known)}"]
    return []


def required_env(catalogue: bindings.Catalogue) -> dict[str, list[str]]:
    """Environment variables the catalogue's commands read, and who reads each.

    An operator setting up an n8n host needs this list, and the honest place to
    derive it is the commands themselves rather than a second document that goes
    stale the first time a flag changes.
    """
    found: dict[str, list[str]] = {}
    for ref, binding in sorted(catalogue.bindings.items()):
        interpolated = set(_ENV.findall(str(binding.parameters.get("command", ""))))
        # A secret is deliberately absent from the command string, so deriving
        # this list from the commands alone would name every variable except the
        # ones whose absence stops the workflow.
        for name in sorted(interpolated | set(binding.env)):
            found.setdefault(name, []).append(ref)
    return found


def main() -> int:
    try:
        catalogue = bindings.load(CATALOGUE)
    except ValidationFailed as exc:
        print(f"FAIL {exc}")
        return 1

    print(catalogue.summary())
    print()

    width = max((len(ref) for ref in catalogue.bindings), default=0)
    for ref, binding in sorted(catalogue.bindings.items()):
        node_type = catalogue.node_type_of(binding)
        if catalogue.is_confirmed(ref):
            status = f"confirmed by {binding.confirmed_by} on {binding.confirmed_at}"
        elif binding.confirmed:
            status = f"binding confirmed, node type {node_type.name!r} is not"
        else:
            status = f"proposed ({binding.source})"
        print(f"  {ref:<{width}}  {node_type.type:<32} {status}")

    unaddressed = sorted(
        ref
        for ref, binding in catalogue.bindings.items()
        if catalogue.node_type_of(binding).calls_out and not binding.parameters.get("url")
    )
    if unaddressed:
        print()
        print(
            f"{len(unaddressed)} binding(s) reach the network with no url, each "
            "carrying a note saying why:"
        )
        for ref in unaddressed:
            print(f"  {ref}")

    environment = required_env(catalogue)
    if environment:
        print()
        print(f"{len(environment)} environment variable(s) the commands read:")
        for name, refs in sorted(environment.items()):
            print(f"  {name:<24} {', '.join(refs)}")

    problems = unresolved_commands(catalogue)
    print()
    if problems:
        print(f"FAIL {len(problems)} command(s) name code this repository does not have:")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print(
        "Every command claiming to run this repository's own code resolves. "
        "Confirmed, though, means somebody imported the workflow and n8n accepted "
        "it — nothing here can establish that, which is why that count is the "
        "number worth reading."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
