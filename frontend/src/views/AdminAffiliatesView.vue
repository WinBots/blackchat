<template>
  <div class="admin-affiliates">
    <div class="page-header">
      <h1>Afiliados</h1>
      <button class="btn-primary" @click="openCreate">
        <i class="fa-solid fa-plus"></i> Novo Afiliado
      </button>
    </div>

    <div class="card">
      <div v-if="loading" class="loading">Carregando...</div>
      <div v-else-if="affiliates.length === 0" class="empty">Nenhum afiliado cadastrado.</div>
      <table v-else class="table">
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
            <td>{{ aff.email }}</td>
            <td><code>{{ aff.code }}</code></td>
            <td>{{ aff.commission_pct }}%</td>
            <td>
              <span :class="['badge', aff.is_active ? 'badge-active' : 'badge-inactive']">
                {{ aff.is_active ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="actions">
              <button class="btn-icon" title="Ver stats" @click="viewStats(aff)">
                <i class="fa-solid fa-chart-bar"></i>
              </button>
              <button class="btn-icon" title="Editar" @click="openEdit(aff)">
                <i class="fa-solid fa-pen"></i>
              </button>
              <button class="btn-icon btn-danger" title="Remover" @click="confirmDelete(aff)">
                <i class="fa-solid fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal criar/editar -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editingId ? 'Editar Afiliado' : 'Novo Afiliado' }}</h2>
          <button class="btn-close" @click="closeModal"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <form @submit.prevent="saveAffiliate" class="modal-form">
          <div class="form-row">
            <div class="form-group">
              <label>Nome</label>
              <input v-model="form.name" required placeholder="Nome completo" />
            </div>
            <div class="form-group">
              <label>E-mail</label>
              <input v-model="form.email" type="email" required placeholder="email@exemplo.com" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Senha {{ editingId ? '(deixe em branco para manter)' : '' }}</label>
              <input v-model="form.password" type="password" :required="!editingId" placeholder="••••••••" />
            </div>
            <div class="form-group">
              <label>Comissão (%)</label>
              <input v-model.number="form.commission_pct" type="number" step="0.01" min="0" max="100" required />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Taxa Stripe (%)</label>
              <input v-model.number="form.stripe_fee_pct" type="number" step="0.01" min="0" />
            </div>
            <div class="form-group">
              <label>Taxa Saque (R$)</label>
              <input v-model.number="form.withdraw_fee" type="number" step="0.01" min="0" />
            </div>
            <div class="form-group">
              <label>Imposto (%)</label>
              <input v-model.number="form.tax_pct" type="number" step="0.01" min="0" />
            </div>
          </div>
          <div v-if="editingId" class="form-group">
            <label>
              <input type="checkbox" v-model="form.is_active" />
              Ativo
            </label>
          </div>
          <div v-if="formError" class="error-msg">{{ formError }}</div>
          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="closeModal">Cancelar</button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal stats -->
    <div v-if="statsModal" class="modal-overlay" @click.self="statsModal = null">
      <div class="modal">
        <div class="modal-header">
          <h2>Stats — {{ statsModal.affiliate?.name }}</h2>
          <button class="btn-close" @click="statsModal = null"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="stats-grid">
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
          <div class="stat-card highlight">
            <div class="stat-label">Comissão Final</div>
            <div class="stat-value">{{ formatCurrency(statsModal.total_final) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
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
.admin-affiliates {
  padding: 32px;
  max-width: 1100px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary, #f8fafc);
  margin: 0;
}

.card {
  background: var(--bg-secondary, #1e293b);
  border: 1px solid var(--border, #334155);
  border-radius: 12px;
  overflow: hidden;
}

.loading, .empty {
  text-align: center;
  padding: 48px;
  color: var(--muted, #94a3b8);
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th {
  text-align: left;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--muted, #64748b);
  padding: 12px 16px;
  border-bottom: 1px solid var(--border, #334155);
  background: rgba(0,0,0,0.15);
}

.table td {
  padding: 14px 16px;
  font-size: 0.9375rem;
  color: var(--text-primary, #cbd5e1);
  border-bottom: 1px solid var(--border, #1e293b);
}

.table tr:last-child td {
  border-bottom: none;
}

.table tr:hover td {
  background: rgba(99, 102, 241, 0.04);
}

code {
  background: rgba(99,102,241,0.12);
  color: #818cf8;
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 0.875rem;
}

.badge {
  display: inline-block;
  border-radius: 20px;
  padding: 3px 12px;
  font-size: 0.8125rem;
  font-weight: 600;
}

.badge-active {
  background: rgba(74, 222, 128, 0.12);
  color: #4ade80;
}

.badge-inactive {
  background: rgba(148, 163, 184, 0.12);
  color: #94a3b8;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid var(--border, #334155);
  background: transparent;
  color: var(--muted, #94a3b8);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon:hover {
  color: #f8fafc;
  border-color: #64748b;
}

.btn-icon.btn-danger:hover {
  color: #f87171;
  border-color: #f87171;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #4f46e5;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 10px 20px;
  background: transparent;
  color: var(--muted, #94a3b8);
  border: 1px solid var(--border, #334155);
  border-radius: 8px;
  font-size: 0.9375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  color: #f8fafc;
  border-color: #64748b;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal {
  background: var(--bg-secondary, #1e293b);
  border: 1px solid var(--border, #334155);
  border-radius: 12px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border, #334155);
}

.modal-header h2 {
  font-size: 1.125rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary, #f8fafc);
}

.btn-close {
  background: transparent;
  border: none;
  color: var(--muted, #94a3b8);
  cursor: pointer;
  font-size: 1rem;
  padding: 4px;
}

.modal-form {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--muted, #cbd5e1);
}

.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="password"],
.form-group input[type="number"] {
  padding: 10px 12px;
  background: var(--bg-primary, #0f172a);
  border: 1px solid var(--border, #334155);
  border-radius: 8px;
  color: var(--text-primary, #f8fafc);
  font-size: 0.9375rem;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input:focus {
  border-color: #6366f1;
}

.form-group input[type="checkbox"] {
  margin-right: 8px;
}

.error-msg {
  background: rgba(239,68,68,0.12);
  color: #f87171;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 0.875rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

/* Stats grid (modal stats) */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 24px;
}

.stat-card {
  background: var(--bg-primary, #0f172a);
  border: 1px solid var(--border, #334155);
  border-radius: 10px;
  padding: 20px;
}

.stat-card.highlight {
  border-color: rgba(99,102,241,0.4);
  background: rgba(99,102,241,0.08);
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--muted, #94a3b8);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary, #f8fafc);
}

.stat-card.highlight .stat-value {
  color: #818cf8;
}
</style>
