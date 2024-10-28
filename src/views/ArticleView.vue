<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <header class="bg-blue-50 border-b border-blue-100">
      <div class="container mx-auto px-4 py-4">
        <div class="flex items-center gap-3">
          <router-link to="/" class="flex items-center gap-3">
            <img src="/images/logo.png" alt="Keep Up Logo" class="h-8 w-8" />
            <h1 class="text-2xl font-bold text-gray-900">Keep Up (跟上)</h1>
          </router-link>
        </div>
      </div>
    </header>

    <!-- 主要内容 -->
    <div class="container mx-auto px-4 py-8">
      <div class="max-w-4xl mx-auto">
        <!-- 文章头部 -->
        <header class="mb-8">
          <div class="relative h-[400px] mb-8">
            <img 
              :src="article?.coverImage" 
              :alt="article?.title"
              class="w-full h-full object-cover rounded-lg"
            />
          </div>
          
          <h1 class="text-4xl font-bold mb-4">{{ article?.title }}</h1>
          
          <div class="flex items-center justify-between">
            <!-- 作者信息 -->
            <div class="flex items-center gap-3">
              <img 
                :src="article?.author.avatar" 
                :alt="article?.author.name"
                class="w-10 h-10 rounded-full"
              />
              <div>
                <div class="font-medium">{{ article?.author.name }}</div>
                <div class="text-sm text-gray-500">作者</div>
              </div>
            </div>
            
            <!-- 发布日期 -->
            <div class="text-gray-500">
              发布于 {{ article?.publishDate }}
            </div>
          </div>

          <!-- 标签 -->
          <div class="flex gap-2 mt-4">
            <span 
              v-for="tag in article?.tags" 
              :key="tag"
              class="px-3 py-1 bg-gray-100 rounded-full text-sm"
            >
              {{ tag }}
            </span>
          </div>
        </header>

        <!-- 文章内容 -->
        <article class="prose prose-lg max-w-none">
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
