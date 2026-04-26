const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

function auth() { return (req, res, next) => req.app.locals.authenticateJWT(req, res, next); }

// GET /api/messages/:groupId
router.get('/:groupId', auth(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const { groupId } = req.params;
    const limit = parseInt(req.query.limit) || 100;

    const [msgs] = await db.query(`
      SELECT * FROM (
        SELECT m.*, p.full_name as sender_name, p.avatar_url as sender_avatar
        FROM messages m
        LEFT JOIN profiles p ON m.sender_id = p.id
        WHERE m.group_id = ?
        ORDER BY m.created_at DESC
        LIMIT ?
      ) sub
      ORDER BY created_at ASC
    `, [groupId, limit]);

    res.json(msgs.map(mapMessage));
  } catch (err) { console.error('Fetch messages error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/messages/:groupId
router.post('/:groupId', auth(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const { groupId } = req.params;
    const { content } = req.body;
    const id = uuidv4();
    const now = new Date();

    const msg = { id, group_id: groupId, sender_id: req.user.id, content, file_url: null, file_name: null, file_type: null, created_at: now };
    
    await db.query('INSERT INTO messages (id, group_id, sender_id, content, file_url, file_name, file_type, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
      [id, groupId, req.user.id, content, null, null, null, now]);

    const [profiles] = await db.query('SELECT full_name, avatar_url FROM profiles WHERE id = ?', [req.user.id]);
    const sender = profiles[0] || {};
    
    const mapped = mapMessage({ ...msg, sender_name: sender.full_name, sender_avatar: sender.avatar_url });
    req.app.locals.broadcastToRoom(groupId, mapped);
    res.status(201).json(mapped);
  } catch (err) { console.error('Send message error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/messages/:groupId/file
router.post('/:groupId/file', auth(), (req, res, next) => {
  req.app.locals.upload.single('chatFile')(req, res, next);
}, async (req, res) => {
  try {
    const { db } = req.app.locals;
    const { groupId } = req.params;
    const id = uuidv4();
    if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

    const fileUrl = `/uploads/chat/${req.file.filename}`;
    const now = new Date();
    const msg = { id, group_id: groupId, sender_id: req.user.id, content: null, file_url: fileUrl, file_name: req.file.originalname, file_type: req.file.mimetype, created_at: now };
    
    await db.query('INSERT INTO messages (id, group_id, sender_id, content, file_url, file_name, file_type, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
      [id, groupId, req.user.id, null, fileUrl, req.file.originalname, req.file.mimetype, now]);

    const [profiles] = await db.query('SELECT full_name, avatar_url FROM profiles WHERE id = ?', [req.user.id]);
    const sender = profiles[0] || {};
    
    const mapped = mapMessage({ ...msg, sender_name: sender.full_name, sender_avatar: sender.avatar_url });
    req.app.locals.broadcastToRoom(groupId, mapped);
    res.status(201).json(mapped);
  } catch (err) { console.error('File message error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// DELETE /api/messages/:id
router.delete('/:id', auth(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    
    const [msgs] = await db.query('SELECT * FROM messages WHERE id = ?', [req.params.id]);
    if (msgs.length === 0) return res.status(404).json({ error: 'Message not found' });
    const msg = msgs[0];
    
    if (msg.sender_id !== req.user.id && !['superadmin', 'faculty'].includes(req.user.role)) {
      return res.status(403).json({ error: 'Forbidden' });
    }
    
    // Broadcast deletion to connected clients in that group
    req.app.locals.broadcastToRoom(msg.group_id, { id: msg.id, deleted: true });
    
    await db.query('DELETE FROM messages WHERE id = ?', [req.params.id]);
    
    res.json({ success: true });
  } catch (err) { console.error('Delete message error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

function mapMessage(row) {
  return {
    id: row.id, groupId: row.group_id, senderId: row.sender_id,
    senderName: row.sender_name || 'Unknown', content: row.file_name || row.content || '',
    timestamp: row.created_at, type: row.file_url ? 'file' : 'text',
    fileUrl: row.file_url || null, fileName: row.file_name || null,
    fileType: row.file_type || null, fileSize: '',
  };
}

module.exports = router;
