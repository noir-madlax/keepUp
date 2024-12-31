<template>
  <div 
    v-if="chatStore.isChatOpen"
    :class="[
      'fixed bg-white shadow-xl transition-transform duration-300 ease-in-out',
      isMobile 
        ? 'top-0 left-0 right-0 bottom-0 z-[1000]'
        : 'top-[71px] right-0 bottom-0 w-[400px] border-l'
    ]"
  >
    <!-- 头部 -->
    <div class="flex justify-between items-center px-4 py-3 border-b bg-white">
      <h3 class="text-lg font-medium">AI 助手</h3>
      <button 
        @click="chatStore.isChatOpen = false"
        class="p-1 hover:bg-gray-100 rounded-full"
      >
        <svg class="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>

    <!-- 消息列表 -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4" :class="{
      'h-[calc(100vh-180px)]': !isMobile,
      'h-[calc(100vh-120px)]': isMobile
    }">
      <template v-if="chatStore.currentSession?.messages.length">
        <div
          v-for="message in chatStore.currentSession.messages"
          :key="message.id"
          :class="[
            'flex',
            message.role === 'assistant' ? 'justify-start' : 'justify-end'
          ]"
        >
          <div 
            :class="[
              'max-w-[80%] rounded-lg px-4 py-2',
              message.role === 'assistant' 
                ? 'bg-gray-100 text-gray-800' 
                : 'bg-blue-500 text-white'
            ]"
          >
            {{ message.content }}
          </div>
        </div>
      </template>
      <div v-else class="text-center text-gray-500">
        开始对话...
      </div>
    </div>

    <!-- 输入框 -->
    <div class="border-t p-4">
      <div class="flex gap-2">
        <input
          v-model="inputMessage"
          type="text"
          placeholder="输入消息..."
          class="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          @keyup.enter="sendMessage"
        >
        <button
          @click="sendMessage"
          :disabled="!inputMessage.trim()"
          :class="[
            'px-4 py-2 rounded-lg transition-colors',
            inputMessage.trim() 
              ? 'bg-blue-500 text-white hover:bg-blue-600' 
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          ]"
        >
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useChatStore } from '../../stores/chat'

const chatStore = useChatStore()
const inputMessage = ref('')
const isMobile = computed(() => window.innerWidth <= 768)

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  
  await chatStore.sendMessage(inputMessage.value)
  inputMessage.value = ''
}
</script>

<style scoped>
.mobile-enter-active,
.mobile-leave-active {
  transition: transform 0.3s ease-in-out;
}

.mobile-enter-from,
.mobile-leave-to {
  transform: translateY(100%);
}
</style> 