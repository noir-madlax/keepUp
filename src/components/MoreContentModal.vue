<template>
  <div 
    v-if="modelValue"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[999]"
    @click="handleClose"
  >
    <div 
      class="bg-white rounded-lg shadow-lg w-[90%] max-w-[600px] max-h-[90vh] relative"
      @click.stop
    >
      <!-- 关闭按钮 -->
      <div class="absolute right-2 top-2">
        <button
          @click="handleClose"
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
          <!-- 标题和基本信息 -->
          <div class="mb-6">
            <h3 class="text-lg font-medium mb-4">{{ t('summarize.title') }}</h3>
            <!-- 文章信息 -->
            <div class="bg-gray-50 p-4 rounded-lg text-sm">
              <div class="mb-2">
                <span class="text-gray-500">{{ t('article.id') }}:</span>
                <span class="ml-2">{{ articleId }}</span>
              </div>
              <div>
                <span class="text-gray-500">{{ t('article.originalUrl') }}:</span>
                <span class="ml-2 break-all">{{ originalUrl }}</span>
              </div>
            </div>
          </div>

          <!-- 语言选择区域 -->
          <div class="grid gap-6">
            <!-- 总结语言的选择 -->
            <div>
              <div class="flex items-center gap-2 mb-2">
                <h3 class="text-sm font-semibold text-gray-700">{{ t('summarize.summaryLanguageTitle') }}</h3>
                <p class="text-xs text-gray-400">{{ t('summarize.summaryLanguageTitleNote') }}</p>
              </div>
              <div class="flex flex-wrap gap-2">
                <label
                  v-for="lang in ['zh', 'en']"
                  :key="`summary-${lang}`"
                  class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer transition-all duration-200"
                  :class="[
                    isLanguageExisting('summary', lang) ? 
                      'bg-gray-100 text-gray-400 cursor-not-allowed' :
                      summaryLanguages.includes(lang) ?
                        'border-blue-600 bg-blue-100 font-medium' :
                        'border-gray-300 text-gray-500'
                  ]"
                >
                  <input 
                    type="checkbox" 
                    :value="lang" 
                    v-model="summaryLanguages" 
                    :disabled="isLanguageExisting('summary', lang)"
                    class="hidden" 
                  />
                  <span>{{ t(`summarize.languages.${lang}`) }}</span>
                  <span v-if="isLanguageExisting('summary', lang)" class="text-sm text-gray-400">
                    {{ t('summarize.alreadyExists') }}
                  </span>
                </label>
              </div>
            </div>

            <!-- 分段详述语言选择 -->
            <div>
              <div class="flex items-center gap-2 mb-2">
                <h3 class="text-sm font-semibold text-gray-700">{{ t('summarize.detailedLanguageTitle') }}</h3>
                <p class="text-xs text-gray-400">{{ t('summarize.detailedLanguageTitleNote') }}</p>
              </div>
              <div class="flex flex-wrap gap-2">
                <label
                  v-for="lang in ['zh', 'en']"
                  :key="`detailed-${lang}`"
                  class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer transition-all duration-200"
                  :class="[
                    isLanguageExisting('detailed', lang) ? 
                      'bg-gray-100 text-gray-400 cursor-not-allowed' :
                      detailedLanguages.includes(lang) ?
                        'border-blue-600 bg-blue-100 font-medium' :
                        'border-gray-300 text-gray-500'
                  ]"
                >
                  <input 
                    type="checkbox" 
                    :value="lang" 
                    v-model="detailedLanguages" 
                    :disabled="isLanguageExisting('detailed', lang)"
                    class="hidden" 
                  />
                  <span>{{ t(`summarize.languages.${lang}`) }}</span>
                  <span v-if="isLanguageExisting('detailed', lang)" class="text-sm text-gray-400">
                    {{ t('summarize.alreadyExists') }}
                  </span>
                </label>
              </div>
            </div>

            <!-- 原文字幕语言选择 -->
            <div>
              <div class="flex items-center gap-2 mb-2">
                <h3 class="text-sm font-semibold text-gray-700">{{ t('summarize.subtitleLanguageTitle') }}</h3>
                <p class="text-xs text-gray-400">{{ t('summarize.subtitleLanguageTitleNote') }}</p>
              </div>
              <div class="flex flex-wrap gap-2">
                <label
                  v-for="lang in ['zh', 'en']"
                  :key="`subtitle-${lang}`"
                  class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer transition-all duration-200"
                  :class="[
                    isLanguageExisting('subtitle', lang) ? 
                      'bg-gray-100 text-gray-400 cursor-not-allowed' :
                      subtitleLanguages.includes(lang) ?
                        'border-blue-600 bg-blue-100 font-medium' :
                        'border-gray-300 text-gray-500'
                  ]"
                >
                  <input 
                    type="checkbox" 
                    :value="lang" 
                    v-model="subtitleLanguages" 
                    :disabled="isLanguageExisting('subtitle', lang)"
                    class="hidden" 
                  />
                  <span>{{ t(`summarize.languages.${lang}`) }}</span>
                  <span v-if="isLanguageExisting('subtitle', lang)" class="text-sm text-gray-400">
                    {{ t('summarize.alreadyExists') }}
                  </span>
                </label>
              </div>
            </div>
          </div>

          <!-- 按钮区域 -->
          <div class="flex justify-end gap-2 mt-6">
            <button 
              @click="handleClose"
              class="px-4 py-2 text-sm border rounded hover:bg-gray-50"
              :disabled="isSubmitting"
            >
              {{ t('summarize.buttons.cancel') }}
            </button>
            <button 
              @click="handleSubmit"
              class="px-4 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
              :disabled="isSubmitting || !hasAnySelection"
            >
              {{ isSubmitting ? t('summarize.buttons.submitting') : t('summarize.buttons.confirm') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'

const { t } = useI18n()

const props = defineProps<{
  modelValue: boolean
  articleId: number
  originalUrl: string
  sectionStatus: {
    summaryZh: boolean
    summaryEn: boolean
    detailedZh: boolean
    detailedEn: boolean
    subtitleZh: boolean
    subtitleEn: boolean
  } | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

// 语言选择状态
const summaryLanguages = ref<string[]>([])
const detailedLanguages = ref<string[]>([])
const subtitleLanguages = ref<string[]>([])

// 提交状态
const isSubmitting = ref(false)

// 判断某个语言是否已存在
const isLanguageExisting = (type: 'summary' | 'detailed' | 'subtitle', lang: string) => {
  if (!props.sectionStatus) return false
  
  switch (type) {
    case 'summary':
      return lang === 'zh' ? props.sectionStatus.summaryZh : props.sectionStatus.summaryEn
    case 'detailed':
      return lang === 'zh' ? props.sectionStatus.detailedZh : props.sectionStatus.detailedEn
    case 'subtitle':
      return lang === 'zh' ? props.sectionStatus.subtitleZh : props.sectionStatus.subtitleEn
  }
}

// 处理关闭
const handleClose = () => {
  emit('update:modelValue', false)
}

// 添加验证函数
const validateSelections = () => {
  const hasSelection = summaryLanguages.value.length > 0 ||
    detailedLanguages.value.length > 0 ||
    subtitleLanguages.value.length > 0
    
  if (!hasSelection) {
    ElMessage.warning(t('summarize.messages.languageRequired'))
    return false
  }
  return true
}

// 处理提交
const handleSubmit = async () => {
  if (!validateSelections()) return
  
  try {
    isSubmitting.value = true
    
    // 准备提交数据
    const requestData = {
      article_id: props.articleId,
      original_url: props.originalUrl,
      is_supplement: true,
      summary_languages: summaryLanguages.value,
      detailed_languages: detailedLanguages.value,
      subtitle_languages: subtitleLanguages.value
    }

    // 发送请求
    const response = await fetch('/api/workflow/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.message || '提交失败')
    }

    ElMessage.success(t('summarize.supplementSuccess'))
    handleClose()
    
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(error instanceof Error ? error.message : t('summarize.messages.submitFailed'))
  } finally {
    isSubmitting.value = false
  }
}

// 添加重置函数
const resetState = () => {
  summaryLanguages.value = []
  detailedLanguages.value = []
  subtitleLanguages.value = []
}

// 监听 modelValue 变化，当 modal 关闭时重置状态
watch(() => props.modelValue, (newVal) => {
  if (!newVal) {
    resetState()
  }
})

// 添加计算属性
const hasAnySelection = computed(() => {
  return summaryLanguages.value.length > 0 ||
    detailedLanguages.value.length > 0 ||
    subtitleLanguages.value.length > 0
})
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