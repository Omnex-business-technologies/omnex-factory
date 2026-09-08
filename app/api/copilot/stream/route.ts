/**
 * POST /api/copilot/stream — P8, the streaming copilot.
 *
 * Streams a run as Server-Sent Events: the shape of the run, the text it
 * produces, and the running cost, updated while it is still running.
 *
 * Order is deliberate and matches the studio route:
 *   auth → rate limit → guard the input → run under a budget → guard the
 *   output → meter and bill what was actually spent
 *
 * ## The money path, and why it was broken
 *
 * The first version of this route shipped with a cost panel that read €0.00 on
 * every real run, no `usage_events` row, no credit debit and no ceiling. Four
 * faults with one root cause: `LlmResult` never carried the provider's token
 * usage, so nothing downstream could price a call. That is fixed in
 * `lib/core/llm/provider.ts`; the rest follows from it.
 *
 * **Bounded while it runs, billed once it has.** `/api/studio/generate` charges
 * first and refunds on failure, which is right for a fixed-price unit of work.
 * A streamed run has no price until it ends, so charging a guess up front is
 * how somebody gets billed for a run they cancelled after two seconds. Here a
 * `RunBudget` caps the spend, and `metering.ts` converts what was actually
 * spent into credits at the end.
 *
 * **Metered on every terminal path, including failure and abort.** A run that
 * spent money and then failed is precisely the one an operator needs to see in
 * `usage_events`. Recording only successes is how a cost centre hides.
 *
 * ## Why the abort signal is passed through
 *
 * `req.signal` fires when the client disconnects. Without it a closed tab
 * leaves the run generating against the user's balance with nobody watching —
 * the failure `lib/core/agents/stream.ts` exists to prevent, asserted in
 * `lib/__tests__/stream.test.ts`.
 */
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/core/supabase/server'
import { checkRateLimit } from '@/lib/core/security/ratelimit'
import { guardInbound, guardOutbound, summarise } from '@/lib/core/agents/guardrails'
import { complete, hasProvider } from '@/lib/core/llm/provider'
import { Trace } from '@/lib/core/agents/trace'
import { RunBudget } from '@/lib/core/agents/budget'
import { creditsFor, priceCall } from '@/lib/core/agents/metering'
import { spendCredits, recordUsage } from '@/lib/core/billing/credits'
import { SSE_HEADERS, toSSE, type RunStep } from '@/lib/core/agents/stream'

export const dynamic = 'force-dynamic'
export const maxDuration = 120

const MODULE_ID = 'copilot'
const MAX_QUESTION = 2_000

/** Ceiling for one copilot run. Well under the studio's per-request exposure. */
const MAX_RUN_COST_EUR = 0.1

const SYSTEM_PROMPT =
  'You are the OMNEX copilot. Answer concisely. If you do not know, say so rather than guessing.'

interface CopilotBody {
  question?: string
}

export async function POST(req: NextRequest) {
  const supabase = await createClient()
  const {
    data: { user },
  } = await supabase.auth.getUser()
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const limit = checkRateLimit(req, 'copilot_stream')
  if (!limit.allowed) {
    return NextResponse.json({ error: 'Too many runs started. Try again shortly.' }, { status: 429 })
  }

  let body: CopilotBody
  try {
    body = (await req.json()) as CopilotBody
  } catch {
    return NextResponse.json({ error: 'Malformed JSON body' }, { status: 400 })
  }

  const question = (body.question ?? '').trim()
  if (question.length < 3) {
    return NextResponse.json({ error: 'Ask a question (min 3 characters).' }, { status: 400 })
  }
  if (question.length > MAX_QUESTION) {
    return NextResponse.json({ error: `Question is too long (max ${MAX_QUESTION}).` }, { status: 400 })
  }

  // Guarded BEFORE the stream opens. A blocked prompt should be an ordinary 400
  // the client can render, not a stream that opens and immediately closes.
  const inbound = guardInbound(question)
  if (!inbound.ok) {
    return NextResponse.json({ error: summarise(inbound) }, { status: 400 })
  }

  const trace = new Trace(MODULE_ID, { userId: user.id.slice(0, 8) })
  const budget = new RunBudget({ maxCostEur: MAX_RUN_COST_EUR, maxPasses: 4 })

  // What actually happened, closed over so the terminal handler can bill it.
  let spentEur = 0
  let calledProvider = false
  let estimated = false

  const steps: RunStep[] = [
    {
      name: 'guard input',
      kind: 'guard',
      run: async () => ({ text: '' }),
    },
    {
      name: 'answer',
      kind: 'llm',
      run: async (signal) => {
        if (signal.aborted) return {}

        const headroom = budget.check()
        if (!headroom.ok) {
          // A stated reason beats being killed by the platform without one.
          throw new Error(headroom.message ?? `run budget exhausted (${headroom.reason})`)
        }

        if (!hasProvider()) {
          // Local-first, same rule as P7: a missing credential is a working
          // degraded path, not a 500, and it genuinely costs nothing.
          return {
            text:
              'No language-model provider is configured, so this run has no model to answer with. ' +
              'Set one of the provider keys, or point the stack at a local Ollama instance.',
            costEur: 0,
            tokens: 0,
            provider: 'none',
          }
        }

        const result = await complete(
          [
            { role: 'system', content: SYSTEM_PROMPT },
            { role: 'user', content: question },
          ],
          { maxTokens: 800, temperature: 0.2, taskProfile: 'fast' },
        )

        const cost = priceCall(result, `${SYSTEM_PROMPT}\n${question}`)
        budget.record({ tokens: cost.promptTokens + cost.completionTokens, costEur: cost.costEur })
        spentEur += cost.costEur
        calledProvider = true
        estimated = estimated || cost.estimated

        // `display` rather than `publish`: this goes to the person who asked.
        const outbound = guardOutbound(result.text, { channel: 'display' })
        return {
          text: outbound.ok ? result.text : outbound.redacted,
          costEur: cost.costEur,
          tokens: cost.promptTokens + cost.completionTokens,
          provider: result.provider,
          model: result.model,
        }
      },
    },
  ]

  const stream = toSSE(trace, steps, {
    signal: req.signal,
    // Billed on EVERY terminal path. A run that spent money and then failed or
    // was cancelled is exactly the one that must not disappear from the ledger.
    onSettled: async (outcome) => {
      const credits = creditsFor(spentEur, calledProvider)
      if (credits > 0) {
        await spendCredits(user.id, credits, MODULE_ID).catch(() => undefined)
      }
      await recordUsage({
        userId: user.id,
        moduleId: MODULE_ID,
        action: 'stream',
        credits,
        ok: outcome.reason === 'complete',
        meta: {
          reason: outcome.reason,
          costEur: spentEur,
          tokens: outcome.tokens,
          durationMs: outcome.durationMs,
          // So a dashboard can never present a guess as a measurement.
          estimated,
        },
      })
    },
  })

  return new Response(stream, { headers: SSE_HEADERS })
}
