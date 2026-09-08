"""What `pip install omnex-engine[x]` actually gives you, measured per dependency.

    python scripts/extras_check.py

`env_check.py` compares a manifest of environment variables with the code that
reads them. This is the same argument one level out, on the promise a package
makes when somebody installs it.

## The defect this exists for, measured

`pip install omnex-engine[agents]` installs langgraph and crewai. **No module in
`src/omnex` imports either.** The install succeeds, the extra looks delivered, and
the user has two large dependencies and no capability. Six of twelve extras were
in that state when this was written: `api`, `memory`, `worker`, `agents`, `evals`,
`finetune` — zero of their declared dependencies imported anywhere.

Two docstrings made it worse by naming adapter modules that do not exist —
`graph/runtime.py` pointed at `langgraph_adapter.py`, `pipeline/queue.py` at
`celery_adapter.py`. That is the same class as `n8n_bindings.json` naming
`omnex.pipeline.verify_webhook`: prose that resolves to nothing, and reads as
though somebody had built it.

## Per dependency, not per extra

"Does this extra have an adapter" is too coarse. `vectors` imports
`qdrant-client` and does not import `sqlite-vec` or `numpy`; calling it backed
hides two unused pins, calling it unbacked erases a real adapter. So each
declared dependency is checked on its own and the extra's status is the summary:

    supported     every dependency is imported by a module here
    partial       some are; `unused` must name the rest and `why` must explain
    unsupported   none are; `why` says what it would take
    tooling       not a capability (dev), exempt

## A declaration is not a requirement

An extra nobody backs is not automatically a bug to fix by writing an adapter.
It is evidence of an intended interface, and the question is whether the
intention still holds. Writing six adapters so twelve declarations look complete
is decorative architecture — the objective is promise integrity, not adapter
count. This script therefore accepts `unsupported` with a stated reason, and
refuses only silence.

## What it refuses

- an extra declared in `[project.optional-dependencies]` and absent from
  `[tool.omnex.extras]`, or the reverse — drift in either direction
- `supported` while a declared dependency is imported nowhere
- `partial` whose `unused` list does not match what was measured
- any non-`supported` status with no reason, or a reason under 40 characters
- a docstring or comment naming `*_adapter.py` that does not exist

Exits non-zero on any of those. It does NOT exit non-zero merely because an
extra is unsupported: unsupported-with-a-reason is an honest state, and a
permanently red build is one people learn to ignore.
"""

from __future__ import annotations

import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
SOURCE = ENGINE / "src" / "omnex"
MANIFEST = ENGINE / "pyproject.toml"

#: Distribution name → the module name it is imported as, where they differ.
#: Only the ones this repository declares; a lookup table nobody maintains would
#: silently mark a real adapter as missing.
IMPORT_NAME = {
    "opentelemetry-api": "opentelemetry",
    "opentelemetry-sdk": "opentelemetry",
    "opentelemetry-exporter-otlp-proto-http": "opentelemetry",
    "prometheus-client": "prometheus_client",
    "sqlite-vec": "sqlite_vec",
    "sentence-transformers": "sentence_transformers",
    "pytest-asyncio": "pytest_asyncio",
    "pytest-cov": "pytest_cov",
}

STATUSES = {"supported", "partial", "unsupported", "tooling"}

#: `pipeline/queue.py` said "Celery is the production path (`celery_adapter.py`)"
#: and that file never existed. Prose that names a module is a claim about the
#: repository, so it is checked like one.
#:
#: The backticks are the rule, not decoration: **a backticked `*_adapter.py` is a
#: claim that the file exists.** Writing about an adapter that does not exist —
#: which both fixed docstrings now do — uses plain words instead. That keeps the
#: check from having to parse negation out of prose, which is exactly the sort of
#: thing that fails quietly in the direction of passing.
_ADAPTER_IN_PROSE = re.compile(r"`([a-z_]+_adapter\.py)`")


@dataclass
class Report:
    problems: list[str] = field(default_factory=list)
    #: extra → {dependency: module that imports it, or ""}
    backing: dict[str, dict[str, str]] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return not self.problems


def _requirement_name(spec: str) -> str:
    """`opentelemetry-sdk>=1.27` → `opentelemetry-sdk`; drop extras and markers."""
    return re.split(r"[><=!~\[;\s]", spec, maxsplit=1)[0].strip()


