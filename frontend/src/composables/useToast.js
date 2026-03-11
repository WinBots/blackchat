import { ref, h, render } from 'vue'
import Toast from '@/components/Toast.vue'

const toasts = ref([])

export function useToast() {
  const show = (options) => {
    const {
      type = 'info',
      title = '',
      message = '',
      duration = 3000
    } = typeof options === 'string' ? { message: options } : options

    const id = Date.now() + Math.random()
    
    // Criar container se não existir
    let container = document.getElementById('toast-container')
    if (!container) {
      container = document.createElement('div')
      container.id = 'toast-container'
      container.style.cssText = 'position: fixed; top: 0; right: 0; z-index: 10000; display: flex; flex-direction: column; gap: 12px; padding: 24px;'
      document.body.appendChild(container)
    }

    // Criar elemento do toast
    const toastEl = document.createElement('div')
    container.appendChild(toastEl)

    // Renderizar componente
    const vnode = h(Toast, {
      type,
      title,
      message,
      duration,
      onClose: () => {
        render(null, toastEl)
        container.removeChild(toastEl)
        
        // Remover container se vazio
        if (container.children.length === 0) {
          document.body.removeChild(container)
        }
      }
    })

    render(vnode, toastEl)

    return id
  }

  const success = (message, title = 'Sucesso') => {
    return show({ type: 'success', title, message })
  }

  const error = (message, title = 'Erro') => {
    return show({ type: 'error', title, message })
  }

  const warning = (message, title = 'Atenção') => {
    return show({ type: 'warning', title, message })
  }

  const info = (message, title = '') => {
    return show({ type: 'info', title, message })
  }

  return {
    show,
    success,
    error,
    warning,
    info
  }
}

