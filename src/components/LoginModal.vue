<template>
  <div 
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click="$emit('close')"
  >
    <div 
      class="bg-white p-6 rounded-lg shadow-lg w-[400px]"
      @click.stop
    >
      <div class="text-center mb-6">
        <h2 class="text-2xl font-bold">登录</h2>
        <p class="text-gray-600 mt-2">选择登录方式继续</p>
      </div>

      <div class="space-y-4">
        <button
          @click="handleGithubLogin"
          class="w-full flex items-center justify-center gap-2 px-4 py-2 border rounded-lg hover:bg-gray-50"
        >
          <img src="/images/logos/github.svg" alt="GitHub" class="w-5 h-5" />
          使用 GitHub 登录
        </button>

        <button
          @click="handleGoogleLogin"
          class="w-full flex items-center justify-center gap-2 px-4 py-2 border rounded-lg hover:bg-gray-50"
        >
          <img src="/images/logos/google.svg" alt="Google" class="w-5 h-5" />
          使用 Google 登录
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()

const handleGithubLogin = async () => {
  try {
    await authStore.signInWithGithub()
  } catch (error) {
    console.error('GitHub login error:', error)
    ElMessage.error('登录失败，请重试')
  }
}

const handleGoogleLogin = async () => {
  try {
    await authStore.signInWithGoogle()
  } catch (error) {
    console.error('Google login error:', error)
    ElMessage.error('登录失败，请重试')
  }
}

defineEmits(['close'])
</script> 