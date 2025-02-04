export interface Feedback {
  id: string
  user_id: string
  need_product: boolean
  satisfied_summary: boolean
  allow_contact: boolean
  notes?: string
  source_url?: string
  created_at: string
}

export interface FeedbackForm {
  need_product: boolean | null
  satisfied_summary: boolean | null
  allow_contact: boolean
  notes?: string
} 