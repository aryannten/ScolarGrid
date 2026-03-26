import UnsupportedFeaturePage from '../../components/feedback/UnsupportedFeaturePage';

export default function ChatPage() {
  return <UnsupportedFeaturePage feature="Chat" endpointHint="/api/groups, /api/groups/:id/messages" />;
}
