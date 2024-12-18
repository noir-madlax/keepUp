<template>
  <div 
    class="card-container"
    @click="navigateToDetail(article.id)"
  >
    <!-- 上半部分 -->
    <div class="card-top">
      <!-- 左侧标题 -->
      <h3 class="article-title">{{ article.title }}</h3>
      
      <!-- 右侧封面 -->
      <img 
        :src="getArticleImage()" 
        :alt="article.title"
        class="cover-image" 
      />
    </div>

    <!-- 分隔线 -->
    <div class="divider"></div>

    <!-- 下半部分 -->
    <div class="card-bottom">
      <!-- 左侧作者信息 -->
      <div class="author-info">
        <div class="author-icon-wrapper">
          <img 
            v-if="article.author?.icon" 
            :src="article.author.icon" 
            :alt="article.author.name" 
            class="author-icon"
          />
        </div>
        <span class="author-name">{{ article.author?.name }}</span>
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
</template>

<script setup lang="ts">
import { format } from 'date-fns'
import { useRouter } from 'vue-router'
import type { Article } from '../types/article'

const router = useRouter()

interface Props {
  article: Article
}

const props = defineProps<Props>()

const getArticleImage = () => {
  if (props.article.cover_image_url) {
    return props.article.cover_image_url;
  }
  return '/images/covers/article-1.png';
}

const formatDate = (date: string | null) => {
  if (!date) return ''
  try {
    return format(new Date(date), 'yyyy-MM-dd')
  } catch (error) {
    console.error('日期格式化错误:', error)
    return ''
  }
}

const navigateToDetail = (id: number) => {
  router.push(`/article/${id}`)
}

const getChannelIcon = (channel: string): string => {
  const iconMap: Record<string, string> = {
    'YouTube': 'youtube.svg',
    'Apple Podcast': 'apple-podcast.svg',
    'Spotify': 'spotify.svg'
  }
  return iconMap[channel] || ''
}
</script>

<style scoped>
.card-container {
  display: flex;
  width: 369px;
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
}

.article-title {
  height: 72px;
  min-width: 200px;
  max-width: 100%;
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

.cover-image {
  width: 100px;
  height: 100px;
  flex-shrink: 0;
  border-radius: 12px;
  object-fit: cover;
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
</style>