const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

function auth() { return (req, res, next) => req.app.locals.authenticateJWT(req, res, next); }
function superadmin() { return (req, res, next) => req.app.locals.requireSuperAdmin(req, res, next); }
function roles(r) { return (req, res, next) => req.app.locals.requireRoles(r)(req, res, next); }

// GET /api/users — all users (superadmin / faculty)
router.get('/', auth(), roles(['superadmin', 'faculty']), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const [profiles] = await db.query('SELECT * FROM profiles ORDER BY created_at DESC');
    res.json(profiles.map(mapUser));
  } catch (err) { console.error('Fetch users error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// GET /api/users/students
router.get('/students', auth(), roles(['superadmin', 'faculty']), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const [students] = await db.query('SELECT * FROM profiles WHERE role = "student" ORDER BY created_at DESC');
    res.json(students.map(mapUser));
  } catch (err) { console.error('Fetch students error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// PUT /api/users/:id
router.put('/:id', auth(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const { id } = req.params;
    if (req.user.id !== id && req.user.role !== 'superadmin') return res.status(403).json({ error: 'Forbidden' });

    const { full_name, about, avatar_url, points } = req.body;
    let updates = [];
    let values = [];
    if (full_name !== undefined) { updates.push('full_name = ?'); values.push(full_name); }
    if (about !== undefined) { updates.push('about = ?'); values.push(about); }
    if (avatar_url !== undefined) { updates.push('avatar_url = ?'); values.push(avatar_url); }
    if (points !== undefined && req.user.role === 'superadmin') { updates.push('points = ?'); values.push(points); }

    if (updates.length > 0) {
      values.push(id);
      await db.query(`UPDATE profiles SET ${updates.join(', ')} WHERE id = ?`, values);
    }
    res.json({ success: true });
  } catch (err) { console.error('Update user error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// PUT /api/users/:id/warn
router.put('/:id/warn', auth(), roles(['superadmin', 'faculty']), async (req, res) => {
  try {
    const { db } = req.app.locals;
    await db.query('UPDATE profiles SET warnings = warnings + 1 WHERE id = ?', [req.params.id]);
    res.json({ success: true });
  } catch (err) { console.error('Warn error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// PUT /api/users/:id/ban
router.put('/:id/ban', auth(), roles(['superadmin', 'faculty']), async (req, res) => {
  try {
    const { db } = req.app.locals;
    await db.query('UPDATE profiles SET is_banned = ? WHERE id = ?', [req.body.banned ? 1 : 0, req.params.id]);
    res.json({ success: true });
  } catch (err) { console.error('Ban error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// PUT /api/users/:id/role
router.put('/:id/role', auth(), superadmin(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const { role } = req.body;
    if (!['student', 'faculty', 'superadmin'].includes(role)) return res.status(400).json({ error: 'Invalid role' });
    await db.query('UPDATE profiles SET role = ? WHERE id = ?', [role, req.params.id]);
    res.json({ success: true });
  } catch (err) { console.error('Role error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/users/:id/avatar
router.post('/:id/avatar', auth(), (req, res, next) => {
  req.app.locals.upload.single('avatar')(req, res, next);
}, async (req, res) => {
  try {
    const { db } = req.app.locals;
    if (!req.file) return res.status(400).json({ error: 'No file uploaded' });
    const avatarUrl = `/uploads/avatars/${req.file.filename}`;
    await db.query('UPDATE profiles SET avatar_url = ? WHERE id = ?', [avatarUrl, req.params.id]);
    res.json({ avatar_url: avatarUrl });
  } catch (err) { console.error('Avatar error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// GET /api/users/faculty-codes
router.get('/faculty-codes', auth(), superadmin(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const [codes] = await db.query('SELECT * FROM faculty_codes ORDER BY created_at DESC');
    res.json(codes);
  } catch (err) { console.error('Codes error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/users/faculty-codes
router.post('/faculty-codes', auth(), superadmin(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const id = uuidv4();
    const code = 'FAC-' + Math.random().toString(36).substring(2, 8).toUpperCase();
    const created_at = new Date();
    await db.query('INSERT INTO faculty_codes (id, code, is_used, created_at) VALUES (?, ?, 0, ?)', [id, code, created_at]);
    res.status(201).json({ id, code, is_used: 0, used_by: null, created_at });
  } catch (err) { console.error('Gen code error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// DELETE /api/users/faculty-codes/:id
router.delete('/faculty-codes/:id', auth(), superadmin(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    // We can delete by id or code. Let's delete by id or code just in case.
    await db.query('DELETE FROM faculty_codes WHERE id = ? OR code = ?', [req.params.id, req.params.id]);
    res.json({ success: true });
  } catch (err) { console.error('Del code error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/users/upgrade-faculty
router.post('/upgrade-faculty', auth(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const { faculty_code } = req.body;
    if (!faculty_code) return res.status(400).json({ error: 'Faculty code is required' });
    
    const [codes] = await db.query('SELECT * FROM faculty_codes WHERE code = ? AND is_used = 0', [faculty_code]);
    if (codes.length === 0) return res.status(400).json({ error: 'Invalid or already used faculty code' });
    
    await db.query('UPDATE faculty_codes SET is_used = 1, used_by = ? WHERE code = ?', [req.user.id, faculty_code]);
    await db.query('UPDATE profiles SET role = "faculty" WHERE id = ?', [req.user.id]);
    res.json({ success: true, role: 'faculty' });
  } catch (err) { console.error('Upgrade error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

function mapUser(row) {
  const getTier = (pts) => { if (pts >= 3000) return 'Elite'; if (pts >= 2000) return 'Gold'; if (pts >= 1000) return 'Silver'; return 'Bronze'; };
  return {
    id: row.id, name: row.full_name || '', email: row.email, role: row.role,
    avatar: row.avatar_url, about: row.about || '',
    joinedAt: row.created_at ? new Date(row.created_at).toISOString().split('T')[0] : '',
    score: row.points || 0, points: row.points || 0, tier: getTier(row.points || 0),
    uploads: 0, downloads: 0, warnings: row.warnings || 0,
    is_banned: row.is_banned ? true : false,
    status: row.is_banned ? 'Banned' : row.warnings > 0 ? 'Warned' : 'Active',
  };
}

module.exports = router;
