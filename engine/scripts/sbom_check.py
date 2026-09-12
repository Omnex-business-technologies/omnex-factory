"""Read a generated SBOM back and check it describes the package it claims to.

    python scripts/sbom_check.py <sbom.json> <pyproject.toml>

Generating an SBOM and never reading it back is exactly the trap the
operator's Sovereign Execution Standard names in words: "a tool is not
compliance... a signed artifact is not automatic production security." A file
with the right shape sitting in a CI log proves nothing on its own; this
checks that what `cyclonedx-py` produced actually names the right package at
the right version, rather than trusting the exit code alone.

## What generates the file this checks

`release.yml`'s `build` job runs `cyclonedx-py environment` against a venv
containing ONLY the built package — not the venv that ran `cyclonedx-py`
itself. Scanning the tool's own venv was tried first, here, before this
script existed: `cyclonedx-bom` and its 30-odd transitive dependencies
(`lxml`, `jsonschema`, `packageurl-python`...) all appeared as if they were
citegate's own runtime dependencies, which would have reported this
dependency-free package as depending on a JSON schema validator. `uvx --from
cyclonedx-bom cyclonedx-py ...` runs the tool from an isolated location and
points it at the target venv's interpreter, so only what is actually
installed there is described.
"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path
from typing import Any


def load_sbom(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_package(pyproject: Path) -> tuple[str, str]:
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    project = data["project"]
    return project["name"], project["version"]


def check(sbom: dict[str, Any], name: str, version: str) -> list[str]:
    """Everything wrong with `sbom` as a description of `name` `version`."""
    problems: list[str] = []
    if sbom.get("bomFormat") != "CycloneDX":
        problems.append(f"bomFormat is {sbom.get('bomFormat')!r}, not 'CycloneDX'")
    if not sbom.get("specVersion"):
        problems.append("no specVersion")

    root = sbom.get("metadata", {}).get("component", {})
    if root.get("name") != name:
        problems.append(f"SBOM describes {root.get('name')!r}, not {name!r}")
    if root.get("version") != version:
        problems.append(
            f"SBOM version {root.get('version')!r} does not match pyproject's {version!r}"
        )

    for component in sbom.get("components", []):
        if not component.get("version"):
            problems.append(f"component {component.get('name', '?')!r} has no version")

    return problems


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: sbom_check.py <sbom.json> <pyproject.toml>")
        return 2

    sbom_path, pyproject_path = Path(sys.argv[1]), Path(sys.argv[2])
    sbom = load_sbom(sbom_path)
    name, version = load_package(pyproject_path)
    problems = check(sbom, name, version)

    if problems:
        print(f"the SBOM does not describe {name} {version}:")
        for problem in problems:
            print(f"  FAIL {problem}")
        return 1

    count = len(sbom.get("components", []))
    print(f"SBOM correctly describes {name} {version} ({count} dependency component(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
