<template>
  <div 
    class="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
    @click="navigateToDetail(article.id)"
  >
    <div class="p-4 flex gap-4">
      <div class="flex-1">
        <h3 class="text-lg font-medium text-gray-900 mb-2">{{ article.title }}</h3>
      </div>
      <img src="/public/images/covers/article-1.png" alt="Article cover" class="w-24 h-24 object-cover rounded" />
    </div>
    <div class="px-4 py-3 bg-gray-50 flex justify-between items-center text-sm text-gray-600">
      <div class="flex items-center gap-2">
        <img :src="getChannelIcon(article.channel)" :alt="article.channel" class="w-4 h-4" />
        <span>{{ article.channel }}</span>
      </div>
      <div class="flex items-center gap-2">
        <span>{{ article.author_name }}</span>
        <span>{{ formatDate(article.created_at) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { format } from 'date-fns'
import { useRouter } from 'vue-router'

const router = useRouter()

interface Props {
  article: {
    id: number
    title: string
    channel: string
    author_name: string
    created_at: string
  }
}

defineProps<Props>()

const formatDate = (date: string | null) => {
  if (!date) return ''
  try {
    return format(new Date(date), 'yyyy-MM-dd')
  } catch (error) {
    console.error('日期格式化错误:', error)
    return ''
  }
}

const getChannelIcon = (channel: string): string => {
  const iconMap: Record<string, string> = {
    '微信': '/images/icons/wechat.svg',
    'YouTube': '/images/icons/youtube.svg',
    '小宇宙': '/images/icons/xiaoyuzhou.svg',
    'PDF': '/images/icons/pdf.svg',
    '视频': '/images/icons/video.svg'
  }
  return iconMap[channel] || '/images/icons/default.svg'
}

const navigateToDetail = (id: number) => {
  router.push(`/article/${id}`)
}
</script>
