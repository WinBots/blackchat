import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/http.js'

const user = ref(null)
const tenant = ref(null)
const token = ref(null)
const workspaces = ref([])

const safeJsonParse = (value) => {
  if (!value) return null
  try {
    return JSON.parse(value)
  } catch {
    return null
  }
}

// Carregar dados do localStorage na inicialização
if (typeof window !== 'undefined') {
  const storedUser = localStorage.getItem('user')
  const storedTenant = localStorage.getItem('tenant')
  const storedToken = localStorage.getItem('token')
  const storedWorkspaces = localStorage.getItem('workspaces')

  const parsedUser = safeJsonParse(storedUser)
  const parsedTenant = safeJsonParse(storedTenant)
  const parsedWorkspaces = safeJsonParse(storedWorkspaces)
  if (storedUser && !parsedUser) localStorage.removeItem('user')
  if (storedTenant && !parsedTenant) localStorage.removeItem('tenant')
  if (storedWorkspaces && !parsedWorkspaces) localStorage.removeItem('workspaces')

  if (parsedUser) user.value = parsedUser
  if (parsedTenant) tenant.value = parsedTenant
  if (storedToken) token.value = storedToken
  if (Array.isArray(parsedWorkspaces)) workspaces.value = parsedWorkspaces
}

export function useAuth() {
  const router = useRouter()
  
  const isAuthenticated = computed(() => !!token.value)

  const activeWorkspaceId = computed(() => tenant.value?.id || null)

  const userRole = computed(() => {
    if (!workspaces.value.length || !tenant.value) return 'owner'
    const ws = workspaces.value.find(w => w.id === tenant.value.id)
    if (!ws) return 'member' // workspace não encontrado na lista = restrito até refresh
    return ws.role || 'owner'
  })

  const isWorkspaceOwner = computed(() => userRole.value === 'owner')

  // Permissões granulares do workspace ativo
  const currentPermissions = computed(() => {
    if (!workspaces.value.length || !tenant.value) return []
    const ws = workspaces.value.find(w => w.id === tenant.value.id)
    return ws?.permissions || []
  })

  const hasPermission = (key) => {
    // Owner sempre tem tudo
    if (userRole.value === 'owner') return true
    return currentPermissions.value.includes(key)
  }
  
  const login = (userData, tenantData, authToken, workspacesList = []) => {
    user.value = userData
    tenant.value = tenantData
    token.value = authToken
    workspaces.value = workspacesList.length ? workspacesList : [
      { id: tenantData.id, name: tenantData.name, role: 'owner', is_default: true }
    ]
    
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('tenant', JSON.stringify(tenantData))
    localStorage.setItem('token', authToken)
    localStorage.setItem('workspaces', JSON.stringify(workspaces.value))
  }

  const switchWorkspace = async (workspaceId) => {
    try {
      const res = await api.post(`/api/v1/workspaces/${workspaceId}/switch`)
      const { access_token, tenant: newTenant, role } = res.data

      token.value = access_token
      tenant.value = newTenant
      if (user.value) {
        user.value = { ...user.value, tenant_id: newTenant.id }
      }

      // Atualizar is_default na lista local
      workspaces.value = workspaces.value.map(ws => ({
        ...ws,
        is_default: ws.id === workspaceId,
      }))

      localStorage.setItem('token', access_token)
      localStorage.setItem('tenant', JSON.stringify(newTenant))
      localStorage.setItem('user', JSON.stringify(user.value))
      localStorage.setItem('workspaces', JSON.stringify(workspaces.value))

      // Recarregar a página para limpar cache de dados do workspace anterior
      window.location.href = '/dashboard'

      return true
    } catch (err) {
      console.error('Erro ao trocar workspace:', err)
      return false
    }
  }

  const refreshWorkspaces = async () => {
    try {
      const res = await api.get('/api/v1/workspaces/')
      workspaces.value = res.data
      localStorage.setItem('workspaces', JSON.stringify(res.data))
    } catch (err) {
      console.error('Erro ao atualizar workspaces:', err)
    }
  }
  
  const logout = () => {
    user.value = null
    tenant.value = null
    token.value = null
    workspaces.value = []
    
    localStorage.removeItem('user')
    localStorage.removeItem('tenant')
    localStorage.removeItem('token')
    localStorage.removeItem('workspaces')
    
    router.push('/login')
  }
  
  const requireAuth = () => {
    if (!isAuthenticated.value) {
      router.push('/login')
      return false
    }
    return true
  }
  
  return {
    user: computed(() => user.value),
    tenant: computed(() => tenant.value),
    token: computed(() => token.value),
    workspaces: computed(() => workspaces.value),
    activeWorkspaceId,
    userRole,
    isWorkspaceOwner,
    currentPermissions,
    hasPermission,
    isAuthenticated,
    login,
    logout,
    switchWorkspace,
    refreshWorkspaces,
    requireAuth
  }
}

