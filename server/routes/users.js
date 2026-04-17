const express = require('express');
const router = express.Router();

function auth() {
  return (req, res, next) => req.app.locals.authenticateJWT(req, res, next);
}
function superadmin() {
  return (req, res, next) => req.app.locals.requireSuperAdmin(req, res, next);
}
function roles(r) {
  return (req, res, next) => req.app.locals.requireRoles(r)(req, res, next);
}

// GET /api/users — all users (superadmin)
router.get('/', auth(), superadmin(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const [rows] = await db.query('SELECT * FROM profiles ORDER BY created_at DESC');
    res.json(rows.map(mapUser));
  } catch (err) {
    console.error('Fetch users error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/users/students — students only (faculty or superadmin)
router.get('/students', auth(), roles(['superadmin', 'faculty']), async (req, res) => {
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

    // Only allow self-update or superadmin
    if (req.user.id !== id && req.user.role !== 'superadmin') {
      return res.status(403).json({ error: 'Forbidden' });
    }

    const updates = {};
    const { full_name, about, avatar_url, points } = req.body;
    if (full_name !== undefined) updates.full_name = full_name;
    if (about !== undefined) updates.about = about;
    if (avatar_url !== undefined) updates.avatar_url = avatar_url;
    if (points !== undefined && req.user.role === 'superadmin') updates.points = points;

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

// PUT /api/users/:id/warn — increment warnings (superadmin)
router.put('/:id/warn', auth(), superadmin(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    await db.query('UPDATE profiles SET warnings = warnings + 1 WHERE id = ?', [req.params.id]);
    res.json({ success: true });
  } catch (err) {
    console.error('Warn user error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// PUT /api/users/:id/ban — ban/unban (superadmin)
router.put('/:id/ban', auth(), superadmin(), async (req, res) => {
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

// PUT /api/users/:id/role — change role (superadmin only)
router.put('/:id/role', auth(), superadmin(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const { role } = req.body;
    if (!['student', 'faculty', 'superadmin'].includes(role)) {
      return res.status(400).json({ error: 'Invalid role' });
    }
    await db.query('UPDATE profiles SET role = ? WHERE id = ?', [role, req.params.id]);
    res.json({ success: true });
  } catch (err) {
    console.error('Role update error:', err);
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

// ── Faculty Codes Management (Superadmin) ──
const { v4: uuidv4 } = require('uuid');

// GET /api/users/faculty-codes — get all codes
router.get('/faculty-codes', auth(), superadmin(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const [rows] = await db.query('SELECT * FROM faculty_codes ORDER BY created_at DESC');
    res.json(rows);
  } catch (err) {
    console.error('Fetch codes error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /api/users/faculty-codes — generate a new code
router.post('/faculty-codes', auth(), superadmin(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const id = uuidv4();
    const code = 'FAC-' + Math.random().toString(36).substring(2, 8).toUpperCase();
    await db.query(
      'INSERT INTO faculty_codes (id, code, created_by) VALUES (?, ?, ?)',
      [id, code, req.user.id]
    );
    res.status(201).json({ id, code, created_by: req.user.id, is_used: 0 });
  } catch (err) {
    console.error('Generate code error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// DELETE /api/users/faculty-codes/:id — delete a code
router.delete('/faculty-codes/:id', auth(), superadmin(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    await db.query('DELETE FROM faculty_codes WHERE id = ?', [req.params.id]);
    res.json({ success: true });
  } catch (err) {
    console.error('Delete code error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /api/users/upgrade-faculty — upgrade to faculty using a code
router.post('/upgrade-faculty', auth(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const { faculty_code } = req.body;
    
    if (!faculty_code) {
      return res.status(400).json({ error: 'Faculty code is required' });
    }

    // Check code
    const [codes] = await db.query('SELECT * FROM faculty_codes WHERE code = ? AND is_used = 0', [faculty_code]);
    if (codes.length === 0) {
      return res.status(400).json({ error: 'Invalid or already used faculty code' });
    }

    // Update role and mark code used
    await db.query('UPDATE profiles SET role = "faculty" WHERE id = ?', [req.user.id]);
    await db.query('UPDATE faculty_codes SET is_used = 1, used_by = ? WHERE code = ?', [req.user.id, faculty_code]);

    res.json({ success: true, role: 'faculty' });
  } catch (err) {
    console.error('Upgrade faculty error:', err);
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
