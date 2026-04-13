import api from './http'

export const getIntegrationToken = () =>
  api.get('/api/v1/integrations/token').then(r => r.data)

export const regenerateIntegrationToken = () =>
  api.post('/api/v1/integrations/token/regenerate').then(r => r.data)
