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
    // 处理认证回调
    const { data, error } = await authStore.handleAuthCallback()
    
    if (error) {
      console.error('认证回调处理失败:', error)
      // 认证失败时重定向到首页
      router.push('/')
      return
    }

    if (data) {
      // 认证成功后立即重定向到首页
      router.push('/')
    }
  } catch (error) {
    console.error('认证过程发生错误:', error)
    router.push('/')
  }
})
</script> 