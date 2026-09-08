"""The final gate, and the one way a final gate is worthless.

A chain-walker that can only print a passing chain is the decorative
architecture it exists to prevent. So most of this file is about the grades it
must be able to *report*, not the grade it currently has.

The distinction that carries the weight is `DOCUMENTED` vs `ABSENT`. Absent
means the code is not there. Documented means the code is there, the test is
there, and **nothing has ever run it** — which is the state `release.yml` and the
run ledger were both in, and the state that reads as finished in every summary
that does not have a word for it.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ENGINE = REPO / "engine"
sys.path.insert(0, str(ENGINE / "scripts"))

import spine_check  # noqa: E402
from spine_check import CHAIN, Grade, Link  # noqa: E402

#: The contract's order, verbatim. A reordering is a different architecture.
CONTRACT_ORDER = (
    "TRUTH → STATE",
    "STATE → CLAIM",
    "CLAIM → EVIDENCE",
    "EVIDENCE → CAPABILITY",
    "CAPABILITY → DEPENDENCY",
    "DEPENDENCY → EXECUTION GRAPH",
    "EXECUTION GRAPH → NEXT ACTION",
    "NEXT ACTION → POLICY",
    "POLICY → EXECUTION",
    "EXECUTION → VERIFICATION",
    "VERIFICATION → RUN LEDGER",
    "RUN LEDGER → CHECKPOINT",
    "CHECKPOINT → RECOVERY",
    "RECOVERY → TRUTH",
)


def test_the_chain_is_the_one_the_contract_names() -> None:
    assert tuple(link.step for link in CHAIN) == CONTRACT_ORDER


def test_every_link_names_what_the_contract_requires() -> None:
    """SOURCE · CONTRACT · VALIDATION · FAILURE MODE · PROOF, per transition."""
    for link in CHAIN:
        assert link.source and link.contract and link.failure_mode
        assert link.performed_by, f"{link.step} names no code"
        assert (ENGINE / link.proof).exists(), f"{link.step} names a proof that is not here"


# ── the grades it must be able to report ──────────────────────────────────
def test_code_that_does_not_resolve_reads_absent() -> None:
    broken = replace(CHAIN[0], performed_by="claims.NoSuchThing")
    grade, detail = broken.grade()
    assert grade is Grade.ABSENT
    assert "does not resolve" in detail


def test_a_named_proof_that_is_not_in_the_checkout_reads_absent() -> None:
    broken = replace(CHAIN[0], proof="tests/test_imaginary.py")
    assert broken.grade()[0] is Grade.ABSENT


def test_code_that_exists_but_has_never_produced_anything_reads_documented() -> None:
    """The distinction the whole file turns on.

    The run ledger was exactly here: `runs.py` resolved, `test_runs.py` existed,
    CI checked it — and `state/runs.jsonl` did not exist because nothing wrote to
    it. Graded EXECUTABLE, that reads as a working mechanism.
    """
    unexercised = replace(CHAIN[0], artifact="state/nothing-has-made-this.jsonl")
    grade, detail = unexercised.grade()
    assert grade is Grade.DOCUMENTED
    assert "nothing has produced one" in detail


def test_a_link_with_no_artifact_is_graded_on_its_code_alone() -> None:
    """Not every transition leaves a file; requiring one would invent a
    ceremony to satisfy the checker."""
    pure = next(link for link in CHAIN if not link.artifact)
    assert pure.grade()[0] is Grade.EXECUTABLE


def test_the_grade_is_derived_and_not_a_field() -> None:
    assert "grade" not in {f for f in Link.__dataclass_fields__}


# ── the gate can fail ─────────────────────────────────────────────────────
def test_strict_exits_non_zero_when_a_link_is_not_executable() -> None:
    """A gate that cannot go red is not a gate."""
    probe = ENGINE / "scripts" / "spine_check.py"
    assert probe.exists()

    ran = subprocess.run(  # a subprocess so the real exit code is observed
        [sys.executable, "-c", CANNOT_PASS],
        capture_output=True,
        text=True,
        cwd=ENGINE,
        timeout=120,
    )
    assert ran.returncode == 1, ran.stdout + ran.stderr
    assert "Not a complete chain" in ran.stdout


CANNOT_PASS = """
import sys
sys.path.insert(0, "scripts")
sys.argv = ["spine_check", "--strict"]
import spine_check
from dataclasses import replace
spine_check.CHAIN = tuple(
    replace(link, artifact="state/nothing-has-made-this.jsonl") if i == 0 else link
    for i, link in enumerate(spine_check.CHAIN)
)
sys.exit(spine_check.main())
"""


def test_the_module_states_that_an_all_green_chain_is_not_the_default_claim() -> None:
    doc = spine_check.__doc__ or ""
    assert "Do not claim completion" in doc
    assert "decorative architecture" in doc


# ── the chain as it actually is ───────────────────────────────────────────
def test_the_committed_chain_is_whole() -> None:
    """It was 13 EXECUTABLE · 1 DOCUMENTED when this was written: the ledger had
    no writer. If this fails, a link regressed — read which, do not relax it."""
    results = spine_check.walk()
    unproven = [
        (link.step, grade.value) for link, grade, _ in results if grade is not Grade.EXECUTABLE
    ]
    assert not unproven, f"links no longer executable: {unproven}"


@pytest.mark.parametrize("link", CHAIN, ids=lambda link: link.step)
def test_each_link_resolves_against_the_shared_resolver(link: Link) -> None:
    """`omnex.core.symbols.resolve`, never a second copy."""
    source = (ENGINE / "scripts" / "spine_check.py").read_text(encoding="utf-8")
    assert "from omnex.core.symbols import resolve" in source
    assert "importlib" not in source, "a private import check is a second resolver"
    assert link.grade()[0] is not Grade.ABSENT
