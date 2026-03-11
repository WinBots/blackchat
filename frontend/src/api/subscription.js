import api from './http'

export async function getMySubscription() {
  const res = await api.get('/api/v1/subscription/me')
  return res.data
}
