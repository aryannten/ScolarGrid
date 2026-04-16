import { api, getToken } from '../lib/apiClient';

/**
 * Upload a user avatar.
 * @returns {string} URL of the uploaded avatar.
 */
export async function uploadAvatar(userId, file) {
  const formData = new FormData();
  formData.append('avatar', file);

  const token = getToken();
  const res = await fetch(`/api/users/${userId}/avatar`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `HTTP ${res.status}`);
  }

  const data = await res.json();
  return data.avatar_url;
}

/**
 * Upload a note file — handled by notesService.uploadNote
 * Kept for backwards compatibility.
 */
export async function uploadNoteFile(userId, noteId, file) {
  // Notes are uploaded directly via POST /api/notes with multer
  // This function is a no-op — file upload is handled in notesService
  return `/uploads/notes/${file.name}`;
}

/**
 * Upload a file attachment for a chat message.
 * Handled by messagesService.sendFileMessage
 */
export async function uploadChatFile(groupId, messageId, file) {
  return `/uploads/chat/${file.name}`;
}

/**
 * Get a download URL for a file.
 * Files are served statically, so we just return the path.
 */
export async function getDownloadUrl(bucket, path) {
  // Files are served via Express static at /uploads/...
  return `/uploads/${bucket}/${path}`;
}

/**
 * Get a public URL.
 */
export function getPublicUrl(bucket, path) {
  return `/uploads/${bucket}/${path}`;
}
