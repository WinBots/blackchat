<template>
  <AppLayout>
    <div class="db-root">

      <!-- ─── Greeting ──────────────────────────────────────── -->
      <div class="db-greeting">
        <div class="db-greeting-text">
          <h1 class="db-greeting-title">{{ greeting }}, {{ firstName }}</h1>
          <p class="db-greeting-sub">{{ todayLabel }} · {{ tenantName }}</p>
        </div>
        <button class="btn btn-ghost btn-sm db-refresh" @click="load" :disabled="loading">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="23 4 23 10 17 10"/>
            <polyline points="1 20 1 14 7 14"/>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
          </svg>
          Atualizar
        </button>
      </div>

      <!-- ─── KPI Cards ─────────────────────────────────────── -->
      <div class="db-kpis">
        <!-- Contatos -->
        <div class="db-kpi-card">
          <div class="db-kpi-icon db-kpi-icon--contacts">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <div class="db-kpi-body">
            <span class="db-kpi-label">Total de Contatos</span>
            <div v-if="loading" class="dash-skel dash-skel-value"></div>
            <span v-else class="db-kpi-value">{{ fmtInt(metrics?.contacts_total) }}</span>
            <div class="db-kpi-delta" :class="metrics?.contacts_last_24h ? 'db-kpi-delta--up' : ''">
              <template v-if="loading"><span class="dash-skel dash-skel-line"></span></template>
              <template v-else>
                <svg v-if="metrics?.contacts_last_24h" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="18 15 12 9 6 15"/></svg>
                +{{ fmtInt(metrics?.contacts_last_24h) }} nas últimas 24h
              </template>
            </div>
          </div>
        </div>

        <!-- Fluxos Ativos -->
        <div class="db-kpi-card">
          <div class="db-kpi-icon db-kpi-icon--flows">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
          </div>
          <div class="db-kpi-body">
            <span class="db-kpi-label">Fluxos Ativos</span>
            <div v-if="loading" class="dash-skel dash-skel-value"></div>
            <span v-else class="db-kpi-value">{{ fmtInt(metrics?.flows_active) }}</span>
            <div class="db-kpi-delta">
              <template v-if="loading"><span class="dash-skel dash-skel-line"></span></template>
              <template v-else>em operação agora</template>
            </div>
          </div>
        </div>

        <!-- Execuções Hoje -->
        <div class="db-kpi-card">
          <div class="db-kpi-icon db-kpi-icon--exec">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
          <div class="db-kpi-body">
            <span class="db-kpi-label">Execuções Hoje</span>
            <div v-if="loading" class="dash-skel dash-skel-value"></div>
            <span v-else class="db-kpi-value">{{ fmtInt(metrics?.flow_executions_today) }}</span>
            <div class="db-kpi-delta">
              <template v-if="loading"><span class="dash-skel dash-skel-line"></span></template>
              <template v-else>disparos automáticos</template>
            </div>
          </div>
        </div>

        <!-- Canais Conectados -->
        <div class="db-kpi-card">
          <div class="db-kpi-icon db-kpi-icon--channels">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <div class="db-kpi-body">
            <span class="db-kpi-label">Canais Conectados</span>
            <div v-if="loading" class="dash-skel dash-skel-value"></div>
            <span v-else class="db-kpi-value">{{ fmtInt(metrics?.channels_connected) }}</span>
            <div class="db-kpi-delta">
              <template v-if="loading"><span class="dash-skel dash-skel-line"></span></template>
              <template v-else>ativos no workspace</template>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── Main Grid ──────────────────────────────────────── -->
      <div class="db-main-grid">

        <!-- ─── Atividade Recente ─────────────────────────────── -->
        <div class="card db-activity-card">
          <div class="db-section-header">
            <div>
              <h2 class="db-section-title">Atividade Recente</h2>
              <p class="db-section-sub">Últimas interações e eventos</p>
            </div>
          </div>

          <div v-if="error" class="db-error">{{ error }}</div>

          <!-- Skeleton -->
          <template v-if="loading">
            <div v-for="n in 6" :key="n" class="db-activity-item db-activity-item--skeleton">
              <div class="dash-skel db-skel-avatar"></div>
              <div class="db-activity-info">
                <span class="dash-skel dash-skel-line" style="width: 110px;"></span>
                <span class="dash-skel dash-skel-line" style="width: 70px; margin-top: 6px;"></span>
              </div>
              <div class="dash-skel dash-skel-line" style="width: 60px; margin-left: auto;"></div>
            </div>
          </template>

          <!-- Empty -->
          <div v-else-if="recentActivity.length === 0" class="db-empty">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <p>Sem atividade recente</p>
          </div>

          <!-- Items -->
          <div
            v-else
            v-for="activity in pagedActivity"
            :key="activity.id"
            class="db-activity-item"
          >
            <div class="db-activity-avatar">{{ activity.initials }}</div>
            <div class="db-activity-info">
              <div class="db-activity-name">{{ activity.name }}</div>
              <div class="db-activity-meta">
                <span class="db-badge" :class="channelBadgeClass(activity.channel_type)">{{ activity.channel }}</span>
                <span class="db-activity-event">{{ activity.event }}</span>
              </div>
            </div>
            <div class="db-activity-right">
              <span class="db-badge" :class="statusBadgeClass(activity)">{{ activity.status }}</span>
              <span class="db-activity-time">{{ timeAgo(activity.created_at) }}</span>
            </div>
          </div>

          <!-- Paginação -->
          <div v-if="!loading && totalPages > 1" class="db-pagination">
            <button
              class="db-page-btn"
              :disabled="currentPage === 1"
              @click="currentPage--"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
            </button>
            <span class="db-page-info">{{ currentPage }} / {{ totalPages }}</span>
            <button
              class="db-page-btn"
              :disabled="currentPage === totalPages"
              @click="currentPage++"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- ─── Sidebar Direito ────────────────────────────────── -->
        <div class="db-sidebar-col">

          <!-- Ações Rápidas -->
          <div class="card db-quick-card">
            <div class="db-section-header">
              <h2 class="db-section-title">Ações Rápidas</h2>
            </div>
            <div class="db-quick-actions">
              <button class="db-quick-btn" @click="navigateTo('/flows')">
                <div class="db-quick-icon db-quick-icon--flows">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                  </svg>
                </div>
                <div class="db-quick-text">
                  <span class="db-quick-label">Criar Automação</span>
                  <span class="db-quick-desc">Novo fluxo de respostas</span>
                </div>
                <svg class="db-quick-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </button>

              <button class="db-quick-btn" @click="navigateTo('/channels')">
                <div class="db-quick-icon db-quick-icon--channels">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                  </svg>
                </div>
                <div class="db-quick-text">
                  <span class="db-quick-label">Adicionar Canal</span>
                  <span class="db-quick-desc">Conectar novo bot</span>
                </div>
                <svg class="db-quick-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </button>

              <button class="db-quick-btn" @click="navigateTo('/contacts')">
                <div class="db-quick-icon db-quick-icon--contacts">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                </div>
                <div class="db-quick-text">
                  <span class="db-quick-label">Ver Contatos</span>
                  <span class="db-quick-desc">Lista e segmentos</span>
                </div>
                <svg class="db-quick-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </button>

              <button class="db-quick-btn" @click="navigateTo('/broadcasts')">
                <div class="db-quick-icon db-quick-icon--broadcast">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 4h16v4H4z"/>
                    <path d="M4 10h10v4H4z"/>
                    <path d="M4 16h7v4H4z"/>
                    <polyline points="18 10 22 12 18 14"/>
                  </svg>
                </div>
                <div class="db-quick-text">
                  <span class="db-quick-label">Disparar Mensagem</span>
                  <span class="db-quick-desc">Mensagem em massa</span>
                </div>
                <svg class="db-quick-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Status do Sistema -->
          <div class="card db-status-card">
            <div class="db-section-header">
              <h2 class="db-section-title">Status</h2>
            </div>
            <div class="db-status-list">
              <div class="db-status-item">
                <span class="db-status-dot db-status-dot--ok"></span>
                <span class="db-status-label">Plataforma</span>
                <span class="db-status-val">Operacional</span>
              </div>
              <div class="db-status-item">
                <span class="db-status-dot" :class="metrics?.channels_connected ? 'db-status-dot--ok' : 'db-status-dot--warn'"></span>
                <span class="db-status-label">Canais</span>
                <span class="db-status-val">
                  <template v-if="loading"><span class="dash-skel dash-skel-line" style="width:40px"></span></template>
                  <template v-else>{{ metrics?.channels_connected || 0 }} ativo{{ metrics?.channels_connected !== 1 ? 's' : '' }}</template>
                </span>
              </div>
              <div class="db-status-item">
                <span class="db-status-dot" :class="metrics?.flows_active ? 'db-status-dot--ok' : 'db-status-dot--warn'"></span>
                <span class="db-status-label">Automações</span>
                <span class="db-status-val">
                  <template v-if="loading"><span class="dash-skel dash-skel-line" style="width:40px"></span></template>
                  <template v-else>{{ metrics?.flows_active || 0 }} ativ{{ metrics?.flows_active !== 1 ? 'as' : 'a' }}</template>
                </span>
              </div>
            </div>
          </div>

        </div>
      </div>

    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { getDashboardMetrics } from '@/api/dashboard'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const auth = useAuth()

