<template>
  <div class="auth-page">
    <div class="card auth-card register-card">
      <div class="auth-logo" style="margin-bottom: 18px;">
        <div class="auth-logo-mark">
          <img src="@/imagens/icon-std.png" alt="Blackchat Pro" />
        </div>
        <div class="auth-logo-text">Blackchat Pro</div>
      </div>

      <div class="auth-header" style="margin-bottom: 18px;">
        <h1 class="auth-title" style="margin-bottom: 6px;">Registre-se agora</h1>
        <p class="auth-subtitle">Comece no plano <strong>Free</strong> e automatize atendimentos, campanhas e fluxos em minutos.</p>
      </div>

      <form class="auth-form register-form" @submit.prevent="handleRegister">
        <div class="input-group">
          <label class="input-label" for="full_name">Nome completo</label>
          <input id="full_name" v-model="form.full_name" type="text" class="input" placeholder="Seu nome" required />
        </div>

        <div class="input-group">
          <label class="input-label" for="email">E-mail</label>
          <input id="email" v-model="form.email" type="email" class="input" placeholder="voce@exemplo.com" required />
        </div>

        <div class="input-group">
          <label class="input-label" for="company_name">Empresa</label>
          <input id="company_name" v-model="form.company_name" type="text" class="input" placeholder="Nome da empresa" required />
        </div>

        <div class="input-group">
          <label class="input-label" for="password">Senha</label>
          <div class="password-field">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              class="input password-input"
              placeholder="Mínimo 6 caracteres"
              required
            />
            <button class="password-toggle" type="button" @click="showPassword = !showPassword" :aria-label="showPassword ? 'Ocultar senha' : 'Mostrar senha'">
              <svg v-if="showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20C7 20 2.73 16.11 1 12c.62-1.47 1.51-2.87 2.64-4.11" />
                <path d="M10.58 10.58a2 2 0 0 0 2.83 2.83" />
                <path d="M9.88 5.09A10.94 10.94 0 0 1 12 4c5 0 9.27 3.89 11 8-1 2.39-2.72 4.45-4.9 5.88" />
                <path d="M1 1l22 22" />
              </svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            </button>
          </div>
        </div>

        <div class="input-group">
          <label class="input-label" for="password_confirm">Confirmar senha</label>
          <div class="password-field">
            <input
              id="password_confirm"
              v-model="form.password_confirm"
              :type="showPasswordConfirm ? 'text' : 'password'"
              class="input password-input"
              placeholder="Digite a senha novamente"
              required
            />
            <button class="password-toggle" type="button" @click="showPasswordConfirm = !showPasswordConfirm" :aria-label="showPasswordConfirm ? 'Ocultar senha' : 'Mostrar senha'">
              <svg v-if="showPasswordConfirm" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20C7 20 2.73 16.11 1 12c.62-1.47 1.51-2.87 2.64-4.11" />
                <path d="M10.58 10.58a2 2 0 0 0 2.83 2.83" />
                <path d="M9.88 5.09A10.94 10.94 0 0 1 12 4c5 0 9.27 3.89 11 8-1 2.39-2.72 4.45-4.9 5.88" />
                <path d="M1 1l22 22" />
              </svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            </button>
          </div>
        </div>

        <div v-if="error" class="register-error" role="alert">
          {{ error }}
        </div>

        <button class="btn btn-primary" type="submit" :disabled="loading">
          <span>{{ loading ? 'Criando…' : 'Criar conta' }}</span>
        </button>
      </form>

      <div class="auth-footer" style="margin-top: 14px;">
        <p>
          Já tem uma conta?
          <router-link to="/login">Fazer login</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const auth = useAuth()

const form = ref({
  full_name: '',
  email: '',
  company_name: '',
  password: '',
  password_confirm: ''
})

const loading = ref(false)
const error = ref('')

const showPassword = ref(false)
const showPasswordConfirm = ref(false)

const handleRegister = async () => {
  error.value = ''

  if (form.value.password.length < 6) {
    error.value = 'A senha deve ter no mínimo 6 caracteres'
    return
  }

  if (form.value.password !== form.value.password_confirm) {
    error.value = 'As senhas não coincidem'
    return
  }

  loading.value = true
  try {
    const response = await axios.post('http://localhost:8061/api/v1/auth/register/', {
      email: form.value.email,
      password: form.value.password,
      full_name: form.value.full_name,
      company_name: form.value.company_name
    })

    auth.login(response.data.user, response.data.tenant, response.data.access_token)
    router.push('/dashboard')
  } catch (err) {
    console.error('Erro no registro:', err)
    error.value = err.response?.data?.detail || 'Erro ao criar conta. Tente novamente.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-card {
  max-width: 760px;
  padding: 22px;
}

.register-form {
  gap: 12px;
}

.password-field {
  position: relative;
}

.password-input {
  padding-right: 44px;
}

.password-toggle {
  position: absolute;
  top: 50%;
  right: 10px;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.6);
  color: var(--muted);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.password-toggle:hover {
  color: var(--text);
  border-color: rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.9);
}

.register-error {
  padding: 10px 12px;
  border-radius: var(--radius-md);
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.35);
  color: #ef4444;
  font-size: 0.875rem;
}

@media (max-width: 720px) {
  .register-card {
    max-width: 460px;
  }
}

@media (max-height: 760px) {
  .auth-logo {
    margin-bottom: 14px !important;
  }

  .auth-header {
    margin-bottom: 14px !important;
  }

  .auth-form {
    gap: 12px;
  }
}
</style>

