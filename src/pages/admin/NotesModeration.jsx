import UnsupportedFeaturePage from '../../components/feedback/UnsupportedFeaturePage';

export default function NotesModeration() {
  return <UnsupportedFeaturePage feature="Notes moderation" endpointHint="/api/notes, /api/notes/moderation" />;
}
