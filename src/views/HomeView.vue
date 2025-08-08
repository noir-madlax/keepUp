<template>
  <!-- 根容器6 -->
  <div class="min-h-screen">
    
    <!-- 移除全屏遮罩式 Loading，改为列表骨架屏与底部轻量指示 -->

    <!-- 顶部导航栏 -->
  <header class="fixed top-0 left-0 right-0 bg-white z-40 w-full">
      <!-- 导航栏内容容器 -->
      <div class="flex justify-between items-center px-4 h-[90px] min-w-[320px] max-w-[1440px] mx-auto">
        <!-- 左侧Logo和标题容器 -->
        <div class="flex flex-col flex-shrink-0">
          <div class="flex items-center gap-2">
            <!-- 网站Logo图片 -->
            <img 
              src="/images/icons/logo.svg" 
              alt="Keep Up Logo" 
              class="w-[36px] h-[36px] sm:w-[48px] sm:h-[48px] flex-shrink-0" 
            />
            <!-- 网站标题文本 -->
            <h1 class="text-[16px] sm:text-[20px] text-[#333333] font-[400] leading-6 font-['PingFang_SC'] flex items-center gap-2 whitespace-nowrap">
              {{ t('home.title') }}
            </h1>
          </div>
        </div>


        
        <!-- 右侧导航元素容器 -->
        <div class="flex items-center gap-1 pl-2">
          <!-- 已登录用户信息区域 -->
          <template v-if="authStore.isAuthenticated">
            <!-- 用户头像 -->
            <img 
              :src="authStore.user?.user_metadata?.avatar_url || '/images/icons/avatar.svg'" 
              :alt="authStore.user?.email || 'User Avatar'" 
              class="w-[24px] h-[24px] rounded-full flex-shrink-0"
            />
            <!-- 登出按钮 - 增加最小宽度确保文字完整显示 -->
            <button 
              @click="handleLogout" 
              class="text-gray-600 hover:text-gray-800 min-w-[48px] sm:min-w-[64px] h-[32px] text-center text-sm sm:text-base whitespace-nowrap"
            >
              {{ t('home.nav.logout') }}
            </button>
          </template>

          <!-- 未登录状态显示 -->
          <template v-else>
            <button 
              @click="showLoginModal = true"
              class="w-[32px] h-[32px] flex items-center justify-center"
            >
              <img 
                src="/images/icons/login.svg" 
                alt="Login"
                class="w-[32px] h-[32px]"
              />
            </button>
          </template>
        </div>
      </div>
      
      <!-- 分割线 -->
      <div class="h-[1px] hidden bg-[#E5E5E5] w-full"></div>
