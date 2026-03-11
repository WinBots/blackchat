import api from './http'

/**
 * Obtém a URL de autenticação OAuth do Instagram
 */
export async function getInstagramAuthUrl() {
  const res = await api.get('/api/v1/instagram/auth-url')
  return res.data
}

/**
 * Finaliza o OAuth do Instagram e retorna as contas disponíveis
 * @param {string} code - Código de autorização retornado pelo Facebook
 * @param {string} state - State (tenant_id) para validação
 */
export async function finishInstagramAuth(code, state) {
  const res = await api.get('/api/v1/instagram/callback', {
    params: { code, state }
  })
  return res.data
}

/**
 * Conecta uma conta Instagram Business ao tenant
 * @param {Object} payload - Dados da conta Instagram
 * @param {string} payload.page_id - ID da página do Facebook
 * @param {string} payload.page_name - Nome da página
 * @param {string} payload.page_access_token - Token de acesso da página
 * @param {string} payload.ig_user_id - ID do usuário Instagram Business
 * @param {string} payload.ig_username - Username do Instagram
 */
export async function connectInstagram(payload) {
  const res = await api.post('/api/v1/instagram/connect', payload)
  return res.data
}

/**
 * Lista todas as contas Instagram conectadas
 */
export async function listInstagramAccounts() {
  const res = await api.get('/api/v1/instagram/accounts')
  return res.data
}

/**
 * Desconecta uma conta Instagram
 * @param {number} channelId - ID do canal
 */
export async function disconnectInstagram(channelId) {
  const res = await api.delete(`/api/v1/channels/${channelId}`)
  return res.data
}
