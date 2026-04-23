import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8061'

const http = axios.create({
  baseURL: BASE,
  withCredentials: true, // envia cookie aff_token automaticamente
})

export async function affiliateLogin(email, password) {
  const res = await http.post('/api/affiliate/auth/login', { email, password })
  return res.data
}

export async function affiliateLogout() {
  const res = await http.post('/api/affiliate/auth/logout')
  return res.data
}

export async function affiliateMe() {
  const res = await http.get('/api/affiliate/auth/me')
  return res.data
}

export async function affiliateDashboard(dateFrom, dateTo) {
  const params = {}
  if (dateFrom) params.date_from = dateFrom
  if (dateTo) params.date_to = dateTo
  const res = await http.get('/api/affiliate/dashboard', { params })
  return res.data
}

// Admin
export async function adminListAffiliates(token) {
  const res = await http.get('/api/affiliate/admin/affiliates', {
    headers: { Authorization: `Bearer ${token}` },
  })
  return res.data
}

export async function adminCreateAffiliate(token, data) {
  const res = await http.post('/api/affiliate/admin/affiliates', data, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return res.data
}

export async function adminUpdateAffiliate(token, id, data) {
  const res = await http.put(`/api/affiliate/admin/affiliates/${id}`, data, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return res.data
}

export async function adminDeleteAffiliate(token, id) {
  const res = await http.delete(`/api/affiliate/admin/affiliates/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return res.data
}

export async function adminAffiliateStats(token, id) {
  const res = await http.get(`/api/affiliate/admin/affiliates/${id}/stats`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return res.data
}
