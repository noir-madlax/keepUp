<template>
  <div 
    :class="[
      'chat-window',
      'transition-all duration-300 ease-in-out',
      { 'transition-none': isResizing }
    ]"
    :style="getChatWindowStyle()"
  >
    <!-- 展开/收起按钮 - 始终显示在顶部 -->
    <div class="relative w-full bg-white" style="z-index: 999;">
      <!-- 桌面端拖拽条 - 仅在展开状态显示 -->
      <div 
        v-if="chatStore.chatWindowState === 'expanded' && !isMobile"
        class="absolute left-0 right-0 top-0 h-1 cursor-ns-resize bg-transparent"
        @mousedown="startResize"
      ></div>
      
      <!-- 桌面端收起状态的展开按钮 -->
      <button
        v-if="!isMobile"
        @click="toggleChatWindow"
        :class="[
          'desktop-toggle-btn',
          chatStore.chatWindowState === 'minimized' ? 'minimized' : 'expanded'
        ]"
        :title="chatStore.chatWindowState === 'expanded' ? '收起聊天' : '展开聊天'"
      >
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
          <path d="M15 18l-6-6 6-6"/>
        </svg>
        <span v-if="chatStore.chatWindowState === 'minimized'" class="toggle-text">Chat</span>
      </button>
      
      <!-- 移动端拖拽按钮 - 保持原有样式 -->
      <button
        v-if="isMobile"
        @click="toggleChatWindow"
        class="absolute left-1/2 -translate-x-1/2 -top-[0px] transition-opacity hover:opacity-100 opacity-90 bg-white rounded-t-lg px-2"
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

    <!-- 收起状态时的展开按钮 -->
    <div 
      v-if="chatStore.chatWindowState === 'minimized' && !isMobile"
      class="w-full h-full bg-gradient-to-b from-blue-50 to-blue-100 hover:from-blue-100 hover:to-blue-200 transition-all duration-200 cursor-pointer relative group border-l border-blue-200 flex items-center justify-center"
      @click="toggleChatWindow"
      title="展开聊天"
    >
      <!-- 聊天图标和文字 - 垂直布局 -->
      <div class="flex flex-col items-center space-y-2">
        <!-- 聊天图标 -->
        <div class="p-2 bg-white rounded-full shadow-sm border border-blue-200 group-hover:shadow-md group-hover:scale-105 transition-all duration-200">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.955 8.955 0 01-3.774-.9L3 21l1.9-6.226A8.955 8.955 0 013 12a8 8 0 018-8c4.418 0 8 3.582 8 8z" />
          </svg>
        </div>
        
        <!-- 垂直文字提示 -->
        <div class="transform -rotate-90 text-xs font-medium text-blue-700 whitespace-nowrap">
          开启对话
        </div>
      </div>
    </div>

    <!-- 聊天内容区域 -->
    <div 
      v-if="chatStore.chatWindowState === 'expanded'"
      class="flex-1 overflow-hidden flex flex-col"
    >
      <!-- 聊天消息内容 -->
      <div 
        ref="messageListRef"
        class="flex-1 overflow-y-auto pt-2 px-4 pb-1 min-h-0"
        @wheel.prevent="handleChatScroll"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
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
            <!-- AI消息 -->
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
            <!-- 用户消息 -->
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
                <img 
                  :src="authStore.user?.user_metadata?.avatar_url || '/images/icons/avatar.svg'" 
                  alt="User Avatar" 
                  class="w-[24px] h-[24px] ml-2 flex-shrink-0 mt-1 rounded-full" 
                />
              </div>
            </template>
          </div>
          
          <!-- AI初始加载骨架屏 -->
          <div v-if="chatStore.isAIInitialLoading" class="flex justify-start mt-3">
            <div class="flex items-start max-w-[98%]">
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
              <div class="w-[24px] h-[24px] ml-2 flex-shrink-0 mt-1 rounded-full bg-blue-200 animate-pulse"></div>
            </div>
          </div>
          <!-- AI回复骨架屏 -->
          <div class="flex justify-start">
            <div class="flex items-start max-w-[98%]">
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

      <!-- ChatToolbar区域 - 固定在聊天内容下方，输入框上方 -->
      <div class="flex-shrink-0 bg-gray-50 border-t border-gray-200 px-3 py-1">
        <ChatToolbar 
          @refresh-anchors="handleRefreshAnchors" 
          :disabled="false"
          @scroll-to-bottom="handleScrollToBottom"
        />
      </div>
    </div>

    <!-- 输入框区域 - 只在展开状态显示 -->
    <div 
      v-if="chatStore.chatWindowState === 'expanded'"
      class="flex-shrink-0 bg-white border-t border-gray-200 p-3"
    >
      <form @submit.prevent="handleSubmit" class="relative flex items-center h-full">
        <input
          v-model="messageInput"
          type="text"
          :placeholder="$t('chat.input.placeholder')"
          :class="[
            'chat-input',
            { 'mobile-chat-input': isMobile }
          ]"
          :disabled="chatStore.isAIResponding"
        />
        <button
          type="button"
          :class="[
            'chat-send-btn',
            { 'mobile-send-btn': isMobile }
          ]"
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
import { format } from 'date-fns'
import type { ChatSession } from '../../types/chat'
import { marked } from 'marked'
import ChatToolbar from './ChatToolbar.vue'

