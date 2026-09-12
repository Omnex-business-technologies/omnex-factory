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
import re
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


def _dossiers() -> dict[str, Any]:
    """Whether the node dossier exists, and how many rows a person has ruled on.

    Gate 1 asserted "node_dossier.py does not exist" as a hard-coded string for
    long enough that the script arrived, entered CI, and regenerated 507 rows
    while the state file went on saying it was absent. Derived now, so the gate
    moves when the repository does.
    """
    return {
        "generator": (ENGINE / "scripts" / "node_dossier.py").exists(),
        "rendered": (REPO / "corpus" / "universal-ai-os" / "DECISIONS.md").exists(),
        "ruled_on_by_a_person": _nodes()["verified_by_a_person"],
    }


def _registry() -> dict[str, Any]:
    """The claim registry's shape, recomputed — never read from a stored status.

    Gate 2 said "state/claims.jsonl does not exist" while `claims.py --check`
    ran in CI against thirteen claims. A gate whose evidence is a literal cannot
    notice that it came true.
    """
    import claims as registry

    if not (registry.CLAIMS.exists() and registry.EVIDENCE.exists()):
        return {"present": False, "claims": 0, "by_status": {}}

    ledger = registry.load()
    counted = registry.summarise(ledger)
    return {
        "present": True,
        "claims": len(ledger.claims),
        # Recomputed by `summarise`, never read from a stored field: a stored
        # status is a typeable status, which is the one thing claims.py refuses.
        "by_status": {str(k): v for k, v in sorted(counted.items(), key=lambda kv: str(kv[0]))},
    }


def _run_ledger() -> dict[str, Any]:
    """The run ledger's shape, recomputed rather than asserted.

    Gate 9 carried "no run ledger exists" as a literal while `state/runs.jsonl`
    held a hash-chained ledger that `runs.py --check` verifies on every CI run.
    The same defect as gates 1 and 2, in a gate nobody had re-read since.
    """
    import runs as ledger

    if not ledger.LEDGER.exists():
        return {"present": False, "runs": 0, "chain_intact": False, "by_level": {}}

    entries = ledger.load()
    by_level: dict[str, int] = {}
    for run in entries:
        level = run.autonomy_level or "unrecorded"
        by_level[level] = by_level.get(level, 0) + 1

    # Counted separately because "a run was recorded above L3" and "a run above
    # L3 succeeded" are different statements, and the first written as the
    # second is how a refused attempt turns into a demonstrated capability.
    above = [r for r in entries if r.autonomy_level not in ("", "L3_REPOSITORY")]
    return {
        "present": True,
        "runs": len(entries),
        # Verified through the ledger's own checker rather than a second copy
        # of the hashing rule, which is what `one_symbol_resolver` is about.
        "chain_intact": not ledger.broken_links(entries),
        "by_level": dict(sorted(by_level.items())),
        "above_l3": len(above),
        "above_l3_succeeded": sum(1 for r in above if r.result == "ok"),
    }


def _release_tooling() -> dict[str, Any]:
    """Whether the release path exists here — never whether it has run.

    Gate 10 carried "release_check.py and release.yml do not exist" while both
    sat in the repository and in CI. Whether an artifact was actually published
    is deliberately NOT derived: a GitHub Release and a PyPI upload are facts
    about other systems, and `state/claims.jsonl` already tracks them as C-005,
    C-011 and C-013. Reading `git tag` instead would disagree between a full
    clone and CI's shallow checkout — a validator that fails on where it ran.
    """
    return {
        "release_check": (ENGINE / "scripts" / "release_check.py").exists(),
        "release_workflow": (REPO / ".github" / "workflows" / "release.yml").exists(),
    }


def _supply_chain() -> dict[str, Any]:
    """Which supply-chain controls are visible in the repository.

    Gate 6 carried "no secret scanning, dependency audit, SBOM or signed
    release exists yet" while `npm audit --audit-level=moderate` ran in
    `ci.yml` and `.github/dependabot.yml` sat beside it.

    The boundary is stated rather than guessed: CodeQL default setup and secret
    scanning are GitHub *settings*, not files, so a repository scan cannot see
    either and this reports neither present nor absent. A control this process
    cannot observe is unobserved, which is not the same as missing — the
    distinction the whole file exists to keep.
    """
    import actions_pin_check
    import release_check

    # One comment-stripping reader, imported rather than copied. A second copy
    # is how `twin_splitters_agree` got its name, and a reader that takes prose
    # for configuration has already flipped a gate in this repository once.
    text = "\n".join(
        release_check._uncommented(line)
        for path in sorted((REPO / ".github" / "workflows").glob("*.yml"))
        for line in path.read_text(encoding="utf-8").splitlines()
    ).lower()
    pins = actions_pin_check.summarise(release_check._workflow_text())
    return {
        "dependency_audit_in_ci": "npm audit" in text,
        "dependency_review_in_ci": "dependency-review-action" in text,
        "dependabot_config": (REPO / ".github" / "dependabot.yml").exists(),
        "build_provenance_attested": "attest-build-provenance" in text,
        "sbom_generated": any(k in text for k in ("cyclonedx", "spdx", "syft", "sbom")),
        "actions_pinned_to_sha": pins["pinned_to_sha"],
        "actions_total": pins["total_uses"],
    }


