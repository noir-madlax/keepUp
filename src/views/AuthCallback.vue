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
    // 设置一个超时，确保不会永远停留在这个页面
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('认证超时')), 5000)
    })

    // 等待 supabase 处理认证回调
    const authPromise = authStore.handleAuthCallback()
    
    // 使用 Promise.race 确保不会永远等待
    await Promise.race([authPromise, timeoutPromise])
    
    console.log('认证回调处理成功，准备跳转首页')
    
  } catch (error) {
    console.error('认证处理出错:', error)
  } finally {
    // 无论如何都重定向到首页
    console.log('开始跳转到首页')
    await router.push('/')
    console.log('跳转完成')
  }
})
</script> 