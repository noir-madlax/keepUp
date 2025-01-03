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
        <h3 class="text-lg font-medium">AI 助手</h3>
        <!-- 添加会话选择下拉框 -->
        <el-select 
          v-model="selectedSessionId" 
          size="small" 
          placeholder="选择会话"
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
      <button 
        @click="chatStore.isChatOpen = false"
        class="p-2 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100"
      >
        <span class="sr-only">Close</span>
        <svg class="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </button>
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
      <div v-else-if="chatStore.isLoading" class="text-center text-gray-500">
        <el-icon class="animate-spin mr-2">
          <Loading />
        </el-icon>
        加载中...
      </div>
      <div v-else class="text-center text-gray-500">
        开始对话...
      </div>
    </div>

    <!-- 输入框 -->
    <div class="p-4 border-t bg-gray-50">
      <form @submit.prevent="handleSubmit" class="flex gap-2">
        <input
          v-model="messageInput"
          type="text"
          placeholder="输入消息..."
          class="flex-1 px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          :disabled="chatStore.isLoading"
        />
        <button
          type="submit"
          class="px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
          :disabled="!messageInput.trim() || chatStore.isLoading"
        >
          <el-icon v-if="chatStore.isLoading" class="animate-spin">
            <Loading />
          </el-icon>
          <span v-else>发送</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useChatStore } from '../../stores/chat'
import { Loading } from '@element-plus/icons-vue'
import { format } from 'date-fns'
import type { ChatSession } from '../../types/chat'

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
</style> 