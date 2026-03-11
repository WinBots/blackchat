import api from './http'

/**
 * Lista todos os contatos
 * @param {Object} params - Parâmetros de filtro
 * @param {string} params.search - Busca por nome ou username
 * @param {number} params.channel_id - Filtrar por canal
 * @param {number} params.limit - Limite de resultados
 * @param {number} params.offset - Offset para paginação
 * @returns {Promise<{items: Array, total: number, limit: number, offset: number}>}
 */
export async function listContacts(params = {}) {
  const res = await api.get('/api/v1/contacts/', { params })
  return res.data
}

/**
 * Estatísticas para a sidebar de contatos
 * @returns {Promise<{contacts_total: number, by_channel: Array, by_tag: Array}>}
 */
export async function getContactsStats() {
  const res = await api.get('/api/v1/contacts/stats')
  return res.data
}

/**
 * Estatísticas de campos customizados (pares campo/valor) para filtros rápidos
 * @param {Object} params
 * @param {number=} params.limit - Limite de pares retornados
 * @returns {Promise<Array<{field: string, value: any, count: number}>>}
 */
export async function getContactsFieldStats(params = {}) {
  const res = await api.get('/api/v1/contacts/field-stats', { params })
  return res.data
}

/**
 * Adiciona tag a um contato
 * @param {number} contactId
 * @param {string} tagName
 * @returns {Promise<Object>}
 */
export async function addContactTag(contactId, tagName) {
  const res = await api.post(`/api/v1/contacts/${contactId}/tags`, { tag_name: tagName })
  return res.data
}

/**
 * Remove tag de um contato
 * @param {number} contactId
 * @param {string} tagName
 * @returns {Promise<Object>}
 */
export async function removeContactTag(contactId, tagName) {
  const encoded = encodeURIComponent(tagName)
  const res = await api.delete(`/api/v1/contacts/${contactId}/tags/${encoded}`)
  return res.data
}

/**
 * Obtém detalhes de um contato
 * @param {number} contactId - ID do contato
 * @returns {Promise<Object>}
 */
export async function getContact(contactId) {
  const res = await api.get(`/api/v1/contacts/${contactId}`)
  return res.data
}

/**
 * Deleta um contato (lead) permanentemente
 * @param {number} contactId
 * @returns {Promise<{deleted: boolean, contact_id: number}>}
 */
export async function deleteContact(contactId) {
  const res = await api.delete(`/api/v1/contacts/${contactId}`)
  return res.data
}

/**
 * Lista mensagens de um contato
 * @param {number} contactId - ID do contato
 * @param {Object} params - Parâmetros de filtro
 * @param {number} params.limit - Limite de resultados
 * @param {number} params.offset - Offset para paginação
 * @returns {Promise<Array>}
 */
export async function getContactMessages(contactId, params = {}) {
  const res = await api.get(`/api/v1/contacts/${contactId}/messages`, { params })
  return res.data
}

/**
 * Envia uma mensagem de texto diretamente a um contato
 * @param {number} contactId
 * @param {string} text
 * @returns {Promise<Object>}
 */
export async function sendMessageToContact(contactId, text, options = {}) {
  const { parse_mode = 'MarkdownV2' } = options
  const res = await api.post(`/api/v1/contacts/${contactId}/send-message`, { text, parse_mode })
  return res.data
}

/**
 * Envia uma mídia (foto, vídeo, áudio, vídeo nota circular) a um contato via upload
 * @param {number} contactId
 * @param {File} file - Arquivo a enviar
 * @param {string} mediaType - 'photo' | 'video' | 'video_note' | 'audio' | 'auto'
 * @returns {Promise<Object>}
 */
export async function sendMediaToContact(contactId, file, mediaType = 'auto') {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('media_type', mediaType)
  const res = await api.post(`/api/v1/contacts/${contactId}/send-media`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return res.data
}

/**
 * Inicia um fluxo para um contato específico
 * @param {number} contactId - ID do contato
 * @param {number} flowId - ID do fluxo
 * @returns {Promise<Object>}
 */
export async function startFlowForContact(contactId, flowId) {
  const res = await api.post(`/api/v1/contacts/${contactId}/start-flow/${flowId}`)
  return res.data
}

/**
 * Busca o histórico de fluxos executados para um contato
 * @param {number} contactId - ID do contato
 * @returns {Promise<Array>}
 */
export async function getContactFlowHistory(contactId) {
  const res = await api.get(`/api/v1/contacts/${contactId}/flow-history`)
  return res.data
}

/**
 * Pré-visualiza um disparo de mensagem em massa (retorna apenas quantidade e amostra)
 * @param {Object} payload - Filtros + texto
 * @returns {Promise<{total: number, sample: Array}>}
 */
export async function previewBulkMessage(payload) {
  const res = await api.post('/api/v1/contacts/bulk-start-flow', {
    ...payload,
    dry_run: true
  })
  return res.data
}

/**
 * Inicia um fluxo em massa para um segmento de contatos
 * @param {Object} payload - Filtros + flow_id
 * @returns {Promise<{total: number, started: number, failed: number, errors: Array}>}
 */
export async function sendBulkMessage(payload) {
  const res = await api.post('/api/v1/contacts/bulk-start-flow', {
    ...payload,
    dry_run: false
  })
  return res.data
}

/**
 * Mescla contatos duplicados do Telegram (mesmo telegram_user_id)
 * @param {Object} payload
 * @param {number} payload.channel_id
 * @param {number} payload.telegram_user_id
 * @param {number=} payload.keep_contact_id
 * @param {boolean=} payload.dry_run
 */
export async function mergeTelegramContactDuplicates(payload) {
  const res = await api.post('/api/v1/debug/telegram/merge-duplicates', payload)
  return res.data
}

