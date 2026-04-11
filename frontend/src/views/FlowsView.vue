<template>
  <AppLayout>
    <div class="card flows-page">

      <!-- ─── Header ─────────────────────────────────────────── -->
      <div class="fp-header">
        <div class="fp-header-info">
          <h2 class="fp-title">Automações</h2>
          <p class="fp-subtitle">Gerencie os fluxos de resposta automática do seu bot</p>
        </div>
        <div class="fp-header-actions">
          <span
            v-if="planUsage && planUsage.limit !== null"
            class="plan-usage-badge"
            :class="{ 'plan-usage-badge--full': flows.length >= planUsage.limit }"
          >
            {{ flows.length }}/{{ planUsage.limit }} fluxos
            <router-link v-if="flows.length >= planUsage.limit" to="/settings" class="plan-usage-upgrade">Upgrade</router-link>
          </span>
          <div class="fp-search-wrap">
            <svg class="fp-search-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              class="fp-search-input"
              placeholder="Buscar por nome ou keyword…"
            />
            <button v-if="searchQuery" class="fp-search-clear" @click="searchQuery = ''" title="Limpar busca">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          <button class="btn btn-primary" @click="openCreateModal" :disabled="loading">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Nova Automação
          </button>
        </div>
      </div>

      <!-- ─── Comportamento padrão (fallback strip) ───────────── -->
      <div class="fp-behavior-strip">
        <div class="fp-behavior-left">
          <div class="fp-behavior-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/>
            </svg>
          </div>
          <span class="fp-behavior-label">Mensagem sem keyword correspondente:</span>
          <span class="fp-behavior-value">Ignorar mensagem</span>
        </div>
        <span class="fp-behavior-soon">IA e Mensagem Fixa em breve</span>
      </div>

      <!-- ─── Loading skeleton ─────────────────────────────────── -->
      <div v-if="loading" class="fp-skeleton-list">
        <div v-for="i in 4" :key="i" class="fp-skeleton-row">
          <div class="fp-skel fp-skel-dot"></div>
          <div class="fp-skel fp-skel-main"></div>
          <div class="fp-skel fp-skel-badge"></div>
          <div class="fp-skel fp-skel-badge" style="width:64px"></div>
          <div class="fp-skel fp-skel-kw"></div>
          <div class="fp-skel fp-skel-actions"></div>
        </div>
      </div>

      <!-- ─── Empty state ──────────────────────────────────────── -->
      <div v-else-if="filteredFlows.length === 0" class="fp-empty">
        <template v-if="searchQuery">
          <div class="fp-empty-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </div>
          <h3 class="fp-empty-title">Nenhuma automação encontrada</h3>
          <p class="fp-empty-desc">Tente outro nome ou keyword</p>
          <button class="btn btn-secondary btn-sm" @click="searchQuery = ''">Limpar busca</button>
        </template>
        <template v-else>
          <div class="fp-empty-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
          </div>
          <h3 class="fp-empty-title">Nenhuma automação criada ainda</h3>
          <p class="fp-empty-desc">Automatize as respostas do seu bot com mensagens, condições e ações</p>
          <button class="btn btn-primary" @click="openCreateModal">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Criar primeira automação
          </button>
        </template>
      </div>

      <!-- ─── Lista de flows ───────────────────────────────────── -->
      <div v-else class="fp-list">
        <div
          v-for="f in filteredFlows"
          :key="f.id"
          class="fp-row"
          @click="goToFlow(f.id)"
          :title="`Editar: ${f.name}`"
        >
          <!-- Status dot -->
          <span class="fp-status-dot" :class="f.is_active ? 'dot-on' : 'dot-off'" :title="f.is_active ? 'Ativo' : 'Inativo'"></span>

          <!-- Nome + descrição -->
          <div class="fp-row-main">
            <span class="fp-row-name">{{ f.name }}</span>
            <span v-if="f.description" class="fp-row-desc">{{ f.description }}</span>
          </div>

          <!-- Meta: canal + gatilho + keywords -->
          <div class="fp-row-meta">
            <div class="fp-channel-badge" :class="`system-${getFlowSystem(f)}`">
              <i :class="getSystemIcon(f)"></i>
              <span>{{ getSystemLabel(f) }}</span>
              <span v-if="!isChannelActive(f.channel_id)" class="fp-bot-warn" title="Bot inativo">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
              </span>
            </div>

            <span class="trigger-badge">{{ getTriggerLabel(f) }}</span>

            <div class="fp-keywords" v-if="f.keywords && f.keywords.length > 0">
              <span
                v-for="(kw, i) in f.keywords.slice(0, 3)"
                :key="i"
                class="keyword-badge"
                :style="{ background: getKeywordColor(kw) }"
              >{{ kw }}</span>
              <span v-if="f.keywords.length > 3" class="kw-overflow">+{{ f.keywords.length - 3 }}</span>
            </div>
            <span v-else class="no-keywords">sem keywords</span>
          </div>

          <!-- Ações (não propagam click para a row) -->
          <div class="fp-row-actions" @click.stop>
            <label class="toggle-switch" :title="f.is_active ? 'Desativar automação' : 'Ativar automação'">
              <input type="checkbox" :checked="f.is_active" @click.prevent="openToggleConfirmModal(f)" />
              <span class="toggle-slider"></span>
            </label>
            <button
              class="btn btn-ghost btn-sm fp-btn-duplicate"
              @click.stop="handleDuplicate(f)"
              :disabled="duplicating === f.id"
              title="Duplicar automação"
            >
              <svg v-if="duplicating !== f.id" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="fp-spin">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
              </svg>
            </button>
            <button class="btn btn-ghost btn-sm fp-btn-edit" @click.stop="goToFlow(f.id)" title="Editar automação">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              Editar
            </button>
            <button class="btn btn-ghost btn-sm fp-btn-delete" @click.stop="openDeleteModal(f)" title="Excluir automação">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

    </div>

    <!-- ─── Modal: Criar Automação ────────────────────────────── -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal-content create-flow-modal" @click.stop>
        <div class="modal-header cfm-header">
          <div class="cfm-title-group">
            <div class="cfm-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
            </div>
            <div>
              <h3 class="modal-title">Nova Automação</h3>
              <p class="cfm-subtitle">Configure o nome e o bot desta automação</p>
            </div>
          </div>
          <button class="modal-close" @click="showCreateModal = false">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Nome da automação <span class="required-star">*</span></label>
            <input
              v-model="newFlow.name"
              type="text"
              class="form-input"
              placeholder="Ex: Boas-vindas, Suporte, Vendas..."
              @keyup.enter="createNewFlow"
              autofocus
            />
            <span class="form-hint">Escolha um nome que descreva o objetivo desta automação</span>
          </div>

          <div class="form-group">
            <label class="form-label">Bot / Canal <span class="required-star">*</span></label>
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
                <span :class="['cs-item-badge', channel.is_active ? 'cs-badge--on' : 'cs-badge--off']">
                  {{ channel.is_active ? 'Ativo' : 'Inativo' }}
                </span>
                <div class="cs-item-radio">
                  <svg v-if="newFlow.channel_id === channel.id" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00FF66" stroke-width="2.5">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
                  </svg>
                  <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <circle cx="12" cy="12" r="10"/>
                  </svg>
                </div>
              </button>

              <div v-if="availableChannels.length === 0" class="cs-empty">
                <i class="fa-brands fa-telegram"></i>
                <span>Nenhum bot ativo. Vá em <router-link to="/settings">Configurações → Telegram</router-link> para adicionar um.</span>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Descrição <span class="form-optional">(opcional)</span></label>
            <textarea
              v-model="newFlow.description"
              class="form-input"
              rows="2"
              placeholder="Descreva brevemente o que esta automação faz..."
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showCreateModal = false">Cancelar</button>
          <button
            class="btn btn-primary"
            @click="createNewFlow"
            :disabled="!newFlow.name || !newFlow.channel_id || creating"
          >
            <svg v-if="!creating" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            {{ creating ? 'Criando…' : 'Criar e Editar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ─── Modal: Confirmar Toggle ──────────────────────────── -->
    <div v-if="showToggleModal" class="modal-overlay" @click="cancelToggle">
      <div class="modal-content confirm-modal" @click.stop>
        <div class="modal-header">
          <div class="confirm-icon" :class="flowToToggle?.is_active ? 'icon-warning' : 'icon-success'">
            <svg v-if="flowToToggle?.is_active" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            <svg v-else width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <h3 class="modal-title">{{ flowToToggle?.is_active ? 'Desativar automação?' : 'Ativar automação?' }}</h3>
          <button class="modal-close" @click="cancelToggle">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <div class="flow-info-box">
            <div class="flow-info-label">Automação</div>
            <div class="flow-info-value">{{ flowToToggle?.name }}</div>
          </div>
          <p v-if="flowToToggle?.is_active" class="confirm-message">
            Ao desativar, esta automação <strong>não responderá mais</strong> às mensagens até ser reativada.
          </p>
          <p v-else class="confirm-message">
            Ao ativar, esta automação voltará a <strong>responder automaticamente</strong> às mensagens que corresponderem às suas keywords.
          </p>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="cancelToggle" :disabled="toggling">Cancelar</button>
          <button
            class="btn"
            :class="flowToToggle?.is_active ? 'btn-warning' : 'btn-success'"
            @click="confirmToggle"
            :disabled="toggling"
          >
            {{ toggling ? 'Processando…' : (flowToToggle?.is_active ? 'Desativar' : 'Ativar') }}
          </button>
        </div>
      </div>
    </div>

    <!-- ─── Modal: Excluir — Etapa 1 ────────────────────────── -->
    <div v-if="showDeleteModal1" class="modal-overlay" @click="cancelDelete">
      <div class="modal-content delete-modal" @click.stop>
        <div class="modal-header delete-header">
          <div class="delete-icon-warning">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <h3 class="modal-title">Excluir automação?</h3>
          <button class="modal-close" @click="cancelDelete">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <p class="delete-warning-text">Você está prestes a excluir permanentemente:</p>
          <div class="delete-flow-info">
            <strong>{{ flowToDelete?.name }}</strong>
          </div>
          <div class="delete-warning-box">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <div><strong>Atenção:</strong> Todos os blocos, conexões e configurações serão perdidos. Esta ação não pode ser desfeita.</div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="cancelDelete">Cancelar</button>
          <button class="btn btn-danger" @click="showDeleteModal2 = true; showDeleteModal1 = false">
            Continuar com exclusão
          </button>
        </div>
      </div>
    </div>

    <!-- ─── Modal: Excluir — Etapa 2 (confirmação crítica) ──── -->
    <div v-if="showDeleteModal2" class="modal-overlay" @click="cancelDelete">
      <div class="modal-content delete-modal critical" @click.stop>
        <div class="modal-header delete-header">
          <div class="delete-icon-critical">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
          </div>
          <h3 class="modal-title">Confirmação final</h3>
          <button class="modal-close" @click="cancelDelete">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <p class="delete-critical-text">
            Para confirmar, digite o nome exato da automação:
          </p>
          <div class="delete-flow-name-box">
            <code>{{ flowToDelete?.name }}</code>
          </div>
          <div class="form-group">
            <input
              v-model="deleteConfirmation"
              type="text"
              class="form-input"
              :class="{ 'input-error': deleteConfirmation && deleteConfirmation !== flowToDelete?.name }"
              placeholder="Digite o nome exato…"
              @keyup.enter="deleteConfirmation === flowToDelete?.name && confirmDelete()"
              autofocus
            />
            <span v-if="deleteConfirmation && deleteConfirmation !== flowToDelete?.name" class="input-error-message">
              Nome incorreto — tente novamente
            </span>
            <span v-if="deleteConfirmation === flowToDelete?.name && deleteConfirmation" class="input-success-message">
              Nome confirmado
            </span>
          </div>
          <div class="delete-final-warning">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            Esta ação é irreversível e não pode ser desfeita.
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showDeleteModal2 = false; showDeleteModal1 = true">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Voltar
          </button>
          <button
            class="btn btn-danger"
            @click="confirmDelete"
            :disabled="deleteConfirmation !== flowToDelete?.name || deleting"
          >
            {{ deleting ? 'Excluindo…' : 'Excluir permanentemente' }}
          </button>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { listFlows, createFlow, createFlowStep, deleteFlow as deleteFlowAPI, updateFlow, duplicateFlow } from '@/api/flows'
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

// Filtro de busca
const searchQuery = ref('')
const filteredFlows = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return flows.value
  return flows.value.filter(f =>
    f.name.toLowerCase().includes(q) ||
    (f.description || '').toLowerCase().includes(q) ||
    (f.keywords || []).some(k => k.toLowerCase().includes(q))
  )
})

