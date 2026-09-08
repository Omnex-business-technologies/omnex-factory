/**
 * P8 — streaming a run to a browser, with what it cost attached as it happens.
 *
 * The scan in `intel/` found that the fastest-growing project in the whole
 * agent ecosystem is a run visualiser: `patoles/agent-flow`, +64.1% over 82
 * days. It renders the SHAPE of a run — which step called what, in what order.
 * What it does not render is what any of it cost, and neither does anything
 * else in that scan: `citations`, `cost_optimization` and `observability` were
 * claimed by almost none of the projects with enough text to judge.
 *
 * `Trace` (lib/core/agents/trace.ts) already carries `costEur` per span. So the
 * only missing piece is a transport, and the product is the combination: a live
 * view where the expensive branch is visibly expensive WHILE it is still
 * running, rather than a bill at the end of the month.
 *
 * ## Four things a streaming endpoint gets wrong, handled here
 *
 * **A closed tab must stop the work.** This is the expensive one. HTTP
 * streaming does not notify the server that anyone is still reading; if nobody
 * wires the abort signal, a user who closes the tab leaves a run generating
 * tokens against their own balance with no one to show them to. `runEvents()`
 * takes an `AbortSignal` and checks it between steps, and `cancel()` on the
 * stream fires it — so a disconnect stops the spend rather than merely stopping
 * the display.
 *
 * **A terminal event is always emitted.** If a run throws, the client must be
 * told, or the UI spins forever on a request that ended a minute ago. Every
 * exit path here emits exactly one `done` — success, failure or abort — and the
 * test suite asserts it on all three.
 *
 * **Idle streams get killed by proxies.** A long tool call with no output looks
 * identical to a dead connection to every intermediary between here and the
 * browser. A comment heartbeat keeps it open and costs nothing.
 *
 * **Events carry no prompts and no customer data.** They carry span records,
 * whose `attrs` are already documented as "small, non-sensitive facts". A
 * streaming endpoint is the easiest place in a system to leak a prompt into a
 * browser log, so the payload is built from the span record rather than from
 * whatever the caller happened to have in scope.
 *
 * The wire format is Server-Sent Events, chosen over the Vercel AI SDK's client
 * runtime because it needs no dependency: this repository's rule is that the
 * core works on a bare install, and SSE is what the AI SDK is transporting
 * underneath in any case. A client written against either can read this.
 */
import type { SpanRecord } from '@/lib/core/agents/trace'
import { Trace } from '@/lib/core/agents/trace'

/** Milliseconds of silence before a comment frame is sent to hold the connection. */
export const HEARTBEAT_MS = 15_000

export type CopilotEvent =
  /** A chunk of assistant text. The only event carrying model output. */
  | { type: 'token'; text: string }
  /** A span opened — the run's shape, as it happens. */
  | { type: 'span'; span: SpanRecord }
  /** Running total. Emitted whenever it changes, so cost is visible mid-run. */
  | { type: 'cost'; costEur: number; tokens: number }
  /** Terminal. Exactly one of these is emitted, on every path. */
  | { type: 'done'; reason: 'complete' | 'error' | 'aborted'; costEur: number; tokens: number; durationMs: number; error?: string }

/** SSE framing. Named events so a client can `addEventListener` per type. */
export function encodeEvent(event: CopilotEvent): string {
  return `event: ${event.type}\ndata: ${JSON.stringify(event)}\n\n`
}

/** A comment frame — ignored by EventSource, enough to keep a proxy from closing. */
export const heartbeat = (): string => `: keep-alive\n\n`

export interface RunStep {
  name: string
  kind: SpanRecord['kind']
  /**
   * Does the work and returns any text to stream. Receives an AbortSignal so a
   * step that calls a provider can pass it through rather than running to
   * completion after the reader has gone.
   */
  run: (signal: AbortSignal) => Promise<{ text?: string; costEur?: number; tokens?: number; provider?: string; model?: string }>
}

export interface StreamOptions {
  /** Fires when the client disconnects. Steps must honour it. */
  signal?: AbortSignal
  /** Injected so tests do not wait real seconds. */
  now?: () => number
}

/**
 * Run steps in order, emitting events. Transport-agnostic and synchronous to
 * reason about: everything a client sees is produced here, and `toSSE` only
 * frames it. That split is what makes the disconnect behaviour testable without
 * standing up a server.
 */
