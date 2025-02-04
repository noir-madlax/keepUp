import { defineStore } from 'pinia'
import { supabase } from '../supabaseClient'
import type { Feedback, FeedbackForm } from '../types/feedback'
import { useAuthStore } from './auth'
import { ElMessage } from 'element-plus'

interface FeedbackState {
  submitting: boolean
}

export const useFeedbackStore = defineStore('feedback', {
  state: (): FeedbackState => ({
    submitting: false
  }),

  actions: {
    async submitFeedback(formData: FeedbackForm): Promise<boolean> {
      const authStore = useAuthStore()
      
      if (!authStore.isAuthenticated || !authStore.user) {
        ElMessage.warning('Please sign in to submit feedback')
        return false
      }

      try {
        this.submitting = true
        
        const { data, error } = await supabase
          .from('keep_feedbacks')
          .insert({
            user_id: authStore.user.id,
            need_product: formData.need_product,
            satisfied_summary: formData.satisfied_summary,
            allow_contact: formData.allow_contact,
            notes: formData.notes || null,
            source_url: window.location.href
          })
          .select()
          .single()

        if (error) throw error

        ElMessage.success('Thanks for your feedback! We will keep improving our product.')
        return true
      } catch (error) {
        console.error('提交反馈失败:', error)
        ElMessage.error('Failed to submit feedback. Please try again later.')
        return false
      } finally {
        this.submitting = false
      }
    }
  }
}) 