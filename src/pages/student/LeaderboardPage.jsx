import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import { fetchLeaderboard, TIER_THRESHOLDS } from '../../services/leaderboardService';
import { Trophy, Medal, Star, TrendingUp, Crown, Award, Flame } from 'lucide-react';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

const tierConfig = {
  Elite: { color: 'from-purple-500 to-indigo-600', text: 'text-purple-500', bg: 'bg-purple-50 dark:bg-purple-900/20', border: 'border-purple-500/30', icon: Crown },
  Gold: { color: 'from-gold-400 to-gold-600', text: 'text-gold-500', bg: 'bg-gold-50 dark:bg-gold-900/20', border: 'border-gold-500/30', icon: Award },
  Silver: { color: 'from-gray-300 to-gray-500', text: 'text-gray-400', bg: 'bg-gray-100 dark:bg-gray-800', border: 'border-gray-400/30', icon: Medal },
  Bronze: { color: 'from-orange-400 to-orange-600', text: 'text-orange-500', bg: 'bg-orange-50 dark:bg-orange-900/20', border: 'border-orange-500/30', icon: Flame },
};

export default function LeaderboardPage() {
  const { user } = useAuth();
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboard();
  }, []);

  const loadLeaderboard = async () => {
    try {
      const data = await fetchLeaderboard(50);
      setLeaderboard(data);
    } catch (err) {
      console.error('Error loading leaderboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const top3 = leaderboard.slice(0, 3);
  const rest = leaderboard.slice(3);
  const currentUserRank = leaderboard.findIndex(u => u.id === user?.id) + 1;

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 rounded bg-gray-100 dark:bg-dark-surface animate-pulse" />
        <div className="h-24 rounded-2xl bg-gray-100 dark:bg-dark-surface animate-pulse" />
        <div className="h-64 rounded-2xl bg-gray-100 dark:bg-dark-surface animate-pulse" />
      </div>
    );
  }

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item}>
        <h1 className="page-title">Leaderboard</h1>
        <p className="page-subtitle">Top contributors and their achievements</p>
      </motion.div>

      {/* Your Rank Banner */}
      {currentUserRank > 0 && (
        <motion.div variants={item} className="glass-card p-5 flex items-center gap-4 border-l-4 border-brand-500">
          <div className="w-12 h-12 rounded-full bg-gradient-premium flex items-center justify-center text-white font-bold text-lg">
            #{currentUserRank}
          </div>
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Your Current Rank</p>
            <p className="text-lg font-bold text-gray-900 dark:text-white">{user?.name}</p>
          </div>
          <div className="ml-auto text-right">
            <p className="text-2xl font-bold gradient-text">{user?.score || 0}</p>
            <span className={`badge ${tierConfig[user?.tier || 'Bronze'].bg} ${tierConfig[user?.tier || 'Bronze'].text} text-xs font-bold`}>
              {user?.tier || 'Bronze'}
            </span>
          </div>
        </motion.div>
      )}

      {/* Top 3 Podium */}
      {top3.length > 0 && (
        <motion.div variants={item} className="flex items-end justify-center gap-4 py-8">
          {/* 2nd Place */}
          {top3[1] && (
            <motion.div variants={item} className="text-center">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-gray-300 to-gray-500 flex items-center justify-center mx-auto mb-2 border-2 border-gray-300 shadow-lg">
                <span className="text-xl font-bold text-white">{top3[1].name.charAt(0)}</span>
              </div>
              <p className="text-sm font-semibold text-gray-900 dark:text-white truncate max-w-[100px]">{top3[1].name.split(' ')[0]}</p>
              <p className="text-xs text-gray-400">{top3[1].score} pts</p>
              <div className="mt-2 w-24 h-20 bg-gray-200 dark:bg-gray-700 rounded-t-xl flex items-center justify-center">
                <span className="text-2xl font-bold text-gray-400">2</span>
              </div>
            </motion.div>
          )}

          {/* 1st Place */}
          {top3[0] && (
            <motion.div variants={item} className="text-center">
              <motion.div animate={{ y: [0, -8, 0] }} transition={{ repeat: Infinity, duration: 2 }} className="mb-2">
                <Crown className="w-8 h-8 text-gold-400 mx-auto mb-1" />
              </motion.div>
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center mx-auto mb-2 border-2 border-gold-300 shadow-glow-gold">
                <span className="text-2xl font-bold text-white">{top3[0].name.charAt(0)}</span>
              </div>
              <p className="text-sm font-semibold text-gray-900 dark:text-white">{top3[0].name.split(' ')[0]}</p>
              <p className="text-xs text-gold-500 font-bold">{top3[0].score} pts</p>
              <div className="mt-2 w-28 h-28 bg-gradient-to-t from-gold-500/30 to-gold-400/10 dark:from-gold-900/40 dark:to-gold-800/10 rounded-t-xl flex items-center justify-center border border-gold-400/30">
                <span className="text-3xl font-bold gradient-text-gold">1</span>
              </div>
            </motion.div>
          )}

          {/* 3rd Place */}
          {top3[2] && (
            <motion.div variants={item} className="text-center">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center mx-auto mb-2 border-2 border-orange-300 shadow-lg">
                <span className="text-xl font-bold text-white">{top3[2].name.charAt(0)}</span>
              </div>
              <p className="text-sm font-semibold text-gray-900 dark:text-white truncate max-w-[100px]">{top3[2].name.split(' ')[0]}</p>
              <p className="text-xs text-gray-400">{top3[2].score} pts</p>
              <div className="mt-2 w-24 h-16 bg-orange-200/50 dark:bg-orange-900/20 rounded-t-xl flex items-center justify-center border border-orange-400/20">
                <span className="text-2xl font-bold text-orange-400">3</span>
              </div>
            </motion.div>
          )}
        </motion.div>
      )}

      {/* Tier Legend */}
      <motion.div variants={item} className="flex flex-wrap justify-center gap-4">
        {Object.entries(TIER_THRESHOLDS).map(([tier, threshold]) => {
          const cfg = tierConfig[tier];
          return (
            <div key={tier} className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${cfg.bg} border ${cfg.border}`}>
              <cfg.icon className={`w-4 h-4 ${cfg.text}`} />
              <span className={`text-xs font-bold ${cfg.text}`}>{tier}</span>
              <span className="text-xs text-gray-400">{threshold}+</span>
            </div>
          );
        })}
      </motion.div>

      {/* Full Rankings Table */}
      <motion.div variants={item} className="glass-card overflow-hidden">
        <div className="table-header px-6 py-3 flex items-center text-xs font-semibold text-gray-500 uppercase tracking-wider">
          <span className="w-16">Rank</span>
          <span className="flex-1">Contributor</span>
          <span className="w-20 text-center">Tier</span>
          <span className="w-24 text-right">Score</span>
        </div>
        {leaderboard.length === 0 && (
          <div className="text-center py-12">
            <Trophy className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No rankings yet. Upload notes to earn points!</p>
          </div>
        )}
        {leaderboard.map((entry) => {
          const cfg = tierConfig[entry.tier || 'Bronze'];
          const isCurrentUser = entry.id === user?.id;
          return (
            <div key={entry.id} className={`table-row px-6 py-3 flex items-center ${isCurrentUser ? 'bg-brand-50/50 dark:bg-brand-900/10' : ''}`}>
              <span className="w-16 text-sm font-bold text-gray-700 dark:text-gray-300">
                {entry.rank <= 3 ? (
                  <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-white text-xs font-bold bg-gradient-to-br ${
                    entry.rank === 1 ? 'from-gold-400 to-gold-600' :
                    entry.rank === 2 ? 'from-gray-300 to-gray-500' :
                    'from-orange-400 to-orange-600'
                  }`}>{entry.rank}</span>
                ) : `#${entry.rank}`}
              </span>
              <div className="flex-1 flex items-center gap-3">
                <div className={`w-8 h-8 rounded-full bg-gradient-to-br ${cfg.color} flex items-center justify-center text-white text-xs font-bold`}>
                  {entry.name.charAt(0)}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {entry.name} {isCurrentUser && <span className="text-brand-500 text-xs">(You)</span>}
                  </p>
                  <p className="text-xs text-gray-400">{entry.about}</p>
                </div>
              </div>
              <span className="w-20 text-center">
                <span className={`badge ${cfg.bg} ${cfg.text} text-xs font-bold`}>{entry.tier || 'Bronze'}</span>
              </span>
              <span className="w-24 text-right text-sm font-bold text-gray-900 dark:text-white flex items-center justify-end gap-1">
                <TrendingUp className="w-3 h-3 text-emerald-500" /> {entry.score || 0}
              </span>
            </div>
          );
        })}
      </motion.div>
    </motion.div>
  );
}
