import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { 
  ChatSession, 
  ChatMessage, 
  MarkType,
  ChatAction,
  ToolbarPosition,
  ChatWindowState,
} from '../types/chat'
import { PromptType } from '../types/chat'
import { supabase } from '../supabaseClient'
import { ElMessage } from 'element-plus'
import { useAuthStore } from './auth'
import { truncate, truncateSync } from 'fs'
import { useI18n } from 'vue-i18n'

// 2024-01-19 14:30: 添加超时和重试相关的常量
const TIMEOUT_MS = 7000 // 7秒超时
const MAX_RETRIES = 2 // 最大重试次数

// 2024-01-19 17:30: 添加 AbortController 实例
let currentAbortController: AbortController | null = null
// 2024-01-19 18:00: 添加用户主动中止的标志
let isUserAborted = false

const handleSSE = async (
  url: string, 
  init: RequestInit,
  onMessage: (data: any) => void,
  onDone: () => void,
  onError: (error: any) => void
) => {
  // 2024-01-19 17:30: 创建新的 AbortController
  currentAbortController = new AbortController()
  init.signal = currentAbortController.signal
  // 2024-01-19 18:00: 重置中止标志
  isUserAborted = false

  // 2024-01-19 14:30: 添加重试计数和超时控制
  let retryCount = 0
  let timeoutId: number | null = null
  
  const startSSEConnection = async () => {
    console.log('SSE 连接开始建立')
    
    // 2024-03-22 11:30: 如果是重试，先清理之前不完整的消息
    if (retryCount > 0 && currentSession.value?.messages) {
      const messages = [...currentSession.value.messages]
      if (messages.length > 0 && messages[messages.length - 1].role === 'assistant') {
        messages.pop() // 删除不完整的消息
        currentSession.value.messages = messages
        currentAIMessage.value = null
      }
    }

    // 2024-01-19 14:30: 设置超时检测
    timeoutId = window.setTimeout(() => {
      console.log('SSE 连接超时')
      if (retryCount < MAX_RETRIES) {
        retryCount++
        console.log(`开始第 ${retryCount} 次重试`)
        startSSEConnection()
      } else {
        onError(new Error('SSE 连接超时且重试失败'))
      }
    }, TIMEOUT_MS)

    try {
      const response = await fetch(url, init)
      if (!response.ok) {
        throw new Error(`网络响应不是 OK: ${response.statusText}`)
      }

      console.log('SSE 连接建立成功')
      const reader = response.body?.getReader()
      console.log('SSE 连接建立成功1')
      const decoder = new TextDecoder('utf-8')
      console.log('SSE 连接建立成功2')
      let buffer = ''
      console.log('SSE 连接建立成功3')
      while (true) {
        const { done, value } = await reader!.read()
        console.log('value', value, new Date().toLocaleTimeString('zh-CN', { hour12: false }))
        console.log('done', done, new Date().toLocaleTimeString('zh-CN', { hour12: false }))
        
        if (done) {
          console.log('SSE 读取完成，调用 onDone')
          onDone()
          break
        }
        
        buffer += decoder.decode(value, { stream: true })
        let boundary = buffer.indexOf('\n\n')
        
        while (boundary !== -1) {
          const chunk = buffer.slice(0, boundary)
          buffer = buffer.slice(boundary + 2)
          
          if (chunk.includes('event: done') || chunk.includes('data: [DONE]')) {
            console.log('检测到 SSE 结束信号，主动结束连接')
            onDone()
            return
          }
          
          if (chunk.startsWith('data: ')) {
            console.log('SSE 连接建立成功6')
            console.log('chunk', chunk)
            // 2024-01-19 14:30: 收到消息时清除超时计时器
            if (timeoutId) {
              console.log('SSE 连接建立成功7')
              window.clearTimeout(timeoutId)
              timeoutId = null
            }
            
            const dataStr = chunk.slice(6)
            if (dataStr === '[DONE]') {
              console.log('SSE 收到完成信号')
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
      console.log('SSE 连接发生错误:', error)
      // 2024-01-19 18:00: 只有在非用户主动中止时才重试和显示错误
      if (!isUserAborted) {
        if (retryCount < MAX_RETRIES) {
          retryCount++
          console.log(`连接失败，开始第 ${retryCount} 次重试`)
          startSSEConnection()
        } else {
          onError(error)
        }
      } else {
        // 用户主动中止，直接调用 onDone
        onDone()
      }
    } finally {
      // 2024-01-19 14:30: 清理超时计时器
      if (timeoutId) {
        window.clearTimeout(timeoutId)
        timeoutId = null
      }
    }
  }

  // 开始首次连接
  await startSSEConnection()
}

export const useChatStore = defineStore('chat', () => {
  const authStore = useAuthStore()
  const { t } = useI18n()
  
  // 状态
  const currentSession = ref<ChatSession | null>(null)
  const sessions = ref<ChatSession[]>([])
  const chatWindowState = ref<ChatWindowState>('minimized')
  const hasActiveSession = ref(false)
  const currentArticleId = ref<number | null>(null)
  
  const toolbarVisible = ref(false)
  const toolbarPosition = ref<ToolbarPosition>({ top: 0, left: 0 })
  const selectedText = ref('')
  
  // 2025-01-13: 添加选中文字的位置信息（用于波浪线标记）
  const selectedTextPosition = ref<any>(null)
  const selectedSectionType = ref<string>('')
  
  // 文章元信息（用于分享功能）
  const currentArticleInfo = ref<{
    title: string
    authorName: string
    isPrivate: boolean
  } | null>(null)
  const isAIResponding = ref(false)
  const isAIInitialLoading = ref(false)
  const lastCreatedSession = ref<ChatSession | null>(null)
  const isInitializing = ref(false)
  const currentAIMessage = ref<ChatMessage | null>(null)
  
  // 2025-01-13: 只读模式（查看他人的公开聊天记录时）
  const isReadOnly = ref(false)

  // 显示工具栏
  // 2025-01-13: 添加 textPosition 和 sectionType 参数
  const showToolbar = (position: ToolbarPosition, text: string, textPosition?: any, sectionType?: string) => {
    toolbarPosition.value = position
    selectedText.value = text
    selectedTextPosition.value = textPosition || null
    selectedSectionType.value = sectionType || ''
    toolbarVisible.value = true
  }

  // 隐藏工具栏
  const hideToolbar = () => {
    toolbarVisible.value = false
    selectedText.value = ''
    selectedTextPosition.value = null
    selectedSectionType.value = ''
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

  const isChatMessage = (data: any): data is ChatMessage => {
    return (
      data &&
      typeof data.id === 'string' &&
      typeof data.session_id === 'string' &&
      (data.role === 'user' || data.role === 'assistant') &&
      typeof data.content === 'string' &&
      typeof data.created_at === 'string'
    )
  }

  // 修改创建会话的函数
  const createSession = async (
    articleId: number,
    markType: MarkType,
    markContent: string,
    actionType: ChatAction,
    context?: any,
    skipInitialMessage?: boolean,
    initialMessage?: string
  ) => {
    if (!authStore.user?.id) {
      throw new Error(t('chat.errors.userNotLoggedIn'))
    }

    try {
      // 2024-01-20 14:30: 确保 context 不为 null
      const sessionContext = context || {
        type: actionType,
        content: markContent,
        timestamp: new Date().toISOString()
      }

      // 创建会话记录
      const { data: session, error: sessionError } = await supabase
        .from('keep_chat_sessions')
        .insert({
          article_id: articleId,
          user_id: authStore.user.id,
          mark_type: markType,
          mark_content: markContent,
          section_type: context?.sectionType,
          context: sessionContext,
          position: context?.position,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .select()
        .single()

      if (sessionError) throw sessionError
      if (!session) throw new Error(t('chat.errors.createSessionFailed'))

      // 如果不跳过初始消息，则创建初始消息
      if (!skipInitialMessage && initialMessage) {
        const { error: messageError } = await supabase
          .from('keep_chat_messages')
          .insert({
            session_id: session.id,
            role: 'user',
            content: initialMessage,
            created_at: new Date().toISOString()
          })

        if (messageError) throw messageError
      }

      await loadSession(session.id)
      hasActiveSession.value = true
      
      // 2025-01-13: 更新 lastCreatedSession，用于通知 ArticleView 刷新标记
      lastCreatedSession.value = session as ChatSession
      
      return session

    } catch (error) {
      console.error('创建会话失败:', error)
      throw error
    }
  }

  // 加载会话
  // 2025-01-13: 添加只读模式判断（查看他人的公开聊天记录）
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
      if (!session) throw new Error(t('chat.errors.sessionNotFound'))
      if (!isChatSession(session)) throw new Error(t('chat.errors.invalidSessionData'))

      currentSession.value = session
      
      // 2025-01-13: 判断是否为只读模式（session 不属于当前用户）
      isReadOnly.value = session.user_id !== authStore.user?.id
      
      // 设置活跃会话状态
      hasActiveSession.value = true
    } catch (error) {
      console.error('加载会话失败:', error)
      ElMessage.error(t('chat.errors.loadSessionFailed'))
    }
  }

  // 2024-01-20 18:30: 修改初始化会话的函数，更优雅地处理文章内容获取
  const initializeSession = async () => {
    if (!authStore.user?.id) {
      throw new Error(t('chat.errors.userNotLoggedIn'))
    }

    if (!currentArticleId.value) {
      throw new Error(t('chat.errors.noCurrentArticle'))
    }

    try {
      // 获取文章内容
      const { data: article } = await supabase
        .from('keep_articles')
        .select('title, content')
        .eq('id', currentArticleId.value)
        .single()

      // 如果获取不到文章内容，使用空字符串作为默认值
      const articleContent = article?.content || ''

      // 创建针对整篇文章的会话，使用标准的 context 格式
      const session = await createSession(
        currentArticleId.value,
        'article',
        articleContent,
        'question',
        {
          selection: {
            type: 'article',
            content: articleContent,
            position: null
          },
          sectionType: 'general'
        }
      )

      if (!session) {
        throw new Error(t('chat.errors.createSessionFailed'))
      }

      hasActiveSession.value = true
      return session
    } catch (error) {
      console.error('初始化会话失败:', error)
      throw error
    }
  }

  // 修改发送消息的函数
  const sendMessage = async (content: string, promptType: PromptType = PromptType.BASE) => {
    if (!authStore.user?.id) {
      throw new Error(t('chat.errors.userNotLoggedIn'))
    }

    try {
      // 2024-03-22 14:30: 检查当前会话是否属于当前文章
      if (currentSession.value && currentSession.value.article_id !== currentArticleId.value) {
        // 如果会话不属于当前文章，重置会话状态
        currentSession.value = null
        hasActiveSession.value = false
      }

      // 如果没有活跃会话，先初始化一个会话
      if (!hasActiveSession.value || !currentSession.value) {
        await initializeSession()
      }

      // 再次检查会话是否创建成功
      if (!currentSession.value) {
        throw new Error(t('chat.errors.createOrGetSessionFailed'))
      }

      // 2024-01-22 17:30: 移除重复的状态设置，改为在消息发送后设置
      // isAIResponding.value = true
      // isAIInitialLoading.value = true

      const userMessage: ChatMessage = {
        id: `temp-${Date.now()}`,
        session_id: currentSession.value.id,
        role: 'user',
        content: content,
        created_at: new Date().toISOString()
      }

      // 更新当前会话的消息列表
      if (!currentSession.value.messages) {
        currentSession.value.messages = []
      }
      currentSession.value.messages.push(userMessage)

      // 发送消息到服务器
      const { error: messageError } = await supabase
        .from('keep_chat_messages')
        .insert({
          session_id: currentSession.value.id,
          role: 'user',
          content: content,
          created_at: new Date().toISOString()
        })

      if (messageError) throw messageError

      currentAIMessage.value = null
      // 2024-01-22 17:30: 关闭初始化状态，开启AI回复加载状态
      isInitializing.value = false
      isAIInitialLoading.value = true

      // 2024-03-22 11:30: 添加重试计数变量
      let retryCount = 0

      // 2024-03-22 11:30: 清理函数
      const cleanupBeforeRetry = () => {
        if (currentSession.value?.messages) {
          const messages = [...currentSession.value.messages]
          if (messages.length > 0 && messages[messages.length - 1].role === 'assistant') {
            messages.pop()
            currentSession.value.messages = messages
            currentAIMessage.value = null
          }
        }
      }

      await handleSSE(
        `/api/chat/${currentSession.value.id}/stream${promptType !== PromptType.BASE ? `?prompt_type=${promptType}` : ''}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({})
        },
        (data) => {
          if (data.content && currentSession.value) {
            if (!currentAIMessage.value) {
              const aiMessage: ChatMessage = {
                id: `ai-${Date.now()}`,
                session_id: currentSession.value.id,
                role: 'assistant',
                content: data.content,
                created_at: new Date().toISOString()
              }
              currentAIMessage.value = aiMessage
              isAIInitialLoading.value = false

              const messages = currentSession.value.messages || []
              currentSession.value = {
                ...currentSession.value,
                messages: [...messages, aiMessage]
              } as ChatSession
            } else {
              currentAIMessage.value.content += data.content
              if (currentSession.value.messages) {
                const messages = [...currentSession.value.messages]
                const lastMessage = messages[messages.length - 1]
                if (lastMessage && lastMessage.role === 'assistant') {
                  lastMessage.content = currentAIMessage.value.content
                  currentSession.value = {
                    ...currentSession.value,
                    messages
                  } as ChatSession
                }
              }
            }
          }
        },
        () => {
          if (!currentAIMessage.value && currentSession.value?.id) {
            setTimeout(() => {
              reloadCurrentAIMessage(currentSession.value!.id)
            }, 1000)
          }
          currentAIMessage.value = null
          isAIResponding.value = false
          isAIInitialLoading.value = false
        },
        (error) => {
          console.error('SSE 连接错误:', error)
          if (!isUserAborted) {
            // 2024-03-22 11:30: 在重试之前清理不完整的消息
            if (retryCount < MAX_RETRIES) {
              retryCount++
              cleanupBeforeRetry()
            }
            ElMessage.error(t('chat.errors.aiResponseFailed'))
          }
          currentAIMessage.value = null
          isAIResponding.value = false
          isAIInitialLoading.value = false
        }
      )
    } catch (error) {
      console.error('发送消息失败:', error)
      ElMessage.error(t('chat.errors.sendMessageFailed'))
      currentAIMessage.value = null
      isAIResponding.value = false
      isAIInitialLoading.value = false
      isInitializing.value = false
      throw error
    }
  }

  // 添加加载会话列表的方法
  const loadSessions = async () => {
    // 2024-01-17: 暂时移除会话列表加载逻辑，提升性能
    try {
      // 返回空数组，保持数据结构一致
      sessions.value = []
    } catch (error) {
      console.error('加载会话列表失败:', error)
      // 保留错误提示，以防其他地方依赖这个行为
      ElMessage.error(t('chat.errors.loadSessionListFailed'))
    }
  }

  // 2024-01-20 11:35: 添加设置当前文章ID的方法
  // 2024-12-15: 扩展支持文章元信息（用于分享功能）
  const setCurrentArticle = (
    articleId: number, 
    articleInfo?: { title: string; authorName: string; isPrivate: boolean }
  ) => {
    // 2024-03-22 15:30: 如果当前有会话且属于不同文章，清除会话
    if (currentSession.value && currentSession.value.article_id !== articleId) {
      currentSession.value = null
      hasActiveSession.value = false
    }
    currentArticleId.value = articleId
    
    // 存储文章元信息
    if (articleInfo) {
      currentArticleInfo.value = articleInfo
    }
  }

  // 2024-01-20 11:35: 添加切换聊天窗口状态的方法
  const toggleChatWindow = () => {
    chatWindowState.value = chatWindowState.value === 'minimized' ? 'expanded' : 'minimized'
  }

  // 2024-01-19 14:30: 添加重新加载当前 AI 消息的函数
  const reloadCurrentAIMessage = async (sessionId: string) => {
    try {
      console.log('开始重新加载最后一条 AI 消息')
      const { data, error } = await supabase
        .from('keep_chat_messages')
        .select('*')
        .eq('session_id', sessionId)
        .eq('role', 'assistant')
        .order('created_at', { ascending: false })
        .limit(1)
      
      if (error) throw error
      
      if (data?.[0] && currentSession.value) {
        // 找到最后一条 AI 消息的索引
        const lastAIMessageIndex = currentSession.value.messages
          .findIndex(msg => msg.role === 'assistant')
        
        if (lastAIMessageIndex !== -1) {
          // 更新消息内容
          currentSession.value.messages[lastAIMessageIndex] = data[0]
          // 强制更新视图
          currentSession.value.messages = [...currentSession.value.messages]
          console.log('成功更新最后一条 AI 消息')
        }
      }
    } catch (error) {
      console.error('重新加载 AI 消息失败:', error)
      ElMessage.error(t('chat.errors.reloadMessageFailed'))
    }
  }

  // 2024-01-20 19:30: 修改中止聊天的方法，确保正确中断 SSE 连接
  const abortChat = () => {
    if (currentAbortController) {
      isUserAborted = true
      currentAbortController.abort()
      currentAbortController = null
      
      // 立即重置所有状态
      isAIResponding.value = false
      isAIInitialLoading.value = false
      
      // 如果有当前 AI 消息，将其标记为中断
      if (currentAIMessage.value && currentSession.value?.messages) {
        currentAIMessage.value.content += '\n[User Aborted]'
        const messages = [...currentSession.value.messages]
        const lastMessage = messages[messages.length - 1]
        if (lastMessage && lastMessage.role === 'assistant') {
          lastMessage.content = currentAIMessage.value.content
          currentSession.value = {
            ...currentSession.value,
            messages
          } as ChatSession
        }
      }
      currentAIMessage.value = null
    }
  }

  // 添加为特定标记加载会话的方法
  const loadSessionsForMark = async (articleId: number, markContent: string, sectionType: string) => {
    try {
      const { data, error } = await supabase
        .from('keep_chat_sessions')
        .select(`
          *,
          messages:keep_chat_messages(*)
        `)
        .eq('article_id', articleId)
        .eq('mark_content', markContent)
        .eq('section_type', sectionType)
        .order('created_at', { ascending: false })

      return { data, error }
    } catch (error) {
      console.error('加载标记会话失败:', error)
      return { data: null, error }
    }
  }

  return {
    currentSession,
    sessions,
    chatWindowState,
    hasActiveSession,
    toolbarVisible,
    toolbarPosition,
    selectedText,
    selectedTextPosition,  // 2025-01-13: 选中文字的位置信息
    selectedSectionType,   // 2025-01-13: 选中文字所在的 section 类型
    isLoading: isAIResponding,
    isAIResponding,
    isAIInitialLoading,
    createSession,
    sendMessage,
    showToolbar,
    hideToolbar,
    loadSession,
    loadSessions,
    loadSessionsForMark,
    lastCreatedSession,
    isInitializing,
    currentAIMessage,
    reloadCurrentAIMessage,
    abortChat,
    setCurrentArticle,
    toggleChatWindow,
    currentArticleId,
    currentArticleInfo,
    isReadOnly  // 2025-01-13: 只读模式状态
  }
}) 