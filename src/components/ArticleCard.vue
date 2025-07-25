<template>
  <!-- 根据状态决定是否使用路由链接 -->
  <router-link 
    v-if="article.status === 'processed'" 
    :to="`/article/${article.id}`"
    custom
    v-slot="{ navigate }"
  >
    <div 
      class="card-container"
      @click="handleClick($event, navigate)"
    >
      <!-- 已处理完成的文章卡片内容 -->
      <div class="card-top">
        <!-- 左侧标题 -->
        <div class="article-title-wrapper">
          <h3 class="article-title">{{ getTitle() }}</h3>
        </div>
        
        <!-- 右侧封面 -->
        <div class="cover-container">
          <img 
            :src="getArticleImage()" 
            :alt="article.title"
            class="cover-image"
            referrerpolicy="no-referrer"
            @error="handleCoverImageError"
          />
          <!-- 隐藏上传时间显示 -->
          <div v-if="false" class="upload-time">
            {{ t('upload.card.fallback.uploaded') }}{{ getUploadTimeText(article.created_at) }}
          </div>
        </div>
      </div>

      <!-- 浏览量信息 -->
      <div v-if="article.viewer_count !== undefined" class="viewer-count">
        <img src="/images/icons/view.svg" alt="Viewers" class="viewer-icon" />
        <span class="viewer-number">{{ article.viewer_count }}</span>
      </div>

      <!-- 分隔线 -->
      <div class="divider"></div>

      <!-- 下半部分 -->
      <div class="card-bottom">
        <!-- 左侧作者信息 -->
        <div class="author-info">
          <div class="author-icon-wrapper">
            <img 
              :src="getAuthorIcon()"
              :alt="article.author?.name" 
              class="author-icon"
              referrerpolicy="no-referrer"
              @error="handleAuthorImageError"
            />
          </div>
          <span class="author-name">{{ getAuthorName() }}</span>
        </div>

        <!-- 右侧渠道和日期 -->
        <div class="channel-date">
          <img 
            :src="`/images/icons/${getChannelIcon(article.channel)}`" 
            :alt="article.channel" 
            class="channel-icon" 
          />
          <span class="date">{{ formatDate(article.publish_date) }}</span>
        </div>
      </div>
    </div>
  </router-link>

  <!-- 处理中/失败状态的卡片 -->
  <div v-else class="card-container">
    <div class="card-top">
      <!-- 左侧状态区域 -->
      <div class="processing-status">
        <!-- 处理中状态 -->
        <div v-if="article.status === 'processing'" class="processing-text">
          <div>Processing...</div>
          <div class="estimate-time">Est. 3 minutes</div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: `${progress}%`, left: 0 }"></div>
          </div>
        </div>
        
        <!-- 失败状态 -->
        <div v-else-if="article.status === 'failed'" class="failed-text">
          <div class="error-title">{{ getErrorMessage }}</div>
          <!-- 失败状态下的URL显示 -->
          <div 
            class="url-text-failed cursor-pointer hover:text-blue-500" 
            @click="handleUrlClick"
          >
            {{ truncateUrl(article.original_url) || t('upload.card.fallback.noLink') }}
          </div>
          <div class="error-text">
            We are aware of this issue and are working on it. You will receive an email once it's resolved.
          </div>
        </div>

        <!-- 未知状态 -->
        <div v-else class="unknown-text">
          <div>Unknown Status</div>
          <div class="error-text">
            {{ t('upload.card.error.unknown') }}
          </div>
        </div>

        <!-- URL显示 (仅对非失败状态显示) -->
        <div 
          v-if="article.status !== 'failed'"
          class="url-text-new cursor-pointer hover:text-blue-500" 
          @click="handleUrlClick"
        >
          {{ truncateUrl(article.original_url) || t('upload.card.fallback.noLink') }}
        </div>
      </div>
      
      <!-- 右侧封面 兜底图-->
      <div class="cover-container">
        <img 
          src="/images/covers/article_default.png" 
          alt="Article placeholder"
          class="cover-image"
        />
      </div>
    </div>

    <!-- 分隔线 -->
    <div class="divider"></div>

    <!-- 底部操作区 -->
    <div class="card-bottom">
      <!-- 左侧渠道图标 -->
      <div class="author-info">
        <div class="author-icon-wrapper">
          <img 
            :src="`/images/icons/${getPlatformIcon(article.platform)}`"
            :alt="article.platform"
            class="platform-icon"
          />
        </div>
      </div>

      <!-- 右侧删除按钮 -->
      <div class="bottom-actions">
        <img 
          v-if="article.status === 'failed'"
          src="/images/icons/delete.svg"
          :alt="t('upload.card.action.delete')"
          class="delete-icon"
          @click.stop="handleDelete"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { format, differenceInMinutes, differenceInHours, differenceInDays } from 'date-fns'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// 2024-03-19: 更新 Props 类型定义
