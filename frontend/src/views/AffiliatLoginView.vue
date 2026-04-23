<template>
  <div class="login-fullscreen">

    <!-- LEFT PANEL -->
    <div class="login-left">
      <div class="login-left-inner">
        <div class="login-brand">
          <img src="@/imagens/bcp-standard.png" alt="Blackchat Pro" class="login-brand-logo" />
        </div>

        <div class="login-hero">
          <h1 class="login-hero-title">Programa de<br /><span>Afiliados.</span></h1>
          <p class="login-hero-sub">Indique a Blackchat Pro e ganhe comissões recorrentes por cada cliente que você trouxer.</p>
        </div>

        <ul class="login-features">
          <li>
            <span class="feat-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            </span>
            Comissões recorrentes sobre cada venda
          </li>
          <li>
            <span class="feat-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            </span>
            Link de indicação personalizado
          </li>
          <li>
            <span class="feat-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            </span>
            Dashboard com relatórios em tempo real
          </li>
          <li>
            <span class="feat-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            </span>
            Acompanhe indicações e comissões
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
          <div class="affiliate-badge">Área exclusiva para afiliados</div>
          <h2>Acesse seu painel</h2>
          <p>Entre com suas credenciais de afiliado</p>
        </div>

        <form class="login-form" @submit.prevent="handleLogin">
          <div class="lf-group">
            <label class="lf-label">E-mail</label>
            <input
              v-model="email"
              type="email"
              class="lf-input"
              placeholder="voce@exemplo.com"
              required
              :disabled="loading"
            />
          </div>

          <div class="lf-group">
            <label class="lf-label">Senha</label>
            <input
              v-model="password"
              type="password"
              class="lf-input"
              placeholder="••••••••"
              required
              :disabled="loading"
            />
          </div>

          <div v-if="error" class="lf-error">{{ error }}</div>

          <button class="lf-btn-primary" type="submit" :disabled="loading">
            <svg v-if="loading" class="lf-spinner" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="40" stroke-dashoffset="10"/></svg>
            <span v-else>Entrar</span>
          </button>
        </form>

        <div class="lf-footer">
          <p>Não é afiliado? <a href="/">Conheça a plataforma</a></p>
        </div>
      </div>
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
.login-fullscreen {
  display: flex;
  min-height: 100vh;
  width: 100%;
  background: #09090a;
}

/* LEFT */
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
  top: 0; right: 0;
  width: 1px; height: 100%;
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

.login-brand { margin-bottom: auto; }

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

.login-hero-title span { color: #00FF66; }

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
  width: 24px; height: 24px;
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

/* RIGHT */
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

.affiliate-badge {
  display: inline-flex;
  align-items: center;
  background: rgba(0, 255, 102, 0.1);
  color: #00FF66;
  border: 1px solid rgba(0, 255, 102, 0.25);
  border-radius: 20px;
  padding: 5px 14px;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.3px;
  margin-bottom: 16px;
}

.login-form-header { margin-bottom: 32px; }

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

.lf-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
}

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

.lf-input:disabled { opacity: 0.6; }

.lf-error {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 0.875rem;
}

.lf-btn-primary {
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
.lf-btn-primary:hover:not(:disabled) { background: #00cc52; }
.lf-btn-primary:active:not(:disabled) { transform: scale(0.98); }
.lf-btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

@keyframes spin { to { transform: rotate(360deg); } }
.lf-spinner {
  width: 20px; height: 20px;
  animation: spin 0.8s linear infinite;
}

.lf-footer {
  margin-top: 24px;
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
