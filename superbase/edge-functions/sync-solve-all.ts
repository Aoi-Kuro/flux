// Edge Function: sync-solve-all
//
// Deploy as "sync-solve-all". Auth mode: "publishable". "Verify JWT with
// legacy secret" OFF — same conventions as sync-quiz-attempts.ts and
// delete-quiz-attempt.ts.
//
// Handles all three actions the client needs for one solve-all session
// (one quiz_num + cumulative combo) in a single function, keyed the same
// device_id -> identity_devices -> identity_id way as the quiz-attempts
// functions:
//   - "pull":  return the stored row's data (or null if none/reset).
//   - "push":  upsert the client's already-merged snapshot.
//   - "reset": upsert data:null — a *tombstone*, not a delete. A bare
//     missing row can't be told apart from "this device never synced,"
//     but a row that exists with data:null unambiguously means "this was
//     reset since you last synced" — see js/solve-all-sync.js's pull
//     handling for why that distinction matters.
//
// solve_all_progress has RLS enabled with zero policies, same reasoning as
// quiz_attempts (see superbase/migrations/006_quiz_attempts.sql) — it's
// only ever reachable through this SECURITY DEFINER-equivalent (service
// role) path, never a direct client query.

import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { withSupabase } from "jsr:@supabase/server@^1";

export default {
  fetch: withSupabase({ auth: "publishable" }, async (req, ctx) => {
    const payload = await req.json();
    const { device_id, quiz_num, cumulative, action, data } = payload ?? {};

    if (typeof device_id !== "string" || !/^[0-9a-f-]{36}$/i.test(device_id)) {
      return Response.json({ ok: false, error: "Invalid device id." }, { status: 400 });
    }
    if (!Number.isInteger(quiz_num) || quiz_num < 1 || quiz_num > 999) {
      return Response.json({ ok: false, error: "Invalid quiz number." }, { status: 400 });
    }
    if (!["pull", "push", "reset"].includes(action)) {
      return Response.json({ ok: false, error: "Invalid action." }, { status: 400 });
    }

    const admin = ctx.supabaseAdmin;
    const cum = !!cumulative;

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

    if (action === "pull") {
      const { data: row, error } = await admin
        .from("solve_all_progress")
        .select("data")
        .eq("identity_id", link.identity_id)
        .eq("quiz_num", quiz_num)
        .eq("cumulative", cum)
        .maybeSingle();
      if (error) {
        console.error("Solve-all pull error:", error);
        return Response.json({ ok: false, error: "Couldn't fetch, try again." }, { status: 500 });
      }
      return Response.json({ ok: true, found: !!row, data: row ? row.data : null });
    }

    if (action === "push") {
      if (typeof data !== "object" || data === null) {
        return Response.json({ ok: false, error: "Missing progress data." }, { status: 400 });
      }
      const { error } = await admin
        .from("solve_all_progress")
        .upsert(
          {
            identity_id: link.identity_id,
            quiz_num,
            cumulative: cum,
            data,
            updated_at: new Date().toISOString(),
          },
          { onConflict: "identity_id,quiz_num,cumulative" },
        );
      if (error) {
        console.error("Solve-all push error:", error);
        return Response.json({ ok: false, error: "Couldn't save, try again." }, { status: 500 });
      }
      return Response.json({ ok: true });
    }

    // action === "reset"
    const { error } = await admin
      .from("solve_all_progress")
      .upsert(
        {
          identity_id: link.identity_id,
          quiz_num,
          cumulative: cum,
          data: null,
          updated_at: new Date().toISOString(),
        },
        { onConflict: "identity_id,quiz_num,cumulative" },
      );
    if (error) {
      console.error("Solve-all reset error:", error);
      return Response.json({ ok: false, error: "Couldn't reset, try again." }, { status: 500 });
    }
    return Response.json({ ok: true });
  }),
};
