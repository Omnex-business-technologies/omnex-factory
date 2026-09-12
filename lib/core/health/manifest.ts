/**
 * Reads `deploy/env.json` and checks a live environment against it —
 * `engine/scripts/env_check.py --runtime`'s question, asked over HTTP instead
 * of SSH.
 *
 * `env_check.py` already answers "does the manifest agree with the code" at
 * CI time. What it cannot answer is "does the machine serving requests RIGHT
 * NOW actually have what it needs" — Docker and deployment infrastructure are
 * not proof of that, and almost every one of these variables fails CLOSED
 * (`cron-auth` returns false unset, every Stripe route answers 503): the site
 * is up, pages render, and a whole feature is silently unreachable. This is
 * the runtime half, exposed so a deploy platform or an uptime check can ask.
 *
 * Values are never read into the response — only whether a name is set. A
 * readiness endpoint that echoed a secret to prove it has one would be the
 * exact mistake `env_check.py`'s own docstring already refuses.
 */

export interface EnvVarSpec {
  required: boolean
  secret: boolean
  why: string
}

export interface EnvGroup {
  why: string
  any_of: string[]
}

export interface EnvManifest {
  version: number
  groups: Record<string, EnvGroup>
  vars: Record<string, EnvVarSpec>
}

export interface ReadinessResult {
  ready: boolean
  /** Names only, never values. */
  missingRequired: string[]
  /** A group name whose `any_of` has no member set. */
  unsatisfiedGroups: string[]
}

/** `env`'s own shape (`Record<string, string | undefined>`) rather than the
 * whole `NodeJS.ProcessEnv` type, so a test can pass a plain object without
 * pulling in Node's global environment. */
export function checkReadiness(
  manifest: EnvManifest,
  env: Record<string, string | undefined>
): ReadinessResult {
  const missingRequired = Object.entries(manifest.vars)
    .filter(([, spec]) => spec.required)
    .map(([name]) => name)
    .filter((name) => !env[name])

  const unsatisfiedGroups = Object.entries(manifest.groups)
    .filter(([, group]) => !group.any_of.some((name) => !!env[name]))
    .map(([name]) => name)

  return {
    ready: missingRequired.length === 0 && unsatisfiedGroups.length === 0,
    missingRequired,
    unsatisfiedGroups,
  }
}
