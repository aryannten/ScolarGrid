import PageMessage from './PageMessage';
import { API_BASE_URL, APP_BACKEND_NAME } from '../../config/env';

export default function UnsupportedFeaturePage({ feature, endpointHint }) {
  return (
    <div className="space-y-6">
      <PageMessage
        eyebrow="Backend mismatch"
        title={`${feature} is not wired to live data`}
        description={`This frontend route no longer reads local mock data. The configured API at ${API_BASE_URL} (${APP_BACKEND_NAME}) does not expose the ${feature.toLowerCase()} endpoints this screen needs${endpointHint ? `, such as ${endpointHint}` : ''}.`}
        tone="warning"
      >
        <p className="text-sm text-gray-600 dark:text-gray-300">
          Add the matching backend contract for ScholarGrid, then replace this placeholder with real queries through the shared API client.
        </p>
      </PageMessage>
    </div>
  );
}
