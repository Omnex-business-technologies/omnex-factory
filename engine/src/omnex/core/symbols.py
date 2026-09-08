"""Resolve a dotted symbol by importing it. One implementation, deliberately.

This is three lines of `importlib` and it lives in the package rather than in
the script that first needed it, for a reason this repository has already paid
for once: the sentence splitter exists twice, in `rag/ingest.py` and in
citegate, and a quadratic bug fixed in one survived in the other for a further
commit. Two copies of a check drift, and the drift is invisible because both
copies keep answering.

`scripts/ontology_map.py`, `scripts/node_map.py` and `omnex.factory` all ask the
same question — *does this name actually exist?* — and they now ask it in the
same place. The factory is why it moved: a spec that names a capability no
symbol backs is a spec that reads correctly and builds nothing.
"""

from __future__ import annotations

import importlib

__all__ = ["resolve", "resolves"]


def resolve(symbol: str) -> str | None:
    """Import a dotted symbol. Returns the reason it failed, or None on success.

    The module half is derived from the symbol rather than taken from any
    declared module list, so a caller can cite `omnex.core.Money` without having
    to claim the whole of `omnex.core`.

    The reason is returned rather than raised because every caller collects
    reasons and reports them together — being refused one at a time is how
    somebody concludes the check is the obstacle.
    """
    module_path, _, attribute = symbol.rpartition(".")
    if not module_path or not attribute:
        return "not a dotted path"
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        return f"module will not import ({exc})"
    if not hasattr(module, attribute):
        return f"{module_path} has no attribute {attribute!r}"
    return None


def resolves(symbol: str) -> bool:
    return resolve(symbol) is None
