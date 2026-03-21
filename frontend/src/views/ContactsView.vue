<template>
  <AppLayout>
    <div class="ct-page">

      <div v-if="pageLoading" class="ct-page-loading loading" aria-busy="true">
        <div class="loading-spinner" aria-hidden="true"></div>
        <div>
          <div class="ct-page-loading-title">Carregando contatos…</div>
          <div class="ct-page-loading-subtitle">Canais, estatísticas e lista</div>
        </div>
      </div>

      <template v-else>

      <!-- Page Header -->
      <div class="ct-header">
        <div class="ct-header-left">
          <div class="ct-header-icon">
            <i class="fa-solid fa-users"></i>
          </div>
          <div>
            <h1 class="ct-title">Contatos</h1>
            <p class="ct-subtitle">Base de contatos da sua conta</p>
          </div>
        </div>
        <div class="ct-header-right">
          <div class="ct-search-box">
            <i class="fa-solid fa-magnifying-glass ct-search-icon"></i>
            <input
              v-model="searchQuery"
              class="ct-search-input"
              placeholder="Buscar por nome, username..."
            />
            <button v-if="searchQuery" class="ct-search-clear" type="button" @click="searchQuery = ''">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
          <div class="ct-stat-pill">
            <i class="fa-solid fa-users" style="font-size:12px;"></i>
            {{ totalContacts.toLocaleString('pt-BR') }} contatos
          </div>
          <button class="ct-btn-secondary" type="button" @click="exportContacts(false)">
            <i class="fa-solid fa-file-arrow-down"></i>
            Exportar
          </button>
        </div>
      </div>

      <!-- 3-Column Body -->
      <div class="ct-body" :class="{ 'has-detail': !!selectedContact }">

        <!-- ════════════════════════════════ -->
        <!-- COL 1 — FILTERS                  -->
        <!-- ════════════════════════════════ -->
        <aside class="ct-col-filters">

          <!-- Active filter chips -->
          <div v-if="hasActiveFilters" class="ct-active-chips">
            <span v-if="selectedChannelId !== null" class="ct-chip">
              <i class="fa-solid fa-tower-broadcast"></i> Canal ativo
              <button type="button" @click="selectChannel(null)"><i class="fa-solid fa-xmark"></i></button>
            </span>
            <span v-for="tag in selectedTags" :key="tag" class="ct-chip">
              <i class="fa-solid fa-hashtag" style="font-size:9px;"></i> {{ tag }}
              <button type="button" @click="toggleTag(tag)"><i class="fa-solid fa-xmark"></i></button>
            </span>
            <span v-for="(ff, idx) in selectedFieldFilters" :key="ff.key" class="ct-chip ct-chip--field">
              {{ ff.field }}: {{ ff.value }}
              <button type="button" @click="removeFieldFilter(idx)"><i class="fa-solid fa-xmark"></i></button>
            </span>
            <button class="ct-chip-clear" type="button" @click="clearFilters">
              <i class="fa-solid fa-filter-circle-xmark"></i> Limpar
            </button>
          </div>

          <!-- ── Canais ── -->
          <div class="ct-filter-group">
            <button class="ct-fgroup-header" type="button" @click="channelsCollapsed = !channelsCollapsed">
              <span class="ct-fgroup-title ct-fgroup-title--canais">
                <i class="fa-solid fa-tower-broadcast"></i>
                Canais
              </span>
              <i :class="channelsCollapsed ? 'fa-solid fa-chevron-down' : 'fa-solid fa-chevron-up'" class="ct-fgroup-arrow"></i>
            </button>
            <div v-show="!channelsCollapsed" class="ct-filter-list">
              <button type="button" class="ct-fi" :class="{ active: selectedChannelId === null }" @click="selectChannel(null)">
                <span class="ct-fi-name"><i class="fa-solid fa-globe"></i> Todos</span>
                <span class="ct-fi-count">{{ contactStats.contacts_total || totalContacts }}</span>
              </button>
              <button
                v-for="ch in availableChannels"
                :key="ch.id"
                type="button"
                class="ct-fi"
                :class="{ active: selectedChannelId === ch.id }"
                @click="selectChannel(ch.id)"
              >
                <span class="ct-fi-name">
                  <i :class="getChannelIcon(ch.channel_type || ch.type)"></i>
                  {{ ch.name || ch.identifier || ch.id }}
                </span>
                <span class="ct-fi-count">{{ getChannelContactCount(ch.id) }}</span>
              </button>
            </div>
          </div>

          <!-- ── Tags ── -->
          <div class="ct-filter-group">
            <button class="ct-fgroup-header" type="button" @click="tagsCollapsed = !tagsCollapsed">
              <span class="ct-fgroup-title ct-fgroup-title--tags">
                <i class="fa-solid fa-tag"></i>
                Tags
                <span v-if="selectedTags.length > 0" class="ct-fgroup-badge">{{ selectedTags.length }}</span>
              </span>
              <i :class="tagsCollapsed ? 'fa-solid fa-chevron-down' : 'fa-solid fa-chevron-up'" class="ct-fgroup-arrow"></i>
            </button>
            <div v-show="!tagsCollapsed" class="ct-filter-list">
              <div v-if="availableTags.length === 0" class="ct-filter-empty">Nenhuma tag ainda.</div>
              <button
                v-for="tag in availableTags"
                :key="tag.name"
                type="button"
                class="ct-fi"
                :class="{ active: selectedTags.includes(tag.name) }"
                @click="toggleTag(tag.name)"
              >
                <span class="ct-fi-name"><i class="fa-solid fa-hashtag" style="font-size:10px;opacity:0.5;"></i> {{ tag.name }}</span>
                <span class="ct-fi-count">{{ tag.count }}</span>
              </button>
            </div>
          </div>

          <!-- ── Campos ── -->
          <div class="ct-filter-group">
            <button class="ct-fgroup-header" type="button" @click="fieldsCollapsed = !fieldsCollapsed">
              <span class="ct-fgroup-title ct-fgroup-title--campos">
                <i class="fa-solid fa-sliders"></i>
                Campos
                <span v-if="selectedFieldFilters.length > 0" class="ct-fgroup-badge">{{ selectedFieldFilters.length }}</span>
              </span>
              <i :class="fieldsCollapsed ? 'fa-solid fa-chevron-down' : 'fa-solid fa-chevron-up'" class="ct-fgroup-arrow"></i>
            </button>
            <div v-show="!fieldsCollapsed" class="ct-fields-body">
              <div class="ct-field-builder">
                <select v-model="fieldDraft" class="ct-select" aria-label="Campo">
                  <option value="">Campo</option>
                  <option v-for="f in availableFieldKeys" :key="f" :value="f">{{ f }}</option>
                </select>
                <input
                  v-model="valueDraft"
                  class="ct-input"
                  type="text"
                  placeholder="Valor"
                  @keyup.enter="addFieldFilter"
                />
                <button type="button" class="ct-field-add-btn" @click="addFieldFilter" title="Adicionar filtro">
                  <i class="fa-solid fa-plus"></i>
                </button>
              </div>
              <div v-if="selectedFieldFilters.length > 0" class="ct-field-chips">
                <div v-for="(it, idx) in selectedFieldFilters" :key="it.key" class="ct-field-chip">
                  <span>{{ it.field }}: {{ it.value }}</span>
                  <button type="button" @click="removeFieldFilter(idx)"><i class="fa-solid fa-xmark"></i></button>
                </div>
              </div>
              <div v-else-if="availableFieldKeys.length === 0" class="ct-filter-empty">Sem campos disponíveis.</div>
            </div>
          </div>

          <!-- ── Segmentos ── -->
          <div class="ct-filter-group ct-segments-group">
            <div class="ct-fgroup-header ct-fgroup-header--static">
              <span class="ct-fgroup-title">
                <i class="fa-solid fa-bookmark"></i>
                Segmentos
              </span>
            </div>
            <div class="ct-segments-body">
              <!-- Saved segments -->
              <div v-if="savedSegments.length === 0 && !hasActiveFilters" class="ct-segment-empty">
                <i class="fa-solid fa-bookmark ct-segment-empty-icon"></i>
                <p>Nenhum segmento salvo.</p>
                <p class="ct-segment-hint">Configure os filtros acima e salve para reutilizar rapidamente.</p>
              </div>
              <div v-else-if="savedSegments.length > 0" class="ct-segment-list">
                <div v-for="(seg, idx) in savedSegments" :key="idx" class="ct-segment-item">
                  <button type="button" class="ct-segment-apply" @click="applySegment(seg)" :title="seg.description || seg.name">
                    <i class="fa-solid fa-bookmark"></i>
                    {{ seg.name }}
                  </button>
                  <button type="button" class="ct-segment-del" @click="deleteSegment(idx)" title="Excluir segmento">
                    <i class="fa-solid fa-xmark"></i>
                  </button>
                </div>
              </div>

              <!-- Save current filters as segment -->
              <template v-if="hasActiveFilters">
                <div v-if="!showSegmentInput" class="ct-segment-save-trigger">
                  <button type="button" class="ct-segment-save-btn" @click="showSegmentInput = true">
                    <i class="fa-solid fa-floppy-disk"></i>
                    Salvar filtros como segmento
                  </button>
                </div>
                <div v-else class="ct-segment-save-form">
                  <input
                    v-model="segmentNameDraft"
                    class="ct-input"
                    placeholder="Nome do segmento..."
                    @keyup.enter="saveSegment"
                    @keyup.esc="showSegmentInput = false"
                    autofocus
                  />
                  <div class="ct-segment-save-actions">
                    <button type="button" class="ct-btn-ghost" @click="showSegmentInput = false">Cancelar</button>
                    <button type="button" class="ct-btn-accent-sm" @click="saveSegment" :disabled="!segmentNameDraft.trim()">Salvar</button>
                  </div>
                </div>
              </template>

              <div v-else-if="savedSegments.length === 0" class="ct-segment-hint-only">
                <!-- already shown in empty state above -->
              </div>
            </div>
          </div>

        </aside>

        <!-- ════════════════════════════════ -->
        <!-- COL 2 — CONTACT LIST             -->
        <!-- ════════════════════════════════ -->
        <div class="ct-col-list">

          <!-- Bulk actions bar -->
          <div v-if="selectedContacts.length > 0" class="ct-bulk-bar">
            <span class="ct-bulk-info">
              <strong>{{ selectedContacts.length }}</strong> selecionado(s)
            </span>
            <div class="ct-bulk-actions">
              <button class="ct-btn-secondary" type="button" @click="bulkAddTag">
                <i class="fa-solid fa-tag"></i> Tag
              </button>
              <button class="ct-btn-secondary" type="button" @click="bulkExport">
                <i class="fa-solid fa-file-arrow-down"></i> Exportar
              </button>
              <button class="ct-btn-danger" type="button" @click="bulkDelete">
                <i class="fa-solid fa-trash"></i> Excluir
              </button>
              <button class="ct-btn-ghost" type="button" @click="selectedContacts = []" title="Desmarcar tudo">
                <i class="fa-solid fa-xmark"></i>
              </button>
            </div>
          </div>

          <!-- Loading skeletons -->
          <div v-if="loading" class="ct-skeletons">
            <div v-for="n in 10" :key="n" class="ct-skeleton-row">
              <div class="ct-sk ct-sk--cb"></div>
              <div class="ct-sk ct-sk--avatar"></div>
              <div class="ct-sk ct-sk--name"></div>
              <div class="ct-sk ct-sk--badge"></div>
              <div class="ct-sk ct-sk--tags"></div>
              <div class="ct-sk ct-sk--time"></div>
            </div>
          </div>

          <!-- Empty state -->
          <div v-else-if="filteredContacts.length === 0" class="ct-empty">
            <i class="fa-solid fa-users-slash ct-empty-icon"></i>
            <p>Nenhum contato encontrado</p>
            <button v-if="hasActiveFilters || searchQuery" class="ct-btn-secondary" type="button" @click="clearFilters(); searchQuery = ''">
              Limpar filtros
            </button>
          </div>

          <!-- Contact table -->
          <div v-else class="ct-table-wrap">
            <table class="ct-table">
              <thead>
                <tr>
                  <th class="ct-th-check">
                    <input type="checkbox" class="ct-checkbox" :checked="isAllSelected" @change="toggleSelectAll" />
                  </th>
                  <th>Contato</th>
                  <th>Canal</th>
                  <th>Tags</th>
                  <th>Inscrito</th>
                  <th class="ct-th-actions">Ações</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="c in filteredContacts"
                  :key="c.id"
                  class="ct-row"
                  :class="{ selected: selectedContacts.includes(c.id), 'row-active': selectedContact?.id === c.id }"
                  @click="viewContact(c.id)"
                >
                  <td @click.stop>
                    <input type="checkbox" class="ct-checkbox" :checked="selectedContacts.includes(c.id)" @change="toggleSelectContact(c.id)" />
                  </td>
                  <td>
                    <div class="ct-contact-cell">
                      <div class="ct-avatar" :style="{ background: c.avatarBg, color: c.avatarColor }">{{ c.initials }}</div>
                      <div>
                        <div class="ct-contact-name">{{ c.name }}</div>
                        <div class="ct-contact-sub">{{ c.username }}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span class="ct-badge" :class="c.channelBadge">{{ c.channel }}</span>
                  </td>
                  <td>
                    <span v-if="(c.tags || []).length === 0" class="ct-muted">—</span>
                    <span v-else>
                      <span v-for="t in c.tags.slice(0, 3)" :key="t" class="ct-tag-pill">{{ t }}</span>
                      <span v-if="c.tags.length > 3" class="ct-muted" style="font-size:0.75rem;"> +{{ c.tags.length - 3 }}</span>
                    </span>
                  </td>
                  <td class="ct-muted" style="font-size:0.82rem; white-space:nowrap;">{{ c.lastEventTime }}</td>
                  <td @click.stop class="ct-actions-cell">
                    <button class="ct-action-btn ct-action-btn--view" type="button" @click="viewContact(c.id)" title="Ver contato">
                      <i class="fa-solid fa-eye"></i>
                    </button>
                    <button class="ct-action-btn ct-action-btn--fields" type="button" @click="openFieldsModal(c)" title="Ver campos">
                      <i class="fa-solid fa-list-ul"></i>
                    </button>
                    <button class="ct-action-btn ct-action-btn--send" type="button" @click="openSendFlowModal(c)" title="Enviar fluxo">
                      <i class="fa-solid fa-paper-plane"></i>
                    </button>
                    <button class="ct-action-btn ct-action-btn--del" type="button" @click="openDeleteModal(c)" title="Excluir">
                      <i class="fa-solid fa-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <div v-if="!loading && totalContacts > 0" class="ct-pagination">
            <span class="ct-pg-meta">
              Página <strong>{{ currentPage }}</strong> de <strong>{{ totalPages }}</strong>
              <span class="ct-pg-sep">·</span>
              {{ totalContacts.toLocaleString('pt-BR') }} contatos
            </span>
            <div class="ct-pg-controls">
              <select class="ct-pg-select" v-model.number="pageLimit" :disabled="loading" @change="onChangePageSize">
                <option :value="25">25 / pág</option>
                <option :value="50">50 / pág</option>
                <option :value="100">100 / pág</option>
              </select>
              <button class="ct-pg-btn" type="button" :disabled="loading || currentPage <= 1" @click="goPrevPage">
                <i class="fa-solid fa-chevron-left"></i>
              </button>
              <button class="ct-pg-btn" type="button" :disabled="loading || currentPage >= totalPages" @click="goNextPage">
                <i class="fa-solid fa-chevron-right"></i>
              </button>
            </div>
          </div>

        </div>
        <!-- /ct-col-list -->

        <!-- ════════════════════════════════ -->
        <!-- COL 3 — CONTACT DETAIL PANEL     -->
        <!-- ════════════════════════════════ -->
        <div v-if="selectedContact" class="ct-col-detail" :style="{ width: detailWidth + 'px', minWidth: detailWidth + 'px' }">

          <!-- Resizer -->
          <div class="ct-detail-resizer" @mousedown.stop.prevent="startDetailResize"></div>

          <!-- Detail Header -->
          <div class="ct-detail-header">
            <div class="ct-detail-contact">
              <div class="ct-avatar ct-avatar--lg" :style="{ background: selectedContact.avatarBg, color: selectedContact.avatarColor }">
                {{ selectedContact.initials }}
              </div>
              <div class="ct-detail-info">
                <h3 class="ct-detail-name">{{ selectedContact.name }}</h3>
                <p class="ct-detail-sub">
                  {{ selectedContact.username }}<span v-if="selectedContact.username && selectedContact.channel"> · </span>{{ selectedContact.channel }}
                </p>
                <div v-if="canMergeTelegramDuplicates" style="margin-top:6px;">
                  <button class="ct-btn-secondary" style="font-size:0.72rem;padding:3px 10px;" :disabled="mergingDuplicates" @click="mergeSelectedContactDuplicates">
                    {{ mergingDuplicates ? 'Mesclando...' : 'Mesclar duplicados' }}
                  </button>
                </div>
              </div>
            </div>
            <button class="ct-detail-close" type="button" @click="closeContactView" title="Fechar">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <!-- Detail Tabs -->
          <div class="ct-detail-tabs">
            <button class="ct-detail-tab" :class="{ active: activeTab === 'info' }" @click="activeTab = 'info'">
              <i class="fa-solid fa-user"></i> Info
            </button>
            <button class="ct-detail-tab" :class="{ active: activeTab === 'tags' }" @click="activeTab = 'tags'">
              <i class="fa-solid fa-tags"></i> Tags
            </button>
            <button class="ct-detail-tab" :class="{ active: activeTab === 'messages' }" @click="activeTab = 'messages'">
              <i class="fa-solid fa-comment"></i> Chat
            </button>
            <button class="ct-detail-tab" :class="{ active: activeTab === 'history' }" @click="activeTab = 'history'">
              <i class="fa-solid fa-clock-rotate-left"></i> Histórico
            </button>
          </div>

          <!-- ── Tab: Info ── -->
          <div v-if="activeTab === 'info'" class="ct-detail-content">
            <div class="ct-info-grid">
              <div class="ct-info-item">
                <label>Nome</label>
                <span>{{ selectedContact.name || '—' }}</span>
              </div>
              <div class="ct-info-item">
                <label>Username</label>
                <span>{{ selectedContact.username || '—' }}</span>
              </div>
              <div class="ct-info-item">
                <label>Canal</label>
                <span class="ct-badge" :class="selectedContact.channelBadge">{{ selectedContact.channel }}</span>
              </div>
              <div class="ct-info-item">
                <label>Gênero</label>
                <span>{{ selectedContact.gender || '—' }}</span>
              </div>
              <div class="ct-info-item">
                <label>Status</label>
                <span class="ct-badge badge-success">{{ selectedContact.status }}</span>
              </div>
              <div class="ct-info-item">
                <label>Inscrito em</label>
                <span>{{ selectedContact.lastEventTime }}</span>
              </div>
            </div>

            <template v-if="selectedContact.customFields && Object.keys(selectedContact.customFields).length > 0">
              <h4 class="ct-info-section-title">Campos personalizados</h4>
              <div class="ct-info-grid">
                <div v-for="(value, key) in selectedContact.customFields" :key="key" class="ct-info-item">
                  <label>{{ key }}</label>
                  <span>{{ value }}</span>
                </div>
              </div>
            </template>
            <div v-else class="ct-detail-empty" style="margin-top:16px;">Nenhum campo personalizado.</div>
          </div>

          <!-- ── Tab: Tags ── -->
          <div v-if="activeTab === 'tags'" class="ct-detail-content">
            <div class="ct-tags-list">
              <span v-for="tag in selectedContact.tags" :key="tag" class="ct-tag-badge">
                {{ tag }}
                <button type="button" @click="removeTagFromContact(selectedContact.id, tag)">
                  <i class="fa-solid fa-xmark"></i>
                </button>
              </span>
              <div v-if="selectedContact.tags.length === 0" class="ct-detail-empty">Nenhuma tag atribuída.</div>
            </div>
            <div class="ct-add-tag">
              <input v-model="newTag" class="ct-input" placeholder="Nova tag..." @keyup.enter="addTagToContact" />
              <button class="ct-btn-accent-sm" type="button" @click="addTagToContact">
                <i class="fa-solid fa-plus"></i> Adicionar
              </button>
            </div>
          </div>

          <!-- ── Tab: Chat (Messages) ── -->
          <div v-if="activeTab === 'messages'" class="ct-detail-content ct-messages-wrap">

            <!-- Quick contact sidebar -->
            <div class="cql-panel">
              <div class="cql-header">
                <i class="fa-solid fa-users" style="font-size:11px;opacity:0.6;"></i>
                Conversas
              </div>
              <div class="cql-search-wrap">
                <input v-model="cqlSearch" class="cql-search" placeholder="Buscar..." />
              </div>
              <div class="cql-items">
                <button
                  v-for="c in chatQuickList"
                  :key="c.id"
                  :class="['cql-item', { 'cql-active': selectedContact?.id === c.id }]"
                  type="button"
                  @click="switchToContact(c.id)"
                >
                  <div class="cql-avatar" :style="{ background: c.avatarBg, color: c.avatarColor }">{{ c.initials }}</div>
                  <div class="cql-info">
                    <div class="cql-name">{{ c.name }}</div>
                    <div class="cql-preview">{{ quickContactLastMsg.get(c.id)?.preview || c.lastEvent }}</div>
                  </div>
                  <span class="cql-time">{{ quickContactLastMsg.get(c.id)?.time || c.lastEventTime }}</span>
                </button>
                <div v-if="chatQuickList.length === 0" class="cql-empty">Nenhum contato</div>
              </div>
            </div>

            <!-- Chat area -->
            <div class="messages-chat-wrap">
              <div class="messages-panel">

                <!-- Topbar -->
                <div class="tg-topbar">
                  <button v-if="messagesHasMore" class="tg-load-more" type="button" :disabled="loadingMessages" @click="loadOlderMessages">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="18 15 12 9 6 15"/></svg>
                    {{ loadingMessages ? 'Carregando...' : 'Mensagens mais antigas' }}
                  </button>
                  <span v-else class="tg-meta">Início do histórico</span>
                  <span class="tg-meta" v-if="messages.length > 0">{{ messages.length }} mensagem(ns)</span>
                  <button v-if="showJumpToBottom" class="tg-jump-btn" type="button" @click="scrollMessagesToBottom" title="Ir para o final">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
                  </button>
                </div>

                <!-- Scroller -->
                <div ref="messagesScroller" class="tg-scroller" @scroll="onMessagesScroll">
                  <div v-if="loadingMessages && messages.length === 0" class="tg-loading">
                    <svg class="tg-spinner" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/>
                      <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
                      <line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/>
                      <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
                    </svg>
                    Carregando mensagens...
                  </div>
                  <div v-else-if="messages.length === 0" class="tg-empty">
                    <svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                    </svg>
                    <p>Nenhuma mensagem ainda</p>
                  </div>
                  <div v-else class="tg-feed">
                    <template v-for="item in messagesFeed" :key="item.key">
                      <div v-if="item.type === 'day'" class="tg-day-pill"><span>{{ item.label }}</span></div>
                      <div v-else :class="['tg-row', item.msg.direction === 'inbound' ? 'tg-in' : 'tg-out']">
                        <div class="tg-bubble">
                          <div v-if="item.msg.extra_data?.forwarded_from" class="tg-fwd">
                            <svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor"><path d="M14 5l7 7-7 7V13H3v-2h11V5z"/></svg>
                            Encaminhado de <strong>{{ item.msg.extra_data.forwarded_from }}</strong>
                          </div>
                          <div v-if="!item.msg.message_type || item.msg.message_type === 'text'" class="tg-text">{{ item.msg.content }}</div>
                          <div v-else-if="item.msg.message_type === 'file'" class="tg-file">
                            <div class="tg-file-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/></svg></div>
                            <div class="tg-file-info">
                              <div class="tg-file-name">{{ item.msg.extra_data?.file_name || item.msg.content || 'Arquivo' }}</div>
                              <div class="tg-file-size" v-if="item.msg.extra_data?.file_size">{{ formatBytes(item.msg.extra_data.file_size) }}</div>
                            </div>
                          </div>
                          <div v-else-if="item.msg.message_type === 'voice'" class="tg-voice">
                            <div class="tg-voice-play">▶</div>
                            <div class="tg-waveform"><div v-for="n in 20" :key="n" class="tg-wave-bar" :style="{ '--h': ((n * 7 + 3) % 10) / 10 }"></div></div>
                            <span class="tg-voice-dur" v-if="item.msg.extra_data?.duration">{{ formatDuration(item.msg.extra_data.duration) }}</span>
                          </div>
                          <div v-else-if="item.msg.message_type === 'image'" class="tg-image-wrap">
                            <a v-if="item.msg.content && isProbablyUrl(item.msg.content)" :href="item.msg.content" target="_blank" rel="noopener noreferrer">
                              <img :src="item.msg.content" alt="Imagem" class="tg-img" />
                            </a>
                            <div v-else class="tg-text">[Imagem recebida]</div>
                            <div v-if="item.msg.extra_data?.caption" class="tg-caption">{{ item.msg.extra_data.caption }}</div>
                          </div>
                          <div v-else-if="item.msg.message_type === 'audio'" class="tg-media">
                            <audio v-if="item.msg.content && isProbablyUrl(item.msg.content)" controls :src="item.msg.content" class="tg-audio"></audio>
                            <div v-else class="tg-text">🎵 {{ item.msg.extra_data?.title || item.msg.extra_data?.file_name || 'Áudio' }}</div>
                            <div v-if="item.msg.extra_data?.caption" class="tg-caption">{{ item.msg.extra_data.caption }}</div>
                          </div>
                          <div v-else-if="item.msg.message_type === 'video' || item.msg.message_type === 'video_note'" class="tg-media">
                            <video v-if="item.msg.content && isProbablyUrl(item.msg.content)" controls :src="item.msg.content" class="tg-video"></video>
                            <div v-else class="tg-text">[Vídeo recebido]</div>
                            <div v-if="item.msg.extra_data?.caption" class="tg-caption">{{ item.msg.extra_data.caption }}</div>
                          </div>
                          <div v-else class="tg-text">{{ item.msg.content }}</div>
                          <div class="tg-footer">
                            <span class="tg-time">{{ formatMessageTime(item.msg.created_at) }}</span>
                            <span v-if="item.msg.direction === 'outbound'" class="tg-ticks">
                              <svg v-if="item.msg.status === 'read'" width="16" height="11" viewBox="0 0 16 11" fill="rgba(255,255,255,0.7)"><path d="M1 5.5L4.5 9 9 1M5 5.5L8.5 9 13 1"/></svg>
                              <svg v-else-if="item.msg.status === 'delivered'" width="16" height="11" viewBox="0 0 16 11" fill="none" stroke="rgba(255,255,255,0.55)" stroke-width="1.8"><polyline points="1,5.5 4.5,9 9,1"/><polyline points="5,5.5 8.5,9 13,1"/></svg>
                              <svg v-else width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="rgba(255,255,255,0.45)" stroke-width="1.8"><polyline points="1,5 4,8 9,1"/></svg>
                            </span>
                          </div>
                          <button v-if="item.msg.content" class="tg-copy" type="button" @click="copyMessage(item.msg)" title="Copiar">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                          </button>
                        </div>
                      </div>
                    </template>
                  </div>
                </div>

                <!-- Composer -->
                <div class="tg-composer">
                  <div v-if="showEmojiPicker" ref="emojiPickerRef" class="tg-emoji-picker">
                    <button v-for="e in emojiList" :key="e" type="button" class="tg-emoji-btn" @click="insertEmoji(e)">{{ e }}</button>
                  </div>
                  <div v-if="uploadingMedia" class="tg-upload-status">
                    <svg class="tg-spinner" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>
                    <span>Enviando {{ pendingMediaName }}…</span>
                  </div>
                  <div class="tg-format-bar">
                    <button type="button" class="tg-fmt-btn" title="Enviar mídia" :disabled="uploadingMedia" @click="triggerMediaUpload">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
                    </button>
                    <button type="button" class="tg-fmt-btn tg-vnote-btn" title="Vídeo nota circular" :disabled="uploadingMedia" @click="triggerVideoNoteUpload">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><polygon points="10 8 16 12 10 16 10 8" fill="currentColor" stroke="none"/></svg>
                    </button>
                    <span class="tg-fmt-sep"></span>
                    <button type="button" class="tg-fmt-btn" title="Negrito" @click="insertFormat('bold')"><b>B</b></button>
                    <button type="button" class="tg-fmt-btn" title="Itálico" @click="insertFormat('italic')"><i>I</i></button>
                    <button type="button" class="tg-fmt-btn" title="Sublinhado" @click="insertFormat('underline')"><u>U</u></button>
                    <button type="button" class="tg-fmt-btn" title="Riscado" @click="insertFormat('strike')"><s>S</s></button>
                    <button type="button" class="tg-fmt-btn" title="Código" @click="insertFormat('code')"><code style="font-size:0.8em">&lt;/&gt;</code></button>
                    <span class="tg-fmt-sep"></span>
                    <button ref="emojiToggleBtnRef" type="button" class="tg-fmt-btn" :class="{ active: showEmojiPicker }" title="Emojis" @click="showEmojiPicker = !showEmojiPicker">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>
                    </button>
                  </div>
                  <div class="tg-input-row">
                    <textarea
                      ref="composerRef"
                      v-model="composerText"
                      class="tg-textarea"
                      placeholder="Escreva uma mensagem..."
                      rows="1"
                      @keydown.enter.exact.prevent="sendMessage"
                      @keydown.ctrl.enter.exact="composerText += '\n'"
                      @input="autoResizeComposer"
                    ></textarea>
                    <button type="button" class="tg-send-btn" :disabled="!composerText.trim() || sendingMessage" @click="sendMessage" title="Enviar">
                      <svg v-if="!sendingMessage" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                      <svg v-else class="tg-spinner" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>
                    </button>
                  </div>
                  <input type="file" ref="mediaFileInput" accept="image/*,video/*,audio/*" style="display:none" @change="handleMediaUpload">
                  <input type="file" ref="videoNoteFileInput" accept="video/*" style="display:none" @change="handleVideoNoteUpload">
                </div>

              </div>
            </div>

          </div>
          <!-- /ct-messages-wrap -->

          <!-- ── Tab: History ── -->
          <div v-if="activeTab === 'history'" class="ct-detail-content">
            <div class="ct-history">
              <div v-if="loadingHistory" class="ct-detail-empty">Carregando histórico...</div>
              <div v-else>
                <div class="ct-history-item">
                  <div class="ct-history-dot ct-history-dot--green"></div>
                  <div>
                    <div class="ct-history-title">Contato criado</div>
                    <div class="ct-history-time">{{ selectedContact.created_at ? formatDate(selectedContact.created_at) : selectedContact.lastEventTime }}</div>
                  </div>
                </div>
                <div v-if="flowHistory.length === 0" class="ct-detail-empty" style="margin-top:12px;">
                  Nenhum fluxo executado ainda.
                </div>
                <div v-for="h in flowHistory" :key="h.flow_id" class="ct-history-item">
                  <div class="ct-history-dot"></div>
                  <div>
                    <div class="ct-history-title">{{ h.flow_name }}</div>
                    <div class="ct-history-time">
                      Executado {{ h.execution_count }}x
                      <span v-if="h.last_execution"> · Último: {{ formatLastExecution(h.last_execution) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
        <!-- /ct-col-detail -->

      </div>
      <!-- /ct-body -->

      </template>

    </div>
    <!-- /ct-page -->

    <!-- ══════════════════════════════════════════ -->
    <!-- MODALS                                    -->
    <!-- ══════════════════════════════════════════ -->

    <!-- Modal: Enviar Fluxo -->
    <div v-if="showSendFlowModal" class="modal-overlay" @click="closeSendFlowModal">
      <div class="modal-content send-flow-modal" @click.stop>
        <div class="modal-header">
          <div>
            <h3 class="modal-title">Enviar Fluxo</h3>
            <p class="modal-subtitle">
              <span class="contact-name-badge">{{ contactToSendFlow?.name }}</span>
            </p>
          </div>
          <button class="btn-close-modal" @click="closeSendFlowModal">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <p class="modal-description">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: text-bottom; margin-right: 6px;">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="16" x2="12" y2="12"/>
              <line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>
            Selecione um fluxo para iniciar imediatamente:
          </p>
          
          <div v-if="availableFlows.length > 0" class="flows-grid">
            <div 
              v-for="flow in availableFlows" 
              :key="flow.id"
              class="flow-card"
              :class="{ 
                'selected': selectedFlowToSend === flow.id,
                'already-sent': flow.already_sent
              }"
              @click="selectedFlowToSend = flow.id"
            >
              <div v-if="flow.already_sent" class="flow-already-sent-badge">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                Enviado {{ flow.execution_count }}x
              </div>
              
              <div class="flow-card-header">
                <div class="flow-card-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="18" cy="18" r="3"/>
                    <circle cx="6" cy="6" r="3"/>
                    <path d="M13 6h3a2 2 0 0 1 2 2v7"/>
                  </svg>
                </div>
                <div class="flow-card-check">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                </div>
              </div>
              <div class="flow-card-body">
                <h4 class="flow-card-title">{{ flow.name }}</h4>
                <p class="flow-card-description">{{ flow.description || 'Fluxo de automação' }}</p>
                <p v-if="flow.already_sent && flow.last_execution" class="flow-last-sent">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                  Último: {{ formatLastExecution(flow.last_execution) }}
                </p>
              </div>
              <div class="flow-card-footer">
                <span class="flow-card-badge" :class="`badge-${flow.system || 'telegram'}`">
                  {{ flow.system || 'telegram' }}
                </span>
                <span v-if="flow.steps_count" class="flow-card-meta">
                  {{ flow.steps_count }} etapa(s)
                </span>
              </div>
            </div>
          </div>

          <div v-else class="empty-state-flows">
            <div class="empty-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="18" cy="18" r="3"/>
                <circle cx="6" cy="6" r="3"/>
                <path d="M13 6h3a2 2 0 0 1 2 2v7"/>
              </svg>
            </div>
            <h4>Nenhum fluxo ativo</h4>
            <p>Crie e ative fluxos para poder enviá-los aos seus contatos</p>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeSendFlowModal">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
            Cancelar
          </button>
          <button 
            class="btn btn-primary" 
            @click="sendFlowToContact"
            :disabled="!selectedFlowToSend || sendingFlow"
          >
            <svg v-if="!sendingFlow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" opacity="0.25"/>
              <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round">
                <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
              </path>
            </svg>
            {{ sendingFlow ? 'Enviando...' : 'Enviar Fluxo' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Deletar Contato -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content delete-contact-modal" @click.stop>
        <div class="modal-header">
          <div class="delete-icon-warning">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <h3 class="modal-title">Excluir Contato?</h3>
          <button class="btn-close-modal" @click="closeDeleteModal">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <p class="delete-warning-text">
            Você está prestes a excluir o contato:
          </p>
          <div class="delete-contact-info">
            <div class="contact-avatar" :style="{ background: contactToDelete?.avatarBg, color: contactToDelete?.avatarColor }">
              {{ contactToDelete?.initials }}
            </div>
            <div>
              <strong>{{ contactToDelete?.name }}</strong>
              <p style="color: var(--muted); font-size: 0.875rem; margin: 4px 0 0;">{{ contactToDelete?.username }}</p>
            </div>
          </div>
          <div class="delete-warning-box">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <div>
              <strong>Atenção:</strong> Esta ação não pode ser desfeita.<br>
              Todo o histórico de mensagens e dados deste contato serão perdidos permanentemente.
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeDeleteModal">
            Cancelar
          </button>
          <button 
            class="btn btn-danger" 
            @click="deleteContact"
            :disabled="deleting"
          >
            <svg v-if="!deleting" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              <line x1="10" y1="11" x2="10" y2="17"/>
              <line x1="14" y1="11" x2="14" y2="17"/>
            </svg>
            {{ deleting ? 'Excluindo...' : 'Excluir Contato' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Campos do contato -->
    <div v-if="showFieldsModal" class="modal-overlay" @click="closeFieldsModal">
      <div class="modal-content fields-modal" @click.stop>
        <div class="modal-header">
          <div>
            <h3 class="modal-title">Campos do contato</h3>
            <p class="modal-subtitle">
              <span class="contact-name-badge">{{ contactToShowFields?.name }}</span>
            </p>
          </div>
          <button class="btn-close-modal" @click="closeFieldsModal" aria-label="Fechar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <div class="fields-sections">
            <section class="fields-section">
              <h4 class="fields-section-title">Campos do sistema</h4>
              <div class="fields-grid">
                <div v-for="item in systemFieldsForModal" :key="item.key" class="field-row">
                  <div class="field-key">{{ item.label }}</div>
                  <div class="field-value">{{ item.value }}</div>
                </div>
              </div>
            </section>

            <section class="fields-section">
              <h4 class="fields-section-title">Campos personalizados</h4>
              <div v-if="customFieldsForModal.length === 0" class="fields-empty">—</div>
              <div v-else class="fields-grid">
                <div v-for="item in customFieldsForModal" :key="item.key" class="field-row">
                  <div class="field-key">{{ item.key }}</div>
                  <div class="field-value">{{ item.value }}</div>
                </div>
              </div>
            </section>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeFieldsModal">Fechar</button>
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
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { listContacts, getContact, getContactMessages, getContactsStats, getContactsFieldStats, addContactTag, removeContactTag, mergeTelegramContactDuplicates, deleteContact as deleteContactAPI, sendMessageToContact, sendMediaToContact } from '@/api/contacts'
import { listChannels } from '@/api/channels'

const searchQuery = ref('')
const toast = useToast()
const confirmDialog = useConfirmDialog()
const pageLoading = ref(true)
const loading = ref(false)
const loadingMore = ref(false)
const filtersOpen = ref(true)

const contacts = ref([])
const totalContacts = ref(0)
const pageLimit = ref(50)
const pageOffset = ref(0)
const selectedContact = ref(null)
const detailWidth = ref(380)
const DETAIL_MIN_W = 280
const DETAIL_MAX_W = 800
let _detailResizing = false
let _detailStartX = 0
let _detailStartW = 0

const startDetailResize = (e) => {
  _detailResizing = true
  _detailStartX = e.clientX
  _detailStartW = detailWidth.value
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
  document.addEventListener('mousemove', onDetailResizeMove)
  document.addEventListener('mouseup', onDetailResizeUp)
}
const onDetailResizeMove = (e) => {
  if (!_detailResizing) return
  const delta = _detailStartX - e.clientX
  detailWidth.value = Math.min(DETAIL_MAX_W, Math.max(DETAIL_MIN_W, _detailStartW + delta))
}
const onDetailResizeUp = () => {
  _detailResizing = false
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
  document.removeEventListener('mousemove', onDetailResizeMove)
  document.removeEventListener('mouseup', onDetailResizeUp)
}
const messages = ref([])
const loadingMessages = ref(false)
const messagesOffset = ref(0)
const messagesPageLimit = ref(60)
const messagesHasMore = ref(true)
const messagesScroller = ref(null)
const showJumpToBottom = ref(false)
const composerText = ref('')
const composerRef = ref(null)
const sendingMessage = ref(false)
const showEmojiPicker = ref(false)
const emojiPickerRef = ref(null)
const emojiToggleBtnRef = ref(null)
const mediaFileInput = ref(null)
const videoNoteFileInput = ref(null)
const uploadingMedia = ref(false)
const pendingMediaName = ref('')
const quickContactLastMsg = ref(new Map())
const cqlSearch = ref('')

const emojiList = [
  '😀','😂','😅','😊','😍','🥰','😎','🤩','🙏','👍','👏','🔥','❤️','💯',
  '😢','😭','😡','🤔','😴','🤗','😏','😮','🤣','😜','🤪','😇','🥳','😤',
  '👋','✌️','🤝','💪','🫡','🫶','🙌','👀','💬','📩','📣','📌','🎉','🎊',
  '✅','❌','⚠️','📊','📈','🚀','💡','🔔','🔕','🔑','📱','💻','⏰','🌟',
  '😸','🐶','🐱','🦊','🐻','🐼','🦁','🐸','🙈','🐝','🌈','☀️','🌙','⭐',
  '🍕','🍔','🍦','☕','🥤','🍺','🎵','🎮','⚽','🏆','🎯','🎲','🃏','🧩'
]

function isProbablyUrl(value) {
  if (!value || typeof value !== 'string') return false
  return /^https?:\/\//i.test(value)
}

function formatBytes(bytes) {
  const value = Number(bytes)
  if (!Number.isFinite(value) || value <= 0) return ''
  const units = ['B', 'KB', 'MB', 'GB']
  const idx = Math.min(units.length - 1, Math.floor(Math.log(value) / Math.log(1024)))
  const sized = value / Math.pow(1024, idx)
  const decimals = idx === 0 ? 0 : idx === 1 ? 0 : 1
  return `${sized.toFixed(decimals)} ${units[idx]}`
}

function formatDuration(totalSeconds) {
  const seconds = Math.max(0, Math.floor(Number(totalSeconds) || 0))
  const m = String(Math.floor(seconds / 60)).padStart(2, '0')
  const s = String(seconds % 60).padStart(2, '0')
  return `${m}:${s}`
}
const loadingHistory = ref(false)
const flowHistory = ref([])
const lastLoadedMessagesFor = ref(null)
const lastLoadedHistoryFor = ref(null)
const selectedContacts = ref([])
const activeTab = ref('info')
const newTag = ref('')
const mergingDuplicates = ref(false)

// Filtros
const selectedChannelId = ref(null)
const selectedTags = ref([])
const selectedFieldFilters = ref([])
const availableFieldPairs = ref([])

const fieldDraft = ref('')
const valueDraft = ref('')

const availableFieldKeys = computed(() => {
  const items = Array.isArray(availableFieldPairs.value) ? availableFieldPairs.value : []
  const totals = new Map()
  for (const it of items) {
    const field = String(it?.field || '').trim()
    if (!field) continue
    if (field === 'None' || field === 'null' || field === 'undefined') continue
    totals.set(field, (totals.get(field) || 0) + Number(it?.count || 0))
  }
  const out = Array.from(totals.entries())
    .sort((a, b) => b[1] - a[1])
    .map(([field]) => field)
  return out.slice(0, 120)
})

// Retráteis
const channelsCollapsed = ref(false)
const tagsCollapsed = ref(false)
const fieldsCollapsed = ref(false)

const normalizedFieldConditions = computed(() => {
  const list = Array.isArray(selectedFieldFilters.value) ? selectedFieldFilters.value : []
  return list
    .filter(it => it && String(it.field || '').trim() && String(it.value || '').trim())
    .map(it => ({
      source: 'custom',
      field: String(it.field).trim(),
      op: 'eq',
      value: String(it.value).trim(),
      value_type: 'string',
    }))
})

const addFieldFilter = () => {
  const field = String(fieldDraft.value || '').trim()
  const value = String(valueDraft.value || '').trim()
  if (!field) {
    toast.error('Selecione um campo')
    return
  }
  if (!value) {
    toast.error('Informe um valor')
    return
  }
  const key = JSON.stringify([field, value])
  if (selectedFieldFilters.value.some(it => it?.key === key)) {
    toast.error('Esse filtro já foi adicionado')
    return
  }
  selectedFieldFilters.value.push({ field, value, key })
  valueDraft.value = ''
  nextTick(() => {
    try {
      const el = document.querySelector('.field-builder input.field-builder-value')
      el?.focus?.()
    } catch {}
  })
}

const removeFieldFilter = (idx) => {
  if (idx < 0) return
  selectedFieldFilters.value.splice(idx, 1)
}

const removeLastFieldFilter = () => {
  if (selectedFieldFilters.value.length === 0) return
  selectedFieldFilters.value.pop()
}

// Canais disponíveis
const availableChannels = ref([])

// Stats reais (para counts na sidebar)
const contactStats = ref({ contacts_total: 0, by_channel: [], by_tag: [] })

// Dados dos filtros
const availableTags = computed(() => {
  return (contactStats.value.by_tag || []).map(t => ({ name: t.name, count: t.count }))
})

// Widgets/Sequências removidos do MVP (voltam quando houver backend)

// Funções auxiliares
const getInitials = (firstName, lastName) => {
  const first = (firstName || '').charAt(0).toUpperCase()
  const last = (lastName || '').charAt(0).toUpperCase()
  return first + last || '??'
}

const getAvatarColors = (id) => {
  const colors = [
    { bg: 'var(--accent-soft)', color: 'var(--accent)' },
    { bg: 'rgba(251, 191, 36, 0.15)', color: '#fbbf24' },
    { bg: 'rgba(14, 165, 233, 0.15)', color: '#0ea5e9' },
    { bg: 'rgba(251, 113, 133, 0.15)', color: '#fb7185' },
    { bg: 'rgba(139, 92, 246, 0.15)', color: '#8b5cf6' }
  ]
  return colors[id % colors.length]
}

const getChannelBadge = (channelType) => {
  const badges = {
    telegram: 'badge-muted'
  }
  return badges[channelType] || 'badge-muted'
}

const mapContactFromBackend = (contact) => {
  const colors = getAvatarColors(contact.id)
  const fullName = [contact.first_name, contact.last_name].filter(Boolean).join(' ') || 'Sem nome'

  return {
    id: contact.id,
    name: fullName,
    username: contact.username ? `@${contact.username}` : '',
    initials: getInitials(contact.first_name, contact.last_name),
    avatarBg: colors.bg,
    avatarColor: colors.color,
    created_at: contact.created_at,
    default_channel_id: contact.default_channel_id,
    channel: contact.channel_name || (contact.channel_type || 'Desconhecido'),
    channelBadge: getChannelBadge(contact.channel_type),
    tags: contact.tags || [],
    customFields: contact.custom_fields || {},
    lastEvent: 'Iniciou conversa',
    lastEventTime: formatDate(contact.created_at),
    status: 'Ativo',
    statusBadge: 'badge-success',
    gender: contact.custom_fields?.genero || contact.custom_fields?.gender || null,
    activeSequences: []
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Sem data'
  
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  if (isNaN(date.getTime())) return 'Sem data'

  // Se por timezone/clock skew a data vier "no futuro", não exibir negativo.
  if (diffMs < 0) {
    const aheadMins = Math.abs(diffMs) / 60000
    if (aheadMins < 2) return 'agora'
    return date.toLocaleDateString('pt-BR')
  }

  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'agora'
  if (diffMins < 60) return `há ${diffMins}min`
  if (diffHours < 24) return `há ${diffHours}h`
  if (diffDays < 7) return `há ${diffDays}d`
  
  return date.toLocaleDateString('pt-BR')
}

const canMergeTelegramDuplicates = computed(() => {
  const c = selectedContact.value
  if (!c) return false
  const userId = c.customFields?.telegram_user_id
  return Boolean(c.default_channel_id && userId)
})

const mergeSelectedContactDuplicates = async () => {
  if (!selectedContact.value) return
  const telegramUserId = selectedContact.value.customFields?.telegram_user_id
  if (!telegramUserId) {
    toast.error('Esse contato não tem telegram_user_id')
    return
  }

  mergingDuplicates.value = true
  try {
    const res = await mergeTelegramContactDuplicates({
      channel_id: selectedContact.value.default_channel_id,
      telegram_user_id: telegramUserId,
      keep_contact_id: selectedContact.value.id
    })

    toast.success('Duplicados mesclados')

    // Recarregar lista e manter selecionado o contato principal
    const keepId = res.keep_contact_id || selectedContact.value.id
    await loadContacts()
    const updated = contacts.value.find(c => c.id === keepId)
    if (updated) {
      selectedContact.value = updated
      if (activeTab.value === 'messages') {
        await loadMessagesForContact(keepId)
      }
    } else {
      selectedContact.value = null
    }
  } catch (error) {
    console.error('❌ Erro ao mesclar duplicados:', error)
    toast.error('Erro ao mesclar duplicados')
  } finally {
    mergingDuplicates.value = false
  }
}

const normalizeMessagesPage = (data) => {
  const arr = Array.isArray(data) ? data : []
  // Backend vem "desc" (newest-first). Para UI de chat, exibimos asc (oldest-first).
  return arr.slice().reverse()
}

const scrollMessagesToBottom = async () => {
  await nextTick()
  const el = messagesScroller.value
  if (!el) return
  el.scrollTop = el.scrollHeight
}

const onMessagesScroll = () => {
  const el = messagesScroller.value
  if (!el) return
  const distanceFromBottom = el.scrollHeight - (el.scrollTop + el.clientHeight)
  showJumpToBottom.value = distanceFromBottom > 220
}

const loadMessagesForContact = async (contactId, { reset = true } = {}) => {
  if (!contactId) return
  if (loadingMessages.value) return

  if (reset) {
    messagesOffset.value = 0
    messagesHasMore.value = true
    messages.value = []
  }

  loadingMessages.value = true
  const scroller = messagesScroller.value
  const prevScrollHeight = scroller ? scroller.scrollHeight : 0
  const prevScrollTop = scroller ? scroller.scrollTop : 0

  try {
    const page = await getContactMessages(contactId, {
      limit: messagesPageLimit.value,
      offset: messagesOffset.value,
      order: 'desc'
    })

    const normalized = normalizeMessagesPage(page)

    if (reset) {
      messages.value = normalized
      await scrollMessagesToBottom()
    } else {
      // Carregando mais antigas: prepend preservando scroll
      messages.value = normalized.concat(messages.value)
      await nextTick()
      if (scroller) {
        const newScrollHeight = scroller.scrollHeight
        scroller.scrollTop = newScrollHeight - prevScrollHeight + prevScrollTop
      }
    }

    messagesHasMore.value = Array.isArray(page) && page.length === messagesPageLimit.value
    lastLoadedMessagesFor.value = contactId

    // Atualizar preview na sidebar de contatos
    const allMsgs = messages.value
    if (allMsgs.length > 0) {
      const lastMsg = allMsgs[allMsgs.length - 1]
      const preview = (lastMsg.content || lastMsg.message_type || '...').slice(0, 42)
      const newMap = new Map(quickContactLastMsg.value)
      newMap.set(contactId, {
        preview,
        time: formatMessageTime(lastMsg.created_at),
        rawTime: new Date(lastMsg.created_at || 0)
      })
      quickContactLastMsg.value = newMap
    }
    console.error('❌ Erro ao carregar mensagens:', error)
    toast.error('Erro ao carregar mensagens')
  } finally {
    loadingMessages.value = false
  }
}

const loadOlderMessages = async () => {
  if (!selectedContact.value) return
  if (!messagesHasMore.value) return
  messagesOffset.value += messagesPageLimit.value
  await loadMessagesForContact(selectedContact.value.id, { reset: false })
}

const copyMessage = async (msg) => {
  const text = String(msg?.content || '').trim()
  if (!text) return
  try {
    await navigator.clipboard.writeText(text)
    toast.success('Mensagem copiada')
  } catch {
    // fallback simples
    try {
      const ta = document.createElement('textarea')
      ta.value = text
      ta.style.position = 'fixed'
      ta.style.left = '-10000px'
      document.body.appendChild(ta)
      ta.focus()
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
      toast.success('Mensagem copiada')
    } catch {
      toast.error('Não foi possível copiar')
    }
  }
}

const sendMessage = async () => {
  const text = composerText.value.trim()
  if (!text || !selectedContact.value) return
  if (sendingMessage.value) return

  sendingMessage.value = true
  showEmojiPicker.value = false
  try {
    const saved = await sendMessageToContact(selectedContact.value.id, text)
    composerText.value = ''
    await nextTick()
    if (composerRef.value) {
      composerRef.value.style.height = 'auto'
    }
    // append to feed optimistically or reload
    if (saved && saved.id) {
      messages.value.push(saved)
      await scrollMessagesToBottom()
    } else {
      await loadMessagesForContact(selectedContact.value.id, { reset: true })
    }
  } catch (err) {
    const detail = err?.response?.data?.detail || 'Erro ao enviar mensagem'
    toast.error(detail)
  } finally {
    sendingMessage.value = false
    await nextTick()
    composerRef.value?.focus()
  }
}

const insertFormat = (type) => {
  const el = composerRef.value
  if (!el) return
  const start = el.selectionStart
  const end = el.selectionEnd
  const sel = composerText.value.slice(start, end)
  const tokens = { bold: ['*', '*'], italic: ['_', '_'], underline: ['__', '__'], strike: ['~', '~'], code: ['`', '`'] }
  const [open, close] = tokens[type] || ['', '']
  const placeholder = sel || (type === 'bold' ? 'negrito' : type === 'italic' ? 'itálico' : type === 'underline' ? 'sublinhado' : type === 'strike' ? 'riscado' : 'código')
  const before = composerText.value.slice(0, start)
  const after = composerText.value.slice(end)
  composerText.value = before + open + placeholder + close + after
  nextTick(() => {
    el.focus()
    const pos = start + open.length + placeholder.length + close.length
    el.setSelectionRange(pos, pos)
  })
}

const insertEmoji = (emoji) => {
  showEmojiPicker.value = false
  const el = composerRef.value
  if (!el) {
    composerText.value += emoji
    return
  }
  const start = el.selectionStart ?? composerText.value.length
  composerText.value = composerText.value.slice(0, start) + emoji + composerText.value.slice(start)
  nextTick(() => {
    el.focus()
    const pos = start + emoji.length
    el.setSelectionRange(pos, pos)
  })
}

const autoResizeComposer = () => {
  const el = composerRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

const triggerMediaUpload = () => {
  if (mediaFileInput.value) mediaFileInput.value.click()
}

const triggerVideoNoteUpload = () => {
  if (videoNoteFileInput.value) videoNoteFileInput.value.click()
}

const handleMediaUpload = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  event.target.value = ''
  let mediaType = 'auto'
  if (file.type.startsWith('image/')) mediaType = 'photo'
  else if (file.type.startsWith('video/')) mediaType = 'video'
  else if (file.type.startsWith('audio/')) mediaType = 'audio'
  else {
    toast.error('Tipo não suportado. Use imagens, vídeos ou áudios.')
    return
  }
  await sendMedia(file, mediaType)
}

const handleVideoNoteUpload = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  event.target.value = ''
  await sendMedia(file, 'video_note')
}

const sendMedia = async (file, mediaType) => {
  if (!selectedContact.value) return
  uploadingMedia.value = true
  pendingMediaName.value = file.name
  try {
    const saved = await sendMediaToContact(selectedContact.value.id, file, mediaType)
    if (saved && saved.id) {
      messages.value.push(saved)
      await scrollMessagesToBottom()
    } else {
      await loadMessagesForContact(selectedContact.value.id, { reset: true })
    }
    toast.success('Mídia enviada!')
  } catch (err) {
    const detail = err?.response?.data?.detail || 'Erro ao enviar mídia'
    toast.error(detail)
  } finally {
    uploadingMedia.value = false
    pendingMediaName.value = ''
  }
}

const messagesFeed = computed(() => {
  const items = []
  let lastDay = null
  for (const msg of (messages.value || [])) {
    const d = msg?.created_at ? new Date(msg.created_at) : null
    const dayLabel = d && !isNaN(d.getTime())
      ? d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
      : 'Sem data'

    if (dayLabel !== lastDay) {
      items.push({ type: 'day', key: `day:${dayLabel}`, label: dayLabel })
      lastDay = dayLabel
    }
    items.push({ type: 'message', key: `msg:${msg.id}`, msg })
  }
  return items
})

const loadHistoryForContact = async (contactId) => {
  loadingHistory.value = true
  try {
    const data = await (await import('@/api/contacts')).getContactFlowHistory(contactId)
    flowHistory.value = Array.isArray(data) ? data : []
    lastLoadedHistoryFor.value = contactId
  } catch (error) {
    console.error('❌ Erro ao carregar histórico:', error)
    toast.error('Erro ao carregar histórico')
  } finally {
    loadingHistory.value = false
  }
}

// Carregar canais disponíveis
const loadChannels = async () => {
  try {
    availableChannels.value = await listChannels()
  } catch (error) {
    console.error('❌ Erro ao carregar canais:', error)
  }
}

const loadContactStats = async () => {
  try {
    contactStats.value = await getContactsStats()
  } catch (error) {
    console.error('❌ Erro ao carregar stats de contatos:', error)
  }
}

const loadFieldStats = async () => {
  try {
    const data = await getContactsFieldStats({ limit: 60 })
    const list = Array.isArray(data) ? data : []
    availableFieldPairs.value = list
      .filter(it => {
        if (!it) return false
        const field = it.field
        const value = it.value
        if (field === null || field === undefined) return false
        if (value === null || value === undefined) return false
        if (String(field).trim() === '') return false
        if (String(value).trim() === '') return false
        return true
      })
      .map(it => {
        const field = String(it.field)
        const value = String(it.value)
        const count = Number(it.count || 0)
        return {
          field,
          value,
          count,
          key: JSON.stringify([field, value]),
        }
      })
  } catch (error) {
    console.error('❌ Erro ao carregar stats de campos:', error)
    availableFieldPairs.value = []
  }
}

// Carregar contatos do backend
const loadContacts = async ({ reset = true } = {}) => {
  if (reset) {
    loading.value = true
    selectedContacts.value = []
  }

  try {
    const offset = pageOffset.value
    const res = await listContacts({
      limit: pageLimit.value,
      offset,
      search: searchQuery.value || undefined,
      channel_id: selectedChannelId.value || undefined,
      tags: selectedTags.value.length > 0 ? selectedTags.value : undefined,
      field_conditions: normalizedFieldConditions.value.length > 0
        ? JSON.stringify(normalizedFieldConditions.value)
        : undefined,
    })

    const mapped = (res.items || []).map(mapContactFromBackend)
    totalContacts.value = typeof res.total === 'number' ? res.total : mapped.length
    contacts.value = mapped
  } catch (error) {
    console.error('❌ Erro ao carregar contatos:', error)
    toast.error('Erro ao carregar contatos')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

// Fechar emoji picker ao clicar fora
const handleOutsideEmojiClick = (event) => {
  if (!showEmojiPicker.value) return
  const picker = emojiPickerRef.value
  const toggleBtn = emojiToggleBtnRef.value
  if (!picker?.contains(event.target) && !toggleBtn?.contains(event.target)) {
    showEmojiPicker.value = false
  }
}

// Carregar ao montar
onMounted(async () => {
  document.addEventListener('mousedown', handleOutsideEmojiClick)
  pageLoading.value = true
  try {
    await loadChannels()
    await Promise.all([
      loadContactStats(),
      loadFieldStats(),
    ])
    await loadContacts({ reset: true })
  } finally {
    pageLoading.value = false
  }
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleOutsideEmojiClick)
})

watch(activeTab, async (tab) => {
  const c = selectedContact.value
  if (!c) return
  if (tab === 'messages' && lastLoadedMessagesFor.value !== c.id) {
    await loadMessagesForContact(c.id)
  }
  if (tab === 'history' && lastLoadedHistoryFor.value !== c.id) {
    await loadHistoryForContact(c.id)
  }
})

let searchDebounce = null
watch(searchQuery, () => {
  if (searchDebounce) window.clearTimeout(searchDebounce)
  searchDebounce = window.setTimeout(() => {
    pageOffset.value = 0
    loadContacts({ reset: true })
  }, 350)
})

let fieldFiltersDebounce = null
watch(
  () => JSON.stringify(normalizedFieldConditions.value),
  () => {
    if (fieldFiltersDebounce) window.clearTimeout(fieldFiltersDebounce)
    fieldFiltersDebounce = window.setTimeout(() => {
      pageOffset.value = 0
      loadContacts({ reset: true })
    }, 350)
  }
)

watch(selectedChannelId, () => {
  pageOffset.value = 0
  loadContacts({ reset: true })
})

watch(selectedTags, () => {
  pageOffset.value = 0
  loadContacts({ reset: true })
}, { deep: true })

// Computeds
const hasActiveFilters = computed(() => {
  return selectedChannelId.value !== null || selectedTags.value.length > 0 || normalizedFieldConditions.value.length > 0
})

const isAllSelected = computed(() => {
  return filteredContacts.value.length > 0 && selectedContacts.value.length === filteredContacts.value.length
})

const filteredContacts = computed(() => {
  // Agora os filtros principais são server-side.
  // Mantemos esse computed como um "alias" para a tabela.
  let filtered = contacts.value
  return filtered
})

const chatQuickList = computed(() => {
  const q = cqlSearch.value.toLowerCase()
  const list = q
    ? contacts.value.filter(c =>
        c.name.toLowerCase().includes(q) || (c.username || '').toLowerCase().includes(q)
      )
    : contacts.value.slice()
  return list.sort((a, b) => {
    const ta = quickContactLastMsg.value.get(a.id)?.rawTime ?? new Date(a.created_at || 0)
    const tb = quickContactLastMsg.value.get(b.id)?.rawTime ?? new Date(b.created_at || 0)
    return tb - ta
  })
})

const totalPages = computed(() => {
  const total = Number(totalContacts.value || 0)
  const size = Number(pageLimit.value || 50)
  if (size <= 0) return 1
  return Math.max(1, Math.ceil(total / size))
})

const currentPage = computed(() => {
  const size = Number(pageLimit.value || 50)
  if (size <= 0) return 1
  return Math.floor(Number(pageOffset.value || 0) / size) + 1
})

const goPrevPage = async () => {
  if (currentPage.value <= 1) return
  pageOffset.value = Math.max(0, pageOffset.value - pageLimit.value)
  await loadContacts({ reset: true })
}

const goNextPage = async () => {
  if (currentPage.value >= totalPages.value) return
  pageOffset.value = pageOffset.value + pageLimit.value
  await loadContacts({ reset: true })
}

const onChangePageSize = async () => {
  pageOffset.value = 0
  await loadContacts({ reset: true })
}

// Funções de filtros
const selectChannel = (channelId) => {
  selectedChannelId.value = channelId
  selectedContacts.value = [] // Limpar seleção ao mudar filtro
}

const getChannelContactCount = (channelId) => {
  const rows = contactStats.value.by_channel || []
  const row = rows.find(r => r.channel_id === channelId)
  return row ? row.count : 0
}

const getChannelIcon = (type) => {
  const icons = {
    telegram: 'fa-brands fa-telegram'
  }
  return icons[type] || 'fa-solid fa-circle-question'
}

const toggleTag = (tagName) => {
  const index = selectedTags.value.indexOf(tagName)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  } else {
    selectedTags.value.push(tagName)
  }
}

const clearFilters = () => {
  selectedChannelId.value = null
  selectedTags.value = []
  selectedFieldFilters.value = []
  fieldDraft.value = ''
  valueDraft.value = ''
  searchQuery.value = ''
}

// Funções de seleção
const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedContacts.value = []
  } else {
    selectedContacts.value = filteredContacts.value.map(c => c.id)
  }
}

const toggleSelectContact = (contactId) => {
  const index = selectedContacts.value.indexOf(contactId)
  if (index > -1) {
    selectedContacts.value.splice(index, 1)
  } else {
    selectedContacts.value.push(contactId)
  }
}

// Ações em massa
const bulkAddTag = () => {
  if (selectedContacts.value.length === 0) return
  const tag = prompt('Digite o nome da tag:')
  if (!tag) return

  const trimmed = String(tag).trim()
  if (!trimmed) return

  const ids = [...selectedContacts.value]
  if (ids.length > 150) {
    const ok = window.confirm(`Aplicar a tag em ${ids.length} contatos? Isso pode demorar.`)
    if (!ok) return
  }

  toast.info(`Adicionando tag "${trimmed}" a ${ids.length} contato(s)...`)
  ;(async () => {
    for (const id of ids) {
      try {
        await addContactTag(id, trimmed)
      } catch (e) {
        // continua para os demais
      }
    }
    selectedContacts.value = []
    await loadContactStats()
    await loadContacts({ reset: true })
    toast.success('Tag aplicada nos contatos selecionados!')
  })()
}

const bulkStartSequence = () => {
  if (selectedContacts.value.length === 0) return
  toast.info(`Iniciando sequência para ${selectedContacts.value.length} contato(s)...`)
  // TODO: implementar no backend
  selectedContacts.value = []
}

const bulkExport = () => {
  if (selectedContacts.value.length === 0) return
  exportContacts(true)
}

const bulkDelete = async () => {
  if (selectedContacts.value.length === 0) return
  
  try {
    await confirmDialog.showConfirm({
      title: 'Excluir contatos',
      message: `Tem certeza que deseja excluir ${selectedContacts.value.length} contato(s)? Esta ação não poderá ser desfeita.`,
      confirmText: 'Excluir',
      cancelText: 'Cancelar',
      type: 'danger'
    })
  } catch {
    return // Usuário cancelou
  }
  
  toast.info(`Excluindo ${selectedContacts.value.length} contato(s)...`)

  const ids = [...selectedContacts.value]
  const previousTotal = Number(totalContacts.value || 0)

  let deletedCount = 0
  for (const id of ids) {
    try {
      await deleteContactAPI(id)
      deletedCount += 1
    } catch (e) {
      // continua
    }
  }

  selectedContacts.value = []

  const afterTotal = Math.max(0, previousTotal - deletedCount)
  const pageSize = Number(pageLimit.value || 50)
  const maxOffset = afterTotal <= 0 ? 0 : Math.floor((afterTotal - 1) / pageSize) * pageSize
  pageOffset.value = Math.min(Number(pageOffset.value || 0), maxOffset)

  await Promise.all([
    loadContactStats(),
    loadContacts({ reset: true }),
  ])

  if (deletedCount > 0) {
    toast.success(`${deletedCount} contato(s) excluído(s)!`)
  } else {
    toast.error('Não foi possível excluir os contatos selecionados')
  }
}

// Exportação
const exportContacts = (onlySelected = false) => {
  const contactsToExport = onlySelected 
    ? contacts.value.filter(c => selectedContacts.value.includes(c.id))
    : filteredContacts.value
  
  if (contactsToExport.length === 0) {
    toast.error('Nenhum contato para exportar')
    return
  }
  
  // Criar CSV
  const headers = ['Nome', 'Username', 'Canal', 'Tags', 'Status', 'Inscrito']
  const rows = contactsToExport.map(c => [
    c.name,
    c.username,
    c.channel,
    c.tags.join('; '),
    c.status,
    c.lastEventTime
  ])
  
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n')
  
  // Download
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `contatos_${new Date().toISOString().split('T')[0]}.csv`
  link.click()
  
  toast.success(`${contactsToExport.length} contato(s) exportado(s)!`)
}

// Modal de contato
const viewContact = async (contactId) => {
  const cached = contacts.value.find(c => c.id === contactId)
  selectedContact.value = cached || null
  try {
    const fresh = await getContact(contactId)
    const mapped = mapContactFromBackend(fresh)
    selectedContact.value = mapped

    // manter lista em sync
    const idx = contacts.value.findIndex(c => c.id === contactId)
    if (idx > -1) contacts.value[idx] = mapped
  } catch (e) {
    // fallback: mantém cached
  }
  if (!selectedContact.value) return

  activeTab.value = 'messages'
  messages.value = []
  flowHistory.value = []
  lastLoadedMessagesFor.value = null
  lastLoadedHistoryFor.value = null
}

const closeContactView = () => {
  selectedContact.value = null
  messages.value = []
  flowHistory.value = []
  activeTab.value = 'info'
}

const switchToContact = async (contactId) => {
  if (selectedContact.value?.id !== contactId) {
    await viewContact(contactId)
  }
  activeTab.value = 'messages'
  if (lastLoadedMessagesFor.value !== contactId) {
    await loadMessagesForContact(contactId)
  }
}

const editContact = (id) => {
  toast.info('Funcionalidade em desenvolvimento')
}

// Modal de campos (sistema + personalizados)
const showFieldsModal = ref(false)
const contactToShowFields = ref(null)

const openFieldsModal = (contact) => {
  contactToShowFields.value = contact
  showFieldsModal.value = true
}

const closeFieldsModal = () => {
  showFieldsModal.value = false
  contactToShowFields.value = null
}

const formatFieldValueForModal = (value) => {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'string') return value.trim() ? value : '—'
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)

  if (Array.isArray(value)) {
    if (value.length === 0) return '—'
    const allPrimitive = value.every(v => ['string', 'number', 'boolean'].includes(typeof v) || v === null || v === undefined)
    if (allPrimitive) return value.map(v => (v === null || v === undefined ? '—' : String(v))).join(', ')
    try {
      return JSON.stringify(value)
    } catch {
      return String(value)
    }
  }

  try {
    return JSON.stringify(value)
  } catch {
    return String(value)
  }
}

const systemFieldsForModal = computed(() => {
  const c = contactToShowFields.value
  if (!c) return []

  const items = [
    { key: 'id', label: 'ID', value: c.id },
    { key: 'name', label: 'Nome', value: c.name },
    { key: 'username', label: 'Username', value: c.username },
    { key: 'channel', label: 'Canal', value: c.channel },
    { key: 'default_channel_id', label: 'Channel ID', value: c.default_channel_id },
    { key: 'created_at', label: 'Criado em', value: c.created_at },
    { key: 'tags', label: 'Tags', value: (c.tags || []).length ? (c.tags || []).join(', ') : '—' },
  ]

  return items.map(i => ({
    ...i,
    value: formatFieldValueForModal(i.value),
  }))
})

const customFieldsForModal = computed(() => {
  const c = contactToShowFields.value
  const fields = c?.customFields && typeof c.customFields === 'object' ? c.customFields : {}
  const keys = Object.keys(fields).sort((a, b) => a.localeCompare(b))
  return keys.map(key => ({
    key,
    value: formatFieldValueForModal(fields[key]),
  }))
})

// Modal de enviar fluxo
const showSendFlowModal = ref(false)
const contactToSendFlow = ref(null)
const selectedFlowToSend = ref('')
const sendingFlow = ref(false)
const availableFlows = ref([])

const openSendFlowModal = async (contact) => {
  contactToSendFlow.value = contact
  showSendFlowModal.value = true
  
  // Carregar fluxos disponíveis e histórico
  try {
    const { listFlows, listFlowSteps } = await import('@/api/flows')
    const { getContactFlowHistory } = await import('@/api/contacts')
    
    // Buscar fluxos e histórico em paralelo
    const [flows, flowHistory] = await Promise.all([
      listFlows(),
      getContactFlowHistory(contact.id)
    ])
    
    const activeFlows = flows.filter(f => f.is_active)
    
    // Criar mapa de fluxos já executados
    const executedFlowsMap = {}
    flowHistory.forEach(h => {
      executedFlowsMap[h.flow_id] = {
        count: h.execution_count,
        last_execution: h.last_execution
      }
    })
    
    // Carregar steps de cada fluxo e marcar os já executados
    const flowsWithSteps = await Promise.all(
      activeFlows.map(async (flow) => {
        try {
          const steps = await listFlowSteps(flow.id)
          const executionInfo = executedFlowsMap[flow.id]
          
          return {
            ...flow,
            steps_count: steps.length,
            system: flow.trigger_config?.system || 'telegram',
            already_sent: !!executionInfo,
            execution_count: executionInfo?.count || 0,
            last_execution: executionInfo?.last_execution || null
          }
        } catch (err) {
          return {
            ...flow,
            steps_count: 0,
            system: flow.trigger_config?.system || 'telegram',
            already_sent: false,
            execution_count: 0,
            last_execution: null
          }
        }
      })
    )
    
    availableFlows.value = flowsWithSteps
  } catch (error) {
    console.error('Erro ao carregar fluxos:', error)
    toast.error('Erro ao carregar fluxos')
  }
}

const closeSendFlowModal = () => {
  showSendFlowModal.value = false
  contactToSendFlow.value = null
  selectedFlowToSend.value = ''
}

const sendFlowToContact = async () => {
  if (!selectedFlowToSend.value) {
    toast.error('Selecione um fluxo')
    return
  }
  
  sendingFlow.value = true
  
  try {
    const { startFlowForContact } = await import('@/api/contacts')
    const result = await startFlowForContact(contactToSendFlow.value.id, selectedFlowToSend.value)
    
    toast.success(`Fluxo "${result.flow_name}" enviado para ${result.contact_name}!`)
    closeSendFlowModal()
  } catch (error) {
    console.error('Erro ao enviar fluxo:', error)
    
    // Extrair mensagem de erro do backend
    let errorMessage = 'Erro ao enviar fluxo'
    if (error.response && error.response.data && error.response.data.detail) {
      errorMessage = error.response.data.detail
    } else if (error.message) {
      errorMessage = error.message
    }
    
    toast.error(errorMessage)
  } finally {
    sendingFlow.value = false
  }
}

// Modal de deletar contato
const showDeleteModal = ref(false)
const contactToDelete = ref(null)
const deleting = ref(false)

const openDeleteModal = (contact) => {
  contactToDelete.value = contact
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  contactToDelete.value = null
}

const deleteContact = async () => {
  if (!contactToDelete.value) return
  
  deleting.value = true
  
  try {
    const idToDelete = contactToDelete.value.id
    const nameToDelete = contactToDelete.value.name

    await deleteContactAPI(idToDelete)

    // Se o contato estava aberto no modal, fechar
    if (selectedContact.value?.id === idToDelete) {
      closeContactView()
    }

    closeDeleteModal()

    // Ajustar paginação: se deletou o último item da página, voltar uma página
    const previousTotal = Number(totalContacts.value || 0)
    const afterTotal = Math.max(0, previousTotal - 1)
    const pageSize = Number(pageLimit.value || 50)
    const maxOffset = afterTotal <= 0 ? 0 : Math.floor((afterTotal - 1) / pageSize) * pageSize
    pageOffset.value = Math.min(Number(pageOffset.value || 0), maxOffset)

    await Promise.all([
      loadContacts({ reset: true }),
      loadContactStats(),
    ])

    toast.success(`Contato ${nameToDelete} excluído com sucesso!`)
  } catch (error) {
    console.error('Erro ao deletar contato:', error)
    const msg = error?.response?.data?.detail || 'Erro ao deletar contato'
    toast.error(msg)
  } finally {
    deleting.value = false
  }
}

// Formatar data do último envio
const formatLastExecution = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'agora'
  if (diffMins < 60) return `${diffMins} min atrás`
  if (diffHours < 24) return `${diffHours}h atrás`
  if (diffDays < 7) return `${diffDays}d atrás`
  
  return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
}

