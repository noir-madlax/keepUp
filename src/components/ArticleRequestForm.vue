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
           class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[999]"
           @click="handleModalClose">
        <!-- 调整 modal 容器的样式，移除固定宽度，使用最大宽度 -->
        <div class="bg-white rounded-lg shadow-lg w-[90%] max-w-[600px] max-h-[90vh] relative"
             @click.stop>
          <!-- 添加切换按钮 -->
          <div class="absolute right-2 top-2 flex gap-2">
            <!-- 切换按钮 -->
            <button
              @click="toggleModalType"
              class="px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-blue-50 hover:text-blue-600 hover:border-blue-300 transition-colors flex items-center gap-2"
            >
              <img
                :src="'/images/icons/doc.svg'"
                class="w-4 h-4"
                :alt="'File mode'"
              />
              {{t('summarize.switchToFile') }}
            </button>
            <!-- 关闭按钮 -->
            <button
              @click="handleModalClose"
              class="p-2 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100"
            >
              <span class="sr-only">Close</span>
              <svg class="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>

          <!-- Modal 内容区域 -->
          <div class="p-6 overflow-y-auto" style="max-height: calc(90vh - 2rem);">
            <div class="bg-white rounded-lg">
              <!-- URL输入区域 -->
              <div class="mb-6">
                 <!-- 添加上方空间，以免和右上角的按钮展示重叠冲突   -->
                 <div class="h-8"></div>
                <div class="flex items-center gap-4 mb-2 flex-wrap">
                  <h3 class="text-lg font-medium">{{ t('summarize.title_early') }}</h3>
                  
                  <!-- 根据模式显示不同的图标 -->
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
                  :placeholder="t(isFileMode ? 'summarize.filePlaceholder' : 'summarize.urlPlaceholder')"
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
                  <div class="h-0 mt-1">
                  </div>
                </div>


                <!-- 全文字幕的语言选择 -->
                <div v-if="isPrivilegedUser">
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
                <div v-if="isPrivilegedUser">
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

    <!-- 文件上传 Modal -->
    <Teleport to="body">
      <div v-if="showFileUploadModal" 
           class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[999]"
           @click="handleModalClose">
        <div class="bg-white rounded-lg shadow-lg w-[90%] max-w-[600px] max-h-[90vh] relative"
             @click.stop>
          <!-- 添加切换按钮 -->
          <div class="absolute right-2 top-2 flex gap-2">
           <!-- 切换按钮 -->
           <button
              @click="toggleModalType"
              class="px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-blue-50 hover:text-blue-600 hover:border-blue-300 transition-colors flex items-center gap-2"
            >
              <img
                :src="'/images/icons/upload.svg'"
                class="w-4 h-4"
                :alt="'Upload mode'"
              />
              {{ t('summarize.switchToUrl') }}
            </button>
            <!-- 关闭按钮 -->
            <button
              @click="handleModalClose"
              class="p-2 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100"
            >
              <span class="sr-only">Close</span>
              <svg class="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>

          <!-- Modal 内容区域 -->
          <div class="p-6 overflow-y-auto" style="max-height: calc(90vh - 2rem);">
            <div class="bg-white rounded-lg">
              <!-- 文件上传区域 -->
              <div class="mb-6">
                <!-- 添加上方空间，以免和右上角的按钮展示重叠冲突   -->
                <div class="h-8"></div>
                <div class="flex items-center gap-4 mb-2 flex-wrap">
                  <h3 class="text-lg font-medium">{{ t('summarize.title') }}</h3>

                  <!-- 文件类型图标 -->
                  <div class="flex items-center gap-3 flex-wrap">
                    <img src="/images/icons/doc.svg" alt="Doc" class="w-6 h-6" />
                    <img src="/images/icons/pdf.svg" alt="Pdf" class="w-6 h-6" />
                    <img src="/images/icons/txt.svg" alt="Txt" class="w-6 h-6" />
                  </div>
                </div>

                <!-- 文件上传区域 -->
                <div
                  class="w-full border-2 border-dashed rounded-lg p-4 text-center cursor-pointer hover:border-blue-500 transition-colors"
                  :class="{'border-blue-500 bg-blue-50': isDragging}"
                  @dragenter.prevent="isDragging = true"
                  @dragleave.prevent="isDragging = false"
                  @dragover.prevent
                  @drop.prevent="handleFileDrop"
                  @click="triggerFileInput"
                >
                  <input
                    type="file"
                    ref="fileInput"
                    class="hidden"
                    @change="handleFileSelect"
                    accept=".doc,.docx,.pdf,.txt"
                  />

                  <div v-if="!selectedFile" class="space-y-2">
                    <img src="/images/icons/file.svg" class="w-12 h-12 mx-auto mb-2" alt="Upload" />
                    <p class="text-gray-600">{{ t('summarize.dragAndDrop') }}</p>
                    <p class="text-sm text-gray-500">{{ t('summarize.or') }}</p>
                    <button class="text-blue-500 font-medium hover:text-blue-600">
                      {{ t('summarize.browseFiles') }}
                    </button>
                    <p class="text-xs text-gray-400 mt-2">
                      {{ t('summarize.supportedFormats') }}: DOC, PDF, TXT ({{ t('summarize.maxSize') }}: 30MB)
                    </p>
                  </div>

                  <div v-else class="space-y-2">
                    <div class="flex items-center justify-center gap-2">
                      <img
                        :src="`/images/icons/${getFileIcon(selectedFile.name)}`"
                        class="w-8 h-8"
                        :alt="selectedFile.name"
                      />
                      <span class="text-gray-700">{{ selectedFile.name }}</span>
                    </div>
                    <button
                      @click.stop="removeFile"
                      class="text-red-500 text-sm hover:text-red-600"
                    >
                      {{ t('summarize.removeFile') }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- 语言选择区域 -->
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
                      :key="`file-summary-${lang}`"
                      class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer transition-all duration-200"
                      :class="fileSummaryLanguages.includes(lang)
                        ? 'border-blue-600 bg-blue-100 font-medium'
                        : 'border-gray-300 text-gray-500'"
                    >
                      <input type="checkbox" :value="lang" v-model="fileSummaryLanguages" class="hidden" />
                      <span>{{ t(`summarize.languages.${lang}`) }}</span>
                      <svg v-if="fileSummaryLanguages.includes(lang)" class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </label>
                  </div>
                </div>
              </div>

              <!-- 按钮区域 -->
              <div class="flex justify-end gap-2 mt-6">
                <button
                  @click="showFileUploadModal = false"
                  class="px-4 py-2 text-sm border rounded hover:bg-gray-50"
                >
                  {{ t('summarize.buttons.cancel') }}
                </button>
                <button
                  @click="submitFileRequest"
                  class="px-4 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  :disabled="isFileProcessing || !validateFileLanguageSelections() || !selectedFile"
                >
                  {{ isFileProcessing 
                      ? `${t('summarize.buttons.processing')} (${uploadProgress}%)` 
                      : t('summarize.buttons.confirm') 
                  }}
                </button>
              </div>

              <!-- 在文件上传区域添加进度条 -->
              <div v-if="isFileProcessing" class="mt-2">
                <div class="w-full bg-gray-200 rounded-full h-2.5">
                  <div class="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                       :style="{ width: `${uploadProgress}%` }">
                  </div>
                </div>
                <p class="text-sm text-gray-500 mt-1">{{ uploadProgress }}%</p>
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
import { ref, watch, onUnmounted, nextTick, computed, h } from 'vue'
import { ElMessage, ElLoading, ElNotification } from 'element-plus'
import { supabase } from '../supabaseClient'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

// 添加 auth store
import { useAuthStore } from '../stores/auth'
const authStore = useAuthStore()
const router = useRouter()

// 2024-03-14: 添加特权用户判断
const isPrivilegedUser = computed(() => {
  return authStore.user?.id === '40568d0d-cd39-4bbe-8cba-634e9484b5cc'
})

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
// 修改默值为当前语言
const summaryLanguages = ref<string[]>([getCurrentLang()])
const subtitleLanguages = ref<string[]>(['na'])
const detailedLanguages = ref<string[]>(['na'])
const isSubmitting = ref(false)

// 在 script setup 中添加新的响应式变量
const subtitleWarningVisible = ref(false)
const detailedWarningVisible = ref(false)

// 修改 isFileMode 的定义，使用 ref 来跟踪状态
const isFileMode = ref(false)

// 修改 toggleModalType 方法
const toggleModalType = () => {
  // 切换 isFileMode 的值
  isFileMode.value = !isFileMode.value

  if (isFileMode.value) {
    // 切换到文件模式
    showUploadModal.value = false
    showFileUploadModal.value = true
    requestUrl.value = ''
  } else {
    // 切换到 URL 模式
    showUploadModal.value = true
    showFileUploadModal.value = false
    selectedFile.value = null
  }
}

// 监听语言变化，动态更新 summaryLanguages
watch(locale, (newLocale) => {
  if (!summaryLanguages.value.includes('na')) {  // 如果不是 na，则更新为当前语言
    summaryLanguages.value = [getCurrentLang()]
  }
})

// 监听字语言选择变化
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

// 添加类型定义
interface UploadResponse {
  success: boolean
  message: string
  request_id?: string
}

// 修改 emit 类型定义
const emit = defineEmits<{
  (e: 'refresh', payload: { type: string, requestId?: string }): void
  (e: 'click'): void
  (e: 'uploadSuccess', url: string): void
  (e: 'clearInput'): void
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
    .maybeSingle()
    
  // 检查 original_url 字段
  const { data: originalUrlData, error: originalUrlError } = await supabase
    .from('keep_article_requests')
    .select('id')
    .eq('original_url', url)
    .maybeSingle()
    
  if (urlData || originalUrlData) {
    // 获取重复的请求ID
    const duplicateId = (urlData as any)?.id || (originalUrlData as any)?.id

    if (duplicateId) {
      // 先查询请求状态
      const { data: requestData, error: requestError } = await supabase
        .from('keep_article_requests')
        .select('status, original_url')
        .eq('id', duplicateId)
        .single()
      
      if (requestError) {
        ElMessage.error(t('summarize.messages.duplicateUrl'))
        return false
      }

      // 如果请求已完成，查找对应的文章
      if ((requestData as any)?.status === 'processed') {
        const { data: articleData, error: articleError } = await supabase
          .from('keep_articles')
          .select('id')
          .eq('original_link', (requestData as any).original_url)
          .single()

        if (!articleError && (articleData as any)?.id) {
          const articleId = (articleData as any).id
          
          // 2024-03-14: 修改为提示后自动跳转
          ElMessage({
            message: t('summarize.messages.duplicateUrlAutoRedirect'),
            type: 'warning',
            duration: 2000,
            showClose: false
          })

          // 2秒后自动跳转
          setTimeout(() => {
            router.push(`/article/${articleId}`)
          }, 2000)

          return false
        } else {
          ElMessage.error(t('summarize.messages.duplicateUrl'))
        }
      } else {
        ElMessage.error(t('summarize.messages.duplicateUrl'))
      }
    } else {
      ElMessage.error(t('summarize.messages.duplicateUrl'))
    }
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
  if (isSubmitting.value) return
  isSubmitting.value = true

  try {
    if (!authStore.isAuthenticated) {
      ElMessage.warning(t('common.pleaseLogin'))
      return
    }

    if (!validateUrl(requestUrl.value)) return
    // 1月24日-注释掉重复检查
    // if (!await checkDuplicate(requestUrl.value)) return

    // 验证语言选择...

    // 先触发乐观更新
    emit('uploadSuccess', requestUrl.value)

    // 2024-03-25: 从URL识别平台
    const platform = getPlatformFromUrl(requestUrl.value)

    // 发送请求并等待响应
    const response = await fetch('/api/workflow/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        original_url: requestUrl.value,
        summary_languages: summaryLanguages.value,
        subtitle_languages: subtitleLanguages.value,
        detailed_languages: detailedLanguages.value,
        user_id: authStore.user?.id,
        platform: platform  // 添加平台信息
      })
    })

    // 检查响应状态
    if (!response.ok) {
      throw new Error(await response.text())
    }

    // 解析响应数据
    const data = await response.json()
    
    if (!data.success) {
      throw new Error(data.message || t('summarize.messages.submitFailed'))
    }

    ElMessage.success(t('summarize.messages.submitSuccess'))
    requestUrl.value = ''
    showUploadModal.value = false
    
    emit('refresh', { type: 'upload' })
    
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : t('summarize.messages.submitFailed'))
  } finally {
    isSubmitting.value = false
  }
}


