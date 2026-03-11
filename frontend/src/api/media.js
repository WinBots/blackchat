import api from './http'

/**
 * Faz upload de uma imagem
 * @param {File} file - Arquivo de imagem
 * @returns {Promise<{filename: string, url: string, size: number, type: string}>}
 */
export async function uploadImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  const res = await api.post('/api/v1/media/upload-image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  
  return res.data
}

/**
 * Faz upload de um arquivo de áudio
 * @param {File} file - Arquivo de áudio
 * @returns {Promise<{filename: string, url: string, size: number, type: string}>}
 */
export async function uploadAudio(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  const res = await api.post('/api/v1/media/upload-audio', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  
  return res.data
}

/**
 * Faz upload de um arquivo de vídeo
 * @param {File} file - Arquivo de vídeo
 * @returns {Promise<{filename: string, url: string, size: number, type: string}>}
 */
export async function uploadVideo(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  const res = await api.post('/api/v1/media/upload-video', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  
  return res.data
}

/**
 * Deleta uma imagem
 * @param {string} filename - Nome do arquivo
 * @returns {Promise<{status: string, message: string}>}
 */
export async function deleteImage(filename) {
  const res = await api.delete(`/api/v1/media/images/${filename}`)
  return res.data
}

/**
 * Deleta um arquivo de áudio
 * @param {string} filename - Nome do arquivo
 * @returns {Promise<{status: string, message: string}>}
 */
export async function deleteAudio(filename) {
  const res = await api.delete(`/api/v1/media/audio/${filename}`)
  return res.data
}

/**
 * Deleta um arquivo de vídeo
 * @param {string} filename - Nome do arquivo
 * @returns {Promise<{status: string, message: string}>}
 */
export async function deleteVideo(filename) {
  const res = await api.delete(`/api/v1/media/video/${filename}`)
  return res.data
}

/**
 * Obtém a URL completa de uma mídia
 * @param {string} urlOrPath - URL completa ou path relativo (/api/v1/media/...)
 * @returns {string} URL completa
 */
export function getMediaUrl(urlOrPath) {
  if (!urlOrPath) return ''
  
  // Se já é uma URL completa (http/https), retorna como está
  if (urlOrPath.startsWith('http://') || urlOrPath.startsWith('https://')) {
    return urlOrPath
  }
  
  // Se é um path relativo, converte para URL completa
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8061'
  return `${baseURL}${urlOrPath}`
}

/**
 * Obtém a URL completa de uma imagem (alias para compatibilidade)
 * @param {string} urlOrPath - URL completa ou path relativo (/api/v1/media/...)
 * @returns {string} URL completa
 */
export function getImageUrl(urlOrPath) {
  return getMediaUrl(urlOrPath)
}

/**
 * Obtém a URL completa de um áudio
 * @param {string} urlOrPath - URL completa ou path relativo (/api/v1/media/...)
 * @returns {string} URL completa
 */
export function getAudioUrl(urlOrPath) {
  return getMediaUrl(urlOrPath)
}

/**
 * Obtém a URL completa de um vídeo
 * @param {string} urlOrPath - URL completa ou path relativo (/api/v1/media/...)
 * @returns {string} URL completa
 */
export function getVideoUrl(urlOrPath) {
  return getMediaUrl(urlOrPath)
}

/**
 * Formata o tamanho do arquivo em formato legível
 * @param {number} bytes - Tamanho em bytes
 * @returns {string} Tamanho formatado (ex: "1.5 MB")
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

