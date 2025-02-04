import { defineStore } from 'pinia'
import { supabase } from '../supabaseClient'
import type { Feedback, FeedbackForm } from '../types/feedback'
import { useAuthStore } from './auth'
import { ElMessage } from 'element-plus'
import { ref } from 'vue'

interface FeedbackState {
  submitting: boolean
}

export const useFeedbackStore = defineStore('feedback', () => {
  // 控制hover效果是否禁用
  const disableHoverEffect = ref(false)
  
  // 控制表单显示状态
  const showFeedbackForm = ref(false)

  // 控制提交状态
  const submitting = ref(false)

  // 重置状态
  const resetState = () => {
    disableHoverEffect.value = false
    showFeedbackForm.value = false
  }

  // 关闭表单并禁用hover
  const closeFeedbackForm = () => {
    showFeedbackForm.value = false
    disableHoverEffect.value = true
  }

  // 显示表单
  const showForm = () => {
    showFeedbackForm.value = true
  }

  // 2024-03-24: 添加提交反馈的方法
  const submitFeedback = async (formData: FeedbackForm) => {
    const authStore = useAuthStore()
    
    if (!authStore.user?.id) {
      ElMessage.error('Please login to submit feedback')
      return false
    }

    try {
      submitting.value = true

      const { error } = await supabase
        .from('keep_feedbacks')
        .insert({
          user_id: authStore.user.id,
          need_product: formData.need_product,
          satisfied_summary: formData.satisfied_summary,
          allow_contact: formData.allow_contact,
          notes: formData.notes,
          created_at: new Date().toISOString()
        })

      if (error) throw error

      ElMessage.success('Thank you for your feedback!')
      return true
    } catch (error) {
      console.error('Failed to submit feedback:', error)
      ElMessage.error('Failed to submit feedback')
      return false
    } finally {
      submitting.value = false
    }
  }

  return {
    disableHoverEffect,
    showFeedbackForm,
    submitting,
    resetState,
    closeFeedbackForm,
    showForm,
    submitFeedback
  }
}) 