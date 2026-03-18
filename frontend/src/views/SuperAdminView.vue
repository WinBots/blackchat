<template>
  <AppLayout>
    <div class="super-admin-page">
      <div class="card super-admin-card">
        <div class="page-header super-admin-header">
          <div>
            <h2 class="page-title">Super Admin</h2>
            <p class="page-description">Gerencie tenants, usuários e assinaturas de todo o sistema</p>
          </div>
          <button class="btn btn-ghost btn-sm" type="button" @click="load" :disabled="loading">
            {{ loading ? 'Carregando…' : 'Atualizar' }}
          </button>
        </div>

        <div v-if="loading" class="super-admin-loading loading" aria-busy="true">
          <div class="loading-spinner" aria-hidden="true"></div>
          <div>
            <div class="super-admin-loading-title">Carregando dados…</div>
            <div class="super-admin-loading-subtitle">Tenants, usuários e planos</div>
          </div>
        </div>

        <template v-else>
          <div class="super-admin-tabs" role="tablist" aria-label="Super Admin">
            <button
              type="button"
              class="super-admin-tab"
              :class="activeTab === 'tenants' ? 'super-admin-tab--active' : ''"
              role="tab"
              :aria-selected="activeTab === 'tenants'"
              @click="activeTab = 'tenants'"
            >
              Tenants
              <span class="super-admin-tab-count">{{ tenants.length }}</span>
            </button>
            <button
              type="button"
              class="super-admin-tab"
              :class="activeTab === 'users' ? 'super-admin-tab--active' : ''"
              role="tab"
              :aria-selected="activeTab === 'users'"
              @click="activeTab = 'users'"
            >
              Usuários
              <span class="super-admin-tab-count">{{ users.length }}</span>
            </button>
            <button
              type="button"
              class="super-admin-tab"
              :class="activeTab === 'plans' ? 'super-admin-tab--active' : ''"
              role="tab"
              :aria-selected="activeTab === 'plans'"
              @click="activeTab = 'plans'"
            >
              Planos
              <span class="super-admin-tab-count">{{ plans.length }}</span>
            </button>
            <button
              type="button"
              class="super-admin-tab"
              :class="activeTab === 'stripe' ? 'super-admin-tab--active' : ''"
              role="tab"
              :aria-selected="activeTab === 'stripe'"
              @click="activeTab = 'stripe'; loadStripeConfig()"
            >
              Stripe
              <span v-if="stripeConfig" class="super-admin-tab-badge" :class="stripeConfig.mode_active === 'live' ? 'badge-live' : 'badge-test'">
                {{ stripeConfig.mode_active === 'live' ? 'LIVE' : 'TEST' }}
              </span>
            </button>
            <button
              type="button"
              class="super-admin-tab"
              :class="activeTab === 'subscriptions' ? 'super-admin-tab--active' : ''"
              role="tab"
              :aria-selected="activeTab === 'subscriptions'"
              @click="activeTab = 'subscriptions'; loadSubscriptions()"
            >
              Assinaturas
              <span v-if="subsData.total" class="super-admin-tab-count">{{ subsData.total }}</span>
            </button>
            <button
              type="button"
              class="super-admin-tab"
              :class="activeTab === 'eventlog' ? 'super-admin-tab--active' : ''"
              role="tab"
              :aria-selected="activeTab === 'eventlog'"
              @click="activeTab = 'eventlog'; loadEventLog()"
            >
              Log de Eventos
              <span v-if="eventsData.total" class="super-admin-tab-count">{{ eventsData.total }}</span>
            </button>
          </div>

          <div v-if="error" class="super-admin-error">
            {{ error }}
          </div>

          <div v-if="activeTab === 'tenants'" class="super-admin-tab-panel" role="tabpanel">
          <div class="super-admin-grid">
            <div class="card super-admin-section">
              <div class="super-admin-section-header">
                <div>
                  <h3 class="super-admin-section-title">Lista de tenants</h3>
                  <div class="super-admin-section-subtitle">Selecione para editar</div>
                </div>
                <div class="super-admin-pagination">
                  <span class="super-admin-pagination-range">{{ tenantsRangeLabel }}</span>
                  <select class="input super-admin-page-size" v-model.number="tenantsPageSize" :disabled="loading">
                    <option :value="10">10</option>
                    <option :value="25">25</option>
                    <option :value="50">50</option>
                    <option :value="100">100</option>
                  </select>
                  <button class="btn btn-ghost btn-sm" type="button" @click="tenantsPage--" :disabled="loading || tenantsPage <= 1">Anterior</button>
                  <button class="btn btn-ghost btn-sm" type="button" @click="tenantsPage++" :disabled="loading || tenantsPage >= tenantsTotalPages">Próximo</button>
                </div>
              </div>

              <div class="table-wrapper super-admin-table">
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
                      <td colspan="5" class="super-admin-muted">Carregando…</td>
                    </tr>
                    <tr v-else-if="tenants.length === 0">
                      <td colspan="5" class="super-admin-muted">Nenhum tenant.</td>
                    </tr>
                    <tr
                      v-else
                      v-for="row in pagedTenants"
                      :key="row.tenant.id"
                      class="super-admin-row-clickable"
                      :class="selectedTenant?.tenant?.id === row.tenant.id ? 'super-admin-row-selected' : ''"
                      @click="selectTenant(row)"
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

            <div class="card super-admin-section">
              <div class="super-admin-section-header">
                <div>
                  <h3 class="super-admin-section-title">Edição do tenant</h3>
                  <div class="super-admin-section-subtitle" v-if="selectedTenant">
                    <span class="super-admin-tenant-pill">
                      ID {{ selectedTenant.tenant.id }} • {{ selectedTenant.tenant.name }}
                    </span>
                  </div>
                  <div class="super-admin-section-subtitle" v-else>Selecione um tenant na lista</div>
                </div>
              </div>

              <div v-if="!selectedTenant" class="super-admin-muted-block">
                Selecione um tenant para editar dados e assinatura.
              </div>

              <div v-else>
                <div class="super-admin-tenant-summary">
                  <div class="super-admin-summary-item">
                    <div class="super-admin-summary-label">Status</div>
                    <div class="super-admin-summary-value">{{ selectedTenant.subscription?.status || '—' }}</div>
                  </div>
                  <div class="super-admin-summary-item">
                    <div class="super-admin-summary-label">Plano</div>
                    <div class="super-admin-summary-value">{{ selectedTenant.plan?.display_name || '—' }}</div>
                  </div>
                  <div class="super-admin-summary-item">
                    <div class="super-admin-summary-label">Stripe customer</div>
                    <div class="super-admin-summary-value">{{ selectedTenant.tenant?.stripe_customer_id || '—' }}</div>
                  </div>
                </div>

                <div class="super-admin-subsection">
                  <h4 class="super-admin-subtitle">Dados do tenant</h4>
                  <div class="super-admin-form-grid">
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
                  <div class="super-admin-actions">
                    <button class="btn btn-primary" type="button" @click="saveTenant" :disabled="savingTenant">
                      {{ savingTenant ? 'Salvando…' : 'Salvar dados do tenant' }}
                    </button>
                  </div>
                </div>

                <div class="super-admin-subsection">
                  <h4 class="super-admin-subtitle">Assinatura</h4>
                  <div class="super-admin-form-grid">
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
                      <label class="input-label">Period start</label>
                      <input class="input" type="text" v-model="subDraft.current_period_start" placeholder="2026-03-17 06:15:41" />
                    </div>
                    <div class="input-group">
                      <label class="input-label">Trial ends</label>
                      <input class="input" type="text" v-model="subDraft.trial_ends_at" placeholder="2026-04-18 06:15:41" />
                    </div>
                    <div class="input-group">
                      <label class="input-label">Period end</label>
                      <input class="input" type="text" v-model="subDraft.current_period_end" placeholder="2026-04-18 06:15:41" />
                    </div>
                  </div>
                  <div class="super-admin-actions">
                    <button class="btn btn-outline" type="button" @click="saveSubscription" :disabled="savingSubscription">
                      {{ savingSubscription ? 'Salvando…' : 'Salvar assinatura' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="activeTab === 'users'" class="super-admin-tab-panel" role="tabpanel">
          <div class="card super-admin-section super-admin-section--full">
            <div class="super-admin-section-header">
              <div>
                <h3 class="super-admin-section-title">Usuários</h3>
                <div class="super-admin-section-subtitle">{{ users.length }} no total</div>
              </div>
              <div class="super-admin-pagination">
                <span class="super-admin-pagination-range">{{ usersRangeLabel }}</span>
                <select class="input super-admin-page-size" v-model.number="usersPageSize" :disabled="loading">
                  <option :value="10">10</option>
                  <option :value="25">25</option>
                  <option :value="50">50</option>
                  <option :value="100">100</option>
                </select>
                <button class="btn btn-ghost btn-sm" type="button" @click="usersPage--" :disabled="loading || usersPage <= 1">Anterior</button>
                <button class="btn btn-ghost btn-sm" type="button" @click="usersPage++" :disabled="loading || usersPage >= usersTotalPages">Próximo</button>
              </div>
            </div>

            <div class="table-wrapper super-admin-table">
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
                    <td colspan="8" class="super-admin-muted">Carregando…</td>
                  </tr>
                  <tr v-else-if="users.length === 0">
                    <td colspan="8" class="super-admin-muted">Nenhum usuário.</td>
                  </tr>
                  <tr v-else v-for="u in pagedUsers" :key="u.id">
                    <td>{{ u.id }}</td>
                    <td>{{ u.tenant_id }}</td>
                    <td>{{ u.email }}</td>
                    <td class="super-admin-cell-wide">
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
                      <button class="btn btn-ghost btn-sm" type="button" @click="saveUser(u)" :disabled="savingUserId === u.id">
                        {{ savingUserId === u.id ? 'Salvando…' : 'Salvar' }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div v-else-if="activeTab === 'plans'" class="super-admin-tab-panel" role="tabpanel">
          <div class="card super-admin-section super-admin-section--full">
            <div class="super-admin-section-header">
              <div>
                <h3 class="super-admin-section-title">Planos (Stripe price_id)</h3>
                <div class="super-admin-section-subtitle">{{ plans.length }} no total</div>
              </div>
              <div class="super-admin-pagination">
                <span class="super-admin-pagination-range">{{ plansRangeLabel }}</span>
                <select class="input super-admin-page-size" v-model.number="plansPageSize" :disabled="loading">
                  <option :value="10">10</option>
                  <option :value="25">25</option>
                  <option :value="50">50</option>
                  <option :value="100">100</option>
                </select>
                <button class="btn btn-ghost btn-sm" type="button" @click="plansPage--" :disabled="loading || plansPage <= 1">Anterior</button>
                <button class="btn btn-ghost btn-sm" type="button" @click="plansPage++" :disabled="loading || plansPage >= plansTotalPages">Próximo</button>
              </div>
            </div>

            <div class="table-wrapper super-admin-table">
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
                    <td colspan="7" class="super-admin-muted">Carregando…</td>
                  </tr>
                  <tr v-else-if="plans.length === 0">
                    <td colspan="7" class="super-admin-muted">Nenhum plano.</td>
                  </tr>
                  <tr v-else v-for="p in pagedPlans" :key="p.id">
                    <td>{{ p.id }}</td>
                    <td>{{ p.name }}</td>
                    <td>{{ p.display_name }}</td>
                    <td class="super-admin-cell-narrow">
                      <input class="input" type="number" step="0.01" v-model="p.price_monthly" />
                    </td>
                    <td class="super-admin-cell-narrow">
                      <select class="input" v-model="p.is_active">
                        <option :value="true">Sim</option>
                        <option :value="false">Não</option>
                      </select>
                    </td>
                    <td class="super-admin-cell-xl">
                      <input class="input" type="text" v-model="p.stripe_price_id_monthly" placeholder="price_..." />
                    </td>
                    <td>
                      <button class="btn btn-ghost btn-sm" type="button" @click="savePlan(p)" :disabled="savingPlanId === p.id">
                        {{ savingPlanId === p.id ? 'Salvando…' : 'Salvar' }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div v-else-if="activeTab === 'stripe'" class="super-admin-tab-panel" role="tabpanel">
          <div class="card super-admin-section super-admin-section--full">
            <div class="super-admin-section-header">
              <div>
                <h3 class="super-admin-section-title">Configuração Stripe</h3>
                <div class="super-admin-section-subtitle">Chaves e produtos para integração com Stripe</div>
              </div>
            </div>

            <div v-if="stripeLoadError" class="super-admin-error">{{ stripeLoadError }}</div>

            <div v-if="stripeConfig" class="stripe-config-section">
              <!-- Checklist de validação -->
              <div class="stripe-validation">
                <span class="stripe-validation-item" :class="stripeConfig.test_secret_key_set ? 'valid' : 'invalid'">TEST secret_key</span>
                <span class="stripe-validation-item" :class="stripeConfig.test_pro_price_id ? 'valid' : 'invalid'">TEST pro_price_id</span>
                <span class="stripe-validation-item" :class="stripeConfig.test_enterprise_product_id ? 'valid' : 'invalid'">TEST enterprise_product_id</span>
                <span class="stripe-validation-item" :class="stripeConfig.live_secret_key_set ? 'valid' : 'invalid'">LIVE secret_key</span>
                <span class="stripe-validation-item" :class="stripeConfig.live_pro_price_id ? 'valid' : 'invalid'">LIVE pro_price_id</span>
                <span class="stripe-validation-item" :class="stripeConfig.live_enterprise_product_id ? 'valid' : 'invalid'">LIVE enterprise_product_id</span>
              </div>

              <!-- Modo Atual -->
              <div class="stripe-mode-box" :class="stripeConfig.mode_active === 'live' ? 'stripe-mode-live' : 'stripe-mode-test'">
                <div class="stripe-mode-label">
                  <strong>Modo ativo:</strong>
                  <span class="super-admin-tab-badge" :class="stripeConfig.mode_active === 'live' ? 'badge-live' : 'badge-test'">{{ stripeConfig.mode_active?.toUpperCase() }}</span>
                </div>
                <div v-if="stripeConfig.mode_active === 'live'" class="stripe-mode-warn">⚠ Modo LIVE ativo — transações reais</div>
                <div class="stripe-mode-actions">
                  <button class="btn btn-ghost btn-sm" type="button" :disabled="stripeConfig.mode_active === 'test' || stripeSaving" @click="toggleStripeMode('test')">Usar TEST</button>
                  <button class="btn btn-danger btn-sm" type="button" :disabled="stripeConfig.mode_active === 'live' || stripeSaving" @click="toggleStripeMode('live')">Usar LIVE</button>
                </div>
              </div>

              <!-- Credenciais TEST -->
              <div class="super-admin-subsection">
                <h4 class="super-admin-subtitle">Credenciais TEST</h4>
                <div class="super-admin-form-grid">
                  <div class="input-group">
                    <label class="input-label">Secret Key <span v-if="stripeConfig.test_secret_key_set" class="stripe-key-set">✓ definida</span></label>
                    <div class="stripe-secret-wrap">
                      <input class="input" :type="showKeys.test_secret_key ? 'text' : 'password'" v-model="stripeDraft.test_secret_key"
                        :placeholder="stripeConfig.test_secret_key_masked || 'sk_test_…'" autocomplete="off" />
                      <button type="button" class="stripe-eye-btn" @click="showKeys.test_secret_key = !showKeys.test_secret_key" :title="showKeys.test_secret_key ? 'Ocultar' : 'Mostrar'">
                        <svg v-if="!showKeys.test_secret_key" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                        <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                      </button>
                    </div>
                  </div>
                  <div class="input-group">
                    <label class="input-label">Publishable Key <span v-if="stripeConfig.test_publishable_key" class="stripe-key-set">✓</span></label>
                    <input class="input" type="text" v-model="stripeDraft.test_publishable_key" placeholder="pk_test_…" />
                  </div>
                  <div class="input-group">
                    <label class="input-label">Webhook Secret <span v-if="stripeConfig.test_webhook_secret_set" class="stripe-key-set">✓ definida</span></label>
                    <div class="stripe-secret-wrap">
                      <input class="input" :type="showKeys.test_webhook_secret ? 'text' : 'password'" v-model="stripeDraft.test_webhook_secret"
                        :placeholder="stripeConfig.test_webhook_secret_masked || 'whsec_…'" autocomplete="off" />
                      <button type="button" class="stripe-eye-btn" @click="showKeys.test_webhook_secret = !showKeys.test_webhook_secret" :title="showKeys.test_webhook_secret ? 'Ocultar' : 'Mostrar'">
                        <svg v-if="!showKeys.test_webhook_secret" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                        <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                      </button>
                    </div>
                  </div>
                  <div class="input-group">
                    <label class="input-label">Pro Price ID <span v-if="stripeConfig.test_pro_price_id" class="stripe-key-set">✓</span></label>
                    <input class="input" type="text" v-model="stripeDraft.test_pro_price_id" placeholder="price_test_…" />
                  </div>
                  <div class="input-group">
                    <label class="input-label">Enterprise Product ID <span v-if="stripeConfig.test_enterprise_product_id" class="stripe-key-set">✓</span></label>
                    <input class="input" type="text" v-model="stripeDraft.test_enterprise_product_id" placeholder="prod_test_…" />
                  </div>
                </div>
              </div>

              <!-- Credenciais LIVE -->
              <div class="super-admin-subsection">
                <h4 class="super-admin-subtitle">Credenciais LIVE</h4>
                <div class="super-admin-form-grid">
                  <div class="input-group">
                    <label class="input-label">Secret Key <span v-if="stripeConfig.live_secret_key_set" class="stripe-key-set">✓ definida</span></label>
                    <div class="stripe-secret-wrap">
                      <input class="input" :type="showKeys.live_secret_key ? 'text' : 'password'" v-model="stripeDraft.live_secret_key"
                        :placeholder="stripeConfig.live_secret_key_masked || 'sk_live_…'" autocomplete="off" />
                      <button type="button" class="stripe-eye-btn" @click="showKeys.live_secret_key = !showKeys.live_secret_key" :title="showKeys.live_secret_key ? 'Ocultar' : 'Mostrar'">
                        <svg v-if="!showKeys.live_secret_key" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                        <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                      </button>
                    </div>
                  </div>
                  <div class="input-group">
                    <label class="input-label">Publishable Key <span v-if="stripeConfig.live_publishable_key" class="stripe-key-set">✓</span></label>
                    <input class="input" type="text" v-model="stripeDraft.live_publishable_key" placeholder="pk_live_…" />
                  </div>
                  <div class="input-group">
                    <label class="input-label">Webhook Secret <span v-if="stripeConfig.live_webhook_secret_set" class="stripe-key-set">✓ definida</span></label>
                    <div class="stripe-secret-wrap">
                      <input class="input" :type="showKeys.live_webhook_secret ? 'text' : 'password'" v-model="stripeDraft.live_webhook_secret"
                        :placeholder="stripeConfig.live_webhook_secret_masked || 'whsec_…'" autocomplete="off" />
                      <button type="button" class="stripe-eye-btn" @click="showKeys.live_webhook_secret = !showKeys.live_webhook_secret" :title="showKeys.live_webhook_secret ? 'Ocultar' : 'Mostrar'">
                        <svg v-if="!showKeys.live_webhook_secret" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                        <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                      </button>
                    </div>
                  </div>
                  <div class="input-group">
                    <label class="input-label">Pro Price ID <span v-if="stripeConfig.live_pro_price_id" class="stripe-key-set">✓</span></label>
                    <input class="input" type="text" v-model="stripeDraft.live_pro_price_id" placeholder="price_live_…" />
                  </div>
                  <div class="input-group">
                    <label class="input-label">Enterprise Product ID <span v-if="stripeConfig.live_enterprise_product_id" class="stripe-key-set">✓</span></label>
                    <input class="input" type="text" v-model="stripeDraft.live_enterprise_product_id" placeholder="prod_live_…" />
                  </div>
                </div>
              </div>

              <div class="super-admin-actions">
                <button class="btn btn-primary" type="button" @click="saveStripeConfig" :disabled="stripeSaving">
                  {{ stripeSaving ? 'Salvando…' : 'Salvar configuração Stripe' }}
                </button>
              </div>
            </div>

            <div v-else class="super-admin-muted-block">
              <button class="btn btn-ghost" type="button" @click="loadStripeConfig">Carregar configuração</button>
            </div>
          </div>
        </div>

        <!-- ═══ Assinaturas ════════════════════════════════════════════════ -->
        <div v-else-if="activeTab === 'subscriptions'" class="super-admin-tab-panel" role="tabpanel">
          <div class="card super-admin-section super-admin-section--full">
            <div class="super-admin-section-header">
              <div>
                <h3 class="super-admin-section-title">Todas as Assinaturas</h3>
                <div class="super-admin-section-subtitle">Listagem completa com filtros</div>
              </div>
              <button class="btn btn-ghost btn-sm" type="button" @click="loadSubscriptions" :disabled="subsLoading">
                {{ subsLoading ? 'Carregando…' : 'Atualizar' }}
              </button>
            </div>

            <!-- Filtros -->
            <div class="sa-filters">
              <div class="sa-filter-row">
                <input class="input sa-filter-input" type="text" v-model="subsFilters.search" placeholder="Buscar por nome ou email…" @keyup.enter="subsPage = 1; loadSubscriptions()" />
                <select class="input sa-filter-select" v-model="subsFilters.status" @change="subsPage = 1; loadSubscriptions()">
                  <option value="">Todos os status</option>
                  <option value="trial">Trial</option>
                  <option value="active">Active</option>
                  <option value="past_due">Past Due</option>
                  <option value="unpaid">Unpaid</option>
                  <option value="canceled">Canceled</option>
                  <option value="expired">Expired</option>
                </select>
                <select class="input sa-filter-select" v-model="subsFilters.plan_id" @change="subsPage = 1; loadSubscriptions()">
                  <option value="">Todos os planos</option>
                  <option v-for="p in plans" :key="p.id" :value="p.id">{{ p.display_name }}</option>
                </select>
                <select class="input sa-filter-select" v-model="subsFilters.stripe_mode" @change="subsPage = 1; loadSubscriptions()">
                  <option value="">Modo Stripe</option>
                  <option value="test">Test</option>
                  <option value="live">Live</option>
                </select>
              </div>
              <div class="sa-filter-row">
                <div class="sa-filter-date-group">
                  <label class="sa-filter-date-label">De:</label>
                  <input class="input sa-filter-date" type="date" v-model="subsFilters.date_from" @change="subsPage = 1; loadSubscriptions()" />
                </div>
                <div class="sa-filter-date-group">
                  <label class="sa-filter-date-label">Até:</label>
                  <input class="input sa-filter-date" type="date" v-model="subsFilters.date_to" @change="subsPage = 1; loadSubscriptions()" />
                </div>
                <button class="btn btn-ghost btn-sm" type="button" @click="clearSubsFilters">Limpar filtros</button>
                <button class="btn btn-primary btn-sm" type="button" @click="subsPage = 1; loadSubscriptions()">Buscar</button>
              </div>
            </div>

            <!-- Paginação -->
            <div class="super-admin-pagination">
              <span class="super-admin-pagination-range">{{ subsRangeLabel }}</span>
              <select class="input super-admin-page-size" v-model.number="subsPageSize" @change="subsPage = 1; loadSubscriptions()">
                <option :value="10">10</option>
                <option :value="25">25</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
              </select>
              <button class="btn btn-ghost btn-sm" type="button" @click="subsPage--; loadSubscriptions()" :disabled="subsLoading || subsPage <= 1">Anterior</button>
              <button class="btn btn-ghost btn-sm" type="button" @click="subsPage++; loadSubscriptions()" :disabled="subsLoading || subsPage >= subsData.total_pages">Próximo</button>
            </div>

            <!-- Tabela -->
            <div class="table-wrapper super-admin-table">
              <table class="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Tenant</th>
                    <th>Owner</th>
                    <th>Plano</th>
                    <th>Status</th>
                    <th>Modo</th>
                    <th>Valor/mês</th>
                    <th>Início</th>
                    <th>Período fim</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="subsLoading">
                    <td colspan="9" class="super-admin-muted">Carregando…</td>
                  </tr>
                  <tr v-else-if="subsData.items.length === 0">
                    <td colspan="9" class="super-admin-muted">Nenhuma assinatura encontrada.</td>
                  </tr>
                  <tr v-else v-for="s in subsData.items" :key="s.id">
                    <td>{{ s.id }}</td>
                    <td>
                      <div class="sa-cell-tenant">
                        <span class="sa-cell-name">{{ s.tenant_name || '—' }}</span>
                        <span class="sa-cell-email">{{ s.tenant_email || '' }}</span>
                      </div>
                    </td>
                    <td>{{ s.owner_name || '—' }}</td>
                    <td>
                      <span class="sa-pill sa-pill--plan">{{ s.plan_name || '—' }}</span>
                    </td>
                    <td>
                      <span class="sa-pill" :class="'sa-status--' + s.status">{{ s.status }}</span>
                    </td>
                    <td>
                      <span v-if="s.stripe_mode" class="super-admin-tab-badge" :class="s.stripe_mode === 'live' ? 'badge-live' : 'badge-test'">{{ s.stripe_mode?.toUpperCase() }}</span>
                      <span v-else class="super-admin-muted">—</span>
                    </td>
                    <td>{{ s.monthly_amount_cents ? fmtCents(s.monthly_amount_cents) : '—' }}</td>
                    <td>{{ s.started_at || '—' }}</td>
                    <td>{{ s.current_period_end || '—' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- ═══ Log de Eventos ═════════════════════════════════════════════ -->
        <div v-else-if="activeTab === 'eventlog'" class="super-admin-tab-panel" role="tabpanel">
          <div class="card super-admin-section super-admin-section--full">
            <div class="super-admin-section-header">
              <div>
                <h3 class="super-admin-section-title">Log de Eventos</h3>
                <div class="super-admin-section-subtitle">Histórico de assinaturas, webhooks Stripe e limites</div>
              </div>
              <button class="btn btn-ghost btn-sm" type="button" @click="loadEventLog" :disabled="eventsLoading">
                {{ eventsLoading ? 'Carregando…' : 'Atualizar' }}
              </button>
            </div>

            <!-- Filtros -->
            <div class="sa-filters">
              <div class="sa-filter-row">
                <input class="input sa-filter-input" type="text" v-model="eventsFilters.search" placeholder="Buscar evento…" @keyup.enter="eventsPage = 1; loadEventLog()" />
                <select class="input sa-filter-select" v-model="eventsFilters.source" @change="eventsPage = 1; loadEventLog()">
                  <option value="">Todas as fontes</option>
                  <option value="subscription">Assinatura</option>
                  <option value="stripe">Stripe Webhook</option>
                  <option value="limit">Limite</option>
                </select>
                <div class="sa-filter-date-group">
                  <label class="sa-filter-date-label">De:</label>
                  <input class="input sa-filter-date" type="date" v-model="eventsFilters.date_from" @change="eventsPage = 1; loadEventLog()" />
                </div>
                <div class="sa-filter-date-group">
                  <label class="sa-filter-date-label">Até:</label>
                  <input class="input sa-filter-date" type="date" v-model="eventsFilters.date_to" @change="eventsPage = 1; loadEventLog()" />
                </div>
                <button class="btn btn-ghost btn-sm" type="button" @click="clearEventsFilters">Limpar</button>
                <button class="btn btn-primary btn-sm" type="button" @click="eventsPage = 1; loadEventLog()">Buscar</button>
              </div>
            </div>

            <!-- Paginação -->
            <div class="super-admin-pagination">
              <span class="super-admin-pagination-range">{{ eventsRangeLabel }}</span>
              <select class="input super-admin-page-size" v-model.number="eventsPageSize" @change="eventsPage = 1; loadEventLog()">
                <option :value="10">10</option>
                <option :value="25">25</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
              </select>
              <button class="btn btn-ghost btn-sm" type="button" @click="eventsPage--; loadEventLog()" :disabled="eventsLoading || eventsPage <= 1">Anterior</button>
              <button class="btn btn-ghost btn-sm" type="button" @click="eventsPage++; loadEventLog()" :disabled="eventsLoading || eventsPage >= eventsData.total_pages">Próximo</button>
            </div>

            <!-- Tabela Eventos -->
            <div class="table-wrapper super-admin-table">
              <table class="table">
                <thead>
                  <tr>
                    <th>Data</th>
                    <th>Fonte</th>
                    <th>Tipo</th>
                    <th>Tenant</th>
                    <th>Descrição</th>
                    <th>Modo</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="eventsLoading">
                    <td colspan="6" class="super-admin-muted">Carregando…</td>
                  </tr>
                  <tr v-else-if="eventsData.items.length === 0">
                    <td colspan="6" class="super-admin-muted">Nenhum evento encontrado.</td>
                  </tr>
                  <tr v-else v-for="(ev, idx) in eventsData.items" :key="idx" class="sa-event-row" :class="'sa-event--' + ev.source">
                    <td class="sa-cell-mono">{{ ev.created_at || '—' }}</td>
                    <td>
                      <span class="sa-pill" :class="'sa-source--' + ev.source">{{ sourceLabel(ev.source) }}</span>
                    </td>
                    <td class="sa-cell-mono">{{ ev.event_type }}</td>
                    <td>
                      <span v-if="ev.tenant_name">{{ ev.tenant_name }}</span>
                      <span v-else-if="ev.tenant_id" class="super-admin-muted">ID {{ ev.tenant_id }}</span>
                      <span v-else class="super-admin-muted">—</span>
                    </td>
                    <td class="sa-cell-desc">{{ ev.description }}</td>
                    <td>
                      <span v-if="ev.stripe_mode" class="super-admin-tab-badge" :class="ev.stripe_mode === 'live' ? 'badge-live' : 'badge-test'">{{ ev.stripe_mode?.toUpperCase() }}</span>
                      <span v-else class="super-admin-muted">—</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        </template>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
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
  adminUpdatePlan,
  adminListSubscriptions,
  adminListEventLog
} from '@/api/superAdmin'
import { getStripeConfig, updateStripeConfig, setStripeMode } from '@/api/stripeConfig'

const router = useRouter()
const toast = useToast()

const loading = ref(false)
const savingTenant = ref(false)
const savingSubscription = ref(false)
const savingUserId = ref(null)
const savingPlanId = ref(null)
const error = ref('')

// ── Stripe ────────────────────────────────────────────────────────────────
const stripeConfig = ref(null)
const stripeLoadError = ref('')
const stripeSaving = ref(false)
const showKeys = ref({
  test_secret_key: false,
  test_webhook_secret: false,
  live_secret_key: false,
  live_webhook_secret: false,
})
const stripeDraft = ref({
  test_secret_key: '',
  test_publishable_key: '',
  test_webhook_secret: '',
  test_pro_price_id: '',
  test_enterprise_product_id: '',
  live_secret_key: '',
  live_publishable_key: '',
  live_webhook_secret: '',
  live_pro_price_id: '',
  live_enterprise_product_id: ''
})

const activeTab = ref('tenants')

const tenants = ref([])
const users = ref([])
const plans = ref([])

const selectedTenant = ref(null)
const tenantDraft = ref({ name: '', email: '', timezone: '', is_active: true })
const subDraft = ref({ plan_id: null, status: 'trial', current_period_start: '', trial_ends_at: '', current_period_end: '' })

// Pagination states
const tenantsPage = ref(1)
const tenantsPageSize = ref(25)
const usersPage = ref(1)
const usersPageSize = ref(25)
const plansPage = ref(1)
const plansPageSize = ref(25)

const tenantsTotalPages = computed(() => Math.max(1, Math.ceil((tenants.value?.length || 0) / tenantsPageSize.value)))
const usersTotalPages = computed(() => Math.max(1, Math.ceil((users.value?.length || 0) / usersPageSize.value)))
const plansTotalPages = computed(() => Math.max(1, Math.ceil((plans.value?.length || 0) / plansPageSize.value)))

const pagedTenants = computed(() => {
  const start = (tenantsPage.value - 1) * tenantsPageSize.value
  return (tenants.value || []).slice(start, start + tenantsPageSize.value)
})

const pagedUsers = computed(() => {
  const start = (usersPage.value - 1) * usersPageSize.value
  return (users.value || []).slice(start, start + usersPageSize.value)
})

const pagedPlans = computed(() => {
  const start = (plansPage.value - 1) * plansPageSize.value
  return (plans.value || []).slice(start, start + plansPageSize.value)
})

const makeRangeLabel = (total, page, pageSize) => {
  const n = Number(total || 0)
  if (n <= 0) return '0–0 de 0'
  const start = (page - 1) * pageSize + 1
  const end = Math.min(n, page * pageSize)
  return `${start}–${end} de ${n}`
}

const tenantsRangeLabel = computed(() => makeRangeLabel(tenants.value.length, tenantsPage.value, tenantsPageSize.value))
const usersRangeLabel = computed(() => makeRangeLabel(users.value.length, usersPage.value, usersPageSize.value))
const plansRangeLabel = computed(() => makeRangeLabel(plans.value.length, plansPage.value, plansPageSize.value))

watch(tenantsTotalPages, (tp) => {
  if (tenantsPage.value > tp) tenantsPage.value = tp
})
watch(usersTotalPages, (tp) => {
  if (usersPage.value > tp) usersPage.value = tp
})
watch(plansTotalPages, (tp) => {
  if (plansPage.value > tp) plansPage.value = tp
})
watch(tenantsPageSize, () => { tenantsPage.value = 1 })
watch(usersPageSize, () => { usersPage.value = 1 })
watch(plansPageSize, () => { plansPage.value = 1 })

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

    // Reset pagination to first page when data refreshes
    tenantsPage.value = 1
    usersPage.value = 1
    plansPage.value = 1
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
  savingTenant.value = true
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
    savingTenant.value = false
  }
}

const saveSubscription = async () => {
  if (!selectedTenant.value?.tenant?.id) return
  savingSubscription.value = true
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
    savingSubscription.value = false
  }
}

const saveUser = async (u) => {
  if (!u?.id) return
  savingUserId.value = u.id
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
    if (savingUserId.value === u.id) savingUserId.value = null
  }
}

const savePlan = async (p) => {
  if (!p?.id) return
  savingPlanId.value = p.id
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
    if (savingPlanId.value === p.id) savingPlanId.value = null
  }
}

