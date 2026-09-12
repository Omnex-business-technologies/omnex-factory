"""The root README's quoted engine test count, checked against the repository.

    python scripts/readme_check.py            # rewrite README.md's number
    python scripts/readme_check.py --check    # fail if it disagrees

Sovereign Execution Standard, §14 (CLAIM PURGE) and §33 (Documentation
Standard): a hand-quoted figure is a claim with a date, not a fact, and this
repository has already paid for exactly this drift once — CLAUDE.md's own
"Lab notes" section records four stale figures found in one pass, because a
number a script derives and a human retypes into prose agrees with reality
only until the next thing changes it. That fix covers CLAUDE.md. It has never
covered `README.md`, which quoted "1,231 tests" through five phases of this
session's own work while the real count moved to 1,286 — the exact same class
of drift, in a file nothing was checking.

No second test-counting implementation: `count_engine_tests()` shells out to
`pytest --collect-only -q`, the same command a person runs by hand, rather
than re-deriving a count from source another way that could disagree with
what `pytest tests/ -q` itself would report.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
README = REPO / "README.md"

#: `pytest --collect-only -q` prints one summary line per file, "path: N".
_FILE_COUNT = re.compile(r"^\S+\.py: (\d+)$", re.MULTILINE)
#: The exact sentence in README.md this script owns. Narrow on purpose: a
#: pattern loose enough to match other numbers in the file would as happily
#: rewrite the wrong one.
_QUOTED = re.compile(r"[\d,]+ tests, zero required dependencies")


def count_engine_tests() -> int:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
        cwd=ENGINE,
        capture_output=True,
        text=True,
        check=False,
    )
    return sum(int(n) for n in _FILE_COUNT.findall(result.stdout))


def main() -> int:
    check = "--check" in sys.argv
    real = count_engine_tests()
    if real == 0:
        print(
            "FAIL pytest --collect-only found 0 tests; something is broken upstream of this check"
        )
        return 1

    text = README.read_text(encoding="utf-8")
    match = _QUOTED.search(text)
    if match is None:
        print("FAIL README.md's test-count sentence was not found by this script's own pattern")
        return 1

    quoted = int(match.group().split()[0].replace(",", ""))
    if quoted == real:
        print(f"README.md's quoted engine test count ({real:,}) matches the repository.")
        return 0

    if check:
        print(f"FAIL README.md says {quoted:,} engine tests; the repository has {real:,}")
        return 1

    README.write_text(
        _QUOTED.sub(f"{real:,} tests, zero required dependencies", text), encoding="utf-8"
    )
    print(f"updated README.md: {quoted:,} -> {real:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
