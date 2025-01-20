<template>
  <div 
    class="fixed bottom-0 left-0 right-0 bg-[#FFFFFF]"
    :class="[
      'transition-all duration-300 ease-in-out',
      { 'transition-none': isResizing }
    ]"
    :style="{
      height: chatStore.chatWindowState === 'expanded' ? `${windowHeight}px` : '105px',
      zIndex: '998',
      borderLeft: '1px solid #DDDDDD',
      borderTop: '1px solid #DDDDDD',
      borderBottom: '1px solid #DDDDDD',
      boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)'
    }"
  >
    <!-- 展开/收起按钮 - 始终显示在顶部 -->
    <div class="relative w-full bg-white" style="z-index: 999;">
      <!-- 拖拽条 - 仅在展开状态显示 -->
      <div 
        v-if="chatStore.chatWindowState === 'expanded'"
        class="absolute left-0 right-0 top-0 h-1 cursor-ns-resize bg-transparent"
        @mousedown="startResize"
      ></div>
      <button
        @click="toggleChatWindow"
        class="absolute left-1/2 -translate-x-1/2 -top-[0px] transition-opacity hover:opacity-100 opacity-90 bg-white rounded-t-lg px-2 "
        style="z-index: 998;"
        :title="chatStore.chatWindowState === 'expanded' ? '收起聊天' : '展开聊天'"
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          :class="[
            'w-10 h-4 transition-transform duration-300',
            chatStore.chatWindowState === 'expanded' ? 'rotate-180' : ''
          ]"
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          stroke-width="3.5"
        >
          <path d="M18 15l-6-6-6 6"/>
        </svg>
      </button>
    </div>

    <!-- 收起状态时的内容区域 -->
    <div 
      v-if="chatStore.chatWindowState === 'minimized'"
      class="border-0 w-full h-full cursor-pointer flex items-center justify-center text-gray-500 hover:bg-gray-50 transition-colors"
      @click="toggleChatWindow"
    >
    </div>

    <!-- 聊天内容区域 -->
    <div 
      v-if="chatStore.chatWindowState === 'expanded'"
      class="h-[calc(100%-60px-40px)] overflow-y-auto"
    >
      <!-- 聊天消息内容 -->
      <div 
        ref="messageListRef"
        class="messages-container pt-4 px-6"
        @wheel.prevent="handleChatScroll"
        @touchmove.prevent="handleChatScroll"
      >
        <!-- 1. 有消息时的显示 -->
        <template v-if="chatStore.currentSession?.messages?.length">
          <div
            v-for="(message, index) in chatStore.currentSession.messages"
            :key="message.id"
            :class="[
              'flex',
              message.role === 'assistant' ? 'justify-start' : 'justify-end',
              index !== chatStore.currentSession.messages.length - 1 ? 'mb-3' : ''
            ]"
          >
            <!-- 2024-03-21 16:00: 添加AI消息的logo -->
                         <!--max-w-[98%]是为了ai的聊天和用户聊天对齐 和输入框对齐 -->
            <template v-if="message.role === 'assistant'">
              <div class="flex items-start max-w-[98%]">
                <img 
                  src="/images/icons/logo.svg" 
                  alt="Keep Up Logo" 
                  class="w-[24px] h-[24px] mr-2 flex-shrink-0 mt-1" 
                />
                <div 
                  :class="[
                    'rounded-lg px-4 py-2 prose prose-sm',
                    'bg-gray-50 text-gray-800 border border-gray-200'
                  ]"
                  v-html="renderMarkdown(message.content)"
                >
                </div>
              </div>
            </template>
            <!-- 用户消息保持原样 -->
            <template v-else>
              <div class="flex items-start max-w-[95%]">
                <div 
                  :class="[
                    'rounded-lg px-4 py-2 prose prose-sm',
                    'bg-blue-600 text-white prose-invert'
                  ]"
                  v-html="renderMarkdown(message.content)"
                >
                </div>
                <!-- 2024-03-21 17:45: 使用与导航栏相同的用户头像获取方式 -->
                <img 
                  :src="authStore.user?.user_metadata?.avatar_url"
                  alt="User Avatar" 
                  class="w-[24px] h-[24px] ml-2 flex-shrink-0 mt-1 rounded-full" 
                />
              </div>
            </template>
          </div>
          
          <!-- 使用isAIInitialLoading来控制骨架屏 -->
          <div v-if="chatStore.isAIInitialLoading" class="flex justify-start">
            <div class="flex items-start max-w-[98%]">
              <!-- AI头像骨架屏 -->
              <div class="w-[24px] h-[24px] mr-2 flex-shrink-0 mt-1 rounded bg-gray-200 animate-pulse"></div>
              <div class="max-w-[80%] space-y-2 bg-gray-50 rounded-lg px-4 py-3 border border-gray-200 animate-pulse">
                <div class="h-2 bg-gray-200 rounded-full w-[180px]"></div>
                <div class="h-2 bg-gray-200 rounded-full w-[120px]"></div>
              </div>
            </div>
          </div>
        </template>

        <!-- 2. 初始化时的骨架屏 -->
        <div v-else-if="chatStore.isInitializing" class="space-y-4">
          <!-- 用户消息骨架屏 -->
          <div class="flex justify-end">
            <div class="flex items-start max-w-[95%]">
              <div class="max-w-[80%] space-y-2 bg-blue-100 rounded-lg px-4 py-3 animate-pulse">
                <div class="h-2 bg-blue-200 rounded-full w-[160px]"></div>
                <div class="h-2 bg-blue-200 rounded-full w-[100px]"></div>
              </div>
              <!-- 用户头像骨架屏 -->
              <div class="w-[24px] h-[24px] ml-2 flex-shrink-0 mt-1 rounded-full bg-blue-200 animate-pulse"></div>
            </div>
          </div>
          <!-- AI回复骨架屏 -->
          <div class="flex justify-start">
            <div class="flex items-start max-w-[98%]">
              <!-- AI头像骨架屏 -->
              <div class="w-[24px] h-[24px] mr-2 flex-shrink-0 mt-1 rounded bg-gray-200 animate-pulse"></div>
              <div class="max-w-[80%] space-y-2 bg-gray-50 rounded-lg px-4 py-3 border border-gray-200 animate-pulse">
                <div class="h-2 bg-gray-200 rounded-full w-[180px]"></div>
                <div class="h-2 bg-gray-200 rounded-full w-[120px]"></div>
              </div>
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
        <!--max-w-[98%]是为了ai的聊天和用户聊天对齐 和输入框对齐 -->
    <div 
      class="absolute bottom-0 left-0 right-0 bg-white px-11 py-3 mr-[-20px] "
      style="height: 59px;"
    >
      <form @submit.prevent="handleSubmit" class="relative flex items-center h-full">
        <input
          v-model="messageInput"
          type="text"
          :placeholder="$t('chat.input.placeholder')"
          class="w-full px-4 py-2 pr-12 mr-[24px] border border-[#D9D9D9] rounded-lg focus:outline-none focus:ring-1 focus:ring-[#BFBFBF] bg-white text-[#333333] text-base"
          :disabled="chatStore.isAIResponding"
        />
        <button
          type="button"
          class="absolute right-[32px] w-[32px] h-[32px] flex items-center justify-center hover:bg-gray-50 rounded-full transition-colors"
          :disabled="!messageInput.trim() && !chatStore.isAIResponding"
          @click="chatStore.isAIResponding ? handleAbort() : handleSubmit()"
        >
          <img 
            src="/images/icons/send.svg" 
            alt="Send" 
            class="w-[20px] h-[20px]"
            :class="chatStore.isAIResponding ? 'hidden' : ''"
          />
          <img 
            v-if="chatStore.isAIResponding"
            src="/images/icons/stop.svg" 
            alt="Stop" 
            class="w-[24px] h-[24px] stop-icon-wrapper"
          />
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, defineExpose } from 'vue'
import { useChatStore } from '../../stores/chat'
import { useAuthStore } from '../../stores/auth'
import { Loading, ArrowRight } from '@element-plus/icons-vue'
import { format } from 'date-fns'
import type { ChatSession } from '../../types/chat'
import { marked } from 'marked'