export async function* runEvents(
  trace: Trace,
  steps: RunStep[],
  options: StreamOptions = {},
): AsyncGenerator<CopilotEvent> {
  const signal = options.signal
  const now = options.now ?? Date.now
  const startedAt = now()
  let aborted = false
  let failure: string | undefined

  try {
    for (const step of steps) {
      // Checked BEFORE the step, not after: the point is not to start work
      // nobody is waiting for.
      if (signal?.aborted) {
        aborted = true
        break
      }

      const span = trace.root.child(step.name, step.kind)
      yield { type: 'span', span: span.record }

      try {
        const result = await step.run(signal ?? new AbortController().signal)
        span.set({
          ...(result.costEur !== undefined ? { costEur: result.costEur } : {}),
          ...(result.tokens !== undefined ? { tokens: { completion: result.tokens } } : {}),
          ...(result.provider ? { provider: result.provider } : {}),
          ...(result.model ? { model: result.model } : {}),
        })
        span.end('ok')

        if (result.text) yield { type: 'token', text: result.text }
        yield { type: 'span', span: span.record }

        const totals = trace.totals()
        yield { type: 'cost', costEur: totals.costEur, tokens: totals.tokens }
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error)
        span.end('error', message)
        yield { type: 'span', span: span.record }
        failure = message
        break
      }
    }
  } finally {
    // `finally` rather than after the loop: a generator abandoned by its
    // consumer still runs this, so the trace is closed even when nobody is
    // listening any more.
    trace.root.end(failure ? 'error' : 'ok', failure)
  }

  const totals = trace.totals()
  yield {
    type: 'done',
    reason: aborted ? 'aborted' : failure ? 'error' : 'complete',
    costEur: totals.costEur,
    tokens: totals.tokens,
    durationMs: now() - startedAt,
    ...(failure ? { error: failure } : {}),
  }
}

/**
 * Wrap the event stream in an SSE `ReadableStream`.
 *
 * `cancel()` is the important half. The browser calls it when the reader goes
 * away, and it aborts the controller the steps are watching — which is what
 * turns "the user closed the tab" into "the run stopped" rather than "the run
 * continued invisibly and billed them for it".
 */
export interface SettledOutcome {
  reason: 'complete' | 'error' | 'aborted'
  costEur: number
  tokens: number
  durationMs: number
  error?: string
}

export function toSSE(
  trace: Trace,
  steps: RunStep[],
  options: {
    signal?: AbortSignal
    heartbeatMs?: number
    /**
     * Called exactly once, on every terminal path — success, failure and
     * abort alike. This is where metering belongs: a run that spent money and
     * then failed is precisely the one that must not vanish from the ledger,
     * and a run the user cancelled still spent whatever it spent before
     * stopping.
     *
     * Failures here are swallowed. Billing that throws must not also break the
     * response the customer is reading; the alternative is a stream that dies
     * at the last frame because an analytics insert timed out.
     */
    onSettled?: (outcome: SettledOutcome) => void | Promise<void>
  } = {},
): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder()
  const controller = new AbortController()
  if (options.signal) {
    if (options.signal.aborted) controller.abort()
    else options.signal.addEventListener('abort', () => controller.abort(), { once: true })
  }

  let timer: ReturnType<typeof setInterval> | undefined

  return new ReadableStream<Uint8Array>({
    async start(stream) {
      const beat = options.heartbeatMs ?? HEARTBEAT_MS
      if (beat > 0) {
        timer = setInterval(() => {
          try {
            stream.enqueue(encoder.encode(heartbeat()))
          } catch {
            // Stream already closed — nothing to keep alive.
          }
        }, beat)
      }

      // Captured from the terminal event so `onSettled` reports what the
      // client was actually told, rather than re-deriving it and risking a
      // ledger that disagrees with the receipt on screen.
      let settled: SettledOutcome | undefined

      try {
        for await (const event of runEvents(trace, steps, { signal: controller.signal })) {
          if (event.type === 'done') {
            settled = {
              reason: event.reason,
              costEur: event.costEur,
              tokens: event.tokens,
              durationMs: event.durationMs,
              ...(event.error ? { error: event.error } : {}),
            }
          }
          stream.enqueue(encoder.encode(encodeEvent(event)))
        }
      } catch (error) {
        // The generator itself failed, which the per-step handler could not
        // catch. The client still gets a terminal event rather than a hang.
        const message = error instanceof Error ? error.message : String(error)
        const totals = trace.totals()
        stream.enqueue(
          encoder.encode(
            encodeEvent({
              type: 'done',
              reason: 'error',
              costEur: totals.costEur,
              tokens: totals.tokens,
              durationMs: totals.durationMs,
              error: message,
            }),
          ),
        )
        settled = {
          reason: 'error',
          costEur: totals.costEur,
          tokens: totals.tokens,
          durationMs: totals.durationMs,
          error: message,
        }
      } finally {
        if (timer) clearInterval(timer)
        if (options.onSettled) {
          // Awaited before closing so the ledger write is not racing the
          // response ending, and swallowed so a billing failure cannot break
          // the answer the customer is reading.
          const totals = trace.totals()
          try {
            await options.onSettled(
              settled ?? {
                reason: 'aborted',
                costEur: totals.costEur,
                tokens: totals.tokens,
                durationMs: totals.durationMs,
              },
            )
          } catch {
            // Metering must never break a customer request.
          }
        }
        stream.close()
      }
    },
    cancel() {
      if (timer) clearInterval(timer)
      controller.abort()
    },
  })
}

/** Headers an SSE response needs. `no-transform` stops proxies buffering it flat. */
export const SSE_HEADERS = {
  'Content-Type': 'text/event-stream; charset=utf-8',
  'Cache-Control': 'no-cache, no-transform',
  Connection: 'keep-alive',
  'X-Accel-Buffering': 'no',
} as const

/** Convenience for a route handler: a Trace plus a stream, wired to the request. */
export function streamRun(name: string, steps: RunStep[], signal?: AbortSignal): Response {
  const trace = new Trace(name)
  return new Response(toSSE(trace, steps, signal ? { signal } : {}), { headers: SSE_HEADERS })
}
