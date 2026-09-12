"""The gates, gated. Nothing in this repository checked its own checkers.

`test_the_round_trip_check_can_actually_fail` exists because a compiler that
compares an artifact with itself proves nothing. The same hole was open one level
up and stayed open longer: CI named two test files by hand, one of which did not
exist, and so ran one suite of seven while reporting green. The suites it skipped
were the ones holding the money path — `liveModules()` is exactly `['studio']`,
the cache-before-fallback rule, the `usage` block every cost figure depends on.

Nothing found that, because nothing was looking. This looks.

## Why the workflows are read as text rather than parsed as YAML

The engine takes no required dependencies, and a test that needs PyYAML is a test
that stops running on a bare interpreter — which is the property that makes this
suite worth having at all. What these assertions are actually about is the
literal shell command each step runs, and a line scan reads exactly that. A YAML
parser would give a tidier tree and the same strings.

## The third assertion is the one that keeps prose honest

CLAUDE.md documents the gate. CI runs the gate. Nothing made them agree, and they
had drifted in the direction that matters: the document was STRICTER than CI, so
a developer running the documented command locally saw failures CI never would.
`test_ci_covers_every_directory_the_documented_gate_covers` reads the fenced
block out of CLAUDE.md and requires CI to be a superset of it.

Its boundary, stated rather than discovered later: it compares two sides and
cannot see a rule that is weak on both. `ruff format --check` omitted `scripts`
in the document AND in CI, so they agreed and this test was satisfied. Only
reading them together with fresh eyes found that one. A drift check is not a
correctness check, and pretending otherwise is how the next weak rule survives.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
WORKFLOWS = REPO / ".github" / "workflows"
CLAUDE_MD = REPO / "CLAUDE.md"

pytestmark = pytest.mark.skipif(
    not WORKFLOWS.is_dir(), reason="no .github/workflows in this checkout"
)

#: A token in a shell command that looks like a path into this repository.
#: Deliberately narrow: it must contain a slash and a dot, so `npm` and
#: `--noEmit` are not mistaken for files while `lib/__tests__/x.test.ts` is not
#: missed.
_PATHLIKE = re.compile(r"(?<![\w/.-])([A-Za-z_][\w./-]*/[\w.-]+\.[A-Za-z]{2,4})(?![\w/.-])")
#: `-o <file>` or `--output-file <file>` names a file the SAME command is about
#: to create, not one it expects to already exist — `release.yml` generates
#: `dist/citegate.cdx.json` this way and reads it back three tokens later in
#: the same block. Structural rather than an allowlist entry, so the next
#: step that writes-then-reads its own output is covered for free.
_DECLARED_OUTPUT = re.compile(r"(?:-o|--output-file)\s+(\S+)")


def _run_commands(path: Path) -> list[str]:
    """Every shell command a workflow runs, including block scalars.

    `run: cmd` yields one command. `run: |` yields each following line that is
    indented past the `run:` key, which is how the eval gate writes its multi-line
    step.
    """
    commands: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        match = re.match(r"^(\s*)-?\s*run:\s*(.*)$", line)
        if match is None:
            index += 1
            continue
        indent, rest = len(match.group(1)), match.group(2).strip()
        index += 1
        if rest not in ("|", ">", "|-", ">-"):
            if rest:
                commands.append(rest)
            continue
        while index < len(lines):
            body = lines[index]
            if body.strip() and (len(body) - len(body.lstrip())) <= indent:
                break
            if body.strip():
                commands.append(body.strip())
            index += 1
    return commands


def _all_commands() -> dict[str, list[str]]:
    return {path.name: _run_commands(path) for path in sorted(WORKFLOWS.glob("*.yml"))}


def _working_directory(path: Path) -> Path:
    """`defaults.run.working-directory`, which engine.yml sets to `engine`."""
    match = re.search(r"working-directory:\s*(\S+)", path.read_text(encoding="utf-8"))
    return REPO / match.group(1) if match else REPO


# ── a workflow may not name a file that does not exist ────────────────────
def test_every_file_a_workflow_names_exists() -> None:
    """The assertion that would have caught the phantom on the day it was written.

    `lib/__tests__/agent-memory.test.ts` was named in CI and has never existed.
    vitest treats positional arguments as filters, so a filter matching nothing
    is not an error — it silently narrows the run instead. The step went green
    for months while covering one file.
    """
    missing: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        base = _working_directory(path)
        commands = _run_commands(path)
        # Declared outputs are gathered across every command in the FILE, not
        # just the one being checked: `_run_commands` yields one entry per
        # physical line of a `run: |` block, so a `-o file \` continued onto
        # the next line and a later line reading that same file back are two
        # separate entries in this list, not one command a single scan sees.
        declared_outputs = {
            output for command in commands for output in _DECLARED_OUTPUT.findall(command)
        }
        for command in commands:
            for token in _PATHLIKE.findall(command):
                if token.startswith(("http", "vercel.")) or "${{" in token:
                    continue
                if token in declared_outputs:
                    continue
                if not (base / token).exists() and not (REPO / token).exists():
                    missing.append(f"{path.name}: {token}")
    assert not missing, "workflows name files that are not in the repository: " + ", ".join(missing)


def test_a_declared_output_does_not_hide_a_genuine_phantom() -> None:
    """The exclusion this test's sibling relies on, checked against both a real
    generated path (release.yml's SBOM, produced by `-o` and read back later in
    the same block) and a synthetic phantom that is never declared as an
    output of anything -- so the exclusion is proven not to swallow the exact
    class of bug `test_every_file_a_workflow_names_exists` exists to catch."""
    generated = [
        "uvx cyclonedx-py environment -o dist/citegate.cdx.json ./python",
        "cat dist/citegate.cdx.json",
    ]
    declared = {output for command in generated for output in _DECLARED_OUTPUT.findall(command)}
    assert "dist/citegate.cdx.json" in declared

    phantom = ["npx vitest run lib/__tests__/agent-memory.test.ts"]
    phantom_declared = {
        output for command in phantom for output in _DECLARED_OUTPUT.findall(command)
    }
    tokens = [t for command in phantom for t in _PATHLIKE.findall(command)]
    assert "lib/__tests__/agent-memory.test.ts" in tokens
    assert "lib/__tests__/agent-memory.test.ts" not in phantom_declared


# ── every test on disk must actually run ──────────────────────────────────
def test_the_typescript_suite_runs_whole_and_not_by_a_hand_written_list() -> None:
    """A file list stops covering whatever somebody adds next, silently.

    So the requirement is not "these seven files are named" — that has the same
    defect one commit later. It is that some step runs vitest with no file
    filter at all.
    """
    ts_tests = sorted(p for p in (REPO / "lib" / "__tests__").glob("*.test.ts"))
    assert ts_tests, "no TypeScript tests found, so this assertion is vacuous"

    whole_suite = [
        command
        for commands in _all_commands().values()
        for command in commands
        if _is_unfiltered(command, "vitest run")
    ]
    assert whole_suite, (
        "no workflow runs `vitest run` without a file filter, so the suites nobody "
        f"named are not covered: {', '.join(p.name for p in ts_tests)}"
    )


def test_the_python_suite_runs_whole() -> None:
    py_tests = sorted(p.name for p in (ENGINE / "tests").glob("test_*.py"))
    assert py_tests
    assert any(
        _is_unfiltered(command, "pytest tests/")
        for commands in _all_commands().values()
        for command in commands
    ), "no workflow runs the whole pytest suite"


#: Directories a package tree may contain that are not this repository's code.
_NOT_OURS = {".venv", "node_modules", "site-packages", ".git", ".mypy_cache"}


def test_every_pytest_suite_in_the_repository_runs_in_ci() -> None:
    """The hole the assertion above left open, found by `release_check.py`.

    `test_the_python_suite_runs_whole` requires *some* workflow to run
    `pytest tests/` unfiltered, and the engine's satisfied it. Meanwhile every
    `pytest` in every workflow inherited `working-directory: engine`, so
    citegate's sixteen tests had never run on a push — green on a developer
    machine, unrun in CI, and invisible to the file whose entire job is catching
    exactly that.

    Keyed on directories rather than a list of names, because a list stops
    covering whatever somebody adds next. `release_check.jobs` is reused rather
    than copied: it is the one reader that resolves a job's *effective* working
    directory, and a second implementation here would drift from it — which is
    the lesson the twin splitters already paid for.
    """
    sys.path.insert(0, str(ENGINE / "scripts"))
    from release_check import covers_changes, jobs

    suites = sorted(
        found.parent.relative_to(REPO).as_posix()
        for found in REPO.glob("**/pyproject.toml")
        if (found.parent / "tests").is_dir() and _NOT_OURS.isdisjoint(found.parts)
    )
    assert suites, "no python package with a tests/ directory found, so this is vacuous"

    texts = {path: path.read_text(encoding="utf-8") for path in sorted(WORKFLOWS.glob("*.yml"))}
    covered = {
        directory.strip("./")
        # `release.yml` runs the whole suite and only on a tag. Counting it would
        # let this pass while no push and no pull request ran anything, which is
        # the gap this test exists for wearing a different hat.
        for text in texts.values()
        if covers_changes(text)
        for directory, block in jobs(text).values()
        if re.search(r"\bpytest\b", block)
    }
    missing = [suite for suite in suites if suite not in covered]
    assert not missing, (
        f"no workflow job runs the tests in {missing} — a suite CI does not run is "
        "green only on the machine that ran it"
    )


def _is_unfiltered(command: str, runner: str) -> bool:
    """True when `runner` appears with no positional file argument after it.

    Flags are allowed — `-q`, `--reporter` and the like narrow output, not
    coverage. A path argument is what narrows coverage, and it is the thing this
    refuses.
    """
    if runner not in command:
        return False
    tail = command.split(runner, 1)[1].strip()
    return not any(token for token in tail.split() if not token.startswith("-") and "." in token)


# ── CI must not be weaker than the documented gate ────────────────────────
def _documented_gate() -> list[str]:
    """The commands in CLAUDE.md's "commands that gate a change" block."""
    text = CLAUDE_MD.read_text(encoding="utf-8")
    block = re.search(r"## The commands that gate a change\s*\n+```bash\n(.*?)```", text, re.S)
    assert block is not None, "CLAUDE.md no longer documents a gate block"
    joined = block.group(1).replace("\\\n", " ")
    return [
        line.strip() for line in joined.splitlines() if line.strip() and not line.startswith("#")
    ]


