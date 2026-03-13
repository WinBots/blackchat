<template>
  <AppLayout>

    <!-- ========== LOADING SKELETON ========== -->
    <transition name="fe-loader">
      <div v-if="isPageLoading" class="fe-loader">
        <!-- Simulated header -->
        <div class="fe-loader-header">
          <div class="fe-loader-row" style="margin-bottom:12px;">
            <div class="fe-sk fe-sk-chip" style="width:60px;"></div>
            <div class="fe-sk fe-sk-chip" style="width:80px;"></div>
          </div>
          <div class="fe-sk fe-sk-title" style="width:220px;"></div>
          <div class="fe-sk fe-sk-text" style="width:380px;margin-top:10px;"></div>
          <div class="fe-loader-row" style="margin-top:20px;gap:8px;">
            <div class="fe-sk fe-sk-btn" style="width:140px;"></div>
            <div class="fe-sk fe-sk-btn" style="width:110px;"></div>
            <div class="fe-sk fe-sk-btn" style="width:110px;"></div>
            <div class="fe-sk fe-sk-btn-primary" style="width:90px;"></div>
          </div>
        </div>

        <!-- Simulated canvas -->
        <div class="fe-loader-canvas">
          <!-- Background grid dots -->
          <div class="fe-loader-grid"></div>

          <!-- Fake nodes -->
          <div class="fe-loader-nodes">
            <div class="fe-loader-node" style="top:80px;left:60px;width:220px;">
              <div class="fe-sk fe-sk-node-icon" style="background:linear-gradient(135deg,#22c55e,#16a34a);"></div>
              <div style="flex:1;">
                <div class="fe-sk fe-sk-node-title" style="width:100px;"></div>
                <div class="fe-sk fe-sk-node-text" style="width:140px;"></div>
              </div>
            </div>
            <div class="fe-loader-node-body" style="top:160px;left:60px;width:220px;height:90px;"></div>

            <div class="fe-loader-node" style="top:80px;left:360px;width:220px;">
              <div class="fe-sk fe-sk-node-icon" style="background:linear-gradient(135deg,#229ED9,#1E88E5);"></div>
              <div style="flex:1;">
                <div class="fe-sk fe-sk-node-title" style="width:110px;"></div>
                <div class="fe-sk fe-sk-node-text" style="width:150px;"></div>
              </div>
            </div>
            <div class="fe-loader-node-body" style="top:160px;left:360px;width:220px;height:120px;"></div>

            <div class="fe-loader-node" style="top:80px;left:660px;width:220px;">
              <div class="fe-sk fe-sk-node-icon" style="background:linear-gradient(135deg,#f59e0b,#d97706);"></div>
              <div style="flex:1;">
                <div class="fe-sk fe-sk-node-title" style="width:90px;"></div>
                <div class="fe-sk fe-sk-node-text" style="width:130px;"></div>
              </div>
            </div>
            <div class="fe-loader-node-body" style="top:160px;left:660px;width:220px;height:70px;"></div>

            <div class="fe-loader-node" style="top:340px;left:200px;width:220px;">
              <div class="fe-sk fe-sk-node-icon" style="background:linear-gradient(135deg,#8b5cf6,#7c3aed);"></div>
              <div style="flex:1;">
                <div class="fe-sk fe-sk-node-title" style="width:120px;"></div>
                <div class="fe-sk fe-sk-node-text" style="width:160px;"></div>
              </div>
            </div>
            <div class="fe-loader-node-body" style="top:420px;left:200px;width:220px;height:80px;"></div>
          </div>

          <!-- Central spinner -->
          <div class="fe-loader-center">
            <div class="fe-loader-ring">
              <div class="fe-loader-ring-inner"></div>
            </div>
            <p class="fe-loader-label">Carregando fluxo...</p>
          </div>
        </div>
      </div>
    </transition>

    <!-- ========== CONTEÚDO REAL ========== -->
    <!-- Header -->
    <div class="card flow-header-card" v-if="flow" v-show="!isPageLoading">
      <div class="page-header flow-page-header">
        <div>
          <div class="flow-header-top">
            <button class="btn btn-ghost btn-sm" @click="$router.back()">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="19" y1="12" x2="5" y2="12"/>
                <polyline points="12 19 5 12 12 5"/>
              </svg>
              Voltar
            </button>
            <span class="badge badge-muted" style="font-size: 0.6875rem;">ID #{{ flow.id }}</span>
            <span class="badge" :class="flow.is_active ? 'badge-success' : 'badge-muted'" style="font-size: 0.6875rem;">
              {{ flow.is_active ? 'Ativo' : 'Inativo' }}
            </span>
          </div>
          <h2 class="page-title">{{ flow.name }}</h2>
          <p class="page-description">
            Arraste os blocos livremente • Conecte saídas (↘) com entradas (↖) • Use scroll para zoom
          </p>
        </div>
        <div style="display: flex; gap: 8px;">
          <button class="btn btn-secondary" @click="showTriggerModal = true">
            <i class="fa-solid fa-bolt"></i>
            Adicionar Gatilho
          </button>
          <button class="btn btn-secondary" @click="resetZoom">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              <line x1="11" y1="8" x2="11" y2="14"/>
              <line x1="8" y1="11" x2="14" y2="11"/>
            </svg>
            Reset Zoom
          </button>
          <button class="btn btn-secondary" @click="saveWorkflow" :disabled="isSaving">
            <svg v-if="!isSaving" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
              <polyline points="17 21 17 13 7 13 7 21"/>
              <polyline points="7 3 7 8 15 8"/>
            </svg>
            <svg v-else class="loading-spinner" width="16" height="16" viewBox="0 0 24 24"></svg>
            {{ isSaving ? 'Salvando...' : 'Salvar' }}
          </button>
          <button class="btn-add-block-circle" @click="showAddBlockModal = true; blockSearch = ''; activeBlockCat = 'inicio'">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Flow Editor Layout -->
      <div class="flow-editor-layout">
        <!-- Painel Lateral de Edição -->
        <aside
          class="flow-editor-sidebar"
          v-if="selectedStep"
          ref="sidebarRootRef"
          @focusin="handleSidebarFocusIn"
          @focusout="handleSidebarFocusOut"
          @mousedown="handleSidebarMouseDown"
        >
          <div class="sidebar-header">
            <div class="sidebar-header-icon">
              <i class="fa-solid fa-message"></i>
            </div>
            <input 
              v-model="selectedStep.name" 
              class="sidebar-title-input"
              placeholder="Nome do Passo"
              @blur="autoSave"
            />
            <button class="sidebar-close-btn" @click="selectedStep = null">
              <i class="fa-solid fa-times"></i>
            </button>
          </div>

          <div class="sidebar-body" v-if="selectedStep">
            <!-- SE for Gatilho -->
            <div class="sidebar-section" v-if="isTriggerStep(selectedStep)">
              <template v-if="selectedStep.type === 'trigger' && selectedStep.config.triggerType === 'message'">
                <p class="sidebar-label">O usuário envia uma mensagem</p>
                <p class="sidebar-helper">Selecione uma forma de acionar a automação</p>

                <div class="keyword-box">
                  <p class="sidebar-label" style="margin-bottom:6px;">Se a mensagem contém</p>
                  <div class="keyword-chips">
                    <span
                      v-for="(kw, idx) in selectedStep.config.keywords || []"
                      :key="`kw-${idx}`"
                      class="keyword-chip"
                    >
                      {{ kw }}
                      <button class="chip-remove" @click="removeKeyword(idx)">&times;</button>
                    </span>
                  </div>
                  <div class="keyword-input-row">
                    <input
                      v-model="keywordInput"
                      class="keyword-input"
                      placeholder="+ Keyword"
                      @keyup.enter="addKeyword"
                    />
                    <button class="btn btn-primary btn-sm" style="padding: 8px 12px;" @click="addKeyword">
                      Adicionar
                    </button>
                  </div>
                  <p class="sidebar-tip">
                    As palavras-chave não diferenciam maiúsculas e minúsculas.
                  </p>
                </div>
              </template>

              <template v-else-if="selectedStep.type === 'trigger' && selectedStep.config.triggerType === 'telegram_ref_url'">
                <p class="sidebar-label">Link de Referência do Telegram</p>
                <p class="sidebar-helper">Crie um link único que inicia este fluxo quando clicado</p>

                  <!-- Info do Bot -->
                  <div v-if="botUsername && botUsername !== 'seu_bot'" class="bot-info-box">
                    <i class="fa-brands fa-telegram"></i>
                    <span>Bot: <strong>@{{ botUsername }}</strong></span>
                  </div>
                  
                  <!-- Aviso se fluxo não tem bot -->
                  <div v-else-if="!flow?.channel_id" class="bot-warning-box">
                    <i class="fa-solid fa-exclamation-triangle"></i>
                    <div>
                      <strong>Atenção:</strong> Este fluxo não tem um bot associado.
                      <br>
                      <small>Edite o fluxo e selecione um bot nas configurações gerais.</small>
                    </div>
                  </div>

                <div class="ref-box">
                  <label class="sidebar-label">Chave de Referência *</label>
                  <input
                    v-model="selectedStep.config.ref_key"
                    class="ref-input"
                    placeholder="Ex: welcome, promo2025, vip"
                    @input="autoSave"
                  />
                  <p class="sidebar-tip">
                    Esta chave será usada para identificar o link único
                  </p>

                  <div v-if="selectedStep.config.ref_key" style="margin-top: 20px;">
                    <label class="sidebar-label">
                      <i class="fa-solid fa-link" style="margin-right: 6px;"></i>
                      Seu Link de Referência Pronto para Usar
                    </label>
                    
                    <div class="ref-url-display-box" @click="copyTelegramRefLink(selectedStep.config.ref_key)">
                      <div class="ref-url-display-inner">
                        <i class="fa-brands fa-telegram ref-url-icon"></i>
                        <span class="ref-url-text">{{ getTelegramRefUrl(selectedStep.config.ref_key) }}</span>
                      </div>
                      <button class="ref-url-copy-btn" @click.stop="copyTelegramRefLink(selectedStep.config.ref_key)" title="Copiar link">
                        <i class="fa-solid fa-copy"></i>
                        Copiar
                      </button>
                    </div>
                    <p class="sidebar-tip success-tip">
                      <i class="fa-solid fa-circle-check"></i>
                      Link pronto! Compartilhe em redes sociais, anúncios ou emails. Quando alguém clicar, este fluxo será executado automaticamente.
                    </p>
                  </div>

                  <div v-else class="ref-warning">
                    <i class="fa-solid fa-exclamation-triangle"></i>
                    <span>Configure a chave de referência para gerar o link</span>
                  </div>

                  <label class="sidebar-label" style="margin-top: 20px;">
                    <i class="fa-solid fa-database" style="margin-right: 6px;"></i>
                    Salvar Parâmetro em Campo Personalizado (opcional)
                  </label>
                  <input
                    v-model="selectedStep.config.save_ref_field"
                    class="ref-input"
                    placeholder="Ex: utm_source, campanha, origem"
                    @blur="autoSave"
                  />
                  <p class="sidebar-tip">
                    O parâmetro completo será salvo neste campo do contato. Útil para rastreamento de campanhas.
                  </p>
                </div>
              </template>
            </div>

            <!-- SE for Bloco de Ações -->
            <div v-else-if="selectedStep.type === 'action'" class="sidebar-section">
              <div class="actions-editor">
                <div class="actions-header">
                  <label class="sidebar-label">Ações</label>
                  <button class="btn-add-action" @click="addAction">
                    <i class="fa-solid fa-plus"></i>
                    Adicionar Ação
                  </button>
                </div>

                <div v-if="!selectedStep.config.actions || selectedStep.config.actions.length === 0" class="actions-empty">
                  <p>Nenhuma ação configurada. Clique em "Adicionar Ação" para começar.</p>
                </div>

                <div v-else class="actions-list">
                  <div 
                    v-for="(action, index) in selectedStep.config.actions" 
                    :key="action.id || index"
                    class="action-item"
                  >
                    <div class="action-header">
                      <select 
                        v-model="action.type" 
                        class="action-type-select"
                        @change="onActionTypeChange(action, index)"
                      >
                        <option value="set_field">Definir Campo Personalizado</option>
                        <option value="add_tag">Adicionar Tag</option>
                        <option value="remove_tag">Remover Tag</option>
                        <option value="start_sequence">Iniciar Sequência</option>
                        <option value="stop_sequence">Parar Sequência</option>
                        <option value="go_to_flow">Ir para Fluxo</option>
                        <option value="go_to_step">Ir para Passo</option>
                        <option value="smart_delay">Atraso Inteligente</option>
                        <option value="webhook">Requisição Externa / Webhook</option>
                        <option value="notify_admin">Notificar Admin / Inbox</option>
                      </select>
                      <button class="btn-remove-action" @click="removeAction(index)">
                        <i class="fa-solid fa-trash"></i>
                      </button>
                    </div>

                    <!-- Set Custom Field -->
                    <div v-if="action.type === 'set_field'" class="action-config">
                      <div class="form-group">
                        <label class="sidebar-label">
                          Nome do Campo
                          <span 
                            class="info-icon" 
                            :class="{ 'tooltip-active': activeTooltip === 'set_field_name' }"
                            @click.stop="toggleTooltip('set_field_name', $event)"
                          >
                            <i class="fa-solid fa-circle-info"></i>
                            <span class="tooltip-text" v-show="activeTooltip === 'set_field_name'">
                              <strong>O que é:</strong> Nome do campo personalizado que você quer guardar.<br><br>
                              <strong>Exemplos:</strong><br>
                              • <code>nome_completo</code><br>
                              • <code>cidade</code><br>
                              • <code>interesse_produto</code><br>
                              • <code>orcamento</code><br>
                              • <code>telefone</code>
                            </span>
                          </span>
                        </label>
                        <PlaceholderInput
                          v-model="action.field_name"
                          placeholder="Ex: cidade, interesse_produto"
                          input-class="sidebar-textarea"
                          
                          @update:modelValue="autoSave"
                        />
                      </div>
                      <div class="form-group">
                        <label class="sidebar-label">
                          Valor
                          <span 
                            class="info-icon" 
                            :class="{ 'tooltip-active': activeTooltip === 'set_field_value' }"
                            @click.stop="toggleTooltip('set_field_value', $event)"
                          >
                            <i class="fa-solid fa-circle-info"></i>
                            <span class="tooltip-text" v-show="activeTooltip === 'set_field_value'">
                              <strong>O que é:</strong> O valor que vai ser guardado no campo.<br><br>
                              <strong>Pode ser:</strong><br>
                              • Texto fixo: <code>São Paulo</code><br>
                              • Variável: <code>{ultima_mensagem}</code><br>
                              • Misto: <code>Olá {primeiro_nome}</code><br><br>
                              <strong>Variáveis disponíveis:</strong><br>
                              • <code>{primeira_mensagem}</code><br>
                              • <code>{ultima_mensagem}</code><br>
                              • <code>{primeiro_nome}</code>
                            </span>
                          </span>
                        </label>
                        <PlaceholderInput
                          v-model="action.field_value"
                          placeholder="Ex: {ultima_mensagem} ou São Paulo"
                          input-class="sidebar-textarea"
                          
                          @update:modelValue="autoSave"
                        />
                      </div>
                    </div>

                    <!-- Add/Remove Tag -->
                    <div v-if="action.type === 'add_tag' || action.type === 'remove_tag'" class="action-config">
                      <div class="form-group">
                        <label class="sidebar-label">
                          Nome da Tag
                          <span 
                            class="info-icon" 
                            :class="{ 'tooltip-active': activeTooltip === 'tag_name' }"
                            @click.stop="toggleTooltip('tag_name', $event)"
                          >
                            <i class="fa-solid fa-circle-info"></i>
                            <span class="tooltip-text" v-show="activeTooltip === 'tag_name'">
                              <strong>O que é:</strong> Etiqueta para organizar e segmentar seus contatos.<br><br>
                              <strong>Exemplos práticos:</strong><br>
                              • <code>interessado_plano_premium</code><br>
                              • <code>lead_quente</code><br>
                              • <code>aguardando_pagamento</code><br>
                              • <code>cliente_vip</code><br>
                              • <code>precisa_suporte</code><br>
                              • <code>respondeu_pesquisa</code>
                            </span>
                          </span>
                        </label>
                        <PlaceholderInput
                          v-model="action.tag_name"
                          placeholder="Ex: lead_quente, cliente_vip"
                          input-class="sidebar-textarea"
                          
                          @update:modelValue="autoSave"
                        />
                      </div>
                    </div>

                    <!-- Start/Stop Sequence -->
                    <div v-if="action.type === 'start_sequence' || action.type === 'stop_sequence'" class="action-config">
                      <div class="form-group">
                        <label class="sidebar-label">
                          Nome da Sequência
                          <span 
                            class="info-icon" 
                            :class="{ 'tooltip-active': activeTooltip === 'sequence_name' }"
                            @click.stop="toggleTooltip('sequence_name', $event)"
                          >
                            <i class="fa-solid fa-circle-info"></i>
                            <span class="tooltip-text" v-show="activeTooltip === 'sequence_name'">
                              <strong>O que é:</strong> Nome da sequência de mensagens automáticas.<br><br>
                              <strong>Exemplos de uso:</strong><br>
                              • <code>followup_orcamento</code> - Dia 1: "Tem dúvidas?", Dia 3: "Oferta especial"<br>
                              • <code>onboarding_cliente</code> - Boas-vindas em 3 dias<br>
                              • <code>recuperacao_carrinho</code> - Lembrete de compra<br>
                              • <code>nutricao_lead</code> - Conteúdo educativo
                            </span>
                          </span>
                        </label>
                        <PlaceholderInput
                          v-model="action.sequence_name"
                          placeholder="Ex: followup_orcamento"
                          input-class="sidebar-textarea"
                          
                          @update:modelValue="autoSave"
                        />
                      </div>
                    </div>

                    <!-- Go to Flow -->
                    <div v-if="action.type === 'go_to_flow'" class="action-config">
                      <div class="form-group">
                        <label class="sidebar-label">
                          Selecionar Fluxo
                          <span 
                            class="info-icon" 
                            :class="{ 'tooltip-active': activeTooltip === 'go_to_flow' }"
                            @click.stop="toggleTooltip('go_to_flow', $event)"
                          >
                            <i class="fa-solid fa-circle-info"></i>
                            <span class="tooltip-text" v-show="activeTooltip === 'go_to_flow'">
                              <strong>O que é:</strong> Direciona o contato para outro fluxo completo.<br><br>
                              <strong>Quando usar:</strong><br>
                              • Enviar para fluxo de vendas<br>
                              • Direcionar para FAQ<br>
                              • Ir para atendimento humano<br>
                              • Voltar ao menu principal<br><br>
                              <strong>Exemplo:</strong> Se o cliente escolher "suporte", vai para o fluxo "Atendimento Técnico"
                            </span>
                          </span>
                        </label>
                        <select
                          class="sidebar-textarea"
                          v-model="action.flow_id"
                          @change="autoSave"
                        >
                          <option value="">Selecione um fluxo...</option>
                          <option v-for="f in availableFlows" :key="f.id" :value="f.id">
                            {{ f.name }}
                          </option>
                        </select>
                      </div>
                    </div>

                    <!-- Go to Step -->
                    <div v-if="action.type === 'go_to_step'" class="action-config">
                      <div class="form-group">
                        <label class="sidebar-label">
                          Selecionar Passo
                          <span 
                            class="info-icon" 
                            :class="{ 'tooltip-active': activeTooltip === 'go_to_step' }"
                            @click.stop="toggleTooltip('go_to_step', $event)"
                          >
                            <i class="fa-solid fa-circle-info"></i>
                            <span class="tooltip-text" v-show="activeTooltip === 'go_to_step'">
                              <strong>O que é:</strong> Pula para outro passo dentro do mesmo fluxo.<br><br>
                              <strong>Quando usar:</strong><br>
                              • Criar loops (ex: voltar ao menu)<br>
                              • Pular etapas desnecessárias<br>
                              • Criar atalhos internos<br><br>
                              <strong>Exemplo:</strong> Se já tem o nome do cliente, pula direto para "Pedir telefone" (passo 5)
                            </span>
                          </span>
                        </label>
                        <select
                          class="sidebar-textarea"
                          v-model="action.step_id"
                          @change="autoSave"
                        >
                          <option value="">Selecione um passo...</option>
                          <option v-for="s in availableSteps" :key="s.id" :value="s.id">
                            {{ s.name || `Passo #${s.order_index}` }}
                          </option>
                        </select>
                      </div>
                    </div>

                    <!-- Smart Delay -->
                    <div v-if="action.type === 'smart_delay'" class="action-config">
                      <div class="form-group">
                        <label class="sidebar-label">
                          Tempo de Espera
                          <span 
                            class="info-icon" 
                            :class="{ 'tooltip-active': activeTooltip === 'smart_delay' }"
                            @click.stop="toggleTooltip('smart_delay', $event)"
                          >
                            <i class="fa-solid fa-circle-info"></i>
                            <span class="tooltip-text" v-show="activeTooltip === 'smart_delay'">
                              <strong>O que é:</strong> Tempo de espera antes da próxima ação.<br><br>
                              <strong>Formatos aceitos:</strong><br>
                              • <code>5m</code> = 5 minutos<br>
                              • <code>2h</code> = 2 horas<br>
                              • <code>1d</code> = 1 dia<br>
                              • <code>30s</code> = 30 segundos<br><br>
                              <strong>Exemplo:</strong> Enviar mensagem, aguardar <code>1h</code>, depois enviar oferta
                            </span>
                          </span>
                        </label>
                        <div style="display: flex; gap: 8px;">
                          <input
                            type="number"
                            min="1"
                            class="sidebar-textarea"
                            style="flex: 1; min-width: 0;"
                            v-model.number="action.delay_value"
                            @input="autoSave"
                          />
                          <select
                            class="sidebar-textarea"
                            style="width: 120px; flex-shrink: 0;"
                            v-model="action.delay_unit"
                            @change="autoSave"
                          >
                            <option value="minutes">Minutos</option>
                            <option value="hours">Horas</option>
                            <option value="days">Dias</option>
                          </select>
                        </div>
                      </div>
                    </div>

                    <!-- Webhook -->
                    <div v-if="action.type === 'webhook'" class="action-config">
                      <div class="form-group">
                        <label class="sidebar-label">
                          URL do Webhook
                          <span 
                            class="info-icon" 
                            :class="{ 'tooltip-active': activeTooltip === 'webhook_url' }"
                            @click.stop="toggleTooltip('webhook_url', $event)"
                          >
                            <i class="fa-solid fa-circle-info"></i>
                            <span class="tooltip-text" v-show="activeTooltip === 'webhook_url'">
                              <strong>O que é:</strong> URL para enviar dados para sistemas externos.<br><br>
                              <strong>Exemplos de uso:</strong><br>
                              • Salvar lead no Google Sheets<br>
                              • Verificar pagamento no seu sistema<br>
                              • Validar cupom de desconto<br>
                              • Integrar com Make/Zapier<br><br>
                              <strong>Exemplo de URL:</strong><br>
                              <code>https://hooks.zapier.com/...</code>
                            </span>
                          </span>
                        </label>
                        <input
                          type="text"
                          class="sidebar-textarea"
                          v-model="action.webhook_url"
                          @input="autoSave"
                        />
                      </div>
                      <div class="form-group">
                        <label class="sidebar-label">Método HTTP</label>
                        <select
                          class="sidebar-textarea"
                          v-model="action.method"
                          @change="autoSave"
                        >
                          <option value="POST">POST</option>
                          <option value="GET">GET</option>
                          <option value="PUT">PUT</option>
                        </select>
                      </div>
                      <div class="form-group">
                        <label class="sidebar-label">
                          Headers (JSON opcional)
                          <span 
                            class="info-icon" 
                            :class="{ 'tooltip-active': activeTooltip === 'webhook_headers' }"
                            @click.stop="toggleTooltip('webhook_headers', $event)"
                          >
                            <i class="fa-solid fa-circle-info"></i>
                            <span class="tooltip-text" v-show="activeTooltip === 'webhook_headers'">
                              <strong>O que é:</strong> Cabeçalhos HTTP para autenticação (opcional).<br><br>
                              <strong>Quando usar:</strong> Se a API exigir token/chave<br><br>
                              <strong>Formato JSON:</strong><br>
                              <code>{</code><br>
                              <code>  "Authorization": "Bearer ABC123",</code><br>
                              <code>  "Content-Type": "application/json"</code><br>
                              <code>}</code><br><br>
                              <em>Deixe vazio se não precisar</em>
                            </span>
                          </span>
                        </label>
                        <textarea
                          class="sidebar-textarea"
                          rows="3"
                          v-model="action.headers"
                          @input="autoSave"
                        ></textarea>
                      </div>
                    </div>

                    <!-- Notify Admin -->
                    <div v-if="action.type === 'notify_admin'" class="action-config">
                      <div class="form-group">
                        <label class="sidebar-label">
                          Mensagem de Notificação
                          <span 
                            class="info-icon" 
                            :class="{ 'tooltip-active': activeTooltip === 'notify_message' }"
                            @click.stop="toggleTooltip('notify_message', $event)"
                          >
                            <i class="fa-solid fa-circle-info"></i>
                            <span class="tooltip-text" v-show="activeTooltip === 'notify_message'">
                              <strong>O que é:</strong> Mensagem que sua equipe vai receber.<br><br>
                              <strong>Exemplos:</strong><br>
                              • <code>Novo lead quente! Nome: {primeiro_nome}</code><br>
                              • <code>Cliente solicitou suporte urgente</code><br>
                              • <code>Orçamento acima de R$ 10.000</code><br>
                              • <code>Pagamento confirmado para {primeiro_nome}</code><br><br>
                              <em>Use variáveis como {primeiro_nome} para personalizar</em>
                            </span>
                          </span>
                        </label>
                        <PlaceholderInput
                          v-model="action.notification_message"
                          placeholder="Ex: Novo lead! Nome: {primeiro_nome}"
                          input-class="sidebar-textarea"
                          :multiline="true"
                          @update:modelValue="autoSave"
                        />
                      </div>
                      <div class="form-group">
                        <label class="sidebar-label">
                          Tag Adicional (opcional)
                          <span 
                            class="info-icon" 
                            :class="{ 'tooltip-active': activeTooltip === 'notify_tag' }"
                            @click.stop="toggleTooltip('notify_tag', $event)"
                          >
                            <i class="fa-solid fa-circle-info"></i>
                            <span class="tooltip-text" v-show="activeTooltip === 'notify_tag'">
                              <strong>O que é:</strong> Tag automática ao notificar a equipe.<br><br>
                              <strong>Exemplos:</strong><br>
                              • <code>aguardando_atendimento</code><br>
                              • <code>requer_atencao_urgente</code><br>
                              • <code>transferido_para_vendas</code><br>
                              • <code>suporte_nivel_2</code><br><br>
                              <em>Ajuda a organizar quem precisa de atenção</em>
                            </span>
                          </span>
                        </label>
                        <PlaceholderInput
                          v-model="action.notify_tag"
                          placeholder="Ex: aguardando_atendimento"
                          input-class="sidebar-textarea"
                          
                          @update:modelValue="autoSave"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- SE for Bloco de Condição -->
            <div v-else-if="selectedStep.type === 'condition'" class="sidebar-section">
              <p class="sidebar-label">Condição (IF/ELSE)</p>
              <p class="sidebar-helper">Direcione o fluxo baseado em campos, tags ou variáveis</p>

              <div class="form-group">
                <label class="sidebar-label">Tipo de Condição</label>
                <select 
                  v-model="selectedStep.config.conditionType" 
                  class="sidebar-textarea"
                  @change="autoSave"
                >
                  <option value="field">Campo Personalizado</option>
                  <option value="tag">Tag do Contato</option>
                  <option value="variable">Variável do Sistema</option>
                </select>
              </div>

              <!-- Se for Campo Personalizado -->
              <div v-if="selectedStep.config.conditionType === 'field'" class="form-group">
                <label class="sidebar-label">Nome do Campo</label>
                <input
                  v-model="selectedStep.config.field"
                  class="sidebar-textarea"
                  placeholder="Ex: cidade, interesse"
                  @input="autoSave"
                />
              </div>

              <!-- Se for Tag -->
              <div v-if="selectedStep.config.conditionType === 'tag'" class="form-group">
                <label class="sidebar-label">Nome da Tag</label>
                <input
                  v-model="selectedStep.config.field"
                  class="sidebar-textarea"
                  placeholder="Ex: cliente_vip"
                  @input="autoSave"
                />
              </div>

              <!-- Se for Variável -->
              <div v-if="selectedStep.config.conditionType === 'variable'" class="form-group">
                <label class="sidebar-label">Variável</label>
                <select 
                  v-model="selectedStep.config.field" 
                  class="sidebar-textarea"
                  @change="autoSave"
                >
                  <option value="first_name">Primeiro Nome</option>
                  <option value="last_name">Sobrenome</option>
                  <option value="username">Username</option>
                  <option value="first_message">Primeira Mensagem</option>
                  <option value="last_message">Última Mensagem</option>
                </select>
              </div>

              <!-- Operador -->
              <div class="form-group">
                <label class="sidebar-label">Operador</label>
                <select 
                  v-model="selectedStep.config.operator" 
                  class="sidebar-textarea"
                  @change="autoSave"
                >
                  <option value="equals">É igual a</option>
                  <option value="not_equals">É diferente de</option>
                  <option value="contains">Contém</option>
                  <option value="not_contains">Não contém</option>
                  <option value="exists">Existe</option>
                  <option value="not_exists">Não existe</option>
                  <option value="greater_than">Maior que</option>
                  <option value="less_than">Menor que</option>
                </select>
              </div>

              <!-- Valor (não mostrar para exists/not_exists) -->
              <div v-if="!['exists', 'not_exists'].includes(selectedStep.config.operator)" class="form-group">
                <label class="sidebar-label">Valor de Comparação</label>
                <input
                  v-model="selectedStep.config.value"
                  class="sidebar-textarea"
                  placeholder="Ex: São Paulo"
                  @input="autoSave"
                />
              </div>

              <!-- Info sobre saídas -->
              <div class="condition-info">
                <i class="fa-solid fa-info-circle"></i>
                <div>
                  <strong>Como funciona:</strong>
                  <p>Este bloco terá 2 saídas: <span style="color: #22c55e;">✓ Verdadeiro</span> e <span style="color: #ef4444;">✗ Falso</span></p>
                  <p>Conecte cada saída ao próximo passo desejado.</p>
                </div>
              </div>
            </div>

            <!-- SE for Bloco Randomizador -->
            <div v-else-if="selectedStep.type === 'randomizer'" class="sidebar-section">
              <p class="sidebar-label">Randomizador (A/B Testing)</p>
              <p class="sidebar-helper">Distribua usuários aleatoriamente em diferentes caminhos</p>

              <div class="randomizer-paths">
                <div 
                  v-for="(path, index) in selectedStep.config.paths" 
                  :key="path.id"
                  class="randomizer-path-item"
                >
                  <div class="path-header">
                    <input
                      v-model="path.name"
                      class="path-name-input"
                      placeholder="Nome do caminho"
                      @input="autoSave"
                    />
                    <button 
                      v-if="selectedStep.config.paths.length > 2"
                      class="btn-remove-path"
                      @click="removeRandomPath(index)"
                    >
                      <i class="fa-solid fa-trash"></i>
                    </button>
                  </div>
                  <div class="path-percentage">
                    <input
                      type="number"
                      min="0"
                      max="100"
                      v-model.number="path.percentage"
                      class="percentage-input"
                      @input="updateRandomPercentages(index)"
                    />
                    <span class="percentage-label">%</span>
                  </div>
                </div>
              </div>

              <button class="btn-add-path" @click="addRandomPath">
                <i class="fa-solid fa-plus"></i>
                Adicionar Caminho
              </button>

              <!-- Total -->
              <div class="randomizer-total" :class="{ error: getTotalPercentage() !== 100 }">
                <span>Total:</span>
                <strong>{{ getTotalPercentage() }}%</strong>
                <span v-if="getTotalPercentage() !== 100" class="error-msg">
                  <i class="fa-solid fa-exclamation-triangle"></i>
                  Deve somar 100%
                </span>
              </div>

              <!-- Info -->
              <div class="randomizer-info">
                <i class="fa-solid fa-info-circle"></i>
                <div>
                  <strong>Como funciona:</strong>
                  <p>Cada usuário que passar por aqui será direcionado aleatoriamente para um dos caminhos, respeitando as porcentagens definidas.</p>
                  <p><strong>Exemplo:</strong> 50% vão para o Caminho A, 50% para o Caminho B.</p>
                </div>
              </div>
            </div>

            <!-- SE for Bloco de Atraso Inteligente -->
            <div v-else-if="selectedStep.type === 'wait'" class="sidebar-section">
              <p class="sidebar-label">Atraso Inteligente</p>
              <p class="sidebar-helper">Adicione um tempo de espera antes do próximo passo</p>

              <div class="form-group">
                <label class="sidebar-label">Tipo de Atraso</label>
                <select 
                  v-model="selectedStep.config.delayType" 
                  class="sidebar-textarea"
                  @change="autoSave"
                >
                  <option value="fixed">Fixo</option>
                  <option value="random">Aleatório (intervalo)</option>
                  <option value="smart">Inteligente (horário comercial)</option>
                </select>
              </div>

              <!-- Atraso Fixo -->
              <div v-if="selectedStep.config.delayType === 'fixed'">
                <div class="form-group">
                  <label class="sidebar-label">Tempo de Espera</label>
                  <div style="display: flex; gap: 8px;">
                    <input
                      type="number"
                      min="1"
                      v-model.number="selectedStep.config.value"
                      class="sidebar-textarea"
                      style="flex: 1;"
                      @input="autoSave"
                    />
                    <select
                      v-model="selectedStep.config.unit"
                      class="sidebar-textarea"
                      style="width: 120px;"
                      @change="autoSave"
                    >
                      <option value="seconds">Segundos</option>
                      <option value="minutes">Minutos</option>
                      <option value="hours">Horas</option>
                      <option value="days">Dias</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- Atraso Aleatório -->
              <div v-if="selectedStep.config.delayType === 'random'">
                <div class="form-group">
                  <label class="sidebar-label">Intervalo Mínimo</label>
                  <div style="display: flex; gap: 8px;">
                    <input
                      type="number"
                      min="1"
                      v-model.number="selectedStep.config.randomMin"
                      class="sidebar-textarea"
                      style="flex: 1;"
                      @input="autoSave"
                    />
                    <select
                      v-model="selectedStep.config.unit"
                      class="sidebar-textarea"
                      style="width: 120px;"
                      @change="autoSave"
                    >
                      <option value="seconds">Segundos</option>
                      <option value="minutes">Minutos</option>
                      <option value="hours">Horas</option>
                      <option value="days">Dias</option>
                    </select>
                  </div>
                </div>
                <div class="form-group">
                  <label class="sidebar-label">Intervalo Máximo</label>
                  <input
                    type="number"
                    min="1"
                    v-model.number="selectedStep.config.randomMax"
                    class="sidebar-textarea"
                    @input="autoSave"
                  />
                </div>
              </div>

              <!-- Atraso Inteligente -->
              <div v-if="selectedStep.config.delayType === 'smart'">
                <div class="smart-delay-info">
                  <i class="fa-solid fa-clock"></i>
                  <div>
                    <strong>Atraso Inteligente:</strong>
                    <p>Aguarda até o próximo horário comercial (9h às 18h, segunda a sexta).</p>
                    <p>Se a mensagem chegar fora do horário, ela é agendada para o próximo dia útil às 9h.</p>
                  </div>
                </div>
              </div>

              <!-- Preview do tempo -->
              <div class="delay-preview">
                <i class="fa-solid fa-hourglass-half"></i>
                <span>{{ getDelayPreview() }}</span>
              </div>
            </div>

            <!-- SE for Bloco de Comentário -->
            <div v-else-if="selectedStep.type === 'comment'" class="sidebar-section">
              <p class="sidebar-label">Comentário / Anotação</p>
              <p class="sidebar-helper">Adicione notas que aparecem apenas no editor (não são enviadas)</p>

              <div class="form-group">
                <label class="sidebar-label">Texto do Comentário</label>
                <textarea
                  v-model="selectedStep.config.text"
                  class="sidebar-textarea"
                  rows="5"
                  placeholder="Adicione suas anotações, lembretes ou documentação aqui..."
                  @input="autoSave"
                ></textarea>
              </div>

              <div class="form-group">
                <label class="sidebar-label">Cor do Comentário</label>
                <div class="comment-color-picker">
                  <button 
                    v-for="color in commentColors" 
                    :key="color"
                    class="color-option"
                    :style="{ background: color }"
                    :class="{ active: selectedStep.config.color === color }"
                    @click="selectedStep.config.color = color; autoSave()"
                  ></button>
                </div>
              </div>

              <div class="comment-info">
                <i class="fa-solid fa-info-circle"></i>
                <div>
                  <strong>Nota:</strong>
                  <p>Comentários são apenas visuais e não afetam o fluxo. Use para documentar sua lógica ou deixar lembretes para a equipe.</p>
                </div>
              </div>
            </div>

            <!-- SE for Iniciar Automação -->
            <div v-else-if="selectedStep.type === 'start_automation'" class="sidebar-section">
              <p class="sidebar-label">Iniciar Outra Automação</p>
              <p class="sidebar-helper">Redirecione o contato para executar outro fluxo</p>

              <div class="form-group">
                <label class="sidebar-label">Selecionar Fluxo</label>
                <select
                  v-model="selectedStep.config.flowId"
                  class="sidebar-textarea"
                  @change="onFlowSelected"
                >
                  <option value="">Escolha um fluxo...</option>
                  <option 
                    v-for="f in availableFlows" 
                    :key="f.id" 
                    :value="f.id"
                    :disabled="f.id === flowId"
                  >
                    {{ f.name }} {{ f.id === flowId ? '(fluxo atual)' : '' }}
                  </option>
                </select>
              </div>

              <div v-if="selectedStep.config.flowId" class="flow-preview">
                <i class="fa-solid fa-arrow-right"></i>
                <span>Vai para: <strong>{{ selectedStep.config.flowName }}</strong></span>
              </div>

              <div class="start-automation-info">
                <i class="fa-solid fa-info-circle"></i>
                <div>
                  <strong>Como funciona:</strong>
                  <p>Quando o contato chegar aqui, ele será direcionado para o fluxo selecionado. O fluxo atual é encerrado.</p>
                  <p><strong>Casos de uso:</strong></p>
                  <ul>
                    <li>Enviar para menu principal</li>
                    <li>Direcionar para atendimento</li>
                    <li>Iniciar sequência de vendas</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- SENÃO, Edição de Mensagem normal -->
            <template v-else>
              <!-- Propriedades do bloco selecionado dentro da mensagem -->
              <template v-if="selectedBlock && selectedBlock.stepId === selectedStep.id">
                <div v-if="currentBlock && currentBlock.type === 'text'" class="sidebar-section">
                  <label class="sidebar-label">Texto</label>
                  <div class="tag-dropdown tag-dropdown-inline">
                    <button type="button" class="tag-dropdown-toggle" @click="toggleTagDropdown('text')">
                      Campos personalizados
                      <span class="tag-dropdown-arrow" :class="{ open: textTagDropdownOpen }">▾</span>
                    </button>
                    <div v-show="textTagDropdownOpen" class="tag-dropdown-panel">
                      <div class="tag-list">
                        <button
                          v-for="tag in personalizationTags"
                          :key="tag.value"
                          type="button"
                          class="tag-chip"
                          @click="insertTag(tag.value)"
                        >
                          {{ tag.label }}
                        </button>
                      </div>
                    </div>
                  </div>
                  <textarea
                    v-model="currentBlock.text"
                    class="sidebar-textarea"
                    placeholder="Digite o texto..."
                    rows="3"
                    @input="autoSave"
                    ref="contentTextareaRef"
                  ></textarea>
                </div>

                <div v-else-if="currentBlock && currentBlock.type === 'delay'" class="sidebar-section">
                  <label class="sidebar-label">Atraso (segundos)</label>
                  <input
                    type="number"
                    min="1"
                    class="sidebar-textarea"
                    v-model.number="currentBlock.seconds"
                    @input="autoSave"
                  />
                </div>

                <div v-else-if="currentBlock && currentBlock.type === 'button'" class="sidebar-section">
                  <label class="sidebar-label">Mensagem (opcional)</label>
                  <div class="sidebar-hint">
                    Essa mensagem aparece acima dos botões. Se deixar vazio, o sistema envia apenas os botões (o Telegram exige um texto e nós enviamos um texto invisível automaticamente).
                  </div>
                  <div class="tag-dropdown tag-dropdown-inline">
                    <button type="button" class="tag-dropdown-toggle" @click="toggleTagDropdown('button')">
                      Campos personalizados
                      <span class="tag-dropdown-arrow" :class="{ open: buttonTagDropdownOpen }">▾</span>
                    </button>
                    <div v-show="buttonTagDropdownOpen" class="tag-dropdown-panel">
                      <div class="tag-list">
                        <button
                          v-for="tag in personalizationTags"
                          :key="`btn-${tag.value}`"
                          type="button"
                          class="tag-chip"
                          @click="insertTag(tag.value)"
                        >
                          {{ tag.label }}
                        </button>
                      </div>
                    </div>
                  </div>
                  <textarea
                    v-model="currentBlock.text"
                    class="sidebar-textarea"
                    placeholder="Mensagem acima dos botões (opcional). Deixe vazio para enviar apenas os botões..."
                    rows="2"
                    @input="autoSave"
                    ref="contentTextareaRef"
                  ></textarea>
                  
                  <div style="margin-top: 16px;">
                    <label class="sidebar-label">Botões</label>
                    <div class="sidebar-hint">O texto abaixo é o texto do botão (o que a pessoa clica no Telegram).</div>
                    
                    <!-- Lista de Botões -->
                    <div v-if="currentBlock.buttons && currentBlock.buttons.length > 0" class="button-list">
                      <div 
                        v-for="(btn, index) in currentBlock.buttons" 
                        :key="index" 
                        class="button-item"
                      >
                        <!-- Texto do botão -->
                        <div class="button-item-inputs">
                          <input
                            type="text"
                            class="button-input"
                            placeholder="Texto do botão (no Telegram)"
                            v-model="btn.text"
                            @input="autoSave"
                          />
                          
                          <!-- Toggle URL / Bloco -->
                          <div class="btn-action-toggle">
                            <button
                              type="button"
                              class="btn-toggle-opt"
                              :class="{ active: !btn.action || btn.action === 'url' }"
                              @click="onBtnActionToUrl(btn, index); btn.action = 'url'; autoSave()"
                            >
                              <i class="fa-solid fa-link"></i> URL
                            </button>
                            <button
                              type="button"
                              class="btn-toggle-opt"
                              :class="{ active: btn.action === 'flow' }"
                              @click="btn.action = 'flow'; autoSave()"
                            >
                              <i class="fa-solid fa-arrow-right"></i> Bloco
                            </button>
                          </div>

                          <!-- Campo URL -->
                          <input
                            v-if="!btn.action || btn.action === 'url'"
                            type="text"
                            class="button-input"
                            placeholder="https://..."
                            v-model="btn.url"
                            @input="autoSave"
                          />

                          <!-- Conexão de Bloco via LINHA (sem seletor para evitar confusão) -->
                          <div v-else class="btn-flow-hint">
                            <div v-if="btn.targetStepId" class="btn-flow-connected">
                              Conectado: {{ getStepLabelById(btn.targetStepId) }}
                            </div>
                            <div v-else class="btn-flow-disconnected">
                              Conecte este botão a um bloco usando a linha.
                            </div>
                          </div>
                        </div>

                        <button 
                          class="btn-remove-button" 
                          @click="removeButton(index)"
                          type="button"
                        >
                          <i class="fa-solid fa-trash"></i>
                        </button>
                      </div>
                    </div>
                    
                    <!-- Botão Adicionar -->
                    <button class="btn-add-button" @click="addButton" type="button">
                      <i class="fa-solid fa-plus"></i>
                      Adicionar Botão
                    </button>
                  </div>
                </div>

                <div v-else-if="currentBlock && currentBlock.type === 'image'" class="sidebar-section">
                  <label class="sidebar-label">Imagem</label>
                  
                  <!-- Componente de Upload de Imagem -->
                  <ImageUpload 
                    v-model="currentBlock.url" 
                    @update:modelValue="autoSave"
                    label="Fazer Upload"
                  />
                  
                  <!-- OU usar URL manual -->
                  <div style="margin-top: 16px;">
                    <label class="sidebar-label">Ou cole a URL da imagem</label>
                    <input
                      type="text"
                      class="sidebar-textarea"
                      v-model="currentBlock.url"
                      @input="autoSave"
                      placeholder="https://exemplo.com/imagem.jpg"
                    />
                  </div>
                  
                  <!-- Legenda -->
                  <div style="margin-top: 16px;">
                    <label class="sidebar-label">Legenda (opcional)</label>
                    <input
                      type="text"
                      class="sidebar-textarea"
                      v-model="currentBlock.caption"
                      @input="autoSave"
                      placeholder="Texto que acompanha a imagem"
                    />
                  </div>
                </div>

                <div v-else-if="currentBlock && currentBlock.type === 'audio'" class="sidebar-section">
                  <label class="sidebar-label">Áudio</label>
                  
                  <!-- Componente de Upload de Áudio -->
                  <AudioUpload 
                    v-model="currentBlock.url" 
                    v-model:title="currentBlock.title"
                    @update:modelValue="autoSave"
                    @update:title="autoSave"
                    label="Fazer Upload"
                  />
                  
                  <!-- OU usar URL manual -->
                  <div style="margin-top: 16px;">
                    <label class="sidebar-label">Ou cole a URL do áudio</label>
                    <input
                      type="text"
                      class="sidebar-textarea"
                      v-model="currentBlock.url"
                      @input="autoSave"
                      placeholder="https://exemplo.com/audio.mp3"
                    />
                  </div>
                  
                  <!-- Título -->
                  <div style="margin-top: 16px;">
                    <label class="sidebar-label">Título (opcional)</label>
                    <input
                      type="text"
                      class="sidebar-textarea"
                      v-model="currentBlock.title"
                      @input="autoSave"
                      placeholder="Ex: Mensagem de boas-vindas"
                    />
                  </div>
                </div>

                <div v-else-if="currentBlock && currentBlock.type === 'video'" class="sidebar-section">
                  <label class="sidebar-label">Vídeo</label>
                  
                  <!-- Toggle: Vídeo Normal ou Bolinha -->
                  <div class="video-type-toggle" style="margin-bottom: 16px;">
                    <label class="toggle-option" :class="{ active: !currentBlock.is_video_note }">
                      <input 
                        type="radio" 
                        :checked="!currentBlock.is_video_note"
                        @change="currentBlock.is_video_note = false; autoSave()"
                      />
                      <i class="fa-solid fa-video"></i>
                      <span>Vídeo Normal</span>
                    </label>
                    <label class="toggle-option" :class="{ active: currentBlock.is_video_note }">
                      <input 
                        type="radio" 
                        :checked="currentBlock.is_video_note"
                        @change="currentBlock.is_video_note = true; autoSave()"
                      />
                      <i class="fa-solid fa-circle"></i>
                      <span>Vídeo Bolinha</span>
                    </label>
                  </div>
                  
                  <!-- Info sobre vídeo bolinha -->
                  <div v-if="currentBlock.is_video_note" class="video-note-info">
                    <i class="fa-solid fa-info-circle"></i>
                    <div>
                      <strong>Vídeo Bolinha:</strong>
                      <ul>
                        <li>Deve ser quadrado (1:1)</li>
                        <li>Máximo 640px</li>
                        <li>Duração ≤ 1 minuto</li>
                      </ul>
                    </div>
                  </div>
                  
                  <!-- Componente de Upload de Vídeo -->
                  <VideoUpload 
                    v-model="currentBlock.url" 
                    v-model:title="currentBlock.title"
                    @update:modelValue="autoSave"
                    @update:title="autoSave"
                    label="Fazer Upload"
                  />
                  
                  <!-- OU usar URL manual -->
                  <div style="margin-top: 16px;">
                    <label class="sidebar-label">Ou cole a URL do vídeo</label>
                    <input
                      type="text"
                      class="sidebar-textarea"
                      v-model="currentBlock.url"
                      @input="autoSave"
                      placeholder="https://exemplo.com/video.mp4"
                    />
                  </div>
                  
                  <!-- Título (apenas para vídeo normal) -->
                  <div v-if="!currentBlock.is_video_note" style="margin-top: 16px;">
                    <label class="sidebar-label">Título (opcional)</label>
                    <input
                      type="text"
                      class="sidebar-textarea"
                      v-model="currentBlock.title"
                      @input="autoSave"
                      placeholder="Ex: Tutorial passo a passo"
                    />
                  </div>
                </div>

                <div v-else-if="currentBlock && currentBlock.type === 'data'" class="sidebar-section">
                  <label class="sidebar-label">Campo</label>
                  <input
                    type="text"
                    class="sidebar-textarea"
                    v-model="currentBlock.field"
                    @input="autoSave"
                  />
                  <label class="sidebar-label" style="margin-top:10px;">Prompt</label>
                  <input
                    type="text"
                    class="sidebar-textarea"
                    v-model="currentBlock.prompt"
                    @input="autoSave"
                  />
                </div>
              </template>

              <!-- Botões para adicionar blocos -->
              <div class="sidebar-section">
                <label class="sidebar-label">Adicione um dos blocos de conteúdo:</label>
                
                <button class="content-block-btn" @click="addContentBlock('text')">
                  <div class="content-block-icon">
                    <i class="fa-solid fa-align-left"></i>
                  </div>
                  <div class="content-block-info">
                    <h4>Texto</h4>
                    <p>Adicione texto simples e botões</p>
                  </div>
                </button>

                <!-- Mídias - Agora com botões separados e mais visuais -->
                <div class="media-blocks-group">
                  <div class="media-group-label">
                    <i class="fa-solid fa-photo-film"></i>
                    <span>Mídias</span>
                  </div>
                  <div class="media-blocks-grid">
                    <button class="media-block-btn media-block-image" @click="addContentBlock('image')">
                      <div class="media-block-icon-wrapper">
                        <i class="fa-solid fa-image"></i>
                      </div>
                      <div class="media-block-label">Imagem</div>
                    </button>
                    <button class="media-block-btn media-block-audio" @click="addContentBlock('audio')">
                      <div class="media-block-icon-wrapper">
                        <i class="fa-solid fa-music"></i>
                      </div>
                      <div class="media-block-label">Áudio</div>
                    </button>
                    <button class="media-block-btn media-block-video" @click="addContentBlock('video')">
                      <div class="media-block-icon-wrapper">
                        <i class="fa-solid fa-video"></i>
                      </div>
                      <div class="media-block-label">Vídeo</div>
                    </button>
                  </div>
                </div>

                <button class="content-block-btn" @click="addContentBlock('delay')">
                  <div class="content-block-icon">
                    <i class="fa-solid fa-clock"></i>
                  </div>
                  <div class="content-block-info">
                    <h4>Atraso</h4>
                    <p>Deixe um intervalo entre as mensagens</p>
                  </div>
                </button>

                <button class="content-block-btn" @click="addContentBlock('data')">
                  <div class="content-block-icon">
                    <i class="fa-solid fa-database"></i>
                  </div>
                  <div class="content-block-info">
                    <h4>Coleta de Dados</h4>
                    <p>Capture e-mails, telefones e mais</p>
                    <span class="pro-badge">PRO</span>
                  </div>
                </button>

                <button class="content-block-btn" @click="addContentBlock('button')">
                  <div class="content-block-icon">
                    <i class="fa-solid fa-ellipsis"></i>
                  </div>
                  <div class="content-block-info">
                    <h4>Botão/Menu</h4>
                    <p>Adicione um botão do menu do Telegram</p>
                  </div>
                </button>
              </div>

              <div class="sidebar-section">
                <button class="sidebar-next-step-btn">
                  <i class="fa-solid fa-arrow-right"></i>
                  Escolher Próximo Passo
                </button>
              </div>
            </template>
          </div>

          <!-- Toolbar fixo (não sobe com scroll) -->
          <div class="sidebar-footer-toolbar">
            <div class="text-toolbar" :class="{ disabled: !canEditActiveText }">
              <button class="text-toolbar-btn" type="button" title="Negrito" :disabled="!canEditActiveText" @mousedown.prevent @click="wrapActiveSelection('*', '*')">
                <i class="fa-solid fa-bold"></i>
              </button>
              <button class="text-toolbar-btn" type="button" title="Itálico" :disabled="!canEditActiveText" @mousedown.prevent @click="wrapActiveSelection('_', '_')">
                <i class="fa-solid fa-italic"></i>
              </button>
              <button class="text-toolbar-btn" type="button" title="Sublinhado" :disabled="!canEditActiveText" @mousedown.prevent @click="wrapActiveSelection('__', '__')">
                <i class="fa-solid fa-underline"></i>
              </button>
              <button class="text-toolbar-btn" type="button" title="Riscado" :disabled="!canEditActiveText" @mousedown.prevent @click="wrapActiveSelection('~', '~')">
                <i class="fa-solid fa-strikethrough"></i>
              </button>
              <div class="text-toolbar-sep"></div>
              <button class="text-toolbar-btn" type="button" title="Pacote de Emojis" :disabled="!canEditActiveText" @mousedown.prevent @click="toggleEmojiPicker">
                <i class="fa-regular fa-face-smile"></i>
              </button>
              <button class="text-toolbar-btn" type="button" title="Criador de Links" :disabled="!canEditActiveText" @mousedown.prevent @click="createLinkOnActiveSelection">
                <i class="fa-solid fa-link"></i>
              </button>

              <div v-if="emojiPickerOpen" class="emoji-popover">
                <button
                  v-for="e in emojiList"
                  :key="e"
                  type="button"
                  class="emoji-btn"
                  @mousedown.prevent
                  @click="insertIntoActiveText(e); emojiPickerOpen = false"
                >
                  {{ e }}
                </button>
              </div>
            </div>
          </div>
        </aside>

        <!-- Canvas de Fluxo -->
        <div 
          class="flow-canvas-container"
          :class="{ 'with-sidebar': selectedStep }"
          ref="containerRef"
          @wheel.prevent="handleWheel"
          @mousedown.self="startPan"
          @mousemove="handlePanMove"
          @mouseup="endPan"
          @mouseleave="endPan"
        >
        <div 
          class="flow-canvas-workspace"
          ref="workspaceRef"
          :style="{
            transform: `translate(${canvasOffset.x}px, ${canvasOffset.y}px) scale(${canvasScale})`,
            transformOrigin: '0 0'
          }"
        >
          <!-- SVG para conexões -->
          <svg class="flow-connections-svg">
            <!-- Definições de marcadores -->
            <defs>
              <!-- Seta no final (linha termina atrás da seta) -->
              <marker
                id="arrow-end"
                viewBox="0 0 10 10"
                markerWidth="6"
                markerHeight="6"
                refX="5"
                refY="5"
                orient="auto"
                markerUnits="strokeWidth"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#22c55e" />
              </marker>
            </defs>
            
            <!-- Linha temporária durante drag -->
            <path
              v-if="isDraggingConnection"
              :d="tempConnectionPath"
              class="connection-line connection-line-temp"
            />
            
            <!-- Conexões permanentes -->
            <path
              v-for="conn in connectionPaths"
              :key="conn.id"
              :d="conn.path"
              class="connection-line connection-line-animated"
              marker-end="url(#arrow-end)"
              @click="removeConnection(conn.id)"
            />
          </svg>

          <!-- Empty state -->
          <div v-if="steps.length === 0" class="flow-empty-state">
            <div class="empty-state-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            </div>
            <h3>Canvas Vazio</h3>
            <p>Adicione um gatilho para iniciar o fluxo</p>
            <button class="btn btn-primary" @click="showTriggerModal = true">
              <i class="fa-solid fa-bolt"></i>
              Adicionar Gatilho
            </button>
          </div>

          <!-- Flow Nodes -->
          <div
            v-for="step in steps"
            :key="step.id"
            class="flow-node"
            :class="{ 
              'is-dragging': draggingNodeId === step.id,
              'is-selected': selectedStep && selectedStep.id === step.id,
              [`node-type-${step.type}`]: true
            }"
            :style="getNodeStyle(step.id)"
            :ref="(el) => registerNodeEl(el, step.id)"
            @mousedown="startNodeDrag($event, step.id)"
            @click="selectStep(step)"
          >
            <!-- Ponto de Entrada (canto superior esquerdo) - Apenas para blocos que não são gatilhos -->
          <div 
              v-if="step.type !== 'trigger'"
              class="flow-port flow-port-input"
              :class="{ 'show-on-drag': isDraggingConnection || hoveredPort === `${step.id}-in` }"
              @mouseup="completeConnection(step.id)"
              @mouseenter="hoveredPort = `${step.id}-in`"
              @mouseleave="hoveredPort = null"
              :ref="(el) => registerPort(el, step.id, 'in')"
            >
              <div class="flow-port-dot"></div>
            </div>

            <!-- Conteúdo do Node -->
            <div class="flow-node-content">
              <div class="flow-node-header-simple">
                <span class="flow-node-icon">
                  <i :class="getStepIcon(step.type)"></i>
                </span>
                <div style="flex:1; min-width:0;" v-if="step.type !== 'message'">
                  <div class="flow-node-title">{{ renderStepTitle(step) }}</div>
                  <div class="flow-node-subtitle" v-html="renderStepSubtitle(step)"></div>
                </div>
                <div style="flex:1; min-width:0;" v-else>
                  <div class="flow-node-title">Mensagem</div>
                </div>
                <button class="btn-node-delete" @click.stop="deleteStep(step.id)">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>

              <div v-if="step.type === 'message'" class="flow-node-body-subblocks">
                <div
                  v-for="(block, blockIndex) in step.config.blocks"
                  :key="block.id"
                  class="msg-block"
                  :class="[
                    `msg-block-${block.type}`,
                    { 
                      'is-dragging-block': draggingBlock && draggingBlock.id === block.id,
                      'drag-over': dragOverIndex === blockIndex
                    }
                  ]"
                  :data-block-index="blockIndex"
                  @click.stop="selectBlock(step, block)"
                  @mousedown="startBlockDrag($event, step, block, blockIndex)"
                  :data-selected="selectedBlock && selectedBlock.blockId === block.id"
                >
                  <div class="msg-block-drag-handle">
                    <i class="fa-solid fa-grip-vertical"></i>
                  </div>
                  <button class="msg-block-remove" @click.stop="removeBlock(block.id)" @mousedown.stop>
                    <i class="fa-solid fa-xmark"></i>
                  </button>
                  <template v-if="block.type === 'text'">
                    <div class="msg-block-text">{{ block.text || 'Adicionar texto' }}</div>
                  </template>
                  <template v-else-if="block.type === 'delay'">
                    <div class="msg-block-delay">
                      <i class="fa-regular fa-clock"></i>
                      Digitando por {{ block.seconds || 3 }} segundos...
                    </div>
                  </template>
                  <template v-else-if="block.type === 'button'">
                    <div class="msg-block-text" style="margin-bottom: 6px;">{{ block.text || 'Mensagem com botões' }}</div>
                    <div v-if="block.buttons && block.buttons.length > 0" style="display: flex; flex-direction: column; gap: 4px;">
                      <div 
                        v-for="(btn, idx) in block.buttons" 
                        :key="idx"
                        class="msg-block-menu-btn"
                        :class="{ 'msg-block-menu-btn-flow': btn.action === 'flow' }"
                        :style="{ fontSize: '0.75rem', position: 'relative', paddingRight: btn.action === 'flow' ? '30px' : undefined }"
                      >
                        <i 
                          :class="btn.action === 'flow' ? 'fa-solid fa-arrow-right' : 'fa-solid fa-link'" 
                          style="font-size: 0.7rem; opacity: 0.7; flex-shrink: 0;"
                        ></i>
                        <span style="flex: 1; text-align: center;">{{ btn.text || 'Botão' }}</span>

                        <!-- Port de saída colado ao botao -->
                        <div
                          v-if="btn.action === 'flow'"
                          class="flow-port flow-port-btn-inline"
                          :ref="(el) => registerPort(el, step.id, `out-btn-${block.id}-${idx}`)"
                          @mousedown.stop="startConnection($event, step.id, `btn-${block.id}-${idx}`)"
                          :title="btn.text || 'Botão'"
                        >
                          <div class="flow-port-dot"></div>
                        </div>
                      </div>
                    </div>
                    <div v-else class="msg-block-menu-btn" style="opacity: 0.5;">
                      <i class="fa-solid fa-plus"></i>
                      Adicionar botões
                    </div>
                  </template>
                  <template v-else-if="block.type === 'image'">
                    <div class="msg-block-image">
                      <div class="media-preview">
                        <i class="fa-solid fa-image"></i>
                        <span>{{ block.url ? 'Imagem' : 'Adicionar imagem' }}</span>
                      </div>
                      <div v-if="block.caption" class="media-caption">{{ block.caption }}</div>
                    </div>
                  </template>
                  <template v-else-if="block.type === 'audio'">
                    <div class="msg-block-media msg-block-audio">
                      <div class="media-icon-wrapper">
                        <i class="fa-solid fa-music"></i>
                      </div>
                      <div class="media-info">
                        <div class="media-title">{{ block.title || 'Áudio' }}</div>
                        <div v-if="block.url" class="media-status">✓ Configurado</div>
                        <div v-else class="media-status">Adicionar áudio</div>
                      </div>
                    </div>
                  </template>
                  <template v-else-if="block.type === 'video'">
                    <div class="msg-block-media msg-block-video">
                      <div class="media-icon-wrapper">
                        <i :class="block.is_video_note ? 'fa-solid fa-circle' : 'fa-solid fa-video'"></i>
                      </div>
                      <div class="media-info">
                        <div class="media-title">
                          {{ block.is_video_note ? 'Vídeo Bolinha' : (block.title || 'Vídeo') }}
                        </div>
                        <div v-if="block.url" class="media-status">✓ Configurado</div>
                        <div v-else class="media-status">Adicionar vídeo</div>
                      </div>
                    </div>
                  </template>
                  <template v-else>
                    <div class="msg-block-text">Conteúdo</div>
                  </template>
                </div>
              </div>
            </div>

            <!-- Múltiplas Saídas para Condição (Verdadeiro/Falso) -->
            <template v-if="step.type === 'condition'">
              <div 
                class="flow-port flow-port-output flow-port-condition-true"
                @mousedown.stop="startConnection($event, step.id, 'true')"
                :ref="(el) => registerPort(el, step.id, 'out-true')"
                title="Verdadeiro"
              >
                <div class="flow-port-dot"></div>
                <span class="flow-port-label">✓</span>
              </div>
              <div 
                class="flow-port flow-port-output flow-port-condition-false"
                @mousedown.stop="startConnection($event, step.id, 'false')"
                :ref="(el) => registerPort(el, step.id, 'out-false')"
                title="Falso"
              >
                <div class="flow-port-dot"></div>
                <span class="flow-port-label">✗</span>
              </div>
            </template>

            <!-- Múltiplas Saídas para Randomizador -->
            <template v-else-if="step.type === 'randomizer'">
              <div 
                v-for="(path, index) in step.config.paths"
                :key="path.id"
                class="flow-port flow-port-output flow-port-randomizer"
                :style="{ top: `calc(50% + ${(index - (step.config.paths.length - 1) / 2) * 30}px)` }"
                @mousedown.stop="startConnection($event, step.id, path.id)"
                :ref="(el) => registerPort(el, step.id, `out-${path.id}`)"
                :title="`${path.name} (${path.percentage}%)`"
              >
                <div class="flow-port-dot"></div>
                <span class="flow-port-label">{{ path.percentage }}%</span>
              </div>
            </template>

            <!-- Ponto de Saída Único (padrão para outros blocos) -->
            <div 
              v-else
              class="flow-port flow-port-output"
              @mousedown.stop="startConnection($event, step.id)"
              :ref="(el) => registerPort(el, step.id, 'out')"
            >
              <div class="flow-port-dot"></div>
            </div>
          </div>
        </div> <!-- Fim flow-canvas-workspace -->

        <!-- Controles de Zoom -->
        <div class="flow-canvas-controls">
          <button class="flow-control-btn" @click="zoomIn" title="Aumentar Zoom">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="8" x2="12" y2="16"/>
              <line x1="8" y1="12" x2="16" y2="12"/>
            </svg>
          </button>
          <div class="flow-control-zoom-label">{{ Math.round(canvasScale * 100) }}%</div>
          <button class="flow-control-btn" @click="zoomOut" title="Diminuir Zoom">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="8" y1="12" x2="16" y2="12"/>
            </svg>
          </button>
        </div>

        <!-- Hint -->
        <div class="flow-canvas-hint-overlay" v-if="isDraggingConnection">
          Solte sobre um ponto de entrada (↖) para conectar
        </div>
      </div>
      </div> <!-- Fim flow-editor-layout -->
    </div>

  <!-- Modal de Adicionar Bloco -->
  <div v-if="showAddBlockModal" class="abm-overlay" @click="showAddBlockModal = false">
    <div class="abm" @click.stop>

      <!-- Header -->
      <div class="abm-header">
        <div class="abm-title-row">
          <h3 class="abm-title">
            <i class="fa-solid fa-puzzle-piece abm-title-icon"></i>
            Adicionar Bloco
          </h3>
          <button class="abm-close" @click="showAddBlockModal = false">
            <i class="fa-solid fa-times"></i>
          </button>
        </div>
        <div class="abm-search-wrap">
          <i class="fa-solid fa-magnifying-glass abm-search-icon"></i>
          <input
            v-model="blockSearch"
            type="text"
            class="abm-search"
            placeholder="Buscar bloco..."
            @keydown.escape="showAddBlockModal = false"
          />
          <button v-if="blockSearch" class="abm-search-clear" @click="blockSearch = ''">
            <i class="fa-solid fa-times"></i>
          </button>
        </div>
      </div>

      <!-- Body -->
      <div class="abm-body">

        <!-- Navegação lateral de categorias -->
        <nav class="abm-nav">
          <button
            v-for="cat in blockCategories"
            :key="cat.id"
            class="abm-nav-item"
            :class="{ active: activeBlockCat === cat.id && !blockSearch }"
            @click="activeBlockCat = cat.id; blockSearch = ''"
          >
            <i :class="cat.icon" class="abm-nav-icon"></i>
            <span>{{ cat.label }}</span>
            <span class="abm-nav-count">{{ cat.blocks.length }}</span>
          </button>
        </nav>

        <!-- Painel de blocos -->
        <div class="abm-blocks">
          <template v-if="!blockSearch">
            <!-- Categoria selecionada -->
            <template v-for="cat in blockCategories" :key="cat.id">
              <div v-if="activeBlockCat === cat.id">
                <div class="abm-group-header">
                  <i :class="cat.icon" class="abm-group-icon"></i>
                  <span class="abm-group-title">{{ cat.label }}</span>
                  <span class="abm-group-desc">{{ cat.desc }}</span>
                </div>
                <div class="abm-cards">
                  <button
                    v-for="block in cat.blocks"
                    :key="block.type"
                    class="abm-card"
                    :class="{ 'abm-card-accent': block.accent }"
                    @click="handleAddBlock(block.type)"
                  >
                    <div class="abm-card-icon" :style="{ background: block.color }">
                      <i :class="block.icon"></i>
                    </div>
                    <div class="abm-card-body">
                      <div class="abm-card-header">
                        <span class="abm-card-label">{{ block.label }}</span>
                        <span v-if="block.pro" class="abm-badge abm-badge-pro">PRO</span>
                        <span v-if="block.ai" class="abm-badge abm-badge-ai">AI</span>
                        <span v-if="block.isNew" class="abm-badge abm-badge-new">NOVO</span>
                      </div>
                      <span class="abm-card-desc">{{ block.desc }}</span>
                    </div>
                    <i class="fa-solid fa-chevron-right abm-card-chevron"></i>
                  </button>
                </div>
              </div>
            </template>
          </template>

          <!-- Resultados de busca -->
          <template v-else>
            <template v-for="cat in blockCategories" :key="cat.id">
              <div
                v-if="cat.blocks.filter(b => b.label.toLowerCase().includes(blockSearch.toLowerCase()) || b.desc.toLowerCase().includes(blockSearch.toLowerCase())).length"
                class="abm-blocks-group"
              >
                <div class="abm-group-search-label">
                  <i :class="cat.icon"></i> {{ cat.label }}
                </div>
                <div class="abm-cards">
                  <button
                    v-for="block in cat.blocks.filter(b => b.label.toLowerCase().includes(blockSearch.toLowerCase()) || b.desc.toLowerCase().includes(blockSearch.toLowerCase()))"
                    :key="block.type"
                    class="abm-card"
                    :class="{ 'abm-card-accent': block.accent }"
                    @click="handleAddBlock(block.type)"
                  >
                    <div class="abm-card-icon" :style="{ background: block.color }">
                      <i :class="block.icon"></i>
                    </div>
                    <div class="abm-card-body">
                      <div class="abm-card-header">
                        <span class="abm-card-label">{{ block.label }}</span>
                        <span v-if="block.pro" class="abm-badge abm-badge-pro">PRO</span>
                        <span v-if="block.ai" class="abm-badge abm-badge-ai">AI</span>
                        <span v-if="block.isNew" class="abm-badge abm-badge-new">NOVO</span>
                      </div>
                      <span class="abm-card-desc">{{ block.desc }}</span>
                    </div>
                    <i class="fa-solid fa-chevron-right abm-card-chevron"></i>
                  </button>
                </div>
              </div>
            </template>
            <div
              v-if="!blockCategories.some(c => c.blocks.some(b => b.label.toLowerCase().includes(blockSearch.toLowerCase()) || b.desc.toLowerCase().includes(blockSearch.toLowerCase())))"
              class="abm-empty"
            >
              <i class="fa-solid fa-magnifying-glass abm-empty-icon"></i>
              <p>Nenhum bloco encontrado para "<strong>{{ blockSearch }}</strong>"</p>
            </div>
          </template>
        </div>

      </div>
    </div>
  </div>

  <!-- Modal de Gatilhos -->
  <div v-if="showTriggerModal" class="modal-overlay" @click="showTriggerModal = false">
    <div class="modal-content" style="max-width: 780px;" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">Iniciar automação quando...</h3>
        <button class="modal-close" @click="showTriggerModal = false">
          <i class="fa-solid fa-times"></i>
        </button>
      </div>
      <div class="modal-body trigger-modal-body">
        <div class="trigger-sidebar">
          <div class="trigger-nav-item active">
            <i class="fa-brands fa-telegram"></i>
            Telegram
          </div>
          <div class="trigger-nav-item disabled">
            <i class="fa-regular fa-square"></i>
            Eventos de contato
          </div>
        </div>
        <div class="trigger-main">
          <div class="trigger-header">
            <div>
              <p class="trigger-kicker">Gatilhos</p>
              <p class="trigger-subkicker">Evento específico do Telegram que inicia sua automação.</p>
            </div>
          </div>

          <div class="trigger-card" @click="addTrigger('telegram_message')">
            <div class="trigger-card-icon">
              <i class="fa-brands fa-telegram"></i>
            </div>
            <div class="trigger-card-body">
              <p class="trigger-card-kicker">Mensagem do Telegram</p>
              <p class="trigger-card-title">O usuário envia uma mensagem</p>
              <p class="trigger-card-desc">Selecione uma forma de acionar a automação.</p>
            </div>
            <div class="trigger-card-chevron">
              <i class="fa-solid fa-chevron-right"></i>
            </div>
          </div>

          <div class="trigger-card" @click="addTrigger('telegram_referral')">
            <div class="trigger-card-icon">
              <i class="fa-brands fa-telegram"></i>
            </div>
            <div class="trigger-card-body">
              <p class="trigger-card-kicker">URL de Referência do Telegram</p>
              <p class="trigger-card-title">O usuário clica em um link de referência</p>
            </div>
            <div class="trigger-card-chevron">
              <i class="fa-solid fa-chevron-right"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="showTriggerModal = false">Cancelar</button>
      </div>
    </div>
  </div>

  <!-- Confirm Dialog -->
  <ConfirmDialog
    :is-visible="confirmDialog.isVisible.value"
    :title="confirmDialog.title.value"
    :message="confirmDialog.message.value"
    :confirm-text="confirmDialog.confirmText.value"
    :cancel-text="confirmDialog.cancelText.value"
    :type="confirmDialog.type.value"
    @confirm="confirmDialog.handleConfirm"
    @cancel="confirmDialog.handleCancel"
    @update:is-visible="(val) => confirmDialog.isVisible.value = val"
  />
