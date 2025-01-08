<template>
  <!-- 页面容器 -->
  <div 
    class="min-h-screen bg-white overflow-x-hidden"
    :class="{ 'chat-open': chatStore.isChatOpen }"
  >
    <!-- 顶部导航栏 -->
    <header class="fixed top-0 left-0 right-0 bg-white z-[999] w-full">
      <!-- 使用transition组件包裹两个导航样式 -->
      <transition 
        mode="out-in"
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0 transform -translate-y-2"
        enter-to-class="opacity-100 transform translate-y-0"
        leave-active-class="transition ease-in duration-200"
        leave-from-class="opacity-100 transform translate-y-0"
        leave-to-class="opacity-0 transform translate-y-2"
      >
        <!-- 导航样式A -->
        <div v-if="!showNavB" class="flex justify-between items-center px-4 h-[70px] min-w-[378px] max-w-[1440px] mx-auto relative" style="max-width: min(100%, 1440px);">
          <!-- 导航栏内容容器 - 添加点击事件和cursor-pointer样式 -->
          <div 
            class="flex items-center gap-2 cursor-pointer" 
            @click="router.push('/')"
          >
            <!-- 网站Logo图片 -->
            <img 
              src="/images/icons/logo.svg" 
              alt="Keep Up Logo" 
              class="w-[48px] h-[48px] flex-shrink-0" 
            />
            <!-- 网站标题文本 -->
            <h1 class="text-[20px] text-[#333333] font-[400] leading-6 font-['PingFang_SC']">
              {{ t('home.title') }}
            </h1>
          </div>
          
          
          <!-- 右侧导航元素容器 - 增加右侧padding并调整gap -->
          <div class="flex items-center gap-3 pr-2">
            <!-- 语言切换组件 -->
            <language-switch/>
        
            <!-- 已登录用户信息区域 -->
            <template v-if="authStore.isAuthenticated">
              <!-- 用户头像 -->
              <img 
                :src="authStore.user?.user_metadata?.avatar_url" 
                alt="User Avatar" 
                class="w-[32px] h-[32px] rounded-full"
              />
              <!-- 登出按钮 -->
              <button 
                @click="handleLogout"
                class="text-gray-600 hover:text-gray-800 min-w-[64px] h-[32px] text-center"
              >
                {{ t('home.nav.logout') }}
              </button>
            </template>

            <!-- 未登录状态显示 -->
            <template v-else>
              <button 
                @click="showLoginModal = true"
                class="w-[32px] h-[32px] flex items-center justify-center"
              >
                <img 
                  src="/images/icons/login.svg" 
                  alt="Login"
                  class="w-[32px] h-[32px]"
                />
              </button>
            </template>
          </div>
        </div>
        
        <!-- 导航样式B -->
        <div v-else class="flex justify-between items-center px-4 h-[70px] min-w-[378px] max-w-[1440px] mx-auto" style="max-width: min(100%, 1440px);">
          <div class="flex-1 max-w-4xl mx-auto px-4">
            <div class="w-full h-[40px] flex items-center justify-between">
              <!-- 使用transition-group为section标题添加动画 -->
              <transition-group 
                :name="transitionName"
                class="flex items-center justify-between w-full relative"
                tag="div"
              >
                <!-- 上一节 -->
                <div 
                  v-if="prevSection" 
                  :key="'prev-' + prevSection.section_type"
                  @click="scrollToSection(prevSection.section_type)"
                  class="flex items-center cursor-pointer text-gray-500 hover:text-gray-700 transition-colors duration-200"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                  <span class="text-sm">{{ getLocalizedSectionType(prevSection.section_type) }}</span>
                </div>
                <div v-else :key="'prev-empty'" class="w-20"></div>

                <!-- 当前section名称 -->
                <h2 
                  :key="currentVisibleSection || 'current'"
                  class="text-base md:text-lg text-gray-900 font-medium"
                >
                  {{ currentVisibleSection ? getLocalizedSectionType(currentVisibleSection) : '' }}
                </h2>

                <!-- 下一节 -->
                <div 
                  v-if="nextSection" 
                  :key="'next-' + nextSection.section_type"
                  @click="scrollToSection(nextSection.section_type)"
                  class="flex items-center cursor-pointer text-gray-500 hover:text-gray-700 transition-colors duration-200"
                >
                  <span class="text-sm">{{ getLocalizedSectionType(nextSection.section_type) }}</span>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
                <div v-else :key="'next-empty'" class="w-20"></div>
              </transition-group>
            </div>
          </div>
        </div>
      </transition>
      
      <!-- 分割线 -->
      <div class="h-[1px] bg-[#E5E5E5] w-full"></div>
    </header>

    <template v-if="article">
      <!-- 添加语言提示横幅 -->
      <div 
        v-if="showLanguageAlert"
        class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4 mx-4 md:mx-8"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1 flex items-center">
            <svg class="h-5 w-5 text-blue-400 mr-2 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div class="flex flex-col sm:flex-row sm:items-center gap-2">
              <p class="text-sm text-blue-700">
                {{ t('article.fallbackLanguage.message', {
                  language: t(`article.fallbackLanguage.${contentLanguage}`)
                }) }}
              </p>
              <!-- 添加获取其他语言内容的按钮 -->
              <button 
                @click="handleMoreContent"
                class="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors"
              >
                {{ t('article.fallbackLanguage.getOtherLanguage') }}
              </button>
            </div>
          </div>
          <button 
            @click="showLanguageAlert = false"
            class="text-blue-400 hover:text-blue-600 ml-4 flex-shrink-0"
          >
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- 文章标题和作者信息 -->
      <div class="bg-white">
        <div 
          class="w-full transition-all duration-300 relative" 
          :style="{
            maxWidth: chatStore.isChatOpen 
              ? 'min(100%, calc(100vw - var(--chat-window-width)))' 
              : 'min(100%, 1024px)',
            margin: chatStore.isChatOpen 
              ? '0 var(--chat-window-width) 0 auto'
              : '0 auto'
          }"
        >
          <div class="relative px-4 py-8">
            <div class="flex flex-col md:flex-row gap-8 items-start md:items-center">
              <!-- 文章封面 -->
              <img 
                :src="getArticleImage(article.cover_image_url)"
                :alt="getArticleTitle()" 
                class="w-full md:w-64 h-48 md:h-64 object-cover rounded-lg shadow-md" 
              />
              <div class="flex-1">
                <!-- 文章标题 --> 
                <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-4">{{ getArticleTitle() }}</h1>
                <!-- 作者信息 -->
                <div class="flex items-center gap-4 text-gray-600 text-sm md:text-base">
                  <div class="flex items-center gap-2">
                    <img 
                      :src="article.author?.icon || '/images/icons/author_default.svg'" 
                      :alt="article.author?.name || t('upload.card.fallback.unknownAuthor')" 
                      class="w-5 h-5 rounded-full"
                    />
                    <span>{{ getAuthorName() }}</span>
                  </div>
                  <span>{{ formatDate(article.publish_date) }}</span>
                </div>
                <!-- 操作按钮组 -->
                <div class="flex flex-wrap gap-1.5 sm:gap-2 mt-4">
                  <!-- 更多内容按钮 -->
                  <button 
                    v-if="isMediaArticle"
                    @click="handleMoreContent" 
                    class="inline-flex items-center px-2.5 sm:px-4 py-1.5 text-xs sm:text-sm font-medium text-gray-600 bg-white hover:bg-gray-50 rounded-full transition-colors border border-gray-200 whitespace-nowrap"
                  >
                    <img
                      src="/images/icons/more_content.svg"
                      alt="More Content"
                      class="h-3 w-3 sm:h-3.5 sm:w-3.5 mr-1 sm:mr-1.5"
                    />
                    {{ t('summarize.moreContent') }}
                  </button>

                  <!-- 查看原文按钮 -->
                  <a 
                    v-if="article.original_link"
                    :href="article.original_link" 
                    target="_blank" 
                    class="inline-flex items-center px-2.5 sm:px-4 py-1.5 text-xs sm:text-sm font-medium text-gray-600 bg-white hover:bg-gray-50 rounded-full transition-colors border border-gray-200 whitespace-nowrap"
                  >
                    <img
                      src="/images/icons/view_original.svg"
                      alt="View Original"
                      class="h-3 w-3 sm:h-3.5 sm:w-3.5 mr-1 sm:mr-1.5"
                    />
                    {{ t('article.viewOriginal') }}
                  </a>

                  <!-- 分享按钮 -->
                  <button 
                    @click="copyCurrentUrl" 
                    class="inline-flex items-center px-2.5 sm:px-4 py-1.5 text-xs sm:text-sm font-medium text-gray-600 bg-white hover:bg-gray-50 rounded-full transition-colors border border-gray-200 whitespace-nowrap"
                  >
                    <img
                      src="/images/icons/share.svg"
                      alt="Share"
                      class="h-3 w-3 sm:h-3.5 sm:w-3.5 mr-1 sm:mr-1.5"
                    />
                    {{ t('article.share') }}
                  </button>

                  <!-- Ask AI 按钮 -->
                  <button 
                    @click="handleAskAI"
                    class="inline-flex items-center px-2.5 sm:px-4 py-1.5 text-xs sm:text-sm font-medium text-blue-600 bg-white hover:bg-blue-50 rounded-full transition-colors border border-blue-200 whitespace-nowrap"
                  >
                    <img
                      src="/images/icons/ask_ai.svg"
                      alt="Ask AI"
                      class="h-3 w-3 sm:h-3.5 sm:w-3.5 mr-1 sm:mr-1.5"
                    />
                    Ask AI
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 小节标签 -->
      <div class="w-full mx-auto bg-white">
        <!-- 小节标签 -->
        <div 
          class="w-full mx-auto transition-all duration-300"
          :style="{
            maxWidth: chatStore.isChatOpen 
              ? 'min(100%, calc(100vw - var(--chat-window-width)))' 
              : 'min(100%, 1024px)',
            margin: chatStore.isChatOpen 
              ? '0 var(--chat-window-width) 0 auto'
              : '0 auto'
          }"
        >
          <div class="tags-container">
            <div class="flex flex-wrap gap-3">
              <button
                v-for="sectionType in ALL_SECTION_TYPES"
                :key="sectionType"
                @click="toggleSection(sectionType)"
                class="px-4 py-1.5 text-sm rounded-[2px] border transition-colors duration-200"
                :class="selectedSections.includes(sectionType) ? 
                  'bg-white border-blue-400 text-blue-400' : 
                  'bg-white border-gray-300 text-gray-300 hover:border-gray-400 hover:text-gray-400'"
              >
                {{ getLocalizedSectionType(sectionType) }}
              </button>
            </div>
          </div>

          <!-- 分割线 -->
          <div class="h-[1px] bg-gray-200"></div>

          <!-- 文章内容部分 -->
          <div class="article-main-container">
            <div 
              class="p-4 md:p-8 article-content"
              @mouseup="handleTextSelection"
              @touchend="handleTextSelection"
            >
              <!-- 文章内容 -->
              <article class="prose prose-sm md:prose-lg max-w-none">
                <!-- 如果sections存在，则渲染sections -->
                <template v-if="sections.length">
                  <!-- 遍历sections，渲染每个section -->
                  <div 
                    v-for="section in displaySections" 
                    :key="section.id"
                    class="mb-8"
                    :data-section-type="section.section_type"
                  >
                    <h2 class="text-xl font-bold mb-4">{{ getLocalizedSectionType(section.section_type) }}</h2>
                    
                    <!-- 根据不同的小节类型使用不同的渲染方式 -->
                    <template v-if="section.section_type === '思维导图'">
                      <div class="flex items-center gap-2">
                            <span 
                              @click="handlePreviewMindmap" 
                              class="text-blue-500 hover:text-blue-600 cursor-pointer text-sm flex items-center"
                            >
                              <i class="el-icon-zoom-in mr-1"></i>
                              {{ t('article.preview.enlarge') }}
                            </span>
                          </div>
                        <mind-map 
                          :content="section.content" 
                          @preview="url => previewImageUrl = url"
                        />

                    </template>
                    <template v-else-if="section.section_type === '结构图'">
                      <!-- 结构图组件 --> 
                      <mermaid :content="section.content" />
                    </template>
                    <template v-else>
                      <!-- 使用问题标记包装markdown内容 -->
                      <div class="relative">
                        <div v-html="renderSectionContent(section)"></div>
                        <!-- 添加section级别的问题标记 -->
                        <template v-if="getSectionQuestionCount(section.id)">
                          <div class="absolute right-0 top-0">
                            <QuestionMark 
                              :count="getSectionQuestionCount(section.id)"
                              :mark-id="section.id.toString()"
                            >
                              <span class="text-gray-400 text-sm">问题</span>
                            </QuestionMark>
                          </div>
                        </template>
                      </div>
                    </template>
                  </div>
                </template>
                <div v-else>  
                  <!-- 如果sections不存在，则渲染markdown内容 -->
                  <div v-html="markdownContent"></div>
                </div>
              </article>
            </div>
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

    <!-- 登录模态框 -->
    <login-modal 
      v-if="showLoginModal" 
      @close="showLoginModal = false"
      @success="handleLoginSuccess"
    />

    <!-- 预览模态框 -->
    <div 
      v-if="showMindmapPreview"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showMindmapPreview = false"
    >
      <div 
        class="bg-white p-6 rounded-lg shadow-lg relative overflow-hidden flex flex-col"
        :class="[
          isMobile 
            ? 'w-[100vw] h-[60vh]' // 移动端尺寸 ！！这里会影响放大后的窗口大小
            : 'w-[100vw] h-[70vh]'  // 桌面端尺寸
        ]"
        @click.stop
      >
        <!-- 标题栏 -->
        <div class="flex justify-between items-center mb-4 flex-shrink-0">
          <h2 class="text-xl font-bold">预览思维导图</h2>
          <button 
            @click="showMindmapPreview = false" 
            class="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              class="h-6 w-6 text-gray-500 hover:text-gray-700" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path 
                stroke-linecap="round" 
                stroke-linejoin="round" 
                stroke-width="2" 
                d="M6 18L18 6M6 6l12 12" 
              />
            </svg>
          </button>
        </div>

        <div 
          ref="containerRef"
          class="relative flex-1 overflow-hidden"
          @mousedown="startDrag"
          @mousemove="onDrag"
          @mouseup="stopDrag"
          @mouseleave="stopDrag"
          @wheel="handleWheel"
          @touchstart="startTouch"
          @touchmove="onTouch"
          @touchend="stopTouch"
        >
          <div class="absolute inset-0 flex items-center justify-center">
            <img 
              :src="previewImageUrl"
              alt="Mindmap Preview"
              class="transition-transform duration-200 origin-center"
              :style="{
                transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
                maxWidth: 'none',
                maxHeight: 'none'
              }"
              @dragstart.prevent
              @load="initializeImage"
            >
          </div>
        </div>
      </div>
    </div>

    <!-- 更多内容 Modal -->
    <more-content-modal
      v-model="showMoreContentModal"
      :article-id="article?.id"
      :original-url="article?.original_link"
      :section-status="sectionStatus"
    />

    <!-- 添加工具栏组件 -->
    <ChatToolbar @refresh-anchors="handleRefreshAnchors" />

    <!-- 添加聊天窗口 -->
    <ChatWindow v-if="chatStore.isChatOpen" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, onUnmounted, nextTick, h, render } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import LoginModal from '../components/LoginModal.vue'
