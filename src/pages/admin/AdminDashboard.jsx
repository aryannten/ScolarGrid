import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import { fetchAnalytics } from '../../services/analyticsService';
import { fetchComplaints } from '../../services/complaintsService';
import { fetchLeaderboard } from '../../services/leaderboardService';
import { Users, FileText, Download, AlertCircle, ArrowUpRight, TrendingUp, Shield, MessageSquare, Plus, CheckCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.08 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function AdminDashboard() {
  const { user, isSuperAdmin } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [complaints, setComplaints] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [a, c, lb] = await Promise.all([
        fetchAnalytics(),
        fetchComplaints(null, true),
        fetchLeaderboard(5),
      ]);
      setAnalytics(a);
      setComplaints(c);
      setLeaderboard(lb);
    } catch (err) {
      console.error('Admin dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !analytics) {
    return (
      <div className="space-y-6">
        <div className="h-40 rounded-2xl bg-gray-100 dark:bg-dark-surface animate-pulse" />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1,2,3,4].map(i => <div key={i} className="h-28 rounded-2xl bg-gray-100 dark:bg-dark-surface animate-pulse" />)}
        </div>
      </div>
    );
  }

  const openComplaints = complaints.filter(c => c.status === 'Open').length;

  const stats = [
    { label: 'Total Users', value: analytics.totalUsers, icon: Users, color: 'text-brand-500', bg: 'bg-brand-50 dark:bg-brand-900/20' },
    { label: 'Total Notes', value: analytics.totalNotes, icon: FileText, color: 'text-emerald-500', bg: 'bg-emerald-50 dark:bg-emerald-900/20' },
    { label: 'Downloads', value: analytics.totalDownloads.toLocaleString(), icon: Download, color: 'text-blue-500', bg: 'bg-blue-50 dark:bg-blue-900/20' },
    { label: 'Open Issues', value: openComplaints, icon: AlertCircle, color: 'text-red-500', bg: 'bg-red-50 dark:bg-red-900/20' },
  ];

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      {/* Welcome Banner - Styled like the student dashboard */}
      <motion.div variants={item} className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-gold-600 via-gold-700 to-amber-900 p-6 lg:p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/4" />
        <div className="absolute bottom-0 right-1/4 w-32 h-32 bg-brand-400/10 rounded-full translate-y-1/2" />
        <div className="relative z-10 flex flex-col sm:flex-row justify-between items-start sm:items-center">
          <div>
            <p className="text-gold-200 text-sm font-medium mb-1">Welcome back,</p>
            <h1 className="text-2xl lg:text-3xl font-serif font-bold text-white mb-2">Professor {user?.name || 'Administrator'} 🏛️</h1>
            <p className="text-gold-100 text-sm max-w-lg">
              {isSuperAdmin 
                ? "Manage platform metrics, resolve complaints, and oversee global operations." 
                : "Manage class groups, review student notes, and contribute your own resources."}
            </p>
          </div>
          <div className="flex gap-3 mt-5 sm:mt-0">
            <Link to="/management/notes" className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm font-medium backdrop-blur-sm transition-colors border border-white/10">
              <Plus className="w-4 h-4" /> Add Note
            </Link>
            <Link to="/management/groups" className="inline-flex items-center gap-2 px-4 py-2 text-gold-900 bg-white hover:bg-gold-50 rounded-xl text-sm font-medium shadow-sm transition-colors border border-white/10">
              <MessageSquare className="w-4 h-4 text-gold-600" /> New Chat
            </Link>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div variants={item} className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(s => (
          <motion.div key={s.label} variants={item} className="glass-card-hover p-5">
            <div className={`w-10 h-10 rounded-xl ${s.bg} flex items-center justify-center mb-3`}>
              <s.icon className={`w-5 h-5 ${s.color}`} />
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{s.value}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{s.label}</p>
          </motion.div>
        ))}
      </motion.div>

      {/* Two Column Layout exactly like StudentDashboard */}
      <div className="grid lg:grid-cols-3 gap-6">
        
        {/* Top Contributors */}
        <motion.div variants={item} className="lg:col-span-2 glass-card p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-serif font-bold text-gray-900 dark:text-white">Top Student Contributors</h2>
            {isSuperAdmin && (
              <Link to="/management/users" className="text-gold-600 hover:text-gold-700 text-sm font-medium flex items-center gap-1">
                Manage Users <ArrowUpRight className="w-3 h-3" />
              </Link>
            )}
          </div>
          <div className="space-y-4">
            {leaderboard.map((u, i) => (
              <div key={u.id} className="flex items-center gap-3 p-2 rounded-xl hover:bg-gray-50 dark:hover:bg-dark-hover transition-colors">
                <span className="text-sm font-bold text-gray-400 w-5">#{i + 1}</span>
                <div className="w-8 h-8 rounded-full bg-gradient-gold flex items-center justify-center text-white text-xs font-bold">{u.name.charAt(0)}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">{u.name}</p>
                  <p className="text-xs text-gray-400">{u.tier}</p>
                </div>
                <span className="text-sm font-bold text-gold-600 dark:text-gold-500">{u.score} pts</span>
              </div>
            ))}
            {leaderboard.length === 0 && (
              <p className="text-sm text-gray-400 text-center py-4">No active students yet.</p>
            )}
          </div>
        </motion.div>

        {/* Action Items (Complaints/Issues) */}
        <motion.div variants={item} className="glass-card p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-serif font-bold text-gray-900 dark:text-white">Action Items</h2>
            <Link to="/management/complaints" className="text-gold-600 hover:text-gold-700 text-sm font-medium flex items-center gap-1">
              View All <ArrowUpRight className="w-3 h-3" />
            </Link>
          </div>
          <div className="space-y-3">
            {complaints.filter(c => c.status !== 'Resolved').length === 0 && (
              <div className="text-center py-10">
                <CheckCircle className="w-10 h-10 text-emerald-500 mx-auto mb-2 opacity-50" />
                <p className="text-sm text-gray-400">All caught up! 🎉</p>
              </div>
            )}
            {complaints.filter(c => c.status !== 'Resolved').slice(0, 5).map((c, i) => (
              <div key={c.id} className="flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-dark-hover transition-colors border border-transparent hover:border-gray-100 dark:hover:border-dark-border">
                <AlertCircle className={`w-5 h-5 flex-shrink-0 ${c.priority === 'High' ? 'text-red-500' : 'text-gold-500'}`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{c.title}</p>
                  <p className="text-xs text-gray-400">{c.userName}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
