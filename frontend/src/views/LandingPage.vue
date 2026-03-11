<template>
  <div class="landing-page">
    <!-- Background ambient glow effects -->
    <div class="bg-glow bg-glow-1"></div>
    <div class="bg-glow bg-glow-2"></div>
    <div class="grid-overlay"></div>

    <!-- Navbar -->
    <header class="lp-navbar">
      <div class="lp-container">
        <div class="lp-logo">
          <div class="lp-logo-mark">
            <img src="@/imagens/icon-wht.png" alt="Blackchat Pro" />
          </div>
          <span class="lp-logo-text">Blackchat Pro</span>
        </div>
        <nav class="lp-nav-links">
          <a href="#recursos">Recursos</a>
          <a href="#planos">Planos</a>
        </nav>
        <div class="lp-nav-actions">
          <router-link to="/login" class="lp-btn lp-btn-ghost">Entrar</router-link>
          <router-link to="/register" class="lp-btn lp-btn-primary">
            <i class="fas fa-rocket"></i> Come�ar Gr�tis
          </router-link>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="lp-hero">
      <div class="lp-container">
        <div class="lp-badge">
          <span class="lp-badge-dot"></span>
          14 dias gr�tis � Sem cart�o de cr�dito
        </div>
        <h1 class="lp-hero-title">
          Automatize suas conversas com
          <span class="lp-highlight">Blackchat Pro</span>
        </h1>
        <p class="lp-hero-subtitle">
          Crie fluxos inteligentes para Telegram, Instagram e WhatsApp.
          Aumente o engajamento e converta mais clientes.
        </p>
        <div class="lp-hero-cta">
          <router-link to="/register" class="lp-btn lp-btn-primary lp-btn-lg">
            <i class="fas fa-rocket"></i> Comece Gr�tis - 14 Dias
          </router-link>
          <router-link to="/login" class="lp-btn lp-btn-outline lp-btn-lg">
            <i class="fas fa-sign-in-alt"></i> J� tenho conta
          </router-link>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="lp-features" id="recursos">
      <div class="lp-container">
        <div class="lp-section-label">Recursos</div>
        <h2 class="lp-section-title">Tudo que voc� precisa para crescer</h2>
        <p class="lp-section-subtitle">Uma plataforma completa para automa��o de conversas em m�ltiplos canais.</p>
        <div class="lp-features-grid">
          <div class="lp-feature-card" v-for="feature in features" :key="feature.title">
            <div class="lp-feature-icon" :style="{ background: feature.iconBg }">
              <i :class="feature.icon"></i>
            </div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="lp-stats">
      <div class="lp-container">
        <div class="lp-stats-grid">
          <div class="lp-stat-item" v-for="stat in stats" :key="stat.label">
            <div class="lp-stat-value">{{ stat.value }}</div>
            <div class="lp-stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Pricing Section -->
    <section class="lp-pricing" id="planos">
      <div class="lp-container">
        <div class="lp-section-label">Planos</div>
        <h2 class="lp-section-title">Pre�os transparentes e flex�veis</h2>
        <p class="lp-section-subtitle">Pague apenas pelos contatos que voc� engaja. Cobran�a mensal, sem fidelidade.</p>

        <div v-if="loading" class="lp-loading">
          <div class="lp-spinner"></div>
          <span>Carregando planos...</span>
        </div>

        <div v-else class="lp-pricing-grid">
          <div
            v-for="plan in plans"
            :key="plan.id"
            class="lp-pricing-card"
            :class="{ 'lp-pricing-card--popular': plan.name === 'pro' }"
          >
            <div v-if="plan.name === 'pro'" class="lp-popular-badge">
              <i class="fas fa-star"></i> Mais Popular
            </div>

            <div class="lp-pricing-header">
              <div class="lp-pricing-plan-icon">
                <i :class="planIcon(plan.name)"></i>
              </div>
              <h3 class="lp-pricing-name">{{ plan.display_name }}</h3>
              <p class="lp-pricing-desc">{{ planDescription(plan.name) }}</p>

              <!-- Plano Gr�tis -->
              <div v-if="plan.name === 'free'" class="pricing-price pricing-inline mb-8">
                <span class="price-value text-green-500">Gr�tis</span>
              </div>

              <!-- Plano Pro (pre�o fixo) -->
              <div v-else-if="plan.name === 'pro'" class="pricing-price pricing-inline mb-8">
                <span class="price-currency p-xs">R$</span>
                <span class="price-value">99</span>
                <span class="price-period p-xs">/m�s</span>
                <div class="pricing-pro-contacts">at� 2.500 contatos</div>
              </div>

              <!-- Plano Enterprise (personalizado) -->
              <div v-else-if="plan.name === 'unlimited'" class="pricing-price pricing-vpm mb-8">
                <div class="pricing-vpm-from">personalizado</div>
                <div class="pricing-ent-main">Enterprise</div>
                <div class="pricing-vpm-unit">cobrado por volume de contatos</div>
                <div class="pricing-vpm-min">
                  <span class="pricing-vpm-min-label">M�n.</span>
                  <span class="pricing-vpm-min-currency">R$</span>
                  <span class="pricing-vpm-min-value">999</span>
                  <span class="pricing-vpm-min-period">/m�s</span>
                </div>
              </div>

              <!-- Outros planos VPM -->
              <div v-else-if="plan.vpm_price" class="pricing-price pricing-vpm mb-8">
                <div class="pricing-vpm-from">a partir de</div>
                <div class="pricing-vpm-main">
                  <span class="price-currency p-xs">R$</span>
                  <span class="price-value">{{ formatPriceNumber(plan.vpm_price) }}</span>
                </div>
                <div class="pricing-vpm-unit">por 1.000 contatos ativos</div>
                <div v-if="plan.min_monthly" class="pricing-vpm-min">
                  <span class="pricing-vpm-min-label">M�n.</span>
                  <span class="pricing-vpm-min-currency">R$</span>
                  <span class="pricing-vpm-min-value">{{ formatPriceNumber(plan.min_monthly) }}</span>
                  <span class="pricing-vpm-min-period">/m�s</span>
                </div>
              </div>
            </div>

            <div class="lp-pricing-divider" style="margin-top: auto;"></div>

            <ul class="lp-pricing-features">
              <template v-if="plan.name === 'free'">
                <li><i class="fas fa-check lp-check"></i> <span>1 Bot no Telegram</span></li>
                <li><i class="fas fa-check lp-check"></i> <span>At� 100 contatos ativos</span></li>
                <li><i class="fas fa-check lp-check"></i> <span>1 Fluxo de automa��o</span></li>
                <li><i class="fas fa-check lp-check"></i> <span>1 Gatilho de entrada</span></li>
                <li><i class="fas fa-check lp-check"></i> <span>1 Sequ�ncia de mensagens</span></li>
                <li><i class="fas fa-check lp-check"></i> <span>1 Tag de segmenta��o</span></li>
                <li><i class="fas fa-check lp-check"></i> <span>1 Usu�rio administrador</span></li>
              </template>
              <template v-else-if="plan.name === 'pro'">
                <li><i class="fas fa-check lp-check"></i> <span>3 Bots no Telegram</span></li>
                <li><i class="fas fa-check lp-check"></i> <span>At� <b>2.500 contatos ativos</b></span></li>
                <li><i class="fas fa-check lp-check"></i> <span>Fluxos de automa��o ilimitados</span></li>
                <li><i class="fas fa-check lp-check"></i> <span>Gatilhos de palavra-chave ilimitados</span></li>
                <li><i class="fas fa-check lp-check"></i> <span>Sequ�ncias de mensagens ilimitadas</span></li>
                <li><i class="fas fa-check lp-check"></i> <span>Tags ilimitadas</span></li>
                <li><i class="fas fa-check lp-check"></i> <span>Campos do usu�rio ilimitados</span></li>
                <li><i class="fas fa-check lp-check"></i> <span>3 Colaboradores</span></li>
              </template>
              <template v-else-if="plan.name === 'unlimited'">
                <li><i class="fas fa-check lp-check"></i> <span><b>Bots ilimitados</b></span></li>
                <li><i class="fas fa-check lp-check"></i> <span><b>Contatos ilimitados</b> (cobrado por volume)</span></li>
                <li><i class="fas fa-check lp-check"></i> <span>Fluxos ilimitados</span></li>
                <li><i class="fas fa-check lp-check"></i> <span>Gatilhos ilimitados</span></li>
                <li><i class="fas fa-check lp-check"></i> <span>Sequ�ncias ilimitadas</span></li>
                <li><i class="fas fa-check lp-check"></i> <span>Tags e campos ilimitados</span></li>
                <li><i class="fas fa-check lp-check"></i> <span><b>Administradores ilimitados</b></span></li>
                <li><i class="fas fa-check lp-check lp-check--gold"></i> <span>Suporte priorit�rio 24/7</span></li>
                <li><i class="fas fa-check lp-check lp-check--gold"></i> <span>API + Webhooks</span></li>
              </template>
            </ul>

            <router-link
              v-if="plan.name !== 'unlimited'"
              :to="`/register?plan=${plan.name}`"
              class="lp-btn-plan"
            >
              {{ plan.name === 'free' ? 'Come�ar Gr�tis' : 'Assinar Agora' }}
              <i class="fas fa-arrow-right"></i>
            </router-link>
            <a
              v-else
              href="#lp-enterprise-calc"
              class="lp-btn-plan lp-btn-plan--enterprise"
            >
              Ver Pre�os
              <i class="fas fa-calculator"></i>
            </a>
          </div>
        </div>

        <!-- Calculadora VPM -->
        <div class="lp-vpm-calc" id="lp-enterprise-calc">
          <div class="lp-vpm-calc-header">
            <h3 class="lp-vpm-calc-title">Calcule o custo do seu plano mensal</h3>
            <p class="lp-vpm-calc-sub">Os planos Pro e Enterprise s�o faturados mensalmente de acordo com o tamanho da sua lista de contatos</p>
          </div>
          <div class="lp-vpm-calc-card">
            <div class="lp-vpm-calc-body">
              <div class="lp-vpm-calc-left">
                <label class="lp-vpm-calc-label">Quantos <b>contatos</b> espera engajar?</label>
                <div class="lp-vpm-calc-number-wrap">
                  <span class="lp-vpm-calc-number">{{ calcContacts.toLocaleString('pt-BR') }}</span>
                </div>
              </div>
              <div class="lp-vpm-calc-equals">=</div>
              <div class="lp-vpm-calc-right">
                <span class="lp-vpm-calc-price">R$&nbsp;{{ formatPriceNumber(calcPrice) }}<small>/m�s</small></span>
                <span class="lp-vpm-calc-plan-label">{{ calcPlanLabel }}</span>
                <span class="lp-vpm-calc-rate-badge">{{ calcRateLabel }}</span>
              </div>
            </div>
            <div class="lp-vpm-calc-slider-wrap">
              <input type="range" class="lp-vpm-calc-range" min="0" max="100" step="1" v-model.number="calcSlider" />
              <div class="lp-vpm-calc-ticks">
                <span>500</span><span>10k</span><span>100k</span><span>500k</span><span>2M</span>
              </div>
            </div>
            <div class="lp-vpm-calc-footer">
              <button class="lp-vpm-calc-link" @click="showPriceTable = true">
                <i class="fas fa-table"></i> Ver tabela de pre�os completa
              </button>
              <router-link
                :to="`/register?plan=unlimited&contacts=${calcContacts}`"
                class="lp-btn lp-btn-primary lp-vpm-calc-cta"
              >
                <i class="fas fa-rocket"></i> Assinar Enterprise
              </router-link>
            </div>
          </div>
        </div>

        <!-- Modal Tabela de Pre�os -->
        <Teleport to="body">
          <div v-if="showPriceTable" class="lp-modal-overlay" @click.self="showPriceTable = false">
            <div class="lp-modal">
              <div class="lp-modal-header">
                <h3>Tabela de Pre�os</h3>
                <button class="lp-modal-close" @click="showPriceTable = false"><i class="fas fa-times"></i></button>
              </div>
              <div class="lp-modal-body">
                <table class="lp-price-table">
                  <thead>
                    <tr>
                      <th>M�x. de contatos</th>
                      <th>Pre�o por m�s</th>
                      <th>Pre�o por 1K</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in pricingTableRows" :key="row.contacts">
                      <td>{{ row.contacts.toLocaleString('pt-BR') }}</td>
                      <td class="lp-price-table-val">R${{ formatPriceNumber(row.price) }}</td>
                      <td class="lp-price-table-per">R${{ formatPriceNumber(row.pricePerK) }}</td>
                    </tr>
                    <tr class="lp-price-table-extra">
                      <td>2.000.001+</td>
                      <td class="lp-price-table-val">R$68.600 + excedente</td>
                      <td class="lp-price-table-per">R$34,30</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </Teleport>

      </div>
    </section>

    <!-- CTA Final -->
    <section class="lp-cta">
      <div class="lp-container">
        <div class="lp-cta-card">
          <div class="lp-cta-glow"></div>
          <h2>Pronto para automatizar suas conversas?</h2>
          <p>Junte-se a centenas de empresas que j� confiam no Blackchat Pro</p>
          <router-link to="/register" class="lp-btn lp-btn-primary lp-btn-lg">
            <i class="fas fa-rocket"></i> Come�ar Agora
          </router-link>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="lp-footer">
      <div class="lp-container">
        <div class="lp-footer-content">
          <div class="lp-logo">
            <div class="lp-logo-mark">
              <img src="@/imagens/icon-wht.png" alt="Blackchat Pro" />
            </div>
            <span class="lp-logo-text">Blackchat Pro</span>
          </div>
          <p class="lp-footer-copy">� 2026 Blackchat Pro. Todos os direitos reservados.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const plans = ref([])
