"""The judgements. Separated from the rendering so they can be argued with.

Everything in this file is opinion. `relevance`, `integration_cost` and
`substitution` are 0.0-1.0 numbers a person chose, and the engine deliberately
does not compute them from star counts — deriving a strategic judgement from a
popularity metric is the exact failure `omnex.intel` exists to prevent.

Keeping them in their own module, one record per project, means a reader who
disagrees edits a line and re-runs the scan rather than arguing with a
paragraph. It also keeps `scan_intel.py` honest: that file may only render what
is here or what is in the committed evidence, so it cannot quietly invent a
fifteenth strength for a project nobody looked at closely.

`original` is the field that matters most. The brief asks for original
improvements rather than copied implementation, so each record names the thing
OMNEX could build that is BETTER than what the project does — usually by
combining it with something already shipped in `engine/`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["JUDGEMENTS", "Judgement", "for_artifact"]


@dataclass(frozen=True)
class Judgement:
    artifact_id: str
    #: How much this bears on what OMNEX sells. 0.0-1.0.
    relevance: float
    relevance_note: str
    #: Effort to absorb or integrate, 0.0 trivial to 1.0 prohibitive.
    integration_cost: float
    #: How directly it substitutes for something we sell. Drives the threat axis.
    substitution: float
    #: Which shipped engine system it collides with, if any.
    collides_with: str = ""
    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()
    #: The original improvement — what we could build that is better.
    original: str = ""
    verdict_note: str = ""
    tier: int = 1
    enterprise_gaps: tuple[str, ...] = field(default_factory=tuple)


JUDGEMENTS: tuple[Judgement, ...] = (
    Judgement(
        "github:HKUDS/OpenSpace",
        relevance=0.9,
        relevance_note="evidence-based skill evaluation is the same idea as our eval gate (P4/P17)",
        integration_cost=0.4,
        substitution=0.5,
        collides_with="P4 evals, P17 FinGround",
        strengths=(
            "judges skills by task outcome rather than by description, which is the correct axis",
            "local-first hub keeps data under the operator's control — no account required to start",
            "MIT, Python, LiteLLM and SQLite: every dependency is one we already use",
        ),
        weaknesses=(
            "skill quality is scored on outcomes it observed, so a skill used twice has a score "
            "with no confidence attached to it",
            "no stated protection against a skill that succeeds by doing something unsafe",
        ),
        missing=(
            "per-capability regression detection",
            "cost per successful task",
            "refusal scoring",
        ),
        enterprise_gaps=("multi-tenant skill isolation", "audit trail for skill changes"),
        original=(
            "OpenSpace scores a skill by outcome; FinGround (P17) shows that an outcome score "
            "with no refusal column ranks a confabulating system respectably. Combining them — "
            "skill selection gated on a suite that scores refusal separately, with "
            "`Gate` comparing case-by-case rather than on the mean — is a skill registry that "
            "can say WHY it demoted something. That is the version an enterprise can adopt."
        ),
        verdict_note="closest thing to a competitor for the eval work, and the most absorbable",
    ),
    Judgement(
        "github:openmemind/memind",
        relevance=0.85,
        relevance_note="direct overlap with P13 agent memory; names the benchmarks we should score on",
        integration_cost=0.75,
        substitution=0.6,
        collides_with="P13 memory",
        strengths=(
            "publishes numbers on three public memory benchmarks rather than asserting quality",
            "Apache-2.0, so the design is studiable and the interfaces are reusable",
            "reports lower context token usage alongside accuracy, which is the honest pairing",
        ),
        weaknesses=(
            "Java, which is a hard boundary against a Python engine — integration means a "
            "network hop and a second runtime to operate",
            "benchmark claims are self-reported under self-described aligned protocols",
        ),
        missing=("per-tenant memory isolation", "cost ceiling per retrieval", "forgetting audit"),
        enterprise_gaps=("data residency", "right-to-erasure across derived memory graphs"),
        original=(
            "Memind proves the benchmarks matter and that token cost belongs next to accuracy. "
            "The improvement is not a better memory graph — it is scoring memory the way P2 "
            "scores routing: pico-dollar cost per correct recall, with the break-even point "
            "where a cheaper memory tier stops paying. Nobody publishes that, and it is the "
            "number that decides whether memory is worth running at all."
        ),
        verdict_note="the benchmark target for P13; adopt the yardstick, not the runtime",
    ),
    Judgement(
        "github:facebookresearch/HyperAgents",
        relevance=0.35,
        relevance_note="self-improving agents are adjacent to P3, but the licence forecloses use",
        integration_cost=1.0,
        substitution=0.2,
        collides_with="P3 multi-agent",
        strengths=(
            "a genuine research contribution with a corporate research lab behind it",
            "states its own safety hazard about executing model-generated code plainly",
        ),
        weaknesses=(
            "CC BY-NC-SA 4.0 is non-commercial — it cannot be built on by a business at all, "
            "and the ShareAlike term would infect anything derived from it",
            "executes model-generated code, which is a production risk rather than a feature",
        ),
        missing=("commercial licence", "sandbox boundary claims that survive scrutiny"),
        enterprise_gaps=("any commercial use whatsoever",),
        original=(
            "The absorbable idea is the loop, not the code: a meta-agent that proposes changes "
            "and an evaluator that accepts them. We already have the evaluator half (P4) and the "
            "approval half (P15). Self-improvement gated on a human-approved, "
            "fingerprint-bound proposal is the version that can run in production — HyperAgents "
            "cannot ship that because its safety story ends at a warning in the README."
        ),
        verdict_note="READ ONLY — non-commercial licence, absorb the idea and nothing else",
    ),
    Judgement(
        "github:neo4j-labs/create-context-graph",
        relevance=0.8,
        relevance_note="GraphRAG plus scaffolding — overlaps P1 retrieval and the OMNEX module thesis",
        integration_cost=0.5,
        substitution=0.45,
        collides_with="P1 RAG, P12 vectors",
        strengths=(
            "three-memory split — conversation, entity graph, reasoning traces — is a better "
            "decomposition than a single vector store",
            "scaffolds a whole working application, which is the OMNEX module thesis validated "
            "by someone else",
            "Apache-2.0 with LiteLLM provider injection, so nothing is locked to one vendor",
        ),
        weaknesses=(
            "Neo4j is a heavy operational dependency for a small team",
            "generated applications are a starting point, and the scaffold cannot help with the "
            "part that is actually hard",
        ),
        missing=("citation verification on graph answers", "cost per query", "eval suite"),
        enterprise_gaps=("tenant isolation in the graph", "cost attribution per tenant"),
        original=(
            "A graph answer is harder to verify than a passage answer, because the claim is "
            "assembled from edges rather than quoted from a page. Applying the P1 grounder to "
            "graph traversals — every asserted relationship must resolve to an edge that exists, "
            "and a path that cannot be reconstructed is refused — is a genuinely new thing. "
            "GraphRAG systems currently ask you to trust the traversal."
        ),
        verdict_note="best architectural ideas in the set; adopt the memory split",
    ),
    Judgement(
        "github:InternLM/WildClawBench",
        relevance=0.7,
        relevance_note="benchmark methodology to learn from; reports cost per run, which is rare",
        integration_cost=0.3,
        substitution=0.3,
        collides_with="P17 FinGround",
        strengths=(
            "reports execution time and API cost next to the score, which almost no benchmark does",
            "includes a Safety Alignment category rather than measuring capability alone",
            "MIT, and evaluated across four harnesses so results are not tied to one runtime",
        ),
        weaknesses=(
            "60 tasks is small enough that a few task-specific fixes move the ranking",
            "in-the-wild tasks are hard to keep stable, so scores drift for reasons unrelated "
            "to the system under test",
        ),
        missing=("refusal scoring as a separate axis", "contamination checking", "per-case gating"),
        enterprise_gaps=("private task sets", "reproducible scoring on internal data"),
        original=(
            "WildClawBench prices a benchmark run and FinGround separates refusal from accuracy. "
            "Neither does both. A benchmark that reports pico-dollar cost per correct answer AND "
            "hallucination rate in the same table ranks systems the way a buyer actually chooses "
            "one — and our eval harness already computes both halves."
        ),
        verdict_note="fastest grower in the set at +37% — benchmarks are having a moment",
    ),
    Judgement(
        "github:cisco-ai-defense/defenseclaw",
        relevance=0.75,
        relevance_note="agent security governance overlaps P6 guardrails and the P3 audit trail",
        integration_cost=0.6,
        substitution=0.5,
        collides_with="P6 guardrails",
        strengths=(
            "frames the product as evidence and policy enforcement rather than as safety, which "
            "is the honest and the sellable framing",
            "durable audit export is exactly what a regulated buyer procures",
            "Apache-2.0 with a corporate security team behind it",
        ),
        weaknesses=(
            "Go gateway plus Python CLI is two runtimes to operate",
            "scanning capabilities before use cannot catch a capability that turns malicious "
            "after approval",
        ),
        missing=(
            "tamper-evident audit chain",
            "per-tenant policy",
            "injection corpus with measured rates",
        ),
        enterprise_gaps=("SOC2 evidence export", "policy versioning"),
        original=(
            "DefenseClaw exports audit evidence; our P3 audit trail is hash-chained, where the "
            "hash covers sequence and previous hash rather than payload alone, so a deletion is "
            "detectable rather than merely logged. Audit evidence that can prove it was not "
            "edited is a materially stronger product than audit evidence that cannot, and it is "
            "the difference between a log and a record."
        ),
        verdict_note="strongest commercial framing in the set — study the positioning",
    ),
    Judgement(
        "github:slowmist/slowmist-agent-security",
        relevance=0.55,
        relevance_note="attack taxonomy directly usable against our injection corpus (P6)",
        integration_cost=0.15,
        substitution=0.15,
        collides_with="P6 guardrails",
        strengths=(
            "26 attack categories is a taxonomy we can test against rather than a warning",
            "every external input is untrusted until verified is the same provenance rule P6 uses",
            "MIT and documentation-only, so it is cheap to adopt and impossible to break",
        ),
        weaknesses=(
            "documentation cannot be executed, so nothing here is measured",
            "a review framework depends on the reviewer, which does not scale",
        ),
        missing=("machine-readable corpus", "measured detection and false-positive rates"),
        enterprise_gaps=("automated enforcement", "regression tracking as attacks evolve"),
        original=(
            "The taxonomy is prose; our injection corpus is 30 cases with a measured 30/30 "
            "detection and 1/30 false-positive rate. Turning their 26 categories into executable "
            "cases with published detection AND false-positive rates produces the artefact the "
            "field is missing — a security claim with a denominator."
        ),
        verdict_note="cheapest high-value absorption in the set: taxonomy in, corpus out",
    ),
    Judgement(
        "github:patoles/agent-flow",
        relevance=0.6,
        relevance_note="agent-run visualisation overlaps P5 tracing and is the P8 UI we have not built",
        integration_cost=0.45,
        substitution=0.4,
        collides_with="P5 observability, P8 streaming UI",
        strengths=(
            "+64% over 82 days, the fastest grower in the set — this is demand, not curiosity",
            "SSE over a relay server is the right shape and needs no infrastructure",
            "ships as a VS Code extension too, meeting people where they already are",
        ),
        weaknesses=(
            "visualises one agent runtime's hooks, so it is coupled to that runtime's format",
            "shows what happened without saying what it cost",
        ),
        missing=("cost per span", "failure path highlighting", "tail-based sampling"),
        enterprise_gaps=("retention policy", "multi-user access control"),
        original=(
            "Agent Flow shows the shape of a run; our P5 trace attaches pico-dollar cost to leaf "
            "spans and exposes `failure_path()`. A visualiser where the expensive branch is "
            "visibly expensive and the failing path is selectable answers the two questions an "
            "operator actually has, and neither tool answers both today."
        ),
        verdict_note="the template for P8 — and proof the demand is real",
    ),
    Judgement(
        "github:saltbo/agent-kanban",
        relevance=0.5,
        relevance_note="human-in-the-loop coordination surface, adjacent to P15 approvals",
        integration_cost=0.55,
        substitution=0.35,
        collides_with="P15 human-in-the-loop",
        strengths=(
            "Ed25519 identity per agent is the right primitive — actions are attributable",
            "+63% over 82 days",
            "treats delegation between agents as a first-class operation",
        ),
        weaknesses=(
            "FSL-1.1-ALv2 is not open source today; it becomes Apache-2.0 only after two years",
            "a kanban board is a coordination metaphor, not an approval control",
        ),
        missing=("approval bound to a proposal fingerprint", "budget ceilings per task"),
        enterprise_gaps=("delegated authority limits", "segregation of duties"),
        original=(
            "A board shows that an agent claimed a task. P15 binds an approval to the fingerprint "
            "of the exact proposal approved, so an agent cannot alter the plan after sign-off and "
            "proceed under the old approval. Attributable identity plus fingerprint-bound "
            "approval is the combination that makes autonomous work auditable rather than merely "
            "visible."
        ),
        verdict_note="watch the licence — not absorbable until 2028",
    ),
    Judgement(
        "github:soulduse/ai-token-monitor",
        relevance=0.65,
        relevance_note="proves people install software purely to see spend — validates P2/P5 framing",
        integration_cost=0.2,
        substitution=0.3,
        collides_with="P2 router, P5 cost tracking",
        strengths=(
            "+64% over 82 days from a small base — the demand signal is unambiguous",
            "offline by default, which removes the objection that kills spend tooling",
            "applies per-model pricing including cache reads, a detail most trackers miss",
        ),
        weaknesses=(
            "reports spend without reducing it — it is a thermometer, not a thermostat",
            "macOS menu bar only, so it cannot serve a team or a production system",
        ),
        missing=("routing recommendation", "break-even analysis", "team aggregation"),
        enterprise_gaps=("per-tenant attribution", "budget enforcement", "invoice reconciliation"),
        original=(
            "Every tool in this category reports spend. P2 computes the break-even escalation "
            "rate — the point past which routing to a cheap model stops saving money — and our "
            "measured run cut cost to 42.4% at a 14.3% escalation rate against a 97.0% "
            "break-even. A monitor that says you are LOSING MONEY on your current routing "
            "policy, with the arithmetic, is a different product from one that draws a chart."
        ),
        verdict_note="the clearest revenue signal in the set",
    ),
    Judgement(
        "github:oguzbilgic/agent-kernel",
        relevance=0.45,
        relevance_note="markdown-only memory is the low-cost end of P13",
        integration_cost=0.1,
        substitution=0.2,
        collides_with="P13 memory",
        strengths=(
            "no database and no vector store, so it works everywhere and cannot break",
            "git history gives it an audit trail for free",
            "MIT and trivially forkable",
        ),
        weaknesses=(
            "+1.8% over 82 days — attention has moved on",
            "flat markdown does not survive scale; retrieval becomes reading everything",
        ),
        missing=("retrieval ranking", "conflict resolution between notes", "decay"),
        enterprise_gaps=("access control", "any multi-user story at all"),
        original=(
            "The insight worth keeping is that memory in a git repository is auditable by "
            "construction. Combining that with P13's ranked retrieval — files as the durable "
            "store, an index for retrieval, git as the audit log — keeps the property that made "
            "this popular while removing the reason it stalled."
        ),
        verdict_note="STALLED at +1.8% — a good idea that stopped compounding",
    ),
    Judgement(
        "github:Ataraxy-Labs/opensessions",
        relevance=0.3,
        relevance_note="developer surface rather than infrastructure; limited OMNEX overlap",
        integration_cost=0.5,
        substitution=0.1,
        strengths=("Rust, MIT, and a local HTTP API that makes it scriptable",),
        weaknesses=("tmux-only, which caps the addressable audience",),
        missing=("cost visibility", "remote sessions"),
        enterprise_gaps=("team visibility",),
        original=(
            "The reusable idea is the local HTTP API for pushing session metadata — a pattern "
            "our pipeline (P16) could expose so any long-running job reports progress to "
            "whatever the operator already has open."
        ),
        verdict_note="adjacent; note the pattern, do not build it",
    ),
    Judgement(
        "github:ovoment/ovo-local-llm",
        relevance=0.6,
        relevance_note="local-first agent stack, the same thesis as P7",
        integration_cost=0.4,
        substitution=0.35,
        collides_with="P7 local-first",
        strengths=(
            "zero API keys is the strongest possible privacy claim and it is verifiable",
            "MLX-native with Ollama and OpenAI compatibility — the right compatibility surface",
            "bundles RAG, LoRA and image generation into one local install",
        ),
        weaknesses=(
            "+2.0% over 82 days — effectively flat",
            "Apple Silicon only, which is a hard ceiling on the market",
        ),
        missing=("eval harness", "cost comparison against hosted", "team deployment"),
        enterprise_gaps=("fleet management", "policy enforcement"),
        original=(
            "The unanswered question in local-first is when it is actually cheaper. P2 prices "
            "the local tier at zero marginal cost and can compute the crossover against hosted "
            "pricing — a local stack that shows the monthly saving it is producing, in exact "
            "money, sells itself to the buyer who currently cannot justify the hardware."
        ),
        verdict_note="flat despite a good thesis — the market is Apple-only and small",
    ),
    Judgement(
        "github:slavingia/skills",
        relevance=0.4,
        relevance_note="the distribution lesson: 9,800 stars for ten markdown files",
        integration_cost=0.05,
        substitution=0.1,
        strengths=(
            "the highest-starred project in the entire signal set and it contains no code",
            "distributed through a plugin marketplace, which is where the audience already is",
        ),
        weaknesses=(
            "no licence file, which means all rights reserved — it cannot be reused",
            "content is one person's book, so it does not generalise",
        ),
        missing=("licence", "any measurement of whether the skills help"),
        enterprise_gaps=("everything — this is a consumer artefact",),
        original=(
            "The lesson is packaging, not content: ten markdown files in a marketplace "
            "outperformed every engineering project in this scan. OMNEX has eighteen production "
            "systems with measured numbers and no distribution surface. Publishing the "
            "measurable ones as installable skills is the highest-leverage move in this report, "
            "and it is nearly free."
        ),
        verdict_note="DISTRIBUTION LESSON — the most valuable row in the scan",
    ),
    Judgement(
        "github:alvinunreal/awesome-opensource-ai",
        relevance=0.35,
        relevance_note="curation as a growth channel; CC0 so the list itself is reusable",
        integration_cost=0.05,
        substitution=0.05,
        strengths=(
            "CC0-1.0 — genuinely public domain, so the curation can be reused outright",
            "+23% over 82 days for a list, which shows curation still compounds",
        ),
        weaknesses=(
            "a list has no defensibility; the next list replaces it",
            "daily updates are a permanent maintenance burden with no revenue attached",
        ),
        missing=("measurement of the projects listed", "any monetisation"),
        enterprise_gaps=("nothing enterprise about it",),
        original=(
            "A list ranks by opinion. This engine ranks by measured 82-day velocity, licence "
            "absorbability and feature-gap opportunity, with the arithmetic printed. A curated "
            "list that publishes WHY each entry is ranked where it is — and updates itself from "
            "a scanner — is a defensible version of the highest-traffic format in this set."
        ),
        verdict_note="the format works; the version with evidence attached is ours to build",
    ),
)


def for_artifact(artifact_id: str) -> Judgement | None:
    for judgement in JUDGEMENTS:
        if judgement.artifact_id == artifact_id:
            return judgement
    return None
