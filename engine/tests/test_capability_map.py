"""The capability registry: evidence derived, never typed, and honestly capped.

The risk this file exists to catch is the same one `nodes.json`'s `verified`
guards against one level over: a registry where the interesting field can be
hand-typed always agrees with whoever wrote it.
"""

from __future__ import annotations

import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
sys.path.insert(0, str(ENGINE / "scripts"))

import capability_map  # noqa: E402


def test_every_declared_capability_actually_resolves() -> None:
    """The first, cheapest thing to check: a capability naming a symbol that
    does not import is a claim with no code behind it, and would read E1
    forever -- that is a finding to report, not something to source around."""
    capabilities = capability_map.derive_all()
    declared_only = [c for c in capabilities if not c["resolves"]]
    assert declared_only == [], [
        f"{c['id']} ({c['symbol']}): {c['resolution_failure']}" for c in declared_only
    ]


def test_evidence_level_is_recomputed_not_read() -> None:
    """Deleting every test reference from a capability's own defining logic
    cannot happen from here, but the derivation must be a pure function of the
    current repository -- running it twice must agree with itself."""
    first = capability_map.derive_all()
    second = capability_map.derive_all()
    assert first == second


def test_e5_through_e7_are_never_claimed() -> None:
    """No deployment exists, so nothing here may claim to be operationally
    verified, production verified, or outcome proven -- E5-E7 must never
    appear as a capability's OWN evidence_level, only as the fixed caption on
    every entry explaining why those three are unreachable from a repo scan."""
    capabilities = capability_map.derive_all()
    for cap in capabilities:
        assert cap["evidence_level"] in {
            "E1_DECLARED",
            "E2_CODE_PRESENT",
            "E3_TESTED",
            "E4_INTEGRATED",
        }, f"{cap['id']} claims {cap['evidence_level']}, which this repository cannot observe"


def test_an_integrated_capability_has_a_reference_outside_its_own_test_files() -> None:
    """E4 means a PRODUCTION module uses it, not that its own test file does
    -- test files live under engine/tests/, never under src/, so integrated_by
    entries must all be production paths."""
    capabilities = capability_map.derive_all()
    for cap in capabilities:
        if cap["evidence_level"] == "E4_INTEGRATED":
            assert cap["integrated_by"], cap["id"]
            assert all("src/omnex" in path for path in cap["integrated_by"]), cap["id"]


def test_a_capability_is_not_integrated_by_its_own_defining_file() -> None:
    """A class is not evidence of its own integration -- excluding the
    defining file is what keeps CAP-00X's own module from inflating its count."""
    capabilities = capability_map.derive_all()
    for cap in capabilities:
        module_path = cap["symbol"].rsplit(".", 1)[0]
        own_file = module_path.replace(".", "/") + ".py"
        assert own_file not in cap["integrated_by"], cap["id"]


def test_the_committed_document_agrees_with_the_repository() -> None:
    """The whole point. If this fails, regenerate -- never hand-edit the file."""
    committed = capability_map.OUTPUT.read_text(encoding="utf-8")
    regenerated = capability_map.render(capability_map.derive_all())
    assert committed == regenerated


def test_the_document_names_its_own_generator_and_forbids_editing() -> None:
    committed = capability_map.OUTPUT.read_text(encoding="utf-8")
    assert "capability_map.py" in committed
    assert "Do not edit" in committed


def test_every_capability_states_dependencies_and_risks() -> None:
    """The standard's minimum field set. A blank field would pass json.loads
    and fail every reader who actually needed the answer."""
    for entry in capability_map.load():
        assert entry["description"].strip()
        assert entry["contract"].strip()
        assert entry["limitations"].strip()
        assert entry["known_risks"].strip()
        assert entry["economic_relevance"].strip()
        assert isinstance(entry["dependencies"], list)
        assert isinstance(entry["security_requirements"], list)


def test_capability_ids_are_unique_and_sequential() -> None:
    ids = [entry["id"] for entry in capability_map.load()]
    assert ids == [f"CAP-{i:03d}" for i in range(1, len(ids) + 1)]
