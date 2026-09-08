"""The harness, tested on the properties that are supposed to be structural.

Most of this package is a set of refusals, and a refusal is worth exactly as
much as the test that proves it still happens. The dangerous failure mode here
is not a crash — it is a gate that quietly starts saying yes: an evaluator that
grows a parameter for the maker's transcript, a frozen criterion that a later
revision is allowed to soften, an outer loop that reaches down and relaxes the
definition of done. Each of those is a one-line change, none of them breaks
anything visibly, and every one of them turns the harness into a loop that
agrees with itself expensively.

So several tests below assert on the *shape* of the API — that a parameter does
not exist, that a constructor is narrow — rather than on behaviour. That is
deliberate. Those are the properties the design is made of, and behaviour tests
cannot see them.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from omnex.core.clock import FakeClock
from omnex.core.errors import ValidationFailed
from omnex.core.money import Money
from omnex.harness import (
    Attempt,
    CheckResult,
    Condition,
    Contract,
    Criterion,
    DisagreementPolicy,
    Evaluator,
    Fleet,
    Grade,
    Health,
    Intervention,
    MergePolicy,
    Node,
    Plan,
    Proposal,
    Rubric,
    RunState,
    Verdict,
    Workspace,
    diagnose,
    evaluate,
    mean_cost_per_accepted,
)
from omnex.harness.meta import mean_cost_per_accepted as _mean_alias

ALL_HOLD = {
    "repeats_weekly": True,
    "verification_is_automated": True,
    "budget_absorbs_waste": True,
    "agent_has_tools": True,
    "has_goal_metric": True,
    "has_change_method": True,
    "has_standard_assessment": True,
}


def _criterion(key: str, *, frozen: bool = False, check: str = "pytest -q") -> Criterion:
    return Criterion(key=key, statement=f"{key} holds", check=check, frozen=frozen)


def _agreed(*criteria: Criterion) -> tuple[Contract, str]:
    contract = Contract(criteria=criteria).agree()
    return contract, contract.fingerprint


# ── worth_it: the gate before the spend ───────────────────────────────────────


def test_all_seven_conditions_holding_is_worth_it() -> None:
    verdict = evaluate(**ALL_HOLD)
    assert verdict.worth_it
    assert verdict.failed == ()


def test_refusal_names_every_failing_condition_at_once() -> None:
    """Not the first failure — all of them.

    Being refused, fixing one condition, and being refused again is how somebody
    concludes the check itself is the obstacle and routes around it.
    """
    verdict = evaluate(**{**ALL_HOLD, "repeats_weekly": False, "has_goal_metric": False})

    assert not verdict.worth_it
    assert set(verdict.failed) == {Condition.REPEATS, Condition.GOAL}

    with pytest.raises(ValidationFailed) as caught:
        verdict.raise_if_not_worth_it()

    message = str(caught.value)
    assert "repeats" in message and "goal" in message
    # Each failure carries its reason, not just its name.
    assert "pay back" in message
    assert "unfalsifiable" in message


def test_economic_but_wrong_shape_still_refuses() -> None:
    """The two source checklists are independent, so either alone can refuse."""
    economic_only = evaluate(
        **{
            **ALL_HOLD,
            "has_goal_metric": False,
            "has_change_method": False,
            "has_standard_assessment": False,
        }
    )
    shaped_only = evaluate(
        **{
            **ALL_HOLD,
            "repeats_weekly": False,
            "verification_is_automated": False,
            "budget_absorbs_waste": False,
            "agent_has_tools": False,
        }
    )
    assert not economic_only.worth_it
    assert not shaped_only.worth_it


def test_no_condition_defaults_to_true() -> None:
    """A default here would be a silent assumption about somebody else's budget."""
    signature = inspect.signature(evaluate)
    assert all(p.kind is p.KEYWORD_ONLY for p in signature.parameters.values())
    assert all(p.default is inspect.Parameter.empty for p in signature.parameters.values())
    assert len(signature.parameters) == len(Condition)