</header>

    <!-- 登录模态框 -->
    <login-modal 
      v-if="showLoginModal" 
      @close="handleLoginModalClose" 
      @success="handleLoginSuccess"
      :allowClose="authStore.isAuthenticated"
      class="z-50"
    />

    <!-- 添加 ArticleRequestForm 组件到顶层 -->
    <ArticleRequestForm 
      ref="articleRequestFormRef" hidden
      @refresh="handleArticleRefresh"
      @uploadSuccess="handleUploadSuccess"
      @clearInput="handleClearInput"
    />

    <!-- 始终展示主要内容；加载中时由骨架屏与底部指示器表现 -->
      <!-- 主要内容区域 - 新用户布局 -->
      <template v-if="isNewUser">
        <div class="flex flex-col items-center justify-center min-h-screen px-4 pt-[90px]">
          <!-- 产品标语和特点 -->
          <div class="text-center mb-8">
            <h2 class="text-3xl sm:text-4xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent flex items-center justify-center gap-2">
              Video & Audio Summary
            </h2>
            <div class="max-w-2xl mx-auto space-y-4">
              <div class="flex flex-wrap justify-center gap-6 mt-6">
                <!-- 产品特点 -->
                <div class="flex items-center gap-2">
                  <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Get Insights</span>
                </div>
                <div class="flex items-center gap-2">
                  <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Ask Questions</span>
                </div>
                <div class="flex items-center gap-2">
                  <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Multiple Platforms</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 新用户 平台图标 -->
          <div class="flex justify-center items-center gap-6 mb-6">
            <img 
              v-for="channel in ['youtube', 'apple-podcast', 'spotify', 'bilibili']"
              :key="channel"
              :src="`/images/icons/${channel}.svg`"
              :alt="channel"
              class="w-8 h-8 sm:w-10 sm:h-10 transform hover:scale-110 transition-all duration-300"
            />
          </div>

          <!-- 新用户上传条 -->
          <div class="w-full max-w-3xl mx-auto px-4">
            <UploadInput
              v-model="requestUrl"
              container-class="relative"
              input-class="w-full h-12 sm:h-14 px-6 pr-14 rounded-full border-2 border-gray-200 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-gray-100 text-gray-800 placeholder-gray-400 transition-all duration-300 text-base sm:text-lg"
              enter-icon-class="absolute right-4 top-1/2 transform -translate-y-1/2 w-6 h-6 sm:w-8 sm:h-8 opacity-80 hover:opacity-100 transition-all duration-200 cursor-pointer"
              @submit="handleSubmit"
              @showLogin="showLoginModal = true"
            />
          </div>
        </div>
      </template>

      <!-- 主要内容区域 - 老用户布局 -->
      <template v-else>
        <pull-to-refresh class="mt-[20px]" :onRefresh="handleRefresh">
          <div class="px-4 sm:px-8 py-2 overflow-x-hidden">
            <div class="max-w-screen-2xl mx-auto w-full px-2 sm:px-0">
              <div class="flex flex-wrap items-center gap-2 sm:gap-4 mb-3 p-3 sm:p-4 bg-white rounded-lg sm:rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-200">
                <div class="flex items-center gap-4 w-full">
                  <div class="flex items-center gap-2 sm:gap-3">
                    <img 
                      v-for="channel in ['youtube', 'apple-podcast', 'spotify', 'wechat', 'bilibili']"
                      :key="channel"
                      :src="`/images/icons/${channel}.svg`"
                      :alt="channel"
                      class="w-4 h-4 sm:w-6 sm:h-6"
                    />
                  </div>

                  <p class="text-sm bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent font-medium whitespace-nowrap">
                    Video & audio summary
                  </p>
                </div>

                <div class="relative flex-grow w-full">
                  <UploadInput
                    v-model="requestUrl"
                    container-class="relative flex-grow w-full"
                    input-class="w-full sm:flex-grow pl-3 pr-12 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-000 focus:border-transparent bg-gray-100 transition-all duration-300"
                    enter-icon-class="absolute right-3 sm:right-4 top-1/2 transform -translate-y-1/2 w-6 h-6 sm:w-8 sm:h-8 opacity-100 transition-opacity duration-200 cursor-pointer hover:scale-110 transition-transform"
                    @submit="handleSubmit"
                    @showLogin="showLoginModal = true"
                  />
                </div>
              </div>
      <!-- 文字区域- 老用户布局  -->
              <div class="articles-section">
                <div class="flex items-center mb-[10px]">
                  <div class="flex items-center gap-2">
                    <!-- 文章标题 -->
                    <h2 class="font-['PingFang_SC'] text-[20px] font-semibold leading-[28px] text-[#000000]">
                      {{ t('home.articles.title') }}
                    </h2>
                    <!-- 只看我上传 开关（简单按钮） -->
                    <button
                      type="button"
                      @click.stop="toggleMineOnly"
                      @mousedown.stop.prevent="() => {}"
                      @touchstart.stop="() => {}"
                      @touchend.stop.prevent="handleTouchEnd"
                      :aria-pressed="mineOnly"
                      class="px-4 sm:px-3 h-9 sm:h-7 rounded-full border text-xs transition-all duration-200 focus:outline-none focus:ring-2 select-none cursor-pointer"
                      :class="mineOnly
                        ? 'bg-blue-600 text-white border-blue-600 shadow'
                        : 'bg-white text-blue-600 border-blue-300 hover:bg-blue-50 shadow-sm hover:shadow-md focus:ring-blue-200'"
                    >
                      <span class="inline-flex items-center gap-1">
                        <span class="text-[12px]" v-if="mineOnly">✓</span>
                        <span>Only my uploads</span>
                      </span>
                    </button>
                  </div>
                </div>
                <!-- 文章列表 -->
                <div class="articles-grid">
                  <template v-if="filteredArticles.length > 0">
                    <ArticleCard
                      v-for="article in filteredArticles"
                      :key="'requestId' in article ? article.requestId : article.id"
                      :article="article"
                      @delete="deleteRequest"
                    />
                  </template>

                 
                  <!-- 加载状态 -->
                  <template v-if="isLoading">
                    <div v-for="n in 27" :key="n" 
                      class="card-container"
                    >
                      <div class="flex flex-col h-full w-full gap-3">
                        <div class="flex justify-between gap-3">
                          <div class="flex flex-col gap-2 flex-1">
                            <div class="h-6 bg-gray-200 rounded w-4/5"></div>
                            <div class="h-6 bg-gray-200 rounded w-3/4"></div>
                            <div class="h-6 bg-gray-200 rounded w-2/3"></div>
                          </div>
                          <div class="w-[120px] h-[120px] bg-gray-200 rounded-xl flex-shrink-0"></div>
                        </div>

                        <div class="h-[1px] bg-gray-200 w-full"></div>

                        <div class="flex justify-between items-center">
                          <div class="flex items-center gap-2">
                            <div class="w-5 h-5 bg-gray-200 rounded-full"></div>
                            <div class="h-4 bg-gray-200 rounded w-20"></div>
                          </div>
                          <div class="flex items-center gap-2">
                            <div class="w-5 h-5 bg-gray-200 rounded"></div>
                            <div class="h-4 bg-gray-200 rounded w-20"></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </template>
                </div>
              </div>

              <!-- 加载更多 -->
              <div v-if="authStore.isAuthenticated && (isLoading || hasMore)" class="text-center py-4">
                <div v-if="isLoading" class="flex justify-center items-center space-x-2">
                  <div class="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                  <span class="text-gray-500">Loading more...</span>
                </div>
                <div v-else-if="hasMore" class="text-gray-500">
                  Scroll to load more
                </div>
              </div>
            </div>
          </div>
        </pull-to-refresh>
      </template>


  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, onActivated, nextTick } from 'vue'
