<template>
  <span 
    v-if="citation.isValid" 
    class="citation-bubble-wrapper"
    ref="bubbleRef"
  >
    <span 
      class="citation-bubble"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
      @click="handleClick"
      @click.stop
    >
      <span class="timestamp">[{{ citation.timestamp }}]</span>
      <span class="speaker">{{ citation.speaker }}</span>
    </span>
    
    <!-- Tooltip -->
    <div 
      v-if="showTooltip"
      class="citation-tooltip"
      :style="tooltipStyle"
      @click.stop
      @touchstart.stop
      @touchend.stop
    >
      <div class="tooltip-header">
        <span class="tooltip-timestamp">[{{ citation.timestamp }}]</span>
        <span class="tooltip-speaker">{{ citation.speaker }}</span>
      </div>
      <div class="tooltip-content">
        "{{ citation.content }}"
      </div>
    </div>
  </span>
  <span v-else>
    <slot></slot>
  </span>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { parseCitation, type ParsedCitation } from '../../utils/citationParser'
import { useChatStore } from '../../stores/chat'

const props = defineProps<{
  markId: string
  articleId: number
  sectionType: string
  markContent: string
  position: any
}>()

const chatStore = useChatStore()
const showTooltip = ref(false)
const bubbleRef = ref<HTMLElement>()
const tooltipStyle = ref({})

// 解析引用内容
const citation = computed(() => parseCitation(props.markContent))

// 处理鼠标悬停
const handleMouseEnter = () => {
  if (window.innerWidth > 768) { // 只在桌面端显示hover效果
    showTooltip.value = true
    updateTooltipPosition()
  }
}

const handleMouseLeave = () => {
  if (window.innerWidth > 768) {
    showTooltip.value = false
  }
}

// 处理点击事件
const handleClick = async () => {
  // 移动端或桌面端都显示tooltip
  if (window.innerWidth <= 768) {
    showTooltip.value = !showTooltip.value
    if (showTooltip.value) {
      updateTooltipPosition()
    }
  }
  
  // 同时处理会话加载逻辑
  try {
    const { data: sessions, error } = await chatStore.loadSessionsForMark(
      props.articleId,
      props.markContent,
      props.sectionType
    )
    
    if (error) throw error
    
    if (sessions && sessions.length > 0) {
      await chatStore.loadSession(sessions[0].id)
    }
    
    chatStore.chatWindowState = 'expanded'
  } catch (error) {
    console.error('加载会话失败:', error)
  }
}

// 更新tooltip位置
const updateTooltipPosition = () => {
  if (!bubbleRef.value) return
  
  const rect = bubbleRef.value.getBoundingClientRect()
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  
  // 计算tooltip位置
  let left = '50%'
  let transform = 'translateX(-50%)'
  
  // 如果tooltip会超出右边界，调整位置
  if (rect.left + 150 > viewportWidth) {
    left = 'auto'
    transform = 'translateX(-100%)'
  }
  
  // 如果tooltip会超出左边界，调整位置
  if (rect.left - 150 < 0) {
    left = '0'
    transform = 'translateX(0)'
  }
  
  tooltipStyle.value = {
    left,
    transform,
    top: '100%',
    marginTop: '8px'
  }
}

// 点击外部关闭tooltip（移动端）
const handleClickOutside = (event: MouseEvent | TouchEvent) => {
  if (bubbleRef.value && !bubbleRef.value.contains(event.target as Node)) {
    showTooltip.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside, { passive: true } as any)
  document.addEventListener('touchstart', handleClickOutside as any, { passive: true } as any)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside as any)
  document.removeEventListener('touchstart', handleClickOutside as any)
})
</script>

<style scoped>
.citation-bubble-wrapper {
  position: relative;
  display: inline;
  margin: 0 2px;
}

.citation-bubble {
  display: inline-block;
  background: #f0f8ff;
  border: 1px solid #e1f5fe;
  border-radius: 12px;
  padding: 3px 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  vertical-align: baseline;
}

.citation-bubble:hover {
  background: #e3f2fd;
  border-color: #0277bd;
  transform: translateY(-1px);
}

.timestamp {
  font-size: 0.75rem;
  color: #666;
  margin-right: 4px;
}

.speaker {
  font-size: 0.75rem;
  color: #0277bd;
  font-weight: 500;
}

.citation-tooltip {
  position: absolute;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  max-width: 300px;
  min-width: 200px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  font-size: 0.875rem;
  line-height: 1.4;
}

.tooltip-header {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.tooltip-timestamp {
  font-size: 0.75rem;
  color: #666;
  font-weight: 500;
}

.tooltip-speaker {
  font-size: 0.75rem;
  color: #0277bd;
  font-weight: 600;
}

.tooltip-content {
  color: #333;
  font-style: italic;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .citation-tooltip {
    max-width: 280px;
    font-size: 0.8rem;
  }
  
  .citation-bubble {
    padding: 2px 6px;
  }
  
  .timestamp,
  .speaker {
    font-size: 0.7rem;
  }
}
</style> 