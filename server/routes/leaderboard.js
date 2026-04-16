const express = require('express');
const router = express.Router();

function auth() {
  return (req, res, next) => req.app.locals.authenticateJWT(req, res, next);
}

// GET /api/leaderboard
router.get('/', auth(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const limit = parseInt(req.query.limit) || 50;

    const [rows] = await db.query(
      `SELECT id, full_name, avatar_url, points, role, about, created_at
       FROM profiles
       WHERE role = 'student' AND is_banned = 0
       ORDER BY points DESC
       LIMIT ?`,
      [limit]
    );

    const getTier = (points) => {
      if (points >= 3000) return 'Elite';
      if (points >= 2000) return 'Gold';
      if (points >= 1000) return 'Silver';
      return 'Bronze';
    };

    const leaderboard = rows.map((row, i) => ({
      id: row.id,
      name: row.full_name || 'Unknown',
      avatar: row.avatar_url,
      score: row.points || 0,
      points: row.points || 0,
      role: row.role,
      about: row.about || '',
      tier: getTier(row.points || 0),
      rank: i + 1,
      uploads: 0,
      downloads: 0,
      joinedAt: row.created_at ? new Date(row.created_at).toISOString().split('T')[0] : '',
    }));

    res.json(leaderboard);
  } catch (err) {
    console.error('Fetch leaderboard error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/leaderboard/:userId/history
router.get('/:userId/history', auth(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const [rows] = await db.query(
      'SELECT * FROM leaderboard_points WHERE user_id = ? ORDER BY created_at DESC',
      [req.params.userId]
    );
    res.json(rows);
  } catch (err) {
    console.error('Fetch point history error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
