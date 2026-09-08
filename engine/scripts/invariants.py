"""The repository's own rules, as predicates instead of prose.

`ontology_map.py` does this for branches: a claim about code that does not
import fails CI. `node_map.py` does it for nodes: a machine may propose an alias
and may not decide two names mean the same thing. `factory.compile` does it for
compilers: `parse(emit(bp)) == bp`.

The one place the pattern was never applied is the place the rules actually live.
CLAUDE.md states 31 of them, 21 phrased as "never / must not / refuses", and
until this file none was checked. That is not a stylistic gap. Two of the five
defects found in the audit that produced this file — a float currency path in
the metrics export, and `time.monotonic()` in the sandbox — were direct
violations of rules written down in that document, greppable in minutes, and
sitting there because nothing greps.

## Where this lives, and why not in the package

The plan put these checkers in `omnex.core`. They are here instead, next to
`ontology_map.py` and `node_map.py`, because they never run at runtime: nothing
in the shipped library calls them, and putting them in `core/` would ship a
source scanner to every consumer for no benefit. `core.symbols.resolve` is in
the package because `factory.spec.audit()` genuinely calls it on a live spec.
These do not have that argument, and inventing one would be the wrong kind of
symmetry.

## What a checker is

A function taking no arguments and returning a list of `Violation`. No
exceptions, no printing, no exit codes — `invariant_map.py` owns all of that, so
a checker stays testable in one line and several checkers can report together.
Refusals name every failure at once for the same reason they do everywhere else
here: being refused one at a time is how somebody concludes the check is the
obstacle.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import re
import sys
import tomllib
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
SRC = ENGINE / "src" / "omnex"
TESTS = ENGINE / "tests"
SCRIPTS = ENGINE / "scripts"
CITEGATE = REPO / "oss" / "citegate" / "src" / "citegate" / "grounding.py"


@dataclass(frozen=True)
class Violation:
    """One breach, located precisely enough to fix without searching."""

    where: str
    detail: str

    def __str__(self) -> str:
        return f"{self.where}: {self.detail}"


def _python_files(*roots: Path) -> Iterator[Path]:
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" not in path.parts:
                yield path


def _rel(path: Path) -> str:
    return str(path.relative_to(REPO))


# ── 1. money is exact ─────────────────────────────────────────────────────
#: Names that mean money in this codebase. A `float()` over any of them is the
#: currency bug `core/money.py` exists to prevent.
_MONEY_WORDS = ("picos", "cost", "price", "spend", "margin", "revenue", "money")


def money_never_float() -> list[Violation]:
    """No `float()` applied to anything named like money.

    AST rather than grep, so `float("inf")` for an infinite payback and
    `float(ratio)` in a statistics helper are not swept up with the real thing.
    What it catches is the exact shape that had come back:
    `self._cost.inc(float(span.cost.picos))`, which turns an exact amount into a
    float64 accumulator that stops being exact above $9,007.20.
    """
    violations: list[Violation] = []
    for path in _python_files(SRC):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
                continue
            if node.func.id != "float" or not node.args:
                continue
            rendered = ast.unparse(node.args[0]).lower()
            hit = next((word for word in _MONEY_WORDS if word in rendered), None)
            if hit is not None:
                violations.append(
                    Violation(
                        f"{_rel(path)}:{node.lineno}",
                        f"float() over {ast.unparse(node.args[0])!r} — {hit!r} is money, "
                        "and a float currency path stops being exact above 2**53 picos",
                    )
                )
    return violations


# ── 2. time is injected ───────────────────────────────────────────────────
_DIRECT_TIME = re.compile(r"\b(?:datetime\.(?:now|utcnow)|time\.(?:monotonic|time))\s*\(")


def clock_is_injected(allowlist: tuple[str, ...] = ()) -> list[Violation]:
    """Nothing reads the wall clock directly except `core/clock.py`.

    `FakeClock` is why this suite asserts on hour-long TTLs and still runs in
    seconds. Every direct call is a code path no test can pin, and `sandbox.py`
    proved the cost is not theoretical: `duration_seconds` went unasserted for
    the whole life of the module because nothing could control it.

    `allowlist` entries come from `invariants.json` and each carries its reason
    there, the way a branch carries `missing`. An unexplained exception is the
    thing this is trying to prevent.
    """
    allowed = {*allowlist, "engine/src/omnex/core/clock.py"}
    violations: list[Violation] = []
    for path in _python_files(SRC):
        if _rel(path) in allowed:
            continue
        source = path.read_text(encoding="utf-8")
        prose = _string_literal_lines(source, path)
        for number, line in enumerate(source.splitlines(), 1):
            if number in prose or line.lstrip().startswith("#"):
                continue
            match = _DIRECT_TIME.search(line)
            if match:
                violations.append(
                    Violation(
                        f"{_rel(path)}:{number}",
                        f"{match.group(0)}) reads the clock directly; take a `Clock` instead",
                    )
                )
    return violations


def _string_literal_lines(source: str, path: Path) -> set[int]:
    """Lines inside a string literal, which are prose and not code.

    The first version of this checker flagged `sandbox.py` for the sentence in
    its own docstring EXPLAINING that it no longer reads the clock — a checker
    that fires on its own fix notice is one people learn to ignore.
    """
    spans: set[int] = set()
    tree = ast.parse(source, filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            spans.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))
    return spans


# ── 3. ordered StrEnums write all four comparisons ────────────────────────
def ordered_strenum_defines_all_comparisons() -> list[Violation]:
    """A `StrEnum` compared with `<` or `>` must define all four operators.

    `StrEnum` inherits `str`'s comparisons, so the operators already exist and
    answer alphabetically. `@total_ordering` therefore fills in NOTHING — it only
    supplies operators a class lacks. `Stage.DEPLOY < Stage.IDEA` was true by
    string order, and a pipeline ordered by that permits every backwards move
    whose name happens to sort earlier while the check still reads as working.
    """
    compared: set[str] = set()
    defined: dict[str, set[str]] = {}

    for path in _python_files(SRC, TESTS, SCRIPTS):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and any(
                isinstance(base, ast.Name) and base.id == "StrEnum" for base in node.bases
            ):
                defined[node.name] = {
                    item.name
                    for item in node.body
                    if isinstance(item, ast.FunctionDef)
                    and item.name in ("__lt__", "__le__", "__gt__", "__ge__")
                }
            if isinstance(node, ast.Compare) and any(
                isinstance(op, ast.Lt | ast.LtE | ast.Gt | ast.GtE) for op in node.ops
            ):
                for side in (node.left, *node.comparators):
                    if isinstance(side, ast.Attribute) and isinstance(side.value, ast.Name):
                        compared.add(side.value.id)

    return [
        Violation(
            name,
            "is ordered somewhere but defines "
            f"{sorted(defined[name]) or 'none'} of the four comparisons; the inherited "
            "string ones answer, and answer wrongly",
        )
        for name in sorted(compared & set(defined))
        if len(defined[name]) != 4
    ]


# ── 4. one symbol resolver ────────────────────────────────────────────────
_RESOLVER = re.compile(r"^\s*def resolve\s*\(\s*symbol", re.MULTILINE)


def one_symbol_resolver() -> list[Violation]:
    """Exactly one implementation of "does this dotted name exist".

    Three callers were about to hold three copies. The splitter in `rag/ingest`
    and citegate is what a second copy costs: a quadratic fixed in one survived
    in the other for a further commit, and nothing said so.
    """
    home = SRC / "core" / "symbols.py"
    return [
        Violation(_rel(path), "a second `resolve(symbol...)`; import `core.symbols` instead")
        for path in _python_files(SRC, SCRIPTS, TESTS)
        if path != home and _RESOLVER.search(path.read_text(encoding="utf-8"))
    ]


# ── 5. the twin splitters agree ───────────────────────────────────────────
def _load(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def twin_splitters_agree() -> list[Violation]:
    """The engine's splitter and citegate's, which are copies on purpose.

    They may not import each other — citegate ships dependency-free — so the
    only thing holding them together was a sentence in CLAUDE.md. That sentence
    has now failed twice: once on the quadratic restore, once on the
    abbreviation set, which diverged while the two FUNCTIONS stayed identical.
    """
    if not CITEGATE.exists():
        return []
    sys.path.insert(0, str(SRC.parent))
    from omnex.rag import ingest

    twin = _load(CITEGATE, "citegate_grounding_invariant")
    violations: list[Violation] = []
    if ingest._ABBREVIATIONS != twin._ABBREVIATIONS:
        only_engine = sorted(ingest._ABBREVIATIONS - twin._ABBREVIATIONS)
        only_twin = sorted(twin._ABBREVIATIONS - ingest._ABBREVIATIONS)
        violations.append(
            Violation(
                "rag/ingest.py vs citegate/grounding.py",
                f"abbreviation sets differ — only in engine: {only_engine}, "
                f"only in citegate: {only_twin}",
            )
        )
    for label, ours, theirs in (
        ("_SENTENCE", ingest._SENTENCE.pattern, twin._SENTENCE.pattern),
        ("_CITATION_SPAN", ingest._CITATION_SPAN.pattern, twin._CITATION_SPAN.pattern),
        ("_MASK_REF", ingest._MASK_REF.pattern, twin._MASK_REF.pattern),
    ):
        if ours != theirs:
            violations.append(
                Violation("rag/ingest.py vs citegate/grounding.py", f"{label} differs")
            )
    return violations


# ── 6. the suite needs nothing installed ──────────────────────────────────
def no_required_dependencies() -> list[Violation]:
    """`pyproject.toml` declares no runtime dependency.

    This is what makes the whole suite runnable on a bare interpreter, which is
    in turn why it actually gets run. Heavy libraries sit behind Protocol
    adapters as optional extras, and the first required dependency is the one
    that quietly ends that.
    """
    config = tomllib.loads((ENGINE / "pyproject.toml").read_text(encoding="utf-8"))
    required = config.get("project", {}).get("dependencies") or []
    return [
        Violation("engine/pyproject.toml", f"required dependency {name!r}") for name in required
    ]


# ── 7. no live listing promises more than exists ──────────────────────────
def live_listings_are_covered(root: Path | None = None) -> list[Violation]:
    """A listing that is SELLING may not promise more than QC passed.

    The rule is not "you must have 170 images". It is "you must not sell 170 you
    do not have", and the difference is what keeps this from being a permanently
    red build that people learn to ignore. `packs/listing.json` carries `live`
    per offer, mirroring `lib/modules/registry.ts`'s `enabled`: nothing is live
    today, so nothing is violated today, and the gate bites the moment somebody
    publishes.

    Measured while writing this: the €49 Complete Vault sells "170+ images" and
    the four QC manifests total 80. That is not a rounding error — it is a
    refund, a one-star review, and on Etsy an account risk, discovered by the
    buyer after paying.
    """
    packs = root or (REPO / "packs")
    checker = REPO / "packs" / "listing_check.py"
    if not checker.exists():
        return []
    module = _load(checker, "packs_listing_check_invariant")
    listing = module.load_listing(packs / "listing.json")

    live = {
        name
        for group in ("packs", "bundles")
        for name, offer in (listing.get(group) or {}).items()
        if offer.get("live")
    }
    if not live:
        return []

    shortfalls, _ = module.audit(listing, packs)
    by_name = {
        str(offer["listing_name"]): name
        for group in ("packs", "bundles")
        for name, offer in (listing.get(group) or {}).items()
    }
    return [
        Violation(f"packs/listing.json:{by_name.get(s.listing, s.listing)}", str(s))
        for s in shortfalls
        if by_name.get(s.listing) in live
    ]


# ── 8. a binding names a credential, it never carries one ─────────────────
def bindings_carry_no_credentials() -> list[Violation]:
    """The n8n catalogue is committed, and a key in a committed file is an incident.

    `compile/n8n.py` scans the workflow it emits, but that scan runs at emit time
    on a document nobody keeps. This scans the file in the repository, which is
    the one that gets pushed — the same rule at the place where it is permanent
    rather than momentary.

    It also refuses a confirmation with nobody behind it, because `confirmed`
    is what `require_confirmed=True` reads before letting a workflow run
    unattended, and a claim no person made is the only way that gate opens by
    accident.
    """
    catalogue = ENGINE / "ontology" / "n8n_bindings.json"
    if not catalogue.exists():
        return []
    sys.path.insert(0, str(ENGINE / "src"))
    from omnex.core.errors import ValidationFailed
    from omnex.factory.compile import bindings

    try:
        bindings.load(catalogue)
    except ValidationFailed as exc:
        return [
            Violation("engine/ontology/n8n_bindings.json", str(problem))
            for problem in exc.context.get("problems", [str(exc)])
        ]
    return []


# ── 9. an install delivers what it declares, or says it does not ──────────
def every_extra_declares_what_it_delivers() -> list[Violation]:
    """`pip install omnex-engine[agents]` installed two libraries and did nothing.

    Six of twelve extras had zero of their declared dependencies imported
    anywhere when this was written. The install succeeds, so the promise looks
    kept, and the user gets a dependency instead of a capability — the same shape
    as a listing selling 170 images against 80, which `live_listings_are_covered`
    already guards from the other side.

    The rule is deliberately NOT "every extra must have an adapter". A
    declaration is evidence of an intended interface, not proof the interface
    should exist, so `unsupported` with a stated reason passes and silence does
    not. Writing six adapters to make twelve declarations look complete would be
    decorative architecture, which is the failure this registry exists against.
    """
    sys.path.insert(0, str(ENGINE / "scripts"))
    import extras_check

    manifest = tomllib.loads((ENGINE / "pyproject.toml").read_text(encoding="utf-8"))
    report = extras_check.check(manifest, extras_check.importers())
    return [Violation("engine/pyproject.toml", problem) for problem in report.problems] + [
        Violation("engine/src/omnex", problem) for problem in extras_check.prose_adapters()
    ]


#: Every checker this module offers, by the name `invariants.json` refers to.
CHECKERS = {
    "money_never_float": money_never_float,
    "clock_is_injected": clock_is_injected,
    "ordered_strenum_defines_all_comparisons": ordered_strenum_defines_all_comparisons,
    "one_symbol_resolver": one_symbol_resolver,
    "twin_splitters_agree": twin_splitters_agree,
    "no_required_dependencies": no_required_dependencies,
    "live_listings_are_covered": live_listings_are_covered,
    "bindings_carry_no_credentials": bindings_carry_no_credentials,
    "every_extra_declares_what_it_delivers": every_extra_declares_what_it_delivers,
}


def load_registry(path: Path | None = None) -> list[dict[str, object]]:
    source = path or (ENGINE / "ontology" / "invariants.json")
    raw = json.loads(source.read_text(encoding="utf-8"))
    entries: list[dict[str, object]] = raw["invariants"]
    return entries
