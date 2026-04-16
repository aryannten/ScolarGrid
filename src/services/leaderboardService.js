import { apiGet } from '../lib/apiClient';

const TIER_THRESHOLDS = { Bronze: 0, Silver: 1000, Gold: 2000, Elite: 3000 };

/**
 * Fetch the leaderboard — students ordered by points.
 */
export async function fetchLeaderboard(limit = 50) {
  return apiGet(`/api/leaderboard?limit=${limit}`);
}

/**
 * Fetch point history for a user.
 */
export async function fetchUserPoints(userId) {
  return apiGet(`/api/leaderboard/${userId}/history`);
}

function getTier(points) {
  if (points >= 3000) return 'Elite';
  if (points >= 2000) return 'Gold';
  if (points >= 1000) return 'Silver';
  return 'Bronze';
}

export { TIER_THRESHOLDS };