def _ruff_directories(commands: list[str], subcommand: str) -> set[str]:
    found: set[str] = set()
    for command in commands:
        for part in command.split("&&"):
            part = part.strip()
            if subcommand not in part:
                continue
            tail = part.split(subcommand, 1)[1]
            found |= {
                token
                for token in tail.split()
                if not token.startswith("-") and "/" not in token and "." not in token
            }
    return found


def _gate_scripts(commands: list[str]) -> set[str]:
    """Every `scripts/*.py` a command list runs, by basename."""
    return {
        Path(token).name
        for command in commands
        for part in command.split("&&")
        for token in part.split()
        if token.startswith("scripts/") and token.endswith(".py")
    }


def test_ci_runs_every_gate_script_the_document_names() -> None:
    """The other half of the same drift, which the ruff check could not see.

    `test_ci_covers_every_directory_the_documented_gate_covers` compares ruff's
    directories, so a whole script added to the documented gate and not to CI
    passed it untouched. That is the same failure one level up: a developer runs
    the documented command, CI does not, and the document becomes advice again.
    """
    documented = _gate_scripts(_documented_gate())
    assert documented, "CLAUDE.md's gate no longer runs any script"
    in_ci = _gate_scripts([c for commands in _all_commands().values() for c in commands])
    assert documented <= in_ci, (
        f"CLAUDE.md's gate runs {sorted(documented - in_ci)} and CI does not"
    )


