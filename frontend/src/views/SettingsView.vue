<template>
  <AppLayout>
    <div class="settings-page">
      <div v-if="statusMessage" class="settings-toast">{{ statusMessage }}</div>

      <div class="settings-layout">
        <!-- Menu Horizontal Superior -->
        <nav class="settings-top-nav">
          <template v-for="(section, sIdx) in menuSections" :key="section.title">
            <button
              v-for="item in section.items"
              :key="item.label"
              :class="['settings-nav-item', { active: activeTab === item.label }]"
              @click="selectTab(item.label)"
            >
              <i :class="item.iconClass"></i>
              <span>{{ item.label }}</span>
            </button>
            <div v-if="sIdx < menuSections.length - 1" class="settings-nav-divider"></div>
          </template>
        </nav>

        <!-- Conteúdo Principal -->
        <section class="settings-content">
          <div class="settings-content-body">

            <div v-if="activeTab === 'Geral'" class="settings-general-table">
              <div class="settings-row">
                <div class="settings-row-label">
                  <p>Nome da conta</p>
                  <small>Nome exibido para esta conta.</small>
                </div>
                <div class="settings-row-control">
                  <input class="input settings-input" type="text" v-model="tenantNameDraft" />
                </div>
                <div class="settings-row-tip">
                  <p></p>
                </div>
              </div>

              <div class="settings-row">
                <div class="settings-row-label">
                  <p>Email</p>
                  <small>Somente leitura.</small>
                </div>
                <div class="settings-row-control">
                  <input class="input settings-input" type="text" :value="tenantEmail" disabled />
                </div>
                <div class="settings-row-tip">
                  <p></p>
                </div>
              </div>

              <div class="settings-row">
                <div class="settings-row-label">
                  <p>Fuso horário</p>
                  <small>Usado para exibição e relatórios.</small>
                </div>
                <div class="settings-row-control">
                  <select class="input settings-input" v-model="tenantTimezoneDraft">
                    <option value="">(não definido)</option>
                    <option v-for="zone in timezoneOptions" :key="zone" :value="zone">
                      {{ zone }}
                    </option>
                  </select>
                </div>
                <div class="settings-row-tip">
                  <p></p>
                </div>
              </div>

              <div class="settings-row">
                <div class="settings-row-label">
                  <p>Salvar</p>
                  <small>Aplica as alterações da conta.</small>
                </div>
                <div class="settings-row-control">
                  <button class="btn btn-primary" type="button" :disabled="savingGeneral" @click="saveGeneral">
                    {{ savingGeneral ? 'Salvando...' : 'Salvar' }}
                  </button>
                </div>
                <div class="settings-row-tip">
                  <p></p>
                </div>
              </div>

              <div class="settings-row">
                <div class="settings-row-label">
                  <p>Sair</p>
                  <small>Encerra sua sessão.</small>
                </div>
                <div class="settings-row-control">
                  <button class="btn btn-ghost" type="button" @click="handleSignOut">Sair</button>
                </div>
                <div class="settings-row-tip">
                  <p></p>
                </div>
              </div>
            </div>

            <div v-else-if="activeTab === 'Cobrança'" class="settings-subscriptions-card">
              <div class="settings-subscriptions-head">
                <div>
                  <p class="settings-subscriptions-title">Situação da conta</p>
                  <span class="settings-subscriptions-tag" v-if="subscriptionStatusLabel">{{ subscriptionStatusLabel }}</span>
                </div>
              </div>

              <div class="settings-subscriptions-table">
                <div class="settings-subscriptions-row settings-subscriptions-row--head">
                  <span>Item</span>
                  <span>Valor</span>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <div class="settings-subscriptions-row">
                  <span><strong>Plano atual</strong></span>
                  <span>{{ subscriptionData?.plan?.display_name || '—' }}</span>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <div class="settings-subscriptions-row">
                  <span><strong>Período</strong></span>
                  <span>{{ subscriptionPeriodLabel }}</span>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>

              <!-- Widget VPM: só aparece em planos pagos com VPM -->
              <div v-if="vpmEstimate" class="vpm-estimate-widget">
                <div class="vpm-estimate-title">
                  <i class="fas fa-chart-bar"></i> Estimativa do ciclo atual
                </div>
                <div class="vpm-estimate-grid">
                  <div class="vpm-estimate-item">
                    <span class="vpm-estimate-label">Contatos ativos (30d)</span>
                    <span class="vpm-estimate-value">{{ vpmEstimate.active_contacts.toLocaleString('pt-BR') }}</span>
                  </div>
                  <div class="vpm-estimate-item">
                    <span class="vpm-estimate-label">Blocos de 1.000</span>
                    <span class="vpm-estimate-value">{{ vpmEstimate.thousand_blocks }}</span>
                  </div>
                  <div class="vpm-estimate-item">
                    <span class="vpm-estimate-label">Calculado ({{ vpmEstimate.thousand_blocks }} × R$ {{ vpmEstimate.vpm_price }})</span>
                    <span class="vpm-estimate-value">{{ formatPrice(vpmEstimate.calculated_amount) }}</span>
                  </div>
                  <div class="vpm-estimate-item vpm-estimate-item--total">
                    <span class="vpm-estimate-label">
                      {{ vpmEstimate.minimum_applied ? 'Cobrança (mínimo aplicado)' : 'Cobrança estimada' }}
                    </span>
                    <span class="vpm-estimate-value vpm-estimate-value--hl">
                      {{ formatPrice(vpmEstimate.final_amount) }}/mês
                      <span v-if="vpmEstimate.minimum_applied" class="vpm-min-badge">mínimo</span>
                    </span>
                  </div>
                </div>
                <p class="vpm-estimate-note">Estimativa com base nos contatos ativos dos últimos 30 dias. O valor real pode variar no fechamento do ciclo.</p>
              </div>

              <div class="settings-subscriptions-actions">
                <button class="btn btn-outline" type="button" :disabled="billingPortalDisabled" @click="openBillingPortal">
                  {{ billingLoading ? 'Abrindo...' : 'Gerenciar cobrança' }}
                </button>
                <button class="btn btn-primary" type="button" @click="selectTab('Planos')">
                  Ver planos
                </button>
              </div>
            </div>

            <div v-else-if="activeTab === 'Planos'" class="settings-subs-wrap">

              <!-- Header: título + toggle + link -->
              <div class="settings-subs-header">
                <div class="settings-subs-header-left">
                  <span class="settings-subs-title">Planos</span>
                  <span v-if="subscriptionStatusLabel" class="settings-subscriptions-tag" :class="{
                    'tag--active': subscriptionData?.status === 'active' || subscriptionData?.status === 'trial',
                    'tag--inactive': subscriptionData?.status === 'canceled' || subscriptionData?.status === 'expired',
                    'tag--warning': subscriptionData?.status === 'past_due'
                  }">{{ subscriptionStatusLabel }}</span>
                </div>
                <div class="settings-subs-header-right">
                  <a href="#" class="settings-subscriptions-link" @click.prevent="selectTab('Cobrança')">Ver cobrança</a>
                </div>
              </div>

              <!-- 3 cards horizontais -->
              <div class="plans-grid">
                <div
                  v-for="plan in plans"
                  :key="plan.id"
                  :class="['plan-card', { 'plan-card--current': isCurrentPlan(plan) }]"
                >
                  <div v-if="isCurrentPlan(plan)" class="plan-card-badge">Plano atual</div>

                  <!-- Nome + Preço -->
                  <div>
                    <p class="plan-card-name">{{ plan.display_name }}</p>

                    <!-- Pro (preço fixo) -->
                    <template v-if="plan.name === 'pro'">
                      <span class="plan-card-price-main">R$&nbsp;99<small>/mês</small></span>
                      <span class="plan-card-price-sub">Até 2.500 contatos ativos</span>
                    </template>

                    <!-- Enterprise (personalizado) -->
                    <template v-else-if="plan.name === 'unlimited'">
                      <span class="plan-card-price-from">personalizado</span>
                      <span class="plan-card-price-main">Enterprise</span>
                      <span class="plan-card-price-sub">cobrado por volume de contatos</span>
                      <div class="enterprise-picker">
                        <div class="enterprise-picker-row">
                          <label class="enterprise-picker-label">Contatos ativos:</label>
                          <input
                            class="enterprise-picker-input"
                            type="number"
                            v-model.number="enterpriseContacts"
                            min="1"
                            step="100"
                          />
                        </div>
                        <input
                          type="range"
                          class="enterprise-picker-range"
                          min="0" max="100" step="1"
                          v-model.number="enterpriseSlider"
                        />
                        <div class="enterprise-picker-ticks">
                          <span>500</span><span>5k</span><span>50k</span><span>500k</span><span>2M</span>
                        </div>
                        <div class="enterprise-picker-price" v-if="enterprisePrice > 0">
                          {{ formatPrice(enterprisePrice) }}<small>/mês</small>
                          <span class="enterprise-picker-min-badge" v-if="enterpriseContacts < 26000">mínimo</span>
                        </div>
                      </div>
                    </template>

                    <!-- Outro VPM -->
                    <!-- Outro VPM -->
                    <template v-else-if="plan.vpm_price">
                      <span class="plan-card-price-from">a partir de</span>
                      <span class="plan-card-price-main">R$&nbsp;{{ plan.vpm_price }}<small>/1K contatos</small></span>
                      <span class="plan-card-price-sub">Mín. {{ formatPrice(plan.min_monthly) }}/mês</span>
                    </template>

                    <!-- Grátis -->
                    <template v-else-if="plan.name === 'free' || plan.price_monthly === 0">
                      <span class="plan-card-price-main">Gr&aacute;tis</span>
                    </template>

                    <!-- Preço fixo genérico -->
                    <template v-else>
                      <span class="plan-card-price-main">{{ formatPrice(plan.price_monthly) }}<small>/mês</small></span>
                    </template>
                  </div>

                  <div class="plan-card-divider"></div>

                  <!-- Features -->
                  <ul class="plan-card-features">
                    <li v-for="item in planUi(plan).items.slice(1, 8)" :key="item.label">
                      <i class="fa-solid fa-check"></i>
                      <span><b>{{ item.value }}</b>&nbsp;{{ item.label }}</span>
                    </li>
                  </ul>

                  <!-- CTA -->
                  <button
                    v-if="plan.name !== 'unlimited'"
                    class="btn plan-card-btn"
                    :class="isCurrentPlan(plan) ? 'btn-outline' : 'btn-primary'"
                    type="button"
                    :disabled="billingLoading || isCurrentPlan(plan) || !stripeConfigured || !plan?.stripe_price_id_monthly"
                    @click="startCheckout(plan)"
                  >
                    {{ isCurrentPlan(plan) ? 'Plano atual' : (billingLoading ? 'Carregando...' : 'Assinar') }}
                  </button>
                  <button
                    v-else
                    class="btn btn-primary plan-card-btn"
                    type="button"
                    :disabled="billingLoading || isCurrentPlan(plan) || !stripeConfigured"
                    @click="startEnterpriseCheckout"
                  >
                    {{ isCurrentPlan(plan) ? 'Plano atual' : (billingLoading ? 'Carregando...' : 'Contratar') }}
                  </button>
                </div>
              </div>

              <!-- Barra de uso -->
              <div class="subs-usage-bar" v-if="subscriptionData">
                <span class="subs-usage-bar-label">Uso atual</span>
                <!-- Chip de contatos contratados: exibido apenas para Enterprise quando preenchido -->
                <span
                  v-if="subscriptionData.contracted_contacts != null && subscriptionData.plan?.name === 'unlimited'"
                  class="subs-usage-bar-item subs-contracted"
                >
                  Contatos contratados: <b>{{ subscriptionData.contracted_contacts.toLocaleString('pt-BR') }}</b>
                </span>
                <span v-for="(v, k) in subscriptionData.usage" :key="k" class="subs-usage-bar-item">
                  {{ usageLabel(k) }}: <b>{{ v.used }}&nbsp;/&nbsp;{{
                    k === 'contacts' && subscriptionData.contracted_contacts
                      ? subscriptionData.contracted_contacts.toLocaleString('pt-BR')
                      : (v.limit != null ? v.limit : '\u221e')
                  }}</b>
                </span>
              </div>

            </div>

            <div v-else-if="activeTab === 'Telegram'" class="telegram-onboarding">

              <!-- Loading skeleton -->
              <div v-if="loadingTelegram" class="tg-loading">
                <div class="tg-loading-header">
                  <div class="tg-skel tg-skel-title"></div>
                  <div class="tg-skel tg-skel-btn"></div>
                </div>
                <div class="tg-loading-grid">
                  <div v-for="i in 3" :key="i" class="tg-skel-card">
                    <div class="tg-skel-card-icon"></div>
                    <div class="tg-skel-card-body">
                      <div class="tg-skel tg-skel-line tg-skel-line--lg"></div>
                      <div class="tg-skel tg-skel-line tg-skel-line--sm"></div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Tela 0: Lista de Bots Conectados -->
              <div v-else-if="telegramStep === 'list'" class="telegram-bots-list">
                <div class="telegram-list-header">
                  <div>
                    <h2 class="telegram-section-title">Bots do Telegram Conectados</h2>
                    <p class="telegram-section-subtitle">
                      {{ telegramChannels.length }} bot(s) • 
                      <span class="text-success">{{ telegramChannels.filter(c => c.is_active).length }} ativo(s)</span> • 
                      <span class="text-muted">{{ telegramChannels.filter(c => !c.is_active).length }} inativo(s)</span>
                    </p>
                  </div>
                  <button class="btn btn-primary" @click="telegramStep = 'intro'">
                    <i class="fa-solid fa-plus"></i>
                    Conectar Novo Bot
                  </button>
                </div>

                <!-- Mensagem quando não há bots -->
                <div v-if="telegramChannels.length === 0" class="no-bots-message">
                  <div class="no-bots-icon">
                    <i class="fa-brands fa-telegram"></i>
                  </div>
                  <h3>Nenhum bot conectado</h3>
                  <p>Conecte seu primeiro bot do Telegram para começar a criar fluxos de automação</p>
                  <button class="btn btn-primary btn-lg" @click="telegramStep = 'intro'" style="margin-top: 20px;">
                    <i class="fa-solid fa-plus"></i>
                    Conectar Primeiro Bot
                  </button>
                </div>

                <!-- Grid de Bots -->
                <div v-else class="telegram-bots-grid">
                  <div 
                    v-for="channel in telegramChannels" 
                    :key="channel.id" 
                    class="bot-card"
                    :class="channel.is_active ? 'bot-card-active' : 'bot-card-inactive'"
                  >
                    <div class="bot-card-main">
                      <!-- Icon e Info Principal -->
                      <div class="bot-card-left">
                        <div class="bot-card-icon">
                          <i class="fa-brands fa-telegram"></i>
                        </div>
                        <div class="bot-card-info-main">
                          <h3 class="bot-card-title">{{ channel.name }}</h3>
                          <div v-if="getBotUsername(channel)" class="bot-card-username">
                            <i class="fa-solid fa-at"></i>
                            <span>{{ getBotUsername(channel) }}</span>
                          </div>
                          <div v-else class="bot-card-username-missing">
                            <i class="fa-solid fa-exclamation-circle"></i>
                            <span>Username não configurado</span>
                          </div>
                        </div>
                      </div>

                      <!-- Toggle -->
                      <div class="bot-card-right">
                        <label class="toggle-switch" :title="channel.is_active ? 'Desativar bot' : 'Ativar bot'">
                          <input 
                            type="checkbox" 
                            :checked="channel.is_active"
                            @change="toggleBotStatus(channel)"
                          />
                          <span class="toggle-slider"></span>
                        </label>
                      </div>
                    </div>

                    <!-- Actions -->
                    <div class="bot-card-actions">
                      <button 
                        class="btn-card-action"
                        @click="openEditBotModal(channel)"
                        title="Editar"
                      >
                        <i class="fa-solid fa-pen"></i>
                        <span>Editar</span>
                      </button>
                      <button 
                        class="btn-card-action btn-card-danger"
                        @click="disconnectBot(channel)"
                        title="Desconectar"
                      >
                        <i class="fa-solid fa-plug-circle-xmark"></i>
                        <span>Desconectar</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Tela 1: Apresentação -->
              <div v-else-if="telegramStep === 'intro'" class="telegram-intro">
                <div class="telegram-intro-content">
                  <div class="telegram-intro-icon">
                    <i class="fa-brands fa-telegram"></i>
                  </div>
                  <h2 class="telegram-intro-title">Crie relações com seus clientes no Telegram</h2>
                  <p class="telegram-intro-subtitle">
                    Crie automações avançadas, inicie novas campanhas e procure as melhores práticas para alcançar 
                    um público de 500 milhões no Telegram. Inicie relações significativas com seus clientes agora mesmo.
                  </p>
                  <button class="btn btn-primary btn-lg" @click="telegramStep = 'choose'">
                    <i class="fa-solid fa-plug"></i>
                    Conectar
                  </button>
                </div>
                <div class="telegram-intro-image">
                  <i class="fa-brands fa-telegram"></i>
                </div>
              </div>

              <!-- Tela 2: Escolha do método -->
              <div v-else-if="telegramStep === 'choose'" class="telegram-choose">
                <button class="telegram-back-btn" @click="telegramStep = 'intro'">
                  <i class="fa-solid fa-arrow-left"></i>
                  Voltar
                </button>

                <div class="telegram-choose-header">
                  <h1 class="choose-main-title">Conectar Bot do Telegram</h1>
                  <p class="choose-description">Você pode criar um novo bot ou conectar um já existente.</p>
                </div>

                <div class="telegram-divider"></div>

                <div class="telegram-choose-body">
                  <h2 class="choose-section-title">Como você quer começar?</h2>
                  <p class="choose-hint">
                    Em cada cenário, guiaremos você através de instruções fáceis e passo a passo.
                  </p>

                  <div class="telegram-options">
                    <button class="telegram-option-card" @click="telegramStep = 'create-new'">
                      <div class="telegram-option-icon">
                        <i class="fa-solid fa-plus-circle"></i>
                      </div>
                      <div class="telegram-option-content">
                        <h4>Criar Novo Bot</h4>
                        <p>Crie um bot do zero com nossa ajuda</p>
                      </div>
                      <i class="fa-solid fa-chevron-right telegram-option-arrow"></i>
                    </button>

                    <button class="telegram-option-card" @click="telegramStep = 'connect-existing'">
                      <div class="telegram-option-icon">
                        <i class="fa-solid fa-link"></i>
                      </div>
                      <div class="telegram-option-content">
                        <h4>Conectar Bot Existente</h4>
                        <p>Conecte um bot que você já possui</p>
                      </div>
                      <i class="fa-solid fa-chevron-right telegram-option-arrow"></i>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Tela 3: Criar Novo Bot -->
              <div v-else-if="telegramStep === 'create-new'" class="telegram-form">
                <button class="telegram-back-btn" @click="telegramStep = 'choose'">
                  <i class="fa-solid fa-arrow-left"></i>
                  Voltar
                </button>

                <div class="telegram-form-header">
                  <div class="telegram-form-icon">
                    <i class="fa-solid fa-plus-circle"></i>
                  </div>
                  <h2 class="telegram-section-title">Criar Novo Bot</h2>
                  <p class="telegram-section-subtitle">
                    Essa instrução ajuda você a criar um novo bot do Telegram.
                  </p>
                </div>

                <div class="telegram-steps">
                  <div class="telegram-step-item">
                    <div class="telegram-step-number">1</div>
                    <div class="telegram-step-content">
                      <p>Abra <strong>@BotFather</strong> no Telegram e clique em <code>/start</code></p>
                    </div>
                  </div>

                  <div class="telegram-step-item">
                    <div class="telegram-step-number">2</div>
                    <div class="telegram-step-content">
                      <p>Envie <code>/newbot</code> e siga as instruções</p>
                    </div>
                  </div>

                  <div class="telegram-step-item">
                    <div class="telegram-step-number">3</div>
                    <div class="telegram-step-content">
                      <p>Quando o bot for criado, você receberá uma mensagem com o token. Copie o token e cole-o aqui</p>
                    </div>
                  </div>
                </div>

                <div class="telegram-form-body">
                  <div class="form-group">
                    <label class="form-label">Nome do Bot *</label>
                    <input 
                      class="form-input form-input-lg" 
                      v-model="telegramForm.bot_name"
                      placeholder="Ex: Bot Vendas, Bot Suporte, Bot Principal..."
                      autocomplete="off"
                      spellcheck="false"
                    />
                    <small class="form-hint">Este nome aparecerá ao criar fluxos para facilitar a identificação</small>
                  </div>

                  <div class="form-group">
                    <label class="form-label">Token do bot do Telegram *</label>
                    <div class="token-input-group">
                      <textarea 
                        class="form-input form-input-lg telegram-token-input" 
                        v-model="telegramForm.bot_token"
                        placeholder="Cole seu token aqui: 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"
                        rows="2"
                        autocomplete="off"
                        spellcheck="false"
                        @input="telegramForm.bot_username = ''"
                      ></textarea>
                      <button 
                        class="btn btn-secondary btn-validate-token"
                        @click="validateTelegramToken"
                        :disabled="!telegramForm.bot_token || validatingToken"
                        type="button"
                      >
                        <i class="fa-solid fa-check-circle"></i>
                        {{ validatingToken ? 'Validando...' : 'Validar Token' }}
                      </button>
                    </div>
                    
                    <!-- Resultado da validação -->
                    <div v-if="tokenValidationResult" class="token-validation-result" :class="tokenValidationResult.success ? 'success' : 'error'">
                      <i :class="tokenValidationResult.success ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-xmark'"></i>
                      <div>
                        <strong>{{ tokenValidationResult.success ? '✓ Token válido!' : '✗ Token inválido' }}</strong>
                        <p>{{ tokenValidationResult.message }}</p>
                      </div>
                    </div>
                  </div>

                  <!-- Campo do username (automático após validação) -->
                  <div class="form-group" v-if="telegramForm.bot_username">
                    <label class="form-label">Username do Bot</label>
                    <div class="bot-username-display">
                      <i class="fa-brands fa-telegram"></i>
                      <span>@{{ telegramForm.bot_username }}</span>
                      <span class="badge badge-success">✓ Detectado</span>
                    </div>
                  </div>

                  <button 
                    class="btn btn-primary btn-lg" 
                    @click="connectTelegramBot" 
                    :disabled="loading || !telegramForm.bot_token || !telegramForm.bot_name"
                    style="width: 100%;"
                  >
                    <i class="fa-solid fa-plug"></i>
                    {{ loading ? 'Conectando...' : 'Conectar' }}
                  </button>
                </div>
              </div>

              <!-- Tela 4: Conectar Bot Existente -->
              <div v-else-if="telegramStep === 'connect-existing'" class="telegram-form">
                <button class="telegram-back-btn" @click="telegramStep = 'choose'">
                  <i class="fa-solid fa-arrow-left"></i>
                  Voltar
                </button>

                <div class="telegram-form-header">
                  <div class="telegram-form-icon">
                    <i class="fa-solid fa-link"></i>
                  </div>
                  <h2 class="telegram-section-title">Conectar Bot Existente</h2>
                  <p class="telegram-section-subtitle">
                    Essa instrução ajuda você a conectar o bot do Telegram.
                  </p>
                  <div class="telegram-warning">
                    <i class="fa-solid fa-exclamation-triangle"></i>
                    <p>
                      Nós recomendamos que você não use o mesmo token para diferentes serviços, 
                      caso contrário o bot irá funcionar incorretamente.
                    </p>
                  </div>
                </div>

                <div class="telegram-steps">
                  <div class="telegram-step-item">
                    <div class="telegram-step-number">1</div>
                    <div class="telegram-step-content">
                      <p>Abra <strong>@BotFather</strong> no Telegram e clique em <code>/start</code></p>
                    </div>
                  </div>

                  <div class="telegram-step-item">
                    <div class="telegram-step-number">2</div>
                    <div class="telegram-step-content">
                      <p>Envie <code>/mybots</code> e escolha o bot que deseja conectar da lista</p>
                    </div>
                  </div>

                  <div class="telegram-step-item">
                    <div class="telegram-step-number">3</div>
                    <div class="telegram-step-content">
                      <p>Copie token da API e cole aqui</p>
                    </div>
                  </div>
                </div>

                <div class="telegram-form-body">
                  <div class="form-group">
                    <label class="form-label">Nome do Bot *</label>
                    <input 
                      class="form-input form-input-lg" 
                      v-model="telegramForm.bot_name"
                      placeholder="Ex: Bot Vendas, Bot Suporte, Bot Principal..."
                      autocomplete="off"
                      spellcheck="false"
                    />
                    <small class="form-hint">Este nome aparecerá ao criar fluxos para facilitar a identificação</small>
                  </div>

                  <div class="form-group">
                    <label class="form-label">Token do bot do Telegram *</label>
                    <div class="token-input-group">
                      <textarea 
                        class="form-input form-input-lg telegram-token-input" 
                        v-model="telegramForm.bot_token"
                        placeholder="Cole seu token aqui: 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"
                        rows="2"
                        autocomplete="off"
                        spellcheck="false"
                        @input="telegramForm.bot_username = ''"
                      ></textarea>
                      <button 
                        class="btn btn-secondary btn-validate-token"
                        @click="validateTelegramToken"
                        :disabled="!telegramForm.bot_token || validatingToken"
                        type="button"
                      >
                        <i class="fa-solid fa-check-circle"></i>
                        {{ validatingToken ? 'Validando...' : 'Validar Token' }}
                      </button>
                    </div>
                    
                    <!-- Resultado da validação -->
                    <div v-if="tokenValidationResult" class="token-validation-result" :class="tokenValidationResult.success ? 'success' : 'error'">
                      <i :class="tokenValidationResult.success ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-xmark'"></i>
                      <div>
                        <strong>{{ tokenValidationResult.success ? '✓ Token válido!' : '✗ Token inválido' }}</strong>
                        <p>{{ tokenValidationResult.message }}</p>
                      </div>
                    </div>
                  </div>

                  <!-- Campo do username (automático após validação) -->
                  <div class="form-group" v-if="telegramForm.bot_username">
                    <label class="form-label">Username do Bot</label>
                    <div class="bot-username-display">
                      <i class="fa-brands fa-telegram"></i>
                      <span>@{{ telegramForm.bot_username }}</span>
                      <span class="badge badge-success">✓ Detectado</span>
                    </div>
                  </div>

                  <button 
                    class="btn btn-primary btn-lg" 
                    @click="connectTelegramBot" 
                    :disabled="loading || !telegramForm.bot_token || !telegramForm.bot_name"
                    style="width: 100%;"
                  >
                    <i class="fa-solid fa-plug"></i>
                    {{ loading ? 'Conectando...' : 'Conectar' }}
                  </button>
                </div>
              </div>

              <!-- Modal: Editar Bot -->
              <div v-if="showEditBotModal" class="modal-overlay" @click="closeEditBotModal">
                <div class="modal-content modal-edit-bot" @click.stop>
                  <div class="modal-header">
                    <h3 class="modal-title">
                      <i class="fa-solid fa-pen-to-square" style="margin-right: 8px;"></i>
                      Editar Bot
                    </h3>
                    <button class="modal-close" @click="closeEditBotModal">
                      <i class="fa-solid fa-times"></i>
                    </button>
                  </div>

                  <div class="modal-body">
                    <!-- Nome do Bot -->
                    <div class="form-group">
                      <label class="form-label">
                        <i class="fa-solid fa-tag" style="margin-right: 6px;"></i>
                        Nome do Bot *
                      </label>
                      <input 
                        class="form-input form-input-lg" 
                        v-model="editBotForm.name"
                        placeholder="Ex: Bot Vendas, Bot Suporte..."
                        autocomplete="off"
                        @keyup.enter="saveBotName"
                      />
                      <small class="form-hint">Este nome aparecerá ao criar fluxos e na lista de bots</small>
                    </div>

                    <!-- Token do Bot -->
                    <div class="form-group">
                      <label class="form-label">
                        <i class="fa-solid fa-key" style="margin-right: 6px;"></i>
                        Token do Bot *
                      </label>
                      <div class="input-with-button">
                        <input 
                          class="form-input form-input-lg" 
                          :type="editBotForm.showToken ? 'text' : 'password'"
                          v-model="editBotForm.bot_token"
                          placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
                          autocomplete="off"
                          @keyup.enter="saveBotName"
                        />
                        <button
                          type="button"
                          class="btn btn-secondary btn-sm"
                          @click="editBotForm.showToken = !editBotForm.showToken"
                          :title="editBotForm.showToken ? 'Ocultar token' : 'Mostrar token'"
                        >
                          <i :class="editBotForm.showToken ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye'"></i>
                        </button>
                      </div>
                      <small class="form-hint">
                        <i class="fa-solid fa-info-circle" style="margin-right: 4px;"></i>
                        Obtido do @BotFather no Telegram. Altere apenas se precisar trocar o bot.
                      </small>
                    </div>

                    <!-- Validação de Token / Username -->
                    <div class="form-group">
                      <label class="form-label">
                        <i class="fa-solid fa-user-check" style="margin-right: 6px;"></i>
                        Username do Bot
                      </label>
                      <div class="input-with-button">
                        <input
                          class="form-input form-input-lg"
                          v-model="editBotForm.bot_username"
                          placeholder="@seu_bot"
                          autocomplete="off"
                          @keyup.enter="saveBotName"
                        />
                        <button
                          type="button"
                          class="btn btn-secondary btn-sm"
                          @click="validateEditToken"
                          :disabled="!editBotForm.bot_token || validatingEditToken"
                        >
                          <i class="fa-solid fa-check-circle"></i>
                          {{ validatingEditToken ? 'Validando...' : 'Validar token e buscar username' }}
                        </button>
                      </div>
                      <small class="form-hint">
                        Validamos direto com a API do Telegram usando o token informado.
                      </small>

                      <div v-if="editTokenValidation" class="token-validation-result" :class="editTokenValidation.success ? 'success' : 'error'">
                        <i :class="editTokenValidation.success ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-xmark'"></i>
                        <div>
                          <strong>{{ editTokenValidation.success ? '✓ Username detectado!' : '✗ Falha ao validar' }}</strong>
                          <p>{{ editTokenValidation.message }}</p>
                        </div>
                      </div>
                    </div>

                    <!-- Chat ID do Admin para Notificações -->
                    <div class="form-group">
                      <label class="form-label">
                        <i class="fa-solid fa-bell" style="margin-right: 6px;"></i>
                        Chat ID do Admin (Notificações)
                      </label>
                      <input
                        class="form-input form-input-lg"
                        v-model="editBotForm.admin_telegram_chat_id"
                        placeholder="Ex: 123456789"
                        autocomplete="off"
                      />
                      <small class="form-hint">
                        <i class="fa-solid fa-info-circle" style="margin-right: 4px;"></i>
                        Seu chat_id pessoal no Telegram. O bot enviará alertas de <em>Notificar Admin</em> para este ID.
                        Para descobrir seu ID, envie /start para @userinfobot no Telegram.
                      </small>
                    </div>

                    <!-- Aviso de Webhook -->
                    <div class="modal-warning" v-if="editBotForm.bot_token !== editBotForm.originalToken">
                      <i class="fa-solid fa-exclamation-triangle"></i>
                      <div>
                        <strong>Atenção:</strong> Ao alterar o token, o webhook será re-registrado automaticamente.
                      </div>
                    </div>
                  </div>

                  <div class="modal-footer">
                    <button class="btn btn-secondary" @click="closeEditBotModal">
                      <i class="fa-solid fa-times"></i>
                      Cancelar
                    </button>
                    <button 
                      class="btn btn-primary" 
                      @click="saveBotName"
                      :disabled="!editBotForm.name || !editBotForm.bot_token || editBotForm.saving"
                    >
                      <i class="fa-solid fa-check"></i>
                      {{ editBotForm.saving ? 'Salvando...' : 'Salvar Alterações' }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- Modal: Confirmar Exclusão de Bot -->
              <div v-if="showDeleteBotModal" class="modal-overlay" @click="cancelDeleteBot">
                <div class="modal-content modal-confirm" @click.stop>
                  <div class="modal-header">
                    <div class="modal-icon-danger">
                      <i class="fa-solid fa-exclamation-triangle"></i>
                    </div>
                  </div>

                  <div class="modal-body">
                    <h3 class="modal-title-center">Desconectar Bot?</h3>
                    <p class="modal-description">
                      Você está prestes a desconectar o bot:
                    </p>
                    
                    <div class="bot-delete-info">
                      <div class="bot-delete-icon">
                        <i class="fa-brands fa-telegram"></i>
                      </div>
                      <div>
                        <strong>{{ botToDelete?.name }}</strong>
                        <span v-if="getBotUsername(botToDelete)">@{{ getBotUsername(botToDelete) }}</span>
                      </div>
                    </div>

                    <div class="modal-warning-box">
                      <i class="fa-solid fa-circle-info"></i>
                      <div>
                        <strong>Atenção:</strong> Os fluxos associados a este bot continuarão existindo, mas não funcionarão até que você conecte outro bot.
                      </div>
                    </div>
                  </div>

                  <div class="modal-footer">
                    <button class="btn btn-secondary" @click="cancelDeleteBot">
                      <i class="fa-solid fa-times"></i>
                      Cancelar
                    </button>
                    <button class="btn btn-danger" @click="confirmDeleteBot">
                      <i class="fa-solid fa-trash"></i>
                      Sim, Desconectar
                    </button>
                  </div>
                </div>
              </div>

              <!-- Tela 5: Sucesso -->
              <div v-else-if="telegramStep === 'success'" class="telegram-success">
                <div class="telegram-success-icon">
                  <i class="fa-solid fa-check-circle"></i>
                </div>
                <h2 class="telegram-section-title">Bot Conectado com Sucesso!</h2>
                <p class="telegram-section-subtitle">
                  Seu bot do Telegram está configurado e pronto para uso.
                </p>

                <div class="telegram-success-info">
                  <div class="telegram-info-item">
                    <i class="fa-solid fa-link"></i>
                    <div>
                      <label>Webhook URL</label>
                      <div class="telegram-webhook-display">
                        <code>{{ webhookUrl }}</code>
                        <button class="btn btn-sm btn-ghost" @click="copyWebhookUrl">
                          <i class="fa-solid fa-copy"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="telegram-success-actions">
                  <button class="btn btn-secondary" @click="telegramStep = 'list'">
                    <i class="fa-solid fa-list"></i>
                    Ver Meus Bots
                  </button>
                  <button class="btn btn-primary" @click="$router.push('/flows')">
                    <i class="fa-solid fa-arrow-right"></i>
                    Criar Fluxo de Automação
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { listChannels, createChannel, updateChannel, updateTelegramConfig, deleteChannel } from '@/api/channels'
import { useToast } from '@/composables/useToast'
import { useAuth } from '@/composables/useAuth'
import { listPlans } from '@/api/plans'
import { getMySubscription } from '@/api/subscription'
import { createCheckoutSession, createEnterpriseCheckoutSession, createPortalSession, getBillingStatus, getVpmEstimate } from '@/api/billing'
import { getTenantMe, updateTenantMe } from '@/api/tenants'

const timezoneOptions = [
  '(UTC-12:00) International Date Line West',
  '(UTC-08:00) Pacific Time (US & Canada)',
  '(UTC-06:00) Central Time (US & Canada)',
  '(UTC-03:00) Brasília Standard Time - São Paulo',
  '(UTC+00:00) London',
  '(UTC+01:00) Berlin',
  '(UTC+05:30) India Standard Time',
  '(UTC+09:00) Tokyo'
]

const statusMessage = ref('')
const activeTab = ref('Geral')
const toast = useToast()
const auth = useAuth()

// Geral (dados reais)
const tenantNameDraft = ref('')
const tenantEmail = ref('')
const tenantTimezoneDraft = ref('')
const savingGeneral = ref(false)

// Cobrança / Assinaturas (dados reais)
const plans = ref([])
const subscriptionData = ref(null)
const billingLoading = ref(false)
const billingStatus = ref(null)
const billingInterval = ref('monthly')
const vpmEstimate = ref(null)

// Enterprise — tabela de preços para calculo dinâmico
const _ENT_PRICE_TABLE = [
  [500, 24.50], [2500, 106.31], [5000, 206.27], [10000, 401.65],
  [15000, 593.80], [20000, 783.93], [30000, 1160.15], [40000, 1532.60],
  [50000, 1902.32], [60000, 2269.90], [70000, 2635.70], [80000, 2999.97],
  [90000, 3362.90], [100000, 3724.64], [120000, 4444.35], [140000, 5160.26],
  [160000, 5872.92], [180000, 6582.79], [200000, 7290.17], [300000, 10790.40],
  [400000, 14266.69], [500000, 17726.88], [600000, 21174.36], [700000, 24611.56],
  [800000, 28040.28], [900000, 31461.87], [1000000, 34877.31],
  [1200000, 41711.85], [1400000, 48467.37], [1600000, 55198.55],
  [1800000, 61908.60], [2000000, 68600.00],
]
const enterpriseContacts = ref(5000)
// Slider 0-100 mapeado em escala logarítmica: 500 → 2.000.000
const enterpriseSlider = ref(Math.round(Math.log(5000 / 500) / Math.log(4000) * 100))

// Sincroniza slider ⇒ contatos
watch(enterpriseSlider, (val) => {
  enterpriseContacts.value = Math.round(500 * Math.pow(4000, val / 100))
})
// Sincroniza digitação ⇒ slider
watch(enterpriseContacts, (val) => {
  const c = Number(val) || 500
  if (c >= 500 && c <= 2_000_000) {
    enterpriseSlider.value = Math.round(Math.log(c / 500) / Math.log(4000) * 100)
  }
})
const enterprisePrice = computed(() => {
  const c = Math.max(Number(enterpriseContacts.value) || 0, 0)
  if (c <= 0) return 999
  const last = _ENT_PRICE_TABLE[_ENT_PRICE_TABLE.length - 1]
  if (c >= last[0]) return Math.max(last[1] + Math.ceil((c - last[0]) / 1000) * 34.30, 999)
  const first = _ENT_PRICE_TABLE[0]
  if (c <= first[0]) return Math.max(first[1] * (c / first[0]), 999)
  for (let i = 1; i < _ENT_PRICE_TABLE.length; i++) {
    if (c <= _ENT_PRICE_TABLE[i][0]) {
      const [lc, lp] = _ENT_PRICE_TABLE[i - 1]
      const [hc, hp] = _ENT_PRICE_TABLE[i]
      const t = (c - lc) / (hc - lc)
      return Math.max(lp + t * (hp - lp), 999)
    }
  }
  return 999
})

const stripeConfigured = computed(() => !!billingStatus.value?.stripe_configured)
const hasStripeCustomer = computed(() => !!billingStatus.value?.has_customer)
const billingPortalDisabled = computed(
  () => billingLoading.value || !stripeConfigured.value || !hasStripeCustomer.value
)

// Telegram Config
const telegramStep = ref('intro') // intro, choose, create-new, connect-existing, success
const telegramChannels = ref([])
const selectedTelegramChannel = ref(null)
const telegramForm = ref({
  bot_name: '',
  bot_token: '',
  bot_username: ''
})
const webhookUrl = ref('')
const validatingToken = ref(false)
const tokenValidationResult = ref(null)
const loading = ref(false)
const loadingTelegram = ref(true)

// Estados para edição de bot
const showEditBotModal = ref(false)
const showDeleteBotModal = ref(false)
const botToDelete = ref(null)
const validatingEditToken = ref(false)
const editTokenValidation = ref(null)
const editBotForm = ref({
  channelId: null,
  name: '',
  bot_token: '',
  bot_username: '',
  originalName: '',
  originalToken: '',
  originalUsername: '',
  showToken: false,
  saving: false
})

const principalItems = [
  { label: 'Geral', iconClass: 'fa-solid fa-cog fa-lg' }
]
const billingItems = [
  { label: 'Cobrança', iconClass: 'fa-solid fa-credit-card fa-lg' },
  { label: 'Planos', iconClass: 'fa-solid fa-layer-group fa-lg' }
]
const telegramItems = [
  { label: 'Telegram', iconClass: 'fa-brands fa-telegram fa-lg' }
]
const menuSections = [
  { title: 'Conta', items: principalItems },
  { title: 'Financeiro', items: billingItems },
  { title: 'Canais', items: telegramItems }
]

// Telegram Functions
const loadTelegramChannels = async () => {
  loadingTelegram.value = true
  try {
    console.log('🔍 Carregando canais...')
    const allChannels = await listChannels()
    console.log('📦 Resposta da API (TODOS):', allChannels)
    console.log('📊 Total de canais (todos):', allChannels.length)
    
    // Exibir TODOS (ativos e inativos) no grid
    telegramChannels.value = allChannels.filter(ch => ch.type === 'telegram')
    
    console.log('📋 Total de canais Telegram:', telegramChannels.value.length)
    console.log('📊 DETALHES de cada canal:')
    telegramChannels.value.forEach(c => {
      console.log(`  - ID: ${c.id}, Nome: ${c.name}, Ativo: ${c.is_active}`)
    })
    
    // Se já existe um canal Telegram, usar o primeiro
    if (telegramChannels.value.length > 0) {
      selectedTelegramChannel.value = telegramChannels.value[0].id
    }
  } catch (error) {
    console.error('❌ Erro ao carregar canais Telegram:', error)
    console.error('📋 Detalhes do erro:', error.response?.data)
    showStatus('Erro ao carregar canais Telegram')
  } finally {
    loadingTelegram.value = false
  }
}

const validateTelegramToken = async () => {
  if (!telegramForm.value.bot_token) return
  
  validatingToken.value = true
  tokenValidationResult.value = null
  
  try {
    // Chamar API do Telegram para validar o token e pegar info do bot
    const response = await fetch(`https://api.telegram.org/bot${telegramForm.value.bot_token}/getMe`)
    const data = await response.json()
    
    if (data.ok && data.result) {
      const bot = data.result
      telegramForm.value.bot_username = bot.username
      
      tokenValidationResult.value = {
        success: true,
        message: `Bot encontrado: @${bot.username} (${bot.first_name})`
      }
      
      console.log('✅ Token válido! Bot:', bot)
    } else {
      tokenValidationResult.value = {
        success: false,
        message: data.description || 'Token inválido. Verifique e tente novamente.'
      }
      console.error('❌ Token inválido:', data)
    }
  } catch (error) {
    tokenValidationResult.value = {
      success: false,
      message: 'Erro ao validar token. Verifique sua conexão e tente novamente.'
    }
    console.error('❌ Erro na validação:', error)
  } finally {
    validatingToken.value = false
  }
}

const validateEditToken = async () => {
  if (!editBotForm.value.bot_token) return

  validatingEditToken.value = true
  editTokenValidation.value = null

  try {
    const response = await fetch(`https://api.telegram.org/bot${editBotForm.value.bot_token}/getMe`)
    const data = await response.json()

    if (data.ok && data.result) {
      const bot = data.result
      editBotForm.value.bot_username = bot.username || ''
      editTokenValidation.value = {
        success: true,
        message: `Bot encontrado: @${bot.username} (${bot.first_name || 'sem nome'})`
      }
      showStatus(`✅ Username detectado: @${bot.username}`)
      console.log('✅ Token válido no modo edição. Bot:', bot)
    } else {
      editTokenValidation.value = {
        success: false,
        message: data.description || 'Token inválido. Verifique e tente novamente.'
      }
      showStatus('❌ Token inválido para este bot')
      console.error('❌ Token inválido (edição):', data)
    }
  } catch (error) {
    editTokenValidation.value = {
      success: false,
      message: 'Erro ao validar token. Verifique sua conexão e tente novamente.'
    }
    showStatus('❌ Erro ao validar token')
    console.error('❌ Erro na validação (edição):', error)
  } finally {
    validatingEditToken.value = false
  }
}

const connectTelegramBot = async () => {
  console.log('🚀 connectTelegramBot chamado!')
  console.log('📝 Nome:', telegramForm.value.bot_name)
  console.log('📝 Token:', telegramForm.value.bot_token ? 'Presente' : 'Ausente')
  console.log('📋 Canais disponíveis:', telegramChannels.value)
  
  if (!telegramForm.value.bot_name || !telegramForm.value.bot_token) {
    showStatus('⚠️ Nome e token do bot são obrigatórios')
    return
  }
  
  // Verificar se o token já existe
  const existingBot = telegramChannels.value.find(ch => {
    try {
      const config = typeof ch.config === 'string' ? JSON.parse(ch.config) : ch.config || {}
      return config.bot_token === telegramForm.value.bot_token
    } catch (e) {
      return false
    }
  })
  
  if (existingBot) {
    showStatus('❌ Este bot já está conectado ao sistema!')
    toast.error(`Bot "${existingBot.name}" já está conectado com este token`)
    return
  }
  
  loading.value = true
  
  try {
    // SEMPRE criar um novo canal quando conectar um bot
    console.log('➕ Criando novo canal para o bot...')
    let channelId = null
    
    try {
      const newChannel = await createChannel({
        tenant_id: 1, // TODO: Obter do contexto do usuário logado
        type: 'telegram',
        name: telegramForm.value.bot_name,
        config: null
      })
      channelId = newChannel.id
      console.log(`✅ Novo canal criado: ${telegramForm.value.bot_name} (ID: ${channelId})`)
      
      // Recarregar a lista de canais
      await loadTelegramChannels()
    } catch (createError) {
      console.error('❌ Erro ao criar canal:', createError)
      console.error('❌ Detalhes do erro:', createError.response?.data)
      showStatus('❌ Erro ao criar canal Telegram')
      loading.value = false
      return
    }
    
    console.log('🔌 Conectando bot ao canal:', channelId)
    console.log('📝 Bot username a ser salvo:', telegramForm.value.bot_username)
    
    const result = await updateTelegramConfig(channelId, {
      bot_token: telegramForm.value.bot_token,
      bot_username: telegramForm.value.bot_username || ''
    })
    
    console.log('✅ Resultado da API:', result)
    
    // Confirmar que o username foi salvo
    try {
      const savedConfig = typeof result.config === 'string' 
        ? JSON.parse(result.config) 
        : result.config || {}
      
      if (savedConfig.bot_username) {
        console.log('✅ Bot username salvo com sucesso:', savedConfig.bot_username)
      } else {
        console.warn('⚠️ Bot username não foi salvo no config')
      }
    } catch (e) {
      console.error('⚠️ Erro ao verificar username salvo:', e)
    }
    
    // Extrair webhook_url do config
    try {
      const config = typeof result.config === 'string' 
        ? JSON.parse(result.config) 
        : result.config || {}
      
      webhookUrl.value = config.webhook_url || ''
      console.log('🔗 Webhook URL:', webhookUrl.value)
    } catch (e) {
      console.error('⚠️ Erro ao parsear config:', e)
      webhookUrl.value = ''
    }
    
    // Recarregar lista de canais
    await loadTelegramChannels()
    
    // Ir para tela de sucesso
    telegramStep.value = 'success'
    showStatus('✅ Bot conectado com sucesso!')
    console.log('🎉 Conexão concluída!')
  } catch (error) {
    console.error('❌ Erro ao conectar bot:', error)
    console.error('❌ Detalhes:', error.response?.data || error.message)
    showStatus(`❌ Erro: ${error.response?.data?.detail || 'Verifique o token'}`)
  } finally {
    loading.value = false
  }
}

const copyWebhookUrl = () => {
  if (webhookUrl.value) {
    navigator.clipboard.writeText(webhookUrl.value)
    showStatus('📋 URL copiada!')
  }
}

// Funções auxiliares para exibir dados dos bots
const getBotUsername = (channel) => {
  try {
    const config = typeof channel.config === 'string' 
      ? JSON.parse(channel.config) 
      : channel.config || {}
    const username = config.bot_username || ''
    console.log('Bot username para canal', channel.name, ':', username)
    return username
  } catch (e) {
    console.error('Erro ao obter username:', e)
    return ''
  }
}

const getBotToken = (channel) => {
  try {
    const config = typeof channel.config === 'string' 
      ? JSON.parse(channel.config) 
      : channel.config || {}
    return config.bot_token || ''
  } catch (e) {
    return ''
  }
}

const getWebhookUrl = (channel) => {
  try {
    const config = typeof channel.config === 'string' 
      ? JSON.parse(channel.config) 
      : channel.config || {}
    return config.webhook_url || ''
  } catch (e) {
    return ''
  }
}

const maskToken = (token) => {
  if (!token) return '••••••••••••••••'
  if (token.length <= 10) return token
  return token.substring(0, 8) + '••••••••' + token.substring(token.length - 4)
}

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text)
  showStatus('📋 Copiado!')
}

