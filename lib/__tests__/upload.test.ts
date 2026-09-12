/**
 * POST /api/studio/upload — the file-signature check this file exists to prove.
 *
 * `file.type` is metadata a multipart sender puts on its own request, not a
 * fact about the bytes that follow it — trivial to set to `image/jpeg` on
 * arbitrary content with a raw `fetch`/`curl`, no browser file picker
 * involved. Before this test file existed, this route had never been tested
 * at all, and it trusted that label alone before writing to a public bucket
 * and handing back a public URL on this product's own domain.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { NextRequest } from 'next/server'
import { matchesSignature } from '@/app/api/studio/upload/route'

const getUser = vi.fn()
vi.mock('@/lib/core/supabase/server', () => ({
  createClient: async () => ({ auth: { getUser } }),
}))

const upload = vi.fn()
const getPublicUrl = vi.fn()
vi.mock('@/lib/core/supabase/admin', () => ({
  createAdminClient: () => ({
    storage: {
      from: () => ({
        upload: (...args: unknown[]) => upload(...args),
        getPublicUrl: (...args: unknown[]) => getPublicUrl(...args),
      }),
    },
  }),
}))

const { POST } = await import('@/app/api/studio/upload/route')

const USER_ID = '33333333-3333-3333-3333-333333333333'

// Real magic bytes for each allowed type, padded so `.length` checks pass.
const REAL_JPEG = Buffer.from([0xff, 0xd8, 0xff, 0xe0, 0, 0, 0, 0, 0, 0])
const REAL_PNG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0, 0])
const REAL_WEBP = Buffer.concat([Buffer.from('RIFF'), Buffer.from([0, 0, 0, 0]), Buffer.from('WEBP')])

function requestWith(file: File, ip: string): NextRequest {
  const form = new FormData()
  form.set('file', file)
  return new NextRequest('http://localhost/api/studio/upload', {
    method: 'POST',
    headers: { 'x-forwarded-for': ip },
    body: form,
  })
}

describe('matchesSignature — the real bytes, not the claimed label', () => {
  it('accepts a real JPEG, PNG or WebP signature', () => {
    expect(matchesSignature('image/jpeg', REAL_JPEG)).toBe(true)
    expect(matchesSignature('image/png', REAL_PNG)).toBe(true)
    expect(matchesSignature('image/webp', REAL_WEBP)).toBe(true)
  })

  it('rejects content that does not match the claimed type', () => {
    // Exactly the attack this check exists for: a claimed image/jpeg label on
    // bytes that are not a JPEG at all -- here, an HTML document.
    const html = Buffer.from('<html><body><script>alert(1)</script></body></html>')
    expect(matchesSignature('image/jpeg', html)).toBe(false)
    expect(matchesSignature('image/png', html)).toBe(false)
    expect(matchesSignature('image/webp', html)).toBe(false)
  })

  it('rejects one real format mislabelled as another', () => {
    expect(matchesSignature('image/png', REAL_JPEG)).toBe(false)
    expect(matchesSignature('image/jpeg', REAL_PNG)).toBe(false)
    expect(matchesSignature('image/webp', REAL_JPEG)).toBe(false)
  })

  it('rejects a buffer too short to carry a real signature', () => {
    expect(matchesSignature('image/jpeg', Buffer.from([0xff]))).toBe(false)
    expect(matchesSignature('image/png', Buffer.alloc(0))).toBe(false)
  })

  it('rejects an unknown mime type outright', () => {
    expect(matchesSignature('image/svg+xml', REAL_JPEG)).toBe(false)
  })
})

describe('POST /api/studio/upload', () => {
  beforeEach(() => {
    getUser.mockReset().mockResolvedValue({ data: { user: { id: USER_ID } } })
    upload.mockReset().mockResolvedValue({ error: null })
    getPublicUrl.mockReset().mockReturnValue({ data: { publicUrl: 'https://example.test/products/x.jpg' } })
  })

  it('refuses content that does not match its claimed image/jpeg label', async () => {
    // The exact bypass this route used to allow: an attacker sets `type:
    // 'image/jpeg'` on a File whose actual bytes are something else entirely,
    // via a raw multipart request nothing about a browser's file picker
    // enforces.
    const disguised = new File(
      [new Blob([Buffer.from('<html><body><script>alert(1)</script></body></html>')])],
      'photo.jpg',
      { type: 'image/jpeg' },
    )
    const response = await POST(requestWith(disguised, '10.7.0.1'))
    expect(response.status).toBe(415)
    expect(upload).not.toHaveBeenCalled()
  })

  it('accepts a real image whose bytes match its claimed type', async () => {
    const real = new File([new Blob([REAL_JPEG])], 'photo.jpg', { type: 'image/jpeg' })
    const response = await POST(requestWith(real, '10.7.0.2'))
    expect(response.status).toBe(200)
    expect(upload).toHaveBeenCalledTimes(1)
    const [path] = upload.mock.calls[0] as [string]
    expect(path).toMatch(new RegExp(`^${USER_ID}/\\d+\\.jpg$`))
  })

  it('refuses an unauthenticated request before touching storage', async () => {
    getUser.mockResolvedValue({ data: { user: null } })
    const real = new File([new Blob([REAL_JPEG])], 'photo.jpg', { type: 'image/jpeg' })
    const response = await POST(requestWith(real, '10.7.0.3'))
    expect(response.status).toBe(401)
    expect(upload).not.toHaveBeenCalled()
  })
})
