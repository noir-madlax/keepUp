<template>
  <div 
    class="relative w-full"
    :class="{ 'opacity-50 pointer-events-none': disabled }"
  >
    <!-- 2024-03-25 16:30: 区分移动端和桌面端显示 -->
    <div class="flex flex-wrap items-start gap-2 pb-2 -mb-2">
      <!-- 移动端只显示基础提示 -->
      <template v-if="isMobile">
        <div class="shrink-0 px-1 py-1.5 rounded-lg text-blue-600 font-medium text-sm">
          {{ t('chat.toolbar.hint') }}
        </div>
      </template>

      <!-- 桌面端保持原有功能 -->
      <template v-else>
        <!-- 提示文字单独一行 -->
        <div class="w-full px-1 py-1.5 rounded-lg text-blue-600 font-medium text-sm">
          {{ hasSelectedText ? t('chat.toolbar.selected_hint') : t('chat.toolbar.hint') }}
        </div>

        <!-- 只在选中文字时显示按钮组，换行显示 -->
        <!-- 只在chat展开时显示按钮 -->
        <template v-if="hasSelectedText && chatStore.chatWindowState === 'expanded'">
          <div class="flex flex-wrap gap-2 w-full">
            <!-- 展开说说按钮 - 蓝色气泡 -->
            <button
              @click="handleChatAction('EXPAND')"
              class="bubble-button"
              :class="{ 'disabled-button': chatStore.isAIResponding }"
              :disabled="chatStore.isAIResponding"
            >
              <img src="/images/icons/expand.svg" alt="Expand" class="w-4 h-4" />
              <span>{{ t('chat.actions.expand') }}</span>
            </button>

            <!-- 分享按钮 -->
            <button
              @click="handleShare"
              class="bubble-button"
            >
              <img src="/images/icons/share.svg" alt="Share" class="w-4 h-4" />
              <span>{{ t('chat.actions.original') }}</span>
            </button>

            <!-- 解释一下按钮 - 紫色气泡 -->
            <button
              v-if="false"
              @click="handleChatAction('EXPLAIN')"
              class="bubble-button"
              :class="{ 'disabled-button': chatStore.isAIResponding }"
              :disabled="chatStore.isAIResponding"
            >
              <img src="/images/icons/explain.svg" alt="Explain" class="w-4 h-4" />
              <span>{{ t('chat.actions.explain_selection') }}</span>
            </button>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useChatStore } from '../../stores/chat'
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { PromptType } from '../../types/chat'
import { ElMessage } from 'element-plus'

// 2024-03-14 21:30: 添加disabled prop
const props = defineProps<{
  disabled?: boolean
}>()

const { t } = useI18n()
const chatStore = useChatStore()
const hasSelectedText = ref(false)

// 2024-03-25 16:30: 添加移动端检测
const isMobile = computed(() => window.innerWidth < 768)

// 2024-03-25 16:30: 修改文本选择监听逻辑
const checkSelectedText = () => {
  // 移动端不检查文本选择
  if (isMobile.value) {
    hasSelectedText.value = false
    return
  }
  
  const selection = window.getSelection()
  const selectedText = selection?.toString().trim()
  hasSelectedText.value = !!selectedText
}

// 监听文本选择事件 - 只在桌面端添加监听
onMounted(() => {
  if (!isMobile.value) {
    document.addEventListener('selectionchange', checkSelectedText)
    // 初始检查
    checkSelectedText()
  }
})

// 清理事件监听
onUnmounted(() => {
  if (!isMobile.value) {
    document.removeEventListener('selectionchange', checkSelectedText)
  }
})

// A组动作 - 聊天相关
const CHAT_ACTIONS = {
  EXPAND: {
    label: t('chat.actions.expand'),
    prompt: t('chat.actions.expand_prompt')
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

// 处理分享按钮点击
const handleShare = async () => {
  const selection = window.getSelection()
  const selectedText = selection?.toString().trim()
  
  if (!selectedText) {
    console.warn('没有选中文本')
    return
  }

  const articleInfo = chatStore.currentArticleInfo
  const articleId = chatStore.currentArticleId
  
  if (!articleInfo || !articleId) {
    console.warn('没有文章信息')
    return
  }

  // 截断选中内容（前100字）
  const truncatedText = selectedText.length > 100 
    ? selectedText.slice(0, 100) + '...' 
    : selectedText

  // 生成分享文案
  let shareText: string
  if (articleInfo.isPrivate || !articleInfo.authorName) {
    // 私密文章或没有作者名，不显示作者
    shareText = `📢《${articleInfo.title}》中提到：\n"${truncatedText}"\n🔗 ${window.location.origin}/article/${articleId}`
  } else {
    // 正常文章
    shareText = `📢 ${articleInfo.authorName} 在《${articleInfo.title}》中提到：\n"${truncatedText}"\n🔗 ${window.location.origin}/article/${articleId}`
  }

  try {
    await navigator.clipboard.writeText(shareText)
    ElMessage.success(t('article.copySuccess'))
  } catch (err) {
    console.error('复制失败:', err)
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
  color: #111827; /* gray-900 */
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease, background 0.15s ease;
  background: linear-gradient(180deg, #ffffff 0%, #f7f7f7 100%);
  border: 1px solid #E3E3E3;
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.9) inset,
              0 1px 2px rgba(16, 24, 40, 0.06),
              0 2px 6px rgba(16, 24, 40, 0.06);
  white-space: nowrap; /* 防止文字换行 */
}

/* 2024-03-19 15:30: 添加禁用状态样式 */
.disabled-button {
  cursor: not-allowed;
  pointer-events: auto !important;  /* 允许hover事件 */
}

.bubble-button:not(.disabled-button):hover {
  transform: translateY(-1px);
  border-color: #D1D5DB; /* gray-300 */
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.9) inset,
              0 3px 6px rgba(16, 24, 40, 0.10);
}

.bubble-button:not(.disabled-button):active {
  transform: translateY(0);
  background: linear-gradient(180deg, #f5f5f5 0%, #efefef 100%);
  box-shadow: 0 0 0 rgba(0,0,0,0);
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