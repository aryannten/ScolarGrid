import { motion } from 'framer-motion';
import { ANALYTICS, LEADERBOARD, NOTES } from '../../data/mockData';
import { TrendingUp, Users, FileText, Download, BarChart3 } from 'lucide-react';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function AnalyticsPage() {
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item}><h1 className="page-title">Analytics</h1><p className="page-subtitle">Platform insights and performance metrics</p></motion.div>

      {/* Key Metrics */}
      <motion.div variants={item} className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Users', value: ANALYTICS.totalUsers, icon: Users, color: 'text-brand-500', bg: 'bg-brand-50 dark:bg-brand-900/20' },
          { label: 'Total Notes', value: ANALYTICS.totalNotes, icon: FileText, color: 'text-emerald-500', bg: 'bg-emerald-50 dark:bg-emerald-900/20' },
          { label: 'Downloads', value: ANALYTICS.totalDownloads.toLocaleString(), icon: Download, color: 'text-blue-500', bg: 'bg-blue-50 dark:bg-blue-900/20' },
          { label: 'Active Chats', value: ANALYTICS.activeChats, icon: BarChart3, color: 'text-gold-500', bg: 'bg-gold-50 dark:bg-gold-900/20' },
        ].map(s => (
          <div key={s.label} className="glass-card p-5">
            <div className={`w-10 h-10 rounded-xl ${s.bg} flex items-center justify-center mb-3`}><s.icon className={`w-5 h-5 ${s.color}`} /></div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{s.value}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">{s.label}</p>
          </div>
        ))}
      </motion.div>

      {/* User Growth */}
      <motion.div variants={item} className="glass-card p-6">
        <h2 className="text-lg font-serif font-bold text-gray-900 dark:text-white mb-4">User Growth</h2>
        <div className="h-52 flex items-end justify-between gap-2 px-2">
          {ANALYTICS.monthlyUsers.map((v, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-1">
              <motion.div initial={{ height: 0 }} animate={{ height: `${(v / 260) * 100}%` }} transition={{ delay: i * 0.04, duration: 0.5 }}
                className="w-full bg-gradient-to-t from-emerald-500 to-emerald-400 rounded-t-lg relative group cursor-pointer">
                <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-dark-card text-white text-xs px-2 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">{v} users</div>
              </motion.div>
              <span className="text-[10px] text-gray-400">{months[i]}</span>
            </div>
          ))}
        </div>
      </motion.div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Upload Trends */}
        <motion.div variants={item} className="glass-card p-6">
          <h2 className="text-lg font-serif font-bold text-gray-900 dark:text-white mb-4">Monthly Uploads</h2>
          <div className="h-44 flex items-end justify-between gap-2 px-2">
            {ANALYTICS.monthlyUploads.map((v, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <motion.div initial={{ height: 0 }} animate={{ height: `${(v / 60) * 100}%` }} transition={{ delay: i * 0.04, duration: 0.5 }}
                  className="w-full bg-gradient-to-t from-brand-500 to-brand-400 rounded-t-lg relative group cursor-pointer">
                  <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-dark-card text-white text-xs px-2 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">{v}</div>
                </motion.div>
                <span className="text-[10px] text-gray-400">{months[i]}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Subject Distribution */}
        <motion.div variants={item} className="glass-card p-6">
          <h2 className="text-lg font-serif font-bold text-gray-900 dark:text-white mb-4">Subject Distribution</h2>
          <div className="space-y-4">
            {ANALYTICS.topSubjects.map((s, i) => {
              const colors = ['from-brand-400 to-brand-600', 'from-emerald-400 to-emerald-600', 'from-blue-400 to-blue-600', 'from-gold-400 to-gold-600', 'from-red-400 to-red-600'];
              return (
                <div key={s.subject}>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{s.subject}</span>
                    <span className="text-sm font-bold text-gray-900 dark:text-white">{s.count}</span>
                  </div>
                  <div className="h-3 bg-gray-100 dark:bg-dark-surface rounded-full overflow-hidden">
                    <motion.div initial={{ width: 0 }} animate={{ width: `${(s.count / 50) * 100}%` }} transition={{ delay: 0.3 + i * 0.1 }}
                      className={`h-full bg-gradient-to-r ${colors[i]} rounded-full`} />
                  </div>
                </div>
              );
            })}
          </div>
        </motion.div>
      </div>

      {/* Top Performers */}
      <motion.div variants={item} className="glass-card p-6">
        <h2 className="text-lg font-serif font-bold text-gray-900 dark:text-white mb-4">Top Performers</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {LEADERBOARD.slice(0, 6).map((u, i) => (
            <div key={u.id} className="flex items-center gap-3 p-3 rounded-xl bg-gray-50 dark:bg-dark-surface">
              <span className="text-sm font-bold text-gray-400 w-5">#{i + 1}</span>
              <div className="w-9 h-9 rounded-full bg-gradient-premium flex items-center justify-center text-white text-sm font-bold">{u.name.charAt(0)}</div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{u.name}</p>
                <p className="text-xs text-gray-400">{u.uploads} uploads · {u.downloads} DLs</p>
              </div>
              <span className="text-sm font-bold gradient-text">{u.score}</span>
            </div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
}