# ── contract: the anti-Goodhart anchor ────────────────────────────────────────


def test_a_criterion_without_a_check_is_refused() -> None:
    with pytest.raises(ValidationFailed, match="not a verification"):
        Criterion(key="quality", statement="it is good", check="   ")


def test_a_frozen_criterion_cannot_be_weakened() -> None:
    anchor = _criterion("no_fabrication", frozen=True, check="citegate --strict")
    contract = Contract(criteria=(anchor, _criterion("fast")))

    weakened = Proposal(
        criteria=(
            Criterion(
                key="no_fabrication",
                statement=anchor.statement,
                check="the agent reports no fabrication",
                frozen=True,
            ),
            _criterion("fast"),
        ),
        note="simplify the check",
    )
    with pytest.raises(ValidationFailed, match="changes the check"):
        contract.negotiate(weakened)


def test_a_frozen_criterion_cannot_be_dropped_or_thawed() -> None:
    anchor = _criterion("no_fabrication", frozen=True)
    contract = Contract(criteria=(anchor,))

    with pytest.raises(ValidationFailed, match="drops frozen criterion"):
        contract.negotiate(Proposal(criteria=()))

    thawed = Criterion(key=anchor.key, statement=anchor.statement, check=anchor.check, frozen=False)
    with pytest.raises(ValidationFailed, match="unfreezes"):
        contract.negotiate(Proposal(criteria=(thawed,)))


def test_a_frozen_criterion_may_be_added_to() -> None:
    """Added to, never weakened — the negotiation must stay useful."""
    contract = Contract(criteria=(_criterion("anchor", frozen=True),))
    revised = contract.negotiate(
        Proposal(criteria=(_criterion("anchor", frozen=True), _criterion("extra")), note="stricter")
    )
    assert {c.key for c in revised.criteria} == {"anchor", "extra"}
    assert not revised.agreed, "a revision reopens the negotiation"
    assert revised.history == ("stricter",)


def test_a_contract_altered_after_agreement_fails_its_fingerprint() -> None:
    contract, agreed = _agreed(_criterion("a"), _criterion("b"))

    altered = Contract(criteria=(_criterion("a"), _criterion("b", check="true")), agreed=True)
    assert altered.fingerprint != agreed

    contract.assert_unchanged(agreed)  # unchanged: no raise
    with pytest.raises(ValidationFailed, match="changed after it was agreed"):
        altered.assert_unchanged(agreed)


def test_fingerprint_ignores_criterion_order_but_not_content() -> None:
    """Order is presentation; the check is the contract."""
    a, b = _criterion("a"), _criterion("b")
    assert Contract(criteria=(a, b)).fingerprint == Contract(criteria=(b, a)).fingerprint
    assert (
        Contract(criteria=(a, b)).fingerprint
        != Contract(criteria=(a, _criterion("b", check="ruff"))).fingerprint
    )


def test_agreement_enforces_a_floor_on_granularity() -> None:
    with pytest.raises(ValidationFailed, match="below the agreed floor"):
        Contract(criteria=(_criterion("a"), _criterion("b"))).agree(minimum_criteria=5)


# ── evaluator: clean context by construction ──────────────────────────────────


def test_the_evaluator_has_no_parameter_for_the_generator_context() -> None:
    """The one assertion that keeps the separation from becoming cosmetic.

    Splitting maker and critic buys nothing if the critic can be handed the
    maker's transcript — it inherits the reasoning it was supposed to check.
    This test fails the moment somebody adds the convenient parameter.
    """
    leaky = {"transcript", "history", "messages", "context", "generator", "agent", "conversation"}

    for function in (Evaluator.__init__, Evaluator.grade):
        names = set(inspect.signature(function).parameters)
        assert not (names & leaky), f"{function.__qualname__} accepts generator context"

    assert set(inspect.signature(Evaluator.grade).parameters) == {
        "self",
        "contract",
        "agreed_fingerprint",
        "results",
    }


