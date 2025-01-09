import { defineStore } from 'pinia'
import { ref } from 'vue'
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

const handleSSE = async (
  url: string, 
  init: RequestInit,
  onMessage: (data: any) => void,
  onDone: () => void,
  onError: (error: any) => void
) => {
  try {
    const response = await fetch(url, init)
    if (!response.ok) {
      throw new Error(`网络响应不是 OK: ${response.statusText}`)
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader!.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      let boundary = buffer.indexOf('\n\n')
      while (boundary !== -1) {
        const chunk = buffer.slice(0, boundary)
        buffer = buffer.slice(boundary + 2)
        if (chunk.startsWith('data: ')) {
          const dataStr = chunk.slice(6)
          if (dataStr === '[DONE]') {
            onDone()
            return
          }
          try {
            const data = JSON.parse(dataStr)
            onMessage(data)
          } catch (err) {
            console.error('解析 SSE 数据失败:', err)
          }
        }
        boundary = buffer.indexOf('\n\n')
      }
    }
  } catch (error) {
    onError(error)
  }
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
  const currentAIMessage = ref<ChatMessage | null>(null)

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
      if (!isChatSession(sessionData)) throw new Error('Invalid session data')

      // 2. 创建初始会话状态
      currentSession.value = {
        ...sessionData,
        messages: [] as ChatMessage[]
      } as ChatSession
      
      // 结束初始化加载状态
      isInitializing.value = false

      if (!skipInitialMessage && currentSession.value) {
        // 3. 创建并显示用户消息
        const userMessage: ChatMessage = {
          id: `temp-${Date.now()}`,
          session_id: sessionData.id,
          role: 'user',
          content: messageContent || content,
          created_at: new Date().toISOString()
        }
        
        // 立即更新界面显示用户消息
        currentSession.value.messages = [userMessage]
        
        // 写入用户消息到数据库
        const { error: messageError } = await supabase
          .from('keep_chat_messages')
          .insert({
            session_id: sessionData.id,
            role: 'user',
            content: messageContent || content,
            created_at: new Date().toISOString()
          })

        if (messageError) throw messageError

        // 4. 开始加载 AI 响应
        isLoading.value = true

        // 处理 AI 响应
        await handleSSE(
          `/api/chat/${sessionData.id}/stream`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ /* 如果需要发送额外的数据 */ })
          },
          (data) => {
            if (data.content) {
              if (!currentAIMessage.value) {
                // 首次收到消息时创建新的 AI 消息对象
                currentAIMessage.value = {
                  id: `ai-${Date.now()}`,
                  session_id: sessionData.id,
                  role: 'assistant',
                  content: data.content,
                  created_at: new Date().toISOString()
                }
                // 添加到消息列表
                currentSession.value!.messages = [
                  ...currentSession.value!.messages,
                  currentAIMessage.value
                ]
              } else {
                // 后续消息累积到现有消息中
                currentAIMessage.value.content += data.content
                // 强制更新视图
                currentSession.value!.messages = [...currentSession.value!.messages]
              }
            }
          },
          () => {
            // 完成时重置当前消息
            currentAIMessage.value = null
            isLoading.value = false
          },
          (error) => {
            console.error('SSE 连接错误:', error)
            ElMessage.error('AI 响应加载失败，请重试')
            currentAIMessage.value = null
            isLoading.value = false
          }
        )
      }

      lastCreatedSession.value = sessionData
      return sessionData
    } catch (error) {
      console.error('创建会话失败:', error)
      ElMessage.error('创建会话失败，请重试')
      isChatOpen.value = false
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
      
      // 1. 立即创建并显示用户消息
      const userMessage: ChatMessage = {
        id: `temp-${Date.now()}`,
        session_id: currentSession.value.id,
        role: 'user',
        content: content,
        created_at: new Date().toISOString()
      }

      // 2. 更新界面显示
      currentSession.value.messages = [
        ...(currentSession.value.messages || []),
        userMessage
      ]

      // 3. 将用户消息写入数据库
      const { error: messageError } = await supabase
        .from('keep_chat_messages')
        .insert({
          session_id: currentSession.value.id,
          role: 'user',
          content: content,
          created_at: new Date().toISOString()
        })

      if (messageError) throw messageError

      // 4. 处理 AI 响应
      await handleSSE(
        `/api/chat/${currentSession.value.id}/stream`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ /* 如果需要发送额外的数据 */ })
        },
        (data) => {
          if (data.content) {
            if (!currentAIMessage.value) {
              // 首次收到消息时创建新的 AI 消息对象
              currentAIMessage.value = {
                id: `ai-${Date.now()}`,
                session_id: currentSession.value.id,
                role: 'assistant',
                content: data.content,
                created_at: new Date().toISOString()
              }
              // 添加到消息列表
              currentSession.value!.messages = [
                ...currentSession.value!.messages,
                currentAIMessage.value
              ]
            } else {
              // 后续消息累积到现有消息中
              currentAIMessage.value.content += data.content
              // 强制更新视图
              currentSession.value!.messages = [...currentSession.value!.messages]
            }
          }
        },
        () => {
          // 完成时重置当前消息
          currentAIMessage.value = null
          isLoading.value = false
        },
        (error) => {
          console.error('SSE 连接错误:', error)
          ElMessage.error('AI 响应加载失败，请重试')
          currentAIMessage.value = null
          isLoading.value = false
        }
      )

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
    isInitializing,
    currentAIMessage
  }
}) 