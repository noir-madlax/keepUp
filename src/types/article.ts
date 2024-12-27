export interface Author {
  id: number
  name: string
  icon: string
  created_at: string
}

export type ArticleStatus = 'processed' | 'processing' | 'failed' | 'rejected' | 'pending';

export interface ArticleRequest {
  id: string
  requestId: string
  url: string
  status: ArticleStatus
  created_at: string
  error_message?: string
  original_url?: string
  platform?: string
  title?: string
  author?: Author
  publish_date?: string
  channel?: string
  cover_image_url?: string
}
