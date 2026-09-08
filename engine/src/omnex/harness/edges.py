"""Which work is actually dependent, and which was only written in a line.

The mistake everybody makes is treating "and then" as a dependency. *Summarise
this file and then tell me the weather* is two independent jobs a linear script
chains for no reason, and the second waits on the first for nothing.

The diagnostic is one question, asked per edge: **does the downstream node read
the upstream node's output?** If yes it is a real edge and the order stands. If
no there is no edge, and the wait is pure cost.

`Plan.connect()` refuses an edge where no data crosses, rather than accepting it
and quietly serialising work that could have run at once. Refusing is the point:
an accepted-but-useless edge is invisible, and invisible serialisation is the
thing that makes a fleet slow for reasons nobody can find.

## And the honest half

Most tasks are not graphs. If no two nodes are independent, `parallelisable()`
returns nothing and `advice()` says so — this is a chain, and fanning it out
buys coordination cost and no speed. Forcing a graph onto sequential work is a
way to spend money on topology.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.errors import ValidationFailed

__all__ = ["Node", "Plan"]


@dataclass(frozen=True)
class Node:
    """One unit of work: one job, its inputs, its output."""

    key: str
    #: Names of the values this node consumes.
    reads: frozenset[str] = frozenset()
    #: Name of the value it produces, if any.
    produces: str = ""

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValidationFailed("a node needs a key")


@dataclass
class Plan:
    """Nodes plus the edges that survived the does-data-cross test."""

    nodes: dict[str, Node] = field(default_factory=dict)
    #: downstream key -> upstream keys it genuinely depends on.
    edges: dict[str, set[str]] = field(default_factory=dict)

    def add(self, node: Node) -> Node:
        if node.key in self.nodes:
            raise ValidationFailed(f"duplicate node {node.key!r}")
        self.nodes[node.key] = node
        self.edges.setdefault(node.key, set())
        return node

    def connect(self, upstream: str, downstream: str) -> None:
        """Declare a dependency. Refused unless data actually crosses.

        The refusal message names the missing value, because the usual cause is
        a genuine edge whose `produces`/`reads` names simply do not match — and
        an error that says "no data crosses" without saying what was expected
        sends people to the wrong fix.
        """
        for key in (upstream, downstream):
            if key not in self.nodes:
                raise ValidationFailed(f"unknown node {key!r}")
        if upstream == downstream:
            raise ValidationFailed(f"{upstream!r} cannot depend on itself")

        produced = self.nodes[upstream].produces
        consumed = self.nodes[downstream].reads
        if not produced or produced not in consumed:
            raise ValidationFailed(
                f"no data crosses from {upstream!r} to {downstream!r}: it produces "
                f"{produced or 'nothing'!r} and {downstream!r} reads "
                f"{sorted(consumed) or 'nothing'}. An 'and then' is not a dependency — "
                "these can run at the same time",
                upstream=upstream,
                downstream=downstream,
            )

        self.edges[downstream].add(upstream)
        if self._creates_cycle(downstream):
            self.edges[downstream].discard(upstream)
            raise ValidationFailed(f"{upstream!r} → {downstream!r} closes a cycle")

    def _creates_cycle(self, start: str) -> bool:
        seen: set[str] = set()
        stack = [start]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            for parent in self.edges.get(current, set()):
                if parent == start:
                    return True
                stack.append(parent)
        return False

    def waves(self) -> list[list[str]]:
        """Nodes grouped into rounds that may run together.

        Each wave is everything whose dependencies are already satisfied. The
        number of waves is the real critical path; the width of each is how much
        parallelism the work actually contains.
        """
        remaining = dict(self.edges)
        done: set[str] = set()
        out: list[list[str]] = []

        while remaining:
            ready = sorted(key for key, deps in remaining.items() if deps <= done)
            if not ready:
                raise ValidationFailed("dependency cycle — no node is ready to run")
            out.append(ready)
            done.update(ready)
            for key in ready:
                remaining.pop(key)
        return out

    def parallelisable(self) -> list[list[str]]:
        """Waves containing more than one node — the work that need not queue."""
        return [wave for wave in self.waves() if len(wave) > 1]

    def advice(self) -> str:
        """Say plainly whether a graph is the right shape here."""
        waves = self.waves()
        wide = self.parallelisable()
        if not wide:
            return (
                f"This is a chain of {len(waves)} steps: every node reads the previous "
                "node's output, so there is nothing to run at once. A graph adds "
                "coordination cost and no speed — keep the loop."
            )
        widest = max(len(w) for w in waves)
        return (
            f"{len(self.nodes)} nodes in {len(waves)} waves, widest {widest}. "
            f"{len(wide)} wave(s) can run in parallel."
        )
