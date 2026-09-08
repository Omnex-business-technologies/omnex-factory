"""Generate the RAG golden suite and its corpus, deterministically.

Both artefacts are committed. Generating them from a script rather than writing
120 JSON objects by hand means the suite can be regrown when the corpus changes,
and — more importantly — that the *shape* of the suite is reviewable: you can
read forty lines here and know the mix of case types, instead of scrolling a
generated file trying to infer it.

The mix is the deliberate part:

    lookup      50   a fact stated on one page
    numeric     25   a figure that must be quoted exactly
    multi_page  20   evidence spanning a page break
    refusal     25   plausible questions the corpus does NOT answer

Refusal cases are a quarter of the suite on purpose. A suite where every
question has an answer cannot distinguish a careful system from a confident
one — it scores a model that always answers exactly the same as one that knows
when to stop, and "knows when to stop" is the property a customer notices.

    python scripts/build_rag_suite.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITES = ROOT / "suites"

SERVICES = [
    "billing",
    "search",
    "ingest",
    "auth",
    "scheduler",
    "notifier",
    "gateway",
    "reporting",
    "archive",
    "webhooks",
    "indexer",
    "importer",
    "exporter",
    "reconciler",
    "dispatcher",
    "collector",
    "renderer",
    "validator",
    "throttler",
    "replicator",
    "compactor",
    "planner",
    "resolver",
    "shipper",
    "sampler",
]


def build_corpus() -> tuple[list[str], dict[str, dict[str, object]]]:
    """One page per service, plus facts recording where each answer lives."""
    pages: list[str] = []
    facts: dict[str, dict[str, object]] = {}

    for index, service in enumerate(SERVICES):
        page = index + 1
        timeout = 5 + index
        pool = 10 + index * 2
        retries = 2 + (index % 4)
        owner = f"team-{chr(ord('a') + index % 6)}"

        pages.append(
            f"The {service} service runs in the shared cluster and is owned by {owner}. "
            f"Its request timeout is {timeout} seconds. "
            f"The {service} connection pool holds {pool} connections. "
            f"Failed {service} requests are retried {retries} times before the request "
            f"is moved to the dead-letter queue. "
            f"Restarting {service} requires draining the queue first."
        )
        facts[service] = {
            "page": page,
            "timeout": timeout,
            "pool": pool,
            "retries": retries,
            "owner": owner,
        }

    return pages, facts


def build_suite(facts: dict[str, dict[str, object]]) -> dict[str, object]:
    cases: list[dict[str, object]] = []

    # Lookup: one stated fact, one page.
    for service in SERVICES[:25]:
        f = facts[service]
        cases.append(
            {
                "id": f"lookup-owner-{service}",
                "question": f"Which team owns the {service} service?",
                "expected": f"The {service} service is owned by {f['owner']}.",
                "must_cite": [f["page"]],
                "tags": ["lookup", "ownership"],
            }
        )
    for service in SERVICES[:25]:
        f = facts[service]
        cases.append(
            {
                "id": f"lookup-restart-{service}",
                "question": f"What must happen before restarting {service}?",
                "expected": f"Restarting {service} requires draining the queue first.",
                "must_cite": [f["page"]],
                "tags": ["lookup", "procedure"],
            }
        )

    # Numeric: the figure must be quoted exactly, which is where grounding earns
    # its keep — a plausible wrong number is the most damaging RAG failure.
    for service in SERVICES[:13]:
        f = facts[service]
        cases.append(
            {
                "id": f"numeric-timeout-{service}",
                "question": f"What is the request timeout for {service}?",
                "expected": f"The {service} request timeout is {f['timeout']} seconds.",
                "must_cite": [f["page"]],
                "tags": ["numeric", "timeout"],
            }
        )
    for service in SERVICES[:12]:
        f = facts[service]
        cases.append(
            {
                "id": f"numeric-pool-{service}",
                "question": f"How many connections are in the {service} pool?",
                "expected": f"The {service} connection pool holds {f['pool']} connections.",
                "must_cite": [f["page"]],
                "tags": ["numeric", "capacity"],
            }
        )

    # Multi-page: two services, two pages, one answer.
    for index in range(20):
        a, b = SERVICES[index], SERVICES[index + 1]
        fa, fb = facts[a], facts[b]
        cases.append(
            {
                "id": f"multi-compare-{a}-{b}",
                "question": f"Do {a} and {b} have the same retry count?",
                "expected": (
                    f"{a} retries {fa['retries']} times and {b} retries {fb['retries']} times."
                ),
                "must_cite": sorted({fa["page"], fb["page"]}),
                "tags": ["multi_page", "comparison"],
            }
        )

    # Refusal: plausible, specific, and genuinely absent from the corpus.
    absent = [
        ("cost", "What is the monthly cost of running {s}?"),
        ("sla", "What is the uptime SLA for {s}?"),
        ("language", "Which programming language is {s} written in?"),
        ("oncall", "Who is on call for {s} this weekend?"),
        ("region", "Which cloud region does {s} run in?"),
    ]
    for kind, template in absent:
        for service in SERVICES[:5]:
            cases.append(
                {
                    "id": f"refusal-{kind}-{service}",
                    "question": template.format(s=service),
                    "expected": "",
                    "expect_refusal": True,
                    "tags": ["refusal", kind],
                }
            )

    return {"name": "rag_core", "version": "1", "cases": cases}


def main() -> None:
    SUITES.mkdir(parents=True, exist_ok=True)
    pages, facts = build_corpus()
    (SUITES / "rag_core_corpus.json").write_text(
        json.dumps({"doc_id": "runbook", "pages": pages}, indent=2)
    )
    suite = build_suite(facts)
    (SUITES / "rag_core.json").write_text(json.dumps(suite, indent=2))

    tags: dict[str, int] = {}
    for case in suite["cases"]:  # type: ignore[index]
        for tag in case["tags"]:  # type: ignore[index]
            tags[tag] = tags.get(tag, 0) + 1
    print(f"{len(suite['cases'])} cases over {len(pages)} pages")  # type: ignore[arg-type]
    for tag, count in sorted(tags.items()):
        print(f"  {tag:<12} {count}")


if __name__ == "__main__":
    main()
