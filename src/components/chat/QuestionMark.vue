<template>
  <span class="relative inline-block group">
    <!-- 波浪下划线文本 -->
    <span 
      class="wavy-underline cursor-pointer"
      @click="handleClick"
    >
      <slot></slot>
    </span>
    
    <!-- 问题计数气泡 -->
    <span 
      v-if="count > 0"
      class="question-count"
      @click="handleClick"
    >
      {{ count }}
    </span>
  </span>
</template>

<script setup lang="ts">
import { useChatStore } from '../../stores/chat'

const props = defineProps<{
  count: number
  markId: string
}>()

const chatStore = useChatStore()

const handleClick = () => {
  // TODO: 加载历史会话
  chatStore.isChatOpen = true
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