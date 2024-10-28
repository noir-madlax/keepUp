<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <header class="bg-blue-50">
      <div class="px-8 py-4">
        <div class="flex items-center gap-3">
          <router-link to="/" class="flex items-center gap-3">
            <img src="/images/logo.png" alt="Keep Up Logo" class="h-8 w-8" />
            <h1 class="text-2xl font-bold text-gray-900">Keep Up (跟牢)</h1>
          </router-link>
        </div>
      </div>
    </header>

    <!-- 文章信息 banner -->
    <div class="bg-blue-50 pb-8">
      <div class="px-8">
        <div class="max-w-screen-2xl mx-auto">
          <div class="flex gap-8">
            <!-- 左侧图片 -->
            <div class="w-[200px] h-[200px] flex-shrink-0">
              <img 
                :src="article?.coverImage" 
                :alt="article?.title"
                class="w-full h-full object-cover rounded-lg"
              />
            </div>
            
            <!-- 右侧内容 -->
            <div class="flex-1 pt-4">
              <h1 class="text-3xl font-bold text-gray-900 mb-4">{{ article?.title }}</h1>
              <div class="flex items-center gap-4 text-gray-600">
                <span class="text-sm">作者</span>
                <span class="text-sm">{{ article?.publishDate }}</span>
              </div>
              <a 
                v-if="article?.originalLink"
                :href="article.originalLink" 
                target="_blank"
                class="inline-flex items-center text-blue-500 hover:text-blue-600 mt-4"
              >
                <span>查看原文内容</span>
                <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="px-8 py-8">
      <div class="max-w-screen-2xl mx-auto">
        <!-- 文章内容 -->
        <article class="prose prose-lg max-w-none bg-white rounded-2xl p-8 shadow-sm">
          <component 
            :is="VueMarkdownRender" 
            :source="article?.content || ''" 
          />
        </article>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import type { Article } from '../types/article'
import { articles } from '../data/articles'
import VueMarkdownRender from 'vue-markdown-render'

const route = useRoute()
const article = ref<Article | undefined>(undefined)

onMounted((): void => {
  const id = route.params.id as string
  article.value = articles.find((a: Article) => a.id === id)
  
  if (!article.value) {
    console.error('Article not found')
  }
})
</script>

<style scoped>
.prose {
  @apply text-gray-800;
}

.prose h1,
.prose h2,
.prose h3 {
  @apply text-gray-900;
}
</style>
