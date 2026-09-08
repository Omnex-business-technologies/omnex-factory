"""The RAG pipeline, as a graph: retrieve → rerank → generate → verify → answer.

A graph rather than a function because the interesting behaviour is in the
edges. `verify` can route back to `generate` with tighter instructions, or
forward to a refusal, and both of those are decisions worth seeing in a trace
and worth being able to interrupt (P15). As a straight-line function the retry
becomes a `while` loop with a counter, and the budget that bounds it becomes a
second counter nobody remembers to check.

The pipeline's product decision, stated plainly: **an answer that cannot be
grounded is not returned.** The honest output is "the documents do not say",
and it is worth far more than a plausible paragraph — a customer who is told the
documents are silent goes and finds out; a customer given a confident invented
answer acts on it. Partial grounding returns the supported sentences and says
how many were removed.

Retrieved content is fenced through P6's `PromptAssembler` before it reaches the
model. A document in a corpus is untrusted input: anyone who can get a file into
the index can put instructions in it, and RAG is the most common delivery route
for indirect prompt injection there is.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from ..core.clock import Clock, SystemClock
from ..core.money import Money
from ..graph.runtime import END, Budget, Graph, GraphRun
from ..guard.injection import PromptAssembler, Provenance, Segment
from ..llm.base import CallOptions, LanguageModel
from ..llm.types import Message
from ..obs.trace import Tracer
from ..vectors.store import VectorStore
from ..vectors.types import Chunk, SearchHit
from .ground import GroundedAnswer, Grounder
from .rerank import LexicalReranker, Reranker

__all__ = ["REFUSAL", "RagAnswer", "RagConfig", "RagPipeline"]

REFUSAL = "The documents provided do not contain an answer to that."

_SYSTEM = """You answer strictly from the supplied excerpts.

