<template>
  <div class="pull-to-refresh" ref="containerRef">
    <!-- 整体容器，包含刷新指示器和内容 -->
    <div 
      class="transform-container"
      :style="{ transform: `translate3d(0, ${distance}px, 0)` }"
      :class="{ 'transition-transform duration-300': !isDragging }"
    >
      <!-- 刷新指示器 -->
      <div 
        v-show="distance > 0"
        class="refresh-indicator"
      >
        <div class="flex items-center justify-center gap-2 py-3">
          <svg 
            class="w-5 h-5 text-gray-600"
            :class="{
              'animate-spin': status === 'refreshing',
              'transition-transform duration-300': true,
              'rotate-180': status === 'canRelease'
            }"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <template v-if="status === 'pulling' || status === 'canRelease'">
              <path d="M12 5v14M19 12l-7 7-7-7"/>
            </template>
            <template v-else-if="status === 'refreshing'">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </template>
            <template v-else-if="status === 'success'">
              <path d="M20 6L9 17l-5-5"/>
            </template>
          </svg>
          <span class="text-gray-600 text-sm">{{ t(statusConfig[status].text) }}</span>
        </div>
      </div>

      <!-- 内容区域 -->
      <div 
        ref="contentRef"
        class="content-container"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
      >
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  onRefresh: () => Promise<void>
  threshold?: number
  maxDistance?: number
}>()

const { t } = useI18n()

const threshold = props.threshold || 50  // 触发刷新的阈值
const maxDistance = props.maxDistance || 100  // 最大下拉距离
const dampingFactor = 0.4  // 阻尼系数，越大阻力越小

const status = ref<'pulling'|'canRelease'|'refreshing'|'success'>('pulling')
const distance = ref(0)
const isDragging = ref(false)
const startY = ref(0)

const statusConfig = {
  pulling: {
    text: 'home.pullToRefresh.pullDown'
  },
  canRelease: {
    text: 'home.pullToRefresh.release'
  },
  refreshing: {
    text: 'home.pullToRefresh.refreshing'
  },
  success: {
    text: 'home.pullToRefresh.success'
  }
}

const isScrolledToTop = () => {
  return window.scrollY <= 0
}

const damping = (distance: number) => {
  return distance * dampingFactor
}

const handleTouchStart = (e: TouchEvent) => {
  if (isScrolledToTop() && status.value !== 'refreshing') {
    isDragging.value = true
    startY.value = e.touches[0].clientY
  }
}

const handleTouchMove = (e: TouchEvent) => {
  if (!isDragging.value || status.value === 'refreshing') return
  
  const touchY = e.touches[0].clientY
  const diff = touchY - startY.value
  
  if (diff > 0 && isScrolledToTop()) {
    e.preventDefault() // 只在下拉时阻止默认行为
    distance.value = Math.min(damping(diff), maxDistance)
    
    if (distance.value >= threshold && status.value !== 'canRelease') {
      status.value = 'canRelease'
    } else if (distance.value < threshold && status.value !== 'pulling') {
      status.value = 'pulling'
    }
  }
}

const handleTouchEnd = async () => {
  if (!isDragging.value) return
  
  isDragging.value = false
  
  if (distance.value >= threshold) {
    status.value = 'refreshing'
    try {
      await props.onRefresh()
      status.value = 'success'
      await new Promise(resolve => setTimeout(resolve, 300))
    } catch (error) {
      console.error('Refresh failed:', error)
    } finally {
      distance.value = 0
      await new Promise(resolve => setTimeout(resolve, 300))
      status.value = 'pulling'
    }
  } else {
    distance.value = 0
  }
}
</script>

<style scoped>
.pull-to-refresh {
  position: relative;
  width: 100%;
}

.transform-container {
  width: 100%;
  will-change: transform;
  background: white;
}

.refresh-indicator {
  width: 100%;
  background: white;
  pointer-events: none;
}

.content-container {
  width: 100%;
}
</style> 