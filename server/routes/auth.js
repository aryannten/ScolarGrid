const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');

// POST /api/auth/signup
router.post('/signup', async (req, res) => {
  try {
    const { db } = req.app.locals;
    const { name, email, password, role } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' });
    }

    const [existing] = await db.query('SELECT * FROM profiles WHERE email = ?', [email]);
    if (existing.length > 0) {
      return res.status(409).json({ error: 'Email already registered' });
    }

    const id = uuidv4();
    const password_hash = await bcrypt.hash(password, 10);
    const userRole = role || 'student';

    if (userRole === 'faculty') {
      const { faculty_code } = req.body;
      if (!faculty_code) {
        return res.status(400).json({ error: 'Faculty code is required for faculty registration' });
      }
      const [codes] = await db.query('SELECT * FROM faculty_codes WHERE code = ?', [faculty_code]);
      if (codes.length === 0 || codes[0].is_used) {
        return res.status(400).json({ error: 'Invalid or already used faculty code' });
      }
      await db.query('UPDATE faculty_codes SET is_used = 1, used_by = ? WHERE code = ?', [id, faculty_code]);
    }

    await db.query(`
      INSERT INTO profiles (id, email, password_hash, full_name, role) 
      VALUES (?, ?, ?, ?, ?)
    `, [id, email, password_hash, name || '', userRole]);

    const [profiles] = await db.query('SELECT * FROM profiles WHERE id = ?', [id]);
    const profile = profiles[0];

    const token = jwt.sign({ id, role: userRole }, req.app.locals.JWT_SECRET, { expiresIn: '7d' });

    res.status(201).json({ token, user: mapProfile(profile, []) });
  } catch (err) {
    console.error('Signup error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /api/auth/login
router.post('/login', async (req, res) => {
  try {
    const { db } = req.app.locals;
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' });
    }

    const [profiles] = await db.query('SELECT * FROM profiles WHERE email = ?', [email]);
    if (profiles.length === 0) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }
    const profile = profiles[0];

    if (profile.is_banned) {
      return res.status(403).json({ error: 'Your account has been banned' });
    }

    const valid = await bcrypt.compare(password, profile.password_hash);
    if (!valid) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    const token = jwt.sign(
      { id: profile.id, role: profile.role },
      req.app.locals.JWT_SECRET,
      { expiresIn: '7d' }
    );

    const [notes] = await db.query('SELECT * FROM notes WHERE uploader_id = ?', [profile.id]);
    res.json({ token, user: mapProfile(profile, notes) });
  } catch (err) {
    console.error('Login error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/auth/me
router.get('/me', (req, res, next) => req.app.locals.authenticateJWT(req, res, next), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const [profiles] = await db.query('SELECT * FROM profiles WHERE id = ?', [req.user.id]);
    if (profiles.length === 0) return res.status(404).json({ error: 'User not found' });
    const profile = profiles[0];
    
    const [notes] = await db.query('SELECT * FROM notes WHERE uploader_id = ?', [profile.id]);
    res.json({ user: mapProfile(profile, notes) });
  } catch (err) {
    console.error('Me error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

function mapProfile(row, notes = []) {
  const getTier = (pts) => {
    if (pts >= 3000) return 'Elite';
    if (pts >= 2000) return 'Gold';
    if (pts >= 1000) return 'Silver';
    return 'Bronze';
  };
  
  const userUploads = notes.filter(n => n.uploader_id === row.id);
  const uploadsCount = userUploads.length;
  const downloadsCount = userUploads.reduce((sum, n) => sum + (n.downloads || 0), 0);

  return {
    id: row.id, name: row.full_name || '', email: row.email, role: row.role,
    avatar: row.avatar_url, about: row.about || '',
    joinedAt: row.created_at ? new Date(row.created_at).toISOString().split('T')[0] : '',
    score: row.points || 0, points: row.points || 0, tier: getTier(row.points || 0),
    uploads: uploadsCount, downloads: downloadsCount, warnings: row.warnings || 0,
    is_banned: row.is_banned ? true : false,
  };
}

module.exports = router;
