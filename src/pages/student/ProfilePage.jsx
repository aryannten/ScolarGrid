import { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { uploadAvatar } from '../../services/storageService';
import { upgradeToFaculty } from '../../services/usersService';
import { User, Mail, Edit3, Save, Sun, Moon, Upload, Star, FileText, Download, Calendar, Award, Camera, Key, Database, Copy, CheckCircle } from 'lucide-react';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function ProfilePage() {
  const { user, updateProfile } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ name: user?.name || '', about: user?.about || '' });
  const [saving, setSaving] = useState(false);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);
  const [copiedId, setCopiedId] = useState(false);
  const [copiedEmail, setCopiedEmail] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateProfile(form);
      setEditing(false);
    } catch (err) {
      console.error('Profile update error:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleUpgrade = async () => {
    const code = prompt('Enter Faculty Registration Code:');
    if (!code) return;
    try {
      const res = await upgradeToFaculty(code);
      if (res.success) {
        alert('Successfully upgraded to Faculty!');
        window.location.href = '/management/dashboard';
      }
    } catch (err) {
      alert('Upgrade failed: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleAvatarUpload = async (e) => {
    const file = e.target.files[0];
    if (!file || !user) return;
    setUploadingAvatar(true);
    try {
      const avatarUrl = await uploadAvatar(user.id, file);
      await updateProfile({ avatar: avatarUrl });
    } catch (err) {
      console.error('Avatar upload error:', err);
      alert('Failed to upload avatar: ' + err.message);
    } finally {
      setUploadingAvatar(false);
    }
  };

  const copyToClipboard = async (text, type) => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === 'id') { setCopiedId(true); setTimeout(() => setCopiedId(false), 2000); }
      else { setCopiedEmail(true); setTimeout(() => setCopiedEmail(false), 2000); }
    } catch (err) {
      console.error('Copy failed:', err);
    }
  };

  const stats = [
    { label: 'Uploads', value: user?.uploads || 0, icon: Upload },
    { label: 'Downloads', value: user?.downloads || 0, icon: Download },
    { label: 'Points', value: user?.score || 0, icon: Star },
    { label: 'Tier', value: user?.tier || 'Bronze', icon: Award },
  ];

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="max-w-3xl mx-auto space-y-6">
      <motion.div variants={item}><h1 className="page-title">Profile</h1><p className="page-subtitle">Manage your account</p></motion.div>

      {/* Profile Card */}
      <motion.div variants={item} className="glass-card p-6">
        <div className="flex items-start gap-5">
          <div className="relative group">
            {user?.avatar ? (
              <img src={user.avatar} alt="Avatar" className="w-20 h-20 rounded-2xl object-cover shadow-glow" />
            ) : (
              <div className="w-20 h-20 rounded-2xl bg-gradient-premium flex items-center justify-center text-white text-3xl font-serif font-bold shadow-glow">
                {user?.name?.charAt(0) || 'S'}
              </div>
            )}
            <label className="absolute inset-0 flex items-center justify-center bg-black/40 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
              <input type="file" accept="image/*" className="hidden" onChange={handleAvatarUpload} />
              {uploadingAvatar ? (
                <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Camera className="w-6 h-6 text-white" />
              )}
            </label>
          </div>
          <div className="flex-1">
            {editing ? (
              <div className="space-y-3">
                <input type="text" value={form.name} onChange={e => setForm({...form, name: e.target.value})} className="input-field" placeholder="Full name" />
                <textarea value={form.about} onChange={e => setForm({...form, about: e.target.value})} className="input-field resize-none" rows={2} placeholder="About you" />
                <div className="flex gap-2">
                  <button onClick={handleSave} disabled={saving} className="btn-primary flex items-center gap-2 text-sm">
                    {saving ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Save className="w-4 h-4" />}
                    Save
                  </button>
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
                  <span className="badge-gold">{user?.tier || 'Bronze'}</span>
                  <span className="text-xs text-gray-400 flex items-center gap-1"><Calendar className="w-3 h-3" /> Joined {user?.joinedAt}</span>
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

      {/* Account Information (Database Record) */}
      <motion.div variants={item} className="glass-card p-6">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-lg bg-emerald-50 dark:bg-emerald-900/20 flex items-center justify-center">
            <Database className="w-4 h-4 text-emerald-500" />
          </div>
          <div>
            <h3 className="text-lg font-serif font-bold text-gray-900 dark:text-white">Account Information</h3>
            <p className="text-xs text-gray-400">Your database record — currently active session</p>
          </div>
          <span className="ml-auto flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 text-xs font-semibold rounded-full">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse inline-block" />
            Connected
          </span>
        </div>

        <div className="space-y-3">
          {/* User ID */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-dark-surface border border-gray-100 dark:border-dark-border">
            <div className="flex-1 min-w-0 mr-3">
              <p className="text-xs text-gray-400 mb-0.5">User ID</p>
              <p className="text-sm font-mono font-medium text-gray-800 dark:text-gray-200 truncate">{user?.id || '—'}</p>
            </div>
            <button
              onClick={() => copyToClipboard(user?.id, 'id')}
              className="flex-shrink-0 p-1.5 rounded-lg hover:bg-gray-200 dark:hover:bg-dark-hover transition-colors"
              title="Copy ID"
            >
              {copiedId ? <CheckCircle className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4 text-gray-400" />}
            </button>
          </div>

          {/* Email */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-dark-surface border border-gray-100 dark:border-dark-border">
            <div className="flex-1 min-w-0 mr-3">
              <p className="text-xs text-gray-400 mb-0.5">Email Address</p>
              <p className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate">{user?.email || '—'}</p>
            </div>
            <button
              onClick={() => copyToClipboard(user?.email, 'email')}
              className="flex-shrink-0 p-1.5 rounded-lg hover:bg-gray-200 dark:hover:bg-dark-hover transition-colors"
              title="Copy Email"
            >
              {copiedEmail ? <CheckCircle className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4 text-gray-400" />}
            </button>
          </div>

          {/* Role + Member since */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded-xl bg-gray-50 dark:bg-dark-surface border border-gray-100 dark:border-dark-border">
              <p className="text-xs text-gray-400 mb-0.5">Role</p>
              <p className="text-sm font-semibold text-gray-800 dark:text-gray-200 capitalize">{user?.role || '—'}</p>
            </div>
            <div className="p-3 rounded-xl bg-gray-50 dark:bg-dark-surface border border-gray-100 dark:border-dark-border">
              <p className="text-xs text-gray-400 mb-0.5">Member Since</p>
              <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">{user?.joinedAt || '—'}</p>
            </div>
          </div>
        </div>
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
        {user?.role === 'student' && (
          <div className="flex items-center justify-between py-3 border-t border-gray-100 dark:border-dark-border/50">
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">Faculty Access</p>
              <p className="text-xs text-gray-500">Upgrade to a faculty account with a registration code</p>
            </div>
            <button onClick={handleUpgrade} className="btn-secondary text-sm flex items-center gap-2">
              <Key className="w-4 h-4" /> Upgrade
            </button>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}
