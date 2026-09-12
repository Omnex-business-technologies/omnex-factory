/**
 * GET /api/readyz — does THIS running process have what it needs to serve
 * real traffic, checked against `deploy/env.json`, the same manifest
 * `engine/scripts/env_check.py` checks against the code at CI time.
 *
 * 503 on anything missing. Never 200-with-a-warning: a platform's own health
 * check only acts on the status code, and a required Stripe key that is
 * merely logged as a warning is the exact "quietly half the product" failure
 * `deploy/env.json`'s own file-level comment names.
 *
 * Names only in the response, never values — the manifest's own rule
 * (`env_check.py` never prints one either) applies here just as much: a
 * readiness probe that echoed a secret to prove it holds one would be a
 * worse leak than the outage it exists to prevent.
 */
import { NextResponse } from 'next/server'
import manifest from '@/deploy/env.json'
import { checkReadiness, type EnvManifest } from '@/lib/core/health/manifest'

export async function GET() {
  const result = checkReadiness(manifest as EnvManifest, process.env)

  if (!result.ready) {
    return NextResponse.json(
      {
        ready: false,
        missingRequired: result.missingRequired,
        unsatisfiedGroups: result.unsatisfiedGroups,
      },
      { status: 503 }
    )
  }

  return NextResponse.json({ ready: true })
}
