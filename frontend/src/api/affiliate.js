import api from './http'

export async function affiliateLogin(email, password) {
  const res = await api.post('/api/affiliate/auth/login', { email, password })
  return res.data
}

export async function affiliateLogout() {
  const res = await api.post('/api/affiliate/auth/logout')
  return res.data
}

export async function affiliateMe() {
  const res = await api.get('/api/affiliate/auth/me')
  return res.data
}

export async function affiliateDashboard(dateFrom, dateTo) {
  const params = {}
  if (dateFrom) params.date_from = dateFrom
  if (dateTo) params.date_to = dateTo
  const res = await api.get('/api/affiliate/dashboard', { params })
  return res.data
}

// Admin
export async function adminListAffiliates() {
  const res = await api.get('/api/affiliate/admin/affiliates')
  return res.data
}

export async function adminCreateAffiliate(data) {
  const res = await api.post('/api/affiliate/admin/affiliates', data)
  return res.data
}

export async function adminUpdateAffiliate(id, data) {
  const res = await api.put(`/api/affiliate/admin/affiliates/${id}`, data)
  return res.data
}

export async function adminDeleteAffiliate(id) {
  const res = await api.delete(`/api/affiliate/admin/affiliates/${id}`)
  return res.data
}

export async function adminAffiliateStats(id) {
  const res = await api.get(`/api/affiliate/admin/affiliates/${id}/stats`)
  return res.data
}
