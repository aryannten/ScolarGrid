import { supabase } from '../lib/supabaseClient';

/**
 * Fetch groups the user is a member of.
 */
export async function fetchUserGroups(userId) {
  const { data, error } = await supabase
    .from('group_members')
    .select('group_id, joined_at, group:groups(*)')
    .eq('user_id', userId);

  if (error) throw error;

  // Get member counts for each group
  const groups = await Promise.all(
    (data || []).map(async (gm) => {
      const { count } = await supabase
        .from('group_members')
        .select('*', { count: 'exact', head: true })
        .eq('group_id', gm.group_id);

      // Get most recent message
      const { data: lastMsg } = await supabase
        .from('messages')
        .select('content, created_at')
        .eq('group_id', gm.group_id)
        .order('created_at', { ascending: false })
        .limit(1)
        .single();

      return mapGroup(gm.group, count || 0, lastMsg);
    })
  );

  return groups;
}

/**
 * Fetch all groups (admin).
 */
export async function fetchAllGroups() {
  const { data, error } = await supabase
    .from('groups')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) throw error;

  const groups = await Promise.all(
    (data || []).map(async (g) => {
      const { count } = await supabase
        .from('group_members')
        .select('*', { count: 'exact', head: true })
        .eq('group_id', g.id);

      const { data: lastMsg } = await supabase
        .from('messages')
        .select('content, created_at')
        .eq('group_id', g.id)
        .order('created_at', { ascending: false })
        .limit(1)
        .maybeSingle();

      return mapGroup(g, count || 0, lastMsg);
    })
  );

  return groups;
}

/**
 * Create a new group (admin).
 */
export async function createGroup(name, description, createdBy) {
  const joinCode = generateJoinCode();

  const { data, error } = await supabase
    .from('groups')
    .insert({
      name,
      description: description || null,
      join_code: joinCode,
      created_by: createdBy,
    })
    .select()
    .single();

  if (error) throw error;

  // Auto-add creator as member
  await supabase.from('group_members').insert({
    group_id: data.id,
    user_id: createdBy,
  });

  return mapGroup(data, 1, null);
}

/**
 * Delete a group.
 */
export async function deleteGroup(groupId) {
  const { error } = await supabase.from('groups').delete().eq('id', groupId);
  if (error) throw error;
}

/**
 * Join a group by join code.
 */
export async function joinGroup(userId, joinCode) {
  // 1. Find the group
  const { data: group, error: findError } = await supabase
    .from('groups')
    .select('id, name')
    .eq('join_code', joinCode.trim().toUpperCase())
    .single();

  if (findError || !group) {
    throw new Error('Invalid join code. Group not found.');
  }

  // 2. Check if already a member
  const { data: existing } = await supabase
    .from('group_members')
    .select('group_id')
    .eq('group_id', group.id)
    .eq('user_id', userId)
    .maybeSingle();

  if (existing) {
    throw new Error('You are already a member of this group.');
  }

  // 3. Join
  const { error } = await supabase.from('group_members').insert({
    group_id: group.id,
    user_id: userId,
  });

  if (error) throw error;
  return group;
}

/**
 * Get member count for a group.
 */
export async function fetchGroupMemberCount(groupId) {
  const { count } = await supabase
    .from('group_members')
    .select('*', { count: 'exact', head: true })
    .eq('group_id', groupId);
  return count || 0;
}

function generateJoinCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  const prefixes = ['GRP', 'STD', 'DSC'];
  const pfx = prefixes[Math.floor(Math.random() * prefixes.length)];
  let code = '';
  for (let i = 0; i < 3; i++) {
    code += chars[Math.floor(Math.random() * chars.length)];
  }
  return `${pfx}-2026-${code}`;
}

function mapGroup(g, memberCount, lastMsg) {
  return {
    id: g.id,
    name: g.name,
    description: g.description || '',
    joinCode: g.join_code,
    members: memberCount,
    createdBy: g.created_by,
    createdAt: g.created_at ? new Date(g.created_at).toISOString().split('T')[0] : '',
    lastMessage: lastMsg?.content || 'No messages yet',
    lastMessageAt: lastMsg?.created_at || g.created_at,
  };
}