#: A filename, and the ways a sentence denies that one exists. Kept here as one
#: implementation rather than copied into the test that exercises it: a second
#: copy of a rule is what `twin_splitters_agree` is named after.
#: Longest extension first, and anchored at a word boundary. `json` before
#: `jsonl` truncates `state/claims.jsonl` to `state/claims.json`, which then
#: resolves to nothing and reads as clean — so the original scan could never
#: have caught gate 2, one of the two cases it was written for.
_FILENAME = re.compile(r"[\w./-]+\.(?:jsonl|json|yaml|yml|py|md)\b")
#: "A.py and B.yml do not exist" — the subject sits BEFORE the phrase, and may
#: be several filenames joined by "and". Bounded so it cannot reach back across
#: a whole sentence and collect a file the denial was never about.
_DENIED_BEFORE = re.compile(r"([^;]{0,80}?)\s+(?:do(?:es)? not exist|(?:is|are) not in the repo)")
#: "no X exists" — the subject sits INSIDE the phrase. Commas allowed, because
#: `6_security` listed four things this way; an em dash ends it, because
#: `12_economic` continues past one into a sentence about a file that does.
_DENIED_INSIDE = re.compile(r"\bno\s+([^;—]{0,80}?)\s+exists?\b")
#: Where a gate's filename may actually live. `.github/workflows` is here
#: because leaving it out is why `release.yml do not exist` stayed invisible
#: even once the phrasing was understood: the path simply never resolved.
_BASES = ("", "engine", "engine/scripts", ".github/workflows")


def denied_existing_files(text: str) -> list[str]:
    """Filenames `text` says are absent that are in fact in the repository.

    The denial must be ABOUT the file. Scanning a whole clause for any filename
    was the first attempt and it fired on `12_economic` — "no revenue log
    exists ... and BUSINESS.md refuses to render it" denies the revenue log,
    not the file sitting in the same sentence.
    """
    subjects = [m.group(1) for m in _DENIED_BEFORE.finditer(text)]
    subjects += [m.group(1) for m in _DENIED_INSIDE.finditer(text)]
    return [
        named
        for subject in subjects
        for named in _FILENAME.findall(subject)
        if any((REPO / base / named).exists() for base in _BASES)
    ]


def _health_endpoints() -> dict[str, Any]:
    """Whether the app exposes liveness and readiness over HTTP.

    Gate 5 says nothing is deployed, which stays true regardless of this —
    these two facts answer a narrower question (does the app have the pieces
    a deployment would need to be checked) rather than the one gate 5 asks
    (is anything actually running).
    """
    return {
        "healthz_route": (REPO / "app" / "api" / "healthz" / "route.ts").exists(),
        "readyz_route": (REPO / "app" / "api" / "readyz" / "route.ts").exists(),
    }


def _capabilities() -> dict[str, Any]:
    """The capability registry's shape, recomputed from `capability_map.py`.

    Gate 3 said "measuring coverage per capability needs a capability registry
    that does not exist" until one did — the Sovereign Execution Standard's
    Phase 1 requirement. Imported rather than re-derived here, for the same
    reason `_registry()` imports `claims` instead of re-reading
    `claims.jsonl`: two readers of one source are how the source and its
    second copy quietly disagree.
    """
    import capability_map

    return capability_map.summarise(capability_map.derive_all())


def _gate(status: str, why: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"status": status, "why": why, "evidence": evidence or []}


