<template>
  <div class="affiliate-dashboard">
    <header class="dash-header">
      <div class="header-left">
        <h1>Portal de Afiliados</h1>
        <span v-if="affiliate" class="code-badge">Código: {{ affiliate.code }}</span>
      </div>
      <button class="btn-logout" @click="handleLogout">Sair</button>
    </header>

    <div v-if="loading" class="loading">Carregando...</div>

    <template v-else-if="affiliate">
      <!-- Link de afiliado -->
      <div class="card link-card">
        <div class="card-title">Seu Link de Indicação</div>
        <div class="link-row">
          <span class="link-text">{{ affiliateLink }}</span>
          <button class="btn-copy" @click="copyLink">
            <i class="fa-solid fa-copy"></i>
            {{ copied ? 'Copiado!' : 'Copiar' }}
          </button>
        </div>
      </div>

      <!-- Filtro de datas -->
      <div class="card filter-card">
        <div class="filter-row">
          <div class="filter-group">
            <label>De</label>
            <input type="date" v-model="dateFrom" @change="loadStats" />
          </div>
          <div class="filter-group">
            <label>Até</label>
            <input type="date" v-model="dateTo" @change="loadStats" />
          </div>
        </div>
      </div>

      <!-- Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Indicações</div>
          <div class="stat-value">{{ stats.referrals ?? 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Vendas</div>
          <div class="stat-value">{{ stats.sales_count ?? 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Total Bruto</div>
          <div class="stat-value">{{ formatCurrency(stats.total_gross) }}</div>
        </div>
        <div class="stat-card highlight">
          <div class="stat-label">Comissão Líquida</div>
          <div class="stat-value">{{ formatCurrency(stats.total_final) }}</div>
        </div>
      </div>

      <!-- Tabela de vendas -->
      <div class="card">
        <div class="card-title">Histórico de Vendas</div>
        <div v-if="stats.sales && stats.sales.length === 0" class="empty">
          Nenhuma venda no período selecionado.
        </div>
        <table v-else class="sales-table">
          <thead>
            <tr>
              <th>Data</th>
              <th>Valor Bruto</th>
              <th>Comissão</th>
              <th>Valor Final</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sale in stats.sales" :key="sale.id">
              <td>{{ formatDate(sale.created_at) }}</td>
              <td>{{ formatCurrency(sale.gross_amount) }}</td>
              <td>{{ formatCurrency(sale.commission) }}</td>
              <td class="final-amount">{{ formatCurrency(sale.final_amount) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { affiliateMe, affiliateDashboard, affiliateLogout } from '@/api/affiliate'

const router = useRouter()
const affiliate = ref(null)
const stats = ref({})
const loading = ref(true)
const dateFrom = ref('')
const dateTo = ref('')
const copied = ref(false)

const affiliateLink = computed(() => {
  if (!affiliate.value) return ''
  const origin = window.location.origin
  return `${origin}/register?ref=${affiliate.value.code}`
})

onMounted(async () => {
  try {
    affiliate.value = await affiliateMe()
    await loadStats()
  } catch {
    router.push('/affiliate/login')
  } finally {
    loading.value = false
  }
})

async function loadStats() {
  try {
    stats.value = await affiliateDashboard(dateFrom.value, dateTo.value)
  } catch {
    stats.value = {}
  }
}

async function handleLogout() {
  await affiliateLogout()
  router.push('/affiliate/login')
}

function copyLink() {
  navigator.clipboard.writeText(affiliateLink.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

function formatCurrency(val) {
  if (val == null) return 'R$ 0,00'
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val)
}

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('pt-BR')
}
</script>

<style scoped>
.affiliate-dashboard {
  min-height: 100vh;
  background: #0f172a;
  color: #f8fafc;
  padding: 0 0 48px;
}

.dash-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 32px;
  background: #1e293b;
  border-bottom: 1px solid #334155;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.dash-header h1 {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}

.code-badge {
  background: rgba(99, 102, 241, 0.15);
  color: #818cf8;
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 20px;
  padding: 4px 14px;
  font-size: 0.8125rem;
  font-weight: 600;
}

.btn-logout {
  background: transparent;
  color: #94a3b8;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-logout:hover {
  color: #f8fafc;
  border-color: #64748b;
}

.loading {
  text-align: center;
  padding: 80px;
  color: #94a3b8;
}

.card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 24px;
  margin: 24px 32px 0;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: #f8fafc;
  margin-bottom: 16px;
}

.link-card .link-row {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 12px 16px;
}

.link-text {
  flex: 1;
  font-family: monospace;
  font-size: 0.875rem;
  color: #94a3b8;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-copy {
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background 0.2s;
}

.btn-copy:hover {
  background: #4f46e5;
}

.filter-card .filter-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-group label {
  font-size: 0.8125rem;
  color: #94a3b8;
}

.filter-group input {
  padding: 8px 12px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  color: #f8fafc;
  font-size: 0.875rem;
  outline: none;
}

.filter-group input:focus {
  border-color: #6366f1;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin: 24px 32px 0;
}

.stat-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 24px;
}

.stat-card.highlight {
  border-color: rgba(99, 102, 241, 0.4);
  background: rgba(99, 102, 241, 0.08);
}

.stat-label {
  font-size: 0.8125rem;
  color: #94a3b8;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #f8fafc;
}

.stat-card.highlight .stat-value {
  color: #818cf8;
}

.empty {
  color: #64748b;
  text-align: center;
  padding: 32px;
  font-size: 0.9375rem;
}

.sales-table {
  width: 100%;
  border-collapse: collapse;
}

.sales-table th {
  text-align: left;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #64748b;
  padding: 8px 12px;
  border-bottom: 1px solid #334155;
}

.sales-table td {
  padding: 12px;
  font-size: 0.9375rem;
  color: #cbd5e1;
  border-bottom: 1px solid #1e293b;
}

.sales-table tr:hover td {
  background: rgba(99, 102, 241, 0.05);
}

.final-amount {
  color: #4ade80;
  font-weight: 600;
}
</style>