import ArticleCard from '../components/ArticleCard.vue'
import { supabase } from '../supabaseClient'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import LoginModal from '../components/LoginModal.vue'
import type { Article as ArticleType, ArticleStatus } from '../types/article'
import ArticleRequestForm from '../components/ArticleRequestForm.vue'
import { useI18n } from 'vue-i18n'
import PullToRefresh from '../components/PullToRefresh.vue'
import localforage from 'localforage'

import UploadInput from '../components/UploadInput.vue'

const authStore = useAuthStore()
const showLoginModal = ref(false)
const selectedTag = ref<string>('all')
const selectedChannels = ref<string[]>([])
const selectedAuthors = ref<number[]>([])
const requestUrl = ref('')


// 添加类型定义
interface Author {
  id: number
  name: string
  icon?: string
}

interface ArticleRequest {
  id: string
  url: string
  status: 'processing' | 'processed' | 'failed'
  created_at: string
  error_message?: string
  original_url: string
  platform?: string
  requestId?: string
  article_id?: string
}

interface OptimisticCard {
  id: string
  url: string
  original_url: string
  created_at: string
  status: 'processing'
  platform?: string
  requestId: string
}

//



// 修改变量定义
const articles = ref<(ArticleType | ArticleRequest)[]>([])
const optimisticCards = ref<OptimisticCard[]>([])
const authors = ref<Author[]>([])
  const mineOnly = ref<boolean>(false)

// 分页相关的状态
const pageSize = 18 // 每加载的文章数量
const currentPage = ref(1)
const isLoading = ref(false) // 加载状态
const hasMore = ref(true) // 否还有更多数据

// 添加重置函数
const resetPageState = async () => {
  currentPage.value = 1
  articles.value = []
  hasMore.value = true
  await fetchArticles(true) // 重新获取第页数据
}

// 监路由激活
onActivated(() => {
  resetPageState()
})

//

// 添加轮询相关的变量
const POLL_INTERVAL = 15000  // 15秒轮询一次
let pollTimer: NodeJS.Timeout | null = null