// Modal 关闭处理
const handleModalClose = () => {
  showUploadModal.value = false
  showFileUploadModal.value = false
  requestUrl.value = ''
  selectedFile.value = null
  // 重置 isFileMode 为默认值
  isFileMode.value = false
}

// 组件卸载时确保清理
onUnmounted(() => {
  document.body.style.overflow = ''
})

// 修改 openModalWithUrl 方法
const openModalWithUrl = (url: string, type: 'url' | 'web' | 'file' = 'url') => {
  // 2024-03-14: 根据类型打开不同的 modal
  if (type === 'file') {
    showFileUploadModal.value = true
    isFileMode.value = true
  } else {
    requestUrl.value = url
    showUploadModal.value = true
    isFileMode.value = false
  }
}


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
         lowercaseUrl.includes('podcasts.apple.com') ||
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

// 文件上传相关的响应式变量
const showFileUploadModal = ref(false)
const fileUrl = ref('')
const isFileProcessing = ref(false)
const fileSummaryLanguages = ref<string[]>([getCurrentLang()])

// 文件上传的验证函数
const validateFileLanguageSelections = (): boolean => {
  const hasSummaryLanguage = fileSummaryLanguages.value.length > 0 &&
    !fileSummaryLanguages.value.includes('na')
  return hasSummaryLanguage
}

