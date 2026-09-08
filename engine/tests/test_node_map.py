"""The node map — 507 capabilities, and the rule a machine may not break.

`ontology_map.py` is guarded because a branch claim decays when a symbol moves.
This file guards something sharper: the map is largely MACHINE-PROPOSED, and the
temptation it creates is for the proposer to also award itself the coverage. The
load-bearing test is `test_no_node_is_implemented_without_a_human`, which is the
frozen-criteria rule one level below where `ontology_map.py` enforces it.
"""

from __future__ import annotations

import json

import pytest
from ingest_atlas import EXPECTED_NODES
from node_map import (
    CLAIMS,
    NODES,
    Node,
    _split_node,
    _split_symbol,
    audit,
    load,
    propose,
    public_symbols,
    render,
)

pytestmark = pytest.mark.skipif(
    not NODES.exists(), reason="the node claim file is not in this checkout"
)

ALL = load() if NODES.exists() else []


def test_every_node_the_export_declares_is_classified() -> None:
    assert len(ALL) == EXPECTED_NODES


def test_no_node_is_implemented_without_a_human() -> None:
    """A proposer that can also confirm its proposals grades its own work.

    Whether `omnex.vectors.HybridStore` *is* "Vector Search" is a judgement about
    meaning, and it is exactly the judgement a system measuring its own coverage
    gets generously wrong. Resolution is mechanical and stays mechanical;
    agreement is not and may not become so.
    """
    for node in ALL:
        if node.claim == "implemented":
            assert node.verified, f"{node.branch}/{node.name}"


def test_every_alias_resolves_right_now() -> None:
    """The map cannot describe a repository that has been refactored out from under it."""
    problems = audit(ALL)
    assert not problems, problems[:5]


def test_a_claim_above_gap_must_name_an_alias() -> None:
    for node in ALL:
        if node.claim != "gap":
            assert node.alias, f"{node.branch}/{node.name} claims {node.claim} with no alias"
        assert node.claim in CLAIMS


def test_an_alias_pointing_at_nothing_is_caught() -> None:
    """The guard, observed failing, rather than assumed wired."""
    liar = Node(
        branch="XII",
        name="Fabricated",
        claim="proposed",
        alias="omnex.router.NoSuchSymbol",
        verified=False,
    )
    problems = audit([liar])
    assert problems and "NoSuchSymbol" in problems[0]


def test_claiming_implemented_without_verification_is_caught() -> None:
    cheat = Node(
        branch="XII",
        name="Fabricated",
        claim="implemented",
        alias="omnex.router.Router",
        verified=False,
    )
    problems = audit([cheat])
    assert any("human verification" in p for p in problems)


def test_proposals_stay_conservative() -> None:
    """A looser rule makes a longer list a reviewer must DISPROVE one by one.

    That is how a review queue becomes a rubber stamp: the cost of rejecting is
    paid per item, the cost of accepting everything is paid once.
    """
    symbols = public_symbols()
    assert propose("Bananas In Transit", symbols) is None
    assert propose("Router", symbols) == "omnex.router.Router"


def test_the_document_says_a_machine_may_not_award_coverage() -> None:
    page = render(ALL)
    assert "did not decide that two names mean the same thing" in page
    assert "correct, not pessimistic" in page


def test_the_claim_file_is_valid_json_with_every_field() -> None:
    raw = json.loads(NODES.read_text(encoding="utf-8"))
    assert len(raw["nodes"]) == EXPECTED_NODES
    for entry in raw["nodes"]:
        assert set(entry) >= {"branch", "name", "claim", "alias", "verified"}


# ── refresh: what a machine may do after code lands ────────────────────────
def test_refresh_proposes_for_a_gap_once_the_code_exists() -> None:
    """The case this was built for: `omnex.mcp` landed after the map was written.

    A map that never looks again reports a gap for a capability now in the
    package, and every number quoting it is wrong from that moment on.
    """
    from node_map import Node, refresh

    nodes = [Node(branch="XII", name="MCP", claim="gap", alias=None, verified=False)]
    moved = refresh(nodes, {"McpClient": "omnex.mcp"})
    assert moved and nodes[0].claim == "proposed"
    assert nodes[0].alias == "omnex.mcp.McpClient"


def test_refresh_never_reopens_something_a_human_closed() -> None:
    """Re-proposing a rejection is how a review queue stops shrinking.

    `Code -> omnex.mcp.ErrorCode` was proposed by the first refresh and is wrong.
    Once somebody says so, it must not come back on the next run, or the queue
    only ever grows and people stop reading it.
    """
    from node_map import Node, refresh

    rejected = Node(
        branch="XIV",
        name="Code",
        claim="rejected",
        alias="omnex.mcp.ErrorCode",
        verified=True,
        note="an error code is not code execution",
    )
    accepted = Node(
        branch="XII", name="MCP", claim="implemented", alias="omnex.mcp.McpClient", verified=True
    )
    before = [(n.claim, n.alias) for n in (rejected, accepted)]
    assert refresh([rejected, accepted], {"ErrorCode": "omnex.mcp"}) == []
    assert [(n.claim, n.alias) for n in (rejected, accepted)] == before


