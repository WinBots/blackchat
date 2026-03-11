<template>
  <transition name="toast">
    <div v-if="visible" :class="['toast', `toast-${type}`]">
      <div class="toast-icon">
        <i v-if="type === 'success'" class="fa-solid fa-circle-check"></i>
        <i v-else-if="type === 'error'" class="fa-solid fa-circle-exclamation"></i>
        <i v-else-if="type === 'warning'" class="fa-solid fa-triangle-exclamation"></i>
        <i v-else class="fa-solid fa-circle-info"></i>
      </div>
      <div class="toast-content">
        <div class="toast-title" v-if="title">{{ title }}</div>
        <div class="toast-message">{{ message }}</div>
      </div>
      <button class="toast-close" @click="close">
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'info', // success, error, warning, info
    validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
  },
  title: {
    type: String,
    default: ''
  },
  message: {
    type: String,
    required: true
  },
  duration: {
    type: Number,
    default: 3000
  }
})

const emit = defineEmits(['close'])

const visible = ref(false)
let timeout = null

onMounted(() => {
  visible.value = true
  
  if (props.duration > 0) {
    timeout = setTimeout(() => {
      close()
    }, props.duration)
  }
})

const close = () => {
  visible.value = false
  if (timeout) clearTimeout(timeout)
  setTimeout(() => {
    emit('close')
  }, 300) // Aguarda animação
}
</script>

<style scoped>
.toast {
  position: fixed;
  top: 24px;
  right: 24px;
  min-width: 300px;
  max-width: 420px;
  background: #1e293b;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(148, 163, 184, 0.1);
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  z-index: 10000;
  border-left: 4px solid currentColor;
}

.toast-success {
  color: #22c55e;
  background: linear-gradient(135deg, #1e293b 0%, #1a2f2a 100%);
}

.toast-error {
  color: #ef4444;
  background: linear-gradient(135deg, #1e293b 0%, #2d1f1f 100%);
}

.toast-warning {
  color: #f59e0b;
  background: linear-gradient(135deg, #1e293b 0%, #2d2717 100%);
}

.toast-info {
  color: #3b82f6;
  background: linear-gradient(135deg, #1e293b 0%, #1e2838 100%);
}

.toast-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  margin-top: 2px;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-weight: 600;
  font-size: 0.9375rem;
  color: #f1f5f9;
  margin-bottom: 4px;
}

.toast-message {
  font-size: 0.875rem;
  color: #cbd5e1;
  line-height: 1.4;
}

.toast-close {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.toast-close:hover {
  background: rgba(148, 163, 184, 0.1);
  color: #cbd5e1;
}

/* Animações */
.toast-enter-active {
  animation: toast-in 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.toast-leave-active {
  animation: toast-out 0.3s ease-in;
}

@keyframes toast-in {
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes toast-out {
  from {
    transform: translateX(0) scale(1);
    opacity: 1;
  }
  to {
    transform: translateX(400px) scale(0.9);
    opacity: 0;
  }
}
</style>