</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import ImageUpload from '@/components/ImageUpload.vue'
import AudioUpload from '@/components/AudioUpload.vue'
import VideoUpload from '@/components/VideoUpload.vue'
import PlaceholderInput from '@/components/PlaceholderInput.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { getFlow, listFlowSteps, updateFlow, updateFlowStep, deleteFlowStep, createFlowStep, runFlowDemo, listFlows } from '@/api/flows'
import { listChannels, updateChannel } from '@/api/channels'

const route = useRoute()
const flowId = computed(() => Number(route.params.id))
const toast = useToast()
const confirmDialog = useConfirmDialog()

const flow = ref(null)
const steps = ref([])
const selectedStep = ref(null)
const selectedBlock = ref(null)
const isSaving = ref(false)
const isPageLoading = ref(true)
let saveTimeout = null
const showTriggerModal = ref(false)
const showAddBlockModal = ref(false)
const blockSearch = ref('')
const activeBlockCat = ref('inicio')
const contentTextareaRef = ref(null)
const availableFlows = ref([])

const blockCategories = computed(() => [
  {
    id: 'inicio',
    label: 'Início',
    desc: 'Ponto de entrada do fluxo',
    icon: 'fa-solid fa-flag',
    blocks: [
      {
        type: 'trigger',
        label: 'Gatilho',
        desc: 'Define como e quando a automação é iniciada',
        icon: 'fa-solid fa-play',
        color: 'linear-gradient(135deg, #22c55e, #16a34a)',
      },
      {
        type: 'start',
        label: 'Iniciar Automação',
        desc: 'Ponto de partida com mensagem de boas-vindas',
        icon: 'fa-solid fa-arrow-right',
        color: 'linear-gradient(135deg, #00FF66, #00cc52)',
      },
    ],
  },
  {
    id: 'conteudo',
    label: 'Conteúdo',
    desc: 'Envie mensagens e mídias',
    icon: 'fa-solid fa-message',
    blocks: [
      {
        type: 'telegram',
        label: 'Mensagem Telegram',
        desc: 'Envia texto, imagem, vídeo ou áudio pelo Telegram',
        icon: 'fa-brands fa-telegram',
        color: 'linear-gradient(135deg, #229ED9, #1E88E5)',
      },
    ],
  },
  {
    id: 'ia',
    label: 'Inteligência Artificial',
    desc: 'Automatize com IA generativa',
    icon: 'fa-solid fa-brain',
    blocks: [
      {
        type: 'ai',
        label: 'Etapa de IA',
        desc: 'Delega a conversa à IA com um prompt personalizado',
        icon: 'fa-solid fa-sparkles',
        color: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
        ai: true,
      },
    ],
  },
  {
    id: 'logica',
    label: 'Lógica',
    desc: 'Controle o fluxo de execução',
    icon: 'fa-solid fa-code-branch',
    blocks: [
      {
        type: 'actions',
        label: 'Ações',
        desc: 'Executa ações: tags, campos, sequences e muito mais',
        icon: 'fa-solid fa-bolt',
        color: 'linear-gradient(135deg, #f59e0b, #d97706)',
      },
      {
        type: 'condition',
        label: 'Condição',
        desc: 'Ramifica o fluxo com base em regras e campos do contato',
        icon: 'fa-solid fa-filter',
        color: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
        pro: true,
      },
      {
        type: 'randomizer',
        label: 'Randomizador',
        desc: 'Distribui o tráfego em caminhos aleatórios (A/B test)',
        icon: 'fa-solid fa-shuffle',
        color: 'linear-gradient(135deg, #a855f7, #9333ea)',
        pro: true,
      },
      {
        type: 'smart-delay',
        label: 'Atraso Inteligente',
        desc: 'Pausa a execução por um tempo determinado',
        icon: 'fa-solid fa-clock',
        color: 'linear-gradient(135deg, #ef4444, #dc2626)',
        pro: true,
      },
    ],
  },
  {
    id: 'fluxos',
    label: 'Fluxos',
    desc: 'Conecte e redirecione entre fluxos',
    icon: 'fa-solid fa-diagram-project',
    blocks: [
      {
        type: 'go_to_flow',
        label: 'Ir para outro Fluxo',
        desc: 'Redireciona o contato para um fluxo diferente ao atingir este passo',
        icon: 'fa-solid fa-arrow-up-right-from-square',
        color: 'linear-gradient(135deg, #00FF66, #00cc52)',
        isNew: true,
        accent: true,
      },
    ],
  },
  {
    id: 'extras',
    label: 'Extras',
    desc: 'Ferramentas de organização',
    icon: 'fa-solid fa-ellipsis',
    blocks: [
      {
        type: 'comment',
        label: 'Comentário',
        desc: 'Adiciona anotações visuais ao fluxo (não afeta execução)',
        icon: 'fa-solid fa-file-lines',
        color: 'linear-gradient(135deg, #f97316, #ea580c)',
      },
    ],
  },
])
const botUsername = ref('seu_bot') // Username do bot Telegram
const channelsCache = ref([]) // guarda lista de canais carregados

