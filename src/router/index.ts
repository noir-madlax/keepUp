import { createRouter, createWebHistory } from 'vue-router'
import { defineAsyncComponent } from 'vue'
import HomeView from '../views/HomeView.vue'
import AdminLayout from '../views/admin/AdminLayout.vue'
import RequestsView from '../views/admin/RequestsView.vue'
import ArticleView from '../views/ArticleView.vue'
import AuthCallback from '../views/AuthCallback.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
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
  next()
})

export default router