def test_the_documented_gate_names_every_script_ci_runs() -> None:
    """The direction the sibling test above cannot see.

    `node_dossier.py` (engine.yml's "Decision queue" step, regenerating and
    diffing DECISIONS.md) and `eval_gate.py` (quality-gate.yml, blocking on a
    golden-suite regression) both ran in CI with no equivalent command in
    CLAUDE.md's gate block, found by generalising the exact class of gap this
    session already closed twice for individual scripts
    (`readme_check.py`, `n8n_bindings_check.py`): a real CI check a developer
    running only the documented commands would never exercise locally, so a
    push that is locally green can still turn CI red for a reason the
    document never mentioned. `test_ci_runs_every_gate_script_the_document_
    names` only ever checked the other direction (documented <= in_ci); this
    closes the loop so the two sets must now be equal.
    """
    documented = _gate_scripts(_documented_gate())
    in_ci = _gate_scripts([c for commands in _all_commands().values() for c in commands])
    assert in_ci <= documented, (
        f"CI runs {sorted(in_ci - documented)} and CLAUDE.md's gate does not — "
        "a developer following only the documented commands cannot reproduce "
        "this locally before pushing"
    )


@pytest.mark.parametrize("subcommand", ["ruff check", "ruff format --check"])
def test_ci_covers_every_directory_the_documented_gate_covers(subcommand: str) -> None:
    """The document was stricter than CI, which is the direction that hurts.

    A developer running the documented command locally saw failures CI would
    never produce, so a red CI was the only thing anybody trusted and the
    documented gate quietly became advice.
    """
    documented = _ruff_directories(_documented_gate(), subcommand)
    assert documented, f"CLAUDE.md's gate no longer runs {subcommand}"
    in_ci = _ruff_directories(
        [command for commands in _all_commands().values() for command in commands], subcommand
    )
    assert documented <= in_ci, (
        f"CI runs `{subcommand}` on {sorted(in_ci)} while CLAUDE.md documents "
        f"{sorted(documented)}; the gate and the document have drifted"
    )


def test_the_extractor_reads_block_scalars_and_not_just_one_liners(tmp_path: Path) -> None:
    """Proof the parser is not quietly seeing half the workflow.

    Every assertion above is only as good as this function. A `run: |` step it
    skipped would make the file-existence check pass by not looking.
    """
    workflow = tmp_path / "sample.yml"
    workflow.write_text(
        "jobs:\n"
        "  a:\n"
        "    steps:\n"
        "      - name: one\n"
        "        run: echo single\n"
        "      - name: two\n"
        "        run: |\n"
        "          echo first\n"
        "          echo second\n"
        "      - name: three\n"
        "        run: echo after\n",
        encoding="utf-8",
    )
    assert _run_commands(workflow) == [
        "echo single",
        "echo first",
        "echo second",
        "echo after",
    ]


def test_a_filtered_runner_is_recognised_as_filtered() -> None:
    """The check that makes the coverage assertions mean something."""
    assert _is_unfiltered("npx vitest run", "vitest run")
    assert _is_unfiltered("uv run pytest tests/ -q", "pytest tests/")
    assert not _is_unfiltered("npx vitest run lib/__tests__/one.test.ts", "vitest run")
    assert not _is_unfiltered(
        "npx vitest run lib/__tests__/a.test.ts lib/__tests__/b.test.ts", "vitest run"
    )
