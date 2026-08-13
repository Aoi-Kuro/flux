// Edge Function: delete-quiz-attempt
//
// Deploy as "delete-quiz-attempt". Auth mode: "publishable", same as
// sync-quiz-attempts. "Verify JWT with legacy secret" OFF.
//
// Fills the gap noted in QUIZ_ATTEMPTS_SYNC_NOTES.md ("No delete-from-
// server"): deleteAttempt() in js/stats.js used to only remove the local
// copy, so a synced attempt would reappear on the next sync. This deletes
// the row server-side too, scoped to the resolved identity — a device can
// only delete attempts belonging to its own linked identity, never an
// arbitrary hash, same trust model sync-quiz-attempts.ts already uses for
// device_id -> identity_id resolution.

import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { withSupabase } from "jsr:@supabase/server@^1";

export default {
  fetch: withSupabase({ auth: "publishable" }, async (req, ctx) => {
    const payload = await req.json();
    const { device_id, attempt_hash } = payload ?? {};

    if (typeof device_id !== "string" || !/^[0-9a-f-]{36}$/i.test(device_id)) {
      return Response.json({ ok: false, error: "Invalid device id." }, { status: 400 });
    }
    if (typeof attempt_hash !== "string" || attempt_hash.length === 0 || attempt_hash.length > 128) {
      return Response.json({ ok: false, error: "Invalid attempt hash." }, { status: 400 });
    }

    const admin = ctx.supabaseAdmin;

    const { data: link, error: linkErr } = await admin
      .from("identity_devices")
      .select("identity_id")
      .eq("device_id", device_id)
      .maybeSingle();

    if (linkErr) {
      console.error("Identity link lookup error:", linkErr);
      return Response.json({ ok: false, error: "Couldn't verify your identity, try again." }, { status: 500 });
    }
    if (!link) {
      return Response.json({ ok: false, error: "no_identity", message: "Claim a name first." }, { status: 403 });
    }

    // Scoped to identity_id, not just attempt_hash — a device can only ever
    // delete its own identity's attempts, never someone else's by guessing
    // a hash.
    const { error: delErr } = await admin
      .from("quiz_attempts")
      .delete()
      .eq("attempt_hash", attempt_hash)
      .eq("identity_id", link.identity_id);

    if (delErr) {
      console.error("Quiz attempt delete error:", delErr);
      return Response.json({ ok: false, error: "Couldn't delete, try again." }, { status: 500 });
    }

    return Response.json({ ok: true });
  }),
};
