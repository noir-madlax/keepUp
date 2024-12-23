<template>
  <!-- 添加 flex 和居中样式到父容器 -->
  <div class="justify-center">
    <!-- 主要上传按钮，点击显示模态框 -->
    <button 
      @click="handleClick"
      class="flex items-center justify-center gap-2 px-4 py-2 text-sm text-white rounded hover:opacity-90 transition-opacity w-[110px] h-[36px]"
      style="background: linear-gradient(to right, #2272EB 0%, #00BEFF 100%)"
    >
      <!-- 调整图标尺寸和对齐方式 -->
      <img
        src="/images/icons/upload_button.png"
        alt="upload icon"
        class="w-4 h-4 object-contain"
      />
      <!-- 添加行高确保文字垂直居中 -->
      <span class="leading-none">{{ t('summarize.title') }}</span>
    </button>

    <!-- 使用 Teleport 将 modal 传送到 body，并添加滚动锁定 -->
    <Teleport to="body">
      <div v-if="showUploadModal" 
           class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999]"
           @click="handleModalClose">
        <!-- 调整 modal 容器的样式，移除固定宽度，使用最大宽度 -->
        <div class="bg-white rounded-lg shadow-lg w-[90%] max-w-[600px] max-h-[90vh] relative"
             @click.stop>
          <!-- Modal 内容区域 -->
          <div class="p-6 overflow-y-auto" style="max-height: calc(90vh - 2rem);">
            <!-- 移除内部容器的固定宽度 -->
            <div class="bg-white rounded-lg">
              <!-- URL输入区域 -->
              <div class="mb-6">
                <div class="flex items-center gap-4 mb-2 flex-wrap">
                  <h3 class="text-lg font-medium">{{ t('summarize.title') }}</h3>
                  
                  <!-- 图标容器 -->
                  <div class="flex items-center gap-3 flex-wrap">
                    <img src="/images/icons/youtube.svg" alt="YouTube" class="w-6 h-6" />
                    <img src="/images/icons/apple-podcast.svg" alt="Apple Podcast" class="w-6 h-6" />
                    <img src="/images/icons/spotify.svg" alt="Spotify" class="w-6 h-6" />
                  </div>

                  <!-- 手工按钮 -->
                  <button 
                    class="px-4 py-2 text-sm bg-gray-100 text-gray-900 rounded border border-gray-300 hover:bg-gray-200 shadow-sm ml-auto"
                    @click="handleManual"
                  >
                    {{ t('summarize.manualupload') }}
                  </button>
                </div>

                <!-- URL输入框 -->
                <input
                  type="text"
                  v-model="requestUrl"
                  :placeholder="t('summarize.urlPlaceholder')"
                  class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  @keyup.enter="submitRequest"
                />
              </div>

              <!-- 语言选择区域使用 grid 布局 -->
              <div class="grid gap-6">
                <!-- 摘要语言选择 -->
                <div>
                  <h3 class="text-sm text-gray-600 mb-2">{{ t('summarize.summaryLanguageTitle') }}</h3>
                  <div class="flex flex-wrap gap-2">
                    <label
                      v-for="lang in ['en', 'zh']"
                      :key="`summary-${lang}`"
                      class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer"
                      :class="summaryLanguages.includes(lang) ? 'border-blue-500 bg-blue-50' : 'border-gray-300'"
                    >
                      <input type="checkbox" :value="lang" v-model="summaryLanguages" class="hidden" />
                      <span>{{ t(`summarize.languages.${lang}`) }}</span>
                      <svg v-if="summaryLanguages.includes(lang)" class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </label>
                  </div>
                </div>

                <!-- 副标题语言选择 -->
                <div>
                  <h3 class="text-sm text-gray-600 mb-2">{{ t('summarize.subtitleLanguageTitle') }}</h3>
                  <div class="flex flex-wrap gap-2">
                    <label
                      v-for="lang in ['en', 'zh']"
                      :key="`subtitle-${lang}`"
                      class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer"
                      :class="subtitleLanguages.includes(lang) ? 'border-blue-500 bg-blue-50' : 'border-gray-300'"
                    >
                      <input type="checkbox" :value="lang" v-model="subtitleLanguages" class="hidden" />
                      <span>{{ t(`summarize.languages.${lang}`) }}</span>
                      <svg v-if="subtitleLanguages.includes(lang)" class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </label>
                  </div>
                </div>

                <!-- 详细摘要语言选择 -->
                <div>
                  <h3 class="text-sm text-gray-600 mb-2">{{ t('summarize.detailedLanguageTitle') }}</h3>
                  <div class="flex flex-wrap gap-2">
                    <label
                      v-for="lang in ['en', 'zh']"
                      :key="`detailed-${lang}`"
                      class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer"
                      :class="detailedLanguages.includes(lang) ? 'border-blue-500 bg-blue-50' : 'border-gray-300'"
                    >
                      <input type="checkbox" :value="lang" v-model="detailedLanguages" class="hidden" />
                      <span>{{ t(`summarize.languages.${lang}`) }}</span>
                      <svg v-if="detailedLanguages.includes(lang)" class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </label>
                  </div>
                </div>
              </div>

              <!-- 按钮区域 -->
              <div class="flex justify-end gap-2 mt-6">
                <button 
                  @click="showUploadModal = false"
                  class="px-4 py-2 text-sm border rounded hover:bg-gray-50"
                >
                  {{ t('summarize.buttons.cancel') }}
                </button>
                <button 
                  @click="submitRequest"
                  class="px-4 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
                  :disabled="isProcessing || !validateLanguageSelections() || isSubmitting"
                >
                  {{ isSubmitting ? t('summarize.buttons.submitting') : (isProcessing ? t('summarize.buttons.processing') : t('summarize.buttons.confirm')) }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
// 导入必要的依赖
import { ref, watch, onUnmounted } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import { supabase } from '../supabaseClient'
import { useI18n } from 'vue-i18n'

// 添加 auth store
import { useAuthStore } from '../stores/auth'
const authStore = useAuthStore()

// 初始化国际化工具
const { t } = useI18n()
const requestUrl = ref('')
const isProcessing = ref(false)
const showUploadModal = ref(false)
const summaryLanguages = ref<string[]>(['en'])
const subtitleLanguages = ref<string[]>([])
const detailedLanguages = ref<string[]>([])
const isSubmitting = ref(false)

// 定义组件事件
const emit = defineEmits<{
  (e: 'refresh'): void
  (e: 'click'): void
}>()

/**
 * URL格式验证函数
 * @param url 待验证的URL字符串
 * @returns boolean 验证结果
 */
const validateUrl = (url: string): boolean => {
  if (!url.trim()) {
    ElMessage.error(t('summarize.messages.urlRequired'))
    return false
  }

  try {
    new URL(url)
    return true
  } catch (e) {
    ElMessage.error(t('summarize.messages.invalidUrl'))
    return false
  }
}

/**
 * 检查URL是否重复提交
 * @param url 待检查的URL
 * @returns boolean 检查结果
 */
const checkDuplicate = async (url: string): Promise<boolean> => {
  // 检查 url 字段
  const { data: urlData, error: urlError } = await supabase
    .from('keep_article_requests')
    .select('id')
    .eq('url', url)
    .single()
    
  // 检查 original_url 字段
  const { data: originalUrlData, error: originalUrlError } = await supabase
    .from('keep_article_requests')
    .select('id')
    .eq('original_url', url)
    .single()
    
  if (urlData || originalUrlData) {
    ElMessage.error(t('summarize.messages.duplicateUrl'))
    return false
  }
  return true
}

// 添加最大选择数量的验函数
const MAX_SELECTIONS = 3

const validateLanguageSelections = (): boolean => {
  const totalSelections = summaryLanguages.value.length +
    subtitleLanguages.value.length +
    detailedLanguages.value.length

  return totalSelections > 0 && totalSelections <= MAX_SELECTIONS
}

/**
 * 提交文章处理请求
 */
const submitRequest = async () => {
  if (isSubmitting.value) return // 立即检查是否正在提交
  isSubmitting.value = true // 立即禁用按钮

  try {
    if (!authStore.isAuthenticated) {
      ElMessage.warning(t('common.pleaseLogin'))
      return
    }

    if (!validateUrl(requestUrl.value)) return
    if (!await checkDuplicate(requestUrl.value)) return

    const totalSelections = summaryLanguages.value.length +
      subtitleLanguages.value.length +
      detailedLanguages.value.length

    if (totalSelections === 0) {
      ElMessage.warning(t('summarize.messages.languageRequired'))
      return
    }
    if (totalSelections > MAX_SELECTIONS) {
      ElMessage.warning(t('summarize.messages.maxSelectionsExceeded'))
      return
    }
    
    // 发送请求到后端
    fetch('/api/workflow/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: requestUrl.value,
        summary_languages: summaryLanguages.value,
        subtitle_languages: subtitleLanguages.value,
        detailed_languages: detailedLanguages.value,
        user_id: authStore.user?.id
      })
    })

    ElMessage.success(t('summarize.messages.submitSuccess'))
    requestUrl.value = ''
    showUploadModal.value = false
    
    // 触发刷新事件
    emit('refresh')
    
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(t('summarize.messages.submitFailed'))
  } finally {
    isSubmitting.value = false // 无论成功失败都恢复按钮状态
  }
}