// Gerenciar tags do contato
const addTagToContact = () => {
  if (!newTag.value.trim()) return
  if (!selectedContact.value) return

  const tag = newTag.value.trim()
  newTag.value = ''

  addContactTag(selectedContact.value.id, tag)
    .then((updated) => {
      const mapped = mapContactFromBackend(updated)
      selectedContact.value = mapped
      const idx = contacts.value.findIndex(c => c.id === mapped.id)
      if (idx > -1) contacts.value[idx] = mapped
      toast.success('Tag adicionada!')
      loadContactStats()
    })
    .catch((err) => {
      console.error('Erro ao adicionar tag:', err)
      toast.error('Erro ao adicionar tag')
    })
}

const removeTagFromContact = (contactId, tagName) => {
  if (!selectedContact.value) return

  removeContactTag(contactId, tagName)
    .then((updated) => {
      const mapped = mapContactFromBackend(updated)
      selectedContact.value = mapped
      const idx = contacts.value.findIndex(c => c.id === mapped.id)
      if (idx > -1) contacts.value[idx] = mapped
      toast.success('Tag removida!')
      loadContactStats()
    })
    .catch((err) => {
      console.error('Erro ao remover tag:', err)
      toast.error('Erro ao remover tag')
    })
}

const formatMessageTime = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}
// ── Segmentos ────────────────────────────────
const SEGMENTS_KEY = 'bc_contact_segments'
const savedSegments = ref(JSON.parse(localStorage.getItem(SEGMENTS_KEY) || '[]'))
const segmentNameDraft = ref('')
const showSegmentInput = ref(false)

