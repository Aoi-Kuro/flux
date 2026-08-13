-- Run this once in the Supabase SQL editor.
--
-- Fixes two problems with "Total quizzes taken" / "My total quizzes taken"
-- (js/stats.js pollStatsPanel, index.html .sfp-dial-row):
--
-- 1. get_total_quiz_attempts() (007_total_quiz_attempts.sql) always returns
--    0. It's not SECURITY DEFINER, so it runs as whichever role calls it —
--    anon, from the browser's publishable key. quiz_attempts has RLS
--    enabled with zero policies (006_quiz_attempts.sql, deliberately —
--    every read/write is meant to go through sync-quiz-attempts.ts's
--    service-role admin client instead). RLS-with-no-policies means anon
--    sees zero rows, full stop — not "sometimes", always. 007's own comment
--    ("a plain aggregate over a table with no RLS enabled needs no elevated
--    privilege") was simply wrong about 006's table having no RLS.
--
-- 2. Both numbers were derived from *current* row counts (count(*) on
--    quiz_attempts server-side, loadStats().length client-side), so
--    deleting an attempt silently decremented them. The request was for
--    simple ever-incrementing counters instead — "how many times has a
--    quiz been completed, ever" — unaffected by later deletions.
--
-- Fix for both: real counters, incremented by a trigger that only fires on
-- genuine INSERTs (Postgres does NOT fire AFTER INSERT triggers for rows
-- skipped by ON CONFLICT DO NOTHING — sync-quiz-attempts.ts's upsert already
-- relies on that same behavior for its own dedup, so this piggybacks on
-- exactly one correctly-defined "this attempt is genuinely new" signal
-- instead of re-deriving it), and never decremented anywhere (no matching
-- AFTER DELETE trigger exists, on purpose).

-- Single-row global counter. Deliberately its own table with NO grants to
-- anon/authenticated at all (not even SELECT) — only the SECURITY DEFINER
-- function below can touch it, same "narrow trusted exception" reasoning
-- 007 already used for the count it was trying to expose.
CREATE TABLE IF NOT EXISTS public.quiz_attempts_counter (
  id smallint PRIMARY KEY DEFAULT 1,
  total_ever bigint NOT NULL DEFAULT 0,
  CONSTRAINT quiz_attempts_counter_singleton CHECK (id = 1)
);
INSERT INTO public.quiz_attempts_counter (id, total_ever)
  VALUES (1, (SELECT count(*) FROM public.quiz_attempts)) -- seed with today's real count, so this migration doesn't reset everyone back to 0
  ON CONFLICT (id) DO NOTHING;

-- Per-identity ever-counter, alongside the existing avatar_svg/nickname
-- columns 001_add_avatar_svg.sql added the same way.
ALTER TABLE public.identities
  ADD COLUMN IF NOT EXISTS total_quiz_attempts_ever bigint NOT NULL DEFAULT 0;
-- Seed it too, same reasoning as the global counter above — otherwise
-- everyone's existing attempts silently "don't count" the moment this runs.
UPDATE public.identities i
  SET total_quiz_attempts_ever = sub.cnt
  FROM (SELECT identity_id, count(*) AS cnt FROM public.quiz_attempts GROUP BY identity_id) sub
  WHERE i.id = sub.identity_id AND i.total_quiz_attempts_ever = 0;

CREATE OR REPLACE FUNCTION public._quiz_attempts_increment_counters()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
  UPDATE public.quiz_attempts_counter SET total_ever = total_ever + 1 WHERE id = 1;
  UPDATE public.identities SET total_quiz_attempts_ever = total_quiz_attempts_ever + 1 WHERE id = NEW.identity_id;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS quiz_attempts_increment_counters ON public.quiz_attempts;
CREATE TRIGGER quiz_attempts_increment_counters
  AFTER INSERT ON public.quiz_attempts
  FOR EACH ROW
  EXECUTE FUNCTION public._quiz_attempts_increment_counters();

-- Replaces 007's version — same name/signature (safe to CREATE OR REPLACE,
-- no return-type change this time, unlike the get_author_stats situation
-- that needed a DROP first), now reading the persistent counter instead of
-- count(*), and SECURITY DEFINER so it actually bypasses RLS instead of
-- silently returning 0 for anon.
CREATE OR REPLACE FUNCTION public.get_total_quiz_attempts()
RETURNS bigint
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
  SELECT total_ever FROM public.quiz_attempts_counter WHERE id = 1;
$$;
GRANT EXECUTE ON FUNCTION public.get_total_quiz_attempts() TO anon, authenticated;

-- New: "my total quizzes taken", resolved from device_id the same way
-- sync-quiz-attempts.ts resolves identity (identity_devices lookup) rather
-- than trusting a client-sent identity_id. Returns 0 (not an error) for a
-- device with no claimed identity yet, since js/stats.js's updateSfpMyQuizzes
-- should be able to call this unconditionally without special-casing "not
-- registered yet" itself.
CREATE OR REPLACE FUNCTION public.get_my_total_quiz_attempts(p_device_id uuid)
RETURNS bigint
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
  v_identity_id uuid;
  v_count bigint;
BEGIN
  SELECT identity_id INTO v_identity_id FROM public.identity_devices WHERE device_id = p_device_id;
  IF v_identity_id IS NULL THEN
    RETURN 0;
  END IF;
  SELECT total_quiz_attempts_ever INTO v_count FROM public.identities WHERE id = v_identity_id;
  RETURN COALESCE(v_count, 0);
END;
$$;
GRANT EXECUTE ON FUNCTION public.get_my_total_quiz_attempts(uuid) TO anon, authenticated;
