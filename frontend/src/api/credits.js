import api from './http'

export const getCreditsBalance = () =>
  api.get('/api/v1/credits/balance').then(r => r.data)

export const purchaseCredits = (amount) =>
  api.post('/api/v1/credits/purchase', { amount }).then(r => r.data)
