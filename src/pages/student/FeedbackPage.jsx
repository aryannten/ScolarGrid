import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { COMPLAINTS, COMPLAINT_CATEGORIES, PRIORITY_LEVELS } from '../../data/mockData';
import { useAuth } from '../../context/AuthContext';
import { MessageCircle, Plus, X, Clock, CheckCircle, AlertCircle, ChevronDown, Send, Bot } from 'lucide-react';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

const statusConfig = {
  Open: { badge: 'badge-blue' },
  'In Progress': { badge: 'badge-gold' },
  Resolved: { badge: 'badge-green' },
  Closed: { badge: 'badge-gray' },
};

export default function FeedbackPage() {
  const { user } = useAuth();
  const [complaints, setComplaints] = useState(COMPLAINTS);
  const [showForm, setShowForm] = useState(false);
  const [filter, setFilter] = useState('All');
  const [form, setForm] = useState({ title: '', description: '', category: '', priority: 'Medium' });

  const filtered = complaints.filter(c => filter === 'All' || c.status === filter);

  const handleSubmit = (e) => {
    e.preventDefault();
    const nc = { id: String(Date.now()), userId: user?.id || '2', userName: user?.name || 'User', ...form, status: 'Open', createdAt: new Date().toISOString(), resolvedAt: null, adminResponse: null };
    setComplaints([nc, ...complaints]);
    setShowForm(false);
    setForm({ title: '', description: '', category: '', priority: 'Medium' });
  };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item} className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div><h1 className="page-title">Feedback & Support</h1><p className="page-subtitle">Submit complaints and track resolution</p></div>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-2"><Plus className="w-4 h-4" /> New Complaint</button>
      </motion.div>

      <motion.div variants={item} className="glass-card p-4 flex items-center gap-4 border-l-4 border-brand-500">
        <div className="w-10 h-10 rounded-xl bg-brand-50 dark:bg-brand-900/20 flex items-center justify-center flex-shrink-0"><Bot className="w-5 h-5 text-brand-500" /></div>
        <div><p className="text-sm font-medium text-gray-900 dark:text-white">AI Assistant</p><p className="text-xs text-gray-500 dark:text-gray-400">Describe your issue — our AI might have a quick solution!</p></div>
      </motion.div>

      <motion.div variants={item} className="flex gap-2 overflow-x-auto pb-1">
        {['All', 'Open', 'In Progress', 'Resolved'].map(s => (
          <button key={s} onClick={() => setFilter(s)} className={`px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${filter === s ? 'bg-brand-500 text-white shadow-glow' : 'bg-gray-100 dark:bg-dark-surface text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-dark-hover'}`}>
            {s}{s !== 'All' && <span className="ml-2 text-xs opacity-70">({complaints.filter(c => c.status === s).length})</span>}
          </button>
        ))}
      </motion.div>

      <motion.div variants={container} className="space-y-3">
        {filtered.map(c => (
          <motion.div key={c.id} variants={item} className="glass-card-hover p-5">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-gray-900 dark:text-white">{c.title}</h3>
              <span className={statusConfig[c.status]?.badge || 'badge-gray'}>{c.status}</span>
              <span className={`badge ${c.priority === 'High' ? 'badge-red' : 'badge-gray'}`}>{c.priority}</span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{c.description}</p>
            <div className="flex items-center gap-4 text-xs text-gray-400">
              <span className="badge-purple">{c.category}</span>
              <span>{new Date(c.createdAt).toLocaleDateString()}</span>
            </div>
            {c.adminResponse && (
              <div className="mt-4 p-3 bg-emerald-50 dark:bg-emerald-900/10 rounded-xl border border-emerald-200 dark:border-emerald-800/30">
                <p className="text-xs font-semibold text-emerald-700 dark:text-emerald-400 mb-1">Admin Response</p>
                <p className="text-sm text-emerald-600 dark:text-emerald-300">{c.adminResponse}</p>
              </div>
            )}
          </motion.div>
        ))}
        {filtered.length === 0 && <div className="text-center py-12"><MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" /><p className="text-gray-500">No complaints found</p></div>}
      </motion.div>

      <AnimatePresence>
        {showForm && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setShowForm(false)}>
            <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} exit={{ scale: 0.95 }} className="bg-light-surface dark:bg-dark-card rounded-2xl border border-light-border dark:border-dark-border w-full max-w-lg p-6" onClick={e => e.stopPropagation()}>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-serif font-bold text-gray-900 dark:text-white">Submit Complaint</h2>
                <button onClick={() => setShowForm(false)} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-hover"><X className="w-5 h-5 text-gray-500" /></button>
              </div>
              <form onSubmit={handleSubmit} className="space-y-4">
                <input type="text" value={form.title} onChange={e => setForm({...form, title: e.target.value})} placeholder="Brief title" className="input-field" required />
                <textarea value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="Describe your issue..." className="input-field min-h-[100px] resize-none" required />
                <div className="grid grid-cols-2 gap-3">
                  <select value={form.category} onChange={e => setForm({...form, category: e.target.value})} className="input-field" required>
                    <option value="">Category</option>
                    {COMPLAINT_CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                  <select value={form.priority} onChange={e => setForm({...form, priority: e.target.value})} className="input-field">
                    {PRIORITY_LEVELS.map(p => <option key={p} value={p}>{p}</option>)}
                  </select>
                </div>
                <div className="flex gap-3 pt-2">
                  <button type="button" onClick={() => setShowForm(false)} className="btn-secondary flex-1">Cancel</button>
                  <button type="submit" className="btn-primary flex-1 flex items-center justify-center gap-2"><Send className="w-4 h-4" /> Submit</button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
