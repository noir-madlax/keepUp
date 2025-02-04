<template>
  <div 
    class="fixed right-0 top-0 bg-white p-8 rounded-l-lg shadow-lg z-[9999] w-[360px] border-l border-t border-b border-gray-200 max-h-[100vh] overflow-y-auto"
    :class="{ 
      'translate-x-full': !isVisible,
      'translate-x-0': isVisible 
    }"
    @click.stop
  >
    <!-- 标题和关闭按钮容器 -->
    <div class="flex items-center mb-4 -mt-4 relative">
      <h3 class="text-2xl font-bold text-gray-900 w-full text-center">Quick Feedback</h3>
      <button 
        @click="handleClose"
        class="text-gray-400 hover:text-gray-600 transition-colors absolute right-[-12px] top-[2px]"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>

    <!-- 表单内容 -->
    <form @submit.prevent="handleSubmit" class="space-y-3">
      <!-- 问题1 -->
      <div class="space-y-2">
        <p class="text-base font-medium text-gray-800">Do you need our product?</p>
        <div class="flex justify-center gap-16 items-center">
          <label class="inline-flex items-center cursor-pointer">
            <input type="radio" v-model="formData.need_product" :value="true" class="form-radio text-blue-500" required>
            <span class="ml-2 text-base text-pink-500 font-medium">Yes</span>
          </label>
          <label class="inline-flex items-center cursor-pointer">
            <input type="radio" v-model="formData.need_product" :value="false" class="form-radio text-blue-500">
            <span class="ml-2 text-base text-pink-500 font-medium">No</span>
          </label>
        </div>
      </div>

      <!-- 问题2 -->
      <div class="space-y-2">
        <p class="text-base font-medium text-gray-800">Are you satisfied with our summary?</p>
        <div class="flex justify-center gap-16 items-center">
          <label class="inline-flex items-center cursor-pointer">
            <input type="radio" v-model="formData.satisfied_summary" :value="true" class="form-radio text-blue-500" required>
            <span class="ml-2 text-base text-pink-500 font-medium">Yes</span>
          </label>
          <label class="inline-flex items-center cursor-pointer">
            <input type="radio" v-model="formData.satisfied_summary" :value="false" class="form-radio text-blue-500">
            <span class="ml-2 text-base text-pink-500 font-medium">No</span>
          </label>
        </div>
      </div>

      <!-- 问题3 -->
      <div class="space-y-2">
        <p class="text-base font-medium text-gray-800">May we contact you?</p>
        <div class="flex justify-center gap-16 items-center">
          <label class="inline-flex items-center cursor-pointer">
            <input type="radio" v-model="formData.allow_contact" :value="true" class="form-radio text-blue-500" required>
            <span class="ml-2 text-base text-pink-500 font-medium">Yes</span>
          </label>
          <label class="inline-flex items-center cursor-pointer">
            <input type="radio" v-model="formData.allow_contact" :value="false" class="form-radio text-blue-500">
            <span class="ml-2 text-base text-pink-500 font-medium">No</span>
          </label>
        </div>
      </div>

      <!-- 提交按钮 -->
      <button 
        type="submit"
        :disabled="!isFormComplete || feedbackStore.submitting"
        :class="[
          'w-full py-2.5 px-4 rounded-md font-medium text-sm shadow-sm transition-all',
          isFormComplete && !feedbackStore.submitting
            ? 'bg-gradient-to-r from-pink-500 to-purple-500 text-white hover:from-pink-600 hover:to-purple-600 cursor-pointer' 
            : 'bg-gray-100 text-gray-400 cursor-not-allowed'
        ]"
      >
        {{ feedbackStore.submitting ? 'Submitting...' : 'Submit' }}
      </button>
    </form>

    <!-- 联系方式图片 -->
    <div class="-mt-0 -mx-0">
      <img 
        :src="getContactImage('ContactMe.PNG')" 
        alt="Contact Details" 
        class="w-full h-auto"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useFeedbackStore } from '../../stores/feedback'
import { useAuthStore } from '../../stores/auth'

const props = defineProps<{
  isVisible: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'submit', data: typeof formData): void
}>()

const feedbackStore = useFeedbackStore()
const authStore = useAuthStore()

const formData = reactive({
  need_product: null as boolean | null,
  satisfied_summary: null as boolean | null,
  allow_contact: true as boolean | null,
  notes: '' as string
})

// 检查表单是否完整
const isFormComplete = computed(() => {
  return formData.need_product !== null && 
         formData.satisfied_summary !== null
})

const handleClose = () => {
  emit('close')
}

const handleSubmit = async () => {
  if (!isFormComplete.value) return
  
  // 检查登录状态
  if (!authStore.isAuthenticated) {
    ElMessage.warning('Please login to submit feedback')
    return
  }

  // 提交反馈
  const success = await feedbackStore.submitFeedback(formData)
  
  if (success) {
    emit('submit', formData)
    handleClose()
    
    // 重置表单，但保持allowContact为true
    formData.need_product = null
    formData.satisfied_summary = null
    formData.allow_contact = true
    formData.notes = ''
  }
}

// 添加获取图片的方法
const getContactImage = (imageName: string): string => {
  try {
    return new URL(`/public/images/covers/${imageName}`, import.meta.url).href
  } catch (error) {
    console.error('Error loading image:', error)
    return ''
  }
}
</script>

<style scoped>
.form-radio {
  @apply h-5 w-5 border-gray-300;
  @apply focus:ring-0 focus:ring-offset-0;
  @apply hover:border-blue-500 transition-colors;
}

div {
  transition: all 0.3s ease-in-out;
}

.form-radio:checked {
  background-color: #3B82F6;
  border-color: #3B82F6;
  transition: all 0.2s ease-in-out;
}

.form-radio:checked:hover {
  background-color: #2563EB;
  border-color: #2563EB;
}

.form-radio:focus {
  outline: none;
}
</style> 