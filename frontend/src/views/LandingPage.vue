<template>
  <div class="landing-page">
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
          <a href="#recursos" @click.prevent="scrollTo('recursos')">Recursos</a>
          <a href="#planos" @click.prevent="scrollTo('planos')">Planos</a>
          <a href="#faq" @click.prevent="scrollTo('faq')">FAQ</a>
          <a href="#contato" @click.prevent="scrollTo('contato')">Contato</a>
        </nav>
        <div class="lp-nav-actions">
          <router-link to="/login" class="lp-btn lp-btn-primary">
            <i class="fas fa-sign-in-alt"></i> Entrar
          </router-link>
        </div>
        <button class="lp-menu-toggle" @click="mobileMenuOpen = !mobileMenuOpen" aria-label="Menu">
          <i :class="mobileMenuOpen ? 'fas fa-times' : 'fas fa-bars'"></i>
        </button>
      </div>
    </header>

    <!-- Mobile Menu -->
    <Transition name="lp-slide">
      <div v-if="mobileMenuOpen" class="lp-mobile-menu">
        <a href="#recursos" @click.prevent="scrollTo('recursos')" class="lp-mobile-link">Recursos</a>
        <a href="#planos" @click.prevent="scrollTo('planos')" class="lp-mobile-link">Planos</a>
        <a href="#faq" @click.prevent="scrollTo('faq')" class="lp-mobile-link">FAQ</a>
        <a href="#contato" @click.prevent="scrollTo('contato')" class="lp-mobile-link">Contato</a>
        <div class="lp-mobile-menu-divider"></div>
        <router-link to="/login" class="lp-btn lp-btn-primary lp-mobile-cta" @click="mobileMenuOpen = false">
          <i class="fas fa-sign-in-alt"></i> Entrar
        </router-link>
      </div>
    </Transition>

    <!-- Hero Section -->
    <section class="lp-hero">
      <div class="lp-container">
        <div class="lp-badge">
          <span class="lp-badge-dot"></span>
          Automação no Telegram — o canal com mais engajamento do mundo
        </div>
        <h1 class="lp-hero-title">
          Mais conversas.<br>
          Mais clientes.<br>
          <span class="lp-highlight">Com Blackchat Pro.</span>
        </h1>
        <p class="lp-hero-subtitle">
          Crie fluxos inteligentes no Telegram, engaje sua base 24h por dia
          e converta mais — sem esforço manual.
        </p>
        <div class="lp-hero-cta">
          <router-link to="/register" class="lp-btn lp-btn-primary lp-btn-lg">
            <i class="fas fa-rocket"></i> Comece agora mesmo
          </router-link>
          <router-link to="/login" class="lp-btn lp-btn-outline lp-btn-lg">
            <i class="fas fa-sign-in-alt"></i> Já tenho conta
          </router-link>
        </div>
        <p class="lp-hero-footnote">14 dias gratuitos · Sem cartão de crédito · Cancele quando quiser</p>
      </div>
    </section>

    <!-- Features Section -->
    <section class="lp-features" id="recursos">
      <div class="lp-container">
        <div class="lp-section-label">Recursos</div>
        <h2 class="lp-section-title">Tudo que você precisa para escalar</h2>
        <p class="lp-section-subtitle">Uma plataforma focada em resultado — do primeiro contato à conversão.</p>
        <div class="lp-features-grid">
          <div
            class="lp-feature-card"
            v-for="feature in features"
            :key="feature.title"
            :class="{ 'lp-feature-card--soon': feature.soon }"
          >
            <div v-if="feature.soon" class="lp-soon-badge">Em Breve</div>
            <div class="lp-feature-icon" :style="{ background: feature.iconBg }">
              <i :class="feature.icon" :style="{ color: feature.iconColor || 'inherit' }"></i>
            </div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
            <a
              v-if="feature.soon"
              href="#contato"
              @click.prevent="scrollTo('contato')"
              class="lp-feature-soon-link"
            >
              Quero ser avisado <i class="fas fa-arrow-right"></i>
            </a>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonial -->
    <!-- Social Proof + Métricas -->
    <section class="bc-proof-section" ref="proofSection">
      <div class="lp-container">

        <!-- Header -->
        <div class="bc-proof-header">
          <div class="lp-section-label">Resultados reais</div>
          <h2 class="bc-proof-title">
            Quem usa o Blackchat Pro<br>
            <span class="lp-highlight">transforma o Telegram em máquina de conversão</span>
          </h2>
          <p class="bc-proof-subtitle">
            Automação de fluxo, qualificação inteligente e atendimento X1 no momento certo —
            tudo dentro do Telegram, com menos custo e mais escala.
          </p>
        </div>

        <!-- Depoimentos -->
        <div class="bc-proof-grid">
          <div
            v-for="(t, i) in testimonials"
            :key="i"
            class="bc-proof-quote"
            :class="{ 'bc-proof-quote--visible': proofVisible }"
            :style="{ transitionDelay: `${i * 120}ms` }"
          >
            <div class="bc-proof-quote-top">
              <div class="bc-proof-stars">
                <i class="fas fa-star" v-for="s in 5" :key="s"></i>
              </div>
              <span class="bc-proof-segment">{{ t.segment }}</span>
            </div>
            <p class="bc-proof-text">{{ t.quote }}</p>
            <div class="bc-proof-author">
              <div class="bc-proof-avatar">
                <i :class="t.icon"></i>
              </div>
              <div>
                <strong>{{ t.name }}</strong>
                <span>{{ t.role }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Cards de Métricas -->
        <div class="bc-proof-metrics">
          <div
            v-for="(m, i) in metrics"
            :key="i"
            class="bc-proof-metric"
            :class="{ 'bc-proof-metric--visible': proofVisible }"
            :style="{ transitionDelay: `${360 + i * 100}ms` }"
          >
            <div class="bc-proof-metric-icon" :style="{ color: m.color, background: m.bg }">
              <i :class="m.icon"></i>
            </div>
            <h4 class="bc-proof-metric-title">{{ m.title }}</h4>
            <p class="bc-proof-metric-desc">{{ m.desc }}</p>
          </div>
        </div>

        <!-- Microcopy -->
        <p class="bc-proof-microcopy">
          <i class="fas fa-check-circle"></i> Menos custo operacional.
          <i class="fas fa-check-circle"></i> Mais controle do funil.
          <i class="fas fa-check-circle"></i> Mais velocidade para vender no Telegram.
        </p>

      </div>
    </section>

    <!-- Pricing Section -->
    <section class="lp-pricing" id="planos">
      <div class="lp-container">
        <div class="lp-section-label">Planos</div>
        <h2 class="lp-section-title">Preços transparentes e flexíveis</h2>
        <p class="lp-section-subtitle">Pague pelos contatos que você engaja. Sem fidelidade, cancele quando quiser.</p>

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
              <div class="lp-pricing-plan-icon" :class="`lp-plan-icon--${plan.name}`">
                <i :class="planIcon(plan.name)"></i>
              </div>
              <h3 class="lp-pricing-name">{{ plan.display_name }}</h3>
              <p class="lp-pricing-desc">{{ planDescription(plan.name) }}</p>

              <!-- Gratuito -->
              <div v-if="plan.name === 'free'" class="pricing-price pricing-inline lp-price-block">
                <span class="price-value lp-free-label">R$ 0</span>
                <span class="price-period">/mês</span>
              </div>

              <!-- Pro -->
              <div v-else-if="plan.name === 'pro'" class="pricing-price pricing-inline lp-price-block">
                <span class="price-currency">R$</span>
                <span class="price-value">99<small class="price-cents">,90</small></span>
                <span class="price-period">/mês</span>
                <div class="pricing-pro-contacts">até 2.500 contatos ativos</div>
              </div>

              <!-- Enterprise -->
              <div v-else-if="plan.name === 'unlimited'" class="pricing-price pricing-vpm lp-price-block">
                <div class="pricing-vpm-from">cobrado por volume</div>
                <div class="pricing-ent-main">Enterprise</div>
                <div class="pricing-vpm-unit">por 1.000 contatos ativos</div>
                <div class="pricing-vpm-min">
                  <span class="pricing-vpm-min-label">A partir de</span>
                  <span class="pricing-vpm-min-currency">R$</span>
                  <span class="pricing-vpm-min-value">999,90</span>
                  <span class="pricing-vpm-min-period">/mês</span>
                </div>
              </div>

              <!-- VPM genérico -->
              <div v-else-if="plan.vpm_price" class="pricing-price pricing-vpm lp-price-block">
                <div class="pricing-vpm-from">a partir de</div>
                <div class="pricing-vpm-main">
                  <span class="price-currency">R$</span>
                  <span class="price-value">{{ formatPriceNumber(plan.vpm_price) }}</span>
                </div>
                <div class="pricing-vpm-unit">por 1.000 contatos ativos</div>
                <div v-if="plan.min_monthly" class="pricing-vpm-min">
                  <span class="pricing-vpm-min-label">A partir de</span>
                  <span class="pricing-vpm-min-currency">R$</span>
                  <span class="pricing-vpm-min-value">{{ formatPriceNumber(plan.min_monthly) }}</span>
                  <span class="pricing-vpm-min-period">/mês</span>
                </div>
              </div>
            </div>

            <div class="lp-pricing-divider" style="margin-top: auto;"></div>

            <ul class="lp-pricing-features">
              <template v-if="plan.name === 'free'">
                <li class="feat-yes"><i class="fas fa-check lp-check"></i><span>1 Bot no Telegram</span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check"></i><span>Até 100 contatos ativos</span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check"></i><span>1 Fluxo de automação</span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check"></i><span>1 Gatilho de entrada</span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check"></i><span>1 Sequência de mensagens</span></li>
                <li class="feat-no"><i class="fas fa-times lp-check lp-check--no"></i><span>Broadcast para lista</span></li>
                <li class="feat-no"><i class="fas fa-times lp-check lp-check--no"></i><span>Analytics avançado</span></li>
                <li class="feat-no"><i class="fas fa-times lp-check lp-check--no"></i><span>Colaboradores</span></li>
              </template>
              <template v-else-if="plan.name === 'pro'">
                <li class="feat-yes"><i class="fas fa-check lp-check"></i><span>3 Bots no Telegram</span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check"></i><span>Até <b>2.500 contatos ativos</b></span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check"></i><span>Fluxos ilimitados</span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check"></i><span>Gatilhos ilimitados</span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check"></i><span>Sequências ilimitadas</span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check"></i><span>Broadcast para lista</span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check"></i><span>Analytics avançado</span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check"></i><span>3 Colaboradores</span></li>
              </template>
              <template v-else-if="plan.name === 'unlimited'">
                <li class="feat-yes"><i class="fas fa-check lp-check lp-check--gold"></i><span><b>Bots ilimitados</b></span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check lp-check--gold"></i><span><b>Contatos ilimitados</b></span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check lp-check--gold"></i><span>Fluxos ilimitados</span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check lp-check--gold"></i><span>Gatilhos ilimitados</span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check lp-check--gold"></i><span>Sequências ilimitadas</span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check lp-check--gold"></i><span>Broadcast ilimitado</span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check lp-check--gold"></i><span>Analytics avançado</span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check lp-check--gold"></i><span><b>Administradores ilimitados</b></span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check lp-check--gold"></i><span>Suporte prioritário 24/7</span></li>
                <li class="feat-yes"><i class="fas fa-check lp-check lp-check--gold"></i><span>API + Webhooks</span></li>
              </template>
            </ul>

            <router-link
              v-if="plan.name === 'free'"
              :to="`/register?plan=${plan.name}`"
              class="lp-btn-plan lp-btn-plan--free"
            >
              Começar Agora <i class="fas fa-arrow-right"></i>
            </router-link>
            <router-link
              v-else-if="plan.name === 'pro'"
              :to="`/register?plan=${plan.name}`"
              class="lp-btn-plan lp-btn-plan--pro"
            >
              Assinar Pro <i class="fas fa-arrow-right"></i>
            </router-link>
            <a
              v-else
              href="#lp-enterprise-calc"
              @click.prevent="scrollTo('lp-enterprise-calc')"
              class="lp-btn-plan lp-btn-plan--enterprise"
            >
              Ver Preços Enterprise <i class="fas fa-calculator"></i>
            </a>
          </div>
        </div>

        <!-- Enterprise Destaque -->
        <div class="lp-enterprise-highlight">
          <div class="lp-enterprise-highlight-inner">
            <div class="lp-enterprise-left">
              <div class="lp-enterprise-icon">
                <i class="fas fa-crown"></i>
              </div>
              <div>
                <h3>Enterprise — Para grandes volumes</h3>
                <p>Bots, contatos, fluxos e usuários ilimitados. Suporte 24/7 e acesso à API.</p>
                <div class="lp-enterprise-features-row">
                  <span><i class="fas fa-check"></i> Bots ilimitados</span>
                  <span><i class="fas fa-check"></i> API + Webhooks</span>
                  <span><i class="fas fa-check"></i> Suporte 24/7</span>
                  <span><i class="fas fa-check"></i> Admins ilimitados</span>
                  <span><i class="fas fa-times lp-x-no"></i> Limite de contatos</span>
                  <span><i class="fas fa-times lp-x-no"></i> Limite de fluxos</span>
                </div>
              </div>
            </div>
            <div class="lp-enterprise-right">
              <div class="lp-enterprise-price">
                <span class="lp-enterprise-from">A partir de</span>
                <span class="lp-enterprise-value">R$ 999,90<small>/mês</small></span>
              </div>
              <a
                href="#lp-enterprise-calc"
                @click.prevent="scrollTo('lp-enterprise-calc')"
                class="lp-btn-plan lp-btn-plan--enterprise lp-enterprise-cta"
              >
                Calcular meu plano <i class="fas fa-arrow-right"></i>
              </a>
            </div>
          </div>
        </div>

        <!-- Calculadora -->
        <div class="lp-vpm-calc" id="lp-enterprise-calc">
          <div class="lp-vpm-calc-header">
            <h3 class="lp-vpm-calc-title">Calcule sua economia</h3>
            <p class="lp-vpm-calc-sub">Arraste o slider e veja quanto você paga no Blackchat Pro — e quanto economiza em comparação com o mercado.</p>
          </div>

          <div class="lp-vpm-calc-card">

            <!-- Slider -->
            <div class="lp-calc-slider-section">
              <label class="lp-calc-slider-label">
                Volume de contatos por mês
              </label>
              <div class="lp-calc-contacts-display">
                <span class="lp-calc-contacts-number">{{ calcContacts.toLocaleString('pt-BR') }}</span>
                <span class="lp-calc-contacts-unit">contatos</span>
              </div>
              <input
                type="range"
                class="lp-vpm-calc-range"
                min="0" max="100" step="1"
                v-model.number="calcSlider"
              />
              <div class="lp-vpm-calc-ticks">
                <span>500</span><span>10k</span><span>100k</span><span>500k</span><span>2M</span>
              </div>
            </div>

            <!-- Divider -->
            <div class="lp-calc-divider"></div>

            <!-- Comparativo de preço -->
            <div class="lp-calc-result">

              <div class="lp-calc-compare-row">
                <!-- Mercado -->
                <div class="lp-calc-compare-col lp-calc-compare-col--market">
                  <span class="lp-calc-compare-label">Outros planos do mercado</span>
                  <div class="lp-calc-compare-price lp-calc-compare-price--strike">
                    <span class="lp-calc-compare-currency">R$</span>
                    <span class="lp-calc-compare-value">{{ formatPriceNumber(calcCompetitorPrice) }}</span>
                    <span class="lp-calc-compare-period">/mês</span>
                  </div>
                  <span class="lp-calc-compare-note">estimativa de mercado</span>
                </div>

                <!-- Seta -->
                <div class="lp-calc-compare-arrow">
                  <i class="fas fa-arrow-right"></i>
                </div>

                <!-- Blackchat Pro -->
                <div class="lp-calc-compare-col lp-calc-compare-col--bcp">
                  <span class="lp-calc-compare-label">Com o Blackchat Pro</span>
                  <div class="lp-calc-compare-price lp-calc-compare-price--bcp">
                    <span class="lp-calc-compare-currency">R$</span>
                    <span class="lp-calc-compare-value">{{ formatPriceNumber(calcPrice) }}</span>
                    <span class="lp-calc-compare-period">/mês</span>
                  </div>
                  <span class="lp-calc-compare-tag">Plano {{ calcPlanLabel }}</span>
                </div>
              </div>

              <!-- Banner de economia -->
              <div class="lp-calc-savings-banner">
                <div class="lp-calc-savings-icon"><i class="fas fa-piggy-bank"></i></div>
                <div class="lp-calc-savings-text">
                  <span class="lp-calc-savings-headline">
                    Você economiza <strong>R$&nbsp;{{ formatPriceNumber(calcSavings) }}/mês</strong>
                  </span>
                  <span class="lp-calc-savings-sub">40% mais barato que as alternativas do mercado</span>
                </div>
              </div>

            </div>

            <!-- Footer -->
            <div class="lp-calc-footer">
              <button class="lp-vpm-calc-link" @click="showPriceTable = true">
                <i class="fas fa-table"></i> Ver tabela de preços completa
              </button>
              <router-link
                :to="`/register?plan=${calcPlanLabel === 'Enterprise' ? 'unlimited' : 'pro'}&contacts=${calcContacts}`"
                class="lp-btn lp-btn-primary lp-vpm-calc-cta"
              >
                <i class="fas fa-rocket"></i> Começar agora
              </router-link>
            </div>

          </div>
        </div>

        <!-- Modal Tabela de Preços -->
        <Teleport to="body">
          <div v-if="showPriceTable" class="lp-modal-overlay" @click.self="showPriceTable = false">
            <div class="lp-modal">
              <div class="lp-modal-header">
                <h3>Tabela de Preços</h3>
                <button class="lp-modal-close" @click="showPriceTable = false"><i class="fas fa-times"></i></button>
              </div>
              <div class="lp-modal-body">
                <table class="lp-price-table">
                  <thead>
                    <tr>
                      <th>Máx. de contatos</th>
                      <th>Preço por mês</th>
                      <th>Preço por 1K</th>
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

    <!-- FAQ -->
    <section class="lp-faq" id="faq">
      <div class="lp-container">
        <div class="lp-section-label">FAQ</div>
        <h2 class="lp-section-title">Dúvidas frequentes</h2>
        <div class="lp-faq-list">
          <div
            v-for="(item, i) in faqItems"
            :key="i"
            class="lp-faq-item"
            :class="{ 'lp-faq-item--open': openFaq === i }"
          >
            <button class="lp-faq-question" @click="openFaq = openFaq === i ? null : i">
              <span>{{ item.q }}</span>
              <i :class="openFaq === i ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
            </button>
            <Transition name="faq-expand">
              <div v-if="openFaq === i" class="lp-faq-answer">{{ item.a }}</div>
            </Transition>
          </div>
        </div>
      </div>
    </section>

    <!-- Contato / CTA Final -->
    <section class="lp-cta" id="contato">
      <div class="lp-container">
        <div class="lp-cta-card">
          <div class="lp-cta-glow"></div>
          <div class="lp-section-label" style="margin-bottom: 20px;">Contato</div>
          <h2>Pronto para automatizar suas conversas?</h2>
          <p>Junte-se a centenas de empresas que já confiam no Blackchat Pro para crescer no Telegram.</p>
          <div class="lp-cta-actions">
            <router-link to="/register" class="lp-btn lp-btn-primary lp-btn-lg">
              <i class="fas fa-rocket"></i> Começar Agora
            </router-link>
            <a href="mailto:contato@blackchatpro.com.br" class="lp-btn lp-btn-outline lp-btn-lg">
              <i class="fas fa-envelope"></i> Falar com a equipe
            </a>
          </div>
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
          <p class="lp-footer-copy">© 2026 Blackchat Pro. Todos os direitos reservados.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api/http.js'

const plans = ref([])
const loading = ref(true)
const mobileMenuOpen = ref(false)
const openFaq = ref(null)

// Social proof
const proofSection = ref(null)
const proofVisible = ref(false)

const testimonials = [
  {
    segment: 'Infoprodutos',
    quote: '"Antes perdíamos lead no meio do caminho porque dependíamos de resposta manual. Com os fluxos do Blackchat Pro, o lead entra, se qualifica automaticamente, recebe o conteúdo na sequência certa e só chega para o X1 quando está realmente pronto para comprar."',
    name: 'Camila Torres',
    role: 'Produtora de conteúdo digital',
    icon: 'fas fa-user',
  },
  {
    segment: 'Comunidade & Mentoria',
    quote: '"O Telegram virou nossa operação central de aquisição. O lead entra no canal, avança pelos fluxos de automação e nossa equipe só entra em cena nos momentos estratégicos. Ficou muito mais organizado — e a taxa de conversão subiu junto."',
    name: 'Diego Fonseca',
    role: 'Mentor de negócios digitais',
    icon: 'fas fa-user',
  },
  {
    segment: 'Captação de Leads',
    quote: '"A virada foi conectar automação com atendimento humano no ponto certo. O sistema aquece o lead, filtra o interesse real e entrega para o time já no momento de decisão. Gastamos menos com ferramenta e operamos com muito mais eficiência."',
    name: 'Renata Alves',
    role: 'Head de Vendas, agência B2B',
    icon: 'fas fa-user',
  },
]

const metrics = [
  {
    icon: 'fas fa-network-wired',
    title: 'Fluxos prontos para rodar',
    desc: 'Capte, qualifique e avance leads automaticamente dentro do Telegram — sem esforço manual e sem perder ninguém no caminho.',
    color: '#00FF66',
    bg: 'rgba(0, 255, 102, 0.08)',
  },
  {
    icon: 'fas fa-crosshairs',
    title: 'X1 no momento certo',
    desc: 'Direcione o atendimento humano apenas para leads mais quentes. Sua equipe foca em quem já está pronto para avançar.',
    color: '#38bdf8',
    bg: 'rgba(56, 189, 248, 0.08)',
  },
  {
    icon: 'fas fa-piggy-bank',
    title: 'Até 40% mais economia',
    desc: 'Estruture sua operação com mais eficiência e pague menos que as soluções similares do mercado. Sem abrir mão de nenhum recurso.',
    color: '#fbbf24',
    bg: 'rgba(251, 191, 36, 0.08)',
  },
]

const scrollTo = (id) => {
  mobileMenuOpen.value = false
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

// Calculadora VPM
const calcSlider = ref(30)
const showPriceTable = ref(false)
const PRO_MIN = 99.90
const ENT_MIN = 999.90

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

const getPrice = (contacts) => {
  if (contacts <= 0) return 0
  const last = PRICE_TABLE[PRICE_TABLE.length - 1]
  if (contacts >= last.contacts) {
    return last.price + Math.ceil((contacts - last.contacts) / 1000) * 34.30
  }
  const first = PRICE_TABLE[0]
  if (contacts <= first.contacts) {
    return first.price * (contacts / first.contacts)
  }
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


const calcContacts = computed(() =>
  Math.round(500 * Math.pow(4000, calcSlider.value / 100))
)

const calcPrice = computed(() => Math.max(getPrice(calcContacts.value), PRO_MIN))

const calcPlanLabel = computed(() =>
  calcPrice.value >= ENT_MIN ? 'Enterprise' : 'Pro'
)

// Preço de mercado = Blackchat Pro + 40%
const calcCompetitorPrice = computed(() => calcPrice.value * 1.4)
const calcSavings = computed(() => calcPrice.value * 0.4)

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
    description: 'Automação completa no Telegram — o canal com maior taxa de abertura do mundo.',
    icon: 'fab fa-telegram',
    iconBg: 'rgba(14, 165, 233, 0.12)',
    iconColor: '#0ea5e9',
  },
  {
    title: 'Fluxos Visuais',
    description: 'Editor drag-and-drop intuitivo para criar automações complexas sem escrever código.',
    icon: 'fas fa-project-diagram',
    iconBg: 'rgba(0, 255, 102, 0.12)',
    iconColor: '#00FF66',
  },
  {
    title: 'Automação 24/7',
    description: 'Respostas instantâneas a qualquer hora do dia, mesmo enquanto você dorme.',
    icon: 'fas fa-bolt',
    iconBg: 'rgba(251, 191, 36, 0.12)',
    iconColor: '#fbbf24',
  },
  {
    title: 'Analytics em Tempo Real',
    description: 'Métricas detalhadas para entender seu público e otimizar cada campanha.',
    icon: 'fas fa-chart-line',
    iconBg: 'rgba(168, 85, 247, 0.12)',
    iconColor: '#a855f7',
  },
  {
    title: 'Broadcast Inteligente',
    description: 'Envie campanhas segmentadas para sua base de contatos com um clique.',
    icon: 'fas fa-bullhorn',
    iconBg: 'rgba(239, 68, 68, 0.12)',
    iconColor: '#ef4444',
  },
  {
    title: 'API & Webhooks',
    description: 'Integração com seus sistemas via API REST e webhooks — em desenvolvimento.',
    icon: 'fas fa-plug',
    iconBg: 'rgba(251, 191, 36, 0.08)',
    iconColor: '#fbbf24',
    soon: true,
  },
]

const faqItems = [
  {
    q: 'Preciso de cartão de crédito para testar?',
    a: 'Não. O período de teste de 14 dias é completamente gratuito e não exige cartão de crédito. Você só precisa cadastrar um método de pagamento ao escolher um plano pago.',
  },
  {
    q: 'O que é um "contato ativo"?',
    a: 'Um contato ativo é qualquer usuário que interagiu com o seu bot no Telegram nos últimos 30 dias. Contatos inativos não são cobrados.',
  },
  {
    q: 'Posso cancelar a qualquer momento?',
    a: 'Sim. Não há fidelidade. Você pode cancelar sua assinatura a qualquer momento diretamente pelo painel, sem multas ou burocracia.',
  },
  {
    q: 'O Blackchat Pro funciona com WhatsApp?',
    a: 'No momento, a plataforma é focada exclusivamente no Telegram. Integrações com outros canais estão no nosso roadmap.',
  },
  {
    q: 'Posso mudar de plano depois?',
    a: 'Sim. Você pode fazer upgrade ou downgrade do seu plano a qualquer momento. A cobrança é proporcional ao período utilizado.',
  },
]

const planIcon = (name) => {
  const icons = { free: 'fas fa-seedling', pro: 'fas fa-rocket', unlimited: 'fas fa-crown' }
  return icons[name] || 'fas fa-layer-group'
}

const planDescription = (name) => {
  const descs = {
    free: 'Para testar a plataforma',
    pro: 'Plano fixo — até 2.500 contatos',
    unlimited: 'Para grandes volumes, cobrado por contatos',
  }
  return descs[name] || 'Plano completo'
}

const loadPlans = async () => {
  try {
    const response = await api.get('/api/v1/public/plans/')
    plans.value = response.data
  } catch (error) {
    console.error('Erro ao carregar planos:', error)
  } finally {
    loading.value = false
  }
}

const formatPriceNumber = (value) => {
  const n = Number(value)
  if (!Number.isFinite(n)) return ''
  const isInt = Math.abs(n - Math.round(n)) < 1e-9
  return n.toLocaleString('pt-BR', {
    minimumFractionDigits: isInt ? 0 : 2,
    maximumFractionDigits: isInt ? 0 : 2,
  })
}

onMounted(() => {
  loadPlans()

  const observer = new IntersectionObserver(
    ([entry]) => { if (entry.isIntersecting) { proofVisible.value = true; observer.disconnect() } },
    { threshold: 0.15 }
  )
  if (proofSection.value) observer.observe(proofSection.value)
})
</script>

<style scoped>
/* ============================================================
   LANDING PAGE
   ============================================================ */

.landing-page {
  min-height: 100vh;
  background: #060606;
  position: relative;
  overflow-x: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, sans-serif;
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
  width: 700px; height: 700px;
  top: -200px; left: -200px;
  background: radial-gradient(circle, rgba(0, 255, 102, 0.08) 0%, transparent 70%);
}

.bg-glow-2 {
  width: 600px; height: 600px;
  bottom: -150px; right: -150px;
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
  background: rgba(6, 6, 6, 0.9);
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
  flex-shrink: 0;
}

.lp-logo-mark {
  width: 36px; height: 36px;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lp-logo-mark img {
  width: 100%; height: 100%;
  object-fit: contain;
}

.lp-logo-text {
  font-weight: 700;
  font-size: 1.05rem;
  color: #f8fafc;
  letter-spacing: -0.3px;
}

.lp-nav-links {
  display: flex;
  gap: 2px;
  flex: 1;
}

.lp-nav-links a {
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #64748b;
  text-decoration: none;
  transition: all 0.15s ease;
  font-weight: 500;
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
  background: linear-gradient(135deg, #00FF66, #00cc52);
  color: #060606;
  box-shadow: 0 0 20px rgba(0, 255, 102, 0.3);
}

.lp-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 35px rgba(0, 255, 102, 0.5);
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
  padding: 120px 0 80px;
  text-align: center;
}

.lp-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  background: rgba(0, 255, 102, 0.07);
  border: 1px solid rgba(0, 255, 102, 0.18);
  border-radius: 999px;
  font-size: 0.8rem;
  color: #00FF66;
  font-weight: 500;
  margin-bottom: 32px;
  letter-spacing: 0.2px;
}

.lp-badge-dot {
  width: 7px; height: 7px;
  background: #00FF66;
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(0, 255, 102, 0.8);
  animation: pulse-dot 2s infinite;
  flex-shrink: 0;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.lp-hero-title {
  font-size: 4rem;
  font-weight: 800;
  line-height: 1.1;
  color: #f8fafc;
  margin: 0 auto 24px;
  max-width: 720px;
  letter-spacing: -2px;
}

.lp-highlight {
  background: linear-gradient(135deg, #00FF66 0%, #00cc52 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 0 30px rgba(0, 255, 102, 0.3));
}

.lp-hero-subtitle {
  font-size: 1.15rem;
  color: #64748b;
  max-width: 560px;
  margin: 0 auto 40px;
  line-height: 1.75;
  font-weight: 400;
}

.lp-hero-cta {
  display: flex;
  gap: 14px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.lp-hero-footnote {
  font-size: 0.78rem;
  color: #334155;
  letter-spacing: 0.3px;
  font-weight: 500;
}

/* === Section Styles === */
.lp-section-label {
  display: inline-block;
  padding: 4px 14px;
  background: rgba(0, 255, 102, 0.07);
  border: 1px solid rgba(0, 255, 102, 0.18);
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: #00FF66;
  margin-bottom: 16px;
}

.lp-section-title {
  font-size: 2.25rem;
  font-weight: 800;
  color: #f8fafc;
  margin-bottom: 12px;
  letter-spacing: -0.8px;
  line-height: 1.2;
}

.lp-section-subtitle {
  font-size: 1rem;
  color: #64748b;
  max-width: 500px;
  line-height: 1.65;
}

/* === Features === */
.lp-features {
  padding: 100px 0;
}

.lp-features .lp-section-subtitle {
  margin-bottom: 60px;
}

.lp-features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 56px;
}

.lp-feature-card {
  background: linear-gradient(135deg, rgba(18, 18, 18, 0.9), rgba(18, 18, 18, 0.7));
  border: 1px solid rgba(148, 163, 184, 0.08);
  border-radius: 20px;
  padding: 28px;
  transition: all 0.25s ease;
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}

.lp-feature-card:hover {
  transform: translateY(-4px);
  border-color: rgba(148, 163, 184, 0.18);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
}

.lp-feature-card--soon {
  border-color: rgba(251, 191, 36, 0.2);
  background: linear-gradient(135deg, rgba(18, 18, 18, 0.9), rgba(251, 191, 36, 0.04));
}

.lp-feature-card--soon:hover {
  border-color: rgba(251, 191, 36, 0.4);
}

.lp-soon-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  background: rgba(251, 191, 36, 0.12);
  border: 1px solid rgba(251, 191, 36, 0.3);
  color: #fbbf24;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  padding: 3px 10px;
  border-radius: 999px;
}

.lp-feature-icon {
  width: 52px; height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  margin-bottom: 18px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.lp-feature-card h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 10px;
  letter-spacing: -0.2px;
}

.lp-feature-card p {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.65;
  margin-bottom: 0;
}

.lp-feature-soon-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 16px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #fbbf24;
  text-decoration: none;
  transition: opacity 0.15s;
}

.lp-feature-soon-link:hover { opacity: 0.75; }

/* === Testimonial === */
/* ============================================================
   SOCIAL PROOF — bc-proof-
   ============================================================ */
.bc-proof-section {
  padding: 100px 0;
  border-top: 1px solid rgba(148, 163, 184, 0.06);
  border-bottom: 1px solid rgba(148, 163, 184, 0.06);
  background: rgba(8, 8, 8, 0.6);
  position: relative;
  overflow: hidden;
}

.bc-proof-section::before {
  content: '';
  position: absolute;
  top: 0; left: 50%;
  transform: translateX(-50%);
  width: 800px; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0, 255, 102, 0.15), transparent);
}