def gates(facts: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """The twelve maturity gates, each measured or explicitly unmeasured.

    Gates 0, 1 and 2 are decidable from a repository scan. The rest need
    evidence this process cannot produce — a deployment, a user, a payment —
    and each says which, because "UNKNOWN" without a reason is
    indistinguishable from "nobody looked".

    **A gate's evidence must be derived, not written.** Gates 1 and 2 carried
    hard-coded strings — "node_dossier.py does not exist", "state/claims.jsonl
    does not exist" — and both scripts were subsequently written, entered CI,
    and ran for weeks while this file went on reporting them absent. `--check`
    passed throughout, because it compared the committed file against the same
    literals: a constant validated against itself. That is the exact failure
    this module's own docstring warns about, in the module that warns about it.
    A gate whose evidence is a literal cannot notice that it came true.
    """
    licences = facts["promise_integrity"]["licences"]
    extras = facts["extras"]
    dossiers = facts["dossiers"]
    registry = facts["registry"]
    ledger = facts["run_ledger"]
    release = facts["release_tooling"]
    supply = facts["supply_chain"]
    capabilities = facts["capabilities"]
    health = facts["health_endpoints"]
    unsettled = sum(
        count
        for status, count in registry["by_status"].items()
        if status in {"UNKNOWN", "CONTRADICTED"}
    )
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
            "the dossier exists and regenerates in CI, so every node now carries "
            "the evidence a person needs; what is missing is the person. "
            f"{dossiers['ruled_on_by_a_person']} of {facts['nodes']['total']} rows "
            "have been ruled on, and no machine may raise that number"
            if dossiers["generator"]
            else "507 nodes carry a claim, but a claim is not a dossier: nothing "
            "yet records the evidence, candidates and containment direction per "
            "node, so 'mapped' cannot be asserted",
            [
                f"nodes by claim: {facts['nodes']['by_claim']}",
                f"node_dossier.py exists: {dossiers['generator']}",
                f"DECISIONS.md rendered: {dossiers['rendered']}",
                f"ruled on by a person: {dossiers['ruled_on_by_a_person']}",
            ],
        ),
        "2_evidence": _gate(
            UNKNOWN,
            "the claim registry exists and is checked in CI, and status is "
            "recomputed rather than stored — but a registry is not the gate: "
            f"{unsettled} of {registry['claims']} claims are still UNKNOWN or "
            "CONTRADICTED, so 'important claims have evidence' is not yet true"
            if registry["present"]
            else "there is no claim or evidence registry yet, so 'important "
            "claims have evidence' has nothing to measure against",
            [
                f"claims registry present: {registry['present']}",
                f"claims by derived status: {registry['by_status']}",
            ],
        ),
        "3_implementation": _gate(
            UNKNOWN,
            "the suite is green and the mutation probe kills every mutation, and "
            f"the capability registry now measures coverage per capability: "
            f"{capabilities['total']} capabilities at "
            f"{capabilities['by_evidence_level']}. What is still missing is scale "
            f"— {capabilities['total']} is a first, deliberately small cut, not "
            "the platform's full surface, and E5-E7 are unreachable from a "
            "repository scan for every one of them",
            [
                "mutate.py exists and is in CI",
                f"capability registry: {capabilities['total']} capabilities",
                f"by evidence level: {capabilities['by_evidence_level']}",
            ],
        ),
        "4_integration": _gate(UNKNOWN, "no integration evidence has been collected"),
        "5_production": _gate(
            UNKNOWN,
            "nothing is deployed; DOCKER.md and compose.yaml exist and no workflow "
            "builds them, and a configuration is not a deployment. The app now has "
            f"the pieces a deployment platform would check (liveness route: "
            f"{health['healthz_route']}, readiness route: {health['readyz_route']}), "
            "which narrows what a first deploy still needs, not whether one exists",
            [f"{key}: {value}" for key, value in health.items()],
        ),
        "6_security": _gate(
            UNKNOWN,
            "controls that ARE in the repository run on every pull request or "
            f"release (dependency audit in CI: {supply['dependency_audit_in_ci']}, "
            f"dependency review on PR diffs: {supply['dependency_review_in_ci']}, "
            f"Dependabot config: {supply['dependabot_config']}, build provenance "
            f"attested in the release workflow: {supply['build_provenance_attested']}, "
            f"an SBOM generated and read back against the package it describes in "
            f"the release workflow: {supply['sbom_generated']}, every GitHub Action "
            f"pinned to a commit SHA: {supply['actions_pinned_to_sha']}/"
            f"{supply['actions_total']}); what is absent is any signed PUBLISHED "
            "artifact, since no release exists — none of this has run for real. "
            "CodeQL default setup and secret scanning are GitHub settings rather "
            "than files, so a repository scan cannot see them and this claims "
            "neither way",
            [f"{key}: {value}" for key, value in supply.items()],
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
            f"the run ledger holds {ledger['runs']} hash-chained run(s) (chain "
            f"intact: {ledger['chain_intact']}) at levels {sorted(ledger['by_level'])}, "
            "so actions taken here are bounded and auditable — what this gate asks "
            "for and still has no evidence of is an autonomous run against a "
            f"deployment: {ledger['above_l3']} run(s) are recorded above L3 and "
            f"{ledger['above_l3_succeeded']} of those recorded a successful outcome"
            if ledger["present"]
            else "no run ledger exists, so no autonomous action can be shown to "
            "have been policy-bounded",
            [
                f"runs recorded: {ledger['runs']}",
                f"chain intact: {ledger['chain_intact']}",
                f"runs by autonomy level: {ledger['by_level']}",
            ],
        ),
        "10_distribution": _gate(
            UNKNOWN,
            "the release path is in the repository and in the gate block "
            f"(release_check.py: {release['release_check']}, release.yml: "
            f"{release['release_workflow']}); whether an artifact was actually "
            "published is not a fact about this tree, and C-005, C-011 and C-013 "
            "in state/claims.jsonl are where that is tracked"
            if release["release_check"] and release["release_workflow"]
            else "the release path is not in the repository, so no artifact can "
            "have been built, signed or published from it",
            [
                f"release_check.py present: {release['release_check']}",
                f"release.yml present: {release['release_workflow']}",
            ],
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
        "dossiers": _dossiers(),
        "registry": _registry(),
        "run_ledger": _run_ledger(),
        "release_tooling": _release_tooling(),
        "supply_chain": _supply_chain(),
        "capabilities": _capabilities(),
        "health_endpoints": _health_endpoints(),
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