def test_an_unrun_check_is_unverified_and_never_a_pass() -> None:
    contract, agreed = _agreed(_criterion("a"), _criterion("b"))
    grade = Evaluator().grade(
        contract,
        agreed,
        (CheckResult(key="a", passed=True), CheckResult(key="b", passed=None, detail="timed out")),
    )

    assert grade.unverified == ("b",)
    assert not grade.accepted
    assert grade.score == pytest.approx(0.5)
    assert "UNVERIFIED b" in grade.report()


def test_a_missing_result_is_unverified_rather_than_ignored() -> None:
    """Silence is not a pass; a criterion nobody ran still counts against."""
    contract, agreed = _agreed(_criterion("a"), _criterion("b"))
    grade = Evaluator().grade(contract, agreed, (CheckResult(key="a", passed=True),))
    assert grade.unverified == ("b",)
    assert not grade.accepted


def test_a_high_score_cannot_buy_past_a_frozen_criterion() -> None:
    contract, agreed = _agreed(
        _criterion("anchor", frozen=True),
        *(_criterion(f"minor{i}") for i in range(9)),
    )
    results = (
        CheckResult(key="anchor", passed=False),
        *(CheckResult(key=f"minor{i}", passed=True) for i in range(9)),
    )
    grade = Evaluator(rubric=Rubric(min_score=0.8)).grade(contract, agreed, results)

    assert grade.score == pytest.approx(0.9)
    assert not grade.accepted
    assert grade.failures == ("anchor",), "reported once, not twice"


def test_grading_requires_an_agreed_contract() -> None:
    contract = Contract(criteria=(_criterion("a"),))
    with pytest.raises(ValidationFailed, match="never agreed"):
        Evaluator().grade(contract, contract.fingerprint, (CheckResult(key="a", passed=True),))


def test_results_for_criteria_outside_the_contract_are_refused() -> None:
    contract, agreed = _agreed(_criterion("a"))
    with pytest.raises(ValidationFailed, match="not in the contract"):
        Evaluator().grade(
            contract, agreed, (CheckResult(key="a", passed=True), CheckResult(key="z", passed=True))
        )


def test_all_criteria_passing_is_accepted() -> None:
    contract, agreed = _agreed(_criterion("anchor", frozen=True), _criterion("b"))
    grade = Evaluator().grade(
        contract,
        agreed,
        (CheckResult(key="anchor", passed=True), CheckResult(key="b", passed=True)),
    )
    assert isinstance(grade, Grade)
    assert grade.accepted and grade.score == pytest.approx(1.0)
    assert Verdict.PASSED is CheckResult(key="x", passed=True).verdict


# ── edges: an edge exists only where data crosses ─────────────────────────────


def test_an_edge_with_no_data_crossing_is_refused() -> None:
    plan = Plan()
    plan.add(Node(key="summarise", reads=frozenset({"file"}), produces="summary"))
    plan.add(Node(key="weather", reads=frozenset({"city"}), produces="forecast"))

    with pytest.raises(ValidationFailed, match="no data crosses") as caught:
        plan.connect("summarise", "weather")

    # The message names what was produced and what was read, because the usual
    # cause is a real edge whose names simply do not match.
    assert "'summary'" in str(caught.value)
    assert "['city']" in str(caught.value)


def test_independent_work_fans_out_instead_of_queueing() -> None:
    plan = Plan()
    plan.add(Node(key="summarise", reads=frozenset({"file"}), produces="summary"))
    plan.add(Node(key="weather", reads=frozenset({"city"}), produces="forecast"))
    plan.add(Node(key="reply", reads=frozenset({"summary", "forecast"}), produces="reply"))
    plan.connect("summarise", "reply")
    plan.connect("weather", "reply")

    assert plan.waves() == [["summarise", "weather"], ["reply"]]
    assert plan.parallelisable() == [["summarise", "weather"]]
    assert "widest 2" in plan.advice()


