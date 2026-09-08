"""Tests for P14 and P9."""

from __future__ import annotations

from random import Random

import pytest

from omnex.core import ValidationFailed
from omnex.finetune import (
    Example,
    ForgettingCheck,
    LoraConfig,
    PreferencePair,
    check_preferences,
    prepare,
)
from omnex.serving import PrefixAwareBalancer, QuantizationProfile, Request, plan_capacity, simulate

# ── P14: batching ─────────────────────────────────────────────────────────


def _long_tail_traffic(n: int = 200) -> list[Request]:
    """Real traffic: mostly short answers, a few very long ones."""
    rng = Random(7)
    requests = []
    for i in range(n):
        long_one = i % 20 == 0
        requests.append(
            Request(
                id=f"r{i}",
                arrives_at=i * 0.05,
                prompt_tokens=rng.randint(400, 800),
                output_tokens=rng.randint(400, 600) if long_one else rng.randint(20, 60),
                shared_prefix_tokens=400,
            )
        )
    return requests


def test_continuous_batching_beats_static_on_a_long_tail():
    """Static returns when the LONGEST in the batch finishes; the rest wait, done."""
    traffic = _long_tail_traffic()
    static = simulate(traffic, policy="static", max_batch=8)
    continuous = simulate(traffic, policy="continuous", max_batch=8)

    assert continuous.completed == static.completed == len(traffic)
    assert continuous.p95_latency < static.p95_latency
    assert continuous.throughput > static.throughput


def test_continuous_wins_on_uniform_traffic_too_and_the_reason_is_not_the_tail():
    """A result that contradicted the obvious hypothesis, kept because it is true.

    The intuition is that continuous batching wins most where output lengths
    vary most, since that is where "wait for the longest" hurts. Measured on
    this model the uniform case shows the LARGER ratio (~33x vs ~22x), and the
    reason is the other half of static batching that gets less attention: a
    static batch is charged the SUMMED prefill of all eight requests before any
    decoding starts, so at 20 req/s it falls behind arrivals and queues without
    bound. The long tail hurts both policies, which compresses the ratio.

    The practical reading: waiting for the longest sequence is the famous
    problem, and batched prefill is the one that actually caps your throughput.
    """
    uniform = [
        Request(id=f"u{i}", arrives_at=i * 0.05, prompt_tokens=500, output_tokens=100)
        for i in range(200)
    ]
    uniform_gap = (
        simulate(uniform, "static").p95_latency / simulate(uniform, "continuous").p95_latency
    )
    tail = _long_tail_traffic()
    tail_gap = simulate(tail, "static").p95_latency / simulate(tail, "continuous").p95_latency

    assert uniform_gap > 5.0
    assert tail_gap > 5.0


def test_time_to_first_token_is_reported_separately_from_total_latency():
    """What a streaming UI actually shows the user."""
    result = simulate(_long_tail_traffic(), "continuous")
    assert result.p95_ttft > 0
    assert result.p95_ttft < result.p95_latency
    assert "TTFT" in result.report()


# ── P14: prefix-aware routing ─────────────────────────────────────────────


def test_requests_sharing_a_prefix_land_on_the_same_replica():
    balancer = PrefixAwareBalancer(replicas=4)
    shared = [
        Request(
            id=f"r{i}", arrives_at=0, prompt_tokens=500, output_tokens=50, shared_prefix_tokens=2000
        )
        for i in range(3)
    ]
    routed = [balancer.route(r) for r in shared]
    assert len(set(routed)) == 1
    assert balancer.hit_rate > 0


def test_affinity_gives_way_before_one_replica_carries_the_whole_fleet():
    """Pure affinity is how one replica serves the popular document while three idle."""
    balancer = PrefixAwareBalancer(replicas=4, max_load_factor=1.5)
    popular = [
        Request(
            id=f"p{i}", arrives_at=0, prompt_tokens=500, output_tokens=50, shared_prefix_tokens=2000
        )
        for i in range(40)
    ]
    for request in popular:
        balancer.route(request)

    assert balancer.overflows > 0
    assert balancer.imbalance < 2.5, "one replica should not have taken everything"
    assert min(balancer.load) > 0, "no replica should be idle"