const loadStripeConfig = async () => {
  stripeLoadError.value = ''
  try {
    stripeConfig.value = await getStripeConfig()
    // Pré-popula campos não-sensíveis no draft para que fiquem visíveis ao usuário
    const c = stripeConfig.value
    stripeDraft.value.test_publishable_key      = c.test_publishable_key || ''
    stripeDraft.value.test_pro_price_id         = c.test_pro_price_id || ''
    stripeDraft.value.test_enterprise_product_id = c.test_enterprise_product_id || ''
    stripeDraft.value.live_publishable_key      = c.live_publishable_key || ''
    stripeDraft.value.live_pro_price_id         = c.live_pro_price_id || ''
    stripeDraft.value.live_enterprise_product_id = c.live_enterprise_product_id || ''
    // Campos sensíveis ficam em branco (o placeholder mostra a versão mascarada)
    stripeDraft.value.test_secret_key    = ''
    stripeDraft.value.test_webhook_secret = ''
    stripeDraft.value.live_secret_key    = ''
    stripeDraft.value.live_webhook_secret = ''
  } catch (e) {
    console.error(e)
    stripeLoadError.value = e?.response?.data?.detail || 'Erro ao carregar configuração Stripe'
  }
}

const saveStripeConfig = async () => {
  stripeSaving.value = true
  try {
    // Monta payload com todos os campos do draft (vazios limpam o campo no banco)
    const payload = { ...stripeDraft.value }
    // Campos sensíveis vazios são omitidos (não apagar acidentalmente)
    const sensitiveFields = ['test_secret_key', 'test_webhook_secret', 'live_secret_key', 'live_webhook_secret']
    sensitiveFields.forEach(k => {
      if (!payload[k] || !payload[k].trim()) delete payload[k]
    })
    stripeConfig.value = await updateStripeConfig(payload)
    // Mantém campos públicos no draft com valores salvos; limpa apenas os sensíveis
    const c = stripeConfig.value
    stripeDraft.value.test_publishable_key       = c.test_publishable_key || ''
    stripeDraft.value.test_pro_price_id          = c.test_pro_price_id || ''
    stripeDraft.value.test_enterprise_product_id = c.test_enterprise_product_id || ''
    stripeDraft.value.live_publishable_key       = c.live_publishable_key || ''
    stripeDraft.value.live_pro_price_id          = c.live_pro_price_id || ''
    stripeDraft.value.live_enterprise_product_id = c.live_enterprise_product_id || ''
    stripeDraft.value.test_secret_key    = ''
    stripeDraft.value.test_webhook_secret = ''
    stripeDraft.value.live_secret_key    = ''
    stripeDraft.value.live_webhook_secret = ''
    toast.success('Configuração Stripe salva!')
  } catch (e) {
    console.error(e)
    toast.error(e?.response?.data?.detail || 'Erro ao salvar configuração Stripe')
  } finally {
    stripeSaving.value = false
  }
}

