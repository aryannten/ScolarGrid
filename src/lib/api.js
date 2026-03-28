import { API_BASE_URL } from '../config/env';

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function parseResponse(response) {
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return response.json();
  }

  const text = await response.text();
  return text ? { message: text } : null;
}

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer test-token',
      ...options.headers,
    },
    ...options,
  });

  const data = await parseResponse(response);

  if (!response.ok) {
    const message = data?.error || data?.message || `Request failed with status ${response.status}`;
    throw new ApiError(message, response.status, data);
  }

  return data;
}

export const api = {
  get: (path, options) => apiRequest(path, { ...options, method: 'GET' }),
  post: (path, body, options) => apiRequest(path, { ...options, method: 'POST', body: JSON.stringify(body) }),
  put: (path, body, options) => apiRequest(path, { ...options, method: 'PUT', body: JSON.stringify(body) }),
  patch: (path, body, options) => apiRequest(path, { ...options, method: 'PATCH', body: JSON.stringify(body) }),
  delete: (path, options) => apiRequest(path, { ...options, method: 'DELETE' }),
};
