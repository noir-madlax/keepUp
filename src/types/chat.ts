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
  session_id: string
  role: ChatRole
  content: string
  created_at: string
}

// 聊天会话
export interface ChatSession {
  id: string
  article_id: number
  user_id: string
  mark_type: MarkType
  mark_content: string
  section_type?: string
  position?: any
  context?: any
  is_private: boolean
  created_at: string
  updated_at: string
  messages?: ChatMessage[]
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