<template>
  <AppLayout>
    <div class="bc-wrapper">

      <!-- ── Page Header ─────────────────────────────────────── -->
      <div class="bc-page-header">
        <div class="bc-page-header-left">
          <div class="bc-page-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.6 1.18h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.91 8.9a16 16 0 0 0 6.09 6.09l.96-.96a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
              <path d="M14.05 2a9 9 0 0 1 8 7.94"/>
              <path d="M14.05 6A5 5 0 0 1 18 10"/>
            </svg>
          </div>
          <div>
            <h1 class="bc-page-title">Mensagens em Massa</h1>
            <p class="bc-page-subtitle">Segmente o público, visualize os contatos e dispare um fluxo com um clique.</p>
          </div>
        </div>
        <div class="bc-reach-pill" :class="{ 'bc-reach-pill--warn': tooLarge, 'bc-reach-pill--zero': !previewState.loading && previewState.total === 0 }">
          <div class="bc-reach-dot">
            <svg v-if="!previewState.loading" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            <svg v-else width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" class="spin-icon">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
          </div>
          <div>
            <div class="bc-reach-label">Alcance estimado</div>
            <div class="bc-reach-value">
              {{ previewState.loading ? 'Calculando...' : `${previewState.total ?? 0} contato(s)` }}
            </div>
          </div>
          <span v-if="tooLarge" class="bc-reach-warn-badge">Acima do limite</span>
        </div>
      </div>

      <!-- ── 3-Column Body ────────────────────────────────────── -->
      <div class="bc-body">

        <!-- ═══════════ COL 1 · FILTROS ═══════════ -->
        <section class="bc-panel bc-panel--filters">
          <header class="bc-panel-header">
            <div class="bc-col-icon bc-col-icon--filters">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
              </svg>
            </div>
            <div>
              <h3 class="bc-panel-title">Filtros / Público</h3>
              <p class="bc-panel-sub">Defina quem receberá o disparo</p>
            </div>
          </header>

          <div class="bc-panel-body">
            <!-- Match mode -->
            <div class="bc-section">
              <div class="bc-section-label-row">
                <span class="bc-label">Combinar condições</span>
                <span class="info-tooltip" tabindex="0" role="button">
                  i
                  <span class="info-tooltip-content">
                    <strong>Todas (E)</strong>: o contato só entra se cumprir <strong>todas</strong> as condições.<br />
                    <strong>Qualquer (OU)</strong>: entra se cumprir <strong>pelo menos uma</strong>.
                  </span>
                </span>
              </div>
              <div class="mode-toggle">
                <button type="button" class="mode-btn" :class="{ active: segment.match_mode === 'all' }" @click="setMatchMode('all')">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                  Todas (E)
                </button>
                <button type="button" class="mode-btn" :class="{ active: segment.match_mode === 'any' }" @click="setMatchMode('any')">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                  Qualquer (OU)
                </button>
              </div>
            </div>

            <!-- Rules list -->
            <div class="bc-section">
              <div class="bc-section-label-row">
                <span class="bc-label">Condições</span>
                <span class="bc-badge-count">{{ segment.rules.length }}</span>
              </div>

              <div v-if="segment.rules.length === 0" class="bc-empty-rules">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
                </svg>
                <span>Nenhuma condição adicionada ainda.</span>
              </div>

              <div v-else class="rules-list">
                <div v-for="rule in segment.rules" :key="rule.id" class="rule-card">
                  <div class="rule-header">
                    <select v-model="rule.kind" class="rule-select" @change="normalizeRule(rule)">
                      <option value="search">Busca (nome/username)</option>
                      <option value="channels">Canal (um ou mais)</option>
                      <option value="tags">Tags</option>
                      <option value="fields">Campos (sistema/custom)</option>
                      <option value="last_inbound_days">Última interação (dias)</option>
                      <option value="created_after">Criado após</option>
                      <option value="created_before">Criado antes</option>
                    </select>
                    <button type="button" class="rule-remove" @click="removeRule(rule.id)" title="Remover">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                      </svg>
                    </button>
                  </div>

                  <div class="rule-body" v-if="rule.kind === 'search'">
                    <input v-model="rule.value" type="text" class="bc-input" placeholder="Ex.: João, @maria..." @input="debouncedPreview" />
                    <p class="rule-hint">Busca por nome, sobrenome ou username.</p>
                  </div>

                  <div class="rule-body" v-else-if="rule.kind === 'channels'">
                    <div class="chip-grid">
                      <button v-for="ch in channels" :key="ch.channel_id || 'none'" type="button" class="chip"
                        :class="{ active: rule.values.includes(ch.channel_id) }"
                        @click="toggleInRuleArray(rule, 'values', ch.channel_id)">
                        {{ ch.channel_name || 'Sem nome' }}<span class="chip-count">{{ ch.count }}</span>
                      </button>
                    </div>
                    <p class="rule-hint">Selecione um ou mais canais.</p>
                  </div>

                  <div class="rule-body" v-else-if="rule.kind === 'tags'">
                    <div class="rule-row">
                      <span class="inline-label">Modo</span>
                      <select v-model="rule.mode" class="bc-select-sm" @change="debouncedPreview">
                        <option value="any">Possui qualquer tag</option>
                        <option value="all">Possui todas as tags</option>
                        <option value="exclude">Não possui as tags</option>
                      </select>
                    </div>
                    <div v-if="tags.length === 0" class="bc-hint-muted">Nenhuma tag cadastrada ainda.</div>
                    <div v-else class="chip-grid">
                      <button v-for="tag in tags" :key="tag.name" type="button" class="chip"
                        :class="{ active: rule.values.includes(tag.name) }"
                        @click="toggleInRuleArray(rule, 'values', tag.name)">
                        {{ tag.name }}<span class="chip-count">{{ tag.count }}</span>
                      </button>
                    </div>
                    <p class="rule-hint">Tags para incluir/excluir do público.</p>
                  </div>

                  <div class="rule-body" v-else-if="rule.kind === 'fields'">
                    <div class="field-grid">
                      <div>
                        <label class="mini-label">Origem</label>
                        <select v-model="rule.source" class="bc-select-sm" @change="debouncedPreview">
                          <option value="system">Campo do sistema</option>
                          <option value="custom">Campo personalizado</option>
                        </select>
                      </div>
                      <div v-if="rule.source === 'system'">
                        <label class="mini-label">Campo</label>
                        <select v-model="rule.field" class="bc-select-sm" @change="debouncedPreview">
                          <option value="first_name">Nome</option>
                          <option value="last_name">Sobrenome</option>
                          <option value="username">Username</option>
                          <option value="id">ID do contato</option>
                          <option value="default_channel_id">ID do canal padrão</option>
                          <option value="created_at">Data de criação</option>
                        </select>
                      </div>
                      <div v-else>
                        <label class="mini-label">Chave</label>
                        <input v-model="rule.field" type="text" class="bc-input-sm" placeholder="ex.: cidade, plano..." @input="debouncedPreview" />
                      </div>
                      <div>
                        <label class="mini-label">Tipo</label>
                        <select v-model="rule.value_type" class="bc-select-sm" @change="debouncedPreview">
                          <option value="string">Texto</option>
                          <option value="number">Número</option>
                          <option value="boolean">Verdadeiro/Falso</option>
                          <option value="date">Data</option>
                        </select>
                      </div>
                      <div>
                        <label class="mini-label">Operador</label>
                        <select v-model="rule.op" class="bc-select-sm" @change="debouncedPreview">
                          <option value="eq">Igual a</option>
                          <option value="neq">Diferente de</option>
                          <option value="contains" v-if="rule.value_type === 'string'">Contém</option>
                          <option value="not_contains" v-if="rule.value_type === 'string'">Não contém</option>
                          <option value="starts_with" v-if="rule.value_type === 'string'">Começa com</option>
                          <option value="ends_with" v-if="rule.value_type === 'string'">Termina com</option>
                          <option value="gt" v-if="rule.value_type !== 'boolean'">Maior que</option>
                          <option value="gte" v-if="rule.value_type !== 'boolean'">Maior ou igual</option>
                          <option value="lt" v-if="rule.value_type !== 'boolean'">Menor que</option>
                          <option value="lte" v-if="rule.value_type !== 'boolean'">Menor ou igual</option>
                          <option value="is_empty">Está vazio</option>
                          <option value="is_not_empty">Não está vazio</option>
                          <option value="exists" v-if="rule.source === 'custom'">Existe</option>
                          <option value="not_exists" v-if="rule.source === 'custom'">Não existe</option>
                        </select>
                      </div>
                    </div>
                    <div class="field-value" v-if="needsValue(rule)">
                      <label class="mini-label">Valor</label>
                      <input v-if="rule.value_type === 'string'" v-model="rule.value" type="text" class="bc-input-sm" placeholder="Digite o valor..." @input="debouncedPreview" />
                      <input v-else-if="rule.value_type === 'number'" v-model="rule.value" type="number" class="bc-input-sm" placeholder="0" @input="debouncedPreview" />
                      <select v-else-if="rule.value_type === 'boolean'" v-model="rule.value" class="bc-select-sm" @change="debouncedPreview">
                        <option value="true">Verdadeiro</option>
                        <option value="false">Falso</option>
                      </select>
                      <input v-else v-model="rule.value" type="date" class="bc-input-sm" @input="debouncedPreview" />
                    </div>
                    <p class="rule-hint">Campos de custom_fields ou campos internos do contato.</p>
                  </div>

                  <div class="rule-body" v-else-if="rule.kind === 'last_inbound_days'">
                    <div class="rule-row">
                      <span class="inline-label">Últimos</span>
                      <input v-model.number="rule.days" type="number" min="0" max="3650" class="bc-input-sm" style="width: 80px;" @input="debouncedPreview" />
                      <span class="inline-label">dias</span>
                    </div>
                    <p class="rule-hint">Contatos que interagiram nos últimos N dias.</p>
                  </div>

                  <div class="rule-body" v-else-if="rule.kind === 'created_after'">
                    <div class="rule-row">
                      <span class="inline-label">A partir de</span>
                      <input v-model="rule.date" type="date" class="bc-input-sm" @input="debouncedPreview" />
                    </div>
                  </div>

                  <div class="rule-body" v-else-if="rule.kind === 'created_before'">
                    <div class="rule-row">
                      <span class="inline-label">Até</span>
                      <input v-model="rule.date" type="date" class="bc-input-sm" @input="debouncedPreview" />
                    </div>
                  </div>
                </div>
              </div>

              <div class="add-rule-row">
                <select v-model="newRuleKind" class="bc-select-sm" style="flex: 1;">
                  <option value="search">Busca</option>
                  <option value="channels">Canal</option>
                  <option value="tags">Tags</option>
                  <option value="fields">Campos</option>
                  <option value="last_inbound_days">Última interação</option>
                  <option value="created_after">Criado após</option>
                  <option value="created_before">Criado antes</option>
                </select>
                <button type="button" class="btn-add-rule" @click="addRule">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                  </svg>
                  Adicionar
                </button>
              </div>
            </div>
          </div>

          <footer class="bc-panel-footer">
            <button type="button" class="bc-footer-btn" :disabled="segment.rules.length === 0" @click="clearSegment">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
              Limpar tudo
            </button>
            <button type="button" class="bc-footer-btn" :disabled="previewState.loading" @click="runPreview">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
              Atualizar
            </button>
          </footer>
        </section>

        <!-- ═══════════ COL 2 · PRÉVIA ═══════════ -->
        <section class="bc-panel bc-panel--preview">
          <header class="bc-panel-header">
            <div class="bc-col-icon bc-col-icon--preview">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </div>
            <div style="flex: 1;">
              <h3 class="bc-panel-title">Audiência</h3>
              <p class="bc-panel-sub">
                <span v-if="previewState.loading">Calculando...</span>
                <span v-else>
                  <strong class="bc-count-accent">{{ previewState.total ?? 0 }}</strong> contato(s) no segmento
                </span>
              </p>
            </div>
            <div v-if="previewState.loading" class="preview-loading-dot">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin-icon">
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
              </svg>
            </div>
          </header>

          <div class="bc-panel-body">
            <!-- Loading skeletons -->
            <div v-if="previewState.loading" class="preview-skeletons">
              <div v-for="i in 8" :key="i" class="preview-skeleton">
                <div class="skeleton-avatar"></div>
                <div class="skeleton-lines">
                  <div class="skeleton-line skeleton-line--name"></div>
                  <div class="skeleton-line skeleton-line--sub"></div>
                </div>
              </div>
            </div>

            <!-- Empty state -->
            <div v-else-if="!previewState.sample || previewState.sample.length === 0" class="preview-empty-state">
              <div class="preview-empty-icon">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <line x1="23" y1="11" x2="17" y2="11"/>
                </svg>
              </div>
              <p class="preview-empty-text">Nenhum contato corresponde às condições.</p>
              <p class="preview-empty-hint">Adicione ou ajuste filtros na coluna ao lado.</p>
            </div>

            <!-- Contact list -->
            <div v-else class="preview-contacts">
              <div v-for="contact in pagedContacts" :key="contact.id" class="preview-contact-row">
                <div class="contact-avatar" :style="{ background: getAvatarColor(contact) }">
                  {{ getAvatarInitials(contact) }}
                </div>
                <div class="contact-info">
                  <span class="contact-name">{{ getContactName(contact) }}</span>
                  <span v-if="contact.username" class="contact-username">@{{ contact.username }}</span>
                </div>
                <div class="contact-id-badge">#{{ contact.id }}</div>
              </div>

              <div v-if="previewState.total > previewState.sample.length" class="preview-more-indicator">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <span>+ {{ (previewState.total - previewState.sample.length).toLocaleString() }} contato(s) não exibidos na amostra</span>
              </div>
            </div>
          </div>

          <!-- Pagination -->
          <footer v-if="previewPageCount > 1" class="bc-panel-footer bc-panel-footer--pagination">
            <button class="pg-btn" :disabled="previewPage === 0" @click="previewPage--">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <span class="pg-info">{{ previewPage + 1 }} / {{ previewPageCount }}</span>
            <button class="pg-btn" :disabled="previewPage >= previewPageCount - 1" @click="previewPage++">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
          </footer>

          <!-- Too large warning -->
          <div v-if="tooLarge" class="bc-panel-alert bc-panel-alert--warn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            Segmento acima do limite de 2.000 contatos. Refine os filtros antes de disparar.
          </div>
        </section>

        <!-- ═══════════ COL 3 · FLUXO ═══════════ -->
        <section class="bc-panel bc-panel--flow">
          <header class="bc-panel-header">
            <div class="bc-col-icon bc-col-icon--flow">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
            </div>
            <div>
              <h3 class="bc-panel-title">Automação</h3>
              <p class="bc-panel-sub">Selecione a automação a disparar</p>
            </div>
          </header>

          <div class="bc-panel-body">
            <!-- Stats box -->
            <div class="flow-meta-box">
              <div class="flow-meta-row">
                <span class="flow-meta-label">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
                  </svg>
                  Alcance
                </span>
                <span class="flow-meta-value" :class="{ 'flow-meta-value--accent': !previewState.loading && (previewState.total ?? 0) > 0 }">
                  {{ previewState.loading ? '...' : `${previewState.total ?? 0} contato(s)` }}
                </span>
              </div>
              <div class="flow-meta-row">
                <span class="flow-meta-label">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
                  </svg>
                  Combinação
                </span>
                <span class="flow-meta-value">{{ segment.match_mode === 'all' ? 'Todas (E)' : 'Qualquer (OU)' }}</span>
              </div>
              <div class="flow-meta-row">
                <span class="flow-meta-label">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/>
                    <line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>
                  </svg>
                  Condições
                </span>
                <span class="flow-meta-value">{{ segment.rules.length }}</span>
              </div>
            </div>

            <div class="bc-section-label-row" style="margin-bottom: 10px;">
              <span class="bc-label">Selecione um fluxo ativo</span>
            </div>

            <div v-if="flows.length === 0" class="bc-empty-rules">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
              <span>Nenhum fluxo disponível. Crie um em Automações.</span>
            </div>

            <div v-else class="flow-cards">
              <button
                v-for="flow in flows"
                :key="flow.id"
                type="button"
                class="flow-card"
                :class="{ 'flow-card--selected': selectedFlowId === flow.id, 'flow-card--inactive': !flow.is_active }"
                :disabled="!flow.is_active"
                @click="selectedFlowId = flow.id"
              >
                <div class="flow-card-left">
                  <div class="flow-card-radio">
                    <div v-if="selectedFlowId === flow.id" class="flow-card-radio-dot"></div>
                  </div>
                  <div class="flow-card-info">
                    <span class="flow-card-name">{{ flow.name }}</span>
                    <span v-if="flow.description" class="flow-card-desc">{{ flow.description }}</span>
                  </div>
                </div>
                <span class="flow-card-status" :class="flow.is_active ? 'status--active' : 'status--inactive'">
                  {{ flow.is_active ? 'Ativo' : 'Inativo' }}
                </span>
              </button>
            </div>

            <div v-if="selectedFlow && !selectedFlow.is_active" class="bc-panel-alert bc-panel-alert--warn" style="margin: 12px 0 0; border-radius: 8px; border: 1px solid rgba(234,179,8,0.25);">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
              Este fluxo está inativo. Ative-o em Automações antes de disparar.
            </div>
          </div>

          <footer class="bc-panel-footer bc-panel-footer--dispatch">
            <!-- Resumo do disparo -->
            <div class="dispatch-summary" v-if="selectedFlow && selectedFlow.is_active">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              <span><strong>{{ selectedFlow.name }}</strong> · {{ previewState.total ?? 0 }} contato(s)</span>
            </div>
            <div class="dispatch-summary dispatch-summary--muted" v-else>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <span>Selecione uma automação ativa para disparar</span>
            </div>

            <!-- Confirmação inline -->
            <div v-if="confirmMode && !sending" class="dispatch-confirm-bar">
              <div class="dispatch-confirm-msg">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                Disparar para <strong>{{ previewState.total }}</strong> contato(s)?
              </div>
              <div class="dispatch-confirm-actions">
                <button type="button" class="btn-cancel-confirm" @click="cancelConfirm">Cancelar</button>
                <button type="button" class="btn-confirm-send" @click="executeSend">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
                  </svg>
                  Confirmar
                </button>
              </div>
            </div>

            <!-- Botão principal -->
            <button
              v-else
              type="button"
              class="btn-dispatch"
              :class="{ 'btn-dispatch--sending': sending }"
              :disabled="sendDisabled"
              @click="confirmAndSend"
            >
              <!-- Enviando: shimmer + spinner -->
              <template v-if="sending">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin-icon">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                </svg>
                Enviando…
              </template>
              <!-- Normal: ícone de envio -->
              <template v-else>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
                Disparar em Massa
              </template>
            </button>
          </footer>
        </section>

      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { getContactsStats, previewBulkMessage, sendBulkMessage } from '@/api/contacts'
