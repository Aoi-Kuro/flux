-- Fixes "my total messages" in the stats panel being frozen when switching
-- accounts on the same device.
--
-- get_stats_panel's my_total_messages counted
--   forum_messages WHERE device_id = p_device_id
-- — the raw device column, which never changes no matter which identity is
-- currently linked to that device. This is the exact same bug
-- 004_fix_author_identity_resolution.sql already fixed for message
-- display/avatars, just missed here: identity_devices.device_id is a
-- primary key (one device -> one identity AT A TIME, see 004's header
-- comment and claim-nickname.ts's "LINK/SWITCH DEVICE" case), and switching
-- accounts just repoints that row — it never touches the device_id already
-- stamped on old forum_messages rows.
--
-- Fix: resolve this device's CURRENT identity via identity_devices first,
-- then count forum_messages by identity_id (the same column
-- forum_messages_public/004 already joins on for correct authorship) —
-- falling back to a raw device_id count only for devices with no linked
-- identity at all (never claimed a nickname), where identity_id is
-- meaningless. This also fixes a second latent bug for free: an identity
-- linked to multiple devices (phone + PC) now has its messages summed
-- across all of them, instead of only counting whichever device is asking.
--
-- Nothing else about this function changes — joined_at,
-- total_participants, total_unique_participants, and total_visits are
-- copied verbatim from the live definition.
--
-- Confirmed against the person's own live definition (Aug 6 2026).

CREATE OR REPLACE FUNCTION public.get_stats_panel(p_device_id uuid)
RETURNS TABLE (
  joined_at                  timestamptz,
  my_total_messages          bigint,
  total_participants         bigint,
  total_unique_participants  bigint,
  total_visits               bigint
)
LANGUAGE sql
STABLE
AS $$
  select
    (
      select i.created_at
      from identity_devices d
      join identities i on i.id = d.identity_id
      where d.device_id = p_device_id
    ) as joined_at,
    (
      -- This device's current identity (if any) counts every message ever
      -- posted under that identity_id, from ANY of its linked devices.
      -- No linked identity (never claimed a nickname on this device) falls
      -- back to the old raw device_id count, since there's no identity_id
      -- to key on yet.
      select count(*)
      from forum_messages fm
      where fm.identity_id = (
        select d.identity_id from identity_devices d where d.device_id = p_device_id
      )
      or (
        not exists (select 1 from identity_devices d where d.device_id = p_device_id)
        and fm.device_id = p_device_id
      )
    ) as my_total_messages,
    (select count(*) from identities)                                   as total_participants,
    (
      -- Every unique device ever seen (site_device_sightings), but a
      -- device linked to a registered identity (identity_devices)
      -- collapses to that identity_id instead of counting itself — so
      -- several devices under the same nickname count once.
      -- identity_devices.device_id is a primary key, so this join can
      -- never fan out (at most one identity_devices row per device).
      select count(distinct coalesce(d.identity_id::text, s.device_id::text))
      from site_device_sightings s
      left join identity_devices d on d.device_id = s.device_id
    ) as total_unique_participants,
    (select count(*) from site_visits) as total_visits;
$$;

GRANT EXECUTE ON FUNCTION public.get_stats_panel(uuid) TO anon, authenticated;
