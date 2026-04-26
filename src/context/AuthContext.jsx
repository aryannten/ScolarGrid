import { createContext, useContext, useState, useEffect } from 'react';
import { api, setToken, clearToken, getToken } from '../lib/apiClient';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  const getTier = (points) => {
    if (points >= 3000) return 'Elite';
    if (points >= 2000) return 'Gold';
    if (points >= 1000) return 'Silver';
    return 'Bronze';
  };

  // Retry helper — retries a fetch up to `maxAttempts` times with increasing delay.
  // Prevents ECONNREFUSED from clearing the token when the backend starts slower than Vite.
  const fetchWithRetry = async (fn, maxAttempts = 5, delayMs = 1000) => {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        return await fn();
      } catch (err) {
        const isConnRefused =
          err.message?.includes('ECONNREFUSED') ||
          err.message?.includes('Failed to fetch') ||
          err.message?.includes('NetworkError') ||
          err.message?.includes('net::ERR_CONNECTION_REFUSED');

        if (isConnRefused && attempt < maxAttempts) {
          console.warn(`[Auth] Server not ready, retrying in ${delayMs}ms… (${attempt}/${maxAttempts})`);
          await new Promise(r => setTimeout(r, delayMs));
          delayMs = Math.min(delayMs * 1.5, 5000); // exponential back-off, cap at 5s
        } else {
          throw err;
        }
      }
    }
  };

  // Check for existing token on mount
  useEffect(() => {
    const timeout = setTimeout(() => setLoading(false), 15000); // extended to cover retries

    const initSession = async () => {
      try {
        const token = getToken();
        if (!token) {
          setLoading(false);
          clearTimeout(timeout);
          return;
        }

        const data = await fetchWithRetry(() => api('/api/auth/me'));
        if (data?.user) {
          setProfile(data.user);
          setUser(data.user);
        }
      } catch (err) {
        // Only clear the token for auth errors (401/403), not network errors
        const isAuthError = err.message?.includes('401') || err.message?.includes('403') || err.message?.includes('Invalid') || err.message?.includes('expired');
        if (isAuthError) {
          console.warn('Session expired or invalid — clearing token.');
          clearToken();
        } else {
          console.warn('Server unreachable during session restore — keeping token for next load.');
        }
      } finally {
        clearTimeout(timeout);
        setLoading(false);
      }
    };

    initSession();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = async (email, password) => {
    try {
      const data = await api('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
        headers: { 'Content-Type': 'application/json' },
      });

      if (data.token) {
        setToken(data.token);
        setProfile(data.user);
        setUser(data.user);
        return { success: true, user: data.user };
      }
      return { success: false, error: 'No token received' };
    } catch (err) {
      return { success: false, error: err.message };
    }
  };

  const signup = async (name, email, password, role, facultyCode) => {
    setLoading(true);
    try {
      const data = await api('/api/auth/signup', {
        method: 'POST',
        body: JSON.stringify({ name, email, password, role: role || 'student', faculty_code: facultyCode }),
        headers: { 'Content-Type': 'application/json' },
      });

      if (data.token) {
        setToken(data.token);
        setProfile(data.user);
        setUser(data.user);
        setLoading(false);
        return { success: true, user: data.user };
      }
      setLoading(false);
      return { success: false, error: 'No token received' };
    } catch (err) {
      setLoading(false);
      return { success: false, error: err.message };
    }
  };

  const logout = async () => {
    clearToken();
    setUser(null);
    setProfile(null);
  };

  const updateProfile = async (updates) => {
    if (!user) return;
    const dbUpdates = {};
    if (updates.name !== undefined) dbUpdates.full_name = updates.name;
    if (updates.about !== undefined) dbUpdates.about = updates.about;
    if (updates.avatar !== undefined) dbUpdates.avatar_url = updates.avatar;
    if (updates.avatar_url !== undefined) dbUpdates.avatar_url = updates.avatar_url;

    try {
      await api(`/api/users/${user.id}`, {
        method: 'PUT',
        body: JSON.stringify(dbUpdates),
        headers: { 'Content-Type': 'application/json' },
      });

      // Refresh profile
      const data = await api('/api/auth/me');
      if (data.user) {
        setProfile(data.user);
        setUser(data.user);
      }
    } catch (err) {
      console.error('Update profile error:', err);
    }
  };

  const refreshProfile = async () => {
    try {
      const data = await api('/api/auth/me');
      if (data.user) {
        setProfile(data.user);
        setUser(data.user);
      }
    } catch (err) {
      console.error('Refresh profile error:', err);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        session: getToken() ? { token: getToken() } : null,
        loading,
        login,
        signup,
        logout,
        updateProfile,
        refreshProfile,
        isSuperAdmin: user?.role === 'superadmin',
        isFaculty: user?.role === 'faculty',
        isStudent: user?.role === 'student',
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
