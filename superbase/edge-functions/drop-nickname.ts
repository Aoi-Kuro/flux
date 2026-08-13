// Edge Function: drop-nickname (v4 — exit-only, "drop everywhere" removed)
//
// Deploy as the "drop-nickname" Edge Function (replace the existing one).
// Same auth mode as the others: "publishable", "Verify JWT with legacy
// secret" OFF.
//
// The client no longer offers a "drop everywhere" button — PIN + Change +
// Exit covered everything Drop did, minus the destructive delete-for-
// everyone part, so it was cut. This function now does exactly one thing:
//
//   { device_id, action: "exit" }
//     Unlinks ONLY the calling device from its identity (deletes its one
//     row in identity_devices). The identity itself, its nickname, its PIN,
//     and every OTHER device still linked to it are completely untouched.
//     No PIN required — this can only ever affect the device that's asking,
//     the same way signing out doesn't need your password on top of
//     already being logged in. Coming back later is just claim-nickname
//     with the nickname + PIN again.
//
// `action` is still required and must be exactly "exit" — kept as an
// explicit field (rather than just trusting the endpoint name) so a client
// bug that calls this without meaning to fails loudly instead of silently
// unlinking a device. If "drop everywhere" ever needs to come back, restore
// it from git history rather than re-adding it here from scratch — the PIN
// verification, throttling, and identities-cascade-delete logic was already
// worked out once.

import { withSupabase } from 'npm:@supabase/server@^1';

function isUuid(v: unknown): v is string {
  return typeof v === 'string' &&
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(v);
}

export default {
  fetch: withSupabase({ auth: 'publishable' }, async (req, ctx) => {
    if (req.method !== 'POST') {
      return Response.json({ ok: false, error: 'method_not_allowed' }, { status: 405 });
    }

    let payload: any;
    try {
      payload = await req.json();
    } catch {
      return Response.json({ ok: false, error: 'bad_json' }, { status: 400 });
    }

    const deviceId: string = payload?.device_id;
    const action: string = payload?.action;

    if (!isUuid(deviceId)) {
      return Response.json({ ok: false, error: 'invalid_device_id' }, { status: 400 });
    }
    if (action !== 'exit') {
      return Response.json({ ok: false, error: 'invalid_action' }, { status: 400 });
    }

    const db = ctx.supabaseAdmin;

    const { data: link, error: linkErr } = await db
      .from('identity_devices')
      .select('identity_id')
      .eq('device_id', deviceId)
      .maybeSingle();
    if (linkErr) {
      console.error('drop-nickname: link lookup error', linkErr);
      return Response.json({ ok: false, error: 'server_error' }, { status: 500 });
    }
    if (!link) {
      return Response.json({ ok: false, error: 'not_found' }, { status: 404 });
    }

    const { error: unlinkErr } = await db
      .from('identity_devices')
      .delete()
      .eq('device_id', deviceId);
    if (unlinkErr) {
      console.error('drop-nickname: exit/unlink error', unlinkErr);
      return Response.json({ ok: false, error: 'server_error' }, { status: 500 });
    }

    return Response.json({ ok: true, exited: true });
  }),
};