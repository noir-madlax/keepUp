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
                    <img src="/images/icons/web.svg" alt="Web Page" class="w-6 h-6" />
                  </div>

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
                <!-- 总结语言的选择 -->
                <div>
                  <div class="flex items-center gap-2 mb-2" :class="locale === 'en' ? 'max-[450px]:flex-col max-[450px]:items-start' : ''">
                    <h3 class="text-sm font-semibold text-gray-700">{{ t('summarize.summaryLanguageTitle') }}</h3>
                    <p class="text-xs text-gray-400">{{ t('summarize.summaryLanguageTitleNote') }}</p>
                  </div>
                  <div class="flex flex-wrap gap-2">
                    <label
                      v-for="lang in ['en', 'zh']"
                      :key="`summary-${lang}`"
                      class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer transition-all duration-200"
                      :class="summaryLanguages.includes(lang)
                        ? 'border-blue-600 bg-blue-100 font-medium'
                        : 'border-gray-300 text-gray-500'"
                    >
                      <input type="checkbox" :value="lang" v-model="summaryLanguages" class="hidden" />
                      <span>{{ t(`summarize.languages.${lang}`) }}</span>
                      <svg v-if="summaryLanguages.includes(lang)" class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </label>
                  </div>
                    <!-- 添加警告提示占位 -->
                    <div class="h-0 mt-1"
                  </div>
                </div>


                <!-- 全文字幕的语言选择 -->
                <div>
                  <div class="flex items-center gap-2 mb-2" :class="locale === 'en' ? 'max-[450px]:flex-col max-[450px]:items-start' : ''">
                    <h3 class="text-sm font-semibold text-gray-700">{{ t('summarize.subtitleLanguageTitle') }}</h3>
                    <p class="text-xs text-gray-400">{{ t('summarize.subtitleLanguageTitleNote') }}</p>
                  </div>
                  <div class="flex flex-wrap gap-2">
                    <label
                      v-for="lang in ['en', 'zh', 'na']"
                      :key="`subtitle-${lang}`"
                      class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer transition-all duration-200"
                      :class="subtitleLanguages.includes(lang)
                        ? 'border-blue-600 bg-blue-100 font-medium'
                        : 'border-gray-300 text-gray-500'"
                    >
                      <input type="checkbox" :value="lang" v-model="subtitleLanguages" class="hidden" />
                      <span>{{ t(`summarize.languages.${lang}`) }}</span>
                      <svg v-if="subtitleLanguages.includes(lang)" class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </label>
                  </div>
                  <!-- 添加警告提示占位 -->
                  <div class="h-0 mt-1">
                    <p v-if="subtitleWarningVisible" class="text-xs text-red-500 transition-opacity duration-200">
                      {{ t('summarize.messages.onlyForMedia') }}
                    </p>
                  </div>
                </div>

                <!-- 分段详述的语言选择 -->
                <div>
                  <div class="flex items-center gap-2 mb-2" :class="locale === 'en' ? 'max-[450px]:flex-col max-[450px]:items-start' : ''">
                    <h3 class="text-sm font-semibold text-gray-700">{{ t('summarize.detailedLanguageTitle') }}</h3>
                    <p class="text-xs text-gray-400">{{ t('summarize.detailedLanguageTitleNote') }}</p>
                  </div>
                  <div class="flex flex-wrap gap-2">
                    <label
                      v-for="lang in ['en', 'zh', 'na']"
                      :key="`detailed-${lang}`"
                      class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer transition-all duration-200"
                      :class="detailedLanguages.includes(lang)
                        ? 'border-blue-600 bg-blue-100 font-medium'
                        : 'border-gray-300 text-gray-500'"
                    >
                      <input type="checkbox" :value="lang" v-model="detailedLanguages" class="hidden" />
                      <span>{{ t(`summarize.languages.${lang}`) }}</span>
                      <svg v-if="detailedLanguages.includes(lang)" class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </label>
                  </div>
                  <!-- 添加警告提示占位 -->
                  <div class="h-0 mt-1">
                    <p v-if="detailedWarningVisible" class="text-xs text-red-500 transition-opacity duration-200">
                      {{ t('summarize.messages.onlyForMedia') }}
                    </p>
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
import { ref, watch, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import { supabase } from '../supabaseClient'
import { useI18n } from 'vue-i18n'

// 添加 auth store
import { useAuthStore } from '../stores/auth'
const authStore = useAuthStore()

// 初始化国际化工具
const { t, locale } = useI18n()

// 获取当前语言并设置默认值
const getCurrentLang = () => {
  // locale 通常是 'zh' 或 'en'
  return locale.value === 'zh' ? 'zh' : 'en'
}

const requestUrl = ref('')
const isProcessing = ref(false)
const showUploadModal = ref(false)
// 修改默���值为当前语言
const summaryLanguages = ref<string[]>([getCurrentLang()])
const subtitleLanguages = ref<string[]>(['na'])
const detailedLanguages = ref<string[]>(['na'])
const isSubmitting = ref(false)

// 在 script setup 中添加新的响应式变量
const subtitleWarningVisible = ref(false)
const detailedWarningVisible = ref(false)

// 监听语言变化，动态更新 summaryLanguages
watch(locale, (newLocale) => {
  if (!summaryLanguages.value.includes('na')) {  // 如果不是 na，则更新为当前语言
    summaryLanguages.value = [getCurrentLang()]
  }
})

// 监听字幕语言选择变化
watch(subtitleLanguages, async (newVal, oldVal) => {
  if (!isSupportedMediaUrl(requestUrl.value) && newVal.some(lang => lang !== 'na')) {
    showWarning('subtitle')
    subtitleLanguages.value = ['na']
    return
  }
  // 如果之前只有 na，现在选择了其他语言
  if (oldVal.includes('na') && oldVal.length === 1 && newVal.length > 1) {
    // 移除 na，保留新选择的语言
    subtitleLanguages.value = newVal.filter(lang => lang !== 'na')
    await nextTick()
    return
  }

  // 其他情况保持原有逻辑
  if (newVal.includes('na')) {
    if (newVal.length > 1) {
      subtitleLanguages.value = ['na']
      await nextTick()
    }
  } else if (newVal.length >= 1) {
    const filtered = newVal.filter(lang => lang !== 'na')
    if (filtered.length !== newVal.length) {
      subtitleLanguages.value = filtered
      await nextTick()
    }
  } else {
    // 如果没有选择任何语言，自动选择 na
    subtitleLanguages.value = ['na']
    await nextTick()
  }
}, { flush: 'post' })

// 监听详细语言选择变化
watch(detailedLanguages, async (newVal, oldVal) => {
  if (!isSupportedMediaUrl(requestUrl.value) && newVal.some(lang => lang !== 'na')) {
    showWarning('detailed')
    detailedLanguages.value = ['na']
    return
  }
  // 如果之前只有 na，现在选择了其他语言
  if (oldVal.includes('na') && oldVal.length === 1 && newVal.length > 1) {
    // 移除 na，保留新选择的语言
    detailedLanguages.value = newVal.filter(lang => lang !== 'na')
    await nextTick()
    return
  }

  // 其他情况保持原有逻辑
  if (newVal.includes('na')) {
    if (newVal.length > 1) {
      detailedLanguages.value = ['na']
      await nextTick()
    }
  } else if (newVal.length >= 1) {
    const filtered = newVal.filter(lang => lang !== 'na')
    if (filtered.length !== newVal.length) {
      detailedLanguages.value = filtered
      await nextTick()
    }
  } else {
    // 如果没有选择任何语言，自动选择 na
    detailedLanguages.value = ['na']
    await nextTick()
  }
}, { flush: 'post' })

// ��义组件事件
const emit = defineEmits<{
  (e: 'refresh', payload: { type: string }): void
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
  // 过滤掉 'na' 后再计算总数
  const totalSelections =
    summaryLanguages.value.filter(lang => lang !== 'na').length +
    subtitleLanguages.value.filter(lang => lang !== 'na').length +
    detailedLanguages.value.filter(lang => lang !== 'na').length

  // 确保总结语言至少选择了一个
  const hasSummaryLanguage = summaryLanguages.value.length > 0 &&
    !summaryLanguages.value.includes('na')

  // 总选择数不超过3，且必须有总结语言
  return totalSelections <= MAX_SELECTIONS && hasSummaryLanguage
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

  // 验证总结语言是否已选择
  if (!summaryLanguages.value.length || summaryLanguages.value.includes('na')) {
    ElMessage.warning(t('summarize.messages.summaryLanguageRequired'))
    return
  }

  const totalSelections =
    summaryLanguages.value.filter(lang => lang !== 'na').length +
    subtitleLanguages.value.filter(lang => lang !== 'na').length +
    detailedLanguages.value.filter(lang => lang !== 'na').length

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
        original_url: requestUrl.value,
        summary_languages: summaryLanguages.value,
        subtitle_languages: subtitleLanguages.value,
        detailed_languages: detailedLanguages.value,
        user_id: authStore.user?.id
      })
    })

    ElMessage.success(t('summarize.messages.submitSuccess'))
    requestUrl.value = ''
    showUploadModal.value = false
    
    // 触发刷新事件,并传递一个标识表明是上传成功
    emit('refresh', { type: 'upload' })
    
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

/**
 * 判断URL是否为支持的媒体类型
 * @param url 待检查的URL
 * @returns boolean 是否支持
 */
const isSupportedMediaUrl = (url: string): boolean => {
  const lowercaseUrl = url.toLowerCase()
  return lowercaseUrl.includes('youtube.com') ||
         lowercaseUrl.includes('youtu.be') ||
         lowercaseUrl.includes('spotify.com') ||
         lowercaseUrl.includes('apple.com/podcast')
}

// 添加警告显示逻辑
const showWarning = (type: 'subtitle' | 'detailed') => {
  if (!isSupportedMediaUrl(requestUrl.value)) {
    if (type === 'subtitle') {
      subtitleWarningVisible.value = true
      setTimeout(() => {
        subtitleWarningVisible.value = false
      }, 2000)
    } else {
      detailedWarningVisible.value = true
      setTimeout(() => {
        detailedWarningVisible.value = false
      }, 2000)
    }
  }
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