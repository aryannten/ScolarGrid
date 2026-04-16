import { useLocation, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, ArrowRight, ExternalLink, Sparkles, CheckCircle, Clock } from 'lucide-react';

export default function EmailConfirmationPage() {
  const location = useLocation();
  const email = location.state?.email || 'your email';

  // Extract domain for the "Open Gmail/Mail" button
  const emailDomain = email.includes('@') ? email.split('@')[1].toLowerCase() : '';

  const getMailLink = () => {
    if (emailDomain.includes('gmail')) return 'https://mail.google.com';
    if (emailDomain.includes('outlook') || emailDomain.includes('hotmail') || emailDomain.includes('live'))
      return 'https://outlook.live.com';
    if (emailDomain.includes('yahoo')) return 'https://mail.yahoo.com';
    // Default to Gmail since it's most common
    return 'https://mail.google.com';
  };

  const getMailLabel = () => {
    if (emailDomain.includes('gmail')) return 'Open Gmail';
    if (emailDomain.includes('outlook') || emailDomain.includes('hotmail') || emailDomain.includes('live'))
      return 'Open Outlook';
    if (emailDomain.includes('yahoo')) return 'Open Yahoo Mail';
    return 'Open Gmail';
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-light-bg dark:bg-dark-bg p-6 relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-brand-500/5 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-emerald-500/5 rounded-full blur-3xl" />
      <div className="absolute top-1/3 right-1/3 w-64 h-64 bg-gold-500/5 rounded-full blur-3xl" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-lg relative z-10"
      >
        {/* Main Card */}
        <div className="bg-white dark:bg-dark-card rounded-3xl border border-gray-100 dark:border-white/5 shadow-xl p-8 lg:p-10 text-center">
          {/* Animated envelope icon */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200, damping: 15 }}
            className="relative mx-auto mb-8 w-24 h-24"
          >
            <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center shadow-glow">
              <Mail className="w-12 h-12 text-white" />
            </div>
            {/* Animated sparkle */}
            <motion.div
              animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
              transition={{ repeat: Infinity, duration: 2 }}
              className="absolute -top-2 -right-2"
            >
              <Sparkles className="w-6 h-6 text-gold-400" />
            </motion.div>
            {/* Pulsing ring */}
            <motion.div
              animate={{ scale: [1, 1.3], opacity: [0.3, 0] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
              className="absolute inset-0 rounded-3xl border-2 border-brand-400"
            />
          </motion.div>

          {/* Title */}
          <motion.h1
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-3xl font-serif font-bold text-gray-900 dark:text-white mb-3"
          >
            Check your inbox
          </motion.h1>

          {/* Description */}
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-gray-500 dark:text-gray-400 mb-2 leading-relaxed"
          >
            We've sent a confirmation link to
          </motion.p>
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45 }}
            className="text-lg font-semibold text-gray-900 dark:text-white mb-6"
          >
            {email}
          </motion.p>

          {/* Steps */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-gray-50 dark:bg-dark-surface rounded-2xl p-5 mb-8 text-left"
          >
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-7 h-7 rounded-full bg-brand-100 dark:bg-brand-900/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-bold text-brand-600 dark:text-brand-400">1</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-800 dark:text-gray-200">Open your email inbox</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Check spam/junk folder if you don't see it</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-7 h-7 rounded-full bg-brand-100 dark:bg-brand-900/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-bold text-brand-600 dark:text-brand-400">2</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-800 dark:text-gray-200">Click the confirmation link</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">The link will verify your email address</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-7 h-7 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-800 dark:text-gray-200">Sign in and start learning!</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">You'll be redirected to the login page</p>
                </div>
              </div>
            </div>
          </motion.div>

          {/* CTA: Open Mail */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="space-y-3"
          >
            <a
              href={getMailLink()}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary w-full flex items-center justify-center gap-2 py-3.5 text-base"
            >
              <ExternalLink className="w-5 h-5" />
              {getMailLabel()}
            </a>

            <Link
              to="/login"
              className="btn-secondary w-full flex items-center justify-center gap-2 py-3"
            >
              Back to Login <ArrowRight className="w-4 h-4" />
            </Link>
          </motion.div>

          {/* Timer hint */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="flex items-center justify-center gap-2 mt-6 text-xs text-gray-400"
          >
            <Clock className="w-3.5 h-3.5" />
            <span>Link expires in 24 hours</span>
          </motion.div>
        </div>

        {/* Footer note */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-center text-xs text-gray-400 mt-6"
        >
          Didn't receive the email? Check your spam folder or{' '}
          <Link to="/signup" className="text-brand-500 hover:text-brand-600 font-medium">
            try again
          </Link>
        </motion.p>
      </motion.div>
    </div>
  );
}