import { format } from 'date-fns'
import { marked } from 'marked'
import { supabase } from '../supabaseClient'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import ArticleForm from '../components/ArticleForm.vue'
import LanguageSwitch from '../components/LanguageSwitch.vue'
import type { Article } from '../types/article'
import type { ArticleSection, SectionType, ViewType } from '../types/section'
import { ALL_SECTION_TYPES, DEFAULT_SELECTED_SECTIONS, getLocalizedSectionType } from '../types/section'
import { useI18n } from 'vue-i18n'
import MindMap from '../components/MindMap.vue'
import Mermaid from '../components/Mermaid.vue'
import { isSupportedMediaUrl } from '../utils/mediaUtils'
import MoreContentModal from '../components/MoreContentModal.vue'
import { useChatStore } from '../stores/chat'
import ChatToolbar from '../components/chat/ChatToolbar.vue'
import ChatWindow from '../components/chat/ChatWindow.vue'
import QuestionMark from '../components/chat/QuestionMark.vue'
import { TextPositionHelper } from '@/utils/textPosition'
import type { ChatSession } from '../types/chat'
import type { TextMark } from '@/utils/textPosition'


// 将 i18n 相关初始化移前面
const { t, locale } = useI18n()
const chatStore = useChatStore()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const article = ref<Article | null>(null)
const sections = ref<ArticleSection[]>([])
const showEditModal = ref(false)
const editForm = ref<Partial<Article>>({})

