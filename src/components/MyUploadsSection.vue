<template>
  <div class="my-uploads-section">
    <!-- 我的上传 标题 -->
    <h2 class="text-xl mb-4">{{ t('home.filter.myUpload') }}</h2>
    
    <!-- 横向滚动容器 -->
    <div class="relative">
      <!-- 左侧渐变遮罩 -->
      <div 
        class="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-white to-transparent z-10"
        v-show="canScrollLeft"
      ></div>
      
      <!-- 右侧渐变遮罩 -->
      <div 
        class="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-white to-transparent z-10"
        v-show="canScrollRight"
      ></div>
      
      <!-- 滚动容器 -->
      <div 
        class="overflow-x-auto scrollbar-hide flex gap-2 pb-2 mb-4" 
        ref="scrollContainer"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
        @scroll="handleScroll"
      >
        <!-- NewUploadCard 固定在第一个位置 -->
        <div class="upload-container flex-shrink-0">
          <!-- 新增可点击区域容器 -->
          <div class="clickable-area" @click="handleNewUploadClick('url', $event)">
            <!-- Upload Icon -->
            <div class="upload-icon">
              <img src="/images/icons/upload.svg" alt="Upload" class="w-[43px] h-[43px]">
            </div>
            <!-- Upload Text -->
            <div class="upload-text">{{ t('upload.card.uploadFile') }}</div>
          </div>
          
          <!-- 不可点击的渠道图标和说明区域 -->
          <div class="non-clickable-area">
            <div class="icon-container">
              <!-- Youtube Icon -->
              <div class="icon">
                <div class="icon-background">
                  <img src="/images/icons/youtube.svg" alt="Youtube" class="youtube-icon">
                </div>
              </div>
              <!-- Apple Icon -->
              <div class="icon">
                <div class="icon-background">
                  <img src="/images/icons/apple-podcast.svg" alt="Apple" class="podcast-icon">
                </div>
              </div>
              <!-- Spotify Icon -->
              <div class="icon">
                <div class="icon-background">
                  <img src="/images/icons/spotify.svg" alt="Spotify" class="podcast-icon">
                </div>
              </div>
            </div>
            <div class="link-text">{{ t('upload.card.supportedPlatforms') }}</div>
          </div>
        </div>

         <!-- NewUploadCard2 固定文章上传的卡片在第二个位置 -->
         <div class="web-content-container flex-shrink-0">
          <!-- 新增可点击区域容器 -->
          <div class="clickable-area" @click="handleNewUploadClick('web', $event)">
            <!-- Upload Icon -->
            <div class="upload-icon">
              <img src="/images/icons/web.svg" alt="Upload" class="w-[45px] h-[45px] object-contain">
            </div>
            <!-- Upload Text -->
            <div class="upload-text">{{ t('upload.card.uploadWeb') }}</div>
          </div>
          
          <!-- 不可点击的说明区域 -->
          <div class="non-clickable-area">
            <div class="link-text">{{ t('upload.card.webLink') }}</div>
          </div>
        </div>

         <!-- NewUploadCard3 pdf/doc/txt的上传-->
         <div class="upload-container flex-shrink-0">
          <!-- 新增可点击区域容器 -->
          <div class="clickable-area" @click="handleNewUploadClick('file', $event)">
            <!-- Upload Icon -->
            <div class="upload-icon">
              <img src="/images/icons/file.svg" alt="Upload" class="w-[43px] h-[43px]">
            </div>
            <!-- Upload Text -->
            <div class="upload-text">{{ t('upload.card.uploadDoc') }}</div>
          </div>
          
          <!-- 不可点击的渠道图标和说明区域 -->
          <div class="non-clickable-area">
            <div class="icon-container">
              <!-- doc Icon -->
              <div class="icon">
                <div class="icon-background">
                  <img src="/images/icons/doc.svg" alt="doc" class="youtube-icon">
                </div>
              </div>
              <!-- pdf Icon -->
              <div class="icon">
                <div class="icon-background">
                  <img src="/images/icons/pdf.svg" alt="pdf" class="podcast-icon">
                </div>
              </div>
              <!-- txt Icon -->
              <div class="icon">
                <div class="icon-background">
                  <img src="/images/icons/txt.svg" alt="txt" class="podcast-icon">
                </div>
              </div>
            </div>
            <div class="link-text">{{ t('upload.card.supportedFiles') }}</div>
          </div>
        </div>
        <!-- 加载状态显示骨架屏 -->
        <template v-if="localLoading">
          <div 
            v-for="n in 8" 
            :key="n"
            class="flex-shrink-0 w-[200px] h-[238px] bg-gray-100 rounded-xl animate-pulse"
          >
            <!-- 骨架屏内部构 -->
            <div class="p-4 space-y-4">
              <!-- 图片占位 -->
              <div class="w-full h-[98px] bg-gray-200 rounded-lg"></div>
              <!-- 标题占位 -->
              <div class="h-4 bg-gray-200 rounded w-3/4"></div>
              <!-- 作者信息占位 -->
              <div class="flex items-center space-x-2">
                <div class="w-8 h-8 bg-gray-200 rounded-full"></div>
                <div class="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
              <!-- 底 -->
              <div class="flex justify-between">
                <div class="h-3 bg-gray-200 rounded w-1/4"></div>
                <div class="h-3 bg-gray-200 rounded w-1/4"></div>
              </div>
            </div>
          </div>
        </template>
       
        <!-- 根据用户id获取这个用户的文章列表 -->
        <template v-else-if="displayCards.length">
          <UploadCard
            v-for="article in displayCards"
            :key="article.requestId || article.original_url"
            :article="article"
            class="flex-shrink-0 w-[200px] mb-2"
            @delete="deleteRequest"
          />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import UploadCard from './UploadCard.vue'
