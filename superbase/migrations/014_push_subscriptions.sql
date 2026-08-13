-- Push notification subscriptions for forum @mentions — lets a browser
-- register a Web Push PushSubscription so a Supabase Edge Function can wake
-- it up with a real OS-level notification even when no tab is open, the
-- same way any other push-enabled site does (see save-push-subscription.ts
-- and the new push-sending step at the end of post-message.ts).
--
-- Keyed by device_id (always present, see FORUM_DEVICE_ID_KEY in forum.js)
-- and, once claimed, identity_id — the same identity_devices link
-- post-message.ts already resolves before every post. A push is only ever
-- sent to identity_id, not device_id: an unclaimed free-text name has no
-- stable identity to notify, since nobody "owns" it across devices or even
-- across two people typing the same name.
--
-- endpoint is unique: re-subscribing the same browser (e.g. after clearing
-- notification permission and re-granting it) just updates the existing
-- row via upsert instead of accumulating duplicates that would each get a
-- separate push for the same mention.
create table if not exists public.push_subscriptions (
  id bigint generated always as identity primary key,
  device_id uuid not null,
  identity_id uuid references public.identities(id) on delete cascade,
  endpoint text not null unique,
  p256dh text not null,
  auth text not null,
  created_at timestamp with time zone not null default now()
);

create index if not exists push_subscriptions_identity_idx on public.push_subscriptions (identity_id);
create index if not exists push_subscriptions_device_idx on public.push_subscriptions (device_id);

-- No direct client access, in either direction: subscriptions are written
-- only by save-push-subscription.ts and read only by post-message.ts, both
-- via the admin client (same pattern forum_messages writes already use).
-- RLS with zero policies blocks the publishable key from touching this
-- table at all — a push subscription's keys are sensitive enough (they let
-- you push arbitrary notifications to that browser) that they shouldn't be
-- readable even by their own owner's client, let alone anyone else's.
alter table public.push_subscriptions enable row level security;
