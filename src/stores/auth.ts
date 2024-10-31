import { defineStore } from 'pinia'
import { supabase } from '../supabaseClient'
import type { User } from '../types/auth'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!user.value)

  async function setUser(userData: User | null) {
    user.value = userData
  }

  async function loadUser() {
    try {
      loading.value = true
      const { data: { user: userData } } = await supabase.auth.getUser()
      user.value = userData
    } catch (error) {
      console.error('Error loading user:', error)
    } finally {
      loading.value = false
    }
  }

  async function signInWithGithub() {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'github',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`
      }
    })
    if (error) throw error
  }

  async function signInWithGoogle() {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`
      }
    })
    if (error) throw error
  }

  async function signOut() {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    user.value = null
  }

  return {
    user,
    loading,
    isAuthenticated,
    setUser,
    loadUser,
    signInWithGithub,
    signInWithGoogle,
    signOut
  }
}) 