const chatStore = useChatStore()
const authStore = useAuthStore()
const messageInput = ref('')
const isMobile = computed(() => window.innerWidth < 768)
const selectedSessionId = ref('')

// 2024-01-21 15:10: 定义默认展开高度常量
const DEFAULT_EXPANDED_HEIGHT = 300 // 默认展开高度
const windowHeight = ref(DEFAULT_EXPANDED_HEIGHT)
const isResizing = ref(false)
const startY = ref(0)
const startHeight = ref(0)

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
  
  // 添加滚动事件监听
  messageListRef.value?.addEventListener('scroll', handleScroll)
})

const handleSubmit = async () => {
  if (!messageInput.value.trim()) return
  
  const content = messageInput.value
  messageInput.value = ''
  
  // 2024-01-22 17:30: 立即展开聊天窗口并设置初始化状态
  chatStore.chatWindowState = 'expanded'
  chatStore.isInitializing = true
  chatStore.isAIResponding = true
  
  try {
    await chatStore.sendMessage(content)
  } catch (error) {
    // 2024-01-22 17:30: 发生错误时重置状态
    chatStore.isInitializing = false
    chatStore.isAIResponding = false
    console.error('发送消息失败:', error)
  }
}

// 添加中止处理函数
const handleAbort = () => {
  chatStore.abortChat()
}

// 添加消息列表引用
const messageListRef = ref<HTMLElement | null>(null)

// 2024-01-21 17:00: 添加自动滚动标志位
const shouldAutoScroll = ref(true)

