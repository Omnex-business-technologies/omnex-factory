"""Fan-out economics: when do N cheap researchers beat one expensive call?

The published pattern is to spawn several cheap models to research in parallel
and hand their findings to one expensive model to synthesise. The argument for
it is always the tier price ratio — "the cheap tier is 60% less, so the research
legs cost 60% less" — and that argument is **incomplete in a way that costs
money**.

Two costs it leaves out:

**Every leg pays for the prompt.** One expensive call reads the context once.
Ten researchers read it ten times. At long contexts the duplicated input alone
can exceed everything the cheaper tier saved.

**The synthesiser's input grows with the fan-out.** It receives every leg's
output. Doubling the legs doubles what the expensive model must read before it
writes a token — so fan-out cost is not linear in `legs`, it is linear in legs
*on both sides* of the fence, and one of those sides is billed at the expensive
rate.

Put together there is a **break-even leg count**: below it fan-out is cheaper
than the single call it replaces, above it you are paying more for the privilege
of finishing sooner. `plan()` returns that number. Nothing in the material this
pattern comes from states it, because those demonstrations are run by people who
say out loud that money is not their bottleneck.

## Fan-out can still be right above break-even

Paying more to finish sooner is a legitimate trade — that is what latency is
worth. What is not legitimate is making that trade without knowing you made it.
`FanoutPlan.verdict` says which side of the line a configuration sits on and
what the extra time cost, so the decision is priced rather than assumed.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..core.errors import ValidationFailed
from ..core.money import Money

__all__ = ["FanoutPlan", "TokenShape", "plan"]


@dataclass(frozen=True)
class TokenShape:
    """The token counts a fan-out decision depends on.

    Estimates are fine — the answer is a ratio, and a proportional error in the
    inputs mostly cancels. What must not be guessed is `context`: underestimating
    the shared prompt is exactly what makes fan-out look free.
    """

    #: Material one researcher must read. Paid once per leg.
    context: int
    #: Tokens one researcher produces.
    research_output: int
    #: Tokens the synthesiser produces.
    synthesis_output: int
    #: Output of the single expensive call being replaced.
    baseline_output: int = 0
    #: Does each leg read DIFFERENT material?
    #:
    #: This single flag decides whether fan-out can save money at all, and
    #: getting it wrong inverts the answer.
    #:
    #: `True` — research fan-out. Leg 1 reads one source, leg 2 another. The
    #: single call it replaces would have had to read every source itself, so
    #: the baseline scales with `legs` too and the cheap tier is doing the bulk
    #: reading. This is where the saving lives: the researchers COMPRESS, and
    #: the expensive model reads summaries instead of sources.
    #:
    #: `False` — stochastic consensus. Every leg reads the same prompt and
    #: offers an independent opinion. The baseline reads it once. Fan-out then
    #: cannot be cheaper by construction: it is buying answer diversity, and it
    #: should be justified that way rather than on cost.
    divergent: bool = False

    def __post_init__(self) -> None:
        for name in ("context", "research_output", "synthesis_output", "baseline_output"):
            if getattr(self, name) < 0:
                raise ValidationFailed(f"{name} cannot be negative")

    @property
    def baseline(self) -> int:
        """The single call's output, defaulting to the synthesis length."""
        return self.baseline_output or self.synthesis_output


