<template>
  <!-- 页面容器 -->
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <header class="bg-blue-50">
      <!-- 导航栏内容 -->
      <div class="px-8 py-4 flex justify-between items-center">
        <!-- 网站Logo和标题 -->
        <div class="flex items-center gap-3" @click="router.push('/')" style="cursor: pointer">
          <img src="/images/logo.png" alt="Keep Up Logo" class="h-8 w-8" />
          <h1 class="text-2xl font-bold text-gray-900">Keep Up</h1>
        </div>
        <!-- 编辑按钮 -->
        <button 
          v-if="canEdit"
          @click="showEditModal = true"
          class="bg-blue-500 text-white px-4 py-2 rounded"
        >
          编辑文章
        </button>
      </div>
    </header>

    <template v-if="article">
      <!-- 文章标题和作者信息 -->
      <div class="bg-blue-50">
        <div class="max-w-4xl mx-auto">
          <div class="relative px-4 py-8">
            <div class="flex flex-col md:flex-row gap-8 items-start md:items-center">
              <!-- 文章封面 -->
              <img 
                src="/public/images/covers/article-1.png" 
                alt="Article Banner" 
                class="w-full md:w-64 h-48 md:h-64 object-cover rounded-lg shadow-md" 
              />
              <div class="flex-1">
                <!-- 文章标题 --> 
                <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-4">{{ article.title }}</h1>
                <!-- 作者信息 -->
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
                <!-- 原文链接 -->
                <a 
                  v-if="article.original_link"
                  :href="article.original_link" 
                  target="_blank" 
                  class="inline-block mt-4 text-blue-500 hover:text-blue-600"
                >
                  {{ t('article.viewOriginal') }} →
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 小节标签 -->
      <div class="max-w-4xl mx-auto px-4 mt-6">
        <!-- 小节标签 -->
        <div class="flex flex-wrap gap-3 pb-4 border-b border-gray-200">
          <button
            v-for="sectionType in ALL_SECTION_TYPES"
            :key="sectionType"
            @click="toggleSection(sectionType)"
            class="px-4 py-1.5 text-sm rounded-[2px] border transition-colors duration-200"
            :class="selectedSections.includes(sectionType) ? 
              'bg-blue-50 border-blue-400 text-blue-400' : 
              'bg-gray-50 border-gray-300 text-gray-300 hover:border-gray-400 hover:text-gray-400'"
          >
            {{ getLocalizedSectionType(sectionType) }}
          </button>
        </div>

        <!-- 文章内容部分 -->
        <div class="mt-6">
          <div class="bg-white rounded-lg shadow-sm p-4 md:p-8">
            <article class="prose prose-sm md:prose-lg max-w-none">
              <template v-if="sections.length">
                <div 
                  v-for="section in displaySections" 
                  :key="section.id"
                  class="mb-8"
                >
                  <h2 class="text-xl font-bold mb-4">{{ getLocalizedSectionType(section.section_type) }}</h2>
                  <div v-html="marked(section.content)"></div>
                </div>
              </template>
              <div v-else>
                <div v-html="markdownContent"></div>
              </div>
            </article>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="text-center py-8">
      <p>加载中...</p>
    </div>

    <!-- 编辑模态框 -->
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

        <article-form 
          v-if="article" 
          v-model="editForm" 
          :articleId="article.id"
          ref="formRef"
        />

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
import type { ArticleSection, SectionType, ViewType } from '../types/section'
import { ALL_SECTION_TYPES, DEFAULT_SELECTED_SECTIONS, getLocalizedSectionType } from '../types/section'
import { useI18n } from 'vue-i18n'

// 将 i18n 相关初始化移到最前面
const { t, locale } = useI18n()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const article = ref<Article | null>(null)
const sections = ref<ArticleSection[]>([])
const showEditModal = ref(false)
const editForm = ref<Partial<Article>>({})

// 小节管理
const selectedSections = ref<SectionType[]>(DEFAULT_SELECTED_SECTIONS)

// 根据当前视角获取可用的小节类型
const availableSectionTypes = computed(() => {
  // 始终返回所��小节类型
  return ALL_SECTION_TYPES
})

