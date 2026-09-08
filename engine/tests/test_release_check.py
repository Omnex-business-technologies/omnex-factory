"""The release gate, and the five defects that running it on a second target found.

Four of the five were in the gate itself. That is the point of this file: a check
nobody has tried to break is a check with an unknown failure mode, and
`release_check.py` shipped its first version reporting thirteen refusals against
`engine` of which thirteen were false.

The worst of them is `test_a_job_inherits_the_workflow_working_directory`. The
check written to find suites CI does not run could not see the suite CI does run,
and it was *right about citegate* — by coincidence of the same bug. A gate that
returns the right answer for the wrong reason is indistinguishable from a working
one until a second target exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ENGINE = REPO / "engine"
sys.path.insert(0, str(ENGINE / "scripts"))

import release_check  # noqa: E402
from release_check import Findings, Package, Target  # noqa: E402


def _package(root: Path, manifest: dict[str, object], package: str = "thing") -> Package:
    return Package(
        name="thing",
        target=Target(
            path=root.relative_to(REPO) if root.is_relative_to(REPO) else root, package=package
        ),
        manifest=manifest,
    )


def _module(root: Path, name: str, body: str) -> Path:
    """Write one module inside a `src/<name>/` tree and return the source root."""
    source = root / "src" / name
    source.mkdir(parents=True, exist_ok=True)
    (source / "__init__.py").write_text(body, encoding="utf-8")
    return root / "src"


# ── bug 2: prose read as an import ────────────────────────────────────────
def test_a_docstring_that_looks_like_an_import_is_not_one(tmp_path: Path) -> None:
    """The regex borrowed from `extras_check` reported imports of `a` and `the`.

    Safe there: that scanner is only ever asked whether a *declared* name appears,
    so a false positive is never looked up. Read as a source of truth it produced
    `imports a`, `imports free`, `imports the` and `imports zero` against the
    engine — four sentences out of four docstrings.
    """
    source = _module(
        tmp_path,
        "thing",
        '"""Zero dependencies.\n\n'
        "    A caller may import a module of its own, or import the adapter, and\n"
        "    from enum import StrEnum is written here only as prose.\n"
        '    """\n'
        "import json\n",
    )
    found = Findings()
    imports = release_check.read_imports(source, found)

    assert set(imports.modules) == {"json"}, imports.modules
    assert found.problems == []
    # And the same prose must not raise the floor, which is the conservative
    # direction of the same bug.
    assert release_check.required_floor(imports) == ((3, 0), [])


def test_a_lazy_import_inside_a_function_still_counts(tmp_path: Path) -> None:
    """Every optional adapter here imports inside the function. Missing those
    would call the whole adapter layer absent."""
    source = _module(
        tmp_path, "thing", "def counter():\n    import tiktoken\n    return tiktoken\n"
    )
    imports = release_check.read_imports(source, Findings())
    assert "tiktoken" in imports.modules


def test_a_relative_import_is_not_a_dependency(tmp_path: Path) -> None:
    source = _module(tmp_path, "thing", "from .grounding import Grounder\n")
    imports = release_check.read_imports(source, Findings())
    assert imports.modules == {}


def test_a_file_that_does_not_parse_is_refused(tmp_path: Path) -> None:
    source = _module(tmp_path, "thing", "def broken(:\n")
    found = Findings()
    release_check.read_imports(source, found)
    assert any("does not parse" in p for p in found.problems)


# ── bug 1: optional dependencies ignored ──────────────────────────────────
def test_an_optional_dependency_imported_lazily_is_not_a_finding(tmp_path: Path) -> None:
    """Reading `dependencies` alone called `zero_required_dependencies` a defect.

    Seven of the engine's imports are optional extras behind Protocol adapters —
    litellm, pypdf, qdrant-client, opentelemetry, pdfplumber,
    sentence-transformers — and the first version reported every one as
    undeclared. That is the architecture, not a bug in it.
    """
    source = _module(tmp_path, "thing", "def load():\n    import qdrant_client\n")
    package = _package(
        tmp_path,
        {
            "project": {
                "dependencies": [],
                "optional-dependencies": {"vectors": ["qdrant-client>=1.12"]},
            }
        },
    )
    found = Findings()
    release_check._check_dependencies(package, release_check.read_imports(source, found), found)
    assert found.problems == []


def test_an_import_no_extra_declares_is_refused(tmp_path: Path) -> None:
    """The one true finding of the thirteen: `omnex.llm.tokens` imported tiktoken
    and no extra named it, so no `pip install omnex-engine[...]` made it work."""
    source = _module(tmp_path, "thing", "def load():\n    import tiktoken\n")
    package = _package(tmp_path, {"project": {"dependencies": []}})
    found = Findings()
    release_check._check_dependencies(package, release_check.read_imports(source, found), found)
    assert any("no dependency or extra declares it" in p for p in found.problems)


