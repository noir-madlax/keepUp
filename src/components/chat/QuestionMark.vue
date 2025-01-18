<template>
  <span v-if="showQuestionMark" class="relative inline-block group">
    <!-- 波浪下划线文本 -->
    <span 
      class="wavy-underline cursor-pointer"
      @click="handleClick"
    >
      <slot></slot>
    </span>
    
    <!-- 问题计数气泡 - 固定显示数字1 -->
    <span 
      class="question-count"
      @click="handleClick"
    >
      1
    </span>
  </span>
  <span v-else>
    <slot></slot>
  </span>
</template>

<script setup lang="ts">
import { useChatStore } from '../../stores/chat'
import { supabase } from '../../supabaseClient'
import type { Position } from '../../types/chat'

const props = defineProps<{
  markId: string
  articleId: number
  sectionType: string
  markContent: string
  position: Position
  showQuestionMark?: boolean
}>()

const chatStore = useChatStore()

const handleClick = async () => {
  try {
    // 获取该标记相关的会话
    const { data: sessions, error } = await supabase
      .from('keep_chat_sessions')
      .select(`
        *,
        messages:keep_chat_messages(*)
      `)
      .eq('article_id', props.articleId)
      .eq('mark_content', props.markContent)
      .eq('section_type', props.sectionType)
      .order('created_at', { ascending: false })

    if (error) throw error

    if (sessions && sessions.length > 0) {
      // 加载最新的会话
      await chatStore.loadSession(sessions[0].id)
    }

    // 打开聊天窗口
    chatStore.chatWindowState = 'expanded'

  } catch (error) {
    console.error('加载会话失败:', error)
  }
}
</script>

<style scoped>
.wavy-underline {
  text-decoration-line: underline;
  text-decoration-style: wavy;
  text-decoration-color: rgba(255, 200, 0, 0.3);
  text-decoration-thickness: 2px;
}

.question-count {
  position: absolute;
  right: -8px;
  bottom: -8px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: #FFB800;
  color: white;
  border-radius: 8px;
  font-size: 12px;
  line-height: 16px;
  text-align: center;
  cursor: pointer;
  user-select: none;
}

/* 悬停效果 */
.group:hover .wavy-underline {
  text-decoration-color: rgba(255, 200, 0, 0.6);
}

.group:hover .question-count {
  transform: scale(1.1);
  transition: transform 0.2s ease;
}
</style> 