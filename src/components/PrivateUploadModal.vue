<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="modelValue" class="modal-overlay" @click.self="closeModal">
        <div class="modal-container">
          <!-- 标题栏 -->
          <div class="modal-header">
            <div class="header-title">
              <span class="lock-icon">🔒</span>
              <span>私密上传</span>
            </div>
            <button class="close-btn" @click="closeModal">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <!-- 私密提示 -->
          <div class="privacy-notice">
            <span class="notice-icon">🔐</span>
            <span class="notice-text">仅你可见，分享链接后他人才能访问</span>
          </div>

          <!-- 总结类型选择（放在最前面，强制用户先选择） -->
          <div class="prompt-section">
            <div class="section-label">总结类型 <span class="required-hint">*</span></div>
            <div class="prompt-options-inline">
              <label 
                v-for="option in promptOptions" 
                :key="option.value"
                class="prompt-chip"
                :class="{ active: promptType === option.value }"
              >
                <input 
                  type="radio" 
                  :value="option.value" 
                  v-model="promptType"
                  class="hidden-radio"
                />
                <span class="chip-icon">{{ option.icon }}</span>
                <span class="chip-label">{{ option.label }}</span>
              </label>
            </div>
          </div>

          <!-- 输入类型选择 -->
          <div class="input-type-section">
            <div class="type-tabs">
              <button 
                class="type-tab" 
                :class="{ active: inputType === 'audio' }"
                @click="inputType = 'audio'"
              >
                <span class="tab-icon">🎤</span>
                <span>音频</span>
              </button>
              <button 
                class="type-tab" 
                :class="{ active: inputType === 'text' }"
                @click="inputType = 'text'"
              >
                <span class="tab-icon">📝</span>
                <span>文字</span>
              </button>
            </div>
          </div>

          <!-- 音频上传区域 -->
          <div v-if="inputType === 'audio'" class="upload-section">
            <div 
              class="upload-dropzone"
              :class="{ 'drag-over': isDragging, 'has-file': selectedFile }"
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="handleFileDrop"
              @click="triggerFileInput"
            >
              <input 
                ref="fileInput"
                type="file" 
                accept=".mp3,.wav,.m4a,.flac,.ogg,.aac"
                class="hidden-input"
                @change="handleFileSelect"
              />
              
              <div v-if="!selectedFile" class="dropzone-content">
                <div class="upload-icon">📁</div>
                <div class="upload-text">点击或拖拽上传音频</div>
                <div class="upload-formats">mp3/wav/m4a/flac · 最大100MB</div>
              </div>
              
              <div v-else class="selected-file">
                <div class="file-icon">🎵</div>
                <div class="file-info">
                  <div class="file-name">{{ selectedFile.name }}</div>
                  <div class="file-size">{{ formatFileSize(selectedFile.size) }}</div>
                </div>
                <button class="remove-file" @click.stop="removeFile">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6L6 18M6 6l12 12"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- 文字输入区域 -->
          <div v-else class="text-section">
            <textarea 
              v-model="textContent"
              class="text-input"
              placeholder="请输入或粘贴会议内容..."
              rows="4"
            ></textarea>
            <div class="text-counter">{{ textContent.length.toLocaleString() }}/100,000</div>
          </div>

          <!-- 标题输入 -->
          <div class="title-section">
            <div class="section-label">
              标题
              <span class="title-hint">（留空将由AI自动生成）</span>
            </div>
            <input 
              v-model="title"
              type="text"
              class="title-input"
              placeholder="留空自动生成，如：2024年12月部门周会"
            />
          </div>

          <!-- 提交按钮 -->
          <div class="submit-section">
            <button 
              class="submit-btn"
              :disabled="!canSubmit || isSubmitting"
              @click="handleSubmit"
            >
              <span v-if="isSubmitting" class="loading-spinner"></span>
              <span v-else>开始处理 🚀</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'submit', data: { requestId: number }): void
}>()

const authStore = useAuthStore()

// 状态
const inputType = ref<'audio' | 'text'>('audio')
const selectedFile = ref<File | null>(null)
const textContent = ref('')
const promptType = ref('')  // 默认空，强制用户选择
const title = ref('')
const isDragging = ref(false)
const isSubmitting = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

