<template>
  <!-- 根容器 -->
  <div class="min-h-screen">
    
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
              <!-- 2024-03-19: 添加beta标记 -->
              <span class="hidden sm:inline-block px-1.5 py-0.5 bg-gradient-to-r from-pink-500 to-purple-500 text-white text-xs rounded-full font-medium transform hover:scale-105 transition-transform">
                BETA
              </span>
            </h1>
          </div>
          <!-- 2024-03-22: 添加介绍文字 -->
          <p class="mt-1 text-xs sm:text-sm bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent font-medium animate-pulse whitespace-nowrap">
            <!-- 移动端显示简短文案 -->
            <span class="sm:hidden">Quick video & audio digest </span>
            <!-- 桌面端显示完整文案 -->
            <span class="hidden sm:inline">Quick video & audio digest</span>
          </p>
        </div>

     <!-- 2024-03-19: Early Access横幅 - 仅在桌面端显示在导航栏中 -->
     <div class="hidden sm:block bg-white py-2 text-center text-pink-500 font-medium relative -ml-20">
      <div 
          class="cursor-pointer group"
          @click="feedbackStore.showForm()"
        >
          <p class="text-base animate-bounce  text-pink-500 ">
            <span class="">📨 Dear early adopters, </span>
            <span class="text-blue-500 font-medium group-hover:text-blue-600 transition-colors">Click here</span>
            <span class=""> to share your feedback and shape our future!</span>
            <span class="ml-1 inline-block animate-bounce">📨</span>
          </p>
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

    <!-- 主要内容区域 -->
    <pull-to-refresh class="mt-[0px]" :onRefresh="handleRefresh">
      <div class="px-4 sm:px-8 py-6 overflow-x-hidden">
        <!-- 修改容器最大宽度并确保居中 -->
        <div class="max-w-screen-2xl mx-auto w-full px-2 sm:px-0">
          <!-- 修改上传框的外边距和响应式布局 -->
          <div class="flex flex-wrap items-center gap-2 sm:gap-4 mb-4 sm:mb-6 p-3 sm:p-6 bg-white rounded-lg sm:rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-200">
            <!-- 标题和图标容器 - 移动端隐藏标题，保留图标 -->
            <div class="flex items-center gap-2 sm:gap-4 w-full sm:w-auto mb-2 sm:mb-0">
              <!-- 标题 - 仅在桌面端显示 -->
              <h3 class="hidden ext-xl sm:text-2xl font-bold text-gray-800 whitespace-nowrap items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 sm:h-8 sm:w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
                </svg>
                {{ t('summarize.title') }}
              </h3>
              
              <!-- 渠道图标 - 移动端和桌面端分别处理 -->
              <div class="flex items-center gap-2 sm:gap-3 ml-0 sm:ml-4">
                <img 
                  v-for="(channel) in ['youtube', 'apple-podcast', 'spotify', 'web']"
                  :key="channel"
                  :src="`/images/icons/${channel}.svg`"
                  :alt="channel"
                  class="w-4 h-4 sm:w-6 sm:h-6"
                />
              </div>
            </div>

            <!-- URL输入框和上传按钮容器 -->
            <div class="flex flex-col sm:flex-1 w-full sm:flex-row items-center gap-2 sm:gap-4">
              <!-- 文章URL输入框 -->
              <div class="relative flex-grow w-full">

                <input
                  type="text"
                  v-model="requestUrl"
                  :placeholder="t('summarize.urlPlaceholder')"
                  :class="['w-full sm:flex-grow pl-3 pr-12 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-000 focus:border-transparent bg-gray-100 transition-all duration-300', 
                    { 'input-highlight': isHighlighted }]"
                  @focus="handleInputFocus"
                  @click="handleInputClick"
                  @blur="handleInputBlur"
                  @keyup.enter="handleNewUploadClick('url')"
                />
                <!-- 添加回车图标，只在输入框激活时显示 -->
                <img 
                  v-if="isInputFocused"
                  src="/images/icons/enter.svg" 
                  alt="Press Enter" 
                  class="absolute right-3 sm:right-4 top-1/2 transform -translate-y-1/2 w-6 h-6 sm:w-8 sm:h-8 opacity-100 transition-opacity duration-200 cursor-pointer hover:scale-110 transition-transform"
                  @click.prevent="handleNewUploadClick('url')"
                  @touchstart.prevent="handleNewUploadClick('url')"
                />
              </div>
              
              <!-- 上传按钮 - 隐藏但保留功能 -->
              <div class="hidden w-[80px] sm:w-[100px] self-center sm:self-auto sm:flex-shrink-0 sm:mr-2 mt-2 sm:mt-0">
                <ArticleRequestForm 
                  ref="articleRequestFormRef"
                  @refresh="handleArticleRefresh"
                  @click="() => submitRequest(requestUrl)"
                  @uploadSuccess="handleUploadSuccess"
                  @clearInput="handleClearInput"
                />
              </div>
            </div>
          </div>
        </div>

          <!-- 文章列表区域的容器结构 -->
          <div class="articles-section">
            <!-- 文章标题和上传按钮 -->
            <div class="flex justify-between items-center mb-[10px]">
              <h2 class="font-['PingFang_SC'] text-[20px] font-semibold leading-[28px] text-[#000000]">
                {{ t('home.articles.title') }}
              </h2>
              
              <!-- 隐藏但保留功能的上传按钮 -->
              <div class="hidden flex items-center gap-2">
                <button 
                  @click="handleNewUploadClick('url')"
                  class="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  <img src="/images/icons/upload.svg" alt="Upload" class="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <!-- 文章卡片网格容器 -->
            <div class="articles-grid">
              <!-- 实际文章列表 -->
              <template v-if="filteredArticles.length > 0">
                <ArticleCard
                  v-for="article in filteredArticles"
                  :key="'requestId' in article ? article.requestId : article.id"
                  :article="article"
                  @delete="deleteRequest"
                />
              </template>

              <!-- 2024-03-24: 添加空状态下的兜底卡片 -->
              <template v-else-if="!isLoading">
                <div class="empty-article-card" @click="handleEmptyCardClick">
                  <!-- 上半部分：标题和图片区域 -->
                  <div class="flex justify-between gap-3">
                    <!-- 左侧标题区域 -->
                    <div class="flex flex-col gap-2 flex-1">
                      <div class="text-xl font-semibold text-gray-900">
                        {{ 'Paste your first link'}}
                      </div>
                      <div class="text-base text-gray-500 mt-1">
                        Support YouTube, Spotify, Apple Podcast 
                      </div>
                    </div>
                    <!-- 右侧图片区域 -->
                    <div class="w-[120px] h-[120px] bg-gray-50 rounded-xl flex items-center justify-center">
                      <img :src="'/images/icons/upload.svg'" alt="Link" class="w-12 h-12">
                    </div>
                  </div>

                  <!-- 分割线 -->
                  <div class="divider"></div>

                  <!-- 底部图标区域 -->
                  <div class="card-bottom">

                    <!-- 右侧渠道图标 -->
                    <div class="channel-date">
                      <div class="flex items-center gap-2">
                        <img src="/images/icons/youtube.svg" alt="Youtube" class="channel-icon">
                        <img src="/images/icons/apple-podcast.svg" alt="Apple" class="channel-icon">
                        <img src="/images/icons/spotify.svg" alt="Spotify" class="channel-icon">
                      </div>
                    </div>
                  </div>
                </div>
              </template>

              <!-- 加载状态显示骨架图 -->
              <template v-if="isLoading">
                <div v-for="n in 27" :key="n" 
                  class="card-container"
                >
                  <!-- 骨架屏内容 -->
                  <div class="flex flex-col h-full w-full gap-3">
                    <!-- 上半部分 -->
                    <div class="flex justify-between gap-3">
                      <!-- 左侧标题骨架 -->
                      <div class="flex flex-col gap-2 flex-1">
                        <div class="h-6 bg-gray-200 rounded w-4/5"></div>
                        <div class="h-6 bg-gray-200 rounded w-3/4"></div>
                        <div class="h-6 bg-gray-200 rounded w-2/3"></div>
                      </div>
                      <!-- 右侧图片骨架 -->
                      <div class="w-[120px] h-[120px] bg-gray-200 rounded-xl flex-shrink-0"></div>
                    </div>

                    <!-- 分割线 -->
                    <div class="h-[1px] bg-gray-200 w-full"></div>

                    <!-- 底部信息骨架 -->
                    <div class="flex justify-between items-center">
                      <!-- 左侧作者信息骨架 -->
                      <div class="flex items-center gap-2">
                        <div class="w-5 h-5 bg-gray-200 rounded-full"></div>
                        <div class="h-4 bg-gray-200 rounded w-20"></div>
                      </div>
                      <!-- 右侧日期和渠道骨架 -->
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

          <!-- 加载状态提示 -->
          <div v-if="authStore.isAuthenticated && (isLoading || hasMore)" class="text-center py-4">
            <div v-if="isLoading" class="flex justify-center items-center space-x-2">
              <div class="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <span class="text-gray-500">{{ t('common.loading') }}</span>
            </div>
            <div v-else-if="hasMore" class="text-gray-500">
              {{ t('common.scrollToLoadMore') }}
            </div>
          </div>
          
        </div>
    </pull-to-refresh>



    <!-- 将 modal 移到 pull-to-refresh 外部 -->
    <Teleport to="body">
      <article-request-form-modal 
        v-if="showUploadModal"
        @close="showUploadModal = false"
        @refresh="fetchArticles"
      />
    </Teleport>

    <!-- 2024-03-24: 添加移动端固定在右下角的反馈按钮 -->
    <div 
      class="sm:hidden fixed bottom-12 right-0 z-[1002] cursor-pointer"
      @click="feedbackStore.showForm()"
    >
      <div class="bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full px-4 py-2 shadow-lg transform hover:scale-105 transition-all duration-300 flex items-center justify-center w-[90px] h-[36px]">
        <span class="text-sm font-medium whitespace-nowrap">Feedback</span>
      </div>
    </div>

    <!-- 2024-03-24: 添加反馈表单组件 -->
    <FeedbackForm 
      :is-visible="feedbackStore.showFeedbackForm"
      @close="feedbackStore.closeFeedbackForm"
      @submit="handleFeedbackSubmit"
      class="z-[1003]"
    />
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
import FeedbackForm from '@/components/feedback/FeedbackForm.vue'
import { useFeedbackStore } from '../stores/feedback'

