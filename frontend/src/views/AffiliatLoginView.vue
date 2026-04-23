<template>
  <div class="affiliate-login-page">
    <div class="login-card">
      <div class="logo">
        <h1>Blackchat Pro</h1>
        <p class="subtitle">Portal de Afiliados</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>E-mail</label>
          <input v-model="email" type="email" placeholder="seu@email.com" required :disabled="loading" />
        </div>
        <div class="form-group">
          <label>Senha</label>
          <input v-model="password" type="password" placeholder="••••••••" required :disabled="loading" />
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <button type="submit" :disabled="loading" class="btn-login">
          <span v-if="loading">Entrando...</span>
          <span v-else>Entrar</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { affiliateLogin } from '@/api/affiliate'

const router = useRouter()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await affiliateLogin(email.value, password.value)
    router.push('/affiliate/dashboard')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Credenciais inválidas'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.affiliate-login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0f172a;
}

.login-card {
  background: #1e293b;
  border-radius: 12px;
  padding: 48px 40px;
  width: 100%;
  max-width: 420px;
  border: 1px solid #334155;
}

.logo h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #f8fafc;
  margin: 0 0 4px;
  text-align: center;
}

.subtitle {
  color: #94a3b8;
  font-size: 0.875rem;
  text-align: center;
  margin: 0 0 36px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #cbd5e1;
}

.form-group input {
  padding: 10px 14px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  color: #f8fafc;
  font-size: 0.9375rem;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input:focus {
  border-color: #6366f1;
}

.form-group input:disabled {
  opacity: 0.6;
}

.error-msg {
  background: rgba(239, 68, 68, 0.12);
  color: #f87171;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 0.875rem;
}

.btn-login {
  padding: 12px;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-login:hover:not(:disabled) {
  background: #4f46e5;
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
