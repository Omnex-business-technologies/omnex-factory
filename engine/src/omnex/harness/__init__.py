"""A long-running harness whose every gate is priced.

Four independent sources — an Anthropic engineering talk, a graph-engineering
write-up, Karpathy's AutoResearch, and a long practitioner course — arrive at
the same handful of rules from different directions. Where four people who have
never coordinated reach the same conclusion, that is the design, so it lives in
the types here rather than in a prompt:

    worth_it.py   Seven conditions, all required, before anything runs. The
                  expensive mistake in this category is not a bad loop — it is a
                  good loop pointed at a task that could never repay it.
    contract.py   Generator and evaluator negotiate what "done" means, granular
                  enough to be actionable, before a line is written. FROZEN
                  criteria may be added to and never weakened: the anchor an
                  optimiser would otherwise learn to relax.
    evaluator.py  The critic, with its own context enforced by construction —
                  there is no parameter through which the maker's transcript can
                  reach it. Grades a real signal; "unchecked" is never "passed".
    edges.py      An edge exists only where data crosses. Refuses "and then",
                  and says plainly when the work is a chain and a graph would
                  buy nothing.
    isolation.py  Where each worker works, how results merge, what happens when
                  two disagree. Two workers cannot be handed one writable tree.
    state.py      The log of what was tried, as JSON on disk. Each entry carves
                  a piece out of the search space so the next run is cheaper.
    meta.py       The outer loop. Theirs watches the score; ours watches
                  PICO-DOLLAR COST PER ACCEPTED CHANGE, which is the only way to
                  tell genuine progress from paying more each round to stand
                  still.

## What makes this ours rather than a reimplementation

Every published version of this pattern gates on a score. This one gates on a
score, a refusal rate and exact money — numbers `engine/` already produces. A
harness that cannot say what a improvement cost cannot tell you whether to keep
running it.

## The honest part

Comprehension debt compounds. The faster a loop ships work nobody has read, the
wider the gap between what this repository contains and what anyone understands
about it, and a smooth-running loop charges interest on that gap daily. The same
harness makes one person faster on work they understand and another person
fluent in a system they have never read. Nothing in this package can tell the
difference; the person configuring it can.
"""

from .contract import Contract, Criterion, Proposal
from .edges import Node, Plan
from .evaluator import CheckResult, Evaluator, Grade, Rubric, Verdict
from .isolation import DisagreementPolicy, Fleet, MergePolicy, Workspace
from .meta import Diagnosis, Health, Intervention, diagnose, mean_cost_per_accepted
from .state import Attempt, RunState
from .worth_it import Condition, evaluate

__all__ = [
    "Attempt",
    "CheckResult",
    "Condition",
    "Contract",
    "Criterion",
    "Diagnosis",
    "DisagreementPolicy",
    "Evaluator",
    "Fleet",
    "Grade",
    "Health",
    "Intervention",
    "MergePolicy",
    "Node",
    "Plan",
    "Proposal",
    "Rubric",
    "RunState",
    "Verdict",
    "Workspace",
    "diagnose",
    "evaluate",
    "mean_cost_per_accepted",
]
