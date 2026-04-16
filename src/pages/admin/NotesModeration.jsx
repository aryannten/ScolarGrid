import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { fetchNotes, fetchSubjects, flagNote, deleteNote } from '../../services/notesService';
import { FileText, Trash2, Eye, Flag, Star, Download, Search, ChevronDown } from 'lucide-react';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

const DEFAULT_SUBJECTS = ['Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'Electrical Engineering', 'Mechanical Engineering', 'Biology', 'Economics'];

export default function NotesModeration() {
  const [notes, setNotes] = useState([]);
  const [subjects, setSubjects] = useState(DEFAULT_SUBJECTS);
  const [search, setSearch] = useState('');
  const [subject, setSubject] = useState('All');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadNotes();
    loadSubjects();
  }, [subject]);

  const loadNotes = async () => {
    try {
      setLoading(true);
      const data = await fetchNotes({ subject, search });
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
    } catch (err) { /* keep defaults */ }
  };

  useEffect(() => {
    const timer = setTimeout(() => loadNotes(), 300);
    return () => clearTimeout(timer);
  }, [search]);

  const filtered = notes.filter(n => n.title.toLowerCase().includes(search.toLowerCase()));

  const handleDelete = async (id) => {
    if (!confirm('Delete this note?')) return;
    try {
      await deleteNote(id);
      setNotes(notes.filter(n => n.id !== id));
    } catch (err) {
      console.error('Delete error:', err);
      alert('Failed to delete: ' + err.message);
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
      console.error('Flag error:', err);
    }
  };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item}><h1 className="page-title">Notes Moderation</h1><p className="page-subtitle">Review, approve, and moderate shared notes</p></motion.div>

      <motion.div variants={item} className="glass-card p-4 flex flex-col sm:flex-row gap-3">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search notes..." className="input-field pl-10" />
        </div>
        <div className="relative">
          <select value={subject} onChange={e => setSubject(e.target.value)} className="input-field pr-10 appearance-none min-w-[160px]">
            <option value="All">All Subjects</option>
            {subjects.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
        </div>
      </motion.div>

      {loading ? (
        <div className="space-y-3">
          {[1,2,3,4].map(i => <div key={i} className="h-16 rounded-2xl bg-gray-100 dark:bg-dark-surface animate-pulse" />)}
        </div>
      ) : (
        <motion.div variants={item} className="glass-card overflow-hidden">
          <div className="table-header px-6 py-3 grid grid-cols-12 gap-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            <span className="col-span-4">Title</span>
            <span className="col-span-2 hidden sm:block">Subject</span>
            <span className="col-span-1 hidden sm:block text-center">DLs</span>
            <span className="col-span-2">Status</span>
            <span className="col-span-3 text-right">Actions</span>
          </div>
          {filtered.length === 0 && (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No notes found</p>
            </div>
          )}
          {filtered.map(note => (
            <div key={note.id} className="table-row px-6 py-3 grid grid-cols-12 gap-4 items-center">
              <div className="col-span-4 flex items-center gap-3 min-w-0">
                <FileText className={`w-5 h-5 flex-shrink-0 ${note.fileType === 'PDF' ? 'text-red-500' : 'text-blue-500'}`} />
                <div className="min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{note.title}</p>
                  <p className="text-xs text-gray-400">{note.uploaderName}</p>
                </div>
              </div>
              <span className="col-span-2 hidden sm:block text-sm text-gray-600 dark:text-gray-400">{note.subject}</span>
              <span className="col-span-1 hidden sm:block text-center text-sm text-gray-600 dark:text-gray-400">{note.downloads}</span>
              <span className="col-span-2"><span className={note.modStatus === 'Flagged' ? 'badge-red' : 'badge-green'}>{note.modStatus}</span></span>
              <div className="col-span-3 flex items-center justify-end gap-1">
                <button onClick={() => handleFlag(note.id)} className="p-1.5 rounded-lg hover:bg-orange-50 dark:hover:bg-orange-900/10 text-gray-400 hover:text-orange-500" title="Flag">
                  <Flag className={`w-4 h-4 ${note.isFlagged ? 'text-orange-500 fill-orange-500' : ''}`} />
                </button>
                <button onClick={() => handleDelete(note.id)} className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/10 text-gray-400 hover:text-red-500" title="Delete"><Trash2 className="w-4 h-4" /></button>
              </div>
            </div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
}
