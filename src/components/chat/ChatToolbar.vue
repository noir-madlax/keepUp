<template>
  <div 
    class="fixed z-[999] flex flex-col gap-2"
    :style="{
      left: '20px',
      bottom: 'calc(60px)',
    }"
  >
    <!-- 2024-01-21 11:30: 添加提示文字 -->
    <div class="w-fit px-3 py-1.5 bg-blue-50 rounded-lg border border-blue-100 text-blue-600 font-medium text-sm animate-pulse-gentle">
      {{ t('chat.toolbar.hint') }}
    </div>
    
    <div class="flex gap-3">
      <!-- B组按钮 - 始终显示 -->
      <!-- 内容结构图按钮 -->
      <button
        @click="handleToolAction('STRUCTURE')"
        class="bubble-button"
      >
        <img src="/images/icons/structure.svg" alt="Structure" class="w-4 h-4" />
        <span>{{ t('chat.actions.structure') }}</span>
      </button>

      <!-- 分段提纲按钮 -->
      <button
        @click="handleToolAction('OVERVIEW')"
        class="bubble-button"
      >
        <img src="/images/icons/overview.svg" alt="Overview" class="w-4 h-4" />
        <span>{{ t('chat.actions.overview') }}</span>
      </button>

      <!-- 金句按钮 -->
      <button
        @click="handleToolAction('QUOTES')"
        class="bubble-button"
      >
        <img src="/images/icons/quotes.svg" alt="Quotes" class="w-4 h-4" />
        <span>{{ t('chat.actions.quotes') }}</span>
      </button>

      <!-- 思维导图按钮 -->
      <button
        @click="handleToolAction('XMIND')"
        class="bubble-button"
      >
        <img src="/images/icons/xmind.svg" alt="XMind" class="w-4 h-4" />
        <span>{{ t('chat.actions.xmind') }}</span>
      </button>

      <!-- A组按钮 - 有锚定词时显示在B组按钮右侧 -->
      <template v-if="hasSelectedText">
        <!-- 展开说说按钮 - 蓝色气泡 -->
        <button
          @click="handleChatAction('EXPAND')"
          class="bubble-button"
        >
          <img src="/images/icons/expand.svg" alt="Expand" class="w-4 h-4" />
          <span>{{ t('chat.actions.expand') }}</span>
        </button>

        <!-- 给出原文按钮 - 绿色气泡 -->
        <button
          @click="handleChatAction('ORIGINAL')"
          class="bubble-button"
        >
          <img src="/images/icons/original.svg" alt="Original" class="w-4 h-4" />
          <span>{{ t('chat.actions.original') }}</span>
        </button>

        <!-- 解释一下按钮 - 紫色气泡 -->
        <button
          @click="handleChatAction('EXPLAIN')"
          class="bubble-button"
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
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { TOOL_SECTIONS } from '../../types/section'
import { useArticleStore } from '../../stores/article'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
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
    label: t('chat.actions.expand'),
    prompt: '请详细展开解释这段内容的含义和背景，用通俗易懂的方式说明。'
  },
  ORIGINAL: {
    label: t('chat.actions.original'),
    prompt: '请给出这段内容的完整原文，并标注出重要的关键词和短语。'
  },
  EXPLAIN: {
    label: t('chat.actions.explain_selection'),
    prompt: '请解释这段内容中的专业术语和难懂概念，帮助我更好地理解。'
  }
}

// B组动作 - 工具相关
const TOOL_ACTIONS = {
  OVERVIEW: {
    label: t('chat.actions.overview'),
    action: () => {
      showAndScrollToSection(TOOL_SECTIONS.OVERVIEW)
    }
  },
  STRUCTURE: {
    label: t('chat.actions.structure'),
    action: () => {
      showAndScrollToSection(TOOL_SECTIONS.STRUCTURE)
    }
  },
  QUOTES: {
    label: t('chat.actions.quotes'),
    action: () => {
      showAndScrollToSection(TOOL_SECTIONS.QUOTES)
    }
  },
  XMIND: {
    label: t('chat.actions.xmind'),
    action: () => {
      showAndScrollToSection(TOOL_SECTIONS.XMIND)
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

.bubble-button:hover {
  transform: translateY(-1px);
  border-color: #BFBFBF;
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
  width: 16px;
  height: 16px;
  filter: none; /* 移除之前的白色滤镜 */
}

/* 文字样式 */
.bubble-button span {
  white-space: nowrap;
  text-shadow: none;
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