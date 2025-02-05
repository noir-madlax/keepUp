<template>
  <!-- 2024-03-24 17:00: 添加variant支持，区分不同场景的loading样式 -->
  <div 
    :class="[
      'fixed flex items-center justify-center',
      variant === 'modal' 
        ? 'inset-0 z-[1002]' // modal场景下覆盖整个区域
        : 'top-[90px] bottom-[60px] left-0 right-0 z-[999]' // 文章页面场景
    ]"
  >
    <!-- 背景遮罩 - modal场景使用不透明背景 -->
    <div 
      :class="[
        'absolute inset-0',
        variant === 'modal' ? 'bg-white' : 'bg-white/80'
      ]"
    ></div>
    <!-- loading内容 -->
    <div class="relative flex items-center gap-3 px-6 py-3 bg-white rounded-lg shadow-lg">
      <div class="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      <span class="text-gray-600 text-sm font-medium">Loading...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
// 定义组件属性
defineProps<{
  variant?: 'default' | 'modal' // 添加variant属性来控制不同场景的样式
}>()
</script> 