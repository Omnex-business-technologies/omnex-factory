/**
 * POST /api/stripe/checkout — start a subscription.
 *
 * The Stripe customer id is stored on the profile so renewals, the billing
 * portal and the webhook all resolve back to the same user. `client_reference_id`
 * carries our user id as a second, independent link — a webhook that arrives
 * before the profile write still knows who paid.
 */
import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'
import { createClient } from '@/lib/core/supabase/server'
import { createAdminClient } from '@/lib/core/supabase/admin'
import { cleanKey } from '@/lib/core/supabase/env'
import { getPack, priceIdFor } from '@/lib/core/billing/plans'
import { checkRateLimit } from '@/lib/core/security/ratelimit'

export const dynamic = 'force-dynamic'

export async function POST(req: NextRequest) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const limit = checkRateLimit(req, 'stripe_checkout', user.id)
  if (!limit.allowed) return NextResponse.json({ error: 'Too many attempts.' }, { status: 429 })

  const key = cleanKey(process.env.STRIPE_SECRET_KEY)
  if (!key) return NextResponse.json({ error: 'Billing is not configured yet.' }, { status: 503 })

  const body = await req.json().catch(() => ({})) as { pack?: string; plan?: string }
  const pack = getPack(body.pack ?? body.plan ?? '')
  if (!pack) return NextResponse.json({ error: 'Unknown pack.' }, { status: 400 })

  const priceId = priceIdFor(pack)
  if (!priceId) return NextResponse.json({ error: `Pack "${pack.id}" is not available yet.` }, { status: 503 })

  const stripe = new Stripe(key, { maxNetworkRetries: 2 })
  const admin = createAdminClient()

  // Reuse the customer if we already have one, so a returning subscriber does
  // not accumulate duplicate Stripe customers.
  const { data: profile } = await admin.from('profiles').select('stripe_customer_id').eq('id', user.id).maybeSingle()
  let customerId = profile?.stripe_customer_id as string | null | undefined
  if (!customerId) {
    const customer = await stripe.customers.create({
      ...(user.email ? { email: user.email } : {}),
      metadata: { user_id: user.id },
    })
    customerId = customer.id
    await admin.from('profiles').update({ stripe_customer_id: customerId }).eq('id', user.id)
  }

  const origin = req.nextUrl.origin
  try {
    const session = await stripe.checkout.sessions.create({
      // One-time payment, not a subscription: nothing to commit to, nothing to
      // cancel. Credits are granted once and never expire.
      mode: 'payment',
      customer: customerId,
      client_reference_id: user.id,
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${origin}/studio?welcome=1`,
      cancel_url: `${origin}/pricing`,
      allow_promotion_codes: true,
      payment_intent_data: { metadata: { user_id: user.id, pack: pack.id } },
      metadata: { user_id: user.id, pack: pack.id },
    })
    if (!session.url) return NextResponse.json({ error: 'Stripe returned no checkout URL.' }, { status: 502 })
    return NextResponse.json({ url: session.url })
  } catch (e) {
    return NextResponse.json({ error: e instanceof Error ? e.message.slice(0, 200) : 'Checkout failed.' }, { status: 502 })
  }
}
