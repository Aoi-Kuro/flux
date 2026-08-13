// ── Supabase project config ──────────────────────────────────────────────────
// The publishable key is designed to be public — it only grants what Row
// Level Security policies on the database allow (currently: read-only SELECT
// on forum_messages). This is the client-side equivalent of the old "anon"
// key, just under Supabase's newer key format (sb_publishable_...).
//
// The secret key (sb_secret_...) must NEVER go in this file, or anywhere in
// this repo. It only ever lives inside a Supabase Edge Function's server-side
// secrets, which we'll wire up when we build the write/moderation path.
const SUPABASE_URL = 'https://eammcjjsjyvmbjsloxpz.supabase.co';
const SUPABASE_PUBLISHABLE_KEY = 'sb_publishable_NjZjecxc0iP1JnPSk5cJWQ_qllgCF7P';
