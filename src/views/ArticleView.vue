<template>
  <!-- 页面容器 - 改为flex布局 -->
  <div class="min-h-screen bg-white w-full  h-screen pr-0 scrollbar-hide overflow-y-hidden">
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
        <div v-if="!showNavB" class="flex justify-between items-center px-4 h-[75px] min-w-[320px] max-w-[1440px] mx-auto relative" style="max-width: min(100%, 1440px);">
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
              </h1>
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
        <div v-else class="flex justify-center items-center px-4 h-[60px] min-w-[378px] max-w-[1440px] mx-auto" style="max-width: min(100%, 1440px);">
          <div class="flex-1 max-w-4xl mx-auto px-4">
            <div class="w-full h-[40px] flex items-center justify-center">
              <!-- 使用transition-group为section标题添加动画 -->
              <transition-group 
                :name="transitionName"
                class="flex items-center justify-center w-full relative"
                tag="div"
              >
                <!-- 当前section名称 -->
                <div 
                  :key="currentDisplayTitle || 'current'"
                  class="relative"
                >
                  <h2 class="text-base md:text-lg text-gray-900 font-medium">
                    {{ currentDisplayTitle || '' }}
                  </h2>
                  <!-- 添加与tabs相同的底部指示条 -->
                  <div 
                    class="absolute inset-x-0 bottom-[-4px] h-0.5 bg-blue-500 transform scale-100 transition-transform duration-200"
                  ></div>
                </div>
              </transition-group>
            </div>
          </div>
        </div>
      </transition>
      
      <!-- 分割线 -->
      <div class="h-[1px] hidden bg-[#E5E5E5] w-full"></div>
    </header>

    <!-- 主要内容区域 - Flex布局：左侧文章 + 右侧Chat -->
    <div class="flex-1 flex h-full overflow-hidden w-full">
      <!-- 左侧：文章内容容器 -->
      <div 
        class="h-full overflow-y-auto overflow-x-hidden transition-all duration-300"
        ref="scrollContainerRef"
        :class="[
          chatStore.chatWindowState === 'minimized' ? 'flex-1' : 'flex-1'
        ]"
      >
        <!-- 内容包装器 - 负责左右边距但不处理滚动 -->
        <div 
          class="min-h-full transition-all duration-300"
          :class="[
            chatStore.chatWindowState === 'minimized' ? 'article-content-centered' : 'article-content-expanded'
          ]"
        >
          <!-- 加载状态显示 -->
          <LoadingSpinner v-if="isLoading || !article" />

          <!-- 文章内容 -->
          <div v-if="!isLoading && article" class="article-content-wrapper h-full">
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

            <!-- 私密内容提示横幅 -->
            <div 
              v-if="article.is_private" 
              class="private-content-banner mx-4 mb-4"
            >
              <div class="banner-content">
                <span class="banner-icon">🔒</span>
                <span class="banner-text">私密内容 · 仅通过链接可访问</span>
              </div>
            </div>

            <!-- 文章标题和作者信息 -->
            <div class="bg-white">
              <div class="w-full transition-all duration-300">
                <div class="relative px-4 pt-8 pb-0">
                  <div class="flex flex-col md:flex-row gap-8 items-start md:items-center">
                    <!-- 文章封面 -->
                    <img 
                      :src="getArticleImage(article.cover_image_url)"
                      :alt="getArticleTitle()" 
                      class="w-auto h-48 md:h-64 object-contain rounded-lg shadow-md" 
                      referrerpolicy="no-referrer"
                      @error="handleArticleCoverError"
                    />
                    <div class="flex-1">
                      <!-- 文章标题 --> 
                      <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-4">{{ getArticleTitle() }}</h1>
                      <!-- 作者信息 -->
                      <div class="flex items-center gap-4 text-gray-600 text-sm md:text-base">
                        <div class="flex items-center gap-2">
                          <img 
                            :src="getAuthorIcon()" 
                            :alt="article.author?.name || t('upload.card.fallback.unknownAuthor')" 
                            class="w-5 h-5 rounded-full"
                            referrerpolicy="no-referrer"
                            @error="handleAuthorImageError"
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

                        <!-- 删除按钮 - 仅文章所有者可见 -->
                        <button 
                          v-if="isOwner"
                          @click="handleDeleteArticle"
                          class="inline-flex items-center px-2.5 sm:px-4 py-1.5 text-xs sm:text-sm font-medium text-red-600 bg-white hover:bg-red-50 rounded-full transition-colors border border-red-200 whitespace-nowrap"
                        >
                          <svg 
                            class="h-3 w-3 sm:h-3.5 sm:w-3.5 mr-1 sm:mr-1.5" 
                            fill="none" 
                            stroke="currentColor" 
                            viewBox="0 0 24 24"
                          >
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                          {{ t('article.delete') }}
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
                class="w-full transition-all duration-300"
              >

                <!-- 文章内容部分 -->
                <div class="article-main-container">
                    <div 
                      class="p-4 md:p-8 article-content"
                      @mouseup="handleMouseUp($event)"
                      @touchend="handleTouchEndArticle($event)"
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
                                      :mark-id="section.id.toString()"
                                      :article-id="Number(route.params.id)"
                                      :section-type="section.section_type"
                                      :mark-content="''"
                                      :position="{}"
                                      :show-question-mark="false"
                                      :count="getSectionQuestionCount(section.id)"
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
        </div>
      </div>

      <!-- 右侧：Chat容器 - 桌面端显示，移动端隐藏 -->
      <div 
        v-if="!isMobile"
        class="flex-shrink-0 transition-all duration-300 ease-in-out relative overflow-hidden h-full"
        :style="{ width: chatStore.chatWindowState === 'expanded' ? 'var(--chat-window-width)' : '0px' }"
      >
        <ChatWindow />
           <!-- Right-top Ask button -->
           <AskKeepupButton />
      </div>
    </div>

    <!-- 移动端Chat窗口 - 固定在底部 -->
    <div v-if="isMobile" class="relative">
      <ChatWindow />
    </div>

    <!-- 浮动文本选择工具栏 - 当chat收起时显示 -->
    <FloatingTextToolbar />

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
    <!-- 2025-01-13: 私密文章未登录时不允许直接关闭，公开文章可以关闭 -->
    <login-modal 
      v-if="showLoginModal" 
      @close="handleLoginModalClose"
      @success="handleLoginSuccess"
      :allowClose="authStore.isAuthenticated || (article && !article.is_private)"
      class="z-[10001]"
    />

    <!-- 2024-03-24: 移动端反馈按钮已移除 -->

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
import { ElMessage, ElMessageBox } from 'element-plus'
import ArticleForm from '../components/ArticleForm.vue'
import LanguageSwitch from '../components/LanguageSwitch.vue'
import type { Article } from '../types/article'
import type { ArticleSection } from '../types/section'
import { ALL_SECTION_TYPES,getLocalizedSectionType } from '../types/section'
import { useI18n } from 'vue-i18n'
import MindMap from '../components/MindMap.vue'
import Mermaid from '../components/Mermaid.vue'
import { isSupportedMediaUrl } from '../utils/mediaUtils'
import { isMeaningfulTimestamp } from '../utils/citationParser'
import MoreContentModal from '../components/MoreContentModal.vue'
import { useChatStore } from '../stores/chat'
import ChatToolbar from '../components/chat/ChatToolbar.vue'
import ChatWindow from '../components/chat/ChatWindow.vue'
import AskKeepupButton from '../components/chat/AskKeepupButton.vue'
import QuestionMark from '../components/chat/QuestionMark.vue'
import CitationBubble from '../components/chat/CitationBubble.vue'
import FloatingTextToolbar from '../components/chat/FloatingTextToolbar.vue'
import { TextPositionHelper } from '@/utils/textPosition'
import type { ChatSession, Position } from '../types/chat'
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

