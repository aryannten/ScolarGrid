import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import { FileText, Download, Star, Trophy, Upload, MessageSquare, ArrowUpRight, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';
import PageMessage from '../../components/feedback/PageMessage';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.08 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function StudentDashboard() {
  const { user } = useAuth();
  const stats = [
    { label: 'Auth Mode', value: 'Live', icon: Upload, color: 'text-brand-500', bg: 'bg-brand-50 dark:bg-brand-900/20' },
    { label: 'Backend User ID', value: user?.id || 'N/A', icon: Download, color: 'text-emerald-500', bg: 'bg-emerald-50 dark:bg-emerald-900/20' },
    { label: 'Role', value: user?.role || 'guest', icon: Star, color: 'text-gold-500', bg: 'bg-gold-50 dark:bg-gold-900/20' },
    { label: 'Data Status', value: 'Pending', icon: Trophy, color: 'text-purple-500', bg: 'bg-purple-50 dark:bg-purple-900/20' },
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
          <p className="text-brand-200 text-sm max-w-lg">Your session is now loaded from the backend. The rest of the student features need matching ScholarGrid APIs before this dashboard can surface live notes, rank, and activity.</p>
          <div className="flex gap-3 mt-5">
            <Link to="/notes" className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm font-medium backdrop-blur-sm transition-colors border border-white/10">
              <Upload className="w-4 h-4" /> Check Notes Wiring
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

      <PageMessage
        eyebrow="Next integration step"
        title="Feature data has been disconnected from mock fixtures"
        description="Dashboard cards still render, but the app no longer injects fake notes, leaderboard ranks, or activity feed items. Add real notes, leaderboard, and activity endpoints to bring this screen back to full functionality."
        tone="warning"
      />

      <div className="grid lg:grid-cols-3 gap-6">
        <motion.div variants={item} className="lg:col-span-2 glass-card p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-serif font-bold text-gray-900 dark:text-white">Recent Activity</h2>
            <Zap className="w-5 h-5 text-gold-500" />
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            No live activity endpoint is configured for ScholarGrid yet.
          </p>
        </motion.div>

        <motion.div variants={item} className="glass-card p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-serif font-bold text-gray-900 dark:text-white">Trending Notes</h2>
            <Link to="/notes" className="text-brand-500 hover:text-brand-600 text-sm font-medium flex items-center gap-1">
              View All <ArrowUpRight className="w-3 h-3" />
            </Link>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Notes are no longer read from local demo fixtures.
          </p>
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
