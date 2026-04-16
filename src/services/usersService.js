import { supabase } from '../lib/supabaseClient';

/**
 * Fetch all students (admin view).
 */
export async function fetchAllStudents() {
  const { data, error } = await supabase
    .from('profiles')
    .select('*')
    .eq('role', 'student')
    .order('created_at', { ascending: false });

  if (error) throw error;

  return (data || []).map(mapUser);
}

/**
 * Fetch all users including admins.
 */
export async function fetchAllUsers() {
  const { data, error } = await supabase
    .from('profiles')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) throw error;
  return (data || []).map(mapUser);
}

/**
 * Warn a user — increment warnings count.
 */
export async function warnUser(userId) {
  // First get current warnings
  const { data: profile } = await supabase
    .from('profiles')
    .select('warnings')
    .eq('id', userId)
    .single();

  const { error } = await supabase
    .from('profiles')
    .update({ warnings: (profile?.warnings || 0) + 1 })
    .eq('id', userId);

  if (error) throw error;
}

/**
 * Ban or unban a user.
 */
export async function banUser(userId, banned) {
  const { error } = await supabase
    .from('profiles')
    .update({ is_banned: banned })
    .eq('id', userId);

  if (error) throw error;
}

/**
 * Update a user's profile.
 */
export async function updateUserProfile(userId, updates) {
  const dbUpdates = {};
  if (updates.full_name !== undefined) dbUpdates.full_name = updates.full_name;
  if (updates.about !== undefined) dbUpdates.about = updates.about;
  if (updates.avatar_url !== undefined) dbUpdates.avatar_url = updates.avatar_url;
  if (updates.points !== undefined) dbUpdates.points = updates.points;

  const { error } = await supabase
    .from('profiles')
    .update(dbUpdates)
    .eq('id', userId);

  if (error) throw error;
}

function mapUser(row) {
  const getTier = (points) => {
    if (points >= 3000) return 'Elite';
    if (points >= 2000) return 'Gold';
    if (points >= 1000) return 'Silver';
    return 'Bronze';
  };

  return {
    id: row.id,
    name: row.full_name || '',
    email: row.email,
    role: row.role,
    avatar: row.avatar_url,
    about: row.about || '',
    joinedAt: row.created_at ? new Date(row.created_at).toISOString().split('T')[0] : '',
    score: row.points || 0,
    points: row.points || 0,
    tier: getTier(row.points || 0),
    uploads: 0,
    downloads: 0,
    warnings: row.warnings || 0,
    is_banned: row.is_banned || false,
    status: row.is_banned ? 'Banned' : row.warnings > 0 ? 'Warned' : 'Active',
  };
}