const viewBotDetails = (channel) => {
  const config = typeof channel.config === 'string' 
    ? JSON.parse(channel.config) 
    : channel.config || {}
  
  console.log('📋 Detalhes do Bot:', {
    id: channel.id,
    name: channel.name,
    username: config.bot_username,
    token: maskToken(config.bot_token),
    webhook: config.webhook_url,
    active: channel.is_active
  })
  
  showStatus('ℹ️ Detalhes exibidos no console')
}

const disconnectBot = (channel) => {
  botToDelete.value = channel
  showDeleteBotModal.value = true
}

const confirmDeleteBot = async () => {
  if (!botToDelete.value) return
  
  try {
    console.log('🗑️ Desconectando bot:', botToDelete.value.id)
    
    await deleteChannel(botToDelete.value.id)
    
    console.log('✅ Bot desconectado!')
    
    // Remover imediatamente da lista local
    telegramChannels.value = telegramChannels.value.filter(ch => ch.id !== botToDelete.value.id)
    
    toast.success('Bot desconectado com sucesso')
    
    // Recarregar lista de canais para sincronizar com backend
    await loadTelegramChannels()
    
    // Se estava na tela de sucesso, voltar para lista
    if (telegramStep.value === 'success') {
      telegramStep.value = 'list'
    }
  } catch (error) {
    console.error('❌ Erro ao desconectar bot:', error)
    toast.error('Erro ao desconectar bot')
  } finally {
    showDeleteBotModal.value = false
    botToDelete.value = null
  }
}