def test_a_required_dependency_nothing_imports_is_refused(tmp_path: Path) -> None:
    source = _module(tmp_path, "thing", "import json\n")
    package = _package(tmp_path, {"project": {"dependencies": ["requests>=2"]}})
    found = Findings()
    release_check._check_dependencies(package, release_check.read_imports(source, found), found)
    assert any("nothing imports" in p for p in found.problems)


def test_a_declared_extra_nothing_imports_is_left_to_extras_check(tmp_path: Path) -> None:
    """Deliberately not checked here. `extras_check.py` answers it per dependency
    with a status and a reason; a second opinion would be a second copy."""
    source = _module(tmp_path, "thing", "import json\n")
    package = _package(
        tmp_path,
        {"project": {"dependencies": [], "optional-dependencies": {"agents": ["langgraph>=0.2"]}}},
    )
    found = Findings()
    release_check._check_dependencies(package, release_check.read_imports(source, found), found)
    assert found.problems == []


# ── bug 3: the target's name is not its import name ───────────────────────
def test_the_target_name_is_not_assumed_to_be_the_import_name() -> None:
    """engine's directory is `engine/` and its package is `omnex`. Assuming they
    matched sent the version and floor probes after a module that does not exist."""
    assert release_check.TARGETS["engine"].package == "omnex"
    assert (ENGINE / "src" / "omnex" / "__init__.py").exists()

    found = Findings()
    release_check._check_version(release_check.load("engine"), found)
    assert found.problems == []
    assert not any("__init__.py not found" in u for u in found.unknowns)


# ── bug 4: the workflow default a job inherits ────────────────────────────
WORKFLOW = """\
name: Example

defaults:
  run:
    working-directory: engine

jobs:
  check:
    steps:
      - run: uv run pytest tests/ -q
  citegate:
    defaults:
      run:
        working-directory: oss/citegate
    strategy:
      matrix:
        python: ["3.11", "3.13"]
    steps:
      - run: uv run pytest tests/ -q
"""


def test_a_job_inherits_the_workflow_working_directory() -> None:
    """The bug that made this whole file worth writing.

    Reading `working-directory` only inside job blocks meant the job that
    inherits it looked like it ran nowhere. The check for unrun suites therefore
    reported the engine's own suite — the one CI has always run — as never run,
    while getting citegate right for the same wrong reason.
    """
    read = release_check.jobs(WORKFLOW)
    assert read["check"][0] == "engine", "an inherited default is still the job's directory"
    assert read["citegate"][0] == "oss/citegate", "a job-level default overrides it"


def test_both_suites_in_this_repository_resolve_to_a_job() -> None:
    """The assertion, against the real workflows rather than a fixture."""
    for name in ("engine", "citegate"):
        assert release_check.ci_job_running(release_check.load(name)) is not None, (
            f"no workflow job runs {name}'s tests"
        )


def test_a_workflow_with_no_jobs_key_reads_as_no_jobs() -> None:
    assert release_check.jobs("name: Nothing\non: push\n") == {}


def test_the_floor_must_be_in_the_matrix_of_the_job_that_runs_the_suite() -> None:
    """A `requires-python` nobody runs is a claim backed by nothing."""
    _, block = release_check.jobs(WORKFLOW)["citegate"]
    assert release_check._floor_in_matrix(block, (3, 11))
    assert not release_check._floor_in_matrix(block, (3, 10))


# ── the floor, statically and dynamically ─────────────────────────────────
def test_strenum_raises_the_floor_to_311(tmp_path: Path) -> None:
    """citegate declared >=3.10 and imports `enum.StrEnum`, which is 3.11. pip
    resolved, installed, and the first import raised."""
    source = _module(tmp_path, "thing", "from enum import StrEnum\n")
    floor, because = release_check.required_floor(release_check.read_imports(source, Findings()))
    assert floor == (3, 11)
    assert because == ["enum.StrEnum"]


def test_a_floor_below_what_the_code_needs_is_refused(tmp_path: Path) -> None:
    source = _module(tmp_path, "thing", "from enum import StrEnum\n")
    package = _package(tmp_path, {"project": {"requires-python": ">=3.10"}})
    found = Findings()
    release_check._check_floor(package, release_check.read_imports(source, found), None, found)
    assert any("pip resolves, installs" in p for p in found.problems)


def test_the_floor_check_states_that_it_cannot_confirm_a_floor() -> None:
    """Its boundary is load-bearing: the table can raise a floor, never confirm
    one, and a docstring that did not say so would be read as proof."""
    doc = release_check.__doc__ or ""
    assert "can never prove one is high enough" in doc


# ── metadata ──────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://github.com/RaveZona/omnex-factory", "ravezona/omnex-factory"),
        ("https://github.com/RaveZona/omnex-factory.git", "ravezona/omnex-factory"),
        ("git@github.com:RaveZona/omnex-factory.git", "ravezona/omnex-factory"),
        (
            "https://github.com/RaveZona/omnex-factory/tree/master/oss/citegate",
            "ravezona/omnex-factory",
        ),
        ("https://pypi.org/project/citegate", None),
    ],
)
def test_a_github_url_reduces_to_the_repository_it_names(url: str, expected: str | None) -> None:
    assert release_check._slug(url) == expected