def importers(root: Path | None = None) -> dict[str, str]:
    """Top-level import name → the first module here that imports it.

    Indented imports count: every lazy `from PIL import Image` inside a function
    is exactly the pattern this codebase uses, and a check that only saw
    module-scope imports would call the whole adapter layer missing.
    """
    base = root or SOURCE
    pattern = re.compile(r"^[ \t]*(?:import|from)[ \t]+([A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE)
    found: dict[str, str] = {}
    for path in sorted(base.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        module = ".".join(path.relative_to(base.parent).with_suffix("").parts)
        for name in pattern.findall(path.read_text(encoding="utf-8", errors="replace")):
            found.setdefault(name, module)
    return found


def prose_adapters(root: Path | None = None) -> list[str]:
    """`*_adapter.py` files named in a docstring or comment that do not exist."""
    base = root or SOURCE
    missing: list[str] = []
    for path in sorted(base.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for named in _ADAPTER_IN_PROSE.findall(text):
            if named == path.name or (path.parent / named).exists():
                continue
            # A path outside the repository is the test's own tree, not a bug;
            # reporting the absolute path there beats raising over the prefix.
            where = path.relative_to(REPO) if path.is_relative_to(REPO) else path
            missing.append(f"{where} names {named}, which does not exist")
    return missing


def check(manifest: dict[str, object], imported: dict[str, str]) -> Report:
    """Compare declared extras with what the code imports, both directions."""
    project: dict[str, object] = manifest.get("project") or {}  # type: ignore[assignment]
    declared: dict[str, list[str]] = project.get("optional-dependencies") or {}  # type: ignore[assignment]
    tool: dict[str, object] = manifest.get("tool") or {}  # type: ignore[assignment]
    described: dict[str, dict[str, object]] = (tool.get("omnex") or {}).get("extras") or {}  # type: ignore[union-attr,assignment]

    report = Report()
    for extra in sorted(set(declared) - set(described)):
        report.problems.append(
            f"{extra} is declared in [project.optional-dependencies] and not in "
            "[tool.omnex.extras] — an install nobody has described"
        )
    for extra in sorted(set(described) - set(declared)):
        report.problems.append(
            f"{extra} is described in [tool.omnex.extras] and is not an extra any "
            "more — a stale entry somebody will read as current"
        )

    for extra, specs in sorted(declared.items()):
        entry = described.get(extra)
        if entry is None:
            continue
        status = str(entry.get("status", ""))
        if status not in STATUSES:
            report.problems.append(
                f"{extra} has status {status!r}; expected one of {', '.join(sorted(STATUSES))}"
            )
            continue

        names = [_requirement_name(spec) for spec in specs]
        backing = {
            name: imported.get(IMPORT_NAME.get(name, name.replace("-", "_")), "") for name in names
        }
        report.backing[extra] = backing
        if status == "tooling":
            continue

        unbacked = sorted(name for name, by in backing.items() if not by)
        report.problems.extend(_status_problems(extra, entry, status, unbacked, len(names)))

    return report


def _status_problems(
    extra: str,
    entry: dict[str, object],
    status: str,
    unbacked: list[str],
    total: int,
) -> list[str]:
    """Where the declared status and the measured backing disagree."""
    problems: list[str] = []
    reason = str(entry.get("why", "")).strip()

    if status == "supported" and unbacked:
        problems.append(
            f"{extra} claims supported, but nothing imports {', '.join(unbacked)} — "
            "installing it delivers a dependency and no capability"
        )
    if status == "partial":
        if not unbacked:
            problems.append(
                f"{extra} claims partial and every dependency is backed; it is supported"
            )
        elif len(unbacked) == total:
            problems.append(f"{extra} claims partial and nothing is backed; it is unsupported")
        else:
            named = sorted(str(name) for name in entry.get("unused") or [])
            if named != unbacked:
                problems.append(
                    f"{extra} lists unused {named} and the measurement says {unbacked} — "
                    "the list drifted from the code"
                )
    if status == "unsupported" and len(unbacked) != total:
        backed = total - len(unbacked)
        problems.append(
            f"{extra} claims unsupported and {backed} of {total} dependencies are "
            "imported; the status understates what exists"
        )
    if status != "supported" and len(reason) < 40:
        problems.append(
            f"{extra} is {status} with no usable reason — without one, the next "
            "reader cannot tell a deliberate placeholder from an oversight"
        )
    return problems


def main() -> int:
    manifest = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
    report = check(manifest, importers())
    described: dict[str, dict[str, object]] = manifest["tool"]["omnex"]["extras"]  # type: ignore[index,assignment]

    by_status: dict[str, list[str]] = {}
    for extra, entry in sorted(described.items()):
        by_status.setdefault(str(entry.get("status", "?")), []).append(extra)
    print(
        "extras   "
        + " · ".join(f"{len(names)} {status}" for status, names in sorted(by_status.items()))
    )
    print()

    width = max((len(e) for e in report.backing), default=0)
    for extra, backing in sorted(report.backing.items()):
        status = str(described[extra].get("status", "?"))
        backed = sum(1 for by in backing.values() if by)
        modules = sorted({by for by in backing.values() if by})
        print(
            f"  {extra:<{width}}  {status:<12} {backed}/{len(backing)} imported"
            + (f"  ← {', '.join(modules)}" if modules else "")
        )

    dead = prose_adapters()
    if dead:
        print()
        for problem in dead:
            print(f"FAIL {problem}")

    if report.problems or dead:
        print()
        for problem in report.problems:
            print(f"FAIL {problem}")
        print(
            f"\n{len(report.problems) + len(dead)} promise(s) the repository makes "
            "and does not keep."
        )
        return 1

    print()
    print(
        "Every extra's status matches what the code imports, and every adapter "
        "named in prose exists. An `unsupported` extra with a stated reason is an "
        "honest placeholder, not a failure — writing adapters so declarations look "
        "complete would be decorative architecture."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