const cancelDeleteBot = () => {
  showDeleteBotModal.value = false
  botToDelete.value = null
}

const toggleBotStatus = async (channel) => {
  const newStatus = !channel.is_active
  const action = newStatus ? 'ativar' : 'desativar'
  
  try {
    console.log(`🔄 ${action} bot:`, channel.id, 'Status atual:', channel.is_active, '→ Novo:', newStatus)
    
    await updateChannel(channel.id, {
      is_active: newStatus
    })
    
    console.log('✅ Status atualizado no backend')
    toast.success(`✅ Bot ${newStatus ? 'ativado' : 'desativado'} com sucesso`)
    
    // Garantir que permanece na tela de lista ANTES de recarregar
    telegramStep.value = 'list'
    
    // Recarregar lista de canais
    await loadTelegramChannels()
    
    console.log('🔄 Lista recarregada!')
    console.log('📊 Total de canais:', telegramChannels.value.length)
    console.log('📊 Status dos canais:', telegramChannels.value.map(c => ({
      id: c.id,
      name: c.name,
      is_active: c.is_active
    })))
  } catch (error) {
    console.error(`❌ Erro ao ${action} bot:`, error)
    const status = error?.response?.status
    const detail = error?.response?.data?.detail
    const detailText = typeof detail === 'string'
      ? detail
      : (detail?.message || detail?.error || detail?.description)

    if (status === 502) {
      toast.error(`Falha ao ${action} bot (502). O servidor pode estar reiniciando ou fora do ar.`)
    } else if (detailText) {
      toast.error(`Erro ao ${action} bot: ${detailText}`)
    } else {
      toast.error(`Erro ao ${action} bot`)
    }
  }
}

