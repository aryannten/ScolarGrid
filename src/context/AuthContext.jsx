import { createContext, useContext, useState, useEffect } from 'react';
import { USERS } from '../data/mockData';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('scholargrid-user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      localStorage.setItem('scholargrid-user', JSON.stringify(user));
    } else {
      localStorage.removeItem('scholargrid-user');
    }
  }, [user]);

  const login = async (email, password, role) => {
    setLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const mockUser = role === 'admin' 
      ? USERS.find(u => u.role === 'admin') 
      : USERS.find(u => u.role === 'student' && u.email === email) || USERS.find(u => u.role === 'student');
    
    if (mockUser) {
      setUser(mockUser);
      setLoading(false);
      return { success: true, user: mockUser };
    }
    setLoading(false);
    return { success: false, error: 'Invalid credentials' };
  };

  const signup = async (name, email, password, role) => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const newUser = {
      id: String(Date.now()),
      name,
      email,
      role,
      avatar: null,
      about: '',
      joinedAt: new Date().toISOString().split('T')[0],
      score: 0,
      tier: 'Bronze',
      uploads: 0,
      downloads: 0,
    };
    
    setUser(newUser);
    setLoading(false);
    return { success: true, user: newUser };
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('scholargrid-user');
  };

  const updateProfile = (updates) => {
    setUser(prev => ({ ...prev, ...updates }));
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, updateProfile, isAdmin: user?.role === 'admin', isStudent: user?.role === 'student' }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
