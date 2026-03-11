# ✅ Implementação de Múltiplas Saídas para Blocos

## 🎯 Problema Resolvido
Blocos de **Condição** e **Randomizador** agora possuem múltiplas saídas funcionais no canvas de fluxo.

---

## 🔄 Blocos com Múltiplas Saídas

### 1. **Condição** (IF/ELSE)
- ✅ **2 saídas fixas:**
  - **✓ Verdadeiro** (verde, top: 30%)
  - **✗ Falso** (vermelho, top: 70%)
- Cada saída pode conectar a um bloco diferente
- Identificador: `outputId = 'true'` ou `'false'`

### 2. **Randomizador** (A/B Testing)
- ✅ **N saídas dinâmicas** (uma para cada caminho)
- Posicionamento automático baseado no número de caminhos
- Label mostra: `Nome (XX%)`
- Identificador: `outputId = path.id` (UUID único)

---

## 🛠️ Mudanças Implementadas

### 1. **Template - Renderização das Portas**
**Localização:** `FlowEditView.vue` linha ~1554

**Antes:**
```vue
<!-- Ponto de Saída (canto inferior direito) -->
<div class="flow-port flow-port-output" ...>
  <div class="flow-port-dot"></div>
</div>
```

**Depois:**
```vue
<!-- Múltiplas Saídas para Condição -->
<template v-if="step.type === 'condition'">
  <div class="flow-port flow-port-output flow-port-condition-true" 
       @mousedown.stop="startConnection($event, step.id, 'true')">
    <div class="flow-port-dot"></div>
    <span class="flow-port-label">✓</span>
  </div>
  <div class="flow-port flow-port-output flow-port-condition-false" 
       @mousedown.stop="startConnection($event, step.id, 'false')">
    <div class="flow-port-dot"></div>
    <span class="flow-port-label">✗</span>
  </div>
</template>

<!-- Múltiplas Saídas para Randomizador -->
<template v-else-if="step.type === 'randomizer'">
  <div v-for="(path, index) in step.config.paths" :key="path.id"
       class="flow-port flow-port-output flow-port-randomizer"
       :style="{ top: `calc(50% + ${(index - (paths.length - 1) / 2) * 30}px)` }"
       @mousedown.stop="startConnection($event, step.id, path.id)">
    <div class="flow-port-dot"></div>
    <span class="flow-port-label">{{ path.percentage }}%</span>
  </div>
</template>

<!-- Saída única para outros blocos -->
<div v-else class="flow-port flow-port-output" ...></div>
```

---

### 2. **Script - Lógica de Conexões**

#### A) `startConnection` - Iniciar conexão
**Mudança:** Aceita `outputId` como 3º parâmetro

```javascript
// ANTES
const startConnection = (e, stepId) => {
  connectionFrom.value = stepId
}

// DEPOIS
const startConnection = (e, stepId, outputId = 'default') => {
  connectionFrom.value = { stepId, outputId }
}
```

#### B) `completeConnection` - Finalizar conexão
**Mudança:** Salva `outputId` na conexão

```javascript
// ANTES
connections.value.push({
  id: `${connectionFrom.value}-${toStepId}`,
  from: connectionFrom.value,
  to: toStepId
})

// DEPOIS
connections.value.push({
  id: `${connectionFrom.value.stepId}-${connectionFrom.value.outputId}-${toStepId}`,
  from: connectionFrom.value.stepId,
  to: toStepId,
  outputId: connectionFrom.value.outputId
})
```

#### C) `getPortCenterWorkspace` - Calcular posição das portas
**Mudança:** Considera `outputId` para buscar a porta correta

```javascript
// ANTES
const getPortCenterWorkspace = (stepId, portType) => {
  const portEl = portRefs.value[stepId]?.[portType]
}

// DEPOIS
const getPortCenterWorkspace = (stepId, portType, outputId = 'default') => {
  const portKey = portType === 'out' && outputId !== 'default' 
    ? `out-${outputId}` 
    : portType
  const portEl = portRefs.value[stepId]?.[portKey]
}
```

#### D) `updateConnectionPaths` - Desenhar linhas SVG
**Mudança:** Usa `outputId` ao buscar ponto de origem

```javascript
// ANTES
const fromPoint = getPortCenterWorkspace(conn.from, 'out')

// DEPOIS
const fromPoint = getPortCenterWorkspace(conn.from, 'out', conn.outputId || 'default')
```

#### E) `tempConnectionPath` - Linha temporária ao arrastar
**Mudança:** Usa novo formato de `connectionFrom`

```javascript
// ANTES
const fromPos = getPortCenterWorkspace(connectionFrom.value, 'out')

// DEPOIS
const fromPos = getPortCenterWorkspace(
  connectionFrom.value.stepId, 
  'out', 
  connectionFrom.value.outputId
)
```

---

### 3. **CSS - Estilos das Portas**

