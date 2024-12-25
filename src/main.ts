import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18n from './i18n'

// 导入 tailwind 基础样式
import './assets/tailwind.css'
// 导入 markdown 样式
import './assets/markdown.css'
// 导入 element-plus 样式
import 'element-plus/dist/index.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

// 添加全局路由守卫
router.beforeEach((to, from) => {
  console.log(`路由变化: 从 ${from.fullPath} 到 ${to.fullPath}`)
  return true
})

// 添加缓存控制
if (import.meta.env.PROD) {
  // 在生产环境下设置适当的缓存控制头
  const meta = document.createElement('meta')
  meta.httpEquiv = 'Cache-Control'
  meta.content = 'no-cache, no-store, must-revalidate'
  document.head.appendChild(meta)
  
  // 处理 cookie 和本地存储
  const clearBrowserData = async () => {
    // 清理不需要持久化的数据
    // const preserveKeys = ['auth-token', 'user-preferences']  // 需要保留的关键数据
    // for (let i = 0; i < localStorage.length; i++) {
    //   const key = localStorage.key(i)
    //   if (key && !preserveKeys.includes(key)) {
    //     localStorage.removeItem(key)
    //   }
    // }
    
    // 清理过期的 sessionStorage
    sessionStorage.clear()
  }
  
  // 在页面加载时执行清理
  window.addEventListener('load', clearBrowserData)
}

app.mount('#app')
