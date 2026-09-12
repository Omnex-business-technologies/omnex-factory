/**
 * POST /api/leads — this route's first test file.
 *
 * Anonymous by design (a brand can send an enquiry with no account), which is
 * exactly why it had no rate limit at all before this round: every other
 * route wired to `checkRateLimit` had a verified user id to key on, and this
 * one genuinely does not. Its insert also runs through the service-role
 * client — bypasses RLS by design, since there is no session to lean on —
 * so an unlimited anonymous caller could flood real database writes through
 * it with nothing else in front of that path.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { NextRequest } from 'next/server'

const insert = vi.fn()
vi.mock('@/lib/core/supabase/admin', () => ({
  createAdminClient: () => ({
    from: () => ({ insert: (...args: unknown[]) => insert(...args) }),
  }),
}))

const { POST } = await import('@/app/api/leads/route')

const LEADS_MAX = 5 // see RATE_LIMITS['leads']

function request(body: unknown, ip: string): NextRequest {
  return new NextRequest('http://localhost/api/leads', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-forwarded-for': ip },
    body: JSON.stringify(body),
  })
}

const validBody = { email: 'brand@example.com', brief: 'We need a full product campaign for launch.' }

describe('POST /api/leads', () => {
  beforeEach(() => {
    insert.mockReset().mockResolvedValue({ error: null })
  })

  it('is rate-limited by IP -- the one public route with no session to key on instead', async () => {
    const ip = '10.9.0.1'
    for (let i = 0; i < LEADS_MAX; i++) {
      const response = await POST(request(validBody, ip))
      expect(response.status).toBe(200)
    }
    const blocked = await POST(request(validBody, ip))
    expect(blocked.status).toBe(429)
    expect(blocked.headers.get('Retry-After')).not.toBeNull()
    // Still only the LEADS_MAX successful calls above ever reached storage.
    expect(insert).toHaveBeenCalledTimes(LEADS_MAX)
  })

  it('a different IP has its own, untouched window', async () => {
    const ip = '10.9.1.1'
    for (let i = 0; i < LEADS_MAX; i++) {
      await POST(request(validBody, ip))
    }
    const otherIp = await POST(request(validBody, '10.9.2.0'))
    expect(otherIp.status).toBe(200)
  })

  it('answers 200 and writes nothing when the honeypot field is filled', async () => {
    const response = await POST(request({ ...validBody, website: 'http://spam.example' }, '10.9.3.0'))
    expect(response.status).toBe(200)
    expect(insert).not.toHaveBeenCalled()
  })

  it('refuses an invalid email before touching storage', async () => {
    const response = await POST(request({ ...validBody, email: 'not-an-email' }, '10.9.4.0'))
    expect(response.status).toBe(400)
    expect(insert).not.toHaveBeenCalled()
  })

  it('refuses a brief that is too short before touching storage', async () => {
    const response = await POST(request({ ...validBody, brief: 'too short' }, '10.9.5.0'))
    expect(response.status).toBe(400)
    expect(insert).not.toHaveBeenCalled()
  })

  it('inserts the cleaned row and answers 200 on a valid submission', async () => {
    const response = await POST(
      request({ ...validBody, name: '  Brand Co  ', budget: '10k-25k' }, '10.9.6.0'),
    )
    expect(response.status).toBe(200)
    expect(insert).toHaveBeenCalledTimes(1)
    const [row] = insert.mock.calls[0] as [Record<string, unknown>]
    expect(row).toMatchObject({ source: 'portfolio', name: 'Brand Co', email: 'brand@example.com', budget: '10k-25k' })
  })

  it('answers 500 when the insert itself fails -- the error is read, not discarded', async () => {
    insert.mockResolvedValue({ error: { message: 'db unavailable' } })
    const response = await POST(request(validBody, '10.9.7.0'))
    expect(response.status).toBe(500)
  })
})
