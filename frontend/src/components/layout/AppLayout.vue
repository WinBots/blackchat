<template>
  <div class="app-layout">
    <!-- Mobile Header -->
    <header class="mobile-header">
      <div class="mobile-header-left">
        <button class="mobile-menu-toggle" @click="toggleSidebar">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
        <div class="mobile-logo">
          <img src="@/imagens/bcp-standard.png" alt="Blackchat Pro" class="mobile-brand-img" />
        </div>
      </div>
      <div class="topbar-avatar" style="width: 36px; height: 36px;">
        U
      </div>
    </header>

    <!-- Mobile Overlay -->
    <div class="overlay" :class="{ show: sidebarOpen }" @click="toggleSidebar"></div>

    <div class="app-shell">
      <aside class="sidebar" :class="{ open: sidebarOpen }">
        <div class="sidebar-logo">
          <img src="@/imagens/bcp-standard.png" alt="Blackchat Pro" class="sidebar-brand-img" />
        </div>

        <!-- Workspace Selector -->
        <div class="ws-selector" v-if="auth.workspaces.value.length > 0">
          <button class="ws-current" @click="wsDropdownOpen = !wsDropdownOpen">
            <div class="ws-current-icon">
              {{ (auth.tenant.value?.name || 'W').charAt(0).toUpperCase() }}
            </div>
            <div class="ws-current-info">
              <span class="ws-current-name">{{ auth.tenant.value?.name || 'Workspace' }}</span>
              <span class="ws-current-role">
                {{ roleLabelMap[currentRole] || 'Dono' }}
                <span v-if="currentPlan" class="ws-plan-tag ws-plan-tag--sm">{{ currentPlan }}</span>
              </span>
            </div>
            <svg class="ws-chevron" :class="{ rotated: wsDropdownOpen }" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
          </button>

          <Transition name="ws-drop">
            <div v-if="wsDropdownOpen" class="ws-dropdown">
              <div class="ws-dropdown-label">Meus Workspaces</div>
              <button
                v-for="ws in auth.workspaces.value"
                :key="ws.id"
                class="ws-dropdown-item"
                :class="{ active: ws.id === auth.tenant.value?.id }"
                @click="handleSwitchWorkspace(ws.id)"
              >
                <div class="ws-item-icon">{{ ws.name.charAt(0).toUpperCase() }}</div>
                <div class="ws-item-info">
                  <span class="ws-item-name">{{ ws.name }}</span>
                  <span class="ws-item-role">{{ roleLabelMap[ws.role] || ws.role }}</span>
                </div>
                <span v-if="ws.plan_name" class="ws-plan-tag">{{ ws.plan_name }}</span>
                <svg v-if="ws.id === auth.tenant.value?.id" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
              </button>
              <div class="ws-dropdown-divider"></div>
              <RouterLink to="/settings?tab=Workspaces" class="ws-dropdown-action" @click="closeSidebar(); wsDropdownOpen = false">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                Gerenciar Workspaces
              </RouterLink>
            </div>
          </Transition>
        </div>

        <nav class="sidebar-nav">
          <RouterLink v-if="auth.hasPermission('dashboard')" to="/dashboard" @click="closeSidebar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="7" height="7" rx="1"/>
              <rect x="14" y="3" width="7" height="7" rx="1"/>
              <rect x="14" y="14" width="7" height="7" rx="1"/>
              <rect x="3" y="14" width="7" height="7" rx="1"/>
            </svg>
            Dashboard
          </RouterLink>
          <RouterLink v-if="auth.hasPermission('contacts')" to="/contacts" @click="closeSidebar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            Contatos
          </RouterLink>
          <RouterLink v-if="auth.hasPermission('flows')" to="/flows" @click="closeSidebar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
            Automações
          </RouterLink>
          <RouterLink v-if="auth.hasPermission('broadcasts')" to="/broadcasts" @click="closeSidebar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 4h16v4H4z"/>
              <path d="M4 10h10v4H4z"/>
              <path d="M4 16h7v4H4z"/>
              <polyline points="18 10 22 12 18 14"/>
            </svg>
            Mensagens em massa
          </RouterLink>
          <RouterLink v-if="auth.hasPermission('settings')" to="/settings" @click="closeSidebar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="9"/>
              <path d="M12 8v4l3 1"/>
            </svg>
            Configurações
          </RouterLink>

          <RouterLink v-if="isSuperAdmin" to="/admin" @click="closeSidebar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2l3 7h7l-5.5 4 2.5 7-7-4-7 4 2.5-7L2 9h7z" />
            </svg>
            Super Admin
          </RouterLink>
        </nav>

        <!-- Widget de progresso de disparo em massa -->
        <div v-if="broadcastProgress.job.value" class="broadcast-progress-widget">
          <div class="bpw-header">
            <div class="bpw-icon">
              <svg v-if="broadcastProgress.isRunning.value" class="bpw-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
              </svg>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </div>
            <div class="bpw-title">{{ broadcastProgress.job.value.flow_name }}</div>
            <button class="bpw-dismiss" @click="broadcastProgress.dismiss()" title="Fechar">×</button>
          </div>
          <div class="bpw-bar-wrap">
            <div class="bpw-bar-fill" :style="{ width: broadcastProgress.percent.value + '%' }"></div>
          </div>
          <div class="bpw-stats">
            <span>
              {{ (broadcastProgress.job.value.sent || 0) + (broadcastProgress.job.value.failed || 0) }}
              /
              {{ broadcastProgress.job.value.total }}
            </span>
            <span class="bpw-pct">{{ broadcastProgress.percent.value }}%</span>
          </div>
          <div v-if="broadcastProgress.isDone.value" class="bpw-done">
            ✓ Concluído — {{ broadcastProgress.job.value.sent }} enviados, {{ broadcastProgress.job.value.failed }} falhas
          </div>
        </div>

        <!-- Usuário Logado na Sidebar -->
        <div class="sidebar-user">
          <div class="sidebar-user-avatar">U</div>
          <div class="sidebar-user-info">
            <div class="sidebar-user-name">{{ userName }}</div>
            <div class="sidebar-user-email">{{ userEmail }}</div>
          </div>
        </div>

        <div class="sidebar-footer">
          <div>Beta • v0.2</div>

          <button type="button" class="sidebar-logout" @click="handleLogout">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            Sair
          </button>
        </div>
      </aside>

      <main class="main-area">
        <section>
          <slot />
        </section>
      </main>
    </div>

    <!-- Mobile Bottom Navigation -->
    <nav class="mobile-bottom-nav">
      <div class="mobile-bottom-nav-inner">
        <RouterLink to="/dashboard" class="mobile-nav-item" @click="closeSidebar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="14" width="7" height="7" rx="1"/>
            <rect x="3" y="14" width="7" height="7" rx="1"/>
          </svg>
          <span>Painel</span>
        </RouterLink>
        
        <RouterLink v-if="auth.hasPermission('contacts')" to="/contacts" class="mobile-nav-item" @click="closeSidebar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          <span>Contatos</span>
        </RouterLink>
        
        <RouterLink v-if="auth.hasPermission('flows')" to="/flows" class="mobile-nav-item" @click="closeSidebar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
          <span>Automações</span>
        </RouterLink>
        <RouterLink v-if="auth.hasPermission('broadcasts')" to="/broadcasts" class="mobile-nav-item" @click="closeSidebar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 4h16v4H4z"/>
            <path d="M4 10h10v4H4z"/>
            <path d="M4 16h7v4H4z"/>
            <polyline points="18 10 22 12 18 14"/>
          </svg>
          <span>Mensagens</span>
        </RouterLink>
        <RouterLink v-if="auth.hasPermission('settings')" to="/settings" class="mobile-nav-item" @click="closeSidebar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="9"/>
            <path d="M12 8v4l3 1"/>
          </svg>
          <span>Configurações</span>
        </RouterLink>

        <RouterLink v-if="isSuperAdmin" to="/admin" class="mobile-nav-item" @click="closeSidebar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2l3 7h7l-5.5 4 2.5 7-7-4-7 4 2.5-7L2 9h7z" />
          </svg>
          <span>Admin</span>
        </RouterLink>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useBroadcastProgress } from '@/composables/useBroadcastProgress'

