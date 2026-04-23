<template>
  <AppLayout>
    <div class="affiliates-page">
      <div class="card affiliates-card">

        <div class="page-header affiliates-header">
          <div>
            <h2 class="page-title">Afiliados</h2>
            <p class="page-description">Gerencie afiliados e acompanhe comissões</p>
          </div>
          <div class="header-actions">
            <button class="btn btn-ghost btn-sm" type="button" @click="loadAffiliates" :disabled="loading">
              {{ loading ? 'Carregando…' : 'Atualizar' }}
            </button>
            <button class="btn btn-accent btn-sm" type="button" @click="openCreate">
              <i class="fa-solid fa-plus"></i> Novo Afiliado
            </button>
          </div>
        </div>

        <div v-if="loading" class="affiliates-loading">
          <div class="loading-spinner"></div>
          <span>Carregando afiliados…</span>
        </div>

        <div v-else-if="affiliates.length === 0" class="affiliates-empty">
          <i class="fa-solid fa-users-slash"></i>
          <p>Nenhum afiliado cadastrado.</p>
        </div>

        <div v-else class="table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>E-mail</th>
                <th>Código</th>
                <th>Comissão</th>
                <th>Status</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="aff in affiliates" :key="aff.id">
                <td>{{ aff.name }}</td>
                <td class="text-muted">{{ aff.email }}</td>
                <td><code class="code-tag">{{ aff.code }}</code></td>
                <td>{{ aff.commission_pct }}%</td>
                <td>
                  <span :class="['status-badge', aff.is_active ? 'status-active' : 'status-inactive']">
                    {{ aff.is_active ? 'Ativo' : 'Inativo' }}
                  </span>
                </td>
                <td>
                  <div class="row-actions">
                    <button class="btn btn-ghost btn-xs" title="Ver stats" @click="viewStats(aff)">
                      <i class="fa-solid fa-chart-bar"></i>
                    </button>
                    <button class="btn btn-ghost btn-xs" title="Editar" @click="openEdit(aff)">
                      <i class="fa-solid fa-pen"></i>
                    </button>
                    <button class="btn btn-ghost btn-xs btn-danger" title="Remover" @click="confirmDelete(aff)">
                      <i class="fa-solid fa-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>

    <!-- Modal criar/editar -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-box">
          <div class="modal-header">
            <h3>{{ editingId ? 'Editar Afiliado' : 'Novo Afiliado' }}</h3>
            <button class="btn btn-ghost btn-xs" @click="closeModal">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <form @submit.prevent="saveAffiliate" class="modal-body">
            <div class="form-row">
              <div class="form-group">
                <label class="input-label">Nome</label>
                <input class="input" v-model="form.name" required placeholder="Nome completo" />
              </div>
              <div class="form-group">
                <label class="input-label">E-mail</label>
                <input class="input" v-model="form.email" type="email" required placeholder="email@exemplo.com" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="input-label">
                  Senha
                  <span v-if="editingId" class="hint">(deixe em branco para manter)</span>
                </label>
                <input class="input" v-model="form.password" type="password" :required="!editingId" placeholder="••••••••" />
              </div>
              <div class="form-group">
                <label class="input-label">Comissão (%)</label>
                <input class="input" v-model.number="form.commission_pct" type="number" step="0.01" min="0" max="100" required />
              </div>
            </div>

            <div class="form-row form-row-3">
              <div class="form-group">
                <label class="input-label">Taxa Stripe (%)</label>
                <input class="input" v-model.number="form.stripe_fee_pct" type="number" step="0.01" min="0" />
              </div>
              <div class="form-group">
                <label class="input-label">Taxa Saque (R$)</label>
                <input class="input" v-model.number="form.withdraw_fee" type="number" step="0.01" min="0" />
              </div>
              <div class="form-group">
                <label class="input-label">Imposto (%)</label>
                <input class="input" v-model.number="form.tax_pct" type="number" step="0.01" min="0" />
              </div>
            </div>

            <div v-if="editingId" class="form-group">
              <label class="toggle-label">
                <input type="checkbox" v-model="form.is_active" />
                <span>Afiliado ativo</span>
              </label>
            </div>

            <div v-if="formError" class="form-error">{{ formError }}</div>

            <div class="modal-footer">
              <button type="button" class="btn btn-ghost" @click="closeModal">Cancelar</button>
              <button type="submit" class="btn btn-accent" :disabled="saving">
                {{ saving ? 'Salvando…' : 'Salvar' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Modal stats -->
    <Teleport to="body">
      <div v-if="statsModal" class="modal-overlay" @click.self="statsModal = null">
        <div class="modal-box modal-box-sm">
          <div class="modal-header">
            <h3>Stats — {{ statsModal.affiliate?.name }}</h3>
            <button class="btn btn-ghost btn-xs" @click="statsModal = null">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
          <div class="stats-grid modal-body">
            <div class="stat-card">
              <div class="stat-label">Indicações</div>
              <div class="stat-value">{{ statsModal.referrals }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">Vendas</div>
              <div class="stat-value">{{ statsModal.sales_count }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">Total Bruto</div>
              <div class="stat-value">{{ formatCurrency(statsModal.total_gross) }}</div>
            </div>
            <div class="stat-card stat-card-highlight">
              <div class="stat-label">Comissão Final</div>
              <div class="stat-value">{{ formatCurrency(statsModal.total_final) }}</div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import {
  adminListAffiliates,
  adminCreateAffiliate,
  adminUpdateAffiliate,
  adminDeleteAffiliate,
  adminAffiliateStats,
} from '@/api/affiliate'

const affiliates = ref([])
const loading = ref(true)
const showModal = ref(false)
const editingId = ref(null)
const saving = ref(false)
const formError = ref('')
const statsModal = ref(null)

const defaultForm = () => ({
  name: '',
  email: '',
  password: '',
  commission_pct: 0,
  stripe_fee_pct: 2.9,
  withdraw_fee: 0,
  tax_pct: 0,
  is_active: true,
})
const form = ref(defaultForm())

const token = () => localStorage.getItem('token') || ''

onMounted(loadAffiliates)

async function loadAffiliates() {
  loading.value = true
  try {
    affiliates.value = await adminListAffiliates(token())
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.value = defaultForm()
  formError.value = ''
  showModal.value = true
}

function openEdit(aff) {
  editingId.value = aff.id
  form.value = {
    name: aff.name,
    email: aff.email,
    password: '',
    commission_pct: aff.commission_pct,
    stripe_fee_pct: aff.stripe_fee_pct,
    withdraw_fee: aff.withdraw_fee,
    tax_pct: aff.tax_pct,
    is_active: aff.is_active,
  }
  formError.value = ''
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

async function saveAffiliate() {
  formError.value = ''
  saving.value = true
  try {
    const payload = { ...form.value }
    if (editingId.value && !payload.password) delete payload.password
    if (editingId.value) {
      await adminUpdateAffiliate(token(), editingId.value, payload)
    } else {
      await adminCreateAffiliate(token(), payload)
    }
    closeModal()
    await loadAffiliates()
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Erro ao salvar'
  } finally {
    saving.value = false
  }
}

async function confirmDelete(aff) {
  if (!confirm(`Remover afiliado "${aff.name}"?`)) return
  await adminDeleteAffiliate(token(), aff.id)
  await loadAffiliates()
}

async function viewStats(aff) {
  const data = await adminAffiliateStats(token(), aff.id)
  statsModal.value = data
}

function formatCurrency(val) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0)
}
</script>

<style scoped>
.affiliates-page {
  padding: 24px;
  max-width: 1100px;
  margin: 0 auto;
}

.affiliates-card {
  overflow: hidden;
}

.affiliates-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Botão de destaque usando a cor do sistema */
.btn-accent {
  background: var(--accent, #00FF66);
  color: #000;
  border-color: transparent;
  font-weight: 600;
}
.btn-accent:hover:not(:disabled) {
  filter: brightness(0.9);
}
.btn-accent:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.affiliates-loading {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 48px 24px;
  color: var(--text-muted);
}

.affiliates-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 64px 24px;
  color: var(--text-muted);
}

.affiliates-empty i {
  font-size: 2rem;
  opacity: 0.4;
}

.affiliates-empty p {
  font-size: 0.9375rem;
  margin: 0;
}

.table-wrapper {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th {
  text-align: left;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-muted);
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}

.table td {
  padding: 13px 16px;
  font-size: 0.9375rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border);
}

.table tbody tr:last-child td {
  border-bottom: none;
}

.table tbody tr:hover td {
  background: var(--bg-hover, rgba(255,255,255,0.02));
}

.text-muted {
  color: var(--text-muted) !important;
  font-size: 0.875rem;
}

.code-tag {
  display: inline-block;
  background: var(--accent-soft, rgba(0,255,102,0.08));
  color: var(--accent, #00FF66);
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 0.8125rem;
  font-family: monospace;
}

.status-badge {
  display: inline-block;
  border-radius: 20px;
  padding: 3px 12px;
  font-size: 0.8125rem;
  font-weight: 600;
}

.status-active {
  background: rgba(34, 197, 94, 0.12);
  color: #22c55e;
}

.status-inactive {
  background: rgba(148, 163, 184, 0.1);
  color: var(--text-muted);
}

.row-actions {
  display: flex;
  gap: 6px;
}

.btn-xs {
  padding: 5px 8px;
  font-size: 0.8125rem;
}

.btn-danger {
  color: var(--danger, #f87171) !important;
}
.btn-danger:hover {
  background: rgba(239, 68, 68, 0.1) !important;
  border-color: rgba(239, 68, 68, 0.3) !important;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 16px;
}

.modal-box {
  background: var(--bg-card, var(--bg-secondary));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg, 12px);
  width: 100%;
  max-width: 580px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 24px 64px rgba(0,0,0,0.4);
}

.modal-box-sm {
  max-width: 460px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.modal-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 8px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.form-row-3 {
  grid-template-columns: 1fr 1fr 1fr;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.hint {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 400;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: var(--text-primary);
  cursor: pointer;
}

.toggle-label input[type="checkbox"] {
  accent-color: var(--accent, #00FF66);
  width: 16px;
  height: 16px;
}

.form-error {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--radius-sm, 8px);
  padding: 10px 14px;
  font-size: 0.875rem;
}

/* Stats grid */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stat-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-md, 10px);
  padding: 18px;
}

.stat-card-highlight {
  border-color: var(--accent-soft, rgba(0,255,102,0.2));
  background: var(--accent-soft, rgba(0,255,102,0.05));
}

.stat-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.stat-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-card-highlight .stat-value {
  color: var(--accent, #00FF66);
}

@media (max-width: 600px) {
  .form-row, .form-row-3 {
    grid-template-columns: 1fr;
  }
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
