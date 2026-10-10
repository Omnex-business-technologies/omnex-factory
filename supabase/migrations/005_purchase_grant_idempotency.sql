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
