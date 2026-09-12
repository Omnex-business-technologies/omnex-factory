"""sbom_check.py: catches an SBOM that does not describe the package it rode in with.

A tool exit code alone is not evidence -- the operator's Sovereign Execution
Standard says so directly ("a signed artifact is not automatic production
security"). These tests exercise the reader against synthetic SBOM payloads
first, then once against a real one this session actually generated with
`cyclonedx-py` against a clean venv containing only citegate, saved as a
fixture so the test suite needs neither network nor a build step to hold the
real shape in place.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE / "scripts"))

import sbom_check  # noqa: E402

FIXTURE = ENGINE / "tests" / "fixtures" / "citegate-sbom.json"


def _sbom(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "metadata": {"component": {"name": "citegate", "version": "0.1.0"}},
        "components": [{"name": "pip", "version": "24.0"}],
    }
    base.update(overrides)
    return base


def test_a_correct_sbom_has_no_problems() -> None:
    assert sbom_check.check(_sbom(), "citegate", "0.1.0") == []


def test_the_wrong_bom_format_is_caught() -> None:
    problems = sbom_check.check(_sbom(bomFormat="SPDX"), "citegate", "0.1.0")
    assert any("bomFormat" in p for p in problems)


def test_a_missing_spec_version_is_caught() -> None:
    problems = sbom_check.check(_sbom(specVersion=""), "citegate", "0.1.0")
    assert any("specVersion" in p for p in problems)


def test_an_sbom_describing_the_wrong_package_is_caught() -> None:
    sbom = _sbom(metadata={"component": {"name": "something-else", "version": "0.1.0"}})
    problems = sbom_check.check(sbom, "citegate", "0.1.0")
    assert any("does not describe" in p or "describes" in p for p in problems)


def test_an_sbom_at_the_wrong_version_is_caught() -> None:
    sbom = _sbom(metadata={"component": {"name": "citegate", "version": "9.9.9"}})
    problems = sbom_check.check(sbom, "citegate", "0.1.0")
    assert any("9.9.9" in p for p in problems)


def test_a_component_with_no_version_is_caught() -> None:
    sbom = _sbom(components=[{"name": "mystery-package"}])
    problems = sbom_check.check(sbom, "citegate", "0.1.0")
    assert any("mystery-package" in p for p in problems)


def test_the_real_fixture_generated_by_cyclonedx_py_passes() -> None:
    """Generated this session: `uv venv` -> `pip install .` (only citegate, no
    other deps -- it declares none) -> `uvx --from cyclonedx-bom cyclonedx-py
    environment` pointed at that venv's interpreter, run from an isolated
    location so the SBOM tool's own dependencies do not appear as citegate's."""
    sbom = sbom_check.load_sbom(FIXTURE)
    problems = sbom_check.check(sbom, "citegate", "0.1.0")
    assert problems == []
    assert sbom["bomFormat"] == "CycloneDX"


def test_main_reports_the_real_package_name_and_version(capsys) -> None:  # type: ignore[no-untyped-def]
    pyproject = ENGINE.parent / "oss" / "citegate" / "pyproject.toml"
    sys_argv = sys.argv
    try:
        sys.argv = ["sbom_check.py", str(FIXTURE), str(pyproject)]
        code = sbom_check.main()
    finally:
        sys.argv = sys_argv
    assert code == 0
    assert "citegate 0.1.0" in capsys.readouterr().out


def test_main_refuses_a_mismatched_sbom(tmp_path, capsys) -> None:  # type: ignore[no-untyped-def]
    pyproject = ENGINE.parent / "oss" / "citegate" / "pyproject.toml"
    bad = json.loads(FIXTURE.read_text())
    bad["metadata"]["component"]["name"] = "not-citegate"
    bad_path = tmp_path / "bad.json"
    bad_path.write_text(json.dumps(bad))

    sys_argv = sys.argv
    try:
        sys.argv = ["sbom_check.py", str(bad_path), str(pyproject)]
        code = sbom_check.main()
    finally:
        sys.argv = sys_argv
    assert code == 1
    assert "FAIL" in capsys.readouterr().out
