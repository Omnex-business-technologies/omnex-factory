import { beforeEach, describe, expect, it, vi } from 'vitest'
import { NextRequest } from 'next/server'

const constructEvent = vi.fn()
vi.mock('stripe', () => ({
  default: class Stripe {
    webhooks = { constructEvent: (...args: unknown[]) => constructEvent(...args) }
  },
}))

const rpc = vi.fn()
const update = vi.fn()
const maybeSingle = vi.fn()
vi.mock('@/lib/core/supabase/admin', () => ({
  createAdminClient: () => ({
    rpc: (...args: unknown[]) => rpc(...args),
    from: () => ({
      select: () => ({ eq: () => ({ maybeSingle }) }),
      update: (...args: unknown[]) => ({ eq: (...where: unknown[]) => update(...args, ...where) }),
    }),
  }),
}))

const grantCredits = vi.fn()
vi.mock('@/lib/core/billing/credits', () => ({ grantCredits }))
const { POST } = await import('@/app/api/stripe/webhook/route')

const userId = '11111111-1111-1111-1111-111111111111'
const session = (payment_status: 'paid' | 'unpaid' | 'no_payment_required' = 'paid') => ({
  id: 'cs_paid',
  client_reference_id: userId,
  metadata: { pack: 'taster' },
  customer: 'cus_1',
  payment_status,
})
const event = (type: string, object = session()) => ({
  id: `evt_${type}`,
  type,
  data: { object },
})
const request = () => new NextRequest('http://localhost/api/stripe/webhook', {
  method: 'POST',
  headers: { 'stripe-signature': 'valid' },
  body: '{}',
})

beforeEach(() => {
  process.env.STRIPE_SECRET_KEY = 'sk_test_placeholder'
  process.env.STRIPE_WEBHOOK_SECRET = 'whsec_placeholder'
  constructEvent.mockReset().mockReturnValue(event('checkout.session.completed'))
  rpc.mockReset().mockResolvedValue({ data: 'new', error: null })
  update.mockReset().mockResolvedValue({ error: null })
  maybeSingle.mockReset().mockResolvedValue({ data: null, error: null })
  grantCredits.mockReset().mockResolvedValue(100)
})

describe('Stripe Checkout credit settlement', () => {
  it('fulfills a completed checkout covered by a full promotion discount', async () => {
    constructEvent.mockReturnValue(event('checkout.session.completed', session('no_payment_required')))
    const response = await POST(request())
    expect(response.status).toBe(200)
    expect(grantCredits).toHaveBeenCalledWith(userId, 100, 'purchase', 'cs_paid')
  })

  it('does not grant credits when completed Checkout has not settled', async () => {
    constructEvent.mockReturnValue(event('checkout.session.completed', session('unpaid')))

    const response = await POST(request())

    expect(response.status).toBe(200)
    expect(grantCredits).not.toHaveBeenCalled()
    expect(rpc).toHaveBeenCalledTimes(1)
  })

  it('grants credits when a delayed payment later succeeds', async () => {
    constructEvent.mockReturnValue(event('checkout.session.async_payment_succeeded'))

    const response = await POST(request())

    expect(response.status).toBe(200)
    expect(grantCredits).toHaveBeenCalledWith(userId, 100, 'purchase', 'cs_paid')
  })

  it('replays a previously claimed settled checkout through the purchase idempotency key', async () => {
    rpc.mockResolvedValue({ data: 'duplicate', error: null })

    const response = await POST(request())

    expect(response.status).toBe(200)
    expect(grantCredits).toHaveBeenCalledWith(userId, 100, 'purchase', 'cs_paid')
    expect(update).toHaveBeenCalledWith({ stripe_customer_id: 'cus_1' }, 'id', userId)
  })

  it('still short-circuits duplicate events that cannot grant a purchase', async () => {
    rpc.mockResolvedValue({ data: 'duplicate', error: null })
    constructEvent.mockReturnValue(event('customer.updated'))

    const response = await POST(request())

    expect(response.status).toBe(200)
    expect(await response.json()).toEqual({ received: true, duplicate: true })
    expect(grantCredits).not.toHaveBeenCalled()
  })

  it('returns retryable 500 and marks event failed when the grant RPC fails', async () => {
    grantCredits.mockResolvedValue(null)

    const response = await POST(request())

    expect(response.status).toBe(500)
    expect(rpc).toHaveBeenLastCalledWith('mark_webhook_event_failed', {
      p_id: 'evt_checkout.session.completed',
      p_type: 'checkout.session.completed',
    })
  })

  it('does not acknowledge an inconsistent async-success event as settled', async () => {
    constructEvent.mockReturnValue(event('checkout.session.async_payment_succeeded', session('unpaid')))

    const response = await POST(request())

    expect(response.status).toBe(500)
    expect(grantCredits).not.toHaveBeenCalled()
    expect(rpc).toHaveBeenLastCalledWith('mark_webhook_event_failed', {
      p_id: 'evt_checkout.session.async_payment_succeeded',
      p_type: 'checkout.session.async_payment_succeeded',
    })
  })

  it('returns retryable failure when a paid session has no recognized pack', async () => {
    constructEvent.mockReturnValue(event('checkout.session.completed', {
      ...session(), metadata: { pack: 'unknown' },
    }))

    const response = await POST(request())

    expect(response.status).toBe(500)
    expect(grantCredits).not.toHaveBeenCalled()
    expect(rpc).toHaveBeenLastCalledWith('mark_webhook_event_failed', expect.objectContaining({ p_id: 'evt_checkout.session.completed' }))
  })

  it('returns retryable failure when a paid session cannot be linked to an account', async () => {
    constructEvent.mockReturnValue(event('checkout.session.completed', {
      ...session(), client_reference_id: null, metadata: { pack: 'taster' },
    }))

    const response = await POST(request())

    expect(response.status).toBe(500)
    expect(grantCredits).not.toHaveBeenCalled()
    expect(rpc).toHaveBeenLastCalledWith('mark_webhook_event_failed', expect.objectContaining({ p_id: 'evt_checkout.session.completed' }))
  })

  it('uses the purchase idempotency key when saving the customer link fails after granting', async () => {
    update.mockResolvedValue({ error: new Error('database temporarily unavailable') })

    const response = await POST(request())

    expect(response.status).toBe(500)
    expect(grantCredits).toHaveBeenCalledWith(userId, 100, 'purchase', 'cs_paid')
    expect(rpc).toHaveBeenLastCalledWith('mark_webhook_event_failed', expect.objectContaining({ p_id: 'evt_checkout.session.completed' }))
  })
})
