-- ============================================================
-- ScholarGrid — Complete Supabase Setup
-- Run this ENTIRE file in your Supabase SQL Editor (one time)
-- Go to: https://supabase.com/dashboard → Your Project → SQL Editor → New Query → Paste this → Run
-- ============================================================

-- =====================
-- 1. TABLES
-- =====================

-- Profiles (extends auth.users)
CREATE TABLE public.profiles (
  id           uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email        text NOT NULL UNIQUE,
  full_name    text,
  avatar_url   text,
  role         text NOT NULL DEFAULT 'student' CHECK (role IN ('student','admin')),
  about        text,
  points       integer NOT NULL DEFAULT 0,
  warnings     integer NOT NULL DEFAULT 0,
  is_banned    boolean NOT NULL DEFAULT false,
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_profiles_role         ON public.profiles(role);
CREATE INDEX idx_profiles_points_desc  ON public.profiles(points DESC);

-- Groups
CREATE TABLE public.groups (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name         text NOT NULL,
  description  text,
  join_code    text NOT NULL UNIQUE,
  created_by   uuid NOT NULL REFERENCES public.profiles(id),
  created_at   timestamptz NOT NULL DEFAULT now()
);

-- Group Members (many-to-many)
CREATE TABLE public.group_members (
  group_id   uuid NOT NULL REFERENCES public.groups(id)   ON DELETE CASCADE,
  user_id    uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  joined_at  timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (group_id, user_id)
);

-- Messages (chat)
CREATE TABLE public.messages (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  group_id    uuid NOT NULL REFERENCES public.groups(id)   ON DELETE CASCADE,
  sender_id   uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  content     text,
  file_url    text,
  file_name   text,
  file_type   text,
  created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_messages_group_time ON public.messages(group_id, created_at DESC);

-- Notes
CREATE TABLE public.notes (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  uploader_id  uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  title        text NOT NULL,
  description  text,
  subject      text NOT NULL,
  file_url     text NOT NULL,
  file_name    text NOT NULL,
  file_type    text NOT NULL,
  file_size    bigint,
  is_flagged   boolean NOT NULL DEFAULT false,
  is_approved  boolean NOT NULL DEFAULT true,
  downloads    integer NOT NULL DEFAULT 0,
  created_at   timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_notes_subject    ON public.notes(subject);
CREATE INDEX idx_notes_uploader   ON public.notes(uploader_id);
CREATE INDEX idx_notes_flagged    ON public.notes(is_flagged);

-- Leaderboard Points (event log)
CREATE TABLE public.leaderboard_points (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  points        integer NOT NULL,
  reason        text NOT NULL CHECK (reason IN (
                  'note_upload','note_download','login_streak',
                  'admin_bonus','penalty')),
  reference_id  uuid,
  created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_points_user_time ON public.leaderboard_points(user_id, created_at DESC);

-- Complaints
CREATE TABLE public.complaints (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id   uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  title        text NOT NULL,
  description  text NOT NULL,
  status       text NOT NULL DEFAULT 'open'
               CHECK (status IN ('open','in_progress','resolved','rejected')),
  admin_reply  text,
  resolved_by  uuid REFERENCES public.profiles(id),
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now()
);


-- =====================
-- 2. TRIGGERS
-- =====================

-- Auto-create profile when user signs up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, role, created_at)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    COALESCE(NEW.raw_user_meta_data->>'role', 'student'),
    NOW()
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SET search_path = public;

CREATE TRIGGER trg_profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER trg_complaints_updated_at
  BEFORE UPDATE ON public.complaints
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Award 10 points when a note is uploaded
CREATE OR REPLACE FUNCTION public.award_points_on_note_upload()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.leaderboard_points (user_id, points, reason, reference_id)
  VALUES (NEW.uploader_id, 10, 'note_upload', NEW.id);

  UPDATE public.profiles
  SET points = points + 10
  WHERE id = NEW.uploader_id;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE TRIGGER trg_award_points_note_upload
  AFTER INSERT ON public.notes
  FOR EACH ROW EXECUTE FUNCTION public.award_points_on_note_upload();


-- =====================
-- 3. ROW LEVEL SECURITY (RLS)
-- =====================

-- Profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can read profiles"      ON public.profiles FOR SELECT USING (true);
CREATE POLICY "Users update own profile"      ON public.profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Admin can update any profile"  ON public.profiles FOR UPDATE USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- Groups
ALTER TABLE public.groups ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Members can read groups" ON public.groups FOR SELECT USING (
  EXISTS (SELECT 1 FROM public.group_members WHERE group_id = id AND user_id = auth.uid())
  OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);
CREATE POLICY "Admins manage groups" ON public.groups FOR ALL USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- Group Members
ALTER TABLE public.group_members ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Members read own membership" ON public.group_members FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Students join groups"        ON public.group_members FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "Admins manage membership"    ON public.group_members FOR ALL USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- Messages
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Group members read messages" ON public.messages FOR SELECT USING (
  EXISTS (SELECT 1 FROM public.group_members WHERE group_id = messages.group_id AND user_id = auth.uid())
);
CREATE POLICY "Group members send messages" ON public.messages FOR INSERT WITH CHECK (
  sender_id = auth.uid() AND
  EXISTS (SELECT 1 FROM public.group_members WHERE group_id = messages.group_id AND user_id = auth.uid())
);
CREATE POLICY "Admins read all messages" ON public.messages FOR SELECT USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- Notes
ALTER TABLE public.notes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "All users read approved notes"  ON public.notes FOR SELECT USING (is_approved = true AND is_flagged = false);
CREATE POLICY "Students upload notes"          ON public.notes FOR INSERT WITH CHECK (uploader_id = auth.uid());
CREATE POLICY "Uploaders delete own notes"     ON public.notes FOR DELETE USING (uploader_id = auth.uid());
CREATE POLICY "Admins manage all notes"        ON public.notes FOR ALL USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- Leaderboard Points
ALTER TABLE public.leaderboard_points ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users read own points"   ON public.leaderboard_points FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Admins read all points"  ON public.leaderboard_points FOR SELECT USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- Complaints
ALTER TABLE public.complaints ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Students read own complaints"  ON public.complaints FOR SELECT USING (student_id = auth.uid());
CREATE POLICY "Students create complaints"    ON public.complaints FOR INSERT WITH CHECK (student_id = auth.uid());
CREATE POLICY "Admins manage complaints"      ON public.complaints FOR ALL USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);