// ===== Text toolbar (sidebar footer) =====
const sidebarRootRef = ref(null)
const activeTextEl = ref(null)
const emojiPickerOpen = ref(false)
const emojiList = [
  '😀','😃','😄','😁','😅','😂','🙂','😉','😍','🤔',
  '👍','🙏','✅','❌','🔥','💡','🎉','❤️','📌','🔗'
]

const canEditActiveText = computed(() => {
  const el = activeTextEl.value
  if (!el) return false
  if (el.disabled) return false
  if (el.readOnly) return false
  return true
})

const isTextEditableEl = (el) => {
  if (!el) return false
  const tag = (el.tagName || '').toLowerCase()
  if (tag === 'textarea') return true
  if (tag === 'input') {
    const type = (el.getAttribute('type') || 'text').toLowerCase()
    return ['text', 'search', 'url', 'email', 'tel', ''].includes(type)
  }
  return false
}

const setActiveTextFromEvent = (event) => {
  const target = event?.target
  if (!isTextEditableEl(target)) return
  activeTextEl.value = target
}

const insertIntoActiveText = (insertText) => {
  const el = activeTextEl.value
  if (!canEditActiveText.value || !el) return

  try { el.focus() } catch (e) {}

  const value = el.value ?? ''
  const start = typeof el.selectionStart === 'number' ? el.selectionStart : value.length
  const end = typeof el.selectionEnd === 'number' ? el.selectionEnd : start
  const nextValue = value.slice(0, start) + insertText + value.slice(end)

  el.value = nextValue
  const cursor = start + String(insertText).length
  if (typeof el.setSelectionRange === 'function') {
    el.setSelectionRange(cursor, cursor)
  }
  el.dispatchEvent(new Event('input', { bubbles: true }))
}

