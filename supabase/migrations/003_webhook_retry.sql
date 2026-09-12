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
