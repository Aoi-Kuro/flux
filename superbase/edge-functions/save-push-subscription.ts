// Setup type definitions for built-in Supabase Runtime APIs
import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { withSupabase } from "jsr:@supabase/server@^1";

interface SubscribePayload {
  action: "subscribe" | "unsubscribe";
  device_id: string;
  endpoint?: string;
  keys?: { p256dh: string; auth: string };
}

export default {
  fetch: withSupabase({ auth: "publishable" }, async (req, ctx) => {
    const payload: SubscribePayload = await req.json();
    const { action, device_id, endpoint, keys } = payload ?? {};

    // ctx.supabaseAdmin bypasses RLS — push_subscriptions has zero client
    // policies (see migration 014), so this is the only client that can
    // touch this table at all.
    const admin = ctx.supabaseAdmin;

    if (typeof device_id !== "string" || !/^[0-9a-f-]{36}$/i.test(device_id)) {
      return Response.json({ ok: false, error: "Invalid device id." }, { status: 400 });
    }
    if (typeof endpoint !== "string" || !endpoint.startsWith("https://")) {
      return Response.json({ ok: false, error: "Invalid subscription endpoint." }, { status: 400 });
    }

    if (action === "unsubscribe") {
      // Scoped to device_id too, not just endpoint, so one device can't
      // drop a subscription it doesn't own even if it somehow knew the
      // endpoint string (it's not secret, just unique).
      const { error } = await admin
        .from("push_subscriptions")
        .delete()
        .eq("endpoint", endpoint)
        .eq("device_id", device_id);
      if (error) {
        console.error("Push unsubscribe error:", error);
        return Response.json({ ok: false, error: "Couldn't remove subscription." }, { status: 500 });
      }
      return Response.json({ ok: true });
    }

    if (action !== "subscribe") {
      return Response.json({ ok: false, error: "Invalid action." }, { status: 400 });
    }
    if (!keys || typeof keys.p256dh !== "string" || typeof keys.auth !== "string") {
      return Response.json({ ok: false, error: "Missing subscription keys." }, { status: 400 });
    }

    // Resolve this device's claimed identity, if any — same identity_devices
    // lookup post-message.ts runs before every post, so a subscription
    // always follows whichever identity is actually claimed on this device
    // right now, and updates automatically the next time this endpoint
    // re-subscribes under a different claim.
    const { data: link, error: linkErr } = await admin
      .from("identity_devices")
      .select("identity_id")
      .eq("device_id", device_id)
      .maybeSingle();
    if (linkErr) console.error("Identity link lookup error (push subscribe):", linkErr);

    const { error: upsertErr } = await admin.from("push_subscriptions").upsert(
      {
        device_id,
        identity_id: link?.identity_id ?? null,
        endpoint,
        p256dh: keys.p256dh,
        auth: keys.auth,
      },
      { onConflict: "endpoint" }
    );

    if (upsertErr) {
      console.error("Push subscribe error:", upsertErr);
      return Response.json({ ok: false, error: "Couldn't save subscription." }, { status: 500 });
    }
    return Response.json({ ok: true });
  }),
};