// 小节理
const selectedSections = ref<SectionType[]>(DEFAULT_SELECTED_SECTIONS)

// 根据当前语言获取可用的节类型
const availableSectionTypes = computed(() => {
  // 始终返回所有小节类型
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
  // 创建新数组来更新
  if (selectedSections.value.includes(sectionType)) {
    // 如果已选中，则移除
    selectedSections.value = selectedSections.value.filter(type => type !== sectionType)
  } else {
    // 如果未选中，则添加
    selectedSections.value = [...selectedSections.value, sectionType]
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
        // 设置提示相关变量
        showLanguageAlert.value = true
        contentLanguage.value = fallbackLanguage
      }
    } else {
      // 如果获取到当前语言的内容，确保提示不显示
      showLanguageAlert.value = false
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

      // 添加新节
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

const showNavB = ref(false)

// 添加一个变量记录上一次的滚动位置
const lastScrollTop = ref(0)

// 添加一个ref来存储当前可见的section
const currentVisibleSection = ref<string>('')

// 添加一个变量来控制是否允许导航切换
const allowNavSwitch = ref(true)

// 修改滚动监听函数
const handleScroll = () => {
  const currentScroll = window.scrollY
  
  // 只有在允许导航切换时才执行切换逻辑
  if (allowNavSwitch.value) {
    // 获取第一个section元素
    const firstSection = document.querySelector('[data-section-type]')
    if (!firstSection) return
    
    // 获取第一个section距离视口顶部的距离
    const firstSectionRect = firstSection.getBoundingClientRect()
    // 设置一个阈值，比如当第一个section进入视口顶部200px范围内时
    const threshold = 200
    
    if (currentScroll > lastScrollTop.value) {
      // 向下滚动
      // 只有当第一个section开始入视口，且滚动超过100px时显示导航
      if (currentScroll > 100 && firstSectionRect.top < threshold) {
        showNavB.value = true
      }
    } else {
      // 向上滚动
      // 只有当向上滚动超过50px时，才切换回原来的导航
      if (lastScrollTop.value - currentScroll > 50) {
        showNavB.value = false
      }
    }
  }
  
  // 更新上次的滚动位置
  lastScrollTop.value = currentScroll <= 0 ? 0 : currentScroll

  // 检测当前可见的section
  const sectionElements = document.querySelectorAll('[data-section-type]')
  sectionElements.forEach((element) => {
    const rect = element.getBoundingClientRect()
    if (rect.top <= window.innerHeight / 3 && rect.bottom >= window.innerHeight / 3) {
      currentVisibleSection.value = element.getAttribute('data-section-type') || ''
    }
  })
}

onMounted(async () => {
  // 2024-01-11: 确保打开新文章时聊天窗口是关闭的
  chatStore.isChatOpen = false
  
  window.addEventListener('scroll', handleScroll)
  await authStore.loadUser()
  await fetchArticle()
  await fetchArticleMarks()
})

// 在 onUnmounted 中移除滚动监听
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

// 复制当前页面URL
const copyCurrentUrl = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href)
    ElMessage.success(t('article.copySuccess'))
  } catch (err) {
    console.error('复制失败:', err)
    ElMessage.error(t('article.copyError'))
  }
}

