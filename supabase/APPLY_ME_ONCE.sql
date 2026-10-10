-- ════════════════════════════════════════════════════════════════════════════
-- OMNEX FACTORY — PASTE THIS ONCE into the Supabase SQL Editor, then press RUN.
--   Dashboard → SQL Editor → New query → paste all → Run
--
-- Part 1 creates exec_migration() for later migrations. Parts 2–6 mirror
-- migrations 001–005 so a first-time SQL Editor install has current billing
-- grants, webhook retry handling, RPC privileges, and purchase idempotency.
-- Safe to re-run: table/function setup is idempotent; purchase backfill is keyed.
-- ════════════════════════════════════════════════════════════════════════════

-- ── Part 1: migration runner ───────────────────────────────────────────────
create or replace function exec_migration(sql text)
returns text
language plpgsql
security definer
set search_path = public
as $fn$
begin
  execute sql;
  return 'ok';
end;
$fn$;

revoke all on function exec_migration(text) from public, anon, authenticated;

-- ── Part 2: factory core ───────────────────────────────────────────────────
-- Migration 001: OMNEX Factory core
--
-- The shared spine every module runs on: one user profile, ONE credit balance,
-- an auditable ledger, and per-module usage events.
--
-- The `module_id` dimension is the thing OMNEX never had: the old platform
-- scoped everything by user_id only, so it could never answer "which product
-- makes money". Every credit spend and every usage event carries a module_id.
--
-- Patterns deliberately reused from the proven live OMNEX schema:
--   * consume_credits()  ← migration 013 consume_run(): SELECT ... FOR UPDATE row
--     lock so two concurrent requests can never double-spend the same credits.
--   * webhook_events     ← migration 014: Stripe idempotency via primary-key
--     conflict, so a redelivered event can never grant credits twice.
--   * RLS `auth.uid() = user_id` on every user-scoped table (service role bypasses).

create extension if not exists pgcrypto;

-- ── Profiles ────────────────────────────────────────────────────────────────
create table if not exists public.profiles (
  id                 uuid primary key references auth.users(id) on delete cascade,
  email              text,
  full_name          text,
  stripe_customer_id text,
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now()
);

alter table public.profiles enable row level security;
drop policy if exists "profiles_owner_select" on public.profiles;
create policy "profiles_owner_select" on public.profiles
  for select to authenticated using (auth.uid() = id);
drop policy if exists "profiles_owner_update" on public.profiles;
create policy "profiles_owner_update" on public.profiles
  for update to authenticated using (auth.uid() = id);

-- ── Credit balance (one balance, spendable across every module) ─────────────
create table if not exists public.credit_balance (
  user_id    uuid primary key references auth.users(id) on delete cascade,
  credits    integer not null default 0 check (credits >= 0),
  updated_at timestamptz not null default now()
);

alter table public.credit_balance enable row level security;
drop policy if exists "credit_balance_owner" on public.credit_balance;
create policy "credit_balance_owner" on public.credit_balance
  for select to authenticated using (auth.uid() = user_id);
-- writes are service-role only (via consume_credits / grant_credits)

-- ── Ledger: every grant and every spend, auditable ──────────────────────────
create table if not exists public.credit_ledger (
  id         bigserial primary key,
  user_id    uuid not null references auth.users(id) on delete cascade,
  delta      integer not null,          -- +granted / -spent
  reason     text not null,             -- 'purchase' | 'signup_bonus' | 'spend' | 'refund'
  module_id  text,                      -- which module spent it (null for grants)
  stripe_ref text,                      -- checkout session / invoice id for grants
  created_at timestamptz not null default now()
);

create index if not exists idx_credit_ledger_user on public.credit_ledger (user_id, created_at desc);
create index if not exists idx_credit_ledger_module on public.credit_ledger (module_id, created_at desc);

alter table public.credit_ledger enable row level security;
drop policy if exists "credit_ledger_owner" on public.credit_ledger;
create policy "credit_ledger_owner" on public.credit_ledger
  for select to authenticated using (auth.uid() = user_id);

