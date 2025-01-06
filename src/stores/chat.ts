import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { 
  ChatSession, 
  ChatMessage, 
  MarkType,
  ChatAction,
  ToolbarPosition 
} from '../types/chat'
import { supabase } from '../supabaseClient'
import { ElMessage } from 'element-plus'
import { useAuthStore } from './auth'

export const useChatStore = defineStore('chat', () => {
  const authStore = useAuthStore()
  
  // 状态
  const currentSession = ref<ChatSession | null>(null)
  const sessions = ref<ChatSession[]>([])
  const isChatOpen = ref(false)
  const toolbarVisible = ref(false)
  const toolbarPosition = ref<ToolbarPosition>({ top: 0, left: 0 })
  const selectedText = ref('')
  const isLoading = ref(false)
  const lastCreatedSession = ref<ChatSession | null>(null)
  const isInitializing = ref(false)

  // 显示工具栏
  const showToolbar = (position: ToolbarPosition, text: string) => {
    toolbarPosition.value = position
    selectedText.value = text
    toolbarVisible.value = true
  }

  // 隐藏工具栏
  const hideToolbar = () => {
    toolbarVisible.value = false
    selectedText.value = ''
  }

  // 创建新会话
  const createSession = async (
    articleId: number, 
    markType: MarkType, 
    content: string,
    action: ChatAction,
    context?: any,
    skipInitialMessage: boolean = false
  ) => {
    try {
      isLoading.value = true
      isInitializing.value = true
      currentSession.value = null
      
      // 1. 创建会话记录
      const { data: sessionData, error: sessionError } = await supabase
        .from('keep_chat_sessions')
        .insert({
          article_id: articleId,
          user_id: authStore.user?.id,
          mark_type: markType,
          mark_content: content,
          section_type: context?.sectionType,
          position: context?.selection?.position,
          context: context,
          is_private: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .select('*')
        .single()

      if (sessionError) throw sessionError
      if (!sessionData) throw new Error('No session data returned')

      // 如果不是跳过初始消息的模式，则创建初始消息
      if (!skipInitialMessage) {
        // 2. 保存用户的首条消息和AI响应
        const { error: messageError } = await supabase
          .from('keep_chat_messages')
          .insert({
            session_id: sessionData.id,
            role: 'user',
            content: content,
            created_at: new Date().toISOString()
          })

        if (messageError) throw messageError

        // 3. 获取AI响应
        const aiResponse = `这是一个模拟的 AI 响应，基于动作类型 "${action}"，处理的内容长度为 ${content.length} 字符。`

        // 4. 保存AI响应消息
        const { error: aiMessageError } = await supabase
          .from('keep_chat_messages')
          .insert({
            session_id: sessionData.id,
            role: 'assistant',
            content: aiResponse,
            created_at: new Date().toISOString()
          })

        if (aiMessageError) throw aiMessageError
      }

      // 3. 先加载会话内容
      await loadSession(sessionData.id)
      
      // 4. 延迟关闭初始化状态
      setTimeout(() => {
        isInitializing.value = false
      }, 1000)
      
      // 5. 设置状态
      isChatOpen.value = true
      lastCreatedSession.value = sessionData
      
      return sessionData
    } catch (error) {
      console.error('创建会话失败:', error)
      ElMessage.error('创建会话失败，请重试')
      isChatOpen.value = false
      isInitializing.value = false
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 加载会话
  const loadSession = async (sessionId: string) => {
    try {
      const { data: session, error } = await supabase
        .from('keep_chat_sessions')
        .select(`
          *,
          messages:keep_chat_messages(*)
        `)
        .eq('id', sessionId)
        .single()

      if (error) throw error

      currentSession.value = session
    } catch (error) {
      console.error('加载会话失败:', error)
      ElMessage.error('加载会话失败，请重试')
    }
  }

  // 发送消息
  const sendMessage = async (content: string) => {
    if (!currentSession.value) return
    
    try {
      isLoading.value = false
      
      // 1. 保存用户消息
      const { error: messageError } = await supabase
        .from('keep_chat_messages')
        .insert({
          session_id: currentSession.value.id,
          role: 'user',
          content: content,
          created_at: new Date().toISOString()
        })

      if (messageError) throw messageError

      // 2. 获取AI响应
      // TODO: 接入实际的AI服务
      const aiResponse = `这是对 "${content}" 的模拟回复`

      // 3. 保存AI响应
      const { error: aiMessageError } = await supabase
        .from('keep_chat_messages')
        .insert({
          session_id: currentSession.value.id,
          role: 'assistant',
          content: aiResponse,
          created_at: new Date().toISOString()
        })

      if (aiMessageError) throw aiMessageError

      // 4. 重新加载会话以获取最新消息
      await loadSession(currentSession.value.id)

    } catch (error) {
      console.error('发送消息失败:', error)
      ElMessage.error('发送消息失败，请重试')
    } finally {
      isLoading.value = false
    }
  }

  // 添加加载会话列表的方法
  const loadSessions = async () => {
    try {
      const { data, error } = await supabase
        .from('keep_chat_sessions')
        .select(`
          *,
          messages:keep_chat_messages(*)
        `)
        .order('created_at', { ascending: false })
        .limit(10)  // 限制加载最近的10条会话

      if (error) throw error

      sessions.value = data || []
    } catch (error) {
      console.error('加载会话列表失败:', error)
      ElMessage.error('加载会话列表失败')
    }
  }

  // 添加创建新会话的方法
  const createNewSession = async (articleId: number, selectedText?: string, isAskAI: boolean = false) => {
    try {
      if (!authStore.user?.id) {
        throw new Error('用户未登录')
      }

      isLoading.value = true
      isChatOpen.value = true  // 立即打开聊天窗口
      
      // 根据是否是 Ask AI 模式设置不同的参数
      const sessionParams = isAskAI ? {
        markType: 'article' as MarkType,
        content: '',  // Ask AI 模式不需要初始内容
        action: 'question' as ChatAction,
        context: {
          sectionType: 'general',
          selection: {
            content: '整篇文章',
            type: 'article',
            position: null
          }
        },
        skipInitialMessage: true  // Ask AI 模式跳过初始消息
      } : {
        markType: 'section' as MarkType,
        content: '让我们开始讨论这篇文章',
        action: 'question' as ChatAction,
        context: {
          sectionType: 'general',
          selection: {
            content: '整篇文章',
            type: 'section',
            position: null
          }
        },
        skipInitialMessage: false
      }
      
      // 创建会话
      const result = await createSession(
        articleId,
        sessionParams.markType,
        sessionParams.content,
        sessionParams.action,
        sessionParams.context,
        sessionParams.skipInitialMessage
      )
      
      // 重新加载会话列表
      await loadSessions()
      
      return result
    } catch (error) {
      console.error('创建新会话失败:', error)
      ElMessage.error(error instanceof Error ? error.message : '创建新会话失败')
      isChatOpen.value = false
      throw error
    } finally {
      isLoading.value = false
    }
  }

  return {
    currentSession,
    sessions,
    isChatOpen,
    toolbarVisible,
    toolbarPosition,
    selectedText,
    isLoading,
    createSession,
    sendMessage,
    showToolbar,
    hideToolbar,
    loadSession,
    loadSessions,
    createNewSession,
    lastCreatedSession,
    isInitializing
  }
}) 