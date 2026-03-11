import api from './http'

export async function listChannels() {
  // incluir inativos por padrão para que bot desativado também apareça
  const res = await api.get('/api/v1/channels/', {
    params: { include_inactive: true }
  })
  return res.data
}

export async function createChannel(payload) {
  const res = await api.post('/api/v1/channels/', payload)
  return res.data
}

export async function updateChannel(channelId, payload) {
  const res = await api.put(`/api/v1/channels/${channelId}`, payload)
  return res.data
}

export async function updateTelegramConfig(channelId, payload) {
  const res = await api.put(`/api/v1/channels/${channelId}/telegram-config`, payload)
  return res.data
}

export async function deleteChannel(channelId) {
  const res = await api.delete(`/api/v1/channels/${channelId}`)
  return res.data
}

