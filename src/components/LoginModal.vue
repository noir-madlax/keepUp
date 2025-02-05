<template>
  <div 
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center login-modal"
    @click="allowClose && $emit('close')"
  >
    <LoadingSpinner v-if="isLoading" variant="modal" />
    
    <div 
      class="bg-white p-6 rounded-lg shadow-lg w-[400px]"
      @click.stop
      v-if="!isLoading"
    >
      <div class="text-center mb-6">
        <h2 class="text-2xl font-bold">Sign in / Sign up</h2>
      </div>

      <!-- 邮箱登录表单 -->
      <form @submit.prevent="handleEmailAuth" class="space-y-4 mb-6">
        <input 
          type="email" 
          v-model="email"
          placeholder="Email"
          class="w-full px-4 py-2 border rounded"
          required
        />
        <div class="relative">
          <input 
            :type="showPassword ? 'text' : 'password'"
            v-model="password"
            placeholder="Password"
            class="w-full px-4 py-2 border rounded"
            required
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
          <div 
            v-if="showPasswordRules"
            class="absolute left-0 right-0 mt-1 p-2 bg-white border rounded shadow-lg text-sm text-gray-600 z-10"
          >
            <p class="font-medium mb-1">Password requirements:</p>
            <ul class="list-disc pl-4 space-y-1">
              <li>At least 6 characters</li>
              <li>No special Unicode characters</li>
            </ul>
          </div>
        </div>
        <div class="text-right">
          <button 
            type="button"
            class="text-sm text-blue-500 hover:text-blue-600"
            @click="handleForgotPassword"
          >
          Forgot Password?
          </button>
        </div>
        <button 
          type="submit"
          class="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
        >
          Continue with Email
        </button>
      </form>

      <div class="relative my-6">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-gray-300"></div>
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-2 bg-white text-gray-500">
            Or 
          </span>
        </div>
      </div>

      <div class="space-y-4">
        <button
          @click="handleGoogleLogin"
          class="w-full flex items-center justify-center gap-2 px-4 py-2 border rounded-lg hover:bg-gray-50"
        >
          <img src="/images/logos/google.svg" alt="Google" class="w-5 h-5" />
          Continue with Google
        </button>

        <button
          @click="handleGithubLogin"
          class="w-full flex items-center justify-center gap-2 px-4 py-2 border rounded-lg hover:bg-gray-50"
        >
          <img src="/images/logos/github.svg" alt="GitHub" class="w-5 h-5" />
          Continue with GitHub
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import { supabase } from '../supabaseClient'
import LoadingSpinner from './LoadingSpinner.vue'

const props = defineProps<{
  allowClose?: boolean
}>()

const authStore = useAuthStore()
const emit = defineEmits(['close', 'success'])

const isLoading = ref(false)
const email = ref('')
const password = ref('')
const showPasswordRules = ref(false)
const showPassword = ref(false)

// 邮箱登录处理方法
const handleEmailAuth = async () => {
  try {
    isLoading.value = true
    // 先尝试登录
    const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
      email: email.value,
      password: password.value
    })

    if (signInError) {
      if (signInError.message.includes('Invalid login credentials')) {
        // 尝试注册
        const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
          email: email.value,
          password: password.value
        })

        if (signUpError) {
          if (signUpError.message.includes('User already registered')) {
            ElMessage.error('Password is incorrect')
          } else if (signUpError.message.includes('Password should be')) {
            ElMessage.error(signUpError.message)
          } else {
            ElMessage.error(signUpError.message)
          }
          return
        }
        
        // 新用户注册成功
        ElMessage.success('Registration successful')
        emit('success')
        return
      } else {
        // 其他登录错误
        ElMessage.error(signInError.message)
        return
      }
    }

    // 登录成功
    emit('success')
  } catch (error: any) {
    console.error('Auth error:', error)
    ElMessage.error('Authentication failed')
  } finally {
    isLoading.value = false
  }
}

const handleGithubLogin = async () => {
  try {
    await authStore.signInWithGithub()
    emit('success')
  } catch (error) {
    console.error('GitHub login error:', error)
    ElMessage.error('Login failed')
  }
}

const handleGoogleLogin = async () => {
  try {
    await authStore.signInWithGoogle()
    emit('success')
  } catch (error) {
    console.error('Google login error:', error)
    ElMessage.error('Login failed')
  }
}

// 2024-03-19: 添加忘记密码处理方法
const handleForgotPassword = async () => {
  if (!email.value) {
    ElMessage.warning('Please enter your email address')
    return
  }

  try {
    const { error } = await supabase.auth.resetPasswordForEmail(email.value, {
      redirectTo: `${window.location.origin}/reset-password`
    })

    if (error) throw error

    ElMessage.success('Password reset link has been sent to your email')
    emit('close')
  } catch (error: any) {
    console.error('Reset password error:', error)
    ElMessage.error(error.message || 'Failed to send password reset email')
  }
}
</script> 