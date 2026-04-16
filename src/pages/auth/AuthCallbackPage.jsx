import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../../lib/supabaseClient';
import { motion } from 'framer-motion';
import { CheckCircle, Loader } from 'lucide-react';

export default function AuthCallbackPage() {
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if there is an error in the URL (e.g., ?error=access_denied&error_description=...)
    const params = new URLSearchParams(window.location.search);
    const hashParams = new URLSearchParams(window.location.hash.replace('#', '?'));
    
    const err = params.get('error_description') || hashParams.get('error_description');
    if (err) {
      setError(err);
      setTimeout(() => navigate('/login'), 4000);
      return;
    }

    // Set up auto-redirect if we get the session
    const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
      if (session) {
        setSuccess(true);
        // We might need to fetch the profile to know the role, 
        // but AuthContext handles the user mapping.
        // Let's just wait a bit and redirect to root to let AppRouter handle it.
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      }
    });

    // Timeout in case it hangs
    const timeout = setTimeout(() => {
      if (!success && !error) {
        navigate('/login');
      }
    }, 10000);

    return () => {
      authListener?.subscription.unsubscribe();
      clearTimeout(timeout);
    };
  }, [navigate, success, error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-light-bg dark:bg-dark-bg p-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md text-center bg-white dark:bg-dark-card p-8 rounded-2xl shadow-xl border border-gray-100 dark:border-white/5"
      >
        {error ? (
          <>
            <div className="w-16 h-16 rounded-2xl bg-red-100 dark:bg-red-900/20 flex items-center justify-center mx-auto mb-6">
              <span className="text-red-500 font-bold text-2xl">!</span>
            </div>
            <h2 className="text-2xl font-serif font-bold text-gray-900 dark:text-white mb-3">Verification Failed</h2>
            <p className="text-gray-500 dark:text-gray-400 mb-6">{error}</p>
          </>
        ) : success ? (
          <>
            <div className="w-16 h-16 rounded-2xl bg-emerald-100 dark:bg-emerald-900/20 flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-8 h-8 text-emerald-500" />
            </div>
            <h2 className="text-2xl font-serif font-bold text-gray-900 dark:text-white mb-3">Email Confirmed!</h2>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              Your email has been successfully verified. Redirecting you to the dashboard...
            </p>
          </>
        ) : (
          <>
            <div className="w-16 h-16 rounded-2xl bg-brand-100 dark:bg-brand-900/20 flex items-center justify-center mx-auto mb-6">
              <Loader className="w-8 h-8 text-brand-500 animate-spin" />
            </div>
            <h2 className="text-2xl font-serif font-bold text-gray-900 dark:text-white mb-3">Confirming Email...</h2>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              Please wait while we verify your email address. You will be redirected automatically.
            </p>
          </>
        )}
      </motion.div>
    </div>
  );
}
