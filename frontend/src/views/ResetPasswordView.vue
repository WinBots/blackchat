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
        <h1 class="auth-title">Nova senha</h1>
        <p class="auth-subtitle">Escolha uma nova senha para sua conta.</p>
      </div>

      <!-- Token inválido / expirado -->
      <div v-if="tokenError" class="error-box">
        {{ tokenError }}
        <div style="margin-top:10px;">
          <router-link to="/forgot-password">Solicitar novo link →</router-link>
        </div>
      </div>

      <!-- Sucesso -->
      <div v-else-if="done" class="success-box">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" />
        </svg>
        <span>Senha redefinida com sucesso! <router-link to="/login">Fazer login →</router-link></span>
      </div>

      <!-- Formulário -->
      <form v-else class="auth-form" @submit.prevent="handleSubmit">
        <div v-if="error" class="error-box">{{ error }}</div>

        <div class="input-group">
          <label class="input-label" for="password">Nova senha</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="input"
            placeholder="Mínimo 6 caracteres"
            required
            :disabled="loading"
          />
        </div>

        <div class="input-group">
          <label class="input-label" for="confirm">Confirmar nova senha</label>
          <input
            id="confirm"
            v-model="form.confirm"
            type="password"
            class="input"
            placeholder="Repita a senha"
            required
            :disabled="loading"
          />
        </div>

        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ loading ? 'Salvando…' : 'Redefinir senha' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route      = useRoute()
const form       = ref({ password: '', confirm: '' })
const loading    = ref(false)
const error      = ref('')
const tokenError = ref('')
const done       = ref(false)
const token      = ref('')

onMounted(() => {
  token.value = route.query.token || ''
  if (!token.value) {
    tokenError.value = 'Link inválido. Solicite um novo link de recuperação.'
  }
})

const handleSubmit = async () => {
  error.value = ''

  if (form.value.password.length < 6) {
    error.value = 'A senha deve ter no mínimo 6 caracteres.'
    return
  }
  if (form.value.password !== form.value.confirm) {
    error.value = 'As senhas não coincidem.'
    return
  }

  loading.value = true
  try {
    await axios.post('http://localhost:8061/api/v1/auth/reset-password/', {
      token: token.value,
      new_password: form.value.password,
    })
    done.value = true
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erro ao redefinir senha. O link pode ter expirado.'
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
  padding: 12px 16px;
  color: #991b1b;
  font-size: 14px;
  margin-bottom: 12px;
}
</style>
