/**
 * BATCH J — Sovereign Rate Limiter
 * Sliding window rate limiter. Per-route limits.
 * Returns Retry-After header on 429.
 *
 * ## No CRON_SECRET exemption, on purpose
 *
 * An earlier version exempted any request carrying a valid `CRON_SECRET`
 * bearer token from every limit below, inherited from the same donor
 * codebase `RATE_LIMITS`' own comment already names ("the inherited list
 * named routes that do not exist here"). Nothing in THIS repository sends
 * that header to `studio_generate`, `studio_upload`, `copilot_stream` or
 * `stripe_checkout` — there is no `app/api/cron/*` route, no `vercel.json`
 * `crons` entry, nothing scheduled that would ever need to call a
 * customer-facing route as an exempted caller. The exemption's only live
 * effect was downside: if `CRON_SECRET` ever leaked, any one of those four
 * routes could be called without limit — undoing every protection this file
 * provides, including the identity-keying immediately below, for whoever
 * holds it. A bypass with no legitimate caller and a real leak scenario is
 * pure liability; removed rather than kept "just in case." If a genuine
 * scheduled job needs to call one of these routes without the normal
 * per-user limit, that is a reason to build the cron route and exempt IT
 * specifically, not to leave a blanket exemption sitting in front of every
 * customer-facing one on the chance it is useful someday.
 *
 * ## Identity: prefer the verified user id, never trust the header alone
 *
 * `getClientId()` reads `x-forwarded-for` / `x-real-ip` — headers a client
 * sets on the request it sends. Whether the value a route ends up seeing is
 * trustworthy depends entirely on what sits in front of this process: a
 * platform edge that overwrites the header before forwarding makes it safe,
 * a bare reverse proxy that blindly forwards it does not, and this codebase
 * documents more than one deployment shape (`DOCKER.md` + `compose.yaml`,
 * a self-hosted target with no such edge). Every route this repository
 * actually wires to `checkRateLimit` — `studio_generate`, `studio_upload`,
 * `copilot_stream`, `stripe_checkout` — already authenticates the caller
 * with Supabase before checking the limit, so all four had a non-spoofable
 * identity sitting unused one line above the call. `checkRateLimit`'s
 * optional `identity` parameter is that user id: when passed, it is the key,
 * full stop, and the header is never consulted — an attacker who cannot
 * forge a verified session cannot rotate their way around their own limit
 * by rewriting a header on every request. `getClientId()` remains the
 * fallback for the two configured routes (`email_send`, `auth`) nothing in
 * this repository calls yet, and inherits whatever trust the deployment
 * platform actually provides for it — a claim this file makes about itself,
 * not about Vercel's or any other host's edge, which this environment
 * cannot verify from here.
 */
import { NextRequest } from 'next/server'

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
  'stripe_portal':   { windowMs: 60_000, maxReqs: 10, keyPrefix: 'sp'  },
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
  /** The verified caller, when the route has one — see the module docstring
   * on why this outranks any header-derived id whenever it is available. */
  identity?: string,
): RateLimitResult {
  const config  = RATE_LIMITS[route]
  const clientId = identity || getClientId(request)
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
