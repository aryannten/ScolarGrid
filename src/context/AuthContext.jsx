import { createContext, useContext, useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null);
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch profile from public.profiles table
  const fetchProfile = async (userId) => {
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .single();
    if (error) {
      console.error('Error fetching profile:', error);
      return null;
    }
    return data;
  };

  // Build a user-like object that the rest of the app expects
  const buildUser = (authUser, profileData) => {
    if (!authUser || !profileData) return null;
    return {
      id: authUser.id,
      name: profileData.full_name || authUser.user_metadata?.full_name || '',
      email: profileData.email || authUser.email,
      role: profileData.role || 'student',
      avatar: profileData.avatar_url,
      about: profileData.about || '',
      joinedAt: profileData.created_at ? new Date(profileData.created_at).toISOString().split('T')[0] : '',
      score: profileData.points || 0,
      tier: getTier(profileData.points || 0),
      uploads: 0,    // computed on demand
      downloads: 0,  // computed on demand
      warnings: profileData.warnings || 0,
      is_banned: profileData.is_banned || false,
      points: profileData.points || 0,
    };
  };

  const getTier = (points) => {
    if (points >= 3000) return 'Elite';
    if (points >= 2000) return 'Gold';
    if (points >= 1000) return 'Silver';
    return 'Bronze';
  };

  useEffect(() => {
    // Safety timeout — never block the UI longer than 5 seconds
    const timeout = setTimeout(() => setLoading(false), 5000);

    // Get initial session
    const initSession = async () => {
      try {
        const { data: { session: s } } = await supabase.auth.getSession();
        setSession(s);
        if (s?.user) {
          const p = await fetchProfile(s.user.id);
          setProfile(p);
          setUser(buildUser(s.user, p));
        }
      } catch (err) {
        console.error('Error getting session:', err);
      } finally {
        clearTimeout(timeout);
        setLoading(false);
      }
    };
    initSession();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, s) => {
        setSession(s);
        if (s?.user) {
          const p = await fetchProfile(s.user.id);
          setProfile(p);
          setUser(buildUser(s.user, p));
        } else {
          setProfile(null);
          setUser(null);
        }
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  const login = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) {
      return { success: false, error: error.message };
    }
    const p = await fetchProfile(data.user.id);
    setProfile(p);
    const u = buildUser(data.user, p);
    setUser(u);
    return { success: true, user: u };
  };

  const signup = async (name, email, password, role) => {
    setLoading(true);
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { full_name: name, role: role || 'student' },
        emailRedirectTo: `${window.location.origin}/auth/callback`,
      },
    });
    if (error) {
      setLoading(false);
      return { success: false, error: error.message };
    }
    // If email confirmation is required, user won't have a session yet
    if (!data.session) {
      setLoading(false);
      return {
        success: true,
        user: { name, email, role: role || 'student' },
        needsConfirmation: true,
      };
    }
    const p = await fetchProfile(data.user.id);
    setProfile(p);
    const u = buildUser(data.user, p);
    setUser(u);
    setLoading(false);
    return { success: true, user: u };
  };

  const logout = async () => {
    await supabase.auth.signOut();
    setSession(null);
    setUser(null);
    setProfile(null);
  };

  const updateProfile = async (updates) => {
    if (!user) return;
    // Map frontend field names to DB column names
    const dbUpdates = {};
    if (updates.name !== undefined) dbUpdates.full_name = updates.name;
    if (updates.about !== undefined) dbUpdates.about = updates.about;
    if (updates.avatar !== undefined) dbUpdates.avatar_url = updates.avatar;
    if (updates.avatar_url !== undefined) dbUpdates.avatar_url = updates.avatar_url;

    const { error } = await supabase
      .from('profiles')
      .update(dbUpdates)
      .eq('id', user.id);

    if (!error) {
      const p = await fetchProfile(user.id);
      setProfile(p);
      setUser(buildUser(session.user, p));
    }
  };

  const refreshProfile = async () => {
    if (!session?.user) return;
    const p = await fetchProfile(session.user.id);
    setProfile(p);
    setUser(buildUser(session.user, p));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        session,
        loading,
        login,
        signup,
        logout,
        updateProfile,
        refreshProfile,
        isAdmin: user?.role === 'admin',
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
