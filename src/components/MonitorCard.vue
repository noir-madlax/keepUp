<template>
  <div class="monitor-card">
    <div class="card-header">
      <div class="site-info">
        <img v-if="site.icon_url" :src="site.icon_url" :alt="site.name" class="site-icon" />
        <div class="site-text">
          <h3 class="site-name">{{ site.name }}</h3>
          <p class="site-desc">{{ site.description }}</p>
        </div>
      </div>
      <div class="status-indicator" :class="{ valid: site.cookie_valid, invalid: !site.cookie_valid }">
        <span class="status-dot"></span>
      </div>
    </div>

    <div class="card-actions">
      <button @click="handleRefresh" :disabled="refreshing" class="action-button" title="刷新">
        <el-icon :class="{ 'rotating': refreshing }"><Refresh /></el-icon>
      </button>
      <button @click="viewDetails" class="action-button" title="查看详情">
        <el-icon><View /></el-icon>
      </button>
    </div>

    <div v-if="site.latest_data" class="card-body">
      <div class="data-display">
        <pre class="data-content">{{ formatData(site.latest_data.data) }}</pre>
      </div>

      <div class="card-meta">
        <span class="meta-item">
          <el-icon><Clock /></el-icon>
          {{ formatDate(site.latest_data.created_at) }}
        </span>
      </div>
    </div>

    <div v-else class="card-body empty">
      <div class="empty-state">
        <el-icon class="empty-icon"><Picture /></el-icon>
        <p class="empty-text">暂无数据</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Clock, Refresh, Picture, View } from '@element-plus/icons-vue'

interface Props {
  site: {
    slug: string
    name: string
    url: string
    description: string
    icon_url?: string
    is_active: boolean
    latest_data?: any
    cookie_valid?: boolean
  }
}

const props = defineProps<Props>()
const emit = defineEmits<{
  refresh: [siteSlug: string]
}>()

const refreshing = ref(false)

function formatData(data: any) {
  if (!data) return 'N/A'
  
  // 格式化显示数据
  if (typeof data === 'object') {
    const entries = Object.entries(data).filter(([key]) => key !== 'test')
    
    // 特殊处理 OpenRouter 的 balance 字段
    if (data.balance !== undefined) {
      return `Balance: ${Number(data.balance).toFixed(4)}`
    }
    
    // 特殊处理Cursor的included字段
    const hasIncludedUsed = entries.some(([key]) => key === 'included_used')
    const hasIncludedTotal = entries.some(([key]) => key === 'included_total')
    
    if (hasIncludedUsed && hasIncludedTotal) {
      const included_used = data.included_used
      const included_total = data.included_total
      const ondemand_used = data.ondemand_used
      const ondemand_limit = data.ondemand_limit
      
      return `Included: ${included_used}/${included_total}\nOndemand: ${ondemand_used}/${ondemand_limit}`
    }
    
    return entries
      .map(([key, value]) => {
        // 智能缩短字段名
        const shortKey = key
          .replace('_used', '')
          .replace('_total', ' Total')
          .replace('_limit', ' Limit')
          .split('_')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ')
        return `${shortKey}: ${value}`
      })
      .join('\n')
  }
  
  return String(data)
}

function formatDate(dateString: string) {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function handleRefresh() {
  refreshing.value = true
  try {
    emit('refresh', props.site.slug)
  } finally {
    // 延迟重置loading状态，给用户反馈
    setTimeout(() => {
      refreshing.value = false
    }, 1000)
  }
}

function viewDetails() {
  window.open(props.site.url, '_blank')
}
</script>

<style scoped>
.monitor-card {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 20px;
  padding: 1.5rem;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08),
              inset 0 1px 0 rgba(255, 255, 255, 0.2);
  height: 240px;
  display: flex;
  flex-direction: column;
  position: relative;
}

.monitor-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  border-radius: 24px 24px 0 0;
}

.monitor-card:hover {
  transform: translateY(-6px) scale(1.01);
  box-shadow: 0 16px 56px rgba(0, 0, 0, 0.12),
              inset 0 1px 0 rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.35);
  background: rgba(255, 255, 255, 0.18);
}

.monitor-card:hover .card-actions {
  opacity: 0.7;
  pointer-events: all;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.25rem;
}

.site-info {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  flex: 1;
  min-width: 0;
}

.site-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  object-fit: contain;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  padding: 6px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.site-text {
  flex: 1;
  min-width: 0;
}

.site-name {
  font-size: 1rem;
  font-weight: 600;
  color: white;
  margin: 0 0 0.25rem 0;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  letter-spacing: -0.01em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.site-desc {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.75);
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-indicator.valid .status-dot {
  background: #10b981;
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7),
              0 0 8px rgba(16, 185, 129, 0.4);
}

.status-indicator.invalid .status-dot {
  background: #ef4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.4);
  animation: none;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7),
                0 0 8px rgba(16, 185, 129, 0.4);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(16, 185, 129, 0),
                0 0 8px rgba(16, 185, 129, 0.4);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0),
                0 0 8px rgba(16, 185, 129, 0.4);
  }
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 0;
}

.card-body.empty {
  justify-content: center;
  align-items: center;
}

.empty-state {
  text-align: center;
  padding: 2rem 1rem;
}

.empty-icon {
  font-size: 2.5rem;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 0.75rem;
}

.empty-text {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

.data-display {
  background: rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 0.875rem;
  flex-shrink: 0;
  max-height: 120px;
  overflow-y: auto;
}

.data-display::-webkit-scrollbar {
  width: 6px;
}

.data-display::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.data-display::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.data-display::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.data-content {
  color: rgba(255, 255, 255, 0.95);
  font-family: 'SF Mono', 'Monaco', 'Consolas', 'Courier New', monospace;
  font-size: 0.75rem;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.5;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: auto;
  padding-top: 0.875rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.75rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

.card-actions {
  position: absolute;
  top: 1.125rem;
  right: 2.875rem;
  display: flex;
  gap: 0.375rem;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 10;
}

.action-button {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px) saturate(180%);
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08),
              inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.action-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.35);
  transform: scale(1.05);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12),
              inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.action-button:active:not(:disabled) {
  transform: translateY(0);
}

.action-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

