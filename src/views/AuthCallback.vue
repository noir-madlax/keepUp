<template>
  <div class="flex items-center justify-center min-h-screen">
    <p>登录中...</p>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  try {
    // 等待 supabase 处理认证回调
    const { data, error } = await authStore.handleAuthCallback()
    
    if (error) {
      console.error('认证回调处理失败:', error)
      throw error
    }

    if (data) {
      // 认证成功后，重定向到首页
      await router.push('/')
    }
  } catch (error) {
    console.error('认证失败:', error)
    // 发生错误时重定向到首页
    await router.push('/')
  }
})
</script> 