let statusTimer

const showStatus = (message) => {
  statusMessage.value = message
  clearTimeout(statusTimer)
  statusTimer = setTimeout(() => {
    statusMessage.value = ''
  }, 2200)
}

const handleSignOut = () => {
  auth.logout()
}

const subscriptionStatusLabel = computed(() => {
  const status = subscriptionData.value?.status
  if (!status) return ''
  const map = {
    trial: 'TRIAL',
    active: 'ATIVA',
    past_due: 'PAGAMENTO PENDENTE',
    canceled: 'CANCELADA',
    expired: 'EXPIRADA'
  }
  return map[status] || String(status).toUpperCase()
})

const subscriptionPeriodLabel = computed(() => {
  const start = subscriptionData.value?.current_period_start
  const end = subscriptionData.value?.current_period_end
  if (!start && !end) return '—'
  return `${start || '—'} → ${end || '—'}`
})

const formatPrice = (v) => {
  const n = Number(v || 0)
  try {
    return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
  } catch {
    return `R$ ${n}`
  }
}

const planDetail = (plan) => {
  const parts = []
  if (plan?.max_contacts != null) parts.push(`${plan.max_contacts} contatos`)
  if (plan?.max_bots != null) parts.push(`${plan.max_bots} bots`)
  if (plan?.max_messages_per_month != null) parts.push(`${plan.max_messages_per_month} msgs/mês`)
  if (parts.length === 0) return plan?.description || '—'
  return parts.join(' • ')
}

