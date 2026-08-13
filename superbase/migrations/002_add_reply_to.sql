ALTER TABLE public.forum_messages
  ADD COLUMN IF NOT EXISTS reply_to_id bigint REFERENCES public.forum_messages(id);

create or replace view public.forum_messages_public as
select
  m.id,
  m.created_at,
  m.device_id,
  m.body,
  m.scope,
  m.problem_key,
  COALESCE(i.nickname, m.author_name) as author_name,
  m.flag_status,
  m.flag_reason,
  m.edited_at,
  i.avatar_svg,
  m.reply_to_id,
  pm.body as reply_to_body,
  pm.flag_status as reply_to_flag_status,
  COALESCE(pi.nickname, pm.author_name) as reply_to_author_name
from
  forum_messages m
  left join identity_devices d on d.device_id = m.device_id
  left join identities i on i.id = d.identity_id
  left join forum_messages pm on pm.id = m.reply_to_id
  left join identity_devices pd on pd.device_id = pm.device_id
  left join identities pi on pi.id = pd.identity_id;