/* Header */
.bc-proof-header {
  text-align: center;
  margin-bottom: 64px;
}

.bc-proof-title {
  font-size: 2.25rem;
  font-weight: 800;
  color: #f8fafc;
  line-height: 1.2;
  letter-spacing: -0.8px;
  margin: 0 0 16px;
  max-width: 680px;
  margin-left: auto;
  margin-right: auto;
}

.bc-proof-subtitle {
  font-size: 1rem;
  color: #64748b;
  line-height: 1.7;
  max-width: 560px;
  margin: 0 auto;
}

/* Depoimentos */
.bc-proof-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 48px;
}

.bc-proof-quote {
  background: linear-gradient(150deg, rgba(18, 18, 18, 0.95), rgba(14, 14, 14, 0.85));
  border: 1px solid rgba(148, 163, 184, 0.09);
  border-radius: 20px;
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease,
              opacity 0.5s ease, translate 0.5s ease;
  opacity: 0;
  translate: 0 24px;
}

.bc-proof-quote--visible {
  opacity: 1;
  translate: 0 0;
}

.bc-proof-quote:hover {
  transform: translateY(-5px);
  border-color: rgba(0, 255, 102, 0.18);
  box-shadow: 0 20px 48px rgba(0, 0, 0, 0.35), 0 0 0 1px rgba(0, 255, 102, 0.07);
}

