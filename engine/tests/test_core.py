"""Tests for the primitives. These assert the properties the rest of the engine assumes."""

from __future__ import annotations

from decimal import Decimal
from random import Random

import pytest

from omnex.core import (
    ConfigurationError,
    Deadline,
    FakeClock,
    IdFactory,
    Money,
    PermanentError,
    RateLimited,
    RetryPolicy,
    Settings,
    TokenPrice,
    TransientError,
    clean_env,
    parse_prefix,
    retry_call,
)
from omnex.core.errors import ProviderError
from omnex.core.retry import Attempt, retry_call_async

# ── Money ─────────────────────────────────────────────────────────────────


def test_money_addition_is_exact_where_float_is_not():
    """The whole reason this type exists. 0.1 + 0.2 == 0.3, exactly."""
    total = Money.from_usd("0.1") + Money.from_usd("0.2")
    assert total == Money.from_usd("0.3")
    assert total.as_usd() == Decimal("0.3")
    # The float version of the same sum does not hold.
    assert 0.1 + 0.2 != 0.3


def test_money_does_not_drift_over_a_million_additions():
    """A per-request spend counter runs for a long time. It must not accumulate error."""
    one_request = Money.from_usd("0.000041")
    total = Money.zero()
    for _ in range(1_000_000):
        total = total + one_request
    assert total == Money.from_usd("41")


def test_money_refuses_floats():
    with pytest.raises(TypeError, match="float"):
        Money.from_usd(0.1)  # type: ignore[arg-type]


def test_money_refuses_sub_pico_precision_rather_than_rounding_silently():
    with pytest.raises(ValueError, match="finer than one pico"):
        Money.from_usd("0.0000000000001")


def test_money_times_money_is_refused():
    with pytest.raises(TypeError):
        _ = Money.from_usd("1") * Money.from_usd("2")  # type: ignore[operator]


def test_stripe_cents_round_half_up_and_only_on_request():
    assert Money.from_usd("1.005").to_cents() == 101
    assert Money.from_usd("1.004").to_cents() == 100
    assert Money.from_cents(2999).as_usd() == Decimal("29.99")


def test_adaptive_formatting_suits_the_magnitude():
    assert Money.from_usd("0.000041").format_adaptive() == "$0.000041"
    assert Money.from_usd("0.4210").format_adaptive() == "$0.4210"
    assert Money.from_usd("1284.3").format_adaptive() == "$1,284.30"
    assert Money.zero().format_adaptive() == "$0.00"


# ── TokenPrice ────────────────────────────────────────────────────────────


def test_cheap_model_token_cost_is_not_rounded_to_zero():
    """Micro-dollar accounting reports 20k cheap tokens as free. Pico-dollars do not."""
    cheap = TokenPrice("0.05", "0.10")
    cost = cheap.cost(input_tokens=20_000, output_tokens=0)
    assert cost == Money.from_usd("0.001")
    assert cost > Money.zero()
    # And one single token is still a non-zero amount.
    assert cheap.cost(1, 0) > Money.zero()


def test_published_prices_convert_without_rounding():
    for quoted in ("0.05", "0.075", "0.15", "0.0375", "3.00", "15"):
        TokenPrice(quoted, quoted)  # must not raise


def test_cached_tokens_are_a_subset_not_an_addition():
    """Treating cached tokens as extra inflates the cost of exactly the cheap requests."""
    price = TokenPrice("3.00", "15.00", cached_input_usd_per_mtok="0.30")
    full = price.cost(input_tokens=1000, output_tokens=0)
    mostly_cached = price.cost(input_tokens=1000, output_tokens=0, cached_input_tokens=900)
    assert full == Money.from_usd("0.003")
    # 100 fresh @ $3/M + 900 cached @ $0.30/M
    assert mostly_cached == Money.from_usd("0.00057")
    assert mostly_cached < full


def test_cached_tokens_exceeding_input_is_a_bug_not_a_clamp():
    price = TokenPrice("3.00", "15.00")
    with pytest.raises(ValueError, match="subset"):
        price.cost(input_tokens=10, output_tokens=0, cached_input_tokens=11)


