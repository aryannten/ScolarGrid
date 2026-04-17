require('dotenv').config();
const express = require('express');
const http = require('http');
const path = require('path');
const cors = require('cors');
const WebSocket = require('ws');
const mysql = require('mysql2/promise');
const multer = require('multer');
const fs = require('fs');

const app = express();
const server = http.createServer(app);

// ── Middleware ──────────────────────────────────────────────
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// ── Static file serving ────────────────────────────────────
const uploadsDir = path.join(__dirname, 'public', 'uploads');
['avatars', 'notes', 'chat'].forEach(dir => {
  const p = path.join(uploadsDir, dir);
  if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true });
});
app.use('/uploads', express.static(path.join(__dirname, 'public', 'uploads')));

// ── MySQL Connection Pool ──────────────────────────────────
const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'scholargrid',
  waitForConnections: true,
  connectionLimit: 10,
  charset: 'utf8mb4',
});

// Make pool available to routes
app.locals.db = pool;

// ── Multer Config ──────────────────────────────────────────
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    if (file.fieldname === 'avatar') cb(null, path.join(uploadsDir, 'avatars'));
    else if (file.fieldname === 'note') cb(null, path.join(uploadsDir, 'notes'));
    else cb(null, path.join(uploadsDir, 'chat'));
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, uniqueSuffix + path.extname(file.originalname));
  }
});
const upload = multer({ storage, limits: { fileSize: 50 * 1024 * 1024 } }); // 50MB limit
app.locals.upload = upload;

// ── JWT Middleware ──────────────────────────────────────────
const jwt = require('jsonwebtoken');
const JWT_SECRET = process.env.JWT_SECRET || 'fallback-secret';

function authenticateJWT(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: 'Missing token' });

  const token = authHeader.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Missing token' });

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'Invalid or expired token' });
    req.user = user; // { id, role }
    next();
  });
}

function requireSuperAdmin(req, res, next) {
  if (req.user.role !== 'superadmin') return res.status(403).json({ error: 'Superadmin only' });
  next();
}

function requireRoles(roles) {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
}

app.locals.authenticateJWT = authenticateJWT;
app.locals.requireSuperAdmin = requireSuperAdmin;
app.locals.requireRoles = requireRoles;
app.locals.JWT_SECRET = JWT_SECRET;

// ── WebSocket Server ───────────────────────────────────────
const wss = new WebSocket.Server({ server });
const rooms = new Map(); // groupId -> Set(ws)

wss.on('connection', (ws) => {
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      if (data.type === 'join_room') {
        ws.groupId = data.groupId;
        if (!rooms.has(data.groupId)) rooms.set(data.groupId, new Set());
        rooms.get(data.groupId).add(ws);
      }
    } catch (e) {
      console.error('WS message parse error:', e);
    }
  });

  ws.on('close', () => {
    if (ws.groupId && rooms.has(ws.groupId)) {
      rooms.get(ws.groupId).delete(ws);
      if (rooms.get(ws.groupId).size === 0) rooms.delete(ws.groupId);
    }
  });
});

function broadcastToRoom(groupId, messageData) {
  if (rooms.has(groupId)) {
    const payload = JSON.stringify({ type: 'new_message', payload: messageData });
    for (const client of rooms.get(groupId)) {
      if (client.readyState === WebSocket.OPEN) {
        client.send(payload);
      }
    }
  }
}
app.locals.broadcastToRoom = broadcastToRoom;

// ── Routes ─────────────────────────────────────────────────
app.use('/api/auth', require('./routes/auth'));
app.use('/api/users', require('./routes/users'));
app.use('/api/notes', require('./routes/notes'));
app.use('/api/groups', require('./routes/groups'));
app.use('/api/messages', require('./routes/messages'));
app.use('/api/leaderboard', require('./routes/leaderboard'));
app.use('/api/complaints', require('./routes/complaints'));
app.use('/api/analytics', require('./routes/analytics'));

// Health check
app.get('/api/health', (req, res) => res.json({ status: 'ok', time: new Date().toISOString() }));

// ── Start ──────────────────────────────────────────────────
const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`✅ ScholarGrid API running on http://localhost:${PORT}`);
  console.log(`📡 WebSocket server ready`);
});
