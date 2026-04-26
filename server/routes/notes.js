const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

function auth() { return (req, res, next) => req.app.locals.authenticateJWT(req, res, next); }
function roles(r) { return (req, res, next) => req.app.locals.requireRoles(r)(req, res, next); }

// GET /api/notes
router.get('/', auth(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const { subject, search, sortBy, limit } = req.query;

    let query = `
      SELECT n.*, p.full_name as uploader_name, p.avatar_url as uploader_avatar,
        (SELECT AVG(rating) FROM note_ratings WHERE note_id = n.id) as avg_rating,
        (SELECT COUNT(*) FROM note_ratings WHERE note_id = n.id) as rating_count
      FROM notes n
      LEFT JOIN profiles p ON n.uploader_id = p.id
      WHERE 1=1
    `;
    const params = [];

    if (subject && subject !== 'All') {
      query += ' AND n.subject = ?';
      params.push(subject);
    }
    if (search) {
      query += ' AND (LOWER(n.title) LIKE ? OR LOWER(n.description) LIKE ?)';
      params.push(`%${search.toLowerCase()}%`, `%${search.toLowerCase()}%`);
    }

    if (sortBy === 'downloads') query += ' ORDER BY n.downloads DESC';
    else if (sortBy === 'rating') query += ' ORDER BY avg_rating DESC';
    else query += ' ORDER BY n.created_at DESC';

    if (limit) {
      query += ' LIMIT ?';
      params.push(parseInt(limit));
    }

    const [notes] = await db.query(query, params);
    res.json(notes.map(mapNote));
  } catch (err) { console.error('Fetch notes error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// GET /api/notes/subjects
router.get('/subjects', auth(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const [rows] = await db.query('SELECT DISTINCT subject FROM notes ORDER BY subject');
    res.json(rows.map(r => r.subject));
  } catch (err) { console.error('Subjects error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/notes
router.post('/', auth(), (req, res, next) => {
  req.app.locals.upload.single('note')(req, res, next);
}, async (req, res) => {
  try {
    const { db } = req.app.locals;
    const noteId = uuidv4();
    const { title, description, subject } = req.body;
    const now = new Date();

    const note = {
      id: noteId, uploader_id: req.user.id, title, description: description || '',
      subject: subject || 'General',
      file_url: req.file ? `/uploads/notes/${req.file.filename}` : 'pending',
      file_name: req.file ? req.file.originalname : 'unknown',
      file_type: req.file ? req.file.mimetype : 'application/octet-stream',
      file_size: req.file ? req.file.size : 0,
      is_flagged: 0, is_approved: 1, downloads: 0, created_at: now,
    };

    await db.query(`
      INSERT INTO notes (id, uploader_id, title, description, subject, file_url, file_name, file_type, file_size, is_flagged, is_approved, downloads, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [note.id, note.uploader_id, note.title, note.description, note.subject, note.file_url, note.file_name, note.file_type, note.file_size, note.is_flagged, note.is_approved, note.downloads, note.created_at]);

    // Award points
    await db.query('INSERT INTO leaderboard_points (id, user_id, points, reason, reference_id, created_at) VALUES (?, ?, ?, ?, ?, ?)', [uuidv4(), req.user.id, 10, 'note_upload', noteId, now]);
    await db.query('UPDATE profiles SET points = points + 10 WHERE id = ?', [req.user.id]);

    const [profiles] = await db.query('SELECT * FROM profiles WHERE id = ?', [req.user.id]);
    const uploader = profiles[0];
    res.status(201).json(mapNote({ ...note, uploader_name: uploader?.full_name || 'Unknown', uploader_avatar: uploader?.avatar_url, avg_rating: 0, rating_count: 0 }));
  } catch (err) { console.error('Upload note error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// DELETE /api/notes/:id
router.delete('/:id', auth(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const [notes] = await db.query('SELECT * FROM notes WHERE id = ?', [req.params.id]);
    if (notes.length === 0) return res.status(404).json({ error: 'Note not found' });
    const note = notes[0];
    
    if (note.uploader_id !== req.user.id && !['superadmin', 'faculty'].includes(req.user.role)) return res.status(403).json({ error: 'Forbidden' });
    await db.query('DELETE FROM notes WHERE id = ?', [req.params.id]);
    res.json({ success: true });
  } catch (err) { console.error('Delete note error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// PUT /api/notes/:id/flag
router.put('/:id/flag', auth(), roles(['superadmin', 'faculty']), async (req, res) => {
  try {
    const { db } = req.app.locals;
    await db.query('UPDATE notes SET is_flagged = ? WHERE id = ?', [req.body.flagged ? 1 : 0, req.params.id]);
    res.json({ success: true });
  } catch (err) { console.error('Flag error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// PUT /api/notes/:id/approve
router.put('/:id/approve', auth(), roles(['superadmin', 'faculty']), async (req, res) => {
  try {
    const { db } = req.app.locals;
    await db.query('UPDATE notes SET is_approved = ? WHERE id = ?', [req.body.approved ? 1 : 0, req.params.id]);
    res.json({ success: true });
  } catch (err) { console.error('Approve error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/notes/:id/rate
router.post('/:id/rate', auth(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const { rating } = req.body;
    if (!rating || rating < 1 || rating > 5) return res.status(400).json({ error: 'Rating must be 1-5' });

    const [existing] = await db.query('SELECT id FROM note_ratings WHERE note_id = ? AND user_id = ?', [req.params.id, req.user.id]);
    if (existing.length > 0) {
      await db.query('UPDATE note_ratings SET rating = ? WHERE id = ?', [rating, existing[0].id]);
    } else {
      await db.query('INSERT INTO note_ratings (id, note_id, user_id, rating, created_at) VALUES (?, ?, ?, ?, ?)', [uuidv4(), req.params.id, req.user.id, rating, new Date()]);
    }
    res.json({ success: true });
  } catch (err) { console.error('Rate error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// GET /api/notes/:id/download
router.get('/:id/download', auth(), async (req, res) => {
  try {
    const { db } = req.app.locals;
    const [notes] = await db.query('SELECT * FROM notes WHERE id = ?', [req.params.id]);
    if (notes.length === 0) return res.status(404).json({ error: 'Note not found' });
    const note = notes[0];
    
    await db.query('UPDATE notes SET downloads = downloads + 1 WHERE id = ?', [note.id]);
    
    if (note.uploader_id !== req.user.id) {
      await db.query('UPDATE profiles SET points = points + 2 WHERE id = ?', [note.uploader_id]);
      await db.query('INSERT INTO leaderboard_points (id, user_id, points, reason, reference_id, created_at) VALUES (?, ?, ?, ?, ?, ?)', [uuidv4(), note.uploader_id, 2, 'note_download', note.id, new Date()]);
    }

    return res.json({ success: true, fileUrl: note.file_url });
  } catch (err) {
    console.error('Download metadata error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

function mapNote(row) {
  const getFileTypeLabel = (mt) => { if (!mt) return 'FILE'; if (mt.includes('pdf')) return 'PDF'; if (mt.includes('word') || mt.includes('document')) return 'DOC'; if (mt.includes('presentation')) return 'PPT'; if (mt.includes('image')) return 'IMG'; if (mt.includes('text')) return 'TXT'; return 'FILE'; };
  const formatFileSize = (b) => { if (!b) return '0 B'; const s = ['B','KB','MB','GB']; const i = Math.floor(Math.log(b)/Math.log(1024)); return `${(b/Math.pow(1024,i)).toFixed(1)} ${s[i]}`; };
  return {
    id: row.id, title: row.title, description: row.description || '', subject: row.subject,
    tags: row.subject ? [row.subject] : [], uploaderId: row.uploader_id,
    uploaderName: row.uploader_name || 'Unknown',
    createdAt: row.created_at ? new Date(row.created_at).toISOString().split('T')[0] : '',
    fileType: getFileTypeLabel(row.file_type), fileSize: formatFileSize(row.file_size),
    fileUrl: row.file_url, fileName: row.file_name,
    downloads: row.downloads || 0, rating: row.avg_rating ? parseFloat(row.avg_rating) : 0,
    totalRatings: row.rating_count || 0, isFlagged: row.is_flagged ? true : false,
    isApproved: row.is_approved ? true : false, modStatus: row.is_flagged ? 'Flagged' : 'Approved',
  };
}

module.exports = router;
