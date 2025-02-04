<template>
  <div 
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center login-modal"
    @click="allowClose && $emit('close')"
  >
    <div 
      class="bg-white p-6 rounded-lg shadow-lg w-[400px]"
      @click.stop
    >
      <div class="text-center mb-6">
        <h2 class="text-2xl font-bold">Sign In</h2>
        <p class="text-gray-600 mt-2">Sign in or create an account</p>
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
            type="password" 
            v-model="password"
            placeholder="Password"
            class="w-full px-4 py-2 border rounded"
            required
            @focus="showPasswordRules = true"
            @blur="showPasswordRules = false"
          />
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
            Or continue with
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

const props = defineProps<{
  allowClose?: boolean
}>()

const authStore = useAuthStore()
const emit = defineEmits(['close', 'success'])

// 邮箱登录相关状态
const email = ref('')
const password = ref('')
const showPasswordRules = ref(false)

// 邮箱登录处理方法
const handleEmailAuth = async () => {
  try {
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
    ElMessage.error(error.message)
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
</script> 