const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

function auth() { return (req, res, next) => req.app.locals.authenticateJWT(req, res, next); }
function superadmin() { return (req, res, next) => req.app.locals.requireSuperAdmin(req, res, next); }

// GET /api/complaints
router.get('/', auth(), (req, res) => {
  try {
    const { store } = req.app.locals;
    let complaints;

    if (['superadmin', 'faculty'].includes(req.user.role)) {
      complaints = [...store.complaints];
    } else {
      complaints = store.complaints.filter(c => c.student_id === req.user.id);
    }

    complaints.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    const enriched = complaints.map(c => {
      const student = store.profiles.find(p => p.id === c.student_id);
      return mapComplaint({ ...c, student_name: student?.full_name });
    });

    res.json(enriched);
  } catch (err) { console.error('Complaints error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/complaints
router.post('/', auth(), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const { title, description } = req.body;
    const now = new Date().toISOString();
    const complaint = { id: uuidv4(), student_id: req.user.id, title, description, status: 'open', admin_reply: null, resolved_by: null, created_at: now, updated_at: now };
    store.complaints.push(complaint);
    saveToDisk();

    const student = store.profiles.find(p => p.id === req.user.id);
    res.status(201).json(mapComplaint({ ...complaint, student_name: student?.full_name }));
  } catch (err) { console.error('Create complaint error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// PUT /api/complaints/:id
router.put('/:id', auth(), superadmin(), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const complaint = store.complaints.find(c => c.id === req.params.id);
    if (!complaint) return res.status(404).json({ error: 'Not found' });

    const { status, adminReply } = req.body;
    if (status) complaint.status = status;
    if (adminReply !== undefined) complaint.admin_reply = adminReply;
    if (status === 'resolved') complaint.resolved_by = req.user.id;
    complaint.updated_at = new Date().toISOString();
    saveToDisk();

    const student = store.profiles.find(p => p.id === complaint.student_id);
    res.json(mapComplaint({ ...complaint, student_name: student?.full_name }));
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
