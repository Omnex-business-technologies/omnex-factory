"""Classify every node in the ontology against code that actually imports.

    python scripts/node_map.py

`ontology_map.py` answers "which of 28 branches does `engine/` cover". That is
the resolution at which the answer is comfortable. This asks the same question of
all 507 NODES, which is the resolution at which it is not.

## Three claims, and why `implemented` is not one a machine may award

A node name will never equal a symbol name — "Vector Search" is
`omnex.vectors.HybridStore`, and no amount of string handling makes that
identity. So each node carries an **alias**: a dotted symbol somebody asserts
means the same capability.

    gap          no alias. Nothing in `engine/` is even a candidate.
    proposed     an alias that IMPORTS, proposed by lexical match, confirmed by
                 nobody. The symbol exists; whether it means the same thing is
                 an open question.
    implemented  a proposed alias a human has marked `verified`.
    rejected     a human looked and said these are not the same capability. The
                 alias stays as the record of what was rejected.

`rejected` is not decoration. Without it a queue can only grow: the first refresh
after `omnex.mcp` landed proposed `Code -> omnex.mcp.ErrorCode`, which is wrong,
and with no way to record that it would come back on every run forever. A review
queue that cannot shrink is one people stop reading, and then `proposed` means
nothing at all.

Rejection is a human judgement for exactly the same reason acceptance is. The
machine may sort the queue — a proposal pointing at a module the branch does not
claim is flagged, because that is where the wrong ones cluster — but flagging is
not deciding.

The machine may propose and may verify that a symbol resolves. It may not decide
that two names mean the same capability, because that is precisely the judgement
a system grading its own coverage would get generously wrong — the frozen-criteria
problem, one level down from where `ontology_map.py` refuses it.

So a freshly generated map reports **zero implemented**, and that is correct
rather than pessimistic. Coverage here is earned by a person reading a proposal
and agreeing with it, one node at a time.

## What the number replaces

Every gap count quoted before this was measured against 28 branches or against a
list somebody wrote down. This one is measured against 507 named capabilities and
320 exported symbols, and it can be re-derived from the repository at any time.
"""

from __future__ import annotations

import importlib
import json
import pkgutil
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ingest_atlas import EXPECTED_NODES, EXPORT, parse
from ontology_map import resolve

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
NODES = ROOT / "ontology" / "nodes.json"
BRANCHES = ROOT / "ontology" / "branches.json"
OUTPUT = REPO / "corpus" / "universal-ai-os" / "NODE_MAP.md"

CLAIMS = ("implemented", "proposed", "rejected", "gap")


@dataclass
class Node:
    """One capability the ontology names, and what in `engine/` might be it."""

    branch: str
    name: str
    claim: str
    alias: str | None
    verified: bool
    note: str = ""
    #: Set by the audit, never stored: whether the alias imports right now.
    resolves: bool = field(default=False, compare=False)


def public_symbols() -> dict[str, str]:
    """Every name the package exports, mapped to the module that exports it."""
    import omnex

    found: dict[str, str] = {}
    for module in pkgutil.iter_modules(omnex.__path__):
        if module.name.startswith("_"):
            continue
        dotted = f"omnex.{module.name}"
        try:
            loaded = importlib.import_module(dotted)
        except ImportError:  # pragma: no cover - an optional extra is absent
            continue
        for name in getattr(loaded, "__all__", []):
            found.setdefault(name, dotted)
    return found


def _split_symbol(name: str) -> set[str]:
    parts = re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*|[a-z0-9]+", name)
    return {p.lower() for p in parts if len(p) > 1}


