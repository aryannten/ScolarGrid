import { supabase } from '../lib/supabaseClient';

/**
 * Upload a user avatar to the 'avatars' bucket.
 * @returns {string} Public URL of the uploaded avatar.
 */
export async function uploadAvatar(userId, file) {
  const ext = file.name.split('.').pop();
  const path = `${userId}/avatar.${ext}`;

  const { data, error } = await supabase.storage
    .from('avatars')
    .upload(path, file, { upsert: true });

  if (error) throw error;

  const { data: urlData } = supabase.storage
    .from('avatars')
    .getPublicUrl(data.path);

  return urlData.publicUrl;
}

/**
 * Upload a note file to 'notes-files' bucket.
 * @returns {string} Storage path of the uploaded file.
 */
export async function uploadNoteFile(userId, noteId, file) {
  const path = `${userId}/${noteId}/${file.name}`;

  const { data, error } = await supabase.storage
    .from('notes-files')
    .upload(path, file);

  if (error) throw error;
  return data.path;
}

/**
 * Upload a file attachment for a chat message.
 * @returns {string} Storage path.
 */
export async function uploadChatFile(groupId, messageId, file) {
  const path = `${groupId}/${messageId}/${file.name}`;

  const { data, error } = await supabase.storage
    .from('chat-files')
    .upload(path, file);

  if (error) throw error;
  return data.path;
}

/**
 * Get a download URL for a file in a private bucket.
 * Uses signed URLs (valid 1 hour).
 */
export async function getDownloadUrl(bucket, path) {
  const { data, error } = await supabase.storage
    .from(bucket)
    .createSignedUrl(path, 3600);

  if (error) throw error;
  return data.signedUrl;
}

/**
 * Get a public URL (for public buckets like avatars).
 */
export function getPublicUrl(bucket, path) {
  const { data } = supabase.storage.from(bucket).getPublicUrl(path);
  return data.publicUrl;
}
