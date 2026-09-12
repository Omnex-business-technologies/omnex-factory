"""The canonical capability registry, evidence derived rather than typed.

    python scripts/capability_map.py            # regenerate ontology/CAPABILITIES.md
    python scripts/capability_map.py --check    # fail if the file disagrees with reality

Required by the operator's Sovereign Execution Standard, Phase 1: "canonical
capability registry" plus "Every material claim must resolve to an evidence
object." `ontology/capabilities.json` is the one thing a person must state per
capability — name, symbol, contract, dependencies, security requirements,
limitations, known risks, economic relevance. Everything the standard calls
"evidence" is derived here, for the same reason `nodes.json`'s `verified` is
the one field `node_map.py` may never set: a registry where evidence is typed
by whoever wrote the entry is a registry that always agrees with itself.

## The evidence ladder, honestly capped

The standard defines E0 (unknown) through E7 (outcome proven). This script can
derive E0 through E4 from static analysis of this repository:

    E1  DECLARED           the entry names a symbol that does not resolve
    E2  CODE_PRESENT       the symbol resolves; nothing references it in tests
    E3  TESTED             at least one test file references the symbol
    E4  INTEGRATED         at least one OTHER production module references it

E5 (operationally verified), E6 (production verified) and E7 (outcome proven)
all require evidence from a running deployment, which does not exist — gate
`5_production` in `state_map.py` already says so. Rather than silently
omitting them or guessing, every capability here is explicitly reported
`E5_UNKNOWN_NOT_OBSERVABLE` with the same reason, because the standard's own
§7 is explicit: "if the state or claim is currently unsupported: UNSUPPORTED
... never guess, never fill gaps with assumptions."

## No timestamp, same reason as state_map.py

A generation time would change on every run and the rendered file would
disagree with itself; `--check` would have to learn to ignore a field, and once
a validator ignores one field it can be taught to ignore another. Verification
is against the working tree at the moment the script runs, not against a
recorded instant.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
SOURCE = ENGINE / "ontology" / "capabilities.json"
OUTPUT = ENGINE / "ontology" / "CAPABILITIES.md"
SRC = ENGINE / "src"

sys.path.insert(0, str(SRC))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from omnex.core.symbols import resolve  # noqa: E402

#: Why E5-E7 cannot be derived here, quoted verbatim into every capability that
#: reaches this rung — a single source of truth for the sentence, since a typo
#: in one of eight copies is exactly the drift this file exists to prevent.
NOT_OBSERVABLE_REASON = (
    "requires evidence from a running deployment (traces, an operator, a "
    "payment); this repository has none, matching state_map.py's gate "
    "5_production, which is UNKNOWN for the same reason"
)


def load() -> list[dict[str, Any]]:
    return json.loads(SOURCE.read_text(encoding="utf-8"))["capabilities"]


def _bare_name(symbol: str) -> str:
    return symbol.rsplit(".", 1)[-1]


def _defining_file(symbol: str) -> Path | None:
    """The source file a resolved symbol's module maps to, so it can be excluded
    from its own integration count — a class is not "integrated" by its own body."""
    module_path = symbol.rsplit(".", 1)[0]
    candidate = SRC / Path(*module_path.split(".")).with_suffix(".py")
    return candidate if candidate.exists() else None


def _referencing_files(root: Path, name: str, exclude: Path | None) -> list[str]:
    pattern = re.compile(rf"\b{re.escape(name)}\b")
    found: list[str] = []
    for path in sorted(root.rglob("*.py")):
        if exclude is not None and path == exclude:
            continue
        if pattern.search(path.read_text(encoding="utf-8")):
            found.append(str(path.relative_to(REPO)))
    return found


def derive(entry: dict[str, Any]) -> dict[str, Any]:
    """One capability's evidence, computed fresh — never read from a stored field."""
    symbol = entry["symbol"]
    name = _bare_name(symbol)
    reason = resolve(symbol)
    resolves = reason is None

    if not resolves:
        return {
            **entry,
            "resolves": False,
            "resolution_failure": reason,
            "test_files": [],
            "integrated_by": [],
            "evidence_level": "E1_DECLARED",
            "lifecycle_state": "DISCOVERED",
            "evidence_reason": f"{symbol} does not resolve: {reason}",
        }

    own_file = _defining_file(symbol)
    test_files = _referencing_files(ENGINE / "tests", name, exclude=None)
    integrated_by = _referencing_files(SRC, name, exclude=own_file)

    if not test_files:
        level, state = "E2_CODE_PRESENT", "IMPLEMENTED"
        why = f"{symbol} resolves; no test file references {name!r}"
    elif not integrated_by:
        level, state = "E3_TESTED", "TESTED"
        why = f"{len(test_files)} test file(s) reference {name!r}; no other production module does"
    else:
        level, state = "E4_INTEGRATED", "INTEGRATED"
        why = (
            f"{len(test_files)} test file(s) and {len(integrated_by)} other "
            f"production module(s) reference {name!r}"
        )

    return {
        **entry,
        "resolves": True,
        "resolution_failure": None,
        "test_files": test_files,
        "integrated_by": integrated_by,
        "evidence_level": level,
        "lifecycle_state": state,
        "evidence_reason": why,
    }