// 修改轮询控制函数
const startPolling = () => {
  if (pollTimer) return
  
  pollTimer = setInterval(async () => {
    try {
      // 获取所有处理中的请求ID
      const processingIds = [
        ...articles.value
          .filter(article => 'status' in article && article.status === 'processing')
          .map(article => 'requestId' in article ? article.requestId : null),
        ...optimisticCards.value.map(card => card.requestId)
      ].filter(Boolean) as string[]

      // 2024-03-24: 如果没有处理中的请求，停止轮询并返回
      if (processingIds.length === 0) {
        stopPolling()
        return
      }

      // 查询这些请求的最新状态
      const { data: updatedRequests } = await supabase
        .from('keep_article_requests')
        .select('*')
        .in('id', processingIds)

      if (!updatedRequests) return

      // 更新状态
      let hasProcessedItems = false
      const typedRequests = updatedRequests as unknown as {
        id: string
        original_url: string
        status: ArticleStatus
        created_at: string
        error_message?: string
        platform?: string
        article_id?: string
      }[]
      
      typedRequests.forEach(request => {
        if (request.status === 'processed') {
          hasProcessedItems = true
          // 移除对应的乐观更新卡片
          optimisticCards.value = optimisticCards.value.filter(
            card => card.requestId !== request.id
          )
          // 移除对应的处理中文章
          articles.value = articles.value.filter(
            article => !('requestId' in article) || article.requestId !== request.id
          )
        } else if (request.status === 'failed') {
          // 对于失败的请求，更新现有的请求状态
          const index = articles.value.findIndex(
            article => 'requestId' in article && article.requestId === request.id
          )
          if (index !== -1) {
            const failedRequest = {
              ...articles.value[index],
              status: 'failed' as const,
              error_message: request.error_message,
              url: (articles.value[index] as ArticleRequest).url,
              original_url: (articles.value[index] as ArticleRequest).original_url
            } as ArticleRequest
            articles.value[index] = failedRequest
          }
          // 移除对应的乐观更新卡片
          optimisticCards.value = optimisticCards.value.filter(
            card => card.requestId !== request.id
          )
        }
      })

      // 只有当有处理完成的项目时，才刷新文章列表获取新的文章
      if (hasProcessedItems) {
        // 获取最新的已处理文章
        let newArticlesData: any[] | null = null
        if (mineOnly.value && authStore.user?.id) {
          // 通过 keep_article_views 获取本人上传文章的最新 ID，再查详情
          const { data: idsRows } = await supabase
            .from('keep_article_views')
            .select('article_id')
            .eq('user_id', authStore.user.id)
            .eq('is_author', true)
            .order('created_at', { ascending: false })
            .limit(pageSize)
          const ids = (idsRows || []).map((r: any) => r.article_id)
          if (ids.length) {
            const { data } = await supabase
              .from('keep_articles')
              .select(`
                id,
                title,
                cover_image_url,
                channel,
                created_at,
                tags,
                publish_date,
                author_id,
                content,
                original_link,
                author:keep_authors(id, name, icon)
              `)
              .eq('is_visible', true)
              .in('id', ids)
              .order('created_at', { ascending: false })
            newArticlesData = data || []
          } else {
            newArticlesData = []
          }
        } else {
          const { data } = await supabase
            .from('keep_articles')
            .select(`
              id,
              title,
              cover_image_url,
              channel,
              created_at,
              tags,
              publish_date,
              author_id,
              content,
              original_link,
              author:keep_authors(id, name, icon)
            `)
            .eq('is_visible', true)
            .order('created_at', { ascending: false })
            .limit(pageSize)
          newArticlesData = data || []
        }

        if (newArticlesData) {
          // 处理新文章数据
          const validNewArticles = (newArticlesData || []).map((article: any) => ({
            ...article,
            is_author: false, // 暂时设为false，避免业务逻辑影响
            status: 'processed' as const,
            content: article.content || '',
            original_link: article.original_link || ''
          })).filter((article): article is ArticleType => 
            article !== null && 
            typeof article.is_author === 'boolean' && 
            article.status === 'processed' &&
            typeof article.content === 'string' &&
            typeof article.original_link === 'string'
          )

          // 保留现有的处理中和失败状态的请求
          const existingRequests = articles.value.filter(
            article => 'status' in article && 
            (article.status === 'processing' || article.status === 'failed')  // 2024-03-24: 明确保留失败状态
          )

          // 合并新文章和现有的请求
          articles.value = [...existingRequests, ...validNewArticles]
        }
      }
    } catch (error) {
      console.error('轮询更新失败:', error)
    }
  }, POLL_INTERVAL)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

// 修改 addOptimisticCard 函数
const addOptimisticCard = async (url: string) => {
  // 先立即添加乐观更新卡片
  const now = new Date().toISOString()
  const id = `temp-${now}`
  const card: OptimisticCard = {
    id,
    url,
    original_url: url,
    created_at: now,
    status: 'processing',
    requestId: id,
    platform: getPlatformFromUrl(url)
  }
  
  // 添加乐观更新卡片
  optimisticCards.value = [card, ...optimisticCards.value]
  
  // 由于添加了卡片，isNewUser 计算属性会自动更新，触发界面切换
  // 开始轮询
  startPolling()

  try {
    // 异步检查是否存在相同URL的请求
    const { data: existingRequest } = await supabase
      .from('keep_article_requests')
      .select('*')
      .or(`url.eq.${url},original_url.eq.${url}`)
      .single()

    if (existingRequest) {
      // 如果已存在请求，移除乐观更新卡片
      optimisticCards.value = optimisticCards.value.filter(c => c.id !== id)

      // 如果是处理中状态，添加到文章列表
      const typedRequest = existingRequest as unknown as {
        id: string
        original_url: string
        status: ArticleStatus
        created_at: string
        error_message?: string
        platform?: string
        article_id?: string
      }
      
      if (typedRequest.status === 'processing') {
        const request = {
          id: typedRequest.id,
          url: typedRequest.original_url,
          status: typedRequest.status,
          created_at: typedRequest.created_at,
          error_message: typedRequest.error_message,
          original_url: typedRequest.original_url,
          platform: typedRequest.platform,
          article_id: typedRequest.article_id,
          requestId: typedRequest.id
        } as ArticleRequest

        articles.value = [request, ...articles.value]
      }
    }
  } catch (error) {
    console.error('检查已存在请求失败:', error)
  }
}

// 从URL判断平台
const getPlatformFromUrl = (url: string): string => {
  if (url.includes('youtube') || url.includes('youtu.be')) {
    return 'youtube'
  }
  if (url.includes('spotify')) {
    return 'spotify'
  }
  if (url.includes('podcasts.apple.com')) {
    return 'apple'
  }
  return 'webpage'
}


// 修改 fetchArticles 函数
const fetchArticles = async (isRefresh = false) => {
  if (!authStore.isAuthenticated) return
  
  try {
    isLoading.value = true
    if (isRefresh) {
      currentPage.value = 1
    }

    // 构建查询 - 尝试包含viewer_count字段，如果不存在则跳过
    let queryFields = `
      id,
      title,
      cover_image_url,
      channel,
      created_at,
      tags,
      publish_date,
      author_id,
      content,
      original_link,
      author:keep_authors(id, name, icon)
    `
    
    // 尝试查询是否有viewer_count字段
    try {
      // 先做一个小的测试查询来检查字段是否存在
      await supabase
        .from('keep_articles')
        .select('id, viewer_count')
        .limit(1)
      
      // 如果成功，则添加viewer_count字段
      queryFields = `
        id,
        title,
        cover_image_url,
        channel,
        created_at,
        tags,
        publish_date,
        author_id,
        content,
        original_link,
        viewer_count,
        author:keep_authors(id, name, icon)
      `
    } catch (e) {
      console.info('viewer_count字段不存在，使用默认值')
    }
    
    // 获取文章数据
    let articlesData: any[] | null = null
    if (mineOnly.value && authStore.user?.id) {
      // 通过 keep_article_views 获取我的文章ID（分页），再查详情
      const { data: idRows, error: idsError } = await supabase
        .from('keep_article_views')
        .select('article_id')
        .eq('user_id', authStore.user.id)
        .eq('is_author', true)
        .order('created_at', { ascending: false })
        .range((currentPage.value - 1) * pageSize, currentPage.value * pageSize - 1)

      if (idsError) throw idsError
      const ids = (idRows || []).map((r: any) => r.article_id)
      // 确保分页顺序与未过滤一致：按 keep_article_views.created_at desc 的顺序再查询详情后，前端再次按 created_at desc 兜底

      if (ids.length === 0) {
        articlesData = []
      } else {
        const { data, error: artErr } = await supabase
          .from('keep_articles')
          .select(queryFields)
          .eq('is_visible', true)
          .in('id', ids)
          .order('created_at', { ascending: false })
        if (artErr) throw artErr
        articlesData = data || []
      }
    } else {
        const { data, error } = await supabase
        .from('keep_articles')
        .select(queryFields)
        .eq('is_visible', true)
        .order('created_at', { ascending: false })
        .range((currentPage.value - 1) * pageSize, currentPage.value * pageSize - 1)
      if (error) throw error
      articlesData = data || []
    }

    // 修改：每次刷新或第一页加载时都获取处理中和失败的请求
    let requests: any[] = []
    if (isRefresh || currentPage.value === 1) {
      // 构建请求查询，mineOnly 时仅查询本人请求
      let requestsQuery = supabase
        .from('keep_article_requests')
        .select('*')
        .in('status', ['processing', 'failed'] as ArticleStatus[])

      if (mineOnly.value && authStore.user?.id) {
        requestsQuery = requestsQuery.eq('user_id', authStore.user.id)
      }

      const { data: requestsData } = await requestsQuery
        .order('created_at', { ascending: false })
      
      requests = requestsData || []
    }

    // 处理文章数据 - 直接使用viewer_count字段，如果不存在则使用0
    const validArticles = (articlesData || [])
      // 兜底保证顺序与“全部”一致
      .sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .map((article: any) => ({
      ...article,
      is_author: false, // 暂时设为false，避免业务逻辑影响
      status: 'processed' as const,
      content: article.content || '',
      original_link: article.original_link || '',
      viewer_count: article.viewer_count || 0
    }))
    .filter((article): article is ArticleType => 
      article !== null && 
      typeof article.is_author === 'boolean' && 
      article.status === 'processed' &&
      typeof article.content === 'string' &&
      typeof article.original_link === 'string'
    )

    // 修改请求的类型处理
    const typedRequests = requests.map(request => ({
      id: request.id,
      url: request.original_url,
      status: request.status || 'processing',
      created_at: request.created_at || new Date().toISOString(),
      error_message: request.error_message,
      original_url: request.original_url,
      platform: request.platform,
      article_id: request.article_id,
      requestId: request.id
    } as ArticleRequest))
    
    // 合并文章列表
    if (isRefresh || currentPage.value === 1) {
      // 如果是刷新或第一页，包含处理中和失败的请求
      articles.value = [...typedRequests, ...validArticles]
    } else {
      // 如果是加载更多，只添加新的文章
      articles.value = [...articles.value, ...validArticles]
    }
    
    // 更新乐观更新卡片
    optimisticCards.value = optimisticCards.value.filter(opt => {
      // 检查是否有对应的请求已经存在
      const hasMatchingRequest = articles.value.some(article => 
        'original_url' in article && 
        (article.original_url === opt.original_url || article.url === opt.original_url)
      )
      // 如果存在匹配的请求，移除乐观更新卡片
      return !hasMatchingRequest
    })

    // 更新是否还有更多数据（过滤场景也根据返回数量判断）
    hasMore.value = validArticles.length === pageSize

    // 只在完整刷新时更新缓存
    if (isRefresh) {
      await localforage.setItem('articles-cache', validArticles)
    }

  } catch (error) {
    console.error('获取文章列表失败:', error)
    ElMessage.error('get article list failed ,please try again later')
  } finally {
    isLoading.value = false
  }
}

// 修改 filteredArticles 计算属性
const filteredArticles = computed(() => {
  let result = [...optimisticCards.value, ...articles.value]


  return result
})

// 修改删除请求的方法
const deleteRequest = async (requestId: string) => {
  try {
    const { error } = await supabase
      .from('keep_article_requests')
      .delete()
      .eq('id', requestId)

    if (error) throw error

    // 从列表中移除该项
    articles.value = articles.value.filter(article => 
      !('requestId' in article) || article.requestId !== requestId
    )
    
    // 同时清理对应的乐观更新卡片
    optimisticCards.value = optimisticCards.value.filter(opt => 
      opt.requestId !== requestId
    )
    
    ElMessage.success(t('upload.message.deleteSuccess'))
  } catch (error) {
    console.error('删除请求失败:', error)
    ElMessage.error(t('upload.message.deleteFailed'))
  }
}

// 修改组件卸载时的清理
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  stopPolling()
})