const wrapActiveSelection = (openTag, closeTag) => {
  const el = activeTextEl.value
  if (!canEditActiveText.value || !el) return

  try { el.focus() } catch (e) {}

  const value = el.value ?? ''
  const start = typeof el.selectionStart === 'number' ? el.selectionStart : value.length
  const end = typeof el.selectionEnd === 'number' ? el.selectionEnd : start

  if (start === end) {
    const nextValue = value.slice(0, start) + openTag + closeTag + value.slice(end)
    el.value = nextValue
    const cursor = start + openTag.length
    if (typeof el.setSelectionRange === 'function') {
      el.setSelectionRange(cursor, cursor)
    }
    el.dispatchEvent(new Event('input', { bubbles: true }))
    return
  }

  const selected = value.slice(start, end)
  const nextValue = value.slice(0, start) + openTag + selected + closeTag + value.slice(end)
  el.value = nextValue
  if (typeof el.setSelectionRange === 'function') {
    el.setSelectionRange(start + openTag.length, start + openTag.length + selected.length)
  }
  el.dispatchEvent(new Event('input', { bubbles: true }))
}

const toggleEmojiPicker = () => {
  if (!canEditActiveText.value) return
  emojiPickerOpen.value = !emojiPickerOpen.value
}

const createLinkOnActiveSelection = () => {
  const el = activeTextEl.value
  if (!canEditActiveText.value || !el) return

  const value = el.value ?? ''
  const start = typeof el.selectionStart === 'number' ? el.selectionStart : value.length
  const end = typeof el.selectionEnd === 'number' ? el.selectionEnd : start
  const selected = start !== end ? value.slice(start, end) : ''

  const url = window.prompt('Cole a URL do link (https://...)', 'https://')
  if (!url) return

  const label = selected || window.prompt('Texto do link', 'Clique aqui') || ''
  if (!label) return

  // Evitar quebrar a sintaxe do MarkdownV2 em URLs comuns.
  const safeUrl = String(url).trim().replace(/\s+/g, '%20').replace(/\(/g, '%28').replace(/\)/g, '%29')
  const safeLabel = String(label).replace(/[\[\]]/g, '')
  const md = `[${safeLabel}](${safeUrl})`

  // Substituir seleção ou inserir no cursor
  if (start !== end) {
    const nextValue = value.slice(0, start) + md + value.slice(end)
    el.value = nextValue
    const cursor = start + md.length
    if (typeof el.setSelectionRange === 'function') el.setSelectionRange(cursor, cursor)
  } else {
    const nextValue = value.slice(0, start) + md + value.slice(end)
    el.value = nextValue
    const cursor = start + md.length
    if (typeof el.setSelectionRange === 'function') el.setSelectionRange(cursor, cursor)
  }

  el.dispatchEvent(new Event('input', { bubbles: true }))
}

const handleSidebarFocusIn = (event) => {
  setActiveTextFromEvent(event)
}

const handleSidebarFocusOut = () => {
  // Wait for the next focused element (focusin may fire right after focusout)
  window.setTimeout(() => {
    const next = document.activeElement
    if (!isTextEditableEl(next)) {
      activeTextEl.value = null
    }
  }, 0)
}

const handleSidebarMouseDown = (event) => {
  setActiveTextFromEvent(event)
}

const handleDocumentMouseDown = (event) => {
  if (!emojiPickerOpen.value) return
  const sidebarEl = sidebarRootRef.value
  if (!sidebarEl) {
    emojiPickerOpen.value = false
    return
  }

  const target = event.target
  const inPopover = target?.closest?.('.emoji-popover')
  const inEmojiBtn = target?.closest?.('.text-toolbar-btn')
  if (!inPopover && !inEmojiBtn) {
    emojiPickerOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleDocumentMouseDown)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleDocumentMouseDown)
})

// Busca username via token e persiste no canal
const fetchBotUsername = async (channel) => {
  if (!channel) return null
  let config = channel.config
  try {
    config = typeof config === 'string' ? JSON.parse(config) : (config || {})
  } catch (e) {
    config = {}
  }

  const token = config.bot_token
  if (!token) return null

  try {
    const res = await fetch(`https://api.telegram.org/bot${token}/getMe`)
    const data = await res.json()
    if (data?.ok && data.result?.username) {
      const username = data.result.username.replace('@', '')
      botUsername.value = username

      // Persistir no canal para próximos usos
      try {
        await updateChannel(channel.id, { bot_username: username })
      } catch (e) {
        console.warn('Não foi possível salvar bot_username no canal:', e)
      }
      return username
    }
  } catch (e) {
    console.warn('Falha ao buscar username do Telegram:', e)
  }
  return null
}
const availableSteps = computed(() => {
  return steps.value.filter(s => s.id !== selectedStep.value?.id)
})
const activeTooltip = ref(null)

const toggleTooltip = (tooltipId, event) => {
  event.stopPropagation()
  if (activeTooltip.value === tooltipId) {
    activeTooltip.value = null
  } else {
    activeTooltip.value = tooltipId
    
    // Posicionar tooltip usando coordenadas fixas
    nextTick(() => {
      const iconElement = event.currentTarget
      const tooltipElement = iconElement.querySelector('.tooltip-text')
      if (tooltipElement && iconElement) {
        const iconRect = iconElement.getBoundingClientRect()
        const tooltipHeight = tooltipElement.offsetHeight
        
        // Posicionar acima do ícone
        tooltipElement.style.top = `${iconRect.top - tooltipHeight - 12}px`
        tooltipElement.style.left = `${iconRect.left + iconRect.width / 2}px`
      }
    })
  }
}

const closeTooltip = (event) => {
  // Não fechar se clicar no tooltip ou no ícone
  if (event && (
    event.target.closest('.tooltip-text') || 
    event.target.closest('.info-icon')
  )) {
    return
  }
  activeTooltip.value = null
}

const personalizationTags = [
  { label: 'Primeiro Nome', value: '{primeiro_nome}' },
  { label: 'Sobrenome', value: '{sobrenome}' },
  { label: 'Nome Completo', value: '{nome_completo}' },
  { label: 'E-mail', value: '{email}' },
  { label: 'Celular', value: '{celular}' },
  { label: 'ID do contato', value: '{contact_id}' },
  { label: 'Última mensagem', value: '{ultima_mensagem}' },
  { label: 'Telegram', value: '{telegram_username}' },
]

const textTagDropdownOpen = ref(false)
const buttonTagDropdownOpen = ref(false)

const toggleTagDropdown = (type = 'text') => {
  if (type === 'button') {
    buttonTagDropdownOpen.value = !buttonTagDropdownOpen.value
  } else {
    textTagDropdownOpen.value = !textTagDropdownOpen.value
  }
}

const hasTrigger = computed(() => steps.value.some((s) => s.type === 'trigger'))

const triggerDefaultLink = computed(() => {
  // Link de exemplo; se tivermos username do bot podemos ajustar depois
  return 'https://t.me/seu_bot?start=ref123'
})

const uid = () => `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`

const createDefaultBlocks = () => ([
  { id: uid(), type: 'text', text: 'Adicionar texto' },
  { id: uid(), type: 'text', text: 'Adicionar texto' },
  { id: uid(), type: 'delay', seconds: 3 },
  { id: uid(), type: 'button', label: 'Botão 1', menuTitle: 'Telegram Menu' }
])

const ensureMessageBlocks = (step) => {
  if (!step.config) step.config = {}
  if (!Array.isArray(step.config.blocks)) {
    step.config.blocks = []
  }

  // Compatibilidade: fluxos antigos podem ter blocks sem `id`.
  // Sem `id`, o :key fica undefined e operações como remover/drag podem falhar.
  step.config.blocks.forEach((block) => {
    if (!block.id) {
      block.id = uid()
    }
  })
}

// Canvas e Zoom
const containerRef = ref(null)
const workspaceRef = ref(null)
const canvasScale = ref(1)
const canvasOffset = ref({ x: 50, y: 50 })
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0 })

// Helper: aplica o transform direto no DOM (zero overhead de reatividade)
const applyWorkspaceTransform = (x, y, scale) => {
  if (workspaceRef.value) {
    workspaceRef.value.style.transform = `translate(${x}px, ${y}px) scale(${scale})`
  }
}

// Variáveis raw (não reativas) para pan — zero overhead Vue durante movimento
let _panCurrentX = 50
let _panCurrentY = 50

