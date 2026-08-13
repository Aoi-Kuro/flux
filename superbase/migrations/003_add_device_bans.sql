create table if not exists public.device_bans (
  device_id uuid primary key,
  flag_count integer not null default 0,
  window_started_at timestamptz,
  ban_level integer not null default 0,
  banned_until timestamptz,
  updated_at timestamptz not null default now()
);