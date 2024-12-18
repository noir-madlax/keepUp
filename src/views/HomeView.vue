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
          <h1 class="text-[20px] text-[#333333] font-[400] leading-6 font-['PingFang_SC']">
            {{ t('home.title') }}
          </h1>
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
      <div class="h-[1px] bg-[#E5E5E5] w-full"></div>
    </header>

    <!-- 登录模态框 -->
    <login-modal 
      v-if="showLoginModal" 
      @close="showLoginModal = false"
    />

    <!-- 主要内容区域 -->
    <pull-to-refresh class="pt-[0px]" :onRefresh="handleRefresh">
      <div class="px-4 sm:px-8 py-6 overflow-x-hidden">
        <!-- 修改容器最大宽度并确保居中 -->
        <div class="max-w-screen-2xl mx-auto w-full">
          <!-- 修改上传框的外边距 -->
          <div class="flex flex-wrap items-center gap-4 mb-6 p-4 sm:p-6 bg-gradient-to-r from-pink-50 to-purple-50 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 border border-pink-100">
            <!-- 标题和图标容器 -->
            <div class="flex items-center gap-4 w-full sm:w-auto mb-2 sm:mb-0">
              <!-- 标题 - 优化字体大小和响应式显示 -->
              <h3 class="text-xl sm:text-2xl font-bold text-gray-800 whitespace-nowrap flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 sm:h-8 sm:w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
                </svg>
                {{ t('summarize.title') }}
              </h3>
              
              <!-- 3个支持的渠道图标 - 优化响应式显示 -->
              <div class="flex items-center gap-3 ml-auto sm:ml-4">
                <img 
                  v-for="(channel, index) in ['youtube', 'apple-podcast', 'spotify']"
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
              <input
                type="text"
                v-model="requestUrl"
                :placeholder="t('summarize.urlPlaceholder')"
                class="w-full sm:flex-grow px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-transparent bg-white"
                @click="handlePaste"
                @keyup.enter="submitRequest"
              />
              
              <!-- 上传按钮 -->
              <div class="w-[80px] sm:w-[100px] self-center sm:self-auto sm:flex-shrink-0 sm:mr-2 mt-2 sm:mt-0">
                <article-request-form 
                  ref="articleRequestFormRef"
                  @refresh="fetchArticles"
                  @click="submitRequest"
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

          <!-- 发现区域 -->
          <div class="mb-8">
            <!-- 发现标题 -->
            <h2 class="text-xl mb-4">{{ t('home.filter.discover') }}</h2>
          </div>
          <!-- 渠道筛选区域 -->
          <div class="mb-8">
            <!-- 渠道标题 -->
            <h2 class="text-sm text-gray-600 mb-2">{{ t('home.filter.channelTitle') }}</h2>
            <!-- 渠道按钮容器 -->
            <div class="flex flex-wrap gap-2">
              <button 
                v-for="channel in ['YouTube', 'Apple Podcast', 'Spotify']"
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

          <div class="mb-8">
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
              <ArticleCard
                v-for="article in articles"
                :key="article.id"
                :article="article"
              />
            </div>
          </div>

          <!-- 加载状态提示 -->
          <div v-if="isLoading || hasMore" class="text-center py-4">
            <div v-if="isLoading" class="flex justify-center items-center space-x-2">
              <div class="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <span class="text-gray-500">{{ t('common.loading') }}</span>
            </div>
            <div v-else-if="hasMore" class="text-gray-500">
              {{ t('common.scrollToLoadMore') }}
            </div>
          </div>
          
          <!-- 没有更多数据的提示 -->
          <div v-if="!isLoading && !hasMore" class="text-center py-4 text-gray-500">
            {{ t('common.noMoreData') }}
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
import { ref, computed, reactive, onMounted, onUnmounted, onActivated } from 'vue'
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

const authStore = useAuthStore()
const showLoginModal = ref(false)
const showUploadModal = ref(false)

// 预定义的签
const PREDEFINED_TAGS = ['24小时', '博客', '论文', '微', '视频']

const articles = ref<Article[]>([])
const selectedTag = ref('all')

// 用预定义��标签替代动态计算的标签
const tags = computed(() => PREDEFINED_TAGS)

// 分页相关的状态
const pageSize = 9 // 每页加载的文章数量
const currentPage = ref(1)
const isLoading = ref(false) // 加载状态
const hasMore = ref(true) // 否还有更多数据

// 添加重置函数
const resetPageState = () => {
  currentPage.value = 1
  articles.value = []
  hasMore.value = true
  fetchArticles(true) // 重新获取第一页数据
}

