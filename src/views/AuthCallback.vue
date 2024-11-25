<template>
  <div class="flex items-center justify-center min-h-screen">
    <p>登录中...</p>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  console.log('开始处理认证回调')
  try {
    // 设置一个超时，确保不会永远停留在这个页面
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('认证超时')), 10000)
    })

    // 等待 supabase 处理认证回调
    const authPromise = authStore.handleAuthCallback()
    
    // 使用 Promise.race 确保不会永远等待
    const success = await Promise.race([authPromise, timeoutPromise])
    
    if (!success) {
      throw new Error('认证失败')
    }

    console.log('认证成功，准备跳转')
    router.replace('/')
  } catch (error) {
    console.error('认证处理详细错误:', error)
    ElMessage.error('登录失败，请重试')
    router.replace('/')
  }
})
</script> 