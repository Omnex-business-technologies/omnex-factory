/**
 * Turning a measured run into a ledger entry.
 *
 * The copilot shipped without this and the arithmetic was stark: every run
 * called a paid provider, displayed a cost to the customer, and recorded
 * nothing — no `usage_events` row, no credit debit. Pure cost, zero revenue,
 * invisible in analytics.
 *
 * ## Why charge afterwards rather than before
 *
 * `/api/studio/generate` charges first and refunds on failure, which is right
 * for a fixed-price unit of work: one generation, one price, known in advance.
 * A streamed run has no such price — it ends when it ends. Charging a guess up
 * front is how a customer gets billed for a run they cancelled after two
 * seconds.
 *
 * So the run is bounded by a budget while it happens, and billed from what it
 * actually spent once it has. The customer never pays for more than was used.
 *
 * ## Why a floor, and why it is small
 *
 * Sub-cent runs would otherwise round to nothing and the platform would carry
 * the request overhead for free. One credit is the floor. It is deliberately
 * the smallest unit rather than a "minimum charge" large enough to be a
 * revenue trick — the honest version of a floor covers overhead and stops.
 *
 * ## Why an estimate is labelled
 *
 * Not every provider reports token usage. Where one does not, cost is
 * estimated from text length, and `estimated: true` travels with the number so
 * a dashboard cannot present a guess as a measurement. A billing system that
 * cannot distinguish the two eventually bills someone for the difference.
 */
import { estimateCostEur } from '@/lib/core/agents/budget'
import type { LlmResult } from '@/lib/core/llm/provider'

/** Credits per euro of measured provider spend. */
export const CREDITS_PER_EUR = 100

/** No completed run bills less than this. */
export const MIN_CREDITS = 1

/** Rough characters per token, used only when a provider reports no usage. */
const CHARS_PER_TOKEN = 4

export interface RunCost {
  costEur: number
  promptTokens: number
  completionTokens: number
  /** True when the token counts were inferred from length, not reported. */
  estimated: boolean
}

/**
 * Price one model call. Uses reported usage when the provider gives it and
 * falls back to a length estimate, saying which it did.
 */
export function priceCall(result: LlmResult, promptText: string): RunCost {
  if (result.usage) {
    return {
      costEur: estimateCostEur(
        result.provider,
        result.usage.promptTokens,
        result.usage.completionTokens,
      ),
      promptTokens: result.usage.promptTokens,
      completionTokens: result.usage.completionTokens,
      estimated: false,
    }
  }

  const promptTokens = Math.ceil(promptText.length / CHARS_PER_TOKEN)
  const completionTokens = Math.ceil(result.text.length / CHARS_PER_TOKEN)
  return {
    costEur: estimateCostEur(result.provider, promptTokens, completionTokens),
    promptTokens,
    completionTokens,
    estimated: true,
  }
}

/**
 * Credits to bill for a finished run.
 *
 * A run that genuinely spent nothing — the local tier, a cache hit, a request
 * aborted before any provider call — bills nothing. The floor applies to work
 * that happened, not to work that did not.
 */
export function creditsFor(costEur: number, didWork: boolean): number {
  if (!didWork) return 0
  if (costEur <= 0) return MIN_CREDITS
  return Math.max(MIN_CREDITS, Math.ceil(costEur * CREDITS_PER_EUR))
}