interface Props {
  article: {
    id?: string
    title?: string
    cover_image_url?: string
    channel?: string
    publish_date?: string
    author?: {
      name?: string
      icon?: string
    }
    status?: 'processing' | 'processed' | 'failed'
    created_at?: string
    error_message?: string
    original_url?: string
    platform?: string
    requestId?: string
    viewer_count?: number
  }
}

const props = defineProps<Props>()

// 2024-03-19: 添加 emit 定义
const emit = defineEmits(['delete'])

// 2024-03-25: 添加进度状态管理
const progress = ref(0)
let progressTimer: ReturnType<typeof setInterval> | null = null

// 图片加载失败状态管理
const coverImageError = ref(false)
const authorImageError = ref(false)

// 处理进度条逻辑
const startProgress = () => {
  // 重置进度
  progress.value = 0
  
  // 清理可能存在的旧定时器
  if (progressTimer) {
    clearInterval(progressTimer)
  }
  
  // 计算每次增加的进度
  // 150秒完成，每200ms更新一次，总共需要更新750次
  // 100% / 750 ≈ 0.133% 每次增加的进度
  const increment = 0.133
  
  progressTimer = setInterval(() => {
    if (progress.value < 100) {
      progress.value = Math.min(100, progress.value + increment)
    } else {
      // 达到100%时清理定时器
      if (progressTimer) {
        clearInterval(progressTimer)
        progressTimer = null
      }
    }
  }, 200) // 每200ms更新一次
}

// 监听处理状态变化
watch(() => props.article.status, (newStatus) => {
  if (newStatus === 'processing') {
    startProgress()
  } else {
    // 状态改变时清理定时器
    if (progressTimer) {
      clearInterval(progressTimer)
      progressTimer = null
    }
  }
}, { immediate: true })

// 监听文章变化，重置图片错误状态
watch(() => props.article.id, () => {
  coverImageError.value = false
  authorImageError.value = false
})

// 组件卸载时清理
onUnmounted(() => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
})

const handleClick = (event: MouseEvent, navigate?: () => void) => {
  if (!navigate || !props.article.id) return
  
  if (event.metaKey || event.ctrlKey) {
    window.open(`/article/${props.article.id}`, '_blank')
  } else {
    navigate()
  }
}

// 2024-03-19: 添加状态文本计算属性
const getStatusText = computed(() => {
  switch (props.article.status) {
    case 'processing':
      return t('upload.card.fallback.processing')
    case 'failed':
      return t('upload.card.fallback.failed')
    default:
      return t('upload.card.fallback.unknownStatus')
  }
})

// 2024-03-19: 添加错误信息处理
const getErrorMessage = computed(() => {
  if (!props.article.error_message) return t('upload.card.error.unknown')
  
  if (props.article.error_message.includes('video') || 
      props.article.error_message.includes('视频')) {
    return 'Processing Failed'
  }
  
  if (props.article.error_message.includes('subtitle') || 
      props.article.error_message.includes('字幕')) {
        return 'Processing Failed'
      }
  
  // 如果没有匹配到具体错误类型，返回未知错误
  return 'Processing Failed'
})

const getArticleImage = () => {
  // 如果图片加载失败，直接返回默认图片
  if (coverImageError.value) {
    return '/images/covers/article_default.png'
  }
  
  if (props.article.cover_image_url && 
      props.article.cover_image_url.trim() !== '' && 
      !props.article.cover_image_url.includes('qpic.cn') &&
      props.article.cover_image_url !== '无缩略图') {
    return props.article.cover_image_url
  }
  return '/images/covers/article_default.png'
}

// 处理封面图片加载错误
const handleCoverImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (!coverImageError.value && img.src !== '/images/covers/article_default.png') {
    coverImageError.value = true
  }
}