// Posições dos Nós (livre)
const nodePositions = ref({}) // { stepId: { x, y } }
const draggingNodeId = ref(null)
const dragStart = ref({ x: 0, y: 0, nodeX: 0, nodeY: 0 })

// Drag and Drop de Blocos
const draggingBlock = ref(null)
const dragOverIndex = ref(null)
const blockDragStep = ref(null)
const ghostElement = ref(null)

// Conexões
const connections = ref([]) // { id, from, to }
const connectionPaths = ref([]) // { id, path }
const isDraggingConnection = ref(false)
const connectionFrom = ref(null)
const tempConnectionEnd = ref({ x: 0, y: 0 })
const hoveredPort = ref(null)
const portRefs = ref({})
let updateFrame = null

const scheduleConnectionUpdate = () => {
  if (updateFrame) {
    cancelAnimationFrame(updateFrame)
  }
  updateFrame = requestAnimationFrame(updateConnectionPaths)
}

const registerPort = (el, stepId, portType) => {
  if (!portRefs.value[stepId]) {
    portRefs.value[stepId] = {}
  }
  if (el) {
    portRefs.value[stepId][portType] = el
  } else {
    delete portRefs.value[stepId][portType]
  }
  scheduleConnectionUpdate()
}

const screenToWorkspace = ({ x, y }) => {
  const container = containerRef.value
  if (!container) return { x: 0, y: 0 }
  const rect = container.getBoundingClientRect()
  return {
    x: (x - rect.left - canvasOffset.value.x) / canvasScale.value,
    y: (y - rect.top - canvasOffset.value.y) / canvasScale.value
  }
}

const getPortCenterWorkspace = (stepId, portType, outputId = 'default') => {
  // Para saídas específicas (condition, randomizer), usar o portType com outputId
  const portKey = portType === 'out' && outputId !== 'default' ? `out-${outputId}` : portType
  const portEl = portRefs.value[stepId]?.[portKey]
  if (!portEl) return null
  const rect = portEl.getBoundingClientRect()
  return screenToWorkspace({
    x: rect.left + rect.width / 2,
    y: rect.top + rect.height / 2
  })
}

// ==================== LOAD DATA ====================
const loadData = async () => {
  try {
    // Reset completo ao carregar novo fluxo
    selectedStep.value = null
    selectedBlock.value = null
    steps.value = []
    connections.value = []
    botUsername.value = 'seu_bot' // ← reset imediato para evitar vazamento de fluxo anterior

    flow.value = await getFlow(flowId.value)
    steps.value = await listFlowSteps(flowId.value)

    // Buscar username do bot do canal conectado
    if (flow.value?.channel_id) {
      try {
        channelsCache.value = await listChannels()
        // Coercão explícita de tipo para evitar falha por string vs number
        const channel = channelsCache.value.find(c => Number(c.id) === Number(flow.value.channel_id))

        if (channel) {
          // Tentar ler bot_username do config, mesmo que config seja null
          let savedUsername = ''
          if (channel.config) {
            try {
              const config = typeof channel.config === 'string'
                ? JSON.parse(channel.config)
                : channel.config
              savedUsername = (config.bot_username || '').replace('@', '')
            } catch (e) {
              console.warn('Erro ao parsear config do canal:', e)
            }
          }

          if (savedUsername) {
            botUsername.value = savedUsername
          } else {
            // Não há bot_username salvo: buscar via token na API do Telegram e persistir
            const resolved = await fetchBotUsername(channel)
            if (!resolved) {
              console.warn('Não foi possível resolver bot_username para canal', channel.id)
            }
          }
        } else {
          console.warn('Canal do fluxo não encontrado na lista. channel_id =', flow.value.channel_id)
        }
      } catch (error) {
        console.error('Erro ao buscar username do bot:', error)
      }
    } else {
      // Mesmo sem canal_id no fluxo, carregar TODOS os canais para poder usar
      try {
        channelsCache.value = await listChannels()

        // Sem canal vinculado: usar o primeiro canal Telegram ativo como fallback
        const firstTelegramChannel = channelsCache.value.find(c => c.type === 'telegram' && c.is_active)
        if (firstTelegramChannel) {
          let savedUsername = ''
          if (firstTelegramChannel.config) {
            try {
              const config = typeof firstTelegramChannel.config === 'string'
                ? JSON.parse(firstTelegramChannel.config)
                : firstTelegramChannel.config
              savedUsername = (config.bot_username || '').replace('@', '')
            } catch (e) { /* ignore */ }
          }
          if (savedUsername) {
            botUsername.value = savedUsername
          } else {
            await fetchBotUsername(firstTelegramChannel)
          }
        }
      } catch (error) {
        console.error('Erro ao carregar canais:', error)
      }
    }
    
    // Carregar fluxos disponíveis para "Go to Flow"
    try {
      availableFlows.value = await listFlows()
    } catch (e) {
      console.warn('Erro ao carregar fluxos:', e)
      availableFlows.value = []
    }
    
    // Garantir blocks padrão para mensagens e estrutura de ações
    steps.value.forEach((step) => {
      if (step.type === 'message') ensureMessageBlocks(step)
      // Garantir estrutura de ações
      if (step.type === 'action') {
        if (!step.config) step.config = {}
        if (!step.config.actions) step.config.actions = []
      }
    })
    
    // Carregar posições e conexões salvas (do config do flow)
    const flowConfig = flow.value.config || {}
    const savedPositions = flowConfig.nodePositions || {}
    const savedConnections = flowConfig.connections || []
    
    // Inicializar posições dos nós
    steps.value.forEach((step, index) => {
      if (savedPositions[step.id]) {
        // Usar posição salva
        nodePositions.value[step.id] = savedPositions[step.id]
      } else {
        // Criar posição em grid
        nodePositions.value[step.id] = {
          x: 100 + (index % 3) * 350,
          y: 100 + Math.floor(index / 3) * 250
        }
      }
    })
    
    // Restaurar conexões
    connections.value = savedConnections

    // Sincronização bidirecional entre conexões e btn.targetStepId
    steps.value.forEach(step => {
      if (step.config?.blocks) {
        step.config.blocks.forEach(block => {
          if (block.type === 'button' && block.buttons) {
            block.buttons.forEach((btn, btnIdx) => {
              const outputId = `btn-${block.id}-${btnIdx}`

              // 1) Se btn.targetStepId existe mas não há conexão visual → criar conexão
              if (btn.action === 'flow' && btn.targetStepId) {
                const alreadyExists = connections.value.some(c =>
                  c.from === step.id && c.outputId === outputId
                )
                if (!alreadyExists) {
                  connections.value.push({
                    id: `${step.id}-${outputId}-${btn.targetStepId}`,
                    from: step.id,
                    to: btn.targetStepId,
                    outputId: outputId
                  })
                }
              }

              // 2) Se há conexão visual mas btn.targetStepId está vazio → popular do flow.config
              if (btn.action === 'flow' && !btn.targetStepId) {
                const conn = connections.value.find(c =>
                  c.from === step.id && c.outputId === outputId
                )
                if (conn) {
                  btn.targetStepId = conn.to
                }
              }
            })
          }
        })
      }
    })
    
    updateConnectionPaths()
  } catch (error) {
    console.error('Erro ao carregar dados:', error)
  } finally {
    isPageLoading.value = false
    // Recalcular conexões após o canvas ficar visível
    nextTick(() => scheduleConnectionUpdate())
  }
}

// ==================== SAVE WORKFLOW ====================
const saveWorkflow = async () => {
  if (isSaving.value || !flow.value) return
  
  try {
    isSaving.value = true
    
    // IMPORTANTE: Recalcular order_index baseado nas conexões
    recalculateOrderIndex()

    // Sincronizar targetStepId de todos os botões a partir das conexões visuais
    // Garante consistência mesmo que o update reativo não tenha sido salvo antes
    steps.value.forEach(step => {
      if (step.config?.blocks) {
        step.config.blocks.forEach(block => {
          if (block.type === 'button' && block.buttons) {
            block.buttons.forEach((btn, btnIdx) => {
              if (btn.action === 'flow') {
                const outputId = `btn-${block.id}-${btnIdx}`
                const conn = connections.value.find(c => c.from === step.id && c.outputId === outputId)
                if (conn) {
                  btn.targetStepId = conn.to
                }
              }
            })
          }
        })
      }
    })
    
    // Salvar posições e conexões no config do flow
    const flowConfig = {
      nodePositions: nodePositions.value,
      connections: connections.value
    }
    
    const payload = {
      name: flow.value.name,
      description: flow.value.description,
      trigger_type: flow.value.trigger_type,
      config: flowConfig
    }
    
    console.log('💾 Salvando workflow...', payload)
    
    await updateFlow(flowId.value, payload)
    
    // Salvar o order_index atualizado de cada step
    for (const step of steps.value) {
      try {
        await updateFlowStep(flowId.value, step.id, {
          type: step.type,
          config: step.config,
          order_index: step.order_index
        })
      } catch (error) {
        console.error(`❌ Erro ao atualizar order_index do step ${step.id}:`, error)
      }
    }
    
    console.log('✅ Workflow salvo! Posições:', Object.keys(nodePositions.value).length, 'Conexões:', connections.value.length, 'Steps:', steps.value.length)
  } catch (error) {
    console.error('❌ Erro ao salvar workflow:', error)
    console.error('❌ Detalhes:', error.response?.data)
  } finally {
    isSaving.value = false
  }
}

// Recalcular order_index baseado nas conexões do fluxo
const recalculateOrderIndex = () => {
  console.log('🔄 Recalculando order_index baseado nas conexões...')
  
  // Encontrar o trigger (sempre é o primeiro)
  const trigger = steps.value.find(s => s.type === 'trigger')
  if (!trigger) {
    console.warn('⚠️ Nenhum trigger encontrado')
    return
  }
  
  // Mapear conexões: stepId -> próximo stepId
  const connectionsMap = {}
  connections.value.forEach(conn => {
    connectionsMap[conn.from] = conn.to
  })
  
  // Percorrer o fluxo a partir do trigger seguindo as conexões
  const orderedSteps = []
  let currentStepId = trigger.id
  let orderIndex = 1
  
  // Adicionar trigger primeiro
  orderedSteps.push({ id: trigger.id, order_index: orderIndex })
  
  // Seguir a cadeia de conexões
  while (connectionsMap[currentStepId]) {
    orderIndex++
    currentStepId = connectionsMap[currentStepId]
    orderedSteps.push({ id: currentStepId, order_index: orderIndex })
  }
  
  // Adicionar steps sem conexão no final (órfãos)
  const connectedIds = orderedSteps.map(s => s.id)
  steps.value.forEach(step => {
    if (!connectedIds.includes(step.id)) {
      orderIndex++
      orderedSteps.push({ id: step.id, order_index: orderIndex })
      console.warn(`⚠️ Step ${step.id} não está conectado, adicionando no final`)
    }
  })
  
  // Atualizar order_index nos steps
  orderedSteps.forEach(ordered => {
    const step = steps.value.find(s => s.id === ordered.id)
    if (step) {
      step.order_index = ordered.order_index
      console.log(`📍 Step ${step.id} → order_index: ${step.order_index}`)
    }
  })
  
  console.log('✅ Order_index recalculado:', orderedSteps.length, 'steps')
  return orderedSteps
}

// Auto-save com debounce (espera 1 segundo após última alteração)
const autoSave = async () => {
  console.log('🔄 Auto-save iniciado...')
  
  // Se estiver editando um step (mensagem ou gatilho), salvar o step
  if (selectedStep.value) {
    try {
      const payload = {
        type: selectedStep.value.type,
        config: selectedStep.value.config,
        order_index: selectedStep.value.order_index
      }
      
      console.log('💾 Salvando step:', selectedStep.value.id, payload)
      
      await updateFlowStep(flowId.value, selectedStep.value.id, payload)
      console.log('✅ Step salvo com sucesso!')
    } catch (error) {
      console.error('❌ Erro ao salvar step:', error)
      console.error('❌ Detalhes:', error.response?.data)
    }
  }
  
  // Salvar workflow (posições e conexões) com debounce
  if (saveTimeout) {
    clearTimeout(saveTimeout)
  }
  saveTimeout = setTimeout(() => {
    saveWorkflow()
  }, 1000)
}

// ==================== NODE OPERATIONS ====================
const addMessageStep = async () => {
  if (!hasTrigger.value) {
    showTriggerModal.value = true
    return
  }
  try {
  const nextIndex = steps.value.length + 1
    const newStep = await createFlowStep(flowId.value, {
      type: 'message',
      order_index: nextIndex,
      config: { text: `Bloco #${nextIndex}`, blocks: [] }
    })
    
    // Adicionar nova posição
    nodePositions.value[newStep.id] = {
      x: 100 + (steps.value.length % 3) * 350,
      y: 100 + Math.floor(steps.value.length / 3) * 250
    }
    
    steps.value.push(newStep)
    
    // Auto-salvar após adicionar bloco
    autoSave()
  } catch (error) {
    console.error('Erro ao adicionar passo:', error)
  }
}

const handleAddBlock = async (type) => {
  showAddBlockModal.value = false
  
  // Verificar se precisa de trigger primeiro
  if (!hasTrigger.value && type !== 'trigger') {
    showTriggerModal.value = true
    toast.warning('Adicione um gatilho primeiro')
    return
  }

  try {
    const nextIndex = steps.value.length + 1
    let stepConfig = {}
    let stepType = 'message'

    switch (type) {
      case 'trigger':
        showTriggerModal.value = true
        return
      
      case 'telegram':
      case 'message':
        stepType = 'message'
        stepConfig = { text: `Mensagem #${nextIndex}`, blocks: [] }
        break
      
      case 'channel':
        toast.info('Funcionalidade de canal em desenvolvimento')
        return
      
      case 'start':
        stepType = 'message'
        stepConfig = { text: 'Iniciar automação', blocks: [{ id: uid(), type: 'text', text: 'Bem-vindo!' }] }
        break
      
      case 'ai':
        stepType = 'ai'
        stepConfig = { prompt: '', model: 'gpt-4' }
        toast.info('Etapa de IA em desenvolvimento')
        return
      
      case 'actions':
        stepType = 'action'
        stepConfig = { 
          actions: []
        }
        break
      
      case 'condition':
        stepType = 'condition'
        stepConfig = { 
          conditionType: 'field', // field, tag, variable
          field: '',
          operator: 'equals', // equals, not_equals, contains, not_contains, exists, not_exists
          value: '',
          conditions: []
        }
        break
      
      case 'randomizer':
        stepType = 'randomizer'
        stepConfig = { 
          paths: [
            { id: uid(), name: 'Caminho A', percentage: 50 },
            { id: uid(), name: 'Caminho B', percentage: 50 }
          ]
        }
        break
      
      case 'smart-delay':
        stepType = 'wait'
        stepConfig = { 
          delayType: 'fixed', // fixed, random, smart
          value: 5,
          unit: 'seconds', // seconds, minutes, hours, days
          randomMin: 1,
          randomMax: 10
        }
        break
      
      case 'comment':
        stepType = 'comment'
        stepConfig = { 
          text: 'Adicione suas anotações aqui',
          color: '#f59e0b'
        }
        break
      
      case 'go_to_flow':
        stepType = 'action'
        stepConfig = {
          actions: [{ type: 'go_to_flow', flow_id: null }]
        }
        break
      
      case 'start':
        stepType = 'start_automation'
        stepConfig = { 
          flowId: null,
          flowName: ''
        }
        break
      
      default:
        stepType = 'message'
        stepConfig = { text: `Bloco #${nextIndex}`, blocks: [] }
    }

    const newStep = await createFlowStep(flowId.value, {
      type: stepType,
      order_index: nextIndex,
      config: stepConfig
    })
    
    // Adicionar nova posição
    nodePositions.value[newStep.id] = {
      x: 100 + (steps.value.length % 3) * 350,
      y: 100 + Math.floor(steps.value.length / 3) * 250
    }
    
    steps.value.push(newStep)
    
    // Selecionar o novo step
    selectedStep.value = newStep
    
    // Auto-salvar
    autoSave()
    
    toast.success('Bloco adicionado ao fluxo')
  } catch (error) {
    console.error('Erro ao adicionar bloco:', error)
    toast.error('Erro ao adicionar bloco')
  }
}

const deleteStep = async (stepId) => {
  try {
    await confirmDialog.showConfirm({
      title: 'Excluir bloco',
      message: 'Esta ação não poderá ser desfeita. Deseja excluir este bloco do fluxo?',
      confirmText: 'Excluir',
      cancelText: 'Cancelar',
      type: 'danger'
    })
  } catch {
    return // Usuário cancelou
  }
  
  try {
    console.log('🗑️ Deletando step:', stepId)
    
    // Deletar no backend
    await deleteFlowStep(flowId.value, stepId)
    
    console.log('✅ Step deletado do backend!')
    
    // Remover conexões relacionadas
    connections.value = connections.value.filter(c => c.from !== stepId && c.to !== stepId)
    
    // Remover o step do frontend
    steps.value = steps.value.filter(s => s.id !== stepId)
    delete nodePositions.value[stepId]
    
    // Fechar sidebar se o step deletado estava selecionado
    if (selectedStep.value && selectedStep.value.id === stepId) {
      selectedStep.value = null
    }
    
    updateConnectionPaths()
    
    // Salvar workflow (posições e conexões atualizadas)
    await saveWorkflow()
    
    console.log('✅ Bloco excluído completamente!')
    toast.success('Bloco removido do fluxo')
  } catch (error) {
    console.error('❌ Erro ao deletar step:', error)
    toast.error('Erro ao excluir bloco')
  }
}

// ==================== MÉTODOS AUXILIARES NOVOS BLOCOS ====================

// Randomizador
const addRandomPath = () => {
  if (!selectedStep.value?.config?.paths) return
  
  const newPath = {
    id: uid(),
    name: `Caminho ${String.fromCharCode(65 + selectedStep.value.config.paths.length)}`,
    percentage: 0
  }
  
  selectedStep.value.config.paths.push(newPath)
  autoSave()
}

const removeRandomPath = (index) => {
  if (!selectedStep.value?.config?.paths) return
  selectedStep.value.config.paths.splice(index, 1)
  autoSave()
}

const updateRandomPercentages = (changedIndex) => {
  // Auto-ajustar outras porcentagens proporcionalmente
  if (!selectedStep.value?.config?.paths) return
  
  const paths = selectedStep.value.config.paths
  const total = paths.reduce((sum, p) => sum + (p.percentage || 0), 0)
  
  if (total > 100) {
    // Reduzir o valor que foi mudado
    paths[changedIndex].percentage = Math.max(0, 100 - paths.reduce((sum, p, i) => 
      i !== changedIndex ? sum + (p.percentage || 0) : sum, 0
    ))
  }
  
  autoSave()
}

const getTotalPercentage = () => {
  if (!selectedStep.value?.config?.paths) return 0
  return selectedStep.value.config.paths.reduce((sum, p) => sum + (p.percentage || 0), 0)
}

// Atraso Inteligente
const getDelayPreview = () => {
  if (!selectedStep.value?.config) return ''
  
  const config = selectedStep.value.config
  const unit = config.unit || 'seconds'
  const unitLabels = {
    seconds: 'segundo(s)',
    minutes: 'minuto(s)',
    hours: 'hora(s)',
    days: 'dia(s)'
  }
  
  if (config.delayType === 'fixed') {
    return `Aguardar ${config.value || 0} ${unitLabels[unit]}`
  } else if (config.delayType === 'random') {
    return `Aguardar entre ${config.randomMin || 0} e ${config.randomMax || 0} ${unitLabels[unit]}`
  } else if (config.delayType === 'smart') {
    return `Aguardar até próximo horário comercial`
  }
  
  return ''
}

// Iniciar Automação
const onFlowSelected = () => {
  if (!selectedStep.value?.config?.flowId) return
  
  const selected = availableFlows.value.find(f => f.id === selectedStep.value.config.flowId)
  if (selected) {
    selectedStep.value.config.flowName = selected.name
  }
  autoSave()
}

// Cores para comentários
const commentColors = [
  '#f59e0b', // laranja
  '#ef4444', // vermelho
  '#3b82f6', // azul
  '#22c55e', // verde
  '#a855f7', // roxo
  '#ec4899', // rosa
  '#64748b'  // cinza
]

// ==================== STEP SELECTION ====================
const selectStep = (step) => {
  selectedStep.value = step
  selectedBlock.value = null
}

const selectBlock = (step, block) => {
  selectedStep.value = step
  selectedBlock.value = { stepId: step.id, blockId: block.id }
}

const removeBlock = (blockId) => {
  if (!selectedStep.value || selectedStep.value.type !== 'message') return
  const blocks = selectedStep.value.config.blocks || []
  const idx = blocks.findIndex((b) => b.id === blockId)
  if (idx >= 0) {
    blocks.splice(idx, 1)
    if (selectedBlock.value && selectedBlock.value.blockId === blockId) {
      selectedBlock.value = null
    }
    autoSave()
    toast.success('Elemento removido com sucesso')
  }
}

