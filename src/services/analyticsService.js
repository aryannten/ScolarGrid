import { apiGet } from '../lib/apiClient';

/**
 * Fetch aggregate analytics from real data.
 */
export async function fetchAnalytics() {
  return apiGet('/api/analytics');
}
