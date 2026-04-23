import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '@/views/LandingPage.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import DashboardView from '@/views/DashboardView.vue'
import ContactsView from '@/views/ContactsView.vue'
import FlowsView from '@/views/FlowsView.vue'
import FlowEditView from '@/views/FlowEditView.vue'
import SettingsView from '@/views/SettingsView.vue'
import BroadcastsView from '@/views/BroadcastsView.vue'
import SuperAdminView from '@/views/SuperAdminView.vue'
import ForgotPasswordView from '@/views/ForgotPasswordView.vue'
import ResetPasswordView from '@/views/ResetPasswordView.vue'
import ThankYouView from '@/views/ThankYouView.vue'
import AffiliatLoginView from '@/views/AffiliatLoginView.vue'
import AffiliateDashboardView from '@/views/AffiliateDashboardView.vue'
import AdminAffiliatesView from '@/views/AdminAffiliatesView.vue'

const routes = [
  { path: '/', name: 'home', component: LandingPage },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/thank-you', name: 'thank-you', component: ThankYouView },
  { path: '/dashboard', name: 'dashboard', component: DashboardView, meta: { permission: 'dashboard' } },
  { path: '/contacts', name: 'contacts', component: ContactsView, meta: { permission: 'contacts' } },
  { path: '/flows', name: 'flows', component: FlowsView, meta: { permission: 'flows' } },
  { path: '/flows/:id', name: 'flow-edit', component: FlowEditView, props: true, meta: { permission: 'flows' } },
  { path: '/broadcasts', name: 'broadcasts', component: BroadcastsView, meta: { permission: 'broadcasts' } },
  { path: '/settings', name: 'settings', component: SettingsView, meta: { permission: 'settings' } },
  { path: '/admin', name: 'super-admin', component: SuperAdminView },
  { path: '/admin/affiliates', name: 'admin-affiliates', component: AdminAffiliatesView },
  { path: '/affiliate/login', name: 'affiliate-login', component: AffiliatLoginView },
  { path: '/affiliate/dashboard', name: 'affiliate-dashboard', component: AffiliateDashboardView },
  { path: '/forgot-password', name: 'forgot-password', component: ForgotPasswordView },
  { path: '/reset-password', name: 'reset-password', component: ResetPasswordView },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard para proteger rotas privadas
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const storedUser = localStorage.getItem('user')
  let currentUser = null
  try {
    currentUser = storedUser ? JSON.parse(storedUser) : null
  } catch {
    currentUser = null
  }
  const publicPages = ['/', '/login', '/register', '/landing', '/forgot-password', '/reset-password', '/thank-you', '/affiliate/login', '/affiliate/dashboard']
  const authRequired = !publicPages.includes(to.path)

  // Se a rota requer autenticação e não há token
  if (authRequired && !token) {
    return next('/login')
  }

  // Se está logado e tenta acessar login/register, redireciona para dashboard
  if (token && (to.path === '/login' || to.path === '/register')) {
    return next('/dashboard')
  }

  // Protege área de super admin
  if (to.path === '/admin' || to.path === '/admin/affiliates') {
    if (!token) return next('/login')
    if (!currentUser?.is_super_admin) return next('/dashboard')
  }

  // Verifica permissão granular do workspace
  if (to.meta?.permission && token) {
    try {
      const storedWorkspaces = localStorage.getItem('workspaces')
      const workspaces = storedWorkspaces ? JSON.parse(storedWorkspaces) : []
      const storedTenant = localStorage.getItem('tenant')
      const activeTenant = storedTenant ? JSON.parse(storedTenant) : null
      const activeWs = workspaces.find(w => w.id === activeTenant?.id)
      const role = activeWs?.role || 'owner'
      const perms = activeWs?.permissions || []
      // Owner sempre tem acesso total
      if (role !== 'owner' && !perms.includes(to.meta.permission)) {
        // Redireciona para o primeiro item permitido, ou dashboard como fallback
        const firstAllowed = ['dashboard', 'contacts', 'flows', 'broadcasts', 'settings'].find(p => perms.includes(p))
        return next(firstAllowed ? `/${firstAllowed}` : '/dashboard')
      }
    } catch {}
  }

  next()
})

export default router
