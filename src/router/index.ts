import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AdminLayout from '../views/admin/AdminLayout.vue'
import RequestsView from '../views/admin/RequestsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
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
    }
  ]
})

export default router
