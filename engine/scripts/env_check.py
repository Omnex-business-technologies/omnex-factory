"""What a deploy cannot run without, and whether this host has it.

    python scripts/env_check.py            # the manifest agrees with the code
    python scripts/env_check.py --runtime  # ...and this machine has what it needs

Twenty-eight variables, no `.env.example`, and nothing saying which of them
matter. Almost all of them **fail closed** — `cron-auth` returns false when
`CRON_SECRET` is unset, `isOwner` refuses below sixteen characters, the Stripe
routes answer 503. That is the correct direction and exactly why the failure is
invisible: the site is up, the pages render, and the feature is simply never
reachable. One missing value is quietly half the product.

## Two modes, because one would be permanently red

The default mode compares `deploy/env.json` with the code and **never looks at
the environment**. It is the mode CI runs, where none of these are set and a
strict check would fail on every run until people stopped reading it.
`--runtime` is the operator's mode, on the host that is about to serve.

## Drift is checked in both directions

A variable the code reads and the manifest does not list is an undocumented
requirement. An entry in the manifest the code no longer reads is a stale
instruction somebody will follow. `test_ci_contract.py` makes exactly this
argument about the gate block, and its stated boundary applies here too: this
compares two sides and cannot see a variable that is missing from **both** — one
read through a computed name, say. Nothing here would catch that.

## No value is ever printed

Not to stdout, not on failure, not truncated. A preflight that prints a key to a
build log has not verified the secret, it has copied it somewhere new. The report
says set or unset, and for a secret it says nothing else at all.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
MANIFEST = REPO / "deploy" / "env.json"
sys.path.insert(0, str(ENGINE / "src"))
sys.path.insert(0, str(ENGINE / "scripts"))

#: Where the app reads its configuration from. Scripts included: a one-off that
#: needs a key needs it documented as much as a request handler does.
SOURCES = ("lib", "app", "scripts", "components")

_USED = re.compile(r"process\.env\.([A-Z][A-Z0-9_]*)")


@dataclass(frozen=True)
class Report:
    used_but_undocumented: list[str]
    documented_but_unused: list[str]
    missing_required: list[str]
    unsatisfied_groups: list[str]

    @property
    def manifest_drifted(self) -> bool:
        return bool(self.used_but_undocumented or self.documented_but_unused)

    @property
    def host_incomplete(self) -> bool:
        return bool(self.missing_required or self.unsatisfied_groups)


def used_in_code(root: Path | None = None) -> set[str]:
    """Every `process.env.NAME` the TypeScript actually reads."""
    base = root or REPO
    found: set[str] = set()
    for source in SOURCES:
        directory = base / source
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if path.suffix not in {".ts", ".tsx"} or "node_modules" in path.parts:
                continue
            found.update(_USED.findall(path.read_text(encoding="utf-8", errors="replace")))
    return found


def load_manifest(path: Path | None = None) -> dict[str, object]:
    return json.loads((path or MANIFEST).read_text(encoding="utf-8"))


def check(
    manifest: dict[str, object],
    used: set[str],
    environment: dict[str, str] | None = None,
) -> Report:
    """Compare the manifest with the code, and optionally with a real environment.

    `environment` is passed in rather than read here so the runtime half is
    testable without setting variables in the test process, which would leak
    into every test that runs after it.
    """
    documented: dict[str, dict[str, object]] = manifest.get("vars") or {}  # type: ignore[assignment]
    groups: dict[str, dict[str, object]] = manifest.get("groups") or {}  # type: ignore[assignment]

    missing_required: list[str] = []
    unsatisfied: list[str] = []
    if environment is not None:
        missing_required = sorted(
            name
            for name, entry in documented.items()
            if entry.get("required") and not (environment.get(name) or "").strip()
        )
        for label, group in sorted(groups.items()):
            options: list[str] = list(group.get("any_of") or [])  # type: ignore[arg-type]
            if options and not any((environment.get(name) or "").strip() for name in options):
                unsatisfied.append(f"{label}: none of {', '.join(sorted(options))} is set")

    return Report(
        used_but_undocumented=sorted(used - set(documented)),
        documented_but_unused=sorted(set(documented) - used),
        missing_required=missing_required,
        unsatisfied_groups=unsatisfied,
    )


def n8n_environment() -> dict[str, list[str]]:
    """The n8n host's variables, derived from the binding catalogue.

    Not listed in `deploy/env.json` on purpose. A second copy of a list that is
    already data drifts the moment a binding changes a flag, and this one cannot.
    """
    import n8n_bindings_check

    from omnex.factory.compile import bindings

    catalogue = bindings.load(ENGINE / "ontology" / "n8n_bindings.json")
    return n8n_bindings_check.required_env(catalogue)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the environment manifest, and the host.")
    parser.add_argument(
        "--runtime",
        action="store_true",
        help="also check THIS machine's environment; for an operator, not for CI",
    )
    args = parser.parse_args()

    manifest = load_manifest()
    used = used_in_code()
    documented: dict[str, dict[str, object]] = manifest.get("vars") or {}  # type: ignore[assignment]
    report = check(manifest, used, dict(os.environ) if args.runtime else None)

    required = sorted(n for n, e in documented.items() if e.get("required"))
    secrets = sum(1 for e in documented.values() if e.get("secret"))
    print(
        f"app      {len(documented)} variable(s) documented, {len(required)} required, "
        f"{secrets} secret"
    )

    for name, refs in sorted(n8n_environment().items()):
        print(f"n8n      {name:<24} {', '.join(refs)}")

    if report.manifest_drifted:
        print()
        for name in report.used_but_undocumented:
            print(f"FAIL {name} is read by the code and is not in deploy/env.json")
        for name in report.documented_but_unused:
            print(f"FAIL {name} is in deploy/env.json and nothing reads it any more")
        return 1

    print()
    print("The manifest and the code agree in both directions.")

    if not args.runtime:
        print(
            "Nothing above looked at this machine's environment. Run --runtime on "
            "the host that is about to serve; here, none of these are set and a "
            "strict check would be red on every run until people stopped reading it."
        )
        return 0

    print()
    for name in required:
        # Set or unset. Never the value, never a prefix of it, never a length.
        state = "set" if (os.environ.get(name) or "").strip() else "UNSET"
        print(f"  {name:<32} {state}")

    if report.host_incomplete:
        print()
        for name in report.missing_required:
            entry = documented[name]
            print(f"FAIL {name} is unset — {entry.get('why', 'required')}")
        for problem in report.unsatisfied_groups:
            print(f"FAIL {problem}")
        return 1

    print()
    print("Every required variable is set on this host.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
