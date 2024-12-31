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
        @click="handleAction(action.type)"
        class="px-3 py-1 text-sm rounded hover:bg-gray-100 transition-colors flex items-center gap-1"
      >
        {{ action.label }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useChatStore } from '../../stores/chat'
import { useRoute } from 'vue-router'
import type { ChatAction } from '../../types/chat'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const chatStore = useChatStore()
const route = useRoute()

const visible = computed(() => chatStore.toolbarVisible)
const position = computed(() => chatStore.toolbarPosition)

// 添加 watch 来调试状态变化
watch(() => chatStore.toolbarVisible, (newVal) => {
  console.log('Toolbar visibility changed:', newVal)
})

watch(() => chatStore.toolbarPosition, (newVal) => {
  console.log('Toolbar position changed:', newVal)
})

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

// 处理按钮点击
const handleAction = (action: ChatAction) => {
  let prompt = ''
  const selectedContent = chatStore.selectedText
  
  // 获取选中文本的 section 信息
  const selection = window.getSelection()
  let currentSectionType: string | undefined
  let selectionRange: Range | null = null
  
  if (selection && selection.rangeCount > 0) {
    selectionRange = selection.getRangeAt(0)
    // 从选中的元素向上查找，直到找到带有 data-section-type 属性的元素
    let element: Element | null = selectionRange.commonAncestorContainer as Element
    while (element && !element.getAttribute) {
      element = element.parentElement
    }
    
    while (element && !element.getAttribute('data-section-type')) {
      element = element.parentElement
    }
    
    // 如果找到了带有 section 信息的元素
    if (element) {
      currentSectionType = element.getAttribute('data-section-type') || undefined
      console.log('Found section type:', currentSectionType)
    }
  }

  // 根据动作类型生成不同的提示语
  switch (action) {
    case 'summary':
      prompt = `请总结以下内容的要点：\n\n${selectedContent}`
      break
    case 'explain':
      prompt = `请解释以下内容的含义：\n\n${selectedContent}`
      break
    case 'question':
      prompt = `关于以下内容，我想请教：\n\n${selectedContent}`
      break
  }
  
  // 获取文章上下文信息
  const articleId = Number(route.params.id)
  
  // 构建会话上下文
  const context = {
    articleId,
    sectionType: currentSectionType,
    selection: {
      content: selectedContent,
      type: 'word' as const,
      position: {
        start: selectionRange?.startOffset || 0,
        end: selectionRange?.endOffset || 0
      }
    },
    action,
    prompt
  }
  
  // 打印完整上下文到控制台
  console.log('Creating chat session with context:', context)

  // 构建发送给聊天窗口的完整消息
  const fullPrompt = `
用户操作：${action}
选中内容：${selectedContent}
位置信息：${currentSectionType ? `在 ${currentSectionType} 部分` : '未知部分'}
提示语：${prompt}
  `.trim()

  chatStore.hideToolbar()
  chatStore.createSession(
    articleId,
    'word',
    fullPrompt,
    action,
    context
  )
}
</script> 

<style scoped>
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