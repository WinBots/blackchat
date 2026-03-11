<template>
  <div class="video-upload">
    <!-- Preview do Vídeo -->
    <div v-if="videoUrl" class="video-preview">
      <div class="video-wrapper">
        <video 
          ref="videoPlayer" 
          :src="videoUrl" 
          class="video-player"
          @loadedmetadata="handleMetadata"
          @loadeddata="handleVideoLoaded"
        >
          Seu navegador não suporta o elemento de vídeo.
        </video>
        <div class="video-overlay" @click="togglePlay">
          <i :class="isPlaying ? 'fa-solid fa-pause' : 'fa-solid fa-play'" class="play-icon"></i>
        </div>
      </div>
      <div class="video-info">
        <div class="video-title-row">
          <div class="video-title">{{ videoTitle || 'Vídeo' }}</div>
          <button class="btn-remove-video" @click="removeVideo" type="button">
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>
        <div class="video-meta">
          <span v-if="fileSize" class="meta-item">
            <i class="fa-solid fa-file"></i>
            {{ fileSize }}
          </span>
          <span v-if="duration" class="meta-item">
            <i class="fa-solid fa-clock"></i>
            {{ formatDuration(duration) }}
          </span>
          <span v-if="videoDimensions" class="meta-item">
            <i class="fa-solid fa-expand"></i>
            {{ videoDimensions }}
          </span>
        </div>
      </div>
    </div>

    <!-- Botão de Upload -->
    <div v-else class="upload-area">
      <input
        ref="fileInput"
        type="file"
        accept="video/mp4,video/webm,video/ogg,video/quicktime,video/x-msvideo"
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
      <p class="upload-hint">MP4, WebM, OGG, MOV ou AVI (máx 100MB)</p>
      <div v-if="uploading && uploadProgress > 0" class="upload-progress">
        <div class="progress-bar" :style="{ width: uploadProgress + '%' }"></div>
      </div>
    </div>

    <!-- Erro -->
    <div v-if="error" class="upload-error">
      <i class="fa-solid fa-triangle-exclamation"></i>
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { uploadVideo, getVideoUrl, formatFileSize } from '@/api/media'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: 'Fazer Upload de Vídeo'
  },
  title: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'update:title'])

const fileInput = ref(null)
const videoPlayer = ref(null)
const videoUrl = ref('')
const uploading = ref(false)
const error = ref('')
const fileSize = ref('')
const duration = ref(0)
const videoDimensions = ref('')
const isPlaying = ref(false)
const uploadProgress = ref(0)

// Inicializar preview se já houver URL
onMounted(() => {
  if (props.modelValue) {
    videoUrl.value = getVideoUrl(props.modelValue)
  }
})

// Atualizar preview quando o modelValue mudar externamente
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    videoUrl.value = getVideoUrl(newVal)
  } else {
    videoUrl.value = ''
    fileSize.value = ''
    duration.value = 0
    videoDimensions.value = ''
  }
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleMetadata = () => {
  if (videoPlayer.value) {
    duration.value = videoPlayer.value.duration
    const width = videoPlayer.value.videoWidth
    const height = videoPlayer.value.videoHeight
    if (width && height) {
      videoDimensions.value = `${width}x${height}`
    }
  }
}

const handleVideoLoaded = () => {
  handleMetadata()
}

const togglePlay = () => {
  if (!videoPlayer.value) return
  
  if (isPlaying.value) {
    videoPlayer.value.pause()
  } else {
    videoPlayer.value.play()
  }
  isPlaying.value = !isPlaying.value
}

const handlePlay = () => {
  isPlaying.value = true
}

const handlePause = () => {
  isPlaying.value = false
}

