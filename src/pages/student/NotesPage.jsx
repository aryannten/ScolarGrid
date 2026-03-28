import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../../lib/api';
import { FileText, Download, Star, Search, Grid3X3, List, Upload, X, Clock, User, ChevronDown } from 'lucide-react';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

const SUBJECTS = [
  'Computer Science',
  'Mathematics',
  'Physics',
  'Chemistry',
  'Biology',
  'Literature',
  'History',
  'Economics',
];

export default function NotesPage() {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [subject, setSubject] = useState('All');
  const [viewMode, setViewMode] = useState('grid');
  const [showUpload, setShowUpload] = useState(false);
  const [sortBy, setSortBy] = useState('date');
  
  const [uploadForm, setUploadForm] = useState({ title: '', description: '', subject: '', tags: '' });
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  // Fetch Notes
  useEffect(() => {
    const fetchNotes = async () => {
      setLoading(true);
      try {
        const queryParams = new URLSearchParams();
        if (search) queryParams.append('keyword', search);
        if (subject !== 'All') queryParams.append('subject', subject);
        if (sortBy) queryParams.append('sort_by', sortBy);
        
        const data = await api.get(`/api/v1/notes?${queryParams.toString()}`);
        setNotes(data.items || []);
      } catch (error) {
        console.error('Failed to fetch notes:', error);
      } finally {
        setLoading(false);
      }
    };

    // Simple debounce for search
    const timeoutId = setTimeout(() => {
      fetchNotes();
    }, 300);
    return () => clearTimeout(timeoutId);
  }, [search, subject, sortBy]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setUploadFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    setUploadError('');

    if (!uploadFile) {
      setUploadError('Please select a file to upload.');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('title', uploadForm.title);
      formData.append('description', uploadForm.description);
      formData.append('subject', uploadForm.subject);
      if (uploadForm.tags) formData.append('tags', uploadForm.tags);
      formData.append('file', uploadFile);

      // We use fetch directly here instead of our api wrapper because FormData needs
      // different headers (browser sets multipart/form-data with boundary)
      const token = localStorage.getItem('scholargrid-token'); // Or manage otherwise
      const user = JSON.parse(localStorage.getItem('scholargrid-user') || '{}');
      
      const response = await fetch('http://localhost:8000/api/v1/notes', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer test-token',
        },
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Upload failed');
      }

      const newNote = await response.json();
      
      // Usually status is 'pending' so it might not show up immediately, 
      // but we add it to the list for optimistic UI if it's approved natively or we just reload
      // setNotes([newNote, ...notes]);
      
      setShowUpload(false);
      setUploadForm({ title: '', description: '', subject: '', tags: '' });
      setUploadFile(null);
      alert('Note uploaded successfully! It may be pending approval.');
      
      // Trigger a re-fetch
      setSubject('All');
      setSearch('');
    } catch (error) {
      setUploadError(error.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (note) => {
    try {
      const resp = await api.post(`/api/v1/notes/${note.id}/download`, {});
      window.open(resp.download_url, '_blank');
      // Optimistically update counts
      setNotes(notes.map(n => n.id === note.id ? { ...n, download_count: n.download_count + 1 } : n));
    } catch (error) {
      console.error('Download failed:', error);
      window.open(note.file_url, '_blank');
    }
  };

  const handleRate = async (noteId, ratingValue) => {
    try {
      await api.post(`/api/v1/notes/${noteId}/rate`, { rating: ratingValue });
      // Reload or optimistically update. Real update requires fetching new average.
    } catch (error) {
      console.error('Rating failed:', error);
    }
  };

  const renderStars = (rating, noteId) => (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map(i => (
        <Star 
          key={i} 
          onClick={noteId ? () => handleRate(noteId, i) : undefined}
          className={`w-3.5 h-3.5 cursor-pointer ${i <= Math.round(rating || 0) ? 'text-gold-400 fill-gold-400' : 'text-gray-300 dark:text-gray-600'}`} 
        />
      ))}
      <span className="text-xs text-gray-500 ml-1">{rating ? rating.toFixed(1) : 'New'}</span>
    </div>
  );

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      {/* Header */}
      <motion.div variants={item} className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="page-title">Notes Library</h1>
          <p className="page-subtitle">{loading ? 'Loading...' : `${notes.length} resources available`}</p>
        </div>
        <button onClick={() => setShowUpload(true)} className="btn-primary flex items-center gap-2">
          <Upload className="w-4 h-4" /> Upload Notes
        </button>
      </motion.div>

      {/* Filters */}
      <motion.div variants={item} className="glass-card p-4 flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search notes by title or description..." className="input-field pl-10" />
        </div>
        <div className="flex gap-3">
          <div className="relative">
            <select value={subject} onChange={e => setSubject(e.target.value)} className="input-field pr-10 appearance-none cursor-pointer min-w-[160px]">
              <option value="All">All Subjects</option>
              {SUBJECTS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
          <div className="relative">
            <select value={sortBy} onChange={e => setSortBy(e.target.value)} className="input-field pr-10 appearance-none cursor-pointer min-w-[130px]">
              <option value="date">Most Recent</option>
              <option value="rating">Top Rated</option>
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
          <div className="flex bg-gray-100 dark:bg-dark-surface rounded-xl p-1">
            <button onClick={() => setViewMode('grid')} className={`p-2 rounded-lg transition-colors ${viewMode === 'grid' ? 'bg-white dark:bg-dark-card shadow-sm' : 'text-gray-400'}`}>
              <Grid3X3 className="w-4 h-4" />
            </button>
            <button onClick={() => setViewMode('list')} className={`p-2 rounded-lg transition-colors ${viewMode === 'list' ? 'bg-white dark:bg-dark-card shadow-sm' : 'text-gray-400'}`}>
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </motion.div>

      {/* Notes Grid/List */}
      {loading ? (
        <div className="flex justify-center py-12"><div className="w-8 h-8 rounded-full border-2 border-brand-500 border-t-transparent animate-spin"/></div>
      ) : notes.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No notes found matching your search.</div>
      ) : viewMode === 'grid' ? (
        <motion.div variants={container} className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {notes.map(note => (
            <motion.div key={note.id} variants={item} className="glass-card-hover p-5 flex flex-col">
              <div className="flex items-start justify-between mb-3">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                  note.file_type === 'pdf' ? 'bg-red-50 dark:bg-red-900/20' :
                  note.file_type?.startsWith('ppt') ? 'bg-orange-50 dark:bg-orange-900/20' :
                  'bg-blue-50 dark:bg-blue-900/20'
                }`}>
                  <FileText className={`w-5 h-5 ${
                    note.file_type === 'pdf' ? 'text-red-500' :
                    note.file_type?.startsWith('ppt') ? 'text-orange-500' :
                    'text-blue-500'
                  }`} />
                </div>
                <button onClick={() => handleDownload(note)} className="p-1.5 text-gray-400 hover:text-brand-500 bg-gray-50 dark:bg-dark-border rounded-lg transition-colors">
                  <Download className="w-4 h-4" />
                </button>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-1 line-clamp-2">{note.title}</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-3 line-clamp-2">{note.description}</p>
              <div className="flex flex-wrap gap-1 mb-3">
                {(note.tags || []).slice(0, 2).map(tag => (
                  <span key={tag} className="badge-purple text-xs">{tag}</span>
                ))}
              </div>
              <div className="mt-auto pt-3 border-t border-gray-100 dark:border-dark-border/50">
                <div className="flex items-center justify-between">
                  {renderStars(note.average_rating, note.id)}
                  <div className="flex items-center gap-1 text-xs text-gray-400">
                    <Download className="w-3 h-3" /> {note.download_count}
                  </div>
                </div>
                <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
                  <span className="flex items-center gap-1"><User className="w-3 h-3" /> {note.uploader_name}</span>
                  <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {new Date(note.upload_date).toLocaleDateString()}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      ) : (
        <motion.div variants={container} className="space-y-3">
          {notes.map(note => (
            <motion.div key={note.id} variants={item} className="glass-card-hover p-4 flex items-center gap-4">
               <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  note.file_type === 'pdf' ? 'bg-red-50 dark:bg-red-900/20' : 'bg-blue-50 dark:bg-blue-900/20'
                }`}>
                  <FileText className={`w-6 h-6 ${note.file_type === 'pdf' ? 'text-red-500' : 'text-blue-500'}`} />
                </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm truncate">{note.title}</h3>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{note.description}</p>
                <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                  <span>{note.uploader_name}</span>
                  <span>{note.subject}</span>
                  <span>{new Date(note.upload_date).toLocaleDateString()}</span>
                </div>
              </div>
              <div className="hidden sm:flex items-center gap-4 flex-shrink-0">
                {renderStars(note.average_rating, note.id)}
                <div className="flex items-center gap-1 text-sm text-gray-500"><Download className="w-4 h-4" /> {note.download_count}</div>
                <button onClick={() => handleDownload(note)} className="btn-secondary text-sm py-1.5 px-3">Download</button>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Upload Modal */}
      <AnimatePresence>
        {showUpload && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4" onClick={() => setShowUpload(false)}>
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }}
              className="bg-light-surface dark:bg-dark-card rounded-2xl border border-light-border dark:border-dark-border w-full max-w-lg p-6 shadow-glass-dark"
              onClick={e => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-serif font-bold text-gray-900 dark:text-white">Upload Notes</h2>
                <button onClick={() => setShowUpload(false)} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-hover"><X className="w-5 h-5 text-gray-500" /></button>
              </div>
              
              {uploadError && <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm rounded-lg">{uploadError}</div>}
              
              <form onSubmit={handleUpload} className="space-y-4">
                <input type="text" value={uploadForm.title} onChange={e => setUploadForm({ ...uploadForm, title: e.target.value })} placeholder="Note title" className="input-field" required />
                <textarea value={uploadForm.description} onChange={e => setUploadForm({ ...uploadForm, description: e.target.value })} placeholder="Description" className="input-field min-h-[80px] resize-none" required />
                <select value={uploadForm.subject} onChange={e => setUploadForm({ ...uploadForm, subject: e.target.value })} className="input-field" required>
                  <option value="">Select subject</option>
                  {SUBJECTS.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
                <input type="text" value={uploadForm.tags} onChange={e => setUploadForm({ ...uploadForm, tags: e.target.value })} placeholder="Tags (comma-separated)" className="input-field" />
                
                <div className="relative border-2 border-dashed border-gray-200 dark:border-dark-border rounded-xl p-8 text-center cursor-pointer hover:border-brand-500/50 transition-colors">
                  <input type="file" onChange={handleFileChange} accept=".pdf,.doc,.docx,.ppt,.pptx" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" required />
                  <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {uploadFile ? uploadFile.name : 'Click or drag files to upload'}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">PDF, PPT, DOC up to 50MB</p>
                </div>

                <div className="flex gap-3 pt-2">
                  <button type="button" onClick={() => setShowUpload(false)} className="btn-secondary flex-1" disabled={uploading}>Cancel</button>
                  <button type="submit" className="btn-primary flex-1 flex justify-center items-center" disabled={uploading}>
                    {uploading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Upload'}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