const toggleStripeMode = async (mode) => {
  if (mode === 'live') {
    const ok = window.confirm(
      'Tem certeza que deseja ativar o modo LIVE?\nTransações reais serão cobradas dos clientes.'
    )
    if (!ok) return
  }
  stripeSaving.value = true
  try {
    stripeConfig.value = await setStripeMode(mode)
    toast.success(`Stripe agora em modo ${mode.toUpperCase()}`)
  } catch (e) {
    console.error(e)
    toast.error(e?.response?.data?.detail || 'Erro ao alternar modo Stripe')
  } finally {
    stripeSaving.value = false
  }
}

// ── Assinaturas (aba) ─────────────────────────────────────────────────────
const subsLoading = ref(false)
const subsPage = ref(1)
const subsPageSize = ref(25)
const subsFilters = ref({ search: '', status: '', plan_id: '', stripe_mode: '', date_from: '', date_to: '' })
const subsData = ref({ items: [], total: 0, page: 1, page_size: 25, total_pages: 1 })

const subsRangeLabel = computed(() => makeRangeLabel(subsData.value.total, subsPage.value, subsPageSize.value))

const loadSubscriptions = async () => {
  subsLoading.value = true
  try {
    const params = { page: subsPage.value, page_size: subsPageSize.value }
    if (subsFilters.value.search) params.search = subsFilters.value.search
    if (subsFilters.value.status) params.status = subsFilters.value.status
    if (subsFilters.value.plan_id) params.plan_id = subsFilters.value.plan_id
    if (subsFilters.value.stripe_mode) params.stripe_mode = subsFilters.value.stripe_mode
    if (subsFilters.value.date_from) params.date_from = subsFilters.value.date_from
    if (subsFilters.value.date_to) params.date_to = subsFilters.value.date_to
    subsData.value = await adminListSubscriptions(params)
  } catch (e) {
    console.error(e)
    toast.error(e?.response?.data?.detail || 'Erro ao carregar assinaturas')
  } finally {
    subsLoading.value = false
  }
}

