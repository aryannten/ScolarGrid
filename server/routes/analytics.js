const express = require('express');
const router = express.Router();

function auth() {
  return (req, res, next) => req.app.locals.authenticateJWT(req, res, next);
}
function roles(r) {
  return (req, res, next) => req.app.locals.requireRoles(r)(req, res, next);
}

// GET /api/analytics
router.get('/', auth(), roles(['superadmin', 'faculty']), async (req, res) => {
  try {
    const db = req.app.locals.db;

    // Total users
    const [[{ totalUsers }]] = await db.query('SELECT COUNT(*) AS totalUsers FROM profiles');

    // Total notes
    const [[{ totalNotes }]] = await db.query('SELECT COUNT(*) AS totalNotes FROM notes');

    // Total downloads
    const [[{ totalDownloads }]] = await db.query('SELECT COALESCE(SUM(downloads), 0) AS totalDownloads FROM notes');

    // Active chat groups
    const [[{ activeChats }]] = await db.query('SELECT COUNT(*) AS activeChats FROM `groups`');

    // Open complaints
    const [[{ openComplaints }]] = await db.query("SELECT COUNT(*) AS openComplaints FROM complaints WHERE status = 'open'");

    // Resolved complaints
    const [[{ resolvedComplaints }]] = await db.query("SELECT COUNT(*) AS resolvedComplaints FROM complaints WHERE status = 'resolved'");

    // Monthly uploads (last 12 months)
    const monthlyUploads = await getMonthlyData(db, 'notes', 'created_at');

    // Monthly user signups
    const monthlyUsers = await getMonthlyData(db, 'profiles', 'created_at');

    // Top subjects
    const [subjectRows] = await db.query(
      `SELECT subject, COUNT(*) AS count FROM notes
       GROUP BY subject ORDER BY count DESC LIMIT 5`
    );
    const topSubjects = subjectRows.length > 0
      ? subjectRows.map(r => ({ subject: r.subject, count: r.count }))
      : [{ subject: 'No data', count: 0 }];

    res.json({
      totalUsers,
      totalNotes,
      totalDownloads,
      activeChats,
      openComplaints,
      resolvedComplaints,
      monthlyUploads: monthlyUploads.length > 0 ? monthlyUploads : Array(12).fill(0),
      monthlyUsers: monthlyUsers.length > 0 ? monthlyUsers : Array(12).fill(0),
      topSubjects,
    });
  } catch (err) {
    console.error('Fetch analytics error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

async function getMonthlyData(db, table, timestampColumn) {
  const now = new Date();
  const counts = [];

  for (let i = 11; i >= 0; i--) {
    const start = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const end = new Date(now.getFullYear(), now.getMonth() - i + 1, 1);

    const [[{ cnt }]] = await db.query(
      `SELECT COUNT(*) AS cnt FROM ${table} WHERE ${timestampColumn} >= ? AND ${timestampColumn} < ?`,
      [start.toISOString().slice(0, 19).replace('T', ' '), end.toISOString().slice(0, 19).replace('T', ' ')]
    );

    counts.push(cnt);
  }

  return counts;
}

module.exports = router;
