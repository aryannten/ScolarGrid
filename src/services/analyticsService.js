import { supabase } from '../lib/supabaseClient';

/**
 * Fetch aggregate analytics from real data.
 */
export async function fetchAnalytics() {
  // Total users
  const { count: totalUsers } = await supabase
    .from('profiles')
    .select('*', { count: 'exact', head: true });

  // Total notes
  const { count: totalNotes } = await supabase
    .from('notes')
    .select('*', { count: 'exact', head: true });

  // Total downloads
  const { data: dlData } = await supabase
    .from('notes')
    .select('downloads');
  const totalDownloads = (dlData || []).reduce((sum, n) => sum + (n.downloads || 0), 0);

  // Active chat groups
  const { count: activeChats } = await supabase
    .from('groups')
    .select('*', { count: 'exact', head: true });

  // Open complaints
  const { count: openComplaints } = await supabase
    .from('complaints')
    .select('*', { count: 'exact', head: true })
    .eq('status', 'open');

  // Resolved complaints
  const { count: resolvedComplaints } = await supabase
    .from('complaints')
    .select('*', { count: 'exact', head: true })
    .eq('status', 'resolved');

  // Monthly uploads (last 12 months)
  const monthlyUploads = await getMonthlyData('notes', 'created_at');

  // Monthly user signups
  const monthlyUsers = await getMonthlyData('profiles', 'created_at');

  // Top subjects
  const { data: subjectData } = await supabase
    .from('notes')
    .select('subject');
  const subjectCounts = {};
  (subjectData || []).forEach((n) => {
    subjectCounts[n.subject] = (subjectCounts[n.subject] || 0) + 1;
  });
  const topSubjects = Object.entries(subjectCounts)
    .map(([subject, count]) => ({ subject, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  return {
    totalUsers: totalUsers || 0,
    totalNotes: totalNotes || 0,
    totalDownloads,
    activeChats: activeChats || 0,
    openComplaints: openComplaints || 0,
    resolvedComplaints: resolvedComplaints || 0,
    monthlyUploads: monthlyUploads.length > 0 ? monthlyUploads : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    monthlyUsers: monthlyUsers.length > 0 ? monthlyUsers : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    topSubjects: topSubjects.length > 0 ? topSubjects : [{ subject: 'No data', count: 0 }],
  };
}

/**
 * Get monthly counts for a table based on a timestamp column.
 */
async function getMonthlyData(table, timestampColumn) {
  const now = new Date();
  const counts = [];

  for (let i = 11; i >= 0; i--) {
    const start = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const end = new Date(now.getFullYear(), now.getMonth() - i + 1, 1);

    const { count } = await supabase
      .from(table)
      .select('*', { count: 'exact', head: true })
      .gte(timestampColumn, start.toISOString())
      .lt(timestampColumn, end.toISOString());

    counts.push(count || 0);
  }

  return counts;
}
