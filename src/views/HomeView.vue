<template>
  <!-- 根容器 -->
  <div class="min-h-screen">
    <!-- 顶部导航栏 -->
    <header>
      <!-- 导航栏内容容器 -->
      <div class="px-4 sm:px-8 py-4 flex justify-between items-center">
        <!-- 左侧Logo和标题容器 -->
        <div class="flex items-center gap-0">
          <!-- 网站Logo图片 -->
          <img src="/images/logo.png" alt="Keep Up Logo" class="h-14 w-14 sm:h-14 sm:w-14" />
          <!-- 网站标题文本 -->
          <h1 class="text-[24px] sm:text-[24px] text-[#333333] font-[1000] leading-6 font-['PingFang_SC'] whitespace-nowrap">
            {{ t('home.title') }}
          </h1>
        </div>

        <!-- 右侧导航元素容器 -->
        <div class="flex items-center gap-2 sm:gap-4">
          <!-- 语言切换组件 -->
          <language-switch />
          <!-- 文章请求表单组件 -->
          <article-request-form @refresh="fetchArticles" />
          
          <!-- 已登录用户信息区域 -->
          <template v-if="authStore.isAuthenticated">
            <!-- 用户信息容器 -->
            <div class="flex items-center gap-2">
              <!-- 用户头像图片 -->
              <img 
                :src="authStore.user?.user_metadata?.avatar_url" 
                alt="User Avatar" 
                class="w-8 h-8 rounded-full"
              />
              <!-- 用户名称显示 -->
              <span>{{ authStore.user?.user_metadata?.user_name }}</span>
            </div>
            <!-- 登出按钮 -->
            <button 
              @click="handleLogout" 
              class="text-gray-600 hover:text-gray-800"
            >
              {{ t('home.nav.logout') }}
            </button>
          </template>

          <!-- 未登录状态显示 -->
          <template v-else>
            <!-- 登录按钮 -->
            <button 
              @click="showLoginModal = true"
              class="w-8 h-8 flex items-center justify-center text-gray-600 hover:text-gray-800"
            >
              <img 
                src="/images/icons/user_avatar_unlogin.png" 
                alt="Login"
                class="w-8 h-8 rounded-full"
              />
            </button>
          </template>
        </div>
      </div>
    </header>

    <!-- 登录模态框 -->
    <login-modal 
      v-if="showLoginModal" 
      @close="showLoginModal = false"
    />

    <!-- 主要内容区域 -->
    <div class="px-8 py-6">
      <!-- 内容最大宽度限制容器 -->
      <div class="max-w-screen-2xl mx-auto">
        <!-- 发现区域 -->
        <div class="mb-8">
          <!-- 发现标题 -->
          <h2 class="text-xl mb-4">{{ t('home.filter.discover') }}</h2>
          <!-- 标签按钮容器 -->
          <div class="flex gap-2 flex-wrap">
            <!-- 全部标签按钮 -->
            <button 
              class="px-4 py-2 rounded-full border transition-colors duration-200"
              :class="selectedTag === 'all' ? 'bg-blue-500 text-white' : 'hover:bg-gray-50'"
              @click="selectTag('all')"
            >
              {{ t('home.filter.all') }}
            </button>
          </div>
        </div>

        <!-- 渠道筛选区域 -->
        <div class="mb-8">
          <!-- 渠道标题 -->
          <h2 class="text-sm text-gray-600 mb-2">{{ t('home.filter.channelTitle') }}</h2>
          <!-- 渠道按钮容器 -->
          <div class="flex flex-wrap gap-2">
            <!-- 渠道选择按钮 -->
            <button 
              v-for="channel in ['微信', 'YouTube', '小宇宙', 'PDF', '网页']"
              :key="channel"
              @click="toggleChannel(channel)"
              class="px-3 py-1.5 text-sm rounded-[2px] border transition-colors duration-200 flex items-center gap-2"
              :class="selectedChannels.includes(channel) ? 
                'bg-blue-50 border-blue-400 text-blue-400' : 
                'bg-gray-50 border-gray-300 text-gray-300 hover:border-gray-400 hover:text-gray-400'"
            >
              <!-- 渠道图标 -->
              <img 
                :src="`/images/icons/${getChannelIcon(channel)}`" 
                :alt="channel"
                class="w-4 h-4"
              />
              <!-- 渠道名称 -->
              {{ t(`home.channels.${getChannelKey(channel)}`) }}
            </button>
          </div>
        </div>

        <div class="mb-8">
          <h2 class="text-sm text-gray-600 mb-2">{{ t('home.filter.authorTitle') }}</h2>
          <div class="flex flex-wrap gap-3">
            <!-- 始终显示的作者 -->
            <template v-for="(author, index) in displayedAuthors" :key="author.id">
              <button
                @click="toggleAuthor(author)"
                class="flex items-center gap-2 px-3 py-1.5 text-sm rounded-[2px] border transition-colors duration-200"
                :class="selectedAuthors.includes(author.id) ? 
                  'bg-blue-50 border-blue-400 text-blue-400' : 
                  'bg-gray-50 border-gray-300 text-gray-300 hover:border-gray-400 hover:text-gray-400'"
              >
                <img 
                  v-if="author.icon" 
                  :src="author.icon" 
                  :alt="author.name"
                  class="w-5 h-5 rounded-full"
                />
                {{ author.name }}
              </button>
            </template>

            <!-- 展开/收起按钮 -->
            <button 
              v-if="authors.length > defaultDisplayCount"
              @click="isExpanded = !isExpanded"
              class="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700"
            >
              <span>{{ isExpanded ? t('home.filter.collapse') : t('home.filter.expand') }}</span>
              <svg 
                class="w-4 h-4 transition-transform duration-200"
                :class="{ 'transform rotate-180': isExpanded }"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
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

        <article-form 
          v-model="articleForm" 
          ref="formRef"
        />

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
import { ref, computed, reactive, onMounted, onUnmounted } from 'vue'
import ArticleCard from '../components/ArticleCard.vue'
import { supabase } from '../supabaseClient'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import LoginModal from '../components/LoginModal.vue'
import type { Article } from '../types/article'
import AuthorSelect from '../components/AuthorSelect.vue'
import ArticleForm from '../components/ArticleForm.vue'
import { getChannelIcon } from '../utils/channel'
import ArticleRequestForm from '../components/ArticleRequestForm.vue'
import { useI18n } from 'vue-i18n'
import LanguageSwitch from '../components/LanguageSwitch.vue'

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
        publish_date,
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