-- =====================
-- 4. STORAGE BUCKETS
-- =====================

-- Avatars (public)
INSERT INTO storage.buckets (id, name, public) VALUES ('avatars', 'avatars', true);
CREATE POLICY "Public read avatars"
  ON storage.objects FOR SELECT USING (
    bucket_id = 'avatars' AND auth.role() = 'authenticated'
  );
CREATE POLICY "Owner uploads avatar"
  ON storage.objects FOR INSERT WITH CHECK (
    bucket_id = 'avatars' AND auth.uid()::text = (storage.foldername(name))[1]
  );
CREATE POLICY "Owner deletes avatar"
  ON storage.objects FOR DELETE USING (
    bucket_id = 'avatars' AND auth.uid()::text = (storage.foldername(name))[1]
  );

-- Notes files (private)
INSERT INTO storage.buckets (id, name, public) VALUES ('notes-files', 'notes-files', false);
CREATE POLICY "Authenticated users download notes"
  ON storage.objects FOR SELECT USING (
    bucket_id = 'notes-files' AND auth.role() = 'authenticated'
  );
CREATE POLICY "Owner uploads note file"
  ON storage.objects FOR INSERT WITH CHECK (
    bucket_id = 'notes-files' AND auth.uid()::text = (storage.foldername(name))[1]
  );
CREATE POLICY "Owner or admin deletes note file"
  ON storage.objects FOR DELETE USING (
    bucket_id = 'notes-files' AND (
      auth.uid()::text = (storage.foldername(name))[1]
      OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    )
  );

-- Chat files (private)
INSERT INTO storage.buckets (id, name, public) VALUES ('chat-files', 'chat-files', false);
CREATE POLICY "Group members download chat files"
  ON storage.objects FOR SELECT USING (
    bucket_id = 'chat-files' AND auth.role() = 'authenticated'
  );
CREATE POLICY "Group members upload chat files"
  ON storage.objects FOR INSERT WITH CHECK (
    bucket_id = 'chat-files' AND auth.role() = 'authenticated'
  );


-- =====================
-- 5. REALTIME
-- =====================

ALTER PUBLICATION supabase_realtime ADD TABLE public.messages;
ALTER PUBLICATION supabase_realtime ADD TABLE public.complaints;
ALTER PUBLICATION supabase_realtime ADD TABLE public.profiles;


-- ============================================================
-- DONE! Your database is ready.
-- Now go to your .env file and add your Supabase URL + anon key.
-- ============================================================
