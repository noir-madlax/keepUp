<template>
  <div 
    class="fixed z-[999] p-2 flex gap-3"
    :style="{
      left: '20px',
      bottom: 'calc(70px)',
    }"
  >
    <!-- A组按钮 - 有锚定词时显示 -->
    <template v-if="hasSelectedText">
      <!-- 展开说说按钮 - 蓝色气泡 -->
      <button
        @click="handleChatAction('EXPAND')"
        class="bubble-button bubble-blue"
      >
        <img src="/images/icons/expand.svg" alt="Expand" class="w-4 h-4" />
        <span>展开说说</span>
      </button>

      <!-- 给出原文按钮 - 绿色气泡 -->
      <button
        @click="handleChatAction('ORIGINAL')"
        class="bubble-button bubble-green"
      >
        <img src="/images/icons/original.svg" alt="Original" class="w-4 h-4" />
        <span>给出原文</span>
      </button>

      <!-- 解释一下按钮 - 紫色气泡 -->
      <button
        @click="handleChatAction('EXPLAIN')"
        class="bubble-button bubble-purple"
      >
        <img src="/images/icons/explain.svg" alt="Explain" class="w-4 h-4" />
        <span>解释一下</span>
      </button>
    </template>

    <!-- B组按钮 - 无锚定词时显示 -->
    <template v-else>
      <!-- 章节概览按钮 - 橙色气泡 -->
      <button
        @click="handleToolAction('OVERVIEW')"
        class="bubble-button bubble-orange"
      >
        <img src="/images/icons/overview.svg" alt="Overview" class="w-4 h-4" />
        <span>分段提纲</span>
      </button>

      <!-- 人物介绍按钮 - 红色气泡 -->
      <button
        @click="handleToolAction('PEOPLE')"
        class="bubble-button bubble-red"
      >
        <img src="/images/icons/people.svg" alt="People" class="w-4 h-4" />
        <span>人物介绍</span>
      </button>

      <!-- 金句按钮 - 金色气泡 -->
      <button
        @click="handleToolAction('QUOTES')"
        class="bubble-button bubble-gold"
      >
        <img src="/images/icons/quotes.svg" alt="Quotes" class="w-4 h-4" />
        <span>金句</span>
      </button>

      <!-- XMind按钮 - 青色气泡 -->
      <button
        @click="handleToolAction('XMIND')"
        class="bubble-button bubble-cyan"
      >
        <img src="/images/icons/xmind.svg" alt="XMind" class="w-4 h-4" />
        <span>思维导图</span>
      </button>

      <!-- 名词解释按钮 - 棕色气泡 -->
      <button
        @click="handleToolAction('TERMS')"
        class="bubble-button bubble-brown"
      >
        <img src="/images/icons/terms.svg" alt="Terms" class="w-4 h-4" />
        <span>名词解释</span>
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useChatStore } from '../../stores/chat'
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { TOOL_SECTIONS } from '../../types/section'
import { useArticleStore } from '../../stores/article'

const chatStore = useChatStore()
const articleStore = useArticleStore()
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
    label: '展开说说',
    prompt: '请详细展开解释这段内容的含义和背景，用通俗易懂的方式说明。'
  },
  ORIGINAL: {
    label: '给出原文',
    prompt: '请给出这段内容的完整原文，并标注出重要的关键词和短语。'
  },
  EXPLAIN: {
    label: '解释一下',
    prompt: '请解释这段内容中的专业术语和难懂概念，帮助我更好地理解。'
  }
}

// B组动作 - 工具相关
const TOOL_ACTIONS = {
  OVERVIEW: {
    label: '分段提纲',
    action: () => {
      showAndScrollToSection(TOOL_SECTIONS.OVERVIEW)
    }
  },
  PEOPLE: {
    label: '人物介绍',
    action: () => {
      showAndScrollToSection(TOOL_SECTIONS.PEOPLE)
    }
  },
  QUOTES: {
    label: '金句',
    action: () => {
      showAndScrollToSection(TOOL_SECTIONS.QUOTES)
    }
  },
  XMIND: {
    label: '思维导图',
    action: () => {
      showAndScrollToSection(TOOL_SECTIONS.XMIND)
    }
  },
  TERMS: {
    label: '名词解释',
    action: () => {
      showAndScrollToSection(TOOL_SECTIONS.TERMS)
    }
  }
}

