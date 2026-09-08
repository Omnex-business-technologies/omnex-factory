"""Everything wrong with a package, before somebody outside this repository finds it.

    python scripts/release_check.py --target citegate                    # drift checks
    python scripts/release_check.py --target citegate --release          # before tagging
    python scripts/release_check.py --target citegate --tag citegate-v1  # inside the workflow

Two modes, the same split `env_check.py` already uses. The default compares the
package's declarations with its own code and with CI; `--release` adds the checks
that are only meaningful on the machine about to cut a tag: a clean tree, a tag
not already taken, a commit somebody else can fetch.

`--tag` is that second mode from the other side of the tag. A workflow triggered
by the tag push cannot ask "is this name free" — the tag is why it is running —
so it asks whether the tag names the version in `pyproject.toml` instead. Without
that, the gate would be unusable in the one place it matters most, which is how a
gate becomes decorative.

## What it found on citegate

**`requires-python = ">=3.10"` and the package needs 3.11.** `grounding.py`
imports `enum.StrEnum`, which landed in 3.11. `pip install citegate` on 3.10
resolves, installs, and then `import citegate` raises ImportError. The first
person to discover that would have been a user.

**Its sixteen tests never ran in CI.** Every `pytest` in `.github/workflows`
inherited `working-directory: engine`, so citegate's suite was green on a
developer machine and unrun on every push. `test_ci_contract` did not see it:
`test_the_python_suite_runs_whole` is satisfied by any unfiltered `pytest tests/`
anywhere, and the engine's satisfied it.

## What running it on the SECOND target found in this file

The first version reported 13 refusals against `engine`, and every one was a
false positive. That is the more useful finding, because a gate is not a gate
until something has tried to break it:

- it read `dependencies` and ignored `[project.optional-dependencies]`, so it
  called `zero_required_dependencies` — the engine's entire design — a defect;
- it borrowed `extras_check.importers()`, whose regex matches inside docstrings,
  and reported imports of `a`, `free`, `the` and `zero`;
- it assumed the target's name was its import name (engine's package is `omnex`);
- and `ci_runs_the_suite` looked for `working-directory` only inside job blocks
  while `engine.yml` sets it in top-level `defaults:`. **The check written to find
  unrun suites could not see the suite that runs.** It was right about citegate by
  coincidence of the same bug, which is indistinguishable from working until a
  second target exists.

One refusal survived the fix and was real: `omnex/llm/tokens.py` lazily imports
`tiktoken` and no extra declared it, so no `pip install omnex-engine[…]` made
`TiktokenCounter` work. `extras_check.py` cannot see that by construction — it
asks *declared → imported*. This asks *imported → declared*, and that reverse
direction is the whole reason a second checker earns its place here.

## Why the import scanner is its own, and not the shared one

`extras_check.importers()` answers "is this declared name imported anywhere",
where a false positive from prose costs nothing because the name is never looked
up. This asks what a package imports and reads the answer as truth. Same words,
different contract — so this reads the syntax tree with `ast` (stdlib, so the
zero-dependency rule holds) and cannot mistake a sentence for an import. What IS
reused is `IMPORT_NAME` and `_requirement_name`: maintained tables, and a second
copy of those would be the drift this repository keeps paying for.

## The floor is a claim about interpreters, so it is checked as one

Statically, from the symbols the package imports: `StrEnum` means 3.11 and
nothing argues with that. The table is deliberately small — only constructs this
repository actually uses, the same rule as `IMPORT_NAME`, because a version table
nobody maintains starts reporting a floor that is merely stale.

**Its boundary, stated rather than discovered later: this can prove a floor is
too low and can never prove one is high enough.** A 3.12-only construct not in
the table passes. That is why the other two halves exist — the floor interpreter
is run when this machine has it, and the job that runs the suite must name the
floor in its matrix. Absence of the interpreter is UNKNOWN, never a pass.

## What it refuses, all at once

- no LICENSE beside the package, or one whose text does not match the declared id
- a license classifier that disagrees with the `license` field
- `version` in `pyproject.toml` disagreeing with `__version__`
- a `readme` naming a file that is missing or a stub
- a `[project.urls]` entry naming a different repository than the remote
- an import no dependency or extra declares; a required dependency nothing imports
- `requires-python` below what the code's own imports require
- a floor the job running the suite does not put in its matrix
- a test suite no workflow runs
- (`--release`) a dirty tree, a tag already taken, a HEAD no remote has
- (`--tag`) the same, except the tag must NAME this version rather than be free

Being refused one reason per run is how somebody concludes the gate is the
obstacle rather than the work.
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
WORKFLOWS = REPO / ".github" / "workflows"
sys.path.insert(0, str(ENGINE / "scripts"))

from extras_check import IMPORT_NAME, _requirement_name  # noqa: E402


@dataclass(frozen=True)
class Target:
    """Where a release target lives, and what it is imported as.

    The two differ and assuming otherwise was a real bug: engine's directory is
    `engine/` and its package is `omnex`, so the version and floor probes went
    looking for a module called `engine` and refused a package that was fine.
    """

    path: Path
    package: str


#: A release target is a directory with its own `pyproject.toml`. Named rather
#: than passed as a path, so `--target` cannot be pointed outside the repository.
TARGETS = {
    "citegate": Target(Path("oss") / "citegate", "citegate"),
    "engine": Target(Path("engine"), "omnex"),
}

#: Symbol → the Python version it first appeared in. Only constructs used in
#: this repository: a table nobody maintains eventually reports a floor that is
#: merely out of date, which is worse than not checking.
#:
#: This can raise a floor and can never confirm one. A 3.12-only construct
#: absent from here passes silently, which is why the floor is also run and also
#: required to appear in the matrix of the job that runs the suite.
SINCE = {
    "enum.StrEnum": (3, 11),
    "enum.ReprEnum": (3, 11),
    "datetime.UTC": (3, 11),
    "typing.Self": (3, 11),
    "typing.Never": (3, 11),
    "asyncio.TaskGroup": (3, 11),
    "tomllib": (3, 11),
    "itertools.batched": (3, 12),
    "typing.override": (3, 12),
}

#: `license = { text = "MIT" }` is a claim about the file next to it.
LICENSE_TEXT = {
    "MIT": ("MIT License", "Permission is hereby granted, free of charge"),
}
LICENSE_CLASSIFIER = {"MIT": "License :: OSI Approved :: MIT License"}


@dataclass
class Package:
    """One release target, read from disk."""

    name: str
    target: Target
    manifest: dict[str, object]

    @property
    def project(self) -> dict[str, object]:
        return self.manifest.get("project") or {}  # type: ignore[return-value]

    @property
    def version(self) -> str:
        return str(self.project.get("version", ""))

    @property
    def root(self) -> Path:
        return REPO / self.target.path

    @property
    def source(self) -> Path:
        return self.root / "src"

    @property
    def module(self) -> str:
        """The importable package name, which is not the target's name."""
        return self.target.package


