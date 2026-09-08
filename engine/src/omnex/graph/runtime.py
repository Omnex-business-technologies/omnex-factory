"""A small state-machine runtime for agent workflows.

Written rather than imported, for reasons that are about testability rather than
not-invented-here. LangGraph is a good library and this is **not** an adapter
over it: the `agents` extra installs langgraph and crewai, nothing here imports
either, and the extra is declared `unsupported` in `pyproject.toml` with that
reason. An earlier version of this docstring pointed at a langgraph adapter
module that has never existed — prose that resolves to nothing reads exactly like
prose that resolves to something, which is why `scripts/extras_check.py` now
refuses a backticked adapter filename with no file behind it.

What writing the runtime gives that pulling LangGraph in as a hard dependency
does not:

- The whole engine's test suite stays dependency-free and runs in seconds.
- Checkpointing is a first-class value type, so P15's pause/resume can be
  asserted on directly — a run interrupted at node 3 and resumed in a *different
  process* must produce the same result, and that is hard to test through an
  abstraction that owns its own persistence.
- Budget enforcement (steps, wall clock, spend) is inside the loop rather than
  bolted onto it, so a runaway graph stops with a stated cause.

The design is deliberately small: nodes are functions from state to a state
patch, edges are either static or a function of state, and the state is an
immutable mapping updated by merging patches. That is enough for every graph in
this repo, and it means a node is a plain function that a test can call directly
with a dict.

**Patches, not mutation.** A node returns what changed rather than editing the
state in place. That is what makes checkpointing cheap, what makes a step
replayable, and what stops the classic bug where a node mutates a list the
previous node still holds a reference to.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from ..core.clock import Clock, Deadline, SystemClock
from ..core.errors import BudgetExceeded, ValidationFailed
from ..core.money import Money

__all__ = ["END", "START", "Budget", "Graph", "GraphRun", "Node", "State", "StepRecord"]

#: Terminal target. A node routing here ends the run.
END = "__end__"
START = "__start__"

State = Mapping[str, Any]
#: A node returns the keys it changed. Returning nothing means "no change".
Patch = Mapping[str, Any] | None
Node = Callable[[dict[str, Any]], Patch]
#: Conditional edge: given the state, name the next node.
Router = Callable[[dict[str, Any]], str]


@dataclass(frozen=True)
class Budget:
    """Three independent ceilings, because they fail differently.

    A step cap catches a loop that thrashes without spending. A spend cap
    catches one runaway generation. A wall-clock cap catches a hung provider
    that is consuming neither. Any one alone leaves a hole the other two cover.
    """

    max_steps: int = 25
    max_spend: Money = field(default_factory=lambda: Money.from_usd("0.50"))
    max_seconds: float = 55.0

    def __post_init__(self) -> None:
        if self.max_steps < 1:
            raise ValueError("max_steps must be at least 1")


@dataclass(frozen=True)
class StepRecord:
    """One executed node. The audit trail is a list of these."""

    index: int
    node: str
    #: Keys the node changed. Values are omitted — a step record that carries
    #: full state is a step record nobody can read and a log nobody can store.
    changed: tuple[str, ...]
    duration_seconds: float
    next_node: str


@dataclass
class GraphRun:
    """The result of a run, including everything needed to resume it."""

    state: dict[str, Any]
    steps: list[StepRecord] = field(default_factory=list)
    #: Where execution stopped. END means it finished.
    at: str = END
    #: Set when a budget stopped the run rather than the graph finishing.
    stopped_reason: str = ""
    spend: Money = field(default_factory=Money.zero)

    @property
    def finished(self) -> bool:
        return self.at == END and not self.stopped_reason

    @property
    def interrupted(self) -> bool:
        return self.at != END and not self.stopped_reason

    def checkpoint(self) -> dict[str, Any]:
        """A resumable snapshot. Plain JSON-able data, deliberately.

        Resumption has to survive a process restart — that is the entire point
        of P15's approval gates, where the human replies hours later and the
        worker that started the run is long gone.
        """
        return {
            "state": dict(self.state),
            "at": self.at,
            "spend_picos": self.spend.picos,
            "steps": [
                {
                    "index": s.index,
                    "node": s.node,
                    "changed": list(s.changed),
                    "duration_s": s.duration_seconds,
                    "next": s.next_node,
                }
                for s in self.steps
            ],
        }


class Graph:
    """Nodes, edges, and a run loop that respects a budget."""

    def __init__(self, budget: Budget | None = None, clock: Clock | None = None) -> None:
        self.budget = budget or Budget()
        self.clock = clock or SystemClock()
        self._nodes: dict[str, Node] = {}
        self._edges: dict[str, str] = {}
        self._routers: dict[str, Router] = {}
        #: Declared branch targets, where a router could name them. See
        #: `add_conditional_edge` for why this is optional.
        self._router_targets: dict[str, tuple[str, ...]] = {}
        self._entry: str = ""
        #: Nodes that stop the run and hand control back to the caller. P15's
        #: approval gates are these.
        self._interrupt_before: set[str] = set()

    # ── construction ──────────────────────────────────────────────────────
    def add_node(self, name: str, node: Node) -> Graph:
        if name in (START, END):
            raise ValidationFailed(f"{name!r} is reserved")
        if name in self._nodes:
            raise ValidationFailed(f"duplicate node {name!r}")
        self._nodes[name] = node
        return self

    def add_edge(self, source: str, target: str) -> Graph:
        self._edges[source] = target
        return self

    def add_conditional_edge(
        self, source: str, router: Router, targets: tuple[str, ...] = ()
    ) -> Graph:
        """A router, and optionally the set of nodes it may choose.

        Declaring `targets` moves a whole class of failure from run time to
        construction time. Without it, `validate()` can only check that the
        router's SOURCE exists; a router returning a typo'd node name is caught
        by `_next` mid-run, after every node before it has already spent money.
        With it, the typo fails before anything runs.

        Optional rather than required because a router computing its target
        dynamically cannot enumerate one, and forcing a wrong answer is worse
        than accepting no answer. Declared targets are also what lets a compiler
        read a graph's topology back out of it — a router is a closure, and
        nothing can recover the branches from a closure.
        """
        self._routers[source] = router
        if targets:
            self._router_targets[source] = tuple(targets)
        return self

    def set_entry(self, name: str) -> Graph:
        self._entry = name
        return self

    def interrupt_before(self, *names: str) -> Graph:
        self._interrupt_before.update(names)
        return self

    def validate(self) -> None:
        """Check the graph is runnable BEFORE running it.

        A dangling edge discovered mid-run has already spent money on the nodes
        before it. Every failure here is a construction error, so it belongs at
        construction time.
        """
        if not self._entry:
            raise ValidationFailed("no entry node set")
        if self._entry not in self._nodes:
            raise ValidationFailed(f"entry node {self._entry!r} does not exist")
        for source, target in self._edges.items():
            if source not in self._nodes:
                raise ValidationFailed(f"edge from unknown node {source!r}")
            if target != END and target not in self._nodes:
                raise ValidationFailed(f"edge to unknown node {target!r}")
        for source in self._routers:
            if source not in self._nodes:
                raise ValidationFailed(f"conditional edge from unknown node {source!r}")
        for source, targets in self._router_targets.items():
            for target in targets:
                if target != END and target not in self._nodes:
                    raise ValidationFailed(
                        f"router at {source!r} declares unknown target {target!r}"
                    )
        for name in self._nodes:
            if name not in self._edges and name not in self._routers:
                raise ValidationFailed(f"node {name!r} has no outgoing edge")

    def topology(self) -> dict[str, tuple[str, ...]]:
        """Every node and where it can go, as plain data.

        Exists so a compiler can read a built graph back out and compare it with
        what it meant to build. A compiler that cannot re-read its own output is
        not a compiler, and for the code target the output IS this object rather
        than a file — which makes the comparison stronger, not weaker: it checks
        the graph the runtime would actually execute.
        """
        out: dict[str, tuple[str, ...]] = {}
        for name in self._nodes:
            if name in self._router_targets:
                out[name] = self._router_targets[name]
            elif name in self._routers:
                out[name] = ()
            else:
                out[name] = (self._edges.get(name, END),)
        return out

    @property
    def entry(self) -> str:
        return self._entry

    # ── execution ─────────────────────────────────────────────────────────
    def run(
        self,
        initial: Mapping[str, Any],
        resume_from: Mapping[str, Any] | None = None,
        spend_of: Callable[[Mapping[str, Any]], Money] | None = None,
    ) -> GraphRun:
        """Execute until END, an interrupt, or a budget stop.

        `spend_of` reads accumulated spend out of the state, so the budget can
        be enforced without the runtime knowing anything about models or money
        beyond the `Money` type.
        """
        self.validate()

        if resume_from is not None:
            state = dict(resume_from["state"])
            current = str(resume_from["at"])
            spend = Money.from_picos(int(resume_from.get("spend_picos", 0)))
            steps = [
                StepRecord(
                    index=int(s["index"]),
                    node=str(s["node"]),
                    changed=tuple(s["changed"]),
                    duration_seconds=float(s["duration_s"]),
                    next_node=str(s["next"]),
                )
                for s in resume_from.get("steps", [])
            ]
        else:
            state = dict(initial)
            current = self._entry
            spend = Money.zero()
            steps = []

        deadline = Deadline.after(self.budget.max_seconds, self.clock)
        run = GraphRun(state=state, steps=steps, at=current, spend=spend)

        # Resuming means the gate at the resume point has already been passed —
        # the human answered. Without this, `resume()` stops at the same
        # interrupt it was resumed from, forever, and the workflow can never
        # move past its first approval.
        pending_interrupt_cleared = resume_from is not None

        while run.at != END:
            # Interrupt is checked BEFORE the step count, so a graph that stops
            # for approval on its last permitted step reports "waiting for a
            # human" rather than "out of budget" — different problems.
            if run.at in self._interrupt_before:
                if pending_interrupt_cleared:
                    pending_interrupt_cleared = False
                else:
                    return run  # interrupted; caller resumes from the checkpoint

            if len(run.steps) >= self.budget.max_steps:
                run.stopped_reason = f"step limit reached ({self.budget.max_steps})"
                return run
            if deadline.expired():
                run.stopped_reason = f"wall clock exceeded ({self.budget.max_seconds}s)"
                return run
            if spend_of is not None:
                run.spend = spend_of(run.state)
                if run.spend > self.budget.max_spend:
                    run.stopped_reason = (
                        f"spend {run.spend.format_adaptive()} exceeded "
                        f"{self.budget.max_spend.format_adaptive()}"
                    )
                    return run

            node = self._nodes.get(run.at)
            if node is None:
                raise ValidationFailed(f"no such node: {run.at!r}")

            started = self.clock.monotonic()
            patch = node(run.state)
            duration = self.clock.monotonic() - started

            changed: tuple[str, ...] = ()
            if patch:
                changed = tuple(sorted(patch))
                run.state.update(patch)

            following = self._next(run.at, run.state)
            run.steps.append(
                StepRecord(
                    index=len(run.steps),
                    node=run.at,
                    changed=changed,
                    duration_seconds=duration,
                    next_node=following,
                )
            )
            run.at = following

        if spend_of is not None:
            run.spend = spend_of(run.state)
        return run

    def _next(self, current: str, state: dict[str, Any]) -> str:
        router = self._routers.get(current)
        if router is not None:
            target = router(state)
            if target != END and target not in self._nodes:
                raise ValidationFailed(
                    f"router at {current!r} chose unknown node {target!r}",
                )
            return target
        return self._edges.get(current, END)

    def resume(
        self,
        checkpoint: Mapping[str, Any],
        patch: Mapping[str, Any] | None = None,
        spend_of: Callable[[Mapping[str, Any]], Money] | None = None,
    ) -> GraphRun:
        """Continue an interrupted run, optionally applying a human's decision."""
        snapshot = dict(checkpoint)
        if patch:
            snapshot["state"] = {**snapshot["state"], **patch}
        return self.run({}, resume_from=snapshot, spend_of=spend_of)

    def raise_if_stopped(self, run: GraphRun) -> GraphRun:
        """Turn a budget stop into an exception, for callers that prefer one.

        Not the default: a run that stopped at its ceiling usually has partial
        results worth returning, and `stopped_reason` says why they are partial.
        """
        if run.stopped_reason:
            raise BudgetExceeded(run.stopped_reason, node=run.at, steps=len(run.steps))
        return run