def derive_all() -> list[dict[str, Any]]:
    return [derive(entry) for entry in load()]


def render(capabilities: list[dict[str, Any]]) -> str:
    by_level: dict[str, int] = {}
    for cap in capabilities:
        by_level[cap["evidence_level"]] = by_level.get(cap["evidence_level"], 0) + 1

    lines = [
        "# Capabilities — the evidence ladder, per capability",
        "",
        "Generated by `engine/scripts/capability_map.py`. Do not edit.",
        "",
        f"**{len(capabilities)} capabilities.** By evidence level: "
        + ", ".join(f"{level} {count}" for level, count in sorted(by_level.items())),
        "",
        "E0-E4 are derived from this repository (symbol resolution, test and "
        "production references). E5-E7 (operationally verified, production "
        "verified, outcome proven) are not derivable from a repository scan and "
        f"are reported `E5_UNKNOWN_NOT_OBSERVABLE` for every capability: "
        f"{NOT_OBSERVABLE_REASON}.",
        "",
        "| id | name | symbol | evidence | lifecycle |",
        "|---|---|---|---|---|",
    ]
    for cap in capabilities:
        lines.append(
            f"| {cap['id']} | {cap['name']} | `{cap['symbol']}` | "
            f"{cap['evidence_level']} | {cap['lifecycle_state']} |"
        )
    lines.append("")

    for cap in capabilities:
        lines += [
            f"## {cap['id']}: {cap['name']}",
            "",
            cap["description"],
            "",
            f"- **symbol:** `{cap['symbol']}`",
            f"- **contract:** {cap['contract']}",
            f"- **dependencies:** {', '.join(cap['dependencies']) or 'none declared'}",
            f"- **security requirements:** {'; '.join(cap['security_requirements']) or 'none declared'}",
            f"- **evidence:** {cap['evidence_level']} — {cap['evidence_reason']}",
            f"- **operational/production/outcome evidence:** E5_UNKNOWN_NOT_OBSERVABLE — "
            f"{NOT_OBSERVABLE_REASON}",
            f"- **test files ({len(cap['test_files'])}):** "
            + (", ".join(f"`{t}`" for t in cap["test_files"]) or "none"),
            f"- **integrated by ({len(cap['integrated_by'])}):** "
            + (", ".join(f"`{t}`" for t in cap["integrated_by"]) or "none"),
            f"- **limitations:** {cap['limitations']}",
            f"- **known risks:** {cap['known_risks']}",
            f"- **economic relevance:** {cap['economic_relevance']}",
            "",
        ]
    return "\n".join(lines)


def summarise(capabilities: list[dict[str, Any]]) -> dict[str, Any]:
    """The counts `state_map.py`'s gate 3 reads. Recomputed there too, never stored."""
    by_level: dict[str, int] = {}
    for cap in capabilities:
        by_level[cap["evidence_level"]] = by_level.get(cap["evidence_level"], 0) + 1
    return {
        "total": len(capabilities),
        "by_evidence_level": dict(sorted(by_level.items())),
        "at_least_integrated": sum(
            1 for c in capabilities if c["evidence_level"] == "E4_INTEGRATED"
        ),
    }


def main() -> int:
    check = "--check" in sys.argv
    capabilities = derive_all()
    rendered = render(capabilities)

    if check:
        if not OUTPUT.exists():
            print(f"FAIL {OUTPUT.relative_to(REPO)} does not exist — run without --check first")
            return 1
        committed = OUTPUT.read_text(encoding="utf-8")
        if committed != rendered:
            print(f"FAIL {OUTPUT.relative_to(REPO)} disagrees with the repository — regenerate it")
            return 1
        print(f"{OUTPUT.relative_to(REPO)} agrees with the repository.")
        return 0

    OUTPUT.write_text(rendered, encoding="utf-8")
    summary = summarise(capabilities)
    print(f"{summary['total']} capabilities  {summary['by_evidence_level']}")
    print(f"wrote {OUTPUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
