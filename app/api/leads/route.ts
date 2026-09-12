/**
 * POST /api/leads — the public brief form.
 *
 * Anonymous by design: a brand should be able to send an enquiry without an
 * account. The service-role client is used for the insert, so this route must do
 * its own validation — the key bypasses RLS and there is no session to lean on.
 *
 * That same anonymity is why this is the one public route in the app that had
 * no rate limit at all: every other route calling `checkRateLimit` had a
 * verified user id to key on before this one existed. There is no session
 * here, so nothing distinguishes a flood of anonymous inserts through the
 * service-role client from ordinary traffic except the caller's IP — the
 * `getClientId()` fallback `checkRateLimit` already falls back to when no
 * identity is passed, exactly the case this route is.
 */
import { NextRequest, NextResponse } from 'next/server'
import { createAdminClient } from '@/lib/core/supabase/admin'
import { checkRateLimit, rateLimitHeaders } from '@/lib/core/security/ratelimit'

interface Body {
  name?: string
  email?: string
  company?: string
  brand_site?: string
  budget?: string
  timeline?: string
  brief?: string
  /** Honeypot: a real person never fills a hidden field. */
  website?: string
}

const clean = (v: unknown, max: number): string =>
  typeof v === 'string' ? v.trim().slice(0, max) : ''

export async function POST(request: NextRequest) {
  const limit = checkRateLimit(request, 'leads')
  if (!limit.allowed) {
    return NextResponse.json(
      { error: 'Too many submissions. Please try again shortly.' },
      { status: 429, headers: rateLimitHeaders(limit, 'leads') },
    )
  }

  const body = (await request.json().catch(() => ({}))) as Body

  // Bots fill every field they find. Answer 200 so the bot believes it succeeded
  // and does not retry with a different shape, but write nothing.
  if (clean(body.website, 200)) {
    return NextResponse.json({ ok: true })
  }

  const email = clean(body.email, 200).toLowerCase()
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
    return NextResponse.json({ error: 'A valid email is required.' }, { status: 400 })
  }

  const brief = clean(body.brief, 4000)
  if (brief.length < 10) {
    return NextResponse.json({ error: 'Tell us a little about the campaign.' }, { status: 400 })
  }

  const row = {
    source: 'portfolio',
    name: clean(body.name, 200) || null,
    email,
    company: clean(body.company, 200) || null,
    brand_site: clean(body.brand_site, 300) || null,
    budget: clean(body.budget, 40) || null,
    timeline: clean(body.timeline, 40) || null,
    brief,
  }

  const supabase = createAdminClient()
  // .error must be read: this client returns failures as values rather than
  // throwing, so an unchecked insert is indistinguishable from a successful one —
  // the exact defect that silently discarded writes for seven weeks.
  const { error } = await supabase.from('leads').insert(row)
  if (error) {
    console.error('leads insert failed:', error.message)
    return NextResponse.json({ error: 'Could not save your enquiry. Please email us.' }, { status: 500 })
  }

  return NextResponse.json({ ok: true })
}
