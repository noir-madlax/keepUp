<template>
  <div class="flex h-screen bg-gray-100">
    <!-- 侧边栏 -->
    <div 
      class="bg-white shadow-md transition-all duration-300"
      :class="isCollapsed ? 'w-16' : 'w-64'"
    >
      <div class="p-4 border-b flex items-center justify-between">
        <h1 class="text-xl font-bold" :class="{ 'hidden': isCollapsed }">Keep Up 后台</h1>
        <button 
          @click="toggleSidebar"
          class="p-1 rounded hover:bg-gray-100"
        >
          <svg 
            class="w-5 h-5 text-gray-500"
            :class="{ 'transform rotate-180': isCollapsed }"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
            />
          </svg>
        </button>
      </div>
      <nav class="p-4">
        <router-link 
          to="/admin/requests" 
          class="block px-4 py-2 rounded hover:bg-blue-50 text-gray-700 flex items-center gap-2"
          :class="{ 
            'bg-blue-50': $route.path === '/admin/requests',
            'justify-center': isCollapsed
          }"
        >
          <svg 
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path 
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
          <span :class="{ 'hidden': isCollapsed }">文章请求管理</span>
        </router-link>
        <!-- 后续可以在这里添加更多菜单项 -->
      </nav>
    </div>

    <!-- 主内容区 -->
    <div class="flex-1 overflow-auto">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isCollapsed = ref(true) // 默认收起

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<style scoped>
/* 添加过渡动画 */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}
</style> 