const formatLimit = (value, { prefix = '', suffix = '' } = {}) => {
  if (value === null || value === undefined) return 'Ilimitado'
  return `${prefix}${value}${suffix}`
}

const planUi = (plan) => {
  const name = String(plan?.name || '').toLowerCase()

  const contactsValue = name === 'free'
    ? 'Até 100 contatos ativos'
    : name === 'pro'
      ? 'Até 2.500 contatos (fixo)'
      : 'Ilimitado (cobrado por volume)'

  const botsValue = name === 'free' ? '1' : name === 'pro' ? '3' : 'Ilimitado'
  const flowsValue = name === 'free' ? '1' : 'Ilimitados'
  const triggersValue = name === 'free' ? '1' : 'Ilimitados'
  const sequencesValue = name === 'free' ? '1' : 'Ilimitadas'
  const tagsValue = name === 'free' ? '1' : 'Ilimitadas'
  const usersValue = name === 'free' ? '1 (administrador)' : name === 'pro' ? '3 colaboradores' : 'Ilimitados'

  const apiValue = plan?.has_api_access ? 'Incluído' : 'Em breve'
  const webhooksValue = plan?.has_webhooks ? 'Incluído' : 'Em breve'

  let title = plan?.description || '—'
  let subtitle = ''

  const vpmLine = plan?.vpm_price
    ? `R$ ${plan.vpm_price} por 1.000 contatos ativos${plan?.min_monthly ? ` • mínimo ${formatPrice(plan.min_monthly)}/mês` : ''}`
    : ''

  if (name === 'free') {
    title = 'Free — até 100 contatos ativos para testar.'
    subtitle = '1 fluxo, 1 gatilho, 1 sequência, 1 tag. Ideal para validar antes de escalar.'
  } else if (name === 'pro') {
    title = 'Pro — automação ilimitada para crescer.'
    subtitle = vpmLine || 'Você paga conforme seu volume de contatos ativos.'
  } else if (name === 'unlimited') {
    title = 'Enterprise — menor VPM + prioridade.'
    subtitle = vpmLine || 'Menor custo por volume e atendimento prioritário.'
  }

  const items = [
    { label: 'Canal', value: 'Telegram' },
    { label: 'Bots no Telegram', value: botsValue },
    { label: 'Contatos ativos', value: contactsValue },
    { label: 'Fluxos de automação', value: flowsValue },
    { label: 'Gatilhos de entrada', value: triggersValue },
    { label: 'Sequências de mensagens', value: sequencesValue },
    { label: 'Tags de segmentação', value: tagsValue },
    { label: 'Usuários', value: usersValue },
    { label: 'API pública', value: apiValue },
    { label: 'Webhooks', value: webhooksValue }
  ]

  if (plan?.has_priority_support) items.push({ label: 'Suporte', value: 'Prioritário' })
  if (plan?.has_early_access) items.push({ label: 'Novidades', value: 'Acesso antecipado' })

  const footnote = name === 'free'
    ? 'Contato ativo = interagiu nos últimos 30 dias ou teve mensagem no mês.'
    : 'VPM: contatos ativos em blocos de 1.000 (arredonda para cima) + mínimo mensal.'

  return { title, subtitle, items, footnote }
}

