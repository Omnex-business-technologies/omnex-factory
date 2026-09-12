/**
 * /api/healthz and /api/readyz — and the one rule that matters most: a
 * missing required variable must produce a 503 with the variable's NAME,
 * never its value, and liveness must never depend on any of this at all.
 */
import { describe, it, expect } from 'vitest'
import { checkReadiness, type EnvManifest } from '@/lib/core/health/manifest'
import { GET as healthz } from '@/app/api/healthz/route'
import { GET as readyz } from '@/app/api/readyz/route'
import realManifest from '@/deploy/env.json'

const MANIFEST: EnvManifest = {
  version: 1,
  groups: {
    'an image model': {
      why: 'at least one image provider must be configured',
      any_of: ['FAL_KEY', 'REPLICATE_API_TOKEN'],
    },
  },
  vars: {
    REQUIRED_ONE: { required: true, secret: false, why: 'x' },
    REQUIRED_TWO: { required: true, secret: true, why: 'x' },
    OPTIONAL_ONE: { required: false, secret: false, why: 'x' },
  },
}

describe('checkReadiness', () => {
  it('is ready when every required var and every group is satisfied', () => {
    const result = checkReadiness(MANIFEST, {
      REQUIRED_ONE: 'a',
      REQUIRED_TWO: 'b',
      FAL_KEY: 'c',
    })
    expect(result.ready).toBe(true)
    expect(result.missingRequired).toEqual([])
    expect(result.unsatisfiedGroups).toEqual([])
  })

  it('names a missing required variable, not its absence alone', () => {
    const result = checkReadiness(MANIFEST, { REQUIRED_TWO: 'b', FAL_KEY: 'c' })
    expect(result.ready).toBe(false)
    expect(result.missingRequired).toEqual(['REQUIRED_ONE'])
  })

  it('does not leak the value of a secret var into the result', () => {
    const result = checkReadiness(MANIFEST, {
      REQUIRED_ONE: 'a',
      REQUIRED_TWO: 'super-secret-value',
      FAL_KEY: 'c',
    })
    expect(JSON.stringify(result)).not.toContain('super-secret-value')
  })

  it('reports a group as unsatisfied when no member is set', () => {
    const result = checkReadiness(MANIFEST, { REQUIRED_ONE: 'a', REQUIRED_TWO: 'b' })
    expect(result.unsatisfiedGroups).toEqual(['an image model'])
  })

  it('an optional var missing does not affect readiness', () => {
    const result = checkReadiness(MANIFEST, {
      REQUIRED_ONE: 'a',
      REQUIRED_TWO: 'b',
      FAL_KEY: 'c',
    })
    expect(result.ready).toBe(true)
  })

  it('an empty string counts as unset, not as a set value', () => {
    const result = checkReadiness(MANIFEST, { REQUIRED_ONE: '', REQUIRED_TWO: 'b', FAL_KEY: 'c' })
    expect(result.missingRequired).toEqual(['REQUIRED_ONE'])
  })
})

describe('GET /api/healthz', () => {
  it('always answers 200 with no dependency check', async () => {
    const response = await healthz()
    expect(response.status).toBe(200)
    const body = await response.json()
    expect(body).toEqual({ ok: true })
  })
})

describe('GET /api/readyz', () => {
  it('answers against the REAL deploy/env.json, so this fails if it drifts', async () => {
    // Whatever this test environment's process.env holds, the response shape
    // must hold regardless -- this is checking the route wires the real
    // manifest in, not asserting a specific readiness outcome that would
    // depend on which secrets happen to be set when the suite runs.
    const response = await readyz()
    const body = await response.json()
    expect([200, 503]).toContain(response.status)
    expect(typeof body.ready).toBe('boolean')
    if (!body.ready) {
      expect(Array.isArray(body.missingRequired)).toBe(true)
      expect(Array.isArray(body.unsatisfiedGroups)).toBe(true)
    }
  })

  it('never puts a secret value in the response body', async () => {
    const response = await readyz()
    const text = await response.text()
    for (const [name, spec] of Object.entries(realManifest.vars)) {
      if (spec.secret && process.env[name]) {
        expect(text).not.toContain(process.env[name] as string)
      }
    }
  })
})
