import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { GraduationCap } from 'lucide-react';
import PageMessage from '../../components/feedback/PageMessage';
import { API_BASE_URL } from '../../config/env';

export default function SignupPage() {
  return (
    <div className="min-h-screen flex bg-light-bg dark:bg-dark-bg items-center justify-center p-6 lg:p-12">
      <div className="w-full max-w-2xl">
        <div className="flex items-center gap-3 mb-8 justify-center">
          <div className="w-12 h-12 rounded-xl bg-gradient-premium flex items-center justify-center">
            <GraduationCap className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-3xl font-serif font-bold text-gray-900 dark:text-white">ScholarGrid</h1>
        </div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <PageMessage
            eyebrow="Signup unavailable"
            title="Registration is disabled until the backend exposes a real signup flow"
            description={`This frontend no longer creates local fake accounts. The configured API at ${API_BASE_URL} does not provide a registration endpoint for students or admins.`}
            tone="warning"
          >
            <div className="flex flex-wrap gap-3">
              <Link to="/login" className="btn-primary">
                Back to Login
              </Link>
              <a href={API_BASE_URL} target="_blank" rel="noreferrer" className="btn-secondary">
                Open Backend Base URL
              </a>
            </div>
          </PageMessage>
        </motion.div>
      </div>
    </div>
  );
}