// 根据选中的小节筛选显示内容
const displaySections = computed(() => {
  return sections.value
    .filter(section => selectedSections.value.includes(section.section_type))
    .sort((a, b) => a.sort_order - b.sort_order)
})

// 切换小节显示状态
const toggleSection = (sectionType: SectionType) => {
  const index = selectedSections.value.indexOf(sectionType)
  if (index === -1) {
    selectedSections.value.push(sectionType)
  } else {
    selectedSections.value.splice(index, 1)
  }
}

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
  return authStore.isAuthenticated && 
         article.value?.user_id === authStore.user?.id
})

// 获取文章和小节内容
const fetchArticle = async () => {
  try {
    // 获取文章基本信息
    const { data: articleData, error: articleError } = await supabase
      .from('keep_articles')
      .select(`
        *,
        user_id,
        author:keep_authors(id, name, icon)
      `)
      .eq('id', route.params.id)
      .single()

    if (articleError) throw articleError

    // 获取当前语言的文章小节内容
    let { data: sectionsData, error: sectionsError } = await supabase
      .from('keep_article_sections')
      .select('*')
      .eq('article_id', route.params.id)
      .eq('language', locale.value)
      .order('sort_order')

    if (sectionsError) throw sectionsError

    // 如果当前语言没有内容,尝试获取另一种语言的内容
    if (!sectionsData?.length) {
      const fallbackLanguage = locale.value === 'zh' ? 'en' : 'zh'
      const { data: fallbackData, error: fallbackError } = await supabase
        .from('keep_article_sections')
        .select('*')
        .eq('article_id', route.params.id)
        .eq('language', fallbackLanguage)
        .order('sort_order')

      if (!fallbackError && fallbackData?.length) {
        sectionsData = fallbackData
        // 使用翻译的提示信息
        ElMessage.info(t('article.fallbackLanguage.message', {
          language: t(`article.fallbackLanguage.${fallbackLanguage}`)
        }))
      }
    }

    article.value = articleData
    sections.value = sectionsData || []
  } catch (error) {
    console.error('获取文章详情失败:', error)
    ElMessage.error('获取文章失败')
  }
}

// 添加表单引用
const formRef = ref<InstanceType<typeof ArticleForm> | null>(null)

const submitEdit = async () => {
  try {
    if (!editForm.value.title || !editForm.value.content || !editForm.value.author_id) {
      ElMessage.error('标题、内容和作者为必填项')
      return
    }

    // 更新文章基本信息
    const updateData = {
      title: editForm.value.title,
      content: editForm.value.content,
      author_id: editForm.value.author_id,
      tags: editForm.value.tags || [],
      channel: editForm.value.channel,
      publish_date: editForm.value.publish_date ? 
        new Date(editForm.value.publish_date).toISOString() : null,
      original_link: editForm.value.original_link
    }

    const { error: articleError } = await supabase
      .from('keep_articles')
      .update(updateData)
      .eq('id', article.value?.id)

    if (articleError) throw articleError

    if (formRef.value) {
      // 删除当前语言的小节
      const { error: deleteError } = await supabase
        .from('keep_article_sections')
        .delete()
        .eq('article_id', article.value?.id)
        .eq('language', locale.value)  // 只删除当前语言的内容

      if (deleteError) throw deleteError

      // 添加新的小节
      const sectionsData = formRef.value.getSectionsData()
      if (sectionsData.length > 0) {
        const { error: insertError } = await supabase
          .from('keep_article_sections')
          .insert(sectionsData.map(section => ({
            ...section,
            article_id: article.value?.id,
            language: locale.value  // 添加语言标识
          })))

        if (insertError) throw insertError
      }
    }

    ElMessage.success('更新成功')
    showEditModal.value = false
    await fetchArticle()
  } catch (error) {
    console.error('更新文章失败:', error)
    ElMessage.error('更新失败，请重试')
  }
}

// 监听语言变化,重新获取内容
watch(() => locale.value, () => {
  if (route.params.id) {
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