import { listFlows } from '@/api/flows'
import { useToast } from '@/composables/useToast'
import { useBroadcastProgress } from '@/composables/useBroadcastProgress'

const toast = useToast()
const broadcastProgress = useBroadcastProgress()

let ruleSeq = 1
const segment = reactive({ match_mode: 'all', rules: [] })
const newRuleKind = ref('tags')
const previewState = reactive({ loading: false, total: null, sample: [] })
const sending = ref(false)
const confirmMode = ref(false)
const channels = ref([])
const tags = ref([])
const flows = ref([])
const selectedFlowId = ref(null)

// ── Pagination ──────────────────────────────────────────────
const previewPage = ref(0)
const previewPerPage = 10
watch(() => previewState.sample, () => { previewPage.value = 0 })
const previewPageCount = computed(() => {
  if (!previewState.sample?.length) return 0
  return Math.ceil(previewState.sample.length / previewPerPage)
})
const pagedContacts = computed(() => {
  if (!previewState.sample?.length) return []
  const start = previewPage.value * previewPerPage
  return previewState.sample.slice(start, start + previewPerPage)
})

// ── Avatar helpers ──────────────────────────────────────────
const AVATAR_COLORS = ['#00cc52', '#0ea5e9', '#8b5cf6', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899', '#6366f1']
const getAvatarColor = (c) => {
  let h = 0
  const str = String(c.id || c.first_name || '')
  for (let i = 0; i < str.length; i++) h = (str.charCodeAt(i) + ((h << 5) - h))
  return AVATAR_COLORS[Math.abs(h) % AVATAR_COLORS.length]
}
const getAvatarInitials = (c) => {
  const f = c.first_name?.[0] || ''
  const l = c.last_name?.[0] || ''
  return (f + l).toUpperCase() || (c.username?.[0] || '#').toUpperCase()
}
const getContactName = (c) => {
  const parts = [c.first_name, c.last_name].filter(Boolean)
  return parts.length ? parts.join(' ') : c.username || `ID ${c.id}`
}

// ── Computed ─────────────────────────────────────────────────
const tooLarge = computed(() => (previewState.total || 0) > 2000)
const selectedFlow = computed(() => flows.value.find((f) => f.id === selectedFlowId.value) || null)
const sendDisabled = computed(() =>
  sending.value ||
  !selectedFlowId.value ||
  !selectedFlow.value ||
  !selectedFlow.value?.is_active ||
  (previewState.total || 0) === 0 ||
  tooLarge.value
)

// ── Data loading ──────────────────────────────────────────────
const loadStats = async () => {
  try {
    const stats = await getContactsStats()
    channels.value = stats.by_channel || []
    tags.value = stats.by_tag || []
    await runPreview()
  } catch (err) {
    console.error(err)
    toast.error('Não foi possível carregar estatísticas de contatos.')
  }
}

const createRule = (kind) => {
  const id = ruleSeq++
  if (kind === 'search') return { id, kind: 'search', value: '' }
  if (kind === 'channels') return { id, kind: 'channels', values: [] }
  if (kind === 'tags') return { id, kind: 'tags', mode: 'any', values: [] }
  if (kind === 'fields') return { id, kind: 'fields', source: 'custom', field: '', value_type: 'string', op: 'eq', value: '' }
  if (kind === 'last_inbound_days') return { id, kind: 'last_inbound_days', days: 30 }
  if (kind === 'created_after') return { id, kind: 'created_after', date: '' }
  if (kind === 'created_before') return { id, kind: 'created_before', date: '' }
  return { id, kind: 'tags', mode: 'any', values: [] }
}

const needsValue = (rule) => {
  if (rule.kind !== 'fields') return true
  return !['is_empty', 'is_not_empty', 'exists', 'not_exists'].includes(rule.op)
}

const normalizeRule = (rule) => {
  const normalized = createRule(rule.kind)
  Object.keys(rule).forEach((k) => delete rule[k])
  Object.assign(rule, normalized)
  debouncedPreview()
}

const hasRuleKind = (kind) => segment.rules.some((r) => r.kind === kind)

const addRule = () => {
  const kind = newRuleKind.value
  if (hasRuleKind(kind)) { toast.info('Essa condição já existe. Ajuste a existente.'); return }
  segment.rules.push(createRule(kind))
  debouncedPreview()
}

const removeRule = (id) => {
  const idx = segment.rules.findIndex((r) => r.id === id)
  if (idx !== -1) segment.rules.splice(idx, 1)
  debouncedPreview()
}

const clearSegment = () => { segment.rules = []; debouncedPreview() }
const setMatchMode = (mode) => { segment.match_mode = mode; debouncedPreview() }

const toggleInRuleArray = (rule, key, value) => {
  const arr = rule[key] || []
  const idx = arr.indexOf(value)
  if (idx === -1) arr.push(value)
  else arr.splice(idx, 1)
  rule[key] = arr
  debouncedPreview()
}

const buildPayload = () => {
  const payload = { match_mode: segment.match_mode }
  const field_conditions = []
  for (const rule of segment.rules) {
    if (rule.kind === 'search' && rule.value?.trim()) payload.search = rule.value.trim()
    if (rule.kind === 'channels' && Array.isArray(rule.values) && rule.values.length) payload.channel_ids = rule.values
    if (rule.kind === 'tags' && Array.isArray(rule.values) && rule.values.length) {
      if (rule.mode === 'all') payload.tags_all = rule.values
      else if (rule.mode === 'exclude') payload.tags_exclude = rule.values
      else payload.tags_any = rule.values
    }
    if (rule.kind === 'last_inbound_days' && Number.isFinite(rule.days)) payload.last_inbound_days = rule.days
    if (rule.kind === 'fields') {
      if (!rule.field || !String(rule.field).trim()) continue
      const fc = {
        source: rule.source || 'custom',
        field: String(rule.field).trim(),
        op: rule.op || 'eq',
        value_type: rule.value_type || 'string'
      }
      if (needsValue(rule)) fc.value = String(rule.value ?? '')
      field_conditions.push(fc)
    }
    if ((rule.kind === 'created_after' || rule.kind === 'created_before') && rule.date) payload[rule.kind] = rule.date
  }
  if (field_conditions.length) payload.field_conditions = field_conditions
  if (selectedFlowId.value) payload.flow_id = selectedFlowId.value
  return payload
}

const runPreview = async () => {
  previewState.loading = true
  try {
    const res = await previewBulkMessage(buildPayload())
    previewState.total = res.total ?? 0
    previewState.sample = res.sample || []
  } catch (err) {
    console.error(err)
    toast.error('Erro ao calcular o alcance do disparo.')
  } finally {
    previewState.loading = false
  }
}

let previewTimeout = null
const debouncedPreview = () => {
  if (previewTimeout) clearTimeout(previewTimeout)
  previewTimeout = setTimeout(runPreview, 500)
}

const confirmAndSend = () => {
  if (!selectedFlow.value) { toast.warning('Selecione uma automação para disparar.'); return }
  if (!previewState.total || previewState.total === 0) { toast.warning('Nenhum contato no segmento atual.'); return }
  if (tooLarge.value) { toast.warning('Segmento acima do limite (2.000). Refine o público.'); return }
  confirmMode.value = true
}

const cancelConfirm = () => {
  confirmMode.value = false
}

const executeSend = async () => {
  confirmMode.value = false
  sending.value = true
  try {
    const payload = { ...buildPayload(), background: true }
    const res = await sendBulkMessage(payload)

    if (res.job_id) {
      // Modo background: tracking via polling na sidebar
      broadcastProgress.startTracking(res.job_id, res.total)
      toast.success(`Disparo iniciado para ${res.total} contatos! Acompanhe na sidebar.`)
    } else {
      // Fallback síncrono (ARQ offline)
      toast.success(`Disparo concluído! Iniciados: ${res.started}/${res.total}. Falhas: ${res.failed}.`)
    }
  } catch (err) {
    console.error(err)
    const detail = err?.response?.data?.detail || 'Erro ao enviar mensagens em massa.'
    toast.error(detail)
  } finally {
    sending.value = false
  }
}

onMounted(async () => {
  await loadStats()
  try {
    const allFlows = await listFlows()
    flows.value = Array.isArray(allFlows) ? allFlows : []
    const firstActive = flows.value.find((f) => f.is_active)
    if (firstActive) selectedFlowId.value = firstActive.id
  } catch (err) {
    console.error(err)
    toast.error('Não foi possível carregar a lista de fluxos.')
  }
})
</script>

<style scoped>
/* ─── Root Layout ─────────────────────────────────────────── */
.bc-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 12px;
  overflow: hidden;
}