// Estados para deletar
const showDeleteModal1 = ref(false)
const showDeleteModal2 = ref(false)
const flowToDelete = ref(null)
const deleteConfirmation = ref('')
const deleting = ref(false)
const duplicating = ref(null) // id do flow sendo duplicado

// Estados para toggle de ativação/desativação
const showToggleModal = ref(false)
const flowToToggle = ref(null)
const toggling = ref(false)

const newFlow = ref({
  name: '',
  channel_id: null,
  description: ''
})


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

    // Keywords já vêm do backend — sem N+1
    flows.value = await listFlows()
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

    // Criar step inicial de gatilho
    await createFlowStep(flow.id, {
      type: 'trigger',
      order_index: 1,
      config: { triggerType: 'message', keywords: [] }
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
  // Buscar em TODOS os canais (ativos e inativos) para não perder o nome
  if (flow.channel_id) {
    const channel = allChannels.value.find(c => c.id === flow.channel_id)
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

const handleDuplicate = async (flow) => {
  duplicating.value = flow.id
  try {
    const newFlow = await duplicateFlow(flow.id)
    await fetchFlows()
    toast.success(`"${flow.name}" duplicado com sucesso`)
    router.push(`/flows/${newFlow.id}`)
  } catch (e) {
    const detail = e?.response?.data?.detail
    if (e?.response?.status === 403 && detail?.code === 'PLAN_LIMIT_EXCEEDED') {
      toast.error(`Limite de fluxos atingido. Faça upgrade para duplicar.`)
    } else {
      toast.error('Erro ao duplicar automação')
    }
  } finally {
    duplicating.value = null
  }
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

onMounted(async () => {
  fetchFlows()
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
/* ── Page container ── */
.flows-page {
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0;
}

/* ── Header ── */
.fp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 24px 16px;
  flex-wrap: wrap;
}

.fp-header-info {
  min-width: 0;
}

.fp-title {
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 3px;
  letter-spacing: -0.01em;
}

.fp-subtitle {
  font-size: 0.8125rem;
  color: var(--text-muted, #64748b);
  margin: 0;
}

.fp-header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  flex-wrap: wrap;
}

/* ── Search ── */
.fp-search-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.fp-search-icon {
  position: absolute;
  left: 10px;
  color: var(--text-muted, #64748b);
  pointer-events: none;
}

.fp-search-input {
  background: var(--bg-secondary, #1e293b);
  border: 1px solid var(--border, rgba(255,255,255,0.08));
  border-radius: 8px;
  padding: 7px 32px 7px 32px;
  font-size: 0.8125rem;
  color: var(--text-primary);
  width: 220px;
  outline: none;
  transition: border-color 0.15s;
}

.fp-search-input:focus {
  border-color: rgba(0, 255, 102, 0.4);
}

.fp-search-input::placeholder {
  color: var(--text-muted, #64748b);
}

.fp-search-clear {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  padding: 2px;
  cursor: pointer;
  color: var(--text-muted, #64748b);
  display: flex;
  align-items: center;
  border-radius: 4px;
  transition: color 0.15s;
}

.fp-search-clear:hover {
  color: var(--text-primary);
}

/* ── Behavior strip ── */
.fp-behavior-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 9px 24px;
  background: rgba(255,255,255,0.025);
  border-top: 1px solid var(--border, rgba(255,255,255,0.06));
  border-bottom: 1px solid var(--border, rgba(255,255,255,0.06));
  font-size: 0.8rem;
  flex-wrap: wrap;
}

.fp-behavior-left {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary, #94a3b8);
}

.fp-behavior-icon {
  display: flex;
  align-items: center;
  color: var(--text-muted, #64748b);
  flex-shrink: 0;
}

.fp-behavior-label {
  color: var(--text-muted, #64748b);
}

.fp-behavior-value {
  font-weight: 600;
  color: var(--text-secondary, #94a3b8);
}

.fp-behavior-soon {
  font-size: 0.72rem;
  color: var(--text-muted, #64748b);
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border, rgba(255,255,255,0.06));
  border-radius: 99px;
  padding: 2px 10px;
  white-space: nowrap;
}

/* ── Skeleton ── */
.fp-skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding: 8px 0;
}

.fp-skeleton-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 24px;
}

.fp-skel {
  background: rgba(255,255,255,0.06);
  border-radius: 6px;
  animation: fp-shimmer 1.5s ease-in-out infinite;
}

.fp-skel-dot  { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.fp-skel-main { height: 14px; flex: 1; max-width: 220px; }
.fp-skel-badge { height: 22px; width: 80px; border-radius: 99px; }
.fp-skel-kw   { height: 22px; width: 120px; border-radius: 99px; }
.fp-skel-actions { height: 28px; width: 100px; border-radius: 8px; margin-left: auto; }

@keyframes fp-shimmer {
  0%   { opacity: 0.5; }
  50%  { opacity: 1; }
  100% { opacity: 0.5; }
}

/* ── Empty state ── */
.fp-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 60px 24px;
  text-align: center;
}

.fp-empty-icon {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border, rgba(255,255,255,0.08));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted, #64748b);
  margin-bottom: 4px;
}

.fp-empty-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.fp-empty-desc {
  font-size: 0.85rem;
  color: var(--text-muted, #64748b);
  margin: 0 0 8px;
  max-width: 360px;
  line-height: 1.5;
}

/* ── List ── */
.fp-list {
  display: flex;
  flex-direction: column;
}

.fp-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 24px;
  border-bottom: 1px solid var(--border, rgba(255,255,255,0.05));
  cursor: pointer;
  transition: background 0.12s;
  min-width: 0;
}

.fp-row:last-child {
  border-bottom: none;
}

.fp-row:hover {
  background: rgba(255,255,255,0.03);
}

/* ── Status dot ── */
.fp-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 1px;
}

.fp-status-dot.dot-on  { background: #22c55e; box-shadow: 0 0 0 3px rgba(34,197,94,0.18); }
.fp-status-dot.dot-off { background: #475569; }

/* ── Row main (name + desc) ── */
.fp-row-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.fp-row-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.fp-row-desc {
  font-size: 0.775rem;
  color: var(--text-muted, #64748b);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── Row meta (channel + trigger + keywords) ── */
.fp-row-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  flex-wrap: wrap;
}

.fp-channel-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 9px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  color: var(--text-secondary, #94a3b8);
  white-space: nowrap;
}

.fp-channel-badge.system-telegram {
  background: rgba(34,158,217,0.1);
  border-color: rgba(34,158,217,0.25);
  color: #60c4f0;
}

.fp-bot-warn {
  display: inline-flex;
  align-items: center;
  color: #f87171;
  margin-left: 2px;
}

.fp-keywords {
  display: flex;
  align-items: center;
  gap: 4px;
}

.kw-overflow {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted, #64748b);
  padding: 3px 7px;
  background: rgba(255,255,255,0.05);
  border-radius: 99px;
}

/* ── Row actions ── */
.fp-row-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.fp-btn-edit {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.8rem;
  padding: 5px 10px;
  color: var(--text-secondary, #94a3b8);
  border: 1px solid transparent;
  border-radius: 7px;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
}

.fp-btn-edit:hover {
  color: var(--text-primary);
  border-color: var(--border, rgba(255,255,255,0.08));
  background: rgba(255,255,255,0.04);
}

.fp-btn-delete {
  display: inline-flex;
  align-items: center;
  padding: 5px 7px;
  color: var(--text-muted, #64748b);
  border: 1px solid transparent;
  border-radius: 7px;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
}

.fp-btn-delete:hover {
  color: #f87171;
  border-color: rgba(248,113,113,0.25);
  background: rgba(248,113,113,0.06);
}

.fp-btn-duplicate {
  display: inline-flex;
  align-items: center;
  padding: 5px 7px;
  color: var(--text-muted, #64748b);
  border: 1px solid transparent;
  border-radius: 7px;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
}

.fp-btn-duplicate:hover:not(:disabled) {
  color: #60a5fa;
  border-color: rgba(96,165,250,0.25);
  background: rgba(96,165,250,0.06);
}

.fp-btn-duplicate:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@keyframes fp-spin {
  to { transform: rotate(360deg); }
}

.fp-spin {
  animation: fp-spin 0.8s linear infinite;
}

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
