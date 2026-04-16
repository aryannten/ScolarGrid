import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import { fetchAllGroups, createGroup, deleteGroup } from '../../services/groupsService';
import { Plus, X, Hash, Users, Copy, Check, Edit3, Trash2 } from 'lucide-react';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function GroupsPage() {
  const { user } = useAuth();
  const [groups, setGroups] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: '', description: '' });
  const [copied, setCopied] = useState(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    try {
      const data = await fetchAllGroups();
      setGroups(data);
    } catch (err) {
      console.error('Error loading groups:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!user) return;
    setCreating(true);
    try {
      const ng = await createGroup(form.name, form.description, user.id);
      setGroups([ng, ...groups]);
      setShowCreate(false);
      setForm({ name: '', description: '' });
    } catch (err) {
      console.error('Create group error:', err);
      alert('Failed to create group: ' + err.message);
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this group?')) return;
    try {
      await deleteGroup(id);
      setGroups(groups.filter(g => g.id !== id));
    } catch (err) {
      console.error('Delete group error:', err);
      alert('Failed to delete group: ' + err.message);
    }
  };

  const copyCode = (code) => { navigator.clipboard.writeText(code); setCopied(code); setTimeout(() => setCopied(null), 2000); };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 rounded bg-gray-100 dark:bg-dark-surface animate-pulse" />
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1,2,3].map(i => <div key={i} className="h-48 rounded-2xl bg-gray-100 dark:bg-dark-surface animate-pulse" />)}
        </div>
      </div>
    );
  }

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item} className="flex items-center justify-between">
        <div><h1 className="page-title">Chat Groups</h1><p className="page-subtitle">Create and manage group conversations</p></div>
        <button onClick={() => setShowCreate(true)} className="btn-primary flex items-center gap-2"><Plus className="w-4 h-4" /> Create Group</button>
      </motion.div>

      <motion.div variants={container} className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {groups.map(g => (
          <motion.div key={g.id} variants={item} className="glass-card-hover p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-premium flex items-center justify-center text-white"><Hash className="w-5 h-5" /></div>
              <div className="flex gap-1">
                <button onClick={() => handleDelete(g.id)} className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/10 text-gray-400 hover:text-red-500"><Trash2 className="w-4 h-4" /></button>
              </div>
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-1">{g.name}</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">{g.description}</p>
            <div className="flex items-center justify-between text-xs text-gray-400 mb-3">
              <span className="flex items-center gap-1"><Users className="w-3 h-3" /> {g.members} members</span>
              <span>{g.createdAt}</span>
            </div>
            <button onClick={() => copyCode(g.joinCode)} className="w-full flex items-center justify-center gap-2 py-2 rounded-lg bg-gray-50 dark:bg-dark-surface text-xs font-mono text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-dark-hover transition-colors">
              {copied === g.joinCode ? <><Check className="w-3 h-3 text-emerald-500" /> Copied!</> : <><Copy className="w-3 h-3" /> {g.joinCode}</>}
            </button>
          </motion.div>
        ))}
        {groups.length === 0 && (
          <div className="col-span-full text-center py-12">
            <Hash className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No groups yet. Create the first one!</p>
          </div>
        )}
      </motion.div>

      <AnimatePresence>
        {showCreate && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setShowCreate(false)}>
            <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} exit={{ scale: 0.95 }} className="bg-light-surface dark:bg-dark-card rounded-2xl border border-light-border dark:border-dark-border w-full max-w-md p-6" onClick={e => e.stopPropagation()}>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-serif font-bold text-gray-900 dark:text-white">Create Group</h2>
                <button onClick={() => setShowCreate(false)} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-hover"><X className="w-5 h-5 text-gray-500" /></button>
              </div>
              <form onSubmit={handleCreate} className="space-y-4">
                <input type="text" value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Group name" className="input-field" required />
                <textarea value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="Description" className="input-field resize-none" rows={3} required />
                <div className="p-3 bg-gray-50 dark:bg-dark-surface rounded-xl"><p className="text-xs text-gray-400 mb-1">A unique join code will be auto-generated</p></div>
                <div className="flex gap-3">
                  <button type="button" onClick={() => setShowCreate(false)} className="btn-secondary flex-1">Cancel</button>
                  <button type="submit" disabled={creating} className="btn-primary flex-1">
                    {creating ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mx-auto" /> : 'Create Group'}
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
