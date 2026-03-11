<template>
  <div class="placeholder-input-wrapper">
    <!-- Input/Textarea -->
    <component
      :is="multiline ? 'textarea' : 'input'"
      ref="inputElement"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder"
      :class="inputClass"
      :style="inputStyle"
    />
    
    <!-- Dropdown de Variáveis -->
    <div class="placeholder-dropdown">
      <button 
        @click.stop="toggleDropdown"
        class="dropdown-trigger"
        type="button"
        :title="showDropdown ? 'Fechar variáveis' : 'Inserir variável'"
      >
        <i class="fa-solid fa-code"></i>
        Variáveis
        <i class="fa-solid" :class="showDropdown ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
      </button>
      
      <!-- Menu de opções -->
      <transition name="dropdown-fade">
        <div v-show="showDropdown" class="dropdown-menu" @click.stop>
          <div class="dropdown-header">
            <span>Clique para inserir na posição do cursor</span>
          </div>
          <div 
            v-for="ph in placeholders" 
            :key="ph.value"
            @click="insertPlaceholder(ph.value)"
            class="dropdown-item"
          >
            <div class="dropdown-item-main">
              <code class="placeholder-code">{{ ph.value }}</code>
              <i class="fa-solid fa-arrow-right"></i>
            </div>
            <span class="dropdown-description">{{ ph.description }}</span>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Digite ou use variáveis'
  },
  multiline: {
    type: Boolean,
    default: false
  },
  inputClass: {
    type: String,
    default: 'sidebar-textarea'
  },
  inputStyle: {
    type: String,
    default: ''
  },
  placeholders: {
    type: Array,
    default: () => [
      { value: '{primeiro_nome}', description: 'Primeiro nome do contato' },
      { value: '{sobrenome}', description: 'Sobrenome do contato' },
      { value: '{nome_completo}', description: 'Nome completo' },
      { value: '{username}', description: 'Username do Telegram' },
      { value: '{contact_id}', description: 'ID do contato' },
      { value: '{ultima_mensagem}', description: 'Última mensagem enviada' },
      { value: '{telegram_username}', description: 'Username do Telegram (@user)' }
    ]
  }
})

const emit = defineEmits(['update:modelValue'])

const inputElement = ref(null)
const showDropdown = ref(false)

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

const closeDropdown = (event) => {
  if (!event.target.closest('.placeholder-dropdown')) {
    showDropdown.value = false
  }
}

const insertPlaceholder = (placeholder) => {
  const element = inputElement.value
  const start = element.selectionStart || 0
  const end = element.selectionEnd || 0
  const text = props.modelValue || ''
  
  // Insere na posição do cursor
  const newValue = 
    text.substring(0, start) + 
    placeholder + 
    text.substring(end)
  
  emit('update:modelValue', newValue)
  
  // Reposiciona cursor após o placeholder
  nextTick(() => {
    element.focus()
    const newPos = start + placeholder.length
    element.setSelectionRange(newPos, newPos)
  })
  
  // Fecha o dropdown
  showDropdown.value = false
}

onMounted(() => {
  document.addEventListener('click', closeDropdown)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', closeDropdown)
})
</script>

<style scoped>
.placeholder-input-wrapper {
  position: relative;
  width: 100%;
}

.placeholder-dropdown {
  position: relative;
  margin-top: 8px;
}

.dropdown-trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 0.75rem;
  font-weight: 500;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 6px;
  color: rgba(96, 165, 250, 1);
  cursor: pointer;
  transition: all 0.2s;
}

.dropdown-trigger:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.5);
  transform: translateY(-1px);
}

.dropdown-trigger i:first-child {
  font-size: 0.875rem;
}

.dropdown-trigger i:last-child {
  font-size: 0.625rem;
  transition: transform 0.2s;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 320px;
  max-width: 400px;
  background: rgba(15, 23, 42, 0.98);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 10000;
  overflow: hidden;
}

.dropdown-header {
  padding: 10px 14px;
  background: rgba(59, 130, 246, 0.1);
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}

.dropdown-header span {
  font-size: 0.6875rem;
  color: rgba(148, 163, 184, 0.8);
  font-weight: 500;
}

.dropdown-item {
  padding: 10px 14px;
  cursor: pointer;
  transition: all 0.15s;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background: rgba(59, 130, 246, 0.15);
}

.dropdown-item-main {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.placeholder-code {
  background: rgba(59, 130, 246, 0.15);
  padding: 3px 8px;
  border-radius: 4px;
  color: rgba(96, 165, 250, 1);
  font-family: 'Courier New', monospace;
  font-size: 0.8125rem;
  font-weight: 600;
}

.dropdown-item-main i {
  font-size: 0.625rem;
  color: rgba(148, 163, 184, 0.5);
}

.dropdown-description {
  font-size: 0.75rem;
  color: rgba(148, 163, 184, 0.7);
  line-height: 1.4;
  display: block;
  padding-left: 2px;
}

/* Animação do dropdown */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: all 0.2s ease;
}

.dropdown-fade-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
