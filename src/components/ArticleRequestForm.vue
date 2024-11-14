<template>
  <div class="flex items-center gap-2">
    <input 
      type="text" 
      v-model="requestUrl"
      placeholder="输入文章、视频内容的链接" 
      class="w-[280px] px-3 py-1.5 text-sm border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
      @keyup.enter="submitRequest"
    />
    <button 
      @click="submitRequest"
      class="px-3 py-1.5 text-sm bg-blue-500 text-white rounded-md hover:bg-blue-600"
    >
      上传
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { supabase } from '../supabaseClient'

const requestUrl = ref('')

// URL验证函数
const validateUrl = (url: string): boolean => {
  if (!url.trim()) {
    ElMessage.error('请输入URL')
    return false
  }

  try {
    new URL(url)
    return true
  } catch (e) {
    ElMessage.error('请输入有效的URL地址')
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
    ElMessage.error('该链接已经提交过了')
    return false
  }
  return true
}

// 提交请求
const submitRequest = async () => {
  if (!validateUrl(requestUrl.value)) return
  if (!await checkDuplicate(requestUrl.value)) return
  
  try {
    const { error } = await supabase
      .from('keep_article_requests')
      .insert({
        url: requestUrl.value,
      })
      
    if (error) throw error
    
    ElMessage.success('提交成功')
    requestUrl.value = '' // 清空输入框
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败，请重试')
  }
}
</script> 