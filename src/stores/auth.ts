import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '../supabaseClient'
import type { User } from '@supabase/supabase-js'
import type { Provider } from '@supabase/supabase-js'
import { identifyUser, updateUserProperties } from '@/utils/analytics'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = computed(() => !!user.value)
  const isInitialized = ref(false)

  const loadUser = async () => {
    try {
      // 2024-12-15: 修复登录状态检查问题
      // 只有当「已初始化」且「用户已存在」时才跳过，避免 onAuthStateChange 未触发时误判为未登录
      if (isInitialized.value && user.value) {
        return
      }

      // 2024-03-24: 检查 localStorage 中是否有有效的 token
      const hasToken = Object.keys(localStorage).some(key => 
        key.startsWith('sb-') && 
        key.includes('auth-token')
      )

      if (!hasToken) {
        console.log('[loadUser] No valid token found in localStorage')
        user.value = null
        isInitialized.value = true
        return
      }

      // 获取 session
      const { data: { session } } = await supabase.auth.getSession()
      
      if (session?.user) {
        user.value = session.user
        // 加载用户信息后设置用户身份
        identifyUser(user.value.id, {
          email: user.value.email,
          name: user.value.user_metadata?.full_name
        })
      } else {
        console.log('[loadUser] No valid session found')
        user.value = null
      }
    } catch (error) {
      console.error('[loadUser] Error:', error)
      user.value = null
    } finally {
      isInitialized.value = true
    }
  }

  const signInWithOAuth = async (provider: Provider) => {
    try {
      // 保存当前页面路径，用于登录后返回
      const currentPath = window.location.pathname + window.location.search
      if (currentPath !== '/' && currentPath !== '/auth/callback') {
        localStorage.setItem('authRedirectUrl', currentPath)
      }
      
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
    try {
      console.log('[signOut] Starting signout process')
      
      // 1. 先清理 localStorage 中的 Supabase token
      const supabaseKeys = Object.keys(localStorage).filter(key => key.startsWith('sb-'))
      supabaseKeys.forEach(key => {
        console.log(`[signOut] Removing localStorage key: ${key}`)
        localStorage.removeItem(key)
      })

      // 2. 调用 Supabase 登出
      const { error } = await supabase.auth.signOut()
      if (error) {
        if (error.message?.includes('Auth session missing')) {
          console.log('[signOut] Session already missing, cleaning up state')
          user.value = null
          return
        }
        throw error
      }
      
      // 3. 清理前端状态
      user.value = null
      
      // 4. 重置初始化状态，确保下次需要重新加载用户信息
      isInitialized.value = false
      
      console.log('[signOut] Signout completed successfully')
    } catch (error) {
      console.error('[signOut] Error:', error)
      // 即使出错也要清理状态
      user.value = null
      isInitialized.value = false
      throw error
    }
  }

  const handleAuthCallback = async () => {
    try {
      const { data: { session }, error } = await supabase.auth.getSession()
      if (error) throw error
      
      if (session) {
        user.value = session.user
        console.log('Callback: 用户会话获取成功', session.user)
        // 登录成功后设置用户身份
        identifyUser(session.user.id, {
          email: session.user.email,
          name: session.user.user_metadata?.full_name,
          login_time: new Date().toISOString()
        })
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
    isInitialized,
    loadUser,
    signInWithGithub,
    signInWithGoogle,
    signOut,
    handleAuthCallback
  }
}) 