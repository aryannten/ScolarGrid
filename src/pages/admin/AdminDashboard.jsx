import UnsupportedFeaturePage from '../../components/feedback/UnsupportedFeaturePage';

export default function AdminDashboard() {
  return <UnsupportedFeaturePage feature="Admin analytics dashboard" endpointHint="/api/analytics, /api/users, /api/complaints" />;
}
