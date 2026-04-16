/**
 * Shared API client — wraps fetch with JWT auth headers.
 * Replaces the old supabaseClient.js
 */

const API_BASE = '';  // Vite proxy handles /api -> localhost:3001

export function getToken() {
  return localStorage.getItem('sg_token');
}

export function setToken(token) {
  localStorage.setItem('sg_token', token);
}

export function clearToken() {
  localStorage.removeItem('sg_token');
}

/**
 * Generic fetch wrapper with auth.
 */
export async function api(path, options = {}) {
  const token = getToken();
  const headers = { ...(options.headers || {}) };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Don't set Content-Type for FormData (browser sets multipart boundary)
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(errorData.error || `HTTP ${res.status}`);
  }

  return res.json();
}

/**
 * Convenience methods
 */
export const apiGet = (path) => api(path);
export const apiPost = (path, body) =>
  api(path, {
    method: 'POST',
    body: body instanceof FormData ? body : JSON.stringify(body),
  });
export const apiPut = (path, body) =>
  api(path, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
export const apiDelete = (path) =>
  api(path, { method: 'DELETE' });