Rules:
1. Every sentence that states a fact MUST end with a page citation like [p. 12].
2. Use only the page numbers shown on the excerpts. Never invent one.
3. If the excerpts do not answer the question, reply exactly: {refusal}
4. Do not add background knowledge. If it is not in an excerpt, it does not exist.
5. Quote numbers exactly as they appear. Do not convert units or round."""


@dataclass
class RagConfig:
    #: Candidates pulled from the store before reranking. Reranking can only
    #: reorder what it is given, so this is the real recall ceiling.
    candidates: int = 30
    #: Excerpts actually placed in the prompt. Beyond roughly this many, added
    #: context reliably lowers answer quality rather than raising it — the
    #: relevant passage gets buried and the model attends to the wrong one.
    top_k: int = 6
    max_answer_tokens: int = 600
    #: One regeneration with a stricter instruction when grounding fails badly.
    #: A second almost never helps and doubles the cost of the worst requests.
    max_regenerations: int = 1
    #: Below this fraction of supported claims, regenerate rather than trim.
    regenerate_below_support: float = 0.6
    budget: Budget = field(default_factory=lambda: Budget(max_steps=12, max_seconds=45.0))


@dataclass
class RagAnswer:
    """The answer, the evidence, and everything that was removed on the way."""

    text: str
    grounded: GroundedAnswer
    hits: list[SearchHit] = field(default_factory=list)
    regenerations: int = 0
    cost: Money = field(default_factory=Money.zero)
    stopped_reason: str = ""

    @property
    def refused(self) -> bool:
        return self.text == REFUSAL

    @property
    def pages(self) -> tuple[int, ...]:
        return self.grounded.pages_cited

    @property
    def sources(self) -> list[Chunk]:
        """Only the chunks whose pages survived verification.

        Listing every retrieved chunk as a "source" is the small dishonesty
        almost every RAG UI ships: the sources panel shows ten documents when
        the answer used two, and the other eight lend it unearned authority.
        """
        return [h.chunk for h in self.hits if set(h.chunk.pages) & set(self.pages)]

    def report(self) -> str:
        lines = [
            f"{'REFUSED' if self.refused else 'answered'} "
            f"from {len(self.sources)}/{len(self.hits)} retrieved chunks, "
            f"pages {list(self.pages)}, cost {self.cost.format_adaptive()}"
        ]
        if self.regenerations:
            lines.append(f"  regenerated {self.regenerations}x")
        if self.grounded.dropped:
            lines.append(self.grounded.report())
        if self.stopped_reason:
            lines.append(f"  stopped: {self.stopped_reason}")
        return "\n".join(lines)


class RagPipeline:
    """Retrieval-augmented answering with verified page citations."""

    def __init__(
        self,
        store: VectorStore,
        model: LanguageModel,
        config: RagConfig | None = None,
        reranker: Reranker | None = None,
        grounder: Grounder | None = None,
        tracer: Tracer | None = None,
        clock: Clock | None = None,
    ) -> None:
        self.store = store
        self.model = model
        self.config = config or RagConfig()
        self.reranker = reranker or LexicalReranker()
        self.grounder = grounder or Grounder()
        self.tracer = tracer
        self.clock = clock or SystemClock()

    # ── the graph ─────────────────────────────────────────────────────────
    def _build(self) -> Graph:
        graph = Graph(budget=self.config.budget, clock=self.clock)
        graph.add_node("retrieve", self._retrieve)
        graph.add_node("rerank", self._rerank)
        graph.add_node("generate", self._generate)
        graph.add_node("verify", self._verify)
        graph.add_node("refuse", self._refuse)

        graph.set_entry("retrieve")
        # Nothing retrieved: refuse without paying for a generation that has
        # nothing to work from. The cheapest correct answer in the system.
        graph.add_conditional_edge("retrieve", lambda s: "rerank" if s["hits"] else "refuse")
        graph.add_edge("rerank", "generate")
        graph.add_edge("generate", "verify")
        graph.add_conditional_edge("verify", self._after_verify)
        graph.add_edge("refuse", END)
        return graph

    def _after_verify(self, state: dict[str, Any]) -> str:
        grounded: GroundedAnswer = state["grounded"]
        # Regeneration is considered BEFORE refusal, deliberately. An answer
        # where nothing at all was supported has support_rate 0.0 — the case
        # most worth one stricter retry — and checking `refused` first would
        # send exactly those straight to a refusal without ever retrying.
        if (
            grounded.support_rate < self.config.regenerate_below_support
            and state["regenerations"] < self.config.max_regenerations
        ):
            return "generate"
        if grounded.refused:
            return "refuse"
        return END

    # ── nodes ─────────────────────────────────────────────────────────────
    def _retrieve(self, state: dict[str, Any]) -> dict[str, Any]:
        hits = self.store.search(
            state["question"],
            limit=self.config.candidates,
            tenant=state.get("tenant"),
            where=state.get("where"),
        )
        return {"hits": hits}

    def _rerank(self, state: dict[str, Any]) -> dict[str, Any]:
        return {"hits": self.reranker.rerank(state["question"], state["hits"], self.config.top_k)}

    def _generate(self, state: dict[str, Any]) -> dict[str, Any]:
        hits: list[SearchHit] = state["hits"]
        # Keyed off whether a draft already exists, not off the counter — the
        # counter is updated in this same patch, so reading it here would make
        # the second attempt use the first attempt's lenient prompt and repeat
        # the failure it was regenerating to fix.
        stricter = bool(state.get("draft"))

        assembler = PromptAssembler()
        segments = [
            Segment(_system_prompt(stricter), Provenance.TRUSTED, "system"),
            # Every excerpt is UNTRUSTED. A document in a corpus is input from
            # whoever could get a file into the index, and RAG is the most
            # common delivery route for indirect prompt injection there is.
            *[
                Segment(_excerpt(hit.chunk), Provenance.UNTRUSTED, f"page-{hit.chunk.page}")
                for hit in hits
            ],
            Segment(f"Question: {state['question']}", Provenance.USER, "question"),
        ]
        messages, findings = assembler.assemble(segments)

        completion = self.model.complete(
            messages, CallOptions(max_tokens=self.config.max_answer_tokens, temperature=0.0)
        )
        return {
            "draft": completion.text,
            "cost_picos": state.get("cost_picos", 0) + completion.cost.picos,
            "regenerations": state["regenerations"] + (1 if stricter else 0),
            "injection_findings": [f.rule for f in findings],
        }

    def _verify(self, state: dict[str, Any]) -> dict[str, Any]:
        evidence = [hit.chunk for hit in state["hits"]]
        return {"grounded": self.grounder.check(state["draft"], evidence)}

    def _refuse(self, state: dict[str, Any]) -> dict[str, Any]:
        return {
            "grounded": GroundedAnswer(
                text="", checks=state.get("grounded", GroundedAnswer("")).checks
            )
        }

    # ── entry point ───────────────────────────────────────────────────────
    def answer(
        self,
        question: str,
        tenant: str | None = None,
        where: dict[str, Any] | None = None,
    ) -> RagAnswer:
        graph = self._build()
        initial: dict[str, Any] = {
            "question": question,
            "tenant": tenant,
            "where": where,
            "hits": [],
            "draft": "",
            "regenerations": 0,
            "cost_picos": 0,
        }

        if self.tracer is None:
            run = graph.run(initial, spend_of=_spend_of)
        else:
            with self.tracer.span("rag", kind="retrieval", question_chars=len(question)) as span:
                run = graph.run(initial, spend_of=_spend_of)
                span.set(
                    hits=len(run.state.get("hits", [])),
                    regenerations=run.state.get("regenerations", 0),
                )
        return self._to_answer(run)

    @staticmethod
    def _to_answer(run: GraphRun) -> RagAnswer:
        grounded: GroundedAnswer = run.state.get("grounded") or GroundedAnswer("")
        return RagAnswer(
            text=grounded.text if grounded.text.strip() else REFUSAL,
            grounded=grounded,
            hits=list(run.state.get("hits", [])),
            regenerations=run.state.get("regenerations", 0),
            cost=Money.from_picos(int(run.state.get("cost_picos", 0))),
            stopped_reason=run.stopped_reason,
        )


def _spend_of(state: Any) -> Money:
    return Money.from_picos(int(state.get("cost_picos", 0)))


def _system_prompt(stricter: bool) -> str:
    base = _SYSTEM.format(refusal=REFUSAL)
    if not stricter:
        return base
    # The regeneration prompt names the failure. "Be more careful" changes
    # nothing; "you cited a page that was not shown to you" changes behaviour.
    return (
        base + "\n\nYour previous answer contained statements that the excerpts do not support, "
        "or cited page numbers that were not shown to you. Write only what the excerpts "
        "state, and cite the page each statement came from. If that leaves nothing to say, "
        f"reply exactly: {REFUSAL}"
    )


def _excerpt(chunk: Chunk) -> str:
    """One excerpt, labelled with the page the model must cite.

    The page marker goes on the excerpt itself rather than in a separate list.
    A list of sources at the end of a prompt is routinely misaligned by the
    model — it cites the third page for the first excerpt — and the failure
    looks exactly like a hallucinated citation while being a formatting bug.
    """
    return f"{chunk.cite}\n{chunk.text}"


def build_messages(question: str, hits: Sequence[SearchHit]) -> list[Message]:
    """The prompt, exposed for tests and for the eval harness (P4)."""
    assembler = PromptAssembler()
    segments = [
        Segment(_system_prompt(False), Provenance.TRUSTED, "system"),
        *[Segment(_excerpt(h.chunk), Provenance.UNTRUSTED, f"page-{h.chunk.page}") for h in hits],
        Segment(f"Question: {question}", Provenance.USER, "question"),
    ]
    messages, _ = assembler.assemble(segments)
    return messages
