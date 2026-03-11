import { ref } from 'vue'

const isVisible = ref(false)
const title = ref('')
const message = ref('')
const confirmText = ref('Confirmar')
const cancelText = ref('Cancelar')
const type = ref('warning')
const resolvePromise = ref(null)
const rejectPromise = ref(null)

export function useConfirmDialog() {
  const showConfirm = (options = {}) => {
    return new Promise((resolve, reject) => {
      title.value = options.title || 'Confirmar ação'
      message.value = options.message || 'Deseja continuar?'
      confirmText.value = options.confirmText || 'Confirmar'
      cancelText.value = options.cancelText || 'Cancelar'
      type.value = options.type || 'warning'
      
      resolvePromise.value = resolve
      rejectPromise.value = reject
      
      isVisible.value = true
    })
  }

  const handleConfirm = () => {
    if (resolvePromise.value) {
      resolvePromise.value(true)
      resolvePromise.value = null
    }
    isVisible.value = false
  }

  const handleCancel = () => {
    if (rejectPromise.value) {
      rejectPromise.value(false)
      rejectPromise.value = null
    }
    isVisible.value = false
  }

  return {
    isVisible,
    title,
    message,
    confirmText,
    cancelText,
    type,
    showConfirm,
    handleConfirm,
    handleCancel
  }
}