def test_refresh_leaves_a_proposal_somebody_may_be_part_way_through() -> None:
    from node_map import Node, refresh

    node = Node(
        branch="VI", name="Chunking", claim="proposed", alias="omnex.rag.Chunk", verified=False
    )
    assert refresh([node], {"Chunker": "omnex.rag"}) == []
    assert node.alias == "omnex.rag.Chunk"


def test_a_rejection_needs_a_human_just_as_much_as_an_acceptance() -> None:
    from node_map import Node, audit

    node = Node(
        branch="XIV", name="Code", claim="rejected", alias="omnex.mcp.ErrorCode", verified=False
    )
    problems = audit([node])
    assert any("without a human verification" in p for p in problems)


def test_an_off_branch_proposal_is_flagged_and_not_filtered() -> None:
    """The wrong proposals cluster off-branch, but the good ones live there too.

    `Code -> omnex.mcp.ErrorCode` sits on a branch that claims no MCP and is
    plainly wrong. `Quantization -> omnex.serving.QuantizationProfile` also
    crosses a boundary and is plainly right. Turning the flag into a filter
    discards the second to catch the first.
    """
    from node_map import Node, off_branch

    modules = {"XIV": {"omnex.graph"}, "XII": {"omnex.mcp"}}
    wrong = Node(
        branch="XIV", name="Code", claim="proposed", alias="omnex.mcp.ErrorCode", verified=False
    )
    right = Node(
        branch="XII", name="MCP", claim="proposed", alias="omnex.mcp.McpClient", verified=False
    )
    assert off_branch(wrong, modules)
    assert not off_branch(right, modules)
    # A branch claiming no modules cannot flag anything, and must not pretend to.
    assert not off_branch(wrong, {"XIV": set()})


# ── containment runs one way ───────────────────────────────────────────────
def test_a_symbol_more_specific_than_the_node_can_be_its_implementation() -> None:
    from node_map import propose

    assert propose("MCP", {"McpClient": "omnex.mcp"}) == "omnex.mcp.McpClient"
    assert propose("Quantization", {"QuantizationProfile": "omnex.serving"}) is not None


def test_a_symbol_broader_than_the_node_is_not_proposed() -> None:
    """The rule that removed thirty-five proposals in one run.

    `omnex.factory.Tool` is not "Tool Registry". It is also not Tool Discovery,
    Tool Selection, Tool Permissions, Tool Invocation, Tool Sandbox, Tool
    Timeout, Tool Retry, Tool Audit or nine others — and the earlier
    bidirectional rule proposed it for every one of them, to the same symbol, in
    a single refresh. A reviewer facing that stops reviewing.
    """
    from node_map import propose

    for node in ("Tool Registry", "Tool Discovery", "Tool Permissions", "Tool Sandbox"):
        assert propose(node, {"Tool": "omnex.factory"}) is None, node


def test_an_exact_token_set_still_matches_in_either_reading() -> None:
    from node_map import propose

    assert propose("Rate Limit", {"RateLimit": "omnex.guard"}) == "omnex.guard.RateLimit"


# ── prune: the machine withdraws what the machine proposed ─────────────────
def test_prune_withdraws_a_proposal_the_rule_no_longer_makes() -> None:
    """Tightening a rule must not leave the file describing a run nobody would get."""
    from node_map import Node, prune

    stale = Node(
        branch="XIV",
        name="Tool Registry",
        claim="proposed",
        alias="omnex.factory.Tool",
        verified=False,
    )
    kept = Node(
        branch="XII", name="MCP", claim="proposed", alias="omnex.mcp.McpClient", verified=False
    )
    withdrawn = prune([stale, kept])
    assert len(withdrawn) == 1
    assert stale.claim == "gap" and stale.alias is None
    assert kept.claim == "proposed" and kept.alias == "omnex.mcp.McpClient"


def test_prune_never_overrules_a_human() -> None:
    """A matcher that changed its mind does not outrank somebody who looked."""
    from node_map import Node, prune

    accepted = Node(
        branch="XIV",
        name="Tool Registry",
        claim="implemented",
        alias="omnex.factory.Tool",
        verified=True,
    )
    assert prune([accepted]) == []
    assert accepted.claim == "implemented" and accepted.alias == "omnex.factory.Tool"


def test_withdrawing_noise_raises_the_gap_count_and_that_is_correct() -> None:
    """The honest direction. The lower number was inflated by proposals nobody believed."""
    nodes = load()
    proposed = [n for n in nodes if n.claim == "proposed"]
    assert proposed, "every proposal was withdrawn, which is a different bug"
    for node in proposed:
        assert node.alias is not None
        symbol = node.alias.rpartition(".")[2]
        assert _split_node(node.name) <= _split_symbol(symbol), node.name
