-- Run this once in the Supabase SQL editor.
--
-- Stores solve-all mode progress (one row per identity + quiz_num +
-- cumulative-mode combo) so it syncs across every device linked to a
-- claimed forum identity. See superbase/edge-functions/sync-solve-all.ts
-- for how this is read/written — same "no RLS policy, service-role Edge
-- Function only" pattern as quiz_attempts (006_quiz_attempts.sql).
--
-- `data` holds the same shape js/quiz-engine.js already saves to
-- localStorage: {order, checkedById, lockedIds, answersById}. It's
-- nullable on purpose: NULL means "explicitly reset," which is different
-- from no row existing at all ("never synced from any device"). That
-- distinction is what lets a reset on one device actually clear a stale,
-- still-populated local copy on another — see sync-solve-all.ts's "reset"
-- action and js/solve-all-sync.js's pull handling.

CREATE TABLE IF NOT EXISTS public.solve_all_progress (
  identity_id  uuid NOT NULL REFERENCES public.identities(id),
  quiz_num     smallint NOT NULL CHECK (quiz_num BETWEEN 1 AND 4),
  cumulative   boolean NOT NULL DEFAULT false,
  data         jsonb,
  updated_at   timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (identity_id, quiz_num, cumulative)
);

ALTER TABLE public.solve_all_progress ENABLE ROW LEVEL SECURITY;
-- No policies defined — deliberately unreachable except through the
-- service-role admin client in sync-solve-all.ts.
