<template>
  <div class="min-h-screen flex items-center justify-center">
    <div class="text-center">
      <h2 class="text-2xl font-bold mb-4">正在处理登录...</h2>
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { supabase } from '../supabaseClient'

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  try {
    const { data: { session }, error } = await supabase.auth.getSession()
    
    if (error) throw error
    
    if (session?.user) {
      await authStore.setUser(session.user)
      router.push('/')
    }
  } catch (error) {
    console.error('Auth callback error:', error)
    router.push('/')
  }
})
</script> 