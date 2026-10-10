/**
 * Credit-ledger tests against a REAL Postgres, in a throwaway container.
 *
 * Why this exists: the credit logic was previously verified by running it against
 * the live production database — creating real auth users, spending real rows,
 * then deleting them. It worked, but a crash mid-run would have left debris in a
 * customer-facing database, and a bug in a cleanup step could have deleted more
 * than it created.
 *
 * The behaviour under test cannot be checked with mocks: `consume_credits` is a
 * PL/pgSQL function whose correctness IS the `SELECT … FOR UPDATE` row lock. A
 * fake client would prove nothing. So the test starts a real Postgres, applies
 * the real migration, and throws the container away afterwards.
 *
 * Skipped automatically when Docker is unavailable, so CI without a daemon stays
 * green instead of failing for an unrelated reason.
 * For local review without Docker, OMNEX_REVIEW_DATABASE_URL may select a
 * dedicated loopback database named review_app. Its public schema is reset.
 */
import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

// Long first run: the image has to be pulled.
const BOOT_TIMEOUT = 240_000

type Pg = import('pg').Client
let container: import('@testcontainers/postgresql').StartedPostgreSqlContainer | null = null
let db: Pg | null = null
let available = false
const REVIEW_DATABASE_URL = process.env.OMNEX_REVIEW_DATABASE_URL
const LEGACY_USER = '33333333-3333-3333-3333-333333333333'

/** The migration minus the pieces that need Supabase's auth schema. */
function migrationSql(): string {
  const sql = readFileSync(resolve(process.cwd(), 'supabase/migrations/001_factory_core.sql'), 'utf8')
  return sql
    // `auth.users` and `auth.uid()` only exist inside Supabase.
    .replace(/references auth\.users\(id\) on delete (cascade|set null)/g, '')
    .replace(/^\s*alter table [\s\S]*?enable row level security;$/gm, '')
    .replace(/^\s*drop policy[\s\S]*?;$/gm, '')
    .replace(/create policy[\s\S]*?;\s*$/gm, '')
    // The trigger needs auth.users, but keep its function so migration 004 can
    // harden every SECURITY DEFINER function exactly like production.
    .replace(/drop trigger if exists on_auth_user_created_factory[\s\S]*?;/m, '')
    .replace(/create trigger on_auth_user_created_factory[\s\S]*?;/m, '')
}

/** Migration 003 references nothing Supabase-only, so it needs no stripping. */
function webhookRetryMigrationSql(): string {
  return readFileSync(resolve(process.cwd(), 'supabase/migrations/003_webhook_retry.sql'), 'utf8')
}

function billingPrivilegeMigrationSql(): string {
  return readFileSync(resolve(process.cwd(), 'supabase/migrations/004_rpc_privileges.sql'), 'utf8')
}

function purchaseIdempotencyMigrationSql(): string {
  const sql = readFileSync(resolve(process.cwd(), 'supabase/migrations/005_purchase_grant_idempotency.sql'), 'utf8')
  // Unit DBs intentionally omit Supabase auth.users while preserving the SQL's
  // function bodies, constraints, conflicts, and privilege checks.
  return sql.replace(/references auth\.users\(id\) on delete cascade/g, '')
}

function connectionString(): string {
  return REVIEW_DATABASE_URL ?? container!.getConnectionUri()
}

