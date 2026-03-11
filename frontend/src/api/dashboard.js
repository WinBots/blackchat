import api from './http'

export const getDashboardMetrics = async ({ limit = 20 } = {}) => {
  const res = await api.get('/api/v1/dashboard/metrics', {
    params: { limit }
  })
  return res.data
}
