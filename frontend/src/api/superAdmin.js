import api from './http'

export async function adminListTenants() {
  const res = await api.get('/api/v1/admin/tenants')
  return res.data
}

export async function adminUpdateTenant(tenantId, payload) {
  const res = await api.put(`/api/v1/admin/tenants/${tenantId}`, payload)
  return res.data
}

export async function adminUpdateTenantSubscription(tenantId, payload) {
  const res = await api.put(`/api/v1/admin/tenants/${tenantId}/subscription`, payload)
  return res.data
}

export async function adminListUsers() {
  const res = await api.get('/api/v1/admin/users')
  return res.data
}

export async function adminUpdateUser(userId, payload) {
  const res = await api.put(`/api/v1/admin/users/${userId}`, payload)
  return res.data
}

export async function adminListPlans() {
  const res = await api.get('/api/v1/admin/plans')
  return res.data
}

export async function adminUpdatePlan(planId, payload) {
  const res = await api.put(`/api/v1/admin/plans/${planId}`, payload)
  return res.data
}
