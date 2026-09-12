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
 *    'duplicate' (already succeeded, or another request currently owns it;
 *    do nothing) — the atomicity of that three-way decision lives in the
 *    database, not here, so two concurrent retries of the same failed event
 *    cannot both win.
 *
 * 2. SIGNATURE VERIFICATION on the RAW body. Parsing before verifying would let
 *    anyone mint credits by POSTing JSON.
 *
 * Credits are granted on `checkout.session.completed`. There is no renewal
 * branch: packs are one-time purchases, so a single event grants a single
 * balance and there is no recurring charge to reconcile.
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

  // Idempotency gate — 'new' or 'retry' proceed to processing below;
  // 'duplicate' means this exact event already succeeded (or is being
  // handled by a concurrent request right now) and must not run again.
  const { data: claim, error: claimErr } = await admin.rpc('claim_webhook_event', {
    p_id: event.id,
    p_type: event.type,
  })
  if (claimErr) return NextResponse.json({ error: 'Could not record event' }, { status: 500 })
  if (claim === 'duplicate') return NextResponse.json({ received: true, duplicate: true })

  try {
    switch (event.type) {
      case 'checkout.session.completed': {
        const s = event.data.object as Stripe.Checkout.Session
        const packId = (s.metadata?.pack as string | undefined) ?? (s.metadata?.plan as string | undefined) ?? ''
        const pack = getPack(packId)
        const userId = await resolveUserId(admin, {
          clientReferenceId: s.client_reference_id,
          metadataUserId: s.metadata?.user_id ?? null,
          customerId: typeof s.customer === 'string' ? s.customer : null,
        })
        if (userId && pack) {
          await grantCredits(userId, pack.credits, 'purchase', s.id)
          if (typeof s.customer === 'string') {
            await admin.from('profiles').update({ stripe_customer_id: s.customer }).eq('id', userId)
          }
        }
        break
      }


      default:
        break
    }
    return NextResponse.json({ received: true })
  } catch (e) {
    // Returning 500 asks Stripe to retry. Marking the row failed (rather than
    // leaving it claimed) is what makes that retry actually reach the switch
    // above instead of being turned away as a duplicate next time.
    await admin.rpc('mark_webhook_event_failed', { p_id: event.id, p_type: event.type })
    return NextResponse.json({ error: e instanceof Error ? e.message.slice(0, 200) : 'handler failed' }, { status: 500 })
  }
}
