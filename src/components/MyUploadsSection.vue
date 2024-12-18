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
        @scroll="handleScroll"
      >
        <!-- NewUploadCard 固定在第一个位置 -->
        <div class="upload-container flex-shrink-0">
          <!-- Upload Icon -->
          <div class="upload-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="66" height="66" viewBox="0 0 66 66" fill="none">
              <rect width="66" height="66" rx="33" fill="#EBEBEB"/>
              <path d="M22.9995 47.9869C21.4082 47.9869 19.8821 47.2969 18.7569 46.0686C17.6317 44.8403 16.9995 43.1744 16.9995 41.4373V37.0943C16.9995 36.5153 17.2102 35.96 17.5853 35.5506C17.9604 35.1411 18.4691 34.9111 18.9995 34.9111C19.5299 34.9111 20.0387 35.1411 20.4137 35.5506C20.7888 35.96 20.9995 36.5153 20.9995 37.0943V41.4504C20.9995 42.0294 21.2102 42.5847 21.5853 42.9942C21.771 43.1969 21.9915 43.3577 22.2341 43.4674C22.4768 43.5771 22.7369 43.6336 22.9995 43.6336H42.9995C43.5299 43.6336 44.0387 43.4036 44.4137 42.9942C44.7888 42.5847 44.9995 42.0294 44.9995 41.4504V37.1074C44.9995 36.5284 45.2102 35.9731 45.5853 35.5637C45.9604 35.1542 46.4691 34.9242 46.9995 34.9242C47.5299 34.9242 48.0387 35.1542 48.4137 35.5637C48.7888 35.9731 48.9995 36.5284 48.9995 37.1074V41.4504C48.9995 43.1875 48.3674 44.8534 47.2422 46.0817C46.1169 47.31 44.5908 48 42.9995 48L22.9995 47.9869ZM30.9995 37.813V25.4519L28.4135 28.2726C28.034 28.6544 27.534 28.8613 27.018 28.85C26.502 28.8388 26.01 28.6102 25.6448 28.2121C25.2796 27.814 25.0696 27.2773 25.0585 26.714C25.0474 26.1508 25.2363 25.6047 25.5855 25.1899L31.5855 18.6403C31.7713 18.4373 31.9918 18.2763 32.2346 18.1664C32.4774 18.0566 32.7377 18 33.0005 18C33.2633 18 33.5236 18.0566 33.7664 18.1664C34.0092 18.2763 34.2298 18.4373 34.4155 18.6403L39.9495 24.6747C40.1501 24.8735 40.3116 25.1147 40.4242 25.3837C40.5367 25.6527 40.5981 25.9439 40.6045 26.2395C40.6108 26.5352 40.5621 26.8292 40.4613 27.1037C40.3604 27.3782 40.2095 27.6274 40.0177 27.8364C39.826 28.0453 39.5973 28.2094 39.3456 28.319C39.0939 28.4285 38.8245 28.481 38.5537 28.4734C38.2828 28.4658 38.0162 28.3983 37.77 28.2748C37.5239 28.1513 37.3032 27.9745 37.1215 27.7552L34.9995 25.4563V37.813C34.9995 38.0997 34.9478 38.3836 34.8473 38.6485C34.7468 38.9133 34.5994 39.154 34.4137 39.3567C34.228 39.5595 34.0075 39.7203 33.7649 39.83C33.5222 39.9397 33.2622 39.9962 32.9995 39.9962C32.7369 39.9962 32.4768 39.9397 32.2341 39.83C31.9915 39.7203 31.771 39.5595 31.5853 39.3567C31.3996 39.154 31.2523 38.9133 31.1518 38.6485C31.0512 38.3836 30.9995 38.0997 30.9995 37.813Z" fill="#31394C"/>
            </svg>
          </div>
          <!-- Upload Text -->
          <div class="upload-text">点击上传文件</div>
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
          <div class="link-text">播客、视频等内容的链接</div>
        </div>

        <!-- 加载状态显示骨架屏 -->
        <template v-if="localLoading">
          <div 
            v-for="n in 8" 
            :key="n"
            class="flex-shrink-0 w-[200px] h-[238px] bg-gray-100 rounded-xl animate-pulse"
          >
            <!-- 骨架屏内部结构 -->
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
        if (request.status !== 'processed' || !request.original_url) {
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
          title: articleData.title,
          author: articleData.author,
          publish_date: articleData.publish_date,
          channel: articleData.channel,
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

/* NewUploadCard 相关样式 */
.upload-container {
  width: 200px;
  height: 238px;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 8px;
  border-radius: 12px;
  background: #FFF;
  box-shadow: 0px 0px 16px 0px rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
  box-sizing: border-box;
  cursor: pointer;
}

.upload-icon {
  width: 66px;
  height: 66px;
  flex-shrink: 0;
}

.upload-text {
  color: #3FA6FC;
  text-align: center;
  font-family: "PingFang SC";
  font-size: 14px;
  font-style: normal;
  font-weight: 600;
  line-height: normal;
}

.icon-container {
  display: flex;
  align-items: center;
  gap: 4px;
}

.icon {
  display: flex;
  justify-content: center;
  align-items: center;
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

.youtube-icon {
  width: 18px;
  height: 14px;
  object-fit: contain;
}

.podcast-icon {
  width: 14px;
  height: 14px;
  object-fit: contain;
}

.link-text {
  color: #999;
  text-align: center;
  font-family: "PingFang SC";
  font-size: 14px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
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