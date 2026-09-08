# OMNEX skills

Five skills, each wrapping a system in `engine/` that has a measured number
behind it.

| skill | what it carries |
|---|---|
| [`cost-router`](cost-router/SKILL.md) | routed spend **42.4%** of always-strong at identical accuracy; fan-out break-even priced |
| [`grounded-answers`](grounded-answers/SKILL.md) | **25–30k sentences/sec**, flat with document size; refuses fabricated citations |
| [`finground`](finground/SKILL.md) | **79.1%** vs **55.4%** — and 50% vs 100% hallucination |
| [`injection-corpus`](injection-corpus/SKILL.md) | **30/30** attacks detected, **1/30** false positives |
| [`eval-gate`](eval-gate/SKILL.md) | blocks on newly-failing cases, not on the mean |

## Every number here is reproducible

```bash
cd engine && .venv/bin/python scripts/skill_numbers.py
```

That script is the only source of these figures. It re-measures the router and
the grounder from scratch, counts the injection corpus, and *reads* the
FinGround rows out of `engine/suites/LEADERBOARD.md` rather than restating them —
a document and its evidence drift apart exactly at the point where somebody
retypes a number by hand.

The script has already earned its place once: writing it turned up a quadratic
in citation restoration that 495 passing tests could not see, because the bug
was a performance bug and every test was a correctness test.

## What these skills are not

They are packaging, not new work. Each one wraps code that already exists,
already has tests, and already has a stated limitation:

- the router's saving depends on the price ratio between your tiers, and the
  skill tells you how to compute *your* break-even rather than quoting ours
- the grounder is lexical: it catches invented entities and wrong figures, and
  it misses an inverted polarity word
- the injection corpus is saturated at 30/30, which says the corpus is small,
  not that prompt injection is solved
- FinGround's corpus is synthetic, deliberately, because a benchmark built on
  copyrighted filings cannot be redistributed and therefore cannot be checked

Each `SKILL.md` states its own limit in its own words. A skill that only lists
what it is good at is a brochure, and the first person to hit the limit in
production stops believing the rest of the numbers too.
