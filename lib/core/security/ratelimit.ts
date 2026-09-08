/**
 * BATCH J — Sovereign Rate Limiter
 * Sliding window rate limiter. Per-route limits.
 * Returns Retry-After header on 429. Exempts CRON_SECRET requests.
 */
import { NextRequest } from 'next/server'
import { isCronAuthorized } from '@/lib/core/cron-auth'

// In-memory sliding window (per Vercel Function instance)
const windows = new Map<string, number[]>()

export interface RateLimitConfig {
  windowMs:  number  // window size in ms
  maxReqs:   number  // max requests per window
  keyPrefix: string  // e.g. 'run', 'linkedin', 'email'
}

/**
 * Factory routes (the inherited list named routes that do not exist here).
 *
 * Generation is deliberately the tightest: credits meter the customer's
 * *balance*, this meters our *infrastructure* — a user with a big balance can
 * still not hammer the provider.
 */
export const RATE_LIMITS = {
  'studio_generate': { windowMs: 60_000, maxReqs: 8,  keyPrefix: 'gen' },
  'studio_upload':   { windowMs: 60_000, maxReqs: 20, keyPrefix: 'up'  },
  'stripe_checkout': { windowMs: 60_000, maxReqs: 10, keyPrefix: 'st'  },
  'email_send':      { windowMs: 60_000, maxReqs: 20, keyPrefix: 'em'  },
  'auth':            { windowMs: 60_000, maxReqs: 15, keyPrefix: 'au'  },
  // Streaming holds a connection open for the length of a run, so the limit is
  // on how many runs may be STARTED — a generous per-message cap would let one
  // user hold every worker slot with long-running streams nobody is reading.
  'copilot_stream':  { windowMs: 60_000, maxReqs: 12, keyPrefix: 'cp'  },
} satisfies Record<string, RateLimitConfig>

export type RateLimitRoute = keyof typeof RATE_LIMITS

export interface RateLimitResult {
  allowed:    boolean
  remaining:  number
  resetAt:    number  // Unix ms
  retryAfter: number  // seconds
}

function getClientId(request: NextRequest): string {
  return (
    request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ??
    request.headers.get('x-real-ip') ??
    'unknown'
  )
}

export function checkRateLimit(
  request: NextRequest,
  route: RateLimitRoute,
): RateLimitResult {
  // CRON_SECRET requests are exempt. Strict check via cron-auth (no hardcoded
  // fallback — the old default string is public in git history, so accepting it
  // here was an open rate-limit bypass for anyone who sent it).
  if (isCronAuthorized(request)) {
    return { allowed: true, remaining: 9999, resetAt: 0, retryAfter: 0 }
  }

  const config  = RATE_LIMITS[route]
  const clientId = getClientId(request)
  const key      = `${config.keyPrefix}:${clientId}`
  const now      = Date.now()
  const windowStart = now - config.windowMs

  // Slide window: remove old timestamps
  const timestamps = (windows.get(key) ?? []).filter(t => t > windowStart)

  const remaining = Math.max(0, config.maxReqs - timestamps.length)

  if (timestamps.length >= config.maxReqs) {
    const oldest    = timestamps[0] ?? now
    const resetAt   = oldest + config.windowMs
    const retryAfter = Math.ceil((resetAt - now) / 1000)
    return { allowed: false, remaining: 0, resetAt, retryAfter }
  }

  timestamps.push(now)
  windows.set(key, timestamps)

  return { allowed: true, remaining: remaining - 1, resetAt: now + config.windowMs, retryAfter: 0 }
}

export function rateLimitHeaders(result: RateLimitResult, route: RateLimitRoute): Record<string, string> {
  return {
    'X-RateLimit-Limit':     String(RATE_LIMITS[route].maxReqs),
    'X-RateLimit-Remaining': String(result.remaining),
    'X-RateLimit-Reset':     String(Math.ceil(result.resetAt / 1000)),
    ...(result.allowed ? {} : { 'Retry-After': String(result.retryAfter) }),
  }
}
