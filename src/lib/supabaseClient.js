/**
 * DEPRECATED — Supabase client is no longer used.
 * All services now use apiClient.js with the Express backend.
 *
 * This file is kept as a stub so that any stale imports
 * don't crash the app at startup.
 */

export const supabase = {
  from: () => ({
    select: () => ({ eq: () => ({ single: () => ({ data: null, error: { message: 'Supabase removed — use apiClient' } }) }) }),
  }),
  auth: {
    getSession: () => Promise.resolve({ data: { session: null } }),
    signInWithPassword: () => Promise.resolve({ data: null, error: { message: 'Use /api/auth/login' } }),
    signUp: () => Promise.resolve({ data: null, error: { message: 'Use /api/auth/signup' } }),
    signOut: () => Promise.resolve(),
    onAuthStateChange: () => ({ data: { subscription: { unsubscribe: () => {} } } }),
  },
  storage: {
    from: () => ({
      upload: () => Promise.resolve({ data: null, error: { message: 'Use multer endpoints' } }),
      getPublicUrl: () => ({ data: { publicUrl: '' } }),
    }),
  },
  channel: () => ({
    on: () => ({ subscribe: () => ({}) }),
  }),
  removeChannel: () => {},
};
