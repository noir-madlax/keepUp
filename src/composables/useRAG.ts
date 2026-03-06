/**
 * RAG 问答 Composable
 * 提供向量搜索和 AI 问答功能，支持分阶段进度展示
 */
import { ref, onUnmounted } from 'vue';
import { supabase } from '@/supabaseClient';

export interface RAGSource {
  article_id: number;
  section_id: number;
  section_type: string;
  language: string;
  content: string;
  score: number;
}

export interface RAGResponse {
  answer: string;
  sources: RAGSource[];
  query_embedding_time_ms: number;
  search_time_ms: number;
  generation_time_ms: number;
  total_time_ms: number;
}

export interface RAGMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: RAGSource[];
  timestamp: Date;
}

export interface RAGSearchResult {
  totalChunks: number;
  summaryCount: number;
  transcriptCount: number;
  uniqueArticleCount: number;
  topScore: number;
  avgScore: number;
  topSources: RAGSource[];
}

export interface RAGProgress {
  stage: 'embedding' | 'searching' | 'search_done' | 'generating' | 'done' | 'error';
  message: string;
  detail?: string;
  searchResult?: RAGSearchResult;
  stageTimings?: Record<string, number>;
  elapsedMs: number;
}

export function useRAG() {
  const loading = ref(false);
  const error = ref<string | null>(null);
  const messages = ref<RAGMessage[]>([]);
  const progress = ref<RAGProgress | null>(null);

  let timerHandle: ReturnType<typeof setInterval> | null = null;
  let startTime = 0;

  function startTimer() {
    startTime = Date.now();
    timerHandle = setInterval(() => {
      if (progress.value && progress.value.stage !== 'done' && progress.value.stage !== 'error') {
        progress.value = { ...progress.value, elapsedMs: Date.now() - startTime };
      }
    }, 100);
  }

  function stopTimer() {
    if (timerHandle) {
      clearInterval(timerHandle);
      timerHandle = null;
    }
  }

  onUnmounted(() => stopTimer());

  const ask = async (
    question: string,
    options?: { top_k?: number; score_threshold?: number }
  ): Promise<RAGResponse | null> => {
    if (!question.trim()) {
      error.value = '问题不能为空';
      return null;
    }

    loading.value = true;
    error.value = null;
    const stageTimings: Record<string, number> = {};

    messages.value.push({
      role: 'user',
      content: question,
      timestamp: new Date()
    });

    startTimer();

    try {
      // 阶段1: Embedding + 向量搜索
      progress.value = {
        stage: 'searching',
        message: '正在理解问题并检索知识库...',
        elapsedMs: 0
      };

      const { data: step1Data, error: step1Error } = await supabase.functions.invoke('rag_search_step1', {
        body: {
          question: question.trim(),
          top_k: options?.top_k ?? 20,
          score_threshold: options?.score_threshold ?? 0.0
        }
      });

      if (step1Error) throw new Error(step1Error.message || '搜索失败');
      if (!step1Data) throw new Error('未收到搜索结果');

      stageTimings['embedding'] = step1Data.query_embedding_time_ms;
      stageTimings['search'] = step1Data.search_time_ms;

      const searchResult: RAGSearchResult = {
        totalChunks: step1Data.sources?.length ?? 0,
        summaryCount: step1Data.summary_count ?? 0,
        transcriptCount: step1Data.transcript_count ?? 0,
        uniqueArticleCount: step1Data.unique_article_count ?? 0,
        topScore: step1Data.top_score ?? 0,
        avgScore: step1Data.avg_score ?? 0,
        topSources: (step1Data.sources || []).slice(0, 5)
      };

      if (searchResult.totalChunks === 0) {
        progress.value = { stage: 'done', message: '未找到相关内容', elapsedMs: Date.now() - startTime, stageTimings };
        stopTimer();
        messages.value.push({
          role: 'assistant',
          content: '抱歉，我在知识库中没有找到与您问题相关的内容。请尝试换个问法或提供更多上下文信息。',
          sources: [],
          timestamp: new Date()
        });
        loading.value = false;
        return null;
      }

      // 阶段2: 展示搜索结果 + 开始生成
      progress.value = {
        stage: 'generating',
        message: '正在整合信息生成回答...',
        searchResult,
        stageTimings,
        elapsedMs: Date.now() - startTime
      };

      const { data: step2Data, error: step2Error } = await supabase.functions.invoke('rag_generate', {
        body: {
          question: question.trim(),
          sources: step1Data.sources
        }
      });

      if (step2Error) throw new Error(step2Error.message || '生成回答失败');
      if (!step2Data?.answer) throw new Error('未收到回答');

      stageTimings['generation'] = step2Data.generation_time_ms;

      // 完成
      const totalElapsed = Date.now() - startTime;
      progress.value = { stage: 'done', message: '回答完成', elapsedMs: totalElapsed, stageTimings, searchResult };
      stopTimer();

      const response: RAGResponse = {
        answer: step2Data.answer,
        sources: step1Data.sources,
        query_embedding_time_ms: stageTimings['embedding'],
        search_time_ms: stageTimings['search'],
        generation_time_ms: stageTimings['generation'],
        total_time_ms: totalElapsed
      };

      messages.value.push({
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        timestamp: new Date()
      });

      return response;
    } catch (e: unknown) {
      const errorMsg = e instanceof Error ? e.message : '搜索失败，请稍后重试';
      error.value = errorMsg;
      progress.value = {
        stage: 'error',
        message: errorMsg,
        elapsedMs: Date.now() - startTime,
        stageTimings,
        searchResult: progress.value?.searchResult
      };
      stopTimer();

      messages.value.push({
        role: 'assistant',
        content: `搜索失败: ${errorMsg}`,
        timestamp: new Date()
      });

      console.error('RAG 错误:', e);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const clearMessages = () => {
    messages.value = [];
    error.value = null;
    progress.value = null;
  };

  return {
    ask,
    loading,
    error,
    messages,
    progress,
    clearMessages
  };
}