const chatStore = useChatStore()
const authStore = useAuthStore()
const messageInput = ref('')
const selectedSessionId = ref('')

// 添加移动端检测
const isMobile = computed(() => window.innerWidth < 768)

// 2024-01-21 15:10: 定义默认展开高度常量
const DEFAULT_EXPANDED_HEIGHT = 300
const windowHeight = ref(DEFAULT_EXPANDED_HEIGHT)

// 计算移动端合适的聊天窗口高度
const getMobileHeight = () => {
  const vh = window.innerHeight
  // 移动端使用视口高度的50%，但至少280px，最多不超过500px
  return Math.min(180, Math.max(100, vh * 0.3))
}
const isResizing = ref(false)
const startY = ref(0)
const startHeight = ref(0)

// 计算chat窗口样式
const getChatWindowStyle = () => {
  const mobile = isMobile.value
  const isExpanded = chatStore.chatWindowState === 'expanded'
  
  if (mobile) {
    // 移动端：保持底部布局，使用动态高度计算
    const mobileHeight = isExpanded ? getMobileHeight() : 60
    return {
      position: 'fixed' as const,
      bottom: '0',
      left: '0',
      right: '0',
      height: `${mobileHeight}px`,
      zIndex: '998',
      borderLeft: '1px solid #DDDDDD',
      borderTop: '1px solid #DDDDDD',
      borderBottom: '1px solid #DDDDDD',
      boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)',
      backgroundColor: '#FFFFFF',
      boxSizing: 'border-box' as const
    }
  } else {
    // 桌面端：使用相对定位，适配flex布局，确保有固定高度
    return {
      position: 'relative' as const,
      height: '100%',
      width: '100%',
      backgroundColor: isExpanded ? '#FFFFFF' : 'transparent',
      borderLeft: isExpanded ? '1px solid #DDDDDD' : 'none',
      boxShadow: isExpanded ? '-2px 0 4px rgba(0, 0, 0, 0.1)' : 'none',
      boxSizing: 'border-box' as const,
      overflow: 'hidden' as const, // 确保chat窗口本身不滚动，由内部区域控制滚动
      display: 'flex' as const,
      flexDirection: 'column' as const
    }
  }
}

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

// 处理ChatToolbar的事件
const handleRefreshAnchors = () => {
  // 刷新锚点的逻辑
  console.log('Refresh anchors')
}

