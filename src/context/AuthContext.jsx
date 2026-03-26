import { useEffect, useState } from 'react';
import { api, ApiError } from '../lib/api';
import { AuthContext } from './AuthContextObject';

function normalizeSession(sessionData) {
  if (!sessionData?.logged_in) {
    return null;
  }

  if (sessionData.type === 'admin' && sessionData.admin) {
    return {
      id: String(sessionData.admin.id),
      name: sessionData.admin.display_name || sessionData.admin.username,
      username: sessionData.admin.username,
      role: 'admin',
    };
  }

  if (sessionData.type === 'user' && sessionData.user) {
    return {
      id: String(sessionData.user.id),
      name: sessionData.user.name,
      email: sessionData.user.email,
      avatar: sessionData.user.avatar_url,
      role: 'student',
    };
  }

  return null;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authBusy, setAuthBusy] = useState(false);
  const [backendError, setBackendError] = useState('');

  const refreshSession = async () => {
    setLoading(true);
    try {
      const sessionData = await api.get('/api/auth/session');
      setUser(normalizeSession(sessionData));
      setBackendError('');
    } catch (error) {
      setUser(null);
      setBackendError(error instanceof Error ? error.message : 'Unable to reach the backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshSession();
  }, []);

  const login = async ({ role, email, password, username, googleName }) => {
    setAuthBusy(true);
    setBackendError('');

    try {
      if (role === 'admin') {
        const data = await api.post('/api/auth/admin-login', { username, password });
        const nextUser = {
          id: String(data.admin.id),
          name: data.admin.display_name || data.admin.username,
          username: data.admin.username,
          role: 'admin',
        };
        setUser(nextUser);
        return { success: true, user: nextUser };
      }

      const derivedName = googleName?.trim() || email?.split('@')[0];
      const data = await api.post('/api/auth/google', { name: derivedName, email });
      const nextUser = {
        id: String(data.user.id),
        name: data.user.name,
        email: data.user.email,
        avatar: data.user.avatar_url,
        role: 'student',
      };
      setUser(nextUser);
      return { success: true, user: nextUser };
    } catch (error) {
      const message = error instanceof ApiError || error instanceof Error ? error.message : 'Login failed.';
      setBackendError(message);
      return { success: false, error: message };
    } finally {
      setAuthBusy(false);
    }
  };

  const signup = async () => ({
    success: false,
    error: 'No signup endpoint is available on the configured backend.',
  });

  const loginWithGoogle = async ({ name, email }) => login({ role: 'student', googleName: name, email });

  const logout = async () => {
    setAuthBusy(true);
    try {
      await api.post('/api/auth/logout', {});
      setUser(null);
      setBackendError('');
    } catch (error) {
      setBackendError(error instanceof Error ? error.message : 'Logout failed.');
    } finally {
      setAuthBusy(false);
    }
  };

  const updateProfile = async () => ({
    success: false,
    error: 'Profile updates are not supported by the configured backend.',
  });

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        authBusy,
        backendError,
        refreshSession,
        login,
        loginWithGoogle,
        signup,
        logout,
        updateProfile,
        isAdmin: user?.role === 'admin',
        isStudent: user?.role === 'student',
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
