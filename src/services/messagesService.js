import { supabase } from '../lib/supabaseClient';

/**
 * Fetch messages for a group, ordered by time.
 */
export async function fetchMessages(groupId, limit = 100) {
  const { data, error } = await supabase
    .from('messages')
    .select('*, sender:profiles!sender_id(full_name, avatar_url)')
    .eq('group_id', groupId)
    .order('created_at', { ascending: true })
    .limit(limit);

  if (error) throw error;
  return (data || []).map(mapMessage);
}

/**
 * Send a text message.
 */
export async function sendMessage(groupId, senderId, content) {
  const { data, error } = await supabase
    .from('messages')
    .insert({
      group_id: groupId,
      sender_id: senderId,
      content,
    })
    .select('*, sender:profiles!sender_id(full_name, avatar_url)')
    .single();

  if (error) throw error;
  return mapMessage(data);
}

/**
 * Send a file message — upload file to chat-files bucket, then insert message.
 */
export async function sendFileMessage(groupId, senderId, file) {
  const messageId = crypto.randomUUID();
  const path = `${groupId}/${messageId}/${file.name}`;

  // Upload file
  const { data: storageData, error: storageError } = await supabase.storage
    .from('chat-files')
    .upload(path, file);

  if (storageError) throw storageError;

  // Insert message
  const { data, error } = await supabase
    .from('messages')
    .insert({
      id: messageId,
      group_id: groupId,
      sender_id: senderId,
      content: null,
      file_url: storageData.path,
      file_name: file.name,
      file_type: file.type,
    })
    .select('*, sender:profiles!sender_id(full_name, avatar_url)')
    .single();

  if (error) throw error;
  return mapMessage(data);
}

/**
 * Subscribe to new messages in a group (realtime).
 * Returns the channel — call supabase.removeChannel(channel) to unsubscribe.
 */
export function subscribeToMessages(groupId, onNewMessage) {
  const channel = supabase
    .channel(`group-${groupId}`)
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'public',
        table: 'messages',
        filter: `group_id=eq.${groupId}`,
      },
      async (payload) => {
        // Fetch the full message with sender info
        const { data } = await supabase
          .from('messages')
          .select('*, sender:profiles!sender_id(full_name, avatar_url)')
          .eq('id', payload.new.id)
          .single();

        if (data) {
          onNewMessage(mapMessage(data));
        }
      }
    )
    .subscribe();

  return channel;
}

function mapMessage(row) {
  return {
    id: row.id,
    groupId: row.group_id,
    senderId: row.sender_id,
    senderName: row.sender?.full_name || 'Unknown',
    content: row.file_name || row.content || '',
    timestamp: row.created_at,
    type: row.file_url ? 'file' : 'text',
    fileUrl: row.file_url || null,
    fileName: row.file_name || null,
    fileType: row.file_type || null,
    fileSize: '', // not stored in messages table
  };
}
