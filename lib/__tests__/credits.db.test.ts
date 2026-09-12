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

/** The migration minus the pieces that need Supabase's auth schema. */
function migrationSql(): string {
  const sql = readFileSync(resolve(process.cwd(), 'supabase/migrations/001_factory_core.sql'), 'utf8')
  return sql
    // `auth.users` and `auth.uid()` only exist inside Supabase.
    .replace(/references auth\.users\(id\) on delete (cascade|set null)/g, '')
    .replace(/^\s*alter table [\s\S]*?enable row level security;$/gm, '')
    .replace(/^\s*drop policy[\s\S]*?;$/gm, '')
    .replace(/create policy[\s\S]*?;\s*$/gm, '')
    // The signup trigger fires on auth.users, which this container does not have.
    .replace(/create or replace function handle_new_factory_user\(\)[\s\S]*?\$\$;/m, '')
    .replace(/drop trigger if exists on_auth_user_created_factory[\s\S]*?;/m, '')
    .replace(/create trigger on_auth_user_created_factory[\s\S]*?;/m, '')
}

/** Migration 003 references nothing Supabase-only, so it needs no stripping. */
function webhookRetryMigrationSql(): string {
  return readFileSync(resolve(process.cwd(), 'supabase/migrations/003_webhook_retry.sql'), 'utf8')
}

beforeAll(async () => {
  try {
    const { PostgreSqlContainer } = await import('@testcontainers/postgresql')
    const { Client } = await import('pg')
    // pgvector image: the real schema declares vector columns elsewhere, and using
    // the same base as production keeps this from passing on a laxer engine.
    container = await new PostgreSqlContainer('pgvector/pgvector:pg16').start()
    db = new Client({ connectionString: container.getConnectionUri() })
    await db.connect()
    await db.query(migrationSql())
    await db.query(webhookRetryMigrationSql())
    available = true
  } catch {
    available = false
  }
}, BOOT_TIMEOUT)

afterAll(async () => {
  await db?.end().catch(() => {})
  await container?.stop().catch(() => {})
})

const USER = '11111111-1111-1111-1111-111111111111'

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
      console.warn('Docker unavailable — database tests skipped.')
      return
    }
    expect(available, 'Docker is running, so the Postgres container had to start').toBe(true)
    const ping = await db!.query('select current_setting($1) as v', ['server_version'])
    expect(String(ping.rows[0].v)).toMatch(/^16\./)
  }, BOOT_TIMEOUT)

  it('grants, spends, and records the ledger', async () => {
    if (!available || !db) return
    await db.query('delete from credit_ledger; delete from credit_balance;')

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
    await db.query('delete from credit_ledger; delete from credit_balance;')
    await db.query('select grant_credits($1, $2)', [USER, 10])

    const res = await db.query('select consume_credits($1, $2, $3) as ok', [USER, 999, 'studio'])
    expect(res.rows[0].ok).toBe(false)

    const bal = await db.query('select credits from credit_balance where user_id = $1', [USER])
    expect(bal.rows[0].credits).toBe(10)
  }, BOOT_TIMEOUT)

  it('cannot double-spend under concurrency — the reason FOR UPDATE is there', async () => {
    if (!available || !db) return
    const { Client } = await import('pg')
    await db.query('delete from credit_ledger; delete from credit_balance;')
    await db.query('select grant_credits($1, $2)', [USER, 100])

    // Ten simultaneous spends of 20 against a balance of 100: exactly five may
    // succeed. Without the row lock, a check-then-decrement would let more
    // through and drive the balance negative.
    const clients = await Promise.all(
      Array.from({ length: 10 }, async () => {
        const c = new Client({ connectionString: container!.getConnectionUri() })
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
        const c = new Client({ connectionString: container!.getConnectionUri() })
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