def _split_node(name: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", name.lower()) if len(t) > 1}


def propose(node_name: str, symbols: dict[str, str]) -> str | None:
    """Suggest a dotted symbol for a node name, or nothing.

    An exact token-set match, or the node's tokens contained in the symbol's.
    **Containment runs one way only**, and that direction is the rule that
    matters.

    A symbol MORE specific than the node can plausibly be its implementation:
    "MCP" is `McpClient`, "Quantization" is `QuantizationProfile`. A symbol LESS
    specific cannot be. `omnex.factory.Tool` is not "Tool Registry", and it is
    also not Tool Discovery, Tool Selection, Tool Permissions, Tool Invocation,
    Tool Sandbox, Tool Timeout, Tool Retry, Tool Audit or nine others — which is
    exactly what the earlier bidirectional rule proposed, all to the same symbol,
    in one run. Thirty-five of sixty proposals came from that direction and
    almost all were noise.

    A reviewer who has to disprove sixty proposals one by one stops reviewing,
    and `proposed` then means nothing. Two good proposals are lost with the
    thirty-five — `Dead Letter Queue -> omnex.pipeline.DeadLetter` is the clear
    one — and a human can commit those by hand. That asymmetry is deliberate: a
    missing proposal costs one manual entry, a queue full of noise costs the
    whole mechanism.
    """
    wanted = _split_node(node_name)
    if not wanted:
        return None
    best: tuple[str, float] | None = None
    for symbol, module in symbols.items():
        have = _split_symbol(symbol)
        if not have:
            continue
        if wanted == have:
            score = 1.0
        elif wanted < have:
            score = 0.8
        else:
            continue
        if best is None or score > best[1]:
            best = (f"{module}.{symbol}", score)
    return best[0] if best else None


def load() -> list[Node]:
    raw: dict[str, Any] = json.loads(NODES.read_text(encoding="utf-8"))
    return [
        Node(
            branch=entry["branch"],
            name=entry["name"],
            claim=entry["claim"],
            alias=entry["alias"],
            verified=entry["verified"],
            note=entry.get("note", ""),
        )
        for entry in raw["nodes"]
    ]


def generate() -> list[Node]:
    """Build the first version of the claim file from the export plus the code."""
    branches, _ = parse(EXPORT.read_text(encoding="utf-8"))
    symbols = public_symbols()
    nodes: list[Node] = []
    for branch in branches:
        for name in branch.node_names:
            alias = propose(name, symbols)
            nodes.append(
                Node(
                    branch=branch.id,
                    name=name,
                    claim="proposed" if alias else "gap",
                    alias=alias,
                    verified=False,
                )
            )
    return nodes


def audit(nodes: list[Node]) -> list[str]:
    """Every rule, collected — refusals are reported together, never one at a time."""
    problems: list[str] = []
    for node in nodes:
        if node.claim not in CLAIMS:
            problems.append(f"{node.branch}/{node.name}: claim {node.claim!r} is unknown")

        if node.alias:
            reason = resolve(node.alias)
            node.resolves = reason is None
            if reason is not None:
                problems.append(f"{node.branch}/{node.name}: alias {node.alias} — {reason}")
        elif node.claim != "gap":
            problems.append(f"{node.branch}/{node.name}: claims {node.claim!r} with no alias")

        if node.claim in ("implemented", "rejected") and not node.verified:
            problems.append(
                f"{node.branch}/{node.name}: {node.claim!r} without a human verification"
            )
        if node.verified and not node.alias:
            problems.append(f"{node.branch}/{node.name}: verified nothing")
    return problems


def branch_modules() -> dict[str, set[str]]:
    raw: dict[str, Any] = json.loads(BRANCHES.read_text(encoding="utf-8"))
    return {b["id"]: set(b["modules"]) for b in raw["branches"]}


def off_branch(node: Node, modules: dict[str, set[str]]) -> bool:
    """Whether a proposal points at a module its branch does not claim.

    A flag for the reviewer, never a decision. The wrong proposals cluster here —
    `Code -> omnex.mcp.ErrorCode` is on a branch that claims no MCP at all — so
    sorting these to the top puts the easy rejections first and the queue drains
    from the end that is cheapest to work.

    It stays a flag because good proposals live here too:
    `Quantization -> omnex.serving.QuantizationProfile` crosses a branch boundary
    and is plainly right. Turning this into a filter would discard it.
    """
    if not node.alias:
        return False
    claimed = modules.get(node.branch, set())
    return bool(claimed) and node.alias.rsplit(".", 1)[0] not in claimed


def render(nodes: list[Node]) -> str:
    counts = {claim: sum(1 for n in nodes if n.claim == claim) for claim in CLAIMS}
    by_branch: dict[str, list[Node]] = {}
    for node in nodes:
        by_branch.setdefault(node.branch, []).append(node)

    lines = [
        "# Node map — 507 capabilities against code that imports",
        "",
        "Generated by `engine/scripts/node_map.py`. Do not edit.",
        "",
        f"**{counts['gap']} of {len(nodes)} nodes have no candidate in `engine/` at "
        f"all.** {counts['proposed']} have an alias that imports but that nobody has "
        f"confirmed means the same capability. {counts['implemented']} are confirmed, "
        f"and {counts['rejected']} were looked at and rejected — a rejection is a "
        "result, and the only thing that stops a wrong proposal returning forever.",
        "",
        "A machine proposed every alias here by lexical match and verified that each "
        "one imports. It did not decide that two names mean the same thing, and it "
        "may not: that is the judgement a system grading its own coverage gets "
        "generously wrong. `implemented` is earned by a person reading a proposal "
        "and agreeing with it, one node at a time — so a freshly generated map "
        "reporting zero implemented is correct, not pessimistic.",
        "",
        "Every gap count quoted before this one was measured against 28 branches or "
        "against a list somebody wrote down. This is measured against 507 named "
        "capabilities and the package's own exported symbols.",
        "",
        "| # | Nodes | gap | proposed | rejected | implemented |",
        "|---|--:|--:|--:|--:|--:|",
    ]
    for branch in sorted(by_branch, key=lambda b: -len(by_branch[b])):
        rows = by_branch[branch]
        lines.append(
            f"| {branch} | {len(rows)} | "
            f"{sum(1 for n in rows if n.claim == 'gap')} | "
            f"{sum(1 for n in rows if n.claim == 'proposed')} | "
            f"{sum(1 for n in rows if n.claim == 'rejected')} | "
            f"{sum(1 for n in rows if n.claim == 'implemented')} |"
        )

    modules = branch_modules()
    pending = [n for n in nodes if n.claim == "proposed"]
    flagged = [n for n in pending if off_branch(n, modules)]
    aligned = [n for n in pending if not off_branch(n, modules)]

    lines += [
        "",
        "## Proposals awaiting a human",
        "",
        "Sorted cheapest-to-judge first. A proposal pointing at a module its own "
        "branch does not claim is where the wrong ones cluster — but not all of "
        "them, so this is a flag and not a filter. Recording a **rejection** "
        "matters as much as recording an acceptance: without it the same wrong "
        "proposal returns on every run, and a queue that cannot shrink is one "
        "nobody reads.",
        "",
        f"### Off-branch — {len(flagged)} proposals on a module the branch does not claim",
        "",
    ]
    for node in sorted(flagged, key=lambda n: (n.branch, n.name)):
        lines.append(f"- `{node.branch}` **{node.name}** → `{node.alias}`")

    lines += ["", f"### On-branch — {len(aligned)} proposals", ""]
    for node in sorted(aligned, key=lambda n: (n.branch, n.name)):
        lines.append(f"- `{node.branch}` **{node.name}** → `{node.alias}`")

    rejected = [n for n in nodes if n.claim == "rejected"]
    if rejected:
        lines += ["", f"## Rejected by a human — {len(rejected)}", ""]
        for node in sorted(rejected, key=lambda n: (n.branch, n.name)):
            reason = f" — {node.note}" if node.note else ""
            lines.append(f"- `{node.branch}` **{node.name}** ≠ `{node.alias}`{reason}")

    lines.append("")
    return "\n".join(lines) + "\n"


def refresh(nodes: list[Node], symbols: dict[str, str]) -> list[str]:
    """Re-propose for gap nodes only, and report what moved.

    Code lands after the map is written — `omnex.mcp` is the first case — and a
    map that never looks again reports a gap for a capability now in the package.
    So the machine gets one more thing it is allowed to do: propose an alias for
    a node that has none.

    It is allowed nothing else. A `proposed` alias is left alone, because
    replacing one proposal with another silently discards whatever a reviewer was
    part-way through reading. A `verified` node — accepted or rejected — is never
    touched at all: a human looked, and a later run of a lexical matcher does not
    outrank that. Re-proposing a rejection is how a queue stops shrinking.
    """
    moved: list[str] = []
    for node in nodes:
        if node.claim != "gap" or node.verified or node.alias:
            continue
        alias = propose(node.name, symbols)
        if alias is None:
            continue
        node.claim = "proposed"
        node.alias = alias
        moved.append(f"{node.branch}/{node.name} -> {alias}")
    return moved


def prune(nodes: list[Node]) -> list[str]:
    """Withdraw proposals the current rule would no longer make.

    The mirror of `refresh()`, and legitimate for the same reason: the machine is
    un-proposing what the machine proposed, under a rule it no longer holds. It
    never touches a verified node — an alias a human accepted or rejected is
    their decision, and a matcher that changed its mind does not outrank it.

    Without this, tightening a rule leaves the queue full of proposals the code
    now agrees are wrong, and the file stops describing what the script would
    produce.
    """
    withdrawn: list[str] = []
    for node in nodes:
        if node.claim != "proposed" or node.verified or not node.alias:
            continue
        module, _, symbol = node.alias.rpartition(".")
        if propose(node.name, {symbol: module}) is not None:
            continue
        withdrawn.append(f"{node.branch}/{node.name} was {node.alias}")
        node.claim = "gap"
        node.alias = None
    return withdrawn


def save(nodes: list[Node]) -> None:
    NODES.write_text(
        json.dumps(
            {
                "ontology_version": "2",
                "nodes": [
                    {
                        "branch": n.branch,
                        "name": n.name,
                        "claim": n.claim,
                        "alias": n.alias,
                        "verified": n.verified,
                        "note": n.note,
                    }
                    for n in nodes
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    if NODES.exists():
        nodes = load()
        withdrawn = prune(nodes)
        moved = refresh(nodes, public_symbols())
        if withdrawn or moved:
            save(nodes)
        if withdrawn:
            print(f"{len(withdrawn)} proposal(s) withdrawn — the rule no longer makes them:")
            for line in withdrawn[:10]:
                print(f"  {line}")
            if len(withdrawn) > 10:
                print(f"  ... and {len(withdrawn) - 10} more")
            print()
        if moved:
            print(f"{len(moved)} gap node(s) now have a proposal:")
            for line in moved:
                print(f"  {line}")
            print()
    else:
        nodes = generate()
        save(nodes)

    problems = audit(nodes)
    if len(nodes) != EXPECTED_NODES:
        problems.append(f"{len(nodes)} nodes loaded, the export declares {EXPECTED_NODES}")

    if problems:
        for problem in problems[:20]:
            print(f"FAIL {problem}")
        if len(problems) > 20:
            print(f"... and {len(problems) - 20} more")
        return 1

    OUTPUT.write_text(render(nodes), encoding="utf-8")
    counts = {claim: sum(1 for n in nodes if n.claim == claim) for claim in CLAIMS}
    print(f"{len(nodes)} nodes · {len(public_symbols())} exported symbols")
    print(f"  gap          {counts['gap']}")
    print(f"  proposed     {counts['proposed']}  (alias imports, unconfirmed)")
    print(f"  rejected     {counts['rejected']}  (a person said no)")
    print(f"  implemented  {counts['implemented']}  (a person agreed)")
    print(f"\nwrote {OUTPUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
