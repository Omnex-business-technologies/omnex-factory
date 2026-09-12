/**
 * POST /api/studio/upload — receives the customer's product photo.
 *
 * Uploads go through the server (not straight from the browser) so the file type
 * and size are enforced before anything lands in storage, and every object is
 * written under the owner's user id. The returned URL is public because the
 * generation providers fetch it server-side; the generate route only accepts
 * URLs with this exact prefix, so an attacker cannot point us at an internal host.
 */
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/core/supabase/server'
import { createAdminClient } from '@/lib/core/supabase/admin'
import { checkRateLimit } from '@/lib/core/security/ratelimit'

export const dynamic = 'force-dynamic'
export const maxDuration = 60

const MAX_BYTES = 10 * 1024 * 1024 // 10 MB
const ALLOWED = new Map([
  ['image/jpeg', 'jpg'],
  ['image/png', 'png'],
  ['image/webp', 'webp'],
])

export async function POST(req: NextRequest) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const limit = checkRateLimit(req, 'studio_upload', user.id)
  if (!limit.allowed) return NextResponse.json({ error: 'Too many uploads. Try again shortly.' }, { status: 429 })

  let file: File | null = null
  try {
    const form = await req.formData()
    const candidate = form.get('file')
    if (candidate instanceof File) file = candidate
  } catch {
    return NextResponse.json({ error: 'Expected a multipart form upload.' }, { status: 400 })
  }
  if (!file) return NextResponse.json({ error: 'No file provided.' }, { status: 400 })

  const ext = ALLOWED.get(file.type)
  if (!ext) return NextResponse.json({ error: 'Use a JPG, PNG or WebP image.' }, { status: 415 })
  if (file.size > MAX_BYTES) return NextResponse.json({ error: 'Image is larger than 10 MB.' }, { status: 413 })

  const bytes = Buffer.from(await file.arrayBuffer())
  const path = `${user.id}/${Date.now()}.${ext}`

  const admin = createAdminClient()
  const { error } = await admin.storage.from('products').upload(path, bytes, {
    contentType: file.type,
    upsert: false,
  })
  if (error) return NextResponse.json({ error: 'Upload failed.', detail: error.message }, { status: 500 })

  return NextResponse.json({
    url: admin.storage.from('products').getPublicUrl(path).data.publicUrl,
    path,
  })
}