const saveSegment = () => {
  const name = segmentNameDraft.value.trim()
  if (!name) return
  const parts = []
  if (selectedTags.value.length) parts.push('tags:' + selectedTags.value.join(','))
  if (selectedFieldFilters.value.length) parts.push(selectedFieldFilters.value.map(f => f.field + ':' + f.value).join(' '))
  const seg = {
    name,
    description: parts.join(' · ') || name,
    channelId: selectedChannelId.value,
    tags: [...selectedTags.value],
    fieldFilters: [...selectedFieldFilters.value],
  }
  const updated = [...savedSegments.value, seg]
  savedSegments.value = updated
  localStorage.setItem(SEGMENTS_KEY, JSON.stringify(updated))
  segmentNameDraft.value = ''
  showSegmentInput.value = false
  toast.success('Segmento "' + name + '" salvo!')
}

const applySegment = (seg) => {
  selectedChannelId.value = seg.channelId ?? null
  selectedTags.value = [...(seg.tags || [])]
  selectedFieldFilters.value = [...(seg.fieldFilters || [])]
  pageOffset.value = 0
  loadContacts({ reset: true })
  toast.info('Segmento "' + seg.name + '" aplicado.')
}

const deleteSegment = (idx) => {
  const updated = savedSegments.value.filter((_, i) => i !== idx)
  savedSegments.value = updated
  localStorage.setItem(SEGMENTS_KEY, JSON.stringify(updated))
}
</script>

