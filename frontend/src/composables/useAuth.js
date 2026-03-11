import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const user = ref(null)
const tenant = ref(null)
const token = ref(null)

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

  const parsedUser = safeJsonParse(storedUser)
  const parsedTenant = safeJsonParse(storedTenant)
  if (storedUser && !parsedUser) localStorage.removeItem('user')
  if (storedTenant && !parsedTenant) localStorage.removeItem('tenant')

  if (parsedUser) user.value = parsedUser
  if (parsedTenant) tenant.value = parsedTenant
  if (storedToken) token.value = storedToken
}

export function useAuth() {
  const router = useRouter()
  
  const isAuthenticated = computed(() => !!token.value)
  
  const login = (userData, tenantData, authToken) => {
    user.value = userData
    tenant.value = tenantData
    token.value = authToken
    
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('tenant', JSON.stringify(tenantData))
    localStorage.setItem('token', authToken)
  }
  
  const logout = () => {
    user.value = null
    tenant.value = null
    token.value = null
    
    localStorage.removeItem('user')
    localStorage.removeItem('tenant')
    localStorage.removeItem('token')
    
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
    isAuthenticated,
    login,
    logout,
    requireAuth
  }
}

