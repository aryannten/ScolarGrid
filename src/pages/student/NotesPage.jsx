import UnsupportedFeaturePage from '../../components/feedback/UnsupportedFeaturePage';

export default function NotesPage() {
  return <UnsupportedFeaturePage feature="Notes" endpointHint="/api/notes, /api/notes/:id, /api/notes/upload" />;
}