.bc-body {
  display: grid;
  grid-template-columns: minmax(280px, 320px) minmax(0, 1fr) minmax(268px, 308px);
  gap: 12px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

/* ─── Page Header ─────────────────────────────────────────── */
.bc-page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 20px;
  background: #060606;
  border: 1px solid rgba(0, 255, 102, 0.08);
  border-radius: 12px;
  flex-shrink: 0;
}

.bc-page-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.bc-page-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(0, 255, 102, 0.08);
  border: 1px solid rgba(0, 255, 102, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00FF66;
  flex-shrink: 0;
}

.bc-page-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #EDEDED;
  letter-spacing: -0.3px;
}

.bc-page-subtitle {
  margin: 2px 0 0;
  font-size: 0.8rem;
  color: #A7ADB3;
}

.bc-reach-pill {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: rgba(0, 255, 102, 0.04);
  border: 1px solid rgba(0, 255, 102, 0.15);
  border-radius: 10px;
  flex-shrink: 0;
}

.bc-reach-pill--warn {
  background: rgba(234, 179, 8, 0.05);
  border-color: rgba(234, 179, 8, 0.22);
}

.bc-reach-pill--zero {
  background: rgba(255, 255, 255, 0.02);
  border-color: rgba(255, 255, 255, 0.08);
}
.bc-reach-pill--zero .bc-reach-dot {
  background: rgba(255, 255, 255, 0.06);
  color: #A7ADB3;
}
.bc-reach-pill--zero .bc-reach-value { color: #A7ADB3; }

.bc-reach-dot {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(0, 255, 102, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00FF66;
  flex-shrink: 0;
}

.bc-reach-label {
  font-size: 0.67rem;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #A7ADB3;
  line-height: 1;
}

.bc-reach-value {
  font-size: 0.88rem;
  font-weight: 700;
  color: #EDEDED;
  margin-top: 2px;
}

.bc-reach-warn-badge {
  font-size: 0.68rem;
  font-weight: 700;
  background: rgba(234, 179, 8, 0.12);
  border: 1px solid rgba(234, 179, 8, 0.28);
  color: #ca8a04;
  padding: 2px 8px;
  border-radius: 5px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* ─── Panel Base ──────────────────────────────────────────── */
.bc-panel {
  display: flex;
  flex-direction: column;
  background: #060606;
  border: 1px solid rgba(0, 255, 102, 0.08);
  border-radius: 12px;
  overflow: hidden;
  min-height: 0;
}

.bc-panel-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px 17px;
  background: #0a0a0a;
  border-bottom: 1px solid rgba(0, 255, 102, 0.06);
  flex-shrink: 0;
}

.bc-col-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.bc-col-icon--filters { background: rgba(0, 255, 102, 0.07); border: 1px solid rgba(0, 255, 102, 0.18); color: #00FF66; }
.bc-col-icon--preview { background: rgba(14, 165, 233, 0.07); border: 1px solid rgba(14, 165, 233, 0.2); color: #0ea5e9; }
.bc-col-icon--flow    { background: rgba(139, 92, 246, 0.07); border: 1px solid rgba(139, 92, 246, 0.2); color: #8b5cf6; }

.bc-panel-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: #EDEDED;
  margin: 0;
  letter-spacing: -0.2px;
}

.bc-panel-sub {
  font-size: 0.73rem;
  color: #A7ADB3;
  margin: 2px 0 0;
}

.bc-panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.bc-panel-footer {
  padding: 11px 16px;
  border-top: 1px solid rgba(0, 255, 102, 0.06);
  background: #0a0a0a;
  flex-shrink: 0;
  display: flex;
  gap: 8px;
}

.bc-panel-footer--dispatch { flex-direction: column; gap: 10px; }
.bc-panel-footer--pagination { align-items: center; justify-content: center; gap: 16px; }

.bc-footer-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: transparent;
  color: #A7ADB3;
  font-size: 0.78rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.bc-footer-btn:hover:not(:disabled) { background: rgba(255, 255, 255, 0.04); color: #EDEDED; border-color: rgba(255, 255, 255, 0.14); }
.bc-footer-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.bc-panel-alert {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 16px;
  font-size: 0.77rem;
  line-height: 1.4;
  flex-shrink: 0;
}

.bc-panel-alert--warn { background: rgba(234, 179, 8, 0.06); border-top: 1px solid rgba(234, 179, 8, 0.18); color: #ca8a04; }
.bc-panel-alert--warn svg { color: #ca8a04; flex-shrink: 0; margin-top: 1px; }

/* ─── Section Labels ──────────────────────────────────────── */
.bc-section { display: flex; flex-direction: column; gap: 9px; }

.bc-section-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.bc-label {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #A7ADB3;
}

.bc-badge-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 18px;
  padding: 0 6px;
  border-radius: 99px;
  background: rgba(0, 255, 102, 0.09);
  border: 1px solid rgba(0, 255, 102, 0.18);
  color: #00FF66;
  font-size: 0.68rem;
  font-weight: 700;
}

/* ─── Match Mode Toggle ───────────────────────────────────── */
.mode-toggle { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }

.mode-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: #0d0d0d;
  color: #A7ADB3;
  font-size: 0.78rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.mode-btn:hover { background: #141414; color: #EDEDED; }
.mode-btn.active { background: rgba(0, 255, 102, 0.07); border-color: rgba(0, 255, 102, 0.28); color: #00FF66; }

/* ─── Rules ───────────────────────────────────────────────── */
.bc-empty-rules {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 7px;
  padding: 20px 12px;
  border: 1px dashed rgba(255, 255, 255, 0.07);
  border-radius: 9px;
  color: #A7ADB3;
  font-size: 0.78rem;
  text-align: center;
}

.bc-empty-rules svg { opacity: 0.35; }
.rules-list { display: flex; flex-direction: column; gap: 7px; }

.rule-card {
  background: #0c0c0c;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 9px;
  padding: 11px;
}

.rule-header { display: flex; align-items: center; gap: 7px; }

.rule-select {
  flex: 1;
  padding: 7px 10px;
  border-radius: 7px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  background: #0d0d0d;
  color: #EDEDED;
  font-size: 0.78rem;
  outline: none;
  color-scheme: dark;
}

.rule-select:focus { border-color: rgba(0, 255, 102, 0.3); }

.rule-remove {
  width: 27px;
  height: 27px;
  border-radius: 7px;
  border: 1px solid rgba(255, 255, 255, 0.07);
  background: transparent;
  color: #A7ADB3;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.15s;
}

.rule-remove:hover { background: rgba(239, 68, 68, 0.09); border-color: rgba(239, 68, 68, 0.28); color: #ef4444; }
.rule-body { margin-top: 9px; }
.rule-hint { margin-top: 7px; font-size: 0.72rem; color: #A7ADB3; line-height: 1.4; }

/* ─── Chips ───────────────────────────────────────────────── */
.chip-grid { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 6px; }

.chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 9px;
  border-radius: 7px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: #0d0d0d;
  color: #EDEDED;
  font-size: 0.76rem;
  cursor: pointer;
  transition: all 0.15s;
}

.chip:hover { background: #141414; }
.chip.active { background: rgba(0, 255, 102, 0.07); border-color: rgba(0, 255, 102, 0.28); color: #00FF66; }
.chip-count { font-size: 0.68rem; color: #A7ADB3; background: rgba(255, 255, 255, 0.05); padding: 1px 5px; border-radius: 4px; }
.chip.active .chip-count { background: rgba(0, 255, 102, 0.1); color: rgba(0, 255, 102, 0.7); }

/* ─── Form Inputs ─────────────────────────────────────────── */
.bc-input, .bc-input-sm {
  width: 100%;
  border-radius: 7px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  background: #0d0d0d;
  color: #EDEDED;
  outline: none;
  transition: border-color 0.15s;
  color-scheme: dark;
  box-sizing: border-box;
}

.bc-input { padding: 9px 12px; font-size: 0.84rem; }
.bc-input-sm { padding: 7px 9px; font-size: 0.78rem; }
.bc-input:focus, .bc-input-sm:focus { border-color: rgba(0, 255, 102, 0.32); }

.bc-select-sm {
  padding: 7px 9px;
  border-radius: 7px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  background: #0d0d0d;
  color: #EDEDED;
  font-size: 0.78rem;
  outline: none;
  color-scheme: dark;
  width: 100%;
}

.bc-select-sm:focus { border-color: rgba(0, 255, 102, 0.32); }
.bc-hint-muted { font-size: 0.76rem; color: #A7ADB3; }

.rule-row { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; }
.inline-label { font-size: 0.73rem; color: #A7ADB3; white-space: nowrap; }
.field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; }
.mini-label { display: block; font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.06em; color: #A7ADB3; margin-bottom: 4px; }
.field-value { margin-top: 7px; }

/* ─── Add Rule ────────────────────────────────────────────── */
.add-rule-row { display: flex; gap: 7px; align-items: center; }

.btn-add-rule {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 11px;
  border-radius: 8px;
  border: 1px solid rgba(0, 255, 102, 0.22);
  background: rgba(0, 255, 102, 0.05);
  color: #00FF66;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
}

.btn-add-rule:hover { background: rgba(0, 255, 102, 0.1); border-color: rgba(0, 255, 102, 0.36); }

/* ─── Preview Skeletons ───────────────────────────────────── */
.preview-loading-dot { color: #0ea5e9; opacity: 0.8; }

.preview-skeletons { display: flex; flex-direction: column; gap: 9px; }
.preview-skeleton { display: flex; align-items: center; gap: 10px; }

.skeleton-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(90deg, #1a1a1a 25%, #232323 50%, #1a1a1a 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  flex-shrink: 0;
}

.skeleton-lines { flex: 1; display: flex; flex-direction: column; gap: 6px; }

.skeleton-line {
  height: 9px;
  border-radius: 5px;
  background: linear-gradient(90deg, #1a1a1a 25%, #232323 50%, #1a1a1a 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}

.skeleton-line--name { width: 60%; }
.skeleton-line--sub  { width: 35%; opacity: 0.6; }

@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ─── Preview Empty ───────────────────────────────────────── */
.preview-empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 28px 16px;
  text-align: center;
  gap: 9px;
}

.preview-empty-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(14, 165, 233, 0.05);
  border: 1px solid rgba(14, 165, 233, 0.14);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0ea5e9;
  opacity: 0.55;
}

.preview-empty-text { font-size: 0.85rem; font-weight: 600; color: #EDEDED; margin: 0; }
.preview-empty-hint { font-size: 0.77rem; color: #A7ADB3; margin: 0; }

/* ─── Contact List ────────────────────────────────────────── */
.preview-contacts { display: flex; flex-direction: column; gap: 3px; }

.preview-contact-row {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 7px 9px;
  border-radius: 8px;
  border: 1px solid transparent;
  transition: all 0.12s;
}

.preview-contact-row:hover { background: rgba(255, 255, 255, 0.025); border-color: rgba(255, 255, 255, 0.05); }

.contact-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  font-weight: 700;
  color: #000;
  flex-shrink: 0;
}

.contact-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 1px; }
.contact-name { font-size: 0.83rem; font-weight: 600; color: #EDEDED; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.contact-username { font-size: 0.71rem; color: #A7ADB3; }
.contact-id-badge {
  font-size: 0.66rem;
  color: #A7ADB3;
  background: rgba(255, 255, 255, 0.04);
  padding: 2px 6px;
  border-radius: 4px;
  flex-shrink: 0;
  font-family: monospace;
}

.preview-more-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 9px;
  font-size: 0.75rem;
  color: #A7ADB3;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  margin-top: 3px;
}

.preview-more-indicator svg { color: rgba(0, 255, 102, 0.45); }

/* ─── Pagination ──────────────────────────────────────────── */
.pg-btn {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: #0d0d0d;
  color: #A7ADB3;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.pg-btn:hover:not(:disabled) { background: rgba(0, 255, 102, 0.07); border-color: rgba(0, 255, 102, 0.22); color: #00FF66; }
.pg-btn:disabled { opacity: 0.28; cursor: not-allowed; }
.pg-info { font-size: 0.78rem; color: #A7ADB3; font-weight: 500; min-width: 48px; text-align: center; }

/* ─── Flow Meta Box ───────────────────────────────────────── */
.flow-meta-box {
  background: #0c0c0c;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 9px;
  overflow: hidden;
}

.flow-meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 13px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  gap: 8px;
}

.flow-meta-row:last-child { border-bottom: none; }
.flow-meta-label { display: flex; align-items: center; gap: 6px; font-size: 0.76rem; color: #A7ADB3; }
.flow-meta-label svg { flex-shrink: 0; }
.flow-meta-value { font-size: 0.8rem; font-weight: 600; color: #EDEDED; }
.flow-meta-value--accent { color: #00FF66; }

/* ─── Flow Cards ──────────────────────────────────────────── */
.flow-cards { display: flex; flex-direction: column; gap: 5px; }

.flow-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 9px;
  padding: 10px 13px;
  border-radius: 9px;
  border: 1.5px solid rgba(255, 255, 255, 0.06);
  background: #0c0c0c;
  cursor: pointer;
  text-align: left;
  width: 100%;
  transition: all 0.15s;
}

.flow-card:hover:not(.flow-card--inactive):not(.flow-card--selected) {
  border-color: rgba(139, 92, 246, 0.28);
  background: rgba(139, 92, 246, 0.04);
}

.flow-card--selected {
  border-color: #8b5cf6;
  background: rgba(139, 92, 246, 0.07);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.07);
}

.flow-card--inactive { opacity: 0.4; cursor: not-allowed; }
.flow-card-left { display: flex; align-items: center; gap: 9px; min-width: 0; }

.flow-card-radio {
  width: 15px;
  height: 15px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: border-color 0.15s;
}

.flow-card--selected .flow-card-radio { border-color: #8b5cf6; }
.flow-card-radio-dot { width: 7px; height: 7px; border-radius: 50%; background: #8b5cf6; }
.flow-card-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.flow-card-name { font-size: 0.83rem; font-weight: 600; color: #EDEDED; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.flow-card-desc { font-size: 0.71rem; color: #A7ADB3; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.flow-card-status {
  font-size: 0.66rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 2px 7px;
  border-radius: 4px;
  flex-shrink: 0;
}

.status--active { background: rgba(0, 255, 102, 0.09); border: 1px solid rgba(0, 255, 102, 0.18); color: #00FF66; }
.status--inactive { background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.07); color: #A7ADB3; }

/* ─── Dispatch Footer ─────────────────────────────────────── */
.dispatch-summary {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 0.78rem;
  color: #00FF66;
}

.dispatch-summary strong { color: #00FF66; }
.dispatch-summary--muted { color: #A7ADB3; }
.dispatch-summary--muted svg { color: #A7ADB3; }

.btn-dispatch {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 13px 20px;
  border-radius: 10px;
  border: none;
  background: #00FF66;
  color: #000;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  letter-spacing: 0.01em;
  transition: all 0.2s;
}

.btn-dispatch:hover:not(:disabled) { background: #00cc52; transform: translateY(-1px); box-shadow: 0 6px 20px rgba(0, 255, 102, 0.25); }
.btn-dispatch:active:not(:disabled) { transform: translateY(0); }
.btn-dispatch:disabled { background: rgba(255, 255, 255, 0.07); color: #A7ADB3; cursor: not-allowed; transform: none; box-shadow: none; }

/* Estado "Enviando" — pulse glow + shimmer */
.btn-dispatch--sending {
  background: #009940 !important;
  cursor: wait !important;
  transform: none !important;
  overflow: hidden;
  animation: dispatch-pulse 1.6s ease-in-out infinite;
}
.btn-dispatch--sending::after {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 60%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.18), transparent);
  animation: dispatch-shimmer 1.6s ease-in-out infinite;
  pointer-events: none;
}
@keyframes dispatch-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0, 255, 102, 0.4); }
  50%       { box-shadow: 0 0 0 7px rgba(0, 255, 102, 0); }
}
@keyframes dispatch-shimmer {
  0%   { left: -100%; }
  100% { left: 200%; }
}

/* ─── Confirmação inline ──────────────────────────────────── */
.dispatch-confirm-bar {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px 14px;
  background: rgba(245, 158, 11, 0.06);
  border: 1px solid rgba(245, 158, 11, 0.22);
  border-radius: 10px;
  animation: confirm-slide-in 0.18s ease;
}
@keyframes confirm-slide-in {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}
.dispatch-confirm-msg {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 0.8rem;
  color: #d97706;
  line-height: 1.4;
}
.dispatch-confirm-msg strong { color: #f59e0b; }
.dispatch-confirm-actions {
  display: flex;
  gap: 8px;
}
.btn-cancel-confirm {
  flex: 1;
  padding: 8px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.1);
  background: transparent;
  color: #A7ADB3;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-cancel-confirm:hover { background: rgba(255,255,255,0.05); color: #EDEDED; }
.btn-confirm-send {
  flex: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 8px;
  border: none;
  background: #f59e0b;
  color: #000;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-confirm-send:hover { background: #d97706; }

/* Destaque do contador de contatos no header da coluna */
.bc-count-accent { color: #00FF66; }

/* ─── Spin Animation ──────────────────────────────────────── */
.spin-icon { animation: spin 0.8s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

/* ─── Info Tooltip ────────────────────────────────────────── */
.info-tooltip {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 17px;
  height: 17px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.11);
  background: rgba(255, 255, 255, 0.04);
  color: #A7ADB3;
  font-size: 0.7rem;
  font-weight: 700;
  cursor: help;
  user-select: none;
}

.info-tooltip-content {
  position: absolute;
  top: 22px;
  right: 0;
  width: 250px;
  background: #111;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 10px 12px;
  color: #EDEDED;
  font-size: 0.78rem;
  line-height: 1.4;
  z-index: 20;
  opacity: 0;
  transform: translateY(-4px);
  pointer-events: none;
  transition: opacity 0.14s, transform 0.14s;
}

.info-tooltip:hover .info-tooltip-content,
.info-tooltip:focus .info-tooltip-content {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

/* ─── Responsive ──────────────────────────────────────────── */
@media (max-width: 1140px) {
  .bc-body {
    grid-template-columns: minmax(250px, 290px) 1fr;
    grid-template-rows: auto auto;
    overflow-y: auto;
  }
  .bc-panel--flow { grid-column: 1 / -1; }
}

@media (max-width: 680px) {
  .bc-body { grid-template-columns: 1fr; overflow-y: auto; }
  .bc-page-header { flex-direction: column; align-items: flex-start; }
  .bc-reach-pill { width: 100%; }
  .field-grid { grid-template-columns: 1fr; }
}
</style>