.bc-proof-quote-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.bc-proof-stars {
  display: flex;
  gap: 3px;
}

.bc-proof-stars i {
  font-size: 0.7rem;
  color: #fbbf24;
}

.bc-proof-segment {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #00FF66;
  background: rgba(0, 255, 102, 0.07);
  border: 1px solid rgba(0, 255, 102, 0.15);
  border-radius: 999px;
  padding: 3px 10px;
  white-space: nowrap;
}

.bc-proof-text {
  font-size: 0.9rem;
  color: #94a3b8;
  line-height: 1.75;
  font-style: italic;
  margin: 0;
  flex: 1;
}

.bc-proof-author {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid rgba(148, 163, 184, 0.07);
  margin-top: auto;
}

.bc-proof-avatar {
  width: 38px; height: 38px;
  border-radius: 50%;
  background: rgba(148, 163, 184, 0.08);
  border: 1px solid rgba(148, 163, 184, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  color: #64748b;
  flex-shrink: 0;
}

.bc-proof-author strong {
  display: block;
  font-size: 0.875rem;
  font-weight: 700;
  color: #e2e8f0;
}

.bc-proof-author span {
  display: block;
  font-size: 0.75rem;
  color: #475569;
  margin-top: 2px;
}

/* Cards de Métricas */
.bc-proof-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 36px;
}

