const express = require('express');
const router = express.Router();

function auth() { return (req, res, next) => req.app.locals.authenticateJWT(req, res, next); }
function roles(r) { return (req, res, next) => req.app.locals.requireRoles(r)(req, res, next); }

// GET /api/analytics
router.get('/', auth(), roles(['superadmin', 'faculty']), (req, res) => {
  try {
    const { store } = req.app.locals;

    const totalUsers = store.profiles.length;
    const totalNotes = store.notes.length;
    const totalDownloads = store.notes.reduce((sum, n) => sum + (n.downloads || 0), 0);
    const activeChats = store.groups.length;
    const openComplaints = store.complaints.filter(c => c.status === 'open').length;
    const resolvedComplaints = store.complaints.filter(c => c.status === 'resolved').length;

    // Monthly data (last 12 months)
    const now = new Date();
    const monthlyUploads = [];
    const monthlyUsers = [];

    for (let i = 11; i >= 0; i--) {
      const start = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const end = new Date(now.getFullYear(), now.getMonth() - i + 1, 1);

      monthlyUploads.push(store.notes.filter(n => {
        const d = new Date(n.created_at);
        return d >= start && d < end;
      }).length);

      monthlyUsers.push(store.profiles.filter(p => {
        const d = new Date(p.created_at);
        return d >= start && d < end;
      }).length);
    }

    // Top subjects
    const subjectCounts = {};
    store.notes.forEach(n => { subjectCounts[n.subject] = (subjectCounts[n.subject] || 0) + 1; });
    const topSubjects = Object.entries(subjectCounts)
      .map(([subject, count]) => ({ subject, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);

    res.json({
      totalUsers, totalNotes, totalDownloads, activeChats,
      openComplaints, resolvedComplaints,
      monthlyUploads: monthlyUploads.length > 0 ? monthlyUploads : Array(12).fill(0),
      monthlyUsers: monthlyUsers.length > 0 ? monthlyUsers : Array(12).fill(0),
      topSubjects: topSubjects.length > 0 ? topSubjects : [{ subject: 'No data', count: 0 }],
    });
  } catch (err) { console.error('Analytics error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

module.exports = router;