// 文件上传相关的响应式变量
const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const isDragging = ref(false)

// 文件大小限制（30MB）
const MAX_FILE_SIZE = 30 * 1024 * 1024

// 获取文件图标
const getFileIcon = (filename: string): string => {
  const ext = filename.split('.').pop()?.toLowerCase()
  switch (ext) {
    case 'doc':
    case 'docx':
      return 'doc.svg'
    case 'pdf':
      return 'pdf.svg'
    case 'txt':
      return 'txt.svg'
    default:
      return 'file.svg'
  }
}

// 验证文件
const validateFile = (file: File): boolean => {
  // 检查文件大小
  if (file.size > MAX_FILE_SIZE) {
    ElMessage.error(t('summarize.messages.fileTooLarge'))
    return false
  }

  // 检查文件类型
  const ext = file.name.split('.').pop()?.toLowerCase()
  const allowedTypes = ['doc', 'docx', 'pdf', 'txt']
  if (!ext || !allowedTypes.includes(ext)) {
    ElMessage.error(t('summarize.messages.invalidFileType'))
    return false
  }

  return true
}

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value?.click()
}

// 处理文件选择
const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    const file = input.files[0]
    if (validateFile(file)) {
      selectedFile.value = file
    }
    // 重置input值，允许选择相同文件
    input.value = ''
  }
}