.bc-proof-metric {
  background: rgba(14, 14, 14, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.08);
  border-radius: 16px;
  padding: 24px 24px 22px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease,
              opacity 0.5s ease, translate 0.5s ease;
  opacity: 0;
  translate: 0 20px;
}

.bc-proof-metric--visible {
  opacity: 1;
  translate: 0 0;
}

.bc-proof-metric:hover {
  transform: translateY(-4px);
  border-color: rgba(148, 163, 184, 0.16);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
}

.bc-proof-metric-icon {
  width: 44px; height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.15rem;
}

.bc-proof-metric-title {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -0.2px;
  margin: 0;
}

.bc-proof-metric-desc {
  font-size: 0.85rem;
  color: #64748b;
  line-height: 1.65;
  margin: 0;
}

/* Microcopy */
.bc-proof-microcopy {
  text-align: center;
  font-size: 0.82rem;
  font-weight: 600;
  color: #475569;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  flex-wrap: wrap;
}

.bc-proof-microcopy i {
  color: #00FF66;
  font-size: 0.72rem;
  margin-right: 5px;
}

/* Responsive */
@media (max-width: 900px) {
  .bc-proof-grid { grid-template-columns: 1fr; }
  .bc-proof-metrics { grid-template-columns: 1fr; }
  .bc-proof-title { font-size: 1.8rem; }
}

