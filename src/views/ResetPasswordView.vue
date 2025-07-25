<!-- 2024-03-19: Reset Password Page -->
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Reset Password
        </h2>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleResetPassword">
        <div class="rounded-md shadow-sm -space-y-px">
          <div class="relative">
            <input
              :type="showPassword ? 'text' : 'password'"
              v-model="password"
              required
              class="appearance-none rounded relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="New Password"
              @focus="showPasswordRules = true"
              @blur="showPasswordRules = false"
            />
            <button 
              type="button"
              class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
              @click="showPassword = !showPassword"
            >
              <svg v-if="showPassword" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
          </div>
          <div class="mt-2">
            <input
              :type="showPassword ? 'text' : 'password'"
              v-model="confirmPassword"
              required
              class="appearance-none rounded relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="Confirm New Password"
            />
          </div>
        </div>

        <div 
          v-if="showPasswordRules"
          class="text-sm text-gray-600 bg-white border rounded p-2 shadow-lg"
        >
          <p class="font-medium mb-1">Password Requirements:</p>
          <ul class="list-disc pl-4 space-y-1">
            <li>At least 6 characters</li>
            <li>No special Unicode characters</li>
          </ul>
        </div>

        <div>
          <button
            type="submit"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            :disabled="isLoading"
          >
            <span v-if="isLoading">Processing...</span>
            <span v-else>Confirm Change</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { supabase } from '../supabaseClient'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showPasswordRules = ref(false)
const isLoading = ref(false)

// 修改为PKCE验证方式
onMounted(async () => {
  try {
    // 使用正确的恢复会话检查方式
    const { data: { user }, error } = await supabase.auth.getUser()
    
    if (error) throw error
    
    if (!user?.app_metadata.provider === 'recovery') {
      ElMessage.error('Invalid or expired reset password link')
      router.push('/')
      return
    }
  } catch (error) {
    console.error('恢复会话验证失败:', error)
    router.push('/')
  }
})

const handleResetPassword = async () => {
  if (password.value !== confirmPassword.value) {
    ElMessage.error('Passwords do not match')
    return
  }
  
  if (password.value.length < 6) {
    ElMessage.error('Password must be at least 6 characters')
    return
  }
  
  try {
    isLoading.value = true
    const { error } = await supabase.auth.updateUser({
      password: password.value
    })

    if (error) throw error

    ElMessage.success('Password changed successfully')
    await supabase.auth.signOut()
    router.push('/')
  } catch (error) {
    console.error('Reset password error:', error)
    ElMessage.error(error.message || 'Failed to change password')
  } finally {
    isLoading.value = false
  }
}
</script> 