// 判断当前用户是否是文章所有者
const isOwner = computed(() => {
  return !!(authStore.user?.id && article.value?.user_id && article.value.user_id === authStore.user.id)
})

// Image error states for cover and author avatar
const articleCoverError = ref(false)
const authorImageError = ref(false)

// Reset image error states when navigating to a new article
watch(() => route.params.id, () => {
  articleCoverError.value = false
  authorImageError.value = false
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


// 获取文章和小节内容
const fetchArticle = async () => {
  try {
    isLoading.value = true
    
    const articleId = route.params.id as string
    
    // 判断是数字ID还是私密slug
    const isNumericId = /^\d+$/.test(articleId)
    
    // 首先获取文章基本信息
    let articleQuery = supabase
      .from('keep_articles')
      .select(`
        *,
        user_id,
        author:keep_authors(id, name, icon)
      `)
    
    // 根据ID类型选择查询条件
    if (isNumericId) {
      articleQuery = articleQuery.eq('id', articleId)
    } else {
      // 使用 private_slug 查询
      articleQuery = articleQuery.eq('private_slug', articleId)
    }
    
    const articleResult = await articleQuery.single()
    
    if (articleResult.error) throw articleResult.error
    
    // 2025-01-13: 检查私密文章权限
    // 如果是私密文章且未登录，显示登录框
    if (articleResult.data.is_private && !authStore.isAuthenticated) {
      showLoginModal.value = true
      isLoading.value = false
      return
    }
    
    // 使用获取到的文章ID查询小节
    const realArticleId = articleResult.data.id
    
    // 获取当前语言的文章小节内容
    const sectionsResult = await supabase
      .from('keep_article_sections')
      .select('*')
      .eq('article_id', realArticleId)
      .eq('language', locale.value)
      .order('sort_order')

    // 设置当前文章ID和元信息（用于分享功能）
    if (realArticleId) {
      chatStore.setCurrentArticle(Number(realArticleId), {
        title: articleResult.data.title || '',
        authorName: articleResult.data.author?.name || '',
        isPrivate: articleResult.data.is_private || false
      })
    }

    // 如果当前语言没有内容,获取另一种语言的内容
    let sectionsData = sectionsResult.data
    if (!sectionsData?.length) {
      const fallbackLanguage = locale.value === 'zh' ? 'en' : 'zh'
      const { data: fallbackData, error: fallbackError } = await supabase
        .from('keep_article_sections')
        .select('*')
        .eq('article_id', realArticleId)
        .eq('language', fallbackLanguage)
        .order('sort_order')

      if (fallbackError) throw fallbackError
      sectionsData = fallbackData
    }

    // 更新数据
    article.value = articleResult.data
    sections.value = sectionsData || []

    // 异步记录访问信息，不阻塞主流程（私密内容也记录）
    if (authStore.user?.id && realArticleId) {
      recordArticleView(authStore.user.id, Number(realArticleId))
        .catch(error => console.error('记录访问失败:', error))
    }

    // 记录访问事件
    trackEvent('article_view', {
      article_id: realArticleId,
      title: article.value?.title,
      channel: article.value?.channel,
      is_private: article.value?.is_private
    })

  } catch (error) {
    console.error('获取文章失败:', error)
    ElMessage.error(t('error.fetchFailed'))
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

// 删除文章（软删除，设置 is_visible 为 false）
const handleDeleteArticle = async () => {
  try {
    // 显示确认对话框
    await ElMessageBox.confirm(
      t('article.deleteConfirm'),
      t('common.warning'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    )
    
    // 用户确认后执行删除
    const { error } = await supabase
      .from('keep_articles')
      .update({ is_visible: false })
      .eq('id', article.value?.id)
      .eq('user_id', authStore.user?.id)  // 双重校验，确保只能删除自己的文章
    
    if (error) throw error
    
    ElMessage.success(t('article.deleteSuccess'))
    router.push('/')
  } catch (error: any) {
    // 用户取消不提示错误
    if (error === 'cancel' || error?.message === 'cancel') {
      return
    }
    console.error('删除文章失败:', error)
    ElMessage.error(t('article.deleteFailed'))
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

// 监听文章内容滚动容器的滚动（兼容 window 回退）
const scrollContainerRef = ref<HTMLElement | null>(null)

// 展示段（通过内容标题解析，不依赖数据库 section）
type DisplayAnchor = { id: string; title: string; el: Element }
const displayAnchors = ref<DisplayAnchor[]>([])
const currentDisplayId = ref<string>('')
const currentDisplayTitle = ref<string>('')
let displayMutationObserver: MutationObserver | null = null
let displayIntersectionObserver: IntersectionObserver | null = null

// 展示段标题白名单（中英同义项）
const DISPLAY_TITLES: Record<string, string[]> = {
  Summary: ['summary', '总结'],
  'Key Takeaways': ['key takeaways', 'key takeaway', 'key points', 'key insights', '要点总结'],
  'People': ['人物介绍', '人物', '嘉宾介绍', 'guests', 'guest intro', 'guest introduction', 'people'],
  'Segmented Outline': ['segmented outline', 'outline', '分段提纲'],
  'Background': ['背景', 'background'],
  'Glossary': ['名词解释', '术语', 'glossary'],
  'Q&A': ['qa环节', 'q&a', 'faq'],
  'Quotes': ['金句', 'quotes', 'highlights'],
  'Easter Eggs': ['彩蛋', 'easter eggs'],
  'Detailed Sections': ['分段详述', 'detailed sections', 'details'],
  'Transcript': ['原文字幕', 'transcript', 'subtitles', 'captions'],
  // 新增：与截图匹配的展示段标题
  'Trending': ['trending', 'trends'],
  'Companies & Products': ['companies & products', 'companies and products', 'company & products', 'company and products']
}

const normalize = (s: string) => s
  .replace(/^[#\s\-:：\[\]]+|[\s\-:：\[\]]+$/g, '')
  .replace(/\s+/g, ' ')
  .replace(/&amp;/gi, '&')
  .replace(/\band\b/gi, 'and')
  .trim()
  .toLowerCase()

const getCanonicalDisplayTitle = (text: string): string | null => {
  const n = normalize(text)
  for (const [canon, syns] of Object.entries(DISPLAY_TITLES)) {
    if (syns.some(x => n === x)) return canon
  }
  return null
}

const isDisplayTitle = (text: string): boolean => getCanonicalDisplayTitle(text) !== null

const parseDisplayAnchors = () => {
  const container = document.querySelector('.article-content .prose') as HTMLElement | null
  const anchors: DisplayAnchor[] = []
  if (!container) {
    displayAnchors.value = anchors
    return
  }
  // 标题通常是 h2/h3，但也可能被 markdown-it/marked 包裹或包含链接元素
  const headingNodes = Array.from(container.querySelectorAll('h1, h2, h3, h4, h2 > a, h3 > a'))
    .map((el) => (el.tagName === 'A' && el.parentElement ? el.parentElement : el)) as Element[]
  // 调试：输出当前页面可用标题
  // console.debug('[display-nav] headings found:', headingNodes.map(h => h.textContent?.trim()))
  let idx = 0
  headingNodes.forEach((el) => {
    const title = (el.textContent || '').trim()
    if (!title) return
    const canon = getCanonicalDisplayTitle(title)
    if (!canon) return
    if (!el.id) {
      el.id = `display-anchor-${idx++}`
    }
    anchors.push({ id: el.id, title: canon, el })
  })

  // 兼容：有些内容不是语义化标题，而是 p>strong 或 div>strong 独立成行，或 strong 内嵌链接
  const strongCandidates = Array.from(container.querySelectorAll('p > strong, div > strong, li > strong, p > a > strong, div > a > strong')) as Element[]
  strongCandidates.forEach((strongEl) => {
    const parent = strongEl.parentElement
    if (!parent) return
    // 只接受这一行只有粗体文本，没有其他内容的情况，以避免误判
    const parentText = (parent.textContent || '').trim()
    const selfText = (strongEl.textContent || '').trim()
    if (!parentText || !selfText) return
    if (normalize(parentText) !== normalize(selfText)) return
    const canon = getCanonicalDisplayTitle(selfText)
    if (!canon) return
    if (!parent.id) parent.id = `display-anchor-${idx++}`
    anchors.push({ id: parent.id, title: canon, el: parent })
  })

  // 兼容：解析我们渲染的 section 标题（不依赖数据库字段，只看 DOM）
  const sectionHeadingNodes = Array.from(container.closest('.article-content')?.querySelectorAll('[data-section-type] > h2') || []) as Element[]
  sectionHeadingNodes.forEach((el) => {
    const title = (el.textContent || '').trim()
    const canon = getCanonicalDisplayTitle(title)
    if (!canon) return
    if (!el.id) el.id = `display-anchor-${idx++}`
    anchors.push({ id: el.id, title: canon, el })
  })
  displayAnchors.value = anchors

  // 重建 IntersectionObserver 以更稳健地追踪当前展示段
  if (displayIntersectionObserver) {
    displayIntersectionObserver.disconnect()
  }
  const rootEl = scrollContainerRef.value || undefined
  // 仅用于触发滚动判断，不直接用 IO 的可见判定改变当前段，避免“提前切换到下一个标题”
  displayIntersectionObserver = new IntersectionObserver(() => {
    handleScroll()
  }, { root: rootEl as Element | undefined, threshold: [0.0, 0.25, 0.5, 0.75, 1.0] })

  anchors.forEach(a => displayIntersectionObserver!.observe(a.el))

  // 监听 DOM 变化（例如引用气泡/后处理可能会插入节点导致标题位移）
  if (displayMutationObserver) {
    displayMutationObserver.disconnect()
  }
  displayMutationObserver = new MutationObserver(() => {
    // 轻量节流
    setTimeout(() => {
      parseDisplayAnchors()
      handleScroll()
    }, 0)
  })
  displayMutationObserver.observe(container, { childList: true, subtree: true })
}

const handleScroll = () => {
  const container = scrollContainerRef.value
  const currentScroll = container ? container.scrollTop : window.scrollY
  
  // 只有在允许导航切换时才执行切换逻辑
  if (allowNavSwitch.value) {
    // 获取第一个展示段元素（优先基于内容解析）
    const firstAnchorEl = displayAnchors.value[0]?.el || document.querySelector('[data-section-type]')
    if (!firstAnchorEl) return
    
    // 获取第一个展示段与容器顶部的相对距离
    const firstSectionRect = firstAnchorEl.getBoundingClientRect()
    const containerRectTop = container ? container.getBoundingClientRect().top : 0
    const relativeTop = firstSectionRect.top - containerRectTop
    // 设置一个阈值，比如当第一个section进入视口顶部200px范围内时
    const threshold = 200
    
    // 2024-01-21 16:30: 修改导航切换逻辑
    if (currentScroll <= 0) {
      // 在顶部时强制显示导航A
      showNavB.value = false
    } else if (currentScroll > lastScrollTop.value) {
      // 向下滚动
      // 只有当第一个section开始入视口，且滚动超过100px时显示导航
      if (currentScroll > 100 && relativeTop < threshold) {
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
  const containerRectTop = container ? container.getBoundingClientRect().top : 0
  const viewportHeight = container ? container.clientHeight : window.innerHeight
  sectionElements.forEach((element) => {
    const rect = element.getBoundingClientRect()
    const top = rect.top - containerRectTop
    const bottom = rect.bottom - containerRectTop
    if (top <= viewportHeight / 3 && bottom >= viewportHeight / 3) {
      currentVisibleSection.value = element.getAttribute('data-section-type') || ''
    }
  })

  // 基于展示段锚点检测当前可见的展示段：
  // 策略：优先选择“最后一个已通过顶部阈值(<= switchTopPx)的标题”；
  // 若尚未经过任何标题，则选择第一个；这样可避免在两个展示段之间提前跳到下一个。
  if (displayAnchors.value.length) {
    const anchors = displayAnchors.value
    const switchTopPx = 120
    let passed: { a: DisplayAnchor; top: number }[] = []
    for (const a of anchors) {
      const rect = a.el.getBoundingClientRect()
      const top = rect.top - containerRectTop
      if (top <= switchTopPx) {
        passed.push({ a, top })
      }
    }
    // 取顶部阈值内 top 最大（最靠近顶部）的标题
    let candidate: DisplayAnchor | null = null
    if (passed.length) {
      passed.sort((x, y) => y.top - x.top)
      candidate = passed[0].a
    } else {
      candidate = anchors[0]
    }
    if (candidate && candidate.id !== currentDisplayId.value) {
      currentDisplayId.value = candidate.id
      currentDisplayTitle.value = candidate.title
    }
  }
}

// 添加记录用户对文章访问
const recordArticleView = async (userId: string, articleId: number) => {
  try {
    // 2024-12-30: 调用后端API来记录访问，这样会触发viewer_count的更新
    const response = await fetch('/api/article-views/record', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        article_id: articleId
      })
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(`API调用失败: ${error}`)
    }

    const result = await response.json()
    if (!result.success) {
      throw new Error('记录访问失败')
    }
  } catch (error) {
    console.error('记录文章访问失败:', error)
    throw error
  }
}

// 修改组件挂载时的事件监听
onMounted(async () => {
  try {
    // 2024-12-15: 与 HomeView 保持一致，直接调用 loadUser
    // 不在外部检查 isInitialized，让 loadUser 内部处理
    await authStore.loadUser()

    // 2025-01-13: 移除强制登录检查，改为在 fetchArticle 中判断私密文章
    // 未登录用户可以查看公开文章，私密文章需要登录

    isLoading.value = true
    
    // 2024-01-20 13:30: 设置当前文章ID
    if (route.params.id) {
      chatStore.setCurrentArticle(Number(route.params.id))
    }
    
    // 2024-01-20 12:30: 确保打开新文章时聊天窗口是最小化的
    // 保持chat窗口默认展开状态
    
    // 加载文章数据
    await fetchArticle()
    
    // 2025-01-13: 如果是私密文章且未登录，fetchArticle 会设置 showLoginModal
    // 此时不需要继续加载其他数据
    if (showLoginModal.value && !authStore.isAuthenticated) {
      return
    }
    
    // 2025-01-13: 获取公开的聊天标记（不需要登录，公开标记所有人可见）
    await fetchArticleMarks()

    // 添加页面滚动事件监听（监听文章容器滚动）
    const sc = scrollContainerRef.value
    if (sc) sc.addEventListener('scroll', handleScroll)
    
    // 添加tabs滚动事件监听
    const container = tabsContainerRef.value
    if (container) {
      container.addEventListener('scroll', handleTabsScroll)
    }
    
    // 解析展示段并初始检查
    await nextTick()
    parseDisplayAnchors()
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
  const sc = scrollContainerRef.value
  if (sc) sc.removeEventListener('scroll', handleScroll)
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

// 新的：基于展示段的上一/当前/下一
const currentDisplayIndex = computed(() => displayAnchors.value.findIndex(a => a.id === currentDisplayId.value))
const prevDisplayAnchor = computed(() => currentDisplayIndex.value > 0 ? displayAnchors.value[currentDisplayIndex.value - 1] : null)
const nextDisplayAnchor = computed(() => currentDisplayIndex.value >= 0 && currentDisplayIndex.value < displayAnchors.value.length - 1 ? displayAnchors.value[currentDisplayIndex.value + 1] : null)

// 添加一个变量来跟踪滑动方向
const transitionName = ref('slide-right')

// 修改 scrollToSection 函数（优先滚动内容容器）
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
    
    const sc = scrollContainerRef.value
    if (sc) {
      const targetTop = element.getBoundingClientRect().top - sc.getBoundingClientRect().top + sc.scrollTop
      sc.scrollTo({ top: targetTop - 20, behavior: 'smooth' })
    } else {
      // 回退到 window 滚动
      const headerHeight = 71
      const elementPosition = element.getBoundingClientRect().top + window.pageYOffset
      window.scrollTo({ top: elementPosition - headerHeight - 20, behavior: 'smooth' })
    }

    // 滚动完成后恢复导航切换功能
    setTimeout(() => {
      allowNavSwitch.value = true
    }, 800)
  }
}

// 新增：滚动到展示段锚点
const scrollToDisplayAnchor = (id: string) => {
  const anchor = displayAnchors.value.find(a => a.id === id)
  if (!anchor) return
  allowNavSwitch.value = false
  const sc = scrollContainerRef.value
  if (sc) {
    const targetTop = (anchor.el.getBoundingClientRect().top - sc.getBoundingClientRect().top) + sc.scrollTop
    sc.scrollTo({ top: targetTop - 20, behavior: 'smooth' })
  } else {
    const y = anchor.el.getBoundingClientRect().top + window.pageYOffset
    window.scrollTo({ top: y - 71 - 20, behavior: 'smooth' })
  }
  setTimeout(() => { allowNavSwitch.value = true }, 800)
}

// 在数据或语言变化后，重新解析锚点
watch([() => sections.value, () => markdownContent.value, () => locale.value], () => {
  nextTick(() => {
    parseDisplayAnchors()
    handleScroll()
  })
})

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

const getArticleImage = (imageUrl: string | null | undefined) => {
  // 私密内容使用对应的默认封面
  if (article.value?.is_private) {
    const channel = article.value?.channel?.toLowerCase() || ''
    switch (channel) {
      case 'private_general':
        return '/images/covers/private_general.svg'
      case 'private_parent':
        return '/images/covers/private_parent.svg'
      case 'private_customer':
        return '/images/covers/private_customer.svg'
      default:
        return '/images/covers/private_general.svg'
    }
  }
  
  if (articleCoverError.value) {
    return '/images/covers/article_default.png'
  }
  if (
    imageUrl &&
    imageUrl.trim() !== '' &&
    !imageUrl.includes('qpic.cn') &&
    imageUrl !== '无缩略图'
  ) {
    return imageUrl
  }
  return '/images/covers/article_default.png'
}

const handleArticleCoverError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (!articleCoverError.value && img.src !== '/images/covers/article_default.png') {
    articleCoverError.value = true
  }
}

const getAuthorIcon = () => {
  if (authorImageError.value) {
    return '/images/icons/author_default.svg'
  }
  return article.value?.author?.icon || '/images/icons/author_default.svg'
}

const handleAuthorImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (!authorImageError.value && img.src !== '/images/icons/author_default.svg') {
    authorImageError.value = true
  }
}

// 添加获取作者名称的方法
const getAuthorName = () => {
  // 私密内容：只有当前用户是作者时才显示"我的上传"
  if (article.value?.is_private) {
    const currentUserId = authStore.user?.id
    const articleUserId = article.value?.user_id
    if (currentUserId && articleUserId && currentUserId === articleUserId) {
      return '我的上传'
    }
    // 别人分享的私密内容，显示"私密分享"
    return '私密分享'
  }
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

  // 防抖：避免移动端一次点击触发 touchend 与 mouseup 双事件
  let lastTouchTime = 0
  const TOUCH_MOUSE_GAP_MS = 350

  // 统一处理逻辑
  const handleTextSelection = (event?: Event) => {
  console.log('Text selection triggered')
  
  // 检查是否点击的是气泡或相关元素
  if (event && event.target) {
    const target = event.target as HTMLElement
    const bubble = target.closest('.citation-bubble')
    const wrapper = target.closest('.citation-bubble-wrapper')
    const tooltip = target.closest('.citation-tooltip')
    
    // 检查是否点击的是案例badge
    const caseBubble = target.closest('.case-bubble')
    const caseWrapper = target.closest('.case-bubble-wrapper')
    const caseTooltip = target.closest('.case-tooltip')
    
    // 如果点击的是tooltip内容,不阻止事件,继续执行文本选择逻辑
    if (tooltip || caseTooltip) {
      // 继续执行下面的文本选择逻辑
    }
    // 如果点击的是badge,处理tooltip切换并return
    else if (caseBubble) {
      // 点击badge时阻止默认行为和冒泡
      event.stopPropagation?.()
      event.preventDefault?.()
      
      const actualWrapper = caseBubble.closest('.case-bubble-wrapper') as HTMLElement
      if (actualWrapper) {
        const tooltipEl = actualWrapper.querySelector('.case-tooltip') as HTMLElement
        if (tooltipEl) {
          const isHidden = tooltipEl.classList.contains('hidden')
          
          if (isHidden) {
            // 先隐藏所有其他tooltip
            document.querySelectorAll('.case-tooltip, .citation-tooltip').forEach(t => {
              t.classList.add('hidden')
            })
            // 显示当前tooltip
            tooltipEl.classList.remove('hidden')
          } else {
            // 隐藏当前tooltip
            tooltipEl.classList.add('hidden')
          }
        }
      }
      return
    }
    else if (bubble) {
      // 点击badge时阻止默认行为和冒泡
      event.stopPropagation?.()
      event.preventDefault?.()
      
      const wrapper = bubble.closest('.citation-bubble-wrapper') as HTMLElement
      if (wrapper) {
        let bubbleTooltip = wrapper.querySelector('.citation-tooltip')
        
        // 如果tooltip不存在，尝试从data属性重建
        if (!bubbleTooltip && bubble.dataset.content) {
          const timestamp = bubble.dataset.timestamp || ''
          const speaker = bubble.dataset.speaker || ''
          const content = bubble.dataset.content || ''
          
          if (speaker && content) {
            const tooltipDiv = document.createElement('div')
            tooltipDiv.className = 'citation-tooltip hidden absolute bg-white border border-gray-300 rounded-lg p-3 max-w-xs min-w-48 shadow-lg z-50 text-sm leading-relaxed'
            tooltipDiv.style.cssText = 'top: 100%; left: 50%; transform: translateX(-50%); margin-top: 8px;'
            
            const tooltipHeader = document.createElement('div')
            tooltipHeader.className = 'tooltip-header flex gap-2 mb-2 pb-2 border-b border-gray-200'
            
            if (isMeaningfulTimestamp(timestamp)) {
              const tsTip = document.createElement('span')
              tsTip.className = 'tooltip-timestamp text-xs text-gray-600 font-medium'
              tsTip.textContent = `[${timestamp}]`
              tooltipHeader.appendChild(tsTip)
            }
            
            const speakerTip = document.createElement('span')
            speakerTip.className = 'tooltip-speaker text-xs text-blue-600 font-semibold'
            speakerTip.textContent = speaker
            tooltipHeader.appendChild(speakerTip)
            
            const tooltipContentDiv = document.createElement('div')
            tooltipContentDiv.className = 'tooltip-content text-gray-700 italic'
            tooltipContentDiv.textContent = content
            
            tooltipDiv.appendChild(tooltipHeader)
            tooltipDiv.appendChild(tooltipContentDiv)
            wrapper.appendChild(tooltipDiv)
            bubbleTooltip = tooltipDiv
          }
        }
        
        if (bubbleTooltip) {
          const isHidden = bubbleTooltip.classList.contains('hidden')
          
          if (isHidden) {
            // 先隐藏所有其他tooltip(包括citation和case)
            document.querySelectorAll('.citation-tooltip, .case-tooltip').forEach(t => {
              if (t !== bubbleTooltip) {
                t.classList.add('hidden')
              }
            })
            
            // 显示当前tooltip
            bubbleTooltip.classList.remove('hidden')
          } else {
            // 隐藏当前tooltip
            bubbleTooltip.classList.add('hidden')
          }
        }
      }
      return
    }
  }
  
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

  // 2025-01-13: 捕获选中文字的位置信息（用于波浪线标记）
  let textPosition = null
  let sectionType = ''
  
  // 找到选中文字所在的 section 容器
  const startContainer = range.startContainer
  const sectionElement = startContainer.parentElement?.closest('[data-section-type]')
  if (sectionElement) {
    sectionType = sectionElement.getAttribute('data-section-type') || ''
    // 获取 section 内的内容容器（prose 区域）
    const contentContainer = sectionElement.querySelector('.prose') || sectionElement
    textPosition = TextPositionHelper.capturePosition(contentContainer as Element, selection)
    console.log('捕获的文字位置:', { textPosition, sectionType, text: selection.toString() })
  }

  chatStore.showToolbar(position, selection.toString(), textPosition, sectionType)
}

  // 分发到统一处理：鼠标场景
  const handleMouseUp = (event: MouseEvent) => {
    const now = Date.now()
    // 若在触摸后短时间内触发的 mouseup，则忽略，避免双触发
    if (now - lastTouchTime < TOUCH_MOUSE_GAP_MS) return
    handleTextSelection(event)
  }

  // 分发到统一处理：触屏场景
  const handleTouchEndArticle = (event: TouchEvent) => {
    lastTouchTime = Date.now()
    // 将触摸事件转为通用处理
    handleTextSelection(event as unknown as Event)
  }


// 添加获取文章标记的方法
const articleMarks = ref<ChatSession[]>([])

// 2025-01-13: 获取文章的聊天标记
// 显示：1. 所有公开的标记 2. 自己的所有标记（包括私密的）
const fetchArticleMarks = async () => {
  try {
    const userId = authStore.user?.id
    
    let query = supabase
      .from('keep_chat_sessions')
      .select('*')
      .eq('article_id', route.params.id)
    
    // 过滤条件：公开的 OR 自己的
    if (userId) {
      query = query.or(`is_private.eq.false,user_id.eq.${userId}`)
    } else {
      // 未登录用户只能看公开的
      query = query.eq('is_private', false)
    }
    
    const { data, error } = await query
    
    if (error) throw error
    if (data) {
      articleMarks.value = data as ChatSession[]
      console.log('获取到的聊天标记:', data.length, '条')
    }
  } catch (error) {
    console.error('获取文章标记失败:', error)
  }
}

// 添加处理标记的方法
// 2025-01-13: 修改为显示波浪线+气泡，支持点击查看公开聊天记录
const processQuestionMarks = () => {
  // 处理普通问号标记
  const questionWrappers = document.querySelectorAll('.question-mark-wrapper')
  questionWrappers.forEach(wrapper => {
    const markId = wrapper.getAttribute('data-mark-id')
    const articleId = wrapper.getAttribute('data-article-id')
    const sectionType = wrapper.getAttribute('data-section-type')
    const markContent = wrapper.getAttribute('data-mark-content')
    const position = wrapper.getAttribute('data-position')

    if (markId && articleId && sectionType && markContent && position) {
      // 创建一个临时容器
      const container = document.createElement('div')
      
      // 使用 h 函数创建 VNode
      // 2025-01-13: showQuestionMark 改为 true，显示波浪线+气泡+点击事件
      const vnode = h(QuestionMark, {
        markId,
        articleId: Number(articleId),
        sectionType,
        markContent,
        position: JSON.parse(position),
        showQuestionMark: true
      }, () => [wrapper.textContent])

      // 渲染到临时容器
      render(vnode, container)
      
      // 替换原始元素
      if (container.firstElementChild) {
        wrapper.replaceWith(container.firstElementChild)
      }
    }
  })

  // 🔧 修复：不再处理引用气泡，保持我们的HTML实现
  console.log('⚠️ 跳过引用气泡的Vue组件替换，保持HTML实现')
  
  // 注释掉引用气泡的处理逻辑，因为会替换我们的tooltip
  // const citationWrappers = document.querySelectorAll('.citation-bubble-wrapper')
  // ... 原有的引用气泡处理代码被注释掉
}

// 修改 renderSectionContent 方法
const renderSectionContent = (section: ArticleSection) => {
  if (!section || !section.content) {
    console.warn('无效的 section:', section)
    return ''
  }

  try {
    let content = section.content

    // 渲染 markdown（保持原始内容）
    let htmlContent = marked(content)
    const container = document.createElement('div')
    container.innerHTML = htmlContent
    
     // 后处理：查找<em>标签中的引用并转换为气泡（容错解析并按需隐藏时间戳）
    const citationMatches: Array<{citation: any, id: string, element: Element}> = []
    
         // 查找所有<em>标签中的引用
     const emElements = container.querySelectorAll('em')
     emElements.forEach(em => {
       const text = (em.textContent || '').trim()
       
       // 先检查是否是案例格式: 案例：[公司] - 描述
       const caseRegex = /^案例[：:]\s*\[?([^\]]+?)\]?\s*[-–—]\s*(.+)$/
       const caseMatch = text.match(caseRegex)
       
       if (caseMatch) {
         // 这是一个案例badge，不作为引用处理
         return
       }
       
       // 检查引用格式 (支持各种引号: 英文" 中文"" 弯引号""\u201C\u201D)
       const citationRegex = /^(?:\[(.+?)\]\s*)?([^：:]+?)[:：]\s*[""\"\u201C](.+?)[""\"\u201D]$/s
       const match = text.match(citationRegex)
       if (!match) return
       const label = (match[1] || '').trim()
       const timestamp = isMeaningfulTimestamp(label) ? label : ''
       const citation = {
         timestamp,
         speaker: match[2].trim(),
         content: match[3].trim(),
         isValid: true
       }
       const citationId = `citation-${Date.now()}-${citationMatches.length}`
       citationMatches.push({ citation, id: citationId, element: em })
     })
    
    // 处理每个找到的引用
    citationMatches.forEach(({citation, id, element}) => {
      const p = element.closest('p')
             if (p) {
         // 确保内容存在
         const safeContent = citation.content || '引用内容缺失'
         console.log('生成气泡HTML，内容:', safeContent) // 调试日志
         
         // 使用DOM API创建气泡元素
          const wrapper = document.createElement('span')
          wrapper.className = 'citation-bubble-wrapper inline-block relative mx-1'
          
          const bubble = document.createElement('span')
          bubble.className = 'citation-bubble inline-block bg-blue-50 border border-blue-200 rounded-xl px-2 py-1 cursor-pointer transition-all duration-200 hover:bg-blue-100 hover:border-blue-300 hover:translate-y-[-1px] text-xs'
          bubble.setAttribute('data-citation-id', id)
          bubble.setAttribute('data-content', safeContent)
          bubble.setAttribute('data-timestamp', citation.timestamp)
          bubble.setAttribute('data-speaker', citation.speaker)
          
          if (citation.timestamp && isMeaningfulTimestamp(citation.timestamp)) {
            const tsSpan = document.createElement('span')
            tsSpan.className = 'timestamp text-gray-600 mr-1'
            tsSpan.textContent = `[${citation.timestamp}]`
            bubble.appendChild(tsSpan)
          }
          
          const speakerSpan = document.createElement('span')
          speakerSpan.className = 'speaker text-blue-600 font-medium'
          speakerSpan.textContent = citation.speaker
          bubble.appendChild(speakerSpan)
          
          const tooltipDiv = document.createElement('div')
          tooltipDiv.className = 'citation-tooltip hidden absolute bg-white border border-gray-300 rounded-lg p-3 max-w-xs min-w-48 shadow-lg z-50 text-sm leading-relaxed'
          tooltipDiv.style.cssText = 'top: 100%; left: 50%; transform: translateX(-50%); margin-top: 8px;'
          
          const tooltipHeader = document.createElement('div')
          tooltipHeader.className = 'tooltip-header flex gap-2 mb-2 pb-2 border-b border-gray-200'
          
          if (citation.timestamp && isMeaningfulTimestamp(citation.timestamp)) {
            const tsTip = document.createElement('span')
            tsTip.className = 'tooltip-timestamp text-xs text-gray-600 font-medium'
            tsTip.textContent = `[${citation.timestamp}]`
            tooltipHeader.appendChild(tsTip)
          }
          
          const speakerTip = document.createElement('span')
          speakerTip.className = 'tooltip-speaker text-xs text-blue-600 font-semibold'
          speakerTip.textContent = citation.speaker
          tooltipHeader.appendChild(speakerTip)
          
          const tooltipContentDiv = document.createElement('div')
          tooltipContentDiv.className = 'tooltip-content text-gray-700 italic'
          tooltipContentDiv.textContent = safeContent
          
          tooltipDiv.appendChild(tooltipHeader)
          tooltipDiv.appendChild(tooltipContentDiv)
          
          wrapper.appendChild(bubble)
          wrapper.appendChild(tooltipDiv)
        
        // 找到紧邻的上一个兄弟块级元素并添加气泡
        // 说明：之前通过“所有<p>的前一个”来定位，遇到列表(<ul>/<ol>)时会错位。
        // 现在统一使用 DOM 兄弟遍历，若命中列表则选择最后一个 <li>，否则直接附加到上一个 <p>/<li>。
        let targetParagraph: Element | null = null
        let prevElement: Element | null = p.previousElementSibling as Element | null
        while (prevElement) {
          const tag = prevElement.tagName
          if (tag === 'P' || tag === 'LI' || tag === 'UL' || tag === 'OL') {
            if (tag === 'UL' || tag === 'OL') {
              const lastLi = prevElement.querySelector('li:last-child')
              if (lastLi) {
                targetParagraph = lastLi
              } else {
                // 列表没有 <li> 时，退化为把气泡加到列表元素本身
                targetParagraph = prevElement
              }
            } else {
              targetParagraph = prevElement
            }
            break
          }
          prevElement = prevElement.previousElementSibling as Element | null
        }
        // 兜底：如果没有可用的上一个兄弟元素，则附加到当前段落自身
        if (!targetParagraph) {
          targetParagraph = p
        }
        
        if (targetParagraph) {
          // 使用DOM API插入元素
          targetParagraph.appendChild(wrapper)
        }
        
        // 移除原始引用段落
        p.remove()
      }
    })

    // 注意：气泡点击逻辑现在由 handleTextSelection 函数处理
    console.log('气泡HTML生成完成，点击事件由主容器的mouseup事件处理')
    
    // 处理案例badges（在列表项的末尾独立一行显示）
    const caseElements = container.querySelectorAll('em')
    const caseRegex = /^案例[：:]\s*\[?([^\]]+?)\]?\s*[-–—]\s*(.+)$/
    
    caseElements.forEach(em => {
      const text = (em.textContent || '').trim()
      const match = text.match(caseRegex)
      
      // 只处理匹配案例格式的em标签,避免误删citation
      if (match) {
        const company = match[1].trim()
        const description = match[2].trim()
        const safeDescription = description.replace(/"/g, '&quot;')
        
        // 使用DOM API创建案例badge元素(避免insertAdjacentHTML截断问题)
        const wrapper = document.createElement('span')
        wrapper.className = 'case-bubble-wrapper inline-block relative mx-1 align-middle'
        
        // 创建badge
        const badge = document.createElement('span')
        badge.className = 'case-bubble inline-flex items-center gap-1 px-2 py-1 bg-gradient-to-r from-purple-500 to-purple-700 text-white rounded-xl text-xs font-medium cursor-pointer transition-all duration-200 hover:translate-y-[-1px] hover:shadow-lg'
        badge.setAttribute('data-company', company)
        badge.setAttribute('data-description', description)
        
        const icon = document.createElement('span')
        icon.className = 'case-icon'
        icon.textContent = '📦'
        
        const companySpan = document.createElement('span')
        companySpan.className = 'case-company'
        companySpan.textContent = company
        
        badge.appendChild(icon)
        badge.appendChild(companySpan)
        
        // 创建tooltip
        const tooltip = document.createElement('div')
        tooltip.className = 'case-tooltip hidden absolute bg-white border border-gray-300 rounded-lg p-3 max-w-xs min-w-48 shadow-lg z-50 text-sm leading-relaxed'
        tooltip.style.cssText = 'bottom: 100%; left: 0; margin-bottom: 8px;'
        
        const tooltipHeader = document.createElement('div')
        tooltipHeader.className = 'tooltip-header pb-2 mb-2 border-b border-gray-200'
        
        const tooltipCompany = document.createElement('span')
        tooltipCompany.className = 'tooltip-company text-xs text-purple-600 font-semibold'
        tooltipCompany.textContent = company
        
        tooltipHeader.appendChild(tooltipCompany)
        
        const tooltipContent = document.createElement('div')
        tooltipContent.className = 'tooltip-content text-gray-700'
        tooltipContent.textContent = description
        
        tooltip.appendChild(tooltipHeader)
        tooltip.appendChild(tooltipContent)
        
        wrapper.appendChild(badge)
        wrapper.appendChild(tooltip)
        
        // 找到包含案例标记的段落
        const p = em.closest('p')
        if (p) {
          const parentLi = p.closest('li')
          
          if (parentLi) {
            // 在LI内查找包含citation-bubble-wrapper的段落
            // 注意:必须找到的是citation wrapper,不是当前案例所在的p
            const allParagraphs = parentLi.querySelectorAll('p')
            let citationParagraph = null
            
            for (const paragraph of allParagraphs) {
              // 跳过当前案例所在的段落
              if (paragraph === p) continue
              // 查找包含citation-bubble-wrapper的段落
              if (paragraph.querySelector('.citation-bubble-wrapper')) {
                citationParagraph = paragraph
                break
              }
            }
            
            if (citationParagraph) {
              // 将案例badge添加到包含citation的段落末尾(在同一行)
              citationParagraph.appendChild(wrapper)
            } else {
              // 如果没有找到citation,就添加到第一个段落末尾
              const firstP = allParagraphs[0]
              if (firstP && firstP !== p) {
                firstP.appendChild(wrapper)
              }
            }
          }
          
          // 移除原始案例段落
          p.remove()
        }
      }
    })

    // 获取该 section 的所有标记（保留原有的chat sessions标记处理）
    // 2026-01-20: 同时包含 section_type 匹配的标记和 "general" 类型的标记
    const sectionMarks = articleMarks.value?.filter(
      mark => mark.section_type === section.section_type || mark.section_type === 'general'
    ) || []

    // 处理chat sessions标记
    sectionMarks.forEach(mark => {
      const position = mark.position

      // 2026-01-20: 改进 position 处理逻辑
      // 如果 position 有效，使用 position 定位
      // 如果 position 为 null 但有 mark_content，尝试通过文本搜索定位
      let range: Range | null = null
      
      if (position && 
          typeof position.nodeIndex === 'number' && 
          typeof position.startOffset === 'number' && 
          typeof position.endOffset === 'number') {
        // 有效的 position，使用原有逻辑
        const textMark: TextMark = {
          nodeIndex: position.nodeIndex,
          startOffset: position.startOffset,
          endOffset: position.endOffset,
          text: mark.mark_content
        }
        range = TextPositionHelper.findPosition(container, textMark)
      } else if (mark.mark_content) {
        // position 为 null，但有 mark_content，尝试通过文本搜索
        console.log('position 为空，尝试通过 mark_content 搜索:', mark.mark_content.slice(0, 50))
        
        // 构造一个只用于文本搜索的 textMark
        const textMark: TextMark = {
          nodeIndex: -1,  // 无效的 nodeIndex，会触发文本搜索回退
          startOffset: 0,
          endOffset: 0,
          text: mark.mark_content
        }
        range = TextPositionHelper.findPosition(container, textMark)
      }
      
      if (range) {
        const markInfo = {
          'mark-id': mark.id,
          'article-id': section.article_id,
          'section-type': section.section_type,
          'mark-content': mark.mark_content,
          'position': position ? JSON.stringify(position) : '{}'
        }
        
        TextPositionHelper.applyMarkStyle(range, markInfo)
      } else if (mark.section_type === 'general') {
        // general 类型的标记可能需要在其他 section 中查找，这里跳过不打印警告
        console.log('general 类型标记未在当前 section 找到匹配:', section.section_type)
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
        // 保持chat窗口默认展开状态
  
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

// 2025-01-13: 监听最新创建的会话，立即显示波浪线标记
watch(() => chatStore.lastCreatedSession, async (newSession) => {
  if (newSession && newSession.position) {
    console.log('新创建的会话，立即更新标记:', newSession)
    
    // 1. 将新 session 添加到 articleMarks
    articleMarks.value = [...articleMarks.value, newSession]
    
    // 2. 在下一个 tick 重新处理该 section 的标记
    await nextTick()
    
    // 找到对应的 section 数据
    const sectionData = sections.value.find(s => s.section_type === newSession.section_type)
    if (sectionData) {
      // 找到 DOM 中对应的 section 容器
      const sectionElement = document.querySelector(`[data-section-type="${newSession.section_type}"]`)
      if (sectionElement) {
        // 重新渲染该 section 的内容
        const contentElement = sectionElement.querySelector('.prose')
        if (contentElement) {
          contentElement.innerHTML = renderSectionContent(sectionData)
        }
      }
    }
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
    
    isLoading.value = true
    
    // 加载文章数据（登录后可以访问私密文章）
    await fetchArticle()
    
    // 2025-01-13: 只有文章加载成功后才获取标记
    if (article.value) {
      await fetchArticleMarks()
      
      // 重新解析展示段
      await nextTick()
      parseDisplayAnchors()
      handleScroll()
      handleTabsScroll()
    }
    
  } catch (error) {
    console.error('[handleLoginSuccess] Error:', error)
    ElMessage.error(t('error.loginFailed'))
  } finally {
    isLoading.value = false
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



const chatWindowRef = ref<InstanceType<typeof ChatWindow> | null>(null)

// 2024-03-21 14:30: 处理滚动到底部事件
const handleScrollToBottom = () => {
  chatWindowRef.value?.scrollToBottom(true)
}


// 添加handleLoginModalClose函数
const handleLoginModalClose = () => {
  // 2025-01-13: 修改关闭逻辑
  // 如果已登录，可以关闭
  if (authStore.isAuthenticated) {
    showLoginModal.value = false
    return
  }
  
  // 如果未登录且是私密文章，关闭后跳转回首页
  // 因为未登录用户无法查看私密文章
  if (article.value?.is_private || !article.value) {
    router.push('/')
    return
  }
  
  // 公开文章可以直接关闭登录框继续浏览
  showLoginModal.value = false
}

// 在 setup 中添加
const showFeedbackForm = ref(false)


const handleFeedbackSubmit = (data: any) => {
  console.log('Feedback submitted:', data)
  showFeedbackForm.value = false
  ElMessage.success(t('feedback.submitSuccess'))
}

// 2024-03-24 22:30: 添加获取section问题标记数量的方法
const getSectionQuestionCount = (sectionId: number) => {
  if (!articleMarks.value) return 0
  const currentSection = sections.value.find(s => s.id === sectionId)
  if (!currentSection) return 0
  return articleMarks.value.filter(mark => 
    mark.section_type && 
    mark.section_type === currentSection.section_type
  ).length
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

/* Optimize scrolling behavior without forcing scrollbar or gutter on root */
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
  width: 100%;
  box-sizing: border-box;
  /* 添加这行来确保内容不会因为滚动条出现而移动 */
  padding-right: 0;
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
  -o-user-drag: none
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
  --content-padding: 1rem;
  --min-side-margin: 1rem;
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

/* 响应式布局：桌面端使用flex布局，移动端为底部chat预留空间 */
.min-h-screen {
  transition: all 0.3s ease-in-out;
}

/* 移动端：保持底部预留空间 */
@media (max-width: 768px) {
  .min-h-screen {
    padding-bottom: 10vh;
  }
}

/* 文章内容区域 */
.article-content-wrapper {
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
  box-sizing: border-box;
}

/* 聊天框收起时的文章布局 - 居中显示，左右各空15% */
.article-content-centered {
  padding-left: 15%;
  padding-right: 15%;
  width: 100%;
}

/* 聊天框展开时的文章布局 - 占用全宽 */
.article-content-expanded {
  padding-left: 0;
  padding-right: 0;
  width: 100%;
}

/* 移动端始终占用全宽 */
@media (max-width: 768px) {
  .article-content-centered,
  .article-content-expanded {
    padding-left: 0;
    padding-right: 0;
  }
}

/* 标签区域样式 */
.tags-container {
  width: 100%;
  padding: 0.5rem var(--content-padding);
}

/* 文章主容器样式 */
.article-main-container {
  width: 100%;
  margin: 0;
}

@media (max-width: 768px) {
  :root {
    --content-padding: 0.5rem;
    --min-side-margin: 0.5rem;
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

/* 添加新的样式类 */
.article-content-centered {
  display: flex;
  justify-content: center;
  align-items: center;
}

.article-content-expanded {
  padding: 0 var(--content-padding);
}

/* 调整内容容器布局 */
.article-content {
  margin: 0;
  padding: 0 1rem;
  width: 100%;
  max-width: none;
}

/* 桌面端文章区域确保不超出可用空间 */
@media (min-width: 769px) {
  .article-content {
    padding-right: calc(1rem + 12px);
  }
}

/* 私密内容横幅样式 */
.private-content-banner {
  background: linear-gradient(135deg, 
    rgba(100, 100, 120, 0.08) 0%, 
    rgba(80, 80, 100, 0.12) 100%
  );
  border: 1px solid rgba(100, 100, 120, 0.15);
  border-radius: 12px;
  padding: 12px 16px;
  margin-top: 16px;
}

.private-content-banner .banner-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.private-content-banner .banner-icon {
  font-size: 16px;
}

.private-content-banner .banner-text {
  font-size: 14px;
  color: #555;
  font-weight: 500;
}
</style>
