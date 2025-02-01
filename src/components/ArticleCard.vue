<template>
  <!-- 根据状态决定是否使用路由链接 -->
  <router-link 
    v-if="article.status === 'processed'" 
    :to="`/article/${article.id}`"
    class="card-container"
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
        <h3 class="article-title">{{ getTitle() }}</h3>
        
        <!-- 右侧封面 -->
        <div class="cover-container">
          <img 
            :src="getArticleImage()" 
            :alt="article.title"
            class="cover-image" 
          />
          <!-- 隐藏上传时间显示 -->
          <div v-if="false" class="upload-time">
            {{ t('upload.card.fallback.uploaded') }}{{ getUploadTimeText(article.created_at) }}
          </div>
        </div>
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
        <span class="processing-text">{{ getStatusText }}</span>
        
        <!-- 处理中状态显示进度条 -->
        <div v-if="article.status === 'processing'" class="progress-bar">
          <div class="progress-fill"></div>
        </div>
        
        <!-- 失败状态显示错误信息 -->
        <div v-if="article.status === 'failed'" class="error-text">
          {{ getErrorMessage }}
        </div>

        <!-- URL显示移到这里 -->
        <div 
          class="url-text-new cursor-pointer hover:text-blue-500" 
          @click="handleUrlClick"
        >
          {{ truncateUrl(article.original_url) || t('upload.card.fallback.noLink') }}
        </div>
      </div>
      
      <!-- 右侧封面 -->
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
import { computed } from 'vue'
import { format, differenceInMinutes, differenceInHours, differenceInDays } from 'date-fns'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const router = useRouter()

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
  }
}

const props = defineProps<Props>()

// 2024-03-19: 添加 emit 定义
const emit = defineEmits(['delete'])

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
    return t('upload.card.error.videoInfo')
  }
  
  if (props.article.error_message.includes('subtitle') || 
      props.article.error_message.includes('字幕')) {
    return t('upload.card.error.subtitle')
  }
  
  return t('upload.card.error.unknown')
})

const getArticleImage = () => {
  if (props.article.cover_image_url && 
      props.article.cover_image_url.trim() !== '' && 
      !props.article.cover_image_url.includes('qpic.cn') &&
      props.article.cover_image_url !== '无缩略图') {
    return props.article.cover_image_url
  }
  return '/images/covers/article_default.png'
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
    'Apple Podcast': 'apple-podcast.svg',
    'Spotify': 'spotify.svg',
    'spotify': 'spotify.svg',
    'webpage': 'web.svg'
  }
  return iconMap[channel.toLowerCase()] || 'channel_default.png'
}

// 2024-03-19: 添加平台图标获取函数
const getPlatformIcon = (platform: string | undefined) => {
  if (!platform) return 'default.svg'
  
  const iconMap: Record<string, string> = {
    'youtube': 'youtube.svg',
    'spotify': 'spotify.svg',
    'apple': 'apple-podcast.svg',
    'webpage': 'web.svg'
  }
  return iconMap[platform.toLowerCase()] || 'default.svg'
}

const getAuthorIcon = () => {
  return props.article.author?.icon || '/images/icons/author_default.svg'
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
  if (!props.article.title || props.article.title.trim() === '') {
    return t('upload.card.fallback.noTitle')
  }
  return props.article.title
}

// 2024-03-19: 添加上传时间处理函数
const getUploadTimeText = (date: string) => {
  const now = new Date()
  const uploadDate = new Date(date)
  
  const minutesDiff = differenceInMinutes(now, uploadDate)
  if (minutesDiff < 60) {
    return t('upload.card.time.minutes', { minutes: minutesDiff })
  }
  
  const hoursDiff = differenceInHours(now, uploadDate)
  if (hoursDiff < 24) {
    return t('upload.card.time.hours', { hours: hoursDiff })
  }
  
  const daysDiff = differenceInDays(now, uploadDate)
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

.card-container:hover {
  transform: translateY(-2px);
  box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
}

.card-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  overflow: hidden;
}

.article-title {
  height: 72px;
  min-width: 140px;
  max-width: calc(100% - 140px);
  flex: 1;
  overflow: hidden;
  color: #333;
  font-family: "PingFang SC";
  font-size: 16px;
  font-weight: 600;
  line-height: 24px;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  white-space: normal;
  text-overflow: ellipsis;
}

.cover-container {
  position: relative;
  width: auto;
  height: 120px;
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
    max-width: 190px;
    object-fit: contain;
  }
  
  .article-title {
    max-width: calc(100% - 202px);
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
}

.progress-bar {
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: #F0F0F0;
  position: relative;
  overflow: hidden;
}

.progress-fill {
  width: 50%;
  height: 100%;
  background: #1890FF;
  border-radius: 2px;
  position: absolute;
  left: 0;
  top: 0;
  animation: progress 2s infinite linear;
}

@keyframes progress {
  0% {
    left: -50%;
  }
  100% {
    left: 100%;
  }
}

.error-text {
  color: #D81E06;
  font-family: "PingFang SC";
  font-size: 14px;
  font-weight: 400;
  line-height: 20px;
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
</style>