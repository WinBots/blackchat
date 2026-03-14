import api from './http'

export async function getStripeConfig() {
  const res = await api.get('/api/v1/admin/stripe-config')
  return res.data
}

export async function updateStripeConfig(payload) {
  const res = await api.put('/api/v1/admin/stripe-config', payload)
  return res.data
}

export async function setStripeMode(mode) {
  const res = await api.put('/api/v1/admin/stripe-config/mode', { mode })
  return res.data
}