# ── Clock and Deadline ────────────────────────────────────────────────────


def test_fake_clock_records_sleeps_without_taking_real_time():
    clock = FakeClock()
    clock.sleep(32.0)
    clock.sleep(0.5)
    assert clock.slept == [32.0, 0.5]
    assert clock.monotonic() == 32.5


def test_deadline_never_reports_negative_remaining():
    clock = FakeClock()
    deadline = Deadline.after(10.0, clock)
    clock.advance(25.0)
    assert deadline.expired()
    assert deadline.remaining() == 0.0


def test_shrink_to_can_only_tighten_a_deadline():
    """A sub-call must not be able to extend its caller's budget."""
    clock = FakeClock()
    outer = Deadline.after(10.0, clock)
    assert outer.shrink_to(2.0).remaining() == 2.0
    assert outer.shrink_to(60.0).remaining() == 10.0


# ── Ids ───────────────────────────────────────────────────────────────────


def test_ids_sort_chronologically_as_plain_strings():
    clock = FakeClock()
    factory = IdFactory(clock=clock, rng=Random(7))
    ids = []
    for _ in range(50):
        ids.append(factory.new("run"))
        clock.advance(0.002)
    assert ids == sorted(ids)


def test_ids_minted_in_the_same_millisecond_still_sort_strictly():
    """A trace and its first span are microseconds apart; the span list must not shuffle."""
    factory = IdFactory(clock=FakeClock(), rng=Random(7))
    ids = [factory.new("span") for _ in range(1000)]
    assert ids == sorted(ids)
    assert len(set(ids)) == 1000


def test_id_prefix_identifies_the_kind_of_thing():
    factory = IdFactory(clock=FakeClock(), rng=Random(1))
    assert parse_prefix(factory.new("tnt")) == "tnt"
    assert parse_prefix(factory.new("run")) == "run"
    with pytest.raises(ValueError):
        parse_prefix("not-an-id")


def test_id_alphabet_excludes_transcription_traps():
    factory = IdFactory(clock=FakeClock(), rng=Random(3))
    body = factory.new("run").split("_", 1)[1]
    assert not (set(body) & set("ILOU"))


def test_mint_time_is_recoverable_from_the_id():
    clock = FakeClock()
    factory = IdFactory(clock=clock, rng=Random(5))
    ident = factory.new("run")
    expected_ms = int(clock.now().timestamp() * 1000)
    assert factory.timestamp_ms_of(ident) == expected_ms


# ── Retry ─────────────────────────────────────────────────────────────────


def test_permanent_errors_are_not_retried():
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        raise PermanentError("malformed prompt")

    with pytest.raises(PermanentError):
        retry_call(fn, RetryPolicy(max_attempts=5), clock=FakeClock(), rng=Random(1))
    assert calls["n"] == 1


def test_plain_python_exceptions_are_treated_as_bugs_not_transients():
    """Retrying a KeyError four times turns one stack trace into four."""
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        raise KeyError("choices")

    with pytest.raises(KeyError):
        retry_call(fn, RetryPolicy(max_attempts=5), clock=FakeClock(), rng=Random(1))
    assert calls["n"] == 1


def test_transient_errors_retry_then_succeed():
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        if calls["n"] < 3:
            raise TransientError("upstream blip")
        return "ok"

    clock = FakeClock()
    assert retry_call(fn, RetryPolicy(max_attempts=5), clock=clock, rng=Random(1)) == "ok"
    assert calls["n"] == 3
    assert len(clock.slept) == 2


def test_backoff_ceiling_doubles_and_is_capped():
    policy = RetryPolicy(base_delay=0.5, multiplier=2.0, max_delay=4.0)
    assert [policy.ceiling_for(i) for i in range(1, 6)] == [0.5, 1.0, 2.0, 4.0, 4.0]


def test_jitter_spreads_retries_across_the_window():
    """Fixed backoff synchronises clients into a second wave. Jitter is the fix."""
    policy = RetryPolicy(base_delay=1.0)
    rng = Random(11)
    delays = [policy.delay_for(3, rng) for _ in range(200)]
    assert all(0.0 <= d <= 4.0 for d in delays)
    assert len(set(delays)) > 190  # essentially all distinct
    assert 1.0 < sum(delays) / len(delays) < 3.0  # centred in the window


