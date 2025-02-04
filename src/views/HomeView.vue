<template>
  <!-- 根容器 -->
  <div class="min-h-screen">
    
  <!-- 网络状态提示 - 保留原有的离线提示，添加弱网提示 -->
      <div v-if="!isOnline" 
          class="bg-yellow-50 p-4">
          <div class="flex items-center justify-center text-yellow-700">
            <span>{{ t('home.network.offline') }}</span>
          </div>
      </div>
      <div v-else-if="isSlowConnection" 
          class="bg-blue-50 p-4">
          <div class="flex items-center justify-center text-blue-700">
            <span>{{ t('home.network.weak') }}</span>
          </div>
      </div>

    <!-- 顶部导航栏 -->
  <header class="fixed top-0 left-0 right-0 bg-white z-40 w-full">
      <!-- 导航栏内容容器 -->
      <div class="flex justify-between items-center px-4 h-[90px] min-w-[378px] max-w-[1440px] mx-auto">
        <!-- 左侧Logo和标题容器 -->
        <div class="flex flex-col">
          <div class="flex items-center gap-2">
            <!-- 网站Logo图片 -->
            <img 
              src="/images/icons/logo.svg" 
              alt="Keep Up Logo" 
              class="w-[48px] h-[48px] flex-shrink-0" 
            />
            <!-- 网站标题文本 -->
            <h1 class="text-[20px] text-[#333333] font-[400] leading-6 font-['PingFang_SC'] flex items-center gap-2">
              {{ t('home.title') }}
              <!-- 2024-03-19: 添加beta标记 -->
              <span class="px-1.5 py-0.5 bg-gradient-to-r from-pink-500 to-purple-500 text-white text-xs rounded-full font-medium transform hover:scale-105 transition-transform">
                BETA
              </span>
            </h1>
          </div>
          <!-- 2024-03-22: 添加介绍文字 -->
          <p class="mt-1 text-sm bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent font-medium animate-pulse">
            Quick video & audio digest - no rewatching
          </p>
        </div>



     <!-- 2024-03-19: 中间的Early Access横幅 -->
     <div class="bg-white py-2 text-center text-pink-500 font-medium relative">
        <div 
          class="cursor-pointer"
          @mouseenter="showFeedbackForm = true"
        >
          <p class="animate-bounce">{{ t('home.earlyAccess.feedback') }}</p>
          <!-- 反馈表单 -->
          <FeedbackForm 
            :is-visible="showFeedbackForm"
            @close="showFeedbackForm = false"
            @submit="handleFeedbackSubmit"
          />
        </div>
      </div>
      
      

        
        <!-- 右侧导航元素容器 - 增加右侧padding并调整gap -->
        <div class="flex items-center gap-3 pr-2">
          <!-- 语言切换组件 先不要了 -->
         <!-- <language-switch/> -->
      
          <!-- 已登录用户信息区域 -->
          <template v-if="authStore.isAuthenticated">
            <!-- 用户头像 -->
            <img 
              :src="authStore.user?.user_metadata?.avatar_url || '/images/icons/avatar.svg'" 
              :alt="authStore.user?.email || 'User Avatar'" 
              class="w-[32px] h-[32px] rounded-full"
            />
            <!-- 登出按钮 - 增加最小宽度确保文字完整显示 -->
            <button 
              @click="handleLogout" 
              class="text-gray-600 hover:text-gray-800 min-w-[64px] h-[32px] text-center"
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
        <div class="max-w-screen-2xl mx-auto w-full">
          <!-- 修改上传框的外边距 -->
          <div class="flex flex-wrap items-center gap-4 mb-6 p-4 sm:p-6 bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-200">
            <!-- 标题和图标容器 -->
            <div class="flex items-center gap-4 w-full sm:w-auto mb-2 sm:mb-0">
              
              <!-- 标题 - 优化字体大小和响应式显示 -->
              <h3 class="hidden text-xl sm:text-2xl font-bold text-gray-800 whitespace-nowrap flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 sm:h-8 sm:w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
                </svg>
                {{ t('summarize.title') }}
              </h3>
              
              <!-- 4个渠道图标 - 优化响应式显示 -->
              <div class="flex items-center gap-3 ml-auto sm:ml-4">
                <!-- 修改渠道图标icon的命名要和svg的文件一样-->  
                <img 
                  v-for="(channel, index) in ['youtube', 'apple-podcast', 'spotify', 'web']"
                  :key="channel"
                  :src="`/images/icons/${channel}.svg`"
                  :alt="channel"
                  class="w-5 h-5 sm:w-6 sm:h-6"
                  :title="t(`home.channels.${channel}`)"
                />
              </div>
            </div>

            <!-- URL输入框和上传按钮容器 -->
            <div class="flex flex-col sm:flex-1 w-full sm:flex-row items-center gap-4">
              
              <!-- 文章URL输入框 -->
              <div class="relative flex-grow">
                <img 
                  src="/images/icons/add.svg" 
                  alt="Add" 
                  class="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 cursor-pointer"
                  @click="handleAddIconClick"
                />
                <input
                  type="text"
                  v-model="requestUrl"
                  :placeholder="t('summarize.urlPlaceholder')"
                  :class="['w-full sm:flex-grow pl-12 pr-12 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-000 focus:border-transparent bg-gray-100 transition-all duration-300', 
                    { 'input-highlight': isHighlighted }]"
                  @click="handlePaste"
                  @focus="handleInputFocus"
                  @blur="handleInputBlur"
                  @keyup.enter="handleNewUploadClick('url')"
                />
                <!-- 添加回车图标，只在输入框激活时显示 -->
                <img 
                  v-if="isInputFocused"
                  src="/images/icons/enter.svg" 
                  alt="Press Enter" 
                  class="absolute right-4 top-1/2 transform -translate-y-1/2 w-8 h-8 opacity-100 transition-opacity duration-200"
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
                  {{ t('upload.button.newUpload') }}
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
              <template v-else-if="authStore.isAuthenticated && !isLoading">
                <div class="empty-article-card" @click="handleEmptyCardClick">
                  <!-- 上半部分：标题和图片区域 -->
                  <div class="flex justify-between gap-3">
                    <!-- 左侧标题区域 -->
                    <div class="flex flex-col gap-2 flex-1">
                      <div class="text-xl font-semibold text-gray-900">
                        Upload your first summary
                      </div>
                      <div class="text-base text-gray-500 mt-1">
                        Support YouTube, Spotify, Apple Podcast 
                      </div>
                    </div>
                    <!-- 右侧图片区域 -->
                    <div class="w-[120px] h-[120px] bg-gray-50 rounded-xl flex items-center justify-center">
                      <img src="/images/icons/upload.svg" alt="Link" class="w-12 h-12">
                    </div>
                  </div>

                  <!-- 分割线 -->
                  <div class="divider"></div>

                  <!-- 底部图标区域 -->
                  <div class="card-bottom">
                    <!-- 左侧留空 -->
                    <div class="author-info">
                    </div>

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
          
          <!-- 没有更多数据的提示 -->
          <div v-if="!isLoading && (!hasMore || !authStore.isAuthenticated)" class="text-center py-4 text-gray-500">
            {{ authStore.isAuthenticated 
              ? (filteredArticles.length === 0 
                ? 'Paste a link to see summaries in 2 minutes'
                : t('common.noMoreData')) 
              : t('common.loginToViewMore') }}
          </div>
        </div>
    </pull-to-refresh>


    <!-- 网络状态提示 -->
    <div 
      v-if="!isOnline" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div 
        class="bg-white p-6 rounded-lg shadow-lg w-[600px] max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold">{{ t('home.network.offline') }}</h2>
          <button class="text-gray-500">
            <i class="el-icon-close"></i>
          </button>
        </div>

        <div class="flex justify-center items-center mb-4">
          <div 
            class="w-16 h-16 border-4 border-red-500 border-t-transparent rounded-full animate-spin"
          ></div>
        </div>

        <div class="mt-6 flex justify-end space-x-3">
          <button 
            @click="checkConnection" 
            class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            {{ t('common.retry') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 将 modal 移到 pull-to-refresh 外部 -->
    <Teleport to="body">
      <article-request-form-modal 
        v-if="showUploadModal"
        @close="showUploadModal = false"
        @refresh="fetchArticles"
      />
    </Teleport>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, reactive, onMounted, onUnmounted, onActivated, nextTick } from 'vue'
import ArticleCard from '../components/ArticleCard.vue'
import UploadCard from '../components/UploadCard.vue'
import { supabase } from '../supabaseClient'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import LoginModal from '../components/LoginModal.vue'
import type { Article as ArticleType, ArticleRequest, OptimisticCard, KeepArticleView, KeepArticleRequest, Author, DbArticleRequestInsert, ArticleStatus } from '../types/article'
import AuthorSelect from '../components/AuthorSelect.vue'
import ArticleForm from '../components/ArticleForm.vue'
import { getChannelIcon } from '../utils/icons'
import ArticleRequestForm from '../components/ArticleRequestForm.vue'
import { useI18n } from 'vue-i18n'
import LanguageSwitch from '../components/LanguageSwitch.vue'
import PullToRefresh from '../components/PullToRefresh.vue'
import localforage from 'localforage'
import { trackEvent, type EventType } from '../utils/analytics'
import type { Database } from '../types/supabase'
import type { SupabaseClient } from '@supabase/supabase-js'
import FeedbackForm from '@/components/feedback/FeedbackForm.vue'

const authStore = useAuthStore()
const showLoginModal = ref(false)
const showUploadModal = ref(false)
const selectedTag = ref<string>('all')
const selectedChannels = ref<string[]>([])
const selectedAuthors = ref<number[]>([])
const requestUrl = ref('')

// 预定义的标签
const PREDEFINED_TAGS = ['24小时', '博客', '论文', '微', '视频']

// 添加类型定义
interface Author {
  id: number
  name: string
  icon?: string
}

interface ArticleBase {
  id: string
  title: string
  cover_image_url?: string
  channel?: string
  publish_date?: string
  created_at: string
  tags?: string[]
  author_id?: number
  author?: Author
}

interface Article extends ArticleBase {
  is_author: boolean
  status: 'processed'
  content: string
  original_link: string
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

interface ArticleView {
  article_id: string
  created_at: string
  is_author: boolean
  article: ArticleBase & {
    content?: string | null
    original_link?: string | null
  }
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

interface KeepArticleRequest {
  id: string
  url: string
  status: 'processing' | 'processed' | 'failed'
  created_at: string
  error_message?: string
  original_url: string
  platform?: string
  article_id?: string
  user_id: string
}

type DbClient = SupabaseClient<Database>

// 修改变量定义
const articles = ref<(ArticleType | ArticleRequest)[]>([])
const optimisticCards = ref<OptimisticCard[]>([])
const authors = ref<Author[]>([])

// 用预定义的标签替代动态计算的标签
const tags = computed(() => PREDEFINED_TAGS)

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
      updatedRequests.forEach(request => {
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
            articles.value[index] = {
              ...articles.value[index],
              status: 'failed',
              error_message: request.error_message
            }
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
        const { data: newArticles } = await (supabase as DbClient)
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
          const validNewArticles = (newArticles as KeepArticleView[]).map(view => ({
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
            article => 'status' in article && article.status !== 'processed'
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
      if (existingRequest.status === 'processing') {
        const request = {
          id: existingRequest.id,
          url: existingRequest.original_url,
          status: existingRequest.status,
          created_at: existingRequest.created_at,
          error_message: existingRequest.error_message,
          original_url: existingRequest.original_url,
          platform: existingRequest.platform,
          article_id: existingRequest.article_id,
          requestId: existingRequest.id
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

// 添加新的状态来追踪是否已经加载过处理中和失败的请求
const hasLoadedRequests = ref(false)

// 修改 fetchArticles 函数
const fetchArticles = async (isRefresh: boolean = false) => {
  try {
    if (isRefresh) {
      currentPage.value = 1
      hasLoadedRequests.value = false  // 重置请求加载状态
    }

    isLoading.value = true

    // 构建查询
    const { data: views, error } = await (supabase as DbClient)
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

    // 只在首次加载或刷新时获取处理中和失败的请求
    let requests: any[] = []
    if (!hasLoadedRequests.value) {
      const { data: requestsData } = await (supabase as DbClient)
        .from('keep_article_requests')
        .select('*')
        .eq('user_id', authStore.user?.id)
        .in('status', ['processing', 'failed'] as ArticleStatus[])
        .order('created_at', { ascending: false })
      
      requests = requestsData || []
      hasLoadedRequests.value = true  // 标记已加载请求
    }

    // 处理文章数据
    const validArticles = ((views || []) as KeepArticleView[]).map(view => ({
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
    if (isRefresh) {
      // 如果是刷新，则完全替换现有列表
      articles.value = [...typedRequests, ...validArticles]
    } else if (currentPage.value === 1) {
      // 如果是第一页，包含处理中和失败的请求
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

  // 标签筛选
  if (selectedTag.value !== 'all') {
    result = result.filter(article => 
      'tags' in article && Array.isArray(article.tags) && article.tags.includes(selectedTag.value)
    )
  }

  // 渠道筛选
  if (selectedChannels.value.length > 0) {
    result = result.filter(article => 
      'channel' in article && typeof article.channel === 'string' && selectedChannels.value.includes(article.channel)
    )
  }

  // 作者筛选
  if (selectedAuthors.value.length > 0) {
    result = result.filter(article => 
      'author_id' in article && typeof article.author_id === 'number' && selectedAuthors.value.includes(article.author_id)
    )
  }

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

// 添加 loading 状态
const isLoadingAuthors = ref(true)

// 改作者获取函数
const fetchAuthors = async () => {
  try {
    console.log('[fetchAuthors] Starting to fetch authors')
    isLoadingAuthors.value = true

    // 1. 先从 IndexedDB 获取缓存数据
    const cachedAuthors = await localforage.getItem('authors-cache')
    if (cachedAuthors) {
      console.log('[fetchAuthors] Found cached authors:', cachedAuthors)
      authors.value = cachedAuthors as Author[]
      isLoadingAuthors.value = false
    }

    // 2. 如果离线且有缓存，直接返回
    if (!navigator.onLine && cachedAuthors) {
      console.log('[fetchAuthors] Offline mode, using cached data')
      return
    }

    console.log('[fetchAuthors] Fetching authors from API')
    // 3. 从 API 获取数据
    const { data, error } = await supabase
      .from('keep_authors')
      .select('id, name, icon')
      .order('name')

    if (error) {
      console.error('[fetchAuthors] API error:', error)
      throw error
    }

    console.log('[fetchAuthors] Received authors from API:', data)
    if (data && data.length > 0) {
      // 4. 更新 IndexedDB 缓存和状态
      await localforage.setItem('authors-cache', data)
      authors.value = data
    } else {
      console.warn('[fetchAuthors] No authors data received from API')
    }
    
  } catch (error) {
    console.error('[fetchAuthors] Error:', error)
    ElMessage.error(t('error.getAuthorsFailed'))
  } finally {
    console.log('[fetchAuthors] Completed, setting isLoadingAuthors to false')
    isLoadingAuthors.value = false
  }
}

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
    isLoadingAuthors.value = true

    try {
      // 先恢复缓存的状态
      const [savedSelectedAuthors, savedExpanded] = await Promise.all([
        localforage.getItem('selected-authors'),
        localforage.getItem('authors-expanded')
      ])

      if (savedSelectedAuthors) {
        selectedAuthors.value = savedSelectedAuthors as number[]
      }
      if (savedExpanded !== null) {
        isExpanded.value = savedExpanded as boolean
      }

      // 获取文章和作者数据
      await Promise.all([
        fetchArticles(),
        fetchAuthors(),
        updateCacheTimestamp()
      ])

      // 刷新我的上传区域
      if (myUploadsRef.value) {
        await myUploadsRef.value.fetchUserArticles()
      }
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
  
  // 2024-03-21: 先检查登录状态，未登录则显示登录框
  await authStore.loadUser()
  console.log('[onMounted] User loaded, new auth status:', authStore.isAuthenticated)
  
  if (!authStore.isAuthenticated) {
    showLoginModal.value = true
    return
  }
  
  // 如果用户已登录，初始化作者相关状态
  if (authStore.isAuthenticated) {
    console.log('[onMounted] User is authenticated, initializing author data')
    isLoadingAuthors.value = true

    try {
      // 先恢复缓存的状态
      const [savedSelectedAuthors, savedExpanded] = await Promise.all([
        localforage.getItem('selected-authors'),
        localforage.getItem('authors-expanded')
      ])

      if (savedSelectedAuthors) {
        selectedAuthors.value = savedSelectedAuthors as number[]
      }
      if (savedExpanded !== null) {
        isExpanded.value = savedExpanded as boolean
      }

      // 获取文章和作者数据
      await Promise.all([
        fetchArticles(),
        fetchAuthors(),
        updateCacheTimestamp()
      ])
    } catch (error) {
      console.error('[onMounted] Error loading data:', error)
    }
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
    // 确保用户信息已加载
    if (!authStore.user) {
      await authStore.loadUser()
    }
    
    // 等待组件完全挂载
    await nextTick()
    
    // 如果用户已登录且组件已挂载，则打开上传modal
    if (articleRequestFormRef.value && authStore.isAuthenticated) {
      articleRequestFormRef.value.openModalWithUrl(pendingUrl)
      localStorage.removeItem('pendingUploadUrl')
    }
  }
})

const articleForm = ref<Partial<ArticleType>>({
  title: '',
  content: '',
  author_id: undefined,
  tags: [],
  channel: '',
  publish_date: null,
  original_link: null
})

const selectTag = (tag: string): void => {
  selectedTag.value = tag
  resetPageState() // 重置并新获取数据
}

const handleUpload = () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning(t('error.loginFirst'))
    showLoginModal.value = true
    return
  }
  showUploadModal.value = true
}

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
    
    // 清理缓存
    await clearCache()
    
    // 执行登出
    await authStore.signOut()
    ElMessage.success(t('auth.logoutSuccessMessage'))
    
  } catch (error) {
    console.error('[handleLogout] Error:', error)
    ElMessage.error(t('auth.logoutFailedMessage'))
  }
}

const resetForm = () => {
  articleForm.value = {
    title: '',
    content: '',
    author_id: undefined,
    tags: [],
    channel: '',
    publish_date: null,
    original_link: null
  }

  // 提交成功后清除稿
  localStorage.removeItem('articleFormDraft')
}

// 在组顶部定义 formRef
const formRef = ref<InstanceType<typeof ArticleForm> | null>(null)

const submitArticle = async () => {
  try {
    if (!authStore.isAuthenticated) {
      ElMessage.warning(t('error.loginFirst'))
      showLoginModal.value = true
      return
    }

    if (!articleForm.value.title || !articleForm.value.content || !articleForm.value.author_id) {
      ElMessage.error(t('error.requiredArticleFields'))
      return
    }
    
    const submitData = {
      title: articleForm.value.title,
      content: articleForm.value.content,
      author_id: articleForm.value.author_id,
      tags: articleForm.value.tags || [],
      channel: articleForm.value.channel || '',
      publish_date: articleForm.value.publish_date,
      original_link: articleForm.value.original_link,
      user_id: authStore.user?.id
    }

    // 提交文章基本信息
    const { data, error } = await supabase
      .from('keep_articles')
      .insert([submitData])
      .select()
      .single()

    if (error) throw error

    if (formRef.value) {
      // 提交小节内容
      const sectionsData = formRef.value.getSectionsData()
      if (sectionsData.length > 0) {
        const { error: sectionsError } = await supabase
          .from('keep_article_sections')
          .insert(sectionsData.map(section => ({
            ...section,
            article_id: data.id
          })))

        if (sectionsError) throw sectionsError
      }
    }

    ElMessage.success(t('error.updateSuccess'))

    showUploadModal.value = false
    resetForm()
    await fetchArticles()
  } catch (error) {
    console.error('提交文章时出错:', error)
    ElMessage.error(t('error.submitArticleFailed'))
  }
}

// 切换道选择
const toggleChannel = (channel: string) => {
  const index = selectedChannels.value.indexOf(channel)
  if (index === -1) {
    selectedChannels.value.push(channel)
  } else {
    selectedChannels.value.splice(index, 1)
  }
  resetPageState() // 重置并重新获取数据
}

// 切换作者选择
const toggleAuthor = async (author: Author) => {
  const index = selectedAuthors.value.indexOf(author.id)
  if (index === -1) {
    selectedAuthors.value.push(author.id)
  } else {
    selectedAuthors.value.splice(index, 1)
  }
  // 保存选择状态
  await localforage.setItem('selected-authors', selectedAuthors.value)
  resetPageState() // 重置并重新获取数据
}

const { t } = useI18n()

// 修改 getChannelKey 函数
const getChannelKey = (channel: string): string => {
  const keyMap: Record<string, string> = {
    'YouTube': 'youtube',
    'Apple Podcast': 'applePodcast',
    'Spotify': 'spotify',
    'webpage': 'webpage'
  }
  return keyMap[channel] || channel.toLowerCase()
}

// 使用计算属性来根据屏幕大小返回不同的显示数量
const defaultDisplayCount = computed(() => {
  // 使用 window.innerWidth 获取当前视口度
  const width = window.innerWidth
  
  // >= 1280px (xl): 显示16个 (4行)
  if (width >= 1280) return 16
  // >= 1024px (lg): 显示6个 (3行)
  if (width >= 1024) return 6
  // >= 768px (md): 显示4个 (2行)
  if (width >= 768) return 4
  // < 768px: 显示4个 (2行)
  return 4
})

const isExpanded = ref(false)

// 修改展开/收起处理
const toggleExpand = async () => {
  isExpanded.value = !isExpanded.value
  // 保存展开状态
  await localforage.setItem('authors-expanded', isExpanded.value)
}

// 监听窗口大小变化
onMounted(() => {
  const handleResize = () => {
    // 果当前显示的作者数量大于新的默认显示数量，则收起列表
    if (!isExpanded.value && displayedAuthors.value.length > defaultDisplayCount.value) {
      isExpanded.value = false
    }
  }

  window.addEventListener('resize', handleResize)
  
  // 组件卸载时移事件监听
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })
})

// 计算要显示作者列表
const displayedAuthors = computed(() => {
  return isExpanded.value ? authors.value : authors.value.slice(0, defaultDisplayCount.value)
})

// 添加网络状态检测
const isSlowConnection = computed(() => {
  if ('connection' in navigator) {
    const conn = (navigator as any).connection
    return conn.effectiveType === '2g' || conn.effectiveType === 'slow-2g'
  }
  return false
})

// 监听网络状态变化
onMounted(() => {
  if ('connection' in navigator) {
    (navigator as any).connection.addEventListener('change', () => {
      // 网络状态变化时重新获取数据
      if (isOnline.value && !isSlowConnection.value) {
        fetchArticles()
      }
    })
  }
})

// 网络状态检测
const isOnline = ref(navigator.onLine)

// 查网络连接
const checkConnection = async () => {
  try {
    await fetch('/api/health-check')
    isOnline.value = true
  } catch (error) {
    isOnline.value = false
  }
}

// 监听网络状态变化
onMounted(() => {
  window.addEventListener('online', () => {
    isOnline.value = true
    fetchArticles()
  })
  
  window.addEventListener('offline', () => {
    isOnline.value = false
  })
})

onUnmounted(() => {
  window.removeEventListener('online', () => {})
  window.removeEventListener('offline', () => {})
})

// 添加清理缓存的函数
const clearCache = async () => {
  try {
    await localforage.removeItem('articles-cache')
    await localforage.removeItem('authors-cache')
    await localforage.removeItem('selected-authors')
    await localforage.removeItem('authors-expanded')
  } catch (error) {
    console.error('清理缓存失败:', error)
  }
}

// 在组件卸载清理过期缓存
onUnmounted(async () => {
  // 清理超过24小时的缓存
  const cacheTime = await localforage.getItem('cache-timestamp')
  if (cacheTime && Date.now() - (cacheTime as number) > 24 * 60 * 60 * 1000) {
    await clearCache()
  }
})

// 在数据更新时记存时间
const updateCacheTimestamp = async () => {
  await localforage.setItem('cache-timestamp', Date.now())
}

// 添加 getChannelIcon 函数
const getChannelIcon = (channel: string): string => {
  const iconMap: Record<string, string> = {
    'YouTube': 'youtube.svg',
    'youtube': 'youtube.svg',
    'Apple Podcast': 'apple-podcast.svg',
    'Spotify': 'spotify.svg',
    'spotify': 'spotify.svg',
    'webpage': 'web.svg'
  }
  return iconMap[channel] || ''
}

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
    const text = await navigator.clipboard.readText();
    // 最简单的URL判断：包含http或https，且包含至少一个点号
    if (text.includes('http') && text.includes('.')) {
      requestUrl.value = text.trim();
    }
  } catch (err) {
    console.error('Failed to read clipboard:', err);
  }
}

// 添加临时存储url的变量
const pendingUrl = ref('')

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

// 添加刷新处理函数
const handleUploadRefresh = () => {
  if (myUploadsRef.value) {
    myUploadsRef.value.fetchUserArticles()
  }
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

// 添加 ref 定义
const myUploadsRef = ref<InstanceType<typeof MyUploadsSection> | null>(null)

// 在相关方法中添加追踪
const handleArticleClick = (article: ArticleType) => {
  trackEvent('article_click_from_home', {
    articleId: article.id,
    title: article.title
  })
}

const handleCategoryChange = (category: string) => {
  trackEvent('category_change', {
    category: category
  })
}

// 添加showContactInfo状态
const showContactInfo = ref(false)

// 修改点击外部关闭联系方式弹窗的逻辑
onMounted(() => {
  const handleClickOutside = (event: MouseEvent) => {
    const target = event.target as HTMLElement
    // 移除自动关闭逻辑
  }
  
  document.addEventListener('click', handleClickOutside)
  
  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
  })
})

// 2024-03-19: 添加图片处理函数
const getContactImage = (imageName: string): string => {
  try {
    // 尝试使用动态导入
    return new URL(`/public/images/covers/${imageName}`, import.meta.url).href
  } catch (error) {
    console.error('Error loading image:', error)
    return '' // 返回空字符串或默认图片路径
  }
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
const showFeedbackForm = ref(false)

// 处理反馈表单提交
const handleFeedbackSubmit = (formData: {
  needProduct: boolean
  satisfiedSummary: boolean
  allowContact: boolean
}) => {
  console.log('Feedback submitted:', formData)
  // TODO: 这里后续会添加发送到后端的逻辑
}

// 2024-03-22: 添加输入框高亮动画
const isHighlighted = ref(false)
const showAnimatedPlaceholder = ref(true)

// 2024-03-22: 添加点击图标的处理函数
const handleAddIconClick = () => {
  isHighlighted.value = true
  showAnimatedPlaceholder.value = false
  
  // 重置高亮状态
  setTimeout(() => {
    isHighlighted.value = false
    showAnimatedPlaceholder.value = true
  }, 600)
}

// 2024-03-22: 修改输入框焦点处理函数
const handleInputFocus = () => {
  isInputFocused.value = true
  handlePaste() // 在获得焦点时也尝试粘贴
}

const handleInputBlur = () => {
  isInputFocused.value = false
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
  .card-container .w-[120px] {
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
.input-highlight {
  animation: highlight 0.6s ease-out;
}

@keyframes highlight {
  0% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.5);
    border-color: #3B82F6;
  }
  70% {
    box-shadow: 0 0 0 10px rgba(59, 130, 246, 0);
    border-color: #3B82F6;
  }
  100% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0);
    border-color: #E5E7EB;
  }
}

/* 2024-03-22: 添加placeholder文字动画 */
input::placeholder {
  transition: opacity 0.3s ease;
}

input.input-highlight::placeholder {
  animation: placeholderPulse 0.6s ease-in-out;
}

@keyframes placeholderPulse {
  0% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.5;
  }
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