<style scoped>
.ct-page-loading {
  width: 100%;
  margin-top: 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  justify-content: center;
  gap: 12px;
  min-height: 180px;
}

.ct-page-loading-title {
  font-weight: 700;
  color: var(--text);
}

.ct-page-loading-subtitle {
  margin-top: 4px;
  font-size: 13px;
  color: var(--muted);
}

/* ═══════════════════════════════════════════
   CONTACTS VIEW — Complete Redesign
   ─────────────────────────────────────────── */

/* ── Page wrapper ── */
.ct-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  gap: 0;
}

/* ── Page Header ── */
.ct-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  gap: 12px;
}

.ct-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.ct-header-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(0, 255, 102, 0.1);
  border: 1px solid rgba(0, 255, 102, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
  font-size: 16px;
  flex-shrink: 0;
}

.ct-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: -0.2px;
}

.ct-subtitle {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 2px 0 0;
}

.ct-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ct-search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.ct-search-icon {
  position: absolute;
  left: 10px;
  color: var(--text-muted);
  font-size: 12px;
  pointer-events: none;
}

.ct-search-input {
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 7px 32px 7px 30px;
  color: var(--text-primary);
  font-size: 0.84rem;
  min-width: 240px;
  transition: border-color 0.2s;
  outline: none;
}