// 显示并滚动到指定小节
const showAndScrollToSection = async (sectionType: string) => {
  // 添加小节到显示列表
  if (!articleStore.selectedSections.includes(sectionType)) {
    articleStore.selectedSections.push(sectionType)
  }

  // 等待DOM更新
  await nextTick()

  // 查找对应的小节元素
  const sectionElement = document.querySelector(`[data-section-type="${sectionType}"]`)
  if (sectionElement) {
    // 平滑滚动到小节位置
    sectionElement.scrollIntoView({ behavior: 'smooth' })
  }
}

// 处理聊天按钮点击
const handleChatAction = async (action: keyof typeof CHAT_ACTIONS) => {
  const selection = window.getSelection()
  const selectedText = selection?.toString().trim()
  
  if (!selectedText) {
    console.warn('没有选中文本')
    return
  }

  try {
    // 将选中的文本作为上下文发送
    const prompt = `${selectedText}\n\n${CHAT_ACTIONS[action].prompt}`
    await chatStore.sendMessage(prompt)
  } catch (error) {
    console.error('发送消息失败:', error)
  }
}

// 处理工具按钮点击
const handleToolAction = (action: keyof typeof TOOL_ACTIONS) => {
  TOOL_ACTIONS[action].action()
}
</script>

<style scoped>
/* 2024-01-20 21:00: 气泡按钮基础样式 */
.bubble-button {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  transition: all 0.2s ease;
  border: none;
  backdrop-filter: blur(8px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.bubble-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.bubble-button:active {
  transform: translateY(0);
}

/* 蓝色气泡 */
.bubble-blue {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.9), rgba(37, 99, 235, 0.9));
}

.bubble-blue:hover {
  background: linear-gradient(135deg, rgba(59, 130, 246, 1), rgba(37, 99, 235, 1));
}

/* 绿色气泡 */
.bubble-green {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.9), rgba(5, 150, 105, 0.9));
}

.bubble-green:hover {
  background: linear-gradient(135deg, rgba(16, 185, 129, 1), rgba(5, 150, 105, 1));
}

/* 紫色气泡 */
.bubble-purple {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.9), rgba(109, 40, 217, 0.9));
}

.bubble-purple:hover {
  background: linear-gradient(135deg, rgba(139, 92, 246, 1), rgba(109, 40, 217, 1));
}

/* 图标样式 */
.bubble-button img {
  filter: brightness(0) invert(1); /* 将图标改为白色 */
}

/* 文字样式 */
.bubble-button span {
  white-space: nowrap;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 新增B组按钮样式 */
/* 橙色气泡 */
.bubble-orange {
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.9), rgba(234, 88, 12, 0.9));
}

.bubble-orange:hover {
  background: linear-gradient(135deg, rgba(251, 146, 60, 1), rgba(234, 88, 12, 1));
}

/* 红色气泡 */
.bubble-red {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.9), rgba(185, 28, 28, 0.9));
}

.bubble-red:hover {
  background: linear-gradient(135deg, rgba(239, 68, 68, 1), rgba(185, 28, 28, 1));
}

/* 金色气泡 */
.bubble-gold {
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.9), rgba(161, 98, 7, 0.9));
}

.bubble-gold:hover {
  background: linear-gradient(135deg, rgba(234, 179, 8, 1), rgba(161, 98, 7, 1));
}

/* 青色气泡 */
.bubble-cyan {
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.9), rgba(21, 94, 117, 0.9));
}

.bubble-cyan:hover {
  background: linear-gradient(135deg, rgba(34, 211, 238, 1), rgba(21, 94, 117, 1));
}

/* 棕色气泡 */
.bubble-brown {
  background: linear-gradient(135deg, rgba(180, 83, 9, 0.9), rgba(124, 45, 18, 0.9));
}

.bubble-brown:hover {
  background: linear-gradient(135deg, rgba(180, 83, 9, 1), rgba(124, 45, 18, 1));
}
</style> 