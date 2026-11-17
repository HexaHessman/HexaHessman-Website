-- HexaHessman CMS: run this whole file once in Supabase (SQL Editor > New query > paste > Run).
-- Safe to run again: it only adds what is missing.
--
-- The owner (signs in with hexahessman@gmail.com) is set below.
--
-- Roles
--   owner   everything, including team accounts
--   editor  words, photos and publishing

-- 1. Team ---------------------------------------------------------------------------------
create table if not exists cms_users (
  email text primary key,
  name  text,
  role  text not null default 'editor' check (role in ('owner', 'editor')),
  added_at timestamptz default now()
);

insert into cms_users (email, name, role) values (lower('hexahessman@gmail.com'), 'Owner', 'owner')
on conflict (email) do update set role = 'owner';

create or replace function cms_role() returns text
language sql stable security definer set search_path = public as $$
  select role from cms_users where lower(email) = lower(auth.email());
$$;
create or replace function cms_is_editor() returns boolean
language sql stable security definer set search_path = public as $$ select cms_role() is not null; $$;
create or replace function cms_is_owner() returns boolean
language sql stable security definer set search_path = public as $$ select cms_role() = 'owner'; $$;

-- 2. Content --------------------------------------------------------------------------------
-- One row per change. o = the original words (or the original photo path), t = what replaces them,
-- scope = '*' for everywhere they appear, or a page address such as '/about/' for that page only.
create table if not exists cms_edits (
  id bigint generated always as identity primary key,
  kind text not null default 'text' check (kind in ('text', 'image')),
  o text not null,
  t text not null,
  scope text not null default '*',
  page text,                                 -- the page it was changed from (for the activity list)
  updated_at timestamptz default now(),
  updated_by text,
  unique (kind, o, scope)
);

-- every save, so a change can be looked back on and undone
create table if not exists cms_history (
  id bigint generated always as identity primary key,
  kind text not null,
  o text not null,
  scope text not null,
  page text,
  before text,
  after text,                                -- null when the change was undone
  at timestamptz default now(),
  by text
);
create index if not exists cms_history_at on cms_history (at desc);

-- photos uploaded through the admin (the files themselves are in the "media" storage bucket)
create table if not exists cms_media (
  path text primary key,
  url text not null,
  name text,
  created_at timestamptz default now(),
  created_by text
);

-- publish requests and finished publishes
create table if not exists cms_publishes (
  id bigint generated always as identity primary key,
  requested_by text,
  status text not null default 'queued',     -- queued | done | failed
  edits int,
  created_at timestamptz default now()
);

-- 3. Security: only people on the team can read or change anything ----------------------------
alter table cms_users enable row level security;
alter table cms_edits enable row level security;
alter table cms_history enable row level security;
alter table cms_media enable row level security;
alter table cms_publishes enable row level security;

do $$ declare r record; begin
  for r in select policyname, tablename from pg_policies where schemaname = 'public' and tablename like 'cms_%' loop
    execute format('drop policy if exists %I on %I', r.policyname, r.tablename);
  end loop;
end $$;

create policy "team reads team" on cms_users for select to authenticated using (cms_is_editor());
create policy "owner manages team" on cms_users for all to authenticated using (cms_is_owner()) with check (cms_is_owner());
create policy "team edits" on cms_edits for all to authenticated using (cms_is_editor()) with check (cms_is_editor());
create policy "team history" on cms_history for all to authenticated using (cms_is_editor()) with check (cms_is_editor());
create policy "team media" on cms_media for all to authenticated using (cms_is_editor()) with check (cms_is_editor());
create policy "team publishes" on cms_publishes for all to authenticated using (cms_is_editor()) with check (cms_is_editor());

-- 4. Photo storage ---------------------------------------------------------------------------
insert into storage.buckets (id, name, public) values ('media', 'media', true)
on conflict (id) do update set public = true;
drop policy if exists "public read media" on storage.objects;
create policy "public read media" on storage.objects for select using (bucket_id = 'media');
drop policy if exists "editors write media" on storage.objects;
create policy "editors write media" on storage.objects for insert to authenticated with check (bucket_id = 'media' and cms_is_editor());
drop policy if exists "editors update media" on storage.objects;
create policy "editors update media" on storage.objects for update to authenticated using (bucket_id = 'media' and cms_is_editor());
drop policy if exists "editors delete media" on storage.objects;
create policy "editors delete media" on storage.objects for delete to authenticated using (bucket_id = 'media' and cms_is_editor());