const handleFileSelect = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  // Validar tipo de arquivo
  const validTypes = ['video/mp4', 'video/webm', 'video/ogg', 'video/quicktime', 'video/x-msvideo']
  const validExtensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi']
  const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
  
  if (!validTypes.includes(file.type) && !validExtensions.includes(fileExtension)) {
    error.value = 'Tipo de arquivo inválido. Use MP4, WebM, OGG, MOV ou AVI.'
    return
  }

  // Validar tamanho (100MB)
  if (file.size > 100 * 1024 * 1024) {
    error.value = 'Arquivo muito grande. Máximo: 100MB'
    return
  }

  error.value = ''
  uploading.value = true
  uploadProgress.value = 0
  fileSize.value = formatFileSize(file.size)

  try {
    console.log('📤 Fazendo upload do vídeo...', file.name)
    
    // Fazer upload (progress pode ser implementado com axios/interceptors se necessário)
    const result = await uploadVideo(file)
    
    console.log('✅ Upload concluído:', result)
    
    // Atualizar URL com URL completa
    const fullUrl = getVideoUrl(result.url)
    videoUrl.value = fullUrl
    
    // Emitir URL completa para o v-model
    emit('update:modelValue', fullUrl)
    
    // Se não houver título, usar o nome do arquivo (sem extensão)
    if (!props.title) {
      const fileNameWithoutExt = file.name.replace(/\.[^/.]+$/, '')
      emit('update:title', fileNameWithoutExt)
    }
    
    uploadProgress.value = 100
    
    // Aguardar um pouco para o vídeo carregar metadados
    setTimeout(() => {
      if (videoPlayer.value) {
        handleMetadata()
      }
    }, 500)
    
  } catch (err) {
    console.error('❌ Erro no upload:', err)
    error.value = err.response?.data?.detail || 'Erro ao fazer upload do vídeo'
    fileSize.value = ''
    uploadProgress.value = 0
  } finally {
    uploading.value = false
    // Limpar input para permitir selecionar o mesmo arquivo novamente
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

const removeVideo = () => {
  if (videoPlayer.value) {
    videoPlayer.value.pause()
    videoPlayer.value.src = ''
  }
  videoUrl.value = ''
  fileSize.value = ''
  duration.value = 0
  videoDimensions.value = ''
  isPlaying.value = false
  emit('update:modelValue', '')
  emit('update:title', '')
  error.value = ''
}

const formatDuration = (seconds) => {
  if (!seconds || isNaN(seconds)) return ''
  const hours = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const videoTitle = computed(() => {
  return props.title || 'Vídeo'
})

// Adicionar event listeners para o vídeo
watch(videoPlayer, (player) => {
  if (player) {
    player.addEventListener('play', handlePlay)
    player.addEventListener('pause', handlePause)
    player.addEventListener('ended', () => {
      isPlaying.value = false
    })
  }
})

onUnmounted(() => {
  if (videoPlayer.value) {
    videoPlayer.value.removeEventListener('play', handlePlay)
    videoPlayer.value.removeEventListener('pause', handlePause)
  }
})
</script>

<style scoped>
.video-upload {
  width: 100%;
}

.video-preview {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
}

.video-wrapper {
  position: relative;
  width: 100%;
  background: #000;
  aspect-ratio: 16/9;
  overflow: hidden;
}

.video-player {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: background 0.2s;
  opacity: 0;
}

.video-wrapper:hover .video-overlay {
  opacity: 1;
}

.play-icon {
  font-size: 48px;
  color: white;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
  transition: transform 0.2s;
}

.video-overlay:hover .play-icon {
  transform: scale(1.1);
}

.video-info {
  padding: 16px;
}

.video-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.video-title {
  font-weight: 600;
  font-size: 0.9375rem;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.btn-remove-video {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.btn-remove-video:hover {
  background: rgba(220, 38, 38, 0.2);
  transform: scale(1.1);
}

.video-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 0.75rem;
  color: var(--muted);
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-item i {
  font-size: 0.6875rem;
}

.upload-area {
  text-align: center;
  padding: 32px 24px;
  border: 2px dashed var(--border);
  border-radius: 8px;
  background: var(--bg-secondary);
  transition: all 0.2s;
  position: relative;
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

.upload-progress {
  margin-top: 16px;
  width: 100%;
  height: 4px;
  background: var(--bg-primary);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--accent) 0%, var(--accent-hover) 100%);
  transition: width 0.3s ease;
  border-radius: 2px;
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