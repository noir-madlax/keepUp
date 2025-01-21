<template>
  <router-link 
    :to="`/article/${article.id}`"
    class="card-container"
    custom
    v-slot="{ navigate }"
  >
    <div 
      class="card-container"
      @click="handleClick($event, navigate)"
    >
      <!-- 上半部分 -->
      <div class="card-top">
        <!-- 左侧标题 -->
        <h3 class="article-title">{{ getTitle() }}</h3>
        
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
</template>

<script setup lang="ts">
import { format } from 'date-fns'
import { useRouter } from 'vue-router'
import type { Article } from '../types/article'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { t } = useI18n()

interface Props {
  article: Article
}

const props = defineProps<Props>()

const getArticleImage = () => {
  if (props.article.cover_image_url && 
      props.article.cover_image_url.trim() !== '' && 
      !props.article.cover_image_url.includes('qpic.cn') &&
      props.article.cover_image_url !== '无缩略图') {
    return props.article.cover_image_url;
  }
  return 'images/covers/article_default.png';
}

const formatDate = (date: string | null) => {
  if (!date) return t('upload.card.fallback.unknownDate')
  try {
    return format(new Date(date), 'yyyy-MM-dd')
  } catch (error) {
    console.error('日期格式化错误:', error)
    return t('upload.card.fallback.unknownDate')
  }
}

const handleClick = (event: MouseEvent, navigate: () => void) => {
  if (event.metaKey || event.ctrlKey) {
    window.open(`/article/${props.article.id}`, '_blank')
  } else {
    navigate()
  }
}

const getChannelIcon = (channel: string): string => {
  const iconMap: Record<string, string> = {
    'YouTube': 'youtube.svg',
    'youtube': 'youtube.svg',
    'Apple Podcast': 'apple-podcast.svg',
    'Spotify': 'spotify.svg',
    'spotify': 'spotify.svg',
    'webpage': 'web.svg'
  }
  return iconMap[channel] || 'channel_default.png'
}

const getAuthorIcon = () => {
  if (props.article.author?.icon) {
    return props.article.author.icon
  }
  return '/images/icons/author_default.svg'
}

const getAuthorName = () => {
  if (!props.article.author?.name || props.article.author.name === t('upload.card.fallback.unknownAuthor') || props.article.author.name === 'Unknown') {
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

.cover-image {
  width: auto;
  height: 120px;
  flex-shrink: 0;
  border-radius: 12px;
  max-width: 120px;
  object-fit: cover;
  object-position: center;
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