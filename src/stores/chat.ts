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

// 2024-01-10: 添加开发模式配置和模拟数据
const isDev = import.meta.env.MODE === 'development'
const MOCK_DELAY = 2000 // 模拟延迟时间

// 2024-01-10 23:15: 添加模拟LLM响应的延迟函数
const mockLLMDelay = async () => {
  if (isDev) {
    await new Promise(resolve => setTimeout(resolve, MOCK_DELAY))
  }
}

// 模拟的AI响应数据
const mockResponses = [
  "这是一个模拟的AI响应，用于开发测试。我理解你的问题，让我来回答一下...",
  "作为一个模拟的AI助手，我认为这个问题可以从以下几个方面来看...",
  "从技术角度来说，这个问题涉及到几个关键点...",
  "根据我的分析，这个问题的解决方案是...",
  "让我们一步步来分析这个问题..."
]

// 获取随机模拟响应
const getRandomMockResponse = () => {
  const index = Math.floor(Math.random() * mockResponses.length)
  return mockResponses[index]
}

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

  // 添加类型检查函数
  const isChatSession = (data: any): data is ChatSession => {
    return (
      data &&
      typeof data.id === 'string' &&
      typeof data.article_id === 'number' &&
      typeof data.mark_type === 'string' &&
      typeof data.mark_content === 'string' &&
      typeof data.created_at === 'string' &&
      typeof data.updated_at === 'string'
    )
  }

  // 创建新会话
  const createSession = async (
    articleId: number, 
    markType: MarkType, 
    content: string,
    action: ChatAction,
    context?: any,
    skipInitialMessage: boolean = false,
    messageContent?: string
  ) => {
    try {
      isLoading.value = true
      isInitializing.value = true
      currentSession.value = null
      
      if (isDev) {
        // 开发模式：使用模拟数据
        const mockSession: ChatSession = {
          id: `mock-${Date.now()}`,
          article_id: articleId,
          mark_type: markType,
          mark_content: content,
          section_type: context?.sectionType,
          context: context,
          messages: [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }

        if (!skipInitialMessage) {
          const userMessage: ChatMessage = {
            id: `mock-${Date.now()}`,
            session_id: mockSession.id,
            role: 'user',
            content: messageContent || content,
            created_at: new Date().toISOString()
          }
          
          // 2024-01-10 23:15: 只在生成AI响应前添加延迟
          await mockLLMDelay()
          
          const aiMessage: ChatMessage = {
            id: `mock-${Date.now() + 1}`,
            session_id: mockSession.id,
            role: 'assistant',
            content: getRandomMockResponse(),
            created_at: new Date().toISOString()
          }
          
          mockSession.messages = [userMessage, aiMessage]
        }

        // 更新状态
        currentSession.value = mockSession
        sessions.value = [mockSession, ...sessions.value]
        lastCreatedSession.value = mockSession
        
        return mockSession
      } else {
        // 生产模式
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
        if (!isChatSession(sessionData)) throw new Error('Invalid session data')

        if (!skipInitialMessage) {
          // 2024-01-12: 使用完整的问题内容
          const { error: messageError } = await supabase
            .from('keep_chat_messages')
            .insert({
              session_id: sessionData.id,
              role: 'user',
              content: messageContent || content, // 优先使用完整问题内容
              created_at: new Date().toISOString()
            })

          if (messageError) throw messageError

          const response = await fetch(`/api/chat/${sessionData.id}`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            }
          })

          if (!response.ok) {
            throw new Error(`API 调用失败: ${response.status}`)
          }
        }

        await loadSession(sessionData.id)
        lastCreatedSession.value = sessionData
        
        return sessionData
      }
    } catch (error) {
      console.error('创建会话失败:', error)
      ElMessage.error('创建会话失败，请重试')
      isChatOpen.value = false
      throw error
    } finally {
      isInitializing.value = false
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
      if (!session) throw new Error('Session not found')
      if (!isChatSession(session)) throw new Error('Invalid session data')

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
      isLoading.value = true
      
      if (isDev) {
        // 开发模式：使用模拟数据
        // 2024-01-10 23:15: 立即添加用户消息，无需延迟
        const userMessage: ChatMessage = {
          id: `mock-${Date.now()}`,
          session_id: currentSession.value.id,
          role: 'user',
          content: content,
          created_at: new Date().toISOString()
        }
        
        // 立即更新用户消息
        currentSession.value.messages = [
          ...(currentSession.value.messages || []),
          userMessage
        ]
        
        // 2024-01-10 23:15: 只在生成AI响应前添加延迟
        await mockLLMDelay()
        
        // 模拟AI响应
        const aiMessage: ChatMessage = {
          id: `mock-${Date.now() + 1}`,
          session_id: currentSession.value.id,
          role: 'assistant',
          content: getRandomMockResponse(),
          created_at: new Date().toISOString()
        }

        // 更新AI响应
        currentSession.value.messages = [
          ...(currentSession.value.messages || []),
          aiMessage
        ]
      } else {
        // 生产模式：正常调用API
        const { error: messageError } = await supabase
          .from('keep_chat_messages')
          .insert({
            session_id: currentSession.value.id,
            role: 'user',
            content: content,
            created_at: new Date().toISOString()
          })

        if (messageError) throw messageError

        // 调用后端 AI 接口
        const response = await fetch(`/api/chat/${currentSession.value.id}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        })

        if (!response.ok) {
          throw new Error(`API 调用失败: ${response.status}`)
        }

        // 重新加载会话以获取最新消息
        await loadSession(currentSession.value.id)
      }

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
        .limit(10)

      if (error) throw error
      if (!data) throw new Error('No sessions found')
      
      // 验证每个会话数据
      const validSessions = data.filter(isChatSession)
      if (validSessions.length !== data.length) {
        console.warn('Some sessions were filtered out due to invalid data')
      }

      sessions.value = validSessions
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