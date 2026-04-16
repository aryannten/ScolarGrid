const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');

// POST /api/auth/signup
router.post('/signup', async (req, res) => {
  try {
    const db = req.app.locals.db;
    const { name, email, password, role } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' });
    }

    // Check if email already exists
    const [existing] = await db.query('SELECT id FROM profiles WHERE email = ?', [email]);
    if (existing.length > 0) {
      return res.status(409).json({ error: 'Email already registered' });
    }

    const id = uuidv4();
    const passwordHash = await bcrypt.hash(password, 10);
    const userRole = role || 'student';

    await db.query(
      `INSERT INTO profiles (id, email, password_hash, full_name, role)
       VALUES (?, ?, ?, ?, ?)`,
      [id, email, passwordHash, name || '', userRole]
    );

    const token = jwt.sign({ id, role: userRole }, req.app.locals.JWT_SECRET, { expiresIn: '7d' });

    const [rows] = await db.query('SELECT * FROM profiles WHERE id = ?', [id]);
    const profile = rows[0];

    res.status(201).json({
      token,
      user: mapProfile(profile),
    });
  } catch (err) {
    console.error('Signup error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /api/auth/login
router.post('/login', async (req, res) => {
  try {
    const db = req.app.locals.db;
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' });
    }

    const [rows] = await db.query('SELECT * FROM profiles WHERE email = ?', [email]);
    if (rows.length === 0) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    const profile = rows[0];

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

    res.json({
      token,
      user: mapProfile(profile),
    });
  } catch (err) {
    console.error('Login error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/auth/me
router.get('/me', req_app_locals_auth(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const [rows] = await db.query('SELECT * FROM profiles WHERE id = ?', [req.user.id]);
    if (rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }
    res.json({ user: mapProfile(rows[0]) });
  } catch (err) {
    console.error('Me error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Middleware helper — returns the authenticateJWT function
function req_app_locals_auth() {
  return (req, res, next) => {
    return req.app.locals.authenticateJWT(req, res, next);
  };
}

function mapProfile(row) {
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
  };
}

module.exports = router;