const handleScrollToBottom = () => {
  // 滚动到底部的逻辑
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

// 在组件挂载时加载会话列表
onMounted(async () => {
  await chatStore.loadSessions()
  // 如果有当前会话，设置为选中
  if (chatStore.currentSession) {
    selectedSessionId.value = chatStore.currentSession.id
  }
  
  // 桌面端和移动端都默认收起
  chatStore.chatWindowState = 'minimized'
  
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

// 2024-03-25 18:30: 添加触摸相关变量
const touchStartY = ref(0)
const isTouchingChat = ref(false)

// 2024-03-25 18:30: 处理触摸开始
const handleTouchStart = (event: TouchEvent) => {
  // 记录开始触摸的位置
  touchStartY.value = event.touches[0].clientY
  
  // 检查触摸是否在聊天窗口内
  const target = event.target as HTMLElement
  const chatWindow = messageListRef.value
  
  if (chatWindow && (chatWindow === target || chatWindow.contains(target))) {
    isTouchingChat.value = true
    // 立即阻止事件冒泡和默认行为，停止文章的惯性滚动
    event.stopPropagation()
    event.preventDefault()
    
    // 2024-03-25 19:30: 添加额外处理确保滚动响应
    document.body.style.overscrollBehavior = 'none'
  } else {
    isTouchingChat.value = false
  }
}

// 2024-03-25 18:30: 处理触摸移动
const handleTouchMove = (event: TouchEvent) => {
  if (!messageListRef.value || !isTouchingChat.value) return
  
  // 立即阻止默认行为和冒泡
  event.preventDefault()
  event.stopPropagation()
  
  const container = messageListRef.value
  const { scrollTop, scrollHeight, clientHeight } = container
  
  // 计算触摸移动距离
  const currentY = event.touches[0].clientY
  const deltaY = touchStartY.value - currentY
  touchStartY.value = currentY
  
  const newScrollTop = scrollTop + deltaY
  
  // 检查是否在可滚动范围内
  if (newScrollTop >= 0 && newScrollTop <= scrollHeight - clientHeight) {
    container.scrollTop = newScrollTop
  } else if (newScrollTop < 0 || newScrollTop > scrollHeight - clientHeight) {
    // 如果已经到达边界，允许事件冒泡
    isTouchingChat.value = false
    // 2024-03-25 19:30: 恢复默认滚动行为
    document.body.style.overscrollBehavior = 'auto'
  }
  
  // 更新自动滚动标志
  shouldAutoScroll.value = isAtBottom()
}

// 2024-03-25 19:30: 添加触摸结束处理
const handleTouchEnd = () => {
  if (isTouchingChat.value) {
    // 恢复默认滚动行为
    document.body.style.overscrollBehavior = 'auto'
    isTouchingChat.value = false
  }
}

// 2024-03-25 20:30: 优化桌面端滚动处理
const handleChatScroll = (event: WheelEvent) => {
  if (!messageListRef.value) return
  
  // 确保事件不会传播到父元素
  event.stopPropagation()
  
  const container = messageListRef.value
  const { scrollTop, scrollHeight, clientHeight } = container
  
  // 计算新的滚动位置
  const deltaY = event.deltaY
  let newScrollTop = scrollTop + deltaY
  
  // 优化边界处理
  if (newScrollTop < 0) {
    // 到达顶部时，允许一点弹性效果
    newScrollTop = 0
  } else if (newScrollTop > scrollHeight - clientHeight) {
    // 到达底部时，允许一点弹性效果
    newScrollTop = scrollHeight - clientHeight
  }
  
  // 使用 scrollTo 来获得更平滑的滚动效果
  container.scrollTo({
    top: newScrollTop,
    behavior: 'auto'  // 使用 auto 而不是 smooth 以保持响应性
  })
  
  // 更新自动滚动标志
  shouldAutoScroll.value = isAtBottom()
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
    // 移动端使用动态高度，桌面端使用固定高度
    windowHeight.value = isMobile.value ? getMobileHeight() : DEFAULT_EXPANDED_HEIGHT
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
/* 桌面端toggle按钮样式 */
.desktop-toggle-btn {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #6b7280;
  z-index: 10;
}

.desktop-toggle-btn:hover {
  background: #f9fafb;
  color: #374151;
}

.desktop-toggle-btn.minimized {
  display: none; /* 收起状态隐藏切换按钮，改用细边区域点击 */
}

.toggle-text {
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

/* 聊天内容区域样式 */
.chat-content-area {
  /* 移除固定高度计算，使用flex布局控制 */
}

.mobile-content {
  height: calc(100% - 60px - 40px);
}

/* 输入框区域样式 - 更新为flex布局 */
/* 移除position: absolute，改用flex布局 */

/* 输入框样式 */
.chat-input {
  width: 100%;
  padding: 8px 40px 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  color: #333333;
  font-size: 14px;
}

.chat-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 1px #3b82f6;
}

.mobile-chat-input {
  padding-right: 48px;
  margin-right: 8px;
}

/* 发送按钮样式 */
.chat-send-btn {
  position: absolute;
  right: 20px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.chat-send-btn:hover {
  background-color: #f9fafb;
}

.mobile-send-btn {
  right: 24px;
}

/* 消息容器样式 */
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
  animation: pulse 2s ease-in-out infinite;
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

/* 过渡效果样式 */
.transition-none {
  transition: none !important;
}

.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* Markdown样式 */
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

/* 响应式样式 */
@media (max-width: 768px) {
  .chat-toggle-btn {
    display: none;
  }
}
</style> 