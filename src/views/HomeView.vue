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
  <header class="fixed top-0 left-0 right-0 bg-white z-50 w-full">
      <!-- 导航栏内容容器 -->
      <div class="flex justify-between items-center px-4 h-[70px] min-w-[378px] max-w-[1440px] mx-auto">
        <!-- 左侧Logo和标题容器 -->
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
     <!-- 2024-03-19: Early Access横幅 -->
     <div class="bg-white py-2 text-center text-pink-500 font-medium relative group">
        <div class="flex items-center justify-center gap-2">
          <p class="animate-bounce">{{ t('home.earlyAccess.feedback') }}</p>
          <!-- 联系方式图标 -->
          <div class="relative contact-info-container group">
            <img 
              :src="getContactImage('ContactMe.PNG')" 
              alt="Contact Us" 
              class="hidden w-10 h-10 cursor-pointer hover:opacity-80 transition-all duration-300 transform hover:scale-110"
              @click.stop="showContactInfo = !showContactInfo"
            />
            <!-- Hover弹出框 - 修改为group-hover显示 -->
            <div 
              class="absolute right-0 top-full mt-2 bg-white p-4 rounded-lg shadow-lg z-50 w-[400px] opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 transform group-hover:translate-y-0 translate-y-2"
              @click.stop
            >
              <img 
                :src="getContactImage('ContactMe.PNG')" 
                alt="Contact Details" 
                class="w-full h-auto hover:scale-105 transition-transform duration-300"
              />
            </div>
          </div>
        </div>
      </div>
      
      

        
        <!-- 右侧导航元素容器 - 增加右侧padding并调整gap -->
        <div class="flex items-center gap-3 pr-2">
          <!-- 语言切换组件 -->
          <language-switch/>
      
          <!-- 已登录用户信息区域 -->
          <template v-if="authStore.isAuthenticated">
            <!-- 用户头像 -->
            <img 
              :src="authStore.user?.user_metadata?.avatar_url" 
              alt="User Avatar" 
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
      @close="showLoginModal = false"
      @success="handleLoginSuccess"
    />

    <!-- 主要内容区域 -->
    <pull-to-refresh class="mt-[-20px]" :onRefresh="handleRefresh">
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
                  v-for="(channel, index) in ['youtube', 'apple-podcast', 'spotify', 'web', 'file']"
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
                  class="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5"
                />
                <input
                  type="text"
                  v-model="requestUrl"
                  :placeholder="t('summarize.urlPlaceholder')"
                  class="w-full sm:flex-grow pl-12 pr-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-000 focus:border-transparent bg-gray-100"
                  @click="handlePaste"
                  @keyup.enter="() => submitRequest(requestUrl)"
                />
              </div>
              
              <!-- 上传按钮 暂时hidden  -->
              <div class=" hidden w-[80px] sm:w-[100px] self-center sm:self-auto sm:flex-shrink-0 sm:mr-2 mt-2 sm:mt-0">
                <ArticleRequestForm 
                  ref="articleRequestFormRef"
                  @refresh="handleArticleRefresh"
                  @click="() => submitRequest(requestUrl.value)"
                  @uploadSuccess="handleUploadSuccess"
                />
              </div>
            </div>
          </div>
        </div>

          <!-- 我的上传区域 -->
          <my-uploads-section 
            ref="myUploadsRef"
            @upload="submitRequest"
          />

          <!-- 发现区域 暂时都不要了-->
          <div class="hidden mb-8">
            <!-- 发现标题 -->
            <h2 class="text-xl mb-4">{{ t('home.filter.discover') }}</h2>
          </div>
          <!-- 渠道筛选区域 暂时都不要了-->
          <div class="hidden mb-8">
            <!-- 渠道标题 -->
            <h2 class="text-sm text-gray-600 mb-2">{{ t('home.filter.channelTitle') }}</h2>
            <!-- 渠道按钮容器 -->
            <div class="flex flex-wrap gap-2">
            <!-- 修改渠道按钮 这里的YouTube', 'Apple Podcast', 'Spotify', 'webpage'是和articels表中的channel字段数据一致-->
              <button 
                v-for="channel in ['YouTube', 'Apple Podcast', 'Spotify', 'webpage']"
                :key="channel"
                @click="toggleChannel(channel)"
                class="px-3 py-1.5 text-sm rounded-[2px] border transition-colors duration-200 flex items-center gap-2"
                :class="selectedChannels.includes(channel) ? 
                  'bg-blue-50 border-blue-400 text-blue-400' : 
                  'bg-gray-50 border-gray-300 text-gray-300 hover:border-gray-400 hover:text-gray-400'"
              >
                <!-- 渠道图标 -->
                <img 
                  :src="`/images/icons/${getChannelIcon(channel)}`" 
                  :alt="channel"
                  class="w-4 h-4"
                />
                <!-- 渠道名称 -->
                {{ t(`home.channels.${getChannelKey(channel)}`) }}
              </button>
            </div>
          </div>

          <!-- 2024-03-15: 只有登录用户才显示作者筛选区域 -->
          <div v-if="authStore.isAuthenticated" class="mb-8" v-show="false">
            <h2 class="text-sm text-gray-600 mb-2">{{ t('home.filter.authorTitle') }}</h2>
            <div class="flex flex-wrap gap-3">
              <!-- 修改加载状态判断 -->
              <template v-if="isLoadingAuthors">
                <div v-for="n in 4" :key="n" 
                  class="h-8 w-24 bg-gray-100 animate-pulse rounded-[2px]">
                </div>
              </template>

              <template v-else>
                <!-- 作者列表部分 -->
                <template v-for="(author, index) in displayedAuthors" :key="author.id">
                  <button
                    @click="toggleAuthor(author)"
                    class="flex items-center gap-2 px-3 py-1.5 text-sm rounded-[2px] border transition-colors duration-200"
                    :class="selectedAuthors.includes(author.id) ? 
                      'bg-blue-50 border-blue-400 text-blue-400' : 
                      'bg-gray-50 border-gray-300 text-gray-300 hover:border-gray-400 hover:text-gray-400'"
                  >
                    <img 
                      v-if="author.icon" 
                      :src="author.icon" 
                      :alt="author.name"
                      class="w-5 h-5 rounded-full"
                      loading="lazy"
                    />
                    {{ author.name }}
                  </button>
                </template>
              </template>

              <!-- 作者展开/收起按钮 -->
              <button 
                v-if="authors.length > defaultDisplayCount"
                @click="toggleExpand"
                class="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700"
              >
                <span>{{ isExpanded ? t('home.filter.collapse') : t('home.filter.expand') }}</span>
                <svg 
                  class="w-4 h-4 transition-transform duration-200"
                  :class="{ 'transform rotate-180': isExpanded }"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
          </div>
          <!-- 文章列表区域的容器结构 -->
          <div class="articles-section">
            <!-- 文章标题 -->
            <div class="h-[28px] mb-[10px]">
              <h2 class="font-['PingFang_SC'] text-[20px] font-semibold leading-[28px] text-[#000000]">
                {{ t('home.articles.title') }}
              </h2>
            </div>
            
            <!-- 文章卡片网格容器 -->
            <div class="articles-grid">
              <!-- 实际文章列表 -->
              <ArticleCard
                v-for="article in filteredArticles"
                :key="article.id"
                :article="article"
              />

              <!-- 加载状态显示骨架图 - 调整为3个且只在加载更多时显示 -->
              <template v-if="isLoading && currentPage > 1">
                <div v-for="n in 3" :key="n" 
                  class="article-card bg-white rounded-lg shadow-md animate-pulse"
                >
                  <!-- 封面图骨架 - 保持16:9比例 -->
                  <div class="aspect-video bg-gray-200 rounded-t-lg"></div>
                  
                  <!-- 内容区域 -->
                  <div class="p-4 space-y-4">
                    <!-- 标题骨架 - 两行 -->
                    <div class="space-y-2">
                      <div class="h-5 bg-gray-200 rounded w-full"></div>
                      <div class="h-5 bg-gray-200 rounded w-2/3"></div>
                    </div>
                    
                    <!-- 底部信息骨架 -->
                    <div class="flex items-center justify-between">
                      <!-- 作者信息 -->
                      <div class="flex items-center space-x-2">
                        <div class="w-8 h-8 bg-gray-200 rounded-full"></div>
                        <div class="h-4 bg-gray-200 rounded w-20"></div>
                      </div>
                      <!-- 日期 -->
                      <div class="h-4 bg-gray-200 rounded w-16"></div>
                    </div>
                  </div>
                </div>
              </template>

              <!-- 初始加载时的骨架图 -->
              <template v-if="isLoading && currentPage === 1">
                <div v-for="n in pageSize" :key="n" 
                  class="article-card bg-white rounded-lg shadow-md animate-pulse"
                >
                  <!-- 与上面相同的骨架结构 -->
                  <div class="aspect-video bg-gray-200 rounded-t-lg"></div>
                  <div class="p-4 space-y-4">
                    <div class="space-y-2">
                      <div class="h-5 bg-gray-200 rounded w-full"></div>
                      <div class="h-5 bg-gray-200 rounded w-2/3"></div>
                    </div>
                    <div class="flex items-center justify-between">
                      <div class="flex items-center space-x-2">
                        <div class="w-8 h-8 bg-gray-200 rounded-full"></div>
                        <div class="h-4 bg-gray-200 rounded w-20"></div>
                      </div>
                      <div class="h-4 bg-gray-200 rounded w-16"></div>
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
            {{ authStore.isAuthenticated ? t('common.noMoreData') : t('common.loginToViewMore') }}
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
import type { Article } from '../types/article'
import AuthorSelect from '../components/AuthorSelect.vue'
import ArticleForm from '../components/ArticleForm.vue'
import { getChannelIcon } from '../utils/channel'
import ArticleRequestForm from '../components/ArticleRequestForm.vue'
import { useI18n } from 'vue-i18n'
import LanguageSwitch from '../components/LanguageSwitch.vue'
import PullToRefresh from '../components/PullToRefresh.vue'
import localforage from 'localforage'
import MyUploadsSection from '../components/MyUploadsSection.vue'
import { trackEvent } from '@/utils/analytics'