beforeAll(async () => {
  try {
    const { Client } = await import('pg')
    if (REVIEW_DATABASE_URL) {
      const reviewUrl = new URL(REVIEW_DATABASE_URL)
      if (!['127.0.0.1', 'localhost', '[::1]', '::1'].includes(reviewUrl.hostname)) {
        throw new Error('OMNEX_REVIEW_DATABASE_URL must use localhost or loopback')
      }
      if (reviewUrl.pathname.replace(/^\//, '') !== 'review_app') {
        throw new Error('OMNEX_REVIEW_DATABASE_URL must point to the disposable review_app database')
      }
      db = new Client({ connectionString: REVIEW_DATABASE_URL })
    } else {
      const { PostgreSqlContainer } = await import('@testcontainers/postgresql')
      // pgvector image: the real schema declares vector columns elsewhere, and using
      // the same base as production keeps this from passing on a laxer engine.
      container = await new PostgreSqlContainer('pgvector/pgvector:pg16').start()
      db = new Client({ connectionString: container.getConnectionUri() })
    }
    await db.connect()

    if (REVIEW_DATABASE_URL) {
      const target = await db.query('select current_database() as name')
      if (target.rows[0].name !== 'review_app') throw new Error('review database name changed during connection')
      await db.query('drop schema public cascade; create schema public;')
      await db.query('grant usage on schema public to public;')
    }
    await db.query(`do $$ begin
      if not exists (select 1 from pg_roles where rolname = 'anon') then execute 'create role anon'; end if;
      if not exists (select 1 from pg_roles where rolname = 'authenticated') then execute 'create role authenticated'; end if;
      if not exists (select 1 from pg_roles where rolname = 'service_role') then execute 'create role service_role'; end if;
    end $$;`)
    await db.query(migrationSql())
    await db.query(webhookRetryMigrationSql())
    // Model a purchase already in the ledger when 005 is installed. Migration
    // 005 must seed its reference so an old Stripe replay cannot grant twice.
    await db.query('insert into public.credit_balance(user_id, credits) values ($1, 100)', [LEGACY_USER])
    await db.query(
      "insert into public.credit_ledger(user_id, delta, reason, stripe_ref) values ($1, 100, 'purchase', 'cs_legacy')",
      [LEGACY_USER],
    )
    await db.query(billingPrivilegeMigrationSql())
    await db.query(purchaseIdempotencyMigrationSql())
    available = true
  } catch (error) {
    available = false
    if (REVIEW_DATABASE_URL) console.error('review_app migration setup failed:', error)
  }
}, BOOT_TIMEOUT)

afterAll(async () => {
  await db?.end().catch(() => {})
  await container?.stop().catch(() => {})
})

const USER = '11111111-1111-1111-1111-111111111111'

describe('purchase grant idempotency and RPC privileges against real Postgres', () => {
  it('backfills existing purchase refs and treats a replay as already granted', async () => {
    if (!available || !db) return
    const seeded = await db.query("select user_id, amount from credit_grant_refs where stripe_ref = 'cs_legacy'")
    expect(seeded.rows).toEqual([{ user_id: LEGACY_USER, amount: 100 }])
    await db.query('select grant_credits($1, $2, $3, $4)', [LEGACY_USER, 100, 'purchase', 'cs_legacy'])
    const balance = await db.query('select credits from credit_balance where user_id = $1', [LEGACY_USER])
    const ledger = await db.query("select count(*)::int as n from credit_ledger where stripe_ref = 'cs_legacy'")
    expect(balance.rows[0].credits).toBe(100)
    expect(ledger.rows[0].n).toBe(1)
  }, BOOT_TIMEOUT)

  it('grants a purchase once when concurrent retries use the same session id', async () => {
    if (!available || !db) return
    const { Client } = await import('pg')
    await db.query('delete from credit_grant_refs; delete from credit_ledger; delete from credit_balance;')
    const clients = await Promise.all(Array.from({ length: 8 }, async () => {
      const client = new Client({ connectionString: connectionString() })
      await client.connect()
      return client
    }))
    const results = await Promise.all(clients.map((client) =>
      client.query('select grant_credits($1, $2, $3, $4) as balance', [USER, 100, 'purchase', 'cs_race']),
    ))
    await Promise.all(clients.map((client) => client.end()))
    expect(results.map((result) => result.rows[0].balance)).toEqual(Array(8).fill(100))
    const balance = await db.query('select credits from credit_balance where user_id = $1', [USER])
    const ledger = await db.query("select count(*)::int as n from credit_ledger where stripe_ref = 'cs_race'")
    expect(balance.rows[0].credits).toBe(100)
    expect(ledger.rows[0].n).toBe(1)
  }, BOOT_TIMEOUT)

  it('rejects missing refs and retries with a different owner or amount', async () => {
    if (!available || !db) return
    await db.query('delete from credit_grant_refs; delete from credit_ledger; delete from credit_balance;')
    await expect(db.query('select grant_credits($1, $2, $3, $4)', [USER, 100, 'purchase', null]))
      .rejects.toThrow(/requires a Stripe reference/)
    await db.query('select grant_credits($1, $2, $3, $4)', [USER, 100, 'purchase', 'cs_guard'])
    await expect(db.query('select grant_credits($1, $2, $3, $4)', [USER, 200, 'purchase', 'cs_guard']))
      .rejects.toThrow(/conflicts with its original user or amount/)
    await expect(db.query('select grant_credits($1, $2, $3, $4)', [LEGACY_USER, 100, 'purchase', 'cs_guard']))
      .rejects.toThrow(/conflicts with its original user or amount/)
  }, BOOT_TIMEOUT)

  it('denies browser RPC execution and allows service_role', async () => {
    if (!available || !db) return
    const result = await db.query(`select
      has_function_privilege('anon', 'public.grant_credits(uuid,integer,text,text)', 'EXECUTE') as anon_grant,
      has_function_privilege('authenticated', 'public.grant_credits(uuid,integer,text,text)', 'EXECUTE') as auth_grant,
      has_function_privilege('anon', 'public.consume_credits(uuid,integer,text)', 'EXECUTE') as anon_spend,
      has_function_privilege('authenticated', 'public.consume_credits(uuid,integer,text)', 'EXECUTE') as auth_spend,
      has_function_privilege('service_role', 'public.grant_credits(uuid,integer,text,text)', 'EXECUTE') as service_grant,
      has_function_privilege('service_role', 'public.claim_webhook_event(text,text)', 'EXECUTE') as service_claim`)
    expect(result.rows[0]).toEqual({
      anon_grant: false, auth_grant: false, anon_spend: false, auth_spend: false,
      service_grant: true, service_claim: true,
    })

    for (const role of ['anon', 'authenticated']) {
      await db.query(`set role ${role}`)
      try {
        await expect(db.query('select public.grant_credits($1, 10, $2, $3)', [USER, 'purchase', 'cs_denied']))
          .rejects.toMatchObject({ code: '42501' })
        await expect(db.query('select public.consume_credits($1, 1, $2)', [USER, 'studio']))
          .rejects.toMatchObject({ code: '42501' })
        await expect(db.query("select public.claim_webhook_event('evt_denied', 'test')"))
          .rejects.toMatchObject({ code: '42501' })
        await expect(db.query("select public.mark_webhook_event_failed('evt_denied', 'test')"))
          .rejects.toMatchObject({ code: '42501' })
      } finally {
        await db.query('reset role')
      }
    }
    await db.query('set role service_role')
    try {
      const grant = await db.query('select public.grant_credits($1, 10, $2, $3) as balance', [USER, 'purchase', 'cs_allowed'])
      expect(grant.rows[0].balance).toBeGreaterThanOrEqual(10)
      const claim = await db.query("select public.claim_webhook_event('evt_allowed', 'test') as status")
      expect(claim.rows[0].status).toBe('new')
    } finally {
      await db.query('reset role')
    }
  }, BOOT_TIMEOUT)
})

describe('consume_credits against real Postgres', () => {
  /**
   * Guard against a vacuous pass. Every test below early-returns when the
   * container did not start, which would report green while asserting nothing —
   * the exact "a control that does nothing" failure this suite exists to catch.
   * When Docker IS reachable, a skipped suite is a real failure and must say so.
   */
  it('actually ran against a container (not silently skipped)', async () => {
    let dockerUp = false
    try {
      const { execSync } = await import('node:child_process')
      execSync('docker info', { stdio: 'ignore' })
      dockerUp = true
    } catch {
      dockerUp = false
    }
    if (!dockerUp) {
      if (REVIEW_DATABASE_URL) {
        expect(available, 'review_app PostgreSQL was specified, so migrations must apply').toBe(true)
        return
      }
      console.warn('Docker unavailable — database tests skipped.')
      return
    }
    expect(available, 'Docker is running, so the Postgres container had to start').toBe(true)
    const ping = await db!.query('select current_setting($1) as v', ['server_version'])
    expect(String(ping.rows[0].v)).toMatch(/^16\./)
  }, BOOT_TIMEOUT)

  it('grants, spends, and records the ledger', async () => {
    if (!available || !db) return
    await db.query('delete from credit_grant_refs; delete from credit_ledger; delete from credit_balance;')

    await db.query('select grant_credits($1, $2, $3, $4)', [USER, 100, 'purchase', 'test'])
    const spent = await db.query('select consume_credits($1, $2, $3) as ok', [USER, 30, 'studio'])
    expect(spent.rows[0].ok).toBe(true)

    const bal = await db.query('select credits from credit_balance where user_id = $1', [USER])
    expect(bal.rows[0].credits).toBe(70)

    const led = await db.query('select delta, reason, module_id from credit_ledger order by id')
    expect(led.rows.map((r) => r.delta)).toEqual([100, -30])
    expect(led.rows[1].module_id).toBe('studio')
  }, BOOT_TIMEOUT)

  it('refuses to overspend and leaves the balance untouched', async () => {
    if (!available || !db) return
    await db.query('delete from credit_grant_refs; delete from credit_ledger; delete from credit_balance;')
    await db.query('select grant_credits($1, $2, $3)', [USER, 10, 'signup_bonus'])

    const res = await db.query('select consume_credits($1, $2, $3) as ok', [USER, 999, 'studio'])
    expect(res.rows[0].ok).toBe(false)

    const bal = await db.query('select credits from credit_balance where user_id = $1', [USER])
    expect(bal.rows[0].credits).toBe(10)
  }, BOOT_TIMEOUT)

  it('cannot double-spend under concurrency — the reason FOR UPDATE is there', async () => {
    if (!available || !db) return
    const { Client } = await import('pg')
    await db.query('delete from credit_grant_refs; delete from credit_ledger; delete from credit_balance;')
    await db.query('select grant_credits($1, $2, $3)', [USER, 100, 'signup_bonus'])

    // Ten simultaneous spends of 20 against a balance of 100: exactly five may
    // succeed. Without the row lock, a check-then-decrement would let more
    // through and drive the balance negative.
    const clients = await Promise.all(
      Array.from({ length: 10 }, async () => {
        const c = new Client({ connectionString: connectionString() })
        await c.connect()
        return c
      }),
    )
    const results = await Promise.all(
      clients.map((c) => c.query('select consume_credits($1, $2, $3) as ok', [USER, 20, 'studio'])),
    )
    await Promise.all(clients.map((c) => c.end()))

    const okCount = results.filter((r) => r.rows[0].ok === true).length
    expect(okCount).toBe(5)

    const bal = await db.query('select credits from credit_balance where user_id = $1', [USER])
    expect(bal.rows[0].credits).toBe(0)
  }, BOOT_TIMEOUT)
})

describe('claim_webhook_event against real Postgres', () => {
  /**
   * The bug this migration closes: `app/api/stripe/webhook/route.ts` used to
   * insert the event id and treat any primary-key conflict as "already
   * handled". A first attempt that claimed the row and then failed (a
   * transient DB error, a timeout) left the row behind, so Stripe's retry of
   * that SAME event hit the same conflict and was silently swallowed as a
   * duplicate — the customer paid, the webhook never actually granted
   * credits, and Stripe stopped retrying because the handler answered 200.
   */
  it('claims a never-seen event as new', async () => {
    if (!available || !db) return
    await db.query('delete from webhook_events;')
    const res = await db.query("select claim_webhook_event($1, $2) as outcome", ['evt_1', 'checkout.session.completed'])
    expect(res.rows[0].outcome).toBe('new')
    const row = await db.query('select type from webhook_events where id = $1', ['evt_1'])
    expect(row.rows[0].type).toBe('checkout.session.completed')
  }, BOOT_TIMEOUT)

  it('treats a redelivery of an already-succeeded event as a duplicate', async () => {
    if (!available || !db) return
    await db.query('delete from webhook_events;')
    await db.query("select claim_webhook_event($1, $2)", ['evt_2', 'checkout.session.completed'])
    // evt_2's row still carries the plain event type -- nothing ever marked it
    // failed, so this is a real duplicate delivery of a successful event.
    const res = await db.query("select claim_webhook_event($1, $2) as outcome", ['evt_2', 'checkout.session.completed'])
    expect(res.rows[0].outcome).toBe('duplicate')
  }, BOOT_TIMEOUT)

  it('lets a failed event be retried instead of swallowing it as a duplicate', async () => {
    if (!available || !db) return
    await db.query('delete from webhook_events;')
    await db.query("select claim_webhook_event($1, $2)", ['evt_3', 'checkout.session.completed'])
    await db.query("select mark_webhook_event_failed($1, $2)", ['evt_3', 'checkout.session.completed'])

    const retry = await db.query("select claim_webhook_event($1, $2) as outcome", ['evt_3', 'checkout.session.completed'])
    expect(retry.rows[0].outcome).toBe('retry')

    // The row now reads as a normal claimed event again, exactly as if this
    // were the first attempt -- so a THIRD delivery of the same event (this
    // retry having since succeeded) is correctly a duplicate, not a retry.
    const row = await db.query('select type from webhook_events where id = $1', ['evt_3'])
    expect(row.rows[0].type).toBe('checkout.session.completed')
    const third = await db.query("select claim_webhook_event($1, $2) as outcome", ['evt_3', 'checkout.session.completed'])
    expect(third.rows[0].outcome).toBe('duplicate')
  }, BOOT_TIMEOUT)

  it('lets exactly one concurrent retry of the same failed event win', async () => {
    if (!available || !db) return
    const { Client } = await import('pg')
    await db.query('delete from webhook_events;')
    await db.query("select claim_webhook_event($1, $2)", ['evt_4', 'checkout.session.completed'])
    await db.query("select mark_webhook_event_failed($1, $2)", ['evt_4', 'checkout.session.completed'])

    // Five simultaneous redeliveries of the one failed event: without the
    // row lock inside claim_webhook_event's UPDATE, more than one could read
    // the ':failed' row before any of them committed the reset and all five
    // would return 'retry', reprocessing (and re-granting) the same payment.
    const clients = await Promise.all(
      Array.from({ length: 5 }, async () => {
        const c = new Client({ connectionString: connectionString() })
        await c.connect()
        return c
      }),
    )
    const results = await Promise.all(
      clients.map((c) => c.query("select claim_webhook_event($1, $2) as outcome", ['evt_4', 'checkout.session.completed'])),
    )
    await Promise.all(clients.map((c) => c.end()))

    const outcomes = results.map((r) => r.rows[0].outcome)
    expect(outcomes.filter((o) => o === 'retry')).toHaveLength(1)
    expect(outcomes.filter((o) => o === 'duplicate')).toHaveLength(4)
  }, BOOT_TIMEOUT)
})
