import api from './http'

export const getIntegrationToken = () =>
  api.get('/api/v1/integrations/token').then(r => r.data)

export const regenerateIntegrationToken = () =>
  api.post('/api/v1/integrations/token/regenerate').then(r => r.data)

export const getTrackingAutomations = () =>
  api.get('/api/v1/integrations/automations').then(r => r.data)

export const saveTrackingAutomation = (payload) =>
  api.put('/api/v1/integrations/automations', payload).then(r => r.data)