.ct-search-input:focus {
  border-color: var(--primary);
}

.ct-search-input::placeholder {
  color: var(--text-muted);
}

.ct-search-clear {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 12px;
  padding: 2px;
  transition: color 0.2s;
}

.ct-search-clear:hover { color: var(--text-primary); }

.ct-stat-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(0, 255, 102, 0.08);
  border: 1px solid rgba(0, 255, 102, 0.18);
  border-radius: 20px;
  color: var(--primary);
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
}

/* ── Buttons ── */
.ct-btn-secondary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.ct-btn-secondary:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-color: rgba(255,255,255,0.2);
}

.ct-btn-danger {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  color: #ef4444;
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.ct-btn-danger:hover {
  background: rgba(239, 68, 68, 0.2);
}

.ct-btn-ghost {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  border-radius: 6px;
  transition: all 0.15s;
}

.ct-btn-ghost:hover { background: var(--bg-tertiary); color: var(--text-primary); }

.ct-btn-accent-sm {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: var(--primary);
  color: #000;
  border: none;
  border-radius: 7px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.ct-btn-accent-sm:hover { background: var(--primary-hover); }
.ct-btn-accent-sm:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── 3-Column Body ── */
.ct-body {
  display: flex;
  flex: 1;
  overflow: hidden;
  gap: 0;
}

/* ══════════════════════════════════════
   COL 1 — FILTERS SIDEBAR
══════════════════════════════════════ */
.ct-col-filters {
  width: 252px;
  min-width: 252px;
  flex-shrink: 0;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  overflow-y: auto;
  padding: 14px 0 20px;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.ct-col-filters::-webkit-scrollbar { width: 4px; }
.ct-col-filters::-webkit-scrollbar-track { background: transparent; }
.ct-col-filters::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

/* Active chips */
.ct-active-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  padding: 10px 14px 6px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 4px;
}

.ct-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 6px 3px 8px;
  background: rgba(0, 255, 102, 0.08);
  border: 1px solid rgba(0, 255, 102, 0.2);
  border-radius: 20px;
  color: var(--primary);
  font-size: 0.74rem;
  font-weight: 500;
}

.ct-chip button {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--primary);
  display: flex;
  align-items: center;
  padding: 0;
  opacity: 0.7;
  transition: opacity 0.15s;
  font-size: 10px;
}

