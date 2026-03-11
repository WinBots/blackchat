import api from './http'

export async function getTenantMe() {
  const res = await api.get('/api/v1/tenants/me')
  return res.data
}

export async function updateTenantMe(payload) {
  const res = await api.put('/api/v1/tenants/me', payload)
  return res.data
}
