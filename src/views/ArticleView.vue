<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-blue-50">
      <div class="px-8 py-4 flex justify-between items-center">
        <div class="flex items-center gap-3" @click="router.push('/')" style="cursor: pointer">
          <img src="/images/logo.png" alt="Keep Up Logo" class="h-8 w-8" />
          <h1 class="text-2xl font-bold text-gray-900">Keep Up (跟牢)</h1>
        </div>
      </div>
    </header>

    <div class="bg-blue-50">
      <div class="container mx-auto px-4 py-8">
        <div class="flex flex-col md:flex-row gap-8 items-start md:items-center">
          <img 
            src="/public/images/covers/article-1.png" 
            alt="Article Banner" 
            class="w-full md:w-64 h-48 md:h-64 object-cover rounded-lg shadow-md" 
          />
          <div class="flex-1">
            <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-4">{{ article.title }}</h1>
            <div class="flex items-center gap-4 text-gray-600 text-sm md:text-base">
              <span>{{ article.author_name }}</span>
              <span>{{ formatDate(article.created_at) }}</span>
            </div>
            <a 
              v-if="article.original_link"
              :href="article.original_link" 
              target="_blank" 
              class="inline-block mt-4 text-blue-500 hover:text-blue-600"
            >
              查看原文内容 →
            </a>
          </div>
        </div>
      </div>
    </div>

    <div class="container mx-auto px-4 py-8">
      <div class="bg-white rounded-lg shadow-sm p-4 md:p-8">
        <article class="prose prose-sm md:prose-lg max-w-none">
          <div v-html="markdownContent"></div>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { format } from 'date-fns'
import { marked } from 'marked'
import { supabase } from '../supabaseClient'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

interface Article {
  id: number
  title: string
  author_name: string
  content: string
  created_at: string
  original_link: string | null
}

const article = ref<Article>({
  id: 0,
  title: '',
  author_name: '',
  content: '',
  created_at: '',
  original_link: null
})

const markdownContent = computed(() => {
  return marked(article.value.content)
})

const formatDate = (date: string | null) => {
  if (!date) return ''
  try {
    return format(new Date(date), 'yyyy-MM-dd')
  } catch (error) {
    console.error('日期格式化错误:', error)
    return ''
  }
}

const fetchArticle = async () => {
  const articleId = route.params.id
  if (!articleId) {
    ElMessage.error('文章ID不存在')
    router.push('/')
    return
  }

  try {
    const { data, error } = await supabase
      .from('keep_articles')
      .select('id, title, author_name, content, created_at, original_link')
      .eq('id', articleId)
      .single()

    if (error) {
      console.error('获取文章详情失败:', error)
      ElMessage.error('获取文章详情失败')
      router.push('/')
      return
    }

    if (!data) {
      ElMessage.error('文章不存在')
      router.push('/')
      return
    }

    article.value = data as Article
  } catch (error) {
    console.error('获取文章详情时出错:', error)
    ElMessage.error('系统错误，请稍后重试')
    router.push('/')
  }
}

// 监听路由参数变化，重新获取文章
watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchArticle()
  }
})

onMounted(() => {
  fetchArticle()
})
</script>

<style>
.prose img {
  margin: 0 auto;
  max-width: 100%;
  height: auto;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .prose {
    font-size: 16px;
    line-height: 1.6;
  }
  
  .prose img {
    margin: 1rem auto;
  }
  
  .prose h1 {
    font-size: 1.5rem;
  }
  
  .prose h2 {
    font-size: 1.25rem;
  }
  
  .prose h3 {
    font-size: 1.125rem;
  }
}
</style>
