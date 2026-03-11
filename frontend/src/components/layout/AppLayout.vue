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

        <nav class="sidebar-nav">
          <RouterLink to="/dashboard" @click="closeSidebar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="7" height="7" rx="1"/>
              <rect x="14" y="3" width="7" height="7" rx="1"/>
              <rect x="14" y="14" width="7" height="7" rx="1"/>
              <rect x="3" y="14" width="7" height="7" rx="1"/>
            </svg>
            Dashboard
          </RouterLink>
          <RouterLink to="/contacts" @click="closeSidebar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            Contatos
          </RouterLink>
          <RouterLink to="/flows" @click="closeSidebar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
            Automações
          </RouterLink>
          <RouterLink to="/broadcasts" @click="closeSidebar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 4h16v4H4z"/>
              <path d="M4 10h10v4H4z"/>
              <path d="M4 16h7v4H4z"/>
              <polyline points="18 10 22 12 18 14"/>
            </svg>
            Mensagens em massa
          </RouterLink>
          <RouterLink to="/settings" @click="closeSidebar">
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

        <!-- Usuário Logado na Sidebar -->
        <div class="sidebar-user">
          <div class="sidebar-user-avatar">U</div>
          <div class="sidebar-user-info">
            <div class="sidebar-user-name">{{ userName }}</div>
            <div class="sidebar-user-email">{{ userEmail }}</div>
          </div>
        </div>

        <div class="sidebar-footer">
          <div>Tenant: <strong>{{ tenantName }}</strong></div>
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
        
        <RouterLink to="/contacts" class="mobile-nav-item" @click="closeSidebar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          <span>Contatos</span>
        </RouterLink>
        
        <RouterLink to="/flows" class="mobile-nav-item" @click="closeSidebar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
          <span>Automações</span>
        </RouterLink>
        <RouterLink to="/broadcasts" class="mobile-nav-item" @click="closeSidebar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 4h16v4H4z"/>
            <path d="M4 10h10v4H4z"/>
            <path d="M4 16h7v4H4z"/>
            <polyline points="18 10 22 12 18 14"/>
          </svg>
          <span>Mensagens</span>
        </RouterLink>
        <RouterLink to="/settings" class="mobile-nav-item" @click="closeSidebar">
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
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const sidebarOpen = ref(false)
const auth = useAuth()

const userName = computed(() => auth.user.value?.full_name || auth.user.value?.email || 'Usuário')
const userEmail = computed(() => auth.user.value?.email || '')
const tenantName = computed(() => auth.tenant.value?.name || String(auth.user.value?.tenant_id || '—'))
const isSuperAdmin = computed(() => !!auth.user.value?.is_super_admin)

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