def test_a_fully_sequential_graph_says_it_is_a_chain() -> None:
    """The honest half: most tasks are not graphs, and this one says so."""
    plan = Plan()
    plan.add(Node(key="fetch", produces="raw"))
    plan.add(Node(key="clean", reads=frozenset({"raw"}), produces="tidy"))
    plan.add(Node(key="report", reads=frozenset({"tidy"}), produces="doc"))
    plan.connect("fetch", "clean")
    plan.connect("clean", "report")

    assert plan.parallelisable() == []
    advice = plan.advice()
    assert "chain of 3 steps" in advice
    assert "no speed" in advice


def test_a_cycle_is_refused_and_leaves_the_plan_usable() -> None:
    plan = Plan()
    plan.add(Node(key="a", reads=frozenset({"y"}), produces="x"))
    plan.add(Node(key="b", reads=frozenset({"x"}), produces="y"))
    plan.connect("a", "b")

    with pytest.raises(ValidationFailed, match="closes a cycle"):
        plan.connect("b", "a")

    assert plan.waves() == [["a"], ["b"]], "the refused edge was not left behind"


def test_nodes_need_keys_and_cannot_depend_on_themselves() -> None:
    with pytest.raises(ValidationFailed, match="needs a key"):
        Node(key="  ")
    plan = Plan()
    plan.add(Node(key="a", reads=frozenset({"x"}), produces="x"))
    with pytest.raises(ValidationFailed, match="cannot depend on itself"):
        plan.connect("a", "a")
    with pytest.raises(ValidationFailed, match="duplicate node"):
        plan.add(Node(key="a"))


# ── isolation: two workers cannot share a writable tree ───────────────────────


def test_two_workers_cannot_share_a_writable_path() -> None:
    fleet = Fleet()
    fleet.assign("alice", "/work/alice")
    with pytest.raises(ValidationFailed, match="overlaps"):
        fleet.assign("bob", "/work/alice")


def test_nesting_counts_as_sharing() -> None:
    """`/w/a` and `/w/a/b` are one tree; the second worker finds out by losing work."""
    fleet = Fleet()
    fleet.assign("alice", "/work/alice")
    with pytest.raises(ValidationFailed, match="overlaps"):
        fleet.assign("bob", "/work/alice/nested")

    outer = Fleet()
    outer.assign("bob", "/work/alice/nested")
    with pytest.raises(ValidationFailed, match="overlaps"):
        outer.assign("alice", "/work/alice")


def test_disjoint_workspaces_are_allowed_and_the_policies_are_explicit() -> None:
    fleet = Fleet(merge=MergePolicy.DISJOINT_UNION, on_disagreement=DisagreementPolicy.MAJORITY)
    alice = fleet.assign("alice", "/work/alice", readonly=frozenset({"/repo"}))
    fleet.assign("bob", "/work/bob")

    assert isinstance(alice, Workspace)
    assert not alice.conflicts_with(fleet.workspaces["bob"])
    assert fleet.ready()
    assert "disjoint_union" in fleet.report() and "majority" in fleet.report()


def test_shared_version_control_commands_are_forbidden_structurally() -> None:
    """The port that failed did not fail on model quality; it failed on `git checkout`."""
    fleet = Fleet()
    fleet.assign("alice", "/work/alice")

    fleet.check_command("alice", "pytest -q")
    for command in ("git push origin main", "GIT CHECKOUT -b x", "  git reset --hard  "):
        with pytest.raises(ValidationFailed, match="may not run"):
            fleet.check_command("alice", command)


def test_a_worker_without_a_workspace_cannot_run_anything() -> None:
    with pytest.raises(ValidationFailed, match="no workspace"):
        Fleet().check_command("ghost", "pytest")
    fleet = Fleet()
    fleet.assign("alice", "/work/alice")
    with pytest.raises(ValidationFailed, match="already has a workspace"):
        fleet.assign("alice", "/work/other")


