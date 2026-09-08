/**
 * P8 streaming — the properties that decide whether it is safe to ship.
 *
 * A streaming endpoint fails in ways that are invisible from the browser: the
 * tab closes and the work carries on, or the run dies and the spinner never
 * stops. Neither shows up in a screenshot, so both are asserted here.
 */
import { describe, it, expect } from 'vitest'
import { Trace } from '@/lib/core/agents/trace'
import {
  encodeEvent,
  heartbeat,
  runEvents,
  toSSE,
  type CopilotEvent,
  type RunStep,
} from '@/lib/core/agents/stream'

const collect = async (
  steps: RunStep[],
  signal?: AbortSignal,
): Promise<{ events: CopilotEvent[]; trace: Trace }> => {
  const trace = new Trace('test-run')
  const events: CopilotEvent[] = []
  for await (const event of runEvents(trace, steps, signal ? { signal } : {})) events.push(event)
  return { events, trace }
}

const step = (name: string, out: Partial<Awaited<ReturnType<RunStep['run']>>> = {}): RunStep => ({
  name,
  kind: 'llm',
  run: async () => ({ text: `${name} output`, costEur: 0.01, tokens: 100, ...out }),
})

const readAll = async (stream: ReadableStream<Uint8Array>): Promise<string> => {
  const reader = stream.getReader()
  const decoder = new TextDecoder()
  let out = ''
  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    out += decoder.decode(value, { stream: true })
  }
  return out
}

describe('copilot stream', () => {
  it('emits exactly one terminal event when every step succeeds', async () => {
    const { events } = await collect([step('plan'), step('answer')])

    const terminal = events.filter((e) => e.type === 'done')
    expect(terminal).toHaveLength(1)
    expect(terminal[0]).toMatchObject({ type: 'done', reason: 'complete' })
  })

  it('emits exactly one terminal event when a step throws', async () => {
    // The spinner-forever bug. A run that dies must still tell the client.
    const boom: RunStep = {
      name: 'explode',
      kind: 'tool',
      run: async () => {
        throw new Error('provider refused')
      },
    }
    const { events } = await collect([step('plan'), boom, step('never runs')])

    const terminal = events.filter((e) => e.type === 'done')
    expect(terminal).toHaveLength(1)
    expect(terminal[0]).toMatchObject({ reason: 'error', error: 'provider refused' })
  })

  it('stops running steps once the client has disconnected', async () => {
    // The expensive bug: a closed tab that keeps generating tokens the user is
    // paying for and nobody will ever see.
    const controller = new AbortController()
    const ran: string[] = []
    const track = (name: string): RunStep => ({
      name,
      kind: 'llm',
      run: async () => {
        ran.push(name)
        controller.abort() // the reader goes away during the first step
        return { text: 'x', costEur: 0.01, tokens: 10 }
      },
    })

    const { events } = await collect([track('first'), track('second')], controller.signal)

    expect(ran).toEqual(['first'])
    expect(events.at(-1)).toMatchObject({ type: 'done', reason: 'aborted' })
  })

  it('does not start any work when the request is already aborted', async () => {
    const controller = new AbortController()
    controller.abort()
    const ran: string[] = []
    const track: RunStep = {
      name: 'work',
      kind: 'llm',
      run: async () => {
        ran.push('work')
        return {}
      },
    }

    const { events } = await collect([track], controller.signal)

    expect(ran).toEqual([])
    expect(events).toHaveLength(1)
    expect(events[0]).toMatchObject({ type: 'done', reason: 'aborted' })
  })

  it('reports cost as it accrues, not only at the end', async () => {
    // The whole point of the feature. A total that only appears when the run
    // finishes is a receipt; a total that moves while it runs is a control.
    const { events } = await collect([
      step('cheap', { costEur: 0.01 }),
      step('expensive', { costEur: 0.5 }),
    ])

    const costs = events.filter((e) => e.type === 'cost').map((e) => (e as { costEur: number }).costEur)
    expect(costs).toEqual([0.01, 0.51])

    const done = events.at(-1) as { costEur: number }
    expect(done.costEur).toBe(0.51)
  })

  it('closes the run span even when the consumer abandons the generator', async () => {
    // A browser that stops reading leaves the generator suspended. `finally`
    // still runs, so the trace does not stay open forever.
    const trace = new Trace('abandoned')
    const generator = runEvents(trace, [step('one'), step('two')])
    await generator.next()
    await generator.return(undefined as never)

    expect(trace.root.record.status).not.toBe('running')
    expect(trace.root.record.endedAt).toBeDefined()
  })

  it('carries the failing span in the trace so the UI can point at it', async () => {
    const boom: RunStep = {
      name: 'retrieve',
      kind: 'retrieval',
      run: async () => {
        throw new Error('index unavailable')
      },
    }
    const { trace } = await collect([step('plan'), boom])

    const path = trace.failurePath()
    expect(path.at(-1)?.name).toBe('retrieve')
    expect(path.at(-1)?.error).toBe('index unavailable')
  })

  it('never puts prompt text in a span event', async () => {
    // Span events are the run's shape and its cost. Model output travels only
    // in `token` events, so a UI that renders spans cannot leak a prompt.
    const { events } = await collect([step('answer', { text: 'SECRET CUSTOMER DATA' })])

    const spanEvents = events.filter((e) => e.type === 'span')
    expect(spanEvents.length).toBeGreaterThan(0)
    for (const event of spanEvents) {
      expect(JSON.stringify(event)).not.toContain('SECRET CUSTOMER DATA')
    }
    expect(events.some((e) => e.type === 'token')).toBe(true)
  })
})

