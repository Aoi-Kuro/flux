-- Fixes the client-side twin of the bug edit-message.ts already had fixed
-- server-side: js/forum.js decided whether to show the ✎ edit button (vs.
-- the ⚑ flag button) using
--
--   msg.device_id === getForumDeviceId() || (message's author_name matches
--   this device's currently-claimed nickname)
--
-- That first clause is a literal, permanent device_id match — the exact
-- same live-join-adjacent mistake 004_fix_author_identity_resolution.sql
-- fixed for author display, and the same one edit-message.ts's ownership
-- check was fixed for a few migrations ago. Since a device's local
-- device_id never rotates (not even on Exit), that clause kept lighting up
-- the edit button on every message the physical device had EVER posted,
-- under every identity it had ever claimed and since dropped — the button
-- just failed silently on submit (edit-message.ts correctly rejects it),
-- but showing it at all is still wrong and confusing.
--
-- The client can't fix this on its own — forum_messages_public never
-- exposed identity_id, only the human-readable author_name (COALESCE(
-- i.nickname, m.author_name), see 004) — so there's no way for js/forum.js
-- to tell "this message has an owning identity, and it isn't me" apart from
-- "this message has no identity at all, and I posted it". This migration
-- adds that column; js/forum.js's isOwn check is updated separately to
-- stop using the literal device_id fallback whenever msg.identity_id is
-- set, mirroring edit-message.ts's own fix exactly.
--
-- Nothing else about the view changes — every other column is copied
-- verbatim from 004's definition (which is still the live one; 011/012
-- only touched get_stats_panel, not this view).

-- create-or-replace-view requires every existing column to keep its exact
-- name AND position — Postgres reads a changed position as a rename, which
-- is exactly the 42P16 error this migration hit when identity_id was first
-- inserted right after device_id. Appending it at the very end instead
-- keeps every other column untouched.
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
  COALESCE(pi.nickname, pm.author_name) as reply_to_author_name,
  m.identity_id
from
  public.forum_messages m
  left join public.identities i on i.id = m.identity_id
  left join public.forum_messages pm on pm.id = m.reply_to_id
  left join public.identities pi on pi.id = pm.identity_id;
