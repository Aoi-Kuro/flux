-- Run this once in the Supabase SQL editor before deploying the updated
-- claim-nickname Edge Function or frontend.

-- 1. New column: raw DiceBear identicon SVG, generated once per claim/rename
--    by claim-nickname.ts. NULL until that first claim/rename happens after
--    this migration runs (existing identities get one lazily on their next
--    rename — there's no backfill here).
ALTER TABLE public.identities
  ADD COLUMN IF NOT EXISTS avatar_svg text;

-- 2. Expose it through forum_messages_public, same as author_name already
--    is, so a rename's new avatar shows up on every past message
--    immediately with no bulk update needed.
--
--    !!! This file does NOT know the exact current definition of
--    forum_messages_public (it isn't checked into this repo — it was
--    created directly in the SQL editor). Find it via Supabase Dashboard
--    → Database → Views → forum_messages_public → "Definition", copy that
--    CREATE VIEW statement, and add `identities.avatar_svg` to its SELECT
--    list (it already JOINs identities to resolve author_name, so this is
--    just one more column off the same join — no new JOIN needed). Then
--    run it here as CREATE OR REPLACE VIEW.
