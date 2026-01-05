<template>
  <div
    v-if="chatStore.toolbarVisible && chatStore.chatWindowState === 'minimized' && !isMobile"
    class="fixed z-50 px-3 py-2"
    :style="{
      top: chatStore.toolbarPosition.top + 'px',
      left: chatStore.toolbarPosition.left + 'px',
      transform: 'translateY(8px)'
    }"
  >
    <div class="flex gap-2">
      <!-- 展开说说按钮 -->
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useChatStore } from '../../stores/chat'
import { useI18n } from 'vue-i18n'
import { PromptType } from '../../types/chat'
import { ElMessage } from 'element-plus'

const { t } = useI18n()
const chatStore = useChatStore()

// 移动端检测
const isMobile = computed(() => window.innerWidth < 768)

// 聊天动作配置
const CHAT_ACTIONS = {
  EXPAND: {
    label: t('chat.actions.expand'),
    prompt: t('chat.actions.expand_prompt')
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
  const selectedText = chatStore.selectedText
  
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

  // 截断选中内容（前200字）
  const truncatedText = selectedText.length > 200 
    ? selectedText.slice(0, 200) + '...' 
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
    // 隐藏工具栏
    chatStore.hideToolbar()
  } catch (err) {
    console.error('复制失败:', err)
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
  color: #111827; /* gray-900 */
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease, background 0.15s ease;
  background: linear-gradient(180deg, #ffffff 0%, #f7f7f7 100%);
  border: 1px solid #E3E3E3;
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.9) inset, /* top highlight */
              0 1px 2px rgba(16, 24, 40, 0.06),       /* subtle base */
              0 2px 6px rgba(16, 24, 40, 0.06);       /* soft depth */
  white-space: nowrap;
  -webkit-tap-highlight-color: transparent;
}

.bubble-button:hover:not(.disabled-button) {
  transform: translateY(-1px);
  border-color: #D1D5DB; /* gray-300 */
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.9) inset,
              0 3px 6px rgba(16, 24, 40, 0.10);
}

.bubble-button:active:not(.disabled-button) {
  transform: translateY(0);
  background: linear-gradient(180deg, #f5f5f5 0%, #efefef 100%);
  box-shadow: 0 0 0 rgba(0,0,0,0);
}

.disabled-button {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>