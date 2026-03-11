import api from './http'

export async function createCheckoutSession(planId, interval = 'monthly') {
  const res = await api.post('/api/v1/billing/checkout-session', { plan_id: planId, interval })
  return res.data
}

export async function createEnterpriseCheckoutSession(contactCount) {
  const res = await api.post('/api/v1/billing/enterprise-checkout', { contact_count: contactCount })
  return res.data
}

export async function createPortalSession() {
  const res = await api.post('/api/v1/billing/portal-session')
  return res.data
}

export async function getBillingStatus() {
  const res = await api.get('/api/v1/billing/status')
  return res.data
}

/**
 * Retorna estimativa VPM do tenant: contatos ativos, blocos, valor calculado e se mínimo foi aplicado.
 * Retorna null se o plano é Free (sem VPM).
 */
export async function getVpmEstimate() {
  const res = await api.get('/api/v1/billing/vpm-estimate')
  return res.data
}