# ── state: the log that makes the next run cheaper ────────────────────────────


def test_a_repeated_change_is_recognised_before_it_is_paid_for() -> None:
    state = RunState(goal="g", clock=FakeClock())
    state.record("a", "  Widen The Regex ", accepted=False, reason="broke unicode", cost_picos=500)

    prior = state.already_tried("a", "widen the regex")
    assert prior is not None and prior.reason == "broke unicode"
    assert state.already_tried("a", "something else") is None
    assert state.already_tried("b", "widen the regex") is None


def test_ruled_out_hands_the_next_pass_the_space_it_need_not_search() -> None:
    state = RunState(goal="g", clock=FakeClock())
    state.record("a", "regex", accepted=False)
    state.record("a", "parser", accepted=False)
    state.record("a", "tokeniser", accepted=True)
    state.record("b", "other", accepted=False)

    assert state.ruled_out("a") == ("regex", "parser")
    assert [x.change for x in state.accepted_for("a")] == ["tokeniser"]


def test_a_repeatedly_failing_criterion_reports_restart_rather_than_patch() -> None:
    state = RunState(goal="g", clock=FakeClock())
    for i in range(2):
        state.record("a", f"patch{i}", accepted=False)
    assert not state.stuck_on("a"), "two failures is a bad day, not a dead end"

    state.record("a", "patch2", accepted=False)
    assert state.stuck_on("a")

    # An acceptance since the failures means the approach is not dead.
    state.record("a", "patch3", accepted=True)
    assert not state.stuck_on("a")


def test_json_state_survives_a_fresh_context(tmp_path: Path) -> None:
    """The point of the file: a compacted context loses specifics, disk does not."""
    clock = FakeClock()
    state = RunState(goal="ship P8", contract_fingerprint="abc123", clock=clock)
    state.record("cost", "meter on settle", accepted=True, cost_picos=1200)
    state.record("cost", "estimate by length", accepted=False, reason="not a measurement")

    path = state.save(tmp_path / "runs" / "state.json")
    reloaded = RunState.load(path, clock=clock)

    assert reloaded.goal == "ship P8"
    assert reloaded.contract_fingerprint == "abc123"
    assert reloaded.attempts == state.attempts
    assert reloaded.ruled_out("cost") == ("estimate by length",)
    assert "2 attempts, 1 accepted" in reloaded.report()


def test_saving_is_atomic_and_leaves_no_partial_file(tmp_path: Path) -> None:
    """A half-written log is worse than none: the next run starts from zero."""
    state = RunState(goal="g", clock=FakeClock())
    state.record("a", "x", accepted=True)
    path = state.save(tmp_path / "state.json")

    assert json.loads(path.read_text())["goal"] == "g"
    assert list(tmp_path.iterdir()) == [path], "no .tmp left behind"


