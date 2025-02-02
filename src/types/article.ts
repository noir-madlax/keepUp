import type { Database } from './supabase'

export type ArticleStatus = 'processing' | 'processed' | 'failed'

export interface Author {
  id: number
  name: string
  icon?: string
}

export interface ArticleBase {
  id: string
  title: string
  cover_image_url?: string
  channel?: string
  publish_date?: string
  created_at: string
  tags?: string[]
  author_id?: number
  author?: Author
}

export interface Article extends ArticleBase {
  is_author: boolean
  status: 'processed'
  content: string
  original_link: string
}

export interface ArticleRequest {
  id: string
  url: string
  status: ArticleStatus
  created_at: string
  error_message?: string
  original_url: string
  platform?: string
  requestId?: string
  article_id?: string
}

export interface OptimisticCard {
  id: string
  url: string
  original_url: string
  created_at: string
  status: 'processing'
  platform?: string
  requestId: string
}

export interface ArticleView {
  article_id: string
  created_at: string
  is_author: boolean
  article: ArticleBase & {
    content?: string | null
    original_link?: string | null
  }
}

export interface KeepArticleView {
  article_id: string
  created_at: string
  is_author: boolean
  article: {
    id: string
    title: string
    cover_image_url?: string
    channel?: string
    created_at: string
    tags?: string[]
    publish_date?: string
    author_id?: number
    content?: string | null
    original_link?: string | null
    author?: Author
  }
}

export interface KeepArticleRequest {
  id: string
  url: string
  status: ArticleStatus
  created_at: string
  error_message?: string
  original_url: string
  platform?: string
  article_id?: string
  user_id: string
}

// 从 Database 类型中提取表类型
export type DbArticleView = Database['public']['Tables']['keep_article_views']['Row']
export type DbArticle = Database['public']['Tables']['keep_articles']['Row']
export type DbArticleRequest = Database['public']['Tables']['keep_article_requests']['Row']
export type DbAuthor = Database['public']['Tables']['keep_authors']['Row']

// 从 Database 类型中提取插入类型
export type DbArticleViewInsert = Database['public']['Tables']['keep_article_views']['Insert']
export type DbArticleInsert = Database['public']['Tables']['keep_articles']['Insert']
export type DbArticleRequestInsert = Database['public']['Tables']['keep_article_requests']['Insert']
export type DbAuthorInsert = Database['public']['Tables']['keep_authors']['Insert']

// 从 Database 类型中提取更新类型
export type DbArticleViewUpdate = Database['public']['Tables']['keep_article_views']['Update']
export type DbArticleUpdate = Database['public']['Tables']['keep_articles']['Update']
export type DbArticleRequestUpdate = Database['public']['Tables']['keep_article_requests']['Update']
export type DbAuthorUpdate = Database['public']['Tables']['keep_authors']['Update']