const clearSubsFilters = () => {
  subsFilters.value = { search: '', status: '', plan_id: '', stripe_mode: '', date_from: '', date_to: '' }
  subsPage.value = 1
  loadSubscriptions()
}

const fmtCents = (cents) => {
  const val = Number(cents || 0) / 100
  try {
    return val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
  } catch {
    return `R$ ${val.toFixed(2)}`
  }
}

// ── Log de Eventos (aba) ──────────────────────────────────────────────────
const eventsLoading = ref(false)
const eventsPage = ref(1)
const eventsPageSize = ref(25)
const eventsFilters = ref({ search: '', source: '', date_from: '', date_to: '' })
const eventsData = ref({ items: [], total: 0, page: 1, page_size: 25, total_pages: 1 })

const eventsRangeLabel = computed(() => makeRangeLabel(eventsData.value.total, eventsPage.value, eventsPageSize.value))

const loadEventLog = async () => {
  eventsLoading.value = true
  try {
    const params = { page: eventsPage.value, page_size: eventsPageSize.value }
    if (eventsFilters.value.search) params.search = eventsFilters.value.search
    if (eventsFilters.value.source) params.source = eventsFilters.value.source
    if (eventsFilters.value.date_from) params.date_from = eventsFilters.value.date_from
    if (eventsFilters.value.date_to) params.date_to = eventsFilters.value.date_to
    eventsData.value = await adminListEventLog(params)
  } catch (e) {
    console.error(e)
    toast.error(e?.response?.data?.detail || 'Erro ao carregar log de eventos')
  } finally {
    eventsLoading.value = false
  }
}

