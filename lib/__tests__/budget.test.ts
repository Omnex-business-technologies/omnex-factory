import { describe, it, expect } from 'vitest'
import { RunBudget, estimateCostEur, DEFAULT_LIMITS } from '@/lib/core/agents/budget'

describe('RunBudget', () => {
  it('allows work while every ceiling has room', () => {
    const b = new RunBudget()
    expect(b.check().ok).toBe(true)
  })

  it('stops on passes — catches a loop that thrashes without spending', () => {
    const b = new RunBudget({ maxPasses: 3 })
    for (let i = 0; i < 3; i++) {
      expect(b.check().ok).toBe(true)
      b.record({ tokens: 10 })
    }
    const c = b.check()
    expect(c.ok).toBe(false)
    expect(c.reason).toBe('passes')
    // The message has to name the number, or a log line cannot be acted on.
    expect(c.message).toContain('3')
  })

  it('stops on tokens — catches one runaway generation a pass cap would miss', () => {
    const b = new RunBudget({ maxPasses: 100, maxTokens: 1000 })
    b.record({ tokens: 1200 })
    const c = b.check()
    expect(c.ok).toBe(false)
    expect(c.reason).toBe('tokens')
  })

  it('stops on cost before passes or tokens are exhausted', () => {
    const b = new RunBudget({ maxPasses: 100, maxTokens: 1_000_000, maxCostEur: 0.10 })
    b.record({ tokens: 100, costEur: 0.15 })
    const c = b.check()
    expect(c.ok).toBe(false)
    expect(c.reason).toBe('cost')
  })

  it('stops on wall clock even with nothing recorded', () => {
    const b = new RunBudget({ maxWallMs: -1 })
    const c = b.check()
    expect(c.ok).toBe(false)
    expect(c.reason).toBe('wall_clock')
  })

  it('default wall limit sits under the 60s platform ceiling', () => {
    // If this ever exceeds the platform timeout, the run dies without a reason —
    // which is the exact failure the budget exists to prevent.
    expect(DEFAULT_LIMITS.maxWallMs).toBeLessThan(60_000)
  })

  it('proves a free run spent nothing rather than assuming it', () => {
    const b = new RunBudget()
    b.record({ tokens: 5000, costEur: estimateCostEur('groq', 'llama-3.3-70b-versatile', 4000, 1000) })
    b.record({ tokens: 3000, costEur: estimateCostEur('ollama', 'llama3.1', 2000, 1000) })
    expect(b.wasFree()).toBe(true)
  })

  it('treats an unknown provider as paid, so real spend cannot hide', () => {
    const known = estimateCostEur('groq', 'llama-3.3-70b-versatile', 1_000_000, 1_000_000)
    const unknown = estimateCostEur('some-new-vendor', 'whatever', 1_000_000, 1_000_000)
    expect(known).toBe(0)
    expect(unknown).toBeGreaterThan(0)
  })

  it('treats a hosted provider as paid once its model is not the free default', () => {
    // GROQ_MODEL / GOOGLE_MODEL / HF_LLM_MODEL can point at any model
    // independently of which provider is selected -- the provider name alone
    // was never evidence the call was free, only the specific default model
    // this codebase's own `providers()` configures is.
    expect(estimateCostEur('groq', 'llama-3.3-70b-versatile', 1_000_000, 1_000_000)).toBe(0)
    expect(estimateCostEur('groq', 'some-other-groq-model', 1_000_000, 1_000_000)).toBeGreaterThan(0)
    expect(estimateCostEur('google', 'gemini-2.0-flash', 1_000_000, 1_000_000)).toBe(0)
    expect(estimateCostEur('google', 'gemini-2.0-pro', 1_000_000, 1_000_000)).toBeGreaterThan(0)
  })

  it("prices an OpenRouter model by its own :free suffix, not by provider name", () => {
    expect(
      estimateCostEur('openrouter', 'meta-llama/llama-3.3-70b-instruct:free', 1_000_000, 1_000_000),
    ).toBe(0)
    expect(
      estimateCostEur('openrouter', 'anthropic/claude-3.5-sonnet', 1_000_000, 1_000_000),
    ).toBeGreaterThan(0)
  })

  it('reports remaining budget so a caller can shrink the next step', () => {
    const b = new RunBudget({ maxPasses: 5, maxTokens: 1000 })
    b.record({ tokens: 400 })
    const c = b.check()
    expect(c.remaining.passes).toBe(4)
    expect(c.remaining.tokens).toBe(600)
  })
})
