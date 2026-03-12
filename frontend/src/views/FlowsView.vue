<template>
  <AppLayout>
    <div class="card flows-container">
      <div class="flows-header">
        <div style="display: flex; align-items: center; gap: 12px;">
          <h2 class="flows-title">Fluxos de Automação</h2>
          <span
            v-if="planUsage && planUsage.limit !== null"
            class="plan-usage-badge"
            :class="{ 'plan-usage-badge--full': flows.length >= planUsage.limit }"
          >
            {{ flows.length }}/{{ planUsage.limit }} fluxos
            <router-link v-if="flows.length >= planUsage.limit" to="/settings" class="plan-usage-upgrade">Upgrade</router-link>
          </span>
        </div>
        <button class="btn btn-primary" @click="openCreateModal" :disabled="loading">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Criar Fluxo
        </button>
      </div>

      <!-- Card de Configuração de Fallback -->
      <div class="fallback-config-card">
        <div class="fallback-header">
          <div class="fallback-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              <path d="M9 10h.01M15 10h.01M9.5 14.5s1.5 2 3.5 2 3.5-2 3.5-2"/>
            </svg>
          </div>
          <div class="fallback-title-section">
            <h3 class="fallback-title">Resposta Quando Não Há Match</h3>
            <p class="fallback-subtitle">Configure o que acontece quando uma mensagem não corresponde a nenhuma keyword</p>
          </div>
        </div>

        <div class="fallback-options">
          <div 
            v-for="option in fallbackOptions.filter(o => !o.disabled)" 
            :key="option.value"
            class="fallback-option"
            :class="{ 
              'selected': fallbackConfig.type === option.value
            }"
            @click="selectFallback(option.value)"
          >
            <div class="option-radio">
              <div class="radio-outer">
                <div v-if="fallbackConfig.type === option.value" class="radio-inner"></div>
              </div>
            </div>
            <div class="option-content">
              <div class="option-header">
                <span class="option-icon-wrapper" v-html="option.icon"></span>
                <span class="option-name">{{ option.label }}</span>
                <span v-if="option.badge" class="option-badge" :class="`badge-${option.badgeType}`">
                  {{ option.badge }}
                </span>
              </div>
              <p class="option-description">{{ option.description }}</p>
            </div>
          </div>
        </div>

        <div v-if="fallbackConfig.type !== fallbackConfigOriginal.type" class="fallback-actions">
          <button class="btn btn-secondary btn-sm" @click="cancelFallbackChanges">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
            Cancelar
          </button>
          <button class="btn btn-primary btn-sm" @click="saveFallbackConfig" :disabled="savingFallback">
            <svg v-if="!savingFallback" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            {{ savingFallback ? 'Salvando...' : 'Salvar Configuração' }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="flows-loading">
        <div class="loading-spinner"></div>
        <span>Carregando fluxos...</span>
      </div>

      <div v-else-if="flows.length === 0" class="flows-empty-state">
        <div class="empty-state-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
        </div>
        <h3 class="empty-state-title">Nenhum fluxo criado</h3>
        <p class="empty-state-description">
          Comece criando seu primeiro fluxo de automação clicando no botão acima
        </p>
      </div>

      <div v-else class="flows-table-wrapper">
        <table class="table flows-table">
          <thead>
            <tr>
              <th>Nome do Fluxo</th>
              <th>Sistema</th>
              <th>Gatilho</th>
              <th>Keywords</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in flows" :key="f.id">
              <td>
                <div style="font-weight: 600; color: var(--text-primary);">{{ f.name }}</div>
                <div v-if="f.description" style="color: var(--muted); font-size: 0.8125rem; margin-top: 2px;">
                  {{ f.description }}
                </div>
              </td>
              <td>
                <div class="system-badge" :class="`system-${getFlowSystem(f)}`">
                  <i :class="getSystemIcon(f)"></i>
                  <span>{{ getSystemLabel(f) }}</span>
                </div>
                <!-- Aviso se o bot está inativo -->
                <div v-if="!isChannelActive(f.channel_id)" class="bot-inactive-warning">
                  <i class="fa-solid fa-exclamation-triangle"></i>
                  <span>Bot inativo</span>
                </div>
              </td>
              <td>
                <span class="trigger-badge">{{ getTriggerLabel(f) }}</span>
              </td>
              <td>
                <div class="keywords-container">
                  <span 
                    v-for="(keyword, index) in f.keywords" 
                    :key="index"
                    class="keyword-badge"
                    :style="{ backgroundColor: getKeywordColor(keyword), color: getKeywordTextColor(keyword) }"
                  >
                    {{ keyword }}
                  </span>
                  <span v-if="!f.keywords || f.keywords.length === 0" class="no-keywords">
                    Sem keywords
                  </span>
                </div>
              </td>
              <td>
                <span class="badge" :class="f.is_active ? 'badge-success' : 'badge-muted'">
                  {{ f.is_active ? 'Ativo' : 'Inativo' }}
                </span>
              </td>
              <td>
                <div class="table-actions">
                  <!-- Toggle Switch Ativar/Desativar -->
                  <div class="toggle-switch-wrapper">
                    <label class="toggle-switch" :title="f.is_active ? 'Desativar fluxo' : 'Ativar fluxo'">
                      <input 
                        type="checkbox" 
                        :checked="f.is_active"
                        @click.prevent="openToggleConfirmModal(f)"
                      />
                      <span class="toggle-slider"></span>
                    </label>
                  </div>

                  <!-- Botão Editar -->
                  <button class="btn btn-ghost btn-sm" @click="goToFlow(f.id)">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                    Editar
                  </button>
                  <button class="btn btn-ghost btn-sm" @click="duplicateFlow(f.id)">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                    </svg>
                  </button>
                  <button class="btn btn-ghost btn-sm" @click="openDeleteModal(f)" style="color: #ef4444;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="3 6 5 6 21 6"/>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal de Criação de Fluxo -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal-content create-flow-modal" @click.stop>
        <div class="modal-header cfm-header">
          <div class="cfm-title-group">
            <div class="cfm-icon"><i class="fa-solid fa-bolt"></i></div>
            <div>
              <h3 class="modal-title">Novo Fluxo</h3>
              <p class="cfm-subtitle">Configure as informações básicas</p>
            </div>
          </div>
          <button class="modal-close" @click="showCreateModal = false">
            <i class="fa-solid fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Nome do Fluxo *</label>
            <input
              v-model="newFlow.name"
              type="text"
              class="form-input"
              placeholder="Ex: Boas-vindas, Suporte, Vendas..."
              @keyup.enter="createNewFlow"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Bot / Canal *</label>
            <div class="cs-list">
              <button
                v-for="channel in availableChannels"
                :key="channel.id"
                :class="['cs-item', { 'cs-item--active': newFlow.channel_id === channel.id }]"
                @click="newFlow.channel_id = channel.id"
                type="button"
              >
                <div class="cs-item-icon" :style="{ background: getChannelColor(channel.type) }">
                  <i :class="getChannelIcon(channel.type)"></i>
                </div>
                <div class="cs-item-body">
                  <span class="cs-item-name">{{ channel.name }}</span>
                  <span class="cs-item-meta">{{ getChannelTypeName(channel.type) }}</span>
                </div>
                <span :class="['cs-item-badge', channel.is_active ? 'cs-badge--on' : 'cs-badge--off']">{{ channel.is_active ? 'Ativo' : 'Inativo' }}</span>
                <div class="cs-item-radio">
                  <i v-if="newFlow.channel_id === channel.id" class="fa-solid fa-circle-check"></i>
                  <i v-else class="fa-regular fa-circle"></i>
                </div>
              </button>

              <div v-if="availableChannels.length === 0" class="cs-empty">
                <i class="fa-brands fa-telegram"></i>
                <span>Nenhum bot ativo. Vá em <router-link to="/settings">Configurações → Telegram</router-link> para adicionar um.</span>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Descrição (opcional)</label>
            <textarea
              v-model="newFlow.description"
              class="form-input"
              rows="3"
              placeholder="Descreva o objetivo deste fluxo..."
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showCreateModal = false">
            Cancelar
          </button>
          <button
            class="btn btn-primary"
            @click="createNewFlow"
            :disabled="!newFlow.name || !newFlow.channel_id || creating"
          >
            <i class="fa-solid fa-plus"></i>
            {{ creating ? 'Criando...' : 'Criar Fluxo' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmação para Toggle (Ativar/Desativar) -->
    <div v-if="showToggleModal" class="modal-overlay" @click="cancelToggle">
      <div class="modal-content confirm-modal" @click.stop>
        <div class="modal-header">
          <div class="confirm-icon" :class="flowToToggle?.is_active ? 'icon-warning' : 'icon-success'">
            <svg v-if="flowToToggle?.is_active" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            <svg v-else width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <h3 class="modal-title">
            {{ flowToToggle?.is_active ? 'Desativar Fluxo?' : 'Ativar Fluxo?' }}
          </h3>
          <button class="modal-close" @click="cancelToggle">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <div class="flow-info-box">
            <div class="flow-info-label">Fluxo:</div>
            <div class="flow-info-value">{{ flowToToggle?.name }}</div>
          </div>

          <p v-if="flowToToggle?.is_active" class="confirm-message">
            Ao desativar este fluxo, ele <strong>não responderá mais</strong> às mensagens dos usuários até que seja reativado.
          </p>
          <p v-else class="confirm-message">
            Ao ativar este fluxo, ele voltará a <strong>responder automaticamente</strong> às mensagens que corresponderem às suas keywords.
          </p>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="cancelToggle" :disabled="toggling">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
            Cancelar
          </button>
          <button 
            class="btn"
            :class="flowToToggle?.is_active ? 'btn-warning' : 'btn-success'"
            @click="confirmToggle"
            :disabled="toggling"
          >
            <svg v-if="!toggling" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <span v-if="toggling">Processando...</span>
            <span v-else>{{ flowToToggle?.is_active ? 'Desativar' : 'Ativar' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmação 1: Aviso Inicial -->
    <div v-if="showDeleteModal1" class="modal-overlay" @click="cancelDelete">
      <div class="modal-content delete-modal" @click.stop>
        <div class="modal-header delete-header">
          <div class="delete-icon-warning">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <h3 class="modal-title">Excluir Fluxo?</h3>
          <button class="modal-close" @click="cancelDelete">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <p class="delete-warning-text">
            Você está prestes a excluir o fluxo:
          </p>
          <div class="delete-flow-info">
            <strong>{{ flowToDelete?.name }}</strong>
          </div>
          <div class="delete-warning-box">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <div>
              <strong>Atenção:</strong> Esta ação não pode ser desfeita.<br>
              Todos os steps, conexões e configurações serão perdidos permanentemente.
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="cancelDelete">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
            Cancelar
          </button>
          <button class="btn btn-danger" @click="showDeleteModal2 = true; showDeleteModal1 = false">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            Continuar com a Exclusão
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmação 2: Confirmação Crítica -->
    <div v-if="showDeleteModal2" class="modal-overlay" @click="cancelDelete">
      <div class="modal-content delete-modal critical" @click.stop>
        <div class="modal-header delete-header critical">
          <div class="delete-icon-critical">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
          </div>
          <h3 class="modal-title">Confirmação Crítica</h3>
          <button class="modal-close" @click="cancelDelete">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <p class="delete-critical-text">
            Para confirmar a exclusão permanente, digite o nome do fluxo exatamente como aparece abaixo:
          </p>
          <div class="delete-flow-name-box">
            <code>{{ flowToDelete?.name }}</code>
          </div>
          <div class="form-group">
            <label class="form-label">Digite o nome do fluxo:</label>
            <input
              v-model="deleteConfirmation"
              type="text"
              class="form-input"
              :class="{ 'input-error': deleteConfirmation && deleteConfirmation !== flowToDelete?.name }"
              placeholder="Digite o nome exato do fluxo..."
              @keyup.enter="deleteConfirmation === flowToDelete?.name && confirmDelete()"
              autofocus
            />
            <span v-if="deleteConfirmation && deleteConfirmation !== flowToDelete?.name" class="input-error-message">
              ❌ O nome não corresponde
            </span>
            <span v-if="deleteConfirmation === flowToDelete?.name" class="input-success-message">
              ✅ Nome correto
            </span>
          </div>
          <div class="delete-final-warning">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <strong>ÚLTIMA CHANCE:</strong> Esta ação é IRREVERSÍVEL!
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="cancelDelete">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Voltar
          </button>
          <button
            class="btn btn-danger"
            @click="confirmDelete"
            :disabled="deleteConfirmation !== flowToDelete?.name || deleting"
          >
            <svg v-if="!deleting" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              <line x1="10" y1="11" x2="10" y2="17"/>
              <line x1="14" y1="11" x2="14" y2="17"/>
            </svg>
            {{ deleting ? 'Excluindo...' : 'EXCLUIR PERMANENTEMENTE' }}
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { listFlows, createFlow, createFlowStep, deleteFlow as deleteFlowAPI, listFlowSteps, updateFlow } from '@/api/flows'
import { getMySubscription } from '@/api/subscription'
import { listChannels } from '@/api/channels'
import { useToast } from '@/composables/useToast'

const flows = ref([])
const availableChannels = ref([]) // Apenas canais ativos (para criar fluxos)
const allChannels = ref([]) // Todos os canais (para verificar status)
const planUsage = ref(null) // { limit: number | null } — limite de fluxos do plano
const loading = ref(false)
const creating = ref(false)
const showCreateModal = ref(false)
const router = useRouter()
const toast = useToast()

// Estados para deletar
const showDeleteModal1 = ref(false)
const showDeleteModal2 = ref(false)
const flowToDelete = ref(null)
const deleteConfirmation = ref('')
const deleting = ref(false)

// Estados para toggle de ativação/desativação
const showToggleModal = ref(false)
const flowToToggle = ref(null)
const toggling = ref(false)

// Estados para configuração de fallback
const fallbackConfig = ref({
  type: 'ignore' // 'ignore', 'ai', 'fixed_message', 'specific_flow'
})
const fallbackConfigOriginal = ref({
  type: 'ignore'
})
const savingFallback = ref(false)

const fallbackOptions = [
  {
    value: 'ignore',
    label: 'Ignorar',
    icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"/>
      <line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/>
    </svg>`,
    description: 'Não responde quando não houver match com keywords',
    disabled: false
  },
  {
    value: 'ai',
    label: 'Responder com IA',
    icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"/>
      <circle cx="9" cy="16" r="1"/>
      <circle cx="15" cy="16" r="1"/>
    </svg>`,
    description: 'Usa inteligência artificial para gerar respostas contextuais (em breve)',
    badge: 'Em Breve',
    badgeType: 'info',
    disabled: true
  },
  {
    value: 'fixed_message',
    label: 'Mensagem Fixa',
    icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      <line x1="9" y1="10" x2="15" y2="10"/>
      <line x1="9" y1="14" x2="13" y2="14"/>
    </svg>`,
    description: 'Envia uma mensagem pré-definida quando não houver match',
    disabled: true,
    badge: 'Em Breve',
    badgeType: 'muted'
  },
  {
    value: 'specific_flow',
    label: 'Executar Fluxo Específico',
    icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polyline points="23 4 23 10 17 10"/>
      <polyline points="1 20 1 14 7 14"/>
      <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
    </svg>`,
    description: 'Direciona para um fluxo padrão quando não houver match',
    disabled: true,
    badge: 'Em Breve',
    badgeType: 'muted'
  }
]

const newFlow = ref({
  name: '',
  channel_id: null,
  description: ''
})

const availableSystems = [
  {
    id: 'telegram',
    label: 'Telegram',
    icon: 'fa-brands fa-telegram',
    color: 'linear-gradient(135deg, #229ED9 0%, #1E88E5 100%)',
    description: 'Crie automações para o Telegram'
  },
]


const loadChannels = async () => {
  try {
    allChannels.value = await listChannels()
    // Filtrar apenas canais ativos para criação de fluxos
    availableChannels.value = allChannels.value.filter(ch => ch.is_active)
    
    if (allChannels.value.length > 0 && availableChannels.value.length === 0) {
      console.warn('⚠️ Existem canais, mas nenhum está ativo')
    }
  } catch (error) {
    console.error('Erro ao carregar canais:', error)
  }
}

const fetchFlows = async () => {
  loading.value = true
  try {
    // Carregar canais se ainda não foram carregados
    if (availableChannels.value.length === 0) {
      await loadChannels()
    }
    
    const flowsList = await listFlows()
    
    // Para cada fluxo, buscar os steps e extrair as keywords
    const flowsWithKeywords = await Promise.all(
      flowsList.map(async (flow) => {
        try {
          const steps = await listFlowSteps(flow.id)
          const triggerStep = steps.find(s => s.type === 'trigger')
          
          let keywords = []
          if (triggerStep && triggerStep.config) {
            const config = typeof triggerStep.config === 'string' 
              ? JSON.parse(triggerStep.config) 
              : triggerStep.config
            
            if (config.keywords && Array.isArray(config.keywords)) {
              keywords = config.keywords.map(kw => 
                typeof kw === 'string' ? kw : kw.text || ''
              ).filter(k => k)
            }
          }
          
          return {
            ...flow,
            keywords
          }
        } catch (error) {
          console.error(`Erro ao buscar keywords do fluxo ${flow.id}:`, error)
          return {
            ...flow,
            keywords: []
          }
        }
      })
    )
    
    flows.value = flowsWithKeywords
    console.log('Fluxos carregados com keywords:', flows.value)
  } catch (e) {
    console.error(e)
    toast.error('Erro ao carregar fluxos')
  } finally {
    loading.value = false
  }
}

const openCreateModal = async () => {
  // Garantir que os canais estão carregados
  if (availableChannels.value.length === 0) {
    await loadChannels()
  }
  
  showCreateModal.value = true
}

const createNewFlow = async () => {
  if (!newFlow.value.name || !newFlow.value.channel_id) {
    toast.warning('Preencha o nome e selecione um bot/canal')
    return
  }

  creating.value = true
  try {
    // Buscar o canal selecionado para pegar o tipo
    const selectedChannel = availableChannels.value.find(c => c.id === newFlow.value.channel_id)
    const channelType = selectedChannel?.type || 'telegram'
    
    const triggerConfig = {
      system: channelType
    }

    const flow = await createFlow({
      tenant_id: 1,
      channel_id: newFlow.value.channel_id,
      name: newFlow.value.name,
      description: newFlow.value.description || `Fluxo de automação`,
      trigger_type: 'manual',
      trigger_config: triggerConfig
    })

    // Criar step inicial de boas-vindas
    await createFlowStep(flow.id, {
      type: 'message',
      order_index: 1,
      config: { text: `Olá! 👋 Bem-vindo ao ${newFlow.value.name}` }
    })

    await fetchFlows()
    
    // Resetar form e fechar modal
    newFlow.value = { name: '', channel_id: null, description: '' }
    showCreateModal.value = false
    
    // Redirecionar para edição do fluxo
    router.push(`/flows/${flow.id}`)
  } catch (e) {
    console.error(e)
    // Tratar limite de plano (403 PLAN_LIMIT_EXCEEDED)
    const detail = e?.response?.data?.detail
    if (e?.response?.status === 403 && detail?.code === 'PLAN_LIMIT_EXCEEDED') {
      toast.error(
        `Limite de fluxos atingido (${detail.current}/${detail.limit}). ` +
        `Faça upgrade para o plano Pro para criar mais fluxos.`
      )
    } else {
      toast.error('Erro ao criar fluxo')
    }
  } finally {
    creating.value = false
  }
}

const getFlowSystem = (flow) => {
  try {
    const config = typeof flow.trigger_config === 'string' 
      ? JSON.parse(flow.trigger_config) 
      : flow.trigger_config || {}
    return config.default_for || 'manual'
  } catch (e) {
    return 'manual'
  }
}

const getChannelIcon = (channelType) => {
  const icons = {
    telegram: 'fa-brands fa-telegram',
    default: 'fa-solid fa-message'
  }
  return icons[channelType] || icons.default
}

const getChannelColor = (channelType) => {
  const colors = {
    telegram: 'linear-gradient(135deg, #0088cc 0%, #229ED9 100%)',
    default: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)'
  }
  return colors[channelType] || colors.default
}

const getChannelTypeName = (channelType) => {
  const names = {
    telegram: 'Telegram',
    default: 'Chat'
  }
  return names[channelType] || names.default
}

const getSystemIcon = (flow) => {
  const system = getFlowSystem(flow)
  const icons = {
    telegram: 'fa-brands fa-telegram',
    manual: 'fa-solid fa-cog'
  }
  return icons[system] || icons.manual
}

const getSystemLabel = (flow) => {
  // Se o flow tem channel_id, buscar o nome do canal específico
  if (flow.channel_id) {
    const channel = availableChannels.value.find(c => c.id === flow.channel_id)
    if (channel) {
      return channel.name
    }
  }
  
  // Fallback para sistema genérico
  const system = getFlowSystem(flow)
  const labels = {
    telegram: 'Telegram'
  }
  return labels[system] || system
}

const isChannelActive = (channelId) => {
  if (!channelId) return true
  
  // Buscar em todos os canais (não apenas nos ativos)
  const channel = allChannels.value.find(c => c.id === channelId)
  return channel ? channel.is_active : false
}

const goToFlow = (id) => {
  router.push(`/flows/${id}`)
}

const duplicateFlow = (id) => {
  toast.info('Funcionalidade em desenvolvimento')
}

// Função para abrir modal de confirmação do toggle
const openToggleConfirmModal = (flow) => {
  flowToToggle.value = flow
  showToggleModal.value = true
}

const cancelToggle = () => {
  showToggleModal.value = false
  flowToToggle.value = null
  toggling.value = false
}

const confirmToggle = async () => {
  if (!flowToToggle.value) return

  const newStatus = !flowToToggle.value.is_active
  toggling.value = true

  try {
    await updateFlow(flowToToggle.value.id, { is_active: newStatus })
    
    // Atualizar o status localmente
    flowToToggle.value.is_active = newStatus
    
    toast.success(`Fluxo ${newStatus ? 'ativado' : 'desativado'} com sucesso!`)
    
    // Fechar modal
    cancelToggle()
  } catch (error) {
    console.error('Erro ao alterar status do fluxo:', error)
    toast.error(`Erro ao ${newStatus ? 'ativar' : 'desativar'} fluxo`)
    toggling.value = false
  }
}

// Funções de deletar com dupla confirmação
const openDeleteModal = (flow) => {
  flowToDelete.value = flow
  deleteConfirmation.value = ''
  showDeleteModal1.value = true
}

const cancelDelete = () => {
  showDeleteModal1.value = false
  showDeleteModal2.value = false
  flowToDelete.value = null
  deleteConfirmation.value = ''
}

const confirmDelete = async () => {
  if (deleteConfirmation.value !== flowToDelete.value?.name) {
    toast.error('O nome do fluxo não corresponde!')
    return
  }
  
  deleting.value = true
  
  try {
    await deleteFlowAPI(flowToDelete.value.id)
    toast.success(`Fluxo "${flowToDelete.value.name}" excluído com sucesso!`)
    
    // Remover da lista
    flows.value = flows.value.filter(f => f.id !== flowToDelete.value.id)
    
    // Fechar modais
    cancelDelete()
  } catch (error) {
    console.error('Erro ao excluir fluxo:', error)
    toast.error('Erro ao excluir fluxo')
  } finally {
    deleting.value = false
  }
}

const formatTrigger = (type) => {
  const types = {
    manual: 'Manual',
    message: 'Mensagem',
    command: 'Comando',
    event: 'Evento'
  }
  return types[type] || type
}

const getTriggerLabel = (flow) => {
  if (flow.trigger_type === 'message') return 'Qualquer Msg'
  if (flow.trigger_type === 'command') return 'Comando'
  if (flow.trigger_type === 'event') return 'Evento'
  if (flow.keywords && flow.keywords.length > 0) return 'Keyword'
  return 'Manual'
}

// Função para gerar cor baseada na keyword (hash consistente)
const getKeywordColor = (keyword) => {
  if (!keyword) return '#e5e7eb'
  
  // Cores vibrantes e distintas
  const colors = [
    '#EF4444', // Vermelho
    '#F59E0B', // Laranja
    '#10B981', // Verde
    '#3B82F6', // Azul
    '#8B5CF6', // Roxo
    '#EC4899', // Rosa
    '#14B8A6', // Teal
    '#F97316', // Laranja escuro
    '#06B6D4', // Ciano
    '#6366F1', // Indigo
    '#84CC16', // Lima
    '#D946EF', // Fúcsia
  ]
  
  // Hash simples da string
  let hash = 0
  for (let i = 0; i < keyword.length; i++) {
    hash = keyword.charCodeAt(i) + ((hash << 5) - hash)
  }
  
  const index = Math.abs(hash) % colors.length
  return colors[index]
}

// Função para determinar cor do texto (branco ou preto) baseado no background
const getKeywordTextColor = (keyword) => {
  const bgColor = getKeywordColor(keyword)
  // Todas as cores escolhidas ficam melhores com texto branco
  return '#FFFFFF'
}

// Funções de configuração de fallback
const selectFallback = (type) => {
  fallbackConfig.value.type = type
}

const cancelFallbackChanges = () => {
  fallbackConfig.value = { ...fallbackConfigOriginal.value }
}

const saveFallbackConfig = async () => {
  savingFallback.value = true
  
  try {
    // TODO: Chamar API para salvar configuração no tenant/channel
    // await saveTenantConfig({ fallback: fallbackConfig.value })
    
    // Simulação por enquanto
    await new Promise(resolve => setTimeout(resolve, 500))
    
    fallbackConfigOriginal.value = { ...fallbackConfig.value }
    toast.success('Configuração salva com sucesso!')
  } catch (error) {
    console.error('Erro ao salvar configuração:', error)
    toast.error('Erro ao salvar configuração')
  } finally {
    savingFallback.value = false
  }
}

const loadFallbackConfig = async () => {
  try {
    // TODO: Carregar configuração do tenant/channel
    // const config = await getTenantConfig()
    // fallbackConfig.value = config.fallback || { type: 'ignore' }
    
    // Por enquanto, mantém o padrão
    fallbackConfig.value = { type: 'ignore' }
    fallbackConfigOriginal.value = { ...fallbackConfig.value }
  } catch (error) {
    console.error('Erro ao carregar configuração:', error)
  }
}

onMounted(async () => {
  fetchFlows()
  loadFallbackConfig()
  try {
    const sub = await getMySubscription()
    const maxFlows = sub?.plan?.max_flows ?? null
    planUsage.value = { limit: maxFlows }
  } catch (e) {
    // Falha silenciosa — badge simplesmete não aparece
    console.warn('Não foi possível carregar uso do plano:', e)
  }
})
</script>

<style scoped>
/* Badge de uso do plano no header */
.plan-usage-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-muted);
  white-space: nowrap;
}

.plan-usage-badge--full {
  background: rgba(234, 179, 8, 0.12);
  border-color: rgba(234, 179, 8, 0.35);
  color: #ca8a04;
}

.plan-usage-upgrade {
  color: #000;
  font-weight: 700;
  text-decoration: none;
  font-size: 0.75rem;
  background: #00FF66;
  border: 1px solid #00FF66;
  padding: 1px 8px;
  border-radius: 6px;
  transition: background 0.2s;
}

.plan-usage-upgrade:hover {
  background: #00cc52;
  border-color: #00cc52;
}

/* Keywords na tabela */
.keywords-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.keyword-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 600;
  white-space: nowrap;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.keyword-badge:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.no-keywords {
  color: var(--muted);
  font-size: 0.8125rem;
  font-style: italic;
}

/* Trigger badge na tabela */
.trigger-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(0, 255, 102, 0.08);
  border: 1px solid rgba(0, 255, 102, 0.2);
  color: #00FF66;
  white-space: nowrap;
  letter-spacing: 0.2px;
}

/* Card de Configuração de Fallback */
.fallback-config-card {
  background: rgba(0, 255, 102, 0.03);
  border: 1px solid rgba(0, 255, 102, 0.12);
  border-radius: 12px;
  padding: 20px 24px;
  margin: 16px 20px 0 20px;
}

.fallback-header {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.fallback-icon {
  width: 44px;
  height: 44px;
  background: rgba(0, 255, 102, 0.12);
  border: 1px solid rgba(0, 255, 102, 0.25);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00FF66;
  flex-shrink: 0;
}

.fallback-title-section {
  flex: 1;
}

.fallback-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.fallback-subtitle {
  font-size: 0.875rem;
  color: var(--muted);
  margin: 0;
}

.fallback-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}

.fallback-option {
  background: #0a0a0a;
  border: 1.5px solid rgba(255,255,255,0.07);
  border-radius: 10px;
  padding: 14px 16px;
  display: flex;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.fallback-option:hover {
  border-color: rgba(0, 255, 102, 0.35);
  background: rgba(0, 255, 102, 0.04);
}

.fallback-option.selected {
  border-color: #00FF66;
  background: rgba(0, 255, 102, 0.06);
  box-shadow: 0 0 0 3px rgba(0, 255, 102, 0.08);
}

.option-radio {
  flex-shrink: 0;
  padding-top: 2px;
}

.radio-outer {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.fallback-option.selected .radio-outer {
  border-color: #00FF66;
}

.radio-inner {
  width: 10px;
  height: 10px;
  background: #00FF66;
  border-radius: 50%;
  animation: radioScale 0.2s ease-out;
}

@keyframes radioScale {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

.option-content {
  flex: 1;
}

.option-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.option-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  color: #00FF66;
}

.fallback-option.selected .option-icon-wrapper {
  color: #00FF66;
}

.option-icon-wrapper svg {
  width: 20px;
  height: 20px;
}

.option-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9375rem;
}

.option-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-info {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.badge-muted {
  background: rgba(156, 163, 175, 0.1);
  color: #9ca3af;
}

.option-description {
  font-size: 0.8125rem;
  color: var(--muted);
  margin: 0;
  line-height: 1.5;
}

.fallback-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 255, 102, 0.1);
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

/* Modais de Delete */
.delete-modal {
  max-width: 600px;
}

.delete-modal.critical {
  border: 2px solid var(--danger);
}

.delete-header {
  flex-direction: column;
  gap: 16px;
  text-align: center;
  padding: 32px 24px 24px;
  position: relative;
}

.delete-header .modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
}

.delete-icon-warning,
.delete-icon-critical {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.delete-icon-warning {
  background: rgba(251, 191, 36, 0.1);
  color: #fbbf24;
}

.delete-icon-critical {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.delete-warning-text {
  font-size: 1rem;
  color: var(--text);
  margin-bottom: 16px;
  text-align: center;
}

.delete-critical-text {
  font-size: 0.9375rem;
  color: var(--text);
  margin-bottom: 16px;
  font-weight: 500;
}

.delete-flow-info {
  padding: 16px;
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  border-radius: 8px;
  text-align: center;
  margin-bottom: 20px;
}

.delete-flow-info strong {
  font-size: 1.125rem;
  color: var(--text-primary);
}

.delete-flow-name-box {
  padding: 16px;
  background: var(--bg-secondary);
  border: 2px dashed var(--danger);
  border-radius: 8px;
  text-align: center;
  margin-bottom: 20px;
}

.delete-flow-name-box code {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--danger);
  font-family: 'Courier New', monospace;
}

.delete-warning-box,
.delete-final-warning {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 8px;
  font-size: 0.875rem;
  color: var(--text);
  margin-top: 20px;
}

.delete-final-warning {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: var(--danger);
  font-weight: 600;
  animation: shake 0.5s;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

.delete-warning-box svg,
.delete-final-warning svg {
  flex-shrink: 0;
  color: #fbbf24;
}

.delete-final-warning svg {
  color: var(--danger);
}

.input-error {
  border-color: var(--danger) !important;
  background: rgba(239, 68, 68, 0.05);
}

.input-error-message {
  display: block;
  margin-top: 8px;
  font-size: 0.875rem;
  color: var(--danger);
  font-weight: 500;
}

.input-success-message {
  display: block;
  margin-top: 8px;
  font-size: 0.875rem;
  color: var(--success);
  font-weight: 500;
}

.btn-danger {
  background: var(--danger);
  color: white;
  border: none;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
  transform: scale(1.02);
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger svg {
  color: white;
}

/* Channel Selector */
.form-helper {
  font-size: 0.875rem;
  color: var(--muted);
  margin: 0 0 12px;
}

/* ── Create flow modal ── */
.create-flow-modal {
  max-width: 460px;
  border-top: 3px solid #00FF66;
}

.cfm-header {
  padding: 20px 22px 16px;
  border-bottom: 1px solid var(--border);
}

.cfm-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cfm-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: rgba(0,255,102,0.12);
  border: 1px solid rgba(0,255,102,0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00FF66;
  font-size: 1rem;
  flex-shrink: 0;
}

.cfm-subtitle {
  font-size: 0.75rem;
  color: var(--muted);
  margin: 2px 0 0;
}

.create-flow-modal .modal-body {
  padding: 18px 22px;
}

.create-flow-modal .modal-footer {
  padding: 14px 22px;
}

/* ── Compact channel selector ── */
.cs-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 280px;
  overflow-y: auto;
  padding-right: 2px;
}

.cs-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  background: var(--bg-secondary);
  border: 1.5px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  text-align: left;
  width: 100%;
}

.cs-item:hover {
  border-color: rgba(0, 255, 102, 0.4);
  background: rgba(0, 255, 102, 0.03);
}

.cs-item--active {
  border-color: #00FF66 !important;
  background: rgba(0, 255, 102, 0.07) !important;
}

.cs-item-icon {
  width: 32px;
  height: 32px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.95rem;
  flex-shrink: 0;
}

.cs-item-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.cs-item-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cs-item-meta {
  font-size: 0.7rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.cs-item-badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 20px;
  letter-spacing: 0.03em;
  flex-shrink: 0;
}

.cs-badge--on {
  background: rgba(0, 255, 102, 0.15);
  color: #00cc52;
}

.cs-badge--off {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}

.cs-item-radio {
  font-size: 1rem;
  flex-shrink: 0;
  color: var(--muted);
}

.cs-item--active .cs-item-radio {
  color: #00FF66;
}

.cs-empty {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px;
  color: var(--muted);
  font-size: 0.85rem;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px dashed var(--border);
}

.cs-empty i {
  font-size: 1.5rem;
  color: #2aabee;
  flex-shrink: 0;
}

.no-channels-message {
  text-align: center;
  padding: 32px;
  color: var(--muted);
}

.no-channels-message i {
  font-size: 3rem;
  color: var(--warning);
  margin-bottom: 16px;
}

.no-channels-message p {
  margin: 8px 0;
}

.no-channels-message a {
  color: var(--primary);
  text-decoration: underline;
}

/* Botão de ativar/desativar fluxo */
.btn-warning {
  background: #f59e0b !important;
  color: white !important;
  border-color: #f59e0b !important;
}

.btn-warning:hover {
  background: #d97706 !important;
  border-color: #d97706 !important;
}

.btn-success {
  background: #10b981 !important;
  color: white !important;
  border-color: #10b981 !important;
}

.btn-success:hover {
  background: #059669 !important;
  border-color: #059669 !important;
}

.table-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* Toggle Switch */
.toggle-switch-wrapper {
  display: flex;
  align-items: center;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;
  cursor: pointer;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #2a2a2a;
  border-radius: 34px;
  transition: all 0.3s ease;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  border-radius: 50%;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.toggle-switch input:checked + .toggle-slider {
  background: linear-gradient(135deg, #00FF66 0%, #00cc52 100%);
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(22px);
}

.toggle-switch:hover .toggle-slider {
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.15), 0 0 0 3px rgba(0, 255, 102, 0.1);
}

/* Modal de Confirmação */
.confirm-modal {
  max-width: 480px;
}

.confirm-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.confirm-icon.icon-warning {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
  color: #f59e0b;
}

.confirm-icon.icon-success {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
  color: #10b981;
}

.flow-info-box {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
}

.flow-info-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-tertiary);
  margin-bottom: 4px;
  font-weight: 600;
}

.flow-info-value {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.confirm-message {
  font-size: 0.9375rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

.confirm-message strong {
  color: var(--text-primary);
  font-weight: 600;
}

/* Aviso de Bot Inativo */
.bot-inactive-warning {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  color: #ef4444;
  font-size: 0.75rem;
  font-weight: 600;
  margin-top: 6px;
}

.bot-inactive-warning i {
  font-size: 0.875rem;
}
</style>
