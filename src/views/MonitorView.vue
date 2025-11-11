<template>
  <div class="monitor-view">
    <div class="monitor-header">
      <h1 class="monitor-title">费用监控</h1>
      <button @click="refreshAll" :disabled="isRefreshing" class="glass-button">
        <el-icon :class="{ 'rotating': isRefreshing }"><Refresh /></el-icon>
      </button>
    </div>

    <div v-if="loading" class="monitor-grid">
      <div v-for="i in 3" :key="i" class="skeleton-card">
        <div class="skeleton-header">
          <div class="skeleton-icon"></div>
          <div class="skeleton-text-group">
            <div class="skeleton-title"></div>
            <div class="skeleton-desc"></div>
          </div>
          <div class="skeleton-dot"></div>
        </div>
        <div class="skeleton-body">
          <div class="skeleton-data-box"></div>
          <div class="skeleton-time"></div>
        </div>
      </div>
    </div>

    <div v-else-if="error" class="error-container">
      <el-alert
        title="加载失败"
        type="error"
        :description="error"
        show-icon
      />
    </div>

    <div v-else class="monitor-grid">
      <MonitorCard
        v-for="site in websites"
        :key="site.slug"
        :site="site"
        @refresh="handleRefresh"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import MonitorCard from '../components/MonitorCard.vue'
import { supabase } from '../supabaseClient'

interface Website {
  slug: string
  name: string
  url: string
  description: string
  icon_url: string
  is_active: boolean
  display_order: number
  latest_data?: any
  cookie_valid?: boolean
}

const loading = ref(true)
const error = ref('')
const websites = ref<Website[]>([])
const isRefreshing = ref(false)

async function loadWebsites() {
  try {
    loading.value = true
    error.value = ''

    // 加载网站列表
    const { data: sitesData, error: sitesError } = await supabase
      .from('websites')
      .select('*')
      .eq('is_active', true)
      .order('display_order')

    if (sitesError) throw sitesError

    websites.value = sitesData || []

    // 加载每个网站的最新数据
    for (const site of websites.value) {
      await loadSiteData(site)
    }
  } catch (err: any) {
    error.value = err.message
    console.error('加载网站失败:', err)
  } finally {
    loading.value = false
  }
}

async function loadSiteData(site: Website) {
  try {
    // 获取最新的抓取数据
    const { data: scrapedData, error: scrapedError } = await supabase
      .from('scraped_data')
      .select('*')
      .eq('site_slug', site.slug)
      .order('created_at', { ascending: false })
      .limit(1)

    if (scrapedError) {
      console.error(`查询 ${site.name} scraped_data 失败:`, scrapedError)
    } else if (scrapedData && scrapedData.length > 0) {
      site.latest_data = scrapedData[0]
    }

    // 获取Cookie状态
    const { data: cookieData, error: cookieError } = await supabase
      .from('cookies')
      .select('is_valid')
      .eq('site_slug', site.slug)
      .order('created_at', { ascending: false })
      .limit(1)

    if (cookieError) {
      console.error(`查询 ${site.name} cookies 失败:`, cookieError)
    } else if (cookieData && cookieData.length > 0) {
      site.cookie_valid = cookieData[0].is_valid
    }
  } catch (err) {
    console.error(`加载 ${site.name} 数据失败:`, err)
  }
}

async function handleRefresh(siteSlug: string) {
  const site = websites.value.find(s => s.slug === siteSlug)
  if (!site) return

  try {
    // 调用API触发抓取
    const response = await fetch(`/api/trigger-scrape?site=${siteSlug}`, {
      method: 'POST'
    })

    if (!response.ok) {
      throw new Error(`抓取失败: ${response.statusText}`)
    }

    ElMessage.success(`${site.name} 刷新成功`)

    // 重新加载数据
    await loadSiteData(site)
  } catch (err: any) {
    ElMessage.error(`${site.name} 刷新失败: ${err.message}`)
    console.error('刷新失败:', err)
  }
}

async function refreshAll() {
  isRefreshing.value = true
  try {
    for (const site of websites.value) {
      await handleRefresh(site.slug)
    }
    ElMessage.success('所有网站刷新完成')
  } catch (err: any) {
    ElMessage.error(`刷新失败: ${err.message}`)
  } finally {
    isRefreshing.value = false
  }
}

onMounted(() => {
  loadWebsites()
})
</script>

<style scoped>
.monitor-view {
  min-height: 100vh;
  padding: 2rem;
  background-image: url('https://images.unsplash.com/photo-1559827260-dc66d52bef19?q=80&w=2070&auto=format&fit=crop');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  position: relative;
}

.monitor-view::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
  pointer-events: none;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  position: relative;
  z-index: 1;
}

.monitor-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: white;
  margin: 0;
  text-shadow: 0 2px 16px rgba(0, 0, 0, 0.2);
  letter-spacing: -0.015em;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

.glass-button {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(20px) saturate(180%);
  color: white;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.1),
              inset 0 1px 0 rgba(255, 255, 255, 0.25);
}

.glass-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.35);
  transform: scale(1.05);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.14),
              inset 0 1px 0 rgba(255, 255, 255, 0.35);
}

.glass-button:active:not(:disabled) {
  transform: translateY(0);
}

.glass-button:disabled {
  opacity: 0.6;
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

.monitor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 2rem;
  position: relative;
  z-index: 1;
}

.error-container {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 24px;
  padding: 2.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12),
              inset 0 1px 0 rgba(255, 255, 255, 0.3);
  position: relative;
  z-index: 1;
}

/* Skeleton Loading Styles */
.skeleton-card {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 24px;
  padding: 1.75rem;
  height: 280px;
  display: flex;
  flex-direction: column;
  position: relative;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08),
              inset 0 1px 0 rgba(255, 255, 255, 0.2);
  overflow: hidden;
}

.skeleton-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  border-radius: 24px 24px 0 0;
}

.skeleton-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.15),
    transparent
  );
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

.skeleton-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.skeleton-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  flex-shrink: 0;
}

.skeleton-text-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.skeleton-title {
  width: 120px;
  height: 20px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.2);
}

.skeleton-desc {
  width: 180px;
  height: 14px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.15);
}

.skeleton-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  flex-shrink: 0;
}

.skeleton-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.skeleton-data-box {
  background: rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  height: 80px;
}

.skeleton-time {
  width: 160px;
  height: 16px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.15);
  margin-top: auto;
}
</style>

