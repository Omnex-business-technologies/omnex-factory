'use client'

/**
 * P8 — the streaming copilot UI.
 *
 * Three panes: the answer as it arrives, the run's shape as it happens, and the
 * cost as it accrues. The third is the one that does not exist elsewhere — the
 * ecosystem scan in `intel/` found the fastest-growing project in the category
 * is a run visualiser that shows shape without cost, and that almost nothing in
 * the signal set advertises cost tracking at all.
 *
 * Reading the stream by hand rather than through a client SDK is deliberate:
 * `fetch` + `ReadableStream` is a dozen lines, works with the SSE the server
 * already speaks, and keeps the promise that this repository installs with no
 * extra dependency. It also means `stop` is a real `AbortController` — the
 * button cancels the request, which the server turns into a cancelled run.
 */

import { useCallback, useRef, useState } from 'react'

interface SpanView {
  id: string
  name: string
  kind: string
  status: 'running' | 'ok' | 'error'
  durationMs?: number
  costEur?: number
  provider?: string
  error?: string
}

type Phase = 'idle' | 'streaming' | 'done' | 'error' | 'aborted'

const money = (eur: number) => (eur === 0 ? '€0.00' : eur < 0.01 ? `€${eur.toFixed(4)}` : `€${eur.toFixed(2)}`)

export default function CopilotPage() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [spans, setSpans] = useState<SpanView[]>([])
  const [cost, setCost] = useState(0)
  const [tokens, setTokens] = useState(0)
  const [phase, setPhase] = useState<Phase>('idle')
  const [error, setError] = useState<string | null>(null)
  const controller = useRef<AbortController | null>(null)

  const stop = useCallback(() => {
    controller.current?.abort()
  }, [])

  const send = useCallback(async () => {
    const asked = question.trim()
    if (asked.length < 3 || phase === 'streaming') return

    setAnswer('')
    setSpans([])
    setCost(0)
    setTokens(0)
    setError(null)
    setPhase('streaming')

    const abort = new AbortController()
    controller.current = abort

    try {
      const response = await fetch('/api/copilot/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: asked }),
        signal: abort.signal,
      })

      if (!response.ok || !response.body) {
        const detail = await response.json().catch(() => ({ error: 'Request failed' }))
        setError(String(detail.error ?? 'Request failed'))
        setPhase('error')
        return
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      for (;;) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        // SSE frames are separated by a blank line. Anything after the last
        // separator is a partial frame and stays in the buffer — parsing it
        // early is how a streamed UI shows half a JSON object.
        const frames = buffer.split('\n\n')
        buffer = frames.pop() ?? ''

        for (const frame of frames) {
          const line = frame.split('\n').find((l) => l.startsWith('data: '))
          if (!line) continue // comment frame: a heartbeat
          let event: Record<string, unknown>
          try {
            event = JSON.parse(line.slice(6))
          } catch {
            continue
          }

          if (event.type === 'token') {
            setAnswer((prev) => prev + String(event.text ?? ''))
          } else if (event.type === 'span') {
            const span = event.span as SpanView
            setSpans((prev) => {
              const next = prev.filter((s) => s.id !== span.id)
              return [...next, span].sort((a, b) => a.id.localeCompare(b.id))
            })
          } else if (event.type === 'cost') {
            setCost(Number(event.costEur ?? 0))
            setTokens(Number(event.tokens ?? 0))
          } else if (event.type === 'done') {
            setCost(Number(event.costEur ?? 0))
            setTokens(Number(event.tokens ?? 0))
            setPhase(event.reason === 'complete' ? 'done' : (event.reason as Phase))
            if (event.error) setError(String(event.error))
          }
        }
      }
      setPhase((prev) => (prev === 'streaming' ? 'done' : prev))
    } catch (e) {
      // An aborted fetch is the user pressing stop, not a failure.
      if (e instanceof DOMException && e.name === 'AbortError') setPhase('aborted')
      else {
        setError(e instanceof Error ? e.message : String(e))
        setPhase('error')
      }
    } finally {
      controller.current = null
    }
  }, [question, phase])

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <header className="mb-8">
        <h1 className="text-2xl font-semibold">Copilot</h1>
        <p className="mt-1 text-sm text-neutral-500">
          Every step of the run, and what it cost, while it is still running.
        </p>
      </header>

      <div className="flex gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              void send()
            }
          }}
          placeholder="Ask something…"
          className="flex-1 rounded-lg border border-neutral-300 px-4 py-2 text-sm outline-none focus:border-neutral-900 dark:border-neutral-700 dark:bg-neutral-900 dark:focus:border-neutral-300"
          aria-label="Question"
        />
        {phase === 'streaming' ? (
          <button
            onClick={stop}
            className="rounded-lg bg-neutral-200 px-4 py-2 text-sm font-medium dark:bg-neutral-800"
          >
            Stop
          </button>
        ) : (
          <button
            onClick={() => void send()}
            disabled={question.trim().length < 3}
            className="rounded-lg bg-neutral-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-40 dark:bg-white dark:text-neutral-900"
          >
            Ask
          </button>
        )}
      </div>

      <section className="mt-6 grid gap-6 md:grid-cols-[1fr_20rem]">
        <div>
          <div className="min-h-[8rem] whitespace-pre-wrap rounded-lg border border-neutral-200 p-4 text-sm leading-relaxed dark:border-neutral-800">
            {answer || (
              <span className="text-neutral-400">
                {phase === 'streaming' ? 'Working…' : 'The answer will stream in here.'}
              </span>
            )}
          </div>
          {error && (
            <p className="mt-3 rounded-lg bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
              {error}
            </p>
          )}
        </div>

        <aside className="space-y-4">
          <div className="rounded-lg border border-neutral-200 p-4 dark:border-neutral-800">
            <div className="text-xs uppercase tracking-wide text-neutral-500">Cost so far</div>
            <div className="mt-1 text-2xl font-semibold tabular-nums">{money(cost)}</div>
            <div className="mt-1 text-xs text-neutral-500">{tokens.toLocaleString()} tokens</div>
          </div>

          <div className="rounded-lg border border-neutral-200 p-4 dark:border-neutral-800">
            <div className="mb-2 text-xs uppercase tracking-wide text-neutral-500">Run</div>
            {spans.length === 0 ? (
              <p className="text-xs text-neutral-400">No steps yet.</p>
            ) : (
              <ol className="space-y-2">
                {spans.map((span) => (
                  <li key={span.id} className="flex items-baseline justify-between gap-2 text-xs">
                    <span className="flex items-center gap-1.5">
                      <span
                        aria-hidden
                        className={
                          span.status === 'error'
                            ? 'inline-block h-1.5 w-1.5 rounded-full bg-red-500'
                            : span.status === 'running'
                              ? 'inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-amber-500'
                              : 'inline-block h-1.5 w-1.5 rounded-full bg-emerald-500'
                        }
                      />
                      <span className={span.status === 'error' ? 'text-red-600 dark:text-red-400' : ''}>
                        {span.name}
                      </span>
                    </span>
                    <span className="tabular-nums text-neutral-500">
                      {span.costEur ? money(span.costEur) : span.durationMs !== undefined ? `${span.durationMs}ms` : '…'}
                    </span>
                  </li>
                ))}
              </ol>
            )}
            {phase !== 'idle' && phase !== 'streaming' && (
              <p className="mt-3 border-t border-neutral-200 pt-2 text-xs text-neutral-500 dark:border-neutral-800">
                {phase === 'aborted' ? 'Stopped — the run was cancelled on the server too.' : `Finished (${phase}).`}
              </p>
            )}
          </div>
        </aside>
      </section>
    </main>
  )
}