const authStore = useAuthStore()
const showLoginModal = ref(false)
const showUploadModal = ref(false)
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

interface KeepArticleView {
  article_id: string
  created_at: string
  is_author: boolean
  article: {
    id: string
    title: string
    cover_image_url?: string
    channel?: string
    created_at: string
    tags?: string[]
    publish_date?: string
    author_id?: number
    content?: string | null
    original_link?: string | null
    author?: Author
  }
}



// 修改变量定义
const articles = ref<(ArticleType | ArticleRequest)[]>([])
const optimisticCards = ref<OptimisticCard[]>([])
const authors = ref<Author[]>([])

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

// 添加个性来判断是否有筛选条件
const hasFilters = computed(() => {
  return selectedTag.value !== 'all' || 
         selectedChannels.value.length > 0 || 
         selectedAuthors.value.length > 0
})

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
        const { data: newArticles } = await supabase
          .from('keep_article_views')
          .select(`
            article_id,
            created_at,
            is_author,
            article:keep_articles(
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
            )
          `)
          .eq('user_id', authStore.user?.id)
          .order('created_at', { ascending: false })
          .limit(pageSize)

        if (newArticles) {
          // 处理新文章数据
          const validNewArticles = ((newArticles || []) as unknown as KeepArticleView[]).map(view => ({
            ...view.article,
            is_author: view.is_author,
            status: 'processed' as const,
            content: view.article?.content || '',
            original_link: view.article?.original_link || ''
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
  optimisticCards.value = [card, ...optimisticCards.value]
  
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
  if (url.includes('youtube.com') || url.includes('youtu.be')) {
    return 'youtube'
  }
  if (url.includes('open.spotify.com')) {
    return 'spotify'
  }
  if (url.includes('podcasts.apple.com')) {
    return 'apple'
  }
  return 'webpage'
}


// 修改 fetchArticles 函数
const fetchArticles = async (isRefresh: boolean = false) => {
  // 添加登录状态检查
  if (!authStore.isAuthenticated) {
    console.log('[fetchArticles] User not authenticated, skipping fetch')
    return
  }

  try {
    if (isRefresh) {
      currentPage.value = 1
    }

    isLoading.value = true

    // 构建查询
    const { data: views, error } = await supabase 
      .from('keep_article_views')
      .select(`
        article_id,
        created_at,
        is_author,
        article:keep_articles(
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
        )
      `)
      .eq('user_id', authStore.user?.id)
      .order('created_at', { ascending: false })
      .range((currentPage.value - 1) * pageSize, currentPage.value * pageSize - 1)

    if (error) throw error

    // 修改：每次刷新或第一页加载时都获取处理中和失败的请求
    let requests: any[] = []
    if (isRefresh || currentPage.value === 1) {
      const { data: requestsData } = await supabase 
        .from('keep_article_requests')
        .select('*')
        .eq('user_id', authStore.user?.id)
        .in('status', ['processing', 'failed'] as ArticleStatus[])
        .order('created_at', { ascending: false })
      
      requests = requestsData || []
    }

    // 处理文章数据
    const validArticles = ((views || []) as unknown as KeepArticleView[]).map(view => ({
      ...view.article,
      is_author: view.is_author,
      status: 'processed' as const,
      content: view.article?.content || '',
      original_link: view.article?.original_link || ''
    })).filter((article): article is ArticleType => 
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

    // 更新是否还有更多数据
    hasMore.value = hasFilters.value ? false : validArticles.length === pageSize

    // 只在完整刷新时更新缓存
    if (isRefresh) {
      await localforage.setItem('articles-cache', validArticles)
    }

  } catch (error) {
    console.error('获取文章列表失败:', error)
    ElMessage.error('获取文章列表失败，请稍后重试')
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
    console.log('[handleLoginSuccess] Starting login success handling')
    // 等待用户信息完全加载
    await authStore.loadUser()
    
    // 确保用户信息已加载完成
    if (!authStore.user?.id) {
      console.error('[handleLoginSuccess] User information not loaded properly')
      return
    }
    
    console.log('[handleLoginSuccess] Loading data after login')
    // 2024-03-15: 登录成功后初始化作者相关状态

    try {
      await Promise.all([
        fetchArticles()
      ])

      
    } catch (error) {
      console.error('[handleLoginSuccess] Error loading data:', error)
      ElMessage.error(t('error.loginFailed'))
      return
    }
    
    // 最后处理待上传的URL
    const pendingUrl = localStorage.getItem('pendingUploadUrl')
    if (pendingUrl && articleRequestFormRef.value && authStore.isAuthenticated) {
      articleRequestFormRef.value.openModalWithUrl(pendingUrl)
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
  
  // 预加载常用资源
  const preloadLinks = [
    '/images/icons/logo.svg',
    // 其他常用资源...
  ]
  
  preloadLinks.forEach(link => {
    const preload = document.createElement('link')
    preload.rel = 'preload'
    preload.href = link
    preload.as = link.endsWith('.svg') ? 'image' : 'script'
    document.head.appendChild(preload)
  })

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
    
    // 2024-03-15: 先清空本地数据
    articles.value = []
    authors.value = []
    selectedAuthors.value = []
    selectedChannels.value = []
    currentPage.value = 1
    hasMore.value = true
    isLoading.value = false
    
    
    // 执行登出
    await authStore.signOut()
    ElMessage.success(t('auth.logoutSuccessMessage'))
    
  } catch (error) {
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

// 修改剪贴板处理函数
const handlePaste = async () => {
  try {
    // 检查剪贴板API是否可用
    if (!navigator.clipboard) {
      console.warn('Clipboard API not available')
      return
    }
    
    const text = await navigator.clipboard.readText()
    // 最简单的URL判断：包含http或https，且包含至少一个点号
    if (text.includes('http') && text.includes('.')) {
      requestUrl.value = text.trim()
    }
  } catch (err) {
    console.error('Failed to read clipboard:', err)
    // 静默失败，不影响用户体验
  }
}


// 修改 submitRequest 函数
const submitRequest = (url?: string) => {
  if (!url) return
  
  if (!authStore.isAuthenticated) {
    localStorage.setItem('pendingUploadUrl', url)
    showLoginModal.value = true
    return
  }

  showUploadModal.value = true
}


// 添加新的处理函数
const handleArticleRefresh = async () => {
  await fetchArticles(true)
}

// 修改 handleUploadSuccess 函数
const handleUploadSuccess = (url: string) => {
  // 移除 async/await，直接调用
  addOptimisticCard(url)
}


// 修改 handleNewUploadClick 函数
const handleNewUploadClick = (type: 'url' | 'web' | 'file' = 'url') => {
  if (!authStore.isAuthenticated) {
    showLoginModal.value = true
    return
  }

  // 2024-03-20: 添加特权用户判断
  const isPrivilegedUser = authStore.user?.id === '40568d0d-cd39-4bbe-8cba-634e9484b5cc'

  if (type === 'url') {
    if (requestUrl.value) {
      if (isPrivilegedUser) {
        // 特权用户保持原有的modal显示
        if (articleRequestFormRef.value) {
          articleRequestFormRef.value.openModalWithUrl(requestUrl.value)
        }
      } else {
        // 普通用户直接提交，默认英文
        if (articleRequestFormRef.value) {
          articleRequestFormRef.value.quickSubmit(requestUrl.value)
        }
      }
    } else {
      // 如果没有URL，特权用户显示modal，普通用户不做操作
      if (isPrivilegedUser) {
        showUploadModal.value = true
      }
    }
  }
}

// 添加输入框焦点状态
const isInputFocused = ref(false)

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

// 添加反馈表单相关的状态和方法
const feedbackStore = useFeedbackStore()

// 处理反馈表单提交
const handleFeedbackSubmit = (formData: {
  needProduct: boolean
  satisfiedSummary: boolean
  allowContact: boolean
}) => {
  console.log('Feedback submitted:', formData)
  feedbackStore.closeFeedbackForm()
  // TODO: 这里后续会添加发送到后端的逻辑
}

// 2024-03-22: 添加输入框高亮动画
const isHighlighted = ref(false)
const showAnimatedPlaceholder = ref(true)

// 2024-03-22: 添加点击图标的处理函数
const handleAddIconClick = () => {
  // 触发placeholder文字高亮动画
  isHighlighted.value = true
  showAnimatedPlaceholder.value = false
  
  // 重置高亮状态
  setTimeout(() => {
    isHighlighted.value = false
    showAnimatedPlaceholder.value = true
  }, 600)

  // 获取输入框元素并聚焦
  const inputElement = document.querySelector('input[type="text"]') as HTMLInputElement
  if (inputElement) {
    inputElement.focus()
  }
}

// 2024-03-22: 修改输入框焦点处理函数
const handleInputFocus = async () => {
  isInputFocused.value = true
  // 只在桌面端执行粘贴操作
  if (!('ontouchstart' in window)) {
    try {
      await handlePaste()
    } catch (error) {
      console.error('Failed to paste:', error)
    }
  }
}

const handleInputBlur = () => {
  isInputFocused.value = false
}

// 2024-03-22: 添加输入框点击处理函数
const handleInputClick = async () => {
  // 只在移动端执行粘贴操作
  if ('ontouchstart' in window) {
    try {
      await handlePaste()
    } catch (error) {
      console.error('Failed to paste on mobile:', error)
    }
  }
}

// 在 script setup 部分添加处理函数
const handleEmptyCardClick = async () => {
  // 1. 触发输入框高亮动画
  handleAddIconClick();
  
  // 2. 获取焦点并触发粘贴
  const inputElement = (window?.document?.querySelector('input[type="text"]') as HTMLInputElement | null);
  if (inputElement) {
    inputElement.focus();
    handlePaste();
  }
  
  // 3. 如果有有效URL，触发上传
  if (requestUrl.value && (requestUrl.value.startsWith('http://') || requestUrl.value.startsWith('https://'))) {
    handleNewUploadClick('url');
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
</style>

