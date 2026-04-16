import { supabase } from '../lib/supabaseClient';

const TIER_THRESHOLDS = { Bronze: 0, Silver: 1000, Gold: 2000, Elite: 3000 };

/**
 * Fetch the leaderboard — students ordered by points.
 */
export async function fetchLeaderboard(limit = 50) {
  const { data, error } = await supabase
    .from('profiles')
    .select('id, full_name, avatar_url, points, role, about, created_at')
    .eq('role', 'student')
    .eq('is_banned', false)
    .order('points', { ascending: false })
    .limit(limit);

  if (error) throw error;

  // Count uploads per user
  return (data || []).map((row, i) => ({
    id: row.id,
    name: row.full_name || 'Unknown',
    avatar: row.avatar_url,
    score: row.points || 0,
    points: row.points || 0,
    role: row.role,
    about: row.about || '',
    tier: getTier(row.points || 0),
    rank: i + 1,
    uploads: 0,    // could be fetched separately if needed
    downloads: 0,
    joinedAt: row.created_at ? new Date(row.created_at).toISOString().split('T')[0] : '',
  }));
}

/**
 * Fetch point history for a user.
 */
export async function fetchUserPoints(userId) {
  const { data, error } = await supabase
    .from('leaderboard_points')
    .select('*')
    .eq('user_id', userId)
    .order('created_at', { ascending: false });

  if (error) throw error;
  return data || [];
}

function getTier(points) {
  if (points >= 3000) return 'Elite';
  if (points >= 2000) return 'Gold';
  if (points >= 1000) return 'Silver';
  return 'Bronze';
}

export { TIER_THRESHOLDS };
