<template>
  <!-- 根据状态显示不同的卡片 -->
  <div v-if="article.status === 'processed'" class="article-card">
    <!-- 已完成的文章卡片内容 -->
    <div class="article-image">
      <img :src="getArticleImage()" :alt="article.title || '文章封面'">
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
        <span class="author-name">{{ article.author?.name || '未知作者' }}</span>
      </div>
      
      <!-- Channel and Date -->
      <div class="meta-container">
        <div class="channel-icon">
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
import { format } from 'date-fns'
import type { ArticleRequest } from '@/types/article'

const props = defineProps<{
  article: ArticleRequest
}>()

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
</script>

<style scoped>
.article-card {
  width: 200px;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  border-radius: 12px;
  background: #FFF;
  box-shadow: 0px 0px 16px 0px rgba(0, 0, 0, 0.15);
}

.article-image {
  width: 176px;
  height: 98px;
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
  overflow: hidden;
  color: #333;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: "PingFang SC";
  font-size: 16px;
  font-style: normal;
  font-weight: 600;
  line-height: normal;
}

.author-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  object-fit: cover;
}

.author-name {
  color: #333;
  font-family: "PingFang SC";
  font-size: 14px;
  font-weight: 400;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.meta-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-text {
  color: #666;
  font-family: "PingFang SC";
  font-size: 14px;
  font-weight: 400;
  line-height: normal;
}

.channel-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
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
  justify-content: flex-end;
  align-items: center;
  opacity: 0.4;
  align-self: flex-end;  /* 添加右对齐 */
  margin-top: auto;      /* 添加自动边距使其置底 */
}

.channel-icon svg {
  width: 20px;
  height: 20px;
}
</style>