@media (max-width: 640px) {
  .bc-proof-section { padding: 72px 0; }
  .bc-proof-title { font-size: 1.6rem; }
  .bc-proof-microcopy { flex-direction: column; gap: 10px; }
}

/* === Pricing === */
.lp-pricing {
  padding: 100px 0;
}

.lp-pricing .lp-section-subtitle {
  margin-bottom: 60px;
}

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
  gap: 8px;
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
  color: #f1f5f9;
  line-height: 1.1;
}

.pricing-vpm-from {
  font-size: 0.7rem;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.pricing-vpm-main {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
  line-height: 1;
}

.pricing-vpm-unit {
  font-size: 0.82rem;
  color: #64748b;
  font-weight: 500;
}

.pricing-vpm-min {
  display: inline-flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
  padding: 7px 14px;
  border-radius: 999px;
  background: rgba(251, 191, 36, 0.08);
  border: 1px solid rgba(251, 191, 36, 0.2);
}

.pricing-vpm-min-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: rgba(251, 191, 36, 0.85);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.pricing-vpm-min-currency {
  font-size: 0.85rem;
  font-weight: 800;
  color: #fbbf24;
}

.pricing-vpm-min-value {
  font-size: 1.1rem;
  font-weight: 900;
  color: #fbbf24;
  letter-spacing: -0.02em;
}

.pricing-vpm-min-period {
  font-size: 0.8rem;
  font-weight: 600;
  color: #94a3b8;
}

.lp-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px;
  color: #64748b;
}

