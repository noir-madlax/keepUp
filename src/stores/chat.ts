import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { 
  ChatSession, 
  ChatMessage, 
  MarkType,
  ChatAction,
  ToolbarPosition 
} from '../types/chat'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const currentSession = ref<ChatSession | null>(null)
  const sessions = ref<ChatSession[]>([])
  const isChatOpen = ref(false)
  const toolbarVisible = ref(false)
  const toolbarPosition = ref<ToolbarPosition>({ top: 0, left: 0 })
  const selectedText = ref('')

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

  // 初始化 - 从 localStorage 加载会话
  const initSessions = () => {
    const savedSessions = localStorage.getItem('chatSessions')
    if (savedSessions) {
      sessions.value = JSON.parse(savedSessions)
    }
  }

  // 保存会话到 localStorage
  const saveSessions = () => {
    localStorage.setItem('chatSessions', JSON.stringify(sessions.value))
  }

  // 创建新会话
  const createSession = async (
    articleId: number, 
    markType: MarkType, 
    content: string,
    action: ChatAction,
    context?: any // TODO: 定义具体的类型
  ) => {
    // 模拟发送到后端的数据
    const requestData = {
      articleId,
      markType,
      content,
      action,
      context
    }
    
    // 打印模拟的请求数据
    console.log('Sending request to backend:', requestData)
    
    // 模拟后端响应
    const mockResponse = {
      sessionId: Date.now().toString(),
      aiResponse: `这是一个模拟的 AI 响应，基于动作类型 "${action}"，
        处理的内容长度为 ${content.length} 字符。
       \n\n选中的内容是：${context?.selection?.content || '无'}`
    }
    
    const session: ChatSession = {
      id: mockResponse.sessionId,
      articleId,
      userId: 'test-user',
      markType,
      markContent: content,
      isPrivate: false,
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }

    // 添加用户的首条消息
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content,
      createdAt: new Date().toISOString()
    }
    session.messages.push(userMessage)

    // 添加 AI 的首条响应
    const aiMessage: ChatMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: mockResponse.aiResponse,
      createdAt: new Date().toISOString()
    }
    session.messages.push(aiMessage)

    // 保存会话
    sessions.value.push(session)
    currentSession.value = session
    saveSessions()
    isChatOpen.value = true
  }

  // 发送消息
  const sendMessage = async (content: string) => {
    if (!currentSession.value) return

    // 添加用户消息
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content,
      createdAt: new Date().toISOString()
    }
    currentSession.value.messages.push(userMessage)

    // TODO: 这里先模拟 AI 回复
    setTimeout(() => {
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `这是对 "${content}" 的模拟回复`,
        createdAt: new Date().toISOString()
      }
      currentSession.value?.messages.push(aiMessage)
      saveSessions()
    }, 1000)

    saveSessions()
  }

  return {
    currentSession,
    sessions,
    isChatOpen,
    toolbarVisible,
    toolbarPosition,
    selectedText,
    initSessions,
    createSession,
    sendMessage,
    showToolbar,
    hideToolbar
  }
}) 