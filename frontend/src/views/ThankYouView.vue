<template>
  <div class="thankyou-page">
    <div class="card thankyou-card">
      <div class="thankyou-badge">
        <span class="thankyou-dot" />
        Pagamento confirmado
      </div>

      <h1 class="thankyou-title">Obrigado por assinar o plano <span class="thankyou-plan">{{ planName }}</span>!</h1>
      <p class="thankyou-subtitle">
        Seu plano foi ativado com sucesso. Agora você pode aproveitar todos os recursos disponíveis.
      </p>

      <div class="thankyou-section">
        <div class="thankyou-section-title">O que você já pode aproveitar</div>
        <ul class="thankyou-list">
          <li>Conectar seus bots no Telegram e atender em múltiplos canais</li>
          <li>Criar fluxos visuais com gatilhos, mensagens e ações</li>
          <li>Gerenciar contatos, segmentar e acompanhar interações</li>
          <li>Enviar campanhas e comunicados (broadcast) para sua base</li>
        </ul>
      </div>

      <div class="thankyou-actions">
        <button class="btn btn-primary" type="button" @click="goToPlans">Ver meu plano</button>
        <button class="btn btn-ghost" type="button" @click="goToDashboard">Ir para Dashboard</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const auth = useAuth()

const planName = computed(() => {
  try {
    const params = new URLSearchParams(window.location.search)
    return params.get('plan') || 'Pro'
  } catch {
    return 'Pro'
  }
})

const goToPlans = () => {
  if (auth.isAuthenticated.value) {
    router.push('/settings?tab=Planos&checkout=success')
  } else {
    router.push('/login')
  }
}

const goToDashboard = () => {
  if (auth.isAuthenticated.value) {
    router.push('/dashboard')
  } else {
    router.push('/login')
  }
}
</script>

<style scoped>
.thankyou-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
}

.thankyou-card {
  width: 100%;
  max-width: 720px;
}

.thankyou-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  border-radius: var(--radius-full);
  background: var(--accent-soft);
  border: 1px solid rgba(0, 255, 102, 0.18);
  color: var(--accent);
  font-weight: 700;
  font-size: 0.85rem;
  letter-spacing: 0.2px;
}

.thankyou-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 0 4px rgba(0, 255, 102, 0.12);
}

.thankyou-title {
  margin-top: 18px;
  font-size: 2rem;
  line-height: 1.15;
  letter-spacing: -0.6px;
}

.thankyou-plan {
  color: var(--accent);
}

.thankyou-subtitle {
  margin-top: 10px;
  color: var(--text-secondary);
}

.thankyou-section {
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid var(--border);
}

.thankyou-section-title {
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.thankyou-list {
  margin: 0;
  padding-left: 18px;
  color: var(--text-secondary);
  display: grid;
  gap: 8px;
}

.thankyou-actions {
  margin-top: 22px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
</style>
