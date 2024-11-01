import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import HomeView from '../views/HomeView.vue'
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
      component: ArticleView
    },
    {
      path: '/auth/callback',
      name: 'auth-callback',
      component: AuthCallback
    }
  ]
})

export default router