// 2024-01-21 17:00: 检查是否在底部
const isAtBottom = () => {
  if (!messageListRef.value) return true
  const { scrollTop, scrollHeight, clientHeight } = messageListRef.value
  // 添加一个小的容差值，因为有时候可能会有小数点的差异
  return Math.abs(scrollHeight - scrollTop - clientHeight) < 1
}

// 2024-01-21 17:00: 更新滚动到底部的工具函数
const scrollToBottom = (force: boolean = false) => {
  if (messageListRef.value && (shouldAutoScroll.value || force)) {
    setTimeout(() => {
      messageListRef.value!.scrollTop = messageListRef.value!.scrollHeight
    }, 0)
  }
}

// 2024-01-21 17:00: 监听滚动事件更新自动滚动标志位
const handleScroll = () => {
  shouldAutoScroll.value = isAtBottom()
}

// 监听消息变化
watch(
  () => chatStore.currentSession?.messages,
  () => {
    // 当有新消息时，根据 shouldAutoScroll 决定是否滚动
    scrollToBottom()
  },
  { deep: true }
)

// 添加滚动处理函数
const handleChatScroll = (event: WheelEvent | TouchEvent) => {
  // 确保事件不会传播到父元素
  event.stopPropagation()
  
  // 根据事件类型处理滚动
  if (event instanceof WheelEvent) {
    if (messageListRef.value) {
      // 手动控制滚动
      messageListRef.value.scrollTop += event.deltaY
      // 更新自动滚动标志
      shouldAutoScroll.value = isAtBottom()
    }
  } else if (event instanceof TouchEvent) {
    // 触摸事件的处理保持不变
    if (messageListRef.value) {
      shouldAutoScroll.value = isAtBottom()
    }
  }
}

// 开始调整大小
const startResize = (e: MouseEvent) => {
  isResizing.value = true
  startY.value = e.clientY
  startHeight.value = windowHeight.value
  
  // 添加事件监听
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
}

// 处理调整大小
const handleResize = (e: MouseEvent) => {
  if (!isResizing.value) return
  
  const deltaY = startY.value - e.clientY
  const newHeight = Math.min(500, Math.max(110, startHeight.value + deltaY))
  windowHeight.value = newHeight
}

// 停止调整大小
const stopResize = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
}

// 在组件卸载时清理事件监听
onUnmounted(() => {
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
  messageListRef.value?.removeEventListener('scroll', handleScroll)
})

// 修改切换聊天窗口状态的函数
const toggleChatWindow = () => {
  chatStore.chatWindowState = chatStore.chatWindowState === 'expanded' ? 'minimized' : 'expanded'
  if (chatStore.chatWindowState === 'expanded') {
    windowHeight.value = DEFAULT_EXPANDED_HEIGHT // 使用默认展开高度常量
  }
}

// 2024-03-21 14:30: 暴露scrollToBottom方法供外部调用
defineExpose({
  scrollToBottom
})

// 2024-03-21 15:30: 添加Markdown渲染函数
const renderMarkdown = (content: string) => {
  try {
    return marked(content)
  } catch (error) {
    console.error('Markdown渲染失败:', error)
    return content
  }
}
</script>

<style scoped>
/* 添加用户选择样式 */
.user-select-none {
  user-select: none;
}

/* 确保拖拽时鼠标样式保持一致 */
.cursor-ns-resize {
  cursor: ns-resize;
}

/* 保持过渡效果，但在调整大小时禁用 */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* 调整大小时禁用过渡效果 */
.resizing {
  transition: none !important;
}

/* 确保内容区域不会超出容器 */
.messages-container {
  height: 100%;
  overflow-y: auto;
  padding: 1rem;
  padding-bottom: 1rem;
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
  padding: 4px;
  transition: transform 0.2s ease-in-out;
}

.stop-icon-wrapper:hover {
  transform: scale(1.2);
}

@keyframes pulse {
  0% {
    opacity: 0.8;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.15);
  }
  100% {
    opacity: 0.8;
    transform: scale(1);
  }
}

.stop-icon-wrapper {
  animation: pulse 2s ease-in-out infinite;
}

/* 移除之前的过渡效果相关样式 */
.transition-none {
  transition: none !important;
}

.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* 移除之前的 resizing 类，因为我们现在使用 transition-none */

/* 2024-03-21 15:30: 添加Markdown样式 */
:deep(.prose) {
  max-width: none;
}

:deep(.prose p) {
  margin: 0.5em 0;
}

:deep(.prose strong) {
  font-weight: 600;
}

:deep(.prose ul),
:deep(.prose ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
}

:deep(.prose li) {
  margin: 0.25em 0;
}

:deep(.prose-invert) {
  color: white;
}

:deep(.prose-invert strong) {
  color: white;
}

:deep(.prose-invert a) {
  color: white;
  text-decoration: underline;
}

:deep(.prose pre) {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 0.5em;
  border-radius: 0.25em;
  overflow-x: auto;
}

:deep(.prose code) {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 0.2em 0.4em;
  border-radius: 0.25em;
}
</style> 