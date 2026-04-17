import { apiGet, apiPut } from '../lib/apiClient';

/**
 * Fetch all students (admin view).
 */
export async function fetchAllStudents() {
  return apiGet('/api/users/students');
}

/**
 * Fetch all users including admins.
 */
export async function fetchAllUsers() {
  return apiGet('/api/users');
}

/**
 * Warn a user — increment warnings count.
 */
export async function warnUser(userId) {
  return apiPut(`/api/users/${userId}/warn`, {});
}

/**
 * Ban or unban a user.
 */
export async function banUser(userId, banned) {
  return apiPut(`/api/users/${userId}/ban`, { banned });
}

/**
 * Change user role (Super Admin only).
 */
export async function changeUserRole(userId, role) {
  return apiPut(`/api/users/${userId}/role`, { role });
}

/**
 * Fetch all faculty codes (Super Admin only).
 */
export async function fetchFacultyCodes() {
  return apiGet('/api/users/faculty-codes');
}

/**
 * Generate a new faculty code (Super Admin only).
 */
import { apiPost, apiDelete } from '../lib/apiClient';

export async function generateFacultyCode() {
  return apiPost('/api/users/faculty-codes', {});
}

/**
 * Delete a faculty code.
 */
export async function deleteFacultyCode(codeId) {
  return apiDelete(`/api/users/faculty-codes/${codeId}`);
}

/**
 * Update a user's profile.
 */
export async function updateUserProfile(userId, updates) {
  const dbUpdates = {};
  if (updates.full_name !== undefined) dbUpdates.full_name = updates.full_name;
  if (updates.about !== undefined) dbUpdates.about = updates.about;
  if (updates.avatar_url !== undefined) dbUpdates.avatar_url = updates.avatar_url;
  if (updates.points !== undefined) dbUpdates.points = updates.points;

  return apiPut(`/api/users/${userId}`, dbUpdates);
}

/**
 * Upgrade to Faculty using a code.
 */
export async function upgradeToFaculty(faculty_code) {
  return apiPost('/api/users/upgrade-faculty', { faculty_code });
}
