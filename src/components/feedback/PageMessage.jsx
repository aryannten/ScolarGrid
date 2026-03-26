import { motion } from 'framer-motion';

export default function PageMessage({
  eyebrow = 'Unavailable',
  title,
  description,
  tone = 'neutral',
  children,
}) {
  const toneClasses = {
    neutral: 'border-light-border dark:border-dark-border',
    warning: 'border-amber-200 bg-amber-50/70 dark:border-amber-900/40 dark:bg-amber-900/10',
    danger: 'border-red-200 bg-red-50/70 dark:border-red-900/40 dark:bg-red-900/10',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`glass-card p-6 lg:p-8 border ${toneClasses[tone]}`}
    >
      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-500 mb-3">{eyebrow}</p>
      <h1 className="text-2xl font-serif font-bold text-gray-900 dark:text-white mb-3">{title}</h1>
      <p className="text-sm leading-6 text-gray-600 dark:text-gray-300 max-w-2xl">{description}</p>
      {children ? <div className="mt-5">{children}</div> : null}
    </motion.div>
  );
}
