<template>
  <div class="image-upload">
    <!-- Preview da Imagem -->
    <div v-if="previewUrl" class="image-preview">
      <img :src="previewUrl" alt="Preview" />
      <button class="btn-remove-image" @click="removeImage" type="button">
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>

    <!-- Botão de Upload -->
    <div v-else class="upload-area">
      <input
        ref="fileInput"
        type="file"
        accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
        @change="handleFileSelect"
        style="display: none"
      />
      <button class="btn-upload" @click="triggerFileInput" type="button" :disabled="uploading">
        <i class="fa-solid fa-cloud-arrow-up"></i>
        <span v-if="!uploading">{{ label }}</span>
        <span v-else>Enviando...</span>
      </button>
      <p class="upload-hint">JPG, PNG, GIF ou WebP (máx 10MB)</p>
    </div>

    <!-- Erro -->
    <div v-if="error" class="upload-error">
      <i class="fa-solid fa-triangle-exclamation"></i>
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { uploadImage, getImageUrl } from '@/api/media'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: 'Fazer Upload de Imagem'
  }
})

const emit = defineEmits(['update:modelValue'])

const fileInput = ref(null)
const previewUrl = ref('')
const uploading = ref(false)
const error = ref('')

// Inicializar preview se já houver URL
onMounted(() => {
  if (props.modelValue) {
    previewUrl.value = getImageUrl(props.modelValue)
  }
})

// Atualizar preview quando o modelValue mudar externamente
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    previewUrl.value = getImageUrl(newVal)
  } else {
    previewUrl.value = ''
  }
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  // Validar tipo de arquivo
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
  if (!validTypes.includes(file.type)) {
    error.value = 'Tipo de arquivo inválido. Use JPG, PNG, GIF ou WebP.'
    return
  }

  // Validar tamanho (10MB)
  if (file.size > 10 * 1024 * 1024) {
    error.value = 'Arquivo muito grande. Máximo: 10MB'
    return
  }

  error.value = ''
  uploading.value = true

  try {
    console.log('📤 Fazendo upload da imagem...', file.name)
    
    // Fazer upload
    const result = await uploadImage(file)
    
    console.log('✅ Upload concluído:', result)
    
    // Atualizar preview com URL completa
    previewUrl.value = getImageUrl(result.url)
    
    // Emitir URL completa para o v-model
    emit('update:modelValue', getImageUrl(result.url))
    
  } catch (err) {
    console.error('❌ Erro no upload:', err)
    error.value = err.response?.data?.detail || 'Erro ao fazer upload da imagem'
  } finally {
    uploading.value = false
    // Limpar input para permitir selecionar o mesmo arquivo novamente
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

const removeImage = () => {
  previewUrl.value = ''
  emit('update:modelValue', '')
  error.value = ''
}
</script>

<style scoped>
.image-upload {
  width: 100%;
}

.image-preview {
  position: relative;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
}

.image-preview img {
  width: 100%;
  height: auto;
  display: block;
  max-height: 300px;
  object-fit: contain;
}

.btn-remove-image {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.btn-remove-image:hover {
  background: rgba(220, 38, 38, 0.9);
}

.upload-area {
  text-align: center;
  padding: 24px;
  border: 2px dashed var(--border);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.btn-upload {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-upload:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: translateY(-1px);
}

.btn-upload:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-upload i {
  font-size: 1.125rem;
}

.upload-hint {
  margin-top: 8px;
  font-size: 0.75rem;
  color: var(--muted);
}

.upload-error {
  margin-top: 8px;
  padding: 8px 12px;
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
  border-radius: 6px;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>