// 当鼠标悬停在文章链接上时预取文章内容
const prefetchArticle = async (id: string) => {
  try {
    const { data } = await supabase
      .from('keep_articles')
      .select('*')
      .eq('id', id)
      .single()
    
    // 将数据存入缓存
    if (data) {
      const cache = await caches.open('articles-cache')
      await cache.put(`/article/${id}`, new Response(JSON.stringify(data)))
    }
  } catch (error) {
    console.error('预取文章失败:', error)
  }
}

const showLoginModal = ref(false)

// 添加登出处理函数
const handleLogout = async () => {
  try {
    await authStore.signOut()
    ElMessage.success(t('auth.logoutSuccess'))
    // 可选：后跳转到首页
    router.push('/')
  } catch (error) {
    console.error('登出失败:', error)
    ElMessage.error(t('auth.logoutError'))
  }
}

// 添加计算性来获取一个和下一个section
const prevSection = computed(() => {
  if (!currentVisibleSection.value || !displaySections.value.length) return null
  const currentIndex = displaySections.value.findIndex(
    section => section.section_type === currentVisibleSection.value
  )
  return currentIndex > 0 ? displaySections.value[currentIndex - 1] : null
})

const nextSection = computed(() => {
  if (!currentVisibleSection.value || !displaySections.value.length) return null
  const currentIndex = displaySections.value.findIndex(
    section => section.section_type === currentVisibleSection.value
  )
  return currentIndex < displaySections.value.length - 1 
    ? displaySections.value[currentIndex + 1] 
    : null
})

// 添加一个变量来跟踪滑动方向
const transitionName = ref('slide-right')

