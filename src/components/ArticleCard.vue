<template>
  <router-link 
    :to="{ name: 'article', params: { id: props.article.id }}"
    class="block bg-white rounded-2xl overflow-hidden shadow hover:shadow-lg transition duration-300 p-4"
  >
    <div class="flex gap-4 h-[120px]">
      <!-- 左侧内容 -->
      <div class="flex-1">
        <h3 class="text-xl font-semibold text-gray-900 line-clamp-3">
          {{ props.article.title }}
        </h3>
      </div>
      
      <!-- 右侧图片 -->
      <div class="w-[120px] h-[120px] flex-shrink-0">
        <img 
          :src="props.article.coverImage" 
          :alt="props.article.title"
          class="w-full h-full object-cover rounded-lg"
        />
      </div>
    </div>
    
    <!-- 底部信息栏 -->
    <div class="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
      <!-- 左侧：渠道信息 -->
      <div class="flex items-center gap-2">
        <img 
          :src="getChannelIcon(props.article.channel)"
          :alt="props.article.channel"
          class="w-6 h-6"
        />
        <span class="text-sm text-gray-600">{{ props.article.channel }}</span>
      </div>
      
      <!-- 右侧：作者和时间 -->
      <div class="flex items-center gap-4 text-sm text-gray-500">
        <span>{{ props.article.author.name }}</span>
        <span>{{ props.article.publishDate }}</span>
      </div>
    </div>
  </router-link>
</template>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

<script setup lang="ts">
import type { Article } from '../types/article'
import { defineProps } from 'vue'

interface Props {
  article: Article
}

const props = defineProps<Props>()

// 根据渠道返回对应的图标路径
const getChannelIcon = (channel: string): string => {
  const icons: Record<string, string> = {
    '微信': '/images/icons/wechat.svg',
    'YouTube': '/images/icons/youtube.svg',
    '小宇宙': '/images/icons/xiaoyuzhou.svg',
    'PDF': '/images/icons/pdf.svg',
    '视频': '/images/icons/video.svg'
  }
  return icons[channel] || '/images/icons/default.svg'
}
</script>
