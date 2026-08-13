-- Run this once in the Supabase SQL editor.
--
-- Stores Random 6 quiz attempts (single + cumulative mode) so stats sync
-- across every device linked to a claimed forum identity, replacing the old
-- localStorage-only + encrypted-export-file approach. See
-- superbase/edge-functions/sync-quiz-attempts.ts for how this table is
-- actually read/written — it's NOT exposed to PostgREST/the browser client
-- directly (no RLS policy is defined here, deliberately): every read and
-- write goes through that one Edge Function, which uses the service-role
-- admin client, same pattern post-message.ts already uses for
-- forum_messages. That keeps "which device can read/write which identity's
-- attempts" logic in one trusted place instead of trying to express it as
-- an RLS policy.
--
-- attempt_hash is the whole dedup mechanism: it's computed client-side
-- (js/attempts-sync.js, SHA-256 over quiz_num+mode+attempted_at+identity+
-- score+answers) and is UNIQUE here. Re-uploading an attempt that's already
-- present (e.g. syncing the same device twice, or two devices racing to
-- upload the same attempt) is a harmless no-op via ON CONFLICT DO NOTHING
-- in the Edge Function, rather than needing any client-side "have I already
-- sent this one" bookkeeping beyond the hash itself.

CREATE TABLE IF NOT EXISTS public.quiz_attempts (
  id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  attempt_hash     text NOT NULL UNIQUE,
  identity_id      uuid NOT NULL REFERENCES public.identities(id),
  device_id        uuid NOT NULL,
  quiz_num         smallint NOT NULL CHECK (quiz_num BETWEEN 1 AND 4),
  mode             text NOT NULL CHECK (mode IN ('single', 'cumulative')),
  duration_seconds integer NOT NULL DEFAULT 0,
  score            numeric NOT NULL,
  max_score        numeric NOT NULL,
  -- One entry per problem: {"problem_id": "P11", "quiz_num": 1,
  -- "entered_value": "3.2e-8", "entered_unit": "N/C", "points": 1}.
  -- quiz_num is per-problem (not just the top-level column) because a
  -- cumulative attempt on Quiz 3 pulls in problems from Quizzes 1-2 too —
  -- the review screen needs to know which quiz's data file each problem
  -- actually came from to look its statement back up.
  answers          jsonb NOT NULL DEFAULT '[]'::jsonb,
  -- When the attempt was actually completed (client clock) — this is what
  -- the "Date & Time" column shows, so an attempt synced hours or days
  -- late still sorts and displays at the moment it really happened, not
  -- when it happened to reach the server.
  attempted_at     timestamptz NOT NULL,
  synced_at        timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS quiz_attempts_identity_id_idx ON public.quiz_attempts(identity_id);
