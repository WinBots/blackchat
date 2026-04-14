<template>
  <div class="reg-fullscreen">

    <!-- LEFT PANEL -->
    <div class="reg-left">
      <div class="reg-left-inner">
        <div class="reg-brand">
          <img src="@/imagens/bcp-standard.png" alt="Blackchat Pro" class="reg-brand-logo" />
        </div>

        <div class="reg-hero">
          <h1 class="reg-hero-title">Comece agora.<br /><span>É grátis.</span></h1>
          <p class="reg-hero-sub">Crie sua conta e automatize atendimentos, campanhas e fluxos em minutos — sem cartão de crédito.</p>
        </div>

        <ul class="reg-features">
          <li>
            <span class="feat-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            </span>
            Plano Free sem limite de tempo
          </li>
          <li>
            <span class="feat-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            </span>
            Fluxos visuais de automação sem código
          </li>
          <li>
            <span class="feat-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            </span>
            Automação Telegram nativa e CRM integrado
          </li>
          <li>
            <span class="feat-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            </span>
            Suporte por chat incluído
          </li>
        </ul>

        <div class="reg-left-footer">
          <p>© 2026 Blackchat Pro. Todos os direitos reservados.</p>
        </div>
      </div>
    </div>

    <!-- RIGHT PANEL -->
    <div class="reg-right">
      <div class="reg-form-wrapper">
        <div class="reg-form-header">
          <h2>Criar conta gratuita</h2>
          <p>Preencha os dados abaixo para começar</p>
        </div>

        <form class="reg-form" @submit.prevent="handleRegister">

          <div class="rf-row">
            <div class="rf-group">
              <label class="rf-label" for="full_name">Nome completo</label>
              <input
                id="full_name"
                v-model="form.full_name"
                type="text"
                class="rf-input"
                placeholder="Seu nome"
                autocomplete="name"
                required
              />
            </div>

            <div class="rf-group">
              <label class="rf-label" for="company_name">Empresa</label>
              <input
                id="company_name"
                v-model="form.company_name"
                type="text"
                class="rf-input"
                placeholder="Nome da empresa"
                autocomplete="organization"
                required
              />
            </div>
          </div>

          <div class="rf-group">
            <label class="rf-label" for="email">E-mail</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              class="rf-input"
              placeholder="voce@exemplo.com"
              autocomplete="email"
              required
            />
          </div>

          <div class="rf-group">
            <label class="rf-label" for="password">Senha</label>
            <div class="rf-pass-wrap">
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                class="rf-input rf-pass-input"
                placeholder="Mínimo 6 caracteres"
                autocomplete="new-password"
                required
              />
              <button class="rf-pass-toggle" type="button" @click="showPassword = !showPassword" :aria-label="showPassword ? 'Ocultar senha' : 'Mostrar senha'">
                <svg v-if="showPassword" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20C7 20 2.73 16.11 1 12c.62-1.47 1.51-2.87 2.64-4.11"/>
                  <path d="M10.58 10.58a2 2 0 0 0 2.83 2.83"/>
                  <path d="M9.88 5.09A10.94 10.94 0 0 1 12 4c5 0 9.27 3.89 11 8-1 2.39-2.72 4.45-4.9 5.88"/>
                  <path d="M1 1l22 22"/>
                </svg>
                <svg v-else width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
            </div>
          </div>

          <div class="rf-group">
            <label class="rf-label" for="password_confirm">Confirmar senha</label>
            <div class="rf-pass-wrap">
              <input
                id="password_confirm"
                v-model="form.password_confirm"
                :type="showPasswordConfirm ? 'text' : 'password'"
                class="rf-input rf-pass-input"
                placeholder="Digite a senha novamente"
                autocomplete="new-password"
                required
              />
              <button class="rf-pass-toggle" type="button" @click="showPasswordConfirm = !showPasswordConfirm" :aria-label="showPasswordConfirm ? 'Ocultar senha' : 'Mostrar senha'">
                <svg v-if="showPasswordConfirm" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20C7 20 2.73 16.11 1 12c.62-1.47 1.51-2.87 2.64-4.11"/>
                  <path d="M10.58 10.58a2 2 0 0 0 2.83 2.83"/>
                  <path d="M9.88 5.09A10.94 10.94 0 0 1 12 4c5 0 9.27 3.89 11 8-1 2.39-2.72 4.45-4.9 5.88"/>
                  <path d="M1 1l22 22"/>
                </svg>
                <svg v-else width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
            </div>
          </div>

          <div v-if="error" class="rf-error" role="alert">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            {{ error }}
          </div>

          <button class="rf-btn-primary" type="submit" :disabled="loading">
            <svg v-if="loading" class="rf-spinner" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="40" stroke-dashoffset="10"/></svg>
            <span v-else>Criar conta gratuitamente</span>
          </button>
        </form>

        <div class="rf-footer">
          <p>Já tem uma conta? <router-link to="/login">Fazer login</router-link></p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/http.js'
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
    const response = await api.post('/api/v1/auth/register', {
      email: form.value.email,
      password: form.value.password,
      full_name: form.value.full_name,
      company_name: form.value.company_name
    })

    auth.login(response.data.user, response.data.tenant, response.data.access_token, response.data.workspaces || [])
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
/* ── Layout ─────────────────────────────────────────── */
.reg-fullscreen {
  display: flex;
  min-height: 100vh;
  width: 100%;
  background: #09090a;
}

