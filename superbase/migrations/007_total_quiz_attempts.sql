-- Run this once in the Supabase SQL editor.
--
-- Adds get_total_quiz_attempts(): a single privacy-safe aggregate (a bare
-- count, nothing per-row or per-identity) for the Forum & Site stats
-- panel's "Total quizzes taken" dial — the third of the three
-- "everybody" tally-counter dials in .sfp-dial-row (js/stats.js
-- pollStatsPanel, index.html #sfpDialQuizzes).
--
-- public.quiz_attempts is deliberately NOT exposed to PostgREST/the browser
-- client for general reads (see 006_quiz_attempts.sql) — every other read
-- or write goes through sync-quiz-attempts.ts's service-role admin client,
-- specifically so "which device can see which identity's attempts" stays
-- logic that lives in one trusted place. This function is a narrow,
-- intentional exception to that: it only ever returns a single count across
-- every identity combined, never any individual attempt's contents (which
-- quiz, which answers, whose device) — same aggregate-only shape as the
-- existing get_unique_participants_count() and get_stats_panel() this panel
-- already polls alongside it, so it doesn't reopen anything 006 was trying
-- to close off.
--
-- No SECURITY DEFINER: runs as whichever role calls it (anon, via the
-- publishable key from the browser), same as get_author_stats
-- (005_author_stats_profile_popup.sql) — a plain aggregate over a table
-- with no RLS enabled needs no elevated privilege to compute.

CREATE OR REPLACE FUNCTION public.get_total_quiz_attempts()
RETURNS bigint
LANGUAGE sql
STABLE
AS $$
  SELECT count(*)::bigint FROM public.quiz_attempts;
$$;

GRANT EXECUTE ON FUNCTION public.get_total_quiz_attempts() TO anon, authenticated;