const isCurrentPlan = (plan) => {
  const cur = subscriptionData.value?.plan?.id
  return !!cur && Number(cur) === Number(plan?.id)
}

const usageLabel = (k) => {
  const map = {
    bots: 'Bots',
    contacts: 'Contatos',
    active_contacts: 'Contatos ativos',
    messages_per_month: 'Mensagens/mês',
    flows: 'Fluxos',
    sequences: 'Sequências',
    tags: 'Tags',
  }
  return map[k] || k
}

const saveGeneral = async () => {
  savingGeneral.value = true
  try {
    const payload = {
      name: tenantNameDraft.value,
      timezone: tenantTimezoneDraft.value
    }
    const updated = await updateTenantMe(payload)
    tenantNameDraft.value = updated?.name || ''
    tenantEmail.value = updated?.email || ''
    tenantTimezoneDraft.value = updated?.timezone || ''
    toast.success('Configurações salvas')
  } catch (e) {
    console.error(e)
    toast.error('Erro ao salvar configurações')
  } finally {
    savingGeneral.value = false
  }
}

const startCheckout = async (plan) => {
  if (!plan?.id) return
  if (!stripeConfigured.value) {
    toast.error('Stripe não está configurado no backend')
    return
  }
  if (!plan?.stripe_price_id_monthly) {
    toast.error('Este plano não possui preço fixo — use o botão "Contratar"')
    return
  }
  billingLoading.value = true
  try {
    const { url } = await createCheckoutSession(plan.id, 'monthly')
    if (url) window.location.href = url
  } catch (e) {
    console.error(e)
    toast.error('Erro ao iniciar checkout')
  } finally {
    billingLoading.value = false
  }
}

const startEnterpriseCheckout = async () => {
  if (!stripeConfigured.value) {
    toast.error('Stripe não está configurado no backend')
    return
  }
  const contacts = Math.max(Number(enterpriseContacts.value) || 0, 500)
  billingLoading.value = true
  try {
    const { url } = await createEnterpriseCheckoutSession(contacts)
    if (url) window.location.href = url
  } catch (e) {
    console.error(e)
    toast.error('Erro ao iniciar checkout Enterprise')
  } finally {
    billingLoading.value = false
  }
}

const openBillingPortal = async () => {
  if (!stripeConfigured.value) {
    toast.error('Stripe não está configurado no backend')
    return
  }
  if (!hasStripeCustomer.value) {
    toast.error('Nenhum cliente Stripe associado (faça uma assinatura primeiro)')
    return
  }
  billingLoading.value = true
  try {
    const { url } = await createPortalSession()
    if (url) window.location.href = url
  } catch (e) {
    console.error(e)
    toast.error('Erro ao abrir portal de cobrança')
  } finally {
    billingLoading.value = false
  }
}

const loadBillingData = async () => {
  try {
    plans.value = await listPlans()
  } catch (e) {
    console.error(e)
    plans.value = []
  }

  try {
    subscriptionData.value = await getMySubscription()
  } catch (e) {
    console.error(e)
    subscriptionData.value = null
  }

  try {
    billingStatus.value = await getBillingStatus()
  } catch (e) {
    console.error(e)
    billingStatus.value = null
  }

  try {
    const est = await getVpmEstimate()
    vpmEstimate.value = est?.is_vpm_plan ? est : null
  } catch (e) {
    vpmEstimate.value = null
  }
}

const loadTenantSettings = async () => {
  try {
    const t = await getTenantMe()
    tenantNameDraft.value = t?.name || ''
    tenantEmail.value = t?.email || ''
    tenantTimezoneDraft.value = t?.timezone || ''
  } catch (e) {
    console.error(e)
  }
}

const openNewBotForm = () => {
  // Resetar formulário
  telegramForm.value = {
    bot_name: '',
    bot_token: '',
    bot_username: ''
  }
  telegramStep.value = 'intro'
}

// Funções para editar nome do bot
const openEditBotModal = (channel) => {
  // Reset validação
  editTokenValidation.value = null
  validatingEditToken.value = false

  let config = {}
  try {
    config = typeof channel.config === 'string'
      ? JSON.parse(channel.config || '{}')
      : channel.config || {}
  } catch (e) {
    config = {}
  }

  editBotForm.value = {
    channelId: channel.id,
    name: channel.name,
    bot_token: config.bot_token || '',
    bot_username: (config.bot_username || '').replace('@', ''),
    admin_telegram_chat_id: config.admin_telegram_chat_id || '',
    originalName: channel.name,
    originalToken: config.bot_token || '',
    originalUsername: (config.bot_username || '').replace('@', ''),
    originalAdminChatId: config.admin_telegram_chat_id || '',
    showToken: false,
    saving: false
  }
  showEditBotModal.value = true
}

const closeEditBotModal = () => {
  showEditBotModal.value = false
  editTokenValidation.value = null
  validatingEditToken.value = false
  editBotForm.value = {
    channelId: null,
    name: '',
    bot_token: '',
    bot_username: '',
    admin_telegram_chat_id: '',
    originalName: '',
    originalToken: '',
    originalUsername: '',
    originalAdminChatId: '',
    showToken: false,
    saving: false
  }
}

