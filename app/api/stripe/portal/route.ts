import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'
import { createClient } from '@/lib/core/supabase/server'
import { createAdminClient } from '@/lib/core/supabase/admin'
import { cleanKey } from '@/lib/core/supabase/env'
import { checkRateLimit } from '@/lib/core/security/ratelimit'

export const dynamic = 'force-dynamic'

// Lets a subscriber change or cancel their plan without us building billing UI.
export async function POST(req: NextRequest) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  // Every other Stripe/billing route this repository has is rate-limited by
  // user id; this one was not, for no documented reason, and it calls the
  // same paid external API.
  const limit = checkRateLimit(req, 'stripe_portal', user.id)
  if (!limit.allowed) return NextResponse.json({ error: 'Too many attempts.' }, { status: 429 })

  const key = cleanKey(process.env.STRIPE_SECRET_KEY)
  if (!key) return NextResponse.json({ error: 'Billing is not configured yet.' }, { status: 503 })

  const admin = createAdminClient()
  const { data: profile } = await admin.from('profiles').select('stripe_customer_id').eq('id', user.id).maybeSingle()
  const customerId = profile?.stripe_customer_id as string | null | undefined
  if (!customerId) return NextResponse.json({ error: 'No subscription found.' }, { status: 404 })

  const stripe = new Stripe(key, { maxNetworkRetries: 2 })
  const session = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: `${req.nextUrl.origin}/studio`,
  })
  return NextResponse.json({ url: session.url })
}