// 修改 scrollToSection 函数
const scrollToSection = (sectionType: string) => {
  const element = document.querySelector(`[data-section-type="${sectionType}"]`)
  if (element) {
    // 暂时禁用导航切换
    allowNavSwitch.value = false
    
    // 判断滑动方向
    const currentIndex = displaySections.value.findIndex(
      section => section.section_type === currentVisibleSection.value
    )
    const targetIndex = displaySections.value.findIndex(
      section => section.section_type === sectionType
    )
    
    // 设置过渡方向
    transitionName.value = targetIndex > currentIndex ? 'slide-left' : 'slide-right'
    
    // 动到目标位置
    const headerHeight = 71
    const elementPosition = element.getBoundingClientRect().top + window.pageYOffset
    window.scrollTo({
      top: elementPosition - headerHeight - 20,
      behavior: 'smooth'
    })

    // 画完成后恢复导航换功能
    setTimeout(() => {
      allowNavSwitch.value = true
    }, 800) // 设置稍长于滚动动画的时间
  }
}

const showMindmapPreview = ref(false)
const previewImageUrl = ref('')

// 添加处理预览的方法
const handlePreviewMindmap = () => {
  showMindmapPreview.value = true
}

// 图片缩放和拖动相关的状态
const scale = ref(1)
const position = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })

// 缩放控制
const zoomIn = () => {
  const newScale = scale.value * 1.2
  if (newScale <= 5) {
    scale.value = newScale
    adjustPosition()
  }
}

const zoomOut = () => {
  const newScale = scale.value / 1.2
  if (newScale >= 0.1) {
    scale.value = newScale
    adjustPosition()
  }
}

const resetZoom = () => {
  scale.value = 1
  position.value = { x: 0, y: 0 }
}

// 拖动控制
const startDrag = (e: MouseEvent) => {
  isDragging.value = true
  dragStart.value = {
    x: e.clientX - position.value.x,
    y: e.clientY - position.value.y
  }
}

const onDrag = (e: MouseEvent) => {
  if (!isDragging.value) return
  position.value = {
    x: e.clientX - dragStart.value.x,
    y: e.clientY - dragStart.value.y
  }
}

const stopDrag = () => {
  isDragging.value = false
}

// 鼠标滚轮缩放
const handleWheel = (e: WheelEvent) => {
  e.preventDefault()
  
  // 2024-01-12: 添加触摸板检测和灵敏度控制
  // 检查是否是触摸板事件 (通过检查 deltaMode 和 deltaY 的精确度)
  const isTouchpad = e.deltaMode === 0 && Math.abs(e.deltaY) < 50
  
  // 根据设备类型使用不同的缩放系数
  let zoomFactor
  if (isTouchpad) {
    // 触摸板使用更小的缩放系数
    zoomFactor = e.deltaY > 0 ? 0.98 : 1.02
  } else {
    // 鼠标滚轮使用稍大的缩放系数
    zoomFactor = e.deltaY > 0 ? 0.9 : 1.1
  }
  
  // 计算新的缩放值
  const newScale = scale.value * zoomFactor
  
  // 限制缩放范围
  if (newScale >= 0.1 && newScale <= 5) {
    scale.value = newScale
  }
}

// 添加触摸相关的状态
const lastTouchDistance = ref(0)
const containerRef = ref<HTMLDivElement | null>(null)

// 修改初始化图片大小和位置的函数
const initializeImage = (e: Event) => {
  const img = e.target as HTMLImageElement
  const container = (e.currentTarget as HTMLElement).parentElement
  if (!container) return

  // 等待下一个渲染周期，确保容器尺寸已更新
  setTimeout(() => {
    // 获取容器的实际尺寸
    const containerWidth = container.clientWidth
    const containerHeight = container.clientHeight
    const containerRatio = containerWidth / containerHeight
    const imageRatio = img.naturalWidth / img.naturalHeight

    // 设置最小缩放比例
    const MIN_SCALE = 0.5
    
    let initialScale
    if (containerRatio > imageRatio) {
      // 图片较窄，以高度为准，但留出一些边距
      initialScale = (containerHeight * 0.9) / img.naturalHeight
    } else {
      // 图片较宽，以宽度为准，但留出一些边距
      initialScale = (containerWidth * 0.9) / img.naturalWidth
    }

    // 设置缩放比例
    scale.value = Math.max(initialScale, MIN_SCALE)

    // 计算图片缩放后的实际尺寸
    const scaledWidth = img.naturalWidth * scale.value
    const scaledHeight = img.naturalHeight * scale.value

    // 计算居中位置！！！！这个居中效果横向的，是目测出来的写法，很奇怪，暂时先这样
    position.value = {
      x: Math.round(-(containerWidth - scaledWidth * 2 ) / 10),
      y: Math.round((containerHeight - scaledHeight) / 2)
    }
  }, 0)
}

// 触摸事件处理
const startTouch = (e: TouchEvent) => {
  e.preventDefault()
  if (e.touches.length === 2) {
    // 双指触摸，记录初始距离
    const touch1 = e.touches[0]
    const touch2 = e.touches[1]
    lastTouchDistance.value = Math.hypot(
      touch2.clientX - touch1.clientX,
      touch2.clientY - touch1.clientY
    )
  } else if (e.touches.length === 1) {
    // 单指触摸，开始拖动
    const touch = e.touches[0]
    isDragging.value = true
    dragStart.value = {
      x: touch.clientX - position.value.x,
      y: touch.clientY - position.value.y
    }
  }
}

