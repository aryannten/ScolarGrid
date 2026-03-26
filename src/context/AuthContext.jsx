import { useEffect, useState } from 'react';
import { api, ApiError } from '../lib/api';
import { AuthContext } from './AuthContextObject';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('scholargrid-user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);
  const [authBusy, setAuthBusy] = useState(false);
  const [backendError, setBackendError] = useState('');

  // On mount, check if we have a saved user and verify the backend is reachable
  useEffect(() => {
    const checkBackend = async () => {
      try {
        await api.get('/');
        setBackendError('');
      } catch (error) {
        setBackendError('Backend is not reachable at the configured URL.');
      } finally {
        setLoading(false);
      }
    };
    checkBackend();
  }, []);

  // Persist user to localStorage
  useEffect(() => {
    if (user) {
      localStorage.setItem('scholargrid-user', JSON.stringify(user));
    } else {
      localStorage.removeItem('scholargrid-user');
    }
  }, [user]);

  const login = async ({ role, email, password, username, googleName }) => {
    setAuthBusy(true);
    setBackendError('');

    try {
      if (role === 'admin') {
        // For admin, we use test-register with admin role concept
        // The backend doesn't have a separate admin login, so we use test-register
        const adminName = username || 'Admin';
        const adminEmail = email || `${username}@scholargrid.admin`;
        const data = await api.post(`/api/v1/auth/test-register?email=${encodeURIComponent(adminEmail)}&name=${encodeURIComponent(adminName)}`, {});
        const nextUser = {
          id: String(data.id),
          name: data.name,
          email: data.email,
          role: 'admin',
        };
        setUser(nextUser);
        return { success: true, user: nextUser };
      }

      // Student login via test-register (no Firebase needed for development)
      const derivedName = googleName?.trim() || email?.split('@')[0] || 'Student';
      const data = await api.post(`/api/v1/auth/test-register?email=${encodeURIComponent(email)}&name=${encodeURIComponent(derivedName)}`, {});
      const nextUser = {
        id: String(data.id),
        name: data.name,
        email: data.email,
        avatar: data.avatar_url,
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

  const signup = async ({ name, email }) => {
    setAuthBusy(true);
    setBackendError('');
    try {
      const data = await api.post(`/api/v1/auth/test-register?email=${encodeURIComponent(email)}&name=${encodeURIComponent(name)}`, {});
      const nextUser = {
        id: String(data.id),
        name: data.name,
        email: data.email,
        role: 'student',
      };
      setUser(nextUser);
      return { success: true, user: nextUser };
    } catch (error) {
      const message = error instanceof ApiError || error instanceof Error ? error.message : 'Signup failed.';
      setBackendError(message);
      return { success: false, error: message };
    } finally {
      setAuthBusy(false);
    }
  };

  const loginWithGoogle = async ({ name, email }) => login({ role: 'student', googleName: name, email });

  const logout = async () => {
    setUser(null);
    localStorage.removeItem('scholargrid-user');
    setBackendError('');
  };

  const updateProfile = async (updates) => {
    setUser(prev => ({ ...prev, ...updates }));
    return { success: true };
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        authBusy,
        backendError,
        refreshSession: () => {},
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