def _price(tokens: int, per_mtok: Money) -> Money:
    return Money.from_picos(tokens * per_mtok.picos // 1_000_000)


@dataclass(frozen=True)
class FanoutPlan:
    """What a fan-out costs against the single call it replaces."""

    legs: int
    fanout_cost: Money
    baseline_cost: Money
    #: Largest leg count that is not MORE expensive than the baseline. At
    #: exactly this count the two cost the same and the parallelism is free;
    #: one leg beyond it, every extra leg is bought with money. 0 when even a
    #: single researcher plus a synthesis pass beats answering directly.
    break_even_legs: int
    #: Share of fan-out spend that is duplicated context — the hidden term.
    duplicated_context_share: float

    @property
    def cheaper(self) -> bool:
        return self.fanout_cost < self.baseline_cost

    @property
    def ratio(self) -> float:
        """Fan-out spend as a fraction of the baseline. Below 1.0 is a saving."""
        if not self.baseline_cost.picos:
            return float("inf") if self.fanout_cost.picos else 1.0
        return self.fanout_cost.picos / self.baseline_cost.picos

    @property
    def verdict(self) -> str:
        # The duplicated-context share is stated on BOTH branches. It is the
        # term the usual argument omits, and it is just as worth knowing on a
        # configuration that is winning — it is what the win is sensitive to.
        tail = (
            f"Break-even is {self.break_even_legs} legs; "
            f"{self.duplicated_context_share:.0%} of the spend is re-read prompt."
        )
        if self.cheaper:
            return (
                f"{self.legs} legs cost {self.ratio:.0%} of the single call — cheaper AND "
                f"parallel. {tail}"
            )
        return (
            f"{self.legs} legs cost {self.ratio:.0%} of the single call. This buys latency, "
            f"not money: {tail}"
        )

    def report(self) -> str:
        return (
            f"fan-out {self.legs} → {self.fanout_cost.format_adaptive()} vs "
            f"{self.baseline_cost.format_adaptive()} baseline. {self.verdict}"
        )


def plan(
    *,
    legs: int,
    shape: TokenShape,
    cheap_in: Money,
    cheap_out: Money,
    expensive_in: Money,
    expensive_out: Money,
) -> FanoutPlan:
    """Price a fan-out against the single expensive call it replaces.

    Prices are per million tokens. All keyword-only: every one of these six
    numbers changes the answer, and a positional call site is where somebody
    later swaps input for output and never finds out.
    """
    if legs < 1:
        raise ValidationFailed("a fan-out needs at least one leg")

    # Researchers: each reads the whole context and writes its findings.
    research_in = _price(shape.context * legs, cheap_in)
    research_out = _price(shape.research_output * legs, cheap_out)

    # Synthesiser: reads every leg's output, writes the answer. Billed at the
    # expensive rate on BOTH sides, which is the term the tier-ratio argument
    # drops.
    synth_in = _price(shape.research_output * legs, expensive_in)
    synth_out = _price(shape.synthesis_output, expensive_out)

    fanout = research_in + research_out + synth_in + synth_out

    # The baseline is the honest part. When the legs read DIFFERENT material,
    # the single call it replaces has to read all of it — so the comparison
    # scales with `legs` on both sides and the cheap tier is genuinely doing the
    # bulk reading. When they read the SAME material, the single call reads it
    # once and fan-out cannot win on cost.
    baseline_context = shape.context * legs if shape.divergent else shape.context
    baseline = _price(baseline_context, expensive_in) + _price(shape.baseline, expensive_out)

    # Cost grows linearly in `legs` on both sides, so solve rather than search.
    fanout_per_leg = (
        _price(shape.context, cheap_in)
        + _price(shape.research_output, cheap_out)
        + _price(shape.research_output, expensive_in)
    )
    baseline_per_leg = _price(shape.context, expensive_in) if shape.divergent else Money.zero()
    slope = fanout_per_leg.picos - baseline_per_leg.picos
    fixed = baseline.picos - (baseline_per_leg.picos * legs) - synth_out.picos

    # slope <= 0 means each extra leg saves more than it costs, so fan-out never
    # stops winning and the only question is whether it wins at all.
    break_even = (legs if fixed >= 0 else 0) if slope <= 0 else max(0, fixed // slope)

    share = research_in.picos / fanout.picos if fanout.picos else 0.0

    return FanoutPlan(
        legs=legs,
        fanout_cost=fanout,
        baseline_cost=baseline,
        break_even_legs=int(break_even),
        duplicated_context_share=share,
    )
