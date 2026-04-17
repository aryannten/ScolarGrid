const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

function auth() { return (req, res, next) => req.app.locals.authenticateJWT(req, res, next); }
function superadmin() { return (req, res, next) => req.app.locals.requireSuperAdmin(req, res, next); }
function roles(r) { return (req, res, next) => req.app.locals.requireRoles(r)(req, res, next); }

// GET /api/users — all users (superadmin / faculty)
router.get('/', auth(), roles(['superadmin', 'faculty']), (req, res) => {
  try {
    const { store } = req.app.locals;
    const sorted = [...store.profiles].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    res.json(sorted.map(mapUser));
  } catch (err) { console.error('Fetch users error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// GET /api/users/students
router.get('/students', auth(), roles(['superadmin', 'faculty']), (req, res) => {
  try {
    const { store } = req.app.locals;
    const students = store.profiles.filter(p => p.role === 'student').sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    res.json(students.map(mapUser));
  } catch (err) { console.error('Fetch students error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// PUT /api/users/:id
router.put('/:id', auth(), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const { id } = req.params;
    if (req.user.id !== id && req.user.role !== 'superadmin') return res.status(403).json({ error: 'Forbidden' });

    const profile = store.profiles.find(p => p.id === id);
    if (!profile) return res.status(404).json({ error: 'User not found' });

    const { full_name, about, avatar_url, points } = req.body;
    if (full_name !== undefined) profile.full_name = full_name;
    if (about !== undefined) profile.about = about;
    if (avatar_url !== undefined) profile.avatar_url = avatar_url;
    if (points !== undefined && req.user.role === 'superadmin') profile.points = points;
    profile.updated_at = new Date().toISOString();
    saveToDisk();

    res.json({ success: true });
  } catch (err) { console.error('Update user error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// PUT /api/users/:id/warn
router.put('/:id/warn', auth(), roles(['superadmin', 'faculty']), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const profile = store.profiles.find(p => p.id === req.params.id);
    if (profile) { profile.warnings = (profile.warnings || 0) + 1; saveToDisk(); }
    res.json({ success: true });
  } catch (err) { console.error('Warn error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// PUT /api/users/:id/ban
router.put('/:id/ban', auth(), roles(['superadmin', 'faculty']), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const profile = store.profiles.find(p => p.id === req.params.id);
    if (profile) { profile.is_banned = req.body.banned ? 1 : 0; saveToDisk(); }
    res.json({ success: true });
  } catch (err) { console.error('Ban error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// PUT /api/users/:id/role
router.put('/:id/role', auth(), superadmin(), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const { role } = req.body;
    if (!['student', 'faculty', 'superadmin'].includes(role)) return res.status(400).json({ error: 'Invalid role' });
    const profile = store.profiles.find(p => p.id === req.params.id);
    if (profile) { profile.role = role; saveToDisk(); }
    res.json({ success: true });
  } catch (err) { console.error('Role error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/users/:id/avatar
router.post('/:id/avatar', auth(), (req, res, next) => {
  req.app.locals.upload.single('avatar')(req, res, next);
}, (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    if (!req.file) return res.status(400).json({ error: 'No file uploaded' });
    const avatarUrl = `/uploads/avatars/${req.file.filename}`;
    const profile = store.profiles.find(p => p.id === req.params.id);
    if (profile) { profile.avatar_url = avatarUrl; saveToDisk(); }
    res.json({ avatar_url: avatarUrl });
  } catch (err) { console.error('Avatar error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// GET /api/users/faculty-codes
router.get('/faculty-codes', auth(), superadmin(), (req, res) => {
  try {
    const { store } = req.app.locals;
    res.json([...store.faculty_codes].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)));
  } catch (err) { console.error('Codes error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/users/faculty-codes
router.post('/faculty-codes', auth(), superadmin(), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const entry = { id: uuidv4(), code: 'FAC-' + Math.random().toString(36).substring(2, 8).toUpperCase(), created_by: req.user.id, is_used: 0, used_by: null, created_at: new Date().toISOString() };
    store.faculty_codes.push(entry);
    saveToDisk();
    res.status(201).json(entry);
  } catch (err) { console.error('Gen code error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// DELETE /api/users/faculty-codes/:id
router.delete('/faculty-codes/:id', auth(), superadmin(), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    store.faculty_codes = store.faculty_codes.filter(c => c.id !== req.params.id);
    saveToDisk();
    res.json({ success: true });
  } catch (err) { console.error('Del code error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/users/upgrade-faculty
router.post('/upgrade-faculty', auth(), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const { faculty_code } = req.body;
    if (!faculty_code) return res.status(400).json({ error: 'Faculty code is required' });
    const code = store.faculty_codes.find(c => c.code === faculty_code && !c.is_used);
    if (!code) return res.status(400).json({ error: 'Invalid or already used faculty code' });
    const profile = store.profiles.find(p => p.id === req.user.id);
    if (profile) profile.role = 'faculty';
    code.is_used = 1; code.used_by = req.user.id;
    saveToDisk();
    res.json({ success: true, role: 'faculty' });
  } catch (err) { console.error('Upgrade error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

function mapUser(row) {
  const getTier = (pts) => { if (pts >= 3000) return 'Elite'; if (pts >= 2000) return 'Gold'; if (pts >= 1000) return 'Silver'; return 'Bronze'; };
  return {
    id: row.id, name: row.full_name || '', email: row.email, role: row.role,
    avatar: row.avatar_url, about: row.about || '',
    joinedAt: row.created_at ? row.created_at.split('T')[0] : '',
    score: row.points || 0, points: row.points || 0, tier: getTier(row.points || 0),
    uploads: 0, downloads: 0, warnings: row.warnings || 0,
    is_banned: row.is_banned ? true : false,
    status: row.is_banned ? 'Banned' : row.warnings > 0 ? 'Warned' : 'Active',
  };
}

module.exports = router;