// 监路由激活
onActivated(() => {
  resetPageState()
})

// 添加一个性来判断是否有筛选条件
const hasFilters = computed(() => {
  return selectedTag.value !== 'all' || 
         selectedChannels.value.length > 0 || 
         selectedAuthors.value.length > 0
})

// 修改 fetchArticles 函数
const fetchArticles = async (isRefresh = false) => {
  try {
    if (isRefresh) {
      currentPage.value = 1
      articles.value = []
      hasMore.value = true
    }

    if (!hasMore.value || isLoading.value) return

    isLoading.value = true

    // 如果有筛选条件，不使用分
    const from = hasFilters.value ? 0 : (currentPage.value - 1) * pageSize
    const to = hasFilters.value ? 999 : from + pageSize - 1

    // 从 API 获取数据
    const { data, error, count } = await supabase
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
        author:keep_authors(id, name, icon)
      `, { count: 'exact' })
      .order('created_at', { ascending: false })
      .range(from, to)

    if (error) throw error

    // 更新文章列表
    articles.value = isRefresh || hasFilters.value ? data : [...articles.value, ...data]
    
    // 更新是否还有更多数据
    // 如有筛选条件就不显示加载更多
    hasMore.value = hasFilters.value ? false : (count ? from + data.length < count : false)

    // 只在完整刷新时更新缓存
    if (isRefresh) {
      await localforage.setItem('articles-cache', data)
    }

  } catch (error) {
    console.error('获取文章列表时出错:', error)
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
    // 1. 先 IndexedDB 获取存数据
    const cachedAuthors = await localforage.getItem('authors-cache')
    if (cachedAuthors) {
      authors.value = cachedAuthors as Author[]
      isLoadingAuthors.value = false // 有缓存数据就关闭loading
    }

    // 2. 如果离线且有缓存，直接返回
    if (!navigator.onLine && cachedAuthors) {
      return
    }

    // 3. 从 API 获取数据
    const { data, error } = await supabase
      .from('keep_authors')
      .select('*')
      .order('name')

    if (error) throw error

    // 4. 更新 IndexedDB 缓存
    await localforage.setItem('authors-cache', data)
    authors.value = data
    
  } catch (error) {
    console.error('获取作者列表失败:', error)
    ElMessage.error('获取作者列表失败')
  } finally {
    isLoadingAuthors.value = false // 无论成功失败都关闭loading
  }
}

// 改 onMounted
onMounted(async () => {
  isLoadingAuthors.value = true // 始化时设置loading

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

  // 并获取据
  await Promise.all([
    fetchArticles(),
    fetchAuthors(),
    updateCacheTimestamp()
  ])

  authStore.loadUser()
  
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
    ElMessage.warning('请登录')
    showLoginModal.value = true
    return
  }
  showUploadModal.value = true
}

const handleLogout = async () => {
  try {
    await authStore.signOut()
    ElMessage.success('已退出登录')
  } catch (error) {
    console.error('Logout error:', error)
    ElMessage.error('退出失败，请重试')
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
      ElMessage.warning('请先登录')
      showLoginModal.value = true
      return
    }

    if (!articleForm.value.title || !articleForm.value.content || !articleForm.value.author_id) {
      ElMessage.error('题、内容和作者为必填项')
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

    ElMessage.success('文章添加成功')

    showUploadModal.value = false
    resetForm()
    await fetchArticles()
  } catch (error) {
    console.error('提交文章时出错:', error)
    ElMessage.error('系统错误，请稍后重试')
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
    'Spotify': 'spotify'
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

// 在数据更新时记录存时间
const updateCacheTimestamp = async () => {
  await localforage.setItem('cache-timestamp', Date.now())
}

// 添加 getChannelIcon 函数
const getChannelIcon = (channel: string): string => {
  const iconMap: Record<string, string> = {
    'YouTube': 'youtube.svg',
    'Apple Podcast': 'apple-podcast.svg',
    'Spotify': 'spotify.svg'
  }
  return iconMap[channel] || ''
}

// 添加滚动加载处理函
const handleScroll = () => {
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

// 添加提交处理函数
const submitRequest = () => {
  if (articleRequestFormRef.value) {
    articleRequestFormRef.value.openModalWithUrl(requestUrl.value)
  }
}

// 添加对 MyUploadsSection 的引用
const myUploadsRef = ref<InstanceType<typeof MyUploadsSection> | null>(null)

// 添加刷新处理函数
const handleUploadRefresh = () => {
  if (myUploadsRef.value) {
    myUploadsRef.value.fetchUserArticles()
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

/* 在桌面端时强制显示3列，并设置合适的列宽 */
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
</style>
