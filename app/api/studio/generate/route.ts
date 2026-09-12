/**
 * POST /api/studio/generate — AI Ad Studio, module #1.
 *
 * Flow, in this order deliberately:
 *   auth → validate → CHARGE credits → generate → persist renders → record usage
 * and refund if the generation failed, so a customer is never billed for nothing.
 *
 * Charging before the provider call is what closes the abuse window: the credit
 * row is locked and decremented inside `consume_credits` (SQL, FOR UPDATE), so
 * two simultaneous requests cannot spend the same balance.
 */
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/core/supabase/server'
import { createAdminClient } from '@/lib/core/supabase/admin'
import { spendCredits, refundCredits, recordUsage, creditBalance } from '@/lib/core/billing/credits'
import { generateImages, capabilitiesOf } from '@/lib/core/images/provider'
import { getFormat, FORMATS, FIDELITY, type FormatId, type FidelityId } from '@/lib/modules/studio/presets'
import { buildCampaignPrompt } from '@/lib/modules/studio/build'
import { getCategory, CATEGORIES, type CategoryId } from '@/lib/modules/studio/categories'
import { SCHOOLS, type SchoolId } from '@/lib/modules/studio/personas'
import { creditCostOf } from '@/lib/modules/registry'
import { checkRateLimit } from '@/lib/core/security/ratelimit'

export const dynamic = 'force-dynamic'
export const maxDuration = 120

const MODULE_ID = 'studio'
const MAX_IMAGES = 4

interface GenerateBody {
  /** What the customer described: product, look, dish, vehicle or space. */
  subject?: string
  category?: CategoryId
  scene?: string
  format?: FormatId
  fidelity?: FidelityId
  /** Beauty school — only meaningful for person-led categories. */
  school?: SchoolId
  imageUrl?: string
  count?: number
}

export async function POST(req: NextRequest) {
  // ── 1. Auth ───────────────────────────────────────────────────────────────
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const limit = checkRateLimit(req, 'studio_generate', user.id)
  if (!limit.allowed) {
    return NextResponse.json({ error: 'Too many requests. Try again shortly.' }, { status: 429 })
  }

  // ── 2. Validate ───────────────────────────────────────────────────────────
  let body: GenerateBody
  try {
    body = (await req.json()) as GenerateBody
  } catch {
    return NextResponse.json({ error: 'Malformed JSON body' }, { status: 400 })
  }

  const subject = (body.subject ?? '').trim()
  if (subject.length < 3) {
    return NextResponse.json({ error: 'Describe your subject in a few words (min 3 characters).' }, { status: 400 })
  }
  if (subject.length > 300) {
    return NextResponse.json({ error: 'Description is too long (max 300 characters).' }, { status: 400 })
  }

  // Every selection is resolved against the catalogue, so an unknown id from the
  // client can never reach the prompt — it falls back to that category's default.
  const category = getCategory(body.category ?? 'product') ?? CATEGORIES[0]!
  const scene = category.scenes.find((s) => s.id === body.scene)?.id ?? category.scenes[0]!.id
  const format = getFormat(body.format ?? 'portrait') ?? FORMATS[1]!
  const fidelity = FIDELITY.find((f) => f.id === body.fidelity)?.id ?? 'balanced'
  const school = SCHOOLS.find((s) => s.id === body.school)?.id ?? SCHOOLS[0]!.id
  const count = Math.min(Math.max(Number(body.count ?? 1), 1), MAX_IMAGES)

  // The uploaded product photo must live in our own storage — never fetch an
  // arbitrary user-supplied URL server-side (SSRF), and providers need it public.
  const imageUrl = body.imageUrl?.trim()
  if (imageUrl) {
    const expectedPrefix = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/storage/v1/object/public/products/`
    if (!imageUrl.startsWith(expectedPrefix)) {
      return NextResponse.json({ error: 'Product photo must be uploaded through the Studio.' }, { status: 400 })
    }
  }

  const cost = creditCostOf(MODULE_ID) * count
  const built = buildCampaignPrompt({ category: category.id, scene, subject, fidelity, school })

  // ── 3. Charge BEFORE any paid work ────────────────────────────────────────
  const charge = await spendCredits(user.id, cost, MODULE_ID)
  if (!charge.ok) {
    if (charge.reason === 'insufficient_credits') {
      const balance = await creditBalance(user.id)
      return NextResponse.json(
        { error: 'Not enough credits.', needed: cost, balance },
        { status: 402 },
      )
    }
    return NextResponse.json({ error: 'Could not reserve credits.' }, { status: 500 })
  }

  // ── 4. Generate ───────────────────────────────────────────────────────────
  const started = Date.now()
  try {
    const result = await generateImages({
      prompt: built.prompt,
      ...(imageUrl ? { imageUrl } : {}),
      aspect: format.aspect,
      count,
      strength: built.strength,
    })

    // ── 5. Persist renders so the customer keeps them after provider URLs expire ──
    const admin = createAdminClient()
    const stored = await Promise.all(result.images.map(async (img, i) => {
      try {
        const res = await fetch(img.url, { signal: AbortSignal.timeout(60_000) })
        if (!res.ok) return { url: img.url, stored: false }
        const bytes = Buffer.from(await res.arrayBuffer())
        const path = `${user.id}/${Date.now()}-${i}.jpg`
        const up = await admin.storage.from('renders').upload(path, bytes, { contentType: 'image/jpeg' })
        if (up.error) return { url: img.url, stored: false }
        return { url: admin.storage.from('renders').getPublicUrl(path).data.publicUrl, stored: true }
      } catch {
        // Keep the provider URL rather than failing the whole request.
        return { url: img.url, stored: false }
      }
    }))

    void recordUsage({
      userId: user.id, moduleId: MODULE_ID, action: 'generate', credits: cost, ok: true,
      meta: { category: category.id, scene, format: format.id, fidelity, count, provider: result.provider, elapsedMs: Date.now() - started, imageToImage: !!imageUrl },
    })

    return NextResponse.json({
      images: stored,
      creditsSpent: cost,
      balance: await creditBalance(user.id),
      provider: result.provider,
      elapsedMs: Date.now() - started,
      // Capabilities of the provider that ACTUALLY served this render — not the
      // one we intended to use, which may have failed over to a fallback.
      capabilities: capabilitiesOf(result.provider),
      // Renders containing a synthetic person must carry a label wherever they
      // are published — the UI shows this under the image.
      ...(built.needsDisclosure ? { disclosure: built.disclosure } : {}),
    })
  } catch (e) {
    // ── 6. Refund — the customer must never pay for a failed generation ─────
    await refundCredits(user.id, cost, 'generation_failed')
    const message = e instanceof Error ? e.message : String(e)
    void recordUsage({
      userId: user.id, moduleId: MODULE_ID, action: 'generate', credits: 0, ok: false,
      meta: { category: category.id, scene, format: format.id, fidelity, error: message.slice(0, 300) },
    })
    return NextResponse.json(
      { error: 'Generation failed — your credits were refunded.', detail: message.slice(0, 200) },
      { status: 502 },
    )
  }
}