const broadcastProgress = useBroadcastProgress()
import { useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const sidebarOpen = ref(false)
const wsDropdownOpen = ref(false)
const auth = useAuth()

// Fechar dropdown ao clicar fora
const handleClickOutside = (e) => {
  if (wsDropdownOpen.value && !e.target.closest('.ws-selector')) {
    wsDropdownOpen.value = false
  }
}
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  // Manter lista de workspaces sempre atualizada (inclui workspaces convidados)
  auth.refreshWorkspaces()
})
onUnmounted(() => document.removeEventListener('click', handleClickOutside))

const roleLabelMap = {
  owner: 'Dono',
  admin: 'Admin',
  member: 'Membro',
}

const currentRole = computed(() => {
  const ws = auth.workspaces.value.find(w => w.id === auth.tenant.value?.id)
  return ws?.role || 'owner'
})

const currentPlan = computed(() => {
  const ws = auth.workspaces.value.find(w => w.id === auth.tenant.value?.id)
  return ws?.plan_name || null
})

const userName = computed(() => auth.user.value?.full_name || auth.user.value?.email || 'Usuário')
const userEmail = computed(() => auth.user.value?.email || '')
const tenantName = computed(() => auth.tenant.value?.name || String(auth.user.value?.tenant_id || '—'))
const isSuperAdmin = computed(() => !!auth.user.value?.is_super_admin)