// 处理文件拖放
const handleFileDrop = (event: DragEvent) => {
  isDragging.value = false
  const file = event.dataTransfer?.files[0]
  if (file && validateFile(file)) {
    selectedFile.value = file
  }
}

// 移除已选文件
const removeFile = () => {
  selectedFile.value = null
}

// 监听 modal 状态变化，控制 body 滚动
// 修改为统一的 watch
watch([showUploadModal, showFileUploadModal], ([uploadVal, fileVal]) => {
  // 只要有任意一个 modal 打开，就禁用动
  if (uploadVal || fileVal) {
    document.body.style.overflow = 'hidden'
  } else {
    // 两个 modal 都关闭时，恢复滚动
    document.body.style.overflow = ''
  }
})

// 添加上传进度状态
const uploadProgress = ref(0)

// 修改文件上传请求处理
const submitFileRequest = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning(t('common.pleaseLogin'))
    return
  }

  if (!selectedFile.value) {
    ElMessage.error(t('summarize.messages.fileRequired'))
    return
  }

  // 验证总结语言是否已选择
  if (!fileSummaryLanguages.value.length || fileSummaryLanguages.value.includes('na')) {
    ElMessage.warning(t('summarize.messages.summaryLanguageRequired'))
    return
  }

  try {
    isFileProcessing.value = true
    uploadProgress.value = 0

    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('summary_languages', JSON.stringify(fileSummaryLanguages.value))
    formData.append('user_id', authStore.user?.id || '')

    // 使用 XMLHttpRequest 来获取上传进度
    const response = await new Promise<UploadResponse>((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          uploadProgress.value = Math.round((e.loaded * 100) / e.total)
        }
      }
      
      xhr.onload = () => {
        if (xhr.status === 200) {
          resolve(JSON.parse(xhr.response))
        } else {
          reject(new Error(xhr.statusText))
        }
      }
      
      xhr.onerror = () => reject(new Error('Network Error'))
      
      xhr.open('POST', '/api/workflow/upload')
      xhr.send(formData)
    })

    if (!response.success) {
      throw new Error(response.message || t('summarize.messages.submitFailed'))
    }

    ElMessage.success(t('summarize.messages.submitSuccess'))
    selectedFile.value = null
    showFileUploadModal.value = false

    // 重置表单状态
    resetForm()

    // 触发刷新事件,传递请求ID
    emit('refresh', { 
      type: 'fileUpload',
      requestId: response.request_id 
    })

  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : t('summarize.messages.submitFailed'))
  } finally {
    isFileProcessing.value = false
    uploadProgress.value = 0
  }
}

// 添加重置表单方法
const resetForm = () => {
  selectedFile.value = null
  fileSummaryLanguages.value = [getCurrentLang()]
  isDragging.value = false
  isFileProcessing.value = false
}

