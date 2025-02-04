<template>
  <div 
    class="fixed z-[1003]"
    :class="{ 'opacity-50 pointer-events-none': disabled }"
    :style="{
      left: '40px',
      bottom: 'calc(60px)',
      maxWidth: 'calc(100vw - 40px)'
    }"
  >
    <!-- 2024-03-19 16:30: 修改为水平布局 -->
    <div class="flex items-center gap-3 overflow-x-auto pb-2 -mb-2">
      <!-- 2024-03-20 11:30: 根据选中状态显示不同提示文字 -->
      <div class="shrink-0 px-1 py-1.5 rounded-lg text-blue-600 font-medium text-sm">
        {{ hasSelectedText ? t('chat.toolbar.selected_hint') : t('chat.toolbar.hint') }}
      </div>

      <!-- 2024-03-20 11:30: 只在选中文字时显示按钮组 -->
      <template v-if="hasSelectedText">
        <!-- 展开说说按钮 - 蓝色气泡 -->
        <button
          @click="handleChatAction('EXPAND')"
          class="bubble-button shrink-0"
          :class="{ 'disabled-button': chatStore.isAIResponding }"
          :disabled="chatStore.isAIResponding"
        >
          <img src="/images/icons/expand.svg" alt="Expand" class="w-4 h-4" />
          <span>{{ t('chat.actions.expand') }}</span>
        </button>

        <!-- 给出原文按钮 - 绿色气泡 -->
        <button
          @click="handleChatAction('ORIGINAL')"
          class="bubble-button shrink-0"
          :class="{ 'disabled-button': chatStore.isAIResponding }"
          :disabled="chatStore.isAIResponding"
        >
          <img src="/images/icons/original.svg" alt="Original" class="w-4 h-4" />
          <span>{{ t('chat.actions.original') }}</span>
        </button>

        <!-- 解释一下按钮 - 紫色气泡 -->
        <button
          @click="handleChatAction('EXPLAIN')"
          class="bubble-button shrink-0"
          :class="{ 'disabled-button': chatStore.isAIResponding }"
          :disabled="chatStore.isAIResponding"
        >
          <img src="/images/icons/explain.svg" alt="Explain" class="w-4 h-4" />
          <span>{{ t('chat.actions.explain_selection') }}</span>
        </button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useChatStore } from '../../stores/chat'
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { PromptType } from '../../types/chat'

// 2024-03-14 21:30: 添加disabled prop
const props = defineProps<{
  disabled?: boolean
}>()

const { t } = useI18n()
const chatStore = useChatStore()
const hasSelectedText = ref(false)

// 检查选中文本
const checkSelectedText = () => {
  const selection = window.getSelection()
  const selectedText = selection?.toString().trim()
  hasSelectedText.value = !!selectedText
}

// 监听文本选择事件
onMounted(() => {
  document.addEventListener('selectionchange', checkSelectedText)
  // 初始检查
  checkSelectedText()
})

// 清理事件监听
onUnmounted(() => {
  document.removeEventListener('selectionchange', checkSelectedText)
})

// A组动作 - 聊天相关
const CHAT_ACTIONS = {
  EXPAND: {
    label: t('chat.actions.expand'),
    prompt: t('chat.actions.expand_prompt')
  },
  ORIGINAL: {
    label: t('chat.actions.original'),
    prompt: t('chat.actions.original_prompt')
  },
  EXPLAIN: {
    label: t('chat.actions.explain_selection'),
    prompt: t('chat.actions.explain_selection_prompt')
  }
}

const emit = defineEmits<{
  (e: 'scrollToBottom'): void
}>()

// 处理聊天按钮点击
const handleChatAction = async (action: keyof typeof CHAT_ACTIONS) => {
  const selection = window.getSelection()
  const selectedText = selection?.toString().trim()
  
  if (!selectedText) {
    console.warn('没有选中文本')
    return
  }

  try {
    chatStore.chatWindowState = 'expanded'
    chatStore.isInitializing = true
    chatStore.isAIResponding = true
    
    emit('scrollToBottom')
    
    let promptType: PromptType
    switch (action) {
      case 'EXPAND':
        promptType = PromptType.ELABORATE
        break
      case 'ORIGINAL':
        promptType = PromptType.ORIGIN
        break
      case 'EXPLAIN':
        promptType = PromptType.EXPLAIN
        break
      default:
        promptType = PromptType.BASE
    }
    
    const prompt = `${selectedText}\n\n${CHAT_ACTIONS[action].prompt}`
    await chatStore.sendMessage(prompt, promptType)
  } catch (error) {
    console.error('发送消息失败:', error)
    chatStore.isInitializing = false
    chatStore.isAIResponding = false
  }
}
</script>

<style scoped>
/* 2024-01-20 21:00: 气泡按钮基础样式 */
/* 2024-01-22 15:30: 修改为自适应宽度 */
.bubble-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  min-width: 96px;  /* 最小宽度保证视觉美观 */
  width: auto;      /* 自适应内容宽度 */
  height: 28px;
  padding: 0 12px;  /* 添加水平内边距，避免文字贴边 */
  border-radius: 14px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #000000;
  transition: all 0.2s ease;
  background: #FFFFFF;
  border: 1px solid #D9D9D9;
  box-shadow: none;
  white-space: nowrap; /* 防止文字换行 */
}

/* 2024-03-19 15:30: 添加禁用状态样式 */
.disabled-button {
  cursor: not-allowed;
  pointer-events: auto !important;  /* 允许hover事件 */
}

.bubble-button:not(.disabled-button):hover {
  transform: translateY(-1px);
  border-color: #BFBFBF;
}

.bubble-button:not(.disabled-button):active {
  transform: translateY(0);
}

/* 图标样式 */
.bubble-button img {
  width: 16px;
  height: 16px;
  filter: none;
}

/* 文字样式 */
.bubble-button span {
  white-space: nowrap;
  text-shadow: none;
}

/* 2024-01-21 12:00: 添加提示文字动画 */
@keyframes gentle-pulse {
  0% { opacity: 0.9; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.02); }
  100% { opacity: 0.9; transform: scale(1); }
}

.animate-pulse-gentle {
  animation: gentle-pulse 3s infinite ease-in-out;
}

.hint-text:hover {
  animation: none;
}
</style> 