const clearEventsFilters = () => {
  eventsFilters.value = { search: '', source: '', date_from: '', date_to: '' }
  eventsPage.value = 1
  loadEventLog()
}

const sourceLabel = (src) => {
  const map = { subscription: 'Assinatura', stripe: 'Stripe', limit: 'Limite' }
  return map[src] || src
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

.super-admin-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.super-admin-header {
  margin-bottom: 0;
}

.super-admin-loading {
  padding: 48px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
}

.super-admin-loading-title {
  font-weight: 700;
  font-size: 1.05rem;
  color: var(--text-primary);
}

.super-admin-loading-subtitle {
  margin-top: 4px;
  font-size: 0.9rem;
  color: var(--muted);
}

.super-admin-tabs {
  display: flex;
  gap: 8px;
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
}

.super-admin-tab {
  appearance: none;
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-primary);
  padding: 10px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  transition: all var(--transition-fast);
}

.super-admin-tab:hover {
  background: var(--bg-card-hover);
  border-color: rgba(0, 255, 102, 0.12);
}

.super-admin-tab--active {
  background: rgba(0, 255, 102, 0.12);
  border-color: rgba(0, 255, 102, 0.18);
  box-shadow: 0 0 0 1px rgba(0, 255, 102, 0.08);
}

.super-admin-tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 22px;
  padding: 0 8px;
  border-radius: var(--radius-full);
  background: rgba(0, 255, 102, 0.12);
  color: var(--text-primary);
  font-size: 0.85rem;
}