const loading = ref(true)

// Calculadora VPM � tabela oficial de pre�os com interpola��o linear
const calcSlider = ref(30) // ~5.000 contatos por padr�o
const showPriceTable = ref(false)
const PRO_MIN = 99
const ENT_MIN = 999

// Tabela de pre�os oficial (contatos ? pre�o/m�s)
const PRICE_TABLE = [
  { contacts:         500, price:      24.50 },
  { contacts:       2_500, price:     106.31 },
  { contacts:       5_000, price:     206.27 },
  { contacts:      10_000, price:     401.65 },
  { contacts:      15_000, price:     593.80 },
  { contacts:      20_000, price:     783.93 },
  { contacts:      30_000, price:   1_160.15 },
  { contacts:      40_000, price:   1_532.60 },
  { contacts:      50_000, price:   1_902.32 },
  { contacts:      60_000, price:   2_269.90 },
  { contacts:      70_000, price:   2_635.70 },
  { contacts:      80_000, price:   2_999.97 },
  { contacts:      90_000, price:   3_362.90 },
  { contacts:     100_000, price:   3_724.64 },
  { contacts:     120_000, price:   4_444.35 },
  { contacts:     140_000, price:   5_160.26 },
  { contacts:     160_000, price:   5_872.92 },
  { contacts:     180_000, price:   6_582.79 },
  { contacts:     200_000, price:   7_290.17 },
  { contacts:     300_000, price:  10_790.40 },
  { contacts:     400_000, price:  14_266.69 },
  { contacts:     500_000, price:  17_726.88 },
  { contacts:     600_000, price:  21_174.36 },
  { contacts:     700_000, price:  24_611.56 },
  { contacts:     800_000, price:  28_040.28 },
  { contacts:     900_000, price:  31_461.87 },
  { contacts:   1_000_000, price:  34_877.31 },
  { contacts:   1_200_000, price:  41_711.85 },
  { contacts:   1_400_000, price:  48_467.37 },
  { contacts:   1_600_000, price:  55_198.55 },
  { contacts:   1_800_000, price:  61_908.60 },
  { contacts:   2_000_000, price:  68_600.00 },
]

