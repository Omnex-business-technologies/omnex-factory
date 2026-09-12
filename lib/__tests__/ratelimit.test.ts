/**
 * The rate limiter, and the bypass this file exists to close.
 *
 * Every route that actually calls `checkRateLimit` — studio_generate,
 * studio_upload, copilot_stream, stripe_checkout — authenticates the caller
 * with Supabase first, so a verified, non-spoofable user id is sitting one
 * line above the call. `checkRateLimit` used to ignore it and key purely on
 * `x-forwarded-for` / `x-real-ip`, headers the calling client sets on its own
 * request. An authenticated attacker who cannot forge a session can trivially
 * forge a header, so the limit was bypassable by anyone willing to send a
 * fresh `x-forwarded-for` value on every request — no test caught this
 * because no test for this module existed at all.
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { NextRequest } from 'next/server'
import { checkRateLimit, rateLimitHeaders } from '@/lib/core/security/ratelimit'

function request(ip: string): NextRequest {
  return new NextRequest('http://localhost/api/studio/generate', {
    method: 'POST',
    headers: { 'x-forwarded-for': ip },
  })
}

// studio_generate: 8 requests per 60s window (see RATE_LIMITS).
const MAX = 8

describe('checkRateLimit', () => {
  // A fresh identity/IP per test avoids the shared in-memory window map
  // carrying state between tests in this file.
  let n = 0
  beforeEach(() => {
    n += 1
  })

  it('an attacker cannot bypass their own limit by rotating the header', () => {
    // The exact bypass this fix closes: same authenticated user, a BRAND NEW
    // spoofed IP on every single call. Before this fix, each call landed in
    // its own IP-keyed window and never hit the limit.
    const user = `user-rotate-${n}`
    for (let i = 0; i < MAX; i++) {
      const result = checkRateLimit(request(`10.0.${n}.${i}`), 'studio_generate', user)
      expect(result.allowed).toBe(true)
    }
    const blocked = checkRateLimit(request(`10.0.${n}.999`), 'studio_generate', user)
    expect(blocked.allowed).toBe(false)
    expect(blocked.retryAfter).toBeGreaterThan(0)
  })

  it('keys by identity, not by IP, whenever identity is available', () => {
    const user = `user-key-${n}`
    // Exhaust the limit entirely through ONE ip.
    for (let i = 0; i < MAX; i++) {
      checkRateLimit(request(`10.1.${n}.1`), 'studio_generate', user)
    }
    // A totally different IP, same identity: still blocked.
    const stillBlocked = checkRateLimit(request(`10.1.${n}.2`), 'studio_generate', user)
    expect(stillBlocked.allowed).toBe(false)
  })

  it('falls back to the header-derived id only when no identity is given', () => {
    // Two anonymous callers (no identity, the shape for a route with no auth
    // wired to it yet) get independent windows keyed by IP.
    const ipA = `10.2.${n}.1`
    const ipB = `10.2.${n}.2`
    for (let i = 0; i < MAX; i++) {
      expect(checkRateLimit(request(ipA), 'studio_generate').allowed).toBe(true)
    }
    expect(checkRateLimit(request(ipA), 'studio_generate').allowed).toBe(false)
    // A different IP is a different window and has not been touched.
    expect(checkRateLimit(request(ipB), 'studio_generate').allowed).toBe(true)
  })

  it('identity takes priority even when the header also varies', () => {
    // Passing identity means the header is never consulted at all -- proven
    // by varying BOTH together and still hitting one shared window.
    const user = `user-both-${n}`
    for (let i = 0; i < MAX - 1; i++) {
      checkRateLimit(request(`10.3.${n}.${i}`), 'studio_generate', user)
    }
    const last = checkRateLimit(request(`10.3.${n}.last`), 'studio_generate', user)
    expect(last.allowed).toBe(true)
    expect(last.remaining).toBe(0)
    const over = checkRateLimit(request(`10.3.${n}.over`), 'studio_generate', user)
    expect(over.allowed).toBe(false)
  })

  it('rateLimitHeaders reports Retry-After only when blocked', () => {
    const user = `user-headers-${n}`
    let last = checkRateLimit(request(`10.4.${n}.0`), 'studio_generate', user)
    for (let i = 1; i < MAX; i++) {
      last = checkRateLimit(request(`10.4.${n}.${i}`), 'studio_generate', user)
    }
    expect(rateLimitHeaders(last, 'studio_generate')['Retry-After']).toBeUndefined()

    const blocked = checkRateLimit(request(`10.4.${n}.over`), 'studio_generate', user)
    const headers = rateLimitHeaders(blocked, 'studio_generate')
    expect(headers['Retry-After']).toBeDefined()
    expect(Number(headers['Retry-After'])).toBeGreaterThan(0)
    expect(headers['X-RateLimit-Remaining']).toBe('0')
  })
})