.super-admin-tab-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.super-admin-error {
  padding: 10px 0;
  color: #ef4444;
}

.super-admin-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

@media (min-width: 1100px) {
  .super-admin-grid {
    grid-template-columns: 1fr 1fr;
    align-items: start;
  }
}

.super-admin-section {
  padding: 14px;
}

.super-admin-section--full {
  grid-column: 1 / -1;
}

.super-admin-section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.super-admin-section-title {
  margin: 0;
  font-size: 1rem;
}

.super-admin-section-subtitle {
  margin-top: 2px;
  color: var(--muted);
  font-size: 0.875rem;
}

.super-admin-pagination {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.super-admin-pagination-range {
  color: var(--muted);
  font-size: 0.875rem;
}

.super-admin-page-size {
  width: 92px;
  padding: 8px 10px;
}

.super-admin-table {
  margin-top: 10px;
}

.super-admin-muted,
.super-admin-muted-block {
  color: var(--muted);
  padding: 14px;
}

.super-admin-muted-block {
  padding: 10px 0;
}

.super-admin-row-clickable {
  cursor: pointer;
}

.super-admin-row-clickable:hover {
  background: var(--bg-card-hover);
}

.super-admin-row-selected {
  background: var(--accent-soft);
}

.super-admin-form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

@media (min-width: 820px) {
  .super-admin-form-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.super-admin-subsection {
  margin-top: 14px;
}

.super-admin-subtitle {
  margin: 0 0 10px 0;
  font-size: 0.95rem;
}

.super-admin-tenant-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: var(--radius-full);
  background: var(--accent-soft);
  border: 1px solid rgba(0, 255, 102, 0.14);
}

.super-admin-tenant-summary {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  padding: 12px;
  border: 1px solid rgba(0, 255, 102, 0.12);
  background: rgba(0, 255, 102, 0.06);
  border-radius: var(--radius-lg);
  margin-bottom: 12px;
}

@media (min-width: 820px) {
  .super-admin-tenant-summary {
    grid-template-columns: 1fr 1fr 1fr;
  }
}

.super-admin-summary-item {
  padding: 10px;
  border-radius: var(--radius-md);
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(0, 255, 102, 0.08);
}

.super-admin-summary-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--muted);
}

