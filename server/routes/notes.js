const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

function auth() {
  return (req, res, next) => req.app.locals.authenticateJWT(req, res, next);
}
function admin() {
  return (req, res, next) => req.app.locals.requireAdmin(req, res, next);
}

// GET /api/notes — list notes with filters
router.get('/', auth(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const { subject, search, sortBy, limit } = req.query;

    let sql = `SELECT n.*, p.full_name AS uploader_name, p.avatar_url AS uploader_avatar
               FROM notes n
               LEFT JOIN profiles p ON n.uploader_id = p.id
               WHERE 1=1`;
    const params = [];

    if (subject && subject !== 'All') {
      sql += ' AND n.subject = ?';
      params.push(subject);
    }
    if (search) {
      sql += ' AND (n.title LIKE ? OR n.description LIKE ?)';
      params.push(`%${search}%`, `%${search}%`);
    }

    if (sortBy === 'downloads' || sortBy === 'rating') {
      sql += ' ORDER BY n.downloads DESC';
    } else {
      sql += ' ORDER BY n.created_at DESC';
    }

    if (limit) {
      sql += ' LIMIT ?';
      params.push(parseInt(limit));
    }

    const [rows] = await db.query(sql, params);
    res.json(rows.map(mapNote));
  } catch (err) {
    console.error('Fetch notes error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/notes/subjects — distinct subjects
router.get('/subjects', auth(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const [rows] = await db.query('SELECT DISTINCT subject FROM notes ORDER BY subject');
    res.json(rows.map(r => r.subject));
  } catch (err) {
    console.error('Fetch subjects error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /api/notes — upload note
router.post('/', auth(), (req, res, next) => {
  req.app.locals.upload.single('note')(req, res, next);
}, async (req, res) => {
  try {
    const db = req.app.locals.db;
    const noteId = uuidv4();
    const { title, description, subject } = req.body;

    let fileUrl = 'pending';
    let fileName = 'unknown';
    let fileType = 'application/octet-stream';
    let fileSize = 0;

    if (req.file) {
      fileUrl = `/uploads/notes/${req.file.filename}`;
      fileName = req.file.originalname;
      fileType = req.file.mimetype;
      fileSize = req.file.size;
    }

    await db.query(
      `INSERT INTO notes (id, uploader_id, title, description, subject, file_url, file_name, file_type, file_size)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [noteId, req.user.id, title, description || null, subject, fileUrl, fileName, fileType, fileSize]
    );

    // The MySQL trigger handles points — fetch the created note
    const [rows] = await db.query(
      `SELECT n.*, p.full_name AS uploader_name, p.avatar_url AS uploader_avatar
       FROM notes n LEFT JOIN profiles p ON n.uploader_id = p.id
       WHERE n.id = ?`,
      [noteId]
    );

    res.status(201).json(mapNote(rows[0]));
  } catch (err) {
    console.error('Upload note error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// DELETE /api/notes/:id
router.delete('/:id', auth(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const { id } = req.params;

    // Check ownership or admin
    const [rows] = await db.query('SELECT uploader_id FROM notes WHERE id = ?', [id]);
    if (rows.length === 0) return res.status(404).json({ error: 'Note not found' });
    if (rows[0].uploader_id !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Forbidden' });
    }

    await db.query('DELETE FROM notes WHERE id = ?', [id]);
    res.json({ success: true });
  } catch (err) {
    console.error('Delete note error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// PUT /api/notes/:id/flag
router.put('/:id/flag', auth(), admin(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const { flagged } = req.body;
    await db.query('UPDATE notes SET is_flagged = ? WHERE id = ?', [flagged ? 1 : 0, req.params.id]);
    res.json({ success: true });
  } catch (err) {
    console.error('Flag note error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// PUT /api/notes/:id/approve
router.put('/:id/approve', auth(), admin(), async (req, res) => {
  try {
    const db = req.app.locals.db;
    const { approved } = req.body;
    await db.query('UPDATE notes SET is_approved = ? WHERE id = ?', [approved ? 1 : 0, req.params.id]);
    res.json({ success: true });
  } catch (err) {
    console.error('Approve note error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

function mapNote(row) {
  const getFileTypeLabel = (mimeType) => {
    if (!mimeType) return 'FILE';
    if (mimeType.includes('pdf')) return 'PDF';
    if (mimeType.includes('word') || mimeType.includes('document')) return 'DOC';
    if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) return 'PPT';
    if (mimeType.includes('image')) return 'IMG';
    if (mimeType.includes('text')) return 'TXT';
    return 'FILE';
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  return {
    id: row.id,
    title: row.title,
    description: row.description || '',
    subject: row.subject,
    tags: row.subject ? [row.subject] : [],
    uploaderId: row.uploader_id,
    uploaderName: row.uploader_name || 'Unknown',
    createdAt: row.created_at ? new Date(row.created_at).toISOString().split('T')[0] : '',
    fileType: getFileTypeLabel(row.file_type),
    fileSize: formatFileSize(row.file_size),
    fileUrl: row.file_url,
    fileName: row.file_name,
    downloads: row.downloads || 0,
    rating: 0,
    totalRatings: 0,
    isFlagged: row.is_flagged ? true : false,
    isApproved: row.is_approved ? true : false,
    modStatus: row.is_flagged ? 'Flagged' : 'Approved',
  };
}

module.exports = router;