// Interpola o pre�o para qualquer n�mero de contatos
const getPrice = (contacts) => {
  if (contacts <= 0) return 0
  const last = PRICE_TABLE[PRICE_TABLE.length - 1]
  if (contacts >= last.contacts) {
    // Excedente cobrado a R$34,30/1K
    return last.price + Math.ceil((contacts - last.contacts) / 1000) * 34.30
  }
  const first = PRICE_TABLE[0]
  if (contacts <= first.contacts) {
    // Abaixo de 500: proporcional
    return first.price * (contacts / first.contacts)
  }
  // Interpola��o linear entre os pontos da tabela
  for (let i = 1; i < PRICE_TABLE.length; i++) {
    if (contacts <= PRICE_TABLE[i].contacts) {
      const lo = PRICE_TABLE[i - 1]
      const hi = PRICE_TABLE[i]
      const t = (contacts - lo.contacts) / (hi.contacts - lo.contacts)
      return lo.price + t * (hi.price - lo.price)
    }
  }
  return last.price
}

const getEffectiveRate = (contacts) => {
  if (contacts <= 0) return 49
  return getPrice(contacts) / (contacts / 1000)
}

// Slider: 500 ? 2.000.000 em escala logar�tmica (500 * 4000^(t/100))
const calcContacts = computed(() =>
  Math.round(500 * Math.pow(4000, calcSlider.value / 100))
)

