<template>
  <transition name="modal-fade">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4"
      @click.self="closeModal"
    >
      <div
        class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-3xl max-h-[85vh] flex flex-col"
        @click.stop
      >
        <!-- 头部 -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h2 class="text-xl font-bold text-gray-900 dark:text-white">智能问答助手</h2>
              <p class="text-sm text-gray-500 dark:text-gray-400">基于文章知识库的 AI 搜索</p>
            </div>
          </div>
          <button
            @click="closeModal"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 对话区域 -->
        <div
          ref="chatContainer"
          class="flex-1 overflow-y-auto px-6 py-4 space-y-4"
        >
          <!-- 欢迎消息 -->
          <div v-if="messages.length === 0 && !loading" class="text-center py-12">
            <div class="inline-block p-4 bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-900 dark:to-blue-900 rounded-full mb-4">
              <svg class="w-12 h-12 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              你好！我是知识库助手
            </h3>
            <p class="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
              你可以向我提问任何关于已收藏文章的问题，我会基于知识库为你提供准确的答案。
            </p>
            <div class="flex flex-wrap justify-center gap-2">
              <button
                v-for="example in exampleQuestions"
                :key="example"
                @click="askExample(example)"
                class="px-4 py-2 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                {{ example }}
              </button>
            </div>
          </div>

          <!-- 消息列表 -->
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="[
              'flex gap-3',
              message.role === 'user' ? 'justify-end' : 'justify-start'
            ]"
          >
            <!-- AI 头像 -->
            <div
              v-if="message.role === 'assistant'"
              class="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center"
            >
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>

            <!-- 消息气泡 -->
            <div
              :class="[
                'max-w-[75%] rounded-2xl px-4 py-3',
                message.role === 'user'
                  ? 'bg-gradient-to-br from-purple-500 to-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
              ]"
            >
              <div class="prose prose-sm dark:prose-invert max-w-none" v-html="formatMessage(message.content)"></div>
              
              <!-- 引用来源 -->
              <div v-if="message.sources && message.sources.length > 0" class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                <p class="text-xs font-semibold mb-2 text-gray-600 dark:text-gray-400">引用来源 ({{ message.sources.length }})</p>
                <div class="space-y-2">
                  <button
                    v-for="(source, idx) in message.sources.slice(0, 3)"
                    :key="idx"
                    @click="viewArticle(source.article_id)"
                    class="block w-full text-left p-2 bg-white dark:bg-gray-800 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
                  >
                    <div class="flex items-center justify-between">
                      <span class="text-xs font-medium text-purple-600 dark:text-purple-400">{{ source.section_type }}</span>
                      <span class="text-xs text-gray-500">相似度: {{ (source.score * 100).toFixed(0) }}%</span>
                    </div>
                    <p class="text-xs text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                      {{ source.content.substring(0, 80) }}...
                    </p>
                  </button>
                </div>
              </div>
            </div>

            <!-- 用户头像 -->
            <div
              v-if="message.role === 'user'"
              class="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-gray-400 to-gray-600 rounded-full flex items-center justify-center"
            >
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </div>

          <!-- 进度面板 -->
          <transition name="progress-fade">
            <div v-if="loading && progress" class="flex gap-3 justify-start">
              <div class="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div class="max-w-[80%] bg-gray-100 dark:bg-gray-700 rounded-2xl px-5 py-4 space-y-3">
                <!-- 阶段列表 -->
                <div class="space-y-2">
                  <!-- 搜索阶段 -->
                  <div class="flex items-center gap-2 text-sm">
                    <span v-if="progress.stage === 'searching'" class="w-4 h-4 flex items-center justify-center">
                      <span class="w-3 h-3 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"></span>
                    </span>
                    <span v-else class="w-4 h-4 flex items-center justify-center text-green-500 font-bold text-xs">✓</span>
                    <span :class="progress.stage === 'searching' ? 'text-purple-600 dark:text-purple-400 font-medium' : 'text-gray-500 dark:text-gray-400'">
                      检索知识库
                    </span>
                    <span v-if="progress.stageTimings?.search" class="text-xs text-gray-400 ml-auto">
                      {{ (progress.stageTimings.embedding / 1000).toFixed(1) }}s + {{ (progress.stageTimings.search / 1000).toFixed(1) }}s
                    </span>
                  </div>

                  <!-- 搜索结果统计 -->
                  <transition name="stats-slide">
                    <div v-if="progress.searchResult" class="ml-6 space-y-2">
                      <div class="flex flex-wrap gap-2">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300">
                          {{ progress.searchResult.totalChunks }} 个片段
                        </span>
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
                          {{ progress.searchResult.uniqueArticleCount }} 篇文章
                        </span>
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300">
                          最高 {{ (progress.searchResult.topScore * 100).toFixed(0) }}%
                        </span>
                      </div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">
                        总结类: {{ progress.searchResult.summaryCount }} 条 · 原文类: {{ progress.searchResult.transcriptCount }} 条 · 平均相似度: {{ (progress.searchResult.avgScore * 100).toFixed(0) }}%
                      </div>
                      <!-- 匹配预览 -->
                      <div v-if="progress.searchResult.topSources.length > 0" class="space-y-1 pt-1">
                        <div
                          v-for="(src, idx) in progress.searchResult.topSources.slice(0, 3)"
                          :key="idx"
                          class="flex items-center gap-2 px-2 py-1.5 bg-white dark:bg-gray-800 rounded-lg text-xs"
                        >
                          <span class="text-purple-500 flex-shrink-0">■</span>
                          <span class="text-gray-700 dark:text-gray-300 truncate flex-1">
                            {{ src.content.substring(0, 50) }}...
                          </span>
                          <span class="text-gray-400 flex-shrink-0 tabular-nums">
                            {{ src.section_type }} · {{ (src.score * 100).toFixed(0) }}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </transition>

                  <!-- 生成阶段 -->
                  <div v-if="progress.stage === 'generating' || progress.stage === 'done'" class="flex items-center gap-2 text-sm">
                    <span v-if="progress.stage === 'generating'" class="w-4 h-4 flex items-center justify-center">
                      <span class="w-3 h-3 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"></span>
                    </span>
                    <span v-else class="w-4 h-4 flex items-center justify-center text-green-500 font-bold text-xs">✓</span>
                    <span :class="progress.stage === 'generating' ? 'text-purple-600 dark:text-purple-400 font-medium' : 'text-gray-500 dark:text-gray-400'">
                      整合信息生成回答
                    </span>
                    <span v-if="progress.stageTimings?.generation" class="text-xs text-gray-400 ml-auto">
                      {{ (progress.stageTimings.generation / 1000).toFixed(1) }}s
                    </span>
                  </div>
                </div>

                <!-- 已用时间 -->
                <div class="flex items-center gap-1.5 text-xs text-gray-400 dark:text-gray-500 pt-1 border-t border-gray-200 dark:border-gray-600">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span class="tabular-nums">已用时间: {{ (progress.elapsedMs / 1000).toFixed(1) }}s</span>
                </div>
              </div>
            </div>
          </transition>
        </div>

        <!-- 输入区域 -->
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
          <form @submit.prevent="handleSubmit" class="flex gap-3">
            <input
              v-model="inputQuestion"
              type="text"
              :disabled="loading"
              placeholder="输入你的问题..."
              class="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              type="submit"
              :disabled="loading || !inputQuestion.trim()"
              class="px-6 py-3 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-xl hover:from-purple-600 hover:to-blue-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {{ loading ? '处理中...' : '发送' }}
            </button>
          </form>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
            基于文章知识库的 AI 回答，可能存在误差
          </p>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useRAG } from '@/composables/useRAG';

