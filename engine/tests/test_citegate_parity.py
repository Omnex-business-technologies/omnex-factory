"""The two splitters, held to each other. A convention is not a check.

`engine/src/omnex/rag/ingest.py` and `oss/citegate/src/citegate/grounding.py`
hold independent copies of one sentence splitter, on purpose: citegate ships
dependency-free and may not import the engine. CLAUDE.md handles the risk with a
sentence — *fix a splitter bug in both, or check the other before claiming it is
fixed* — and that sentence has already failed once, when a quadratic restore was
repaired in the engine and survived in citegate for a further commit.

It failed a second time, and differently, which is why this file exists rather
than a firmer sentence. The two functions were line-for-line equivalent; the
DATA behind them was not. The engine's abbreviation set had grown by `dr.`,
`mr.` and `ms.` and citegate's had not, so citegate split

    "Mr. Lee and Ms. Park disagreed."

into four fragments. Comparing the algorithms found nothing. Only running both
over the same text does.

That matters more for citegate than for the engine, because a fragment is
exactly what its grounding check cannot handle: `'Mr.'` carries no claim and no
citation, and a claim cannot be verified against half of the sentence that
supports it.

## Why the corpus is adversarial rather than large

Each case here is a documented reason one of these two files is written the way
it is: masked citations, abbreviation merging, the quote and bracket characters
in the split lookahead. A thousand lines of ordinary prose would agree in both
implementations and prove nothing, because ordinary prose is not where a
splitter differs.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

from omnex.rag.ingest import split_sentences as engine_split

CITEGATE = (
    Path(__file__).resolve().parents[2] / "oss" / "citegate" / "src" / "citegate" / "grounding.py"
)

pytestmark = pytest.mark.skipif(not CITEGATE.exists(), reason="citegate is not in this checkout")


def _load_citegate() -> ModuleType:
    """Import the twin by path.

    By path rather than by installing it, because the engine may not depend on
    citegate and citegate may not depend on the engine — that independence is
    the whole reason there are two copies. Registered in `sys.modules` before
    execution because `@dataclass` resolves its own module during class
    creation.
    """
    spec = importlib.util.spec_from_file_location("citegate_grounding", CITEGATE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["citegate_grounding"] = module
    spec.loader.exec_module(module)
    return module


#: Every entry is a case one of the two files has a comment about.
CORPUS: tuple[str, ...] = (
    # Abbreviations — the case that had actually diverged.
    "Dr. Smith reported a 12% gain [p. 4]. The trial ended early.",
    "Mr. Lee and Ms. Park disagreed. Both cited Table 2.",
    "The result held, e.g. Table 4 [p. 9]. Nothing else changed.",
    "See i.e. the appendix, no. 7, fig. 3 and approx. 12 others. Then stop.",
    "Revenue grew vs. last year. Margin did not.",
    "Compare cf. the 2024 filing, etc. That is the whole list.",
    # Citations, which are masked before splitting and restored after.
    "Twenty percent [p. 12]. Thirty the year after [pp. 13-14].",
    "The claim is supported [source: annual report, page 4]. The next is not.",
    "Nothing here is cited. Nor here.",
    # The lookahead characters: capitals, digits, quotes, brackets, parens.
    'He said "no". "Yes" came later.',
    "The figure is 12. 13 was the revision.",
    "That was the finding. (The caveat came later.)",
    "It ended there. [Editor's note follows.]",
    # Shapes that must not crash either copy.
    "",
    "   ",
    "One sentence with no terminator",
    "Ends with a citation [p. 1]",
    "Multiple\nlines\nwith no terminators",
    "A. B. C. D.",
    "Ellipsis... then more. And an end.",
)


def test_the_twins_split_every_case_identically() -> None:
    """The check the prose could not make.

    Not "both are correct" — both being wrong the same way is a separate
    problem, and each file has its own tests for correctness. This is the
    narrower claim the two-copy design actually needs: whatever they do, they do
    the same thing.
    """
    citegate = _load_citegate()
    differences: list[str] = []
    for text in CORPUS:
        ours, theirs = engine_split(text), citegate.split_sentences(text)
        if ours != theirs:
            differences.append(f"{text!r}\n    engine  : {ours}\n    citegate: {theirs}")
    assert not differences, "the splitters have diverged:\n  " + "\n  ".join(differences)


def test_the_abbreviation_sets_are_the_same_set() -> None:
    """The data behind the algorithm, which is where they actually diverged.

    Asserted directly as well as through behaviour, because a set that grows on
    one side is the cheapest possible divergence to make and the hardest to see
    in a diff of two files nobody views side by side.
    """
    citegate = _load_citegate()
    from omnex.rag.ingest import _ABBREVIATIONS as ours

    theirs = citegate._ABBREVIATIONS
    assert ours == theirs, (
        f"only in engine: {sorted(ours - theirs)}; only in citegate: {sorted(theirs - ours)}"
    )


def test_the_split_pattern_is_the_same_pattern() -> None:
    citegate = _load_citegate()
    from omnex.rag.ingest import _CITATION_SPAN, _MASK_REF, _SENTENCE

    assert _SENTENCE.pattern == citegate._SENTENCE.pattern
    assert _CITATION_SPAN.pattern == citegate._CITATION_SPAN.pattern
    assert _MASK_REF.pattern == citegate._MASK_REF.pattern, (
        "the placeholder restore differs — this is the quadratic that was fixed "
        "in one copy and survived in the other for a commit"
    )


def test_the_parity_check_can_actually_fail() -> None:
    """Proof this file is comparing two things rather than one thing with itself.

    The whole corpus agreeing is only evidence if disagreement would be seen. A
    text the engine merges on an abbreviation and a hand-rolled splitter without
    that abbreviation does not must come out different.
    """
    citegate = _load_citegate()
    text = "Dr. Smith reported a gain. The trial ended."

    without_titles = {a for a in citegate._ABBREVIATIONS if a not in ("dr.", "mr.", "ms.")}
    original = citegate._ABBREVIATIONS
    try:
        citegate._ABBREVIATIONS = without_titles
        assert citegate.split_sentences(text) != engine_split(text)
    finally:
        citegate._ABBREVIATIONS = original
    assert citegate.split_sentences(text) == engine_split(text)


def test_neither_copy_is_quadratic_in_citations() -> None:
    """The growth-ratio guard, applied to both at once.

    The original quadratic cost 4.5s on a 4,000-sentence filing and was
    invisible on the three-sentence answers the benchmark measured. Ten times
    the document must cost roughly ten times, not a hundred.
    """
    citegate = _load_citegate()
    small = " ".join(f"Claim {i} is supported [p. {i}]." for i in range(200))
    large = " ".join(f"Claim {i} is supported [p. {i}]." for i in range(2000))

    for name, split in (("engine", engine_split), ("citegate", citegate.split_sentences)):
        assert len(split(small)) == 200, name
        assert len(split(large)) == 2000, name
