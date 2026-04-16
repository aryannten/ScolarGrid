const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

function auth() {
  return (req, res, next) => req.app.locals.authenticateJWT(req, res, next);
}
function admin() {
  return (req, res, next) => req.app.locals.requireAdmin(req, res, next);
}

// GET /api/complaints
router.get('/', auth(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    let rows;

    if (req.user.role === 'admin') {
      [rows] = await db.query(
        `SELECT c.*, p.full_name AS student_name
         FROM complaints c
         LEFT JOIN profiles p ON c.student_id = p.id
         ORDER BY c.created_at DESC`
      );
    } else {
      [rows] = await db.query(
        `SELECT c.*, p.full_name AS student_name
         FROM complaints c
         LEFT JOIN profiles p ON c.student_id = p.id
         WHERE c.student_id = ?
         ORDER BY c.created_at DESC`,
        [req.user.id]
      );
    }

    res.json(rows.map(mapComplaint));
  } catch (err) {
    console.error('Fetch complaints error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /api/complaints
router.post('/', auth(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const { title, description } = req.body;
    const id = uuidv4();

    await db.query(
      'INSERT INTO complaints (id, student_id, title, description) VALUES (?, ?, ?, ?)',
      [id, req.user.id, title, description]
    );

    const [rows] = await db.query(
      `SELECT c.*, p.full_name AS student_name
       FROM complaints c LEFT JOIN profiles p ON c.student_id = p.id
       WHERE c.id = ?`,
      [id]
    );

    res.status(201).json(mapComplaint(rows[0]));
  } catch (err) {
    console.error('Create complaint error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// PUT /api/complaints/:id
router.put('/:id', auth(), admin(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const { status, adminReply } = req.body;

    const updates = [];
    const params = [];

    if (status) {
      updates.push('status = ?');
      params.push(status);
    }
    if (adminReply !== undefined) {
      updates.push('admin_reply = ?');
      params.push(adminReply);
    }
    if (status === 'resolved') {
      updates.push('resolved_by = ?');
      params.push(req.user.id);
    }

    if (updates.length === 0) {
      return res.status(400).json({ error: 'No fields to update' });
    }

    params.push(req.params.id);
    await db.query(`UPDATE complaints SET ${updates.join(', ')} WHERE id = ?`, params);

    const [rows] = await db.query(
      `SELECT c.*, p.full_name AS student_name
       FROM complaints c LEFT JOIN profiles p ON c.student_id = p.id
       WHERE c.id = ?`,
      [req.params.id]
    );

    res.json(mapComplaint(rows[0]));
  } catch (err) {
    console.error('Update complaint error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

function mapComplaint(row) {
  const statusMap = {
    open: 'Open',
    in_progress: 'In Progress',
    resolved: 'Resolved',
    rejected: 'Closed',
  };

  return {
    id: row.id,
    userId: row.student_id,
    userName: row.student_name || 'Unknown',
    category: 'General',
    title: row.title,
    description: row.description,
    status: statusMap[row.status] || row.status,
    priority: 'Medium',
    createdAt: row.created_at,
    resolvedAt: row.status === 'resolved' ? row.updated_at : null,
    adminResponse: row.admin_reply,
  };
}

module.exports = router;
