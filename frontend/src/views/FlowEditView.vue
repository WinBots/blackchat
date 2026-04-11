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
          <button class="btn btn-secondary" :class="{ 'btn-trigger-pulse': steps.length === 0 }" @click="showTriggerModal = true">
            <i class="fa-solid fa-bolt"></i>
            Adicionar Gatilho
          </button>
          <button class="btn btn-secondary" @click="fitToScreen" title="Encaixar tudo na tela">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/>
            </svg>
            Encaixar
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
          <button class="btn btn-ai-generate" @click="showAIModal = true" title="Gerar fluxo com IA">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
            Gerar com IA
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
          :style="sidebarCollapsed ? { width: '44px' } : { width: `${sidebarWidth}px` }"
          :class="{ 'is-resizing': isResizingSidebar, 'is-collapsed': sidebarCollapsed }"
          @focusin="handleSidebarFocusIn"
          @focusout="handleSidebarFocusOut"
          @mousedown="handleSidebarMouseDown"
        >
          <!-- Resizer só aparece quando expandido -->
          <div
            v-if="!sidebarCollapsed"
            class="sidebar-resizer"
            role="separator"
            aria-orientation="vertical"
            :aria-valuenow="sidebarWidth"
            :aria-valuemin="SIDEBAR_MIN_W"
            :aria-valuemax="SIDEBAR_MAX_W"
            tabindex="0"
            title="Arraste para ajustar a largura"
            @mousedown.stop.prevent="startSidebarResize"
          ></div>

          <!-- Sidebar colapsado: só o botão de reabrir -->
          <div v-if="sidebarCollapsed" class="sidebar-collapsed-btn" @click.stop="sidebarCollapsed = false" title="Expandir painel">
            <i class="fa-solid fa-chevron-right"></i>
          </div>

          <!-- Sidebar expandido: conteúdo normal -->
          <template v-else>
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
              <button class="sidebar-close-btn" @click.stop="sidebarCollapsed = true" title="Recolher painel">
                <i class="fa-solid fa-chevron-left"></i>
              </button>
            </div>
          </template>

          <div class="sidebar-body" v-if="selectedStep && !sidebarCollapsed">
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
                  <div class="text-editor-unified">
                    <div class="tag-chips-bar">
                      <button
                        v-for="tag in personalizationTags"
                        :key="tag.value"
                        type="button"
                        class="tag-chip-inline"
                        @click="insertTag(tag.value)"
                        :title="tag.value"
                      >
                        {{ tag.label }}
                      </button>
                    </div>
                    <textarea
                      v-model="currentBlock.text"
                      class="sidebar-textarea"
                      placeholder="Digite o texto..."
                      rows="4"
                      @input="autoSave"
                      ref="contentTextareaRef"
                    ></textarea>
                    <div class="text-toolbar-embedded">
                      <button class="text-toolbar-btn" type="button" title="Negrito" @mousedown.prevent @click="wrapActiveSelection('*', '*')"><i class="fa-solid fa-bold"></i></button>
                      <button class="text-toolbar-btn" type="button" title="Itálico" @mousedown.prevent @click="wrapActiveSelection('_', '_')"><i class="fa-solid fa-italic"></i></button>
                      <button class="text-toolbar-btn" type="button" title="Sublinhado" @mousedown.prevent @click="wrapActiveSelection('__', '__')"><i class="fa-solid fa-underline"></i></button>
                      <button class="text-toolbar-btn" type="button" title="Riscado" @mousedown.prevent @click="wrapActiveSelection('~', '~')"><i class="fa-solid fa-strikethrough"></i></button>
                      <div class="text-toolbar-sep"></div>
                      <button class="text-toolbar-btn" type="button" title="Emojis" @mousedown.prevent @click="toggleEmojiPicker"><i class="fa-regular fa-face-smile"></i></button>
                      <button class="text-toolbar-btn" type="button" title="Link" @mousedown.prevent @click="createLinkOnActiveSelection"><i class="fa-solid fa-link"></i></button>
                      <div v-if="emojiPickerOpen" class="emoji-popover">
                        <button v-for="e in emojiList" :key="e" type="button" class="emoji-btn" @mousedown.prevent @click="insertIntoActiveText(e); emojiPickerOpen = false">{{ e }}</button>
                      </div>
                    </div>
                  </div>
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
                  <div class="text-editor-unified">
                    <div class="tag-chips-bar">
                      <button
                        v-for="tag in personalizationTags"
                        :key="`btn-${tag.value}`"
                        type="button"
                        class="tag-chip-inline"
                        @click="insertTag(tag.value)"
                        :title="tag.value"
                      >
                        {{ tag.label }}
                      </button>
                    </div>
                    <textarea
                      v-model="currentBlock.text"
                      class="sidebar-textarea"
                      placeholder="Mensagem acima dos botões (opcional)..."
                      rows="3"
                      @input="autoSave"
                      ref="contentTextareaRef"
                    ></textarea>
                    <div class="text-toolbar-embedded">
                      <button class="text-toolbar-btn" type="button" title="Negrito" @mousedown.prevent @click="wrapActiveSelection('*', '*')"><i class="fa-solid fa-bold"></i></button>
                      <button class="text-toolbar-btn" type="button" title="Itálico" @mousedown.prevent @click="wrapActiveSelection('_', '_')"><i class="fa-solid fa-italic"></i></button>
                      <button class="text-toolbar-btn" type="button" title="Sublinhado" @mousedown.prevent @click="wrapActiveSelection('__', '__')"><i class="fa-solid fa-underline"></i></button>
                      <button class="text-toolbar-btn" type="button" title="Riscado" @mousedown.prevent @click="wrapActiveSelection('~', '~')"><i class="fa-solid fa-strikethrough"></i></button>
                      <div class="text-toolbar-sep"></div>
                      <button class="text-toolbar-btn" type="button" title="Emojis" @mousedown.prevent @click="toggleEmojiPicker"><i class="fa-regular fa-face-smile"></i></button>
                      <button class="text-toolbar-btn" type="button" title="Link" @mousedown.prevent @click="createLinkOnActiveSelection"><i class="fa-solid fa-link"></i></button>
                    </div>
                  </div>
                  
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
        </aside>

        <!-- Canvas de Fluxo -->
        <div
          class="flow-canvas-container"
          :class="{ 'with-sidebar': selectedStep }"
          ref="containerRef"
          @wheel.prevent="handleWheel"
          @mousedown="startPan"
        >
        <!-- Empty state — fora do workspace para não ser arrastado com o canvas -->
        <div v-if="steps.length === 0" class="flow-empty-state">
          <div class="empty-state-icon">
            <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
          </div>
          <h3 class="empty-state-title">Seu fluxo está vazio</h3>
          <p class="empty-state-desc">Clique em <strong>Adicionar Gatilho</strong> <i class="fa-solid fa-bolt" style="color:#10b981;font-size:0.85em;"></i> no topo para começar</p>
          <div class="empty-state-arrow">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>
          </div>
        </div>

        <!-- Overlay de loading da IA -->
        <div v-if="isApplyingAI" class="ai-applying-overlay">
          <div class="ai-applying-inner">
            <div class="ai-applying-icon">
              <svg class="ai-spinner" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
            <p class="ai-applying-title">Aplicando fluxo</p>
            <p class="ai-applying-sub">Criando blocos e organizando o canvas...</p>
            <div class="ai-applying-bar">
              <div class="ai-applying-bar-fill"></div>
            </div>
          </div>
        </div>
        <div 
          class="flow-canvas-workspace"
          ref="workspaceRef"
          :style="{
            transform: `translate(${(isPanning ? panOffset.x : canvasOffset.x)}px, ${(isPanning ? panOffset.y : canvasOffset.y)}px) scale(${canvasScale})`,
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
            <g
              v-for="conn in connectionPaths"
              :key="conn.id"
              class="connection-group"
            >
              <path
                :d="conn.path"
                class="connection-line connection-line-animated"
                marker-end="url(#arrow-end)"
              />

              <!-- Lixeira no meio da linha (deletar conexão) -->
              <g
                class="connection-delete"
                :transform="`translate(${conn.midX}, ${conn.midY})`"
                role="button"
                tabindex="0"
                @mousedown.stop.prevent
                @click.stop.prevent="removeConnection(conn.id)"
              >
                <circle class="connection-delete-bg" r="9" />
                <g class="connection-delete-icon" transform="translate(-4.5,-5)">
                  <rect x="1.5" y="3" width="6" height="7" rx="1" />
                  <path d="M1 3h7" />
                  <path d="M3 3V2h2v1" />
                  <line x1="3.5" y1="5" x2="3.5" y2="9" />
                  <line x1="5.5" y1="5" x2="5.5" y2="9" />
                </g>
              </g>
            </g>
          </svg>

          <!-- Flow Nodes -->
          <div
            v-for="step in steps"
            :key="step.id"
            class="flow-node"
            :class="{
              'is-dragging': draggingNodeId === step.id,
              'is-selected': selectedStep && selectedStep.id === step.id,
              'is-deleting': deletingStepId === step.id,
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
              <!-- Overlay de loading ao excluir -->
              <div v-if="deletingStepId === step.id" class="flow-node-deleting-overlay">
                <i class="fa-solid fa-spinner fa-spin"></i>
                <span>Excluindo…</span>
              </div>

              <div class="flow-node-header-simple">
                <span class="flow-node-icon">
                  <i :class="getStepIcon(step.type)"></i>
                </span>
                <div style="flex:1; min-width:0;">
                  <div class="flow-node-title">{{ renderStepTitle(step) }}</div>
                  <div class="flow-node-subtitle" v-html="renderStepSubtitle(step)"></div>
                </div>
                <button
                  class="btn-node-duplicate"
                  title="Duplicar (em branco)"
                  @click.stop="duplicateStep(step)"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="11" height="11" rx="2" />
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                  </svg>
                </button>
                <button class="btn-node-delete" title="Excluir" @click.stop="deleteStep(step.id)">
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
                  :data-block-id="block.id"
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
                    :disabled="isAddingBlock"
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
                    :disabled="isAddingBlock"
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

          <div class="trigger-card" :class="{ 'trigger-card--loading': isAddingBlock }" @click="addTrigger('telegram_message')">
            <div class="trigger-card-icon">
              <i v-if="isAddingBlock" class="fa-solid fa-spinner fa-spin"></i>
              <i v-else class="fa-brands fa-telegram"></i>
            </div>
            <div class="trigger-card-body">
              <p class="trigger-card-kicker">Mensagem do Telegram</p>
              <p class="trigger-card-title">O usuário envia uma mensagem</p>
              <p class="trigger-card-desc">Selecione uma forma de acionar a automação.</p>
            </div>
            <div class="trigger-card-chevron">
              <i v-if="isAddingBlock" class="fa-solid fa-spinner fa-spin"></i>
              <i v-else class="fa-solid fa-chevron-right"></i>
            </div>
          </div>

          <div class="trigger-card" :class="{ 'trigger-card--loading': isAddingBlock }" @click="addTrigger('telegram_referral')">
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

  <!-- Modal: Conflito de Keywords -->
  <div v-if="aiKeywordConflict" class="modal-overlay" @click.self="aiKeywordConflict = null">
    <div class="modal-content kw-conflict-modal" @click.stop>
      <div class="modal-header">
        <div>
          <h3 class="modal-title">Palavras-chave em conflito</h3>
          <p class="kw-conflict-subtitle">
            Estas palavras já estão em uso no fluxo <strong>"{{ aiKeywordConflict.conflictingFlowName }}"</strong>. Substitua-as para continuar.
          </p>
        </div>
        <button class="modal-close" @click="aiKeywordConflict = null">
          <i class="fa-solid fa-times"></i>
        </button>
      </div>

      <div class="modal-body kw-conflict-body">
        <div
          v-for="kw in aiKeywordConflict.conflictingKeywords"
          :key="kw"
          class="kw-conflict-row"
        >
          <div class="kw-conflict-original">
            <span class="kw-conflict-label">Conflitante</span>
            <span class="kw-chip kw-chip--conflict">{{ kw }}</span>
          </div>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="2" flex-shrink="0">
            <line x1="5" y1="12" x2="19" y2="12"/>
            <polyline points="12 5 19 12 12 19"/>
          </svg>
          <div class="kw-conflict-new">
            <span class="kw-conflict-label">Nova palavra-chave</span>
            <input
              class="kw-conflict-input"
              :class="{ 'kw-conflict-input--same': (aiKeywordEdits[kw] || '').toLowerCase().trim() === kw }"
              v-model="aiKeywordEdits[kw]"
              :placeholder="`ex: ${kw}-novo`"
            />
          </div>
        </div>

        <p class="kw-conflict-hint">
          Cada palavra-chave deve ser única por canal para evitar ambiguidade no disparo dos fluxos.
        </p>
      </div>

      <div class="modal-footer kw-conflict-footer">
        <button class="btn btn-secondary" @click="aiKeywordConflict = null">Cancelar</button>
        <button
          class="btn kw-btn-apply"
          @click="resolveKeywordConflict"
          :disabled="Object.values(aiKeywordEdits).some(v => !v.trim() || aiKeywordConflict.conflictingKeywords.includes(v.toLowerCase().trim()))"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          Aplicar com novas palavras-chave
        </button>
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

  <!-- ──────────────────────────────────────────────────────── -->
  <!-- Modal: Gerar Fluxo com IA                               -->
  <!-- ──────────────────────────────────────────────────────── -->
  <div v-if="showAIModal" class="ai-modal-overlay" @click.self="closeAIModal">
    <div class="ai-modal">

      <!-- Header -->
      <div class="ai-modal-header">
        <div class="ai-modal-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
          Gerar Fluxo com IA
        </div>
        <button class="ai-modal-close" @click="closeAIModal" :disabled="aiGenerating">×</button>
      </div>

      <!-- Conteúdo: estado inicial (prompt) -->
      <div v-if="!aiResult" class="ai-modal-body">
        <p class="ai-modal-hint">
          Descreva o fluxo que deseja criar. Quanto mais detalhes, melhor o resultado.
        </p>

        <!-- Exemplos rápidos -->
        <div class="ai-examples">
          <span class="ai-examples-label">Exemplos:</span>
          <button
            v-for="ex in aiExamples"
            :key="ex"
            class="ai-example-chip"
            @click="aiPrompt = ex"
            :disabled="aiGenerating"
          >{{ ex }}</button>
        </div>

        <textarea
          v-model="aiPrompt"
          class="ai-prompt-input"
          placeholder="Ex: Crie um fluxo de boas-vindas que pergunta o nome do usuário, depois oferece 3 planos com botões (Básico, Pro, Enterprise), salva a escolha e adiciona a tag correspondente..."
          rows="5"
          :disabled="aiGenerating"
          @keydown.ctrl.enter="runAIGenerate"
        />
        <div class="ai-prompt-meta">
          <span class="ai-char-count" :class="{ 'ai-char-count--warn': aiPrompt.length > 1800 }">
            {{ aiPrompt.length }}/2000
          </span>
          <span class="ai-hint-shortcut">Ctrl+Enter para gerar</span>
        </div>

        <div v-if="aiError" class="ai-error">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {{ aiError }}
        </div>
      </div>

      <!-- Conteúdo: preview do resultado gerado -->
      <div v-else class="ai-modal-body">
        <div class="ai-result-header">
          <div class="ai-result-badge">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            Fluxo gerado com sucesso
          </div>
        </div>

        <div class="ai-result-info">
          <div class="ai-result-row">
            <span class="ai-result-label">Nome</span>
            <span class="ai-result-value">{{ aiResult.name }}</span>
          </div>
          <div class="ai-result-row" v-if="aiResult.description">
            <span class="ai-result-label">Descrição</span>
            <span class="ai-result-value">{{ aiResult.description }}</span>
          </div>
          <div class="ai-result-row">
            <span class="ai-result-label">Steps</span>
            <span class="ai-result-value">{{ aiResult.steps.length }} blocos</span>
          </div>
          <div class="ai-result-row">
            <span class="ai-result-label">Conexões</span>
            <span class="ai-result-value">{{ aiResult.connections.length }}</span>
          </div>
        </div>

        <!-- Lista de steps gerados -->
        <div class="ai-steps-preview">
          <div
            v-for="step in aiResult.steps"
            :key="step.id"
            class="ai-step-item"
          >
            <span class="ai-step-badge" :class="`ai-step-badge--${step.type}`">
              {{ step.type }}
            </span>
            <span class="ai-step-label">
              {{ step.config?.text || step.config?.triggerType || step.type }}
            </span>
          </div>
        </div>

        <p class="ai-apply-warning">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          Isso substituirá todos os blocos atuais do fluxo.
        </p>
      </div>

      <!-- Loading -->
      <!-- Loading progressivo -->
      <div v-if="aiGenerating" class="ai-loading">
        <div class="ai-loading-inner">
          <!-- Ícone pulsante -->
          <div class="ai-loading-icon">
            <svg class="ai-spinner" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
          </div>

          <!-- Etapas progressivas -->
          <div class="ai-loading-steps">
            <div
              v-for="(step, idx) in aiLoadingSteps"
              :key="idx"
              class="ai-loading-step"
              :class="{
                'ai-loading-step--done':    idx < aiLoadingCurrentStep,
                'ai-loading-step--active':  idx === aiLoadingCurrentStep,
                'ai-loading-step--pending': idx > aiLoadingCurrentStep,
              }"
            >
              <span class="ai-loading-step-icon">
                <svg v-if="idx < aiLoadingCurrentStep" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <svg v-else-if="idx === aiLoadingCurrentStep" class="ai-step-spin" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                </svg>
                <span v-else class="ai-step-dot"></span>
              </span>
              <span class="ai-loading-step-label">{{ step }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="ai-modal-footer">
        <template v-if="!aiResult">
          <button class="ai-btn-cancel" @click="closeAIModal" :disabled="aiGenerating">Cancelar</button>
          <button
            class="ai-btn-generate"
            @click="runAIGenerate"
            :disabled="aiGenerating || !aiPrompt.trim() || aiPrompt.length > 2000"
          >
            <svg v-if="!aiGenerating" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
            {{ aiGenerating ? 'Gerando...' : 'Gerar Fluxo' }}
          </button>
        </template>
        <template v-else>
          <button class="ai-btn-cancel" @click="aiResult = null; aiError = null">
            ← Tentar novamente
          </button>
          <button class="ai-btn-apply" @click="applyAIFlow">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            Aplicar ao Canvas
          </button>
        </template>
      </div>

    </div>
  </div>

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
import { generateFlowWithAI } from '@/api/ai'
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
const hasUnsavedChanges = ref(false)

// Histórico para undo/redo (conexões + posições — steps têm confirmação própria)
const undoStack = []
const redoStack = []
const MAX_HISTORY = 40

const snapshotState = () => ({
  connections: JSON.parse(JSON.stringify(connections.value)),
  nodePositions: JSON.parse(JSON.stringify(nodePositions.value)),
})

const pushUndo = () => {
  undoStack.push(snapshotState())
  if (undoStack.length > MAX_HISTORY) undoStack.shift()
  redoStack.length = 0  // nova ação limpa o redo
}

const applySnapshot = (snapshot) => {
  connections.value = snapshot.connections
  nodePositions.value = snapshot.nodePositions
  nextTick(() => updateConnectionPaths())
  scheduleWorkflowSave({ withStepSync: false })
}

const undo = () => {
  if (undoStack.length === 0) return
  redoStack.push(snapshotState())
  applySnapshot(undoStack.pop())
}

const redo = () => {
  if (redoStack.length === 0) return
  undoStack.push(snapshotState())
  applySnapshot(redoStack.pop())
}

let saveTimeout = null
let saveStepTimeout = null
let workflowSaveOptions = { withStepSync: false }

const SIDEBAR_MIN_W = 280
const SIDEBAR_MAX_W = 720
const sidebarWidth = ref(280)
const isResizingSidebar = ref(false)
const sidebarCollapsed = ref(false)
let _sidebarResizeStartX = 0
let _sidebarResizeStartW = 280
let _sidebarResizeMoveHandler = null
let _sidebarResizeUpHandler = null
let _sidebarResizePrevCursor = ''
let _sidebarResizePrevUserSelect = ''

const clamp = (val, min, max) => Math.min(max, Math.max(min, val))

const startSidebarResize = (e) => {
  if (e.button !== 0) return
  if (isResizingSidebar.value) return

  isResizingSidebar.value = true
  _sidebarResizeStartX = e.clientX
  _sidebarResizeStartW = sidebarWidth.value

  _sidebarResizePrevCursor = document.body.style.cursor
  _sidebarResizePrevUserSelect = document.body.style.userSelect
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'

  const handleMove = (ev) => {
    const dx = ev.clientX - _sidebarResizeStartX
    sidebarWidth.value = clamp(_sidebarResizeStartW + dx, SIDEBAR_MIN_W, SIDEBAR_MAX_W)
  }

  const handleUp = () => {
    isResizingSidebar.value = false
    document.body.style.cursor = _sidebarResizePrevCursor
    document.body.style.userSelect = _sidebarResizePrevUserSelect

    if (_sidebarResizeMoveHandler) document.removeEventListener('mousemove', _sidebarResizeMoveHandler)
    if (_sidebarResizeUpHandler) document.removeEventListener('mouseup', _sidebarResizeUpHandler)
    _sidebarResizeMoveHandler = null
    _sidebarResizeUpHandler = null
  }

  _sidebarResizeMoveHandler = handleMove
  _sidebarResizeUpHandler = handleUp

  document.addEventListener('mousemove', _sidebarResizeMoveHandler)
  document.addEventListener('mouseup', _sidebarResizeUpHandler)
}
const showTriggerModal = ref(false)
const showAddBlockModal = ref(false)

// ── IA: Gerar fluxo ──────────────────────────────────────────
const showAIModal = ref(false)
const aiPrompt = ref('')
const aiGenerating = ref(false)
const aiResult = ref(null)
const aiError = ref(null)

// Etapas do loader progressivo
const aiLoadingSteps = [
  'Lendo o seu prompt...',
  'Identificando os blocos necessários...',
  'Montando a estrutura do fluxo...',
  'Conectando os passos...',
  'Revisando e validando...',
  'Finalizando o fluxo...',
]
const aiLoadingCurrentStep = ref(0)
let _aiLoadingTimer = null

const _startAILoadingProgress = () => {
  aiLoadingCurrentStep.value = 0
  const intervals = [1200, 2500, 4000, 6000, 9000] // ms para avançar cada etapa
  let idx = 0
  const advance = () => {
    if (idx < intervals.length) {
      _aiLoadingTimer = setTimeout(() => {
        aiLoadingCurrentStep.value = idx + 1
        idx++
        advance()
      }, idx === 0 ? intervals[0] : intervals[idx] - intervals[idx - 1])
    }
  }
  advance()
}

const _stopAILoadingProgress = () => {
  if (_aiLoadingTimer) { clearTimeout(_aiLoadingTimer); _aiLoadingTimer = null }
  // Marcar todas como concluídas ao terminar
  aiLoadingCurrentStep.value = aiLoadingSteps.length
}

const aiExamples = [
  'Captura de lead com nome e email',
  'Suporte ao cliente com menu de opções',
  'Apresentação de planos com botões e tags',
  'Agendamento com coleta de data e horário',
]

const closeAIModal = () => {
  if (aiGenerating.value) return
  showAIModal.value = false
  aiResult.value = null
  aiError.value = null
}

const runAIGenerate = async () => {
  if (!aiPrompt.value.trim() || aiGenerating.value) return
  aiGenerating.value = true
  aiError.value = null
  aiResult.value = null
  _startAILoadingProgress()
  try {
    aiResult.value = await generateFlowWithAI(aiPrompt.value.trim())
  } catch (err) {
    const detail = err?.response?.data?.detail
    aiError.value = detail || 'Erro ao gerar fluxo. Verifique se a API Key está configurada e tente novamente.'
  } finally {
    _stopAILoadingProgress()
    aiGenerating.value = false
  }
}

/**
 * Calcula layout hierárquico automático (esquerda → direita).
 * Retorna um mapa { stepId: { x, y } } sem sobreposições.
 *
 * @param {Array}  stepIds     - IDs reais dos nós na ordem de criação
 * @param {Array}  conns       - conexões já com IDs reais { from, to }
 * @param {Object} stepTypeMap - { stepId: 'trigger'|'message'|'action'|... }
 */
const computeAutoLayout = (stepIds, conns, stepTypeMap) => {
  const X_GAP = 380   // espaço horizontal entre colunas
  const Y_GAP = 240   // espaço vertical entre nós na mesma coluna
  const ORIGIN_X = 80
  const ORIGIN_Y = 80

  // 1. Monta adjacências
  const children = {}  // id -> [id]
  const parents  = {}  // id -> [id]
  for (const id of stepIds) { children[id] = []; parents[id] = [] }
  for (const c of conns) {
    if (children[c.from]) children[c.from].push(c.to)
    if (parents[c.to])    parents[c.to].push(c.from)
  }

  // 2. Atribui camadas via BFS (longest-path from roots)
  const layer = {}
  // Raízes: nós sem pais, ou do tipo trigger
  const roots = stepIds.filter(id => parents[id].length === 0 || stepTypeMap[id] === 'trigger')
  if (roots.length === 0 && stepIds.length > 0) roots.push(stepIds[0])

  const queue = [...roots]
  for (const id of roots) layer[id] = 0
  // BFS — garante que cada nó fica na camada máxima de todos os pais
  const visited = new Set(roots)
  let head = 0
  while (head < queue.length) {
    const cur = queue[head++]
    for (const child of children[cur]) {
      const proposed = (layer[cur] ?? 0) + 1
      if (layer[child] === undefined || layer[child] < proposed) {
        layer[child] = proposed
      }
      if (!visited.has(child)) {
        visited.add(child)
        queue.push(child)
      }
    }
  }
  // Nós não alcançados (ilhas) ficam na camada 0
  for (const id of stepIds) {
    if (layer[id] === undefined) layer[id] = 0
  }

  // 3. Agrupa nós por camada
  const maxLayer = Math.max(...Object.values(layer))
  const layers = Array.from({ length: maxLayer + 1 }, () => [])
  for (const id of stepIds) layers[layer[id]].push(id)

  // 4. Ordena nós dentro de cada camada pelo índice do pai (reduz cruzamentos)
  for (let l = 1; l <= maxLayer; l++) {
    layers[l].sort((a, b) => {
      const pa = parents[a]?.[0] ? layers[l - 1].indexOf(parents[a][0]) : 0
      const pb = parents[b]?.[0] ? layers[l - 1].indexOf(parents[b][0]) : 0
      return pa - pb
    })
  }

  // 5. Calcula posições centralizando cada camada em torno do centro vertical
  const positions = {}
  for (let l = 0; l <= maxLayer; l++) {
    const nodes = layers[l]
    const totalH = nodes.length * Y_GAP
    const startY = ORIGIN_Y - totalH / 2 + Y_GAP / 2
    nodes.forEach((id, i) => {
      positions[id] = {
        x: ORIGIN_X + l * X_GAP,
        y: startY + i * Y_GAP,
      }
    })
  }

  return positions
}

const applyAIFlow = async () => {
  if (!aiResult.value) return
  const result = aiResult.value

  // Fecha o modal e ativa o loader do canvas
  closeAIModal()
  isApplyingAI.value = true
  await nextTick()

  try {
    // 1. Deletar todos os steps existentes
    await Promise.all(
      steps.value.map(s => deleteFlowStep(flowId.value, s.id).catch(() => {}))
    )
    steps.value = []
    connections.value = []
    nodePositions.value = {}

    // 2. Criar os novos steps em sequência para garantir IDs retornados
    const idMap = {}       // { ai_step_id -> real_step_id }
    const stepTypeMap = {} // { real_step_id -> type }
    for (const step of result.steps) {
      const created = await createFlowStep(flowId.value, {
        type: step.type,
        order_index: step.order_index,
        config: step.config || {},
      })
      idMap[step.id] = created.id
      stepTypeMap[created.id] = created.type
      steps.value.push(created)
      if (step.type === 'message') ensureMessageBlocks(created)
    }

    // 3. Remapear connections com IDs reais
    const mappedConns = result.connections
      .filter(c => idMap[c.from] && idMap[c.to])
      .map(c => ({
        id: `${idMap[c.from]}-${c.outputId || 'default'}-${idMap[c.to]}`,
        from: idMap[c.from],
        to: idMap[c.to],
        outputId: c.outputId || 'default',
      }))
    connections.value = mappedConns

    // 4. Remapear targetStepId nos botões
    steps.value.forEach(step => {
      if (step.config?.blocks) {
        step.config.blocks.forEach(block => {
          if (block.type === 'button' && block.buttons) {
            block.buttons.forEach(btn => {
              if (btn.action === 'flow' && btn.targetStepId) {
                btn.targetStepId = idMap[btn.targetStepId] || btn.targetStepId
              }
            })
          }
        })
      }
    })

    // 5. Calcular layout automático hierárquico
    const realIds = steps.value.map(s => s.id)
    const autoPositions = computeAutoLayout(realIds, mappedConns, stepTypeMap)
    nodePositions.value = autoPositions

    // 6. Atualizar nome do fluxo se gerado pela IA
    if (result.name && flow.value) {
      flow.value.name = result.name
      if (result.description) flow.value.description = result.description
    }

    // 7. Salvar tudo (inclui nodePositions no config do flow)
    await saveWorkflow()
    await nextTick()
    fitToScreen()

    toast.success(`Fluxo "${result.name}" aplicado com ${result.steps.length} blocos!`)
  } catch (err) {
    console.error('Erro ao aplicar fluxo IA:', err)
    const detail = err?.response?.data?.detail
    if (err?.response?.status === 409 && detail?.conflicting_keywords) {
      // Abre modal para o usuário resolver o conflito de keywords
      aiKeywordConflict.value = {
        conflictingKeywords: detail.conflicting_keywords,
        conflictingFlowName: detail.conflicting_flow_name,
        pendingResult: result,
      }
    } else {
      toast.error('Erro ao aplicar o fluxo gerado. Tente novamente.')
    }
  } finally {
    isApplyingAI.value = false
  }
}
const isApplyingAI = ref(false)

// Modal de conflito de keywords
const aiKeywordConflict = ref(null) // { conflictingKeywords, conflictingFlowName, pendingResult }
const aiKeywordEdits = ref({})      // { keyword: novoValor }

watch(aiKeywordConflict, (val) => {
  if (!val) return
  // Pré-preenche os inputs com as keywords conflitantes
  const edits = {}
  for (const kw of val.conflictingKeywords) edits[kw] = kw
  aiKeywordEdits.value = edits
})

const resolveKeywordConflict = async () => {
  if (!aiKeywordConflict.value) return
  const { pendingResult } = aiKeywordConflict.value
  const edits = aiKeywordEdits.value

  // Aplica as substituições no trigger step do resultado da IA
  const updatedResult = {
    ...pendingResult,
    steps: pendingResult.steps.map(step => {
      if (step.type !== 'trigger' || !step.config?.keywords) return step
      return {
        ...step,
        config: {
          ...step.config,
          keywords: step.config.keywords.map(kw => {
            const key = typeof kw === 'string' ? kw : kw.text || ''
            return edits[key.toLowerCase().trim()] ?? kw
          }),
        },
      }
    }),
  }

  aiKeywordConflict.value = null
  aiResult.value = updatedResult
  await applyAIFlow()
}

const isAddingBlock = ref(false)
const deletingStepId = ref(null)
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
        label: 'Mensagem',
        desc: 'Envia texto, imagem, vídeo ou áudio',
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
        color: 'linear-gradient(135deg, #00FF66, #16a34a)',
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

const handleDocumentClickCloseSidebar = (event) => {
  if (!selectedStep.value) return
  if (isResizingSidebar.value) return

  const target = event.target
  const sidebarEl = sidebarRootRef.value

  const clickedInsideSidebar = sidebarEl && (sidebarEl === target || sidebarEl.contains(target))
  if (clickedInsideSidebar) return

  const clickedOnNode = target?.closest?.('.flow-node')
  if (clickedOnNode) return

  // Clique em qualquer outro lugar (canvas vazio, linhas, etc) colapsa o menu
  sidebarCollapsed.value = true
}

const handleGlobalKeydown = (e) => {
  // Ignorar se o foco estiver em um input/textarea
  const tag = document.activeElement?.tagName?.toLowerCase()
  if (tag === 'input' || tag === 'textarea' || document.activeElement?.isContentEditable) return

  const ctrl = e.ctrlKey || e.metaKey
  if (ctrl && e.key === 'z' && !e.shiftKey) {
    e.preventDefault()
    undo()
  } else if (ctrl && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
    e.preventDefault()
    redo()
  }
}

const handleBeforeUnload = (e) => {
  if (hasUnsavedChanges.value || saveTimeout !== null || saveStepTimeout !== null) {
    e.preventDefault()
    e.returnValue = ''
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleDocumentMouseDown)
  document.addEventListener('click', handleDocumentClickCloseSidebar)
  window.addEventListener('beforeunload', handleBeforeUnload)
  window.addEventListener('keydown', handleGlobalKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleDocumentMouseDown)
  document.removeEventListener('click', handleDocumentClickCloseSidebar)
  window.removeEventListener('beforeunload', handleBeforeUnload)
  window.removeEventListener('keydown', handleGlobalKeydown)
  // Limpar timers pendentes para não vazar memória
  if (saveTimeout) clearTimeout(saveTimeout)
  if (saveStepTimeout) clearTimeout(saveStepTimeout)
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
const panOffset = ref({ x: 50, y: 50 })
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

let _panFrame = null
let _pendingPanOffset = null
const schedulePanOffsetUpdate = () => {
  if (_panFrame) return
  _panFrame = requestAnimationFrame(() => {
    _panFrame = null
    if (_pendingPanOffset) {
      panOffset.value = _pendingPanOffset
      _pendingPanOffset = null
    }
  })
}

const getCanvasOffsetCurrent = () => {
  return isPanning.value ? panOffset.value : canvasOffset.value
}

// Posições dos Nós (livre)
const nodePositions = ref({}) // { stepId: { x, y } }
const draggingNodeId = ref(null)
const dragNodePos = ref({ x: 0, y: 0 })
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
let _connectionsDirty = false

const scheduleConnectionUpdate = () => {
  _connectionsDirty = true
  if (updateFrame) return
  updateFrame = requestAnimationFrame(() => {
    updateFrame = null
    if (!_connectionsDirty) return
    _connectionsDirty = false
    updateConnectionPaths()
  })
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
  const offset = getCanvasOffsetCurrent()
  return {
    x: (x - rect.left - offset.x) / canvasScale.value,
    y: (y - rect.top - offset.y) / canvasScale.value
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

    // Todas as requisições são independentes — rodar em paralelo
    const [flowResult, stepsResult, channelsResult, flowsResult] = await Promise.all([
      getFlow(flowId.value),
      listFlowSteps(flowId.value),
      listChannels().catch(e => { console.error('Erro ao carregar canais:', e); return [] }),
      listFlows().catch(e => { console.warn('Erro ao carregar fluxos:', e); return [] }),
    ])

    flow.value = flowResult
    steps.value = stepsResult
    channelsCache.value = channelsResult
    availableFlows.value = flowsResult

    // Resolver bot_username a partir dos canais já carregados
    const targetChannel = flow.value?.channel_id
      ? channelsCache.value.find(c => Number(c.id) === Number(flow.value.channel_id))
      : channelsCache.value.find(c => c.type === 'telegram' && c.is_active)

    if (targetChannel?.bot_username) {
      botUsername.value = targetChannel.bot_username.replace('@', '')
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
const saveWorkflow = async (opts = {}) => {
  if (!flow.value) return
  // Se outro save está rodando, reagendar para não perder a posição
  if (isSaving.value) {
    scheduleWorkflowSave(opts)
    return
  }

  const withStepSync = opts.withStepSync !== undefined ? !!opts.withStepSync : true
  
  try {
    isSaving.value = true

    if (withStepSync) {
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
    }
    
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
    
    await updateFlow(flowId.value, payload)
    hasUnsavedChanges.value = false

    if (withStepSync) {
      // Salvar todos os steps em paralelo (era sequencial: N × latência → agora: 1 × latência)
      await Promise.all(
        steps.value.map(step =>
          updateFlowStep(flowId.value, step.id, {
            type: step.type,
            config: step.config,
            order_index: step.order_index,
          }).catch(error => {
            // 409 = conflito de keyword → propagar para o catch externo mostrar toast
            if (error?.response?.status === 409) throw error
            console.error(`❌ Erro ao atualizar step ${step.id}:`, error)
          })
        )
      )
    }
  } catch (error) {
    console.error('❌ Erro ao salvar workflow:', error)
    if (error?.response?.status === 409) {
      const detail = error.response?.data?.detail || 'Keyword duplicada entre fluxos do mesmo canal.'
      toast.error(detail)
    } else {
      console.error('❌ Detalhes:', error.response?.data)
    }
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

const scheduleStepSave = (stepSnapshot) => {
  hasUnsavedChanges.value = true
  if (saveStepTimeout) clearTimeout(saveStepTimeout)
  saveStepTimeout = setTimeout(async () => {
    try {
      await updateFlowStep(flowId.value, stepSnapshot.id, {
        type: stepSnapshot.type,
        config: stepSnapshot.config,
        order_index: stepSnapshot.order_index
      })
      if (!saveTimeout) hasUnsavedChanges.value = false
    } catch (error) {
      console.error('❌ Erro ao salvar step:', error)
    }
    saveStepTimeout = null
  }, 650)
}

const scheduleWorkflowSave = (opts = {}) => {
  hasUnsavedChanges.value = true
  workflowSaveOptions = {
    withStepSync: !!opts.withStepSync || !!workflowSaveOptions.withStepSync
  }

  if (saveTimeout) clearTimeout(saveTimeout)
  saveTimeout = setTimeout(() => {
    const currentOpts = workflowSaveOptions
    workflowSaveOptions = { withStepSync: false }
    saveTimeout = null
    saveWorkflow({ withStepSync: currentOpts.withStepSync })
  }, 900)
}

// Auto-save (debounced): por padrão salva só o step (não o workflow)
const autoSave = (opts = {}) => {
  const scope = opts.scope || 'step' // 'step' | 'workflow' | 'both'

  if ((scope === 'step' || scope === 'both') && selectedStep.value) {
    // Snapshot leve para não depender de seleção futura
    const stepSnapshot = {
      id: selectedStep.value.id,
      type: selectedStep.value.type,
      config: selectedStep.value.config,
      order_index: selectedStep.value.order_index
    }
    scheduleStepSave(stepSnapshot)
  }

  if (scope === 'workflow' || scope === 'both') {
    scheduleWorkflowSave({ withStepSync: !!opts.withStepSync })
  }
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
    autoSave({ scope: 'workflow', withStepSync: false })
  } catch (error) {
    console.error('Erro ao adicionar passo:', error)
  }
}

const handleAddBlock = async (type) => {
  if (isAddingBlock.value) return
  showAddBlockModal.value = false

  // Verificar se precisa de trigger primeiro
  if (!hasTrigger.value && type !== 'trigger') {
    showTriggerModal.value = true
    toast.warning('Adicione um gatilho primeiro')
    return
  }

  isAddingBlock.value = true
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
        showTriggerModal.value = true
        return
      
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
    autoSave({ scope: 'workflow', withStepSync: false })
    
    toast.success('Bloco adicionado ao fluxo')
  } catch (error) {
    console.error('Erro ao adicionar bloco:', error)
    toast.error('Erro ao adicionar bloco')
  } finally {
    isAddingBlock.value = false
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
  
  deletingStepId.value = stepId
  try {
    await deleteFlowStep(flowId.value, stepId)

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
    await saveWorkflow()
    toast.success('Bloco removido do fluxo')
  } catch (error) {
    console.error('❌ Erro ao deletar step:', error)
    toast.error('Erro ao excluir bloco')
  } finally {
    deletingStepId.value = null
  }
}

const getBlankConfigForStepType = (type) => {
  switch (type) {
    case 'message':
      return { text: '', blocks: [] }

    case 'action':
      return { actions: [] }

    case 'condition':
      return {
        conditionType: 'field',
        field: '',
        operator: 'equals',
        value: '',
        conditions: []
      }

    case 'randomizer':
      return {
        paths: [
          { id: uid(), name: 'Caminho A', percentage: 50 },
          { id: uid(), name: 'Caminho B', percentage: 50 }
        ]
      }

    case 'wait':
      return {
        delayType: 'fixed',
        value: 5,
        unit: 'seconds',
        randomMin: 1,
        randomMax: 10
      }

    case 'comment':
      return { text: '', color: '#f59e0b' }

    case 'start_automation':
      return { flowId: null, flowName: '' }

    default:
      // fallback seguro
      return { text: '', blocks: [] }
  }
}

const duplicateStep = async (step) => {
  try {
    if (!step?.id) return
    if (step.type === 'trigger') {
      toast.info('Gatilho não pode ser duplicado')
      return
    }

    const nextIndex = steps.value.length + 1
    const stepType = step.type
    const stepConfig = getBlankConfigForStepType(stepType)

    const newStep = await createFlowStep(flowId.value, {
      type: stepType,
      order_index: nextIndex,
      config: stepConfig
    })

    const srcPos = nodePositions.value[step.id]
    nodePositions.value[newStep.id] = srcPos
      ? { x: srcPos.x + 40, y: srcPos.y + 40 }
      : { x: 120, y: 120 }

    steps.value.push(newStep)
    selectedStep.value = newStep

    autoSave({ scope: 'workflow', withStepSync: false })
    toast.success('Bloco duplicado (em branco)')
  } catch (error) {
    console.error('Erro ao duplicar step:', error)
    toast.error('Erro ao duplicar bloco')
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
  sidebarCollapsed.value = false
}

const selectBlock = (step, block) => {
  selectedStep.value = step
  selectedBlock.value = { stepId: step.id, blockId: block.id }
  sidebarCollapsed.value = false
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
  draggingBlock.value = { ...block, startIndex: blockIndex, currentIndex: blockIndex }
  blockDragStep.value = step
  
  // Criar elemento ghost
  const originalElement = event.target.closest('.msg-block')
  const blocksContainerEl = originalElement?.parentElement || null
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
  
  let pendingReorderIndex = null
  let reorderFrame = null

  const applyReorder = () => {
    reorderFrame = null
    if (!draggingBlock.value || pendingReorderIndex === null) return
    const blocks = blockDragStep.value?.config?.blocks
    if (!blocks) return

    const draggedId = String(draggingBlock.value.id)
    const fromIndex = blocks.findIndex(b => String(b.id) === draggedId)
    if (fromIndex < 0) return

    let toIndex = pendingReorderIndex
    // Inserção pode ser no final (length)
    toIndex = Math.max(0, Math.min(blocks.length, toIndex))
    if (toIndex === fromIndex) return

    const [moved] = blocks.splice(fromIndex, 1)
    // Após remover, o array diminui 1; clamp novamente
    toIndex = Math.max(0, Math.min(blocks.length, toIndex))
    blocks.splice(toIndex, 0, moved)
    draggingBlock.value.currentIndex = toIndex
  }

  const scheduleReorder = (toIndex) => {
    pendingReorderIndex = toIndex
    if (reorderFrame) return
    reorderFrame = requestAnimationFrame(applyReorder)
  }

  const handleMouseMove = (e) => {
    if (!draggingBlock.value) return
    
    // Mover ghost
    if (ghostElement.value) {
      ghostElement.value.style.left = `${e.clientX - ghostElement.value.offsetWidth / 2}px`
      ghostElement.value.style.top = `${e.clientY - 20}px`
    }
    
    const blocks = blockDragStep.value?.config?.blocks
    if (!blocks || blocks.length < 2) return

    // Descobrir qual bloco está sob o mouse (sem depender do índice original)
    const el = document.elementFromPoint(e.clientX, e.clientY)
    const overBlockEl = el?.closest?.('.msg-block')
    const overId = overBlockEl?.dataset?.blockId
    const draggedId = String(draggingBlock.value.id)

    const isInThisContainer = (candidateEl) => {
      if (!blocksContainerEl || !candidateEl) return true
      return blocksContainerEl.contains(candidateEl)
    }

    let targetIndex = null
    if (overId && overId !== draggedId && isInThisContainer(overBlockEl)) {
      const overIndex = blocks.findIndex(b => String(b.id) === String(overId))
      if (overIndex >= 0) {
        const rect = overBlockEl.getBoundingClientRect()
        const insertAfter = e.clientY > rect.top + rect.height / 2
        targetIndex = insertAfter ? overIndex + 1 : overIndex
      }
    }

    // Fallback: mouse entre blocos (ou fora do bloco) → usar o mais próximo pelo eixo Y
    if (targetIndex === null && blocksContainerEl) {
      const blockEls = Array.from(blocksContainerEl.querySelectorAll('.msg-block[data-block-id]'))
      const closest = blockEls
        .map((node) => {
          const rect = node.getBoundingClientRect()
          const centerY = rect.top + rect.height / 2
          return { node, rect, distance: Math.abs(e.clientY - centerY) }
        })
        .sort((a, b) => a.distance - b.distance)[0]

      if (closest?.node) {
        const cid = closest.node.dataset.blockId
        if (cid && cid !== draggedId) {
          const overIndex = blocks.findIndex(b => String(b.id) === String(cid))
          if (overIndex >= 0) {
            const insertAfter = e.clientY > (closest.rect.top + closest.rect.height / 2)
            targetIndex = insertAfter ? overIndex + 1 : overIndex
          }
        }
      }
    }

    if (targetIndex === null) {
      dragOverIndex.value = null
      return
    }

    // Ajuste do índice de inserção considerando remoção
    const fromIndex = blocks.findIndex(b => String(b.id) === draggedId)
    if (fromIndex < 0) return
    let toIndex = targetIndex
    if (toIndex > fromIndex) toIndex -= 1

    if (toIndex === fromIndex) {
      dragOverIndex.value = null
      return
    }

    dragOverIndex.value = toIndex
    scheduleReorder(toIndex)
  }
  
  const handleMouseUp = () => {
    if (reorderFrame) cancelAnimationFrame(reorderFrame)
    reorderFrame = null
    pendingReorderIndex = null

    const moved = draggingBlock.value && draggingBlock.value.startIndex !== draggingBlock.value.currentIndex
    if (moved) {
      autoSave()
      toast.success('Sequência atualizada')
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
  const pos = draggingNodeId.value === stepId
    ? dragNodePos.value
    : (nodePositions.value[stepId] || { x: 0, y: 0 })
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

let _nodeDragFrame = null
let _pendingDragNodePos = null

const scheduleDragNodePosUpdate = () => {
  if (_nodeDragFrame) return
  _nodeDragFrame = requestAnimationFrame(() => {
    _nodeDragFrame = null
    if (_pendingDragNodePos) {
      dragNodePos.value = _pendingDragNodePos
      _pendingDragNodePos = null
    }
  })
}

const startNodeDrag = (e, stepId) => {
  if (e.button !== 0) return
  if (isApplyingAI.value) return

  e.stopPropagation() // não iniciar pan junto

  draggingNodeId.value = stepId
  const pos = nodePositions.value[stepId] || { x: 0, y: 0 }
  _dragNodeX = pos.x
  _dragNodeY = pos.y

  // Mantém o nó seguindo o mouse mesmo com re-render
  dragNodePos.value = { x: pos.x, y: pos.y }

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

  // Atualiza posição do nó em drag (throttled por RAF)
  _pendingDragNodePos = { x: _dragNodeX, y: _dragNodeY }
  scheduleDragNodePosUpdate()

  scheduleConnectionUpdate()
}

const endNodeDrag = () => {
  const id = draggingNodeId.value
  pushUndo()
  draggingNodeId.value = null
  document.removeEventListener('mousemove', handleNodeDragMove)
  document.removeEventListener('mouseup', endNodeDrag)

  if (_nodeDragFrame) {
    cancelAnimationFrame(_nodeDragFrame)
    _nodeDragFrame = null
  }
  _pendingDragNodePos = null

  // Sincroniza estado reativo uma vez ao soltar
  if (id) {
    nodePositions.value[id] = { x: _dragNodeX, y: _dragNodeY }
    dragNodePos.value = { x: _dragNodeX, y: _dragNodeY }
    autoSave({ scope: 'workflow', withStepSync: false })
  }
}

// ==================== PAN ====================
const startPan = (e) => {
  if (e.button !== 0) return
  if (isApplyingAI.value) return

  // Não iniciar pan se estiver arrastando nó ou conexão
  if (draggingNodeId.value) return
  if (isDraggingConnection.value) return

  // Se clicou em algo "interativo", não panear (nó, porta, linha)
  const t = e.target
  if (
    t?.closest?.('.flow-node') ||
    t?.closest?.('.flow-port') ||
    t?.closest?.('.connection-line')
  ) {
    return
  }

  e.preventDefault()

  isPanning.value = true
  _panCurrentX = canvasOffset.value.x
  _panCurrentY = canvasOffset.value.y

  // estado reativo usado no template durante o pan
  panOffset.value = { x: _panCurrentX, y: _panCurrentY }
  panStart.value = {
    x: e.clientX - canvasOffset.value.x,
    y: e.clientY - canvasOffset.value.y
  }

  document.addEventListener('mousemove', handlePanMove)
  document.addEventListener('mouseup', endPan)
}

const handlePanMove = (e) => {
  if (!isPanning.value) return
  _panCurrentX = e.clientX - panStart.value.x
  _panCurrentY = e.clientY - panStart.value.y

  _pendingPanOffset = { x: _panCurrentX, y: _panCurrentY }
  schedulePanOffsetUpdate()

  // Aplicação direta no DOM para resposta imediata
  applyWorkspaceTransform(_panCurrentX, _panCurrentY, canvasScale.value)
}

const endPan = () => {
  if (!isPanning.value) return
  isPanning.value = false
  canvasOffset.value = { x: _panCurrentX, y: _panCurrentY }
  panOffset.value = { x: _panCurrentX, y: _panCurrentY }
  scheduleConnectionUpdate()

  document.removeEventListener('mousemove', handlePanMove)
  document.removeEventListener('mouseup', endPan)

  if (_panFrame) {
    cancelAnimationFrame(_panFrame)
    _panFrame = null
  }
  _pendingPanOffset = null
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

const fitToScreen = () => {
  const container = containerRef.value
  const posEntries = Object.entries(nodePositions.value)
  if (!container || posEntries.length === 0) {
    resetZoom()
    return
  }

  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
  for (const [stepId, pos] of posEntries) {
    const el = nodeEls[stepId]
    const w = el ? el.offsetWidth : 300
    const h = el ? el.offsetHeight : 140
    minX = Math.min(minX, pos.x)
    minY = Math.min(minY, pos.y)
    maxX = Math.max(maxX, pos.x + w)
    maxY = Math.max(maxY, pos.y + h)
  }

  const PADDING = 80
  const contentW = maxX - minX + PADDING * 2
  const contentH = maxY - minY + PADDING * 2
  const containerW = container.clientWidth
  const containerH = container.clientHeight

  const newScale = Math.min(Math.max(0.25, Math.min(containerW / contentW, containerH / contentH)), 1.2)
  const offsetX = (containerW - contentW * newScale) / 2 - (minX - PADDING) * newScale
  const offsetY = (containerH - contentH * newScale) / 2 - (minY - PADDING) * newScale

  canvasScale.value = newScale
  canvasOffset.value = { x: offsetX, y: offsetY }
  applyWorkspaceTransform(offsetX, offsetY, newScale)
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
    pushUndo()
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
    recalculateOrderIndex()
    
    // Auto-salvar após criar conexão
    autoSave({ scope: 'workflow', withStepSync: true })
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
    // A ação remove conexões do workflow + altera config do step
    autoSave({ scope: 'workflow', withStepSync: true })
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
  pushUndo()
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
  recalculateOrderIndex()
  
  // Auto-salvar após remover conexão
  autoSave({ scope: 'workflow', withStepSync: true })
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
    if (!distance) return null

    // Deslocamento para dar espaço à seta no final
    const offsetEnd = 15   // espaço para a seta

    const startX = fromPoint.x
    const startY = fromPoint.y
    const endX = toPoint.x - (dx / distance) * offsetEnd
    const endY = toPoint.y - (dy / distance) * offsetEnd

    const controlOffset = Math.abs(dx) * 0.5
    const c1x = startX + controlOffset
    const c1y = startY
    const c2x = endX - controlOffset
    const c2y = endY
    const path = `M ${startX} ${startY} C ${c1x} ${c1y}, ${c2x} ${c2y}, ${endX} ${endY}`

    // Ponto aproximado do meio da curva (t=0.5) para posicionar o botão de delete
    const t = 0.5
    const mt = 1 - t
    const midX = (mt * mt * mt) * startX + (3 * mt * mt * t) * c1x + (3 * mt * t * t) * c2x + (t * t * t) * endX
    const midY = (mt * mt * mt) * startY + (3 * mt * mt * t) * c1y + (3 * mt * t * t) * c2y + (t * t * t) * endY

    return { id: conn.id, path, midX, midY }
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
  if (step.type === 'message') return step.name || 'Mensagem'
  return step.name || step.config?.text || 'Sem título'
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
  if (isAddingBlock.value) return
  if (hasTrigger.value) {
    toast.warning('Já existe um gatilho neste fluxo')
    showTriggerModal.value = false
    return
  }
  isAddingBlock.value = true

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
    isAddingBlock.value = false
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
  if (!refKey) {
    toast.warning('Configure a chave de referência primeiro')
    return
  }
  const username = (botUsername.value || '').replace('@', '').trim()
  if (!username || username === 'seu_bot') {
    toast.warning('Configure o username do bot nas configurações do canal primeiro')
    return
  }
  const link = `https://t.me/${username}?start=${refKey}`
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
const handleTooltipDocumentClick = (e) => {
  if (!e.target.closest('.info-icon')) {
    closeTooltip()
  }
}

onMounted(() => {
  loadData()
  
  // Fechar tooltip ao clicar fora
  document.addEventListener('click', handleTooltipDocumentClick)
})

// Watch para recarregar quando mudar o ID da rota
watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    console.log('🔄 Mudando de fluxo, recarregando dados...')
    loadData()
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleTooltipDocumentClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousemove', handleNodeDragMove)
  document.removeEventListener('mouseup', endNodeDrag)
  document.removeEventListener('mousemove', handleConnectionDragMove)
  document.removeEventListener('mouseup', cancelConnection)
  document.removeEventListener('mousemove', handlePanMove)
  document.removeEventListener('mouseup', endPan)

  if (_sidebarResizeMoveHandler) document.removeEventListener('mousemove', _sidebarResizeMoveHandler)
  if (_sidebarResizeUpHandler) document.removeEventListener('mouseup', _sidebarResizeUpHandler)
  _sidebarResizeMoveHandler = null
  _sidebarResizeUpHandler = null
  document.body.style.cursor = _sidebarResizePrevCursor
  document.body.style.userSelect = _sidebarResizePrevUserSelect

  if (_panFrame) {
    cancelAnimationFrame(_panFrame)
    _panFrame = null
  }

  // Caso estivesse redimensionando e a view seja desmontada
  isResizingSidebar.value = false
})
</script>

<style scoped>

/* ===================== SIDEBAR RESIZER ===================== */
.flow-editor-sidebar {
  position: relative;
  background: #0d0d0d !important;
  transition: width 0.2s ease;
}

/* Estado colapsado */
.flow-editor-sidebar.is-collapsed {
  border-right: 1px solid rgba(148, 163, 184, 0.15);
}

.sidebar-collapsed-btn {
  flex: 1;
  width: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #4ade80;
  font-size: 1rem;
  transition: background 0.15s, color 0.15s;
}

.sidebar-collapsed-btn:hover {
  background: rgba(0, 255, 102, 0.08);
  color: #00FF66;
}

.flow-editor-sidebar .sidebar-header {
  position: relative;
  z-index: 10;
  padding-right: 18px;
  background: #0a0f0a !important;
}

.sidebar-title-input {
  flex: 1;
  min-width: 0;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 7px;
  color: #f1f5f9;
  font-size: 0.9375rem;
  font-weight: 500;
  padding: 7px 11px;
  outline: none;
  transition: border-color 0.18s, box-shadow 0.18s;
}

.sidebar-title-input::placeholder {
  color: rgba(148, 163, 184, 0.5);
  font-weight: 400;
}

.sidebar-title-input:focus {
  border-color: #00FF66;
  box-shadow: 0 0 0 3px rgba(0, 255, 102, 0.12);
}

.flow-editor-sidebar .sidebar-close-btn {
  position: relative;
  z-index: 11;
}

.sidebar-resizer {
  position: absolute;
  top: 0;
  right: 0;
  width: 8px;
  height: 100%;
  cursor: col-resize;
  z-index: 2;
  background: transparent;
}

.sidebar-resizer::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 2px;
  transform: translateX(-50%);
  background: rgba(148, 163, 184, 0.18);
  opacity: 0;
  transition: opacity 0.15s ease, background 0.15s ease;
}

.flow-editor-sidebar:hover .sidebar-resizer::after {
  opacity: 1;
}

.flow-editor-sidebar.is-resizing .sidebar-resizer::after {
  opacity: 1;
  background: var(--accent);
}


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
  cursor: default;
  transition: stroke 0.2s, stroke-width 0.2s;
}

.connection-line:hover {
  stroke: rgba(34, 197, 94, 1);
  stroke-width: 4;
}

.connection-delete {
  opacity: 1;
  pointer-events: all;
  transition: opacity 0.15s ease;
  cursor: pointer;
}

.connection-delete-bg {
  fill: rgba(2, 6, 23, 0.75);
  stroke: rgba(239, 68, 68, 0.55);
  stroke-width: 1;
}

.connection-delete-icon {
  fill: none;
  stroke: rgba(239, 68, 68, 0.95);
  stroke-width: 1.4;
  stroke-linecap: round;
  stroke-linejoin: round;
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
  background: rgba(0, 0, 0, 0.55);
  border: 1px solid rgba(148, 163, 184, 0.22);
  color: var(--accent);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 10;
}

.btn-add-block-circle:hover {
  transform: scale(1.1);
  background: rgba(0, 0, 0, 0.75);
  border-color: var(--accent);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.55), 0 0 0 4px var(--accent-soft-hover);
}

.btn-add-block-circle:active {
  transform: scale(0.95);
}

.btn-add-block-circle svg {
  stroke: currentColor;
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
  width: 210px;
  flex-shrink: 0;
  border-right: 1px solid rgba(255, 255, 255, 0.07);
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  overflow-y: auto;
  overflow-x: hidden;
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

.abm-card:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.abm-card:hover:not(:disabled) {
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
  background: rgba(148, 163, 184, 0.12);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: var(--text-primary);
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
    width: 140px;
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
  background: rgba(0, 0, 0, 0.45);
  border: 1px solid rgba(148, 163, 184, 0.22);
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
  background: rgba(0, 0, 0, 0.6);
  border-color: var(--accent);
}

.actions-empty {
  padding: 24px;
  text-align: center;
  color: var(--muted);
  font-size: 0.875rem;
  background: rgba(5, 10, 5, 0.5);
  border-radius: 8px;
  border: 1px dashed rgba(148, 163, 184, 0.2);
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-item {
  background: rgba(5, 10, 5, 0.6);
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
  background: rgba(5, 10, 5, 0.7);
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
  background: rgba(5, 10, 5, 0.8);
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
  background: rgba(5, 10, 5, 0.92);
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
  display: none;
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
  background: rgba(255, 255, 255, 0.04);
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
  background: rgba(0, 255, 102, 0.08);
  border-color: rgba(0, 255, 102, 0.3);
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
  background: rgba(255, 255, 255, 0.04);
  cursor: pointer;
  font-size: 16px;
}

.emoji-btn:hover {
  background: rgba(0, 255, 102, 0.08);
  border-color: rgba(0, 255, 102, 0.3);
}

.info-icon {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  color: rgba(74, 222, 128, 0.8);
  cursor: help;
  transition: all 0.2s;
  flex-shrink: 0;
  border-radius: 50%;
  background: rgba(0, 255, 102, 0.08);
  z-index: 10001;
}

.info-icon:hover {
  color: var(--accent);
  background: rgba(0, 255, 102, 0.18);
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
  background: rgba(5, 10, 5, 0.99);
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
  color: #00FF66;
  display: block;
  margin-bottom: 4px;
}

.tooltip-text code {
  background: rgba(0, 255, 102, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
  color: #4ade80;
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
  border-top-color: rgba(5, 10, 5, 0.99);
}

.info-icon.tooltip-active {
  background: rgba(0, 255, 102, 0.2);
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
  background: rgba(5, 10, 5, 0.8);
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
  background: rgba(5, 10, 5, 0.92);
}

.flow-empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
  user-select: none;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.flow-empty-state .empty-state-icon {
  color: #10b981;
  opacity: 0.6;
  animation: empty-float 3s ease-in-out infinite;
}

.empty-state-title {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #e2e8f0;
  letter-spacing: 0.01em;
}

.empty-state-desc {
  margin: 0;
  font-size: 0.95rem;
  color: #94a3b8;
  line-height: 1.6;
}

.empty-state-desc strong {
  color: #10b981;
  font-weight: 600;
}

.empty-state-arrow {
  animation: empty-bounce 1.5s ease-in-out infinite;
  transform: rotate(180deg);
  margin-top: 4px;
  opacity: 0.7;
}

@keyframes empty-float {
  0%, 100% { transform: translateY(0px); opacity: 0.6; }
  50% { transform: translateY(-6px); opacity: 1; }
}

@keyframes empty-bounce {
  0%, 100% { transform: rotate(180deg) translateY(0px); }
  50% { transform: rotate(180deg) translateY(-6px); }
}

/* Botão Adicionar Gatilho pulsante quando canvas vazio */
.btn-trigger-pulse {
  border-color: #10b981 !important;
  color: #10b981 !important;
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.5);
  animation: trigger-pulse 2s ease-in-out infinite;
}

@keyframes trigger-pulse {
  0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.5); }
  50% { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
  100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
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
  border-color: #00FF66;
  background: linear-gradient(135deg, rgba(0, 255, 102, 0.10) 0%, rgba(74, 222, 128, 0.06) 100%);
}

.flow-node.node-type-message:hover {
  border-color: #4ade80;
  box-shadow: 0 8px 30px rgba(0, 255, 102, 0.2);
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
  background: rgba(0, 255, 102, 0.06);
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
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4), 0 0 20px rgba(0, 255, 102, 0.3);
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
  border-left-color: #00FF66;
  background: rgba(0, 255, 102, 0.06);
}

.msg-block-text:hover {
  background: rgba(0, 255, 102, 0.1);
  border-left-color: #4ade80;
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
  position: relative;
}

.flow-node-deleting-overlay {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(2px);
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  z-index: 10;
  color: #f87171;
  font-size: 0.8rem;
  font-weight: 500;
  letter-spacing: 0.01em;
}

.flow-node-deleting-overlay i {
  font-size: 1.1rem;
}

.flow-node.is-deleting {
  opacity: 0.7;
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

.btn-node-duplicate {
  background: transparent;
  border: none;
  color: var(--muted);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
  pointer-events: auto;
  transition: all 0.2s;
}

.btn-node-duplicate:hover {
  background: var(--accent-soft);
  color: var(--accent);
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
  background: radial-gradient(circle at top right, rgba(0, 255, 102, 0.08), transparent 45%),
    #0a0a0a;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 28px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.9);
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
  background: rgba(5, 10, 5, 0.92);
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
  background: rgba(0, 255, 102, 0.10);
  border-color: rgba(0, 255, 102, 0.5);
  color: #4ade80;
}

.trigger-nav-item.disabled {
  opacity: 0.4;
}

.trigger-main {
  background: rgba(5, 10, 5, 0.95);
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
  color: #4ade80;
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

.trigger-card:hover:not(.trigger-card--loading) {
  border-color: rgba(132, 204, 22, 0.6);
  transform: translateY(-2px);
}

.trigger-card--loading {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

.trigger-card-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: rgba(0, 255, 102, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4ade80;
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
  color: #4ade80;
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
  background: rgba(0, 255, 102, 0.08);
  border-color: rgba(0, 255, 102, 0.35);
  color: #4ade80;
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
  background: rgba(5, 10, 5, 0.92);
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
  background: rgba(5, 10, 5, 1);
}

.tag-dropdown-panel {
  margin-top: 8px;
  padding: 12px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: var(--radius-lg);
  background: rgba(5, 10, 5, 0.97);
  box-shadow: 0 12px 24px rgba(5, 10, 5, 0.6);
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
  background: rgba(5, 10, 5, 0.8);
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
  background: rgba(5, 10, 5, 0.8);
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
  background: rgba(0, 255, 102, 0.12);
  color: #4ade80;
  border: 1px solid rgba(0, 255, 102, 0.25);
}

.btn-toggle-opt.active i {
  color: #4ade80;
}

.btn-flow-hint {
  background: rgba(5, 10, 5, 0.5);
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
  background: rgba(5, 10, 5, 0.98);
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

/* Modal de conflito de keywords */
.kw-conflict-modal {
  max-width: 520px;
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}

.kw-conflict-subtitle {
  font-size: 0.82rem;
  color: #6b7280;
  margin: 6px 0 0;
  line-height: 1.5;
}
.kw-conflict-subtitle strong { color: #c4b5fd; }

.kw-conflict-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  padding-right: 4px;
  flex: 1;
}

.kw-conflict-row {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 12px;
  padding: 14px 16px;
}

.kw-conflict-original,
.kw-conflict-new {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.kw-conflict-label {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #4b5563;
}

.kw-chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  width: fit-content;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.kw-chip--conflict {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #f87171;
}

.kw-conflict-input {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 7px 10px;
  font-size: 0.85rem;
  color: #e5e7eb;
  outline: none;
  transition: border-color 0.2s;
  width: 100%;
  min-width: 0;
}
.kw-conflict-input:focus { border-color: rgba(139, 92, 246, 0.5); }
.kw-conflict-input--same {
  border-color: rgba(239, 68, 68, 0.4);
  color: #f87171;
}

.kw-conflict-hint {
  font-size: 0.75rem;
  color: #4b5563;
  padding: 10px 12px;
  background: rgba(255,255,255,0.02);
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.05);
  line-height: 1.5;
}

.kw-conflict-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.07);
  flex-shrink: 0;
}

.kw-btn-apply {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: rgba(0, 255, 102, 0.08);
  border: 1px solid rgba(0, 255, 102, 0.35);
  color: #4ade80;
  padding: 9px 18px;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.kw-btn-apply:hover:not(:disabled) {
  background: rgba(0, 255, 102, 0.15);
  border-color: rgba(0, 255, 102, 0.5);
}
.kw-btn-apply:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

/* Overlay de loading IA — padrão visual do sistema */
.ai-applying-overlay {
  position: absolute;
  inset: 0;
  z-index: 100;
  background: rgba(15, 17, 22, 0.82);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: all;
  cursor: not-allowed;
}

.ai-applying-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  background: rgba(24, 26, 35, 0.95);
  border: 1px solid rgba(139, 92, 246, 0.25);
  border-radius: 18px;
  padding: 32px 40px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(139,92,246,0.1);
  min-width: 280px;
  text-align: center;
}

.ai-applying-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.25), rgba(139, 92, 246, 0.05));
  border: 1px solid rgba(139, 92, 246, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: ai-pulse-ring 2s ease-in-out infinite;
}

.ai-applying-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #e9d5ff;
  margin: 0;
  letter-spacing: 0.01em;
}

.ai-applying-sub {
  font-size: 0.78rem;
  color: #6b7280;
  margin: 0;
}

/* Barra de progresso indeterminada */
.ai-applying-bar {
  width: 180px;
  height: 3px;
  border-radius: 99px;
  background: rgba(139, 92, 246, 0.12);
  overflow: hidden;
  margin-top: 4px;
}

.ai-applying-bar-fill {
  height: 100%;
  width: 45%;
  border-radius: 99px;
  background: linear-gradient(90deg, #7c3aed, #a78bfa, #7c3aed);
  background-size: 200% 100%;
  animation: ai-bar-slide 1.4s ease-in-out infinite;
}

@keyframes ai-bar-slide {
  0%   { transform: translateX(-120%); }
  100% { transform: translateX(340%); }
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
  flex-wrap: wrap;
  min-height: 56px;
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
  flex: 1;
  min-width: 0;
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
  background: rgba(0, 255, 102, 0.06);
  border: 1px solid rgba(0, 255, 102, 0.18);
  border-radius: 8px;
  margin-top: 12px;
  margin-bottom: 16px;
  color: #4ade80;
  font-size: 0.9375rem;
}

.bot-info-box i {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.bot-info-box strong {
  font-weight: 700;
  color: #00FF66;
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
  background: rgba(0, 255, 102, 0.06);
  border: 1px solid rgba(0, 255, 102, 0.18);
  border-radius: 8px;
  color: #4ade80;
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
  color: #00FF66;
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
  background: rgba(0, 255, 102, 0.06);
  border-radius: 8px;
  margin-top: 8px;
}

.condition-info i {
  color: #4ade80;
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

/* ==================== BLOCK PICKER ==================== */

.sidebar-section .sidebar-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #64748b;
  margin-bottom: 10px;
  display: block;
}

.sidebar-textarea {
  width: 100%;
  box-sizing: border-box;
  background: rgba(2, 8, 20, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 10px;
  color: #e2e8f0;
  font-size: 0.875rem;
  font-family: inherit;
  line-height: 1.6;
  padding: 12px 14px;
  resize: vertical;
  transition: border-color 0.2s;
  outline: none;
}

.sidebar-textarea:focus {
  border-color: rgba(34, 197, 94, 0.5);
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.08);
}

.sidebar-textarea::placeholder { color: #475569; }

/* Editor unificado: chips + textarea como um só controle */
.text-editor-unified {
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 10px;
  overflow: hidden;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.text-editor-unified:focus-within {
  border-color: rgba(34, 197, 94, 0.45);
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.07);
}

.tag-chips-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px;
  padding: 8px 10px;
  background: rgba(2, 8, 20, 0.6);
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.tag-chip-inline {
  background: rgba(34, 197, 94, 0.06);
  border: 1px solid rgba(34, 197, 94, 0.15);
  color: #4ade80;
  padding: 3px 9px;
  font-size: 0.71rem;
  font-weight: 600;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  font-family: inherit;
  line-height: 1.6;
}

.tag-chip-inline:hover {
  background: rgba(34, 197, 94, 0.16);
  border-color: rgba(34, 197, 94, 0.4);
  color: #86efac;
}

.text-editor-unified .sidebar-textarea {
  border: none;
  border-radius: 0;
  background: rgba(2, 8, 20, 0.45);
  box-shadow: none;
}

.text-editor-unified .sidebar-textarea:focus {
  border: none;
  box-shadow: none;
  outline: none;
}

/* Toolbar embutido no rodapé do editor */
.text-toolbar-embedded {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 7px 10px;
  background: rgba(2, 8, 20, 0.6);
  border-top: 1px solid rgba(148, 163, 184, 0.1);
  position: relative;
}

.text-toolbar-embedded .text-toolbar-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: #64748b;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  transition: background 0.15s, color 0.15s;
  flex-shrink: 0;
}

.text-toolbar-embedded .text-toolbar-btn:hover {
  background: rgba(34, 197, 94, 0.1);
  color: #4ade80;
}

.text-toolbar-embedded .text-toolbar-sep {
  width: 1px;
  height: 16px;
  background: rgba(148, 163, 184, 0.15);
  margin: 0 4px;
  flex-shrink: 0;
}

.text-toolbar-embedded .emoji-popover {
  position: absolute;
  bottom: calc(100% + 6px);
  left: 10px;
  background: #0f172a;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 10px;
  padding: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  width: 220px;
  z-index: 50;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

/* Botões de adicionar bloco */
.content-block-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 14px;
  background: rgba(2, 8, 20, 0.55);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.18s ease;
  text-align: left;
  margin-bottom: 6px;
  color: inherit;
}

.content-block-btn:hover {
  background: rgba(34, 197, 94, 0.07);
  border-color: rgba(34, 197, 94, 0.25);
  transform: translateX(2px);
}

.content-block-btn:last-child { margin-bottom: 0; }

.content-block-icon {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.18);
  color: #4ade80;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  flex-shrink: 0;
  transition: background 0.18s, box-shadow 0.18s;
}

.content-block-btn:hover .content-block-icon {
  background: rgba(34, 197, 94, 0.16);
  box-shadow: 0 0 10px rgba(34, 197, 94, 0.2);
}

.content-block-info { flex: 1; min-width: 0; }

.content-block-info h4 {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 2px;
  line-height: 1.3;
}

.content-block-info p {
  font-size: 0.72rem;
  color: #64748b;
  margin: 0;
  line-height: 1.35;
}

/* Grupo de mídias */
.media-blocks-group {
  margin-bottom: 6px;
}

.media-group-label {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #475569;
  padding: 0 2px;
  margin-bottom: 8px;
}

.media-group-label i { color: #4ade80; font-size: 0.75rem; }

.media-blocks-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.media-block-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 8px;
  background: rgba(2, 8, 20, 0.55);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.18s ease;
  color: inherit;
}

.media-block-btn:hover {
  background: rgba(34, 197, 94, 0.07);
  border-color: rgba(34, 197, 94, 0.25);
  transform: translateY(-2px);
}

.media-block-icon-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  transition: background 0.18s, box-shadow 0.18s;
}

.media-block-btn:hover .media-block-icon-wrapper {
  box-shadow: 0 0 12px rgba(34, 197, 94, 0.2);
}

.media-block-image .media-block-icon-wrapper {
  background: rgba(0, 255, 102, 0.08);
  border: 1px solid rgba(0, 255, 102, 0.18);
  color: #4ade80;
}

.media-block-audio .media-block-icon-wrapper {
  background: rgba(168, 85, 247, 0.12);
  border: 1px solid rgba(168, 85, 247, 0.2);
  color: #c084fc;
}

.media-block-video .media-block-icon-wrapper {
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #f87171;
}

.media-block-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: #94a3b8;
  text-align: center;
  line-height: 1;
}

.media-block-btn:hover .media-block-label { color: #e2e8f0; }

/* ─── Botão IA no header ─────────────────────────────────── */
.btn-ai-generate {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 8px;
  border: 1px solid rgba(139, 92, 246, 0.5);
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(167, 139, 250, 0.08));
  color: #c4b5fd;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s;
}
.btn-ai-generate:hover {
  border-color: rgba(139, 92, 246, 0.8);
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.28), rgba(167, 139, 250, 0.15));
  color: #e9d5ff;
  box-shadow: 0 0 12px rgba(139, 92, 246, 0.25);
}
.btn-ai-generate svg {
  flex-shrink: 0;
}

/* ─── Modal IA ───────────────────────────────────────────── */
.ai-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(4px);
  z-index: 9000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: ai-fade-in 0.18s ease;
}
@keyframes ai-fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}

.ai-modal {
  background: #1a1d23;
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 14px;
  width: 100%;
  max-width: 560px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(139, 92, 246, 0.1);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  animation: ai-slide-up 0.2s ease;
  position: relative;
  overflow: hidden;
}
@keyframes ai-slide-up {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

.ai-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
}
.ai-modal-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  font-weight: 700;
  color: #e9d5ff;
}
.ai-modal-title svg { color: #a78bfa; }
.ai-modal-close {
  width: 28px; height: 28px;
  border-radius: 6px;
  border: none;
  background: rgba(255,255,255,0.05);
  color: #888;
  font-size: 1.1rem;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s;
}
.ai-modal-close:hover:not(:disabled) { background: rgba(255,255,255,0.1); color: #ddd; }
.ai-modal-close:disabled { opacity: 0.4; cursor: not-allowed; }

.ai-modal-body {
  padding: 18px 20px;
  overflow-y: auto;
  flex: 1;
}

.ai-modal-hint {
  font-size: 0.82rem;
  color: #9ca3af;
  margin: 0 0 12px;
  line-height: 1.5;
}

/* Exemplos rápidos */
.ai-examples {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
  align-items: center;
}
.ai-examples-label {
  font-size: 0.75rem;
  color: #6b7280;
  flex-shrink: 0;
}
.ai-example-chip {
  padding: 4px 10px;
  border-radius: 20px;
  border: 1px solid rgba(139, 92, 246, 0.3);
  background: rgba(139, 92, 246, 0.08);
  color: #c4b5fd;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.15s;
}
.ai-example-chip:hover:not(:disabled) {
  border-color: rgba(139, 92, 246, 0.6);
  background: rgba(139, 92, 246, 0.15);
}
.ai-example-chip:disabled { opacity: 0.5; cursor: not-allowed; }

/* Textarea */
.ai-prompt-input {
  width: 100%;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 0.85rem;
  padding: 12px 14px;
  resize: vertical;
  min-height: 100px;
  line-height: 1.6;
  font-family: inherit;
  transition: border-color 0.15s;
  box-sizing: border-box;
}
.ai-prompt-input:focus {
  outline: none;
  border-color: rgba(139, 92, 246, 0.5);
  background: rgba(255,255,255,0.06);
}
.ai-prompt-input:disabled { opacity: 0.5; cursor: not-allowed; }

.ai-prompt-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
}
.ai-char-count { font-size: 0.72rem; color: #6b7280; }
.ai-char-count--warn { color: #f59e0b; }
.ai-hint-shortcut { font-size: 0.72rem; color: #4b5563; }

/* Erro */
.ai-error {
  margin-top: 12px;
  display: flex;
  align-items: flex-start;
  gap: 7px;
  padding: 10px 12px;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: 8px;
  font-size: 0.8rem;
  color: #fca5a5;
  line-height: 1.5;
}
.ai-error svg { flex-shrink: 0; margin-top: 1px; }

/* Resultado */
.ai-result-header { margin-bottom: 14px; }
.ai-result-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.25);
  border-radius: 20px;
  color: #86efac;
  font-size: 0.78rem;
  font-weight: 600;
}

.ai-result-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
  padding: 12px 14px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 8px;
}
.ai-result-row {
  display: flex;
  gap: 10px;
  font-size: 0.82rem;
}
.ai-result-label { color: #6b7280; min-width: 80px; flex-shrink: 0; }
.ai-result-value { color: #d1d5db; }

/* Steps preview */
.ai-steps-preview {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 14px;
}
.ai-step-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 10px;
  background: rgba(255,255,255,0.025);
  border-radius: 6px;
  font-size: 0.8rem;
}
.ai-step-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  flex-shrink: 0;
}
.ai-step-badge--trigger  { background: rgba(245,158,11,0.15); color: #fbbf24; }
.ai-step-badge--message  { background: rgba(59,130,246,0.15); color: #93c5fd; }
.ai-step-badge--action   { background: rgba(16,185,129,0.15); color: #6ee7b7; }
.ai-step-badge--condition{ background: rgba(239,68,68,0.15);  color: #fca5a5; }
.ai-step-badge--wait     { background: rgba(107,114,128,0.15);color: #d1d5db; }
.ai-step-badge--randomizer{ background: rgba(168,85,247,0.15);color: #d8b4fe; }
.ai-step-label { color: #9ca3af; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.ai-apply-warning {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  font-size: 0.78rem;
  color: #d97706;
  line-height: 1.5;
  margin: 0;
}
.ai-apply-warning svg { flex-shrink: 0; margin-top: 1px; color: #f59e0b; }

/* Loading overlay */
.ai-loading {
  position: absolute;
  inset: 0;
  background: rgba(15, 17, 22, 0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  z-index: 10;
  backdrop-filter: blur(3px);
}
.ai-loading-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 0 24px;
  width: 100%;
  max-width: 360px;
}

/* Ícone pulsante */
.ai-loading-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.25), rgba(139, 92, 246, 0.05));
  border: 1px solid rgba(139, 92, 246, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: ai-pulse-ring 2s ease-in-out infinite;
}
@keyframes ai-pulse-ring {
  0%, 100% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.4); }
  50%       { box-shadow: 0 0 0 10px rgba(139, 92, 246, 0); }
}
.ai-spinner {
  animation: ai-spin 2s linear infinite;
  color: #a78bfa;
}
@keyframes ai-spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

/* Etapas */
.ai-loading-steps {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}
.ai-loading-step {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.82rem;
  transition: all 0.3s ease;
}
.ai-loading-step--done .ai-loading-step-label  { color: #6ee7b7; }
.ai-loading-step--active .ai-loading-step-label { color: #e9d5ff; font-weight: 600; }
.ai-loading-step--pending .ai-loading-step-label { color: #374151; }

.ai-loading-step-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s ease;
}
.ai-loading-step--done   .ai-loading-step-icon { background: rgba(16, 185, 129, 0.2); color: #6ee7b7; }
.ai-loading-step--active .ai-loading-step-icon { background: rgba(139, 92, 246, 0.2); color: #c4b5fd; }
.ai-loading-step--pending .ai-loading-step-icon { background: rgba(255,255,255,0.04); color: #374151; }

.ai-step-spin { animation: ai-spin 1s linear infinite; }
.ai-step-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
  display: block;
}

/* Footer */
.ai-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 14px 20px;
  border-top: 1px solid rgba(255,255,255,0.07);
}
.ai-btn-cancel {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.1);
  background: transparent;
  color: #9ca3af;
  font-size: 0.83rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}
.ai-btn-cancel:hover { background: rgba(255,255,255,0.05); color: #e2e8f0; }
.ai-btn-generate {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #7c3aed, #6d28d9);
  color: #fff;
  font-size: 0.83rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.18s;
  box-shadow: 0 4px 14px rgba(124, 58, 237, 0.35);
}
.ai-btn-generate:hover:not(:disabled) {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  box-shadow: 0 6px 20px rgba(124, 58, 237, 0.45);
  transform: translateY(-1px);
}
.ai-btn-generate:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
.ai-btn-apply {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #059669, #047857);
  color: #fff;
  font-size: 0.83rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.18s;
  box-shadow: 0 4px 14px rgba(5, 150, 105, 0.35);
}
.ai-btn-apply:hover {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 6px 20px rgba(5, 150, 105, 0.45);
  transform: translateY(-1px);
}
</style>
