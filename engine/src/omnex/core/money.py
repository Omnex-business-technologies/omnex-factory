"""Money, as exact integers. Never a float.

Two constraints collide here.

The first is the usual one: `0.1 + 0.2 != 0.3` in binary floating point, so a
per-request spend total accumulated as a float drifts, and a spend total that
drifts is a spend total that eventually disagrees with the invoice. P2 routes on
a budget and P10 bills a tenant from these numbers; both need addition to be
exact and to stay exact across a million requests.

The second is specific to LLM cost. Prices are quoted per MILLION tokens, and a
single token of a cheap model costs on the order of $0.00000005. Micro-dollars
(1e-6), the usual choice for payments, round that to zero — so a system that
tracks micro-dollars per call reports that 20,000 cheap tokens cost nothing.

So the unit here is the PICO-dollar, 1e-12 USD. That is not arbitrary: a price
of $X per million tokens is exactly `X * 1_000_000` picos per token, so every
published price this engine will ever meet — $0.05/M, $0.075/M, $3.00/M,
$0.0375/M — converts to an exact integer with no rounding at all. Python's ints
are arbitrary precision, so there is no overflow to worry about; a trillion
dollars is 1e24 picos and still just an int.

Rounding happens exactly once, at the boundary where a human or Stripe sees a
number, and it is stated explicitly there rather than accumulated silently.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

__all__ = ["PICOS_PER_USD", "Money", "TokenPrice"]

PICOS_PER_USD = 1_000_000_000_000  # 1e12
_PICOS_PER_CENT = PICOS_PER_USD // 100


class Money:
    """An exact USD amount, stored as an integer count of pico-dollars.

    Immutable, hashable, and orderable. Arithmetic is restricted on purpose:
    money plus money is money, money times a count is money, but money times
    money is meaningless and raises rather than silently producing a number
    someone will later put on an invoice.
    """

    __slots__ = ("_picos",)

    _picos: int

    def __init__(self, picos: int) -> None:
        if not isinstance(picos, int) or isinstance(picos, bool):
            raise TypeError(f"Money is built from an integer count of picos, got {type(picos)!r}")
        self._picos = picos

    # ── construction ──────────────────────────────────────────────────────
    @classmethod
    def zero(cls) -> Money:
        return cls(0)

    @classmethod
    def from_picos(cls, picos: int) -> Money:
        return cls(picos)

    @classmethod
    def from_usd(cls, amount: str | int | Decimal) -> Money:
        """Parse a dollar amount exactly.

        A `float` is refused rather than accepted-and-rounded. `Money.from_usd(0.1)`
        would have to decide what to do with 0.1000000000000000055511151231257827,
        and any answer it picks is a silent one. Pass a string.
        """
        if isinstance(amount, float):
            raise TypeError(
                'refusing to build Money from a float — pass a string, e.g. Money.from_usd("0.10")'
            )
        dec = Decimal(amount) * PICOS_PER_USD
        # Sub-pico input is the caller's rounding decision, so make it visible.
        if dec != dec.to_integral_value():
            raise ValueError(f"{amount!r} is finer than one pico-dollar")
        return cls(int(dec))

    @classmethod
    def from_cents(cls, cents: int) -> Money:
        """For Stripe, which speaks in integer cents."""
        return cls(cents * _PICOS_PER_CENT)

    # ── access ────────────────────────────────────────────────────────────
    @property
    def picos(self) -> int:
        return self._picos

    def as_usd(self) -> Decimal:
        """The exact value as a Decimal. No rounding."""
        return Decimal(self._picos) / PICOS_PER_USD

    def to_cents(self) -> int:
        """Round to whole cents, half-up, for a payment processor.

        The only rounding in this module, and it is a method call — so a
        rounded number can never appear by accident in an accumulation.
        """
        return int((self.as_usd() * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    # ── arithmetic ────────────────────────────────────────────────────────
    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self._picos + other._picos)

    def __sub__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self._picos - other._picos)

    def __mul__(self, count: int) -> Money:
        """Money times a whole count of things. Fractional multipliers are refused."""
        if isinstance(count, bool) or not isinstance(count, int):
            return NotImplemented
        return Money(self._picos * count)

    __rmul__ = __mul__

    def __neg__(self) -> Money:
        return Money(-self._picos)

    def __abs__(self) -> Money:
        return Money(abs(self._picos))

    # ── comparison ────────────────────────────────────────────────────────
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Money) and other._picos == self._picos

    def __lt__(self, other: Money) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._picos < other._picos

    def __le__(self, other: Money) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._picos <= other._picos

    def __gt__(self, other: Money) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._picos > other._picos

    def __ge__(self, other: Money) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._picos >= other._picos

    def __hash__(self) -> int:
        return hash(("Money", self._picos))

    def __bool__(self) -> bool:
        return self._picos != 0

    # ── display ───────────────────────────────────────────────────────────
    def __str__(self) -> str:
        """Six decimal places — enough to show a single cheap request as non-zero."""
        return f"${self.as_usd():.6f}"

    def __repr__(self) -> str:
        return f"Money.from_usd('{self.as_usd()}')"

    def format_adaptive(self) -> str:
        """A width that suits the magnitude, for dashboards and CLI output.

        A per-request cost and a monthly bill do not want the same precision:
        `$0.000041` is the useful rendering of one, `$1,284.30` of the other.
        """
        usd = self.as_usd()
        mag = abs(usd)
        if mag == 0:
            return "$0.00"
        if mag < Decimal("0.01"):
            return f"${usd:.6f}"
        if mag < Decimal("1"):
            return f"${usd:.4f}"
        return f"${usd:,.2f}"


class TokenPrice:
    """A model's price sheet, held as exact picos per token.

    Constructed from the numbers a provider actually publishes (dollars per
    million tokens), because a price copied from a pricing page and then
    converted by hand is a price that is eventually wrong.

    `cached_input_usd_per_mtok` exists because prompt caching changes the
    economics of P1 and P2 more than model choice does — a cached system prompt
    can be an order of magnitude cheaper than a fresh one, and a router that
    cannot represent that will route as if caching did not exist.
    """

    __slots__ = ("cached_input_picos", "input_picos", "output_picos")

    def __init__(
        self,
        input_usd_per_mtok: str | int | Decimal,
        output_usd_per_mtok: str | int | Decimal,
        cached_input_usd_per_mtok: str | int | Decimal | None = None,
    ) -> None:
        self.input_picos = self._per_token(input_usd_per_mtok)
        self.output_picos = self._per_token(output_usd_per_mtok)
        self.cached_input_picos = (
            self.input_picos
            if cached_input_usd_per_mtok is None
            else self._per_token(cached_input_usd_per_mtok)
        )

    @staticmethod
    def _per_token(usd_per_mtok: str | int | Decimal) -> int:
        if isinstance(usd_per_mtok, float):
            raise TypeError("refusing a float price — pass a string, e.g. '0.15'")
        # $X per 1e6 tokens == X * 1e12 picos per 1e6 tokens == X * 1e6 picos per token.
        picos = Decimal(usd_per_mtok) * (PICOS_PER_USD // 1_000_000)
        if picos != picos.to_integral_value():
            raise ValueError(f"price {usd_per_mtok!r} is finer than one pico per token")
        return int(picos)

    def cost(
        self,
        input_tokens: int,
        output_tokens: int,
        cached_input_tokens: int = 0,
    ) -> Money:
        """Exact cost of one call.

        `cached_input_tokens` is a SUBSET of `input_tokens` — that is how every
        provider reports it — so it is subtracted from the full-price count
        rather than added on top. Getting this backwards inflates the reported
        cost of exactly the requests a cache was supposed to make cheap.
        """
        if cached_input_tokens > input_tokens:
            raise ValueError(
                f"cached_input_tokens ({cached_input_tokens}) exceeds "
                f"input_tokens ({input_tokens}); cached tokens are a subset"
            )
        fresh = input_tokens - cached_input_tokens
        return Money(
            fresh * self.input_picos
            + cached_input_tokens * self.cached_input_picos
            + output_tokens * self.output_picos
        )

    def __repr__(self) -> str:
        return (
            f"TokenPrice(in={Money(self.input_picos * 1_000_000)}/Mtok, "
            f"out={Money(self.output_picos * 1_000_000)}/Mtok)"
        )
