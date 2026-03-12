<template>
  <div class="auth-page">
    <div class="card auth-card">
      <div class="auth-logo">
        <div class="auth-logo-mark">
          <img src="@/imagens/icon-std.png" alt="Blackchat Pro" />
        </div>
        <div class="auth-logo-text">Blackchat Pro</div>
      </div>

      <div class="auth-header">
        <h1 class="auth-title">Recuperar senha</h1>
        <p class="auth-subtitle">
          Informe seu e-mail cadastrado e enviaremos as instruções de redefinição.
        </p>
      </div>

      <!-- Sucesso -->
      <div v-if="sent" class="success-box">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
          <polyline points="22 4 12 14.01 9 11.01" />
        </svg>
        <span>Se o e-mail estiver cadastrado, você receberá as instruções em breve.</span>
      </div>

      <!-- Formulário -->
      <form v-else class="auth-form" @submit.prevent="handleSubmit">
        <div v-if="error" class="error-box">{{ error }}</div>

        <div class="input-group">
          <label class="input-label" for="email">E-mail</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="input"
            placeholder="voce@exemplo.com"
            required
            :disabled="loading"
          />
        </div>

        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ loading ? 'Enviando…' : 'Enviar instruções' }}
        </button>
      </form>

      <div class="auth-footer" style="margin-top: 14px;">
        <p>
          Lembrou a senha?
          <router-link to="/login">Fazer login</router-link>
        </p>
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
.success-box {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  padding: 14px 16px;
  color: #166534;
  font-size: 14px;
  line-height: 1.5;
}
.success-box svg { flex-shrink: 0; margin-top: 1px; color: #16a34a; }

.error-box {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 10px 14px;
  color: #991b1b;
  font-size: 14px;
  margin-bottom: 12px;
}
</style>
