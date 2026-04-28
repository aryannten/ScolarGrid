const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

function auth() { return (req, res, next) => req.app.locals.authenticateJWT(req, res, next); }
function superadmin() { return (req, res, next) => req.app.locals.requireSuperAdmin(req, res, next); }

// GET /api/complaints
router.get('/', auth(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    let query = 'SELECT c.*, p.full_name as student_name FROM complaints c LEFT JOIN profiles p ON c.student_id = p.id';
    const params = [];

    if (!['superadmin', 'faculty'].includes(req.user.role)) {
      query += ' WHERE c.student_id = ?';
      params.push(req.user.id);
    }

    query += ' ORDER BY c.created_at DESC';

    const [complaints] = await db.query(query, params);
    res.json(complaints.map(mapComplaint));
  } catch (err) { console.error('Complaints error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/complaints
router.post('/', auth(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const { title, description } = req.body;
    const id = uuidv4();
    const now = new Date();

    const complaint = { id, student_id: req.user.id, title, description, status: 'open', admin_reply: null, resolved_by: null, created_at: now, updated_at: now };
    
    await db.query('INSERT INTO complaints (id, student_id, title, description, status, admin_reply, resolved_by, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
      [id, req.user.id, title, description, 'open', null, null, now, now]);

    const [profiles] = await db.query('SELECT full_name FROM profiles WHERE id = ?', [req.user.id]);
    res.status(201).json(mapComplaint({ ...complaint, student_name: profiles[0]?.full_name }));
  } catch (err) { console.error('Create complaint error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// PUT /api/complaints/:id
router.put('/:id', auth(), (req, res, next) => req.app.locals.requireRoles(['superadmin', 'faculty'])(req, res, next), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const [complaints] = await db.query('SELECT * FROM complaints WHERE id = ?', [req.params.id]);
    if (complaints.length === 0) return res.status(404).json({ error: 'Not found' });
    const complaint = complaints[0];

    const { status, adminReply } = req.body;
    let updates = [];
    let values = [];
    if (status) { updates.push('status = ?'); values.push(status); }
    if (adminReply !== undefined) { updates.push('admin_reply = ?'); values.push(adminReply); }
    if (status === 'resolved') { updates.push('resolved_by = ?'); values.push(req.user.id); }
    
    updates.push('updated_at = ?'); values.push(new Date());
    
    values.push(req.params.id);
    await db.query(`UPDATE complaints SET ${updates.join(', ')} WHERE id = ?`, values);

    const [updated] = await db.query('SELECT c.*, p.full_name as student_name FROM complaints c LEFT JOIN profiles p ON c.student_id = p.id WHERE c.id = ?', [req.params.id]);
    res.json(mapComplaint(updated[0]));
  } catch (err) { console.error('Update complaint error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

function mapComplaint(row) {
  const statusMap = { open: 'Open', in_progress: 'In Progress', resolved: 'Resolved', rejected: 'Closed' };
  return {
    id: row.id, userId: row.student_id, userName: row.student_name || 'Unknown',
    category: 'General', title: row.title, description: row.description,
    status: statusMap[row.status] || row.status, priority: 'Medium',
    createdAt: row.created_at, resolvedAt: row.status === 'resolved' ? row.updated_at : null,
    adminResponse: row.admin_reply,
  };
}

module.exports = router;
