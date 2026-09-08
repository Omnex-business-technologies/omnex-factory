"""The agent factory: nodes compile into a specification that can be refused.

Parts 1 to 4 of this chain answered *what should exist* — 509 figures, 507
nodes, a ranking, and the top-ranked node built. This answers the next question:
what turns a set of capabilities into an agent somebody can approve, cost and
grade, rather than into a paragraph that sounds like one.

Two things carry the weight.

**A spec is bound to itself.** `AgentSpec.agree()` returns a fingerprint of the
specification and a fingerprint of the `harness.Contract` derived from it. Every
later gate re-checks both. An agent approved on an economics gate and then
quietly re-scoped was approved on numbers that no longer describe it, and
nothing downstream would otherwise notice — the same failure `hitl` prevents for
human approvals, prevented the same way.

**The gate order is a type.** `idea → market → unit economics → architecture →
simulation → evaluation → security → deploy → observe → scale or kill`, with
`Pipeline.advance()` refusing anything out of order. As prose this is a diagram
everybody agrees with and nobody follows, because the interesting stage is
architecture and the economics gate becomes something that happens after launch
when the margin turns out negative.

`worth_it` runs at the head of that order: seven answers that cost nothing,
before anything that costs something.
"""

from .economics import MINIMUM_RUNS, AgentEconomics, Margin, Run, RunCost
from .feedback import NodeClaim, Observation, Source, claim, observe, to_run_state
from .gates import Gate, Pipeline, Stage, start
from .portfolio import Asset, Decision, Portfolio, Recommendation
from .spec import AgentSpec, Capability, CostModel, Paradigm, Tool

__all__ = [
    "MINIMUM_RUNS",
    "AgentEconomics",
    "AgentSpec",
    "Asset",
    "Capability",
    "CostModel",
    "Decision",
    "Gate",
    "Margin",
    "NodeClaim",
    "Observation",
    "Paradigm",
    "Pipeline",
    "Portfolio",
    "Recommendation",
    "Run",
    "RunCost",
    "Source",
    "Stage",
    "Tool",
    "claim",
    "observe",
    "start",
    "to_run_state",
]
