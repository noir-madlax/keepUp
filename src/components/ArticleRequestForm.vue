<template>
  <div>
    <!-- 主要上传按钮，点击显示模态框 -->
    <button 
      @click="showUploadModal = true"
      class="flex items-center gap-2 px-4 py-2 text-sm text-white rounded hover:opacity-90 transition-opacity"
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
      <div
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        @click="showUploadModal = false"
      >
        <div
          class="bg-white p-6 rounded-lg shadow-lg w-[500px]"
          @click.stop
        >
          <div class="mb-6">
            <h3 class="text-lg font-medium mb-2">{{ t('summarize.title') }}</h3>
            <input
              type="text"
              v-model="requestUrl"
              :placeholder="t('summarize.urlPlaceholder')"
              class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              @keyup.enter="submitRequest"
            />
          </div>

        <div class="mb-6">
          <h3 class="text-sm text-gray-600 mb-2">{{ t('summarize.summaryLanguageTitle') }}</h3>
          <div class="flex gap-2">
            <label
              v-for="lang in ['en', 'zh']"
              :key="`summary-${lang}`"
              class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer"
              :class="summaryLanguages.includes(lang) ? 'border-blue-500 bg-blue-50' : 'border-gray-300'"
            >
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
          <h3 class="text-sm text-gray-600 mb-2">{{ t('summarize.subtitleLanguageTitle') }}</h3>
          <div class="flex gap-2">
            <label
              v-for="lang in ['en', 'zh']"
              :key="`subtitle-${lang}`"
              class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer"
              :class="subtitleLanguages.includes(lang) ? 'border-blue-500 bg-blue-50' : 'border-gray-300'"
            >
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
          <h3 class="text-sm text-gray-600 mb-2">{{ t('summarize.detailedLanguageTitle') }}</h3>
          <div class="flex gap-2">
            <label
              v-for="lang in ['en', 'zh']"
              :key="`detailed-${lang}`"
              class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer"
              :class="detailedLanguages.includes(lang) ? 'border-blue-500 bg-blue-50' : 'border-gray-300'"
            >
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
          <button 
            @click="showUploadModal = false"
            class="px-4 py-2 text-sm border rounded hover:bg-gray-50"
          >
            {{ t('summarize.buttons.cancel') }}
          </button>
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
const selectedLanguages = ref<string[]>(['en'])
const summaryLanguages = ref<string[]>(['en'])
const subtitleLanguages = ref<string[]>([])
const detailedLanguages = ref<string[]>([])

// 响应式状态管理
const requestUrl = ref('') // 存储用户输入的URL
const isProcessing = ref(false) // 处理状态标志
const showUploadModal = ref(false) // 控制模态框显示
const selectedLanguages = ref<string[]>(['en']) // 选中的语言列表，默认英语

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
  const { data, error } = await supabase
    .from('keep_article_requests')
    .select('id')
    .eq('url', url)
    .single()
    
  if (data) {
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
 * 1. 验证输入
 * 2. 创建数据库记录
 * 3. 触发后端处理
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
    // 1. 创建请求记录
    const { data: requestData, error: requestError } = await supabase
      .from('keep_article_requests')
      .insert({
        url: requestUrl.value,
      })
      .select()
      .single()
      
    if (requestError) throw requestError

    // 2. 触发后端处理但不等待完成
    fetch('/api/workflow/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id: requestData.id,
        url: requestUrl.value,
        summary_languages: summaryLanguages.value,
        subtitle_languages: subtitleLanguages.value,
        detailed_languages: detailedLanguages.value
      })
    })

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