def test_a_malformed_attempt_entry_does_not_destroy_the_whole_log(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text(
        json.dumps(
            {"goal": "g", "attempts": [{"criterion": "a", "change": "x", "accepted": True}, "junk"]}
        )
    )
    reloaded = RunState.load(path)
    assert len(reloaded.attempts) == 1
    assert reloaded.attempts[0] == Attempt(criterion="a", change="x", accepted=True)


# ── meta: the outer loop watches money, not the score ─────────────────────────


def _state(rounds: list[tuple[bool, int]]) -> RunState:
    state = RunState(goal="g", clock=FakeClock())
    for index, (accepted, cost) in enumerate(rounds):
        state.record("a", f"change{index}", accepted=accepted, cost_picos=cost)
    return state


ANCHORED, _ = _agreed(_criterion("anchor", frozen=True))


def test_too_few_rounds_says_unknown_rather_than_guessing() -> None:
    diagnosis = diagnose(_state([(True, 100), (True, 100)]), ANCHORED)
    assert diagnosis.health is Health.UNKNOWN
    assert diagnosis.intervention is Intervention.CONTINUE
    assert "too few to judge" in diagnosis.detail


def test_falling_cost_per_accepted_change_is_improving() -> None:
    diagnosis = diagnose(_state([(True, 400), (True, 400), (True, 200), (True, 200)]), ANCHORED)
    assert diagnosis.health is Health.IMPROVING
    assert diagnosis.intervention is Intervention.CONTINUE
    assert diagnosis.accepted == 4
    assert diagnosis.spent == Money.from_picos(1200)
    assert diagnosis.cost_per_accepted == Money.from_picos(300)
    assert diagnosis.trend == pytest.approx(0.5)


def test_a_loop_still_accepting_but_paying_more_is_reported_stuck() -> None:
    """The expensive middle case. Every score dashboard calls this progress."""
    diagnosis = diagnose(
        _state([(True, 100), (True, 100), (True, 100), (True, 900)]),
        ANCHORED,
    )
    assert diagnosis.health is Health.STUCK
    assert diagnosis.trend > 1.5
    assert "paying more to stand still" in diagnosis.detail
    assert "STUCK" in diagnosis.report()


def test_a_severely_worsening_loop_is_told_to_stop() -> None:
    diagnosis = diagnose(_state([(True, 100), (True, 100), (True, 100), (True, 5000)]), ANCHORED)
    assert diagnosis.intervention is Intervention.STOP


def test_a_recent_half_that_accepts_nothing_is_stuck_on_its_priors() -> None:
    diagnosis = diagnose(_state([(True, 100), (True, 100), (False, 400), (False, 400)]), ANCHORED)
    assert diagnosis.health is Health.STUCK
    assert diagnosis.intervention is Intervention.DIVERSIFY
    assert diagnosis.trend == float("inf")
    assert "returned to priors" in diagnosis.detail


def test_accepting_nothing_at_all_restarts_rather_than_patches() -> None:
    diagnosis = diagnose(_state([(False, 100)] * 4), ANCHORED)
    assert diagnosis.health is Health.STALLED
    assert diagnosis.intervention is Intervention.RESTART_APPROACH
    assert "start differently" in diagnosis.detail


def test_the_outer_loop_has_no_path_to_a_frozen_criterion() -> None:
    """The failure this whole package exists to prevent, arriving one level up.

    An outer loop allowed to relax the definition of success would optimise the
    definition, because that is the cheapest thing in reach. `diagnose()` takes
    the contract so a diagnosis cannot be made around it, and returns a frozen
    dataclass with no reference to it.
    """
    before = ANCHORED.fingerprint
    diagnosis = diagnose(_state([(True, 100)] * 4), ANCHORED)

    assert ANCHORED.fingerprint == before
    assert ANCHORED.frozen_keys == frozenset({"anchor"})
    assert not any(isinstance(v, Contract) for v in vars(diagnosis).values())
    with pytest.raises((AttributeError, TypeError)):
        diagnosis.health = Health.IMPROVING  # type: ignore[misc]


def test_mean_cost_per_accepted_weights_runs_not_attempts() -> None:
    """One enormous run must not decide the figure for every small one."""
    cheap = _state([(True, 100)])
    expensive = _state([(True, 900)] * 50)
    assert mean_cost_per_accepted([cheap, expensive]) == Money.from_picos(500)
    assert _mean_alias is mean_cost_per_accepted


def test_runs_that_accepted_nothing_are_excluded_rather_than_scored_as_free() -> None:
    """Infinite cost per accepted change is not zero cost per accepted change."""
    assert mean_cost_per_accepted([_state([(False, 100)])]) == Money.zero()
    assert mean_cost_per_accepted([]) == Money.zero()
    assert mean_cost_per_accepted([_state([(False, 500)]), _state([(True, 200)])]) == (
        Money.from_picos(200)
    )
