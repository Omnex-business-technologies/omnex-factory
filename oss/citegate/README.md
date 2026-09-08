# citegate

**Check that every sentence of a RAG answer is actually supported by the page it
cites. No dependencies, no model call, microseconds.**

```python
from citegate import Grounder, Source

grounder = Grounder()
result = grounder.check(
    "The connection pool defaults to twenty connections. [p. 12] "
    "It also scales automatically during peak load. [p. 12]",
    sources=[Source(page=12, text="The connection pool defaults to twenty connections.")],
)

result.text          # "The connection pool defaults to twenty connections. [p. 12]"
result.support_rate  # 0.5
result.dropped       # the autoscaling claim, with the reason
result.refused       # False — something survived
```

## What it catches

| Failure | Example | Verdict |
|---|---|---|
| **Fabricated citation** | cites `[p. 41]` of a 30-page document | `fabricated_citation` |
| **Unsupported claim** | real page, but it does not say that | `unsupported` |
| **Invented number** | "4.2%" where the source says "8.4%" | `unsupported` |
| **Invented quantity in words** | "fifty connections" where the source says "twenty" | `unsupported` |
| **Uncited assertion** | a factual sentence with no citation | `uncited` |

Connectives that assert nothing ("In summary,") pass without a citation, and a
sentence carrying a quantity is always treated as a claim however short it is.

## Why zero dependencies

Every other grounding checker needs either a judge model — a network call and a
bill *per sentence, per request* — or a cross-encoder, which means torch, a
2 GB install and a model download. Both are more accurate than this.

Neither can run inside a request handler on every response. citegate can, which
means it is a **gate** rather than an offline metric, and a gate is the only
thing that stops an invented figure reaching a user.

Use both: citegate in the request path, a judge in your weekly eval.

## What it does not catch

Stated plainly, because a checker that oversells itself is worse than none.

**A swapped polarity word.** "Latency increases" against a source saying
"latency decreases" shares three content words out of four and passes. Closing
this needs entailment, which needs a model.

**Anything requiring inference.** If the source says "revenue grew 10% to €110m"
and the answer says "revenue was €100m last year", that is correct and citegate
rejects it.

The design is deliberately conservative in the safe direction: it will reject a
correctly-paraphrased sentence — costing you a slightly terser answer — before
it will accept an invented one.

## Integrations

```python
# LangChain
sources = [Source(page=d.metadata["page"], text=d.page_content) for d in docs]

# LlamaIndex
sources = [Source(page=n.metadata["page_label"], text=n.get_content()) for n in nodes]
```

Both are one line because `Source` is deliberately just a page number and text.

## Benchmark

`python -m pytest tests/ -q` runs the correctness suite. `python bench.py`
measures throughput — roughly 40,000 sentence-checks per second on one core, or
about 25 microseconds per sentence, against 300–1500 ms for a judge call.

## Licence

MIT. Extracted from the [OMNEX engine](https://github.com/RaveZona/omnex-factory),
where it runs in the request path of a production RAG pipeline.
