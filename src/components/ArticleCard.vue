<template>
  <router-link 
    :to="{ name: 'article', params: { id: props.article.id }}"
    class="block bg-white rounded-lg overflow-hidden shadow hover:shadow-lg transition duration-300"
  >
    <div class="aspect-w-16 aspect-h-9 overflow-hidden">
      <img 
        :src="props.article.coverImage" 
        :alt="props.article.title"
        class="w-full h-full object-cover"
      />
    </div>
    <div class="p-6">
      <h3 class="text-xl font-semibold mb-3 text-gray-900 line-clamp-2">{{ props.article.title }}</h3>
      <p class="text-gray-600 mb-4 text-sm line-clamp-2">{{ props.article.summary }}</p>
      
      <div class="flex items-center justify-between pt-4 border-t border-gray-100">
        <div class="flex items-center gap-2">
          <img 
            :src="props.article.author.avatar" 
            :alt="props.article.author.name"
            class="w-8 h-8 rounded-full"
          />
          <span class="text-sm text-gray-700">{{ props.article.author.name }}</span>
        </div>
        <span class="text-sm text-gray-500">{{ props.article.publishDate }}</span>
      </div>
    </div>
  </router-link>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
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
</script>
