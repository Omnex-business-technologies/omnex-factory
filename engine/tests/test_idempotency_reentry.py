from __future__ import annotations

import pytest

from omnex.core import PermanentError
from omnex.pipeline.queue import IdempotencyStore


def test_same_thread_reentry_fails_without_releasing_outer_guard():
    store = IdempotencyStore()

    def reenter() -> None:
        with store.serialise("nested-key"):
            pytest.fail("reentrant same-key work must not enter")

    with store.serialise("nested-key"):
        with pytest.raises(PermanentError, match="recursive execution"):
            reenter()
        assert store._key_locks["nested-key"][1] == 1
    assert store._key_locks == {}
