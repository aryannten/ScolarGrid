import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ProtectedRoute } from './ProtectedRoute';
import LoadingScreen from '../components/feedback/LoadingScreen';

// Layouts
import StudentLayout from '../components/layout/StudentLayout';
import AdminLayout from '../components/layout/AdminLayout';

// Auth pages
import LoginPage from '../pages/auth/LoginPage';
import SignupPage from '../pages/auth/SignupPage';

// Student pages
import StudentDashboard from '../pages/student/Dashboard';
import NotesPage from '../pages/student/NotesPage';
import ChatPage from '../pages/student/ChatPage';
import LeaderboardPage from '../pages/student/LeaderboardPage';
import FeedbackPage from '../pages/student/FeedbackPage';
import ProfilePage from '../pages/student/ProfilePage';

// Admin pages
import AdminDashboard from '../pages/admin/AdminDashboard';
import GroupsPage from '../pages/admin/GroupsPage';
import NotesModeration from '../pages/admin/NotesModeration';
import UsersPage from '../pages/admin/UsersPage';
import ComplaintsPage from '../pages/admin/ComplaintsPage';
import AnalyticsPage from '../pages/admin/AnalyticsPage';

export default function AppRouter() {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingScreen label="Loading ScholarGrid..." />;
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={user ? <Navigate to={user.role === 'admin' ? '/admin/dashboard' : '/dashboard'} /> : <LoginPage />} />
        <Route path="/signup" element={user ? <Navigate to={user.role === 'admin' ? '/admin/dashboard' : '/dashboard'} /> : <SignupPage />} />

        {/* Student Routes */}
        <Route path="/" element={
          <ProtectedRoute allowedRoles={['student']}>
            <StudentLayout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<StudentDashboard />} />
          <Route path="notes" element={<NotesPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="leaderboard" element={<LeaderboardPage />} />
          <Route path="feedback" element={<FeedbackPage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>

        {/* Admin Routes */}
        <Route path="/admin" element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminLayout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/admin/dashboard" replace />} />
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="groups" element={<GroupsPage />} />
          <Route path="notes" element={<NotesModeration />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="complaints" element={<ComplaintsPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to={user ? (user.role === 'admin' ? '/admin/dashboard' : '/dashboard') : '/login'} replace />} />
      </Routes>
    </BrowserRouter>
  );
}
