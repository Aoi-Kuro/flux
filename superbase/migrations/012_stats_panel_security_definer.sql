-- Root-causes and fixes ALL of the stats panel's wrong numbers at once —
-- not just my_total_messages.
--
-- get_stats_panel was never SECURITY DEFINER, so it always ran as anon
-- (the browser's publishable key), same trap 008's header comment already
-- documents for get_total_quiz_attempts/get_my_total_quiz_attempts:
-- RLS-enabled-with-zero-policies means anon sees ZERO ROWS, silently, not
-- an error. That's why the panel was returning 0/"Not registered yet" for
-- EVERY number that touches identities/identity_devices — joined_at, the
-- identity resolution behind my_total_messages, and total_participants —
-- and, going by the screenshots, total_visits and total_unique_participants
-- too (site_visits/site_device_sightings are apparently under the same
-- restriction). forum_messages itself must NOT have this restriction
-- (011's raw device_id fallback did return real, if wrong, numbers), which
-- is why messages looked "differently broken" rather than "just zero" like
-- everything else.
--
-- Also, per explicit request: my_total_messages no longer falls back to a
-- raw device_id count for a device with no linked identity. That fallback
-- was only ever a stand-in for "we can't resolve who this is" — now that
-- SECURITY DEFINER actually lets the identity resolve correctly, a
-- genuinely unclaimed device gets NULL (js/stats.js renders this as "—"),
-- not a number that was never a real "your messages" figure to begin with.

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
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
  select
    (
      select i.created_at
      from identity_devices d
      join identities i on i.id = d.identity_id
      where d.device_id = p_device_id
    ) as joined_at,
    (
      -- NULL means this device has never claimed a nickname (no
      -- identity_devices row) — deliberately distinct from a real
      -- registered identity that just happens to have posted 0 messages.
      -- The outer scalar subquery is driven by identity_devices itself so
      -- it naturally evaluates to NULL when that lookup finds nothing,
      -- rather than count(*) silently reporting 0 either way.
      select (select count(*) from forum_messages fm where fm.identity_id = idev.identity_id)
      from identity_devices idev
      where idev.device_id = p_device_id
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
