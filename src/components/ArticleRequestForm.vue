<template>
  <div>
    <!-- 上传按钮 -->
    <button 
      @click="showUploadModal = true"
      class="flex items-center gap-2 px-4 py-2 text-sm border rounded hover:bg-gray-50"
    >
      <span>{{ t('summarize.title') }}</span>
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
    </button>

    <!-- 上传模态框 -->
    <div 
      v-if="showUploadModal" 
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
          <h3 class="text-sm text-gray-600 mb-2">{{ t('summarize.languageTitle') }}</h3>
          <div class="flex gap-2">
            <label 
              v-for="lang in ['en', 'zh']" 
              :key="lang"
              class="flex items-center gap-2 px-3 py-2 border rounded cursor-pointer"
              :class="selectedLanguages.includes(lang) ? 'border-blue-500 bg-blue-50' : 'border-gray-300'"
            >
              <input 
                type="checkbox" 
                :value="lang" 
                v-model="selectedLanguages"
                class="hidden"
              />
              <span>{{ t(`summarize.languages.${lang}`) }}</span>
              <svg 
                v-if="selectedLanguages.includes(lang)"
                class="w-4 h-4 text-blue-500" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
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
            :disabled="isProcessing || !selectedLanguages.length"
          >
            {{ isProcessing ? t('summarize.buttons.processing') : t('summarize.buttons.confirm') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import { supabase } from '../supabaseClient'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const requestUrl = ref('')
const isProcessing = ref(false)
const showUploadModal = ref(false)
const selectedLanguages = ref<string[]>(['en'])

const emit = defineEmits(['refresh'])

// URL验证函数
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

// 检查重复提交
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

// 提交请求
const submitRequest = async () => {
  if (!validateUrl(requestUrl.value)) return
  if (!await checkDuplicate(requestUrl.value)) return
  if (!selectedLanguages.value.length) {
    ElMessage.warning(t('summarize.messages.languageRequired'))
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
        languages: selectedLanguages.value
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