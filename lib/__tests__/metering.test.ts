/**
 * The money path. These are the tests that decide whether the copilot is a
 * product or a cost centre.
 *
 * The first version of the route shipped with a cost panel reading €0.00, no
 * ledger entry, no ceiling and no manifest — every run spending provider money
 * and billing nobody. Each fault below is pinned so it cannot come back
 * quietly, because a billing bug is invisible from the screen: the customer
 * sees an answer either way.
 */
import { describe, it, expect, vi } from 'vitest'
import { Trace } from '@/lib/core/agents/trace'
import { toSSE, type RunStep, type SettledOutcome } from '@/lib/core/agents/stream'
import { creditsFor, priceCall, MIN_CREDITS, CREDITS_PER_EUR } from '@/lib/core/agents/metering'
import { estimateCostEur, RunBudget } from '@/lib/core/agents/budget'
import { MODULES, liveModules } from '@/lib/modules/registry'
import type { LlmResult } from '@/lib/core/llm/provider'

const drain = async (stream: ReadableStream<Uint8Array>): Promise<void> => {
  const reader = stream.getReader()
  for (;;) {
    const { done } = await reader.read()
    if (done) break
  }
}

const step = (name: string, run: RunStep['run']): RunStep => ({ name, kind: 'llm', run })

describe('pricing a call', () => {
  it('uses the provider’s reported usage when it gives one', () => {
    const result: LlmResult = {
      text: 'hello',
      provider: 'anthropic',
      model: 'm',
      usage: { promptTokens: 1_000_000, completionTokens: 1_000_000 },
    }
    const cost = priceCall(result, 'prompt')

    expect(cost.estimated).toBe(false)
    expect(cost.promptTokens).toBe(1_000_000)
    // 0.8 in + 4.0 out per million, from the rate table.
    expect(cost.costEur).toBeCloseTo(4.8, 4)
  })

  it('falls back to a length estimate and SAYS it estimated', () => {
    // A guess presented as a measurement is how a billing system eventually
    // bills someone for the difference.
    const result: LlmResult = { text: 'x'.repeat(400), provider: 'anthropic', model: 'm' }
    const cost = priceCall(result, 'y'.repeat(400))

    expect(cost.estimated).toBe(true)
    expect(cost.promptTokens).toBeGreaterThan(0)
    expect(cost.completionTokens).toBeGreaterThan(0)
  })

  it('prices a cache hit at zero rather than at the unknown-provider rate', () => {
    // `complete()` returns `cache:exact` as the provider. That name is not in
    // the rate table, so the unknown-provider fallback would charge the one
    // genuinely free path in the system at the most expensive rate it knows.
    expect(estimateCostEur('cache:exact', 500_000, 500_000)).toBe(0)
    expect(estimateCostEur('cache:semantic', 500_000, 500_000)).toBe(0)

    // …while a genuinely unknown provider is still treated as paid.
    expect(estimateCostEur('some-new-vendor', 1_000_000, 0)).toBeGreaterThan(0)
  })

  it('treats a free provider as free', () => {
    expect(estimateCostEur('ollama', 1_000_000, 1_000_000)).toBe(0)
  })
})

describe('credits charged', () => {
  it('never charges for a run that called no provider', () => {
    // An aborted run that never reached the model owes nothing.
    expect(creditsFor(0, false)).toBe(0)
    expect(creditsFor(1.5, false)).toBe(0)
  })

  it('charges the floor for a run that did work but spent nothing', () => {
    // The local tier and cache hits are free to us but still consumed request
    // overhead. The floor is the smallest unit, not a minimum-charge trick.
    expect(creditsFor(0, true)).toBe(MIN_CREDITS)
  })

  it('scales with measured spend and never bills less than was spent', () => {
    const cost = 0.42
    const credits = creditsFor(cost, true)

    expect(credits).toBe(Math.ceil(cost * CREDITS_PER_EUR))
    expect(credits / CREDITS_PER_EUR).toBeGreaterThanOrEqual(cost)
  })

  it('is monotone in cost — a dearer run never bills less', () => {
    const cheap = creditsFor(0.01, true)
    const dear = creditsFor(0.9, true)
    expect(dear).toBeGreaterThan(cheap)
  })
})