// 修改筛选逻辑以适应的数据结构
const filteredArticles = computed(() => {
  let result = articles.value

  // 标签筛选
  if (selectedTag.value !== 'all') {
    result = result.filter(article => 
      article.tags && article.tags.includes(selectedTag.value)
    )
  }

  // 渠道筛选
  if (selectedChannels.value.length > 0) {
    result = result.filter(article => 
      article.channel && selectedChannels.value.includes(article.channel)
    )
  }

  // 作者筛选
  if (selectedAuthors.value.length > 0) {
    result = result.filter(article => 
      article.author_id && selectedAuthors.value.includes(article.author_id)
    )
  }

  return result
})

// 页面加载时获文章列表
onMounted(() => {
  fetchArticles()
  fetchAuthors()
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
  if (tag === 'all' && (selectedTag.value !== 'all' || selectedChannels.value.length > 0)) {
    selectedTag.value = 'all'
    selectedChannels.value = []
  }
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

  // 提交成功后清除草稿
  localStorage.removeItem('articleFormDraft')
}

// 在组件顶部定义 formRef
const formRef = ref<InstanceType<typeof ArticleForm> | null>(null)

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

    // 提交文章基本信息
    const { data, error } = await supabase
      .from('keep_articles')
      .insert([submitData])
      .select()
      .single()

    if (error) throw error

    if (formRef.value) {
      // 提交小节内容
      const sectionsData = formRef.value.getSectionsData()
      if (sectionsData.length > 0) {
        const { error: sectionsError } = await supabase
          .from('keep_article_sections')
          .insert(sectionsData.map(section => ({
            ...section,
            article_id: data.id
          })))

        if (sectionsError) throw sectionsError
      }
    }

    ElMessage.success('文章添加成')

    showUploadModal.value = false
    resetForm()
    await fetchArticles()
  } catch (error) {
    console.error('提交文章时出错:', error)
    ElMessage.error('系统错误，请稍后重试')
  }
}

// 添加作者相关的状态
interface Author {
  id: number;
  name: string;
  icon?: string;
}

const authors = ref<Author[]>([])
const selectedChannels = ref<string[]>([])
const selectedAuthors = ref<number[]>([])

// 获取所有作者
const fetchAuthors = async () => {
  try {
    const { data, error } = await supabase
      .from('keep_authors')
      .select('*')
      .order('name')

    if (error) throw error
    authors.value = data
  } catch (error) {
    console.error('获取作者列表失败:', error)
    ElMessage.error('获取作者列表失败')
  }
}

// 切换渠道选择
const toggleChannel = (channel: string) => {
  const index = selectedChannels.value.indexOf(channel)
  if (index === -1) {
    selectedChannels.value.push(channel)
  } else {
    selectedChannels.value.splice(index, 1)
  }
}

// 切换作者选择
const toggleAuthor = (author: Author) => {
  const index = selectedAuthors.value.indexOf(author.id)
  if (index === -1) {
    selectedAuthors.value.push(author.id)
  } else {
    selectedAuthors.value.splice(index, 1)
  }
}

const { t } = useI18n()

// 添加一个辅助函数来获取channel的key
const getChannelKey = (channel: string): string => {
  const keyMap: Record<string, string> = {
    '微信': 'wechat',
    'YouTube': 'youtube',
    '小宇宙': 'xiaoyuzhou',
    'PDF': 'pdf',
    '网页': 'web'
  }
  return keyMap[channel] || channel.toLowerCase()
}

// 使用计算属性来根据屏幕大小返回不同的显示数量
const defaultDisplayCount = computed(() => {
  // 使用 window.innerWidth 获取当前视口宽度
  const width = window.innerWidth
  
  // >= 1280px (xl): 显示16个 (4行)
  if (width >= 1280) return 16
  // >= 1024px (lg): 显示6个 (3行)
  if (width >= 1024) return 6
  // >= 768px (md): 显示4个 (2行)
  if (width >= 768) return 4
  // < 768px: 显示4个 (2行)
  return 4
})

const isExpanded = ref(false)

// 监听窗口大小变化
onMounted(() => {
  const handleResize = () => {
    // 如果当前显示的作者数量大于新的默认显示数量，则收起列表
    if (!isExpanded.value && displayedAuthors.value.length > defaultDisplayCount.value) {
      isExpanded.value = false
    }
  }

  window.addEventListener('resize', handleResize)
  
  // 组件卸载时移除事件监听
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })
})

// 计算要显示的作者列表
const displayedAuthors = computed(() => {
  return isExpanded.value ? authors.value : authors.value.slice(0, defaultDisplayCount.value)
})
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
