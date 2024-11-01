<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <header class="bg-blue-50">
      <div class="px-8 py-4 flex justify-between items-center">
        <div class="flex items-center gap-3">
          <img src="/images/logo.png" alt="Keep Up Logo" class="h-8 w-8" />
          <h1 class="text-2xl font-bold text-gray-900">Keep Up (跟牢)</h1>
        </div>
        <div class="flex items-center gap-4">
          <template v-if="authStore.isAuthenticated">
            <div class="flex items-center gap-2">
              <img 
                :src="authStore.user?.user_metadata?.avatar_url" 
                alt="User Avatar" 
                class="w-8 h-8 rounded-full"
              />
              <span>{{ authStore.user?.user_metadata?.user_name }}</span>
            </div>
            <button 
              @click="handleLogout" 
              class="text-gray-600 hover:text-gray-800"
            >
              退出
            </button>
          </template>
          <template v-else>
            <button 
              @click="showLoginModal = true"
              class="text-gray-600 hover:text-gray-800"
            >
              登录
            </button>
          </template>
          <button 
            @click="handleUpload" 
            class="bg-blue-500 text-white px-4 py-2 rounded"
          >
            上传
          </button>
        </div>
      </div>
    </header>
    
    <!-- 添加登录模态框 -->
    <login-modal 
      v-if="showLoginModal" 
      @close="showLoginModal = false"
    />

    <!-- 主要内容 -->
    <div class="px-8 py-6">
      <div class="max-w-screen-2xl mx-auto">
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

        <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          <article-card
            v-for="article in filteredArticles"
            :key="article.id"
            :article="article"
          />
        </div>
      </div>
    </div>

    <!-- 上传弹框 -->
    <div 
      v-if="showUploadModal" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showUploadModal = false"
    >
      <div 
        class="bg-white p-6 rounded-lg shadow-lg w-[600px] max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold">上传文章</h2>
          <button @click="showUploadModal = false" class="text-gray-500">
            <i class="el-icon-close"></i>
          </button>
        </div>

        <article-form v-model="articleForm" />

        <div class="mt-6 flex justify-end space-x-3">
          <button 
            @click="showUploadModal = false" 
            class="px-4 py-2 border rounded-md hover:bg-gray-50"
          >
            取消
          </button>
          <button 
            @click="submitArticle" 
            class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            提交
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import ArticleCard from '../components/ArticleCard.vue'
import { supabase } from '../supabaseClient'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import LoginModal from '../components/LoginModal.vue'
import type { Article } from '../types/article'
import AuthorSelect from '../components/AuthorSelect.vue'
import ArticleForm from '../components/ArticleForm.vue'

const authStore = useAuthStore()
const showLoginModal = ref(false)
const showUploadModal = ref(false)

// 预定义的标签
const PREDEFINED_TAGS = ['24小时', '博客', '论文', '微信', '视频']

const articles = ref<Article[]>([])
const selectedTag = ref('all')

// 使用预定义的标签替代动态计算的标签
const tags = computed(() => PREDEFINED_TAGS)

// 修改文章获取函数
const fetchArticles = async () => {
  try {
    const { data, error } = await supabase
      .from('keep_articles')
      .select(`
        id,
        title,
        channel,
        created_at,
        tags,
        author_id,
        author:keep_authors(id, name, icon)
      `)
      .order('created_at', { ascending: false })

    if (error) {
      console.error('获取文章列表失败:', error)
      ElMessage.error('获取文章列表失败')
      return
    }

    articles.value = data
  } catch (error) {
    console.error('获取文章列表时出错:', error)
    ElMessage.error('系统错误，请稍后重试')
  }
}

// 修改筛选逻辑以适应新的数据结构
const filteredArticles = computed(() => {
  if (selectedTag.value === 'all') return articles.value
  return articles.value.filter(article => 
    article.tags && article.tags.includes(selectedTag.value)
  )
})

// 页面加载时获文章列表
onMounted(() => {
  fetchArticles()
  authStore.loadUser()
})

const articleForm = ref<Partial<Article>>({
  title: '',
  content: '',
  author_id: undefined,
  tags: [],
  channel: '',
  publish_date: null,
  original_link: null
})

const selectTag = (tag: string): void => {
  selectedTag.value = tag
}

const handleUpload = () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    showLoginModal.value = true
    return
  }
  showUploadModal.value = true
}

const handleLogout = async () => {
  try {
    await authStore.signOut()
    ElMessage.success('已退出登录')
  } catch (error) {
    console.error('Logout error:', error)
    ElMessage.error('退出失败，请重试')
  }
}

const resetForm = () => {
  articleForm.value = {
    title: '',
    content: '',
    author_id: undefined,
    tags: [],
    channel: '',
    publish_date: null,
    original_link: null
  }
}

const submitArticle = async () => {
  try {
    if (!authStore.isAuthenticated) {
      ElMessage.warning('请先登录')
      showLoginModal.value = true
      return
    }

    if (!articleForm.value.title || !articleForm.value.content || !articleForm.value.author_id) {
      ElMessage.error('标题、内容和作者为必填项')
      return
    }
    
    // 创建一个普通对象，只包含需要的字段
    const submitData = {
      title: articleForm.value.title,
      content: articleForm.value.content,
      author_id: articleForm.value.author_id,
      tags: articleForm.value.tags || [],
      channel: articleForm.value.channel || '',
      publish_date: articleForm.value.publish_date,
      original_link: articleForm.value.original_link,
      user_id: authStore.user?.id
    }

    const { data, error } = await supabase
      .from('keep_articles')
      .insert([submitData])
      .select()
      .single()

    if (error) {
      console.error('添加文章失败:', error)
      ElMessage.error('添加失败：' + error.message)
      return
    }

    ElMessage.success('文章添加成功')
    showUploadModal.value = false
    resetForm()
    await fetchArticles()
  } catch (error) {
    console.error('提交文章时出错:', error)
    ElMessage.error('系统错误，请稍后重试')
  }
}
</script>

<style scoped>
/* 添加滚动条样式 */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: #CBD5E0 #EDF2F7;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #EDF2F7;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: #CBD5E0;
  border-radius: 4px;
}
</style>
