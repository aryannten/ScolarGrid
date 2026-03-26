import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/useAuth';
import { motion } from 'framer-motion';
import { GraduationCap, Mail, Lock, Eye, EyeOff, ArrowRight, Sparkles, User } from 'lucide-react';

export default function LoginPage() {
  const { login, loginWithGoogle, authBusy, backendError } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('student');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  const handleSuccess = (nextUser) => {
    navigate(nextUser.role === 'admin' ? '/admin/dashboard' : '/dashboard');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email.trim()) {
      setError('Please enter your email address.');
      return;
    }

    const displayName = name.trim() || email.split('@')[0];

    const result = await login({
      role,
      email,
      password,
      username: email,
      googleName: displayName,
    });

    if (result.success) {
      handleSuccess(result.user);
    } else {
      setError(result.error);
    }
  };

  const handleGoogleSignIn = async () => {
    setError('');
    if (!email.trim()) {
      setError('Enter your email before continuing with Google.');
      return;
    }
    const displayName = name.trim() || email.split('@')[0];
    const result = await loginWithGoogle({ name: displayName, email });
    if (result.success) {
      handleSuccess(result.user);
    } else {
      setError(result.error);
    }
  };

  const activeError = error || backendError;

  return (
    <div className="min-h-screen flex bg-light-bg dark:bg-dark-bg">
      <motion.div
        initial={{ opacity: 0, x: -40 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.7 }}
        className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-brand-950 via-brand-900 to-dark-bg relative overflow-hidden flex-col items-center justify-center p-12"
      >
        <div className="absolute top-0 right-0 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-gold-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-brand-400/5 rounded-full blur-2xl" />

        <div className="relative z-10 text-center max-w-lg">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3, type: 'spring', stiffness: 200 }}
            className="w-20 h-20 rounded-2xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center mx-auto mb-8 shadow-glow"
          >
            <GraduationCap className="w-10 h-10 text-white" />
          </motion.div>

          <h1 className="text-5xl font-serif font-bold text-white mb-4 leading-tight">
            Scholar<span className="gradient-text-gold">Grid</span>
          </h1>
          <p className="text-lg text-gray-300 mb-8 leading-relaxed">
            The premium college collaboration platform. Share knowledge, engage in discussions, and rise through the ranks.
          </p>

          <div className="flex items-center justify-center gap-6 text-sm text-gray-400">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-gold-400" />
              <span>AI-Powered</span>
            </div>
            <div className="w-1 h-1 rounded-full bg-gray-600" />
            <span>Real-time Chat</span>
            <div className="w-1 h-1 rounded-full bg-gray-600" />
            <span>Gamified</span>
          </div>
        </div>
      </motion.div>

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
            <h2 className="text-3xl font-serif font-bold text-gray-900 dark:text-white mb-2">Welcome back</h2>
            <p className="text-gray-500 dark:text-gray-400">Sign in to continue your learning journey</p>
          </div>

          {activeError && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-600 dark:text-red-400 text-sm"
            >
              {activeError}
            </motion.div>
          )}

          <div className="flex bg-gray-100 dark:bg-dark-surface rounded-xl p-1 mb-6">
            <button
              type="button"
              onClick={() => setRole('student')}
              className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                role === 'student' ? 'bg-white dark:bg-dark-card text-brand-600 shadow-sm' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700'
              }`}
            >
              Student
            </button>
            <button
              type="button"
              onClick={() => setRole('admin')}
              className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                role === 'admin' ? 'bg-white dark:bg-dark-card text-gold-600 shadow-sm' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700'
              }`}
            >
              Admin
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="relative">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Full name"
                className="input-field pl-11"
              />
            </div>

            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email address"
                className="input-field pl-11"
                required
              />
            </div>

            {role === 'admin' && (
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  className="input-field pl-11 pr-11"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            )}

            <button
              type="submit"
              disabled={authBusy}
              className="btn-primary w-full flex items-center justify-center gap-2 py-3"
            >
              {authBusy ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  Sign In <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="flex items-center gap-4 my-6">
            <div className="flex-1 h-px bg-gray-200 dark:bg-dark-border" />
            <span className="text-xs text-gray-400 uppercase tracking-wider">or continue with</span>
            <div className="flex-1 h-px bg-gray-200 dark:bg-dark-border" />
          </div>

          <button
            type="button"
            onClick={handleGoogleSignIn}
            disabled={authBusy}
            className="w-full flex items-center justify-center gap-3 py-3 px-4 bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border rounded-xl text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-50 dark:hover:bg-dark-hover transition-colors disabled:opacity-60"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            {authBusy ? 'Connecting...' : 'Continue with Google'}
          </button>

          <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
            Don't have an account?{' '}
            <Link to="/signup" className="text-brand-500 hover:text-brand-600 font-semibold">Create Account</Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
