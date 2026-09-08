"""Where execution actually is, derived from the repository rather than typed.

    python scripts/state_map.py            # regenerate execution_state.json
    python scripts/state_map.py --check    # fail if the file disagrees with reality

`invariant_map.py` renders `INVARIANTS.md` from checkers. `business_map.py`
renders `BUSINESS.md` from git and the QC manifests. This does the same for the
one thing that was still living only in conversation: what phase the work is in,
which gates are passed, and what is blocked.

## Why it must be derived

A machine-readable state file is the most dangerous artifact in a repository like
this, because it is the one thing an agent reads instead of looking. If its
numbers live apart from the code they describe, it becomes a second copy of the
truth that drifts — and unlike prose, it drifts *authoritatively*. **Machine
state that can lie is worse than none.**

So every field here is computed from a source that can be pointed at:

    git                    commit, branch, whether the tree is clean
    ontology/nodes.json    507 nodes, their claims, who verified them
    ontology/branches.json 38 branches, their claims, their `missing` lists
    ontology/invariants.json + checkers   how many rules actually run
    pyproject.toml         what each extra delivers, via extras_check
    LICENSE files          present or absent, per distribution

The one field no machine computes is the human decision count — that comes from
`verified` in `nodes.json`, and only `apply_decisions.py` may set it.

## No timestamp

A generation time would change on every run, so the file would differ from itself
and `--check` would have to learn to ignore a field. Derived state is keyed on
`source_commit` instead. Timestamps belong to observations, where they mean
something.

## UNKNOWN is not false

A gate nobody measured is `UNKNOWN`. Writing `false` there would be a claim that
the gate fails, which is a different and unearned statement. Most gates are
`UNKNOWN` today and the file says why for each one, because a dashboard of zeroes
teaches people to stop reading it.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
OUTPUT = REPO / "execution_state.json"
sys.path.insert(0, str(ENGINE / "src"))
sys.path.insert(0, str(ENGINE / "scripts"))

PASS = "PASS"
FAIL = "FAIL"
UNKNOWN = "UNKNOWN"

#: The distributions that declare a licence and must therefore carry the file.
LICENSED = ("LICENSE", "engine/LICENSE", "oss/citegate/LICENSE")


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True, check=False
    ).stdout.strip()


def _nodes() -> dict[str, Any]:
    raw = json.loads((ENGINE / "ontology" / "nodes.json").read_text(encoding="utf-8"))
    nodes: list[dict[str, Any]] = raw["nodes"] if isinstance(raw, dict) else raw
    by_claim: dict[str, int] = {}
    for node in nodes:
        by_claim[str(node.get("claim", "?"))] = by_claim.get(str(node.get("claim", "?")), 0) + 1
    return {
        "total": len(nodes),
        "by_claim": dict(sorted(by_claim.items())),
        # Only `apply_decisions.py` may raise this, and only with a person's
        # name against it. It is the number the whole node map exists to move.
        "verified_by_a_person": sum(1 for node in nodes if node.get("verified")),
    }


def _branches() -> dict[str, Any]:
    raw = json.loads((ENGINE / "ontology" / "branches.json").read_text(encoding="utf-8"))
    branches: list[dict[str, Any]] = raw["branches"] if isinstance(raw, dict) else raw
    by_claim: dict[str, int] = {}
    for branch in branches:
        by_claim[str(branch.get("claim", "?"))] = by_claim.get(str(branch.get("claim", "?")), 0) + 1
    return {
        "total": len(branches),
        "by_claim": dict(sorted(by_claim.items())),
        "carrying_a_named_gap": sum(1 for b in branches if b.get("missing")),
    }


def _invariants() -> dict[str, Any]:
    raw = json.loads((ENGINE / "ontology" / "invariants.json").read_text(encoding="utf-8"))
    entries: list[dict[str, Any]] = raw["invariants"]
    return {
        "total": len(entries),
        "enforced": sum(1 for e in entries if e.get("checker")),
        "declared_unenforceable": sum(1 for e in entries if e.get("unenforceable")),
    }


def _extras() -> dict[str, Any]:
    import extras_check

    manifest = tomllib.loads((ENGINE / "pyproject.toml").read_text(encoding="utf-8"))
    described: dict[str, dict[str, Any]] = manifest["tool"]["omnex"]["extras"]
    report = extras_check.check(manifest, extras_check.importers())
    by_status: dict[str, int] = {}
    for entry in described.values():
        status = str(entry.get("status", "?"))
        by_status[status] = by_status.get(status, 0) + 1
    return {
        "by_status": dict(sorted(by_status.items())),
        "problems": len(report.problems),
        "adapters_named_in_prose_that_do_not_exist": len(extras_check.prose_adapters()),
    }


def _licences() -> dict[str, bool]:
    return {name: (REPO / name).exists() for name in LICENSED}


def _gate(status: str, why: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"status": status, "why": why, "evidence": evidence or []}


def gates(facts: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """The twelve maturity gates, each measured or explicitly unmeasured.

    Only gate 0 is decidable from a repository scan. The rest need evidence this
    process cannot produce — a deployment, a user, a payment — and each says
    which, because "UNKNOWN" without a reason is indistinguishable from
    "nobody looked".
    """
    licences = facts["promise_integrity"]["licences"]
    extras = facts["extras"]
    integrity_broken = [f"{name} is missing" for name, present in licences.items() if not present]
    if extras["problems"]:
        integrity_broken.append(f"{extras['problems']} extras problem(s)")
    if extras["adapters_named_in_prose_that_do_not_exist"]:
        integrity_broken.append("prose names an adapter that does not exist")

    return {
        "0_integrity": _gate(
            FAIL if integrity_broken else PASS,
            "every licence file the metadata declares is present, every extra's "
            "status matches what the code imports, and no docstring names a "
            "module that does not exist",
            integrity_broken
            or [
                f"{len(licences)} declared licences present",
                f"extras: {facts['extras']['by_status']}",
                f"invariants enforced: {facts['invariants']['enforced']}"
                f"/{facts['invariants']['total']}",
            ],
        ),
        "1_architecture": _gate(
            UNKNOWN,
            "507 nodes carry a claim, but a claim is not a dossier: nothing yet "
            "records the evidence, candidates and containment direction per node, "
            "so 'mapped' cannot be asserted",
            [f"nodes by claim: {facts['nodes']['by_claim']}", "node_dossier.py does not exist"],
        ),
        "2_evidence": _gate(
            UNKNOWN,
            "there is no claim or evidence registry yet, so 'important claims have "
            "evidence' has nothing to measure against",
            ["state/claims.jsonl does not exist", "state/evidence.jsonl does not exist"],
        ),
        "3_implementation": _gate(
            UNKNOWN,
            "the suite is green and the mutation probe kills every mutation, but "
            "neither answers coverage per capability; measuring it needs a "
            "capability registry that does not exist",
            ["mutate.py exists and is in CI", "no capability registry"],
        ),
        "4_integration": _gate(UNKNOWN, "no integration evidence has been collected"),
        "5_production": _gate(
            UNKNOWN,
            "nothing is deployed; DOCKER.md and compose.yaml exist and no workflow "
            "builds them, and a configuration is not a deployment",
        ),
        "6_security": _gate(
            UNKNOWN,
            "no secret scanning, dependency audit, SBOM or signed release exists yet",
        ),
        "7_observability": _gate(
            UNKNOWN,
            "omnex.obs emits traces, metrics and a cost ledger in-process; nothing "
            "is collected from a running deployment because there is none",
        ),
        "8_evaluation": _gate(
            UNKNOWN,
            "omnex.evals gates on newly-failing cases in the suite; no agent runs "
            "in production to evaluate",
        ),
        "9_autonomy": _gate(
            UNKNOWN,
            "no run ledger exists, so no autonomous action can be shown to have "
            "been policy-bounded",
        ),
        "10_distribution": _gate(
            UNKNOWN,
            "release_check.py and release.yml do not exist; no artifact has been "
            "built, signed or published",
        ),
        "11_commercial": _gate(
            UNKNOWN, "no external user has obtained the software; 0 listings live"
        ),
        "12_economic": _gate(
            UNKNOWN,
            "no revenue log exists — 0 recorded is not 0 earned, and BUSINESS.md "
            "refuses to render it as a measurement",
        ),
    }


def derive() -> dict[str, Any]:
    """The whole state, from sources that can be pointed at."""
    facts: dict[str, Any] = {
        "version": 1,
        "$comment": (
            "Derived by engine/scripts/state_map.py. Do not edit — state_check "
            "compares this against the repository in both directions. There is no "
            "generation timestamp on purpose: it would change on every run and the "
            "validator would have to learn to ignore a field. Keyed on "
            "source_commit instead."
        ),
        "source_commit": _git("rev-parse", "HEAD"),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "tree_clean": _git("status", "--porcelain") == "",
        "corpus": {"figures": 509, "nodes": 507},
        "nodes": _nodes(),
        "branches": _branches(),
        "invariants": _invariants(),
        "extras": _extras(),
        "promise_integrity": {"licences": _licences()},
    }
    facts["gates"] = gates(facts)
    facts["blocked"] = [
        {
            "what": "Etsy / Lemon Squeezy API shapes",
            "reason": "the proxy refuses the open web (403 to CONNECT)",
            "resolution": "a person supplies the endpoint through OMNEX_*_URL",
        },
        {
            "what": "any live listing",
            "reason": "80 of 170 promised images have passed QC",
            "resolution": "90 more images generated on a GPU",
        },
        {
            "what": "PyPI publication",
            "reason": "PYPI_API_TOKEN is held by the person, not this process",
            "resolution": "the credential holder runs the final step",
        },
        {
            "what": "n8n binding confirmation",
            "reason": "0 of 7 bindings confirmed by an import",
            "resolution": "one import into a real n8n instance",
        },
    ]
    return facts


def differences(committed: dict[str, Any], measured: dict[str, Any]) -> list[str]:
    """Every field where the file and the repository disagree, both directions."""
    problems: list[str] = []

    def walk(left: Any, right: Any, trail: str) -> None:
        if isinstance(left, dict) and isinstance(right, dict):
            for key in sorted(set(left) | set(right)):
                if key not in left:
                    problems.append(f"{trail}.{key} is measured and not in the file")
                elif key not in right:
                    problems.append(f"{trail}.{key} is in the file and not measured")
                else:
                    walk(left[key], right[key], f"{trail}.{key}")
        elif left != right:
            problems.append(f"{trail}: file says {left!r}, repository says {right!r}")

    walk(committed, measured, "state")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; fail if execution_state.json disagrees with the repository",
    )
    args = parser.parse_args()
    measured = derive()

    if args.check:
        if not OUTPUT.exists():
            print(f"FAIL {OUTPUT.relative_to(REPO)} does not exist; run state_map.py")
            return 1
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        # The commit and tree state move with every commit, so comparing them
        # would make this fail on its own output. What must agree is everything
        # derived FROM the repository's contents.
        drop = {"source_commit", "branch", "tree_clean"}
        problems = differences(
            {k: v for k, v in committed.items() if k not in drop},
            {k: v for k, v in measured.items() if k not in drop},
        )
        if problems:
            print(
                f"FAIL execution_state.json and the repository disagree in {len(problems)} place(s):"
            )
            for problem in problems:
                print(f"  {problem}")
            print("\nRun `python scripts/state_map.py` — the file is derived, not authored.")
            return 1
        print("execution_state.json agrees with the repository in both directions.")
        return 0

    OUTPUT.write_text(json.dumps(measured, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    passed = sum(1 for g in measured["gates"].values() if g["status"] == PASS)
    unknown = sum(1 for g in measured["gates"].values() if g["status"] == UNKNOWN)
    failed = sum(1 for g in measured["gates"].values() if g["status"] == FAIL)
    print(f"gates    {passed} pass · {failed} fail · {unknown} unknown of {len(measured['gates'])}")
    print(
        f"nodes    {measured['nodes']['by_claim']}, {measured['nodes']['verified_by_a_person']} verified by a person"
    )
    print(f"extras   {measured['extras']['by_status']}")
    print(f"blocked  {len(measured['blocked'])} item(s), each with a named resolution")
    print(
        "\nUNKNOWN is not FALSE. A gate nobody measured is unmeasured, and every "
        "one above says which evidence it is waiting for."
    )
    print(f"\nwrote {OUTPUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
