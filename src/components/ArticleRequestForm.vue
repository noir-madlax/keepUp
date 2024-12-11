<template>
  <div>
    <!-- 主要上传按钮，点击显示模态框 -->
    <button 
      @click="showUploadModal = true"
      class="flex items-center justify-center gap-2 px-4 py-2 text-sm text-white rounded hover:opacity-90 transition-opacity w-[85px]"
      style="background: linear-gradient(to right, #2272EB 0%, #00BEFF 100%)"
    >
      <!-- 按钮图标 -->
      <img
        src="/images/icons/upload_button.png"
        alt="upload icon"
        class="w-4 h-4"
      />
      <!-- 按钮文字 -->
      <span>{{ t('summarize.title') }}</span>
    </button>

    <!-- 模态框组件，包含文章URL输入和语言选择 -->
    <div v-if="showUploadModal">
      <!-- 模态框遮罩层 -->
      <div
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        @click="showUploadModal = false"
      >
        <!-- 模态框内容 -->
        <div
          class="bg-white p-6 rounded-lg shadow-lg w-[500px]"
          @click.stop
        >
          <!-- 文章URL输入 -->
          <div class="mb-6">
            <!-- 标题和手工按钮的容器 -->
            <div class="flex items-center gap-4 mb-2">
              <!-- 标题 -->
              <h3 class="text-lg font-medium">{{ t('summarize.title') }}</h3>
              
              <!-- 3个支持的渠道图标 - 调整位置和大小 -->
              <div class="flex items-center gap-3">
                <img src="/images/icons/youtube.svg" alt="YouTube" class="w-6 h-6 text-gray-500" title="YouTube" />
                <!-- 更新 Apple Podcast 图标 -->
                <img 
                  src="/images/icons/apple-podcast.svg" 
                  alt="Apple Podcast" 
                  class="w-6 h-6" 
                  title="Apple Podcast" 
                />
                <!-- 更新 Spotify 图标 -->
                <img 
                  src="/images/icons/spotify.svg" 
                  alt="Spotify" 
                  class="w-6 h-6" 
                  title="Spotify" 
                />
              </div>

              <!-- 手工按钮 -->
              <button 
                class="px-4 py-2 text-sm bg-gray-100 text-gray-900 rounded border border-gray-300 hover:bg-gray-200 shadow-sm ml-auto"
                @click="handleManual"
              >
                {{ t('summarize.manualupload') }}
              </button>
            </div>
            <!-- 文章URL输入框 -->
            <input
              type="text"
              v-model="requestUrl"
              :placeholder="t('summarize.urlPlaceholder')"
              class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              @keyup.enter="submitRequest"
            />
          </div>

          <div class="mb-6">
            <!-- 摘要语言选择 -->
            <h3 class="text-sm text-gray-600 mb-2">{{ t('summarize.summaryLanguageTitle') }}</h3>
            <div class="flex gap-2">
              <!-- 摘要语言选择复选框 -->
              <label
              v-for="lang in ['en', 'zh']"
              :key="`summary-${lang}`"
              class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer"
              :class="summaryLanguages.includes(lang) ? 'border-blue-500 bg-blue-50' : 'border-gray-300'"
            >
              <!-- 摘要语言选择复选框 -->
              <input
                type="checkbox"
                :value="lang"
                v-model="summaryLanguages"
                class="hidden"
              />
              <span>{{ t(`summarize.languages.${lang}`) }}</span>
              <svg v-if="summaryLanguages.includes(lang)" class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              </label>
            </div>
          </div>

        <div class="mb-6">
          <!-- 副标题语言选择 -->
          <h3 class="text-sm text-gray-600 mb-2">{{ t('summarize.subtitleLanguageTitle') }}</h3>
          <!-- 副标题语言选择复选框 -->
          <div class="flex gap-2">
            <label
              v-for="lang in ['en', 'zh']"
              :key="`subtitle-${lang}`"
              class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer"
              :class="subtitleLanguages.includes(lang) ? 'border-blue-500 bg-blue-50' : 'border-gray-300'"
            >
              <!-- 副标题语言选择复选框 -->
              <input
                type="checkbox"
                :value="lang"
                v-model="subtitleLanguages"
                class="hidden"
              />
              <span>{{ t(`summarize.languages.${lang}`) }}</span>
              <svg v-if="subtitleLanguages.includes(lang)" class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </label>
          </div>
        </div>

        <div class="mb-6">
          <!-- 详细摘要语言选择 -->
          <h3 class="text-sm text-gray-600 mb-2">{{ t('summarize.detailedLanguageTitle') }}</h3>
          <!-- 详细摘要语言选择复选框 -->
          <div class="flex gap-2">
            <label
              v-for="lang in ['en', 'zh']"
              :key="`detailed-${lang}`"
              class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer"
              :class="detailedLanguages.includes(lang) ? 'border-blue-500 bg-blue-50' : 'border-gray-300'"
            >
              <!-- 详细摘要语言选择复选框 -->
            <input
                type="checkbox"
                :value="lang"
                v-model="detailedLanguages"
                class="hidden"
              />
              <span>{{ t(`summarize.languages.${lang}`) }}</span>
              <svg v-if="detailedLanguages.includes(lang)" class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </label>
          </div>
        </div>

          <div class="flex justify-end gap-2">
          <!-- 取消按钮 -->
          <button 
            @click="showUploadModal = false"
            class="px-4 py-2 text-sm border rounded hover:bg-gray-50"
          >
            {{ t('summarize.buttons.cancel') }}
          </button>
          <!-- 确认按钮 -->
          <button 
            @click="submitRequest"
            class="px-4 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
            :disabled="isProcessing || !validateLanguageSelections()"
          >
            {{ isProcessing ? t('summarize.buttons.processing') : t('summarize.buttons.confirm') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup lang="ts">
// 导入必要的依赖
import { ref } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import { supabase } from '../supabaseClient'
import { useI18n } from 'vue-i18n'

// 初始化国际化工具
const { t } = useI18n()
const requestUrl = ref('')
const isProcessing = ref(false)
const showUploadModal = ref(false)
const summaryLanguages = ref<string[]>(['en'])
const subtitleLanguages = ref<string[]>([])
const detailedLanguages = ref<string[]>([])

// 定义组件事件
const emit = defineEmits(['refresh'])

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

  try {
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
        detailed_languages: detailedLanguages.value
      })
    })

    // 直接显示成功消息并关闭窗口
    ElMessage.success(t('summarize.messages.submitSuccess'))
    requestUrl.value = ''
    showUploadModal.value = false
    emit('refresh')
    
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(t('summarize.messages.submitFailed'))
  }
}
</script> 