// 监听 modal 状态变化，控制 body 滚动
watch(showUploadModal, (newVal) => {
  if (newVal) {
    // Modal 打开时禁用 body 滚动
    document.body.style.overflow = 'hidden'
  } else {
    // Modal 关闭时恢复 body 滚动
    document.body.style.overflow = ''
  }
})

// Modal 关闭处理
const handleModalClose = () => {
  showUploadModal.value = false
  requestUrl.value = ''
}

// 组件卸载时确保清理
onUnmounted(() => {
  document.body.style.overflow = ''
})

// 修改 openModalWithUrl 方法
const openModalWithUrl = (url: string) => {
  // 移除登录检查，由父组件统一处理
  requestUrl.value = url
  showUploadModal.value = true
}

// 暴露方法给父组件
defineExpose({
  openModalWithUrl
})

// 修改 handleManual 方法
const handleManual = () => {
  // 移除登录检查，由父组件统一处理
  // TODO: 处理手动上传逻辑
}

// 修改按钮点击处理
const handleClick = () => {
  // 移除登录检查，由父组件统一处理
  emit('click')
}
</script> 

<style scoped>
/* 添加自定义滚动条样式 */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: #CBD5E0 #EDF2F7;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #EDF2F7;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: #CBD5E0;
  border-radius: 3px;
}
</style>