import { supabase } from '../lib/supabaseClient';

/**
 * Fetch complaints. Students see own, admins see all.
 */
export async function fetchComplaints(userId, isAdmin) {
  let query = supabase
    .from('complaints')
    .select('*, student:profiles!student_id(full_name)')
    .order('created_at', { ascending: false });

  if (!isAdmin && userId) {
    query = query.eq('student_id', userId);
  }

  const { data, error } = await query;
  if (error) throw error;
  return (data || []).map(mapComplaint);
}

/**
 * Create a new complaint.
 */
export async function createComplaint(studentId, complaintData) {
  const { data, error } = await supabase
    .from('complaints')
    .insert({
      student_id: studentId,
      title: complaintData.title,
      description: complaintData.description,
    })
    .select('*, student:profiles!student_id(full_name)')
    .single();

  if (error) throw error;
  return mapComplaint(data);
}

/**
 * Update complaint status and optional admin reply.
 */
export async function updateComplaintStatus(complaintId, status, adminReply, resolvedBy) {
  const updates = { status };
  if (adminReply !== undefined) updates.admin_reply = adminReply;
  if (resolvedBy) updates.resolved_by = resolvedBy;

  const { data, error } = await supabase
    .from('complaints')
    .update(updates)
    .eq('id', complaintId)
    .select('*, student:profiles!student_id(full_name)')
    .single();

  if (error) throw error;
  return mapComplaint(data);
}

/**
 * Subscribe to complaint updates (realtime).
 */
export function subscribeToComplaints(onUpdate) {
  const channel = supabase
    .channel('complaints-updates')
    .on(
      'postgres_changes',
      {
        event: 'UPDATE',
        schema: 'public',
        table: 'complaints',
      },
      async (payload) => {
        const { data } = await supabase
          .from('complaints')
          .select('*, student:profiles!student_id(full_name)')
          .eq('id', payload.new.id)
          .single();

        if (data) onUpdate(mapComplaint(data));
      }
    )
    .subscribe();

  return channel;
}

function mapComplaint(row) {
  // Map DB status values to frontend display values
  const statusMap = {
    open: 'Open',
    in_progress: 'In Progress',
    resolved: 'Resolved',
    rejected: 'Closed',
  };

  return {
    id: row.id,
    userId: row.student_id,
    userName: row.student?.full_name || 'Unknown',
    category: 'General',
    title: row.title,
    description: row.description,
    status: statusMap[row.status] || row.status,
    priority: 'Medium',
    createdAt: row.created_at,
    resolvedAt: row.status === 'resolved' ? row.updated_at : null,
    adminResponse: row.admin_reply,
  };
}