.ct-chip button:hover { opacity: 1; }

.ct-chip--field {
  background: rgba(139, 92, 246, 0.08);
  border-color: rgba(139, 92, 246, 0.2);
  color: #a78bfa;
}

.ct-chip--field button { color: #a78bfa; }

.ct-chip-clear {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 20px;
  color: #f87171;
  font-size: 0.74rem;
  cursor: pointer;
  transition: all 0.15s;
}

.ct-chip-clear:hover { background: rgba(239, 68, 68, 0.15); }

/* Filter groups */
.ct-filter-group {
  border-bottom: 1px solid var(--border);
}

.ct-filter-group:last-child {
  border-bottom: none;
}

.ct-fgroup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 10px 14px;
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
}

.ct-fgroup-header:hover { background: rgba(255,255,255,0.03); }

.ct-fgroup-header--static {
  cursor: default;
}

.ct-fgroup-header--static:hover { background: none; }

.ct-fgroup-title {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.ct-fgroup-title i { font-size: 11px; }

.ct-fgroup-title--canais {
  color: #4ade80;
}
.ct-fgroup-title--canais i {
  color: #00FF66;
  filter: drop-shadow(0 0 4px rgba(0, 255, 102, 0.4));
}

.ct-fgroup-title--tags {
  color: #f59e0b;
}
.ct-fgroup-title--tags i {
  color: #fbbf24;
  filter: drop-shadow(0 0 4px rgba(251, 191, 36, 0.4));
}

.ct-fgroup-title--campos {
  color: #a78bfa;
}
.ct-fgroup-title--campos i {
  color: #c084fc;
  filter: drop-shadow(0 0 4px rgba(192, 132, 252, 0.4));
}

.ct-fgroup-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: var(--primary);
  color: #000;
  border-radius: 9px;
  font-size: 0.65rem;
  font-weight: 700;
}