const onTouch = (e: TouchEvent) => {
  e.preventDefault()
  if (e.touches.length === 2) {
    // 双指缩放
    const touch1 = e.touches[0]
    const touch2 = e.touches[1]
    const currentDistance = Math.hypot(
      touch2.clientX - touch1.clientX,
      touch2.clientY - touch1.clientY
    )

    if (lastTouchDistance.value) {
      const delta = currentDistance / lastTouchDistance.value
      const newScale = scale.value * delta
      if (newScale >= 0.1 && newScale <= 5) {
        scale.value = newScale
      }
    }
    lastTouchDistance.value = currentDistance
  } else if (e.touches.length === 1 && isDragging.value) {
    // 单指拖动
    const touch = e.touches[0]
    position.value = {
      x: touch.clientX - dragStart.value.x,
      y: touch.clientY - dragStart.value.y
    }
  }
}

const stopTouch = (e: TouchEvent) => {
  e.preventDefault()
  isDragging.value = false
  lastTouchDistance.value = 0
}

// 添加位置调整函数
const adjustPosition = () => {
  const container = containerRef.value
  const img = container?.querySelector('img')
  if (!container || !img) return

  // 获取容器的实际尺寸
  const containerWidth = container.clientWidth
  const containerHeight = container.clientHeight
  
  // 计算图片缩放后的实际尺寸
  const scaledWidth = img.naturalWidth * scale.value
  const scaledHeight = img.naturalHeight * scale.value

  // 如果图片尺寸小于容器，则居中显示
  if (scaledWidth < containerWidth) {
    position.value.x = Math.round((containerWidth - scaledWidth) / 2)
  } else {
    // 则限制拖动范围
    const minX = Math.min(0, containerWidth - scaledWidth)
    position.value.x = Math.max(minX, Math.min(0, position.value.x))
  }

  if (scaledHeight < containerHeight) {
    position.value.y = Math.round((containerHeight - scaledHeight) / 2)
  } else {
    // 否则限制拖动范围
    const minY = Math.min(0, containerHeight - scaledHeight)
    position.value.y = Math.max(minY, Math.min(0, position.value.y))
  }
}

// 添加移动端检测
const isMobile = ref(window.innerWidth <= 768)

// 监听窗口大小变化
onMounted(() => {
  window.addEventListener('resize', () => {
    isMobile.value = window.innerWidth <= 768
  })
  console.log('ChatStore initialized:', chatStore)
  console.log('ChatToolbar component mounted')
})

onUnmounted(() => {
  window.removeEventListener('resize', () => {
    isMobile.value = window.innerWidth <= 768
  })
})

const getArticleImage = (imageUrl: string | null) => {
  // 使用与ArticleCard相同的判断逻辑
  if (imageUrl && 
      imageUrl.trim() !== '' && 
      !imageUrl.includes('qpic.cn') &&
      imageUrl !== '无缩略图') {
    return imageUrl;
  }
  return '/images/covers/article_default.png';
}

// 添加获取作者名称的方法
const getAuthorName = () => {
  if (!article.value?.author?.name || 
      article.value?.author?.name === t('upload.card.fallback.unknownAuthor') || 
      article.value?.author?.name === 'Unknown') {
    return t('upload.card.fallback.unknownAuthor')
  }
  return article.value.author.name
}

// 添加获取标题的方法
const getArticleTitle = () => {
  if (!article.value?.title || article.value.title.trim() === '') {
    return t('upload.card.fallback.noTitle')
  }
  return article.value.title
}

// 判断是否为媒体类型文章
const isMediaArticle = computed(() => {
  return article.value && isSupportedMediaUrl(article.value.original_link || '')
})

// 定义响应式状态
const sectionStatus = ref({
  summaryZh: false,
  summaryEn: false,
  detailedZh: false,
  detailedEn: false,
  subtitleZh: false,
  subtitleEn: false
})

// 获取所有语言的sections
const fetchAllSections = async () => {
  try {
    const { data: allSections, error } = await supabase
      .from('keep_article_sections')
      .select('section_type, language')
      .eq('article_id', route.params.id)

    if (error) throw error

    if (allSections) {
      sectionStatus.value = {
        summaryZh: allSections.some(s => s.section_type === '总结' && s.language === 'zh'),
        summaryEn: allSections.some(s => s.section_type === '总结' && s.language === 'en'),
        detailedZh: allSections.some(s => s.section_type === '分段详述' && s.language === 'zh'),
        detailedEn: allSections.some(s => s.section_type === '分段详述' && s.language === 'en'),
        subtitleZh: allSections.some(s => s.section_type === '原文字幕' && s.language === 'zh'),
        subtitleEn: allSections.some(s => s.section_type === '原文字幕' && s.language === 'en')
      }
    }
  } catch (error) {
    console.error('获取sections状态失败:', error)
    ElMessage.error(t('article.fetchSectionsError'))
  }
}

// 在组件挂载时获取sections状态
onMounted(() => {
  fetchAllSections()
})

// 当路由参数变化时重新获取
watch(() => route.params.id, () => {
  fetchAllSections()
})

// 控制更多内容 modal 的显示
const showMoreContentModal = ref(false)

// 处理更多内容按钮点击
const handleMoreContent = () => {
  if (!authStore.isAuthenticated) {
    showLoginModal.value = true
    return
  }
  showMoreContentModal.value = true
}

// 添加控制提示显示的变量
const showLanguageAlert = ref(false)
const contentLanguage = ref('')