// 2024-03-20: 修改快速提交方法，使用 notification 替代全屏 loading
const quickSubmit = async (url: string) => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning(t('common.pleaseLogin'))
    return
  }

  if (!validateUrl(url)) return

  let progressInterval: NodeJS.Timeout | null = null
  
  // 创建模拟上传进度条，右侧通知栏
  const notification = ElNotification({
    title: t('summarize.title'),
    message: h('div', { style: 'margin: 10px 0;' }, [
      h('p', { style: 'margin-bottom: 10px;' }, t('summarize.messages.submitting')),
      h('div', { class: 'progress-bar' }, [
        h('div', { 
          class: 'progress-bar-inner',
          style: {
            width: '0%',
            height: '2px',
            background: 'var(--el-color-primary)',
            transition: 'width 0.3s ease-in-out'
          }
        })
      ])
    ]),
    duration: 0,
    showClose: false,
    position: 'top-right'
  })

  try {
    isSubmitting.value = true
    
    // 模拟上传进度
    let progress = 0
    progressInterval = setInterval(() => {
      progress += 5
      if (progress <= 90) {
        const progressBar = document.querySelector('.progress-bar-inner') as HTMLElement
        if (progressBar) {
          progressBar.style.width = `${progress}%`
        }
      }
    }, 100)
    
    // 2024-03-25: 从URL识别平台
    const platform = getPlatformFromUrl(url)
    
    // 发送请求，默认使用英文
    const response = await fetch('/api/workflow/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        original_url: url,
        summary_languages: ['en','zh'],
        subtitle_languages: ['na'],
        detailed_languages: ['na'],
        user_id: authStore.user?.id,
        platform: platform  // 添加平台信息
      })
    })

    if (!response.ok) {
      throw new Error(await response.text())
    }

    const data = await response.json()
    
    if (!data.success) {
      throw new Error(data.message || t('summarize.messages.submitFailed'))
    }

    // 完成进度条
    if (progressInterval) {
      clearInterval(progressInterval)
    }
    const progressBar = document.querySelector('.progress-bar-inner') as HTMLElement
    if (progressBar) {
      progressBar.style.width = '100%'
    }

    // 延迟一小段时间后关闭通知
    setTimeout(() => {
      notification.close()
    }, 500)

    // 请求成功后，再触发乐观更新
    emit('uploadSuccess', url)
    emit('clearInput')
    emit('refresh', { type: 'upload' })
    
  } catch (error) {
    // 完成进度条
    if (progressInterval) {
      clearInterval(progressInterval)
    }
    const progressBar = document.querySelector('.progress-bar-inner') as HTMLElement
    if (progressBar) {
      progressBar.style.width = '100%'
    }

    // 延迟一小段时间后关闭通知
    setTimeout(() => {
      notification.close()
    }, 500)

    // 2024-03-27: 错误时也触发更新，让错误状态在卡片中显示
    emit('uploadSuccess', url)
    emit('clearInput')
    emit('refresh', { type: 'upload' })

    // 去掉错误提示，用错误卡片展示报错
   // ElMessage.error(error instanceof Error ? error.message : t('summarize.messages.submitFailed'))
  } finally {
    isSubmitting.value = false
  }
}

// 添加样式
const styles = `
<style>
.progress-bar {
  width: 100%;
  height: 2px;
  background: var(--el-border-color-lighter);
  border-radius: 1px;
  overflow: hidden;
}

.progress-bar-inner {
  height: 100%;
  background: var(--el-color-primary);
  transition: width 0.3s ease-in-out;
}

.el-notification {
  min-width: 300px;
}
</style>
`

// 将样式添加到文档中
if (typeof document !== 'undefined') {
  const styleElement = document.createElement('style')
  styleElement.innerHTML = styles
  document.head.appendChild(styleElement)
}

// 2024-03-20: 合并所有需要暴露的方法到一个 defineExpose 
defineExpose({
  openModalWithUrl,
  quickSubmit
})

// 从URL判断平台
const getPlatformFromUrl = (url: string): string => {
  if (url.includes('youtube.com') || url.includes('youtu.be')) {
    return 'youtube'
  }
  if (url.includes('open.spotify.com')) {
    return 'spotify'
  }
  if (url.includes('podcasts.apple.com')) {
    return 'apple'
  }
  return 'webpage'
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

.clickable-message {
  cursor: pointer !important;
  &:hover {
    opacity: 0.8;
  }
}
</style>