const loading = ref(true)
const error = ref('')
const metrics = ref(null)
const recentActivity = ref([])

// ── Greeting ──────────────────────────────────────────────
const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Bom dia'
  if (h < 18) return 'Boa tarde'
  return 'Boa noite'
})

const firstName = computed(() => {
  const name = auth.user.value?.full_name || auth.user.value?.email || 'Usuário'
  return name.split(' ')[0]
})

const tenantName = computed(() => auth.tenant.value?.name || 'Workspace')

const todayLabel = computed(() => {
  return new Date().toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })
})

// ── Formatters ────────────────────────────────────────────
const fmtInt = (n) => {
  const v = typeof n === 'number' && Number.isFinite(n) ? n : 0
  return new Intl.NumberFormat('pt-BR').format(v)
}

const channelBadgeClass = (channelType) => {
  const t = (channelType || '').toLowerCase()
  if (t === 'telegram') return 'db-badge--telegram'
  return 'db-badge--muted'
}

const statusBadgeClass = (activity) => {
  const dir = (activity?.direction || '').toLowerCase()
  const st = (activity?.status || '').toLowerCase()
  if (dir === 'inbound') return 'db-badge--success'
  if (st.includes('fail') || st.includes('erro')) return 'db-badge--danger'
  if (st.includes('sent') || st.includes('envi')) return 'db-badge--success'
  return 'db-badge--muted'
}

