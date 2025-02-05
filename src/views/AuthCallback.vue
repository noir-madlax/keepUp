<template>
  <div class="flex items-center justify-center min-h-screen">
    <p>Signing in...</p>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { supabase } from '../supabaseClient'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  try {
    // First handle the auth state change
    const { data: { session }, error: sessionError } = await supabase.auth.getSession()
    if (sessionError) throw sessionError

    // Check if this is a password reset callback
    const type = new URLSearchParams(window.location.search).get('type')
    if (type === 'recovery') {
      // PKCE流程下不需要在此处理密码重置
      await router.push('/reset-password')
      return
    }

    // Set a timeout to ensure we don't stay on this page forever
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Authentication timeout')), 5000)
    })

    // Wait for supabase to handle auth callback
    const authPromise = authStore.handleAuthCallback()
    
    // Use Promise.race to ensure we don't wait forever
    await Promise.race([authPromise, timeoutPromise])
    
    console.log('Auth callback handled successfully, preparing to redirect')
    
    // Normal login flow, redirect to home page
    await router.push('/')
  } catch (error) {
    console.error('Auth handling error:', error)
    // On error, also redirect to home page
    await router.push('/')
  }
})
</script> 