// Prompt 选项
const promptOptions = [
  { value: 'general', label: '通用会议纪要', icon: '🎯' },
  { value: 'parent', label: '家长会纪要', icon: '👨‍👩‍👧' },
  { value: 'customer', label: '客户商机分析纪要', icon: '💼' }
]

// 计算属性
const canSubmit = computed(() => {
  // 必须选择总结类型
  if (!promptType.value) return false
  
  if (inputType.value === 'audio') {
    return selectedFile.value !== null
  } else {
    return textContent.value.trim().length >= 50
  }
})

// 方法
const closeModal = () => {
  if (!isSubmitting.value) {
    emit('update:modelValue', false)
    resetForm()
  }
}

const resetForm = () => {
  inputType.value = 'audio'
  selectedFile.value = null
  textContent.value = ''
  promptType.value = ''  // 重置为空，强制再次选择
  title.value = ''
  isDragging.value = false
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    validateAndSetFile(file)
  }
}

const handleFileDrop = (event: DragEvent) => {
  isDragging.value = false
  const file = event.dataTransfer?.files[0]
  if (file) {
    validateAndSetFile(file)
  }
}

const validateAndSetFile = (file: File) => {
  const validExtensions = ['mp3', 'wav', 'm4a', 'flac', 'ogg', 'aac']
  const ext = file.name.split('.').pop()?.toLowerCase() || ''
  
  if (!validExtensions.includes(ext)) {
    alert(`不支持的音频格式: ${ext}\n支持的格式: ${validExtensions.join(', ')}`)
    return
  }
  
  const maxSize = 100 * 1024 * 1024 // 100MB
  if (file.size > maxSize) {
    alert('文件大小超过限制，最大支持 100MB')
    return
  }
  
  selectedFile.value = file
}

const removeFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const handleSubmit = async () => {
  if (!canSubmit.value || isSubmitting.value) return
  
  if (!authStore.isAuthenticated || !authStore.user?.id) {
    alert('请先登录')
    return
  }
  
  isSubmitting.value = true
  
  try {
    const formData = new FormData()
    formData.append('input_type', inputType.value)
    formData.append('prompt_type', promptType.value)
    formData.append('title', title.value.trim())  // 传空字符串让后端用 LLM 生成标题
    formData.append('user_id', authStore.user.id)
    
    if (inputType.value === 'audio' && selectedFile.value) {
      formData.append('file', selectedFile.value)
    } else if (inputType.value === 'text') {
      formData.append('text_content', textContent.value)
    }
    
    const response = await fetch('/api/workflow/private-upload', {
      method: 'POST',
      body: formData
    })
    
    const result = await response.json()
    
    if (result.success) {
      // 成功后先重置提交状态，然后关闭 modal 并通知父组件
      isSubmitting.value = false
      emit('update:modelValue', false)  // 直接关闭 modal
      resetForm()
      emit('submit', { requestId: result.request_id })
    } else {
      alert(`提交失败: ${result.message}`)
    }
  } catch (error: any) {
    console.error('提交私密内容失败:', error)
    if (error.message?.includes('Failed to fetch') || error.message?.includes('network')) {
      alert('网络连接失败，请检查网络后重试')
    } else {
      alert(`提交失败：${error.message || '请稍后重试'}`)
    }
  } finally {
    isSubmitting.value = false
  }
}

// 监听 modal 关闭时重置表单
watch(() => props.modelValue, (newVal) => {
  if (!newVal) {
    resetForm()
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.modal-container {
  width: 100%;
  max-width: 420px;
  max-height: 90vh;
  overflow-y: auto;
  /* 液态玻璃效果 */
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.95) 0%, 
    rgba(255, 255, 255, 0.88) 100%
  );
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.12),
    0 2px 8px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
  padding: 20px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.lock-icon {
  font-size: 20px;
}

.close-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #333;
}

/* 私密提示 */
.privacy-notice {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(100, 100, 120, 0.06);
  border-radius: 8px;
  margin-bottom: 16px;
}

.notice-icon {
  font-size: 14px;
}

.notice-text {
  font-size: 12px;
  color: #666;
}

.section-label {
  font-size: 13px;
  font-weight: 500;
  color: #666;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.required-hint {
  color: #ef4444;
  font-weight: 600;
}