const timeAgo = (iso) => {
  if (!iso) return ''
  const dt = new Date(iso)
  if (Number.isNaN(dt.getTime())) return ''
  const diffSec = Math.max(0, Math.floor((Date.now() - dt.getTime()) / 1000))
  if (diffSec < 60) return 'agora'
  const diffMin = Math.floor(diffSec / 60)
  if (diffMin < 60) return `${diffMin}min`
  const diffHr = Math.floor(diffMin / 60)
  if (diffHr < 24) return `${diffHr}h`
  return `${Math.floor(diffHr / 24)}d`
}

// ── Paginação ─────────────────────────────────────────────
const PAGE_SIZE = 8
const currentPage = ref(1)

const totalPages = computed(() =>
  Math.max(1, Math.ceil(recentActivity.value.length / PAGE_SIZE))
)

const pagedActivity = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return recentActivity.value.slice(start, start + PAGE_SIZE)
})

// Volta para página 1 ao recarregar dados
watch(recentActivity, () => { currentPage.value = 1 })

// ── Data ──────────────────────────────────────────────────
const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await getDashboardMetrics({ limit: 20 })
    metrics.value = data
    recentActivity.value = data?.recent_activity || []
  } catch {
    error.value = 'Não foi possível carregar a dashboard.'
  } finally {
    loading.value = false
  }
}

const navigateTo = (path) => router.push(path)

onMounted(load)
</script>