// 修改登录成功的处理函数
const handleLoginSuccess = async () => {
  showLoginModal.value = false
  
  try {
    await authStore.loadUser()
    
    if (!authStore.user?.id) {
      console.error('[handleLoginSuccess] User information not loaded properly')
      return
    }
    
    await fetchArticles()
    
    // 处理待上传的URL
    const pendingUrl = localStorage.getItem('pendingUploadUrl')
    if (pendingUrl && articleRequestFormRef.value && authStore.isAuthenticated) {
      articleRequestFormRef.value.quickSubmit(pendingUrl)
      localStorage.removeItem('pendingUploadUrl')
    }
  } catch (error) {
    console.error('[handleLoginSuccess] Error:', error)
    ElMessage.error(t('error.loginFailed'))
  }
}

// 修改 onMounted 钩子
onMounted(async () => {
  console.log('[onMounted] Component mounting, auth status:', authStore.isAuthenticated)
  
  // 先检查登录状态
  await authStore.loadUser()
  console.log('[onMounted] User loaded, new auth status:', authStore.isAuthenticated)
  
  if (!authStore.isAuthenticated) {
    showLoginModal.value = true
    // 未登录时直接返回，不执行后续数据获取
    return
  }
  
  // 只在登录状态下执行数据获取
  console.log('[onMounted] User is authenticated, initializing data')

  try {
    // 获取文章和作者数据
    await Promise.all([
      fetchArticles()
    ])
  } catch (error) {
    console.error('[onMounted] Error loading data:', error)
  } finally {
  }
  

  // 添加滚动监听
  window.addEventListener('scroll', handleScroll)

  // 检查是否有待处理的URL
  const pendingUrl = localStorage.getItem('pendingUploadUrl')
  if (pendingUrl && authStore.isAuthenticated) {
    // 等待组件完全挂载
    await nextTick()
    
    // 如果用户已登录且组件已挂载，则打开上传modal
  }
})


