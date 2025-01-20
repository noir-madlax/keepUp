import { createRouter, createWebHistory } from 'vue-router'
import { defineAsyncComponent } from 'vue'
import HomeView from '../views/HomeView.vue'
import AdminLayout from '../views/admin/AdminLayout.vue'
import RequestsView from '../views/admin/RequestsView.vue'
import ArticleView from '../views/ArticleView.vue'
import AuthCallback from '../views/AuthCallback.vue'
import { trackEvent } from '@/utils/analytics'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
      meta: {
        keepAlive: true
      }
    },
    {
      path: '/article/:id',
      name: 'article',
      component: () => import('../views/ArticleView.vue'),
      props: true,
      beforeEnter: (to, from, next) => {
        import('../views/ArticleView.vue')
        next()
      }
    },
    {
      path: '/admin',
      component: AdminLayout,
      children: [
        {
          path: 'requests',
          name: 'admin-requests',
          component: RequestsView
        }
        // 后续可以在这里添加更多后台路由
      ]
    },
    {
      path: '/auth/callback',
      name: 'auth-callback',
      component: AuthCallback
    }
  ]
})

router.beforeEach((to, from, next) => {
  if (to.name === 'home') {
    import('../views/ArticleView.vue')
  }
  console.log(`路由变化: 从 ${from.fullPath} 到 ${to.fullPath}`)
  
  // 添加页面访问追踪
  trackEvent('page_view', {
    path: to.fullPath,
    title: to.meta.title || to.name,
    from: from.fullPath
  })
  
  next()
})

export default router