// 处理文本选择
const handleTextSelection = () => {
  console.log('Text selection triggered')
  const selection = window.getSelection()
  if (!selection || selection.isCollapsed) {
    console.log('No text selected')
    chatStore.hideToolbar()
    return
  }

  const range = selection.getRangeAt(0)
  const rect = range.getBoundingClientRect()
  
  // 计算工具栏位置
  const position = {
    top: rect.bottom, // 放在选择区域下方
    left: rect.left
  }

  // 处理边界情况
  const viewportWidth = window.innerWidth
  if (position.left + 200 > viewportWidth) {
    position.left = viewportWidth - 220
  }

  // 确保不会超出底部
  const viewportHeight = window.innerHeight
  if (position.top + 50 > viewportHeight) { // 50 是工具栏的预估高度
    position.top = rect.top - 50 // 如果底部放不下就放到上方
  }

  chatStore.showToolbar(position, selection.toString())
}

// 添加获取section级别问题数量的方法
const getSectionQuestionCount = (sectionId: string) => {
  // 这里需要实现获取section级别问题数量的逻辑
  // 这里只是一个示例，实际实现需要根据你的需求来实现
  return 0
}

// 添加处理 Ask AI 的方法
const handleAskAI = async () => {
  if (!authStore.isAuthenticated) {
    showLoginModal.value = true
    return
  }
  
  if (!article.value?.id) {
    ElMessage.error('文章信息不存在')
    return
  }
  
  try {
    // 传入isAskAI参数，第三个变量为ture
    await chatStore.createNewSession(article.value.id, undefined, true)
  } catch (error) {
    console.error('创建AI对话失败:', error)
  }
}

// 添加获取文章标记的方法
const articleMarks = ref<ChatSession[]>([])

const fetchArticleMarks = async () => {
  try {
    const { data, error } = await supabase
      .from('keep_chat_sessions')
      .select('*')
      .eq('article_id', route.params.id)
    
    if (error) throw error
    if (data) {
      articleMarks.value = data
    }
  } catch (error) {
    console.error('获取文章标记失败:', error)
  }
}

// 添加处理标记的方法
const processQuestionMarks = () => {
  const wrappers = document.querySelectorAll('.question-mark-wrapper')
  wrappers.forEach(wrapper => {
    const markId = wrapper.getAttribute('data-mark-id')
    const articleId = wrapper.getAttribute('data-article-id')
    const sectionType = wrapper.getAttribute('data-section-type')
    const markContent = wrapper.getAttribute('data-mark-content')
    const position = wrapper.getAttribute('data-position')

    if (markId && articleId && sectionType && markContent && position) {
      // 创建一个临时容器
      const container = document.createElement('div')
      
      // 使用 h 函数创建 VNode
      const vnode = h(QuestionMark, {
        markId,
        articleId: Number(articleId),
        sectionType,
        markContent,
        position: JSON.parse(position)
      }, () => [wrapper.textContent])

      // 渲染到临时容器
      render(vnode, container)
      
      // 替换原始元素
      if (container.firstElementChild) {
        wrapper.replaceWith(container.firstElementChild)
      }
    }
  })
}

// 修改 renderSectionContent 方法
const renderSectionContent = (section: ArticleSection) => {
  if (!section || !section.content) {
    console.warn('无效的 section:', section)
    return ''
  }

  try {
    // 先渲染 markdown
    const htmlContent = marked(section.content)
    const container = document.createElement('div')
    container.innerHTML = htmlContent

    // 获取该 section 的所有标记
    const sectionMarks = articleMarks.value?.filter(
      mark => mark.section_type === section.section_type
    ) || []

    // 处理标记
    sectionMarks.forEach(mark => {
      const position = mark.position

      if (!position || 
          typeof position.nodeIndex !== 'number' || 
          typeof position.startOffset !== 'number' || 
          typeof position.endOffset !== 'number') {
        console.warn('无效的标记位置:', { mark, position })
        return
      }

      const textMark: TextMark = {
        nodeIndex: position.nodeIndex,
        startOffset: position.startOffset,
        endOffset: position.endOffset,
        text: mark.mark_content // 使用原文内容进行匹配
      }

      const range = TextPositionHelper.findPosition(container, textMark)
      if (range) {
        // 使用新的 applyMarkStyle 方法
        const markInfo = {
          'mark-id': mark.id,
          'article-id': section.article_id,
          'section-type': section.section_type,
          'mark-content': mark.mark_content, // 使用原文内容作为显示内容
          'position': JSON.stringify(position)
        }
        
        TextPositionHelper.applyMarkStyle(range, markInfo)
      }
    })

    // 在处理完标记后，调用 processQuestionMarks
    nextTick(() => {
      processQuestionMarks()
    })

    return container.innerHTML
  } catch (error) {
    console.error('渲染 section 内容失败:', error)
    return ''
  }
}

// 在组件挂载时获取标记
onMounted(async () => {
  await fetchArticle()
  await fetchArticleMarks()
})

// 监听最新创建的会话
watch(() => chatStore.lastCreatedSession, async (newSession) => {
  if (newSession) {
    // 重新获取文章标记
    await fetchArticleMarks()
    
    // 在下一个 tick 重新处理标记
    nextTick(() => {
      const sections = document.querySelectorAll('[data-section-type]')
      sections.forEach(section => {
        if (section.getAttribute('data-section-type') === newSession.section_type) {
          // 重新渲染该 section 的内容
          const sectionData = sections.value.find(s => s.section_type === newSession.section_type)
          if (sectionData) {
            renderSectionContent(sectionData)
          }
        }
      })
    })
  }
})