.lp-spinner {
  width: 22px; height: 22px;
  border: 2px solid rgba(0, 255, 102, 0.2);
  border-top-color: #00FF66;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.lp-pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-top: 60px;
  align-items: start;
}

.lp-pricing-card {
  background: linear-gradient(160deg, rgba(18, 18, 18, 0.95), rgba(18, 18, 18, 0.8));
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
  border-color: rgba(0, 255, 102, 0.3);
  box-shadow: 0 0 0 1px rgba(0, 255, 102, 0.12), 0 30px 60px rgba(0, 0, 0, 0.3);
}

.lp-pricing-card--popular:hover {
  border-color: rgba(0, 255, 102, 0.5);
  box-shadow: 0 0 0 1px rgba(0, 255, 102, 0.25), 0 30px 80px rgba(0, 0, 0, 0.4);
}

.lp-popular-badge {
  position: absolute;
  top: -14px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #00FF66, #00cc52);
  color: #060606;
  padding: 5px 18px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  white-space: nowrap;
  letter-spacing: 0.3px;
  box-shadow: 0 0 20px rgba(0, 255, 102, 0.4);
}

.lp-pricing-header {
  text-align: center;
  margin-bottom: 24px;
}

.lp-pricing-plan-icon {
  width: 52px; height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  margin: 0 auto 16px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.lp-plan-icon--free {
  background: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
}

.lp-plan-icon--pro {
  background: rgba(0, 255, 102, 0.1);
  color: #00FF66;
  border-color: rgba(0, 255, 102, 0.2);
}

.lp-plan-icon--unlimited {
  background: rgba(251, 191, 36, 0.1);
  color: #fbbf24;
  border-color: rgba(251, 191, 36, 0.2);
}

.lp-pricing-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 6px;
}

.lp-pricing-desc {
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 20px;
}

.lp-price-block { margin-bottom: 8px; }

.lp-free-label {
  font-size: 2.4rem;
  font-weight: 800;
  color: #94a3b8 !important;
  letter-spacing: -1px;
}

.pricing-price .price-currency {
  font-size: 1.1rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 6px;
}

.pricing-price .price-value {
  font-size: 3.4rem;
  font-weight: 800;
  color: #f8fafc;
  letter-spacing: -2px;
  line-height: 1;
}

.price-cents {
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.pricing-price .price-period {
  font-size: 0.95rem;
  font-weight: 500;
  color: #64748b;
  margin-bottom: 4px;
}

.lp-pricing-divider {
  height: 1px;
  background: rgba(148, 163, 184, 0.07);
  margin: 24px 0;
}

.lp-pricing-features {
  list-style: none;
  padding: 0;
  margin: 0 0 28px;
  display: flex;
  flex-direction: column;
  gap: 11px;
  flex: 1;
}

.lp-pricing-features li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.875rem;
}

.feat-yes { color: #94a3b8; }
.feat-no { color: #475569; }
.feat-no span { text-decoration: line-through; opacity: 0.6; }

.lp-check {
  font-size: 0.7rem;
  width: 18px; height: 18px;
  background: rgba(0, 255, 102, 0.1);
  color: #00FF66;
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

.lp-check--no {
  color: #475569;
  background: rgba(71, 85, 105, 0.12);
}

/* === Plan Buttons === */
.lp-btn-plan {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 13px;
  border-radius: 14px;
  font-size: 0.88rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  background: none;
}

.lp-btn-plan--free {
  background: rgba(148, 163, 184, 0.08);
  border-color: rgba(148, 163, 184, 0.18);
  color: #94a3b8;
}

.lp-btn-plan--free:hover {
  background: rgba(148, 163, 184, 0.14);
  border-color: rgba(148, 163, 184, 0.3);
  color: #e5e7eb;
  transform: translateY(-2px);
}

.lp-btn-plan--pro {
  background: linear-gradient(135deg, #00FF66, #00cc52);
  border-color: transparent;
  color: #060606;
  box-shadow: 0 0 20px rgba(0, 255, 102, 0.3);
}

.lp-btn-plan--pro:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 255, 102, 0.5);
}

.lp-btn-plan--enterprise {
  background: rgba(251, 191, 36, 0.08);
  border-color: rgba(251, 191, 36, 0.25);
  color: #fbbf24;
}

.lp-btn-plan--enterprise:hover {
  background: rgba(251, 191, 36, 0.14);
  border-color: rgba(251, 191, 36, 0.45);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(251, 191, 36, 0.15);
}

/* === Enterprise Highlight === */
.lp-enterprise-highlight {
  margin-top: 40px;
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.05), rgba(18, 18, 18, 0.9));
  border: 1px solid rgba(251, 191, 36, 0.2);
  padding: 36px 40px;
  backdrop-filter: blur(12px);
}

.lp-enterprise-highlight-inner {
  display: flex;
  align-items: center;
  gap: 40px;
}

.lp-enterprise-left {
  display: flex;
  align-items: flex-start;
  gap: 24px;
  flex: 1;
}

