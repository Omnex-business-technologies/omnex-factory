"""P13 — agent memory.

Short-term buffer, durable recall, context compression and eviction, shaped by
three failures that happen rather than three that might:

- **Recency-only eviction drops the important thing first.** "I am allergic to
  peanuts", said in turn 2, outranks the last five turns of scheduling chatter,
  and a sliding window discards it precisely because it is old. Eviction scores
  salience against age, and pinned entries are never evictable.
- **Compression that loses facts is worse than forgetting.** Summarising reads
  well and silently drops the one number the next question needs. Compression
  here EXTRACTS statements verbatim, and `preserves()` can check.
- **Last-write-wins sync loses edits with no error anywhere.** Entries carry a
  per-key version and a conflict is reported, because which edit should win is
  a product decision and storage is the wrong layer to make it.
"""

from .memory import (
    CompressionResult,
    EvictionPolicy,
    LongTermMemory,
    MemoryEntry,
    MemoryKind,
    ShortTermBuffer,
    compress,
)

__all__ = [
    "CompressionResult",
    "EvictionPolicy",
    "LongTermMemory",
    "MemoryEntry",
    "MemoryKind",
    "ShortTermBuffer",
    "compress",
]
