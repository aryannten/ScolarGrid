const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

function auth() { return (req, res, next) => req.app.locals.authenticateJWT(req, res, next); }
function roles(r) { return (req, res, next) => req.app.locals.requireRoles(r)(req, res, next); }

// GET /api/leaderboard
router.get('/', auth(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const limit = parseInt(req.query.limit) || 50;

    const [students] = await db.query('SELECT * FROM profiles WHERE role = "student" AND is_banned = 0 ORDER BY points DESC LIMIT ?', [limit]);

    const getTier = (pts) => { if (pts >= 3000) return 'Elite'; if (pts >= 2000) return 'Gold'; if (pts >= 1000) return 'Silver'; return 'Bronze'; };

    const leaderboard = students.map((row, i) => ({
      id: row.id, name: row.full_name || 'Unknown', avatar: row.avatar_url,
      score: row.points || 0, points: row.points || 0, role: row.role,
      about: row.about || '', tier: getTier(row.points || 0), rank: i + 1,
      uploads: 0, downloads: 0,
      joinedAt: row.created_at ? new Date(row.created_at).toISOString().split('T')[0] : '',
    }));

    res.json(leaderboard);
  } catch (err) { console.error('Leaderboard error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// GET /api/leaderboard/:userId/history
router.get('/:userId/history', auth(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const [history] = await db.query('SELECT * FROM leaderboard_points WHERE user_id = ? ORDER BY created_at DESC', [req.params.userId]);
    res.json(history);
  } catch (err) { console.error('History error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/leaderboard/points
router.post('/points', auth(), roles(['superadmin', 'faculty']), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const { studentId, points, reason } = req.body;
    if (!studentId || !points || !reason) return res.status(400).json({ error: 'Missing required fields' });

    const id = uuidv4();
    const dbReason = points > 0 ? 'admin_bonus' : 'penalty';

    await db.query('INSERT INTO leaderboard_points (id, user_id, points, reason, reference_id, created_at) VALUES (?, ?, ?, ?, ?, ?)',
      [id, studentId, points, dbReason, req.user.id, new Date()]);

    await db.query('UPDATE profiles SET points = points + ? WHERE id = ?', [points, studentId]);

    res.json({ success: true, id, points });
  } catch (err) { console.error('Points error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

module.exports = router;