.lp-enterprise-icon {
  width: 56px; height: 56px;
  border-radius: 16px;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fbbf24;
  font-size: 1.4rem;
  flex-shrink: 0;
}

.lp-enterprise-left h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 6px;
}

.lp-enterprise-left p {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 16px;
  line-height: 1.55;
}

.lp-enterprise-features-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
}

.lp-enterprise-features-row span {
  font-size: 0.8rem;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 6px;
}

.lp-enterprise-features-row .fa-check { color: #fbbf24; }
.lp-x-no { color: #475569; }

.lp-enterprise-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 16px;
  flex-shrink: 0;
}

.lp-enterprise-price { text-align: right; }

.lp-enterprise-from {
  display: block;
  font-size: 0.72rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
  margin-bottom: 4px;
}

.lp-enterprise-value {
  font-size: 2rem;
  font-weight: 800;
  color: #fbbf24;
  letter-spacing: -1px;
}

.lp-enterprise-value small {
  font-size: 0.9rem;
  font-weight: 600;
  color: #64748b;
  letter-spacing: 0;
}

.lp-enterprise-cta { width: auto; padding: 12px 24px; }

/* === VPM Calculator === */
/* === Calculator === */
.lp-vpm-calc {
  margin-top: 80px;
  text-align: center;
}

.lp-vpm-calc-header { margin-bottom: 32px; }

.lp-vpm-calc-title {
  font-size: 1.9rem;
  font-weight: 800;
  color: #f8fafc;
  letter-spacing: -0.6px;
  margin-bottom: 10px;
}

.lp-vpm-calc-sub {
  font-size: 0.9rem;
  color: #64748b;
  max-width: 480px;
  margin: 0 auto;
  line-height: 1.6;
}

.lp-vpm-calc-card {
  background: rgba(18, 18, 18, 0.92);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 24px;
  padding: 40px 48px;
  max-width: 680px;
  margin: 0 auto;
  backdrop-filter: blur(12px);
}

/* Slider section */
.lp-calc-slider-section {
  margin-bottom: 0;
}

.lp-calc-slider-label {
  display: block;
  font-size: 0.78rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 16px;
}

.lp-calc-contacts-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 10px;
  margin-bottom: 24px;
}

.lp-calc-contacts-number {
  font-size: 3.2rem;
  font-weight: 900;
  color: #f8fafc;
  letter-spacing: -2px;
  line-height: 1;
}

.lp-calc-contacts-unit {
  font-size: 1rem;
  font-weight: 600;
  color: #475569;
}

.lp-vpm-calc-range {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(148, 163, 184, 0.15);
  border-radius: 999px;
  outline: none;
  cursor: pointer;
  margin-bottom: 12px;
}

.lp-vpm-calc-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px; height: 24px;
  border-radius: 50%;
  background: #0a0a0a;
  border: 3px solid #00FF66;
  cursor: pointer;
  box-shadow: 0 0 12px rgba(0, 255, 102, 0.5);
  transition: box-shadow 0.15s;
}

.lp-vpm-calc-range::-webkit-slider-thumb:hover {
  box-shadow: 0 0 20px rgba(0, 255, 102, 0.75);
}

.lp-vpm-calc-ticks {
  display: flex;
  justify-content: space-between;
  font-size: 0.68rem;
  color: #334155;
  font-weight: 600;
  margin-bottom: 0;
}

/* Divider */
.lp-calc-divider {
  height: 1px;
  background: rgba(148, 163, 184, 0.08);
  margin: 32px 0;
}

/* Resultado / comparativo */
.lp-calc-result {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 32px;
}

.lp-calc-compare-row {
  display: grid;
  grid-template-columns: 1fr 40px 1fr;
  align-items: center;
  gap: 12px;
}

.lp-calc-compare-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 20px 16px;
  border-radius: 16px;
}

.lp-calc-compare-col--market {
  background: rgba(148, 163, 184, 0.04);
  border: 1px solid rgba(148, 163, 184, 0.08);
}

.lp-calc-compare-col--bcp {
  background: rgba(0, 255, 102, 0.04);
  border: 1px solid rgba(0, 255, 102, 0.15);
}

.lp-calc-compare-label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: #64748b;
}

.lp-calc-compare-price {
  display: flex;
  align-items: baseline;
  gap: 2px;
  line-height: 1;
}

.lp-calc-compare-price--strike .lp-calc-compare-currency,
.lp-calc-compare-price--strike .lp-calc-compare-value,
.lp-calc-compare-price--strike .lp-calc-compare-period {
  color: #475569;
  text-decoration: line-through;
  text-decoration-color: rgba(239, 68, 68, 0.6);
}

.lp-calc-compare-price--bcp .lp-calc-compare-currency {
  font-size: 1rem;
  font-weight: 700;
  color: #00FF66;
  margin-bottom: 4px;
}

.lp-calc-compare-price--bcp .lp-calc-compare-value {
  font-size: 2.4rem;
  font-weight: 900;
  color: #00FF66;
  letter-spacing: -1.5px;
}

.lp-calc-compare-price--bcp .lp-calc-compare-period {
  font-size: 0.9rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 4px;
}

.lp-calc-compare-price--strike .lp-calc-compare-value {
  font-size: 1.8rem;
  font-weight: 800;
  letter-spacing: -1px;
}

.lp-calc-compare-price--strike .lp-calc-compare-currency {
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 3px;
}

.lp-calc-compare-price--strike .lp-calc-compare-period {
  font-size: 0.8rem;
  font-weight: 500;
  margin-bottom: 3px;
}

.lp-calc-compare-note {
  font-size: 0.68rem;
  color: #334155;
  font-style: italic;
}

.lp-calc-compare-tag {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #00FF66;
  background: rgba(0, 255, 102, 0.08);
  border: 1px solid rgba(0, 255, 102, 0.18);
  border-radius: 999px;
  padding: 2px 10px;
}

.lp-calc-compare-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #334155;
  font-size: 0.85rem;
}

/* Banner de economia */
.lp-calc-savings-banner {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 24px;
  background: rgba(0, 255, 102, 0.05);
  border: 1px solid rgba(0, 255, 102, 0.18);
  border-radius: 14px;
  text-align: left;
}

.lp-calc-savings-icon {
  font-size: 1.5rem;
  color: #00FF66;
  flex-shrink: 0;
  opacity: 0.85;
}