const authStore = useAuthStore()
const showLoginModal = ref(false)
const showUploadModal = ref(false)

// 预定义的标签
const PREDEFINED_TAGS = ['24小时', '博客', '论文', '微', '视频']

const articles = ref<Article[]>([])
const selectedTag = ref('all')

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

// 修改 fetchArticles 函数
const fetchArticles = async (isRefresh = false) => {
  try {
    // 重置页码
    if (isRefresh) {
      currentPage.value = 1
    }

    isLoading.value = true

    // 构建查询
    const query = supabase
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
          author:keep_authors(id, name, icon)
        )
      `)
      .eq('user_id', authStore.user?.id)
      .order('created_at', { ascending: false })
      .range((currentPage.value - 1) * pageSize, currentPage.value * pageSize - 1)

    // 添加筛选条件
    if (selectedTag.value !== 'all') {
      query.contains('article.tags', [selectedTag.value])
    }

    const { data: views, error } = await query

    if (error) throw error

    // 处理结果,提取文章信息
    const validArticles = views
      ?.map(view => ({
        ...view.article,
        is_author: view.is_author
      }))
      .filter(article => article !== null)

    // 更新文章列表
    articles.value = isRefresh || hasFilters.value ? validArticles : [...articles.value, ...validArticles]
    
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

// 修改筛选逻辑以适应的数据结构
const filteredArticles = computed(() => {
  let result = articles.value

  // 标签筛选
  if (selectedTag.value !== 'all') {
    result = result.filter(article => 
      article.tags && article.tags.includes(selectedTag.value)
    )
  }

  // 渠道筛选
  if (selectedChannels.value.length > 0) {
    result = result.filter(article => 
      article.channel && selectedChannels.value.includes(article.channel)
    )
  }

  // 作者筛选
  if (selectedAuthors.value.length > 0) {
    result = result.filter(article => 
      article.author_id && selectedAuthors.value.includes(article.author_id)
    )
  }

  return result
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
  
  // 2024-03-15: 先加载用户信息
  await authStore.loadUser()
  console.log('[onMounted] User loaded, new auth status:', authStore.isAuthenticated)
  
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

const articleForm = ref<Partial<Article>>({
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

// 添作者相关状态
interface Author {
  id: number;
  name: string;
  icon?: string;
}

const authors = ref<Author[]>([])
const selectedChannels = ref<string[]>([])
const selectedAuthors = ref<number[]>([])

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

const requestUrl = ref('')
const articleRequestFormRef = ref<InstanceType<typeof ArticleRequestForm> | null>(null)

// 添加贴板处理函数
const handlePaste = async () => {
  try {
    const text = await navigator.clipboard.readText()
    requestUrl.value = text
  } catch (err) {
    console.error('Failed to read clipboard:', err)
  }
}

// 添加临时存储url的变量
const pendingUrl = ref('')

// 修改 submitRequest 函数
const submitRequest = async (url?: string, type: 'url' | 'web' | 'file' = 'url') => {
  // 2024-03-14: 添加类型参数处理
  // 如果没有传入url，则使用输入框的值
  let uploadUrl = url || requestUrl.value
  
  
  if (!authStore.isAuthenticated) {
    // 保存URL到localStorage
    localStorage.setItem('pendingUploadUrl', uploadUrl)
    showLoginModal.value = true
    return
  }
  
  // 确保用户已完全登录
  if (!authStore.user) {
    await authStore.loadUser()
  }
  
  // 已登录则根据类型打开对应的modal
  if (articleRequestFormRef.value) {
    // 2024-03-14: 根据类型调用不同的打开方式
    articleRequestFormRef.value.openModalWithUrl(uploadUrl, type)
  }
}

// 添加刷新处理函数
const handleUploadRefresh = () => {
  if (myUploadsRef.value) {
    myUploadsRef.value.fetchUserArticles()
  }
}

// 添加新的处理函数
const handleArticleRefresh = async (event?: { type: string }) => {
  // 如果是上传成功触发的刷新
  if (event?.type === 'upload') {
    // 刷新我的上传区域
    if (myUploadsRef.value) {
      await myUploadsRef.value.fetchUserArticles()
    }
  }
  // 刷新文章列表
  await fetchArticles()
}

// 添加处理上传成功的方法
const handleUploadSuccess = (url: string) => {
  // 添加乐观更新卡片
  if (myUploadsRef.value) {
    myUploadsRef.value.addOptimisticCard(url)
  }
}

// 添加 ref 定义
const myUploadsRef = ref<InstanceType<typeof MyUploadsSection> | null>(null)

// 在相关方法中添加追踪
const handleArticleClick = (article: Article) => {
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

// 添加点击外部关闭联系方式弹窗
onMounted(() => {
  const handleClickOutside = (event: MouseEvent) => {
    const target = event.target as HTMLElement
    if (!target.closest('.contact-info-container')) {
      showContactInfo.value = false
    }
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
</style>

