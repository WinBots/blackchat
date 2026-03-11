<template>
  <div class="audio-upload">
    <!-- Preview do Áudio -->
    <div v-if="audioUrl" class="audio-preview">
      <div class="audio-preview-content">
        <div class="audio-icon-wrapper">
          <i class="fa-solid fa-music"></i>
        </div>
        <div class="audio-info">
          <div class="audio-title">{{ audioTitle || 'Áudio' }}</div>
          <div class="audio-meta">
            <span v-if="fileSize">{{ fileSize }}</span>
            <span v-if="duration" class="audio-duration">
              <i class="fa-solid fa-clock"></i>
              {{ formatDuration(duration) }}
            </span>
          </div>
          <audio 
            ref="audioPlayer" 
            :src="audioUrl" 
            controls 
            class="audio-player"
            @loadedmetadata="handleMetadata"
          ></audio>
        </div>
        <button class="btn-remove-audio" @click="removeAudio" type="button">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
    </div>

    <!-- Botão de Upload -->
    <div v-else class="upload-area">
      <input
        ref="fileInput"
        type="file"
        accept="audio/mpeg,audio/mp3,audio/ogg,audio/wav,audio/m4a,audio/opus"
        @change="handleFileSelect"
        style="display: none"
      />
      <button class="btn-upload" @click="triggerFileInput" type="button" :disabled="uploading">
        <i class="fa-solid fa-cloud-arrow-up"></i>
        <span v-if="!uploading">{{ label }}</span>
        <span v-else class="uploading-text">
          <span class="spinner"></span>
          Enviando...
        </span>
      </button>
      <p class="upload-hint">MP3, OGG, WAV, M4A ou OPUS (máx 50MB)</p>
    </div>

    <!-- Erro -->
    <div v-if="error" class="upload-error">
      <i class="fa-solid fa-triangle-exclamation"></i>
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { uploadAudio, getAudioUrl, formatFileSize } from '@/api/media'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: 'Fazer Upload de Áudio'
  },
  title: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'update:title'])

const fileInput = ref(null)
const audioPlayer = ref(null)
const audioUrl = ref('')
const uploading = ref(false)
const error = ref('')
const fileSize = ref('')
const duration = ref(0)

// Inicializar preview se já houver URL
onMounted(() => {
  if (props.modelValue) {
    audioUrl.value = getAudioUrl(props.modelValue)
  }
})

// Atualizar preview quando o modelValue mudar externamente
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    audioUrl.value = getAudioUrl(newVal)
  } else {
    audioUrl.value = ''
    fileSize.value = ''
    duration.value = 0
  }
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleMetadata = () => {
  if (audioPlayer.value) {
    duration.value = audioPlayer.value.duration
  }
}

const handleFileSelect = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  // Validar tipo de arquivo
  const validTypes = ['audio/mpeg', 'audio/mp3', 'audio/ogg', 'audio/wav', 'audio/m4a', 'audio/opus', 'audio/x-m4a']
  const validExtensions = ['.mp3', '.ogg', '.wav', '.m4a', '.opus']
  const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
  
  if (!validTypes.includes(file.type) && !validExtensions.includes(fileExtension)) {
    error.value = 'Tipo de arquivo inválido. Use MP3, OGG, WAV, M4A ou OPUS.'
    return
  }

  // Validar tamanho (50MB)
  if (file.size > 50 * 1024 * 1024) {
    error.value = 'Arquivo muito grande. Máximo: 50MB'
    return
  }

  error.value = ''
  uploading.value = true
  fileSize.value = formatFileSize(file.size)

  try {
    console.log('📤 Fazendo upload do áudio...', file.name)
    
    // Fazer upload
    const result = await uploadAudio(file)
    
    console.log('✅ Upload concluído:', result)
    
    // Atualizar URL com URL completa
    const fullUrl = getAudioUrl(result.url)
    audioUrl.value = fullUrl
    
    // Emitir URL completa para o v-model
    emit('update:modelValue', fullUrl)
    
    // Se não houver título, usar o nome do arquivo (sem extensão)
    if (!props.title) {
      const fileNameWithoutExt = file.name.replace(/\.[^/.]+$/, '')
      emit('update:title', fileNameWithoutExt)
    }
    
  } catch (err) {
    console.error('❌ Erro no upload:', err)
    error.value = err.response?.data?.detail || 'Erro ao fazer upload do áudio'
    fileSize.value = ''
  } finally {
    uploading.value = false
    // Limpar input para permitir selecionar o mesmo arquivo novamente
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

const removeAudio = () => {
  audioUrl.value = ''
  fileSize.value = ''
  duration.value = 0
  emit('update:modelValue', '')
  emit('update:title', '')
  error.value = ''
}

const formatDuration = (seconds) => {
  if (!seconds || isNaN(seconds)) return ''
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const audioTitle = computed(() => {
  return props.title || 'Áudio'
})
</script>

<style scoped>
.audio-upload {
  width: 100%;
}

.audio-preview {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  padding: 16px;
}

.audio-preview-content {
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
}

.audio-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  flex-shrink: 0;
}

.audio-info {
  flex: 1;
  min-width: 0;
}

.audio-title {
  font-weight: 600;
  font-size: 0.9375rem;
  color: var(--text-primary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.audio-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.75rem;
  color: var(--muted);
  margin-bottom: 8px;
}

.audio-duration {
  display: flex;
  align-items: center;
  gap: 4px;
}

.audio-player {
  width: 100%;
  height: 32px;
  margin-top: 8px;
}

.audio-player::-webkit-media-controls-panel {
  background-color: var(--bg-primary);
}

.btn-remove-audio {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  flex-shrink: 0;
}

.btn-remove-audio:hover {
  background: rgba(220, 38, 38, 0.9);
}

.upload-area {
  text-align: center;
  padding: 32px 24px;
  border: 2px dashed var(--border);
  border-radius: 8px;
  background: var(--bg-secondary);
  transition: all 0.2s;
}

.upload-area:hover {
  border-color: var(--accent);
  background: var(--bg-hover);
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

.uploading-text {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.upload-hint {
  margin-top: 12px;
  font-size: 0.75rem;
  color: var(--muted);
}

.upload-error {
  margin-top: 12px;
  padding: 10px 12px;
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
  border-radius: 6px;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>