const formatDate = (date: string | undefined) => {
  if (!date) return t('upload.card.fallback.unknownDate')
  try {
    return format(new Date(date), 'yyyy-MM-dd')
  } catch (error) {
    console.error('日期格式化错误:', error)
    return t('upload.card.fallback.unknownDate')
  }
}

const getChannelIcon = (channel: string | undefined): string => {
  if (!channel) return 'channel_default.png'
  
  const iconMap: Record<string, string> = {
    'YouTube': 'youtube.svg',
    'youtube': 'youtube.svg',
    'bilibili': 'bilibili.svg',
    'Apple Podcast': 'apple-podcast.svg',
    'Spotify': 'spotify.svg',
    'spotify': 'spotify.svg',
    'wechat': 'wechat.svg',  
    'WeChat': 'wechat.svg',
    'weixin': 'wechat.svg',
    'webpage': 'web.svg'
  }
  return iconMap[channel.toLowerCase()] || 'channel_default.png'
}

// 2024-03-19: 添加平台图标获取函数
const getPlatformIcon = (platform: string | undefined) => {
  if (!platform) return 'default.svg'
  
  const iconMap: Record<string, string> = {
    'youtube': 'youtube.svg',
    'YouTube': 'youtube.svg',
    'bilibili': 'bilibili.svg',
    'spotify': 'spotify.svg',
    'Spotify': 'spotify.svg',
    'apple': 'apple-podcast.svg',
    'Apple Podcast': 'apple-podcast.svg',
    'webpage': 'web.svg'
  }
  return iconMap[platform.toLowerCase()] || 'default.svg'
}

const getAuthorIcon = () => {
  // 如果图片加载失败，直接返回默认头像
  if (authorImageError.value) {
    return '/images/icons/author_default.svg'
  }
  
  return props.article.author?.icon || '/images/icons/author_default.svg'
}

// 处理作者头像加载错误
const handleAuthorImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (!authorImageError.value && img.src !== '/images/icons/author_default.svg') {
    authorImageError.value = true
  }
}

const getAuthorName = () => {
  if (!props.article.author?.name || 
      props.article.author.name === t('upload.card.fallback.unknownAuthor') || 
      props.article.author.name === 'Unknown') {
    return t('upload.card.fallback.unknownAuthor')
  }
  return props.article.author.name
}

const getTitle = () => {
  return props.article.title || t('upload.card.fallback.noTitle')
}

// 2024-03-19: 添加上传时间处理函数
const getUploadTimeText = (date: string | undefined) => {
  if (!date) return t('upload.card.fallback.unknownDate')
  
  const now = new Date()
  const uploadTime = new Date(date)
  
  const minutesDiff = differenceInMinutes(now, uploadTime)
  if (minutesDiff < 60) {
    return t('upload.card.time.minutes', { minutes: minutesDiff })
  }
  
  const hoursDiff = differenceInHours(now, uploadTime)
  if (hoursDiff < 24) {
    return t('upload.card.time.hours', { hours: hoursDiff })
  }
  
  const daysDiff = differenceInDays(now, uploadTime)
  return t('upload.card.time.days', { days: daysDiff })
}

// 2024-03-19: 添加URL点击处理函数
const handleUrlClick = (event: Event) => {
  event.stopPropagation()
  const url = props.article.original_url
  if (url) {
    window.open(url, '_blank')
  }
}

// 2024-03-19: 添加删除处理函数
const handleDelete = (event: Event) => {
  event.stopPropagation()
  if (props.article.requestId) {
    emit('delete', props.article.requestId)
  }
}

// 添加URL截断函数
const truncateUrl = (url?: string): string => {
  if (!url) return ''
  if (url.length <= 50) return url
  return url.substring(0, 47) + '...'
}
</script>

<style scoped>
.card-container {
  display: flex;
  width: 100%;
  min-width: 340px;
  max-width: 450px;
  min-height: 180px;
  padding: 12px;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  border-radius: 12px;
  border: 1px solid #F2F2F2;
  background: #FFF;
  box-shadow: 0px 0px 8px 0px rgba(0, 0, 0, 0.10);
  cursor: pointer;
  transition: all 0.3s ease;
}

.card-container:hover {
  transform: translateY(-2px);
  box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
}

.card-top {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
  overflow: hidden;
}

