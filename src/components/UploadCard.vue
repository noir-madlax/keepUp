<template>
  <!-- 根据状态显示不同的卡片 -->
  <div v-if="article.status === 'processed'" class="article-card cursor-pointer hover:shadow-lg transition-shadow" @click="navigateToDetail(article.id)">
    <!-- 已完成的文章卡片内容 -->
    <div class="article-image">
      <img :src="getArticleImage()" :alt="article.title || '文章封面'">
      <div class="upload-time">{{ getUploadTimeText(article.created_at) }}上传</div>
    </div>
    
    <div class="title-text">
      {{ article.title || '无标题' }}
    </div>
    
    <div class="info-container">
      <!-- Author Info -->
      <div class="author-container">
        <div class="author-avatar-wrapper">
          <img 
            v-if="article.author?.icon" 
            :src="article.author.icon" 
            :alt="article.author.name" 
            class="author-avatar"
          />
        </div>
        <span class="author-name">
          {{ article.author?.name || '未知作者' }}
        </span>
      </div>
      
      <!-- Channel and Date -->
      <div class="meta-container">
        <div class="finish-channel-icon">
          <img 
            v-if="article.channel"
            :src="`/images/icons/${getChannelIcon(article.channel)}`" 
            :alt="article.channel" 
          />
        </div>
        <span class="date-text">{{ formatDate(article.publish_date) }}</span>
      </div>
    </div>
  </div>

  <!-- 处理中/失败/等待处理的卡片 -->
  <div v-else class="upload">
    <div class="image-placeholder">
      <svg xmlns="http://www.w3.org/2000/svg" width="176" height="98" viewBox="0 0 176 98" fill="none">
        <g opacity="0.4">
          <rect width="176" height="98" rx="8" fill="#D9D9D9"/>
        </g>
      </svg>
      <div class="upload-time">{{ getUploadTimeText(article.created_at) }}上传</div>
    </div>

    <div class="processing-status">
      <span class="processing-text">{{ getStatusText }}</span>
      <div v-if="article.status === 'processing'" class="progress-bar">
        <div class="progress-fill"></div>
      </div>
    </div>

    <div class="url-text">
      {{ article.url || article.original_url || '无链接' }}
    </div>

    <div class="channel-icon">
      <img 
        :src="`/images/icons/${getPlatformIcon()}`"
        :alt="article.platform || '未知平台'"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { format, differenceInMinutes, differenceInHours, differenceInDays } from 'date-fns'
import type { ArticleRequest } from '@/types/article'
import { useRouter } from 'vue-router'

const props = defineProps<{
  article: ArticleRequest
}>()

const router = useRouter()

// 添加跳转方法
const navigateToDetail = (articleId?: string) => {
  if (articleId) {
    router.push(`/article/${articleId}`)
  }
}

// 获取状态显示文本
const getStatusText = computed(() => {
  switch (props.article.status) {
    case 'processing':
      return '处理中...'
    case 'failed':
      return '处理失败'
    case 'rejected':
      return '已拒绝'
    case 'pending':
      return '等待处理'
    default:
      return '未知状态'
  }
})

// 获取文章封面图片
const getArticleImage = () => {
  return props.article.cover_image_url || '/images/default-cover.png'
}

// 获取频道图标
const getChannelIcon = (channel: string) => {
  switch (channel?.toLowerCase()) {
    case 'youtube':
      return 'youtube.svg'
    case 'spotify':
      return 'spotify.svg'
    case 'apple':
      return 'apple-podcast.svg'
    default:
      return 'default-channel.svg'
  }
}

// 格式化日期
const formatDate = (date?: string) => {
  if (!date) return ''
  return format(new Date(date), 'yyyy-MM-dd')
}

// 获取平台图标
const getPlatformIcon = (platform: string | undefined) => {
  // 如果有明确的平台信息，直接使用
  if (platform) {
    switch (platform.toLowerCase()) {
      case 'youtube':
        return 'youtube.svg'
      case 'spotify':
        return 'spotify.svg'
      case 'applet':
        return 'apple-podcast.svg'
      default:
        return 'default.svg'
    }
  }
  
  // 如果没有平台信息，根据 URL 判断
  const url = props.article.url || props.article.original_url || ''
  if (!url) return 'default-channel.svg'

  if (url.includes('youtube.com') || url.includes('youtu.be')) {
    return 'youtube.svg'
  }
  if (url.includes('spotify.com')) {
    return 'spotify.svg'
  }
  if (url.includes('apple.com') || url.includes('podcasts.apple')) {
    return 'apple-podcast.svg'
  }
  
  return 'default-channel.svg'
}

