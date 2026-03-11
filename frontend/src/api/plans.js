import api from './http'

export async function listPlans() {
  const res = await api.get('/api/v1/plans/')
  return res.data
}
