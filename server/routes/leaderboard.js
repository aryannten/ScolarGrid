const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

function auth() { return (req, res, next) => req.app.locals.authenticateJWT(req, res, next); }
function roles(r) { return (req, res, next) => req.app.locals.requireRoles(r)(req, res, next); }

// GET /api/leaderboard
router.get('/', auth(), (req, res) => {
  try {
    const { store } = req.app.locals;
    const limit = parseInt(req.query.limit) || 50;

    const students = store.profiles
      .filter(p => p.role === 'student' && !p.is_banned)
      .sort((a, b) => (b.points || 0) - (a.points || 0))
      .slice(0, limit);

    const getTier = (pts) => { if (pts >= 3000) return 'Elite'; if (pts >= 2000) return 'Gold'; if (pts >= 1000) return 'Silver'; return 'Bronze'; };

    const leaderboard = students.map((row, i) => ({
      id: row.id, name: row.full_name || 'Unknown', avatar: row.avatar_url,
      score: row.points || 0, points: row.points || 0, role: row.role,
      about: row.about || '', tier: getTier(row.points || 0), rank: i + 1,
      uploads: 0, downloads: 0,
      joinedAt: row.created_at ? row.created_at.split('T')[0] : '',
    }));

    res.json(leaderboard);
  } catch (err) { console.error('Leaderboard error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// GET /api/leaderboard/:userId/history
router.get('/:userId/history', auth(), (req, res) => {
  try {
    const { store } = req.app.locals;
    const history = store.leaderboard_points
      .filter(lp => lp.user_id === req.params.userId)
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    res.json(history);
  } catch (err) { console.error('History error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/leaderboard/points
router.post('/points', auth(), roles(['superadmin', 'faculty']), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const { studentId, points, reason } = req.body;
    if (!studentId || !points || !reason) return res.status(400).json({ error: 'Missing required fields' });

    const id = uuidv4();
    const dbReason = points > 0 ? 'admin_bonus' : 'penalty';

    store.leaderboard_points.push({ id, user_id: studentId, points, reason: dbReason, reference_id: req.user.id, created_at: new Date().toISOString() });

    const profile = store.profiles.find(p => p.id === studentId);
    if (profile) profile.points = (profile.points || 0) + points;

    saveToDisk();
    res.json({ success: true, id, points });
  } catch (err) { console.error('Points error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

module.exports = router;