// ==================== DRAG AND DROP DE BLOCOS ====================
const startBlockDrag = (event, step, block, blockIndex) => {
  // Só iniciar drag se clicar no handle
  if (!event.target.closest('.msg-block-drag-handle')) {
    return
  }
  
  event.stopPropagation()
  draggingBlock.value = { ...block, originalIndex: blockIndex }
  blockDragStep.value = step
  
  // Criar elemento ghost
  const originalElement = event.target.closest('.msg-block')
  const ghost = originalElement.cloneNode(true)
  ghost.classList.add('msg-block-ghost')
  ghost.style.position = 'fixed'
  ghost.style.width = `${originalElement.offsetWidth}px`
  ghost.style.pointerEvents = 'none'
  ghost.style.zIndex = '9999'
  ghost.style.left = `${event.clientX - originalElement.offsetWidth / 2}px`
  ghost.style.top = `${event.clientY - 20}px`
  document.body.appendChild(ghost)
  ghostElement.value = ghost
  
  const handleMouseMove = (e) => {
    if (!draggingBlock.value) return
    
    // Mover ghost
    if (ghostElement.value) {
      ghostElement.value.style.left = `${e.clientX - ghostElement.value.offsetWidth / 2}px`
      ghostElement.value.style.top = `${e.clientY - 20}px`
    }
    
    // Calcular sobre qual bloco está passando
    const blocks = blockDragStep.value.config.blocks
    const mouseY = e.clientY
    
    // Encontrar o bloco mais próximo
    let closestIndex = draggingBlock.value.originalIndex
    let closestDistance = Infinity
    
    blocks.forEach((_, index) => {
      if (index === draggingBlock.value.originalIndex) return
      
      const element = document.querySelector(`[data-block-index="${index}"]`)
      if (element) {
        const rect = element.getBoundingClientRect()
        const centerY = rect.top + rect.height / 2
        const distance = Math.abs(mouseY - centerY)
        
        if (distance < closestDistance) {
          closestDistance = distance
          closestIndex = index
        }
      }
    })
    
    dragOverIndex.value = closestIndex
  }
  
  const handleMouseUp = () => {
    if (draggingBlock.value && dragOverIndex.value !== null) {
      const blocks = blockDragStep.value.config.blocks
      const fromIndex = draggingBlock.value.originalIndex
      const toIndex = dragOverIndex.value
      
      if (fromIndex !== toIndex) {
        // Remover do índice original
        const [movedBlock] = blocks.splice(fromIndex, 1)
        // Inserir no novo índice
        blocks.splice(toIndex, 0, movedBlock)
        
        console.log(`Bloco movido de ${fromIndex} para ${toIndex}`)
        autoSave()
        toast.success('Sequência atualizada')
      }
    }
    
    // Remover ghost com animação
    if (ghostElement.value) {
      ghostElement.value.style.transition = 'all 0.2s'
      ghostElement.value.style.opacity = '0'
      ghostElement.value.style.transform = 'scale(0.8)'
      setTimeout(() => {
        if (ghostElement.value && ghostElement.value.parentNode) {
          ghostElement.value.parentNode.removeChild(ghostElement.value)
        }
        ghostElement.value = null
      }, 200)
    }
    
    draggingBlock.value = null
    dragOverIndex.value = null
    blockDragStep.value = null
    
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

// Adicionar botão ao bloco de button
const addButton = () => {
  if (!currentBlock.value || currentBlock.value.type !== 'button') return
  
  if (!currentBlock.value.buttons) {
    currentBlock.value.buttons = []
  }
  
  currentBlock.value.buttons.push({
    text: '',
    action: 'url',   // 'url' | 'flow'
    url: '',
    targetStepId: ''
  })
  
  autoSave()
}

// Remover botão do bloco de button
const removeButton = (index) => {
  if (!currentBlock.value || currentBlock.value.type !== 'button') return
  if (!currentBlock.value.buttons) return
  
  currentBlock.value.buttons.splice(index, 1)
  autoSave()
}

// ==================== CONTENT BLOCKS ====================

const addContentBlock = (type) => {
  if (!selectedStep.value) {
    toast.warning('Selecione um bloco de mensagem primeiro')
    return
  }
  if (!hasTrigger.value) {
    showTriggerModal.value = true
    return
  }

  // Se não for um bloco de mensagem, por ora não adicionamos sub-blocos
  if (selectedStep.value.type !== 'message') {
    toast.info('Adicione sub-blocos apenas em blocos de Mensagem')
    return
  }

  ensureMessageBlocks(selectedStep.value)

  const mapping = {
    text: { type: 'text', text: '' },
    image: { type: 'image', url: '', caption: '' },
    audio: { type: 'audio', url: '', title: '' },
    video: { type: 'video', url: '', title: '', is_video_note: false },
    delay: { type: 'delay', seconds: 3 },
    data: { type: 'data', field: '', prompt: '' },
    more: { type: 'button', text: '', buttons: [] },
    button: { type: 'button', text: '', buttons: [] }
  }

  const block = mapping[type] || mapping.more
  const newBlock = { id: uid(), ...block }
  selectedStep.value.config.blocks.push(newBlock)
  selectedBlock.value = { stepId: selectedStep.value.id, blockId: newBlock.id }
  autoSave()
  
  // Feedback visual ao adicionar mídia
  if (['image', 'audio', 'video'].includes(type)) {
    toast.success(`${type === 'image' ? 'Imagem' : type === 'audio' ? 'Áudio' : 'Vídeo'} adicionado!`)
  }
}

const getNodeStyle = (stepId) => {
  const pos = nodePositions.value[stepId] || { x: 0, y: 0 }
  return {
    transform: `translate(${pos.x}px, ${pos.y}px)`
  }
}

// ==================== NODE DRAGGING ====================
// DOM refs dos nós para manipulação direta durante drag
const nodeEls = {}
const registerNodeEl = (el, stepId) => {
  if (el) nodeEls[stepId] = el
  else delete nodeEls[stepId]
}

// Posição raw do nó em drag (não reativo)
let _dragNodeX = 0
let _dragNodeY = 0

const startNodeDrag = (e, stepId) => {
  if (e.button !== 0) return

  e.stopPropagation() // não iniciar pan junto

  draggingNodeId.value = stepId
  const pos = nodePositions.value[stepId] || { x: 0, y: 0 }
  _dragNodeX = pos.x
  _dragNodeY = pos.y

  dragStart.value = {
    x: e.clientX,
    y: e.clientY,
    nodeX: pos.x,
    nodeY: pos.y
  }

  document.addEventListener('mousemove', handleNodeDragMove)
  document.addEventListener('mouseup', endNodeDrag)
}

const handleNodeDragMove = (e) => {
  if (!draggingNodeId.value) return

  const dx = (e.clientX - dragStart.value.x) / canvasScale.value
  const dy = (e.clientY - dragStart.value.y) / canvasScale.value
  _dragNodeX = dragStart.value.nodeX + dx
  _dragNodeY = dragStart.value.nodeY + dy

  // DOM direto — zero reatividade Vue
  const el = nodeEls[draggingNodeId.value]
  if (el) el.style.transform = `translate(${_dragNodeX}px, ${_dragNodeY}px)`

  scheduleConnectionUpdate()
}

const endNodeDrag = () => {
  const id = draggingNodeId.value
  draggingNodeId.value = null
  document.removeEventListener('mousemove', handleNodeDragMove)
  document.removeEventListener('mouseup', endNodeDrag)

  // Sincroniza estado reativo uma vez ao soltar
  if (id) {
    nodePositions.value[id] = { x: _dragNodeX, y: _dragNodeY }
    autoSave()
  }
}

// ==================== PAN ====================
const startPan = (e) => {
  if (e.button !== 0) return
  isPanning.value = true
  _panCurrentX = canvasOffset.value.x
  _panCurrentY = canvasOffset.value.y
  panStart.value = {
    x: e.clientX - canvasOffset.value.x,
    y: e.clientY - canvasOffset.value.y
  }
}

const handlePanMove = (e) => {
  if (!isPanning.value) return
  _panCurrentX = e.clientX - panStart.value.x
  _panCurrentY = e.clientY - panStart.value.y
  applyWorkspaceTransform(_panCurrentX, _panCurrentY, canvasScale.value)
}

const endPan = () => {
  if (!isPanning.value) return
  isPanning.value = false
  canvasOffset.value = { x: _panCurrentX, y: _panCurrentY }
  scheduleConnectionUpdate()
}

// ==================== ZOOM ====================
const handleWheel = (e) => {
  const delta = -e.deltaY * 0.001
  const newScale = Math.min(Math.max(0.3, canvasScale.value + delta), 2)
  canvasScale.value = newScale
  applyWorkspaceTransform(canvasOffset.value.x, canvasOffset.value.y, newScale)
  scheduleConnectionUpdate()
}

const zoomIn = () => {
  canvasScale.value = Math.min(2, canvasScale.value + 0.1)
  applyWorkspaceTransform(canvasOffset.value.x, canvasOffset.value.y, canvasScale.value)
  updateConnectionPaths()
}

const zoomOut = () => {
  canvasScale.value = Math.max(0.3, canvasScale.value - 0.1)
  applyWorkspaceTransform(canvasOffset.value.x, canvasOffset.value.y, canvasScale.value)
  updateConnectionPaths()
}

const resetZoom = () => {
  canvasScale.value = 1
  canvasOffset.value = { x: 50, y: 50 }
  applyWorkspaceTransform(50, 50, 1)
  updateConnectionPaths()
}

// ==================== CONNECTIONS ====================
const startConnection = (e, stepId, outputId = 'default') => {
  isDraggingConnection.value = true
  connectionFrom.value = { stepId, outputId }
  
  tempConnectionEnd.value = { x: e.clientX, y: e.clientY }
  
  document.addEventListener('mousemove', handleConnectionDragMove)
  document.addEventListener('mouseup', cancelConnection)
}

const handleConnectionDragMove = (e) => {
  if (!isDraggingConnection.value) return
  tempConnectionEnd.value = { x: e.clientX, y: e.clientY }
}

const completeConnection = (toStepId) => {
  if (!isDraggingConnection.value || !connectionFrom.value) return
  if (connectionFrom.value.stepId === toStepId) {
    cancelConnection()
    return
  }
  
  // Verificar se já existe uma conexão da mesma saída para o mesmo destino
  const exists = connections.value.some(c => 
    c.from === connectionFrom.value.stepId && 
    c.to === toStepId && 
    c.outputId === connectionFrom.value.outputId
  )
  
  if (!exists) {
    connections.value.push({
      id: `${connectionFrom.value.stepId}-${connectionFrom.value.outputId}-${toStepId}`,
      from: connectionFrom.value.stepId,
      to: toStepId,
      outputId: connectionFrom.value.outputId
    })

    // Se for uma porta de botão, sincronizar btn.targetStepId
    const oid = connectionFrom.value.outputId
    if (oid && oid.startsWith('btn-')) {
      const lastDash = oid.lastIndexOf('-')
      const btnIdx = parseInt(oid.substring(lastDash + 1))
      const blockId = oid.substring(4, lastDash) // remove 'btn-' prefix
      const fromStep = steps.value.find(s => s.id === connectionFrom.value.stepId)
      if (fromStep?.config?.blocks) {
        const block = fromStep.config.blocks.find(b => b.id === blockId)
        if (block?.buttons?.[btnIdx] !== undefined) {
          block.buttons[btnIdx].targetStepId = toStepId
          block.buttons[btnIdx].action = 'flow'
        }
      }
    }
    
    // IMPORTANTE: Recalcular order_index imediatamente ao conectar blocos
    console.log('🔗 Conexão criada! Recalculando order_index...')
    recalculateOrderIndex()
    
    // Auto-salvar após criar conexão
    autoSave()
  }
  
  cancelConnection()
  updateConnectionPaths()
}

const cancelConnection = () => {
  isDraggingConnection.value = false
  connectionFrom.value = null
  document.removeEventListener('mousemove', handleConnectionDragMove)
  document.removeEventListener('mouseup', cancelConnection)
}

// ==================== BUTTON PORT SYNC ====================

// Sincroniza conexão visual com btn.targetStepId
// Use targetStepId = '' para remover a conexão
const syncBtnConnection = (step, block, btnIdx, targetStepId) => {
  if (!step || !block) return
  const outputId = `btn-${block.id}-${btnIdx}`
  // Remove any existing connection from this button port
  connections.value = connections.value.filter(c =>
    !(c.from === step.id && c.outputId === outputId)
  )
  // Create new connection if a target is set
  if (targetStepId) {
    connections.value.push({
      id: `${step.id}-${outputId}-${targetStepId}`,
      from: step.id,
      to: targetStepId,
      outputId: outputId
    })
  }
  updateConnectionPaths()
}

// Called when user toggles btn action back to 'url'
const onBtnActionToUrl = (btn, btnIdx) => {
  const step = selectedStep.value
  const block = currentBlock.value
  btn.targetStepId = ''
  if (step && block) {
    syncBtnConnection(step, block, btnIdx, '')
  }
}

// Calcula a posição vertical do port de botão dentro do node
const getBtnPortStyle = (step, block, btn) => {
  if (!step.config?.blocks) return { top: '70%', right: '-10px' }
  
  const blocks = step.config.blocks
  // Cabeçalho do node (~52px) + cada sub-bloco (~44px estimado)
  const HEADER_H = 52
  const BLOCK_H = 44

  let blockOffset = 0
  for (const b of blocks) {
    if (b.id === block.id) break
    blockOffset++
  }

  // Dentro do bloco de botões, cada botão tem ~28px de altura
  const BTN_ROW_H = 28
  // Texto acima dos botões (~30px)
  const TEXT_ABOVE = 30
  // Encontrar índice do btn dentro dos botões que têm action=flow
  const flowBtns = (block.buttons || []).filter(b => b.action === 'flow')
  const btnFlowIdx = flowBtns.indexOf(btn)

  // Offset estimado em px a partir do topo do node
  const totalOffset = HEADER_H + blockOffset * BLOCK_H + TEXT_ABOVE + btnFlowIdx * BTN_ROW_H + 14
  
  return {
    top: `${totalOffset}px`,
    right: '-10px',
    transform: 'translateY(-50%)',
    bottom: 'auto'
  }
}

const removeConnection = async (connId) => {
  try {
    await confirmDialog.showConfirm({
      title: 'Remover conexão',
      message: 'Deseja remover esta conexão entre os blocos?',
      confirmText: 'Remover',
      cancelText: 'Cancelar',
      type: 'warning'
    })
  } catch {
    return // Usuário cancelou
  }

  // Encontrar conexão antes de remover para sincronizar targetStepId
  const removedConn = connections.value.find(c => c.id === connId)
  connections.value = connections.value.filter(c => c.id !== connId)

  // Se era porta de botão, limpar btn.targetStepId
  if (removedConn?.outputId?.startsWith('btn-')) {
    const oid = removedConn.outputId
    const lastDash = oid.lastIndexOf('-')
    const btnIdx = parseInt(oid.substring(lastDash + 1))
    const blockId = oid.substring(4, lastDash)
    const fromStep = steps.value.find(s => s.id === removedConn.from)
    if (fromStep?.config?.blocks) {
      const block = fromStep.config.blocks.find(b => b.id === blockId)
      if (block?.buttons?.[btnIdx] !== undefined) {
        block.buttons[btnIdx].targetStepId = ''
      }
    }
  }

  updateConnectionPaths()
  
  // IMPORTANTE: Recalcular order_index ao remover conexão
  console.log('🔗 Conexão removida! Recalculando order_index...')
  recalculateOrderIndex()
  
  // Auto-salvar após remover conexão
  autoSave()
}

// ==================== SVG PATHS ====================
const updateConnectionPaths = () => {
  if (!containerRef.value) return
  if (isPageLoading.value) return
  
  connectionPaths.value = connections.value.map(conn => {
    const fromPoint = getPortCenterWorkspace(conn.from, 'out', conn.outputId || 'default')
    const toPoint = getPortCenterWorkspace(conn.to, 'in')
    
    if (!fromPoint || !toPoint) return null
    
    // Calcular direção e ajustar ponto final para dar espaço à seta
    const dx = toPoint.x - fromPoint.x
    const dy = toPoint.y - fromPoint.y
    const distance = Math.sqrt(dx * dx + dy * dy)
    
    // Deslocamento para dar espaço à seta no final
    const offsetEnd = 15   // espaço para a seta
    
    const startX = fromPoint.x
    const startY = fromPoint.y
    const endX = toPoint.x - (dx / distance) * offsetEnd
    const endY = toPoint.y - (dy / distance) * offsetEnd
    
    const controlOffset = Math.abs(dx) * 0.5
    const path = `M ${startX} ${startY} C ${startX + controlOffset} ${startY}, ${endX - controlOffset} ${endY}, ${endX} ${endY}`
    
    return { id: conn.id, path }
  }).filter(Boolean)
}

const tempConnectionPath = computed(() => {
  if (!isDraggingConnection.value || !connectionFrom.value) return ''
  
  const fromPos = getPortCenterWorkspace(connectionFrom.value.stepId, 'out', connectionFrom.value.outputId)
  if (!fromPos) return ''
  
  const container = containerRef.value
  if (!container) return ''
  
  const rect = container.getBoundingClientRect()
  
  const x1 = fromPos.x
  const y1 = fromPos.y
  
  // Ponto do mouse ajustado para a transformação do canvas
  const x2 = (tempConnectionEnd.value.x - rect.left - canvasOffset.value.x) / canvasScale.value
  const y2 = (tempConnectionEnd.value.y - rect.top - canvasOffset.value.y) / canvasScale.value
  
  const dx = x2 - x1
  const controlOffset = Math.abs(dx) * 0.5
  
  return `M ${x1} ${y1} C ${x1 + controlOffset} ${y1}, ${x2 - controlOffset} ${y2}, ${x2} ${y2}`
})

// ==================== HELPERS ====================
const getStepIcon = (type) => {
  const icons = {
    message: 'fa-solid fa-message',
    image: 'fa-solid fa-image',
    wait: 'fa-solid fa-clock',
    data: 'fa-solid fa-database',
    trigger: 'fa-solid fa-bolt',
    action: 'fa-solid fa-bolt'
  }
  return icons[type] || 'fa-solid fa-rectangle-list'
}

const formatTrigger = (type) => {
  const mapping = {
    message: 'Mensagem',
    wait: 'Espera',
    image: 'Imagem',
    data: 'Coleta de Dados',
    trigger: 'Gatilho'
  }
  return mapping[type] || type
}

const renderStepTitle = (step) => {
  if (step.type === 'trigger') {
    if (step.config?.triggerType === 'message') return 'O usuário envia uma mensagem'
    if (step.config?.triggerType === 'ref_url') return 'Usuário clica em um link de referência'
    return 'Gatilho'
  }
  if (step.type === 'action') {
    const actions = step.config?.actions || []
    if (actions.length === 0) return 'Ações'
    if (actions.length === 1) {
      return getActionLabel(actions[0].type)
    }
    return `${actions.length} Ações`
  }
  return step.config?.text || step.name || 'Sem título'
}

const getStepLabelById = (targetStepId) => {
  if (!targetStepId) return ''
  const targetIdStr = String(targetStepId)
  const step = steps.value.find(s => String(s.id) === targetIdStr)
  if (!step) return `Bloco ${targetIdStr}`
  const title = renderStepTitle(step)
  return title || `${step.type} #${targetIdStr.slice(-4)}`
}

const getActionLabel = (actionType) => {
  const labels = {
    set_field: 'Definir Campo Personalizado',
    add_tag: 'Adicionar Tag',
    remove_tag: 'Remover Tag',
    start_sequence: 'Iniciar Sequência',
    stop_sequence: 'Parar Sequência',
    go_to_flow: 'Ir para Fluxo',
    go_to_step: 'Ir para Passo',
    smart_delay: 'Atraso Inteligente',
    webhook: 'Requisição Externa / Webhook',
    notify_admin: 'Notificar Admin / Inbox'
  }
  return labels[actionType] || 'Ação'
}

const renderStepSubtitle = (step) => {
  if (step.type === 'trigger') {
    if (step.config?.triggerType === 'message') {
      const keywords = step.config?.keywords || []
      if (keywords.length === 0) return 'Detectar mensagem de texto'
      return `Palavras-chave: ${keywords.join(', ')}`
    }
    if (step.config?.triggerType === 'telegram_ref_url') {
      const refKey = step.config?.ref_key || ''
      return refKey ? `Chave: ${refKey}` : 'Configure a chave de referência'
    }
  }
  if (step.type === 'action') {
    const actions = step.config?.actions || []
    if (actions.length === 0) return 'Nenhuma ação configurada'
    
    // Se tiver apenas uma ação do tipo add_tag ou remove_tag, mostrar as tags
    if (actions.length === 1 && (actions[0].type === 'add_tag' || actions[0].type === 'remove_tag')) {
      const action = actions[0]
      const tagName = action.tag_name || ''
      if (tagName) {
        const actionLabel = action.type === 'add_tag' ? 'Adicionar Tag' : 'Remover Tag'
        return `${actionLabel}: <span style="padding: 2px 8px; background: rgba(99, 102, 241, 0.1); border-radius: 4px; font-weight: 600; color: #6366f1; font-size: 0.75rem;">${tagName}</span>`
      }
    }
    
    const actionTypes = actions.map(a => getActionLabel(a.type))
    return actionTypes.join(', ')
  }
  return formatTrigger(step.type)
}

const isTriggerStep = (step) => {
  return step?.type === 'trigger'
}

const currentBlock = computed(() => {
  if (!selectedBlock.value) return null
  if (!selectedStep.value || selectedStep.value.id !== selectedBlock.value.stepId) return null
  const blocks = selectedStep.value.config?.blocks || []
  return blocks.find((b) => b.id === selectedBlock.value.blockId) || null
})

const addTrigger = async (kind) => {
  if (hasTrigger.value) {
    toast.warning('Já existe um gatilho neste fluxo')
    showTriggerModal.value = false
    return
  }

  const typeMap = {
    telegram_message: 'trigger',
    telegram_referral: 'trigger'
  }

  const type = typeMap[kind] || 'trigger'
  const config = kind === 'telegram_message'
    ? { triggerType: 'message', keywords: [] }
    : { triggerType: 'telegram_ref_url', ref_key: '', save_ref_field: '' }

  try {
    const orderIndex = steps.value.length + 1
    const newStep = await createFlowStep(flowId.value, {
      type,
      order_index: orderIndex,
      config
    })

    nodePositions.value[newStep.id] = { x: 80, y: 120 }
    steps.value.push(newStep)
    selectedStep.value = newStep
    updateConnectionPaths()
    autoSave()
  } catch (error) {
    console.error('Erro ao criar gatilho:', error)
  } finally {
    showTriggerModal.value = false
  }
}

const keywordInput = ref('')
const insertTag = (tagValue) => {
  if (!currentBlock.value || !contentTextareaRef.value) return

  const textarea = contentTextareaRef.value
  const original = currentBlock.value.text || ''
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const updated = `${original.slice(0, start)}${tagValue}${original.slice(end)}`
  currentBlock.value.text = updated

  nextTick(() => {
    const ta = contentTextareaRef.value
    if (ta) {
      const cursorPosition = start + tagValue.length
      ta.focus()
      ta.setSelectionRange(cursorPosition, cursorPosition)
    }
  })

  autoSave()
}

const addKeyword = () => {
  if (!selectedStep.value || selectedStep.value.type !== 'trigger' || selectedStep.value.config.triggerType !== 'message') return
  const kw = (keywordInput.value || '').trim()
  if (!kw) return
  const list = selectedStep.value.config.keywords || []
  list.push(kw)
  selectedStep.value.config.keywords = list
  keywordInput.value = ''
  autoSave()
}

const removeKeyword = (idx) => {
  if (!selectedStep.value || selectedStep.value.type !== 'trigger' || selectedStep.value.config.triggerType !== 'message') return
  const list = selectedStep.value.config.keywords || []
  list.splice(idx, 1)
  selectedStep.value.config.keywords = list
  autoSave()
}

const copyReferralLink = () => {
  const link = selectedStep.value?.config?.ref || triggerDefaultLink.value
  navigator.clipboard.writeText(link)
  toast.success('URL copiada para área de transferência')
}

// Funções para link de referência do Telegram
const getTelegramRefUrl = (refKey) => {
  if (!refKey) return 'Configure a chave de referência primeiro'

  // botUsername.value é resolvido pelo loadData() a partir do canal vinculado ao fluxo.
  // Não fazemos lookup extra na channelsCache para evitar usar bot_username
  // desatualizado (antes de fetchBotUsername persistir o valor).
  const username = (botUsername.value || '').replace('@', '').trim()

  if (!username || username === 'seu_bot') {
    return 'Configure o username do bot nas configurações primeiro'
  }

  return `https://t.me/${username}?start=${refKey}`
}

const copyTelegramRefLink = (refKey) => {
  const link = getTelegramRefUrl(refKey)
  if (link.includes('Configure')) {
    toast.warning('Configure a chave de referência primeiro')
    return
  }
  navigator.clipboard.writeText(link)
  toast.success('Link copiado para área de transferência')
}

// Função auxiliar para selecionar todo o texto do input ao clicar
const selectAllText = (event) => {
  event.target.select()
}

// ==================== AÇÕES ====================
const addAction = () => {
  if (!selectedStep.value || selectedStep.value.type !== 'action') return
  
  if (!selectedStep.value.config) {
    selectedStep.value.config = { actions: [] }
  }
  if (!selectedStep.value.config.actions) {
    selectedStep.value.config.actions = []
  }
  
  const newAction = {
    id: uid(),
    type: 'set_field',
    field_name: '',
    field_value: ''
  }
  
  selectedStep.value.config.actions.push(newAction)
  autoSave()
}

const removeAction = (index) => {
  if (!selectedStep.value || selectedStep.value.type !== 'action') return
  if (!selectedStep.value.config?.actions) return
  
  selectedStep.value.config.actions.splice(index, 1)
  autoSave()
}

const onActionTypeChange = (action, index) => {
  // Limpar campos específicos do tipo anterior
  const oldType = action.type
  
  // Resetar campos baseado no novo tipo
  switch (action.type) {
    case 'set_field':
      action.field_name = action.field_name || ''
      action.field_value = action.field_value || ''
      break
    case 'add_tag':
    case 'remove_tag':
      action.tag_name = action.tag_name || ''
      break
    case 'start_sequence':
    case 'stop_sequence':
      action.sequence_name = action.sequence_name || ''
      break
    case 'go_to_flow':
      action.flow_id = action.flow_id || null
      break
    case 'go_to_step':
      action.step_id = action.step_id || null
      break
    case 'smart_delay':
      action.delay_value = action.delay_value || 1
      action.delay_unit = action.delay_unit || 'minutes'
      break
    case 'webhook':
      action.webhook_url = action.webhook_url || ''
      action.method = action.method || 'POST'
      action.headers = action.headers || ''
      break
    case 'notify_admin':
      action.notification_message = action.notification_message || ''
      action.notify_tag = action.notify_tag || ''
      break
  }
  
  autoSave()
}

// ==================== LIFECYCLE ====================
onMounted(() => {
  loadData()
  
  // Fechar tooltip ao clicar fora
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.info-icon')) {
      closeTooltip()
    }
  })
})

