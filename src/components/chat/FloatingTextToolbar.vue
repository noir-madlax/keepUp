<template>
  <div
    v-if="chatStore.toolbarVisible && chatStore.chatWindowState === 'minimized' && !isMobile"
    class="fixed z-50 bg-white border border-gray-200 rounded-lg shadow-lg px-3 py-2"
    :style="{
      top: chatStore.toolbarPosition.top + 'px',
      left: chatStore.toolbarPosition.left + 'px',
      transform: 'translateY(8px)'
    }"
  >
    <div class="flex gap-2">
      <!-- Elaborate按钮 -->
      <button
        @click="handleChatAction('EXPAND')"
        class="bubble-button"
        :class="{ 'disabled-button': chatStore.isAIResponding }"
        :disabled="chatStore.isAIResponding"
      >
        <img src="/images/icons/expand.svg" alt="Expand" class="w-4 h-4" />
        <span>{{ t('chat.actions.expand') }}</span>
      </button>

      <!-- Show Original按钮 -->
      <button
        @click="handleChatAction('ORIGINAL')"
        class="bubble-button"
        :class="{ 'disabled-button': chatStore.isAIResponding }"
        :disabled="chatStore.isAIResponding"
      >
        <img src="/images/icons/original.svg" alt="Original" class="w-4 h-4" />
        <span>{{ t('chat.actions.original') }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useChatStore } from '../../stores/chat'
import { useI18n } from 'vue-i18n'
import { PromptType } from '../../types/chat'

const { t } = useI18n()
const chatStore = useChatStore()

// 移动端检测
const isMobile = computed(() => window.innerWidth < 768)

// 聊天动作配置
const CHAT_ACTIONS = {
  EXPAND: {
    label: t('chat.actions.expand'),
    prompt: t('chat.actions.expand_prompt')
  },
  ORIGINAL: {
    label: t('chat.actions.original'),
    prompt: t('chat.actions.original_prompt')
  }
}

// 处理聊天按钮点击
const handleChatAction = async (action: keyof typeof CHAT_ACTIONS) => {
  const selectedText = chatStore.selectedText
  
  if (!selectedText) {
    console.warn('没有选中文本')
    return
  }

  try {
    // 展开聊天窗口
    chatStore.chatWindowState = 'expanded'
    chatStore.isInitializing = true
    chatStore.isAIResponding = true
    
    // 隐藏工具栏
    chatStore.hideToolbar()
    
    let promptType: PromptType
    switch (action) {
      case 'EXPAND':
        promptType = PromptType.ELABORATE
        break
      case 'ORIGINAL':
        promptType = PromptType.ORIGIN
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
.bubble-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  min-width: 96px;
  width: auto;
  height: 28px;
  padding: 0 12px;
  border-radius: 14px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #000000;
  transition: all 0.2s ease;
  background: #FFFFFF;
  border: 1px solid #D9D9D9;
  box-shadow: none;
  white-space: nowrap;
}

.bubble-button:hover:not(.disabled-button) {
  transform: translateY(-1px);
  border-color: #BFBFBF;
}

.disabled-button {
  cursor: not-allowed;
  opacity: 0.6;
}
</style> 