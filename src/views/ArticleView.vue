<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-blue-50">
      <div class="px-8 py-4 flex justify-between items-center">
        <div class="flex items-center gap-3" @click="router.push('/')" style="cursor: pointer">
          <img src="/images/logo.png" alt="Keep Up Logo" class="h-8 w-8" />
          <h1 class="text-2xl font-bold text-gray-900">Keep Up (跟牢)</h1>
        </div>
        <button 
              v-if="canEdit"
              @click="showEditModal = true"
                class="absolute top-4 right-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
          编辑文章
        </button>
      </div>
    </header>

    <template v-if="article">
      <div>
        <div class="max-w-4xl mx-auto">
          <div class="relative px-4 py-8">
           

            <div class="flex flex-col md:flex-row gap-8 items-start md:items-center">
              <img 
                src="/public/images/covers/article-1.png" 
                alt="Article Banner" 
                class="w-full md:w-64 h-48 md:h-64 object-cover rounded-lg shadow-md" 
              />
              <div class="flex-1">
                <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-4">{{ article.title }}</h1>
                <div class="flex items-center gap-4 text-gray-600 text-sm md:text-base">
                  <div class="flex items-center gap-2">
                    <img 
                      v-if="article.author?.icon" 
                      :src="article.author.icon" 
                      :alt="article.author.name" 
                      class="w-5 h-5 rounded-full"
                    />
                    <span>{{ article.author?.name }}</span>
                  </div>
                  <span>{{ formatDate(article.publish_date) }}</span>
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
      </div>

      <div class="max-w-4xl mx-auto px-4 py-8">
        <div class="bg-white rounded-lg shadow-sm p-4 md:p-8">
          <article class="prose prose-sm md:prose-lg max-w-none">
            <div v-html="markdownContent"></div>
          </article>
        </div>
      </div>
    </template>

    <div v-else class="text-center py-8">
      <p>加载中...</p>
    </div>

    <div 
      v-if="showEditModal" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showEditModal = false"
    >
      <div 
        class="bg-white p-6 rounded-lg shadow-lg w-[600px] max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold">编辑文章</h2>
          <button @click="showEditModal = false" class="text-gray-500">
            <i class="el-icon-close"></i>
          </button>
        </div>

        <article-form v-if="article" v-model="editForm" />

        <div class="mt-6 flex justify-end space-x-3">
          <button 
            @click="showEditModal = false" 
            class="px-4 py-2 border rounded-md hover:bg-gray-50"
          >
            取消
          </button>
          <button 
            @click="submitEdit" 
            class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            保存
          </button>
        </div>
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
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import ArticleForm from '../components/ArticleForm.vue'
import type { Article } from '../types/article'

  const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const article = ref<Article | null>(null)
const showEditModal = ref(false)
const editForm = ref<Partial<Article>>({})

const markdownContent = computed(() => {
  return article.value?.content ? marked(article.value.content) : ''
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

const canEdit = computed(() => {
  const isAuth = authStore.isAuthenticated
  const userId = authStore.user?.id
  const articleUserId = article.value?.user_id
  
  console.log('Auth status:', {
    isAuthenticated: isAuth,
    userId: userId,
    articleUserId: articleUserId
  })
  
  return isAuth && userId === articleUserId
})

const fetchArticle = async () => {
  try {
    const { data, error } = await supabase
      .from('keep_articles')
      .select(`
        *,
        user_id,
        author:keep_authors(id, name, icon)
      `)
      .eq('id', route.params.id)
      .single()

    if (error) {
      ElMessage.error('获取文章失败')
      return
    }

    const formattedData = {
      ...data,
      publish_date: data.publish_date ? new Date(data.publish_date).toISOString().split('T')[0] : null
    }

    article.value = formattedData as Article
    editForm.value = { ...formattedData }
  } catch (error) {
    console.error('获取文章详情失败:', error)
    ElMessage.error('获取文章失败')
  }
}

const submitEdit = async () => {
  try {
    if (!editForm.value.title || !editForm.value.content || !editForm.value.author_id) {
      ElMessage.error('标题、内容和作者为必填项')
      return
    }

    const updateData = {
      title: editForm.value.title,
      content: editForm.value.content,
      author_id: editForm.value.author_id,
      tags: editForm.value.tags || [],
      channel: editForm.value.channel,
      publish_date: editForm.value.publish_date ? new Date(editForm.value.publish_date).toISOString() : null,
      original_link: editForm.value.original_link
    }

    const { error } = await supabase
      .from('keep_articles')
      .update(updateData)
      .eq('id', article.value?.id)

    if (error) throw error

    ElMessage.success('更新成功')
    showEditModal.value = false
    await fetchArticle()
  } catch (error) {
    console.error('更新文章失败:', error)
    ElMessage.error('更新失败，请重试')
  }
}

watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchArticle()
  }
})

onMounted(async () => {
  await authStore.loadUser()
  await fetchArticle()
})
</script>

<style>
.prose img {
  margin: 0 auto;
  max-width: 100%;
  height: auto;
}

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
