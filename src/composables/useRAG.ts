/**
 * RAG 问答 Composable
 * 提供向量搜索和 AI 问答功能
 */
import { ref } from 'vue';
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

export function useRAG() {
  const loading = ref(false);
  const error = ref<string | null>(null);
  const messages = ref<RAGMessage[]>([]);

  /**
   * 发起 RAG 问答
   */
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

    // 添加用户消息
    messages.value.push({
      role: 'user',
      content: question,
      timestamp: new Date()
    });

    try {
      const { data, error: funcError } = await supabase.functions.invoke('rag_search', {
        body: {
          question: question.trim(),
          top_k: options?.top_k ?? 20,
          score_threshold: options?.score_threshold ?? 0.0
        }
      });

      if (funcError) {
        throw new Error(funcError.message || '搜索失败');
      }

      if (!data) {
        throw new Error('未收到响应数据');
      }

      const response = data as RAGResponse;

      // 添加 AI 回答消息
      messages.value.push({
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        timestamp: new Date()
      });

      return response;
    } catch (e: any) {
      const errorMsg = e.message || '搜索失败，请稍后重试';
      error.value = errorMsg;
      
      // 添加错误消息
      messages.value.push({
        role: 'assistant',
        content: `❌ ${errorMsg}`,
        timestamp: new Date()
      });

      console.error('RAG 错误:', e);
      return null;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 清空对话历史
   */
  const clearMessages = () => {
    messages.value = [];
    error.value = null;
  };

  return {
    ask,
    loading,
    error,
    messages,
    clearMessages
  };
}