describe('metering the run', () => {
  it('settles once on success, with what the client was told', async () => {
    const settled: SettledOutcome[] = []
    const trace = new Trace('t')
    await drain(
      toSSE(trace, [step('answer', async () => ({ text: 'hi', costEur: 0.02, tokens: 30 }))], {
        heartbeatMs: 0,
        onSettled: (o) => {
          settled.push(o)
        },
      }),
    )

    expect(settled).toHaveLength(1)
    expect(settled[0]).toMatchObject({ reason: 'complete', costEur: 0.02 })
  })

  it('settles when the run FAILS — the ledger must not lose a paid failure', async () => {
    const settled: SettledOutcome[] = []
    const trace = new Trace('t')
    const steps = [
      step('paid', async () => ({ text: 'x', costEur: 0.05, tokens: 10 })),
      step('boom', async () => {
        throw new Error('provider refused')
      }),
    ]
    await drain(toSSE(trace, steps, { heartbeatMs: 0, onSettled: (o) => void settled.push(o) }))

    expect(settled).toHaveLength(1)
    expect(settled[0]?.reason).toBe('error')
    // The money spent before the failure is still on the record.
    expect(settled[0]?.costEur).toBeCloseTo(0.05, 4)
  })

  it('settles when the client disconnects mid-run', async () => {
    const settled: SettledOutcome[] = []
    const controller = new AbortController()
    const trace = new Trace('t')
    const steps = [
      step('first', async () => {
        controller.abort()
        return { text: 'x', costEur: 0.03, tokens: 5 }
      }),
      step('second', async () => ({ text: 'y', costEur: 1, tokens: 5 })),
    ]
    await drain(
      toSSE(trace, steps, {
        signal: controller.signal,
        heartbeatMs: 0,
        onSettled: (o) => void settled.push(o),
      }),
    )

    expect(settled).toHaveLength(1)
    expect(settled[0]?.reason).toBe('aborted')
    // Billed for the first step only — the second never ran.
    expect(settled[0]?.costEur).toBeCloseTo(0.03, 4)
  })

  it('a billing failure does not break the customer’s stream', async () => {
    // Metering that throws must not take the answer down with it.
    const trace = new Trace('t')
    const onSettled = vi.fn(() => {
      throw new Error('ledger unavailable')
    })

    await expect(
      drain(
        toSSE(trace, [step('answer', async () => ({ text: 'hi', costEur: 0.01 }))], {
          heartbeatMs: 0,
          onSettled,
        }),
      ),
    ).resolves.toBeUndefined()

    expect(onSettled).toHaveBeenCalledTimes(1)
  })
})

describe('the run budget', () => {
  it('stops the run with a stated reason instead of running to the platform limit', async () => {
    const budget = new RunBudget({ maxCostEur: 0.05 })
    budget.record({ costEur: 0.06 })

    const check = budget.check()
    expect(check.ok).toBe(false)
    expect(check.reason).toBe('cost')
    expect(check.message).toBeTruthy()
  })
})

describe('the module manifest', () => {
  it('lists the copilot, so finished work is priced and findable', () => {
    const copilot = MODULES.find((m) => m.id === 'copilot')
    expect(copilot).toBeDefined()
    expect(copilot?.creditCost).toBeGreaterThanOrEqual(MIN_CREDITS)
    expect(copilot?.route).toBe('/copilot')
  })

  it('keeps the module-gate rule: only module #1 is live', () => {
    // The registry documents that module #2 does not open until module #1 has
    // taken a real payment. Shipping a module early because it happens to be
    // finished is how that rule dies.
    expect(liveModules().map((m) => m.id)).toEqual(['studio'])
  })

  it('gives every module a price and a route', () => {
    for (const module of MODULES) {
      expect(module.creditCost).toBeGreaterThanOrEqual(0)
      expect(module.route.startsWith('/')).toBe(true)
    }
  })

  it('has no duplicate ids or order positions', () => {
    expect(new Set(MODULES.map((m) => m.id)).size).toBe(MODULES.length)
    expect(new Set(MODULES.map((m) => m.order)).size).toBe(MODULES.length)
  })
})