def test_metadata_naming_another_repository_is_refused(tmp_path: Path) -> None:
    package = _package(
        tmp_path, {"project": {"urls": {"Homepage": "https://github.com/SomeoneElse/other"}}}
    )
    found = Findings()
    release_check._check_urls(package, found)
    assert any("sends every reader to the wrong place" in p for p in found.problems)


def test_no_urls_at_all_is_not_a_finding(tmp_path: Path) -> None:
    """engine declares none. An absent table is absence, not disagreement."""
    found = Findings()
    release_check._check_urls(_package(tmp_path, {"project": {}}), found)
    assert found.problems == []


def test_a_missing_license_file_is_refused(tmp_path: Path) -> None:
    package = _package(tmp_path, {"project": {"license": {"text": "MIT"}}})
    found = Findings()
    release_check._check_license(package, found)
    assert any("no LICENSE" in p for p in found.problems)


def test_a_version_that_disagrees_with_itself_is_refused(tmp_path: Path) -> None:
    _module(tmp_path, "thing", '__version__ = "0.2.0"\n')
    package = _package(tmp_path, {"project": {"version": "0.1.0"}})
    found = Findings()
    release_check._check_version(package, found)
    assert any("nobody could tell which build they have" in p for p in found.problems)


def test_a_stub_readme_is_refused(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# thing\n", encoding="utf-8")
    package = _package(tmp_path, {"project": {"readme": "README.md"}})
    found = Findings()
    release_check._check_readme(package, found)
    assert any("the whole product page on PyPI" in p for p in found.problems)


# ── the tag, from both sides of it ────────────────────────────────────────
def _fake_git(answers: dict[str, str]) -> object:
    """Stand in for `git`, keyed on the command's leading arguments.

    `rev-parse` is asked two different questions here, so keying on the verb
    alone answers one of them wrongly — which is how the first version of this
    helper made a passing case look like a failure.
    """

    def run(*args: str) -> str:
        joined = " ".join(args)
        return next((value for key, value in answers.items() if joined.startswith(key)), "")

    return run


#: A clean checkout with a pushed HEAD and full history.
_HEALTHY = {
    "rev-parse HEAD": "abc1234",
    "rev-parse --is-shallow-repository": "false",
    "branch --remotes": "  origin/master",
}


def test_a_tag_that_does_not_name_the_version_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Inside the workflow the tag push triggered, "is this name free" is always
    false — the tag is why the job is running. The question there is whether it
    names the version being built."""
    monkeypatch.setattr(release_check, "_git", _fake_git(_HEALTHY))
    package = _package(tmp_path, {"project": {"version": "0.1.0"}})
    found = Findings()
    release_check._check_git(package, found, tag="thing-v9.9.9")
    assert any("would disagree" in p for p in found.problems)

    clean = Findings()
    release_check._check_git(package, clean, tag="thing-v0.1.0")
    assert clean.problems == []


def test_a_shallow_clone_cannot_answer_whether_head_is_pushed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`business_map.py` already paid for this one. `actions/checkout` clones at
    depth 1, so `git branch --remotes --contains` is empty for a reason that has
    nothing to do with the commit — answering anyway refuses every release CI
    cuts. UNKNOWN is a state; false would be a claim."""
    monkeypatch.setattr(
        release_check, "_git", _fake_git({**_HEALTHY, "rev-parse --is-shallow-repository": "true"})
    )
    found = Findings()
    release_check._check_git(_package(tmp_path, {"project": {"version": "0.1.0"}}), found, tag=None)
    assert any("shallow clone" in u for u in found.unknowns)
    assert not any("no remote branch" in p for p in found.problems)


# ── the repository as it actually is ──────────────────────────────────────
@pytest.mark.parametrize("target", ["citegate", "engine"])
def test_the_committed_target_passes_the_drift_checks(target: str) -> None:
    """Both, not one. One passing target is exactly what hid the four bugs."""
    found = release_check.check(release_check.load(target))
    assert found.problems == [], f"{target}: " + "; ".join(found.problems)


def test_citegate_declares_the_floor_its_code_actually_needs() -> None:
    """It said >=3.10 until this gate measured it."""
    package = release_check.load("citegate")
    assert str(package.project["requires-python"]) == ">=3.11"


def test_a_tag_only_workflow_does_not_count_as_continuous_integration() -> None:
    """`release.yml` runs the whole suite and only when somebody pushes a tag.

    Counting it would let "CI runs this package's tests" pass while no push and
    no pull request ran anything — the same gap this check was built to find,
    one level over.
    """
    tag_only = "name: R\non:\n  push:\n    tags:\n      - 'citegate-v*'\n"
    on_changes = "name: E\non:\n  push:\n    branches: [master]\n  pull_request:\n"
    assert not release_check.covers_changes(tag_only)
    assert release_check.covers_changes(on_changes)

    release = (REPO / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert not release_check.covers_changes(release), "release.yml must not count as CI"
