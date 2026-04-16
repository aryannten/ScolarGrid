import { supabase } from '../lib/supabaseClient';

/**
 * Fetch notes with optional filters.
 */
export async function fetchNotes({ subject, search, sortBy, limit } = {}) {
  let query = supabase
    .from('notes')
    .select('*, uploader:profiles!uploader_id(full_name, avatar_url)');

  if (subject && subject !== 'All') {
    query = query.eq('subject', subject);
  }

  if (search) {
    query = query.or(`title.ilike.%${search}%,description.ilike.%${search}%`);
  }

  if (sortBy === 'rating') {
    // notes table doesn't have rating yet, sort by downloads as proxy
    query = query.order('downloads', { ascending: false });
  } else if (sortBy === 'downloads') {
    query = query.order('downloads', { ascending: false });
  } else {
    query = query.order('created_at', { ascending: false });
  }

  if (limit) {
    query = query.limit(limit);
  }

  const { data, error } = await query;
  if (error) throw error;

  // Map to frontend-expected shape
  return (data || []).map(mapNote);
}

/**
 * Fetch distinct subjects from notes.
 */
export async function fetchSubjects() {
  const { data, error } = await supabase
    .from('notes')
    .select('subject')
    .order('subject');

  if (error) throw error;
  const unique = [...new Set((data || []).map((n) => n.subject))];
  return unique;
}

/**
 * Upload a new note (file + metadata).
 */
export async function uploadNote(userId, noteData, file) {
  const noteId = crypto.randomUUID();

  // 1. Upload file to storage
  let fileUrl = '';
  let filePath = '';
  if (file) {
    const path = `${userId}/${noteId}/${file.name}`;
    const { data: storageData, error: storageError } = await supabase.storage
      .from('notes-files')
      .upload(path, file);
    if (storageError) throw storageError;
    filePath = storageData.path;

    // Get a URL for the file
    const { data: urlData } = supabase.storage
      .from('notes-files')
      .getPublicUrl(filePath);
    fileUrl = urlData.publicUrl;
  }

  // 2. Insert note record
  const { data, error } = await supabase.from('notes').insert({
    id: noteId,
    uploader_id: userId,
    title: noteData.title,
    description: noteData.description || null,
    subject: noteData.subject,
    file_url: fileUrl || 'pending',
    file_name: file?.name || 'unknown',
    file_type: file?.type || 'application/octet-stream',
    file_size: file?.size || 0,
  }).select('*, uploader:profiles!uploader_id(full_name, avatar_url)').single();

  if (error) throw error;
  return mapNote(data);
}

/**
 * Delete a note by ID.
 */
export async function deleteNote(noteId) {
  const { error } = await supabase.from('notes').delete().eq('id', noteId);
  if (error) throw error;
}

/**
 * Flag or unflag a note.
 */
export async function flagNote(noteId, flagged) {
  const { error } = await supabase
    .from('notes')
    .update({ is_flagged: flagged })
    .eq('id', noteId);
  if (error) throw error;
}

/**
 * Approve or unapprove a note.
 */
export async function approveNote(noteId, approved) {
  const { error } = await supabase
    .from('notes')
    .update({ is_approved: approved })
    .eq('id', noteId);
  if (error) throw error;
}

/**
 * Map a Supabase note row to the frontend shape.
 */
function mapNote(row) {
  return {
    id: row.id,
    title: row.title,
    description: row.description || '',
    subject: row.subject,
    tags: row.subject ? [row.subject] : [],
    uploaderId: row.uploader_id,
    uploaderName: row.uploader?.full_name || 'Unknown',
    createdAt: row.created_at ? new Date(row.created_at).toISOString().split('T')[0] : '',
    fileType: getFileTypeLabel(row.file_type),
    fileSize: formatFileSize(row.file_size),
    fileUrl: row.file_url,
    fileName: row.file_name,
    downloads: row.downloads || 0,
    rating: 0,        // no rating column yet
    totalRatings: 0,
    isFlagged: row.is_flagged,
    isApproved: row.is_approved,
    modStatus: row.is_flagged ? 'Flagged' : 'Approved',
  };
}

function getFileTypeLabel(mimeType) {
  if (!mimeType) return 'FILE';
  if (mimeType.includes('pdf')) return 'PDF';
  if (mimeType.includes('word') || mimeType.includes('document')) return 'DOC';
  if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) return 'PPT';
  if (mimeType.includes('image')) return 'IMG';
  if (mimeType.includes('text')) return 'TXT';
  return 'FILE';
}

function formatFileSize(bytes) {
  if (!bytes) return '0 B';
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
}
