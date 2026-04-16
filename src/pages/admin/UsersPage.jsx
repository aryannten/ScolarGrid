import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { fetchAllStudents, warnUser, banUser } from '../../services/usersService';
import { Search, Ban, AlertTriangle, Eye, Shield, User } from 'lucide-react';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const data = await fetchAllStudents();
      setUsers(data);
    } catch (err) {
      console.error('Error loading users:', err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = users.filter(u =>
    u.name.toLowerCase().includes(search.toLowerCase()) ||
    u.email.toLowerCase().includes(search.toLowerCase())
  );

  const handleWarn = async (id) => {
    try {
      await warnUser(id);
      setUsers(users.map(u => u.id === id ? { ...u, warnings: (u.warnings || 0) + 1, status: 'Warned' } : u));
    } catch (err) {
      console.error('Warn error:', err);
      alert('Failed to warn user: ' + err.message);
    }
  };

  const handleToggleBan = async (id) => {
    const u = users.find(x => x.id === id);
    if (!u) return;
    const newBanned = u.status !== 'Banned';
    try {
      await banUser(id, newBanned);
      setUsers(users.map(x => x.id === id ? { ...x, is_banned: newBanned, status: newBanned ? 'Banned' : 'Active' } : x));
    } catch (err) {
      console.error('Ban error:', err);
      alert('Failed to update ban status: ' + err.message);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 rounded bg-gray-100 dark:bg-dark-surface animate-pulse" />
        <div className="h-12 rounded-2xl bg-gray-100 dark:bg-dark-surface animate-pulse" />
        {[1,2,3,4].map(i => <div key={i} className="h-16 rounded-2xl bg-gray-100 dark:bg-dark-surface animate-pulse" />)}
      </div>
    );
  }

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item}><h1 className="page-title">User Management</h1><p className="page-subtitle">Manage student accounts and permissions</p></motion.div>

      <motion.div variants={item} className="glass-card p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search by name or email..." className="input-field pl-10" />
        </div>
      </motion.div>

      <motion.div variants={item} className="glass-card overflow-hidden">
        <div className="table-header px-6 py-3 grid grid-cols-12 gap-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">
          <span className="col-span-3">User</span>
          <span className="col-span-2 hidden sm:block">Role</span>
          <span className="col-span-2 hidden sm:block">Tier</span>
          <span className="col-span-1 hidden sm:block text-center">Score</span>
          <span className="col-span-2">Status</span>
          <span className="col-span-2 text-right">Actions</span>
        </div>
        {filtered.length === 0 && (
          <div className="text-center py-12">
            <User className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No users found</p>
          </div>
        )}
        {filtered.map(u => (
          <div key={u.id} className={`table-row px-6 py-3 grid grid-cols-12 gap-4 items-center ${u.status === 'Banned' ? 'opacity-60' : ''}`}>
            <div className="col-span-3 flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-gradient-premium flex items-center justify-center text-white text-sm font-bold flex-shrink-0">{u.name.charAt(0)}</div>
              <div className="min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{u.name}</p>
                <p className="text-xs text-gray-400 truncate">{u.email}</p>
              </div>
            </div>
            <span className="col-span-2 hidden sm:block"><span className="badge-purple text-xs">{u.role}</span></span>
            <span className="col-span-2 hidden sm:block"><span className="badge-gold text-xs">{u.tier || 'Bronze'}</span></span>
            <span className="col-span-1 hidden sm:block text-center text-sm font-bold text-gray-700 dark:text-gray-300">{u.score || 0}</span>
            <span className="col-span-2">
              <span className={`badge text-xs ${u.status === 'Active' ? 'badge-green' : u.status === 'Warned' ? 'badge-gold' : 'badge-red'}`}>{u.status}</span>
            </span>
            <div className="col-span-2 flex items-center justify-end gap-1">
              <button onClick={() => handleWarn(u.id)} className="p-1.5 rounded-lg hover:bg-orange-50 dark:hover:bg-orange-900/10 text-gray-400 hover:text-orange-500" title="Warn"><AlertTriangle className="w-4 h-4" /></button>
              <button onClick={() => handleToggleBan(u.id)} className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/10 text-gray-400 hover:text-red-500" title={u.status === 'Banned' ? 'Unban' : 'Ban'}><Ban className="w-4 h-4" /></button>
            </div>
          </div>
        ))}
      </motion.div>
    </motion.div>
  );
}