def test_distinct_prefixes_spread_across_replicas():
    balancer = PrefixAwareBalancer(replicas=4)
    for i in range(40):
        balancer.route(
            Request(
                id=f"d{i}",
                arrives_at=0,
                prompt_tokens=500,
                output_tokens=50,
                shared_prefix_tokens=i,
            )
        )
    assert min(balancer.load) > 0
    assert balancer.imbalance < 1.6


# ── P14: capacity and quantisation ────────────────────────────────────────


def test_capacity_comes_from_littles_law_with_headroom():
    plan = plan_capacity(requests_per_second=20, mean_seconds_per_request=2.0, slots_per_replica=8)
    assert plan.concurrency_needed == 40.0
    # 40 concurrent at 70% of 8 slots = 5.6 -> 8 replicas, not 5.
    assert plan.replicas >= 8
    assert plan.utilisation < 0.75
    assert "replicas" in plan.report()


def test_a_single_replica_is_the_floor():
    assert plan_capacity(0.1, 0.5).replicas == 1


def test_quantisation_is_only_acceptable_if_quality_was_measured():
    """2x cheaper and quietly worse: the bill improves, the complaints do not."""
    good = QuantizationProfile(
        "int8", 8, memory_ratio=0.5, measured_pass_rate=0.89, throughput_ratio=1.6
    )
    lossy = QuantizationProfile("int4", 4, memory_ratio=0.25, measured_pass_rate=0.78)

    assert good.acceptable(baseline_pass_rate=0.90)
    assert not lossy.acceptable(baseline_pass_rate=0.90)
    assert "TOO LOSSY" in lossy.report(0.90)


# ── P9: dataset preparation ───────────────────────────────────────────────


def test_preparation_refuses_to_run_without_an_eval_set_to_decontaminate_against():
    """Made optional, it gets omitted, and the model is evaluated on what it memorised."""
    with pytest.raises(ValidationFailed, match="decontaminate"):
        prepare([Example("q", "a long enough response here")], eval_questions=[])


def test_contaminated_examples_are_removed():
    eval_questions = ["What is the request timeout for the billing service?"]
    examples = [
        Example(
            "What is the request timeout for the billing service?",
            "The billing service request timeout is five seconds by default.",
        ),
        Example(
            "Summarise the deployment runbook for new engineers.",
            "Drain the queue first, then restart the service and watch the error rate.",
        ),
    ]
    report = prepare(examples, eval_questions)
    assert report.contaminated == 1
    assert len(report.kept) == 1


def test_duplicates_are_removed_because_they_act_as_a_higher_learning_rate():
    example = Example("Explain the retry policy", "Requests retry three times with backoff.")
    report = prepare(
        [example] * 5
        + [
            Example(
                "Other question here", "A different answer entirely, with enough words to keep."
            )
        ],
        eval_questions=["unrelated eval question"],
    )
    assert report.exact_duplicates == 4
    assert len(report.kept) == 2


def test_near_duplicates_are_caught_too():
    report = prepare(
        [
            Example(
                "Explain the retry policy", "Requests retry three times with exponential backoff."
            ),
            Example(
                "Explain the retry policy.", "Requests retry three times with exponential backoff!"
            ),
        ],
        eval_questions=["unrelated"],
    )
    assert report.exact_duplicates + report.near_duplicates == 1
    assert "removed" in report.report()


def test_stub_responses_are_dropped():
    report = prepare(
        [
            Example("Explain the retry policy", "Yes."),
            Example("Explain it properly", "It retries three times with backoff."),
        ],
        eval_questions=["unrelated"],
    )
    assert report.too_short == 1