describe('SSE framing', () => {
  it('frames each event with its type so a client can subscribe per type', () => {
    const frame = encodeEvent({ type: 'token', text: 'hello' })

    expect(frame.startsWith('event: token\n')).toBe(true)
    expect(frame.endsWith('\n\n')).toBe(true)
    expect(JSON.parse(frame.split('data: ')[1]!.trim())).toEqual({ type: 'token', text: 'hello' })
  })

  it('escapes newlines in payloads so one event cannot become two frames', () => {
    // A raw newline inside a data line ends the frame early and the rest is
    // parsed as a new event. JSON encoding is what prevents it.
    const frame = encodeEvent({ type: 'token', text: 'line one\nline two' })

    expect(frame.split('\n\n')).toHaveLength(2)
    expect(frame).toContain('line one\\nline two')
  })

  it('sends heartbeats as comments, which EventSource ignores', () => {
    expect(heartbeat().startsWith(':')).toBe(true)
    expect(heartbeat().endsWith('\n\n')).toBe(true)
  })

  it('produces a readable SSE body ending in a done frame', async () => {
    const trace = new Trace('sse')
    const body = await readAll(toSSE(trace, [step('one')], { heartbeatMs: 0 }))

    expect(body).toContain('event: span')
    expect(body).toContain('event: token')
    expect(body).toContain('event: cost')
    expect(body.trimEnd().endsWith('}')).toBe(true)
    expect(body).toContain('"reason":"complete"')
  })

  it('cancelling the response body aborts the run', async () => {
    // What actually happens when a user closes the tab.
    const ran: string[] = []
    const slow = (name: string): RunStep => ({
      name,
      kind: 'llm',
      run: async () => {
        ran.push(name)
        await new Promise((resolve) => setTimeout(resolve, 5))
        return { text: name, costEur: 0.01, tokens: 1 }
      },
    })

    const trace = new Trace('cancelled')
    const stream = toSSE(trace, [slow('a'), slow('b'), slow('c')], { heartbeatMs: 0 })
    const reader = stream.getReader()
    await reader.read()
    await reader.cancel()
    await new Promise((resolve) => setTimeout(resolve, 30))

    expect(ran.length).toBeLessThan(3)
  })
})