const handleLogout = async () => {
  try {
    console.log('[handleLogout] Starting logout process')
    
    // 2024-03-24: 清空本地数据（无论如何都要执行）
    const clearLocalState = () => {
      articles.value = []
      authors.value = []
      selectedAuthors.value = []
      selectedChannels.value = []
      currentPage.value = 1
      hasMore.value = true
      isLoading.value = false
      
      // 清理其他可能的本地存储数据
      localStorage.removeItem('pendingUploadUrl')
      localStorage.removeItem('lastViewedArticle')
      
      // 停止所有轮询
      if (typeof stopPolling === 'function') {
        stopPolling()
      }
    }
    
    clearLocalState()
    
    // 执行登出
    try {
      await authStore.signOut()
    } catch (error: any) {
      // 如果是 session missing，视为正常的登出状态
      if (error.message?.includes('Auth session missing')) {
        console.log('[handleLogout] Session already expired, treating as logged out')
      } else {
        // 其他错误才抛出
        throw error
      }
    }
    
    // 不管是正常登出还是 session missing，都显示登出成功
    ElMessage.success(t('auth.logoutSuccessMessage'))
    
    // 2024-03-24: 确保用户看到登出后的界面
    showLoginModal.value = true
    
  } catch (error) {
    // 只有真正的错误才会到这里
    console.error('[handleLogout] Error:', error)
    ElMessage.error(t('auth.logoutFailedMessage'))
  }
}


