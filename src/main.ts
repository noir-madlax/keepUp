import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { inject } from '@vercel/analytics'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import { initAnalytics } from './utils/analytics'
import { RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from './stores/auth'

// 导入 tailwind 基础样式
import './assets/tailwind.css'
// 导入 markdown 样式
import './assets/markdown.css'
// 导入 element-plus 样式
import 'element-plus/dist/index.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)

// 2024-03-24 17:30: 在应用启动时预加载用户状态
const authStore = useAuthStore(pinia)
await authStore.loadUser()

app.use(router)
app.use(i18n)

// 添加全局路由守卫
router.beforeEach(async (to: RouteLocationNormalized, from: RouteLocationNormalized) => {
  // 确保用户状态已加载
  if (!authStore.isInitialized) {
    await authStore.loadUser()
  }
  console.log(`路由变化: 从 ${from.fullPath} 到 ${to.fullPath}`)
  return true
})

// 2024-03-20: 添加版本控制和缓存刷新机制
if (import.meta.env.PROD) {
  // 获取当前应用版本
  const currentVersion = document.querySelector('meta[name="app-version"]')?.getAttribute('content')

  // 检查本地存储的版本
  const storedVersion = localStorage.getItem('app-version')
  
  if (currentVersion !== storedVersion) {
    // 版本不匹配，执行缓存刷新
    console.log(`版本更新: ${storedVersion || '初始版本'} -> ${currentVersion}`)
    
    // 清理旧版本的缓存数据
    const clearCache = async () => {
      try {
        // 2024-03-21: 修复版本更新时登录态丢失的问题
        // 保护 Supabase 认证相关的数据
        const preserveKeys = [
          'auth-token', 
          'user-preferences',
          ...Object.keys(localStorage).filter(key => key.startsWith('sb-'))  // 保护所有 Supabase 相关的键
        ]

        // 清理 localStorage 中的非关键数据
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i)
          if (key && !preserveKeys.includes(key)) {
            localStorage.removeItem(key)
          }
        }

        // 清理 sessionStorage 中的非认证数据
        for (let i = 0; i < sessionStorage.length; i++) {
          const key = sessionStorage.key(i)
          if (key && !key.startsWith('sb-')) {  // 保留 Supabase 相关的 session 数据
            sessionStorage.removeItem(key)
          }
        }

        // 如果支持 Cache API，清理旧的缓存
        if ('caches' in window) {
          const cacheKeys = await caches.keys()
          await Promise.all(
            cacheKeys.map(key => caches.delete(key))
          )
        }

        // 更新存储的版本号
        localStorage.setItem('app-version', currentVersion || '')

        // 如果是版本更新（非首次访问），刷新页面以加载新资源
        if (storedVersion) {
          // 确保在清理完成后再刷新
          setTimeout(() => {
            window.location.reload()
          }, 100)
        }
      } catch (error) {
        console.error('清理缓存失败:', error)
      }
    }

    // 执行缓存清理
    clearCache()
  }
  
  // 添加缓存控制头
  const cacheControl = document.createElement('meta')
  cacheControl.httpEquiv = 'Cache-Control'
  cacheControl.content = 'no-cache, no-store, must-revalidate, max-age=0'
  document.head.appendChild(cacheControl)

  const pragma = document.createElement('meta')
  pragma.httpEquiv = 'Pragma'
  pragma.content = 'no-cache'
  document.head.appendChild(pragma)

  const expires = document.createElement('meta')
  expires.httpEquiv = 'Expires'
  expires.content = '0'
  document.head.appendChild(expires)
}

// 初始化 analytics
initAnalytics()

// 注入 Vercel Analytics
inject()

app.mount('#app')
