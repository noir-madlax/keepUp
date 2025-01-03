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
export interface Position {
  start: number
  end: number
}

export interface ChatSession {
  id?: string
  article_id: number
  section_type: string
  mark_type: 'word' | 'sentence' | 'section'
  mark_content: string
  position: TextMark
  user_id: string
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

// 使用统一的 TextMark 接口
export interface TextMark {
  nodeIndex: number
  startOffset: number
  endOffset: number
  text: string
} 