const saveBotName = async () => {
  if (!editBotForm.value.name || !editBotForm.value.channelId) {
    showStatus('⚠️ Nome do bot é obrigatório')
    return
  }

  if (!editBotForm.value.bot_token) {
    showStatus('⚠️ Token do bot é obrigatório')
    return
  }

  // Verificar se algo mudou
  const nameChanged = editBotForm.value.name !== editBotForm.value.originalName
  const tokenChanged = editBotForm.value.bot_token !== editBotForm.value.originalToken
  const usernameChanged = editBotForm.value.bot_username !== editBotForm.value.originalUsername
  const adminChatIdChanged = editBotForm.value.admin_telegram_chat_id !== editBotForm.value.originalAdminChatId

  if (!nameChanged && !tokenChanged && !usernameChanged && !adminChatIdChanged) {
    closeEditBotModal()
    return
  }

  editBotForm.value.saving = true

  try {
    // Preparar payload com apenas os campos que mudaram
    const payload = {}
    
    if (nameChanged) {
      payload.name = editBotForm.value.name
    }
    
    if (tokenChanged) {
      payload.bot_token = editBotForm.value.bot_token
    }

    if (usernameChanged) {
      payload.bot_username = editBotForm.value.bot_username
    }

    if (adminChatIdChanged) {
      payload.admin_telegram_chat_id = editBotForm.value.admin_telegram_chat_id
    }

    // Atualizar o canal
    await updateChannel(editBotForm.value.channelId, payload)

    showStatus('Bot atualizado com sucesso!')
    
    // Recarregar lista de canais
    await loadTelegramChannels()
    
    // Fechar modal
    closeEditBotModal()
  } catch (error) {
    console.error('Erro ao atualizar bot:', error)
    showStatus(`Erro: ${error.response?.data?.detail || 'Não foi possível atualizar'}`)
  } finally {
    editBotForm.value.saving = false
  }
}

const selectTab = (label) => {
  activeTab.value = label
  
  // Se selecionou Telegram, definir o step inicial
  if (label === 'Telegram') {
    if (telegramChannels.value.length > 0) {
      telegramStep.value = 'list'
    } else {
      telegramStep.value = 'intro'
    }
  }
}

// Carregar canais ao montar o componente
onMounted(async () => {
  let checkoutSuccess = false
  try {
    const params = new URLSearchParams(window.location.search || '')
    const tab = params.get('tab')
    if (tab) activeTab.value = tab
    checkoutSuccess = params.get('checkout') === 'success'
    // Limpa o query string da URL sem recarregar a página
    if (checkoutSuccess) {
      const cleanUrl = window.location.pathname + (tab ? `?tab=${encodeURIComponent(tab)}` : '')
      window.history.replaceState({}, '', cleanUrl)
    }
  } catch {}

  await loadTenantSettings()
  await loadBillingData()
  await loadTelegramChannels()

  if (checkoutSuccess) {
    toast.success('🎉 Plano ativado com sucesso! Bem-vindo ao Pro.')
    // Aguarda 3s e recarrega novamente para garantir que o webhook já foi processado
    setTimeout(async () => {
      await loadBillingData()
    }, 3000)
  }

  if (telegramChannels.value.length > 0) {
    telegramStep.value = 'list'
  } else {
    telegramStep.value = 'intro'
  }
})
</script>

<style scoped>
/* Layout Principal */
.settings-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.settings-layout {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

/* Menu Horizontal Superior */
.settings-top-nav {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  padding: 10px 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  flex-shrink: 0;
}

.settings-nav-divider {
  width: 1px;
  height: 20px;
  background: var(--border);
  flex-shrink: 0;
  margin: 0 6px;
}

.settings-nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.settings-nav-item i {
  font-size: 16px;
}

.settings-nav-item:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-color: var(--border);
}

.settings-nav-item.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.settings-nav-item.active:hover {
  background: var(--primary-hover);
  border-color: var(--primary-hover);
}

/* === Billing Toggle in Settings (segmented) === */
.lp-billing-toggle-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 16px;
}

.lp-billing-toggle {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0;
  padding: 4px;
  border-radius: 999px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
}

.lp-toggle-thumb {
  position: absolute;
  top: 4px;
  left: 4px;
  height: calc(100% - 8px);
  width: calc(50% - 4px);
  border-radius: 999px;
  background: var(--bg-card);
  border: 1px solid var(--border);
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
  padding: 8px 14px;
  min-width: 100px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  cursor: pointer;
  user-select: none;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-muted);
  transition: color 0.2s ease;
}

.lp-toggle-option.active {
  color: var(--text-primary);
}

.lp-toggle-option:focus-visible {
  outline: 2px solid rgba(34, 197, 94, 0.45);
  outline-offset: 2px;
}

.lp-discount-badge {
  background: rgba(34, 197, 94, 0.15);
  color: var(--primary);
  border: 1px solid rgba(34, 197, 94, 0.3);
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 800;
  white-space: nowrap;
}

.settings-content {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.settings-content-body {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  width: 100%;
}

/* Telegram Onboarding Container */
/* ── Telegram loading skeleton ── */
@keyframes tg-shimmer {
  0%   { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}

.tg-loading {
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
  padding-top: 8px;
}

.tg-loading-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.tg-skel {
  background: linear-gradient(90deg, #1a1a1a 25%, #2a2a2a 50%, #1a1a1a 75%);
  background-size: 800px 100%;
  animation: tg-shimmer 1.4s infinite linear;
  border-radius: 6px;
}

.tg-skel-title  { width: 220px; height: 28px; }
.tg-skel-btn    { width: 150px; height: 36px; border-radius: 20px; }

.tg-skel-line         { height: 13px; margin-bottom: 8px; }
.tg-skel-line--lg     { width: 60%; }
.tg-skel-line--sm     { width: 40%; opacity: 0.6; }

.tg-loading-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tg-skel-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
}

.tg-skel-card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  flex-shrink: 0;
  background: linear-gradient(90deg, #1e1e1e 25%, #2e2e2e 50%, #1e1e1e 75%);
  background-size: 800px 100%;
  animation: tg-shimmer 1.4s infinite linear;
}

.tg-skel-card-body {
  flex: 1;
}

.telegram-onboarding {
  max-width: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100%;
}

.telegram-form,
.telegram-intro,
.telegram-choose,
.telegram-success,
.telegram-bots-list {
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
}

/* Grid de Bots */
.telegram-bots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

/* Card do Bot - Design Compacto */
.bot-card {
  background: var(--bg-primary);
  border: 2px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.bot-card:hover {
  box-shadow: 0 4px 12px rgba(0, 136, 204, 0.1);
}

/* Card Ativo - Borda Verde */
.bot-card-active {
  border-color: #10b981;
  background: var(--bg-primary);
}

.bot-card-active:hover {
  border-color: #059669;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

/* Card Inativo - Borda Vermelha */
.bot-card-inactive {
  border-color: #ef4444;
  background: var(--bg-secondary);
}

.bot-card-inactive:hover {
  border-color: #dc2626;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.bot-card-inactive .bot-card-icon {
  background: linear-gradient(135deg, #6b7280 0%, #9ca3af 100%);
}

.bot-card-inactive .bot-card-title {
  color: var(--text-secondary);
}

/* Main Content */
.bot-card-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  gap: 12px;
}

.bot-card-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.bot-card-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #0088cc 0%, #229ED9 100%);
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.bot-card-icon i {
  font-size: 20px;
}

.bot-card-info-main {
  flex: 1;
  min-width: 0;
}

.bot-card-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bot-card-username {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #0088cc;
  font-size: 0.8125rem;
  font-weight: 500;
}

.bot-card-username i {
  font-size: 0.75rem;
  opacity: 0.8;
}

.bot-card-username-missing {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-tertiary);
  font-size: 0.8125rem;
  font-style: italic;
}

.bot-card-username-missing i {
  font-size: 0.75rem;
}

.bot-card-right {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;
  flex-shrink: 0;
  cursor: pointer;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border);
  transition: all 0.3s;
}

/* === Assinaturas — card grid === */
.settings-subs-wrap {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
}

/* Tag status colors */
.settings-subscriptions-tag.tag--active {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.settings-subscriptions-tag.tag--inactive {
  background: rgba(248, 113, 113, 0.15);
  color: #ef4444;
  border: 1px solid rgba(248, 113, 113, 0.3);
}

.settings-subscriptions-tag.tag--warning {
  background: rgba(251, 191, 36, 0.15);
  color: #f59e0b;
  border: 1px solid rgba(251, 191, 36, 0.3);
}

.plan-yearly-badge {
  display: inline-block;
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.3);
  font-size: 0.65rem;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 4px;
  margin-left: 4px;
  vertical-align: middle;
}

.settings-subs-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.settings-subs-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.settings-subs-title {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.settings-subs-header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 3 cards side by side */
.plans-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  width: 100%;
}

.plan-card {
  position: relative;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(15, 23, 42, 0.6);
  padding: 28px 24px 22px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: visible;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.plan-card:hover {
  border-color: rgba(79, 70, 229, 0.5);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.09);
}

.plan-card--current {
  border-color: #4f46e5;
  background: rgba(79, 70, 229, 0.07);
}

.plan-card-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: #4f46e5;
  color: #fff;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 3px 14px;
  border-radius: 99px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  white-space: nowrap;
}

.plan-card-name {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0 0 2px;
}

.plan-card-price-from {
  display: block;
  font-size: 0.68rem;
  font-weight: 500;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: -2px;
}

.plan-card-price-main {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.1;
  display: block;
}

.plan-card-price-main small {
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-left: 3px;
}

.plan-card-price-sub {
  display: block;
  font-size: 0.75rem;
  color: var(--text-tertiary);
  margin-top: 2px;
}

.enterprise-picker {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.enterprise-picker-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.enterprise-picker-label {
  font-size: 0.72rem;
  color: var(--text-secondary);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  white-space: nowrap;
}

.enterprise-picker-input {
  background: rgba(148, 163, 184, 0.08);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 8px;
  padding: 4px 8px;
  color: var(--text-primary);
  font-size: 0.85rem;
  width: 110px;
  text-align: right;
  outline: none;
}
.enterprise-picker-input:focus {
  border-color: #22c55e;
}

.enterprise-picker-range {
  width: 100%;
  height: 4px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(148, 163, 184, 0.2);
  border-radius: 4px;
  cursor: pointer;
  outline: none;
}
.enterprise-picker-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #22c55e;
  cursor: pointer;
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.5);
}
.enterprise-picker-range::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #22c55e;
  border: none;
  cursor: pointer;
}