const calcPrice = computed(() => Math.max(getPrice(calcContacts.value), PRO_MIN))

const calcPlanLabel = computed(() =>
  calcPrice.value >= ENT_MIN ? 'Enterprise' : 'Pro'
)

const calcRateLabel = computed(() =>
  `R$\u00a0${formatPriceNumber(getEffectiveRate(calcContacts.value))}/1K contatos`
)

// Tabela completa de pre�os (exata, sem interpola��o)
const pricingTableRows = computed(() =>
  PRICE_TABLE.map(({ contacts, price }) => ({
    contacts,
    price: Math.max(price, PRO_MIN),
    pricePerK: price / (contacts / 1000),
  }))
)

const features = [
  {
    title: 'Telegram Nativo',
    description: 'Automa��o completa no Telegram � o canal com 500M+ de usu�rios ativos no mundo.',
    icon: 'fab fa-telegram',
    iconBg: 'rgba(14, 165, 233, 0.15)'
  },
  {
    title: 'Fluxos Visuais',
    description: 'Editor drag-and-drop intuitivo para criar automa��es complexas sem escrever c�digo.',
    icon: 'fas fa-project-diagram',
    iconBg: 'rgba(174, 255, 145, 0.15)'
  },
  {
    title: 'Automa��o 24/7',
    description: 'Respostas instant�neas a qualquer hora do dia, mesmo enquanto voc� dorme.',
    icon: 'fas fa-bolt',
    iconBg: 'rgba(251, 191, 36, 0.15)'
  },
  {
    title: 'Analytics em Tempo Real',
    description: 'M�tricas detalhadas para entender seu p�blico e otimizar cada campanha.',
    icon: 'fas fa-chart-line',
    iconBg: 'rgba(168, 85, 247, 0.15)'
  },
  {
    title: 'Broadcast Inteligente',
    description: 'Envie campanhas segmentadas para sua base de contatos com um clique.',
    icon: 'fas fa-bullhorn',
    iconBg: 'rgba(239, 68, 68, 0.15)'
  },
  {
    title: 'Em Breve: API & Webhooks',
    description: 'Integra��o com seus sistemas via API REST e webhooks � em desenvolvimento.',
    icon: 'fas fa-plug',
    iconBg: 'rgba(174, 255, 145, 0.08)'
  }
]

const stats = [
  { value: '500M+', label: 'Usu�rios no Telegram' },
  { value: '24/7', label: 'Disponibilidade' },
  { value: '< 1s', label: 'Tempo de resposta' },
  { value: '99.9%', label: 'Uptime garantido' }
]

const planIcon = (name) => {
  const icons = {
    free: 'fas fa-seedling',
    pro: 'fas fa-rocket',
    unlimited: 'fas fa-crown'
  }
  return icons[name] || 'fas fa-layer-group'
}

const planDescription = (name) => {
  const descs = {
    free: 'Para testar a ferramenta',
    pro: 'Plano fixo � at� 2.500 contatos',
    unlimited: 'Para grandes volumes � cobrado por contatos'
  }
  return descs[name] || 'Plano completo'
}