// Watch para recarregar quando mudar o ID da rota
watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    console.log('🔄 Mudando de fluxo, recarregando dados...')
    loadData()
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', closeTooltip)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousemove', handleNodeDragMove)
  document.removeEventListener('mouseup', endNodeDrag)
  document.removeEventListener('mousemove', handleConnectionDragMove)
  document.removeEventListener('mouseup', cancelConnection)
})
</script>

<style scoped>

/* ===================== FLOW EDITOR LOADER ===================== */

/* Shimmer keyframe */
@keyframes fe-shimmer {
  0%   { background-position: -600px 0; }
  100% { background-position:  600px 0; }
}
@keyframes fe-pulse {
  0%, 100% { opacity: 0.55; }
  50%       { opacity: 1; }
}
@keyframes fe-spin {
  to { transform: rotate(360deg); }
}

/* Transition */
.fe-loader-enter-active { transition: opacity 0.3s ease; }
.fe-loader-leave-active { transition: opacity 0.4s ease; }
.fe-loader-enter-from,
.fe-loader-leave-to    { opacity: 0; }

/* Outer wrapper */
.fe-loader {
  position: fixed;
  inset: 0;
  z-index: 900;
  background: var(--bg, #060606);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header skeleton */
.fe-loader-header {
  padding: 20px 24px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  background: rgba(10, 12, 16, 0.9);
  flex-shrink: 0;
}

.fe-loader-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Shimmer base */
.fe-sk {
  border-radius: 6px;
  background: linear-gradient(
    90deg,
    rgba(255,255,255,0.05) 25%,
    rgba(255,255,255,0.11) 50%,
    rgba(255,255,255,0.05) 75%
  );
  background-size: 600px 100%;
  animation: fe-shimmer 1.6s infinite linear;
}

.fe-sk-chip      { height: 20px; border-radius: 20px; }
.fe-sk-title     { height: 28px; border-radius: 8px; }
.fe-sk-text      { height: 14px; border-radius: 6px; }
.fe-sk-btn       { height: 36px; border-radius: 8px; }
.fe-sk-btn-primary {
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(
    90deg,
    rgba(0,255,102,0.18) 25%,
    rgba(0,255,102,0.32) 50%,
    rgba(0,255,102,0.18) 75%
  );
  background-size: 600px 100%;
  animation: fe-shimmer 1.6s infinite linear;
}
.fe-sk-node-icon  { width: 38px; height: 38px; border-radius: 10px; flex-shrink: 0; animation: fe-shimmer 1.6s infinite linear; background-size: 600px 100%; }
.fe-sk-node-title { height: 13px; border-radius: 5px; margin-bottom: 8px; }
.fe-sk-node-text  { height: 11px; border-radius: 5px; }

/* Canvas area */
.fe-loader-canvas {
  flex: 1;
  position: relative;
  overflow: hidden;
}

/* Grid dots background */
.fe-loader-grid {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, rgba(255,255,255,0.07) 1px, transparent 1px);
  background-size: 28px 28px;
}

/* Fake nodes container */
.fe-loader-nodes {
  position: absolute;
  inset: 0;
}

/* Node header skeleton */
.fe-loader-node {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px 12px 0 0;
  border-bottom: none;
  animation: fe-pulse 2s ease-in-out infinite;
}

/* Node body skeleton */
.fe-loader-node-body {
  position: absolute;
  background: rgba(255,255,255,0.025);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 0 0 12px 12px;
  animation: fe-pulse 2s ease-in-out infinite;
}

/* Center spinner */
.fe-loader-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 18px;
  background: radial-gradient(ellipse at center, rgba(0,0,0,0.55) 0%, transparent 70%);
}

.fe-loader-ring {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: 3px solid rgba(0,255,102,0.15);
  border-top-color: #00FF66;
  animation: fe-spin 0.9s linear infinite;
  box-shadow: 0 0 20px rgba(0,255,102,0.25);
}

.fe-loader-ring-inner {
  display: none;
}

.fe-loader-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255,255,255,0.45);
  letter-spacing: 0.3px;
  margin: 0;
}

/* ===================== FLOW CANVAS CONTAINER ===================== */
.flow-canvas-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 0;
  background: 
    linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px),
    linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px);
  background-size: 20px 20px;
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: grab;
  user-select: none;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.flow-canvas-container:active {
  cursor: grabbing;
}

.flow-canvas-workspace {
  position: relative;
  width: 100%;
  height: 100%;
  will-change: transform;
  /* Sem transition — pan deve ser 1:1 com o mouse, zero latência */
}

.flow-connections-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: visible;
  z-index: 10;
}

.connection-line {
  fill: none;
  stroke: rgba(34, 197, 94, 0.8);
  stroke-width: 3;
  stroke-linecap: round;
  filter: drop-shadow(0 0 4px rgba(34, 197, 94, 0.4));
  pointer-events: stroke;
  cursor: pointer;
  transition: stroke 0.2s, stroke-width 0.2s;
}

.connection-line:hover {
  stroke: rgba(239, 68, 68, 0.9);
  stroke-width: 4;
}

.connection-line-animated {
  stroke-dasharray: 8, 4;
  animation: flowAnimation 1s linear infinite;
}

.connection-line-temp {
  stroke: rgba(34, 197, 94, 0.5);
  stroke-dasharray: 5, 5;
  animation: dashAnimation 0.5s linear infinite;
  pointer-events: none;
}

@keyframes flowAnimation {
  to {
    stroke-dashoffset: -12;
  }
}

@keyframes dashAnimation {
  to {
    stroke-dashoffset: -10;
  }
}

/* ===================== BOTÃO CIRCULAR ADICIONAR BLOCO ===================== */
.btn-add-block-circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 10;
}

.btn-add-block-circle:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.btn-add-block-circle:active {
  transform: scale(0.95);
}

.btn-add-block-circle svg {
  stroke: white;
}

/* ===================== MODAL ADICIONAR BLOCO (ABM) ===================== */

.abm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.72);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.abm {
  background: #0d1117;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 20px;
  box-shadow:
    0 32px 96px rgba(0, 0, 0, 0.65),
    0 0 0 1px rgba(0, 255, 102, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  width: 100%;
  max-width: 840px;
  max-height: 86vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.abm-header {
  padding: 20px 22px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  flex-shrink: 0;
}

.abm-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.abm-title {
  font-size: 1.0625rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 9px;
}

.abm-title-icon {
  color: var(--primary);
  font-size: 0.95rem;
}

.abm-close {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: 1.5px solid rgba(239, 68, 68, 0.35);
  background: rgba(239, 68, 68, 0.09);
  color: #ef4444;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9375rem;
  transition: all 0.18s;
  flex-shrink: 0;
}

.abm-close:hover {
  background: #ef4444;
  border-color: #ef4444;
  color: white;
  transform: scale(1.06);
  box-shadow: 0 4px 14px rgba(239, 68, 68, 0.4);
}

/* Search */
.abm-search-wrap {
  position: relative;
  padding-bottom: 16px;
}

.abm-search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-60%);
  color: var(--muted);
  font-size: 0.8125rem;
  pointer-events: none;
}

.abm-search {
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 10px;
  padding: 9px 36px 9px 34px;
  color: var(--text-primary);
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.abm-search:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(0, 255, 102, 0.1);
}

.abm-search::placeholder {
  color: var(--muted);
}

.abm-search-clear {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-60%);
  width: 20px;
  height: 20px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  color: var(--muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.675rem;
  transition: all 0.15s;
}

.abm-search-clear:hover {
  background: rgba(255, 255, 255, 0.2);
  color: var(--text-primary);
}

/* Body: 2 columns */
.abm-body {
  display: flex;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

/* Left nav */
.abm-nav {
  width: 168px;
  flex-shrink: 0;
  border-right: 1px solid rgba(255, 255, 255, 0.07);
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  overflow-y: auto;
}

.abm-nav-item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 9px 11px;
  border-radius: 9px;
  border: 1px solid transparent;
  background: transparent;
  color: rgba(148, 163, 184, 0.8);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.16s;
  text-align: left;
  white-space: nowrap;
  width: 100%;
}

.abm-nav-icon {
  font-size: 0.8125rem;
  width: 15px;
  text-align: center;
  flex-shrink: 0;
}

.abm-nav-count {
  margin-left: auto;
  font-size: 0.6875rem;
  background: rgba(255, 255, 255, 0.07);
  border-radius: 10px;
  padding: 1px 7px;
  color: var(--muted);
}

.abm-nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.abm-nav-item.active {
  background: rgba(0, 255, 102, 0.09);
  color: var(--primary);
  border-color: rgba(0, 255, 102, 0.2);
}

.abm-nav-item.active .abm-nav-count {
  background: rgba(0, 255, 102, 0.15);
  color: var(--primary);
}

/* Right blocks panel */
.abm-blocks {
  flex: 1;
  overflow-y: auto;
  padding: 16px 18px;
  min-width: 0;
}

.abm-group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.abm-group-icon {
  color: var(--primary);
  font-size: 0.875rem;
}

.abm-group-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--text-primary);
}

.abm-group-desc {
  font-size: 0.8rem;
  color: var(--muted);
  margin-left: 2px;
}

.abm-group-search-label {
  font-size: 0.6875rem;
  font-weight: 700;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.abm-blocks-group {
  margin-bottom: 20px;
}

.abm-blocks-group:last-child {
  margin-bottom: 0;
}

.abm-cards {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* Block card */
.abm-card {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.16s;
  text-align: left;
  position: relative;
  width: 100%;
}

.abm-card:hover {
  background: rgba(255, 255, 255, 0.065);
  border-color: rgba(255, 255, 255, 0.14);
  transform: translateX(3px);
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.22);
}

.abm-card-accent {
  border-color: rgba(0, 255, 102, 0.18);
  background: rgba(0, 255, 102, 0.04);
}

.abm-card-accent:hover {
  border-color: rgba(0, 255, 102, 0.35);
  background: rgba(0, 255, 102, 0.08);
  box-shadow: 0 4px 20px rgba(0, 255, 102, 0.1);
}

.abm-card-icon {
  width: 44px;
  height: 44px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.075rem;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.abm-card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.abm-card-header {
  display: flex;
  align-items: center;
  gap: 7px;
  flex-wrap: wrap;
}

.abm-card-label {
  font-size: 0.8875rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.2;
}

.abm-card-desc {
  font-size: 0.775rem;
  color: var(--muted);
  line-height: 1.45;
}

.abm-card-chevron {
  color: rgba(148, 163, 184, 0.3);
  font-size: 0.75rem;
  flex-shrink: 0;
  transition: all 0.16s;
}

.abm-card:hover .abm-card-chevron {
  color: rgba(148, 163, 184, 0.7);
  transform: translateX(2px);
}

/* Badges */
.abm-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 7px;
  border-radius: 4px;
  font-size: 0.595rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

.abm-badge-pro {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.abm-badge-ai {
  background: #111;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.abm-badge-new {
  background: linear-gradient(135deg, #00FF66, #00cc52);
  color: #000;
}

/* Empty state */
.abm-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 48px 20px;
  text-align: center;
  color: var(--muted);
}

.abm-empty-icon {
  font-size: 1.75rem;
  opacity: 0.4;
}

.abm-empty p {
  font-size: 0.875rem;
  margin: 0;
}

/* Mobile */
@media (max-width: 640px) {
  .abm {
    max-height: 92vh;
    border-radius: 16px 16px 0 0;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    max-width: 100%;
  }
  .abm-nav {
    width: 110px;
    padding: 10px 6px;
  }
  .abm-nav-count {
    display: none;
  }
  .abm-group-desc {
    display: none;
  }
}



/* ===================== EDITOR DE AÇÕES ===================== */
.actions-editor {
  width: 100%;
  min-width: 0;
  overflow: visible;
  box-sizing: border-box;
}

.actions-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  min-width: 0;
  gap: 8px;
}

.btn-add-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 6px;
  color: var(--accent);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-add-action:hover {
  background: rgba(59, 130, 246, 0.25);
  border-color: rgba(59, 130, 246, 0.5);
}

.actions-empty {
  padding: 24px;
  text-align: center;
  color: var(--muted);
  font-size: 0.875rem;
  background: rgba(15, 23, 42, 0.3);
  border-radius: 8px;
  border: 1px dashed rgba(148, 163, 184, 0.2);
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-item {
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 10px;
  padding: 14px;
  transition: all 0.2s;
  min-width: 0;
  overflow: visible;
  box-sizing: border-box;
}

.action-item:hover {
  border-color: rgba(148, 163, 184, 0.3);
  background: rgba(15, 23, 42, 0.5);
}

.action-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  min-width: 0;
  overflow: visible;
}

.action-type-select {
  flex: 1;
  padding: 6px 10px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 0;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.action-type-select:focus {
  outline: none;
  border-color: var(--accent);
  background: rgba(15, 23, 42, 0.8);
}

.btn-remove-action {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  color: #ef4444;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.btn-remove-action:hover {
  background: rgba(239, 68, 68, 0.25);
  border-color: rgba(239, 68, 68, 0.5);
  transform: scale(1.05);
}

.action-config {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
  overflow: visible;
}

.action-config .form-group {
  margin-bottom: 0;
  min-width: 0;
  overflow: visible;
}

.sidebar-label {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
  position: relative;
  z-index: 1;
}

.sidebar-hint {
  margin-top: 6px;
  margin-bottom: 10px;
  font-size: 0.78rem;
  line-height: 1.25;
  color: rgba(148, 163, 184, 0.9);
}

.sidebar-footer-toolbar {
  flex-shrink: 0;
  padding: 10px;
  border-top: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(15, 23, 42, 0.92);
  position: relative;
}

.text-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(2, 6, 23, 0.55);
  backdrop-filter: blur(10px);
}

.text-toolbar.disabled {
  opacity: 0.55;
}

.text-toolbar-btn {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(59, 130, 246, 0.06);
  color: rgba(226, 232, 240, 0.92);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.15s ease, background 0.15s ease, border-color 0.15s ease;
}

.text-toolbar-btn:disabled {
  cursor: not-allowed;
}

.text-toolbar-btn:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.12);
  border-color: rgba(59, 130, 246, 0.35);
  transform: translateY(-1px);
}

.text-toolbar-sep {
  width: 1px;
  height: 22px;
  background: rgba(148, 163, 184, 0.18);
  margin: 0 2px;
}

.emoji-popover {
  position: absolute;
  right: 10px;
  bottom: 56px;
  width: 260px;
  padding: 10px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(2, 6, 23, 0.96);
  box-shadow: 0 10px 30px rgba(0,0,0,0.35);
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 6px;
  z-index: 10002;
}

.emoji-btn {
  height: 28px;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  background: rgba(59, 130, 246, 0.06);
  cursor: pointer;
  font-size: 16px;
}

.emoji-btn:hover {
  background: rgba(59, 130, 246, 0.12);
  border-color: rgba(59, 130, 246, 0.35);
}

.info-icon {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  color: rgba(59, 130, 246, 0.8);
  cursor: help;
  transition: all 0.2s;
  flex-shrink: 0;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.1);
  z-index: 10001;
}

.info-icon:hover {
  color: var(--accent);
  background: rgba(59, 130, 246, 0.2);
  transform: scale(1.1);
}

.info-icon i {
  font-size: 0.75rem;
}

/* Tooltip customizado */
.tooltip-text {
  position: fixed;
  bottom: auto;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 16px;
  background: rgba(15, 23, 42, 0.98);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.8125rem;
  font-weight: 400;
  white-space: normal;
  z-index: 999999;
  max-width: 320px;
  min-width: 260px;
  text-align: left;
  line-height: 1.6;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  pointer-events: auto;
  animation: tooltipFadeIn 0.15s ease-out forwards;
}

@keyframes tooltipFadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.tooltip-text strong {
  color: rgba(59, 130, 246, 1);
  display: block;
  margin-bottom: 4px;
}

.tooltip-text code {
  background: rgba(59, 130, 246, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  color: rgba(96, 165, 250, 1);
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
}

.tooltip-text em {
  color: rgba(148, 163, 184, 0.8);
  font-style: italic;
  font-size: 0.75rem;
  display: block;
  margin-top: 8px;
}

.tooltip-text br + br {
  display: block;
  content: "";
  margin: 8px 0;
}

.tooltip-text::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 8px solid transparent;
  border-top-color: rgba(15, 23, 42, 0.98);
}

.info-icon.tooltip-active {
  background: rgba(59, 130, 246, 0.3);
  color: var(--accent);
  z-index: 10002;
}

.sidebar-textarea,
.action-type-select,
.action-config input[type="text"],
.action-config input[type="number"],
.action-config select,
.action-config textarea {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  word-wrap: break-word;
  overflow-wrap: break-word;
  min-width: 0;
  overflow: hidden;
}

.action-config input[type="text"],
.action-config input[type="number"],
.action-config select {
  padding: 6px 10px;
  height: 32px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 0.8125rem;
  font-family: inherit;
  transition: all 0.2s;
}

.action-config input[type="text"]:focus,
.action-config input[type="number"]:focus,
.action-config select:focus {
  outline: none;
  border-color: var(--accent);
  background: rgba(15, 23, 42, 0.8);
}

.flow-empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: var(--muted);
  pointer-events: none;
}

.flow-empty-state .empty-state-icon {
  width: 56px;
  height: 56px;
  margin-bottom: 16px;
  opacity: 0.5;
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
}

.flow-empty-state h3 {
  margin: 0 0 8px;
  font-size: 1.2rem;
  color: var(--text);
}

.flow-node {
  position: absolute;
  width: 300px;
  min-height: 120px;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border: 2px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  cursor: move;
  transition: box-shadow 0.2s, border-color 0.2s;
  z-index: 5;
}

/* Cores específicas por tipo de node */
.flow-node.node-type-trigger {
  border-color: #10b981;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.1) 100%);
}

.flow-node.node-type-trigger:hover {
  border-color: #10b981;
  box-shadow: 0 8px 30px rgba(16, 185, 129, 0.3);
}

