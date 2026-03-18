import api from './http.js'

// ─── Workspaces ───────────────────────────────────────────────────────────────

export async function listWorkspaces () {
  const res = await api.get('/api/v1/workspaces/')
  return res.data
}

export async function createWorkspace (name) {
  const res = await api.post('/api/v1/workspaces/', { name })
  return res.data
}

export async function updateWorkspace (id, name) {
  const res = await api.put(`/api/v1/workspaces/${id}`, { name })
  return res.data
}

export async function switchWorkspace (id) {
  const res = await api.post(`/api/v1/workspaces/${id}/switch`)
  return res.data
}

// ─── Members ──────────────────────────────────────────────────────────────────

export async function listMembers (workspaceId) {
  const res = await api.get(`/api/v1/workspaces/${workspaceId}/members`)
  return res.data
}

export async function inviteMember (workspaceId, email, role = 'member', permissions = null) {
  const payload = { email, role }
  if (permissions !== null) payload.permissions = permissions
  const res = await api.post(`/api/v1/workspaces/${workspaceId}/members`, payload)
  return res.data
}

export async function updateMemberRole (workspaceId, userId, role) {
  const res = await api.put(`/api/v1/workspaces/${workspaceId}/members/${userId}`, { role })
  return res.data
}

export async function updateMemberPermissions (workspaceId, userId, permissions) {
  const res = await api.put(`/api/v1/workspaces/${workspaceId}/members/${userId}/permissions`, { permissions })
  return res.data
}

export async function removeMember (workspaceId, userId) {
  const res = await api.delete(`/api/v1/workspaces/${workspaceId}/members/${userId}`)
  return res.data
}

// ─── Permissions ──────────────────────────────────────────────────────────────

export async function getAvailablePermissions () {
  const res = await api.get('/api/v1/workspaces/permissions/available')
  return res.data
}
