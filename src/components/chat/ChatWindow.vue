<template>
  <div class="chat-window fixed right-0 bg-white shadow-lg flex flex-col" 
    :class="[
      isMobile ? 'w-full' : 'w-[420px]',  // 移动端全宽，桌面端固定宽度
      'top-[71px]',  // 从导航栏下方开始
      'bottom-0',    // 延伸到底部
      'border-l'     // 左侧添加边框
    ]"
  >
    <!-- 标题栏 -->
    <div class="flex justify-between items-center p-4 border-b">
      <div class="flex items-center gap-2">
        <h3 class="text-lg font-medium">{{ $t('chat.window.title') }}</h3>
        <!-- 添加会话选择下拉框 -->
        <el-select 
          v-model="selectedSessionId" 
          size="small" 
          :placeholder="$t('chat.window.sessionSelect')"
          class="w-48"
          @change="handleSessionChange"
        >
          <el-option
            v-for="session in chatStore.sessions"
            :key="session.id"
            :label="formatSessionLabel(session)"
            :value="session.id"
          />
        </el-select>
      </div>
      <CloseButton @click="handleClose" />
    </div>

    <!-- 消息列表 减去导航栏高度和其他元素高度 -->
    <div 
      class="flex-1 overflow-y-auto p-4 space-y-4" 
      style="height: calc(100vh - 71px - 130px);"  
    >
      <template v-if="chatStore.currentSession?.messages?.length">
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
                ? 'bg-gray-50 text-gray-800 border border-gray-200' 
                : 'bg-blue-600 text-white'
            ]"
          >
            {{ message.content }}
          </div>
        </div>
      </template>
      <div v-else-if="chatStore.isInitializing" class="space-y-4 animate-pulse">
        <!-- AI消息骨架 -->
        <div class="flex justify-start">
          <div class="max-w-[80%] space-y-2 bg-gray-50 rounded-lg px-4 py-3 border border-gray-200">
            <div class="h-2 bg-gray-200 rounded-full w-[180px]"></div>
            <div class="h-2 bg-gray-200 rounded-full w-[120px]"></div>
          </div>
        </div>
        
        <!-- 用户消息骨架 -->
        <div class="flex justify-end">
          <div class="max-w-[80%] space-y-2 bg-blue-100 rounded-lg px-4 py-3">
            <div class="h-2 bg-blue-200 rounded-full w-[160px]"></div>
            <div class="h-2 bg-blue-200 rounded-full w-[100px]"></div>
          </div>
        </div>

        <!-- AI第二条消息骨架 -->
        <div class="flex justify-start">
          <div class="max-w-[80%] space-y-2 bg-gray-50 rounded-lg px-4 py-3 border border-gray-200">
            <div class="h-2 bg-gray-200 rounded-full w-[200px]"></div>
            <div class="h-2 bg-gray-200 rounded-full w-[140px]"></div>
          </div>
        </div>
      </div>
      <div v-else class="text-center text-gray-500">
        {{ $t('chat.window.startChat') }}
      </div>
    </div>

    <!-- 输入框 -->
    <div class="p-4 border-t bg-gray-50">
      <form @submit.prevent="handleSubmit" class="flex gap-2">
        <input
          v-model="messageInput"
          type="text"
          :placeholder="$t('chat.input.placeholder')"
          class="flex-1 px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          :disabled="chatStore.isLoading"
        />
        <button
          type="submit"
          class="relative px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium min-w-[80px] overflow-hidden transition-all duration-200"
          :disabled="!messageInput.trim() || chatStore.isLoading"
        >
          <div class="flex items-center justify-center gap-1"
               :class="[chatStore.isLoading ? 'opacity-0' : 'opacity-100']"
               style="transition: opacity 0.2s ease-in-out">
            <span>{{ $t('chat.window.send') }}</span>
            <el-icon class="text-lg">
              <ArrowRight />
            </el-icon>
          </div>

          <div v-if="chatStore.isLoading" 
               class="absolute inset-0 flex items-center justify-center bg-blue-600"
               style="transition: all 0.2s ease-in-out">
            <div class="relative w-5 h-5">
              <div class="absolute inset-0 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <div class="absolute inset-1 border-2 border-white border-b-transparent rounded-full animate-spin-reverse"></div>
            </div>
          </div>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useChatStore } from '../../stores/chat'
import { Loading, ArrowRight } from '@element-plus/icons-vue'
import { format } from 'date-fns'
import type { ChatSession } from '../../types/chat'
import CloseButton from '../common/CloseButton.vue'

const chatStore = useChatStore()
const messageInput = ref('')
const isMobile = computed(() => window.innerWidth < 768)
const selectedSessionId = ref('')

// 格式化会话标签
const formatSessionLabel = (session: ChatSession) => {
  const date = format(new Date(session.created_at), 'MM-dd HH:mm')
  const content = session.mark_content?.substring(0, 15) + '...'
  return `${date} - ${content}`
}

// 处理会话切换
const handleSessionChange = async (sessionId: string) => {
  if (sessionId) {
    await chatStore.loadSession(sessionId)
  }
}

// 在组件挂载时加载会话列表
onMounted(async () => {
  await chatStore.loadSessions()
  // 如果有当前会话，设置为选中
  if (chatStore.currentSession) {
    selectedSessionId.value = chatStore.currentSession.id
  }
})

// 2024-01-10: 添加关闭处理函数，同时处理 chat 窗口和 toolbar 的状态
const handleClose = () => {
  chatStore.isChatOpen = false
  chatStore.hideToolbar()  // 同时隐藏 toolbar
}

const handleSubmit = async () => {
  if (!messageInput.value.trim() || chatStore.isLoading) return
  
  const content = messageInput.value
  messageInput.value = ''
  
  await chatStore.sendMessage(content)
}
</script>

<style scoped>
.chat-window {
  z-index: 998;  /* 确保在导航栏下方 */
}

/* 美化滚动条 */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}

/* 2024-01-10 22:45: 添加反向旋转动画 */
@keyframes spin-reverse {
  from {
    transform: rotate(360deg);
  }
  to {
    transform: rotate(0deg);
  }
}

.animate-spin-reverse {
  animation: spin-reverse 1s linear infinite;
}
</style> 