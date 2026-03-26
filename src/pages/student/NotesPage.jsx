import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { NOTES, SUBJECTS } from '../../data/mockData';
import { FileText, Download, Star, Search, Filter, Grid3X3, List, Upload, X, Tag, Clock, User, ChevronDown } from 'lucide-react';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function NotesPage() {
  const [notes, setNotes] = useState(NOTES);
  const [search, setSearch] = useState('');
  const [subject, setSubject] = useState('All');
  const [viewMode, setViewMode] = useState('grid');
  const [showUpload, setShowUpload] = useState(false);
  const [sortBy, setSortBy] = useState('recent');
  const [uploadForm, setUploadForm] = useState({ title: '', description: '', subject: '', tags: '' });

  const filtered = notes
    .filter(n => (subject === 'All' || n.subject === subject))
    .filter(n => n.title.toLowerCase().includes(search.toLowerCase()) || n.description.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => {
      if (sortBy === 'rating') return b.rating - a.rating;
      if (sortBy === 'downloads') return b.downloads - a.downloads;
      return new Date(b.createdAt) - new Date(a.createdAt);
    });

  const handleUpload = (e) => {
    e.preventDefault();
    const newNote = {
      id: String(Date.now()),
      ...uploadForm,
      tags: uploadForm.tags.split(',').map(t => t.trim()),
      uploaderId: '2',
      uploaderName: 'Current User',
      createdAt: new Date().toISOString().split('T')[0],
      fileType: 'PDF',
      fileSize: '2.1 MB',
      downloads: 0,
      rating: 0,
      totalRatings: 0,
    };
    setNotes([newNote, ...notes]);
    setShowUpload(false);
    setUploadForm({ title: '', description: '', subject: '', tags: '' });
  };

  const renderStars = (rating) => (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map(i => (
        <Star key={i} className={`w-3.5 h-3.5 ${i <= Math.round(rating) ? 'text-gold-400 fill-gold-400' : 'text-gray-300 dark:text-gray-600'}`} />
      ))}
      <span className="text-xs text-gray-500 ml-1">{rating}</span>
    </div>
  );

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      {/* Header */}
      <motion.div variants={item} className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="page-title">Notes Library</h1>
          <p className="page-subtitle">{filtered.length} resources available</p>
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
              <option value="recent">Most Recent</option>
              <option value="rating">Top Rated</option>
              <option value="downloads">Most Downloaded</option>
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
      {viewMode === 'grid' ? (
        <motion.div variants={container} className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(note => (
            <motion.div key={note.id} variants={item} className="glass-card-hover p-5 flex flex-col">
              <div className="flex items-start justify-between mb-3">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                  note.fileType === 'PDF' ? 'bg-red-50 dark:bg-red-900/20' :
                  note.fileType === 'PPT' ? 'bg-orange-50 dark:bg-orange-900/20' :
                  'bg-blue-50 dark:bg-blue-900/20'
                }`}>
                  <FileText className={`w-5 h-5 ${
                    note.fileType === 'PDF' ? 'text-red-500' :
                    note.fileType === 'PPT' ? 'text-orange-500' :
                    'text-blue-500'
                  }`} />
                </div>
                <span className="badge-gray text-xs">{note.fileType}</span>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-1 line-clamp-2">{note.title}</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-3 line-clamp-2">{note.description}</p>
              <div className="flex flex-wrap gap-1 mb-3">
                {note.tags.slice(0, 2).map(tag => (
                  <span key={tag} className="badge-purple text-xs">{tag}</span>
                ))}
              </div>
              <div className="mt-auto pt-3 border-t border-gray-100 dark:border-dark-border/50">
                <div className="flex items-center justify-between">
                  {renderStars(note.rating)}
                  <div className="flex items-center gap-1 text-xs text-gray-400">
                    <Download className="w-3 h-3" /> {note.downloads}
                  </div>
                </div>
                <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
                  <span className="flex items-center gap-1"><User className="w-3 h-3" /> {note.uploaderName}</span>
                  <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {note.createdAt}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      ) : (
        <motion.div variants={container} className="space-y-3">
          {filtered.map(note => (
            <motion.div key={note.id} variants={item} className="glass-card-hover p-4 flex items-center gap-4">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${
                note.fileType === 'PDF' ? 'bg-red-50 dark:bg-red-900/20' : 'bg-blue-50 dark:bg-blue-900/20'
              }`}>
                <FileText className={`w-6 h-6 ${note.fileType === 'PDF' ? 'text-red-500' : 'text-blue-500'}`} />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm truncate">{note.title}</h3>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{note.description}</p>
                <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                  <span>{note.uploaderName}</span>
                  <span>{note.subject}</span>
                  <span>{note.createdAt}</span>
                </div>
              </div>
              <div className="hidden sm:flex items-center gap-4 flex-shrink-0">
                {renderStars(note.rating)}
                <div className="flex items-center gap-1 text-sm text-gray-500"><Download className="w-4 h-4" /> {note.downloads}</div>
                <button className="btn-secondary text-sm py-1.5 px-3">Download</button>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Upload Modal */}
      <AnimatePresence>
        {showUpload && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setShowUpload(false)}>
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }}
              className="bg-light-surface dark:bg-dark-card rounded-2xl border border-light-border dark:border-dark-border w-full max-w-lg p-6 shadow-glass-dark"
              onClick={e => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-serif font-bold text-gray-900 dark:text-white">Upload Notes</h2>
                <button onClick={() => setShowUpload(false)} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-hover"><X className="w-5 h-5 text-gray-500" /></button>
              </div>
              <form onSubmit={handleUpload} className="space-y-4">
                <input type="text" value={uploadForm.title} onChange={e => setUploadForm({ ...uploadForm, title: e.target.value })} placeholder="Note title" className="input-field" required />
                <textarea value={uploadForm.description} onChange={e => setUploadForm({ ...uploadForm, description: e.target.value })} placeholder="Description" className="input-field min-h-[80px] resize-none" required />
                <select value={uploadForm.subject} onChange={e => setUploadForm({ ...uploadForm, subject: e.target.value })} className="input-field" required>
                  <option value="">Select subject</option>
                  {SUBJECTS.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
                <input type="text" value={uploadForm.tags} onChange={e => setUploadForm({ ...uploadForm, tags: e.target.value })} placeholder="Tags (comma-separated)" className="input-field" />
                <div className="border-2 border-dashed border-gray-200 dark:border-dark-border rounded-xl p-8 text-center cursor-pointer hover:border-brand-500/50 transition-colors">
                  <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-500">Click or drag files to upload</p>
                  <p className="text-xs text-gray-400 mt-1">PDF, PPT, DOC up to 50MB</p>
                </div>
                <div className="flex gap-3 pt-2">
                  <button type="button" onClick={() => setShowUpload(false)} className="btn-secondary flex-1">Cancel</button>
                  <button type="submit" className="btn-primary flex-1">Upload</button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
