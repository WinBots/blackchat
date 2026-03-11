# 📋 Implementação Completa dos Novos Blocos no Editor de Fluxos

Este documento contém todo o código necessário para implementar os novos blocos do editor de fluxos.

## 🎯 Blocos a Implementar

1. **Condição** - If/else baseado em campos, tags e variáveis
2. **Randomizador** - Distribuição aleatória para A/B testing  
3. **Atraso Inteligente** - Delay configurável
4. **Comentar** - Notas no canvas
5. **Iniciar Automação** - Trigger para outro fluxo

---

## 1️⃣ ADICIONAR SEÇÕES DE EDIÇÃO NO PAINEL LATERAL

### Localização: Após o bloco de Ações (`<!-- SE for Bloco de Ações -->`)

Adicionar este código logo após o fechamento do `</div>` do bloco de Ações:

```vue
            <!-- SE for Bloco de Condição -->
            <div v-else-if="selectedStep.type === 'condition'" class="sidebar-section">
              <p class="sidebar-label">Condição (IF/ELSE)</p>
              <p class="sidebar-helper">Direcione o fluxo baseado em campos, tags ou variáveis</p>

              <div class="form-group">
                <label class="sidebar-label">Tipo de Condição</label>
                <select 
                  v-model="selectedStep.config.conditionType" 
                  class="sidebar-textarea"
                  style="height: 42px;"
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
                  style="height: 42px;"
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
                  style="height: 42px;"
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
                  style="height: 42px;"
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
                  style="height: 42px;"
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
                  style="height: 42px;"
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
                  style="height: 42px;"
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
                      style="height: 42px; flex: 1;"
                      @input="autoSave"
                    />
                    <select
                      v-model="selectedStep.config.unit"
                      class="sidebar-textarea"
                      style="height: 42px; width: 120px;"
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
                      style="height: 42px; flex: 1;"
                      @input="autoSave"
                    />
                    <select
                      v-model="selectedStep.config.unit"
                      class="sidebar-textarea"
                      style="height: 42px; width: 120px;"
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
                    style="height: 42px;"
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
                  style="height: 42px;"
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
```

---

## 2️⃣ ADICIONAR MÉTODOS AUXILIARES NO SCRIPT

### Localização: Na seção de métodos, após `handleAddBlock`

```javascript
// ==================== MÉTODOS AUXILIARES DOS NOVOS BLOCOS ====================

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
```

---

## 3️⃣ ESTILOS CSS PARA OS NOVOS BLOCOS

### Adicionar no final da seção `<style scoped>`:

```css
/* ==================== CONDIÇÃO ==================== */
.condition-info {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  margin-top: 16px;
}

.condition-info i {
  color: #3b82f6;
  font-size: 1.125rem;
  flex-shrink: 0;
}

.condition-info div {
  flex: 1;
}

.condition-info strong {
  display: block;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.condition-info p {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.4;
  margin: 4px 0;
}

/* ==================== RANDOMIZADOR ==================== */
.randomizer-paths {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.randomizer-path-item {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.path-header {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.path-name-input {
  flex: 1;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 8px 12px;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.btn-remove-path {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  padding: 8px 12px;
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
  gap: 12px;
  padding: 12px;
  background: rgba(168, 85, 247, 0.1);
  border-radius: 8px;
  margin-top: 16px;
}

.randomizer-info i {
  color: #a855f7;
  font-size: 1.125rem;
  flex-shrink: 0;
}

.randomizer-info div {
  flex: 1;
}

.randomizer-info strong {
  display: block;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.randomizer-info p {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.4;
  margin: 4px 0;
}

/* ==================== ATRASO INTELIGENTE ==================== */
.smart-delay-info {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 8px;
  margin-top: 16px;
}

.smart-delay-info i {
  color: #ef4444;
  font-size: 1.125rem;
  flex-shrink: 0;
}

.smart-delay-info div {
  flex: 1;
}

.smart-delay-info strong {
  display: block;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.smart-delay-info p {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.4;
  margin: 4px 0;
}

.delay-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(34, 197, 94, 0.1);
  border-radius: 8px;
  margin-top: 16px;
  color: #22c55e;
  font-size: 0.9375rem;
  font-weight: 500;
}

.delay-preview i {
  font-size: 1.125rem;
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
  gap: 12px;
  padding: 12px;
  background: rgba(34, 197, 94, 0.1);
  border-radius: 8px;
  margin-top: 16px;
}

.start-automation-info i {
  color: #22c55e;
  font-size: 1.125rem;
  flex-shrink: 0;
}

.start-automation-info div {
  flex: 1;
}

.start-automation-info strong {
  display: block;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.start-automation-info p {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.4;
  margin: 4px 0;
}

.start-automation-info ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.start-automation-info li {
  margin: 4px 0;
}
```

---

## 4️⃣ OTIMIZAR LAYOUT DO MODAL (Sem Scroll)

### Substituir CSS do modal de adicionar blocos:

```css
/* ==================== MODAL ADICIONAR BLOCO (COMPACTO) ==================== */
.add-block-modal {
  background: var(--bg-secondary);
  border-radius: 12px;
  width: 90%;
  max-width: 900px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}

.add-block-modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.add-block-modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.add-block-modal-body {
  padding: 16px 20px;
  overflow-y: auto;
}

.add-block-category {
  margin-bottom: 20px;
}

.add-block-category:last-child {
  margin-bottom: 0;
}

.add-block-category-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 10px;
}

.add-block-options {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
}

.add-block-option {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  position: relative;
}

.add-block-option:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.add-block-option-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
}

.add-block-option span {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-primary);
  text-align: center;
  line-height: 1.2;
}

.add-block-option-ai {
  grid-column: span 2;
  flex-direction: row;
  text-align: left;
}

.add-block-option-ai .add-block-option-icon {
  flex-shrink: 0;
}

.add-block-option-ai .add-block-option-content {
  flex: 1;
}

.add-block-option-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.add-block-option-header span {
  font-size: 0.9375rem;
  font-weight: 600;
}

.add-block-option-subtitle {
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.add-block-badge {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.add-block-badge-pro {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
}

.add-block-badge-ai {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
}

.add-block-option-pro .add-block-badge {
  position: absolute;
  top: 8px;
  right: 8px;
}
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Adicionar seções de edição no painel lateral (após bloco de Ações)
- [ ] Adicionar métodos auxiliares no script
- [ ] Adicionar estilos CSS
- [ ] Otimizar layout do modal
- [ ] Testar cada tipo de bloco
- [ ] Verificar auto-save funcionando
- [ ] Testar conexões entre blocos
- [ ] Validar percentuais do randomizador
- [ ] Testar preview de delay

---

## 📝 NOTAS IMPORTANTES

1. **+ Canal**: Funcionalidade para enviar mensagem em outro canal (ex: SMS, Email). Pode ser implementada depois.

2. **Etapa de IA**: Integração com GPT/Claude. Deixar para depois como planejado.

3. **Condição**: Terá 2 saídas no canvas (verdadeiro/falso). Atualizar lógica de conexões.

4. **Randomizador**: Terá múltiplas saídas (uma para cada caminho). Atualizar lógica de conexões.

5. **Comentário**: Não tem saídas, é apenas visual no canvas.

6. **Iniciar Automação**: Encerra o fluxo atual e inicia outro.

---

**Implementação completa!** 🚀