.ct-fgroup-arrow {
  color: var(--text-muted);
  font-size: 10px;
}

.ct-filter-list {
  padding: 2px 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.ct-filter-empty {
  padding: 8px 14px;
  color: var(--text-muted);
  font-size: 0.78rem;
  font-style: italic;
}

.ct-fi {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 7px 10px;
  background: none;
  border: none;
  border-radius: 7px;
  cursor: pointer;
  transition: background 0.15s;
  text-align: left;
}

.ct-fi:hover { background: var(--bg-tertiary); }

.ct-fi.active {
  background: rgba(0, 255, 102, 0.08);
}

.ct-fi-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.ct-fi.active .ct-fi-name { color: var(--primary); }

.ct-fi-count {
  font-size: 0.72rem;
  color: var(--text-muted);
  background: var(--bg-tertiary);
  border-radius: 10px;
  padding: 1px 6px;
  margin-left: 6px;
  flex-shrink: 0;
}

.ct-fi.active .ct-fi-count {
  background: rgba(0, 255, 102, 0.12);
  color: var(--primary);
}

/* Fields builder */
.ct-fields-body {
  padding: 6px 10px 10px;
}

.ct-field-builder {
  display: flex;
  gap: 5px;
  margin-bottom: 8px;
}

.ct-select,
.ct-input {
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 6px 8px;
  color: var(--text-primary);
  font-size: 0.78rem;
  outline: none;
  transition: border-color 0.2s;
  min-width: 0;
}

.ct-select { flex: 1.2; }
.ct-input { flex: 1.5; }

.ct-select:focus,
.ct-input:focus { border-color: var(--primary); }

.ct-field-add-btn {
  width: 30px;
  height: 30px;
  flex-shrink: 0;
  background: rgba(0, 255, 102, 0.1);
  border: 1px solid rgba(0, 255, 102, 0.2);
  border-radius: 7px;
  color: var(--primary);
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.ct-field-add-btn:hover { background: rgba(0, 255, 102, 0.2); }

.ct-field-chips {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.ct-field-chip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5px 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 7px;
  font-size: 0.76rem;
  color: var(--text-secondary);
}

.ct-field-chip button {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 11px;
  padding: 0;
  transition: color 0.15s;
}

.ct-field-chip button:hover { color: #f87171; }

/* ── Segments section ── */
.ct-segments-group {
  margin-top: auto;
  border-top: 1px solid var(--border);
  border-bottom: none;
}

.ct-segments-body {
  padding: 6px 12px 14px;
}

.ct-segment-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 16px 8px;
  gap: 4px;
}

.ct-segment-empty-icon {
  font-size: 22px;
  opacity: 0.2;
  margin-bottom: 4px;
}

.ct-segment-empty p {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin: 0;
}

.ct-segment-hint {
  font-size: 0.73rem !important;
  color: var(--text-muted) !important;
  opacity: 0.7;
  line-height: 1.4;
}

.ct-segment-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
}

.ct-segment-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.ct-segment-apply {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 10px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 7px;
  color: var(--text-secondary);
  font-size: 0.8rem;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ct-segment-apply:hover {
  border-color: rgba(0, 255, 102, 0.3);
  color: var(--primary);
  background: rgba(0, 255, 102, 0.06);
}

.ct-segment-apply i { font-size: 11px; color: var(--primary); flex-shrink: 0; }

.ct-segment-del {
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  border-radius: 5px;
  transition: all 0.15s;
  font-size: 11px;
  flex-shrink: 0;
}

.ct-segment-del:hover { background: rgba(239, 68, 68, 0.12); color: #f87171; }

.ct-segment-save-trigger {
  margin-top: 4px;
}

.ct-segment-save-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 7px 10px;
  background: rgba(0, 255, 102, 0.06);
  border: 1px dashed rgba(0, 255, 102, 0.25);
  border-radius: 7px;
  color: var(--primary);
  font-size: 0.78rem;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.ct-segment-save-btn:hover {
  background: rgba(0, 255, 102, 0.12);
  border-color: rgba(0, 255, 102, 0.4);
}

.ct-segment-save-form {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 4px;
}

.ct-segment-save-form .ct-input {
  width: 100%;
}

.ct-segment-save-actions {
  display: flex;
  gap: 6px;
  justify-content: flex-end;
}

/* ══════════════════════════════════════
   COL 2 — CONTACT LIST
══════════════════════════════════════ */
.ct-col-list {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-primary, #000);
}

/* Bulk actions */
.ct-bulk-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: rgba(0, 255, 102, 0.05);
  border-bottom: 1px solid rgba(0, 255, 102, 0.15);
  flex-shrink: 0;
  gap: 12px;
}

.ct-bulk-info {
  font-size: 0.84rem;
  color: var(--text-secondary);
}

.ct-bulk-info strong { color: var(--primary); }

.ct-bulk-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Skeletons */
.ct-skeletons {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  flex: 1;
}

.ct-skeleton-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 4px;
}

.ct-sk {
  background: linear-gradient(90deg, var(--bg-tertiary) 25%, rgba(255,255,255,0.04) 50%, var(--bg-tertiary) 75%);
  background-size: 200% 100%;
  animation: ct-shimmer 1.6s infinite;
  border-radius: 6px;
  height: 14px;
  flex-shrink: 0;
}

@keyframes ct-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.ct-sk--cb { width: 18px; height: 18px; border-radius: 4px; }
.ct-sk--avatar { width: 36px; height: 36px; border-radius: 50%; }
.ct-sk--name { flex: 1; max-width: 160px; height: 12px; }
.ct-sk--badge { width: 60px; height: 20px; border-radius: 10px; }
.ct-sk--tags { flex: 1; max-width: 120px; }
.ct-sk--time { width: 70px; }

/* Empty */
.ct-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-muted);
}

.ct-empty-icon {
  font-size: 48px;
  opacity: 0.15;
}

.ct-empty p {
  font-size: 0.95rem;
  margin: 0;
}

/* Table */
.ct-table-wrap {
  flex: 1;
  overflow-y: auto;
}

.ct-table-wrap::-webkit-scrollbar { width: 5px; }
.ct-table-wrap::-webkit-scrollbar-track { background: transparent; }
.ct-table-wrap::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

.ct-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.84rem;
}

.ct-table thead {
  position: sticky;
  top: 0;
  z-index: 2;
  background: var(--bg-secondary);
}

.ct-table thead th {
  padding: 10px 14px;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--text-muted);
  text-align: left;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}

.ct-th-check { width: 40px; }
.ct-th-actions { width: 130px; }

.ct-row {
  cursor: pointer;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  transition: background 0.12s;
}

.ct-row:hover { background: rgba(255,255,255,0.03); }
.ct-row.selected { background: rgba(0, 255, 102, 0.04); }
.ct-row.row-active { background: rgba(0, 255, 102, 0.06) !important; }

.ct-row td {
  padding: 11px 14px;
  vertical-align: middle;
}

.ct-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: var(--primary);
}

/* Contact cell */
.ct-contact-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ct-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  font-weight: 700;
  flex-shrink: 0;
  letter-spacing: 0;
}

.ct-avatar--lg {
  width: 44px;
  height: 44px;
  font-size: 0.9rem;
  border-radius: 12px;
}

.ct-contact-name {
  font-size: 0.84rem;
  font-weight: 500;
  color: var(--text-primary);
  max-width: 160px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ct-contact-sub {
  font-size: 0.74rem;
  color: var(--text-muted);
  margin-top: 1px;
}

/* Badge */
.ct-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.72rem;
  font-weight: 500;
  white-space: nowrap;
}

.badge-success { background: rgba(0,255,102,0.1); color: var(--primary); }
.badge-muted { background: rgba(255,255,255,0.07); color: var(--text-muted); }
.badge-warning { background: rgba(251,191,36,0.1); color: #fbbf24; }

/* Tags */
.ct-tag-pill {
  display: inline-block;
  padding: 2px 7px;
  background: rgba(139,92,246,0.1);
  border: 1px solid rgba(139,92,246,0.2);
  border-radius: 10px;
  font-size: 0.7rem;
  color: #a78bfa;
  margin-right: 3px;
}

.ct-muted { color: var(--text-muted); }

/* Actions */
.ct-actions-cell {
  display: flex;
  align-items: center;
  gap: 4px;
}

.ct-action-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 7px;
  border: 1px solid transparent;
  background: none;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.15s;
  color: var(--text-muted);
}

.ct-action-btn:hover { border-color: var(--border); background: var(--bg-tertiary); }

.ct-action-btn--view:hover { color: var(--primary); border-color: rgba(0,255,102,0.3); }
.ct-action-btn--fields:hover { color: #60a5fa; border-color: rgba(96,165,250,0.3); }
.ct-action-btn--send:hover { color: #a78bfa; border-color: rgba(167,139,250,0.3); }
.ct-action-btn--del:hover { color: #f87171; border-color: rgba(248,113,113,0.3); background: rgba(239,68,68,0.08); }

/* Pagination */
.ct-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border);
  flex-shrink: 0;
}

.ct-pg-meta {
  font-size: 0.8rem;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
}

.ct-pg-meta strong { color: var(--text-secondary); }

.ct-pg-sep { opacity: 0.3; }

.ct-pg-controls {
  display: flex;
  align-items: center;
  gap: 6px;
}

.ct-pg-select {
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 5px 8px;
  color: var(--text-secondary);
  font-size: 0.78rem;
  cursor: pointer;
  outline: none;
}

.ct-pg-btn {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 7px;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 11px;
  transition: all 0.15s;
}

.ct-pg-btn:hover:not(:disabled) { border-color: rgba(255,255,255,0.2); color: var(--text-primary); }
.ct-pg-btn:disabled { opacity: 0.35; cursor: not-allowed; }

/* ══════════════════════════════════════
   COL 3 — CONTACT DETAIL PANEL
══════════════════════════════════════ */
.ct-detail-resizer {
  position: absolute;
  top: 0;
  left: 0;
  width: 6px;
  height: 100%;
  cursor: col-resize;
  z-index: 10;
  background: transparent;
  transition: background 0.15s;
}

.ct-detail-resizer:hover,
.ct-detail-resizer:active {
  background: rgba(0, 255, 102, 0.25);
}

.ct-col-detail {
  position: relative;
  width: 380px;
  min-width: 380px;
  flex-shrink: 0;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Detail header */
.ct-detail-header {
  padding: 16px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  flex-shrink: 0;
  background: var(--bg-secondary);
}

.ct-detail-contact {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.ct-detail-info {
  flex: 1;
  min-width: 0;
}

.ct-detail-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ct-detail-sub {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 0;
}

.ct-detail-close {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  border-radius: 7px;
  transition: all 0.15s;
  font-size: 13px;
  flex-shrink: 0;
}

.ct-detail-close:hover { background: var(--bg-tertiary); color: var(--text-primary); }

/* Detail tabs */
.ct-detail-tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  background: var(--bg-secondary);
}

.ct-detail-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 10px 4px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-muted);
  font-size: 0.76rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.ct-detail-tab:hover { color: var(--text-primary); }
.ct-detail-tab.active { color: var(--primary); border-bottom-color: var(--primary); }

/* Detail content */
.ct-detail-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.ct-detail-content::-webkit-scrollbar { width: 4px; }
.ct-detail-content::-webkit-scrollbar-track { background: transparent; }
.ct-detail-content::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

.ct-detail-empty {
  color: var(--text-muted);
  font-size: 0.82rem;
  font-style: italic;
}

/* Info grid */
.ct-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}

.ct-info-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.ct-info-item label {
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--text-muted);
}

.ct-info-item span {
  font-size: 0.83rem;
  color: var(--text-primary);
}

.ct-info-section-title {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--text-muted);
  margin: 16px 0 10px;
  padding-top: 14px;
  border-top: 1px solid var(--border);
}

/* Tags tab */
.ct-tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
}

.ct-tag-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  background: rgba(139,92,246,0.1);
  border: 1px solid rgba(139,92,246,0.25);
  border-radius: 20px;
  font-size: 0.8rem;
  color: #a78bfa;
}

.ct-tag-badge button {
  background: none;
  border: none;
  cursor: pointer;
  color: rgba(167,139,250,0.6);
  font-size: 10px;
  padding: 0;
  display: flex;
  align-items: center;
  transition: color 0.15s;
}

.ct-tag-badge button:hover { color: #f87171; }

.ct-add-tag {
  display: flex;
  gap: 8px;
  border-top: 1px solid var(--border);
  padding-top: 14px;
  margin-top: 4px;
}

.ct-add-tag .ct-input { flex: 1; }

/* Messages tab layout */
.ct-messages-wrap {
  display: flex !important;
  flex-direction: row !important;
  padding: 0 !important;
  gap: 0 !important;
  overflow: hidden;
  height: 100%;
}

/* History tab */
.ct-history {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.ct-history-item {
  display: flex;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}

.ct-history-item:last-child { border-bottom: none; }

.ct-history-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--border);
  flex-shrink: 0;
  margin-top: 4px;
}

