<template>
  <div class="monitor-view">
    <div class="monitor-header">
      <h1 class="monitor-title">费用监控</h1>
      <el-button @click="refreshAll" :loading="isRefreshing" type="primary">
        <el-icon class="mr-1"><Refresh /></el-icon>
        刷新所有
      </el-button>
    </div>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="3" animated />
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
    const { data: scrapedData } = await supabase
      .from('scraped_data')
      .select('*')
      .eq('site_slug', site.slug)
      .order('created_at', { ascending: false })
      .limit(1)
      .single()

    if (scrapedData) {
      site.latest_data = scrapedData
    }

    // 获取Cookie状态
    const { data: cookieData } = await supabase
      .from('cookies')
      .select('is_valid')
      .eq('site_slug', site.slug)
      .order('created_at', { ascending: false })
      .limit(1)
      .single()

    if (cookieData) {
      site.cookie_valid = cookieData.is_valid
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.monitor-title {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 0;
}

.monitor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.loading-container,
.error-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
}

.mr-1 {
  margin-right: 0.25rem;
}
</style>