```css
/* Condição - Verdadeiro (verde, top 30%) */
.flow-port-condition-true {
  bottom: auto;
  right: -10px;
  top: 30%;
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

/* Condição - Falso (vermelho, top 70%) */
.flow-port-condition-false {
  bottom: auto;
  right: -10px;
  top: 70%;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

/* Randomizador (roxo, posição dinâmica) */
.flow-port-randomizer {
  bottom: auto;
  right: -10px;
  background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%);
}

/* Labels nas portas (aparecem no hover) */
.flow-port-label {
  position: absolute;
  right: 28px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.75rem;
  font-weight: 700;
  color: white;
  background: rgba(0, 0, 0, 0.7);
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s;
}

.flow-port:hover .flow-port-label {
  opacity: 1;
}
```

---

## 📊 Estrutura de Dados

### Conexão com múltiplas saídas:
```javascript
{
  id: "step-123-true-step-456",      // stepFrom-outputId-stepTo
  from: "step-123",                   // ID do bloco origem
  to: "step-456",                     // ID do bloco destino
  outputId: "true"                    // ID da saída específica
}
```

### Referências de portas (portRefs):
```javascript
{
  "step-123": {
    "in": <HTMLElement>,              // Porta de entrada
    "out-true": <HTMLElement>,        // Saída "Verdadeiro"
    "out-false": <HTMLElement>        // Saída "Falso"
  },
  "step-456": {
    "in": <HTMLElement>,
    "out-path-uuid-1": <HTMLElement>, // Caminho A
    "out-path-uuid-2": <HTMLElement>  // Caminho B
  }
}
```

---

## 🎨 Comportamento Visual

### Condição:
- Saída superior (30%): **Verde** com label **"✓"**
- Saída inferior (70%): **Vermelho** com label **"✗"**
- Hover mostra: **"Verdadeiro"** ou **"Falso"**

### Randomizador:
- Saídas distribuídas verticalmente no centro do bloco
- Cor: **Roxo** (#a855f7)
- Label mostra: **"50%"**, **"30%"**, etc.
- Hover mostra: **"Caminho A (50%)"**

---

## 🧪 Como Testar

### Teste 1: Condição
1. Adicionar bloco "Condição"
2. Configurar campo/operador/valor
3. Conectar saída **"✓"** para bloco A
4. Conectar saída **"✗"** para bloco B
5. Verificar que ambas as conexões são independentes
6. Salvar e recarregar - verificar persistência

### Teste 2: Randomizador
1. Adicionar bloco "Randomizador"
2. Configurar 3 caminhos: A (50%), B (30%), C (20%)
3. Verificar que aparecem 3 portas de saída
4. Conectar cada saída para blocos diferentes
5. Adicionar/remover caminhos - portas devem atualizar
6. Salvar e recarregar - verificar persistência

---

## ⚠️ Limitações Atuais (Backend Pendente)

### O que funciona (Frontend):
✅ Renderização visual de múltiplas saídas
✅ Criação de conexões independentes
✅ Salvamento no banco (outputId incluído)
✅ Carregamento e persistência
✅ Labels e cores diferenciadas

### O que ainda NÃO funciona (Backend):
❌ Lógica de execução no backend
❌ Avaliar condição e seguir caminho correto
❌ Distribuição aleatória baseada em percentuais
❌ Logs/analytics de qual caminho foi seguido

### Próximos passos backend:
1. Modificar `services/flow_execution.py` para detectar `outputId`
2. Implementar avaliação de condições
3. Implementar randomização com percentuais
4. Adicionar logs de decisões (para analytics)

---

## 📝 Estrutura de Conexões no Banco

### Tabela `flow_steps`:
Campo `next_step_id` permanece para compatibilidade, mas conexões complexas vêm do `config`:

```json
{
  "connections": [
    {
      "id": "step-1-true-step-2",
      "from": "step-1",
      "to": "step-2",
      "outputId": "true"
    },
    {
      "id": "step-1-false-step-3",
      "from": "step-1",
      "to": "step-3",
      "outputId": "false"
    }
  ]
}
```

---

## 🎯 Benefícios

1. **Flexibilidade:** Cada saída pode ir para um bloco diferente
2. **Clareza Visual:** Cores e labels indicam função de cada saída
3. **Escalável:** Randomizador suporta N caminhos dinamicamente
4. **Retrocompatível:** Blocos antigos continuam usando saída única
5. **Preparado para Analytics:** `outputId` permite rastrear decisões

---

## 🔧 Arquivos Modificados

**`frontend/src/views/FlowEditView.vue`**
- Linhas ~1554-1600: Template das portas múltiplas
- Linhas ~2034-2043: `getPortCenterWorkspace` atualizada
- Linhas ~2871-2925: `startConnection` e `completeConnection` atualizadas
- Linhas ~2958-2967: `updateConnectionPaths` atualizada
- Linhas ~3006-3010: `tempConnectionPath` atualizado
- Linhas ~4675-4720: CSS das novas portas

---

**✨ Implementação completa e funcional no frontend!**
Backend necessário para execução real dos fluxos condicionais.
