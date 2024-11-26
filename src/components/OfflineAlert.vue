<template>
  <div 
    v-if="isOffline"
    class="fixed top-0 left-0 right-0 bg-red-500 text-white p-2 text-center"
  >
    您当前处于离线状态
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const isOffline = ref(!navigator.onLine)

const handleOnline = () => {
  isOffline.value = false
}

const handleOffline = () => {
  isOffline.value = true
}

onMounted(() => {
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
})

onUnmounted(() => {
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
})
</script> 