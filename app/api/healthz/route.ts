/**
 * GET /api/healthz — liveness only. Answers 200 the instant the process can
 * run a route handler at all, with no dependency check of any kind.
 *
 * Kept deliberately separate from `/api/readyz`: a platform's restart policy
 * should act on "is the process alive" alone, never on "is Stripe configured
 * yet" — conflating the two turns a missing environment variable into a
 * crash-loop instead of a visible, fixable 503.
 */
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({ ok: true })
}
