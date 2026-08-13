-- post-message.ts's rate-limit check (edge-functions/post-message.ts) now
-- queries "most recent message" filtered by identity_id when the poster has
-- a claimed identity, and by device_id otherwise (previously device_id
-- only — see that file's comment for why). Both are `ORDER BY id DESC
-- LIMIT 1` lookups, so give each its own composite index rather than
-- letting either fall back to a sequential scan as the table grows.

create index if not exists forum_messages_identity_id_id_idx
  on public.forum_messages (identity_id, id desc);

create index if not exists forum_messages_device_id_id_idx
  on public.forum_messages (device_id, id desc);
