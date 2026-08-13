-- Run this once in the Supabase SQL editor. Adds avatar_svg and
-- last_message_at to get_author_stats' return columns, for the mention
-- profile popup's bigger avatar + "Last message" line (js/forum.js,
-- openForumMentionProfile / loadForumMentionProfile).
--
-- Confirmed against the person's own live definition (Aug 2 2026):
--
--   select
--     count(*)::bigint      as total_messages,
--     min(created_at)        as first_message_at
--   from public.forum_messages_public
--   where author_name ilike p_author_name;
--
-- Same source table (forum_messages_public) and same ILIKE match, no
-- flag_status filter — so this is a straight column addition, nothing else
-- changes about which messages get counted.
--
-- Postgres won't let CREATE OR REPLACE FUNCTION widen a RETURNS TABLE
-- column list (errors with 42P13, "cannot change return type of existing
-- function") — the old one has to be dropped first, hence the DROP below
-- before the CREATE. DROP wipes any GRANT on the function, so the explicit
-- GRANT EXECUTE at the end restores public/anon access — get_author_stats
-- is called straight from the browser via client.rpc(...) with the
-- publishable key, same as every other RPC this forum uses (no
-- SECURITY DEFINER, no server-side trust). Plain SQL functions default to
-- PUBLIC EXECUTE on creation anyway, so this is likely redundant with that
-- default, but explicit here so a restrictive dashboard-level setting (if
-- one exists) doesn't silently survive the drop as "no grant at all."

DROP FUNCTION IF EXISTS public.get_author_stats(text);

CREATE FUNCTION public.get_author_stats(p_author_name text)
RETURNS TABLE (
  total_messages    bigint,
  first_message_at  timestamptz,
  last_message_at   timestamptz,
  avatar_svg        text
)
LANGUAGE sql
STABLE
AS $$
  SELECT
    count(*)                                                                    AS total_messages,
    min(fm.created_at)                                                          AS first_message_at,
    max(fm.created_at)                                                          AS last_message_at,
    (array_agg(fm.avatar_svg ORDER BY fm.created_at DESC) FILTER (WHERE fm.avatar_svg IS NOT NULL))[1] AS avatar_svg
  FROM public.forum_messages_public fm
  WHERE fm.author_name ILIKE p_author_name;
$$;

-- Why forum_messages_public and not raw forum_messages: that view already
-- resolves avatar_svg live from the identities join (a rename retroactively
-- updates the avatar shown on every past message, no bulk update needed —
-- see the avatar_svg comments in js/forum.js), so picking the most recent
-- non-null avatar_svg for this name gets their CURRENT avatar, which is
-- what the popup should show — not whatever avatar_svg happened to be
-- stored on their very first message.

GRANT EXECUTE ON FUNCTION public.get_author_stats(text) TO anon, authenticated;