<style scoped>
/* ─── Root ────────────────────────────────────────────────── */
.db-root {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ─── Skeleton shimmer ───────────────────────────────────── */
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
.dash-skel-value { width: 72px; height: 34px; border-radius: 6px; }
.dash-skel-line  { width: 120px; height: 12px; border-radius: 4px; vertical-align: middle; }

/* ─── Greeting ──────────────────────────────────────────── */
.db-greeting {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.db-greeting-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 4px;
}
.db-greeting-sub {
  font-size: 0.85rem;
  color: var(--muted);
  margin: 0;
  text-transform: capitalize;
}
.db-refresh {
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  flex-shrink: 0;
}

/* ─── KPI Cards ─────────────────────────────────────────── */
.db-kpis {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
@media (max-width: 900px) { .db-kpis { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .db-kpis { grid-template-columns: 1fr; } }

.db-kpi-card {
  background: var(--bg-card, #111);
  border: 1px solid var(--border, rgba(148,163,184,.15));
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  transition: border-color .18s, box-shadow .18s;
}
.db-kpi-card:hover {
  border-color: var(--accent, #00ff66);
  box-shadow: 0 4px 20px rgba(0,0,0,.25);
}

.db-kpi-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.db-kpi-icon--contacts  { background: rgba(0,255,102,.12); color: #00ff66; }
.db-kpi-icon--flows     { background: rgba(139,92,246,.15); color: #a78bfa; }
.db-kpi-icon--exec      { background: rgba(251,191,36,.12); color: #fbbf24; }
.db-kpi-icon--channels  { background: rgba(14,165,233,.12); color: #38bdf8; }

.db-kpi-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.db-kpi-label {
  font-size: 0.72rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: .5px;
  color: var(--muted);
}
.db-kpi-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.1;
  letter-spacing: -.5px;
}
.db-kpi-delta {
  font-size: 0.75rem;
  color: var(--muted);
  display: flex;
  align-items: center;
  gap: 3px;
  margin-top: 2px;
}
.db-kpi-delta--up { color: #4ade80; }

/* ─── Main Grid ─────────────────────────────────────────── */
.db-main-grid {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 16px;
  align-items: start;
}
@media (max-width: 900px) {
  .db-main-grid { grid-template-columns: 1fr; }
  .db-sidebar-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
}
@media (max-width: 600px) {
  .db-sidebar-col { grid-template-columns: 1fr; }
}

/* ─── Section headers ───────────────────────────────────── */
.db-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}
.db-section-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 2px;
}
.db-section-sub {
  font-size: 0.78rem;
  color: var(--muted);
  margin: 0;
}

/* ─── Activity Feed ─────────────────────────────────────── */
.db-activity-card { padding: 20px; }

.db-activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border, rgba(148,163,184,.08));
}
.db-activity-item:last-child { border-bottom: none; }
.db-activity-item--skeleton { pointer-events: none; }

.db-activity-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--accent-soft, rgba(0,255,102,.1));
  color: var(--accent, #00ff66);
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.db-skel-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  flex-shrink: 0;
}

.db-activity-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  flex: 1;
}
.db-activity-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.db-activity-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.db-activity-event {
  font-size: 0.75rem;
  color: var(--muted);
}

.db-activity-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}
.db-activity-time {
  font-size: 0.72rem;
  color: var(--muted);
}

/* ─── Badges ────────────────────────────────────────────── */
.db-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: .2px;
  white-space: nowrap;
}
.db-badge--success  { background: rgba(74,222,128,.15); color: #4ade80; }
.db-badge--danger   { background: rgba(239,68,68,.15);  color: #f87171; }
.db-badge--telegram { background: rgba(14,165,233,.15); color: #38bdf8; }
.db-badge--muted    { background: var(--bg-secondary, rgba(148,163,184,.1)); color: var(--muted); }

/* ─── Paginação ─────────────────────────────────────────── */
.db-pagination {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 14px;
  border-top: 1px solid var(--border, rgba(148,163,184,.08));
  margin-top: 4px;
}
.db-page-btn {
  width: 30px;
  height: 30px;
  border-radius: var(--radius-sm, 6px);
  border: 1px solid var(--border, rgba(148,163,184,.15));
  background: transparent;
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background .15s, border-color .15s;
}
.db-page-btn:hover:not(:disabled) {
  background: var(--bg-secondary, rgba(255,255,255,.05));
  border-color: var(--accent, #00ff66);
  color: var(--accent, #00ff66);
}
.db-page-btn:disabled {
  opacity: .35;
  cursor: not-allowed;
}
.db-page-info {
  font-size: 0.78rem;
  color: var(--muted);
  min-width: 44px;
  text-align: center;
}

/* ─── Error / Empty ────────────────────────────────────── */
.db-error {
  padding: 10px 0;
  color: #f87171;
  font-size: 0.85rem;
}
.db-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px 0;
  color: var(--muted);
}
.db-empty p { margin: 0; font-size: 0.875rem; }

/* ─── Sidebar ───────────────────────────────────────────── */
.db-sidebar-col {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ─── Quick Actions ─────────────────────────────────────── */
.db-quick-card { padding: 20px; }
.db-quick-actions { display: flex; flex-direction: column; gap: 4px; }

.db-quick-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 8px;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background .15s;
  text-align: left;
}
.db-quick-btn:hover { background: var(--bg-secondary, rgba(255,255,255,.05)); }

.db-quick-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.db-quick-icon--flows     { background: rgba(139,92,246,.15); color: #a78bfa; }
.db-quick-icon--channels  { background: rgba(14,165,233,.15); color: #38bdf8; }
.db-quick-icon--contacts  { background: rgba(0,255,102,.12);  color: #4ade80; }
.db-quick-icon--broadcast { background: rgba(251,191,36,.12); color: #fbbf24; }

.db-quick-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
  flex: 1;
  min-width: 0;
}
.db-quick-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-primary);
}
.db-quick-desc {
  font-size: 0.72rem;
  color: var(--muted);
}
.db-quick-arrow {
  color: var(--muted);
  flex-shrink: 0;
  opacity: .6;
}
.db-quick-btn:hover .db-quick-arrow { opacity: 1; color: var(--accent, #00ff66); }

/* ─── Status Card ───────────────────────────────────────── */
.db-status-card { padding: 20px; }
.db-status-list { display: flex; flex-direction: column; gap: 10px; }
.db-status-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.db-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.db-status-dot--ok   { background: #4ade80; box-shadow: 0 0 6px rgba(74,222,128,.5); }
.db-status-dot--warn { background: #fbbf24; box-shadow: 0 0 6px rgba(251,191,36,.5); }
.db-status-dot--err  { background: #f87171; box-shadow: 0 0 6px rgba(239,68,68,.5); }
.db-status-label {
  font-size: 0.82rem;
  color: var(--muted);
  flex: 1;
}
.db-status-val {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--text-primary);
}
</style>