.lp-calc-savings-text {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.lp-calc-savings-headline {
  font-size: 0.95rem;
  color: #e2e8f0;
  font-weight: 500;
}

.lp-calc-savings-headline strong {
  color: #00FF66;
  font-weight: 800;
}

.lp-calc-savings-sub {
  font-size: 0.78rem;
  color: #64748b;
}

/* Footer */
.lp-calc-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.lp-vpm-calc-cta {
  flex-shrink: 0;
  justify-content: center;
  font-size: 0.95rem;
  padding: 12px 28px;
}

.lp-vpm-calc-link {
  background: none;
  border: none;
  color: #475569;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: color 0.15s;
}

.lp-vpm-calc-link:hover { color: #94a3b8; }

/* Responsive calculator */
@media (max-width: 640px) {
  .lp-vpm-calc-card { padding: 28px 20px; }
  .lp-calc-contacts-number { font-size: 2.4rem; }
  .lp-calc-compare-row { grid-template-columns: 1fr; gap: 8px; }
  .lp-calc-compare-arrow { transform: rotate(90deg); }
  .lp-calc-footer { flex-direction: column; align-items: stretch; }
  .lp-vpm-calc-cta { text-align: center; }
}

/* === Modal === */
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
  background: #121212;
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
  font-size: 1.05rem;
  font-weight: 700;
  color: #f8fafc;
}

.lp-modal-close {
  background: rgba(148, 163, 184, 0.1);
  border: none;
  color: #94a3b8;
  width: 32px; height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}

.lp-modal-close:hover { background: rgba(148, 163, 184, 0.2); color: #f8fafc; }

.lp-modal-body { overflow-y: auto; padding: 0; }

.lp-price-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.lp-price-table thead tr { background: rgba(148, 163, 184, 0.06); }

.lp-price-table th {
  padding: 12px 20px;
  text-align: left;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #64748b;
}

.lp-price-table td {
  padding: 13px 20px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.07);
  color: #cbd5e1;
  font-size: 0.875rem;
}

.lp-price-table tbody tr:hover td { background: rgba(148, 163, 184, 0.04); }
.lp-price-table-val { font-weight: 700; color: #00FF66 !important; }
.lp-price-table-per { color: #fbbf24 !important; }
.lp-price-table-extra td { opacity: 0.6; font-style: italic; font-size: 0.82rem; }

/* === FAQ === */
.lp-faq {
  padding: 100px 0;
  border-top: 1px solid rgba(148, 163, 184, 0.06);
}

.lp-faq .lp-section-title { margin-bottom: 48px; }

.lp-faq-list {
  max-width: 720px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.lp-faq-item {
  border: 1px solid rgba(148, 163, 184, 0.08);
  border-radius: 14px;
  overflow: hidden;
  transition: border-color 0.2s;
}

.lp-faq-item--open {
  border-color: rgba(0, 255, 102, 0.2);
}

.lp-faq-question {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 22px;
  background: none;
  border: none;
  color: #e2e8f0;
  font-size: 0.925rem;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s;
}

.lp-faq-question:hover { background: rgba(148, 163, 184, 0.04); }
.lp-faq-question i { color: #64748b; flex-shrink: 0; font-size: 0.8rem; }

.lp-faq-answer {
  padding: 0 22px 18px;
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.7;
}

.faq-expand-enter-active,
.faq-expand-leave-active {
  transition: all 0.2s ease;
}

.faq-expand-enter-from,
.faq-expand-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* === CTA Final === */
.lp-cta {
  padding: 100px 0;
}

.lp-cta-card {
  background: linear-gradient(135deg, rgba(18, 18, 18, 0.95), rgba(18, 18, 18, 0.85));
  border: 1px solid rgba(0, 255, 102, 0.18);
  border-radius: 28px;
  padding: 80px 40px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.lp-cta-glow {
  position: absolute;
  width: 500px; height: 500px;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, rgba(0, 255, 102, 0.05) 0%, transparent 70%);
  pointer-events: none;
}

.lp-cta-card h2 {
  font-size: 2.4rem;
  font-weight: 800;
  color: #f8fafc;
  margin-bottom: 14px;
  letter-spacing: -0.8px;
}

.lp-cta-card p {
  font-size: 1rem;
  color: #64748b;
  margin-bottom: 36px;
  max-width: 480px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.65;
}

.lp-cta-actions {
  display: flex;
  gap: 14px;
  justify-content: center;
  flex-wrap: wrap;
}

/* === Footer === */
.lp-footer {
  padding: 32px 0;
  border-top: 1px solid rgba(148, 163, 184, 0.07);
  background: rgba(6, 6, 6, 0.8);
}

.lp-footer-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.lp-footer-copy {
  font-size: 0.78rem;
  color: #334155;
}

/* === Mobile hamburger === */
.lp-menu-toggle {
  display: none;
  background: none;
  border: 1px solid rgba(148, 163, 184, 0.18);
  color: #64748b;
  width: 40px; height: 40px;
  border-radius: 10px;
  cursor: pointer;
  align-items: center;
  justify-content: center;
  font-size: 1.05rem;
  transition: all 0.15s ease;
  margin-left: auto;
}

.lp-menu-toggle:hover {
  background: rgba(148, 163, 184, 0.08);
  color: #e5e7eb;
  border-color: rgba(148, 163, 184, 0.3);
}

.lp-mobile-menu {
  position: sticky;
  top: 65px;
  z-index: 99;
  background: rgba(8, 8, 8, 0.97);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(148, 163, 184, 0.08);
  display: flex;
  flex-direction: column;
  padding: 12px 20px 20px;
  gap: 2px;
}

.lp-mobile-link {
  padding: 11px 16px;
  border-radius: 10px;
  color: #64748b;
  text-decoration: none;
  font-size: 0.925rem;
  font-weight: 500;
  transition: all 0.15s ease;
  display: block;
}

.lp-mobile-link:hover {
  background: rgba(148, 163, 184, 0.07);
  color: #94a3b8;
}

.lp-mobile-menu-divider {
  height: 1px;
  background: rgba(148, 163, 184, 0.08);
  margin: 10px 0 8px;
}

.lp-mobile-cta {
  justify-content: center;
}

/* Mobile menu transition */
.lp-slide-enter-active,
.lp-slide-leave-active { transition: all 0.22s ease; }

.lp-slide-enter-from,
.lp-slide-leave-to { opacity: 0; transform: translateY(-10px); }

/* === Responsive === */
@media (max-width: 900px) {
  .lp-features-grid { grid-template-columns: repeat(2, 1fr); }
  .lp-menu-toggle { display: flex; }
  .lp-nav-links, .lp-nav-actions { display: none; }

  .lp-enterprise-highlight-inner {
    flex-direction: column;
    gap: 24px;
  }
  .lp-enterprise-right {
    align-items: center;
    width: 100%;
  }
  .lp-enterprise-cta { width: 100%; max-width: 320px; }
}

@media (max-width: 640px) {
  .lp-hero { padding: 80px 0 60px; }
  .lp-hero-title { font-size: 2.6rem; letter-spacing: -1.2px; }
  .lp-hero-subtitle { font-size: 0.975rem; }
  .lp-section-title { font-size: 1.8rem; }
  .lp-features-grid { grid-template-columns: 1fr; }
  .lp-hero-cta { flex-direction: column; align-items: center; }
  .lp-cta-card { padding: 50px 24px; }
  .lp-cta-card h2 { font-size: 1.8rem; }
  .lp-footer-content { flex-direction: column; text-align: center; }

  .lp-testimonial-stats {
    flex-direction: column;
    gap: 20px;
    padding: 24px 20px;
  }
  .lp-t-stat-divider { width: 48px; height: 1px; }
  .lp-t-stat-label { white-space: normal; }

  .lp-vpm-calc-card { padding: 24px 16px; }
  .lp-vpm-calc-body { flex-direction: column; gap: 16px; }
  .lp-vpm-calc-equals { display: none; }
  .lp-vpm-calc-left { text-align: center; }
  .lp-vpm-calc-number { font-size: 1.8rem; }
  .lp-vpm-calc-price { font-size: 2.2rem; }
  .lp-vpm-calc-title { font-size: 1.5rem; }
  .lp-vpm-calc-cta { max-width: 100%; }

  .lp-cta-actions { flex-direction: column; align-items: center; }
  .lp-enterprise-highlight { padding: 24px 20px; }
}
</style>