// 处理登录成功
const handleLoginSuccess = () => {
  showLoginModal.value = false
  // 2024-01-09: 移除登录成功提示,避免重复提示
  // ElMessage.success(t('auth.loginSuccess')) // 删除这行
}

// 添加处理刷新锚点的方法
const handleRefreshAnchors = async () => {
  // 2024-01-11: 重新获取文章标记并刷新显示
  await fetchArticleMarks()
  
  // 在下一个 tick 重新处理标记
  nextTick(() => {
    const sections = document.querySelectorAll('[data-section-type]')
    sections.forEach(section => {
      const sectionType = section.getAttribute('data-section-type')
      if (sectionType) {
        const sectionData = sections.value.find(s => s.section_type === sectionType)
        if (sectionData) {
          renderSectionContent(sectionData)
        }
      }
    })
  })
}
</script>

<style>
/* 替换原来的动画样式为新的横向滑动动画 */

/* 向左滑动动画 */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.8s;
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(80px);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-80px);
}

/* 向右滑动动画 */
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.8s ;
}

.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-100px);
}

.slide-right-leave-to {
  opacity: 0;
  transform: translateX(100px);
}

/* 确保动画期间元素不会重叠 */
.slide-left-leave-active,
.slide-right-leave-active {
  position: absolute;
}

/* 移动过渡效果 */
.slide-left-move,
.slide-right-move {
  transition: transform 0.2s ease-out;
}

/* 其他现有样式保持不变 */
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

/* 优化滚动行为 */
html {
  scroll-behavior: smooth;
}

/*  style 标签中加下全样式 */
body {
  overflow-x: hidden;
  width: 100%;
}

/* 确保所有图片不会导容器溢出 */
img {
  max-width: 100%;
  height: auto;
}

/* 确保 prose 内容不会导致溢出 */
.prose {
  max-width: 100% !important;
  overflow-wrap: break-word;
}

/* 确保代码块不会导致溢出 */
.prose pre {
  max-width: 100%;
  overflow-x: auto;
}

/* 确保导航栏始终在最上层 */
header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: white;
  z-index: 999;
}

/* 为内容添加顶部内边距，防止被导航栏遮挡 */
.min-h-screen {
  padding-top: 71px; /* 导航栏高度 + 1px 边框 */
}

/* 确保所有弹出层和态框的 z-index 大于导航栏 */
.el-message {
  z-index: 1000 !important;
}

.el-dialog__wrapper {
  z-index: 1000 !important;
}

.mindmap-preview-dialog {
  :deep(.el-dialog__body) {
    height: calc(100vh - 100px);
    padding: 20px;
    background: #f5f5f5;
  }
}

/* 禁用图片拖动的默认行为 */
img {
  -webkit-user-drag: none;
  -khtml-user-drag: none;
  -moz-user-drag: none;
  -o-user-drag: none;
  user-drag: none;
}

/* 确保预览容器不会滚动 */
.overflow-hidden {
  overflow: hidden !important;
}

.wavy-underline {
  text-decoration-line: underline;
  text-decoration-style: wavy;
  text-decoration-color: rgba(255, 200, 0, 0.3);
  text-decoration-thickness: 2px;
}

.wavy-underline:hover {
  text-decoration-color: rgba(255, 200, 0, 0.6);
}

/* 添加必要的样式 */
.question-mark-wrapper {
  position: relative;
  display: inline-block;
}

/* 添加CSS变量 */
:root {
  --chat-window-width: 30vw;
  --content-max-width: 1024px;
  --content-padding: 1rem;  /* 新增：统一内容padding */
  --min-side-margin: 1rem;  /* 新增：最小侧边距 */
}

@media (max-width: 1600px) {
  :root {
    --chat-window-width: 480px;
  }
}

@media (max-width: 1200px) {
  :root {
    --chat-window-width: 420px;
    --content-padding: 0.75rem;
  }
}

/* 确保内容不会被聊天窗口遮挡 */
.min-h-screen {
  padding-top: 71px;
  transition: all 0.3s ease-in-out;
}

/* 调整内容容器布局 */
.article-content {
  margin: 0 auto;
  padding: 0 var(--content-padding);
  max-width: var(--content-max-width);
  transition: all 0.3s ease-in-out;
  width: 100%;
}

/* 当聊天窗口打开时的样式 */
.chat-open .article-content {
  margin-right: var(--chat-window-width);
  max-width: calc(100vw - var(--chat-window-width) - var(--min-side-margin) * 2);
}

/* 标签区域样式 */
.tags-container {
  width: 100%;
  padding: 1rem var(--content-padding);
  transition: all 0.3s ease-in-out;
}

.chat-open .tags-container {
  margin-right: var(--chat-window-width);
  max-width: calc(100vw - var(--chat-window-width));
}

/* 文章主容器样式 */
.article-main-container {
  width: 100%;
  margin: 0 auto;
  transition: all 0.3s ease-in-out;
}

.chat-open .article-main-container {
  margin-right: var(--chat-window-width);
  max-width: calc(100vw - var(--chat-window-width));
}

@media (max-width: 768px) {
  :root {
    --content-padding: 0.5rem;
    --min-side-margin: 0.5rem;
  }
  
  .chat-open .article-content,
  .chat-open .tags-container,
  .chat-open .article-main-container {
    margin-right: 0;
    max-width: 100%;
  }
}
</style>