const { t } = useI18n()




// 添加滚动加载处理函数
const handleScroll = () => {
  // 2024-03-15: 未登录用户不执行滚动加载
  if (!authStore.isAuthenticated) return
  
  // 获取滚容
  const container = document.documentElement
  
  // 计算距离底部的距离
  const bottomOfWindow = container.scrollHeight - container.scrollTop - container.clientHeight
  
  // 当距离底部100px时加载更多
  if (bottomOfWindow < 100 && !isLoading.value && hasMore.value) {
    currentPage.value++
    fetchArticles()
  }
}

// 修改 PullToRefresh 组件的刷新处理
const handleRefresh = async () => {
  await fetchArticles(true) // 传入 true 表示刷新
}

const articleRequestFormRef = ref<InstanceType<typeof ArticleRequestForm> | null>(null)


// 添加新的处理函数
const handleArticleRefresh = async () => {
  await fetchArticles(true)
}

// 修改 handleUploadSuccess 函数
const handleUploadSuccess = (url: string) => {
  addOptimisticCard(url)
  // 清空输入框
  handleClearInput()
  // 开始轮询更新状态
  startPolling()
}



// 添加处理函数
const handleClearInput = () => {
  requestUrl.value = ''
  // 移除输入框焦点
  const inputElement = document.querySelector('input[type="text"]') as HTMLInputElement
  if (inputElement) {
    inputElement.blur()
  }
}

// 在script setup部分添加handleLoginModalClose函数
const handleLoginModalClose = () => {
  // 2024-03-21: 只有在已登录状态下才允许关闭登录框
  if (authStore.isAuthenticated) {
    showLoginModal.value = false
  }
}

// 兼容移动端 touch：只在 touchend 触发一次点击逻辑
const handleTouchEnd = (e: TouchEvent) => {
  e.preventDefault()
  e.stopPropagation()
  toggleMineOnly()
}

// 简单切换“只看我上传”，并重置分页与数据
const toggleMineOnly = async () => {
  // 立即给用户反馈
  isLoading.value = true
  // 切换状态并持久化（实际重载由 watcher 触发）
  mineOnly.value = !mineOnly.value
  try { localStorage.setItem('home-mine-only', mineOnly.value ? '1' : '0') } catch {}
  // 直接重置并重新加载，确保点击必然生效
  await resetPageState()
}

