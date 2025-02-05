<template>
  <!-- 页面容器 -->
  <div 
    class="min-h-screen bg-white overflow-x-hidden w-full"
    :class="{ 'chat-open': chatStore.chatWindowState === 'expanded' }"
  >
    <!-- 顶部导航栏 - 始终显示 -->
    <header class="fixed top-0 left-0 right-0 bg-white z-[1001] w-full">
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
        <div v-if="!showNavB" class="flex justify-between items-center px-4 h-[90px] min-w-[320px] max-w-[1440px] mx-auto relative" style="max-width: min(100%, 1440px);">
          <!-- 左侧Logo和标题容器 -->
          <div class="flex flex-col flex-shrink-0">
            <!-- 2024-03-24: 添加点击返回首页功能 -->
            <div 
              class="flex items-center gap-2 cursor-pointer" 
              @click="router.push('/')"
            >
              <!-- 网站Logo图片 -->
              <img 
                src="/images/icons/logo.svg" 
                alt="Keep Up Logo" 
                class="w-[36px] h-[36px] sm:w-[48px] sm:h-[48px] flex-shrink-0" 
              />
              <!-- 网站标题文本 -->
              <h1 class="text-[16px] sm:text-[20px] text-[#333333] font-[400] leading-6 font-['PingFang_SC'] flex items-center gap-2 whitespace-nowrap">
                {{ t('home.title') }}
                <!-- 2024-03-19: 添加beta标记 -->
                <span class="hidden sm:inline-block px-1.5 py-0.5 bg-gradient-to-r from-pink-500 to-purple-500 text-white text-xs rounded-full font-medium transform hover:scale-105 transition-transform">
                  BETA
                </span>
              </h1>
            </div>
            <!-- 2024-03-22: 添加介绍文字 -->
            <p class="mt-1 text-xs sm:text-sm bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent font-medium animate-pulse whitespace-nowrap">
              <!-- 移动端显示简短文案 -->
              <span class="sm:hidden">Quick video & audio summary</span>
              <!-- 桌面端显示完整文案 -->
              <span class="hidden sm:inline">Quick video & audio summary</span>
            </p>
          </div>

          <!-- 2024-03-19: Early Access横幅 - 仅在桌面端显示在导航栏中 -->
          <div class="hidden sm:block bg-white py-2 text-center text-pink-500 font-medium relative -ml-20">
            <div 
              class="cursor-pointer"
              @click="feedbackStore.showForm()"
            >
              <p class="text-base animate-bounce text-pink-500">
                <span class="">📨 Dear early adopters, </span>
                <span class="text-blue-500 font-medium group-hover:text-blue-600 transition-colors">Click here</span>
                <span class=""> to share your feedback and shape our future!</span>
                <span class="ml-1 inline-block animate-bounce">📨</span>
              </p>
            </div>
          </div>
          
          <!-- 右侧导航元素容器 -->
          <div class="flex items-center gap-1 pl-2">
            <!-- 语言切换组件 -->
            <language-switch/>
        
            <!-- 已登录用户信息区域 -->
            <template v-if="authStore.isAuthenticated">
              <!-- 用户头像 -->
              <img 
                :src="authStore.user?.user_metadata?.avatar_url || '/images/icons/avatar.svg'" 
                :alt="authStore.user?.email || 'User Avatar'" 
                class="w-[24px] h-[24px] rounded-full flex-shrink-0"
              />
              <!-- 登出按钮 -->
              <button 
                @click="handleLogout"
                class="text-gray-600 hover:text-gray-800 min-w-[48px] sm:min-w-[64px] h-[32px] text-center text-sm sm:text-base whitespace-nowrap"
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
                <div 
                  :key="currentVisibleSection || 'current'"
                  class="relative"
                >
                  <h2 class="text-base md:text-lg text-gray-900 font-medium">
                    {{ currentVisibleSection ? getLocalizedSectionType(currentVisibleSection) : '' }}
                  </h2>
                  <!-- 添加与tabs相同的底部指示条 -->
                  <div 
                    class="absolute inset-x-0 bottom-[-4px] h-0.5 bg-blue-500 transform scale-100 transition-transform duration-200"
                  ></div>
                </div>

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
      <div class="h-[1px] hidden bg-[#E5E5E5] w-full"></div>
    </header>

    <!-- 加载状态显示 -->
    <LoadingSpinner v-if="isLoading || !article" />

    <!-- 主要内容区域 -->
    <div v-if="!isLoading && article">
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
          class="w-full max-w-[1024px] mx-auto transition-all duration-300"
        >
          <div class="relative px-4 pt-8 pb-0">
            <div class="flex flex-col md:flex-row gap-8 items-start md:items-center">
              <!-- 文章封面 -->
              <img 
                :src="getArticleImage(article.cover_image_url)"
                :alt="getArticleTitle()" 
                class="w-auto h-48 md:h-64 object-contain rounded-lg shadow-md" 
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
                    class="hidden inline-flex items-center px-2.5 sm:px-4 py-1.5 text-xs sm:text-sm font-medium text-gray-600 bg-white hover:bg-gray-50 rounded-full transition-colors border border-gray-200 whitespace-nowrap"
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
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2024-01-17: 添加分割线 -->
      <div class="hidden w-full h-[1px] bg-[#E5E5E5]"></div>

      <!-- 小节标签 -->
      <div class="w-full mx-auto bg-white">
        <!-- 小节标签 -->
        <div 
          class="w-full max-w-[1024px] mx-auto transition-all duration-300"
        >

          <!-- 文章内容部分 -->
          <div class="article-main-container">
            <div 
              class="p-4 md:p-8 article-content"
              @mouseup="handleTextSelection"
              @touchend="handleTextSelection"
            >
              <!-- 文章内容 -->
              <article class="prose prose-sm md:prose-lg max-w-none">
                <!-- 2024-03-20 14:30: 添加文章内容hover提示 -->
                <div 
                  class="relative group"
                  @mouseenter="handleContentHover"
                  @mousemove="handleMouseMove"
                  @mouseleave="handleContentLeave"
                >
                  <!-- 添加提示框 -->
                  <div 
                    v-if="showHoverHint"
                    class="fixed text-white px-3 py-1.5 rounded text-sm whitespace-nowrap
                           opacity-0 group-hover:opacity-100 transition-opacity duration-300
                           pointer-events-none z-[1000] bg-blue-500/90"
                    :style="{
                      left: hintPosition.x + 'px',
                      top: hintPosition.y + 'px',
                      transform: 'translate(-50%, -100%)'
                    }"
                  >
                    {{ t('chat.toolbar.hover_hint') }}
                    <div class="absolute left-1/2 bottom-0 transform -translate-x-1/2 translate-y-full
                              border-8 border-transparent border-t-blue-500/90"></div>
                  </div>

                  <!-- 如果sections存在，则渲染sections -->
                  <template v-if="sections.length">
                    <!-- 遍历sections，渲染每个section -->
                    <div 
                      v-for="section in displaySections" 
                      :key="section.id"
                      class="mb-8"
                      :data-section-type="section.section_type"
                      :id="'section-' + section.section_type"
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
                                :show-question-mark="false"
                              >
                                <span class="text-gray-400 text-sm">{{ t('chat.questionMark') }}</span>
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
                </div>
              </article>
            </div>
          </div>
        </div>
      </div>
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
          <h2 class="text-xl font-bold">{{ t('common.edit') }}</h2>
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
            {{ t('common.cancel') }}
          </button>
          <button 
            @click="submitEdit" 
            class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            {{ t('common.save') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 登录模态框 -->
    <login-modal 
      v-if="showLoginModal" 
      @close="handleLoginModalClose"
      @success="handleLoginSuccess"
      :allowClose="authStore.isAuthenticated"
      class="z-[10001]"
    />

    <!-- 2024-03-24: 添加移动端固定在右下角的反馈按钮 -->
    <div 
      class="sm:hidden fixed bottom-32 right-0 z-[1002] cursor-pointer"
      @click="feedbackStore.showForm()"
    >
      <div class="bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full px-4 py-2 shadow-lg transform hover:scale-105 transition-all duration-300 flex items-center justify-center w-[90px] h-[36px]">
        <span class="text-sm font-medium whitespace-nowrap">Feedback</span>
      </div>
    </div>

    <!-- 2024-03-24: 添加反馈表单组件 -->
    <FeedbackForm 
      :is-visible="feedbackStore.showFeedbackForm"
      @close="feedbackStore.closeFeedbackForm"
      @submit="handleFeedbackSubmit"
      class="z-[1003]"
    />

    <!-- 预览模态框 -->
    <div 
      v-if="showMindmapPreview"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[1001]"
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
          <h2 class="text-xl font-bold">{{ t('common.preview') }}</h2>
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
    <div class="z-[1002]">
      <more-content-modal
        v-model="showMoreContentModal"
        :article-id="article?.id"
        :original-url="article?.original_link"
        :section-status="sectionStatus"
      />
    </div>

    <!-- 添加工具栏组件 -->
    <ChatToolbar 
      @refresh-anchors="handleRefreshAnchors" 
      :disabled="showMoreContentModal"
      @scroll-to-bottom="handleScrollToBottom"
    />

    <!-- 添加聊天窗口 -->
    <ChatWindow ref="chatWindowRef" />
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
import { useArticleStore } from '../stores/article'
import { trackEvent } from '@/utils/analytics'
import FeedbackForm from '../components/feedback/FeedbackForm.vue'
import { useFeedbackStore } from '../stores/feedback'
import LoadingSpinner from '../components/LoadingSpinner.vue'


// 将 i18n 相关初始化移前面
const { t, locale } = useI18n()
const chatStore = useChatStore()
const route = useRoute()  // 移到最前面
const router = useRouter()
const authStore = useAuthStore()
const articleStore = useArticleStore()
const feedbackStore = useFeedbackStore()

const isLoading = ref(false)  // 添加 loading 状态

// 2024-03-20 16:30: 优化hover提示位置，使用当前鼠标位置
const showHoverHint = ref(false)
const hintPosition = ref({ x: 0, y: 0 })
let hoverTimer: number | null = null
let hideTimer: number | null = null
let hasShownInCurrentPage = false
let lastMouseEvent: MouseEvent | null = null // 添加记录最后鼠标事件

// 处理鼠标移动
const handleMouseMove = (event: MouseEvent) => {
  lastMouseEvent = event
  // 如果正在显示提示，实时更新位置
  if (showHoverHint.value) {
    hintPosition.value = {
      x: event.clientX,
      y: event.clientY - 30
    }
  }
}

// 处理文章内容hover
const handleContentHover = (event: MouseEvent) => {
  // 如果当前页面已经显示过，则不再显示
  if (hasShownInCurrentPage) return

  lastMouseEvent = event

  // 清除之前的计时器
  if (hoverTimer) {
    clearTimeout(hoverTimer)
  }
  if (hideTimer) {
    clearTimeout(hideTimer)
  }

  // 设置2秒后显示提示
  hoverTimer = window.setTimeout(() => {
    if (lastMouseEvent) {
      showHoverHint.value = true
      hasShownInCurrentPage = true
      
      // 使用最后记录的鼠标位置
      hintPosition.value = {
        x: lastMouseEvent.clientX,
        y: lastMouseEvent.clientY - 30
      }
    }

    // 2秒后强制隐藏
    hideTimer = window.setTimeout(() => {
      showHoverHint.value = false
    }, 2000)
  }, 2000)
}

// 添加鼠标移出事件处理
const handleContentLeave = () => {
  lastMouseEvent = null
  // 清除所有计时器
  if (hoverTimer) {
    clearTimeout(hoverTimer)
    hoverTimer = null
  }
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
  showHoverHint.value = false
}

// 组件卸载时清理
onUnmounted(() => {
  if (hoverTimer) {
    clearTimeout(hoverTimer)
  }
  if (hideTimer) {
    clearTimeout(hideTimer)
  }
})

// 监听路由变化，重置显示状态
watch(() => route.params.id, () => {
  hasShownInCurrentPage = false
})

const article = ref<Article | null>(null)
const sections = ref<ArticleSection[]>([])
const showEditModal = ref(false)
const editForm = ref<Partial<Article>>({})

// 2024-03-20: 添加联系方式显示状态
const showContactInfo = ref(false)

// 根据当前语言获取可用的节类型
const availableSectionTypes = computed(() => {
  // 2024-01-16: 只返回文章中实际存在的section类型
  const existingSectionTypes = new Set(sections.value.map(section => section.section_type))
  return ALL_SECTION_TYPES.filter(type => existingSectionTypes.has(type))
})

// 根据选中的小节筛选显示内容
const displaySections = computed(() => {
  return sections.value
    .filter(section => articleStore.selectedSections.includes(section.section_type))
    .sort((a, b) => {
      // 首先按照 ALL_SECTION_TYPES 中的顺序排序
      const orderA = ALL_SECTION_TYPES.indexOf(a.section_type)
      const orderB = ALL_SECTION_TYPES.indexOf(b.section_type)
      if (orderA !== orderB) {
        return orderA - orderB
      }
      // 如果类型顺序相同，则使用 sort_order 作为次要排序条件
      return a.sort_order - b.sort_order
    })
})

// 切换小节显示状态
const toggleSection = (sectionType: SectionType) => {
  // 2024-01-16: 修改为只实现滚动定位功能，移除选中状态切换
  const element = document.getElementById('section-' + sectionType)
  if (element) {
    const headerHeight = 71 // header的固定高度
    const elementPosition = element.getBoundingClientRect().top + window.pageYOffset
    
    // 平滑滚动到目标位置，考虑header高度和一些额外的空间
    window.scrollTo({
      top: elementPosition - headerHeight - 20,
      behavior: 'smooth'
    })
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
    console.error(t('error.dateFormatError'), error)
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
    isLoading.value = true
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

    // 2024-01-20 13:30: 设置当前文章ID
    if (route.params.id) {
      chatStore.setCurrentArticle(Number(route.params.id))
    }

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

    trackEvent('article_view', {
      articleId: route.params.id,
      title: articleData.title
    })
  } catch (error) {
    console.error(t('error.getArticleDetailsFailed'), error)
    ElMessage.error(t('error.articleFetchFailed'))
  } finally {
    isLoading.value = false
  }
}

// 添加表单引用
const formRef = ref<InstanceType<typeof ArticleForm> | null>(null)

const submitEdit = async () => {
  try {
    if (!editForm.value.title || !editForm.value.content || !editForm.value.author_id) {
      ElMessage.error(t('error.requiredFields'))
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

    ElMessage.success(t('error.updateSuccess'))
    showEditModal.value = false
    await fetchArticle()
  } catch (error) {
    console.error('更新文章失败:', error)
    ElMessage.error(t('error.updateFailed'))
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

// 添加新的section tabs滚动处理函数
const handleTabsScroll = () => {
  const container = tabsContainerRef.value
  if (container) {
    const hasOverflow = container.scrollWidth > container.clientWidth
    // 更精确的滚动到末端判断，添加1px的容差
    const isScrolledToEnd = Math.abs(container.scrollWidth - container.clientWidth - container.scrollLeft) <= 1
    
    showGradientMask.value = hasOverflow
    isAtEnd.value = isScrolledToEnd
  }
}

// 保持原有的handleScroll函数不变
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
    
    // 2024-01-21 16:30: 修改导航切换逻辑
    if (currentScroll <= 0) {
      // 在顶部时强制显示导航A
      showNavB.value = false
    } else if (currentScroll > lastScrollTop.value) {
      // 向下滚动
      // 只有当第一个section开始入视口，且滚动超过100px时显示导航
      if (currentScroll > 100 && firstSectionRect.top < threshold) {
        showNavB.value = true
      }
    } else {
      // 向上滚动
      // 只有当向上滚动超过30px时，才切换回原来的导航
      if (lastScrollTop.value - currentScroll > 30) {
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

// 添加记录文章访问的方法
const recordArticleView = async (userId: string, articleId: number) => {
  try {
    const response = await fetch('/api/article-views/record', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        article_id: articleId
      })
    })

    if (!response.ok) {
      throw new Error('请求失败')
    }
  } catch (error) {
    console.error('记录文章访问失败:', error)
  }
}

// 修改组件挂载时的事件监听
onMounted(async () => {
  try {
    // 确保用户状态已加载
    if (!authStore.isInitialized) {
      await authStore.loadUser()
    }

    // 如果未登录，显示登录框并返回
    if (!authStore.isAuthenticated) {
      showLoginModal.value = true
      return
    }

    isLoading.value = true
    
    // 2024-01-20 13:30: 设置当前文章ID
    if (route.params.id) {
      chatStore.setCurrentArticle(Number(route.params.id))
    }
    
    // 2024-01-20 12:30: 确保打开新文章时聊天窗口是最小化的
    chatStore.chatWindowState = 'minimized'
    
    // 加载文章数据
    await Promise.all([
      fetchArticle(),
      fetchArticleMarks()
    ])

    // 添加页面滚动事件监听
    window.addEventListener('scroll', handleScroll)
    
    // 添加tabs滚动事件监听
    const container = tabsContainerRef.value
    if (container) {
      container.addEventListener('scroll', handleTabsScroll)
    }
    
    // 初始检查
    handleScroll()
    handleTabsScroll()

  } catch (error) {
    console.error('Error in component mount:', error)
    ElMessage.error(t('error.loadingFailed'))
  } finally {
    isLoading.value = false
  }
})

// 修改组件卸载时的事件监听移除
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  const container = tabsContainerRef.value
  if (container) {
    container.removeEventListener('scroll', handleTabsScroll)
  }
})

// 监听sections变化，重新检查tabs状态
watch(() => sections.value, () => {
  nextTick(() => {
    handleTabsScroll()
  })
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

  // 2024-01-21 16:30: 添加登录检查
  if (!authStore.isAuthenticated) {
    ElMessage.warning(t('chat.loginRequired'))
    showLoginModal.value = true
    return
  }

  const range = selection.getRangeAt(0)
  const rect = range.getBoundingClientRect()
  
  // 计算工具栏位置
  const position = {
    top: rect.bottom,
    left: rect.left
  }

  // 处理边界情况
  const viewportWidth = window.innerWidth
  if (position.left + 200 > viewportWidth) {
    position.left = viewportWidth - 220
  }

  // 确保不会超出底部
  const viewportHeight = window.innerHeight
  if (position.top + 50 > viewportHeight) {
    position.top = rect.top - 50
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
        position: JSON.parse(position),
        showQuestionMark: false
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
  // 2024-01-20 13:30: 设置当前文章ID
  if (route.params.id) {
    chatStore.setCurrentArticle(Number(route.params.id))
  }
  
  // 2024-01-20 12:30: 确保打开新文章时聊天窗口是最小化的
  chatStore.chatWindowState = 'minimized'
  
  // 添加页面滚动事件监听
  window.addEventListener('scroll', handleScroll)
  
  // 添加tabs滚动事件监听
  const container = tabsContainerRef.value
  if (container) {
    container.addEventListener('scroll', handleTabsScroll)
  }
  
  // 初始检查
  handleScroll()
  handleTabsScroll()
  
  // 加载用户信息和文章数据
  await authStore.loadUser()
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
const handleLoginSuccess = async () => {
  showLoginModal.value = false
  
  try {
    // 重新加载用户信息
    await authStore.loadUser()
    if (!authStore.user?.id) {
      console.error('[handleLoginSuccess] User information not loaded properly')
      return
    }
    
    // 加载文章数据
    await fetchArticle()
    await fetchArticleMarks()
    
  } catch (error) {
    console.error('[handleLoginSuccess] Error:', error)
    ElMessage.error(t('error.loginFailed'))
  }
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

// 添加新的响应式变量
const sectionTabsRef = ref<HTMLElement | null>(null)
const tabsContainerRef = ref<HTMLElement | null>(null)
const showGradientMask = ref(false)

// 添加新的计算属性来判断是否滚动到最右端
const isAtEnd = ref(false)

// 修改 checkOverflow 函数
const checkOverflow = () => {
  const container = tabsContainerRef.value
  if (container) {
    const hasOverflow = container.scrollWidth > container.clientWidth
    const isScrolledToEnd = Math.abs(container.scrollWidth - container.clientWidth - container.scrollLeft) < 1
    
    showGradientMask.value = hasOverflow
    isAtEnd.value = isScrolledToEnd
  }
}

// 监听滚动事件
onMounted(() => {
  const container = tabsContainerRef.value
  if (container) {
    container.addEventListener('scroll', checkOverflow)
  }
  checkOverflow()
})

// 在组件卸载时移除事件监听
onUnmounted(() => {
  const container = tabsContainerRef.value
  if (container) {
    container.removeEventListener('scroll', handleTabsScroll)
  }
})

// 监听sections变化，重新检查是否需要显示遮罩
watch(() => sections.value, () => {
  nextTick(checkOverflow)
})

// 添加 handleMoreSections 函数
const handleMoreSections = () => {
  const container = tabsContainerRef.value
  if (container) {
    const scrollStep = container.clientWidth * 0.8 // 滚动80%的可视区域宽度
    const targetScroll = container.scrollLeft + scrollStep
    
    // 使用平滑滚动
    container.scrollTo({
      left: targetScroll,
      behavior: 'smooth'
    })
  }
}

// 修改toggleChatWindow函数，添加登录检查
const toggleChatWindow = () => {
  // 2024-01-21 16:30: 添加登录检查
  if (!authStore.isAuthenticated && chatStore.chatWindowState === 'minimized') {
    ElMessage.warning(t('chat.loginRequired'))
    showLoginModal.value = true
    return
  }
  
  chatStore.chatWindowState = chatStore.chatWindowState === 'expanded' ? 'minimized' : 'expanded'
  if (chatStore.chatWindowState === 'expanded') {
    windowHeight.value = DEFAULT_EXPANDED_HEIGHT
  }
}

const chatWindowRef = ref<InstanceType<typeof ChatWindow> | null>(null)

// 2024-03-21 14:30: 处理滚动到底部事件
const handleScrollToBottom = () => {
  chatWindowRef.value?.scrollToBottom(true)
}

// 2024-03-20: 添加获取联系方式图片的函数
const getContactImage = (imageName: string): string => {
  return `/images/covers/${imageName}`
}

// 添加handleLoginModalClose函数
const handleLoginModalClose = () => {
  // 2024-03-21: 只有在已登录状态下才允许关闭登录框
  if (authStore.isAuthenticated) {
    showLoginModal.value = false
  }
}

// 在 setup 中添加
const showFeedbackForm = ref(false)
const disableHoverEffect = ref(false)

const handleFeedbackFormClose = () => {
  showFeedbackForm.value = false
  disableHoverEffect.value = true
}

const handleFeedbackSubmit = (data: any) => {
  console.log('Feedback submitted:', data)
  showFeedbackForm.value = false
  ElMessage.success(t('feedback.submitSuccess'))
}

// 添加反馈表单相关的处理函数
const handleFeedbackHover = () => {
  showFeedbackForm.value = true
}

const handleFeedbackClose = () => {
  showFeedbackForm.value = false
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
  overflow-y: scroll;
  /* 下面两行确保滚动条总是显示，即使内容不够长 */
  min-height: 101vh;
  scrollbar-gutter: stable;
}

/*  style 标签中加下全样式 */
body {
  overflow-x: hidden;
  width: 100%;
  /* 添加这行来防止滚动条导致的页面跳动 */
  margin-right: calc(-1 * (100vw - 100%));
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
  width: 100%;
  box-sizing: border-box;
  /* 添加这行来确保内容不会因为滚动条出现而移动 */
  padding-right: calc(100vw - 100%);
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
  padding-bottom: 40vh; /* 为聊天窗口预留空间 */
  transition: all 0.3s ease-in-out;
}

/* 调整内容容器布局 */
.article-content {
  margin: 0 auto;
  padding: 0 var(--content-padding);
  max-width: var(--content-max-width);
  width: 100%;
}

/* 标签区域样式 */
.tags-container {
  width: 100%;
  padding: 0.5rem var(--content-padding);
}

/* 文章主容器样式 */
.article-main-container {
  width: 100%;
  margin: 0 auto;
}

@media (max-width: 768px) {
  :root {
    --content-padding: 0.5rem;
    --min-side-margin: 0.5rem;
  }
  
  .min-h-screen {
    padding-bottom: 60vh; /* 移动端聊天窗口更高，预留更多空间 */
  }
}

/* 2024-01-16: 更新section tabs的样式 */
.section-tabs {
  width: 100%;
  position: relative;
}

.section-tabs .flex {
  position: relative;
  padding: 0.25rem 0; /* 减少上下padding */
}

/* 隐藏滚动条但保持可滚动 */
.hide-scrollbar {
  scrollbar-width: none;
  -ms-overflow-style: none;
  -webkit-overflow-scrolling: touch;
  padding-right: 100px; /* 调整为与渐变区域相同的宽度 */
}

.hide-scrollbar::-webkit-scrollbar {
  display: none;
}

/* 胶囊式按钮样式 */
.section-tabs button {
  white-space: nowrap;
  min-width: 100px;
  position: relative;
  overflow: visible; /* 改为visible允许hover效果溢出 */
  padding: 0.5rem 1.25rem; /* 调整按钮内部的padding */
}

/* 更新hover效果 */
.section-tabs button .relative {
  position: relative;
  z-index: 2;
  display: inline-block; /* 确保容器大小贴合文字 */
}

/* 底部指示条样式优化 */
.section-tabs button > div:last-child {
  transform-origin: center;
  bottom: -1px;
}

@media (min-width: 768px) {
  .section-tabs button {
    min-width: 140px;
  }
}

/* 添加自定义指示条样式 */
.indicator-line {
  height: 2px;
}

@media (max-width: 768px) {
  .tags-container {
    padding: 0.25rem var(--content-padding); /* 移动端进一步减少padding */
  }
  
  .section-tabs .flex {
    padding: 0.125rem 0; /* 移动端进一步减少padding */
  }
  
  .section-tabs button {
    padding: 0.375rem 1rem; /* 移动端减小按钮内部padding */
  }
}

/* 添加反馈表单相关样式 */
.contact-info-container {
  position: relative;
  z-index: 1001;
}

/* 移除不需要的按钮样式 */
.contact-info-container button,
.contact-info-container button:hover,
.contact-info-container button svg,
.contact-info-container button:hover svg {
  all: unset;
}

/* 确保反馈表单在正确的位置，从右边滑出 */
.feedback-form-container {
  position: fixed;
  top: 0;
  right: 0;
  height: 100vh;
  width: 360px;
  z-index: 1002;
  background-color: white;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform;
}

.feedback-form-container.visible {
  transform: translateX(0);
}

/* 优化反馈文字样式 */
.feedback-text {
  position: relative;
  display: inline-block;
  padding: 0.25rem 0.5rem;
  transition: all 0.3s ease;
  font-weight: 500;
}

.feedback-text:hover {
  transform: translateY(-1px);
  text-shadow: 0 2px 4px rgba(236, 72, 153, 0.2);
  color: #db2777; /* pink-600 */
}

/* 优化动画效果 */
.animate-bounce {
  animation: bounce 1s infinite;
  animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(-10%);
  }
  50% {
    transform: translateY(0);
  }
}

@media (max-width: 640px) {
  .feedback-form-container {
    width: 100%;
  }
}
</style>
