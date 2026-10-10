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
