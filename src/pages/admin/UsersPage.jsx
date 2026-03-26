import UnsupportedFeaturePage from '../../components/feedback/UnsupportedFeaturePage';

export default function UsersPage() {
  return <UnsupportedFeaturePage feature="User management" endpointHint="/api/users" />;
}
