export type ChatRole = 'user' | 'assistant'
export type MarkType = 'section' | 'sentence' | 'word'
export type ChatAction = 'elaborate' | 'explain' | 'question'

// 2024-01-20 11:30: 添加聊天窗口状态类型
export type ChatWindowState = 'minimized' | 'expanded'

// 工具栏位置
export interface ToolbarPosition {
  top: number
  left: number
}

// 聊天消息
export interface ChatMessage {
  id: string
  session_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

// 聊天会话
export interface Position {
  start: number
  end: number
}

export interface ChatSession {
  id: string
  article_id: number
  mark_type: string
  mark_content: string
  section_type?: string
  context?: any
  messages?: ChatMessage[]
  created_at: string
  updated_at: string
  user_id?: string
  position?: any
  is_private?: boolean
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

// 使用统一的 TextMark 接口
export interface TextMark {
  nodeIndex: number
  startOffset: number
  endOffset: number
  text: string
}

export interface ChatResponse {
  content: string
} 