const props = defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
}>();

const router = useRouter();
const { ask, loading, messages, progress, clearMessages } = useRAG();

const inputQuestion = ref('');
const chatContainer = ref<HTMLDivElement>();

const exampleQuestions = [
  'Claude Skills 的核心功能是什么？',
  '最近有哪些 AI 技术趋势？',
  '如何使用 MCP 协议？'
];

const closeModal = () => {
  emit('update:modelValue', false);
};

const handleSubmit = async () => {
  if (!inputQuestion.value.trim() || loading.value) return;

  const question = inputQuestion.value.trim();
  inputQuestion.value = '';

  await ask(question);
  scrollToBottom();
};

const askExample = (question: string) => {
  inputQuestion.value = question;
  handleSubmit();
};

const formatMessage = (content: string) => {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
};

const viewArticle = (articleId: number) => {
  closeModal();
  router.push(`/article/${articleId}`);
};

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
  });
};

watch(() => props.modelValue, (newVal) => {
  if (!newVal) {
    // clearMessages();
  }
});

watch(() => [messages.value.length, progress.value?.stage], () => {
  scrollToBottom();
});
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.progress-fade-enter-active {
  transition: all 0.3s ease-out;
}

.progress-fade-leave-active {
  transition: all 0.2s ease-in;
}

.progress-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.progress-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.stats-slide-enter-active {
  transition: all 0.4s ease-out;
}

.stats-slide-enter-from {
  opacity: 0;
  max-height: 0;
  transform: translateY(-8px);
}

.stats-slide-enter-to {
  max-height: 300px;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
