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
        {{ t(`chat.actions.${action.type}`) }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useChatStore } from '../../stores/chat'
import { useAuthStore } from '../../stores/auth'
import { useRoute } from 'vue-router'
import type { ChatAction, Position, MarkType } from '../../types/chat'
import { useI18n } from 'vue-i18n'
import { TextPositionHelper } from '@/utils/textPosition'
import { ElMessage } from 'element-plus'

// 2024-01-11: 添加emit定义，用于通知父组件刷新锚点
const emit = defineEmits<{
  (e: 'refresh-anchors'): void
}>()

const { t, locale } = useI18n()
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
    type: 'explain' as ChatAction
  },
  {
    type: 'elaborate' as ChatAction
  },
  {
    type: 'question' as ChatAction
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

// 生成提问内容
const generateQuestion = (type: ChatAction, selectedContent: string): string => {
  // 2024-01-09: 根据当前语言环境生成对应语言的提问
  if (locale.value === 'zh') {
    switch (type) {
      case 'explain':
        return `请解释一下"${selectedContent}"在这篇文章中的具体含义和用法。`
      case 'elaborate':
        return `请详细展开说明"${selectedContent}"这部分内容，包括具体的细节和例子。`
      case 'question':
        return selectedContent
      default:
        return selectedContent
    }
  } else {
    switch (type) {
      case 'explain':
        return `Please explain the meaning and usage of "${selectedContent}" in this article.`
      case 'elaborate':
        return `Please elaborate on "${selectedContent}" with more details and examples.`
      case 'question':
        return selectedContent
      default:
        return selectedContent
    }
  }
}

const handleAction = async (type: ChatAction) => {
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
    // 2024-01-09: 先打开聊天窗口并设置初始化状态
    chatStore.isChatOpen = true
    chatStore.isInitializing = true

    // 生成对应的提问内容
    const questionContent = type === 'question' ? selectedContent : generateQuestion(type, selectedContent)

    // 2024-01-11: 分开保存原文内容和问题内容
    const context = {
      sectionType: currentSection.getAttribute('data-section-type'),
      position,
      selection: {
        content: selectedContent, // 原文内容
        type: 'word',
        position
      },
      messages: [
        {
          role: 'user',
          content: questionContent // 完整的问题内容
        }
      ]
    }

    // 2024-01-12: 修改createSession调用，传入完整问题内容作为message content
    const session = await chatStore.createSession(
      articleId,
      'word' as MarkType,
      selectedContent, // mark_content仍然使用原文内容
      type,
      context,
      type === 'question', // 只有question类型跳过初始消息
      questionContent // 新增参数：传入完整的问题内容
    )

    // 2024-01-11: session创建成功后，隐藏toolbar
    chatStore.hideToolbar()
    
    // 2024-01-11: 触发锚点刷新
    if (session) {
      // 通知父组件刷新锚点
      emit('refresh-anchors')
    }

  } catch (error) {
    console.error('创建会话失败:', error)
    // 2024-01-09: 发生错误时重置状态
    chatStore.isInitializing = false
    chatStore.isChatOpen = false
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