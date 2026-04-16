import { apiGet, apiPost, apiPut } from '../lib/apiClient';

/**
 * Fetch complaints. Students see own, admins see all.
 */
export async function fetchComplaints(userId, isAdmin) {
  return apiGet('/api/complaints');
}

/**
 * Create a new complaint.
 */
export async function createComplaint(studentId, complaintData) {
  return apiPost('/api/complaints', {
    title: complaintData.title,
    description: complaintData.description,
  });
}

/**
 * Update complaint status and optional admin reply.
 */
export async function updateComplaintStatus(complaintId, status, adminReply, resolvedBy) {
  return apiPut(`/api/complaints/${complaintId}`, { status, adminReply });
}

/**
 * Subscribe to complaint updates.
 * Since we no longer use Supabase realtime, this is a no-op
 * that returns a dummy channel object for compatibility.
 */
export function subscribeToComplaints(onUpdate) {
  // Polling could be added here if needed
  return {
    close: () => {},
    unsubscribe: () => {},
  };
}
