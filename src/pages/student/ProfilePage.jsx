import { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { Mail, Edit3, Save, Sun, Moon, Upload, Star, Download, Calendar, Award } from 'lucide-react';
import PageMessage from '../../components/feedback/PageMessage';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function ProfilePage() {
  const { user, updateProfile } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ name: user?.name || '', about: user?.about || '' });
  const [profileMessage, setProfileMessage] = useState('');

  const handleSave = async () => {
    const result = await updateProfile(form);
    setProfileMessage(result.error);
    setEditing(false);
  };

  const stats = [
    { label: 'Uploads', value: user?.uploads || 0, icon: Upload },
    { label: 'Downloads', value: user?.downloads || 0, icon: Download },
    { label: 'Avg Rating', value: '4.7', icon: Star },
    { label: 'Score', value: user?.score || 0, icon: Award },
  ];

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="max-w-3xl mx-auto space-y-6">
      <motion.div variants={item}><h1 className="page-title">Profile</h1><p className="page-subtitle">Manage your account</p></motion.div>

      {profileMessage && (
        <PageMessage
          eyebrow="Read only"
          title="Profile editing is not available yet"
          description={profileMessage}
          tone="warning"
        />
      )}

      {/* Profile Card */}
      <motion.div variants={item} className="glass-card p-6">
        <div className="flex items-start gap-5">
          <div className="w-20 h-20 rounded-2xl bg-gradient-premium flex items-center justify-center text-white text-3xl font-serif font-bold shadow-glow">
            {user?.name?.charAt(0) || 'S'}
          </div>
          <div className="flex-1">
            {editing ? (
              <div className="space-y-3">
                <input type="text" value={form.name} onChange={e => setForm({...form, name: e.target.value})} className="input-field" placeholder="Full name" />
                <textarea value={form.about} onChange={e => setForm({...form, about: e.target.value})} className="input-field resize-none" rows={2} placeholder="About you" />
                <div className="flex gap-2">
                  <button onClick={handleSave} className="btn-primary flex items-center gap-2 text-sm"><Save className="w-4 h-4" /> Save</button>
                  <button onClick={() => setEditing(false)} className="btn-secondary text-sm">Cancel</button>
                </div>
              </div>
            ) : (
              <>
                <h2 className="text-xl font-serif font-bold text-gray-900 dark:text-white">{user?.name}</h2>
                <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-1 mt-0.5"><Mail className="w-3.5 h-3.5" /> {user?.email}</p>
                <p className="text-sm text-gray-600 dark:text-gray-300 mt-2">{user?.about || 'No bio set'}</p>
                <div className="flex items-center gap-3 mt-3">
                  <span className="badge-purple">{user?.role}</span>
                  <span className="badge-gold">{user?.tier || 'Pending'}</span>
                  <span className="text-xs text-gray-400 flex items-center gap-1"><Calendar className="w-3 h-3" /> Joined via backend session</span>
                </div>
                <button onClick={() => setEditing(true)} className="btn-ghost text-sm mt-3 flex items-center gap-1"><Edit3 className="w-3.5 h-3.5" /> Edit Profile</button>
              </>
            )}
          </div>
        </div>
      </motion.div>

      {/* Stats */}
      <motion.div variants={item} className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(s => (
          <div key={s.label} className="glass-card p-4 text-center">
            <s.icon className="w-5 h-5 text-brand-500 mx-auto mb-2" />
            <p className="text-xl font-bold text-gray-900 dark:text-white">{s.value}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">{s.label}</p>
          </div>
        ))}
      </motion.div>

      {/* Settings */}
      <motion.div variants={item} className="glass-card p-6">
        <h3 className="text-lg font-serif font-bold text-gray-900 dark:text-white mb-4">Preferences</h3>
        <div className="flex items-center justify-between py-3 border-b border-gray-100 dark:border-dark-border/50">
          <div><p className="text-sm font-medium text-gray-900 dark:text-white">Theme</p><p className="text-xs text-gray-500">Switch between dark and light mode</p></div>
          <button onClick={toggleTheme} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-100 dark:bg-dark-surface text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-dark-hover transition-colors">
            {isDark ? <><Sun className="w-4 h-4 text-gold-400" /> Light</> : <><Moon className="w-4 h-4 text-brand-500" /> Dark</>}
          </button>
        </div>
        <div className="flex items-center justify-between py-3">
          <div><p className="text-sm font-medium text-gray-900 dark:text-white">Notifications</p><p className="text-xs text-gray-500">Email and push notifications</p></div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" defaultChecked className="sr-only peer" />
            <div className="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-brand-500/50 rounded-full peer dark:bg-dark-surface peer-checked:bg-brand-500 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full"></div>
          </label>
        </div>
      </motion.div>
    </motion.div>
  );
}
