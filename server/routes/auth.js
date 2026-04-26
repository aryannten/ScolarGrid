const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');

// POST /api/auth/signup
router.post('/signup', async (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const { name, email, password, role } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' });
    }

    const existing = store.profiles.find(p => p.email === email);
    if (existing) {
      return res.status(409).json({ error: 'Email already registered' });
    }

    const id = uuidv4();
    const password_hash = await bcrypt.hash(password, 10);
    const userRole = role || 'student';
    const now = new Date().toISOString();

    if (userRole === 'faculty') {
      const { faculty_code } = req.body;
      if (!faculty_code) {
        return res.status(400).json({ error: 'Faculty code is required for faculty registration' });
      }
      const codeEntry = store.faculty_codes.find(c => c.code === faculty_code && !c.is_used);
      if (!codeEntry) {
        return res.status(400).json({ error: 'Invalid or already used faculty code' });
      }
      codeEntry.is_used = 1;
      codeEntry.used_by = id;
    }

    const profile = {
      id, email, password_hash, full_name: name || '', role: userRole,
      about: '', avatar_url: null, points: 0, warnings: 0, is_banned: 0,
      created_at: now, updated_at: now,
    };
    store.profiles.push(profile);
    saveToDisk();

    const token = jwt.sign({ id, role: userRole }, req.app.locals.JWT_SECRET, { expiresIn: '7d' });

    res.status(201).json({ token, user: mapProfile(profile, store.notes) });
  } catch (err) {
    console.error('Signup error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /api/auth/login
router.post('/login', async (req, res) => {
  try {
    const { store } = req.app.locals;
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' });
    }

    const profile = store.profiles.find(p => p.email === email);
    if (!profile) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

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

    res.json({ token, user: mapProfile(profile, store.notes) });
  } catch (err) {
    console.error('Login error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/auth/me
router.get('/me', (req, res, next) => req.app.locals.authenticateJWT(req, res, next), (req, res) => {
  try {
    const { store } = req.app.locals;
    const profile = store.profiles.find(p => p.id === req.user.id);
    if (!profile) return res.status(404).json({ error: 'User not found' });
    res.json({ user: mapProfile(profile, store.notes) });
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
    joinedAt: row.created_at ? row.created_at.split('T')[0] : '',
    score: row.points || 0, points: row.points || 0, tier: getTier(row.points || 0),
    uploads: uploadsCount, downloads: downloadsCount, warnings: row.warnings || 0,
    is_banned: row.is_banned ? true : false,
  };
}

module.exports = router;
