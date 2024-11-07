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
        <img :src="`/images/icons/${getChannelIcon(article.channel)}`" :alt="article.channel" class="w-4 h-4" />
        <span>{{ article.channel }}</span>
      </div>
      <div class="flex items-center gap-2">
        <img 
          v-if="article.author?.icon" 
          :src="article.author.icon" 
          :alt="article.author.name" 
          class="w-4 h-4 rounded-full"
        />
        <span>{{ article.author?.name }}</span>
        <span>{{ formatDate(article.publish_date) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { format } from 'date-fns'
import { useRouter } from 'vue-router'
import type { Article } from '../types/article'
import { getChannelIcon } from '../utils/channel'

const router = useRouter()

interface Props {
  article: Article
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

const navigateToDetail = (id: number) => {
  router.push(`/article/${id}`)
}
</script>
