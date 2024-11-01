import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '../supabaseClient'
import type { User } from '@supabase/supabase-js'
import type { Provider } from '@supabase/supabase-js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = computed(() => !!user.value)

  const loadUser = async () => {
    try {
      const { data: { user: currentUser } } = await supabase.auth.getUser()
      console.log('Loaded user:', currentUser)
      user.value = currentUser
    } catch (error) {
      console.error('Error loading user:', error)
      user.value = null
    }
  }

  const signInWithOAuth = async (provider: Provider) => {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      })

      if (error) throw error
      return data
    } catch (error) {
      console.error('OAuth sign in error:', error)
      throw error
    }
  }

  const signInWithGithub = () => {
    return signInWithOAuth('github')
  }

  const signInWithGoogle = () => {
    return signInWithOAuth('google')
  }

  // 在用户登录时更新用户信息
  supabase.auth.onAuthStateChange((event, session) => {
    console.log('Auth state changed:', event, session?.user)
    user.value = session?.user || null
  })

  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    user.value = null
  }

  return {
    user,
    isAuthenticated,
    loadUser,
    signInWithGithub,
    signInWithGoogle,
    signOut
  }
}) 