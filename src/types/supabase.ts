export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      keep_article_views: {
        Row: {
          article_id: string
          created_at: string
          is_author: boolean
          user_id: string
        }
        Insert: {
          article_id: string
          created_at?: string
          is_author?: boolean
          user_id: string
        }
        Update: {
          article_id?: string
          created_at?: string
          is_author?: boolean
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "keep_article_views_article_id_fkey"
            columns: ["article_id"]
            referencedRelation: "keep_articles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "keep_article_views_user_id_fkey"
            columns: ["user_id"]
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      keep_articles: {
        Row: {
          id: string
          title: string
          cover_image_url?: string
          channel?: string
          created_at: string
          tags?: string[]
          publish_date?: string
          author_id?: number
          content?: string
          original_link?: string
        }
        Insert: {
          id: string
          title: string
          cover_image_url?: string
          channel?: string
          created_at?: string
          tags?: string[]
          publish_date?: string
          author_id?: number
          content?: string
          original_link?: string
        }
        Update: {
          id?: string
          title?: string
          cover_image_url?: string
          channel?: string
          created_at?: string
          tags?: string[]
          publish_date?: string
          author_id?: number
          content?: string
          original_link?: string
        }
        Relationships: [
          {
            foreignKeyName: "keep_articles_author_id_fkey"
            columns: ["author_id"]
            referencedRelation: "keep_authors"
            referencedColumns: ["id"]
          }
        ]
      }
      keep_article_requests: {
        Row: {
          id: string
          url: string
          status: 'processing' | 'processed' | 'failed'
          created_at: string
          error_message?: string
          original_url: string
          platform?: string
          article_id?: string
          user_id: string
        }
        Insert: {
          id?: string
          url: string
          status?: 'processing' | 'processed' | 'failed'
          created_at?: string
          error_message?: string
          original_url: string
          platform?: string
          article_id?: string
          user_id: string
        }
        Update: {
          id?: string
          url?: string
          status?: 'processing' | 'processed' | 'failed'
          created_at?: string
          error_message?: string
          original_url?: string
          platform?: string
          article_id?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "keep_article_requests_article_id_fkey"
            columns: ["article_id"]
            referencedRelation: "keep_articles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "keep_article_requests_user_id_fkey"
            columns: ["user_id"]
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      keep_authors: {
        Row: {
          id: number
          name: string
          icon?: string
        }
        Insert: {
          id?: number
          name: string
          icon?: string
        }
        Update: {
          id?: number
          name?: string
          icon?: string
        }
        Relationships: []
      }
      users: {
        Row: {
          id: string
          email?: string
          created_at?: string
          updated_at?: string
          name?: string
          avatar_url?: string
          provider?: string
          provider_id?: string
        }
        Insert: {
          id: string
          email?: string
          created_at?: string
          updated_at?: string
          name?: string
          avatar_url?: string
          provider?: string
          provider_id?: string
        }
        Update: {
          id?: string
          email?: string
          created_at?: string
          updated_at?: string
          name?: string
          avatar_url?: string
          provider?: string
          provider_id?: string
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
} 