-- ── Usage events: per-module analytics + revenue attribution ────────────────
create table if not exists public.usage_events (
  id         bigserial primary key,
  user_id    uuid references auth.users(id) on delete set null,
  module_id  text not null,
  action     text not null,             -- e.g. 'generate'
  credits    integer not null default 0,
  ok         boolean not null default true,
  meta       jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_usage_events_module on public.usage_events (module_id, created_at desc);
create index if not exists idx_usage_events_user on public.usage_events (user_id, created_at desc);

alter table public.usage_events enable row level security;
drop policy if exists "usage_events_owner" on public.usage_events;
create policy "usage_events_owner" on public.usage_events
  for select to authenticated using (auth.uid() = user_id);

-- ── Stripe webhook idempotency (migration 014 pattern) ─────────────────────
create table if not exists public.webhook_events (
  id          text primary key,          -- Stripe event.id
  type        text,
  received_at timestamptz not null default now()
);

alter table public.webhook_events enable row level security;
-- service-role only; no client policy = default deny.

-- ── Atomic spend (migration 013 consume_run pattern) ───────────────────────
-- Locks the balance row, verifies sufficient credits, decrements, and writes the
-- ledger line in ONE transaction. Returns false when the balance is insufficient
-- so the caller can 402 without having charged anything.
create or replace function consume_credits(
  p_user_id uuid,
  p_amount  integer,
  p_module  text
) returns boolean
language plpgsql
security definer
as $$
declare
  v_credits integer;
begin
  if p_amount <= 0 then
    return true;                       -- nothing to charge
  end if;

  select credits into v_credits
  from public.credit_balance
  where user_id = p_user_id
  for update;                          -- row lock closes the double-spend race

  if v_credits is null or v_credits < p_amount then
    return false;
  end if;

  update public.credit_balance
  set credits = credits - p_amount, updated_at = now()
  where user_id = p_user_id;

  insert into public.credit_ledger (user_id, delta, reason, module_id)
  values (p_user_id, -p_amount, 'spend', p_module);

  return true;
end;
$$;

-- ── Grant credits (purchase / bonus / refund) ──────────────────────────────
create or replace function grant_credits(
  p_user_id uuid,
  p_amount  integer,
  p_reason  text default 'purchase',
  p_ref     text default null
) returns integer
language plpgsql
security definer
as $$
declare
  v_new integer;
begin
  insert into public.credit_balance (user_id, credits)
  values (p_user_id, greatest(p_amount, 0))
  on conflict (user_id) do update
    set credits = public.credit_balance.credits + greatest(p_amount, 0),
        updated_at = now()
  returning credits into v_new;

  insert into public.credit_ledger (user_id, delta, reason, stripe_ref)
  values (p_user_id, p_amount, p_reason, p_ref);

  return v_new;
end;
$$;

-- ── New user: profile + starter credits so the product can be TRIED ────────
create or replace function handle_new_factory_user()
returns trigger
language plpgsql
security definer
as $$
begin
  insert into public.profiles (id, email, full_name)
  values (new.id, new.email, new.raw_user_meta_data->>'full_name')
  on conflict (id) do nothing;

  insert into public.credit_balance (user_id, credits)
  values (new.id, 20)                  -- enough for 2 Ad Studio generations
  on conflict (user_id) do nothing;

  insert into public.credit_ledger (user_id, delta, reason)
  values (new.id, 20, 'signup_bonus');

  return new;
end;
$$;

drop trigger if exists on_auth_user_created_factory on auth.users;
create trigger on_auth_user_created_factory
  after insert on auth.users
  for each row execute function handle_new_factory_user();

-- ── Part 3: migration 002 (lead intake) ───────────────────────────────────
-- Leads from the public portfolio brief form.
--
-- RLS is on with NO public select policy: an anonymous visitor may insert their own
-- enquiry and read nothing back. Without that, the brief form would double as a
-- customer-list endpoint for anyone who found the anon key.

create table if not exists public.leads (
  id            uuid primary key default gen_random_uuid(),
  created_at    timestamptz not null default now(),
  source        text not null default 'portfolio',
  name          text,
  email         text not null,
  company       text,
  brand_site    text,
  -- Kept as free text rather than an enum: the options on the form will change
  -- faster than a migration should.
  budget        text,
  timeline      text,
  brief         text,
  -- Scored later by the qualification step; null means "not yet scored".
  score         int,
  stage         text not null default 'new',
  meta          jsonb not null default '{}'::jsonb
);

create index if not exists leads_created_at_idx on public.leads (created_at desc);
create index if not exists leads_stage_idx on public.leads (stage);

alter table public.leads enable row level security;

-- Insert-only for anonymous visitors. Service-role bypasses RLS for the owner view.
drop policy if exists leads_public_insert on public.leads;
create policy leads_public_insert
  on public.leads for insert
  to anon, authenticated
  with check (true);


-- ── Part 4: migration 003 (retryable webhook claims) ─────────────────────
-- Migration 003: webhook idempotency that survives a failed first attempt.
--
-- Migration 001's `webhook_events` idempotency gate inserts the event id
-- BEFORE processing, so two concurrent deliveries of the same event can never
-- both pass a check-then-act race. That is correct for closing the duplicate
-- race, but it has a second, unintended effect: Stripe retries a webhook on
-- any non-2xx response, and a retry of an event whose FIRST attempt failed
-- (a transient DB error, a timeout, anything after the row was claimed) hits
-- the same primary-key conflict and is silently treated as "already handled"
-- -- even though nothing was ever granted. A customer who paid and hit that
-- window would never receive their credits, and Stripe would stop retrying
-- because the handler answered 200. That is the exact failure §9 (Credit /
-- Billing Integrity) names: "nepotvrđenog settlementa" that looks settled.
--
-- `claim_webhook_event()` distinguishes three outcomes instead of one boolean:
--   'new'       — never seen; caller processes and marks success or failure.
--   'retry'     — a PRIOR attempt at this exact event failed; this caller now
--                 owns the retry and must process it again.
--   'duplicate' — already succeeded, or another request currently owns it.
--
-- The insert-then-conditional-update happens inside ONE function so the
-- atomicity is a property of the database, not of application code: two
-- concurrent retries of the same failed event race on the UPDATE's row lock
-- the same way `consume_credits`' `FOR UPDATE` already does, and only one can
-- win. A mock cannot prove this; only a real Postgres constraint violation
-- and a real concurrent UPDATE can, which is why this is tested in
-- `credits.db.test.ts` against a container, not with a fake client.
create or replace function claim_webhook_event(
  p_id   text,
  p_type text
) returns text
language plpgsql
as $$
begin
  insert into public.webhook_events (id, type) values (p_id, p_type);
  return 'new';
exception when unique_violation then
  update public.webhook_events
  set type = p_type
  where id = p_id and type = p_type || ':failed';

  if found then
    return 'retry';
  end if;
  return 'duplicate';
end;
$$;

-- Marks a claimed event as failed so a later redelivery of the SAME event id
-- is eligible for `claim_webhook_event` to return 'retry' rather than
-- 'duplicate'. Never touches a row this call did not itself just fail to
-- finish processing -- the caller only invokes it inside its own error path.
create or replace function mark_webhook_event_failed(
  p_id   text,
  p_type text
) returns void
language plpgsql
as $$
begin
  update public.webhook_events set type = p_type || ':failed' where id = p_id;
end;
$$;


-- ── Part 5: migration 004 (RPC privileges) ────────────────────────────────
-- Security boundary for service-role RPCs. PostgreSQL grants EXECUTE on new
-- functions to PUBLIC by default; these functions accept target user ids.
-- Keep financial mutations and webhook claims inaccessible to browser roles.

alter function public.consume_credits(uuid, integer, text)
  set search_path = public, pg_temp;
alter function public.grant_credits(uuid, integer, text, text)
  set search_path = public, pg_temp;
alter function public.handle_new_factory_user()
  set search_path = public, pg_temp;
alter function public.claim_webhook_event(text, text)
  set search_path = public, pg_temp;
alter function public.mark_webhook_event_failed(text, text)
  set search_path = public, pg_temp;

revoke all on function public.consume_credits(uuid, integer, text)
  from public, anon, authenticated;
revoke all on function public.grant_credits(uuid, integer, text, text)
  from public, anon, authenticated;
revoke all on function public.handle_new_factory_user()
  from public, anon, authenticated;
revoke all on function public.claim_webhook_event(text, text)
  from public, anon, authenticated;
revoke all on function public.mark_webhook_event_failed(text, text)
  from public, anon, authenticated;

grant execute on function public.consume_credits(uuid, integer, text)
  to service_role;
grant execute on function public.grant_credits(uuid, integer, text, text)
  to service_role;
grant execute on function public.claim_webhook_event(text, text)
  to service_role;
grant execute on function public.mark_webhook_event_failed(text, text)
  to service_role;

-- These webhook functions run as the caller, so EXECUTE alone is insufficient.
grant select, insert, update on public.webhook_events to service_role;


-- ── Part 6: migration 005 (purchase grant idempotency) ────────────────────
-- Apply while billing RPC and webhook workers are quiesced. The ledger backfill
-- and function replacement must not race an in-flight legacy grant.
BEGIN;

-- Make Stripe credit grants safe across webhook retries, including the case
-- where Postgres committed the grant but the HTTP response was lost.
create table if not exists public.credit_grant_refs (
  stripe_ref text primary key check (length(btrim(stripe_ref)) > 0),
  user_id uuid not null references auth.users(id) on delete cascade,
  amount integer not null check (amount > 0),
  created_at timestamptz not null default now()
);

alter table public.credit_grant_refs enable row level security;
revoke all on public.credit_grant_refs from public, anon, authenticated;
grant all on public.credit_grant_refs to service_role;

-- Seed the idempotency keys from grants already in the append-only ledger.
-- Fail closed if the old data cannot establish one unambiguous owner and pack
-- amount per Stripe session. Inspect and reconcile ledger/balances before
-- retrying a failed migration; do not delete audit rows to bypass this check.
do $$
begin
  if exists (
    select 1 from public.credit_ledger
    where reason = 'purchase'
      and (nullif(btrim(stripe_ref), '') is null or stripe_ref <> btrim(stripe_ref))
  ) then
    raise exception 'purchase ledger has rows without a usable Stripe reference; resolve before applying migration 005';
  end if;

  if exists (
    select stripe_ref
    from public.credit_ledger
    where reason = 'purchase' and stripe_ref is not null
    group by stripe_ref
    having count(distinct user_id) > 1 or count(distinct delta) > 1 or min(delta) <= 0
  ) then
    raise exception 'purchase ledger has conflicting owner or amount for a Stripe reference';
  end if;
end;
$$;

insert into public.credit_grant_refs (stripe_ref, user_id, amount)
select stripe_ref, min(user_id::text)::uuid, min(delta)
from public.credit_ledger
where reason = 'purchase' and stripe_ref is not null
group by stripe_ref
on conflict (stripe_ref) do nothing;

create or replace function public.grant_credits(
  p_user_id uuid,
  p_amount integer,
  p_reason text default 'purchase',
  p_ref text default null
) returns integer
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  v_new integer;
  v_ref text := nullif(btrim(p_ref), '');
  v_ref_user uuid;
  v_ref_amount integer;
begin
  if p_amount <= 0 then
    raise exception 'credit grant amount must be positive';
  end if;

  if p_reason = 'purchase' then
    if v_ref is null then
      raise exception 'purchase credit grant requires a Stripe reference';
    end if;

    -- The ref claim and credit mutation share this transaction. A duplicate
    -- waits for the original insert to commit, then sees its owner and amount.
    insert into public.credit_grant_refs (stripe_ref, user_id, amount)
    values (v_ref, p_user_id, p_amount)
    on conflict (stripe_ref) do nothing;

    if not found then
      select user_id, amount into v_ref_user, v_ref_amount
      from public.credit_grant_refs
      where stripe_ref = v_ref;
      if v_ref_user is distinct from p_user_id or v_ref_amount is distinct from p_amount then
        raise exception 'purchase reference conflicts with its original user or amount';
      end if;
      select credits into v_new
      from public.credit_balance
      where user_id = p_user_id;
      if v_new is null then
        raise exception 'purchase reference exists without a credit balance';
      end if;
      return v_new;
    end if;
  end if;

  insert into public.credit_balance (user_id, credits)
  values (p_user_id, p_amount)
  on conflict (user_id) do update
    set credits = public.credit_balance.credits + p_amount,
        updated_at = now()
  returning credits into v_new;

  insert into public.credit_ledger (user_id, delta, reason, stripe_ref)
  values (p_user_id, p_amount, p_reason, v_ref);

  return v_new;
end;
$$;

-- CREATE OR REPLACE preserves ACLs, but repeat the boundary here so migration
-- 005 remains safe if installed independently after the privilege migration.
revoke all on function public.grant_credits(uuid, integer, text, text)
  from public, anon, authenticated;
grant execute on function public.grant_credits(uuid, integer, text, text)
  to service_role;

COMMIT;






-- ── Part 7: refresh PostgREST after all tables and RPC grants ─────────────
notify pgrst, 'reload schema';