def test_retry_after_header_overrides_computed_delay():
    clock = FakeClock()
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        if calls["n"] == 1:
            raise RateLimited("slow down", retry_after=7.0)
        return "ok"

    retry_call(fn, RetryPolicy(base_delay=0.1), clock=clock, rng=Random(1))
    assert clock.slept == [7.0]


def test_retry_after_is_capped_so_one_header_cannot_pin_a_worker():
    policy = RetryPolicy(max_delay=30.0)
    assert policy.delay_for(1, Random(1), RateLimited("x", retry_after=3600.0)) == 30.0


def test_deadline_stops_the_loop_before_sleeping_through_it():
    """The failure raised must be the real cause, not a timeout on the far side of a sleep."""
    clock = FakeClock()
    deadline = Deadline.after(1.0, clock)
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        raise TransientError("upstream down")

    with pytest.raises(TransientError, match="upstream down"):
        retry_call(
            fn,
            RetryPolicy(max_attempts=6, base_delay=10.0, max_delay=60.0),
            clock=clock,
            rng=Random(1),
            deadline=deadline,
        )
    assert clock.total_slept == 0.0  # never slept past the deadline
    assert calls["n"] < 6  # gave up early rather than burning all attempts


def test_attempts_are_observable_for_tracing():
    seen: list[Attempt] = []
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        if calls["n"] < 2:
            raise TransientError("blip")
        return "ok"

    retry_call(fn, RetryPolicy(), clock=FakeClock(), rng=Random(1), on_attempt=seen.append)
    assert [a.number for a in seen] == [1, 2]
    assert seen[0].will_retry is True and seen[0].delay > 0
    assert seen[1].will_retry is False and seen[1].error is None


async def test_async_retry_records_waits_through_the_injected_sleep():
    clock = FakeClock()
    calls = {"n": 0}

    async def fn():
        calls["n"] += 1
        if calls["n"] < 3:
            raise TransientError("blip")
        return "ok"

    async def fake_sleep(seconds: float) -> None:
        clock.sleep(seconds)

    result = await retry_call_async(fn, RetryPolicy(), clock=clock, rng=Random(2), sleep=fake_sleep)
    assert result == "ok"
    assert len(clock.slept) == 2


# ── Error classification ──────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("status", "retryable"),
    [
        (429, True),
        (500, True),
        (503, True),
        (504, True),
        (408, True),
        (400, False),
        (401, False),
        (403, False),
        (404, False),
        (422, False),
    ],
)
def test_http_status_classification(status: int, retryable: bool):
    """A 4xx from a provider is a permanent failure wearing a network error's clothes."""
    err = ProviderError.from_status(status, provider="groq")
    assert err.retryable is retryable


def test_errors_carry_structured_context_not_a_baked_sentence():
    err = ProviderError("call failed", provider="groq", model="llama-3.3-70b")
    assert err.as_dict()["provider"] == "groq"
    assert err.as_dict()["code"] == "provider_error"
    assert "provider='groq'" in str(err)


# ── Settings ──────────────────────────────────────────────────────────────


def test_clean_env_strips_the_characters_that_break_a_correct_looking_key():
    assert clean_env("﻿sk_live_abc\n") == "sk_live_abc"
    assert clean_env('"sk_live_abc"') == "sk_live_abc"
    assert clean_env("  sk_live_abc\t") == "sk_live_abc"
    assert clean_env(None) == ""


def test_missing_required_env_vars_are_all_named_at_once(monkeypatch):
    monkeypatch.delenv("OMNEX_A", raising=False)
    monkeypatch.delenv("OMNEX_B", raising=False)
    with pytest.raises(ConfigurationError) as exc:
        Settings().require("OMNEX_A", "OMNEX_B")
    assert "OMNEX_A, OMNEX_B" in str(exc.value)


def test_settings_dict_is_safe_to_log():
    dumped = Settings().as_dict()
    assert all("key" not in k and "secret" not in k for k in dumped)
