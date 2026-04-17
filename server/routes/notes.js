const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

function auth() { return (req, res, next) => req.app.locals.authenticateJWT(req, res, next); }
function roles(r) { return (req, res, next) => req.app.locals.requireRoles(r)(req, res, next); }

// GET /api/notes
router.get('/', auth(), (req, res) => {
  try {
    const { store } = req.app.locals;
    const { subject, search, sortBy, limit } = req.query;

    let notes = [...store.notes];

    if (subject && subject !== 'All') {
      notes = notes.filter(n => n.subject === subject);
    }
    if (search) {
      const s = search.toLowerCase();
      notes = notes.filter(n => (n.title || '').toLowerCase().includes(s) || (n.description || '').toLowerCase().includes(s));
    }

    // Enrich with uploader info and ratings
    const enriched = notes.map(n => {
      const uploader = store.profiles.find(p => p.id === n.uploader_id);
      const ratings = store.note_ratings.filter(r => r.note_id === n.id);
      const avgRating = ratings.length > 0 ? ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length : 0;
      return { ...n, uploader_name: uploader?.full_name || 'Unknown', uploader_avatar: uploader?.avatar_url, avg_rating: avgRating, rating_count: ratings.length };
    });

    if (sortBy === 'downloads') enriched.sort((a, b) => b.downloads - a.downloads);
    else if (sortBy === 'rating') enriched.sort((a, b) => b.avg_rating - a.avg_rating);
    else enriched.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    const result = limit ? enriched.slice(0, parseInt(limit)) : enriched;
    res.json(result.map(mapNote));
  } catch (err) { console.error('Fetch notes error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// GET /api/notes/subjects
router.get('/subjects', auth(), (req, res) => {
  try {
    const { store } = req.app.locals;
    const subjects = [...new Set(store.notes.map(n => n.subject))].sort();
    res.json(subjects);
  } catch (err) { console.error('Subjects error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/notes
router.post('/', auth(), (req, res, next) => {
  req.app.locals.upload.single('note')(req, res, next);
}, (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const noteId = uuidv4();
    const { title, description, subject } = req.body;
    const now = new Date().toISOString();

    const note = {
      id: noteId, uploader_id: req.user.id, title, description: description || '',
      subject: subject || 'General',
      file_url: req.file ? `/uploads/notes/${req.file.filename}` : 'pending',
      file_name: req.file ? req.file.originalname : 'unknown',
      file_type: req.file ? req.file.mimetype : 'application/octet-stream',
      file_size: req.file ? req.file.size : 0,
      is_flagged: 0, is_approved: 1, downloads: 0, created_at: now,
    };
    store.notes.push(note);

    // Award points
    store.leaderboard_points.push({ id: uuidv4(), user_id: req.user.id, points: 10, reason: 'note_upload', reference_id: noteId, created_at: now });
    const profile = store.profiles.find(p => p.id === req.user.id);
    if (profile) profile.points = (profile.points || 0) + 10;

    saveToDisk();

    const uploader = store.profiles.find(p => p.id === req.user.id);
    res.status(201).json(mapNote({ ...note, uploader_name: uploader?.full_name || 'Unknown', uploader_avatar: uploader?.avatar_url, avg_rating: 0, rating_count: 0 }));
  } catch (err) { console.error('Upload note error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// DELETE /api/notes/:id
router.delete('/:id', auth(), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const idx = store.notes.findIndex(n => n.id === req.params.id);
    if (idx === -1) return res.status(404).json({ error: 'Note not found' });
    const note = store.notes[idx];
    if (note.uploader_id !== req.user.id && !['superadmin', 'faculty'].includes(req.user.role)) return res.status(403).json({ error: 'Forbidden' });
    store.notes.splice(idx, 1);
    store.note_ratings = store.note_ratings.filter(r => r.note_id !== req.params.id);
    saveToDisk();
    res.json({ success: true });
  } catch (err) { console.error('Delete note error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// PUT /api/notes/:id/flag
router.put('/:id/flag', auth(), roles(['superadmin', 'faculty']), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const note = store.notes.find(n => n.id === req.params.id);
    if (note) { note.is_flagged = req.body.flagged ? 1 : 0; saveToDisk(); }
    res.json({ success: true });
  } catch (err) { console.error('Flag error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// PUT /api/notes/:id/approve
router.put('/:id/approve', auth(), roles(['superadmin', 'faculty']), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const note = store.notes.find(n => n.id === req.params.id);
    if (note) { note.is_approved = req.body.approved ? 1 : 0; saveToDisk(); }
    res.json({ success: true });
  } catch (err) { console.error('Approve error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// POST /api/notes/:id/rate
router.post('/:id/rate', auth(), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const { rating, review } = req.body;
    if (!rating || rating < 1 || rating > 5) return res.status(400).json({ error: 'Rating must be 1-5' });

    const existing = store.note_ratings.find(r => r.note_id === req.params.id && r.user_id === req.user.id);
    if (existing) {
      existing.rating = rating;
      existing.review = review || null;
    } else {
      store.note_ratings.push({ id: uuidv4(), note_id: req.params.id, user_id: req.user.id, rating, review: review || null, created_at: new Date().toISOString() });
    }
    saveToDisk();
    res.json({ success: true });
  } catch (err) { console.error('Rate error:', err); res.status(500).json({ error: 'Internal server error' }); }
});

// GET /api/notes/:id/download
router.get('/:id/download', auth(), (req, res) => {
  try {
    const { store, saveToDisk } = req.app.locals;
    const note = store.notes.find(n => n.id === req.params.id);
    if (!note) return res.status(404).json({ error: 'Note not found' });
    
    note.downloads = (note.downloads || 0) + 1;
    saveToDisk();
    
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
    createdAt: row.created_at ? row.created_at.split('T')[0] : '',
    fileType: getFileTypeLabel(row.file_type), fileSize: formatFileSize(row.file_size),
    fileUrl: row.file_url, fileName: row.file_name,
    downloads: row.downloads || 0, rating: row.avg_rating ? parseFloat(row.avg_rating) : 0,
    totalRatings: row.rating_count || 0, isFlagged: row.is_flagged ? true : false,
    isApproved: row.is_approved ? true : false, modStatus: row.is_flagged ? 'Flagged' : 'Approved',
  };
}

module.exports = router;
