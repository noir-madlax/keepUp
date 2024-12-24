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
      // 1. 先获取 session
      const { data: { session } } = await supabase.auth.getSession()
      
      if (session?.user) {
        // 2. 如果 session 中有用户信息，直接使用
        user.value = session.user
      } else {
        // 3. 没有 session 才调用 getUser
        const { data: { user: currentUser } } = await supabase.auth.getUser()
        user.value = currentUser
      }
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

  const handleAuthCallback = async () => {
    try {
      const { data: { session }, error } = await supabase.auth.getSession()
      if (error) throw error
      
      if (session) {
        user.value = session.user
        console.log('Callback: 用户会话获取成功', session.user)
      } else {
        console.log('Callback: 没有获取到用户会话')
      }
      
      return session
    } catch (error) {
      console.error('Callback 处理错误:', error)
      throw error
    }
  }

  return {
    user,
    isAuthenticated,
    loadUser,
    signInWithGithub,
    signInWithGoogle,
    signOut,
    handleAuthCallback
  }
}) 