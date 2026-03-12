<template>
  <div class="login-fullscreen">

    <!-- LEFT PANEL -->
    <div class="login-left">
      <div class="login-left-inner">
        <div class="login-brand">
          <img src="@/imagens/bcp-standard.png" alt="Blackchat Pro" class="login-brand-logo" />
        </div>

        <div class="login-hero">
          <h1 class="login-hero-title">Automatize suas conversas.<br /><span>Escale seu negócio.</span></h1>
          <p class="login-hero-sub">A plataforma inteligente de automação via Telegram para equipes modernas.</p>
        </div>

        <ul class="login-features">
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
            Automação Telegram nativa
          </li>
          <li>
            <span class="feat-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            </span>
            CRM integrado e gestão de leads
          </li>
          <li>
            <span class="feat-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            </span>
            Relatórios e métricas em tempo real
          </li>
        </ul>

        <div class="login-left-footer">
          <p>© 2026 Blackchat Pro. Todos os direitos reservados.</p>
        </div>
      </div>
    </div>

    <!-- RIGHT PANEL -->
    <div class="login-right">
      <div class="login-form-wrapper">
        <div class="login-form-header">
          <h2>Bem-vindo de volta</h2>
          <p>Entre com suas credenciais para acessar o painel</p>
        </div>

        <form class="login-form" @submit.prevent="onSubmit">
          <div class="lf-group">
            <label class="lf-label">E-mail</label>
            <input
              v-model="email"
              type="email"
              class="lf-input"
              placeholder="voce@exemplo.com"
              required
            />
          </div>

          <div class="lf-group">
            <div class="lf-label-row">
              <label class="lf-label">Senha</label>
              <router-link to="/forgot-password" class="lf-link">Esqueceu a senha?</router-link>
            </div>
            <input
              v-model="password"
              type="password"
              class="lf-input"
              placeholder="••••••••"
              required
            />
          </div>

          <label class="lf-remember">
            <input type="checkbox" />
            <span>Lembrar de mim</span>
          </label>

          <button class="lf-btn-primary" type="submit" :disabled="loading">
            <svg v-if="loading" class="lf-spinner" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="40" stroke-dashoffset="10"/></svg>
            <span v-else>Entrar</span>
          </button>
        </form>

        <div class="lf-footer">
          <p>Não tem uma conta? <router-link to="/register">Criar conta gratuita</router-link></p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/http.js'
import { useToast } from '@/composables/useToast'
import { useAuth } from '@/composables/useAuth'

const email = ref('admin@blackchatpro.com')
const password = ref('admin123')
const loading = ref(false)
const router = useRouter()
const toast = useToast()
const auth = useAuth()

const onSubmit = async () => {
  loading.value = true
  try {
    const response = await api.post('/api/v1/auth/login/', {
      email: email.value,
      password: password.value
    })
    auth.login(response.data.user, response.data.tenant, response.data.access_token)
    toast.success('Login realizado com sucesso!')
    router.push('/dashboard')
  } catch (err) {
    console.error('Erro no login:', err)
    toast.error(err.response?.data?.detail || 'Erro ao fazer login. Verifique suas credenciais.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ── Layout ─────────────────────────────────────────── */
.login-fullscreen {
  display: flex;
  min-height: 100vh;
  width: 100%;
  background: #09090a;
}

/* ── Left Panel ─────────────────────────────────────── */
.login-left {
  flex: 1;
  position: relative;
  display: flex;
  align-items: stretch;
  background: #09090a;
  overflow: hidden;
}

.login-left::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 20% 20%, rgba(0, 255, 102, 0.12) 0%, transparent 60%),
    radial-gradient(ellipse 60% 80% at 80% 80%, rgba(0, 255, 102, 0.06) 0%, transparent 60%);
  pointer-events: none;
}

.login-left::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(to bottom, transparent, rgba(0, 255, 102, 0.2), transparent);
}

.login-left-inner {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  padding: 48px 56px;
  width: 100%;
}

.login-brand {
  margin-bottom: auto;
}

.login-brand-logo {
  height: 130px;
  width: auto;
  object-fit: contain;
}

.login-hero {
  margin-top: auto;
  padding-top: 48px;
}

.login-hero-title {
  font-size: 2.4rem;
  font-weight: 800;
  color: #fff;
  line-height: 1.25;
  letter-spacing: -0.8px;
  margin-bottom: 16px;
}

.login-hero-title span {
  color: #00FF66;
}

.login-hero-sub {
  font-size: 1.05rem;
  color: rgba(255, 255, 255, 0.55);
  line-height: 1.65;
  max-width: 380px;
}

.login-features {
  list-style: none;
  padding: 0;
  margin: 36px 0 48px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.login-features li {
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

.login-left-footer {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.25);
}

/* ── Right Panel ────────────────────────────────────── */
.login-right {
  width: 480px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0d0f0d;
  border-left: 1px solid rgba(255, 255, 255, 0.06);
  padding: 40px 24px;
}

.login-form-wrapper {
  width: 100%;
  max-width: 380px;
}

.login-form-header {
  margin-bottom: 32px;
}

.login-form-header h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.5px;
  margin-bottom: 8px;
}

.login-form-header p {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.45);
}

/* ── Form Elements ──────────────────────────────────── */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.lf-group {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.lf-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.lf-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
}

.lf-link {
  font-size: 0.8rem;
  color: #00FF66;
  text-decoration: none;
  opacity: 0.8;
  transition: opacity 0.2s;
}
.lf-link:hover { opacity: 1; }

.lf-input {
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

.lf-input::placeholder { color: rgba(255, 255, 255, 0.25); }

.lf-input:focus {
  border-color: rgba(0, 255, 102, 0.5);
  box-shadow: 0 0 0 3px rgba(0, 255, 102, 0.08);
}

.lf-remember {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  margin-top: -4px;
}

.lf-remember input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #00FF66;
  cursor: pointer;
}

.lf-btn-primary {
  width: 100%;
  padding: 13px;
  background: #00FF66;
  color: #000000;
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
.lf-btn-primary:hover:not(:disabled) { background: #00cc52; }
.lf-btn-primary:active:not(:disabled) { transform: scale(0.98); }
.lf-btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

@keyframes spin { to { transform: rotate(360deg); } }
.lf-spinner {
  width: 20px; height: 20px;
  animation: spin 0.8s linear infinite;
}

.lf-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 20px 0;
  color: rgba(255, 255, 255, 0.2);
  font-size: 0.8rem;
}
.lf-divider::before,
.lf-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
}

.lf-footer {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  text-align: center;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.4);
}

.lf-footer a {
  color: #00FF66;
  text-decoration: none;
  font-weight: 500;
}
.lf-footer a:hover { text-decoration: underline; }

/* ── Responsive ─────────────────────────────────────── */
@media (max-width: 900px) {
  .login-fullscreen { flex-direction: column; }
  .login-left { display: none; }
  .login-right {
    width: 100%;
    min-height: 100vh;
    border-left: none;
  }
}
</style>
