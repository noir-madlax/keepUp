<template>
  <router-link 
    :to="{ name: 'article', params: { id: props.article.id }}"
    class="block bg-white rounded-lg overflow-hidden shadow-md hover:shadow-lg transition"
  >
    <img 
      :src="props.article.coverImage" 
      :alt="props.article.title"
      class="w-full h-48 object-cover"
    />
    <div class="p-4">
      <h3 class="text-xl font-semibold mb-2">{{ props.article.title }}</h3>
      <p class="text-gray-600 mb-4">{{ props.article.summary }}</p>
      
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <img 
            :src="props.article.author.avatar" 
            :alt="props.article.author.name"
            class="w-6 h-6 rounded-full"
          />
          <span class="text-sm text-gray-600">{{ props.article.author.name }}</span>
        </div>
        <span class="text-sm text-gray-600">{{ props.article.publishDate }}</span>
      </div>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import type { Article } from '../types/article'
import { defineProps } from 'vue'

interface Props {
  article: Article
}

const props = defineProps<Props>()
</script>
