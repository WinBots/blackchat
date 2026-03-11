<template>
  <Transition name="confirm-dialog">
    <div v-if="isVisible" class="confirm-dialog-overlay" @click.self="handleCancel">
      <div class="confirm-dialog-container">
        <div class="confirm-dialog-header">
          <div class="confirm-dialog-icon" :class="`confirm-dialog-icon-${type}`">
            <i :class="getIconClass()"></i>
          </div>
          <h3 class="confirm-dialog-title">{{ title }}</h3>
        </div>
        
        <div class="confirm-dialog-body">
          <p class="confirm-dialog-message">{{ message }}</p>
        </div>
        
        <div class="confirm-dialog-actions">
          <button 
            class="confirm-dialog-btn confirm-dialog-btn-cancel" 
            @click="handleCancel"
          >
            {{ cancelText }}
          </button>
          <button 
            class="confirm-dialog-btn confirm-dialog-btn-confirm" 
            :class="`confirm-dialog-btn-${type}`"
            @click="handleConfirm"
          >
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Confirmar ação'
  },
  message: {
    type: String,
    required: true
  },
  confirmText: {
    type: String,
    default: 'Confirmar'
  },
  cancelText: {
    type: String,
    default: 'Cancelar'
  },
  type: {
    type: String,
    default: 'warning', // warning, danger, info
    validator: (value) => ['warning', 'danger', 'info'].includes(value)
  }
})

const emit = defineEmits(['confirm', 'cancel', 'update:isVisible'])

const handleConfirm = () => {
  emit('confirm')
  emit('update:isVisible', false)
}

const handleCancel = () => {
  emit('cancel')
  emit('update:isVisible', false)
}

const getIconClass = () => {
  const iconMap = {
    warning: 'fas fa-exclamation-triangle',
    danger: 'fas fa-trash-alt',
    info: 'fas fa-info-circle'
  }
  return iconMap[props.type] || iconMap.warning
}

// Adiciona listener para ESC
watch(() => props.isVisible, (newValue) => {
  if (newValue) {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        handleCancel()
        document.removeEventListener('keydown', handleEscape)
      }
    }
    document.addEventListener('keydown', handleEscape)
  }
})
</script>

<style scoped>
.confirm-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.confirm-dialog-container {
  background: var(--bg-secondary, #1e293b);
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  max-width: 480px;
  width: 90%;
  overflow: hidden;
}

.confirm-dialog-header {
  padding: 24px 24px 16px;
  text-align: center;
}

.confirm-dialog-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  font-size: 28px;
}

.confirm-dialog-icon-warning {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05));
  color: #f59e0b;
}

.confirm-dialog-icon-danger {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.05));
  color: #ef4444;
}

.confirm-dialog-icon-info {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(59, 130, 246, 0.05));
  color: #3b82f6;
}

.confirm-dialog-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary, #f1f5f9);
  margin: 0;
}

.confirm-dialog-body {
  padding: 0 24px 24px;
  text-align: center;
}

.confirm-dialog-message {
  font-size: 0.9375rem;
  line-height: 1.5;
  color: var(--text-secondary, #cbd5e1);
  margin: 0;
}

.confirm-dialog-actions {
  display: flex;
  gap: 12px;
  padding: 16px 24px 24px;
  background: rgba(0, 0, 0, 0.2);
}

.confirm-dialog-btn {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}

.confirm-dialog-btn-cancel {
  background: rgba(148, 163, 184, 0.1);
  color: var(--text-secondary, #cbd5e1);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.confirm-dialog-btn-cancel:hover {
  background: rgba(148, 163, 184, 0.15);
  border-color: rgba(148, 163, 184, 0.3);
}

.confirm-dialog-btn-confirm {
  color: white;
  border: 1px solid transparent;
}

.confirm-dialog-btn-warning {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.confirm-dialog-btn-warning:hover {
  background: linear-gradient(135deg, #d97706, #b45309);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.confirm-dialog-btn-danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.confirm-dialog-btn-danger:hover {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.confirm-dialog-btn-info {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.confirm-dialog-btn-info:hover {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* Transições */
.confirm-dialog-enter-active,
.confirm-dialog-leave-active {
  transition: opacity 0.2s ease;
}

.confirm-dialog-enter-active .confirm-dialog-container,
.confirm-dialog-leave-active .confirm-dialog-container {
  transition: transform 0.2s ease;
}

.confirm-dialog-enter-from,
.confirm-dialog-leave-to {
  opacity: 0;
}

.confirm-dialog-enter-from .confirm-dialog-container {
  transform: scale(0.95) translateY(-20px);
}

.confirm-dialog-leave-to .confirm-dialog-container {
  transform: scale(0.95) translateY(20px);
}
</style>
