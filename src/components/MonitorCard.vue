<template>
  <div class="monitor-card">
    <div class="card-header">
      <div class="site-info">
        <img v-if="site.icon_url" :src="site.icon_url" :alt="site.name" class="site-icon" />
        <div>
          <h3 class="site-name">{{ site.name }}</h3>
          <p class="site-desc">{{ site.description }}</p>
        </div>
      </div>
      <div class="status-indicator" :class="{ valid: site.cookie_valid, invalid: !site.cookie_valid }">
        <span class="status-dot"></span>
      </div>
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

      <div v-if="site.latest_data.screenshot_url" class="screenshot-preview">
        <el-image
          :src="site.latest_data.screenshot_url"
          :preview-src-list="[site.latest_data.screenshot_url]"
          fit="cover"
          class="screenshot-img"
        >
          <template #placeholder>
            <div class="image-placeholder">
              <el-icon><Picture /></el-icon>
            </div>
          </template>
        </el-image>
      </div>
    </div>

    <div v-else class="card-body empty">
      <el-empty description="暂无数据" />
    </div>

    <div class="card-footer">
      <el-button @click="handleRefresh" :loading="refreshing" size="small" type="primary">
        <el-icon class="mr-1"><Refresh /></el-icon>
        刷新
      </el-button>
      <el-button @click="viewDetails" size="small" type="info" text>
        查看详情
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Clock, Refresh, Picture } from '@element-plus/icons-vue'

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
    return Object.entries(data)
      .map(([key, value]) => `${key}: ${value}`)
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
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 1.5rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.monitor-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
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
  gap: 0.75rem;
  flex: 1;
}

.site-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  object-fit: contain;
  background: white;
  padding: 6px;
}

.site-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
  margin: 0 0 0.25rem 0;
}

.site-desc {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-indicator.valid .status-dot {
  background: #10b981;
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
}

.status-indicator.invalid .status-dot {
  background: #ef4444;
  box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
  animation: none;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
  }
}

.card-body {
  margin-bottom: 1rem;
}

.card-body.empty {
  padding: 2rem 0;
}

.data-display {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.data-content {
  color: white;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
}

.screenshot-preview {
  margin-top: 1rem;
}

.screenshot-img {
  width: 100%;
  height: 180px;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.1);
  color: rgba(255, 255, 255, 0.5);
  font-size: 2rem;
}

.card-footer {
  display: flex;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.mr-1 {
  margin-right: 0.25rem;
}
</style>