const loadPlans = async () => {
  try {
    const response = await axios.get('http://localhost:8061/api/v1/public/plans/')
    plans.value = response.data
  } catch (error) {
    console.error('Erro ao carregar planos:', error)
  } finally {
    loading.value = false
  }
}

const formatNumber = (num) => {
  if (!num) return 'Ilimitados'
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(0)}K`
  return num.toString()
}

const formatPriceNumber = (value) => {
  const n = Number(value)
  if (!Number.isFinite(n)) return ''
  const isInt = Math.abs(n - Math.round(n)) < 1e-9
  return n.toLocaleString('pt-BR', {
    minimumFractionDigits: isInt ? 0 : 2,
    maximumFractionDigits: isInt ? 0 : 2
  })
}

const minChargeValue = (plan) => plan?.min_monthly ?? null

onMounted(() => {
  loadPlans()
})
</script>

<style scoped>
/* ============================================================
   LANDING PAGE - DESIGN TECNOL�GICO
   ============================================================ */

/* === Background === */
.landing-page {
  min-height: 100vh;
  background: #050816;
  position: relative;
  overflow-x: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #e5e7eb;
}

.bg-glow {
  position: fixed;
  border-radius: 50%;
  filter: blur(120px);
  pointer-events: none;
  z-index: 0;
}

.bg-glow-1 {
  width: 700px;
  height: 700px;
  top: -200px;
  left: -200px;
  background: radial-gradient(circle, rgba(174, 255, 145, 0.08) 0%, transparent 70%);
}

.bg-glow-2 {
  width: 600px;
  height: 600px;
  bottom: -150px;
  right: -150px;
  background: radial-gradient(circle, rgba(14, 165, 233, 0.07) 0%, transparent 70%);
}

.grid-overlay {
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(148, 163, 184, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  pointer-events: none;
  z-index: 0;
}

.lp-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  position: relative;
  z-index: 1;
}

/* === Navbar === */
.lp-navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(9, 9, 10, 0.85);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(148, 163, 184, 0.08);
  padding: 14px 0;
}

.lp-navbar .lp-container {
  display: flex;
  align-items: center;
  gap: 32px;
}

.lp-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}

.lp-logo-mark {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.lp-logo-mark img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.lp-logo-text {
  font-weight: 700;
  font-size: 1.1rem;
  color: #f8fafc;
  letter-spacing: -0.3px;
}

.lp-nav-links {
  display: flex;
  gap: 4px;
  flex: 1;
}

.lp-nav-links a {
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #94a3b8;
  text-decoration: none;
  transition: all 0.15s ease;
}

.lp-nav-links a:hover {
  background: rgba(148, 163, 184, 0.08);
  color: #e5e7eb;
}

.lp-nav-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* === Buttons === */
.lp-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 999px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s ease;
  border: none;
  white-space: nowrap;
}

.lp-btn-primary {
  background: linear-gradient(135deg, #aeff91, #7de86a);
  color: #0b1120;
  box-shadow: 0 0 20px rgba(174, 255, 145, 0.35);
}

.lp-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 35px rgba(174, 255, 145, 0.5);
}

.lp-btn-ghost {
  background: transparent;
  color: #94a3b8;
}

.lp-btn-ghost:hover {
  background: rgba(148, 163, 184, 0.08);
  color: #e5e7eb;
}

.lp-btn-outline {
  background: rgba(255, 255, 255, 0.05);
  color: #e5e7eb;
  border: 1px solid rgba(148, 163, 184, 0.2);
  backdrop-filter: blur(10px);
}

.lp-btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(148, 163, 184, 0.4);
  transform: translateY(-2px);
}

.lp-btn-lg {
  padding: 14px 28px;
  font-size: 1rem;
}

/* === Hero === */
.lp-hero {
  padding: 120px 0 100px;
  text-align: center;
}

.lp-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  background: rgba(174, 255, 145, 0.08);
  border: 1px solid rgba(174, 255, 145, 0.2);
  border-radius: 999px;
  font-size: 0.8rem;
  color: #aeff91;
  font-weight: 500;
  margin-bottom: 28px;
  letter-spacing: 0.3px;
}

.lp-badge-dot {
  width: 7px;
  height: 7px;
  background: #aeff91;
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(174, 255, 145, 0.8);
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.lp-hero-title {
  font-size: 3.75rem;
  font-weight: 800;
  line-height: 1.15;
  color: #f8fafc;
  margin: 0 auto 24px;
  max-width: 800px;
  letter-spacing: -1.5px;
}

.lp-highlight {
  background: linear-gradient(135deg, #aeff91 0%, #7de86a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 0 30px rgba(174, 255, 145, 0.3));
}

.lp-hero-subtitle {
  font-size: 1.2rem;
  color: #94a3b8;
  max-width: 600px;
  margin: 0 auto 48px;
  line-height: 1.7;
}

.lp-hero-cta {
  display: flex;
  gap: 14px;
  justify-content: center;
  flex-wrap: wrap;
}

/* === Section Styles === */
.lp-section-label {
  display: inline-block;
  padding: 4px 14px;
  background: rgba(174, 255, 145, 0.08);
  border: 1px solid rgba(174, 255, 145, 0.2);
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #aeff91;
  margin-bottom: 16px;
}

.lp-section-title {
  font-size: 2.4rem;
  font-weight: 800;
  color: #f8fafc;
  margin-bottom: 12px;
  letter-spacing: -0.8px;
}

.lp-section-subtitle {
  font-size: 1.05rem;
  color: #64748b;
  max-width: 520px;
  line-height: 1.6;
}

/* === Features === */
.lp-features {
  padding: 100px 0;
}

.lp-features .lp-container > * {
  margin-bottom: 0;
}

.lp-features .lp-section-subtitle {
  margin-bottom: 60px;
}

.lp-features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 60px;
}

.lp-feature-card {
  background: linear-gradient(135deg, rgba(11, 13, 11, 0.9), rgba(11, 13, 11, 0.7));
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 20px;
  padding: 28px;
  transition: all 0.25s ease;
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}

.lp-feature-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(174, 255, 145, 0.03) 0%, transparent 60%);
  opacity: 0;
  transition: opacity 0.25s ease;
}

.lp-feature-card:hover::before {
  opacity: 1;
}

.lp-feature-card:hover {
  transform: translateY(-4px);
  border-color: rgba(174, 255, 145, 0.2);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
}

.lp-feature-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  margin-bottom: 18px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.lp-feature-card h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 10px;
}

.lp-feature-card p {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.65;
}

/* === Stats === */
.lp-stats {
  padding: 60px 0;
  border-top: 1px solid rgba(148, 163, 184, 0.06);
  border-bottom: 1px solid rgba(148, 163, 184, 0.06);
  background: rgba(11, 13, 11, 0.4);
  backdrop-filter: blur(10px);
}

.lp-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 32px;
  text-align: center;
}

.lp-stat-value {
  font-size: 2.4rem;
  font-weight: 800;
  color: #f8fafc;
  letter-spacing: -1px;
  background: linear-gradient(135deg, #aeff91, #7de86a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.lp-stat-label {
  font-size: 0.85rem;
  color: #64748b;
  margin-top: 6px;
  font-weight: 500;
}

/* === Pricing === */
.lp-pricing {
  padding: 100px 0;
}

.lp-pricing .lp-section-subtitle {
  margin-bottom: 60px;
}

/* === Billing Toggle === */
.lp-billing-toggle-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 60px;
}

.lp-billing-toggle {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0;
  padding: 4px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.12);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.lp-toggle-thumb {
  position: absolute;
  top: 4px;
  left: 4px;
  height: calc(100% - 8px);
  width: calc(50% - 4px);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(148, 163, 184, 0.18);
  transform: translateX(0);
  transition: transform 0.25s cubic-bezier(0.4, 0.0, 0.2, 1);
}

.lp-toggle-thumb.is-yearly {
  transform: translateX(100%);
}

.lp-toggle-option {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 14px;
  min-width: 112px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  cursor: pointer;
  user-select: none;
  font-size: 0.95rem;
  font-weight: 700;
  color: #94a3b8;
}

.lp-toggle-option.active {
  color: #f8fafc;
}

.lp-discount-badge {
  background: rgba(174, 255, 145, 0.15);
  color: #aeff91;
  border: 1px solid rgba(174, 255, 145, 0.3);
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 800;
  white-space: nowrap;
}

/* Acessibilidade: foco vis�vel */
.lp-toggle-option:focus-visible {
  outline: 2px solid rgba(174, 255, 145, 0.45);
  outline-offset: 2px;
}

@media (max-width: 420px) {
  .lp-toggle-option {
    min-width: 96px;
    padding: 10px 12px;
    font-size: 0.9rem;
  }
}

/* === Pricing Price helpers === */
.pricing-inline {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 2px;
  line-height: 1;
}

.pricing-vpm {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.pricing-pro-contacts {
  font-size: 0.78rem;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
}

.pricing-ent-main {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text-primary, #f1f5f9);
  line-height: 1.1;
}

.pricing-vpm-from {
  font-size: 0.72rem;
  color: #94a3b8;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: -4px;
}

.pricing-vpm-main {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 6px;
  line-height: 1;
}

.pricing-vpm-unit {
  font-size: 0.85rem;
  color: #64748b;
  margin-top: -8px;
  font-weight: 600;
}

.pricing-vpm-min {
  margin-top: 2px;
  display: inline-flex;
  align-items: baseline;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(251, 191, 36, 0.10);
  border: 1px solid rgba(251, 191, 36, 0.22);
  box-shadow: 0 0 18px rgba(251, 191, 36, 0.10);
}

.pricing-vpm-min-label {
  font-size: 0.72rem;
  font-weight: 900;
  color: rgba(251, 191, 36, 0.95);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.pricing-vpm-min-currency {
  font-size: 0.85rem;
  font-weight: 900;
  color: rgba(251, 191, 36, 0.95);
}

.pricing-vpm-min-value {
  font-size: 1.15rem;
  font-weight: 900;
  color: #fbbf24;
  letter-spacing: -0.02em;
}

.pricing-vpm-min-period {
  font-size: 0.82rem;
  font-weight: 800;
  color: #94a3b8;
}

.lp-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px;
  color: #64748b;
  font-size: 0.95rem;
}

.lp-spinner {
  width: 22px;
  height: 22px;
  border: 2px solid rgba(174, 255, 145, 0.2);
  border-top-color: #aeff91;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.lp-pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-top: 60px;
  align-items: start;
}

.lp-pricing-card {
  background: linear-gradient(160deg, rgba(11, 13, 11, 0.95), rgba(11, 13, 11, 0.8));
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 24px;
  padding: 32px;
  position: relative;
  transition: all 0.25s ease;
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.lp-pricing-card:hover {
  transform: translateY(-6px);
  border-color: rgba(148, 163, 184, 0.2);
  box-shadow: 0 30px 70px rgba(0, 0, 0, 0.3);
}

.lp-pricing-card--popular {
  border-color: rgba(174, 255, 145, 0.35);
  background: linear-gradient(160deg, rgba(11, 13, 11, 0.98), rgba(11, 13, 11, 0.92));
  box-shadow: 0 0 0 1px rgba(174, 255, 145, 0.15), 0 30px 60px rgba(0, 0, 0, 0.3);
}

.lp-pricing-card--popular:hover {
  border-color: rgba(174, 255, 145, 0.55);
  box-shadow: 0 0 0 1px rgba(174, 255, 145, 0.3), 0 30px 80px rgba(0, 0, 0, 0.4);
}

.lp-popular-badge {
  position: absolute;
  top: -14px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #aeff91, #7de86a);
  color: #0b1120;
  padding: 5px 18px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  white-space: nowrap;
  letter-spacing: 0.3px;
  box-shadow: 0 0 20px rgba(174, 255, 145, 0.4);
}

.lp-pricing-header {
  text-align: center;
  margin-bottom: 24px;
}

.lp-pricing-plan-icon {
  width: 52px;
  height: 52px;
  background: rgba(174, 255, 145, 0.1);
  border: 1px solid rgba(174, 255, 145, 0.2);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  color: #aeff91;
  margin: 0 auto 16px;
}

.lp-pricing-name {
  font-size: 1.3rem;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 6px;
}

.lp-pricing-desc {
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 20px;
}

.lp-pricing-price {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 2px;
  line-height: 1;
}

.lp-price-free {
  font-size: 2.5rem;
  font-weight: 800;
  color: #aeff91;
  letter-spacing: -1px;
}

.lp-price-currency, .pricing-price .price-currency {
  font-size: 1.2rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 6px;
}

.lp-price-amount, .pricing-price .price-value {
  font-size: 3.6rem;
  font-weight: 800;
  color: #f8fafc;
  letter-spacing: -2px;
  line-height: 1;
}

.lp-price-period, .pricing-price .price-period {
  font-size: 1rem;
  font-weight: 500;
  color: #64748b;
  margin-bottom: 6px;
}

.lp-pricing-divider {
  height: 1px;
  background: rgba(148, 163, 184, 0.08);
  margin: 24px 0;
}

.lp-pricing-features {
  list-style: none;
  padding: 0;
  margin: 0 0 28px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}

.lp-pricing-features li {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.875rem;
  color: #94a3b8;
}

.lp-check {
  color: #aeff91;
  font-size: 0.75rem;
  width: 18px;
  height: 18px;
  background: rgba(174, 255, 145, 0.12);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.lp-check--gold {
  color: #fbbf24;
  background: rgba(251, 191, 36, 0.12);
}

.lp-btn-plan {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 13px;
  border-radius: 14px;
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  background: rgba(174, 255, 145, 0.1);
  border: 1px solid rgba(174, 255, 145, 0.25);
  color: #aeff91;
}

.lp-btn-plan:hover {
  background: rgba(174, 255, 145, 0.18);
  border-color: rgba(174, 255, 145, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(174, 255, 145, 0.2);
}

.lp-pricing-card--popular .lp-btn-plan {
  background: linear-gradient(135deg, #aeff91, #7de86a);
  border-color: transparent;
  color: #0b1120;
  box-shadow: 0 0 20px rgba(174, 255, 145, 0.3);
}

.lp-pricing-card--popular .lp-btn-plan:hover {
  box-shadow: 0 8px 30px rgba(174, 255, 145, 0.5);
}

/* === CTA === */
.lp-cta {
  padding: 100px 0;
}

.lp-cta-card {
  background: linear-gradient(135deg, rgba(11, 13, 11, 0.95), rgba(11, 13, 11, 0.85));
  border: 1px solid rgba(174, 255, 145, 0.2);
  border-radius: 28px;
  padding: 80px 40px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.lp-cta-glow {
  position: absolute;
  width: 500px;
  height: 500px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, rgba(174, 255, 145, 0.06) 0%, transparent 70%);
  pointer-events: none;
}

.lp-cta-card h2 {
  font-size: 2.5rem;
  font-weight: 800;
  color: #f8fafc;
  margin-bottom: 14px;
  letter-spacing: -0.8px;
}

.lp-cta-card p {
  font-size: 1.05rem;
  color: #64748b;
  margin-bottom: 36px;
}

/* === Footer === */
.lp-footer {
  padding: 32px 0;
  border-top: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(9, 9, 10, 0.8);
}

.lp-footer-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.lp-footer-copy {
  font-size: 0.8rem;
  color: #475569;
}

/* === Responsive === */
@media (max-width: 900px) {
  .lp-features-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .lp-stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }

  .lp-nav-links {
    display: none;
  }
}

/* === VPM Calculator === */
.lp-vpm-calc {
  margin-top: 80px;
  text-align: center;
}

.lp-vpm-calc-header {
  margin-bottom: 32px;
}

.lp-vpm-calc-title {
  font-size: 2rem;
  font-weight: 800;
  color: #f8fafc;
  letter-spacing: -0.6px;
  margin-bottom: 10px;
}

.lp-vpm-calc-sub {
  font-size: 0.9rem;
  color: #64748b;
}

.lp-vpm-calc-card {
  background: rgba(11, 13, 11, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 24px;
  padding: 40px 48px;
  max-width: 720px;
  margin: 0 auto;
  backdrop-filter: blur(12px);
}

.lp-vpm-calc-body {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 32px;
  margin-bottom: 36px;
}

.lp-vpm-calc-left {
  flex: 1;
  text-align: left;
  background: #fff;
  border-radius: 16px;
  padding: 20px 24px;
}

.lp-vpm-calc-label {
  display: block;
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 8px;
  font-weight: 500;
}

.lp-vpm-calc-label b {
  color: #aeff91;
  font-weight: 700;
}

.lp-vpm-calc-number {
  font-size: 2.4rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -1px;
  line-height: 1;
}

.lp-vpm-calc-equals {
  font-size: 2.4rem;
  font-weight: 300;
  color: #334155;
  flex-shrink: 0;
}

.lp-vpm-calc-right {
  flex: 1;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.lp-vpm-calc-price {
  font-size: 3rem;
  font-weight: 900;
  color: #aeff91;
  letter-spacing: -2px;
  line-height: 1;
}

.lp-vpm-calc-plan-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.lp-vpm-calc-rate-badge {
  font-size: 0.78rem;
  font-weight: 600;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.08);
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-radius: 999px;
  padding: 2px 10px;
  margin-top: 4px;
  display: inline-block;
}

.lp-vpm-calc-slider-wrap {
  margin-bottom: 24px;
}

.lp-vpm-calc-range {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(148, 163, 184, 0.2);
  border-radius: 999px;
  outline: none;
  cursor: pointer;
  margin-bottom: 14px;
}

.lp-vpm-calc-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #0f172a;
  border: 3px solid #aeff91;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(174, 255, 145, 0.4);
  transition: box-shadow 0.15s;
}

.lp-vpm-calc-range::-webkit-slider-thumb:hover {
  box-shadow: 0 0 18px rgba(174, 255, 145, 0.7);
}

.lp-vpm-calc-ticks {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
  color: #475569;
  font-weight: 500;
  padding: 0 2px;
}

.lp-vpm-calc-footer {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

.lp-vpm-calc-cta {
  width: 100%;
  max-width: 320px;
  justify-content: center;
  font-size: 0.95rem;
  padding: 12px 24px;
}

.lp-btn-plan--enterprise {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-color: #f59e0b;
}
.lp-btn-plan--enterprise:hover {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
}

.lp-vpm-calc-link {
  background: none;
  border: none;
  color: #aeff91;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 3px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: opacity 0.15s;
}

.lp-vpm-calc-link:hover { opacity: 0.75; }

/* === Modal Tabela de Pre�os === */
.lp-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(6px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.lp-modal {
  background: #0f172a;
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 20px;
  width: 100%;
  max-width: 560px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.lp-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.lp-modal-header h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #f8fafc;
}

.lp-modal-close {
  background: rgba(148, 163, 184, 0.1);
  border: none;
  color: #94a3b8;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}

.lp-modal-close:hover { background: rgba(148, 163, 184, 0.2); color: #f8fafc; }

.lp-modal-body {
  overflow-y: auto;
  padding: 0;
}

.lp-price-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.lp-price-table thead tr {
  background: rgba(148, 163, 184, 0.06);
}

.lp-price-table th {
  padding: 12px 20px;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #64748b;
}

.lp-price-table td {
  padding: 14px 20px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  color: #cbd5e1;
  font-size: 0.88rem;
}

.lp-price-table tbody tr:hover td { background: rgba(148, 163, 184, 0.04); }

.lp-price-table-val {
  font-weight: 700;
  color: #aeff91 !important;
}

.lp-price-table-per {
  color: #fbbf24 !important;
}

.lp-price-table-extra td {
  opacity: 0.6;
  font-style: italic;
  font-size: 0.82rem;
}

@media (max-width: 640px) {
  .lp-hero-title {
    font-size: 2.4rem;
  }

  .lp-hero-subtitle {
    font-size: 1rem;
  }

  .lp-section-title {
    font-size: 1.8rem;
  }

  .lp-features-grid {
    grid-template-columns: 1fr;
  }

  .lp-stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .lp-hero-cta {
    flex-direction: column;
    align-items: center;
  }

  .lp-cta-card {
    padding: 50px 24px;
  }

  .lp-cta-card h2 {
    font-size: 1.8rem;
  }

  .lp-footer-content {
    flex-direction: column;
    text-align: center;
  }
}
</style>
