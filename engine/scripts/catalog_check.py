"""The model price catalogue's own freshness check, actually wired to a gate.

`omnex.llm.catalog.ModelCatalog.assert_fresh()` and `models.json`'s own
committed comment both state, in prose, that a deploy fails on a catalogue
older than `STALE_AFTER_DAYS` -- "stale prices flow straight into routing
decisions and customer bills where nothing about the program's behaviour
reveals they are wrong." Nothing called it. `assert_fresh()` is exercised in
`test_router.py` (it raises correctly, in isolation, against a synthetic
future date), but no gate script, no CI workflow, and no other module in this
repository ever imports `omnex.llm.catalog` at all -- confirmed by grepping
every script and every workflow. A safeguard that is only ever invoked by its
own unit test is not a safeguard in production; it is a claim about one,
which is precisely the shape this repository's own culture is built to catch.

This script is that missing caller: load the real committed catalogue and
fail loudly, the same way the module's own docstring already says the deploy
path should, so `models.json`'s comment stops describing a check that does
not exist anywhere it can run.

    python scripts/catalog_check.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE / "src"))

from omnex.core.errors import ConfigurationError  # noqa: E402
from omnex.llm.catalog import ModelCatalog  # noqa: E402


def main() -> int:
    catalog = ModelCatalog.load()
    try:
        catalog.assert_fresh()
    except ConfigurationError as exc:
        print(f"FAIL {exc}")
        return 1
    print(
        f"{catalog.source}: {len(catalog.specs)} model(s), verified "
        f"{catalog.verified_on.isoformat()} ({catalog.age_days()} days ago) -- fresh."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
