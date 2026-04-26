const express = require('express');
const router = express.Router();

function auth() { return (req, res, next) => req.app.locals.authenticateJWT(req, res, next); }
function roles(r) { return (req, res, next) => req.app.locals.requireRoles(r)(req, res, next); }

// GET /api/analytics
router.get('/', auth(), roles(['superadmin', 'faculty']), async (req, res) => {
  try {
    const { db } = req.app.locals;

    const [[{ totalUsers }]] = await db.query('SELECT COUNT(*) as totalUsers FROM profiles');
    const [[{ totalNotes }]] = await db.query('SELECT COUNT(*) as totalNotes FROM notes');
    const [[{ totalDownloads }]] = await db.query('SELECT SUM(downloads) as totalDownloads FROM notes');
    const [[{ activeChats }]] = await db.query('SELECT COUNT(*) as activeChats FROM \`groups\`');
    const [[{ openComplaints }]] = await db.query('SELECT COUNT(*) as openComplaints FROM complaints WHERE status = "open"');
    const [[{ resolvedComplaints }]] = await db.query('SELECT COUNT(*) as resolvedComplaints FROM complaints WHERE status = "resolved"');

    // Monthly data (last 12 months)
    const now = new Date();
    const oneYearAgo = new Date(now.getFullYear() - 1, now.getMonth(), 1);

    const [monthlyNotesData] = await db.query('SELECT YEAR(created_at) as y, MONTH(created_at) as m, COUNT(*) as c FROM notes WHERE created_at >= ? GROUP BY y, m', [oneYearAgo]);
    const [monthlyUsersData] = await db.query('SELECT YEAR(created_at) as y, MONTH(created_at) as m, COUNT(*) as c FROM profiles WHERE created_at >= ? GROUP BY y, m', [oneYearAgo]);

    const monthlyUploads = Array(12).fill(0);
    const monthlyUsers = Array(12).fill(0);

    for (let i = 11; i >= 0; i--) {
      const targetYear = now.getFullYear() - (now.getMonth() - i < 0 ? 1 : 0);
      const targetMonth = (now.getMonth() - i + 12) % 12 + 1; // 1-12
      
      const nData = monthlyNotesData.find(d => d.y === targetYear && d.m === targetMonth);
      if (nData) monthlyUploads[11 - i] = nData.c;

      const uData = monthlyUsersData.find(d => d.y === targetYear && d.m === targetMonth);
      if (uData) monthlyUsers[11 - i] = uData.c;
    }

    // Top subjects
    const [topSubjects] = await db.query('SELECT subject, COUNT(*) as count FROM notes GROUP BY subject ORDER BY count DESC LIMIT 5');

    res.json({
      totalUsers, totalNotes, 
      totalDownloads: totalDownloads || 0, 
      activeChats,
      openComplaints, resolvedComplaints,
      monthlyUploads,
      monthlyUsers,
      topSubjects: topSubjects.length > 0 ? topSubjects : [{ subject: 'No data', count: 0 }],
    });
  } catch (err) { console.error('Analytics error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

module.exports = router;
