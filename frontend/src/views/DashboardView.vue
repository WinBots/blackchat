<template>
  <AppLayout>
    <!-- Stats Cards -->
    <div class="grid grid-3 dashboard-stats-grid">
      <div class="card card-interactive">
        <div class="stats-card">
          <div class="stats-label">Total de Contatos</div>
          <div v-if="loading" class="dash-skel dash-skel-value"></div>
          <div v-else class="stats-value">{{ fmtInt(metrics?.contacts_total) }}</div>
          <div class="stats-change" :class="metrics?.contacts_last_24h ? 'positive' : ''">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
              <polyline points="17 6 23 6 23 12"/>
            </svg>
            <span v-if="loading" class="dash-skel dash-skel-line"></span>
            <span v-else>+{{ fmtInt(metrics?.contacts_last_24h) }} nas últimas 24h</span>
          </div>
        </div>
      </div>

      <div class="card card-interactive">
        <div class="stats-card">
          <div class="stats-label">Fluxos Ativos</div>
          <div v-if="loading" class="dash-skel dash-skel-value"></div>
          <div v-else class="stats-value">{{ fmtInt(metrics?.flows_active) }}</div>
          <div class="stats-change">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
            <span v-if="loading" class="dash-skel dash-skel-line"></span>
            <span v-else>{{ fmtInt(metrics?.flow_executions_today) }} disparados hoje</span>
          </div>
        </div>
      </div>

      <div class="card card-interactive">
        <div class="stats-card">
          <div class="stats-label">Canais Conectados</div>
          <div v-if="loading" class="dash-skel dash-skel-value"></div>
          <div v-else class="stats-value">{{ fmtInt(metrics?.channels_connected) }}</div>
          <div class="stats-change">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <span v-if="loading" class="dash-skel dash-skel-line"></span>
            <span v-else>Ativos no tenant</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="card">
      <div class="page-header">
        <div>
          <h2 class="page-title">Atividade Recente</h2>
          <p class="page-description">Últimas interações e eventos do sistema</p>
        </div>
        <button class="btn btn-ghost btn-sm" type="button" @click="load" :disabled="loading">Atualizar</button>
      </div>

      <div v-if="error" style="padding: 12px 0; color: #ef4444;">
        {{ error }}
      </div>

      <div class="table-wrapper">
        <table class="table">
          <thead>
            <tr>
              <th>Contato</th>
              <th>Canal</th>
              <th>Evento</th>
              <th>Data</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <template v-if="loading">
              <tr v-for="n in 5" :key="n">
                <td><div class="dash-skel dash-skel-cell" style="width:120px"></div></td>
                <td><div class="dash-skel dash-skel-cell" style="width:70px"></div></td>
                <td><div class="dash-skel dash-skel-cell" style="width:100px"></div></td>
                <td><div class="dash-skel dash-skel-cell" style="width:60px"></div></td>
                <td><div class="dash-skel dash-skel-cell" style="width:60px"></div></td>
              </tr>
            </template>
            <tr v-else-if="recentActivity.length === 0">
              <td colspan="5" style="color: var(--muted); padding: 18px;">Sem atividade recente.</td>
            </tr>
            <tr v-else v-for="activity in recentActivity" :key="activity.id">
              <td>
                <div style="display: flex; align-items: center; gap: 10px;">
                  <div style="width: 32px; height: 32px; border-radius: 50%; background: var(--accent-soft); display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 0.75rem; color: var(--accent);">
                    {{ activity.initials }}
                  </div>
                  <div>
                    <div style="font-weight: 500; color: var(--text-primary);">{{ activity.name }}</div>
                    <div style="font-size: 0.75rem; color: var(--muted);">{{ activity.username }}</div>
                  </div>
                </div>
              </td>
              <td>
                <span class="badge" :class="channelBadge(activity.channel_type)">
                  {{ activity.channel }}
                </span>
              </td>
              <td>{{ activity.event }}</td>
              <td style="color: var(--muted);">{{ timeAgo(activity.created_at) }}</td>
              <td>
                <span class="badge" :class="statusBadge(activity)">
                  {{ activity.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-3 dashboard-actions-grid">
      <div class="card card-interactive" style="cursor: pointer;" @click="navigateTo('/flows')">
        <div style="display: flex; align-items: center; gap: 16px;">
          <div style="width: 48px; height: 48px; border-radius: var(--radius-md); background: var(--accent-soft); display: flex; align-items: center; justify-content: center; color: var(--accent);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
          </div>
          <div>
            <div class="card-title">Criar Fluxo</div>
            <div class="card-description">Novo fluxo de automação</div>
          </div>
        </div>
      </div>

      <div class="card card-interactive" style="cursor: pointer;" @click="navigateTo('/channels')">
        <div style="display: flex; align-items: center; gap: 16px;">
          <div style="width: 48px; height: 48px; border-radius: var(--radius-md); background: rgba(14, 165, 233, 0.15); display: flex; align-items: center; justify-content: center; color: #0ea5e9;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <div>
            <div class="card-title">Adicionar Canal</div>
            <div class="card-description">Conectar novo canal</div>
          </div>
        </div>
      </div>

      <div class="card card-interactive" style="cursor: pointer;" @click="navigateTo('/contacts')">
        <div style="display: flex; align-items: center; gap: 16px;">
          <div style="width: 48px; height: 48px; border-radius: var(--radius-md); background: rgba(251, 191, 36, 0.15); display: flex; align-items: center; justify-content: center; color: #fbbf24;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <div>
            <div class="card-title">Ver Contatos</div>
            <div class="card-description">Lista de contatos</div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { getDashboardMetrics } from '@/api/dashboard'

const router = useRouter()

const loading = ref(true)
const error = ref('')
const metrics = ref(null)
const recentActivity = ref([])

const fmtInt = (n) => {
  const v = typeof n === 'number' && Number.isFinite(n) ? n : 0
  return new Intl.NumberFormat('pt-BR').format(v)
}

const channelBadge = (channelType) => {
  const t = (channelType || '').toLowerCase()
  return 'badge-muted' // telegram/default
}

const statusBadge = (activity) => {
  const dir = (activity?.direction || '').toLowerCase()
  const st = (activity?.status || '').toLowerCase()

  // inbound: consider "Recebida" ok
  if (dir === 'inbound') return 'badge-success'

  // outbound: map common statuses
  if (st.includes('fail') || st.includes('erro')) return 'badge-danger'
  if (st.includes('sent') || st.includes('envi')) return 'badge-success'
  return 'badge-muted'
}

const timeAgo = (iso) => {
  if (!iso) return ''
  const dt = new Date(iso)
  if (Number.isNaN(dt.getTime())) return ''
  const diffMs = Date.now() - dt.getTime()
  const diffSec = Math.max(0, Math.floor(diffMs / 1000))
  if (diffSec < 60) return 'agora'
  const diffMin = Math.floor(diffSec / 60)
  if (diffMin < 60) return `há ${diffMin} min`
  const diffHr = Math.floor(diffMin / 60)
  if (diffHr < 24) return `há ${diffHr} h`
  const diffDay = Math.floor(diffHr / 24)
  return `há ${diffDay} d`
}

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await getDashboardMetrics({ limit: 20 })
    metrics.value = data
    recentActivity.value = data?.recent_activity || []
  } catch (e) {
    error.value = 'Não foi possível carregar a dashboard.'
  } finally {
    loading.value = false
  }
}

const navigateTo = (path) => {
  router.push(path)
}

onMounted(() => {
  load()
})
</script>

<style scoped>
/* ─── Dashboard skeleton shimmer ─────────────────────────── */
@keyframes dash-shimmer {
  0%   { background-position: -400px 0; }
  100% { background-position:  400px 0; }
}

.dash-skel {
  background: linear-gradient(90deg, var(--bg-secondary, #1a1a1a) 25%, var(--border, #2a2a2a) 50%, var(--bg-secondary, #1a1a1a) 75%);
  background-size: 800px 100%;
  animation: dash-shimmer 1.4s infinite linear;
  border-radius: 6px;
  display: inline-block;
}

.dash-skel-value {
  width: 80px;
  height: 38px;
  border-radius: 6px;
  margin: 4px 0;
}

.dash-skel-line {
  width: 160px;
  height: 13px;
  border-radius: 4px;
  vertical-align: middle;
}

.dash-skel-cell {
  height: 16px;
  border-radius: 4px;
  display: block;
}
</style>
