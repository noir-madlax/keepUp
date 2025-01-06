<template>
  <div class="toolbar-container">
    <div 
      v-if="visible"
      class="fixed z-[99999] bg-white shadow-lg rounded-lg px-2 py-1.5 flex gap-2 items-center"
      :style="{
        top: `${position.top}px`,
        left: `${position.left}px`,
        transform: 'translateY(10px)'
      }"
    >
      <button 
        v-for="action in actions"
        :key="action.type"
        @click.prevent="handleAction(action.type)"
        @touchstart.prevent="handleAction(action.type)"
        class="px-3 py-1 text-sm rounded hover:bg-gray-100 transition-colors flex items-center gap-1"
      >
        {{ action.label }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useChatStore } from '../../stores/chat'
import { useAuthStore } from '../../stores/auth'
import { useRoute } from 'vue-router'
import type { ChatAction, Position } from '../../types/chat'
import { useI18n } from 'vue-i18n'
import { TextPositionHelper } from '@/utils/textPosition'
import { ElMessage } from 'element-plus'

const { t } = useI18n()
const chatStore = useChatStore()
const authStore = useAuthStore()
const route = useRoute()

const visible = computed(() => chatStore.toolbarVisible)
const position = computed(() => chatStore.toolbarPosition)
const selectedText = computed(() => chatStore.selectedText)
const articleId = Number(route.params.id)

// 定义工具栏按钮
const actions = [
  {
    type: 'summary' as ChatAction,
    label: t('chat.actions.summary')
  },
  {
    type: 'explain' as ChatAction,
    label: t('chat.actions.explain')
  },
  {
    type: 'question' as ChatAction,
    label: t('chat.actions.question')
  }
]

// 获取当前section
const getCurrentSection = () => {
  const selection = window.getSelection()
  if (!selection) return null
  
  const range = selection.getRangeAt(0)
  const element = range.startContainer.parentElement
  return element?.closest('[data-section-type]')
}

// 添加工具函数
const getTextOffset = (text: string, selectedText: string): Position | null => {
  const startIndex = text.indexOf(selectedText)
  if (startIndex === -1) {
    console.warn('无法找到选中文本的位置:', {
      selectedText,
      textLength: text.length,
      textPreview: text.slice(0, 100) + '...' // 只显示前100个字符
    })
    return null
  }
  return {
    start: startIndex,
    end: startIndex + selectedText.length
  }
}

const handleAction = async (type: 'summary' | 'explain' | 'question') => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning(t('auth.loginRequired'))
    chatStore.hideToolbar()
    return
  }

  const selectedContent = window.getSelection()?.toString() || ''
  
  const currentSection = getCurrentSection()
  if (!currentSection) return

  const selection = window.getSelection()
  if (!selection) return

  const position = TextPositionHelper.capturePosition(currentSection, selection)
  if (!position) {
    console.warn('无法记录文本位置')
    return
  }

  try {
    if (type === 'question') {
      const session = await chatStore.createSession(
        articleId,
        'word',
        selectedContent,
        type,
        {
          sectionType: currentSection.getAttribute('data-section-type'),
          position,
          selection: {
            content: selectedContent,
            type: 'word',
            position
          }
        },
        true
      )
    } else {
      const session = await chatStore.createSession(
        articleId,
        'word',
        selectedContent,
        type,
        {
          sectionType: currentSection.getAttribute('data-section-type'),
          position
        }
      )
    }

    chatStore.isChatOpen = true
  } catch (error) {
    console.error('创建会话失败:', error)
  }
}
</script> 

<style scoped>
.toolbar-container button {
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}

.toolbar-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 99999;
}

.toolbar-container > div {
  pointer-events: auto;
  background-color: rgba(255, 255, 255, 0.95);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
</style> 