# ── P9: preference pairs ──────────────────────────────────────────────────


def test_an_inverted_pair_teaches_the_opposite_of_what_was_intended():
    issues = check_preferences(
        [PreferencePair("q", "worse answer", "better answer", chosen_score=0.3, rejected_score=0.9)]
    )
    assert [i.kind for i in issues] == ["inverted"]


def test_a_pair_that_teaches_nothing_is_flagged():
    issues = check_preferences(
        [
            PreferencePair("q", "the same text", "the same text"),
            PreferencePair(
                "q",
                "The service retries three times with exponential backoff and jitter applied.",
                "The service retries three times with exponential backoff and jitter applied!",
            ),
        ]
    )
    kinds = {i.kind for i in issues}
    assert "identical" in kinds
    assert "near_identical" in kinds


def test_a_weak_preference_is_reported_without_being_fatal():
    issues = check_preferences(
        [PreferencePair("q", "a", "b", chosen_score=0.55, rejected_score=0.50)]
    )
    assert [i.kind for i in issues] == ["weak_preference"]


def test_a_clean_pair_produces_no_issues():
    assert (
        check_preferences(
            [
                PreferencePair(
                    "q",
                    "The connection pool holds twenty connections and is configured per service.",
                    "I am not sure about that.",
                    chosen_score=0.9,
                    rejected_score=0.2,
                )
            ]
        )
        == []
    )


# ── P9: catastrophic forgetting ───────────────────────────────────────────


def test_a_gain_on_the_target_cannot_hide_a_collapse_elsewhere():
    """The regression a customer finds, in the capability nobody was watching."""
    check = ForgettingCheck()
    deltas = check.compare(
        before={"support_tone": 0.60, "instruction_following": 0.90, "reasoning": 0.85},
        after={"support_tone": 0.85, "instruction_following": 0.55, "reasoning": 0.84},
    )
    accept, reason = check.verdict(deltas, target="support_tone")
    assert not accept
    assert "forgot instruction_following" in reason
    assert "←" in check.report(deltas, target="support_tone")


def test_a_fine_tune_that_gains_without_forgetting_is_accepted():
    check = ForgettingCheck()
    deltas = check.compare(
        before={"support_tone": 0.60, "instruction_following": 0.90},
        after={"support_tone": 0.82, "instruction_following": 0.89},
    )
    accept, reason = check.verdict(deltas, target="support_tone")
    assert accept and "+0.22" in reason


def test_a_fine_tune_with_no_gain_on_its_own_target_is_rejected():
    check = ForgettingCheck()
    deltas = check.compare(
        before={"support_tone": 0.80, "instruction_following": 0.90},
        after={"support_tone": 0.79, "instruction_following": 0.90},
    )
    accept, reason = check.verdict(deltas, target="support_tone")
    assert not accept and "no gain" in reason


def test_an_unmeasured_target_is_a_rejection_not_a_pass():
    check = ForgettingCheck()
    deltas = check.compare(before={"reasoning": 0.8}, after={"reasoning": 0.85})
    accept, reason = check.verdict(deltas, target="support_tone")
    assert not accept and "was not measured" in reason


# ── P9: LoRA configuration ────────────────────────────────────────────────


def test_the_effective_scaling_is_alpha_over_r():
    """Doubling r while holding alpha HALVES the update — the opposite of intuition."""
    assert LoraConfig(r=16, alpha=32).scaling == 2.0
    assert LoraConfig(r=32, alpha=32).scaling == 1.0


def test_the_default_targets_include_the_mlp_layers():
    """Attention-only is the common default and is why a style fine-tune 'does nothing'."""
    targets = LoraConfig().target_modules
    assert "down_proj" in targets and "gate_proj" in targets


def test_an_excessive_epoch_count_has_to_be_chosen_deliberately():
    with pytest.raises(ValidationFailed, match="memorises"):
        LoraConfig(epochs=20)
