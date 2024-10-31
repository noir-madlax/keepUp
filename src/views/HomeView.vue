<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <header class="bg-blue-50">
      <div class="px-8 py-4 flex justify-between items-center">
        <div class="flex items-center gap-3">
          <img src="/images/logo.png" alt="Keep Up Logo" class="h-8 w-8" />
          <h1 class="text-2xl font-bold text-gray-900">Keep Up (跟牢)</h1>
        </div>
        <button @click="showUploadModal = true" class="bg-blue-500 text-white px-4 py-2 rounded">
          上传
        </button>
      </div>
    </header>
    
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

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">标题 *</label>
            <input 
              v-model="articleForm.title" 
              class="w-full border rounded-md px-3 py-2" 
              placeholder="请输入文章标题"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">作者</label>
            <input 
              v-model="articleForm.author_name" 
              class="w-full border rounded-md px-3 py-2" 
              placeholder="请输入作者名称"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">内容 *</label>
            <textarea 
              v-model="articleForm.content" 
              rows="6" 
              class="w-full border rounded-md px-3 py-2" 
              placeholder="请输入文章内容"
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">标签</label>
            <div class="space-x-4">
              <label v-for="tag in ['24小时', '博客', '论文', '微信', '视频']" :key="tag" class="inline-flex items-center">
                <input 
                  type="checkbox" 
                  :value="tag" 
                  v-model="articleForm.tags" 
                  class="rounded border-gray-300"
                />
                <span class="ml-2">{{ tag }}</span>
              </label>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">频道</label>
            <div class="space-x-4">
              <label v-for="channel in ['微信', 'YouTube', '小宇宙', 'PDF','视频']" :key="channel" class="inline-flex items-center">
                <input 
                  type="radio" 
                  :value="channel" 
                  v-model="articleForm.channel" 
                  class="border-gray-300"
                />
                <span class="ml-2">{{ channel }}</span>
              </label>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">发布日期</label>
            <input 
              type="datetime-local" 
              v-model="articleForm.publish_date" 
              class="w-full border rounded-md px-3 py-2"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">原文链接</label>
            <input 
              v-model="articleForm.original_link" 
              class="w-full border rounded-md px-3 py-2" 
              placeholder="请输入原文链接"
            />
          </div>
        </div>

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

// 预定义的标签
const PREDEFINED_TAGS = ['24小时', '博客', '论文', '微信', '视频']

interface Article {
  id: number
  title: string
  author_name: string
  channel: string
  created_at: string
  tags: string[]
}

const articles = ref<Article[]>([])
const selectedTag = ref('all')
const showUploadModal = ref(false)

// 使用预定义的标签替代动态计算的标签
const tags = computed(() => PREDEFINED_TAGS)

// 修改文章获取函数，不获取 content 字段
const fetchArticles = async () => {
  try {
    const { data, error } = await supabase
      .from('keep_articles')
      .select('id, title, author_name, channel, created_at, tags')
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

// 页面加载时获取文章列表
onMounted(() => {
  fetchArticles()
})

const articleForm = reactive({
  title: '',
  author_name: '',
  author_avatar: '',
  content: '',
  tags: [],
  channel: '',
  publish_date: null,
  original_link: ''
})

const selectTag = (tag: string): void => {
  selectedTag.value = tag
}

const submitArticle = async () => {
  try {
    if (!articleForm.title || !articleForm.content) {
      ElMessage.error('标题和内容为必填项')
      return
    }
    
    const { data, error } = await supabase
      .from('keep_articles')
      .insert([articleForm])

    if (error) {
      console.error('添加文章失败:', error)
      ElMessage.error('添加失败：' + error.message)
      return
    }

    ElMessage.success('文章添加成功')
    showUploadModal.value = false
    // 重置表单
    Object.assign(articleForm, {
      title: '',
      author_name: '',
      author_avatar: '',
      content: '',
      tags: [],
      channel: '',
      publish_date: null,
      original_link: ''
    })
    // 刷新文章列表
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