.enterprise-picker-ticks {
  display: flex;
  justify-content: space-between;
  font-size: 0.65rem;
  color: #475569;
  margin-top: -4px;
}

.enterprise-picker-price {
  font-weight: 800;
  font-size: 1.15rem;
  color: #22c55e;
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.enterprise-picker-price small {
  font-size: 0.75rem;
  font-weight: 500;
  color: #64748b;
}

.enterprise-picker-min-badge {
  font-size: 0.65rem;
  font-weight: 600;
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.25);
  border-radius: 999px;
  padding: 1px 7px;
  margin-left: 4px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.plan-card-divider {
  height: 1px;
  background: rgba(148, 163, 184, 0.15);
}

.plan-card-features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 9px;
  flex: 1;
}

.plan-card-features li {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 0.84rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

.plan-card-features li i {
  color: #22c55e;
  font-size: 0.72rem;
  flex-shrink: 0;
}

.plan-card-features li b {
  color: var(--text-primary);
  font-weight: 700;
}

.plan-card-btn {
  width: 100%;
  flex-shrink: 0;
  font-size: 0.92rem;
  padding: 11px 0;
  margin-top: 4px;
}

.subs-usage-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  padding: 10px 16px;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.4);
  font-size: 0.82rem;
  color: var(--text-secondary);
  border: 1px solid rgba(148, 163, 184, 0.18);
}

.subs-usage-bar-label {
  color: var(--text-tertiary);
  font-weight: 600;
}

.subs-usage-bar-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.subs-usage-bar-item b {
  color: var(--text-primary);
  font-weight: 700;
}

.subs-contracted {
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--accent) 30%, transparent);
  border-radius: 6px;
  padding: 2px 10px;
  font-size: 0.82rem;
  font-weight: 600;
}

.subs-contracted b {
  color: var(--accent);
}

/* === Plans (Assinaturas) details (legacy) === */
.plan-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.plan-details-title {
  font-weight: 700;
  color: var(--text-primary);
  font-size: 0.92rem;
  line-height: 1.25;
}

.plan-details-sub {
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.35;
}

.plan-details-list {
  list-style: none;
  padding: 0;
  margin: 2px 0 0;
  display: grid;
  gap: 4px;
}

.plan-details-list li {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
}

.plan-details-k {
  color: var(--text-tertiary);
  font-size: 0.8rem;
  white-space: nowrap;
}

.plan-details-v {
  color: var(--text-primary);
  font-size: 0.8rem;
  font-weight: 600;
  text-align: right;
}

.plan-details-foot {
  margin-top: 4px;
  color: var(--text-tertiary);
  font-size: 0.78rem;
}

.plan-price {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.plan-price-main {
  font-weight: 700;
  color: var(--text-primary);
}

.plan-price-sub {
  color: var(--text-tertiary);
  font-size: 0.8rem;
}

/* === VPM Estimate Widget === */
.vpm-estimate-widget {
  margin: 16px 0;
  padding: 16px;
  border-radius: 12px;
  background: rgba(251, 191, 36, 0.06);
  border: 1px solid rgba(251, 191, 36, 0.18);
}

.vpm-estimate-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 12px;
}

.vpm-estimate-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.vpm-estimate-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.vpm-estimate-item--total {
  grid-column: 1 / -1;
  padding-top: 8px;
  border-top: 1px solid rgba(251, 191, 36, 0.15);
}

.vpm-estimate-label {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  font-weight: 500;
}

.vpm-estimate-value {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.vpm-estimate-value--hl {
  font-size: 1rem;
  color: #fbbf24;
}

.vpm-min-badge {
  font-size: 0.65rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 2px 7px;
  border-radius: 999px;
  background: rgba(251, 191, 36, 0.15);
  border: 1px solid rgba(251, 191, 36, 0.3);
  color: #fbbf24;
}

.vpm-estimate-note {
  margin-top: 10px;
  font-size: 0.72rem;
  color: var(--text-tertiary);
  font-style: italic;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: all 0.3s;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.toggle-switch input:checked + .toggle-slider {
  background-color: #10b981;
  border-color: #10b981;
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(22px);
}

/* Actions */
.bot-card-actions {
  padding: 10px 14px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border);
  display: flex;
  gap: 8px;
}

.btn-card-action {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 7px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-card-action:hover:not(:disabled) {
  border-color: #0088cc;
  color: #0088cc;
  background: rgba(0, 136, 204, 0.03);
}

.btn-card-action i {
  font-size: 0.875rem;
}

.btn-card-danger {
  border-color: rgba(239, 68, 68, 0.25) !important;
  color: #ef4444 !important;
}

.btn-card-danger:hover:not(:disabled) {
  border-color: #ef4444 !important;
  background: rgba(239, 68, 68, 0.06) !important;
  color: #dc2626 !important;
}

.btn-card-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsivo */
@media (max-width: 768px) {
  .telegram-bots-grid {
    grid-template-columns: 1fr;
  }
  
  .bot-card {
    min-width: 100%;
  }
  
  .bot-card-footer {
    flex-wrap: wrap;
  }
  
  .btn-card {
    flex: 1 1 auto;
  }
}

@media (min-width: 1200px) {
  .telegram-bots-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.form-hint {
  display: block;
  margin-top: 6px;
  font-size: 0.8125rem;
  color: var(--muted);
  line-height: 1.4;
}

/* Modal de Edição */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6); /* mais escuro para aumentar contraste */
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(1px); /* menos blur para não “lavar” o conteúdo */
}

.modal-content {
  background: rgba(17, 24, 39, 0.98); /* quase sólido para melhor leitura */
  border-radius: 14px;
  box-shadow: 0 26px 70px rgba(0, 0, 0, 0.55);
  max-width: 540px;
  width: 90%;
  max-height: 90vh;
  overflow: auto;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.modal-edit-bot {
  max-width: 520px;
}

.modal-header {
  padding: 24px 24px 16px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-close {
  background: none;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--muted);
  transition: all 0.2s;
}

.modal-close:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.modal-body {
  padding: 22px 24px;
  background: rgba(255, 255, 255, 0.01);
}

.modal-warning {
  display: flex;
  align-items: start;
  gap: 12px;
  padding: 14px 16px;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 8px;
  color: #fbbf24;
  font-size: 13px;
  margin-top: 16px;
  line-height: 1.5;
}

.modal-warning i {
  font-size: 18px;
  margin-top: 2px;
  flex-shrink: 0;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.form-group {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.form-input-lg {
  width: 100%;
  padding: 12px 16px;
  font-size: 1rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  transition: all 0.2s;
}

.form-input-lg:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* Responsividade */
@media (max-width: 1200px) {
  .settings-top-nav {
    padding: 12px 16px;
    gap: 6px;
  }
}

@media (max-width: 768px) {
  .settings-top-nav {
    flex-wrap: wrap;
    gap: 6px;
  }

  .settings-nav-divider {
    display: none;
  }

  .settings-nav-item {
    flex: 1;
    min-width: 120px;
    justify-content: center;
  }
}

.btn-lg {
  padding: 16px 32px;
  font-size: 1.125rem;
  font-weight: 600;
  position: relative;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Token Validation */
.token-input-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn-validate-token {
  align-self: flex-start;
  display: flex;
  align-items: center;
  gap: 8px;
}

.token-validation-result {
  display: flex;
  align-items: start;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  margin-top: 10px;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.token-validation-result.success {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #059669;
}

.token-validation-result.error {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #dc2626;
}

.token-validation-result i {
  font-size: 1.5rem;
  flex-shrink: 0;
  margin-top: 2px;
}

.token-validation-result div {
  flex: 1;
}

.token-validation-result strong {
  display: block;
  font-size: 0.9375rem;
  font-weight: 700;
  margin-bottom: 4px;
}

.token-validation-result p {
  font-size: 0.875rem;
  margin: 0;
  opacity: 0.9;
}

/* Bot Username Display */
.bot-username-display {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: linear-gradient(135deg, rgba(0, 136, 204, 0.1) 0%, rgba(34, 158, 217, 0.1) 100%);
  border: 2px solid rgba(0, 136, 204, 0.3);
  border-radius: 10px;
  color: #0088cc;
  font-size: 1rem;
  font-weight: 600;
}

.bot-username-display i {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-left: auto;
}

.badge-success {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #059669;
}

/* Classes de texto */
.text-success {
  color: #10b981;
  font-weight: 600;
}

.text-muted {
  color: var(--text-tertiary);
}

/* Mensagem de sem bots */
.no-bots-message {
  text-align: center;
  padding: 40px 20px;
  background: var(--bg-secondary);
  border: 2px dashed var(--border);
  border-radius: 12px;
  margin-top: 16px;
}

.no-bots-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, rgba(0, 136, 204, 0.1) 0%, rgba(34, 158, 217, 0.1) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0088cc;
}

.no-bots-icon i {
  font-size: 32px;
}

.no-bots-message h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.no-bots-message p {
  font-size: 0.9375rem;
  color: var(--text-secondary);
  margin: 0;
  max-width: 400px;
  margin: 0 auto;
}

/* Modal de Confirmação */
.modal-confirm {
  max-width: 500px;
  text-align: center;
}

.modal-icon-danger {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
  border: 3px solid rgba(239, 68, 68, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ef4444;
  font-size: 36px;
  animation: scaleIn 0.3s ease-out;
}

@keyframes scaleIn {
  from {
    transform: scale(0.5);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.modal-title-center {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.modal-description {
  font-size: 0.9375rem;
  color: var(--text-secondary);
  margin: 0 0 20px 0;
  line-height: 1.6;
}

.bot-delete-info {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  border-radius: 12px;
  margin-bottom: 20px;
}

.bot-delete-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #0088cc 0%, #229ED9 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  flex-shrink: 0;
}

.bot-delete-info div {
  text-align: left;
  flex: 1;
}

.bot-delete-info strong {
  display: block;
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.bot-delete-info span {
  font-size: 0.9375rem;
  color: #0088cc;
  font-weight: 600;
}

.modal-warning-box {
  display: flex;
  align-items: start;
  gap: 12px;
  padding: 14px 16px;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 10px;
  text-align: left;
}

.modal-warning-box i {
  color: #f59e0b;
  font-size: 1.25rem;
  flex-shrink: 0;
  margin-top: 2px;
}

.modal-warning-box div {
  flex: 1;
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.modal-warning-box strong {
  color: var(--text-primary);
  font-weight: 700;
}
</style>