// 如需响应其它地方修改 mineOnly，可恢复 watcher；目前点击已直接触发刷新

// 初始化：读取本地持久化，保证返回详情页后保持筛选
try {
  const saved = localStorage.getItem('home-mine-only')
  if (saved === '1') {
    mineOnly.value = true
  }
} catch {}




// 在 script setup 部分添加
const isNewUser = computed(() => {
  // 在加载状态下返回 null，避免显示任何布局
  if (isLoading.value) {
    return null
  }
  return articles.value.length === 0 && optimisticCards.value.length === 0
})

// 修改 handleSubmit 函数
const handleSubmit = (url: string) => {
  if (articleRequestFormRef.value) {
    articleRequestFormRef.value.quickSubmit(url)
    handleClearInput()
  }
}
</script>

<style scoped>
/* 添加滚动条样式 */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: #CBD5E0 #EDF2F7;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #EDF2F7;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: #CBD5E0;
  border-radius: 4px;
}

/* 添加容器过渡动画 */
.my-uploads-section {
  transition: all 0.3s ease;
}

.articles-section {
  width: 100% !important;
  max-width: 1440px;
  margin: 0 auto;
}

.articles-grid {
  display: grid;
  gap: 28px;
  width: 100%;
  margin: 0 auto;
}

/* 在桌面端时强制显示3列，并设置合适的列 */
@media (min-width: 1199px) {
  .articles-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* 在中等屏幕上显示2列 */
@media (min-width: 900px) and (max-width: 1200px) {
  .articles-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 在移动端显示1列 */
@media (max-width: 450px) {
  .articles-grid {
    grid-template-columns: 1fr;
  }
}

/* 确保架图卡片与实际文章卡片样式一致 */
.article-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 保持原有的网格布局样式 */
.articles-grid {
  display: grid;
  gap: 28px;
  width: 100%;
  margin: 0 auto;
}

/* 添加骨架屏卡片样式 */
.card-container {
  display: flex;
  width: 100%;
  min-width: 340px;
  max-width: 450px;
  height: 190px;
  padding: 12px;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
  border-radius: 12px;
  border: 1px solid #F2F2F2;
  background: #FFF;
  box-shadow: 0px 0px 8px 0px rgba(0, 0, 0, 0.10);
}

@media (min-width: 400px) {
  .card-container [class*="w-[120px]"] {
    width: 190px;
  }
}

/* 添加骨架屏动画 */
.bg-gray-200 {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .5;
  }
}

/* 2024-03-21: 添加登录modal的z-index样式 */
:deep(.login-modal) {
  z-index: 9999;
}

/* 2024-03-21: 确保其他fixed元素的z-index低于modal */
.fixed {
  z-index: 40;
}

/* 添加反馈表单容器样式 */
.feedback-container {
  display: inline-block;
  position: relative;
}

/* 2024-03-22: 添加输入框高亮动画 */
.input-highlight::placeholder {
  animation: textHighlight 1s ease-out;
  color: #3B82F6;
}

@keyframes textHighlight {
  0% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.5);
  }
  100% {
    opacity: 0.3;
    transform: scale(1);
  }
}

/* 2024-03-22: 修改placeholder文字动画 */
input::placeholder {
  transition: all 0.3s ease;
}

/* 添加空状态卡片样式 */
.empty-article-card {
  display: flex;
  width: 100%;
  min-width: 340px;
  max-width: 450px;
  height: 190px;
  padding: 12px;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
  border-radius: 12px;
  border: 1px solid #F2F2F2;
  background: #FFF;
  box-shadow: 0px 0px 8px 0px rgba(0, 0, 0, 0.10);
  cursor: pointer;
  transition: all 0.3s ease;
}

.empty-article-card:hover {
  transform: translateY(-2px);
  box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
}

.empty-article-card .divider {
  width: 100%;
  height: 0;
  border-top: 1px solid #EEE;
  margin: 0;
}

.empty-article-card .card-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 24px;
}

.empty-article-card .author-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.empty-article-card .channel-date {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 8px;
}

.empty-article-card .channel-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* 添加新的样式 */
.channel-icon {
  @apply w-6 h-6 transition-transform duration-300;
}

.channel-icon:hover {
  @apply transform scale-110;
}

/* 添加新的样式 */
input::placeholder {
  color: #9CA3AF;
}

input:focus::placeholder {
  color: #6B7280;
}

/* 输入框聚焦时的阴影效果 */
input:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 平台图标悬停效果 */
img.transform:hover {
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}
</style>

