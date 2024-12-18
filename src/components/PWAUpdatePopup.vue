<template>
  <div v-if="needRefresh" class="fixed bottom-0 right-0 m-4 p-4 bg-white rounded-lg shadow-lg">
    <p class="text-gray-700 mb-2">有新版本可用</p>
    <div class="flex gap-2">
      <button 
        @click="updateServiceWorker"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        更新
      </button>
      <button 
        @click="close"
        class="px-4 py-2 border rounded hover:bg-gray-50"
      >
        关闭
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { registerSW } from 'virtual:pwa-register'

const needRefresh = ref(false)

let updateSW: (() => Promise<void>) | undefined

onMounted(() => {
  updateSW = registerSW({
    onNeedRefresh() {
      needRefresh.value = true
    },
    immediate: true,
    onRegisteredSW(swUrl, r) {
      r?.update()
      
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        window.location.reload()
      })
    }
  })
})

const updateServiceWorker = async () => {
  if (updateSW) {
    await caches.keys().then(keys => {
      return Promise.all(
        keys.map(key => caches.delete(key))
      )
    })
    
    await updateSW()
  }
}

const close = () => {
  needRefresh.value = false
}
</script> 