/* ── Left Panel ─────────────────────────────────────── */
.reg-left {
  flex: 1;
  position: relative;
  display: flex;
  align-items: stretch;
  background: #09090a;
  overflow: hidden;
}

.reg-left::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 20% 20%, rgba(0, 255, 102, 0.12) 0%, transparent 60%),
    radial-gradient(ellipse 60% 80% at 80% 80%, rgba(0, 255, 102, 0.06) 0%, transparent 60%);
  pointer-events: none;
}

.reg-left::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(to bottom, transparent, rgba(0, 255, 102, 0.2), transparent);
}

.reg-left-inner {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  padding: 48px 56px;
  width: 100%;
}

.reg-brand { margin-bottom: auto; }

.reg-brand-logo {
  height: 130px;
  width: auto;
  object-fit: contain;
}

.reg-hero {
  margin-top: auto;
  padding-top: 48px;
}

.reg-hero-title {
  font-size: 2.4rem;
  font-weight: 800;
  color: #fff;
  line-height: 1.25;
  letter-spacing: -0.8px;
  margin-bottom: 16px;
}

.reg-hero-title span { color: #00FF66; }

.reg-hero-sub {
  font-size: 1.05rem;
  color: rgba(255, 255, 255, 0.55);
  line-height: 1.65;
  max-width: 380px;
}

.reg-features {
  list-style: none;
  padding: 0;
  margin: 36px 0 48px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.reg-features li {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.7);
}

.feat-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(0, 255, 102, 0.15);
  color: #00FF66;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.reg-left-footer {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.25);
}

/* ── Right Panel ────────────────────────────────────── */
.reg-right {
  width: 520px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0d0f0d;
  border-left: 1px solid rgba(255, 255, 255, 0.06);
  padding: 40px 24px;
  overflow-y: auto;
}

.reg-form-wrapper {
  width: 100%;
  max-width: 420px;
  padding: 16px 0;
}

.reg-form-header {
  margin-bottom: 28px;
}

.reg-form-header h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.5px;
  margin-bottom: 8px;
}

.reg-form-header p {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.45);
}

/* ── Form ───────────────────────────────────────────── */
.reg-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rf-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.rf-group {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.rf-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
}

.rf-input {
  width: 100%;
  padding: 11px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: #fff;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.rf-input::placeholder { color: rgba(255, 255, 255, 0.25); }

.rf-input:focus {
  border-color: rgba(0, 255, 102, 0.5);
  box-shadow: 0 0 0 3px rgba(0, 255, 102, 0.08);
}

/* ── Password field ─────────────────────────────────── */
.rf-pass-wrap {
  position: relative;
}

.rf-pass-input {
  padding-right: 42px;
}

.rf-pass-toggle {
  position: absolute;
  top: 50%;
  right: 12px;
  transform: translateY(-50%);
  background: none;
  border: none;
  padding: 0;
  color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.rf-pass-toggle:hover { color: rgba(255, 255, 255, 0.75); }

/* ── Error ──────────────────────────────────────────── */
.rf-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #f87171;
  font-size: 0.875rem;
  line-height: 1.4;
}

/* ── Submit button ──────────────────────────────────── */
.rf-btn-primary {
  width: 100%;
  padding: 13px;
  background: #00FF66;
  color: #000;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 4px;
}

.rf-btn-primary:hover:not(:disabled) { background: #00cc52; }
.rf-btn-primary:active:not(:disabled) { transform: scale(0.98); }
.rf-btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

@keyframes spin { to { transform: rotate(360deg); } }
.rf-spinner {
  width: 20px;
  height: 20px;
  animation: spin 0.8s linear infinite;
}

/* ── Footer ─────────────────────────────────────────── */
.rf-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.4);
}

.rf-footer a {
  color: #00FF66;
  text-decoration: none;
  font-weight: 500;
}
.rf-footer a:hover { text-decoration: underline; }

/* ── Responsive ─────────────────────────────────────── */
@media (max-width: 960px) {
  .reg-fullscreen { flex-direction: column; }
  .reg-left { display: none; }
  .reg-right {
    width: 100%;
    min-height: 100vh;
    border-left: none;
  }
}

@media (max-width: 480px) {
  .rf-row {
    grid-template-columns: 1fr;
  }
}
</style>
