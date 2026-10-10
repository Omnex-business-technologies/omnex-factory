/**
 * POST /api/stripe/webhook — the only place credits are granted for money.
 *
 * Two properties matter more than anything else here:
 *
 * 1. IDEMPOTENCY THAT SURVIVES A FAILED FIRST ATTEMPT. Every event id is
 *    claimed via `claim_webhook_event` (migration 003) before processing.
 *    "Already claimed" is not the same as "already succeeded": Stripe retries
 *    on any non-2xx response, and a first attempt can fail after claiming the
 *    row (a transient DB error, a timeout). Treating that retry as a
 *    duplicate would silently and permanently drop a paid customer's
 *    credits — the handler used to do exactly that, closed only once this
 *    distinction existed. `claim_webhook_event` returns 'new' (process),
 *    'retry' (a prior attempt at this exact event failed; process again) or
 *    'duplicate' means this event id was claimed before. Non-purchase events
 *    can stop there. Settled Checkout events still reach the purchase grant:
 *    its Stripe session reference is the durable idempotency key, so a crash
 *    after the grant or a failed event-state update cannot drop fulfillment.
 *
 * 2. SIGNATURE VERIFICATION on the RAW body. Parsing before verifying would let
 *    anyone mint credits by POSTing JSON.
 *
 * Credits are granted only after Stripe reports the payment as paid. A delayed
 * payment's completed event is acknowledged without granting credits; Stripe
 * later sends `checkout.session.async_payment_succeeded` when settlement lands.
 * Packs are one-time purchases, so there is no recurring charge to reconcile.
 */
import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'
import { createAdminClient } from '@/lib/core/supabase/admin'
import { cleanKey } from '@/lib/core/supabase/env'
import { grantCredits } from '@/lib/core/billing/credits'
import { getPack } from '@/lib/core/billing/plans'

export const dynamic = 'force-dynamic'

/** Resolve our user id from whatever the event carries. */
async function resolveUserId(admin: ReturnType<typeof createAdminClient>, opts: {
  clientReferenceId?: string | null
  metadataUserId?: string | null
  customerId?: string | null
}): Promise<string | null> {
  if (opts.clientReferenceId) return opts.clientReferenceId
  if (opts.metadataUserId) return opts.metadataUserId
  if (opts.customerId) {
    const { data } = await admin.from('profiles').select('id').eq('stripe_customer_id', opts.customerId).maybeSingle()
    return (data?.id as string | undefined) ?? null
  }
  return null
}

export async function POST(req: NextRequest) {
  const key = cleanKey(process.env.STRIPE_SECRET_KEY)
  const secret = cleanKey(process.env.STRIPE_WEBHOOK_SECRET)
  if (!key || !secret) return NextResponse.json({ error: 'Billing not configured' }, { status: 503 })

  const signature = req.headers.get('stripe-signature')
  if (!signature) return NextResponse.json({ error: 'Missing signature' }, { status: 400 })

  const raw = await req.text()
  const stripe = new Stripe(key, { maxNetworkRetries: 2 })

  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(raw, signature, secret)
  } catch (e) {
    return NextResponse.json({ error: `Signature verification failed: ${e instanceof Error ? e.message : ''}` }, { status: 400 })
  }

  const admin = createAdminClient()

  // Claim webhook events for retry coordination. The purchase grant's session
  // reference is the exactly-once boundary for settled Checkout events, so
  // those events remain safe to process even when this event id was claimed.
  const { data: claim, error: claimErr } = await admin.rpc('claim_webhook_event', {
    p_id: event.id,
    p_type: event.type,
  })
  if (claimErr) return NextResponse.json({ error: 'Could not record event' }, { status: 500 })
  const checkoutSettlement =
    event.type === 'checkout.session.completed' ||
    event.type === 'checkout.session.async_payment_succeeded'
  if (claim === 'duplicate' && !checkoutSettlement) {
    return NextResponse.json({ received: true, duplicate: true })
  }

  try {
    switch (event.type) {
      case 'checkout.session.completed':
      case 'checkout.session.async_payment_succeeded': {
        const s = event.data.object as Stripe.Checkout.Session
        // Checkout can complete before a delayed payment method settles. The
        // later async_payment_succeeded event is the fulfillment signal. A
        // fully discounted Checkout needs no payment and may also be fulfilled.
        const settled = s.payment_status === 'paid' || s.payment_status === 'no_payment_required'
        if (!settled) {
          if (event.type === 'checkout.session.completed') break
          throw new Error('Async payment success event did not contain a paid session')
        }
        const packId = (s.metadata?.pack as string | undefined) ?? (s.metadata?.plan as string | undefined) ?? ''
        const pack = getPack(packId)
        const userId = await resolveUserId(admin, {
          clientReferenceId: s.client_reference_id,
          metadataUserId: s.metadata?.user_id ?? null,
          customerId: typeof s.customer === 'string' ? s.customer : null,
        })
        if (!pack) throw new Error('Paid Checkout session has an unknown credit pack')
        if (!userId) throw new Error('Could not resolve the paid Checkout session to a user')

        const balance = await grantCredits(userId, pack.credits, 'purchase', s.id)
        if (balance === null) throw new Error('Could not grant purchased credits')
        if (typeof s.customer === 'string') {
          const { error } = await admin.from('profiles').update({ stripe_customer_id: s.customer }).eq('id', userId)
          if (error) throw new Error('Could not save the Stripe customer link')
        }
        break
      }


      default:
        break
    }
    return NextResponse.json({ received: true })
  } catch (e) {
    // Returning 500 asks Stripe to retry. Preserve the failure marker for event
    // accounting, but Checkout retries also reach session-level idempotency if
    // this marker write fails or a previous process died after claiming.
    await admin.rpc('mark_webhook_event_failed', { p_id: event.id, p_type: event.type })
    return NextResponse.json({ error: e instanceof Error ? e.message.slice(0, 200) : 'handler failed' }, { status: 500 })
  }
}
