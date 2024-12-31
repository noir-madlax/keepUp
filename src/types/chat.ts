export type ChatRole = 'user' | 'assistant'
export type MarkType = 'section' | 'sentence' | 'word'
export type ChatAction = 'summary' | 'explain' | 'question'

// 工具栏位置
export interface ToolbarPosition {
  top: number
  left: number
}

// 聊天消息
export interface ChatMessage {
  id: string
  role: ChatRole
  content: string
  createdAt: string
}

// 聊天会话
export interface ChatSession {
  id: string
  articleId: number
  userId: string
  markType: MarkType
  markContent: string
  sectionType?: string
  isPrivate: boolean
  messages: ChatMessage[]
  createdAt: string
  updatedAt: string
}

// 问题标记
export interface QuestionMark {
  id: string
  articleId: number
  sectionType?: string
  markType: MarkType
  markContent: string
  position: {
    start: number
    end: number
  }
  questionCount: number
} 