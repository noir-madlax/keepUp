<template>
  <span 
    v-if="caseData.isValid" 
    class="case-bubble-wrapper"
    ref="bubbleRef"
  >
    <span 
      class="case-bubble"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
      @click.stop
    >
      <span class="case-icon">📦</span>
      <span class="case-company">{{ caseData.company }}</span>
    </span>
    
    <!-- Tooltip -->
    <div 
      v-if="showTooltip"
      class="case-tooltip"
      :style="tooltipStyle"
      @click.stop
      @touchstart.stop
      @touchend.stop
    >
      <div class="tooltip-header">
        <span class="tooltip-company">{{ caseData.company }}</span>
      </div>
      <div class="tooltip-content">
        {{ caseData.description }}
      </div>
    </div>
  </span>
  <span v-else>
    <slot></slot>
  </span>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { parseCase, type ParsedCase } from '@/utils/citationParser'

const props = defineProps<{
  markContent: string
}>()

const bubbleRef = ref<HTMLElement | null>(null)
const showTooltip = ref(false)
const tooltipStyle = ref({})

const caseData = computed<ParsedCase>(() => {
  return parseCase(props.markContent)
})

let tooltipTimer: ReturnType<typeof setTimeout> | null = null

const handleMouseEnter = () => {
  if (tooltipTimer) {
    clearTimeout(tooltipTimer)
    tooltipTimer = null
  }
  
  tooltipTimer = setTimeout(() => {
    showTooltip.value = true
    updateTooltipPosition()
  }, 300)
}

const handleMouseLeave = () => {
  if (tooltipTimer) {
    clearTimeout(tooltipTimer)
    tooltipTimer = null
  }
  
  tooltipTimer = setTimeout(() => {
    showTooltip.value = false
  }, 200)
}

const updateTooltipPosition = () => {
  if (!bubbleRef.value) return
  
  const rect = bubbleRef.value.getBoundingClientRect()
  const viewportWidth = window.innerWidth
  const tooltipWidth = 320
  
  let left = 0
  if (rect.left + tooltipWidth > viewportWidth) {
    left = viewportWidth - rect.left - tooltipWidth - 10
  }
  
  tooltipStyle.value = {
    left: `${left}px`,
    bottom: '100%',
    marginBottom: '8px'
  }
}

onMounted(() => {
  window.addEventListener('scroll', () => {
    if (showTooltip.value) {
      updateTooltipPosition()
    }
  })
})

onUnmounted(() => {
  if (tooltipTimer) {
    clearTimeout(tooltipTimer)
  }
})
</script>

<style scoped>
.case-bubble-wrapper {
  position: relative;
  display: inline-block;
  vertical-align: middle;
}

.case-bubble {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  font-size: 0.85em;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  margin: 0 2px;
}

.case-bubble:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.case-icon {
  font-size: 0.9em;
}

.case-company {
  font-weight: 500;
}

.case-tooltip {
  position: absolute;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  min-width: 250px;
  max-width: 320px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  pointer-events: none;
}

.tooltip-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.tooltip-company {
  font-weight: 600;
  color: #667eea;
  font-size: 0.95em;
}

.tooltip-content {
  color: #374151;
  font-size: 0.9em;
  line-height: 1.5;
  word-wrap: break-word;
}

/* 暗色模式支持 */
@media (prefers-color-scheme: dark) {
  .case-tooltip {
    background: #1f2937;
    border-color: #374151;
    color: #e5e7eb;
  }
  
  .tooltip-header {
    border-bottom-color: #374151;
  }
  
  .tooltip-company {
    color: #818cf8;
  }
  
  .tooltip-content {
    color: #d1d5db;
  }
}
</style>