// 添加计算上传时间的函数
const getUploadTimeText = (uploadTime?: string) => {
  if (!uploadTime) return '未知时间'
  
  const now = new Date()
  const uploadDate = new Date(uploadTime)
  const diffInMinutes = differenceInMinutes(now, uploadDate)
  const diffInHours = differenceInHours(now, uploadDate)
  const diffInDays = differenceInDays(now, uploadDate)

  if (diffInMinutes < 1) {
    return '刚刚'
  }
  
  if (diffInMinutes < 60) {
    return `${diffInMinutes}分钟前`
  }
  
  if (diffInDays < 1) {
    return `${diffInHours}小时前`
  }
  
  return `${diffInDays}天前`
}
</script>

<style scoped>
.article-card {
  position: relative;
  width: 200px;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  border-radius: 12px;
  background: #FFF;
  box-shadow: 0px 0px 16px 0px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease-in-out;
}

.article-card:hover {
  transform: translateY(-2px);
}

.article-image {
  width: 176px;
  height: 98px;
  position: relative;
  border-radius: 8px;
  overflow: hidden;
}

.article-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.title-text {
  width: 158px;
  height: 44px;
  color: #333333;
  font-family: "PingFang SC";
  font-size: 16px;
  font-weight: 600;
  line-height: 22px;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: break-all;
}

.author-container {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
}

.author-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.author-name {
  color: #666666;
  font-family: "PingFang SC";
  font-size: 14px;
  font-weight: 250;
  line-height: 20px;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: break-all;
  max-width: 100px;
}

.meta-container {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
}

.date-text {
  color: #666666;
  font-family: "PingFang SC";
  font-size: 14px;
  font-weight: 250;
  line-height: 20px;
}

.finish-channel-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.channel-icon img {
  width: 100%;
  height: 100%;
}

/* 处理中卡基础样式 */
.upload {
  width: 200px;
  height: 238px;
  padding: 16px 12px;
  display: flex;  /* 添加 display: flex */
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  border-radius: 12px;
  background: #FFF;
  box-shadow: 0px 0px 16px 0px rgba(0, 0, 0, 0.15);
  box-sizing: border-box;
}

/* 图片占位符样式 */
.image-placeholder {
  width: 176px;
  height: 98px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  position: relative;  /* 添加相对定位 */
}

.image-placeholder svg {
  width: 100%;
  height: 100%;
}

/* 处理状态区域样式 */
.processing-status {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  width: 100%;
}

.processing-text {
  color: #333;
  font-family: "PingFang SC";
  font-size: 14px;
  font-style: normal;
  font-weight: 600;
  line-height: normal;
}

/* 进度条样式 */
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

/* URL文本样式 */
.url-text {
  width: 176px;
  height: 44px;
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

/* 频道图标样式 */
.channel-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.4;
}

.channel-icon svg {
  width: 20px;
  height: 20px;
}

/* 修改 info-container 样式 */
.info-container {
  display: flex;
  flex-direction: column;
  gap: 8px;  /* 控制作者区域和channel区域的垂直间距 */
  width: 100%;
}

/* 修改 author-container 样式 */
.author-container {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
}

/* 添加 author-avatar-wrapper 样式 */
.author-avatar-wrapper {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: #F5F5F5;  /* 添加背景色 */
  flex-shrink: 0;  /* 防止被压缩 */
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* 修改 meta-container 样式 */
.meta-container {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
}

/* 修改 author-avatar 样式 */
.author-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 修改上传时间样式 */
.upload-time {
  position: absolute;
  top: 2px;
  right: 1px;
  color: #FFFFFF;  /* 白色文字 #FFFFFF 100% */
  font-family: "PingFang SC";
  font-size: 11px;
  font-weight: Medium;
  line-height: 15px;
  background: rgba(0, 0, 0, 0.8);  /* 黑色背景 #000000 80% */
  padding: 2px 4px;
  border-radius: 4px;
  z-index: 1;
}
</style>