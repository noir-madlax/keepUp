<template>
  <div 
    class="fixed bottom-0 left-0 right-0 transition-all duration-300 ease-in-out bg-white shadow-lg border border-gray-200"
    :class="{
      'h-[70px]': chatStore.chatWindowState === 'minimized',
      'h-[400px]': chatStore.chatWindowState === 'expanded'
    }"
    style="z-index: 998;"
  >
    <!-- 展开/收起按钮 - 放在中间顶部 -->
    <button
      @click="toggleChatWindow"
      class="absolute left-1/2 -translate-x-1/2 -top-2 p-1 rounded-t-lg bg-white shadow-md hover:bg-gray-50 transition-colors"
      :title="chatStore.chatWindowState === 'expanded' ? '收起聊天' : '展开聊天'"
    >
      <div class="w-12 h-3 flex items-center justify-center">
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          :class="[
            'w-4 h-4 transition-transform duration-300',
            chatStore.chatWindowState === 'expanded' ? 'rotate-180' : ''
          ]"
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          stroke-width="2"
        >
          <path d="M18 15l-6-6-6 6"/>
        </svg>
      </div>
    </button>

    <!-- 聊天内容区域 -->
    <div 
      v-if="chatStore.chatWindowState === 'expanded'"
      class="h-[calc(100%-60px)] overflow-y-auto"
    >
      <!-- 聊天消息内容 -->
      <div class="messages-container">
        <!-- 1. 有消息时的显示 -->
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
          
          <!-- 使用isAIInitialLoading来控制骨架屏 -->
          <div v-if="chatStore.isAIInitialLoading" class="flex justify-start">
            <div class="max-w-[80%] space-y-2 bg-gray-50 rounded-lg px-4 py-3 border border-gray-200 animate-pulse">
              <div class="h-2 bg-gray-200 rounded-full w-[180px]"></div>
              <div class="h-2 bg-gray-200 rounded-full w-[120px]"></div>
            </div>
          </div>
        </template>

        <!-- 2. 初始化时的骨架屏 -->
        <div v-else-if="chatStore.isInitializing" class="space-y-4">
          <div class="flex justify-end">
            <div class="max-w-[80%] space-y-2 bg-blue-100 rounded-lg px-4 py-3 animate-pulse">
              <div class="h-2 bg-blue-200 rounded-full w-[160px]"></div>
              <div class="h-2 bg-blue-200 rounded-full w-[100px]"></div>
            </div>
          </div>
        </div>

        <!-- 3. 空状态提示 -->
        <div v-else class="text-center text-gray-500">
          {{ $t('chat.window.startChat') }}
        </div>
      </div>
    </div>

    <!-- 输入框区域 -->
    <div 
      class="absolute bottom-0 left-0 right-0 bg-white p-4"
      style="height: 60px;"
    >
      <form @submit.prevent="chatStore.isAIResponding ? handleAbort() : handleSubmit()" class="flex gap-2">
        <input
          v-model="messageInput"
          type="text"
          :placeholder="$t('chat.input.placeholder')"
          class="flex-1 px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          :disabled="chatStore.isAIResponding"
        />
        <button
          type="submit"
          class="relative px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium min-w-[80px] overflow-hidden transition-all duration-200"
          :disabled="!messageInput.trim()"
        >
          <div 
            class="flex items-center justify-center gap-1"
            :class="[chatStore.isAIResponding ? 'opacity-0' : 'opacity-100']"
          >
            <span>{{ $t('chat.window.send') }}</span>
            <el-icon class="text-lg">
              <ArrowRight />
            </el-icon>
          </div>

          <div 
            v-if="chatStore.isAIResponding"
            class="absolute inset-0 flex items-center justify-center bg-white hover:bg-gray-50 cursor-pointer rounded-lg"
          >
            <div class="stop-icon-wrapper">
              <img 
                src="/images/icons/stop.svg" 
                alt="Stop" 
                class="w-8 h-8"
              />
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

const chatStore = useChatStore()
const messageInput = ref('')
const isMobile = computed(() => window.innerWidth < 768)
const selectedSessionId = ref('')
const windowHeight = ref(400)

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
  if (!messageInput.value.trim()) return
  
  const content = messageInput.value
  messageInput.value = ''
  
  await chatStore.sendMessage(content)
}

// 添加中止处理函数
const handleAbort = () => {
  chatStore.abortChat()
}

// 添加消息列表引用
const messageListRef = ref<HTMLElement | null>(null)

// 添加滚动处理函数
const handleChatScroll = (event: WheelEvent | TouchEvent) => {
  if (!messageListRef.value) return
  
  const container = messageListRef.value
  const isAtBottom = container.scrollHeight - container.scrollTop === container.clientHeight
  const isAtTop = container.scrollTop === 0
  
  // 如果是触摸事件
  if (event.type === 'touchmove') {
    event.stopPropagation()
    return
  }
  
  // 如果是滚轮事件
  const wheelEvent = event as WheelEvent
  const deltaY = wheelEvent.deltaY
  
  // 在顶部向上滚动或底部向下滚动时阻止事件传播
  if ((isAtTop && deltaY < 0) || (isAtBottom && deltaY > 0)) {
    event.preventDefault()
  }
}

// 切换聊天窗口状态
const toggleChatWindow = () => {
  chatStore.chatWindowState = chatStore.chatWindowState === 'expanded' ? 'minimized' : 'expanded'
}
</script>

<style scoped>
/* 保持过渡效果 */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* 确保内容区域不会超出容器 */
.messages-container {
  height: 100%;
  overflow-y: auto;
  padding: 1rem;
}

/* 自定义滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: transparent;
}

.messages-container::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background-color: rgba(156, 163, 175, 0.8);
}

/* Stop图标动画效果 */
.stop-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 6px;
  transition: transform 0.2s ease-in-out;
}

.stop-icon-wrapper:hover {
  transform: scale(1.15);
}

@keyframes pulse {
  0% {
    opacity: 0.7;
    transform: scale(0.95);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
  100% {
    opacity: 0.7;
    transform: scale(0.95);
  }
}

.stop-icon-wrapper {
  animation: pulse 1.5s ease-in-out infinite;
}
</style> 