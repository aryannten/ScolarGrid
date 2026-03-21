import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import { NOTES, ACTIVITY_FEED, LEADERBOARD } from '../../data/mockData';
import { FileText, Download, Star, Trophy, Upload, MessageSquare, ArrowUpRight, TrendingUp, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.08 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function StudentDashboard() {
  const { user } = useAuth();

  const stats = [
    { label: 'Notes Uploaded', value: user?.uploads || 23, icon: Upload, color: 'text-brand-500', bg: 'bg-brand-50 dark:bg-brand-900/20' },
    { label: 'Total Downloads', value: user?.downloads || 156, icon: Download, color: 'text-emerald-500', bg: 'bg-emerald-50 dark:bg-emerald-900/20' },
    { label: 'Current Rating', value: '4.7', icon: Star, color: 'text-gold-500', bg: 'bg-gold-50 dark:bg-gold-900/20' },
    { label: 'Leaderboard Rank', value: `#${LEADERBOARD.findIndex(u => u.id === user?.id) + 1 || 2}`, icon: Trophy, color: 'text-purple-500', bg: 'bg-purple-50 dark:bg-purple-900/20' },
  ];

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      {/* Welcome Banner */}
      <motion.div variants={item} className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-brand-600 via-brand-700 to-brand-900 p-6 lg:p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/4" />
        <div className="absolute bottom-0 right-1/4 w-32 h-32 bg-gold-400/10 rounded-full translate-y-1/2" />
        <div className="relative z-10">
          <p className="text-brand-200 text-sm font-medium mb-1">Welcome back,</p>
          <h1 className="text-2xl lg:text-3xl font-serif font-bold text-white mb-2">{user?.name || 'Scholar'} ✨</h1>
          <p className="text-brand-200 text-sm max-w-lg">Continue your learning journey. You've made great progress this week!</p>
          <div className="flex gap-3 mt-5">
            <Link to="/notes" className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm font-medium backdrop-blur-sm transition-colors border border-white/10">
              <Upload className="w-4 h-4" /> Upload Notes
            </Link>
            <Link to="/chat" className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm font-medium backdrop-blur-sm transition-colors border border-white/10">
              <MessageSquare className="w-4 h-4" /> Join Chat
            </Link>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div variants={item} className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            variants={item}
            className="glass-card-hover p-5"
          >
            <div className={`w-10 h-10 rounded-xl ${stat.bg} flex items-center justify-center mb-3`}>
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{stat.label}</p>
          </motion.div>
        ))}
      </motion.div>

      {/* Two Column Layout */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <motion.div variants={item} className="lg:col-span-2 glass-card p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-serif font-bold text-gray-900 dark:text-white">Recent Activity</h2>
            <Zap className="w-5 h-5 text-gold-500" />
          </div>
          <div className="space-y-4">
            {ACTIVITY_FEED.slice(0, 5).map((activity) => (
              <div key={activity.id} className="flex items-start gap-3 group">
                <div className="w-8 h-8 rounded-full bg-brand-50 dark:bg-brand-900/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  {activity.type === 'upload' && <Upload className="w-4 h-4 text-brand-500" />}
                  {activity.type === 'rating' && <Star className="w-4 h-4 text-gold-500" />}
                  {activity.type === 'join' && <MessageSquare className="w-4 h-4 text-emerald-500" />}
                  {activity.type === 'complaint' && <FileText className="w-4 h-4 text-orange-500" />}
                  {activity.type === 'download' && <Download className="w-4 h-4 text-blue-500" />}
                  {activity.type === 'resolve' && <TrendingUp className="w-4 h-4 text-emerald-500" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    <span className="font-semibold">{activity.user}</span>{' '}
                    {activity.action}{' '}
                    <span className="font-medium text-brand-600 dark:text-brand-400">{activity.target}</span>
                    {activity.detail && <span className="text-gold-500 ml-1">({activity.detail})</span>}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Top Notes */}
        <motion.div variants={item} className="glass-card p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-serif font-bold text-gray-900 dark:text-white">Trending Notes</h2>
            <Link to="/notes" className="text-brand-500 hover:text-brand-600 text-sm font-medium flex items-center gap-1">
              View All <ArrowUpRight className="w-3 h-3" />
            </Link>
          </div>
          <div className="space-y-3">
            {NOTES.sort((a, b) => b.downloads - a.downloads).slice(0, 4).map((note, i) => (
              <div key={note.id} className="flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-dark-hover transition-colors cursor-pointer group">
                <span className="text-lg font-bold text-gray-300 dark:text-gray-600 w-6">{i + 1}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">{note.title}</p>
                  <div className="flex items-center gap-2 text-xs text-gray-400 mt-0.5">
                    <span className="flex items-center gap-1"><Star className="w-3 h-3 text-gold-400" />{note.rating}</span>
                    <span>·</span>
                    <span>{note.downloads} downloads</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <motion.div variants={item} className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { label: 'Browse Notes', desc: 'Explore shared academic resources', icon: FileText, to: '/notes', color: 'from-brand-500 to-brand-700' },
          { label: 'Leaderboard', desc: 'See top contributors and your rank', icon: Trophy, to: '/leaderboard', color: 'from-gold-500 to-gold-700' },
          { label: 'Submit Feedback', desc: 'Report issues or suggest features', icon: MessageSquare, to: '/feedback', color: 'from-emerald-500 to-emerald-700' },
        ].map((action) => (
          <Link key={action.label} to={action.to} className="group">
            <div className="glass-card-hover p-5 flex items-center gap-4">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${action.color} flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform`}>
                <action.icon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm">{action.label}</h3>
                <p className="text-xs text-gray-500 dark:text-gray-400">{action.desc}</p>
              </div>
              <ArrowUpRight className="w-4 h-4 text-gray-400 ml-auto group-hover:text-brand-500 transition-colors" />
            </div>
          </Link>
        ))}
      </motion.div>
    </motion.div>
  );
}
