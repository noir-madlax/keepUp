<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-r from-blue-50 to-indigo-50">
    <div class="text-center p-8 max-w-2xl">
      <h1 class="text-4xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
        Team 3PO
      </h1>
      <p class="text-xl text-gray-700 leading-relaxed">
        We are Team 3PO, FROM MIT.<br/>
        Our app is under development, stay tuned.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
// 2024-03-25: 创建3PO团队页面
</script>

<style scoped>
/* 添加渐变动画 */
h1 {
  animation: gradientFlow 3s ease infinite;
}

@keyframes gradientFlow {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
</style> 