@dataclass
class Findings:
    problems: list[str] = field(default_factory=list)
    #: Measured but not decidable here. `UNKNOWN` is a state; reporting it as a
    #: pass would be a claim nothing checked.
    unknowns: list[str] = field(default_factory=list)

    def refuse(self, reason: str) -> None:
        self.problems.append(reason)

    def unknown(self, what: str) -> None:
        self.unknowns.append(what)


def load(name: str) -> Package:
    target = TARGETS[name]
    manifest = tomllib.loads((REPO / target.path / "pyproject.toml").read_text(encoding="utf-8"))
    return Package(name=name, target=target, manifest=manifest)


# ── what the code imports ─────────────────────────────────────────────────
@dataclass
class Imports:
    """What a package imports, read from its syntax tree rather than its text."""

    #: top-level module name → the first file here that imports it
    modules: dict[str, str] = field(default_factory=dict)
    #: fully qualified names, e.g. `enum.StrEnum`, for the version floor
    symbols: set[str] = field(default_factory=set)


def read_imports(source: Path, found: Findings) -> Imports:
    """Every import in a package, via `ast` rather than a regex.

    Indented imports count: every lazy `import tiktoken` inside a method is
    exactly the pattern this codebase uses, and a scan that only saw module-scope
    imports would call the whole adapter layer missing.

    Relative imports are skipped — `from .grounding import Grounder` is internal
    and says nothing about what must be installed.
    """
    imports = Imports()
    for path in sorted(source.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        where = path.relative_to(source).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as error:
            found.refuse(
                f"{where} does not parse ({error.msg}, line {error.lineno}) — "
                "a file that cannot be read cannot be shipped"
            )
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.modules.setdefault(alias.name.split(".")[0], where)
                    imports.symbols.add(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                imports.modules.setdefault(node.module.split(".")[0], where)
                imports.symbols |= {f"{node.module}.{alias.name}" for alias in node.names}
    return imports


def required_floor(imports: Imports) -> tuple[tuple[int, int], list[str]]:
    """The lowest interpreter the code's own imports allow, and what forced it.

    Anything absent from `SINCE` contributes nothing, which is the stated
    boundary: a floor can be raised here and never confirmed.
    """
    floor = (3, 0)
    because: list[str] = []
    for symbol in sorted(imports.symbols):
        needs = SINCE.get(symbol)
        if needs is None:
            continue
        if needs > floor:
            floor, because = needs, [symbol]
        elif needs == floor:
            because.append(symbol)
    return floor, because


def imports_on(interpreter: Path, package: Package) -> str | None:
    """Import the package on one interpreter. The error, or None when it worked.

    The static table can only raise a floor. This is the half that can say the
    floor actually holds — but only for the interpreters present on this machine,
    so its absence is UNKNOWN rather than a pass.
    """
    probe = subprocess.run(
        [
            str(interpreter),
            "-c",
            f"import sys; sys.path.insert(0, {str(package.source)!r}); import {package.module}",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if probe.returncode == 0:
        return None
    return (probe.stderr.strip().splitlines() or ["failed with no output"])[-1]


# ── CI ────────────────────────────────────────────────────────────────────
def _workflow_text() -> dict[str, str]:
    if not WORKFLOWS.is_dir():
        return {}
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(WORKFLOWS.glob("*.yml"))}


def _uncommented(line: str) -> str:
    """`line` with its YAML comment removed, quotes respected.

    Both readers below are substring scans over raw text, which means a workflow
    *comment* describing a key counts as that key. That is not hypothetical: the
    comment added to `release.yml`'s `on:` block explaining that it deliberately
    has no `branches:` contains the string `branches:`, and flipped
    `covers_changes` to True — making a tag-only workflow read as continuous
    integration, which is the exact gap that function exists to close. It fails
    toward passing, so nothing downstream would have said so.

    A comment opens at `#` when it starts the line or follows whitespace, and
    never inside a quoted scalar — `- "citegate-v*"` must survive intact.
    """
    quote = ""
    for index, char in enumerate(line):
        if quote:
            if char == quote:
                quote = ""
        elif char in "\"'":
            quote = char
        elif char == "#" and (index == 0 or line[index - 1].isspace()):
            return line[:index]
    return line


def _working_directory(lines: list[str]) -> str:
    for line in lines:
        match = re.search(r"working-directory:\s*(\S+)", _uncommented(line))
        if match:
            return match.group(1)
    return ""


def jobs(text: str) -> dict[str, tuple[str, str]]:
    """job name → (effective working directory, the job's block).

    A hand-rolled reader rather than PyYAML, for the reason `test_ci_contract`
    already gives: a test that needs a dependency is a test that stops running on
    a bare interpreter, and what matters here is the literal shell command a step
    runs plus one key above it.

    **The inheritance is the whole point.** `engine.yml` sets
    `defaults.run.working-directory` at the top level, so every job runs in
    `engine` unless it overrides. Reading only job blocks reported the engine's
    own suite as never run — a check for unrun suites that could not see the
    suite that runs.

    Comments are stripped first, for the reason `_uncommented` gives. It matters
    twice here: a top-level comment at column 0 would close the section early,
    and `engine.yml`'s citegate job explains itself with a comment containing the
    word `pytest` — so a job that only *discussed* running a suite would satisfy
    every caller that greps this block for one.
    """
    lines = [_uncommented(line) for line in text.splitlines()]
    opens = next((i for i, line in enumerate(lines) if line.rstrip() == "jobs:"), None)
    if opens is None:
        return {}

    inherited = _working_directory(lines[:opens])
    found: dict[str, tuple[str, str]] = {}
    name, start = "", -1

    def close(end: int) -> None:
        if start < 0:
            return
        block = lines[start:end]
        found[name] = (_working_directory(block) or inherited, "\n".join(block))

    index = opens + 1
    while index < len(lines):
        line = lines[index]
        if line.strip() and not line.startswith(" "):
            break  # a top-level key after `jobs:` closes the section
        header = re.match(r"^  ([A-Za-z_][\w-]*):\s*$", line)
        if header:
            close(index)
            name, start = header.group(1), index
        index += 1
    close(index)
    return found


def covers_changes(text: str) -> bool:
    """Whether a workflow runs on ordinary changes rather than only on a tag.

    `release.yml` runs the whole suite — and only when somebody pushes a tag. It
    would otherwise satisfy "CI runs this package's tests" while covering no
    push and no pull request, which is the same shape as the gap this check was
    built to find, one level over. A release gate is not continuous integration.

    Comments are stripped before the scan — see `_uncommented`. A workflow that
    explains in prose why it has no `branches:` must not thereby acquire one.
    """
    lines = [_uncommented(line) for line in text.splitlines()]
    opens = next((i for i, line in enumerate(lines) if re.match(r"^on:\s*$", line)), None)
    if opens is None:
        return bool(re.search(r"^on:.*\b(push|pull_request)\b", "\n".join(lines), re.MULTILINE))
    body: list[str] = []
    for line in lines[opens + 1 :]:
        if line.strip() and not line.startswith(" "):
            break
        body.append(line)
    block = "\n".join(body)
    return "pull_request:" in block or "branches:" in block


def ci_job_running(package: Package) -> tuple[str, str] | None:
    """`(workflow:job, block)` for the job that runs this package's tests, or None."""
    where = package.target.path.as_posix()
    for workflow, text in _workflow_text().items():
        if not covers_changes(text):
            continue
        for name, (directory, block) in jobs(text).items():
            if directory.strip("./") == where and re.search(r"\bpytest\b", block):
                return f"{workflow}:{name}", block
    return None


def _floor_in_matrix(block: str, floor: tuple[int, int]) -> bool:
    """The job that runs the suite must name the floor among its interpreters.

    A `requires-python` nobody runs is a claim about interpreters backed by
    nothing — the same shape as an extra whose dependency no module imports.
    """
    return re.search(rf'["\']{floor[0]}\.{floor[1]}["\']', block) is not None


# ── the checks ────────────────────────────────────────────────────────────
def check(package: Package, *, release: bool = False, tag: str | None = None) -> Findings:
    """Every reason this package is not ready, collected rather than raised."""
    found = Findings()
    imports = read_imports(package.source, found)
    job = ci_job_running(package)

    _check_license(package, found)
    _check_version(package, found)
    _check_readme(package, found)
    _check_urls(package, found)
    _check_dependencies(package, imports, found)
    _check_floor(package, imports, job, found)

    if job is None:
        found.refuse(
            f"no workflow job runs {package.name}'s tests in {package.target.path} — "
            "a suite CI does not run is green only on the machine that ran it"
        )
    if release:
        _check_git(package, found, tag)
    return found


def _check_license(package: Package, found: Findings) -> None:
    declared = package.project.get("license")
    ident = declared.get("text", "") if isinstance(declared, dict) else str(declared or "")
    path = package.root / "LICENSE"

    if not path.exists():
        found.refuse(
            f"no LICENSE in {package.target.path} — `license = {ident!r}` in the "
            "metadata is the claim; the file is what a user actually receives"
        )
    elif ident in LICENSE_TEXT:
        body = path.read_text(encoding="utf-8")
        missing = [phrase for phrase in LICENSE_TEXT[ident] if phrase not in body]
        if missing:
            found.refuse(
                f"LICENSE does not read like {ident}: missing {missing!r}. "
                "The metadata and the file disagree about what was granted"
            )
    else:
        found.unknown(f"license {ident!r} — no text known for it, so the file is unchecked")

    classifiers = [str(c) for c in package.project.get("classifiers") or []]
    wanted = LICENSE_CLASSIFIER.get(ident)
    if wanted and classifiers and wanted not in classifiers:
        found.refuse(
            f"classifiers do not include {wanted!r} while the license field says "
            f"{ident!r} — PyPI shows the classifier, so the two must agree"
        )


def _check_version(package: Package, found: Findings) -> None:
    """`pyproject.toml` and `__version__` are two places one number lives."""
    if not package.version:
        found.refuse("no version in [project] — nothing to tag or to install")
        return
    init = package.source / package.module / "__init__.py"
    if not init.exists():
        found.unknown(f"{package.module}/__init__.py not found, so `__version__` is unchecked")
        return
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', init.read_text(), re.MULTILINE)
    if match is None:
        found.unknown(f"{package.module}/__init__.py declares no `__version__` to compare")
    elif match.group(1) != package.version:
        found.refuse(
            f"version {package.version} in pyproject.toml and {match.group(1)} in "
            f"{package.module}/__init__.py — the installed package would report the "
            "wrong one and nobody could tell which build they have"
        )


def _check_readme(package: Package, found: Findings) -> None:
    named = str(package.project.get("readme", ""))
    if not named:
        found.refuse("no readme in [project] — PyPI would show an empty description")
        return
    path = package.root / named
    if not path.exists():
        found.refuse(f"readme names {named}, which is not in {package.target.path}")
    elif len(path.read_text(encoding="utf-8").strip()) < 200:
        found.refuse(f"{named} is a stub; it is the whole product page on PyPI")


def _slug(url: str) -> str | None:
    """`https://github.com/Owner/repo/tree/master/x` → `owner/repo`."""
    match = re.search(r"github\.com[:/]+([\w.-]+/[\w.-]+?)(?:\.git)?(?:/|$)", url.strip())
    return match.group(1).lower() if match else None


def _check_urls(package: Package, found: Findings) -> None:
    """A github.com URL in the metadata names a repository; check it names this one.

    Reads the remote's *name*, which is stable configuration, and never the tree,
    tags or HEAD — those are properties of a moment and belong to `--release`.
    An absent `[project.urls]` is not a finding: engine declares none.
    """
    urls: dict[str, object] = package.project.get("urls") or {}  # type: ignore[assignment]
    if not urls:
        return
    here = _slug(_git("config", "--get", "remote.origin.url"))
    if here is None:
        found.unknown("no github remote to compare [project.urls] against")
        return
    for label, url in sorted(urls.items()):
        named = _slug(str(url))
        if named is not None and named != here:
            found.refuse(
                f"[project.urls].{label} points at {named} and this repository is "
                f"{here} — metadata naming another repository sends every reader "
                "to the wrong place"
            )


def _check_dependencies(package: Package, imports: Imports, found: Findings) -> None:
    """Imported against declared, counting every extra as a declaration.

    An optional dependency imported lazily behind a Protocol is this repository's
    design, not a defect — reading only `dependencies` reported the whole adapter
    layer as undeclared.

    Only the *required* list is checked in the other direction. "A declared extra
    nothing imports" is `extras_check.py`'s question, measured per dependency with
    statuses and reasons, and a second opinion here would be a second copy.
    """
    project = package.project
    required = {_requirement_name(str(s)) for s in project.get("dependencies") or []}
    groups: dict[str, list[str]] = project.get("optional-dependencies") or {}  # type: ignore[assignment]
    declared = set(required)
    for specs in groups.values():
        declared |= {_requirement_name(str(s)) for s in specs}
    known = {IMPORT_NAME.get(name, name.replace("-", "_")) for name in declared}

    for name, where in sorted(imports.modules.items()):
        if name in sys.stdlib_module_names or name == package.module or name in known:
            continue
        found.refuse(
            f"{where} imports {name} and no dependency or extra declares it — "
            "there is no `pip install` that makes this code work"
        )

    for name in sorted(required):
        if IMPORT_NAME.get(name, name.replace("-", "_")) not in imports.modules:
            found.refuse(
                f"{name} is a required dependency nothing imports — every install "
                "pays for it and no code uses it"
            )


def _check_floor(
    package: Package,
    imports: Imports,
    job: tuple[str, str] | None,
    found: Findings,
) -> None:
    declared = _version_tuple(str(package.project.get("requires-python", "")))
    needed, because = required_floor(imports)

    if declared is None:
        found.refuse("requires-python is missing or not a simple `>=` floor")
        return
    if declared < needed:
        found.refuse(
            f"requires-python is >={declared[0]}.{declared[1]} and the code needs "
            f"{needed[0]}.{needed[1]} ({', '.join(because)}) — pip resolves, installs, "
            "and the first import raises"
        )

    floor = max(declared, needed)
    interpreter = Path(f"/usr/bin/python{floor[0]}.{floor[1]}")
    if interpreter.exists():
        failure = imports_on(interpreter, package)
        if failure:
            found.refuse(f"does not import on python{floor[0]}.{floor[1]}: {failure}")
    else:
        found.unknown(
            f"python{floor[0]}.{floor[1]} is not on this machine, so the floor was "
            "not run here. The table can raise a floor, never confirm one"
        )

    # A missing job is already refused by name in `check`; saying it twice from
    # one cause is how a reader learns to skim the list.
    if job is not None and not _floor_in_matrix(job[1], floor):
        found.refuse(
            f"{job[0]} runs the suite and does not name python {floor[0]}.{floor[1]} — "
            "the floor is the version a user is most likely to be on and the least "
            "likely to be tested"
        )


def _version_tuple(spec: str) -> tuple[int, int] | None:
    """`">=3.11"` → `(3, 11)`. None when the constraint is not a simple floor."""
    match = re.search(r">=\s*(\d+)\.(\d+)", spec)
    return (int(match.group(1)), int(match.group(2))) if match else None


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args], capture_output=True, text=True, timeout=60
    ).stdout.strip()


def _check_git(package: Package, found: Findings, tag: str | None = None) -> None:
    """Release-time: the state of the machine about to cut a tag, or running on one.

    The tag check inverts between the two, and getting that wrong would make this
    gate unusable in the one place it matters most. Before the tag exists, the
    question is "is this name still free". Inside a workflow the tag push
    triggered, the tag necessarily exists and the question becomes "does it name
    the version in `pyproject.toml`" — a release tagged `citegate-v0.2.0` against
    a 0.1.0 manifest publishes an artifact that disagrees with its own name.
    """
    dirty = _git("status", "--porcelain", "--", str(package.target.path))
    if dirty:
        found.refuse(
            f"working tree is dirty under {package.target.path}:\n    "
            + "\n    ".join(dirty.splitlines())
            + "\n    An artifact built from an uncommitted tree cannot be reproduced"
        )

    expected = f"{package.name}-v{package.version}"
    if tag is None:
        if expected in _git("tag", "--list", expected).splitlines():
            found.refuse(
                f"tag {expected} already exists — either the version needs bumping "
                "or this would publish different code under a name somebody has"
            )
    elif tag != expected:
        found.refuse(
            f"tag {tag} does not name {package.name} {package.version} (expected "
            f"{expected}) — the artifact and the tag it ships under would disagree"
        )

    head = _git("rev-parse", "HEAD")
    if _git("rev-parse", "--is-shallow-repository") == "true":
        # The lesson `business_map.py` already paid for: a shallow clone cannot
        # answer this, and answering anyway would refuse every release CI cuts.
        # `fetch-depth: 0` in the workflow is what makes it answerable.
        found.unknown(
            "shallow clone — whether HEAD is on a remote branch is unanswerable "
            "here. Check out with fetch-depth: 0 to make this a real check"
        )
    elif not _git("branch", "--remotes", "--contains", head):
        found.refuse(
            f"HEAD ({head[:8]}) is on no remote branch — the sdist would name a "
            "commit nobody outside this machine can fetch, which is provenance "
            "that cannot be followed"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Refuse a package that is not ready to ship.")
    parser.add_argument("--target", choices=sorted(TARGETS), required=True)
    parser.add_argument(
        "--release",
        action="store_true",
        help="also check tree, tag and provenance — the operator's mode, at tag time",
    )
    parser.add_argument(
        "--tag",
        help="the tag being released; asserts it names this version instead of "
        "asserting the name is still free. What a workflow triggered BY the tag passes",
    )
    args = parser.parse_args()

    package = load(args.target)
    found = check(package, release=args.release or bool(args.tag), tag=args.tag)
    mode = f"tag {args.tag}" if args.tag else ("release" if args.release else "drift")

    print(f"{package.name} {package.version}  ({mode} checks)")
    print()
    for unknown in found.unknowns:
        print(f"  UNKNOWN  {unknown}")
    if found.unknowns:
        print()

    if found.problems:
        for problem in found.problems:
            print(f"FAIL {problem}")
        print(f"\n{len(found.problems)} reason(s) not to ship {package.name} {package.version}.")
        return 1

    print(f"Nothing refuses {package.name} {package.version}.")
    if not (args.release or args.tag):
        print(
            "This did not look at the tree, the tags or HEAD. Run --release on the "
            "machine about to tag: those are properties of that moment, not of "
            "this file."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
