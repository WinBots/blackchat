import api from './http'

/**
 * Gera um fluxo completo a partir de um prompt usando IA (Claude)
 * @param {string} prompt - Descrição em linguagem natural do fluxo desejado
 * @returns {Promise<{ name, description, trigger_type, steps, connections, node_positions }>}
 */
export async function generateFlowWithAI(prompt) {
  const res = await api.post('/api/v1/flows/ai-generate', { prompt })
  return res.data
}
