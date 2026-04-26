const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

function auth() { return (req, res, next) => req.app.locals.authenticateJWT(req, res, next); }
function roles(r) { return (req, res, next) => req.app.locals.requireRoles(r)(req, res, next); }

// GET /api/groups
router.get('/', auth(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    let query = `
      SELECT g.*, 
        (SELECT COUNT(*) FROM group_members WHERE group_id = g.id) as memberCount,
        (SELECT content FROM messages WHERE group_id = g.id ORDER BY created_at DESC LIMIT 1) as lastMsg,
        (SELECT created_at FROM messages WHERE group_id = g.id ORDER BY created_at DESC LIMIT 1) as lastMsgAt
      FROM \`groups\` g
    `;
    const params = [];

    if (!['superadmin', 'faculty'].includes(req.user.role)) {
      query += ' JOIN group_members gm ON gm.group_id = g.id WHERE gm.user_id = ?';
      params.push(req.user.id);
    }

    query += ' ORDER BY g.created_at DESC';

    const [groups] = await db.query(query, params);
    
    const enriched = groups.map(g => ({
      id: g.id, name: g.name, description: g.description || '', joinCode: g.join_code,
      members: g.memberCount, createdBy: g.created_by,
      createdAt: g.created_at ? new Date(g.created_at).toISOString().split('T')[0] : '',
      lastMessage: g.lastMsg || 'No messages yet',
      lastMessageAt: g.lastMsgAt || g.created_at,
    }));

    res.json(enriched);
  } catch (err) { console.error('Fetch groups error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/groups
router.post('/', auth(), roles(['superadmin', 'faculty']), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const { name, description } = req.body;
    const id = uuidv4();
    const joinCode = generateJoinCode();
    const now = new Date();

    await db.query('INSERT INTO \`groups\` (id, name, description, join_code, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?)', 
      [id, name, description || '', joinCode, req.user.id, now]);
    await db.query('INSERT INTO group_members (group_id, user_id, joined_at) VALUES (?, ?, ?)', 
      [id, req.user.id, now]);

    res.status(201).json({
      id, name, description: description || '', joinCode,
      members: 1, createdBy: req.user.id,
      createdAt: now.toISOString().split('T')[0],
      lastMessage: 'No messages yet',
      lastMessageAt: now,
    });
  } catch (err) { console.error('Create group error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// DELETE /api/groups/:id
router.delete('/:id', auth(), roles(['superadmin', 'faculty']), async (req, res) => {
  try {
    const { db } = req.app.locals;
    await db.query('DELETE FROM \`groups\` WHERE id = ?', [req.params.id]);
    res.json({ success: true });
  } catch (err) { console.error('Delete group error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/groups/join
router.post('/join', auth(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const { joinCode } = req.body;
    
    const [groups] = await db.query('SELECT * FROM \`groups\` WHERE join_code = ?', [joinCode.trim().toUpperCase()]);
    if (groups.length === 0) return res.status(404).json({ error: 'Invalid join code. Group not found.' });
    const group = groups[0];

    const [existing] = await db.query('SELECT * FROM group_members WHERE group_id = ? AND user_id = ?', [group.id, req.user.id]);
    if (existing.length > 0) return res.status(409).json({ error: 'You are already a member of this group.' });

    await db.query('INSERT INTO group_members (group_id, user_id, joined_at) VALUES (?, ?, ?)', [group.id, req.user.id, new Date()]);
    res.json(group);
  } catch (err) { console.error('Join group error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

function generateJoinCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  const prefixes = ['GRP', 'STD', 'DSC'];
  const pfx = prefixes[Math.floor(Math.random() * prefixes.length)];
  let code = '';
  for (let i = 0; i < 3; i++) code += chars[Math.floor(Math.random() * chars.length)];
  return `${pfx}-2026-${code}`;
}

module.exports = router;