.super-admin-summary-value {
  margin-top: 4px;
  font-weight: 600;
  color: var(--text-primary);
  word-break: break-word;
}

.super-admin-actions {
  display: flex;
  gap: 10px;
  margin-top: 14px;
  flex-wrap: wrap;
}

.super-admin-cell-wide {
  min-width: 220px;
}

.super-admin-cell-narrow {
  min-width: 140px;
}

.super-admin-cell-xl {
  min-width: 320px;
}

.super-admin-page .input,
.super-admin-page .btn,
.super-admin-page select.input,
.super-admin-page .btn-sm {
  border-radius: var(--radius-sm);
}

.super-admin-page .input {
  padding: 10px 12px;
}

/* ── Stripe Config Panel ─────────────────────────────── */
.super-admin-tab-badge { display:inline-flex; align-items:center; padding:2px 8px; border-radius:var(--radius-full); font-size:0.75rem; font-weight:700; }
.badge-test { background:rgba(234,179,8,0.15); color:#eab308; }
.badge-live { background:rgba(239,68,68,0.15); color:#ef4444; }
.stripe-mode-box { padding:14px; border-radius:var(--radius-lg); border:1px solid; margin-bottom:12px; }
.stripe-mode-test { background:rgba(234,179,8,0.05); border-color:rgba(234,179,8,0.2); }
.stripe-mode-live { background:rgba(239,68,68,0.05); border-color:rgba(239,68,68,0.3); }
.stripe-mode-label { display:flex; align-items:center; gap:8px; font-size:1rem; }
.stripe-mode-warn { margin-top:8px; color:#f87171; font-size:0.875rem; }
.stripe-mode-actions { display:flex; gap:10px; margin-top:12px; }
.stripe-config-section .input-label { display:flex; align-items:center; justify-content:space-between; gap:6px; }
.stripe-key-set {
  display:inline-flex; align-items:center; gap:3px;
  color:#22c55e; font-size:0.72rem; font-weight:600;
  background:rgba(34,197,94,0.12); border-radius:4px;
  padding:1px 7px; white-space:nowrap; flex-shrink:0;
  border:1px solid rgba(34,197,94,0.25);
}
.stripe-validation { display:flex; flex-wrap:wrap; gap:10px; margin-bottom:14px; }
.stripe-validation-item { padding:6px 12px; border-radius:var(--radius-full); font-size:0.85rem; font-weight:600; }
.stripe-validation-item.valid { background:rgba(34,197,94,0.12); color:#22c55e; }
.stripe-validation-item.invalid { background:rgba(239,68,68,0.1); color:#f87171; }
.btn-danger { background:rgba(239,68,68,0.15); border-color:rgba(239,68,68,0.4); color:#f87171; }
.btn-danger:hover { background:rgba(239,68,68,0.25); }

.stripe-secret-wrap { position:relative; display:flex; align-items:center; }
.stripe-secret-wrap .input { flex:1; padding-right:38px; }
.stripe-eye-btn {
  position:absolute; right:8px;
  background:none; border:none; cursor:pointer;
  color:var(--text-muted, #888); padding:4px;
  display:flex; align-items:center; justify-content:center;
  border-radius:4px; transition:color 0.15s;
}
.stripe-eye-btn:hover { color:var(--text-primary, #fff); }

/* ── Filtros (Assinaturas & Eventos) ──────────────────── */
.sa-filters {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
}

.sa-filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.sa-filter-input {
  flex: 1 1 220px;
  min-width: 180px;
}

.sa-filter-select {
  flex: 0 1 180px;
  min-width: 140px;
}

.sa-filter-date-group {
  display: flex;
  align-items: center;
  gap: 4px;
}

.sa-filter-date-label {
  font-size: 0.82rem;
  color: var(--muted);
  white-space: nowrap;
}

.sa-filter-date {
  width: 150px;
}

/* ── Pills ─────────────────────────────────────────────── */
.sa-pill {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  font-weight: 600;
  white-space: nowrap;
}

.sa-pill--plan {
  background: rgba(99, 102, 241, 0.12);
  color: #818cf8;
}

.sa-status--trial    { background: rgba(234, 179, 8, 0.12); color: #eab308; }
.sa-status--active   { background: rgba(34, 197, 94, 0.12); color: #22c55e; }
.sa-status--past_due { background: rgba(251, 146, 60, 0.15); color: #fb923c; }
.sa-status--unpaid   { background: rgba(239, 68, 68, 0.12); color: #f87171; }
.sa-status--canceled { background: rgba(156, 163, 175, 0.15); color: #9ca3af; }
.sa-status--expired  { background: rgba(156, 163, 175, 0.15); color: #6b7280; }

.sa-source--subscription { background: rgba(99, 102, 241, 0.12); color: #818cf8; }
.sa-source--stripe       { background: rgba(234, 179, 8, 0.12); color: #eab308; }
.sa-source--limit        { background: rgba(239, 68, 68, 0.12); color: #f87171; }

/* ── Células especiais ─────────────────────────────────── */
.sa-cell-tenant {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.sa-cell-name {
  font-weight: 600;
  color: var(--text-primary);
}

.sa-cell-email {
  font-size: 0.78rem;
  color: var(--muted);
}

.sa-cell-mono {
  font-family: 'Fira Code', 'Cascadia Code', monospace;
  font-size: 0.82rem;
}

.sa-cell-desc {
  max-width: 420px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sa-event-row:hover .sa-cell-desc {
  white-space: normal;
  overflow: visible;
}

@media (max-width: 820px) {
  .sa-filter-input,
  .sa-filter-select {
    flex: 1 1 100%;
  }
  .sa-filter-date {
    width: 100%;
  }
}
</style>