const handleSwitchWorkspace = async (wsId) => {
  if (wsId === auth.tenant.value?.id) {
    wsDropdownOpen.value = false
    return
  }
  wsDropdownOpen.value = false
  await auth.switchWorkspace(wsId)
}

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const closeSidebar = () => {
  sidebarOpen.value = false
}

const handleLogout = () => {
  closeSidebar()
  auth.logout()
}

const pageTitle = computed(() => {
  const titles = {
    '/dashboard': 'Dashboard',
    '/contacts': 'Contatos',
    '/flows': 'Automações',
    '/broadcasts': 'Mensagens em massa',
    '/settings': 'Configurações'
  }
  return titles[route.path] || 'Painel'
})

const pageDescription = computed(() => {
  const descriptions = {
    '/dashboard': 'Visão geral da sua automação',
    '/contacts': 'Visualize e gerencie seus contatos',
    '/flows': 'Crie e gerencie suas automações',
    '/broadcasts': 'Dispare mensagens em massa para segmentos de contatos',
    '/settings': 'Controle geral das preferências da conta'
  }
  return descriptions[route.path] || 'Automatize suas conversas no Telegram'
})
</script>

<style scoped>
/* Widget de progresso de disparo em massa */
.broadcast-progress-widget {
  margin: 0 12px 10px;
  background: rgba(0, 255, 102, 0.05);
  border: 1px solid rgba(0, 255, 102, 0.2);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.bpw-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bpw-icon {
  color: #00ff66;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.bpw-spin {
  animation: bpw-spin 1s linear infinite;
}
@keyframes bpw-spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

.bpw-title {
  flex: 1;
  font-size: 0.78rem;
  font-weight: 600;
  color: #e2e8f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bpw-dismiss {
  background: none;
  border: none;
  color: #4b5563;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  padding: 0 2px;
  transition: color 0.2s;
  flex-shrink: 0;
}
.bpw-dismiss:hover { color: #e5e7eb; }

.bpw-bar-wrap {
  height: 4px;
  border-radius: 99px;
  background: rgba(255,255,255,0.07);
  overflow: hidden;
}

.bpw-bar-fill {
  height: 100%;
  border-radius: 99px;
  background: linear-gradient(90deg, #00cc52, #00ff66);
  transition: width 0.6s ease;
}

.bpw-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
  color: #6b7280;
}

.bpw-pct {
  font-weight: 600;
  color: #00ff66;
}

.bpw-done {
  font-size: 0.72rem;
  color: #6ee7b7;
  padding-top: 2px;
}
</style>
