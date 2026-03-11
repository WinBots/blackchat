import api from './http'

export async function listFlows() {
  const res = await api.get('/api/v1/flows/')
  return res.data
}

export async function getFlow(id) {
  const res = await api.get(`/api/v1/flows/${id}`)
  return res.data
}

export async function createFlow(payload) {
  const res = await api.post('/api/v1/flows/', payload)
  return res.data
}

export async function listFlowSteps(flowId) {
  const res = await api.get(`/api/v1/flows/${flowId}/steps`)
  return res.data
}

export async function createFlowStep(flowId, payload) {
  const res = await api.post(`/api/v1/flows/${flowId}/steps`, payload)
  return res.data
}

export async function updateFlow(flowId, payload) {
  const res = await api.put(`/api/v1/flows/${flowId}`, payload)
  return res.data
}

export async function updateFlowStep(flowId, stepId, payload) {
  const res = await api.put(`/api/v1/flows/${flowId}/steps/${stepId}`, payload)
  return res.data
}

export async function deleteFlowStep(flowId, stepId) {
  const res = await api.delete(`/api/v1/flows/${flowId}/steps/${stepId}`)
  return res.data
}

export async function deleteFlow(flowId) {
  const res = await api.delete(`/api/v1/flows/${flowId}`)
  return res.data
}

export async function runFlowDemo(flowId) {
  const res = await api.post(`/api/v1/flows/${flowId}/run-demo`)
  return res.data
}
