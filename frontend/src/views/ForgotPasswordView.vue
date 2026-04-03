<template>
  <div class="fp-fullscreen">

    <!-- LEFT PANEL -->
    <div class="fp-left">
      <div class="fp-left-inner">
        <div class="fp-brand">
          <img src="@/imagens/bcp-standard.png" alt="Blackchat Pro" class="fp-brand-logo" />
        </div>

        <div class="fp-hero">
          <h1 class="fp-hero-title">Esqueceu<br />a senha?<br /><span>Sem problema.</span></h1>
          <p class="fp-hero-sub">Informe seu e-mail e enviaremos as instruções para redefinir sua senha rapidamente.</p>
        </div>

        <div class="fp-left-footer">
          <p>© 2026 Blackchat Pro. Todos os direitos reservados.</p>
        </div>
      </div>
    </div>

    <!-- RIGHT PANEL -->
    <div class="fp-right">
      <div class="fp-form-wrapper">

        <!-- Sucesso -->
        <div v-if="sent" class="fp-success">
          <div class="fp-success-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <h2>E-mail enviado!</h2>
          <p>Se o endereço <strong>{{ email }}</strong> estiver cadastrado, você receberá as instruções em breve. Verifique também a caixa de spam.</p>
          <router-link to="/login" class="fp-btn-primary" style="text-decoration:none; display:flex; align-items:center; justify-content:center;">
            Voltar para o login
          </router-link>
        </div>

        <!-- Formulário -->
        <template v-else>
          <div class="fp-form-header">
            <h2>Recuperar senha</h2>
            <p>Digite o e-mail associado à sua conta</p>
          </div>

          <form class="fp-form" @submit.prevent="handleSubmit">
            <div class="ff-group">
              <label class="ff-label" for="email">E-mail</label>
              <input
                id="email"
                v-model="email"
                type="email"
                class="ff-input"
                placeholder="voce@exemplo.com"
                autocomplete="email"
                required
                :disabled="loading"
              />
            </div>

            <div v-if="error" class="ff-error" role="alert">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              {{ error }}
            </div>

            <button class="fp-btn-primary" type="submit" :disabled="loading">
              <svg v-if="loading" class="fp-spinner" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="40" stroke-dashoffset="10"/></svg>
              <span v-else>Enviar instruções</span>
            </button>
          </form>

          <div class="ff-footer">
            <p>Lembrou a senha? <router-link to="/login">Fazer login</router-link></p>
          </div>
        </template>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api/http.js'

const email   = ref('')
const loading = ref(false)
const error   = ref('')
const sent    = ref(false)

const handleSubmit = async () => {
  error.value = ''
  loading.value = true
  try {
    await api.post('/api/v1/auth/forgot-password/', { email: email.value.trim() })
    sent.value = true
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erro ao processar solicitação. Tente novamente.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ── Layout ─────────────────────────────────────────── */
.fp-fullscreen {
  display: flex;
  min-height: 100vh;
  width: 100%;
  background: #09090a;
}

/* ── Left Panel ─────────────────────────────────────── */
.fp-left {
  flex: 1;
  position: relative;
  display: flex;
  align-items: stretch;
  background: #09090a;
  overflow: hidden;
}

.fp-left::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 20% 20%, rgba(0, 255, 102, 0.12) 0%, transparent 60%),
    radial-gradient(ellipse 60% 80% at 80% 80%, rgba(0, 255, 102, 0.06) 0%, transparent 60%);
  pointer-events: none;
}

.fp-left::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(to bottom, transparent, rgba(0, 255, 102, 0.2), transparent);
}

.fp-left-inner {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  padding: 48px 56px;
  width: 100%;
}

.fp-brand { margin-bottom: auto; }

.fp-brand-logo {
  height: 130px;
  width: auto;
  object-fit: contain;
}

.fp-hero {
  margin-top: auto;
  padding-top: 48px;
  padding-bottom: 48px;
}

.fp-hero-title {
  font-size: 2.4rem;
  font-weight: 800;
  color: #fff;
  line-height: 1.25;
  letter-spacing: -0.8px;
  margin-bottom: 16px;
}

.fp-hero-title span { color: #00FF66; }

.fp-hero-sub {
  font-size: 1.05rem;
  color: rgba(255, 255, 255, 0.55);
  line-height: 1.65;
  max-width: 360px;
}

.fp-left-footer {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.25);
}

/* ── Right Panel ────────────────────────────────────── */
.fp-right {
  width: 480px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0d0f0d;
  border-left: 1px solid rgba(255, 255, 255, 0.06);
  padding: 40px 24px;
}

.fp-form-wrapper {
  width: 100%;
  max-width: 380px;
}

/* ── Header ─────────────────────────────────────────── */
.fp-form-header {
  margin-bottom: 32px;
}

.fp-form-header h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.5px;
  margin-bottom: 8px;
}

.fp-form-header p {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.45);
}

/* ── Form ───────────────────────────────────────────── */
.fp-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.ff-group {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.ff-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
}

.ff-input {
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

.ff-input::placeholder { color: rgba(255, 255, 255, 0.25); }

.ff-input:focus {
  border-color: rgba(0, 255, 102, 0.5);
  box-shadow: 0 0 0 3px rgba(0, 255, 102, 0.08);
}

.ff-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Error ──────────────────────────────────────────── */
.ff-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #f87171;
  font-size: 0.875rem;
}

/* ── Button ─────────────────────────────────────────── */
.fp-btn-primary {
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
}

.fp-btn-primary:hover:not(:disabled) { background: #00cc52; }
.fp-btn-primary:active:not(:disabled) { transform: scale(0.98); }
.fp-btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

@keyframes spin { to { transform: rotate(360deg); } }
.fp-spinner {
  width: 20px;
  height: 20px;
  animation: spin 0.8s linear infinite;
}

/* ── Footer ─────────────────────────────────────────── */
.ff-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.4);
}

.ff-footer a {
  color: #00FF66;
  text-decoration: none;
  font-weight: 500;
}
.ff-footer a:hover { text-decoration: underline; }

/* ── Success state ──────────────────────────────────── */
.fp-success {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 16px;
}

.fp-success-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(0, 255, 102, 0.12);
  border: 1px solid rgba(0, 255, 102, 0.25);
  color: #00FF66;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fp-success h2 {
  font-size: 1.6rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.4px;
}

.fp-success p {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.6;
  max-width: 320px;
}

.fp-success strong {
  color: rgba(255, 255, 255, 0.8);
}

.fp-success .fp-btn-primary {
  margin-top: 8px;
}

/* ── Responsive ─────────────────────────────────────── */
@media (max-width: 900px) {
  .fp-fullscreen { flex-direction: column; }
  .fp-left { display: none; }
  .fp-right {
    width: 100%;
    min-height: 100vh;
    border-left: none;
  }
}
</style>
