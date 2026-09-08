---
name: cost-router
description: Route LLM calls between a cheap and an expensive tier, verify the cheap answer, and escalate only when it fails. Use when cutting inference spend without losing accuracy, deciding whether a router is worth building at all, or computing the break-even escalation rate for a given pair of models.
---

# Cost router

Send everything to the cheap model first. Verify the answer. Escalate only what
fails verification.

Measured on a 200-task benchmark (120 mechanically easy, 60 genuinely hard, 20
hard tasks phrased to look easy):

| | always-cheap | **routed** | always-strong |
|---|--:|--:|--:|
| accuracy | 60.0% | **100.0%** | 100.0% |
| spend | 3.3% | **42.4%** | 100% |

Reproduce: `cd engine && .venv/bin/python scripts/skill_numbers.py`

The accuracy row is the part that makes the spend row mean anything. A router
that is cheaper and worse is not a router, it is a downgrade with extra steps.

## The one number that decides whether to bother

**Break-even escalation rate = 1 − (cheap price ÷ expensive price).**

Escalating means paying twice: once for the cheap attempt, once for the real
one. Below the break-even rate the cheap attempts you *didn't* have to escalate
have already paid for the ones you did.

| price gap | break-even | reading |
|---|--:|---|
| 30× cheaper | 96.7% | escalation is nearly free; route everything cheap first |
| 10× cheaper | 90.0% | comfortable |
| 2× cheaper | 50.0% | escalate more than half and you are losing money |

The benchmark above ran at **14.3% escalation against a 97.0% break-even** —
not close to the line. If your two tiers are 2× apart and your work is hard,
compute this before building anything; the answer may be "don't".

```python
from omnex.router import break_even_escalation_rate
from omnex.core import Money

break_even_escalation_rate(Money.from_usd("0.10"), Money.from_usd("3.00"))  # 0.967
```

## Use it

```python
from omnex.router import Router, RoutingPolicy

router = Router([cheap_model, strong_model], policy=RoutingPolicy())
router.calibrate()

result = router.route([Message("user", prompt)])
result.completion.text   # the answer
result.escalated         # did the cheap tier fail verification
result.total_cost        # exact, in pico-dollars — both attempts if it escalated
```

`router.economics.report()` prints observed escalation rate, break-even, and
money saved. `is_losing_money()` is true when escalation has passed break-even —
check it in production rather than assuming the benchmark still holds.

## How the classifier and the verifier divide the work

The classifier reads the prompt and picks a starting tier. It gets the obvious
cases right and is wrong in one specific, systematic way: **length is not
difficulty.** A 4,000-word extraction prompt is easy; a one-line "compare these
two strategies and explain the trade-offs" is not.

The verifier is what catches the rest. Twenty of the 200 benchmark tasks are
hard questions phrased as lookups — *"what is the capital of the country whose
central bank set rate 17 in 1997?"* — and the classifier routes every one of
them cheap. The verifier fails the cheap answer and escalation recovers the
accuracy. Without it, routed accuracy is 90%, not 100%.

So: a classifier alone is a downgrade. The verifier is not optional.

## Fan-out: the saving that usually isn't

The companion pattern — spawn N cheap researchers, hand their findings to one
expensive synthesiser — is normally justified by the per-token price gap
between tiers. **That is the wrong comparison**, and `fanout_plan()` prices the
right one:

```python
from omnex.router import TokenShape, fanout_plan

plan = fanout_plan(
    legs=6,
    shape=TokenShape(context=20_000, research_output=800,
                     synthesis_output=1_500, divergent=True),
    cheap_in=Money.from_usd("3"),  cheap_out=Money.from_usd("15"),
    expensive_in=Money.from_usd("5"), expensive_out=Money.from_usd("25"),
)
plan.cheaper           # True
plan.break_even_legs   # 6
plan.verdict           # says which side of the line, and why
```

Two costs the price-gap argument drops: **every leg re-reads the prompt**, and
**the synthesiser pays the expensive input rate for every leg's output**. So one
flag decides the answer, and it inverts it:

| legs read | 6 legs vs one big call | reading |
|---|--:|---|
| **different** sources | **77%** | cheaper — the cheap tier does the bulk reading and compresses |
| the **same** prompt | **359%** | dearer — this buys answer diversity and latency, not money |

Same prices, same leg count, opposite verdict. At a 1.7× tier gap, consensus
fan-out over one shared prompt costs **three and a half times** the single call
it replaces. That can still be the right call — latency and diversity are worth
paying for — but it should be a decision, not a rounding error someone believed
was a 60% saving.

Reproduce both rows: `cd engine && .venv/bin/python scripts/skill_numbers.py`

## What this does not do

It does not know whether the cheap answer is *right*, only whether it passes
the verifier you supplied. `HeuristicVerifier` checks form — refusals, empty
answers, truncation, malformed JSON. `JsonVerifier` checks a schema. For
correctness you need a task-specific check, and if you cannot write one, the
honest position is that this task cannot be routed safely.

Verification cost is real and is counted: a verifier that itself calls a model
adds a call to every request, and at that point the break-even arithmetic above
changes. The included verifiers are local and free.
