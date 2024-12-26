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
        <div class="upload-container flex-shrink-0" @click="handleNewUploadClick">
          <!-- Upload Icon -->
          <div class="upload-icon">
            <img src="/images/icons/upload.svg" alt="Upload" class="w-full h-full">
          </div>
          <!-- Upload Text -->
          <div class="upload-text">{{ t('upload.card.uploadFile') }}</div>
          <!-- Icon Container -->
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
          <!-- Link Text -->
          <div class="link-text">{{ t('upload.card.supportedPlatforms') }}</div>
        </div>

         <!-- NewUploadCard2 固定文章上传的卡片在第二个位置 -->
         <div class="upload-container flex-shrink-0" @click="handleNewUploadClick">
          <!-- Upload Icon -->
          <div class="upload-icon">
            <img src="/images/icons/web.svg" alt="Upload" class="w-full h-full">
          </div>
          <!-- Upload Text -->
          <div class="upload-text">{{ t('upload.card.uploadWeb') }}</div>
          <!-- Icon Container -->
          <div class="icon-container">
            
          </div>
          <!-- Link Text -->
          <div class="link-text">{{ t('upload.card.webLink') }}</div>
        </div>
        <!-- 加载状态显示骨架屏 -->
        <template v-if="localLoading">
          <div 
            v-for="n in 8" 
            :key="n"
            class="flex-shrink-0 w-[200px] h-[238px] bg-gray-100 rounded-xl animate-pulse"
          >
            <!-- 骨架屏内部��构 -->
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
        <template v-else-if="articles.length">
          <UploadCard
            v-for="article in articles"
            :key="article.id"
            :article="article"
            class="flex-shrink-0 w-[200px] mb-2"
          />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import UploadCard from './UploadCard.vue'
import type { ArticleRequest } from '../types/article'
import { useAuthStore } from '../stores/auth'
import { supabase } from '../supabaseClient'

const { t } = useI18n()
const authStore = useAuthStore()

// Props
interface Props {
  isLoading?: boolean
  loadCompleted?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  loadCompleted: false
})

// Refs
const scrollContainer = ref<HTMLElement | null>(null)
const canScrollLeft = ref(false)
const canScrollRight = ref(true)
const articles = ref<ArticleRequest[]>([])
const localLoading = ref(true)

// 添加手势相关的状态
const touchStartX = ref(0)
const touchStartY = ref(0)
const isHorizontalMove = ref(false)
const minDirectionDelta = 20 // 判断方向的最小位移差值

// Methods
const handleScroll = () => {
  if (!scrollContainer.value) return
  
  const { scrollLeft, scrollWidth, clientWidth } = scrollContainer.value
  
  canScrollLeft.value = scrollLeft > 0
  canScrollRight.value = scrollLeft < scrollWidth - clientWidth
}

// 获取用户上传的文章
const fetchUserArticles = async () => {
  try {
    const userId = authStore.user?.id
    if (!userId) {
      localLoading.value = false
      articles.value = []
      return
    }

    localLoading.value = true
    
    // 1. 获取用户的所有请求
    const { data: requestsData, error: requestsError } = await supabase
      .from('keep_article_requests')
      .select(`
        id,
        url,
        status,
        created_at,
        error_message,
        original_url,
        platform
      `)
      .eq('user_id', userId)
      .order('created_at', { ascending: false })

    if (requestsError) {
      throw requestsError
    }

    // 2. 只对已处理的请求获取详细信息
    const processedRequests = await Promise.all(
      requestsData.map(async (request) => {
        // 如果不是已处理状态，直接返回请求信息
        if (request.status !== 'processed' || !request.url) {
          return request
        }

        // 通过 original_url 查找对应的文章
        const { data: articleData, error: articleError } = await supabase
          .from('keep_articles')
          .select(`
            id,
            title,
            publish_date,
            channel,
            cover_image_url,
            original_link,
            author:keep_authors (
              id,
              name,
              icon
            )
          `)
          .eq('original_link', request.original_url)
          .single()

        if (articleError) {
          return request
        }

        return {
          ...request,
          id: articleData.id,
          title: articleData.title,
          author: articleData.author,
          publish_date: articleData.publish_date,
          channel: request.platform,
          cover_image_url: articleData.cover_image_url
        }
      })
    )

    articles.value = processedRequests || []
    
  } catch (error) {
    ElMessage.error('获取上传文章失败')
  } finally {
    localLoading.value = false
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
const handleNewUploadClick = async () => {
  try {
    // 读取剪贴板内容
    const clipboardText = await navigator.clipboard.readText()
    // 验证是否是有效的URL
    const isValidUrl = clipboardText.startsWith('http://') || clipboardText.startsWith('https://')
    
    // 使用剪贴板内容或默认标记URL
    const uploadUrl = isValidUrl ? clipboardText : 'https://'
    
    if (!authStore.isAuthenticated) {
      // 存储到 localStorage，复用现有逻辑
      localStorage.setItem('pendingUploadUrl', uploadUrl)
    }
    
    // 触发上传事件，并传递 URL
    emit('upload', uploadUrl)
  } catch (err) {
    console.error('Failed to read clipboard:', err)
    // 读取失败时使用默认标记URL
    const defaultUrl = 'https://'
    if (!authStore.isAuthenticated) {
      localStorage.setItem('pendingUploadUrl', defaultUrl)
    }
    emit('upload', defaultUrl)
  }
}

// 处理触摸开始
const handleTouchStart = (e: TouchEvent) => {
  touchStartX.value = e.touches[0].clientX
  touchStartY.value = e.touches[0].clientY
  isHorizontalMove.value = false // 重置方向判断
}

// 处理触摸移动
const handleTouchMove = (e: TouchEvent) => {
  const touchX = e.touches[0].clientX
  const touchY = e.touches[0].clientY
  const diffX = Math.abs(touchX - touchStartX.value)
  const diffY = Math.abs(touchY - touchStartY.value)
  
  // 如果移动距离足够判断方向
  if (diffX > minDirectionDelta || diffY > minDirectionDelta) {
    // 如果是水平移动
    if (diffX > diffY) {
      isHorizontalMove.value = true
      e.stopPropagation() // 阻止事件冒泡，防止触发下拉刷新
    }
  }
}

// 处理触摸结束
const handleTouchEnd = () => {
  // 重置状态
  isHorizontalMove.value = false
}

// Lifecycle
onMounted(async () => {
  // 等待用户信息加载完成
  await authStore.loadUser()
  
  // 只有在登录状态下才获取文章
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
})

// 添加暴露给父组件的刷新方法
defineExpose({
  fetchUserArticles
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
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-container:hover {
  transform: translateY(-2px);
  box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.2);
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

/* 链接文字���式 */
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
</style> 