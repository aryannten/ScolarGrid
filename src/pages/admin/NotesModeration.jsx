import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import { fetchNotes, fetchSubjects, uploadNote, rateNote, flagNote, deleteNote } from '../../services/notesService';
import { FileText, Download, Star, Search, Grid3X3, List, Upload, X, Clock, User, ChevronDown, Trash2, Flag } from 'lucide-react';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };
const DEFAULT_SUBJECTS = ['Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'Electrical Engineering', 'Mechanical Engineering', 'Biology', 'Economics'];

export default function NotesModeration() {
  const { user, isSuperAdmin, isFaculty } = useAuth();
  const [notes, setNotes] = useState([]);
  const [subjects, setSubjects] = useState(DEFAULT_SUBJECTS);
  const [search, setSearch] = useState('');
  const [subject, setSubject] = useState('All');
  const [viewMode, setViewMode] = useState('grid');
  const [showUpload, setShowUpload] = useState(false);
  const [sortBy, setSortBy] = useState('top-rated');
  const [uploadForm, setUploadForm] = useState({ title: '', description: '', subject: '' });
  const [uploadFile, setUploadFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  // Review Modal state
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [reviewNoteId, setReviewNoteId] = useState(null);
  const [reviewScore, setReviewScore] = useState(5);
  const [reviewText, setReviewText] = useState('');

  useEffect(() => {
    loadNotes();
    loadSubjects();
  }, [subject, sortBy]);

  const loadNotes = async () => {
    try {
      setLoading(true);
      const data = await fetchNotes({ subject, search, sortBy: sortBy === 'top-rated' ? 'rating' : sortBy });
      setNotes(data);
    } catch (err) {
      console.error('Error loading notes:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadSubjects = async () => {
    try {
      const s = await fetchSubjects();
      if (s.length > 0) setSubjects(s);
    } catch (err) {}
  };

  useEffect(() => {
    const timer = setTimeout(() => loadNotes(), 300);
    return () => clearTimeout(timer);
  }, [search]);

  const filtered = notes.filter(n => n.title.toLowerCase().includes(search.toLowerCase()) || n.description.toLowerCase().includes(search.toLowerCase()));

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!user) return;
    setUploading(true);
    try {
      const newNote = await uploadNote(user.id, uploadForm, uploadFile);
      setNotes([newNote, ...notes]);
      setShowUpload(false);
      setUploadForm({ title: '', description: '', subject: '' });
      setUploadFile(null);
    } catch (err) {
      alert('Upload failed: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  // Moderation Handlers
  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to permanently delete this note?')) return;
    try {
      await deleteNote(id);
      setNotes(notes.filter(n => n.id !== id));
    } catch (err) {
      alert('Delete failed: ' + err.message);
    }
  };

  const handleFlag = async (id) => {
    const note = notes.find(n => n.id === id);
    if (!note) return;
    const newFlagged = !note.isFlagged;
    try {
      await flagNote(id, newFlagged);
      setNotes(notes.map(n => n.id === id ? { ...n, isFlagged: newFlagged, modStatus: newFlagged ? 'Flagged' : 'Approved' } : n));
    } catch (err) {
      alert('Flag failed: ' + err.message);
    }
  };

  const handleDownload = async (id, fileUrl) => {
    try {
      // Record download locally
      const token = localStorage.getItem('sg_token');
      const res = await fetch(`/api/notes/${id}/download`, {
        headers: { ...(token ? { 'Authorization': `Bearer ${token}` } : {}) }
      });
      if (res.ok) {
        setNotes(notes.map(n => n.id === id ? { ...n, downloads: n.downloads + 1 } : n));
      }
      // Actual download action bypassing Vite proxy intercept explicitly
      const link = document.createElement('a');
      link.href = fileUrl;
      link.download = '';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error('Download error', err);
    }
  };

  const submitReview = async () => {
    if (!reviewNoteId) return;
    try {
      await rateNote(reviewNoteId, reviewScore, reviewText);
      setNotes(notes.map(n => n.id === reviewNoteId ? { ...n, rating: reviewScore, totalRatings: n.totalRatings + 1 } : n));
      setShowReviewModal(false);
      setReviewText('');
    } catch (err) {
      alert('Failed to submit review: ' + err.message);
    }
  };

  const renderStars = (rating) => (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map(i => (
        <Star key={i} className={`w-3.5 h-3.5 ${i <= Math.round(rating) ? 'text-gold-400 fill-gold-400' : 'text-gray-300 dark:text-gray-600'}`} />
      ))}
      <span className="text-xs text-gray-500 ml-1">{rating ? rating.toFixed(1) : 0}</span>
    </div>
  );

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item} className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="page-title">Notes Mastery</h1>
          <p className="page-subtitle">Manage, moderate, and upload academic resources</p>
        </div>
        <button onClick={() => setShowUpload(true)} className="btn-primary flex items-center gap-2">
          <Upload className="w-4 h-4" /> Upload Note
        </button>
      </motion.div>

      <motion.div variants={item} className="glass-card p-4 flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search notes..." className="input-field pl-10" />
        </div>
        <div className="flex gap-3 relative">
          <div className="relative">
            <select value={subject} onChange={e => setSubject(e.target.value)} className="input-field pr-10 appearance-none min-w-[150px]">
              <option value="All">All Subjects</option>
              {subjects.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
          <div className="relative">
            <select value={sortBy} onChange={e => setSortBy(e.target.value)} className="input-field pr-10 appearance-none min-w-[130px]">
              <option value="top-rated">Top Rated</option>
              <option value="recent">Most Recent</option>
              <option value="downloads">Most Downloaded</option>
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
        </div>
      </motion.div>

      {loading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1,2,3,4,5,6].map(i => <div key={i} className="h-48 rounded-2xl bg-gray-100 dark:bg-dark-surface animate-pulse" />)}
        </div>
      ) : (
        <motion.div variants={container} className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(note => (
            <motion.div key={note.id} variants={item} className={`glass-card-hover p-5 flex flex-col relative ${note.isFlagged ? 'border-orange-500/50 dark:border-orange-500/30 bg-orange-50/50 dark:bg-orange-900/10' : ''}`}>
              
              {/* Admin Actions */}
              <div className="absolute top-3 right-3 flex gap-1 z-10">
                <button onClick={() => handleFlag(note.id)} className="p-1.5 rounded-lg bg-light-surface/80 dark:bg-dark-surface/80 hover:bg-orange-100 dark:hover:bg-orange-900/40 text-gray-400 hover:text-orange-500 backdrop-blur-md transition-colors" title={note.isFlagged ? "Unflag" : "Flag as inappropriate"}>
                  <Flag className={`w-4 h-4 ${note.isFlagged ? 'text-orange-500 fill-orange-500' : ''}`} />
                </button>
                <button onClick={() => handleDelete(note.id)} className="p-1.5 rounded-lg bg-light-surface/80 dark:bg-dark-surface/80 hover:bg-red-100 dark:hover:bg-red-900/40 text-gray-400 hover:text-red-500 backdrop-blur-md transition-colors" title="Delete Note">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div className="flex items-start justify-between mb-3 pr-20">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                  note.fileType === 'PDF' ? 'bg-red-50 dark:bg-red-900/20 text-red-500' :
                  note.fileType === 'PPT' ? 'bg-orange-50 dark:bg-orange-900/20 text-orange-500' :
                  'bg-blue-50 dark:bg-blue-900/20 text-blue-500'
                }`}>
                  <FileText className="w-5 h-5" />
                </div>
              </div>
              
              <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-1 line-clamp-2">{note.title}</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-3 line-clamp-2 min-h-[32px]">{note.description}</p>
              
              <div className="mt-auto pt-3 border-t border-gray-100 dark:border-dark-border/50">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-brand-600 font-medium bg-brand-50 dark:bg-brand-900/20 px-2 py-0.5 rounded-md">{note.subject}</span>
                  <div className="flex items-center gap-3">
                    <button onClick={() => { setReviewNoteId(note.id); setShowReviewModal(true); }} className="flex items-center gap-1 text-xs text-gray-400 hover:text-gold-500 transition-colors" title="Leave a review">
                      {renderStars(note.rating)}
                    </button>
                    <button onClick={() => handleDownload(note.id, note.fileUrl)} className="flex items-center gap-1 text-xs text-gray-400 hover:text-emerald-500 transition-colors cursor-pointer" title="Download">
                      <Download className="w-3 h-3" /> {note.downloads}
                    </button>
                  </div>
                </div>
                <div className="flex items-center justify-between mt-3 text-xs text-gray-400">
                  <span className="flex items-center gap-1"><User className="w-3 h-3" /> {note.uploaderName}</span>
                  <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {note.createdAt}</span>
                </div>
              </div>
            </motion.div>
          ))}
          {filtered.length === 0 && !loading && (
            <div className="col-span-full text-center py-12">
              <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No notes found.</p>
            </div>
          )}
        </motion.div>
      )}

      {/* Review Modal */}
      <AnimatePresence>
        {showReviewModal && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60] flex items-center justify-center p-4">
            <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} exit={{ scale: 0.95 }} className="bg-light-surface dark:bg-dark-card rounded-2xl p-6 w-full max-w-sm">
              <h3 className="text-lg font-bold mb-4">Rate Note</h3>
              <div className="flex gap-2 justify-center mb-6">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star key={star} onClick={() => setReviewScore(star)} className={`w-8 h-8 cursor-pointer transition-colors ${star <= reviewScore ? 'text-gold-400 fill-gold-400' : 'text-gray-300 dark:text-gray-600 hover:text-gold-200'}`} />
                ))}
              </div>
              <textarea value={reviewText} onChange={(e) => setReviewText(e.target.value)} placeholder="Write an optional review..." className="input-field min-h-[80px] mb-4 text-sm" />
              <div className="flex gap-3">
                <button onClick={() => setShowReviewModal(false)} className="btn-secondary flex-1">Cancel</button>
                <button onClick={submitReview} className="btn-primary flex-1">Submit</button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Upload Modal */}
      <AnimatePresence>
        {showUpload && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setShowUpload(false)}>
            <motion.div className="bg-light-surface dark:bg-dark-card rounded-2xl border border-light-border dark:border-dark-border w-full max-w-lg p-6 shadow-glass-dark" onClick={e => e.stopPropagation()}>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-serif font-bold text-gray-900 dark:text-white">Upload Educational Note</h2>
                <button onClick={() => setShowUpload(false)} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-hover"><X className="w-5 h-5 text-gray-500" /></button>
              </div>
              <form onSubmit={handleUpload} className="space-y-4">
                <input type="text" value={uploadForm.title} onChange={e => setUploadForm({ ...uploadForm, title: e.target.value })} placeholder="Note title" className="input-field" required />
                <textarea value={uploadForm.description} onChange={e => setUploadForm({ ...uploadForm, description: e.target.value })} placeholder="Detailed description..." className="input-field min-h-[80px] resize-none" required />
                <select value={uploadForm.subject} onChange={e => setUploadForm({ ...uploadForm, subject: e.target.value })} className="input-field" required>
                  <option value="">Select subject context</option>
                  {subjects.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
                <div className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer hover:border-brand-500/50 transition-colors ${uploadFile ? 'border-brand-500 bg-brand-50/50 dark:bg-brand-900/10' : 'border-gray-200 dark:border-dark-border'}`} onClick={() => document.getElementById('file-input').click()}>
                  <input id="file-input" type="file" className="hidden" accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.png,.jpg,.jpeg" onChange={e => setUploadFile(e.target.files[0])} />
                  <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  {uploadFile ? <p className="text-sm text-brand-600 font-medium">{uploadFile.name}</p> : <p className="text-sm text-gray-500">Pick a file to enrich the library</p>}
                </div>
                <div className="flex gap-3 pt-2">
                  <button type="button" onClick={() => setShowUpload(false)} className="btn-secondary flex-1">Cancel</button>
                  <button type="submit" disabled={uploading} className="btn-primary flex-1">{uploading ? 'Uploading...' : 'Publish'}</button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
