import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { motion } from 'framer-motion';
import { GraduationCap, Mail, Lock, Eye, EyeOff, ArrowRight, User } from 'lucide-react';

export default function SignupPage() {
  const { signup, loading } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState('student');
  const [facultyCode, setFacultyCode] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    const result = await signup(name, email, password, role, facultyCode);
    if (result.success) {
      if (result.needsConfirmation) {
        navigate('/auth/confirm-email', { state: { email } });
      } else {
        navigate(['superadmin', 'faculty'].includes(result.user.role) ? '/admin/dashboard' : '/dashboard');
      }
    } else {
      setError(result.error);
    }
  };

  return (
    <div className="min-h-screen flex bg-light-bg dark:bg-dark-bg">
      {/* Left — Branding */}
      <motion.div
        initial={{ opacity: 0, x: -40 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.7 }}
        className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-brand-950 via-brand-900 to-dark-bg relative overflow-hidden flex-col items-center justify-center p-12"
      >
        <div className="absolute top-0 right-0 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-gold-500/10 rounded-full blur-3xl" />

        <div className="relative z-10 text-center max-w-lg">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3, type: 'spring', stiffness: 200 }}
            className="w-20 h-20 rounded-2xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center mx-auto mb-8 shadow-glow"
          >
            <GraduationCap className="w-10 h-10 text-white" />
          </motion.div>

          <h1 className="text-5xl font-serif font-bold text-white mb-4">
            Join Scholar<span className="gradient-text-gold">Grid</span>
          </h1>
          <p className="text-lg text-gray-300 leading-relaxed">
            Create your account and become part of the most vibrant academic community.
          </p>

          <div className="mt-10 grid grid-cols-3 gap-4">
            {[{ num: '5K+', label: 'Students' }, { num: '1.2K', label: 'Notes Shared' }, { num: '98%', label: 'Satisfaction' }].map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + i * 0.1 }}
                className="text-center p-4 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10"
              >
                <p className="text-2xl font-bold text-white">{stat.num}</p>
                <p className="text-xs text-gray-400">{stat.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Right — Signup Form */}
      <motion.div
        initial={{ opacity: 0, x: 40 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.7 }}
        className="w-full lg:w-1/2 flex items-center justify-center p-6 lg:p-12"
      >
        <div className="w-full max-w-md">
          <div className="flex items-center gap-3 mb-8 lg:hidden">
            <div className="w-10 h-10 rounded-xl bg-gradient-premium flex items-center justify-center">
              <GraduationCap className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-2xl font-serif font-bold text-gray-900 dark:text-white">ScholarGrid</h1>
          </div>

          <div className="mb-8">
            <h2 className="text-3xl font-serif font-bold text-gray-900 dark:text-white mb-2">Create Account</h2>
            <p className="text-gray-500 dark:text-gray-400">Start your academic journey with ScholarGrid</p>
          </div>

          {error && (
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-600 dark:text-red-400 text-sm">
              {error}
            </motion.div>
          )}

          <div className="flex bg-gray-100 dark:bg-dark-surface rounded-xl p-1 mb-6">
            <button onClick={() => setRole('student')} className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${role === 'student' ? 'bg-white dark:bg-dark-card text-brand-600 shadow-sm' : 'text-gray-500'}`}>
              Student
            </button>
            <button onClick={() => setRole('faculty')} className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${role === 'faculty' ? 'bg-white dark:bg-dark-card text-gold-600 shadow-sm' : 'text-gray-500'}`}>
              Faculty
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Full name" className="input-field pl-11" required />
            </div>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email address" className="input-field pl-11" required />
            </div>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" className="input-field pl-11 pr-11" required />
              <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="Confirm password" className="input-field pl-11" required />
            </div>
            
            {role === 'faculty' && (
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input type="text" value={facultyCode} onChange={(e) => setFacultyCode(e.target.value)} placeholder="Faculty Code" className="input-field pl-11" required />
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2 py-3">
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>Create Account <ArrowRight className="w-4 h-4" /></>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-brand-500 hover:text-brand-600 font-semibold">Sign In</Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