.title-hint {
  font-size: 11px;
  color: #999;
  font-weight: 400;
}

.input-type-section {
  margin-bottom: 12px;
}

.type-tabs {
  display: flex;
  gap: 8px;
}

.type-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid #e5e5e5;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: #666;
}

.type-tab:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.type-tab.active {
  border-color: #1890ff;
  background: rgba(24, 144, 255, 0.08);
  color: #1890ff;
}

.tab-icon {
  font-size: 16px;
}

/* 上传区域 - 紧凑版 */
.upload-section {
  margin-bottom: 12px;
}

.upload-dropzone {
  border: 1.5px dashed #d9d9d9;
  border-radius: 10px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(255, 255, 255, 0.6);
}

.upload-dropzone:hover,
.upload-dropzone.drag-over {
  border-color: #1890ff;
  background: rgba(24, 144, 255, 0.04);
}

.upload-dropzone.has-file {
  border-style: solid;
  border-color: #52c41a;
  background: rgba(82, 196, 26, 0.04);
  padding: 12px;
}

.hidden-input {
  display: none;
}

.dropzone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.upload-icon {
  font-size: 28px;
}

.upload-text {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.upload-formats {
  font-size: 11px;
  color: #999;
}

.selected-file {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-icon {
  font-size: 24px;
}

.file-info {
  flex: 1;
  text-align: left;
}

.file-name {
  font-size: 13px;
  font-weight: 500;
  color: #333;
  word-break: break-all;
  line-height: 1.3;
}

.file-size {
  font-size: 11px;
  color: #999;
  margin-top: 2px;
}

.remove-file {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: rgba(255, 77, 79, 0.1);
  border-radius: 6px;
  cursor: pointer;
  color: #ff4d4f;
  transition: all 0.2s;
}

.remove-file:hover {
  background: rgba(255, 77, 79, 0.2);
}

/* 文字输入区域 */
.text-section {
  margin-bottom: 12px;
}

.text-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e5e5e5;
  border-radius: 10px;
  font-size: 13px;
  line-height: 1.5;
  resize: vertical;
  min-height: 80px;
  background: rgba(255, 255, 255, 0.8);
  transition: all 0.2s;
}

.text-input:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.text-input::placeholder {
  color: #bbb;
}

.text-counter {
  text-align: right;
  font-size: 11px;
  color: #999;
  margin-top: 4px;
}

/* Prompt 选择 - 横向紧凑版 */
.prompt-section {
  margin-bottom: 12px;
}

.prompt-options-inline {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.prompt-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border: 1px solid #e5e5e5;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(255, 255, 255, 0.8);
  font-size: 12px;
}

.prompt-chip:hover {
  border-color: #1890ff;
}

.prompt-chip.active {
  border-color: #1890ff;
  background: rgba(24, 144, 255, 0.08);
  color: #1890ff;
}

.hidden-radio {
  display: none;
}

.chip-icon {
  font-size: 14px;
}

.chip-label {
  color: #333;
}

.prompt-chip.active .chip-label {
  color: #1890ff;
}

/* 标题输入 */
.title-section {
  margin-bottom: 16px;
}

.title-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e5e5e5;
  border-radius: 10px;
  font-size: 13px;
  background: rgba(255, 255, 255, 0.8);
  transition: all 0.2s;
}

.title-input:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.title-input::placeholder {
  color: #bbb;
  font-size: 12px;
}

/* 提交按钮 */
.submit-section {
  display: flex;
  justify-content: center;
}

.submit-btn {
  width: 100%;
  padding: 12px 24px;
  font-size: 15px;
  font-weight: 500;
  color: white;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #40a9ff 0%, #1890ff 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.35);
}

.submit-btn:disabled {
  background: #d9d9d9;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Modal 动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .modal-container,
.modal-fade-leave-to .modal-container {
  transform: scale(0.95) translateY(20px);
}

/* 响应式 */
@media (max-width: 440px) {
  .modal-container {
    max-width: 100%;
    margin: 0 10px;
    padding: 16px;
    border-radius: 16px;
  }
  
  .prompt-options-inline {
    flex-direction: column;
  }
  
  .prompt-chip {
    justify-content: center;
  }
}
</style>
