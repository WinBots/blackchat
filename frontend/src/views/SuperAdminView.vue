<template>
  <AppLayout>
    <div class="super-admin-page">
      <div class="card">
      <div class="page-header">
        <div>
          <h2 class="page-title">Super Admin</h2>
          <p class="page-description">Gerencie tenants, usuários e assinaturas de todo o sistema</p>
        </div>
        <button class="btn btn-ghost btn-sm" type="button" @click="load" :disabled="loading">
          {{ loading ? 'Carregando…' : 'Atualizar' }}
        </button>
      </div>

      <div v-if="error" style="padding: 10px 0; color: #ef4444;">
        {{ error }}
      </div>

      <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 16px;">
        <div class="card" style="padding: 14px;">
          <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px;">
            <h3 style="margin: 0; font-size: 1rem;">Tenants</h3>
            <span style="color: var(--muted); font-size: 0.875rem;">{{ tenants.length }}</span>
          </div>

          <div class="table-wrapper" style="margin-top: 10px;">
            <table class="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nome</th>
                  <th>Email</th>
                  <th>Plano</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="5" style="color: var(--muted); padding: 14px;">Carregando…</td>
                </tr>
                <tr v-else-if="tenants.length === 0">
                  <td colspan="5" style="color: var(--muted); padding: 14px;">Nenhum tenant.</td>
                </tr>
                <tr
                  v-else
                  v-for="row in tenants"
                  :key="row.tenant.id"
                  @click="selectTenant(row)"
                  style="cursor: pointer;"
                  :style="selectedTenant?.tenant?.id === row.tenant.id ? 'background: var(--accent-soft);' : ''"
                >
                  <td>{{ row.tenant.id }}</td>
                  <td>{{ row.tenant.name }}</td>
                  <td>{{ row.tenant.email }}</td>
                  <td>{{ row.plan?.display_name || '—' }}</td>
                  <td>{{ row.subscription?.status || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card" style="padding: 14px;">
          <h3 style="margin: 0 0 10px 0; font-size: 1rem;">Editar Tenant</h3>

          <div v-if="!selectedTenant" style="color: var(--muted); padding: 10px 0;">
            Selecione um tenant na lista.
          </div>

          <div v-else>
            <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 10px;">
              <div class="input-group">
                <label class="input-label">Nome</label>
                <input class="input" type="text" v-model="tenantDraft.name" />
              </div>
              <div class="input-group">
                <label class="input-label">Email</label>
                <input class="input" type="text" v-model="tenantDraft.email" />
              </div>
              <div class="input-group">
                <label class="input-label">Timezone</label>
                <input class="input" type="text" v-model="tenantDraft.timezone" placeholder="(ex: America/Sao_Paulo)" />
              </div>
              <div class="input-group">
                <label class="input-label">Ativo</label>
                <select class="input" v-model="tenantDraft.is_active">
                  <option :value="true">Sim</option>
                  <option :value="false">Não</option>
                </select>
              </div>
            </div>

            <div style="margin-top: 14px;">
              <h4 style="margin: 0 0 10px 0; font-size: 0.95rem;">Assinatura</h4>
              <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 10px;">
                <div class="input-group">
                  <label class="input-label">Plano</label>
                  <select class="input" v-model="subDraft.plan_id">
                    <option :value="null">(não definido)</option>
                    <option v-for="p in plans" :key="p.id" :value="p.id">{{ p.display_name }} ({{ fmtPrice(p.price_monthly) }})</option>
                  </select>
                </div>
                <div class="input-group">
                  <label class="input-label">Status</label>
                  <select class="input" v-model="subDraft.status">
                    <option value="trial">trial</option>
                    <option value="active">active</option>
                    <option value="past_due">past_due</option>
                    <option value="canceled">canceled</option>
                    <option value="expired">expired</option>
                  </select>
                </div>
                <div class="input-group">
                  <label class="input-label">Period start (ISO)</label>
                  <input class="input" type="text" v-model="subDraft.current_period_start" placeholder="2026-02-27T02:23:21Z" />
                </div>
                <div class="input-group">
                  <label class="input-label">Trial ends (ISO)</label>
                  <input class="input" type="text" v-model="subDraft.trial_ends_at" placeholder="2026-03-13T02:23:21Z" />
                </div>
                <div class="input-group">
                  <label class="input-label">Period end (ISO)</label>
                  <input class="input" type="text" v-model="subDraft.current_period_end" placeholder="2026-03-13T02:23:21Z" />
                </div>
              </div>
            </div>

            <div style="display: flex; gap: 10px; margin-top: 14px;">
              <button class="btn btn-primary" type="button" @click="saveTenant" :disabled="saving">
                {{ saving ? 'Salvando…' : 'Salvar Tenant' }}
              </button>
              <button class="btn btn-outline" type="button" @click="saveSubscription" :disabled="saving">
                {{ saving ? 'Salvando…' : 'Salvar Assinatura' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="card" style="padding: 14px; margin-top: 16px;">
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px;">
          <h3 style="margin: 0; font-size: 1rem;">Usuários</h3>
          <span style="color: var(--muted); font-size: 0.875rem;">{{ users.length }}</span>
        </div>

        <div class="table-wrapper" style="margin-top: 10px;">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Tenant</th>
                <th>Email</th>
                <th>Nome</th>
                <th>Ativo</th>
                <th>Admin</th>
                <th>Super</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="8" style="color: var(--muted); padding: 14px;">Carregando…</td>
              </tr>
              <tr v-else-if="users.length === 0">
                <td colspan="8" style="color: var(--muted); padding: 14px;">Nenhum usuário.</td>
              </tr>
              <tr v-else v-for="u in users" :key="u.id">
                <td>{{ u.id }}</td>
                <td>{{ u.tenant_id }}</td>
                <td>{{ u.email }}</td>
                <td style="min-width: 220px;">
                  <input class="input" type="text" v-model="u.full_name" />
                </td>
                <td>
                  <select class="input" v-model="u.is_active">
                    <option :value="true">Sim</option>
                    <option :value="false">Não</option>
                  </select>
                </td>
                <td>
                  <select class="input" v-model="u.is_admin">
                    <option :value="true">Sim</option>
                    <option :value="false">Não</option>
                  </select>
                </td>
                <td>
                  <select class="input" v-model="u.is_super_admin">
                    <option :value="true">Sim</option>
                    <option :value="false">Não</option>
                  </select>
                </td>
                <td>
                  <button class="btn btn-ghost btn-sm" type="button" @click="saveUser(u)" :disabled="saving">
                    Salvar
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card" style="padding: 14px; margin-top: 16px;">
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px;">
          <h3 style="margin: 0; font-size: 1rem;">Planos (Stripe price_id)</h3>
          <span style="color: var(--muted); font-size: 0.875rem;">{{ plans.length }}</span>
        </div>

        <div class="table-wrapper" style="margin-top: 10px;">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nome</th>
                <th>Display</th>
                <th>Preço</th>
                <th>Ativo</th>
                <th>Stripe price_id mensal</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="7" style="color: var(--muted); padding: 14px;">Carregando…</td>
              </tr>
              <tr v-else-if="plans.length === 0">
                <td colspan="7" style="color: var(--muted); padding: 14px;">Nenhum plano.</td>
              </tr>
              <tr v-else v-for="p in plans" :key="p.id">
                <td>{{ p.id }}</td>
                <td>{{ p.name }}</td>
                <td>{{ p.display_name }}</td>
                <td style="min-width: 140px;">
                  <input class="input" type="number" step="0.01" v-model="p.price_monthly" />
                </td>
                <td style="min-width: 120px;">
                  <select class="input" v-model="p.is_active">
                    <option :value="true">Sim</option>
                    <option :value="false">Não</option>
                  </select>
                </td>
                <td style="min-width: 320px;">
                  <input class="input" type="text" v-model="p.stripe_price_id_monthly" placeholder="price_..." />
                </td>
                <td>
                  <button class="btn btn-ghost btn-sm" type="button" @click="savePlan(p)" :disabled="saving">
                    Salvar
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useToast } from '@/composables/useToast'
import {
  adminListTenants,
  adminUpdateTenant,
  adminUpdateTenantSubscription,
  adminListUsers,
  adminUpdateUser,
  adminListPlans,
  adminUpdatePlan
} from '@/api/superAdmin'

const router = useRouter()
const toast = useToast()

const loading = ref(false)
const saving = ref(false)
const error = ref('')

const tenants = ref([])
const users = ref([])
const plans = ref([])

const selectedTenant = ref(null)
const tenantDraft = ref({ name: '', email: '', timezone: '', is_active: true })
const subDraft = ref({ plan_id: null, status: 'trial', current_period_start: '', trial_ends_at: '', current_period_end: '' })

const fmtPrice = (v) => {
  const n = Number(v || 0)
  try {
    return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
  } catch {
    return `R$ ${n}`
  }
}

const selectTenant = (row) => {
  selectedTenant.value = row
  tenantDraft.value = {
    name: row.tenant?.name || '',
    email: row.tenant?.email || '',
    timezone: row.tenant?.timezone || '',
    is_active: !!row.tenant?.is_active
  }

  subDraft.value = {
    plan_id: row.subscription?.plan_id ?? null,
    status: row.subscription?.status || 'trial',
    current_period_start: row.subscription?.current_period_start || '',
    trial_ends_at: row.subscription?.trial_ends_at || '',
    current_period_end: row.subscription?.current_period_end || ''
  }
}

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const [t, u, p] = await Promise.all([
      adminListTenants(),
      adminListUsers(),
      adminListPlans()
    ])
    tenants.value = Array.isArray(t) ? t : []
    users.value = Array.isArray(u) ? u : []
    plans.value = Array.isArray(p) ? p : []
  } catch (e) {
    console.error(e)
    const msg = e?.response?.data?.detail || 'Sem permissão (é preciso ser super admin)'
    error.value = msg
    toast.error(msg)
    // se não tem acesso, volta pro dashboard
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}

const saveTenant = async () => {
  if (!selectedTenant.value?.tenant?.id) return
  saving.value = true
  try {
    const updated = await adminUpdateTenant(selectedTenant.value.tenant.id, tenantDraft.value)
    toast.success('Tenant atualizado')
    // Atualiza cache local
    const idx = tenants.value.findIndex(r => r.tenant?.id === updated.id)
    if (idx >= 0) tenants.value[idx].tenant = { ...tenants.value[idx].tenant, ...updated }
  } catch (e) {
    console.error(e)
    toast.error(e?.response?.data?.detail || 'Erro ao salvar tenant')
  } finally {
    saving.value = false
  }
}

const saveSubscription = async () => {
  if (!selectedTenant.value?.tenant?.id) return
  saving.value = true
  try {
    const payload = {
      plan_id: subDraft.value.plan_id,
      status: subDraft.value.status,
      current_period_start: subDraft.value.current_period_start,
      trial_ends_at: subDraft.value.trial_ends_at,
      current_period_end: subDraft.value.current_period_end
    }
    const updated = await adminUpdateTenantSubscription(selectedTenant.value.tenant.id, payload)
    toast.success('Assinatura atualizada')
    const idx = tenants.value.findIndex(r => r.tenant?.id === selectedTenant.value.tenant.id)
    if (idx >= 0) tenants.value[idx].subscription = { ...updated }
  } catch (e) {
    console.error(e)
    toast.error(e?.response?.data?.detail || 'Erro ao salvar assinatura')
  } finally {
    saving.value = false
  }
}

const saveUser = async (u) => {
  if (!u?.id) return
  saving.value = true
  try {
    await adminUpdateUser(u.id, {
      full_name: u.full_name,
      is_active: u.is_active,
      is_admin: u.is_admin,
      is_super_admin: u.is_super_admin
    })
    toast.success('Usuário atualizado')
  } catch (e) {
    console.error(e)
    toast.error(e?.response?.data?.detail || 'Erro ao salvar usuário')
  } finally {
    saving.value = false
  }
}

const savePlan = async (p) => {
  if (!p?.id) return
  saving.value = true
  try {
    await adminUpdatePlan(p.id, {
      price_monthly: p.price_monthly,
      is_active: p.is_active,
      stripe_price_id_monthly: p.stripe_price_id_monthly
    })
    toast.success('Plano atualizado')
  } catch (e) {
    console.error(e)
    toast.error(e?.response?.data?.detail || 'Erro ao salvar plano')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.super-admin-page {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding-bottom: 96px;
  color-scheme: dark;
}

.super-admin-page .input {
  border-radius: var(--radius-sm);
  padding: 10px 12px;
}

.super-admin-page select.input {
  border-radius: var(--radius-sm);
}

.super-admin-page .btn {
  border-radius: var(--radius-sm);
}

.super-admin-page .btn-sm {
  border-radius: var(--radius-sm);
}
</style>
