-- Fixes a real bug, not a cosmetic one: forum_messages_public previously
-- resolved a message's author identity via a LIVE join through
-- identity_devices (device_id -> identity_id), re-evaluated on every read.
-- identity_devices.device_id is a primary key — one device can only ever
-- point to ONE identity at a time — so that join actually answers "who owns
-- this device_id RIGHT NOW", not "who posted this message". Two concrete
-- breakages from that:
--   1. Exiting a device deletes its identity_devices row -> the join finds
--      nothing -> that device's past messages lose their avatar/color.
--   2. Claiming a NEW nickname on that same (now-unlinked) device overwrites
--      the identity_devices row -> every past message ever posted from that
--      device_id now resolves to the NEW identity, retroactively.
--
-- Fix: store identity_id directly on forum_messages at insert time (a
-- snapshot of whoever was actually posting), and join on THAT instead.
-- Renaming an identity still retroactively updates all its own past
-- messages as intended, since identity_id itself never changes on rename —
-- only nickname/avatar_svg on the identities row do.

alter table public.forum_messages
  add column if not exists identity_id uuid references public.identities(id);

-- Best-effort one-time backfill: attribute each existing message to
-- whichever identity currently owns its device_id. This is only an
-- approximation for any message whose device has since been reclaimed by a
-- different identity (exactly the bug being fixed) — true historical
-- authorship for those can't be recovered — but it's the best available
-- guess for everything else, and does no harm going forward since all new
-- rows get the correct value written directly by post-message.ts.
update public.forum_messages m
set identity_id = d.identity_id
from public.identity_devices d
where d.device_id = m.device_id
  and m.identity_id is null;

create or replace view public.forum_messages_public as
select
  m.id,
  m.created_at,
  m.device_id,
  m.body,
  m.scope,
  m.problem_key,
  COALESCE(i.nickname, m.author_name) as author_name,
  m.flag_status,
  m.flag_reason,
  m.edited_at,
  i.avatar_svg,
  m.reply_to_id,
  pm.body as reply_to_body,
  pm.flag_status as reply_to_flag_status,
  COALESCE(pi.nickname, pm.author_name) as reply_to_author_name
from
  public.forum_messages m
  left join public.identities i on i.id = m.identity_id
  left join public.forum_messages pm on pm.id = m.reply_to_id
  left join public.identities pi on pi.id = pm.identity_id;