.article-title {
  min-height: 48px;
  max-height: 96px;
  min-width: 140px;
  max-width: calc(100% - 130px);
  overflow: hidden;
  color: #333;
  font-family: "PingFang SC";
  font-size: 16px;
  font-weight: 600;
  line-height: 24px;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  white-space: normal;
  text-overflow: ellipsis;
  -webkit-line-clamp: 4;
}

.cover-container {
  position: relative;
  width: auto;
  height: 100px;
  flex-shrink: 0;
  border-radius: 12px;
  overflow: hidden;
}

.cover-image {
  width: 100%;
  height: 100%;
  max-width: 120px;
  object-fit: cover;
  object-position: center;
  border-radius: 12px;
}

@media (min-width: 400px) {
  .cover-image {
    max-width: 180px;
    object-fit: contain;
  }
  
  .article-title {
    max-width: calc(100% - 20px);
  }
}

.divider {
  width: 100%;
  height: 0;
  border-top: 1px solid #EEE;
  margin: 0;
}

.card-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 24px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.author-icon-wrapper {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.author-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
}

.author-name {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #666;
  font-family: "PingFang SC";
  font-size: 14px;
  font-weight: 400;
}

.channel-date {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 8px;  /* 添加负边距使整体向左移动1px */
}

.channel-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.date {
  width: 83px;
  color: #666;
  font-family: "PingFang SC";
  font-size: 14px;
  font-weight: 400;
  white-space: nowrap;
}

/* 2024-03-19: 添加处理中状态相关样式 */
.processing-status {
  flex: 1;
  min-width: 0;
  padding-right: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.processing-text {
  color: #333;
  font-family: "PingFang SC";
  font-size: 16px;
  font-weight: 600;
  line-height: 24px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* 2024-03-26: 添加失败状态样式 */
.failed-text {
  display: flex;
  flex-direction: column;
  gap: 4px; /* 减小整体间距 */
  padding-bottom: 4px;
}

.error-title {
  color: #333;
  font-family: "PingFang SC";
  font-size: 16px;
  font-weight: 600;
  line-height: 20px; /* 减小行高 */
  margin-bottom: 2px; /* 微调与URL的间距 */
}

.unknown-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: #666;
  font-family: "PingFang SC";
  font-size: 16px;
  font-weight: 600;
  line-height: 24px;
}

.estimate-time {
  font-size: 14px;
  color: #666;
  font-weight: 400;
}

.progress-bar {
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: #F0F0F0;
  position: relative;
  overflow: hidden;
  margin-top: 8px;
}

.progress-fill {
  height: 100%;
  background: #1890FF;
  border-radius: 2px;
  position: absolute;
  top: 0;
  transition: width 0.3s ease-in-out;
}

.error-text {
  color: #D81E06;
  font-family: "PingFang SC";
  font-size: 14px;
  font-weight: 400;
  line-height: 18px; /* 减小行高 */
}

.url-text-new {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
  max-width: calc(100% px);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
  font-family: "PingFang SC";
  font-weight: 400;
}

.platform-icon {
  width: 20px;
  height: 20px;
  opacity: 0.6;
  transition: opacity 0.2s;
  border-radius: 50%;  /* 添加圆角，与作者头像样式一致 */
}

.bottom-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
}

.delete-icon {
  width: 20px;
  height: 20px;
  opacity: 0.6;
  transition: opacity 0.2s;
  cursor: pointer;
}

.delete-icon:hover {
  opacity: 1;
}

/* 隐藏上传时间 */
.upload-time {
  display: none;
}

/* 2024-03-26: 添加失败状态下URL的特殊样式 */
.url-text-failed {
  font-size: 12px;
  color: #999;
  /* 移除margin设置，统一使用gap控制 */
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.2; /* 减小行高 */
  font-family: "PingFang SC";
  font-weight: 400;
}

/* 浏览人数相关样式 */
.article-title-wrapper {
  flex: 1;
  min-width: 0;
}

.viewer-count {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0;
  margin: 0;
}

.viewer-icon {
  width: 18px; /* 放大50%: 12px -> 18px */
  height: 18px;
  opacity: 0.6;
  flex-shrink: 0;
}

.viewer-number {
  color: #999;
  font-family: "PingFang SC";
  font-size: 16px; /* 放大50%: 11px -> 16px */
  font-weight: 400;
  line-height: 1;
}
</style>