import { useAuthStore } from '../stores/auth'
import { supabase } from '../supabaseClient'

const { t } = useI18n()
const authStore = useAuthStore()

// 添加类型定义
interface SupabaseArticleRequest {
  id: string
  url: string
  status: 'processing' | 'processed' | 'failed'
  created_at: string
  error_message?: string
  original_url: string
  platform?: string
}

interface ArticleRequest extends SupabaseArticleRequest {
  requestId: string
}

interface OptimisticCard {
  original_url: string
  created_at: string
  status: 'processing'
  platform?: string
  requestId: string
}

// 声明响应式变量
const scrollContainer = ref<HTMLElement | null>(null)
const canScrollLeft = ref(false)
const canScrollRight = ref(true)
const articles = ref<ArticleRequest[]>([])
const optimisticCards = ref<OptimisticCard[]>([])
const localLoading = ref(true)

// 添加手势相关的状态
const touchStartX = ref(0)
const touchStartY = ref(0)
const isHorizontalMove = ref(false)
const minDirectionDelta = 20 // 判断方向的最小位移差值

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

// 添加轮询相关的变量
const POLL_INTERVAL = 15000  // 5秒轮询一次
let pollTimer: NodeJS.Timeout | null = null

// 添加轮询控制函数
const startPolling = () => {
  if (pollTimer) {
    return
  }
  
  pollTimer = setInterval(async () => {
    const hasProcessingItems = articles.value.some(
      (article: ArticleRequest) => article.status === 'processing'
    ) || optimisticCards.value.length > 0
    
    if (hasProcessingItems) {
      await fetchUserArticles(true)
    } else {
      stopPolling()
    }
  }, POLL_INTERVAL)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

// 添加乐观更新的方法
const addOptimisticCard = (url: string) => {
  const requestId = `temp-${Date.now()}`
  optimisticCards.value.push({
    original_url: url,
    created_at: new Date().toISOString(),
    status: 'processing' as const,
    platform: getPlatformFromUrl(url),
    requestId
  })
  
  // 添加乐观更新卡片时启动轮询
  startPolling()
}

// 计算属性
const displayCards = computed(() => {
  // 过滤掉已经存在于数据库记录中的乐观更新卡片
  const filteredOptimisticCards = optimisticCards.value.filter(opt => 
    !articles.value.some(article => article.original_url === opt.original_url)
  )
  // 把乐观更新卡片放在最前面
  return [...filteredOptimisticCards, ...articles.value]
})

// 修改 fetchUserArticles 函数的类型处理
const fetchUserArticles = async (isPolling: boolean = false) => {
  try {
    const userId = authStore.user?.id
    if (!userId) {
      localLoading.value = false
      articles.value = []
      return
    }
    
    if (!isPolling) {
      localLoading.value = true
    }
    
    interface ArticleRequestResponse {
      id: string
      url: string
      status: 'processing' | 'processed' | 'failed'
      created_at: string
      error_message?: string
      original_url: string
      platform?: string
      article_id?: string
    }

    interface ArticleDataResponse {
      id: string
      title: string
      publish_date: string
      channel: string
      cover_image_url: string
      original_link: string
      author: {
        id: string
        name: string
        icon: string
      }
    }

    const { data: requestsData, error: requestsError } = await supabase
      .from('keep_article_requests')
      .select(`
        id,
        url,
        status,
        created_at,
        error_message,
        original_url,
        platform,
        article_id
      `)
      .eq('user_id', userId)
      .order('created_at', { ascending: false })

    if (requestsError || !requestsData) {
      throw requestsError
    }

    const processedRequests = await Promise.all(
      (requestsData as unknown as ArticleRequestResponse[]).map(async (request) => {
        const baseRequest: ArticleRequest = {
          id: request.id,
          url: request.url,
          status: request.status,
          created_at: request.created_at,
          error_message: request.error_message,
          original_url: request.original_url,
          platform: request.platform,
          requestId: request.id
        }

        if (request.status !== 'processed' || !request.article_id) {
          return baseRequest
        }

        try {
          const { data: articleData, error: articleError } = await supabase
            .from('keep_articles')
            .select(`
              *,
              user_id,
              author:keep_authors (
                id,
                name,
                icon
              )
            `)
            .eq('id', request.article_id)
            .single()

          if (articleError || !articleData) {
            return baseRequest
          }

          const typedArticleData = articleData as unknown as ArticleDataResponse

          return {
            ...baseRequest,
            ...typedArticleData,
            author: typedArticleData.author,
            id: typedArticleData.id
          }
        } catch (error) {
          return baseRequest
        }
      })
    )

    articles.value = processedRequests
    
    optimisticCards.value = optimisticCards.value.filter(opt => 
      !processedRequests.some(article => 
        article.original_url === opt.original_url && article.status === 'processed'
      )
    )

    const hasProcessingItems = processedRequests.some(
      (article: ArticleRequest) => article.status === 'processing'
    ) || optimisticCards.value.length > 0

    if (hasProcessingItems && !pollTimer) {
      startPolling()
    } else if (!hasProcessingItems && pollTimer) {
      stopPolling()
    }
    
  } catch (error) {
    ElMessage.error(t('upload.message.getFailed'))
  } finally {
    if (!isPolling) {
      localLoading.value = false
    }
  }
}

// 监听用户状态变化
watch(() => authStore.user?.id, (newId) => {
  if (newId) {
    fetchUserArticles()
  } else {
    localLoading.value = false
    articles.value = []
  }
})

// 添加 emit
const emit = defineEmits(['upload'])

// 修改点击处理函数
const handleNewUploadClick = async (type: 'url' | 'web' | 'file' = 'url') => {
  try {
    // 2024-03-14: 添加类型参数，区分不同上传方式
    if (type === 'file') {
      // 如果是文件上传类型，直接触发上传事件
      emit('upload', '', type)
      return
    }

    // 保留原有的剪贴板读取逻辑
    const clipboardText = await navigator.clipboard.readText()
    // 验证是否是有效的URL
    const isValidUrl = clipboardText.startsWith('http://') || clipboardText.startsWith('https://')
    
    // 使用剪贴板内容或默认标记URL
    const uploadUrl = isValidUrl ? clipboardText : ''
    
    if (!authStore.isAuthenticated) {
      // 存储到 localStorage，复用现有逻辑
      localStorage.setItem('pendingUploadUrl', uploadUrl)
    }
    // 触发上传事件，并传递 URL 和类型
    emit('upload', uploadUrl, type)
  } catch (err) {
    console.error('Failed to read clipboard:', err)
    // 读取失败时使用默认标记URL
    const defaultUrl = ''
    if (!authStore.isAuthenticated) {
      localStorage.setItem('pendingUploadUrl', defaultUrl)
    }
    emit('upload', defaultUrl, type)
  }
}

// Methods
const handleScroll = () => {
  if (!scrollContainer.value) return
  
  const { scrollLeft, scrollWidth, clientWidth } = scrollContainer.value
  
  canScrollLeft.value = scrollLeft > 0
  canScrollRight.value = scrollLeft < scrollWidth - clientWidth
}

// 处理触摸开始
const handleTouchStart = (e: TouchEvent) => {
  touchStartX.value = e.touches[0].clientX
  touchStartY.value = e.touches[0].clientY
  isHorizontalMove.value = false
}

// 处理触摸移动
const handleTouchMove = (e: TouchEvent) => {
  const touchX = e.touches[0].clientX
  const touchY = e.touches[0].clientY
  const diffX = Math.abs(touchX - touchStartX.value)
  const diffY = Math.abs(touchY - touchStartY.value)
  
  if (diffX > minDirectionDelta || diffY > minDirectionDelta) {
    if (diffX > diffY) {
      isHorizontalMove.value = true
      e.stopPropagation()
    }
  }
}

// 处理触摸结束
const handleTouchEnd = () => {
  isHorizontalMove.value = false
}

// Lifecycle
onMounted(async () => {
  // 等待用户信息加载完成
  await authStore.loadUser()
  
  // 只在登录状态下才获取文章
  if (authStore.user?.id) {
    localLoading.value = true
    await fetchUserArticles()
  } else {
    localLoading.value = false
  }
  
  handleScroll()
  window.addEventListener('resize', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleScroll)
  stopPolling()
})

// 添加删除请求的方法
const deleteRequest = async (requestId: string) => {
  try {
    // 2024-03-14: 先找到要删除的文章，用于后续清理乐观更新卡片
    const articleToDelete = articles.value.find(article => article.requestId === requestId)
    
    const { error } = await supabase
      .from('keep_article_requests')
      .delete()
      .eq('id', requestId)

    if (error) throw error

    // 删除成功后从列表中移除该项
    articles.value = articles.value.filter(article => article.requestId !== requestId)
    
    // 如果找到了要删除的文章，同时清理对应的乐观更新卡片
    if (articleToDelete) {
      optimisticCards.value = optimisticCards.value.filter(opt => 
        opt.original_url !== articleToDelete.original_url
      )
    }
    
    ElMessage.success(t('upload.message.deleteSuccess'))
  } catch (error) {
    console.error('删除请求失败:', error)
    ElMessage.error(t('upload.message.deleteFailed'))
  }
}

// 添加暴露给父组件的刷新方法
defineExpose({
  fetchUserArticles,
  addOptimisticCard
})
</script>

<style scoped>
/* 隐藏滚动条但保持可以滚动 */
.scrollbar-hide {
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;  /* Chrome, Safari and Opera */
}

/* 添加平滑滚动效果 */
.overflow-x-auto {
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch; /* 支持iOS惯性滚动 */
}

/* 添加容器过渡画 */
.my-uploads-section {
  transition: all 0.3s ease;
}

/* 添加骨架屏动画 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* 卡片容器基础样式 */
.upload-container {
  width: 200px;
  height: 238px;
  padding: 24px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  border-radius: 12px;
  background: #FFF;
  box-shadow: 0px 0px 16px 0px rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
  transition: all 0.3s ease;
  position: relative;
}


.upload-container .upload-icon {
  margin-top: -16px;  /* 减小图标底部间距 */
}

.upload-container .icon {
  margin-top: -60px;  /* 图标位置 */
}
.upload-container .link-text {
  margin-top: -30px;  /* 微调文字位置 */
}

.upload-container .link-text {
  margin-top: -30px;  /* 微调文字位置 */
}


.web-content-container {
  width: 200px;
  height: 238px;
  padding: 24px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;  /* 减小整体间距 */
  border-radius: 12px;
  background: #FFF;
  box-shadow: 0px 0px 16px 0px rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
  transition: all 0.3s ease;
  position: relative;
}

.web-content-container .upload-icon {
  margin-top: -10px;  /* 减小图标底部间距 */
}

.web-content-container .upload-text {
  margin-top: -6px;  /* 微调文字位置 */
}

.web-content-container .link-text {
  margin-top: +20px;  /* 微调文字位置 */
}


/* 上传图标容器 */
.upload-icon {
  width: 66px;
  height: 66px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 4px;
}

/* 上传文字样式 */
.upload-text {
  color: #3FA6FC;
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  line-height: 20px;
  margin-bottom: 0px;
}

/* 图标容器样式 */
.icon-container {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 0px;
  height: 28px; /* 固定高度 */
}

/* 单个图标样式 */
.icon {
  width: 28px;
  height: 28px;
}

.icon-background {
  width: 28px;
  height: 28px;
  background: #EBEBEB;
  border-radius: 3.5px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 图标尺寸 */
.youtube-icon {
  width: 18px;
  height: 14px;
}

.podcast-icon {
  width: 14px;
  height: 14px;
}


.webpage-icon {
  width: 14px;
  height: 14px;
}

/* 链接文字样式 */
.link-text {
  color: #999;
  text-align: center;
  font-size: 14px;
  font-weight: 400;
  line-height: 20px;
  margin-top: 0; /* 将文字推到底部 */
  padding-bottom: 8px;
}

/* 处理中卡片样式 */
.upload {
  width: 200px;
  height: 238px;
  padding: 16px 12px;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
  border-radius: 12px;
  background: #FFF;
  box-shadow: 0px 0px 16px 0px rgba(0, 0, 0, 0.15);
}

.image-placeholder {
  width: 176px;
  height: 98px;
  flex-shrink: 0;
  fill: #D9D9D9;
  opacity: 0.4;
}

.processing-status {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.processing-text {
  color: #333;
  font-family: "PingFang SC";
  font-size: 14px;
  font-style: normal;
  font-weight: 600;
  line-height: normal;
}

.progress-bar {
  width: 175px;
  height: 4px;
  border-radius: 2px;
  background: #F0F0F0;
  position: relative;
}

.progress-fill {
  width: 83px;
  height: 4px;
  position: absolute;
  left: -0.5px;
  bottom: 0.169px;
  background: #1890FF;
  border-radius: 2px;
}

.url-text {
  width: 176px;
  height: 44px;
  flex-shrink: 0;
  color: rgba(153, 153, 153, 0.40);
  font-family: "PingFang SC";
  font-size: 14px;
  font-style: normal;
  font-weight: 400;
  line-height: 22px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: break-all;
}

/* 可点击区域样式 */
.clickable-area {
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 12px 8px;
}

/* 鼠标悬停效果只应用于可点击区域 */
.clickable-area:hover {
  opacity: 0.8;
}

/* 不可点击区域样式 */
.non-clickable-area {
  pointer-events: none; /* 禁用鼠标事件 */
  opacity: 0.8;
  padding: 8px 12px 24px;
}

/* 调整图标和文字间距 */
.upload-icon {
  margin-bottom: 8px;
}

.upload-text {
  color: #3FA6FC;
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  line-height: 20px;
}

/* 渠道图标容器样式 */
.icon-container {
  display: flex;
  justify-content: center;
  gap: 4px;
  margin: 8px 0;
}

/* 底部说明文字样式 */
.link-text {
  color: #999;
  text-align: center;
  font-size: 14px;
  font-weight: 400;
  line-height: 20px;
}

/* 添加最小高度确保容器尺寸稳定 */
.my-uploads-section {
  min-height: 310px; /* 根据实际内容调整这个值 */
  transition: all 0.3s ease;
  will-change: height; /* 优化高度变化的性能 */
}

/* 确保滚动容器也具有最小高度 */
.overflow-x-auto {
  min-height: 238px; /* 这个高度应该和卡片的高度一致 */
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
  transition: height 0.3s ease;
}
</style> 