const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

function auth() { return (req, res, next) => req.app.locals.authenticateJWT(req, res, next); }

// GET /api/messages/:groupId
router.get('/:groupId', auth(), (req, res) => {
  try {
    const { store } = req.app.locals;
    const { groupId } = req.params;
    const limit = parseInt(req.query.limit) || 100;

    const msgs = store.messages
      .filter(m => m.group_id === groupId)
      .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
      .slice(-limit);

    const enriched = msgs.map(m => {
      const sender = store.profiles.find(p => p.id === m.sender_id);
      return mapMessage({ ...m, sender_name: sender?.full_name, sender_avatar: sender?.avatar_url });
    });

    res.json(enriched);
  } catch (err) { console.error('Fetch messages error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/messages/:groupId
router.post('/:groupId', auth(), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const { groupId } = req.params;
    const { content } = req.body;
    const id = uuidv4();
    const now = new Date().toISOString();

    const msg = { id, group_id: groupId, sender_id: req.user.id, content, file_url: null, file_name: null, file_type: null, created_at: now };
    store.messages.push(msg);
    saveToDisk();

    const sender = store.profiles.find(p => p.id === req.user.id);
    const mapped = mapMessage({ ...msg, sender_name: sender?.full_name, sender_avatar: sender?.avatar_url });
    req.app.locals.broadcastToRoom(groupId, mapped);
    res.status(201).json(mapped);
  } catch (err) { console.error('Send message error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/messages/:groupId/file
router.post('/:groupId/file', auth(), (req, res, next) => {
  req.app.locals.upload.single('chatFile')(req, res, next);
}, (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const { groupId } = req.params;
    const id = uuidv4();
    if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

    const fileUrl = `/uploads/chat/${req.file.filename}`;
    const now = new Date().toISOString();
    const msg = { id, group_id: groupId, sender_id: req.user.id, content: null, file_url: fileUrl, file_name: req.file.originalname, file_type: req.file.mimetype, created_at: now };
    store.messages.push(msg);
    saveToDisk();

    const sender = store.profiles.find(p => p.id === req.user.id);
    const mapped = mapMessage({ ...msg, sender_name: sender?.full_name, sender_avatar: sender?.avatar_url });
    req.app.locals.broadcastToRoom(groupId, mapped);
    res.status(201).json(mapped);
  } catch (err) { console.error('File message error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// DELETE /api/messages/:id
router.delete('/:id', auth(), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const idx = store.messages.findIndex(m => m.id === req.params.id);
    if (idx === -1) return res.status(404).json({ error: 'Message not found' });
    
    const msg = store.messages[idx];
    if (msg.sender_id !== req.user.id && !['superadmin', 'faculty'].includes(req.user.role)) {
      return res.status(403).json({ error: 'Forbidden' });
    }
    
    // Broadcast deletion to connected clients in that group
    req.app.locals.broadcastToRoom(msg.group_id, { id: msg.id, deleted: true });
    
    store.messages.splice(idx, 1);
    saveToDisk();
    
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
