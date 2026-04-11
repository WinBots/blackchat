/**
 * Store global para progresso de disparo em massa.
 * Persiste entre navegações pois fica fora do componente.
 */
import { ref, computed } from 'vue'
import api from '@/api/http'

const job = ref(null)   // { job_id, total, sent, failed, status, flow_name }
let _pollTimer = null

export function useBroadcastProgress() {

  const isRunning = computed(() =>
    job.value && (job.value.status === 'queued' || job.value.status === 'running')
  )

  const isDone = computed(() =>
    job.value && (job.value.status === 'done' || job.value.status === 'error')
  )

  const percent = computed(() => {
    if (!job.value || !job.value.total) return 0
    const done = (job.value.sent || 0) + (job.value.failed || 0)
    return Math.min(100, Math.round((done / job.value.total) * 100))
  })

  function startTracking(jobId, total, flowName) {
    job.value = {
      job_id: jobId,
      total,
      sent: 0,
      failed: 0,
      status: 'queued',
      flow_name: flowName || 'Disparo em massa',
    }
    _schedulePoll()
  }

  function _schedulePoll() {
    if (_pollTimer) clearTimeout(_pollTimer)
    _pollTimer = setTimeout(_poll, 2000)
  }

  async function _poll() {
    if (!job.value?.job_id) return
    try {
      const res = await api.get(`/api/v1/contacts/jobs/${job.value.job_id}`)
      const data = res.data
      job.value = {
        ...job.value,
        sent: data.sent ?? data.started ?? 0,
        failed: data.failed ?? 0,
        status: data.status ?? 'running',
      }
      if (job.value.status === 'running' || job.value.status === 'queued') {
        _schedulePoll()
      }
    } catch {
      // Job pode não ter iniciado ainda — tenta de novo
      _schedulePoll()
    }
  }

  function dismiss() {
    if (_pollTimer) clearTimeout(_pollTimer)
    job.value = null
  }

  return { job, isRunning, isDone, percent, startTracking, dismiss }
}