.flow-node.node-type-message {
  border-color: #3b82f6;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.1) 100%);
}

.flow-node.node-type-message:hover {
  border-color: #3b82f6;
  box-shadow: 0 8px 30px rgba(59, 130, 246, 0.3);
}

.flow-node.node-type-action {
  border-color: #a855f7;
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.15) 0%, rgba(147, 51, 234, 0.1) 100%);
}

.flow-node.node-type-action:hover {
  border-color: #a855f7;
  box-shadow: 0 8px 30px rgba(168, 85, 247, 0.3);
}

.flow-node.node-type-condition {
  border-color: #f59e0b;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.1) 100%);
}

.flow-node.node-type-condition:hover {
  border-color: #f59e0b;
  box-shadow: 0 8px 30px rgba(245, 158, 11, 0.3);
}

.flow-node:hover {
  border-color: var(--accent);
  box-shadow: 0 8px 30px rgba(34, 197, 94, 0.2);
}

.flow-node.is-dragging {
  opacity: 0.9;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), 0 0 0 2px var(--primary);
  will-change: transform;
  transition: none;
  cursor: grabbing;
  z-index: 100;
}

/* Cores específicas para sub-blocos de mensagem */
.msg-block {
  position: relative;
  padding: 12px;
  padding-left: 36px;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.2s;
  border-left: 3px solid transparent;
  cursor: default;
}

.msg-block-drag-handle {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--muted);
  cursor: grab;
  opacity: 0;
  transition: opacity 0.2s;
  z-index: 10;
}

.msg-block:hover .msg-block-drag-handle {
  opacity: 1;
}

.msg-block-drag-handle:hover {
  color: var(--text);
}

.msg-block-drag-handle:active {
  cursor: grabbing;
}

.msg-block.is-dragging-block {
  opacity: 0.3;
  transform: scale(0.95);
  cursor: grabbing;
  filter: blur(1px);
  border-style: dashed;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.2;
  }
}

.msg-block.drag-over {
  border-top: 3px solid var(--primary);
  padding-top: 15px;
  background: rgba(59, 130, 246, 0.1);
  animation: dragOverPulse 0.5s ease-in-out;
}

@keyframes dragOverPulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
  100% {
    transform: scale(1);
  }
}

/* Elemento Ghost durante drag */
.msg-block-ghost {
  opacity: 0.9;
  transform: rotate(3deg) scale(1.05);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4), 0 0 20px rgba(59, 130, 246, 0.4);
  cursor: grabbing;
  animation: ghostFloat 0.3s ease-in-out infinite alternate;
  border: 2px solid var(--primary);
}

@keyframes ghostFloat {
  0% {
    transform: rotate(3deg) scale(1.05) translateY(0);
  }
  100% {
    transform: rotate(3deg) scale(1.05) translateY(-3px);
  }
}

.msg-block-text {
  border-left-color: #3b82f6;
  background: rgba(59, 130, 246, 0.08);
}

.msg-block-text:hover {
  background: rgba(59, 130, 246, 0.12);
  border-left-color: #2563eb;
}

.msg-block-delay {
  border-left-color: #f59e0b;
  background: rgba(245, 158, 11, 0.08);
  display: flex;
  align-items: center;
  gap: 8px;
}

.msg-block-delay:hover {
  background: rgba(245, 158, 11, 0.12);
  border-left-color: #d97706;
}

.msg-block-image {
  border-left-color: #ec4899;
  background: rgba(236, 72, 153, 0.08);
}

.msg-block-image:hover {
  background: rgba(236, 72, 153, 0.12);
  border-left-color: #db2777;
}

.msg-block-audio {
  border-left-color: #8b5cf6;
  background: rgba(139, 92, 246, 0.08);
}

.msg-block-audio:hover {
  background: rgba(139, 92, 246, 0.12);
  border-left-color: #7c3aed;
}

.msg-block-video {
  border-left-color: #ef4444;
  background: rgba(239, 68, 68, 0.08);
}

.msg-block-video:hover {
  background: rgba(239, 68, 68, 0.12);
  border-left-color: #dc2626;
}

.msg-block-button {
  border-left-color: #10b981;
  background: rgba(16, 185, 129, 0.08);
}

.msg-block-button:hover {
  background: rgba(16, 185, 129, 0.12);
  border-left-color: #059669;
}

.flow-node-content {
  padding: 16px;
  pointer-events: none;
}

.flow-node-header-simple {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.flow-node-icon {
  font-size: 1.5rem;
}

.flow-node-title {
  flex: 1;
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text);
}

.btn-node-delete {
  background: transparent;
  border: none;
  color: var(--muted);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
  pointer-events: auto;
  transition: all 0.2s;
}

.btn-node-delete:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.flow-node-body-simple {
  pointer-events: none;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(8px);
}

.modal-content {
  position: relative;
  width: min(960px, 92vw);
  background: radial-gradient(circle at top right, rgba(59, 130, 246, 0.15), transparent 45%),
    #0b1224;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 28px;
  box-shadow: 0 20px 60px rgba(2, 6, 23, 0.8);
  padding: 40px;
  overflow: hidden;
}

.modal-header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.modal-close {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: none;
  background: rgba(239, 68, 68, 0.15);
  border: 1.5px solid rgba(239, 68, 68, 0.4);
  color: #ef4444;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
  font-weight: 600;
  z-index: 10;
  transition: all 0.2s;
  flex-shrink: 0;
}

.modal-close:hover {
  background: #ef4444;
  border-color: #ef4444;
  color: white;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.5);
}

.modal-close:active {
  transform: scale(0.95);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.8rem;
  color: #e2e8f0;
}

.modal-body {
  margin-top: 24px;
}

.trigger-modal-body {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 24px;
  color: #cbd5f5;
}

.trigger-sidebar {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 18px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.trigger-nav-item {
  padding: 10px 12px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  border: 1px solid transparent;
  color: #94a3b8;
}

.trigger-nav-item.active {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.6);
  color: #bfdbfe;
}

.trigger-nav-item.disabled {
  opacity: 0.4;
}

.trigger-main {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 22px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.trigger-header h3 {
  margin: 0;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: #a5b4fc;
}

.trigger-header p {
  margin: 4px 0 0;
  color: #94a3b8;
  font-size: 0.9rem;
}

.trigger-card {
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 20px;
  padding: 18px;
  display: grid;
  grid-template-columns: 48px 1fr 32px;
  gap: 16px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s ease, transform 0.2s ease;
  background: rgba(30, 41, 59, 0.7);
}

.trigger-card:hover {
  border-color: rgba(132, 204, 22, 0.6);
  transform: translateY(-2px);
}

.trigger-card-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: rgba(14, 165, 233, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #38bdf8;
  font-size: 1.3rem;
}

.trigger-card-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.trigger-card-kicker {
  margin: 0;
  font-size: 0.75rem;
  color: #a5b4fc;
  text-transform: uppercase;
  letter-spacing: 0.2em;
}

.trigger-card-title {
  margin: 0;
  font-size: 1.1rem;
  color: #f8fafc;
  font-weight: 600;
}

.trigger-card-desc {
  margin: 0;
  color: #cbd5f5;
  font-size: 0.9rem;
}

.trigger-card-chevron {
  color: rgba(148, 163, 184, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-footer {
  margin-top: 22px;
  text-align: right;
}

.modal-footer .btn {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.5);
  color: #a5b4fc;
}

.tag-dropdown {
  margin-top: 12px;
}

.tag-dropdown-inline {
  margin-top: 6px;
  margin-bottom: 12px;
}

.tag-dropdown-toggle {
  width: 100%;
  border: 1px solid rgba(148, 163, 184, 0.6);
  background: rgba(15, 23, 42, 0.8);
  color: #e2e8f0;
  padding: 10px 12px;
  font-size: 0.8rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.tag-dropdown-toggle:hover {
  border-color: rgba(34, 197, 94, 0.8);
  background: rgba(15, 23, 42, 1);
}

.tag-dropdown-panel {
  margin-top: 8px;
  padding: 12px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: var(--radius-lg);
  background: rgba(15, 23, 42, 0.9);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.4);
}

.tag-dropdown-arrow {
  font-size: 0.8rem;
  transition: transform 0.2s;
}

.tag-dropdown-arrow.open {
  transform: rotate(-180deg);
}

.tag-picker {
  padding-top: 12px;
  border-top: 1px solid rgba(226, 232, 240, 0.4);
  margin-top: 12px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 6px;
}

.tag-chip {
  border: 1px solid rgba(148, 163, 184, 0.7);
  background: rgba(15, 23, 42, 0.6);
  color: #e2e8f0;
  padding: 6px 10px;
  font-size: 0.75rem;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-chip:hover {
  border-color: rgba(34, 197, 94, 0.8);
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
}

.flow-port {
  position: absolute;
  width: 20px;
  height: 20px;
  background: rgba(34, 197, 94, 0.2);
  border: 2px solid var(--accent);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 10;
}

.flow-port:hover {
  background: var(--accent);
  transform: translateY(-50%) scale(1.3);
  box-shadow: 0 0 15px rgba(34, 197, 94, 0.6);
}

.flow-port-dot {
  width: 8px;
  height: 8px;
  background: var(--accent);
  border-radius: 50%;
}

.flow-port-input {
  top: 30%;
  left: -10px;
  transform: translateY(-50%);
  opacity: 0;
  pointer-events: auto;
  transition: opacity 0.2s, transform 0.2s;
}

.flow-port-input.show-on-drag {
  opacity: 1;
  transform: translateY(-50%);
}

.flow-port-input:hover {
  opacity: 1;
  transform: translateY(-50%) scale(1.2);
}

.flow-port-output {
  bottom: 4px;
  top: auto;
  right: -10px;
  transform: none;
}

.flow-port-output:hover {
  transform: scale(1.3);
  background: var(--accent);
  box-shadow: 0 0 15px rgba(34, 197, 94, 0.6);
}

/* Múltiplas saídas - Condição */
.flow-port-condition-true {
  top: 35%;
  right: -10px;
  bottom: auto;
  transform: translateY(-50%);
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.flow-port-condition-false {
  top: 65%;
  right: -10px;
  bottom: auto;
  transform: translateY(-50%);
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

/* Múltiplas saídas - Randomizador */
.flow-port-randomizer {
  bottom: auto;
  right: -10px;
  background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%);
  transform: translateY(-50%);
}

.flow-port-randomizer:hover {
  transform: translateY(-50%) scale(1.3);
}

/* Port de saída por botão (inline, colado na borda direita do botão) */
.flow-port-btn-inline {
  position: absolute;
  right: -21px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  cursor: crosshair;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.6), 0 0 0 3px rgba(245, 158, 11, 0.15);
  transition: all 0.2s;
}

.flow-port-btn-inline:hover {
  transform: translateY(-50%) scale(1.35);
  box-shadow: 0 0 16px rgba(245, 158, 11, 1), 0 0 0 5px rgba(245, 158, 11, 0.2);
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
}

.flow-port-btn-inline .flow-port-dot {
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 0 3px rgba(255,255,255,0.8);
}

/* Botão no node com action=flow */
.msg-block-menu-btn-flow {
  background: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.45);
  border-right-color: rgba(245, 158, 11, 0.7);
  color: #fbbf24;
}

/* Toggle URL/Bloco no sidebar */
.btn-action-toggle {
  display: flex;
  gap: 2px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 6px;
  padding: 2px;
  margin-top: 4px;
}

.btn-toggle-opt {
  flex: 1;
  padding: 4px 8px;
  font-size: 0.75rem;
  font-weight: 500;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.btn-toggle-opt.active {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.btn-toggle-opt.active i {
  color: #60a5fa;
}

.btn-flow-hint {
  background: rgba(15, 23, 42, 0.35);
  border: 1px dashed rgba(148, 163, 184, 0.25);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 0.78rem;
  line-height: 1.2;
  padding: 6px 8px;
}

.btn-flow-connected {
  background: rgba(34, 197, 94, 0.08);
  border: 1px solid rgba(34, 197, 94, 0.22);
  border-radius: 6px;
  color: var(--text-primary);
  padding: 6px 8px;
}

.btn-flow-disconnected {
  opacity: 0.9;
}

/* Labels nas portas */
.flow-port-label {
  position: absolute;
  right: 28px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.75rem;
  font-weight: 700;
  color: white;
  background: rgba(0, 0, 0, 0.7);
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s;
}

.flow-port:hover .flow-port-label {
  opacity: 1;
}

.flow-canvas-controls {
  position: absolute;
  bottom: 16px;
  right: 16px;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: var(--shadow-lg);
}

.flow-control-btn {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text);
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.flow-control-btn:hover {
  background: var(--accent);
  border-color: var(--accent);
  color: #000;
}

.flow-control-zoom-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text);
  min-width: 50px;
  text-align: center;
}

.flow-canvas-hint-overlay {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--accent);
  color: #000;
  padding: 12px 20px;
  border-radius: var(--radius-lg);
  font-size: 0.9rem;
  font-weight: 600;
  box-shadow: var(--shadow-xl);
  animation: slideDown 0.3s ease-out;
  pointer-events: none;
}

/* Estilos para Link de Referência */
.ref-box {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  margin-top: 12px;
}

.ref-url-display-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  background: rgba(0, 255, 102, 0.05);
  border: 1.5px solid rgba(0, 255, 102, 0.3);
  border-radius: 8px;
  padding: 10px 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.ref-url-display-box:hover {
  border-color: #00FF66;
  background: rgba(0, 255, 102, 0.09);
}

.ref-url-display-inner {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.ref-url-icon {
  color: #00FF66;
  font-size: 1rem;
  flex-shrink: 0;
  margin-top: 2px;
}

.ref-url-text {
  font-size: 0.78rem;
  font-weight: 600;
  color: #00FF66;
  word-break: break-all;
  line-height: 1.5;
  letter-spacing: 0.01em;
}

.ref-url-copy-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-shrink: 0;
  background: #00FF66;
  color: #000;
  border: none;
  border-radius: 6px;
  padding: 6px 10px;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.ref-url-copy-btn:hover {
  background: #00cc52;
}

.ref-warning {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 6px;
  color: #f59e0b;
  font-size: 0.875rem;
  margin-top: 12px;
}

.ref-warning i {
  font-size: 1.125rem;
  flex-shrink: 0;
}

.success-tip {
  color: #10b981 !important;
  background: rgba(16, 185, 129, 0.1);
  padding: 10px 12px;
  border-radius: 6px;
  display: flex;
  align-items: start;
  gap: 8px;
  margin-top: 8px;
}

.success-tip i {
  margin-top: 2px;
  flex-shrink: 0;
}

.btn-primary.btn-sm {
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  padding: 8px 16px;
}

.btn-icon-only {
  padding: 10px !important;
  min-width: 44px;
  justify-content: center;
}

.btn-icon-only i {
  margin: 0 !important;
}

/* Info do Bot */
.bot-info-box {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(0, 136, 204, 0.1) 0%, rgba(34, 158, 217, 0.1) 100%);
  border: 1px solid rgba(0, 136, 204, 0.3);
  border-radius: 8px;
  margin-top: 12px;
  margin-bottom: 16px;
  color: #0088cc;
  font-size: 0.9375rem;
}

.bot-info-box i {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.bot-info-box strong {
  font-weight: 700;
  color: #0068aa;
}

.bot-warning-box {
  display: flex;
  align-items: start;
  gap: 12px;
  padding: 14px 16px;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 8px;
  margin-top: 12px;
  margin-bottom: 16px;
  color: #f59e0b;
  font-size: 0.875rem;
}

.bot-warning-box i {
  font-size: 1.25rem;
  flex-shrink: 0;
  margin-top: 2px;
}

.bot-warning-box strong {
  font-weight: 700;
  color: #d97706;
}

.bot-warning-box small {
  display: block;
  margin-top: 4px;
  opacity: 0.9;
}

/* Toggle de Tipo de Vídeo */
.video-type-toggle {
  display: flex;
  gap: 12px;
  padding: 8px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.video-type-toggle .toggle-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 6px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  font-weight: 600;
  background: var(--bg-primary);
}

.video-type-toggle .toggle-option input[type="radio"] {
  display: none;
}

.video-type-toggle .toggle-option:hover {
  border-color: var(--primary);
  background: rgba(99, 102, 241, 0.05);
}

.video-type-toggle .toggle-option.active {
  border-color: var(--primary);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  color: var(--primary);
}

.video-type-toggle .toggle-option i {
  font-size: 1.125rem;
}

/* Info sobre Vídeo Bolinha */
.video-note-info {
  display: flex;
  align-items: start;
  gap: 12px;
  padding: 12px 14px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 8px;
  color: #3b82f6;
  font-size: 0.8125rem;
  margin-bottom: 16px;
}

.video-note-info i {
  font-size: 1.125rem;
  flex-shrink: 0;
  margin-top: 2px;
}

.video-note-info strong {
  font-weight: 700;
  color: #2563eb;
}

.video-note-info ul {
  margin: 6px 0 0 0;
  padding-left: 20px;
  list-style: disc;
}

.video-note-info li {
  margin: 3px 0;
  line-height: 1.4;
}

/* ==================== CONDIÇÃO ==================== */
.condition-info {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  margin-top: 8px;
}

.condition-info i {
  color: #3b82f6;
  font-size: 1rem;
  flex-shrink: 0;
}

.condition-info div {
  flex: 1;
}

.condition-info strong {
  display: block;
  color: var(--text-primary);
  margin-bottom: 2px;
  font-size: 0.8125rem;
}

.condition-info p {
  color: var(--text-secondary);
  font-size: 0.8125rem;
  line-height: 1.4;
  margin: 2px 0;
}

/* ==================== RANDOMIZADOR ==================== */
.randomizer-paths {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 8px;
}

.randomizer-path-item {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  padding: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.path-header {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-bottom: 6px;
}

.path-name-input {
  flex: 1;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 5px 8px;
  color: var(--text-primary);
  font-size: 0.8125rem;
  height: 30px;
}

.btn-remove-path {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  padding: 5px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-remove-path:hover {
  background: rgba(239, 68, 68, 0.3);
}

.path-percentage {
  display: flex;
  align-items: center;
  gap: 8px;
}

.percentage-input {
  width: 80px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 8px 12px;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 600;
  text-align: center;
}

.percentage-label {
  color: var(--text-secondary);
  font-size: 1rem;
}

.btn-add-path {
  width: 100%;
  background: rgba(34, 197, 94, 0.1);
  border: 1px dashed rgba(34, 197, 94, 0.3);
  color: #22c55e;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-add-path:hover {
  background: rgba(34, 197, 94, 0.15);
  border-color: rgba(34, 197, 94, 0.5);
}

.randomizer-total {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(34, 197, 94, 0.1);
  border-radius: 8px;
  margin-top: 16px;
  color: #22c55e;
  font-size: 0.9375rem;
}

.randomizer-total strong {
  font-size: 1.125rem;
  font-weight: 700;
}

.randomizer-total.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.randomizer-total .error-msg {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8125rem;
}

.randomizer-info {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: rgba(168, 85, 247, 0.1);
  border-radius: 8px;
  margin-top: 8px;
}

.randomizer-info i {
  color: #a855f7;
  font-size: 1rem;
  flex-shrink: 0;
}

.randomizer-info div {
  flex: 1;
}

.randomizer-info strong {
  display: block;
  color: var(--text-primary);
  margin-bottom: 2px;
  font-size: 0.8125rem;
}

.randomizer-info p {
  color: var(--text-secondary);
  font-size: 0.8125rem;
  line-height: 1.4;
  margin: 2px 0;
}

/* ==================== ATRASO INTELIGENTE ==================== */
.smart-delay-info {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 8px;
  margin-top: 8px;
}

.smart-delay-info i {
  color: #ef4444;
  font-size: 1rem;
  flex-shrink: 0;
}

.smart-delay-info div {
  flex: 1;
}

.smart-delay-info strong {
  display: block;
  color: var(--text-primary);
  margin-bottom: 2px;
  font-size: 0.8125rem;
}

.smart-delay-info p {
  color: var(--text-secondary);
  font-size: 0.8125rem;
  line-height: 1.4;
  margin: 2px 0;
}

.delay-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: rgba(34, 197, 94, 0.1);
  border-radius: 8px;
  margin-top: 8px;
  color: #22c55e;
  font-size: 0.8125rem;
  font-weight: 500;
}

.delay-preview i {
  font-size: 1rem;
}

/* ==================== COMENTÁRIO ==================== */
.comment-color-picker {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.color-option {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.color-option:hover {
  transform: scale(1.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.color-option.active {
  border-color: rgba(255, 255, 255, 0.6);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

.comment-info {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 8px;
  margin-top: 16px;
}

.comment-info i {
  color: #f59e0b;
  font-size: 1.125rem;
  flex-shrink: 0;
}

.comment-info div {
  flex: 1;
}

.comment-info strong {
  display: block;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.comment-info p {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.4;
  margin: 4px 0;
}

/* ==================== INICIAR AUTOMAÇÃO ==================== */
.flow-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(34, 197, 94, 0.1);
  border-radius: 8px;
  margin-top: 16px;
  color: #22c55e;
  font-size: 0.9375rem;
}

.flow-preview i {
  font-size: 1.125rem;
}

.flow-preview strong {
  font-weight: 600;
}

.start-automation-info {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: rgba(34, 197, 94, 0.1);
  border-radius: 8px;
  margin-top: 8px;
}

.start-automation-info i {
  color: #22c55e;
  font-size: 1rem;
  flex-shrink: 0;
}

.start-automation-info div {
  flex: 1;
}

.start-automation-info strong {
  display: block;
  color: var(--text-primary);
  margin-bottom: 2px;
  font-size: 0.8125rem;
}

.start-automation-info p {
  color: var(--text-secondary);
  font-size: 0.8125rem;
  line-height: 1.4;
  margin: 2px 0;
}

.start-automation-info ul {
  margin: 4px 0 0 0;
  padding-left: 16px;
  color: var(--text-secondary);
  font-size: 0.8125rem;
}

.start-automation-info li {
  margin: 2px 0;
}
</style>
