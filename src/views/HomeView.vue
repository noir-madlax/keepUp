<template>
  <div class="container mx-auto px-4">
    <header class="py-6">
      <h1 class="text-2xl font-bold">Keep Up (跟上)</h1>
    </header>
    
    <div class="mb-8">
      <h2 class="text-xl mb-4">Discover Articles by Tag</h2>
      <div class="flex gap-2 flex-wrap">
        <button 
          class="px-4 py-2 rounded-full border"
          :class="selectedTag === 'all' ? 'bg-blue-500 text-white' : ''"
          @click="selectTag('all')"
        >
          全部
        </button>
        <button 
          v-for="tag in tags" 
          :key="tag"
          class="px-4 py-2 rounded-full border"
          :class="selectedTag === tag ? 'bg-blue-500 text-white' : ''"
          @click="selectTag(tag)"
        >
          {{ tag }}
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <article-card
        v-for="article in filteredArticles"
        :key="article.id"
        :article="article"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ArticleCard from '../components/ArticleCard.vue'
import type { Article } from '../types/article'
import { articles as articleData } from '../data/articles'

const articles = ref<Article[]>(articleData)
const selectedTag = ref<string>('all')

const tags = computed((): string[] => {
  const allTags = new Set<string>()
  articles.value.forEach((article: Article) => {
    article.tags.forEach((tag: string) => allTags.add(tag))
  })
  return Array.from(allTags)
})

const filteredArticles = computed((): Article[] => {
  if (selectedTag.value === 'all') return articles.value
  return articles.value.filter((article: Article) => 
    article.tags.includes(selectedTag.value)
  )
})

const selectTag = (tag: string): void => {
  selectedTag.value = tag
}
</script>