.ct-history-dot--green { background: var(--primary); }

.ct-history-title {
  font-size: 0.83rem;
  color: var(--text-primary);
  font-weight: 500;
}

.ct-history-time {
  font-size: 0.74rem;
  color: var(--text-muted);
  margin-top: 2px;
}

/* ══════════════════════════════════════
   CHAT AREA (reused from original)
══════════════════════════════════════ */
.cql-panel {
  width: 200px;
  min-width: 200px;
  flex-shrink: 0;
  border-right: 1px solid rgba(255,255,255,0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #0d0d0d;
}

.cql-header {
  padding: 10px 12px;
  font-size: 0.7rem;
  font-weight: 700;
  color: #4ade80;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.cql-search-wrap {
  padding: 8px 10px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
}

.cql-search {
  width: 100%;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  padding: 6px 9px;
  color: var(--text-primary);
  font-size: 0.75rem;
  outline: none;
  transition: border-color 0.15s;
}

.cql-search:focus {
  border-color: rgba(0, 255, 102, 0.35);
}

.cql-items {
  flex: 1;
  overflow-y: auto;
}

.cql-items::-webkit-scrollbar { width: 3px; }
.cql-items::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

.cql-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 12px;
  width: 100%;
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background 0.12s;
  border-bottom: 1px solid rgba(255,255,255,0.03);
}

.cql-item:hover { background: rgba(255,255,255,0.04); }
.cql-active {
  background: rgba(0,255,102,0.08) !important;
  border-left: 2px solid #00FF66;
}

.cql-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6rem;
  font-weight: 700;
  flex-shrink: 0;
}

.cql-info {
  flex: 1;
  min-width: 0;
}

.cql-name {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cql-preview {
  font-size: 0.69rem;
  color: rgba(148, 163, 184, 0.6);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 1px;
}

.cql-time {
  font-size: 0.62rem;
  color: rgba(148, 163, 184, 0.45);
  white-space: nowrap;
  flex-shrink: 0;
  align-self: flex-start;
  margin-top: 1px;
}

.cql-empty {
  padding: 16px 8px;
  text-align: center;
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* ── Chat wrap ── */
.messages-chat-wrap {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tg-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-secondary);
  flex-shrink: 0;
  gap: 8px;
}

.tg-meta {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.tg-load-more {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.72rem;
  color: var(--text-muted);
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.15s;
  padding: 0;
}

.tg-load-more:hover { color: var(--text-primary); }

.tg-jump-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 50%;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s;
}

.tg-jump-btn:hover { color: var(--text-primary); }

.tg-scroller {
  flex: 1;
  overflow-y: auto;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  background: #080808;
}

.tg-scroller::-webkit-scrollbar { width: 4px; }
.tg-scroller::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }

.tg-loading,
.tg-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--text-muted);
  font-size: 0.82rem;
}

.tg-feed {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tg-day-pill {
  text-align: center;
  margin: 14px 0;
}

.tg-day-pill span {
  display: inline-block;
  padding: 4px 14px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  font-size: 0.68rem;
  color: rgba(148, 163, 184, 0.7);
  letter-spacing: 0.3px;
}

.tg-row {
  display: flex;
  align-items: flex-end;
  gap: 6px;
}

.tg-in { justify-content: flex-start; }
.tg-out { justify-content: flex-end; }

.tg-bubble {
  position: relative;
  max-width: 80%;
  padding: 9px 13px;
  border-radius: 14px;
  font-size: 0.84rem;
  line-height: 1.5;
  word-break: break-word;
  box-shadow: 0 1px 4px rgba(0,0,0,0.4);
}

/* Mensagem recebida (contato → bot) */
.tg-in .tg-bubble {
  background: #1e2430;
  color: #e2e8f0;
  border-radius: 4px 14px 14px 14px;
  border: 1px solid rgba(255,255,255,0.07);
}

/* Mensagem enviada (bot → contato) */
.tg-out .tg-bubble {
  background: rgba(0, 255, 102, 0.13);
  color: #e2e8f0;
  border-radius: 14px 4px 14px 14px;
  border: 1px solid rgba(0, 255, 102, 0.2);
}

.tg-footer {
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: flex-end;
  margin-top: 4px;
}

.tg-time {
  font-size: 0.63rem;
  color: rgba(148, 163, 184, 0.55);
}

.tg-ticks { display: flex; align-items: center; }

.tg-text { white-space: pre-wrap; word-break: break-word; }

.tg-fwd {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.7rem;
  color: rgba(148, 163, 184, 0.7);
  margin-bottom: 5px;
  border-left: 2px solid #4ade80;
  padding-left: 6px;
}

.tg-copy {
  position: absolute;
  top: 4px;
  right: 4px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 5px;
  padding: 3px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.15s;
  color: var(--text-muted);
  display: flex;
  align-items: center;
}

.tg-bubble:hover .tg-copy { opacity: 1; }

.tg-file {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tg-file-icon { color: var(--text-muted); }
.tg-file-name { font-size: 0.8rem; color: var(--text-primary); }
.tg-file-size { font-size: 0.7rem; color: var(--text-muted); margin-top: 2px; }

.tg-voice {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tg-voice-play {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(0,255,102,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: var(--primary);
}

.tg-waveform {
  display: flex;
  align-items: center;
  gap: 1px;
  height: 20px;
}

.tg-wave-bar {
  width: 2px;
  background: rgba(0,255,102,0.5);
  border-radius: 1px;
  height: calc(4px + var(--h, 0.5) * 14px);
}

.tg-voice-dur { font-size: 0.7rem; color: var(--text-muted); }

.tg-image-wrap img.tg-img {
  max-width: 100%;
  max-height: 160px;
  border-radius: 7px;
  display: block;
  cursor: pointer;
}

.tg-caption { font-size: 0.75rem; color: var(--text-muted); margin-top: 4px; }
.tg-audio { max-width: 100%; }
.tg-video { max-width: 100%; max-height: 140px; border-radius: 7px; }
.tg-media { display: flex; flex-direction: column; gap: 6px; }

/* Composer */
.tg-composer {
  border-top: 1px solid var(--border);
  background: var(--bg-secondary);
  flex-shrink: 0;
}

.tg-upload-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  font-size: 0.75rem;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border);
}

.tg-format-bar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 5px 8px 3px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}

.tg-fmt-btn {
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  border-radius: 5px;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 12px;
  transition: all 0.15s;
}

.tg-fmt-btn:hover, .tg-fmt-btn.active { background: var(--bg-tertiary); color: var(--text-primary); }
.tg-fmt-sep { width: 1px; height: 16px; background: var(--border); margin: 0 3px; }

.tg-input-row {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  padding: 6px 8px 8px;
}

.tg-textarea {
  flex: 1;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 7px 10px;
  color: var(--text-primary);
  font-size: 0.82rem;
  resize: none;
  outline: none;
  min-height: 34px;
  max-height: 100px;
  line-height: 1.4;
  font-family: inherit;
  transition: border-color 0.2s;
}

.tg-textarea:focus { border-color: var(--primary); }
.tg-textarea::placeholder { color: var(--text-muted); }

.tg-send-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #00FF66;
  border: none;
  border-radius: 10px;
  color: #000;
  cursor: pointer;
  transition: background 0.15s, box-shadow 0.15s, transform 0.1s;
  flex-shrink: 0;
  box-shadow: 0 0 10px rgba(0, 255, 102, 0.35);
}

.tg-send-btn:hover:not(:disabled) {
  background: #00e65c;
  box-shadow: 0 0 16px rgba(0, 255, 102, 0.55);
  transform: scale(1.06);
}

.tg-send-btn:disabled { opacity: 0.25; cursor: not-allowed; box-shadow: none; }

.tg-emoji-picker {
  position: absolute;
  bottom: 100%;
  left: 8px;
  width: 280px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  z-index: 100;
  filter: drop-shadow(0 8px 24px rgba(0,0,0,0.5));
}

.tg-emoji-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 15px;
  border-radius: 5px;
  transition: background 0.1s;
}

.tg-emoji-btn:hover { background: var(--bg-tertiary); }

@keyframes tg-spin { to { transform: rotate(360deg); } }
.tg-spinner { animation: tg-spin 1s linear infinite; }

/* ══════════════════════════════════════
   MODALS
══════════════════════════════════════ */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 16px;
  max-width: 540px;
  width: 90%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 24px 60px rgba(0,0,0,0.6);
}

.modal-header {
  padding: 20px 24px 16px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.modal-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.modal-subtitle {
  font-size: 0.82rem;
  color: var(--text-muted);
  margin: 4px 0 0;
}

.contact-name-badge {
  background: rgba(0,255,102,0.08);
  color: var(--primary);
  border-radius: 8px;
  padding: 2px 8px;
  font-size: 0.8rem;
  font-weight: 500;
}

.modal-body {
  padding: 0 24px 20px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.modal-description {
  font-size: 0.84rem;
  color: var(--text-secondary);
  margin: 0 0 16px;
}

.btn-close-modal {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  border-radius: 8px;
  transition: all 0.15s;
  flex-shrink: 0;
}

.btn-close-modal:hover { background: var(--bg-tertiary); color: var(--text-primary); }

/* Send flow modal */
.send-flow-modal { max-width: 640px; }

.flows-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px;
}

.flow-card {
  position: relative;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.flow-card:hover { border-color: rgba(255,255,255,0.2); }
.flow-card.selected { border-color: var(--primary); background: rgba(0,255,102,0.06); }
.flow-card.already-sent { opacity: 0.8; }

.flow-already-sent-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 7px;
  background: rgba(0,255,102,0.1);
  border: 1px solid rgba(0,255,102,0.2);
  border-radius: 8px;
  font-size: 0.68rem;
  color: var(--primary);
}

.flow-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.flow-card-icon {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  background: rgba(139,92,246,0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #a78bfa;
}

.flow-card-check {
  color: transparent;
  transition: color 0.15s;
}

.flow-card.selected .flow-card-check { color: var(--primary); }

.flow-card-title {
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px;
}

.flow-card-description {
  font-size: 0.74rem;
  color: var(--text-muted);
  margin: 0 0 6px;
  line-height: 1.35;
}

.flow-last-sent {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.71rem;
  color: var(--text-muted);
  margin: 0;
}

.flow-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
}

.flow-card-badge {
  padding: 2px 7px;
  border-radius: 10px;
  font-size: 0.68rem;
  font-weight: 500;
  background: rgba(255,255,255,0.07);
  color: var(--text-muted);
}

.flow-card-badge.badge-telegram { background: rgba(14,165,233,0.1); color: #38bdf8; }

.flow-card-meta {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.empty-state-flows {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
  gap: 10px;
  text-align: center;
  color: var(--text-muted);
}

.empty-state-flows .empty-icon { opacity: 0.2; }
.empty-state-flows h4 { margin: 0; font-size: 0.9rem; color: var(--text-secondary); }
.empty-state-flows p { margin: 0; font-size: 0.8rem; }

/* Delete modal */
.delete-contact-modal { max-width: 400px; }

.delete-icon-warning {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: rgba(239,68,68,0.1);
  color: #ef4444;
  margin-bottom: 8px;
}

.delete-warning-text {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0 0 14px;
}

.delete-contact-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 10px;
  margin-bottom: 14px;
}

.contact-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
}

.delete-warning-box {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 12px;
  background: rgba(239,68,68,0.06);
  border: 1px solid rgba(239,68,68,0.15);
  border-radius: 10px;
  font-size: 0.82rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.delete-warning-box svg { color: #f87171; flex-shrink: 0; margin-top: 2px; }

/* Fields modal */
.fields-modal { max-width: 480px; }

.fields-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.fields-section-title {
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--text-muted);
  margin: 0 0 10px;
}

.fields-grid {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.field-row {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  gap: 12px;
}

.field-row:last-child { border-bottom: none; }

.field-key {
  width: 130px;
  flex-shrink: 0;
  font-size: 0.78rem;
  color: var(--text-muted);
  font-weight: 500;
}

.field-value {
  flex: 1;
  font-size: 0.82rem;
  color: var(--text-primary);
  word-break: break-word;
}

.fields-empty {
  font-size: 0.82rem;
  color: var(--text-muted);
  padding: 8px 0;
}

/* Generic buttons for modals */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 18px;
  border-radius: 9px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.btn-primary {
  background: var(--primary);
  color: #000;
  border-color: var(--primary);
}

.btn-primary:hover { background: var(--primary-hover); border-color: var(--primary-hover); }
.btn-primary:disabled { opacity: 0.45; cursor: not-allowed; }

.btn-secondary {
  background: transparent;
  color: var(--text-secondary);
  border-color: var(--border);
}

.btn-secondary:hover { background: var(--bg-tertiary); color: var(--text-primary); }

.btn-danger {
  background: rgba(239,68,68,0.1);
  color: #ef4444;
  border-color: rgba(239,68,68,0.3);
}

.btn-danger:hover { background: rgba(239,68,68,0.2); }
.btn-danger:disabled { opacity: 0.45; cursor: not-allowed; }

/* ══════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════ */
@media (max-width: 1100px) {
  .ct-col-filters { width: 220px; min-width: 220px; }
}

@media (max-width: 900px) {
  .ct-body {
    flex-direction: column;
    overflow: auto;
  }

  .ct-col-filters {
    width: 100%;
    min-width: unset;
    max-height: 240px;
    border-right: none;
    border-bottom: 1px solid var(--border);
    flex-direction: row;
    flex-wrap: wrap;
    overflow-x: auto;
  }

  .ct-col-detail {
    width: 100%;
    min-width: unset;
    border-left: none;
    border-top: 1px solid var(--border);
    max-height: 60vh;
  }
}

</style>
