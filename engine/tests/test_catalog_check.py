"""catalog_check.py -- the missing caller for ModelCatalog.assert_fresh().

`assert_fresh()` existed, was correct, and was exercised by `test_router.py`
against a synthetic date -- but nothing in this repository ever called it
against the real, committed `models.json`. A price catalogue could go stale
for months with every other gate green. This is that call, verified both
ways: it passes today, and it is proven capable of failing at all by pointing
it at a catalogue whose `verified_on` is deliberately old.
"""

from __future__ import annotations

import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE / "src"))
sys.path.insert(0, str(ENGINE / "scripts"))

import catalog_check  # noqa: E402

from omnex.llm.catalog import ModelCatalog  # noqa: E402


def test_the_committed_catalogue_is_fresh() -> None:
    """The whole point. A red run here means: go re-verify prices and bump
    `verified_on` -- never widen `STALE_AFTER_DAYS` to make this pass."""
    catalog = ModelCatalog.load()
    catalog.assert_fresh()


def test_main_passes_on_the_real_committed_catalogue() -> None:
    assert catalog_check.main() == 0


def test_main_fails_on_a_stale_catalogue(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Sabotage: a catalogue whose own `verified_on` is over a year old must
    make `main()` return non-zero, not just make `assert_fresh()` raise in
    isolation -- proving this script is a real, wired caller."""
    stale = tmp_path / "models.json"
    stale.write_text(
        """
        {
          "verified_on": "2020-01-01",
          "models": {
            "test/model": {
              "provider": "test",
              "tier": "small",
              "input_usd_per_mtok": "1",
              "output_usd_per_mtok": "2",
              "context_window": 1000,
              "max_output_tokens": 100
            }
          }
        }
        """
    )
    # Capture the real classmethod BEFORE patching -- replacing it with
    # something that calls `ModelCatalog.load` again would recurse into
    # itself once the attribute is overwritten.
    real_load = ModelCatalog.load
    monkeypatch.setattr(catalog_check.ModelCatalog, "load", lambda: real_load(stale))
    assert catalog_check.main() == 1
