import UnsupportedFeaturePage from '../../components/feedback/UnsupportedFeaturePage';

export default function ComplaintsPage() {
  return <UnsupportedFeaturePage feature="Complaint resolution" endpointHint="/api/complaints" />;
}
