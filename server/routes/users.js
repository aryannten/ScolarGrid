const express = require('express');
const router = express.Router();

function auth() {
  return (req, res, next) => req.app.locals.authenticateJWT(req, res, next);
}
function admin() {
  return (req, res, next) => req.app.locals.requireAdmin(req, res, next);
}

// GET /api/users — all users (admin)
router.get('/', auth(), admin(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const [rows] = await db.query('SELECT * FROM profiles ORDER BY created_at DESC');
    res.json(rows.map(mapUser));
  } catch (err) {
    console.error('Fetch users error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/users/students — students only (admin)
router.get('/students', auth(), admin(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const [rows] = await db.query("SELECT * FROM profiles WHERE role = 'student' ORDER BY created_at DESC");
    res.json(rows.map(mapUser));
  } catch (err) {
    console.error('Fetch students error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// PUT /api/users/:id — update profile
router.put('/:id', auth(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const { id } = req.params;

    // Only allow self-update or admin
    if (req.user.id !== id && req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Forbidden' });
    }

    const updates = {};
    const { full_name, about, avatar_url, points } = req.body;
    if (full_name !== undefined) updates.full_name = full_name;
    if (about !== undefined) updates.about = about;
    if (avatar_url !== undefined) updates.avatar_url = avatar_url;
    if (points !== undefined && req.user.role === 'admin') updates.points = points;

    if (Object.keys(updates).length === 0) {
      return res.status(400).json({ error: 'No fields to update' });
    }

    const setClauses = Object.keys(updates).map(k => `${k} = ?`).join(', ');
    const values = Object.values(updates);

    await db.query(`UPDATE profiles SET ${setClauses} WHERE id = ?`, [...values, id]);
    res.json({ success: true });
  } catch (err) {
    console.error('Update user error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// PUT /api/users/:id/warn — increment warnings (admin)
router.put('/:id/warn', auth(), admin(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    await db.query('UPDATE profiles SET warnings = warnings + 1 WHERE id = ?', [req.params.id]);
    res.json({ success: true });
  } catch (err) {
    console.error('Warn user error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// PUT /api/users/:id/ban — ban/unban (admin)
router.put('/:id/ban', auth(), admin(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const { banned } = req.body;
    await db.query('UPDATE profiles SET is_banned = ? WHERE id = ?', [banned ? 1 : 0, req.params.id]);
    res.json({ success: true });
  } catch (err) {
    console.error('Ban user error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /api/users/:id/avatar — upload avatar
router.post('/:id/avatar', auth(), (req, res, next) => {
  req.app.locals.upload.single('avatar')(req, res, next);
}, async (req, res) => {
  try {
    const db = req.app.locals.db;
    if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

    const avatarUrl = `/uploads/avatars/${req.file.filename}`;
    await db.query('UPDATE profiles SET avatar_url = ? WHERE id = ?', [avatarUrl, req.params.id]);
    res.json({ avatar_url: avatarUrl });
  } catch (err) {
    console.error('Avatar upload error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

function mapUser(row) {
  const getTier = (points) => {
    if (points >= 3000) return 'Elite';
    if (points >= 2000) return 'Gold';
    if (points >= 1000) return 'Silver';
    return 'Bronze';
  };

  return {
    id: row.id,
    name: row.full_name || '',
    email: row.email,
    role: row.role,
    avatar: row.avatar_url,
    about: row.about || '',
    joinedAt: row.created_at ? new Date(row.created_at).toISOString().split('T')[0] : '',
    score: row.points || 0,
    points: row.points || 0,
    tier: getTier(row.points || 0),
    uploads: 0,
    downloads: 0,
    warnings: row.warnings || 0,
    is_banned: row.is_banned ? true : false,
    status: row.is_banned ? 'Banned' : row.warnings > 0 ? 'Warned' : 'Active',
  };
}

module.exports = router;
