/**
 * POST /api/studio/upload — receives the customer's product photo.
 *
 * Uploads go through the server (not straight from the browser) so the file type
 * and size are enforced before anything lands in storage, and every object is
 * written under the owner's user id. The returned URL is public because the
 * generation providers fetch it server-side; the generate route only accepts
 * URLs with this exact prefix, so an attacker cannot point us at an internal host.
 *
 * ## `file.type` is a label the client wrote, not a fact about the bytes
 *
 * A multipart form's `Content-Type` for one part is metadata the sender sets on
 * the request — trivial to set to `image/jpeg` on any bytes whatsoever with a
 * raw `fetch`/`curl`, no browser file picker involved. Checking only `file.type`
 * meant this route would store arbitrary content (an HTML file, an SVG carrying
 * a `<script>`, anything) under a claimed image type, in the `products` bucket
 * this same docstring already calls public, and hand back a public URL on this
 * product's own domain serving it with that claimed content-type — unrestricted
 * file upload, OWASP's own name for exactly this class. `matchesSignature`
 * checks the first bytes actually uploaded against each allowed format's real
 * file signature before anything reaches storage, so the label can no longer
 * stand in for the content it claims to describe.
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

/**
 * The real file signature for each allowed type, checked against the bytes
 * actually uploaded — never the client-supplied `Content-Type` label alone.
 * `matchesSignature` is exported so a test can prove both directions: a real
 * image of each type passes, and a mismatched or truncated one does not.
 */
export function matchesSignature(mimeType: string, bytes: Buffer): boolean {
  switch (mimeType) {
    case 'image/jpeg':
      return bytes.length >= 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff
    case 'image/png':
      return (
        bytes.length >= 8 &&
        bytes[0] === 0x89 &&
        bytes[1] === 0x50 &&
        bytes[2] === 0x4e &&
        bytes[3] === 0x47 &&
        bytes[4] === 0x0d &&
        bytes[5] === 0x0a &&
        bytes[6] === 0x1a &&
        bytes[7] === 0x0a
      )
    case 'image/webp':
      return (
        bytes.length >= 12 &&
        bytes.toString('ascii', 0, 4) === 'RIFF' &&
        bytes.toString('ascii', 8, 12) === 'WEBP'
      )
    default:
      return false
  }
}

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
  // `file.type` is the label the client put on this multipart part, not a fact
  // about `bytes` — see the module docstring. Refused here, before anything
  // reaches storage or gets a public URL.
  if (!matchesSignature(file.type, bytes)) {
    return NextResponse.json(
      { error: 'File content does not match a JPG, PNG or WebP image.' },
      { status: 415 },
    )
  }
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
