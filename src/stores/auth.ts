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

  // 添加处理回调的方法
  const handleAuthCallback = async () => {
    try {
      // 先等待 Supabase 处理 URL 中的认证参数
      const { error: callbackError } = await supabase.auth.getSession()
      if (callbackError) throw callbackError

      // 然后获取 session
      const { data: { session }, error } = await supabase.auth.getSession()
      if (error) throw error
      
      console.log('Callback session:', session) // 添加日志
      
      if (session) {
        user.value = session.user
        return true
      }
      return false
    } catch (error) {
      console.error('处理认证回调失败:', error)
      throw error
    }
  }

  // 添加初始化方法
  const init = async () => {
    try {
      // 获取初始会话状态
      const { data: { session } } = await supabase.auth.getSession()
      user.value = session?.user || null
      
      // 设置认证状态变化监听
      supabase.auth.onAuthStateChange((event, session) => {
        console.log('Auth state changed:', event, session?.user)
        user.value = session?.user || null
      })
    } catch (error) {
      console.error('Auth initialization error:', error)
    }
  }

  // 在 store 创建时立即初始化
  init()

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