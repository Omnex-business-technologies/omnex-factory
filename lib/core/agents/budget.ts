/**
 * Run budget — the stop condition an agent loop is missing by default.
 *
 * An agent loop without a cap is an open wallet. It runs until the platform
 * kills the request, and whatever it spent is spent. That is survivable while
 * every provider is free, and stops being survivable the moment one is not.
 *
 * This enforces three independent ceilings, because they fail differently:
 *   passes  — a loop that makes no progress still counts passes, so this catches
 *             thrash that a token cap would not (short repeated calls).
 *   tokens  — a single runaway generation, which a pass cap would not catch.
 *   wall    — an upstream provider hanging, which neither of the above catches.
 *
 * It is deliberately not a wrapper: an agent calls `check()` before each step,
 * so the loop keeps its own control flow and there is no hidden throw. The
 * reason for stopping is always explicit, which is what makes it debuggable.
 */

export type StopReason = 'passes' | 'tokens' | 'cost' | 'wall_clock' | 'goal_met' | 'aborted'

export interface BudgetLimits {
  /** Maximum loop iterations. */
  maxPasses: number
  /** Maximum total tokens (prompt + completion) across the run. */
  maxTokens: number
  /** Maximum spend in EUR. Zero means "free providers only". */
  maxCostEur: number
  /** Maximum wall-clock milliseconds for the whole run. */
  maxWallMs: number
}

/**
 * Defaults sized for the workflow executor, which runs under a 60s platform
 * limit: the wall-clock ceiling sits below it so the budget stops the run with a
 * reason instead of the platform killing it without one.
 */
export const DEFAULT_LIMITS: BudgetLimits = {
  maxPasses: 12,
  maxTokens: 60_000,
  maxCostEur: 0.5,
  maxWallMs: 50_000,
}

export interface BudgetState {
  passes: number
  tokens: number
  costEur: number
  startedAt: number
}

export interface BudgetCheck {
  ok: boolean
  reason?: StopReason
  /** Human-readable, safe to surface in a response or a log line. */
  message?: string
  remaining: { passes: number; tokens: number; costEur: number; wallMs: number }
}

export class RunBudget {
  readonly limits: BudgetLimits
  private state: BudgetState

  constructor(limits: Partial<BudgetLimits> = {}) {
    this.limits = { ...DEFAULT_LIMITS, ...limits }
    this.state = { passes: 0, tokens: 0, costEur: 0, startedAt: Date.now() }
  }

  /** Call before each step. Does not throw — the caller decides what to do. */
  check(): BudgetCheck {
    const wallMs = Date.now() - this.state.startedAt
    const remaining = {
      passes: this.limits.maxPasses - this.state.passes,
      tokens: this.limits.maxTokens - this.state.tokens,
      costEur: round(this.limits.maxCostEur - this.state.costEur),
      wallMs: this.limits.maxWallMs - wallMs,
    }

    if (remaining.passes <= 0) {
      return { ok: false, reason: 'passes', message: `Stopped after ${this.state.passes} passes (limit ${this.limits.maxPasses}).`, remaining }
    }
    if (remaining.tokens <= 0) {
      return { ok: false, reason: 'tokens', message: `Stopped at ${this.state.tokens} tokens (limit ${this.limits.maxTokens}).`, remaining }
    }
    if (remaining.costEur <= 0) {
      return { ok: false, reason: 'cost', message: `Stopped at €${round(this.state.costEur)} (limit €${this.limits.maxCostEur}).`, remaining }
    }
    if (remaining.wallMs <= 0) {
      return { ok: false, reason: 'wall_clock', message: `Stopped after ${Math.round(wallMs / 1000)}s (limit ${Math.round(this.limits.maxWallMs / 1000)}s).`, remaining }
    }
    return { ok: true, remaining }
  }

  /** Record what a completed step consumed. */
  record(step: { tokens?: number; costEur?: number }): void {
    this.state.passes += 1
    this.state.tokens += Math.max(0, step.tokens ?? 0)
    this.state.costEur += Math.max(0, step.costEur ?? 0)
  }

  /** Snapshot for logging and for the run summary. */
  snapshot(): BudgetState & { wallMs: number } {
    return { ...this.state, wallMs: Date.now() - this.state.startedAt }
  }

  /** True when nothing has been spent — used to assert a run was truly free. */
  wasFree(): boolean {
    return this.state.costEur === 0
  }
}

function round(n: number): number {
  return Math.round(n * 10_000) / 10_000
}

/**
 * Rough EUR cost for a call. Free providers are zero by definition, which is why
 * `wasFree()` is meaningful: a run that touched only the free chain provably
 * spent nothing, rather than being assumed to have.
 */
const RATE_PER_MTOK: Record<string, { in: number; out: number }> = {
  ollama: { in: 0, out: 0 },
  pollinations: { in: 0, out: 0 },
  local: { in: 0, out: 0 },
  groq: { in: 0, out: 0 },
  google: { in: 0, out: 0 },
  huggingface: { in: 0, out: 0 },
  openrouter: { in: 0, out: 0 },
  anthropic: { in: 0.8, out: 4.0 },
  openai: { in: 0.15, out: 0.6 },
}

export function estimateCostEur(provider: string, promptTokens: number, completionTokens: number): number {
  // A cache hit made no provider call, so it cost nothing. This has to be
  // checked BEFORE the unknown-provider fallback: `complete()` returns
  // `cache:exact` / `cache:semantic` as the provider name, which is not in the
  // table, so the fallback would price the one genuinely free path in the
  // system at the most expensive rate it knows.
  if (provider.startsWith('cache:')) return 0

  const rate = RATE_PER_MTOK[provider]
  // An unknown provider is treated as paid, not free: assuming zero would hide
  // real spend behind a name this table has not been updated for.
  const { in: rin, out: rout } = rate ?? { in: 1.0, out: 3.0 }
  return round((promptTokens / 1_000_000) * rin + (completionTokens / 1_000_000) * rout)
}
