const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

function auth() { return (req, res, next) => req.app.locals.authenticateJWT(req, res, next); }
function roles(r) { return (req, res, next) => req.app.locals.requireRoles(r)(req, res, next); }

// GET /api/groups
router.get('/', auth(), (req, res) => {
  try {
    const { store } = req.app.locals;
    let groups;

    if (['superadmin', 'faculty'].includes(req.user.role)) {
      groups = [...store.groups];
    } else {
      const memberGroupIds = store.group_members.filter(gm => gm.user_id === req.user.id).map(gm => gm.group_id);
      groups = store.groups.filter(g => memberGroupIds.includes(g.id));
    }

    groups.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    const enriched = groups.map(g => {
      const memberCount = store.group_members.filter(gm => gm.group_id === g.id).length;
      const groupMsgs = store.messages.filter(m => m.group_id === g.id).sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      const lastMsg = groupMsgs[0] || null;
      return mapGroup(g, memberCount, lastMsg);
    });

    res.json(enriched);
  } catch (err) { console.error('Fetch groups error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/groups
router.post('/', auth(), roles(['superadmin', 'faculty']), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const { name, description } = req.body;
    const id = uuidv4();
    const joinCode = generateJoinCode();
    const now = new Date().toISOString();

    const group = { id, name, description: description || '', join_code: joinCode, created_by: req.user.id, created_at: now };
    store.groups.push(group);
    store.group_members.push({ group_id: id, user_id: req.user.id, joined_at: now });
    saveToDisk();

    res.status(201).json(mapGroup(group, 1, null));
  } catch (err) { console.error('Create group error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// DELETE /api/groups/:id
router.delete('/:id', auth(), roles(['superadmin', 'faculty']), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    store.groups = store.groups.filter(g => g.id !== req.params.id);
    store.group_members = store.group_members.filter(gm => gm.group_id !== req.params.id);
    store.messages = store.messages.filter(m => m.group_id !== req.params.id);
    saveToDisk();
    res.json({ success: true });
  } catch (err) { console.error('Delete group error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/groups/join
router.post('/join', auth(), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const { joinCode } = req.body;
    const group = store.groups.find(g => g.join_code === joinCode.trim().toUpperCase());
    if (!group) return res.status(404).json({ error: 'Invalid join code. Group not found.' });

    const existing = store.group_members.find(gm => gm.group_id === group.id && gm.user_id === req.user.id);
    if (existing) return res.status(409).json({ error: 'You are already a member of this group.' });

    store.group_members.push({ group_id: group.id, user_id: req.user.id, joined_at: new Date().toISOString() });
    saveToDisk();
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

function mapGroup(g, memberCount, lastMsg) {
  return {
    id: g.id, name: g.name, description: g.description || '', joinCode: g.join_code,
    members: memberCount, createdBy: g.created_by,
    createdAt: g.created_at ? g.created_at.split('T')[0] : '',
    lastMessage: lastMsg?.content || 'No messages yet',
    lastMessageAt: lastMsg?.created_at || g.created_at,
  };
}

module.exports = router;
