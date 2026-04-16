import { apiGet, apiPost, apiDelete, apiPut } from '../lib/apiClient';

/**
 * Fetch notes with optional filters.
 */
export async function fetchNotes({ subject, search, sortBy, limit } = {}) {
  const params = new URLSearchParams();
  if (subject && subject !== 'All') params.set('subject', subject);
  if (search) params.set('search', search);
  if (sortBy) params.set('sortBy', sortBy);
  if (limit) params.set('limit', limit);

  const qs = params.toString();
  return apiGet(`/api/notes${qs ? '?' + qs : ''}`);
}

/**
 * Fetch distinct subjects from notes.
 */
export async function fetchSubjects() {
  return apiGet('/api/notes/subjects');
}

/**
 * Upload a new note (file + metadata).
 */
export async function uploadNote(userId, noteData, file) {
  const formData = new FormData();
  if (file) formData.append('note', file);
  formData.append('title', noteData.title);
  formData.append('subject', noteData.subject);
  if (noteData.description) formData.append('description', noteData.description);

  return apiPost('/api/notes', formData);
}

/**
 * Delete a note by ID.
 */
export async function deleteNote(noteId) {
  return apiDelete(`/api/notes/${noteId}`);
}

/**
 * Flag or unflag a note.
 */
export async function flagNote(noteId, flagged) {
  return apiPut(`/api/notes/${noteId}/flag`, { flagged });
}

/**
 * Approve or unapprove a note.
 */
export async function approveNote(noteId, approved) {
  return apiPut(`/api/notes/${noteId}/approve`, { approved });
}
